---
name: GraphQL
description: >-
  Implement GraphQL schemas and resolvers correctly — SDL types, resolver
  chains, N+1 prevention via DataLoader, subscriptions over WebSocket, schema
  evolution, typed codegen via GraphQL Code Generator, persisted queries, and
  production hardening (depth/cost limits, error masking). Use when the tech
  is GraphQL and the task is implementation, not for the REST-vs-GraphQL
  choice (graphql-api-design).
spec_version: "1.0"
---

## Purpose & scope

Implement GraphQL APIs correctly using the `graphql-js` reference implementation
and the GraphQL specification. Covers SDL schema authoring, resolver chains and
context threading, DataLoader-based N+1 prevention, authorization through the
context/business-logic layer, subscriptions over WebSocket, additive schema
evolution, typed client generation (GraphQL Code Generator), persisted queries
for caching, and production hardening. The REST-vs-GraphQL paradigm decision and
design-level concerns (type modeling, pagination shape, field-level authorization
design) belong to [graphql-api-design](../graphql-api-design/SKILL.md) —
this skill starts from "GraphQL and graphql-js are chosen" and owns the
implementation mechanics from there.

## When to use / When not to use

**Use** when implementing or extending a GraphQL schema or resolver in a project
that already has GraphQL in its stack (a `.graphql`/`.gql` file, `graphql-js`
in `package.json`, a codegen config). **Do not use** while REST vs. GraphQL is
still undecided (that's [api-design](../api-design/SKILL.md)), when the question
is schema design only without implementation detail (that's
[graphql-api-design](../graphql-api-design/SKILL.md)), or for non-GraphQL API work.

## Knowledge

**SDL type system.** Types are declared in SDL: `type`, `interface`, `union`,
`enum`, `input`, and `scalar` [Source: graphql.org/learn/schema/]. `!` marks
Non-Null; `[Type]` marks a List. Design fields nullable by default and reserve
Non-Null only where `null` is genuinely invalid — a nullable leaf lets the server
return partial data rather than failing the entire response when one downstream
dependency errors [Source: graphql.org/learn/schema-design/].

**Resolver execution model.** Each field has a resolver invoked with four arguments:
parent value, field arguments, shared context, and field-level execution info
[Source: graphql.org/learn/execution/]. Many implementations provide trivial
default resolvers (same-named property lookup on the parent object), so leaf
fields on simple value types need no explicit resolver [Source:
graphql.org/learn/execution/].

**Context threading.** A single context object created per request is passed to
every resolver; use it to carry request-scoped state — authenticated user/claims,
DataLoader instances, and service/database handles [Source:
graphql.org/learn/execution/]. Authorization decisions should delegate to the
business logic layer the context surfaces, not be re-implemented in individual
field resolvers [Source: graphql.org/learn/authorization/].

**N+1 prevention via DataLoader.** The per-field resolver model naturally produces
N+1: each nested-relationship resolver independently fetches child data, issuing
one backend call per parent-list item [Source: graphql.org/learn/performance/].
**DataLoader** coalesces IDs requested within the same event-loop tick into a
single batched call [Source: graphql.org/learn/performance/]. This is a required
pattern for nested-relationship fields — not an optional optimization.

**Subscriptions.** A `Subscription` root type supports long-lived real-time
operations; each subscription operation must have exactly one root field [Source:
graphql.org/learn/subscriptions/]. Transport is not spec-mandated — WebSocket
(via community subprotocols) is the common choice. The server must maintain
per-connection state for the subscription's lifetime, which complicates
horizontal scaling (each client binds to a specific server instance) [Source:
graphql.org/learn/subscriptions/].

**graphql-js v16 vs. v17.** As of June 2026, `graphql-js` v17 is the current
release. Key differences from v16 [Source:
www.graphql-js.org/upgrade-guides/v16-v17/]:
- Requires **Node.js 22/24/25/26+**, TypeScript typings target **TS 4.4+**.
- `execute()` may return synchronously or as a Promise — callers must handle
  both return shapes (v16 always returned a Promise).
- `GraphQLError` positional constructor removed; must use `(message, options)`.
- Development mode is no longer implicitly driven by `NODE_ENV` — must be
  enabled explicitly via package condition or `enableDevelopmentMode()`.

**Schema evolution.** Adding new types and new fields is non-breaking because
GraphQL responses include only requested fields [Source:
graphql.org/learn/schema-design/]. Deprecate with `@deprecated` before removing.
Prefer additive evolution; `/v1`/`/v2` URL versioning is a REST pattern and does
not apply to GraphQL.

**Testing gap.** No official `graphql-js` testing guide was located during this
library's research — `www.graphql-js.org/docs/testing/` returned HTTP 404
[Source: research/technologies/graphql.md §9]. The closest documented pattern is
invoking `graphql({ schema, source, rootValue })` directly from a test runner and
asserting on `{ data, errors }` [Source: www.graphql-js.org/docs/getting-started/].
Community tools (`@graphql-tools/mock`, graphql-inspector) are not independently
verified by this library's research — verify against current docs.

**Apollo Server / Apollo Client scope boundary.** This library's research
(`research/technologies/graphql.md`) covers `graphql-js` and the GraphQL
specification. Apollo Server wraps `graphql-js` behind an HTTP/transport layer;
Apollo Client handles client-side caching and state management. For Apollo-specific
API details (datasources, `InMemoryCache` normalization, response-cache directives,
Apollo Studio), verify against the official Apollo documentation — this skill does
not make Apollo-specific API claims beyond the cited research.

**GraphQL Code Generator.** A community tool (`@graphql-codegen/*`) that generates
typed TypeScript operation types, hooks, and fragment types from a schema and
`.graphql` operation files; configuration lives in `codegen.ts` or `codegen.yml`.
Not part of `graphql-js` — verify current plugin APIs against Code Generator's
official docs.

## Decision framework

1. **SDL (`buildSchema(sdlString)`) vs. programmatic (`new GraphQLObjectType(...)`)
   schema construction.** Use SDL for the overwhelming majority of schemas — it is
   the documented default and is more readable/toolable [Source:
   www.graphql-js.org/docs/getting-started/]. Use the programmatic API only for
   schemas that must be generated dynamically (e.g., from a database schema) or
   that require constructs that don't map cleanly onto SDL text [Source:
   www.graphql-js.org/docs/constructing-types/]. Mixed SDL + programmatic is an
   over-engineering trap unless a specific need drives it.

2. **graphql-js standalone vs. a server framework.** `graphql-js` is a library,
   not a server; real applications need an HTTP transport layer [Source:
   www.graphql-js.org/docs/getting-started/]. Choose a server framework (Apollo
   Server, Yoga, or an Express adapter) for convention-over-configuration HTTP
   transport, subscription support, and middleware integration — verify the chosen
   framework's current API against its official docs. Use `graphql-js` directly
   (e.g., calling `graphql()`) in tests and for tooling, regardless of which
   server framework is in production.

3. **Subscriptions or not.** Subscriptions add architectural complexity (per-connection
   state, pub/sub backend, scaling constraints) [Source:
   graphql.org/learn/subscriptions/]. For data that changes infrequently, polling
   (repeated queries on an interval) is simpler. Reserve subscriptions for
   incrementally-changing, high-frequency data where the push model justifies the
   added infrastructure — route scaling design to
   [realtime-communication](../realtime-communication/SKILL.md) (SK-BE-004).

4. **Introspection in production: on or off.** Disabling introspection reduces
   attack surface but breaks developer tooling (GraphiQL, codegen, IDE plugins)
   [Source: www.graphql-js.org/docs/going-to-production/]. The documented balance:
   use trusted-document allowlisting to disable unrestricted introspection while
   preserving it for known trusted clients.

## Workflow

1. Confirm the `graphql-js` (or Apollo Server) version from `package.json` before
   writing any resolver or schema code.
2. Author or update SDL types — nullable by default, Non-Null only where `null` is
   truly invalid; `input` types for mutation arguments.
3. For every nested-relationship field, create a DataLoader batch function scoped
   to the request context — no per-item fetches inside the resolver body.
4. Wire the authenticated user/claims into the per-request context object; route
   authorization decisions to the business logic layer the context exposes.
5. If subscriptions are needed, design the single-root-field subscription document
   and confirm the WebSocket transport and pub/sub backend.
6. Configure production hardening: max query depth, per-request field/alias/batch
   caps, query complexity analysis; decide introspection posture; wire error masking.
7. If a typed client is needed, set up GraphQL Code Generator against the schema
   and run codegen to produce TypeScript operation types.
8. Run at least one representative query via `graphql({ schema, source })` or schema
   introspection to confirm schema validity and resolver execution.

## Engineering rules

- Never issue a per-item backend call inside a nested-relationship resolver — always use a DataLoader or equivalent batch function scoped to the request context.
- Design fields nullable by default; apply `!` only where `null` is genuinely invalid and a null value would break the consumer.
- Thread authorization through context → business logic layer; do not re-implement access checks ad hoc in individual resolvers.
- Evolve schemas additively; deprecate with `@deprecated` before removing any field or type.
- Apply max query depth and/or complexity analysis for any externally reachable endpoint — fixed-window per-request rate limiting is documented as insufficient [Source: graphql.org/learn/security/].
- Check the `graphql-js` major version before using `execute()`, `GraphQLError`, or development-mode settings; v16 and v17 differ in all three.

## Anti-patterns

- **Per-item resolver fetches in a loop** — the canonical N+1 bug; creates unbounded backend load proportional to list size.
- **Authorization in individual resolvers** — duplicates logic, risks inconsistency across resolvers and entry points, and is explicitly called out as not recommended for production [Source: graphql.org/learn/authorization/].
- **Non-Null on every field by default** — removes partial-failure resilience; a single failed resolver propagates null up the entire parent chain instead of nulling only the affected field.
- **Rate limiting by request count alone** — documented as insufficient for GraphQL's variable per-query cost [Source: graphql.org/learn/security/].
- **Unbounded query depth or nested list fields without limits** — deeply nested list fields produce exponential response size relative to query size [Source: graphql.org/learn/security/].
- **Asserting Apollo-specific API behavior from this skill** — this skill's research covers `graphql-js` and the spec; Apollo-specific claims must be verified against Apollo's own documentation.

## Security

GraphQL's single-endpoint, variable-cost model is a documented DoS surface —
cyclic/deep queries, excessive field breadth, and batching attacks [Source:
graphql.org/learn/security/]. Apply: max query depth, stricter limits for nested
list fields (exponential blow-up), per-request field/alias/batch caps, and query
complexity analysis rather than request-count rate limiting. Disable introspection
in production unless trusted-document allowlisting is in use [Source:
www.graphql-js.org/docs/going-to-production/]. Mask errors via a custom formatter
that strips stack traces and internal detail from production error responses [Source:
www.graphql-js.org/docs/going-to-production/]. Deep threat modeling →
[security-engineering](../../core/taxonomy/skill-catalog.md) (SK-QA-002).

## Performance

DataLoader batching for N+1 is the primary lever [Source:
graphql.org/learn/performance/]. Use persisted queries (send a query hash instead
of full text) to enable HTTP/CDN caching and shrink payloads [Source:
graphql.org/learn/performance/]. Multi-layer caching: resolver-level for expensive
computations, HTTP/CDN via persisted queries, schema-build caching (avoid
rebuilding the schema object per request), and external caches (e.g., Redis) for
larger systems [Source: www.graphql-js.org/docs/going-to-production/]. Deep
performance method → [performance-engineering](../../core/taxonomy/skill-catalog.md)
(SK-QA-003).

## Testing

No official `graphql-js` testing guide exists as of this library's research
[Source: research/technologies/graphql.md §9]. The closest documented integration
is invoking `graphql({ schema, source, rootValue })` from a test runner and
asserting on `{ data, errors }` [Source: www.graphql-js.org/docs/getting-started/].
Community tools such as `@graphql-tools/mock` for resolver mocking are not
independently verified by this library's research — verify against current docs.
Deep test strategy → [testing-strategy](../../core/taxonomy/skill-catalog.md)
(SK-QA-001).

## Failure handling

- If `graphql-js` or Apollo Server version is unknown, ask or check `package.json` before giving resolver/API guidance — v16 and v17 differ in `execute()` return type, `GraphQLError` constructor, and development mode.
- If shell is unavailable, produce advisory schema and resolver code and state that codegen, schema introspection, and test execution were not run.
- If asked for Apollo Server or Apollo Client specifics not covered by this library's research, state that gap and direct to official Apollo documentation.

## Escalation

- Disabling introspection or adding depth/cost limits to an already-public API is a consumer-facing breaking change — surface for explicit confirmation before applying.
- A subscription architecture requiring horizontal scaling (clients across multiple server instances) is a significant infrastructure choice — surface for explicit confirmation and route to [realtime-communication](../realtime-communication/SKILL.md) (SK-BE-004).

## Outputs & verification

- **Outputs:** SDL schema changes and/or resolver code with DataLoader batching, an optional GraphQL Code Generator config, and a production-readiness assessment.
- **Verify:** Run at least one representative query via `graphql({ schema, source })` or `npx graphql-inspector introspect <endpoint>` to confirm the schema validates without errors; confirm nested-relationship resolvers use DataLoader and not per-item fetches.

## References

- [research/technologies/graphql.md](../../research/technologies/graphql.md) — graphql-js v17 API, GraphQL spec September 2025, security/performance/production guidance
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md) — §7 API spec tooling context
- [graphql-api-design](../graphql-api-design/SKILL.md) — schema design method (type modeling, N+1-safe resolver structure, pagination, field-level authorization design, schema evolution at design level)
