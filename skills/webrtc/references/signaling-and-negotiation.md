# Signaling flow, perfect negotiation, and data-channel limits (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Condensed from
[research/technologies/webrtc.md](../../../research/technologies/webrtc.md)
— consult that document for the full citation trail and caveats.

## Connection-establishment sequence

WebRTC does not define the signaling transport; the sequence below assumes
some out-of-band channel (WebSocket, HTTP, etc.) is already routing
application-defined JSON messages between two identified peers
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling].

1. **Offer.** Peer A calls `createOffer()` (or, in the perfect-negotiation
   pattern, `setLocalDescription()` with no explicit offer argument) and
   sends the resulting SDP to Peer B over signaling.
2. **Answer.** Peer B calls `setRemoteDescription()` with A's offer, then
   `createAnswer()`/`setLocalDescription()`, and sends its SDP answer back
   to A.
3. **Candidate gathering (parallel to 1–2).** Each peer's ICE Agent gathers
   candidates as they become available:
   - **host** — a local interface address.
   - **server-reflexive (`srflx`)** — the peer's public-facing address as
     seen by a STUN server.
   - **peer-reflexive (`prflx`)** — discovered during connectivity checks
     themselves.
   - **relay** — an address on a TURN server, used when no direct path
     works.
4. **Trickle ICE.** Candidates are sent to the remote peer incrementally via
   the `icecandidate` event rather than waiting for full gathering to
   complete before sending the offer/answer; `addIceCandidate()` accepts
   candidates that arrive after the initial exchange
   [Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity].
5. **Pair selection.** ICE selects a working candidate pair. One peer acts
   as the **controlling agent** (makes the final pair selection); the other
   is **controlled** (same source).

Signaling/negotiation states exposed on `RTCPeerConnection`:
`signalingState` (`stable`, `have-local-offer`, `have-remote-offer`,
`have-local-pranswer`, `have-remote-pranswer`) and `iceConnectionState`
(`new` → `checking` → `connected`/`completed`, or `disconnected`/`failed`)
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity].

## Perfect negotiation — state machine

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Perfect_negotiation]

Each peer is assigned a fixed role, independent of who happens to initiate
a given renegotiation:

- **Polite peer** — on an offer collision, rolls back its own local offer
  (`setLocalDescription({type: "rollback"})`) and accepts the incoming
  offer instead.
- **Impolite peer** — on an offer collision, ignores the incoming offer and
  lets its own offer proceed.

This symmetry means both peers can run *identical* negotiation code — no
caller/callee-specific branches.

Core guard state:

- `makingOffer` (boolean) — set `true` immediately before calling
  `setLocalDescription()` inside `onnegotiationneeded`, `false` once sent.
  Prevents a second, re-entrant offer from being created while one is
  already in flight.
- `isSettingRemoteAnswerPending` (boolean) — tracks whether the peer is
  mid-way through applying a remote answer.
- **Collision detection:** `offerCollision = description.type === "offer" &&
  (makingOffer || signalingState !== "stable")`. On collision, the polite
  peer rolls back; the impolite peer ignores the incoming offer.

Trigger point: `pc.onnegotiationneeded` fires whenever a local change (e.g.
adding a track) requires renegotiation. The handler calls
`setLocalDescription()` (no explicit offer argument in the modern pattern)
and sends the result over signaling, bracketed by `makingOffer` to avoid
glare.

The documentation frames the *pre*-perfect-negotiation approach — asymmetric
caller/callee-specific logic, ad hoc `signalingState` checks to decide who
should offer — as what perfect negotiation replaces: it produces race
conditions, "glare" collisions, and unnecessary asymmetric code paths.

## ICE restart

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime]

On network change (Wi-Fi ↔ cellular, VPN toggling), the documented recovery
pattern is:

1. Detect `iceConnectionState === "failed"`.
2. Optionally call `setConfiguration()` with updated ICE server info.
3. Call `pc.restartIce()` — generates new ICE ufrag/password credentials.
4. The answering side auto-detects and follows the restart via the normal
   offer/answer exchange; media continues flowing on the prior connection
   until the new path is ready, avoiding a hard drop.

## RTCDataChannel configuration and limits

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels]

`RTCPeerConnection.createDataChannel(label, options)` documented options:

| Option | Meaning |
|---|---|
| `negotiated` | `false` (default): WebRTC auto-negotiates the channel via in-band signaling. `true`: both peers must create channels with a matching `id` for manual/out-of-band negotiation. |
| `id` | Used to pair manually-negotiated channels when `negotiated: true`. |

`Unresolved: other commonly-known RTCDataChannelInit fields (ordered,
maxRetransmits, maxPacketLifeTime, protocol) were not present in the
specific MDN "Using data channels" guide page this research drew from —
verify directly against the RTCDataChannel/createDataChannel MDN reference
pages before relying on them.`

**Message-size limits**
[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels]:
the SDP `max-message-size` attribute (RFC 8841) governs the negotiated
maximum; absent an explicit value the default maximum is **64 KB**, while
"modern browsers" are documented as supporting at least **256 KB**. The
guide's own recommendation regardless of the negotiated ceiling: keep
messages "moderately small," because large messages can cause head-of-line
blocking across every data channel sharing the same underlying SCTP
association, absent RFC 8260 message interleaving.

**Encryption:** `RTCDataChannel` traffic is automatically encrypted via
DTLS, "providing the same security level as HTTPS connections" (same
source).

## Plan B → Unified Plan — practical breakage detail

[Source: https://webrtc.org/getting-started/unified-plan-transition-guide]

| Milestone | Event |
|---|---|
| Chrome M65 | Unified Plan available behind an experimental flag |
| Chrome M69 / Sept 2018 | Unified Plan generally available; default still Plan B |
| Chrome M72 / Jan 2019 | Default switched to Unified Plan |
| Chrome M93 | Canary channel throws on `sdpSemantics: "plan-b"` |
| Chrome M96 | Throws across all channels, including Stable |

Practical breakage for applications that hadn't migrated: apps using
multiple audio or multiple video tracks on a single `RTCPeerConnection`
needed retesting/adaptation under Unified Plan's multi-track SDP
representation; interop calls where a non-Chrome endpoint initiates the
offer and Chrome answers could see a changed offer shape. `sdpSemantics` is
now a legacy `RTCConfiguration` field — modern Chrome supports only
`"unified-plan"` and explicitly requesting `"plan-b"` throws rather than
silently falling back.

`Unresolved: Firefox shipped Unified-Plan-conformant behavior on its own
timeline per the same source page's framing, but was not itemized with
specific version numbers in the excerpt retrieved for this research pass.`
