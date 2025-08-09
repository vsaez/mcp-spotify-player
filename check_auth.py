#!/usr/bin/env python3
"""
Script to check the authentication status with Spotify
"""

import sys
import os

# Add current directory to path when importing modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.spotify_controller import SpotifyController

def main():
    """Checks the authentication status with Spotify"""
    print("Checking authentication with Spotify...")
    print("=" * 50)
    
    try:
        controller = SpotifyController()
        
        if controller.is_authenticated():
            print("✅ Successfully authenticated with Spotify")
            print("🎵 You can use music commands")
            
            # Test to get current information
            try:
                current = controller.get_current_playing()
                print(f"📻 Currently playing: {current}")
            except Exception as e:
                print(f"⚠️  Could not get current information: {e}")
                
        else:
            print("❌ Not authenticated with Spotify")
            print("🔐 To authenticate:")
            print("1. Run: python main.py")
            print("2. Visit: http://127.0.0.1:8000/auth")
            print("3. Complete the authentication flow")
            print("4. Run this script again")
            
    except Exception as e:
        print(f"❌ Error checking authentication: {e}")

if __name__ == "__main__":
    main() 