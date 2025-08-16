from mcp_spotify_player.mcp_stdio_server import MCPServer


def test_get_album_tracks_in_manifest():
    server = MCPServer()
    tool_names = [tool["name"] for tool in server.manifest["tools"]]
    assert "get_album_tracks" in tool_names
