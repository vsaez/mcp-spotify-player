#!/usr/bin/env python3
"""
MCP server for Spotify Player using stdio
Implements the MCP protocol over JSON-RPC for communication with Cursor
"""

import json
import sys
import logging
from typing import Dict, Any, Optional
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
<<<<<<< HEAD
                    "description": "Obtiene las canciones de una playlist dada",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "playlist_id": {"type": "string", "description": "ID de la playlist"},
=======
                    "description": "Retrieve tracks from a given playlist",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "playlist_id": {"type": "string", "description": "Playlist ID"},
>>>>>>> 722939547f9251c7c92d98116d41467c5a817b1d
                            "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
                        },
                        "required": ["playlist_id"]
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
                
<<<<<<< HEAD
                # Verificar autenticación para comandos que la requieren
                if tool_name in ["play_music", "pause_music", "skip_next", "skip_previous", 
                               "set_volume", "get_current_playing", "get_playback_state","get_playlist_tracks"]:
                    logger.info(f"Verificando autenticación para {tool_name}")
=======
                # Check authentication for commands that require it
                if tool_name in ["play_music", "pause_music", "skip_next", "skip_previous",
                               "set_volume", "get_current_playing", "get_playback_state","get_playlist_tracks"]:
                    logger.info(f"Checking authentication for {tool_name}")
>>>>>>> 722939547f9251c7c92d98116d41467c5a817b1d
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
                    tracks = result.get('tracks', [])
                    total = result.get('total_results', 0)
                    if tracks:
                        track_list = []
                        for i, track in enumerate(tracks[:5], 1):
                            track_list.append(f"{i}. {track.get('name', 'Unknown')} - {track.get('artist', 'Unknown')}")
                        return f"Found {len(tracks)} songs for '{query}' (of {total} total):\n" + "\n".join(track_list)
                    else:
                        return f"No songs found for '{query}'"
                else:
                    return f"Search error: {result.get('message', 'Unknown error')}"
            
            elif tool_name == "get_playlists":
                result = self.controller.get_playlists()
                if result.get('success'):
                    playlists = result.get('playlists', [])
                    total = result.get('total_playlists', 0)
                    if playlists:
                        playlist_list = []
                        for i, playlist in enumerate(playlists, 1):
<<<<<<< HEAD
                            playlist_list.append(f"{i}. {playlist.get('name', 'Desconocida')} ({playlist.get('track_count', 0)} canciones)")
                            playlist_list.append(f"{i}. {playlist.get('name', 'Desconocida')} ({playlist.get('track_count', 0)} canciones) - ID: {playlist.get('id')}")
                        return f"Encontradas {len(playlists)} playlists (de {total} total):\n" + "\n".join(playlist_list)
=======
                            playlist_list.append(f"{i}. {playlist.get('name', 'Unknown')} ({playlist.get('track_count', 0)} songs)")
                            playlist_list.append(f"{i}. {playlist.get('name', 'Unknown')} ({playlist.get('track_count', 0)} songs) - ID: {playlist.get('id')}")
                        return f"Found {len(playlists)} playlists (of {total} total):\n" + "\n".join(playlist_list)
                    else:
                        return "No playlists found"
                else:
                    return f"Error fetching playlists: {result.get('message', 'Unknown error')}"
            elif tool_name == "get_playlist_tracks":
                playlist_id = arguments.get("playlist_id")
                if not playlist_id:
                    raise ValueError("playlist_id is required")

                # Validate if playlist_id is a valid Spotify ID
                if playlist_id.isdigit() and len(playlist_id) < 10:  # Most likely is an index not a real ID
                    return "Error: The provided identifier appears to be a position number, not a valid Spotify ID. Spotify IDs are long alphanumeric codes."

                limit = arguments.get("limit", 20)
                result = self.controller.get_playlist_tracks(playlist_id, limit)
                if result.get('success'):
                    tracks = result.get('tracks', [])
                    total = result.get('total_tracks', 0)
                    if tracks:
                        track_list = []
                        for i, track in enumerate(tracks[:5], 1):
                            track_list.append(f"{i}. {track.get('name', 'Unknown')} - {track.get('artist', 'Unknown')}")
                        return f"Found {len(tracks)} tracks in the playlist (of {total} total):\n" + "\n".join(track_list)
>>>>>>> 722939547f9251c7c92d98116d41467c5a817b1d
                    else:
                        return "No tracks found in the playlist"
                else:
<<<<<<< HEAD
                    return f"Error obteniendo playlists: {result.get('message', 'Error desconocido')}"
            elif tool_name == "get_playlist_tracks":
                playlist_id = arguments.get("playlist_id")
                if not playlist_id:
                    raise ValueError("playlist_id is required")

                # Validdate if playlist_id is a valid Spotify ID
                if playlist_id.isdigit() and len(playlist_id) < 10:  # Most likely is an index not a real ID
                    return "Error: The provided identifier appears to be a position number, not a valid Spotify ID. Spotify IDs are long alphanumeric codes."

                limit = arguments.get("limit", 20)
                result = self.controller.get_playlist_tracks(playlist_id, limit)
                if result.get('success'):
                    tracks = result.get('tracks', [])
                    total = result.get('total_tracks', 0)
                    if tracks:
                        track_list = []
                        for i, track in enumerate(tracks[:5], 1):
                            track_list.append(f"{i}. {track.get('name', 'Desconocida')} - {track.get('artist', 'Desconocido')}")
                        return f"Encontradas {len(tracks)} canciones en la playlist (de {total} total):\n" + "\n".join(track_list)
                    else:
                        return f"No se encontraron canciones en la playlist"
                else:
                    return f"Error obteniendo canciones de la playlist: {result.get('message', 'Error desconocido')}"
=======
                    return f"Error fetching playlist tracks: {result.get('message', 'Unknown error')}"
>>>>>>> 722939547f9251c7c92d98116d41467c5a817b1d
            
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
