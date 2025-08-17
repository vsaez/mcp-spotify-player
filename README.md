# 🎵 MCP Spotify Player

Control your Spotify music from Claude using the MCP (Model Context Protocol).

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
- **Artist related artists**: View artists related to a given artist by ID
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

## 🔐 Spotify Configuration

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Get your `CLIENT_ID` and `CLIENT_SECRET`
4. In the app settings, add `http://127.0.0.1:8000/auth/callback` as a redirect URI

## 🛠️ Commands

After authenticating with Spotify, you can use these commands in your MCP client:

- `play_music` — "Play Bohemian Rhapsody"
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
- `get_artist_related_artists` — "Show artists related to a given artist by ID"
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

### Search – Playlists & Albums

Use the `search_collections` tool to find public playlists or albums.

```bash
/search_collections {"q": "study", "type": "playlist", "limit": 5}
```

Parameters:

| Name | Type | Description |
| ---- | ---- | ----------- |
| `q` | string | Search query (required) |
| `type` | string | `playlist` or `album` (required) |
| `limit` | integer | 1–50, default 20 |
| `offset` | integer | ≥0, default 0 |
| `market` | string | Optional ISO 3166-1 alpha-2 code |

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
