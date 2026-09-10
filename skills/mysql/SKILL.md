---
name: MySQL
description: >-
  MySQL-specific storage-engine choice, indexing, replication, authentication,
  and at-rest encryption. Use when the stack uses MySQL (mysql:// URL, mysql2/
  Connector driver, a MySQL-targeted ORM provider, or the task names MySQL/
  InnoDB/binlog/GTID/an LTS-to-LTS upgrade). Not for PostgreSQL/other engines,
  generic data modeling (use data-modeling), or ORM usage mechanics (use
  orm-integration).
spec_version: "1.0"
---

## Purpose & scope

Apply MySQL correctly for the version in use — storage-engine choice,
indexing, replication/HA topology, authentication, at-rest encryption, and
version-gated upgrade hazards. The *method* for designing the schema itself
comes from the parent skill ([data-modeling](../data-modeling/SKILL.md));
this skill supplies MySQL's concrete facts on top of that method. Deeper
query/index-tuning procedure beyond MySQL-specific facts belongs to
[database-operations](../database-operations/SKILL.md) (`SK-DATA-003`).

## When to use / When not to use

**Use** when a `mysql://` URL, a MySQL driver (`mysql2`, Connector/J,
Connector/Python, Connector/Node.js, Connector/ODBC, `libmysqlclient`), or a
MySQL-targeted ORM provider is present, or the task names a MySQL feature
(InnoDB, binlog, GTID, Group Replication, the Keyring) or a version upgrade.
**Do not use** for PostgreSQL/other engines (route to that engine's skill),
engine-agnostic schema design ([data-modeling](../data-modeling/SKILL.md)),
ORM mapping mechanics ([orm-integration](../orm-integration/SKILL.md)), or
evolving an already-populated schema's data
([data-migration](../data-migration/SKILL.md)).

## Knowledge

**Pluggable storage engines.** MySQL separates a server layer (connection
handling, auth, SQL parsing/optimization) from a pluggable storage-engine
layer that does the actual read/write; the engine is set per table via
`ENGINE=...`, and engines can be mixed within one database without changing
application SQL [Source: https://dev.mysql.com/doc/refman/9.7/en/pluggable-storage-overview.html].
Documented engines: **InnoDB** (default — transactional, row-level locking,
foreign keys), **MyISAM**, **MEMORY**, **CSV**, **ARCHIVE**, **BLACKHOLE**,
**MERGE**, and **FEDERATED** (remote table access), each suited to a
different workload shape [Source: https://dev.mysql.com/doc/refman/9.7/en/pluggable-storage-overview.html].

**Indexing.** The Optimization chapter's documented method: analyze the
actual plan with `EXPLAIN` before hand-tuning; index columns used in `WHERE`,
join, and `ORDER BY` clauses; let the optimizer's index-merge, condition-
pushdown, and hash-join capabilities do their job where applicable; monitor
via Performance Schema/`sys` schema rather than guessing
[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html]. Index
key-prefix limits are engine-specific (InnoDB: 3,072 bytes for
DYNAMIC/COMPRESSED row format, 767 bytes for REDUNDANT/COMPACT, scaled down
for smaller `innodb_page_size`), and InnoDB caps secondary indexes at 64 per
table and 16 columns per multi-column index
[Source: https://dev.mysql.com/doc/refman/9.7/en/innodb-limits.html].

**Replication.** Async by default: a **binary log** on the source, a
**relay log** on the replica, replication threads, and an optional metadata
repository [Source: https://dev.mysql.com/doc/refman/9.7/en/replication.html].
Formats: statement-based, row-based, mixed. Identity/positioning:
classic binlog-file-position or **GTID**, which the manual recommends for
new deployments as the more modern, position-independent approach
[Source: https://dev.mysql.com/doc/refman/9.7/en/replication.html]. For
multi-instance HA, **Group Replication** (single-primary or multi-primary)
provides membership/consistency but *not* client failover on its own; the
documented recommended production path wraps it as **InnoDB Cluster**
(Group Replication + MySQL Shell + MySQL Router), while **InnoDB
ReplicaSet** is recommended for non-HA async topologies and **MySQL NDB
Cluster** is the separate, shared-nothing product for true synchronous
replication [Source: https://dev.mysql.com/doc/refman/9.7/en/group-replication.html].

**Authentication.** Documented plugins: caching SHA-2, SHA-256, cleartext,
PAM, Windows native, LDAP, Kerberos, **OpenID Connect**, socket peer-
credential, and **WebAuthn**
[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html]. **Version-
sensitive (>=8.4.0):** `mysql_native_password` is disabled by default and
`default_authentication_plugin` was removed in favor of
`authentication_policy`; `authentication_fido*` plugins were replaced by
`authentication_webauthn`
[Source: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html].

**Versioning model (read before citing any version number).** MySQL 9.7 is
the last release on traditional `MAJOR.MINOR.PATCH` numbering; starting with
MySQL 26.7.0, Innovation releases switch to calendar-based `YY.M.P`
versioning [Source: https://blogs.oracle.com/mysql/a-more-predictable-mysql-release-model-calendar-versions-lts-and-innovation].
As of the July 2026 GA wave, MySQL 26.7.0 (Innovation), 9.7.2 LTS, and
8.4.11 LTS are all current simultaneously — old and new numbering schemes
coexist [Source: https://blogs.oracle.com/mysql/mysql-july-2026-ga-releases-now-available].
Upgrade paths cannot skip a bugfix/LTS series (5.7 → 8.0 → 8.4, never 5.7 →
8.4 direct), and Innovation-to-Innovation upgrades cannot skip across an LTS
boundary [Source: https://dev.mysql.com/doc/refman/9.7/en/upgrade-paths.html].
Deep 8.4.0 breaking-changes detail lives in
[references/8.4-breaking-changes.md](references/8.4-breaking-changes.md).

## Decision framework

1. **Storage engine (simplest first):** default to **InnoDB** — it's the
   documented default and the only one with transactions/row-level
   locking/foreign keys
   [Source: https://dev.mysql.com/doc/refman/9.7/en/pluggable-storage-overview.html].
   Deviate only for a workload the engine matrix actually fits: MyISAM/MEMORY
   for genuinely read-only or ephemeral data, ARCHIVE for compressed
   write-once history, CSV for interchange, MERGE/FEDERATED for the specific
   remote/multi-table access patterns they exist for. Don't pick a non-InnoDB
   engine "for speed" without a concrete, current reason — mixed-engine
   databases add operational complexity (backup/replication semantics differ
   per engine).
2. **Index strategy:** run `EXPLAIN` against the real query before adding an
   index; add the index the plan justifies (WHERE/join/ORDER BY columns),
   not a speculative one
   [Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html]. Prefer
   letting the optimizer's index-merge/hash-join do the work before hand-
   engineering a composite index; respect InnoDB's per-table/per-index limits
   when designing wide composite keys
   [Source: https://dev.mysql.com/doc/refman/9.7/en/innodb-limits.html].
3. **Replication/HA topology:** default to plain async (GTID-based) source/
   replica if the workload just needs read scaling or a warm standby
   [Source: https://dev.mysql.com/doc/refman/9.7/en/replication.html]. Escalate
   to InnoDB Cluster only when automatic failover is an actual requirement —
   raw Group Replication without Router/InnoDB Cluster leaves the
   application to implement its own failover
   [Source: https://dev.mysql.com/doc/refman/9.7/en/group-replication.html].
   Reach for NDB Cluster only when true synchronous replication is a hard
   requirement, given its distinct architecture.
4. **MySQL vs. PostgreSQL, when genuinely open:** the underlying research
   records **no documented head-to-head performance claim** between the two
   — each engine's performance section is self-referential, not comparative
   [Source: research/knowledge-maps/technology-decision-matrix.md §2,
   "Unresolved"]. Don't manufacture a performance argument either way.
   Real, documented differences to decide on instead: MySQL's pluggable-
   engine model and Keyring-based at-rest encryption
   (file/KMIP/AWS KMS/HashiCorp Vault backends) vs. PostgreSQL's native
   row-level security and richer built-in full-text search; MySQL has no
   documented RLS equivalent in the source data
   [Source: research/knowledge-maps/technology-decision-matrix.md §2]. Weigh
   team familiarity, existing ecosystem (managed-service availability,
   ORM/driver maturity for the stack), and which native security feature
   (Keyring vs. RLS) actually matches the requirement — not brand preference.
   If neither engine is already in play, this is an open decision belonging
   to [data-modeling](../data-modeling/SKILL.md)'s store-shape step, not a
   default to assert here.

## Workflow

1. Determine the MySQL version in use (server, image tag, or manifest) —
   required given the concurrent 8.4/9.7/26.x lines.
2. For a performance task, reproduce with `EXPLAIN` (JSON format for detail)
   before proposing a change
   [Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html].
3. Apply the smallest change that addresses the observed plan/requirement:
   an index, an engine choice, a replication-topology change, or an
   auth/encryption setting.
4. For schema/engine changes, produce a reversible migration and hand
   rollout discipline to [data-migration](../data-migration/SKILL.md).
5. For a version upgrade, check the target against the no-skip-a-series
   restriction and any version-gated breaking change (see References) before
   proposing the path.
6. Verify (below) before declaring done.

## Engineering rules

- Read the actual `EXPLAIN` plan before adding an index; don't index on a
  guess [Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html].
- Default to InnoDB; name the concrete reason before choosing a different
  engine for any table.
- Prefer GTID-based replication for any new replication topology over
  classic binlog-position tracking
  [Source: https://dev.mysql.com/doc/refman/9.7/en/replication.html].
- Never assume "latest" MySQL behavior implicitly — state the version the
  guidance targets, given three concurrently-supported lines (8.4 LTS, 9.7
  LTS, 26.x Innovation).
- Before any upgrade crossing into 8.4+, check for `AUTO_INCREMENT` on
  `FLOAT`/`DOUBLE` columns and alter them first — the manual states such a
  table "cannot be upgraded" otherwise
  [Source: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html].
- Run the MySQL Shell Upgrade Checker Utility before any in-place upgrade,
  and upgrade replicas before the source in a replicated topology
  [Source: https://dev.mysql.com/doc/refman/9.7/en/upgrade-paths.html].

## Trade-offs

- Pluggable storage engines give per-table workload fit (e.g. ARCHIVE for
  compressed history) but mixed-engine databases complicate backup and
  replication semantics, which are engine-dependent — most schemas are
  simpler and safer staying all-InnoDB.
- InnoDB Cluster gives automatic failover but adds MySQL Shell/Router as
  extra operational surface versus plain async replication; only worth it
  once automatic failover is an actual requirement, not a default.
- GTID replication simplifies failover/topology changes over classic
  position-based replication but requires every server in the topology to
  support it consistently.

## Anti-patterns

- **Relying on full table scans instead of appropriate indexes, and using
  overly wide/inefficient data types** — the optimization chapter's
  "Database Structure Optimization"/"Data Type Optimization" sections exist
  specifically to correct this
  [Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html].
- **Adding indexes speculatively "for performance"** without an `EXPLAIN`
  plan justifying them — the domain's over-engineering trap; write
  amplification and wasted space are the cost.
- **Leaving `LOAD DATA LOCAL` enabled without restriction** — documented as
  a security risk in the manual's General Security Issues section
  [Source: https://dev.mysql.com/doc/refman/9.7/en/security.html].
- **`AUTO_INCREMENT` on `FLOAT`/`DOUBLE` columns** — deprecated since 8.0,
  removed as an error in 8.4+; don't create new columns this way, and audit
  for it before any 8.4+ upgrade
  [Source: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html].
- **Running raw Group Replication in production without Router/InnoDB
  Cluster**, then being surprised there's no client failover — the manual is
  explicit that Group Replication alone doesn't provide it
  [Source: https://dev.mysql.com/doc/refman/9.7/en/group-replication.html].
- **Skipping a bugfix/LTS series on upgrade** (e.g. attempting 5.7 → 8.4
  directly) — explicitly unsupported
  [Source: https://dev.mysql.com/doc/refman/9.7/en/upgrade-paths.html].

## Security

Documented authentication plugins include caching SHA-2, SHA-256, PAM,
LDAP, Kerberos, OpenID Connect, and WebAuthn, with `mysql_native_password`
disabled by default as of 8.4.0
[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html]. Access
control is privilege-based at global/database/table/column granularity plus
role-based access control, account locking, per-account resource limits,
multifactor authentication, and partial revokes
[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html].
At-rest encryption is via the **Keyring**, with file-based, KMIP, AWS KMS,
HashiCorp Vault, and OCI Vault backends
[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html] — note this
has no direct RLS equivalent documented for MySQL in the source data
[Source: research/knowledge-maps/technology-decision-matrix.md §2]. Audit
logging has moved from the deprecated Enterprise Audit Plugin to the Audit
Log Component; Connection Control mitigates brute-force login attempts, and
the Password Validation Component enforces password strength
[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html]. For the
full threat model (injection, secrets, transport) beyond MySQL-specific
mechanisms, defer to `SK-QA-002` — not restated here (no-duplication rule
QR-2).

## Performance

The **InnoDB buffer pool** is documented as the primary tunable for InnoDB
performance/memory configuration
[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html]. `EXPLAIN`
(including JSON format) is the primary tool for understanding the
optimizer's chosen plan, with optimizer hints and index hints as the
override mechanism when it picks a suboptimal one
[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html]. No
official numeric "buffer pool as X% of RAM" rule was found in the docs —
treat any such percentage as community guidance, not an official threshold
[Source: research/technologies/mysql.md §8, "Unresolved"]. Performance
Schema and the `sys` schema are the documented facilities for runtime
monitoring beyond static `EXPLAIN` analysis
[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html]. Deeper
cross-cutting performance method is owned by `SK-QA-003`.

## Testing

**Documented gap:** the MySQL Reference Manual's own test framework (the
MySQL Test Suite, driven by `mysql-test-run.pl`) is scoped to testing the
**MySQL server codebase itself**, not "how to test your application's use
of MySQL"
[Source: https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_MYSQL_TEST_RUN_PL.html].
No first-party application-testing guidance (ephemeral test databases,
fixtures, transactional test isolation) exists in the official docs for
this dimension — this mirrors the same gap already noted for PostgreSQL in
[data-modeling](../data-modeling/SKILL.md#testing). Application-level test
strategy for MySQL-backed code should come from the ORM/framework layer
instead; deep test-strategy method is owned by `SK-QA-001`.

## Failure handling

- If the MySQL version cannot be determined, ask for it or state the
  version its guidance assumes; never assume "latest" silently — this
  matters more than usual given the concurrent 8.4/9.7/26.x numbering.
- If shell is unavailable/denied, degrade to advisory DDL/engine/index
  output and state that `EXPLAIN` or the migration was not run.
- If a claim would depend on the still-unresearched 9.7→26.x breaking-
  changes page, say "verify against current 26.x release notes" rather than
  assert behavior by analogy to the 8.0→8.4 transition.

## Escalation

- A destructive migration (`DROP`/data-losing `ALTER`), a storage-engine
  change on a populated table, or an in-place major-version upgrade
  requires explicit user confirmation before execution (defer to
  [data-migration](../data-migration/SKILL.md) rollout discipline).

## Outputs & verification

- **Outputs:** version-correct DDL/migration, storage-engine or index
  changes, or analysis (engine choice, replication topology, upgrade plan)
  with rationale and applicable version.
- **Verify:** the index matches the actual `EXPLAIN` plan; the storage
  engine is justified against the table's real workload; every
  version-specific claim is tagged with its range; an upgrade path respects
  the no-skip-a-series rule and the FLOAT/DOUBLE `AUTO_INCREMENT`
  pre-upgrade check when crossing into 8.4+.

## References

- [references/8.4-breaking-changes.md](references/8.4-breaking-changes.md)
  — Tier-2: the full documented 8.4.0 breaking-changes list.
- Source list: see `skill.yaml.source_references` (MySQL Reference Manual
  and Oracle MySQL blog, retrieved 2026-09-09, via
  `research/technologies/mysql.md`, `research/knowledge-maps/version-matrix.md`,
  and `research/knowledge-maps/technology-decision-matrix.md`).

**Unresolved (carried from research, do not paper over):**
- No official "Changes in MySQL 9.x" or "Changes in MySQL 26.7.0"
  breaking-changes page was located; only the 8.0→8.4 transition is
  enumerated here. Treat any 8.4→9.7 or 9.7→26.x claim as unverified.
- Whether MySQL 9.7 LTS itself is eventually renumbered under calendar
  versioning, or stays a permanent legacy-numbered LTS line, is not stated
  in the docs.
- Exact EOL dates for 8.4 LTS/9.7 LTS were derived from a search summary of
  `mysql.com/support/eol-notice.html`, not a direct fetch showing both
  dates verbatim — re-verify before treating as load-bearing.
- No official numeric InnoDB-buffer-pool-as-%-of-RAM recommendation was
  found; don't present a specific percentage as an official rule.
- X DevAPI/C API compatibility and versioning guarantees were not fully
  verified against a dedicated compatibility-policy page.
- Official Kubernetes/MySQL Operator deployment documentation was not
  independently verified.
