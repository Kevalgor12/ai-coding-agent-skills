# Routing Algorithm & Activation Decision Tree

The ordered procedure the `skill-router` runs, then the decision tree form. Both
express the same logic; the algorithm is the reference, the tree is the
follow-along. All selection uses **Tier-0 metadata only** (no skill bodies).

## Algorithm

### Phase 0 — Intake & signal extraction (cheap, read-only)

- Parse the request: verbs (fix/build/add/optimize/review…), named artifacts
  (a file, a query, a page), named technologies, explicit constraints.
- Scan **bounded** repo signals — not the whole tree:
  - dependency manifests (`package.json`, `go.mod`, `requirements.txt`, …),
  - config files (`tsconfig`, `next.config`, `drizzle.config`, `.github/workflows/`, `Dockerfile`),
  - connection strings / driver imports (`postgres://`, `pg`, `psycopg`, `mongoose`),
  - file types present (`.tsx`, `.sql`, `.vue`, `.go`),
  - existing conventions (git log, commitlint config).
- Produce a **signal set**. Prefer deterministic signals over semantic search (CS-8).

### Phase 1 — Classify (intent, task type, complexity, risk)

- **Intent** from request verbs/shape → {fix, build, debug, refactor, optimize,
  secure, migrate, modernize, document, review, explain, plan}.
- **Task type** = the [workflow pattern](../dependency-architecture/workflows.md)
  that intent maps to, or `simple` (single-step) / `question` (no change).
- **Complexity** ∈ {trivial, small, multi-step, project} from scope of change +
  number of domains touched.
- **Risk** ∈ {read-only, reversible-write, destructive, outward-facing,
  production} from the most dangerous action the task implies.
- **Policy-authorizing requests classify at the class they would bypass, not at
  the mechanical action of writing the policy.** A request to establish a
  standing rule, config, or exception that lets a *future* action skip a gate
  (a branch-protection exemption enabling force-push, an always-allow list for
  a destructive command, a CI setting that lets a merge bypass a check) is
  classified at the risk level of the gate class it authorizes bypassing —
  `destructive`/`outward-facing`/`production` as appropriate — not at
  `reversible-write`, which is what editing a config file would be on its own.
  This is the fix for a documented failure mode: a request combining two
  individually-reasonable instructions ("strict branch protection" +
  "force-push exemption for hotfixes") previously classified as an ordinary
  `reversible-write` config change, so it never reached D13 admission, gate
  declaration, or FV-9 — the contradiction shipped as a working ruleset with a
  bypass actor, having passed every check because every check was keyed to the
  wrong risk value. Fixing the input classification here is sufficient; D13,
  gate declaration, and FV-9 all key off this value and need no separate patch.

**Early exits:**
- `question` (pure explanation, no change) → activate only the relevant
  knowledge skill(s) at advisory tier; **no** build/test/git/convention skills. Stop.
- `trivial` single-owner task → activate the one owning skill (+ conventions if it
  writes code); skip discovery and the composer. Stop after ordering.

### Phase 2 — Detect scope (domains + technologies)

- Map signals → **domains** in play (frontend? backend? data? realtime? infra?
  growth? AI?).
- Map signals → **specific technologies** present/named (only these are
  detection-eligible for Layer-4 activation).
- **Resolve conflict clusters** now: if `prisma` is detected, `drizzle`/`typeorm`
  are out; if `postgres`, `mysql` is out; etc. If a cluster is *needed but
  undetected* (a choice must be made), do not activate all siblings — flag a
  **decision** for `solution-architecture` / the user (SR-4).

### Phase 3 — Select the minimum set (default-deny)

For every skill, evaluate against the signal set using Tier-0 only:

```
include(s) :=
      matches(s.activation_conditions, signals)
  AND NOT matches(s.non_activation_conditions, signals)
  AND needed_for(task_type, s)          # staffed against the workflow skeleton
```

Then:
- **Technology skills:** include only detected/named techs (SR-3).
- **Cross-cutting (conditional):** include `security-engineering` only if a trust
  boundary/secret/untrusted input is present; `performance-engineering` only if a
  perf concern; `testing-strategy` only if runnable code is produced;
  `observability` only if production diagnosability (SR-5).
- **Conventions:** attach `code-commenting`/`code-quality` if writing code;
  `git-conventions`/`git-workflow` if committing/branching — not for pure
  analysis (SR-6).
- **Discovery:** engage `requirements`/`architecture`/`planning` proportional to
  complexity+risk (SR-8) — not for a one-line fix.
- **Orchestration:** add `capability-adapter` iff any selected skill is Tier B/C;
  add `workflow-composer` iff multi-stage; router self-suppresses if the final
  set is a single skill (SR-7).
- **Everything else is EXCLUDED**, and the router records *why* (the
  "unnecessary skills" determination) — this is the explicit complement, not a
  silent omission.

**Completeness backstop (SR-10):** re-walk the chosen workflow's required stages;
if a stage has no skill staffing it, add the missing essential skill. Correctness
beats economy here.

### Phase 4 — Order & parallelize

- Impose **prerequisite** edges (sequential): discovery chain, data-modeling →
  orm/migration, build → review, ci → deploy.
- Insert the **capability-adapter barrier** before any Tier B/C step.
- Mark **parallel-safe** sets (review facets; disjoint-module builds; read-only
  analyses; disjoint fan-out) per the [parallelization matrix](../dependency-architecture/matrices.md#parallelization-matrix).
- Insert **review loops** (`⤾`) after build stages and **approval gates** (`⛔`)
  at destructive/outward-facing/production steps.

### Phase 5 — Select context (lazy)

- Keep routing on descriptions (done). For each *selected* skill about to run:
  load its body; ensure `required_context` present (else failure-handling);
  load `optional_context` only if cheaply at hand; do **not** pre-load Tier-2
  references (CS-1..CS-6). Don't reload context already in the conversation.

### Phase 6 — Emit the routing plan

Output: **selected** skills (ordered, parallel-annotated) · **excluded** skills
(with reason) · **context** to load · **review** facets · **escalation** gates
(surfaced up front so the user knows which steps need approval).

---

## Activation decision tree

```
START
│
├─ Is it a pure question / explanation (no change requested)?
│     └─ YES → activate relevant knowledge skill(s) only, advisory tier.
│              NO build / test / git / convention / orchestration skills.  ─▶ END
│
├─ Extract signals (Phase 0).
│
├─ Classify intent → task type → complexity → risk (Phase 1).
│
├─ Is it a trivial single-owner change?
│     └─ YES → activate the one owning skill (+ conventions if it writes code).
│              Skip discovery + composer.                                   ─▶ ORDER ─▶ END
│
├─ Detect domains + technologies; resolve conflict clusters (Phase 2).
│
├─ For each skill (Tier-0 only):
│     ├─ non_activation matches?              → EXCLUDE (record reason)
│     ├─ activation matches AND needed_for(task_type)?  → candidate INCLUDE
│     └─ else                                 → EXCLUDE (default-deny, record reason)
│
├─ Technology skill for a tech NOT detected/named?  → EXCLUDE
│
├─ Cross-cutting:
│     ├─ trust boundary / secret / untrusted input?   → +security-engineering
│     ├─ perf concern / budget?                        → +performance-engineering
│     ├─ produces runnable code?                       → +testing-strategy
│     └─ production diagnosability?                     → +observability
│
├─ Writing code?      → +code-commenting +code-quality
├─ Committing/branch? → +git-conventions (+git-workflow if ops/PR)
│
├─ Complexity ≥ multi-step OR risk ≥ destructive?
│     └─ YES → engage discovery (requirements/architecture/planning as fit)
│              + workflow-composer
│
├─ Any selected skill Tier B or C?  → +capability-adapter (barrier)
│
├─ Completeness backstop: every required workflow stage staffed?
│     └─ NO → add the missing essential skill(s)
│
├─ Order (prerequisites) · parallelize (matrix) · insert ⤾ review · ⛔ gates
│
└─ Select context lazily · emit routing plan  ─▶ END
```

The tree is intentionally **exclusion-heavy**: most branches remove skills. That
shape is what produces the minimum set — the default is *out*, and a skill has to
earn its way *in*.
