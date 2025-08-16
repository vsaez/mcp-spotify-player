#!/usr/bin/env python3
"""
MCP server for Spotify Player using stdio
Implements the MCP protocol over JSON-RPC for communication with Cursor
"""

import json
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import platform

from mcp_logging import get_logger

import mcp_spotify_player

from mcp_spotify.auth.tokens import Tokens
from mcp_spotify.errors import InvalidTokenFileError, McpUserError
from mcp_spotify_player.client_auth import try_load_tokens
from mcp_spotify_player.config import Config, resolve_tokens_path
from mcp_spotify_player.mcp_manifest import MANIFEST
from mcp_spotify_player.spotify_controller import SpotifyController

# Configure logging
logger = get_logger(__name__)


class MCPServer:
    def __init__(self):
        self.config = Config()

        try:
            tokens = try_load_tokens()
            self.auth_status = "OK"
        except InvalidTokenFileError as e:
            logger.error(str(e))
            tokens = None
            self.auth_status = "INVALID_TOKEN_FILE"

        self.current_tokens: Optional[Tokens] = tokens

        def tokens_provider() -> Optional[Tokens]:
            if self.auth_status == "INVALID_TOKEN_FILE":
                raise InvalidTokenFileError(
                    "Token file is invalid. Fix tokens.json or run /auth to regenerate it."
                )
            return self.current_tokens

        self.controller = SpotifyController(tokens_provider)
        self.request_id = 0
        # MCP Manifest
        self.manifest = MANIFEST

        # Tool dispatch configuration
        self.TOOL_HANDLERS = {
            "play_music": self.controller.playback.play_music,
            "pause_music": self.controller.playback.pause_music,
            "skip_next": self.controller.playback.skip_next,
            "skip_previous": self.controller.playback.skip_previous,
            "set_volume": self.controller.playback.set_volume,
            "set_repeat": self.controller.playback.set_repeat,
            "get_current_playing": self.controller.playback.get_current_playing,
            "get_playback_state": self.controller.playback.get_playback_state,
            "get_devices": self.controller.playback.get_devices,
            "search_music": self.controller.playback.search_music,
            "search_collections": self.controller.playback.search_collections,
            "get_playlists": self.controller.playlists.get_playlists,
            "get_playlist_tracks": self.controller.playlists.get_playlist_tracks,
            "rename_playlist": self.controller.playlists.rename_playlist,
            "clear_playlist": self.controller.playlists.clear_playlist,
            "create_playlist": self.controller.playlists.create_playlist,
            "add_tracks_to_playlist": self.controller.playlists.add_tracks_to_playlist,
            "diagnose": self._diagnose,
            "queue_add": self.controller.playback.queue_add,
            "queue_list": self.controller.playback.queue_list,
        }

        # Optional validators and result formatters
        self.TOOL_VALIDATORS = {
            "set_volume": self._validate_set_volume,
            "set_repeat": self._validate_set_repeat,
            "search_music": self._validate_search_music,
            "search_collections": self._validate_search_collections,
            "get_playlist_tracks": self._validate_get_playlist_tracks,
            "rename_playlist": self._validate_rename_playlist,
            "clear_playlist": self._validate_clear_playlist,
            "create_playlist": self._validate_create_playlist,
            "add_tracks_to_playlist": self._validate_add_tracks_to_playlist,
            "queue_add": self._validate_queue_add,
            "queue_list": self._validate_queue_list,
        }

        self.RESULT_FORMATTERS = {
            "get_current_playing": self._format_get_current_playing,
            "get_playback_state": self._format_get_playback_state,
            "get_devices": self._format_json_result,
            "search_music": self._format_json_result,
            "search_collections": self._format_json_result,
            "get_playlists": self._format_json_result,
            "get_playlist_tracks": self._format_json_result,
            "queue_list": self._format_json_result,
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
            "error": {"code": code, "message": message},
        }
        self.send_response(error_response)

    def handle_initialize(self, request_id: Any, params: Dict[str, Any]):
        """Handle MCP client initialization"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                #"protocolVersion": "2025-06-18",
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "spotify-player", "version": "1.0.0"},
            },
        }
        self.send_response(response)

    def handle_tools_list(self, request_id: Any):
        """List available tools"""
        response = {"jsonrpc": "2.0", "id": request_id, "result": {"tools": self.manifest["tools"]}}
        self.send_response(response)

    def handle_tools_call(self, request_id: Any, params: Dict[str, Any]):
        """Execute a tool"""
        try:
            if "calls" in params:
                calls = params.get("calls", [])
            else:
                calls = [{"name": params.get("name"), "arguments": params.get("arguments", {})}]

            results = []
            for call in calls:
                tool_name = call.get("name")
                arguments = call.get("arguments", {})
                if not tool_name:
                    continue

                logger.info(f"Executing {tool_name} with arguments: {arguments}")
                try:
                    result = self.execute_tool(tool_name, arguments)
                    results.append(
                        {"name": tool_name, "content": [{"type": "text", "text": result}]}
                    )
                except McpUserError as exc:
                    logger.warning(f"User error executing {tool_name}: {exc}")
                    results.append(
                        {"name": tool_name, "content": [{"type": "text", "text": str(exc)}]}
                    )

            if len(results) == 1:
                response = {"jsonrpc": "2.0", "id": request_id, "result": results[0]}
            else:
                response = {"jsonrpc": "2.0", "id": request_id, "result": {"calls": results}}
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
            logger.info("AAAAAAAAAAAAAAA executing tool: %s with arguments: %s", tool_name, arguments)
            return formatter(result, arguments)

        except McpUserError:
            raise
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {str(e)}")
            return f"Error: {str(e)}"

    def _diagnose(self) -> str:
        path = resolve_tokens_path()
        lines: list[str] = [f"tokens_path: {path}"]
        try:
            tokens = try_load_tokens()
        except InvalidTokenFileError:
            tokens = None
            lines.append("tokens: invalid")
        if tokens:
            expires_dt = datetime.fromtimestamp(tokens.expires_at, tz=timezone.utc)
            minutes = int((tokens.expires_at - time.time()) / 60)
            lines.append(
                f"expires_at: {expires_dt.isoformat()} ({minutes} min)"
            )
            lines.append(
                f"refresh_token: {'yes' if tokens.refresh_token else 'no'}"
            )
            scopes = sorted(tokens.scopes)
            lines.append("scopes: " + (" ".join(scopes) if scopes else "none"))
            missing = sorted(set(Config.SPOTIFY_SCOPES) - tokens.scopes)
            lines.append(
                "missing_scopes: " + (" ".join(missing) if missing else "none")
            )
        elif "tokens: invalid" not in lines:
            lines.append("tokens: missing")

        lines.append(f"python: {platform.python_version()}")
        lines.append(f"package: {mcp_spotify_player.__version__}")
        return "\n".join(lines)

    # -----------------------
    # Validators
    # -----------------------
    def _validate_set_volume(self, arguments: Dict[str, Any]):
        if arguments.get("volume_percent") is None:
            raise ValueError("volume_percent is required")

    def _validate_set_repeat(self, arguments: Dict[str, Any]):
        state = arguments.get("state")
        if not state:
            raise ValueError("state is required")
        if state not in ["track", "context", "off"]:
            raise ValueError("state must be 'track', 'context', or 'off'")

    def _validate_search_music(self, arguments: Dict[str, Any]):
        if not arguments.get("query"):
            raise ValueError("query is required")

    def _validate_search_collections(self, arguments: Dict[str, Any]):
        if not arguments.get("q"):
            raise ValueError("q is required")
        collection_type = arguments.get("type")
        if collection_type not in ("playlist", "album"):
            raise ValueError("type must be 'playlist' or 'album'")
        limit = arguments.get("limit", 20)
        if not isinstance(limit, int) or limit < 1 or limit > 50:
            raise ValueError("limit must be between 1 and 50")
        offset = arguments.get("offset", 0)
        if not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be >= 0")
        arguments.setdefault("limit", limit)
        arguments.setdefault("offset", offset)

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

    def _validate_queue_add(self, args: dict) -> None:
        """Validate input for the queue_add tool."""
        if not args.get("uri"):
            raise ValueError("'uri' is required")
        # device_id is optional, no check needed

    def _validate_queue_list(self, arguments: Dict[str, Any]) -> None:
        # We only accept 'limit' (optional, integer >= 1)
        allowed = {"limit"}
        for k in arguments.keys():
            if k not in allowed:
                raise ValueError("queue_list only accepts 'limit'")
        if "limit" in arguments:
            try:
                limit = int(arguments["limit"])
            except Exception:
                raise ValueError("limit must be an integer")
            if limit < 1:
                raise ValueError("limit must be >= 1")

    # -----------------------
    # Result formatters
    # -----------------------
    def _default_formatter(self, result: Any, _arguments: Dict[str, Any]) -> str:
        if isinstance(result, dict):
            if result.get("success"):
                return result.get("message", "Success")
            return result.get("message", "Error")
        return str(result)

    def _format_get_current_playing(
        self, result: Dict[str, Any], _arguments: Dict[str, Any]
    ) -> str:
        if result.get("success"):
            track = result.get("track", {})
            is_playing = result.get("is_playing", False)
            if track:
                status = "Playing" if is_playing else "Paused"
                return (
                    f"{status}: {track.get('name', 'Unknown')} by {track.get('artist', 'Unknown')}"
                )
            return "No music is currently playing"
        return f"Could not retrieve information: {result.get('message', 'Unknown error')}"

    def _format_get_playback_state(self, result: Dict[str, Any], _arguments: Dict[str, Any]) -> str:
        if result.get("success"):
            state = result.get("state", {})
            current_track = state.get("current_track", {})
            is_playing = state.get("is_playing", False)
            volume = state.get("volume_percent", 0)
            device = state.get("device_name", "Unknown")
            if current_track:
                status = "Playing" if is_playing else "Paused"
                track_info = f"{current_track.get('name', 'Unknown')} - {current_track.get('artist', 'Unknown')}"
                return f"{status}: {track_info} | Volume: {volume}% | Device: {device}"
            return f"No music playing | Volume: {volume}% | Device: {device}"
        return f"Could not retrieve state: {result.get('message', 'Unknown error')}"

    def _format_json_result(self, result, _args):
        """
        Envuelve cualquier resultado en un sobre estándar y evita petar si el result
        no es serializable.
        """
        try:
            payload = {"success": True, "data": result}
            return json.dumps(payload, ensure_ascii=False)
        except Exception as e:
            logger.exception("Failed to serialize tool result for %s", _args)
            return json.dumps({"success": False, "message": str(e) or "Unknown error"})

    # def _format_json_result(self, result: Dict[str, Any], _arguments: Dict[str, Any]) -> str:
    #     logger.info(f"BBBBBBBBBBBBBBBB formatting result: {result}")
    #     if result.get("success"):
    #         return json.dumps(result)
    #     return json.dumps({"success": False, "message": result.get("message", "Unknown error")})

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
                            self.send_error(
                                request_id, -32601, f"Method '{method}' not implemented"
                            )
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
