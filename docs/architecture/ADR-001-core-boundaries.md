# ADR-001: Transport-agnostic core separation

- **Status**: Proposed
- **Date**: 2025-09-17

## Context

We must evolve the MCP Spotify player into a dual server (stdio + streamable HTTP) without duplicating business rules or control logic. The current code couples transport concerns (stdio framing, HTTP socket handling) with the MCP execution flow, making it difficult to enable new transports, test domain logic, and keep stable contracts with clients. Supporting two adapters simultaneously demands clear responsibility boundaries to avoid regressions between modes.

## Decision

We will define a **transport-agnostic core** that encapsulates MCP logic and Spotify business operations, delegating input/output and server lifecycle management to specific adapters (stdio and HTTP). The core will expose pure interfaces and already-deserialized MCP models so that it can be reused by any transport.

### Core responsibilities

- Register and describe MCP tools available to clients.
- Route and execute MCP calls against Spotify controllers without performing transport input/output.
- Perform minimal validation of already-deserialized MCP requests (required parameters, basic types, tool schemas).
- Build MCP success and error responses, normalizing shared metadata.
- Map Spotify domain errors to the typed MCP errors defined in the core taxonomy.

### Out of scope for the core (adapter responsibilities)

- Full management of I/O and framing (stdio, HTTP, headers, chunked encoding, sockets).
- Transport-level authentication (Bearer tokens), header `Origin`/CORS validation, and any channel-specific policy.
- Marshalling between bytes and JSON as well as orchestration of server lifecycle and network configuration.

### Allowed dependencies within the core

- Internal types and utilities that do not couple the core to any transport.
- Abstract interfaces to the Spotify client.
- No server frameworks, direct environment access, or dependencies with network side effects.

## Alternatives considered

1. **Transport-bound core**: keep the logic attached to the existing stdio model. Rejected because it prevents HTTP support without duplicating logic and triggers regressions across transports.
2. **Duplicated logic per transport**: build two complete pipelines (stdio and HTTP) with separate implementations. Rejected due to higher maintenance cost, behavioral inconsistencies, and increased error surface.
3. **Event-driven core with shared buses**: introduce an internal messaging framework. Rejected as over-engineering for the current scope and for introducing unnecessary dependencies.

## Consequences

- **Positive**: reusable and stable core contracts; easier testing of MCP logic without transport dependencies; alignment with the dual-transport strategy. Enables future adapters to iterate quickly.
- **Risks**: regressions if adapters do not faithfully replicate stdio framing; hidden coupling with the Spotify client; incorrect error mapping.

## Mitigations

- Define transport-specific contract test suites to validate framing and backward compatibility.
- Establish clear interfaces for the Spotify client and review them with the domain team before implementation.
- Document and automate the error taxonomy so that each adapter respects the codes and semantics defined by the core.
