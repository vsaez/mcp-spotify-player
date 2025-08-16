from typing import Any, Dict

from mcp_logging import get_logger
from mcp_spotify_player.mcp_models import AlbumInfo
from mcp_spotify_player.spotify_client import SpotifyClient

logger = get_logger(__name__)


class AlbumController:
    """Controller for album-related operations using SpotifyClient."""

    def __init__(self, client: SpotifyClient):
        self.client = client
        self.albums_client = client.albums

    def get_album(self, album_id: str) -> Dict[str, Any]:
        """Retrieve album information by ID."""
        try:
            if not self._validate_spotify_id(album_id):
                return {
                    "success": False,
                    "message": "Invalid album ID. It must be a valid Spotify ID.",
                }
            album = self.albums_client.get_album(album_id)
            if album:
                album_info = AlbumInfo(
                    id=album.get("id", album_id),
                    name=album.get("name", ""),
                    artists=[artist.get("name", "") for artist in album.get("artists", [])],
                    release_date=album.get("release_date"),
                    total_tracks=album.get("total_tracks", 0),
                    uri=album.get("uri", ""),
                )
                return {"success": True, "album": album_info.dict()}
            return {"success": False, "message": "Could not get album"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def _validate_spotify_id(self, id_string: str) -> bool:
        """Validates if the string is a valid Spotify ID"""
        return bool(id_string) and len(id_string) > 10 and id_string.isalnum()
