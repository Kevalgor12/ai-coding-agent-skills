# Evaluation Specification

Status: **design + first content**. This is Step 30 of the project's master
build plan — the behavioral evaluation suite for the Skill Library. It
defines what "correct" means for a skill-driven run, in a form concrete
enough to score, and grounds every scenario in the vocabulary already
established by [`core/orchestrator/`](../core/orchestrator/),
[`core/routing-architecture/`](../core/routing-architecture/), and
[`core/dependency-architecture/`](../core/dependency-architecture/) rather
than inventing a parallel one.

## What this suite is not

Per the master plan's own instruction, this suite does **not** evaluate:

- prose quality
- file existence
- formatting
- keyword presence

Those are already covered elsewhere and cheaply: file existence and
formatting are mechanical (`core/skill-specification/specification.md`'s
validation rules, VR-1 through VR-8, and content-expectation rules CE-1/
CE-2), and prose/keyword checks are what [`audits/individual-skills/`](../audits/individual-skills/)
already did per-skill. A behavioral suite that re-tested those would be
redundant and would miss the thing that actually matters: **whether a
skill, when activated on a real task, causes an agent to behave
correctly** — not whether the skill's text reads well.

## What this suite evaluates

15 dimensions, verbatim from the master plan, each grounded in an existing
design artifact rather than defined fresh:

| # | Dimension | Grounded in |
|---|---|---|
| 1 | Correct skill activation | `core/routing-architecture/rules.md` (selection rules), the default-deny principle |
| 2 | Correct dependency resolution | `core/dependency-architecture/` (the 8 edge types), VR-4 (acyclic, layer-monotone) |
| 3 | Correct sequencing | `core/dependency-architecture/README.md`'s execution-semantics model (`A → B`) |
| 4 | Correct parallelization | The same model's `A ∥ B` semantic, `core/dependency-architecture/matrices.md`'s parallelization matrix |
| 5 | Correct context usage | `core/routing-architecture/rules.md` (context-selection rules), [`audits/cross-skill/context-audit.md`](../audits/cross-skill/context-audit.md)'s CS-9 (an affinity hint is not a load list) |
| 6 | Correct implementation decisions | Each activated skill's own `decision_framework_present`/Decision framework section |
| 7 | Correct security behavior | `SK-QA-002`/`SK-AI-008`'s owned content; the orchestrator's `security-and-validation.md` gates |
| 8 | Correct testing behavior | `SK-QA-001`/`SK-AI-007`'s owned content; the orchestrator's testing gates |
| 9 | Correct failure handling | Each skill's `failure_handling` field; the orchestrator's `failure-recovery-and-escalation.md` (F1–F9, R1–R8) |
| 10 | Correct escalation | Each skill's `escalation` field; the orchestrator's gate classes (GA-0…GA-8) |
| 11 | Repository convention adherence | `SK-CONV-001` (git-conventions), `SK-CONV-002` (code-commenting), the precedence ladder (`state-and-contract.md`) |
| 12 | Technology-specific accuracy | Each `kind: technology` skill's `covered_versions`/`source_references`, cross-checked against `research/technologies/` |
| 13 | Maintainability | QR-1 (no unnecessary abstraction), the anti-over-engineering trap every skill's Anti-patterns section is required to name (QR-4) |
| 14 | Performance reasoning | `SK-QA-003` (performance-engineering)'s decision framework; "measure before optimizing" |
| 15 | Documentation quality | `SK-CONV-006` (technical-documentation); this is the one dimension closest to "prose," but evaluated here as *did the task produce documentation a maintainer could act on*, not *is the prose polished* |

## The core method: behavioral assertions, not prose matching

Every scenario's expected outcome is expressed as a set of **assertions
about what happened**, checkable against the orchestrator's own invocation/
return envelope shape (`core/orchestrator/state-and-contract.md` Part 2) —
never as a required sentence or paragraph.

**Bad (prose matching, prohibited in this suite):**
> The agent's response must say "I recommend using parameterized queries to
> prevent SQL injection."

**Good (behavioral assertion, used throughout this suite):**
> `security-engineering` (or a technology skill specializing it) activates;
> its return envelope's `verification[]` includes a check against
> SQL-injection risk with `pass`/`fail` (not `not-run`); if the task
> involves raw string interpolation into a query, the run's `status` is not
> `complete` until that check passes or an `unverified_claims` entry
> explains why it could not run.

The second form is checkable by inspecting *what the run actually did*
(which skills activated, what their return envelopes contain, what gates
fired, what got escalated) regardless of the specific words a model
chooses to use. This is also why every scenario names an explicit
**activation set** (both included and excluded skills, per SR-11's
completeness-backstop discipline and CS-9's anti-over-loading discipline)
rather than only a prose task description — a scenario that only says
"handle this task" cannot be scored behaviorally.

## Scenario schema

Every file under `scenarios/` follows this structure:

```markdown
# Scenario: <id> — <short name>

**Category:** <one of the 8 categories below>
**Complexity:** trivial | small | multi-step | project
**Risk level:** read-only | reversible-write | destructive | outward-facing | production

## Task

<The exact request a user would give, verbatim — this is what gets "handed to" the router.>

## Repository signals

<What's actually in the repo: manifests, config files, file extensions, existing code —
whatever a real router would detect. Absence of a signal is itself a signal (e.g. "no
test files present" is relevant to whether testing-strategy should activate).>

## Expected activation set

**Must activate:** <skill IDs, each with the one-line reason — the activation
condition it matches>
**Must NOT activate:** <skill IDs a naive/keyword-based router might wrongly pull in,
each with the non-activation condition or scoping reason it should be excluded on>
**Uncertain / acceptable either way:** <skills where a reasonable router could go
either way — named explicitly so a false activation here isn't scored as an error>

## Expected sequencing and parallelization

<Which determinations from routing-architecture apply: sequential edges (prerequisite),
parallel opportunities, conditional gates, iteration/review loops — expressed as the
`A → B` / `A ∥ B` / `[cond] A` / `⟳ A` / `A ⤾ R` notation from
core/dependency-architecture/README.md.>

## Expected behavioral assertions

<One row per applicable dimension from the 15 above — only the dimensions this
scenario actually exercises, not all 15 every time. Each assertion is checkable
against a return envelope, a gate record, or a recovery-ladder rung, not against
prose content.>
```

Every scenario file under `scenarios/` has a matching file under
`expected-behaviors/` with the same base filename — `scenarios/S03-...md`
pairs with `expected-behaviors/S03-...md`. The `scenarios/` file states the
task and setup; the `expected-behaviors/` file states the full graded
assertion list plus the scoring weight of each (see `scoring.md`). This
split exists so a scenario can be handed to an agent under test **without**
the answer key attached in the same file.

## The 8 required scenario categories

Per the master plan, verbatim, with this suite's interpretation of each:

1. **Simple tasks** — a single, unambiguous skill clearly owns the task.
   Tests that the router does *not* over-activate (SR-2/SR-7 self-suppression) —
   the main failure mode here is false-positive activation, not a missing skill.
2. **Ambiguous tasks** — the correct skill set is genuinely non-obvious from
   the request alone and depends on repository signals or a clarifying
   question. Tests intent classification and the router's handling of
   under-specified requests.
3. **Multi-skill tasks** — a task spanning several domains (e.g. build +
   verify phases), exercising sequencing, parallelization, and the
   workflow-composer's staged-plan behavior.
4. **Security-sensitive tasks** — exercises dimension 7 directly: does the
   right security skill activate, and does a destructive/outward-facing
   action get gated per the orchestrator's `security-and-validation.md`.
5. **Performance-sensitive tasks** — exercises dimension 14: does
   `performance-engineering` (or a technology skill) activate on a genuine
   performance complaint, and does it correctly demand a measurement before
   recommending an optimization (the anti-pattern every performance-adjacent
   skill is expected to guard against).
6. **Legacy-code tasks** — exercises `legacy-modernization`/`refactoring`
   activation and their (already flagged, see
   [`audits/2026-09-10-individual-skill-review.md`](../audits/2026-09-10-individual-skill-review.md))
   VR-4 upward dependency on QA skills — a good stress test for whether that
   tension actually causes a bad run in practice or is benign.
7. **Failure scenarios** — a step's `verification` fails, a capability turns
   out to be unavailable mid-run, or a tool call errors. Exercises the
   recovery ladder (F1–F9 → R1–R8) directly.
8. **Conflicting-requirement scenarios** — the user's request and a
   repository convention disagree, or two plausible skills would recommend
   incompatible things. Exercises the precedence ladder (`state-and-contract.md`:
   safety > user instruction > repo convention > skill default > library
   default) and `conflicts_with` resolution.

## Honest scope

**What exists after this step:** a spec, a 16-scenario scenario+expected-behavior
corpus (2 per category), a scoring method, and a regression-suite process
description. **What does not exist:** an executable test harness. This
repository has no runtime that invokes skills against a live agent — skills
are markdown instructions consumed by an external host (Claude Code,
Cursor, etc.), not code this repository can execute in CI. Running this
suite today means: a human (or an agent explicitly role-playing "the
orchestrator") works through a scenario using the actual skill files as
instructions, and scores the resulting run against `expected-behaviors/`
per `scoring.md`. This is the same honest-scoping discipline
`core/orchestrator/observability-and-evaluation.md` already applied to its
own evaluation hooks (EH-1 through EH-5) — this suite is what turns EH-3's
"observation" into an actual scored evaluation, and what EH-4's fixture
format is for, but it does not itself build a harness. Building an
automated harness, if ever warranted, is separate, later work.

## Files in this directory

- **`evaluation-spec.md`** (this file)
- **`scenarios/`** — one task description per scenario, no answer key
- **`expected-behaviors/`** — the paired, gradable assertion list per scenario
- **`scoring.md`** — how an assertion list becomes a score
- **`regression-suite.md`** — how this suite is meant to be re-run over time, and what triggers a re-run
