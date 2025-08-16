from typing import Any, Dict, List, Optional

from mcp_logging import get_logger

logger = get_logger(__name__)


class SpotifyPlaylistsClient:
    """Client specialized in playlist-related operations."""

    def __init__(self, requester):
        """Initialise with an object providing ``_make_request``."""
        self.requester = requester

    def get_user_playlists(self, limit: int = 20) -> Optional[Dict[str, Any]]:
        """Gets the user's playlists"""
        params = {'limit': limit}
        return self.requester._make_request('GET', '/me/playlists', feature='playlists', params=params)

    def create_playlist(
        self,
        playlist_name: str,
        description: str = "",
        public: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Create a new playlist for the current user."""
        logger.info(
            "spotify_client -- Creating playlist with name %s", playlist_name
        )
        user_profile = self.requester._make_request('GET', '/me')
        if not user_profile or 'id' not in user_profile:
            return None
        payload = {
            'name': playlist_name,
            'description': description,
            'public': public,
        }
        result = self.requester._make_request(
            'POST', f"/users/{user_profile['id']}/playlists", feature='playlists', json=payload
        )
        logger.debug("Response creating playlist %s: %s", playlist_name, result)
        return result

    def get_playlist_tracks(self, playlist_id: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """Gets songs from a playlist"""
        params = {'limit': limit}
        return self.requester._make_request('GET', f'/playlists/{playlist_id}/tracks', feature='playlists', params=params)

    def rename_playlist(self, playlist_id: str, playlist_name: str) -> bool:
        """Rename a playlist from the user's library"""
        logger.info("spotify_client -- Renaming playlist with id %s", playlist_id)
        result = self.requester._make_request(
            'PUT',
            f'/playlists/{playlist_id}',
            feature='playlists',
            json={"name": playlist_name}
        )
        logger.debug("Response renaming playlist by id %s: %s", playlist_id, result)
        return result is not None

    def clear_playlist(self, playlist_id: str) -> bool:
        """Remove all tracks from a playlist"""
        logger.info("spotify_client -- Clearing playlist with id %s", playlist_id)
        result = self.requester._make_request(
            'PUT',
            f'/playlists/{playlist_id}/tracks',
            feature='playlists',
            json={"uris": []}
        )
        logger.debug("Response clearing playlist by id %s: %s", playlist_id, result)
        return result is not None

    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> bool:
        """Add tracks to a playlist"""
        logger.info("spotify_client -- Adding tracks to playlist %s", playlist_id)
        result = self.requester._make_request(
            'POST',
            f'/playlists/{playlist_id}/tracks',
            feature='playlists',
            json={'uris': track_uris},
        )
        logger.debug("Response adding tracks to playlist %s: %s", playlist_id, result)
        return result is not None
