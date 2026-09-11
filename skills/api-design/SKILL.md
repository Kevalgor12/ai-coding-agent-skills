---
name: API design
description: >-
  Design REST/HTTP API contracts — resources, versioning, pagination, status/
  error semantics, idempotency — and decide REST vs. GraphQL when that choice
  is open. Use when designing or extending an HTTP API. Not for GraphQL
  schema design itself, spec-tooling mechanics, or the service's internal
  structure.
spec_version: "1.0"
---

## Purpose & scope

Design the HTTP/REST contract: resources, versioning, pagination, error/
status semantics, idempotency — and make the REST-vs-GraphQL call when it's
genuinely open. This skill owns REST contract design specifically;
[graphql-api-design](../graphql-api-design/SKILL.md) owns GraphQL schema
design once that paradigm is chosen, and
[openapi-swagger](../openapi-swagger/SKILL.md) owns the spec-tooling
mechanics (docs generation, codegen) once a contract exists.

## When to use / When not to use

**Use** when designing or extending an HTTP/REST API, or when REST vs.
GraphQL is an open decision. **Do not use** for GraphQL schema/resolver
design once GraphQL is chosen, for realtime/bidirectional transport design,
or for spec-tooling mechanics with no contract-design question.

## Knowledge

**OpenAPI's own FAQ states REST and GraphQL "solve similar problems in
slightly different ways"** [Source: technology-decision-matrix.md §7] — this
is not a strict superiority relationship, and the underlying research
explicitly does not support ranking one as universally better.

**Versioning is handled completely differently by design.** REST versions
implicitly via URL/path convention (`/v1`, `/v2`) — external to the spec
itself. GraphQL's documented alternative is schema evolution: adding fields/
types without breaking existing clients, avoiding versioning as a concept
entirely [Source: technology-decision-matrix.md §7]. If a system genuinely
needs many breaking contract changes over time with many external consumers,
this is a real point in GraphQL's favor worth weighing explicitly — not
something to default past.

**REST has a mature, well-defined security-scheme model; GraphQL does not.**
OpenAPI defines five formal security-scheme types (`apiKey`, `http`,
`mutualTLS`, `oauth2`, `openIdConnect`) under `components.securitySchemes`,
referenceable globally or per-operation [Source: technology-decision-matrix.md
§7]. GraphQL has no equivalent formal object — security relies on
transport-level TLS plus app-layer authorization. This isn't necessarily a
weakness of GraphQL, but it does mean REST's contract can *declare* its auth
requirements in a way tooling can introspect, where GraphQL's cannot.

**Testing/contract-verification is a real, documented gap for GraphQL that
REST doesn't share.** OpenAPI documents mock-server generation directly from
a spec as a primary use case, with CI-verification of implementation against
spec as a named best practice. GraphQL has **no official testing methodology
guide** — the closest official page (`graphql-js.org/docs/testing/`) 404'd
during this project's research [Source: technology-decision-matrix.md §7].
This is a real asymmetry worth knowing when choosing a paradigm for a
contract-testing-heavy environment.

Full REST/GraphQL comparison table (DoS exposure, caching strategy, spec
evolution) is in
[references/rest-vs-graphql.md](references/rest-vs-graphql.md).

## Decision framework

1. **Is the access pattern resource-oriented or graph-oriented?** Clients
   fetching whole resources by ID/collection → REST fits naturally. Clients
   needing to fetch deeply nested, client-specified shapes in one round-trip
   → GraphQL's model fits better.
2. **How much does the contract need to evolve, and how many consumers does
   it have?** Few consumers, infrequent breaking changes → REST's explicit
   versioning is simple and sufficient. Many consumers, frequent additive
   evolution → GraphQL's schema-evolution model avoids versioning overhead.
3. **Does the team need a formal, tooling-introspectable security-scheme
   declaration?** REST/OpenAPI has one; GraphQL doesn't — weigh this if
   API-gateway or auto-generated-client tooling depends on it.
4. **Standard HTTP caching, or need for computed/aggregated results?**
   REST's GET+cache-headers model is simple and battle-tested. GraphQL
   requires deliberate caching strategy (persisted queries, resolver-level
   caching) since POST-based queries aren't cacheable by default [Source:
   technology-decision-matrix.md §7].
5. **Within REST:** design resources around the domain model, choose a
   versioning strategy explicitly (don't leave it implicit), specify
   pagination for any unbounded list, and use idempotency keys for
   non-idempotent operations that might be retried.

## Workflow

1. Confirm the domain model is available (hand off to data-modeling if not).
2. If REST vs. GraphQL is open, apply the decision framework and record the trade-off.
3. Model resources/routes around the domain, with consistent naming.
4. Specify status codes and a consistent error-response shape.
5. Specify pagination for any list endpoint that can grow unbounded.
6. State the versioning strategy explicitly.
7. Specify idempotency handling for retryable non-idempotent operations.
8. Hand off spec/tooling mechanics to openapi-swagger.

## Engineering rules

- State the versioning strategy explicitly; never leave it implicit.
- Specify pagination for any endpoint whose result set can grow unbounded.
- Use consistent status codes and one error-response shape across the whole API.
- Don't default to REST or GraphQL out of habit when the choice is genuinely open and the trade-offs point the other way.

## Trade-offs

REST's per-resource simplicity and mature caching/security-scheme tooling
trade against potential over-fetching/under-fetching and the need to version
explicitly. GraphQL's flexible, client-specified queries and versionless
schema evolution trade against a documented, real DoS-exposure surface
(query cost varies per request shape) and thin official testing guidance.
Neither is free.

## Anti-patterns

- **Leaving versioning implicit** — no `/v1` convention and no plan for how a breaking change would be introduced.
- **Unbounded list endpoints with no pagination.**
- **Inconsistent error shapes across endpoints** — one route returns a string, another an object, another nothing.
- **Choosing GraphQL by default "for flexibility"** without a workload that actually needs client-specified query shapes — the domain's overengineering trap, given GraphQL's real DoS-mitigation and tooling overhead.
- **Treating REST's simplicity as automatically sufficient** for a system with many consumers making frequent, evolving, deeply-nested data requests.

## Security

REST/OpenAPI has a formal, five-type security-scheme model
(`apiKey`/`http`/`mutualTLS`/`oauth2`/`openIdConnect`) declarable per-operation
[Source: technology-decision-matrix.md §7] — use it to make auth requirements
introspectable by tooling, not just documented in prose. Deep auth mechanics
are owned by authentication-authorization; deep threat modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Standard HTTP caching (GET + cache headers) applies naturally to REST
resources with no extra design work. Deep performance method (indexing,
caching layers behind the API) is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

Mock servers generated directly from an OpenAPI description are a documented
primary use case, and wiring the description into CI to verify
implementation-matches-spec is a named best practice [Source:
technology-decision-matrix.md §7]. Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If the domain model isn't designed yet, hand off to data-modeling rather than guessing a resource shape.
- If consumer needs are unstated, ask rather than assuming public/multi-consumer scope.

## Escalation

- Choosing GraphQL over REST (or vice versa) for a system with many existing
  consumers is presented with trade-offs for explicit confirmation before
  being treated as decided.

## Outputs & verification

- **Outputs:** a REST API contract (resources, status/error semantics,
  pagination, versioning) and, when open, a REST-vs-GraphQL recommendation
  with trade-offs.
- **Verify:** consistent error shape and status codes; pagination specified
  where needed; versioning strategy explicit.

## References

- [references/rest-vs-graphql.md](references/rest-vs-graphql.md) — Tier-2 full comparison table.
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
