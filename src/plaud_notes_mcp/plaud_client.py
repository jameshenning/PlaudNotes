"""Plaud Notes API client.

Reverse-engineered API client for accessing Plaud Notes recordings,
transcripts, and AI summaries. Based on the publicly documented APIs
at api.plaud.ai used by web.plaud.ai.
"""

from __future__ import annotations

import logging
import os
import re
import stat
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

# Strict pattern for Plaud file IDs (32-char hex)
_FILE_ID_PATTERN = re.compile(r"^[a-fA-F0-9]{24,64}$")

# Allowed API domains for redirect safety
_ALLOWED_API_DOMAINS = frozenset({
    "api.plaud.ai",
    "api-euc1.plaud.ai",
    "api-use1.plaud.ai",
})

# Regional API base URLs
API_DOMAINS = {
    "us": "https://api.plaud.ai",
    "eu": "https://api-euc1.plaud.ai",
}

DEFAULT_TIMEOUT = 30.0


@dataclass
class Recording:
    """A Plaud recording entry."""

    file_id: str
    filename: str
    duration_ms: int
    start_time: int
    end_time: int
    filesize: int
    created_at: datetime | None = None

    is_transcribed: bool = False
    is_summarized: bool = False
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Recording:
        created = None
        st = data.get("start_time", 0)
        if st:
            try:
                created = datetime.fromtimestamp(st / 1000, tz=timezone.utc)
            except (ValueError, OSError):
                pass
        return cls(
            file_id=data.get("id", data.get("file_id", "")),
            filename=data.get("filename", "Untitled"),
            duration_ms=data.get("duration", 0),
            start_time=st,
            end_time=data.get("end_time", 0),
            filesize=data.get("filesize", 0),
            created_at=created,
            is_transcribed=bool(data.get("is_trans", False)),
            is_summarized=bool(data.get("is_summary", False)),
            tags=data.get("filetag_id_list", []) or [],
        )

    @property
    def duration_str(self) -> str:
        total_seconds = self.duration_ms // 1000
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}h {minutes}m {seconds}s"
        if minutes:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"


@dataclass
class TranscriptSegment:
    """A single segment of a transcript."""

    text: str
    speaker: str = ""
    start_ms: int = 0
    end_ms: int = 0

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> TranscriptSegment:
        return cls(
            text=data.get("text", ""),
            speaker=data.get("speaker", data.get("spk", "")),
            start_ms=data.get("start_time_ms", data.get("start", data.get("bg", 0))),
            end_ms=data.get("end_time_ms", data.get("end", data.get("ed", 0))),
        )


@dataclass
class Transcript:
    """Full transcript for a recording."""

    file_id: str
    segments: list[TranscriptSegment] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Get the full transcript as plain text with speaker labels."""
        lines = []
        current_speaker = None
        for seg in self.segments:
            if seg.speaker and seg.speaker != current_speaker:
                current_speaker = seg.speaker
                lines.append(f"\n[{current_speaker}]")
            lines.append(seg.text)
        return "\n".join(lines).strip()

    @property
    def text_only(self) -> str:
        """Get transcript text without speaker labels."""
        return " ".join(seg.text for seg in self.segments if seg.text)


@dataclass
class Tag:
    """A Plaud tag/folder."""

    tag_id: str
    name: str
    count: int = 0


class PlaudAPIError(Exception):
    """Raised when the Plaud API returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class PlaudAuthError(PlaudAPIError):
    """Raised when authentication fails."""


class PlaudClient:
    """Client for the Plaud Notes API.

    Authentication requires a bearer token obtained from web.plaud.ai.
    The token can be provided directly, via PLAUD_TOKEN env var, or
    from a ~/.config/plaud/token file.
    """

    def __init__(
        self,
        token: str | None = None,
        region: str = "us",
        api_domain: str | None = None,
    ):
        self._token = self._resolve_token(token)
        if api_domain:
            self._base_url = self._validate_api_url(api_domain)
        else:
            self._base_url = API_DOMAINS.get(region, API_DOMAINS["us"])

        self._client = httpx.Client(
            base_url=self._base_url,
            headers=self._build_headers(),
            timeout=DEFAULT_TIMEOUT,
        )

    @staticmethod
    def _validate_file_id(file_id: str) -> str:
        """Validate that a file_id is a safe hex string."""
        if not _FILE_ID_PATTERN.match(file_id):
            raise PlaudAPIError(
                f"Invalid file_id format: expected 24-64 character hex string, "
                f"got {file_id!r:.50}"
            )
        return file_id

    @staticmethod
    def _validate_api_url(url: str) -> str:
        """Validate that an API URL is HTTPS and points to a known Plaud domain."""
        url = url.rstrip("/")
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise PlaudAPIError(
                f"API URL must use HTTPS, got {parsed.scheme!r}"
            )
        if parsed.hostname not in _ALLOWED_API_DOMAINS:
            raise PlaudAPIError(
                f"API domain {parsed.hostname!r} is not a recognized Plaud domain. "
                f"Allowed: {', '.join(sorted(_ALLOWED_API_DOMAINS))}"
            )
        if parsed.path and parsed.path != "/":
            raise PlaudAPIError("API URL must not contain a path")
        if parsed.query or parsed.fragment:
            raise PlaudAPIError("API URL must not contain query or fragment")
        return url

    @staticmethod
    def _resolve_token(token: str | None) -> str:
        """Resolve token from multiple sources."""
        if token:
            return token.removeprefix("bearer ").removeprefix("Bearer ")

        env_token = os.environ.get("PLAUD_TOKEN", "")
        if env_token:
            return env_token.removeprefix("bearer ").removeprefix("Bearer ")

        # Check config file
        config_path = os.path.expanduser("~/.config/plaud/token")
        if os.path.isfile(config_path):
            # Warn if token file is readable by others
            try:
                file_mode = os.stat(config_path).st_mode
                if file_mode & (stat.S_IRGRP | stat.S_IROTH):
                    logger.warning(
                        "Token file %s is readable by other users (mode %o). "
                        "Run: chmod 600 %s",
                        config_path, file_mode & 0o777, config_path,
                    )
            except OSError:
                pass
            with open(config_path) as f:
                file_token = f.read().strip()
            if file_token:
                return file_token.removeprefix("bearer ").removeprefix("Bearer ")

        raise PlaudAuthError(
            "No Plaud token found. Set PLAUD_TOKEN env var, create "
            "~/.config/plaud/token, or pass token directly. "
            "Get your token from web.plaud.ai -> DevTools -> Network -> "
            "Authorization header."
        )

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        _redirected: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an API request with error handling and retries."""
        last_error = None
        for attempt in range(3):
            try:
                response = self._client.request(method, path, **kwargs)
                if response.status_code == 401:
                    raise PlaudAuthError(
                        "Authentication failed. Your token may be expired. "
                        "Get a new one from web.plaud.ai.",
                        status_code=401,
                    )
                response.raise_for_status()
                data = response.json()

                # Handle region mismatch: API returns status -302
                # with the correct domain to use.
                # Only redirect once to prevent infinite loops.
                if isinstance(data, dict) and data.get("status") == -302:
                    if _redirected:
                        raise PlaudAPIError(
                            "Multiple API redirects detected; aborting."
                        )
                    correct_domain = data.get("domain", "")
                    if correct_domain and correct_domain in _ALLOWED_API_DOMAINS:
                        new_base = f"https://{correct_domain}"
                        old_client = self._client
                        self._client = httpx.Client(
                            base_url=new_base,
                            headers=self._build_headers(),
                            timeout=DEFAULT_TIMEOUT,
                        )
                        old_client.close()
                        self._base_url = new_base
                        return self._request(
                            method, path, _redirected=True, **kwargs
                        )
                    elif correct_domain:
                        logger.warning(
                            "Ignoring redirect to untrusted domain: %s",
                            correct_domain,
                        )

                return data
            except PlaudAuthError:
                raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < 2:
                    last_error = e
                    continue
                # Sanitize: don't include full response body which may
                # contain sensitive data in error messages
                raise PlaudAPIError(
                    f"API error: HTTP {e.response.status_code}",
                    status_code=e.response.status_code,
                ) from None
            except httpx.RequestError as e:
                if attempt < 2:
                    last_error = e
                    continue
                # Sanitize: strip potential token/header info from error
                raise PlaudAPIError(
                    f"Request failed: {type(e).__name__}"
                ) from None
        raise PlaudAPIError(
            f"Request failed after retries: {type(last_error).__name__}"
        )

    def _get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self._request("POST", path, **kwargs)

    # ── Recordings ──────────────────────────────────────────────

    _ALLOWED_SORT_FIELDS = frozenset({"edit_time", "start_time"})

    def list_recordings(
        self,
        limit: int = 100,
        skip: int = 0,
        sort_by: str = "edit_time",
        descending: bool = True,
    ) -> list[Recording]:
        """List all recordings in the account."""
        if sort_by not in self._ALLOWED_SORT_FIELDS:
            sort_by = "edit_time"
        data = self._get(
            "/file/simple/web",
            params={
                "skip": skip,
                "limit": limit,
                "is_trash": 0,
                "sort_by": sort_by,
                "is_desc": str(descending).lower(),
            },
        )
        # API returns data_file_list at the top level
        files = data.get("data_file_list", [])
        if not files:
            # Fallback for alternative response shapes
            files = data.get("data", [])
            if isinstance(files, dict):
                files = files.get("file_list", files.get("files", []))
        return [Recording.from_api(f) for f in files]

    def get_recording_detail(self, file_id: str) -> dict[str, Any]:
        """Get full detail for a recording including transcript and AI content."""
        file_id = self._validate_file_id(file_id)
        data = self._get(f"/file/detail/{file_id}")
        return data.get("data", data)

    def get_audio_url(self, file_id: str) -> str:
        """Get a temporary download URL for the recording audio."""
        file_id = self._validate_file_id(file_id)
        data = self._get(f"/file/temp-url/{file_id}", params={"is_opus": 0})
        # API returns temp_url at top level
        return data.get("temp_url", data.get("data", {}).get("url", ""))

    # ── Transcripts ─────────────────────────────────────────────

    def get_transcript(self, file_id: str) -> Transcript:
        """Get the transcript for a recording."""
        file_id = self._validate_file_id(file_id)
        detail = self.get_recording_detail(file_id)
        trans_result = detail.get("trans_result", {})

        segments = []
        if isinstance(trans_result, dict):
            raw_segments = trans_result.get("segments", trans_result.get("result", []))
            segments = [TranscriptSegment.from_api(s) for s in raw_segments]
        elif isinstance(trans_result, list):
            segments = [TranscriptSegment.from_api(s) for s in trans_result]

        return Transcript(file_id=file_id, segments=segments)

    # ── AI Summaries ────────────────────────────────────────────

    def get_summary(self, file_id: str) -> str:
        """Get the AI-generated summary for a recording."""
        file_id = self._validate_file_id(file_id)
        detail = self.get_recording_detail(file_id)
        ai_content = detail.get("ai_content", "")
        if isinstance(ai_content, dict):
            return ai_content.get("content", ai_content.get("summary", str(ai_content)))
        return str(ai_content) if ai_content else ""

    def get_notes(self, file_id: str) -> str:
        """Get AI-generated notes for a recording."""
        file_id = self._validate_file_id(file_id)
        try:
            data = self._get("/ai/query_note", params={"file_id": file_id})
            return data.get("data", {}).get("content", "")
        except PlaudAPIError:
            return ""

    # ── Tags ────────────────────────────────────────────────────

    def list_tags(self) -> list[Tag]:
        """List all tags/folders."""
        data = self._get("/filetag/")
        # API returns data_filetag_list at top level
        tags_data = data.get("data_filetag_list", data.get("data", []))
        return [
            Tag(
                tag_id=t.get("id", t.get("tag_id", "")),
                name=t.get("name", ""),
                count=t.get("file_count", t.get("count", 0)),
            )
            for t in tags_data
        ]

    # ── Speakers ────────────────────────────────────────────────

    def list_speakers(self) -> list[dict[str, Any]]:
        """List all known speakers."""
        data = self._get("/speaker/list")
        return data.get("data_speaker_list", data.get("data", []))

    # ── User & Devices ─────────────────────────────────────────

    def get_user_info(self) -> dict[str, Any]:
        """Get authenticated user account info."""
        data = self._get("/user/me")
        return data.get("data", data)

    def list_devices(self) -> list[dict[str, Any]]:
        """List all bound Plaud devices."""
        data = self._get("/device/list")
        return data.get("data", [])

    # ── Batch Operations ───────────────────────────────────────

    def get_batch_details(self, file_ids: list[str]) -> list[dict[str, Any]]:
        """Batch fetch details for multiple recordings."""
        data = self._post("/file/list", json=file_ids, timeout=60)
        return data.get("data", [])

    def get_recent_context(
        self,
        count: int = 5,
    ) -> list[dict[str, Any]]:
        """Get transcripts and summaries for the most recent recordings.

        Returns a list of dicts with recording metadata, transcript text,
        and AI summary for each of the most recent recordings.
        """
        recordings = self.list_recordings(limit=count, sort_by="start_time")
        results = []
        for rec in recordings:
            entry: dict[str, Any] = {
                "file_id": rec.file_id,
                "filename": rec.filename,
                "duration": rec.duration_str,
                "created": rec.created_at.isoformat() if rec.created_at else "unknown",
            }
            try:
                detail = self.get_recording_detail(rec.file_id)

                # Extract transcript
                trans_result = detail.get("trans_result", {})
                if isinstance(trans_result, dict):
                    segments = trans_result.get("segments", [])
                    if segments:
                        transcript = Transcript(
                            file_id=rec.file_id,
                            segments=[TranscriptSegment.from_api(s) for s in segments],
                        )
                        entry["transcript"] = transcript.full_text

                # Extract summary
                ai_content = detail.get("ai_content", "")
                if isinstance(ai_content, dict):
                    entry["summary"] = ai_content.get(
                        "content", ai_content.get("summary", "")
                    )
                elif ai_content:
                    entry["summary"] = str(ai_content)
            except PlaudAPIError:
                entry["error"] = "Could not fetch details"

            results.append(entry)
        return results

    def get_recordings_by_tag(self, tag_id: str) -> list[Recording]:
        """Get all recordings that have a specific tag."""
        all_recordings = self.list_recordings(limit=500)
        return [rec for rec in all_recordings if tag_id in rec.tags]

    # ── Search (client-side) ────────────────────────────────────

    def search_recordings(
        self,
        query: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Search recordings by matching query against filenames,
        transcripts, and summaries. This is a client-side search
        since Plaud doesn't provide a server-side search endpoint.
        """
        recordings = self.list_recordings(limit=limit)
        query_lower = query.lower()
        results = []

        for rec in recordings:
            # Check filename
            if query_lower in rec.filename.lower():
                results.append({
                    "recording": rec,
                    "match_type": "filename",
                    "snippet": rec.filename,
                })
                continue

            # Check transcript and summary
            try:
                detail = self.get_recording_detail(rec.file_id)

                # Search transcript
                trans_result = detail.get("trans_result", {})
                trans_text = ""
                if isinstance(trans_result, dict):
                    segments = trans_result.get("segments", [])
                    trans_text = " ".join(
                        s.get("text", "") for s in segments
                    )
                if query_lower in trans_text.lower():
                    # Extract snippet around match
                    idx = trans_text.lower().index(query_lower)
                    start = max(0, idx - 100)
                    end = min(len(trans_text), idx + len(query) + 100)
                    snippet = trans_text[start:end]
                    results.append({
                        "recording": rec,
                        "match_type": "transcript",
                        "snippet": f"...{snippet}...",
                    })
                    continue

                # Search summary
                ai_content = detail.get("ai_content", "")
                summary_text = ""
                if isinstance(ai_content, dict):
                    summary_text = ai_content.get("content", str(ai_content))
                elif isinstance(ai_content, str):
                    summary_text = ai_content

                if query_lower in summary_text.lower():
                    idx = summary_text.lower().index(query_lower)
                    start = max(0, idx - 100)
                    end = min(len(summary_text), idx + len(query) + 100)
                    snippet = summary_text[start:end]
                    results.append({
                        "recording": rec,
                        "match_type": "summary",
                        "snippet": f"...{snippet}...",
                    })
            except PlaudAPIError:
                continue

        return results

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> PlaudClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
