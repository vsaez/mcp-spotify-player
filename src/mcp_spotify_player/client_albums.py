from typing import Any, Dict, List, Optional

from mcp_logging import get_logger

logger = get_logger(__name__)


class SpotifyAlbumsClient:
    """Client specialized in album-related operations."""

    def __init__(self, requester):
        """Initialise with an object providing ``_make_request``."""
        self.requester = requester

    def get_album(self, album_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single album by its Spotify ID."""
        logger.info("spotify_client -- Getting album with id %s", album_id)
        result = self.requester._make_request("GET", f"/albums/{album_id}")
        logger.debug("Response getting album by id %s: %s", album_id, result)
        return result

    def get_albums(self, album_ids: List[str]) -> Optional[Dict[str, Any]]:
        """Retrieve multiple albums by their Spotify IDs."""
        ids_param = ",".join(album_ids)
        logger.info("spotify_client -- Getting albums with ids %s", ids_param)
        result = self.requester._make_request(
            "GET",
            "/albums",
            params={"ids": ids_param},
        )
        logger.debug(
            "Response getting albums by ids %s: %s",
            ids_param,
            result,
        )
        return result

    def get_album_tracks(self, album_id: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """Retrieve tracks for a specific album."""
        logger.info(
            "spotify_client -- Getting tracks for album id %s", album_id
        )
        params = {"limit": limit}
        result = self.requester._make_request(
            "GET", f"/albums/{album_id}/tracks", params=params
        )
        logger.debug(
            "Response getting tracks for album id %s: %s", album_id, result
        )
        return result

    def get_saved_albums(self, limit: int = 20) -> Optional[Dict[str, Any]]:
        """Retrieve albums saved in the user's library."""
        params = {"limit": limit}
        logger.info(
            "spotify_client -- Getting user saved albums with limit %s", limit
        )
        result = self.requester._make_request(
            "GET",
            "/me/albums",
            feature="albums",
            params=params,
        )
        logger.debug("Response getting user saved albums: %s", result)
        return result

    def save_albums(self, album_ids: List[str]) -> bool:
        """Save one or more albums to the user's library."""
        ids_param = ",".join(album_ids)
        logger.info(
            "spotify_client -- Saving albums with ids %s", ids_param
        )
        result = self.requester._make_request(
            "PUT",
            "/me/albums",
            feature="albums",
            json={"ids": album_ids},
        )
        logger.debug("Response saving albums %s: %s", ids_param, result)
        return result is not None
