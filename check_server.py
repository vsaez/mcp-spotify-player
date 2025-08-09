#!/usr/bin/env python3
"""
Script for quick verification of the MCP Spotify Player server
"""

import requests
import socket
import sys
import time

def check_port(host, port):
    """Verifies if a port is open on a given host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def check_server_status():
    """Verifying server status"""
    print("🔍 Verifying server status...")
    
    # Verify if the server is running on port 8000
    if check_port("127.0.0.1", 8000):
        print("✅ Port 8000 is in use")
    else:
        print("❌ Port 8000 is not in use")
        print("💡 Service might not be running")
        return False
    
    # Try to connect to server
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Server responds correctly")
            data = response.json()
            print(f"   Name: {data.get('name', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"❌ Server responds with code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server")
        print("💡 Make sure the server is running")
        return False
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return False

def check_spotify_auth():
    """Verifies Spotify authentication configuration"""
    print("\n🔐 Verifying Spotify configuration...")

    try:
        response = requests.get("http://127.0.0.1:8000/auth", timeout=5)
        if response.status_code == 200:
            print("✅ Authentication endpoint available")
            data = response.json()
            auth_url = data.get('auth_url', '')
            if auth_url:
                print("✅ Authentication URL generated")
                print(f"   URL: {auth_url[:50]}...")
            else:
                print("❌ Could not generate authentication URL")
        else:
            print(f"❌ Error in auth endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verifying auth: {e}")

def check_mcp_manifest():
    """Verify MCP manifest availability"""
    print("\n📋 Verifying MCP manifest...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/.well-known/mcp", timeout=5)
        if response.status_code == 200:
            print("✅ MCP manifest available")
            manifest = response.json()
            tools = manifest.get('tools', [])
            print(f"   Available tools: {len(tools)}")
            for tool in tools:
                print(f"   - {tool.get('name', 'N/A')}")
        else:
            print(f"❌ Error in MCP manifest: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verifying MCP manifest: {e}")

def main():
    """Main function to run the verification script"""
    print("🎵 MCP Spotify Player - Server Verification Script")
    print("=" * 50)
    
    # Verify if the server is running
    if not check_server_status():
        print("\n💡 To start the server:")
        print("   1. Make sure you have the dependencies installed: pip install -r requirements.txt")
        print("   2. Configure your .env file with your Spotify credentials")
        print("   3. Run: python main.py")
        return
    
    # Verify Spotify authentication
    check_spotify_auth()
    
    # Verify MCP manifest
    check_mcp_manifest()


    print("\n" + "=" * 50)
    print("✅ Verification completed")
    print("💡 If everything is correct, you can:")
    print("   1. Visit http://127.0.0.1:8000/auth to authenticate")
    print("   2. Use http://127.0.0.1:8000/docs to view the documentation")
    print("   3. Run python test_server.py to perform full tests")

if __name__ == "__main__":
    main() 