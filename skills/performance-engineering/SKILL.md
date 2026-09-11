---
name: Performance engineering
description: >-
  Diagnose performance from evidence, not guesswork — profile before
  optimizing, address the dominant cost, know when caching vs. tuning is
  the right lever, and recognize cross-stack performance patterns (the
  "disable a dev-mode default before shipping" pattern, Redis as
  connective tissue, real-time transports' shared backpressure hazard).
  Use when a performance problem or budget is in play. Database/caching-
  specific depth comes from database-operations/caching-strategy.
spec_version: "1.0"
---

## Purpose & scope

Diagnose performance problems from evidence and address the dominant cost
— the cross-cutting discipline, not a repeat of any single technology's
own performance page (each technology skill in this library already owns
its own mechanics: bundle size and rendering for frontend frameworks,
query planning for databases, build-tool internals). Database-specific
performance (indexing, N+1, pooling) is owned by
[database-operations](../database-operations/SKILL.md); caching design is
owned by [caching-strategy](../caching-strategy/SKILL.md). This skill's
own content is the diagnostic method and the patterns only visible when
reading across sources.

## When to use / When not to use

**Use** when a performance problem or budget is in play, or a diagnostic
is needed before optimizing. **Do not use** for no performance concern,
premature optimization the user didn't ask for, or database-indexing/
caching-specific questions (route to the dedicated skills for those).

## Knowledge

**"Disable a development-mode default before shipping" recurs across
unrelated stacks as the same architectural mistake, independently
rediscovered.** Express's `NODE_ENV=production` flag makes roughly a 3x
performance difference per Express's own benchmark. Mongoose's
`autoIndex` (enabled by default) is explicitly recommended off in
production to avoid index-build overhead on large collections. None of
the individual sources frames this as a shared pattern — it's the same
shape every time: a convenience default that measurably costs performance
and must be explicitly disabled for production
[Synthesis, performance-knowledge-map.md §17]. **Check for this class of
issue first** before assuming a deeper architectural cause — it is a
cheap, high-yield check.

**Redis functions as the default cross-layer performance/coordination
primitive across this stack, visible only by reading multiple
integrations side by side** — see
[caching-strategy](../caching-strategy/SKILL.md) for the full pattern
(TypeORM's query cache, Drizzle's Upstash integration, Express's session
store, graphql-js's external cache, Socket.IO's redis-adapter, none of
which reference each other).

**N+1 query patterns recur at every data-access layer with a different
name per technology** — see
[database-operations](../database-operations/SKILL.md) for the full
pattern (Mongoose's populate/select, TypeORM's `leftJoinAndSelect`,
Prisma's `include`, GraphQL's DataLoader — the same "batch or join instead
of iterate" fix, independently rediscovered per layer).

**Connection-pool sizing is treated as a first-class, quantified
provisioning step regardless of language or stack** — MongoDB/Mongoose
(110–115% of concurrency), Prisma+PgBouncer (external pooler required in
Transaction mode), and Go's `database/sql` all carry dedicated pool-sizing
guidance with no cross-reference between them — see
[database-operations](../database-operations/SKILL.md) for detail.

**Real-time transports converge on the same unbounded-send-buffer hazard,
independently, across every protocol this research covers.** WebSocket
API's documented core limitation is the absence of backpressure — fast
producers overrun a slow consumer, causing unbounded memory growth.
Socket.IO's `socket.volatile.emit()` trades reliability for reduced
buffering. WebRTC data channels auto-buffer, with `bufferedamountlow` as
the monitoring signal. **None of the individual docs frames this as a
shared transport-layer pattern** — every real-time layer in this dataset
independently re-derives the same problem and the same class of fix
(monitor buffered amount and back off, or explicitly opt into a lossy/
volatile delivery mode) [Synthesis, performance-knowledge-map.md §8, §17].

**Systems-language rewrites of core JS/Node tooling are an ecosystem-wide
trend, not an isolated event, and each independently reports large
speedups.** TypeScript 7.0's Go-native compiler (8–12x on full builds,
vendor-reported), Vite 8's Rust-based Rolldown bundler (10–30x faster
builds, vendor-reported), and Tailwind CSS v4's Rust-based Oxide engine
(3.78–5x full builds, up to ~182x for no-new-CSS incremental rebuilds,
vendor-reported) each independently made this move
[Synthesis, performance-knowledge-map.md §9, §17]. No single source frames
this as an ecosystem trend — it's relevant context for any build-tool
version-upgrade or tool-selection decision, and every one of these figures
is vendor-reported, not independently corroborated; state that caveat
when citing them.

**Sync beats async for CPU-bound compile/transform work, repeatedly, as a
recurring shape rather than a single tool's quirk.** Sass's synchronous
JS API is documented faster than its async variants (legacy `render()` is
2–3x slower than `renderSync()`); Vitest's `forks` pool (safe, can be
slower) vs. `threads`/`vmThreads` echoes the same theme in a different
tool [Synthesis, performance-knowledge-map.md §17]. Async plumbing costs
throughput even when it doesn't change correctness — worth checking
whenever a CPU-bound transform step is the identified bottleneck.

**Profiling/diagnostic tooling is genuinely uneven across this research —
know what's actually available before assuming a tool exists.**
PostgreSQL has `EXPLAIN`/`EXPLAIN (ANALYZE, BUFFERS)` and `pg_stat_*`
views; MySQL has `EXPLAIN` plus Performance Schema/`sys` schema; Python
has `cProfile`/`profile` plus (3.12+) `sys.monitoring` for low-overhead
event tracing and `perf` interoperability; Go has the race detector
(`-race`, at a documented 5–10x memory / 2–20x execution-time cost —
clearly a testing/CI-time tool, not a production configuration).
**ClickHouse has no documented diagnostic/profiling tool equivalent to
Postgres's `EXPLAIN` or MySQL's Performance Schema in this research** —
state that gap rather than assuming parity across databases
[Source: performance-knowledge-map.md §16].

**This library's research is explicitly silent on several categories a
performance skill would normally be expected to cover — state these gaps
rather than improvising:** general-purpose CDN vendors (Cloudflare,
Fastly, CloudFront, Akamai) have no dedicated research entry — CDN
behavior surfaces only through framework-level edge features (Next.js
Cache Components, Nuxt `routeRules`); message-queue/event-streaming
performance (Kafka, RabbitMQ, SQS) is not covered, consistent with the
Event-Driven-Architecture research gap noted elsewhere in this library;
load-balancer configuration performance beyond high-level
offload-to-reverse-proxy recommendations is not covered; Node.js
runtime-level performance (V8 tuning, event-loop diagnostics) is not
present as its own researched technology
[Source: performance-knowledge-map.md §18].

## Decision framework

1. **Is there actual profiling/benchmark evidence, or is this a guess?**
   Measure before proposing a change — this is the single most-repeated
   discipline across every technology's own performance guidance in this
   research.
2. **Does the symptom match a known cross-stack pattern** (a dev-mode
   default left on, connection-pool exhaustion, real-time backpressure,
   an N+1 pattern)? Check these first — they're cheap to rule in or out
   and recur constantly across unrelated stacks.
3. **Is the identified cost actually dominant**, or would fixing it move
   the needle only marginally? Refuse to micro-optimize a non-bottleneck
   — the research consistently frames this as wasted effort.
4. **Is the right lever caching, tuning, or scaling?** These are different
   fixes for different root causes — caching helps a repeated-computation
   cost, tuning helps an inefficient-computation cost, horizontal scaling
   helps a genuine capacity ceiling. Don't reach for the familiar lever
   without checking it matches the actual cause.
5. **Does this library's research actually cover the specific technology/
   vendor in question?** If not (a named CDN vendor, a message queue,
   Node.js runtime internals), say so rather than improvising generic
   performance advice presented as researched fact.

## Workflow

1. Gather profiling/benchmark evidence for the actual symptom.
2. Check the symptom against known cross-stack patterns (dev-mode default,
   N+1, pool exhaustion, real-time backpressure) before assuming a novel
   cause.
3. Confirm the identified cost is actually dominant, not a marginal
   contributor.
4. Choose the right lever (caching, tuning, scaling) matched to the root
   cause; hand off to database-operations/caching-strategy for depth in
   those domains.
5. State plainly where this library's research doesn't cover the specific
   technology/vendor in question.

## Engineering rules

- Measure before optimizing; never propose a change without evidence it
  addresses the actual bottleneck.
- Check for known cross-stack patterns (dev-mode defaults, N+1, pool
  exhaustion, real-time backpressure) before assuming a novel cause.
- Refuse to micro-optimize a component that isn't the measured dominant
  cost.
- State plainly when a vendor-reported performance figure (a native-
  rewrite speedup claim, a benchmark number) hasn't been independently
  corroborated.
- State plainly when this library's research doesn't cover a specific
  technology/vendor, rather than improvising.

## Trade-offs

Profiling before optimizing costs upfront time but avoids wasted effort on
a non-bottleneck — the research consistently frames unmeasured
optimization as the more expensive path in aggregate. Systems-language
tooling rewrites (TypeScript/Vite/Tailwind) buy large speedups at the cost
of ecosystem churn during the transition; their reported figures are
vendor-published and should be treated as directional, not guaranteed for
a given codebase.

## Anti-patterns

- **Optimizing without measuring first** — the single most consistently
  reinforced discipline across this entire research corpus.
- **Micro-optimizing a component that isn't the actual bottleneck.**
- **Treating a cross-stack pattern as novel** (re-diagnosing a dev-mode-
  default issue from scratch instead of checking for it first).
- **Citing a vendor-reported speedup figure as independently
  corroborated** without stating that caveat.
- **Assuming diagnostic-tooling parity across databases** — ClickHouse
  specifically has no documented `EXPLAIN`-equivalent in this research;
  don't assume one exists.

## Security

Not a primary concern for this skill's scope; where performance tuning
intersects security (e.g. disabling a rate limit for throughput), flag the
trade-off and defer to
[security-engineering](../security-engineering/SKILL.md).

## Performance

This skill's entire content is performance method. Database-specific and
caching-specific depth are owned by
[database-operations](../database-operations/SKILL.md) and
[caching-strategy](../caching-strategy/SKILL.md) respectively;
per-technology mechanics (bundle size, rendering, build tooling) are owned
by each technology's own skill.

## Testing

Load/performance testing tools are technology-specific (`redis-benchmark`,
OpenSearch Benchmark, ClickHouse's hardware performance-test script,
Vitest's Tinybench-powered `bench()`) — see
[testing-strategy](../testing-strategy/SKILL.md) for the load-testing
layer's place in the broader test-strategy decision framework.

## Failure handling

- If no profiling/benchmark evidence is available, gather it before
  proposing a change rather than guessing at the bottleneck.
- If the request is really database-specific or caching-specific, route
  to database-operations/caching-strategy.
- If this library's research is silent on a specific vendor/product, say
  so rather than inventing guidance.

## Escalation

- A capacity/scaling decision with real infrastructure cost implications
  (adding instances, a managed caching tier) is presented with trade-offs
  for explicit confirmation, not applied unilaterally.

## Outputs & verification

- **Outputs:** performance findings — the dominant cost identified from
  evidence, with prioritized changes.
- **Verify:** the identified cost is evidence-backed, not guessed; no
  micro-optimization is proposed for a non-bottleneck; cross-stack
  patterns are checked before assuming a novel cause.

## References

- [research/knowledge-maps/performance-knowledge-map.md](../../research/knowledge-maps/performance-knowledge-map.md)
