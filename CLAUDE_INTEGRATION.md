# 🎵 MCP Server Integration with Claude

## 📋 Steps to integrate the MCP server with Claude

### 1. **Configure the configuration file**

**Option A - Claude Desktop:**
1. Open Claude Desktop
2. Go to Settings → MCP Servers
3. Add the `claude-desktop-config.json` file
4. **IMPORTANT:** Edit the file and change:
   - `"tu_client_id_aqui"` to your actual CLIENT_ID
   - `"tu_client_secret_aqui"` to your actual CLIENT_SECRET
   - `"path_to_your_python"` to your Python interpreter path
   - `"Z:/projects/mcp/mcp-spotify-player"` to your actual path

**Option B - Other MCP clients:**
1. Use the `mcp-spotify-player.yaml` file
2. Edit the credentials as above

### 2. **Verify the server is running**

Before integrating with Claude, make sure the server is running:

```bash
# In your terminal, from the project folder:
python -m mcp_spotify_player
```

### 3. **Authenticate with Spotify**

Run the `/auth` command in your MCP client to start the authentication process.

### 4. **Use with Claude**

Once configured, you can say to Claude:
```
"Play REM"
"Pause the music"
"Skip to the next song"
"Set volume to 80%"
"What’s playing now?"
```

## 🔧 Example configuration

### For Claude Desktop (`claude-desktop-config.json`):
```json
{
  "mcpServers": {
    "spotify-player": {
      "command": "path_to_your_python",
      "args": ["-m", "mcp_spotify_player"],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_actual_client_id",
        "SPOTIFY_CLIENT_SECRET": "your_actual_client_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8000/auth/callback"
      },
      "cwd": "Z:/projects/mcp/mcp-spotify-player",
      "description": "MCP server to control Spotify"
    }
  }
}
```

### For other clients (`mcp-spotify-player.yaml`):
```yaml
mcpServers:
  spotify-player:
    command: path_to_your_python
    args:
      - -m
      - mcp_spotify_player
    env:
      SPOTIFY_CLIENT_ID: "your_actual_client_id"
      SPOTIFY_CLIENT_SECRET: "your_actual_client_secret"
      SPOTIFY_REDIRECT_URI: "http://127.0.0.1:8000/auth/callback"
    cwd: "Z:/projects/mcp/mcp-spotify-player"
    description: "MCP server to control Spotify"
    capabilities:
      tools: {}
```

## 🎯 Available commands

Once integrated, Claude can use these commands:

- `play_music` - Play music
- `pause_music` - Pause playback
- `skip_next` - Next track
- `skip_previous` - Previous track
- `set_volume` - Change volume
- `get_current_playing` - Current track
- `get_playback_state` - Full playback state
- `get_devices` - List available devices
- `search_music` - Search music
- `get_playlists` - List playlists

## 🔧 Available server types

### MCP stdio server (Recommended for Claude)
- **Command**: `python -m mcp_spotify_player`
- **Protocol**: JSON-RPC over stdio
- **Usage**: Direct integration with MCP-compatible clients
- **Communication**: Direct, no HTTP

**Note**: For integration with Claude, always use the MCP stdio server (`python -m mcp_spotify_player`).

## 🐛 Troubleshooting

### Error: "Server not found" or timeout
- Check the server is running with `python -m mcp_spotify_player`
- Make sure the path in `cwd` is correct
- Ensure environment variables are set in the `.env` file

### Error: "Authentication required"
- Run the `/auth` command to authenticate

### Error: "Invalid credentials"
- Check that the credentials in the config file are correct
- Ensure the redirect URL matches your Spotify app configuration

### Timeout error
If you see `McpError: MCP error -32001: Request timed out`:
1. Verify you are using `python -m mcp_spotify_player` in your MCP configuration
2. Restart the client after changing the configuration
3. Ensure environment variables are set

### Browser not responding
**IMPORTANT**: The MCP stdio server does NOT use HTTP. Do not open the browser when using MCP clients.

## 📞 Support

If you have issues:
1. Verify the server runs manually with `python -m mcp_spotify_player`
2. Check the server logs
3. Review the Spotify Developer Dashboard configuration
