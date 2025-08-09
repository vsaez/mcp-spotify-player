import sys
import os

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.spotify_controller import SpotifyController


def test_add_tracks_invalid_playlist_id():
    controller = SpotifyController()
    result = controller.add_tracks_to_playlist("123", ["spotify:track:abcdef"])
    assert result["success"] is False
    assert "Invalid playlist ID" in result["message"]


def test_add_tracks_invalid_track_uris():
    controller = SpotifyController()
    valid_playlist_id = "1234567890ABCDEF123456"
    result = controller.add_tracks_to_playlist(valid_playlist_id, ["invalid_uri"])
    assert result["success"] is False
    assert "Invalid track URIs" in result["message"]
