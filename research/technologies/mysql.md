# MySQL — Deep Technology Research

Research conducted 2026-09-09. Primary source: the official MySQL Reference Manual at `dev.mysql.com/doc`, cross-checked against the current live manual version (9.7) and, where a claim is 8.4-LTS-specific, the 8.4 reference manual/release notes. Canonical docs host confirmed unmoved: **dev.mysql.com/doc** is still the current official documentation root as of this research date; no migration to a new host was found.

---

## 0. Versioning model note (read this first)

[Source: https://dev.mysql.com/doc/refman/9.7/en/mysql-releases.html] MySQL 9.7 documents itself as the manual for "version 9.7, through release 9.7.2," and its "MySQL Releases: Innovation and LTS" chapter describes the dual-track Innovation/LTS model used through the 9.x series.

[Source: https://blogs.oracle.com/mysql/a-more-predictable-mysql-release-model-calendar-versions-lts-and-innovation] Oracle's official MySQL blog announced (around June 2026) that **MySQL 9.7 is the last release using the traditional sequential `MAJOR.MINOR.PATCH` numbering**. Starting with MySQL 26.7.0, Innovation releases switch to **calendar-based versioning in `YY.M.P` format** (YY = last two digits of the year, M = release month without a leading zero, P = patch). MySQL 26.7.0 is described as the first GA Innovation release under this new scheme, released after MySQL 9.7 LTS.

[Source: https://blogs.oracle.com/mysql/mysql-july-2026-ga-releases-now-available] The July 2026 GA release wave included MySQL 26.7.0 (Innovation), MySQL 9.7.2 LTS, MySQL 8.4.11 LTS, and MySQL Workbench 26.7 — confirming both the old (9.7.x, 8.4.x) and new (26.7.0) numbering schemes are live simultaneously, one for existing LTS lines and one for the new Innovation line.

**Version-sensitivity flag:** Any fact below tied to "MySQL 8.0," "8.4," or "9.x" numbering should be read as pre-calendar-versioning-era; the project should re-verify against 26.x-era docs before citing version numbers in skills authored after this transition stabilizes. [Inference, not confirmed in docs: it is not yet clear from the fetched pages whether "MySQL 9.7 LTS" itself will eventually be renumbered, or whether it remains a permanent legacy LTS line alongside future calendar-versioned LTS releases such as a hypothetical 28.4 LTS.]

---

## 1. Core Concepts

[Source: https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html] MySQL is described as "the world's most popular open source database," a relational database management system (RDBMS) developed, distributed, and supported by Oracle Corporation.

[Source: https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html] The relational model stores data in separate tables (rather than one large storage area), organized for speed, with a SQL-based structural language governing relationships between tables (one-to-one, one-to-many, unique, required/optional, "pointers" between tables) so that data stays consistent and is not duplicated unnecessarily.

[Source: https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html] "SQL" stands for Structured Query Language — the standard language for accessing databases, standardized by ANSI/ISO SQL standards, usable directly, embedded in application code, or via language-specific APIs.

[Source: https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html] MySQL software operates on a client/server model: a multithreaded SQL server supporting different backends, several client programs/libraries, administrative tools, and a wide range of application programming interfaces (APIs); MySQL is also available as an embedded multithreaded library for linking into standalone applications.

[Source: https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html] MySQL is described as free/open source software (GPL-licensed for the community edition), fast/reliable/scalable, portable to many platforms (desktop, server, embedded), and Internet-ready. MySQL HeatWave is named as Oracle's cloud service offering in-memory query acceleration, available on OCI, AWS, and Azure.

---

## 2. Architecture

[Source: https://dev.mysql.com/doc/refman/9.7/en/pluggable-storage-overview.html] MySQL uses a **pluggable storage engine architecture** separating the SQL-processing "server layer" from the storage/retrieval "storage engine layer." The server layer handles connection handling, authentication, SQL parsing/optimization, and provides a consistent API regardless of storage engine; the storage engine layer performs the actual physical read/write of data.

[Source: https://dev.mysql.com/doc/refman/9.7/en/pluggable-storage-overview.html] The documented layer stack (roughly): Connectors/Interfaces → Common (server) layer (SQL parser, optimizer, caches) → Pluggable storage engines → filesystem (data files, logs). Applications specify a storage engine per table via `ENGINE=...` in `CREATE TABLE`, and can mix engines within one database without changing application-level SQL.

[Source: https://dev.mysql.com/doc/refman/9.7/en/pluggable-storage-overview.html] Documented storage engines include **InnoDB** (default, transactional, row-level locking, foreign keys), **MyISAM**, **MEMORY**, **CSV**, **ARCHIVE**, **BLACKHOLE**, **MERGE**, and **FEDERATED** (remote table access), each optimized for a different workload (OLTP vs. read-heavy vs. temp data vs. compressed history, etc.).

[Source: https://dev.mysql.com/doc/refman/9.7/en/replication.html] MySQL's **replication architecture** copies data from a "source" server to one or more "replica" servers. Core components: the **binary log** on the source (records changes), the **relay log** on the replica (staging area for received events), replication threads, and an optional **replication metadata repository**. Replication is asynchronous by default.

[Source: https://dev.mysql.com/doc/refman/9.7/en/replication.html] Documented replication formats: statement-based (SBR), row-based (RBR), and mixed (MBR). Documented replication identity/positioning mechanisms: classic binary-log-file-position-based, and **GTID (Global Transaction Identifier)**-based, which the manual frames as the more modern, position-independent, consistency-guaranteeing approach.

[Source: https://dev.mysql.com/doc/refman/9.7/en/group-replication.html] **Group Replication** is a MySQL Server plugin providing group-membership management, automatic failure detection, and distributed data consistency across a set of instances. It supports **single-primary mode** (one writable primary, automatic election) and **multi-primary mode** (all members writable). [Source: https://dev.mysql.com/doc/refman/9.7/en/group-replication.html] Group Replication does not itself provide client failover — the docs state that **InnoDB Cluster** (which wraps Group Replication plus MySQL Shell plus **MySQL Router**) is the recommended way to deploy multi-instance MySQL topologies, and **InnoDB ReplicaSet** is recommended for non-HA, single-primary async replication topologies.

[Source: https://dev.mysql.com/doc/refman/9.7/en/group-replication.html] For workloads requiring true synchronous replication (rather than Group Replication's virtually-synchronous certification-based consistency), the docs point to **MySQL NDB Cluster** as the distinct, separately-architected clustering product (shared-nothing, in-memory-oriented, distributed storage engine — architecturally very different from the InnoDB/Group-Replication stack).

---

## 3. APIs

[Source: https://dev.mysql.com/doc/refman/9.7/en/connectors-apis.html] Official Oracle-developed connectors documented: **Connector/C++**, **Connector/J** (JDBC), **Connector/NET** (ADO.NET), **Connector/ODBC**, **Connector/Python** (DB API 2.0-compliant native driver), and **Connector/Node.js** (uses the **X Protocol**, an asynchronous API for document-store/session-based access).

[Source: https://dev.mysql.com/doc/refman/9.7/en/connectors-apis.html] The low-level **MySQL C API** (`libmysqlclient`) ships with MySQL distributions and underlies the command-line client and many connectors. The docs distinguish two connector implementation approaches: those built on `libmysqlclient` (broad compatibility) versus "native drivers" that implement the MySQL wire protocol directly (documented as generally offering better performance/deployment ergonomics).

[Source: https://dev.mysql.com/doc/refman/9.7/en/connectors-apis.html] Third-party/community language bindings referenced from the official manual: Perl `DBI`/`DBD::mysql`, PHP `mysqli` and `PDO_MYSQL`, Python `MySQLdb`, Ruby `mysql2`, Tcl `MySQLtcl`, and an Eiffel binding — these are documented as separate sections in the manual rather than Oracle-maintained connectors per se.

[Source: https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html] The **X DevAPI / X Plugin / Document Store** functionality is documented as a distinct chapter of the manual (JSON document CRUD over the X Protocol), layered on top of the same server, allowing NoSQL-style document access alongside relational SQL access to the same data.

Unresolved: The exact current API stability/versioning guarantees for X DevAPI vs. classic C API were not directly fetched from a dedicated compatibility-policy page in this research pass; only the existence and purpose of each API surface was confirmed.

---

## 4. Configuration

[Source: https://dev.mysql.com/doc/refman/9.7/en/server-configuration.html] MySQL server configuration is layered: (1) **command-line options** passed to `mysqld`/`mysqld_safe`, which apply only to that single invocation; (2) **option files** (`my.cnf` on Unix-like systems, `my.ini` on Windows), which persist configuration across restarts using `[mysqld]`-style option groups; (3) runtime **system variables**, settable dynamically via SQL (`SET GLOBAL`/`SET SESSION`) for variables marked dynamic.

[Source: https://dev.mysql.com/doc/refman/9.7/en/server-configuration.html] Documented ways to inspect configuration: `mysqld --verbose --help` (lists all options and defaults), `SHOW VARIABLES` and `SHOW STATUS` (SQL-level), and the `mysqladmin variables` / `mysqladmin extended-status` CLI commands. Windows-specific: a graphical **MySQL Configurator** tool is documented for GUI-based setup.

[Source: https://dev.mysql.com/doc/refman/9.7/en/server-configuration.html] The manual references dedicated reference sections for **Server Command Options**, **Server System Variables**, and **Server Status Variables** as the authoritative per-variable documentation, plus the **Performance Schema** and **MySQL sys Schema** chapters for deeper runtime introspection of configuration effects.

[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html] The **InnoDB buffer pool** is documented as the primary tunable for InnoDB performance/memory configuration (Section 10.10 area of the optimization chapter covers buffering/caching, including buffer pool and the deprecated MyISAM key cache).

---

## 5. Recommended Patterns

[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html] The Optimization chapter recommends: analyzing query plans with **`EXPLAIN`** before hand-tuning; indexing columns used in `WHERE`, join, and `ORDER BY` clauses; using the query optimizer's index-merge, condition-pushdown, and hash-join capabilities where applicable; and monitoring via **Performance Schema** / **`sys` schema** rather than ad hoc guessing.

[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html] Documented InnoDB-specific tuning guidance: sizing the buffer pool appropriately, tuning redo logging for bulk-load/DDL-heavy workloads, and preferring **bulk data loading** techniques (documented separately) over row-by-row inserts for large data imports.

[Source: https://dev.mysql.com/doc/refman/9.7/en/replication.html] GTID-based replication is presented as the recommended approach over classic binary-log-position-based replication for new deployments, because it is transactional/position-independent and simplifies failover and topology-change operations.

[Source: https://dev.mysql.com/doc/refman/9.7/en/group-replication.html] For multi-instance high availability, the documented recommended pattern is to deploy via **InnoDB Cluster** (Group Replication + MySQL Shell + MySQL Router) rather than configuring Group Replication directly, because InnoDB Cluster provides the client-routing/failover layer that raw Group Replication lacks.

[Source: https://dev.mysql.com/doc/refman/9.7/en/upgrade-paths.html] The documented recommended upgrade pattern is to run the **MySQL Shell Upgrade Checker Utility** before any in-place upgrade, and to follow a rolling-upgrade scheme for replication topologies (upgrade replicas before the source, per the manual's replication upgrade section) rather than upgrading all nodes simultaneously.

[Source: https://dev.mysql.com/doc/refman/9.7/en/backup-and-recovery.html] The documented recommended production backup pattern combines periodic logical/physical full backups (mysqldump, MySQL Shell dump utilities, or MySQL Enterprise Backup) with continuous binary-log retention, to support point-in-time recovery rather than relying on full backups alone.

---

## 6. Anti-Patterns

[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html] The Security chapter's "General Security Issues" section documents that using `LOAD DATA LOCAL` carelessly is a security risk and gives explicit guidance on constraining it — implying "leaving `LOAD DATA LOCAL` enabled without restriction" is a documented anti-pattern.

[Source: https://blogs.oracle.com/mysql (via search result on 8.4.0 relnotes)] AUTO_INCREMENT on FLOAT/DOUBLE columns was deprecated in 8.0 and removed as an error in 8.4 — the manual's framing (deprecate-then-remove with an explicit "you must alter such tables before upgrading" warning) documents this as a pattern to avoid going forward. [Source: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html]

[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html] The optimization chapter documents that relying on full table scans instead of appropriate indexes, and using overly wide/inefficient data types, are things the "Database Structure Optimization" and "Data Type Optimization" subsections exist specifically to correct — implying they are documented as common inefficiencies to avoid.

Unresolved: I did not find a single official page titled something like "MySQL anti-patterns" — this dimension had to be assembled by inference from what the optimization/security/upgrade chapters explicitly warn against, rather than quoted from one canonical "anti-patterns" source. Treat items in this section as [Inference, not confirmed in docs verbatim as "anti-patterns"] even though each underlying warning is separately sourced.

---

## 7. Security

[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html] Chapter 8 (Security) covers, per the fetched table of contents: General Security Issues (guidelines, password security, protection against attackers, `LOAD DATA LOCAL` security, secure client programming); Access Control and Account Management (user accounts, the privilege system at global/database/table/column granularity, grant tables, role-based access control, account locking, per-account resource limits, multifactor authentication, proxy users, partial revokes); Encrypted Connections (TLS/SSL setup, protocol/cipher configuration, certificate management via MySQL utilities or OpenSSL); Security Components and Plugins; MySQL Enterprise Data Masking; MySQL Enterprise Encryption; SELinux integration; and FIPS 140 support.

[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html] Documented authentication plugins: caching SHA-2 authentication, SHA-256 authentication, cleartext (client-side) authentication, PAM, Windows native authentication, LDAP, Kerberos, **OpenID Connect**, socket peer-credential authentication, and **WebAuthn**.

[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html] Documented at-rest key management: the **MySQL Keyring**, with backends for file-based (plain or encrypted) keystores, **KMIP**, **AWS KMS**, **HashiCorp Vault**, and **Oracle Cloud Infrastructure Vault**.

[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html] Documented audit tooling: the legacy **Enterprise Audit Plugin is deprecated**, in favor of the newer **Audit Log Component**. Also documented: **Connection Control** (mitigates brute-force login attempts by inserting delays after repeated failures) and **Password Validation Component** (enforces password strength policy).

[Source: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html] **Version-sensitive:** As of MySQL 8.4.0, `mysql_native_password` authentication is disabled by default (must be explicitly re-enabled via `mysql_native_password=ON` if legacy clients require it), and the `default_authentication_plugin` system variable (deprecated since 8.0.27) was removed — `authentication_policy` is now the documented mechanism for controlling default authentication behavior.

[Source: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html] **Version-sensitive:** As of 8.4.0, weak TLS/cipher configurations are more strictly rejected; the `--ssl`, `--admin-ssl`, `have_ssl`, and `have_openssl` items (deprecated since 8.0.26) were removed in favor of `--tls-version`/`--admin-tls-version`.

[Source: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html] **Version-sensitive:** The `authentication_fido`/`authentication_fido_client` plugins were removed in 8.4.0 in favor of `authentication_webauthn`.

---

## 8. Performance

[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html] Chapter 10 (Optimization) documents optimization at multiple levels: SQL statement optimization (WHERE-clause/range optimization, index merge, hash joins, condition pushdown, subquery/derived-table materialization strategies, optimizing `INSERT`/`UPDATE`/`DELETE`); indexing strategy (B-Tree vs. hash indexes, multi-column indexes, invisible indexes, descending indexes, index statistics); database structure optimization (data types, "many tables" management, temporary tables, column/table limits); InnoDB-specific tuning (storage layout, transactions, read-only-transaction optimization, redo log tuning, bulk loading, DDL performance, disk I/O); query execution plan analysis via **`EXPLAIN`** (including extended/JSON formats); optimizer control (switchable optimizations, optimizer hints, index hints, cost model, statistics); buffering/caching (InnoDB buffer pool, MyISAM key cache, prepared-statement/stored-program caching); locking optimization (internal vs. external locking, table-locking issues, concurrent inserts, metadata locking); server-level optimization (disk I/O, memory usage); and performance monitoring (benchmarking methodology, Performance Schema, thread/process inspection, optimizer tracing).

[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html] The manual explicitly names `EXPLAIN` as the primary tool for understanding how the optimizer will execute a given statement, and documents optimizer hints and index hints as the mechanism for overriding optimizer choices when it makes a suboptimal plan.

[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html] The **Performance Schema** (Chapter 29 per the TOC) and **MySQL `sys` schema** (Chapter 30, built as convenience views over Performance Schema) are the documented facilities for runtime performance monitoring and diagnostics, distinct from `EXPLAIN`'s static plan analysis.

Unresolved: No single official page was fetched that gives a canonical "buffer pool should be X% of RAM" numeric recommendation as an explicit rule — any such percentage figure circulating in secondary sources should be treated as community guidance, not an official documented threshold, unless a specific dev.mysql.com page stating that percentage is located separately.

---

## 9. Testing

[Source: https://dev.mysql.com/doc/extending-mysql/9.7/en/mysql-test-suite.html and https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_INTRODUCTION.html] MySQL's own test framework is called the **MySQL Test Suite**, driven by **`mysql-test-run.pl`**, located in the `mysql-test` directory of the source tree. The framework consists of a test-language interpreter (**`mysqltest`**), the Perl test runner (`mysql-test-run.pl`) that starts/restarts MySQL servers as needed per test case, test case files written in the mysqltest test language, and expected-result files that are diffed against actual output.

[Source: https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_MYSQL_TEST_RUN_PL.html] This documentation is scoped to testing the **MySQL server codebase itself** (used by MySQL's own developers/contributors and by anyone building MySQL from source who wants to run its regression suite) — it is not a general-purpose "how to test your application's use of MySQL" guide.

Unresolved / gap: The official reference manual does not appear to contain a dedicated "how to test applications against MySQL" chapter (e.g., no first-party guidance on ephemeral test databases, fixtures, or transactional test isolation patterns for application developers was found in this pass). Application-level testing guidance for MySQL-backed applications would need to come from the specific application framework/ORM's own docs rather than from dev.mysql.com, per this research. This is a genuine documentation gap for dimension 9, not an omission on the researcher's part.

---

## 10. Deployment

[Source: https://dev.mysql.com/doc/refman/9.7/en/docker-mysql-getting-started.html] MySQL is officially distributed as a Docker image via the **Oracle Container Registry**: `container-registry.oracle.com/mysql/community-server:<tag>` for Community Edition; Enterprise Edition images require OCR authentication/license acceptance or a downloadable tarball loaded via `docker load`.

[Source: https://dev.mysql.com/doc/refman/9.7/en/docker-mysql-getting-started.html] Documented basic container lifecycle: `docker run --name=<name> --restart on-failure -d <image>:<tag>`; retrieve the auto-generated root password via `docker logs <name> 2>&1 | grep GENERATED`; then `ALTER USER 'root'@'localhost' IDENTIFIED BY '<password>'` to set a real password. Data/config persistence is achieved via bind-mounted volumes (`--mount type=bind,src=...,dst=/var/lib/mysql` for the data directory, and similarly for a custom `my.cnf`).

[Source: https://dev.mysql.com/doc/refman/9.7/en/docker-mysql-getting-started.html] **Documented limitation:** official MySQL Docker images are built for **Linux platforms only**; other platforms are explicitly called out as unsupported for the image itself (host OS can be non-Linux via Docker Desktop's Linux VM, but the image target is Linux).

[Source: https://dev.mysql.com/doc/refman/9.7/en/upgrading.html] Beyond Docker, the manual documents installation/deployment via native OS packages and repositories: the MySQL **Yum Repository**, **APT Repository**, and **SLES Repository** for Linux, plus native Windows installers and a Windows **MySQL Configurator**.

---

## 11. Migration (Upgrading Between Major Versions)

[Source: https://dev.mysql.com/doc/refman/9.7/en/upgrade-paths.html] Documented supported upgrade paths: within an LTS/bugfix series (e.g., 8.0.37 → 8.0.41, in-place upgrade, dump/load, replication, or MySQL Clone); from an LTS/bugfix series to the next LTS series (e.g., 8.0.37 → 8.4.x); from an LTS/bugfix release to an Innovation release released before the next LTS (e.g., 8.4.0 → 9.2.0); from an Innovation series to the next LTS (e.g., 8.3.0 → 8.4 LTS); and within an Innovation series (e.g., 8.1.0 → 8.3.0). All support in-place upgrade, logical dump-and-load, and replication as migration mechanisms unless otherwise noted.

[Source: https://dev.mysql.com/doc/refman/9.7/en/upgrade-paths.html] **Hard restriction, explicitly documented:** a bugfix or LTS series **cannot be skipped** — for example, MySQL 5.7 must go to 8.0 before going to 8.4; you cannot jump 5.7 → 8.4 directly, nor skip an LTS series (e.g., cannot go straight from an Innovation release to a *later* LTS bypassing the intervening one). Also, innovation-to-innovation upgrades cannot skip across an LTS boundary — e.g. to get from an 8.x Innovation release to a 9.x Innovation release you must pass through the 8.4 LTS release first.

[Source: https://dev.mysql.com/doc/refman/9.7/en/upgrade-paths.html] The documented recommended pre-upgrade step is running the **MySQL Shell Upgrade Checker Utility**, and for replicated topologies, following the documented **rolling upgrade scheme** rather than upgrading all servers at once.

[Source: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html] **Version-sensitive migration blocker:** prior to upgrading to 8.4, any table using `FLOAT`/`DOUBLE` columns with `AUTO_INCREMENT` must be altered first — the manual states such a table "cannot be upgraded" otherwise, because AUTO_INCREMENT on FLOAT/DOUBLE was removed (not just deprecated) as of 8.4.0.

[Source: https://dev.mysql.com/doc/refman/9.7/en/upgrading.html] Downgrading is documented as a separate, more restricted operation from upgrading (in-place downgrade is only supported within certain narrow windows; the general downgrade path is dump/load or replication-based rollback) — see Version Information section below for the specific downgrade-support matrix per release track.

[Inference, not confirmed in docs] The manual's structure treats "migrating from a comparable alternative RDBMS into MySQL" as out of scope for the core Reference Manual; no such migration guide was located at dev.mysql.com in this pass — only version-to-version MySQL upgrade paths are covered as official first-party migration documentation.

---

## 12. Version Information

[Source: https://dev.mysql.com/doc/refman/9.7/en/mysql-releases.html] MySQL's dual-track release model: **Innovation releases** (formerly quarterly-cadence minor versions like 8.1, 8.2, 8.3, 9.0, 9.1...) carry new features, behavior changes, deprecations, and removals, and are supported only until the next Innovation release ships. **LTS releases** (e.g., 8.4, 9.7) ship on a roughly ~2-year cadence, receive bug/security fixes only (no new features or removals after the first LTS release in a series, e.g. 8.4.0), and carry Oracle's standard **5 years premier + 3 years extended = 8 years total** support lifecycle.

[Source: https://blogs.oracle.com/mysql/a-more-predictable-mysql-release-model-calendar-versions-lts-and-innovation] **As of ~June 2026, this changed for future Innovation releases**: sequential `MAJOR.MINOR.PATCH` numbering is retired after 9.7; new Innovation releases use calendar-based `YY.M.P` versioning (e.g., 26.7.0 = July 2026, 26.10.0 = scheduled October 2026 Innovation release). Once a specific calendar-versioned release is designated LTS, its `YY.M` prefix is fixed for that LTS line's entire support lifecycle (example given in sources: a hypothetical `28.4.10` would still be part of an LTS line that launched April 2028).

[Source: https://blogs.oracle.com/mysql/mysql-july-2026-ga-releases-now-available] The July 2026 GA wave: **MySQL 26.7.0** (first Innovation release under new calendar versioning), **MySQL 9.7.2 LTS**, **MySQL 8.4.11 LTS**, **MySQL Workbench 26.7**.

[Source: https://www.mysql.com/support/eol-notice.html] Official EOL notice: **MySQL 5.7** moved to Oracle Lifetime Sustaining Support as of **October 25, 2023** (5.7 EOL October 2023). **MySQL 8.0** moved to Oracle Lifetime Sustaining Support as of **April 21, 2026** ("Users are encouraged to upgrade to MySQL 8.4 LTS or 9.7 LTS.").

[Source: search-derived from official EOL/support pages, not independently WebFetched in full] Currently supported LTS lines per official support material located: **MySQL 8.4 LTS**, end of life around **April 30, 2032**; **MySQL 9.7 LTS**, end of life around **April 21, 2034** (8 years each from their respective LTS GA dates, consistent with the documented 5+3-year support policy). Unresolved: I was not able to independently WebFetch a single official page stating both exact 8.4 and 9.7 EOL dates verbatim in this pass — these dates are derived from a WebSearch summary of official EOL announcement content and should be re-verified directly against https://www.mysql.com/support/eol-notice.html before being treated as load-bearing in a skill.

**Current stable/latest as of 2026-09-09:** [Source: https://blogs.oracle.com/mysql/mysql-july-2026-ga-releases-now-available] MySQL 26.7.0 is the latest Innovation release (July 2026); MySQL 9.7.2 and MySQL 8.4.11 are the latest patch releases of the two currently-supported LTS lines as of that same July 2026 wave. A later patch release may exist by 2026-09-09 that was not captured in this research pass — treat 26.7.0 / 9.7.2 / 8.4.11 as "latest known as of the July 2026 GA announcement," not necessarily "latest as of today."

---

## 13. Breaking Changes (Recent Major-Version)

All items below are **version-sensitive to the 8.0 → 8.4 LTS transition** specifically, per [Source: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html] ("Changes in MySQL 8.4.0"):

- **Replication SQL syntax removed** (not merely deprecated): `START SLAVE`/`STOP SLAVE`/`SHOW SLAVE STATUS`/`CHANGE MASTER TO`/`RESET SLAVE`/`SHOW MASTER STATUS` are removed in favor of `START REPLICA`/`STOP REPLICA`/`SHOW REPLICA STATUS`/`CHANGE REPLICATION SOURCE TO`/`RESET REPLICA`/`SHOW BINARY LOG STATUS`. Applications issuing the old syntax will error, not just warn.
- **`mysql_native_password` disabled by default**; must be explicitly turned on if legacy clients need it.
- **`default_authentication_plugin` variable removed**, replaced by `authentication_policy`.
- **`AUTO_INCREMENT` on `FLOAT`/`DOUBLE` columns removed** as an error condition (was deprecated in 8.0) — pre-upgrade schema changes required, or the table cannot be upgraded.
- **Utilities removed:** `mysql_upgrade` (deprecated since 8.0.16), `mysqlpump` (plus its `lz4_decompress`/`zlib_decompress` helpers), `mysql_ssl_rsa_setup`. Replacements: automatic server-driven upgrade for `mysql_upgrade`; `mysqldump` or MySQL Shell dump utilities for `mysqlpump`; automatic SSL/RSA generation by the server for `mysql_ssl_rsa_setup`.
- **`SET_USER_ID` privilege removed**; `GRANT SET_USER_ID ...` is now a syntax error. Replacement: `SET_ANY_DEFINER` + `ALLOW_NONEXISTENT_DEFINER`.
- **`authentication_fido`/`authentication_fido_client` plugins removed**, replaced by `authentication_webauthn`.
- **Keyring plugins removed** in favor of component equivalents: `keyring_file`→`component_keyring_file`, `keyring_encrypted_file`→`component_keyring_encrypted_file`, `keyring_oci`→`component_keyring_oci`.
- **`--ssl`, `--skip-ssl`, `--admin-ssl` options and `have_ssl`/`have_openssl` variables removed**, replaced by `--tls-version`/`--admin-tls-version`.
- **`INFORMATION_SCHEMA.TABLESPACES` table removed**; use `INNODB_TABLESPACES`/`INNODB_DATAFILES` instead.
- **`LOW_PRIORITY` with `LOCK TABLES` removed** (syntax error).
- **Column index-prefix support in partitioning keys removed** — a previously-deprecated pattern (`PARTITION BY KEY(id, name(10))`) is now a hard error at `CREATE TABLE`/`ALTER TABLE` time.
- **Non-unique/partial-key foreign keys restricted by default** via `restrict_fk_on_non_standard_key` (default now restrictive).
- **Direct MySQL 5.7 → 8.4 in-place upgrade not supported** — must go through 8.0 first (consistent with the general "cannot skip an LTS series" rule in Section 11 above).
- **Group Replication:** special-case handling for members running 8.0.17 or earlier is removed — all Group Replication members must be on a recent 8.0 patch before upgrading to 8.4; the default consistency level for Group Replication changed to `BEFORE_ON_PRIMARY_FAILOVER`.

Unresolved: This research pass did not fetch a dedicated "Changes in MySQL 9.x" or "Changes in MySQL 26.7.0" breaking-changes page, so **breaking changes specific to the 8.4→9.7 LTS transition, or to the new 26.7.0 calendar-versioned Innovation release, are not enumerated here** and should be separately researched (likely at `https://dev.mysql.com/doc/relnotes/mysql/9.7/en/` and whatever relnotes path Oracle uses for the 26.x line) before being relied on in a skill.

---

## 14. Limitations (Explicitly Documented Constraints)

[Source: https://dev.mysql.com/doc/refman/9.7/en/column-count-limit.html] MySQL has a **hard limit of 4096 columns per table** (server-level general limit), though the practical/effective maximum for a given table may be lower depending on column types and row-size limits. The **maximum row size is 65,535 bytes** for the internal row representation, even when the storage engine could in principle support larger rows; `BLOB`/`TEXT` columns count only 9–12 bytes toward this limit because their content is stored out-of-row.

[Source: https://dev.mysql.com/doc/refman/9.7/en/innodb-limits.html — via search summary, page itself returned inconsistent direct-fetch results] Documented InnoDB-specific limits: **maximum ~1,017 columns per InnoDB table** (including virtual generated columns — lower than the general 4096 limit); **maximum 64 secondary indexes per table**; **maximum 16 columns per multi-column index**; index key prefix length limits of **3,072 bytes** (DYNAMIC/COMPRESSED row format) or **767 bytes** (REDUNDANT/COMPACT row format), proportionally reduced for smaller `innodb_page_size` settings; maximum InnoDB row size is slightly less than half a page (e.g., roughly 8KB for the default 16KB page size); combined InnoDB log files capped at **512GB**; maximum tablespace size scales with page size, from **16TB at 4KB pages up to 256TB at 64KB pages**; up to **2³² tablespaces** and **2³² tables per shared tablespace**.

[Source: https://dev.mysql.com/doc/refman/9.7/en/group-replication.html] Group Replication is explicitly documented as **not providing client-side failover on its own** — a connector with failover logic, a load balancer, or MySQL Router is required; this is documented as the reason InnoDB Cluster (which bundles Router) is the recommended production path rather than bare Group Replication.

[Source: https://dev.mysql.com/doc/refman/9.7/en/docker-mysql-getting-started.html] Official MySQL Docker images are documented as **Linux-only**; other platforms are explicitly stated as unsupported for the image build itself.

Unresolved: The InnoDB limits figures above were captured via a WebSearch tool summary of the `innodb-limits.html` page content, because a direct WebFetch of that exact URL path returned inconsistent results (one attempt 404'd on a slightly different path). The figures are consistent with what MySQL has documented across recent versions, but the specific page URL should be re-verified directly (try `https://dev.mysql.com/doc/refman/9.7/en/innodb-limits.html`) before being cited as a primary source in downstream skill content.

---

## 15. Debugging

[Source: https://dev.mysql.com/doc/refman/9.7/en/error-log.html] The **error log** is the primary diagnostic facility: it records server startup/shutdown, errors/warnings/notes during operation, diagnostic messages (e.g., automatic table check/repair events), and stack traces on abnormal server exit. On restart, MySQL can recover unprocessed stack traces from a previous crash and emit each trace line as a discrete event tagged `ER_STACK_BACKTRACE`.

[Source: https://dev.mysql.com/doc/refman/9.7/en/error-log.html] Error log content can be configured for multiple destinations (file, syslog, Windows Event Log) and formats (traditional text, JSON), with **priority-based filtering** (`log_filter_internal`) and **rule-based filtering** (`log_filter_dragnet`) components documented as the two filtering mechanisms. Error log content is also queryable via the Performance Schema `error_log` table.

[Source: https://dev.mysql.com/doc/refman/9.7/en/error-log.html] Beyond the error log, the manual documents the **general query log** (records all SQL statements received), the **slow query log** (records queries exceeding a configurable execution-time threshold), and the **binary log** (records data-modifying statements, primarily for replication/point-in-time recovery, but usable as a secondary debugging/audit trail) as the other first-party logging facilities. A dedicated "Debugging MySQL" section (Section 7.9 per the TOC reference found) exists for deeper crash/stack-trace analysis procedures.

[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html] For query-level debugging (as opposed to server-level), `EXPLAIN` (including its extended/JSON output formats) and **optimizer tracing** are the documented tools for understanding why the optimizer chose a particular execution plan.

Unresolved: The dedicated "Debugging MySQL" chapter (Section 7.9, referenced by URL pattern `debugging-mysql.html`) was identified by reference but not independently fetched and read in full during this pass — its detailed content (e.g., core dump analysis, using a debugger against `mysqld`, `--debug` build options) is not captured here beyond confirming the section exists and covers stack-trace/crash analysis.

---

## 16. Integration

[Source: https://dev.mysql.com/doc/refman/9.7/en/connectors-apis.html] First-party integration surfaces documented: JDBC via Connector/J (Java ecosystem), ADO.NET via Connector/NET (.NET ecosystem), ODBC via Connector/ODBC (cross-language via the ODBC standard), native Python driver via Connector/Python, native Node.js driver via Connector/Node.js (X Protocol/document-store aware), and the C API (`libmysqlclient`) as the lowest-level integration point that most other language bindings build on.

[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html] Documented enterprise-identity integration points: **PAM**, **LDAP**, **Kerberos**, and **OpenID Connect** authentication plugins integrate MySQL account authentication with external identity systems; the **Keyring** integrates with external key-management systems (AWS KMS, HashiCorp Vault, OCI Vault, KMIP-compliant appliances) for encryption-at-rest key storage.

[Source: https://dev.mysql.com/doc/refman/9.7/en/group-replication.html] **MySQL Router** is documented as the integration/routing layer that sits between applications and an InnoDB Cluster/Group Replication topology, providing transparent connection routing to the current primary (or read replicas) without requiring the application to implement its own failover-aware connection logic.

[Source: https://dev.mysql.com/doc/refman/9.7/en/docker-mysql-getting-started.html] Container/orchestration integration is documented at the Docker level (official Oracle Container Registry images); the manual references further container topics (Kubernetes-oriented material was referenced by URL pattern but not independently fetched in this pass — see `docker-mysql-more-topics.html`).

Unresolved: I did not independently fetch a dedicated Kubernetes/MySQL Operator integration page in this pass (a `mysql/mysql-operator` product exists per general Oracle MySQL ecosystem knowledge, but I did not verify current official documentation for it against dev.mysql.com in this research session) — flag as **Unresolved: MySQL Operator / Kubernetes-native deployment documentation not directly verified in this pass.**

---

## 17. Production Considerations

[Source: https://dev.mysql.com/doc/refman/9.7/en/backup-and-recovery.html] Documented backup tooling for production: **`mysqldump`** (logical/SQL-format backups, used also for cross-server copies, upgrade-compatibility testing, and stored-program extraction), **MySQL Enterprise Backup** (Enterprise Edition, physical backup tool built for production), **MySQL Shell dump/load utilities** (modern logical backup/restore, integrated with InnoDB Cluster tooling), and **binary log retention** for point-in-time recovery layered on top of periodic full backups.

[Source: https://dev.mysql.com/doc/refman/9.7/en/backup-and-recovery.html] Documented high-availability alternatives to backup-based recovery for production continuity: standard **replication** (near-real-time redundant copies with no backup-window impact on the source), **InnoDB Cluster** (multi-server HA with automatic failover), and **MySQL NDB Cluster** (high-redundancy, shared-nothing clustering for the most demanding availability requirements).

[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html] Production security guidance documented across the Security chapter includes: minimal-privilege account design, network-level access restriction, mandatory TLS/SSL for connections, strong password policy enforcement (Password Validation Component), audit logging (Audit Log Component), and brute-force mitigation (Connection Control Component) — these are presented as a defense-in-depth checklist rather than optional add-ons for production deployments.

[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html] Production performance guidance is centered on Performance Schema-based continuous monitoring (rather than one-off `EXPLAIN` checks alone), proper InnoDB buffer pool sizing, and disk I/O optimization as the primary levers documented for keeping a production instance healthy under load.

[Source: https://dev.mysql.com/doc/refman/9.7/en/upgrade-paths.html] Production upgrade guidance: test upgrades on a non-production system first, use the MySQL Shell Upgrade Checker Utility beforehand, and — for replicated/clustered production topologies — perform rolling upgrades (replicas/secondaries before the source/primary) rather than a simultaneous cutover.

---

## Sources Cited (deduplicated)

- https://dev.mysql.com/doc/refman/9.7/en/manual-info.html
- https://dev.mysql.com/doc/refman/9.7/en/mysql-releases.html
- https://dev.mysql.com/doc/refman/9.7/en/
- https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html
- https://dev.mysql.com/doc/refman/9.7/en/pluggable-storage-overview.html
- https://dev.mysql.com/doc/refman/9.7/en/security.html
- https://dev.mysql.com/doc/refman/9.7/en/server-configuration.html
- https://dev.mysql.com/doc/refman/9.7/en/connectors-apis.html
- https://dev.mysql.com/doc/refman/9.7/en/optimization.html
- https://dev.mysql.com/doc/refman/9.7/en/upgrading.html
- https://dev.mysql.com/doc/refman/9.7/en/upgrade-paths.html
- https://dev.mysql.com/doc/refman/9.7/en/replication.html
- https://dev.mysql.com/doc/refman/9.7/en/group-replication.html
- https://dev.mysql.com/doc/refman/9.7/en/docker-mysql-getting-started.html
- https://dev.mysql.com/doc/refman/9.7/en/error-log.html
- https://dev.mysql.com/doc/refman/9.7/en/backup-and-recovery.html
- https://dev.mysql.com/doc/refman/9.7/en/column-count-limit.html
- https://dev.mysql.com/doc/refman/9.7/en/innodb-limits.html
- https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html
- https://dev.mysql.com/doc/extending-mysql/9.7/en/mysql-test-suite.html
- https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_INTRODUCTION.html
- https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_MYSQL_TEST_RUN_PL.html
- https://blogs.oracle.com/mysql/a-more-predictable-mysql-release-model-calendar-versions-lts-and-innovation
- https://blogs.oracle.com/mysql/mysql-july-2026-ga-releases-now-available
- https://www.mysql.com/support/eol-notice.html

## Unresolved Items (consolidated)

1. Whether MySQL 9.7 LTS will itself eventually be renumbered under the new calendar-versioning scheme, or remains a permanently legacy-numbered LTS line.
2. Exact official EOL dates for MySQL 8.4 LTS and 9.7 LTS were derived from a search-engine summary of official EOL material rather than a direct full WebFetch of https://www.mysql.com/support/eol-notice.html with those exact dates visible in the fetched text — needs direct re-verification.
3. Breaking changes specific to the 8.4→9.7 LTS transition, and to the new 26.7.0 calendar-versioned Innovation release, were not enumerated (only 8.0→8.4 breaking changes were fully researched).
4. The `innodb-limits.html` page was fetched inconsistently (one direct WebFetch 404'd); figures were sourced via a search-tool summary rather than a clean direct fetch and should be re-verified at the primary URL.
5. Official Kubernetes/MySQL Operator integration documentation was not independently verified in this research pass.
6. No first-party "testing your application against MySQL" guidance (as distinct from MySQL's own internal test suite for server development) was found in the official docs — this appears to be a genuine gap in official documentation coverage for dimension 9, not a research oversight.
7. X DevAPI / C API compatibility and versioning guarantees were not fully verified against a dedicated compatibility-policy page.
