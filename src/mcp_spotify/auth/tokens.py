from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import requests
import time

from mcp_spotify.errors import (
    InvalidTokenFileError,
    MissingScopesError,
    RefreshNotPossibleError,
)
from mcp_spotify_player.config import Config, resolve_tokens_path
from mcp_logging import get_logger

logger = get_logger(__name__)

@dataclass(slots=True)
class Tokens:
    access_token: str
    refresh_token: str
    expires_at: int
    scopes: set[str] = field(default_factory=set)


REQUIRED_SCOPES: dict[str, set[str]] = {
    "playback": {
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
    },
    "playlists": {
        "playlist-read-private",
        "playlist-read-collaborative",
        "playlist-modify-private",
    },
}


def check_scopes(tokens: Tokens, required: set[str]) -> None:
    """Validate that ``tokens`` contain all ``required`` scopes.

    Raises
    ------
    MissingScopesError
        If any scope in ``required`` is missing.
    """

    missing = required - tokens.scopes
    if missing:
        raise MissingScopesError(missing)


def needs_refresh(tokens: Tokens, now: int | None = None) -> bool:
    """Return ``True`` if the access token is close to expiring."""

    if now is None:
        now = int(time.time())
    return now >= tokens.expires_at - 60


def refresh_tokens(tokens: Tokens, client_id: str, client_secret: str) -> Tokens:
    """Refresh ``tokens`` using Spotify's OAuth refresh flow and persist them."""

    if not tokens.refresh_token:
        raise RefreshNotPossibleError("No refresh_token. Please run /auth.")

    data = {
        "grant_type": "refresh_token",
        "refresh_token": tokens.refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(Config.SPOTIFY_TOKEN_URL, data=data)
    if response.status_code != 200:
        raise RefreshNotPossibleError(
            f"Token refresh failed: {response.status_code}"
        )
    payload: dict[str, Any] = response.json()
    refreshed = Tokens(
        access_token=payload["access_token"],
        refresh_token=payload.get("refresh_token", tokens.refresh_token),
        expires_at=int(time.time()) + int(payload["expires_in"]),
        scopes=tokens.scopes,
    )

    path = resolve_tokens_path()
    data = asdict(refreshed)
    data["scopes"] = sorted(refreshed.scopes)
    path.write_text(json.dumps(data))
    return refreshed


def load_tokens(path: Path) -> Tokens:
    """Load and validate Spotify OAuth tokens from ``path``.

    Parameters
    ----------
    path:
        The path to the JSON file containing the tokens.

    Returns
    -------
    Tokens
        The validated tokens.

    Raises
    ------
    InvalidTokenFileError
        If the file is missing, malformed, or lacks required fields.
    """
    logger.info("Loading tokens from %s", path)
    if not path.exists():
        raise InvalidTokenFileError(f"Token file not found: {path}")

    try:
        data: dict[str, Any] = json.loads(path.read_text())
        # Normalize expires_at to an integer timestamp
        if "expires_at" in data:
            data["expires_at"] = int(float(data["expires_at"]))
    except json.JSONDecodeError as exc:
        raise InvalidTokenFileError("Token file is not valid JSON") from exc

    required: list[tuple[str, type]] = [
        ("access_token", str),
        ("refresh_token", str),
        ("expires_at", int),
    ]
    missing: list[str] = []
    invalid: list[str] = []

    for key, typ in required:
        logger.info("Checking key '%s' of type %s. Value: %s", key, typ.__name__, data.get(key))
        if key not in data:
            missing.append(key)
        elif not isinstance(data[key], typ):
            invalid.append(key)

    if missing or invalid:
        parts: list[str] = []
        if missing:
            parts.append(f"missing: {', '.join(missing)}")
        if invalid:
            parts.append(f"invalid types: {', '.join(invalid)}")
        detail = "; ".join(parts)
        raise InvalidTokenFileError(f"Token file has errors: {detail}")

    # scopes may be provided as space-separated string or list
    raw_scopes = data.get("scopes") or data.get("scope", "")
    scopes: set[str]
    if isinstance(raw_scopes, list):
        scopes = set(str(s) for s in raw_scopes)
    elif isinstance(raw_scopes, str):
        scopes = set(raw_scopes.split())
    else:  # pragma: no cover - unexpected types
        scopes = set()

    return Tokens(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_at=data["expires_at"],
        scopes=scopes,
    )
