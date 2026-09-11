# core

Agent-agnostic foundations that every skill and adapter depends on. This is the
contract layer of the library — it does not contain any skill content itself.

Contains:

| Directory | Contents |
|---|---|
| [`taxonomy/`](taxonomy/) | Domain/layer taxonomy, skill catalog (all 88 skills), taxonomy-analysis |
| [`skill-specification/`](skill-specification/) | Universal skill schema (VR-1–VR-9), adapter projection rules, authoring examples |
| [`dependency-architecture/`](dependency-architecture/) | Dependency graph, edge types (composition vs. related), workflow patterns, dependency matrices |
| [`routing-architecture/`](routing-architecture/) | Routing algorithm, activation/non-activation rules, routing examples |
| [`orchestrator/`](orchestrator/) | Master orchestrator — lifecycle, state/contract, security/validation, failure recovery, self-review, observability |

Nothing in this directory is specific to one target agent or one skill's
subject matter. Agent-specific content belongs in `adapters/`; skill content
belongs in `skills/`.
