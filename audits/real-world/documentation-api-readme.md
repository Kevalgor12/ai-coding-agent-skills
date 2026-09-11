# Real-World Evaluation — Documentation: API reference + stale README

Date: 2026-09-11. Step 32 of the project's master build plan. Domain: **Documentation**.
Adversarial pattern: **none** — this is the clean-baseline task, chosen so that a
defect found here is a defect in the library's ordinary path, not an artifact of
a hostile setup.

**Method.** I worked this task as the orchestrator described in
[`core/orchestrator/`](../../core/orchestrator/), routing against the real
`skill.yaml` Tier-0 metadata per `CS-1`, then loaded the bodies of the skills a
compliant run would actually activate. Every claim below cites a real file and
line. Per `core/orchestrator/self-review.md` R-1 and the standing caveat in
[`audits/cross-skill/routing-audit.md`](../cross-skill/routing-audit.md), nothing
here is observed runtime behaviour — these are findings about a specification's
behaviour when traced against its own rules.

**Not re-derived.** Findings established by Step 28
([`audits/2026-09-10-individual-skill-review.md`](../2026-09-10-individual-skill-review.md))
and Step 29 ([`audits/cross-skill/`](../cross-skill/)) are treated as settled.
Where this trace adds a new *consequence* to one of them, it says so.

---

## The task

> Write API documentation for our newly-built REST endpoints, and update the
> README with setup instructions for new engineers.

**Repository context.** A backend with 12 REST endpoints. No existing API docs.
A README two years stale, describing an old setup process.

---

## Trace

### P0 — Intake

| Determination | Value | Basis |
|---|---|---|
| `task_statement` | verbatim as above (ST-1) | — |
| `user_constraints[]` | none stated | — |
| Intent | `document` | routing-algorithm.md:22-23 |
| Task type | **no workflow pattern exists** → collapses to `simple` | see **D-05** |
| Complexity | multi-step (12 endpoints + a full README rewrite) | — |
| Risk | reversible-write | no destructive/outward/production action |
| S-Gate 1 | one hit: a README setup section routinely carries env vars and example connection strings → secret-in-file risk | security-and-validation.md:66 |

Bounded signal scan (routing Phase 0): backend manifest present; route/handler
files present; no `openapi.yaml`/`swagger.json`; no `docs/`; a stale `README.md`.

Neither early exit applies: this is not a `question`, and it is not a trivial
single-owner change (two distinct artifact classes, twelve endpoints).

### P1/P2 — Discovery and routing

**Selected.**

| Skill | Why it earns inclusion |
|---|---|
| `technical-documentation` (SK-CONV-006) | `activation_conditions[0]` "The user asks for documentation" matches verbatim; none of its three non-activation conditions matches (skill.yaml:29-36) |
| `git-conventions` (SK-CONV-001) | SR-6, **only if** a commit is actually made |

**Excluded, with reasons** (SR-11).

| Excluded | Reason |
|---|---|
| `code-commenting` (SK-CONV-002) | Its own scope routes prose docs out: "Prose documentation (READMEs, API docs, ADRs) belongs to…" (`code-commenting/SKILL.md:21`), and its decision framework says "(a README, API doc, ADR)? Route to technical-documentation instead" (`:87`). SR-2, cleanly. |
| `openapi-swagger` (SK-TECH-openapi-swagger) | SR-3. All four activation conditions presuppose an existing OpenAPI document or Swagger tooling (skill.yaml:29-33); neither is present nor named. Its non-activation explicitly returns READMEs/ADRs to `SK-CONV-006` (skill.yaml:37). See **D-06** for the tension this creates. |
| `testing-strategy` (SK-QA-001) | SR-5 — no runnable code is produced |
| `requirements-engineering`, `solution-architecture`, `technical-planning` | SR-8 — not a new system, not high-risk |
| `code-quality` (SK-CONV-003) | SR-6 — no code written or edited |
| `security-engineering` (SK-QA-002) | SR-5 — no trust-boundary change. The secret-in-README risk is handled at the orchestrator layer by S-Gate 3, not by activating the skill. Acceptable either way. |
| all 40 `SK-TECH-*` | SR-3 — none of the detected technologies is the subject of the task |
| `api-design` (SK-BE-002) | Borderline. Its condition "Reviewing an existing REST API's resource/versioning/pagination/error design" (skill.yaml:31) would fire if accuracy-checking surfaced inconsistent error shapes — but the intent is `document`, not `review`, so `needed_for(task_type)` is false. **Uncertain / acceptable either way**; see D-02, where its absence has a cost. |
| `workflow-composer`, `capability-adapter`, `skill-router` | SR-7 self-suppression: the final set is effectively one Tier-A skill |

**Net result: one skill, Tier A, no plan artifact, no gates, no review loop.**
That is the correct *shape* under SR-7 — and it is also the finding, because a
twelve-endpoint reference plus a two-year-stale README rewrite is not a
one-skill job. See D-05.

### P3–P7 — what a compliant run then does

`technical-documentation` loads (189 lines, Tier A, no Tier-2 references —
proportionate). Its decision framework runs:

1. *Generate from a source of truth?* → names OpenAPI as "the clearest instance"
   (SKILL.md:78-81). No spec exists → see D-06.
2. *Does it match current behavior?* → "Write what's actually true now" (:82-84).
3. *Already documented elsewhere?* → link, don't duplicate (:85-87).
4. *An architectural decision?* → ADR structure (:88-90).
5. *Code-only request?* → no.

Workflow (SKILL.md:96-104) then produces the docs. P6 runs the skill's own
`verification` list (skill.yaml:75-79). P7 reports.

---

## Findings

### D-01 · `technical-documentation` treats "documentation" as one undifferentiated deliverable — **Medium**

**Finding.** The task names two related-but-distinct artifacts: an endpoint-by-endpoint
API reference and a new-engineer onboarding README. The skill's own scope names
four artifact classes ("READMEs, API docs, ADRs, inline module docs",
skill.yaml:10-13) but models them as one output: a single `outputs` entry named
`documentation`, kind `edit`, description "Documentation files/sections (README,
API docs, ADRs, inline module docs)" (skill.yaml:46-49). Its decision framework
(SKILL.md:76-92) has five steps and **none of them asks which artifact class or
which reader** the work is for. The only artifact-specific content in the entire
skill is ADR structure (decision + rationale + alternatives) — one of four named
classes gets a structure; the other three get none.

Concretely absent: what an API reference entry must contain (method, path, path
and query parameters, request body shape, success status, error statuses and
shapes, auth requirement, an example), and what an onboarding README must contain
(prerequisites, install, configuration/env vars, run, test, common failure
modes). A full-text search across all 86 `SKILL.md` files for
`onboard|getting started|setup instruction|new engineer|quickstart` returns
**zero** substantive hits — no skill in the library owns onboarding documentation
as a content model.

**Root cause.** The skill was scoped by *medium* (human-readable prose, as
against `code-commenting`'s in-code prose) rather than by *artifact class ×
audience*, and the single `outputs` entry encodes that choice. The per-artifact
structure the library does possess lives in `openapi-swagger` — and SR-3 gates
that off whenever no OpenAPI artifact exists, which is exactly the greenfield
case this task presents.

**Recommended correction.** Add a decision-framework step 0 — "Which artifact,
and for which reader?" — and a Tier-2 `references/artifact-checklists.md` giving
a minimum-content checklist per class, at minimum API reference and
README/onboarding. Split `outputs` into `api-reference`, `readme`, `adr`,
`module-doc` so a return envelope can bind them separately (IC-4). Keep it Tier-2
so CE-4/CS-5 economy is preserved.

**Regression test.** **Yes — new scenario required.** `evaluations/scenarios/`
contains sixteen scenarios and **not one documentation scenario**, despite
"Documentation quality" being dimension 15 of `evaluation-spec.md`. Propose
`S17-api-docs-and-stale-readme`, category *Multi-skill tasks*. Assert the run
produces two separately-named artifacts, each satisfying its own content
checklist — not one undifferentiated `documentation` output.

---

### D-02 · No procedure for verifying documentation accuracy; the verification rules are assertions, not a method — **High**

**Finding.** The skill's central commitment is that docs match reality. It says so
four times: `verification[0]` "Produced docs match the actual current
interface/behavior, not a stale or aspirational description" (skill.yaml:76);
Knowledge "Documentation that drifts from the code it describes is worse than no
documentation" (SKILL.md:51-55); Workflow step 2 "checking against the code
itself, not assumptions" (SKILL.md:98-99); Anti-pattern 2 (SKILL.md:133-134).

**That is the entire method.** There is no procedure for establishing the
property — no instruction to derive the endpoint inventory from the route
definitions rather than from the existing docs, no per-endpoint reconciliation
step, no record of which claims were confirmed against a handler and which could
not be determined. And `depends_on_skills: []` (skill.yaml:51) means the skill
takes no hard dependency on anything that could produce that evidence.

The contrast with the rest of the library is stark, and it is what makes this a
defect rather than a stylistic gap. Every comparable "must match reality" claim
elsewhere carries an evidentiary procedure: `database-operations` DF#1 demands
`EXPLAIN`/`EXPLAIN ANALYZE` evidence before proposing an index; `performance-engineering`
demands a measured baseline before optimizing; `llm-evaluation` demands a named
grading method and a golden set; `refactoring` hard-depends on `SK-QA-001` for a
green baseline precisely because "behavior preserved" is otherwise unverifiable.
`technical-documentation` asserts the same class of property with none of that.

The consequence under the orchestrator contract is specific. IC-6 states that
`complete` "requires `verification` to have actually run and passed," and FV-5
requires "every mutating step has verification evidence." With no method, the
skill's verification collapses to self-assertion by the same actor that wrote the
prose — which is the precise failure mode IC-6 exists to prevent.

**Root cause.** The skill states the *property* documentation must have and never
states how to establish it. For most skills `verification` is a post-hoc check on
a separately-produced artifact; for a documentation skill the check and the work
are the same activity, so an unstated method degenerates into "I believe I was
careful."

**Recommended correction.** Add a Workflow step between current 1 and 2: enumerate
the source of truth explicitly (route table, handler signatures, type
definitions, schema) and produce a per-claim reconciliation record marking each
as `confirmed` / `corrected` / `not-determinable`. Add a matching `verification`
entry naming that record as the evidence. Add `SK-BE-002` to `related_skills` for
the endpoint-inventory step (it is already reciprocal — `api-design` lists
`SK-CONV-006`, skill.yaml:60).

**Regression test.** **Yes**, folded into `S17`. Assert the return envelope carries
a per-endpoint reconciliation, and that any claim that could not be checked lands
in `unverified_claims[]` rather than silently in the published doc.

---

### D-03 · The skill cannot verify executable setup instructions and does not declare the limit — **High**

**Finding.** `execution_tier: A`, `required_capabilities: [file-read, file-write]`
(skill.yaml:55-56). A README's setup section is a sequence of commands; the only
way to verify it is to run it, which requires `shell`. The skill's
`failure_handling` has exactly two rules (skill.yaml:72-74) — don't impose docs
on a code-only request, don't duplicate existing docs — and **neither concerns
capability**. Step 29's X-21 found "degrade to advisory and say so" present in 23
skills' `failure_handling`; `technical-documentation` is not among them, and it
is one of the few where the omission changes the output's truth value, because
its own Anti-pattern 2 is "Writing documentation that describes aspirational
behavior rather than what the code actually currently does." **An unexecuted
setup sequence is aspirational by construction.**

No other layer catches this:

- **T-Gate 1** (testability admission, P3) triggers "if the plan produces runnable
  code" (security-and-validation.md:96). A README is not runnable code, so the
  gate does not arm and the limit is never declared at P4.
- **`capability-adapter`** is inserted only before a Tier B/C step (PR-3). The
  skill is Tier A, so no barrier exists and no `execution_mode` is resolved.
- **IC-3** would require an `unverified_claims` entry *under advisory or fallback
  mode* — but the step is never classified as degraded, because nothing ever
  compared its capability needs against the host.

So the single most consequential claim in the deliverable — "these commands will
set the project up" — is produced, never executed, and reported without a caveat.

**Root cause.** The library's capability model is keyed to *producing runnable
code*. Setup documentation is the case where the artifact is not code but its
correctness is establishable only by execution, and no rule covers that shape.

**Recommended correction.** Add a `failure_handling` rule: "If shell access is
unavailable, setup and run instructions are produced as advisory and marked
explicitly as not-executed; never present an unexecuted setup sequence as
verified." Add the matching `verification` entry. Consider raising
`execution_tier` to `B` with `shell` declared optional, so the adapter barrier
engages and `execution_mode` is resolved honestly (this is the change that makes
IC-3 reachable). Separately, consider widening T-Gate 1's trigger from "produces
runnable code" to "produces an artifact whose correctness is only establishable
by execution."

**Regression test.** **Yes — new scenario.** Category *Failure scenarios*
(capability absent). The nearest existing scenario is `S14-test-suite-shell-capability-loss`,
which covers a *test suite* losing shell; the documentation case is not covered.
Propose `S18-readme-setup-unverifiable`. Assert the run's final report carries
"setup instructions authored, not executed" as a declared residual (FV-10), never
as a pass.

---

### D-04 · No escalation path for a doc/code contradiction, on the skill whose task is most likely to find one — **Medium**

**Finding.** `escalation: - None — this skill has no escalation path of its own
beyond the standard confirmation rules for any file the user hasn't explicitly
asked to be changed` (skill.yaml:80-81), repeated verbatim in the body
(SKILL.md:172-176).

The defining discovery of *this* task is a contradiction: a two-year-stale README
says the app is started one way and the code starts it another. The engineering
question that follows is not answered anywhere in the skill — **which one is
wrong?** Sometimes the doc drifted. Sometimes the *code* drifted: a documented
feature was removed by accident, a default was changed without intent, an
environment variable stopped being read. Silently rewriting the doc to match the
code erases the only surviving record that the behaviour was once different.

The library models this exact pattern everywhere else. `matrices.md`'s escalation
matrix has `refactoring` → discovers a latent bug → `↑ code-review / bug-fixing`,
annotated "don't silently fix"; `code-review` → security finding → `↑
security-engineering`. There is **no documentation analogue** in the matrix or in
the skill.

The gap compounds with D-02. `failure_handling[1]` reads "If existing docs
already cover the topic accurately, don't duplicate them — update in place
instead" (skill.yaml:74) — which *presupposes* an accuracy determination the
skill has no method to make (D-02) and provides no branch for the outcome
"they contradict."

**Root cause.** The skill models documentation as strictly downstream of code
(docs describe code, therefore a mismatch is by definition a doc bug). In a
greenfield repo that assumption is safe. In a two-year-stale one it is not, and
this task is the stale case.

**Recommended correction.** Replace the "None" escalation with: "A documented
behavior that contradicts the current code is surfaced as a finding — which is
correct? — rather than silently resolved in the code's favour." Add the
reciprocal `failure_handling` rule. Add the row to `matrices.md`'s escalation
matrix so ER-5 gains a documentation edge.

**Regression test.** **Yes**, folded into `S17`: seed one endpoint whose README
description contradicts its handler, and assert `findings[]` or `open_questions[]`
is non-empty — i.e. the run surfaced the contradiction rather than resolving it.

---

### D-05 · The intent `document` maps to no workflow pattern, so SR-10's backstop and the review loop are both inert — **Medium**

**Finding.** `core/routing-architecture/` classifies twelve intents (*fix, build,
debug, refactor, optimize, secure, migrate, modernize, document, review, explain,
plan* — routing-algorithm.md:22-23). `core/dependency-architecture/workflows.md`
defines ten canonical patterns. **The mapping is not total.** `document`,
`review`, and `plan` map to no pattern. Phase 1 states "Task type = the workflow
pattern that intent maps to, or `simple` (single-step) / `question` (no change)"
(routing-algorithm.md:24-25) — so a twelve-endpoint documentation job with a full
README rewrite is classified `simple`, which is false: its own complexity
determination is multi-step.

Three consequences chain from that single misclassification:

1. **SR-10 cannot fire.** Its instruction is "re-walk the chosen workflow's
   required stages; if a stage has no skill staffing it, add the missing
   essential skill" (routing-algorithm.md:78-80). With no workflow there are no
   stages, so the mechanism that exists specifically to catch under-activation —
   which the rules themselves call "a correctness bug [that] overrides economy"
   (SR-10) — has nothing to check against.
2. **SR-7 suppresses the composer**, so no staged plan inserts a verification or
   review stage.
3. **`code-review` does not fire.** Step 29's R-06 established that the review
   loop has no Tier-0 trigger for "a skill in this run just produced an edit";
   `code-review`'s three activation conditions all require the review to be
   externally occasioned. So D-02's missing verification is not backstopped by a
   review either.

Net: a compliant run authors twelve endpoint descriptions and a README, and
**nothing in the library checks any of it**.

This is the structural mirror of Step 29's R-02. R-02 found an intent (`debug`)
that has a workflow but no owning skill. This is an intent that has an owning
skill but no workflow. Same root shape — two lists authored in separate steps,
never reconciled — arriving from the opposite direction.

**Root cause.** Nothing asserts that the intent list and the workflow-pattern list
are in correspondence, and no validation rule (VR-1…VR-8) covers cross-document
consistency at that level.

**Recommended correction.** Preferred: add a documentation workflow pattern to
`workflows.md` — *assess existing docs → enumerate the source of truth →
reconcile claim-by-claim → author → verify against source → review ⤾* — because
the two stages it adds (reconcile, verify) are exactly the two D-02 shows are
missing, so one change closes both. Alternative: state explicitly in
`workflows.md` which intents deliberately have no pattern and what task type they
take instead. Do not leave the mapping implicit.

**Regression test.** **Yes**, folded into `S17`. Assert the run produces a staged
plan containing an explicit verification stage, rather than collapsing to a
single-skill invocation.

---

### D-06 · The skill's top decision rule proposes adopting a technology SR-3 forbids activating — **Low**

**Finding.** Decision-framework step 1 is "Does a source of truth already exist
that this documentation could be generated from (an OpenAPI spec, a type
definition, a schema)? If so, prefer generating from it" (SKILL.md:78-81), and
Knowledge calls OpenAPI "the clearest instance of this in this library's own
research" (:57-66). For this repo no OpenAPI document exists and none is named,
so SR-3 correctly excludes `openapi-swagger` — all four of its activation
conditions presuppose an existing document or deployed tooling (skill.yaml:29-33).

The router's behaviour is right. The *outcome* is that the skill's highest-priority
recommendation — adopt OpenAPI so the docs cannot drift — is a **proposal to
introduce a technology**, which is `solution-architecture`'s territory
(activation: "A significant technology choice is open"), and nothing routes it
there. The run therefore either hand-writes twelve endpoints of prose, accepting
the drift risk its own anti-patterns condemn (SKILL.md:139-141), or adopts
OpenAPI implicitly with the owning technology skill never loaded.

**Root cause.** The library has no edge for "a Layer-2 skill recommends adopting a
technology that is not currently present." SR-3 is a *detection* gate, and a
recommendation is not a detection. Note the gate is self-resolving once the user
agrees: SR-3 admits a technology "named in the request," so a user saying "yes,
use OpenAPI" activates `openapi-swagger` correctly on the next turn.

**Recommended correction.** Add to `technical-documentation`'s escalation: "A
recommendation to adopt a spec or source-of-truth technology not currently in the
repository is raised as an open decision for `solution-architecture` / the user,
not adopted implicitly." Generalisable to any Layer-2 skill whose decision
framework can propose a new technology.

**Regression test.** No separate scenario. Fold in as one assertion on `S17`: if
the run recommends OpenAPI, it appears in `open_questions[]` as a decision, not
in `changes[]` as a fait accompli.

---

## What the library gets right here

Stated because it is the larger half of the result and because several findings
above are visible only *because* the surrounding mechanism is precise.

- **SR-2 works exactly as designed on the hardest adjacent pair.**
  `code-commenting` and `technical-documentation` are the two prose skills and
  they cross-route each other explicitly and reciprocally
  (`code-commenting/SKILL.md:21,87`; `technical-documentation/skill.yaml:34`).
  No ambiguity, no overlap, no `conflicts_with` needed.
- **SR-3 holds under pressure.** A documentation task is the classic over-activation
  invitation — every technology in the repo is arguably "documentable." All 40
  `SK-TECH-*` skills stay out.
- **Context loading is exemplary.** One 189-line Tier-A body, no Tier-2, no
  technology skills, no orchestration overhead. Matches `context-audit.md`'s
  C-04 finding that the frequently-loaded generic skills are the small ones.
- **The skill's judgement is right even where its method is missing.** The
  anti-drift stance, the generate-from-source preference, the link-don't-duplicate
  rule, and the ADR structure are all correct and well-grounded. Every finding
  above is about *procedure*, not about *values* — which is the better of the two
  problems to have.

---

## Score

| # | Dimension | Score | Note |
|---|---|---|---|
| 1 | Skill routing | **4 / 5** | Correct skill, correct and reasoned exclusions. −1 for the D-06 tension and the borderline `api-design` call. |
| 2 | Dependency activation | **3 / 5** | `depends_on_skills: []` is defensible, but D-02 shows a real missing linkage to whatever produces the endpoint inventory. No prerequisite chain at all for a multi-stage job. |
| 3 | Context efficiency | **5 / 5** | Proportional and then some. Nothing loaded that the task did not need. |
| 4 | Implementation quality | **2 / 5** | Two distinct deliverables, one undifferentiated output, no per-artifact content model (D-01). |
| 5 | Security | **4 / 5** | The skill names SECURITY.md and placeholder-credential discipline (SKILL.md:143-151); S-Gate 3 covers the secret-in-README risk at the orchestrator layer. |
| 6 | Testing | **2 / 5** | `testing-strategy` is correctly excluded, but no verification stage exists for the docs themselves (D-02, D-05) and the setup-instruction executability limit is never declared (D-03). |
| 7 | Maintainability | **4 / 5** | Anti-rot, anti-duplication, generate-from-source: the skill's whole value proposition is maintainability and it argues it well. |
| 8 | Error handling | **2 / 5** | No escalation for a doc/code contradiction (D-04); no capability-degradation rule (D-03). Two branches this exact task will hit. |
| 9 | Repository convention adherence | **4 / 5** | ST-5 conventions travel to the writing stage; the skill respects existing docs and updates in place; `git-conventions` attaches correctly on commit. |
| 10 | Final outcome | **3 / 5** | A plausible-looking README and twelve endpoint sections that nobody verified, with a stale-README contradiction likely resolved silently. Better than no guidance; not something a principal engineer would sign off without a second pass. |
| | **Total** | **33 / 50** | |

**One-line verdict.** Well-routed and context-efficient; **under-verified**. The
library knows exactly what good documentation *is* and has no procedure for
establishing that it produced any.

---

## Proposed regression scenarios

| ID | Name | Category | Covers | Already covered? |
|---|---|---|---|---|
| `S17` | api-docs-and-stale-readme | Multi-skill tasks | D-01, D-02, D-04, D-05, D-06 | **No** — `evaluations/scenarios/` has no documentation scenario at all |
| `S18` | readme-setup-unverifiable | Failure scenarios | D-03 | **No** — S14 covers shell loss for a *test suite*, not for docs |
