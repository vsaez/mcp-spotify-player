import base64
import hashlib
import json
import os
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlencode, urlparse, quote

import requests

from mcp_spotify.auth.tokens import Tokens, load_tokens, needs_refresh
from mcp_spotify.errors import InvalidTokenFileError
from mcp_spotify_player.config import Config, get_tokens_path
from mcp_spotify_player.mcp_manifest import MANIFEST
from mcp_logging import get_logger

logger = get_logger(__name__)

_CODE_VERIFIER: str | None = None

APP_NAME = "mcp-spotify-player"
GITHUB_URL = "https://github.com/victor-saez-gonzalez/mcp-spotify-player"
COMMAND_NAMES = [
    "auth",
    "play_music",
    "pause_music",
    "skip_next",
    "skip_previous",
    "search_music",
    "queue_add",
    "get_current_playing",
    "set_volume",
]
INITIAL_COMMANDS = [
    tool["name"]
    for tool in MANIFEST.get("tools", [])
    if tool["name"] in COMMAND_NAMES
]
WELCOME_TEXT = (
    "You've connected your Spotify account so the MCP tools can control playback, "
    "search tracks, manage playlists and queue."
)
CLOSE_NOTE = "You can close this window and return to your client."


def build_success_page(commands: list[str]) -> str:
    items = "\n".join(f"<li><code>{cmd}</code></li>" for cmd in commands)
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
<title>{APP_NAME}</title>
<style>
body{{font-family:sans-serif;max-width:600px;margin:2rem auto;padding:1rem;line-height:1.6;background:#fff;color:#111}}
h1{{font-size:1.8rem;margin-bottom:1rem}}
h2{{font-size:1.4rem;margin-top:2rem}}
a{{color:#1DB954}}
button{{margin-top:1rem;padding:0.5rem 1rem;font-size:1rem}}
@media (prefers-reduced-motion: reduce){{*{{animation-duration:0s!important;transition:none!important}}}}
</style>
</head>
<body>
<h1>{APP_NAME}</h1>
<p>{WELCOME_TEXT}</p>
<p><a href=\"{GITHUB_URL}\">Project on GitHub</a></p>
<h2>What can I do next?</h2>
<ul>
{items}
</ul>
<button type=\"button\" onclick=\"window.close()\">Close</button>
<p>{CLOSE_NOTE}</p>
</body>
</html>"""


def build_authorize_url(scopes: list[str], state: str, pkce: bool) -> str:
    params = {
        "client_id": Config.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": Config.SPOTIFY_REDIRECT_URI,
        "scope": " ".join(scopes),
        "state": state,
    }
    if pkce:
        global _CODE_VERIFIER
        _CODE_VERIFIER = base64.urlsafe_b64encode(
            secrets.token_bytes(64)
        ).rstrip(b"=").decode()
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(_CODE_VERIFIER.encode()).digest()
        ).rstrip(b"=").decode()
        params["code_challenge"] = challenge
        params["code_challenge_method"] = "S256"
    return f"{Config.SPOTIFY_AUTH_URL}?{urlencode(params, quote_via=quote)}"


def exchange_code_for_tokens(code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": Config.SPOTIFY_REDIRECT_URI,
    }
    auth = None
    if Config.SPOTIFY_CLIENT_SECRET:
        auth = (Config.SPOTIFY_CLIENT_ID, Config.SPOTIFY_CLIENT_SECRET)
    else:
        data["client_id"] = Config.SPOTIFY_CLIENT_ID
        data["code_verifier"] = _CODE_VERIFIER or ""
    response = requests.post(Config.SPOTIFY_TOKEN_URL, data=data, auth=auth)
    response.raise_for_status()
    return response.json()


def save_tokens_minimal(tokens: dict) -> None:
    expires_at = int(time.time()) + int(tokens["expires_in"]) - 60
    data = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at": expires_at,
    }
    path = get_tokens_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data))
    try:
        os.replace(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def ensure_user_tokens() -> None:
    path = get_tokens_path()
    tokens: Tokens | None
    try:
        tokens = load_tokens(path)
    except (InvalidTokenFileError, FileNotFoundError):
        tokens = None
    if tokens and tokens.refresh_token:
        return

    logger.info("No user token found. Launching browser for Spotify OAuth…")
    state = secrets.token_urlsafe(16)
    pkce = not Config.SPOTIFY_CLIENT_SECRET
    url = build_authorize_url(Config.SPOTIFY_SCOPES, state, pkce)
    webbrowser.open(url)

    parsed = urlparse(Config.SPOTIFY_REDIRECT_URI)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 80
    callback_path = parsed.path

    event = threading.Event()
    code_holder: dict[str, str] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            parsed_qs = urlparse(self.path)
            if parsed_qs.path != callback_path:
                self.send_response(404)
                self.end_headers()
                return
            params = parse_qs(parsed_qs.query)
            if params.get("state", [""])[0] != state or "code" not in params:
                self.send_response(400)
                self.end_headers()
                return
            code_holder["code"] = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = build_success_page(INITIAL_COMMANDS)
            self.wfile.write(html.encode("utf-8"))
            event.set()
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        def log_message(self, *args, **kwargs):  # noqa: D401
            """Silence logging."""
            return

    httpd = HTTPServer((host, port), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    if not event.wait(120):
        httpd.shutdown()
        thread.join()
        raise TimeoutError(
            "Authorization not completed within timeout. Please try /auth again."
        )
    thread.join()

    token_payload = exchange_code_for_tokens(code_holder["code"])
    save_tokens_minimal(token_payload)



def try_load_tokens() -> Optional[Tokens]:
    """Attempt to load tokens from disk.

    Returns ``None`` if the token file does not exist. If the file exists but
    is invalid an ``InvalidTokenFileError`` is raised.
    """

    path: Path = get_tokens_path()
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
