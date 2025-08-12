import logging
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


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
            f"DEBUG: spotify_client -- Creating playlist with name {playlist_name}"
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
        sys.stderr.write(
            f"DEBUG: Response creating playlist {playlist_name}: {result}\n"
        )
        return result

    def get_playlist_tracks(self, playlist_id: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """Gets songs from a playlist"""
        params = {'limit': limit}
        return self.requester._make_request('GET', f'/playlists/{playlist_id}/tracks', feature='playlists', params=params)

    def rename_playlist(self, playlist_id: str, playlist_name: str) -> bool:
        """Rename a playlist from the user's library"""
        logger.info(f"DEBUG: spotify_client -- Renaming playlist with id {playlist_id}")
        result = self.requester._make_request(
            'PUT',
            f'/playlists/{playlist_id}',
            feature='playlists',
            json={"name": playlist_name}
        )
        sys.stderr.write(f"DEBUG: Response renaming playlist by id {playlist_id}: {result}\n")
        return result is not None

    def clear_playlist(self, playlist_id: str) -> bool:
        """Remove all tracks from a playlist"""
        logger.info(f"DEBUG: spotify_client -- Clearing playlist with id {playlist_id}")
        result = self.requester._make_request(
            'PUT',
            f'/playlists/{playlist_id}/tracks',
            feature='playlists',
            json={"uris": []}
        )
        sys.stderr.write(f"DEBUG: Response clearing playlist by id {playlist_id}: {result}\n")
        return result is not None

    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> bool:
        """Add tracks to a playlist"""
        logger.info(f"DEBUG: spotify_client -- Adding tracks to playlist {playlist_id}")
        result = self.requester._make_request(
            'POST',
            f'/playlists/{playlist_id}/tracks',
            feature='playlists',
            json={'uris': track_uris},
        )
        sys.stderr.write(f"DEBUG: Response adding tracks to playlist {playlist_id}: {result}\n")
        return result is not None
