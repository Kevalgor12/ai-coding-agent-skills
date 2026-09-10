# Audit: SEO-domain skill generation & validation

Date: 2026-09-10. Scope: one skill, generic — `SK-GROW-001`
seo-optimization. Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).

**Scope note:** the user's 6-item list ("SEO Architecture, Technical SEO,
Next.js SEO, Structured Data, Crawlability, Performance SEO") maps to 1
skill — the largest proportional collapse yet in this project (6→1,
surpassing SEARCH's 5→2 and SECURITY's 8→2). The taxonomy has exactly one
SEO skill, `SK-GROW-001` seo-optimization, already unified with
`SK-TECH-google-seo` at the taxonomy-design stage (Google is the dominant
search engine in this library's research, so the generic and the
Google-SEO technology content were merged into one skill rather than split
— the same unification pattern already applied to Docker/GitHub-Actions in
earlier batches). "SEO Architecture," "Technical SEO," "Structured Data,"
"Crawlability," and "Performance SEO" all collapsed into it directly — each
is a named responsibility in its own taxonomy entry ("indexability,
structured data, canonicalization, Core Web Vitals, sitemaps, i18n
hreflang"). "Next.js SEO" had no separate taxonomy entry either; Next.js's
own SEO-relevant mechanics (Metadata API, sitemap/robots generation) were
folded in as additional grounding within this same skill rather than
spun out, consistent with how the research itself treats it (one line in
Next.js's production checklist, not an independently deep methodology).
Confirmed via `AskUserQuestion` ("Yes, proceed with 1") rather than
assumed.

**Authorship note:** as with SECURITY and PERFORMANCE, this batch contains
**no separate technology skill to delegate** — the taxonomy's own merge
decision means Google-SEO's technology-level content lives inside this
same generic skill rather than a paired `SK-TECH-*` skill. Authored
directly by hand, grounded in `research/technologies/google-seo.md` (read
in full — a document explicitly scoped as covering a documented set of
requirements/guidelines rather than versioned software, per its own
framing note) plus the SEO-relevant excerpt of `research/technologies/
nextjs.md`'s production checklist.

## Completed skills

| Skill | ID | Tier | Files | Citations in SKILL.md |
|---|---|---|---|---|
| [seo-optimization](../skills/seo-optimization/) | SK-GROW-001 | A | yaml, SKILL.md | 12 |

Independently confirmed on disk (file existence, line count) —
self-authored by hand; YAML validity and field-presence checks were still
run and passed, consistent with the discipline established for
self-authored work in the SECURITY and PERFORMANCE batches.

**Mechanical checks run and passed (scripted, not manual):**
- YAML validity for `skill.yaml`.
- VR-1 (all always-required fields present, including
  `depends_on_skills` present-and-empty).
- CE-1 (description ≤ 500 chars) — well within range.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically.
- VR-3 (every `related_skills`/`conflicts_with` ID resolves to a real
  taxonomy entry) — all resolve cleanly, including forward references to
  `SK-GROW-002` (web-monetization, unauthored) and `SK-FE-005`
  (rendering-strategy, unauthored, the same standing gap noted across
  several prior FRONTEND-adjacent batches), and a reference to the
  already-authored `SK-TECH-nextjs`.
- `depends_on_skills: []` — correct; this skill hands off to
  performance-engineering (Core Web Vitals depth) and rendering-strategy
  (rendering-mode decision) via `related_skills` only, with no hard
  sub-step composition.
- `execution_tier: A` matches the taxonomy's own "A / C (browser
  verification)" dual-tier note — resolved the same way as
  `web-accessibility` (FRONTEND batch) and `deployment-release` (INFRA
  batch): the primary tier (A, advisory/authoring) is encoded in
  `execution_tier`, and the secondary Tier-C constraint (browser-based
  verification of rendered-DOM content, not guaranteed available in every
  agent environment) is stated in prose (Testing/Failure-handling
  sections) rather than a second YAML field.
- All relative links resolve.

## Unresolved questions

1. **HTTPS's exact ranking-signal weight could not be independently
   verified** from current official Search Central copy in this
   library's research — only its role as one signal among several in
   canonical-selection is confirmed. The skill states this explicitly as
   unresolved rather than asserting a specific "HTTPS boosts ranking by
   X%"-style claim, which would have been fabricated.
2. **Whether the INP-replaces-FID transition still carries an explicit
   "breaking change" migration notice in current official copy is
   unconfirmed** — the live Core Web Vitals page presented INP as current
   with no visible migration callout in this research pass; the skill
   states the historical fact (FID replaced by INP, March 2024,
   industry-wide) without asserting Google's docs still frame it as a
   migration notice.
3. **The exact current numeric quota for the Indexing API's onboarding/
   testing tier is unconfirmed** — described only qualitatively in the
   official page fetched during research, with a WebSearch-derived figure
   of "200" that could not be independently verified against primary
   text. Not surfaced in the authored skill at all since it wasn't
   load-bearing for the skill's core scope (crawlability/structured-data/
   canonicalization/Core-Web-Vitals/sitemaps/hreflang), but worth noting
   as a boundary of the underlying research.
4. **No dedicated official "site move / domain migration" guide page was
   located** during the underlying research pass — only the
   canonicalization/redirect signals relevant to migration were directly
   confirmed. The skill's Escalation section flags migration-adjacent
   changes for explicit confirmation partly because of this documented
   grounding gap, not just general caution.

None of these four were load-bearing enough to block the skill.

## Duplicated responsibilities

**None found**, and this is notable given SEO work naturally intersects
performance (Core Web Vitals) and frontend-rendering concerns that already
have their own skills: `seo-optimization` explicitly defers Core Web
Vitals *measurement/optimization* depth to
[performance-engineering](../skills/performance-engineering/SKILL.md)
(authored in the immediately prior batch), tracking only the ranking-
relevant thresholds themselves as targets. It explicitly defers the
rendering-mode decision to rendering-strategy (not yet authored) rather
than re-deriving SSR-vs-CSR trade-offs already partially covered by
`frontend-architecture` (FRONTEND batch). Its Next.js-specific content is
scoped narrowly to what Next.js's own docs say about SEO/metadata
specifically (Metadata API, sitemap/robots generation), explicitly
declining to restate `nextjs`'s own already-authored technology-skill
content on rendering/caching/App-Router mechanics.

## Missing dependencies

- `seo-optimization` references `SK-GROW-002` (web-monetization,
  unauthored — a taxonomy entry itself flagged "thin" in the catalog) and
  `SK-FE-005` (rendering-strategy, unauthored — the same standing gap
  referenced by `frontend-architecture`, `react`, `nuxt`, and several
  other FRONTEND-batch skills across multiple prior audits) in
  `related_skills`. `SK-TECH-nextjs` is already authored.

Neither unauthored reference fabricates content for the missing skill;
both are consistent, non-fabricated forward references.

## Potential corrections

1. **This is the third consecutive batch with zero technology-skill
   delegation** (after SECURITY and PERFORMANCE), and the second batch
   (after Docker/GitHub-Actions-style unifications in earlier batches)
   where the *reason* is a taxonomy-level generic+technology merge rather
   than the concern being purely cross-cutting with no tech specialization
   at all. Worth distinguishing the two reasons going forward: "no
   technology skill exists because the concern is cross-cutting"
   (SECURITY, PERFORMANCE) vs. "no *separate* technology skill exists
   because it was deliberately unified with the generic at the taxonomy-
   design stage" (this batch) — both produce the same "no delegation
   needed" batch shape, but for different underlying reasons worth keeping
   distinct in future audits.
2. **The dual-tier catalog resolution pattern (`A / C` → encode A, state C
   in prose) has now been applied three times** across three different
   domains (`web-accessibility` in FRONTEND, `deployment-release` in
   INFRA, `seo-optimization` here) with the same resolution each time —
   confirms this is a settled, reusable pattern rather than a one-off
   judgment call.
3. **This batch's citation density (12) is lower than most single-skill
   technology batches but appropriate given its content** — the skill's
   grounding is genuinely broad-but-shallow-per-claim by nature of the
   source material itself (a set of documented guidelines/policies rather
   than a deep technical API surface), and several of its most important
   statements are structural/definitional (the crawl-render-index
   pipeline, robots.txt-vs-noindex, canonical-as-hint) rather than
   individually-citable facts requiring a citation per sentence — no
   correction needed, just noting the pattern for future single-skill
   batches grounded in a similarly policy-shaped research document.
4. **No skill in this batch was promoted to `final/`** — same standing
   gap as all eleven prior batches.

## Overall assessment

The skill is internally consistent with the specification, taxonomy,
dependency architecture, and routing architecture, well-grounded (12
citations spanning the full crawl/render/index pipeline, structured-data
formats, canonicalization signals, sitemap limits, hreflang, Core Web
Vitals thresholds, and named spam policies), and appropriately honest
about the two different depths of its two source documents — deep,
well-organized coverage from `google-seo.md`'s dedicated 17-section
research pass, versus a single, explicitly-flagged-as-thin line of
Next.js-specific SEO guidance rather than an inflated claim of deep
framework-specific research. The skill surfaces several genuinely
load-bearing, easy-to-conflate distinctions correctly: robots.txt
(prevents crawling) vs. `noindex` (prevents indexing while still
allowing crawling); the crawl→render→index pipeline's sequencing as the
root cause of most JS-SEO bugs (Google indexes the rendered DOM, not the
raw server response); canonical signals as a hint Google can override, not
an enforced rule; and the "scaled content abuse" spam-policy category's
explicit inclusion of AI-generated low-value content at scale — a directly
relevant, dated policy fact for any AI-assisted content workflow this
library's own users might otherwise walk into unknowingly. This batch also
extends the now-three-times-applied dual-tier `execution_tier` resolution
pattern and the third consecutive "no technology-skill delegation needed"
batch, for a taxonomy-merge reason distinct from the two immediately
preceding batches' cross-cutting reason.
