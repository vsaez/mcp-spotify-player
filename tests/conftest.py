import json
import time
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _tokens_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "tokens.json"
    data = {
        "access_token": "test-token",
        "refresh_token": "test-refresh",
        "expires_at": int(time.time()) + 3600,
    }
    path.write_text(json.dumps(data))
    monkeypatch.setenv("MCP_SPOTIFY_TOKENS_PATH", str(path))
    yield
