import json
import os
from pathlib import Path

import pytest

from mcp_spotify.auth.tokens import Tokens
from mcp_spotify.errors import InvalidTokenFileError, UserAuthRequiredError
from mcp_spotify_player.client_auth import SpotifyAuthClient, try_load_tokens
from mcp_spotify_player.mcp_stdio_server import MCPServer
from mcp_spotify_player.spotify_client import SpotifyClient


def test_no_tokens_file_returns_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "alt" / "tokens.json"
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(path))

    tokens = try_load_tokens()
    assert tokens is None
    assert not path.exists()


def test_no_tokens_file_fails_without_creating_client_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "alt" / "tokens.json"
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(path))
    with pytest.raises(UserAuthRequiredError):
        MCPServer()
    assert not path.exists()


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


def test_atomic_write_tokens_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "tokens.json"
    path.write_text(
        json.dumps({"access_token": "a", "refresh_token": "r", "expires_at": 1})
    )
    client = SpotifyAuthClient()
    client.tokens_file = str(path)
    client.access_token = "b"
    client.refresh_token = "r2"
    client.token_expires_at = 2

    def fail_replace(src, dst):
        raise OSError("boom")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError):
        client._save_tokens()
    data = json.loads(path.read_text())
    assert data["access_token"] == "a"
