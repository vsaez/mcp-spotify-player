from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mcp_spotify.errors import InvalidTokenFileError


@dataclass(slots=True)
class Tokens:
    access_token: str
    refresh_token: str
    expires_at: int


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
