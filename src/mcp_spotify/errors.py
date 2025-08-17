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


class UserAuthRequiredError(McpUserError):
    """Raised when a user OAuth token with refresh capability is required."""


class MissingScopesError(McpUserError):
    """Raised when the OAuth token lacks required scopes."""

    def __init__(self, scopes: set[str]):
        message = ", ".join(sorted(scopes))
        super().__init__(f"Missing required scopes: {message}")
        self.scopes = scopes


class PremiumRequiredError(McpUserError):
    """Raised when an operation requires Spotify Premium."""


class NoActiveDeviceError(McpUserError):
    """Raised when there is no active playback device."""

