---
name: Database operations
description: >-
  Operate a database well — index strategy, query-plan analysis and N+1
  avoidance, transaction/isolation-level choices, connection-pool sizing,
  and replication/backup/PITR awareness. Use when query performance,
  transactions, indexing, or pooling are in play. Not for schema design
  itself (data-modeling) or caching design (caching-strategy).
spec_version: "1.0"
---

## Purpose & scope

Operate a database well once its schema exists — indexing, query
optimization, transactions, connection pooling — independent of which
database or ORM. Specialized by each database/ORM technology skill for
engine-specific mechanics. Schema design itself belongs to
[data-modeling](../data-modeling/SKILL.md); caching design belongs to
[caching-strategy](../caching-strategy/SKILL.md).

## When to use / When not to use

**Use** when query performance, transactions, indexing, or connection
pooling are in play. **Do not use** for pure schema design with no
operational question, or for caching design specifically.

## Knowledge

**N+1 is documented, independently, at essentially every data-access
layer in this research — the same fix pattern, restated with a different
name each time.** Mongoose's populate guidance recommends `select` to
limit fields and avoiding `perDocumentLimit` (which issues one query per
parent document instead of a batched one). TypeORM's fix is
`leftJoinAndSelect`/`innerJoinAndSelect` or the `relations` object syntax.
Prisma's is `include` for eager-loading, or `relationLoadStrategy:'join'`
to force a single SQL join. GraphQL's is DataLoader-style batching,
coalescing same-tick requests into one backend call
[Synthesis, performance-knowledge-map.md §2]. **None of these individual
sources frames this as a cross-stack pattern — it's only visible placed
side by side**: batch or join instead of iterating per row, regardless of
which data-access layer is in use.

**Index-type selection is genuinely workload-specific across engines, not
a single "add an index" rule.** PostgreSQL offers B-tree (equality/range/
sort), GIN (contains-queries over arrays/jsonb/full-text), GiST
(geometric/nearest-neighbor), BRIN (large physically-correlated tables),
and Hash (pure equality) — choosing the wrong type for the query shape
leaves performance on the table even with an index present
[Source: postgresql.org/docs/current/indexes-types.html]. MongoDB's
compound-index field ordering follows the **ESR rule (Equality, Sort,
Range)**. ClickHouse's primary-key index is **sparse** (one mark per
~8,192-row granule, not per row) specifically to keep huge datasets'
primary keys memory-resident — and ClickHouse's own docs explicitly
caution that "partitioning does not speed up queries" in general, it's
primarily a data-management tool, a real, counter-intuitive point worth
stating precisely rather than assuming partitioning is a performance
lever by default.

**Indexes have a real, often-overlooked write-time and memory cost, not
just a read-time benefit.** MongoDB's docs state plainly that every
insert/update/delete must update matching indexes, and indexes consume
memory. Mongoose's `autoIndex` (enabled by default) auto-builds every
declared index on connect — **explicitly recommended to disable in
production** to avoid index-build performance degradation on large
collections [Source: mongoosejs.com/docs/connections.html]. This is a
real, concrete, easy-to-miss production-readiness check.

**Connection-pool sizing is treated as a first-class, quantified
provisioning step across every stack this research covers — not an
afterthought.** MongoDB's documented guidance: size the pool at roughly
**110–115% of typical concurrent request volume**
[Source: mongodb.com/docs/manual/administration/production-notes/].
Prisma explicitly requires an external pooler (PgBouncer) for
high-concurrency workloads, and PgBouncer **must run in Transaction
mode** for Prisma Client to work reliably — the default pooling mode
causes "prepared statement s0 already exists" errors, a real, specific,
otherwise-confusing failure mode. A single global `PrismaClient` instance
must be reused across the app; multiple instances exhaust the DB
connection pool [Source: prisma.io/docs — pgbouncer, best-practices].
**None of these sources cross-reference each other, but together they
indicate pool-size tuning is a first-class provisioning step regardless
of language or ORM** [Synthesis, performance-knowledge-map.md §4].

## Decision framework

1. **Is there an actual query plan or slow-query symptom, or is this
   speculative?** Diagnose from evidence (`EXPLAIN`/`EXPLAIN ANALYZE`,
   MySQL's `EXPLAIN`, Performance Schema) before proposing an index or
   rewrite — don't add an index speculatively.
2. **What's the query shape actually asking for** (equality, range, sort,
   contains/full-text, geometric)? Match the index type to that shape —
   B-tree isn't universally correct across every workload.
3. **Is this an N+1 pattern?** If so, batch or join at the data-access
   layer's own idiom (populate+select, `leftJoinAndSelect`, `include`,
   DataLoader) rather than accepting per-row query iteration.
4. **What isolation level does this transaction actually need?** Higher
   isolation buys consistency at a throughput cost — choose deliberately,
   state the trade-off, don't default to the strictest or the weakest
   without reasoning about it.
5. **Is the connection pool sized to actual concurrency**, or left at a
   default? Quantify from expected concurrent request volume (MongoDB's
   110–115% guidance is a reasonable starting heuristic), and check
   whether an external pooler is needed for the ORM/database combination
   in use (e.g. Prisma + PgBouncer in Transaction mode).
6. **Is `autoIndex`-style auto-build-on-connect behavior disabled in
   production**, where the ORM defaults it on? A real, easy-to-miss
   production-readiness check.

## Workflow

1. Gather the actual query plan/symptom rather than diagnosing
   speculatively.
2. Identify whether the dominant cost is a missing/wrong-type index, an
   N+1 pattern, or a transaction/pooling issue.
3. Apply the fix matching the actual data-access layer's own idiom.
4. State the isolation-level trade-off explicitly for any transaction
   design.
5. Size the connection pool to actual concurrency; verify auto-index-on-
   connect behavior is disabled in production where applicable.
6. Hand off caching-layer decisions to caching-strategy rather than
   designing them here.

## Engineering rules

- Diagnose from an actual query plan/symptom, never add an index
  speculatively.
- Match index type to query shape (equality/range/sort/contains/
  geometric), not a one-size-fits-all default.
- Fix N+1 at the data-access layer's own idiom (batch or join), never
  leave it as accepted per-row iteration.
- State the isolation-level trade-off explicitly for every transaction
  design decision.
- Size connection pools to actual concurrency; verify auto-index-build
  behavior is disabled in production.

## Trade-offs

Adding an index speeds reads but costs write-time overhead (every insert/
update/delete must update it) and memory — not free, and unindexed columns
that are rarely queried shouldn't be indexed reflexively. Higher isolation
levels buy consistency guarantees at reduced concurrency/throughput.
External connection poolers (PgBouncer) buy protection against connection
exhaustion at the cost of an additional operational component and mode-
specific compatibility constraints (Transaction mode requirement for
Prisma).

## Anti-patterns

- **Adding an index without a query plan justifying it** — real, avoidable
  write-time/memory cost for no measured benefit.
- **Leaving N+1 query patterns unaddressed** — the single most-repeated
  performance finding across every data-access layer in this research.
- **Assuming partitioning speeds up queries** (ClickHouse specifically
  documents that it does not, in general — it's a data-management tool).
- **Leaving `autoIndex`-style behavior on in production** where the ORM
  defaults it enabled.
- **Instantiating multiple ORM client instances** (e.g. multiple
  `PrismaClient`s) instead of one reused global instance, exhausting the
  connection pool.

## Security

Restoring a `pg_dump`/`pg_restore` archive from an untrusted source is
explicitly flagged as dangerous — dumps contain superuser code that
executes during restore [Source via security-knowledge-map.md]. Deep
threat modeling is owned by
[security-engineering](../security-engineering/SKILL.md).

## Performance

This skill's own content IS the database-operational performance method
(indexing, N+1, connection pooling). Broader cross-cutting performance
method (bundle size, scaling, profiling tooling) is owned by
[performance-engineering](../performance-engineering/SKILL.md).

## Testing

This library's research shows a real, recurring gap: PostgreSQL, MySQL,
and MongoDB (via its drivers) all lack a first-party "how to test your app
against me" methodology (ephemeral test DBs, fixtures, transactional
isolation) — state this plainly when it applies rather than inventing an
official-sounding methodology. Deep test-strategy method is owned by
[testing-strategy](../testing-strategy/SKILL.md).

## Failure handling

- If no query plan or workload evidence is available, ask for it rather
  than guessing at the dominant cost.
- If the target database/ORM has no documented first-party operational
  guidance for a specific concern, state that gap.

## Escalation

- A transaction/isolation-level change or connection-pool resize on an
  existing production database is presented with trade-offs for explicit
  confirmation, given the potential for a subtle correctness or
  availability regression.

## Outputs & verification

- **Outputs:** index/query-rewrite recommendations matched to an actual
  plan, and transaction/pooling design with stated rationale.
- **Verify:** recommendations trace to actual evidence, not speculation;
  isolation-level and pool-sizing choices state their trade-off
  explicitly.

## References

- [research/knowledge-maps/performance-knowledge-map.md](../../research/knowledge-maps/performance-knowledge-map.md)
