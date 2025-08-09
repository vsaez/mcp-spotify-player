#!/usr/bin/env python3
"""
Script to verify authentication in the MCP server context
"""

import sys
import os
import json

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp_stdio_server import MCPServer


def main():
    """Verify authentication in the MCP server context"""
    print("Verifying authentication in the MCP server context...")
    print("=" * 60)

    try:
        # Create MCP server instance
        server = MCPServer()

        print("🔧 MCP server created")
        print(f"📁 Project directory: {server.controller.client.project_dir}")
        print(f"📄 Tokens file: {server.controller.client.tokens_file}")

        # Check if the tokens file exists
        if os.path.exists(server.controller.client.tokens_file):
            print("✅ Tokens file found")

            # Load tokens manually
            with open(server.controller.client.tokens_file, 'r') as f:
                token_data = json.load(f)
                print(f"🔑 Access token: {token_data['access_token'][:20]}...")
                print(f"🔄 Refresh token: {token_data['refresh_token'][:20]}...")
                print(f"⏰ Expires at: {token_data['expires_at']}")
        else:
            print("❌ Tokens file not found")
            return

        # Verify authentication
        print("\n🔍 Verifying authentication...")
        is_auth = server.controller.is_authenticated()
        print(f"🔐 is_authenticated(): {is_auth}")

        if is_auth:
            print("✅ Successful authentication in the MCP server")

            # Test an operation
            print("\n🎵 Testing playback...")
            result = server.controller.get_current_playing()
            print(f"📻 Result: {result}")
        else:
            print("❌ Authentication failed in the MCP server")

            # Manually verify tokens
            print("\n🔍 Manually verifying tokens...")
            token = server.controller.client._get_valid_token()
            if token:
                print(f"✅ Valid token obtained: {token[:20]}...")
            else:
                print("❌ Could not obtain a valid token")

            # Verify token loading
            print("\n📂 Verifying token loading...")
            load_success = server.controller.client._load_tokens()
            print(f"📥 _load_tokens(): {load_success}")

            if load_success:
                print(
                    f"🔑 Access token loaded: {server.controller.client.access_token[:20] if server.controller.client.access_token else 'None'}...")
                print(
                    f"🔄 Refresh token loaded: {server.controller.client.refresh_token[:20] if server.controller.client.refresh_token else 'None'}...")
                print(f"⏰ Expires at: {server.controller.client.token_expires_at}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()