---
name: Requirements engineering
description: >-
  Elicit and structure requirements from an ambiguous or high-stakes request:
  explicit asks, implicit constraints, non-functional requirements, and
  acceptance criteria. Use when scoping a new feature/system or when a request
  is under-specified. Not for requests that are already explicit, or for
  choosing how to build something (that's solution-architecture).
spec_version: "1.0"
---

## Purpose & scope

Turn a request into requirements a competent engineer could implement without
having to guess intent — explicit asks, the constraints implied but not
stated, and acceptance criteria a reviewer can actually check. This skill
produces *what is needed and why*, never *how to build it* (that's
[solution-architecture](../solution-architecture/SKILL.md)) and never *the
order of work* (that's [technical-planning](../technical-planning/SKILL.md)).

## When to use / When not to use

**Use** when a request is under-specified, could reasonably be read more than
one way, scopes a new feature/system from a short description, or carries an
unstated constraint (an audience, a scale, a compliance regime, an
environment). **Do not use** when the requirement is already explicit and
narrow (a one-line bug fix with an obvious fix), or when the actual open
question is *how* to build something the requirement already nails down —
that is a solution-architecture question, not this one.

## Knowledge

A requirement states a **need**; it must not smuggle in a **solution**.
"Use Redis for the session store" is a design decision wearing a requirement's
clothes — the real requirement underneath is usually "session lookups must be
fast enough to not bottleneck login" or "sessions must survive an app-server
restart." Separating the two matters: if the disguised solution is wrong or
becomes unavailable, the actual need is still on record and can be re-solved.
When a request names a technology, ask what need it's satisfying and record
both — the need as the requirement, the named technology as a stated
preference/constraint for solution-architecture to weigh.

**Functional vs. non-functional.** Functional requirements describe what the
system does; non-functional requirements describe the qualities it must have
while doing it (latency, availability, security posture, compliance,
accessibility, observability, cost ceiling, deployment environment). Most
under-specification failures are non-functional gaps, not functional ones —
people describe the feature and forget to say it needs to handle 10,000
concurrent users, or that it touches regulated data. Always check, at minimum:

- **Scale/performance** — expected load, latency budget, data volume.
- **Security/compliance** — auth requirements, data sensitivity, regulatory
  regime (GDPR/HIPAA/PCI/etc.), audit needs. *(This skill elicits these as
  requirements; it does not design the mitigations — that's
  [security-engineering](../../core/taxonomy/skill-catalog.md).)*
- **Availability/reliability** — acceptable downtime, disaster-recovery expectations.
- **Accessibility/i18n** — target standard (e.g. WCAG level), locales/languages.
- **Deployment environment** — target infrastructure, network constraints
  (air-gapped, on-prem, existing cluster), release cadence expectations.
- **Observability** — what "working correctly in production" needs to be verifiable as.

The full elicitation checklist with prompting questions per category is in
[references/nonfunctional-requirements-checklist.md](references/nonfunctional-requirements-checklist.md)
— consult it for a request whose non-functional shape is unclear; don't
re-derive it from scratch each time.

**Acceptance criteria** must be independently verifiable: a reviewer with no
access to your reasoning could mark each one pass/fail. "Should be fast" is
not a criterion; "p95 response time under 200ms at 500 req/s" is. Where the
user hasn't given you a number, either ask for one or state the assumed
threshold explicitly as an open question — never bake in a made-up number as
if it were given.

## Decision framework

Elicitation depth is itself a judgment call — over-eliciting a small task is
its own form of overengineering (the anti-pattern below), under-eliciting a
high-stakes one causes expensive rework downstream.

1. **How reversible is a wrong interpretation?** Cheap-to-undo (a copy tweak, a
   local dev script) → proceed on the most reasonable reading, note the
   assumption, don't block. Expensive-to-undo (a schema shape, a public API
   contract, a compliance-relevant flow) → resolve the ambiguity before any
   design work starts.
2. **How many reasonable readings are there?** One dominant reading with minor
   variants → state the reading and proceed. Genuinely multiple plausible
   readings that lead to materially different systems → this is a blocking
   question, not a footnote.
3. **Does the gap live in functional or non-functional territory?** Missing
   non-functional constraints are the more common and more expensive gap
   (§Knowledge) — always run the checklist even when the functional ask seems clear.
4. **Is what looks like a requirement actually a solution?** If so, extract the
   underlying need, record the stated preference separately, and let
   solution-architecture weigh it rather than treating it as fixed.

## Workflow

1. Restate the goal in your own words — if you can't, the ambiguity is real, not imagined.
2. Extract the explicit asks as a functional-requirements list.
3. Run the non-functional checklist (§Knowledge / references) against the
   request and any known context; record what's stated, infer what's strongly
   implied, and mark the rest as an open question rather than guessing.
4. Separate any solution-shaped statements from the need underneath them.
5. Draft acceptance criteria per requirement — each independently verifiable.
6. Mark requirements MUST / SHOULD / explicitly out-of-scope. An unbounded
   "and it would be nice if…" list is scope creep in disguise.
7. Surface open questions explicitly rather than silently resolving them; flag
   anything with a legal/compliance shape for the user's attention specifically.

## Engineering rules

- Never invent scope beyond what was requested or an assumption you've stated out loud.
- Ask a small number of high-leverage questions, not an exhaustive
  questionnaire — a senior engineer's clarifying questions are the ones that
  actually change the design, not every conceivable one.
- Write every acceptance criterion so a reviewer can check it without asking you what you meant.
- Capture non-functional constraints even when unasked — they are frequently
  the ones a requester forgot to mention and the architecture most needs.
- Keep the requirement and the solution in separate columns, always.

## Trade-offs

Thorough elicitation reduces downstream rework and mis-scoped implementation,
but it costs real time and the requester's patience — and a long
clarification round on a low-stakes task is itself a cost. Calibrate depth to
the reversibility and stakes of getting it wrong (§Decision framework), not to
a fixed process.

## Anti-patterns

- **Over-eliciting a trivial task** — running the full non-functional
  checklist on a one-line copy change. This *is* the overengineering trap for
  this skill: treat elicitation depth as proportional, not automatic.
- **Unverifiable acceptance criteria** — "should be fast," "should be
  secure," "should be user-friendly" with no threshold or check attached.
- **Solution-shaped requirements** — a named technology or pattern presented
  as if it were the actual constraint, foreclosing solution-architecture's job.
- **Silent scope invention** — adding capabilities the requester didn't ask
  for because they "seemed useful."
- **Silently resolving a genuine ambiguity** instead of surfacing it as an
  open question — this looks efficient but hides the risk instead of managing it.

## Failure handling

- If the requester is unavailable to resolve a blocking ambiguity, state the
  assumption explicitly and proceed on the narrowest reasonable
  interpretation, rather than stalling indefinitely or guessing broadly.
- If a new requirement conflicts with an existing constraint on record, surface
  the conflict explicitly; do not silently pick a side.

## Escalation

- Any requirement carrying a legal/compliance implication (data residency,
  accessibility law, data retention/deletion obligations, licensing) is
  flagged to the user directly — this skill does not assume how to resolve it.

## Outputs & verification

- **Outputs:** structured functional + non-functional requirements,
  independently verifiable acceptance criteria, and an explicit open-questions list.
- **Verify:** every acceptance criterion is checkable without further
  interpretation; no requirement is actually a disguised solution; no scope
  was invented; every material ambiguity is either resolved-and-stated or
  raised as an open question — never silently absorbed.

## References

- [references/nonfunctional-requirements-checklist.md](references/nonfunctional-requirements-checklist.md) — Tier-2 elicitation checklist by category.
- [core/taxonomy/skill-catalog.md](../../core/taxonomy/skill-catalog.md) — this skill's taxonomy entry (SK-DISC-001) and its neighbors.
