from mcp_spotify_player.artists_controller import ArtistsController


def test_get_artist_related_artists_controller():
    class DummyArtists:
        def get_artist_related_artists(self, artist_id):
            return {
                "artists": [
                    {
                        "id": "artist1",
                        "name": "Related Artist 1",
                        "genres": ["rock"],
                        "followers": {"total": 500},
                        "popularity": 60,
                        "uri": "spotify:artist:artist1",
                    }
                ]
            }

    dummy_client = type("Dummy", (), {"artists": DummyArtists()})()
    controller = ArtistsController(dummy_client)

    result = controller.get_artist_related_artists("1234567890abc")
    assert result["success"] is True
    artists = result["artists"]
    assert artists[0]["name"] == "Related Artist 1"
    assert result["total_artists"] == 1
