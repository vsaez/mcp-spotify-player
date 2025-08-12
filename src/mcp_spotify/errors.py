from __future__ import annotations


class McpUserError(Exception):
    """Base error surfaced directly to MCP clients."""


class InvalidTokenFileError(McpUserError):
    """Raised when the token file is missing or malformed."""


class NotAuthenticatedError(McpUserError):
    """Raised when no Spotify authentication is available."""


class TokenExpiredError(McpUserError):
    """Raised when the Spotify access token has expired."""


class RefreshNotPossibleError(McpUserError):
    """Raised when refreshing the Spotify access token is not possible."""

