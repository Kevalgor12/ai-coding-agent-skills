# Socket.IO version changelog (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Condensed from
[research/technologies/socketio.md](../../../research/technologies/socketio.md)
§11–13 — consult that document for the full citation trail. All claims below
carry `[Source: <url>]` tags resolvable to `skill.yaml.source_references`.

## Feature-addition table (v4.x line)

| Version | Addition | Source |
|---|---|---|
| 4.0.0 (Mar 2021) | Full TypeScript rewrite; no protocol change from a client-compatibility standpoint | [Source: https://socket.io/docs/v4/changelog/] |
| 4.1.0 | `serverSideEmit()`; `InterServerEvents` typing generic | [Source: https://socket.io/docs/v4/changelog/, https://socket.io/docs/v4/typescript/] |
| 4.1.3 | Heartbeat direction changed to server-initiated pings (mitigates browser tab-throttling causing spurious disconnects) | [Source: https://socket.io/docs/v4/logging-and-debugging/, https://socket.io/docs/v4/troubleshooting-connection-issues/] |
| 4.4.0 | `SocketData` typing generic; µWebSockets.js binding support | [Source: https://socket.io/docs/v4/changelog/, https://socket.io/docs/v4/server-installation/] |
| 4.6.0 | `connectionStateRecovery` server option; `cleanupEmptyChildNamespaces`; `addTrailingSlash`; `io.engine.use()` for Express-style HTTP middleware | [Source: https://socket.io/docs/v4/changelog/, https://socket.io/docs/v4/server-options/, https://socket.io/docs/v4/middlewares/] |
| 4.7.0 | WebTransport support | [Source: https://socket.io/docs/v4/changelog/] |

No v5 docs tree exists as of the research date (2026-09-09); 4.x is the
current major version line, currently at 4.8.3 stable
[Source: https://socket.io/docs/v4/changelog/, https://registry.npmjs.org/socket.io].

## 3.x → 4.0 breaking changes (server-side only)

[Source: https://socket.io/docs/v4/migrating-from-3-x-to-4-0/]

1. `io.to()`/`io.in()` no longer mutate the shared `io`/`Namespace` instance —
   each call now returns an immutable broadcast operator. Code that called
   `io.to(room)` without immediately chaining `.emit()` and relied on the
   mutated state silently breaks on upgrade.
2. `wsEngine` must be passed as the actual server class/object (e.g.
   `require("eiows").Server`), not a string — avoids bundler issues.
3. `socket.to("room1").broadcast.emit()` is now invalid — redundant, since
   `.to()` already implies broadcast mode.

**v3 and v4 clients remain protocol-compatible with each other** — this
boundary is a server-side implementation/API change only, not a wire-protocol
break. An upgrade from a v3 server to a v4 server does not require
simultaneously upgrading every connected client.

## 2.x → 3.0 breaking changes

[Source: https://socket.io/docs/v4/migrating-from-2-x-to-3-0/]

- `maxHttpBufferSize` default reduced 100x: 100 MB → 1 MB.
- WebSocket `perMessageDeflate` compression disabled by default.
- CORS disabled by default (previously implicit-allow; now must be
  explicitly allow-listed).
- Cookies must be explicitly enabled rather than sent automatically.
- `io.set()`, `Socket.binary()`, `Socket.use()` removed.
- `Namespace.connected` (object) → `Namespace.sockets` (Map).
- `Socket.rooms` changed from object to `Set`.
- `Socket.join()`/`Socket.leave()` became synchronous (previously
  callback-based).
- Client auth split into a distinct `auth` option, separate from `query`.
- Connecting to a non-default namespace no longer implicitly connects the
  default namespace too.
- `error` event renamed `connect_error`.
- `Namespace.clients()` renamed `Namespace.allSockets()`, now returns a
  Promise.
- Package uses named imports (`import { Server } from "socket.io"`);
  external `@types` no longer needed (codebase rewritten in TypeScript).
- IE8 and Node.js 8 support dropped.

## Why this matters for an upgrade

A server upgrade spanning both boundaries (e.g. 2.x straight to 4.x) inherits
*both* breaking-change sets — the CORS-default flip and `maxHttpBufferSize`
cut from 2.x→3.0 are easy to miss when only the 3.x→4.0 notes are reviewed.
Audit for: (a) any `io.to()`/`io.in()` call not immediately chained with
`.emit()`, (b) any reliance on implicit CORS allow or a >1 MB payload
assumption, (c) any use of the removed 2.x APIs above.
[Source: https://socket.io/docs/v4/migrating-from-3-x-to-4-0/, https://socket.io/docs/v4/migrating-from-2-x-to-3-0/]
