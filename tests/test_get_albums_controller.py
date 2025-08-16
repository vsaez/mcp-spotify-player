from mcp_spotify_player.album_controller import AlbumController


def test_get_albums_controller():
    class DummyAlbums:
        def get_albums(self, album_ids):
            return {
                "albums": [
                    {
                        "id": album_id,
                        "name": f"Album {album_id}",
                        "artists": [{"name": f"Artist {album_id}"}],
                        "release_date": "2024-01-01",
                        "total_tracks": 10,
                        "uri": f"spotify:album:{album_id}",
                    }
                    for album_id in album_ids
                ]
            }

    dummy_client = type("Dummy", (), {"albums": DummyAlbums()})()
    controller = AlbumController(dummy_client)

    result = controller.get_albums(["1234567890abc", "abcdef123456"])
    assert result["success"] is True
    albums = result["albums"]
    assert len(albums) == 2
    assert albums[0]["name"].startswith("Album")
    assert albums[1]["artists"][0].startswith("Artist")
