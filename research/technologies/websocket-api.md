# WebSocket API — Technology Research

Research date: 2026-09-09. WebSocket API is a browser Web API and companion wire protocol, not a versioned library — so "official documentation" here spans three canonical, jointly-authoritative sources rather than one vendor's docs:

- **`developer.mozilla.org/en-US/docs/Web/API/WebSocket*`** (MDN) — the de facto canonical developer-facing reference for the browser-side JavaScript API. MDN is not the spec owner but is widely treated as the practical authoritative documentation for web platform APIs and is used as such throughout this document.
- **`websockets.spec.whatwg.org`** (WHATWG WebSockets Living Standard) — the actual normative specification for the `WebSocket` JavaScript interface as implemented by browsers. [Source: https://websockets.spec.whatwg.org/] Confirmed live and current as of this research (most recent commit in the `whatwg/websockets` GitHub repo dated 2026-03-15, per `github.com/whatwg/websockets/commits/main`). This spec was split out of the WHATWG HTML Standard into its own Living Standard in 2021.
- **`www.rfc-editor.org/rfc/rfc6455.html`** (IETF RFC 6455) — the normative wire-protocol specification (handshake, framing, opcodes, masking) that both the WHATWG spec and all server implementations must interoperate with. Published December 2011; status Internet Standard (STD 34).

Two related IETF extension/companion RFCs are also cited: RFC 7692 (permessage-deflate compression extension) and RFC 8441 (WebSockets over HTTP/2).

Citation convention: `[Source: <url>] <claim>.` for documented facts, `[Inference, not confirmed in docs]` for reasoning not explicitly stated, and "Not documented / could not verify" where no official source was found. `Unresolved:` flags items with conflicting or uncertain information. This document is explicitly about **WebSocket API** (the browser JS interface + RFC 6455 wire protocol) and does **not** cover Socket.IO, SockJS, or other userland libraries built on top of it — those are separate technologies with their own abstractions (rooms, auto-reconnect, fallback transports) not part of the WebSocket API surface itself.

---

## 1. Core concepts

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] "The WebSocket API makes it possible to open a two-way interactive communication session between the user's browser and a server. With this API, you can send messages to a server and receive responses without having to poll the server for a reply."

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] RFC 6455 defines the WebSocket Protocol as providing full-duplex, bidirectional communication over a single TCP connection: "The goal of this technology is to provide a mechanism for browser-based applications that need two-way communication with servers that does not rely on opening multiple HTTP connections." The protocol begins with an HTTP-compatible opening handshake and then switches to a lightweight framed message format layered directly over TCP.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] MDN documents two distinct JS-facing mechanisms under the "WebSocket API" umbrella:
- **`WebSocket`** interface — the primary, stable interface for connecting to a server and sending/receiving data.
- **`WebSocketStream`** interface — a newer, Promise/Streams-based alternative that adds automatic backpressure; explicitly marked non-standard (see §4, §14).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] Two companion event interfaces are part of the API surface: `MessageEvent` (delivered on `message`, carries received data) and `CloseEvent` (delivered on `close`, carries close code/reason/cleanliness).

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] The protocol registers two URI schemes: `ws` (unencrypted, conventionally port 80) and `wss` (TLS-encrypted, conventionally port 443).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] MDN explicitly frames WebSocket relative to adjacent technologies: Server-Sent Events is the recommended alternative for one-way server-to-client streaming, and **WebTransport** is described as "expected to replace the WebSocket API for many applications" going forward (see §14 for the tradeoffs cited).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket] [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/close_event] Connection lifecycle is modeled as a small state machine exposed via `readyState`: `CONNECTING` (0) → `OPEN` (1) → `CLOSING` (2) → `CLOSED` (3), with the `open`, `message`, `error`, and `close` events marking transitions.

## 2. Architecture

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] Architecturally, RFC 6455 splits the protocol into two phases layered over one persistent TCP connection: (1) an **opening handshake** that reuses HTTP semantics (a `GET` request with `Upgrade: websocket`, answered by an HTTP `101 Switching Protocols` response), and (2) a **framing protocol** that takes over the same TCP stream afterward — no further HTTP request/response cycles occur on that connection.

**Opening handshake** — [Source: https://www.rfc-editor.org/rfc/rfc6455.html] Client sends `Upgrade: websocket`, `Connection: Upgrade`, a random 16-byte base64-encoded `Sec-WebSocket-Key` nonce, `Sec-WebSocket-Version: 13`, and optionally `Origin`, `Sec-WebSocket-Protocol`, `Sec-WebSocket-Extensions`. The server must respond `101 Switching Protocols` with a `Sec-WebSocket-Accept` header computed as base64(SHA-1(`Sec-WebSocket-Key` + the fixed GUID `258EAFA5-E914-47DA-95CA-C5AB0DC85B11`)) — this proves the responder is WebSocket-aware and not merely echoing an arbitrary Upgrade.

[Source: https://websockets.spec.whatwg.org/] The WHATWG Living Standard states it "integrates WebSocket protocol handshaking with the Fetch standard, replacing RFC 6455's original algorithm," specifically so that "CSP, cookies, HSTS, and other Fetch-related protocols are handled in a single location." **[Version-sensitive / architectural note]** This means the *browser-implemented* handshake algorithm is technically governed by the WHATWG spec's Fetch-integrated procedure rather than RFC 6455 §4 verbatim, even though the resulting bytes on the wire are RFC-6455-compatible; RFC 6455 remains the source of truth for non-browser (server/library) implementations.

**Framing** — [Source: https://www.rfc-editor.org/rfc/rfc6455.html] Each frame carries: a FIN bit (last fragment of a message), 3 reserved bits (RSV1-3, used by extensions, e.g. permessage-deflate uses RSV1), a 4-bit opcode, a MASK bit, a variable-length payload-length field (7/16/64-bit forms), an optional 4-byte masking key, and the payload. Opcodes: `0x0` continuation, `0x1` text, `0x2` binary, `0x8` close, `0x9` ping, `0xA` pong; `0x3`-`0x7` and `0xB`-`0xF` are reserved.

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] **Masking is architecturally mandatory in one direction only**: "A client MUST mask all frames that it sends to the server" (using a fresh, cryptographically random key per message); a server must never mask frames it sends to a client, and must close the connection if it receives an unmasked frame from a client.

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] **Fragmentation**: a single logical message may be split across multiple frames — the first frame carries the real opcode (text/binary) with FIN=0, continuation frames use opcode `0x0`, and the final fragment has FIN=1. Control frames (close/ping/pong, opcodes `0x8`-`0xA`) must never be fragmented and are capped at 125 bytes of payload.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] MDN recommends putting a **reverse proxy** (a conventional HTTP server) in front of a WebSocket server to detect the handshake, pre-process the request, and handle cookie/authentication validation before forwarding legitimate connections — shifting some architectural security burden off the WebSocket server itself.

[Source: https://www.rfc-editor.org/rfc/rfc8441.html] RFC 8441 defines an alternate architecture, **WebSockets over HTTP/2**: instead of the RFC 6455 GET+Upgrade handshake, it uses HTTP/2's Extended CONNECT method with a new `:protocol` pseudo-header set to `websocket`, tunneling the WebSocket framing protocol inside a single HTTP/2 stream. This requires the server to advertise support via the `SETTINGS_ENABLE_CONNECT_PROTOCOL` SETTINGS parameter for backward compatibility; once negotiated, ordinary WebSocket framing takes over on that stream exactly as over raw TCP.

## 3. APIs

[Source: https://websockets.spec.whatwg.org/] The normative WHATWG IDL for the `WebSocket` interface:

```webidl
interface WebSocket : EventTarget {
  constructor(USVString url, optional (DOMString or sequence<DOMString>) protocols);
  readonly attribute USVString url;
  readonly attribute unsigned short readyState;
  readonly attribute unsigned long long bufferedAmount;

  attribute EventHandler onopen;
  attribute EventHandler onerror;
  attribute EventHandler onclose;
  readonly attribute DOMString extensions;
  readonly attribute DOMString protocol;

  undefined close(optional unsigned short code, optional USVString reason);

  attribute EventHandler onmessage;
  attribute BinaryType binaryType;
  undefined send((BufferSource or Blob or USVString) data);
};
```

**Constructor** — [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket] `new WebSocket(url, protocols)`. `url` accepts `ws`, `wss`, `http`, or `https` schemes; an `https://` (or `http://`) URL is automatically resolved to `wss://` (or `ws://`) — **[Version-sensitive]** this http(s)-scheme acceptance was added to the spec in May 2023 per the WHATWG repo's commit history (see header note); earlier implementations only accepted `ws`/`wss` literally. The URL cannot include a fragment. `protocols` is a single string or array of strings (each value must be unique and match the `Sec-WebSocket-Protocol` header grammar); throws `SyntaxError` on any violation.

**Properties** — [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket]
| Property | Read-only | Description |
|---|---|---|
| `url` | yes | Absolute resolved URL of the connection |
| `readyState` | yes | `CONNECTING`(0) / `OPEN`(1) / `CLOSING`(2) / `CLOSED`(3) |
| `bufferedAmount` | yes | Bytes queued by `send()` not yet transmitted |
| `protocol` | yes | Sub-protocol selected by the server (empty string if none/unopened) |
| `extensions` | yes | Extensions negotiated by the server |
| `binaryType` | no | `"blob"` (default) or `"arraybuffer"` — controls the type of `MessageEvent.data` for binary frames |

**Methods** — [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/send] `send(data)` accepts `string` (UTF-8 encoded), `Blob`, `ArrayBuffer`, `TypedArray`, or `DataView`; it is fire-and-forget/asynchronous, incrementing `bufferedAmount` by the queued byte size. It throws `InvalidStateError` if `readyState` is `CONNECTING`; if `readyState` is `CLOSING` or `CLOSED` the data is silently discarded (no exception). [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket] `close(code, reason)` — both parameters optional; initiates the closing handshake with an optional numeric close code and human-readable reason string.

**Events** — [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket] `open` (connection established, no event-specific data), `message` (fires as `MessageEvent`, `.data` is string/Blob/ArrayBuffer per `binaryType`), `error` (connection error; MDN notes the browser always closes the connection and fires `close` immediately afterward — the `error` event itself carries no diagnostic detail per spec), `close` (fires as `CloseEvent`).

**`CloseEvent`** — [Source: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent] Properties: `code` (unsigned short — the close code), `reason` (string, server/subprotocol-specific), `wasClean` (boolean — whether the closing handshake completed cleanly).

**Close status codes** — [Source: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code] (cross-referencing RFC 6455 §7.4 registry, as tabulated by MDN):
| Code | Name |
|---|---|
| 1000 | Normal Closure |
| 1001 | Going Away |
| 1002 | Protocol error |
| 1003 | Unsupported Data |
| 1004 | Reserved |
| 1005 | No Status Received (never actually sent on the wire) |
| 1006 | Abnormal Closure (never actually sent on the wire) |
| 1007 | Invalid frame payload data |
| 1008 | Policy Violation |
| 1009 | Message Too Big |
| 1010 | Mandatory Extension |
| 1011 | Internal Error |
| 1012 | Service Restart |
| 1013 | Try Again Later |
| 1014 | Bad Gateway |
| 1015 | TLS handshake (never actually sent on the wire) |
| 1016–2999 | Reserved for future protocol/extension revisions |
| 3000–3999 | Registered with IANA for library/framework/application use |
| 4000–4999 | Private use, by prior agreement between endpoints |

**No JS-level ping/pong API** — [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket] Not documented / could not verify any method on the `WebSocket` interface to send a ping frame from JavaScript. [Source: https://www.rfc-editor.org/rfc/rfc6455.html] Ping/pong (opcodes `0x9`/`0xA`) is a protocol-level heartbeat mechanism handled by the underlying implementation (browser or server library), not exposed as a JS method — application-level heartbeats over `WebSocket` from a browser client must be implemented by sending ordinary text/binary messages, since script cannot originate protocol-level ping frames. **[Inference, not confirmed in docs]** This is why most JS ping/pong "heartbeat" code in the wild is actually application-level text messages, not RFC 6455 ping/pong frames.

**`WebSocketStream`** (non-standard) — [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocketStream] Constructor `new WebSocketStream(url)`; properties `url`, `opened` (Promise resolving to `{readable, writable, extensions, protocol}`), `closed` (Promise resolving to close code/reason); method `close()`. Explicitly marked experimental and non-standard, not part of any official spec, with standardization tracked as an open PR (`whatwg/websockets#48`) at time of writing.

## 4. Configuration

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket] There is no separate "configuration object" for `WebSocket` — the entire configurable surface is the two constructor arguments (`url`, `protocols`) plus the mutable `binaryType` property (default `"blob"`, settable to `"arraybuffer"`) chosen after construction.

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] Handshake-time configuration is expressed via the `Sec-WebSocket-Protocol` (application sub-protocol negotiation) and `Sec-WebSocket-Extensions` (protocol extension negotiation, e.g. compression) headers — both are request-side "offers" from the client and response-side "selections" from the server; only extensions/protocols the client actually offered may be selected by the server.

[Source: https://www.rfc-editor.org/rfc/rfc7692.html] The `permessage-deflate` extension (registered via `Sec-WebSocket-Extensions`) is the standard compression configuration: negotiable parameters are `server_no_context_takeover` / `client_no_context_takeover` (disable reuse of compression state between messages) and `server_max_window_bits` / `client_max_window_bits` (LZ77 window size, 8–15, i.e. 256–32768 bytes). RFC 7692 recommends a window of "1,024 or more" for useful compression ratios. **[Security-relevant configuration]** RFC 7692 explicitly warns of a known CRIME-style compression-oracle exploit when history-based compression is combined with a secure transport (TLS), and instructs implementers to integrate the extension with the security protocol carefully.

[Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/connect-src] Server/document-side configuration of *which* origins a page may open WebSocket connections to is governed by the `connect-src` Content Security Policy directive, which explicitly lists `WebSocket` among the APIs it controls. A documented interoperability caveat: `connect-src 'self'` does not resolve to `ws:`/`wss:` schemes in all browsers (tracked in `w3c/webappsec-csp` issue 7), so CSP authors may need to list the WebSocket origin/scheme explicitly rather than relying on `'self'`.

[Source: https://nodejs.org/api/globals.html] In Node.js, the global `WebSocket` client class can be disabled entirely via the `--no-experimental-websocket` CLI flag (a configuration knob at the runtime level, not the API level).

## 5. Recommended patterns

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications] Use `addEventListener()` for `open`/`message`/`error`/`close` rather than only the `on*` properties, so multiple listeners can coexist; check `WebSocket.bufferedAmount` before sending more data if flow control matters to the application (since `send()` provides no backpressure signal itself — see §14).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications] **bfcache-friendly lifecycle pattern**: close the WebSocket connection on the page's `pagehide` event and reopen it on `pageshow` when `event.persisted` is `true`. MDN's stated rationale: "If a page has an open WebSocket connection, the browser may not add it to the bfcache. It's therefore good practice to close the connection when the user has finished with the page." The Performance API's `notRestoredReasons` property is cited as a way to debug bfcache-blocking.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications] Use `wss://` in production; MDN notes most modern user agents now require secure (`wss://`) connections except for same-device/localhost development, and mixing schemes with the hosting page (opening `ws://` from an `https://` page) is treated as mixed content and commonly blocked.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] **Server-side origin checking**: "You can use this header for security (checking for same origin, automatically allowing or denying, etc.) and send a 403 Forbidden if you don't like what you see. This is effective against Cross Site WebSocket Hijacking (CSWH)." MDN also notes non-browser clients can forge the `Origin` header, so this check is a defense specifically against browser-based CSWH, not a full authentication mechanism.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] Recommended server request-validation pattern: reject with HTTP `400 Bad Request` and close the socket immediately if any handshake header is missing/malformed/unsupported (e.g., unsupported `Sec-WebSocket-Version` — respond with the versions the server does support in the same header field).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] Recommended architecture pattern: **front the WebSocket server with a reverse proxy** for handshake pre-processing, cookie/auth validation, and general HTTP-layer concerns before traffic reaches the WebSocket-handling process.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] Ping/pong heartbeat pattern at the protocol level (server-authored libraries, not raw browser JS — see §3): respond to each received ping with exactly one pong carrying identical payload data; if multiple pings arrive before a pong is sent, send only the most recent single pong; pongs received without a preceding ping should be ignored.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] Choose `WebSocket` when a standard, widely-interoperable, well-supported two-way channel is a good fit; MDN's explicit guidance is to reach for `WebTransport` instead only "if your application requires a non-standard custom solution" needing backpressure, unidirectional streams, out-of-order delivery, or unreliable datagrams — i.e. `WebSocket` remains the recommended default.

## 6. Anti-patterns

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] Relying on plain `WebSocket` for very high-throughput or bursty message streams without any application-level flow control: MDN states directly that when messages "arrive faster than the application can process them, the application will either fill up the device's memory by buffering those messages, become unresponsive due to 100% CPU usage, or both" — because the base API has no backpressure mechanism.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] Trusting a client-forged `Origin` header as sole authentication/authorization: MDN explicitly flags that non-browser agents can send arbitrary `Origin` values, so origin-checking alone is CSWH mitigation, not a substitute for real authentication.

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] Server implementations that fail to enforce the client-must-mask / server-must-not-mask rule, or that skip disconnecting clients sending unmasked frames, violate a security-motivated requirement of the protocol (Section 5.1) rather than a mere stylistic convention.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocketStream] Using `WebSocketStream` in production code today: MDN marks it experimental/non-standard, "may change or be removed," with limited browser engine support — an anti-pattern for anything beyond experimentation as of this research date.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications] Leaving WebSocket connections open indefinitely across page navigations without handling `pagehide`/`pageshow`: this both blocks bfcache eligibility and can leak server-side connection/resource state for pages the user has effectively left.

[Inference, not confirmed in docs] Assuming `send()` guarantees delivery or throws on network failure: per §3, `send()` is fire-and-forget and silently drops data once the socket is `CLOSING`/`CLOSED`, so code that treats a successful `send()` call as delivery confirmation is relying on behavior the spec does not provide.

## 7. Security

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] **Masking as an anti-cache-poisoning measure**: RFC 6455 requires client-to-server frame masking specifically to prevent malicious page content from crafting byte sequences (over an attacker-controlled but same-origin-permitted WebSocket) that could poison intermediary caches or confuse misconfigured proxies/firewalls that don't understand WebSocket framing; masking keys must be drawn from "a strong source of entropy." Masking is required even over `wss://` (TLS) — it is not a substitute for TLS confidentiality, it is a distinct wire-level protection.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] **Cross-Site WebSocket Hijacking (CSWH)**: browsers always send `Origin` on WebSocket handshake requests; servers are directed to validate it and reject (403) unexpected origins as an effective mitigation, with the caveat that this only defends against browser-originated cross-site attacks, not forged non-browser clients.

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] The WebSocket handshake deliberately reuses the browser's existing same-origin/cookie machinery (it's an HTTP request before the Upgrade), so ordinary HTTP-layer authentication (session cookies, `Authorization` headers set during the handshake) applies to the initial request — but the spec places the origin-validation *responsibility* on the server, since the browser itself does not block cross-origin WebSocket connections the way it blocks cross-origin `fetch`/XHR by default.

[Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/connect-src] `connect-src` CSP directive governs which origins a document's script may open `WebSocket` connections to; note the documented `'self'`-vs-`ws:`/`wss:` scheme-matching inconsistency across browsers (see §4).

[Source: https://www.rfc-editor.org/rfc/rfc7692.html] Compression-related security: permessage-deflate carries a documented CRIME-style compression-oracle risk when combined with secret data and a TLS channel; RFC 7692 flags this explicitly rather than leaving it implicit.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] DoS mitigation is mentioned only briefly and generically: "The server can deny [connections] if they attempt too many connections in order to save itself from Denial-of-Service attacks" — MDN does not prescribe a specific rate-limiting algorithm or threshold; Not documented / could not verify any official recommended rate-limit values.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications] Browsers require secure contexts for WebSocket in most cases: "Most user agents now require secure connections unless on the same device/network" — meaning `ws://` from a non-localhost page is increasingly restricted by browser policy, independent of what the server allows.

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] Constructor-level guard: [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket] the `WebSocket()` constructor throws `SecurityError` if the target URL is one the calling context is not permitted to access (e.g., blocked by CSP or other browser-enforced policy) — this is the JS-visible enforcement point for the browser-side origin/CSP restrictions described above.

Unresolved: MDN's client-application guide references browsers requiring secure connections "unless on the same device/network" without a precise, citable specification of what counts as "same network" — this appears to be implementation-specific relaxation (e.g., private-network/localhost exceptions) rather than a normative requirement in RFC 6455 or the WHATWG spec, and the exact boundary is not pinned down in the fetched official text.

## 8. Performance

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] The core documented performance characteristic of plain `WebSocket` is the **absence of backpressure**: fast producers can overrun a slow consumer, leading to unbounded memory growth from internal buffering, or CPU saturation from continuous event dispatch — MDN states this is exactly the gap `WebSocketStream` (via the Streams API) is designed to close.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket] `bufferedAmount` is the one performance-relevant introspection point exposed on `WebSocket` itself — the number of bytes queued by `send()` calls but not yet actually transmitted over the network; MDN's client guide implies polling/checking this value is the manual mitigation available to callers wanting to avoid runaway internal buffering (see §5).

[Source: https://www.rfc-editor.org/rfc/rfc7692.html] Compression (`permessage-deflate`) is the documented mechanism for reducing on-wire payload size; RFC 7692 frames the `*_no_context_takeover` parameters as a memory-vs-compression-ratio tradeoff (disabling context takeover reduces per-connection server memory retained between messages at the cost of worse compression) and recommends an LZ77 window of at least 1,024 bytes for the compression to be "useful."

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] Because a single WebSocket connection is one long-lived TCP stream, RFC 6455 avoids the per-request overhead (new TCP/TLS handshake, HTTP headers) that repeated HTTP polling would incur — this is the protocol's foundational performance rationale ("does not rely on opening multiple HTTP connections"), though the RFC does not provide throughput/latency benchmarks itself.

Not documented / could not verify: any officially specified maximum message size, maximum frame size, or maximum number of concurrent connections per browser/tab — these are left as implementation-defined limits by both RFC 6455 and the WHATWG spec; the 64-bit payload-length field in the frame format is a protocol-level ceiling, not a practical/recommended one.

## 9. Testing

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] MDN references third-party testing/inspection tools only in passing (e.g., "WebSocket King" as a client tool for manually testing WebSocket servers, and AsyncAPI for describing event-driven WebSocket-based APIs) — these are not official Mozilla/WHATWG/IETF tools, just external resources MDN links to.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications] [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] The closest thing to official "testing guidance" is MDN's worked example client/server code (a ping/pong echo application, source linked at `github.com/mdn/dom-examples/tree/main/websockets`), which functions as a manual integration-testing reference implementation rather than a testing framework or methodology.

[Source: https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/inspecting_web_sockets/index.html] Firefox DevTools' Network Monitor has a dedicated WebSocket inspector: filter for `WS` (HTTP 101) requests, then a live-updating "Response" pane lists individual frames with sent/received direction indicators, and optional columns for `Data`, `Size`, `Time`, `OpCode`, `MaskBit`, `FinBit`. It supports pausing capture, filtering by `All`/`Sent`/`Received`/`Control`, and — notably — parses and pretty-prints payloads for several known sub-protocols (including JSON, Socket.IO, SignalR, STOMP, WAMP) as expandable trees. This is the one genuinely "official testing/debugging tool" documentation found for WebSocket.

Not documented / could not verify: any official unit/integration-testing framework, mocking library, or WHATWG/IETF-endorsed conformance test suite specifically for WebSocket API consumers (as opposed to browser-engine conformance testing, which is out of scope for application developers).

## 10. Deployment

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] Deployment guidance from MDN is limited to server-authoring concerns rather than infrastructure/orchestration concerns: servers may listen on any port, but choosing a port other than 80/443 "may have problems with firewalls and/or proxies," and browsers generally require secure connections for WebSocket except for local-device exceptions (see §7).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] The recommended deployment topology is explicitly a **reverse proxy in front of the WebSocket process**, handling the HTTP-layer handshake pre-processing, cookies, and authentication before proxying the upgraded connection through.

[Source: https://www.rfc-editor.org/rfc/rfc8441.html] For HTTP/2-fronted deployments, RFC 8441 (WebSockets over HTTP/2, via Extended CONNECT and `SETTINGS_ENABLE_CONNECT_PROTOCOL`) is the standardized mechanism for tunneling WebSocket traffic through an HTTP/2 connection/proxy rather than requiring a dedicated HTTP/1.1 Upgrade path — relevant to deployments behind HTTP/2-terminating load balancers or gateways.

Not documented / could not verify: official guidance on horizontal scaling of WebSocket servers (sticky sessions, connection-count-aware load balancing, pub/sub fan-out across server instances) — this falls outside the scope of the browser API and protocol specs themselves and is typically addressed by server frameworks/infrastructure, not by MDN/WHATWG/IETF.

## 11. Migration

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] RFC 6455 itself is the successor to a series of pre-standard IETF "hybi" drafts and the earlier Hixie-76 draft protocol used by early browser implementations; `Sec-WebSocket-Version: 13` is the version negotiated by all RFC-6455-conformant implementations, and a server that doesn't support the requested version responds with the versions it does support in the `Sec-WebSocket-Version` response header — this is the protocol's own built-in version-negotiation/migration mechanism rather than a document describing how to port code between major API versions.

[Source: https://websockets.spec.whatwg.org/] Because the WHATWG spec is a Living Standard (no numbered major/minor releases), there is no "migrating from WebSocket API vX to vY" document analogous to a library's changelog-driven migration guide; changes land incrementally (see §13 for the one concrete recent behavioral change identified: http(s)-scheme acceptance in the constructor, added ~May 2023).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocketStream] The closest thing to a forward-migration path documented is WebSocket → `WebSocketStream` (for backpressure) or WebSocket → WebTransport (for advanced transport features) — both explicitly framed by MDN as "consider instead," not as required migrations, since plain `WebSocket` remains the stable, broadly-supported default.

This dimension does not map cleanly onto WebSocket API in the "upgrading between major library versions" sense used for frameworks/ORMs, because the Web API has no semver-style major versions; the applicable migration content is protocol-version negotiation (above) and cross-technology migration to newer complementary APIs (`WebSocketStream`, `WebTransport`).

## 12. Version information

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] RFC 6455, "The WebSocket Protocol," published December 2011 by the IETF; status **Internet Standard (STD 34)**. This is the normative wire-protocol version; the protocol identifies itself on the wire via `Sec-WebSocket-Version: 13`.

[Source: https://websockets.spec.whatwg.org/] The WHATWG **WebSockets Living Standard** has no version number by design (Living Standards are continuously updated rather than versioned/released). [Source: https://github.com/whatwg/websockets/commits/main] The `whatwg/websockets` GitHub repository's most recent commit at research time is dated 2026-03-15 ("Meta: update repository files"), with substantive translation-related commits in mid/late 2025 — confirming the spec is actively maintained, not abandoned. It was split into its own standalone Living Standard, separate from the HTML Standard, in 2021.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket] MDN marks the `WebSocket` interface **Baseline: Widely available**, with support across major browsers dating to **July 2015**.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocketStream] `WebSocketStream` is explicitly marked **experimental / non-standard**, with support limited to "one rendering engine" per MDN's overview page — i.e. not broadly available across browsers as of this research.

[Source: https://nodejs.org/api/globals.html] **[Version-sensitive, Node.js runtime]** The global `WebSocket` client class in Node.js: introduced in Node **v21.0.0** / backported to **v20.10.0**, initially gated behind the `--experimental-websocket` flag; the flag requirement was removed in **v22.0.0**, and the API was marked no-longer-experimental (stable) as of **v22.4.0**. This is a client-only implementation (browser-compatible `WebSocket`), not a WebSocket *server* — Node.js does not ship a built-in WebSocket server.

[Source: https://www.rfc-editor.org/rfc/rfc7692.html] RFC 7692 (`permessage-deflate` compression extension) published December 2015.

[Source: https://www.rfc-editor.org/rfc/rfc8441.html] RFC 8441 (WebSockets over HTTP/2) published September 2018.

Unresolved: whether there is a formal "LTS" or support-window concept for the WHATWG spec or RFC 6455 — neither applies in the way it does to a released software package; both are treated as evergreen/current by definition (Living Standard / Internet Standard respectively), so "LTS status" as a question does not have a meaningful documented answer beyond "currently in force."

## 13. Breaking changes

[Source: https://github.com/whatwg/websockets/commits/main] The most significant recently-identified behavioral change to the browser-facing API: the `WebSocket()` constructor's `url` parameter began accepting `http`/`https` schemes (auto-normalized to `ws`/`wss`) — per the commit history summary retrieved, this "allowing HTTP(S) schemes in the WebSocket constructor" change is dated **May 2023**. **[Version-sensitive]** Code or documentation written before this date, or environments running older browser engines, should not assume `http(s)://` URLs are accepted by `new WebSocket()` — only `ws`/`wss` were valid earlier.

[Source: https://websockets.spec.whatwg.org/] The Fetch-integration rewrite of the opening-handshake algorithm (WHATWG spec now delegates handshake mechanics to the Fetch standard rather than restating RFC 6455 §4 directly, per §2 above) is a documented architectural change relative to treating RFC 6455 as the sole normative handshake description for browsers — though this is a spec-authoring/architecture change, not a documented break in observable client behavior.

Not documented / could not verify: any breaking change to the RFC 6455 wire protocol itself since its December 2011 publication — RFC 6455 has not been superseded or revised by a subsequent RFC (extensions like RFC 7692/RFC 8441 layer on top of it rather than replacing it), so there is no "RFC 6455 v2" breaking-change history to report.

Unresolved: whether any other WHATWG spec changes between 2021 (spec split from HTML) and the May 2023 http(s)-scheme change constitute additional breaking changes — the commit-history summary retrieved was not exhaustive (only the top few commits were surfaced), so a full breaking-change timeline could not be independently verified from the sources fetched.

## 14. Limitations

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] **No backpressure**: explicitly documented as the primary limitation of the `WebSocket` interface — no mechanism exists for the receiving side to signal the sender to slow down; this is the stated reason `WebSocketStream` and `WebTransport` exist as alternatives.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] **No unidirectional streams, no out-of-order delivery, no unreliable/datagram delivery mode**: MDN lists these as capabilities `WebTransport` has that `WebSocket` does not, implying they are out of scope for the WebSocket API by design (WebSocket is a single ordered, reliable, bidirectional message stream).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/send] No delivery confirmation from `send()` — it is fire-and-forget; data is silently dropped once the socket has entered `CLOSING`/`CLOSED` rather than raising an error.

[Source: https://www.rfc-editor.org/rfc/rfc6455.html] Control frames (ping/pong/close) are capped at **125 bytes** of payload by the protocol and must not be fragmented — a hard protocol-level limitation, not implementation-specific.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket] No JS-level API to originate a protocol ping frame from a browser client (see §3) — heartbeating from browser script must be done at the application/message layer instead.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] Open connections can block the page from entering the browser's back/forward cache (bfcache) unless explicitly closed on navigation-away, a documented interaction limitation rather than a protocol one (see §5/§6).

Not documented / could not verify: an official maximum message size or maximum frame size at the API or protocol level (the 64-bit length field is the theoretical ceiling; real limits are implementation-defined per browser/server).

## 15. Debugging

[Source: https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/inspecting_web_sockets/index.html] Firefox DevTools' Network Monitor provides first-party WebSocket frame inspection: filter to `WS` (HTTP 101) requests, inspect a live-updating frame table (sent/received direction, `Data`, `Size`, `Time`, `OpCode`, `MaskBit`, `FinBit` columns), filter frames by `All`/`Sent`/`Received`/`Control`, pause/resume capture, and get automatic pretty-printed parsing for several known sub-protocol payload formats (JSON, Socket.IO, SignalR, STOMP, WAMP, and others).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket] The `error` event itself is documented as carrying essentially no diagnostic payload — MDN's description is that it fires "if an error occurs" and is immediately followed by `close`; application-level debugging therefore leans on the `CloseEvent`'s `code`/`reason`/`wasClean` (see §3) to distinguish clean vs. abnormal termination, since `error` alone doesn't disambiguate cause.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code] Because codes 1005, 1006, and 1015 are explicitly documented as "never actually sent on the wire" (they're reserved for the *local* API to report conditions where no real close frame was received, e.g. an abrupt network drop), a `close` handler that sees `1006` is diagnosing a client-side-observed abnormal disconnect, not a value the remote peer chose to send — a subtlety relevant to writing correct disconnect-diagnosis logic.

Not documented / could not verify: equivalent official documentation for Chrome DevTools' or Safari Web Inspector's WebSocket frame inspectors was not directly fetched in this research pass (only Firefox's was retrieved); their existence is widely known but not independently confirmed here against an official Chrome/WebKit doc page, so no citation is given for them.

## 16. Integration

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] MDN's overview page lists example server-side implementations across ecosystems (without endorsing any single one as "official"): Node.js (`ws`, Socket.IO, SocketCluster, WebSocket-Node, Total.js), Python (Flask-SocketIO, Django Channels), Go (Gorilla WebSocket), C#/.NET (SignalR), Elixir (Phoenix Channels, Phoenix LiveView), C++/Erlang (µWebSockets, Cowboy), PHP. These are cited by MDN as illustrative options, not as part of the WebSocket API spec itself.

[Source: https://nodejs.org/api/globals.html] Node.js ships a **browser-compatible global `WebSocket` client** (see §12) as part of its own standard library surface, described as "a browser-compatible implementation of `<WebSocket>`" — the official Node.js integration point for consuming WebSocket servers from server-side/CLI JavaScript without a third-party dependency. This is client-only; Node.js does not provide a built-in server-side WebSocket implementation.

[Source: https://www.rfc-editor.org/rfc/rfc8441.html] Integration with HTTP/2 infrastructure (proxies, load balancers, gateways) is standardized via RFC 8441's Extended CONNECT mechanism (§2, §10), letting WebSocket traffic be tunneled through HTTP/2-terminating intermediaries without falling back to HTTP/1.1.

[Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/connect-src] Integration with the web platform's security model is via the `connect-src` CSP directive (governs allowed WebSocket destinations) and, per §7, the browser's Fetch-integrated handshake (cookies, HSTS, and other Fetch-related behaviors apply to the handshake request per the WHATWG spec).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] `WebSocket` is available inside Web Workers, not just the main document thread — documented explicitly on both the overview and interface reference pages.

## 17. Production considerations

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications] Use `wss://` (TLS) in production; most modern browsers restrict plain `ws://` outside of local/same-device development contexts (see §7).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] Validate the `Origin` header server-side (CSWH mitigation), enforce masking rules per RFC 6455 §5.1 (disconnect clients sending unmasked frames), return proper HTTP error codes (400/403) for malformed or disallowed handshake requests before the connection upgrades, and consider connection-count limiting as a basic DoS defense (see §7).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers] Architect with a reverse proxy in front of the WebSocket process for handshake pre-processing and auth (see §2, §10); be mindful that non-standard ports (other than 80/443) may run into firewall/proxy interoperability problems in production networks.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API] Plan for the lack of backpressure in plain `WebSocket` under production load — either implement application-level flow control (watch `bufferedAmount`), cap message rate/size server-side, or adopt `WebSocketStream`/`WebTransport` where broader-than-experimental support and backpressure are required (weighing `WebSocketStream`'s current non-standard status per §12).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications] Close connections explicitly on `pagehide` and reconnect on `pageshow` (`event.persisted`) to avoid interfering with the browser's bfcache and to avoid leaking idle server-side connections from navigated-away tabs (see §5).

[Source: https://www.rfc-editor.org/rfc/rfc7692.html] If enabling `permessage-deflate` compression in production, be aware of the documented CRIME-style compression-oracle risk when compressing data that mixes attacker-influenced and secret content over TLS (see §7) — this is a production security tradeoff, not just a performance knob.

[Inference, not confirmed in docs] Because RFC 6455 and the WHATWG spec do not mandate reconnection, exponential backoff, or message-delivery guarantees, production systems needing those properties must implement them at the application layer or adopt a userland library (e.g., Socket.IO) that layers such guarantees on top of raw WebSocket — this inference follows directly from the documented absence of those features in the base API (§14) rather than being stated as production advice in the fetched sources themselves.

---

## Sources cited (deduplicated)

- https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API — MDN WebSocket API overview
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket — MDN `WebSocket` interface reference
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket — MDN `WebSocket()` constructor reference
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/send — MDN `send()` method reference
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/close_event — MDN `close` event reference
- https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent — MDN `CloseEvent` interface reference
- https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code — MDN close-code table
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocketStream — MDN `WebSocketStream` (experimental) reference
- https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications — MDN client-implementation guide
- https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers — MDN server-implementation guide
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/connect-src — MDN CSP `connect-src` directive reference
- https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/inspecting_web_sockets/index.html — Firefox DevTools WebSocket inspector documentation
- https://websockets.spec.whatwg.org/ — WHATWG WebSockets Living Standard
- https://github.com/whatwg/websockets/commits/main — WHATWG WebSockets spec repo commit history (used to establish currency/version-sensitive change dates)
- https://www.rfc-editor.org/rfc/rfc6455.html — RFC 6455, The WebSocket Protocol (IETF)
- https://www.rfc-editor.org/rfc/rfc7692.html — RFC 7692, Compression Extensions for WebSocket (permessage-deflate)
- https://www.rfc-editor.org/rfc/rfc8441.html — RFC 8441, Bootstrapping WebSockets with HTTP/2
- https://nodejs.org/api/globals.html — Node.js official docs, global `WebSocket` client class
