import requests
import json
import time
import os
import sys
from typing import Optional, Dict, Any, List
from src.config import Config

class SpotifyClient:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = 0
        self.config = Config()
        
        # Get project  dir path
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.tokens_file = os.path.join(self.project_dir, 'tokens.json')
    
    def get_auth_url(self) -> str:
        """Generate Spotify Authorization URL"""
        params = {
            'client_id': self.config.SPOTIFY_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': self.config.SPOTIFY_REDIRECT_URI,
            'scope': ' '.join(self.config.SPOTIFY_SCOPES),
            'show_dialog': 'true'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.config.SPOTIFY_AUTH_URL}?{query_string}"
    
    def exchange_code_for_tokens(self, auth_code: str) -> bool:
        """Exchange the authorization code for tokens"""
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.config.SPOTIFY_REDIRECT_URI,
            'client_id': self.config.SPOTIFY_CLIENT_ID,
            'client_secret': self.config.SPOTIFY_CLIENT_SECRET
        }
        
        response = requests.post(self.config.SPOTIFY_TOKEN_URL, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token')
            self.token_expires_at = time.time() + token_data['expires_in']
            
            # Save tokens in file
            self._save_tokens()
            return True
        
        return False
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            return False
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.config.SPOTIFY_CLIENT_ID,
            'client_secret': self.config.SPOTIFY_CLIENT_SECRET
        }
        
        response = requests.post(self.config.SPOTIFY_TOKEN_URL, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.token_expires_at = time.time() + token_data['expires_in']
            
            # Actualizar refresh token si se proporciona uno nuevo
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            
            self._save_tokens()
            return True
        
        return False
    
    def _save_tokens(self):
        """Save the tokens to a local file"""
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.token_expires_at
        }
        
        with open(self.tokens_file, 'w') as f:
            json.dump(token_data, f)
    
    def _load_tokens(self) -> bool:
        """Load tokens from local file"""
        try:
            with open(self.tokens_file, 'r') as f:
                token_data = json.load(f)
            
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.token_expires_at = token_data['expires_at']
            return True
        except FileNotFoundError:
            return False
    
    def _get_valid_token(self) -> Optional[str]:
        """Obtains a valid token, refreshing if necessary"""
        if not self.access_token:
            if not self._load_tokens():
                return None
        
        # Check if the token has expired
        if time.time() >= self.token_expires_at - 60:  # Refrescar 1 minuto antes
            if not self.refresh_access_token():
                return None
        
        return self.access_token

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make a request to the Spotify API"""
        token = self._get_valid_token()
        if not token:
            sys.stderr.write(f"INFO: Could not obtain valid token for {endpoint}\n")
            return None

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        url = f"{self.config.SPOTIFY_API_BASE}{endpoint}"

        # Building parameters for logging
        params_str = ""
        if 'params' in kwargs:
            params_str = f" with params : {kwargs['params']}"

        sys.stderr.write(f"DEBUG: Making request {method} to {endpoint}{params_str}\n")

        response = requests.request(method, url, headers=headers, **kwargs)

        sys.stderr.write(f"DEBUG: Response {response.status_code} for {endpoint}\n")

        if response.status_code in [200, 201, 204]:
            result = response.json() if response.content else {}
            sys.stderr.write(f"DEBUG: Successful outcome for{endpoint}: {result}\n")
            return result
        else:
            sys.stderr.write(f"DEBUG: Error {response.status_code} for {endpoint}: {response.text}\n")
            try:
                sys.stderr.write(f"DEBUG: Trying to parse JSON response for  {endpoint}\n. Response: {response.json()}\n")
                return response.json()
            except Exception:
                sys.stderr.write(f"DEBUG: Error for {endpoint}: {response}\n")
                return {"error": response.text}

    def play(self, context_uri: Optional[str] = None, uris: Optional[List[str]] = None) -> bool:
        """Starts playback and returns True if successful, or the error message if it fails"""
        data = {}
        if context_uri:
            data['context_uri'] = context_uri
        elif uris:
            data['uris'] = uris

        result = self._make_request('PUT', '/me/player/play', json=data)
        sys.stderr.write(f"DEBUG: Received response: {result}\n")
        if result is not None:
            return result
        else:
            sys.stderr.write(f"DEBUG: Error initializing playback: {result}\n")
            return {"error": "Playback failed. Please check that you have an active device on Spotify."}
    
    def pause(self) -> bool:
        """Pause playback"""
        result = self._make_request('PUT', '/me/player/pause')
        return result is not None
    
    def skip_next(self) -> bool:
        """Skip to the next song"""
        result = self._make_request('POST', '/me/player/next')
        return result is not None
    
    def skip_previous(self) -> bool:
        """Skip to the previous song"""
        result = self._make_request('POST', '/me/player/previous')
        return result is not None
    
    def set_volume(self, volume_percent: int) -> bool:
        """Sets the volume (0-100)"""
        if not 0 <= volume_percent <= 100:
            return False
        
        result = self._make_request('PUT', f'/me/player/volume?volume_percent={volume_percent}')
        return result is not None
    
    def get_current_playing(self) -> Optional[Dict[str, Any]]:
        """Gets the information of the currently playing song"""
        return self._make_request('GET', '/me/player/currently-playing')
    
    def get_playback_state(self) -> Optional[Dict[str, Any]]:
        """Gets the current playback status"""
        return self._make_request('GET', '/me/player')
    
    def search_tracks(self, query: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Search for songs on Spotify"""
        params = {
            'q': query,
            'type': 'track',
            'limit': limit
        }
        return self._make_request('GET', '/search', params=params)
    
    def search_artists(self, query: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Search for artists on Spotify"""
        params = {
            'q': query,
            'type': 'artist',
            'limit': limit
        }
        return self._make_request('GET', '/search', params=params)
    
    def get_user_playlists(self, limit: int = 20) -> Optional[Dict[str, Any]]:
        """Gets the user's playlists"""
        params = {'limit': limit}
        return self._make_request('GET', '/me/playlists', params=params)
    
    def get_playlist_tracks(self, playlist_id: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """Gets songs from a playlist"""
        params = {'limit': limit}
        return self._make_request('GET', f'/playlists/{playlist_id}/tracks', params=params) 