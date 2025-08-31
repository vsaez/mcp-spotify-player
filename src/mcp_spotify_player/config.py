import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_tokens_path() -> Path:
    """Return the path where OAuth tokens are stored.

    The location can be overridden via the ``MCP_SPOTIFY_TOKENS_PATH``
    environment variable. The file itself is not created by this function.
    """

    env_path = os.getenv("MCP_SPOTIFY_TOKENS_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return Path("~/.config/mcp_spotify_player/tokens.json").expanduser()


# Backwards compatibility
def resolve_tokens_path() -> Path:  # pragma: no cover - legacy alias
    return get_tokens_path()


class Config:
    # Spotify API Configuration
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv(
        "SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/auth/callback"
    )

    # Server Configuration
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "127.0.0.1")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # MCP Configuration
    MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "spotify-player")
    MCP_SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "1.0.0")

    # Spotify API URLs
    SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    SPOTIFY_API_BASE = "https://api.spotify.com/v1"

    # Scopes need for Spotify API access
    SPOTIFY_SCOPES = [
        "user-read-playback-state",  # Read current playback state
        "user-modify-playback-state",  # Control playback (play, pause, skip)
        "user-read-currently-playing",  # Read what song is currently playing
        "user-read-recently-played",  # View recently played songs
        "user-read-playback-position",  # Read current position in the song
        "user-top-read",  # Read user's favorite songs/artists
        "playlist-read-private",  # Read user's private playlists
        "playlist-read-collaborative",  # Read collaborative playlists
        "playlist-modify-private",  # Modify private playlists
        "user-library-read",  # Read user's library (likes)
        "user-library-modify",  # Modify user's library (like/unlike)
    ]
