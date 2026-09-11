# Routing Rules

The rule sets the router applies in [algorithm](routing-algorithm.md) Phases 3–6.
These are the normative decision rules; the algorithm is how they're sequenced.

---

## Skill-selection rules

- **SR-1 · Default-deny.** A skill is excluded unless its activation matches *and*
  the task type needs it. Keyword overlap alone never includes a skill.
- **SR-2 · Non-activation is decisive.** If a skill's non-activation conditions
  match the signals, exclude it — even if its activation also matches. (This is
  the rule that keeps `technical-documentation` out of "fix this query": its
  non-activation names "route in-code work elsewhere".)
- **SR-3 · Technology skills are detection-gated.** Never activate a `SK-TECH-*`
  skill for a technology absent from the repo and unnamed in the request. Presence
  = a manifest entry, a driver import, a config file, a connection string, a file
  type, or an explicit mention.
- **SR-4 · Conflict resolution before selection.** Within a
  [conflict cluster](../dependency-architecture/matrices.md#conflict-matrix),
  include only the sibling actually in use. If a choice is *required but
  undetected*, include the generic Layer-3 skill and raise the choice as a
  decision (→ `solution-architecture` / user); do **not** activate every sibling.
- **SR-5 · Cross-cutting is conditional.** `security-engineering` only on a trust
  boundary/secret/untrusted input; `performance-engineering` only on a perf
  concern/budget; `testing-strategy` only when runnable code is produced;
  `observability` only for production diagnosability. None are "always on."
- **SR-6 · Conventions attach to actions, not analysis.** `code-commenting` /
  `code-quality` engage when code is written/edited; `git-conventions` /
  `git-workflow` when committing/branching. A pure read/analysis task gets none.
- **SR-7 · Orchestration minimalism.** `capability-adapter` only if a Tier B/C
  skill is selected; `workflow-composer` only if multi-stage; the router
  self-suppresses when the final set is a single skill (no meta-overhead on
  trivial work).
- **SR-8 · Discovery proportional to complexity + risk.** `requirements` /
  `solution-architecture` / `technical-planning` engage for new, multi-domain, or
  high-risk work — not for a bounded single-file change.
- **SR-9 · Prefer generic unless specifics matter.** For an engine-agnostic task,
  the Layer-3 skill suffices; add the Layer-4 technology skill only when
  version/engine-specific detail is actually needed.
- **SR-10 · Completeness backstop.** After minimizing, verify every required
  stage of the chosen workflow is staffed; add any missing essential skill.
  Under-activation is a correctness bug and overrides economy.
- **SR-11 · Record exclusions.** The excluded set (the "unnecessary skills"
  determination) is produced explicitly with a one-line reason per exclusion
  class — never a silent omission. This is what makes routing auditable.

---

## Context-selection rules

- **CS-1 · Route on Tier-0 only.** Selection uses `name` + `description` +
  activation/non-activation. Never load a skill body to decide whether to select it.
- **CS-2 · Load bodies on activation.** A selected skill's body loads when its
  stage runs, not at routing time.
- **CS-3 · Required context or fail gracefully.** If a skill's `required_context`
  is absent, trigger its failure-handling (ask, or degrade to advisory) rather
  than proceeding blind.
- **CS-4 · Optional context only if cheap.** Load `optional_context` when it's
  already in hand or one bounded read away; don't chase it.
- **CS-5 · Tier-2 on demand.** `references/`, `examples/`, `scripts/`, `assets/`
  load only when a running skill body links to them — never pre-loaded.
- **CS-6 · Bounded signal scan.** The repo scan reads manifests/config/entrypoints,
  not the whole tree; it's for detection, not comprehension.
- **CS-7 · No reloading.** Context already in the conversation is not re-read.
- **CS-8 · Cheap signals first.** Prefer deterministic detection (file existence,
  manifest keys, connection-string patterns) over semantic/RAG search — which
  half the target agents don't even have (capability map §9).

---

## Parallelization rules

Applied in Phase 4; the lookup is the
[parallelization matrix](../dependency-architecture/matrices.md#parallelization-matrix).

- **PR-1 · Serialize prerequisites and same-target writes.** Any prerequisite
  edge, or two skills editing the same file/artifact, forces sequential order.
- **PR-2 · Parallelize the independent.** Review facets, disjoint-module builds,
  read-only analyses, and disjoint fan-out (same op over disjoint files) are
  parallel-safe.
- **PR-3 · Adapter is a barrier.** `capability-adapter` runs before any Tier B/C
  step; nothing parallel crosses that barrier.
- **PR-4 · Parallelism is an optimization, never a correctness requirement.** The
  composer *offers* parallelism; the adapter degrades it to sequential where the
  host lacks sub-agents. A workflow must produce the same result either way.
- **PR-5 · Respect host limits.** Cap parallel breadth to the host's known
  nesting/concurrency (Cursor ~1 level, Claude Code 3 deep / 20 wide, Antigravity
  10) — surfaced by the adapter. When unknown, prefer sequential.

---

## Escalation rules

Applied in Phase 6; the lookup is the
[escalation matrix](../dependency-architecture/matrices.md#escalation-matrix).

- **ER-1 · Surface gates up front.** The routing plan names every approval gate
  the task will hit *before* work starts, so the user isn't surprised mid-run.
- **ER-2 · Risk drives gating.** `destructive` (data loss, history rewrite),
  `outward-facing` (PR post, external send, disclosure), and `production` (deploy/
  release, secret rotation) actions require explicit human approval — a hard stop,
  non-overridable by any skill (safety-rules contract).
- **ER-3 · Missing capability → fallback, not failure.** A required Tier B/C
  capability the host lacks routes through `capability-adapter` to a documented
  fallback (advisory, MCP bridge, shell-wrapped CLI) — the task degrades, it
  doesn't error out.
- **ER-4 · Ambiguity escalates before building.** If intent or requirements are
  genuinely ambiguous on a non-trivial/high-stakes task, escalate to
  `requirements-engineering` / the user *before* selecting build skills — don't
  guess a direction and implement it.
- **ER-5 · Cross-skill handoffs.** Apply the escalation matrix's skill-to-skill
  edges: a security finding in review → `security-engineering`; a bug found while
  refactoring → `code-review`/`bug-fixing` (never a silent fix); a root cause
  found while debugging → `bug-fixing`; an engine-agnostic problem in a tech skill
  → its Layer-3 parent.
- **ER-6 · Review requirements follow the selected set.** Which review facets
  apply is derived from what was built: any authored code → quality + comment
  facets; a trust-boundary change → security facet; a hot-path/budget change →
  performance facet. `code-review` aggregates them; the facets run in parallel
  (PR-2).

---

## How the rules deliver the two named examples

- **"Fix this PostgreSQL query"** → SR-1/SR-2 exclude every skill whose
  activation doesn't match a data/query task; SR-3 keeps out all undetected
  technologies (no React/Three.js/WebRTC signals present); SR-5 admits
  `performance-engineering` only because it's a query-optimization concern; SR-6
  admits no git/doc skills for a pure analysis+edit. Result: a tight set
  (`postgresql` + `database-operations`/`performance-engineering`, advisory/Tier-B).
- **"Build a realtime multiplayer browser game"** → Phase 2 detects the frontend +
  realtime + backend + data domains; SR-8 engages discovery (project complexity);
  SR-3 activates only the detected/named techs (Three.js, a realtime transport);
  SR-5 admits security + performance (multiplayer trust + latency); SR-10's
  backstop ensures no required stage is unstaffed. Result: the broad correct
  composition — without ever pulling in SEO, AdSense, or ORM/search skills the
  task doesn't imply.

Full traces in [examples.md](examples.md).
