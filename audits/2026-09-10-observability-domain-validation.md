# Audit: OBSERVABILITY-domain skill generation & validation

Date: 2026-09-10. Scope: five skills — one generic (`SK-QA-004`
observability) and four technology skills (`SK-TECH-opentelemetry`,
`SK-TECH-prometheus`, `SK-TECH-grafana`, `SK-TECH-sentry`). Validated
against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).
This batch corresponds to **Step 23** of the project's master build plan
(`AI_Coding_Agent_Skill_Library_Complete_Step_By_Step.md`) and is the
**third** dedicated mid-project research pass in this library's history,
after Node.js (BACKEND-domain batch) — the first and, until now, only
prior instance of "hold a batch pending research, then close the gap
within the same batch."

**Scope note:** this batch was explicitly held one turn earlier when the
user's list ("Observability Architecture, Logging, Metrics, Tracing,
Error Monitoring, Reliability, Resilience") mapped entirely onto a
taxonomy-flagged research gap (`SK-QA-004`, originally "near-zero
grounding: only Docker log aggregation, OpenSearch log analytics"). When
the user later asked to complete the full master plan, they explicitly
chose to run the deferred research pass now rather than skip ahead. A
dedicated research pass on four technologies (OpenTelemetry, Prometheus,
Grafana, Sentry — the exact set named in the taxonomy's own "run a
dedicated research pass (e.g. OpenTelemetry, Prometheus, Grafana, Sentry)"
suggestion) closed the gap. **"Reliability" and "Resilience" remain
explicitly unresolved** — application-level resilience/fault-tolerance
patterns (retries, circuit breakers, timeouts, bulkheads) are a
genuinely distinct discipline from observability (visibility vs.
behavior-under-failure) with zero taxonomy presence, not even as a
flagged gap before this batch; this batch surfaced it as its own,
separately-tracked open item in `taxonomy-analysis.md` rather than folding
it into `SK-QA-004` or fabricating resilience-pattern guidance to fill it.

**Authorship note:** the generic skill was authored directly by hand,
grounded in the four new research docs' Core Concepts/Anti-Patterns
sections read across all four for cross-cutting synthesis (matching the
SECURITY/PERFORMANCE batches' pattern of reading full knowledge-map-
equivalent material rather than sampling). The four technology skills
were delegated to parallel agents with pre-verified relationship data and
pre-verified version/security/performance facts extracted directly from
the freshly-completed research, then independently re-verified on disk.

## Pre-work: dedicated research pass

Four new technology research docs were authored via four parallel agents,
matching the Node.js precedent's 17-dimension methodology exactly (same
citation-format convention, same closing-section structure):

| Technology | File | Lines | `[Source:]` citations |
|---|---|---|---|
| OpenTelemetry | `research/technologies/opentelemetry.md` | 335 | 82 |
| Prometheus | `research/technologies/prometheus.md` | 314 | 93 |
| Grafana | `research/technologies/grafana.md` | 348 | 82 |
| Sentry | `research/technologies/sentry.md` | 335 | 85 |

All four independently confirmed on disk (line counts, citation counts,
17-numbered-section structure, closing "Unresolved Items"/"Sources
Consulted" sections) — not accepted from agent self-reports alone. The
four registry files (`README.md`, `SOURCE_REGISTRY.md`,
`VERSION_REGISTRY.md`, `UNRESOLVED.md`) were then updated: `SOURCE_
REGISTRY.md`'s per-technology source lists were inserted at their correct
alphabetical positions and its domain-citation-count rollup table was
programmatically regenerated from the full, now-49-technology file rather
than hand-adjusted (confirmed 49 technology sections via script, matching
the expected 45+4 count exactly); `VERSION_REGISTRY.md` and
`UNRESOLVED.md` received hand-synthesized entries drawn directly from each
doc's own Version Information/Breaking Changes/Unresolved Items sections.
Prometheus was correctly **omitted** from `UNRESOLVED.md` — its research
doc has zero unresolved items, and the registry's own stated convention
is "technologies with no unresolved items are omitted," so no entry was
fabricated to keep the count even. `core/taxonomy/skill-catalog.md` and
`taxonomy-analysis.md` were both updated: `SK-QA-004`'s research-gap flag
was removed and replaced with a resolved-gap note plus the four new
`SK-TECH-*` catalog rows; the missing-capabilities table's Observability
row was marked Resolved and a new, separate Reliability/Resilience row
was added rather than conflating the two.

## Completed skills

| Skill | ID | Tier | Files | `[Source:]` citations |
|---|---|---|---|---|
| [observability](../skills/observability/) | SK-QA-004 | B | yaml, SKILL.md | 12 |
| [opentelemetry](../skills/opentelemetry/) | SK-TECH-opentelemetry | B | yaml, SKILL.md | 44 |
| [prometheus](../skills/prometheus/) | SK-TECH-prometheus | B | yaml, SKILL.md | 17 |
| [grafana](../skills/grafana/) | SK-TECH-grafana | B | yaml, SKILL.md | 36 |
| [sentry](../skills/sentry/) | SK-TECH-sentry | B | yaml, SKILL.md, 1 reference | 28 |

All five independently confirmed on disk (file existence, line counts) —
not accepted from any agent's self-report alone.

**Mechanical checks run and passed, all five (scripted, not manual):**
- YAML validity for all 5 `skill.yaml` files — all four delegated agents
  additionally ran the mandatory final YAML-parse-check themselves this
  time (a standing instruction added after the `github-actions` syntax
  defect two batches ago), and independent re-verification found zero
  syntax defects in any of the four — the first batch where every single
  delegated agent's own final-check claim held up cleanly.
- VR-1 (all always-required fields present, including `depends_on_skills`
  present-and-either-empty-or-populated, never omitted) — held across all
  four technology skills with no exceptions.
- CE-1 (description ≤ 500 chars) — **two of four technology skills
  (Grafana, Sentry) initially exceeded the 500-char limit during
  authoring (511 and 523 chars respectively) and were caught and fixed by
  the delegated agents themselves before reporting done**, not by this
  audit's own validation pass. This is the first batch where the CE-1
  defect class (previously caught only by this project's own post-hoc
  script, e.g. in the DOCUMENTATION batch) was caught and self-corrected
  by the authoring agents directly.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically, zero mismatches across all five.
- **`depends_on_skills`-vs-`parents` conflation: zero recurrence**,
  extending the now-long streak across every technology skill in this
  batch (`parents: [SK-QA-004]` for all four, `depends_on_skills: []` for
  all four, correctly separated).
- VR-3 (every `parents`/`related_skills`/`conflicts_with`/
  `depends_on_skills` ID resolves to a real, now-updated taxonomy entry)
  — all resolve cleanly, including the four new `SK-TECH-*` catalog rows
  added as part of this same batch's taxonomy update.
- Conflict-cluster check: **zero `conflicts_with` entries across all four
  technology skills** — correct and deliberate: OpenTelemetry,
  Prometheus, Grafana, and Sentry are documented as composing WITH each
  other (OTel is the vendor-neutral instrumentation layer; Prometheus/
  Grafana are the metrics-storage-and-visualization pair; Sentry is a
  distinct error/trace/session product surface with its own JS SDK
  running on OTel internally since v8) rather than competing for the same
  architectural slot — the same "don't invent a conflict where the
  research shows composition, not competition" discipline established in
  REALTIME/SEARCH/INFRA/CONV-INFRA, now confirmed symmetric and correct
  across all six possible pairs in a four-technology cluster, the largest
  such cluster tested in this project.
- All relative links resolve.

## Unresolved questions

1. **OpenTelemetry's exact current-release calendar dates could not be
   confirmed** — GitHub release-page fetches returned apparently-
   inconsistent years across separate tool calls during research; the
   skill states version numbers with this uncertainty flagged explicitly
   rather than asserting fabricated dates.
2. **No dedicated official OpenTelemetry instrumentation-testing guide
   was found** beyond one Node.js-specific page checked (which itself
   doesn't cover testing) — stated as a real gap, not papered over.
3. **Grafana's "LGTM stack" acronym (Loki/Grafana/Tempo/Mimir) was not
   found verbatim anywhere in official grafana.com/docs pages** despite
   the underlying four-component architecture being fully documented
   under the OpenTelemetry/OTLP ingestion pages — the skill correctly
   describes the components explicitly rather than treating the acronym
   as resolving to an official docs anchor.
4. **Sentry's exact default server-side PII-scrubbing field list, and any
   Python SDK migration-guide history, were not located** — both stated
   as documented gaps in the skill rather than inferred from the (fully
   documented) JS SDK equivalents.
5. **No consolidated SDK×runtime×framework compatibility matrix exists
   for Sentry**, and **no numeric SDK performance-overhead benchmarks
   exist for either Sentry or OpenTelemetry** — both stated honestly
   rather than backfilled with invented numbers.

None of these five were load-bearing enough to block any skill — each is
a correctly-surfaced boundary of the freshly-completed research, carried
forward faithfully from the research docs' own "Unresolved Items"
sections rather than resolved by guessing.

## Duplicated responsibilities

**None found**, despite this batch having the highest technology-skill
count (four) sharing a single generic parent since FRONTEND's five-
sibling React/Vue/Angular/Next.js/Nuxt cluster, and despite genuine
content-overlap risk given all four technologies touch overlapping
observability concerns:

- All four technology skills explicitly declined to repeat
  `observability`'s cross-cutting synthesis (signal-selection method,
  the independently-converging high-cardinality anti-pattern across
  Prometheus/OpenTelemetry, PII-scrubbing discipline, alert-design
  method), adding only their own technology-specific implementation
  mechanics.
- `prometheus` and `grafana` — despite Grafana's own docs citing
  Prometheus extensively and the parent citing both — each covered their
  own side of the relationship without restating the other's content
  (Prometheus's skill covers its own OTLP receiver and Grafana data-
  source registration from Prometheus's side; Grafana's skill covers
  its own Prometheus-datasource mechanics and unified-alerting-vs-
  Prometheus-Alertmanager distinction from Grafana's side).
- `sentry`'s skill states its unusually deep OpenTelemetry relationship
  (the JS SDK runs on OTel internally since v8) precisely, without
  restating OpenTelemetry's own architecture already covered in the
  `opentelemetry` skill.

## Missing dependencies

None — every cross-reference in all five skills resolves to an
already-authored skill (all four technology skills reference each other,
all authored within this same batch; the generic references already-
authored `SK-QA-003`/`SK-INFRA-003`). This is the fourth consecutive
batch (after UI/UX, CODE-QUALITY, DOCUMENTATION) with zero unauthored
forward references.

## Potential corrections

1. **This batch closes the third of this project's dedicated mid-project
   research passes** (Node.js in BACKEND; implicitly, the taxonomy/
   registry-update choreography from that pass was replicated here nearly
   exactly — research → registries → taxonomy → skill generation → audit
   → commit — confirming that sequence is now a settled, reusable
   procedure for any future taxonomy gap, not something to re-derive each
   time).
2. **The mandatory final-YAML-parse-check instruction, standing since the
   prior batch's `github-actions` defect, held with zero recurrence across
   all four technology skills in this batch** — the second consecutive
   batch (after QA) confirming this fix is durable.
3. **Two agents self-corrected a CE-1 description-length overage before
   reporting done**, rather than this audit's own script catching it
   post-hoc (as happened in the DOCUMENTATION batch). Worth continuing to
   include the explicit description-length reminder in future delegation
   prompts, since it appears to reliably prompt agents to self-check this
   specific field.
4. **The "don't invent a conflict where the research shows composition"
   discipline was tested at its largest scale yet** (four technologies,
   six possible pairs) and held cleanly — worth treating as conclusively
   settled at this point rather than a per-batch judgment call.
5. **The Reliability/Resilience gap is now explicitly tracked as its own,
   separately-named open item** in `taxonomy-analysis.md`, distinct from
   the now-resolved Observability gap — this is a template worth
   following whenever a user's request straddles a resolved gap and an
   adjacent-but-distinct unresolved one, rather than either conflating
   the two or silently dropping the unresolved half.
6. **No skill in this batch was promoted to `final/`** — same standing
   gap as all sixteen prior batches.

## Overall assessment

All five skills are internally consistent with the specification,
taxonomy (now updated to reflect the resolved research gap), dependency
architecture, and routing architecture, well-grounded (12–44 citations
per skill), and version-aware — including several genuinely load-bearing
findings correctly surfaced rather than flattened: OpenTelemetry's per-
language-per-signal stability matrix (JS/Python have Stable traces/
metrics but NOT-yet-stable logs — a real, easy-to-miss caveat for this
library's own heavily-JS/Python-weighted technology set); Prometheus's
TSDB v2.55 read-compatibility boundary and its explicit "not clustered/
not HA natively" architectural stance; Grafana's v13.0.0 dashboard/folder
data-loss migration-risk bug and the real distinction between its
embedded Alertmanager and an external one; and Sentry's Metrics-API
removal in v9 (the strongest evidence it is not a Prometheus-style
platform) alongside its unusually deep, load-bearing OpenTelemetry
dependency. This batch is the clearest evidence yet that this project's
"hold a batch, run dedicated research, then close it properly" procedure
(first proven with Node.js) generalizes cleanly to a multi-technology gap
(four technologies at once, not one), and that the standing disciplines
accumulated across fifteen prior batches — mandatory YAML self-checks,
explicit depends_on_skills warnings, "don't invent a conflict" — continue
to hold without degradation as batch complexity grows.
