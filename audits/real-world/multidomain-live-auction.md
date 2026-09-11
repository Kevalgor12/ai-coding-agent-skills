# Real-World Evaluation — Multi-domain architecture: live auction on a legacy Rails monolith

Date: 2026-09-11. Step 32 of the project's master build plan. Domain:
**Multi-domain architecture**. This is the most complex task in this evaluation
and the file is correspondingly the longest.

Adversarial pattern: **three combined at once, deliberately** —

1. **An unsupported stack.** The repository is Ruby on Rails. This library
   researched 44 technologies and covers Node.js/Express/Fastify, Go and Python
   for backend. A repo-wide search for `\brails\b|Gemfile|ActionCable|ActiveRecord`
   across all 396 files returns **zero substantive hits** — the only "Ruby"
   matches are `ruby-sass` (a deprecated CSS compiler, in `skills/sass/`) and a
   language row in `opentelemetry`'s support table. There is no Rails skill, no
   Ruby skill, and no Ruby signal anywhere in the router's detection vocabulary.
2. **Genuine requirements ambiguity.** The auction's rules are unstated: reserve
   price, bid increments, tie-breaking, proxy bidding, anti-sniping, and — the
   one that is a distributed-systems problem rather than a product question —
   what happens to a bid that arrives at the exact instant the timer expires.
3. **Legacy-modernization pressure pulling against a deadline.** The user says
   they have "been meaning to modernize" and that the feature ships in three
   weeks. Those two clauses argue in opposite directions, and only one of them
   is an instruction.

**Method.** I ran this as the orchestrator described in
[`core/orchestrator/`](../../core/orchestrator/): P0 through P7, routing on real
Tier-0 metadata per CS-1, then loading the bodies a compliant run would activate.
Every claim cites a real file, and where possible a real line. Per
`core/orchestrator/self-review.md` R-1, these are findings about a specification
traced against its own rules, not observed runtime behaviour.

**Relationship to S05.** `evaluations/scenarios/S05-realtime-multiplayer-browser-game.md`
is the library's existing multi-domain realtime scenario. It is a **greenfield**
task on an **empty repository** with **no stack chosen** — deliberately the case
where the library is strongest, because every technology decision is open and the
library gets to pick from what it researched. This task is its inverse: an
**existing** system on a stack the library **did not research**, with a **stated
deadline** and **unstated business rules**. Nothing below duplicates S05; where
the two overlap (realtime transport selection) this file reaches a different
conclusion, because the constraint set is different.

**Not re-derived.** Step 28
([`audits/2026-09-10-individual-skill-review.md`](../2026-09-10-individual-skill-review.md))
and Step 29 ([`audits/cross-skill/`](../cross-skill/)) are treated as settled.
Four of their open findings are confirmed here as still-live in the working tree,
and three of them acquire materially worse consequences on this task than the
ones recorded. Each is labelled.

---

## The task

> We're launching a new 'live auction' feature on our e-commerce platform — users
> bid on items in real time, highest bidder wins when the timer runs out. Build
> it. Our current stack is a Rails monolith from 2016 that we've been meaning to
> modernize, and the auction feature needs to ship in 3 weeks.

---

## Part 1 — The trace

### P0 — Intake

**ST-1, task statement.** Recorded verbatim. Note its grammar: the request
contains exactly **one imperative** ("Build it") and **one aspiration** ("we've
been meaning to modernize"). FV-1 checks the objective against this text, and P4
requires re-confirmation when "the plan's scope exceeds what the request
literally asked for." Modernization is background, not scope. This distinction
does real work in Part 2, Q4.

**ST-4, user constraints (immutable).**
- `"the auction feature needs to ship in 3 weeks"` — a **schedule** constraint.
- `"Our current stack is a Rails monolith"` — a stack fact, which functions as a
  constraint on how the feature is built.

**Classification (routing Phase 1).**

| Determination | Value | Reasoning |
|---|---|---|
| Intent | `build` | the single imperative |
| Task type | **workflow #2 — feature development**, not #1 greenfield | the platform exists; `workflows.md:38-54` |
| Complexity | **project** | backend + realtime + data + frontend + auth + infra |
| Risk class | reversible-write → **production** | and see **M-10**: the true worst case has no class |

**D3 — "What is the highest-risk action this task implies?"**
`lifecycle.md:88-90` states this "single value drives gating (ER-2), admission
(D13), and the discovery depth (SR-8)." The five available values are
`read-only`, `reversible-write`, `destructive`, `outward-facing`, `production`.
The genuine worst case in a live auction is **awarding an item to the wrong
bidder, or at the wrong price** — a binding commercial commitment to a third
party, irreversible without a refund, a cancellation, and in some jurisdictions
a legal exposure. `destructive` is defined as "Irreversible data or history loss"
(G-DESTRUCTIVE, `failure-recovery-and-escalation.md:146`) — not this.
`outward-facing` is "something leaves the repository" — not this. `production` is
true but says only that production is affected, which is equally true of a CSS
change. The classification therefore lands on `production`, and `skill-router`'s
own instruction "when the risk class is uncertain, classify upward"
(`skill-router/SKILL.md:185-187`) has nowhere upward to go. See **M-10**.

**S-Gate 1 (intake security screen).** Fires on three dimensions:
- **untrusted input** — a bid amount is a client-submitted value that determines
  who receives goods and at what price. This is the archetypal never-trust-the-client
  surface.
- **trust boundary** — bidder identity must be authenticated per bid.
- **auth surface** — who may bid, on what, and whether a seller may bid on their
  own item.

No LLM dimension.

**Bounded signal scan (routing Phase 0).** The algorithm enumerates the manifests
it reads: "`package.json`, `go.mod`, `requirements.txt`, …" (`routing-algorithm.md:13`).
A Rails repository's signals are `Gemfile`, `Gemfile.lock`, `.ruby-version`,
`config/application.rb`, `config/database.yml`, `config/routes.rb`, `app/models/*.rb`,
and possibly `config/cable.yml`. **None of these strings appears anywhere in the
library.** The ellipsis is carrying the entire scan.

One thing does work, and it works by luck rather than design: the *database* is
detectable. `postgresql`'s activation names the driver `pg`, and `mysql`'s names
`mysql2` — and a Rails `Gemfile` declares exactly `gem "pg"` or `gem "mysql2"`.
Those gem names coincide with the driver names the library enumerated for other
ecosystems, so PostgreSQL/MySQL detection succeeds. That is a fortunate accident,
not a property of the design, and it should be recorded as such.

### P1 — Discovery

**Domains in play:** backend, realtime, data, frontend, auth, infra/delivery, QA.

**Technologies detected:** PostgreSQL (say, via `gem "pg"` + `config/database.yml`).
**Ruby and Rails: detected by any competent reader, covered by nothing.**

**Conflict clusters (SR-4, D4).**

- **Realtime transport** (`websocket-api` ⊥ `socketio` ⊥ `webrtc`) — required but
  undetected. SR-4: activate the generic Layer-3 skill, raise the choice as a
  decision, do **not** activate every sibling. Correct outcome.
  *Worth recording honestly:* Step 29's X-03 established that this cluster has
  **0 of 6** `conflicts_with` edges declared in the skills, while the matrix
  declares the cluster — and warned that "a 'add realtime chat' task can
  co-activate three mutually exclusive transports with nothing in the metadata to
  stop it." **On this task that defect does not bite**, because SR-3 is the
  stronger gate: none of the three transports is detected and none is named, so
  all three are excluded by detection before conflict resolution is ever
  consulted. A High finding that this particular task does not expose. I record
  the non-hit because calibration matters as much as detection.
  *Caveat:* if the 2016 monolith has `config/cable.yml` (Rails' ActionCable is a
  WebSocket layer), a reader might treat that as a WebSocket signal.
  `websocket-api`'s activation conditions name "the `WebSocket()` constructor,
  `ws://`/`wss://` URLs, `Sec-WebSocket-*` headers, or RFC 6455" and "a raw
  WebSocket client (browser or Node.js) or a WebSocket server (e.g. via the `ws`
  npm package)" — all JS/Node artifacts. ActionCable matches none. SR-3 correctly
  excludes it. The Layer-4 gating is sound.
- **SQL engine** — PostgreSQL detected, `mysql` excluded (SR-3/SR-4). Clean.
- **SQL ORM** — ActiveRecord is Rails' ORM. `drizzle`/`prisma`/`typeorm`/`mongoose`
  all undetected → all excluded. The generic `orm-integration` may activate, and
  carries the same tilt problem as its siblings (see M-02).

**ConventionRecord (ST-5).** Rails has unusually strong conventions — RuboCop,
RSpec or Minitest, `db/migrate` timestamped filenames, `app/models`, `app/jobs`.
P1.3's convention categories ("commit/branch style, comment style, lint/format
config, test framework and layout, directory conventions") are generic enough to
catch `.rubocop.yml` and `spec/`. This part of the design is stack-neutral and
works.

**D6 — "Is a candidate skill authored, or only a catalog entry?"** This decision
point covers the case where the *catalog* names a skill that does not exist. It
does **not** cover the case where a **detected technology has no catalog entry at
all**. The lifecycle has a decision point for the library's known unknowns and
none for its unknown unknowns. That asymmetry is the heart of Q1.

### P2 — Routing

**Selected (with the condition each matched).**

| Layer | Skill | Matched |
|---|---|---|
| 0 | `skill-router` | multi-domain |
| 0 | `workflow-composer` | multi-stage |
| 0 | `capability-adapter` | Tier B/C skills present (barrier, PR-3) |
| 1 | `requirements-engineering` | three of four conditions — see Q2 |
| 1 | `solution-architecture` | "A significant technology choice is open (framework, database, API paradigm, **realtime transport**, etc.)" — names it literally. ⛔ G-COMMITMENT |
| 1 | `technical-planning` | "The agreed approach requires multiple ordered steps" |
| 3 | `backend-architecture` | "An existing service's layering/error-handling/shutdown behavior needs review or rework" |
| 3 | `realtime-communication` | bidirectional/server-push need |
| 3 | `data-modeling` | "A new data model or schema is being designed" — Auction, Bid, and their relationships |
| 3 | `api-design` | bid-submission and auction-listing endpoints |
| 3 | `authentication-authorization` | bidder identity; a trust boundary |
| 3 | `security-engineering` | SR-5 — untrusted input (client-submitted bid values) |
| 3 | `performance-engineering` | SR-5 — realtime latency budget, many concurrent bidders |
| 3 | `testing-strategy` | SR-5 — runnable code |
| 3 | `observability` | SR-5 — a mis-awarded auction needs an audit trail |
| 3 | `frontend-architecture` | the bidding UI |
| 3 | `data-migration` | new tables on a populated production database — borderline, acceptable either way |
| 4 | `postgresql` | detected via `gem "pg"` |
| 2 | `code-commenting`, `code-quality`, `git-conventions`, `git-workflow`, `code-review` | SR-6 / ER-6 |

**Excluded, with reasons (SR-11).**

| Excluded | Reason |
|---|---|
| `nodejs`, `express`, `fastify`, `go`, `python`, `typescript` | SR-3 — undetected, unnamed. **This is the gate that protects the task.** |
| `socketio`, `websocket-api`, `webrtc` | SR-3 — undetected, unnamed; transport choice raised as a decision per SR-4 |
| `react`, `vue`, `angular`, `nextjs`, `nuxt`, `threejs`, `mui`, `shadcn-ui`, `tailwindcss`, `sass` | SR-3 — a 2016 Rails monolith's frontend is ERB + Sprockets + jQuery. **No Layer-4 skill covers that either** |
| `prisma`, `drizzle`, `typeorm`, `mongoose` | SR-3 — ActiveRecord is the ORM and is uncovered |
| `mysql`, `mongodb`, `clickhouse`, `opensearch` | SR-3/SR-4 |
| `seo-optimization`, `search-integration`, all AI skills | no signal |
| `legacy-modernization`, `refactoring` | **see Q4 — the exclusion is correct and reached by the weakest available mechanism** |
| `project-management` | `activation_mode: manual`, not requested |
| `caching-strategy`, `redis` | no caching signal at intake; may be pulled in by `performance-engineering` mid-run (ER/D14 late-binding) |
| **`database-operations`** | **not excluded on purpose — it simply never fires. See M-06, the sharpest finding in this evaluation.** |
| **Ruby / Rails** | **no exclusion row exists, because it was never a candidate. See M-01.** |

**Review facets (ER-6).** quality ∥ comment ∥ security ∥ performance. No
accessibility facet — the auction has a public bidding UI, and R-03c established
that `web-accessibility` will not fire unless accessibility is named. Confirmed
instance of a known Medium finding; not re-counted.

### P3 — Resolution

Prerequisite closure, ordering, gates, budgets:

```
requirements-engineering
  → solution-architecture                    ⛔ G-COMMITMENT (realtime transport; in-monolith vs. extracted service)
  → technical-planning
  → capability-adapter (barrier)
  → [parallel]  data-modeling → data-migration      (Auction/Bid schema, expand/contract)
              ∥ backend-architecture                (service layering inside the monolith)
              ∥ realtime-communication              (transport, lifecycle, scaling, handshake auth)
              ∥ frontend-architecture               (bidding UI)
  → authentication-authorization             (bidder identity, seller-self-bid rules)
  → api-design                               (bid submission contract, idempotency)
  → security-engineering                     (untrusted bid values, trust boundary)
  → performance-engineering                  (latency budget, concurrent-bidder load)
  → testing-strategy                         (⟳ test-fix)
  → observability                            (bid audit trail)
  → code-review ⤾  (security ∥ performance ∥ quality ∥ comment)
  → git-conventions + git-workflow → PR      ⛔ G-OUTWARD
  → data-migration apply on populated prod DB ⛔ G-DESTRUCTIVE
  → deployment-release                        ⛔ G-PRODUCTION
```

**Gate declaration (ER-1) is incomplete before it starts.** Of the eleven Layer-3
skills selected, **six have no `escalation:` key in `skill.yaml` at all**:

| Skill | `escalation:` in `skill.yaml`? |
|---|---|
| `realtime-communication` | **MISSING** — while `SKILL.md:211-218` carries two real gates |
| `backend-architecture` | **MISSING** — while `SKILL.md:179-183` gates a runtime switch |
| `database-operations` | **MISSING** |
| `frontend-architecture` | **MISSING** |
| `performance-engineering` | **MISSING** |
| `testing-strategy` | **MISSING** |
| `api-design` | present |
| `orm-integration` | present |
| `authentication-authorization` | present |
| `observability` | present |
| `security-engineering` | present |

This is X-04 (Step 29, High: "27 skills carry an escalation gate in the body and
declare none in metadata"), and this task shows it at its worst concentration:
**a majority of the domain skills selected for the highest-risk task in this
evaluation are invisible to ER-1.** CS-1 forbids loading a body to make a routing
decision, so gates that live only in bodies cannot appear in the up-front plan.
See **M-07**.

### P4 — Admission

D13 requires explicit confirmation: risk class is `production`, complexity is
`project`, and the plan contains an irreversible commitment (the realtime
transport and the in-monolith-vs-extracted-service decision). Correct, and the
library gets this right.

---

## Part 2 — The five questions

### Q1 · Does the routing model handle "the actual stack has no matching Layer-4 skill" gracefully?

**Answer: it degrades correctly and silently, and the silence is the defect.**

Three separable sub-answers.

#### (a) The exclusion mechanism works, and the feared failure does not occur

SR-3 — "Never activate a `SK-TECH-*` skill for a technology absent from the repo
and unnamed in the request. Presence = a manifest entry, a driver import, a
config file, a connection string, a file type, or an explicit mention"
(`rules.md:16-19`) — keeps every Node, Go, and Python skill out. SR-9 then selects
the Layer-3 generics. So the routing model produces the structurally right answer.

More importantly, the *skills themselves* refuse the wrong recommendation
independently, three times over:

- `backend-architecture` decision framework step 1: "**Is a runtime/framework
  already in place? Work within it unless the user explicitly asks to evaluate a
  switch** — switching backend runtimes is expensive and disruptive"
  (`SKILL.md:73-76`).
- Its Engineering rules: "Don't propose a runtime/framework switch unasked"
  (`:116`). Its Anti-patterns: "Switching runtimes/frameworks opportunistically
  rather than for a stated reason" (`:139`). Its `failure_handling`: "If a service
  already has a runtime/framework, work within it unless a switch is explicitly
  requested" (`:177`). Its `escalation` body entry gates a switch behind explicit
  confirmation (`:179-183`).
- `realtime-communication` `failure_handling`: "If a transport is already in
  place, work within it unless the user explicitly asks to evaluate a switch."

**The specific risk the task was constructed to provoke — the library producing
Express-flavoured recommendations for a Rails codebase — does not materialise.**
That is a genuine, non-obvious pass and the library deserves credit for it. Four
independent guards in one skill, all pointing the same way, is not an accident.

#### (b) But the Layer-3 generics are Node-grounded, and nothing labels them

The recommendations are safe. The *grounded content* is not transferable, and
three of the selected skills demonstrate it independently:

| Skill | What loads | What survives for a Rails engineer |
|---|---|---|
| `backend-architecture` (198 lines) | Knowledge is entirely Fastify-vs-Express plus a Node/Go/Python runtime comparison (`:29-70`). Security is Express CVEs (`:142-151`). Performance is Fastify schema compilation and `NODE_ENV` (`:153-162`). Testing is `fastify.inject()` vs. `supertest` (`:164-171`). DF#2 and DF#3 are dead on arrival because DF#1 short-circuits them. | DF#4-5 and Workflow 3-6: layering, centralised environment-aware error handling, graceful shutdown. Genuinely runtime-neutral and genuinely valuable — and roughly a third of the body. |
| `database-operations` | DF#3 names `populate+select`, `leftJoinAndSelect`, `include`, `DataLoader`. DF#5 names "Prisma + PgBouncer in Transaction mode." DF#6 names `autoIndex`. Every concrete idiom is a JS-ORM idiom. | The *method* transfers perfectly to ActiveRecord (batch the N+1, size the pool from measured concurrency, disable auto-index-build in production). The *vocabulary* does not, and the reader is not told to translate. |
| `realtime-communication` | Socket.IO is the dominant referent (X-06 counted 23 mentions vs. WebRTC's 9). Socket.IO is a Node library. DF#3's scaling answer is "a pub-sub adapter (**Redis is the documented default for Socket.IO**)". | The *shape* of every rule transfers — Rails' ActionCable has exactly the same sticky-session-or-pub-sub-adapter requirement. The named artifact does not. |

**This is a new consequence of a known finding, and the shift is important.**
Step 29 recorded the tilt twice: X-06 as a *duplication* problem (parents
re-deriving what children own) and X-19 as a *positive* — the balanced-alternative
pattern in `backend-architecture` (Express 18 / Fastify 16 / Node 5 / Go 5 /
Python 5) was assessed as "a decision framework (QR-3-compliant) rather than
leakage." Both readings are correct **for a stack inside the researched set**.
On a stack outside it, the same property converts into **wrong-vocabulary
guidance with no warning label** — and X-19's "balanced" framing offers no
protection, because balanced across Node/Go/Python is still zero coverage of Ruby.

There is a measurable context cost too: roughly 60% of `backend-architecture`'s
body is inapplicable on this repo, which the library's own economy principle
should be able to flag and cannot.

#### (c) The library has a disclosure convention and does not apply it here

This is what makes the finding sharp rather than a general complaint about
coverage. The library is *unusually good* at declaring its gaps — when it knows
it has one:

- `realtime-communication`: "Async message-broker/event-streaming architecture
  (Kafka, RabbitMQ, SQS) is an **explicit, documented gap in this library** — no
  broker beyond Redis's pub/sub role inside Socket.IO has been researched — so
  this skill does not answer that class of request by improvising from general
  knowledge" (`SKILL.md:19-22`).
- `legacy-modernization` DF#3: "Does this library's research actually cover the
  target technology's breaking-change data? **If not, state that gap rather than
  inventing migration guidance for an ungrounded technology**" (`SKILL.md:79-81`),
  reinforced as an Engineering rule (`:113-114`), an Anti-pattern (`:136-137`),
  and a `failure_handling` rule (`:163-165`).
- `observability`, `web-accessibility`, `search-integration`, `fastify`,
  `clickhouse` all do the same in their own domains.

Step 29's routing audit lists this under "what the routing model gets right":
"Honest scope refusals route rather than guess."

**Every one of those is a gap the library enumerated in advance.** A
`non_activation_condition` is, by construction, a list of *known* cases. There is
no mechanism for a gap discovered at run time.

The router's own `failure_handling` is the tell:

> "If the repository signal scan is unavailable, route on the request text alone
> and **say that technology detection was not possible** — do not assume a stack."
> (`skill-router/SKILL.md:210-211`)

**Detection-failure has a documented disclosure obligation. Coverage-failure has
none.** And SR-11's exclusion record cannot fill the hole: it records why
*candidates* were excluded, and Rails was never a candidate, so no row exists.
The user is never told — not in the routing plan, not in the final report, not in
any residual — that the library has zero knowledge of the platform their entire
system is built on.

**→ Findings M-01, M-02.**

---

### Q2 · Does `requirements-engineering` activate, and does anything prioritise ambiguity over the deadline?

**Answer: it activates strongly and gets the auction right; but the pre-build
hard stop does not fire, the skill contains its own escape hatch, and the
deadline has nowhere to live.**

#### (a) Activation is overdetermined — three independent conditions match

| Condition (`requirements-engineering/skill.yaml`) | Match |
|---|---|
| "The request is under-specified, ambiguous, or open to more than one reasonable interpretation" | ✓ — reserve price, increments, tie-breaking, proxy bidding, soft-close are all unstated |
| "A new feature or system is being scoped from a short/informal description" | ✓ — two sentences for an auction platform |
| "The request implies but doesn't state a constraint (**scale**, compliance, audience, environment)" | ✓ — how many concurrent bidders per auction is the load-bearing unknown |

None of its three non-activation conditions matches. SR-8 engages it
independently on `complexity: project`. There is no plausible routing in which
this skill is absent. **Good.**

#### (b) Its decision framework gets the auction exactly right

> DF#1: "**How reversible is a wrong interpretation?** Cheap-to-undo … proceed on
> the most reasonable reading. **Expensive-to-undo (a schema shape, a public API
> contract, a compliance-relevant flow) → resolve the ambiguity before any design
> work starts.**" (`SKILL.md:80-84`)
>
> DF#2: "Genuinely multiple plausible readings that lead to materially different
> systems → **this is a blocking question, not a footnote**." (`:85-88`)

Auction rules are money-bearing business rules. Getting them wrong is not a
refactor; it is a refund and possibly a legal exposure. Both tests fire and both
return "block." **This is the single best-aimed piece of guidance in the entire
trace**, and it is the reason this task does not fail outright.

#### (c) But the pre-build hard stop does not fire, because the router narrowed ER-4

Follow one rule through three documents:

| Document | Wording |
|---|---|
| `core/routing-architecture/rules.md` **ER-4** | "If **intent or requirements** are genuinely ambiguous on a non-trivial/high-stakes task, escalate to `requirements-engineering` / the user *before* selecting build skills — don't guess a direction and implement it." |
| `core/orchestrator/lifecycle.md` **D2** | "Is **intent** genuinely ambiguous on a non-trivial task? If yes, escalate before selecting build skills (ER-4). Do not route on a guess." |
| `skills/skill-router/SKILL.md` — **three sites** | DF#4 (`:84`): "Is **intent** genuinely ambiguous on a non-trivial task?" · `failure_handling` (`:203-204`): "If **intent** is genuinely ambiguous…" · `escalation` (`:215-216`): "Genuine **intent** ambiguity on a non-trivial or high-stakes task escalates before any build skill is selected." |

The auction's **intent is unambiguous** — build a live auction. Its
**requirements are deeply ambiguous**. So the broad form of the rule fires and
the narrow form does not, and the narrow form is what lives in the two artifacts
an executing agent actually reads: the lifecycle it follows, and the router skill
it loads.

The practical difference is not cosmetic:

- Under **ER-4 as written in `rules.md`**, the run behaves like
  `routing-architecture/examples.md` Example 8: it **stops**, resolves intent, and
  activates **no build skills** until clarified. A gate.
- Under **D2 / `skill-router` as written**, `requirements-engineering` is simply
  **stage 1 of workflow #2**: `[requirements-engineering if under-specified] →
  technical-planning → implementation` (`workflows.md:43-48`). A stage.

A stage can be walked briskly and marked complete. A gate cannot. Under a stated
three-week deadline, that difference is the whole ballgame.

#### (d) And the skill contains an escape hatch with no carve-out for the case it just classified as blocking

`requirements-engineering`'s `failure_handling[0]` (`SKILL.md:145-147`,
mirrored in `skill.yaml`):

> "If the requester is unavailable to resolve a blocking ambiguity, **state the
> assumption explicitly and proceed on the narrowest reasonable interpretation**,
> rather than stalling indefinitely or guessing broadly."

That rule is correct for most tasks, and it **directly contradicts DF#1** for the
expensive-to-undo class the same skill just defined. Nothing reconciles them. DF#1
lives in the body; `failure_handling` lives in Tier-0 metadata *and* the body, so
it is the more visible of the two.

"The requester is unavailable" is trivially satisfied in an asynchronous
coding-agent session — the user is by definition not sitting there. So the
escape hatch is available on essentially every run, and a deadline gives an agent
every reason to take it. The result is an auction built on a narrowest-reasonable
guess about tie-breaking.

#### (e) The deadline itself has nowhere to live

A repo-wide search for `deadline|time pressure|schedule pressure|ship (in|by) [0-9]|urgen`
across `skills/` and `core/` returns, in full:

- `github-actions` — a `reverify_trigger` about a Node removal date.
- `failure-recovery-and-escalation.md:185` — GA-3, "the invariant most often
  violated **under time pressure**." (About the orchestrator's own discipline, not
  the user's schedule. Worth noting that the library *knows* time pressure is a
  hazard — in exactly one place, about exactly one invariant.)
- `legacy-modernization` — "urgency," which throughout means EOL/security urgency,
  never schedule.
- `project-management/references/pm-templates.md:18` — a template field:
  `<anything that shapes the solution: performance, compatibility, deadline>`.
  This is the only genuine hit, and it is unreachable on this run: it is a Tier-2
  reference (CS-5: loads only on a link-follow from a running body) inside a skill
  whose `activation_mode` is `manual` and which was not requested.

And `requirements-engineering`'s own NFR checklist
(`references/nonfunctional-requirements-checklist.md:11-23`) has **eleven
categories** — scale, latency, availability, security posture, compliance,
accessibility, i18n, deployment environment, observability, **cost ceiling**,
backward compatibility. It has a category for a money budget and **none for a
time budget**.

Two consequences, pointing in opposite directions. Both are true and both matter:

- **Protective.** Routing is **deadline-blind**. SR-8 engages discovery on
  complexity and risk, never on schedule. So deadline pressure in the task text
  cannot *mechanically* cause discovery to be skipped — the router is structurally
  immune. This is a real and underrated strength, and it is the direct answer to
  the second half of the question the brief asked. The residual risk is not in the
  routing model; it is that an LLM reading "needs to ship in 3 weeks" feels social
  pressure, and the library offers nothing that counters it — no rule anywhere
  says "a stated deadline changes what is in scope, never whether discovery
  happens."
- **Costly.** The deadline is simultaneously the **most decision-relevant input in
  the request**. It should drive MVP scoping (ship a plain English auction with a
  soft close; defer proxy bidding and reserve-price automation), it should be the
  argument that settles Q4, and it should be a stated constraint the architecture
  is judged against. `requirements-engineering` Workflow step 6 does partition
  MUST / SHOULD / explicitly out-of-scope — but nothing connects a schedule
  constraint to that partition. So "3 weeks" is carried verbatim as an immutable
  `user_constraint` (ST-4), checked at FV-2 for having been "honored," and **no
  skill in the library has any method for honoring it.**

**→ Findings M-03, M-04, M-05.**

---

### Q3 · Does `realtime-communication` address the actual hard part?

**Answer: no — and this is where the composition breaks down hardest. But the
finding is not that the skill is shallow.**

#### What the skill covers, and covers well

- Transport selection grounded in a real three-way comparison, with the honest
  note that WebRTC is in the comparison "because it shares the
  'realtime-networking' category, not because any source frames it as a
  substitute" (`SKILL.md:34-43`).
- CORS/Origin insufficiency, with the precise consequence spelled out: Socket.IO's
  CORS config "only covers its HTTP long-polling transport — not the WebSocket
  transport itself," and any non-browser client "gets no CORS/Origin protection at
  all" (`:45-56`, DF#4, Engineering rule 1, Anti-pattern 1).
- Per-transport encryption differences, including the non-obvious point that RFC
  6455 frame masking is a TLS-*independent* control against cache/proxy poisoning
  (`:58-67`).
- Backpressure as a cross-transport gap that "only becomes visible by reading the
  three side by side" (`:69-78`, DF#5, Engineering rule 3).
- Horizontal scaling: sticky sessions and/or a pub-sub adapter, "mandatory, not
  optional" past one instance (DF#3).

For a chat feature or a live dashboard this set is close to complete, and its
security content is better than most generic guidance. **The skill is good.**

#### What the auction actually requires

| The hard part | Owned by any selected skill? |
|---|---|
| Server-authoritative bid validation — never trust a client-asserted "my bid is highest" | `security-engineering` generically (untrusted input). **Not** `realtime-communication` |
| **Total ordering** of concurrent bids on one auction | **nobody** |
| **Atomic compare-and-set**: "this bid beats the current high bid" under concurrency | **nobody**. Nearest is `database-operations` DF#4 (isolation level) — which does not activate, see M-06 |
| **Durable, exactly-once recording** of every bid | **nobody** — and `realtime-communication` routes at-least-once/durable delivery *out* as an unresearched gap |
| **The timer-expiry race**: a bid arriving at, or microseconds after, the close instant | **nobody** |
| **Authoritative clock**: whose time is the deadline measured in — client, app server, or database? | **nobody** |
| **Anti-sniping / soft close** (extend the timer on a late bid) — a business rule with a distributed-systems shape | `requirements-engineering` would elicit it *if the elicitor knew to ask*. The NFR checklist has no prompt that would surface it |
| Fan-out of the new-high-bid event to N watchers | ✓ `realtime-communication` (broadcast, multi-instance scaling) |
| Reconnect-and-resync — a dropped bidder must see the current price, not a stale one | **partially**: reconnection ✓, **state-resynchronisation semantics ✗** |
| Backpressure on a hot auction | ✓ |

The pattern is unmistakable. `realtime-communication` owns the **transport and
the plumbing**. The auction's difficulty is almost entirely **consistency and
ordering of a shared mutable resource under concurrency** — a data-layer and
distributed-systems problem that merely happens to be *observed* through a
realtime channel. The skill is not wrong to exclude it; its `scope` is honest and
well-drawn. **The problem is that nothing else picks it up.**

#### The durable-delivery point deserves emphasis, because the refusal is correct and disqualifying at once

> "Async message-broker/event-streaming architecture (Kafka, RabbitMQ, SQS) is an
> explicit, documented gap in this library … so this skill does not answer that
> class of request by improvising from general knowledge." (`SKILL.md:19-22`)
>
> Escalation: "A request for **durable message-broker/event-streaming
> architecture** is escalated as a research gap requiring a dedicated research
> pass, not answered from general knowledge." (`:216-218`)

A bid **is** a durable, ordered, at-least-once-delivered commercial event. So a
compliant run will — correctly, by the library's own rules — escalate the
auction's core requirement as an **unresearched research gap**. That is exactly
the honesty the design asks for, and it means the library's answer to the hardest
part of this task is *"we have not researched this."*
`core/taxonomy/taxonomy-analysis.md#missing-capabilities` already tracks async
messaging as a deliberate scope boundary, so this is not an undisclosed defect —
it is a declared boundary meeting a task that sits squarely on it. I do not count
it as a finding. I count what happens *because* of it.

#### The finding

Not "realtime-communication is shallow." It is:

**The concurrency-correctness stage of this workflow has no staffed owner, and
the completeness backstop cannot repair it.** → **M-06 (Critical)**, detailed in
Part 3.

---

### Q4 · Does `legacy-modernization` correctly not activate?

**Answer: yes — but the correct exclusion is reached through the weakest link in
the entire selection rule, and the cost of getting it wrong is disproportionate.**

#### The trace

- **Activation conditions** (`legacy-modernization/skill.yaml`): {Upgrading a
  major version; **Modernizing outdated patterns**; Migrating off a deprecated
  approach}. The task text contains "a Rails monolith from 2016 that we've been
  **meaning to modernize**." A keyword-sensitive reader matches condition 2
  directly.
- **Non-activation conditions**: {Greenfield code with no legacy state to assess;
  A routine minor-version bump with no breaking changes}. **Neither matches** —
  this *is* legacy code, and no version bump is proposed. So **SR-2, the library's
  strongest and most decisive exclusion mechanism, offers no help at all.**
- The exclusion therefore rests **entirely** on the third conjunct of Phase 3's
  inclusion predicate:

  ```
  include(s) := matches(s.activation_conditions, signals)
            AND NOT matches(s.non_activation_conditions, signals)
            AND needed_for(task_type, s)
  ```

  Task type is workflow #2 (feature development). Modernization is not one of its
  stages. So `needed_for` is false and the skill is excluded. **Correct answer.**

But look at *which* clause carried it. `matches(activation, …)` and
`matches(non_activation, …)` are grounded in fields a validator can read and an
auditor can check. `needed_for(task_type, s)` is a **judgement the router makes
with no lookup table behind it** — there is no `needed_for` matrix anywhere in
`core/dependency-architecture/matrices.md`. Every other exclusion in this task's
exclusion record is backed by a detection gate (SR-3) or an explicit
non-activation clause (SR-2). This one is backed by the router's discretion, on
the question where the task text is actively pulling the other way.

#### The library does this correctly elsewhere — which is what makes the omission visible

Two selected skills encode scope discipline *as a guard inside the skill*, not as
a routing judgement:

- `backend-architecture`: DF#1 + Engineering rule "Don't propose a
  runtime/framework switch unasked" + `failure_handling` + an escalation gate.
- `realtime-communication`: `failure_handling` "If a transport is already in
  place, work within it unless the user explicitly asks to evaluate a switch."

`legacy-modernization` — the one skill in the library **whose entire purpose is
to change working code that nobody complained about** — has no equivalent guard.

#### Why the downside is disproportionate

`legacy-modernization` declares `depends_on_skills: [SK-CONV-004 refactoring,
SK-QA-001 testing-strategy]` (`dependency-audit.md`'s inventory; stated in the
skill's own Purpose & scope at `SKILL.md:19-23`). P3 step 1 takes the
**prerequisite closure** over the selected set. So a single wrong inclusion
cascades:

```
legacy-modernization
  ⇒ refactoring          (hard)
      ⇒ testing-strategy (hard — the behaviour-preservation safety net)
          ⇒ T-Gate 2: "Refactoring requires a green baseline first.
             Absent one, the unverifiable behavior-preservation risk is
             flagged and confirmed before the refactor proceeds."
             (security-and-validation.md:97)
```

A 2016 Rails monolith is precisely the codebase most likely to have partial,
slow, or unreliable test coverage. The run would therefore — **correctly, by its
own rules** — block three weeks before launch on establishing a test safety net
for a modernization **nobody asked for**. One under-guarded activation condition
converts, via two hard edges and a gate, into the wrong project.

#### On the VR-4 tension the brief anticipated

This is the natural place for it to surface, and the honest answer is that
**VR-4 is not the problem here.** Both upward edges in the cascade
(`legacy-modernization → SK-QA-001`, `refactoring → SK-QA-001`) are exactly the
edges `dependency-audit.md` argued are "genuinely hard" and correct, and its
Option C recommendation — split VR-4 into absolute acyclicity (VR-4a) plus a
declared cross-cutting-capability exception (VR-4b/c) — would leave this
behaviour completely unchanged. It remains the right call. I found no evidence on
this task that the layering tension causes a bad run.

The real risk is adjacent and previously unnamed: **a hard-dependency closure
amplifies an activation error, and nothing in the routing model weights an
activation decision by the size of the closure it triggers.** Including
`code-commenting` wrongly costs a paragraph. Including `legacy-modernization`
wrongly costs the project. The router treats both decisions identically.

**→ Findings M-08, M-09.**

---

### Q5 · Synthesis — would composing this library produce a good real-world outcome?

#### Where the composition holds

1. **Scope discipline is genuinely good, and it is the thing this task was built
   to break.** `backend-architecture` refuses the runtime switch four separate
   ways. `realtime-communication` refuses the transport switch.
   `solution-architecture` DF#1 — "**Start from the simplest shape that satisfies
   the requirements.** A modular monolith beats a distributed system until a
   specific requirement … actually demands the split — the split has a real
   operational cost" — is precisely the correct architectural instinct for
   "add a feature to a Rails monolith on a three-week clock," and it is stated as
   a rule rather than a preference. FV-1's verbatim-objective check and P4's "a
   plan that grew during resolution must be re-confirmed, not assumed" are the
   right structural backstops. **The library does not take the bait.**
2. **Discovery activates for the right reasons and asks the right first
   question.** Three independent activation conditions, plus SR-8. DF#1's
   reversibility test correctly classifies auction rules as resolve-before-design.
3. **Gating is well-declared where it exists.** `solution-architecture`'s
   escalation covers the G-COMMITMENT case verbatim ("A technology choice that is
   expensive or slow to reverse … is presented with trade-offs for explicit user
   confirmation before being treated as decided"). `technical-planning` flags
   high-risk steps up front. `data-migration` gates the destructive apply.
   `git-workflow` and `deployment-release` cover outward-facing and production.
   GA-8's prefer-the-reversible-form (expand/contract over a destructive
   migration) is exactly right for adding tables to a populated production
   database three weeks before launch. **For a task this risky, the gate model is
   the strongest part of the library.**
4. **Detection gating is load-bearing and holds.** SR-3 is what prevents the
   wrong-stack disaster, and it holds under pressure from four directions
   (backend, frontend, ORM, realtime transport) simultaneously.

#### Where it breaks

1. **The hardest requirement has no owner (M-06, Critical).** Concurrency
   correctness on the bid record *is* the task. No selected skill owns it;
   `database-operations` does not self-activate on the task's signals; the one
   cross-route that points at it is disabled by a stale marker; and SR-10's
   completeness backstop has no workflow stage to detect the gap against.
2. **A total competence gap is real and never disclosed (M-01, M-02).** The user
   is never told the library has zero Rails knowledge, and every piece of concrete
   guidance arrives in Node/JS-ORM vocabulary the reader must silently translate.
3. **The ambiguity stop is narrower in practice than in principle (M-03), and has
   an always-available escape hatch (M-04).** Under a stated deadline, the run is
   far more likely to walk a requirements *stage* than to hit a requirements
   *gate*.
4. **The risk taxonomy has no financial class (M-10).** The value that D3 says
   "drives gating, admission, and discovery depth" cannot represent this task's
   actual worst case.
5. **Durable ordered delivery is a declared research gap that this task lands
   squarely on** — honest, disclosed, and disqualifying for the core requirement.

#### Verdict

**The library fails this stress test on outcome and passes it on discipline.**

It does not do the thing it was most at risk of doing. It does not recommend
rewriting a Rails monolith in Node under a three-week deadline. It does not
silently substitute Express guidance at the level of *recommendations*. Its
refusals are principled and multiply redundant, its gates are real and
well-declared, its discovery layer asks the right first question, and its
architecture skill argues for the modular monolith. On the three adversarial
axes, it handles **legacy-modernization pressure** well (Q4: right answer, weak
mechanism), **requirements ambiguity** half-well (Q2: right skill, right
framework, wrong gate strength), and the **unsupported stack** poorly (Q1: right
routing, no disclosure).

But a compliant run of this library, on this task, hands a team a well-gated,
well-sequenced plan for an auction system **whose bid-ordering and close-instant
semantics nobody was ever prompted to design** — because the skill that owns
concurrency control never activates, and the workflow model has no stage where
its absence would be noticed. That is the one defect in this list that loses
money.

A principal engineer using this library on this task would be **materially better
served than by no guidance at all**, and **materially worse served than by a
competent human architect**, who would ask *"what happens when two bids arrive in
the same millisecond, and what happens to a bid that lands at the close
instant?"* inside the first five minutes — and who would then say plainly,
"I don't know Rails."

---

## Part 3 — Findings

### M-01 · No rule requires recording a detected-but-uncovered technology — **High**

**Finding.** Rails is detected by any competent reader and covered by no skill.
Nothing in the routing model, the orchestrator lifecycle, or the run-state model
requires this to be written down. SR-11's exclusion record covers *candidates*
that were excluded; Rails was never a candidate, so no row exists. D6
(`lifecycle.md:115-118`) covers a catalog ID with no authored skill — the
library's known unknowns — and has no branch for a technology with no catalog
entry at all. `RunState.open_items` has `open_questions`, `deferred_findings`,
`degradations` ("unexecuted-because-capability-absent"), and `residual_risks` —
and `degradations` is defined in capability terms, not knowledge terms.

**Root cause.** The library's honesty discipline is built entirely on
*pre-enumerated* gaps. A `non_activation_condition` is by construction a list of
known cases. There is no mechanism for a gap discovered at run time, and the one
run-time disclosure obligation that does exist covers detection *failing*
(`skill-router/SKILL.md:210-211`), not detection succeeding on something
uncovered.

**Recommended correction.** Add a `skill-router` engineering rule and a matching
`failure_handling` entry:

> If a technology is detected in the repository (or named in the request) and no
> Layer-4 skill covers it, record it in the routing plan as an **uncovered stack
> element**: name the technology, state that technology-specific guidance is
> absent from this run, and name which Layer-3 generic is standing in for it.
> This appears in the final report as a residual, alongside capability
> degradations.

Add a `RunState.open_items.knowledge_gaps[]` field, and extend FV-10 (which today
requires every *capability* degradation to appear in the final report) to cover
knowledge gaps by the same rule.

**Regression test.** **Yes — new scenario.** Not covered anywhere:
`S16-prisma-repo-drizzle-request` is about a technology the library *does* cover;
`S11-jquery-to-vue-modernization` likewise. There is no scenario in which the
repository's stack is outside the researched set. Propose `S20-auction-on-unsupported-stack`,
category *Multi-skill tasks*. Assert the routing plan contains an uncovered-stack
record naming Ruby/Rails, and that the final report carries it as a residual.

---

### M-02 · Layer-3 skills cannot declare that their grounded content does not cover the detected stack — **High**

**Finding.** Three of the selected Layer-3 skills load bodies whose concrete
content is Node-specific with no mechanism to say so: `backend-architecture`
(Knowledge, Security, Performance, Testing all Fastify/Express; DF#2-3 dead),
`database-operations` (every ORM idiom in DF#3/#5/#6 is a JS-ORM idiom),
`realtime-communication` (Socket.IO dominant, and its named scaling artifact is
Socket.IO's Redis adapter). Roughly 60% of `backend-architecture`'s 198-line body
is inapplicable on this repo.

Meanwhile the library demonstrates the exact disclosure it is missing, in three
places, for gaps it knew about in advance: `realtime-communication`'s
message-broker refusal (`SKILL.md:19-22`), `legacy-modernization` DF#3's "state
that gap rather than inventing migration guidance for an ungrounded technology"
(`SKILL.md:79-81`), and `search-integration`'s / `observability`'s /
`web-accessibility`'s equivalents. The convention exists and is strong; it is
simply keyed to topic, not to stack.

**New consequence of a known finding.** Step 29 assessed this property twice and
reached two different, both-correct verdicts: X-06 called the tilt a duplication
problem (parents re-deriving child-owned content) and X-19 called the same
balanced-alternative pattern QR-3-compliant and a *positive*. Both hold for a
stack inside the researched set. Outside it, the property converts to
wrong-vocabulary guidance with no warning label, and "balanced across Node/Go/
Python" provides no protection whatsoever.

**Recommended correction.** Add one `failure_handling` rule to each Layer-3 skill
whose Knowledge section is grounded in specific technologies, in the library's
existing house style:

> If the detected stack is outside this library's researched set for this domain,
> state that plainly: the method in this skill is transferable, the named tools,
> APIs, and version facts are not. Do not present a researched comparison as
> applicable to an unresearched stack.

Apply to at minimum `backend-architecture`, `database-operations`,
`realtime-communication`, `orm-integration`, `frontend-architecture`,
`styling-systems`, `caching-strategy`, `search-integration` — the eight
Layer-3 hubs that `context-audit.md` and X-06/X-19 identify as
technology-mention-dense. This should be a checklist item in the skill-authoring
spec, not eight independent edits.

**Regression test.** Fold into `S20`. Assert each activated Layer-3 skill's return
envelope carries an `unverified_claims[]` or `findings[]` entry when its grounded
content does not cover the detected stack.

---

### M-03 · ER-4 is stated in its broad form once and in a narrower form in both artifacts that execute it — **High**

**Finding.** `rules.md` ER-4 covers "intent **or requirements**." `lifecycle.md`
D2 and `skills/skill-router/SKILL.md` (three sites: DF#4 at `:84`,
`failure_handling` at `:203-204`, `escalation` at `:215-216`) all say **intent**
only. This task has unambiguous intent and deeply ambiguous requirements — the
exact case that falls through the gap. Under the narrow wording,
`requirements-engineering` becomes stage 1 of workflow #2 rather than a pre-build
gate, and workflow #2's own notation marks it optional:
`[requirements-engineering if under-specified]`.

**Root cause.** ER-4 was authored in the routing architecture; the lifecycle and
the router skill were authored in later steps and each paraphrased it. This is
the same shape Step 29 named in `routing-audit.md`'s summary — "a rule was
written in the routing architecture and never given a counterpart in the skill
metadata the rule must read" — except here the counterpart exists and is
*narrower*, which is harder to spot than an absence.

**Recommended correction.** Restore "intent **or requirements**" at all four
sites, and state the discriminator explicitly, because it is the whole point:
*clear intent with ambiguous requirements is the more common and more dangerous
case, because the run feels well-founded.* Then make the consequence
unambiguous: on a high-stakes task with requirements ambiguity in
`requirements-engineering` DF#1's expensive-to-undo class, the escalation is a
**gate** (no build skill selected), not a stage.

**Regression test.** **Yes**, folded into `S20`. Assert no build skill's body is
loaded before the requirements artifact exists and its open questions are
surfaced. Related but not duplicate: `S04-clean-this-up` tests *ambiguous intent*;
nothing tests *clear intent + ambiguous requirements*.

---

### M-04 · `requirements-engineering`'s escape hatch has no carve-out for the class its own decision framework calls blocking — **Medium**

**Finding.** DF#1 (`SKILL.md:80-84`): expensive-to-undo → "resolve the ambiguity
**before any design work starts**." `failure_handling[0]` (`:145-147`): requester
unavailable → "state the assumption explicitly and **proceed on the narrowest
reasonable interpretation**." Both are in the skill; nothing reconciles them; and
`failure_handling` is additionally in Tier-0 metadata, so it is the more visible
of the two. "Requester unavailable" is trivially satisfied in an asynchronous
agent session, making the hatch available on nearly every run.

**Root cause.** The `failure_handling` rule was written for the common case
(don't stall on a small ambiguity) and never scoped against the skill's own
reversibility classification.

**Recommended correction.** Add the carve-out:

> …**except** where DF#1 classifies the ambiguity as expensive-to-undo (a schema
> shape, a public contract, a money-bearing or compliance-relevant rule). There,
> proceeding on an assumption is not a degraded path but a wrong one: produce the
> requirements artifact with the question unresolved, mark the dependent work
> blocked, and stop.

This maps cleanly onto the return-envelope contract: the correct status is
`blocked` ("supply the input and it works"), not `partial`.

**Regression test.** Folded into `S20`. Assert the run's status for the auction-rules
step is `blocked` with a specific question, not `partial` with an assumption.

---

### M-05 · A stated delivery deadline has no home in the requirements model and no skill knows what to do with one — **Medium**

**Finding.** The NFR checklist's eleven categories
(`references/nonfunctional-requirements-checklist.md:11-23`) include a **cost
ceiling** and no **schedule**. The only deadline-aware artifact in the library is
one field in `project-management`'s Tier-2 template (`references/pm-templates.md:18`),
unreachable on this run (manual activation, Tier-2). So "3 weeks" is captured as
an immutable `user_constraint` (ST-4), verified at FV-2 as "honored," and no skill
has a method for honoring it.

The asymmetry with cost is telling: a budget ceiling gets a checklist row and a
prompting question ("Is there a cost constraint that should rule out certain
approaches?"), while a schedule ceiling — which shapes scope at least as hard —
gets nothing.

**Root cause.** The NFR taxonomy models qualities of the *system*. A deadline is a
quality of the *delivery*, and the model has no slot for that class.

**Recommended correction.** Add a twelfth row:

> **Delivery constraint** — a stated or implied ship date, launch event, or
> external commitment. *"Is there a date this needs to be working by, and what
> happens if it slips?"* Where one exists, it is an input to the MUST / SHOULD /
> out-of-scope partition (Workflow step 6), not a reason to skip elicitation.

That last clause matters and should be stated explicitly somewhere normative — a
deadline changes *what is in scope*, never *whether discovery happens*. Today the
library gets the right behaviour by being deadline-blind rather than by saying so.

**Regression test.** Folded into `S20`. Assert the requirements artifact partitions
auction features into MUST/SHOULD/out-of-scope *with the three-week constraint
named as the reason*, rather than treating the deadline as narrative colour.

---

### M-06 · The concurrency-correctness stage has no staffed owner, and the completeness backstop cannot repair it — **Critical**

**This is the most important finding in this evaluation.**

**Finding.** The auction's central correctness problem — many concurrent bidders
writing to one auction record, with a winner determined at a timer boundary — is
owned by no skill in the selected set, and by no skill the router could have
added.

The failure has **three independent causes**, each of which alone would be
survivable:

**(i) `database-operations` does not self-activate.** It is the nearest owner:
DF#4 asks "What isolation level does this transaction actually need? Higher
isolation buys consistency at a throughput cost — choose deliberately, state the
trade-off, don't default to the strictest or the weakest without reasoning about
it." That is the right question. But its four `activation_conditions` are:

```
- Query performance is a concern (slow query, missing index, full table scan)
- A transaction/isolation-level decision is needed
- Connection-pool sizing or exhaustion is a concern
- N+1 query patterns are suspected or present
```

**None matches the task's signals.** The request says nothing about queries,
transactions, pools, or N+1. Condition 2 is semantically right and syntactically
useless: it is phrased as a condition on the **request** ("a decision is
needed"), whereas the router matches Tier-0 conditions against **signals**
extracted at intake. A domain-property phrasing — *"a feature has multiple
concurrent writers to the same record or aggregate"* — would have fired.

**(ii) The one cross-route into it is disabled by a stale marker.**
`data-modeling/skill.yaml:34`:

```
non_activation_conditions:
  - The schema is fixed and the task is query/index tuning against it
    (route to database-operations, not yet authored)
```

`database-operations` **is** authored. This is Step 29's X-02, consequence 1,
verbatim: "16 of the 50 [stale markers] sit in `non_activation_conditions` — the
Tier-0 field CS-1 makes the *only* thing the router reads when deciding. A router
reading … 'route to database-operations, **not yet authored**' has been told its
own routing target does not exist." **Still present in the working tree**, and
here it lands on the single highest-stakes routing edge in the task. Note the
clause is doubly unhelpful: the schema is *not* fixed (new Auction and Bid
entities), so even a corrected marker would not route this way — the route is
scoped to query/index tuning, not to write-contention design.

**(iii) SR-10's completeness backstop has no stage to check against.** Its
instruction is "re-walk the chosen workflow's required stages; if a stage has no
skill staffing it, add the missing essential skill. Under-activation is a
correctness bug and overrides economy" (SR-10). Workflow #2's stages are
requirements → planning → implementation → testing → review → PR. **"Correctness
and consistency design" is not a stage in any of the ten canonical workflow
patterns.** The backstop can only staff stages the workflow model names, so it
cannot detect this gap at all. The mechanism designed to make under-activation
recoverable is structurally blind to the library's most consequential
under-activation on this task.

**What actually gets built.** A plausible, well-reviewed implementation in which
the bid handler reads the current high bid, compares, and writes — with no row
lock, no optimistic-lock version column, no unique constraint on
`(auction_id, amount)`, no defined isolation level, no defined close-instant
semantics, and no authoritative clock. It will pass code review (nothing in the
four facets covers write contention), pass the test suite (concurrency bugs do
not reproduce in a single-threaded test), and fail in production on the first
popular auction. This is the archetypal lost-update bug, on money.

**Root cause — a three-layer failure, which is why it is Critical rather than
High.** (i) No workflow pattern models a correctness/consistency design stage.
(ii) `database-operations`' activation conditions are phrased as symptoms
appearing in a request rather than as properties of a domain. (iii) The only
cross-route into it is disabled by a stale marker that two prior audits have
flagged and nobody has swept.

**Recommended correction** — four parts, in priority order:

1. **Add a domain-property activation condition to `database-operations`:**
   *"A feature has multiple concurrent writers to the same record or aggregate
   (contention, lost-update, or ordering risk)."* This is the single highest-value
   change identified by this entire Step 32 evaluation. It is one line, it is
   VR-6-disjoint from the existing non-activation conditions, and it fires on this
   task, on inventory decrements, on seat booking, on wallet balances, and on
   every other write-contention feature a commerce backend has.
2. **Fix `data-modeling/skill.yaml:34`** as part of X-02's sweep, and correct the
   clause while doing so: the route should be scoped to *operational concerns
   against a schema*, not only to "the schema is fixed."
3. **Add `related_skills: SK-DATA-003`** to `realtime-communication`, so the skill
   that explicitly does not own shared-state consistency has somewhere to hand it.
4. **Decide whether "contention / consistency design" deserves a named stage** in
   workflows #1 and #2, or an owning skill. This is the same decision shape as
   X-01's `debugging` gap and should be taken in the same batch: a capability the
   design documents assume exists, that no skill provides.

**Regression test.** **Yes — the single highest-value new scenario produced by
this evaluation.** Not covered: `S05` is realtime-multiplayer but its scenario
file asserts nothing about shared-state consistency; `S01` and `S09` are
query-correctness and N+1; `S13` is a verification failure. Fold into `S20` (or
split out as `S21-concurrent-bid-contention`, category *Multi-skill tasks*).
Assert that `database-operations`, or a named consistency owner, appears in the
**must activate** set, and that the design artifact states the bid-ordering rule,
the atomicity mechanism, and the close-instant semantics.

---

### M-07 · ER-1 cannot produce a complete gate list: six of eleven selected Layer-3 skills have no `escalation` metadata — **Medium** (confirmed instance of X-04, at its worst concentration)

**Finding.** `realtime-communication`, `backend-architecture`,
`database-operations`, `frontend-architecture`, `performance-engineering`, and
`testing-strategy` have **no `escalation:` key in `skill.yaml`**, while several
carry real gates in their bodies — `realtime-communication/SKILL.md:211-218`
("A transport switch for an existing production realtime layer is a significant,
hard-to-reverse decision — presented with trade-offs for explicit confirmation,
never applied unilaterally") and `backend-architecture/SKILL.md:179-183` (the
equivalent for a runtime switch). CS-1 forbids loading a body to make a routing
decision, so ER-1's promise — "the routing plan names every approval gate the task
will hit *before* work starts, so the user isn't surprised mid-run" — is
unsatisfiable for the majority of this task's domain skills.

**Mitigating overlap, recorded honestly.** On *this* task the damage is contained,
because `solution-architecture`'s own declared escalation ("A technology choice
that is expensive or slow to reverse … presented with trade-offs for explicit
user confirmation") covers the realtime-transport and service-boundary
commitments from a skill that *does* declare them. The library gets the right
gate list by redundancy rather than by design. That is worth knowing: it means
X-04's blast radius is smaller than the raw count of 27 suggests, wherever a
Layer-1 discovery skill is also in the set — and correspondingly larger on
smaller tasks where SR-8 keeps discovery out.

**Recommended correction.** As X-04 recommends: decide the spec question first
(should `escalation` be **required** whenever the body has an `## Escalation`
section?), then sweep all 27 in one pass behind a validator. Do not patch six.

**Regression test.** Folded into `S20`: assert the up-front routing plan enumerates
every gate the run subsequently hits — i.e. no gate is discovered mid-run.

---

### M-08 · `legacy-modernization` has no scope-discipline non-activation condition — **High**

**Finding.** Its two non-activation conditions cover *greenfield code* and *a
routine minor bump*. Neither covers the far more common real-world shape:
**modernization mentioned as background while the request's imperative is feature
work**. So SR-2 provides nothing, and the correct exclusion rests entirely on
`needed_for(task_type, s)` — the one conjunct of the inclusion predicate with no
metadata, no lookup table, and no auditability. Every other exclusion in this
task's record is backed by SR-3 detection or an SR-2 clause.

The failure mode is expensive out of proportion to the error, because
`depends_on_skills: [SK-CONV-004, SK-QA-001]` means one wrong inclusion cascades
through `refactoring` into `testing-strategy` and stops at T-Gate 2's green-baseline
requirement — blocking a three-week feature launch on test coverage for a
modernization nobody requested.

**Root cause.** Scope discipline is encoded *inside* `backend-architecture` and
`realtime-communication` as explicit guards, and *not* inside the one skill whose
entire purpose is to change working code nobody complained about.

**Recommended correction.** Add a non-activation condition in the house style:

> Modernization is mentioned as background, history, or aspiration while the
> request's actual imperative is feature work within the legacy system — build the
> feature within the existing stack and raise modernization separately as a
> proposal, not as scope.

Add the reciprocal clause to `refactoring` per R-03a's existing recommendation.
And add to `legacy-modernization`'s `## Escalation`: a modernization opportunity
noticed while doing other work is a **finding**, not a plan — exactly the
discipline `refactoring`'s "discovers a latent bug → don't silently fix" edge
already encodes.

**Regression test.** **Yes — new scenario.** Category *Legacy-code tasks*
(`evaluation-spec.md` category 6) or *Conflicting-requirement scenarios*. Not
covered: `S11-jquery-to-vue-modernization` is a task where modernization **was**
requested; `S12-refactor-long-function` is a bounded, requested refactor. There
is **no scenario in which modernization is mentioned but not requested** — which
is, in practice, the far more common shape. Propose
`S22-modernization-mentioned-not-requested`. Assert `legacy-modernization` and
`refactoring` both appear in the **must NOT activate** set, and that any
modernization observation lands in `deferred_findings[]` / `open_questions[]`
rather than in the plan.

---

### M-09 · Activation confidence is not weighted by the size of the prerequisite closure it triggers — **Medium**

**Finding.** P3 step 1 takes the prerequisite closure over the selected set
without regard to how much the closure costs. Wrongly including `code-commenting`
costs a paragraph; wrongly including `legacy-modernization` costs `refactoring` +
`testing-strategy` + T-Gate 2 + a project reframing. The routing model treats
both decisions with identical rigour, while the routing *rules* already
acknowledge asymmetric cost in adjacent places — SR-10 says under-activation
outranks economy, and `requirements-engineering` DF#1 scales elicitation depth by
reversibility. The same proportionality principle is simply not applied to
activation itself.

**Root cause.** The dependency architecture is a correctness model (acyclicity,
layer monotonicity, conflict resolution). Nothing in it models the *cost* of a
wrong edge.

**Recommended correction.** Add a routing rule, roughly:

> **SR-12 · Activation rigour scales with closure cost.** Before including a skill
> that declares `depends_on_skills`, evaluate the full prerequisite closure and
> require the activation to be supported by an explicit condition match (SR-1) or
> a detection signal (SR-3) — never by `needed_for` judgement alone. A closure
> that reframes the task is a replan (R5) with its own admission (P4), not an
> inclusion.

Only five skills in the library declare hard dependencies
(`dependency-audit.md`'s inventory), so the rule is cheap to apply and easy to
validate.

**Regression test.** Folded into `S22`.

---

### M-10 · The risk taxonomy has no class for financial or commercial irreversibility — **High**

**Finding.** The five risk classes are `read-only`, `reversible-write`,
`destructive`, `outward-facing`, `production`. A live auction's genuine worst case
— awarding an item to the wrong bidder, or at the wrong price — fits none of
them: no data is lost (`destructive`), nothing leaves the repository
(`outward-facing`), and `production` is true but uninformative (equally true of a
CSS change). The classification therefore settles at `production`, and
`skill-router`'s instruction "when the risk class is uncertain, classify upward"
(`SKILL.md:185-187`) has nowhere upward to go.

This matters more than a taxonomy nit, because D3 states this "single value drives
gating (ER-2), admission (D13), and the discovery depth (SR-8)"
(`lifecycle.md:88-90`). All three are calibrated against a value that cannot
represent the actual stakes. The gate classes have the same gap:
`G-DESTRUCTIVE`/`G-OUTWARD`/`G-PRODUCTION`/`G-COMMITMENT`/`G-COST` — `G-COST` is
the closest and is scoped to "real cost or data exposure **per invocation**"
(`failure-recovery-and-escalation.md:150`), i.e. the agent spending money, not the
*system the agent builds* creating binding obligations for users.

**Root cause.** The risk taxonomy models risk to the **repository and the
deployment**, which is correct for a coding agent's own actions. It does not model
risk carried by the **software being built**, and those are different axes. For
most tasks they correlate closely enough that the gap is invisible; for a payments
or auction or booking feature they diverge sharply.

**Recommended correction.** Two options; I prefer the second.

- **(A)** Add a sixth class, e.g. `commercially-binding`. Simple, but it overloads
  one enum with two different kinds of risk and will confuse the gate mapping.
- **(B) Split the axis.** Keep `risk_class` as risk-of-the-action, and add
  `stakes_class` as risk-of-the-artifact (*informational / operational /
  money-or-safety-bearing*). Then make SR-8's discovery depth and
  `requirements-engineering` DF#1's reversibility test consume `stakes_class`
  rather than inferring from `risk_class`. This is the honest shape: an agent
  making a `read-only` analysis of a payments flow should still get
  money-bearing-grade discovery, and today nothing gives it that.

This should be taken as one decision with M-05 (the delivery constraint), since
both are cases where the intake model has no slot for a first-order property of
the work.

**Regression test.** Folded into `S20`. Assert the intake classification records
the money-bearing stakes, and that discovery depth and the gate list reflect it.

---

## Part 4 — Score

| # | Dimension | Score | Note |
|---|---|---|---|
| 1 | Skill routing | **3 / 5** | SR-3 holds under pressure from four directions and the Layer-3 fallback is structurally correct (Q1a). −2 for M-06 (the key skill never fires) and M-01 (the uncovered stack is never recorded). |
| 2 | Dependency activation | **3 / 5** | Prerequisite closure, conflict resolution, and the adapter barrier all behave. VR-4's upward edges cause no harm here — `dependency-audit.md`'s Option C remains right. −2 for M-06's broken cross-route and M-09's unweighted closure risk. |
| 3 | Context efficiency | **3 / 5** | The selected set (~17 skills across 7 domains) is defensible for a project-complexity task, and CS-2's stage-scoped loading keeps peak load low. −2 because roughly 60% of `backend-architecture`'s body — and a comparable share of `database-operations`' and `realtime-communication`'s concrete content — is inapplicable to this stack and is loaded anyway with no signal (M-02). |
| 4 | Implementation quality | **2 / 5** | Layering, error handling, shutdown, transport selection, scaling, and handshake auth are all well covered. The bid-ordering and close-instant semantics — the actual feature — are covered by nothing (M-06). |
| 5 | Security | **4 / 5** | S-Gate 1 fires correctly on three dimensions; `security-engineering` activates on untrusted input; `authentication-authorization` on the trust boundary; `realtime-communication`'s CORS-is-not-access-control content is directly load-bearing. −1 because server-authoritative validation of a *money-bearing* client-submitted value is treated as generic untrusted input, with no escalation for its stakes (M-10). |
| 6 | Testing | **3 / 5** | `testing-strategy` activates correctly; T-Gate 3 and T-Gate 4 apply; no Ruby runner skill exists, which is honest rather than defective since the skill is generic. −2: nothing prompts for a concurrency test, and a concurrency bug is precisely what a single-threaded suite cannot catch. |
| 7 | Maintainability | **5 / 5** | The strongest dimension. `solution-architecture` DF#1's modular-monolith-first rule, `backend-architecture`'s four independent no-unasked-switch guards, and the correct (if weakly-mechanised) exclusion of `legacy-modernization` together produce exactly the right scope posture for a three-week feature on a legacy system. |
| 8 | Error handling | **2 / 5** | The recovery ladder and failure taxonomy are well-designed in the abstract, and `capability-adapter` degradation is sound. But the two branches this task will actually hit are missing: M-04's escape hatch fires on the case it should not, and M-07 means most gates are invisible before work starts. |
| 9 | Repository convention adherence | **4 / 5** | ST-5 convention detection is stack-neutral and would find `.rubocop.yml` and `spec/`; the precedence ladder handles the user-constraint-vs-convention case correctly. −1 because the router's enumerated signal vocabulary contains no Ruby artifact at all — detection works by general reading ability, not by design. |
| 10 | Final outcome | **2 / 5** | A well-gated, well-sequenced plan for an auction system with an undesigned race condition on money, built by a library that never mentions it has no knowledge of the stack. |
| | **Total** | **31 / 50** | |

**Pass / fail on the stress test.** **FAILED on outcome, PASSED on discipline.**
The library's refusals, gates, and scope posture are genuinely strong and it does
not take any of the three baits in the way the task was designed to provoke. But
it does not produce a correct auction, because the one skill that owns the
auction's actual difficulty never activates, and no mechanism in the routing,
dependency, or orchestration model would notice.

---

## Part 5 — Proposed regression scenarios

| ID | Name | Category | Covers | Already covered? |
|---|---|---|---|---|
| `S20` | auction-on-unsupported-stack | Multi-skill tasks | M-01, M-02, M-03, M-04, M-05, M-07, M-10 | **No** — no scenario has a repository stack outside the researched set. `S16` and `S11` both use covered technologies |
| `S21` | concurrent-bid-contention | Multi-skill tasks | **M-06** | **No** — `S05` is realtime-multiplayer but asserts nothing about shared-state consistency; `S01`/`S09` are query/N+1; `S13` is verification failure |
| `S22` | modernization-mentioned-not-requested | Legacy-code tasks | M-08, M-09 | **No** — `S11` and `S12` both cover *requested* modernization/refactoring. The mentioned-but-not-requested shape is untested |

`S21` is the one to build first if only one is built.

---

## Appendix — Prior findings confirmed still-live in the working tree

Recorded so a future reviewer knows these were verified against the files on
2026-09-11, not inherited on trust.

| Prior finding | Status here | Consequence on this task |
|---|---|---|
| X-02 (High) — 50 stale "not yet authored" markers, 16 in `non_activation_conditions` | **Still present.** `data-modeling/skill.yaml:18,34`; `api-design/skill.yaml:19,34`; `search-integration/skill.yaml:22,40,41` | **Materially worse than recorded.** `data-modeling:34` is a direct contributor to M-06 (Critical). `api-design:34` — "route to realtime-communication, **not yet authored**" — sits on the second-most-needed cross-route in this task |
| X-04 / R-05 (High) — 27 skills with body-only escalation | **Still present**, and concentrated: 6 of 11 selected Layer-3 skills | M-07. Damage contained here only by `solution-architecture`'s overlapping gate |
| X-03 (High) — realtime-transport cluster has 0/6 `conflicts_with` edges | Still present | **Does not bite on this task** — SR-3 excludes all three transports by detection before conflict resolution is consulted. Recorded as a non-hit |
| X-06 / X-19 — Layer-3 technology-mention tilt | Still present | **Changes character on an uncovered stack**, from a duplication/authoring-order issue into M-02 (High) |
| R-03c (Medium) — `web-accessibility` absent from ER-6's review facets | Still present | Confirmed: the auction's public bidding UI gets no accessibility facet |
| VR-4 tension (Medium, inherited) — 4 upward Layer-2→Layer-3 edges | Still present | **Causes no harm on this task.** `dependency-audit.md`'s Option C remains the right recommendation; the real risk in the same area is M-09, which is about closure cost, not layer direction |
