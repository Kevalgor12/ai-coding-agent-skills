# ClickHouse — Technology Research

Research date: 2026-09-09. Primary source: `clickhouse.com/docs/*` (canonical documentation host — confirmed reachable and current at time of research). Secondary official sources used for location purposes only (never as sole citation): the `ClickHouse/ClickHouse` and `ClickHouse/clickhouse-docs` GitHub repositories (source of truth for docs content — the docs site is generated from `ClickHouse/clickhouse-docs`, which the project's own README states has since been folded back into `ClickHouse/ClickHouse/tree/master/docs`), and `clickhouse.com/blog/*` official release-announcement posts. Third-party sources (`endoflife.date`, `releases.sh`, Wikipedia) were used only to help locate/cross-check official pages during search and are not cited as claims below.

All claims are tagged per this project's convention: `[Source: <url>]` for documented facts, `[Inference, not confirmed in docs]` for reasoning, "Not documented / could not verify" where docs did not cover something, and "Unresolved: ..." where confidence is genuinely low.

**Doc host note**: [Source: https://clickhouse.com/docs] The canonical docs live at `clickhouse.com/docs/<section>/<page>`, reorganized into `get-started/`, `architecture/`, `guides/`, `reference/`, `products/`, and `integrations/` top-level sections. [Inference, not confirmed in docs] Some older URL forms encountered during this research (e.g. paths under `/docs/en/...`, or `/docs/introduction/...`) redirected or 404'd, suggesting the site has undergone at least one internal restructuring (old `introduction/distinctive_features` → new `about-us/distinctive-features`; old `cloud/bestpractices/avoid-nullable-columns` → new `best-practices/avoid-nullable-columns` / `optimize/avoid-nullable-columns`) — treat any older/blog-referenced ClickHouse doc URL as a candidate for staleness and re-resolve via search rather than assuming it's live. The underlying docs source-of-truth also appears to have moved from a standalone `ClickHouse/clickhouse-docs` repo into the main `ClickHouse/ClickHouse` monorepo per that repo's own description, which is the kind of host/location move this project's instructions ask to flag explicitly.

---

## 1. Core concepts

[Source: https://clickhouse.com/docs] ClickHouse is a **column-oriented SQL database management system (DBMS)** built for **online analytical processing (OLAP)** — fast computation of aggregations and analytical queries over very large datasets, rather than low-latency single-row transactional access.

[Source: https://clickhouse.com/docs] The defining architectural idea is **columnar storage**: data is physically organized and stored by column rather than by row, so a query touching only a few columns of a wide table reads only those columns from disk, avoiding I/O for irrelevant data. The docs illustrate this with a benchmark query scanning 100 million rows across a handful of columns completing "within milliseconds," at throughput "approximately over 1 billion rows per second."

[Source: https://clickhouse.com/docs/get-started/about/deployment-modes] ClickHouse ships in five distinct forms sharing "the same powerful database engine, just packaged differently": (1) **ClickHouse Server** — traditional client/server, self-hosted or cloud-VM-hosted, single node or clustered; (2) **ClickHouse Cloud** — fully managed SaaS; (3) **ClickHouse CLI** (`clickhousectl`) — a tool for local dev and Cloud management; (4) **clickhouse-local** — a standalone executable providing full ClickHouse SQL functionality without a server process, for ad-hoc analysis of local files or cloud storage; (5) **chDB** — ClickHouse embedded as an in-process engine, primarily for Python but also Go, Rust, Node.js, and Bun, integrating with Pandas/Arrow.

[Source: https://clickhouse.com/docs/architecture/introduction] Core distributed-systems vocabulary used throughout the docs: a **replica** is "a copy of data" (ClickHouse always has at least one, so the "original" copy also counts as a replica); a **shard** is "a subset of data," used to split load across multiple servers via a sharding key, with a table having at least one shard by default (i.e., unsharded = single shard).

[Source: https://clickhouse.com/docs] Key documented features: asynchronous multi-master **replication**; SQL-based **role-based access control** resembling the ANSI SQL standard; broad **SQL compatibility** (`GROUP BY`, JOINs, window functions, subqueries); and built-in **approximate calculation** functions (approximate distinct counts, quantiles) that trade exactness for speed.

[Source: https://clickhouse.com/docs/about-us/distinctive-features] Distinctive features documented: true column-oriented storage with no extra per-value overhead; per-column-type specialized compression codecs; parallel distributed query processing across shards/replicas; asynchronous multi-master replication (writes to any replica propagate to others in the background); aggressive use of available CPU/RAM/IO for each query; approximate aggregate functions (distinct count, median, quantiles); and a "flexible" runtime schema — tables/databases can be created, and data loaded and queried, without reconfiguring or restarting the server.

[Source: https://clickhouse.com/docs/en/introduction/features_considered_disadvantages] ClickHouse's own documentation explicitly lists limitations that also function as "what ClickHouse is not": (1) no full/general-purpose transaction support; (2) it cannot efficiently modify or delete already-inserted rows at high rate/low latency — batch-style cleanup (e.g. for GDPR) is supported, but that is different from OLTP-style row updates; (3) the sparse primary index makes ClickHouse comparatively inefficient for point queries retrieving single rows by key. These reflect a deliberate OLAP-over-OLTP design trade-off. Note: this specific URL uses an older `/en/introduction/...` path form; see the doc-host note above.

---

## 2. Architecture

[Source: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree] The **MergeTree** family is ClickHouse's primary table-engine family, "engineered for high data ingest rates and huge data volumes." Storage/organization hierarchy: table → **partitions** → **parts** → **granules** → rows. On `INSERT`, data lands as a new, immutable **part**, sorted by the table's primary/`ORDER BY` key; a background **merge** process periodically combines parts within the same partition into larger parts for efficiency (parts in different partitions are never merged together).

[Source: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree] Two on-disk part layouts exist: **wide format** (one file per column; the default for larger parts) and **compact format** (all columns in a single file; used for small/frequent-insert parts).

[Source: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree] The primary key produces a **sparse index**, not a per-row index: rows are grouped into **granules** of (by default) ~8,192 rows, and the index stores one "mark" per granule rather than per row. This keeps "primary keys of huge data sets small enough to remain loaded in main memory, while still providing fast access to on-disk data." Primary keys need not be unique, and Nullable expressions are technically permitted in a primary key though discouraged (per best-practices guidance elsewhere in the docs).

[Source: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree] **Partitioning** splits data by an arbitrary expression (commonly a time bucket, e.g. `toYYYYMM(date_column)`) to enable **partition pruning** (skip whole partitions irrelevant to a query) and lifecycle operations (drop/move whole partitions cheaply). The docs are explicit that "partitioning does not speed up queries" in general — it is primarily a data-management tool, not a query-acceleration tool.

[Source: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree] Concurrency: reads and writes use a multi-versioning scheme allowing concurrent read/insert without locking; longer primary keys cost more at insert time and in memory; over-granular partitioning adds overhead without benefit.

[Source: https://clickhouse.com/docs/architecture/introduction] Distributed coordination — for data replication and distributed DDL execution — is handled by **ClickHouse Keeper**, described as providing "the coordination system for data replication and distributed DDL queries execution," compatible with the Apache ZooKeeper protocol/API.

[Source: https://github.com/ClickHouse/ClickHouse — located via search, not separately fetched] [Inference, not confirmed in docs] ClickHouse Keeper is a from-scratch C++ reimplementation (using the Raft consensus algorithm) of ZooKeeper's coordination semantics, intended as a drop-in replacement so operators need not run a separate Java/ZooKeeper cluster; this is stated with lower confidence because the dedicated Keeper overview page (`guides/sre/keeper/...`) 404'd during this research pass and was not independently confirmed by a fetched official page — see Unresolved items.

Not documented / could not verify in pages fetched: a single consolidated description of the query-execution engine internals (vectorized execution, the query pipeline/processor framework) — search located references to these concepts but no official architecture page describing them was successfully fetched in this research pass.

---

## 3. APIs

[Source: https://clickhouse.com/docs/interfaces/overview] ClickHouse documents two core network protocols: the **HTTP interface** ("documented and easy to use directly") and the **Native TCP protocol** (described as lower-overhead than HTTP).

[Source: https://clickhouse.com/docs/interfaces/overview] Official client tooling includes a command-line client, an **ADBC** driver, a **JDBC** driver, an **ODBC** driver, and a **C++ client library**, plus third-party/community language client libraries and GUI tools listed separately in the integrations catalog.

[Source: https://clickhouse.com/docs/interfaces/overview] RPC-style protocol support: a custom **gRPC** protocol, and **Apache Arrow Flight** support.

[Source: https://clickhouse.com/docs/interfaces/overview] Built-in embedded web UIs served by the server itself: **Play UI** (`/play`), the **Advanced Dashboard** (`/dashboard`), a binary-symbols viewer (`/binary`), and a ClickStack observability UI (`/clickstack`).

[Source: https://clickhouse.com/docs/interfaces/mysql] ClickHouse implements **MySQL wire-protocol compatibility**, letting MySQL-only clients/BI tools (validated against Looker Studio, Tableau Online, Amazon QuickSight) connect without a native ClickHouse driver. Default port 3306 on ClickHouse Cloud, commonly port 9004 self-managed (configured via `mysql_port`). Documented caveats: SSL/TLS support "might not be fully compatible" (potential TLS-SNI issues); some MySQL-specific dialect functions/settings are unimplemented; **prepared queries are not supported** through this interface; it is not guaranteed to be a drop-in replacement for MySQL application code. Cloud users needing SNI-less TLS routing must use a `mysql4<subdomain>_<username>` username convention.

[Source: https://clickhouse.com/docs/guides/sre/network-ports] A **PostgreSQL wire-protocol emulation** interface also exists, default port 9005 (`postgresql_port`), alongside the other protocol ports (see Configuration section for full port table).

[Inference, not confirmed in docs] The presence of both MySQL- and Postgres-protocol emulation ports strongly implies both wire protocols are documented compatibility interfaces analogous to `interfaces/mysql`; a dedicated `interfaces/postgresql` page was referenced by the ports listing but not independently fetched in full in this pass.

[Source: https://clickhouse.com/docs] SQL itself — `CREATE`/`ALTER`/`DROP`, `INSERT`, `SELECT`, and ClickHouse-specific DDL like `CREATE MATERIALIZED VIEW` and `ALTER TABLE ... DROP PARTITION` — is the primary "API" surface for interacting with the database, documented in the SQL reference section of the docs.

---

## 4. Configuration

[Source: https://clickhouse.com/docs/operations/configuration-files] The server reads `/etc/clickhouse-server/config.xml` by default (overridable at startup); both **XML and YAML** formats are supported (not mixed within a single file — the YAML parser auto-wraps content in a `clickhouse:` root tag if omitted, and YAML sequences map to repeated XML tags with `@`-prefixed attribute syntax).

[Source: https://clickhouse.com/docs/operations/configuration-files] User/profile/quota settings live in a separate `users.xml`, referenced from `config.xml` via the `users_config` element.

[Source: https://clickhouse.com/docs/operations/configuration-files] **Modular overrides are the documented best practice**: "it is a best practice to keep the default config.xml file unmodified and place additional customization into config.d/" (and analogously `users.d/` for user config). Files in these directories merge in lexicographical order, using recursive node merging by default, with `replace="replace"` to fully override a node and `remove="remove"` to delete one.

[Source: https://clickhouse.com/docs/operations/configuration-files] Dynamic value substitution is supported three ways: environment variables (`from_env="VAR_NAME"`), ZooKeeper/Keeper nodes (`from_zk="/path"`), and file/subtree inclusion (`incl` attribute for value substitution, `include` element for whole subtrees) — a `replace="1"`-style default can accompany these.

[Source: https://clickhouse.com/docs/operations/configuration-files] Sensitive config values can be stored encrypted via symmetric-encryption codecs using the `encrypted_by` attribute; `hide_in_preprocessed="true"` keeps encrypted values out of the server's generated preprocessed config file.

[Source: https://clickhouse.com/docs/operations/configuration-files] The server writes out a **preprocessed config file** and watches the original files for changes; user/cluster/settings-level config changes reload live without a server restart (other structural changes may still require restart — not exhaustively enumerated in the fetched excerpt).

[Source: https://clickhouse.com/docs/guides/sre/network-ports] Documented default network ports: **8123** HTTP; **8443** HTTP over TLS; **9000** Native/TCP protocol; **9009** inter-server data-exchange/replication port; **9010** inter-server TLS; **9004** MySQL wire-protocol emulation; **9005** PostgreSQL wire-protocol emulation; **9181** ClickHouse Keeper client port (recommended); **9234** Keeper Raft port (recommended); **9363** Prometheus metrics; **9019** JDBC bridge; **9100** gRPC; **42000** Graphite metrics. All are reconfigurable via `config.d/` overrides.

---

## 5. Recommended patterns

[Source: https://clickhouse.com/docs/best-practices] The official best-practices index enumerates these topics as the primary documented guidance surface: choosing a primary key; selecting data types; using materialized views to shift computation from query time to insert time; minimizing/optimizing JOINs; choosing a partitioning key; selecting an insert strategy; using data skipping indices; avoiding mutations; avoiding `OPTIMIZE ... FINAL`; avoiding Nullable columns; using the JSON type "where appropriate."

[Source: https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy] **Insert strategy**: batch inserts — "batching inserts reduces the overhead as a proportion of total insert time" — with a recommended minimum of ~1,000 rows per batch and an ideal range of **10,000–100,000 rows** per insert. Keep insert-query frequency around **~1 per second**; frequent small inserts create excess parts, triggering background-merge pressure and potential "too many parts" errors. Where client-side batching isn't feasible (e.g. many small-payload observability agents), use **async inserts** (`async_insert=1`), which shifts buffering to the server, flushing on size/time/count thresholds; the docs strongly recommend keeping `wait_for_async_insert=1` (the default) so the insert is acknowledged only once flushed to disk, preserving durability guarantees.

[Source: https://clickhouse.com/docs/best-practices/minimize-optimize-joins] **JOINs**: prefer denormalization (shifting join work to insert/pre-processing time) when tables change infrequently; pick a JOIN algorithm deliberately — direct JOIN via dictionary for fastest point lookups, parallel hash for small/medium tables, grace hash or partial merge for large, memory-constrained joins; filter early/aggressively (ClickHouse pushes filters down automatically, but rewriting a side as a subquery can force pushdown); exploit sort-merge JOIN when joining on primary-key/sorted columns (skips an explicit sort step); keep JOIN count to roughly **3–4 per query**.

[Source: https://clickhouse.com/docs/best-practices/choosing-a-partitioning-key] **Partitioning key**: choose a **low-cardinality** key, docs suggest fewer than 100–1,000 distinct values; align with data lifecycle/retention needs (commonly time-bucketed) to enable cheap partition drops and tiered storage; start **without** partitioning and add it only for demonstrated data-management needs, not as a first-resort query optimization.

[Source: https://clickhouse.com/docs/best-practices/use-data-skipping-indices-where-appropriate] **Data skipping indices**: add only after type optimization, a strong primary key, and materialized views have been considered; effective for columns with high overall cardinality but low cardinality per granule/block, where filtering targets rare values. Documented index types: `minmax` (range queries on loosely sorted data), `set(N)` (low-cardinality columns), `text` (inverted index for tokenized full-text search), `bloom_filter` (probabilistic set-membership / "needle in haystack" queries), and the deprecated `tokenbf_v1`/`ngrambf_v1` Bloom-filter variants ([Version-sensitive] documented as deprecated as of ClickHouse **26.2+**). Docs caution that "if even a single matching value exists in a block, that entire block must still be read" — a misaligned skip index adds overhead without benefit.

[Source: https://clickhouse.com/docs/optimize/avoid-nullable-columns] **Avoid Nullable columns**: `Nullable(T)` stores a hidden `UInt8` "is-null" mask processed on every access, costing extra storage and "almost always negatively affects performance." Recommended alternative: use a sensible default value (empty string, `0`, or a sentinel like `-1`) instead of `Nullable`, reserving `Nullable` for cases where distinguishing "empty" from "genuinely absent" is a real business requirement.

[Source: https://clickhouse.com/docs/optimize/query-optimization] The documented query-optimization workflow has three entry points depending on what's known: **Diagnose** (start from a recurring slow-query pattern; use query history/resource stats to form a hypothesis), **Isolate** (start from one slow query with an unknown bottleneck; progressively simplify the query under controlled conditions), **Optimize** (start once the bottleneck is known; reduce data read, realign data layout, or precompute work). Emphasizes comparing baseline runs and testing one change at a time against a consistent benchmark, illustrated with the NYC Taxi dataset.

[Source: https://clickhouse.com/docs/faq/operations/production] For choosing a production version, the docs explicitly decline to hand down a single recommendation: "No external person knows better than you what's going on in your company's production environment." Recommended process: maintain a realistic pre-production environment (mirroring replication/sharding/multi-region topology) with automated tests against real ClickHouse instances; validate new releases there before rolling to production; prefer gradual/canary rollout; always read the changelog before upgrading. **Stable** releases (monthly, three latest receiving bug fixes) are the default recommendation; **LTS** releases are suggested only if organizational policy requires infrequent upgrades.

---

## 6. Anti-patterns

[Inference, not confirmed in docs] ClickHouse's best-practices pages are framed prescriptively/positively ("do X") rather than as an explicitly labeled anti-pattern catalog; the items below are the documented inverse of a stated recommendation.

[Source: https://clickhouse.com/docs/best-practices/avoid-mutations] **Frequent/large-scale mutations** (`ALTER TABLE ... UPDATE`/`DELETE`) are an anti-pattern: mutations "rewrite entire data parts affected by the change," causing disk I/O spikes even for small logical changes, cannot be undone once submitted, persist across restarts unless explicitly cancelled, and can produce inconsistent reads mid-mutation (queries may see a mix of mutated and unmutated parts). Documented alternatives: `ReplacingMergeTree`/`CollapsingMergeTree` engines for correction-at-merge/query semantics, **lightweight deletes** for row removal, and dropping whole partitions instead of row-level modification.

[Source: https://clickhouse.com/docs/best-practices] `OPTIMIZE TABLE ... FINAL` is documented as something to avoid: ClickHouse performs "smart background merges automatically," and forcing `FINAL` merges is unnecessary and costly absent a specific need.

[Source: https://clickhouse.com/docs/best-practices/minimize-optimize-joins] Anti-patterns called out for JOINs: unintended **Cartesian products** from multiple matches per key (use `ANY JOIN` when only one match is wanted); **excessive JOIN chains** (beyond ~3–4); JOINs that **spill to disk** (supported by some algorithms but "significantly degrades performance" — better to reduce intermediate state size than rely on disk spill); and **dictionary misuse** for many-to-many relationships, since dictionaries silently deduplicate keys and can silently drop data.

[Source: https://clickhouse.com/docs/best-practices/choosing-a-partitioning-key] **Over-partitioning** via a high-cardinality partition key, and choosing a partition key primarily to speed up queries rather than for data-lifecycle management, are both documented anti-patterns; both risk fragmenting data into too many parts and eventual "too many parts" errors.

[Source: https://clickhouse.com/docs/optimize/avoid-nullable-columns] Reflexive/default use of `Nullable(T)` columns without a genuine need to distinguish "empty" from "null" is documented as an anti-pattern due to the storage/performance overhead described above.

[Source: https://clickhouse.com/docs/knowledgebase/maximum_number_of_tables_and_databases] Creating very large numbers of databases/tables/partitions/parts is an anti-pattern at scale: docs recommend staying under **1,000 databases, 5,000 tables, 50,000 partitions, and 100,000 parts** per service, since table/partition count (not database count — "databases ... are more of a namespace and have no performance impact") affects server startup time; the server emits warnings as these thresholds are approached.

[Source: https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy] Sending many small, frequent insert statements (rather than batching or using async inserts) is documented as an anti-pattern, producing excess parts and background-merge/"too many parts" pressure.

---

## 7. Security

[Source: https://clickhouse.com/docs/operations/access-rights] Access control is **RBAC-based** with five entity types: **Users** (authenticate; hold privileges, allowed source hosts, assigned roles, default settings), **Roles** (containers bundling privileges/settings/nested roles), **Row Policies** (per-user/role row-level filtering applied at read time), **Settings Profiles** (bundles of configuration constraints), and **Quotas** (resource-consumption limits per time interval). Two parallel, simultaneously-usable configuration methods exist: the recommended **SQL-driven workflow** (`CREATE USER`, `GRANT`, `REVOKE`) and traditional **config-file** management (`users.xml`/`config.xml`); a site can migrate smoothly from config-file to SQL-driven management. Privilege grants are hierarchical (granting a parent privilege includes children); delegating a grant requires `WITH GRANT OPTION`; there is no privilege "lifetime" — privileges on a dropped table persist and must be explicitly revoked.

[Source: https://clickhouse.com/docs/security-and-authentication] Security/authentication documentation is organized under: **Users and Roles** (the RBAC system above), **Network Ports** (see Configuration section), **TLS** (configuring TLS for secure client connections), and **External Authenticators** (external authentication services supported in open-source ClickHouse — the fetched index page did not itself enumerate LDAP/Kerberos by name in the retrieved excerpt, so treat specific external-authenticator support as **Not documented in the pages fetched during this pass** rather than confirmed absent).

[Source: https://clickhouse.com/docs — search result summary, not independently fetched] [Inference, not confirmed in docs] Database user passwords may be configured to comply with NIST 800-63B guidance (minimum 12 characters plus complexity requirements), and SSH-key-based user authentication is supported; this was surfaced via search-result summarization of official pages rather than a directly fetched official page in this research pass, so it is flagged with lower confidence rather than a full citation. See Unresolved items below.

[Source: https://clickhouse.com/docs/guides/sre/network-ports] TLS-enabled variants of the core protocol ports exist: 8443 (HTTPS), 9010 (inter-server TLS); dedicated TLS-configuration guides (`guides/sre/tls/...`) were located via search but not independently fetched to full-text depth in this pass. A page at `guides/sre/network-security` referenced in search results returned HTTP 404 when fetched directly — flagged as a possibly-stale/reorganized URL rather than confirmed content.

[Source: https://clickhouse.com/docs/en/introduction/features_considered_disadvantages] As noted in Core Concepts, ClickHouse's data-modification model (no efficient low-latency row update/delete) has security-adjacent implications for compliance workflows (e.g. GDPR-style deletion), which the docs address via supported **batch** deletion/mutation rather than row-level operations — see Anti-patterns for why frequent mutations are still discouraged even for this purpose.

**Unresolved**: LDAP/Kerberos support specifics, and the precise password-policy/SSH-authentication claims above, were surfaced only via WebSearch result summaries of official-looking pages (`security-and-authentication`, and related `concepts/features/security` / `products/cloud/features/security` pages); direct WebFetch of the full `security-and-authentication` page returned only an index/navigation stub in this pass, and a follow-up fetch of the TLS/network-security detail page 404'd. Treat exact external-authenticator and password-policy details as needing re-verification against the live docs before being used as ground truth in a skill.

---

## 8. Performance

[Source: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree] Core performance levers live in MergeTree design: sparse primary-key index (keeps index resident in memory even for huge tables), partition pruning (skip whole partitions), background merges (fewer, larger parts read faster), and wide-vs-compact part format trade-offs for small vs. large inserts.

[Source: https://clickhouse.com/docs/optimize/query-optimization] The documented, structured optimization workflow (Diagnose → Isolate → Optimize) is described in Recommended Patterns above; it emphasizes evidence-driven changes (reduce data read, realign data layout, precompute) over speculative tuning.

[Source: https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy] Insert throughput is a first-class, separately documented performance concern (batch size 10k–100k rows ideal; async inserts for high-cardinality small-payload producers) — see Recommended Patterns.

[Source: https://clickhouse.com/docs/best-practices/minimize-optimize-joins] JOIN algorithm selection (direct/dictionary, parallel hash, grace hash, partial merge, sort-merge) is documented as a deliberate performance choice depending on table size and memory budget — see Recommended Patterns.

[Source: https://clickhouse.com/docs/best-practices/use-data-skipping-indices-where-appropriate] Data skipping indices (minmax/set/text/bloom_filter) are a documented secondary performance layer, applied only after primary-key and materialized-view design has been optimized — see Recommended Patterns.

[Source: https://clickhouse.com/docs/operations/performance-test] ClickHouse provides an official **hardware performance-test script** that can benchmark a server "without installation of ClickHouse packages," useful for validating whether hardware (not query design) is the bottleneck before deeper query-level tuning.

[Source: https://clickhouse.com/docs/about-us/distinctive-features] Approximate-computation functions (approximate `count(DISTINCT)`, quantiles/medians) are a documented performance/accuracy trade-off mechanism, allowing queries to sacrifice exactness for speed on very large datasets.

Not documented / could not verify in pages fetched: a single canonical page enumerating memory/CPU tuning settings (e.g. `max_threads`, `max_memory_usage`) with recommended production values — these individual settings are referenced across multiple pages (troubleshooting, configuration) but no consolidated "performance settings reference" page was fetched in full during this research pass.

---

## 9. Testing

[Source: https://clickhouse.com/docs/resources/develop-contribute/contribute/tests] This section documents how the **ClickHouse project itself** is tested (i.e., testing ClickHouse's own source code, relevant to anyone building/patching ClickHouse or deeply verifying its behavior), not a "how to test your application code against ClickHouse" guide. Documented test types: **Functional tests** (`.sql` and `.sh` scripts under `tests/queries`, run against a live server, comparing output to reference results — "mandatory ... for every change in ClickHouse code that can be tested that way"; subcategorized into fast/minimal, stateless (no DB population needed), and sequential (non-parallelizable) tests); **Integration tests** (Docker-based, multi-container, testing clustered ClickHouse plus external systems like MySQL/PostgreSQL/MongoDB, including network-partition/packet-drop emulation); **Unit tests** (isolated library/class-level tests built via the `ENABLE_TESTS` CMake option, run with `ninja test`, largely using `gtest`); **Performance tests** (XML-defined, under `tests/performance/`, looped synthetic-query benchmarks); **Stress tests** (all functional tests run in parallel, randomly ordered, against one server, checking for crashes, deadlocks, data-consistency issues, and clean restart); plus **sanitizer runs** (ASan/TSan/MSan/UBSan), **fuzzing** (libFuzzer plus random SQL-query generation), a **Thread Fuzzer**, and static analysis (clang-tidy, clang-static-analyzer, shellcheck).

[Source: https://clickhouse.com/docs/guides/generating-test-data] For generating synthetic/test data against a ClickHouse instance (application-facing, unlike the above), the docs note ClickHouse's own random-data-generation SQL functions are often sufficient without an external data generator, useful for benchmarking or exercising new schemas.

[Source: https://clickhouse.com/docs/operations/performance-test] The hardware performance-test script (see Performance section) doubles as a testing tool for validating a target machine before deployment.

Not documented / could not verify: an official, application-level "how to unit/integration-test code that talks to ClickHouse" guide (e.g. recommended test-container patterns, mocking strategies) was not located as a distinct official page during this research pass; the fetched testing content is specifically about testing ClickHouse server code, not client application code against it.

---

## 10. Deployment

[Source: https://clickhouse.com/docs/get-started/about/deployment-modes] Five deployment forms are documented (ClickHouse Server, ClickHouse Cloud, ClickHouse CLI, clickhouse-local, chDB) — see Core Concepts for detail on each.

[Source: https://clickhouse.com/docs/architecture/introduction] Deployment topology terminology (replica, shard) and the role of **ClickHouse Keeper** in coordinating replication and distributed DDL are documented at an introductory level; the docs point to a companion **example-recipe repository** (`github.com/ClickHouse/examples/tree/main/docker-compose-recipes/recipes`) — described as built by ClickHouse's own Support and Services team — as working starting-point topologies (single-node, replicated, sharded, etc.) rather than exhaustively documenting each topology inline on the architecture page itself.

[Source: https://clickhouse.com/docs/get-started/about/deployment-modes] **ClickHouse Cloud** is documented as removing operational burden entirely: "you don't need to worry about updates, backups, scaling, or security patches – these are all handled automatically," and bundles ClickPipes (ingestion), a query API, an interactive SQL Console with dashboarding, and built-in query-insight monitoring.

[Source: https://clickhouse.com/docs] A **Kubernetes Operator** for ClickHouse is documented as one of the products under `products/kubernetes-operator/...` (confirmed via a fetched TLS-configuration sub-page referencing "Securing a cluster with TLS" for the operator); this indicates official Kubernetes deployment support, though a dedicated Kubernetes-operator overview page was not independently fetched in full during this pass.

Not documented / could not verify in pages fetched: an exhaustive, single "production deployment topology" reference page (e.g. minimum recommended cluster sizes, specific replica-count-per-shard guidance) beyond the general shard/replica terminology and the pointer to the external examples repo.

---

## 11. Migration

[Source: https://clickhouse.com/docs/operations/update] **Upgrading self-managed ClickHouse** is officially documented (`operations/update`, also aliased at `guides/oss/update`). Guidance: adopt **minor** version upgrades promptly and frequently — "minor releases do not have breaking changes but do have important bug fixes (and may have security fixes)." **Major** version upgrades need more care, especially if the jump spans more than a year of releases. For **rolling, zero-downtime upgrades**: upgrade replicas shard-by-shard, keeping some replicas live while others upgrade — for each node: stop the server, install the new version, restart, verify stability via Keeper logs, then proceed to the next. For **single-node/package-based** systems: standard `apt-get update && apt-get install clickhouse-server clickhouse-client && service clickhouse-server restart` (or pin an explicit version). **Downgrades** are documented as possible only to versions "less than one year old," and only if no new features introduced by the newer version have actually been used — once used, downgrade is not possible. Avoid running nodes in the same cluster whose versions differ by more than a year, as this risks cluster instability/data unavailability; use intermediate "stepping stone" versions for large version jumps, or accept downtime by upgrading all nodes simultaneously.

[Source: https://clickhouse.com/docs/operations/update] **ClickHouse Keeper** does not need to be upgraded in lockstep with ClickHouse server — "unless there is a security fix needed for ClickHouse Keeper or Apache ZooKeeper it is not necessary to upgrade Keeper when you upgrade ClickHouse server," and Keeper stability during the server upgrade should be prioritized, completing server upgrades before considering a Keeper upgrade.

[Source: https://clickhouse.com/docs/operations/update] **Experimental features** carry no upgrade-compatibility guarantee: "the compatibility of experimental features can be broken at any moment in any way." Recommended practice is to check changelogs and validate experimental-feature behavior on a separate test instance running the target version before upgrading production.

[Source: https://clickhouse.com/docs/migrations/postgresql/overview] **Migrating from PostgreSQL** is officially documented as a distinct guide track. Framing: Postgres is OLTP (ACID transactional guarantees — "an engineer can submit a block of updates ... and be sure that it will ... either succeed or fail"), ClickHouse is OLAP (fast aggregation/analytics over large datasets, real-time as data arrives); migrate when workload shifts toward analytical `GROUP BY`-style queries over large data. Two documented migration approaches: (1) **real-time CDC** (recommended for most cases) via ClickPipes (ClickHouse Cloud) or PeerDB (on-prem/self-managed), continuously capturing inserts/updates/deletes from Postgres; (2) **manual bulk load + periodic refresh**, via the `postgresql` table function/engine or CSV/SQL-script export-import, for simpler cases without a real-time-freshness requirement.

[Source: https://clickhouse.com/docs/migrations/postgresql] The PostgreSQL migration track also includes dedicated pages for **rewriting PostgreSQL-specific SQL queries** for ClickHouse's dialect and for the mechanics of **migrating a dataset**.

[Source: https://clickhouse.com/docs] MySQL-to-ClickHouse migration guidance also exists in the docs' migrations section per site navigation (referenced during site-structure search), analogous in structure to the PostgreSQL track (integration engines/table functions plus CDC-style tooling), but a dedicated MySQL migration-overview page was not independently fetched to full text in this research pass — flagged for completeness rather than fabricated in detail.

**Unresolved**: The MySQL migration-guide content above is inferred from site navigation/structure rather than a directly fetched page; do not treat its specifics as confirmed without a follow-up fetch of `clickhouse.com/docs/migrations/mysql` (or equivalent) directly.

---

## 12. Version information

[Source: https://clickhouse.com/docs/resources/changelogs/oss/2026] ClickHouse **26.8** is documented as an **LTS** release, dated **August 27, 2026** (the most recent LTS designation found in the fetched 2026 changelog page at the time of this research).

[Source: https://clickhouse.com/docs/faq/operations/production] ClickHouse uses two parallel release tracks: **Stable** releases, published **monthly**, with the three most recent Stable releases receiving bug-fix/diagnostic support ("the current Regular Stable Release is supported in conjunction with the two prior Regular Stable Releases for a minimum period of three months," per search-summarized official support-policy content — see version-sensitivity note below); and **LTS** releases, published **twice yearly** (historically March and August), each supported for a **minimum of one year**, with the current LTS supported alongside the immediately prior LTS for at least that year.

[Source: https://clickhouse.com/docs/faq/operations/production] Stable is the **documented default recommendation** for production; LTS is suggested specifically for organizations whose policies require infrequent upgrades.

[Version-sensitive / Unresolved] The precise wording of the "three most recent Stable releases, three-month support minimum" and "one-year LTS overlap" policy was obtained via a WebSearch summary of `clickhouse.com/legal/support-services-policy` and related official pages rather than a directly fetched, full-text official page in this research pass; the version-numbering scheme itself (Calendar Versioning, `Year.Month.Patch.Build`, e.g. `26.8.2.7`) is consistent with the fetched changelog page's version strings and treated as confirmed, but the exact support-duration figures should be re-verified directly against `clickhouse.com/legal/support-services-policy` before being relied on as precise SLA language.

[Inference, not confirmed in docs] As of this research (2026-09-09), the two most recent LTS lines appear to be **26.8** (released 2026-08-27) and **26.3** (released 2026-03-26, per a corroborating official presentation page title "ClickHouse: Release 26.3 LTS Call" surfaced in search, not independently fetched as a docs page) — stated as inference because the LTS-status of 26.3 specifically was not confirmed from a directly fetched `clickhouse.com/docs` page in this pass, only from search-result metadata.

---

## 13. Breaking changes

[Source: https://clickhouse.com/docs/resources/changelogs/oss/2026] The **26.8** changelog documents these backward-incompatible changes ([Version-sensitive: specific to 26.8, released 2026-08-27]):
- The `X-ClickHouse-Format` HTTP header now **explicitly and authoritatively** selects the response format, overriding both the `FORMAT` SQL clause and any URL-path-extension-based format inference (previously it served only as a default/fallback).
- Unquoted JSON numbers mapped to `DateTime`/`DateTime64` columns via `JSONEachRow` are now interpreted as **Unix timestamps**; previously, fractional unquoted numbers in that position were rejected outright.
- `max_insert_threads` default changed from **`1` to `auto`**, meaning `INSERT SELECT` is now parallelized by default — this can change resulting part creation and row ordering compared to prior versions' single-threaded-by-default behavior.
- The `PostgreSQL` and `MaterializedPostgreSQL` database engines now respect the `remote_url_allow_hosts` allow-list setting (previously they could reach hosts outside that restriction).
- The `library` dictionary source was **removed**.
- The Apache-Arrow-library-based reader/writer for Arrow-format data was **removed** in favor of ClickHouse's native Arrow implementation.
- `arrayIntersect` and `arraySymmetricDifference` **changed behavior** regarding how duplicate values within a single array argument are handled.

[Inference, not confirmed in docs] These are the changes captured from the 2026 changelog page as fetched; the full official changelog for prior major-version lines (24.x, 25.x, etc.) was not fetched in this research pass, so this section reflects only the most recent (26.8) documented breaking-change set, not a comprehensive multi-version breaking-changes history. A skill needing older-version breaking-change detail should fetch `clickhouse.com/docs/resources/changelogs/oss/<year>` for the relevant year(s) directly.

**Unresolved**: Whether any additional breaking changes shipped in the 26.1–26.7 monthly Stable releases between the 26.3 and 26.8 LTS points was not verified in this pass — only the 2026 changelog page's aggregate/most-recent content was fetched, and the fetch summary explicitly said "only one version was released in 2026" per the tool's read of that page, which is inconsistent with the version numbers (26.1 through 26.8) found elsewhere in search results; this discrepancy suggests the changelog page's full content was not completely captured by the fetch, and the breaking-changes list above should be treated as partial, not exhaustive, for 2026.

---

## 14. Limitations

[Source: https://clickhouse.com/docs/en/introduction/features_considered_disadvantages] Documented, first-party limitations: no full/general transaction support; inefficient high-rate/low-latency row-level update or delete (batch modification is supported, ongoing row-level OLTP-style mutation is not the design target); comparatively inefficient point queries (single-row lookup by key) due to the sparse primary index rather than a dense per-row index.

[Source: https://clickhouse.com/docs/knowledgebase/maximum_number_of_tables_and_databases] Documented scale ceilings (recommended, not hard-enforced, maximums, applicable to both self-managed and Cloud): **1,000 databases**, **5,000 tables**, **50,000 partitions**, **100,000 parts** per service; the server warns as these are approached. Databases are described as lightweight namespaces with no performance cost themselves; table/partition/part counts are what affect startup time and operational health.

[Source: https://clickhouse.com/docs/operations/settings/query-complexity] ClickHouse documents configurable **restrictions on query complexity** (e.g. limits on result-set size, read-row/byte counts, execution time) as a protective mechanism against resource-intensive queries — implying that, absent such configured limits, sufficiently complex or unbounded queries can otherwise consume excessive resources, which is itself a documented operational constraint operators must actively manage rather than one ClickHouse prevents by default.

[Source: https://clickhouse.com/docs/best-practices/choosing-a-partitioning-key] High-cardinality partitioning is a documented practical limitation/failure mode ("too many parts" errors) rather than a hard product limit — see Anti-patterns.

Not documented / could not verify: an official, single "known limitations" or "unsupported SQL features" reference page enumerating full SQL-standard compliance gaps was not located as one consolidated page in this research pass; individual feature pages (e.g. per-function, per-engine docs) note specific unsupported behaviors inline rather than in one master limitations list.

---

## 15. Debugging

[Source: https://clickhouse.com/docs/troubleshooting] The official troubleshooting page organizes guidance into four categories: **performance and errors**, **memory and resources**, **connections and authentication**, and **setup and configuration**. For slow queries: identify resource-intensive queries via dedicated guides, run diagnostic queries to isolate bottlenecks, consult the query-optimization guide, and specifically scrutinize JOINs; also check currently-running processes. For memory errors ("Memory limit exceeded" and similar): identify what is consuming memory via debugging tools and system tables/process lists, use allocation profiling, and configure memory limits at both server and session/query level, right-sizing the deployment to actual load. For connection issues: check HTTP-interface configuration, SSL certificate validation, user authentication/access-rights setup, and interface-specific quirks (MySQL, PostgreSQL, gRPC, SSH protocol emulation), plus network-security settings and data-format parsing errors.

[Source: https://clickhouse.com/docs/troubleshooting] Escalation path when self-service troubleshooting doesn't resolve an issue: consult AI assistance, query relevant **system tables**, review **server logs**, ask in the community Slack, or contact professional ClickHouse support.

[Source: https://clickhouse.com/docs/guides/developer/debugging-memory-issues] A dedicated **memory-debugging guide** exists specifically for identifying which queries/resources are driving memory consumption.

[Source: https://clickhouse.com/docs/knowledgebase/useful-queries-for-troubleshooting] An official knowledgebase page collects **useful diagnostic SQL queries**, including queries to surface stack traces for the currently slowest-running queries via system tables.

[Inference, not confirmed in docs] Based on the pattern of guidance across the troubleshooting and memory-debugging pages, `system.*` tables (e.g. `system.processes`, `system.query_log`, `system.errors`, replication-status tables) are the central, recurring debugging primitive across nearly every troubleshooting category — this is a reasonable synthesis of the repeated "check system tables" guidance rather than a single documented statement enumerating all relevant system tables in one place.

---

## 16. Integration

[Source: https://clickhouse.com/docs/integrations] Integrations are organized by category: **language clients**, **data ingestion**, **data visualization** (BI tools), **AI/ML**, **SQL clients**, **data integration** (workflow/infra connectors), **data management** (monitoring/optimization tooling), **security & governance**, and **ClickPipes** (ClickHouse's own native ingestion engine).

[Source: https://clickhouse.com/docs/integrations] Integrations are documented in three officially-defined support tiers: **Core** ("built or maintained by ClickHouse, ... supported by ClickHouse and live in the ClickHouse GitHub organization"), **Partner** (built/supported by third-party vendors), and **Community** ("built or maintained and supported by community members. No direct support is available besides the public GitHub repositories and community Slack channels").

[Source: https://clickhouse.com/docs/interfaces/mysql] MySQL wire-protocol compatibility is documented specifically as an integration path for BI tools lacking native ClickHouse drivers (Looker Studio, Tableau Online, QuickSight named explicitly as validated) — see APIs section for caveats.

[Source: https://clickhouse.com/docs/migrations/postgresql/overview] PostgreSQL integration/migration tooling is documented via ClickPipes (Cloud) and PeerDB (self-managed) for CDC-based sync, plus a `postgresql` table function/engine for direct querying/bulk load — see Migration section.

[Inference, not confirmed in docs] Given the deployment-modes page's mention of chDB integrating "with data science tools like Pandas and Arrow," and the interfaces page's mention of Apache Arrow Flight support, ClickHouse's documented integration surface leans heavily toward the modern data/analytics-engineering stack (Arrow-ecosystem tools, BI platforms, CDC pipelines) rather than toward general-purpose OLTP application-integration patterns — this is a synthesis across multiple fetched pages, not a single documented statement.

Not documented / could not verify: a single, exhaustive list of every Core-tier integration (e.g. the full roster of officially-maintained language clients) was not enumerated in the fetched integrations-overview page; that content lives in a catalog/directory UI rather than flat prose, so exact roster details would need a targeted per-integration fetch.

---

## 17. Production considerations

[Source: https://clickhouse.com/docs/faq/operations/production] The core documented production-readiness philosophy: build a **pre-production environment realistically mirroring production topology** (replication, sharding, multi-region if applicable) with **automated tests run against real ClickHouse instances**; validate new releases there, including changelog review, before any production rollout; prefer **gradual/canary deployment**. The docs explicitly reject "ask someone else which version is safe" as a substitute for this process.

[Source: https://clickhouse.com/docs/knowledgebase/maximum_number_of_tables_and_databases] Production capacity planning should respect the documented scale ceilings (1,000 databases / 5,000 tables / 50,000 partitions / 100,000 parts per service) — see Limitations.

[Source: https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy] Production ingestion design should follow the documented batching/async-insert guidance (10k–100k rows per batch, ~1 insert/sec cadence, async inserts with `wait_for_async_insert=1` for durability) to avoid "too many parts" degradation under real load — see Recommended Patterns.

[Source: https://clickhouse.com/docs/operations/update] Production upgrade discipline: adopt minor versions promptly, treat major-version jumps (especially >1 year) with a defined rolling-upgrade or planned-downtime procedure, keep Keeper stable and upgraded independently/conservatively, and validate experimental-feature usage on a separate instance before upgrading — see Migration section.

[Source: https://clickhouse.com/docs/operations/access-rights] Production security posture should use the SQL-driven RBAC workflow (users/roles/row-policies/settings-profiles/quotas) documented in Security, with quotas specifically relevant for protecting shared production services from runaway resource consumption by a given user/role.

[Source: https://clickhouse.com/docs/operations/settings/query-complexity] Production services should configure **query-complexity restrictions** (result size, rows/bytes read, execution time limits) to protect shared resources from expensive ad-hoc queries — see Limitations.

[Source: https://clickhouse.com/docs/get-started/about/deployment-modes] For teams wanting to avoid operating ClickHouse themselves, **ClickHouse Cloud** is documented as handling "updates, backups, scaling, ... security patches" automatically — a documented production-operations trade-off (managed-service convenience vs. self-managed control) rather than a claim that self-managed ClickHouse lacks these capabilities.

---

## Summary of version-sensitive facts to track

| Fact | Version / range | Note |
|---|---|---|
| `26.8` designated LTS | 26.8, released 2026-08-27 | [Source: https://clickhouse.com/docs/resources/changelogs/oss/2026] |
| `26.3` believed LTS (prior line) | 26.3, released 2026-03-26 | Inference from search metadata only, not a directly fetched docs page — see Version information section |
| `X-ClickHouse-Format` header now overrides `FORMAT`/path extension | Changed in 26.8 | Breaking change |
| `max_insert_threads` default `1` → `auto` | Changed in 26.8 | Breaking change; affects INSERT SELECT parallelism, part creation, row order |
| Unquoted JSON numbers in `JSONEachRow` now parsed as Unix timestamps for DateTime columns | Changed in 26.8 | Breaking change |
| `library` dictionary source removed | Removed in 26.8 | Breaking change |
| Arrow-library-based reader/writer removed (native Arrow impl only) | Removed in 26.8 | Breaking change |
| `tokenbf_v1`/`ngrambf_v1` skip-index types deprecated | Deprecated as of 26.2+ | Recommended pattern section |
| Calendar-versioning scheme `Year.Month.Patch.Build` | Ongoing scheme, current as of research date | Version information |
| Downgrade only supported to versions <1 year old, and only if no new features used | General policy, current as of research date | Migration section |

---

## Unresolved items (surfaced explicitly per project convention)

1. Exact LDAP/Kerberos external-authenticator support details and the NIST-800-63B password-policy/SSH-auth claims (Security section) — obtained via WebSearch summaries of official-looking pages, not a directly fetched full-text official page; needs re-verification.
2. Precise Stable/LTS support-duration policy language ("three prior Stable releases, three-month minimum"; "one-year LTS overlap") — obtained via WebSearch summary of `clickhouse.com/legal/support-services-policy`, not independently fetched in full.
3. Whether ClickHouse Keeper is definitively a from-scratch Raft-based C++ reimplementation of ZooKeeper (Architecture section) — the dedicated Keeper overview page 404'd during fetch; this is stated as inference pending direct confirmation.
4. Completeness of the 2026 breaking-changes list (Breaking changes section) — the changelog-page fetch summary asserted "only one version released in 2026," which conflicts with other evidence (26.1 through 26.8 release numbers found via search), suggesting the fetched page content was incomplete; breaking changes from 26.1–26.7 were not captured.
5. MySQL-to-ClickHouse migration guide specifics (Migration section) — inferred from site navigation, not fetched directly.
6. Whether a `network-security` guide page exists at a stable URL — a search-indexed URL for it returned HTTP 404 on direct fetch, suggesting either a stale search index entry or a since-moved page.
7. Query-execution-engine internals (vectorized execution / processor pipeline architecture) — referenced in search results but no official architecture page describing this was successfully fetched in this pass (Architecture section).

---

## Notes on doc-site structure churn

[Inference, not confirmed in docs] Multiple URL forms encountered during this research either 404'd or appeared to be older paths superseded by newer ones (`/docs/en/introduction/features_considered_disadvantages` vs. `/docs/about-us/distinctive-features`; `/docs/cloud/bestpractices/avoid-nullable-columns` vs. `/docs/best-practices/avoid-nullable-columns` / `/docs/optimize/avoid-nullable-columns`; `/docs/guides/sre/network-security` 404ing; `/docs/architecture/single-node-deployment` appearing under an `/en/` prefix in one search hit). This is consistent with an actively-reorganized documentation site rather than a single stable URL taxonomy — any ClickHouse doc URL cited elsewhere (including in this document) should be spot-checked for continued validity before being hard-coded into a downstream skill, and where two URL forms for the same content were found, this document cites whichever form was successfully fetched.
