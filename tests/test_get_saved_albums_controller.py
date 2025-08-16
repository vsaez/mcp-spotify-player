from mcp_spotify_player.album_controller import AlbumController


def test_get_saved_albums_controller():
    class DummyAlbums:
        def get_saved_albums(self, limit):
            return {
                "items": [
                    {
                        "album": {
                            "id": "abc123",
                            "name": "Album 1",
                            "artists": [{"name": "Artist 1"}],
                            "release_date": "2024-01-01",
                            "total_tracks": 10,
                            "uri": "spotify:album:abc123",
                        }
                    }
                ],
                "total": 1,
            }

    dummy_client = type("Dummy", (), {"albums": DummyAlbums()})()
    controller = AlbumController(dummy_client)

    result = controller.get_saved_albums()
    assert result["success"] is True
    albums = result["albums"]
    assert len(albums) == 1
    assert albums[0]["name"] == "Album 1"
