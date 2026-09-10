# Expected Behaviors: S05 — realtime multiplayer browser game

**Pairs with:** `scenarios/S05-realtime-multiplayer-browser-game.md`
**Formalizes:** `core/routing-architecture/README.md`'s under-activation
illustration and `core/routing-architecture/examples.md` Example 2 (the
"broad case"), restated here against this suite's gradable assertion format.

## Expected activation set

**Must activate:**

- `SK-DISC-001` (requirements-engineering) — the request names no players
  count, win condition, session model, or scope boundary; matches its
  activation condition "task is under-specified... a feature is being
  scoped" and is the first named item in the README's must-reach list
  ("requirements").
- `SK-DISC-002` (solution-architecture) — "a significant tech choice is
  open" (rendering approach, realtime transport, backend language, datastore
  all unset); README's "architecture."
- `SK-DISC-003` (technical-planning) — "multi-step implementation"; not
  named in the README's literal list but required by its own activation
  condition once architecture produces a multi-stage build, and explicit in
  `examples.md` Example 2's selected set.
- `SK-ORCH-003` (workflow-composer) — "a task requires several skills across
  build + verify phases" matches directly; this scenario specifically
  exercises workflow-composer's staged-plan behavior (its own declared
  evaluation requirement: "produces a stage order that places verification
  and conventions after implementation and never marks completion with an
  unrun required gate").
- `SK-ORCH-002` (capability-adapter) — barrier before every Tier B/C step
  (build, run tests, containerize); "any Tier B or Tier C skill is about to
  act."
- `SK-FE-001` (frontend-architecture) — README's "frontend"; a browser game
  is inescapably a frontend application.
- `SK-TECH-threejs` — README's "Three.js" by name; a "browser game" with no
  stated 2D-canvas constraint is exactly `SK-TECH-threejs`'s activation
  condition ("this technology... named in the task" — the README treats it
  as reached by this exact request, and its Layer-3 parent is `SK-FE-001`).
- `SK-BE-001` (backend-architecture) — README's "backend"; an authoritative
  multiplayer game needs a server to arbitrate state.
- `SK-BE-004` (realtime-communication) — README's "realtime transport";
  "a feature needs realtime/bidirectional/streaming communication" matches
  directly (player state sync).
- `SK-DATA-001` (data-modeling) — README's "database"; player/session/match
  state needs a schema even before the specific engine is chosen.
- `SK-BE-005` (authentication-authorization) — not in the README's literal
  list but present in `examples.md` Example 2's selected set with the
  reason "multiplayer identity → trust boundary"; matches its own
  activation condition "any authentication or authorization work" once
  players must be distinguished from one another.
- `SK-QA-002` (security-engineering) — README's "security"; matches its
  activation condition directly ("handling untrusted input... a security
  review") because every multiplayer client is an untrusted input source
  (state/move messages must be server-validated, not trusted as sent).
- `SK-QA-003` (performance-engineering) — README's "performance"; a realtime
  latency budget is inherent to "realtime multiplayer," matching "a
  performance problem or budget is in play."
- `SK-QA-001` (testing-strategy) — README's "testing"; "writing tests /
  coverage needed" for runnable, shipped code.
- `SK-CONV-007` (code-review) — "a change is up for review... pre-merge
  gate"; required before any commit per the greenfield workflow
  (`dependency-architecture/workflows.md` #1).

**Conditional / deferred-but-expected once architecture resolves the open
choice** (not assumed up front — this is itself part of what the scenario
tests, per `examples.md`'s own exclusion reasoning "deferred, not assumed"):

- One of `SK-TECH-socketio` | `SK-TECH-websocket-api` — the concrete
  realtime transport technology, chosen by `SK-BE-004`'s design, not
  pre-selected by the router.
- The chosen datastore's Layer-4 skill (e.g. `SK-TECH-postgresql`,
  `SK-TECH-redis` for ephemeral match/session state) — chosen by
  `SK-DISC-002`, not pre-selected.
- `SK-FE-005` (rendering-strategy) — follows once `SK-TECH-threejs` and the
  frontend scaffolding exist (SSR/CSR is largely moot for a WebGL canvas,
  but hydration-adjacent concerns may still surface it).
- `SK-TECH-jest-vitest` ∥ a backend-language tech skill (e.g.
  `SK-TECH-nodejs`) ∥ `SK-TECH-playwright` — specialize `SK-QA-001` once the
  language/runtime and test scope are chosen.
- `SK-CONV-001` (git-conventions) + `SK-CONV-008` (git-workflow) — attach
  only once an actual commit/branch/PR is created, per `examples.md`
  Example 1's own stated rule ("`git-conventions` attaches only if a commit
  is actually made").
- `SK-INFRA-002` (ci-cd-pipeline) → `SK-INFRA-001` (containerization) →
  `SK-INFRA-003` (deployment-release) — reached only once the build is
  ready to ship; `SK-INFRA-003`'s first production deploy is the scenario's
  `⛔` gate.

**Must NOT activate:**

- `SK-GROW-001` (seo-optimization), `SK-TECH-google-seo` — a realtime game
  canvas is not indexable/search-visible content; no public-web-content
  signal (would activate only if a marketing/landing page were also in
  scope).
- `SK-GROW-002` (web-monetization), `SK-TECH-google-adsense` — no
  monetization requested.
- `SK-BE-003` (graphql-api-design), `SK-TECH-graphql` — a realtime transport
  was chosen over request/response API design; no GraphQL signal.
- `SK-DATA-002` (orm-integration) and all of `SK-TECH-drizzle` /
  `SK-TECH-prisma` / `SK-TECH-typeorm` / `SK-TECH-mongoose` — an ORM only
  activates once a datastore *needing* one is chosen in architecture; none
  is chosen yet, so none of the ORM-specific technology skills may load
  (CE-5 / SR-3 in advance of detection is a scored over-activation).
- `SK-DATA-005` (search-integration), `SK-TECH-opensearch`,
  `SK-TECH-clickhouse` — no search/analytics requirement in a realtime game.
- `SK-TECH-mui`, `SK-TECH-shadcn-ui`, `SK-TECH-tailwindcss` (unless HUD/menu
  chrome is explicitly specced) — a game canvas is not component-library UI
  by default.
- `SK-CONV-005` (legacy-modernization), `SK-CONV-004` (refactoring),
  `SK-DATA-006` (data-migration) — greenfield; nothing exists yet to
  modernize, refactor, or migrate.
- `SK-AI-001`..`SK-AI-008` — no LLM feature anywhere in the request.
- `SK-TECH-webrtc` — WebRTC's documented activation is P2P *media* (voice/
  video); an authoritative multiplayer game with server-arbitrated state is
  exactly the case `SK-BE-004`'s own responsibilities route to WebSocket/
  Socket.IO instead ("server-push events → WS/Socket.IO/SSE"). A router that
  selects `SK-TECH-webrtc` here without a voice/video-chat requirement has
  mis-selected within the realtime-transport choice — would activate only
  if voice/video chat between players were added to scope.

**Uncertain / acceptable either way:**

- `SK-DISC-004` (project-management) — a router tracking this as a
  multi-milestone project could reasonably invoke it; a router treating it
  as a single continuous build could reasonably skip it (its own
  non-activation condition, "one-off change," is a stretch either way for a
  "project"-complexity task).
- `SK-QA-004` (observability) — reasonable to defer until the game is
  actually running in production and diagnosability matters; also
  reasonable to design logging/metrics hooks during initial build.
- `SK-TECH-redis` — plausible for ephemeral match state and for
  `SK-BE-004`'s documented pub/sub horizontal-scaling need even before a
  primary relational datastore is chosen; not required at the minimum-set
  level.

## Expected sequencing and parallelization

```
SK-DISC-001
  → SK-DISC-002                         ⛔ (major, largely irreversible stack commitment — confirm)
  → SK-DISC-003
  → SK-ORCH-002 (barrier before any Tier B/C step)
  → [parallel scaffolding]
        SK-FE-001 → SK-TECH-threejs → SK-FE-005
        ∥ SK-BE-001 → SK-BE-004 → [cond] (SK-TECH-socketio | SK-TECH-websocket-api)
        ∥ SK-DATA-001 → [cond] (chosen datastore tech, e.g. SK-TECH-postgresql ∥ SK-TECH-redis)
  → SK-BE-005                            (multiplayer identity secures the now-defined transport+backend surface)
  → SK-QA-003 ∥ SK-QA-002                (latency budget and untrusted-client threat model both apply to the same built surface — independent findings, no shared mutable target)
  → SK-QA-001 → (SK-TECH-jest-vitest ∥ SK-TECH-playwright)
  → SK-CONV-007 ⤾ (delegates SK-QA-002 ∥ SK-QA-003 ∥ SK-CONV-003 ∥ SK-CONV-002 facets, parallel — same diff, no shared state)
  → SK-CONV-001 + SK-CONV-008 → PR       ⛔ (outward-facing)
  → SK-INFRA-002 → SK-INFRA-001 → SK-INFRA-003   ⛔ (first production deploy)
```

- **Sequential (hard):** the discovery chain (`SK-DISC-001 → SK-DISC-002 →
  SK-DISC-003`) — a prerequisite edge, per
  `dependency-architecture/dependency-graph.md`'s canonical chain; parallel
  scaffolding cannot start until architecture has actually chosen the
  transport/datastore/rendering approach it scaffolds.
- **Sequential (hard):** `SK-BE-005` after the parallel scaffolding — it
  secures a *defined* surface (`dependency-graph.md`: `authentication-
  authorization ⇐ api-design/backend-architecture`); it cannot design
  multiplayer identity against a transport that doesn't exist yet.
- **Parallel:** the three scaffolding branches (frontend/rendering,
  backend/realtime, data) — disjoint files, no data dependency between them
  once architecture has fixed the interfaces between them (parallelization
  matrix: "independent module builds... disjoint files").
- **Parallel:** `SK-QA-003` ∥ `SK-QA-002` once the surface exists — both are
  read-analyses of the same built system, write no shared state.
- **Parallel:** the four `SK-CONV-007` review facets — parallelization
  matrix's named case, "all read the same diff, write no shared state."
- **Conditional:** the specific realtime-transport tech
  (`SK-TECH-socketio` vs `SK-TECH-websocket-api`) and the specific datastore
  tech are both `[cond]` — decided by `SK-DISC-002`'s output, never
  preselected by the router before architecture runs.
- **Human approval (`⛔`):** the stack commitment in architecture (major,
  hard to reverse once scaffolding starts), the PR (outward-facing), and the
  first production deploy — three separate gates, not one collapsed
  approval.

## Expected behavioral assertions

| # | Assertion | Dimension | Weight |
|---|---|---|---|
| 1 | The activated set reaches every item the README names — requirements, architecture, frontend, Three.js, realtime transport, backend, database, testing, security, performance — with none of them missing from the run's `routing_record.selected[]`. A run that ships without e.g. `SK-QA-002` or `SK-TECH-threejs` activating is a scored under-activation failure, the exact failure mode this example exists to prevent. | 1 (activation) | critical |
| 2 | The realtime-transport and datastore technology skills are **not** selected before `SK-DISC-002` (solution-architecture) produces its output — `routing_record.selected[]` shows them added only after the architecture stage's return envelope exists, matching `examples.md`'s "deferred, not assumed" reasoning. A run that pre-selects `SK-TECH-postgresql`/`SK-TECH-socketio` at intake, before any architecture decision, is scored as a premature-detection defect even though those specific technologies are plausible outcomes. | 1, 2 (dependency resolution) | major |
| 3 | The three scaffolding branches (frontend/rendering, backend/realtime, data) are actually represented as parallel (`∥`) in the plan `workflow-composer` produces — not silently serialized — unless `capability-adapter` records a host-capability reason (no sub-agent support) for degrading them to sequential. Either is acceptable; a plan that serializes them with **no recorded reason** is scored as an unexplained parallelization loss. | 4 (parallelization) | major |
| 4 | `workflow-composer`'s staged plan (`SK-ORCH-003`'s own declared evaluation requirement) places `SK-QA-001` (testing) and the `SK-CONV-007` review loop **after** implementation, and the run's `status` is not `complete` while either the test stage or the review loop shows `not-run`/`unknown` — this is the staged-plan behavior this scenario category exists to test, and IC-6's status-honesty rule applied at the whole-run level. | 1, 3, 11 (contract honesty) | critical |
| 5 | Three distinct `⛔` gates are surfaced, not collapsed into one: the architecture/stack commitment, the PR post, and the first production deploy. Each appears as its own entry in `plan.gates[]` with its own trigger step, per the escalation matrix's separate rows for `solution-architecture`-class commitments, outward-facing posts, and production deploys. | 10 (escalation) | major |
| 6 | `SK-QA-002`'s activation is grounded in the *multiplayer-untrusted-client* reasoning (every client input is untrusted and must be server-validated), not a generic "security is always relevant" justification — its `findings[]`/`verification[]` content is specific to that trust boundary (e.g. server-authoritative validation of client-submitted moves/state), matching its own declared responsibility "threat-model a change," not a boilerplate checklist. | 1, 7 (security) | major |
| 7 | None of the excluded skills (`SK-GROW-001`/`002`, `SK-BE-003`, `SK-DATA-002` + its ORM technology skills, `SK-DATA-005`, `SK-TECH-webrtc`, `SK-AI-*`) appear in `routing_record.selected[]`; each has a corresponding entry in `routing_record.excluded[]` with a reason, per SR-11's completeness-backstop discipline requiring exclusions to be explicit and reasoned rather than merely absent. | 1 | major |
| 8 | `SK-QA-003`'s (performance-engineering) findings are grounded in an actual stated or measured latency budget for the realtime channel, not a speculative "make it fast" recommendation issued before any traffic exists — consistent with its own non-activation condition ("premature optimization the user didn't ask for") and the library-wide measure-before-optimizing rule (dimension 14). | 14 (performance reasoning) | minor |
| 9 | `SK-TECH-threejs`'s output is checked against its documented **r-number versioning (no semver)** caveat from the technology-skill table — a claim like "upgrade to the next semver-minor" would be a technology-accuracy defect for this specific skill. | 12 (technology-specific accuracy) | minor |
