from mcp_spotify_player.mcp_stdio_server import MCPServer


def test_get_artist_albums_in_stdio_manifest():
    server = MCPServer()
    tool_names = [tool["name"] for tool in server.manifest["tools"]]
    assert "get_artist_albums" in tool_names
