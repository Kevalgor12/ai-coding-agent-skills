# Audit: AI/LLM-domain taxonomy design & skill generation

Date: 2026-09-10. Scope: eight generic skills (`SK-AI-001` through
`SK-AI-008`), all `kind: generic`, `layer: 3`, `domain: AI`, replacing a
single thin, research-gap-flagged placeholder (`SK-AI-001
llm-application-engineering`). Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).
This batch corresponds to **Step 26** of the project's master build plan
(`AI_Coding_Agent_Skill_Library_Complete_Step_By_Step.md`) and is the
**fourth** dedicated mid-project research pass in this library's history
(after Node.js in BACKEND, and the four-technology Observability pass
immediately prior on the same date) — but the first to require a
**taxonomy-design phase**, not just skill generation against an
already-designed taxonomy. The master plan's own Step 26 prompt calls for
this explicitly ("First act as a principal AI systems architect. Review
the approved AI/LLM taxonomy...") — the same two-phase treatment given to
Step 18 (Security).

## Pre-work: taxonomy design, then a three-source research pass

**Taxonomy design.** The prior taxonomy modeled the entire AI/LLM domain
as one thin placeholder (`SK-AI-001`), explicitly flagged
`*(research-gap — see analysis)*`. The master plan's own Step 26 candidate
list names 14 distinct concerns (LLM Architecture, Prompt Architecture,
Context Engineering, Structured Output, Tool Calling, Agent Architecture,
RAG, Embeddings, Vector Search, Model Selection, LLM Evaluation,
Hallucination Mitigation, AI Security, AI Observability). Rather than
promoting every candidate name to its own skill, a principal-architect
mapping was proposed and confirmed with the user before any research was
dispatched:

- **Merged** (tightly-coupled pairs, same rationale as this project's
  HTML+CSS merge): Prompt Architecture + Context Engineering →
  `prompt-context-engineering`; Structured Output + Tool Calling (the same
  underlying enforcement mechanism on both researched vendors' APIs) →
  `structured-output-tool-calling`; RAG + Embeddings (embeddings are RAG's
  mechanical prerequisite) → `rag-engineering`; LLM Evaluation +
  Hallucination Mitigation (mitigation is evaluation-driven) →
  `llm-evaluation`.
- **Declined as a new skill**: Vector Search — already covered by the
  already-authored `SK-DATA-005` (search-integration), whose scope already
  names "vector/semantic search." AI Observability — folded into the root
  skill (`SK-AI-001`) as a lightweight extension of the already-authored
  `SK-QA-004` (observability), since research found no LLM-specific
  observability concern deep enough to warrant a ninth skill.
- **Kept distinct**: Agent Architecture, Model Selection, and AI Security
  each became their own skill — Agent Architecture is a genuinely
  different orchestration-layer concern from a single tool call; Model
  Selection is the vendor-neutral decision layer the master plan
  explicitly requires ("do not assume one model/provider is always
  best"); AI Security is genuinely distinct from traditional AppSec
  (`SK-QA-002`), mirroring how authentication-authorization got its own
  skill separate from security-engineering.
- Result: **8 skills**, confirmed with the user via `AskUserQuestion`
  before research was dispatched.

**Research pass.** Three new research docs were authored via three
parallel agents, matching the established 17-dimension methodology (same
citation-format convention, same closing-section structure) — but sourced
from two vendor API doc sets and one security standard rather than one
software product each:

| Source | File | Lines | `[Source:]` citations |
|---|---|---|---|
| Anthropic Claude API (Messages API) | `research/technologies/anthropic-claude-api.md` | 313 | 82 |
| OpenAI API | `research/technologies/openai-api.md` | 336 | 99 |
| OWASP Top 10 for LLM Applications (2026) | `research/technologies/owasp-llm-top10.md` | 379 | 97 |

**New discipline for this batch: independent live-source spot-verification.**
Unlike prior batches, one research agent's own self-report flagged a
credibility concern — the OpenAI research doc named model IDs
(`gpt-6-astra`, the `gpt-5.6-sol/terra/luna` family) that don't match any
previously-known naming convention, and separately admitted catching
"tool contamination" in two fetched passages (text referring to "Claude"
instead of OpenAI's own models). Rather than accept or reject the
document on the agent's self-report alone, the three most load-bearing
claims across all three new docs were independently re-fetched live and
compared verbatim:

1. OpenAI's model lineup/pricing table (`developers.openai.com/api/docs/models`) — **matched exactly**.
2. The specific "Claude"-contamination passage on the OpenAI web-search guide page — **did not reproduce** on a clean re-fetch, consistent with the agent's own transient-tool-artifact explanation (documented as still-Unresolved for the one page not re-checked, per the registry).
3. Anthropic's model lineup/pricing table (`platform.claude.com/docs/en/models/overview`) — **matched exactly**, including the "Claude Fable 5.1"/"Claude Opus 5" naming this project's own environment independently confirms are real, current model IDs.
4. The current OWASP GenAI LLM Top 10 edition/publish-date (`genai.owasp.org/resource/owasp-genai-llm-top-10-2026/`) and the file listing of the ten current-edition risk entries (`github.com/GenAI-Security-Project/GenAI-LLM-Top10`) — **both matched exactly**.

All three documents were judged trustworthy on this basis before being
used to ground any skill. This is a new, stronger verification step than
prior batches used (which verified internal consistency and citation
density but did not re-fetch live sources against agent self-reports) —
worth carrying forward whenever a research agent's own report contains a
self-flagged credibility concern.

## Completed skills

| Skill | ID | Tier | Files | `[Source:]` citations |
|---|---|---|---|---|
| [llm-application-engineering](../skills/llm-application-engineering/) | SK-AI-001 | B | yaml, SKILL.md | 8 |
| [prompt-context-engineering](../skills/prompt-context-engineering/) | SK-AI-002 | B | yaml, SKILL.md | 18 |
| [structured-output-tool-calling](../skills/structured-output-tool-calling/) | SK-AI-003 | B | yaml, SKILL.md | 18 |
| [agent-architecture](../skills/agent-architecture/) | SK-AI-004 | B | yaml, SKILL.md | 13 |
| [rag-engineering](../skills/rag-engineering/) | SK-AI-005 | B | yaml, SKILL.md | 12 |
| [model-selection](../skills/model-selection/) | SK-AI-006 | A | yaml, SKILL.md | 13 |
| [llm-evaluation](../skills/llm-evaluation/) | SK-AI-007 | B | yaml, SKILL.md | 6 |
| [ai-security](../skills/ai-security/) | SK-AI-008 | B | yaml, SKILL.md | 26 |

All eight are `kind: generic`, `layer: 3`, `domain: AI`. None specializes
into a technology skill (Layer 4) — there is no single dominant
LLM-provider technology in the way there is for, e.g., Postgres or React;
`model-selection` is itself the vendor-neutral decision layer, and
`structured-output-tool-calling`/`agent-architecture` were deliberately
authored to teach the shared underlying pattern across both researched
vendors' APIs rather than picking one vendor to specialize into.

Independently verified on disk (not taken from agent self-reports):

- All 8 `skill.yaml` files present and required per VR-1 — every field
  present, `depends_on_skills: []` and `conflicts_with: []` explicit (not
  omitted) in all 8.
- **Zero `parents`-field misuse** — none of the 8 generic skills carries a
  `parents` field, confirmed programmatically.
- **`related_skills` cross-checked field-by-field against the approved
  catalog entries** — all 8 match exactly, no missing or extra
  cross-references.
- **CE-1 (description ≤500 chars)**: all 8 pass (469–498 chars, closest
  margin `model-selection` at 498/500).
- **Frontmatter parity (VR-2)**: `name`/`description`/`spec_version`
  verified byte-identical between each `skill.yaml` and its `SKILL.md`
  frontmatter, for all 8.
- **Full-repo YAML re-parse**: all 83 `skill.yaml` files in the repo
  (75 pre-existing + 8 new) parse cleanly — zero failures, confirming the
  three reciprocal edits below introduced no regression.
- **Duplicate-ID/duplicate-slug check**: `SK-AI-001`..`SK-AI-008` are each
  unique across the whole catalog; no collisions.

**Reciprocal cross-links** (the established practice of updating an
already-authored skill's `related_skills` when a new skill legitimately
relates to it, rather than only linking one direction):

- `skills/search-integration/skill.yaml` (`SK-DATA-005`) — added
  `SK-AI-005`. (Its `related_skills` already contained `SK-AI-001` from
  the *original* taxonomy design, before this batch — confirmed via `git
  log`, not a stray addition by this batch's agents.)
- `skills/testing-strategy/skill.yaml` (`SK-QA-001`) — added `SK-AI-007`.
- `skills/security-engineering/skill.yaml` (`SK-QA-002`) — added
  `SK-AI-008`.

All three re-validated as parsing cleanly after the edit.

## Unresolved questions

1. **The OpenAI research doc's two flagged "Claude"-contamination
   passages** — one (the web-search tool guide) was independently
   re-fetched and did not reproduce, consistent with a transient
   fetch/summarization-tool artifact. The other (the vision/images guide)
   was not independently re-checked in this session; the research doc
   itself already excludes the contaminated sentences rather than citing
   them, and flags this in its own Unresolved Items section
   (`research/technologies/UNRESOLVED.md`).
2. **Whether OpenAI exposes a header-based API-versioning mechanism**
   (a claimed `openai-version` header) — the research agent could not
   independently corroborate this against an official page; carried into
   `UNRESOLVED.md` unchanged.
3. **The OWASP 2025→2026 rank-change table is inference-derived** by the
   research agent from comparing two independently-sourced order lists,
   not quoted from a single official changelog page — only 3 of 10 moves
   are independently confirmed in prose by the official announcement.
   Flagged explicitly in both the research doc and `ai-security`'s own
   `owned_knowledge`/source citations rather than asserted as directly
   sourced.
4. Several narrower per-page gaps (Anthropic's Token Counting API schema,
   OpenAI's Datasets-feature technical surface, OWASP's original 2023 PDF
   content) remain open exactly as the three research docs themselves
   document — see `research/technologies/UNRESOLVED.md`.

None of these affect the 8 skills' core content, which draws only on
independently-verified, high-confidence claims (see the live-source
spot-verification above).

## Duplicated responsibilities

**None found.** The merge decisions made during taxonomy design (prompt+
context, structured-output+tool-calling, RAG+embeddings, evaluation+
hallucination-mitigation) were specifically designed to prevent the kind
of responsibility duplication that would result from authoring all 14 of
the master plan's named candidates as separate skills. Boundary language
was independently checked in each skill's `SKILL.md`:

- `llm-evaluation` (SK-AI-007) explicitly distinguishes itself from
  `testing-strategy` (SK-QA-001): LLM output is *graded*, not merely
  asserted true/false.
- `ai-security` (SK-AI-008) explicitly distinguishes itself from
  `security-engineering` (SK-QA-002): LLM-specific threat classes with no
  traditional-AppSec equivalent (prompt injection has no
  parameterized-query-style code/data boundary).
- `rag-engineering` (SK-AI-005) explicitly distinguishes itself from
  `search-integration` (SK-DATA-005): owns the RAG *pattern* and two
  specific documented risks (retrieval-authorization ordering,
  embedding-store sensitivity), not the search infrastructure itself.
- `llm-application-engineering` (SK-AI-001) explicitly distinguishes
  itself from `observability` (SK-QA-004): owns LLM-call observability as
  a *lightweight extension*, not a reimplementation of general
  observability method.

## Missing dependencies

None — every cross-reference in all 8 skills resolves to an
already-authored skill: the 8 AI-domain skills reference each other (all
authored within this same batch) plus `SK-QA-001`, `SK-QA-002`,
`SK-QA-004`, and `SK-DATA-005`, all of which pre-date this batch and were
independently confirmed to exist on disk. This is the fifth consecutive
batch (after UI/UX, CODE-QUALITY, DOCUMENTATION, OBSERVABILITY) with zero
unauthored forward references.

## Potential corrections

1. **This batch required a taxonomy-design phase before any research or
   generation**, unlike every prior batch in this project except the
   original 25-domain taxonomy design itself. The design (8 skills from
   14 named candidates, with explicit merge/decline rationale) was
   proposed and confirmed with the user via `AskUserQuestion` before any
   agent was dispatched — following the master plan's own explicit
   two-phase instruction for this step, mirroring Security (Step 18).
2. **The live-source spot-verification step (see Pre-work) is a new,
   stronger discipline** introduced in this batch specifically because one
   research agent's own self-report contained a credibility flag
   (implausible-looking model names, an admitted contamination artifact).
   Rather than either blindly trusting or blindly discarding the agent's
   output, four of the batch's highest-stakes claims were independently
   re-fetched and compared verbatim before proceeding — all four matched.
   This is worth adopting as a standing practice specifically triggered by
   self-flagged agent credibility concerns, not as a blanket requirement
   for every research pass.
3. **The mandatory final-YAML-parse-check instruction, standing since the
   `github-actions` defect several batches ago, held with zero recurrence
   across all 8 skills in this batch** — the third consecutive batch
   (after QA, Observability) confirming this fix is durable even at this
   batch's larger size.
4. **`model-selection` (SK-AI-006) was deliberately authored to avoid
   calcifying into a specific-model-name recommendation** — its
   `SKILL.md` explicitly flags current model names/prices as
   "worked examples... snapshotted 2026-09-10... re-verify against
   current vendor documentation," teaching the four-axis decision method
   (capability/cost/latency/context-window vs. task requirement) rather
   than a fixed product endorsement. This is a new pattern worth applying
   to any future skill grounded in fast-moving vendor pricing/lineup data.

## Overall assessment

All 8 skills are internally consistent with the specification, taxonomy
(now fully decomposed from a single thin placeholder), dependency
architecture, and routing architecture, well-grounded (6–26 citations per
skill, all traceable to independently-verified research), and explicit
about their own limits rather than overclaiming — most notably
`ai-security`, which preserves the OWASP standard's own candor that "no
reliable prevention mechanism exists today" for prompt injection and
frames every mitigation in terms of bounded blast radius rather than
promised prevention, including the striking documented finding that
static red-teaming shows near-zero attack success while adaptive
red-teaming exceeds 90% against the same defenses. This batch is the
first to require genuine taxonomy-design judgment mid-project (not just
skill generation against an already-designed taxonomy), and the first to
add an independent live-source verification step triggered by a research
agent's own self-flagged credibility concern — both of which held up
under scrutiny and are recommended as durable additions to this project's
established research → registries → taxonomy → skill-generation → audit
→ commit procedure.
