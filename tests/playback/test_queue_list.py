import pytest

from mcp_spotify_player.spotify_client import SpotifyClient
from mcp_spotify_player.playback_controller import PlaybackController
import mcp_spotify_player.playback_controller as playback_controller_module
from mcp_spotify.errors import NoActiveDeviceError


def test_client_get_queue(monkeypatch: pytest.MonkeyPatch):
    client = SpotifyClient()
    calls = []
    sample = {
        "currently_playing": {"id": "t1"},
        "queue": [{"id": "t2"}, {"id": "t3"}],
    }

    def fake_make_request(method, endpoint, **kwargs):
        calls.append((method, endpoint, kwargs))
        return sample

    client._make_request = fake_make_request
    result = client.playback.get_queue()
    assert calls[-1][0] == "GET"
    assert calls[-1][1] == "/me/player/queue"

    # El resultado incluye success: True además de los datos originales
    expected = {
        "success": True,
        "currently_playing": {"id": "t1"},
        "queue": [{"id": "t2"}, {"id": "t3"}],
    }
    assert result == expected



def test_queue_list_no_device(monkeypatch: pytest.MonkeyPatch):
    class DummyPlayback:
        def get_queue(self, limit=None):  # Añadir parámetro limit
            raise NoActiveDeviceError("boom")

    class DummyPlaylists:
        pass

    class DummyClient:
        playback = DummyPlayback()
        playlists = DummyPlaylists()

    monkeypatch.setattr(
        playback_controller_module, "SpotifyClient", lambda: DummyClient()
    )

    controller = PlaybackController(DummyClient())
    with pytest.raises(NoActiveDeviceError):
        controller.queue_list()


def test_queue_list_success(monkeypatch: pytest.MonkeyPatch):
    data = {
        "currently_playing": {"id": "t1"},
        "queue": [{"id": "t2"}, {"id": "t3"}],
    }

    class DummyPlayback:
        def get_queue(self, limit=None):
            return data

    class DummyPlaylists:
        pass

    class DummyClient:
        playback = DummyPlayback()
        playlists = DummyPlaylists()

    monkeypatch.setattr(
        playback_controller_module, "SpotifyClient", lambda: DummyClient()
    )

    controller = PlaybackController(DummyClient())
    result = controller.queue_list()

    # El controlador devuelve directamente los datos del cliente
    assert result == data

    limited = controller.queue_list(limit=1)
    assert limited == data
