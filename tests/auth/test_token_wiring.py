import json
import json
import json
from pathlib import Path

import pytest

from mcp_spotify.auth.tokens import Tokens
from mcp_spotify.errors import (
    InvalidTokenFileError,
    NotAuthenticatedError,
    RefreshNotPossibleError,
)
from mcp_spotify_player.client_auth import try_load_tokens
from mcp_spotify_player.spotify_client import SpotifyClient


def test_no_tokens_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(tmp_path / "tokens.json"))
    assert try_load_tokens() is None
    client = SpotifyClient(lambda: None)
    with pytest.raises(NotAuthenticatedError):
        client.playback.get_playback_state()


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
