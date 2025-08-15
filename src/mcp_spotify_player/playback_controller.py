import logging
from typing import Any, Dict, List, Optional

from mcp_spotify_player.mcp_models import TrackInfo
from mcp_spotify_player.spotify_client import SpotifyClient

logger = logging.getLogger(__name__)


class PlaybackController:
    """Controller for playback-related operations using SpotifyClient."""

    def __init__(self, client: SpotifyClient):
        self.client = client
        self.playback_client = client.playback
        self.playlists_client = client.playlists

    def play_music(
            self,
            query: Optional[str] = None,
            playlist_name: Optional[str] = None,
            track_uri: Optional[str] = None,
            artist_uri: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Play music based on different parameters"""

        def handle_play_result(result, success_message):
            if isinstance(result, dict) and "error" in result:
                error_msg = result["error"].get("message", "Unknow error")
                return {"success": False, "message": error_msg}
            elif result is None or result == {}:
                return {"success": True, "message": success_message}
            elif result:
                return {"success": True, "message": success_message}
            else:
                return {"success": False, "message": "Playback could not be started"}

        try:
            if track_uri:
                result = self.playback_client.play(uris=[track_uri])
                return handle_play_result(result, "Playing specific song")
            elif artist_uri:
                result = self.playback_client.play(context_uri=artist_uri)
                return handle_play_result(result, "Playing artist")
            elif playlist_name:
                playlists = self.playlists_client.get_user_playlists()
                if playlists and 'items' in playlists:
                    for playlist in playlists['items']:
                        if playlist['name'].lower() == playlist_name.lower():
                            result = self.playback_client.play(context_uri=playlist['uri'])
                            return handle_play_result(result, f"Playing playlist: {playlist['name']}")
                    return {"success": False, "message": f"Playlist '{playlist_name}' not found"}
            elif query:
                search_result = self.playback_client.search_tracks(query, limit=1)
                if search_result and 'tracks' in search_result and search_result['tracks']['items']:
                    track = search_result['tracks']['items'][0]
                    result = self.playback_client.play(uris=[track['uri']])
                    return handle_play_result(result, f"Playing: {track['name']} - {track['artists'][0]['name']}")
                return {"success": False, "message": f"Songs not found for '{query}'"}
            else:
                result = self.playback_client.play()
                return handle_play_result(result, "playback resumed")
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def pause_music(self) -> Dict[str, Any]:
        """Pause playback"""
        try:
            success = self.playback_client.pause()
            if success:
                return {"success": True, "message": "Playback paused"}
            return {"success": False, "message": "Could not pause playback"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def skip_next(self) -> Dict[str, Any]:
        """Skip to the next song"""
        try:
            success = self.playback_client.skip_next()
            if success:
                return {"success": True, "message": "Skipping to the next song"}
            return {"success": False, "message": "Could not skip to the next song"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def skip_previous(self) -> Dict[str, Any]:
        """Skip to the previous song"""
        try:
            success = self.playback_client.skip_previous()
            if success:
                return {"success": True, "message": "Skipping to the previous song"}
            return {"success": False, "message": "Could not skip to the previous song"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def set_volume(self, volume_percent: int) -> Dict[str, Any]:
        """Set the volume"""
        try:
            success = self.playback_client.set_volume(volume_percent)
            if success:
                return {"success": True, "message": f"Volume set to {volume_percent}%"}
            return {"success": False, "message": "Could not change volume"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def set_repeat(self, state: str) -> Dict[str, Any]:
        """Set the repeat mode"""
        try:
            success = self.playback_client.set_repeat(state)
            if success:
                return {"success": True, "message": f"Repeat mode set to {state}"}
            return {"success": False, "message": "Could not set repeat mode"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_current_playing(self) -> Dict[str, Any]:
        """Gets the information of the current song"""
        try:
            current = self.playback_client.get_current_playing()
            if current and 'item' in current:
                track = current['item']
                track_info = TrackInfo(
                    name=track['name'],
                    artist=track['artists'][0]['name'],
                    album=track['album']['name'],
                    uri=track['uri'],
                    duration_ms=track['duration_ms'],
                    external_url=track['external_urls']['spotify'],
                )
                return {
                    "success": True,
                    "track": track_info.dict(),
                    "is_playing": current.get('is_playing', False),
                    "progress_ms": current.get('progress_ms', 0),
                }
            return {"success": False, "message": "There is no music currently playing"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_playback_state(self) -> Dict[str, Any]:
        """Gets the full playback status"""
        try:
            state = self.playback_client.get_playback_state()
            if state:
                current_track = None
                if state.get('item'):
                    track = state['item']
                    current_track = TrackInfo(
                        name=track['name'],
                        artist=track['artists'][0]['name'],
                        album=track['album']['name'],
                        uri=track['uri'],
                        duration_ms=track['duration_ms'],
                        external_url=track['external_urls']['spotify'],
                    ).dict()

                playback_state = {
                    "is_playing": state.get('is_playing', False),
                    "current_track": current_track,
                    "volume_percent": state.get('device', {}).get('volume_percent', 0),
                    "device_name": state.get('device', {}).get('name'),
                    "shuffle_state": state.get('shuffle_state', False),
                    "repeat_state": state.get('repeat_state', 'off'),
                }
                return {"success": True, "state": playback_state}
            return {"success": False, "message": "Could not get playback status"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_devices(self) -> Dict[str, Any]:
        """Get available playback devices"""
        try:
            devices_data = self.playback_client.get_devices()
            if devices_data and devices_data.get('devices'):
                devices = [
                    {
                        "id": d.get('id'),
                        "name": d.get('name'),
                        "type": d.get('type'),
                        "is_active": d.get('is_active', False),
                        "volume_percent": d.get('volume_percent'),
                    }
                    for d in devices_data['devices']
                ]
                return {"success": True, "devices": devices}
            return {"success": False, "message": "No devices available"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def search_music(self, query: str, search_type: str = "track", limit: int = 10) -> Dict[str, Any]:
        """Search for music on Spotify"""
        try:
            if search_type == "track":
                result = self.playback_client.search_tracks(query, limit)
                if result:
                    tracks: List[Dict[str, Any]] = []
                    if 'tracks' in result and 'items' in result['tracks']:
                        for track in result['tracks']['items']:
                            track_info = TrackInfo(
                                name=track['name'],
                                artist=track['artists'][0]['name'],
                                album=track['album']['name'],
                                uri=track['uri'],
                                duration_ms=track['duration_ms'],
                                external_url=track['external_urls']['spotify'],
                            )
                            tracks.append(track_info.dict())

                    return {
                        "success": True,
                        "tracks": tracks,
                        "total_results": result.get('tracks', {}).get('total', 0),
                    }
                return {"success": False, "message": "No results found"}

            elif search_type == "artist":
                result = self.playback_client.search_artists(query, limit)
                if result:
                    artists: List[Dict[str, Any]] = []
                    if 'artists' in result and 'items' in result['artists']:
                        for artist in result['artists']['items']:
                            artists.append(
                                {
                                    "name": artist['name'],
                                    "uri": artist['uri'],
                                    "external_url": artist['external_urls']['spotify'],
                                }
                            )

                    return {
                        "success": True,
                        "artists": artists,
                        "total_results": result.get('artists', {}).get('total', 0),
                    }
                return {"success": False, "message": "No results found"}

            else:
                return {"success": False, "message": f"Search type '{search_type}' not supported"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def queue_add(self, uri: str, device_id: str | None = None) -> dict:
        """Add a track/episode to the active device queue."""
        try:
            self.playback_client.add_to_queue(uri, device_id)
            return {"success": True, "message": f"Queued: {uri}", "uri": uri, "device_id": device_id}
        except Exception as e:
            return {"success": False, "message": f"Error queueing item: {e}"}

    def queue_list(self, limit: int | None = None) -> dict:
        """Thin wrapper to match MCP tool name → delegates to client.get_queue()."""
        return self.playback_client.get_queue(limit=limit)

    def is_authenticated(self) -> bool:
        """Checks if the user is authenticated"""
        try:
            state = self.playback_client.get_playback_state()
            return state is not None
        except Exception:
            return False
