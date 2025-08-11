import mcp_spotify_player
from mcp_spotify_player import cli


def test_package_importable():
    assert mcp_spotify_player is not None


def test_cli_main_exists():
    assert callable(cli.main)
