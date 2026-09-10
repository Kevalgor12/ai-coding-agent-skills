---
name: WebRTC
description: >-
  WebRTC-specific peer-to-peer implementation: RTCPeerConnection/ICE/STUN/TURN
  connection establishment, SDP offer/answer and the perfect-negotiation
  pattern, RTCDataChannel usage, mandatory DTLS-SRTP security, and the
  Plan-B-to-Unified-Plan SDP history. Use when integrating RTCPeerConnection,
  getUserMedia/getDisplayMedia, or RTCDataChannel for true peer-to-peer
  media/data. Not for choosing among realtime transports (realtime-
  communication) or server-mediated WebSocket/Socket.IO implementation.
spec_version: "1.0"
---

## Purpose & scope

Implement WebRTC's peer-to-peer connection mechanics correctly:
`RTCPeerConnection`/ICE/STUN/TURN establishment, SDP negotiation,
`RTCDataChannel` usage, and the mandatory DTLS-SRTP security model. The
transport-selection judgment (WebRTC vs. WebSocket vs. Socket.IO vs. SSE)
and the generic connection-lifecycle/scaling/handshake-auth framework belong
to the parent skill, [realtime-communication](../realtime-communication/SKILL.md)
(`SK-BE-004`) — this skill supplies what's structurally unique to WebRTC's
peer-to-peer model instead of repeating that comparison.

## When to use / When not to use

**Use** when a task integrates `RTCPeerConnection`,
`getUserMedia`/`getDisplayMedia` feeding a peer connection, or
`RTCDataChannel`, or names WebRTC mechanics (ICE, STUN, TURN, SDP,
peer-to-peer signaling, DTLS-SRTP). **Do not use** while the
peer-to-peer-vs-server-mediated transport choice is still open (route to
`SK-BE-004` first), for purely server-mediated realtime needs (route to
`socketio`/`websocket-api`), or for camera/mic capture UI alone with no
peer connection in play.

## Knowledge

**Signaling is explicitly out of scope of the WebRTC specification itself**
— applications choose any transport (WebSocket, XMPP, SIP, HTTPS polling,
"carrier pigeons" per MDN's own phrasing) to exchange SDP and ICE candidates
before a peer connection can complete
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime].
This is a structural difference from WebSocket/Socket.IO: WebRTC is
peer-to-peer *after* connection setup, but setup itself requires an
out-of-band channel the technology does not provide. The signaling server
is documented as intentionally a "black box" plain message router — it
doesn't need to understand SDP/ICE content, only route messages between
identified peers
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling].

**Connection establishment** [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity]:
(1) signaling exchanges an SDP **offer** from the initiating peer and an SDP
**answer** from the receiving peer, each set via
`setLocalDescription()`/`setRemoteDescription()`; (2) in parallel, the ICE
Agent gathers **candidates** — host, server-reflexive (`srflx`, via STUN),
peer-reflexive (`prflx`), and relay (via TURN) — and exchanges them,
optionally incrementally ("trickle ICE") over the same signaling channel;
(3) ICE selects a working candidate pair, with one peer as the
**controlling agent** (final pair selection) and the other **controlled**.
STUN alone is not sufficient in production: "a server is required for
relaying the traffic between peers, since a direct socket between clients is
often not possible"
[Source: https://webrtc.org/getting-started/turn-server] — TURN is a
baseline requirement, not an edge-case fallback.

**Perfect negotiation** is the officially documented pattern for offer/answer
negotiation and renegotiation, replacing ad hoc caller/callee-specific logic
that produces race conditions and "glare" collisions. Each peer is assigned
a role independent of call direction: **polite** (uses ICE rollback, drops
its own colliding offer in favor of an incoming one) or **impolite**
(ignores incoming offers that collide with one it's already sending) — this
lets both peers run identical negotiation code. Core state: `makingOffer`
(guards re-entrant offer creation) and `isSettingRemoteAnswerPending`,
combined with `signalingState === "stable"`, to detect an offer collision
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Perfect_negotiation].
`onnegotiationneeded` is the trigger point for calling `setLocalDescription()`
and sending the result over signaling, bracketed by `makingOffer` to avoid
glare (same source).

**SDP is a data format, not a transport protocol** — structured lines (RFC
8866) describing codecs, resolution, and encryption parameters, describing
session *content*, not how media is actually moved
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity].

**Plan B → Unified Plan SDP-semantics history (Chrome-specific, full
timeline)**
[Source: https://webrtc.org/getting-started/unified-plan-transition-guide]:
**M65** — Unified Plan available behind an experimental flag; **M69 /
September 2018** — Unified Plan generally available, but default was still
Plan B; **M72 / January 2019** — default switched to Unified Plan; **M93** —
Canary channel starts throwing on `sdpSemantics: "plan-b"`; **M96** — throws
across all channels including Stable, making `"plan-b"` effectively inert
everywhere. `sdpSemantics` is a legacy `RTCConfiguration` field; modern
Chrome supports only `"unified-plan"`
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API — see
Configuration note below]. **[Version-sensitive: Chrome-specific milestones
M65–M96; binding for all Chrome ≥M96.]** Practical breakage: apps that used
multiple audio or multiple video tracks on one `RTCPeerConnection` needed
retesting under Unified Plan, and interop where a non-Chrome endpoint offers
and Chrome answers could see a changed offer shape.

**ICE restart** is the documented recovery pattern for network changes
(Wi-Fi ↔ cellular, VPN toggling): on `iceConnectionState === "failed"`,
optionally call `setConfiguration()` with updated ICE server info, then
`pc.restartIce()`, which generates new ICE ufrag/password credentials; the
answering side auto-detects and follows the restart while media keeps
flowing on the prior connection until the new path is ready
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime].

**RTCDataChannel** is built on SCTP-over-DTLS. `createDataChannel(label,
options)` accepts `negotiated` (boolean; `false` default auto-negotiates the
channel, `true` requires both peers to create channels with a matching `id`
for manual/out-of-band negotiation) and `id`
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels].
`Unresolved: other commonly-known RTCDataChannelInit fields (ordered,
maxRetransmits, maxPacketLifeTime, protocol) were not present in the
specific MDN guide page this research drew from — verify against the
dedicated RTCDataChannel/createDataChannel reference pages before relying on
them.`

Deep signaling-flow/perfect-negotiation code walkthrough and the full
`RTCDataChannel` configuration reference live in
[references/signaling-and-negotiation.md](references/signaling-and-negotiation.md).

## Decision framework

1. **Is peer-to-peer actually required, given what it costs?** Choosing
   WebRTC over a server-mediated transport (`SK-BE-004`'s classification)
   commits you to two things a server-mediated transport avoids entirely:
   building/operating a signaling channel yourself (WebRTC provides none
   [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime]),
   and provisioning TURN relay infrastructure, since STUN alone won't
   traverse all real-world NAT/firewall combinations in production
   [Source: https://webrtc.org/getting-started/turn-server]. Reach for
   WebRTC only when true peer-to-peer (no server needing to see/process the
   media/data after setup) is an actual requirement — not merely because the
   feature "feels realtime."
2. **`iceTransportPolicy`: `"relay"` (always) vs. `"all"` (best-effort
   direct).** `"relay"` forces every connection through TURN — added
   latency and TURN bandwidth/operational cost at scale — but fully hides
   both peers' host/server-reflexive IP addresses from each other,
   mitigating the IP-exposure privacy concern the spec calls out explicitly
   [Source: https://www.w3.org/TR/webrtc/]. `"all"` (the default) permits a
   direct host/`srflx` connection when possible — lower latency, no TURN
   bandwidth cost for most connections — but exposes IP addresses to the
   remote peer. Choose `"relay"`-always when IP-privacy from the *other
   peer* is a hard requirement (e.g. anonymous chat, whistleblower/safety
   tooling); default to `"all"` otherwise, with TURN still present as the
   NAT-traversal fallback either way.
3. **Codec choice is a compatibility-vs-bandwidth trade-off**, not a single
   default: Opus (audio) plus VP8 or AVC/H.264 (video) are within the
   mandatory-to-implement set for maximum baseline compatibility; AV1/VP9
   are more bandwidth-efficient at equivalent quality but are
   version-gated (see Performance) and not universally available
   [Source: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs].
   Don't assume any codec beyond the mandatory set is available without
   checking the actual target browser/platform matrix.

## Workflow

1. Confirm or build the out-of-band signaling channel — WebRTC assumes one
   exists; it does not ship one
   [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling].
2. Construct `RTCPeerConnection` with `iceServers` covering both STUN and a
   real TURN relay, and an explicit `iceTransportPolicy` decision (Decision
   framework §2).
3. Implement perfect negotiation symmetrically on both peers: assign
   polite/impolite roles, guard `onnegotiationneeded` with `makingOffer`,
   and handle offer collisions via ICE rollback on the polite peer
   [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Perfect_negotiation].
4. Gather and exchange ICE candidates incrementally (trickle ICE) over the
   signaling channel rather than waiting for full gathering before sending
   the offer/answer
   [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity].
5. Handle `iceConnectionState === "failed"` with `setConfiguration()` +
   `restartIce()` rather than tearing down and rebuilding the connection.
6. If using a data channel, size messages moderately and wire up
   `bufferedamountlow` monitoring (see Performance) before shipping.
7. Verify against the checks below.

## Engineering rules

- Implement perfect negotiation (polite/impolite roles) for every
  bidirectional-renegotiation scenario; don't hand-roll asymmetric
  caller/callee-specific negotiation logic — the documented source of glare
  bugs.
- Always provision a real TURN relay alongside STUN; STUN-only
  configurations will fail to connect a meaningful fraction of real-world
  NAT combinations in production.
- Never point production traffic at public/shared STUN servers beyond
  testing — MDN's signaling guide explicitly cautions "use your own
  servers, not public ones."
- Treat `sdpSemantics: "plan-b"` as dead code in any Chrome-targeting
  deployment — it throws from M96 onward; if it's still present, that's a
  migration task, not a config knob.
- Keep `RTCDataChannel` messages moderately small; without message
  interleaving (RFC 8260), one large message on a channel can head-of-line
  block every other channel sharing the same SCTP association
  [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels].
- Make `iceTransportPolicy` an explicit, stated decision (Decision framework
  §2) rather than leaving the default unexamined when IP-privacy matters.

## Trade-offs

`iceTransportPolicy: "relay"` buys IP-address privacy from the remote peer
at the cost of latency and TURN bandwidth/operations spend on every call,
versus `"all"`'s better-performing but IP-exposing direct-connection
attempts. Mandatory-set codecs (Opus/VP8/H.264-CB) buy maximum baseline
compatibility at the cost of bandwidth efficiency versus AV1/VP9, which are
more efficient at equal quality but not available on every target browser
version — treat this as a real per-deployment choice, not a default to
"whichever is newest."

## Anti-patterns

- **Leaving `sdpSemantics: "plan-b"` code paths in a modern deployment** —
  broken (throws) on Chrome ≥M96; a real, historically significant breaking
  change, not a hypothetical one
  [Source: https://webrtc.org/getting-started/unified-plan-transition-guide].
- **Not setting `iceTransportPolicy: "relay"` when IP-privacy from the
  remote peer actually matters** — the default (`"all"`) exposes host/NAT-
  mapped addresses; this is a documented, actionable privacy control being
  left off by omission rather than by considered choice.
- **Oversized single data-channel messages** — causes head-of-line blocking
  across every channel sharing the SCTP association absent RFC 8260
  interleaving; "keep messages moderately small" is explicit guidance, not
  a suggestion.
- **Asymmetric caller/callee-specific negotiation logic** instead of perfect
  negotiation — the documented source of race conditions and glare
  collisions that the perfect-negotiation pattern was created to eliminate.
- **STUN-only NAT traversal with no TURN fallback** — will fail to connect a
  meaningful fraction of real NAT combinations in production; TURN
  deployment is a baseline requirement, not an edge-case optimization.

## Security

DTLS-SRTP is mandated for media transport with no plaintext mode available
at all; the spec requires **self-signed rather than PKI certificates**, so a
given certificate/key is not usable indefinitely, and certificates **must
not be expired at connection-creation time and must match the calling
document's origin**
[Source: https://www.w3.org/TR/webrtc/] — this is a cross-origin-reuse
constraint, not just a validity-window check. `RTCDataChannel` traffic is
automatically encrypted via DTLS, "providing the same security level as
HTTPS connections"
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels].

IP-address exposure to the remote endpoint is called out as a specific
privacy concern in the spec; `iceTransportPolicy: "relay"` is the documented
configuration-level mitigation, forcing the ICE Agent to use only
TURN-relayed candidates rather than host/server-reflexive addresses. "Impact
on local network" is its own distinct privacy consideration — the ICE Agent
is required to refuse to gather or connect to "administratively prohibited"
candidates
[Source: https://www.w3.org/TR/webrtc/]. Camera/microphone access itself is
governed by the separate Media Capture and Streams API's consent model,
referenced rather than redefined by WebRTC 1.0 (same source). Cross-cutting
threat modeling beyond this is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

`getStats()`/`RTCStatsReport` is the documented mechanism for real-time
performance telemetry — bitrate, loss, RTT, jitter, and candidate-pair
state, via type-specific reports (`RTCInboundRtpStreamStats`,
`RTCOutboundRtpStreamStats`, `RTCIceCandidatePairStats`, and related types)
[Source: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/getStats].
It has been "Widely Available (Baseline)" since September 2017; the
3-argument legacy callback form is deprecated (same source).

Outbound data-channel data is auto-buffered by the implementation; monitor
buffered amount via the `bufferedamountlow` event to avoid excess memory
use, and keep messages moderately small to avoid the head-of-line-blocking
risk described in Anti-patterns
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels].

Codec choice is a direct performance lever: AV1 and VP9 are named as more
bandwidth-efficient than VP8/H.264 at equivalent quality
[Source: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs].
**[Version-sensitive, point-in-time as captured 2026-09-09, re-check before
relying on it]**: AV1 support at Chrome 113+ and Firefox 136+; HEVC/H.265 at
Chrome 136+ (same source). Two further documented, browser/version-specific
codec gaps to account for when targeting older platforms: Firefox for
Android versions 68–72 lacked H.264 support "due to Google Play store
requirements," and Safari's VP8 support was only added at Safari 12.1+
(same source) — don't assume any codec beyond the mandatory Opus/VP8/
H.264-CB/G.711 set is universally available.

## Testing

CI/headless testing avoids real devices and manual permission prompts via
documented flags: Chrome — `--use-fake-ui-for-media-stream`,
`--use-file-for-fake-audio-capture`, `--use-file-for-fake-video-capture`,
`--headless`, `--mute-audio`, `--allow-file-access-from-files`; Firefox —
`media.navigator.streams.fake: true` and
`media.navigator.permission.disabled: true`
[Source: https://webrtc.org/getting-started/testing]. The W3C spec
references a Web Platform Tests (WPT)-based suite used to validate
conformance at Recommendation time — WPT is the spec's own official
cross-browser conformance mechanism
[Source: https://www.w3.org/TR/webrtc/]. Deep test-strategy method beyond
this WebRTC-specific CI setup is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If no out-of-band signaling transport exists yet, treat building one as
  an explicit task — WebRTC does not define signaling itself.
- If shell is unavailable or denied, degrade to advisory
  `RTCPeerConnection`/signaling code and configuration guidance, and state
  that no signaling server, TURN deployment, or headless test run was
  actually executed.
- If the target browser/platform matrix is unknown, don't assert codec-
  support or Plan-B/Unified-Plan-compatibility claims as universal — state
  the assumption or ask (rule VA-3).

## Escalation

- Deploying dedicated TURN infrastructure (self-hosted, e.g. coturn, vs. a
  managed provider) is a real cost/operations decision — present the
  trade-off and get explicit confirmation rather than provisioning
  unilaterally.
- Forcing `iceTransportPolicy: "relay"` for every connection trades
  reliability/latency and TURN bandwidth cost for IP-address privacy — a
  product-level decision, confirmed explicitly rather than defaulted either
  way.
- Legacy code still specifying `sdpSemantics: "plan-b"` is broken on modern
  Chrome — flagged for explicit migration confirmation, not silently
  patched around.

## Outputs & verification

- **Outputs:** peer-connection/signaling design (ICE server setup,
  `iceTransportPolicy` recommendation), `RTCPeerConnection`/data-channel
  implementation code, and analysis of codec/privacy trade-offs.
- **Verify:** perfect-negotiation state is implemented symmetrically for
  both peers, not asymmetric caller/callee logic; ICE-restart handling
  exists for the `failed` state; data-channel message sizing and
  `bufferedamountlow` monitoring are addressed when a data channel is used;
  every version-specific claim is tagged with the range it holds for.

## References

- [references/signaling-and-negotiation.md](references/signaling-and-negotiation.md) — Tier-2 signaling-flow walkthrough, perfect-negotiation state-machine detail, and the full `RTCDataChannel` configuration/limits reference.
- Source list: see `skill.yaml.source_references` (W3C/MDN/webrtc.org
  official docs, retrieved 2026-09-10, via `research/technologies/webrtc.md`).
- [research/technologies/webrtc.md](../../research/technologies/webrtc.md) — full primary research, including limitations and unresolved items.
- [realtime-communication/references/transport-comparison.md](../realtime-communication/references/transport-comparison.md) — the WebSocket-API-vs-Socket.IO-vs-WebRTC comparison this skill does not repeat.
