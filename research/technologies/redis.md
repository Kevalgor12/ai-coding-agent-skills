# Redis — Technology Research

Research date: 2026-09-09. Primary source: `redis.io/docs/latest/*` (canonical documentation host — confirmed reachable and current at research time; no evidence found of a doc-host migration away from `redis.io`). Secondary official sources used: `github.com/redis/redis` (core source repo and release notes), `github.com/redis/redis-doc` and `github.com/redis/docs` (docs source repos, referenced for context, not quoted directly), and `redis.io/tutorials/*` / `redis.io/blog/*` (official first-party tutorials and blog, published by Redis the maintaining organization). All claims are tagged per this project's convention: `[Source: <url>]` for documented facts, `[Inference, not confirmed in docs]` for reasoning, "Not documented / could not verify" where docs did not cover something, and "Unresolved: ..." where confidence is genuinely low.

**Doc host note**: [Source: https://redis.io/docs/latest/get-started/] The canonical docs URL pattern is `redis.io/docs/latest/<section>/<page>/`. No migration away from `redis.io` was found. Redis documents several distinct but related products under this one host: **Redis Open Source** (the free/source-available server, formerly "Redis Community Edition"), **Redis Cloud** (`rc` path segment), **Redis Software** (`rs` path segment, formerly "Redis Enterprise Software"), and **Redis Enterprise for Kubernetes** (`operate/kubernetes`). This research focuses on Redis Open Source (the server/database itself) since that is what a "set up Redis" skill would be grounded in, but notes Cloud/Software/Kubernetes docs where they are the only place a topic (e.g. Kubernetes operator, Active-Active) is documented.

**Naming/licensing note**: [Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] As of Redis 8.0 (May 2025), "Redis Community Edition" was renamed **"Redis Open Source"**, and the license changed from the earlier BSD-3-Clause/dual-license arrangement to a **tri-license choice**: (a) Redis Source Available License 2.0 (RSALv2), (b) Server Side Public License v1 (SSPLv1), or (c) GNU Affero General Public License v3 (AGPLv3). [Source: https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/] Versions 7.4 and 7.2 remain on RSALv2/SSPLv1 dual-license (no AGPL option); versions 7.2 and earlier were BSD-3-Clause. This licensing history matters for any skill that recommends "which Redis version/license to adopt."

---

## 1. Core concepts

[Source: https://redis.io/docs/latest/get-started/] Redis is described as "an in-memory data store used by millions of developers as a cache, vector database, document database, streaming engine, and message broker." It supports complex data types with atomic operations defined on those types, and has built-in replication and configurable on-disk persistence.

[Source: https://redis.io/docs/latest/develop/data-types/] Redis Open Source implements the following core data types, each documented with its own overview page and command reference: **Strings** (with **Bitmaps** and **Bitfields** as string sub-features), **Arrays**, **Geospatial indexes**, **Hashes**, **JSON**, **Lists**, **Probabilistic data types** (Bloom filter, Count-min sketch, Cuckoo filter, HyperLogLog, t-digest, Top-K), **Sets**, **Sorted sets**, **Streams**, **Time series**, and **Vector sets**.

- [Source: https://redis.io/docs/latest/develop/data-types/] Sets support add/remove/existence-check in O(1) time regardless of set size.
- [Source: https://redis.io/docs/latest/develop/data-types/] Vector sets are "a specialized data type designed for managing high-dimensional vector data," supporting the HNSW (hierarchical navigable small world) algorithm and cosine-similarity queries, with native hybrid search (vector similarity + structured filters).
- [Version-sensitive, Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] Vector sets were introduced as a **preview** feature in Redis 8.0.0. JSON, Time series, and the five probabilistic data types (Bloom, Cuckoo, Count-min sketch, Top-K, t-digest) — previously separate "Redis Stack" modules — became integral, bundled parts of Redis itself starting with Redis 8.0, along with Redis Search.

[Source: https://redis.io/docs/latest/develop/data-types/] Redis is extensible via two documented mechanisms: (1) server-side functions written in Lua, and (2) custom Redis modules via the modules API.

[Source: https://redis.io/docs/latest/develop/reference/eviction/] Because Redis is fundamentally an **in-memory** system, dataset size is bounded by available RAM; this is a defining architectural trade-off, not merely a configuration detail — "very high write and read speed is achieved" at the cost of data sets that "can't be larger than memory" [Inference, not confirmed in docs: this framing paraphrases the FAQ page found via search, `redis.io/docs/latest/develop/get-started/faq/`, which was not fetched directly in this research pass — treat this specific phrasing as approximate rather than a verbatim quote].

[Source: https://redis.io/docs/latest/develop/using-commands/transactions/] Redis provides **transactions** via `MULTI`/`EXEC`/`DISCARD`/`WATCH`: commands queued between `MULTI` and `EXEC` execute sequentially and atomically as a single isolated step, with no other client's request served in the middle. `WATCH` adds optimistic-locking (check-and-set) semantics.

[Source: https://redis.io/docs/latest/develop/programmability/] "Programmability" in Redis means executing arbitrary user-defined logic server-side via **scripts**, run by an embedded, sandboxed Lua 5.1 interpreter — Redis's only supported scripting engine.

---

## 2. Architecture

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/replication/] At the base of Redis's high-availability story is simple **leader-follower (master-replica) replication**: a master keeps replicas updated by streaming the commands that changed its dataset; on disconnect, a replica attempts **partial resynchronization** (`PSYNC`) using a replication ID + offset pair, and falls back to a **full resynchronization** (master forks, produces an RDB snapshot, streams it, then streams the buffered command backlog) when partial sync isn't possible.

- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/replication/] Replication is **asynchronous by default**: "the master does not wait every time for a command to be processed by the replicas." Synchronous behavior for specific writes can be requested via the `WAIT` command, but this does not turn Redis into a CP (strongly consistent) system — acknowledged writes can still be lost on failover depending on persistence configuration.
- [Version-sensitive, Source: https://redis.io/docs/latest/operate/oss_and_stack/management/replication/] Since Redis 4.0, sub-replicas in a cascading replica-of-replica chain all receive an identical replication stream from the top-level master (not from the intermediate replica's local writes, even if that replica is writable). Since Redis 4.0, writable replicas can also expire TTL'd keys like masters do (except keys in DB numbers >63). Since Redis 2.8.18, **diskless replication** is available (`repl-diskless-sync`), letting the master stream the RDB directly over the wire instead of via a temp file on disk.
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/replication/] Replicas are **read-only by default** (`replica-read-only`), and the docs explicitly discourage using writable replicas except for legacy reasons, noting that "as of version 7.0, these use cases are now all obsolete."

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] **Redis Cluster** is Redis's horizontal-scaling topology: data is automatically sharded across nodes using **16384 hash slots** (not consistent hashing) — a key's slot = CRC16(key) mod 16384. Every node in a cluster requires two open TCP ports: the normal client port (e.g. 6379) and a **cluster bus port** (client port + 10000 by default, e.g. 16379) used for a binary node-to-node protocol handling failure detection, config propagation, and failover authorization.

- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] A minimal working cluster requires **at least 3 master nodes**; a production deployment is recommended to use 6 nodes (3 masters + 3 replicas). Each hash slot's master has 1–N replicas; if a master and all of its replicas fail simultaneously the slots they served become unavailable.
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] Multi-key operations (transactions, Lua scripts touching multiple keys) require all keys to be in the same hash slot, enforced by the user via **hash tags** — a `{...}` substring in the key name, e.g. `user:{123}:profile` and `user:{123}:account` hash to the same slot.
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] **Redis Cluster does not guarantee strong consistency.** Because replication to replicas is asynchronous, writes acknowledged to a client can be lost if the master crashes before propagating them, and a promoted replica did not receive them. A second write-loss scenario occurs during network partitions: a client isolated with a minority-side master can keep writing until **node timeout** elapses, after which the minority side stops accepting writes — but writes sent during that window can be lost if the majority side elects a new master. `WAIT` reduces (but the docs state explicitly does not eliminate) this risk.
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] Redis Cluster does **not** support NATted/port-remapped environments (e.g. default Docker port mapping); Docker's `--net=host` mode is required for cluster nodes to communicate correctly.
- [Version-sensitive, Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] Starting with Redis 5, the project stopped using the word "slave" in new documentation/APIs, except where it remains baked into the wire-level `CLUSTER NODES` output format for backward compatibility.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/] **Redis Sentinel** provides high availability for **non-clustered** Redis: it is a distributed system of Sentinel processes that monitor masters/replicas, detect failures, and orchestrate automatic failover. (Full detail on quorum and failover mechanics is in the fetched-but-truncated Sentinel page; see "Unresolved" below.)

[Source: https://redis.io/docs/latest/develop/reference/protocol-spec/] The client/server wire protocol is **RESP** (Redis Serialization Protocol) — a simple, binary-safe, request/response protocol distinct from Redis Cluster's internal node-to-node binary bus protocol.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/] Redis is documented as fundamentally **single-threaded** for command execution ("Finally, Redis is single threaded"), which the docs frame as advantageous for per-core throughput and predictable latency, but which creates a specific challenge: the single thread must perform incremental background tasks (e.g. key expiration) without materially impacting client-facing latency.

- [Version-sensitive, Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] Redis 8.0 introduced "a new I/O threading implementation, which enables throughput increase on multi-core environments" configured via the `io-threads` parameter — i.e. while command execution logic is single-threaded, I/O handling has become more multi-threaded in recent major versions. Unresolved: the exact scope of what the `io-threads` implementation parallelizes (network I/O only vs. more) was not covered in the pages fetched during this pass.

Not documented / could not verify in the pages fetched: a single consolidated diagram of Redis's internal process architecture (event loop, forked child processes for RDB/AOF, I/O thread pool) in one place — this research pulled the pieces from persistence, replication, and latency-monitoring pages rather than one architecture chapter.

---

## 3. APIs

[Source: https://redis.io/docs/latest/develop/reference/protocol-spec/] Redis's primary wire-level API is **RESP** (Redis Serialization Protocol). [Version-sensitive] RESP1 shipped experimentally in Redis 1.2; **RESP2** became the standard in Redis 2.0; **RESP3** (a superset of RESP2) was introduced as opt-in in **Redis 6.0** via the `HELLO` command handshake. From **Redis 7 onward, both RESP2 and RESP3 clients can invoke all core commands**, though a command's reply may be typed differently depending on protocol version. The docs state future versions "may change the default protocol version" but that full RESP2 deprecation is "unlikely."

- [Source: https://redis.io/docs/latest/develop/reference/protocol-spec/] RESP2 has 6 data types (Simple strings, Simple errors, Integers, Bulk strings, Arrays, plus historical null-bulk-string/null-array encodings). RESP3 adds Nulls, Booleans, Doubles, Big numbers, Bulk errors, Verbatim strings, Maps, Attributes, Sets, Pushes, plus streamed-string and streamed-aggregate encodings (the latter two are permitted for modules but Redis itself does not emit them).
- [Source: https://redis.io/docs/latest/develop/reference/protocol-spec/] Bulk strings are limited to **512 MB by default**, controlled by `proto-max-bulk-len`.
- [Source: https://redis.io/docs/latest/develop/reference/protocol-spec/] Clients send commands as a RESP Array of Bulk Strings; **pipelining** (batching multiple commands in one write, reading replies later) and **inline commands** (space-delimited, for interactive `telnet`-style sessions) are both part of the protocol-level API surface.

[Source: https://redis.io/docs/latest/develop/clients/] Redis officially documents **first-party client libraries** for nine languages (with the GitHub org actively maintaining these): Python (`redis-py`, plus `RedisVL` for vector workloads), C#/.NET (`StackExchange.Redis`, `NRedisStack`), JavaScript (`node-redis`, `ioredis`), Java (`Jedis`, `Lettuce`), Go (`go-redis`), PHP (`Predis`, "best effort" support), C (`hiredis`), Rust (`redis-rs`, "best effort"), Ruby (`redis-rb`). Several **Object-Mapping (OM)** libraries are also documented for Python, C#/.NET, Node.js, and Java/Spring. Community-supported (non-Redis-maintained) clients exist for C++, Dart, PHP (phpredis), Python (coredis), and Scala.

[Source: https://redis.io/docs/latest/develop/using-commands/transactions/] The **transaction command API** (`MULTI`, `EXEC`, `DISCARD`, `WATCH`, `UNWATCH`) is a distinct API surface layered on top of normal commands.

[Source: https://redis.io/docs/latest/develop/programmability/] The **scripting API** consists of `EVAL`/`EVALSHA` (since Redis 2.6.0) for ad-hoc Lua scripts, and, since **Redis 7.0**, **Redis Functions** (`FUNCTION LOAD`, `FCALL`) which decouple scripts from application code into first-class, independently deployable database objects.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/] The **ACL command family** (`ACL SETUSER`, `ACL GETUSER`, `ACL LIST`, `ACL CAT`, `ACL GENPASS`, `ACL LOAD`, `ACL SAVE`, etc.) is a documented management API for access control, distinct from the data-plane commands.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/] [Version-sensitive] Since **Redis 8.10.0**, a new **`BACKUP` command family** (`BACKUP START`, `BACKUP LIST`, `BACKUP SEAL`, `BACKUP STATUS`, `BACKUP ABORT`, `BACKUP CLEANUP`) provides an online, self-contained backup API that reuses the multi-part AOF format without stopping writes or manually managing AOF rewrites.

Not documented / could not verify: a formal OpenAPI/gRPC-style spec for the command set beyond the per-command reference pages linked from `redis.io/docs/latest/commands/`; this research did not enumerate the full command reference (hundreds of commands) as that is out of scope for a technology-grounding document of this size.

---

## 4. Configuration

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] The canonical config file is **`redis.conf`**, and settings can be applied at three points: in `redis.conf` at startup, via `CONFIG SET` at runtime (with `CONFIG REWRITE` to persist runtime changes back to the file), or via command-line flags at server start (implied by the `redis-server ./redis.conf` invocation pattern shown across the docs).

- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] Cluster-specific config directives include `cluster-enabled`, `cluster-config-file` (an auto-generated, not user-edited, node-state file, default `nodes.conf`), `cluster-node-timeout`, `cluster-slave-validity-factor`, `cluster-migration-barrier`, `cluster-require-full-coverage`, and `cluster-allow-reads-when-down`.
- [Source: https://redis.io/docs/latest/develop/reference/eviction/] Memory-management directives: `maxmemory` (cache size limit; default unlimited on 64-bit, implicit 3GB on 32-bit systems), `maxmemory-policy` (eviction policy selector), `maxmemory-samples` (LRU/LFU/LRM approximation sample size, default 5), `lfu-log-factor` and `lfu-decay-time` (LFU counter tuning).
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/] `latency-monitor-threshold` (milliseconds; 0 = disabled by default) enables the built-in latency-spike monitor.
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/] Persistence directives: `save <seconds> <changes>` (RDB snapshot triggers), `appendonly yes|no` (AOF on/off), `appendfsync always|everysec|no` (AOF durability policy, default `everysec`), `appenddirname` (multi-part AOF directory, since Redis 7.0.0), and (since **Redis 8.10.0**) `backupdirname` (default `backupdir`) and `backup-sealed-ttl` for the new `BACKUP` command family; `preload-file` (startup-only, `<type>:<path>` where type is `aof` or `rdb`) restores a specific backup/RDB file at startup.
- [Source: https://redis.io/docs/latest/develop/reference/clients/] Client-handling directives: `maxclients` (default 10,000, configurable since Redis 2.6), `timeout` (idle-client disconnect, does not apply to Pub/Sub clients), `maxmemory-clients` (aggregate client-buffer memory cap, default 0 = off; available since **Redis 7.0**).
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/] Security directives: `bind` (interface binding, e.g. `bind 127.0.0.1`), `requirepass` (legacy single-password auth, now interpreted as setting the `default` ACL user's password), `rename-command` (deprecated mechanism to rename/disable commands, e.g. `rename-command CONFIG ""`).
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/] ACL users can be defined directly in `redis.conf` (`user <name> ...rules...`) or in an external file referenced by `aclfile /path/to/users.acl` — the two mechanisms are documented as **mutually incompatible** (Redis requires choosing one).
- [Source: https://redis.io/docs/latest/develop/programmability/] `busy-reply-threshold` sets the maximum script/function execution time in milliseconds (default 5 seconds).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/] For Docker deployments, a custom `redis.conf` is supplied either by building a derived image (`COPY redis.conf /usr/local/etc/redis/redis.conf` + `CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]`) or by bind-mounting a config directory at `docker run` time.

Not documented / could not verify: this research did not fetch the full annotated example `redis.conf` shipped in the source distribution (referenced repeatedly throughout the docs as the authoritative, most-complete config reference) — the docs consistently point to that file as the canonical source for the complete list of directives and their defaults, rather than duplicating it on the config-file webpage.

---

## 5. Recommended patterns

[Source: https://redis.io/docs/latest/develop/using-commands/pipelining/] **Pipelining** — batching multiple commands into one write and reading replies afterward — is documented as the recommended way to reduce round-trip-time (RTT) overhead and dramatically increase throughput (the docs show up to a 10x increase in ops/sec with longer pipelines, and roughly a 5x wall-clock improvement in a Ruby benchmark even over a low-RTT loopback interface). The docs recommend batching in bounded chunks (e.g. 10k commands) rather than unboundedly, since the server must queue all replies in memory while pipelining.

[Source: https://redis.io/docs/latest/develop/using-commands/transactions/] For atomic **check-and-set style updates**, the documented pattern is `WATCH key` → read → `MULTI` → write commands → `EXEC`, retrying on a nil `EXEC` reply (indicating a watched key changed). [Version-sensitive] Since **Redis 8.4**, `SET` supports `IFEQ`/`IFNE`/`IFDEQ`/`IFDNE` options and there is a new `DELEX` command, giving atomic single-command compare-and-set / compare-and-delete for strings as a simpler, faster alternative to the `WATCH`/`MULTI`/`EXEC` pattern for that specific case.

[Source: https://redis.io/docs/latest/develop/programmability/] For logic that needs both a read and a write with minimal latency ("read, compute, write"), the docs recommend **Lua scripting/Functions over pipelining**, since scripts execute atomically server-side and pipelining alone can't let a client react to a read's result before issuing the dependent write.

[Source: https://redis.io/docs/latest/develop/programmability/] Use **`EVAL_RO`/`EVALSHA_RO`/`FCALL_RO`** (or the `no-writes` script flag) for read-only scripts: they can always run on replicas, are always killable via `SCRIPT KILL`, never fail under OOM, and aren't blocked during coordinated-failover write pauses — advantages the docs recommend leaning on for ACL-restricted or replica-read-scaling use cases. [Version-sensitive] Introduced in Redis 7.0; several edge-case behaviors (whether `no-writes` implies `allow-oom`, whether it permits running during write pauses, and whether `PUBLISH`/`SPUBLISH`/`PFCOUNT` count as writes) changed in **Redis 7.0.1**.

[Source: https://redis.io/docs/latest/develop/reference/eviction/] For cache-style workloads, the docs give explicit eviction-policy selection guidance: `allkeys-lru` as the general-purpose default (per the Pareto-principle assumption that a subset of keys dominates access), `allkeys-lrm` (Redis 8.6+) when distinguishing "read-heavy but rarely written" data, `allkeys-random` for roughly-uniform access patterns, and `volatile-ttl` when the application can predict good eviction candidates and assign them short TTLs.

[Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/] (Official Redis tutorial content, inverse framing of anti-patterns 3 and 7 below.) Recommended patterns include: connecting through a **proxy** rather than directly to Redis instances to avoid reconnect-flood failover storms; running an **odd number of shards/replicas (primary + 2 replicas)** in open-source Redis to avoid split-brain during partitions; **sharding hot keys** across multiple keys/shards using hashing when a single key receives disproportionate traffic; and preferring **`SCAN`** or Redis Search over `KEYS` for keyspace iteration in production.

[Source: https://redis.io/docs/latest/develop/tools/cli/] For debugging keyspace shape, `redis-cli --bigkeys` / `--memkeys` / `--keystats` (scan-based, safe for production use, unlike `KEYS`) are the documented tools for finding oversized keys and memory hot spots; `--hotkeys` finds frequently-accessed keys but "only works when maxmemory-policy is `*lfu`."

---

## 6. Anti-patterns

[Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/] (Official Redis-authored tutorial, published on redis.io.) The tutorial enumerates 11 documented anti-patterns with severity/impact ratings:

1. **Large database on a single shard** (High severity) — slows failover, backup, and recovery, and puts the entire dataset in one failure's blast radius. Rule of thumb given: keep shards under ~25 GB or ~25K ops/sec (up to ~50GB tolerable at lower ops/sec).
2. **Connecting directly to Redis instances without a proxy** (High) — a reconnect flood after a network hiccup can overwhelm the single-threaded Redis process and force an unnecessary failover.
3. **Using only one replica in open-source Redis** (Medium) — creates split-brain risk during partitions; the docs recommend an odd number of shards (primary + 2 replicas) for quorum.
4. **Serial single operations without pipelining** (Medium) — wastes round-trips and inflates latency, especially over high-RTT links; see Section 5.
5. **Caching keys without TTL** (High) — leads to unbounded memory growth and eviction storms.
6. **Endless replication loop** — replicating a very large, actively-written database over a slow/saturated link can mean replication never completes because writes outpace transfer; documented fix is tuning replica/client buffers.
7. **Hot keys** (High) — in a cluster, all traffic for one key hits one shard regardless of cluster size, since key→slot mapping is deterministic; `redis-cli --hotkeys` (requires an LFU `maxmemory-policy`) is the documented detection tool.
8. **Using the `KEYS` command in application code** (High) — `KEYS` is an O(N) full-keyspace scan that **blocks Redis for its duration** (Redis is single-threaded); the docs explicitly liken this to an unbounded `SELECT ... FROM` without a `WHERE` clause and recommend `SCAN` (incremental, non-blocking) or Redis Search instead.
9. **Running ephemeral Redis (no persistence, no HA) as a primary database** (High) — a restart means total data loss and any downtime takes the whole application down; open-source Redis needs Sentinel for HA plus AOF/RDB for durability to be safe as a primary store.
10. **Storing JSON blobs as opaque strings** (Medium) — forces full deserialize/reserialize on every read/update, precludes atomic field-level updates, and requires application-level locking/`WATCH`; the documented fix is using `HASH` or the native JSON data type.
11. **Converting a relational table or JSON document to a `HASH` without considering query patterns** (Medium) — leaves `SCAN` as the only retrieval mechanism (slow, `MATCH`-only filtering); documented fix is storing the object as a string plus maintaining reverse indexes in `SET`/sorted-set structures pointing back to it.

[Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/] The tutorial also separately attributes to Redis's creator (Salvatore Sanfilippo, "antirez") the guidance that using `SELECT`/multiple numbered databases inside one Redis instance is an anti-pattern, particularly in microservice architectures, recommending a dedicated Redis instance per logical database instead.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/replication/] Running a replicated setup where the **master has persistence disabled** combined with **auto-restart on crash** is explicitly documented as dangerous: a crashed, auto-restarted master comes back with an empty dataset, and connected replicas will then replicate that emptiness, destroying their own copies. The docs recommend disabling auto-restart whenever a persistence-off master is used with replication (including with Sentinel).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/#disallowing-specific-commands] Using `rename-command` to hide/disable commands is explicitly marked as **deprecated and may be removed in future versions** — ACL rules are the documented replacement.

---

## 7. Security

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/] The documented **security model**: "Redis is designed to be accessed by trusted clients inside trusted environments" — it is explicitly *not* designed to be exposed directly to untrusted networks/the internet; untrusted access should always be mediated by an application layer implementing its own ACLs and input validation.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/] **Network security**: bind Redis to a trusted interface only (`bind 127.0.0.1`) and firewall the Redis port from untrusted networks — failing to do so can be catastrophic, since e.g. a single unauthenticated `FLUSHALL` can wipe the whole dataset.

- [Version-sensitive, Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/] Since **Redis 3.2.0**, **protected mode** activates automatically when Redis runs with default config (bound to all interfaces) and no password: it then only replies to loopback-interface connections, returning an explanatory error to any other client. It can be manually disabled by the administrator.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/] Two authentication mechanisms exist: (1) **ACLs**, the recommended method since **Redis 6**, allowing named users with fine-grained permissions; (2) the legacy `requirepass` single-password mechanism (all clients share one password, sent via `AUTH <password>`), which under the hood now just sets the `default` ACL user's password. `AUTH` traffic is sent **unencrypted** absent TLS, so it does not protect against network eavesdropping.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/] **ACL details**: [Version-sensitive] ACLs were introduced in Redis 6; in default configuration Redis 6 behaves exactly like pre-ACL Redis (single implicit `default` user with full access, backward-compatible). Rule syntax highlights: `+<command>`/`-<command>` grant/revoke individual commands (subcommand-level allow/block via `|`, e.g. `+config|get`, added in **Redis 7.0**); `+@<category>`/`-@<category>` grant/revoke whole command categories (29 categories documented, e.g. `@admin`, `@dangerous`, `@read`, `@write`, `@fast`, `@slow`); `~<pattern>` / `%R~<pattern>` / `%W~<pattern>` (read/write-scoped key patterns, **Redis 7.0+**) restrict key access; `&<pattern>` restricts Pub/Sub channels (**Redis 6.2+**); **selectors** — parenthesized secondary rule sets, e.g. `+GET ~key1 (+SET ~key2)` — allow multiple independent permission sets per user (**Redis 7.0+**).

- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/] Passwords are stored **SHA-256 hashed** server-side; `ACL GENPASS` generates a cryptographically random 256-bit password. The docs explicitly argue against slow/salted password-hashing schemes for ACL passwords, reasoning that these are shared secrets between server and client rather than human-memorized credentials, so brute-force resistance should come from length/randomness, not hash cost.
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/] Key-pattern restrictions apply only to commands that take explicit key arguments; whole-keyspace commands like `FLUSHALL`/`FLUSHDB`/`SWAPDB` are **not** limited by key patterns and must be explicitly excluded (`-flushall -flushdb -swapdb`) even for a user scoped to `~tenant1:*`.
- [Version-sensitive, breaking change, Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] As of **Redis 8.0**, the existing `@read`/`@write`/`@dangerous`/`@admin`/`@slow`/`@fast` ACL categories now include Redis Search, JSON, time series, Bloom, Cuckoo, Top-K, count-min sketch, and t-digest commands — previously they did not. This silently **widens** existing `+@read`/`+@write`-style rules (e.g. a `+@read` user can now run `FT.SEARCH`) and can **narrow** `+@all -@write`-style rules (e.g. such a user can no longer run `JSON.SET`). The docs explicitly call this a potentially breaking change requiring re-analysis of existing ACL rules on upgrade.
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/] Since **Redis 8.8**, `ACL LOAD` allows comment lines (`#`) in the external ACL file (stripped on load, not persisted through `ACL LOAD`/`ACL SAVE` round-trips).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/] **TLS**: Redis has optional TLS support across all channels — client connections, replication links, and the Cluster bus protocol.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/] **Attack-surface notes documented explicitly**: Redis randomizes its internal hash-table seed per execution to prevent algorithmic-complexity (hash-flooding) DoS attacks; the `SORT` command's `qsort`-based implementation is *not* randomized and can in principle be driven to quadratic worst-case behavior by crafted input. The RESP protocol has no string-escaping concept (prefixed-length, binary-safe strings), so classic injection attacks are not possible via a conforming client library — this safety also extends to Lua scripts run via `EVAL`, though the docs caution against building a script's source from untrusted-input strings. Redis does not require root privileges and the docs recommend running it as a dedicated unprivileged `redis` user; `CONFIG SET`'s ability to alter the working directory/dump filename is flagged as a documented historical security issue (RDB files can be written to attacker-influenced paths) with a link to an external write-up by Redis's creator.

Unresolved: the fetched `security/` page table-of-contents lists a "String escaping and NoSQL injection" and "Code security" section (both summarized above), but the full detail of "Other security topics" (a subsection pointing to further pages) was not individually fetched in this pass — there may be additional first-party security guidance (e.g. dedicated TLS setup instructions, a Redis University security-course reference the page links to) not captured here.

---

## 8. Performance

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/] The docs maintain a dedicated "Optimizing Redis" section covering benchmarking, profiling, and memory/latency optimizations (page fetched returned only its table of contents in this pass — see Unresolved below for what wasn't captured).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/] `redis-benchmark` is the official load-testing utility, simulating N concurrent clients issuing M total requests. Key documented factors affecting Redis performance: network bandwidth/latency (often the actual bottleneck before CPU, since Redis is in-memory); CPU (Redis favors fast single-core performance over many cores, being effectively single-threaded for command execution); RAM speed (matters more for large, e.g. >10KB, objects); virtualization overhead (Redis runs measurably slower on VMs than bare metal, mostly due to `fork()` and I/O differences, not raw compute); Unix domain sockets vs. TCP loopback (up to ~50% more throughput on Linux, benefit shrinking as pipeline length grows); NUMA topology and process/core placement on multi-socket servers; and connection count (throughput roughly halves going from ~100 to ~30,000 concurrent connections, per the docs' documented rule of thumb).

- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/] The docs explicitly warn against common benchmarking misconceptions: `redis-benchmark`'s default mode uses concurrency (many connections) but **no pipelining**, so it tends to reflect worst-case rather than best-case throughput unless `-P` (pipeline depth) is explicitly set; naive synchronous busy-loop benchmarks mostly measure kernel-scheduler and client-library latency, not Redis itself.
- [Source: https://redis.io/docs/latest/develop/using-commands/pipelining/] Pipelining is presented as a primary lever for both **latency** (amortizing RTT across many commands) and **raw throughput** (up to ~10x ops/sec via fewer `read()`/`write()` syscalls and fewer user/kernel context switches).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/] For latency **diagnosis** (as opposed to raw throughput), Redis ships a built-in **Latency Monitoring** subsystem (introduced in **Redis 2.8.13**): event-tagged time series (e.g. `command`, `fast-command`, `fork`, `aof-fsync-always`, `expire-cycle`, `eviction-cycle`, etc.), enabled via `CONFIG SET latency-monitor-threshold <ms>` (disabled/0 by default though near-zero overhead), and queried via the `LATENCY` command family (`LATENCY LATEST`, `HISTORY`, `RESET`, `GRAPH`, `DOCTOR`).

[Source: https://redis.io/docs/latest/develop/reference/eviction/] `INFO stats`/`INFO memory` fields (`keyspace_hits`/`keyspace_misses`, `evicted_keys`, `expired_keys`, `used_memory_dataset`, `current_eviction_exceeded_time`, `mem_not_counted_for_evict`, per-command rejection counts in `commandstats`) are the documented instrumentation for cache-hit-ratio and eviction-policy tuning.

[Version-sensitive, Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] Redis 8.0 documents "more than 30 performance and resource utilization improvements" plus the new multi-core `io-threads` implementation and "an improved replication mechanism that is more performant and robust," but this research did not fetch a page itemizing all 30+ improvements individually.

Not documented / could not verify in the pages fetched: the `optimization/` index page itself returned only a bare table of contents with no body text in this pass (likely because it is a landing page linking to `latency`, `latency-monitor`, `benchmarks`, `memory-optimization`, and `cpu-optimization` subpages, several of which — memory-optimization and cpu-optimization specifically — were not individually fetched in this research pass). Unresolved: dedicated official memory-optimization guidance (e.g. `OBJECT ENCODING`-driven advice on compact encodings for small hashes/lists/sets) is referenced elsewhere in Redis's docs ecosystem but was not directly fetched and confirmed in this pass.

---

## 9. Testing

[Source: https://redis.io/docs/latest/develop/tools/cli/] `redis-cli` is documented as usable for scripted/ad-hoc testing: piping command files (`cat commands.txt | redis-cli`), `-r <count>`/`-i <interval>` for repeated command execution, `--pipe` for raw-protocol bulk injection, and `-x`/`-X` for feeding stdin as a command argument (useful for scripted setup/teardown in test fixtures).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/] `redis-benchmark` is the documented tool for load/performance testing against a running instance, including targeting a subset of command types (`-t set,lpush`) and custom ad-hoc commands.

[Source: https://redis.io/docs/latest/develop/tools/cli/] `redis-cli --replica` puts the CLI into a mode that logs the exact replication stream a replica would receive from a master — documented as "useful for debugging operations" and verifying that writes replicate as expected, which is adjacent to integration-testing replication behavior.

[Source: https://redis.io/docs/latest/develop/programmability/] For Lua script development/testing, `redis-cli --eval <file>` runs a script file directly, and `redis-cli --ldb` (with `--ldb-sync-mode`) launches the official **Lua debugger**, available since **Redis 3.2**.

Not documented / could not verify: this research found **no official, dedicated "testing your application against Redis" guide** (e.g. no first-party recommendation for an embedded/in-memory Redis test double, no first-party Testcontainers module, no unit-testing framework integration guide) among the pages reachable from `redis.io/docs`. Client-library-specific test guidance (e.g. `redis-py`'s or `node-redis`'s own testing recommendations) was out of scope for this pass and was not fetched. Unresolved: whether Redis or its client libraries officially endorse a specific mocking/fake-Redis approach for unit tests — not found in the pages fetched; treat any such recommendation from a skill as coming from community convention, not official Redis documentation, unless separately verified.

---

## 10. Deployment

[Source: https://redis.io/docs/latest/get-started/] Redis documents several deployment paths: source build; OS-native packages (APT, RPM, Snap, Homebrew) for Linux/macOS; Docker; Redis Cloud (managed SaaS); Redis Software (self-managed Enterprise, on-prem or cloud VM); and the Redis Enterprise Kubernetes operator.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/] **Docker**: `docker run -d --name redis -p 6379:6379 redis:<version>` is the documented minimal invocation, using the official image from Docker Hub. Custom config is supplied via a derived Dockerfile (`COPY redis.conf ...`) or a bind-mounted config directory (`-v /myredis/conf:/usr/local/etc/redis`); the mapped config directory should be **writable**, since Redis may rewrite/create additional config files depending on mode. Data persistence across container restarts requires a bind-mounted data volume (`-v /local-data/:/data`).

[Source: https://redis.io/docs/latest/operate/kubernetes/] For Kubernetes, the officially documented path is the **Redis Enterprise operator** (bringing Redis *Software*/Enterprise features — clustering, HA/auto-failover, Active-Active geo-distribution, enterprise security — onto Kubernetes via CRDs: `REC` for clusters, `REDB` for databases, `REAADB` for Active-Active databases). It targets **CNCF-conformant Kubernetes** distributions, with deployment options including a quick-start path, Helm, and an OpenShift-specific path. [Inference, not confirmed in docs] This operator packages the commercial Redis Software/Enterprise product rather than plain Redis Open Source; a bare-metal Redis Open Source Kubernetes deployment (e.g. via a community Helm chart or StatefulSet) was not documented on the official `redis.io/docs` pages fetched in this pass.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] For Redis Cluster specifically, `redis-cli --cluster create <ip:port> ... --cluster-replicas 1` is the documented cluster-bootstrap command, or the bundled `utils/create-cluster` bash script for local/dev clusters.

[Source: https://redis.io/docs/latest/get-started/] Provisioning/observability integrations documented: Pulumi and Terraform providers for Redis Cloud, and Prometheus/Grafana integration guides for both Redis Cloud and Redis Software.

Not documented / could not verify: a first-party, official "Redis Open Source on Kubernetes via plain Helm chart / Operator" page distinct from the commercial Redis Enterprise operator was not found among the pages fetched — deployment guidance for self-managed Redis Open Source on Kubernetes (as opposed to Redis Software/Enterprise) may exist elsewhere on the site or may rely on general-purpose StatefulSet patterns not specific to Redis; treat this as **Unresolved** rather than assuming no such guidance exists anywhere on the site.

---

## 11. Migration

[Source: https://redis.io/docs/latest/operate/oss_and_stack/install/upgrade/standalone/] **Upgrading a standalone instance to Redis 8**: documented supported upgrade paths are Redis Open Source 7.x (with or without modules) → Redis 8, and Redis Stack 7.2/7.4 → Redis 8. Documented procedure: `redis-cli SAVE` (or note the AOF directory) to snapshot current data, back up the data directory, stop the old server, install the new version, start it, and verify with `redis-cli INFO server | grep redis_version`; restore from backup if data is missing or the server fails to start post-upgrade. The docs explicitly recommend practicing the upgrade in a controlled environment (e.g. Docker) before touching production.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] **Upgrading nodes in a Redis Cluster**: replicas can simply be stopped and restarted on the new version; masters require a **manual failover first** (`CLUSTER FAILOVER` to promote a replica), then the now-demoted-to-replica old master is upgraded like any replica, with an optional second failover afterward to restore the original master/replica roles — done one node at a time across the cluster.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] **Migrating to Redis Cluster** from a single instance or a pre-existing custom/client-side sharding scheme: the documented, supported path depends on whether the application uses multi-key operations. Single-key-only (or same-hash-tag multi-key) workloads can migrate via: generate an AOF per source shard (`BGREWRITEAOF`), place each AOF as the initial data for one cluster node, restart nodes with those AOFs, then run `redis-cli --cluster fix` and `--cluster check` to redistribute keys to their correct hash-slot owners, finally cutting clients over to a cluster-aware client library. An alternative is `redis-cli --cluster import`, which moves (deletes-from-source) keys from a running instance into an existing cluster — noted as slow against Redis 2.8 sources specifically, due to the absence of `MIGRATE` connection caching in that version. Workloads using multi-key operations across **arbitrary, non-hash-tagged keys are explicitly not supported** by Redis Cluster and require application-level changes first.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/] **Migrating persistence mode** (RDB-only → AOF) on a live server: enable AOF via `CONFIG SET appendonly yes`, optionally disable RDB (`CONFIG SET save ""`), persist the change via `CONFIG REWRITE` (documented as a step easy to forget, causing configuration loss on the next restart), and — critically — wait for the AOF rewrite to finish (poll `INFO persistence` for `aof_rewrite_in_progress`/`aof_rewrite_scheduled` = 0 and `aof_last_bgrewrite_status` = `ok`) **before** restarting the server, or data loss can result.

[Source: https://redis.io/docs/latest/develop/clients/] For client-library migration, Redis documents a dedicated **ioredis → node-redis migration guide** (linked from the clients overview page as `redis.io/docs/latest/develop/clients/nodejs/migration`), reflecting node-redis being the currently-recommended JavaScript client over the older ioredis.

Not documented / could not verify: this research did not find an official "migrating from Memcached to Redis" or "migrating from another vendor's data store" comparison page among the pages fetched (searches surfaced only third-party comparison content, which per this project's sourcing rules is excluded as a primary citation).

---

## 12. Version information

[Source: https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/] Redis Open Source uses **MAJOR.MINOR.PATCH** versioning. Major versions (e.g. 7 → 8) may include breaking changes; minor versions (e.g. 8.2 → 8.4 → 8.6 → 8.8) add features/improvements within a major line; patch versions (e.g. 8.6.1 → 8.6.2) are bug/security fixes.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/] **Release-type/support-window policy** (as documented on the version-management page, fetched live during this research pass): **Standard releases** — the first minor in a major series (e.g. 8.0) and intermediate minors (e.g. 8.4, 8.6) — receive security fixes and critical bug fixes for **6 months after the next minor version ships**. **Extended releases** — the *second* minor in a major series (e.g. 8.2) and the *final* minor in a series — receive security fixes and critical bug fixes for **5 years** from their release date.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/] The **supported-versions table**, as published at research time (2026-09-09), lists (Version / Release type / Status / EOL date): **Redis 8.10** (Standard, GA, EOL TBD) — the current latest; **Redis 8.8** (Standard, GA, TBD); **Redis 8.6** (Standard, GA, TBD); **Redis 8.4** (Standard, GA, TBD); **Redis 8.2** (Extended, GA, EOL 2030-09-01); **Redis 8.0** (Standard, GA, EOL 2026-12-01); **Redis 7.4** (Extended, GA, EOL 2029-12-01); **Redis 7.2** (Extended, GA, EOL 2029-12-01); **Redis 6.2** (Extended, GA, EOL 2027-04-01).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] Patch history confirms active maintenance into 2026: **Redis 8.0.6** shipped **February 2026** (security fix — CRLF injection in error replies), **8.0.5** shipped **November 2025** (bug fixes), **8.0.4** shipped **October 2025** (four CVE fixes including a Lua-script RCE chain: CVE-2025-49844, -46817, -46818, -46819), **8.0.3** shipped **July 2025** (CVE-2025-32023 HyperLogLog out-of-bounds write, CVE-2025-48367), **8.0.2** shipped **May 2025** (CVE-2025-27151, `redis-check-aof` stack overflow/RCE), **8.0.0** GA shipped **May 2025**.

[Source: https://raw.githubusercontent.com/redis/redis/unstable/00-RELEASENOTES] Per the release-notes file in the `redis/redis` GitHub repo, **Redis 8.10-RC2 (v8.9.241)** and **8.10-RC1 (v8.9.240)** were both tagged around **July 20, 2026**, with the file explicitly noting "Pre-releases are not suitable for production use" — 8.10 subsequently reached GA (per the version-mgmt table above, listed as GA at research time with 8.10.1 also having shipped as a security patch per web-search corroboration; the 8.10.1 changelog itself was not independently fetched in this pass, so **Unresolved**: exact 8.10.1 release date and full changelog contents were not directly confirmed against an official page in this research pass — treat as probable-but-not-independently-fetched).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] Release cadence, stated in `version-mgmt/`: [Inference, not confirmed in docs — this specific cadence figure was reported by a WebSearch summary of `endoflife.date/redis`, a third-party tracker, not independently confirmed against an official redis.io page in this pass] "a new major version is planned for release once a year," with minor releases roughly six months after each major version. Treat this specific cadence claim as **Unresolved** pending direct confirmation from an official redis.io page, since it was surfaced via a third-party aggregator summary rather than directly read from `redis.io/docs`.

---

## 13. Breaking changes

[Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] **Redis 8.0** (May 2025) is the major version boundary most recently documented with explicit breaking-change callouts:

- **ACL category breaking change** (documented explicitly as "Potentially breaking changes to ACLs"): the `@read`, `@write`, `@dangerous`, `@admin`, `@slow`, `@fast` categories now include Redis Search/JSON/time-series/probabilistic-type commands that they previously excluded. This can **widen** access for rules like `+@read +@write` (now also grants e.g. `FT.SEARCH`, `JSON.SET`) and can **narrow** access for rules like `+@all -@write` (now also excludes e.g. `JSON.SET`). The docs direct affected users — anyone using Search/JSON/time-series/probabilistic types *and* custom ACL rules — to re-analyze their ACLs before upgrading.
- **Licensing change**: Redis Community Edition renamed to **Redis Open Source**; license changed from the prior arrangement to a **tri-license choice** (RSALv2 / SSPLv1 / AGPLv3). This is a legal/compliance-relevant breaking change for organizations with license-compatibility requirements, not a technical/API break.
- **Module consolidation**: standalone RediSearch, RedisJSON, RedisTimeSeries, and RedisBloom modules are "no longer needed as they are now part of Redis" — deployments that separately installed/loaded these modules alongside Redis 7.x need to adjust their deployment tooling for Redis 8.
- [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/] Separately, note the `acl-pubsub-default` history documented on the ACL page: it defaulted to `allchannels` through Redis 6.0, changed default behavior for **new users created under Redis 6.2** (backward-compat: existing/new users got `allchannels` by default to match 6.0 semantics), and then the default flipped to **`resetchannels`** starting in **Redis 7.0** "to provide better security" — a security-hardening default change across three different version boundaries (6.0 → 6.2 → 7.0) that could silently change Pub/Sub access for newly created ACL users depending on which version a deployment upgrades from.

[Source: https://redis.io/docs/latest/develop/programmability/] **Redis 7.0.1** changed read-only-script semantics from what shipped in 7.0.0: `PUBLISH`/`SPUBLISH`/`PFCOUNT` became treated as write commands inside scripts (they weren't before), and the `no-writes` flag started implying `allow-oom` and permitting execution during write pauses (neither was true before). This is a narrow but real behavioral break for any 7.0.0-era script relying on the old semantics.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/] **Redis 7.0** also changed ACL `+<command>|first-arg` first-argument allowlisting to **deprecated status** ("may be removed in the future"), superseded by full subcommand allow/block syntax (`+config|get`, `-config|set`).

[Source: https://redis.io/docs/latest/develop/using-commands/transactions/] **Redis 6.0.9**: prior to this version, an **expired key did not cause a `WATCH`ed transaction to abort** — a subtle correctness-relevant behavior change (transactions became more conservative/correct about expiry-driven changes from 6.0.9 onward).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/] **AOF format change at Redis 7.0.0**: the single-file AOF became a **multi-part AOF** (base file + incremental files + manifest, all under the `appenddirname` directory) — this changes how AOF backup/restore tooling must operate (see Section 5's backup-procedure documentation) and is a structural, not just behavioral, breaking change for anything that assumed a single `appendonly.aof` file.

Not documented / could not verify: this research did not fetch a single canonical "Redis N to N+1 breaking changes" page for every major version boundary (e.g. Redis 6→7 in full, or a hypothetical future 8→9) — the 8.0 release notes page was the most detailed breaking-changes source found and fetched directly; earlier major-version transitions' breaking changes were only partially reconstructed from scattered version-note callouts on feature pages (ACL, persistence, transactions) rather than one authoritative source per version.

---

## 14. Limitations

[Source: https://redis.io/docs/latest/develop/reference/protocol-spec/] **Bulk string / value size**: RESP bulk strings (and thus Redis string values generally) are limited to **512 MB by default**, governed by `proto-max-bulk-len`.

[Source: https://redis.io/docs/latest/develop/reference/eviction/] **Dataset size**: bounded by available RAM — this is a fundamental architectural property, not a configurable soft limit, since Redis is an in-memory data store (persistence/AOF/RDB provide durability, not a way to exceed RAM-sized working sets without eviction or Redis Cluster sharding).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] **Redis Cluster**: no strong consistency guarantee (documented explicitly, see Section 2); multi-key operations restricted to a single hash slot (via hash tags); not compatible with NATted/port-remapped environments including default Docker networking; a minimum of 3 master nodes required for a functioning cluster.

[Source: https://redis.io/docs/latest/develop/reference/clients/] **Client connections**: `maxclients` defaults to 10,000 and is further capped by the OS's file-descriptor soft limit (Redis reserves 32 FDs internally and will silently reduce its effective client cap below a configured `maxclients` if the OS limit is insufficient, logging a warning). The per-client **query buffer hard limit is a non-configurable 1 GB** (a safety limit against client/server bugs, not a tunable). Output-buffer limits differ by client class: normal clients default to no limit (0); Pub/Sub clients default to a 32 MB hard / 8 MB-per-60s soft limit; replica connections default to 256 MB hard / 64 MB-per-60s soft limit.

[Source: https://redis.io/docs/latest/develop/using-commands/transactions/] **Transactions have no rollback support** — Redis explicitly does not implement rollback of a `MULTI`/`EXEC` transaction on a mid-transaction command failure, citing simplicity and performance as the rationale; all queued commands still execute even if one fails.

[Source: https://redis.io/docs/latest/develop/programmability/] **Scripts/Functions block the entire server for their duration** (5-second default timeout, `busy-reply-threshold`), and once a script has performed even one write, the *only* way to recover from a runaway script is `SHUTDOWN NOSAVE` (aborting the server without persisting) — Redis will not forcibly kill a script mid-execution once it has written, to avoid leaving the dataset in a half-written state.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/] **ACL key-pattern scoping does not cover whole-database commands** (`FLUSHALL`, `FLUSHDB`, `SWAPDB`) — these must be explicitly denied per-user even when a user's key patterns are narrowly scoped, since key-pattern rules only restrict commands that take explicit key name arguments.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] **`redis-cli`'s built-in cluster support is described as "very basic"** — production applications are expected to use a cluster-aware client library that caches the hash-slot-to-node map rather than relying on redirect-following alone.

Not documented / could not verify: a single consolidated "Redis limits" reference page (analogous to, e.g., a database vendor's "maximum row size / maximum identifier length" appendix) was not found among the pages fetched in this research pass; the limits captured above were each sourced from the specific feature page documenting that limit, not from one canonical limits table.

---

## 15. Debugging

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/] The **Latency Monitoring framework** (`LATENCY LATEST`/`HISTORY`/`RESET`/`GRAPH`/`DOCTOR`, enabled via `CONFIG SET latency-monitor-threshold <ms>`) is the documented first-line tool for diagnosing latency spikes, with per-event time series covering both command execution and internal maintenance operations (fork, AOF fsync/write/rename, active defrag, expire/eviction cycles).

[Source: https://redis.io/docs/latest/develop/reference/clients/] The **`CLIENT` command family** — especially `CLIENT LIST` (per-connection state: address, fd, idle time, buffer sizes, last command, etc.) and `CLIENT KILL` — is documented as "a very powerful debugging tool if you use Redis at scale," letting an operator inspect and terminate individual problematic connections.

[Source: https://redis.io/docs/latest/develop/tools/cli/] `redis-cli` provides an extensive suite of special debugging modes:
- `MONITOR` (via `redis-cli MONITOR` or the raw command) streams every command executed against the server in real time — the docs explicitly warn this "will impact the measured performance significantly" and should not be used alongside benchmarking.
- `--latency` / `--latency-history` / `--latency-dist` measure round-trip `PING` latency against a live server, distinct from the server-side Latency Monitor.
- `--intrinsic-latency <seconds>` measures the *host system's* baseline scheduler latency (must be run on the same machine as `redis-server`, and does not connect to Redis at all) — used to establish a floor below which Redis itself cannot be blamed for latency.
- `--bigkeys` / `--memkeys` / `--keystats` scan (via `SCAN`, non-blocking) for oversized keys and per-type memory usage; `--hotkeys` finds frequently-accessed keys (requires an LFU `maxmemory-policy`).
- `--replica` mode shows the exact replication stream a replica receives, useful for debugging replication-correctness issues.
- `--rdb <file>` performs a full-sync-based remote RDB backup/transfer for inspection or disaster-recovery verification.
- `--stat` prints a rolling one-line-per-second summary of keys/memory/clients/requests for real-time monitoring.
- `--eval <file>` plus `--ldb`/`--ldb-sync-mode` run the official **Lua debugger** (available since **Redis 3.2**) against `EVAL` scripts.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/] For AOF corruption/truncation, the docs specify `redis-check-aof --fix <filename>` to repair a damaged AOF file, and describe the server's own graceful handling of a truncated (but not corrupted) AOF on startup — logging a "short read" warning and continuing when `aof-load-truncated` is enabled (the default).

[Source: https://redis.io/docs/latest/develop/reference/eviction/] `INFO` output (particularly the `stats` and `memory` sections: `keyspace_hits`/`keyspace_misses`, `evicted_keys`, `expired_keys`, `used_memory_dataset`, `current_eviction_exceeded_time`, `commandstats`) is the documented primary introspection surface for diagnosing cache-eviction and memory-pressure issues.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/replication/] The `INFO replication` section and the `ROLE` command are documented as the primary tools for inspecting live replication state (offsets, replica list, role) for debugging replication lag or split-brain suspicion.

---

## 16. Integration

[Source: https://redis.io/docs/latest/develop/clients/] Redis's primary documented integration surface is its **first-party client library set** across nine languages (enumerated in Section 3), plus **Object-Mapping (OM)** libraries for Python, C#/.NET, Node.js, and Java/Spring, and `RedisVL` (a Python library specialized for vector/AI workloads).

[Source: https://redis.io/docs/latest/get-started/] Documented **data-integration tooling**: **Redis Data Integration** (a CDC-style integration product, linked but not detailed in the pages fetched), **Redis Cloud with Amazon Bedrock** integration, and language-specific object-mapping integrations for .NET and Java/Spring specifically called out.

[Source: https://redis.io/docs/latest/get-started/] Documented **provisioning/observability integrations**: a **Pulumi provider** and a **Terraform provider** for Redis Cloud, and **Prometheus + Grafana** integration guides for both Redis Cloud and Redis Software (Enterprise) — no equivalent first-party Prometheus exporter guide specific to plain Redis Open Source was found among the pages fetched in this pass; this should be treated as **Unresolved** rather than "does not exist," since it may be documented elsewhere on the site (e.g. via the community `redis_exporter`, which is not first-party and thus wasn't pursued further under this project's official-sources-only rule).

[Source: https://redis.io/docs/latest/develop/programmability/] Redis integrates with **Lua 5.1** as its sole embedded scripting engine, and with the **Redis Modules API** for compiled C extensions (the mechanism underlying RediSearch/RedisJSON/RedisTimeSeries/RedisBloom historically, and still the documented path for community-supported modules going forward).

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/] Redis documents specific, minimal ACL rule sets required for **Sentinel** and **replica** processes to integrate correctly with an ACL-secured master — e.g. Sentinel needs `+multi +slaveof +ping +exec +subscribe +config|rewrite +role +publish +info +client|setname +client|kill +script|kill` plus `allchannels`, and replicas need only `+psync +replconf +ping` with no key access at all.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] Redis Cluster integration with client libraries requires the client to be explicitly **cluster-aware** (able to follow `-MOVED`/`-ASK` redirects and cache the slot map); `redis-cli -c` provides a minimal reference implementation of this behavior for testing purposes only.

Not documented / could not verify: this research did not fetch the dedicated `redis.io/docs/latest/integrate/` hub page in full (only saw it linked from other pages), so the complete catalog of officially documented third-party integrations (beyond Bedrock, Pulumi, Terraform, and Prometheus/Grafana, which were surfaced incidentally from the `get-started` page) was not exhaustively captured in this pass.

---

## 17. Production considerations

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/] **Persistence strategy is a first production decision**: RDB (compact point-in-time snapshots, best for backups/disaster-recovery/fast restarts, but can lose the last save-interval's writes and its `fork()` can cause brief latency spikes on large datasets), AOF (durable, tunable `fsync` policy — `always`/`everysec`/`no` — but larger on disk and can be slower depending on fsync policy), no persistence, or RDB+AOF combined. The docs' explicit recommendation: "use both persistence methods if you want a degree of data safety comparable to what PostgreSQL can provide"; RDB alone is acceptable if a few minutes of data loss is tolerable; AOF alone is explicitly discouraged ("we discourage it") because periodic RDB snapshots are still valuable for backups, fast restarts, and as a hedge against AOF-engine bugs.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/] **Backups**: RDB files are safe to copy while Redis is running (atomic rename on completion); the docs recommend a tiered retention scheme (e.g. hourly snapshots for 48 hours, daily for 1–2 months) plus off-machine/off-datacenter transfer (S3, encrypted with `gpg -c`, or SCP to a remote host) with independent monitoring/alerting for backup-transfer failures. [Version-sensitive] Since **Redis 8.10.0**, the new `BACKUP` command family provides a non-blocking, self-contained, MP-AOF-compatible backup workflow (`START`/`LIST`/`SEAL`/`STATUS`/`ABORT`/`CLEANUP`) as an alternative to manually staggering `BGREWRITEAOF`/RDB copy timing.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/replication/] **Replication safety**: persistence should be enabled on both master and replicas in production; a persistence-off master combined with auto-restart-on-crash is a documented data-loss trap (see Section 6). `min-replicas-to-write`/`min-replicas-max-lag` (since **Redis 2.8**) give a best-effort bounded-data-loss guarantee by refusing writes when too few replicas are keeping up, at the cost of write availability during replica lag.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/] **High availability**: open-source Redis needs either **Sentinel** (non-clustered HA) or **Redis Cluster** (sharded HA) explicitly configured and operated — plain standalone Redis with no Sentinel/Cluster has no automatic failover.

[Source: https://redis.io/docs/latest/develop/reference/clients/] **Client/connection tuning for scale**: `maxclients` (verify against the OS file-descriptor limit), `maxmemory-clients` (aggregate client-buffer memory cap, **off by default**, but the docs state "for any large production deployment, it is highly recommended to configure some non-zero `maxmemory-clients` value," suggesting `5%` as a starting point), per-client-class output-buffer limits (especially raising replica/Pub/Sub limits if slow consumers are expected), and TCP keepalive (on by default since **Redis 3.2**, ~300 seconds) to detect dead peers.

[Source: https://redis.io/docs/latest/develop/reference/eviction/] **Memory sizing**: when using replication or persistence, the docs recommend setting `maxmemory` to leave headroom for replication/AOF buffers, since that buffer memory is deliberately excluded from the `maxmemory` eviction calculation (to avoid a feedback loop where eviction itself generates more buffered replication traffic); `INFO memory`'s `mem_not_counted_for_evict` field quantifies this headroom need.

[Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/] Production sizing guidance from the official tutorial: keep individual shards under roughly **25 GB or 25K ops/sec** as a conservative starting point for deciding when to shard (up to ~50 GB tolerable at a lower ops/sec rate); route client connections through a **proxy** rather than direct-to-instance in high-connection-churn environments to avoid reconnect-flood-induced failovers.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/] **Production security posture**: never expose the Redis port directly to untrusted networks; rely on `bind`, firewalling, protected mode (automatic since 3.2.0 under default+no-password config), ACLs (Redis 6+) over legacy `requirepass`, and TLS for any traffic crossing an untrusted network segment; run the server process as an unprivileged OS user.

[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/] **Hardware/topology considerations for production capacity planning**: prefer fast single-core CPU performance over core count (single-threaded command execution); prefer bare metal over virtualized instances where latency-sensitive; size network bandwidth against expected payload×throughput (the docs' own example: 4 KB values at 100K ops/sec ≈ 3.2 Gbit/s, exceeding a 1 Gbit/s link); watch connection count, since very high connection counts materially reduce achievable throughput per the documented rule of thumb (~2x reduction going from ~100 to ~30,000 connections).

---

## Summary of version-sensitive facts worth tracking

| Version / range | Fact |
|---|---|
| Redis 1.2 | RESP protocol first (optional) support |
| Redis 2.0 | RESP2 becomes the standard client protocol |
| Redis 2.2 | `WATCH`-based optimistic locking (CAS) introduced |
| Redis 2.4 | Automatic AOF rewrite triggering; avoids concurrent AOF-rewrite + RDB-save disk I/O contention |
| Redis 2.6 | `EVAL`/Lua scripting introduced; `maxclients` becomes configurable (default 10,000); client-handling docs apply "only to Redis 2.6+" |
| Redis 2.6.5 | Server detects command-queueing errors before `EXEC`, refuses to run the transaction |
| Redis 2.8 | `min-replicas-to-write`/`min-replicas-max-lag` bounded-data-loss write guard |
| Redis 2.8.13 | Latency Monitoring subsystem introduced |
| Redis 2.8.18 | Diskless replication introduced |
| Redis 3.2 | Protected mode auto-enables on default+no-password config; TCP keepalive on by default (~300s); Lua debugger (`--ldb`) added to `redis-cli` |
| Redis 3.2.2 | `replica-announce-ip`/`replica-announce-port` for NAT/Docker replication topologies |
| Redis 4.0 | Sub-replicas in a chain receive an identical stream from the top-level master; writable replicas gain TTL-eviction parity with masters (except DBs >63); client name shown in `SLOWLOG`; partial resync survives failover-promotion |
| Redis 5 | Project stops using "slave" terminology (except where baked into `CLUSTER NODES` wire format) |
| Redis 6 | ACLs introduced (replacing single-password model as the recommended auth mechanism); default-config behavior remains backward compatible with pre-ACL Redis |
| Redis 6.0 | RESP3 experimental opt-in support (via `HELLO`), excluding streaming types |
| Redis 6.0.9 | Expired keys now correctly abort a `WATCH`ed transaction (previously did not) |
| Redis 6.2 | ACL Pub/Sub channel permissions (`&<pattern>`) introduced; new ACL users default to `allchannels` for 6.0 backward compatibility |
| Redis 7.0 | Redis Functions introduced (first-class, decoupled scripts); ACL subcommand-level allow/block (`+config\|get`); ACL selectors and `%R~`/`%W~` key-permission patterns; read-only script commands (`EVAL_RO` etc.); client eviction (`maxmemory-clients`) introduced; multi-part AOF format; `acl-pubsub-default` flips to `resetchannels`; writable-replica legacy use cases declared obsolete; all core commands invocable under both RESP2 and RESP3 |
| Redis 7.0.1 | Read-only-script semantics tightened: `PUBLISH`/`SPUBLISH`/`PFCOUNT` now count as writes in scripts; `no-writes` now implies `allow-oom` and permits execution during write pauses |
| Redis 7.2 and earlier | BSD-3-Clause license |
| Redis 7.4 / 7.2 | RSALv2/SSPLv1 dual-license (no AGPL option); both are "Extended" releases, EOL 2029-12-01 |
| Redis 8.0 (May 2025) | Renamed Community Edition → **Redis Open Source**; tri-license (RSALv2/SSPLv1/AGPLv3); Search/JSON/Time-series/probabilistic types become bundled-in (not separate modules); **breaking ACL-category widening/narrowing** for `@read`/`@write`/etc.; new `io-threads` multi-core I/O; Vector sets introduced (preview); new hash commands `HGETDEL`/`HGETEX`/`HSETEX`; EOL 2026-12-01 |
| Redis 8.2 | "Extended" release, EOL 2030-09-01 |
| Redis 8.4 | New atomic `SET ... IFEQ/IFNE/IFDEQ/IFDNE` and `DELEX` compare-and-set/delete commands for strings |
| Redis 8.6 | LRM (Least Recently Modified) eviction policy introduced |
| Redis 8.8 | `ACL LOAD` allows `#`-comment lines in external ACL files; `redis-cli` gains word-jump line editing |
| Redis 8.10.0 | New online `BACKUP` command family (`BACKUP START`/`LIST`/`SEAL`/`STATUS`/`ABORT`/`CLEANUP`) and `preload-file` startup restore option |
| Redis 8.10 (current, GA at research time 2026-09-09) | Latest "Standard" release per the official supported-versions table; EOL not yet set (TBD) |

---

## Unresolved items (surfaced explicitly, not papered over)

- Exact quorum/failover mechanics of **Redis Sentinel** — the Sentinel page (`redis.io/docs/latest/operate/oss_and_stack/management/sentinel/`) was fetched but its body exceeded this pass's capture size; only its table of contents and the fact that it exists/covers "Sentinel as a distributed system," quorum-adjacent config, and a full API were confirmed. A future pass should re-fetch this page in full or in sections.
- The precise scope of what Redis 8.0's new **`io-threads`** implementation parallelizes (network I/O only, or more) was not confirmed beyond the one-line release-note description.
- Whether an official, first-party "testing your app against Redis" guide (embedded/fake Redis, Testcontainers module, etc.) exists anywhere on `redis.io/docs` — none was found among pages reached in this pass, but the site was not exhaustively crawled.
- Whether an official Kubernetes deployment path exists for plain **Redis Open Source** (as distinct from the commercial Redis Enterprise/Software operator, which is the only Kubernetes deployment path documented and fetched in this pass).
- The exact release-cadence claim ("new major version once a year, minors ~6 months apart") was sourced via a WebSearch summary of a third-party tracker (`endoflife.date`), not independently confirmed by directly reading an official redis.io page in this pass.
- Full changelog contents and exact release date for **Redis 8.10.1** (referenced by a WebSearch summary as a security patch) were not independently fetched from an official page.
- The complete "Other security topics" subsection referenced at the bottom of the main security page (`redis.io/docs/latest/operate/oss_and_stack/management/security/`) was not individually followed to its linked subpages.
- Dedicated official memory-optimization and CPU-optimization guidance pages (linked from the `optimization/` index) were not fetched in this pass — only latency-monitoring and benchmarking subpages were captured in full.
