---
name: Solution architecture
description: >-
  Decompose a system into components, identify cross-cutting concerns, and
  choose a technology approach with explicit trade-offs — using the technology
  decision matrix as the source of truth for alternatives. Use for a new
  system/feature of non-trivial size or an open significant technology
  choice. Not for elaborating already-fixed architecture, or for the
  technology-specific how-to once a choice is made (route to the matching
  Layer-3/Layer-4 skill).
spec_version: "1.0"
---

## Purpose & scope

Turn requirements into a system shape: components, boundaries, data flow, and
the technology choices that satisfy the stated constraints — with the
trade-offs recorded, not just the winner. This skill decides *what to build
and with what*; it does not decide *in what order to build it*
([technical-planning](../technical-planning/SKILL.md)) and it does not carry
the technology-specific facts once a choice is made (the matching Layer-3/
Layer-4 skill owns that).

## When to use / When not to use

**Use** for a new system or non-trivial feature that needs a component
structure, or when a real technology decision is open (a database, a
framework, an API paradigm, a realtime transport). **Do not use** when the
architecture and stack are already fixed and the task is implementation
within them, or when requirements for a non-trivial system haven't been
gathered yet — get [requirements-engineering](../requirements-engineering/SKILL.md)
first; architecting against assumptions instead of stated needs is how
requirement gaps turn into expensive rework.

## Knowledge

**This skill's grounding is different from a technology skill's.** It does
not itself carry official-docs citations for framework APIs — that's owned by
each Layer-4 technology skill. Its source of truth is this library's own
research synthesis: the
[Technology Decision Matrix](../../research/knowledge-maps/technology-decision-matrix.md)
(head-to-head comparisons for genuine "pick one" decision points, with
citations back to the underlying official docs), the
[Integration Map](../../research/knowledge-maps/integration-map.md) (which
technologies are documented to work together and how), the
[Technology Knowledge Map](../../research/knowledge-maps/technology-knowledge-map.md)
(the dependency/complement/conflict graph across the 44 researched
technologies), and the
[Agent Capability Map](../../research/knowledge-maps/agent-capability-map.md)
(what execution capabilities are actually portable across the coding-agent
ecosystems this library targets — relevant when the architecture itself will
be built/operated by an agent). Consult these before asserting a trade-off
from memory; where they're silent on a comparison, say so rather than
presenting an unresearched guess as a documented conclusion.

**Decomposition is about boundaries, not layers-for-their-own-sake.** A
component boundary should track a real seam — a different team, a different
scaling profile, a different data-consistency need, a different deployment
cadence. Splitting a system into services because "microservices are how it's
done" without one of those seams is the domain's overengineering trap (see
Anti-patterns).

**Cross-cutting concerns are easy to miss because no single component owns
them.** Identify early, even before their owning skill designs them in depth:
auth/authz boundary, caching layer, observability (how will this be debugged
in production), and how the system fails (see Trade-offs). This skill flags
where these concerns attach; the deep design is
[authentication-authorization](../../core/taxonomy/skill-catalog.md),
[caching-strategy](../../core/taxonomy/skill-catalog.md),
[security-engineering](../../core/taxonomy/skill-catalog.md), and
[observability](../../core/taxonomy/skill-catalog.md) respectively.

More architecture patterns and their trade-off shapes are in
[references/architecture-patterns-and-tradeoffs.md](references/architecture-patterns-and-tradeoffs.md).

## Decision framework

1. **Start from the simplest shape that satisfies the requirements.** A
   modular monolith beats a distributed system until a specific requirement
   (independent scaling, independent deployment, a hard team boundary)
   actually demands the split — the split has a real operational cost.
2. **For each open technology decision, check the decision matrix first.**
   If the category is covered, use its comparison as the starting trade-off
   set rather than re-deriving it from general knowledge. If it isn't
   covered, reason explicitly and say the comparison isn't research-backed.
3. **Check the integration/technology maps before combining choices.** A
   combination the research flags as conflicting or "not typically paired"
   needs a stated reason to proceed, not silent adoption.
4. **Weigh reversibility, not just fit.** A choice that's cheap to change
   later (a UI library) deserves less deliberation than one that's expensive
   to change (a primary datastore, a public API shape, a core language) —
   spend the judgment budget where it matters.
5. **Account for who's building it.** If a coding agent will implement and
   operate parts of this, check the
   [Agent Capability Map](../../research/knowledge-maps/agent-capability-map.md)
   for capability gaps (e.g. no native browser automation, no first-class
   container primitive) before assuming an execution path exists.
6. **State the trade-off, not just the pick.** "We chose X" without "because
   Y, at the cost of Z" is not a decision a future engineer can evaluate or revisit.

## Workflow

1. Confirm requirements are in hand; if not, stop and get them.
2. Propose a component/service decomposition at the simplest viable
   granularity for the stated requirements.
3. For each open technology decision, consult the decision matrix / knowledge
   maps, shortlist real alternatives, and record the trade-off — don't jump straight to a pick.
4. Check chosen combinations against the integration map / conflict data.
5. Identify cross-cutting concerns and where they attach in the decomposition.
6. Identify architectural failure modes (below) and how the shape handles or doesn't handle them.
7. Write up the architecture + choices + trade-offs + risks as the output.

## Engineering rules

- Never state "we chose X" without the alternatives considered and why they lost.
- Don't decompose further than a real seam justifies.
- Place cross-cutting concerns explicitly; don't leave them implicit and hope
  a later skill notices.
- Defer technology-specific implementation detail to the owning Layer-4 skill
  — this skill records *that* PostgreSQL was chosen and *why*, not how to write its migrations.
- When the research is silent on a comparison, say so rather than presenting
  an unresearched opinion as if it were sourced.

## Trade-offs

Every non-trivial architecture decision trades something for something:
monolith-vs-services trades operational simplicity for independent
scaling/deployment; a relational vs. document datastore trades query
flexibility for schema flexibility; synchronous vs. event-driven communication
trades simplicity/traceability for decoupling/resilience. State which side of
each trade-off the requirements actually justify — don't default to either
extreme out of habit.

## Anti-patterns

- **Distributing a system before a real seam demands it** — this is this
  domain's overengineering trap. Team size, deployment need, and scaling
  profile are real seams; "it's more scalable in theory" alone is not.
- **Premature abstraction** — building a plugin system, a generic
  configuration layer, or an abstraction over a single current use case
  "in case we need it later." Add the abstraction when a second real case
  appears, not preemptively.
- **Silent default technology bias** — picking a familiar stack without
  checking it against the actual requirements and the decision matrix,
  then presenting it as the only reasonable choice.
- **Ignoring a documented conflict/inappropriate combination** without stating why the exception is justified here.
- **Skipping cross-cutting concerns** until implementation surfaces them as a scramble.

## Security

Identify where auth/authz, secrets, and trust boundaries attach in the
decomposition, and flag data-sensitivity implications of the storage/transport
choices — this shapes the architecture (e.g., where a boundary needs to sit).
The threat-modeling and mitigation depth belongs to
[security-engineering](../../core/taxonomy/skill-catalog.md); this skill does
not re-derive it, only ensures the shape has a place for it.

## Performance

Identify where the requirements imply a real performance constraint (a
latency budget, a throughput target, a data-volume growth curve) and let that
inform decomposition/technology choice (e.g., whether a cache layer or an
OLAP-shaped store belongs in the architecture at all) — deep performance
method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

An architecture should be shaped so its pieces are independently testable —
flag where a proposed boundary would make testing harder (e.g., a
tightly-coupled synchronous chain with no seam for mocking). Test-strategy
depth is owned by [testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If requirements are missing or too thin for a real decision, stop and
  request them (or hand off) rather than architecting against assumptions.
- If the decision matrix / knowledge maps don't cover a needed comparison,
  say so explicitly rather than presenting an unsourced guess as researched.

## Escalation

- A choice that's expensive or slow to reverse (primary datastore, core
  framework, public API paradigm) is presented with trade-offs for explicit
  user confirmation before being treated as decided.
- A requirement gap or contradiction discovered while architecting is
  escalated to requirements-engineering / the user, not silently resolved.

## Outputs & verification

- **Outputs:** a component/data-flow description; a technology choice per
  open decision point with recorded trade-offs and alternatives considered;
  identified cross-cutting concerns and architectural risks/failure modes.
- **Verify:** every requirement is covered by some part of the architecture;
  the decision matrix's documented trade-offs are recorded for each relevant
  choice, not just the winner; no flagged-conflicting combination was chosen
  without a stated reason.

## References

- [references/architecture-patterns-and-tradeoffs.md](references/architecture-patterns-and-tradeoffs.md) — Tier-2 pattern catalog.
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
- [research/knowledge-maps/integration-map.md](../../research/knowledge-maps/integration-map.md)
- [research/knowledge-maps/technology-knowledge-map.md](../../research/knowledge-maps/technology-knowledge-map.md)
- [research/knowledge-maps/agent-capability-map.md](../../research/knowledge-maps/agent-capability-map.md)
