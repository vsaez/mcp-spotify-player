# 🎵 MCP Server for Spotify

MCP Server for Spotify lets you control your Spotify music from Claude using the MCP (Model Context Protocol).

## 🚀 Features

- **Playback control**: Play, pause, skip songs
- **Playback status**: Check current song and device status
- **Device information**: List available playback devices
- **Volume control**: Adjust volume from 0 to 100%
- **Repeat mode**: Set to off, context, or track
- **Queue management**: Add items to the queue and view upcoming tracks
- **Music search**: Search for songs, artists, and albums
- **Collection search**: Find public playlists or albums
- **Album browsing**: View album details and track lists
- **Artist info**: View artist details by ID
- **Artist albums**: View albums of an artist by ID
- **Artist top tracks**: View top tracks of an artist by ID
- **Saved albums**: List albums saved in your library
- **Check saved albums**: Verify if albums are in your library
- **Save albums**: Add albums to your library
- **Delete saved albums**: Remove albums from your library
- **Playlist management**: List playlists, retrieve tracks, create, rename, clear, and add tracks
- **Diagnostics**: Display authentication and environment info
- **Integration with Claude**: Use natural commands to control your music

## 📋 Requirements

- Python 3.10+
- Spotify Premium account
- Registered application in the Spotify Developer Dashboard

## 🔧 Installation

1. **Clone the repository**:

```bash
   git clone <your-repository>
   cd mcp-spotify-player
```

2. **Install**:

```bash
  pip install .
```

For development:

```bash
  pip install -e .
```

3. **Set up environment variables**:

```bash
cp env.example .env
```

Edit the `.env` file with your Spotify credentials:

```env
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback
   # Optional: custom path to store OAuth tokens
   # Defaults to ~/.config/mcp_spotify_player/tokens.json
   MCP_SPOTIFY_TOKENS_PATH=/path/to/tokens.json
```

Note: dependencies are managed with `pyproject.toml`.

If `MCP_SPOTIFY_TOKENS_PATH` is not set, tokens will be stored in
   `~/.config/mcp_spotify_player/tokens.json` by default.

## ⚡ Quick start

1. Trigger the `/auth` command from your MCP client.
2. A browser window opens for Spotify login. After approving access you will see a
   confirmation page from **mcp-spotify-player** with a close button.
3. Tokens are saved to `tokens.json` (by default under `~/.config/mcp_spotify_player/`).
4. Back in your client, try a simple command like `get_current_playing` to verify
   authentication.

### What can I ask Claude?

- `auth`
- `play_music`
- `pause_music`
- `skip_next`
- `skip_previous`
- `set_volume`
- `set_repeat`
- `get_current_playing`
- `get_playback_state`
- `get_devices`
- `search_music`
- `search_collections`
- `get_playlists`
- `get_playlist_tracks`
- `get_artist`
- `get_artist_albums`
- `get_artist_top_tracks`
- `get_album`
- `get_albums`
- `get_album_tracks`
- `get_saved_albums`
- `check_saved_albums`
- `save_albums`
- `delete_saved_albums`
- `create_playlist`
- `rename_playlist`
- `clear_playlist`
- `add_tracks_to_playlist`
- `queue_add`
- `queue_list`
- `diagnose`

### Token file format

```json
{
  "access_token": "ACCESS",
  "refresh_token": "REFRESH",
  "expires_at": 1700000000,
  "scopes": [
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "user-read-recently-played",
    "user-read-playback-position",
    "user-top-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-private",
    "user-library-read",
    "user-library-modify"
  ]
}
```

## User Authentication (PKCE)

The server uses Spotify's PKCE OAuth flow:

1. A random `code_verifier` and its SHA-256 `code_challenge` are created.
2. Your browser opens the Spotify authorization page.
3. Spotify redirects back to `http://127.0.0.1:8000/auth/callback` where a local
   handler completes the flow and displays a confirmation page.
4. Access and refresh tokens are stored in `tokens.json` and refreshed as needed.

Make sure your Spotify app configuration includes the redirect URI above and the
required scopes from `env.example`. Set the `SPOTIFY_CLIENT_ID` and, if using
the confidential flow, `SPOTIFY_CLIENT_SECRET` as environment variables.

## 🔐 Spotify Configuration

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Get your `CLIENT_ID` and `CLIENT_SECRET`
4. In the app settings, add `http://127.0.0.1:8000/auth/callback` as a redirect URI

## 🐍 Quick Python Demo

```python
from mcp_spotify_player.spotify_controller import SpotifyController
from mcp_spotify_player.client_auth import load_tokens
c = SpotifyController(load_tokens)
if not c.is_authenticated():
    raise SystemExit("Run the auth tool first")
c.play_music(query="Where Is My Mind by The Pixies")
current = c.get_current_playing()
name = current["item"]["name"]
artist = current["item"]["artists"][0]["name"]
print(f"{name} – {artist}")
```

## Integration with Claude

This section consolidates everything needed to integrate the MCP stdio server with Claude (Anthropic). It explains configuration for Claude Desktop and other MCP-compatible clients, how to authenticate, example commands, and troubleshooting notes.

### Overview

- Recommended server command: `python -m mcp_spotify_player` (JSON-RPC over stdio).
- If Claude cannot find a tokens file and the server attempts to open a browser, configure the MCP server inside Claude/Claude Desktop with proper environment variables prior to running `/auth`.

### Claude Desktop configuration

1. Open Claude Desktop → Settings → MCP Servers
2. Add a server configuration (e.g. `claude-desktop-config.json`) with these fields:
   - `command`: path to your Python interpreter
   - `args`: ["-m", "mcp_spotify_player"]
   - `cwd`: project path (e.g. "Z:/projects/mcp/mcp-spotify-player")
   - `env`: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

Example JSON:

```json
{
  "mcpServers": {
    "spotify-player": {
      "command": "path_to_your_python",
      "args": ["-m", "mcp_spotify_player"],
      "cwd": "Z:/projects/mcp/mcp-spotify-player",
      "env": {
        "SPOTIFY_CLIENT_ID": "your_actual_client_id",
        "SPOTIFY_CLIENT_SECRET": "your_actual_client_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8000/auth/callback"
      },
      "description": "MCP server to control Spotify"
    }
  }
}
```

> Do not commit real credentials to the repository.


### Configuring MCP Server in PyCharm / IntelliJ

JetBrains IDEs (PyCharm, IntelliJ, etc.) with GitHub Copilot have native support for MCP servers.

1. Go to **File → Settings → GitHub Copilot → Model Context Protocol (MCP)**.
2. On the right side, click **Configure** to edit the `mcp.json` file.
3. Add the following snippet, replacing the paths and dummy credentials as needed:

```json
{
  "servers": {
    "spotify-player": {
      "command": "C:/Users/YourUser/AppData/Local/Programs/Python/Python311/python.exe",
      "args": ["-m", "mcp_spotify_player"],
      "cwd": "Z:/projects/mcp/mcp-spotify-player",
      "env": {
        "SPOTIFY_CLIENT_ID": "your-client-id",
        "SPOTIFY_CLIENT_SECRET": "your-client-secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8000/auth/callback"
      }
    }
  }
}
```

Replace `your-client-id` and `your-client-secret` with the credentials from your Spotify Developer Dashboard. **Do not commit your real credentials into version control.**

Once configured, the server will appear in the Copilot Agent inside PyCharm/IntelliJ, and tools like `/auth`, `/play_music`, and `/pause_music` can be invoked directly.


### Other MCP clients

Use `mcp-spotify-player.yaml` as a template (same fields: command, args, cwd, env).

### Authentication flow

- Start the server manually to verify: `python -m mcp_spotify_player`.
- From Claude run `/auth` (or `auth`) to start the authorization flow.
- Tokens are saved by default to `~/.config/mcp_spotify_player/tokens.json` (or the path in `MCP_SPOTIFY_TOKENS_PATH`).

### Troubleshooting

- "Server not found" / timeout: check the server is running and `cwd` is correct in Claude's configuration.
- "Authentication required": run `/auth` in Claude after configuring the server.
- "Invalid credentials": verify environment variables and redirect URI in your Spotify app.
- MCP timeout (-32001): ensure you configured the command as `python -m mcp_spotify_player` (stdio) and restart Claude after changes.
- Browser not responding: the stdio server does not use HTTP; do not expect an HTTP server to be reachable from Claude.

### Example usage

User: "Play REM"
Claude: [play_music with query="REM"]

User: "Pause the music"
Claude: [pause_music]

User: "Set volume to 80%"
Claude: [set_volume with volume_percent=80]

User: "What's playing now?"
Claude: [get_current_playing]

- `play_music` — "Play Where Is My Mind by The Pixies"
- `pause_music` — "Pause the music"
- `skip_next` — "Next song"
- `skip_previous` — "Previous song"
- `set_volume` — "Set volume to 50%"
- `set_repeat` — "Set repeat mode to `off`, `track`, or `context` (e.g., "Repeat current track")"
- `get_current_playing` — "What's playing?"
- `get_playback_state` — "What's the playback state?"
- `get_devices` — "List my available devices"
- `search_music` — "Search for songs by Queen"
- `search_collections` — "Search for playlists or albums"
- `get_playlists` — "List my playlists"
- `get_playlist_tracks` — "Show tracks in playlist 'Road Trip'"
- `get_artist` — "Show info about artist with a given ID"
- `get_artist_albums` — "Show albums of an artist by ID"
- `get_artist_top_tracks` — "Show top tracks of an artist by ID"
- `get_album` — "Show info about album 'The Dark Side of the Moon'"
- `get_albums` — "Show info about multiple albums"
- `get_album_tracks` — "Show tracks in album 'The Dark Side of the Moon'"
- `get_saved_albums` — "List my saved albums"
- `check_saved_albums` — "Check if these albums are saved"
- `save_albums` — "Save these albums to my library"
- `delete_saved_albums` — "Remove these albums from my library"
- `create_playlist` — "Create playlist 'Road Trip' with these songs..."
- `rename_playlist` — "Rename playlist 'Road Trip' to 'Vacation'"
- `clear_playlist` — "Remove all songs from playlist 'Road Trip'"
- `add_tracks_to_playlist` — "Add these songs to playlist 'Road Trip'"
- `queue_add` — "Add this track to the queue"
- `queue_list` — "Show the upcoming queue"
- `diagnose` — "Display diagnostic information"


### Prompt Examples

Copy and paste these prompts into your MCP client:

```
Play "Where Is My Mind?" by The Pixies
Search for albums by R.E.M.
Add "Cayetano" by Carolina Durante to my queue
Create a playlist called "Indie Mix" and add "Debaser" by The Pixies
```

### Required scopes

| Feature | Scopes |
| ------- | ------ |
| Playback control & status | `user-read-playback-state`, `user-modify-playback-state`, `user-read-currently-playing`, `user-read-playback-position` |
| Playback insights | `user-read-recently-played`, `user-top-read` |
| Playlist management | `playlist-read-private`, `playlist-read-collaborative`, `playlist-modify-private` |
| Library access | `user-library-read`, `user-library-modify` |

## 🔧 Development

### Project structure

```
mcp-spotify-player/
├── src/
│   ├── mcp_logging/
│   │   └── __init__.py
│   ├── mcp_spotify/
│   │   ├── __init__.py
│   │   └── errors.py
│   └── mcp_spotify_player/
│       ├── __init__.py
│       ├── __main__.py
│       ├── album_controller.py
│       ├── cli.py
│       ├── client_albums.py
│       ├── client_auth.py
│       ├── client_playback.py
│       ├── client_playlists.py
│       ├── client_artists.py
│       ├── config.py
│       ├── mcp_manifest.py
│       ├── mcp_models.py
│       ├── mcp_stdio_server.py
│       ├── playback_controller.py
│       ├── playlist_controller.py
│       ├── artists_controller.py
│       ├── spotify_client.py
│       └── spotify_controller.py
├── pyproject.toml
└── requirements.txt
```

### MCP stdio server

- For integration with MCP clients
- JSON-RPC protocol over stdio
- Direct communication with Claude

### Run in development mode

```bash
mcp-spotify-player
# or
python -m mcp_spotify_player
```

## 🐛 Troubleshooting

### Timeout error

If you see this error in client logs:

```
McpError: MCP error -32001: Request timed out
```

**Solution**:

1. Make sure you are using `mcp-spotify-player` in the MCP configuration
2. Ensure environment variables are set
3. Check that `cwd` in the configuration is correct

### Authentication error

If you see "Not authenticated with Spotify":

1. Run the `/auth` command in your MCP client
2. Verify that the credentials in `.env` are correct

### Browser not responding

**IMPORTANT**: The MCP stdio server does NOT use HTTP. Do not open the browser when using MCP clients. The server
communicates directly via stdio.

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the project
2. Create a branch for your feature
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 Support

If you have issues:

1. Check the troubleshooting section
2. Open an issue on GitHub
3. Include error logs and your configuration
