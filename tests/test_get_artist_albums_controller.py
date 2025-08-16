from mcp_spotify_player.artists_controller import ArtistsController


def test_get_artist_albums_controller():
    class DummyArtists:
        def get_artist_albums(self, artist_id, include_groups=None, limit=20):
            return {
                "items": [
                    {
                        "id": "album1",
                        "name": "Album 1",
                        "artists": [{"name": "Artist 1"}],
                        "release_date": "2020-01-01",
                        "total_tracks": 10,
                        "uri": "spotify:album:album1",
                    }
                ],
                "total": 1,
            }

    dummy_client = type("Dummy", (), {"artists": DummyArtists()})()
    controller = ArtistsController(dummy_client)

    result = controller.get_artist_albums("1234567890abc")
    assert result["success"] is True
    albums = result["albums"]
    assert albums[0]["name"] == "Album 1"
    assert albums[0]["artists"][0] == "Artist 1"
