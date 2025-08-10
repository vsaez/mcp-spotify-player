#!/usr/bin/env python3
"""
MCP server for Spotify Player using stdio
Implements the MCP protocol over JSON-RPC for communication with Cursor
"""

import json
import sys
import logging
from typing import Dict, Any
from src.config import Config
from src.spotify_controller import SpotifyController

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServer:
    def __init__(self):
        self.config = Config()
        self.controller = SpotifyController()
        self.request_id = 0

        # MCP Manifest
        self.manifest = {
            "schema_url": "https://json-schema.org/draft/2020-12/schema",
            "nameForHuman": "Spotify Player",
            "nameForModel": "spotify_player",
            "descriptionForHuman": "Control your Spotify music using natural commands",
            "descriptionForModel": "Tool for controlling music playback on Spotify. You can play songs, pause, skip, adjust volume, search for music, and more.",
            "auth": {
                "type": "oauth",
                "instructions": "You need to authenticate with Spotify to use this tool"
            },
            "tools": [
                {
                    "name": "play_music",
                    "description": "Play music on Spotify. You can specify a song, artist, playlist or simply resume playback.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Song or artist search (e.g., 'REM', 'Bohemian Rhapsody')"
                            },
                            "playlist_name": {
                                "type": "string",
                                "description": "Name of the playlist to play"
                            },
                            "track_uri": {
                                "type": "string",
                                "description": "Specific track URI"
                            },
                            "artist_uri": {
                                "type": "string",
                                "description": "Specific artist URI"
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
                    "description": "Skip to the next song in the playback queue",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "skip_previous",
                    "description": "Skip to the previous song in the playback queue",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "set_volume",
                    "description": "Set the playback volume (0-100%)",
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
                    "description": "Retrieve information about the currently playing song",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_playback_state",
                    "description": "Retrieve the full playback state including device, volume, etc.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "search_music",
                    "description": "Search for music on Spotify by track, artist, or album",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search term"
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
                                "description": "Maximum number of results"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_playlists",
                    "description": "Retrieve the user's playlists list",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_playlist_tracks",
                    "description": "Retrieve tracks from a given playlist",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "playlist_id": {"type": "string", "description": "Playlist ID"},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
                        },
                        "required": ["playlist_id"]
                    }
                },
                {
                    "name": "rename_playlist",
                    "description": "Rename a Spotify playlist by its ID to a new name",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "playlist_id": {"type": "string", "description": "Spotify playlist ID"},
                            "new_name": {"type": "string", "description": "New name for the playlist"}
                        },
                        "required": ["playlist_id", "new_name"]
                    }
                },
                {
                    "name": "create_playlist",
                    "description": "Create a new Spotify playlist with the given name",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "playlist_name": {"type": "string", "description": "Name for the new playlist"},
                            "description": {"type": "string", "description": "Optional playlist description"}
                        },
                        "required": ["playlist_name"]
                    }
                },
                {
                    "name": "add_tracks_to_playlist",
                    "description": "Add tracks to a Spotify playlist by its ID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "playlist_id": {"type": "string", "description": "Spotify playlist ID"},
                            "track_uris": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of track URIs to add"
                            }
                        },
                        "required": ["playlist_id", "track_uris"]
                    }
                }
            ]
        }

    def send_response(self, response: Dict[str, Any]):
        """Send a JSON-RPC response over stdout"""
        json_response = json.dumps(response, ensure_ascii=False) + "\n"
        sys.stdout.write(json_response)
        sys.stdout.flush()
        logger.info(f"Sending response: {response}")

    def send_error(self, request_id: Any, code: int, message: str):
        """Send a JSON-RPC error"""
        # Handle the case where request_id is None
        if request_id is None:
            return  # Do not send a response for notifications without ID

        error_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        self.send_response(error_response)

    def handle_initialize(self, request_id: Any, params: Dict[str, Any]):
        """Handle MCP client initialization"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "spotify-player",
                    "version": "1.0.0"
                }
            }
        }
        self.send_response(response)

    def handle_tools_list(self, request_id: Any):
        """List available tools"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.manifest["tools"]
            }
        }
        self.send_response(response)

    def handle_tools_call(self, request_id: Any, params: Dict[str, Any]):
        """Execute a tool"""
        try:
            # Handle both array and direct formats
            if "calls" in params:
                # Format: {"calls": [{"name": "...", "arguments": {...}}]}
                calls = params.get("calls", [])
            else:
                # Format: {"name": "...", "arguments": {...}}
                calls = [{"name": params.get("name"), "arguments": params.get("arguments", {})}]

            results = []

            for call in calls:
                tool_name = call.get("name")
                arguments = call.get("arguments", {})

                if not tool_name:
                    continue

                # Check authentication for commands that require it
                if tool_name in ["play_music", "pause_music", "skip_next", "skip_previous",
                                 "set_volume", "get_current_playing", "get_playback_state", "get_playlist_tracks",
                                 "rename_playlist", "create_playlist", "add_tracks_to_playlist"]:

                    logger.info(f"Checking authentication for {tool_name}")
                    if not self.controller.is_authenticated():
                        logger.warning(f"Not authenticated for {tool_name}")
                        results.append({
                            "name": tool_name,
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Not authenticated with Spotify. You need to authenticate first."
                                }
                            ]
                        })
                        continue
                    else:
                        logger.info(f"Authenticated successfully for {tool_name}")

                # Execute the command
                logger.info(f"Executing {tool_name} with arguments: {arguments}")
                result = self.execute_tool(tool_name, arguments)
                logger.info(f"Result of {tool_name}: {result}")
                results.append({
                    "name": tool_name,
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                })

            if len(results) == 1:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": results[0]
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "calls": results
                    }
                }

            self.send_response(response)

        except Exception as e:
            logger.error(f"Error executing tool: {str(e)}")
            self.send_error(request_id, -32603, f"Internal error: {str(e)}")

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a specific tool"""
        try:
            if tool_name == "play_music":
                result = self.controller.play_music(
                    query=arguments.get("query"),
                    playlist_name=arguments.get("playlist_name"),
                    track_uri=arguments.get("track_uri"),
                    artist_uri=arguments.get("artist_uri")
                )
                if result.get('success'):
                    return f"{result.get('message', 'Playback started')}"
                else:
                    return f"{result.get('message', 'Could not play music')}"

            elif tool_name == "pause_music":
                result = self.controller.pause_music()
                if result.get('success'):
                    return f"{result.get('message', 'Playback paused')}"
                else:
                    return f"{result.get('message', 'Could not pause')}"

            elif tool_name == "skip_next":
                result = self.controller.skip_next()
                if result.get('success'):
                    return f"{result.get('message', 'Skipping to the next song')}"
                else:
                    return f"{result.get('message', 'Could not skip')}"

            elif tool_name == "skip_previous":
                result = self.controller.skip_previous()
                if result.get('success'):
                    return f"{result.get('message', 'Skipping to the previous song')}"
                else:
                    return f"{result.get('message', 'Could not skip')}"

            elif tool_name == "set_volume":
                volume = arguments.get("volume_percent")
                if volume is None:
                    raise ValueError("volume_percent is required")
                result = self.controller.set_volume(volume)
                if result.get('success'):
                    return f"{result.get('message', f'Volume set to {volume}%')}"
                else:
                    return f"{result.get('message', 'Could not change volume')}"

            elif tool_name == "get_current_playing":
                result = self.controller.get_current_playing()
                if result.get('success'):
                    track = result.get('track', {})
                    is_playing = result.get('is_playing', False)
                    progress_ms = result.get('progress_ms', 0)

                    if track:
                        status = "Playing" if is_playing else "Paused"
                        logger.info("Debug: running get_current_playing")
                        return f"{status}: {track.get('name', 'Unknown')} by {track.get('artist', 'Unknown')}"
                    else:
                        return "No music is currently playing"
                else:
                    return f"Could not retrieve information: {result.get('message', 'Unknown error')}"

            elif tool_name == "get_playback_state":
                result = self.controller.get_playback_state()
                if result.get('success'):
                    state = result.get('state', {})
                    current_track = state.get('current_track', {})
                    is_playing = state.get('is_playing', False)
                    volume = state.get('volume_percent', 0)
                    device = state.get('device_name', 'Unknown')

                    if current_track:
                        status = "Playing" if is_playing else "Paused"
                        track_info = f"{current_track.get('name', 'Unknown')} - {current_track.get('artist', 'Unknown')}"
                        return f"{status}: {track_info} | Volume: {volume}% | Device: {device}"
                    else:
                        return f"No music playing | Volume: {volume}% | Device: {device}"
                else:
                    return f"Could not retrieve state: {result.get('message', 'Unknown error')}"

            elif tool_name == "search_music":
                query = arguments.get("query")
                if not query:
                    raise ValueError("query is required")
                result = self.controller.search_music(
                    query=query,
                    search_type=arguments.get("search_type", "track"),
                    limit=arguments.get("limit", 10)
                )
                if result.get('success'):
                    # Return full track information so clients can access URIs
                    return json.dumps(result)
                else:
                    return json.dumps({
                        "success": False,
                        "message": result.get('message', 'Unknown error')
                    })

            elif tool_name == "get_playlists":
                result = self.controller.get_playlists()
                if result.get('success'):
                    return json.dumps(result)
                else:
                    return json.dumps({
                        "success": False,
                        "message": result.get('message', 'Unknown error')
                    })

            elif tool_name == "get_playlist_tracks":
                playlist_id = arguments.get("playlist_id")
                if not playlist_id:
                    raise ValueError("playlist_id is required")

                # Validate if playlist_id is a valid Spotify ID
                if playlist_id.isdigit() and len(playlist_id) < 10:  # Most likely is an index not a real ID
                    return (
                        "Error: The provided identifier appears to be a position number, not a valid Spotify ID. "
                        "Spotify IDs are long alphanumeric codes."
                    )

                limit = arguments.get("limit", 20)
                result = self.controller.get_playlist_tracks(playlist_id, limit)
                if result.get('success'):
                    return json.dumps(result)
                else:
                    return json.dumps({
                        "success": False,
                        "message": result.get('message', 'Unknown error')
                    })

            elif tool_name == "rename_playlist":
                logger.info(f"DEBUG: mcp_stdio_server : Renaming playlist with id {arguments.get('playlist_id')}")
                playlist_id = arguments.get("playlist_id")
                new_name = arguments.get("new_name")
                if not playlist_id:
                    raise ValueError("playlist_id is required")

                # Validate if playlist_id is a valid Spotify ID
                result = self.controller.rename_playlist(playlist_id, new_name)
                if isinstance(result, dict):
                    if result.get('success'):
                        return f"{result.get('message', 'Playlist renamed successfully')}"
                    else:
                        return f"Error renaming playlist: {result.get('message', 'Unknown error')}"
                else:
                    return result

            elif tool_name == "create_playlist":
                playlist_name = arguments.get("playlist_name")
                if not playlist_name:
                    raise ValueError("playlist_name is required")
                description = arguments.get("description", "")
                result = self.controller.create_playlist(playlist_name, description)
                if result.get('success'):
                    playlist = result.get('playlist', {})
                    return f"Playlist '{playlist.get('name', playlist_name)}' created successfully"
                else:
                    return f"Error creating playlist: {result.get('message', 'Unknown error')}"

            elif tool_name == "add_tracks_to_playlist":
                playlist_id = arguments.get("playlist_id")
                track_uris = arguments.get("track_uris")
                if not playlist_id or not track_uris:
                    raise ValueError("playlist_id and track_uris are required")

                result = self.controller.add_tracks_to_playlist(playlist_id, track_uris)
                if isinstance(result, dict):
                    if result.get('success'):
                        return f"{result.get('message', 'Tracks added successfully')}"
                    else:
                        return f"Error adding tracks: {result.get('message', 'Unknown error')}"
                else:
                    return result

            else:
                raise ValueError(f"Tool '{tool_name}' not supported")

        except Exception as e:
            logger.error(f"Error executing {tool_name}: {str(e)}")
            return f"Error: {str(e)}"

    def run(self):
        """Run the MCP server"""
        logger.info("Starting MCP Spotify Player server...")

        try:
            while True:
                # Read line from stdin
                line = sys.stdin.readline()
                if not line:
                    break

                try:
                    # Parse JSON-RPC
                    request = json.loads(line.strip())
                    method = request.get("method")
                    request_id = request.get("id")
                    params = request.get("params", {})

                    logger.info(f"Received: {method}")

                    # Handle MCP methods
                    if method == "initialize":
                        self.handle_initialize(request_id, params)
                    elif method == "notifications/initialized":
                        # No action for initialization notifications
                        logger.info("Client initialized successfully")
                    elif method == "tools/list":
                        self.handle_tools_list(request_id)
                    elif method == "tools/call":
                        self.handle_tools_call(request_id, params)
                    elif method in ["resources/list", "prompts/list"]:
                        # Optional methods not implemented
                        logger.info(f"Optional method not implemented: {method}")
                        if request_id is not None:
                            self.send_error(request_id, -32601, f"Method '{method}' not implemented")
                    else:
                        logger.warning(f"Unsupported method: {method}")
                        if request_id is not None:
                            self.send_error(request_id, -32601, f"Method '{method}' not supported")

                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing request: {e}")
                    continue

        except KeyboardInterrupt:
            logger.info("Server stopped by the user")
        except Exception as e:
            logger.error(f"Server error: {e}")


if __name__ == "__main__":
    server = MCPServer()
    server.run()