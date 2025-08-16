from typing import Any, Dict

from mcp_logging import get_logger
from mcp_spotify_player.mcp_models import ArtistInfo
from mcp_spotify_player.spotify_client import SpotifyClient

logger = get_logger(__name__)


class ArtistsController:
    """Controller for artist-related operations using SpotifyClient."""

    def __init__(self, client: SpotifyClient):
        self.client = client
        self.artists_client = client.artists

    def get_artist(self, artist_id: str) -> Dict[str, Any]:
        """Retrieve artist information by ID."""
        logger.info("artists_controller -- Getting artist with id %s", artist_id)
        try:
            if not self._validate_spotify_id(artist_id):
                return {
                    "success": False,
                    "message": "Invalid artist ID. It must be a valid Spotify ID.",
                }
            artist = self.artists_client.get_artist(artist_id)
            if artist:
                artist_info = ArtistInfo(
                    id=artist.get("id", artist_id),
                    name=artist.get("name", ""),
                    genres=artist.get("genres", []),
                    followers=artist.get("followers", {}).get("total", 0),
                    popularity=artist.get("popularity", 0),
                    uri=artist.get("uri", ""),
                )
                return {"success": True, "artist": artist_info.dict()}
            return {"success": False, "message": "Could not get artist"}
        except Exception as e:
            logger.error("Error retrieving artist %s: %s", artist_id, e)
            return {"success": False, "message": f"Error: {str(e)}"}

    def _validate_spotify_id(self, id_string: str) -> bool:
        """Validates if the string is a valid Spotify ID"""
        return bool(id_string) and len(id_string) > 10 and id_string.isalnum()
