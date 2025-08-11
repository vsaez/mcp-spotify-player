import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp_spotify_player.playback_controller import PlaybackController


def test_search_music_tracks():
    class DummyPlayback:
        def search_tracks(self, query, limit):
            assert query == "song"
            assert limit == 1
            return {
                "tracks": {
                    "items": [
                        {
                            "name": "Song 1",
                            "artists": [{"name": "Artist 1"}],
                            "album": {"name": "Album 1"},
                            "uri": "spotify:track:1",
                            "duration_ms": 123,
                            "external_urls": {"spotify": "https://open.spotify.com/track/1"},
                        }
                    ],
                    "total": 1,
                }
            }

    dummy_client = type("Dummy", (), {"playback": DummyPlayback(), "playlists": None})()
    controller = PlaybackController(dummy_client)

    result = controller.search_music("song", search_type="track", limit=1)
    assert result["success"] is True
    assert result["total_results"] == 1
    assert result["tracks"][0]["name"] == "Song 1"
    assert result["tracks"][0]["artist"] == "Artist 1"


def test_search_music_artists():
    class DummyPlayback:
        def search_artists(self, query, limit):
            assert query == "beatles"
            assert limit == 2
            return {
                "artists": {
                    "items": [
                        {
                            "name": "Artist A",
                            "uri": "spotify:artist:a",
                            "external_urls": {"spotify": "https://open.spotify.com/artist/a"},
                        },
                        {
                            "name": "Artist B",
                            "uri": "spotify:artist:b",
                            "external_urls": {"spotify": "https://open.spotify.com/artist/b"},
                        },
                    ],
                    "total": 2,
                }
            }

    dummy_client = type("Dummy", (), {"playback": DummyPlayback(), "playlists": None})()
    controller = PlaybackController(dummy_client)

    result = controller.search_music("beatles", search_type="artist", limit=2)
    assert result["success"] is True
    assert result["total_results"] == 2
    assert "tracks" not in result
    assert result["artists"][0]["name"] == "Artist A"
    assert result["artists"][1]["external_url"].endswith("/b")
