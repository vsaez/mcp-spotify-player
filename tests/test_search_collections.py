import os
import sys
from unittest.mock import patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp_spotify_player.playback_controller import PlaybackController
from mcp_spotify_player.mcp_stdio_server import MCPServer


def test_search_collections_playlist():
    class DummyPlayback:
        def search_collections(self, q, type, limit, offset, market):
            assert market is None
            return {
                "playlists": {
                    "limit": limit,
                    "offset": offset,
                    "total": 1,
                    "items": [
                        {
                            "id": "p1",
                            "name": "Mix",
                            "uri": "spotify:playlist:p1",
                            "images": [{"url": "http://img"}],
                        }
                    ],
                }
            }

    dummy_client = type("Dummy", (), {"playback": DummyPlayback(), "playlists": None})()
    controller = PlaybackController(dummy_client)
    result = controller.search_collections(q="mix", type="playlist", limit=1)
    assert result == {
        "type": "playlist",
        "limit": 1,
        "offset": 0,
        "total": 1,
        "items": [
            {"id": "p1", "name": "Mix", "uri": "spotify:playlist:p1", "image": "http://img"}
        ],
    }
    assert "artists" not in result["items"][0]


def test_search_collections_album_with_market():
    class DummyPlayback:
        def search_collections(self, q, type, limit, offset, market):
            assert market == "US"
            assert offset == 2
            return {
                "albums": {
                    "limit": limit,
                    "offset": offset,
                    "total": 1,
                    "items": [
                        {
                            "id": "a1",
                            "name": "Album",
                            "uri": "spotify:album:a1",
                            "images": [{"url": "http://img"}],
                            "artists": [{"name": "Artist"}],
                        }
                    ],
                }
            }

    dummy_client = type("Dummy", (), {"playback": DummyPlayback(), "playlists": None})()
    controller = PlaybackController(dummy_client)
    result = controller.search_collections(q="alb", type="album", limit=1, offset=2, market="US")
    assert result["type"] == "album"
    assert result["offset"] == 2
    assert result["items"][0]["artists"] == ["Artist"]


# Validation tests

def _server():
    with patch("mcp_spotify_player.mcp_stdio_server.try_load_tokens", return_value=None):
        return MCPServer()


def test_validate_search_collections_invalid_type():
    server = _server()
    with pytest.raises(ValueError):
        server._validate_search_collections({"q": "a", "type": "track"})


def test_validate_search_collections_invalid_limit():
    server = _server()
    with pytest.raises(ValueError):
        server._validate_search_collections({"q": "a", "type": "album", "limit": 0})


# Error handling tests

def test_search_collections_http_401():
    class DummyPlayback:
        def search_collections(self, q, type, limit, offset, market):
            return {"error": {"status": 401, "message": "Unauthorized"}}

    dummy_client = type("Dummy", (), {"playback": DummyPlayback(), "playlists": None})()
    controller = PlaybackController(dummy_client)
    result = controller.search_collections(q="x", type="playlist")
    assert "Unauthorized" in result["error"]


def test_search_collections_http_429():
    class DummyPlayback:
        def search_collections(self, q, type, limit, offset, market):
            return {"error": {"status": 429, "message": "Too Many Requests"}}

    dummy_client = type("Dummy", (), {"playback": DummyPlayback(), "playlists": None})()
    controller = PlaybackController(dummy_client)
    result = controller.search_collections(q="x", type="playlist")
    assert "429" in result["error"]
