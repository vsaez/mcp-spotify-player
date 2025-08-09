# 🎵 MCP Spotify Player - Resources and Context

## 📚 Reference Documentation

### Spotify API
- **Web API**: https://developer.spotify.com/documentation/web-api/
- **Authorization Code Flow**: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
- **Scopes**: https://developer.spotify.com/documentation/web-api/concepts/scopes

### Anthropic Model Context Protocol (MCP)
- **Tool Use Overview**: https://docs.anthropic.com/claude/docs/tool-use
- **GitHub Examples**: https://github.com/anthropics/tools-mcp
- **MCP Specification**: https://modelcontextprotocol.io/

## 🎯 Project Objective

Create an MCP server that allows Claude to control Spotify using natural commands such as:
- "Play REM"
- "Pause the music"
- "Skip to the next song"
- "Set the volume to 80%"
- "What’s playing now?"

## 🏗️ Implemented Architecture

### Main Components
1. **`src/config.py`** - Configuration and environment variables
2. **`src/spotify_client.py`** - Spotify API client with token management
3. **`src/spotify_controller.py`** - Business logic and command control
4. **`src/mcp_models.py`** - Pydantic models for MCP structures
5. **`src/mcp_server.py`** - FastAPI server with MCP endpoints

### Authentication Flow
1. User visits `/auth`
2. Redirect to Spotify OAuth
3. Callback with authorization code
4. Exchange for access_token and refresh_token
5. Local storage in `tokens.json`

### Available MCP Commands
- `play_music` - Play music
- `pause_music` - Pause playback
- `skip_next` - Next track
- `skip_previous` - Previous track
- `set_volume` - Change volume
- `get_current_playing` - Current track
- `get_playback_state` - Full playback state
- `search_music` - Search music
- `get_playlists` - List playlists

## 🔧 Required Configuration

### Environment Variables (.env)
```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8000/auth/callback
PORT=8000
HOST=0.0.0.0
DEBUG=True
```

### Required Spotify Scopes
- `user-read-playback-state`
- `user-modify-playback-state`
- `user-read-currently-playing`
- `user-read-recently-played`
- `user-read-playback-position`
- `user-top-read`
- `playlist-read-private`
- `playlist-read-collaborative`
- `user-library-read`
- `user-library-modify`

## 🚀 Quick Usage

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure credentials**: Edit `.env` with your Spotify details
3. **Start server**: `python main.py`
4. **Authenticate**: Visit `http://localhost:8000/auth`
5. **Test**: Run `python test_server.py`

## 📋 Server Endpoints

- `GET /` - Server information
- `GET /.well-known/mcp` - MCP manifest
- `POST /mcp` - MCP commands
- `GET /auth` - Start authentication
- `GET /auth/callback` - Authentication callback
- `GET /status` - Server status
- `GET /docs` - Swagger documentation

## 🎵 Example Usage with Claude

```
User: "Play REM"
Claude: [play_music with query="REM"]

User: "Pause the music"
Claude: [pause_music]

User: "Set volume to 80%"
Claude: [set_volume with volume_percent=80]

User: "What’s playing now?"
Claude: [get_current_playing]
```
