# Plaud Notes MCP Server

An MCP (Model Context Protocol) server that connects your Plaud Notes account to Claude, giving Claude access to your voice recordings, transcripts, and AI summaries for context and historical reference.

## Features

- **List Recordings** - Browse all your Plaud Notes recordings with titles, durations, and dates
- **Get Transcripts** - Retrieve full transcriptions with speaker labels
- **Get AI Summaries** - Access Plaud's AI-generated summaries and notes
- **Search Notes** - Search across all your recordings by title, transcript content, or summary
- **Tags & Speakers** - View your organizational tags and identified speakers
- **Audio URLs** - Get temporary download links for recording audio files

## Prerequisites

- Python 3.10+
- A Plaud Notes account with recordings
- A bearer token from your Plaud account

## Getting Your Plaud Token

1. Go to [web.plaud.ai](https://web.plaud.ai) and sign in
2. Open your browser's Developer Tools (F12 or Cmd+Option+I)
3. Go to the **Network** tab
4. Click on any recording or navigate the app
5. Find a request to `api.plaud.ai` (or `api-euc1.plaud.ai` for EU)
6. Copy the `Authorization` header value (it starts with `bearer eyJ...`)
7. Remove the `bearer ` prefix - the remaining string is your token

Your token is valid for approximately 10 months.

## Installation

```bash
# Clone the repository
git clone https://github.com/jameshenning/PlaudNotes.git
cd PlaudNotes

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install the package
pip install -e ".[cli]"
```

## Configuration

Set your token using one of these methods:

### Option 1: Environment Variable
```bash
export PLAUD_TOKEN="eyJhbGciOiJI..."
```

### Option 2: .env File
```bash
cp .env.example .env
# Edit .env and add your token
```

### Option 3: Config File
```bash
mkdir -p ~/.config/plaud
echo "eyJhbGciOiJI..." > ~/.config/plaud/token
chmod 600 ~/.config/plaud/token
```

### EU Region Users
If your account is in the EU region:
```bash
export PLAUD_REGION=eu
# or
export PLAUD_API_DOMAIN=https://api-euc1.plaud.ai
```

## Usage with Claude Code (CLI)

```bash
# Add the MCP server to Claude Code
claude mcp add plaud-notes -- python -m plaud_notes_mcp.server

# Or with the full path
claude mcp add plaud-notes -- /path/to/venv/bin/python -m plaud_notes_mcp.server

# With environment variables
claude mcp add plaud-notes -e PLAUD_TOKEN=your_token_here -- python -m plaud_notes_mcp.server

# Verify it's registered
claude mcp list
```

## Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

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

Restart Claude Desktop after saving.

## Available Tools

Once connected, Claude can use these tools:

| Tool | Description |
|------|-------------|
| `list_recordings` | List your recordings with titles, durations, and dates |
| `get_transcript` | Get the full transcript of a recording with speaker labels |
| `get_summary` | Get the AI-generated summary of a recording |
| `get_recording_detail` | Get complete metadata, transcript, and AI content |
| `search_notes` | Search across all recordings for specific content |
| `list_tags` | List your organizational tags and folders |
| `list_speakers` | List identified speakers across recordings |
| `get_audio_url` | Get a temporary audio download URL |

## Example Conversations with Claude

Once configured, you can ask Claude things like:

- "Show me my recent Plaud Notes recordings"
- "Get the transcript from my meeting yesterday"
- "Search my notes for anything about the Q4 budget"
- "Summarize the key points from my last 3 recordings"
- "What did we discuss about the product roadmap?"
- "Find all recordings where we talked about hiring"

## Security Notes

- Your Plaud bearer token grants full access to your account's recordings
- Never commit your `.env` file or token to version control
- The token is valid for ~10 months; refresh by signing into web.plaud.ai again
- This server uses the reverse-engineered Plaud API; it is not officially supported by Plaud

## License

MIT
