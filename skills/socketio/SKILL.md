---
name: Socket.IO
description: >-
  Socket.IO-specific event-emitter API, namespaces/rooms, io.use()
  middleware, Engine.IO transport negotiation, multi-node adapters, and the
  v3→v4 upgrade boundary. Use when the stack has a socket.io/socket.io-client
  dependency or the task names Socket.IO, namespaces, or rooms. Not for raw
  WebSocket API code (use websocket-api) or an open realtime-transport choice
  (use realtime-communication).
spec_version: "1.0"
---

## Purpose & scope

Apply Socket.IO's own API and version specifics once Socket.IO is the chosen
transport: the event-emitter API, namespaces/rooms, the `io.use()` middleware
pattern, transport negotiation, and the v3→v4 upgrade boundary. The transport
*choice* itself (Socket.IO vs. raw WebSocket vs. WebRTC) and the generic
connection-lifecycle/scaling/handshake-auth framework belong to the parent
skill, [`realtime-communication`](../realtime-communication/SKILL.md)
(`SK-BE-004`) — not repeated here.

## When to use / When not to use

**Use** when a `socket.io`/`socket.io-client` dependency, import, or require
is present, or the task names Socket.IO, namespaces, rooms, `io.use()`
middleware, or a Socket.IO adapter. **Do not use** for raw WebSocket API code
with no Socket.IO dependency (route to `websocket-api`), for an open
realtime-transport choice (route to `realtime-communication`), or for WebRTC
peer-to-peer media/data with no Socket.IO involvement.

## Knowledge

- **Two-layer architecture.** Engine.IO is the low-level transport layer
  (HTTP long-polling, WebSocket, WebTransport, handshake, heartbeat);
  Socket.IO is built on top of it, adding reconnection, acknowledgements,
  broadcasting, and namespace/room multiplexing. Socket.IO is explicitly
  "not a raw WebSocket implementation." [Source: https://socket.io/docs/v4/how-it-works/]
- **Transport negotiation.** A client always starts with HTTP long-polling
  (for reliability), then attempts to upgrade to WebSocket (or WebTransport)
  once available; the handshake response carries the session ID, available
  upgrade options, heartbeat intervals, and payload size limits.
  [Source: https://socket.io/docs/v4/how-it-works/]
- **Namespaces** split application logic over one shared connection
  (multiplexing). The default namespace is `/`; `io.on("connection")` is
  equivalent to `io.of("/").on("connection")`. Dynamic namespaces can be
  created via a regex (`io.of(/^\/dynamic-\d+$/)`) or a validating function —
  prefer the function form when namespace creation depends on user identity,
  since open regex matching lets any client create a namespace and grow
  memory unbounded. [Source: https://socket.io/docs/v4/namespaces/]
- **Rooms** are an arbitrary, server-only channel concept for targeted
  broadcast — not part of the wire protocol, and clients have no API to query
  their own room membership. Always manage membership via `socket.join()`/
  `socket.leave()`, never by mutating the adapter's internal `rooms`/`sids`
  maps. Listen for `disconnecting` (fires before `disconnect`) if you need a
  socket's rooms at disconnect time. [Source: https://socket.io/docs/v4/rooms/]
- **Event-emitter API surface.** Server-side: `Server` (`emit()`, `to()`/
  `in()`/`except()`, `of()`, `use()`, `on("connection")`, `close()`,
  `fetchSockets()`, `socketsJoin()`/`socketsLeave()`, `.engine`); `Namespace`
  (own `emit()`/`to()`/`use()`/`disconnectSockets()`); `Socket` (`emit()`,
  `to()`/`in()`/`except()`, `join()`/`leave()`, `disconnect()`, `use()`, plus
  `broadcast`/`volatile`/`compress()` flags); `Engine` (`io.engine`, exposes
  `use()` for Express-style middleware, `handleUpgrade()`).
  [Source: https://socket.io/docs/v4/server-api/]
- **Client-side surface.** `io()` factory creates a `Socket` (`io.protocol`
  reports the protocol version); `Manager` owns the underlying Engine.IO
  connection and reconnection logic and can be shared by multiple `Socket`
  instances across namespaces; `Socket` exposes `connected`, `active`, `id`,
  `recovered`, and methods `connect()`/`disconnect()`, `emit()`,
  `emitWithAck()` (Promise-based ack), `on()`/`once()`/`off()`, `timeout()`.
  [Source: https://socket.io/docs/v4/client-api/]
- **Emit/broadcast/ack patterns:** `io.emit()` (all clients), `socket.emit()`
  (one client), ack via a callback arg or `socket.emitWithAck()`, bounded
  waits via `socket.timeout(ms).emit()`, room targeting (`io.to(room).emit()`
  / `io.except(room).emit()`), namespace targeting (`io.of("/ns").emit()`),
  and inter-server messaging via `io.serverSideEmit()` (added v4.1.0,
  optionally with an ack). Reserved event names (`connect`, `disconnect`,
  etc.) must not be reused as custom event names.
  [Source: https://socket.io/docs/v4/emit-cheatsheet/]
- **Middleware pattern.** `io.use((socket, next) => {...})` runs once per
  incoming connection; call `next()` to allow or `next(new Error(...))` to
  reject (client receives `connect_error`). [Version-sensitive: v4.6.0+]
  `io.engine.use()` additionally accepts Express-style HTTP middleware (e.g.
  `express-session`, `helmet`), running for all HTTP requests including the
  WebSocket upgrade request. [Source: https://socket.io/docs/v4/middlewares/]
- **v3→v4 boundary is server-side only.** The 3.x→4.0 breaking changes
  (immutable `io.to()`/`io.in()` broadcast operators, `wsEngine` option
  shape, invalid `socket.to().broadcast.emit()`) affect only server-side
  code; **v3 and v4 clients remain protocol-compatible with each other**
  [Version-sensitive: 3.x→4.0 boundary]. Full breaking-change enumeration
  (both 2.x→3.0 and 3.x→4.0) and the v4.x feature-addition table live in
  [references/version-changelog.md](references/version-changelog.md).
  [Source: https://socket.io/docs/v4/migrating-from-3-x-to-4-0/]
- **Version floors:** Node.js server package requires >=10 ("older versions
  are not supported anymore"); browser floor is IE9+ (IE6/7/8 explicitly
  unsupported). [Source: https://socket.io/docs/v4/server-installation/,
  https://socket.io/docs/v4/client-installation/]

## Decision framework

This assumes `realtime-communication` (SK-BE-004) has already selected
Socket.IO over raw WebSocket/WebRTC/SSE for the broad transport question.
The decisions below are internal to that choice:

1. **Is Socket.IO's added abstraction still earning its keep inside this
   feature, or did the app just default to it?** The concrete signal is
   whether the feature actually uses namespaces (multiplexed logical
   channels), rooms (targeted broadcast to a dynamic subset), acks/
   `emitWithAck()`, automatic reconnection with backoff, or packet buffering
   while disconnected — the specific things Socket.IO's docs cite as what
   you'd otherwise build yourself on raw WebSocket. If a feature uses none
   of these and talks to browser-only clients with an already-bounded
   message shape, it may be a candidate to reconsider under SK-BE-004's
   framework, not a reason to add Socket.IO-specific complexity here.
   [Source: https://socket.io/docs/v4/]
2. **Which multi-node adapter — Redis, MongoDB, or PostgreSQL?** All three
   are officially documented. If the only requirement is real-time fan-out
   across instances, Redis (pub+sub client pair, or sharded Pub/Sub on
   Redis 7.0+) is the simplest and most common choice. If the deployment
   also needs `connectionStateRecovery` (restoring socket id/rooms/data and
   missed packets after a brief disconnect), the plain Redis Pub/Sub adapter
   does **not** support it — MongoDB (and the Redis Streams adapter) do.
   Pick Redis by default for pure fan-out; escalate to MongoDB/Redis Streams
   only when session-recovery UX is an actual requirement, since it's a
   documented capability gap, not an oversight.
   [Source: https://socket.io/docs/v4/using-multiple-nodes/,
   https://socket.io/docs/v4/connection-state-recovery/]
3. **µWebSockets.js vs. the default `ws` engine?** Default `ws` (optionally
   sped up with the native `bufferutil`/`utf-8-validate` add-ons, falling
   back to pure JS if absent) is sufficient for most deployments.
   [Version-sensitive: v4.4.0+] Binding to `µWebSockets.js` is a documented,
   higher-throughput alternative engine worth adopting only once WebSocket
   frame throughput is an observed bottleneck, not preemptively; a
   `@socket.io/bun-engine` package exists for Bun-specific optimization.
   [Source: https://socket.io/docs/v4/server-installation/]

## Workflow

1. Confirm the Socket.IO major/minor version in use (or being targeted) —
   several options used below (`connectionStateRecovery`, `io.engine.use()`,
   `SocketData`, WebTransport) only exist from specific minor versions
   onward (see Knowledge).
2. Design namespaces (isolation by feature/tenant/admin-access) and rooms
   (targeted broadcast) before writing event handlers — retrofitting either
   is more disruptive than starting with them.
3. Implement `io.use()` auth middleware validating `socket.handshake.auth`/
   headers/cookies, rejecting via `next(new Error(...))` (see Security).
4. Set transport/engine config deliberately rather than accepting every
   default blind: `maxHttpBufferSize`, `perMessageDeflate`, `pingInterval`/
   `pingTimeout`, and the WS engine (`ws` vs. µWebSockets.js per the decision
   framework).
5. If the deployment runs multiple instances, pick the adapter (decision
   framework above) and wire it in; sticky-session configuration at the load
   balancer is the parent skill's concern, but the adapter choice and its
   Socket.IO-side setup is this skill's.
6. Write tests using the official pattern (see Testing) before shipping
   event handlers.
7. For production, ship the minified client bundle and, if Admin UI
   instrumentation is added, configure production auth (see Security/
   Performance).

## Engineering rules

- Always resolve `io.use()` middleware explicitly — call `next()` or
  `next(new Error(...))`; never leave a middleware without a terminal call.
  [Source: https://socket.io/docs/v4/middlewares/]
- Manage room membership only via `socket.join()`/`socket.leave()`; never
  mutate the adapter's internal `rooms`/`sids` maps directly.
  [Source: https://socket.io/docs/v4/rooms/]
- Validate dynamic namespaces with a function when namespace creation
  depends on user identity/permissions; open regex matching is a documented
  unbounded-resource-growth risk. [Source: https://socket.io/docs/v4/namespaces/]
- Reconcile `pingInterval + pingTimeout` (45s combined by default) with any
  reverse-proxy/load-balancer idle timeout before deploying — a shorter
  proxy timeout is a documented cause of spurious `transport close`
  disconnects. [Source: https://socket.io/docs/v4/troubleshooting-connection-issues/]
- On a 3.x→4.0 upgrade, audit every `io.to()`/`io.in()` call for reliance on
  the old mutate-in-place behavior — it now returns an immutable broadcast
  operator, and unchained calls silently stop working as they did before.
  [Source: https://socket.io/docs/v4/migrating-from-3-x-to-4-0/]
- Don't recommend `connectionStateRecovery`, `io.engine.use()`,
  `cleanupEmptyChildNamespaces`, or `addTrailingSlash` for a deployment on
  Socket.IO <4.6 — they don't exist there. [Version-sensitive: >=4.6.0]

## Trade-offs

Default `ws` engine is simpler to operate and sufficient for most workloads;
µWebSockets.js trades that simplicity for higher throughput, and should be
adopted only once `ws` is an observed bottleneck. The Redis adapter is the
simplest multi-node story (pure pub/sub, no persistence) but cannot provide
`connectionStateRecovery`; MongoDB/Redis Streams buy that capability at the
cost of a heavier, stateful adapter dependency.
[Source: https://socket.io/docs/v4/server-installation/,
https://socket.io/docs/v4/connection-state-recovery/]

## Anti-patterns

- **Disabling Admin UI auth in production** — the docs allow this only for
  development; production instrumentation requires bcrypt-hashed
  credentials with basic auth. [Source: https://socket.io/docs/v4/admin-ui/]
- **Relying on the Redis adapter for anything beyond real-time fan-out** —
  it uses Pub/Sub only, does not persist data, does not support
  `connectionStateRecovery`, and silently degrades broadcasts to
  local-server-only if Redis becomes unavailable (already flagged by the
  parent skill at a high level). If persistence or session-recovery
  guarantees are actually required, that's a signal to choose MongoDB/Redis
  Streams instead, not to keep Redis and hope.
  [Source: https://socket.io/docs/v4/redis-adapter/, https://socket.io/docs/v4/connection-state-recovery/]
- **Directly mutating the adapter's internal `rooms`/`sids` maps** instead of
  `join()`/`leave()`. [Source: https://socket.io/docs/v4/rooms/]
- **Open regex-based dynamic namespaces without validation** — lets any
  client create a namespace by connecting, an unbounded resource-growth
  risk. [Source: https://socket.io/docs/v4/namespaces/]
- **Carrying forward the pre-4.0 `socket.to("room1").broadcast.emit()`
  pattern** — invalid in v4.x since `.to()` already implies broadcast mode.
  [Version-sensitive: removed in v4.0] [Source: https://socket.io/docs/v4/migrating-from-3-x-to-4-0/]
- **Over-engineering trap:** switching to µWebSockets.js or a
  persistence-capable adapter (MongoDB/PostgreSQL) before measuring an
  actual throughput bottleneck or needing session-recovery UX — the default
  `ws` engine plus a Redis pub/sub adapter is sufficient for most
  deployments, and adopting the heavier option preemptively adds ops
  surface without a demonstrated need.

## Security

- **Middleware auth pattern (full):** implement `io.use((socket, next) =>
  {...})` reading `socket.handshake.auth`/headers/cookies, calling `next()`
  to allow or `next(new Error(...))` to reject. Credentials are sent
  client-side via the `auth` option (`io({ auth: { token: "abc" } })`).
  Because `auth` can be a function that gets **re-evaluated on every
  reconnect attempt**, the middleware must validate on every connect **and**
  reconnect — not just the initial handshake — or a revoked/expired
  credential keeps a reconnecting client authenticated indefinitely.
  [Source: https://socket.io/docs/v4/middlewares/]
- **Admin UI production auth is required**, not optional: disabling auth is
  documented as acceptable only for development; production instrumentation
  should use bcrypt-hashed credentials with basic auth.
  [Source: https://socket.io/docs/v4/admin-ui/]
- **CORS config surface** (the parent skill already covers that CORS only
  protects browser clients and only the long-polling transport): the
  concrete option shape is `cors: { origin, credentials, allowedHeaders,
  methods, maxAge }`, disabled/restricted by default since v3. A wildcard
  `origin: "*"` paired with client-side `withCredentials: true` does not
  work (browsers reject it); the server must set `credentials: true` if the
  client sets `withCredentials`. Use `allowRequest` as the additional
  server-side handshake check the docs recommend alongside CORS.
  [Source: https://socket.io/docs/v4/handling-cors/]
- `maxHttpBufferSize` (default 1 MB, tightened from 100 MB in 2.x) caps
  message size as a basic DoS/resource-exhaustion guard; exceeding it closes
  the socket rather than gracefully rejecting the oversized message at the
  application layer — size it deliberately per workload rather than raising
  it reflexively. [Source: https://socket.io/docs/v4/server-options/,
  https://socket.io/docs/v4/troubleshooting-connection-issues/]
- If using the Redis adapter, Redis must not be exposed to untrusted
  networks; ACLs and TLS are recommended for its pub/sub connections.
  [Source: https://socket.io/docs/v4/redis-adapter/]

## Performance

- **Bundle sizes:** unminified/debug build `socket.io.js` is 34.7 kB gzip;
  minified production build `socket.io.min.js` is 14.7 kB min+gzip; the
  msgpack-parser variant `socket.io.msgpack.min.js` is 15.3 kB min+gzip. Ship
  the minified build in production. [Source: https://socket.io/docs/v4/client-installation/]
- The `debug` package used for internal logging adds roughly 4 KB
  minified/gzipped; it's excluded from the "slim" browser build, and
  `webpack-remove-debug` is the documented way to strip it from a custom
  build. [Source: https://socket.io/docs/v4/logging-and-debugging/]
- **Engine choice as a throughput lever:** optional native add-ons
  `bufferutil`/`utf-8-validate` speed up WebSocket frame operations under
  the default `ws` engine (pure-JS fallback if absent). [Version-sensitive:
  v4.4.0+] Binding to µWebSockets.js is the documented higher-throughput
  alternative engine; `@socket.io/bun-engine` exists for Bun-specific
  optimization — reach for these only once `ws` is a measured bottleneck
  (see Decision framework). [Source: https://socket.io/docs/v4/server-installation/]

## Testing

The official testing guide (already noted at a high level by the parent
skill) is concrete: create a plain Node `http.Server`, attach a Socket.IO
`Server` to it, `listen()` on an ephemeral port, then connect a
`socket.io-client` instance (commonly aliased `ioc`) to
`http://localhost:${port}`; use lifecycle hooks (`beforeAll`/`after`, etc.)
to set up and tear down the server and disconnect the client between tests
to avoid cross-test interference. The same pattern is demonstrated across
Mocha (with Chai), Jest, Tape, and Vitest. For assertions: basic emit/receive
tests listen for a server-emitted event and assert the payload;
acknowledgement tests assert on the ack-callback payload or use
`emitWithAck()` for Promise-based ack testing; a documented `waitFor()`
helper reduces event/Promise boilerplate. Ensure the connection is fully
established before asserting. [Source: https://socket.io/docs/v4/testing/]
Deep test-strategy method is owned by
[testing-strategy](../testing-strategy/SKILL.md).

## Failure handling

- If the Socket.IO version in use cannot be determined, ask or explicitly
  state the version this guidance targets (>=4.6); never assume the latest
  release (4.8.x) silently.
- If shell is unavailable/denied, produce advisory code/config and state
  that install/build/test commands were not run.
- If the actual need is raw-WebSocket-only code, or the transport choice
  itself is still open, defer to `websocket-api` or `realtime-communication`
  respectively rather than assuming Socket.IO is the right fit.

## Escalation

- A version upgrade spanning both the 2.x→3.0 and 3.x→4.0 boundaries (or any
  future major) on a production system is presented with the full breaking-
  change list (see [references/version-changelog.md](references/version-changelog.md))
  for explicit confirmation before applying — not upgraded unilaterally.
- A mismatch between a stated requirement (e.g. "sessions must survive a
  brief disconnect") and the currently-configured adapter (Redis Pub/Sub,
  which doesn't support `connectionStateRecovery`) is flagged before
  shipping, not left for production to surface.

## Outputs & verification

- **Outputs:** namespace/room design and event handlers, `io.use()`
  middleware, client-side Manager/Socket configuration, multi-node adapter
  setup, and version-upgrade/engine-choice/Admin-UI-auth analysis.
- **Verify:** middleware auth runs on connect and reconnect; the chosen
  adapter's documented limitations are stated alongside the recommendation;
  every version-gated API used is tagged with the version it requires and
  checked against `covered_versions`; Admin UI instrumentation, if present,
  uses production auth.

## References

- [references/version-changelog.md](references/version-changelog.md) —
  Tier-2: full v2.x→v3.0 and v3.x→v4.0 breaking-change lists, and the v4.x
  feature-addition table.
- Source list: see `skill.yaml.source_references` (Socket.IO official docs,
  retrieved 2026-09-10, via `research/technologies/socketio.md`).
- Parent skill: [realtime-communication](../realtime-communication/SKILL.md)
  (`SK-BE-004`) — transport selection, connection-lifecycle/reconnection,
  horizontal-scaling, and handshake-auth framework.
- Version constraints: `research/knowledge-maps/version-matrix.md` — "Socket.IO" section.
