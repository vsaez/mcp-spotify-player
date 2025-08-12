import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from mcp_spotify.auth.tokens import Tokens, load_tokens, needs_refresh
from mcp_spotify_player.config import Config, resolve_tokens_path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def try_load_tokens() -> Optional[Tokens]:
    """Attempt to load tokens from disk.

    Returns ``None`` if the token file does not exist. If the file exists but
    is invalid an ``InvalidTokenFileError`` is raised.
    """

    path: Path = resolve_tokens_path()
    if not path.exists():
        return None
    return load_tokens(path)


def is_token_expired(tokens: Tokens, now: int | None = None) -> bool:
    """Compatibility wrapper around :func:`needs_refresh`."""

    return needs_refresh(tokens, now)


class SpotifyAuthClient:
    """Handles Spotify authentication and token management."""

    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = 0
        self.scopes: list[str] = []
        self.config = Config()

        # Get project dir path
        # Determine tokens storage path
        tokens_path = os.getenv("MCP_SPOTIFY_TOKENS_PATH")
        if tokens_path:
            self.tokens_file = os.path.expanduser(tokens_path)
        else:
            self.tokens_file = os.path.expanduser(
                os.path.join("~", ".config", "mcp_spotify_player", "tokens.json")
            )

    def get_auth_url(self) -> str:
        """Generate Spotify Authorization URL"""
        params = {
            "client_id": self.config.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": self.config.SPOTIFY_REDIRECT_URI,
            "scope": " ".join(self.config.SPOTIFY_SCOPES),
            "show_dialog": "true",
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.config.SPOTIFY_AUTH_URL}?{query_string}"

    def exchange_code_for_tokens(self, auth_code: str) -> bool:
        """Exchange the authorization code for tokens"""
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.config.SPOTIFY_REDIRECT_URI,
            "client_id": self.config.SPOTIFY_CLIENT_ID,
            "client_secret": self.config.SPOTIFY_CLIENT_SECRET,
        }
        response = requests.post(self.config.SPOTIFY_TOKEN_URL, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token")
            self.scopes = token_data.get("scope", "").split()
            self.token_expires_at = int(time.time()) + int(token_data["expires_in"])
            self._save_tokens()
            return True
        return False

    def refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            return False
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.config.SPOTIFY_CLIENT_ID,
            "client_secret": self.config.SPOTIFY_CLIENT_SECRET,
        }
        response = requests.post(self.config.SPOTIFY_TOKEN_URL, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expires_at = int(time.time()) + int(token_data["expires_in"])
            if "refresh_token" in token_data:
                self.refresh_token = token_data["refresh_token"]
            self._save_tokens()
            return True
        return False

    def _save_tokens(self):
        """Save the tokens to a local file"""
        token_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": int(self.token_expires_at),
            "scopes": self.scopes,
        }
        os.makedirs(os.path.dirname(self.tokens_file), exist_ok=True)
        with open(self.tokens_file, "w") as f:
            json.dump(token_data, f)

    def _load_tokens(self) -> bool:
        """Load tokens from local file"""
        try:
            with open(self.tokens_file) as f:
                token_data = json.load(f)
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            self.token_expires_at = token_data["expires_at"]
            self.scopes = token_data.get("scopes", [])
            return True
        except FileNotFoundError:
            return False

    def _get_valid_token(self) -> Optional[str]:
        """Obtains a valid token, refreshing if necessary"""
        if not self.access_token:
            if not self._load_tokens():
                return None
        if time.time() >= self.token_expires_at - 60:
            if not self.refresh_access_token():
                return None
        return self.access_token

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make a request to the Spotify API"""
        token = self._get_valid_token()
        if not token:
            sys.stderr.write(f"INFO: Could not obtain valid token for {endpoint}\n")
            return None
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"{self.config.SPOTIFY_API_BASE}{endpoint}"
        params_str = ""
        if "params" in kwargs:
            params_str = f" with params : {kwargs['params']}"
        sys.stderr.write(f"DEBUG: Making request {method} to {endpoint}{params_str}\n")
        response = requests.request(method, url, headers=headers, **kwargs)
        sys.stderr.write(f"DEBUG: Response {response.status_code} for {endpoint}\n")
        if response.status_code in [200, 201, 204]:
            if method == "PUT" and endpoint == "/me/player/repeat":
                return True
            try:
                return response.json() if response.text else True
            except ValueError:
                return True
        else:
            sys.stderr.write(
                f"DEBUG: Error {response.status_code} for {endpoint}: {response.text}\n"
            )
            try:
                sys.stderr.write(
                    f"DEBUG: Trying to parse JSON response for  {endpoint}\n. Response: {response.json()}\n"
                )
                return response.json()
            except Exception:
                sys.stderr.write(f"DEBUG: Error for {endpoint}: {response}\n")
                return {"error": response.text}
