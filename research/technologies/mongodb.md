# MongoDB — Deep Reference Research

Research date: 2026-09-09. Primary source: the official MongoDB documentation hub at `https://www.mongodb.com/docs/` (the "MongoDB Manual" lives at `https://www.mongodb.com/docs/manual/`). [Source: https://www.mongodb.com/docs/] This is still the canonical docs host as of this research date — no migration away from `mongodb.com/docs` was found. [Source: https://www.mongodb.com/docs/] The docs site also publishes an AI-oriented index at `https://www.mongodb.com/docs/llms.txt` and exposes a Markdown variant of any docs page by appending `.md` to its URL. [Source: https://www.mongodb.com/docs/]

**Version scope note:** Unless otherwise tagged, claims below reflect the current MongoDB Manual (untagged `/docs/manual/…` URLs, which track the latest stable release). Version-specific pages are cited as `/docs/v7.0/…`, `/docs/v8.0/…`, etc. where fetched directly.

---

## 1. Core Concepts

[Source: https://www.mongodb.com/docs/manual/core/document/] A **document** is the basic unit of data in MongoDB, stored as BSON (Binary JSON) — field-and-value pairs, e.g. `{ field1: value1, field2: value2, ... }`.

[Source: https://www.mongodb.com/docs/manual/core/document/] Every document requires a unique `_id` field (auto-generated as an `ObjectId` if not supplied); it is always the first field in the document and cannot be an array or a regex type.

[Source: https://www.mongodb.com/docs/manual/core/document/] Field names cannot contain the null character and must be unique within a document; **as of MongoDB 5.0**, field names may contain dots (`.`) and dollar signs (`$`) with restrictions (subfield names still cannot begin with `$`).

[Source: https://www.mongodb.com/docs/manual/core/document/] **Collections** are groups of documents, and **databases** are groups of collections — MongoDB's "object-oriented" document model is designed to let data structures mirror application object models, avoiding an object-relational mapping layer.

[Source: https://www.mongodb.com/docs/manual/core/document/] BSON is a binary representation of JSON documents that supports more data types than plain JSON; the specification lives at bsonspec.org.

[Source: https://www.mongodb.com/docs/manual/core/document/] Documents support dot notation to reach into embedded documents and arrays (e.g. `"name.last"`, `"contribs.2"`).

[Source: https://www.mongodb.com/docs/manual/core/document/] Maximum BSON document size is 16 MiB; field order is preserved on writes (except that `_id` is always first); duplicate field names are not supported and can cause unexpected behavior.

[Source: https://www.mongodb.com/docs/manual/crud/] The CRUD API is built around per-collection operations: `insertOne`/`insertMany` (create), `find` (read, supporting queries against embedded documents and arrays), `updateOne`/`updateMany`/`replaceOne` (update), and `deleteOne`/`deleteMany` (delete). Write operations are atomic at the single-document level.

[Source: https://www.mongodb.com/docs/manual/aggregation/] Beyond CRUD, the **aggregation framework** is the primary mechanism for multi-document analytics: pipelines of stages (`$match`, `$group`, `$unwind`, `$sort`, `$limit`, `$lookup`, `$filter`, `$merge`, `$out`, etc.) where each stage's output feeds the next.

---

## 2. Architecture

### Storage engine (WiredTiger)

[Source: https://www.mongodb.com/docs/manual/core/wiredtiger/] WiredTiger is the default storage engine for MongoDB Atlas, Enterprise, and Community Edition alike.

[Source: https://www.mongodb.com/docs/manual/core/wiredtiger/] WiredTiger provides document-level concurrency control using optimistic concurrency control for most operations, with only intent locks held at the global/database/collection levels; conflicting operations are detected and transparently retried.

[Source: https://www.mongodb.com/docs/manual/core/wiredtiger/] **As of MongoDB 7.0**, a dynamic algorithm automatically tunes the number of concurrent storage-engine transactions (read/write "tickets"), capped at 128 read and 128 write tickets, configurable via `storageEngineConcurrentReadTransactions` / `storageEngineConcurrentWriteTransactions`.

[Source: https://www.mongodb.com/docs/manual/core/wiredtiger/] Default compression: Snappy block compression for most collections, zstd for time-series collections, prefix compression on indexes by default; journal is Snappy-compressed by default (records ≤128 bytes are not compressed). Compressors are configurable via `storage.wiredTiger.*` settings.

[Source: https://www.mongodb.com/docs/manual/core/wiredtiger/] Default WiredTiger internal cache size is the larger of `50% × (RAM − 1 GB)` or `256 MB`, configurable via `--wiredTigerCacheSizeGB`/`storage.wiredTiger.engineConfig.cacheSizeGB` or a percentage-based `--wiredTigerCacheSizePct` (up to 80% of available memory); valid range 0.256 GB–10,000 GB. The internal cache holds uncompressed collection data and compressed index data; the filesystem cache picks up the remainder.

[Source: https://www.mongodb.com/docs/manual/core/wiredtiger/] WiredTiger uses a write-ahead log (journal) for durability between checkpoints (checkpoints occur roughly every 60 seconds) and MVCC to provide point-in-time snapshots for operations. **As of MongoDB 5.0**, snapshot history retention is configurable via `minSnapshotHistoryWindowInSeconds`.

[Source: https://www.mongodb.com/docs/manual/core/wiredtiger/] Cache cannot be pinned per document, is not partitioned between reads/writes, and is allocated to the whole `mongod` instance rather than per-database/per-collection.

### Replication

[Source: https://www.mongodb.com/docs/manual/core/replica-set-architectures/] A **replica set** has one primary (accepts all writes, replicates via the oplog) and one or more secondaries (replicate from the primary), plus optional non-data-bearing **arbiters** that vote in elections only.

[Source: https://www.mongodb.com/docs/manual/core/replica-set-architectures/] Replica sets support up to 50 total members but only 7 voting members; a majority of voting members must be reachable to elect a primary. Recommended: an odd number of voting members to avoid ties/split-brain (e.g., 3 members tolerate 1 failure; 5 members tolerate 2).

[Source: https://www.mongodb.com/docs/manual/core/replica-set-architectures/] The **oplog** is a capped collection on every member recording all data-modifying operations; secondaries replicate off it.

[Source: https://www.mongodb.com/docs/manual/core/replica-set-architectures/] Read preference defaults to routing reads to the primary; `secondaryPreferred`/`secondary` and tag sets can direct reads elsewhere (e.g., per data center). Cluster-wide write concern can be set via the `setDefaultRWConcern` command.

[Source: https://www.mongodb.com/docs/manual/core/replica-set-architectures/] The minimum recommended production topology is a **three-member replica set**. For geographic distribution, deploy across an odd number of data centers, keep at least one member in an alternate data center, and set lower priority on non-primary-region members; config servers and shard replica sets should span at least 3 data centers for high availability.

[Source: https://www.mongodb.com/docs/manual/core/replica-set-architectures/] **As of MongoDB 5.0**, replica set members configured purely by IP address (no DNS hostname) fail startup validation — DNS hostnames are required, especially for split-horizon DNS deployments.

[Source: https://www.mongodb.com/docs/manual/core/replica-set-architectures/] Journaling is enabled by default and is essential to replication durability guarantees.

### Sharding

[Source: https://www.mongodb.com/docs/manual/sharding/] A sharded cluster has three component types: **shards** (each deployed as its own replica set, holding a subset of the data), **config servers** (deployed as a Config Server Replica Set, or CSRS, holding cluster metadata), and **mongos** query routers. Applications connect only to `mongos`, never directly to a shard.

[Source: https://www.mongodb.com/docs/manual/sharding/] Data is distributed by a **shard key**; populated collections must already have an index that starts with the shard key (MongoDB auto-creates it for empty collections). **As of MongoDB 5.0**, sharded collections can be resharded to a new shard key.

[Source: https://www.mongodb.com/docs/manual/sharding/] Two sharding strategies: **hashed sharding** (even distribution, but range queries scatter-gather across shards) and **ranged sharding** (enables targeted queries but distribution quality depends heavily on shard key choice).

[Source: https://www.mongodb.com/docs/manual/sharding/] Data is partitioned into **chunks**; a background **balancer** migrates chunks between shards for even distribution. A single shard can only participate in one chunk migration at a time. **As of MongoDB 8.0**, `sh.shardAndDistributeCollection()` allows sharding and immediately redistributing to the same key without waiting on the balancer.

[Source: https://www.mongodb.com/docs/manual/sharding/] **As of MongoDB 5.1**, Cluster Wide Write Concern (CWWC) must be set when adding shards.

[Source: https://www.mongodb.com/docs/manual/sharding/] **As of MongoDB 8.3**, DDL operations and `applyOps` run only on `mongos` for all sharded clusters (see Breaking Changes below for the related 8.0 change that already blocked most direct-to-shard commands).

---

## 3. APIs

[Source: https://www.mongodb.com/docs/manual/crud/] **CRUD API**: `insertOne`, `insertMany`, `find`, `updateOne`, `updateMany`, `replaceOne`, `deleteOne`, `deleteMany`, plus bulk write operations. Insert operations auto-create the target collection if it doesn't exist.

[Source: https://www.mongodb.com/docs/manual/aggregation/] **Aggregation API**: pipeline-based (`db.collection.aggregate([...])`), with narrower single-purpose helpers `count()`, `distinct()`, and `estimatedDocumentCount()`. Default per-stage memory limit is 100 MB; `allowDiskUse` permits spilling to disk for larger operations. Pipelines are read-only unless they end in `$merge` or `$out`.

[Source: https://www.mongodb.com/docs/drivers/] MongoDB officially develops and supports drivers for **C, C++, C#, Go, Java, Kotlin, Node.js, PHP, Python, Ruby, Rust, Scala, and TypeScript** — "MongoDB actively develops new features, adds performance enhancements, fixes bugs, and applies security patches to them." Compatibility across server/driver versions is tracked on a dedicated compatibility-tables page (`/docs/drivers/compatibility/`).

[Source: https://www.mongodb.com/docs/drivers/] MongoDB's docs explicitly list community-maintained libraries built on top of the official drivers (e.g., Mongoose for Node.js, Prisma) as distinct from the officially supported driver set.

[Source: https://www.mongodb.com/docs/manual/core/transactions/] **Multi-document ACID transaction API**: `session.startTransaction()` / `commitTransaction()` / `abortTransaction()`, tied to a client session; supported on replica sets **as of MongoDB 4.0** and sharded clusters **as of MongoDB 4.2**.

[Source: https://www.mongodb.com/docs/manual/data-modeling/schema-validation/specify-json-schema/] **Schema validation API**: `$jsonSchema` validator specified at `createCollection`/`collMod` time, with `validationLevel` and `validationAction` (`error` to reject non-conforming writes, `warn` to log but allow) controlling enforcement.

---

## 4. Configuration

[Source: https://www.mongodb.com/docs/manual/reference/configuration-options/] `mongod`/`mongos` are configured via a **YAML** config file (YAML does not support tab indentation — use spaces). Default locations: `/etc/mongod.conf` (Linux apt/yum/zypper packages), `/usr/local/etc/mongod.conf` or `/opt/homebrew/etc/mongod.conf` (macOS Homebrew, Intel vs Apple Silicon), `<install dir>\bin\mongod.cfg` (Windows MSI).

[Source: https://www.mongodb.com/docs/manual/reference/configuration-options/] Config file is passed at startup via `--config`/`-f` (e.g. `mongod --config /etc/mongod.conf`).

[Source: https://www.mongodb.com/docs/manual/reference/configuration-options/] Major config sections: `systemLog` (verbosity 0–5, destination `file`/`syslog`, log rotation mode `rename`/`reopen`), `processManagement` (`fork`, `pidFilePath`, `timeZoneInfo`), `net` (`port`, `bindIp`, `bindIpAll`, `maxIncomingConnections`, Unix domain socket options), `net.tls` (`mode`: `disabled`/`allowTLS`/`preferTLS`/`requireTLS`, cert/CA file paths), plus `storage`, `replication`, `sharding`, and `security` sections referenced elsewhere in the manual.

[Source: https://www.mongodb.com/docs/manual/reference/configuration-options/] **As of MongoDB 8.0**, config files support **expansion directives** `__rest` (load a value from a REST endpoint) and `__exec` (load a value from a shell command's output), activated via `--configExpand "rest,exec"`; MongoDB's docs specifically warn to lock down file read/write permissions to the `mongod`/`mongos` user when using these.

[Source: https://www.mongodb.com/docs/manual/reference/configuration-options/] Warning specific to Debian/Red Hat official packages: do not hand-edit `systemLog.path`, `storage.dbPath`, or `processManagement.fork` when using the packaged init scripts, or `mongod` may fail to start — use a custom init script instead.

[Source: https://www.mongodb.com/docs/manual/reference/configuration-options/] Before binding to a publicly reachable IP, the docs direct readers to first enable authentication, harden the network, prefer hostnames over IPs for cluster members, and consult the Security Checklist.

---

## 5. Recommended Patterns

[Source: https://www.mongodb.com/docs/manual/data-modeling/design-patterns/] MongoDB's data modeling docs favor designing schema around **application access patterns** rather than normalization, choosing between **embedding** (nesting related data in one document) and **referencing** (storing relationships across documents) per use case.

[Source: https://www.mongodb.com/docs/manual/data-modeling/design-patterns/] Named design patterns documented officially include:
- **Computed Pattern** — precompute/store values in the database so they don't need repeated calculation on read.
- **Bucket/Group Pattern** — group related data into series (e.g., time-bucketed) to improve performance and handle outliers.
- **Polymorphic Pattern** — allow documents in one collection to vary in fields/types for evolving or heterogeneous data.
- **Schema Versioning Pattern** — embed a schema-version marker in documents to allow multiple schema generations to coexist during migrations.
- **Archive Pattern** — move cold/old data to separate storage to keep the active working set lean.
- **Single Collection Pattern** — use references to group related, heterogeneous document types into one collection where useful.

[Source: https://www.mongodb.com/docs/manual/applications/indexes/] Indexing strategy guidance: map application queries to the fields they touch before building indexes; MongoDB generally uses **only one index per query** (an exception being `$or` queries, which may use a different index per clause); profile candidate index configurations against production-representative data; periodically audit and drop unused indexes.

[Source: https://www.mongodb.com/docs/manual/applications/indexes/] The **ESR (Equality, Sort, Range) rule**: order compound index fields as Equality fields first, then Sort fields, then Range fields, for best performance.

[Source: https://www.mongodb.com/docs/manual/applications/indexes/] Combine unique indexes with schema validation to jointly enforce application-level data-design invariants.

[Source: https://www.mongodb.com/docs/manual/data-modeling/schema-validation/specify-json-schema/] `$jsonSchema` validation (draft-4 JSON Schema syntax) is the documented mechanism to enforce document structure — required fields, allowed types, value ranges — at the database layer, independent of application code; `title`/`description` keywords surface in validation-failure error output.

[Source: https://www.mongodb.com/docs/manual/core/transactions/] The transactions page itself recommends denormalized/embedded schema design as the preferred alternative to multi-document transactions wherever the data model allows it, reserving transactions for cases that genuinely require cross-document atomicity.

---

## 6. Anti-Patterns

[Source: https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/] MongoDB's documentation explicitly names five schema anti-patterns:
1. **Unbounded arrays** — arrays that grow without bound risk exceeding the 16 MB document limit and degrade index performance.
2. **Massive number of collections** — too many collections decreases storage-engine performance and adds unnecessary complexity.
3. **Unnecessary indexes** — indexes not backing real queries consume disk space and degrade write performance.
4. **Bloated documents** — excessively large documents degrade common query performance and increase memory usage.
5. **Excessive `$lookup` use** — heavy reliance on `$lookup` (cross-collection joins) signals data that should likely be denormalized/restructured instead.

[Source: https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/] MongoDB Atlas's **Performance Advisor** (M10+ clusters) and **MongoDB Compass Performance Insights** are the officially documented tools for automatically surfacing these anti-patterns in an existing deployment.

---

## 7. Security

[Source: https://www.mongodb.com/docs/manual/security/] Supported authentication mechanisms: **SCRAM** (default), **X.509** certificate auth, **LDAP**, **Kerberos**, and **OIDC/OAuth 2.0**.

[Source: https://www.mongodb.com/docs/manual/security/] Role-Based Access Control (RBAC) is the documented authorization model; access control (authentication enforcement) must be explicitly enabled on self-managed deployments — it is **not on by default**.

[Source: https://www.mongodb.com/docs/manual/security/] Encryption features: **encryption at rest** (an Enterprise feature for self-managed deployments; Atlas offers Customer Key Management), **TLS/SSL in transit** (on by default in Atlas; must be configured explicitly on self-managed instances), **Queryable Encryption** and **Client-Side Field Level Encryption (CSFLE)** for encrypting specific fields while retaining query capability.

[Source: https://www.mongodb.com/docs/manual/security/] Auditing and log redaction of sensitive data are documented capabilities (auditing is Enterprise-only per the Security Checklist page below).

[Source: https://www.mongodb.com/docs/manual/administration/security-checklist/] The official **Security Checklist** for production deployments recommends, in summary:
- Enable access control (SCRAM by default in Community; X.509/LDAP/Kerberos on Enterprise/Atlas).
- Apply RBAC with least privilege; create a dedicated user administrator first; use unique users per person/application.
- Enable TLS/SSL for all `mongod`↔`mongos` and application↔MongoDB connections.
- Encrypt data at rest via WiredTiger's native encryption or filesystem/device-level encryption (e.g. dm-crypt); protect data/config/log/key files with correct filesystem permissions; consider Queryable Encryption/CSFLE for sensitive fields.
- Limit network exposure: run in a trusted network, configure firewalls, disable direct SSH root, use `net.bindIp`, `security.clusterIpSourceAllowlist`, and per-user `authenticationRestrictions`.
- Enable auditing (Enterprise only) for authentication, connection, and user-operation events.
- Run `mongod`/`mongos` under a dedicated, minimally privileged OS user.
- Disable server-side JavaScript with `--noscripting` if unused; leave `net.wireObjectCheck` (input validation) enabled — it's on by default.
- On an ongoing basis: monitor MongoDB CVEs, track EOL dates, patch infrastructure, review network rules/users, rotate credentials, and (for Queryable Encryption users) schedule metadata compaction.
- **Exclude the `storage.dbPath` and `systemLog.path` directories from antivirus/EDR scanning** — scanning them can cause performance degradation and data corruption.

[Source: https://www.mongodb.com/docs/drivers/client-libraries-best-practices/] Driver-level security best practices documented centrally: prefer `mongodb+srv://` connection strings (enables TLS by default, resolves seed hosts via DNS SRV); **validate untrusted input before it is converted from JSON to BSON** to prevent injection, preferring typed document-builder APIs over string concatenation; restrict/avoid server-side JavaScript execution in `$where`/`$function`/`$accumulator` (string-concatenated expressions are an injection vector), and disable it entirely via `security.javascriptEnabled: false` if not needed.

---

## 8. Performance

[Source: https://www.mongodb.com/docs/manual/applications/indexes/] Indexes are the primary performance lever: they speed up queries but add write overhead (every insert/update/delete must also update matching indexes) and consume memory, so the documented guidance is to justify each index by real query frequency and to drop unused ones.

[Source: https://www.mongodb.com/docs/manual/administration/analyzing-mongodb-performance/] `serverStatus` output is the central diagnostic surface: `locks.<type>.timeAcquiringMicros`/`acquireWaitCount`/`deadlockCount` for lock contention, `globalLock.currentQueue.total` and `globalLock.totalTime` vs `uptime` for global-lock pressure, `connections.current`/`connections.available` for connection saturation. Documented common root causes of poor performance: ineffective indexing, non-optimal schema design, poor query structure, architectural issues, insufficient RAM (forcing disk reads), and connection-pool exhaustion.

[Source: https://www.mongodb.com/docs/manual/administration/analyzing-mongodb-performance/] For write-heavy workloads, the documented scaling recommendation is sharding across multiple `mongod` instances rather than vertical scaling alone. Note: some `serverStatus` fields are restricted on Atlas Free/Flex tier clusters.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] Connection pool sizing guidance: size the pool at roughly **110–115% of typical concurrent request volume**.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] `iostat -xmt 1` is recommended to diagnose disk I/O bottlenecks (watch `%util` and `avgrq-sz`); `mongostat --interval 1` to watch active/queued read/write operations (`ar`/`aw` columns); `db.adminCommand("connPoolStats")` for connection pool state; `bwm-ng` for network usage.

[Source: https://www.mongodb.com/docs/manual/core/wiredtiger/] Cache sizing is a first-order performance factor — see Architecture section above for the default formula and tuning knobs.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] Storage/OS-level performance tuning: XFS filesystem strongly recommended over EXT4 for WiredTiger; disable NUMA or interleave memory across nodes (`vm.zone_reclaim_mode=0`, `numactl --interleave=all`); pick I/O scheduler by hardware (`none` for virtualized/NVMe/SSD, `mq-deadline` for spinning disks, `kyber` for mixed workloads on Linux 4.12+); `vm.swappiness` set to 1 (or 0) rather than the distro default; **Transparent Hugepages should be enabled as of MongoDB 8.0+ but disabled on MongoDB 7.0 and earlier**.

---

## 9. Testing

[Source: https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-for-testing/] MongoDB officially documents deploying a self-managed replica set specifically for testing/development purposes (a lighter-weight, non-production topology).

[Source: https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-deploy-docker/] MongoDB officially ships and documents the `mongodb/mongodb-atlas-local` Docker image for creating a local Atlas-compatible deployment for development/testing (`docker run -p 27017:27017 mongodb/mongodb-atlas-local`, with optional `MONGODB_INITDB_ROOT_USERNAME`/`MONGODB_INITDB_ROOT_PASSWORD` env vars and a documented Docker Compose pattern). Minimum requirements documented: Docker Desktop v4.31+ or Docker Engine v27.0+, 2 GB RAM / 2 CPU cores, port 27017 free, optionally `mongosh` v2.0+.

[Source: https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-deploy-docker/] This official page does **not** mention Testcontainers; MongoDB's own docs focus on direct Docker / Docker Compose workflows rather than a Testcontainers-based flow.

[Source: https://www.mongodb.com/docs/drivers/client-libraries-best-practices/] The best-practices page shared across driver docs is scoped to security guidance only — it does not cover unit/integration testing methodology, connection-pooling test strategy, or retryable-write/read testing.

Unresolved: whether MongoDB officially documents or endorses in-process/in-memory test servers (the kind provided by the popular but community-maintained `mongodb-memory-server` npm package) could not be confirmed — a search of official docs turned up no MongoDB-authored guidance on this pattern, only community forum discussion. Not documented / could not verify beyond the two officially-documented local-deployment paths above (replica-set-for-testing tutorial, and the `mongodb-atlas-local` Docker image).

---

## 10. Deployment

[Source: https://www.mongodb.com/docs/manual/installation/] Deployment paths documented: **MongoDB Atlas** (fully managed, multi-cloud across AWS/Azure/GCP, described in the docs as including "AI-ready" features like integrated Vector Search and Stream Processing, with a free tier); **self-managed Community Edition** (free, installable via OS package managers — APT, DNF, Zypper); **self-managed Enterprise Edition** (supported on Red Hat/CentOS/Ubuntu/Debian/SUSE/Amazon Linux, macOS, Windows, and Docker).

[Source: https://www.mongodb.com/docs/manual/installation/] Kubernetes deployment options: the **Atlas Kubernetes Operator** for managed/cloud deployments, and separate **Controllers for Kubernetes Operator** for on-premises Kubernetes.

[Source: https://www.mongodb.com/docs/manual/installation/] Infrastructure-as-code integrations documented: an Atlas Terraform provider and AWS CloudFormation resources.

[Source: https://www.mongodb.com/docs/manual/installation/] Important package-manager caveat: APT/DNF/Zypper installs can only be **patch-upgraded** in place; major/minor version upgrades require following the full OS-specific installation instructions rather than a simple package upgrade.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] Recommended production OS/CPU baseline: Amazon Linux, Debian, RHEL (and RHEL-compatible Rocky Linux 8.0+/AlmaLinux 8.0+), SLES, Ubuntu LTS, or Windows Server; Intel Haswell-or-later / AMD Bulldozer-or-later / ARMv8.2-A-or-later; **MongoDB 5.0+ requires AVX instruction-set support**.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **Critical compatibility note**: MongoDB is documented as incompatible with **Linux kernel versions 6.19 through 7.0.13** due to a TCMalloc incompatibility that causes crashes; the documented fix is to upgrade to kernel 7.0.14 or later. This affects all MongoDB packages (direct download, package managers, and Docker images).

---

## 11. Migration

**Upgrading between major server versions:**

[Source: https://www.mongodb.com/docs/manual/tutorial/upgrade-revision/] MongoDB versions follow `X.Y.Z` semantic versioning (major.minor.patch); patch releases are documented as never introducing backward-breaking changes. The central mechanism gating a major-version binary upgrade is **`featureCompatibilityVersion` (FCV)** — before upgrading `mongod`/`mongos` binaries to a new major version, the deployment's FCV must first be fully raised to the current version (checked via `db.adminCommand({ getParameter: 1, featureCompatibilityVersion: 1 })`); restarting with a newer binary before FCV has finished upgrading can crash nodes.

[Source: https://www.mongodb.com/docs/manual/tutorial/upgrade-revision/] Documented upgrade order: (1) upgrade drivers first, (2) upgrade standalone instances, (3) upgrade replica sets not part of a sharded cluster, (4) upgrade sharded clusters. For a **replica set**: upgrade all secondaries one at a time (each must return to `SECONDARY` state before continuing) then step down and upgrade the primary last. For a **sharded cluster**: disable the balancer, upgrade config servers (as a replica set), upgrade each shard, upgrade all `mongos` routers (any order), then re-enable the balancer.

[Source: https://www.mongodb.com/docs/manual/tutorial/upgrade-revision/] Preferred upgrade method is OS package management with official MongoDB packages; the documented fallback is manual binary replacement (download → shutdown → replace binaries → update config if needed → restart).

**Migrating from a relational database:**

[Source: https://www.mongodb.com/docs/relational-migrator/] MongoDB officially provides **Relational Migrator**, a free tool for migrating from relational databases (Oracle, SQL Server, MySQL, PostgreSQL, and others) to MongoDB Atlas or a self-managed deployment. It includes an entity-relationship diagram builder to map relational schema to MongoDB schema (starting from a recommended schema, a 1:1 mapping, or from scratch), and supports point-in-time snapshot migrations, batch migrations, and incremental syncs for migrating legacy applications with or without downtime.

---

## 12. Version Information

[Source: https://www.mongodb.com/docs/manual/reference/versioning/] Versioning format is `X.Y.Z` (release series `X.Y`, patch `Z`).

[Source: https://www.mongodb.com/docs/manual/reference/versioning/] **Release model as currently documented**: Major releases ship roughly every 2 years with a 5-year lifecycle. Since **MongoDB 8.2**, MongoDB also ships **minor releases** within a major series (e.g., 8.2, 8.3) that the docs describe as "as stable as major releases" and suitable for production, trading a longer support window for more frequent, sequential mandatory upgrades — minor releases **may not support Atlas Live Migration or `mongosync`**, and upgrades through minor releases must be sequential (e.g. 8.1 → 8.2 → 8.3, no skipping), with the previous minor release stopping patches once a new one ships. Patch releases (`X.Y.Z`) ship as needed for both major and minor series.

[Source: https://www.mongodb.com/community/forums (via WebSearch, MongoDB's own product blog)] **Historical/superseded model**: earlier "Rapid Releases" (introduced alongside the Stable API in MongoDB 5.0 on a quarterly cadence) were Atlas-only until MongoDB 8.2, when they began being made downloadable for self-managed Community/Enterprise use as well — i.e., 8.2 marks the transition point from "Atlas-only Rapid Release" to "downloadable minor release." [Inference, not confirmed on an official docs page — this synthesis is based on WebSearch snippets referencing MongoDB's own release-cadence blog post plus the official versioning page above, not on a single directly-fetched official page; treat the exact transition mechanics as a summary, not a verbatim citation.]

[Source: https://www.mongodb.com/legal/support-policy/lifecycles] Release lifecycle table (GA date → documented End-of-Life date) as officially published:

| Version | GA Date | End of Life |
|---|---|---|
| 8.3 | May 2026 | October 31, 2029 |
| 8.2 (minor/rapid) | September 2025 | July 31, 2026 |
| 8.0 | October 2024 | October 31, 2029 (extended) |
| 7.0 | August 2023 | August 31, 2027 (extended) |
| 6.0 | July 2022 | July 31, 2025 |
| 5.0 | July 2021 | October 31, 2024 |
| 4.4 | July 2020 | February 29, 2024 |
| 4.2 | August 2019 | April 30, 2023 |
| 4.0 | June 2018 | April 30, 2022 |
| 3.6 | November 2017 | April 30, 2021 |

[Source: https://www.mongodb.com/legal/support-policy/lifecycles] Baseline GA major-release support window is **30 months**; MongoDB has since **extended** 7.0's window to ~4 years (through August 31, 2027) and 8.0's (and later majors') window to ~5 years (through October 31, 2029). A commercial **MongoDB Extended Lifecycle Support Add-On** can extend support up to 2 additional years beyond standard EOL. Driver compatibility guarantee: "MongoDB Drivers released more than 3 years after a MongoDB Server version's end-of-life date will not be compatible with that server version."

[Source: https://www.mongodb.com/docs/manual/release-notes/8.0/ ; https://www.mongodb.com/docs/manual/release-notes/7.0/] As of this research date (2026-09-09), patch-level state observed in the docs: MongoDB 8.0 was at patch **8.0.30** (Sept 8, 2026) and MongoDB 7.0 was at patch **7.0.41** (Sept 2026), both still receiving active CVE/security patches.

Unresolved: whether **MongoDB 9.0** has reached General Availability could not be confirmed from official docs at research time. A WebSearch turned up a reference to "MongoDB 9.0 server PPA artifacts" being published alongside an August 13, 2026 `mongosh` release, suggesting 9.0 packaging/build activity was underway, but no official 9.0 release-notes page was found or fetched, and no official docs page confirms GA status, GA date, or feature scope for 9.0. Treat any claim about MongoDB 9.0 as unverified.

---

## 13. Breaking Changes

**MongoDB 8.0 (vs 7.0)** — [Source: https://www.mongodb.com/docs/upcoming/release-notes/8.0-compatibility/] and [Source: https://www.mongodb.com/docs/manual/release-notes/8.0/]:

- **Query semantics change**: comparisons to `null` in equality match expressions (`$eq`, `$in`, and `$lookup`'s null-local-field matching) **no longer match `undefined` values** — only actual `null` values and missing fields match. This is a behavior-breaking change for any query relying on the old null/undefined equivalence.
- **Direct-to-shard connections restricted**: you can only run a limited set of commands directly against a shard node in a sharded cluster; unsupported commands now return an explicit error directing you to connect via `mongos` (or use the maintenance-only `directShardOperations` role). **As of 8.3**, this was tightened further so that DDL and `applyOps` run only via `mongos`.
- **`"majority"` write concern semantics changed**: acknowledgment now returns once a majority of replica-set members have **written** the oplog entry (rather than applied it), improving performance but changing the exact durability/visibility timing applications should assume.
- **Oplog buffer metrics renamed/restructured**: `metrics.repl.buffer.count`/`maxSizeBytes`/`sizeBytes` are deprecated in favor of separate `metrics.repl.buffer.apply.*` and `metrics.repl.buffer.write.*` metrics, reflecting that secondaries now write and apply oplog batches in parallel.
- **Geospatial query input validation tightened**: malformed geospatial query input is now rejected rather than silently tolerated.
- **`wiredTiger.concurrentTransactions` renamed** to `queues.execution` in `serverStatus` output.
- **TCMalloc upgraded** to a per-CPU-cache design (vs. per-thread caches) to reduce memory fragmentation; `tcmallocReleaseRate` semantics changed to bytes/second (default `0`).
- **Concurrent `compact` commands on the same collection** now return an error instead of being allowed.
- Deprecations: **LDAP authentication** deprecated (still available through the 8.x line, planned removal in a future major release); **hedged reads** deprecated (`nearest` read preference no longer hedges by default); **index filters** deprecated in favor of `setQuerySettings`; `tcmallocAggressiveMemoryDecommit` and `enableFinerGrainedCatalogCacheRefresh` parameters removed; using `timeField` as a shard key on time-series collections deprecated; `cleanupOrphaned` command deprecated in favor of `$shardedDataDistribution`; the `rangePreview` Queryable Encryption algorithm removed in favor of `range`.
- **Time-series `system.buckets` collection handling**: **MongoDB 8.0.4 and earlier** require dropping/renaming any non-time-series `system.buckets` collection **before** upgrading; **MongoDB 8.0.5+** relaxed this so the upgrade itself succeeds and cleanup can happen **after**.
- Known infra issues noted in the release notes rather than the compatibility page: incompatibility with Linux kernel 6.19–7.0.13 (see Deployment section); a TLS/OpenSSL high-CPU issue on `openssl-3.2.2-6.el9_5.x86_64` fixed by upgrading to MongoDB 8.0.5+ or downgrading the OpenSSL package.

**MongoDB 7.0** — [Source: https://www.mongodb.com/docs/manual/release-notes/7.0/]: the fetched 7.0 release-notes page (as currently rendered, reflecting patch 7.0.41 as of Sept 2026) is oriented around the cumulative patch-release changelog (CVE fixes, index-handling/encryption/query-execution fixes across dozens of patches) rather than a curated "what changed vs 6.0" summary; it references a "Critical Advisories" section affecting 7.0.0–7.0.15 requiring an upgrade to the latest 7.0 patch. Not documented / could not verify: a itemized list of 7.0-vs-6.0 breaking changes analogous to the 8.0-compatibility page above — no equivalent `7.0-compatibility` page was located and fetched in this research pass.

---

## 14. Limitations

[Source: https://www.mongodb.com/docs/manual/reference/limits/] Documented hard/soft limits (self-managed unless noted):

- **BSON document size**: 16 MiB max; use GridFS for larger content. Max nesting depth: 100 levels (each object/array adds a level).
- **Naming**: database names < 64 bytes (non-empty, case-sensitive; Windows additionally disallows `/\. "$*<>:|?` and the null char, Unix/Linux disallows `/\. "$` and the null char); collection names ≤ 255 bytes unsharded / ≤ 235 bytes sharded, cannot start with `system.` or contain `$`; field names have no documented length limit but cannot contain the null character; `_id` may be any type except array or regex, must be unique and is immutable.
- **Indexes**: max 64 indexes per collection; max 32 fields in a compound index; max 1024 bytes per index key; 2dsphere indexes cap at 100,000 generated keys per document by default (configurable via `indexMaxNumGeneratedKeysPerDocument`); default `createIndexes` memory budget is 200 MB, shared across all indexes built in one command, configurable via `maxIndexBuildMemoryUsageMegabytes`.
- **Replica sets**: max 50 total members, max 7 voting members, max 7 electable nodes per shard; auto-created oplog caps at 50 GB.
- **Sharded clusters**: max 12 shards for multi-region clusters, max 70 shards for single-region clusters; shard key index must be ascending, a compound index led by the shard key ascending, or hashed — it cannot be descending, partial, geospatial, multikey, text, or wildcard; monotonically increasing shard keys bottleneck insert throughput onto a single shard.
- **Aggregation**: max 1,000 pipeline stages; default 100 MB memory per stage before requiring `allowDiskUse`; only `$bucket`, `$bucketAuto`, `$group`, `$setWindowFields`, `$sort`, and `$sortByCount` can spill to disk, gated by `allowDiskUseByDefault`.
- **Transactions**: default lifetime 60 seconds (`transactionLifetimeLimitSeconds`); max 100,000 write operations per batch; cannot write to capped collections; cannot use `"snapshot"` read concern with capped collections; cannot touch `config`/`admin`/`local` databases or `system.*` collections; cannot create collections in cross-shard write transactions.
- **Sorts**: max 32 sort keys; duplicate fields not allowed in a sort pattern.
- **Capped collections**: max 2³¹ (2,147,483,647) documents.
- **Sessions**: 30-minute idle timeout (expired sessions kill their cursors); `$external` username max 10 KB.
- **Collection/database size**: MongoDB imposes **no hard limit** — bounded only by the host filesystem.
- **Atlas-specific limits** (not applicable to self-managed): up to 100 database users/project, 500 Atlas users/project, 200 IP access-list entries/project, 100 custom roles/project, 25 clusters/project, 250 projects/org, 25 federated instances/project; collection+index counts capped by tier (M10: 5,000; M20–M30: 10,000; M40+: 100,000).

[Source: https://www.mongodb.com/docs/manual/core/transactions/] Additional transaction-specific restrictions: transactions must use `primary` read preference (all ops route to the same member); at most one open transaction per session; `listCollections`/`listIndexes` and most non-CRUD admin commands (`createUser`, `getParameter`, `count`, etc.) are disallowed inside a transaction; `$graphLookup` cannot run against sharded collections inside a transaction; `explain` cannot be used with transaction operations; individual operations inside a transaction must not set their own write concern (only the transaction-level write concern at commit applies); transactions are documented as carrying a materially greater performance cost than single-document writes, and MongoDB explicitly recommends denormalized schema design over transactions where feasible.

---

## 15. Debugging

[Source: https://www.mongodb.com/docs/manual/tutorial/manage-the-database-profiler/] The **database profiler** logs command execution detail (CRUD + admin commands) to the capped `system.profile` collection (default 1 MB, resizable by dropping and recreating with `capped: true`). Levels: `0` off (default), `1` logs ops exceeding a `slowms` threshold (default 100 ms, based on `workingMillis` — excludes lock-wait/flow-control time) or matching an optional filter, `2` logs everything regardless of `slowms`/filter. Configurable at runtime (`db.setProfilingLevel(1, { slowms: 20 })`, `db.getProfilingStatus()`) or at startup (`operationProfiling.mode`/`slowOpThresholdMs` in the config file, or `--profile`/`--slowms` flags). Cannot be enabled on `mongos`. The docs explicitly warn the profiler can degrade production performance and suggest Atlas Query Profiler, Atlas Performance Advisor, or the `$queryStats` aggregation stage as production-safer alternatives.

[Source: https://www.mongodb.com/docs/manual/tutorial/manage-the-database-profiler/] Complementary debugging tools referenced (though not detailed on this specific page): `explain()` for query plan analysis and `db.currentOp()` for inspecting in-flight operations.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] Operational diagnostic tools: `mongostat --interval 1` (watch active/queued read/write ops via `ar`/`aw` columns), `iostat -xmt 1` (disk I/O bottleneck diagnosis, focusing on `%util` and `avgrq-sz`), `db.adminCommand("connPoolStats")` (connection pool inspection), `db.hostInfo()` (check `memLimitMB` — important for confirming WiredTiger cache sizing inside containers with memory limits), and `bwm-ng` for network monitoring.

[Source: https://www.mongodb.com/docs/manual/administration/analyzing-mongodb-performance/] `serverStatus` command output is the central performance/debugging data source (lock contention via `locks.*`, global lock pressure via `globalLock.*`, connection saturation via `connections.*`).

---

## 16. Integration

[Source: https://www.mongodb.com/docs/tools-and-connectors/] MongoDB maintains an official "Tools, Migrators, and Connectors" documentation hub covering its first-party integration ecosystem.

[Source: https://www.mongodb.com/docs/kafka-connector/current/] MongoDB officially maintains the **MongoDB Connector for Apache Kafka** (Confluent-verified), which can act as a Kafka sink (persisting topic data into MongoDB) or a Kafka source (publishing MongoDB change-stream events as Kafka topic messages); documented at `/docs/kafka-connector/current/`.

[Source: https://www.mongodb.com/products/integrations/spark-connector] MongoDB officially maintains a **Connector for Apache Spark** exposing Spark's Scala/Java/Python/R libraries, materializing MongoDB data as DataFrames/Datasets for ML, graph, streaming, and SQL workloads.

[Source: https://www.mongodb.com/products/integrations/connectors] MongoDB officially documents Microsoft-certified **Power BI** and **Tableau** connectors for Atlas, enabling live-data querying with native BI-tool features (Power Query, calculated columns, custom SQL pass-through, etc.).

[Source: https://www.mongodb.com/docs/relational-migrator/] **Relational Migrator** (see Migration section) is the officially documented integration path from relational databases (Oracle, SQL Server, MySQL, PostgreSQL, others) into MongoDB.

[Source: https://www.mongodb.com/docs/drivers/] Officially supported first-party drivers span 13 languages (see APIs section); the docs distinguish these from community ODMs/ORMs like Mongoose and Prisma, which are acknowledged but not officially maintained by MongoDB.

Unresolved: the precise, exhaustive current catalog of every officially maintained MongoDB connector (this research fetched Kafka, Spark, Power BI, and Tableau specifically, plus the general connectors landing page) — a full enumeration would require walking `/docs/tools-and-connectors/` exhaustively, which was out of scope for this pass. Treat the list above as representative, not complete.

---

## 17. Production Considerations

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **Filesystem**: XFS strongly recommended over EXT4 for WiredTiger on Linux (kernel 2.6.36+); disable `atime` on the storage volume (`mount -o noatime`); set block-device readahead between 8–32 (`blockdev --setra 16`); filesystem must support `fsync()` on directories.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **NUMA**: disable NUMA or interleave memory (`vm.zone_reclaim_mode=0`; on systemd, prefix `mongod`'s `ExecStart` with `numactl --interleave=all`); on Windows, enable memory interleaving in BIOS.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **Disk I/O scheduler**: `none` for virtualized/cloud disks and physical NVMe/SSD; `kyber` (Linux 4.12+) for mixed workloads; `mq-deadline` for spinning disks.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **Networking**: run in a trusted network; enable authorization (off by default); never enable the HTTP interface in production (disabled by default); size connection pools at 110–115% of typical concurrent load; tune TCP keepalive to 120 seconds (Linux `net.ipv4.tcp_keepalive_time`, Windows registry `KeepAliveTime`) — values above 300s (Linux) / 600000ms (Windows) are overridden by MongoDB.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **ulimits**: low file-descriptor/process ulimits cause failed connections and outages; MongoDB warns at startup if file descriptors are set below 64,000 (`ulimit -n 64000`, `ulimit -u 64000` recommended).

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **Memory/swap**: set `vm.swappiness` to 1 (preferred) or 0, not the distro default (often 60+); on RHEL/CentOS also set `vm.force_cgroup_v2_swappiness=1`.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **Hugepages**: enable Transparent Hugepages **as of MongoDB 8.0+**; disable THP on **MongoDB 7.0 and earlier** (which perform better with standard 4 KB pages) — this is an explicit version-dependent flip in guidance.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **Hardware**: minimum 2 real cores (or 1 multi-core processor); SSD (SATA-class or better) recommended for price/performance; RAID-10 recommended, RAID-5/6 called out as insufficient; separate data, journal, and log files onto different physical devices where possible; if NFS is required, mount with `bg,hard,nolock,noatime,nointr`.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **Clock sync**: use NTP across all cluster components — clock drift causes unreliable inter-node communication and inconsistent time-dependent behavior; tolerance is controlled by `maxAcceptableLogicalClockDriftSecs`.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **Backups**: the production notes point to a dedicated backup-methods overview covering filesystem snapshots, `mongodump`, Atlas continuous backups, and point-in-time recovery via journaling.

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] **Antivirus/EDR**: explicitly exclude `storage.dbPath` and `systemLog.path` from scanning to avoid performance degradation and data corruption (this same guidance also appears on the Security Checklist page).

[Source: https://www.mongodb.com/docs/manual/administration/production-notes/] Container-specific note: use `db.hostInfo()` to check `memLimitMB` and account for container memory limits when sizing the WiredTiger cache, rather than relying on host-level RAM detection.

---

## Sources Consulted (all official)

- https://www.mongodb.com/docs/ — docs hub / landing
- https://www.mongodb.com/docs/manual/core/document/ — documents, BSON, `_id`, dot notation
- https://www.mongodb.com/docs/manual/crud/ — CRUD API
- https://www.mongodb.com/docs/manual/aggregation/ — aggregation framework
- https://www.mongodb.com/docs/manual/core/replica-set-architectures/ — replication architecture
- https://www.mongodb.com/docs/manual/sharding/ — sharding architecture
- https://www.mongodb.com/docs/manual/core/wiredtiger/ — WiredTiger storage engine
- https://www.mongodb.com/docs/drivers/ — official driver list
- https://www.mongodb.com/docs/drivers/client-libraries-best-practices/ — driver security best practices
- https://www.mongodb.com/docs/manual/reference/configuration-options/ — mongod/mongos config file reference
- https://www.mongodb.com/docs/manual/security/ — security overview
- https://www.mongodb.com/docs/manual/administration/security-checklist/ — production security checklist
- https://www.mongodb.com/docs/manual/applications/indexes/ — indexing strategies
- https://www.mongodb.com/docs/manual/data-modeling/design-patterns/ — schema design patterns
- https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/ — schema anti-patterns
- https://www.mongodb.com/docs/manual/data-modeling/schema-validation/specify-json-schema/ — `$jsonSchema` validation
- https://www.mongodb.com/docs/manual/core/transactions/ — multi-document ACID transactions
- https://www.mongodb.com/docs/manual/tutorial/upgrade-revision/ — major-version upgrade procedure / FCV
- https://www.mongodb.com/docs/relational-migrator/ — Relational Migrator (RDBMS → MongoDB migration)
- https://www.mongodb.com/docs/manual/reference/versioning/ — versioning scheme, release model
- https://www.mongodb.com/legal/support-policy/lifecycles — official support-lifecycle/EOL table
- https://www.mongodb.com/docs/manual/release-notes/8.0/ — MongoDB 8.0 release notes / patch history
- https://www.mongodb.com/docs/manual/release-notes/7.0/ — MongoDB 7.0 release notes / patch history
- https://www.mongodb.com/docs/upcoming/release-notes/8.0-compatibility/ — MongoDB 8.0 breaking/compatibility changes
- https://www.mongodb.com/docs/manual/reference/limits/ — limits and thresholds
- https://www.mongodb.com/docs/manual/tutorial/manage-the-database-profiler/ — database profiler
- https://www.mongodb.com/docs/manual/administration/analyzing-mongodb-performance/ — performance analysis / serverStatus
- https://www.mongodb.com/docs/manual/installation/ — deployment/installation options
- https://www.mongodb.com/docs/manual/administration/production-notes/ — production notes (OS, filesystem, NUMA, networking, hardware)
- https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-deploy-docker/ — official Docker-based local Atlas deployment for dev/test
- https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-for-testing/ — replica set deployment for testing
- https://www.mongodb.com/docs/tools-and-connectors/ — tools/migrators/connectors hub
- https://www.mongodb.com/docs/kafka-connector/current/ — Kafka connector
- https://www.mongodb.com/products/integrations/spark-connector — Spark connector
- https://www.mongodb.com/products/integrations/connectors — connectors landing page (BI connectors, etc.)
