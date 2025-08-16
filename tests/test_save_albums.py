from unittest.mock import patch

from mcp_spotify_player.spotify_client import SpotifyClient
from mcp_spotify_player.spotify_controller import SpotifyController
from mcp_spotify_player.mcp_stdio_server import MCPServer


def test_spotify_client_save_albums():
    client = SpotifyClient()
    with patch.object(client, "_make_request", return_value=True) as mock_request:
        assert client.save_albums(["album1", "album2"]) is True
        mock_request.assert_called_once_with(
            "PUT",
            "/me/albums",
            feature="albums",
            json={"ids": ["album1", "album2"]},
        )


def test_album_controller_save_albums():
    controller = SpotifyController(lambda: None)
    with patch.object(
        controller.albums_client, "save_albums", return_value=True
    ) as mock_save:
        result = controller.save_albums(["1234567890a"])
        assert result["success"] is True
        mock_save.assert_called_once_with(["1234567890a"])


def test_album_controller_save_albums_invalid():
    controller = SpotifyController(lambda: None)
    result = controller.save_albums(["bad id!"])
    assert result["success"] is False


def test_mcp_server_save_albums():
    server = MCPServer()
    assert any(tool["name"] == "save_albums" for tool in server.manifest["tools"])
    with patch.object(
        server.controller,
        "save_albums",
        return_value={"success": True, "message": "Albums saved successfully"},
    ) as mock_save:
        server.TOOL_HANDLERS["save_albums"] = server.controller.save_albums
        result = server.execute_tool("save_albums", {"album_ids": ["1234567890a"]})
        assert "saved" in result.lower()
        mock_save.assert_called_once_with(album_ids=["1234567890a"])

