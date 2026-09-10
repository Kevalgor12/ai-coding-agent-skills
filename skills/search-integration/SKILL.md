---
name: Search integration
description: >-
  Add full-text and/or vector/semantic search — choose an engine
  (database-native FTS vs. dedicated search engine vs. vector search),
  design indexing/mapping, tune relevance, and keep the index in sync with
  the source of truth. Use when a feature needs search beyond a simple
  indexed lookup. Not for plain `WHERE`-clause queries, and not for the
  RAG/LLM-application layer on top of vector search, which this library
  has not researched.
spec_version: "1.0"
---

## Purpose & scope

Choose a search approach when that's open, and design indexing, relevance
tuning, and index-sync strategy around it — independent of which engine is
eventually used. A simple indexed `WHERE`-clause lookup doesn't need this
skill at all. **The RAG/LLM-application layer built on top of vector
search — retrieval-augmented generation, prompt assembly, embedding-model
selection for an LLM pipeline — is a documented research gap in this
library** (`llm-application-engineering`, flagged in
`taxonomy-analysis.md` as needing a dedicated research pass); this skill
covers the search/indexing layer underneath that, not the LLM layer on top
of it, and says so rather than improvising.

## When to use / When not to use

**Use** when a feature needs full-text, faceted/filtered, or semantic/
vector search, or when an existing search layer's relevance/mapping/sync
strategy needs review. **Do not use** when a simple indexed lookup query
suffices, or when the actual request is about the RAG/LLM-application layer
on top of vector search — state that gap rather than answering as if it
were a search-integration question.

## Knowledge

**Three technologies in this library's research all do search, but at
different scope** [Source: concept-knowledge-map.md — Full-Text Search /
Vector-Semantic Search sections]. PostgreSQL has built-in full-text search
as one capability among many. Redis has full-text search *and* vector
similarity search among its multi-model capabilities — it "doubles as a
vector database." OpenSearch is the only technology in this dataset whose
**primary purpose** is search — full-text plus semantic/vector search
together, as a dedicated engine. This maps directly onto the three-way
engine decision: reuse a database you already run (PostgreSQL/Redis) vs.
add a dedicated search engine (OpenSearch) vs. treat the need as vector-only
(Redis or OpenSearch both do this).

**OpenSearch is the only search engine actually profiled in this library's
research — Elasticsearch has no first-party data at all**
[Source: technology-decision-matrix.md — Search engine]. OpenSearch's own
Migration Assistant documents migration *from* Elasticsearch, and it is
"widely known as a fork of Elasticsearch/Kibana 7.10.2" — but that lineage
claim is itself flagged as an inference, not confirmed in OpenSearch's own
docs. Do not present Elasticsearch comparisons as researched fact; this
skill and its OpenSearch specialization are grounded in OpenSearch alone.

**Search-specific performance tuning is a distinct discipline from generic
database performance** [Source: performance-knowledge-map.md]. For a
dedicated engine like OpenSearch, tuning centers on: thread-pool and
circuit-breaker/admission-control settings (to prevent OOM under load);
separating index (write) and search (read) workloads to avoid resource
contention; and shard sizing as a first-class lever (10–30GB shards for
search-latency-sensitive workloads, 30–50GB for write-heavy/analytics
workloads — too many small shards wastes JVM heap on per-shard metadata,
too few large shards limits parallelization).

**Index-sync-with-source-of-truth is the structural risk unique to a
dedicated search engine that DB-native FTS doesn't have** — a dedicated
engine's index is a second copy of the data, not a view over the primary
store, so it can silently drift if writes to the source of truth aren't
reliably propagated to the index (via dual-write, change-data-capture, or a
documented reindex/ingestion pipeline). DB-native FTS (PostgreSQL, Redis)
avoids this class of bug entirely since the index lives alongside the data
it indexes.

## Decision framework

1. **Does a database already in use (PostgreSQL, Redis) already cover the
   need?** If the requirement is full-text search at moderate scale with no
   need for a separate cluster, DB-native FTS avoids the sync-drift risk
   and an entirely new operational surface — don't reach for a dedicated
   engine by default.
2. **Does the need include semantic/vector search, faceting, or
   search-specific relevance tuning beyond what the database offers?** If
   yes, and scale/query-complexity justify it, a dedicated engine
   (OpenSearch) or a vector-capable store (Redis) becomes the defensible
   choice.
3. **Is the actual need the RAG/LLM-application layer on top of vector
   search** (retrieval-augmented generation, prompt assembly)? If so, state
   that this exceeds this skill's grounded scope rather than answering as
   if it were an indexing/relevance question.
4. **If a dedicated engine is chosen, design the index-sync strategy
   explicitly before implementation** — dual-write, CDC, or a scheduled
   reindex pipeline — since this is the specific new failure mode a
   dedicated engine introduces that DB-native FTS doesn't have.
5. **Tune relevance deliberately, not by accepting engine defaults
   unexamined** — analyzer/tokenizer choice, field boosting, and query-type
   selection (match vs. match_phrase vs. more_like_this-style queries)
   materially change result quality for a given corpus.

## Workflow

1. Classify the need: full-text, faceted/filtered, and/or semantic/vector.
2. Apply the decision framework to select an approach/engine, citing the
   comparison above where relevant, and stating explicitly where research
   is thin (no first-party Elasticsearch data exists in this library).
3. Design index/analyzer/mapping structure for the chosen approach.
4. Design the index-sync strategy if a dedicated engine or vector store is
   chosen — how writes to the source of truth reach the index, and how
   drift would be detected.
5. Tune relevance deliberately rather than accepting defaults.
6. If the engine has search-specific performance levers (e.g. OpenSearch's
   shard sizing, thread-pool/circuit-breaker settings), address them before
   the index is at meaningful scale, not after a latency incident.
7. Hand off to the matching technology skill (opensearch, or the relevant
   database's technology skill) for implementation-level depth.

## Engineering rules

- Don't reach for a dedicated search engine when DB-native FTS on a
  database already in use would satisfy the requirement.
- Design the index-sync strategy explicitly whenever a dedicated engine or
  separate vector store is chosen — an implicit "we'll reindex eventually"
  plan is not a strategy.
- Tune relevance deliberately for the actual corpus and query patterns,
  not by leaving analyzer/boosting at engine defaults unexamined.
- State plainly when this library's research doesn't cover a comparison
  (e.g. Elasticsearch) rather than presenting an unresearched claim as fact.
- Don't answer a RAG/LLM-application-layer request as if it were a
  search-integration question — that's a documented gap, not silently
  covered here.

## Trade-offs

DB-native FTS (PostgreSQL, Redis) avoids a new operational surface and the
index-sync-drift risk, at the cost of less search-specific tooling
(analyzer richness, faceting, dedicated relevance tuning) than a purpose-
built engine offers. A dedicated engine (OpenSearch) buys that tooling and
scale headroom, at the cost of a second data copy to keep in sync and an
additional cluster to operate. Vector/semantic search (Redis or OpenSearch)
buys similarity-based retrieval that keyword search can't do, at the cost
of embedding-generation infrastructure and a genuinely different failure
mode (semantically-plausible-but-wrong results) than keyword search's
more predictable failure mode (no match found).

## Anti-patterns

- **Standing up a dedicated search engine before checking whether the
  database already in use covers the need** — an unjustified new
  operational surface.
- **Leaving index-sync implicit** ("we'll reindex eventually") instead of
  an explicit dual-write/CDC/scheduled-reindex design — the single most
  common way a dedicated-engine search index silently goes stale.
- **Leaving relevance at engine defaults** for a corpus/query pattern that
  actually needs analyzer or boosting tuning.
- **Presenting Elasticsearch guidance as researched fact** — this
  library's research covers OpenSearch only; say so rather than
  improvising an Elasticsearch comparison.
- **Answering a RAG/LLM-application-layer question as a search-integration
  question** — the domain's specific overreach trap, given this library's
  documented research gap there.

## Security

Access-control and encryption specifics belong to the engine (e.g.
OpenSearch's RBAC/document-level/field-level security model, covered in
the [opensearch](../opensearch/SKILL.md) technology skill) rather than this
generic skill. Deep threat modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Search-specific tuning (shard sizing, thread-pool/circuit-breaker settings,
read/write workload separation) is engine-specific — see the
[opensearch](../opensearch/SKILL.md) technology skill for OpenSearch's
documented levers. Deep performance method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

Index-sync correctness (does the index actually reflect the source of
truth) and relevance-quality regression are the two search-specific testing
concerns beyond generic functional testing — both should be verified
explicitly for any non-trivial search feature, not assumed from the engine
working correctly in isolation. Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If the search requirement is too thin to support an engine decision,
  request it rather than assuming a default.
- If a search engine is already in place, work within it unless a switch
  is explicitly requested.
- If the actual need is the RAG/LLM-application layer, state that gap
  explicitly.

## Escalation

- A search-engine switch for an existing production index is a
  significant, hard-to-reverse decision (reindexing at scale, potential
  downtime) — presented with trade-offs for explicit confirmation, never
  applied unilaterally.
- A request for RAG/LLM-application-layer depth is escalated as a research
  gap requiring a dedicated research pass, not answered from general
  knowledge.

## Outputs & verification

- **Outputs:** a search-engine/approach recommendation with trade-offs
  (when open), and an index-design/relevance/sync-strategy.
- **Verify:** the index-sync strategy is explicit, not implicit; relevance
  is tuned deliberately for the actual corpus/queries; an engine
  recommendation cites real research where it exists and states plainly
  where it doesn't.

## References

- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
- [research/knowledge-maps/performance-knowledge-map.md](../../research/knowledge-maps/performance-knowledge-map.md)
- [research/knowledge-maps/concept-knowledge-map.md](../../research/knowledge-maps/concept-knowledge-map.md)
