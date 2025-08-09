# 🎯 MCP Server Configuration in Cursor

## 🔧 Steps to configure the MCP Spotify Player server in Cursor

### 1. Prepare the MCP configuration

1. **Copy the configuration file**:
   ```bash
   cp mcp-spotify-player.yaml ~/.cursor/mcp-servers/
   ```

2. **Edit the configuration** (`~/.cursor/mcp-servers/mcp-spotify-player.yaml`):
   ```yaml
   mcpServers:
     spotify-player:
       command: python
       args:
         - start_mcp_server.py
       env:
         SPOTIFY_CLIENT_ID: "your_client_id_here"
         SPOTIFY_CLIENT_SECRET: "your_client_secret_here"
         SPOTIFY_REDIRECT_URI: "http://127.0.0.1:8000/auth/callback"
       cwd: "Z:/projects/mcp/mcp-spotify-player"  # CHANGE THIS to your actual path
       description: "MCP server to control Spotify from Claude"
       capabilities:
         tools: {}
   ```

### 2. Set environment variables

**IMPORTANT**: Make sure the environment variables are correctly configured:

1. **Create the `env` file** at the project root:
   ```bash
   cp env.example env
   ```

2. **Edit the `env` file** with your Spotify credentials:
   ```env
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback
   ```

### 3. Get Spotify credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Obtain your `CLIENT_ID` and `CLIENT_SECRET`
4. In the app settings, add `http://127.0.0.1:8000/auth/callback` as a redirect URI

### 4. Restart Cursor

1. **Close Cursor completely**
2. **Reopen Cursor**
3. **Start a new conversation**

### 5. Verify the connection

When you open a conversation in Cursor, you should see in the logs:
```
[spotify-player] [info] Initializing server...
[spotify-player] [info] Server started and connected successfully
```

## 🎵 Server usage

### Authentication

1. **The server will connect automatically** when you open a conversation
2. **To authenticate with Spotify**, use the command:
   ```
   /auth
   ```
   Or visit: `http://127.0.0.1:8000/auth`

### Available commands

Once authenticated, you can use these natural commands:

- **"Play Bohemian Rhapsody"**
- **"Pause the music"**
- **"Next song"**
- **"Previous song"**
- **"Set volume to 50%"**
- **"Search for songs by Queen"**
- **"What’s playing?"**

## 🐛 Troubleshooting

### Timeout error

If you see this error:
```
McpError: MCP error -32001: Request timed out
```

**Solutions**:
1. ✅ **Check MCP configuration**: Ensure `start_mcp_server.py` is in the args
2. ✅ **Check cwd**: Must be the full path to your project
3. ✅ **Check environment variables**: Must be set in the `env` file
4. ✅ **Restart Cursor**: After changing the configuration

### Browser not responding

**IMPORTANT**: The MCP stdio server does NOT use HTTP. Do not open the browser when using Cursor.

- ❌ **Do not use**: `http://127.0.0.1:8000`
- ✅ **Use**: Direct commands in Cursor

### Authentication error

If you see "Not authenticated with Spotify":
1. Visit `http://127.0.0.1:8000/auth`
2. Complete the Spotify authentication flow
3. Check that the credentials in `env` are correct

### Verify the server works

Run the local test:
```bash
python test_mcp_server.py
```

You should see:
```
✅ Server started successfully
✅ Response received
✅ Tools available
✅ Test completed successfully
```

## 📁 File structure

```
mcp-spotify-player/
├── start_mcp_server.py        # Main script for Cursor
├── src/mcp_stdio_server.py    # MCP stdio server
├── mcp-spotify-player.yaml    # MCP configuration
├── env                        # Environment variables
└── test_mcp_server.py         # Test script
```

## 🔄 Updates

If you update the code:
1. **Restart Cursor** to load the changes
2. **Or run**: `python test_mcp_server.py` to verify it works

## 📞 Support

If you encounter issues:
1. Run `python test_mcp_server.py` to check the server
2. Check the Cursor logs in the developer console
3. Verify the MCP configuration is correct
4. Ensure environment variables are set