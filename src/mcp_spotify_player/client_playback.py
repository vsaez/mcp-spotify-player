import logging
import sys
from typing import Any, Dict, List, Optional


class SpotifyPlaybackClient:
    """Client specialized in playback-related operations."""

    def __init__(self, requester):
        """Initialise with an object providing ``_make_request``."""
        self.requester = requester

    def play(self, context_uri: Optional[str] = None, uris: Optional[List[str]] = None) -> bool:
        """Starts playback and returns True if successful, or the error message if it fails"""
        data = {}
        if context_uri:
            data['context_uri'] = context_uri
        elif uris:
            data['uris'] = uris
        result = self.requester._make_request(
            'PUT', '/me/player/play', feature='playback', json=data
        )
        sys.stderr.write(f"DEBUG: Received response: {result}\n")
        if result is not None:
            return result
        else:
            sys.stderr.write(f"DEBUG: Error initializing playback: {result}\n")
            return {"error": "Playback failed. Please check that you have an active device on Spotify."}

    def pause(self) -> bool:
        """Pause playback"""
        result = self.requester._make_request('PUT', '/me/player/pause', feature='playback')
        return result is not None

    def skip_next(self) -> bool:
        """Skip to the next song"""
        result = self.requester._make_request('POST', '/me/player/next', feature='playback')
        return result is not None

    def skip_previous(self) -> bool:
        """Skip to the previous song"""
        result = self.requester._make_request('POST', '/me/player/previous', feature='playback')
        return result is not None

    def set_volume(self, volume_percent: int) -> bool:
        """Sets the volume (0-100)"""
        if not 0 <= volume_percent <= 100:
            return False
        result = self.requester._make_request(
            'PUT', f'/me/player/volume?volume_percent={volume_percent}', feature='playback'
        )
        return result is not None

    def set_repeat(self, state: str, device_id: Optional[str] = None) -> bool:
        """Sets repeat mode: 'track', 'context', or 'off'"""
        if state not in {'track', 'context', 'off'}:
            return False
        params = {'state': state}
        if device_id:
            params['device_id'] = device_id
        result = self.requester._make_request(
            'PUT', '/me/player/repeat', feature='playback', params=params
        )
        logging.info(f"DEBUG: Setting repeat state to {state} with params {params} result: {result}")
        return result is not None

    def add_to_queue(self, uri: str, device_id: str | None = None) -> None:
        """Add a track or episode to the user's queue."""
        params = {"uri": uri}
        if device_id:
            params["device_id"] = device_id
        result = self.requester._make_request(
            "POST", "/me/player/queue", feature="playback", params=params
        )
        if result is not True:
            raise RuntimeError("Failed to add item to queue")

    def get_queue(self, limit: int | None = None) -> dict:
        """Fetch current queue using shared requester (_make_request)."""
        try:
            # Use the shared requester; do NOT build URLs here.
            data = self.requester._make_request("GET", "/me/player/queue")

            queue = (data.get("queue") or [])
            if limit is not None:
                queue = queue[: int(limit)]

            return {
                "success": True,
                "currently_playing": data.get("currently_playing"),
                "queue": queue,
            }
        except Exception as e:
            # Keep the server-wide error contract.
            return {"success": False, "message": f"Error fetching queue: {e}"}

    def get_current_playing(self) -> Optional[Dict[str, Any]]:
        """Gets the information of the currently playing song"""
        return self.requester._make_request('GET', '/me/player/currently-playing', feature='playback')

    def get_playback_state(self) -> Optional[Dict[str, Any]]:
        """Gets the current playback status"""
        return self.requester._make_request('GET', '/me/player', feature='playback')

    def get_devices(self) -> Optional[Dict[str, Any]]:
        """Get available playback devices"""
        return self.requester._make_request('GET', '/me/player/devices', feature='playback')

    def _search(self, query: str, type_: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Internal helper to perform a search request against Spotify."""
        params = {
            'q': query,
            'type': type_,
            'limit': limit
        }
        return self.requester._make_request('GET', '/search', params=params)

    def search(self, query: str, type_: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Search for any supported type on Spotify (track, artist, album, etc.)."""
        return self._search(query, type_, limit)

    def search_tracks(self, query: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Search for songs on Spotify."""
        return self._search(query, 'track', limit)

    def search_artists(self, query: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Search for artists on Spotify."""
        return self._search(query, 'artist', limit)
