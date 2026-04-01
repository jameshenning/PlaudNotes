# Plaud Notes MCP Server

An MCP (Model Context Protocol) server that connects your Plaud Notes account to Claude, giving Claude access to your voice recordings, transcripts, and AI summaries for context and historical reference.

## Features

- **List & Browse Recordings** - Browse all your Plaud Notes with titles, durations, dates, and transcript/summary status
- **Full Transcripts** - Retrieve complete transcriptions with speaker labels and timestamps
- **AI Summaries & Notes** - Access Plaud's AI-generated summaries and notes for any recording
- **Search Across Notes** - Search by title, transcript content, or summary text
- **Recent Context Loading** - Pull transcripts and summaries from your most recent recordings in one call
- **Tags & Folders** - View and filter recordings by organizational tags
- **Speakers** - List all identified speakers across your recordings
- **Account & Devices** - Check your account info and connected Plaud devices
- **Audio URLs** - Get temporary pre-signed download links for recording audio

## Quick Start

### 1. Get Your Plaud Token

1. Sign in to [web.plaud.ai](https://web.plaud.ai)
2. Open browser DevTools (`F12` or `Cmd+Option+I`)
3. Go to the **Network** tab and click any recording
4. Find a request to `api.plaud.ai` and copy the `Authorization` header value
5. The token is the part after `bearer ` (starts with `eyJ...`)

> **Tip:** Your token lasts ~10 months. Alternatively, go to **Application > Local Storage** and copy the `tokenstr` value.

> **Note:** If you use Google or Apple sign-in, you'll need to set a password first via "Forgot Password" on web.plaud.ai to ensure token compatibility.

### 2. Install

```bash
git clone https://github.com/jameshenning/PlaudNotes.git
cd PlaudNotes

# Option A: Install directly
pip install -e .

# Option B: Use a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### 3. Configure Your Token

Choose one method:

```bash
# Environment variable (simplest)
export PLAUD_TOKEN="eyJhbGciOiJI..."

# Or .env file
cp .env.example .env
# Edit .env and paste your token

# Or config file (most persistent)
mkdir -p ~/.config/plaud
echo "eyJhbGciOiJI..." > ~/.config/plaud/token
chmod 600 ~/.config/plaud/token
```

**EU region users** - set the region or API domain:
```bash
export PLAUD_REGION=eu
# or explicitly: export PLAUD_API_DOMAIN=https://api-euc1.plaud.ai
```

> The server auto-detects region mismatches and redirects automatically, but setting the correct region avoids the extra round-trip.

### 4. Connect to Claude

**Claude Code (CLI):**
```bash
# Basic setup
claude mcp add plaud-notes -- python -m plaud_notes_mcp.server

# With environment variable for token
claude mcp add plaud-notes -e PLAUD_TOKEN=your_token_here -- python -m plaud_notes_mcp.server

# With virtual environment
claude mcp add plaud-notes -e PLAUD_TOKEN=your_token_here -- /path/to/PlaudNotes/venv/bin/python -m plaud_notes_mcp.server

# Verify it's registered
claude mcp list
```

**Claude Desktop:**

Edit your config file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "plaud-notes": {
      "command": "python",
      "args": ["-m", "plaud_notes_mcp.server"],
      "cwd": "/path/to/PlaudNotes",
      "env": {
        "PLAUD_TOKEN": "your_token_here"
      }
    }
  }
}
```

Fully quit and restart Claude Desktop after saving.

## Available Tools

Once connected, Claude has access to 12 tools:

| Tool | Description |
|------|-------------|
| `list_recordings` | Browse recordings with titles, durations, dates, and transcript/summary status |
| `get_transcript` | Get the full transcript of a recording with speaker labels |
| `get_summary` | Get the AI-generated summary and notes for a recording |
| `get_recording_detail` | Get complete metadata, transcript, and AI content for a recording |
| `search_notes` | Search across all recordings for specific content in titles, transcripts, or summaries |
| `get_recent_context` | Load transcripts and summaries from your N most recent recordings at once |
| `get_recordings_by_tag` | Get all recordings within a specific tag/folder |
| `list_tags` | List your organizational tags and folders |
| `list_speakers` | List all identified speakers across recordings |
| `get_audio_url` | Get a temporary pre-signed audio download URL |
| `get_user_info` | Check your Plaud account information and membership status |
| `list_devices` | List connected Plaud devices (NotePin, Note, Note Pro) |

## Example Conversations

Once configured, you can ask Claude things like:

- *"Load my last 5 Plaud recordings for context"* - uses `get_recent_context`
- *"Show me my recent Plaud Notes recordings"* - uses `list_recordings`
- *"Get the transcript from my meeting yesterday"* - uses `get_transcript`
- *"Search my notes for anything about the Q4 budget"* - uses `search_notes`
- *"Summarize the key points from my last 3 recordings"* - uses `get_recent_context` + analysis
- *"What did we discuss about the product roadmap?"* - uses `search_notes`
- *"Show me all recordings tagged as Work"* - uses `list_tags` + `get_recordings_by_tag`
- *"Who were the speakers in my last meeting?"* - uses `list_speakers`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Authentication error` | Your token may be expired. Sign into web.plaud.ai again and get a new token. |
| `No recordings found` | Ensure "Private Cloud Sync" is enabled in the Plaud mobile app (Me > Private Cloud Sync). |
| `Region mismatch` | The server auto-redirects, but you can explicitly set `PLAUD_REGION=eu` if your account is in the EU. |
| `Connection refused` | Verify the server is running. Test with `python -m plaud_notes_mcp.server` directly. |

## Architecture

```
src/plaud_notes_mcp/
  __init__.py          # Package metadata
  plaud_client.py      # Plaud API client (auth, recordings, transcripts, summaries)
  server.py            # MCP server (12 tools + 3 resources)
```

The server uses the Plaud web API (the same API that powers web.plaud.ai). This is a reverse-engineered, unofficial API - it is not endorsed by Plaud and may change without notice.

## Security Notes

- Your Plaud bearer token grants full read access to your account's recordings
- Never commit your `.env` file or token to version control (`.gitignore` covers this)
- The token is valid for ~10 months; refresh by signing into web.plaud.ai again
- Token is stored locally and only sent to Plaud's own API servers

## License

MIT
