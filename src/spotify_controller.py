from typing import Optional, Dict, Any, List
from src.spotify_client import SpotifyClient
from src.mcp_models import TrackInfo, PlaybackState, SearchResult, PlaylistInfo

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpotifyController:
    def __init__(self):
        self.client = SpotifyClient()

    def play_music(self, query: Optional[str] = None, playlist_name: Optional[str] = None,
                   track_uri: Optional[str] = None, artist_uri: Optional[str] = None) -> Dict[str, Any]:
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
                result = self.client.play(uris=[track_uri])
                return handle_play_result(result, "Playing specific song")

            elif artist_uri:
                result = self.client.play(context_uri=artist_uri)
                return handle_play_result(result, "Playing artist")

            elif playlist_name:
                playlists = self.client.get_user_playlists()
                if playlists and 'items' in playlists:
                    for playlist in playlists['items']:
                        if playlist['name'].lower() == playlist_name.lower():
                            result = self.client.play(context_uri=playlist['uri'])
                            return handle_play_result(result, f"Playing playlist: {playlist['name']}")
                    return {"success": False, "message": f"Playlist '{playlist_name}' not found"}

            elif query:
                search_result = self.client.search_tracks(query, limit=1)
                if search_result and 'tracks' in search_result and search_result['tracks']['items']:
                    track = search_result['tracks']['items'][0]
                    result = self.client.play(uris=[track['uri']])
                    return handle_play_result(result, f"Playing: {track['name']} - {track['artists'][0]['name']}")
                return {"success": False, "message": f"Songs not found for '{query}'"}

            else:
                result = self.client.play()
                return handle_play_result(result, "playback resumed")

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def pause_music(self) -> Dict[str, Any]:
        """Pausa la reproducción"""
        try:
            success = self.client.pause()
            if success:
                return {"success": True, "message": "Playback paused"}
            return {"success": False, "message": "Could not pause playback"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def skip_next(self) -> Dict[str, Any]:
        """Skip to the next song"""
        try:
            success = self.client.skip_next()
            if success:
                return {"success": True, "message": "Skipping to the next song"}
            return {"success": False, "message": "Could not skip to the next song"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def skip_previous(self) -> Dict[str, Any]:
        """Skip to the previous song"""
        try:
            success = self.client.skip_previous()
            if success:
                return {"success": True, "message": "Skipping to the previous song"}
            return {"success": False, "message": "Could not skip to the previous song"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def set_volume(self, volume_percent: int) -> Dict[str, Any]:
        """Set the volume"""
        try:
            success = self.client.set_volume(volume_percent)
            if success:
                return {"success": True, "message": f"Volume set to {volume_percent}%"}
            return {"success": False, "message": "Could not change volume"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_current_playing(self) -> Dict[str, Any]:
        """Gets the information of the current song"""
        try:
            current = self.client.get_current_playing()
            if current and 'item' in current:
                track = current['item']
                track_info = TrackInfo(
                    name=track['name'],
                    artist=track['artists'][0]['name'],
                    album=track['album']['name'],
                    uri=track['uri'],
                    duration_ms=track['duration_ms'],
                    external_url=track['external_urls']['spotify']
                )
                return {
                    "success": True, 
                    "track": track_info.dict(),
                    "is_playing": current.get('is_playing', False),
                    "progress_ms": current.get('progress_ms', 0)
                }
            return {"success": False, "message": "There is no music currently playing"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_playback_state(self) -> Dict[str, Any]:
        """Gets the full playback status"""
        try:
            state = self.client.get_playback_state()
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
                        external_url=track['external_urls']['spotify']
                    ).dict()
                
                playback_state = {
                    "is_playing": state.get('is_playing', False),
                    "current_track": current_track,
                    "volume_percent": state.get('device', {}).get('volume_percent', 0),
                    "device_name": state.get('device', {}).get('name'),
                    "shuffle_state": state.get('shuffle_state', False),
                    "repeat_state": state.get('repeat_state', 'off')
                }
                return {"success": True, "state": playback_state}
            return {"success": False, "message": "Could not get playback status"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def search_music(self, query: str, search_type: str = "track", limit: int = 10) -> Dict[str, Any]:
        """Search for music on Spotify"""
        try:
            if search_type == "track":
                result = self.client.search_tracks(query, limit)
            elif search_type == "artist":
                result = self.client.search_artists(query, limit)
            else:
                return {"success": False, "message": f"Search type '{search_type}' not supported"}
            
            if result:
                tracks = []
                if 'tracks' in result and 'items' in result['tracks']:
                    for track in result['tracks']['items']:
                        track_info = TrackInfo(
                            name=track['name'],
                            artist=track['artists'][0]['name'],
                            album=track['album']['name'],
                            uri=track['uri'],
                            duration_ms=track['duration_ms'],
                            external_url=track['external_urls']['spotify']
                        )
                        tracks.append(track_info.dict())
                
                return {
                    "success": True, 
                    "tracks": tracks,
                    "total_results": result.get('tracks', {}).get('total', 0) if 'tracks' in result else 0
                }
            return {"success": False, "message": "No results found"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_playlists(self) -> Dict[str, Any]:
        """Gets the user's playlists"""
        try:
            playlists = self.client.get_user_playlists()
            if playlists and 'items' in playlists:
                playlist_list = []
                for playlist in playlists['items']:
                    playlist_info = PlaylistInfo(
                        id=playlist['id'],
                        name=playlist['name'],
                        description=playlist.get('description'),
                        owner=playlist['owner']['display_name'],
                        track_count=playlist['tracks']['total'],
                        uri=playlist['uri']
                    )
                    playlist_list.append(playlist_info.dict())
                
                return {
                    "success": True, 
                    "playlists": playlist_list,
                    "total_playlists": playlists.get('total', 0)
                }
            return {"success": False, "message": "Could not get playlists"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def is_authenticated(self) -> bool:
        """Checks if the user is authenticated"""
        try:
            # Attempt to get playback status to verify authentication
            state = self.client.get_playback_state()
            return state is not None
        except:
            return False

    def get_playlist_tracks(self, playlist_id: str, limit: int = 20) -> Dict[str, Any]:
        """Gets songs from a playlist"""
        try:
            if not self._validate_spotify_id(playlist_id):
                return {'success': False, 'message': 'ID de playlist inválido. Debe ser un ID de Spotify válido.'}

            tracks = self.client.get_playlist_tracks(playlist_id, limit)
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
                        external_url=track['external_urls']['spotify']
                    )
                    track_list.append(track_info.dict())

                return {
                    "success": True,
                    "tracks": track_list,
                    "total_tracks": tracks.get('total', 0)
                }
            return {"success": False, "message": "Could not get playlist tracks"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def rename_playlist(self, playlist_id: str, playlist_name: str) -> Dict[str, Any]:
        """Rename a playlist from the user's library"""
        logger.info(f"DEBUG: spotify_controller : Renaming playlist with id {playlist_id}")
        try:
            if not self._validate_spotify_id(playlist_id):
                return {'success': False, 'message': 'Invalid playlist ID. It must be a valid Spotify ID.'}
            result = self.client.rename_playlist(playlist_id,playlist_name)
            if result:
                return {"success": True, "message": "Playlist renamed successfully"}
            return {"success": False, "message": "Could not rename the playlist"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def create_playlist(self, playlist_name: str) -> Dict[str, Any]:
        """Create a new playlist with the given name"""
        try:
            result = self.client.create_playlist(playlist_name)
            if result and result.get('id'):
                return {
                    "success": True,
                    "playlist": {
                        "id": result["id"],
                        "name": result["name"],
                        "uri": result.get("uri")
                    }
                }
            return {"success": False, "message": "Could not create playlist"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}


    def _validate_spotify_id(self, id_string: str) -> bool:
        """Validates if the string it's a valid Spotify ID"""
        # And usual ID has 22 alphanumeric characters
        return bool(id_string) and len(id_string) > 10 and all(c.isalnum() for c in id_string)
