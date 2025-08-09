#!/usr/bin/env python3
"""
Script to test the play_music functionality
"""

import sys
import os

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.spotify_controller import SpotifyController


def main():
    """Test the play_music functionality"""
    print("Testing play_music with 'El Último de la Fila'...")
    print("=" * 50)

    try:
        controller = SpotifyController()

        if not controller.is_authenticated():
            print("❌ Not authenticated with Spotify")
            return

        print("✅ Successfully authenticated")

        # Test play_music
        result = controller.play_music(query="El Último de la Fila")
        print(f"🎵 Result: {result}")

        # Check what is currently playing
        current = controller.get_current_playing()
        print(f"📻 Currently playing: {current}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
