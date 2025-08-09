from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
from typing import Dict, Any, Optional
from src.config import Config
from src.spotify_controller import SpotifyController
from src.mcp_models import MCPRequest, MCPResponse, MCPError

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Spotify Player",
    description="MCP server to control Spotify from Claude",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
config = Config()
controller = SpotifyController()

# MCP Manifest
MCP_MANIFEST = {
    "schema_url": "https://json-schema.org/draft/2020-12/schema",
    "nameForHuman": "Spotify Player",
    "nameForModel": "spotify_player",
    "descriptionForHuman": "Control your Spotify music using natural commands",
    "descriptionForModel": "A tool for controlling music playback on Spotify. You can play songs, pause, skip, change volume, search for music, and more.",
    "auth": {
        "type": "oauth",
        "instructions": "You need to authenticate with Spotify to use this tool."
    },
    "api": {
        "type": "openapi",
        "url": "http://127.0.0.1:8000/openapi.json"
    },
    "contactEmail": "support@example.com",
    "legalInfoUrl": "https://example.com/legal",
    "tools": [
        {
            "name": "play_music",
            "description": "Play music on Spotify. You can specify a song, artist, playlist, or simply resume playback.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search for a song or artist (e.g., 'REM', 'Bohemian Rhapsody')"
                    },
                    "playlist_name": {
                        "type": "string",
                        "description": "Name of the playlist to play"
                    },
                    "track_uri": {
                        "type": "string",
                        "description": "Song-specific URI"
                    },
                    "artist_uri": {
                        "type": "string",
                        "description": "Artist-specific URI"
                    }
                }
            }
        },
        {
            "name": "pause_music",
            "description": "Pause the current music playback",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "skip_next",
            "description": "Skip to the next song in the queue",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "skip_previous",
            "description": "Skip to the previous song in the play queue",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "set_volume",
            "description": "Sets the playback volume (0-100%)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "volume_percent": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "Volume between 0 and 100"
                    }
                },
                "required": ["volume_percent"]
            }
        },
        {
            "name": "get_current_playing",
            "description": "Gets information about the currently playing song",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_playback_state",
            "description": "Get the complete playback status including device, volume, etc.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "search_music",
            "description": "Search for music on Spotify by song, artist, or album",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Seach Term"
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["track", "artist", "album"],
                        "default": "track",
                        "description": "Search type"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10,
                        "description": "Maximum number of results to return"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "get_playlists",
            "description": "Get the user's playlists from Spotify",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "create_playlist",
            "description": "Create a new playlist in the user's library",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "playlist_name": {"type": "string", "description": "Name of the new playlist"}
                },
                "required": ["playlist_name"]
            }
        }
    ]
}

@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "MCP Spotify Player",
        "version": "1.0.0",
        "description": "MCP server to control Spotify from Claude",
        "status": "running"
    }

@app.get("/.well-known/mcp")
async def get_mcp_manifest():
    """Endpoint for the MCP manifest"""
    return MCP_MANIFEST

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Handle MCP requests"""
    try:
        body = await request.json()
        mcp_request = MCPRequest(**body)
        
        # Verify authentication for commands that require it
        if mcp_request.method in ["play_music", "pause_music", "skip_next", "skip_previous",
                                 "set_volume", "get_current_playing", "get_playback_state", "create_playlist"]:
            if not controller.is_authenticated():
                return JSONResponse(
                    status_code=401,
                    content=MCPResponse(
                        jsonrpc="2.0",
                        id=mcp_request.id,
                        error=MCPError(
                            code=-32001,
                            message="Not authenticated with Spotify. Visit /auth to authenticate."
                        ).dict()
                    ).dict()
                )
        
        # Process the command
        result = await process_mcp_command(mcp_request)
        
        return JSONResponse(
            content=MCPResponse(
                jsonrpc="2.0",
                id=mcp_request.id,
                result=result
            ).dict()
        )
    
    except Exception as e:
        logger.error(f"Error processing MCP request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=MCPResponse(
                jsonrpc="2.0",
                id=body.get("id", "unknown") if 'body' in locals() else "unknown",
                error=MCPError(
                    code=-32603,
                    message=f"Internal Server Error: {str(e)}"
                ).dict()
            ).dict()
        )

async def process_mcp_command(request: MCPRequest) -> Dict[str, Any]:
    """Processes MCP commands and calls the corresponding controller methods"""
    method = request.method
    params = request.params or {}
    
    if method == "play_music":
        return controller.play_music(
            query=params.get("query"),
            playlist_name=params.get("playlist_name"),
            track_uri=params.get("track_uri"),
            artist_uri=params.get("artist_uri")
        )
    
    elif method == "pause_music":
        return controller.pause_music()
    
    elif method == "skip_next":
        return controller.skip_next()
    
    elif method == "skip_previous":
        return controller.skip_previous()
    
    elif method == "set_volume":
        volume = params.get("volume_percent")
        if volume is None:
            raise ValueError("volume_percent is required")
        return controller.set_volume(volume)
    
    elif method == "get_current_playing":
        return controller.get_current_playing()
    
    elif method == "get_playback_state":
        return controller.get_playback_state()
    
    elif method == "search_music":
        query = params.get("query")
        if not query:
            raise ValueError("query is required")
        return controller.search_music(
            query=query,
            search_type=params.get("search_type", "track"),
            limit=params.get("limit", 10)
        )
    
    elif method == "get_playlists":
        return controller.get_playlists()

    elif method == "create_playlist":
        playlist_name = params.get("playlist_name")
        if not playlist_name:
            raise ValueError("playlist_name is required")
        return controller.create_playlist(playlist_name)

    else:
        raise ValueError(f"Method '{method}' not supported")

@app.get("/auth")
async def auth_redirect():
    """Redirects the user to Spotify authentication"""
    auth_url = controller.client.get_auth_url()
    return {
        "message": "Authentication required",
        "auth_url": auth_url,
        "instructions": "Visit the authentication URL to connect your Spotify account."
    }

@app.get("/auth/callback")
async def auth_callback(code: str):
    """Handles Spotify's authentication callback"""
    try:
        success = controller.client.exchange_code_for_tokens(code)
        if success:
            return {
                "success": True,
                "message": "Successful authentication with Spotify",
                "instructions": "You can now use music commands"
            }
        else:
            return {
                "success": False,
                "message": "Autentication error"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

@app.get("/status")
async def get_status():
    """Gets server status and authentication"""
    return {
        "server_status": "running",
        "spotify_authenticated": controller.is_authenticated(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.mcp_server:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    ) 
