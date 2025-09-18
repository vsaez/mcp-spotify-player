# MCP core interfaces

The core operates on already-deserialized MCP models and assumes no transport detail. All interfaces are stable contracts for adapters (stdio, HTTP) and domain providers (Spotify).

## ToolRegistry

Manager of tools exposed by the MCP server.

- `register(tool: ToolDefinition) -> None`: adds or updates an available tool.
- `unregister(name: str) -> None`: removes an existing tool.
- `list() -> List[ToolDefinition]`: returns the full registered definitions.
- `describe(name: str) -> ToolDefinition | None`: fetches the definition of a specific tool.

Requirements:
- In-memory or pluggable persistence with no access to transport layers.
- Validate unique name, input schema, and description before registering.

## Dispatcher

Primary orchestrator of MCP calls.

- `dispatch(request: McpMessage, ctx: ExecutionContext) -> McpResponse`

Expected behavior:
- Select the appropriate operation (initialize, tools/list, tool.call, etc.).
- Invoke `ToolRegistry` and Spotify controllers when needed.
- Propagate `correlation_id` to logs and responses.
- Always return an `McpResponse` instance (success or typed error).

## ExecutionContext

Operational context associated with every request.

Mandatory fields:
- `request_id: str`
- `correlation_id: str`
- `time_budget_ms: int`
- `locale: str`

Optional fields:
- `user: Optional[UserIdentity]` (abstract identifier resolved by the adapter).

Notes:
- The context is immutable for the core; any extension must be documented via new fields.
- Adapters resolve timeouts and cancellations, notifying the core if operations must be aborted.

## SpotifyController (port)

Abstract interface that encapsulates domain operations against Spotify. Adapters provide concrete implementations that comply with authentication and transport policies.

High-level operations (typed inputs and outputs):
- `play(target: PlayTarget, options: PlayOptions) -> PlaybackState`
- `pause() -> PlaybackState`
- `queue(item: QueueItem) -> QueueState`
- `search(query: SearchQuery) -> SearchResults`
- `list_playlists(owner: OwnerRef, page: PageRequest) -> PlaylistPage`

Characteristics:
- The core never manages tokens or network retries directly.
- Types such as `PlayTarget`, `PlayOptions`, `PlaybackState`, etc. are transport-independent domain models.

## Abstract logger

The core relies on an injected logger with the following operations:

- `info(event: str, fields: Dict[str, Any]) -> None`
- `warn(event: str, fields: Dict[str, Any]) -> None`
- `error(event: str, fields: Dict[str, Any]) -> None`

Rules:
- `fields` must include `correlation_id` when available.
- The core performs no string formatting; only key/value pairs are passed through.
- The logger does not write directly to process stdout/stderr; adapters decide the sink (files, observability, etc.).
