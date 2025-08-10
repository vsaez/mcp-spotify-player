from src.mcp_stdio_server import MCPServer
from src.mcp_manifest import MANIFEST


def test_manifest_loaded():
    server = MCPServer()
    assert server.manifest == MANIFEST
