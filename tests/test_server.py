#!/usr/bin/env python3
"""
Test script for the MCP Spotify Player server
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"


def test_endpoints():
    """Test the server's basic endpoints"""
    print("🧪 Testing server endpoints...")

    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Server: {response.json()}")
        else:
            print(f"❌ Error on root endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

    try:
        response = requests.get(f"{BASE_URL}/.well-known/mcp")
        if response.status_code == 200:
            manifest = response.json()
            print("✅ MCP manifest available")
            print(f"   Available tools: {len(manifest.get('tools', []))}")
        else:
            print(f"❌ Error on MCP manifest: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting manifest: {e}")

    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ Status endpoint working")
            print(f"   Authenticated with Spotify: {status.get('spotify_authenticated', False)}")
        else:
            print(f"❌ Error on status endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting status: {e}")

    return True


def test_mcp_commands():
    """Test MCP commands"""
    print("\n🎵 Testing MCP commands...")

    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "search_music",
            "params": {
                "query": "REM",
                "search_type": "track",
                "limit": 3
            }
        }

        response = requests.post(f"{BASE_URL}/mcp", json=mcp_request)
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print("✅ search_music command working")
                tracks = result["result"].get("tracks", [])
                print(f"   Found {len(tracks)} songs")
                for track in tracks[:2]:
                    print(f"   - {track['name']} - {track['artist']}")
            else:
                print("❌ Error in search_music response")
        else:
            print(f"❌ Error in search_music command: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing search_music: {e}")

    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "get_current_playing",
            "params": {}
        }

        response = requests.post(f"{BASE_URL}/mcp", json=mcp_request)
        if response.status_code == 401:
            print("✅ Authentication requirement correctly detected")
            print("   💡 Visit /auth to authenticate with Spotify")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing get_current_playing: {e}")


def test_auth_flow():
    """Test the authentication flow"""
    print("\n🔐 Testing authentication flow...")

    try:
        response = requests.get(f"{BASE_URL}/auth")
        if response.status_code == 200:
            auth_data = response.json()
            print("✅ Auth endpoint working")
            print(f"   Auth URL: {auth_data.get('auth_url', 'Not available')}")
            print("   💡 Copy the URL and paste it in your browser to authenticate")
        else:
            print(f"❌ Error on auth endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing auth: {e}")


def main():
    """Main test function"""
    print("🎵 MCP Spotify Player - Server Tests")
    print("=" * 50)

    print("🔍 Checking if server is running...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server responded with code: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("   💡 Make sure the server is running with: python main.py")
        return
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return

    test_endpoints()
    test_mcp_commands()
    test_auth_flow()

    print("\n" + "=" * 50)
    print("📋 Test summary completed")
    print("💡 To fully use the server:")
    print("   1. Visit http://localhost:8000/auth")
    print("   2. Authenticate with Spotify")
    print("   3. Enjoy controlling your music!")


if __name__ == "__main__":
    main()
