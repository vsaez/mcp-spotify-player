from mcp_spotify_player.mcp_stdio_server import MCPServer


def test_set_repeat_in_manifest():
    server = MCPServer()
    tool_names = [tool["name"] for tool in server.manifest["tools"]]
    assert "set_repeat" in tool_names
