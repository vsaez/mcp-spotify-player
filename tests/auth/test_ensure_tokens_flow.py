import importlib
import json
import socket
import threading
import time as real_time
import urllib.request

import pytest


def test_ensure_tokens_creates_file_via_auth_flow(monkeypatch, tmp_path):
    path = tmp_path / "tokens.json"
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(path))
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "cid")
    monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("SPOTIFY_REDIRECT_URI", f"http://127.0.0.1:{port}/auth/callback")

    import mcp_spotify_player.config as config
    importlib.reload(config)
    import mcp_spotify_player.client_auth as client_auth
    importlib.reload(client_auth)

    path.unlink()
    monkeypatch.setattr(client_auth.secrets, "token_urlsafe", lambda n=16: "state")
    monkeypatch.setattr(client_auth.webbrowser, "open", lambda url: True)
    monkeypatch.setattr(
        client_auth,
        "exchange_code_for_tokens",
        lambda code: {"access_token": "a", "refresh_token": "r", "expires_in": 3600},
    )
    monkeypatch.setattr(client_auth.time, "time", lambda: 1000)

    thread = threading.Thread(target=client_auth.ensure_user_tokens)
    thread.start()

    for _ in range(50):
        try:
            urllib.request.urlopen(
                f"http://127.0.0.1:{port}/auth/callback?code=code&state=state"
            )
            break
        except Exception:
            real_time.sleep(0.1)
    thread.join(5)
    assert not thread.is_alive()

    data = json.loads(path.read_text())
    assert set(data.keys()) == {"access_token", "refresh_token", "expires_at"}
    assert data["access_token"] == "a"
    assert data["refresh_token"] == "r"
    assert data["expires_at"] == 1000 + 3600 - 60
