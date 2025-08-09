#!/usr/bin/env python3
"""
Script to start the MCP Spotify Player server
"""

import sys
import os

# This allows the script to be run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp_stdio_server import MCPServer

def main():
    """Main function to run the MCP server"""
    print("MCP Spotify Player - stdio server", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print("Initializying MCP server...", file=sys.stderr)
    print("This server connect to Cursor through STDIO", file=sys.stderr)
    print("Do not open browser, this server is not using HTTP", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    try:
        server = MCPServer()
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Error initializing server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
