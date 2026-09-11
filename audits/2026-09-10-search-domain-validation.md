# Audit: SEARCH-domain skill generation & validation

Date: 2026-09-10. Scope: two skills — one generic (`SK-DATA-005`
search-integration) and one technology skill (`SK-TECH-opensearch`).
Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).

**Scope note:** the user's 5-item list ("Search Architect, OpenSearch,
Indexing, Search Relevance, Search Performance") maps to 2 skills, not 5 —
"Search Architect," "Indexing," and "Search Relevance" are all explicitly
named as the purpose/responsibilities of the single taxonomy-defined generic
skill `SK-DATA-005` (search-integration: "full-text and/or vector/semantic
search — indexing, mapping, relevance, and the engine choice"). "Search
Performance" was likewise folded into `SK-DATA-005`'s scope (search-specific
performance tuning) rather than deferred to the not-yet-authored
`SK-QA-002` (performance-engineering), per the user's explicit choice
between the two options offered. "OpenSearch" maps to the technology
specialization, `SK-TECH-opensearch`. Confirmed via `AskUserQuestion`
("Yes, proceed with 2") rather than assumed — the largest single-batch
collapse of this project so far (5 items → 2 skills, vs. 2→1 for HTML+CSS
and API-Architect+REST in earlier batches).

**Authorship note:** as with all five prior batches, the generic skill was
authored directly by hand; the technology skill was delegated to a single
agent with pre-verified relationship data (`parents`, `conflicts_with`,
`related_skills`) and pre-verified version/security/performance facts
pulled from `version-matrix.md`/`technology-decision-matrix.md`/
`security-knowledge-map.md`/`performance-knowledge-map.md`/
`integration-map.md`/`concept-knowledge-map.md`, then independently
re-verified on disk (not trusted from the self-report alone).

## Completed skills

| Skill | ID | Tier | Files | Citations in SKILL.md |
|---|---|---|---|---|
| [search-integration](../skills/search-integration/) | SK-DATA-005 | B | yaml, SKILL.md | 3 |
| [opensearch](../skills/opensearch/) | SK-TECH-opensearch | B | yaml, SKILL.md | 36 |

Both independently confirmed on disk (file existence, line counts) — not
accepted from the agent's self-report alone.

**Mechanical checks run and passed, both (scripted, not manual):**
- YAML validity for both `skill.yaml` files.
- VR-1 (all always-required fields present) and technology-conditional
  fields (`parents`, `covered_versions`, `version_sensitive_claims`,
  `reverify_triggers`) present for `opensearch`.
- CE-1 (description ≤ 500 chars) — 442 (search-integration) and 486
  (opensearch); the latter is a repeat of the standing note from the last
  two batches to leave more headroom.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically, zero mismatches.
- **`depends_on_skills`-vs-`parents` conflation: zero recurrence**, the
  fourth consecutive batch (after BACKEND, FRONTEND, REALTIME) where the
  technology skill correctly left `depends_on_skills: []` with
  specialization captured only in `parents: [SK-DATA-005, SK-QA-004]`.
- VR-3 (every `parents`/`related_skills`/`conflicts_with` ID resolves to a
  real taxonomy entry) — all resolve cleanly, including the forward
  reference to `SK-QA-004` (observability, a research-gap skill).
- `conflicts_with: []` for `opensearch` — correct per the research: it is
  the *only* search engine actually profiled in this library
  (Elasticsearch has no first-party data at all, named only via
  OpenSearch's own migration-assistant docs and an unconfirmed
  fork-lineage inference) — same "don't invent a conflict with an
  unresearched technology" discipline the REALTIME batch established.
- `execution_tier`/`required_capabilities` consistency: both Tier B with
  `shell` — correct, since both search-integration design work and
  OpenSearch cluster operation are runtime/shell-execution-adjacent
  (unlike e.g. the frontend authoring-only skills).
- The agent correctly removed its pre-created empty `references/`
  directory rather than leaving an unused artifact, since no genuinely
  substantial Tier-2 material was needed.
- All relative links resolve.

## Unresolved questions

1. **OpenSearch's JVM-heap-sizing guidance (50% of RAM, `-Xms`=`-Xmx`,
   ~32GB ceiling)** — the source knowledge-map itself flags this as an
   inference from `opensearch.md`, not an explicit doc statement verified
   verbatim. The skill correctly carries this exact caveat forward
   ("documented guidance, though the exact source page wasn't
   independently re-verified verbatim") rather than stating it with false
   certainty.
2. **OpenSearch's testing story outside the JVM ecosystem** —
   `opensearch-testcontainers` (JUnit 4/5) is the only documented testing
   integration found; the skill correctly states the research is silent on
   non-JVM test-container equivalents (e.g. for Python/Node) rather than
   inventing one.
3. **`search-integration`'s Elasticsearch gap** — carried forward from the
   decision-matrix's own "no first-party Elasticsearch data exists in this
   dataset" flag; both skills state this plainly rather than filling the
   gap with general knowledge.

None of these three were load-bearing enough to block either skill — each
is a correctly-surfaced boundary of current research.

## Duplicated responsibilities

**None found.** `opensearch` explicitly declined to repeat
`search-integration`'s engine-selection decision framework (DB-native FTS
vs. dedicated engine vs. vector search) or its Elasticsearch-research-gap
caveat, adding only OpenSearch-specific implementation depth (cluster/
mapping/analyzer mechanics, the full security-plugin auth/access-control
surface, concrete shard-sizing and JVM-tuning parameters, the three-tier
version-lifecycle). This is a smaller-surface-area version of the pattern
established across all four prior batches (generic parent owns the
comparison/decision framework; technology skill adds implementation depth
without restating it) — here tested with only one technology skill instead
of a sibling group, so there was no cross-sibling duplication risk to begin
with.

## Missing dependencies

- `opensearch` forward-references `SK-QA-004` (observability) as its
  second formal parent — `SK-QA-004` is an explicit, documented
  research-gap skill in this library's taxonomy (no APM/tracing technology
  beyond OpenSearch's own log-analytics use case has been researched), not
  an oversight. Handled correctly as a non-fabricated forward reference,
  consistent with how prior batches handled forward references to
  research-gap skills (e.g. `python`→`SK-AI-001` in the BACKEND batch).
- `search-integration` forward-references `SK-DATA-003`
  (database-operations, in `non_activation_conditions`) and `SK-AI-001`
  (llm-application-engineering, in `related_skills`) — both unauthored.
  `SK-DATA-003` is a taxonomy gap left over from the DATA-domain batch
  (which authored `SK-DATA-001`/`002`/`005`/`006` but not `003`/`004`);
  `SK-AI-001` is the same documented research-gap skill referenced by the
  BACKEND batch's `python` skill. Neither reference fabricates content for
  the missing skill.

## Potential corrections

1. **The `depends_on_skills`-vs-`parents` fix continues to hold with zero
   recurrence** across a fourth consecutive batch. No further spec action
   needed.
2. **The "don't invent a conflict with an unresearched technology"
   discipline extended cleanly from REALTIME's transport triad to a
   single-technology case** — OpenSearch correctly declared no conflict
   with the unresearched Elasticsearch, the same discipline applied even
   though there's no sibling technology skill in this batch to compare
   against.
3. **This batch's mapping collapse (5 user-list items → 2 skills) is the
   largest yet** and was correctly caught before generation via
   `AskUserQuestion` rather than after — worth noting as reinforcement that
   the taxonomy-mapping-confirmation step continues to earn its keep as
   the list-collapse ratio grows across batches.
4. **`SK-DATA-003` (database-operations) and `SK-DATA-004`
   (caching-strategy) remain gaps in the DATA domain**, left over from the
   original DATA-domain batch, which authored only 001/002/005 (now)/006 of
   the six generic DATA skills in the taxonomy. Not blocking anything in
   this batch (both are only referenced as non-fabricated forward
   references), but worth surfacing for a future DATA-domain follow-up
   batch if the user wants those two gaps closed.
5. **No skill in this batch was promoted to `final/`** — same standing gap
   as all five prior batches (no executable validator or `evaluations/`
   tests yet).

## Overall assessment

Both skills are internally consistent with the specification, taxonomy,
dependency architecture, and routing architecture, well-grounded (3
citations for the generic — appropriately light, since its content is
decision-framework/synthesis-heavy rather than citation-dense — and 36 for
the technology skill), and version-aware, including genuinely load-bearing
findings correctly surfaced rather than flattened: OpenSearch's three-tier
support lifecycle (1.x EOL, 2.x maintenance-only through 2026 with a
concrete 60-day vulnerability-patch SLA, 3.x actively developed); the
demo-TLS-certificate production risk stated with exact file-mode detail
(`600`/`644`); the shard-sizing trade-off table tied to workload shape; and
the JVM-heap-guidance inference correctly flagged as lower-confidence
rather than asserted outright. The batch also reinforced two patterns from
recent audits: surfacing a large taxonomy-mapping collapse via
`AskUserQuestion` before generating anything (this time 5→2, the largest
yet), and declining to manufacture a `conflicts_with` relationship with an
unresearched competing technology (Elasticsearch) even under no
cross-sibling pressure to do so.
