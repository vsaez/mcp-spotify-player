import argparse
import sys

from mcp_logging import get_logger
from .mcp_stdio_server import MCPServer

logger = get_logger(__name__)


def main(argv: list[str] | None = None) -> None:
    """Start the MCP Spotify Player stdio server."""
    parser = argparse.ArgumentParser(description="MCP Spotify Player stdio server")
    parser.add_argument("--version", action="version", version="0.1.0")
    parser.parse_args(argv)

    logger.info("MCP Spotify Player - stdio server")
    logger.info("=" * 50)
    logger.info("Initializying MCP server...")
    logger.info("This server connect to Cursor through STDIO")
    logger.info("Do not open browser, this server is not using HTTP")
    logger.info("=" * 50)

    try:
        server = MCPServer()
        server.run()
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:  # pragma: no cover - defensive
        logger.error("Error initializing server: %s", e)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
