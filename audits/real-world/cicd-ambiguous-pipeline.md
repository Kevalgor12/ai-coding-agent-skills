# Real-World Evaluation — "Add a CI pipeline that runs before every merge"

**Step 32 · Task 3 of 3 · Domain: CI/CD · Adversarial pattern: ambiguous requirements**

Date: 2026-09-11. Method per [`evaluations/regression-suite.md`](../../evaluations/regression-suite.md):
routed and executed against the actual skill files, then evaluated. Severity
vocabulary is this project's audit convention (Critical / High / Medium / Low).

> **Note on proposed scenario IDs.** Other Step-32 real-world evaluations were
> written into this directory in parallel and independently propose scenarios
> numbered from `S17`. The proposed scenario below should be identified by its
> **slug** — `ci-pipeline-over-knowingly-flaky-suite` — and assigned its numeric
> ID when it is actually authored into
> [`evaluations/scenarios/`](../../evaluations/scenarios/), after de-duplicating
> against every sibling file in this directory. References to `S18` below mean the
> scenario proposed in [`git-conflicting-conventions.md`](git-conflicting-conventions.md)
> (slug `strict-branch-protection-with-force-push-exemption`), not any
> similarly-numbered scenario proposed by a sibling evaluation.

## The task

> "Add a CI pipeline that runs before every merge."

**Repository context.** No existing CI config. The test suite is a mix of unit
tests (fast, reliable) and a handful of known-flaky integration tests — a
`FLAKY_TESTS.md` file in the repo documents 3 tests that fail ~10% of the time for
reasons the team has not fixed.

**What makes this adversarial.** The request is *clear in intent* and *silent on
the one parameter that decides whether the deliverable helps or hurts*: should the
flaky integration tests block a merge, be retried, or be quarantined out of the
required set? The three answers produce materially different pipelines. With 3
independent tests at ~10% each, "block on everything" fails roughly
**1 − 0.9³ ≈ 27%** of merges spuriously — a gate the team will route around within
a week, either by force-merging or by deleting the gate. The failure mode under
test is whether the library prompts for the clarification or silently picks a
default; and specifically whether `requirements-engineering` (SK-DISC-001) is
reachable given genuine ambiguity in a *bounded* task.

---

## What actually happens — the traced run

### P0 · Intake

- **ST-1.** Task statement recorded verbatim.
- **ST-4 · user constraints.** One: "before every merge" — a gating *point*.
  Nothing about gating *policy*.
- **Bounded signal scan** ([routing-algorithm.md:13-19](../../core/routing-architecture/routing-algorithm.md)).
  The categories are dependency manifests, config files (`tsconfig`,
  `next.config`, `drizzle.config`, **`.github/workflows/`**, `Dockerfile`),
  connection strings / driver imports, file types present, and existing
  conventions (`git log`, commitlint config). CS-6 bounds it further: "the repo
  scan reads manifests/config/entrypoints, not the whole tree; it's for detection,
  not comprehension" ([rules.md:64-65](../../core/routing-architecture/rules.md)).

  What the scan *does* find: no `.github/workflows/`, a manifest with test
  scripts, an integration-test directory, the test runner in devDependencies.
  What it does **not** find: `FLAKY_TESTS.md`. A root-level markdown policy
  document is not a manifest, a config file, a connection string, a file type, or
  a commit convention. **The single fact that determines the correct pipeline
  design is outside the signal set.** See **C-1**.
- **Classification.** Intent = `build`/`config`. Task type = infra setup (the
  closest precedent is [examples.md:189-199](../../core/routing-architecture/examples.md),
  Example 7). Complexity = **small** (one config file). Risk = **reversible-write**
  (authoring `.github/workflows/ci.yml`).
- **D2 · "Is intent genuinely ambiguous on a non-trivial task?"**
  ([lifecycle.md:86-88](../../core/orchestrator/lifecycle.md)) — intent is clear:
  add CI, gate merges. What is unspecified is a *parameter*, not the intent. D2
  keys on intent. **No escalation.** See **C-5**.
- **D3 · highest-risk action.** Writing one YAML file — trivially reversible. The
  *consequence* is a standing gate every future pull request must clear. The risk
  taxonomy has no value for that; it classifies the file write.
  See **C-2**, and compare **G-9** in
  [`git-conflicting-conventions.md`](git-conflicting-conventions.md) — the same
  action-vs-policy blind spot reached from a different domain.
- **S-Gate 1 · security intake screen** — correctly fires. CI configuration
  touches tokens and secrets, and this drives `ci-cd-pipeline`'s genuinely strong
  security posture (see *positives*).

### P1 · Discovery

- Conventions detection (ST-5,
  [lifecycle.md:101-105](../../core/orchestrator/lifecycle.md)) records
  "commit/branch style, comment style, lint/format config, **test framework and
  layout**, directory conventions." The test framework and layout *are* detected.
  A documented team decision to tolerate three flaky tests is a repository
  convention by any reasonable reading and is not in the enumerated list.
  See **C-1**.
- Technology detection (SR-3): the test runner is detected. **The CI platform is
  not** — there is no `.github/` directory and the request names no platform.

### P2 · Routing — the selected set

| Skill | Tier-0 verdict | Reasoning |
|---|---|---|
| `ci-cd-pipeline` (SK-INFRA-002) | **INCLUDE** | `activation_conditions[0]` ([skill.yaml:34](../../skills/ci-cd-pipeline/skill.yaml)): "Setting up CI/CD for a project that doesn't have it" — exact match |
| `github-actions` (SK-TECH-github-actions) | **EXCLUDE initially**, admissible once the platform is settled | `activation_conditions[0]` ([skill.yaml:36](../../skills/github-actions/skill.yaml)) covers a workflow file "being authored", but `non_activation_conditions[0]` ([skill.yaml:40](../../skills/github-actions/skill.yaml)) — "Platform-agnostic pipeline design with **no CI platform chosen yet** (route to ci-cd-pipeline)" — matches, and SR-2 is decisive. Correct, and a genuine positive |
| `testing-strategy` (SK-QA-001) | **contested** | Its own activation ("Deciding test strategy or structure for a project"; "An existing test suite's layer distribution, isolation, or fixture design needs review", [skill.yaml:34,37](../../skills/testing-strategy/skill.yaml)) matches, and [examples.md:193-194](../../core/routing-architecture/examples.md) composes it. But SR-5 says "`testing-strategy` only when runnable code is produced" ([rules.md:26-27](../../core/routing-architecture/rules.md)) and a YAML config is not runnable code. See **C-3** |
| `jest-vitest` / `playwright` | INCLUDE iff detected | SR-3 detection-gating, correct |
| `husky` (SK-TECH-husky) | EXCLUDE | `non_activation_conditions[0]` ([skill.yaml:40](../../skills/husky/skill.yaml)): "The task is CI/CD pipeline design itself… route to ci-cd-pipeline". Correct and crisp |
| `deployment-release` (SK-INFRA-003) | EXCLUDE | `non_activation_conditions[2]` ([skill.yaml:41](../../skills/deployment-release/skill.yaml)): "CI/CD pipeline definition itself… route to ci-cd-pipeline". Correct routing — though the same line carries a stale "(not yet authored)" marker, an instance of the already-tracked **X-02** ([cross-skill-audit.md:597](../cross-skill/cross-skill-audit.md)), not re-derived here |
| `security-engineering` (SK-QA-002) | either-way | SR-5 fires if OIDC/secrets are configured, per [examples.md:196-198](../../core/routing-architecture/examples.md). `ci-cd-pipeline` carries the relevant content inline regardless |
| `requirements-engineering` (SK-DISC-001) | **EXCLUDE** | see below — this is the task's central question |
| `git-workflow` (SK-CONV-008) | EXCLUDE | Required-status-check configuration is repository governance, which its activation conditions do not cover — the same gap documented as **G-3** in [`git-conflicting-conventions.md`](git-conflicting-conventions.md). Relevant here because "runs before every merge" implies a *required check*, which is a governance setting, not a workflow file |

### Would `requirements-engineering` be pulled in? Tracing its own activation conditions

This is the specific question the task poses. Four independent gates, and the
skill fails three of them:

1. **Its own `activation_conditions[0]`**
   ([skill.yaml:28](../../skills/requirements-engineering/skill.yaml)) — "The
   request is under-specified, ambiguous, or **open to more than one reasonable
   interpretation**." On the gating policy this genuinely matches:
   block-on-everything, retry-the-flaky-three, and split-required-from-advisory
   are three reasonable readings producing materially different pipelines.
   **Match.**
2. **Its `non_activation_conditions[0]`**
   ([skill.yaml:33](../../skills/requirements-engineering/skill.yaml)) — "The
   requirements are already explicit, unambiguous, and **narrowly scoped**." "Add
   a CI pipeline that runs before every merge" reads explicit and narrowly scoped
   on its face. SR-2: "If a skill's non-activation conditions match the signals,
   exclude it — **even if its activation also matches**"
   ([rules.md:12-15](../../core/routing-architecture/rules.md)). **Excluded.**
3. **SR-8 · discovery proportionality**
   ([rules.md:36-38](../../core/routing-architecture/rules.md)) — "`requirements` /
   `solution-architecture` / `technical-planning` engage for new, multi-domain, or
   high-risk work — **not for a bounded single-file change**." Authoring one
   `ci.yml` is a bounded single-file change. **Excluded.**
4. **The activation decision tree**
   ([routing-algorithm.md:142-144](../../core/routing-architecture/routing-algorithm.md))
   — "Complexity ≥ multi-step OR risk ≥ destructive? → YES → engage discovery."
   Complexity is `small`; risk is `reversible-write`. **Excluded.**

And the library's own closest worked example agrees. Example 7 — "Set up CI to
run our tests on every push" — selects `ci-cd-pipeline → github-actions`
composing `testing-strategy`, and names **no discovery skill at all**
([examples.md:189-199](../../core/routing-architecture/examples.md)).

**Verdict: `requirements-engineering` does not activate.** Three of the four gates
exclude it, and the fourth is a knife-edge reading of a single non-activation
clause. See **C-5**.

The irony is sharp: `requirements-engineering`'s *body* contains precisely the
right test. Decision-framework step 1
([SKILL.md:80-83](../../skills/requirements-engineering/SKILL.md)) —
"**How reversible is a wrong interpretation?** Cheap-to-undo… → proceed on the
most reasonable reading… Expensive-to-undo… → resolve the ambiguity before any
design work starts" — and step 2 — "Genuinely multiple plausible readings that
lead to materially different systems → **this is a blocking question, not a
footnote**". Applied here it returns *block and ask*. But CS-1 forbids the router
from reading a body to decide selection
([rules.md:53-55](../../core/routing-architecture/rules.md)), so the correct test
sits one layer below the decision that would have used it. (Structurally identical
to GA-8's unreachability in Task 2 — the right answer present at the wrong layer.)

### P4 · Admission

**D13** ([lifecycle.md:191-201](../../core/orchestrator/lifecycle.md)) requires
plan confirmation when risk is destructive/outward-facing/production, or an
irreversible commitment is locked in, or complexity is `project`, or the plan grew
beyond the request. None applies: "Not required for `read-only` or bounded
`reversible-write` work of small complexity — proportionality… applies here too,
and asking for confirmation of a one-file edit is friction, not safety." **The run
proceeds straight to authoring, unconfirmed.** See **C-2**.

### P5 · Execution — does `ci-cd-pipeline` prompt for the clarification?

**No. It silently resolves the ambiguity, in the direction that maximizes damage
here, and its own verification criterion then rewards the result.**

| Where | What it says |
|---|---|
| Decision framework step 1 ([SKILL.md:90-93](../../skills/ci-cd-pipeline/SKILL.md)) | "**What gates the merge?** Tests, lint, and build **should block merge by default** — a pipeline that runs these advisory-only when they're meant to gate is a common, easy-to-miss design mistake." A prescription, not a question |
| Workflow step 2 ([SKILL.md:114-115](../../skills/ci-cd-pipeline/SKILL.md)) | "Design stage sequencing so tests/lint/build gate the merge." |
| Engineering rule 1 ([SKILL.md:133-134](../../skills/ci-cd-pipeline/SKILL.md)) | "Tests/lint/build gate the merge by default; a pipeline that runs them advisory-only **should be a deliberate, stated choice**, not an oversight." The escape hatch exists — but nothing instructs the agent to *raise* the choice with the user |
| Anti-pattern 1 ([SKILL.md:155-156](../../skills/ci-cd-pipeline/SKILL.md)) | "**Running tests/lint/build as advisory-only** when they're meant to gate the merge." Actively biases away from the non-blocking option |
| `verification[0]` ([skill.yaml:89](../../skills/ci-cd-pipeline/skill.yaml)) | "Tests/lint/build gate the merge — the pipeline doesn't just run them advisory-only when they're meant to block." The skill's own success criterion **scores block-on-everything as correct** |
| `evaluation_criteria[0]` ([skill.yaml:93](../../skills/ci-cd-pipeline/skill.yaml)) | "Produces a pipeline that **gates merge on tests**/lint/build…" — same, at the evaluation layer |
| `failure_handling` ([skill.yaml:85-87](../../skills/ci-cd-pipeline/skill.yaml)) | Exactly two branches: missing build/test/lint commands (request them), existing pipeline (work within it). **No branch for an unspecified gating policy** |
| `required_context` ([skill.yaml:50-51](../../skills/ci-cd-pipeline/skill.yaml)) | "The repo's build/test/lint **commands** and how they're currently run" — the commands, not the policy. So CS-3's ask-or-degrade ([rules.md:56-59](../../core/routing-architecture/rules.md)) cannot fire on the policy gap: `required_context` is fully satisfiable without ever confronting it |

Nothing in the skill mentions flaky tests, test reliability, retries,
quarantine, required-vs-optional checks, or `continue-on-error`.

### The gap behind the gap: no skill owns flaky-test policy

Verified by grep across `testing-strategy`, `ci-cd-pipeline`, `github-actions`,
`jest-vitest`, `playwright`, and `code-quality`:

- `testing-strategy` treats flakiness **only as a property to avoid when
  authoring**: `verification[1]` — "Tests are isolated and deterministic — no
  shared mutable state… **no flaky timing dependencies**"
  ([skill.yaml:87](../../skills/testing-strategy/skill.yaml)); SKILL.md:147 and
  :170 in the same vein. There is nothing about triaging, quarantining, retrying,
  or gating on an *already-flaky* suite that the team has chosen not to fix.
- `playwright` has real retry mechanics — `retryStrategy: 'isolated'`
  ([SKILL.md:244-245](../../skills/playwright/SKILL.md)) — but it is
  detection-gated (SR-3) and may not be the repo's runner, and its content is
  tool mechanics, not gating policy.
- `github-actions` mentions re-running failed jobs manually
  ([SKILL.md:328-331](../../skills/github-actions/SKILL.md)) — a remediation
  action, not a design decision.

So even if a run *did* ask the right question, no skill owns the answer.
See **C-4**.

### The compliant output

A single `.github/workflows/ci.yml` — well-structured, dependency-cached with the
real 7-day/10GB/LRU limits accounted for, `GITHUB_TOKEN` scoped read-only with
per-job elevation, third-party actions SHA-pinned, OIDC preferred over static keys
— running the **entire** suite as a blocking merge gate. Technically excellent;
spuriously red roughly one merge in four; scored `complete` by the skill's own
`verification` and `evaluation_criteria`.

---

## Findings

### C-6 · `ci-cd-pipeline` silently resolves the merge-gating policy, and its own verification rewards the wrong answer — **High**

**Finding.** The skill's decision framework opens with "What gates the merge?" and
immediately answers it — "Tests, lint, and build should block merge by default" —
rather than treating it as a decision to surface. The prescription is reinforced
at five further points (workflow, engineering rule, anti-pattern, `verification`,
`evaluation_criteria`), and the skill's `required_context` is satisfiable without
ever encountering the question. Applied to this repository the result blocks ~27%
of merges for reasons the team has already decided not to fix — and the skill's
own success criteria score it as correct.

The engineering rule's qualifier ("should be a deliberate, stated choice, not an
oversight") is the right instinct, but it addresses the *agent's* deliberation,
not the *user's* decision. There is no instruction to ask.

**Root cause.** The skill was authored against the *general* case, where
block-on-everything is genuinely the right default and advisory-only gates are
genuinely a common mistake. The general-case advice was then hardened into a
`verification` item — converting a good default into a criterion that cannot
recognize a legitimate exception. This is the inverse of the over-engineering trap
QR-4 asks every skill to name: an under-parameterized default presented as a
correctness property.

**Recommended correction.** Three edits to
[`skills/ci-cd-pipeline/`](../../skills/ci-cd-pipeline/):

1. Split decision-framework step 1 into the default *and* its precondition:
   > **1. What gates the merge, and is every gated check actually trustworthy?**
   > Tests, lint, and build should block merge by default. **Before committing to
   > that, check whether any check in the gated set is known-unreliable** — a
   > documented flaky test, a test depending on an external service, a long-tail
   > timeout. A gate that fails spuriously is worse than no gate: teams route
   > around it, and it trains everyone to ignore red. Where unreliable checks
   > exist, the choice between *block*, *bounded retry*, and *quarantine out of
   > the required set* is the **user's decision, not a default** — surface it with
   > the spurious-failure rate implied by each option.
2. Add a `failure_handling` branch: *"If the repository contains known-unreliable
   tests, or the gating policy for them is unstated, surface the choice (block /
   retry / quarantine) with its consequences before authoring the pipeline rather
   than assuming block-on-everything."*
3. Amend `verification[0]` to: *"Tests/lint/build gate the merge — **and every
   check in the required set is one the team considers trustworthy; any
   known-unreliable check is either excluded from the required set by an explicit
   recorded decision, or its blocking behavior was confirmed with the user.**"*

**Regression test requirement.** **New scenario required.** Checked
[`evaluations/scenarios/`](../../evaluations/scenarios/): the two ambiguous-task
scenarios are S03 ("app feels slow" — no object, no cause) and S04 ("can you clean
this up?" — no object at all). **Both test a request that is ambiguous in its
*object*. Neither tests a request that is clear in its object and ambiguous in a
consequential *parameter*.** That is a distinct and arguably more common shape.
Propose `S19 — CI pipeline over a knowingly-flaky suite`, category *ambiguous
tasks*, repository signals including `FLAKY_TESTS.md` verbatim, with a `critical`
assertion that the run surfaces the gating-policy choice before authoring the
workflow, and a `critical` assertion that it does not author a required check over
the documented-flaky tests without an explicit user decision.

---

### C-5 · Discovery is gated on scope, never on the consequence of a wrong default — **High**

**Finding.** Every mechanism that could engage `requirements-engineering` keys on
the *size* of the change rather than the *cost of guessing wrong*:

- SR-8 — "not for a bounded single-file change"
  ([rules.md:36-38](../../core/routing-architecture/rules.md)).
- The decision tree — "Complexity ≥ multi-step OR risk ≥ destructive?"
  ([routing-algorithm.md:142-144](../../core/routing-architecture/routing-algorithm.md)).
- D13 admission — risk class, irreversible commitment, `project` complexity, or
  plan growth ([lifecycle.md:191-201](../../core/orchestrator/lifecycle.md)).
- The skill's own `non_activation_conditions[0]` — "narrowly scoped"
  ([skill.yaml:33](../../skills/requirements-engineering/skill.yaml)).

A one-file change whose wrong default costs the team a broken merge gate is
exactly the case none of these reaches. And the correct test — "How reversible is
a wrong interpretation?" — exists in the skill body
([SKILL.md:80-83](../../skills/requirements-engineering/SKILL.md)) where CS-1
forbids the router from consulting it.

Note the pattern across this evaluation: `requirements-engineering` is correctly
excluded in Task 1 (a genuinely well-specified request), and incorrectly excluded
in both Task 2 (**G-5**) and Task 3 — in both cases by the *same*
`non_activation_conditions[0]` clause. The clause is doing too much work.

**Root cause.** SR-8 encodes a real and correct anti-pattern — over-eliciting a
trivial task, which the skill itself names as its own over-engineering trap
([SKILL.md:131-133](../../skills/requirements-engineering/SKILL.md)). But it
proxies "low stakes" with "small scope," and the two diverge precisely for
configuration and policy work, where a small artifact carries a large standing
consequence.

**Recommended correction.** Amend SR-8 to carry both axes:

> **SR-8 · Discovery proportional to complexity, risk, *and the cost of a wrong
> default*.** `requirements` / `solution-architecture` / `technical-planning`
> engage for new, multi-domain, or high-risk work — and additionally whenever a
> **bounded** task turns on an unstated parameter whose plausible values produce
> materially different outcomes, or whose wrong value is expensive for the user to
> discover later. Scope is not a reliable proxy for stakes: a one-file
> configuration change can create a standing policy. Elicitation stays
> proportional — surface the one decision, do not run the full checklist.

Add a matching clause to the decision tree and lift the reversibility test out of
`requirements-engineering`'s body into an activation condition:
*"The request is bounded but turns on an unstated parameter whose plausible values
lead to materially different outcomes."*

**Regression test requirement.** Covered by the proposed `S19` with a `critical`
assertion that `requirements-engineering` (or an equivalent user-facing
clarification before authoring) appears in the selected set with the
consequence-of-wrong-default reason recorded. Also re-run S01 and S02 after the
SR-8 change — both are *simple task* scenarios whose central claim is that the
router does **not** over-activate, and a loosened SR-8 is exactly the kind of edit
that could regress them (`regression-suite.md` trigger 3).

---

### C-4 · No skill owns flaky-test policy — **High**

**Finding.** The library has no owner for triaging, quarantining, retrying, or
gating on an already-flaky test suite. `testing-strategy` treats determinism as an
authoring property to preserve
([skill.yaml:87](../../skills/testing-strategy/skill.yaml)) and offers nothing for
a suite that is already unreliable and knowingly so. `ci-cd-pipeline` does not
mention reliability of the gated checks at all. `playwright` carries retry
mechanics but is detection-gated and tool-specific. `github-actions` covers manual
re-runs, which is remediation, not design.

This is not a niche concern: a documented, tolerated flaky suite is an extremely
common state in real repositories, and it is the single input that determines
whether a merge gate helps or hurts.

**Root cause.** `testing-strategy` was grounded in
[`testing-knowledge-map.md`](../../research/knowledge-maps/testing-knowledge-map.md),
which is organized by *test layer* (unit/integration/e2e/component/visual/
contract/load) across 44 technologies. Flaky-test management is a process
discipline that crosses every layer and belongs to none, so no source carried it
in. The skill's own honest scope note — "Manual QA process, test-case management,
and formal QA-team workflow are out of scope"
([skill.yaml:19-23](../../skills/testing-strategy/skill.yaml)) — shows the boundary
being drawn, but flaky-test policy is a *technical* gating decision, not QA
process, and it fell outside anyway.

**Recommended correction.** Prefer extending `testing-strategy` over authoring a
new skill (QR-1 — no unnecessary abstraction). Add:

- an activation condition: *"An existing suite contains known-unreliable tests
  and a decision is needed about how they are gated"*;
- a decision-framework step: *"For each unreliable test — is it unreliable because
  of the test (fix or isolate it), because of the environment (stabilize the
  environment), or because of the system under test (that is a real defect, not
  flakiness)? Until it is fixed, the options are bounded retry (masks a real
  intermittent defect), quarantine out of the required set (keeps the signal,
  loses the gate), or delete (loses both). Name which, and record it."*;
- an anti-pattern: *"Treating a flaky test as a scheduling problem. A test that
  fails 10% of the time is either testing something genuinely intermittent — a
  real finding — or is badly written. Retrying it converts a signal into
  silence."*;
- a `related_skills` edge to `SK-INFRA-002` so the gating half has an owner to
  hand off to.

State honestly in the skill that this guidance is `grounding:
engineering-convention` rather than official-docs, matching how
`git-workflow` handles its own un-researched-plumbing boundary
([git-workflow/SKILL.md:18-26](../../skills/git-workflow/SKILL.md)).

**Regression test requirement.** Covered by `S19` as a `critical` assertion that
`testing-strategy` activates on the flaky-suite signal and produces a named policy
per test, not a blanket retry. Per `regression-suite.md` trigger 1, changing
`testing-strategy`'s activation conditions requires re-running every scenario that
names it — S05, S06, S09, S12, S13, S14 by inspection.

---

### C-1 · The signal scan and the convention record cannot see `FLAKY_TESTS.md` — **High**

**Finding.** Phase 0's five signal categories
([routing-algorithm.md:13-19](../../core/routing-architecture/routing-algorithm.md))
and CS-6's bound ([rules.md:64-65](../../core/routing-architecture/rules.md)) do
not reach a root-level policy document. ST-5's convention record
([lifecycle.md:101-105](../../core/orchestrator/lifecycle.md)) enumerates
"commit/branch style, comment style, lint/format config, test framework and
layout, directory conventions" — a documented decision to tolerate three flaky
tests is a convention in substance and is in none of those categories.

The library already reads *some* root markdown for conventions —
`git-conventions`' `repo-history-and-config` input names
"`CONTRIBUTING`/`CLAUDE.md` guidance"
([git-conventions/skill.yaml:45](../../skills/git-conventions/skill.yaml)) — so the
mechanism exists; it is scoped to commit-message conventions only. This is the
same class as **P-2** in
[`performance-dashboard-regression.md`](performance-dashboard-regression.md),
where the decisive signal (the recent commit) was likewise outside the scan. Two
of three tasks in this evaluation turn on a fact the bounded scan is structurally
unable to see.

**Root cause.** The signal taxonomy was designed to answer "which technologies are
present," because that is what SR-3's detection-gating needs. "What has this team
already decided" is a second question the taxonomy was never extended to cover,
even though the same cheap deterministic reads (CS-8) would serve it.

**Recommended correction.** Extend the Phase 0 category list and ST-5's
enumeration with a sixth, deliberately bounded category: *root-level and
`docs/`-level engineering-policy documents (`CONTRIBUTING`, `CLAUDE.md`,
`AGENTS.md`, `ARCHITECTURE`, `ADR`s, and any root document whose filename names a
known engineering concern — `FLAKY_TESTS`, `SECURITY`, `DEPRECATIONS`,
`RELEASE_PROCESS`). Read titles and headings, not full contents; load the body
only when a selected skill's `required_context` names it.* That keeps CS-6's
"detection, not comprehension" discipline intact while making a documented team
decision visible to routing.

**Regression test requirement.** Covered by `S19` with a `critical` assertion that
the routing record's `signals` includes the flaky-test policy document. No
existing scenario asserts anything about policy-document detection; S02 is the
only scenario that mentions `CONTRIBUTING.md`/`CLAUDE.md` and does so to state
their **absence** for commit-convention purposes.

---

### C-3 · SR-5 and the routing examples disagree about whether `testing-strategy` activates for CI work — **Medium**

**Finding.** SR-5 states the condition as production of runnable code —
"`testing-strategy` only when runnable code is produced"
([rules.md:26-27](../../core/routing-architecture/rules.md)), restated verbatim in
the decision tree ([routing-algorithm.md:136](../../core/routing-architecture/routing-algorithm.md)),
in `skill-router`'s decision framework step 7
([SKILL.md:91-94](../../skills/skill-router/SKILL.md)), and in the routing
README's operating principles. A CI workflow YAML is configuration, not runnable
application code, so the strict reading excludes `testing-strategy`.

Example 7 in the same subsystem includes it: "`ci-cd-pipeline` → `github-actions`
(SK-TECH), **composing `testing-strategy` (what to gate on)**"
([examples.md:193-194](../../core/routing-architecture/examples.md)).
`ci-cd-pipeline`'s own Testing section agrees with the example — "this skill
designs that gating structure; the actual test strategy being gated is owned by
testing-strategy" ([SKILL.md:186-191](../../skills/ci-cd-pipeline/SKILL.md)) — and
`related_skills` carries the `SK-QA-001` edge
([skill.yaml:62](../../skills/ci-cd-pipeline/skill.yaml)).

The router therefore has two contradictory normative statements about the same
decision, in the same subsystem. On this task the resolution matters: under the
strict SR-5 reading, the one skill that could own the flaky-test question is
excluded before the question is even asked.

**Root cause.** SR-5 compresses four distinct cross-cutting triggers into one
line, and the `testing-strategy` clause was written for the dominant case
(authoring code → author tests). "Deciding what an existing suite is gated on" is
a second, legitimate trigger that the compression dropped — it is present in the
skill's own `activation_conditions[1]` and `[3]`
([skill.yaml:34,37](../../skills/testing-strategy/skill.yaml)) but not in the rule
the router applies.

**Recommended correction.** Amend SR-5's clause to: *"`testing-strategy` when
runnable code is produced, **or when a decision is being made about what an
existing suite is gated on or which of its checks are trusted**."* Propagate to
the decision tree, `skill-router`'s step 7, and the routing README, so all four
statements agree with Example 7 and with the skill's own metadata.

**Regression test requirement.** Covered by `S19` as a `major` activation
assertion. Per `regression-suite.md` trigger 3, a change to
`core/routing-architecture/rules.md` should trigger a re-read of every scenario
whose expected activation set includes or excludes `testing-strategy` on SR-5
grounds — S01 and S10 are the ones where SR-5's exclusion half is load-bearing.

---

### C-2 · A merge gate is admitted as a one-file reversible write — **Medium**

**Finding.** D3 classifies risk from "the most dangerous action this task implies"
([lifecycle.md:89-90](../../core/orchestrator/lifecycle.md)) — here, writing a YAML
file. D13 then declines to require plan confirmation, correctly per its own text,
because this is "bounded `reversible-write` work of small complexity"
([lifecycle.md:198-201](../../core/orchestrator/lifecycle.md)). But the artifact
being created is a **standing gate every future merge must clear**, and the
required-check configuration that makes "runs before every merge" true is a
repository governance setting, not a file in the working tree — it is not
reversible by `git revert`.

This is the same action-vs-policy blind spot documented as **G-9** in
[`git-conflicting-conventions.md`](git-conflicting-conventions.md), reached from a
different domain. In Task 2 it lets a force-push exemption through ungated; here
it lets an unconfirmed merge gate through. The recurrence across two unrelated
domains is what makes it structural rather than incidental.

**Root cause.** Same as G-9: the risk taxonomy classifies the *mutation* and has
no vocabulary for the *authorization surface* a mutation creates.

**Recommended correction.** The G-POLICY gate class and GA-9 invariant proposed in
**G-9** cover this case directly — a required-status-check configuration is a
durable rule that gates future actions on behalf of humans. Additionally extend
D13's confirmation triggers with: *"the plan creates or changes a standing policy
that will gate, block, or authorize future human actions."* Proportionality is
preserved: this is one confirmation on a policy artifact, not a checklist on a
one-line edit.

**Regression test requirement.** Covered by `S19` as a `major` assertion that the
run surfaces the required-check configuration as a separate, confirmable decision
rather than folding it silently into the workflow file. Cross-referenced with
Task 2's `S18`, which tests the same gate class from the destructive side.

---

## What the library gets right on this task

Substantial, and worth stating precisely because the findings above are all about
*policy* while the library's *technical* content here is the strongest of the
three tasks:

- **The platform boundary is handled properly.** `github-actions`'
  `non_activation_conditions[0]` routes a platform-agnostic request to the parent
  ([skill.yaml:40](../../skills/github-actions/skill.yaml)); its `required_context`
  is "Whether the target platform is confirmed to be GitHub Actions"
  ([skill.yaml:52-53](../../skills/github-actions/skill.yaml)); its
  `failure_handling[0]` says "If it's unclear whether the platform is GitHub
  Actions vs. undecided, **ask** or route to the parent rather than assuming"
  ([skill.yaml:177](../../skills/github-actions/skill.yaml)). A compliant run asks
  which CI platform. **The library does prompt for clarification here — just on
  the platform, not on the policy.** Which shows the mechanism works when the
  ambiguity is represented in a skill's metadata; C-6 is about a question that has
  no such representation.
- **Honest scope on platform coverage.** `ci-cd-pipeline` states plainly that
  GitHub Actions is the only researched implementation and that the generic/
  technology pair are "closely paired… rather than covering meaningfully different
  platforms" ([skill.yaml:15-22](../../skills/ci-cd-pipeline/skill.yaml)). A team
  on GitLab CI gets told the truth rather than improvised guidance.
- **Honest capability posture.** Tier A with an explicit comment that "this
  library's capability map found no ecosystem that drives GitHub Actions natively
  — actual workflow execution is external"
  ([github-actions/skill.yaml:71-74](../../skills/github-actions/skill.yaml),
  echoed at [ci-cd-pipeline/SKILL.md:24-28](../../skills/ci-cd-pipeline/SKILL.md)).
  IC-3's no-silent-substitution rule is satisfied by construction.
- **The security content is the best of the three tasks by a wide margin.** OIDC
  over static long-lived keys as the *default posture* rather than an opt-in
  hardening step; per-job least-privilege `GITHUB_TOKEN` with read-only default;
  third-party actions pinned to full-length commit SHAs rather than mutable tags;
  and a genuinely non-obvious finding — that log redaction does exact-string
  matching, so treating a structured JSON/YAML blob as a single secret leaves its
  derived values unmasked
  ([SKILL.md:40-50](../../skills/ci-cd-pipeline/SKILL.md)). Plus the
  `pull_request_target` cache-poisoning and `::set-output::` log-injection
  mechanics in the technology skill. A team following this gets a materially
  better-hardened pipeline than most hand-written ones.
- **Realistic operational limits.** Cache eviction at 7 days, the per-repository
  10GB cap with LRU, and the observation that a cache falling outside those bounds
  "degrades to uncached performance without an obvious error"
  ([SKILL.md:72-79](../../skills/ci-cd-pipeline/SKILL.md)) — the kind of detail
  that distinguishes researched guidance from generated boilerplate.
- **Clean skill boundaries.** `husky` → CI design routes to `ci-cd-pipeline`;
  `deployment-release` → pipeline definition routes to `ci-cd-pipeline`;
  `github-actions` explicitly refuses to restate the parent's OIDC/token/matrix/
  caching principles (QR-2, `evaluation_criteria[3]`,
  [github-actions/skill.yaml:192](../../skills/github-actions/skill.yaml)). The
  non-activation network does real work here.

---

## Dimension scoring

| # | Dimension | Score | Basis |
|---|---|---|---|
| 1 | Skill routing | 3 / 5 | `ci-cd-pipeline` activates correctly and the parent/child platform boundary is handled well; but `requirements-engineering` is excluded by three independent gates (C-5) and `testing-strategy`'s inclusion is governed by two contradictory rules (C-3) |
| 2 | Dependency activation | 4 / 5 | `parents: [SK-INFRA-002]` correctly orders generic-before-specific; `husky` and `deployment-release` correctly route away; the `ci-cd-pipeline ⟷ testing-strategy` edge exists in `related_skills` but is not enforced by any rule the router applies |
| 3 | Context efficiency | 3 / 5 | Small, proportionate, well-bounded — but the one file that determines the answer is outside the scan (C-1), which is efficiency achieved by not looking |
| 4 | Implementation quality | 2 / 5 | A technically excellent pipeline implementing a policy nobody chose; ~27% spurious merge-failure rate, scored `complete` by the skill's own criteria (C-6) |
| 5 | Security | 5 / 5 | The strongest dimension across all three tasks: OIDC default posture, per-job least privilege, SHA pinning, the structured-blob redaction insight, `pull_request_target` cache-poisoning. Genuinely better than most hand-written pipelines |
| 6 | Testing | 2 / 5 | `testing-strategy` may not activate at all (C-3); no skill owns flaky-test policy (C-4); T-Gate 1 asks whether the *plan's* code is verifiable, never whether the *gate* is trustworthy |
| 7 | Maintainability | 3 / 5 | Cache-limit realism and reusable-workflow structure are good; a gate that fails one merge in four is the definition of unmaintainable and nothing in the library flags it |
| 8 | Error handling | 3 / 5 | `failure_handling` correctly covers missing commands and an existing pipeline; the honest "execution is external" posture is exactly right; nothing covers an unspecified policy, and `required_context` is satisfiable without confronting it |
| 9 | Repository convention adherence | 2 / 5 | `FLAKY_TESTS.md` is a documented team decision — a convention in substance — and ST-5's convention record cannot represent it (C-1). The run would overwrite a deliberate team choice without knowing one existed |
| 10 | Final outcome | 2 / 5 | The team gets a well-hardened pipeline that blocks roughly a quarter of their merges for reasons they had already decided not to fix, with no question asked |

**Task verdict: `partial`.** The technical content — especially security — is
excellent and would genuinely serve a team well. The library silently answers the
one question that decides whether the deliverable helps or hurts, and its own
verification criterion certifies the wrong answer.
