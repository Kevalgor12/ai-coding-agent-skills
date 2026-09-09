# PostgreSQL — Technology Research

Research date: 2026-09-09. Primary source: `postgresql.org/docs/current/*` (canonical documentation host — confirmed reachable and current; no evidence of a doc-host migration for PostgreSQL, unlike some other projects). Version-specific pages (e.g. `/docs/18/...`, `/docs/release/18.6/...`) and `postgresql.org/support/versioning/`, `postgresql.org/about/news/*` were also used. All claims are tagged per this project's convention: `[Source: <url>]` for documented facts, `[Inference, not confirmed in docs]` for reasoning, "Not documented / could not verify" where docs did not cover something, and "Unresolved: ..." where confidence is genuinely low.

**Doc host note**: [Source: https://www.postgresql.org/docs/current/release.html] The canonical docs URL pattern is `postgresql.org/docs/<major-version-or-"current">/<page>.html`. `current` always aliases to the latest stable major version's docs (PostgreSQL 18 at the time of this research). No migration away from `postgresql.org` was found; this differs from some adjacent projects in this library's research set that have moved doc hosts.

---

## 1. Core concepts

[Source: https://www.postgresql.org/docs/current/mvcc-intro.html] PostgreSQL uses **Multiversion Concurrency Control (MVCC)** as its concurrency model: each SQL statement sees a snapshot of data as it existed at a point in time, so readers never block writers and writers never block readers. This is the central concept underlying nearly all of PostgreSQL's transactional behavior.

[Source: https://www.postgresql.org/docs/current/wal-intro.html] **Write-Ahead Logging (WAL)** is the mechanism ensuring durability and crash recovery: "changes to data files ... must be written only after those changes have been logged, that is, after WAL records describing the changes have been flushed to permanent storage." WAL also underlies PostgreSQL's physical replication, point-in-time recovery (PITR), and online backup capabilities.

[Source: https://www.postgresql.org/docs/current/transaction-iso.html] PostgreSQL supports the four SQL-standard **transaction isolation levels** (Read Uncommitted, Read Committed, Repeatable Read, Serializable) but implements only three distinct behaviors internally: Read Uncommitted is aliased to Read Committed (no separate implementation exists); Repeatable Read and Serializable are both built on Snapshot Isolation, with Serializable additionally performing Serializable Snapshot Isolation (SSI) with predicate locking to detect and prevent serialization anomalies. Read Committed is the default. PostgreSQL's Repeatable Read prevents phantom reads, exceeding the SQL standard's minimum guarantee for that level.

[Source: https://www.postgresql.org/docs/current/datatype.html] PostgreSQL documents a large built-in type system, including: numeric types (`smallint`/`integer`/`bigint`, arbitrary-precision `numeric`/`decimal`, `real`/`double precision`, `serial`/`bigserial`), `money`, character types (`char(n)`, `varchar(n)`, `text`), `bytea` binary data, date/time types (`date`, `time`, `timestamp`, with/without time zone, `interval`), `boolean`, geometric types (`point`, `line`, `box`, `polygon`, `circle`, etc.), network types (`inet`, `cidr`, `macaddr`), bit strings, full-text search types (`tsvector`/`tsquery`), `json`/`jsonb`/`jsonpath`, `uuid`, `xml`, arrays (of any base type, multi-dimensional), composite (row) types, range and multirange types, domains (user-defined constrained types), and PostgreSQL-internal types like `oid`, `pg_lsn`, `pg_snapshot`.

[Source: https://www.postgresql.org/docs/current/routine-vacuuming.html] Because MVCC does not physically remove old row versions on `UPDATE`/`DELETE`, PostgreSQL requires periodic **VACUUM** to reclaim space, update planner statistics, maintain the visibility map (for index-only scans), and — critically — prevent 32-bit transaction ID ("XID") wraparound by freezing old rows. This XID-wraparound-avoidance requirement is a PostgreSQL-specific architectural concept with no close analog in many other RDBMSes.

[Source: https://www.postgresql.org/docs/current/extend-extensions.html] **Extensions** are PostgreSQL's first-class mechanism for packaging related SQL objects (types, functions, operators, index access methods) as a single unit installed via `CREATE EXTENSION`, tracked by `pg_dump`/`pg_upgrade` as a unit rather than as loose objects.

---

## 2. Architecture

[Source: https://www.postgresql.org/docs/current/tutorial-arch.html] PostgreSQL uses a **client/server, process-per-connection** architecture: a supervisor process (informally "postmaster") runs continuously, listening for incoming connections. On each new client connection the postmaster **forks a dedicated backend process** for that connection; client and backend then communicate directly without further supervisor involvement until the connection closes. "The supervisor server process is always running, waiting for client connections, whereas client and associated server processes come and go." Client and server can be on different machines, communicating over TCP/IP.

[Source: https://www.postgresql.org/docs/current/overview.html] Chapter 51 of the manual ("Overview of PostgreSQL Internals") documents the query-processing pipeline inside a backend process: connection establishment → parser stage → rewrite/rule system → planner/optimizer → executor. [Inference, not confirmed in docs] This chapter is aimed at developers extending PostgreSQL internals rather than application developers, based on its framing as "an overview of the internal structure of the backend."

[Source: https://www.postgresql.org/docs/current/wal-intro.html] WAL records are flushed to durable storage before corresponding data-file changes, giving crash recovery via WAL replay ("REDO") and enabling checkpoints to lag behind actual writes without risking durability.

Not documented / could not verify in the pages fetched: a single consolidated diagram/description of shared memory structures (shared buffers, lock tables, etc.) — the fetched `tutorial-arch.html` page explicitly does not cover shared memory in the excerpt retrieved; that detail lives in other internals chapters not fetched in this pass.

---

## 3. APIs

[Source: https://www.postgresql.org/docs/current/external-interfaces.html] PostgreSQL's own distribution officially includes and documents exactly two client programming interfaces: **libpq** (the C client library, Chapter 32 — the foundation most other language drivers are built on) and **ECPG** (embedded SQL in C, Chapter 34, included in core because it's sensitive to server-side SQL grammar changes). All other language bindings (Python, Java/JDBC, Node.js, Go, Ruby, PHP, etc.) are explicitly **external projects**, not maintained by the PostgreSQL Global Development Group, and may carry different licenses; the docs point to the community wiki's driver list rather than documenting them directly.

[Source: https://www.postgresql.org/docs/current/protocol.html] The **frontend/backend wire protocol** (Chapter 54) is itself a documented API surface: a message-based protocol over TCP/IP (default port 5432) or Unix domain sockets. [Version-sensitive] Protocol version **3.2** was introduced in PostgreSQL 18; protocol version 3.0 (PostgreSQL 7.4+) remains supported for backward compatibility. The protocol chapter covers startup/auth sequences, simple and extended query flows, pipelining, COPY, SASL authentication (including SCRAM-SHA-256 and OAUTHBEARER), SSL/GSSAPI encryption negotiation, and both physical and logical streaming-replication sub-protocols.

[Source: https://www.postgresql.org/docs/current/extend-extensions.html] SQL itself (the full SQL command reference, Chapter/Part VI of the manual) is PostgreSQL's primary "API" as a database — `CREATE`/`ALTER`/`DROP` DDL, DML, and the extension mechanism (`CREATE EXTENSION` / `DROP EXTENSION` / `ALTER EXTENSION ... UPDATE`) for adding packaged functionality.

[Source: https://www.postgresql.org/docs/current/fdwhandler.html] The **Foreign Data Wrapper (FDW) API** is a documented C-level extension API: "All operations on a foreign table are handled through its foreign data wrapper, which consists of a set of functions that the core server calls," letting a wrapper fetch (and optionally write) data from a remote source and expose it as a foreign table. The docs note that FDWs bundled in the standard distribution's `contrib` subdirectory (e.g. `postgres_fdw`, referenced by name in `CREATE FOREIGN DATA WRAPPER` docs) serve as reference implementations.

---

## 4. Configuration

[Source: https://www.postgresql.org/docs/current/runtime-config.html] Server configuration is centered on **`postgresql.conf`** (general settings) and **`pg_hba.conf`** (host-based authentication rules), with three ways to set parameters: editing the config file (persists across restarts), SQL commands (`SHOW` to read, `SET` for the current session, `ALTER SYSTEM` to persist changes without hand-editing the file), and command-line/shell options at server start. Settings are organized into documented categories: Connections & Authentication, Resource Consumption, Write-Ahead Log, Replication, Query Planning, Error Reporting & Logging, Run-time Statistics, Vacuuming, and Client Connection Defaults, among others.

[Source: https://www.postgresql.org/docs/current/ssl-tcp.html] TLS/SSL is enabled via `ssl = on` plus `server.crt`/`server.key` in the data directory (or paths given by `ssl_cert_file`/`ssl_key_file`); the private key must be `chmod 0600` (or `0640` if root-owned). Client-certificate verification is opt-in per `pg_hba.conf` entry via `clientcert=verify-ca` (CA-signed only) or `clientcert=verify-full` (also matches CN to username), backed by `ssl_ca_file` and optionally `ssl_crl_file`.

[Source: https://www.postgresql.org/docs/current/auth-methods.html] `pg_hba.conf` selects one of PostgreSQL's documented authentication methods per connection rule: `trust`, `password` (plain, discouraged), `md5` (deprecated, see Section 13 below), `scram-sha-256` (via the generic "password" family), `gssapi`, `sspi` (Windows), `ident`, `peer` (local Unix-socket, OS-identity based), `ldap`, `radius`, `cert`, `pam`, `bsd` (OpenBSD only), and `oauth`. The docs recommend `peer` (or `trust`) for local connections and `password`/`scram-sha-256` for remote connections absent other infrastructure.

[Source: https://www.postgresql.org/docs/current/runtime-config-logging.html] Logging-related configuration (`log_destination`, `logging_collector`, `log_min_duration_statement`, `log_statement`, `log_line_prefix`, `log_rotation_age`/`log_rotation_size`) lives in the same `postgresql.conf` and most such settings require a config reload or restart rather than a runtime `SET` (session-scoped exceptions exist for superusers on some parameters).

[Inference, not confirmed in docs] Most resource/WAL/logging parameters are process-wide and take effect only on `SIGHUP` (reload) or full restart, per the general pattern described in `runtime-config.html`; the exact reload-vs-restart requirement is documented per-parameter in each config subsection rather than as one blanket rule, so this is stated cautiously.

---

## 5. Recommended patterns

[Source: https://www.postgresql.org/docs/current/populate.html] For **bulk data loading**, the docs recommend, in combination: wrap multiple inserts in one transaction (avoid per-statement autocommit overhead); prefer `COPY` over individual `INSERT`s (COPY is "optimized for bulk loading" and, when run in the same transaction as the `CREATE TABLE`/`TRUNCATE` under `wal_level = minimal`, can skip WAL writes entirely); create indexes and foreign keys **after** loading rather than maintaining them incrementally during load; temporarily raise `maintenance_work_mem` to speed index/FK builds; raise `max_wal_size` to reduce checkpoint frequency during the load; and run `ANALYZE` on affected tables afterward so the planner has current statistics. For restoring `pg_dump` archives, use `pg_restore --jobs=N` for parallelism and consider `--single-transaction`.

[Source: https://www.postgresql.org/docs/current/using-explain.html] The documented workflow for query performance work is: run plain `EXPLAIN` to see the chosen plan and cost/row estimates; run `EXPLAIN (ANALYZE, BUFFERS)` to compare actual vs. estimated rows/timing and see buffer hit/read counts; treat large estimate-vs-actual discrepancies as a signal to run `ANALYZE`; and use `EXPLAIN ANALYZE` inside `BEGIN`/`ROLLBACK` when analyzing data-modifying statements, since `EXPLAIN ANALYZE` actually executes the query and its side effects.

[Source: https://www.postgresql.org/docs/current/routine-vacuuming.html] The documented guidance is to leave **autovacuum enabled** (the default) rather than hand-scheduling `VACUUM`, reserving manual, scheduled vacuuming only for cases autovacuum can't handle well; and to prefer plain `VACUUM` run "often enough" over ever needing `VACUUM FULL` (which takes an exclusive lock and rewrites the table). `TRUNCATE` is recommended over `DELETE` + `VACUUM` when clearing an entire table.

[Source: https://www.postgresql.org/docs/current/ddl-rowsecurity.html] For per-row access control, the documented pattern is `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` plus one or more `CREATE POLICY` statements with `USING` (read-side filter) and, where write rules differ from read rules, a separate `WITH CHECK` clause.

[Source: https://www.postgresql.org/docs/current/indexes-types.html] Index-type selection is documented as workload-driven: B-tree (the default) for equality/range/sort queries; GIN for "contains" queries over composite values like arrays, `jsonb`, and full-text `tsvector`; GiST for geometric/nearest-neighbor and other extensible search structures; BRIN for very large tables whose column values correlate with physical row order (cheap, low-storage-overhead summarization); Hash for pure equality lookups only.

---

## 6. Anti-patterns

[Inference, not confirmed in docs] The official manual is written prescriptively (how to configure/use features correctly) rather than as an explicit "anti-patterns" catalog, so most items below are the *inverse* of a documented recommendation rather than a directly-labeled anti-pattern in the source text.

[Source: https://www.postgresql.org/docs/current/routine-vacuuming.html] Routinely using `VACUUM FULL` instead of relying on regular standard `VACUUM`/autovacuum is discouraged: it is markedly slower and takes an exclusive table lock, versus the documented goal of vacuuming "often enough" with plain `VACUUM` to avoid ever needing `FULL`.

[Source: https://www.postgresql.org/docs/current/populate.html] Loading large datasets via many individual autocommitted `INSERT` statements, or with indexes/foreign keys already in place, is implicitly anti-pattern by omission — the documented recommendation is `COPY` in bulk with indexes/FKs added afterward, the explicit inverse of this approach.

[Source: https://www.postgresql.org/docs/current/app-pgdump.html] Restoring a `pg_dump`/`pg_restore` archive from an untrusted source is explicitly flagged as dangerous: the docs warn that "dumps contain superuser code that executes during restore" — restoring untrusted dumps is a documented security anti-pattern, not just a style concern. Relying on `pg_dump` alone as a production backup strategy is also discouraged; the docs point to Chapter 25 (physical backup / WAL archiving / PITR) for that purpose instead.

[Source: https://www.postgresql.org/docs/current/ddl-rowsecurity.html] Writing RLS policies with subqueries against tables that can be concurrently modified is documented as a potential information-leakage race condition, unless mitigated with `SELECT ... FOR SHARE` or stronger locking — an implicit anti-pattern the docs call out directly under "Row Security Policies" caveats.

[Source: https://www.postgresql.org/docs/current/release-18.html] As of PostgreSQL 18, `md5` password authentication is being phased toward removal: `CREATE ROLE`/`ALTER ROLE` now emit deprecation warnings for `md5` (silenceable via `md5_password_warnings = off`), signaling continued reliance on `md5` auth as an anti-pattern going forward. [Version-sensitive: warning behavior introduced in PostgreSQL 18; full removal not yet dated in the pages fetched — see Section 13.]

---

## 7. Security

[Source: https://www.postgresql.org/docs/current/auth-methods.html] Authentication is configured per-connection-rule in `pg_hba.conf`, selecting among `trust`, `password`, `md5` (deprecated), `scram-sha-256`, `gssapi`, `sspi`, `ident`, `peer`, `ldap`, `radius`, `cert`, `pam`, `bsd`, and (new in v18) `oauth`.

[Source: https://www.postgresql.org/docs/current/user-manag.html] Access control is role-based: "a role can be thought of as either a database user, or a group of database users" — since PostgreSQL 8.1 the separate user/group concepts were unified so any role can act as either or both. Roles own objects, can be granted privileges on objects, and can be granted membership in other roles to inherit privileges. Predefined roles (documented separately) provide granular capability grants (e.g. read-all-stats-style roles) without full superuser.

[Source: https://www.postgresql.org/docs/current/ddl-rowsecurity.html] **Row-Level Security (RLS)**, enabled via `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` + `CREATE POLICY`, supplements the standard GRANT-based privilege system with per-row Boolean predicates. Permissive policies (the default) combine with `OR`; restrictive policies combine with `AND`. Superusers, `BYPASSRLS` roles, and (by default) table owners bypass RLS unless the table is explicitly set with `FORCE ROW LEVEL SECURITY`. If RLS is enabled with no policies defined, the default is **deny all rows** — a fail-closed default. Setting `row_security = off` turns silent filtering into hard errors, which the docs recommend for debugging policy interactions.

[Source: https://www.postgresql.org/docs/current/ssl-tcp.html] Server-side TLS is configured with `ssl = on`, a certificate/key pair, correct key file permissions (`0600`), and optional mandatory client-certificate verification (`clientcert=verify-ca`/`verify-full` in `pg_hba.conf`).

[Version-sensitive, Source: https://www.postgresql.org/docs/current/release-18.html] PostgreSQL 18 adds OAuth 2.0 as a `pg_hba.conf` authentication method and introduces 256-bit cancel-request keys (protocol 3.2) as a security hardening measure over the previous 32-bit cancel keys.

---

## 8. Performance

[Source: https://www.postgresql.org/docs/current/using-explain.html] `EXPLAIN` / `EXPLAIN ANALYZE` (optionally with `BUFFERS`, `VERBOSE`, `SERIALIZE`, and `FORMAT JSON/XML/YAML`) is the documented primary tool for diagnosing query performance; the docs explicitly describe plan-reading as "an art that requires some experience to master" and warn that `EXPLAIN ANALYZE` executes the query (including side effects) and that timing overhead can itself be significant on systems with slow `gettimeofday()`.

[Source: https://www.postgresql.org/docs/current/indexes-types.html] Index choice materially affects performance and is workload-specific: B-tree for equality/range/ordering; Hash for equality-only; GiST for extensible/geometric/nearest-neighbor search; SP-GiST for non-balanced partitioned structures (quadtrees, k-d trees, radix trees); GIN for "contains-a-value" queries over composite data (arrays, jsonb, full-text); BRIN for large, physically-correlated tables (a `bloom` extension index type also exists but wasn't detailed in the fetched page).

[Version-sensitive, Source: https://www.postgresql.org/docs/current/release-18.html] PostgreSQL 18 introduces a new **asynchronous I/O (AIO) subsystem**, documented as improving performance of sequential scans, bitmap heap scans, and vacuum, with the release announcement citing "up to 3× performance improvements when reading from storage" [Source: https://www.postgresql.org/about/news/postgresql-18-released-3142/]. It also adds B-tree **"skip scan"** support, letting multicolumn B-tree indexes be used even when a leading column lacks a restriction — expanding the set of queries that can use an existing index.

[Source: https://www.postgresql.org/docs/current/monitoring-stats.html] Ongoing performance monitoring is driven by the cumulative statistics system's views: `pg_stat_activity` (live per-backend state, including `wait_event`), `pg_stat_user_tables`/`pg_stat_user_indexes` (scan counts, dead/live tuples, vacuum/analyze history), `pg_statio_*` (buffer hit/read counts), `pg_stat_io` (per-backend/object I/O, expanded in v18), `pg_stat_bgwriter`/`pg_stat_checkpointer`/`pg_stat_wal` (background writer, checkpoint, WAL activity), and `pg_stat_replication` for replica lag. Statistics update with a documented minimum lag (roughly one second) and are gated by `track_activities`/`track_counts`/`track_io_timing` configuration.

[Source: https://www.postgresql.org/docs/current/populate.html] Bulk-load performance guidance (see Section 5) — `COPY`, deferred index/FK creation, larger `maintenance_work_mem`/`max_wal_size`, temporarily reduced WAL levels — is documented as a distinct performance topic from steady-state query tuning.

---

## 9. Testing

[Source: https://www.postgresql.org/docs/current/regress.html] PostgreSQL ships a **regression test suite** ("a comprehensive set of tests for the SQL implementation in PostgreSQL... test[ing] standard SQL operations as well as the extended capabilities of PostgreSQL"), runnable via `pg_regress` against a temporary or existing installation, plus TAP (Test Anything Protocol) tests for broader scenarios and coverage tooling.

**Important scope caveat** [Inference, not confirmed in docs, but strongly implied by the chapter's framing and audience]: this regression-test chapter documents how the PostgreSQL Global Development Group tests **PostgreSQL itself** (the server/SQL engine) during development, not guidance for application developers on how to test applications built on top of PostgreSQL. The official docs do not appear (in the pages fetched) to prescribe an application-level testing methodology (e.g. no official guidance on ephemeral test databases, transactional test isolation patterns for app test suites, or fixture/seeding tooling) — such guidance, where it exists, comes from third-party tooling/ORMs, which is out of scope for "official docs only" citations here.

Not documented / could not verify: any official PostgreSQL-maintained tooling equivalent to "testcontainers" or a first-party ephemeral-database-for-CI story; this appears to be left to the broader ecosystem (official Docker Hub `postgres` image, cloud-provider tooling, third-party libraries) rather than documented by postgresql.org itself.

---

## 10. Deployment

[Source: https://www.postgresql.org/docs/current/installation.html] Chapter 17 covers installing **from source** (Requirements, obtaining source, building via Autoconf/Make or the newer Meson build system, post-install setup, supported platforms including platform-specific notes for Cygwin/macOS/MinGW/Solaris/Visual Studio). The chapter explicitly defers to a different chapter for pre-packaged installs: "If you are installing a pre-packaged distribution, such as an RPM or Debian package, ignore this chapter and see Chapter 16 instead."

Not documented / could not verify (in pages fetched): official first-party guidance on **containerized/Docker deployment**. [Inference, not confirmed in docs] The widely-used `postgres` image on Docker Hub is maintained as part of Docker's Official Images program (with PostgreSQL community involvement) rather than being a `postgresql.org`-authored artifact as far as the fetched documentation shows; this research pass did not locate an official postgresql.org page documenting container deployment, so it should be treated as ecosystem/community tooling rather than PGDG-official for citation purposes.

[Source: https://www.postgresql.org/docs/current/high-availability.html] For deployment topologies beyond a single instance, the docs describe log-shipping standby servers (warm standby = cannot serve reads until promoted; hot standby = serves read-only queries while standing by), streaming replication, replication slots (to retain WAL for standbys), cascading replication (standbys feeding other standbys), and synchronous vs. asynchronous replication trade-offs — synchronous guarantees no data loss on failover but the docs note it "may significantly impact performance (>50% slowdown over slow networks)"; asynchronous has minimal performance impact but risks data loss/stale reads on failover.

[Source: https://www.postgresql.org/docs/current/app-pgdump.html] `pg_dump`/`pg_dumpall`/`pg_restore` are the documented logical-backup/restore tools (single database vs. whole-cluster-plus-globals respectively); the docs point to Chapter 25 for physical backup and continuous WAL archiving as the recommended approach for production backup strategy rather than relying on `pg_dump` alone.

---

## 11. Migration

[Source: https://www.postgresql.org/docs/current/pgupgrade.html] **`pg_upgrade`** performs in-place major-version upgrades without a full dump/restore cycle, by creating new system catalogs for the target version and reusing old data files directly (relying on PostgreSQL's on-disk storage format rarely changing between major versions). [Version-sensitive] Supports upgrading from PostgreSQL 9.2 and later up to the current major release. Requirements/limitations documented: binary compatibility (matching 32/64-bit and certain compile-time settings) between old and new clusters; does not support clusters with columns of `regcollation`/`regconfig`/`regdictionary`/`regnamespace`/`regoper`/`regoperator`/`regproc`/`regprocedure` types; the docs explicitly warn that running `pg_upgrade` executes code chosen by the source cluster's superusers, so trust boundaries matter. Upgrade modes: **copy** (default, safest, slowest), **link** (`-k`, fastest, but the old cluster becomes unusable once the new one starts), **clone** (`--clone`, link-speed without destroying the old cluster, limited filesystem support), **swap** (`--swap`, fastest for many relations but destructively modifies the old cluster). `pg_upgrade --check` validates compatibility without making changes. The documented general procedure spans roughly 17 steps: build/install new binaries, `initdb` the new cluster, install extension `.so` files and custom full-text-search files into the new tree, adjust `pg_hba.conf` for the upgrade, stop both servers, run `pg_upgrade`, upgrade standbys (e.g. via `rsync` in link mode), restore configuration files, start the new server, run post-upgrade scripts, regenerate statistics with `vacuumdb`, and eventually decommission the old cluster.

[Version-sensitive, Source: https://www.postgresql.org/docs/current/release-18.html] As of PostgreSQL 18, `pg_upgrade` retains/carries forward optimizer statistics across the upgrade (previously statistics had to be fully regenerated post-upgrade), reducing the post-upgrade `ANALYZE` burden. [Inference, not confirmed in docs] The Section 10 note about running `vacuumdb`/`ANALYZE` post-upgrade in the general procedure may therefore be less critical starting with v18 than it was for upgrades into earlier major versions, though the docs still list statistics regeneration as a step.

[Source: https://www.postgresql.org/docs/current/app-pgdump.html] The alternative to `pg_upgrade` for major-version migration is the classic dump/restore path (`pg_dumpall`/`pg_dump` + `pg_restore`/`psql`), and/or **logical replication** for near-zero-downtime migrations (referenced in the high-availability chapter), letting a new-version replica be built and promoted while the old cluster keeps serving traffic.

Migrating **from a different database product to PostgreSQL** (e.g. from MySQL, Oracle) is not covered by official postgresql.org documentation in the pages examined — Not documented / could not verify. [Inference, not confirmed in docs] Cross-database migration tooling appears to live with third-party or vendor-specific projects, outside PGDG's own docs.

---

## 12. Version information

[Source: https://www.postgresql.org/support/versioning/] PostgreSQL ships a new **major version roughly once a year**, each supported for **five years** after its initial release, after which a final minor release is issued and the major version reaches end-of-life (EOL). **Minor releases** (bug fixes, security fixes) ship at least once every three months per major version, with out-of-band releases possible for urgent security issues. The docs explicitly recommend: "We recommend that users always run the current minor release associated with their major version" — minor upgrades are lower-risk than staying on an old minor release and require only a binary swap + restart (no dump/restore).

As of this research date (2026-09-09), per [Source: https://www.postgresql.org/about/news/postgresql-186-1711-1615-1519-1424-and-19-beta-3-released-3365/] and [Source: https://www.postgresql.org/support/versioning/]:

| Major version | Current minor (as of research date) | Initial release | Documented EOL |
|---|---|---|---|
| 18 | 18.6 | 2025-09-25 | 2030-11-14 |
| 17 | 17.11 | 2024-09-26 | 2029-11-08 |
| 16 | 16.15 | 2023-09-14 | 2028-11-09 |
| 15 | 15.19 | 2022-10-13 | 2027-11-11 |
| 14 | 14.24 | 2021-09-30 | 2026-11-12 |

[Source: https://www.postgresql.org/about/news/postgresql-186-1711-1615-1519-1424-and-19-beta-3-released-3365/] **PostgreSQL 19 Beta 3** was released 2026-08-13, meaning PostgreSQL 19 is currently in beta as of the research date and is expected to reach general availability around the traditional September/October release window later in 2026 [Inference, not confirmed in docs — exact GA date not published in the fetched sources]. Note PostgreSQL 14 is nearing its documented EOL (2026-11-12), roughly two months after this research date — relevant to flag for any skill recommending PG14 for new projects.

[Inference, not confirmed in docs] Given 19 is in beta and 18 is the current stable ("current" alias) release, skills grounded on "current official docs" as of this research date should treat **PostgreSQL 18** as the baseline stable target, while noting PostgreSQL 19 features are still subject to change until GA.

---

## 13. Breaking changes

[Version-sensitive — all items below are from Source: https://www.postgresql.org/docs/current/release-18.html, i.e. changes introduced going from PostgreSQL 17 to PostgreSQL 18]

- **Data checksums default to ON**: `initdb` now enables data checksums by default (`--no-data-checksums` opts out). `pg_upgrade` requires matching checksum settings between old and new clusters, so this affects upgrade planning.
- **`COPY FROM` CSV end-of-file marker removed**: `\.` alone is no longer treated as an implicit CSV EOF marker; it must appear alone on its own line to have special meaning. The docs flag a specific compatibility risk: older `psql` clients connecting to a PostgreSQL 18 server may hit `\copy` problems.
- **`COPY FREEZE` on foreign tables** now errors instead of being silently ignored.
- **AFTER trigger execution role changed**: triggers now execute using the role that was active when the triggering event was *queued*, not the role active at transaction commit — a semantic change for workloads that change role mid-transaction.
- **Primary/foreign key collation requirements tightened**: keys must use deterministic collations, or identical nondeterministic collations across referencing/referenced columns; `pg_dump`-based restores can now fail if this requirement isn't met, requiring schema fixes before upgrade.
- **Unlogged partitioned tables**: `ALTER TABLE ... SET [UN]LOGGED` now enforces logging consistency between a partitioned table and its children (previously inconsistent states were possible).
- **VACUUM/ANALYZE on partitioned tables**: now process child (partition) tables by default; a new `ONLY` option restricts the operation to just the named (parent) table — the inverse of prior default behavior.
- **Rule privileges removed**: `GRANT`/`REVOKE` support for rule privileges, non-functional since PostgreSQL 8.2, has been fully removed.
- **System catalog changes**: `pg_backend_memory_contexts.parent` column removed; `pg_backend_memory_contexts.level` and `pg_log_backend_memory_contexts()` output switched from zero-based to one-based numbering.
- **Full-text search collation behavior changed**: full text search now uses the cluster's default collation provider instead of always using libc; clusters using non-libc providers (ICU, the new built-in provider) may see search behavior changes, and the docs recommend reindexing full-text-search and `pg_trgm` indexes after upgrading.
- **`md5` password authentication deprecated**: `CREATE ROLE`/`ALTER ROLE` now emit warnings when `md5`-based passwords are set; removal is signaled as planned for a future version (no removal version number given in the fetched release notes) — silenceable via `md5_password_warnings = off`.
- **Minimum toolchain requirements raised**: Python ≥ 3.6.8 (up from 3.5.x), OpenSSL ≥ 1.1.1, LLVM ≥ 14.
- **Architecture support dropped**: HP-PA/PA-RISC is no longer supported.
- **Session time zone abbreviation resolution order changed**: session-level time zone abbreviations are now checked before the server's `timezone_abbreviations` setting.
- **Wire protocol bumped to 3.2**: adds 256-bit cancel-request keys (previously 32-bit) — a security-motivated protocol change, backward compatible with 3.0 per the protocol docs.

Not documented / could not verify: a similarly detailed breaking-changes list for the PostgreSQL 19 (currently beta) release, since `release-19.html`/`release-19-*.html` pages were not fetched in this research pass and content is still subject to change pre-GA. [Unresolved: whether any PG18 breaking changes listed above will be reverted or altered before v19 GA — not checked.]

---

## 14. Limitations

[Source: https://www.postgresql.org/docs/current/limits.html] Documented hard limits:

| Item | Limit | Note |
|---|---|---|
| Database size | Unlimited | — |
| Number of databases | 4,294,950,911 | — |
| Relations per database | 1,431,650,303 | — |
| Relation size | 32 TB | with default 8192-byte `BLCKSZ` |
| Rows per table | Limited by tuples fitting on 4,294,967,295 pages | — |
| Columns per table | 1,600 | further limited by tuple-size-per-page constraints |
| Columns in a result set | 1,664 | — |
| Field size | 1 GB | — |
| Indexes per table | Unlimited | bounded only by max relations per database |
| Columns per index | 32 | can be raised by recompiling PostgreSQL |
| Partition keys | 32 | can be raised by recompiling PostgreSQL |
| Identifier length | 63 bytes | can be raised by recompiling PostgreSQL |
| Function arguments | 100 | can be raised by recompiling PostgreSQL |
| Query parameters | 65,535 | — |

[Source: https://www.postgresql.org/docs/current/limits.html] Tables can hold a theoretical maximum of 2^32 out-of-line (TOAST) values; the effective column-count limit is further constrained by the requirement that a tuple fit on a single 8192-byte heap page, so the practical column limit is usually well under 1,600 depending on column types/widths.

[Source: https://www.postgresql.org/docs/current/routine-vacuuming.html] The 32-bit transaction ID space is a documented operational limitation: clusters must be vacuumed regularly to "freeze" old rows and avoid transaction ID wraparound, which is a correctness (not just performance) requirement in long-lived, high-write clusters.

[Source: https://www.postgresql.org/docs/current/pgupgrade.html] `pg_upgrade` cannot upgrade clusters containing columns of certain OID-reference pseudo-types (`regcollation`, `regconfig`, `regdictionary`, `regnamespace`, `regoper`, `regoperator`, `regproc`, `regprocedure`) — a documented migration-path limitation.

---

## 15. Debugging

[Source: https://www.postgresql.org/docs/current/using-explain.html] `EXPLAIN` / `EXPLAIN (ANALYZE, BUFFERS)` is the primary documented query-debugging tool — comparing estimated vs. actual row counts/timing to identify stale statistics, bad selectivity estimates, or missing indexes; `SET enable_seqscan = OFF` (and similar `enable_*` planner flags) is documented as a way to force alternative plans for comparison.

[Source: https://www.postgresql.org/docs/current/runtime-config-logging.html] Server-side debugging relies on logging configuration: `log_min_duration_statement` to surface slow queries, `log_statement` (`none`/`ddl`/`mod`/`all`) to control statement-level logging, `log_line_prefix` escape sequences (`%m` timestamp, `%p` PID, `%u` user, `%d` database, `%a` application_name, `%e` SQLSTATE) for structured log lines, `log_destination`/`logging_collector` to route output to `stderr`/`csvlog`/`jsonlog`/`syslog`, and `log_error_verbosity = verbose` for full error detail. These settings generally require a config reload/restart rather than a runtime `SET`, with exceptions.

[Source: https://www.postgresql.org/docs/current/monitoring-stats.html] Live and cumulative statistics views back most runtime debugging: `pg_stat_activity` (per-backend state, current query, `wait_event`/`wait_event_type` — useful for diagnosing lock contention or stuck queries), `pg_stat_replication`/`pg_stat_wal_receiver` (replication lag debugging), `pg_stat_user_tables`/`pg_stat_user_indexes` (dead-tuple buildup, missed autovacuum, unused indexes), `pg_stat_io` (I/O-pattern debugging, expanded in v18), and `pg_stat_database_conflicts` (recovery-conflict debugging on standbys). `pg_stat_clear_snapshot()` discards the cached statistics snapshot within a transaction; ordinary users see only their own sessions in `pg_stat_activity` unless granted `pg_read_all_stats` or superuser.

[Version-sensitive, Source: https://www.postgresql.org/docs/current/release-18.html] PostgreSQL 18 adds `pg_aios` (async I/O introspection) and expands `pg_stat_io` with byte-level counts, plus richer `VACUUM`/`ANALYZE VERBOSE` output (WAL, CPU, average-read statistics) and `EXPLAIN` improvements (auto-`BUFFERS` under `ANALYZE`, index-lookup counts, fractional row-count display) — all directly relevant to debugging workflows on v18+.

---

## 16. Integration

[Source: https://www.postgresql.org/docs/current/fdwhandler.html] **Foreign Data Wrappers (FDW)** are PostgreSQL's documented mechanism for integrating external data sources as if they were local tables, via `CREATE FOREIGN DATA WRAPPER` / `CREATE SERVER` / `CREATE FOREIGN TABLE`, with `postgres_fdw` (bundled in `contrib`) as the reference wrapper for connecting one PostgreSQL server to another.

[Source: https://www.postgresql.org/docs/current/extend-extensions.html] The **extension** mechanism (`CREATE EXTENSION`) is the general integration point for adding functionality — data types, index access methods, procedural languages, foreign data wrappers themselves — as versioned, dump/upgrade-aware units, with a documented control-file + versioned-SQL-script packaging format.

[Source: https://www.postgresql.org/docs/current/external-interfaces.html] Language-level integration (from applications) is officially limited to **libpq** (C) and **ECPG** (embedded SQL in C); all other language drivers (Python, Java/JDBC, Node.js, etc.) are external, community/vendor-maintained projects referenced only via the community wiki's driver list, not documented or supported directly by the PostgreSQL Global Development Group.

[Source: https://www.postgresql.org/docs/current/high-availability.html] Replication-level integration includes both **physical (streaming) replication** — for standbys, HA, and read scaling — and **logical replication** (referenced in the same chapter and in the v18 release notes, which specifically added logical replication of generated columns), enabling integration with external systems that consume a logical change stream (e.g. CDC pipelines), though the specific CDC/downstream-tool ecosystem itself is third-party and outside official docs.

[Source: https://www.postgresql.org/docs/current/protocol.html] SASL-based authentication integration includes `SCRAM-SHA-256` and, as of v18, `OAUTHBEARER`, letting PostgreSQL integrate with external OAuth 2.0 identity providers per the auth-methods documentation.

---

## 17. Production considerations

[Source: https://www.postgresql.org/docs/current/routine-vacuuming.html] Long-running production clusters must keep autovacuum tuned/enabled to avoid both table bloat and transaction ID wraparound; the docs frame wraparound avoidance as a hard operational requirement, not merely a performance nicety.

[Source: https://www.postgresql.org/docs/current/high-availability.html] For availability, the documented trade-off is explicit: synchronous replication guarantees zero data loss on failover but can materially slow write throughput ("may significantly impact performance (>50% slowdown over slow networks)" per the docs), while asynchronous replication preserves performance but risks losing recently-committed transactions and serving stale reads from standbys during/after failover — a decision every production HA topology has to make consciously.

[Source: https://www.postgresql.org/docs/current/app-pgdump.html] The docs explicitly steer production backup strategy away from `pg_dump` alone (a logical, single-database, non-continuous backup tool) toward the physical-backup/continuous-WAL-archiving approach in Chapter 25 for real point-in-time-recovery capability; `pg_dump`/`pg_dumpall` remain useful for portable exports and version migrations but are not positioned as the primary production backup mechanism.

[Source: https://www.postgresql.org/docs/current/support/versioning/... (see also https://www.postgresql.org/support/versioning/)] Production operators are advised to always run the current **minor** release of whatever major version they're on — minor upgrades only require a binary swap and restart (no dump/restore) — and to plan major-version upgrades before a version's five-year support window ends, since after EOL a major version receives no further fixes, including security fixes.

[Source: https://www.postgresql.org/docs/current/ssl-tcp.html] Production deployments handling sensitive data are expected to enable TLS (`ssl = on`) with correctly-permissioned key files, and to consider mandatory client-certificate verification (`clientcert=verify-full`) where mutual TLS is warranted.

[Source: https://www.postgresql.org/docs/current/monitoring-stats.html] Production monitoring is expected to be built on the `pg_stat_*`/`pg_statio_*` view family plus `track_io_timing`/`track_wal_io_timing` for I/O-latency visibility — these are the documented first-party observability surface, with the note that statistics persist across a **clean** shutdown (via the `pg_stat` subdirectory) but not necessarily across a crash.

[Version-sensitive, Source: https://www.postgresql.org/docs/current/release-18.html] Production clusters upgrading to v18 should specifically plan around: matching data-checksum settings between old/new clusters for `pg_upgrade`, potential `\copy` incompatibility with older `psql` clients against an 18 server (CSV `\.` EOF change), and reindexing full-text-search/`pg_trgm` indexes if using a non-libc collation provider, per the breaking-changes items in Section 13.

---

## Sources cited (deduplicated)

- https://www.postgresql.org/docs/current/release.html — Release notes index / doc-versioning confirmation
- https://www.postgresql.org/docs/current/release-18.html — PostgreSQL 18 feature and breaking-change summary
- https://www.postgresql.org/about/news/postgresql-18-released-3142/ — PG18 GA announcement (AIO performance claim)
- https://www.postgresql.org/about/news/postgresql-186-1711-1615-1519-1424-and-19-beta-3-released-3365/ — Aug 2026 combined minor-release + v19 Beta 3 announcement
- https://www.postgresql.org/support/versioning/ — Official versioning/support-window policy and current version table
- https://www.postgresql.org/docs/current/tutorial-arch.html — Client/server, process-per-connection architecture
- https://www.postgresql.org/docs/current/overview.html — Internals overview (query path) chapter framing
- https://www.postgresql.org/docs/current/runtime-config.html — Configuration file structure and parameter-setting methods
- https://www.postgresql.org/docs/current/wal-intro.html — WAL concept and rationale
- https://www.postgresql.org/docs/current/mvcc-intro.html — MVCC concurrency model
- https://www.postgresql.org/docs/current/transaction-iso.html — Transaction isolation levels
- https://www.postgresql.org/docs/current/limits.html — Documented hard limits table
- https://www.postgresql.org/docs/current/auth-methods.html — Authentication method catalog
- https://www.postgresql.org/docs/current/ssl-tcp.html — TLS/SSL server configuration
- https://www.postgresql.org/docs/current/using-explain.html — EXPLAIN / EXPLAIN ANALYZE usage
- https://www.postgresql.org/docs/current/routine-vacuuming.html — VACUUM / autovacuum rationale and practice
- https://www.postgresql.org/docs/current/ddl-rowsecurity.html — Row-level security (RLS) policies
- https://www.postgresql.org/docs/current/app-pgdump.html — pg_dump / pg_restore usage and backup guidance
- https://www.postgresql.org/docs/current/pgupgrade.html — pg_upgrade process, modes, limitations
- https://www.postgresql.org/docs/current/high-availability.html — Replication / HA topologies and trade-offs
- https://www.postgresql.org/docs/current/external-interfaces.html — Official client interfaces (libpq, ECPG) scope
- https://www.postgresql.org/docs/current/regress.html — PostgreSQL's own regression-test framework
- https://www.postgresql.org/docs/current/indexes-types.html — Index type catalog and use cases
- https://www.postgresql.org/docs/current/user-manag.html — Roles and privilege model
- https://www.postgresql.org/docs/current/extend-extensions.html — Extension packaging and CREATE EXTENSION
- https://www.postgresql.org/docs/current/runtime-config-logging.html — Logging configuration parameters
- https://www.postgresql.org/docs/current/populate.html — Bulk-load performance recommendations
- https://www.postgresql.org/docs/current/monitoring-stats.html — Cumulative statistics views (pg_stat_*)
- https://www.postgresql.org/docs/current/fdwhandler.html — Foreign Data Wrapper API
- https://www.postgresql.org/docs/current/installation.html — Source-build installation chapter scope
- https://www.postgresql.org/docs/current/protocol.html — Frontend/backend wire protocol
- https://www.postgresql.org/docs/current/datatype.html — Built-in data type catalog

---

## Unresolved items (surfaced explicitly, per project convention)

- **Unresolved**: Exact GA date for PostgreSQL 19 — only Beta 3 (2026-08-13) was confirmed in the fetched sources; the traditional September/October release window is an inference from PostgreSQL's historical release cadence, not a confirmed date.
- **Unresolved**: Whether any of the PostgreSQL 18 breaking changes documented in Section 13 will be altered, reverted, or joined by new breaking changes before PostgreSQL 19 reaches GA — the v19 release-notes pages were not fetched in this pass since content is still in flux pre-release.
- **Unresolved**: The exact future version in which `md5` password authentication will be removed outright — PG18 release notes describe only a deprecation warning stage, with no target removal version stated in the fetched text.
- **Unresolved**: Whether `postgresql.org` documents any first-party container/Docker deployment path at all (a page may exist that this research pass did not surface); treated as "not documented in pages fetched" rather than "confirmed absent."
- **Unresolved**: Full detail on PostgreSQL's shared-memory architecture (buffer pool, lock manager internals) — the `tutorial-arch.html` page explicitly stated this wasn't covered in the section fetched; a fuller architecture chapter likely exists elsewhere in the internals documentation (Chapter 51 subsections) but was not individually fetched.
