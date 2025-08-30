import importlib
import socket
import threading
import pytest


def test_server_ready_before_open(monkeypatch, tmp_path):
    path = tmp_path / "tokens.json"
    path.unlink(missing_ok=True)
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

    monkeypatch.setattr(client_auth.secrets, "token_urlsafe", lambda n=16: "state")
    monkeypatch.setattr(
        client_auth,
        "exchange_code_for_tokens",
        lambda code: {"access_token": "a", "refresh_token": "r", "expires_in": 3600},
    )
    monkeypatch.setattr(client_auth.time, "time", lambda: 1000)

    waited = {"value": False}

    def fake_wait(host: str, port_: int, timeout: float = 5.0) -> None:
        waited["value"] = True

    opened = {"value": False}

    class DummyHTTPServer:
        def __init__(self, *args, **kwargs):
            pass

        def serve_forever(self) -> None:  # pragma: no cover - no-op
            return

        def shutdown(self) -> None:  # pragma: no cover - no-op
            return

    def fake_open(url: str) -> bool:
        assert waited["value"]
        opened["value"] = True
        raise RuntimeError("stop")

    monkeypatch.setattr(client_auth, "HTTPServer", DummyHTTPServer)
    monkeypatch.setattr(client_auth, "_wait_for_server", fake_wait)
    monkeypatch.setattr(client_auth.webbrowser, "open", fake_open)

    with pytest.raises(RuntimeError):
        client_auth.ensure_user_tokens()

    assert opened["value"]

