---
name: Technical documentation
description: >-
  Produce and maintain accurate prose documentation — READMEs, API docs,
  ADRs, inline module docs. Write docs matching current behavior, concise
  and non-duplicative, recording architectural decisions with rationale
  and alternatives, avoiding docs that will rot (prefer generating from
  source where possible). Use when the user asks for docs, a public
  interface changed, or a decision needs recording. Not for in-code
  comments or changelog drafting.
spec_version: "1.0"
---

## Purpose & scope

Produce and maintain human-readable documentation — READMEs, API docs,
ADRs, inline module docs — that matches current behavior and resists rot.
In-code comments belong to
[code-commenting](../code-commenting/SKILL.md); changelog/release-notes
drafting is already owned by
[project-management](../../core/taxonomy/skill-catalog.md) (authored in
the DISC-domain batch). Specialized by
[openapi-swagger](../openapi-swagger/SKILL.md) for OpenAPI-spec-as-
documentation authoring — an API description that also functions as its
own documentation artifact.

## When to use / When not to use

**Use** when the user asks for documentation, a public interface changed
and its docs need updating, or an architectural decision needs recording.
**Do not use** for in-code commenting, when the user explicitly wants code
only, or for changelog/release-notes drafting.

## Knowledge

**GitHub's own documented repository best practices name a specific,
concrete set of expected documentation artifacts, not just "have some
docs."** A README, LICENSE, CITATION file (where applicable), contribution
guidelines, and a SECURITY.md with vulnerability-reporting instructions
are the named baseline
[Source: docs.github.com/en/repositories/creating-and-managing-
repositories/best-practices-for-repositories]. **Skipping documentation
entirely is explicitly named as a documented anti-pattern**, grouped
alongside skipping security features (no Dependabot/secret-scanning/code-
scanning) — treated as a real, named repository-hygiene failure, not a
minor omission.

**Documentation that drifts from the code it describes is worse than no
documentation** — a stale doc actively misleads a reader who trusts it
over the actual current behavior. This is the same underlying principle
[code-commenting](../code-commenting/SKILL.md) applies to in-code
comments, extended to prose artifacts: the fix for drift risk is either
keeping the doc rigorously in sync, or generating it from source where
that's possible so drift becomes structurally impossible rather than a
discipline problem.

**Generating documentation from source, where a source of truth already
exists, structurally eliminates the drift problem rather than just
managing it.** An OpenAPI specification is the clearest instance of this
in this library's own research — the spec itself doubles as the API's
documentation artifact (consumed by Swagger UI/Editor/Codegen), so
keeping the spec accurate keeps the documentation accurate by
construction, rather than maintaining a separate hand-written description
that can silently diverge from the spec. Prefer this pattern wherever an
equivalent source of truth exists, rather than defaulting to hand-
maintained prose.

**An ADR (Architecture Decision Record) that captures only the outcome,
without the rationale and alternatives considered, loses most of its
future value.** The decision itself is often the least useful part of an
ADR months or years later — a future reader (including a future AI agent)
needs to know *why* that decision was made and *what else was
considered*, since that's the context that actually helps evaluate
whether the decision still holds as circumstances change.

## Decision framework

1. **Does a source of truth already exist that this documentation could
   be generated from** (an OpenAPI spec, a type definition, a schema)?
   If so, prefer generating from it over hand-maintained prose that can
   drift.
2. **Does this documentation match the code's actual current behavior**,
   or does it describe an aspirational/planned state? Write what's
   actually true now.
3. **Is this content already documented elsewhere?** If so, link to it
   rather than duplicating — duplicated docs are a second place for drift
   to happen.
4. **Is this an architectural decision that needs recording?** If so,
   capture the decision, its rationale, and the alternatives considered —
   not just the outcome.
5. **Did the user explicitly say they want code only?** If so, don't
   impose documentation uninvited.

## Workflow

1. Check whether a source of truth exists that documentation could be
   generated from instead of hand-written.
2. Write documentation matching the actual current behavior, checking
   against the code itself, not assumptions.
3. Check for existing coverage of the same content; link rather than
   duplicate.
4. For an architectural decision, capture decision + rationale +
   alternatives as a structured ADR.
5. Keep docs concise — say what's needed, not more.

## Engineering rules

- Prefer generating documentation from an existing source of truth over
  hand-maintained prose that can drift.
- Documentation must match actual current behavior, not an aspirational
  or planned state.
- Don't duplicate documentation that already exists elsewhere — link to
  it.
- An ADR captures decision + rationale + alternatives, not just the
  outcome.
- Don't impose documentation the user explicitly said they don't want.

## Trade-offs

Generating documentation from source eliminates drift risk but requires
the source of truth to actually exist and be expressive enough to serve
as documentation (an OpenAPI spec works well for this; many architectural
decisions have no equivalent structured source and need hand-written
prose). Hand-maintained prose is more flexible and can explain things a
generated artifact can't, at the ongoing cost of needing deliberate
upkeep to avoid drift.

## Anti-patterns

- **Skipping documentation entirely** — GitHub's own best-practices
  guidance names this as a real, documented anti-pattern, not a minor
  omission.
- **Writing documentation that describes aspirational behavior** rather
  than what the code actually currently does.
- **Duplicating documentation** that already exists elsewhere instead of
  linking to it.
- **An ADR that records only the outcome**, without the rationale or
  alternatives considered — loses most of its future value.
- **Hand-maintaining prose documentation for something that could instead
  be generated from an existing source of truth**, accepting drift risk
  unnecessarily.

## Security

A SECURITY.md with vulnerability-reporting instructions is a named,
expected documentation artifact per GitHub's own best-practices guidance
[Source: docs.github.com/en/repositories/creating-and-managing-
repositories/best-practices-for-repositories]. Documentation should never
embed secrets/credentials as examples without clearly marking them as
placeholders. Deep threat modeling is owned by
[security-engineering](../security-engineering/SKILL.md).

## Performance

Not applicable to this skill's scope.

## Testing

This skill's own correctness is verified by whether produced docs
actually match current behavior (see `skill.yaml`'s evaluation criteria)
rather than a runtime test suite. Where documentation is generated from
source (e.g. an OpenAPI spec), the generation pipeline itself may have
its own testing concerns owned by the relevant technology skill.

## Failure handling

- If the user explicitly wants code only with no docs, don't impose
  documentation uninvited.
- If existing docs already cover the topic accurately, update in place
  rather than duplicating.

## Escalation

None — this skill has no escalation path of its own beyond the standard
confirmation rules for any file the user hasn't explicitly asked to be
changed.

## Outputs & verification

- **Outputs:** documentation files/sections (README, API docs, ADRs,
  inline module docs) matching current behavior.
- **Verify:** docs match actual current behavior; no unnecessary
  duplication; ADRs capture decision + rationale + alternatives;
  generation-from-source is preferred where a source of truth exists.

## References

- [research/technologies/github.md](../../research/technologies/github.md) — recommended repository documentation practices.
