---
name: Technical planning
description: >-
  Break an agreed approach into an ordered, dependency-aware task plan with a
  verification point per step and risk flags on uncertain steps. Use for
  multi-step implementation or when a plan is requested. Not for a
  single-step change, not for issue/milestone tracking (project-management),
  and not for sequencing which skills a coding agent activates (that's
  runtime orchestration, not engineering planning).
spec_version: "1.0"
---

## Purpose & scope

Take an agreed approach and break it into an ordered sequence of engineering
steps — real dependencies respected, a way to verify each step, and the
uncertain steps flagged honestly rather than presented with false confidence.

**Two things this is explicitly not**, because both are easy to confuse it
with:

- **Not project tracking.** Turning steps into issues/milestones and tracking
  status over the life of an effort is
  [project-management](../project-management/SKILL.md)'s job. This skill
  produces the plan; that skill (optionally) tracks its execution.
- **Not skill orchestration.** This library's runtime orchestration layer
  includes a `workflow-composer` skill that sequences *which library skills
  activate when* during a task. That is a meta-concern about the skill system
  itself. This skill plans *the engineering work* — the steps a human or agent
  would actually execute (write this migration, then this endpoint, then this
  test) — regardless of which skills end up doing each step.

## When to use / When not to use

**Use** when an agreed approach needs more than one ordered step, or the user
explicitly asks for a plan/breakdown. **Do not use** for a single-step change
with no real ordering decision, for tracking work over time (route to
project-management), or when the host agent already has its own native
planning/plan-mode tool active for this task — defer to it rather than
producing a second, competing plan.

## Knowledge

A good plan makes **two things explicit that are easy to leave implicit**:
real dependencies (what genuinely can't start before something else finishes)
and genuine uncertainty (what might not go as expected). Confusing "the order
I happen to be thinking about this in" with "the order dependencies require"
produces plans that look ordered but aren't actually constrained correctly —
and steps presented with uniform confidence hide the ones actually worth
worrying about.

**Dependency vs. convenience ordering.** A step is a true dependency of
another only if the second cannot be meaningfully started (not just
"logically follows") before the first completes. Many steps that feel
sequential are actually independent and could run in parallel if capacity
allows — see [dependency-architecture/matrices.md](../../core/dependency-architecture/matrices.md#parallelization-matrix)
for the general parallel-safety rules this planning should respect (no shared
mutable target, no data dependency).

**Verification points aren't an afterthought.** Every build step should have
a stated way to know it worked — a test that should pass, a manual check, a
specific behavior to observe — decided *when the step is planned*, not
retrofitted after. A step with no verification point is a step whose
completion is a guess.

**Risk flags are honesty, not hedging.** A step is risk-flagged when its
outcome or approach is genuinely uncertain (a new integration, an unfamiliar
API, a step that depends on an assumption not yet confirmed) — not
reflexively applied to everything to avoid being wrong. Over-flagging is as
unhelpful as under-flagging: it drowns the signal.

More sequencing heuristics are in
[references/planning-heuristics.md](references/planning-heuristics.md).

## Decision framework

1. **Is there a real dependency, or just a natural narrative order?** Only
   true dependencies force sequencing; everything else is a candidate for
   parallel execution or reordering by convenience/risk.
2. **Should risky steps go first or last?** Front-load a step whose failure
   would invalidate the rest of the plan (de-risk early); defer a step that's
   risky but isolated, so its uncertainty doesn't block unrelated work.
3. **Is the plan itself worth the planning cost?** For a small multi-step
   task, a short ordered list is enough — building a heavily annotated plan
   for three obvious steps is over-planning (see Anti-patterns). Scale
   planning depth to the task's real complexity and risk, the same
   proportionality principle requirements-engineering applies to elicitation.
4. **Can an unresolvable unknown be planned around, or does it need a spike?**
   If more planning can't reduce the uncertainty (only doing the work can),
   say so and flag the step as needing an exploratory spike rather than
   pretending a more detailed plan would resolve it.

## Workflow

1. Confirm the approach being planned is actually agreed (if not, hand off to
   solution-architecture — planning against an unsettled design produces a
   plan that has to be redone).
2. List the concrete steps the approach implies.
3. Identify true dependencies between steps; everything else is unordered
   relative to each other (a candidate for parallel execution, see
   dependency-architecture matrices).
4. Order by dependency first, then by risk-front-loading where it helps.
5. Attach a verification point to every build step.
6. Flag genuinely uncertain steps explicitly, and note the smallest thing that
   would resolve the uncertainty (a spike, a question, a check).
7. Present the plan as ordered steps with dependencies, verification points,
   and risk flags — not as prose narrating what you're about to do.

## Engineering rules

- Never order a step after another unless a real dependency requires it.
- Attach a verification point to every build step; a step without one isn't finished planning.
- Flag genuine uncertainty; don't inflate confidence to look decisive, and
  don't hedge everything to avoid being wrong.
- Keep the plan proportional to the task — a three-step change gets a short list, not a project charter.
- Defer to the host agent's own native plan/task tooling when it's already active for this task; don't produce a competing artifact.

## Trade-offs

More granular plans surface risk and dependency earlier but cost time to
produce and can go stale the moment reality diverges from the plan. Coarser
plans are cheaper and more robust to change but can hide a real dependency
until it causes rework. Match granularity to how much the task's outcome
depends on getting the order right.

## Anti-patterns

- **Planning depth disproportionate to the task** — a heavily-staged plan for
  three obvious, independent steps. This is the domain's overengineering trap.
- **Convenience ordering presented as dependency ordering** — sequencing
  steps that could run in parallel just because they were thought of in that
  order, silently forfeiting real parallel-execution opportunities.
- **Uniform-confidence plans** — no step flagged as risky when several
  clearly are, because flagging feels like admitting doubt.
- **A plan with no verification points** — steps whose "done" is just "I did the thing."
- **Duplicating the host agent's native planning tool** instead of deferring to it.

## Failure handling

- If the approach isn't actually agreed yet, hand off to solution-architecture
  rather than planning against an assumption that might not hold.
- If a step's uncertainty can only be resolved by doing it, say so plainly and
  mark it for a spike rather than manufacturing false planning precision.

## Escalation

- A step whose risk is high enough that a wrong turn would be expensive (a
  schema change, a change to a public interface) is surfaced for explicit
  acknowledgment before work starts on it — not discovered mid-implementation.

## Outputs & verification

- **Outputs:** an ordered task plan with explicit dependencies, a
  verification point per build step, and risk flags on uncertain steps.
- **Verify:** no step depends on one ordered after it; every build step has a
  verification point; risk flags land on the steps a reviewer would
  independently consider uncertain.

## References

- [references/planning-heuristics.md](references/planning-heuristics.md) — Tier-2 sequencing/risk-flagging heuristics.
- [core/dependency-architecture/matrices.md](../../core/dependency-architecture/matrices.md) — the library's parallelization/escalation matrices this plan's ordering should respect.
