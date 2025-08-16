from typing import Any, Dict, Optional

from mcp_logging import get_logger

logger = get_logger(__name__)


class SpotifyArtistsClient:
    """Client specialized in artist-related operations."""

    def __init__(self, requester):
        """Initialise with an object providing ``_make_request``."""
        self.requester = requester

    def get_artist(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single artist by its Spotify ID."""
        logger.info("spotify_client -- Getting artist with id %s", artist_id)
        result = self.requester._make_request("GET", f"/artists/{artist_id}")
        logger.debug("Response getting artist by id %s: %s", artist_id, result)
        return result
