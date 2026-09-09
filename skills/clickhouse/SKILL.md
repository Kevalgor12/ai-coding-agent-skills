---
name: ClickHouse
description: >-
  ClickHouse-specific columnar OLAP: MergeTree engine family, sparse
  primary-key indexing (1 mark per ~8,192-row granule), partitioning,
  batch/async insert strategy, SQL-driven RBAC (5 entity types), and
  version-gated 26.x behavior (max_insert_threads auto-parallel as of 26.8).
  Use once analytical load is actually degrading an OLTP primary. Not for
  the store-shape decision itself (data-modeling), OLTP schema/query design
  (PostgreSQL/MySQL), or "for analytics later" premature adoption.
spec_version: "1.0"
---

## Purpose & scope

ClickHouse is a **complementary OLAP (analytical) store, not a general-purpose
replacement** for a transactional primary [Source:
https://clickhouse.com/docs]. This skill applies ClickHouse correctly once it
is (or is being seriously evaluated as) part of the stack: MergeTree
table-engine design, sparse primary-key indexing, partitioning, insert
strategy, and SQL-driven RBAC. It does **not** own the question of *whether*
a columnar store is warranted at all — that decision belongs to
[data-modeling](../data-modeling/SKILL.md) (`SK-DATA-001`), which this skill
treats as already settled. Generic cross-engine query-tuning/indexing/
transaction method is owned by `SK-DATA-003` (database-operations), the
skill's formal taxonomy parent — a **forward reference**: `SK-DATA-003` is
not yet authored anywhere in this library, so this skill supplies
ClickHouse's concrete specifics standalone rather than delegating to it.

## When to use / When not to use

**Use** when a ClickHouse client/driver, connection config, or
`clickhouse-server`/`clickhouse-local`/chDB reference is present, when the
task names ClickHouse or a ClickHouse-specific feature (MergeTree, `ORDER BY`
primary key, partitioning key, skip index, `async_insert`, ClickHouse
Keeper), or when an existing OLTP primary (PostgreSQL/MySQL) has analytical/
aggregate query load that is **demonstrably** degrading it and adding
ClickHouse is being evaluated.

**Do not use** — and do not recommend adopting ClickHouse — when no
analytical load has actually degraded the primary store yet ("we might need
analytics later" is premature adoption; this is the domain's central
overengineering trap, see Anti-patterns). Route a still-open store-shape
question to `SK-DATA-001`; route OLTP schema/query design with no ClickHouse
in play to `SK-TECH-postgresql`/`SK-TECH-mysql`; route generic cross-engine
tuning method with ClickHouse not actually in the stack to `SK-DATA-003`
(forward reference).

## Knowledge

- **Columnar storage** is the defining idea: data is physically organized by
  column, so a query touching a few columns of a wide table reads only those
  columns from disk. The docs illustrate a 100M-row scan across a handful of
  columns completing "within milliseconds," at throughput "approximately over
  1 billion rows per second" [Source: https://clickhouse.com/docs].
- **MergeTree** is the primary table-engine family, "engineered for high data
  ingest rates and huge data volumes." Storage hierarchy: table →
  **partitions** → **parts** → **granules** → rows. `INSERT` creates a new
  immutable part sorted by the `ORDER BY`/primary key; a background **merge**
  process periodically combines parts within the same partition (parts in
  different partitions never merge) [Source:
  https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree].
  Two on-disk part layouts exist: **wide** (one file per column, default for
  larger parts) and **compact** (all columns in one file, for small/frequent
  parts) [same source].
- **Sparse primary index**: rows are grouped into **granules** of (by
  default) ~8,192 rows, and the index stores **one mark per granule**, not
  per row — this keeps the index small enough to stay memory-resident even
  for huge tables, at the cost of being comparatively inefficient for
  single-row point queries by key [Source:
  https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree;
  https://clickhouse.com/docs/en/introduction/features_considered_disadvantages].
- **Partitioning** splits data by an arbitrary expression (commonly a time
  bucket) to enable partition pruning and cheap lifecycle operations
  (drop/move whole partitions). The docs are explicit: "partitioning does not
  speed up queries" in general — it is a data-management tool, not a
  query-acceleration tool [Source:
  https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree].
- **RBAC** is SQL-driven across **five entity types**: Users, Roles, Row
  Policies (per-row filtering), Settings Profiles, and Quotas. Privilege
  grants are hierarchical; there is **no privilege "lifetime"** — privileges
  on a dropped table persist until explicitly revoked [Source:
  https://clickhouse.com/docs/operations/access-rights].
- **Deployment forms**: five packagings share the same engine — ClickHouse
  Server, ClickHouse Cloud, ClickHouse CLI, `clickhouse-local` (no server
  process, ad-hoc local/cloud-storage analysis), and chDB (in-process,
  embedded, Pandas/Arrow-integrated) [Source:
  https://clickhouse.com/docs/get-started/about/deployment-modes].
- **[Version-sensitive, >=26.8]** `26.8` is the current documented **LTS**
  release (2026-08-27); LTS ships twice yearly (historically March/August)
  with ≥1-year support, current and prior LTS overlapping. **Stable**
  releases publish monthly, with the three most recent getting bug-fix
  support, and Stable — not LTS — is the documented default recommendation
  for production [Source:
  https://clickhouse.com/docs/resources/changelogs/oss/2026;
  https://clickhouse.com/docs/faq/operations/production]. **Unresolved**: the
  exact support-duration wording ("3 releases," "1-year overlap") was
  obtained via a search summary of the legal support-policy page, not a
  directly fetched full-text page — treat as needing re-verification before
  citing as precise SLA language.
- **[Version-sensitive, >=26.8]** `max_insert_threads` default changed from
  `1` to `auto`, meaning `INSERT SELECT` is now parallelized by default — a
  **breaking change** affecting resulting part creation and row ordering
  versus prior versions' single-threaded-by-default behavior [Source:
  https://clickhouse.com/docs/resources/changelogs/oss/2026]. State this
  explicitly whenever advising on an upgrade crossing this boundary.
- **[Version-sensitive, >=26.2]** `tokenbf_v1`/`ngrambf_v1` Bloom-filter
  skip-index types are deprecated [Source:
  https://clickhouse.com/docs/best-practices/use-data-skipping-indices-where-appropriate].

Comparative context vs. PostgreSQL/MySQL/MongoDB (transaction model, RBAC,
documented anti-patterns) is pre-researched in
[technology-decision-matrix.md §2](../../research/knowledge-maps/technology-decision-matrix.md#2-database-model-postgresql-vs-mysql-vs-mongodb-vs-clickhouse)
and condensed in
[data-modeling's store-shape reference](../data-modeling/references/store-shape-comparison.md)
— use those rather than re-deriving the comparison here.

## Decision framework

This skill does **not** re-litigate whether a columnar store is warranted —
that method lives in `SK-DATA-001`'s decision framework (dominant access
pattern, consistency needs, whether normalization is buying anything, and
whether a second specialized store solves a problem the primary can't). Once
ClickHouse is the settled second store, the ClickHouse-specific choices are:

1. **Table engine and `ORDER BY` key**: choose the `ORDER BY`/primary key
   from the actual filter/aggregation pattern, not a default — it directly
   determines granule-mark efficiency [Source:
   https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree].
2. **Partitioning key**: start **without** partitioning; add a low-cardinality
   key (docs suggest fewer than 100–1,000 distinct values) only for a
   demonstrated data-lifecycle need (retention, tiered storage), never as a
   first-resort query optimization [Source:
   https://clickhouse.com/docs/best-practices/choosing-a-partitioning-key].
3. **Insert strategy**: batch client-side (10,000–100,000 rows/insert
   ideal) when the producer can batch; use `async_insert=1` (with
   `wait_for_async_insert=1` for durability) when it can't (e.g. many
   small-payload observability agents) [Source:
   https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy].
4. **Data skipping indices**: add only after primary-key design and
   materialized views have been considered — a misaligned skip index adds
   overhead without benefit [Source:
   https://clickhouse.com/docs/best-practices/use-data-skipping-indices-where-appropriate].
5. **Version gate**: confirm the ClickHouse version before recommending
   version-gated behavior — the `max_insert_threads` auto-parallelism change
   at 26.8 alone can silently change part creation and row ordering if
   assumed rather than confirmed (rule VA-3).

## Workflow

1. Confirm the store-shape decision is already settled (`SK-DATA-001`) and
   that analytical load is real, not anticipated — otherwise stop and
   escalate to that decision instead of proceeding (see Failure handling).
2. Determine the ClickHouse version (server, Cloud, or image tag).
3. Design the MergeTree table: engine variant, `ORDER BY` key, `PARTITION
   BY` (only if lifecycle-justified), and data types (avoiding `Nullable`
   by default — see Anti-patterns).
4. Design the insert path: batch sizing or `async_insert` configuration
   matching the producer's actual write pattern.
5. Add skip indices only if a specific, observed query pattern justifies
   them, following the documented workflow (Diagnose → Isolate → Optimize)
   [Source: https://clickhouse.com/docs/optimize/query-optimization].
6. Configure RBAC (Users/Roles/Row Policies/Settings Profiles/Quotas) for
   the access the table needs.
7. Verify (below) before declaring done.

## Engineering rules

- Never recommend adding ClickHouse before analytical load has actually
  degraded the OLTP primary — verify this with the caller rather than assume
  it (ties to `SK-DATA-001`'s overengineering guard).
- Choose the `ORDER BY`/primary key from the real access pattern; a longer
  key costs more at insert time and in memory [Source:
  https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree].
- Batch inserts (10,000–100,000 rows) or use async inserts; never send many
  small, frequent inserts — they create excess parts and background-merge
  pressure, potentially producing "too many parts" errors [Source:
  https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy].
- Prefer denormalization (shifting join work to insert time) over deep JOIN
  chains; keep JOIN count to roughly 3–4 per query [Source:
  https://clickhouse.com/docs/best-practices/minimize-optimize-joins].
- Avoid `Nullable(T)` by default; use a sensible sentinel default instead,
  reserving `Nullable` for a genuine "empty vs. absent" business requirement
  (see Anti-patterns).
- Always state the ClickHouse version a piece of guidance targets; never
  assume "latest" silently (rule VA-3).
- Stay under the documented scale ceilings — 1,000 databases, 5,000 tables,
  50,000 partitions, 100,000 parts per service — since table/partition/part
  count (not database count) affects server startup time [Source:
  https://clickhouse.com/docs/knowledgebase/maximum_number_of_tables_and_databases].

## Trade-offs

ClickHouse **deliberately abandons general transaction support and efficient
point-queries/row-updates in exchange for columnar analytical scan speed** —
an explicit design trade-off stated in its own docs, not a limitation to
work around [Source:
https://clickhouse.com/docs/en/introduction/features_considered_disadvantages].
Concretely: no full/general-purpose transaction support; cannot efficiently
modify or delete already-inserted rows at high rate/low latency (batch-style
cleanup, e.g. for GDPR, is supported — that is different from OLTP-style row
updates); and the sparse primary index makes single-row point-lookup queries
comparatively inefficient by design. This is exactly why ClickHouse is
positioned as a **second** store alongside an OLTP primary rather than a
replacement — the primary keeps transactional/point-query workloads, and
ClickHouse takes the scan/aggregate-heavy analytical ones. Async inserts
trade slightly higher latency-to-visibility for server-side buffering
efficiency; batching client-side trades producer-side complexity for lower
per-insert overhead.

## Anti-patterns

- **Adding ClickHouse before analytical load actually justifies it** — the
  domain's central over-engineering trap. `SK-DATA-001` already calls this
  out generically ("for later" store bolting); the ClickHouse-specific
  version is treating "we might do analytics eventually" as sufficient
  justification for a second operational system with its own deployment,
  RBAC, and upgrade discipline.
- **Reflexive `Nullable(T)` usage**: stores a hidden `UInt8` "is-null" mask
  processed on every access, and "almost always negatively affects
  performance" — use a sensible default instead unless distinguishing
  "empty" from "genuinely absent" is a real business requirement [Source:
  https://clickhouse.com/docs/optimize/avoid-nullable-columns].
- **Frequent/large-scale mutations** (`ALTER TABLE ... UPDATE`/`DELETE`):
  rewrite entire affected data parts, causing disk I/O spikes even for small
  logical changes; cannot be undone once submitted; persist across restarts
  unless explicitly cancelled; can produce inconsistent reads mid-mutation.
  Use `ReplacingMergeTree`/`CollapsingMergeTree` engines, lightweight
  deletes, or dropping whole partitions instead [Source:
  https://clickhouse.com/docs/best-practices/avoid-mutations].
- **`OPTIMIZE TABLE ... FINAL`**: ClickHouse performs smart background
  merges automatically; forcing `FINAL` is unnecessary and costly absent a
  specific need [Source: https://clickhouse.com/docs/best-practices].
- **Choosing a high-cardinality partitioning key**, or partitioning
  primarily to speed up queries rather than for data-lifecycle management —
  both risk fragmenting data into too many parts [Source:
  https://clickhouse.com/docs/best-practices/choosing-a-partitioning-key].
- **Sending many small, frequent inserts** instead of batching or using
  async inserts [Source:
  https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy].
- **Dictionary misuse for many-to-many relationships** — dictionaries
  silently deduplicate keys and can silently drop data [Source:
  https://clickhouse.com/docs/best-practices/minimize-optimize-joins].

## Security

Access control is **RBAC-based** across **five entity types**: Users
(authenticate; hold privileges/allowed hosts/roles/default settings), Roles
(bundle privileges/settings/nested roles), Row Policies (per-user/role
row-level filtering at read time), Settings Profiles (configuration-
constraint bundles), and Quotas (resource-consumption limits per time
interval). Two parallel, simultaneously-usable configuration paths exist:
the recommended **SQL-driven workflow** (`CREATE USER`, `GRANT`, `REVOKE`)
and traditional config-file management (`users.xml`/`config.xml`); a site can
migrate smoothly from one to the other. Privilege grants are hierarchical;
delegating a grant requires `WITH GRANT OPTION`; and critically, there is
**no privilege "lifetime"** — privileges on a dropped table persist and must
be explicitly revoked, not something that lapses automatically [Source:
https://clickhouse.com/docs/operations/access-rights]. Sensitive
configuration values (e.g. connection secrets) can be stored encrypted via
symmetric-encryption codecs using the `encrypted_by` attribute, with
`hide_in_preprocessed="true"` keeping them out of the server's generated
preprocessed config [Source:
https://clickhouse.com/docs/operations/configuration-files]. **Unresolved**:
exact LDAP/Kerberos external-authenticator support and NIST-800-63B
password-policy/SSH-auth claims were only surfaced via search-result
summaries in the source research, not a directly fetched full-text official
page — treat as needing re-verification, don't assert specifics. For the
full cross-cutting threat model (injection defense, secrets handling beyond
config-file encryption, transport security), defer to `SK-QA-002` — not
restated here (rule QR-2).

## Performance

Core levers live in MergeTree design: the **sparse primary index** (1 mark
per ~8,192-row granule by default) keeps the index memory-resident even for
huge tables [Source:
https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree];
**partition pruning** skips whole irrelevant partitions; **background
merges** produce fewer, larger parts that read faster. **Insert strategy is
a first-class, separately documented performance concern**: batch
10,000–100,000 rows per insert (minimum ~1,000), keep insert-query frequency
around ~1/second, and use `async_insert=1` (with `wait_for_async_insert=1`
for durability) when client-side batching isn't feasible [Source:
https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy].
**[Version-sensitive, >=26.8]** `max_insert_threads` now defaults to `auto`
rather than `1`, parallelizing `INSERT SELECT` by default — a real
performance change, but also a breaking one for part creation and row
ordering versus older versions; confirm the version before assuming this
behavior [Source: https://clickhouse.com/docs/resources/changelogs/oss/2026].
The documented query-optimization workflow (Diagnose → Isolate → Optimize)
emphasizes evidence-driven changes over speculative tuning [Source:
https://clickhouse.com/docs/optimize/query-optimization]. Cross-cutting
performance method beyond ClickHouse specifics is owned by `SK-QA-003`.

## Testing

**Documented gap, real and citable**: ClickHouse's own test suite
(functional `.sql`/`.sh` tests, Docker-based integration tests, `gtest` unit
tests, performance/stress tests, sanitizers, fuzzing) tests **ClickHouse
itself** — the database's own source code — not application code written
against it [Source:
https://clickhouse.com/docs/resources/develop-contribute/contribute/tests].
No official, application-level "how to test code that talks to ClickHouse"
guide (test-container patterns, mocking strategy) was located in the source
research. Don't assume first-party app-testing guidance exists; app-level
test strategy is owned by `SK-QA-001` and is not restated here. ClickHouse's
own random-data-generation SQL functions are documented as often sufficient
for generating synthetic test data without an external generator [Source:
https://clickhouse.com/docs/guides/generating-test-data].

## Failure handling

- If it is unclear whether analytical load is actually degrading the OLTP
  primary (vs. anticipated future need), ask rather than recommending
  ClickHouse adoption preemptively.
- If the ClickHouse version cannot be determined, ask for it or explicitly
  state the version the guidance assumes — never assume "latest" silently
  (rule VA-3); this is consequential given the `max_insert_threads` change
  at 26.8.
- If shell is unavailable or denied, degrade to advisory DDL/insert-config
  output and state that it was not actually executed.

## Escalation

- Enabling `ALTER TABLE ... UPDATE`/`DELETE` (mutations) at scale, or
  dropping a partition, requires explicit user confirmation before
  execution — mutations rewrite whole data parts, cannot be undone once
  submitted, and persist across restarts unless cancelled [Source:
  https://clickhouse.com/docs/best-practices/avoid-mutations].
- A cluster upgrade spanning more than a year of releases, or any downgrade
  attempt after newer-version features have already been used, requires an
  explicit stepping-stone plan and user confirmation — downgrades are only
  supported to versions less than a year old, and only if no newer features
  were used [Source: https://clickhouse.com/docs/operations/update].

## Outputs & verification

- **Outputs:** version-correct MergeTree table DDL, insert-strategy or
  query/skip-index changes, RBAC configuration, or analysis with rationale;
  CLI commands actually run (`clickhouse-client`/`clickhouse-local`) when
  shell is available.
- **Verify:** the table engine and `ORDER BY`/primary key match the actual
  access pattern, not a default choice; insert strategy follows the
  documented sizing guidance rather than many small synchronous inserts;
  every version-specific claim is tagged with the range it holds for;
  `Nullable(T)` usage is justified by a genuine "empty vs. absent"
  requirement.

## References

- Source list: see `skill.yaml.source_references` (ClickHouse official
  docs, retrieved 2026-09-09, via `research/technologies/clickhouse.md`;
  plus `research/knowledge-maps/technology-decision-matrix.md` and
  `research/knowledge-maps/version-matrix.md`).
- [research/technologies/clickhouse.md](../../research/technologies/clickhouse.md) — full primary research, including breaking changes, limitations, and unresolved items (doc-site URL churn, LDAP/Kerberos specifics, exact Stable/LTS support-duration wording).
- [Technology Decision Matrix §2](../../research/knowledge-maps/technology-decision-matrix.md#2-database-model-postgresql-vs-mysql-vs-mongodb-vs-clickhouse) — PostgreSQL vs. MySQL vs. MongoDB vs. ClickHouse comparison.
- [data-modeling](../data-modeling/SKILL.md) (`SK-DATA-001`) — owns the store-shape decision this skill assumes is already settled.
