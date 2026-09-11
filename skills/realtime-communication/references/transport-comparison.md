# Realtime transport comparison (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Condensed from
[technology-decision-matrix.md §6](../../../research/knowledge-maps/technology-decision-matrix.md)
— consult that document for the full citation trail.

## WebSocket API vs. Socket.IO vs. WebRTC

| | WebSocket API | Socket.IO | WebRTC |
|---|---|---|---|
| Relationship | Raw, standard, browser-native two-way channel | Protocol/framework layer *on top of* transports (one of which is WebSocket), adding reconnection/ack/broadcast/multiplexing | Peer-to-peer (no server relay for media once connected); no `alternativesTo` recorded |
| Origin/CORS-class defense | Servers should validate the `Origin` header on handshake (browsers always send it); only defends against **browser-originated** attacks since non-browser clients can forge `Origin` | **CORS must be explicitly configured** (disabled/restricted by default since v3); CORS only covers the long-polling transport, so `allowRequest` is recommended as an additional handshake check | Camera/mic access governed by the separate Media Capture and Streams API's consent model |
| Transport-layer masking/hijack defense | RFC 6455 **mandates** client-to-server frame masking with a fresh random key per message — required even over `wss`/TLS, since masking is a distinct wire-level protection, not a TLS substitute | N/A (built atop WebSocket/HTTP) | DTLS-SRTP mandated for media; self-signed certs required (not reusable indefinitely), must match document origin |
| Documented DoS control | Only generic guidance ("a server can deny connections that attempt too many connections"), no specific algorithm/threshold prescribed | `maxHttpBufferSize` (default **1 MB**, deliberately tightened from 100 MB in 2.x) acts as a basic DoS guard | Not addressed as a DoS-specific control in the source data |
| Backpressure handling | **Documented core limitation**: no built-in backpressure — fast producers can overrun a slow consumer, causing unbounded memory growth; `WebSocketStream` (Streams API) exists specifically to close this gap | `socket.volatile.emit()` trades reliability for reduced buffering — the documented mechanism for loss-tolerant, performance-sensitive messages | Outbound data-channel data auto-buffers; apps should monitor `bufferedamountlow` to avoid excess memory |
| Compression trade-off | `permessage-deflate` reduces payload size but carries a documented **CRIME-style compression-oracle risk** over TLS with secret data (RFC 7692 flags this explicitly) | WebSocket `perMessageDeflate` defaults to **false**, while long-polling `httpCompression` defaults to **true** — not uniform, an explicit CPU-vs-bandwidth trade-off | Codec choice is the analogous lever: AV1/VP9 named as more bandwidth-efficient than VP8/H.264 at equivalent quality |
| Official testing/mocking story | **None found** — no official unit/integration test framework, mocking library, or conformance suite for API *consumers* | Official testing guide demonstrates the same pattern across **Jest, Mocha, Tape, and Vitest**, with a documented `waitFor()` helper and `emitWithAck()` pattern | CI/headless guidance via Chrome flags (`--use-fake-ui-for-media-stream`, etc.) and Firefox prefs (`media.navigator.streams.fake`) to run without real devices |

**Unresolved (per source research):** no quantified performance comparison
(latency/throughput) exists between raw WebSocket and Socket.IO for
equivalent workloads — only that Socket.IO's own docs concede WebSocket has
"materially lower per-message overhead than HTTP long-polling," without a
number for WebSocket vs. Socket.IO-over-WebSocket specifically.

## Horizontal-scaling adapters (Socket.IO)

Socket.IO documents officially-supported multi-node adapters: Redis (pub+sub
client pair, or sharded Pub/Sub on Redis 7.0+), MongoDB, and PostgreSQL —
MongoDB additionally supports connection-state recovery, which the plain
Redis Pub/Sub adapter does not. Reverse-proxy/load-balancer integration
(e.g. sticky sessions on a Google Cloud Load Balancer) is documented with
worked timeout configuration.

**Anti-pattern flagged in the source data:** relying on the Redis adapter
for anything beyond real-time fan-out — it uses Pub/Sub only, doesn't
persist data, and **silently degrades broadcasts to local-server-only if
Redis is unavailable**.
