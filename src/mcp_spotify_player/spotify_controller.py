from typing import Any, Callable, Optional

from mcp_logging import get_logger

from mcp_spotify.auth.tokens import Tokens
from mcp_spotify.errors import InvalidTokenFileError
from mcp_spotify_player.client_auth import is_token_expired
from mcp_spotify_player.playback_controller import PlaybackController
from mcp_spotify_player.playlist_controller import PlaylistController
from mcp_spotify_player.album_controller import AlbumController
from mcp_spotify_player.spotify_client import SpotifyClient

logger = get_logger(__name__)


TokensProvider = Callable[[], Optional[Tokens]]


class SpotifyController:
    """Facade that groups playback and playlist controllers."""

    def __init__(self, tokens_provider: TokensProvider):
        self.tokens_provider = tokens_provider
        self.client = SpotifyClient(tokens_provider)
        self.playback = PlaybackController(self.client)
        self.playlists = PlaylistController(self.client)
        self.albums = AlbumController(self.client)

    def is_authenticated(self) -> bool:
        """Checks if valid authentication tokens are available."""

        try:
            tokens = self.tokens_provider()
        except InvalidTokenFileError:
            return False
        return tokens is not None and not is_token_expired(tokens)

    def __getattr__(self, name: str) -> Any:
        if hasattr(self.playback, name):
            return getattr(self.playback, name)
        if hasattr(self.playlists, name):
            return getattr(self.playlists, name)
        if hasattr(self.albums, name):
            return getattr(self.albums, name)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")
