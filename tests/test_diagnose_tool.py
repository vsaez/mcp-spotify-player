import json
from datetime import datetime, timezone

from mcp_spotify_player.mcp_stdio_server import MCPServer


def test_diagnose_output(tmp_path, monkeypatch):
    tokens_path = tmp_path / "tokens.json"
    expires_at = 4600
    data = {
        "access_token": "a",
        "refresh_token": "b",
        "expires_at": expires_at,
        "scopes": ["user-read-playback-state"],
    }
    tokens_path.write_text(json.dumps(data))
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(tokens_path))
    monkeypatch.setattr("time.time", lambda: 1000)

    server = MCPServer()
    result = server.execute_tool("diagnose", {})
    lines = result.splitlines()

    assert lines[0] == f"tokens_path: {tokens_path.resolve()}"
    expected_iso = datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat()
    assert f"expires_at: {expected_iso} (60 min)" in lines[1]
    assert "refresh_token: yes" in lines[2]
    assert "scopes: user-read-playback-state" in lines[3]
    missing_line = lines[4]
    assert missing_line.startswith("missing_scopes:")
    assert "user-modify-playback-state" in missing_line
    assert any(l.startswith("python: ") for l in lines)
    assert any(l.startswith("package: ") for l in lines)
