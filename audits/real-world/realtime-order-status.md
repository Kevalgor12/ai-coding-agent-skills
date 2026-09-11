# Real-World Evaluation — Realtime / live order-status updates

**Step 32** of the master build plan. Date: 2026-09-11. Domain: Realtime.
Adversarial pattern: **this domain's own already-known cluster issue** —
`audits/cross-skill/cross-skill-audit.md` finding **X-03**, which flagged that
the conflict matrix declares a `webrtc ⊥ socketio ⊥ websocket-api` cluster
(`core/dependency-architecture/matrices.md:92`) while **0 of 6** directed
`conflicts_with` edges are declared in the skills themselves.

**Method and caveats** as stated in
[`infrastructure-legacy-deploy.md`](infrastructure-legacy-deploy.md). Severity is
this project's Critical/High/Medium/Low audit convention. X-03 is cited and
**evaluated for whether it bites on this task**, not re-derived.

---

## The task

> "Add real-time order-status updates so customers see live updates without
> refreshing the page."

**Repository signals:** Next.js frontend (`next` in `package.json`,
`app/` routing) + Express backend (`express` in `package.json`).
**No existing realtime infrastructure**: no `socket.io`, no `ws`, no
`@socket.io/*` adapter, no WebRTC code, nothing. Single-instance deployment (not
contradicted by any signal). No transport is named in the request.

**Task shape, stated precisely**, because every finding below turns on it:
**one-way, server-to-client, discrete status events, browser-only clients, low
message frequency.** No client→server channel. No peer-to-peer anything. No
media.

---

## Trace

### P0 — Intake

- **Intent**: `build`. **Task type**: workflow pattern **#2 Feature development**.
- **Complexity**: `multi-step` (transport decision → server channel → client
  consumption → verification).
- **Risk class**: `reversible-write`.
- **S-Gate 1**: a new network-accepting endpoint is a trust boundary —
  *whose* order can a connected client see? This admits `SK-QA-002` and
  `SK-BE-005` under SR-5. (Important, and the library gets it right: see
  "What works".)

### P1–P2 — Discovery and routing

**Conflict-cluster resolution (D4) — the X-03 moment.** The realtime-transport
cluster is *needed but undetected*: a choice must be made and no signal reveals
it. SR-4 (`rules.md:20-24`) and `skill-router`'s own failure-handling
(`skill.yaml:101`, `SKILL.md:205-207`) both prescribe the same response —
"activate the generic Layer-3 skill and raise the choice as a decision rather
than activating every sibling", reinforced by its anti-pattern **"Speculative
breadth"** (`SKILL.md:164`).

**Selected:**

| Skill | Fires on |
|---|---|
| `SK-BE-004` realtime-communication | activation 1 + 2 (`skill.yaml:31-32`) — "A feature needs bidirectional, streaming, or **server-push** communication"; "A realtime transport choice is open" |
| `SK-TECH-nextjs` | `next` in `package.json` (activation 1) |
| `SK-TECH-express` | `express` in `package.json` (activation 2) |
| `SK-FE-001` frontend-architecture | a new client-side data-flow/state concern in the UI |
| `SK-QA-002` security-engineering | trust boundary on a new connection endpoint (S-Gate 1) |
| `SK-BE-005` authentication-authorization | per-customer order scoping — "a trust boundary/auth is involved" |
| `SK-QA-001` testing-strategy | runnable code produced |

**Excluded, and the reasoning is the interesting part:**

- **`SK-TECH-socketio`, `SK-TECH-websocket-api`, `SK-TECH-webrtc` — all three
  excluded, by three independent mechanisms:**
  1. **SR-3 detection gating** (`rules.md:16-19`): none of the three technologies
     is present in the repo or named in the request, so none is
     detection-eligible. *This alone is dispositive.*
  2. **Reciprocal non-activation, decisive under SR-2.** All three name the
     transport-choice-is-open case as their **first** non-activation condition:
     `socketio/skill.yaml:40`, `webrtc/skill.yaml:41`, `websocket-api/skill.yaml:39`
     — each routing to `SK-BE-004`. That is exactly this task's signal.
  3. **`skill-router`'s own body discipline**, cited above.
- `SK-TECH-redis` — excluded. Its realtime role is the Socket.IO pub/sub
  adapter, which is only relevant multi-instance; no multi-instance signal
  exists. Correctly held back rather than pulled in speculatively.
- `SK-BE-002` api-design — borderline; see RWR-02.

### P3–P5

`realtime-communication` is Tier **A** (`skill.yaml:66-67`,
`required_capabilities: [file-read, file-write]`), so **no `capability-adapter`
barrier is inserted** for the decision step — correct and cheap. The adapter
engages later only if a Tier-B technology skill runs.

Its Decision framework then executes:

- **Step 1** (`SKILL.md:86-89`): "Is this peer-to-peer media/data, or
  server-mediated events? … Server-mediated discrete events or broadcast →
  WebSocket or Socket.IO." → **WebRTC eliminated in one question.**
- **Step 2** (`:90-95`): "Browser-only clients with a simple, already-bounded
  message shape → raw WebSocket API may be sufficient and avoids the extra
  dependency." → points at raw WebSocket, reinforced by Engineering rule 5
  (`:134-136`) and Anti-pattern 4 (`:158-160`), both of which forbid reaching
  for Socket.IO by default.
- **Steps 3-4**: single instance, browser-only → no pub/sub adapter mandated, and
  CORS/Origin correctly declared insufficient on its own.

**Outcome: raw WebSocket API, browser-only, single instance, with handshake auth
scoping each connection to its own customer's orders.** That is a defensible,
non-over-engineered answer — and it is one structural step more than the task
needs. See RWR-01.

---

## Findings

### RWR-01 · SSE is advertised in Tier-0 metadata at five skills and exists nowhere in the library — **High**

**This is the most significant finding across all three Step-32 tasks.**

**Finding.** `realtime-communication` declares, in fields the router reads
without loading any body (CS-1):

- `skill.yaml:12` (`purpose`) — "Choose and design a realtime transport —
  WebSocket, Socket.IO, WebRTC, **or SSE**"
- `skill.yaml:23` (`description`, **Tier-0**) — same list
- `skill.yaml:32` (`activation_conditions[2]`, **Tier-0**) — "A realtime
  transport choice is open (WebSocket vs. Socket.IO vs. WebRTC **vs. SSE**)"
- `SKILL.md:4` (frontmatter description, VR-2-mirrored)

**SSE appears in none of the skill's reasoning surfaces.** Verified section by
section: Knowledge (`SKILL.md:32-82`) covers exactly three transports; Decision
framework (`:84-107`) — five steps, zero SSE; Workflow (`:109-122`);
Engineering rules (`:124-136`); Trade-offs (`:138-146`); Anti-patterns
(`:148-163`); Security (`:165-177`); Performance (`:179-187`); Testing
(`:189-199`). The Tier-2 reference is titled "**WebSocket API vs. Socket.IO vs.
WebRTC**" and has three columns (`references/transport-comparison.md:7-17`).
Workflow step 6's handoff names three targets: "websocket-api / socketio /
webrtc" (`:121-122`).

**The underlying research does not contain SSE either.** The skill's own
`source_reference` (`skill.yaml:71-74`) points at
`research/knowledge-maps/technology-decision-matrix.md` **§6**, whose heading is
literally "Realtime networking: WebSocket API vs. Socket.IO vs. WebRTC"
(`:143`). A corpus-wide `grep -i "SSE\|server-sent\|EventSource"` over
`research/` returns only MCP-transport hits, unrelated. There is no
`SK-TECH-sse`, and no SSE content in `nextjs`, `express`, `api-design`, or
`web-standards`.

**The phantom is not one author's slip — it is encoded across five skills.**
Every skill in the realtime cluster routes SSE questions to `SK-BE-004`:

| Site | Field | Text |
|---|---|---|
| `realtime-communication/skill.yaml:23, :32` | description, activation (**Tier-0**) | advertises SSE as selectable |
| `websocket-api/skill.yaml:39` | **non-activation** (**Tier-0**) | "The transport choice itself is still open (WebSocket vs. Socket.IO vs. WebRTC vs. SSE) — route to SK-BE-004" |
| `websocket-api/skill.yaml:20`, `SKILL.md:20,30` | scope, body | same framing |
| `webrtc/skill.yaml:19`, `SKILL.md:19` | scope | "(WebRTC vs. WebSocket/Socket.IO/SSE)" deferred to the generic skill |
| `socketio/SKILL.md:102` | body | "Socket.IO over raw WebSocket/WebRTC/**SSE** for the broad transport question" |
| `redis/skill.yaml:42` | **non-activation** (**Tier-0**) | "choosing WebSocket vs. WebRTC vs. SSE (route to SK-BE-004 **once authored**)" — *and* a stale X-02 marker on the same clause |

So a user who asks "should we use SSE here?" is routed by any of four skills to
`realtime-communication`, which loads 233 lines and has nothing to say. That is
a **dead-end route** — structurally worse than X-02's stale markers, because
there the target did not exist; here it exists and cannot serve.

**Why it matters on *this* task specifically.** One-way server→client push of
discrete status events to browser clients is the canonical SSE case. `EventSource`
gives automatic reconnection with server-controlled retry and `Last-Event-ID`
resumption for free — the exact two things Decision-framework step 2 treats as
Socket.IO's justification for its dependency weight. SSE rides ordinary HTTP, so
there is no upgrade handshake, no separate proxy configuration class, and no
sticky-session problem beyond normal HTTP affinity. And it needs no client→server
channel, which this task does not have.

The library's reachable minimum is raw WebSocket: a bidirectional, framed,
upgrade-negotiated protocol, for which — by the library's own Tier-2 reference
(`transport-comparison.md:15,17`) — there is **no backpressure mechanism** and
**"no official unit/integration test framework, mocking library, or conformance
suite"**. The skill recommends the simplest option *within the three transports
it can reason about*, and that option carries two documented deficiencies the
task shape did not require anyone to accept.

**Rule citations.** CE-1 (`specification.md:163`) — `description` "MUST encode
*what the skill does*"; here it encodes a capability the skill does not have.
SG-3 (`:185`) — "A skill MUST NOT state an API/flag/option that does not appear
in a cited source." QR-4 (`:203`) — "the decision framework MUST include the
simplest viable option": satisfied *within* the declared three-transport scope,
violated relative to the four-transport scope Tier-0 advertises.

**It has already propagated into the evaluation suite.**
`evaluations/expected-behaviors/S05-realtime-multiplayer-browser-game.md:116`
paraphrases `SK-BE-004`'s responsibilities as *"server-push events →
WS/Socket.IO/SSE"* — the answer key for the suite's flagship realtime scenario
now asserts a routing the library cannot produce. This is the same class of
consequence R-01 identified for `SK-FE-005`, arriving in a new place.

**The contrast that makes this a defect rather than a gap.** The *same skill*
refuses its message-broker gap explicitly and repeatedly — `skill.yaml:18-20`,
`:37`, `:93`; `SKILL.md:19-22`, `:104-107`, `:132-133`, `:161-163`, `:216-218` —
**eight sites**, and `audits/cross-skill/routing-audit.md` cites it by name as an
exemplar of "honest scope refusals route rather than guess." It refuses the gap
it knows about and silently over-claims the one it does not. The discipline
exists in the file; it was applied to one gap and not the other.

**Root cause.** The research pass profiled three named *technologies*
(each with a `research/technologies/` doc). SSE is a *web platform standard* with
no vendor profile, so it fell outside the research shape — and the skill's
author, writing a transport-selection skill, correctly knew SSE belongs in that
list and wrote it into the metadata without the research to back the body. The
four sibling skills then mirrored the list from the parent. **This is the failure
mode of composing generic-skill scope from a technology-driven research corpus:
the option set a decision framework *should* cover is not the option set the
research *does* cover, and nothing checks the two against each other.**

**Recommended correction — three options, in order of preference.**

1. **Research and author the SSE branch.** Add SSE to
   `technology-decision-matrix.md` §6 (a fourth column: one-way-only, HTTP-native,
   built-in reconnection via `EventSource`, `Last-Event-ID` resumption, no binary
   frames, per-origin connection limits under HTTP/1.1), then add Decision-framework
   step 0 to `realtime-communication`: *"Is the channel one-way server→client
   only? If yes, SSE over HTTP is the simplest sufficient transport; WebSocket
   and Socket.IO are justified only by an actual client→server or binary
   requirement."* Highest value; it is also the branch most real tasks need.
2. **Disclose the gap in the house style** — keep SSE in the option list but add
   the refusal the skill already applies to brokers: *"SSE is named here as a
   real fourth option, but this library's research does not cover it; a task
   whose answer is plausibly SSE is escalated as a research gap rather than
   answered by analogy to WebSocket."* Cheap, honest, and consistent with the
   skill's own existing discipline.
3. **Remove SSE from all five skills' metadata.** VR-3/SG-3-clean, but loses
   real information and makes the skill's transport-selection claim narrower than
   its name.

**Do not** choose option 3 silently — that would repeat the error in reverse, by
making the option set look complete when it is not.

**Regression test requirement.** **New scenario required.** Verified against
`evaluations/scenarios/`: `SK-BE-004` appears in S01, S05, S06, S08, but only S05
exercises it as a genuine transport decision — and S05 is a *project*-complexity,
bidirectional, low-latency **game**, where WebSocket/Socket.IO is genuinely
right and SSE genuinely wrong. **No scenario in the suite presents a one-way
server-push task**, which is precisely the shape that exposes this defect.

Proposed **`S19 — one-way live status push`**, category **Simple tasks** (its
purpose is to catch *over*-activation and over-selection, which is what
`evaluation-spec.md:137-140` says that category is for), with this as a
`critical` assertion: the transport recommendation either selects a one-way
transport or explicitly records that the one-way case was considered and why a
bidirectional transport is nonetheless justified. A run that recommends
WebSocket/Socket.IO **without ever naming the one-way option** fails the
scenario — even though the recommendation itself is workable.

Also required: correct
`expected-behaviors/S05-realtime-multiplayer-browser-game.md:116` under
`regression-suite.md`'s trigger 5, since it currently encodes the phantom.

---

### RWR-02 · The decision framework has no "plain polling still suffices" branch, and the declared route back to it carries a false marker — Medium

**Finding.** QR-4 requires the decision framework to include "the simplest viable
option (**including 'do nothing'**)". For this task the do-nothing option is
real and often correct: an order's status changes a handful of times over minutes
to hours, so polling an existing REST endpoint every 10–30 seconds delivers the
user-visible outcome ("live updates without refreshing") with **zero new
infrastructure, zero new connection-lifecycle code, and zero new trust
boundary**.

`realtime-communication`'s non-activation condition 1 (`skill.yaml:35`) does name
the case — "Plain request/response HTTP suffices (route to api-design)" — but
that is a *routing* guard evaluated at P2, before anyone knows the message
frequency. Once the skill activates, its Decision framework's **five steps never
ask whether a realtime transport is warranted at all**; step 1 presupposes it and
asks only *which*. There is no step that can reach "keep polling."

The escape hatch is impaired in both directions:

- **Forward** — SSE, the cheapest realtime option, is unreachable (RWR-01).
- **Backward** — `api-design`'s reciprocal non-activation (`skill.yaml:34`) reads
  "Realtime/bidirectional transport design (route to **realtime-communication,
  not yet authored**)". `realtime-communication` has been authored. This is an
  X-02 instance sitting on a **Tier-0 field**, on the single edge that connects
  this task back to its simplest answer. (`api-design` is on X-02's list of 15
  affected skills; this evaluation confirms the site and its consequence.)

Note the asymmetry with `search-integration`, which handles the analogous
"do you even need this?" question *inside* its framework as step 1 and gets full
marks for it (see `search-catalog-fulltext.md`). The pattern exists in the
library; `realtime-communication` does not use it.

**Root cause.** Scope framing. The skill's `purpose` is "choose and design a
realtime transport", so "don't" was placed in non-activation rather than in the
framework — which is defensible in isolation and wrong in composition, because
non-activation is evaluated once, on Tier-0 signals, before the frequency and
latency facts that decide the question are known.

**Recommended correction.** Add Decision-framework step 0 (pairs naturally with
RWR-01's option 1): *"Does the update frequency and latency requirement actually
warrant a persistent connection, or would periodic polling of an existing
endpoint deliver the same user-visible result? State the frequency/latency
figures the answer rests on. If polling suffices, hand back to `SK-BE-002`."*
Note this makes the skill's `required_context` item 2 ("Expected
concurrent-connection scale…", `skill.yaml:49`) actually load-bearing rather than
informational.

**Regression test requirement.** Fold into **S19** as a `major` assertion: the
run states the update-frequency assumption its transport recommendation rests on,
rather than treating "real-time" in the request text as settling the question.
This is the realtime analogue of the measure-before-optimizing discipline
(dimension 14) that `performance-engineering` already enforces elsewhere.

---

### RWR-03 · X-03's zero `conflicts_with` coverage does **not** bite on this task — and mechanically adding the six edges would introduce false conflicts — Medium *(a correction to X-03's recommendation, not a new defect)*

**The brief's question, answered directly: no, the absence of `conflicts_with`
does not cause an observable problem here, and the decision framework is not what
saves it — the routing metadata is.**

**X-03's finding, confirmed.** `socketio/skill.yaml:70`, `webrtc/skill.yaml:86`,
`websocket-api/skill.yaml:67` all declare `conflicts_with: []`. `matrices.md:92`
declares the cluster. 0 of 6 edges. Confirmed exactly as X-03 stated.

**Why it is inert here — three redundant protections, any one sufficient:**

1. **SR-3 is dispositive on its own.** No realtime technology is present in the
   repo and none is named. All three are detection-ineligible. A conflict edge
   could not change this outcome, because the siblings never become candidates in
   the first place.
2. **The cluster is declared — just in `non_activation_conditions` rather than in
   `conflicts_with`, and under SR-2 that is *more* decisive, not less.** A census
   of the six directed edges:

   | Directed edge | Declared? | Where |
   |---|---|---|
   | socketio excluded when websocket-api applies | ✅ | `socketio:39` |
   | socketio excluded when webrtc applies | ✅ | `socketio:41` |
   | websocket-api excluded when socketio applies | ✅ | `websocket-api:41` |
   | webrtc excluded when socketio applies | ✅ | `webrtc:42` |
   | webrtc excluded when websocket-api applies | ✅ | `webrtc:42` |
   | websocket-api excluded when webrtc applies | ❌ | — (and correctly so, below) |

   **5 of 6**, plus all three declare "the transport choice is still open →
   `SK-BE-004`" as their *first* non-activation condition — which is this task's
   exact signal, so all three self-exclude from Tier-0 alone.
3. **`skill-router`'s own body** carries the discipline independently
   (`SKILL.md:164`, `:205-207`; `skill.yaml:101`).

**The substantive correction to X-03.** X-03 recommended "add the 8 missing
realtime + API-paradigm edges to the skills." For the realtime cluster, at least
two of the six should **not** be declared as static `conflicts_with`, and doing so
would cause real under-activation:

- **`webrtc` + `websocket-api` are routinely complementary, not exclusive.**
  WebRTC defines no signaling channel. `webrtc/skill.yaml:50-52` declares
  `signaling-transport` as an input and names **WebSocket** as the example. A
  WebRTC application with a WebSocket signaling channel is the normal shape, and
  a `webrtc ⊥ websocket-api` edge would exclude the skill that owns the signaling
  half. The one missing edge in the census above is missing *for the right
  reason*.
- **`socketio` and `websocket-api` are compositional.** Socket.IO is built on top
  of WebSocket — `realtime-communication/SKILL.md:36-39` and
  `transport-comparison.md:11` both state this from Socket.IO's own docs ("not a
  raw WebSocket implementation"). `socketio`'s existing guard is correctly
  scoped: "The stack uses **only** the raw WebSocket API **with no Socket.IO
  dependency**" (`:39`) — a component-scoped condition, not a blanket exclusion.
  A symmetric `conflicts_with` edge cannot express that scoping.

The root issue is that `matrices.md:92` qualifies the cluster "*for the same
channel*", and **`conflicts_with` is a static, unqualified field that cannot
carry the qualifier.** This is the same failure mode `routing-audit.md` R-04
documented for the runtime cluster, where unscoped guards cause `go`/`nodejs` to
exclude themselves on polyglot repos — arrived at from the opposite direction.

**Where it *would* bite (bounding the claim honestly).** A repo already carrying
`socket.io` for an existing chat feature **and** `ws` for something else, with the
same order-status request. Then `socketio` activation 1 (dependency present) and
`websocket-api` activation 3 (`ws` package) both fire on repo signals, and neither
"choice still open" guard applies — a choice *was* made, twice, for different
channels. Nothing in the metadata then arbitrates which owns the new channel, and
a run could plausibly implement order status on one while the existing
infrastructure sits on the other. **That** is the task shape a regression scenario
should encode.

**Recommended correction.** Amend X-03's recommendation for the realtime cluster
specifically: (a) do **not** add the 6 symmetric edges; (b) add the one missing
non-activation clause to `websocket-api` in the component-scoped form its siblings
already use; (c) resolve `matrices.md:4`'s claim that the matrices are
"projections of the same edge set" by making the projection source
`non_activation_conditions` for scoped clusters and `conflicts_with` for
genuinely artifact-exclusive ones (frontend framework, SQL engine, ORM) — the
distinction being whether the exclusion survives without a qualifier.

**Regression test requirement.** **New scenario recommended, and it is not S19.**
Proposed **`S20 — new realtime channel in a repo that already has two`**,
category **Conflicting-requirement scenarios** (`evaluation-spec.md:164-168`
— "two plausible skills would recommend incompatible things"), sibling to S16's
`prisma`-repo-`drizzle`-request shape. Critical assertion: the run identifies
that two transports are already in use, and either reuses the one that already
serves the relevant surface or raises the choice as an explicit decision — it does
not silently introduce a third channel. This scenario is what would actually
test X-03; S19 would not.

---

### RWR-04 · WebRTC is correctly and cheaply excluded — no defect *(the brief's second question, answered)*

**Finding.** The brief asked whether the decision framework is "generic enough
that a real run might waste effort considering WebRTC unnecessarily." **It is
not, and it would not.**

- `realtime-communication`'s Decision-framework **step 1** (`SKILL.md:86-89`)
  resolves it in a single question — peer-to-peer media/data vs. server-mediated
  events — and this task answers it unambiguously.
- The Knowledge section pre-empts the question outright: "WebRTC serves a
  different use case entirely… The decision-matrix data includes WebRTC in this
  comparison because it **shares the 'realtime-networking' category, not because
  any source frames it as a substitute** for the other two" (`SKILL.md:39-43`).
  That sentence exists specifically to stop the confusion the brief anticipated.
- `webrtc`'s own non-activation conditions 1 and 2 (`skill.yaml:41-42`)
  self-exclude on exactly this shape: transport choice still open → `SK-BE-004`;
  server-mediated realtime with no P2P requirement → socketio or websocket-api.
- **Cost of the exclusion: zero.** It is decidable from Tier-0, so `webrtc`'s
  body never loads (CS-2). No context is spent.

`expected-behaviors/S05:113-118` already asserts the same exclusion for the game
scenario. This evaluation confirms the guard holds on a second, differently-shaped
realtime task.

---

### RWR-05 · The client half of the feature is unowned — Medium

**Finding.** The user's request is about what a customer sees on a page. The
library staffs the server side well and the client side not at all.

- `realtime-communication`'s Workflow step 6 (`SKILL.md:121-122`) hands off only
  to "websocket-api / socketio / webrtc" — three server-and-client-protocol
  skills, no frontend target. Its `related_skills` (`skill.yaml:63`) are
  `[SK-BE-001, SK-BE-002, SK-TECH-redis]` — entirely backend. No `SK-FE-001`.
- `nextjs` and `express` bodies contain **no realtime content**: a grep for
  `realtime|websocket|socket|SSE|stream` over both returns only React streaming
  SSR, Express middleware ordering, and one Next.js **CVE** reference to
  "SSRF in WebSocket upgrade handling" (`nextjs/SKILL.md:225`) — nothing
  implementational.
- The concrete unowned decisions this leaves: a long-lived connection cannot live
  in a Next.js Route Handler, so the channel must terminate on the Express
  process — a deployment-topology fact with real consequences for the
  Next.js/Express split this repo has; and on the client, connection lifecycle in
  React (effect cleanup on unmount, React 18+ StrictMode's double-invoked effects
  opening two connections in development, reconnect/backoff state) is exactly the
  class of bug that makes realtime features flaky.

`SK-FE-001` does activate independently on the UI change, so the *stage* is
staffed — but it has no realtime content either, and nothing in the plan declares
a handoff (D11) between the transport decision and the client implementation.

**Root cause.** `realtime-communication` is filed in the **BE** domain
(`skill.yaml:8`) and its edge set is entirely backend, even though every transport
it selects among is consumed by a browser.

**Recommended correction.** Add `SK-FE-001` to `related_skills` and extend
Workflow step 3 (connection lifecycle) to state explicitly that the lifecycle has
a client half whose framework-specific implementation belongs to the detected
frontend skill. No new content in the frontend skills is required; the missing
piece is the declared edge.

**Regression test requirement.** Fold into **S19** as a `minor` assertion: the
plan contains a client-side implementation stage with a named owner, not only a
server-side transport design. Kept `minor` because a competent run would likely
do this anyway; the finding is about the declared graph, not the likely behavior.

---

### RWR-06 · `realtime-communication` declares no `escalation` field — Medium, **does not bite here**

**Finding.** Verified: no `escalation:` key in `realtime-communication/skill.yaml`,
while `SKILL.md:211-218` carries two gates — a transport switch on an existing
production realtime layer (**G-COMMITMENT**) and the message-broker research-gap
escalation. X-04 / R-05 instance, confirmed.

**Bite on this task: nil.** No existing realtime layer exists to switch away
from, and no broker request is made. Recorded for completeness and as a third
data point (with `search-integration` and `deployment-release`) that X-04's
practical severity is entirely task-shape-dependent: it is inert here and on the
search task, and materially harmful on the infrastructure task where the same
defect sits on a `production`-risk gate.

**Regression test requirement.** **No new scenario.** Would require an existing
production realtime layer plus a switch request — a different task, and better
covered by the S20 shape proposed under RWR-03 than by a dedicated file.

---

## What works (recorded so a later reviewer does not re-open it)

- **The X-03 gap is covered by a better mechanism than the one X-03 proposed.**
  Five of six directed exclusions are declared as component-scoped non-activation
  clauses, which SR-2 makes decisive and which can carry the "same channel"
  qualifier that `conflicts_with` cannot. This is the cross-routing discipline
  `routing-audit.md` praised, doing real work in the cluster the audit flagged.
- **The security reasoning is genuinely strong and specific.** The skill
  establishes that CORS/Origin is browser-only and, for Socket.IO,
  transport-partial (`SKILL.md:45-56`, Engineering rule 1, Anti-pattern 1,
  `verification` item 3) — four sites insisting that handshake authentication is
  designed independently of CORS. For a task where the trust question is "can a
  connected client see another customer's orders," that is exactly the right
  emphasis, and it fires without the user raising it.
- **Backpressure is treated as a first-class, cross-transport concern**
  (`SKILL.md:69-78`, Workflow step 5, Anti-pattern 3) with the honest observation
  that "none of the individual technology docs frame this as a shared
  transport-layer pattern — it only becomes visible by reading the three side by
  side." That is the generic skill adding value its children cannot, which is
  what a Layer-3 parent is for.
- **Tier A is correctly assigned**, so no `capability-adapter` barrier is
  inserted for the decision step (PR-3) — proportionate orchestration.
- **Anti-pattern 4 and Engineering rule 5 both forbid defaulting to Socket.IO**
  (`:158-160`, `:134-136`), which is the domain's real over-engineering trap and
  satisfies QR-4 within the skill's declared scope.

---

## Score

| # | Dimension | Verdict | Why |
|---|---|---|---|
| 1 | Skill routing | **Strong** | `SK-BE-004` fires on two verbatim conditions; all three technology siblings excluded by three independent mechanisms; `redis` correctly held back. No over-activation; **X-03 does not produce one** (RWR-03). |
| 2 | Dependency activation | **Adequate** | Backend sequencing is correct and the auth/security edges fire without prompting. The frontend half of the feature has no declared edge (RWR-05). |
| 3 | Context efficiency | **Strong** | One Layer-3 body (233 lines) + two framework bodies; all three realtime technology bodies stay unloaded. The Tier-2 comparison loads only on a link-follow (CS-5). Exemplary. |
| 4 | Implementation quality | **Weak** | The chosen transport works, but the task's actual shape — one-way, browser-only, low-frequency — admits two simpler answers (SSE, polling) that the framework cannot reach (RWR-01, RWR-02), and the client half is unguided (RWR-05). |
| 5 | Security | **Strong** | S-Gate 1 classifies correctly; `SK-BE-005` activates on per-customer scoping; the CORS-is-not-access-control discipline is stated four times and is exactly right for this trust question. |
| 6 | Testing | **Adequate** | T-Gate 1 staffs verification, and the skill honestly discloses that raw WebSocket has no official testing story (`SKILL.md:194-197`) — but that disclosure is a consequence of the transport it steered toward, which the task did not require. |
| 7 | Maintainability | **Weak** | The dimension this task damages most. The framework guards well against Socket.IO-by-default, then stops — leaving a persistent bidirectional connection, its lifecycle, and its backpressure exposure as the minimum, for a feature that pushes a status string a few times per order. |
| 8 | Error handling | **Good** | `failure_handling` correctly requests the missing requirement rather than assuming a transport, and refuses the broker gap explicitly. |
| 9 | Convention adherence | **Good** | Nothing contested; the Next.js/Express split is respected by the existing skills. |
| 10 | Final outcome | **Adequate** | A real engineer gets a correct, secure, well-reasoned WebSocket design — having never been told that the simplest transport for their exact requirement exists, while four skills' routing metadata claims the library can choose it. |

**Summary:** High ×1 (RWR-01), Medium ×4 (RWR-02, RWR-03, RWR-05, RWR-06),
no defect on RWR-04.

The domain's known cluster issue (X-03) turns out to be the *less* important
problem here — it is inert on this task and its recommended fix is partly wrong.
The real defect is one layer up: a decision framework whose advertised option set
is wider than its reasoned option set, in the direction of simplicity, at five
sites in Tier-0 metadata.
