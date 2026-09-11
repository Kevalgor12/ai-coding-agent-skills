# Dependency Architecture

Status: **design only**. Defines how the library's skills relate, compose,
sequence, and gate each other. Builds on the [taxonomy](../taxonomy/) (the 69
skills, layers, execution tiers A/B/C) and the [skill specification](../skill-specification/)
(the `depends_on_skills` / `conflicts_with` / `related_skills` /
`required_capabilities` / `escalation` fields). It authors no skill content.

## Files

- **README.md** (this file) — the relationship-type vocabulary and the
  execution-semantics model that everything else uses.
- **[dependency-graph.md](dependency-graph.md)** — the layered composition graph:
  prerequisites, parents/children, complementary/conflicting/fallback/review/escalation edges.
- **[matrices.md](matrices.md)** — the activation, conflict, parallelization, and
  escalation matrices.
- **[workflows.md](workflows.md)** — the ten workflow patterns, each annotated
  with sequencing, parallelism, conditionals, iteration, review loops, and
  human-approval gates.

## Relationship-type vocabulary

Eight edge types connect skills. They are **directional** unless noted. Every
edge traces to a field in the [skill specification](../skill-specification/specification.md#25-composition-dependencies--conflicts)
or the taxonomy.

| Edge | Meaning | Spec source |
|---|---|---|
| **prerequisite** (A ⇐ B) | B's output must exist before A can meaningfully run (a *temporal* ordering, not just composition). E.g. `solution-architecture ⇐ requirements-engineering`. | derived from `required_context` + workflow order |
| **parent — specialization** (Tech → L3) | A Layer-4 technology skill specializes a Layer-3 generic parent (supplies concrete detail for its method). E.g. `postgresql → data-modeling`. | `parents` |
| **parent — composition** (A → B) | A invokes B as a sub-step during its own work. E.g. `refactoring → testing-strategy`. | `depends_on_skills` |
| **child** | Inverse of either parent edge. | inverse |
| **complementary** (A — B) | Frequently co-activated and mutually reinforcing; no hard ordering. E.g. `code-commenting — code-quality`. Symmetric. | `related_skills` |
| **conflicting** (A ⊥ B) | Must not co-activate *for the same decision* (mutual exclusion). E.g. `prisma ⊥ drizzle`. Symmetric. | `conflicts_with` |
| **fallback** (A ⤳ B) | If A cannot execute (capability missing / choice unavailable / step fails), route to B. E.g. `playwright ⤳ advisory-only`. | `capability_fallbacks`, `failure_handling` |
| **review** (R ⇒ T) | Review skill R evaluates the output of target skill T. E.g. `code-review ⇒ (any build skill)`. | taxonomy review facet |
| **escalation** (A ↑ X) | When A hits a gate it defers to X — a human (approval) or another skill. E.g. `data-migration ↑ human` (destructive), `code-review ↑ security-engineering` (security finding). | `escalation` |

Two invariants from the taxonomy hold for the composition graph:

- **Acyclic** — composition/prerequisite edges never form a cycle.
- **Layer-monotone** — a skill composes only same-or-lower layers (Layer 0 may
  invoke anything; a Layer-4 skill never invokes Layer 0–3 orchestration). This
  is what keeps the graph a DAG and is enforced by validation rule VR-4.

## Execution-semantics model

Every skill activation and every edge carries one or more execution semantics.
The brief's six determinations map to these; each is defined once here and used
throughout the matrices and workflows.

| Semantic | Notation | Definition | Who decides at runtime |
|---|---|---|---|
| **Sequential** | `A → B` | B starts only after A completes; a prerequisite or a same-file write dependency forces it. | `workflow-composer` (SK-ORCH-003) |
| **Parallel** | `A ∥ B` | Independent — no data dependency and no shared mutable target — so they may run concurrently (incl. as sub-agents where the host supports it). | `workflow-composer`, subject to `capability-adapter` |
| **Conditional** | `[cond] A` | A activates only when a condition holds (technology present, trust boundary exists, public site, populated DB…). | `skill-router` (SK-ORCH-001) via activation/non-activation |
| **Iteration** | `⟳ A` | A repeats until a stated criterion is met (root cause found, perf budget met, tests green). | the skill's own loop + composer |
| **Review loop** | `A ⤾ R` | build → review → fix → re-review until the review is clean. | `workflow-composer` + review skills |
| **Human approval** | `⛔ A` | A must not execute without explicit user confirmation (destructive, outward-facing, or production-affecting). Enforced by the safety rules, not overridable by a skill. | the runtime + user |

**Capability barrier.** `capability-adapter` (SK-ORCH-002) is a **barrier**
before any Tier B/C skill: it resolves abstract `required_capabilities` against
the host and picks execute / degrade-to-advisory / fallback / refuse *before* the
skill acts. No Tier B/C skill runs "blind." This is the single mechanism that
keeps a workflow portable across the eight target agents whose execution
capabilities the research found non-uniform.

## How to read the rest

- The **dependency graph** gives structure (who depends on / reviews / conflicts with whom).
- The **matrices** give the lookup tables (is this pair parallel-safe? conflicting? what escalates where?).
- The **workflows** give the runtime shapes (the ordered, gated compositions for the ten canonical task types).

All three are consistent projections of the same underlying edge set.
