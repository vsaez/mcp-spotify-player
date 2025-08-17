import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from mcp_spotify.auth.tokens import Tokens, load_tokens, needs_refresh
from mcp_spotify_player.config import Config, resolve_tokens_path
from mcp_logging import get_logger

logger = get_logger(__name__)


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
            self.token_expires_at = int(time.time()) + int(token_data["expires_in"]) - 60
            if token_data.get("refresh_token"):
                self.refresh_token = token_data["refresh_token"]
            self._save_tokens()
            return True
        return False

    def _save_tokens(self):
        """Save the tokens to a local file"""
        if not isinstance(self.access_token, str):
            raise TypeError("access_token must be str")
        if not isinstance(self.refresh_token, str):
            raise TypeError("refresh_token must be str")
        if not isinstance(self.token_expires_at, (int, float)):
            raise TypeError("expires_at must be int")
        data: Dict[str, Any] = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": int(self.token_expires_at),
        }
        if self.scopes:
            data["scopes"] = self.scopes
        path = Path(self.tokens_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(data))
        try:
            os.replace(tmp, path)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise

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
            logger.info("Could not obtain valid token for %s", endpoint)
            return None
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"{self.config.SPOTIFY_API_BASE}{endpoint}"
        params_str = ""
        if "params" in kwargs:
            params_str = f" with params : {kwargs['params']}"
        logger.debug("Making request %s to %s%s", method, endpoint, params_str)
        response = requests.request(method, url, headers=headers, **kwargs)
        logger.debug("Response %s for %s", response.status_code, endpoint)
        if response.status_code in [200, 201, 204]:
            if method == "PUT" and endpoint == "/me/player/repeat":
                return True
            try:
                return response.json() if response.text else True
            except ValueError:
                return True
        else:
            logger.debug(
                "Error %s for %s: %s", response.status_code, endpoint, response.text
            )
            try:
                logger.debug(
                    "Trying to parse JSON response for %s. Response: %s", endpoint, response.json()
                )
                return response.json()
            except Exception:
                logger.debug("Error for %s: %s", endpoint, response)
                return {"error": response.text}
