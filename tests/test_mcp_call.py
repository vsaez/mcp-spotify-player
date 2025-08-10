#!/usr/bin/env python3
"""
Script to test the MCP call exactly as Claude makes it
"""

import json
import subprocess
import sys
import time


def test_mcp_call():
    """Test the MCP call with the format used by Claude"""
    print("Testing MCP call with Claude format...")
    print("=" * 50)

    # Command to run the server
    cmd = [sys.executable, "start_mcp_server.py"]

    try:
        # Start the server as a subprocess
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        print("✅ Server started")

        # Wait for the server to initialize
        time.sleep(1)

        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        print("📨 Sending initialization...")
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()

        # Read initialization response
        response = process.stdout.readline()
        print(f"✅ Initialization: {response.strip()}")

        # Send initialized notification
        initialized_message = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }

        print("📨 Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_message) + "\n")
        process.stdin.flush()

        # Send play_music call (Claude format)
        play_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "play_music",
                "arguments": {
                    "query": "El Último de la Fila"
                }
            }
        }

        print("📨 Sending play_music...")
        process.stdin.write(json.dumps(play_message) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        if response:
            try:
                parsed_response = json.loads(response.strip())
                print("✅ Response received:")
                print(json.dumps(parsed_response, indent=2))

                # Check if there are results
                calls = parsed_response.get("result", {}).get("calls", [])
                if calls:
                    for call in calls:
                        content = call.get("content", [])
                        for item in content:
                            if item.get("type") == "text":
                                print(f"📝 Result: {item.get('text')}")
                else:
                    print("❌ No results in the response")

            except json.JSONDecodeError:
                print("❌ Error parsing JSON response")
                print(f"Raw response: {response}")
        else:
            print("❌ No response received")

        # Terminate the process
        process.terminate()
        process.wait()

        print("\n✅ Test completed")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

    return True


if __name__ == "__main__":
    success = test_mcp_call()
    sys.exit(0 if success else 1)
