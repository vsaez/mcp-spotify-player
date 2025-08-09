#!/usr/bin/env python3
"""
Simple script to test Spotify search
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.spotify_client import SpotifyClient


def test_search():
    print("=== SPOTIFY SEARCH TEST ===\n")

    client = SpotifyClient()

    # Test search
    query = "jazz"
    print(f"Searching: '{query}'")

    result = client.search_tracks(query, limit=5)

    if result:
        print("✓ Search successful")
        if 'tracks' in result and 'items' in result['tracks']:
            tracks = result['tracks']['items']
            print(f"✓ Found {len(tracks)} songs")
            for i, track in enumerate(tracks[:3]):
                print(f"  {i + 1}. {track['name']} - {track['artists'][0]['name']}")
        else:
            print(f"✗ Unexpected result: {result}")
    else:
        print("✗ Search failed")


if __name__ == "__main__":
    test_search()