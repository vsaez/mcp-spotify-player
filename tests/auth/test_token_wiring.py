import json
from pathlib import Path

import pytest
import requests

from mcp_spotify.auth.tokens import Tokens
from mcp_spotify.errors import (
    InvalidTokenFileError,
    RefreshNotPossibleError,
)
from mcp_spotify_player.client_auth import try_load_tokens
from mcp_spotify_player.config import Config
from mcp_spotify_player.spotify_client import SpotifyClient


def test_no_tokens_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "tokens.json"
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(path))
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "secret")
    monkeypatch.setattr(Config, "SPOTIFY_CLIENT_ID", "id")
    monkeypatch.setattr(Config, "SPOTIFY_CLIENT_SECRET", "secret")

    class DummyResponse:
        def __init__(self, data):
            self.status_code = 200
            self._data = data
            self.text = json.dumps(data)

        def json(self):
            return self._data

    def fake_post(url, data):
        assert data["grant_type"] == "client_credentials"
        return DummyResponse({"access_token": "abc", "expires_in": 60})

    monkeypatch.setattr(requests, "post", fake_post)

    tokens = try_load_tokens()
    assert tokens is not None
    assert path.exists()
    stored = json.loads(path.read_text())
    assert stored["access_token"] == "abc"


def test_invalid_token_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "tokens.json"
    path.write_text("{")
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(path))
    with pytest.raises(InvalidTokenFileError):
        try_load_tokens()

    def provider() -> Tokens | None:
        raise InvalidTokenFileError(
            "Token file is invalid. Fix tokens.json or run /auth to regenerate it."
        )

    client = SpotifyClient(provider)
    with pytest.raises(InvalidTokenFileError):
        client.playback.get_playback_state()


def test_missing_refresh_token(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "tokens.json"
    data = {"access_token": "a", "refresh_token": "", "expires_at": 0}
    path.write_text(json.dumps(data))
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(path))
    tokens = try_load_tokens()
    assert tokens is not None
    client = SpotifyClient(lambda: tokens)
    with pytest.raises(RefreshNotPossibleError):
        client.playback.get_playback_state()
