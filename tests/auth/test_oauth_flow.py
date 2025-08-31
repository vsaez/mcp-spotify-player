import time
from unittest import mock

import requests

from mcp_spotify_player.mcp_stdio_server import MCPServer
from mcp_spotify_player.config import Config


def test_auth_flow_opens_browser_once(monkeypatch, tmp_path):
    port = 8765
    redirect = f"http://127.0.0.1:{port}/auth/callback"
    monkeypatch.setenv("SPOTIFY_REDIRECT_URI", redirect)
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "dummy")
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(tmp_path / "tokens.json"))
    monkeypatch.setattr(Config, "SPOTIFY_REDIRECT_URI", redirect)
    monkeypatch.setattr(
        "mcp_spotify_player.mcp_stdio_server.try_load_tokens", lambda: None
    )

    with mock.patch("webbrowser.open") as mock_open:
        server = MCPServer()

        result1 = server.execute_tool("auth", {})
        assert "Opened browser" in result1

        result2 = server.execute_tool("auth", {})
        assert "already in progress" in result2
        assert mock_open.call_count == 1

        resp = requests.get(
            f"http://127.0.0.1:{port}/auth/callback?code=abc",
            proxies={"http": None, "https": None},
        )
        assert resp.status_code == 200

        for _ in range(50):
            if not server.oauth_flow.in_progress():
                break
            time.sleep(0.1)

        assert mock_open.call_count == 1
