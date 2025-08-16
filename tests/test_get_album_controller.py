from mcp_spotify_player.album_controller import AlbumController


def test_get_album_controller():
    class DummyAlbums:
        def get_album(self, album_id):
            return {
                "id": album_id,
                "name": "Test Album",
                "artists": [{"name": "Test Artist"}],
                "release_date": "2024-01-01",
                "total_tracks": 10,
                "uri": f"spotify:album:{album_id}",
            }

    dummy_client = type("Dummy", (), {"albums": DummyAlbums()})()
    controller = AlbumController(dummy_client)

    result = controller.get_album("1234567890abc")
    assert result["success"] is True
    album = result["album"]
    assert album["name"] == "Test Album"
    assert album["artists"][0] == "Test Artist"
