---
name: PostgreSQL
description: >-
  PostgreSQL-specific schema, indexing, transactions, MVCC, row-level security,
  and full-text search. Use when the stack uses PostgreSQL (postgres:// URL,
  pg/psycopg drivers, a Postgres-targeted ORM, or the task names it). Not for
  MySQL/other SQL engines, generic data modeling (use data-modeling), or ORM
  usage patterns (use orm-integration).
spec_version: "1.0"
---

<!-- ILLUSTRATIVE EXAMPLE: complex SKILL.md body. Abbreviated; not the authored
     SK-TECH-postgresql skill. Source markers like [src: mvcc] resolve to
     skill.yaml.source_references. Shows all Tier-1 sections for a technology skill;
     deep material is pushed to references/ per context-efficiency rules. -->

## Purpose & scope

Apply PostgreSQL correctly for the version in use — schema, indexing,
transactions/MVCC, row-level security, and full-text search. The *method* (how
to model data, how to reason about a query plan) comes from the parent skills
(`SK-DATA-001`, `SK-DATA-003`, `SK-DATA-005`); this skill supplies the
PostgreSQL specifics.

## When to use / When not to use

**Use** when a `postgres://` URL, a PG driver (`pg`/`psycopg`/`pgx`), or a
Postgres-targeted ORM is present, or the task names a PG feature. **Do not use**
for MySQL/other engines (route to that skill), engine-agnostic schema design
(`SK-DATA-001`), or ORM mechanics (`SK-DATA-002`).

## Knowledge (essential)

- **MVCC:** readers don't block writers; long-open transactions and dead tuples
  drive bloat — `VACUUM`/autovacuum reclaim it. [src: mvcc]
- **Index types:** B-tree (equality/range), GIN (full-text, arrays, jsonb), GiST
  (geometric/nearest-neighbor), BRIN (large, naturally-ordered tables). Match the
  type to the access pattern. [src: indexes]
- **Row-level security:** `ENABLE ROW LEVEL SECURITY` + `CREATE POLICY` enforce
  per-row access at the database, complementing app-level authz. [src: rls]
- **Full-text search:** `tsvector`/`tsquery` with a GIN index for in-database
  search before reaching for a separate engine. [src: fts]

> Deep material (isolation-level matrix, index-selection decision table, RLS
> policy recipes) lives in [`references/indexing-and-mvcc.md`](references/indexing-and-mvcc.md)
> — loaded only when needed (context-efficiency rule CE-3).

## Decision framework

1. **Simplest first (anti-overengineering):** can a B-tree index or a query
   rewrite fix it? Prefer that over partitioning, materialized views, or a new
   engine.
2. **Search:** in-DB full-text (GIN + `tsvector`) suffices for moderate needs;
   escalate to a dedicated search engine (`SK-DATA-005` → OpenSearch) only when
   relevance/scale demands it.
3. **Access control:** app-level authz for most cases; add RLS when the database
   must enforce tenancy/row ownership independently.
4. **Version gate:** confirm the PG major version before recommending a
   version-gated feature; state the version your guidance targets.

## Workflow

1. Determine the PostgreSQL major version (server / image tag / manifest).
2. Reproduce the problem with `EXPLAIN (ANALYZE, BUFFERS)` where a query is involved.
3. Apply the smallest change that addresses the observed plan / requirement.
4. For schema changes, produce a reversible migration (hand to `SK-DATA-006`).
5. Verify (below) before declaring done.

## Engineering rules

- Read the actual query plan before adding an index; don't index on a guess.
- Keep transactions short (MVCC bloat); avoid idle-in-transaction.
- Prefer parameterized queries; never string-concatenate SQL (see Security).
- Choose the index type from the access pattern, not by default to B-tree.

## Trade-offs

- RLS centralizes enforcement but adds per-query policy overhead and debugging
  complexity — worth it for hard multi-tenant isolation, overkill for a
  single-tenant app.
- In-DB full-text avoids operating a second system but tops out below a
  dedicated engine on relevance features and scale.

## Anti-patterns

- Adding indexes speculatively "for performance" without a plan (write
  amplification, wasted space) — the domain's over-engineering trap.
- Long-lived transactions / disabling autovacuum.
- Reaching for a separate search engine when GIN full-text would do.

## Security

- Parameterize all queries; RLS complements but does not replace app-level
  authorization. For the full threat model (injection, secrets, transport),
  defer to `SK-QA-002` — not restated here (no-duplication rule QR-2).

## Performance

- The dominant levers are indexing, query shape, and connection pooling; measure
  first. Cross-cutting performance method lives in `SK-QA-003`.

## Testing

- Test migrations against a disposable Postgres (a container per `SK-TECH-docker`);
  assert both the up and down paths. Test strategy is owned by `SK-QA-001`.

## Failure handling

- If the PG major version is unknown, ask or explicitly state the assumed
  version — never assume "latest" (rule VA-3).
- If shell is unavailable, output advisory DDL/queries and state that the
  migration/EXPLAIN was not executed.

## Escalation

- A data-losing migration (`DROP`/destructive `ALTER`) requires explicit user
  confirmation before execution.

## Outputs & verification

- **Outputs:** version-correct DDL/migration, index/query changes, or analysis.
- **Verify:** index type matches the access pattern; every version-specific
  claim is tagged with its range; a migration has a rollback path.

## References

- [`references/indexing-and-mvcc.md`](references/indexing-and-mvcc.md) — Tier-2 deep dive.
- Source list: see `skill.yaml.source_references` (PostgreSQL official docs,
  retrieved 2026-09-09, via `research/technologies/postgresql.md`).
