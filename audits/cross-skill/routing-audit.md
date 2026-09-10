# Routing Audit (Step 29)

Companion to [`cross-skill-audit.md`](cross-skill-audit.md). Covers check 7
(routing ambiguity and unresolved activation overlaps), check 15 (missing
escalation paths), and check 16 (missing review loops) — the last two
belong here because both are routing/workflow-completeness concerns rather
than per-skill content defects.

Method: read `core/routing-architecture/` in full (README, algorithm,
rules, examples), then stress-test the default-deny model against the
actual 86 skills' `activation_conditions` / `non_activation_conditions` /
`conflicts_with` as authored — not against the catalog's description of
them. Every task below is a request a real user would plausibly type.

**Standing caveat** (per `core/orchestrator/self-review.md` R-1): nothing
here is enforced by a runtime. These are findings about a specification's
internal consistency, not observed misbehavior. The router has never run.

---

## What the routing model gets right

Stated first because it is the larger half of the result, and because
several findings below are only visible *because* the rest is so precise.

- **Cross-routing discipline is excellent.** The dominant pattern in
  `non_activation_conditions` is an explicit "route to X" naming the
  sibling that owns the case. Reciprocal, unambiguous pairs include
  `skill-router` ↔ `technical-planning` ↔ `workflow-composer` (all three
  directions, all three skills), `requirements-engineering` ↔
  `solution-architecture`, `api-design` ↔ `graphql-api-design`,
  `security-engineering` ↔ `authentication-authorization` ↔ `ai-security`,
  `llm-evaluation` ↔ `testing-strategy`, `caching-strategy` ↔
  `database-operations` ↔ `performance-engineering`, `styling-systems` ↔
  `ui-ux-design` ↔ `frontend-architecture`, `rag-engineering` ↔
  `search-integration`, `code-commenting` ↔ `technical-documentation`.
  This is what SR-2 needs to work, and it is present far more often than
  not.
- **VR-6 and VR-7 hold exactly.** No skill's activation and non-activation
  sets intersect; no two skills across the library share an identical
  activation trigger. Both checked mechanically, 0 violations.
- **SR-3 detection gating is concrete.** Technology skills name real
  detection signals (`angular.json`, `go.mod`, `pyproject.toml`,
  `require('express')`, `@fastify/*`, a `postgres://` string) rather than
  vague topical matches. This is the single biggest defense against
  over-activation in a 40-technology library and it is done well.
- **Honest scope refusals route rather than guess.** `observability`
  refuses resilience-pattern requests, `realtime-communication` refuses
  message-broker architecture, `web-accessibility` refuses WCAG
  conformance-certification depth — each naming the gap instead of
  extrapolating.

---

## R-01 · The router's normative source names skills that do not exist — High

`routing-architecture/examples.md` opens by declaring that its skill IDs
are taken from `core/taxonomy/skill-catalog.md`. That catalog contains six IDs
with no authored skill (see X-05), and the routing examples use them —
including in **selected** sets, not just exclusion tables:

| Site | Uses | As |
|---|---|---|
| Example 2 (the mandated "realtime multiplayer game" case) | `rendering-strategy` | **selected**, in the parallel frontend branch |
| Example 5 ("why is our Next.js page slow") | `rendering-strategy` | **selected**, twice |
| Example 1 | `rendering-strategy`, `web-monetization` | excluded |
| Example 2 | `google-seo`, `google-adsense`, `web-monetization` | excluded |

Both mandated examples in the brief therefore describe a routing the
library cannot actually produce. This is not a new gap —
`SK-FE-005` is Step 28's finding — but it is a materially worse
*consequence* than the 12 cross-reference sites Step 28 counted: the
worked proofs that the routing model produces correct sets are themselves
unproduceable.

Example 3 also states the router excludes "all 68 other skills"; there are
85 others.

**Recommendation:** whichever way the `SK-FE-005` decision goes (author it,
or drop it), `examples.md` must be re-run afterward. If `SK-FE-005` is
dropped, Examples 2 and 5 need a real owner for the rendering-mode
decision — most plausibly `frontend-architecture` plus the framework
skill — and that reassignment is a taxonomy decision, not an edit.

## R-02 · The debugging intent has no skill to route to — High

The router classifies `debug` as one of its twelve intents
(`README.md` determination 1) and `workflows.md` defines Debugging as
canonical pattern #4. No skill owns it (X-01). The consequences are
routing-specific and worth stating separately from the missing-capability
finding:

- **SR-10 (completeness backstop) cannot fire.** Its instruction is
  "verify every required stage of the chosen workflow is staffed; add any
  missing essential skill." For workflows #3 and #4 there is no skill to
  add. The backstop that makes under-activation recoverable is inert for
  two of ten workflow patterns.
- **ER-5 points at nothing, twice.** "a bug found while refactoring →
  `code-review`/`bug-fixing`"; "a root cause found while debugging →
  `bug-fixing`". `refactoring`'s own `conflicts_with` prose says it "hands
  off rather than silently fixing" — the hand-off target does not exist,
  so the discipline has nowhere to land.
- **Example 5 selects an unattributed loop.** `⟳ debugging loop
  { hypothesize → measure → narrow }` appears in a selected set with no
  skill ID, which no other element of any example does.

---

## R-03 · Four unresolved activation overlaps

The default-deny model resolves an overlap when at least one of the two
skills names the other in `non_activation_conditions` (SR-2). These four
pairs overlap on realistic tasks with **no cross-route in either
direction** and **no `conflicts_with` edge**.

### R-03a · `code-quality` vs. `refactoring` — Medium, with a safety consequence

**Task: "This module is a mess — there's duplicated logic all over it.
Clean it up."**

| | fires? | why |
|---|---|---|
| `code-quality` (SK-CONV-003, Tier A) | ✅ | activation: "Dead code, duplication, or an over-abstracted structure is suspected" |
| `refactoring` (SK-CONV-004, Tier B) | ✅ | activation: "A change is blocked by structural debt"; the requested work *is* behavior-preserving restructuring |

Neither names the other in non-activation. Neither declares a conflict.
`code-quality`'s non-activation excludes only throwaway snippets and
explicit spikes; `refactoring`'s excludes only new-feature work and
unverifiable-behavior cases.

This one matters more than an ordinary ambiguity because **the two skills
carry different safety obligations for the same operation.** `refactoring`
requires a test safety net or an explicit statement of its absence — that
requirement is its declared scope and the reason it hard-depends on
`SK-QA-001`. `code-quality` has no such requirement. If the router picks
`code-quality` for a task that is materially a refactor, the safety net
disappears silently. The failure is invisible: both skills produce
plausible, well-formed output.

**Recommendation:** add a boundary to both. `code-quality` should
non-activate on "restructuring existing working code where behavior must
be preserved (route to `refactoring`, which owns the safety-net
discipline)"; `refactoring` should non-activate on "naming, dead-code
removal, or readability cleanup inside code being newly written (route to
`code-quality`)." The clean line is *existing behavior at risk* vs. *code
being authored now*.

### R-03b · `observability` vs. `performance-engineering` — Medium

**Task: "Our API's p99 latency spiked in production yesterday. Figure out
why."**

| | fires? | why |
|---|---|---|
| `observability` (SK-QA-004) | ✅ | activation: "Debugging a production issue that needs logging/metrics/tracing evidence" |
| `performance-engineering` (SK-QA-003) | ✅ | activation: "A performance problem or budget is in play"; "A diagnostic (profiling, benchmarking) is needed before optimizing" |

`performance-engineering`'s non-activation carefully routes out the
database and caching cases; it says nothing about observability.
`observability`'s non-activation routes out local code and resilience
patterns; it says nothing about performance. They are `related_skills` of
each other, which signals composition but resolves no precedence.

The boundary is real and expressible — observability owns *making the
system emit evidence*, performance owns *interpreting evidence to find the
dominant cost* — and both skills' bodies clearly understand it. It is just
not in the routing metadata, and this is a top-5 most common production
task. Compounded by R-02: the diagnostic loop that ought to sequence them
has no owner.

**Recommendation:** add reciprocal non-activation clauses on the
instrument-vs-interpret line. If a `debugging` skill is authored (X-01),
it becomes the natural sequencer and this resolves as a by-product.

### R-03c · `web-accessibility` is absent from the review-facet model — Medium

**Task: "Review this UI component."**

`ui-ux-design` fires ("A frontend design review is requested", "A UI's
hierarchy, layout, or interaction states need review").
`web-accessibility` does **not** — its review trigger is "An accessibility
audit or review is **requested**", i.e. it needs to be named. So a generic
UI review silently omits accessibility.

That would be a defensible economy except that ER-6 enumerates the review
facets and accessibility is not among them:

> any authored code → quality + comment facets; a trust-boundary change →
> security facet; a hot-path/budget change → performance facet.

There is no facet for UI work at all, while `matrices.md`'s
parallelization table explicitly treats `web-accessibility` as a
parallel-safe audit facet ("seo-optimization ∥ web-accessibility (both
audit rendered pages)"). One matrix models a11y as a review facet and the
escalation rules do not list it.

This is an **under-activation** finding, which operating principle 7 and
SR-10 both classify as a correctness bug outranking economy.

**Recommendation:** extend ER-6 with a fourth conditional facet — "a
user-facing UI change → accessibility facet" — and add a matching
activation condition to `web-accessibility` ("a review of user-facing UI
markup or components, whether or not accessibility is named"). The
non-activation guard ("backend/non-UI work") already prevents over-reach.

### R-03d · `legacy-modernization` vs. `data-migration` — Low

**Task: "Upgrade us from Prisma 6 to Prisma 7."**

Both fire — `legacy-modernization` on "Upgrading a major version",
`data-migration` on "A version upgrade of the database/ORM carries a
breaking schema-relevant change" (and Prisma 6→7 does: `data-migration`'s
own Knowledge section documents that Prisma 7 drops MongoDB support).

The guard is **asymmetric**: `data-migration` routes broad modernization
out to `legacy-modernization`; `legacy-modernization` says nothing about
`data-migration`. In practice the asymmetry resolves the common case in
the right direction, and both skills are individually correct about their
scope, so this is Low. Worth a reciprocal clause when the stale-marker
sweep (X-02) touches `data-migration` anyway.

---

## R-04 · Polyglot repositories are actively mis-excluded — Medium

A distinct class from R-03: not an overlap, an over-broad guard.

`go`, `python`, and `nodejs` declare `conflicts_with` on each other
(6 edges). The conflict matrix's own framing is "must not co-activate
**for the same decision/artifact**", and the sibling clusters honor that
scoping — `express ⊥ fastify` is qualified "one Node framework", the ORM
cluster "one data-access layer". The runtime cluster is not scoped at all,
and two of the three non-activation conditions are written as if a
repository has exactly one runtime:

| Skill | Non-activation, as authored | Scoped? |
|---|---|---|
| `go` | "The stack uses **Node.js or Python** (route to that runtime's skill)" | ❌ |
| `nodejs` | "The stack runs on **Go, Python, or another non-Node runtime**" | ❌ |
| `python` | "The stack uses another language/runtime (Node.js, Go, etc.) **with no Python component**" | ✅ |

Now apply **SR-2** — "Non-activation is decisive. If a skill's
non-activation conditions match the signals, exclude it — **even if its
activation also matches**."

In a repository containing both a Go service and Python tooling (or a Node
API and a Python ML service — an extremely common shape), a Go task
detects `go.mod` *and* detects `pyproject.toml`. `go`'s activation fires;
`go`'s non-activation *also* fires; SR-2 excludes it. The correct skill is
removed from its own task.

`python`'s phrasing ("with no Python component") is immune, which shows
the right wording already exists in the library — the three siblings are
just inconsistently scoped.

**Recommendation:** re-scope `go`'s and `nodejs`'s runtime guards to match
`python`'s component-based form, and add the "same service/artifact"
qualifier to the runtime cluster in the conflict matrix. Genuinely narrow,
but re-scoping a non-activation condition changes routing behavior on
every polyglot repo, so it is a decision rather than a typo fix. Related
to X-03, which found the reverse problem (declared conflicts absent from
the matrix) in the same cluster.

---

## R-05 · Missing escalation paths (check 15)

### The central finding: ER-1 is unimplementable for 27 skills

Restated here in routing terms; full evidence in X-04.

Two rules in `rules.md` interact badly given how skills are authored:

- **ER-1** — "The routing plan names every approval gate the task will hit
  *before* work starts."
- **CS-1** — "Route on Tier-0 only… **never load a skill body** to decide."

27 of 86 skills carry substantive escalation gates **only in the
`## Escalation` body section**, with an empty `escalation` field in
`skill.yaml`. A gate the router can only see after loading the body cannot
be surfaced before work starts. Zero skills have the inverse problem, so
this is one convention drift, not 27 oversights.

The sharpest instance: `deployment-release`. The escalation matrix names it
`↑ human (confirm)` for production deploys; its body says "Any
production-affecting deployment action is guarded behind explicit
confirmation — this is not optional"; its `escalation` field is empty.
Also in the 27: `database-operations` (production isolation-level and
pool-resize changes), `ci-cd-pipeline` (pipeline changes affecting
production deploys), `containerization` (rootless-mode change on a
production image).

### Escalation-matrix rows with no skill counterpart

Auditing `matrices.md#escalation-matrix` row by row against the authored
skills:

| Matrix row | Status |
|---|---|
| data-migration → destructive migration ↑ human | ✅ declared in `escalation` |
| git-workflow → force-push/history rewrite ↑ human | ✅ declared |
| **deployment-release → production deploy ↑ human** | ❌ **body only** |
| project-management, code-review → outward-facing post ↑ human | ✅ both declared |
| solution-architecture → requirement gap ↑ requirements-engineering | ✅ declared |
| **refactoring → latent bug ↑ code-review / bug-fixing** | ⚠️ target `bug-fixing` does not exist (R-02) |
| **debugging → root cause ↑ bug-fixing** | ⚠️ **neither skill exists** (R-02) |
| code-review → security finding ↑ security-engineering | ✅ declared |
| code-review → performance finding ↑ performance-engineering | ✅ declared |
| any technology skill → engine-agnostic problem ↑ its parent | ✅ pervasive in non-activation |
| any Tier B/C → capability absent ↑ capability-adapter | ✅ pervasive in `failure_handling` |
| security-engineering → secrets exposed ↑ human | ✅ declared |
| llm-application-engineering → live LLM call with cost/data implications ↑ human | ✅ declared |

11 of 13 rows are well-implemented. The two that are not are the two
findings already raised (X-04, X-01) arriving from a third direction.

**No skill was found whose scope implies risk and which has no escalation
route at all** — every one of the 86 has a `## Escalation` section with
real content. The defect is purely that a third of them are invisible to
the layer that needs to read them.

---

## R-06 · Missing review loops (check 16)

### The review loop has no Tier-0 representation

57 of 61 edit-producing skills never reference `code-review` (SK-CONV-007)
anywhere. **This is correct by design and I am not flagging it** — QR-2
would be violated if 61 skills each restated the review loop, and the
architecture deliberately locates review in the composition layer
(ER-6, and `code-review ⤾` in every one of the 10 workflow patterns).

The finding is narrower and sharper. `code-review`'s own activation
conditions are:

```
+ A change is up for review
+ The user asks for a code review
+ A pre-merge gate is in play
```

None of these fires on *"a build skill in this run just produced an
edit."* ER-6 says review facets "follow the selected set" — but ER-6 is a
rule in a routing document, and CS-1 requires the router to decide using
Tier-0 metadata only. So the automatic post-build review exists in the
prose layer and has no counterpart in the layer that actually drives
selection.

This is amplified by **SR-7** (orchestration minimalism): the router
self-suppresses `workflow-composer` on single-skill tasks. The single-skill
path is precisely where no composer inserts a review stage, no build skill
names one, and `code-review`'s own triggers do not fire.

**Worked case — "Add a Dockerfile for this service."** SR-3 detects no
technology conflict; `containerization` owns it unambiguously; SR-7
suppresses the composer (one stage) and the router (single owner).
`containerization` produces `edit: image-guidance` + `edit:
compose-config`, references `SK-QA-002` in its body but not
`SK-CONV-007`. Nothing in Tier-0 causes a review. A Dockerfile is a
security-relevant artifact (base image, root user, secret handling) and
`SK-QA-002` is exactly the facet ER-6 would demand — via a rule with no
trigger.

**Recommendation (structural, human decision):** the cleanest fix is to
give `code-review` a Tier-0 signal for the run-internal case — an
activation condition equivalent to *"a skill in the current run has
produced an edit that has not yet been reviewed."* That is a
run-state-dependent trigger, which is a new *kind* of activation signal
for this library (all 86 skills currently trigger on task text or repo
signals), so it is a design decision rather than a field edit. The
alternative — accepting that review is composer-only and tightening SR-7
so the composer is never suppressed when the selected set produces edits —
is simpler but makes every one-line change pay orchestration overhead,
which R-6 of the orchestrator self-review already worries about.

---

## Summary

| ID | Finding | Severity | Kind |
|---|---|---|---|
| R-01 | Routing examples select and exclude 6 non-existent skills; both mandated examples affected | **High** | inherited gap, new consequence |
| R-02 | `debug` intent and workflows #3/#4 have no skill; SR-10 inert; ER-5 dangling ×2 | **High** | missing capability |
| R-03a | `code-quality` ⟷ `refactoring` unresolved; safety-net obligation can be silently dropped | Medium | activation overlap |
| R-03b | `observability` ⟷ `performance-engineering` unresolved on production diagnosis | Medium | activation overlap |
| R-03c | `web-accessibility` missing from ER-6's review facets; won't fire on "review this UI" | Medium | under-activation |
| R-03d | `legacy-modernization` → `data-migration` guard is one-directional | Low | activation overlap |
| R-04 | `go`/`nodejs` runtime guards exclude themselves on polyglot repos under SR-2 | Medium | over-broad guard |
| R-05 | ER-1 unimplementable for 27 skills incl. `deployment-release` | **High** (=X-04) | metadata/body desync |
| R-06 | Review loop has no Tier-0 trigger; SR-7 suppression leaves single-skill edits unreviewed | Medium | structural |

**Overall:** the default-deny model is sound and the cross-routing
discipline behind it is genuinely good — six of the nine findings are
*missing* guards on specific pairs rather than a flaw in the mechanism.
The two High findings that are not inherited from Step 28 (R-02, R-05)
both share a shape worth naming: **a rule was written in the routing
architecture and never given a counterpart in the skill metadata the rule
must read.** That is the pattern to watch for when the orchestrator layer
and the skill corpus are authored in separate steps.
