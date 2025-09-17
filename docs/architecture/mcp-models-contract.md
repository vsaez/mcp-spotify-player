# MCP models contract

The transport determines framing and low-level serialization. The core models describe logical structures after JSON parsing.

## Core models

- `McpMessage`
  - `method: str`
  - `params: Dict[str, Any]` with schema validation handled before reaching the core.
- `ToolDefinition`
  - `name: str`
  - `description: str`
  - `input_schema: JsonSchema`
  - `output_schema: JsonSchema`
- `ToolCall`
  - `name: str`
  - `arguments: Dict[str, Any]`
- `McpResponse`
  - `Success`
    - `result: Any`
    - `meta: Optional[Dict[str, Any]]`
  - `Error`
    - `code: str`
    - `message: str`
    - `data: Optional[Dict[str, Any]]`

## Contract examples

Examples show logical payloads. Transports may embed them in frames or envelopes as needed.

### initialize

```json
{
  "id": "req-001",
  "method": "initialize",
  "params": {
    "client": {
      "name": "spotify-cli",
      "version": "1.4.0"
    },
    "capabilities": {
      "streaming": true,
      "max_chunk": 65536
    }
  }
}
```

### tools/list

```json
{
  "id": "req-105",
  "method": "tools/list",
  "params": {}
}
```

Sample response:

```json
{
  "id": "req-105",
  "result": {
    "tools": [
      {
        "name": "play",
        "description": "Start playback on the preferred device",
        "input_schema": {
          "type": "object",
          "required": ["uri"],
          "properties": {
            "uri": {
              "type": "string",
              "format": "spotify"
            },
            "start_position_ms": {
              "type": "integer",
              "minimum": 0
            }
          }
        },
        "output_schema": {
          "type": "object",
          "properties": {
            "playback_state": {
              "$ref": "#/definitions/PlaybackState"
            }
          }
        }
      }
    ]
  },
  "meta": {
    "generated_at": "2025-09-17T11:42:00Z"
  }
}
```

### tool.call (`play` example)

Request:

```json
{
  "id": "req-512",
  "method": "tool.call",
  "params": {
    "tool": "play",
    "arguments": {
      "uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
      "start_position_ms": 15000
    }
  }
}
```

Success response:

```json
{
  "id": "req-512",
  "result": {
    "playback_state": {
      "track_uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
      "is_playing": true,
      "position_ms": 15000,
      "device": "desktop-player"
    }
  },
  "meta": {
    "correlation_id": "corr-512",
    "duration_ms": 84
  }
}
```

Error response:

```json
{
  "id": "req-512",
  "error": {
    "code": "NotFound",
    "message": "Requested track or device is not available",
    "data": {
      "missing": "device",
      "schema": {
        "$ref": "#/definitions/DeviceUnavailable"
      }
    }
  }
}
```
