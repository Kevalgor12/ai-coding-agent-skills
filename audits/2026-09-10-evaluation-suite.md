# Audit: Behavioral Evaluation Suite (Step 30)

Date: 2026-09-10. Scope: the first behavioral evaluation suite for the
Skill Library, built under [`evaluations/`](../evaluations/). This is
**Step 30** of the project's master build plan
(`AI_Coding_Agent_Skill_Library_Complete_Step_By_Step.md`), model/effort
Sonnet 5 / High. Unlike Steps 27–29, this is a **build** step producing
new usable content, not an audit of existing content — though it inherits
and is grounded in everything those three prior steps established.

## What was built

| Deliverable | Content |
|---|---|
| [`evaluation-spec.md`](../evaluations/evaluation-spec.md) | The 15 behavioral dimensions (each mapped to an existing design artifact, not defined fresh), the scenario/expected-behavior schema, the 8 required scenario categories, honest scope statement |
| `scenarios/` | 16 task scenarios, 2 per category, no answer key |
| `expected-behaviors/` | 16 paired, graded assertion files (117 total assertions: 36 critical, 54 major, 27 minor) |
| [`scoring.md`](../evaluations/scoring.md) | The critical/major/minor weight vocabulary (formalized from what the 16 scenario files already converged on independently), assertion-level and scenario-level scoring rules, suite-level aggregation |
| [`regression-suite.md`](../evaluations/regression-suite.md) | Re-run triggers, the manual run procedure (no harness exists), a dated-log tracking format, coverage-growth priorities |
| [`README.md`](../evaluations/README.md) | Updated from its stale "no skills exist yet to evaluate" placeholder (86 skills exist) |

Grounded throughout in `core/orchestrator/state-and-contract.md`'s
invocation/return envelope shape and six-status model, so a scenario's
expected behavior is checkable against what a real run's record would
contain, not against required prose — directly answering the master
plan's explicit instruction to prefer behavioral assertions over exact
prose matching.

## Process note: a mid-batch API session-limit interruption

6 of the first 8 scenario-writing agents (all but "ambiguous" and
"failure") hit a hard API session-limit error partway through and
terminated before writing their assigned files. Two (`simple`,
`legacy-code`) left partial, truncated scenario files on disk (a complete
`scenarios/S01...md` with no matching `expected-behaviors/` file; two
`scenarios/` files with only their first two of four required sections).
After the user confirmed the session limit had reset, all 6 categories
were re-dispatched as fresh agents, explicitly pointed at the existing
partial files with instructions to complete rather than discard them
where the existing content was good (it was, in both cases — the partial
work was reused, not thrown away). All 16 scenario/expected-behavior pairs
were independently confirmed present and complete before proceeding.

This step also applied a lesson directly from Steps 27–28: every one of
the 8 (then 6 retry) scenario-writing agents was explicitly instructed
not to spawn sub-agents and not to run git commands. None did — confirmed
via `ListAgents` showing exactly the dispatched agent count at every check
during this step, and via `git status` showing no unexpected commits.

## A real defect found and fixed during verification

Independent verification (never trusting an agent's self-report, per this
project's standing discipline) caught one factual inaccuracy in
`expected-behaviors/S06-user-auth-email-verification.md`: the scenario
asserted that `SK-BE-005` (authentication-authorization) has a hard
`depends_on_skills`-style **composition** edge into `SK-QA-002`
(security-engineering), citing `core/taxonomy/skill-catalog.md`'s
"Dependencies: `SK-QA-002` (security)" line for that skill. Checked
directly: `skills/authentication-authorization/skill.yaml`'s actual
`depends_on_skills` field is `[]` — `SK-QA-002` is declared only in
`related_skills`. This is a live instance of the exact catalog-imprecision
pattern `audits/cross-skill/cross-skill-audit.md` already flagged as a
repo-wide finding (the catalog's "Dependencies:" field conflating
relationship types) — the scenario-writing agent took the catalog's prose
at face value rather than checking the underlying `skill.yaml`.

**Fixed** by reclassifying the relationship: since `SK-QA-002`'s review
genuinely needs `SK-BE-005`'s concrete design as input (which hashing
scheme, what "expired" means) but is not invoked *by* `SK-BE-005` as an
internal sub-step, the correct edge type per
`core/dependency-architecture/README.md`'s own vocabulary is
**prerequisite** (`A ⇐ B`), not **composition** (`A → B`). This changes a
concrete, checkable consequence in the scenario: `SK-QA-002` must appear
as its **own** entry in a compliant run's activation record, not folded
silently into `SK-BE-005`'s activity — the sequencing diagram, the prose
explanation, and two dependent assertions were all corrected to match,
and the scenario's underlying conclusion (that `SK-QA-002` should
activate at all) was preserved, since it independently holds on
`SK-QA-002`'s own activation condition alone (reason (b) in the original
draft), which is unaffected by the composition/prerequisite distinction.

This is the kind of finding this evaluation suite exists to make routine:
a scenario's own construction surfaced a real, previously-undetected
instance of an already-tracked systemic issue, simply by requiring every
activation claim to be precise enough to grade.

## Verification performed

- All 16 `scenarios/*.md` files confirmed to have a matching
  `expected-behaviors/*.md` file (and vice versa) — no orphans in either
  direction.
- All 16 scenario files confirmed to carry all 4 required top-level
  sections (Task, Repository signals, Expected activation set, Expected
  sequencing and parallelization) — the two truncated partial files from
  the interrupted first pass were confirmed complete after the retry.
- Spot-checked specific factual claims across a sample of scenarios
  against the actual `skill.yaml` files and design documents they cite:
  the `git-conventions`/`git-workflow` scope boundary (S02), the
  `SK-BE-005`/`SK-QA-002` relationship (S06 — found and fixed, above), the
  `redis` non-activation-condition quote (S10), and the precedence
  ladder's exact wording (S15) — all confirmed to quote their sources
  precisely, with the one exception already corrected.
- Confirmed the `critical`/`major`/`minor` weight vocabulary was used
  consistently across all 16 files (117 total assertions: 36/54/27) before
  formalizing it in `scoring.md`, rather than inventing a scheme the
  existing content would need retrofitting to match.
- Confirmed 77 of 86 authored skills are referenced somewhere across the
  16 scenarios (as a required activation, a correctly-required exclusion,
  or an explicitly-named uncertain case) — stated plainly in
  `regression-suite.md` as partial, not full, coverage.

## What this step deliberately did not build

Per `evaluation-spec.md`'s own honest-scope section: no executable test
harness. This repository has no runtime that invokes skills against a
live agent — skills are markdown instructions consumed by an external
host, not code this repository can execute in CI. Running this suite
today is a manual (or agent-role-played) process, scored by hand against
`scoring.md`. This mirrors the same honest-scoping discipline
`core/orchestrator/observability-and-evaluation.md` already applied to its
own evaluation hooks one step ago — this suite is what turns that
document's EH-3 "observation" into an actual scored evaluation and
supplies EH-4's fixture format, without building the harness EH-4 also
named as separate, later work.

## Overall assessment

The suite is grounded, not invented: every one of the 15 evaluated
dimensions, the scenario schema, and the scoring vocabulary trace to an
artifact this project already built (the orchestrator's envelope/status
model, the dependency-architecture's edge vocabulary, the routing-
architecture's own canonical examples, two prior audits' specific
findings). Several scenarios directly formalize claims this project's own
design documents already made in prose (S05 turns the routing-
architecture README's "realtime multiplayer game" claim into a gradable
scenario; S11/S12 turn the already-flagged VR-4 tension into an empirical
test of whether it causes a bad run in practice) — this is evaluation
content built to catch regressions in claims this library has already
made about itself, not a generic test suite bolted on afterward. The one
defect found during verification (S06's composition-vs-prerequisite
mischaracterization) is itself evidence the suite's own construction
process works: a scenario had to be precise enough to grade, and that
precision requirement is what surfaced an inaccuracy a looser prose
description would have let through unnoticed.
