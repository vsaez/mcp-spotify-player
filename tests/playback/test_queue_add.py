import pytest

import mcp_spotify_player.playback_controller as playback_controller_module
from mcp_spotify.errors import (
    NotAuthenticatedError,
    NoActiveDeviceError,
    PremiumRequiredError,
)
from mcp_spotify_player.playback_controller import PlaybackController
from mcp_spotify_player.spotify_client import SpotifyClient


def test_client_add_to_queue(monkeypatch: pytest.MonkeyPatch):
    client = SpotifyClient()
    calls = []

    def fake_make_request(method, endpoint, **kwargs):
        calls.append((method, endpoint, kwargs))
        return True

    client._make_request = fake_make_request

    client.playback.add_to_queue("spotify:track:123", "dev1")
    assert calls[-1][0] == "POST"
    assert calls[-1][1] == "/me/player/queue"
    assert calls[-1][2]["params"] == {
        "uri": "spotify:track:123",
        "device_id": "dev1",
    }

    client.playback.add_to_queue("spotify:track:456")
    assert calls[-1][2]["params"] == {"uri": "spotify:track:456"}


def test_queue_add_success(monkeypatch: pytest.MonkeyPatch):
    recorded: dict[str, str | None] = {}

    class DummyPlayback:
        def add_to_queue(self, uri: str, device_id: str | None = None):
            recorded["uri"] = uri
            recorded["device_id"] = device_id

    class DummyPlaylists:
        pass  # No necesitamos implementar nada aquí

    class DummyClient:
        playback = DummyPlayback()
        playlists = DummyPlaylists()  # Añadimos el atributo playlists

    monkeypatch.setattr(
        playback_controller_module, "SpotifyClient", lambda: DummyClient()
    )

    controller = PlaybackController(DummyClient())
    result = controller.queue_add("spotify:track:123", "dev1")
    assert recorded == {"uri": "spotify:track:123", "device_id": "dev1"}


@pytest.mark.parametrize(
    "exc",
    [NotAuthenticatedError, NoActiveDeviceError, PremiumRequiredError],
)
def test_queue_add_errors(monkeypatch: pytest.MonkeyPatch, exc):
    class DummyPlayback:
        def add_to_queue(self, uri: str, device_id: str | None = None):
            raise exc("boom")

    class DummyPlaylists:
        pass

    class DummyClient:
        playback = DummyPlayback()
        playlists = DummyPlaylists()

    monkeypatch.setattr(
        playback_controller_module, "SpotifyClient", lambda: DummyClient()
    )

    controller = PlaybackController(DummyClient())
    result = controller.queue_add("spotify:track:123")

    # Verificar que el resultado indica error
    assert result["success"] == False
    assert "boom" in result["message"]
