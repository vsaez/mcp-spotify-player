from typing import Callable, Optional

import requests

from mcp_spotify.auth.tokens import (
    REQUIRED_SCOPES,
    Tokens,
    check_scopes,
    has_refresh_token,
    needs_refresh,
    refresh_tokens,
)
from mcp_spotify.errors import (
    NoActiveDeviceError,
    NotAuthenticatedError,
    PremiumRequiredError,
    RefreshNotPossibleError,
)
from mcp_spotify_player.client_playback import SpotifyPlaybackClient
from mcp_spotify_player.client_playlists import SpotifyPlaylistsClient
from mcp_spotify_player.client_albums import SpotifyAlbumsClient
from mcp_spotify_player.client_artists import SpotifyArtistsClient
from mcp_spotify_player.config import Config


TokensProvider = Callable[[], Optional[Tokens]]


class SpotifyClient:
    """Unified interface to the Spotify Web API."""

    def __init__(
        self,
        tokens_provider: TokensProvider | None = None,
        *,
        verify_scopes: bool = False,
        verify_at_startup: bool = False,
    ):
        self.tokens_provider: TokensProvider = tokens_provider or (lambda: None)
        self.config = Config()
        self.playback = SpotifyPlaybackClient(self)
        self.playlists = SpotifyPlaylistsClient(self)
        self.albums = SpotifyAlbumsClient(self)
        self.artists = SpotifyArtistsClient(self)
        self.verify_scopes = verify_scopes
        if verify_at_startup:
            tokens = self.tokens_provider()
            if tokens:
                all_scopes = set().union(*REQUIRED_SCOPES.values())
                check_scopes(tokens, all_scopes)

    def _refresh(self, tokens: Tokens) -> Tokens:
        return refresh_tokens(
            tokens, self.config.SPOTIFY_CLIENT_ID, self.config.SPOTIFY_CLIENT_SECRET
        )

    def _make_request(
        self, method: str, endpoint: str, *, feature: str | None = None, **kwargs
    ):
        tokens = self.tokens_provider()
        if tokens is None:
            raise NotAuthenticatedError("Not authenticated with Spotify. Run /auth.")
        if has_refresh_token(tokens) and needs_refresh(tokens):
            tokens = self._refresh(tokens)

        if feature and self.verify_scopes:
            check_scopes(tokens, REQUIRED_SCOPES[feature])

        headers = {
            "Authorization": f"Bearer {tokens.access_token}",
            "Content-Type": "application/json",
        }
        url = f"{self.config.SPOTIFY_API_BASE}{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)

        if response.status_code == 401:
            if has_refresh_token(tokens):
                tokens = self._refresh(tokens)
                headers["Authorization"] = f"Bearer {tokens.access_token}"
                response = requests.request(method, url, headers=headers, **kwargs)
            else:
                raise RefreshNotPossibleError(
                    "Cannot refresh access token: missing refresh_token in stored credentials."
                )

        if response.status_code in [200, 201, 204]:
            if method == "PUT" and endpoint == "/me/player/repeat":
                return True
            try:
                return response.json() if response.text else True
            except ValueError:
                return True

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code == 403:
            reason = ""
            err = data.get("error", {}) if isinstance(data, dict) else {}
            if isinstance(err, dict):
                reason = err.get("reason") or err.get("message", "")
            if reason == "PREMIUM_REQUIRED":
                raise PremiumRequiredError("Spotify Premium required.")
            if "scope" in reason.lower() and feature:
                check_scopes(tokens, REQUIRED_SCOPES[feature])
            return data

        if (
            response.status_code == 404
            and endpoint.startswith("/me/player")
        ):
            message = ""
            err = data.get("error", {}) if isinstance(data, dict) else {}
            if isinstance(err, dict):
                message = err.get("message", "")
            if message in ("Device not found", "No active device"):
                raise NoActiveDeviceError(
                    "No active device. Open Spotify on any device."
                )
            return data

        return data

    def __getattr__(self, name):
        for client in (self.playback, self.playlists, self.albums, self.artists):
            if hasattr(client, name):
                return getattr(client, name)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")
