from mcp_spotify_player.client_auth import SpotifyAuthClient
from mcp_spotify_player.client_playback import SpotifyPlaybackClient
from mcp_spotify_player.client_playlists import SpotifyPlaylistsClient


class SpotifyClient:
    """Unified interface that composes auth, playback and playlist clients."""

    def __init__(self):
        self.auth = SpotifyAuthClient()
        # Expose _make_request so tests can patch it on the main client
        self._make_request = self.auth._make_request
        self.playback = SpotifyPlaybackClient(self)
        self.playlists = SpotifyPlaylistsClient(self)

    def __getattr__(self, name):
        for client in (self.playback, self.playlists, self.auth):
            if hasattr(client, name):
                return getattr(client, name)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")
