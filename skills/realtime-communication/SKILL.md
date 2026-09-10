---
name: Realtime communication
description: >-
  Select a realtime transport (WebSocket, Socket.IO, WebRTC, or SSE) and
  design its connection lifecycle, reconnection, horizontal-scaling, and
  handshake-authentication strategy. Use when a feature needs bidirectional,
  streaming, or low-latency push communication. Not for request/response
  APIs, and not for message-broker/event-streaming architecture, which this
  library has not researched.
spec_version: "1.0"
---

## Purpose & scope

Choose a realtime transport when that's open, and design the connection
lifecycle, horizontal-scaling, and handshake-authentication strategy around
it — independent of which transport is eventually used. Plain
request/response HTTP belongs to [api-design](../api-design/SKILL.md).
**Async message-broker/event-streaming architecture (Kafka, RabbitMQ, SQS)
is an explicit, documented gap in this library** — no broker beyond Redis's
pub/sub role inside Socket.IO has been researched — so this skill does not
answer that class of request by improvising from general knowledge.

## When to use / When not to use

**Use** when a feature needs bidirectional, streaming, or server-push
communication, or when an existing realtime layer's connection/scaling/auth
design needs review. **Do not use** when request/response HTTP is
sufficient, or for message-broker/event-streaming architecture — say the
gap out loud rather than fabricating broker guidance.

## Knowledge

**The three realtime transports serve genuinely different purposes, not
interchangeable ones** [Source: technology-decision-matrix.md §6]. WebSocket
API is the raw, standard, browser-native two-way channel. Socket.IO is a
protocol/framework layer built *on top of* transports (WebSocket among
them) — its own docs describe it as "not a raw WebSocket implementation,"
adding reconnection, acknowledgements, broadcast, and multiplexing. WebRTC
serves a different use case entirely: peer-to-peer media/data with no
server relay once connected. The decision-matrix data includes WebRTC in
this comparison because it shares the "realtime-networking" category, not
because any source frames it as a substitute for the other two.

**CORS/Origin checks are a browser-only, partial-transport control for
both WebSocket and Socket.IO — never a complete access-control
mechanism** [Source: security-knowledge-map.md, synthesis]. WebSocket's
`Origin`-header validation defends only against browser-originated attacks,
since non-browser clients can forge `Origin` freely. Socket.IO's CORS
configuration (explicitly restricted by default since v3) only covers its
HTTP long-polling transport — not the WebSocket transport itself — which is
exactly why Socket.IO's own docs recommend `allowRequest` as a required
supplement, not a nice-to-have. **Any server accepting connections from
non-browser clients (native apps, other backend services, `curl`) gets no
CORS/Origin protection at all** and needs its own connection-level
authentication regardless of CORS configuration.

**Encryption guarantees differ in kind across the three transports**
[Source: security-knowledge-map.md, synthesis]. WebRTC treats encryption as
architecturally non-optional — DTLS-SRTP is mandated for media, with no
plaintext mode available at all. WebSocket treats frame-masking as an
*additional*, TLS-independent wire-level control (RFC 6455 mandates
client-to-server masking even over `wss`/TLS, since masking guards against
cache/proxy poisoning, not confidentiality). Socket.IO inherits whichever
of these applies to its underlying transport. "Is TLS enabled" is not the
same question for all three — a review that only checks that misses
meaningfully different residual risks per transport.

**No realtime transport in this dataset has built-in backpressure handling
— all three independently converge on "monitor the buffer, then back off or
go lossy"** [Source: performance-knowledge-map.md §8, synthesis]. Plain
WebSocket has no backpressure at all (`bufferedAmount` is the only
introspection point; `WebSocketStream` exists specifically to close this
gap). Socket.IO's `socket.volatile.emit()` trades reliability for reduced
buffering. WebRTC data channels auto-buffer, with `bufferedamountlow` as the
monitoring signal. None of the individual technology docs frame this as a
shared transport-layer pattern — it only becomes visible by reading the
three side by side.

Full transport comparison table (Origin/CORS defense, masking/DTLS-SRTP,
DoS controls, compression trade-offs, official testing support) is in
[references/transport-comparison.md](references/transport-comparison.md).

## Decision framework

1. **Is this peer-to-peer media/data, or server-mediated events?** P2P
   media/data with no need for a server relay after connection setup →
   WebRTC. Server-mediated discrete events or broadcast → WebSocket or
   Socket.IO.
2. **If server-mediated: does the client set include non-browser clients,
   or does the app need reconnection/ack/broadcast/multiplexing
   out of the box?** Non-browser clients, or a need for those higher-level
   guarantees → Socket.IO (accepting its added dependency/bundle weight).
   Browser-only clients with a simple, already-bounded message shape → raw
   WebSocket API may be sufficient and avoids the extra dependency.
3. **Does the app run on more than one server instance?** If yes, a
   horizontal-scaling story is mandatory, not optional — sticky sessions
   and/or a pub-sub adapter (Redis is the documented default for Socket.IO)
   are required before the realtime layer can scale past one process.
4. **Does the client set include non-browser clients?** If yes, CORS/Origin
   checks provide zero protection for those clients — connection-level
   authentication (handshake auth, not just CORS) is mandatory regardless
   of transport.
5. **Is the actual need message-broker/event-streaming architecture rather
   than realtime transport?** (durable queues, at-least-once delivery,
   consumer groups) — if so, say this exceeds this skill's grounded scope
   rather than answering as if it were a transport-selection question.

## Workflow

1. Classify the need: peer-to-peer media/data vs. server-mediated events.
2. Apply the decision framework to select a transport, citing the
   comparison table where relevant.
3. Design the connection lifecycle: initial handshake, reconnection
   strategy, and — for non-browser clients — connection-level auth
   independent of CORS.
4. If the service runs on multiple instances, design the horizontal-scaling
   approach (sticky sessions and/or pub-sub adapter) before shipping.
5. Address backpressure explicitly: monitor buffered amount, or opt into a
   documented lossy/volatile-delivery mode where the transport offers one.
6. Hand off to the matching technology skill (websocket-api / socketio /
   webrtc) for implementation-level depth.

## Engineering rules

- Never treat CORS/Origin validation as sufficient access control for a
  realtime endpoint — it's browser-only and, for Socket.IO, transport-partial.
- Design the horizontal-scaling story before scaling past one instance, not
  after a production incident surfaces it.
- Address backpressure explicitly; an unmonitored send buffer is a latent
  memory-growth bug in every transport covered here.
- Don't propose message-broker/event-streaming architecture — that's outside
  this skill's grounded scope; say so.
- Don't default to Socket.IO by habit when the client set is browser-only
  and raw WebSocket's guarantees are already sufficient — the added
  dependency should be justified by an actual need for its features.

## Trade-offs

Raw WebSocket API avoids Socket.IO's dependency/bundle weight but leaves
reconnection, acknowledgement, and broadcast/multiplexing entirely to the
application. Socket.IO buys those guarantees plus multi-node scaling
adapters at the cost of protocol overhead and an added dependency. WebRTC
buys true peer-to-peer media/data with no server relay after setup, at the
cost of NAT-traversal/TURN infrastructure complexity that WebSocket and
Socket.IO don't need at all.

## Anti-patterns

- **Treating CORS as sufficient realtime access control** — it's
  browser-only and doesn't cover every transport Socket.IO offers.
- **Scaling a WebSocket/Socket.IO service past one instance without a
  sticky-session or pub-sub story** — connections silently stop
  broadcasting to peers on other instances.
- **Ignoring backpressure until a memory-growth incident** — every
  transport here documents the same unbounded-buffer risk; monitor it from
  the start.
- **Reaching for Socket.IO by default** when the client set is
  browser-only and raw WebSocket's simpler guarantees already suffice — an
  unjustified dependency.
- **Answering a message-broker/event-streaming question as if it were a
  realtime-transport question** — the domain's specific overreach trap,
  given this library's documented research gap there.

## Security

CORS/Origin checks are browser-only and partial (WebSocket: browser-only;
Socket.IO: covers only its long-polling transport) — never sufficient
alone; connection-level handshake authentication is required for any
non-browser client. WebRTC mandates DTLS-SRTP for media with no plaintext
mode; WebSocket mandates client-to-server frame masking even over `wss`,
as a TLS-independent control against cache/proxy poisoning, not a TLS
substitute. `permessage-deflate` compression (used by both WebSocket and
Socket.IO) carries a documented CRIME-style compression-oracle risk over
TLS with secret data [Source: security-knowledge-map.md]. Deep threat
modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

No transport covered here has built-in backpressure; all converge on the
same fix pattern (monitor the buffer, then back off or go lossy) — see
Knowledge above. Socket.IO's `maxHttpBufferSize` (default 1 MB, tightened
from 100 MB in 2.x) is a basic DoS/resource-exhaustion guard worth setting
deliberately rather than trusting the default blindly for every workload.
Deep performance method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

Official testing support differs sharply across the three: Socket.IO
documents a testing guide across Jest, Mocha, Tape, and Vitest with a
`waitFor()` helper and `emitWithAck()` pattern; WebRTC has CI/headless
guidance via Chrome/Firefox fake-media flags; the raw WebSocket API has
**no official unit/integration test framework, mocking library, or
conformance suite for consumers** — state this gap explicitly rather than
inventing a testing story for it [Source: technology-decision-matrix.md
§6]. Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If the realtime requirement (latency need, media-vs-events, expected
  scale) is too thin to support a transport decision, request it rather
  than assuming a default.
- If a transport is already in place, work within it unless a switch is
  explicitly requested.
- If the actual need is message-broker/event-streaming architecture, state
  that gap explicitly.

## Escalation

- A transport switch for an existing production realtime layer is a
  significant, hard-to-reverse decision — presented with trade-offs for
  explicit confirmation, never applied unilaterally.
- A request for durable message-broker/event-streaming architecture is
  escalated as a research gap requiring a dedicated research pass, not
  answered from general knowledge.

## Outputs & verification

- **Outputs:** a realtime-transport recommendation with trade-offs (when
  open), and a connection-lifecycle/scaling/handshake-auth design.
- **Verify:** reconnection is handled explicitly; a horizontal-scaling
  story exists whenever more than one instance is in play; handshake auth
  doesn't rely on CORS/Origin alone; backpressure is addressed.

## References

- [references/transport-comparison.md](references/transport-comparison.md) — Tier-2 full comparison table.
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
- [research/knowledge-maps/security-knowledge-map.md](../../research/knowledge-maps/security-knowledge-map.md)
- [research/knowledge-maps/performance-knowledge-map.md](../../research/knowledge-maps/performance-knowledge-map.md)
