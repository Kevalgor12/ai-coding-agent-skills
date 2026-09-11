---
name: RAG Engineering
description: >-
  Design retrieval-augmented generation: the retrieve-then-generate
  pipeline, chunking/embedding strategy, and context injection for
  grounding LLM output in a retrievable corpus. Enforces authorization
  inside the retrieval query (not post-filtering) and treats embedding
  stores/backups as source-document-sensitive. Use when a feature needs
  LLM output grounded in a specific document/data corpus. Not for the
  vector/semantic search infrastructure itself — route to
  search-integration (SK-DATA-005).
spec_version: "1.0"
---

## Purpose & scope

Design retrieval-augmented generation — the retrieve-then-generate
pipeline, the embedding layer feeding it (model/dimensionality choice,
chunking strategy), and context injection — independent of which
embedding model, vector store, or search engine is eventually used.
**This skill draws an explicit boundary against
[search-integration](../search-integration/SKILL.md) (SK-DATA-005), which
already owns the vector/semantic search infrastructure itself**: engine
selection (database-native FTS vs. dedicated engine vs. vector store),
index/mapping design, relevance tuning, and index-sync strategy are
SK-DATA-005's scope, not restated here. This skill owns what sits above
that infrastructure — the RAG pattern — plus two risks the OWASP GenAI
LLM Top 10 (2026) research documents directly against retrieval and
embedding stores: retrieval-authorization ordering and embedding-store
sensitivity.

## When to use / When not to use

**Use** when a feature needs LLM output grounded in a specific
document/data corpus rather than the model's own knowledge, or when
designing/reviewing a retrieve-then-generate pipeline's chunking,
embedding, or context-injection strategy. **Do not use** when no
retrieval corpus is involved, or when the actual request is about the
vector/semantic search infrastructure itself (engine choice, indexing,
relevance tuning) — route to
[search-integration](../search-integration/SKILL.md).

## Knowledge

**RAG is a three-stage pipeline — retrieval, context injection,
generation — and each stage has a distinct failure mode.** Retrieval
finds the candidate content (via the vector/semantic search
infrastructure owned by SK-DATA-005); context injection places that
content into the LLM's context window following
[prompt-context-engineering](../prompt-context-engineering/SKILL.md)'s
placement guidance (long-context content belongs before the query, not
after); generation produces output conditioned on it. Chunking and
embedding-model/dimensionality choice sit upstream of retrieval and
determine what a query can actually match — chunk size/overlap and
embedding-model choice are RAG-pipeline decisions, not search-engine
configuration, and should be stated explicitly rather than left at a
library default.

**Retrieval-authorization ordering is the single most repeated
architectural recommendation in the OWASP research, stated independently
in two separate risk entries.** LLM09 (Vector and Embedding Weaknesses)
documents **cross-tenant leakage**: probing a shared index can reveal
another tenant's data existence/volume through result counts and score
patterns even with correct authentication, "because access control
applied post-search enables this geometric exploitation"
[Source: owasp-llm-top10.md — LLM09:2026]. LLM02 (Sensitive Information
Disclosure) states the same fix as a Tier-1, all-deployments mitigation:
"Authorize before retrieval: enforce document- and chunk-level
authorization inside the index query" — not after
[Source: owasp-llm-top10.md — LLM02:2026 Tier 1]. The cross-cutting
patterns section of the same research restates this again as one of the
standard's "most repeated single architectural recommendations"
[Source: owasp-llm-top10.md — Section 8]. Concretely: a RAG retrieval
query MUST filter by the requesting user's/tenant's authorization scope
as part of the index query itself (a `WHERE`-equivalent inside the
vector/keyword search call), never as a step that fetches unscoped
results and discards unauthorized ones afterward.

**Embedding stores, exports, and backups are source-document-sensitive,
not a lower-sensitivity derived artifact — this is a documented, not
inferred, claim.** LLM09 reports embedding-inversion recovery rates of
"roughly 50–70% of words from sentence embeddings to 92% exact
reconstruction of short 32-token inputs," working "across black-box
systems" and persisting "despite differential-privacy protections"
[Source: owasp-llm-top10.md — LLM09:2026]. Because of this, the
research's own framing is explicit: "an embeddings-only backup is a
source-document breach" once inversion is accounted for
[Source: owasp-llm-top10.md — LLM09:2026, Section 9 Anti-Patterns]. LLM02
cross-references the same claim as load-bearing for anyone treating
vector-store backups as lower-sensitivity than the documents they were
built from [Source: owasp-llm-top10.md — LLM02:2026]. Practically: an
embedding store's backup/export/retention policy, access controls, and
breach classification should match the source corpus's sensitivity
tier — not a weaker one — and encrypted vector stores with per-tenant
ACLs are the documented Tier-2 hardening for regulated contexts
[Source: owasp-llm-top10.md — LLM02:2026 Tier 2].

**Two further LLM09-documented risks worth designing against explicitly
at the RAG-pipeline layer.** **Retrieval jamming**: "a single engineered
'blocker' document causes the LLM to refuse answers" — a pure
availability attack requiring no malicious instructions in the retrieved
content, so retrieval-quality monitoring should watch for anomalous
refusal rates, not just latency/error rates
[Source: owasp-llm-top10.md — LLM09:2026]. **Retrieved content is an
indirect-prompt-injection surface**: the research's prompt-injection
entry names "RAG passages" explicitly among untrusted external content
that "the model ingesting... carries attacker instructions the user
never supplied or saw"
[Source: owasp-llm-top10.md — LLM01:2026 — Section 4], meaning retrieved
chunks must be treated as untrusted input at the context-injection stage,
consistent with [ai-security](../ai-security/SKILL.md)'s (SK-AI-008)
broader indirect-injection guidance rather than trusted verbatim because
they came from "your own" corpus.

**Anthropic's Claude API has no first-party RAG feature documented in
this library's research** — Claude Managed Agents provides a managed
agent-loop/sandbox harness, not a retrieval/vector-store product, so RAG
on Claude means composing your own retrieval layer with context injection
[Source: anthropic-claude-api.md]. **OpenAI's Responses API ships a
hosted File Search tool** that performs "semantic and keyword search"
against **vector stores** (files uploaded via the Files API, added to a
vector store, referenced by `vector_store_ids`), requiring no
retrieval-side implementation code
[Source: openai-api.md]. OpenAI's own prompt-engineering guidance frames
RAG plainly: add "additional relevant context to the model generation
request" (via vector databases or the File Search tool) "to constrain
responses to a specific set of resources"
[Source: openai-api.md]. This is a real platform-choice fork in the
decision framework below, not a universal default.

## Decision framework

1. **Is grounding in a specific corpus actually needed, or would the
   model's own knowledge (or context already in the request) suffice?**
   Don't stand up a retrieval pipeline for a task that doesn't need
   external grounding — the simplest viable option is no RAG at all.
2. **Is the retrieval infrastructure itself already decided, or open?**
   If open, that decision belongs to
   [search-integration](../search-integration/SKILL.md) (SK-DATA-005) —
   don't re-litigate engine choice here; this skill starts from "a
   retrieval mechanism exists or will exist" and designs the pipeline
   around it.
3. **What chunking and embedding-model/dimensionality choice fits the
   corpus and query pattern?** State it explicitly (chunk size/overlap,
   embedding model) rather than accepting a library default unexamined —
   this determines what a query can match at all.
4. **Does the retrieval query enforce authorization inside the query, or
   does it filter results after retrieval?** Post-retrieval filtering is
   the documented cross-tenant-leakage pattern (LLM09) and the anti-
   pattern the Tier-1 LLM02 mitigation exists specifically to close —
   redesign to filter inside the index query before treating this as
   done.
5. **Is the embedding store's sensitivity classification, access
   control, and backup policy at least as strict as the source corpus's?**
   Given documented inversion rates up to 92% exact reconstruction,
   never classify an embeddings-only backup as lower-sensitivity than
   the source documents.
6. **Is a hosted retrieval product available and sufficient (e.g.
   OpenAI's File Search/vector stores), or does the task need a
   self-managed retrieval layer?** A hosted tool trades control for
   zero retrieval-side implementation; a self-managed layer (composed
   with SK-DATA-005) buys control at the cost of building and operating
   it — state this trade-off rather than defaulting either way.
7. **Where does retrieved content get injected, and is it treated as
   untrusted input?** Follow SK-AI-002's context-placement guidance, and
   treat retrieved chunks as an indirect-prompt-injection surface per
   SK-AI-008, not as trusted-by-default because they came from an
   internal corpus.

## Workflow

1. Confirm grounding in a specific corpus is actually needed (Decision
   framework step 1).
2. Identify or hand off the retrieval infrastructure decision to
   [search-integration](../search-integration/SKILL.md) if it's still
   open.
3. Design the chunking strategy and choose an embedding model/
   dimensionality for the corpus and expected query pattern.
4. Design the retrieval query so that authorization is enforced inside
   the query itself (document/chunk-level scoping), not as a
   post-retrieval filter.
5. Design context injection — where retrieved content lands in the
   context window and how it's delimited as untrusted content — per
   [prompt-context-engineering](../prompt-context-engineering/SKILL.md).
6. Classify the embedding store's sensitivity (access control, backup/
   retention policy, breach classification) as source-document-equivalent.
7. Decide hosted-tool vs. self-managed retrieval per the target
   platform's documented capabilities (e.g. OpenAI File Search vs. a
   composed vector-store pipeline).
8. Hand off implementation-level retrieval-infrastructure depth to
   [search-integration](../search-integration/SKILL.md), and
   security-review the finished design against
   [ai-security](../ai-security/SKILL.md) (SK-AI-008) for
   indirect-injection and blast-radius concerns.

## Engineering rules

- Enforce authorization inside the retrieval/index query, never as a
  post-retrieval filter over unscoped results.
- Classify embedding stores, exports, and backups as source-document-
  sensitive — never a lower-sensitivity tier than the source corpus.
- State the chunking strategy and embedding-model/dimensionality choice
  explicitly rather than leaving them at an unexamined default.
- Treat retrieved content as untrusted input at the context-injection
  stage, not as trusted-by-default because it came from an internal
  corpus.
- Don't re-decide the vector/semantic search engine here — that decision
  belongs to search-integration (SK-DATA-005).

## Trade-offs

A hosted retrieval product (e.g. OpenAI's File Search/vector stores)
buys zero retrieval-side implementation at the cost of platform lock-in
and less control over chunking/relevance internals; a self-managed
retrieval layer composed with SK-DATA-005's infrastructure buys full
control at the cost of building and operating it. Finer chunking
(smaller chunks) improves retrieval precision for narrow queries at the
cost of more chunks to embed/store and less surrounding context per
retrieved unit; coarser chunking preserves context at the cost of
precision and higher per-query token cost from injecting larger chunks.

## Anti-patterns

- **Filtering authorization after retrieval** instead of inside the
  index query — the documented cross-tenant-leakage pattern this
  library's research names explicitly (LLM09, LLM02).
- **Treating an embeddings-only backup as lower-sensitivity than the
  source documents** — a documented anti-pattern given inversion
  recovery rates up to 92% exact reconstruction of short inputs.
- **Building a RAG pipeline when the task doesn't actually need external
  grounding** — the domain's over-engineering trap; the model's own
  knowledge or already-supplied context is the simpler, correct choice
  when sufficient.
- **Re-deciding the search/vector-store engine inside this skill**
  instead of deferring to search-integration (SK-DATA-005) — duplicates
  an already-owned decision.
- **Trusting retrieved content as safe by default** because it came from
  an internal corpus, ignoring that RAG passages are a documented
  indirect-prompt-injection surface.

## Security

Retrieval-authorization ordering and embedding-store sensitivity
(above) are this skill's own security-relevant content, grounded
directly in LLM09/LLM02. Retrieved content as an indirect-prompt-
injection vector, and broader LLM-specific threat modeling (excessive
agency, blast-radius bounding), are owned by
[ai-security](../ai-security/SKILL.md) (SK-AI-008) — coordinate with it
rather than restating its guidance here.

## Testing

Retrieval-quality evaluation (does the pipeline retrieve the right
chunks for a representative query set, and does generation stay grounded
in what was retrieved rather than drifting into unsupported claims) is
an LLM-output grading concern, not a plain assert-true/false test — owned
by [llm-evaluation](../llm-evaluation/SKILL.md) (referenced
by ID: SK-AI-007) for grading-method and golden-dataset design.

## Failure handling

- If the retrievable corpus isn't identified, ask rather than designing
  a generic pipeline.
- If the request is actually about the vector/semantic search
  infrastructure itself, state that this is SK-DATA-005's scope rather
  than answering as if it were RAG-pipeline design.
- If an existing retrieval layer filters authorization after retrieval
  rather than inside the query, flag it as a documented cross-tenant-
  leakage risk rather than treating it as a stylistic choice.

## Escalation

- A retrieval layer found to filter authorization post-search (rather
  than inside the query) is escalated as a security finding coordinated
  with [ai-security](../ai-security/SKILL.md) (SK-AI-008), not silently
  redesigned without flagging the risk.

## Outputs & verification

- **Outputs:** a RAG pipeline design (retrieval, chunking/embedding
  choice, context injection) and authorization/sensitivity notes for the
  retrieval layer.
- **Verify:** authorization is enforced inside the retrieval query, not
  post-filtered; embedding stores/backups are classified as source-
  document-sensitive; context injection follows documented placement
  guidance; the chunking/embedding strategy is stated explicitly.

## References

- [research/technologies/owasp-llm-top10.md](../../research/technologies/owasp-llm-top10.md)
- [research/technologies/openai-api.md](../../research/technologies/openai-api.md)
- [research/technologies/anthropic-claude-api.md](../../research/technologies/anthropic-claude-api.md)
- [llm-application-engineering](../llm-application-engineering/SKILL.md)
- [search-integration](../search-integration/SKILL.md)
- [prompt-context-engineering](../prompt-context-engineering/SKILL.md)
- [ai-security](../ai-security/SKILL.md)
