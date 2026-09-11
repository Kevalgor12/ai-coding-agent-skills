---
name: MongoDB
description: >-
  MongoDB-specific document modeling (embedding vs. referencing), aggregation
  pipeline, sharding, the ESR indexing rule, multi-document transactions, and
  RBAC/field-level encryption. Use when the stack uses MongoDB
  (mongodb://+mongodb+srv:// URI, an official MongoDB driver, Mongoose/another
  ODM, or the task names MongoDB). Not for generic schema design
  (data-modeling), ODM usage mechanics (orm-integration/mongoose), or other
  database engines (postgresql/mysql).
spec_version: "1.0"
---

## Purpose & scope

Apply MongoDB correctly and version-appropriately: document schema design
(embedding vs. referencing), the aggregation pipeline, sharding and
replication, ESR-rule indexing, transactions, and security/deployment
specifics. This skill specializes [data-modeling](../data-modeling/SKILL.md)
(SK-DATA-001) with MongoDB's concrete API and does not repeat its generic
store-shape/entity-relationship method. It does not cover ODM/driver usage
mechanics ([orm-integration](../orm-integration/SKILL.md), SK-TECH-mongoose)
or full-text/vector search integration depth
([search-integration](../search-integration/SKILL.md), SK-DATA-005 —
referenced, not restated, here).

## When to use / When not to use

**Use** when the stack has a `mongodb://`/`mongodb+srv://` connection string,
an official MongoDB driver, Mongoose or another ODM, or when the task names
MongoDB or a MongoDB-specific concept (aggregation pipeline, sharding,
WiredTiger, replica set, `$lookup`, BSON). **Do not use** when the store
engine is PostgreSQL/MySQL/another engine (route to that skill), when the
store-shape decision itself is still open (route to
[data-modeling](../data-modeling/SKILL.md)), or when the question is purely
about ODM/driver mechanics with MongoDB already decided (route to
orm-integration or the Mongoose skill).

## Knowledge

**Document model.** A document is BSON — field/value pairs, max 16 MiB, max
100 levels of nesting — and every document requires a unique `_id` (always
first field, auto-`ObjectId` if unsupplied, any type except array/regex)
[Source: https://www.mongodb.com/docs/manual/core/document/]. As of MongoDB
5.0, field names may contain dots and dollar signs with restrictions
(subfields still cannot begin with `$`) [Source:
https://www.mongodb.com/docs/manual/core/document/]. Collections group
documents; MongoDB's data model is designed to mirror application object
models and avoid an ORM layer entirely [Source:
https://www.mongodb.com/docs/manual/core/document/]. The CRUD API
(`insertOne`/`insertMany`, `find`, `updateOne`/`updateMany`/`replaceOne`,
`deleteOne`/`deleteMany`) is atomic only at the single-document level
[Source: https://www.mongodb.com/docs/manual/crud/].

**Aggregation pipeline.** Multi-document analytics run through a pipeline of
stages (`$match`, `$group`, `$unwind`, `$sort`, `$limit`, `$lookup`,
`$filter`, `$merge`, `$out`, …), each stage's output feeding the next
[Source: https://www.mongodb.com/docs/manual/aggregation/]. Default per-stage
memory limit is 100 MB; `allowDiskUse` permits spilling to disk. Pipelines
are read-only unless they end in `$merge`/`$out`. Max 1,000 pipeline stages;
only `$bucket`, `$bucketAuto`, `$group`, `$setWindowFields`, `$sort`, and
`$sortByCount` can spill to disk (gated by `allowDiskUseByDefault`) [Source:
https://www.mongodb.com/docs/manual/reference/limits/].

**Sharding.** A sharded cluster has shards (each its own replica set),
config servers (a Config Server Replica Set), and `mongos` query routers;
applications connect only to `mongos`, never directly to a shard [Source:
https://www.mongodb.com/docs/manual/sharding/]. Data is distributed by a
shard key using **hashed sharding** (even distribution, but range queries
scatter-gather) or **ranged sharding** (targeted queries, but distribution
quality depends on key choice) [Source:
https://www.mongodb.com/docs/manual/sharding/]. A background balancer
migrates chunks between shards; a single shard can only participate in one
chunk migration at a time. **As of MongoDB 8.3, DDL operations and
`applyOps` run only on `mongos` for all sharded clusters** — this tightened
an already-restrictive MongoDB 8.0 change that blocked most direct-to-shard
commands [Source: https://www.mongodb.com/docs/manual/sharding/]. A
monotonically increasing shard key bottlenecks insert throughput onto a
single shard [Source: https://www.mongodb.com/docs/manual/reference/limits/].
Max 12 shards for multi-region clusters, 70 for single-region [Source:
https://www.mongodb.com/docs/manual/reference/limits/].

**Indexing — the ESR rule.** For compound indexes, order fields as
**Equality, Sort, Range** for best performance [Source:
https://www.mongodb.com/docs/manual/applications/indexes/]. MongoDB
generally uses only one index per query (exception: `$or` queries may use a
different index per clause); map application queries to the fields they
touch before building indexes, and periodically audit/drop unused ones
[Source: https://www.mongodb.com/docs/manual/applications/indexes/]. Combine
unique indexes with `$jsonSchema` validation to jointly enforce
data-design invariants at the database layer [Source:
https://www.mongodb.com/docs/manual/applications/indexes/;
https://www.mongodb.com/docs/manual/data-modeling/schema-validation/specify-json-schema/].
Limits: max 64 indexes/collection, max 32 fields in a compound index, max
1024 bytes per index key [Source:
https://www.mongodb.com/docs/manual/reference/limits/].

**Officially named schema design patterns** (beyond the generic
embed/reference axis owned by data-modeling): Computed (precompute values to
avoid recalculation on read), Bucket/Group (time-bucket related data),
Polymorphic (documents in one collection vary in fields/types), Schema
Versioning (embed a version marker so schema generations coexist during
migration), Archive (move cold data to separate storage), and Single
Collection (group related heterogeneous document types via references)
[Source: https://www.mongodb.com/docs/manual/data-modeling/design-patterns/].

**Transactions.** Multi-document ACID transactions (`startTransaction()` /
`commitTransaction()` / `abortTransaction()` on a client session) are
available on replica sets **as of MongoDB 4.0** and on sharded clusters **as
of MongoDB 4.2** [Source:
https://www.mongodb.com/docs/manual/core/transactions/]. MongoDB's own
transactions documentation recommends denormalized/embedded schema design as
the preferred alternative wherever the data model allows it, reserving
transactions for cases that genuinely require cross-document atomicity
[Source: https://www.mongodb.com/docs/manual/core/transactions/]. Default
transaction lifetime is 60 seconds; max 100,000 write operations per batch;
transactions must use `primary` read preference; at most one open
transaction per session [Source:
https://www.mongodb.com/docs/manual/reference/limits/].

## Decision framework

This assumes the document-store decision was already made by
[data-modeling](../data-modeling/SKILL.md) — the choices below are
MongoDB-internal, not "should we use MongoDB."

1. **Embed or reference this relationship?** Embed when the related data is
   always read together with its parent, is bounded in size, and doesn't
   need independent querying at scale — this is MongoDB's own default bias
   [Source: https://www.mongodb.com/docs/manual/data-modeling/design-patterns/].
   Reference when the related data is large/unbounded, is queried/updated
   independently, or is shared across many parents. Watch the 16 MiB
   document ceiling and the unbounded-array anti-pattern as hard limits on
   how far embedding can go [Source:
   https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/].
2. **Do I actually need a multi-document transaction, or does single-document
   atomicity already cover this?** A single document's writes are always
   atomic. Reach for a transaction only when an invariant genuinely spans
   multiple documents/collections and cannot be restructured into one
   document — MongoDB's own docs prefer the restructuring [Source:
   https://www.mongodb.com/docs/manual/core/transactions/]. Confirm the
   deployment actually supports transactions for the topology in play
   (replica set since 4.0, sharded cluster since 4.2) [Source:
   https://www.mongodb.com/docs/manual/core/transactions/].
3. **Is sharding actually warranted yet?** Sharding is the documented
   scaling recommendation for write-heavy workloads once a single
   `mongod`/replica set is the bottleneck [Source:
   https://www.mongodb.com/docs/manual/administration/analyzing-mongodb-performance/],
   not a day-one default. Sharding adds real operational cost (shard-key
   selection is hard to reverse, config servers, balancer coordination,
   restricted direct-to-shard operations as of 8.0/8.3). Prefer a
   well-sized single replica set until write throughput or working-set size
   demonstrably exceeds it. When sharding, prefer ranged sharding when
   targeted range queries matter and the key has good cardinality/write
   distribution; prefer hashed sharding when even write distribution matters
   more than range-query locality [Source:
   https://www.mongodb.com/docs/manual/sharding/].
4. **Enforce structure with `$jsonSchema` or leave it to the application?**
   Use `$jsonSchema` (with `validationAction: warn` first, then `error`)
   when the invariant must hold regardless of which code path writes the
   document; leave it to application code only for genuinely optional,
   evolving fields where database-level enforcement would fight the
   document model's flexibility [Source:
   https://www.mongodb.com/docs/manual/data-modeling/schema-validation/specify-json-schema/].

## Workflow

1. Confirm the store-shape decision (document vs. relational) is already
   settled by data-modeling; if not, hand off there first.
2. Design the document shape: decide embed vs. reference per the decision
   framework, using the named design patterns (Computed, Bucket, Polymorphic,
   Schema Versioning, Archive, Single Collection) where they fit.
3. Specify a `$jsonSchema` validator for invariants that must hold at the
   database layer; start at `validationAction: warn` on populated
   collections before moving to `error`.
4. Build compound indexes in ESR order against the actual query set; drop
   indexes not backing a real query.
5. Decide whether a multi-document transaction is genuinely needed, or
   whether restructuring to a single document removes the need.
6. Only after write throughput or working-set size demonstrably exceeds a
   single replica set, design a shard key and sharding strategy.
7. Apply the Security Checklist (RBAC, TLS, encryption-at-rest posture) and
   hand off ODM-level mapping to [orm-integration](../orm-integration/SKILL.md)
   or SK-TECH-mongoose.

## Engineering rules

- Order compound index fields Equality → Sort → Range (ESR rule); state a
  reason when deviating.
- Justify embed vs. reference by the access pattern and document-size
  limits, not by convenience or ORM familiarity.
- Prefer restructuring to a single document over reaching for a
  multi-document transaction; use transactions only for invariants that
  genuinely cross documents.
- Don't shard until a single replica set is the demonstrated bottleneck —
  shard-key choice is expensive to reverse.
- Stage `$jsonSchema` validation changes through `warn` before `error` on
  populated collections.
- Tag every version-gated claim (FCV mechanics, sharding DDL routing,
  Transparent Hugepages guidance, AVX requirement, minor-release
  sequencing) with the version range it holds for; never assume "latest"
  silently.

## Trade-offs

Embedding speeds single-aggregate reads and keeps writes atomic per document,
but risks the 16 MiB ceiling and unbounded-array growth, and duplicates data
that's referenced elsewhere. Referencing avoids duplication and unbounded
growth but reintroduces `$lookup`-based joins, which MongoDB's own docs flag
as a signal to denormalize instead [Source:
https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/].
Sharding buys horizontal write/storage scale but costs a hard-to-reverse
shard-key decision, restricted direct-to-shard operations, and added
operational surface (config servers, balancer, cross-shard query
scatter-gather on range queries under hashed sharding) [Source:
https://www.mongodb.com/docs/manual/sharding/]. Multi-document transactions
buy cross-document atomicity but carry materially greater performance cost
than single-document writes, per MongoDB's own docs [Source:
https://www.mongodb.com/docs/manual/reference/limits/].

## Anti-patterns

MongoDB's documentation names five schema anti-patterns [Source:
https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/]:

1. **Unbounded arrays** — arrays that grow without bound risk exceeding the
   16 MB document limit and degrade index performance.
2. **Massive number of collections** — decreases storage-engine performance
   and adds unnecessary operational complexity.
3. **Unnecessary indexes** — indexes not backing real queries consume disk
   space and degrade write performance.
4. **Bloated documents** — excessively large documents degrade common query
   performance and increase memory usage.
5. **Excessive `$lookup` use** — heavy reliance on cross-collection
   `$lookup` joins is a signal the data should be denormalized/embedded
   instead. **This is the domain's over-engineering trap in reverse**:
   reaching for relational-style joins in a document store instead of
   restructuring the schema around the actual read pattern.

Also avoid: sharding "for later" before write/storage demonstrably
outgrows a single replica set (mirrors data-modeling's general
"second store for later" anti-pattern, applied to sharding specifically);
reaching for a multi-document transaction where restructuring to one
document would remove the need [Source:
https://www.mongodb.com/docs/manual/core/transactions/]; and choosing a
monotonically increasing shard key, which bottlenecks inserts onto a single
shard [Source: https://www.mongodb.com/docs/manual/reference/limits/].

## Security

Role-Based Access Control (RBAC) is the documented authorization model, but
**access control is not on by default on self-managed deployments** — it
must be explicitly enabled [Source:
https://www.mongodb.com/docs/manual/security/]. Supported authentication
mechanisms: SCRAM (default), X.509, LDAP, Kerberos, OIDC/OAuth 2.0 [Source:
https://www.mongodb.com/docs/manual/security/]. **Encryption at rest is an
Enterprise-only feature for self-managed deployments**; Atlas offers
Customer Key Management instead; Queryable Encryption and Client-Side Field
Level Encryption (CSFLE) encrypt specific fields while retaining query
capability [Source: https://www.mongodb.com/docs/manual/security/]. TLS is
on by default in Atlas but must be configured explicitly on self-managed
instances [Source: https://www.mongodb.com/docs/manual/security/]. The
official Security Checklist additionally recommends: least-privilege RBAC
with a dedicated user administrator, unique users per person/application,
encrypting data at rest via WiredTiger native encryption or filesystem/
device-level encryption, limiting network exposure (`net.bindIp`,
`clusterIpSourceAllowlist`), enabling auditing (Enterprise-only), running
`mongod`/`mongos` under a dedicated minimally-privileged OS user, and
disabling server-side JavaScript (`--noscripting`) if unused [Source:
https://www.mongodb.com/docs/manual/administration/security-checklist/].
At the driver level: prefer `mongodb+srv://` connection strings (TLS by
default), validate untrusted input before JSON→BSON conversion to prevent
injection, prefer typed document-builder APIs over string concatenation,
and restrict/disable server-side JavaScript execution in
`$where`/`$function`/`$accumulator`, a documented injection vector [Source:
https://www.mongodb.com/docs/drivers/client-libraries-best-practices/]. Deep
threat-modeling and RBAC-vs-other-engines comparison is owned by
data-modeling's Security section and `security-engineering`; this section
states only MongoDB-specific defaults.

## Performance

WiredTiger cache sizing is a first-order performance lever: default
internal cache is `max(50% × (RAM − 1 GB), 256 MB)`, tunable via
`--wiredTigerCacheSizeGB` or a percentage-based
`--wiredTigerCacheSizePct` (valid range 0.256 GB–10,000 GB); the internal
cache holds uncompressed collection data plus compressed index data, with
the filesystem cache picking up the remainder [Source:
https://www.mongodb.com/docs/manual/core/wiredtiger/]. In containers, check
`db.hostInfo().memLimitMB` rather than relying on host-level RAM detection
when sizing the cache [Source:
https://www.mongodb.com/docs/manual/administration/production-notes/].
Indexes are the primary query-performance lever but add write overhead and
memory cost — justify each by real query frequency (ESR rule above) and
drop unused ones [Source:
https://www.mongodb.com/docs/manual/applications/indexes/]. For write-heavy
workloads, the documented scaling recommendation is sharding across
multiple `mongod` instances rather than vertical scaling alone [Source:
https://www.mongodb.com/docs/manual/administration/analyzing-mongodb-performance/].
`serverStatus` is the central diagnostic surface (`locks.*` for contention,
`globalLock.*` for global-lock pressure, `connections.*` for saturation)
[Source: https://www.mongodb.com/docs/manual/administration/analyzing-mongodb-performance/].
Version-gated OS tuning: **enable Transparent Hugepages as of MongoDB 8.0+,
but disable them on MongoDB 7.0 and earlier** — this guidance flips by
version, so check the deployment's major before applying it [Source:
https://www.mongodb.com/docs/manual/administration/production-notes/].
Deep general performance methodology is owned by `SK-QA-003`; this section
states only MongoDB-specific levers.

## Testing

MongoDB is a documented exception among this library's researched database
technologies: it has official first-party testing-deployment guidance where
PostgreSQL/MySQL/ClickHouse do not. Two officially documented local-testing
paths exist: a lightweight, non-production **replica-set-for-testing**
topology [Source:
https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-for-testing/],
and the official `mongodb/mongodb-atlas-local` Docker image
(`docker run -p 27017:27017 mongodb/mongodb-atlas-local`, with optional
`MONGODB_INITDB_ROOT_USERNAME`/`MONGODB_INITDB_ROOT_PASSWORD` and a
documented Compose pattern; minimum Docker Desktop v4.31+/Engine v27.0+, 2
GB RAM/2 CPU cores) [Source:
https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-deploy-docker/].
**This official page does not mention Testcontainers** — MongoDB's own docs
focus on direct Docker/Compose workflows, not a Testcontainers-based flow
[Source: https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-deploy-docker/].
Unresolved: whether MongoDB officially documents or endorses in-process/
in-memory test servers (e.g. the community `mongodb-memory-server` package)
could not be confirmed from official docs. Deep test-strategy method is
owned by `SK-QA-001` / `testing-strategy`.

## Failure handling

- If the MongoDB major version and deployment form (self-managed vs. Atlas)
  cannot be determined, ask for them or state the version the guidance
  assumes — never assume "latest" silently.
- If shell is unavailable/denied, degrade to advisory schema/pipeline/index
  output and say that indexes, aggregation, or `explain()` were not
  actually run.
- If the store-shape decision (document vs. relational) is still open, hand
  off to data-modeling rather than assuming MongoDB is already the right
  choice.

## Escalation

- A sharding-topology decision, or moving a `$jsonSchema` `validationAction`
  from `warn` to `error` on a populated collection, requires explicit user
  confirmation before being treated as decided.
- Raising `featureCompatibilityVersion` (FCV) as part of a major-version
  upgrade removes the easy downgrade path within that major — confirm
  before doing so.
- A change to authentication/authorization configuration on a production
  deployment requires explicit confirmation.

## Outputs & verification

- **Outputs:** a document schema/`$jsonSchema` validator reflecting the
  embed-vs-reference decision; index/pipeline changes addressing the actual
  access pattern; an analysis with rationale and the MongoDB version it
  applies to.
- **Verify:** compound indexes follow ESR order (or deviation is justified);
  embed vs. reference is justified by access pattern and document-size
  limits; version-gated claims are tagged with their applicable range; a
  schema-validation change has a staged rollout path; any proposed
  transaction is justified against MongoDB's own preference for
  denormalized design.

## References

- [research/technologies/mongodb.md](../../research/technologies/mongodb.md) — full primary research (all citations above trace here).
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md) — §2, MongoDB vs. PostgreSQL/MySQL/ClickHouse comparison.
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md) — MongoDB section, version-gated facts used in `skill.yaml.version_sensitive_claims`.
- [data-modeling](../data-modeling/SKILL.md) (SK-DATA-001) — the generic store-shape and schema-design method this skill specializes.
- [orm-integration](../orm-integration/SKILL.md) (SK-DATA-002) — ODM/ORM usage mechanics; see also SK-TECH-mongoose for Mongoose-specific detail.
- [data-migration](../data-migration/SKILL.md) (SK-DATA-006) — safely evolving an already-populated MongoDB deployment.
