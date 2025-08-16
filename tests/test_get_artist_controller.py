from mcp_spotify_player.artists_controller import ArtistsController


def test_get_artist_controller():
    class DummyArtists:
        def get_artist(self, artist_id):
            return {
                "id": artist_id,
                "name": "Test Artist",
                "genres": ["rock"],
                "followers": {"total": 1000},
                "popularity": 50,
                "uri": f"spotify:artist:{artist_id}",
            }

    dummy_client = type("Dummy", (), {"artists": DummyArtists()})()
    controller = ArtistsController(dummy_client)

    result = controller.get_artist("1234567890abc")
    assert result["success"] is True
    artist = result["artist"]
    assert artist["name"] == "Test Artist"
    assert artist["genres"][0] == "rock"
