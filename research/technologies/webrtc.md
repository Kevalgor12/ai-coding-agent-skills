# WebRTC — Technology Research

Research date: 2026-09-09. Primary sources checked: `w3.org/TR/webrtc/` (the W3C Recommendation, WebRTC 1.0), `w3c.github.io/webrtc-pc/` (living editor's draft), `developer.mozilla.org/en-US/docs/Web/API/WebRTC_API` and its sub-guides (Mozilla's official API reference/guide docs), `webrtc.org` (the project site backed by Google and the WebRTC native-code project), `webrtc.googlesource.com/src` and `github.com/webrtc` (canonical source repos), `firefox-source-docs.mozilla.org` and `blog.mozilla.org/webrtc` (Mozilla's own engineering docs/blog). All claims below use the citation convention: `[Source: <url>] <claim>.` for documented facts, `[Inference, not confirmed in docs]` for reasoning drawn from documented facts but not stated outright, `Unresolved: ...` where available official sources conflicted or were ambiguous, and `Not documented / could not verify` where no official source found covers it.

**Doc-host note:** [Source: https://webrtc.org/] The main webrtc.org site was redesigned; the fetched homepage carries a banner pointing to the previous version of the site, archived at `https://webrtc.github.io/webrtc-org/`. Both the current `webrtc.org` and the archived `webrtc.github.io/webrtc-org/` were used below since some getting-started/native-code pages were only confirmed reachable under the `webrtc.org` path structure (e.g. `webrtc.org/getting-started/...`) while native-code overview content was confirmed at the archived `webrtc.github.io/webrtc-org/native-code/` path. `Unresolved: it was not possible in this pass to fully confirm which of webrtc.org vs. the webrtc.github.io archive is considered canonical going forward, versus simply an old/new pair of the same GitHub-Pages-hosted site; both resolved and served real content at time of research.`

---

## 1. Core concepts

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API] WebRTC (Web Real-Time Communication) is a technology that lets web applications and sites capture and optionally stream audio and/or video media, and exchange arbitrary data between browsers, without requiring an intermediary or plugins.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API] WebRTC is not a single API but "several interrelated APIs and protocols which work together" to achieve this.

[Source: https://www.w3.org/TR/webrtc/] The core client-side interface is `RTCPeerConnection`, which manages a full peer-to-peer connection between the local browser and a remote peer, including establishment, monitoring, and closing.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API] Key building-block concepts: peer connections (`RTCPeerConnection`), media streams and tracks (`MediaStream`, `MediaStreamTrack`), data channels (`RTCDataChannel`) for arbitrary binary data, ICE (Interactive Connectivity Establishment) for NAT traversal, and SDP (Session Description Protocol) for negotiating session parameters.

[Source: https://webrtc.org/getting-started/overview] Two central technology areas are called out on the official getting-started overview: (1) media capture devices — cameras, microphones, and "screen capturing 'devices'" — accessed via `navigator.mediaDevices.getUserMedia()` and `getDisplayMedia()`; and (2) peer-to-peer connectivity via `RTCPeerConnection`, described as "the central point for establishing and controlling the connection between two peers."

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime] Signaling — the exchange of control messages, network/ICE candidate information, and media-capability negotiation needed to set up a session — is explicitly **not defined by the WebRTC specification itself**; applications are free to choose any transport (WebSocket, XMPP, SIP, HTTPS polling, etc.).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Protocols] SDP is a data format, not a transport protocol: "structured value" lines describing codecs, resolution, encryption parameters, etc., per RFC 8866; it describes the content of a session, not the media transport itself.

## 2. Architecture

[Source: https://www.w3.org/TR/webrtc/] Architecturally, WebRTC defines a browser-side JavaScript API layer (`RTCPeerConnection` and related interfaces) that sits atop a set of standard network/transport protocols (ICE/STUN/TURN for connectivity, DTLS for the secure channel, SRTP for encrypted media, SCTP for data channels) — see Section 3 (Protocols) below for the stack breakdown, which the W3C spec references normatively via IETF RFCs rather than reinventing.

[Source: https://webrtc.github.io/webrtc-org/native-code/] Separately from the browser-embedded implementation, there is a **WebRTC native code** C++ library (source at `webrtc.googlesource.com/src`) intended for "browser developers who want to integrate WebRTC" (i.e., browser vendors and native/mobile app developers), while the page explicitly states "application developers are encouraged to use the WebRTC API instead" (i.e., the browser JS API, not the native library directly).

[Inference, not confirmed in docs] Chrome, Firefox, and other browsers are widely understood to build on Google's native WebRTC C++ library or their own implementation of the same standards, but the fetched native-code overview page did not itself explicitly confirm which browsers embed that exact codebase — `Unresolved: the native-code page describes the library as being "for browser developers" but the excerpt retrieved did not state outright that Chrome/Firefox/Safari all embed it; this is treated as unconfirmed rather than assumed.`

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity] The connection-establishment architecture is: (1) signaling exchanges an SDP **offer** from the initiating peer and an SDP **answer** from the receiving peer, each set via `setLocalDescription()`/`setRemoteDescription()`; (2) in parallel, the ICE Agent gathers **candidates** (host, server-reflexive `srflx` via STUN, peer-reflexive `prflx`, and relay via TURN) and exchanges them (optionally incrementally, "trickle ICE") over the same signaling channel; (3) ICE selects a working candidate pair, one peer acting as the **controlling agent** (makes the final pair selection) and the other as **controlled**.

[Source: https://webrtc.org/getting-started/turn-server] Because a direct socket between clients is often not possible (NATs/firewalls), "a server is required for relaying the traffic between peers" — this is the TURN relay role, deployable via self-hosted software (e.g., coturn, named on the page) or a cloud/managed provider.

[Inference, not confirmed in docs] WebRTC's `RTCPeerConnection` architecture is inherently peer-to-peer (one connection object per remote peer); the official pages reviewed here (webrtc.org getting-started, MDN connectivity/session-lifetime guides) describe only the two-peer case and TURN-as-relay-for-media, and do **not** themselves document multi-party topologies (mesh, SFU, MCU) or provide server-side scaling architecture guidance — see Limitations (§14) for what is and is not documented on that point.

## 3. APIs

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API] Primary interfaces documented under the WebRTC API umbrella on MDN:
- Connection setup/management: `RTCPeerConnection`, `RTCSessionDescription`, `RTCIceCandidate`, `RTCRtpSender`/`RTCRtpReceiver`, `RTCRtpTransceiver`, `RTCStatsReport`, `RTCSctpTransport`.
- Data exchange: `RTCDataChannel`.
- Media: `MediaStream`, `MediaStreamTrack`, `MediaDevices.getUserMedia()` (from the related Media Capture and Streams API).
- Telephony: `RTCDTMFSender`, `RTCDTMFToneChangeEvent`.
- Encoded transforms (insertable streams): `RTCRtpScriptTransform`, `RTCEncodedVideoFrame`, `RTCEncodedAudioFrame`.
- Identity/security: `RTCCertificate`, `RTCIdentityAssertion`.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API] Key events across these interfaces: `icecandidate`, `track`, `datachannel`, `connectionstatechange`, `negotiationneeded`, plus on `RTCDataChannel`: `message`, `open`, `close`.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity] Signaling/negotiation states exposed on `RTCPeerConnection`: `signalingState` (`stable`, `have-local-offer`, `have-remote-offer`, `have-local-pranswer`, `have-remote-pranswer`) and `iceConnectionState` (`new` → `checking` → `connected`/`completed`, or `disconnected`/`failed`).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/getStats] `RTCPeerConnection.getStats([selector])` returns a `Promise<RTCStatsReport>` — a read-only Map-like object keyed by stat-object id — providing connection statistics; if `selector` (a `MediaStreamTrack`) is omitted/`null`, stats cover the whole connection. `[Source: same URL]` This has been "Widely Available (Baseline)" since September 2017 per the MDN compatibility data on that page. A 3-argument legacy callback form (`getStats(selector, successCallback, failureCallback)`) is marked deprecated on the same page. `RTCRtpSender.getStats()` and `RTCRtpReceiver.getStats()` provide the equivalent scoped-to-outgoing/incoming-traffic variants.

[Source: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs] `RTCRtpSender.getCapabilities("video"|"audio")` and `transceiver.setCodecPreferences()` are documented APIs for inspecting and reordering codec preferences on a per-transceiver basis.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime] `pc.restartIce()` plus `pc.setConfiguration()` is the documented API pattern for triggering an ICE restart (e.g., after a network change causes `iceConnectionState` to become `"failed"`), which generates new ICE ufrag/password credentials and lets the answering side auto-detect and follow the restart while media keeps flowing on the prior connection until the new path is ready.

[Source: https://www.w3.org/TR/webrtc/] The W3C Recommendation formally scopes the API surface into: peer-to-peer connections (configuration/state/`RTCPeerConnection`), the RTP media API (senders/receivers/transceivers/transport), peer-to-peer data channels (SCTP transport + `RTCDataChannel`), DTMF support, a statistics model, and privacy/security + accessibility considerations sections.

## 4. Configuration

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity] `RTCPeerConnection` is configured at construction via an `RTCConfiguration` dictionary, most commonly `iceServers` — an array of `{urls, username?, credential?}` objects for STUN and TURN endpoints, e.g.:
```javascript
const configuration = {
  iceServers: [
    { urls: ['stun:stun.l.google.com:19302', 'stun:stun1.l.google.com:19302'] },
    { urls: ['turn:your-turn-server.com:3478'], username: 'user', credential: 'pass' }
  ]
};
const peerConnection = new RTCPeerConnection(configuration);
```

[Source: https://www.w3.org/TR/webrtc/] `iceTransportPolicy` is a documented `RTCConfiguration` field; setting it to `"relay"` forces the ICE Agent to use only relay (TURN) candidates — a privacy-relevant setting (see §7 Security) that also affects connectivity behavior/cost.

[Source: https://webrtc.org/getting-started/unified-plan-transition-guide] `sdpSemantics` is (historically) a documented `RTCConfiguration` field (`"plan-b" | "unified-plan"`) controlling which SDP multi-track representation Chrome used; see §13 Breaking changes — as of the versions cited on that page, setting it to `"plan-b"` throws in current Chrome and the field is effectively legacy/inert for `"unified-plan"`, which is the only supported value in modern Chrome.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels] `RTCPeerConnection.createDataChannel(label, options)` configuration options documented include `negotiated` (boolean; `false` default lets WebRTC auto-negotiate the channel, `true` requires both peers to create channels with a matching `id` for manual/out-of-band negotiation) and `id` (used to pair manually-negotiated channels). `[Inference, not confirmed in docs]` Other commonly-known `RTCDataChannelInit` fields such as `ordered`, `maxRetransmits`, `maxPacketLifeTime`, and `protocol` are part of the broader WebRTC data channel model but were **not** present in the specific MDN guide excerpt fetched for this research pass — `Unresolved: confirm these fields directly on the RTCDataChannel/RTCDataChannelInit MDN reference pages rather than the "Using data channels" guide page, which is where this pass looked.`

[Source: https://webrtc.org/getting-started/testing] For automated/headless testing, Chrome supports launch flags `--use-fake-ui-for-media-stream`, `--use-file-for-fake-audio-capture` / `--use-file-for-fake-video-capture`, `--headless`, `--mute-audio`, and `--allow-file-access-from-files`; Firefox supports equivalent preferences `media.navigator.streams.fake: true` and `media.navigator.permission.disabled: true`, among cache/update-disabling prefs, to run without real devices or permission prompts.

## 5. Recommended patterns

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Perfect_negotiation] **Perfect negotiation** is the officially documented recommended pattern for handling offer/answer negotiation, including renegotiation. It assigns each peer a role independent of call direction: a **polite** peer, which uses ICE rollback and drops its own colliding offer in favor of an incoming one, and an **impolite** peer, which ignores incoming offers that collide with one it's already sending. This lets both peers run identical negotiation logic. Documented core state flags: `makingOffer` (guards against re-entrant offer creation) and `isSettingRemoteAnswerPending` (used together with `signalingState === "stable"` to detect an offer collision: `offerCollision = description.type === "offer" && !readyForOffer`).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Perfect_negotiation] `pc.onnegotiationneeded` is documented as the trigger point for calling `setLocalDescription()` (with no explicit offer argument, in the modern pattern) and sending the result through the signaling channel; a `makingOffer` boolean flag brackets this call to avoid glare.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity] **Trickle ICE** — sending ICE candidates to the remote peer incrementally as they're discovered via the `icecandidate` event, rather than waiting for full candidate gathering before sending the offer/answer — is documented as the way to speed up connection establishment; `addIceCandidate()` accepts candidates that arrive after the initial offer/answer exchange.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling] The signaling server is documented as intentionally a "black box" / plain message router — it need not understand SDP or ICE content, only route messages between identified peers (e.g., by `target`/`name` fields in application-defined JSON messages) — with the transport left up to the app (the guide's own words: "from WebSocket to fetch() to carrier pigeons").

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime] For network changes (e.g., Wi-Fi to cellular), the recommended pattern is: on `iceConnectionState === "failed"`, optionally call `setConfiguration()` with updated ICE server info, then call `restartIce()`; ongoing media continues on the existing connection until the restarted negotiation completes.

[Source: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs] Recommended codec choices per the compatibility notes on that page: Opus for audio (cited as offering superior quality/efficiency), and VP8 or AVC/H.264 for video for maximum baseline compatibility, since these plus Opus are within the mandatory-to-implement set (see §12 Version info).

## 6. Anti-patterns

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Perfect_negotiation] The documentation frames the *pre*-perfect-negotiation approach — asymmetric caller/callee-specific negotiation logic, and relying on ad hoc `signalingState` checks to decide who should offer — as the thing perfect negotiation replaces, implying it as an anti-pattern: it is described as producing race conditions, "glare" collisions, unnecessary complexity, and asymmetric code paths.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels] Sending very large single messages on a data channel is discouraged: "keep messages moderately small" is explicit guidance, because large messages without message interleaving (RFC 8260) can cause head-of-line blocking that hurts latency on other data channels sharing the same SCTP association.

[Source: https://webrtc.org/getting-started/turn-server] Relying only on public/shared STUN servers plus no TURN fallback is implicitly discouraged by the page's framing that "a server is required for relaying traffic ... since a direct socket is often not possible" — i.e., STUN-only configurations will fail to connect a meaningful fraction of real-world NAT combinations. `[Inference, not confirmed in docs]` The MDN signaling guide separately warns against using public STUN servers for anything beyond testing ("use your own servers, not public ones") — this is a documented caution, not merely inferred.

[Source: https://webrtc.org/getting-started/unified-plan-transition-guide] Continuing to depend on Plan-B-specific SDP munging/behavior is a now-broken anti-pattern in current Chrome — see §13.

## 7. Security

[Source: https://www.w3.org/TR/webrtc/] The specification's security/privacy considerations mandate DTLS-SRTP for media transport, and require the use of self-signed rather than PKI certificates so that a given certificate/key is not usable indefinitely; certificates must not be expired at connection-creation time and must match the document's origin.

[Source: https://www.w3.org/TR/webrtc/] IP-address exposure to the remote endpoint is called out as a specific privacy concern; the spec provides `iceTransportPolicy: "relay"` as a configuration-level mitigation, forcing the ICE Agent to use only TURN-relayed candidates rather than exposing host/server-reflexive (real or NAT-mapped) addresses.

[Source: https://www.w3.org/TR/webrtc/] "Impact on local network" is called out as its own distinct security/privacy consideration in the spec (i.e., WebRTC's local-network candidate gathering has recognized privacy implications), and the ICE Agent is required to refuse to gather or connect to "administratively prohibited" candidates.

[Source: https://www.w3.org/TR/webrtc/] Camera/microphone access itself is governed by the separate Media Capture and Streams API's permission model (user consent), which WebRTC 1.0 references rather than redefining.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels] `RTCDataChannel` traffic is automatically encrypted via DTLS, "providing the same security level as HTTPS connections" per the guide's own wording.

[Source: https://webrtc.org/getting-started/turn-server] TURN server credentials in the sample configuration are username/password (or time-limited token) based, provided as part of the `RTCConfiguration.iceServers` entries; the page does not itself detail credential-rotation or shared-secret (`use-auth-secret`)-style schemes — that level of TURN-server-side detail was not found on an official webrtc.org/W3C/MDN page in this pass. `Unresolved: TURN long-term vs. time-limited credential mechanisms (e.g., the REST API for TURN credentials, RFC 5766-adjacent practices) were referenced only by non-official third-party TURN-server (coturn) guides during this research, not by an official WebRTC doc; treated as not officially documented here rather than cited from those secondary sources.`

## 8. Performance

[Source: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/getStats] `getStats()` / `RTCStatsReport` is the documented mechanism for obtaining real-time performance telemetry (per-report `type`, `id`, `timestamp`, plus type-specific fields exposed via related MDN reference pages for `RTCInboundRtpStreamStats`, `RTCOutboundRtpStreamStats`, `RTCIceCandidatePairStats`, `RTCRemoteInboundRtpStreamStats`, `RTCRemoteOutboundRtpStreamStats`, `RTCPeerConnectionStats`, among others named on that page).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels] Data-channel performance guidance: outbound data is automatically buffered by the implementation; applications should monitor buffered amount and use the `bufferedamountlow` event to avoid over-buffering/using excessive memory, and keep messages moderately small (see §6) to avoid head-of-line blocking across channels.

[Source: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs] Minimum baseline media capability required unless otherwise signaled in SDP: video at minimum 320×240 at 20 FPS, and audio (Opus) across its full 6 kbps–510 kbps bit-rate range.

[Source: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs] Codec choice is presented as a performance lever: AV1 and VP9 are named as more bandwidth-efficient than VP8/H.264 at the same quality, with the page noting AV1 support at Chrome 113+ and Firefox 136+, and HEVC/H.265 at Chrome 136+. `[Version-sensitive: these per-browser version numbers reflect the state at the time the MDN page was captured in this research pass, 2026-09-09; MDN compatibility tables update continuously and should be re-checked for current values.]`

[Inference, not confirmed in docs] The mesh/SFU/MCU multi-party scaling trade-off (mesh topology degrading in CPU/bandwidth cost as participant count grows) is a widely-discussed WebRTC performance topic, but it was **not found documented on an official webrtc.org, W3C, or MDN page** in this research pass — see §14 Limitations. Numeric claims about "practical participant limits" for mesh/SFU/MCU circulating in secondary sources are excluded here per the no-fabrication rule.

## 9. Testing

[Source: https://webrtc.org/getting-started/testing] Official testing guidance (webrtc.org) is narrowly scoped to configuring headless/CI-friendly browser instances rather than to broader test methodology: Chrome flags (`--use-fake-ui-for-media-stream`, `--use-file-for-fake-audio-capture`, `--use-file-for-fake-video-capture`, `--headless`, `--mute-audio`, `--allow-file-access-from-files`) and Firefox prefs (`media.navigator.streams.fake: true`, `media.navigator.permission.disabled: true`, plus cache/update-disabling prefs) to run WebRTC code without real devices or manual permission grants.

[Source: https://www.w3.org/TR/webrtc/] The W3C spec references an implementation report and a Web Platform Tests (WPT) based test suite used to validate conformance at Recommendation time, confirming WPT as the spec's own official cross-browser conformance-testing mechanism. `[Inference, not confirmed in docs]` The exact WPT test directory path for WebRTC was not independently browsed in this pass.

[Not documented / could not verify] A dedicated official page equivalent to "test.webrtc.org" (a browser feature/connectivity test page sometimes referenced informally) was not confirmed as part of the current webrtc.org site during this pass — the official testing guidance found was limited to the CI/headless-flags content above.

## 10. Deployment

[Source: https://webrtc.org/getting-started/turn-server] Deploying a TURN relay server is documented as a required piece of production WebRTC infrastructure ("a server is required for relaying the traffic between peers, since a direct socket is often not possible"), with self-hosted (e.g., coturn, named on the page) and cloud/managed-service options both mentioned as valid deployment approaches, plus a code sample showing how to wire TURN hostname/port/username/credential into `RTCConfiguration`.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling] Signaling-server deployment is documented only at the pattern level (see §5) — a WebSocket-based Node.js example server is walked through, but production concerns (horizontal scaling of the signaling tier, authentication, presence) are not covered by that guide.

[Not documented / could not verify] Official guidance on deploying media servers (SFUs/MCUs) for group calling, load-balancing TURN clusters, or geographic TURN server placement was not found on webrtc.org, MDN, or the W3C spec in this research pass — these are client-API/protocol specs and a getting-started guide, not a deployment/operations manual, and no official document covering that operational layer was located.

## 11. Migration

[Source: https://webrtc.org/getting-started/unified-plan-transition-guide] The one migration webrtc.org documents in depth is the **Plan B → Unified Plan** SDP-semantics transition in Chrome (see §13 for the version timeline). Guidance: applications that used multiple audio or multiple video tracks on a single `RTCPeerConnection` needed to test under Unified Plan and adapt; interop calls where a non-Chrome endpoint initiates the offer and Chrome answers could see a changed offer shape. The guide points to separate JS-API and native/C++ migration documents for API-level specifics (not retrieved in full in this pass).

[Source: https://github.com/webrtc/adapter] `adapter.js` (the WebRTC-org GitHub org's shim) is documented as being for insulating applications from "spec changes and prefix differences" across browsers; the README states this specific `github.com/webrtc/adapter` repository is now a **"READ ONLY FORK"**, with active development having moved elsewhere (the README indicates the repo continues to receive updates reflecting new releases from the actively-maintained project, without this pass confirming the exact new canonical location beyond that it is distributed as the `webrtc-adapter` npm package). `Unresolved: the precise current canonical source repo for adapter.js/webrtc-adapter (vs. the now-read-only github.com/webrtc/adapter fork) was not conclusively identified from an official page in this pass.`

[Not documented / could not verify] Official migration guidance from comparable alternative real-time technologies (e.g., Flash/RTMP, or SIP-only telephony stacks) was not found on the primary WebRTC docs surfaces checked (webrtc.org, MDN, W3C spec) — those specs and guides describe WebRTC as it is, not migration paths onto it from other stacks.

## 12. Version information

[Source: https://www.w3.org/TR/webrtc/] The current specification status is **W3C Recommendation**, published **13 March 2025**, at the versioned URL `https://www.w3.org/TR/2025/REC-webrtc-20250313/`; the living editor's draft continues at `https://w3c.github.io/webrtc-pc/`.

[Source: https://www.w3.org/groups/wg/webrtc/] The maintaining body, the Web Real-Time Communications Working Group, is stated as "Chartered until 30 September 2026" as of the fetch date in this research pass. `[Version-sensitive / time-sensitive fact: this charter end date is fixed as documented, but W3C working group charters are commonly renewed; check the working-group page again after that date for renewal status.]`

[Source: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs] Mandatory-to-implement codecs per spec/browser-conformance as documented on this MDN page: video — VP8 and AVC/H.264 Constrained Baseline (CB) profile; audio — Opus and G.711 PCM (both A-law and µ-law). These are described as required across Chrome, Edge, Firefox, and Safari (with Safari's VP8 support noted as added at Safari 12.1+).

[Not documented / could not verify — but explicitly flagged for this project's version-tracking need] WebRTC (the API/spec) does not have an npm-style semantic "current stable version" the way a library does; it is a W3C Recommendation with a single publication date plus a continuously-updated editor's draft, and separately each browser has its own WebRTC feature/version rollout (e.g., Chrome M-numbers referenced throughout §13). There is no single "vX.Y.Z" version number to report for the specification as a whole beyond the Recommendation publication date above.

[Source: https://webrtc.org/getting-started/unified-plan-transition-guide] Chrome-specific version/rollout milestones for one major documented feature transition: M65 (Unified Plan behind an experimental flag), M69/Sept 2018 (feature generally available, default still Plan B), M72/Jan 2019 (default switched to Unified Plan), M93 (Canary starts throwing on `sdpSemantics: "plan-b"`), M96 (throws across all channels including Stable). `[Version-sensitive: these are Chrome-specific milestones, not spec-wide version numbers; Firefox shipped Unified Plan-conformant behavior on its own timeline per the same page's framing, not itemized with version numbers in the excerpt retrieved.]`

## 13. Breaking changes

[Source: https://webrtc.org/getting-started/unified-plan-transition-guide] The major documented breaking change in the WebRTC ecosystem's history is the Chrome **Plan B → Unified Plan** SDP-semantics switch (see version milestones in §12). Practical breakage: applications using multiple audio or multiple video tracks per `RTCPeerConnection` needed retesting/adaptation under Unified Plan; interop where a non-Chrome caller offers and Chrome answers could see the offer's SDP shape need to change; from Chrome M96 onward, explicitly requesting the old `sdpSemantics: "plan-b"` configuration value throws an exception rather than falling back silently.

[Inference, not confirmed in docs] Community/Chromium-project sources (a `blink-dev` "Intent to Deprecate: WebRTC's Plan B SDP semantics" mailing-list thread, surfaced via search but not independently fetched/verified as primary text in this pass) corroborate the same timeline; because that thread was not directly fetched and verified as primary source text here, it is not cited as a standalone claim — the webrtc.org transition guide fetched directly is the citation of record for §12/§13's Plan B/Unified Plan facts.

[Not documented / could not verify] A consolidated official "breaking changes" changelog analogous to a library's CHANGELOG.md was not found for the W3C spec itself (Recommendations don't carry that kind of changelog) nor for webrtc.org as a whole; browser-specific breaking changes (e.g., a given Chrome or Firefox release removing a WebRTC API) would need to be tracked via each browser's own release notes, which were out of scope for the pages fetched in this pass beyond the Unified Plan case above.

## 14. Limitations

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels] `RTCDataChannel` message size is explicitly limited: the SDP `max-message-size` attribute (RFC 8841) governs the negotiated maximum; absent an explicit value the default maximum is **64 KB**, while "modern browsers" are documented as supporting at least **256 KB**; the guide's own recommendation is to keep messages "moderately small" regardless, due to head-of-line blocking risk without message interleaving (RFC 8260).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime] The MDN "Lifetime of a WebRTC session" guide page is explicitly marked by MDN as **"under construction"**, with stated gaps including full connection-termination/closing procedure detail, complete renegotiation-process detail, scalability limits, and session-management best practices — i.e., MDN itself documents that its own coverage of session lifecycle/scalability is incomplete, rather than asserting there are no limits.

[Source: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs] Browser codec support is uneven and version-gated: e.g., Firefox for Android 68–72 lacked H.264 support "due to Google Play store requirements" per the page; AV1/VP9/HEVC support varies by browser and version as noted in §8/§12 — an application cannot assume any codec beyond the mandatory Opus/VP8/H.264-CB/G.711 set is universally available.

[Inference, not confirmed in docs] WebRTC's `RTCPeerConnection` model is fundamentally one-to-one (peer-to-peer); building group calls beyond a small number of participants is widely known to require either a full mesh of pairwise connections (with attendant CPU/bandwidth cost per added participant) or a server-side media relay/mixing component (SFU/MCU) that WebRTC itself does not define or ship. This general shape of the limitation follows from the documented one-peer-per-`RTCPeerConnection` API model (§2/§3), but **no official webrtc.org/W3C/MDN page fetched in this pass explicitly states a mesh/multi-party scaling limit or names SFU/MCU as the standard mitigation** — flagged as inference, not a documented claim, and any specific participant-count numbers should be treated as unverified.

[Source: https://www.w3.org/TR/webrtc/] Certificates used for DTLS must not be expired at connection-creation time and must match the calling document's origin — a documented constraint on long-lived, cross-origin certificate reuse.

## 15. Debugging

[Source: https://firefox-source-docs.mozilla.org/contributing/debugging/debugging_webrtc_calls.html] Firefox's official engineering docs describe `about:webrtc` as the central in-browser debugging surface, showing `RTCPeerConnection` creation parameters, connection/negotiation details, and RTP stream statistics; `about:support` supplements this with device/system info for bug reports. The page documents `MOZ_LOG`-based module logging (named modules include `jsep`, `sdp` for signaling; `mtransport`, `nicer` for networking; `RTCRtpReceiver`, `RTCRtpSender` for the JS-API layer; `MediaTrackGraph`, `cubeb` for media processing; `CamerasChild`, `CamerasParent`, `VideoEngine` for capture) and an `RtpLogger` module that can produce PCAP files for Wireshark inspection. Recommended workflow per the page: open `about:webrtc` during an active call, use the "Enable WebRTC Log Preset" button (or set `MOZ_LOG` directly), check RTT/jitter in the RTP stats, optionally capture a `profiler.firefox.com` performance profile with media settings enabled, and use "Copy Report"/"Copy Report History" to export JSON stats for bug reports.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/getStats] `getStats()`/`RTCStatsReport` (see §3/§8) is the underlying data source both `about:webrtc` and Chromium's `chrome://webrtc-internals` are built on, per the general documented purpose of the API (real-time connection statistics).

[Not documented / could not verify] A single official Chromium/Google documentation page specifically describing `chrome://webrtc-internals` was not located during this research pass (searches surfaced only third-party explainer articles, not an official chromium.org or webrtc.org reference page for that internal tool) — its existence and general function (per-`PeerConnection` SDP/stats/ICE-candidate-pair inspection, live bitrate/packet-loss/jitter graphs) is well corroborated across those secondary sources, but per this project's sourcing rule, no official citation is given for its specific documented behavior; it is noted here only as a known Chromium-side counterpart to Firefox's `about:webrtc`.

## 16. Integration

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling] WebRTC integrates with an application's own signaling transport of choice; the MDN guide's own worked example uses a WebSocket-based Node.js server relaying JSON messages (`video-offer`, `video-answer`, `new-ice-candidate`, `hang-up` message types shown), explicitly noting SIP/XMPP/third-party signaling services are alternative options but not detailing them in that guide.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API] WebRTC is documented as integrating with the separate **Media Capture and Streams API** (for `getUserMedia`/device capture feeding into `MediaStream`s attached to a peer connection), the **WebSocket API** (as one common signaling transport, per the guides), and **Web Workers**/`TransformStream` (for the Encoded Transforms / insertable-streams feature, letting encoded frame data be processed off the main thread).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels] `RTCDataChannel` is built on SCTP-over-DTLS per the protocol stack (§3/§7), letting it interoperate as an arbitrary binary/text data transport alongside the media transport on the same peer connection.

[Source: https://github.com/webrtc/adapter] `adapter.js`/`webrtc-adapter` is the documented official-org shim for smoothing over remaining cross-browser behavioral differences (historically also vendor-prefix differences, now largely gone) — i.e., it's the documented integration layer for writing one WebRTC codebase that runs across browsers, though see §11 for its current (read-only-fork) repository status.

## 17. Production considerations

[Source: https://www.w3.org/TR/webrtc/] Production deployments must provision DTLS-SRTP-compliant media transport (mandatory per spec — not optional/toggleable) and should decide on an explicit `iceTransportPolicy` (`all` vs `relay`) based on the IP-exposure/privacy trade-off documented in §7.

[Source: https://webrtc.org/getting-started/turn-server] Production deployments need a real TURN relay (self-hosted or managed) rather than STUN alone, since STUN cannot traverse all real-world NAT/firewall configurations — this is presented as a baseline requirement, not an edge-case optimization.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime] Networks change during a call (Wi-Fi ↔ cellular, VPN toggling, etc.); production apps are expected to listen for `iceConnectionState === "failed"` and drive an ICE restart (`setConfiguration()` + `restartIce()`) to recover without dropping the call.

[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Perfect_negotiation] Production negotiation logic should implement the perfect-negotiation pattern (§5) rather than ad hoc caller/callee-specific logic, to avoid glare-related call-setup failures under real-world timing (both peers renegotiating simultaneously, e.g., after both add a screen-share track at once).

[Source: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/getStats] Production monitoring/observability should be built on `getStats()`, since it is the only documented programmatic source of per-connection health data (bitrate, loss, RTT, jitter, candidate-pair state) available to application code.

[Not documented / could not verify] Official capacity-planning guidance (concurrent-call limits per TURN server instance, bandwidth budgeting formulas, or multi-region TURN/SFU topology recommendations) was not found in the official WebRTC docs surfaces reviewed; this is operational/infrastructure guidance that sits outside the scope of the client-side API spec and the introductory getting-started guides checked here.

---

## Summary of version-sensitive facts to track

| Fact | Version/date scope | Source |
|---|---|---|
| WebRTC 1.0 spec is a W3C Recommendation | Published 13 March 2025 | w3.org/TR/webrtc/ |
| WG charter | Chartered through 30 Sept 2026 (as observed 2026-09-09) | w3.org/groups/wg/webrtc/ |
| Unified Plan default in Chrome | Default since M72 (Jan 2019) | webrtc.org unified-plan-transition-guide |
| Plan B `sdpSemantics` throws | From M93 (Canary) / M96 (Stable, all channels) | webrtc.org unified-plan-transition-guide |
| Data channel default max message size | 64 KB default; ≥256 KB in "modern browsers" absent negotiation | MDN Using_data_channels |
| `getStats()` availability | Baseline/widely available since Sept 2017 | MDN RTCPeerConnection/getStats |
| AV1 video codec support | Chrome 113+, Firefox 136+ (as captured 2026-09-09) | MDN WebRTC_codecs |
| HEVC/H.265 support | Chrome 136+ (as captured 2026-09-09) | MDN WebRTC_codecs |
| Firefox Android H.264 gap | Firefox for Android versions 68–72 lacked H.264 | MDN WebRTC_codecs |
| Safari VP8 support | Added at Safari 12.1+ | MDN WebRTC_codecs |

## Unresolved items surfaced during this research

1. Whether `webrtc.org` (redesigned) or `webrtc.github.io/webrtc-org/` (archived) is the forward-canonical doc host, or whether they're simply old/new snapshots of the same GitHub Pages project — both served live content during this pass.
2. Whether Chrome/Firefox/Safari's browser-embedded WebRTC implementations are built directly on the `webrtc.googlesource.com/src` native code library — the native-code overview page describes the library's audience/purpose but the excerpt retrieved did not explicitly confirm browser embedding.
3. The current canonical source repository for `adapter.js`/`webrtc-adapter`, given `github.com/webrtc/adapter` is now marked a read-only fork.
4. `RTCDataChannelInit` fields beyond `negotiated`/`id` (i.e., `ordered`, `maxRetransmits`, `maxPacketLifeTime`, `protocol`) were not present in the specific MDN guide page fetched and should be verified against the dedicated `RTCDataChannel`/`createDataChannel()` MDN reference pages.
5. TURN server credential-rotation mechanisms (e.g., time-limited/shared-secret schemes) — not found documented on an official WebRTC page in this pass.
6. Mesh/SFU/MCU multi-party scaling guidance and any official participant-count limits — not found on an official WebRTC page in this pass; treated purely as inference from the one-peer-per-`RTCPeerConnection` API model.
7. Whether there is a current official page equivalent to a "test.webrtc.org" browser capability/connectivity test tool.
8. No official standalone documentation page for `chrome://webrtc-internals` was located (Chromium/Google side); only Firefox's `about:webrtc` had an official Mozilla source-docs page.
