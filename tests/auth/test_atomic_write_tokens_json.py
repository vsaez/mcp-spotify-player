import importlib
import pytest


def test_atomic_write_tokens_json(monkeypatch, tmp_path):
    path = tmp_path / "tokens.json"
    original = path.read_text()
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(path))
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "cid")

    import mcp_spotify_player.config as config
    importlib.reload(config)
    import mcp_spotify_player.client_auth as client_auth
    importlib.reload(client_auth)

    tokens = {"access_token": "a", "refresh_token": "r", "expires_in": 60}

    def fail_replace(src, dst):
        raise RuntimeError("fail")

    monkeypatch.setattr(client_auth.os, "replace", fail_replace)
    monkeypatch.setattr(client_auth.time, "time", lambda: 0)

    with pytest.raises(RuntimeError):
        client_auth.save_tokens_minimal(tokens)

    assert path.read_text() == original
