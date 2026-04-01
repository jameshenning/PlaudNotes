"""Plaud Notes MCP Server.

Exposes Plaud Notes recordings, transcripts, and AI summaries to Claude
via the Model Context Protocol (MCP).
"""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from plaud_notes_mcp.plaud_client import (
    PlaudAPIError,
    PlaudAuthError,
    PlaudClient,
)

load_dotenv()

mcp = FastMCP(
    "Plaud Notes",
    instructions=(
        "Access your Plaud Notes recordings, transcripts, and AI summaries. "
        "Search across all your voice notes for context and historical reference."
    ),
)

# ── Client singleton ────────────────────────────────────────────

_client: PlaudClient | None = None


def _get_client() -> PlaudClient:
    """Get or create the Plaud API client."""
    global _client
    if _client is None:
        token = os.environ.get("PLAUD_TOKEN")
        region = os.environ.get("PLAUD_REGION", "us")
        api_domain = os.environ.get("PLAUD_API_DOMAIN")
        _client = PlaudClient(
            token=token,
            region=region,
            api_domain=api_domain,
        )
    return _client


# ── Tools ───────────────────────────────────────────────────────


@mcp.tool()
def list_recordings(
    limit: int = 50,
    skip: int = 0,
    sort_by: str = "edit_time",
) -> str:
    """List your Plaud Notes recordings.

    Returns a list of recordings with their IDs, titles, durations, and dates.
    Use the file_id from the results with other tools to get transcripts or summaries.

    Args:
        limit: Maximum number of recordings to return (default 50, max 500).
        skip: Number of recordings to skip for pagination.
        sort_by: Sort field - "edit_time" (default) or "start_time".
    """
    try:
        client = _get_client()
        recordings = client.list_recordings(
            limit=min(limit, 500),
            skip=skip,
            sort_by=sort_by,
        )

        if not recordings:
            return "No recordings found in your Plaud Notes account."

        results = []
        for rec in recordings:
            entry = {
                "file_id": rec.file_id,
                "title": rec.filename,
                "duration": rec.duration_str,
                "created": rec.created_at.isoformat() if rec.created_at else "unknown",
                "size_bytes": rec.filesize,
                "has_transcript": rec.is_transcribed,
                "has_summary": rec.is_summarized,
            }
            results.append(entry)

        return json.dumps(
            {"total_returned": len(results), "recordings": results},
            indent=2,
        )
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def get_transcript(file_id: str) -> str:
    """Get the full transcript of a Plaud Notes recording.

    Returns the complete transcription text with speaker labels.
    Use list_recordings first to find the file_id.

    Args:
        file_id: The recording's file ID (32-character hex string).
    """
    try:
        client = _get_client()
        transcript = client.get_transcript(file_id)

        if not transcript.segments:
            return f"No transcript available for recording {file_id}. It may not have been transcribed yet."

        return json.dumps(
            {
                "file_id": file_id,
                "segment_count": len(transcript.segments),
                "transcript": transcript.full_text,
            },
            indent=2,
        )
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def get_summary(file_id: str) -> str:
    """Get the AI-generated summary of a Plaud Notes recording.

    Returns the summary/notes that Plaud AI generated from the recording.
    Use list_recordings first to find the file_id.

    Args:
        file_id: The recording's file ID (32-character hex string).
    """
    try:
        client = _get_client()
        summary = client.get_summary(file_id)

        if not summary:
            return f"No AI summary available for recording {file_id}."

        # Also try to get AI notes
        notes = client.get_notes(file_id)

        result = {"file_id": file_id, "summary": summary}
        if notes:
            result["notes"] = notes

        return json.dumps(result, indent=2)
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def get_recording_detail(file_id: str) -> str:
    """Get complete details for a Plaud Notes recording.

    Returns all metadata, transcript, and AI content for a single recording.
    This is the most comprehensive view of a recording.

    Args:
        file_id: The recording's file ID (32-character hex string).
    """
    try:
        client = _get_client()
        detail = client.get_recording_detail(file_id)

        # Build a clean summary of the detail
        result: dict = {
            "file_id": file_id,
            "filename": detail.get("filename", "Unknown"),
            "duration_ms": detail.get("duration", 0),
        }

        # Extract transcript text
        trans_result = detail.get("trans_result", {})
        if isinstance(trans_result, dict):
            segments = trans_result.get("segments", [])
            if segments:
                result["transcript_segments"] = len(segments)
                result["transcript_preview"] = " ".join(
                    s.get("text", "") for s in segments[:10]
                )

        # Extract AI summary
        ai_content = detail.get("ai_content", "")
        if ai_content:
            if isinstance(ai_content, dict):
                result["ai_summary"] = ai_content.get(
                    "content", ai_content.get("summary", "")
                )
            else:
                result["ai_summary"] = str(ai_content)

        return json.dumps(result, indent=2)
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def search_notes(query: str, limit: int = 20) -> str:
    """Search across all your Plaud Notes for specific content.

    Searches recording titles, transcripts, and AI summaries for the
    given query string. Useful for finding specific conversations,
    topics, or mentions.

    Note: This searches through your recordings one by one, so it may
    take a moment for large collections. Use a smaller limit for faster results.

    Args:
        query: The search term to look for in your notes.
        limit: Maximum number of recordings to search through (default 20).
    """
    try:
        client = _get_client()
        results = client.search_recordings(query, limit=min(limit, 100))

        if not results:
            return f'No recordings found matching "{query}".'

        matches = []
        for r in results:
            rec = r["recording"]
            matches.append({
                "file_id": rec.file_id,
                "title": rec.filename,
                "match_type": r["match_type"],
                "snippet": r["snippet"],
                "duration": rec.duration_str,
                "created": rec.created_at.isoformat() if rec.created_at else "unknown",
            })

        return json.dumps(
            {
                "query": query,
                "matches_found": len(matches),
                "results": matches,
            },
            indent=2,
        )
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def list_tags() -> str:
    """List all tags/folders in your Plaud Notes account.

    Returns tag names and IDs that can be used to organize and filter recordings.
    """
    try:
        client = _get_client()
        tags = client.list_tags()

        if not tags:
            return "No tags found in your Plaud Notes account."

        results = [
            {"tag_id": t.tag_id, "name": t.name, "count": t.count}
            for t in tags
        ]
        return json.dumps({"tags": results}, indent=2)
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def list_speakers() -> str:
    """List all known speakers identified in your Plaud Notes recordings.

    Returns speaker names that Plaud has identified across your recordings.
    """
    try:
        client = _get_client()
        speakers = client.list_speakers()

        if not speakers:
            return "No speakers found."

        return json.dumps({"speakers": speakers}, indent=2)
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def get_audio_url(file_id: str) -> str:
    """Get a temporary download URL for a recording's audio file.

    Returns a pre-signed URL that can be used to download the MP3 audio.
    The URL is temporary and will expire.

    Args:
        file_id: The recording's file ID (32-character hex string).
    """
    try:
        client = _get_client()
        url = client.get_audio_url(file_id)

        if not url:
            return f"Could not get audio URL for recording {file_id}."

        return json.dumps(
            {
                "file_id": file_id,
                "audio_url": url,
                "note": "This is a temporary pre-signed URL. Download promptly.",
            },
            indent=2,
        )
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def get_user_info() -> str:
    """Get your Plaud Notes account information.

    Returns your user profile including email, nickname, country,
    and membership type. Useful for verifying the connection is working.
    """
    try:
        client = _get_client()
        info = client.get_user_info()
        return json.dumps({"user": info}, indent=2)
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def list_devices() -> str:
    """List all Plaud devices connected to your account.

    Returns device names, serial numbers, models, and firmware versions.
    """
    try:
        client = _get_client()
        devices = client.list_devices()

        if not devices:
            return "No devices found on your Plaud account."

        return json.dumps({"devices": devices}, indent=2)
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def get_recent_context(count: int = 5) -> str:
    """Get transcripts and summaries from your most recent recordings.

    This is the best tool for loading recent conversation context into Claude.
    It fetches the full transcript and AI summary for each of your most recent
    recordings, giving Claude rich historical context from your voice notes.

    Args:
        count: Number of recent recordings to fetch (default 5, max 20).
    """
    try:
        client = _get_client()
        results = client.get_recent_context(count=min(count, 20))

        if not results:
            return "No recent recordings found."

        return json.dumps(
            {"recent_notes_count": len(results), "notes": results},
            indent=2,
        )
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


@mcp.tool()
def get_recordings_by_tag(tag_id: str) -> str:
    """Get all recordings with a specific tag/folder.

    Use list_tags first to find available tag IDs, then use this tool
    to see all recordings within that tag.

    Args:
        tag_id: The tag ID to filter by.
    """
    try:
        client = _get_client()
        recordings = client.get_recordings_by_tag(tag_id)

        if not recordings:
            return f"No recordings found with tag {tag_id}."

        results = [
            {
                "file_id": rec.file_id,
                "title": rec.filename,
                "duration": rec.duration_str,
                "created": rec.created_at.isoformat() if rec.created_at else "unknown",
                "has_transcript": rec.is_transcribed,
                "has_summary": rec.is_summarized,
            }
            for rec in recordings
        ]

        return json.dumps(
            {"tag_id": tag_id, "count": len(results), "recordings": results},
            indent=2,
        )
    except PlaudAuthError as e:
        return f"Authentication error: {e}"
    except PlaudAPIError as e:
        return f"API error: {e}"


# ── Resources ───────────────────────────────────────────────────


@mcp.resource("plaud://recordings")
def recordings_resource() -> str:
    """List of all Plaud Notes recordings."""
    return list_recordings(limit=100)


@mcp.resource("plaud://recording/{file_id}/transcript")
def transcript_resource(file_id: str) -> str:
    """Full transcript for a specific recording."""
    return get_transcript(file_id)


@mcp.resource("plaud://recording/{file_id}/summary")
def summary_resource(file_id: str) -> str:
    """AI summary for a specific recording."""
    return get_summary(file_id)


# ── Entry point ─────────────────────────────────────────────────


def main() -> None:
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
