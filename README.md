# 🎵 MCP Spotify Player

Control your Spotify music from Claude using the MCP (Model Context Protocol).

## 🚀 Features

- **Playback control**: Play, pause, skip songs
- **Volume control**: Adjust volume from 0 to 100%
- **Music search**: Search for songs, artists, and albums
- **Playlist management**: List, rename and clear your playlists
- **Integration with Claude**: Use natural commands to control your music

## 📋 Requirements

- Python 3.8+
- Spotify Premium account
- Registered application in the Spotify Developer Dashboard

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repository>
   cd mcp-spotify-player
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example env
   ```
   
   Edit the `env` file with your Spotify credentials:
   ```env
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback
   ```

## 🔐 Spotify Configuration

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Get your `CLIENT_ID` and `CLIENT_SECRET`
4. In the app settings, add `http://127.0.0.1:8000/auth/callback` as a redirect URI

## 🎯 Usage with Cursor

### MCP Server configuration

1. **Copy the MCP configuration**:
   ```bash
   cp mcp-spotify-player.yaml ~/.cursor/mcp-servers/
   ```

2. **Edit the configuration**:
   - Change `cwd` to the actual path of your project
   - Set environment variables with your credentials

3. **Restart Cursor** to load the new configuration

### Authentication

1. **Start Cursor** and open a conversation
2. **The MCP server will connect automatically**
3. **To authenticate with Spotify**, use the command:
   ```
   /auth
   ```
   Or visit: `http://127.0.0.1:8000/auth`

### Available commands

Once authenticated, you can use these commands:

- `play_music` — "Play Bohemian Rhapsody"
- `pause_music` — "Pause the music"
- `skip_next` — "Next song"
- `skip_previous` — "Previous song"
- `set_volume` — "Set volume to 50%"
- `get_current_playing` — "What's playing?"
- `get_playback_state` — "What's the playback state?"
- `search_music` — "Search for songs by Queen"
- `get_playlists` — "List my playlists"
- `get_playlist_tracks` — "Show tracks in playlist 'Road Trip'"
- `create_playlist` — "Create playlist 'Road Trip' with these songs..."
- `rename_playlist` — "Rename playlist 'Road Trip' to 'Vacation'"
- `clear_playlist` — "Remove all songs from playlist 'Road Trip'"
- `add_tracks_to_playlist` — "Add these songs to playlist 'Road Trip'"

## 🔧 Development

### Project structure

```
mcp-spotify-player/
├── src/
│   ├── config.py              # Configuration
│   ├── spotify_client.py      # Spotify client
│   ├── spotify_controller.py  # Main controller
│   ├── mcp_models.py          # MCP models
│   ├── mcp_server.py          # HTTP server (legacy)
│   └── mcp_stdio_server.py    # MCP stdio server
├── start_mcp_server.py        # MCP startup script
├── main.py                    # Main HTTP server
├── mcp-spotify-player.yaml    # MCP configuration
└── requirements.txt           # Dependencies
```

### Available servers

1. **HTTP server** (`main.py`):
   - For web use and testing
   - REST endpoints
   - Documentation at `/docs`

2. **MCP stdio server** (`start_mcp_server.py`):
   - For integration with Cursor
   - JSON-RPC protocol over stdio
   - Direct communication with Claude

### Run in development mode

```bash
# HTTP server (for testing)
python main.py

# MCP stdio server (for Cursor)
python start_mcp_server.py
```

## 🐛 Troubleshooting

### Timeout error in Cursor

If you see this error in Cursor logs:
```
McpError: MCP error -32001: Request timed out
```

**Solution**:
1. Make sure you are using `start_mcp_server.py` in the MCP configuration
2. Ensure environment variables are set
3. Check that `cwd` in the configuration is correct

### Authentication error

If you see "Not authenticated with Spotify":
1. Visit `http://127.0.0.1:8000/auth`
2. Complete the Spotify authentication flow
3. Verify that the credentials in `env` are correct

### Browser not responding

**IMPORTANT**: The MCP stdio server does NOT use HTTP. Do not open the browser when using Cursor. The server communicates directly via stdio.

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
