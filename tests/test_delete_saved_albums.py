from unittest.mock import patch

from unittest.mock import patch

from mcp_spotify_player.spotify_client import SpotifyClient
from mcp_spotify_player.spotify_controller import SpotifyController
from mcp_spotify_player.mcp_stdio_server import MCPServer


def test_spotify_client_delete_saved_albums():
    client = SpotifyClient()
    with patch.object(client, "_make_request", return_value=True) as mock_request:
        assert client.delete_saved_albums(["album1", "album2"]) is True
        mock_request.assert_called_once_with(
            "DELETE",
            "/me/albums",
            feature="albums",
            json={"ids": ["album1", "album2"]},
        )


def test_album_controller_delete_saved_albums():
    controller = SpotifyController(lambda: None)
    with patch.object(
        controller.albums_client, "delete_saved_albums", return_value=True
    ) as mock_delete:
        result = controller.delete_saved_albums(["1234567890a"])
        assert result["success"] is True
        mock_delete.assert_called_once_with(["1234567890a"])


def test_album_controller_delete_saved_albums_invalid():
    controller = SpotifyController(lambda: None)
    result = controller.delete_saved_albums(["bad id!"])
    assert result["success"] is False


def test_mcp_server_delete_saved_albums():
    server = MCPServer()
    assert any(
        tool["name"] == "delete_saved_albums" for tool in server.manifest["tools"]
    )
    with patch.object(
        server.controller,
        "delete_saved_albums",
        return_value={"success": True, "message": "Albums deleted successfully"},
    ) as mock_delete:
        server.TOOL_HANDLERS["delete_saved_albums"] = server.controller.delete_saved_albums
        result = server.execute_tool(
            "delete_saved_albums", {"album_ids": ["1234567890a"]}
        )
        assert "deleted" in result.lower()
        mock_delete.assert_called_once_with(album_ids=["1234567890a"])
