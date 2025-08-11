from mcp_spotify_player.mcp_stdio_server import MCPServer
from mcp_spotify_player.mcp_manifest import MANIFEST


def test_manifest_loaded():
    server = MCPServer()
    assert server.manifest == MANIFEST
