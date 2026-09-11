# Socket.IO — Technology Research

Research date: 2026-09-09. Primary source: `socket.io` (the canonical official Socket.IO documentation host, at `https://socket.io/docs/v4/`) — confirmed current at time of research; no indication in search results or fetched pages that the documentation host has moved. Secondary official sources: `github.com/socketio/socket.io` and related `socketio/*` GitHub repos (source, releases, changelog), `registry.npmjs.org/socket.io` (npm registry metadata, used only to corroborate version/release-date facts, not as a documentation citation). Citation convention: `[Source: <url>] <claim>.` for documented facts, `[Inference, not confirmed in docs]` for reasoning not explicitly stated in the cited page, and "Not documented / could not verify" where no official source was found. `Unresolved:` flags items with conflicting or uncertain information.

**Documentation host note**: [Source: https://socket.io/docs/v4/] The current docs are versioned under `/docs/v4/`; a `v3` reference tree also still resolves at `socket.io/docs/v3/server-api/` for legacy lookups, but the actively maintained/linked documentation is the v4 tree. [Source: https://socket.io/docs/v4/changelog/] Socket.IO v2 was released May 2017 and v3 was released November 2020; the docs state Socket.IO 3.x is no longer actively maintained, and v4.0 (March 2021) is described as a full TypeScript rewrite. No v5 docs tree was found during this research; **4.x is the current major version line** as of the research date.

---

## 1. Core concepts

[Source: https://socket.io/docs/v4/] Socket.IO is described as "a library that enables low-latency, bidirectional and event-based communication between a client and a server." It is explicitly **not** a raw WebSocket implementation — it is a protocol/framework layer built on top of transports, one of which is WebSocket.

[Source: https://socket.io/docs/v4/] Socket.IO establishes connections through multiple transport options: HTTP long-polling, WebSocket, and WebTransport, automatically selecting the best available option based on browser/environment capabilities and network conditions.

[Source: https://socket.io/docs/v4/] Core built-in features listed by the docs: HTTP long-polling fallback (graceful degradation when WebSocket is unavailable), automatic reconnection (heartbeat mechanism + exponential back-off), packet buffering (queues messages sent while disconnected), acknowledgements (request/response pattern with timeout support), broadcasting (to all clients or a subset), and multiplexing via namespaces.

[Source: https://socket.io/docs/v4/] The docs frame Socket.IO's value proposition as providing battle-tested implementations of features (reconnection, acknowledgements, broadcasting, multiplexing) that developers would otherwise have to build themselves on top of raw WebSockets; the added protocol overhead is described as "a few additional bytes for each message."

[Source: https://socket.io/docs/v4/rooms/] A **room** is "an arbitrary channel that sockets can join and leave" — a server-only grouping concept used for targeted broadcasting, not part of the underlying protocol itself.

[Source: https://socket.io/docs/v4/namespaces/] A **namespace** is a communication channel that allows splitting application logic over a single shared connection; the default namespace is `/`, and `io.on("connection")` is equivalent to `io.of("/").on("connection")`.

## 2. Architecture

[Source: https://socket.io/docs/v4/how-it-works/] Socket.IO is architecturally two-layered: **Engine.IO** is the low-level transport layer (handles the actual connection: HTTP long-polling, WebSocket, WebTransport, handshake, heartbeat/PING-PONG), and **Socket.IO** is the higher-level layer built on top of it, adding reconnection, acknowledgements, broadcasting, and namespace/room multiplexing.

[Source: https://socket.io/docs/v4/how-it-works/] Three Engine.IO transports are documented: (1) **HTTP long-polling** — successive GET/POST requests, broadly compatible but higher header overhead/lower performance, used as the initial connection method for reliability; (2) **WebSocket** — persistent bidirectional connection, preferred when available, with (per the fetched page) ~99.84% browser support cited as of early 2026; (3) **WebTransport** — newest transport, described as "the most efficient transport, especially in environments prone to packet loss," with limited availability.

[Source: https://socket.io/docs/v4/how-it-works/] Connection sequence: the client starts with HTTP long-polling, then attempts to upgrade to a better transport (e.g. WebSocket). During the handshake, the server sends a session ID, available upgrade options, heartbeat (ping) intervals, and payload size limits. A PING/PONG heartbeat mechanism detects dead connections.

[Source: https://socket.io/docs/v4/logging-and-debugging/, https://socket.io/docs/v4/troubleshooting-connection-issues/] [Version-sensitive: v4.1.3+] As of Socket.IO v4.1.3, the heartbeat mechanism direction was changed (server-initiated pings) to mitigate browser tab-throttling issues that could otherwise cause spurious disconnects when a tab loses focus.

[Source: https://socket.io/docs/v4/namespaces/] Namespaces provide isolated event handlers, rooms, and middlewares within a single underlying transport connection (multiplexing); dynamic namespaces can be created via regular expressions (e.g. `io.of(/^\/dynamic-\d+$/)`) or a validating function, with existing namespaces taking priority over dynamic ones.

[Source: https://socket.io/docs/v4/rooms/] Rooms exist per-server-process by default; in a multi-server deployment, an **adapter** (e.g. Redis) is required to broadcast across the set of rooms/sockets distributed over multiple server instances — the in-memory default adapter only knows about sockets connected to its own process.

[Source: https://socket.io/docs/v4/using-multiple-nodes/] For horizontal scaling, the documented architecture requires (a) sticky sessions / session affinity at the load balancer so all requests for a given Engine.IO session route to the same server process, plus (b) a shared adapter (Redis, MongoDB, PostgreSQL, Cluster adapter, Google Cloud Pub/Sub, AWS SQS, or Azure Service Bus) so broadcasts issued on one server instance reach clients connected to other instances via pub/sub-style message forwarding.

[Source: https://socket.io/docs/v4/socket-io-protocol/] The Socket.IO protocol is built on top of the Engine.IO protocol; the two protocols are versioned independently. [Source: https://socket.io/docs/v4/client-api/] The client API page shows `io.protocol` as a property reporting the Socket.IO protocol version currently in use (reported as version 5 for the current client/server line).

## 3. APIs

### Server API
[Source: https://socket.io/docs/v4/server-api/] Main server-side classes:
- **`Server`** — top-level class constructed as `new Server(httpServer, options)`; manages connections/namespaces. Key methods: `emit()` (broadcast to main namespace), `to(room)`/`in(room)` (target rooms), `except(rooms)` (exclude rooms), `of(nsp)` (create/retrieve a namespace), `use(fn)` (register middleware), `on("connection", cb)`, `close()`, `fetchSockets()` (retrieve sockets, cluster-aware), `socketsJoin()`/`socketsLeave()` (bulk room ops), and an `.engine` property exposing the underlying Engine.IO server.
- **`Namespace`** — pool of sockets scoped to a pathname (e.g. `/chat`); supports its own `emit()`, `to()`/`in()`/`except()`, `use()` (namespace-scoped middleware), `disconnectSockets()`, `fetchSockets()`, `socketsJoin()`/`socketsLeave()`.
- **`Socket`** — represents one client connection server-side; `emit()` (to that client), `to()`/`in()`/`except()` (broadcast excluding sender), `join()`/`leave()` (room membership), `on()`, `disconnect()`, `use()` (socket-scoped middleware). Flags: `broadcast` (send to all but sender), `volatile` (may be dropped if the client isn't ready to receive), `compress()`.
- **`Engine`** (`io.engine`) — low-level transport server; `use()` accepts Express-style middleware (v4.6.0+, see Section 5); `handleUpgrade()`; emits a `connection_error` event and a `headers` event for customizing response headers.

### Client API
[Source: https://socket.io/docs/v4/client-api/] Main client-side surfaces:
- **`io()`** factory function — creates a `Socket`, called with a URL and options (defaults to current host). `io.protocol` reports the protocol version in use.
- **`Manager`** — manages the underlying Engine.IO connection and reconnection logic; multiple `Socket` instances (different namespaces) can share one `Manager` (multiplexing). Methods: `manager.open()`/`manager.connect()`, `manager.reconnection(value)`, `manager.reconnectionAttempts()`, `manager.reconnectionDelay()`, `manager.socket(nsp, options)`. Events: `error`, `ping`, `reconnect`, `reconnect_attempt`, `reconnect_error`, `reconnect_failed`.
- **`Socket`** — EventEmitter-based primary client interface. Properties: `socket.connected`, `socket.active` (whether it will auto-reconnect), `socket.id` (ephemeral session id), `socket.io` (reference to the Manager), `socket.recovered` (connection-state-recovery outcome). Methods: `connect()`/`open()`, `disconnect()`/`close()`, `emit(eventName, ...args, ack)`, `emitWithAck()` (Promise-based ack), `on()`, `once()`, `off()`, `timeout(value)` (ack timeout), `compress(value)`. Events: `connect`, `connect_error`, `disconnect`.

### Emit patterns
[Source: https://socket.io/docs/v4/emit-cheatsheet/] Documented emit patterns: `io.emit()` (all connected clients), `socket.emit()` (single client), acknowledgements via a callback argument or `socket.emitWithAck()` (Promise-based), `socket.timeout(ms).emit()`/`socket.timeout(ms).emitWithAck()` (bounded wait for an ack), room targeting via `io.to(room).emit()` / `io.except(room).emit()`, namespace-scoped emission via `io.of("/namespace").emit()`, and inter-server messaging via `io.serverSideEmit()` (optionally with an ack). The cheatsheet also flags reserved event names (`connect`, `disconnect`, etc.) that must not be used as custom event names.

### Protocol
[Source: https://socket.io/docs/v4/socket-io-protocol/] The Socket.IO protocol specification page documents the wire-level packet types and framing, built atop the Engine.IO protocol, for anyone implementing a custom client/server rather than using the reference implementations. Not documented / could not verify: full byte-level detail was not extracted in this research pass — the protocol spec page itself is the authoritative reference for implementers.

## 4. Configuration

### Server options
[Source: https://socket.io/docs/v4/server-options/] Socket.IO-level server options (with documented defaults):
- `adapter` — default in-memory adapter (`socket.io-adapter`); swap for Redis/etc. to scale across processes.
- `cleanupEmptyChildNamespaces` — default `false` [Version-sensitive: added v4.6.0] — auto-removes dynamic namespaces once empty.
- `connectionStateRecovery` — default `undefined` [Version-sensitive: added v4.6.0] — enables session/state recovery; sub-options `maxDisconnectionDuration`, `skipMiddlewares`.
- `connectTimeout` — default `45000` ms — time allowed for a client to join a namespace before being disconnected.
- `parser` — default `socket.io-parser`.
- `path` — default `/socket.io/`.
- `serveClient` — default `true` — serves the bundled client library.

Low-level Engine.IO options (also set via the Socket.IO `Server` constructor): `addTrailingSlash` (default `true`, added v4.6.0), `allowEIO3` (default `false` — enables backward compatibility with Socket.IO v2 clients/Engine.IO v3 protocol), `allowRequest` (validate handshake before accept), `allowUpgrades` (default `true`), `cookie` (default off; configurable `domain`/`httpOnly`/`maxAge`/`sameSite`/`secure`), `cors` (default off — origin/methods/credentials/headers), `httpCompression` (default `true`, for long-polling), `maxHttpBufferSize` (default `1e6`, 1 MB), `perMessageDeflate` (default `false`, WebSocket compression), `pingInterval` (default `25000` ms), `pingTimeout` (default `20000` ms), `transports` (default `["polling", "websocket"]`), `upgradeTimeout` (default `10000` ms), `wsEngine` (default `require("ws").Server`).

### Client options
[Source: https://socket.io/docs/v4/client-options/] IO factory options: `forceNew` (default `false`), `multiplex` (default `true`).

Low-level Engine options: `addTrailingSlash` (default `true`), `autoUnref` (default `false`), `closeOnBeforeunload` (default `false`), `extraHeaders` (ignored for browser WebSocket-only transport), `forceBase64` (default `false`), `path` (default `/socket.io/`, must match server), `protocols` (WebSocket sub-protocols), `query`, `rememberUpgrade` (default `false`), `timestampParam`/`timestampRequests` (cache-busting, default `true`), `transportOptions`, `transports` (default `["polling", "websocket", "webtransport"]`), `tryAllTransports` (default `false`), `upgrade` (default `true`), `withCredentials` (default `false`).

Manager options: `autoConnect` (default `true`), `parser`, `randomizationFactor` (default `0.5`), `reconnection` (default `true`), `reconnectionAttempts` (default `Infinity`), `reconnectionDelay` (default `1000`), `reconnectionDelayMax` (default `5000`), `timeout` (default `20000`).

Socket options: `ackTimeout` (must pair with `retries`), `auth` (object or function, sent at handshake/reconnect), `retries` (max resend attempts, must pair with `ackTimeout`).

## 5. Recommended patterns

[Source: https://socket.io/docs/v4/middlewares/] Server-side auth/validation is implemented via `io.use((socket, next) => {...})` middlewares run once per incoming connection; must call `next()` to allow, or `next(new Error(...))` to reject (client receives a `connect_error`). Credentials should be sent from the client via the `auth` option (`io({ auth: { token: "abc" } })`), read server-side as `socket.handshake.auth`.

[Source: https://socket.io/docs/v4/middlewares/] [Version-sensitive: v4.6.0+] Express-style HTTP middleware (e.g. `express-session`, `helmet`) can be attached via `io.engine.use()`, which runs for all HTTP requests including the WebSocket upgrade request — documented as the recommended way to reuse existing Express middleware with Socket.IO.

[Source: https://socket.io/docs/v4/namespaces/] Recommended use cases for namespaces: access restriction (e.g., an admin-only namespace gated by middleware) and multi-tenant isolation (per-tenant namespace). Function-based dynamic namespace validation is recommended over open regex matching when namespace creation depends on user identity/permissions, for security reasons.

[Source: https://socket.io/docs/v4/rooms/] Always manage room membership through `socket.join()`/`socket.leave()` rather than mutating the adapter's internal `rooms`/`sids` maps directly. Listen for the `disconnecting` event (fired before `disconnect`) if you need to know which rooms a socket was in at the moment of disconnection.

[Source: https://socket.io/docs/v4/using-multiple-nodes/] For any multi-process/multi-server deployment, configure sticky sessions at the load balancer (documented example configs given for nginx, Apache HTTPD, HAProxy, Traefik, Kubernetes/nginx Ingress, and the Node.js `cluster` module via `@socket.io/sticky`) and install a shared adapter.

[Source: https://socket.io/docs/v4/typescript/] [Version-sensitive: first-class TypeScript support since v3] Recommended pattern for typed events: define `ServerToClientEvents`, `ClientToServerEvents`, `InterServerEvents` (added v4.1.0), and `SocketData` (added v4.4.0) interfaces, and pass them as generics to `new Server<C2S, S2C, ISE, SocketData>()` server-side and `Socket<S2C, C2S>` client-side (note the argument order is reversed between server and client, reflecting each side's perspective).

[Source: https://socket.io/docs/v4/admin-ui/] For operational visibility, the officially maintained Admin UI (`@socket.io/admin-ui`, instrumented via `instrument(io, options)`) is the documented tool for inspecting connected servers/clients, socket handshake data, room membership, and live event traffic, plus admin actions like forcing a socket to join/leave a room or disconnecting it.

## 6. Anti-patterns

[Source: https://socket.io/docs/v4/rooms/] Directly mutating the adapter's internal `rooms`/`sids` maps instead of using `join()`/`leave()` is called out as something that should never be done.

[Source: https://socket.io/docs/v4/using-multiple-nodes/] Running multiple Socket.IO server processes behind a load balancer **without** sticky sessions is a documented failure mode: HTTP long-polling clients whose successive requests land on different processes will break, because "all requests associated with a particular session ID" must reach the process that originated them; the docs explicitly reject synchronizing session state across servers as an alternative, citing "a big performance hit."

[Source: https://socket.io/docs/v4/troubleshooting-connection-issues/] Leaving a reverse proxy's default idle/read timeout below `pingInterval + pingTimeout` (45s combined by default) is a documented cause of spurious `transport close` disconnects — proxy timeouts must be configured longer than that window.

[Source: https://socket.io/docs/v4/namespaces/] Using open regex-based dynamic namespaces without validation is flagged as risky: "any client to create a new namespace by connecting," which can lead to unbounded resource/memory growth; function-based validation is the documented mitigation.

[Source: https://socket.io/docs/v4/migrating-from-3-x-to-4-0/] [Version-sensitive: pre-4.0 API, removed in v4.0] Prior to v4.0, calling `io.to()` mutated the shared `io` instance rather than returning an immutable broadcast operator, which the docs describe as a source of "surprising behaviors" when the return value wasn't immediately chained with `.emit()`. The related pattern `socket.to("room1").broadcast.emit()` is now invalid in v4.x because `to()` already implies broadcast mode.

[Source: https://socket.io/docs/v4/redis-adapter/] Relying on the Redis adapter for anything beyond real-time fan-out is a documented anti-pattern: "the Redis adapter uses the Pub/Sub mechanism to forward the packets," it does not persist data, and if Redis becomes unavailable, broadcasts silently degrade to reaching only clients connected to the local server.

## 7. Security

[Source: https://socket.io/docs/v4/handling-cors/] CORS must be explicitly configured (`cors: { origin, credentials, allowedHeaders, methods, maxAge }`) — [Version-sensitive: since v3] CORS is disabled/restricted by default and there is no implicit "allow same host" behavior assumed. Two limitations are explicitly called out: "CORS only applies to browsers" (server-to-server or script clients bypass it entirely) and "CORS only applies to HTTP long-polling" (WebSocket connections are not subject to CORS at all) — so CORS configuration alone is not a sufficient access-control mechanism; `allowRequest` is recommended for additional server-side validation.

[Source: https://socket.io/docs/v4/handling-cors/] Common misconfiguration warnings: pairing a wildcard `origin: "*"` with `withCredentials: true` client-side does not work (browsers reject wildcard origin + credentials); the server must also set `credentials: true` if the client sets `withCredentials`.

[Source: https://socket.io/docs/v4/middlewares/] Authentication/authorization is expected to be implemented as connection middleware (`io.use()`) validating `socket.handshake.auth`/headers/cookies at connect time and on every reconnect attempt (since the `auth` option can be a function re-evaluated per attempt), rejecting via `next(new Error(...))`.

[Source: https://socket.io/docs/v4/redis-adapter/] When using the Redis adapter, the docs state "Redis should therefore not be exposed to untrusted networks" and recommend Redis ACLs and TLS for the adapter's pub/sub connections.

[Source: https://socket.io/docs/v4/admin-ui/] The Admin UI requires authentication; the docs explicitly allow disabling auth only for development, and recommend bcrypt-hashed credentials with basic auth for production instrumentation. The hosted `admin.socket.io` UI itself is described as static with no data collection (it connects directly, browser-to-server, once pointed at a deployment).

[Source: https://socket.io/docs/v4/server-options/] `maxHttpBufferSize` (default 1 MB) acts as a basic DoS/resource-exhaustion guard on message size; [Source: https://socket.io/docs/v4/migrating-from-2-x-to-3-0/] this default was deliberately tightened from 100 MB (in 2.x) down to 1 MB starting in 3.0, alongside disabling WebSocket compression (`perMessageDeflate`) by default — both framed in the migration guide as safer-by-default changes.

## 8. Performance

[Source: https://socket.io/docs/v4/client-installation/] Documented client bundle sizes: `socket.io.js` (unminified, includes debug) 34.7 kB gzip; `socket.io.min.js` (production, minified) 14.7 kB min+gzip; `socket.io.msgpack.min.js` (msgpack parser variant) 15.3 kB min+gzip. The docs recommend the minified production bundle to exclude the `debug` dependency from shipped code.

[Source: https://socket.io/docs/v4/logging-and-debugging/] The `debug` package used for internal logging adds roughly 4 KB minified/gzipped to bundles; it's excluded from the "slim" browser build, and `webpack-remove-debug` is suggested for stripping it from custom builds.

[Source: https://socket.io/docs/v4/server-installation/] Optional native add-ons `bufferutil` and `utf-8-validate` can be installed to speed up WebSocket frame operations under the default `ws` engine; Socket.IO falls back to pure-JS implementations if they're absent. [Version-sensitive: v4.4.0+] Binding to `µWebSockets.js` is supported as an alternative, higher-throughput WebSocket engine; a `@socket.io/bun-engine` package exists for Bun-specific optimization.

[Source: https://socket.io/docs/v4/how-it-works/] Transport choice is itself a performance lever: WebSocket has materially lower per-message overhead than HTTP long-polling (which repeats HTTP headers per request); WebTransport is documented as the most efficient option "especially in environments prone to packet loss," though availability is limited.

[Source: https://socket.io/docs/v4/emit-cheatsheet/] The `volatile` flag (`socket.volatile.emit()`) is the documented mechanism for performance-sensitive, loss-tolerant messages (e.g. frequent state updates) — packets may be dropped if the client isn't ready to receive, trading reliability for reduced buffering/backpressure.

[Source: https://socket.io/docs/v4/server-options/] `perMessageDeflate` (WebSocket permessage-deflate compression) defaults to `false`, and `httpCompression` (long-polling) defaults to `true` — i.e., compression is not uniformly on by default, an explicit tradeoff between CPU cost and bandwidth documented as configurable per deployment.

Not documented / could not verify: the official docs fetched in this research did not surface a dedicated benchmarks page or specific "max concurrent connections per server" numbers; any such figures would be environment-dependent and were not found stated as an official guarantee.

## 9. Testing

[Source: https://socket.io/docs/v4/testing/] The official testing guide demonstrates the same test pattern across four frameworks: **Mocha** (with Chai), **Jest**, **Tape**, and **Vitest**, in CommonJS, ES module, and TypeScript variants.

[Source: https://socket.io/docs/v4/testing/] Documented setup pattern: create a plain Node `http.Server`, attach a Socket.IO `Server` to it, `listen()` on an ephemeral port, then create a `socket.io-client` connection (`ioc`) to `http://localhost:${port}`; lifecycle hooks (`beforeAll`/`after`, etc.) handle setup/teardown of the server and disconnecting the client.

[Source: https://socket.io/docs/v4/testing/] Documented patterns: basic emit/receive assertions (client listens for a server-emitted event and asserts the payload), acknowledgement testing (assert on ack-callback payloads), Promise-based ack testing via `emitWithAck()`, and a `waitFor()` helper utility to reduce Promise/event boilerplate in tests.

[Source: https://socket.io/docs/v4/testing/] The guide stresses ensuring connections are fully established before assertions run and performing proper teardown (closing the server, disconnecting the client) to avoid cross-test interference.

## 10. Deployment

[Source: https://socket.io/docs/v4/reverse-proxy/] Deploying behind a reverse proxy requires forwarding the WebSocket `Upgrade`/`Connection` headers and using HTTP/1.1; example nginx directives given: `proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";`. Documented reverse proxies with worked examples: nginx (including multi-backend load-balancing config), Apache HTTPD (`mod_proxy_wstunnel`), Node.js `http-proxy` (with the `ws` option enabled), Caddy 2, and Google Cloud Load Balancer.

[Source: https://socket.io/docs/v4/reverse-proxy/] Critical timeout note: the proxy's read/idle timeout (e.g. nginx `proxy_read_timeout`, default 60s) must exceed Socket.IO's `pingInterval + pingTimeout` (45s combined by default), or the proxy will forcibly close idle-looking connections that are actually still alive, surfacing as a `transport close` error client-side. The same guidance is given for Google Cloud Load Balancer backend service timeouts.

[Source: https://socket.io/docs/v4/using-multiple-nodes/] Multi-instance/production deployment requires sticky sessions (documented configs for nginx, Apache, HAProxy, Traefik, Kubernetes nginx-ingress, and `@socket.io/sticky` for Node's `cluster` module) plus a shared adapter (Redis, MongoDB, PostgreSQL, Cluster adapter, Google Cloud Pub/Sub, AWS SQS, Azure Service Bus) so broadcasts propagate across processes/nodes.

[Source: https://socket.io/docs/v4/redis-adapter/] Redis adapter install: `npm install @socket.io/redis-adapter`; requires two Redis clients (pub + sub, the sub typically `pubClient.duplicate()`), supports the `redis` or `ioredis` packages, and sharded Pub/Sub as an alternative topology [Version-sensitive: sharded Pub/Sub requires Redis 7.0+].

[Source: https://socket.io/docs/v4/server-installation/] [Version-sensitive] Minimum supported Node.js version for the server package is Node.js 10 ("older versions are not supported anymore"); the docs recommend targeting the current LTS release as a baseline rather than the bare minimum.

## 11. Migration

[Source: https://socket.io/docs/v4/migrating-from-3-x-to-4-0/] **3.x → 4.0** documented breaking changes (server-side only; protocol-compatible with v3 clients): (1) `io.to()`/`io.in()` no longer mutate the shared `io`/`Namespace` instance — each call now returns an immutable broadcast operator, enabling safe chaining; (2) `wsEngine` must now be passed as the actual server class/object (e.g. `require("eiows").Server`) rather than a string, to avoid bundler issues; (3) `socket.to("room1").broadcast.emit()` is now invalid — redundant since `.to()` already implies broadcast mode. The guide explicitly notes v3 and v4 clients remain protocol-compatible with each other.

[Source: https://socket.io/docs/v4/migrating-from-2-x-to-3-0/] **2.x → 3.0** documented breaking changes: `maxHttpBufferSize` default reduced from 100 MB to 1 MB; WebSocket `perMessageDeflate` compression disabled by default; CORS disabled by default (must be explicitly allow-listed, replacing 2.x's implicit-allow behavior); cookies must be explicitly enabled rather than sent automatically; `io.set()`, `Socket.binary()`, and `Socket.use()` removed; `Namespace.connected` (object) replaced by `Namespace.sockets` (Map); `Socket.rooms` changed from object to Set; `Socket.join()`/`Socket.leave()` became synchronous (previously callback-based); client auth split into a distinct `auth` option separate from the `query` option; connecting to a non-default namespace no longer implicitly connects the default namespace too; `error` event renamed `connect_error`; `Namespace.clients()` renamed `Namespace.allSockets()` and now returns a Promise; package now uses named imports (`import { Server } from "socket.io"`); codebase rewritten in TypeScript (external `@types` no longer needed); IE8 and Node.js 8 support dropped.

[Source: https://socket.io/docs/v4/troubleshooting-connection-issues/] Client/server protocol-version mismatches surface as an "Unsupported protocol version" (Engine.IO error code 5); the docs point to compatibility tables per client platform (JavaScript, Java, Swift) against server version as the way to resolve version-skew issues, rather than a general "migrate from X" narrative — i.e. the official migration content is scoped to major-version-to-major-version guides (2.x→3.0, 3.x→4.0), not to migrating from other libraries (e.g. raw `ws`, SockJS). Not documented / could not verify: no official "migrating from a different real-time library" guide was found.

## 12. Version information

[Source: https://socket.io/docs/v4/changelog/, https://registry.npmjs.org/socket.io] The current stable `socket.io` (server) release is **4.8.3**, corroborated as the npm `latest` dist-tag; the official changelog page lists 4.8.3 and 4.8.2 with a December 23/22, 2025 date grouping, and 4.8.1 (Oct 25, 2024) and 4.8.0 (Sep 21, 2024) before that. Unresolved: an earlier web search summary reported the npm registry showing 4.8.3 "last published 8 months ago" (relative to a 2026-09-09 research date, implying roughly January 2026), which is inconsistent with the changelog page's December 23, 2025 date for the same version; the discrepancy is minor (weeks) and likely reflects either a republish/deprecation-metadata update or a rounding artifact in the relative-time display — flagged rather than resolved, since neither source's raw timestamp was directly confirmed byte-for-byte in this pass.

[Source: https://socket.io/docs/v4/changelog/] Major version milestones per the official changelog: 4.0.0 (March 2021) — full TypeScript rewrite, no protocol change from a client compatibility standpoint per the 3.x→4.0 migration guide; 4.1.0 — `serverSideEmit()`; 4.4.0 — µWebSockets.js integration; 4.6.0 — connection state recovery; 4.7.0 — WebTransport support.

[Source: https://github.com/socketio/socket.io/releases] Sub-packages (published separately from the core `socket.io` package, standard for this monorepo-style multi-package project) have newer patch releases than 4.8.3 itself as of the research date — e.g. `@socket.io/cluster-engine@0.1.1` (Sep 8, 2026), `engine.io@6.6.10` (Sep 3, 2026), `socket.io-parser@3.3.6`/`4.2.7` (Jul 2026), `socket.io-adapter@2.5.8`/`2.5.7` (Jun/May 2026), `engine.io@6.6.9`/`6.6.8` and `engine.io-client@6.6.6` (May–Jun 2026, largely `ws` dependency/CVE bumps).

Not documented / could not verify: no explicit LTS/support-window policy (e.g. "version N.x supported until date Y") was found on the official docs or changelog pages fetched in this research — Socket.IO does not appear to publish a formal LTS schedule the way some runtimes do; the only explicit maintenance signal found is the changelog's note that 3.x is "no longer actively maintained," implying only the current major (4.x) receives active fixes.

## 13. Breaking changes

[Source: https://socket.io/docs/v4/migrating-from-3-x-to-4-0/] See Section 11 for the full enumerated list. Summary of the most consequential v3→v4 breaks: immutable `io.to()`/broadcast operators (silent-behavior-change risk for code relying on the old mutation semantics), `wsEngine` option shape change (object instead of string).

[Source: https://socket.io/docs/v4/migrating-from-2-x-to-3-0/] See Section 11 for the full enumerated list. Summary of the most consequential v2→v3 breaks: CORS default flipped from open to closed (silent connection failures for un-migrated cross-origin clients), `maxHttpBufferSize` default cut 100x (100 MB → 1 MB, can silently start rejecting previously-accepted large payloads), and several data-structure/API renames (`Namespace.connected`→`Namespace.sockets`, `error`→`connect_error`, `Namespace.clients()`→`Namespace.allSockets()` now async).

[Source: https://github.com/socketio/socket.io/releases] Recent (2026) sub-package releases were predominantly security/dependency patches (e.g. `ws` bumped for CVE-2026-48779 and CVE-2026-45736 across `engine.io`, `engine.io-client`, and `socket.io-adapter`) and bug fixes (e.g. binary-packet validation fixes in `socket.io-parser` 3.3.6/4.2.7, protocol-mismatch session rejection and Node 10 compatibility restoration in `engine.io` 6.6.10) rather than API-breaking changes — no new major version (5.0) release or its associated breaking-changes/migration guide was found during this research.

## 14. Limitations

[Source: https://socket.io/docs/v4/rooms/] "Rooms are a server-only concept" — clients have no API to query which rooms they are currently in; that state must be tracked/communicated by the application if the client needs it.

[Source: https://socket.io/docs/v4/handling-cors/] CORS protections apply only to browser clients and only to the HTTP long-polling transport — they provide no protection against non-browser clients or against WebSocket connections, so CORS cannot be relied on as a complete access-control layer.

[Source: https://socket.io/docs/v4/connection-state-recovery/] Connection state recovery is explicitly not guaranteed: "the recovery will not always be successful." It is bounded by a configurable `maxDisconnectionDuration` window, and it is adapter-dependent — the documented example states the plain Redis Pub/Sub adapter does not support it, while MongoDB and Redis Streams adapters do.

[Source: https://socket.io/docs/v4/redis-adapter/] The Redis adapter provides no message persistence or delivery guarantee beyond best-effort pub/sub fan-out; if Redis is down, cross-server broadcast silently degrades to local-server-only delivery (no queuing/replay).

[Source: https://socket.io/docs/v4/server-options/] `maxHttpBufferSize` (default 1 MB) caps message size; exceeding it, per the troubleshooting page, causes the socket to be closed rather than the oversized message being fragmented or rejected gracefully at the application layer.

[Source: https://socket.io/docs/v4/client-installation/] Browser support floor: "IE9 and above" — IE6/7/8 are explicitly unsupported.

[Source: https://socket.io/docs/v4/server-installation/] Server-side Node.js floor is Node.js 10; older Node versions are unsupported.

## 15. Debugging

[Source: https://socket.io/docs/v4/logging-and-debugging/] Socket.IO uses the `debug` npm package for internal instrumentation, silent by default. Server-side: set the `DEBUG` environment variable, e.g. `DEBUG=socket.io* node yourfile.js`, `DEBUG=* node yourfile.js` (everything), `DEBUG=socket.io:client*` (client-side-only scope), or `DEBUG=engine,socket.io*` (both Engine.IO and Socket.IO scopes). Browser-side: set `localStorage.debug = '*'` in the devtools console, then reload.

[Source: https://socket.io/docs/v4/logging-and-debugging/] The docs explicitly note that certain browser-surfaced errors (e.g. connection-refused messages, CORS errors) "are not emitted by the Socket.IO library but by the browser itself," and are therefore outside what Socket.IO's own debug logging can control or suppress.

[Source: https://socket.io/docs/v4/admin-ui/] The **Admin UI** (`@socket.io/admin-ui`, instrumented via `instrument(io, opts)`) is the documented higher-level debugging/monitoring tool: it shows connected servers/clients, per-socket handshake and transport data, room membership, and a live log of every event sent/received, plus supports admin actions (force room join/leave, force-disconnect a socket). Compatible with Socket.IO v4 servers and v3.1.0+ servers.

[Source: https://socket.io/docs/v4/troubleshooting-connection-issues/] The troubleshooting guide catalogs specific error signatures and root causes: CORS/"Cross-Origin Request Blocked" (missing/misconfigured `cors` option or unreachable server), "Unsupported protocol version" / Engine.IO error code 5 (client/server version mismatch), path mismatch (client/server `path` option must match, default `/socket.io/`), proxy-timeout-induced disconnects (see Sections 9–10), oversized-payload or slow-payload disconnects (`maxHttpBufferSize` / `pingTimeout` interplay), "Session ID unknown" / error code 1 (missing sticky sessions in a load-balanced deployment), and `TRANSPORT_MISMATCH` (proxy not forwarding WebSocket upgrade headers correctly).

## 16. Integration

[Source: https://socket.io/docs/v4/middlewares/] [Version-sensitive: v4.6.0+] Express-compatible HTTP middleware integrates via `io.engine.use()`, explicitly documented as working with libraries like `express-session` and `helmet`.

[Source: https://socket.io/docs/v4/redis-adapter/] Redis integration via `@socket.io/redis-adapter`, using either the `redis` or `ioredis` client packages, for cross-process broadcast in scaled deployments (see Sections 2, 10).

[Source: https://socket.io/docs/v4/using-multiple-nodes/] Additional officially documented adapters beyond Redis for multi-node deployments: MongoDB, PostgreSQL, a dedicated Cluster adapter (for single-machine multi-process via Node's `cluster`), Google Cloud Pub/Sub, AWS SQS, and Azure Service Bus.

[Source: https://socket.io/docs/v4/server-installation/] Alternative WebSocket-engine integrations: `eiows` (native `ws`-compatible alternative) via `wsEngine`; [Version-sensitive: v4.4.0+] `µWebSockets.js` binding for higher throughput; `@socket.io/bun-engine` for the Bun runtime.

[Source: https://socket.io/docs/v4/typescript/] First-class TypeScript integration (typed events, see Section 5) [Version-sensitive: since v3, extended in v4.1.0 with `InterServerEvents` and v4.4.0 with `SocketData`].

[Source: https://socket.io/docs/v4/admin-ui/] Integrates with the hosted `admin.socket.io` static UI (or a self-hosted instance) for operational monitoring, gated behind server-side auth configuration.

[Source: https://socket.io/docs/v4/reverse-proxy/] Documented integration with reverse proxies/load balancers/ingress controllers: nginx, Apache HTTPD, Node `http-proxy`, Caddy 2, Google Cloud Load Balancer, plus Kubernetes nginx-ingress and Traefik sticky-session configuration in the multiple-nodes guide.

## 17. Production considerations

[Source: https://socket.io/docs/v4/using-multiple-nodes/, https://socket.io/docs/v4/reverse-proxy/] Any production deployment beyond a single process requires: sticky sessions at the load balancer AND a shared adapter (Redis or other supported backend) for cross-instance broadcast — both are documented as necessary, not optional, once more than one server process is involved. Reverse-proxy/load-balancer idle timeouts must be configured above `pingInterval + pingTimeout` (45s combined default) to avoid spurious disconnects.

[Source: https://socket.io/docs/v4/handling-cors/] Production CORS configuration should use explicit origin allow-lists (not wildcards, especially when `credentials`/`withCredentials` are in play) and `allowRequest` for any additional server-side handshake validation beyond CORS.

[Source: https://socket.io/docs/v4/redis-adapter/] When running the Redis adapter in production, Redis must not be exposed to untrusted networks; ACLs and TLS are recommended for the pub/sub connection. Redis downtime degrades broadcasts to local-server-only rather than failing the whole system, which is a documented resilience characteristic to plan around (broadcasts don't queue/replay once Redis returns).

[Source: https://socket.io/docs/v4/connection-state-recovery/] For production UX around reconnects, `connectionStateRecovery` can restore socket id/rooms/data and missed packets within a bounded `maxDisconnectionDuration`, but the docs are explicit that recovery is not always successful — applications should not assume it as a guaranteed data-consistency mechanism and must still handle full-resync paths.

[Source: https://socket.io/docs/v4/admin-ui/] Production Admin UI instrumentation should use authenticated access (bcrypt-hashed credentials over basic auth), not the "disable auth" development shortcut.

[Source: https://socket.io/docs/v4/client-installation/] Production client bundles should use the minified build (`socket.io.min.js`) rather than the debug-inclusive default build, both for size (14.7 kB vs 34.7 kB gzip) and to avoid shipping the `debug` package's console output to end users.

[Source: https://socket.io/docs/v4/server-options/] Production tuning knobs worth reviewing against defaults: `maxHttpBufferSize` (1 MB default — raise if legitimately larger payloads are expected, but this trades off DoS surface), `perMessageDeflate` (off by default — CPU/bandwidth tradeoff for WebSocket compression), `pingInterval`/`pingTimeout` (heartbeat cadence, must be reconciled with any intermediary proxy timeout as above).

---

## Summary of sources cited

- https://socket.io/docs/v4/ — introduction, core concepts, feature list
- https://socket.io/docs/v4/how-it-works/ — architecture (Engine.IO vs Socket.IO, transports, handshake)
- https://socket.io/docs/v4/rooms/ — rooms API and caveats
- https://socket.io/docs/v4/namespaces/ — namespaces, dynamic namespaces
- https://socket.io/docs/v4/middlewares/ — server middleware, auth, Express integration
- https://socket.io/docs/v4/using-multiple-nodes/ — scaling, sticky sessions, adapters
- https://socket.io/docs/v4/redis-adapter/ — Redis adapter setup/limitations
- https://socket.io/docs/v4/logging-and-debugging/ — debug logging (DEBUG env var, localStorage.debug)
- https://socket.io/docs/v4/admin-ui/ — Admin UI monitoring/debugging tool
- https://socket.io/docs/v4/server-api/ — server-side API reference
- https://socket.io/docs/v4/client-api/ — client-side API reference
- https://socket.io/docs/v4/emit-cheatsheet/ — emit/broadcast/ack patterns
- https://socket.io/docs/v4/server-options/ — server configuration reference
- https://socket.io/docs/v4/client-options/ — client configuration reference
- https://socket.io/docs/v4/typescript/ — TypeScript typing patterns
- https://socket.io/docs/v4/testing/ — official testing guide (Mocha/Jest/Tape/Vitest)
- https://socket.io/docs/v4/reverse-proxy/ — reverse proxy / load balancer deployment configs
- https://socket.io/docs/v4/server-installation/ — server install, Node.js version requirements
- https://socket.io/docs/v4/client-installation/ — client install, CDN, bundle sizes, browser support
- https://socket.io/docs/v4/handling-cors/ — CORS configuration and limitations
- https://socket.io/docs/v4/connection-state-recovery/ — connection state recovery feature and limits
- https://socket.io/docs/v4/troubleshooting-connection-issues/ — documented error catalog
- https://socket.io/docs/v4/migrating-from-3-x-to-4-0/ — 3.x→4.0 breaking changes
- https://socket.io/docs/v4/migrating-from-2-x-to-3-0/ — 2.x→3.0 breaking changes
- https://socket.io/docs/v4/changelog/ — version history / major milestones
- https://socket.io/docs/v4/socket-io-protocol/ — wire protocol reference
- https://github.com/socketio/socket.io/releases — GitHub releases (recent patch/security releases)
- https://registry.npmjs.org/socket.io — npm registry metadata (version corroboration only, not used as a documentation citation)
