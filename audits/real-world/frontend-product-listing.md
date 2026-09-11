# Real-World Evaluation — Frontend: responsive product listing page

Step 32 of the master build plan. Adversarial pattern: **excessive context**.
Date: 2026-09-11. Method per the step brief: work the task as the orchestrator
specified in [`core/orchestrator/`](../../core/orchestrator/) would, deciding
activation from the *actual* `skill.yaml` Tier-0 fields rather than from skill
names, then evaluate what that trace produced.

**Standing caveat** (inherited from [`audits/cross-skill/routing-audit.md`](../cross-skill/routing-audit.md)
and `core/orchestrator/self-review.md` R-1): nothing here is enforced by a
runtime. Every claim below is a claim about what the written rules and the
written metadata *say*, not about observed misbehavior.

> **Scenario-ID note.** The `S17`+ identifiers proposed below are allocated
> within this file's scope only. Sibling Step 32 real-world audits were written
> in parallel and independently propose `S17`/`S18`/`S19`, so **every new
> scenario ID across `audits/real-world/` needs one reconciliation pass before
> any scenario file is created.** Treat the IDs here as placeholders; the
> findings and assertions they carry are what matter.

## Task and repository signals

> Build a responsive product listing page with category filters and infinite
> scroll, for our Next.js + React + Tailwind storefront.

Signals a bounded Phase-0 scan (`routing-algorithm.md` §Phase 0) would return:

| Signal | Source | Bearing on this task |
|---|---|---|
| `next`, `next.config.*`, `app/` | manifest + config | in scope |
| `react`, `react-dom`, `.tsx` files | manifest + file types | in scope |
| `tailwindcss` / `@import "tailwindcss"` | manifest + CSS entry | in scope |
| **`three`** (3D product viewer elsewhere) | manifest + imports | **unrelated baggage** |
| **`graphql` client layer** | manifest | **data source, not a design target** |
| **`socket.io-client`** (live inventory count) | manifest + imports | **unrelated baggage** |

Classification: intent `build`; task type **feature development**
(`workflows.md` #2); complexity `multi-step`; risk `reversible-write`.
S-Gate 1 (`security-and-validation.md`:64): filter parameters are
user-controlled input reaching a data query — a weak but real trust-boundary
signal.

---

## Routing trace

### Correctly included

| Skill | Matching condition (verbatim) | Cite |
|---|---|---|
| `frontend-architecture` SK-FE-001 | "Building or structuring a new frontend application or non-trivial feature" | `skills/frontend-architecture/skill.yaml:29` |
| `react` SK-TECH-react | "react and/or react-dom are dependencies in package.json, or JSX/TSX files are present" | `skills/react/skill.yaml:33` |
| `nextjs` SK-TECH-nextjs | "A next.config.js/.mjs/.ts file, or \"next\" in package.json/lockfile, is present" | `skills/nextjs/skill.yaml:33` |
| `tailwindcss` SK-TECH-tailwindcss | "A tailwind.config.js/…, an \"@import \"tailwindcss\";\" CSS entry… is present" | `skills/tailwindcss/skill.yaml:35` |
| `ui-ux-design` SK-FE-002 | "Designing or improving a user-facing interface" | `skills/ui-ux-design/skill.yaml:35` |
| `web-accessibility` SK-FE-004 | "Building user-facing UI markup or components" | `skills/web-accessibility/skill.yaml:30` |
| `seo-optimization` SK-GROW-001 | "Search visibility matters for the work (a public-facing page or site)" | `skills/seo-optimization/skill.yaml:35` |
| `testing-strategy` SK-QA-001 | SR-5 — runnable code is produced | `rules.md:25` |
| `code-commenting`, `code-quality` | SR-6 — code is written | `rules.md:30` |
| `capability-adapter`, `workflow-composer` | Tier-B skills present; multi-stage | SR-7, `rules.md:33` |

Two of these are worth calling out as the library working *well*, because both
catch a real risk a naive implementation would miss:

- **`web-accessibility` does fire here.** Its activation[0] is a build trigger,
  not an audit-request trigger, so the R-03c under-activation finding
  (`routing-audit.md`:176) — which bites on *"review this UI"* — does **not**
  bite on *"build this UI"*. Its verification list
  (`skills/web-accessibility/skill.yaml:91-93`) is directly on point for a
  filter-plus-infinite-scroll page.
- **`seo-optimization` fires on the storefront signal alone**, and its owned
  content on JS-rendered crawlability (`skills/seo-optimization/SKILL.md:42-52`,
  `176`) is exactly the trap in an infinite-scroll product listing — a
  scroll-only list with no crawlable paginated URLs. The task text never
  mentioned SEO; the library found it anyway. This is the completeness backstop
  (SR-10) working in the direction it is supposed to.

### Correctly excluded

- `graphql-api-design` SK-BE-003 — activation is "Building or **extending** a
  GraphQL API" (`skills/graphql-api-design/skill.yaml:28`). The task *consumes*
  the GraphQL layer; it does not build one. Task-gated activation excludes it
  cleanly, with no reliance on a non-activation clause. This is the shape the
  other two baggage technologies do not have.
- `realtime-communication` SK-BE-004 — activation is need-gated ("A feature
  needs bidirectional, streaming, or server-push communication",
  `skills/realtime-communication/skill.yaml:31`). Infinite scroll is
  client-pull pagination, not server push. Excluded.
- `vue`, `angular`, `nuxt` — SR-4 conflict-cluster resolution plus explicit
  non-activation (`skills/react/skill.yaml:38`, `skills/nextjs/skill.yaml:38`).
- `styling-systems` SK-FE-003 — none of its three activation conditions match
  (`skills/styling-systems/skill.yaml:29-31`: setting up/restructuring styling,
  designing a token architecture, or an open tool choice). The Tailwind system
  is established. Excluded by SR-1 default-deny, correctly.
- All backend/data/infra skills — no signal.

### Not excluded, and that is the finding

**`threejs` and `socketio` survive the entire Tier-0 filter.** Both match
activation on a bare repository-presence signal, and neither has a
non-activation clause that can fire when the technology *is* present:

```
threejs  activation[0]      : "A `three` npm dependency, or an import from
                              'three'/'three/webgpu'/'three/addons', is present"   :35
         non_activation[0]  : "**No Three.js dependency/import**, and the task is
                              generic frontend component/state structure…"          :40
         non_activation[1]  : "2D-only visualization using Canvas 2D, SVG…"         :41
         non_activation[2]  : "A different WebGL/3D library…"                       :42
         non_activation[3]  : "Backend-only or non-browser rendering work"          :43
```

```
socketio activation[0]      : "A socket.io / socket.io-client dependency, import,
                              or require is present in the stack"                   :35
         non_activation[0]  : "The stack uses only the raw WebSocket API **with no
                              Socket.IO dependency**…"                              :39
         non_activation[1]  : "The realtime transport choice itself is still open"  :40
         non_activation[2]  : "…WebRTC peer-to-peer… with no Socket.IO involvement" :41
```

Clause [0] in each is a *conjunction whose first conjunct is the absence of the
very signal that fired activation*. It is unsatisfiable in a repository that
contains the technology. The remaining clauses each name a *different*
technology or rendering mode, none of which describes "build a product listing
page." So under SR-2 ("Non-activation is decisive", `rules.md:13`) neither skill
is excluded, and the only remaining barrier is the third conjunct of the
selection predicate:

```
include(s) :=  matches(activation) AND NOT matches(non_activation)
               AND needed_for(task_type, s)        # routing-algorithm.md:57
```

`needed_for` is the one term in that predicate with **no rule ID, no
definition, and no metadata source anywhere in `core/`.** It is where all the
work of this task's adversarial pattern lands.

---

## Findings

### F1-FE · Absence-scoped non-activation guards cannot exclude an irrelevant technology that is present in the repo — **High**

**Finding.** `threejs` and `socketio` both pass activation and both fail to
match any non-activation clause for this task. Every one of their
non-activation clauses is either conditioned on the absence of their own
detection signal (`threejs`:40, `socketio`:39) or names a competing technology
(`threejs`:42, `socketio`:41-42). In a repository that contains the dependency
— which is the only repository in which their activation fires at all — their
non-activation set is dead metadata. The same shape is present in 10 of the 40
technology skills; `tailwindcss`:40 has it too (harmless here only because
Tailwind happens to be relevant).

**Root cause.** Two-part. (a) Layer-4 activation condition #1 is, by
convention, a bare detection signal with no task-relevance qualifier — which is
correct per SR-3, since SR-3 makes detection *necessary*, not sufficient. (b)
The sufficiency half is delegated to `needed_for(task_type, s)`
(`routing-algorithm.md:57`), which is never defined, carries no rule ID, and
reads no field. So the architecture's defence against over-activation on a
broad-footprint repo rests entirely on an undefined term, while SR-11
(`rules.md:45`) still demands the router *record a reason* for each exclusion —
a reason it has no rule to derive.

This is the exact inverse of `routing-audit.md` **R-04**, which found `go`'s and
`nodejs`' runtime guards *over*-broad (they exclude themselves on a polyglot
repo). Same root cause — non-activation clauses written as if a repository
contains exactly one relevant technology — producing opposite failures. R-04's
recommendation (re-scope to `python`'s component-based phrasing) does not fix
this direction and should not be applied without also fixing it.

**Recommended correction.** Two changes, both narrow:

1. Add a **task-shape** non-activation clause to every technology skill whose
   guards are currently absence-scoped, of the form:
   *"The technology is present in the repository but the task under change does
   not touch it (route on the artifact under change, not the manifest)."*
   For `threejs` that reads: "A Three.js scene exists elsewhere in the
   repository but the artifact under change contains no 3D rendering."
2. Promote `needed_for` from an undefined predicate term to a stated rule in
   `rules.md`, e.g. **SR-12 · Detection is necessary, not sufficient.** A
   technology skill is included only when the *artifact under change* uses it —
   manifest presence alone never includes a technology skill, and the recorded
   exclusion reason for a detected-but-unused technology is "present in repo,
   absent from the artifact under change."

Both are decisions, not typo fixes: (1) edits routing behavior across ~10
skills, and (2) adds a normative rule. Neither was applied here.

**Regression test requirement.** Not covered by any existing scenario.
`evaluations/scenarios/` S01–S16 contains no case where an irrelevant
technology is *present in the repository*; S01's exclusion table
(`expected-behaviors/S01-…`) excludes technologies that are simply absent, which
is the easy case SR-3 already handles. **New scenario required: `S17 —
broad-footprint repo, narrow task`** (category 1, Simple tasks — the category
whose stated failure mode is "false-positive activation"). Its critical
assertion: *`SK-TECH-threejs` and `SK-TECH-socketio` appear in
`routing_record.excluded[]` with a stated reason, and neither appears in
`routing_record.selected[]` nor loads a body* — with the repo signals explicitly
stipulating both dependencies present.

---

### F2-FE · The rendering-mode decision this task turns on has no owner — **High** *(instance of an inherited finding)*

**Finding.** The first real engineering decision for a storefront product
listing page is the rendering mode: SSG/ISR for the first page (SEO, TTFB) with
client-side fetch for subsequent pages, versus streamed SSR, versus full CSR.
Every skill that could own it explicitly disclaims it:

- `frontend-architecture` description: *"Not for styling specifics,
  accessibility depth, **or the SSR/SSG rendering-mode decision**"*
  (`skills/frontend-architecture/skill.yaml:25-26`).
- `nextjs` scope: *"the rendering-mode decision method comes from SK-FE-005 (not
  yet authored)"* (`skills/nextjs/skill.yaml:17-19`).
- `react` scope: *"the broader SSR/SSG/CSR rendering-mode decision comes from
  SK-FE-005 … not yet authored"* (`skills/react/skill.yaml:19-21`).
- `SK-FE-005` is not in `skills/`.

`skill-router`'s own failure_handling has the right instinct — *"If a candidate
skill exists only as a taxonomy catalog entry and has not been authored, record
the gap and route to the nearest authored skill"*
(`skills/skill-router/skill.yaml:102`) — but on this task the instruction
dead-ends: the two nearest authored skills have both explicitly written the
decision out of their scope. D6 (`lifecycle.md:116`) then produces the honest
outcome "no skill covers this," for a decision that is not optional.

This is `routing-audit.md` **R-01** / Step 28's `SK-FE-005` gap. The step brief
asked whether *this* task actually triggers it: **it does, and at the first
decision, not at the margin.** R-01 showed the gap breaks the routing docs'
worked examples; this shows it breaks a routine e-commerce page.

**Root cause.** An approved catalog entry was never authored, and the skills
that would otherwise have absorbed its content deliberately carved it out in
deference to it — so the gap is *wider* than the unauthored skill, because two
authored skills narrowed themselves around an absence.

**Recommended correction.** Unchanged from Step 28 Option A: author `SK-FE-005`.
This task is additional evidence for prioritising it over `SK-GROW-002` /
`SK-TECH-graphql` / `SK-TECH-vite`. If Option B (drop the references) is chosen
instead, `frontend-architecture:25-26` and `nextjs:19-20` must be *widened* in
the same pass, not merely de-referenced — otherwise the decision stays orphaned.

**Regression test requirement.** Partially covered: S05
(realtime-multiplayer-browser-game) exercises `rendering-strategy` in its
activation set, so the gap is already visible to the suite. But S05 tolerates it
as one skill among ~15. **New scenario recommended: `S18 — rendering-mode
decision with no owner`**, category 2 (Ambiguous tasks), whose critical
assertion is that the run *surfaces the unowned decision as an
`open_questions[]` entry* rather than silently defaulting to a rendering mode —
which is the actually-dangerous behavior, since defaulting to CSR on a
storefront is an SEO regression the user never asked for.

---

### F3-FE · `performance-engineering` has no design-time branch, so infinite-scroll cost is either unowned or misrouted — **High**

**Finding.** Infinite scroll is a performance-shaped design decision made
*before* any code exists: page size, cursor-vs-offset pagination, whether the
list needs windowing, and how many product images are in flight. The library's
performance owner cannot take it:

- Activation is symptom-gated: "A performance problem or budget is in play" /
  "A diagnostic … is needed before optimizing"
  (`skills/performance-engineering/skill.yaml:35-36`).
- Non-activation names "Premature optimization the user didn't ask for" (`:40`).
- If it *is* activated anyway, its decision framework opens with *"Is there
  actual profiling/benchmark evidence, or is this a guess? **Measure before
  proposing a change**"* (`skills/performance-engineering/SKILL.md:134-136`) and
  its workflow step 1 is *"Gather profiling/benchmark evidence for the actual
  symptom"* (`:157`). Its failure_handling repeats it: *"If no
  profiling/benchmark evidence is available, gather it before proposing a
  change"* (`skill.yaml:77`).

There is nothing to profile. The code does not exist. Both branches are wrong:
exclude it and nobody owns the cost model; include it and the skill's own
first instruction is unsatisfiable, which under IC-6 (`state-and-contract.md`
:207) should return `blocked`, not `complete`.

Compounding it: **no skill in the library mentions "infinite scroll,"
"virtualization," or "windowing"** — a full-corpus grep returns one hit, in
`skills/vue/SKILL.md:302`, about Vue's lack of first-party list
virtualization. The Next.js/React path has none.

**Root cause.** `SK-QA-003` was scoped entirely as *remediation of a measured
regression*. The library has no home for *design-time* performance — choosing
the cheaper shape before writing the code — and the measure-first discipline
(genuinely correct for remediation) is stated in an unqualified form that
forecloses it. The same gap will recur on any greenfield feature with inherent
cost characteristics; see F3-BE in
[`backend-bulk-import.md`](backend-bulk-import.md) for the second instance.

**Recommended correction.** Add a fourth activation condition and a matching
decision-framework branch to `SK-QA-003`:
*"A feature being designed has an inherent cost characteristic (unbounded list,
bulk operation, large payload) and the cheaper shape must be chosen before
implementation."* The branch must state explicitly that design-time selection of
a cheaper shape is **not** the micro-optimization its anti-patterns prohibit —
otherwise the new condition contradicts `SKILL.md:195-197`. Scope creep risk is
real and should be bounded by requiring a *stated* cost characteristic, not an
imagined one.

**Regression test requirement.** Not covered. S03 (app-feels-slow) and S09
(dashboard-n-plus-one) are both remediation-shaped, which is precisely the half
that works. **New scenario required: `S19 — design-time performance with no
measurement available`**, category 5 (Performance-sensitive tasks). Critical
assertion: the run neither (a) silently omits a pagination/payload decision nor
(b) returns `blocked` on the absence of profiling evidence for code that does
not yet exist.

---

### F4-FE · Stale "not yet authored" markers in this task's Tier-0 fields — **Medium** *(instance of X-02)*

**Finding.** `frontend-architecture`'s non_activation[0] reads *"Pure styling
work with structure already settled (route to styling-systems, **not yet
authored**)"* (`skills/frontend-architecture/skill.yaml:33`). `styling-systems`
is authored (`skills/styling-systems/`). This is one of the 16 stale markers
`cross-skill-audit.md` X-02 found sitting in `non_activation_conditions` — the
one Tier-0 field CS-1 makes the router's only input. On this task the router
reads a routing target and is told, in the same sentence, that it does not
exist.

**Root cause.** X-02's root cause, unchanged: nothing re-checks forward
references when a referenced skill lands.

**Recommended correction.** The single mechanical sweep X-02 already
recommended, plus the repo-level guard it asked for. No new decision needed.

**Regression test requirement.** No new scenario. This is a metadata-hygiene
defect, not a behavioral one; a mechanical validator check ("no Tier-0 field
names a skill ID that resolves, with a 'not yet authored' qualifier") is the
right instrument, not a behavioral scenario. Recommend it be added to the
`[V]` rule set rather than to `evaluations/scenarios/`.

---

### F5-FE · API *consumption* has no owner, so the pagination contract is negotiated by nobody — **Medium**

**Finding.** Infinite scroll requires a cursor-based pagination contract from
the GraphQL layer. `api-design` owns "pagination for any unbounded list"
(`skills/api-design/SKILL.md:87`) and `graphql-api-design` owns cursor
pagination (`skills/graphql-api-design/skill.yaml:82`) — but both activate only
on *designing or extending* the API, and this task is on the consuming side.
`taxonomy-analysis.md#missing-capabilities` tracks this honestly ("API
consumption/client-side integration … Fold into `api-design`/tech skills for
now"), but the fold-in never happened: `api-design`'s activation conditions
contain no consumer-side trigger.

The practical consequence is specific: if the existing GraphQL list field is
offset-paginated, an infinite-scroll client built on it will duplicate and skip
rows under concurrent writes, and no activated skill is scoped to notice.

**Root cause.** A tracked research gap whose stated interim mitigation ("fold
into `api-design`") was recorded in the taxonomy analysis and never reflected in
`api-design`'s metadata.

**Recommended correction.** Either add a consumer-side activation condition to
`api-design` ("An existing API's pagination/versioning/error contract is being
consumed and its shape constrains the client") or upgrade the gap from "fold in"
to a tracked unstaffed capability. Do not leave the taxonomy claiming a fold-in
that does not exist in metadata.

**Regression test requirement.** Fold into **S17** as a `major` assertion rather
than a new scenario — the same broad-footprint repo naturally carries it.

---

## Scoring

| # | Dimension | Verdict | Note |
|---|---|---|---|
| 1 | Skill routing | **Partial** | Right skills included; 2 of 3 baggage technologies not excluded by metadata (F1-FE) |
| 2 | Dependency activation | **Pass** | No hard dependencies in this chain; `parents` edges resolve except `SK-FE-005` (F2-FE) |
| 3 | Context efficiency | **Fail** | `threejs` (≈24KB) + `socketio` bodies are loadable on a task that touches neither |
| 4 | Implementation quality | **Partial** | Strong on a11y/SEO/interaction states; silent on rendering mode, pagination shape, virtualization |
| 5 | Security | **Pass** | Weak trust boundary correctly handled; `react`'s RSC CVE verification (`skill.yaml:232`) is a real catch on a Next.js repo |
| 6 | Testing | **Pass** | SR-5 staffs `testing-strategy`; T-Gate 1/4 apply |
| 7 | Maintainability | **Pass** | No over-engineering pressure; `styling-systems` correctly not pulled in |
| 8 | Error handling | **Partial** | `skill-router:102` handles the unauthored skill honestly but its "nearest authored skill" fallback dead-ends (F2-FE) |
| 9 | Repo conventions | **Pass** | SR-6 attaches `code-commenting`/`code-quality`; `git-conventions` gated on an actual commit |
| 10 | Final outcome | **Partial** | An engineer gets good accessibility, SEO and interaction-state guidance, and no answer at all on the two decisions that determine whether the page is fast or crawlable |

**Summary:** the adversarial pattern lands. The library's *positive* routing is
good — it found SEO and accessibility concerns the user never mentioned — but
its *negative* routing depends on an undefined predicate term, and the two
highest-value decisions on this specific task (rendering mode, pagination/list
cost) are both unowned.
