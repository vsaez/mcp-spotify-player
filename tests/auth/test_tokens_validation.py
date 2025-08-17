from __future__ import annotations

from pathlib import Path
import json

import pytest

from mcp_spotify.auth.tokens import Tokens, load_tokens
from mcp_spotify.errors import InvalidTokenFileError


def test_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "missing.json"
    with pytest.raises(InvalidTokenFileError):
        load_tokens(path)


def test_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "tokens.json"
    path.write_text("{")
    with pytest.raises(InvalidTokenFileError):
        load_tokens(path)


def test_missing_keys(tmp_path: Path) -> None:
    path = tmp_path / "tokens.json"
    path.write_text('{"access_token": "a"}')
    with pytest.raises(InvalidTokenFileError) as exc:
        load_tokens(path)
    assert "missing" in str(exc.value)


def test_wrong_types(tmp_path: Path) -> None:
    path = tmp_path / "tokens.json"
    path.write_text('{"access_token": 123, "refresh_token": "r", "expires_at": "1"}')
    with pytest.raises(InvalidTokenFileError) as exc:
        load_tokens(path)
    assert "invalid types" in str(exc.value)


def test_valid_tokens(tmp_path: Path) -> None:
    path = tmp_path / "tokens.json"
    data = '{"access_token": "a", "refresh_token": "r", "expires_at": 1}'
    path.write_text(data)
    tokens = load_tokens(path)
    assert isinstance(tokens, Tokens)
    assert tokens.access_token == "a"
    assert tokens.refresh_token == "r"
    assert tokens.expires_at == 1


def test_load_tokens_minimal_shape_without_scopes(tmp_path: Path) -> None:
    path = tmp_path / "tokens.json"
    data = {"access_token": "a", "refresh_token": "r", "expires_at": 1}
    path.write_text(json.dumps(data))
    tokens = load_tokens(path)
    assert tokens.scopes == set()
