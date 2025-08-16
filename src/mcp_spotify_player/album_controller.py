from typing import Any, Dict, List

from mcp_logging import get_logger
from mcp_spotify_player.mcp_models import AlbumInfo, TrackInfo
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

    def get_album_tracks(self, album_id: str, limit: int = 20) -> Dict[str, Any]:
        """Retrieve tracks from an album."""
        try:
            if not self._validate_spotify_id(album_id):
                return {
                    "success": False,
                    "message": "Invalid album ID. It must be a valid Spotify ID.",
                }
            tracks_data = self.albums_client.get_album_tracks(album_id, limit)
            if tracks_data and tracks_data.get("items"):
                track_list = []
                for track in tracks_data.get("items", []):
                    track_info = TrackInfo(
                        name=track.get("name", ""),
                        artist=track.get("artists", [{}])[0].get("name", ""),
                        album=track.get("album", {}).get("name", ""),
                        uri=track.get("uri", ""),
                        duration_ms=track.get("duration_ms", 0),
                        external_url=track.get("external_urls", {}).get("spotify", ""),
                    )
                    track_list.append(track_info.dict())

                return {
                    "success": True,
                    "tracks": track_list,
                    "total_tracks": tracks_data.get("total", 0),
                }
            return {"success": False, "message": "Could not get album tracks"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_albums(self, album_ids: List[str]) -> Dict[str, Any]:
        """Retrieve information for multiple albums by their IDs."""
        try:
            if not album_ids or not all(self._validate_spotify_id(aid) for aid in album_ids):
                return {
                    "success": False,
                    "message": "Invalid album IDs. Provide valid Spotify IDs.",
                }
            albums_data = self.albums_client.get_albums(album_ids)
            if albums_data and albums_data.get("albums"):
                albums = [
                    AlbumInfo(
                        id=album.get("id", ""),
                        name=album.get("name", ""),
                        artists=[artist.get("name", "") for artist in album.get("artists", [])],
                        release_date=album.get("release_date"),
                        total_tracks=album.get("total_tracks", 0),
                        uri=album.get("uri", ""),
                    ).dict()
                    for album in albums_data.get("albums", [])
                    if album
                ]
                return {"success": True, "albums": albums}
            return {"success": False, "message": "Could not get albums"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_saved_albums(self, limit: int = 20) -> Dict[str, Any]:
        """Retrieve albums saved in the user's library."""
        try:
            saved = self.albums_client.get_saved_albums(limit)
            if saved and saved.get("items"):
                albums = []
                for item in saved.get("items", []):
                    album = item.get("album")
                    if not album:
                        continue
                    album_info = AlbumInfo(
                        id=album.get("id", ""),
                        name=album.get("name", ""),
                        artists=[artist.get("name", "") for artist in album.get("artists", [])],
                        release_date=album.get("release_date"),
                        total_tracks=album.get("total_tracks", 0),
                        uri=album.get("uri", ""),
                    )
                    albums.append(album_info.dict())

                return {
                    "success": True,
                    "albums": albums,
                    "total_albums": saved.get("total", 0),
                }
            return {"success": False, "message": "Could not get saved albums"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def _validate_spotify_id(self, id_string: str) -> bool:
        """Validates if the string is a valid Spotify ID"""
        return bool(id_string) and len(id_string) > 10 and id_string.isalnum()
