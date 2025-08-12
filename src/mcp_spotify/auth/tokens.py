from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import requests
import time

from mcp_spotify.errors import InvalidTokenFileError, RefreshNotPossibleError
from mcp_spotify_player.config import Config, resolve_tokens_path


@dataclass(slots=True)
class Tokens:
    access_token: str
    refresh_token: str
    expires_at: int


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
    )

    path = resolve_tokens_path()
    path.write_text(json.dumps(asdict(refreshed)))
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
    if not path.exists():
        raise InvalidTokenFileError(f"Token file not found: {path}")

    try:
        data: dict[str, Any] = json.loads(path.read_text())
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

    return Tokens(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_at=data["expires_at"],
    )
