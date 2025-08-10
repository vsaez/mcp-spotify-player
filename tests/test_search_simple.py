#!/usr/bin/env python3
"""Tests for Spotify search helpers."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.spotify_client import SpotifyClient


def test_search_methods():
    client = SpotifyClient()
    calls = []

    def fake_make_request(method, endpoint, params=None, json=None):
        calls.append({'method': method, 'endpoint': endpoint, 'params': params})
        return {'ok': True}

    client._make_request = fake_make_request

    # search_tracks wrapper
    result = client.search_tracks('jazz', limit=5)
    assert result == {'ok': True}
    assert calls[-1]['params'] == {'q': 'jazz', 'type': 'track', 'limit': 5}

    # search_artists wrapper
    result = client.search_artists('miles', limit=3)
    assert result == {'ok': True}
    assert calls[-1]['params'] == {'q': 'miles', 'type': 'artist', 'limit': 3}

    # generic search for albums
    result = client.search('blue', type_='album', limit=2)
    assert result == {'ok': True}
    assert calls[-1]['params'] == {'q': 'blue', 'type': 'album', 'limit': 2}

