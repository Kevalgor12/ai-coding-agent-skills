# Routing & Activation Architecture

Status: **design only**. Defines the runtime behavior of the `skill-router`
(`SK-ORCH-001`) and its coordination with `capability-adapter` (`SK-ORCH-002`)
and `workflow-composer` (`SK-ORCH-003`). Builds on the [taxonomy](../taxonomy/),
[skill specification](../skill-specification/), and
[dependency architecture](../dependency-architecture/). It authors no skill.

## The job in one sentence

Given a request, **activate the minimum appropriate skill set** — every skill the
task genuinely needs, and *no others* — then order, parallelize, and gate them.

Two failure modes it must avoid, in tension:

- **Over-activation** (wastes context, mis-triggers): "Fix this PostgreSQL query"
  must not pull in frontend, SEO, UI/UX, Three.js, WebRTC, or documentation skills.
- **Under-activation** (incorrect/incomplete): "Build a realtime multiplayer
  browser game" must reach requirements, architecture, frontend, Three.js,
  realtime transport, backend, database, testing, security, and performance.

The router resolves the tension with a **default-deny** rule (exclude unless
there is a positive reason to include) plus a **completeness backstop** (verify
no essential stage of the chosen workflow is left unstaffed).

## Files

- **README.md** (this file) — the twelve determinations, the operating
  principles, and how routing stays context-efficient.
- **[routing-algorithm.md](routing-algorithm.md)** — the ordered algorithm and
  the activation decision tree.
- **[rules.md](rules.md)** — skill-selection, context-selection, parallelization,
  and escalation rules.
- **[examples.md](examples.md)** — realistic worked routings, including the two
  mandated examples with explicit exclusion reasoning.

## The twelve determinations the router makes

Each maps to a phase of the algorithm and reuses structures already defined.

| # | Determination | Derived from | Defined in |
|---|---|---|---|
| 1 | **User intent** | request parse (fix/build/debug/refactor/optimize/secure/migrate/modernize/document/review/explain/plan) | algorithm §1 |
| 2 | **Task type** | intent + signals → one of the 10 workflow patterns (or "simple/ad-hoc") | [workflows](../dependency-architecture/workflows.md) |
| 3 | **Complexity** | signals (trivial / small / multi-step / project) | algorithm §1 |
| 4 | **Technologies involved** | repo signals (manifests, config, imports, connection strings, file types) + named tech | algorithm §2 |
| 5 | **Risk level** | action class (read-only / reversible-write / destructive / outward-facing / production) | algorithm §1 |
| 6 | **Required skills** | default-deny selection over activation/non-activation, staffed against the workflow skeleton | [selection rules](rules.md#skill-selection-rules) |
| 7 | **Unnecessary skills** | the explicit complement — everything excluded, with reason | [selection rules](rules.md#skill-selection-rules) |
| 8 | **Execution order** | prerequisite edges + workflow order | [matrices](../dependency-architecture/matrices.md) |
| 9 | **Parallel opportunities** | parallelization matrix | [parallelization rules](rules.md#parallelization-rules) |
| 10 | **Required context** | each skill's `required_context`/`optional_context`, loaded lazily | [context rules](rules.md#context-selection-rules) |
| 11 | **Review requirements** | selected skills + risk → review facets | [escalation rules](rules.md#escalation-rules) |
| 12 | **Escalation requirements** | risk level + escalation matrix → approval gates | [escalation rules](rules.md#escalation-rules) |

## Operating principles

1. **Route on metadata, not bodies.** The router decides using only Tier-0
   (`name` + `description` + activation/non-activation) — it never loads a skill
   body to choose. This is the context-efficiency backbone: selection is cheap.
2. **Default-deny.** A skill is excluded unless its activation matches *and* the
   task type needs it. Loose keyword overlap is not enough.
3. **Non-activation is decisive.** If a skill's non-activation conditions match,
   it is excluded even if its activation also loosely matches.
4. **Detection-gated technology skills.** A technology skill never activates for a
   technology that is not present in the repo or named in the request.
5. **Proportional orchestration.** Router self-suppresses on single-skill tasks;
   the composer engages only for multi-stage work; the capability-adapter engages
   only when a Tier B/C skill is selected. Discovery (requirements/architecture/
   planning) scales with complexity and risk, not with every task.
6. **Lazy context.** Skill descriptions are always available; bodies load on
   activation; Tier-2 references load only when a running skill links to them.
7. **Correctness over economy at the margin.** When minimizing risks dropping an
   essential skill, the completeness backstop wins — under-activation is a
   correctness bug; a slightly larger set is only an efficiency cost.

These principles are what let the same router produce a tight 3-skill set for
"fix this query" and a correct 15-skill composition for "build a game," from one
mechanism.
