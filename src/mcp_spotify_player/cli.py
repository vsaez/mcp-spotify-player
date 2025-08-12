import argparse
import sys

from .mcp_stdio_server import MCPServer


def main(argv: list[str] | None = None) -> None:
    """Start the MCP Spotify Player stdio server."""
    parser = argparse.ArgumentParser(description="MCP Spotify Player stdio server")
    parser.add_argument("--version", action="version", version="0.1.0")
    parser.parse_args(argv)

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
    except Exception as e:  # pragma: no cover - defensive
        print(f"Error initializing server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
