from mcp_spotify_player.mcp_stdio_server import MCPServer


def test_check_saved_albums_in_manifest():
    server = MCPServer()
    tool_names = [tool["name"] for tool in server.manifest["tools"]]
    assert "check_saved_albums" in tool_names
