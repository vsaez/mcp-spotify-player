from typing import Callable, Optional

import requests

from mcp_spotify.auth.tokens import Tokens
from mcp_spotify.errors import NotAuthenticatedError, TokenExpiredError
from mcp_spotify_player.client_auth import is_token_expired
from mcp_spotify_player.client_playback import SpotifyPlaybackClient
from mcp_spotify_player.client_playlists import SpotifyPlaylistsClient
from mcp_spotify_player.config import Config


TokensProvider = Callable[[], Optional[Tokens]]


class SpotifyClient:
    """Unified interface to the Spotify Web API."""

    def __init__(self, tokens_provider: TokensProvider | None = None):
        self.tokens_provider: TokensProvider = tokens_provider or (lambda: None)
        self.config = Config()
        self.playback = SpotifyPlaybackClient(self)
        self.playlists = SpotifyPlaylistsClient(self)

    def _make_request(self, method: str, endpoint: str, **kwargs):
        tokens = self.tokens_provider()
        if tokens is None:
            raise NotAuthenticatedError("Not authenticated with Spotify. Run /auth.")
        if is_token_expired(tokens):
            raise TokenExpiredError("Access token expired. Run /auth or refresh tokens.")

        headers = {
            "Authorization": f"Bearer {tokens.access_token}",
            "Content-Type": "application/json",
        }
        url = f"{self.config.SPOTIFY_API_BASE}{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)

        if response.status_code in [200, 201, 204]:
            if method == "PUT" and endpoint == "/me/player/repeat":
                return True
            try:
                return response.json() if response.text else True
            except ValueError:
                return True

        try:
            return response.json()
        except Exception:
            return {"error": response.text}

    def __getattr__(self, name):
        for client in (self.playback, self.playlists):
            if hasattr(client, name):
                return getattr(client, name)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")
