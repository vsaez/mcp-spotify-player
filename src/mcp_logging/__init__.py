"""Centralized logging configuration for mcp-spotify-player.

This module exposes a :func:`get_logger` helper that other modules should
use instead of configuring logging individually. Logging output can be
customised via environment variables:

- ``MCP_LOG_LEVEL`` sets the minimum log level (default: ``INFO``).
- ``MCP_LOG_FILE``  if set, log output will also be written to this file
  in addition to stderr.
"""

from __future__ import annotations

import logging
import os

_LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
_LOG_FORMAT = (
    "%(asctime)s [%(levelname)s] %(filename)s:%(funcName)s - %(message)s"
)
_LOG_FILE = os.getenv("MCP_LOG_FILE")

_handlers: list[logging.Handler] = [logging.StreamHandler()]
if _LOG_FILE:
    _handlers.append(logging.FileHandler(_LOG_FILE, encoding="utf-8"))

logging.basicConfig(level=_LOG_LEVEL, format=_LOG_FORMAT, handlers=_handlers)


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a module-specific logger.

    ``name`` defaults to ``"mcp"`` when ``None`` is provided.
    """
    return logging.getLogger(name or "mcp")
