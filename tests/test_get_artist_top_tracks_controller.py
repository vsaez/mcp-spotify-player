from mcp_spotify_player.artists_controller import ArtistsController


def test_get_artist_top_tracks_controller():
    class DummyArtists:
        def get_artist_top_tracks(self, artist_id, market='US'):
            return {
                "tracks": [
                    {
                        "name": "Track 1",
                        "artists": [{"name": "Artist 1"}],
                        "album": {"name": "Album 1"},
                        "uri": "spotify:track:track1",
                        "duration_ms": 180000,
                        "external_urls": {"spotify": "https://open.spotify.com/track/track1"},
                    }
                ]
            }

    dummy_client = type("Dummy", (), {"artists": DummyArtists()})()
    controller = ArtistsController(dummy_client)

    result = controller.get_artist_top_tracks("1234567890abc")
    assert result["success"] is True
    tracks = result["tracks"]
    assert tracks[0]["name"] == "Track 1"
    assert tracks[0]["artist"] == "Artist 1"
