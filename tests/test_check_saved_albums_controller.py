from mcp_spotify_player.album_controller import AlbumController


def test_check_saved_albums_controller():
    class DummyAlbums:
        def check_saved_albums(self, album_ids):
            return [True, False]

    dummy_client = type("Dummy", (), {"albums": DummyAlbums()})()
    controller = AlbumController(dummy_client)

    result = controller.check_saved_albums(["abc123def456", "def456abc789"])
    assert result["success"] is True
    assert result["albums"] == [
        {"id": "abc123def456", "saved": True},
        {"id": "def456abc789", "saved": False},
    ]
