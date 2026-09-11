---
name: PostgreSQL
description: >-
  PostgreSQL-specific indexing (B-tree/GIN/GiST/BRIN), MVCC/VACUUM, transaction
  isolation levels, row-level security, full-text search, replication, and
  version-gated v18 features (OAuth2 auth, async I/O, protocol 3.2). Use when
  the stack targets PostgreSQL (postgres:// URL, pg/psycopg/pgx driver, a
  Postgres-configured ORM, or the task names a PG feature). Not for MySQL or
  other engines, generic schema design, or ORM mapping mechanics.
spec_version: "1.0"
---

## Purpose & scope

Apply PostgreSQL correctly and version-appropriately: indexing, MVCC/VACUUM,
transaction isolation, row-level security, full-text search, replication, and
the extension mechanism. The *method* for deciding what the schema should
look like and which store shape fits the workload lives in the parent skill,
[data-modeling](../data-modeling/SKILL.md) (`SK-DATA-001`) — this skill
supplies PostgreSQL's concrete, version-correct implementation of that model.
Query-tuning/operations depth (`SK-DATA-003`, database-operations) and the
in-DB-search-vs-dedicated-engine escalation path (`SK-DATA-005`,
search-integration) are owned by those sibling Layer-3 skills and referenced,
not restated, here.

## When to use / When not to use

**Use** when a `postgres://`/`postgresql://` connection string, a PG driver
(`pg`, `psycopg`, `pgx`, `libpq`), or a Postgres-configured ORM is present, or
the task names a PG-specific feature (MVCC, RLS, VACUUM, `EXPLAIN ANALYZE`,
`tsvector`, `pg_upgrade`, `LISTEN`/`NOTIFY`). **Do not use** for MySQL/
MongoDB/ClickHouse/other engines (route to that engine's skill), for
engine-agnostic schema design with no engine chosen yet (`SK-DATA-001`), for
ORM-mapping mechanics independent of the engine (`SK-DATA-002`), or for the
process discipline of migrating an already-populated schema (`SK-DATA-006`).

## Knowledge

- **MVCC** is PostgreSQL's concurrency model: each statement sees a snapshot,
  so readers never block writers and vice versa [Source: postgresql.org/docs/current/mvcc-intro.html].
  Because `UPDATE`/`DELETE` don't physically remove old row versions,
  **VACUUM** (autovacuum by default) reclaims space, updates planner
  statistics, and — critically — prevents 32-bit transaction ID (XID)
  wraparound by freezing old rows; this is a correctness requirement in
  long-lived, high-write clusters, not just a performance nicety
  [Source: postgresql.org/docs/current/routine-vacuuming.html].
- **Write-Ahead Logging (WAL)** gives durability and crash recovery, and
  underlies both physical replication and point-in-time recovery
  [Source: postgresql.org/docs/current/wal-intro.html (research/technologies/postgresql.md §1)].
- **Isolation levels:** PostgreSQL implements only three distinct behaviors —
  Read Uncommitted is aliased to Read Committed; Repeatable Read and
  Serializable both build on Snapshot Isolation, with Serializable adding
  Serializable Snapshot Isolation (predicate locking) to prevent serialization
  anomalies. Read Committed is the default. PostgreSQL's Repeatable Read
  prevents phantom reads, exceeding the SQL standard's minimum for that level
  [Source: postgresql.org/docs/current/transaction-iso.html].
- **Index types are workload-driven, not one-size-fits-all:** B-tree (default;
  equality/range/sort), GIN ("contains" queries over arrays/`jsonb`/full-text
  `tsvector`), GiST (geometric/nearest-neighbor/extensible search), BRIN
  (very large tables whose values correlate with physical row order — cheap,
  low storage overhead), Hash (equality-only), SP-GiST (non-balanced
  partitioned structures) [Source: postgresql.org/docs/current/indexes-types.html].
- **Row-level security (RLS):** `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` +
  `CREATE POLICY` (with `USING` for reads, optional `WITH CHECK` for writes)
  enforces per-row predicates at the database. Permissive policies combine
  with `OR`, restrictive with `AND`. **Fails closed**: RLS enabled with no
  policy defined denies all rows by default. Superusers, `BYPASSRLS` roles,
  and (by default) table owners bypass RLS unless the table has
  `FORCE ROW LEVEL SECURITY` [Source: postgresql.org/docs/current/ddl-rowsecurity.html].
- **Full-text search:** `tsvector`/`tsquery` types with a GIN index support
  in-database search without a separate engine
  [Source: postgresql.org/docs/current/datatype.html; postgresql.org/docs/current/indexes-types.html].
- **Replication:** physical (streaming) replication for standbys/HA/read
  scaling, and logical replication for selective/cross-version streaming.
  Synchronous replication guarantees no data loss on failover but "may
  significantly impact performance (>50% slowdown over slow networks)";
  asynchronous preserves throughput but risks losing recently-committed
  transactions and serving stale reads on failover
  [Source: postgresql.org/docs/current/high-availability.html].
- **Extensions** (`CREATE EXTENSION`) are the first-class mechanism for
  packaging types/functions/operators/index access methods as a single unit,
  tracked by `pg_dump`/`pg_upgrade` as a unit
  [Source: postgresql.org/docs/current/extend-extensions.html].
- **[Version-sensitive, >=18]** PostgreSQL 18 added OAuth 2.0 (SASL
  `OAUTHBEARER`) as a `pg_hba.conf` authentication method, 256-bit
  cancel-request keys under wire protocol **3.2** (protocol 3.0, PG 7.4+,
  remains supported for backward compatibility
  [Source: research/knowledge-maps/version-matrix.md; postgresql.org/docs/current/protocol.html]),
  an asynchronous I/O (AIO) subsystem the release announcement cites as "up to
  3× performance improvements when reading from storage"
  [Source: postgresql.org/about/news/postgresql-18-released-3142/], and B-tree
  "skip scan" support (multicolumn indexes usable even when the leading
  column is unconstrained) [Source: postgresql.org/docs/current/release-18.html].
- **[Version-sensitive, >=18]** `pg_upgrade` now carries forward optimizer
  statistics, reducing (not eliminating) the need for a full post-upgrade
  `ANALYZE` [Source: research/knowledge-maps/version-matrix.md]. Across all
  supported versions, `pg_upgrade` supports upgrading from PostgreSQL 9.2+ to
  the current major and requires binary compatibility
  [Source: research/knowledge-maps/version-matrix.md; postgresql.org/docs/current/pgupgrade.html].
- **[Version-sensitive]** Support window is 5 years per major release
  post-GA, minor releases at least every 3 months. As of 2026-09-09: PG14 is
  nearing EOL (2026-11-12), PG18 is the current stable baseline, PG19 is in
  Beta 3 (not GA) [Source: research/knowledge-maps/version-matrix.md;
  postgresql.org/support/versioning/]. This skill's guidance targets
  **PostgreSQL 14–18**; treat anything marked `>=18` as inapplicable on
  older majors still in support.

Comparative context vs. MySQL/MongoDB/ClickHouse (auth methods, RLS support,
transaction models, documented anti-patterns) is pre-researched in
[technology-decision-matrix.md §2](../../research/knowledge-maps/technology-decision-matrix.md#2-database-model-postgresql-vs-mysql-vs-mongodb-vs-clickhouse)
— use it rather than re-deriving a comparison.

## Decision framework

1. **Simplest first (anti-overengineering):** can a B-tree index or a query
   rewrite fix the observed plan? Prefer that over partitioning, a
   materialized view, or reaching for a new engine.
2. **Index type:** match the access pattern, not habit — equality/range/sort
   → B-tree; "contains" over arrays/`jsonb`/text → GIN; geometric/nearest-
   neighbor → GiST; huge, naturally-ordered tables → BRIN; pure equality at
   scale → Hash. Read the actual `EXPLAIN (ANALYZE, BUFFERS)` plan before
   choosing [Source: postgresql.org/docs/current/using-explain.html].
3. **Access control — RLS vs. app-level authz:** app-level authorization is
   sufficient for most single-tenant systems. Add RLS when the database
   itself must enforce tenancy/row ownership independently of the
   application (defense in depth, or multiple app surfaces hitting the same
   database). RLS is not a substitute for parameterized queries or GRANT-
   based privileges — it supplements them [Source: postgresql.org/docs/current/ddl-rowsecurity.html].
4. **In-DB full-text vs. a dedicated search engine:** `tsvector`/`tsquery` +
   GIN covers moderate full-text needs without operating a second system.
   Escalate to a dedicated engine (`SK-DATA-005`, search-integration) only
   once relevance-tuning or scale requirements exceed what GIN-backed FTS
   documents supporting — don't add a search engine "in case."
5. **Isolation level:** Read Committed (the default) is correct for most
   OLTP workloads. Choose Repeatable Read when a transaction must see a
   single consistent snapshot across multiple statements. Choose Serializable
   only when true serialization anomalies (not just dirty/non-repeatable
   reads) must be prevented — it costs more (SSI predicate locking, more
   retries) [Source: postgresql.org/docs/current/transaction-iso.html].
6. **Version gate:** confirm the PostgreSQL major version before
   recommending a version-gated feature (OAuth2 auth, async I/O, protocol
   3.2, skip-scan, statistics-carrying `pg_upgrade` all require `>=18`);
   state the version the guidance targets rather than assuming "latest"
   (rule VA-3).

## Workflow

1. Determine the PostgreSQL major version (server, container image tag, or
   manifest) — required before recommending any version-gated feature.
2. For a query problem, reproduce it with `EXPLAIN (ANALYZE, BUFFERS)`
   [Source: postgresql.org/docs/current/using-explain.html]; large
   estimate-vs-actual discrepancies signal stale statistics — run `ANALYZE`.
3. Apply the decision framework and make the smallest change that addresses
   the observed plan or requirement.
4. For schema changes, produce a reversible migration and hand rollout
   discipline to [data-migration](../data-migration/SKILL.md) (`SK-DATA-006`).
5. For a destructive migration or an untrusted `pg_dump` restore, stop and
   escalate (see Escalation) before executing.
6. Verify against the checks below before declaring done.

## Engineering rules

- Read the actual `EXPLAIN (ANALYZE, BUFFERS)` plan before adding an index —
  never index on a guess (see Anti-patterns).
- Keep transactions short; long-open/idle-in-transaction sessions block
  VACUUM's freezing and drive bloat [Source: postgresql.org/docs/current/routine-vacuuming.html].
- Leave autovacuum enabled; reserve manual `VACUUM` for cases autovacuum
  handles poorly, and prefer plain `VACUUM` run often enough over ever
  needing `VACUUM FULL` (exclusive lock, full rewrite)
  [Source: postgresql.org/docs/current/routine-vacuuming.html].
- Prefer parameterized queries; never string-concatenate SQL.
- For bulk loads: batch into `COPY` within one transaction, add
  indexes/foreign keys *after* loading, temporarily raise
  `maintenance_work_mem`/`max_wal_size`, and `ANALYZE` afterward
  [Source: postgresql.org/docs/current/populate.html].
- RLS policies with subqueries against concurrently-modified tables can leak
  information via a race condition unless mitigated with `SELECT ... FOR
  SHARE` or stronger locking [Source: postgresql.org/docs/current/ddl-rowsecurity.html].
- Always state the PostgreSQL version a piece of guidance targets; never
  assume "latest" silently (rule VA-3).

## Trade-offs

- RLS centralizes per-row enforcement at the database but adds per-query
  policy-evaluation overhead and a subquery race-condition class to reason
  about — worth it for hard multi-tenant isolation, overkill for a
  single-tenant app.
- In-DB full-text search avoids operating a second system but tops out below
  a dedicated search engine on relevance-tuning features and scale (see
  `SK-DATA-005`, search-integration).
- Synchronous replication trades write throughput for zero data loss on
  failover; asynchronous trades potential data loss/stale reads for
  performance — every HA topology makes this choice consciously
  [Source: postgresql.org/docs/current/high-availability.html].
- Serializable isolation gives the strongest correctness guarantee but costs
  more in locking overhead and transaction retries than Read Committed;
  don't default to it without a concrete anomaly it prevents.

## Anti-patterns

- **Adding indexes speculatively "for performance" without reading a plan**
  — write amplification and wasted space; this is the domain's
  over-engineering trap. Match the index type to the observed access
  pattern (Decision framework §2), not habit.
- **Routine `VACUUM FULL`** instead of relying on autovacuum/plain `VACUUM`
  — markedly slower and takes an exclusive table lock, the inverse of the
  documented "vacuum often enough" guidance [Source: postgresql.org/docs/current/routine-vacuuming.html].
- **Bulk-loading via many autocommitted `INSERT`s with indexes/FKs already
  in place** — the documented recommendation is `COPY` with indexes/FKs
  added afterward [Source: postgresql.org/docs/current/populate.html].
- **Restoring a `pg_dump`/`pg_restore` archive from an untrusted source** —
  the docs explicitly warn dumps "contain superuser code that executes
  during restore"; this is a documented security anti-pattern, not just a
  style concern [Source: postgresql.org/docs/current/app-pgdump.html]. See
  Escalation.
- **Relying on `pg_dump` alone as a production backup strategy** — the docs
  point to physical backup / continuous WAL archiving (PITR) instead
  [Source: postgresql.org/docs/current/app-pgdump.html].
- **Continuing to configure `md5` password authentication** — deprecated as
  of PG18 with warnings on `CREATE ROLE`/`ALTER ROLE`; no removal version
  has been published yet, but new configuration should not target it
  [Source: research/technologies/postgresql.md §6, §13; Unresolved: removal
  version].
- **Long-lived or idle-in-transaction sessions** — block VACUUM's freezing
  work and drive both bloat and XID-wraparound risk.

## Security

- Parameterize all queries; RLS supplements but does not replace GRANT-based
  privileges or app-level authorization
  [Source: postgresql.org/docs/current/ddl-rowsecurity.html].
- Authentication is configured per-connection-rule in `pg_hba.conf`:
  `trust`, `password`, `md5` (deprecated, see Anti-patterns), `scram-sha-256`,
  `gssapi`, `sspi`, `ident`, `peer`, `ldap`, `radius`, `cert`, `pam`, `bsd`,
  and **[Version-sensitive, >=18]** `oauth` (SASL `OAUTHBEARER`)
  [Source: postgresql.org/docs/current/auth-methods.html]. Prefer
  `scram-sha-256` or stronger for remote connections; avoid `trust`/`password`
  outside trusted local contexts.
- Enable TLS with `ssl = on`, a correctly-permissioned key file (`chmod
  0600`), and consider mandatory client-certificate verification
  (`clientcert=verify-full`) for mutual TLS
  [Source: postgresql.org/docs/current/ssl-tcp.html].
- Access control is role-based (`GRANT`/role membership); a role can act as a
  user, a group, or both [Source: postgresql.org/docs/current/user-manag.html].
- For the full cross-cutting threat model (injection defense in depth,
  secrets handling, transport security beyond TLS config), defer to
  `SK-QA-002` — not restated here (no-duplication rule QR-2).

## Performance

- `EXPLAIN (ANALYZE, BUFFERS)` is the primary diagnostic tool: compares
  estimated vs. actual rows/timing and shows buffer hit/read counts; large
  discrepancies signal stale statistics — run `ANALYZE`. Use inside
  `BEGIN`/`ROLLBACK` when analyzing data-modifying statements, since
  `EXPLAIN ANALYZE` actually executes the query and its side effects
  [Source: postgresql.org/docs/current/using-explain.html].
- Ongoing monitoring is backed by `pg_stat_activity` (live per-backend state,
  `wait_event`), `pg_stat_user_tables`/`pg_stat_user_indexes` (dead/live
  tuples, missed autovacuum, unused indexes), `pg_statio_*`/`pg_stat_io`
  (buffer/I/O counts), and `pg_stat_replication` (replica lag)
  [Source: postgresql.org/docs/current/monitoring-stats.html].
- **[Version-sensitive, >=18]** The async I/O (AIO) subsystem improves
  sequential scans, bitmap heap scans, and vacuum ("up to 3× ... reading
  from storage," vendor-cited); B-tree skip-scan lets multicolumn indexes
  serve queries that don't constrain the leading column
  [Source: postgresql.org/docs/current/release-18.html; postgresql.org/about/news/postgresql-18-released-3142/].
- Connection pooling is the other dominant lever alongside indexing and
  query shape — PostgreSQL's process-per-connection architecture means
  unpooled high-connection-count workloads pay a real per-connection cost
  [Source: postgresql.org/docs/current/tutorial-arch.html]. Cross-cutting
  performance method beyond this is owned by `SK-QA-003`.

## Testing

**Documented gap:** official PostgreSQL docs have **no first-party
application-level testing guidance** (no ephemeral-test-database story,
transactional test-isolation pattern, or fixture/seeding tooling). The
regression-test chapter (`pg_regress`, TAP tests) documents how the
PostgreSQL Global Development Group tests PostgreSQL *itself*, not how
application developers should test code against it
[Source: postgresql.org/docs/current/regress.html; research/technologies/postgresql.md §9].
This is a real, citable absence, not an oversight in this skill — app-level
test strategy against PostgreSQL is delegated to ORMs/tooling (e.g. Drizzle's
PGlite, the community `postgres` Docker image) and is owned by `SK-QA-001`
and the relevant ORM technology skill, not restated here.

## Failure handling

- If the PostgreSQL major version cannot be determined, ask for it or
  explicitly state the version the guidance assumes — never assume "latest"
  silently (rule VA-3).
- If shell is unavailable or denied, degrade to advisory DDL/query/index
  output and state that the migration/EXPLAIN was not actually run.
- If `EXPLAIN` output is unavailable for a "slow query" task, ask for it
  rather than guessing an index from the query text alone.

## Escalation

- A destructive migration (`DROP`, a data-losing `ALTER`, or a `pg_upgrade`
  in `link`/`swap` mode that makes the old cluster unusable) requires
  explicit user confirmation before execution
  [Source: postgresql.org/docs/current/pgupgrade.html]. Defer rollout
  discipline to `SK-DATA-006`.
- Restoring a `pg_dump`/`pg_restore` archive from an untrusted source is
  flagged and confirmed before running, since dumps execute superuser code
  on restore [Source: postgresql.org/docs/current/app-pgdump.html].

## Outputs & verification

- **Outputs:** version-correct DDL/migration, index/query changes, or
  analysis with rationale; CLI commands actually run (psql, `EXPLAIN`,
  `pg_upgrade`) when shell is available.
- **Verify:** the proposed index type matches the access pattern, not
  chosen by default; every version-specific claim is tagged with the PG
  range it holds for; a migration has a rollback path; destructive
  operations and untrusted-dump restores are flagged for confirmation, not
  executed silently.

## References

- Source list: see `skill.yaml.source_references` (PostgreSQL official docs,
  retrieved 2026-09-09, via `research/technologies/postgresql.md`; plus
  `research/knowledge-maps/technology-decision-matrix.md` and
  `research/knowledge-maps/version-matrix.md`).
- [research/technologies/postgresql.md](../../research/technologies/postgresql.md) — full primary research, including limits, breaking changes (v17→v18), and unresolved items.
- [Technology Decision Matrix §2](../../research/knowledge-maps/technology-decision-matrix.md#2-database-model-postgresql-vs-mysql-vs-mongodb-vs-clickhouse) — PostgreSQL vs. MySQL vs. MongoDB vs. ClickHouse comparison.
