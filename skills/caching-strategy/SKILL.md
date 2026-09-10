---
name: Caching strategy
description: >-
  Design caching — choose the layer(s) (client/CDN/app/ORM/database),
  design the invalidation strategy (the hard part), and set TTLs/eviction
  avoiding stale-data and thundering-herd pitfalls. Use when performance/
  scale needs caching or a cache layer is being added. Redis-specific
  implementation depth comes from the redis technology skill.
spec_version: "1.0"
---

## Purpose & scope

Choose cache layer(s) and design invalidation/TTL strategy — cross-
cutting, since this library's research shows caching spanning Redis, ORM
query-result caches, framework rendering layers, and CI/build tooling.
Redis-specific mechanics are owned by
[redis](../redis/SKILL.md); database query optimization itself belongs to
[database-operations](../database-operations/SKILL.md).

## When to use / When not to use

**Use** when performance/scale needs caching, a cache layer is being
added, or an existing cache is suspected of serving stale data.
**Do not use** when there's no caching need, or for database query/index
optimization with no caching question.

## Knowledge

**Redis functions as the default cross-layer caching/coordination
primitive across nearly every stack this library researched — a pattern
visible only when the individual integrations are placed side by side.**
TypeORM's query-result cache supports Redis/IORedis/IORedis-Cluster as a
production-recommended backend over the default DB-table store. Drizzle's
experimental caching layer integrates with Upstash Redis via
`upstashCache()`, auto-invalidating affected queries on mutation. Express
recommends Redis as an externalized session store specifically so the app
can stay stateless behind clustering. graphql-js names Redis as the
external-cache layer for larger systems. Socket.IO's official
`@socket.io/redis-adapter` handles cross-process broadcast for multi-node
deployments. **None of these five sources reference each other** — Redis
emerges as connective tissue only by reading across all five
[Synthesis, performance-knowledge-map.md §17].

**Query-result caching is genuinely uneven across ORMs — check what the
specific ORM actually supports before assuming a caching story exists.**
TypeORM ships `cache:true` with a default 1000ms lifetime, per-query
override, and pluggable storage backends
[Source: typeorm.io/docs/query-builder/caching/]. Drizzle's caching layer
is explicitly experimental and opt-in per-query or global. Prisma names
the *absence* of caching as one of its own documented common causes of
slow queries — Prisma itself doesn't ship a query-result cache; Query
Insights (built into Prisma Postgres) helps identify slow queries instead.
**Mongoose, MySQL, and MongoDB's own docs describe no query-result caching
layer of their own** — their caching-relevant material is about
connection/index tuning, not a result cache [Source: performance-
knowledge-map.md §1.1].

**Application/HTTP-layer caching consistently gets pushed to the
edge/reverse-proxy, not left in the app process, across the frameworks
surveyed.** Express recommends caching at the reverse-proxy/edge layer
(Varnish, Nginx) rather than in the Express process itself
[Source: expressjs.com/en/advanced/best-practice-performance.html].
Next.js's Cache Components produce a static shell (PPR) servable directly
from a CDN without hitting the upstream server at all. GraphQL's persisted
queries (sending a hash instead of full query text) enable HTTP/CDN
caching of otherwise-uncacheable POST requests — a real, specific
mechanism for making a normally-uncacheable request type cacheable.

**Redis's own performance characteristics matter for how it's used as
caching infrastructure, not just whether to use it.** Pipelining — batching
multiple commands into one write, reading replies after — is documented as
giving **up to a 10x increase in ops/sec** by reducing round-trip overhead
[Source: redis.io/docs/latest/develop/using-commands/pipelining/]. Redis
is fundamentally single-threaded for command execution (favoring
single-core speed over core count, though Redis 8.0 added multi-core I/O
threading for the I/O path specifically, not command execution). **Redis
throughput roughly halves going from ~100 to ~30,000 concurrent
connections** — directly relevant to how a cache client pools connections
to it, not just how the app's own database connections are pooled.

**A convenience default left on in a non-production environment is a
recurring, cross-stack performance mistake — caching is one instance of a
broader pattern.** Express's `NODE_ENV=production` flag (Express's own
benchmark: ~3x performance difference), Mongoose's `autoIndex` (recommended
off in production), and framework debug flags elsewhere in this research
all share the same shape: a convenience default that measurably costs
performance and must be explicitly disabled for production
[Synthesis, performance-knowledge-map.md §17]. Check this class of
default whenever setting up a caching layer for production, not just the
cache configuration itself.

## Decision framework

1. **What's the actual data-volatility and access pattern?** High-read,
   low-write, tolerant-of-some-staleness data is a strong caching
   candidate; frequently-changing or consistency-critical data may not be,
   or needs a much shorter TTL / event-driven invalidation instead of a
   time-based one.
2. **Which layer actually needs the cache** — client, CDN/edge, app
   process, ORM query-result, or the database's own mechanisms? Prefer
   pushing cacheable content as close to the edge as the framework
   supports (this research shows Express/Next.js/GraphQL all doing this)
   rather than defaulting to an in-app cache.
3. **Is invalidation designed explicitly, or is TTL doing all the work?**
   TTL-only caching is the easy default but produces a bounded staleness
   window even for data that changed the instant after a cache write —
   design explicit invalidation (event-driven, mutation-triggered) for
   anything where that window matters.
4. **Is Redis (or an equivalent) actually warranted**, or does a simpler
   in-process/HTTP-layer cache suffice for the scale in question? Redis
   earns its keep at genuine multi-process/cross-layer coordination scale
   — don't reach for it reflexively for a single-process app's local cache
   needs.
5. **Is a thundering-herd risk present** — many concurrent requests
   missing the cache simultaneously after a hard expiry on hot data? If
   so, design around it (staggered TTLs, request coalescing, stale-while-
   revalidate) rather than accepting a cache-stampede risk.
6. **Are convenience-mode defaults (NODE_ENV, autoIndex, debug flags)
   actually disabled for production** wherever they'd affect the cache
   layer's own performance?

## Workflow

1. Establish data-volatility and access pattern for the data being
   cached.
2. Choose the cache layer(s), preferring the edge/CDN where the stack
   supports it.
3. Design the invalidation strategy explicitly — this is the hard part,
   not an afterthought to TTL.
4. Set TTL/eviction policy matched to actual staleness tolerance.
5. Address thundering-herd risk for any hot-data cache with a hard expiry.
6. If Redis is the chosen layer, account for its own performance
   characteristics (pipelining, connection-count scaling) in the client
   design; hand off deep Redis mechanics to
   [redis](../redis/SKILL.md).
7. Verify production-mode convenience defaults are disabled.

## Engineering rules

- Never propose a cache without an explicit invalidation strategy — a
  TTL alone is not invalidation design.
- Prefer pushing cacheable content to the edge/CDN where the framework
  supports it, over defaulting to an in-app process cache.
- Check what the specific ORM/framework in use actually supports before
  assuming a caching story exists — this varies significantly
  (TypeORM/Drizzle have one; Mongoose/MySQL/MongoDB's own docs don't).
- Design around thundering-herd risk for hot data with a hard expiry.
- Verify production-mode convenience defaults (NODE_ENV, autoIndex, debug
  flags) are actually disabled.

## Trade-offs

TTL-only caching is simple to implement but produces a bounded staleness
window regardless of when the underlying data actually changed.
Event-driven/mutation-triggered invalidation is more precise but adds
real implementation complexity (the cache and the mutation path must stay
correctly wired together). Pushing caching to the edge/CDN buys lower
latency and reduced origin load at the cost of less fine-grained control
than an app-level cache offers. Redis buys cross-process/cross-layer
coordination at genuine scale, at the cost of an additional operational
component and connection-count-sensitive throughput characteristics not
every app needs to reason about.

## Anti-patterns

- **Treating a TTL as sufficient invalidation strategy** on its own — the
  genuinely hard part of caching is invalidation, not expiry.
- **Defaulting to an in-app process cache** when the framework's own edge/
  CDN caching features (Next.js Cache Components, persisted GraphQL
  queries) would serve the need with less origin load.
- **Assuming every ORM has a query-result cache** — Mongoose, MySQL, and
  MongoDB's own docs describe none; check before assuming.
- **Ignoring thundering-herd risk** on hot data with a hard TTL expiry.
- **Reaching for Redis reflexively** for scale that doesn't actually need
  cross-process coordination.

## Security

Session data cached in Redis or an equivalent store should follow the
same secrets-hygiene discipline as any other credential storage — never
log cached session tokens, and set appropriate TTLs so stale sessions
don't linger indefinitely. Deep threat modeling is owned by
[security-engineering](../security-engineering/SKILL.md).

## Performance

This skill's own content IS the caching-performance method. Redis's own
performance characteristics (pipelining's ~10x ops/sec gain, single-
threaded command execution, connection-count-sensitive throughput) are
covered in Knowledge above; broader cross-cutting performance method is
owned by [performance-engineering](../performance-engineering/SKILL.md).

## Testing

Cache-invalidation correctness (does a mutation actually invalidate the
right cached entries) is the caching-specific testing concern — verify it
explicitly rather than assuming the invalidation logic works because the
cache-write logic does. Deep test-strategy method is owned by
[testing-strategy](../testing-strategy/SKILL.md).

## Failure handling

- If data-volatility/access-pattern information isn't available, ask
  rather than guessing a TTL.
- If the target ORM/framework has no documented first-party caching
  story, state that gap.

## Escalation

- A caching-layer change affecting production data freshness (e.g.
  lengthening a TTL on consistency-sensitive data) is presented with
  trade-offs for explicit confirmation.

## Outputs & verification

- **Outputs:** a caching design — layer(s), invalidation strategy, and
  TTL/eviction policy, with rationale.
- **Verify:** invalidation is explicit, not TTL-only; the chosen layer
  matches actual access pattern/volatility; thundering-herd risk is
  addressed where relevant.

## References

- [research/knowledge-maps/performance-knowledge-map.md](../../research/knowledge-maps/performance-knowledge-map.md)
