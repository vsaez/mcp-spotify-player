import json
import time

import pytest
import requests

from mcp_spotify.auth.tokens import Tokens, REQUIRED_SCOPES, check_scopes
from mcp_spotify.errors import (
    MissingScopesError,
    NoActiveDeviceError,
    PremiumRequiredError,
)
from mcp_spotify_player.spotify_client import SpotifyClient


class DummyResponse:
    def __init__(self, status_code: int, data: dict | None = None):
        self.status_code = status_code
        self._data = data or {}
        self.text = json.dumps(self._data) if self._data else ""

    def json(self):
        return self._data


def _fresh_tokens(scopes: set[str] | None = None) -> Tokens:
    return Tokens(
        "a",
        "r",
        int(time.time()) + 3600,
        scopes=scopes or set(),
    )


def test_check_scopes_missing():
    tokens = _fresh_tokens({"a"})
    with pytest.raises(MissingScopesError) as exc:
        check_scopes(tokens, {"a", "b"})
    assert exc.value.scopes == {"b"}


def test_premium_required_mapping(monkeypatch: pytest.MonkeyPatch):
    tokens = _fresh_tokens(REQUIRED_SCOPES["playback"])
    response = DummyResponse(
        403,
        {"error": {"status": 403, "reason": "PREMIUM_REQUIRED"}},
    )
    monkeypatch.setattr(requests, "request", lambda *args, **kwargs: response)
    client = SpotifyClient(lambda: tokens)
    with pytest.raises(PremiumRequiredError):
        client.playback.play()


def test_missing_scope_mapping(monkeypatch: pytest.MonkeyPatch):
    tokens = _fresh_tokens({"user-read-playback-state"})
    response = DummyResponse(
        403,
        {"error": {"status": 403, "reason": "MISSING_SCOPE"}},
    )
    monkeypatch.setattr(requests, "request", lambda *args, **kwargs: response)
    client = SpotifyClient(lambda: tokens)
    with pytest.raises(MissingScopesError) as exc:
        client.playback.play()
    assert "user-modify-playback-state" in exc.value.scopes


def test_no_active_device_mapping(monkeypatch: pytest.MonkeyPatch):
    tokens = _fresh_tokens(REQUIRED_SCOPES["playback"])
    response = DummyResponse(
        404,
        {"error": {"status": 404, "message": "No active device"}},
    )
    monkeypatch.setattr(requests, "request", lambda *args, **kwargs: response)
    client = SpotifyClient(lambda: tokens)
    with pytest.raises(NoActiveDeviceError):
        client.playback.play()
