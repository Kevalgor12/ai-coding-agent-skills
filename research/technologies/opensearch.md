# OpenSearch — Deep Reference Research

Research date: 2026-09-09. Primary source: the official OpenSearch documentation hub at `https://docs.opensearch.org/latest/` (rendered/linked from `https://opensearch.org/docs/`). [Source: https://docs.opensearch.org/latest/] Versioned docs are available at paths like `https://docs.opensearch.org/2.19/…` and `https://docs.opensearch.org/3.4/…`.

**Canonical host note:** [Source: https://docs.opensearch.org/latest/] The documentation now lives at `docs.opensearch.org` (a dedicated docs subdomain). Older links under `opensearch.org/docs/<version>/...` still resolve for some legacy version paths (e.g. 1.x, early 2.x), but current-version content is served from `docs.opensearch.org`. This is noted explicitly because the task brief's suggested location (`opensearch.org/docs`) has effectively moved/split to the `docs.opensearch.org` subdomain for current versions.

**Tooling caveat:** Several deep pages on `docs.opensearch.org` are served via a client-side redirect/Jekyll structure that this research session's fetch tooling sometimes rendered as bare navigation menus rather than full article bodies. Where this happened, the section below is built from the parts of the page that *did* return substantive text, from directly-fetched raw Markdown source in the `opensearch-project/documentation-website` GitHub repo, or is explicitly marked "could not verify full detail" rather than filled in with invented specifics.

---

## 1. Core Concepts

[Source: https://docs.opensearch.org/latest/getting-started/concepts/] A **cluster** is a collection of interconnected nodes that work together to store and search data; nodes within a cluster communicate to distribute data and coordinate operations.

[Source: https://docs.opensearch.org/latest/getting-started/concepts/] A **node** is an individual server instance that is part of a cluster, storing data segments and participating in indexing and search operations.

[Source: https://docs.opensearch.org/latest/getting-started/concepts/] An **index** is a logical container for documents (comparable to a database table); it includes configuration settings and **mappings** that define field types, plus settings controlling behavior like the number of shards and replicas.

[Source: https://docs.opensearch.org/latest/getting-started/concepts/] A **shard** is a subset of an index's data distributed across nodes; sharding allows an index to scale horizontally by dividing documents into smaller segments processed in parallel across nodes.

[Source: https://docs.opensearch.org/latest/getting-started/concepts/] A **replica** is a copy of a primary shard, created for redundancy and improved search performance — it maintains availability if a node fails and lets search requests be distributed across multiple copies.

[Source: https://docs.opensearch.org/latest/getting-started/concepts/] A **document** is an individual JSON record stored within an index — the fundamental unit of data that can be indexed, searched, and retrieved.

[Source: https://docs.opensearch.org/latest/getting-started/concepts/] A **mapping** defines the structure and type of fields within an index, specifying field types (text, keyword, numeric, etc.) and the analyzers/processing rules applied to them.

[Source: https://docs.opensearch.org/latest/about/] OpenSearch is described as a distributed, community-driven, Apache 2.0-licensed, 100% open-source search and analytics suite used for use cases such as real-time application monitoring, log analytics, and website search.

[Source: https://docs.opensearch.org/latest/about/] The project ships multiple integrated components under one umbrella: **OpenSearch** (the search/analytics engine core), **OpenSearch Dashboards** (visualization UI), **Data Prepper** (server-side data collector for filtering/enriching/transforming/normalizing/aggregating data for downstream analysis), and language **Clients** (APIs for popular programming languages).

[Inference, not confirmed in docs] OpenSearch is a fork of Elasticsearch/Kibana 7.10.2, created in 2021 after Elastic changed Elasticsearch's license; this lineage is widely known but was not re-confirmed against an official docs.opensearch.org page in this research pass — flagged as inference rather than a direct citation.

---

## 2. Architecture

[Source: https://docs.opensearch.org/latest/tuning-your-cluster/] OpenSearch clusters are composed of nodes with distinct roles: **cluster manager nodes** (handle cluster coordination and state management — the successor naming to the historical "master node" term), **data nodes** (store and search index data), **ingest nodes** (process documents through ingest pipelines before indexing), and **coordinating nodes** (route requests without storing data or managing cluster state).

[Source: https://docs.opensearch.org/latest/getting-started/concepts/] Data is horizontally partitioned into shards distributed across data nodes, with each shard itself a self-contained Lucene index; replica shards provide redundancy and let search load spread across copies.

[Source: https://docs.opensearch.org/latest/api-reference/] OpenSearch exposes discovery/cluster-formation configuration for how nodes find each other and elect a cluster manager, plus voting and bootstrapping mechanisms, under "Creating and tuning your cluster" documentation.

[Source: https://github.com/opensearch-project/OpenSearch/issues/3351] **Version-sensitive (3.0):** OpenSearch 3.0 requires **JDK 21** as the minimum supported Java runtime and upgraded the search core to **Apache Lucene 10**.

[Source: https://github.com/opensearch-project/OpenSearch/issues/3351] **Version-sensitive (3.0):** The Java Security Manager (JSM) was permanently disabled system-wide in OpenSearch 3.0, and the transport layer moved to Apache HttpClient 5.x.

[Source: https://docs.opensearch.org/latest/about/] Machine learning is integrated into the core architecture (via `ml-commons`) enabling semantic search, and the platform supports multiple pluggable authentication methods through its security layer.

[Source: https://docs.opensearch.org/latest/tools/] Plugin-based extensibility is a core architectural trait: functionality such as k-NN (vector search), neural search, ML Commons, SQL/PPL, index state management (ISM), and the security plugin are implemented as OpenSearch plugins layered on the core engine.

Not documented / could not verify: a single canonical "architecture diagram" page giving exact internal request-routing/consensus-protocol details (e.g. specifics of the cluster-manager election algorithm) was not retrieved in full during this pass; the discovery/cluster-formation documentation referenced above exists but its full body content did not render through the fetch tooling used.

---

## 3. APIs

[Source: https://docs.opensearch.org/latest/api-reference/] OpenSearch exposes a RESTful API surface over HTTP using standard verbs (GET, POST, PUT, DELETE). Major documented API groups include:
- **Index Management APIs** — create/manage/configure indexes, including index templates and aliases.
- **Document APIs** — index, retrieve, update, and delete individual documents.
- **Search APIs** — query execution via Query DSL and search parameters.
- **Cluster APIs** — cluster state, node operations, cluster-wide configuration.
- **Ingest Pipeline APIs** — create/manage document-transformation pipelines.
- **Security APIs** — user, role, and permission management.
- **Index State Management (ISM) APIs** — policy management for automated index lifecycle actions.
- **Snapshot and Restore APIs** — backup/recovery operations.
- **Replication APIs** — cross-cluster replication configuration.
- **Machine Learning APIs** — model registration, deployment, and inference.
- **Analysis APIs** — text analysis/tokenization operations.
- **cat APIs** — human-readable, tabular cluster/index diagnostics (referenced throughout the docs; e.g. used for troubleshooting).

[Source: https://docs.opensearch.org/latest/getting-started/intro/] The docs' "Getting started" material demonstrates communicating with a cluster via `curl`-style REST calls and via the Dev Tools console in OpenSearch Dashboards, covering data ingestion, search, and the Query DSL as the primary query language.

[Source: https://docs.opensearch.org/latest/about/] Language **Clients** provide idiomatic API access from multiple programming languages as an alternative to raw REST calls.

Not documented / could not verify: exact current sub-path listings for every API group (this pass could not fully enumerate every endpoint under `/api-reference/` due to page-rendering limits in the fetch tooling); consult `https://docs.opensearch.org/latest/api-reference/` directly for the authoritative, current endpoint list.

---

## 4. Configuration

[Source: https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/] Configuration is organized by the docs into distinct areas: general "Configuration and system settings," Network settings, Discovery and gateway settings, Security settings, Cluster settings, Index settings, Cache settings, Search settings, Thread pool settings, Circuit breaker settings, Admission control settings, Monitoring settings, and Availability/recovery settings.

[Source: https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/] Core node identity and topology are configured via `opensearch.yml`, including settings such as `cluster.name`, `node.name`, and `network.host` (exact default values not confirmed in this pass — see caveat below).

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md] Security-plugin configuration is split between `opensearch.yml` (for TLS certificate paths — `pemcert`, `pemkey`, `pemtrustedcas` for both the transport and HTTP layers) and `config.yml` inside the `opensearch-security` config directory (for authentication backend setup, internal or external).

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md] The security plugin can be fully disabled by setting `plugins.security.disabled: true` in `opensearch.yml`; removing that line re-enables protection.

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md] Custom certificates (as opposed to the bundled demo certificates) must be placed under `<OPENSEARCH_HOME>/config/` with private keys set to file permission `600` and public certificates to `644`; configuration changes made via `config.yml` are applied by running the `securityadmin` script bundled in the plugin's tools directory.

[Source: https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/ (via search-indexed summary)] `vm.max_map_count` must be at least `262144` on the host for OpenSearch to start reliably; on Linux this is set persistently by adding `vm.max_map_count=262144` to `/etc/sysctl.conf` and reloading with `sysctl -p`. On Windows with Docker Desktop/WSL, the equivalent is `wsl -d docker-desktop sysctl -w vm.max_map_count=262144`.

[Inference, not confirmed in docs — but strongly indicated by search-indexed docs snippets referencing `jvm.options`] JVM heap sizing follows the standard Lucene-ecosystem guidance carried in the install docs: set `-Xms` and `-Xmx` to the **same** value, at roughly **50% of available system RAM**, subject to a practical ceiling of about **32 GB** (beyond which JVM compressed-oops addressing stops applying and effective memory efficiency drops); configured via the `config/jvm.options` file, not `opensearch.yml`. This is marked as inference/best-effort because the fetch tooling could not retrieve the full body text of the specific install-settings page to quote it verbatim, though indexed docs snippets point to this exact guidance living on `docs.opensearch.org`.

[Source: https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/] Settings are split between static settings (require a node restart, set in `opensearch.yml`) and dynamic settings (updatable at runtime via the Cluster Settings API) — this static/dynamic split is referenced by the docs' navigation structure; exact per-setting classification should be checked per setting on the relevant settings-category page.

Not documented / could not verify: complete default values for `path.data`, `path.logs`, and `network.host` were not directly confirmed with quoted text in this pass due to rendering limits; consult `https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/configuration-system/` and `network-settings/` directly.

---

## 5. Recommended Patterns

[Source: https://opensearch.org/blog/optimize-opensearch-index-shard-size/] The official OpenSearch project blog recommends starting with shard sizes between **10–50 GB per shard** as a baseline, then tuning by workload: **10–30 GB per shard** for search-latency-sensitive workloads (e.g. application search), and **30–50 GB per shard** for write-heavy/analytics workloads (e.g. log processing).

[Source: https://opensearch.org/blog/optimize-opensearch-index-shard-size/] The blog explicitly frames both extremes as anti-patterns to avoid: too many small shards wastes JVM heap on per-shard metadata overhead, while too few large shards limits request parallelization across nodes and undermines the distributed-computing benefit of sharding. It states that only performance testing with different shard counts can determine the ideal count for a specific index/workload.

[Source: https://docs.opensearch.org/latest/mappings/mapping-explosion/] To avoid "mapping explosion" (an index accumulating an excessive number of fields, degrading performance/memory/cluster stability — commonly triggered by dynamic mapping over highly variable document structures such as logs with varying source structure or user-generated custom fields), the docs recommend defining **explicit mappings** rather than relying on dynamic mapping wherever possible, and offer settings to cap mapping growth.

[Source: https://docs.opensearch.org/latest/mappings/supported-field-types/flat-object/] The **flat object** field type is a documented pattern for high-cardinality/variable nested JSON: it treats an entire JSON object as a single field (subfields reachable via dot-path notation) rather than indexing each subfield individually, avoiding mapping explosion for that use case.

[Source: https://docs.opensearch.org/latest/mappings/] Setting an index's dynamic mapping mode to `"dynamic": "strict"` causes OpenSearch to reject documents containing unmapped fields, which the docs present as a way to positively enforce a fixed schema and prevent uncontrolled mapping growth (trade-off: all object structures must be explicitly defined upfront).

[Source: https://docs.opensearch.org/latest/tuning-your-cluster/] The docs recommend separating index (write) and search (read) workloads where cluster resources allow, to avoid resource contention between ingestion and query traffic — covered under "Separate index and search workloads" in the cluster-tuning documentation.

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md] For production, the docs explicitly instruct replacing the bundled demo TLS certificates with your own trusted certificates ("For a production environment, it's critical to replace these with your own trusted certificates") — using the demo certs in production is treated as a pattern to avoid, not a recommended pattern.

---

## 6. Anti-Patterns

[Source: https://opensearch.org/blog/optimize-opensearch-index-shard-size/] Oversized shards (well beyond the ~50 GB guidance) are called out as risking OpenSearch's ability to relocate or recover shards, which can lead to operational trouble; undersized/too-numerous shards waste heap on shard bookkeeping. Both extremes are documented anti-patterns.

[Source: https://docs.opensearch.org/latest/mappings/mapping-explosion/] Relying on unconstrained dynamic mapping against highly variable document sources (arbitrary user-defined fields, deeply nested/varying log structures) is a documented anti-pattern that leads to mapping explosion, memory pressure, and cluster instability.

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md] Running a production cluster with the bundled demo certificates, or with `plugins.security.disabled: true`, is implicitly flagged as an anti-pattern by the docs' explicit "for a production environment, it's critical to replace these" language and by scoping the disable-security setting as something to be reverted (re-enabled) rather than left in place.

[Source: https://docs.opensearch.org/latest/tuning-your-cluster/] Not separating ingest-heavy and search-heavy workloads on shared resources is presented as something to correct via the "Separate index and search workloads" guidance, implying co-mingled heavy indexing and heavy search on the same nodes without tuning is an anti-pattern for cluster stability.

Not documented / could not verify: a single, dedicated "Anti-patterns" page enumerating a canonical list (analogous to some vendor docs) was not found under docs.opensearch.org in this research pass; the anti-patterns above are drawn from prescriptive/prohibitive language embedded in topic-specific pages (shard sizing blog post, mapping-explosion page, security configuration page) rather than one consolidated anti-patterns reference.

---

## 7. Security

[Source: https://docs.opensearch.org/latest/security/] OpenSearch ships a **Security plugin** supporting multiple authentication backends: HTTP basic authentication, JSON Web Token (JWT), OpenID Connect, SAML, Active Directory/LDAP, proxy-based authentication, client certificate authentication, and Kerberos.

[Source: https://docs.opensearch.org/latest/security/] TLS is configured for both transport (node-to-node) and HTTP (client-to-node) layers, with support for self-signed certificates and FIPS-compliance-oriented settings.

[Source: https://docs.opensearch.org/latest/security/] Access control is role-based (RBAC) with fine-grained capabilities: **document-level security**, **field-level security**, **field masking**, user impersonation controls, API key management, and anonymous authentication options.

[Source: https://docs.opensearch.org/latest/security/] **Audit logging** is supported, with configurable field references and multiple storage backend options for compliance tracking.

[Source: https://docs.opensearch.org/latest/security/] Security administration includes YAML-based backend configuration, a `securityadmin` CLI tool, configuration versioning, API rate limiting, multiple simultaneous authentication/sign-in methods, per-plugin enable/disable controls, and keystore management for sensitive values.

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md] Custom (non-demo) certificates must be stored under `<OPENSEARCH_HOME>/config/` with private keys at file mode `600` and public certs at `644`; certificate paths are then referenced from `opensearch.yml`.

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md] The security plugin can be disabled entirely via `plugins.security.disabled: true` in `opensearch.yml` — the docs frame this as an option, not a recommendation, and pair it with the demo-certificate production warning.

[Source: https://github.com/opensearch-project/OpenSearch/issues/3351] **Version-sensitive (3.0):** thread-context permission requirements for header-manipulation methods changed as part of the 3.0 breaking changes (tightening how internal request headers can be mutated), and non-inclusive terminology was removed from Java/REST APIs and cluster settings.

Not documented / could not verify: specific default password-complexity policy values for the internal user database were referenced by the docs' navigation ("strong password policies" recommended) but the exact enforced regex/complexity rules were not retrieved with quoted text in this pass.

---

## 8. Performance

[Source: https://docs.opensearch.org/latest/tuning-your-cluster/] The docs organize performance tuning around: thread pool settings (concurrency), circuit breaker settings and admission control settings (both aimed at preventing out-of-memory conditions), a dedicated "Tuning for indexing speed" guide, and "Separate index and search workloads" for resource isolation.

[Source: https://opensearch.org/blog/optimize-opensearch-index-shard-size/] Shard-count/size tuning is treated as a first-class performance lever: 10–30 GB shards for low-latency search workloads, 30–50 GB shards for write-heavy/log-analytics workloads, with the caution that too many shards depletes heap on metadata and too few limits parallelism across data nodes.

[Inference, not confirmed in docs — see Configuration section caveat] JVM heap should be set to ~50% of available system RAM up to a practical ~32 GB ceiling to preserve compressed-oops efficiency; `-Xms`/`-Xmx` should be set equal. Flagged as inference because this session's tooling could not pull verbatim quoted text from the specific `docs.opensearch.org` settings page, though indexed snippets from that domain corroborate the "half of available system memory" starting point.

[Source: https://docs.opensearch.org/latest/tools/benchmark/] **OpenSearch Benchmark** is the official performance-testing tool: it runs a defined "workload" (test scenario) against a cluster and produces metrics, supporting use cases like ongoing cluster performance monitoring, informing upgrade decisions, and assessing the impact of mapping/query changes. It supports multiple pre-built workloads or custom workloads, corpus expansion/synthetic data generation, telemetry device integration, target-throughput configuration, query randomization, and distributed load generation, via commands including `run`, `compare`, `aggregate`, `download`, and `generate-data`.

[Source: https://docs.opensearch.org/latest/tuning-your-cluster/] Cache settings and search-specific settings are documented as separate tunable categories for optimizing query performance.

Not documented / could not verify: specific numeric bulk-indexing-size recommendations (e.g. an exact recommended bulk request byte size) and exact `refresh_interval` guidance were referenced by the docs' navigation structure ("Tuning your cluster for indexing speed") but this pass could not retrieve the page's full quoted body text to state precise numbers — consult `https://docs.opensearch.org/latest/tuning-your-cluster/performance/` directly.

---

## 9. Testing

[Source: https://docs.opensearch.org/latest/tools/benchmark/] OpenSearch Benchmark is the officially documented tool for load/performance testing clusters (see Performance section above) — this is the closest official analogue to a "testing" framework at the cluster-operations level.

[Source: https://github.com/opensearch-project/opensearch-testcontainers] The OpenSearch project maintains an official **`opensearch-testcontainers`** GitHub repository (`opensearch-project/opensearch-testcontainers` org) providing a Testcontainers module for spinning up real OpenSearch Docker containers in integration tests, for use with JUnit 4/JUnit 5 in JVM-based test suites.

[Source: https://docs.opensearch.org/latest/troubleshoot/] The Dev Tools console (part of OpenSearch Dashboards) and a **Query Profiler** are documented tools for interactively exercising and validating queries, which functions as a manual/exploratory testing aid distinct from automated test frameworks.

Not documented / could not verify: OpenSearch's own core-engine test suite (Gradle-based integration/REST-layer tests in the `opensearch-project/OpenSearch` repo) is real and referenced across the project's contributing docs, but a dedicated "how end users should test applications built on OpenSearch" guide beyond OpenSearch Benchmark and the testcontainers module was not located as a single consolidated docs.opensearch.org page in this pass.

---

## 10. Deployment

[Source: https://docs.opensearch.org/latest/install-and-configure/install-opensearch/index/] Documented installation/deployment methods include: **Docker**, **Helm** (Kubernetes package manager), **tarball**, **RPM**, **Debian (.deb)**, **Windows** installer, the **OpenSearch Kubernetes Operator**, and an **Ansible playbook**.

[Source: https://docs.opensearch.org/latest/install-and-configure/install-opensearch/index/] A "Compatible operating systems" reference page is maintained separately from the install-method pages, indicating OS-level compatibility is tracked per release.

[Source: https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/ (search-indexed summary)] For Docker specifically, the docs cover host `vm.max_map_count` configuration (must be ≥262144) and Docker Desktop memory allocation guidance (a minimum of 4 GB host memory utilization is called out for Docker Desktop users), plus example docker-compose based single/multi-node setups.

[Source: https://docs.opensearch.org/latest/tools/] **OpenSearch Dashboards** and **Data Prepper** are deployed as separate, complementary services/components alongside the OpenSearch core cluster rather than being embedded in it.

Not documented / could not verify: this pass could not retrieve fully quoted body text for exact minimum RAM/CPU/disk sizing recommendations per node role (data vs. cluster-manager vs. coordinating) — consult `https://docs.opensearch.org/latest/install-and-configure/` and the OS-specific install pages directly for current numbers.

---

## 11. Migration

[Source: https://docs.opensearch.org/latest/migrate-or-upgrade/] The docs document three primary migrate/upgrade paths: **rolling upgrades** (incremental, node-by-node, no-downtime upgrades within a cluster, with an accompanying hands-on lab), **snapshot and restore** (used both as a backup mechanism and as a data-migration mechanism between clusters), and a dedicated **Migration Assistant** tool.

[Source: https://docs.opensearch.org/latest/migrate-or-upgrade/] The **Migration Assistant** is explicitly documented as covering migration **from Elasticsearch** to OpenSearch, i.e. OpenSearch's official docs cover migrating from the comparable/ancestor project as well as upgrading between OpenSearch's own major versions.

[Source: https://docs.opensearch.org/latest/migrate-or-upgrade/] The docs direct users to consult the dedicated **Breaking changes** reference (under "About" → "Version history") before upgrading, since breaking changes are catalogued per version rather than repeated inside the upgrade guide itself.

[Source: https://github.com/opensearch-project/OpenSearch/issues/3351] **Version-sensitive:** upgrading to **3.0** specifically requires JDK 21 at minimum (a hard prerequisite change from earlier 1.x/2.x JVM requirements) and involves Lucene 10 — both should be checked against an existing deployment's Java runtime before attempting the 3.0 upgrade.

---

## 12. Version Information

[Source: https://opensearch.org/releases/] Current stable version as of this research date (2026-09-09): **OpenSearch 3.8.0** (release-candidate window closed; the release-schedule page shows 3.8.0's RC window as July 23–August 4, 2026).

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_about/version-history.md] The official version-history table records **3.8.0** as released **04 August 2026** (a one-day discrepancy vs. the releases-page RC-window end date of Aug 4/5 is noted here for transparency; both sources agree 3.8.0 is current).

[Source: https://opensearch.org/releases/] Upcoming releases per the schedule at research time: **3.9.0** (RC window September 15–29, 2026) and **3.10.0** (RC window November 3–17, 2026).

[Source: https://opensearch.org/releases/] Release cadence: OpenSearch targets **a new minor version approximately every eight weeks**, using a release-window model where each window spans roughly two weeks during which release candidates are generated daily until exit criteria are met.

[Source: https://opensearch.org/releases/] Maintenance/support policy: **"Versions will remain under maintenance until the next major version enters maintenance, or 1 year passes, whichever is longer."** The project commits to no unpatched vulnerabilities of medium-or-higher severity that have been publicly known for more than 60 days in actively maintained versions.

[Source: https://opensearch.org/releases/] Status snapshot at research time: **1.x is end-of-life** (maintenance ended May 6, 2025); **2.x is in maintenance** until 4.0 reaches GA (patch releases for the 2.19.x line were scheduled to continue through December 2026); **3.x is the actively developed major line**.

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_about/version-history.md] Latest 2.x maintenance patch on record: **2.19.6**, released **02 July 2026**. Latest 1.x patch on record: **1.3.20**, released 11 December 2024 (1.x is EOL per the releases-page statement above).

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_about/version-history.md] The **3.x** line began with **3.0.0** on **06 May 2025**, followed by 3.1.0 (24 Jun 2025), 3.2.0 (19 Aug 2025), 3.3.0 (14 Oct 2025), 3.4.0 (16 Dec 2025), 3.5.0 (10 Feb 2026), 3.6.0 (07 Apr 2026), 3.7.0 (09 Jun 2026), 3.8.0 (04 Aug 2026) — confirming the roughly-eight-week minor cadence documented above.

[Source: https://github.com/opensearch-project/OpenSearch/issues/3351] **Version-sensitive:** OpenSearch 3.x requires **JDK 21** minimum; this is a hard break from the 1.x/2.x Java baseline and must be checked before upgrading.

---

## 13. Breaking Changes

[Source: https://github.com/opensearch-project/OpenSearch/issues/3351] **OpenSearch 3.0 breaking changes** (tracked in the project's own "[META] Breaking changes in 3.0" GitHub issue):
- Minimum supported Java runtime raised to **JDK 21**.
- Search core upgraded to **Apache Lucene 10**.
- Non-inclusive terminology removed from Java APIs, REST APIs, and cluster settings (renamed identifiers).
- Java Security Manager (JSM) **permanently disabled** system-wide.
- Transport layer migrated to **Apache HttpClient 5.x**.
- Thread-context permission requirements changed for header-manipulation methods.
- Document ID size enforcement (**512-byte limit**) now applied consistently across bulk API operations.
- Node-role configuration via environment variables now correctly recognizes empty array strings.
- XContent/Jackson content limits realigned to the Jackson **2.16.0** defaults.
- New index-level query nesting-depth constraints introduced.
- Indexing-buffer metric reporting formatting corrected.
- Removed: obsolete thread-pool configurations, outdated Java-API terminology, legacy `JodaCompatibleZonedDateTime` methods, the COMPAT locale provider, and the **transport-nio plugin**.

[Source: https://docs.opensearch.org/latest/migrate-or-upgrade/] The docs maintain a dedicated, version-indexed **"Breaking changes"** reference page (under About → Version history) intended to be consulted before every major/minor upgrade — this is the authoritative place to check for a specific version pair, since this research pass could not retrieve the full rendered body of that consolidated page (it returned only navigation structure through the fetch tooling used).

Not documented / could not verify: a fully quoted, version-by-version breaking-changes list for every 2.x minor release (e.g. 2.0, 2.12) was not retrieved in this pass beyond the 3.0 GitHub-issue tracker above; consult `https://docs.opensearch.org/latest/breaking-changes/` directly for the complete, current catalogue.

---

## 14. Limitations

[Source: https://docs.opensearch.org/latest/sql-and-ppl/limitation/] The SQL and PPL plugin documents explicit, dedicated limitations (per indexed docs summary — full page body not retrieved verbatim in this pass, so treat the following bullet points, sourced from search-engine-indexed docs text, as *summarized from* rather than *verbatim-quoted from* the official page): `SELECT` without a `FROM` clause (e.g. bare `SELECT 1`) is not supported; `WHERE` clauses do not support arbitrary expressions; aggregation cannot be applied over an expression (only over a raw field — e.g. `avg(log(age))` is not supported); `JOIN` results cannot have aggregations applied to them; pagination is supported only for basic queries (queries combining aggregation and join do not support pagination); qualifying an index name with the cluster name (e.g. `my_cluster.my_index`) is not supported.

[Inference, not confirmed in docs — flagged because the underlying claim mixes OpenSearch project docs with AWS's managed "Amazon OpenSearch Service" docs, which is a distinct, vendor-managed product, not the open-source OpenSearch project itself] Some vector-search-collection limitations found during search (no Lucene ANN engine support, HNSW/Faiss only, no IVF/IVFQ, no warmup/stats/model-training API operations, no inline/stored scripts) were sourced from **Amazon OpenSearch Service** documentation (`docs.aws.amazon.com`), which is AWS's managed offering and is **not** an official OpenSearch-project documentation source per this task's sourcing rules — excluded as a primary citation and flagged here only to note that AWS's managed serverless vector-search tier has its own, separately-documented limitation set distinct from self-managed open-source OpenSearch's k-NN plugin.

Not documented / could not verify: a consolidated, single "Known limitations" page for core OpenSearch (outside of the SQL/PPL plugin) was not located in this pass; limitations for individual features (k-NN, ISM, cross-cluster replication, etc.) appear to be documented per-feature rather than in one master limitations page.

---

## 15. Debugging

[Source: https://docs.opensearch.org/latest/troubleshoot/] The docs maintain a dedicated "Troubleshooting OpenSearch" section covering: logging configuration for diagnostic purposes, the **Dev Tools console** (for executing queries and inspecting behavior interactively), the **Query Profiler** (to analyze query execution and find performance bottlenecks), and a **Grok Debugger** (for debugging ingest-pipeline grok patterns).

[Source: https://docs.opensearch.org/latest/troubleshoot/] Additional diagnostic surfaces referenced from the troubleshooting section include: index-management diagnostics for index-related problems, cluster-configuration inspection via discovery/cluster-formation docs, and security **audit logs** for tracking authentication/authorization issues.

[Source: https://docs.opensearch.org/latest/troubleshoot/] Documented common-issue areas include: cluster formation/node discovery problems, index state management (ISM) errors (with dedicated error-prevention/resolution guidance), circuit breaker and admission control issues, search performance/backpressure scenarios, and ingest-pipeline failures.

Not documented / could not verify: this pass did not retrieve the full body text (with exact log-level names, exact `_cat`/`_nodes/hot_threads`-style API examples, etc.) for the troubleshooting pages beyond the section-list summary above; consult `https://docs.opensearch.org/latest/troubleshoot/` directly for exact commands.

---

## 16. Integration

[Source: https://docs.opensearch.org/latest/about/] **Data Prepper** is the officially documented server-side data-collection/ingestion component for filtering, enriching, transforming, normalizing, and aggregating data before it reaches OpenSearch.

[Source: https://docs.opensearch.org/latest/tools/] Documented ingest-pipeline **processor types** include grok, text-embedding, and text-chunking processors (among others), used to transform documents as part of an ingest pipeline before indexing.

[Source: https://docs.opensearch.org/latest/tools/] **Logstash** integration is referenced in the tools documentation as a supported data-pipeline path into OpenSearch.

[Source: https://docs.opensearch.org/latest/tools/] The **k-NN plugin** enables approximate nearest-neighbor vector search; **Neural Search** builds semantic/hybrid search capability using embeddings on top of it; **ML Commons** supports integrating and serving machine learning models within the cluster.

[Source: https://docs.opensearch.org/latest/tools/] **OpenSearch Dashboards** is the documented visualization/management UI, including multi-tenant **Workspaces** for organizing dashboards and saved objects.

[Source: https://docs.opensearch.org/latest/about/] Language **Clients** (per-language API libraries) are the documented mechanism for application-code integration, as an alternative to raw REST calls.

[Source: https://docs.opensearch.org/latest/migrate-or-upgrade/] The **Migration Assistant** tool is documented as the integration/migration path specifically for organizations moving from **Elasticsearch** to OpenSearch.

[Source: https://github.com/opensearch-project/opensearch-testcontainers] For test/CI integration, the project maintains an official Testcontainers module (`opensearch-project/opensearch-testcontainers`) to run real OpenSearch instances inside automated test suites.

---

## 17. Production Considerations

[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md] Replace bundled demo TLS certificates with trusted, properly-permissioned (`600`/`644`) certificates before going to production; the docs call this "critical."

[Source: https://opensearch.org/blog/optimize-opensearch-index-shard-size/] Size and count shards deliberately (10–50 GB/shard depending on workload) — oversized shards risk relocation/recovery failures, undersized/over-numerous shards waste heap and limit throughput; the official guidance is to performance-test different shard counts for a given workload rather than assume a fixed number.

[Source: https://docs.opensearch.org/latest/tuning-your-cluster/] Configure circuit breakers and admission control deliberately to prevent out-of-memory failures under load, and consider separating indexing and search workloads onto different node pools/resources when both are heavy.

[Source: https://opensearch.org/releases/] Track the maintenance window for your running major/minor version against the documented policy ("maintained until the next major version enters maintenance, or 1 year, whichever is longer") and the project's 60-day medium+-severity vulnerability-patch commitment, to plan upgrade timing rather than running an EOL version (e.g. 1.x, which reached EOL May 6, 2025 per the docs).

[Source: https://docs.opensearch.org/latest/migrate-or-upgrade/] Use **rolling upgrades** for no-downtime version upgrades within supported paths, and always check the version-specific **Breaking changes** page before upgrading a production cluster.

[Source: https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/ (search-indexed summary)] Set host `vm.max_map_count` to at least 262144 before running OpenSearch (containerized or not) — the process will fail to start otherwise.

[Source: https://docs.opensearch.org/latest/tools/benchmark/] Use **OpenSearch Benchmark** against a staging/representative cluster before rolling out mapping or query changes in production, and to validate cluster performance ahead of and after upgrades.

[Source: https://docs.opensearch.org/latest/mappings/mapping-explosion/] Guard production indices against mapping explosion (explicit mappings, `"dynamic": "strict"`, or the flat-object field type for highly variable nested JSON) to avoid memory pressure and cluster instability from uncontrolled field growth — especially relevant for log/observability and user-generated-content indices.

---

## Summary of Version-Sensitive Facts Worth Tracking

- **3.0**: minimum JDK raised to **21**; Lucene upgraded to **10**; Java Security Manager permanently disabled; transport layer moved to Apache HttpClient 5.x; `transport-nio` plugin removed; 512-byte document-ID limit now enforced consistently in bulk API. [Source: https://github.com/opensearch-project/OpenSearch/issues/3351]
- **Current stable (as of 2026-09-09)**: **3.8.0** (04 Aug 2026). [Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_about/version-history.md]
- **1.x**: end-of-life, maintenance ended **May 6, 2025**. [Source: https://opensearch.org/releases/]
- **2.x**: in maintenance mode until 4.0 reaches GA; latest patch **2.19.6** (02 Jul 2026). [Source: https://opensearch.org/releases/, https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_about/version-history.md]
- Release cadence: new minor roughly **every 8 weeks**. [Source: https://opensearch.org/releases/]

## Unresolved Items

- Exact default values for `network.host`, `path.data`, `path.logs` in `opensearch.yml` — page navigation confirmed the settings exist but full quoted body text was not retrieved.
- Exact numeric bulk-indexing-size and `refresh_interval` tuning recommendations on `tuning-your-cluster/performance/` — page returned only navigation structure to the fetch tooling used in this session.
- Exact minimum RAM/CPU/disk sizing per node role (data / cluster-manager / coordinating) — referenced in docs structure but specific numbers not retrieved verbatim.
- Full quoted text of the consolidated `breaking-changes/` page across all 2.x minor versions (only the 3.0 GitHub-issue-tracked list was fully retrieved).
- Whether the JVM heap "50% of RAM, ~32 GB cap" guidance is stated in those exact terms on a current `docs.opensearch.org` page, versus only in search-engine-indexed snippets of that domain — flagged as inference pending direct-page confirmation.
