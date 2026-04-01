# Plaud Notes MCP Server

Connect your Plaud voice recorder to Claude. Claude gets access to your recordings, transcripts, and AI summaries -- so you can ask it about anything you've ever recorded.

> **New here? No coding experience?** Follow the [Step-by-Step Setup Guide](https://github.com/jameshenning/PlaudNotes/issues/2) -- it walks you through everything with checkboxes.
>
> **Before you start:** Read the [Security Setup Guide](SECURITY_SETUP.md) to lock down your Claude account first. Your Plaud Notes contain private conversations -- make sure they stay private.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/plaud-notes?referralCode=plaud)

## What Can Claude Do With Your Plaud Notes?

Once connected, just talk to Claude naturally:

- *"Show me my recent recordings"*
- *"Get the transcript from my meeting yesterday"*
- *"Search my notes for anything about the Q4 budget"*
- *"Summarize my last 3 recordings"*
- *"What did we discuss about hiring?"*
- *"Load my last 5 recordings for context, then help me write a follow-up email"*

## Features

- **Browse Recordings** - See all your notes with titles, durations, and dates
- **Full Transcripts** - Complete transcriptions with speaker labels
- **AI Summaries** - Plaud's AI-generated summaries and notes
- **Search Everything** - Find any topic across all your recordings
- **Bulk Context Loading** - Pull recent transcripts into Claude in one go
- **Tags, Speakers, Devices** - Filter by folder, see who spoke, check your devices

## Quick Start

**The short version (3 steps):**
1. Get your token from [web.plaud.ai](https://web.plaud.ai) (DevTools → Local Storage → `tokenstr`)
2. Deploy this server (click the Railway button above, or use Docker)
3. Point Claude at it

**Detailed instructions below, or see the [full beginner guide](https://github.com/jameshenning/PlaudNotes/issues/2).**

---

### 1. Get Your Plaud Token

1. Sign in to [web.plaud.ai](https://web.plaud.ai)
2. Open browser DevTools (`F12` or `Cmd+Option+I`)
3. Go to **Application** tab (or **Storage** in Firefox) → **Local Storage** → `https://web.plaud.ai`
4. Find `tokenstr` and copy its value
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

## Remote Deployment (Docker)

Deploy the server to the cloud so Claude connects to it over HTTP -- no local install needed.

> **Security:** Always set `PLAUD_MCP_API_KEY` when deploying over HTTP. This requires all MCP clients to authenticate with a Bearer token, preventing unauthorized access to your recordings.
>
> Generate a key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### Docker (self-hosted)

```bash
# Clone and configure
git clone https://github.com/jameshenning/PlaudNotes.git
cd PlaudNotes
cp .env.example .env
# Edit .env: set PLAUD_TOKEN, PLAUD_MCP_API_KEY, and optionally PLAUD_REGION

# Run with Docker Compose
docker compose up -d

# Server is now running at http://localhost:8000/mcp
```

Then connect Claude Code to the remote server:
```bash
# Without API key auth
claude mcp add --transport http plaud-notes http://localhost:8000/mcp

# With API key auth (pass as header)
claude mcp add --transport http -H "Authorization: Bearer YOUR_API_KEY" plaud-notes http://localhost:8000/mcp
```

### Railway (one-click cloud)

1. Push this repo to your GitHub
2. Go to [railway.app](https://railway.app), create a new project from your repo
3. Add environment variables in the Railway dashboard:
   - `PLAUD_TOKEN` = your Plaud token
   - `PLAUD_MCP_API_KEY` = a generated API key (see above)
   - `PLAUD_TRANSPORT` = `http`
   - `PLAUD_MCP_HOST` = `0.0.0.0`
   - `PLAUD_REGION` = `us` (or `eu`)
4. Railway auto-detects the `Dockerfile` and deploys
5. Copy your Railway URL and connect Claude:
   ```bash
   claude mcp add --transport http plaud-notes https://your-app.up.railway.app/mcp
   ```

### Fly.io

```bash
# Install the Fly CLI, then:
cd PlaudNotes
fly launch --no-deploy

# Set secrets (never in fly.toml)
fly secrets set PLAUD_TOKEN="eyJhbGciOiJI..."
fly secrets set PLAUD_MCP_API_KEY="your_generated_key"

# Deploy
fly deploy

# Connect Claude to your Fly app
claude mcp add --transport http plaud-notes https://plaud-notes-mcp.fly.dev/mcp
```

### Render / Generic Docker Host

Any platform that runs Docker containers works. Set these environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PLAUD_TOKEN` | Yes | - | Your Plaud bearer token |
| `PLAUD_MCP_API_KEY` | Recommended | - | API key for HTTP auth (Bearer token) |
| `PLAUD_TRANSPORT` | Yes (remote) | `stdio` | Set to `http` for remote deployment |
| `PLAUD_MCP_HOST` | No | `0.0.0.0` | Bind address |
| `PLAUD_MCP_PORT` | No | `8000` | Listen port |
| `PLAUD_REGION` | No | `us` | `us` or `eu` |
| `PLAUD_API_DOMAIN` | No | - | Override API URL directly |

### Connect Claude Desktop to a Remote Server

For Claude Desktop, add the remote URL to your config:

```json
{
  "mcpServers": {
    "plaud-notes": {
      "type": "http",
      "url": "https://your-deployment-url.example.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

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
| `Connection refused` (local) | Verify the server is running. Test with `python -m plaud_notes_mcp.server` directly. |
| `Connection refused` (remote) | Check that `PLAUD_TRANSPORT=http` and `PLAUD_MCP_HOST=0.0.0.0` are set. Check your cloud platform logs. |
| Docker container exits | Run `docker compose logs` to see the error. Usually a missing `PLAUD_TOKEN`. |

## Architecture

```
PlaudNotes/
  src/plaud_notes_mcp/
    __init__.py          # Package metadata
    plaud_client.py      # Plaud API client (auth, recordings, transcripts, summaries)
    server.py            # MCP server (12 tools, 3 resources, stdio + HTTP transport)
  Dockerfile             # Container image for remote deployment
  docker-compose.yml     # One-command local Docker setup
  fly.toml               # Fly.io deployment config
  railway.toml           # Railway deployment config
  Procfile               # Generic PaaS entry point
  pyproject.toml         # Python package definition
  .env.example           # Configuration template
```

The server uses the Plaud web API (the same API that powers web.plaud.ai). This is a reverse-engineered, unofficial API -- it is not endorsed by Plaud and may change without notice.

**Transport modes:**
- **stdio** (default) -- for local use with Claude Code CLI and Claude Desktop
- **HTTP** (`PLAUD_TRANSPORT=http`) -- for remote/cloud deployment, serves at `/mcp`

## Security Notes

> **Important:** Before connecting sensitive data, follow the [Security Setup Guide](SECURITY_SETUP.md) to harden your Claude account (disable training, pause memory, enable 2FA).

**Your data flow:**
- Raw audio files stay on Plaud's servers -- they are never sent to Claude
- Only transcript text and summaries (returned by MCP tools) are sent to Claude's API
- With training OFF, Anthropic retains data for 30 days only and never trains on it
- Using Incognito Chats means nothing is stored at all

**Server security:**
- Your Plaud bearer token is stored locally and only sent to Plaud's own API servers
- When deployed over HTTP, set `PLAUD_MCP_API_KEY` to require authentication
- All `file_id` inputs are validated against path traversal and injection attacks
- API redirects are restricted to known Plaud domains only
- Docker container runs as non-root with read-only filesystem
- Never commit your `.env` file or token to version control (`.gitignore` covers this)

## Need Help?

- [Security Setup Guide](SECURITY_SETUP.md) -- Lock down your Claude account before connecting
- [Step-by-Step Setup Guide](https://github.com/jameshenning/PlaudNotes/issues/2) -- Beginner-friendly checklist
- [Open an Issue](https://github.com/jameshenning/PlaudNotes/issues/new) -- Report bugs or ask questions

## License

MIT
