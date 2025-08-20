from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any

import pytest
import requests

from mcp_spotify.auth.tokens import Tokens
from mcp_spotify.errors import NotAuthenticatedError
from mcp_spotify_player.client_auth import SpotifyAuthClient
from mcp_spotify_player.spotify_client import SpotifyClient


class DummyResponse:
    def __init__(self, status_code: int, data: dict[str, Any] | None = None):
        self.status_code = status_code
        self._data = data or {}
        self.text = json.dumps(self._data) if self._data else ""

    def json(self) -> dict[str, Any]:
        return self._data


def test_request_200(monkeypatch: pytest.MonkeyPatch) -> None:
    tokens = Tokens("a", "r", int(time.time()) + 3600)
    calls: list[str] = []

    def fake_request(method, url, headers=None, **kwargs):
        calls.append(headers["Authorization"])
        return DummyResponse(200, {"ok": True})

    def fake_post(*args, **kwargs):  # pragma: no cover - should not be called
        raise AssertionError("refresh should not be attempted")

    monkeypatch.setattr(requests, "request", fake_request)
    monkeypatch.setattr(requests, "post", fake_post)

    client = SpotifyClient(lambda: tokens)
    assert client.playback.get_playback_state() == {"ok": True}
    assert calls == ["Bearer a"]


def test_request_401_triggers_refresh(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tokens = Tokens("old", "refresh", int(time.time()) + 3600)
    path = tmp_path / "tokens.json"
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(path))

    responses = [DummyResponse(401), DummyResponse(200, {"ok": True})]
    headers_seen: list[str] = []

    def fake_request(method, url, headers=None, **kwargs):
        headers_seen.append(headers["Authorization"])
        return responses.pop(0)

    def fake_post(url, data):
        assert data["refresh_token"] == "refresh"
        return DummyResponse(200, {"access_token": "new", "expires_in": 60})

    monkeypatch.setattr(requests, "request", fake_request)
    monkeypatch.setattr(requests, "post", fake_post)

    client = SpotifyClient(lambda: tokens)
    assert client.playback.get_playback_state() == {"ok": True}
    assert headers_seen == ["Bearer old", "Bearer new"]
    stored = json.loads(path.read_text())
    assert stored["access_token"] == "new"


def test_no_refresh_when_no_refresh_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tokens = Tokens("a", "", int(time.time()) + 3600)

    def fake_request(method, url, headers=None, **kwargs):
        return DummyResponse(401)

    def fail_post(*args, **kwargs):  # pragma: no cover
        raise AssertionError("refresh should not be attempted")

    monkeypatch.setattr(requests, "request", fake_request)
    monkeypatch.setattr(requests, "post", fail_post)

    client = SpotifyClient(lambda: tokens)
    with pytest.raises(NotAuthenticatedError) as exc:
        client.playback.get_playback_state()
    assert "User token missing" in str(exc.value)


def test_refresh_preserves_refresh_token_when_missing_in_response(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "tokens.json"
    client = SpotifyAuthClient()
    client.tokens_file = str(path)
    client.access_token = "old"
    client.refresh_token = "refresh"
    client.token_expires_at = 0

    def fake_post(url, data):
        return DummyResponse(200, {"access_token": "new", "expires_in": 120})

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(time, "time", lambda: 1000)

    assert client.refresh_access_token() is True
    assert client.refresh_token == "refresh"
    stored = json.loads(path.read_text())
    assert stored["refresh_token"] == "refresh"
    assert client.token_expires_at == 1000 + 120 - 60

