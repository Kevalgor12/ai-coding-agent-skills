# Redis data-structure selection (Tier-2)

Redis Open Source implements the following core data types, each documented
with its own overview page and command reference
[Source: https://redis.io/docs/latest/develop/data-types/]. This table maps
each documented type to the access pattern it fits and the caveats the
research surfaced. Load this file only when a data-structure choice is the
actual question — the SKILL.md body covers the types that matter for most
caching/messaging tasks (strings, hashes, sets, sorted sets) inline.

| Data type | Fits when... | Documented properties / caveats | Source |
|---|---|---|---|
| **Strings** (+ Bitmaps, Bitfields as sub-features) | A single scalar value, counter, or session blob per key. | Value size capped by the RESP bulk-string limit, 512 MB default (`proto-max-bulk-len`). Storing a JSON document as an opaque string forces full deserialize/reserialize on every read/update and precludes atomic field-level updates — a documented anti-pattern (Medium severity); use `HASH` or the native JSON type instead. | [Source: https://redis.io/docs/latest/develop/reference/protocol-spec/]; [Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/] |
| **Hashes** | An object with several fields you need to read/write individually (a user profile, a converted JSON blob). | Documented as the fix for the "JSON blob as opaque string" anti-pattern. Converting a relational row or JSON document to a `HASH` without considering query patterns is itself a separate documented anti-pattern (Medium) if it leaves `SCAN`+`MATCH` as the only retrieval path — pair with reverse indexes in `SET`/sorted-set structures if you need to look hashes up by a field other than their key. | [Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/] |
| **JSON** | A nested/document-shaped value you need to query or partially update natively. | Bundled into core Redis as of **8.0** (previously the separate RedisJSON module) [Version-sensitive, >=8.0]. The 8.0 ACL category widening means `@write`/`@dangerous` etc. now cover `JSON.*` commands — re-check ACL rules on upgrade. | [Source: https://redis.io/docs/latest/develop/data-types/]; [Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] |
| **Lists** | An ordered sequence (queue, recent-activity feed) accessed from either end. | Documented as a core type with its own command reference; this research pass did not capture list-specific command detail beyond its listing. | [Source: https://redis.io/docs/latest/develop/data-types/] |
| **Sets** | Unordered unique membership (tags, "has this user done X") with O(1) add/remove/existence checks regardless of set size. | Add/remove/existence-check are documented as O(1) time regardless of the set's size. Useful as a reverse-index structure pointing back to `HASH`/string objects (see the Hashes row). | [Source: https://redis.io/docs/latest/develop/data-types/] |
| **Sorted sets** | Ranked/scored membership (leaderboards, priority queues, time-windowed data by score). | Documented as a core type; commonly paired with Sets as a reverse-index structure per the anti-patterns tutorial's documented fix for the "HASH without considering query patterns" anti-pattern. | [Source: https://redis.io/docs/latest/develop/data-types/]; [Source: https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/] |
| **Streams** | An append-only, consumer-group-readable log (event sourcing, activity logs) — the "streaming engine" role in Redis's own description. | Listed as a core type; command-level detail (XADD/XREAD/consumer groups) was not individually fetched in this research pass. | [Source: https://redis.io/docs/latest/get-started/]; [Source: https://redis.io/docs/latest/develop/data-types/] |
| **Geospatial indexes** | Location data and radius/bounding-box queries. | Documented as one of Redis's core data types with its own overview/command-reference page. Command-level detail (`GEOADD`/`GEOSEARCH` semantics) was not individually fetched in this research pass — verify exact command syntax against current docs before relying on it. | [Source: https://redis.io/docs/latest/develop/data-types/]; Not documented / could not verify beyond this listing in this research pass. |
| **Probabilistic types** (Bloom filter, Cuckoo filter, Count-min sketch, HyperLogLog, Top-K, t-digest) | Approximate membership/frequency/cardinality/quantile queries at a scale where exact structures would be too large. | Previously separate "Redis Stack" modules; became integral, bundled parts of core Redis starting with **8.0** [Version-sensitive, >=8.0]. The 8.0 ACL category widening covers these commands too — re-check ACL rules on upgrade. A HyperLogLog out-of-bounds-write CVE (CVE-2025-32023) was patched in Redis 8.0.3 (July 2025) — a concrete reason to stay current on patch releases for this data-type family. | [Source: https://redis.io/docs/latest/develop/data-types/]; [Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] |
| **Time series** | Timestamped metric data with range/aggregation queries. | Bundled into core Redis as of **8.0** (previously a separate RedisTimeSeries module) [Version-sensitive, >=8.0]. | [Source: https://redis.io/docs/latest/develop/data-types/]; [Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] |
| **Vector sets** | High-dimensional vector similarity/hybrid search (embeddings + structured filters). | Introduced as a **preview** feature in Redis **8.0.0** [Version-sensitive, preview status]. Supports HNSW (hierarchical navigable small world) indexing and cosine-similarity queries, with native hybrid search combining vector similarity and structured filters. Preview status means the API/behavior may still change — confirm current status before committing to it for a production search architecture (defer the broader search-engine-choice question to `SK-DATA-005`, a forward reference). | [Source: https://redis.io/docs/latest/develop/data-types/]; [Source: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/] |

## Extensibility

Redis is extensible via two documented mechanisms: server-side functions
written in Lua, and custom Redis modules via the modules API — the same
mechanism that historically underlay RediSearch/RedisJSON/RedisTimeSeries/
RedisBloom before they were bundled into core Redis at 8.0
[Source: https://redis.io/docs/latest/develop/data-types/];
[Source: https://redis.io/docs/latest/develop/programmability/].

## Unresolved

- List-type and Stream-type command-level detail (beyond their existence as
  documented core types) was not individually fetched in the primary
  research pass — verify specific command syntax against current docs.
- Geospatial command syntax (`GEOADD`, `GEOSEARCH`, etc.) was not fetched
  beyond the type's listing on the data-types overview page.
