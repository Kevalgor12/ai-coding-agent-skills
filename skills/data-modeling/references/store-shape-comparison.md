# Store-shape comparison (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Condensed from
[technology-decision-matrix.md §2](../../../research/knowledge-maps/technology-decision-matrix.md)
— consult that document directly for the full citation trail; this file is a
quick-reference distillation, not a replacement.

| | PostgreSQL | MySQL | MongoDB | ClickHouse |
|---|---|---|---|---|
| Model | Relational (SQL), MVCC | Relational (SQL) | Document (BSON) | Columnar OLAP |
| Transaction model | Full ACID, 4 isolation levels via MVCC/SSI | Full ACID (InnoDB) | Atomic single-document; multi-doc ACID since 4.0 (replica sets) / 4.2 (sharded) | **No general transaction support** — deliberate trade-off |
| Row/document-level security | Native RLS, fails closed with no policy | Not documented | RBAC documented but **not on by default** (self-managed) | Row Policies (1 of 5 RBAC entity types) |
| Documented anti-pattern | Restoring `pg_dump` from an untrusted source (dumps contain superuser-executed code) | Full table scans / overly wide data types | Excessive `$lookup` — a signal to denormalize instead | Nullable(T) columns — hidden is-null mask hurts perf on every access |
| App-level testing guidance | **Explicit gap** — delegated to ORMs/tooling | **Explicit gap** — no first-party guidance | Documents a lightweight replica-set-for-testing topology + official Docker image | Tests ClickHouse itself, not app code against it |
| Positioned as migration target of | — | — | (from Postgres/MySQL/Oracle/SQL Server, via Relational Migrator) | (from Postgres/MySQL, once workload shifts OLTP→OLAP) |

## When each shape tends to fit

- **PostgreSQL** — default choice for transactional systems with real
  cross-entity invariants, need for native RLS, or built-in full-text search
  without adding a separate search engine.
- **MySQL** — comparable relational fit to PostgreSQL; consider when the
  operational ecosystem (hosting, team familiarity, existing tooling) already
  favors it — the research does not document a performance reason to prefer
  one over the other for equivalent OLTP workloads.
- **MongoDB** — aggregate-oriented data (a document that's almost always read/
  written as a whole), schema that genuinely varies per record, or a team
  that needs to move fast on an evolving shape before it stabilizes enough to
  normalize. Not a good fit for data with many enforced cross-entity invariants.
- **ClickHouse** — analytical/aggregate queries at volume, once (not before)
  they'd otherwise degrade an OLTP store. Virtually never the *only* store in
  a system — it complements a transactional primary rather than replacing it.

## Synthesis note

The research's own cross-cutting synthesis frames these four as points on a
**normalization-tolerance spectrum**: PostgreSQL/MySQL optimize for
normalized, joined, transactional correctness; MongoDB's own guidance steers
toward embedding over joining; ClickHouse abandons transactional/point-query
support entirely for analytical scan speed
[Source: technology-decision-matrix.md §2, cross-cutting synthesis]. No
single technology in this set is positioned as strictly "better" — each
trades a different set of guarantees for a different access pattern.
