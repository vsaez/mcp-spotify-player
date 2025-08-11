from src.mcp_stdio_server import MCPServer


def test_create_playlist_in_stdio_manifest():
    server = MCPServer()
    tool_names = [tool["name"] for tool in server.manifest["tools"]]
    assert "create_playlist" in tool_names
