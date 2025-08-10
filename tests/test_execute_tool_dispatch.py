import pytest
from src.mcp_stdio_server import MCPServer

class DummyController:
    def pause_music(self):
        return {"success": True, "message": "Playback paused"}

    def set_volume(self, volume_percent):
        return {"success": True, "message": f"Volume set to {volume_percent}%"}


def test_dispatch_calls_correct_handler():
    server = MCPServer()
    server.controller = DummyController()
    server.TOOL_HANDLERS["pause_music"] = server.controller.pause_music
    result = server.execute_tool("pause_music", {})
    assert result == "Playback paused"


def test_validation_errors_are_raised():
    server = MCPServer()
    server.controller = DummyController()
    server.TOOL_HANDLERS["set_volume"] = server.controller.set_volume
    result = server.execute_tool("set_volume", {})
    assert "volume_percent is required" in result


def test_unknown_tool():
    server = MCPServer()
    result = server.execute_tool("unknown_tool", {})
    assert "Tool 'unknown_tool' not supported" in result
