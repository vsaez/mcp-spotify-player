import logging
from typing import Any

from mcp_spotify_player.playback_controller import PlaybackController
from mcp_spotify_player.playlist_controller import PlaylistController
from mcp_spotify_player.spotify_client import SpotifyClient

logger = logging.getLogger(__name__)


class SpotifyController:
    """Facade that groups playback and playlist controllers."""

    def __init__(self):
        self.client = SpotifyClient()
        self.playback = PlaybackController(self.client)
        self.playlists = PlaylistController(self.client)

    def is_authenticated(self) -> bool:
        """Checks if the user is authenticated"""
        return self.playback.is_authenticated()

    def __getattr__(self, name: str) -> Any:
        if hasattr(self.playback, name):
            return getattr(self.playback, name)
        if hasattr(self.playlists, name):
            return getattr(self.playlists, name)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")
