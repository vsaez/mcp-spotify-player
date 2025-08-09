from src.mcp_stdio_server import MCPServer
from src.mcp_server import MCP_MANIFEST


def test_create_playlist_in_stdio_manifest():
    server = MCPServer()
    tool_names = [tool["name"] for tool in server.manifest["tools"]]
    assert "create_playlist" in tool_names


def test_create_playlist_in_http_manifest():
    tool_names = [tool["name"] for tool in MCP_MANIFEST["tools"]]
    assert "create_playlist" in tool_names
