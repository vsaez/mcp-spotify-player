import pytest
from src.config import Config


def test_playlist_modify_private_scope_present():
    assert "playlist-modify-private" in Config.SPOTIFY_SCOPES
    assert all(" - " not in scope for scope in Config.SPOTIFY_SCOPES)
