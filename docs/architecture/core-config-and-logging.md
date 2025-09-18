# Core configuration and logging

## CoreConfig contract

`CoreConfig` is injected by adapters with resolved values. It must include:

- `token_store_path`: filesystem or secret location managed outside the core.
- `required_scopes`: list of Spotify scopes the business operations need.
- `preferred_device`: optional logical device identifier for playback.
- `business_timeouts`: dictionary of operation → milliseconds.
- `default_locale`: locale code used when the request context omits it.

Adapters are responsible for reading environment variables, feature flags, or configuration files. The core receives sanitized values and must not access process environment or CLI flags directly.

## Logging policy

Structured logging is mandatory. Minimum fields:

| Field | Description |
| --- | --- |
| `timestamp` | ISO-8601 instant provided by the logger implementation. |
| `level` | Severity (`info`, `warn`, `error`, etc.). |
| `area` | Logical subsystem (e.g., `core.dispatcher`, `core.spotify`). |
| `message` | Short event description. |
| `correlation_id` | Propagated from `ExecutionContext`. |
| `tool_name` | Present for tool invocations; empty otherwise. |
| `duration_ms` | Execution time in milliseconds when relevant. |

The core must never write to stdout/stderr directly. All logging goes through the injected logger, which adapts to each transport’s observability stack.
