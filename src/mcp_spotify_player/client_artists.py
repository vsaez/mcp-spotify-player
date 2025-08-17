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

    def get_artist_albums(
        self,
        artist_id: str,
        *,
        include_groups: Optional[str] = None,
        limit: int = 20,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve albums of a specific artist."""
        logger.info(
            "spotify_client -- Getting albums for artist id %s", artist_id
        )
        params: Dict[str, Any] = {"limit": limit}
        if include_groups:
            params["include_groups"] = include_groups
        result = self.requester._make_request(
            "GET", f"/artists/{artist_id}/albums", params=params
        )
        logger.debug(
            "Response getting albums for artist id %s: %s", artist_id, result
        )
        return result

    def get_artist_top_tracks(
        self, artist_id: str, *, market: str = "US"
    ) -> Optional[Dict[str, Any]]:
        """Retrieve top tracks for a specific artist."""
        logger.info(
            "spotify_client -- Getting top tracks for artist id %s", artist_id
        )
        params: Dict[str, Any] = {"market": market}
        result = self.requester._make_request(
            "GET", f"/artists/{artist_id}/top-tracks", params=params
        )
        logger.debug(
            "Response getting top tracks for artist id %s: %s", artist_id, result
        )
        return result

    def get_artist_related_artists(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve artists related to a specific artist."""
        logger.info(
            "spotify_client -- Getting related artists for artist id %s", artist_id
        )
        result = self.requester._make_request(
            "GET", f"/artists/{artist_id}/related-artists"
        )
        logger.debug(
            "Response getting related artists for artist id %s: %s", artist_id, result
        )
        return result
