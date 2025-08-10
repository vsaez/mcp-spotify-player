from typing import Dict, Any, List
import logging

from src.spotify_client import SpotifyClient
from src.mcp_models import TrackInfo, PlaylistInfo

logger = logging.getLogger(__name__)


class PlaylistController:
    """Controller for playlist-related operations using SpotifyClient."""

    def __init__(self, client: SpotifyClient):
        self.client = client
        self.playlists_client = client.playlists

    def get_playlists(self) -> Dict[str, Any]:
        """Gets the user's playlists"""
        try:
            playlists = self.playlists_client.get_user_playlists()
            if playlists and 'items' in playlists:
                playlist_list = []
                for playlist in playlists['items']:
                    playlist_info = PlaylistInfo(
                        id=playlist['id'],
                        name=playlist['name'],
                        description=playlist.get('description'),
                        owner=playlist['owner']['display_name'],
                        track_count=playlist['tracks']['total'],
                        uri=playlist['uri'],
                    )
                    playlist_list.append(playlist_info.dict())

                return {
                    "success": True,
                    "playlists": playlist_list,
                    "total_playlists": playlists.get('total', 0),
                }
            return {"success": False, "message": "Could not get playlists"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def create_playlist(self, playlist_name: str, description: str = "") -> Dict[str, Any]:
        """Create a new private playlist."""
        logger.info(
            f"DEBUG: playlist_controller : Creating playlist with name {playlist_name}"
        )
        try:
            result = self.playlists_client.create_playlist(playlist_name, description, False)
            if result:
                playlist_info = PlaylistInfo(
                    id=result.get('id', ''),
                    name=result.get('name', playlist_name),
                    description=result.get('description'),
                    owner=result.get('owner', {}).get('display_name', ''),
                    track_count=result.get('tracks', {}).get('total', 0),
                    uri=result.get('uri', ''),
                )
                return {"success": True, "playlist": playlist_info.dict()}
            return {"success": False, "message": "Could not create playlist"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_playlist_tracks(self, playlist_id: str, limit: int = 20) -> Dict[str, Any]:
        """Gets songs from a playlist"""
        try:
            if not self._validate_spotify_id(playlist_id):
                return {'success': False, 'message': 'ID de playlist inválido. Debe ser un ID de Spotify válido.'}

            tracks = self.playlists_client.get_playlist_tracks(playlist_id, limit)
            if tracks and 'items' in tracks:
                track_list = []
                for item in tracks['items']:
                    track = item['track']
                    track_info = TrackInfo(
                        name=track['name'],
                        artist=track['artists'][0]['name'],
                        album=track['album']['name'],
                        uri=track['uri'],
                        duration_ms=track['duration_ms'],
                        external_url=track['external_urls']['spotify'],
                    )
                    track_list.append(track_info.dict())

                return {
                    "success": True,
                    "tracks": track_list,
                    "total_tracks": tracks.get('total', 0),
                }
            return {"success": False, "message": "Could not get playlist tracks"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def rename_playlist(self, playlist_id: str, playlist_name: str) -> Dict[str, Any]:
        """Rename a playlist from the user's library"""
        logger.info(f"DEBUG: playlist_controller : Renaming playlist with id {playlist_id}")
        try:
            if not self._validate_spotify_id(playlist_id):
                return {'success': False, 'message': 'Invalid playlist ID. It must be a valid Spotify ID.'}
            result = self.playlists_client.rename_playlist(playlist_id, playlist_name)
            if result:
                return {"success": True, "message": "Playlist renamed successfully"}
            return {"success": False, "message": "Could not rename the playlist"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def clear_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """Remove all tracks from a playlist"""
        logger.info(f"DEBUG: playlist_controller : Clearing playlist with id {playlist_id}")
        try:
            if not self._validate_spotify_id(playlist_id):
                return {'success': False, 'message': 'Invalid playlist ID. It must be a valid Spotify ID.'}
            result = self.client.clear_playlist(playlist_id)
            if result:
                return {"success": True, "message": "Playlist cleared successfully"}
            return {"success": False, "message": "Could not clear the playlist"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> Dict[str, Any]:
        """Add tracks to a playlist"""
        try:
            if not self._validate_spotify_id(playlist_id):
                return {'success': False, 'message': 'Invalid playlist ID. It must be a valid Spotify ID.'}
            if not track_uris or not all(
                isinstance(uri, str) and uri.startswith('spotify:track:') for uri in track_uris
            ):
                return {'success': False, 'message': 'Invalid track URIs. Must be valid Spotify track URIs.'}
            result = self.playlists_client.add_tracks_to_playlist(playlist_id, track_uris)
            if result:
                return {'success': True, 'message': 'Tracks added successfully'}
            return {'success': False, 'message': 'Could not add tracks to playlist'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def _validate_spotify_id(self, id_string: str) -> bool:
        """Validates if the string is a valid Spotify ID"""
        return bool(id_string) and len(id_string) > 10 and all(c.isalnum() for c in id_string)
