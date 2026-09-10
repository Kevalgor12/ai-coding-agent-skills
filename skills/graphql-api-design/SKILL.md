---
name: GraphQL API design
description: >-
  Design GraphQL schemas and resolvers — types, N+1-safe resolver structure,
  cursor pagination, field-level authorization, schema evolution, and
  production-readiness (introspection, query-cost limits). Use when building
  or extending a GraphQL API. Not for REST design or the REST-vs-GraphQL
  paradigm decision itself (api-design owns that).
spec_version: "1.0"
---

## Purpose & scope

Design a GraphQL schema and its resolvers correctly, once GraphQL is the
chosen paradigm. The REST-vs-GraphQL decision itself belongs to
[api-design](../api-design/SKILL.md) — this skill starts from "GraphQL is
the answer" and owns everything from there: type modeling, N+1-safe
resolvers, pagination, field-level authorization, schema evolution, and
production-readiness posture.

## When to use / When not to use

**Use** when building or extending a GraphQL API, or when a schema/resolver
has a specific N+1, pagination, or authorization design question. **Do not
use** while REST vs. GraphQL is still an open decision (that's api-design),
for REST design itself, or for service structure with no GraphQL-specific question.

## Knowledge

**GraphQL's biggest documented risk is that a single endpoint can express
wildly varying query cost.** Unlike REST, where each URL has roughly bounded
cost, one GraphQL endpoint can serve a cheap query or a deeply nested,
alias-heavy, batched query that costs orders of magnitude more — this is
called out explicitly in GraphQL's own security documentation, not an
inferred risk [Source: technology-decision-matrix.md §7]. **Traditional
fixed-window rate limiting is explicitly called insufficient** for this,
since request *count* can't distinguish cheap from expensive query shapes.
The documented mitigations are: enforce max query depth, apply stricter
limits to nested list fields, cap top-level fields/aliases per request, and
cap batched operations per request.

**N+1 is the single most common documented GraphQL performance issue**,
arising directly from the per-field resolver execution model — each field
resolver can independently trigger a data fetch, so a naive resolver for a
list of parents each fetching their own children issues one query per
parent. DataLoader-style batching (collect requested IDs across a tick,
issue one batched fetch) is the standard, documented fix [Source:
technology-decision-matrix.md §7]. This is not optional for any
nested-relationship field — treat it as a required pattern, not an
optimization to add later.

**Introspection is a real production-posture decision, not a default to
leave alone.** Disabling introspection in production is common practice, but
many developer tools depend on it — the documented recommendation is
selective disabling via trusted-document allowlisting rather than a blanket
toggle [Source: technology-decision-matrix.md §7].

**Caching needs deliberate design; it doesn't fall out for free the way REST's
does.** Persisted queries (send a hash instead of full query text) enable
HTTP/CDN caching of what would otherwise be uncacheable POST requests;
multi-layer caching (resolver-level, HTTP/CDN, schema-build, a store like
Redis) is the documented pattern for `graphql-js` deployments [Source:
technology-decision-matrix.md §7].

**Testing has a real, documented gap.** No official GraphQL testing
methodology guide could be located during this project's research — the
closest official page 404'd [Source: technology-decision-matrix.md §7]. Don't
assume first-party testing guidance exists the way it might for a REST
framework; the closest documented pattern is calling the generic
`graphql({schema, source, rootValue})` function directly from a test runner.

## Decision framework

1. **Does every nested-relationship resolver batch?** If a resolver fetches
   per-item inside a loop, it needs a DataLoader-style batching layer before
   it ships — this isn't a judgment call, it's a correctness requirement for
   any non-trivial schema.
2. **Offset/limit or cursor pagination?** Cursor-based pagination is the
   documented, standard idiom for GraphQL connections; use it by default for
   list fields, and only use offset/limit where there's a specific stated
   reason (e.g., a UI that genuinely needs jump-to-page).
3. **Does a field expose data not every caller should see?** Apply
   field-level authorization there specifically — GraphQL's single-endpoint
   model makes it easy to forget that different fields on the same type may
   need different access rules.
4. **What's the production introspection/query-cost posture?** For a public
   or externally-exposed API, apply depth/complexity limits and consider
   introspection restriction; for an internal-only API behind other access
   controls, the calculus may differ — state which case applies rather than
   defaulting silently.
5. **Schema evolution, not versioning.** Add new fields/types rather than
   breaking existing ones; deprecate with `@deprecated` rather than removing outright.

## Workflow

1. Confirm GraphQL is the settled paradigm (hand off to api-design if not).
2. Model types from the domain model.
3. Design resolvers with batching for every nested relationship.
4. Apply cursor pagination to list fields.
5. Apply field-level authorization where required.
6. Decide and state the production introspection/query-cost posture.
7. Plan schema evolution via additive changes and `@deprecated`, not breaking removals.

## Engineering rules

- Every nested-relationship resolver batches; no per-item-in-a-loop fetching.
- List fields use cursor pagination unless a specific reason says otherwise.
- Field-level authorization is applied wherever a field's visibility differs from its type's default.
- Evolve the schema additively; don't remove/rename fields without a deprecation period.
- Never rely on fixed-window rate limiting alone as a cost-control measure.

## Trade-offs

Field-level authorization and per-resolver batching add real implementation
overhead compared to REST's simpler per-endpoint model, in exchange for the
client-driven query flexibility GraphQL exists to provide. Persisted-query
caching recovers some of REST's free HTTP-caching behavior but requires
deliberate setup, not just adopting GraphQL.

## Anti-patterns

- **Unbatched nested resolvers** — the classic, most common GraphQL
  performance bug, and this domain's most important thing to get right.
- **Relying on fixed-window rate limiting as the only cost control** — explicitly documented as insufficient for GraphQL's variable-cost queries.
- **Leaving introspection and query-cost limits at their defaults for a
  public-facing schema** without a deliberate decision.
- **Removing or renaming a field outright** instead of deprecating it — breaks existing consumers without warning.
- **Building a fully generic, config-driven resolver framework** before more than one resolver pattern is actually needed — the domain's overengineering trap.

## Security

The single-endpoint, variable-cost query model is GraphQL's defining risk —
apply max query depth, nested-list limits, and per-request field/alias/batch
caps; do not rely on request-count rate limiting alone [Source:
technology-decision-matrix.md §7]. Apply field-level authorization
deliberately, since GraphQL has no formal security-scheme object the way
OpenAPI does. Deep threat modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

N+1 avoidance via DataLoader-style batching is the dominant lever. Persisted
queries plus multi-layer caching (resolver/HTTP-CDN/schema-build/store) is
the documented pattern for recovering cacheability that REST gets for free
[Source: technology-decision-matrix.md §7]. Deep performance method is owned
by [performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

State the real documented gap: no official GraphQL testing methodology guide
exists per this project's research; the closest pattern is invoking
`graphql({schema, source, rootValue})` directly from a test runner. Deep
test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If REST-vs-GraphQL hasn't actually been decided, hand off to api-design rather than assuming GraphQL.
- If production posture (introspection, query-cost limits) is unstated for a public API, ask rather than shipping unguarded defaults.

## Escalation

- Disabling introspection or adding query-cost limits to an already-public
  schema is a consumer-facing breaking change — surfaced for explicit
  confirmation before applying.

## Outputs & verification

- **Outputs:** a GraphQL schema/type design and N+1-safe resolver structure,
  with pagination and field-level authorization applied.
- **Verify:** nested resolvers batch; list fields use cursor pagination;
  field-level auth is present where needed.

## References

- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
