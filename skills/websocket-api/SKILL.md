---
name: WebSocket API
description: >-
  WebSocket-API-specific implementation: opening handshake mechanics,
  Sec-WebSocket-* headers, subprotocol/extension negotiation, close codes,
  and the browser WebSocket/WebSocketStream vs. Node.js WebSocket client API
  surface. Use once WebSocket is the chosen transport (see
  realtime-communication for that choice) and implementation-level detail is
  needed. Not for choosing between WebSocket/Socket.IO/WebRTC, or generic
  connection/scaling/auth design.
spec_version: "1.0"
---

## Purpose & scope

Implement the WebSocket API correctly once WebSocket is the chosen
transport: RFC 6455 handshake mechanics, the `Sec-WebSocket-*` headers,
subprotocol/extension negotiation, close codes, and the browser
`WebSocket`/`WebSocketStream` vs. Node.js `WebSocket` client API surface.
Transport *selection* (WebSocket vs. Socket.IO vs. WebRTC vs. SSE) and the
generic connection-lifecycle/scaling/handshake-auth method belong to the
parent skill, [realtime-communication](../realtime-communication/SKILL.md)
(`SK-BE-004`) — not repeated here.

## When to use / When not to use

**Use** once WebSocket has already been selected as the transport and the
task needs implementation-level detail: handshake handling, close-code
logic, subprotocol negotiation, or the client/server API surface. **Do not
use** to choose between WebSocket/Socket.IO/WebRTC/SSE (route to
`SK-BE-004`), for generic connection-lifecycle/scaling/handshake-auth design
(route to `SK-BE-004`), or for Socket.IO-specific API usage — rooms,
namespaces, acknowledgements (route to `SK-TECH-socketio`).

## Knowledge

**Handshake.** The client sends a `GET` with `Upgrade: websocket`,
`Connection: Upgrade`, a random 16-byte base64 `Sec-WebSocket-Key`, and
`Sec-WebSocket-Version: 13`; the server must answer `101 Switching
Protocols` with `Sec-WebSocket-Accept` computed as
`base64(SHA-1(key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))`, proving it is
WebSocket-aware rather than echoing an arbitrary Upgrade
[Source: https://www.rfc-editor.org/rfc/rfc6455.html]. The WHATWG Living
Standard now delegates this handshake to the Fetch standard (so CSP,
cookies, and HSTS apply uniformly) instead of restating RFC 6455 §4
verbatim for browsers — the wire bytes stay RFC-6455-compatible, but RFC
6455 remains authoritative for non-browser (server/library) implementations
[Source: https://websockets.spec.whatwg.org/]. Full header table →
[references/protocol-details.md](references/protocol-details.md).

**Subprotocol/extension negotiation.** `Sec-WebSocket-Protocol` and
`Sec-WebSocket-Extensions` are client-side "offers"; a server may only
select a protocol/extension the client actually offered
[Source: https://www.rfc-editor.org/rfc/rfc6455.html]. In the JS API,
offered subprotocols are the `WebSocket()` constructor's second argument;
the server's selection surfaces on the read-only `.protocol` property
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket].

**Close codes.** `CloseEvent` exposes `code`/`reason`/`wasClean`. Codes 1005
(No Status Received), 1006 (Abnormal Closure), and 1015 (TLS handshake) are
explicitly documented as never actually sent on the wire — they're the
local API's way of reporting "no real close frame arrived," so a handler
seeing `1006` is diagnosing a client-observed abnormal disconnect, not a
code the remote peer chose to send
[Source: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code].
Full registry → references.

**Node.js gap** *(applies to all Node.js versions; client global
specifically: introduced v21.0.0, backported to v20.10.0, behind
`--experimental-websocket`; flag removed v22.0.0; stable as of v22.4.0)*.
Node ships a global, browser-compatible `WebSocket` **client** — but **no
built-in WebSocket server at all**; a server implementation (e.g. the `ws`
npm package) is still required
[Source: https://nodejs.org/api/globals.html].

**`http(s)` URL normalization** *(applies to engines implementing the
change dated May 2023; older engines may only accept `ws`/`wss` literally)*.
`new WebSocket(url)` accepts `ws`, `wss`, `http`, or `https`, auto-
normalizing `http(s)` to `ws(s)`
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket].

**No JS-level ping/pong.** Ping/pong (opcodes `0x9`/`0xA`) is a
protocol-level heartbeat handled by the underlying implementation, not
exposed as a JS method — browser-script heartbeats must be ordinary
application-level messages
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket]
[Source: https://www.rfc-editor.org/rfc/rfc6455.html].

## Decision framework

1. **Raw WebSocket API vs. reaching for a library.** The base API has no
   official unit/integration test framework, mocking library, or
   conformance suite for consumers, and no built-in backpressure
   [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API].
   If the app needs testable/mockable connection handling or
   backpressure-safe streaming without hand-rolling it, that documented gap
   is a real reason to reach for a library (see `SK-TECH-socketio`,
   related) — not a default. A small, well-bounded message shape that's
   fine with manual/integration testing often doesn't need one.
2. **Node.js native client vs. a server package (`ws`, etc.).** Node's
   global `WebSocket` (stable v22.4.0+) is sufficient for *outbound client*
   connections once the runtime meets that floor. For a WebSocket *server*
   on any Node.js version — Node ships none built-in — a server library is
   required, not optional [Source: nodejs.org/api/globals.html].
3. **`permessage-deflate` or not.** It trades CPU/complexity for smaller
   payloads, but RFC 7692 explicitly flags a CRIME-style compression-oracle
   risk when compressing attacker-influenced content mixed with secret data
   over TLS — enable it deliberately, not by default
   [Source: https://www.rfc-editor.org/rfc/rfc7692.html].
4. **`WebSocketStream` vs. `bufferedAmount` polling.** `WebSocketStream`
   closes the backpressure gap but is experimental/non-standard,
   implemented in only one rendering engine; for production code today,
   manual `bufferedAmount` monitoring is the supported path, not
   `WebSocketStream`
   [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocketStream].

Transport selection itself (WebSocket vs. Socket.IO vs. WebRTC) is not
re-decided here — see `SK-BE-004`.

## Workflow

1. Confirm the runtime target (browser client, Node.js client, or server) —
   it determines which API surface applies (see Knowledge).
2. Server-side: validate handshake headers, reject malformed/unsupported
   requests with `400` (echoing supported versions in the response header
   on a `Sec-WebSocket-Version` mismatch), enforce client-must-mask, and
   negotiate subprotocol/extensions only from what the client offered
   [Source: MDN Writing WebSocket servers] [Source: RFC 6455].
3. Client-side: use `addEventListener()` for `open`/`message`/`error`/
   `close` rather than only `on*` properties, so multiple listeners can
   coexist [Source: MDN Writing WebSocket client applications].
4. Implement close-code handling that distinguishes locally-synthesized
   codes (1005/1006/1015) from remote-sent ones.
5. If flow control matters, monitor `bufferedAmount` before sending more
   data (see Performance).
6. Since there's no official test framework for consumers, plan manual or
   integration tests against a real/in-process server rather than assuming
   a mocking library exists (see Testing).

## Engineering rules

- Validate `Sec-WebSocket-Version` and required handshake headers
  server-side; respond `400` and close immediately on anything malformed
  [Source: MDN Writing WebSocket servers].
- Enforce client-must-mask / server-must-not-mask; disconnect clients
  sending unmasked frames — an RFC 6455 §5.1 security requirement, not a
  style choice [Source: RFC 6455].
- Only select subprotocols/extensions the client actually offered
  [Source: RFC 6455].
- Treat `send()` as fire-and-forget: it throws only when `readyState` is
  `CONNECTING`, and silently drops data once `CLOSING`/`CLOSED` — never
  treat a successful call as delivery confirmation
  [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/send].
- Close on `pagehide` and reopen on `pageshow` (`event.persisted`) in
  browser clients, to avoid blocking bfcache and leaking idle server-side
  connections [Source: MDN Writing WebSocket client applications].
- On Node.js, don't assume a WebSocket server exists just because the
  client global does — it doesn't; pick a server library deliberately
  [Source: nodejs.org/api/globals.html].

## Trade-offs

Raw WebSocket keeps the dependency footprint minimal and matches the wire
protocol exactly, but leaves reconnection, message acknowledgement, and
backpressure entirely to hand-rolled application code, with no official
testing story to lean on. `permessage-deflate` reduces bandwidth at the cost
of CPU and a documented compression-oracle risk over TLS with secret
data — worth it for large, non-secret-heavy payloads, questionable for
small or highly sensitive ones.

## Anti-patterns

- Assuming `wss://` alone satisfies RFC 6455's masking requirement —
  masking is a distinct, TLS-independent wire-level control mandated even
  over `wss`; not enforcing it server-side breaks a security-motivated
  protocol rule, not a style guideline [Source: RFC 6455].
- Relying on `connect-src 'self'` in CSP to cover WebSocket connections — it
  does not reliably resolve to `ws:`/`wss:` schemes across browsers; list
  the WebSocket scheme/origin explicitly
  [Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/connect-src].
- Assuming Node.js ships a WebSocket server because it ships a WebSocket
  client — it doesn't; the client global is outbound-connection-only
  [Source: nodejs.org/api/globals.html].
- Treating a successful `send()` call as delivery confirmation — it's
  fire-and-forget by design [Source: MDN WebSocket/send].
- **Over-engineering trap:** reaching for `WebSocketStream` or a full
  client library in production before plain `bufferedAmount` monitoring has
  even been tried — `WebSocketStream` is experimental and one-engine-only
  today [Source: MDN WebSocketStream].
- Writing `http(s)://` URLs into `new WebSocket()` and assuming universal
  acceptance — the auto-normalization only landed with the May 2023 spec
  change; older/other engines may reject it [Source: version-matrix.md].

## Security

RFC 6455 mandates client-to-server frame masking with a fresh random key
per message — **required even over `wss`/TLS**, since masking is a distinct
wire-level defense against cache/proxy poisoning and confused
intermediaries, not a substitute for TLS confidentiality
[Source: https://www.rfc-editor.org/rfc/rfc6455.html]. Most modern browsers
now require `wss://` except for same-device/localhost development
[Source: MDN Writing WebSocket client applications]. The `connect-src` CSP
directive governs which origins a document's script may open WebSocket
connections to — but `connect-src 'self'` does not reliably resolve to
`ws:`/`wss:` schemes across browsers (a documented cross-browser
inconsistency), so list the WebSocket scheme/origin explicitly rather than
relying on `'self'`
[Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/connect-src].
DoS mitigation is documented only generically — "a server can deny
connections that attempt too many connections" — with no specific
rate-limiting algorithm or threshold prescribed; don't assume an official
recommended rate-limit value exists [Source: MDN Writing WebSocket
servers]. Origin/CORS-class defense, encryption-guarantee comparisons
across realtime transports, and connection-level handshake-auth design are
owned by `SK-BE-004` — not restated here.

## Performance

The core documented limitation is the **absence of backpressure**: a fast
producer can overrun a slow consumer, causing unbounded memory growth (or
CPU saturation from continuous event dispatch); `bufferedAmount` is the one
performance-relevant introspection point available to callers, and polling
it before sending more is the only manual mitigation
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API]
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket].
Because a single WebSocket connection is one long-lived TCP stream, it
avoids the per-request overhead (new TCP/TLS handshake, HTTP headers) that
repeated HTTP polling would incur — RFC 6455 itself provides no
throughput/latency benchmarks
[Source: https://www.rfc-editor.org/rfc/rfc6455.html]. Deep performance
method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

There is **no official unit/integration test framework, mocking library, or
conformance suite for WebSocket API consumers** — a real, documented gap,
not an oversight to paper over
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API].
The closest official material is MDN's worked ping/pong echo client/server
example — a manual reference implementation, not a test methodology
[Source: MDN Writing WebSocket client applications / servers].
Practically: test against a real or in-process server instance rather than
assuming a mock exists; Firefox DevTools' Network Monitor has a first-party
WebSocket frame inspector (filter `WS`, per-frame `Data`/`Size`/`OpCode`/
`MaskBit`/`FinBit`) useful for manual verification
[Source: https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/inspecting_web_sockets/index.html].
Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If the transport choice is still open, defer to `SK-BE-004` rather than
  assuming WebSocket.
- If the runtime target is unknown, ask — the available API surface differs
  (Node ships no built-in server).
- If shell is unavailable/denied, output advisory client/server code and
  state that it was not run or tested.

## Escalation

- A server accepting non-browser clients with no connection-level
  authentication beyond Origin checking is escalated to `SK-BE-004`'s
  handshake-auth guidance rather than decided here.

## Outputs & verification

- **Outputs:** WebSocket client/server implementation code (handshake
  handling, close-code handling, subprotocol negotiation), and
  version/compatibility analysis where relevant.
- **Verify:** handshake code validates `Sec-WebSocket-Version` and required
  headers; masking rules are enforced server-side; close-code handling
  distinguishes never-sent-on-the-wire codes (1005/1006/1015) from real
  ones; every version-specific claim carries its applicable range.

## References

- [references/protocol-details.md](references/protocol-details.md) —
  Tier-2: full `Sec-WebSocket-*` header table, close-code registry, frame
  structure.
- Source list: see `skill.yaml.source_references` (MDN / WHATWG / IETF RFC
  6455, 7692, 8441 / Node.js docs, retrieved 2026-09-10, via
  `research/technologies/websocket-api.md`).
