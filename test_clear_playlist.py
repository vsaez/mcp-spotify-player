import pytest
from unittest.mock import patch

from src.spotify_client import SpotifyClient
from src.spotify_controller import SpotifyController


def test_spotify_client_clear_playlist():
    client = SpotifyClient()
    with patch.object(client, '_make_request', return_value={}) as mock_request:
        assert client.clear_playlist('playlist123') is True
        mock_request.assert_called_once_with('PUT', '/playlists/playlist123/tracks', json={'uris': []})


def test_spotify_controller_clear_playlist():
    controller = SpotifyController()
    with patch.object(controller.client, 'clear_playlist', return_value=True) as mock_clear:
        result = controller.clear_playlist('playlist123')
        assert result['success'] is True
        assert 'cleared' in result['message'].lower()
        mock_clear.assert_called_once_with('playlist123')


def test_spotify_controller_clear_playlist_invalid():
    controller = SpotifyController()
    result = controller.clear_playlist('bad id!')
    assert result['success'] is False
