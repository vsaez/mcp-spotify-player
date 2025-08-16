from mcp_spotify_player.album_controller import AlbumController


def test_get_album_tracks_controller():
    class DummyAlbums:
        def get_album_tracks(self, album_id, limit):
            return {
                "items": [
                    {
                        "name": "Song 1",
                        "artists": [{"name": "Artist 1"}],
                        "uri": f"spotify:track:{album_id}1",
                        "duration_ms": 180000,
                        "external_urls": {"spotify": "http://example.com"},
                    }
                ],
                "total": 1,
            }

    dummy_client = type("Dummy", (), {"albums": DummyAlbums()})()
    controller = AlbumController(dummy_client)

    result = controller.get_album_tracks("1234567890abc")
    assert result["success"] is True
    tracks = result["tracks"]
    assert tracks[0]["name"] == "Song 1"
    assert tracks[0]["artist"] == "Artist 1"
