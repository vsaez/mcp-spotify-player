import pytest

from mcp_spotify_player.spotify_client import SpotifyClient
from mcp_spotify_player.playback_controller import queue_list
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
    assert result == sample


def test_queue_list_success(monkeypatch: pytest.MonkeyPatch):
    data = {
        "currently_playing": {"id": "t1"},
        "queue": [{"id": "t2"}, {"id": "t3"}],
    }

    class DummyPlayback:
        def get_queue(self):
            return data

    monkeypatch.setattr(
        playback_controller_module, "SpotifyPlaybackClient", lambda: DummyPlayback()
    )

    result = queue_list()
    assert result == {
        "now_playing": data["currently_playing"],
        "queue": data["queue"],
        "count": 2,
        "note": "Queue may be truncated by Spotify API.",
    }

    limited = queue_list(limit=1)
    assert limited["queue"] == data["queue"][:1]
    assert limited["count"] == 1


def test_queue_list_no_device(monkeypatch: pytest.MonkeyPatch):
    class DummyPlayback:
        def get_queue(self):
            raise NoActiveDeviceError("boom")

    monkeypatch.setattr(
        playback_controller_module, "SpotifyPlaybackClient", lambda: DummyPlayback()
    )

    with pytest.raises(NoActiveDeviceError):
        queue_list()
