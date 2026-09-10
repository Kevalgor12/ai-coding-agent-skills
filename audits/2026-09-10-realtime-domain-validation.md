# Audit: REALTIME-domain skill generation & validation

Date: 2026-09-10. Scope: five skills — one generic (`SK-BE-004`
realtime-communication) and four technology skills (`SK-TECH-threejs`,
`SK-TECH-websocket-api`, `SK-TECH-socketio`, `SK-TECH-webrtc`). Validated
against [skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).

**Scope note:** the user's 6-item list ("Three.js, Realtime Architecture,
WebSocket, Socket.IO, WebRTC, Event-Driven Architecture") maps to 5 skills,
not 6 — **Event-Driven Architecture does not exist in the taxonomy**, and is
an explicitly documented research gap (`taxonomy-analysis.md`: "No skill
yet; add a research pass if the library should cover event-driven/queue
architectures" — no message-broker technology beyond Redis's pub/sub role
inside Socket.IO has been researched). Surfaced via `AskUserQuestion` rather
than guessed at or silently dropped; the user chose "Generate the 5 now,
hold EDA" — the same treatment given to the Node.js gap in the BACKEND
batch, but scoped to just the one missing item rather than holding the
whole batch, since the other 5 items mapped cleanly to existing catalog
entries.

**Authorship note:** as with all four prior batches, the generic skill was
authored directly by hand; the four technology skills were delegated to
parallel agents with pre-verified relationship data (`parents`,
`conflicts_with`, `related_skills`) and pre-verified version/security/
performance facts pulled from `version-matrix.md`/
`technology-decision-matrix.md §6`/`security-knowledge-map.md`/
`performance-knowledge-map.md`, then independently re-verified on disk (not
trusted from self-reports).

## Completed skills

| Skill | ID | Tier | Files | Citations in SKILL.md |
|---|---|---|---|---|
| [realtime-communication](../skills/realtime-communication/) | SK-BE-004 | A | yaml, SKILL.md, 1 reference | 6 |
| [threejs](../skills/threejs/) | SK-TECH-threejs | A | yaml, SKILL.md, 1 reference | 27 |
| [websocket-api](../skills/websocket-api/) | SK-TECH-websocket-api | B | yaml, SKILL.md, 1 reference | 38 |
| [socketio](../skills/socketio/) | SK-TECH-socketio | B | yaml, SKILL.md, 1 reference | 33 |
| [webrtc](../skills/webrtc/) | SK-TECH-webrtc | B | yaml, SKILL.md, 1 reference | 27 |

All five independently confirmed on disk (file existence, line counts,
directory contents) — not accepted from agent self-reports alone.

**Mechanical checks run and passed, all five (scripted, not manual):**
- YAML validity for all 5 `skill.yaml` files.
- VR-1 (all always-required fields present) and technology-conditional
  fields (`parents`, `covered_versions`, `version_sensitive_claims`,
  `reverify_triggers`) present for all 4 technology skills.
- CE-1 (description ≤ 500 chars) — range 389–498; `threejs` (492) and
  `webrtc` (498) landed close to the ceiling, compliant but a repeat of the
  FRONTEND batch's note to leave more headroom in future prompts.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically for all 5, zero mismatches.
- **`depends_on_skills`-vs-`parents` conflation: zero recurrence**, the
  third consecutive batch (after BACKEND and FRONTEND) where every
  technology skill correctly left `depends_on_skills: []` with
  specialization captured only in `parents`.
- VR-3 (every `parents`/`related_skills`/`conflicts_with` ID resolves to a
  real taxonomy entry) — all resolve cleanly, no defects found this time
  (unlike FRONTEND, which surfaced and required fixing one pre-existing
  taxonomy-table inconsistency).
- Conflict-cluster check: **no `conflicts_with` entries at all in this
  batch**, which is itself a deliberate, research-grounded finding, not an
  omission — see "Notably different from prior batches" below.
- `execution_tier`/`required_capabilities` consistency: 2 Tier A skills
  (realtime-communication, threejs — both authoring/design-level work with
  no fundamental shell dependency) and 3 Tier B skills (websocket-api,
  socketio, webrtc — each implies a runtime/signaling-server component).
- All relative links resolve.

### Notably different from prior batches: no conflicts declared

Every prior batch (FRONTEND's React/Vue/Angular triangle, Next.js/Nuxt,
MUI/shadcn-ui) had genuine `conflicts_with` pairs — mutually-exclusive
choices for the same architectural slot. This batch has **none**, and that
is a correct reflection of the research, not a gap:

- Socket.IO is *built on top of* WebSocket as one of its transports (its
  own docs: "not a raw WebSocket implementation") — choosing it doesn't
  preclude WebSocket-protocol usage underneath, unlike React vs. Vue's true
  mutual exclusion as base frameworks.
- WebRTC "carries no recorded `alternativesTo`" per
  `technology-decision-matrix.md §6` — it's grouped with the other two only
  because it shares the "realtime-networking" category, not because any
  source frames it as competing with WebSocket/Socket.IO. It solves a
  structurally different problem (peer-to-peer media/data vs.
  server-mediated events).
- Three.js is the *only* 3D-graphics technology actually profiled in this
  library's research (`technology-decision-matrix.md §12`) — Babylon.js/
  PlayCanvas are named only via the absence of an official
  "migrating from" guide, not as documented alternatives, so declaring a
  conflict would have been fabricated.

This is the batch where the "when in doubt, don't invent a conflict" rule
established across prior audits was tested against real cases that *look*
like they should conflict (three realtime transports side by side) but
don't per the actual source material — and every agent correctly held the
line.

## Unresolved questions

1. **Three.js: no official cross-origin texture/asset-loading security
   guidance** (`crossOrigin` handling on loaders, canvas tainting, CSP for
   WebGL/WebGPU contexts) — flagged as a documentation gap in the source
   research and correctly marked "Unresolved" rather than papered over.
2. **Three.js: no official first-party guide for application developers**
   (as opposed to Three.js's own contributors) to unit- or
   visual-regression-test their own Three.js apps — stated as a real gap.
3. **WebSocket API: no official rate-limiting algorithm/threshold, no
   official max message/frame size, and no official unit/integration test
   framework or conformance suite for consumers** — all three correctly
   stated as documented gaps rather than invented defaults.
4. **WebRTC: other `RTCDataChannelInit` fields** (`ordered`,
   `maxRetransmits`, `maxPacketLifeTime`, `protocol`) weren't independently
   confirmed against the specific MDN guide page used — flagged to verify
   against the dedicated reference pages before relying on them.
5. **WebRTC: Firefox's Unified Plan rollout wasn't itemized with version
   numbers** in the source research (only Chrome's full M65→M96 timeline
   was) — stated as a gap rather than backfilled with an unverified guess.

None of these five were load-bearing enough to block any skill — each is a
correctly-surfaced boundary of current research.

## Duplicated responsibilities

**None found at the engineering-content level**, and this batch's structure
made the risk unusually concentrated (three sibling technology skills all
specializing the same generic parent's transport-comparison table):

- `websocket-api`, `socketio`, and `webrtc` all explicitly declined to
  repeat `realtime-communication`'s existing WebSocket-vs-Socket.IO-vs-
  WebRTC comparison table (CORS/Origin scope, masking-vs-DTLS-SRTP,
  backpressure, compression trade-offs, official testing support) and its
  connection-lifecycle/scaling/handshake-auth decision framework, instead
  adding only technology-specific implementation depth (handshake/close-code
  mechanics for WebSocket; namespaces/rooms/middleware for Socket.IO;
  ICE/STUN/TURN/signaling for WebRTC).
- `socketio` explicitly deferred to `realtime-communication`'s existing
  Redis-adapter anti-pattern note (silent degrade-to-local-only) rather
  than restating it, adding only the adapter-selection decision (Redis vs.
  MongoDB vs. PostgreSQL, keyed on `connectionStateRecovery` support) that
  the parent didn't cover.
- `threejs` has no sibling in this batch to duplicate against; it correctly
  avoided restating `frontend-architecture`'s generic framework-selection
  content, which doesn't apply to it anyway.

## Missing dependencies

- `threejs`'s only formal parent (`SK-FE-001` frontend-architecture) is
  already authored — no forward reference needed.
- `websocket-api`, `socketio`, and `webrtc` all forward-reference
  `SK-BE-004` (realtime-communication) — but that parent was authored
  *within this same batch*, by hand, before the technology skills were
  delegated, so in practice all three technology skills' formal parent
  already existed by the time they were authored.
- `realtime-communication` itself (the generic) references `SK-BE-001`,
  `SK-BE-002` (both already authored) and `SK-TECH-redis` (already
  authored, from the DATA-domain batch) in `related_skills` — no
  unauthored forward references from the generic skill either.

**This is the first batch where zero skills carry an unauthored forward
reference at authoring time** — a byproduct of generating the generic
parent by hand first, in the same session, rather than across batches.

## Potential corrections

1. **The `depends_on_skills`-vs-`parents` fix continues to hold with zero
   recurrence** across all 4 technology skills in this batch — the third
   consecutive batch confirming this. No further spec action needed.
2. **The "don't invent a conflict" discipline held under a harder test than
   prior batches** — three realtime transports that superficially look like
   alternatives, correctly resolved to zero `conflicts_with` entries based
   on what the research actually documents (see "Notably different from
   prior batches" above). Worth citing as a template for future batches
   where technologies *appear* to compete but the research doesn't actually
   frame them that way.
3. **Two skills' descriptions landed within 8 characters of the 500-char
   CE-1 ceiling** (threejs 492, webrtc 498) — same standing note as the
   FRONTEND batch; future prompts could ask for a lower target ceiling.
4. **No skill in this batch was promoted to `final/`** — same standing gap
   as all four prior batches (no executable validator or `evaluations/`
   tests yet).
5. **Event-Driven Architecture remains an open, deferred item** — not
   generated, not dropped. Per the user's choice, it awaits a dedicated
   research pass (message-broker technologies: Kafka, RabbitMQ, SQS, or
   similar) and a taxonomy addition before it can be authored as a skill,
   following the same procedure documented in the BACKEND-domain audit for
   the Node.js gap.

## Overall assessment

All five skills are internally consistent with the specification, taxonomy,
dependency architecture, and routing architecture, well-grounded (6–38
citations per skill, with the generic intentionally lighter since its
content is decision-framework/synthesis-heavy rather than citation-dense),
and version-aware — including several genuinely load-bearing findings
correctly surfaced: Three.js's non-semver r-number release scheme (a real
risk for any version-compatibility tooling that assumes semver-shaped
strings) alongside its single largest breaking change (the r152+
color-management overhaul) and its 90-day-private-disclosure-only security
policy; the raw WebSocket API's complete absence of an official testing
story and its Node.js client-only/no-built-in-server gap; Socket.IO's
server-only 3.x→4.0 breaking-change boundary (clients stay protocol-
compatible across it) and its documented Redis-adapter silent-degrade
failure mode; and WebRTC's full Plan-B-to-Unified-Plan Chrome transition
history alongside its architecturally-mandatory DTLS-SRTP encryption. The
batch also cleanly demonstrated two patterns worth carrying forward: (1)
surfacing a taxonomy gap (Event-Driven Architecture) via `AskUserQuestion`
rather than guessing, scoped this time to holding only the missing item
rather than the whole batch, since the other five items were unambiguous;
and (2) correctly declining to manufacture `conflicts_with` relationships
among technologies that are thematically adjacent but not actually
documented as mutually exclusive.
