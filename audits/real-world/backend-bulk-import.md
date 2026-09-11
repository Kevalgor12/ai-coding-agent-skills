# Real-World Evaluation — Backend: bulk CSV import endpoint

Step 32 of the master build plan. Adversarial pattern: **failed dependency**.
Date: 2026-09-11. Method per the step brief: trace the run as the orchestrator
in [`core/orchestrator/`](../../core/orchestrator/) specifies, from the actual
`skill.yaml` fields, then simulate the failure of the verification step and
check whether any skill in the chain has `failure_handling` content that
handles it.

**Standing caveat:** nothing here is enforced by a runtime (`self-review.md`
R-1). These are findings about written rules and written metadata.

> **Scenario-ID note.** The `S17`+ identifiers proposed below are allocated
> within this file's scope only. Sibling Step 32 real-world audits were written
> in parallel and independently propose `S17`/`S18`/`S19`, so **every new
> scenario ID across `audits/real-world/` needs one reconciliation pass before
> any scenario file is created.** Treat the IDs here as placeholders; the
> findings and assertions they carry are what matter.

## Task and repository signals

> Add a bulk CSV import endpoint for restaurant menu items, including
> validation and duplicate detection.

| Signal | Bearing |
|---|---|
| `express` in `package.json` | `SK-TECH-express` detection-gated hit |
| `pg` driver / `postgres://` connection string | `SK-TECH-postgresql` detection-gated hit |
| no ORM in the manifest | `orm-integration` excluded by its own non-activation |
| no existing bulk-import code | greenfield *within* an existing service |
| populated `menu_items` table | a uniqueness constraint is a migration, not a create |

Classification: intent `build`; task type **feature development**
(`workflows.md` #2); complexity `multi-step`; risk `reversible-write`, rising
to `destructive` if duplicate detection is implemented by adding a UNIQUE
constraint to a populated table (constraint creation can fail, and de-duping
existing rows to satisfy it is data loss). S-Gate 1
(`security-and-validation.md`:64): an uploaded file is untrusted input crossing
a trust boundary — a clear hit.

---

## Routing trace

### Included

| Skill | Matching condition | Cite |
|---|---|---|
| `requirements-engineering` SK-DISC-001 | "The request is under-specified, ambiguous, or open to more than one reasonable interpretation" + "The request implies but doesn't state a constraint (scale, compliance, audience, environment)" | `skills/requirements-engineering/skill.yaml:28,30` |
| `technical-planning` SK-DISC-003 | "The agreed approach requires multiple ordered steps to implement" | `skills/technical-planning/skill.yaml:29` |
| `api-design` SK-BE-002 | "Designing or extending an HTTP/REST API" | `skills/api-design/skill.yaml:29` |
| `data-modeling` SK-DATA-001 | "An existing schema needs a structural change (new entity, changed relationship)" | `skills/data-modeling/skill.yaml:31` |
| `express` SK-TECH-express | "package.json/lockfile lists express as a dependency" | `skills/express/skill.yaml:33` |
| `postgresql` SK-TECH-postgresql | "A postgres:// … connection string or a PG driver (pg, psycopg, pgx, libpq) is present" | `skills/postgresql/skill.yaml:30` |
| `security-engineering` SK-QA-002 | "Writing or reviewing security-sensitive code (handling untrusted input…)" | `skills/security-engineering/skill.yaml:33` |
| `data-migration` SK-DATA-006 *(conditional)* | "A schema change is needed on a database that already has data" | `skills/data-migration/skill.yaml:28` |
| `testing-strategy` SK-QA-001 | SR-5 — runnable code is produced | `rules.md:25` |
| conventions + orchestration | SR-6, SR-7 | `rules.md:30,33` |

`requirements-engineering` firing is the single best routing outcome on this
task. The request hides at least five undecided constraints — what "duplicate"
means (name-per-restaurant? external SKU?), whether import is synchronous or a
job, all-or-nothing vs. partial success, maximum file size, and who may import
for which restaurant. ER-4 (`rules.md:110`) and its own activation conditions
both catch this before any build skill commits to an answer.

`api-design` is the second. Its engineering rules already carry two of this
task's real answers: *"use idempotency keys for non-idempotent operations that
might be retried"* (`skills/api-design/SKILL.md:87`, `:98`) and a consistent
error-response shape — which is what a partial-failure bulk import needs.

### Correctly excluded

- `orm-integration` — non_activation[0] "No ORM is in use and the work is raw
  SQL / a direct driver" (`skills/orm-integration/skill.yaml:33`) fires exactly
  as intended; `prisma`/`drizzle`/`typeorm`/`mongoose` fall out with it via SR-3.
- `graphql-api-design`, `realtime-communication`, all frontend skills, `mysql`,
  `mongodb` — no signal.
- `nodejs` — worth naming as a **positive**: its non_activation[1] is *"The
  question is Express- or Fastify-specific routing/middleware/plugin behavior
  with the runtime itself not in question (route to SK-TECH-express)"*
  (`skills/nodejs/skill.yaml:41`). That is a *task-shape* guard, not an
  absence-scoped one, so it can actually fire in a repository where Node is
  present. It is the exact wording pattern
  [`frontend-product-listing.md`](frontend-product-listing.md) F1-FE recommends
  for `threejs`/`socketio` — the fix already exists in this corpus.

### Ambiguous, and consequential

`backend-architecture` SK-BE-001 is a coin flip. Its non_activation[1] — "The
task is the HTTP/GraphQL contract itself with structure already settled (route
to api-design/graphql-api-design)" (`skills/backend-architecture/skill.yaml:33`)
— plausibly matches, and SR-2 makes a match decisive. But the task carries a
genuine *layering* question that `api-design` does not own: whether a 50k-row
CSV is parsed as a stream or buffered, and whether the import runs in-request or
as a background job. If `backend-architecture` is excluded, nobody owns it —
and the background-job half routes to async messaging, a tracked research gap
(`taxonomy-analysis.md#missing-capabilities`). Recorded rather than scored,
because either routing is defensible from the metadata as written.

---

## The adversarial case: the verification step fails

### First, a correction to the premise

The brief posits `testing-strategy` as "a hard dependency of some other skill in
this chain." **It is not, and cannot be.** Per
[`audits/cross-skill/dependency-audit.md`](../cross-skill/dependency-audit.md),
the library's complete `depends_on_skills` inventory is nine edges across five
skills; only `refactoring` and `legacy-modernization` depend on `SK-QA-001`, and
neither is in this chain. Stronger: **no skill in this chain references
`SK-QA-001` in any field.** Verified across all seven:

```
api-design            related_skills: [SK-BE-001, SK-BE-003, SK-TECH-openapi-swagger,
                                       SK-DATA-001, SK-CONV-006]        :60
data-modeling         related_skills: [SK-DISC-002, SK-DATA-002, SK-DATA-006]  :63
express               related_skills: [SK-TECH-nodejs]                  :66
postgresql            related_skills: [SK-TECH-drizzle, -prisma, -typeorm,
                                       SK-DATA-002, SK-DATA-006]        :80
security-engineering  related_skills: [SK-CONV-007, SK-BE-005, SK-QA-003, SK-AI-008] :58
backend-architecture  related_skills: [SK-DISC-002, SK-BE-002, SK-BE-003, SK-DATA-001] :59
code-review           depends_on_skills: [SK-QA-002, SK-QA-003, SK-CONV-002, SK-CONV-003] :51
```

`testing-strategy`'s presence in this run rests entirely on three
orchestrator-side prose rules — SR-5 (`rules.md:25`), SR-10 (`rules.md:42`) and
T-Gate 1 (`security-and-validation.md`:96) — with **zero** support in skill
metadata. That is the structural precondition for everything below.

### Branch (a) — `testing-strategy` never activates

SR-10's completeness backstop and T-Gate 1 are the only catches. If both are
missed, nothing else notices: no skill in the chain names `SK-QA-001`, and
`code-review` — the natural last line of defence — does not delegate a testing
facet. Its `depends_on_skills` is the four review facets `ER-6` enumerates
(`rules.md:118`: quality, comment, security, performance), and **testing is not
among them.** `code-review`'s body does defer correctly
(`skills/code-review/SKILL.md:146-150`), but that is Tier-1 content, invisible
to routing under CS-1. So "was this change tested?" is not a review facet in
this library.

### Branch (b) — it activates and returns `blocked` on missing input

F1 (input-deficient). D16's F1 row (`failure-recovery-and-escalation.md`:75)
says "R7 (ask) or R4 — **the skill's own `failure_handling` decides which**."
`testing-strategy`'s failure_handling[0] — *"If the risk profile of a change
isn't clear, ask what's actually at risk"* — supplies an R7. **This branch works
correctly.**

### Branch (c) — it activates but shell is unavailable

F2 (capability-deficient). D16 routes R3 → R4 → R7. R4 is "degrade to advisory,
mark it not-executed." The skill the agent is actually reading at that moment
says nothing about it: `testing-strategy` is `execution_tier: B` with
`required_capabilities: [file-read, file-write, shell]`, and its two
`failure_handling` rules cover risk-profile ambiguity and undocumented testing
methodologies — neither mentions shell, capability, or advisory degradation.

Mechanically: **51 skills declare Tier B/C with `shell`; 36 carry a
capability-degradation `failure_handling` rule; 15 do not** — and
`testing-strategy` is one of the 15, alongside `database-operations`,
`observability`, `orm-integration` and `performance-engineering`. The absent
rule matters most in exactly this skill, because T-Gate 1 and T-Gate 4 route to
it by name and the orchestrator's honest-limit rule
(`security-and-validation.md`:102-106) presumes it will say so.

### Branch (d) — it delivers, but degraded, and the next step consumes that

This is the branch the brief actually asks about, and **no skill in the library
handles it.** A full-corpus scan of all 86 `failure_handling` fields finds 13
skills with hand-off rules, and every one is *upstream input deficiency* — "if
**my** input is missing, hand off to X":

```
api-design    : "If the domain model isn't yet designed, request it or hand off to data-modeling…"
data-modeling : "If requirements are too thin to design against, request them or hand off…"
data-migration: "If the target schema isn't clear, request it or hand off to data-modeling…"
technical-planning: "If the approach being planned is itself unclear… hand off to solution-architecture"
```

**Zero** rules of the form "if the step I depend on returned `partial`/
`blocked`, do X." The orchestrator has the same hole: the invocation envelope's
`prior_outputs{}` is defined as "Declared handoff artifacts from prerequisite
steps only" (`state-and-contract.md`:154) with **no status annotation** — a
downstream skill cannot tell whether its input came from a `complete` step or a
`partial` one. And none of F1–F9 (`failure-recovery-and-escalation.md`:33-41)
names this class: F1 is "input absent" (here it is present, just degraded), F6
is "evidence invalidates the plan," F7 is a contract violation. CM-2
(`state-and-contract.md`:231) covers an *undeclared* artifact, not a *declared
but degraded* one.

**Verdict on vacuity:** the library's `failure_handling` is **not** vacuous —
X-21's finding holds, no rule anywhere is a bare "ask the user." But it is a
**monoculture**: one failure class (F1, input deficiency) is covered
consistently and well; a second (F2, capability) is covered by 36 of 51 skills
and missed by the most load-bearing one; a third (degraded upstream delivery) is
covered by none, in either the skills or the contract.

---

## Findings

### F1-BE · The verification step has no metadata anchor — **High**

**Finding.** `testing-strategy` is staffed on this task only by orchestrator
prose (SR-5, SR-10, T-Gate 1). No skill in the chain declares it as a
dependency or a related skill, and `code-review` does not delegate a testing
facet — `ER-6` (`rules.md:118`) enumerates four facets and testing is not one.
The run can therefore reach `complete` with no test staffing and no rule
violated at the metadata layer.

**Root cause.** The same shape `routing-audit.md` named in its summary: *"a rule
was written in the routing architecture and never given a counterpart in the
skill metadata the rule must read."* Here it is SR-5 and T-Gate 1.

**Recommended correction.** Extend ER-6 with a fifth facet — *"any change that
produces runnable code → testing facet"* — and add `SK-QA-001` to
`code-review`'s `depends_on_skills`. That edge is VR-4-clean only under
`dependency-audit.md`'s recommended **Option C** (the cross-cutting-QA
exception), since `code-review` is Layer 2 and `SK-QA-001` is Layer 3; it should
land in the same decision batch, not ahead of it.

**Regression test requirement.** Not covered. S13
(`endpoint-validation-verification-failure`) exercises a verification check that
*runs and fails*; S14 (`test-suite-shell-capability-loss`) exercises a
capability revoked mid-run. Neither covers a run in which the verification step
is **never staffed at all**. **New scenario required: `S20 — verification step
unstaffed`**, category 7 (Failure scenarios). Critical assertion: on a
feature-development run producing runnable code with no explicit test request,
`SK-QA-001` appears in `routing_record.selected[]` — or, if the backstop had to
add it, in `routing_record.backstop_additions[]` with the stage it staffed
(SR-10 / EH-5).

---

### F2-BE · `testing-strategy` declares shell and has no capability-degradation failure rule — **High**

**Finding.** `skills/testing-strategy/skill.yaml` is `execution_tier: B` (`:63`) with
`required_capabilities: [file-read, file-write, shell]` and two
`failure_handling` rules (`:83-84`), neither of which addresses shell being
unavailable. 36 of the 51 Tier-B/C-with-shell skills carry that rule; this is
one of the 15 that do not. D16's F1 row explicitly delegates the ask-vs-degrade
choice to "the skill's own `failure_handling`", and the orchestrator's
honest-limit rule presumes the skill will declare the limit.

Compounding it: all three of `testing-strategy`'s `verification` items are about
**test design** — layer selection matching actual risk, test isolation and
determinism, explicit fixture setup/teardown — and none of them is *"the suite
was executed and is green."* So IC-6's automatic `complete → partial` downgrade
(`state-and-contract.md`:207) and EH-2 (`observability-and-evaluation.md`:109)
cannot fire on the one fact that matters: T-Gate 4's "Red is `F3`, not done"
(`security-and-validation.md`:99) has no counterpart in the skill's own
verification list.

`testing-strategy` also has **no `escalation` field at all** — one of the 27
skills in `cross-skill-audit.md` X-04.

**Root cause.** The capability-degradation rule became a strong authoring
convention for *technology* skills (all four ORM skills, `express`, `nodejs`,
`postgresql`, `socketio`, `jest-vitest`, `react`, `nextjs` all have it) and was
not applied to the Layer-3 QA skills, which are the ones the orchestrator's gate
points route to by name.

**Recommended correction.** Add to `testing-strategy`'s `failure_handling`:
*"If shell/test-runner execution is unavailable, author the tests and state
explicitly that the suite was not executed — never report an unrun suite as
passing."* Add a fourth `verification` item: *"If the suite was run, its result
is stated; if it was not run, that is stated as an unverified claim rather than
omitted."* Sweep the other 14 skills in the same pass. This should be paired
with a new mechanical rule rather than left to authoring discipline — see below.

**Regression test requirement.** The *behavior* is already covered by S14, whose
critical assertions 6 and 7 test exactly the "don't report unrun as run" case.
What S14 does not test is whether `SK-QA-001` supplies the rule D16 delegates to
it — and a behavioral scenario is the wrong instrument for a metadata gap.
**Recommend a new `[V]` validation rule instead of a scenario:** *"VR-9 — a
skill declaring `execution_tier: B|C` with a non-universal capability MUST carry
a `failure_handling` rule naming what happens when that capability is absent."*
15 current violations, mechanically checkable, no judgement call.

---

### F3-BE · No skill owns the cost shape of a bulk operation — **High** *(second instance of F3-FE)*

**Finding.** A bulk CSV import's central engineering decisions are all
cost-shaped and all made before code exists: batch size, transaction
granularity (one transaction for 50k rows vs. chunked), `COPY` vs. multi-row
`INSERT`, streaming vs. buffering the upload, and back-pressure. None is owned:

- `performance-engineering` is symptom-gated ("A performance problem or budget
  is in play", `skill.yaml:35`) and its workflow opens with *"Gather
  profiling/benchmark evidence for the actual symptom"* (`SKILL.md:157`) — there
  is no symptom and no code.
- `database-operations` is likewise evidence-gated: *"If no query plan or
  workload evidence is available, ask for it rather than guessing at the
  dominant cost"* (`skill.yaml:76`).
- A full-corpus grep for `CSV`, `bulk insert`, `COPY FROM`, `ON CONFLICT` and
  `upsert` returns **no hits in any skill's guidance** — only `mysql`'s storage-
  engine list mentions CSV, as an engine name.

`data-migration` is the one skill that gets close, with *"Large backfills must
be batched"* (`SKILL.md:44-49`) — but it activates on schema evolution, not on
an application-level bulk write path, so the batching discipline is one
non-activation clause away from not applying here.

**Root cause.** Identical to F3-FE: `SK-QA-003` is scoped purely as remediation
of a measured regression. Two independent tasks in this evaluation hit the same
wall, which is what elevates it from a per-task gap to a library-level one.

**Recommended correction.** As in F3-FE: add a design-time activation condition
and decision-framework branch to `SK-QA-003`, gated on a *stated* inherent cost
characteristic. Separately, consider whether `ON CONFLICT`/upsert belongs in
`postgresql`'s `owned_knowledge` — it is a PostgreSQL-specific mechanism for
exactly the "duplicate detection" this task names, and the skill does not have
it.

**Regression test requirement.** Covered by the proposed **S19 — design-time
performance with no measurement available**
([`frontend-product-listing.md`](frontend-product-listing.md) F3-FE). Recommend
S19 use *this* backend task as its second variant rather than creating a
separate scenario — one scenario, two repository setups, since the finding is
the same and duplicating it would inflate the suite without adding a dimension.

---

### F4-BE · Duplicate detection can become a destructive migration, and the risk class never re-evaluates — **Medium**

**Finding.** "Duplicate detection" has two implementations with very different
risk classes. As an application-level check before insert, it is
`reversible-write`. As a `UNIQUE` constraint on the populated `menu_items`
table, it requires de-duplicating existing rows first — data loss — which is
G-DESTRUCTIVE (`failure-recovery-and-escalation.md`:146) and `data-migration`'s
own escalation gate (`skills/data-migration/skill.yaml:85`).

The architecture handles this correctly *if* the branch is noticed: D13
(`lifecycle.md`:191) requires re-admission when "the plan's scope exceeds what
the request literally asked for," and ST-6/R5 require a replan when the risk
class changes. But nothing triggers the noticing. The risk class is fixed at P0
from the request text, which says only "duplicate detection"; `data-migration`'s
activation ("A schema change is needed on a database that already has data")
only fires *after* someone decides the schema is the implementation.

**Root cause.** Risk classification is a P0 judgement over request text, and
`lifecycle.md` D3 ("What is the highest-risk action this task implies?") has no
mechanism for a request whose risk class is determined by an implementation
choice made two stages later.

**Recommended correction.** This is the one place `requirements-engineering`
already almost closes the gap — its activation[2] is "The request implies but
doesn't state a constraint." Add to its `verification` list an item requiring
that *any ambiguity whose resolutions carry different risk classes is surfaced
as such*, so the P4 re-admission trigger has an input. Narrow, and it uses a
skill that already activates on this task.

**Regression test requirement.** Not covered — S16
(`prisma-repo-drizzle-request`) is the nearest, but it is a
conflicting-requirement scenario, not a risk-class-escalation one. **New
scenario recommended: `S21 — implementation choice raises the risk class`**,
category 8 (Conflicting-requirement scenarios) or 7. Critical assertion: the run
does not reach the constraint-adding implementation without a re-admission
(D13) or a G-DESTRUCTIVE gate request.

---

### F5-BE · Stale routing markers in two of this chain's Tier-0 fields — **Low** *(instance of X-02)*

`data-modeling`'s non_activation[0] routes to "database-operations, **not yet
authored**" (`skills/data-modeling/skill.yaml:34`) and `api-design`'s
non_activation[1] routes to "realtime-communication, **not yet authored**"
(`skills/api-design/skill.yaml:34`). Both skills exist. Both markers sit in
`non_activation_conditions` — the Tier-0 field CS-1 makes the router's only
input. Low here only because neither guard is load-bearing on *this* task.
Root cause, correction and instrument are X-02's, unchanged; see F4-FE for the
recommendation to make this a validator rule rather than a scenario.

---

## Scoring

| # | Dimension | Verdict | Note |
|---|---|---|---|
| 1 | Skill routing | **Pass** | Correct set; `orm-integration` and `nodejs` both excluded by well-written task-shape guards |
| 2 | Dependency activation | **Fail** | Zero metadata edges to `SK-QA-001` anywhere in the chain (F1-BE) |
| 3 | Context efficiency | **Pass** | ~7 bodies, stage-scoped per CS-2; no over-inclusion |
| 4 | Implementation quality | **Partial** | `api-design`'s idempotency-key rule is exactly right; nothing covers CSV parsing, batching, or upsert |
| 5 | Security | **Pass** | `security-engineering` activates on untrusted input; S-Gate 3 applies at the writing step |
| 6 | Testing | **Fail** | Staffed only by prose; the staffed skill cannot declare an unrun suite (F1-BE, F2-BE) |
| 7 | Maintainability | **Pass** | `requirements-engineering` firing first is the main guard against building the wrong import semantics |
| 8 | Error handling | **Fail** | Branch (d) — degraded upstream delivery — has no rule in any skill and no class in F1–F9 |
| 9 | Repo conventions | **Pass** | SR-6 conventions attach; `git-conventions` gated on an actual commit |
| 10 | Final outcome | **Partial** | A good API contract and a correctly-surfaced requirements gap; no verification anchor and no cost model |

**Summary:** the adversarial pattern exposes a sharper problem than the brief
anticipated. `testing-strategy` is not a failed *dependency* because it is not a
dependency at all — its place in this run is held entirely by orchestrator prose
with no metadata counterpart, it cannot declare when its own execution did not
happen, and neither the skills nor the invocation contract has any concept of a
prerequisite step that delivered something degraded.
