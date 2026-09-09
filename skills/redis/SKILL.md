---
name: Redis
description: >-
  Redis-specific data structures, eviction policies, TTL/key expiration,
  pipelining, transactions (MULTI/EXEC/WATCH), pub/sub, Cluster sharding,
  Sentinel HA, ACLs, and the Redis 8.0 licensing/module-bundling change. Use
  when the stack uses Redis (redis:// URL, a Redis client library, or the
  task names caching/pub-sub/search/vector work backed by Redis). Not for
  generic caching strategy, realtime-transport choice, or search-engine
  choice made independent of Redis.
spec_version: "1.0"
---

## Purpose & scope

Redis is genuinely multi-role: an in-memory data store used as a **cache**, a
**pub/sub message broker**, a **full-text/vector search** engine, and a
general-purpose **in-memory data-structure server** — the docs' own framing
is "a cache, vector database, document database, streaming engine, and
message broker" [Source: https://redis.io/docs/latest/get-started/]. This
skill applies Redis correctly and version-appropriately across whichever of
those roles the task actually needs: eviction/TTL design for caching,
MULTI/EXEC/pub-sub for messaging, RediSearch/vector sets for search, and
Cluster/Sentinel for scaling and HA. The *method* for deciding whether
caching, a pub/sub transport, or a search architecture is the right answer at
all belongs to the parent Layer-3 skills — `SK-DATA-004` (caching-strategy),
`SK-BE-004` (realtime-communication), and `SK-DATA-005` (search-integration).
All three are **forward references, not yet authored anywhere in this
library**, so this skill stays self-contained and comprehensive on Redis's
own facts rather than assuming depth it can't yet borrow from them.
[data-modeling](../data-modeling/SKILL.md) (`SK-DATA-001`) is related only
for basic key-design framing, not a formal parent.

## When to use / When not to use

**Use** when a `redis://`/`rediss://` connection string or a Redis client
library (`redis-py`, `ioredis`, `node-redis`, Jedis, Lettuce, `go-redis`,
`StackExchange.Redis`, `hiredis`, `redis-rs`, `redis-rb`) is present, or the
task names Redis or a Redis-specific feature (`MULTI`/`EXEC`/`WATCH`,
pub/sub, Redis Cluster, Sentinel, RDB/AOF, `ACL SETUSER`, `FT.SEARCH`, vector
sets). **Do not use** when no Redis dependency exists and the question is
still an open store-shape/cache-layer choice (route to `SK-DATA-001`, or
`SK-DATA-004` once authored), when the question is realtime-transport
selection independent of Redis (WebSocket vs. WebRTC vs. SSE — route to
`SK-BE-004` once authored), or when the question is search-engine selection
independent of Redis (Redis vs. OpenSearch vs. Postgres FTS — route to
`SK-DATA-005` once authored).

## Knowledge

**Architecture.** Redis is fundamentally an **in-memory** system — dataset
size is bounded by available RAM; this is an architectural property, not a
soft limit [Source: https://redis.io/docs/latest/develop/reference/eviction/].
Command execution is documented as **single-threaded** ("Finally, Redis is
single threaded"), which the docs frame as advantageous for per-core
throughput and predictable latency
[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/].
**[Version-sensitive, >=8.0]** Redis 8.0 introduced a new I/O threading
implementation (`io-threads`) that increases throughput on multi-core
environments — command-execution logic itself remains single-threaded, but
I/O handling has become more parallel. The exact scope of what `io-threads`
parallelizes is Unresolved beyond this one-line release-note description
[Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/].

**Data model as architecture, not just a use-case.** Redis documents twelve
core data types (Strings/Bitmaps/Bitfields, Arrays, Geospatial indexes,
Hashes, JSON, Lists, Probabilistic types, Sets, Sorted sets, Streams, Time
series, Vector sets)
[Source: https://redis.io/docs/latest/develop/data-types/]. **[Version-sensitive,
>=8.0]** JSON, Time series, and the five probabilistic types (Bloom, Cuckoo,
Count-min sketch, Top-K, t-digest) — previously separate "Redis Stack"
modules — became bundled parts of core Redis as of 8.0, along with Redis
Search; Vector sets were introduced as a **preview** feature in 8.0.0,
supporting HNSW indexing, cosine-similarity queries, and native hybrid search
(vector similarity + structured filters)
[Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/].
Choosing the right type for the access pattern (opaque string vs. `HASH` vs.
native JSON; `SET`/sorted-set as a reverse index) materially changes what's
possible later — see
[references/data-structure-selection.md](references/data-structure-selection.md)
for the full type-by-type table; geospatial and list/stream command-level
detail beyond their listing as core types is Not documented / could not
verify in this research pass — verify exact command syntax against current
docs.

**Eviction policies.** For cache-style workloads, `maxmemory-policy` governs
eviction: `allkeys-lru` is the general-purpose default (assuming a subset of
keys dominates access), `allkeys-random` fits roughly-uniform access,
`volatile-ttl` fits workloads where the application can predict good
eviction candidates and assigns them short TTLs, and **[Version-sensitive,
>=8.6]** `allkeys-lrm` (Least Recently Modified) distinguishes "read-heavy
but rarely written" data
[Source: https://redis.io/docs/latest/develop/reference/eviction/]. Sample
size (`maxmemory-samples`, default 5) and LFU tuning (`lfu-log-factor`,
`lfu-decay-time`) refine the approximation
[Source: https://redis.io/docs/latest/develop/reference/eviction/].

**TTL / key expiration.** Caching keys without a TTL is a documented **High**
severity anti-pattern — it leads to unbounded memory growth and eviction
storms [Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/].
`volatile-ttl` eviction leans directly on assigning short TTLs to keys the
application already knows are good eviction candidates
[Source: https://redis.io/docs/latest/develop/reference/eviction/].

**Pipelining.** Batching multiple commands into one write and reading
replies afterward is the documented way to reduce round-trip overhead — the
docs show up to a **10x** increase in ops/sec, and roughly 5x wall-clock
improvement even over a low-RTT loopback interface. Batch in bounded chunks
(the docs' example: ~10k commands) rather than unboundedly, since the server
queues all replies in memory while pipelining
[Source: https://redis.io/docs/latest/develop/using-commands/pipelining/].

**Transactions.** `MULTI`/`EXEC`/`DISCARD`/`WATCH` queue commands to execute
sequentially and atomically as one isolated step; `WATCH` adds
optimistic-locking (check-and-set) semantics — documented pattern: `WATCH
key` → read → `MULTI` → writes → `EXEC`, retrying on a nil `EXEC` reply
[Source: https://redis.io/docs/latest/develop/using-commands/transactions/].
**Redis has no transaction rollback**: if one queued command fails mid-`MULTI`/`EXEC`,
the rest still execute — a documented, deliberate simplicity/performance
trade-off, not a bug
[Source: https://redis.io/docs/latest/develop/using-commands/transactions/].
**[Version-sensitive, >=8.4]** `SET` gained `IFEQ`/`IFNE`/`IFDEQ`/`IFDNE`
options and a new `DELEX` command, giving atomic single-command compare-and-set
/ compare-and-delete for strings as a simpler alternative to `WATCH`/`MULTI`/`EXEC`
for that specific case
[Source: https://redis.io/docs/latest/develop/programmability/].

**Programmability.** Server-side logic runs via a sandboxed, embedded Lua 5.1
interpreter (`EVAL`/`EVALSHA`, since 2.6.0), or, **[Version-sensitive,
>=7.0]**, via Redis **Functions** (`FUNCTION LOAD`, `FCALL`) — first-class,
independently deployable script objects decoupled from application code
[Source: https://redis.io/docs/latest/develop/programmability/]. For
read-then-write logic needing minimal latency, the docs recommend scripting
over pipelining, since pipelining alone can't let a client react to a read's
result before issuing the dependent write
[Source: https://redis.io/docs/latest/develop/programmability/]. Read-only
scripts (`EVAL_RO`/`EVALSHA_RO`/`FCALL_RO`, or the `no-writes` flag) can
always run on replicas and are always killable via `SCRIPT KILL`
[Source: https://redis.io/docs/latest/develop/programmability/]. **Scripts
block the entire server** for their duration (5-second default
`busy-reply-threshold`), and once a script has performed a write, the only
recovery from a runaway script is `SHUTDOWN NOSAVE`
[Source: https://redis.io/docs/latest/develop/programmability/].

**Pub/sub.** Redis's own description names "message broker" as one of its
headline roles [Source: https://redis.io/docs/latest/get-started/]. Detailed
Pub/Sub delivery-semantics documentation (exact `PUBLISH`/`SUBSCRIBE`
guarantees) was **not fetched in this research pass** — verify current
delivery-guarantee behavior against current docs before relying on it for a
messaging design. What is documented: Pub/Sub channel access is ACL-scoped
via `&<pattern>` (**6.2+**), the `acl-pubsub-default` setting governs new
users' default channel access, and Pub/Sub client connections have their own
idle-timeout exemption and output-buffer defaults (32 MB hard / 8 MB-per-60s
soft) distinct from normal clients
[Source: https://redis.io/docs/latest/develop/reference/clients/];
[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/].

**Replication & scaling.** Base HA is **leader-follower (master-replica)
replication**, asynchronous by default; `WAIT` can request stronger
synchronous behavior for specific writes but does not make Redis a CP system
[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/replication/].
**Redis Cluster** shards data across nodes using **16384 hash slots**
(`CRC16(key) mod 16384`, not consistent hashing); every node needs a client
port plus a cluster bus port (client port + 10000). Multi-key operations
require all keys in one hash slot, enforced via hash tags (`{...}`)
[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/].
**[Version-sensitive]** A minimal working cluster requires **at least 3
master nodes**; production deployments are recommended to use **6 nodes (3
masters + 3 replicas)**
[Source: research/knowledge-maps/version-matrix.md; https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/].
Redis Cluster does **not guarantee strong consistency** (async replication +
a partition-timeout write window can both lose acknowledged writes) and does
**not** support NATted/port-remapped environments including default Docker
networking [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/].
**Sentinel** provides HA for **non-clustered** Redis via monitoring, failure
detection, and automatic failover
[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/].

**Persistence.** RDB (compact snapshots, best for backup/fast restart, can
lose the last save-interval's writes) vs. AOF (durable, tunable `fsync`
policy, larger on disk) vs. both. The docs' explicit recommendation: use
both "if you want a degree of data safety comparable to what PostgreSQL can
provide"; AOF alone is explicitly discouraged
[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/].
**[Version-sensitive, >=8.10.0]** A new `BACKUP` command family
(`START`/`LIST`/`SEAL`/`STATUS`/`ABORT`/`CLEANUP`) provides a non-blocking,
self-contained online backup workflow
[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/].

## Decision framework

1. **Which Redis role does this task actually need?** Not every Redis use
   needs every role — cache-only needs TTL + eviction policy, not
   `MULTI`/`EXEC` or search; a pub/sub need doesn't require persistence
   tuning; a search/vector need requires confirming RediSearch/vector sets
   are actually bundled at the deployment's version (`>=8.0`). Naming the
   role first prevents pulling in irrelevant complexity.
2. **Eviction policy (cache role):** `allkeys-lru` as the general-purpose
   default; `allkeys-lrm` (**8.6+**) when distinguishing read-heavy/rarely-written
   data; `allkeys-random` for roughly-uniform access; `volatile-ttl` when the
   application can predict good eviction candidates and assign them short
   TTLs. Don't default to `allkeys-lru` without checking whether the access
   pattern actually matches its Pareto assumption.
3. **In-Redis search/vector vs. a dedicated engine:** bundled RediSearch/JSON
   (**8.0+**) or preview vector sets (**8.0.0+**) can suffice for moderate
   full-text/vector needs without operating a second system. Escalate to a
   dedicated search engine (`SK-DATA-005`, forward reference) only once
   relevance-tuning, scale, or vector-sets' preview-status risk exceeds what
   Redis's own search features support — don't add a second engine "in
   case."
4. **Single instance vs. Sentinel vs. Cluster (anti-overengineering):** a
   single instance is correct until the dataset or throughput genuinely
   exceeds it — the documented starting-point sizing rule is keeping a shard
   under **~25 GB or ~25K ops/sec**. Add Sentinel when automatic failover
   for a non-clustered deployment is needed. Add Redis Cluster only once a
   single instance (even with Sentinel) is verified insufficient — Cluster
   brings real complexity (hash-slot/hash-tag design, no strong consistency,
   a hard minimum of 3 master nodes, no default NAT/Docker networking
   support) that isn't worth paying for "to be safe."
5. **Version gate:** confirm the Redis major version before recommending a
   version-gated feature — `>=6.0` for ACLs, `>=7.0` for ACL subcommand/key-pattern
   scoping and Functions, `>=8.0` for bundled Search/JSON/time-series/probabilistic
   types, the licensing/naming change, and the ACL category-widening breaking
   change. State the version the guidance targets rather than assuming
   "latest" (rule VA-3).

## Workflow

1. Confirm which Redis role(s) the task needs and the Redis major version in
   use — both gate almost everything downstream.
2. For a cache task: define the key schema and TTLs, pick an eviction policy
   per the decision framework, and verify via `INFO stats`
   (`keyspace_hits`/`keyspace_misses`, `evicted_keys`) once implemented.
3. For a messaging, search, or data-structure task, apply the role-specific
   facts from Knowledge and, for search/vector, confirm the deployment's
   version actually bundles the needed feature (`>=8.0`).
4. For any multi-command sequence, prefer pipelining (or a Function/script
   only if a read must drive a dependent write) over serial round-trips.
5. Only escalate to Sentinel or Cluster per the decision framework; if
   Cluster, design hash tags for any multi-key operation up front, since
   Redis Cluster does not support arbitrary cross-slot multi-key operations.
6. For an upgrade crossing the Redis 8.0 boundary with existing ACL rules,
   re-analyze the category-widening impact before upgrading (see Security).
7. Verify against the checks below before declaring done.

## Engineering rules

- Always set a TTL on cache keys — caching without TTL is a documented
  **High**-severity anti-pattern (unbounded growth, eviction storms).
- Use `SCAN` (or Redis Search) for keyspace iteration in production; never
  `KEYS` — it's an O(N) scan that blocks the single-threaded server for its
  duration [Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/].
- Batch multi-command sequences with pipelining in bounded chunks (~10k
  commands) rather than serial round-trips.
- At scale, connect through a proxy rather than directly to Redis instances,
  to avoid reconnect-flood-induced failover storms.
- Run an odd number of shards/replicas (primary + at least 2 replicas) in
  open-source Redis to avoid split-brain risk during partitions.
- Never combine a persistence-off master with auto-restart-on-crash in a
  replicated setup — a crashed, auto-restarted master comes back empty and
  replicas will replicate that emptiness.
- Never store a JSON document as an opaque string if partial or atomic
  field-level access is needed — use `HASH` or the native JSON type instead.
- State the Redis version any piece of guidance targets; never assume
  "latest" silently (rule VA-3), especially across the 8.0 boundary.

## Trade-offs

- `allkeys-lru` is simple and generally effective but its LRU/LFU
  approximation is sample-based (`maxmemory-samples`, default 5); `volatile-ttl`
  gives the application precise control at the cost of requiring it to assign
  good TTLs itself.
- Redis Cluster buys horizontal scale and sharded HA but costs real
  operational complexity (hash-slot/hash-tag design, no strong consistency,
  a 3-master floor, no default NAT/Docker support) — a Sentinel-backed
  single dataset is simpler whenever the data actually fits one node.
- AOF buys durability at the cost of write latency (depending on `fsync`
  policy) and disk size vs. RDB's compact-but-lossier snapshots; the
  documented recommendation to run both trades operational simplicity for
  PostgreSQL-comparable durability.
- Lua scripting/Functions give atomic read-compute-write at the cost of
  blocking the single-threaded server for the script's duration, with an
  unrecoverable-except-by-`SHUTDOWN NOSAVE` failure mode once a script has
  performed a write.

## Anti-patterns

- **Reaching for Redis Cluster before a single instance (optionally with
  Sentinel) is verified insufficient** — the added hash-slot/hash-tag
  complexity and consistency trade-offs aren't worth paying for "to be
  safe." This is the domain's over-engineering trap (Decision framework §4).
- **Using `KEYS` in application code** (**High** severity) — an O(N)
  full-keyspace scan that blocks the single-threaded server for its
  duration; use `SCAN` or Redis Search instead
  [Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/].
- **Caching keys without a TTL** (**High**) — unbounded memory growth and
  eviction storms.
- **Connecting directly to Redis instances without a proxy** at scale
  (**High**) — a reconnect flood after a network hiccup can overwhelm the
  single-threaded process and force an unnecessary failover.
- **Running ephemeral Redis (no persistence, no HA) as a primary database**
  (**High**) — a restart means total data loss.
- **Storing JSON blobs as opaque strings** (**Medium**) — forces full
  deserialize/reserialize on every read/update and precludes atomic
  field-level updates.
- **Using `SELECT`/multiple numbered databases inside one Redis instance**,
  especially in microservice architectures — attributed to Redis's creator
  as an anti-pattern; use a dedicated instance per logical database instead.
- **A persistence-off master combined with auto-restart-on-crash** in a
  replicated setup — replicas replicate the resulting emptiness.

(All anti-patterns above are documented in the official Redis tutorial
[Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/]
except the last, which is documented on the replication page
[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/replication/].)

## Security

- Redis's documented security model: designed for **trusted clients inside
  trusted environments** — not for direct exposure to untrusted networks;
  untrusted access must be mediated by an application layer implementing its
  own ACLs and input validation
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/].
- Bind to a trusted interface (`bind 127.0.0.1`) and firewall the port — a
  single unauthenticated `FLUSHALL` can wipe the whole dataset. Protected
  mode auto-enables since **3.2.0** under default-config-plus-no-password
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/].
- **ACLs** (**Redis 6+**) are the recommended auth mechanism over legacy
  `requirepass`. Rule syntax: `+`/`-<command>` (subcommand allow/block via
  `|`, **7.0+**), `+`/`-@<category>` (29 documented categories), `~`/`%R~`/`%W~`
  key-pattern scoping (**7.0+**), `&<pattern>` Pub/Sub channel scoping
  (**6.2+**), and selectors (**7.0+**). Passwords are SHA-256 hashed
  server-side; `ACL GENPASS` generates a random 256-bit password
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/].
- **Key-pattern restrictions do not cover whole-keyspace commands**
  (`FLUSHALL`/`FLUSHDB`/`SWAPDB`) — these must be explicitly denied even for
  a user scoped to a narrow key pattern
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/].
- **[Version-sensitive, breaking change, >=8.0]** The `@read`/`@write`/`@dangerous`/`@admin`/`@slow`/`@fast`
  ACL categories now include Redis Search, JSON, time-series, and
  probabilistic-type commands — previously they did not. This **silently
  widens** rules like `+@read` (now also grants `FT.SEARCH`) and can
  **narrow** rules like `+@all -@write` (now also excludes `JSON.SET`).
  Existing ACL rules require re-analysis before upgrading to 8.0
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/];
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/].
- **[Version-sensitive]** `acl-pubsub-default` defaulted to `allchannels`
  through **6.0** (and for users created under **6.2**, for backward
  compatibility), then flipped to `resetchannels` starting in **7.0** "to
  provide better security" — a default change spanning three version
  boundaries that can silently change Pub/Sub access for newly created ACL
  users depending on upgrade path
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/].
- **[Version-sensitive, >=8.0]** "Redis Community Edition" was renamed
  **"Redis Open Source"** and the license changed from the prior
  BSD-3-Clause/dual-license arrangement to a **tri-license choice**
  (RSALv2, SSPLv1, or AGPLv3). Versions 7.4/7.2 remain RSALv2/SSPLv1 only
  (no AGPL option); 7.2 and earlier were BSD-3-Clause. This is a
  legal/compliance-relevant change, not a technical one, but affects which
  Redis version/license an organization can adopt
  [Source: research/knowledge-maps/version-matrix.md; https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/].
- **TLS** is optional across client connections, replication links, and the
  Cluster bus protocol — enable it for any traffic crossing an untrusted
  network segment
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/].
- `rename-command` (hiding/disabling commands) is deprecated and may be
  removed; ACL rules are the documented replacement
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/security/].
- For the full cross-cutting threat model (injection defense in depth,
  secrets handling, transport security beyond TLS config), defer to
  `SK-QA-002` — not restated here (no-duplication rule QR-2).

## Performance

- **Pipelining** is the primary lever for both latency and raw throughput —
  up to ~10x ops/sec via fewer syscalls and context switches
  [Source: https://redis.io/docs/latest/develop/using-commands/pipelining/].
- **Eviction-policy tuning:** `allkeys-lru` default; `allkeys-lrm` (**8.6+**)
  for read-heavy/rarely-written data; `allkeys-random` for uniform access;
  `volatile-ttl` when good eviction candidates are predictable. Tune sample
  size and LFU decay via `maxmemory-samples`/`lfu-log-factor`/`lfu-decay-time`
  [Source: https://redis.io/docs/latest/develop/reference/eviction/].
- **Cluster sharding** scales throughput/dataset size beyond a single node's
  RAM ceiling — but only once a single instance (or Sentinel-backed single
  instance) is verified insufficient, per the Decision framework and the
  over-engineering anti-pattern above.
- `redis-benchmark` is the official load-testing tool; its default mode uses
  concurrency but **no pipelining**, so it tends to reflect worst-case
  throughput unless `-P` (pipeline depth) is set explicitly
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/].
  The built-in **Latency Monitoring** subsystem (`LATENCY LATEST`/`HISTORY`/`GRAPH`/`DOCTOR`,
  enabled via `CONFIG SET latency-monitor-threshold <ms>`) is the documented
  first-line tool for diagnosing latency spikes
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/].
- Network bandwidth/latency is often the actual bottleneck for an in-memory
  system; prefer fast single-core CPU over core count for command execution;
  prefer bare metal over VMs for latency-sensitive workloads; throughput
  roughly halves going from ~100 to ~30,000 concurrent connections
  [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/].
- `INFO stats`/`INFO memory` fields (`keyspace_hits`/`keyspace_misses`,
  `evicted_keys`, `expired_keys`, `used_memory_dataset`) are the documented
  instrumentation for cache-hit-ratio and eviction-policy tuning
  [Source: https://redis.io/docs/latest/develop/reference/eviction/].

## Testing

**Documented gap:** this research found **no official, dedicated "testing
your application against Redis" guide** — no first-party embedded/in-memory
test double, no first-party Testcontainers module, no unit-testing framework
integration guide among the pages reachable from `redis.io/docs`
[Source: https://redis.io/docs/latest/develop/tools/cli/; Unresolved]. What
*is* documented: `redis-cli` supports scripted/ad-hoc testing (piping
command files, `--pipe` for raw-protocol injection, `-x`/`-X` for stdin-fed
command arguments), `redis-benchmark` for load testing, and the Lua debugger
(`--eval`, `--ldb`/`--ldb-sync-mode`, since **3.2**) for testing scripts
specifically
[Source: https://redis.io/docs/latest/develop/tools/cli/]. Treat any
mocking/fake-Redis recommendation as community convention, not official
Redis guidance, unless separately verified. Deep test-strategy method is
owned by `SK-QA-001` — not restated here.

## Failure handling

- If the Redis role needed (cache / pub-sub / search-vector / general
  data-structure store) is unclear, ask rather than assuming cache — the
  wrong assumption produces materially wrong guidance given Redis's
  multi-role nature.
- If the Redis major version cannot be determined, ask for it or explicitly
  state the version the guidance assumes — never assume "latest" silently
  (rule VA-3); flag the 8.0 boundary specifically (licensing, module
  bundling, ACL category widening) since it changes both legal and security
  posture.
- If shell is unavailable or denied, degrade to advisory `redis.conf`/ACL/command
  output and state that nothing was actually run against a live instance.

## Escalation

- Adopting Redis Cluster (rather than a single instance, or a single
  instance plus Sentinel) is confirmed with the user before being treated as
  decided — it is a materially more complex, harder-to-reverse operational
  commitment (see Anti-patterns).
- Upgrading a deployment across the Redis 8.0 boundary while custom ACL
  rules exist is flagged for explicit user re-analysis of those rules before
  the upgrade proceeds, per the documented breaking change.
- A licensing choice among RSALv2/SSPLv1/AGPLv3 (**8.0+**) affecting
  legal/compliance posture is presented with trade-offs for user
  confirmation, not decided silently.

## Outputs & verification

- **Outputs:** a data-structure/key-design recommendation with TTL/eviction
  rationale; `redis.conf`/ACL/command changes implementing the design;
  role/topology/security analysis with version scope; CLI commands actually
  run (`redis-cli`, `CONFIG SET`, Cluster bootstrap) when shell is available.
- **Verify:** the recommended role matches the stated need, not defaulted to
  "cache"; the eviction/TTL choice is justified against the access pattern;
  every version-specific claim is tagged with the range it holds for; a
  Cluster recommendation is justified against an actual RAM/throughput need
  with the minimum-3-master topology stated; `FLUSHALL`/`FLUSHDB`/`SWAPDB`
  are explicitly denied for any key-pattern-scoped ACL user.

## References

- [references/data-structure-selection.md](references/data-structure-selection.md)
  — Tier-2 table of Redis's documented data types by access pattern.
- Source list: see `skill.yaml.source_references` (Redis official docs,
  retrieved 2026-09-09, via `research/technologies/redis.md`; plus
  `research/knowledge-maps/version-matrix.md` and
  `research/knowledge-maps/concept-knowledge-map.md`).
- [research/technologies/redis.md](../../research/technologies/redis.md) —
  full primary research, including limits, breaking changes, migration
  guidance, and unresolved items.
