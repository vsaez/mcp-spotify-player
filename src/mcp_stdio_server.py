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
from src.mcp_manifest import MANIFEST

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServer:
    def __init__(self):
        self.config = Config()
        self.controller = SpotifyController()
        self.request_id = 0
        # MCP Manifest
        self.manifest = MANIFEST

        # Tool dispatch configuration
        self.TOOL_HANDLERS = {
            "play_music": self.controller.play_music,
            "pause_music": self.controller.pause_music,
            "skip_next": self.controller.skip_next,
            "skip_previous": self.controller.skip_previous,
            "set_volume": self.controller.set_volume,
            "get_current_playing": self.controller.get_current_playing,
            "get_playback_state": self.controller.get_playback_state,
            "search_music": self.controller.search_music,
            "get_playlists": self.controller.get_playlists,
            "get_playlist_tracks": self.controller.get_playlist_tracks,
            "rename_playlist": self.controller.rename_playlist,
            "clear_playlist": self.controller.clear_playlist,
            "create_playlist": self.controller.create_playlist,
            "add_tracks_to_playlist": self.controller.add_tracks_to_playlist,
        }

        # Optional validators and result formatters
        self.TOOL_VALIDATORS = {
            "set_volume": self._validate_set_volume,
            "search_music": self._validate_search_music,
            "get_playlist_tracks": self._validate_get_playlist_tracks,
            "rename_playlist": self._validate_rename_playlist,
            "clear_playlist": self._validate_clear_playlist,
            "create_playlist": self._validate_create_playlist,
            "add_tracks_to_playlist": self._validate_add_tracks_to_playlist,
        }

        self.RESULT_FORMATTERS = {
            "get_current_playing": self._format_get_current_playing,
            "get_playback_state": self._format_get_playback_state,
            "search_music": self._format_json_result,
            "get_playlists": self._format_json_result,
            "get_playlist_tracks": self._format_json_result,
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
                                 "rename_playlist", "clear_playlist", "create_playlist", "add_tracks_to_playlist"]:

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
        """Execute a specific tool using dynamic dispatch"""
        try:
            handler = self.TOOL_HANDLERS.get(tool_name)
            if not handler:
                raise ValueError(f"Tool '{tool_name}' not supported")

            validator = self.TOOL_VALIDATORS.get(tool_name)
            if validator:
                validator(arguments)

            result = handler(**arguments)
            formatter = self.RESULT_FORMATTERS.get(tool_name, self._default_formatter)
            return formatter(result, arguments)

        except Exception as e:
            logger.error(f"Error executing {tool_name}: {str(e)}")
            return f"Error: {str(e)}"

    # -----------------------
    # Validators
    # -----------------------
    def _validate_set_volume(self, arguments: Dict[str, Any]):
        if arguments.get("volume_percent") is None:
            raise ValueError("volume_percent is required")

    def _validate_search_music(self, arguments: Dict[str, Any]):
        if not arguments.get("query"):
            raise ValueError("query is required")

    def _validate_get_playlist_tracks(self, arguments: Dict[str, Any]):
        playlist_id = arguments.get("playlist_id")
        if not playlist_id:
            raise ValueError("playlist_id is required")
        if playlist_id.isdigit() and len(playlist_id) < 10:
            raise ValueError(
                "The provided identifier appears to be a position number, not a valid Spotify ID. Spotify IDs are long alphanumeric codes."
            )

        # set default limit if not provided
        arguments.setdefault("limit", 20)

    def _validate_rename_playlist(self, arguments: Dict[str, Any]):
        if not arguments.get("playlist_id"):
            raise ValueError("playlist_id is required")

    def _validate_clear_playlist(self, arguments: Dict[str, Any]):
        if not arguments.get("playlist_id"):
            raise ValueError("playlist_id is required")

    def _validate_create_playlist(self, arguments: Dict[str, Any]):
        if not arguments.get("playlist_name"):
            raise ValueError("playlist_name is required")

    def _validate_add_tracks_to_playlist(self, arguments: Dict[str, Any]):
        if not arguments.get("playlist_id") or not arguments.get("track_uris"):
            raise ValueError("playlist_id and track_uris are required")

    # -----------------------
    # Result formatters
    # -----------------------
    def _default_formatter(self, result: Any, _arguments: Dict[str, Any]) -> str:
        if isinstance(result, dict):
            if result.get('success'):
                return result.get('message', 'Success')
            return result.get('message', 'Error')
        return str(result)

    def _format_get_current_playing(self, result: Dict[str, Any], _arguments: Dict[str, Any]) -> str:
        if result.get('success'):
            track = result.get('track', {})
            is_playing = result.get('is_playing', False)
            if track:
                status = "Playing" if is_playing else "Paused"
                return f"{status}: {track.get('name', 'Unknown')} by {track.get('artist', 'Unknown')}"
            return "No music is currently playing"
        return f"Could not retrieve information: {result.get('message', 'Unknown error')}"

    def _format_get_playback_state(self, result: Dict[str, Any], _arguments: Dict[str, Any]) -> str:
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
            return f"No music playing | Volume: {volume}% | Device: {device}"
        return f"Could not retrieve state: {result.get('message', 'Unknown error')}"

    def _format_json_result(self, result: Dict[str, Any], _arguments: Dict[str, Any]) -> str:
        if result.get('success'):
            return json.dumps(result)
        return json.dumps({
            "success": False,
            "message": result.get('message', 'Unknown error')
        })

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