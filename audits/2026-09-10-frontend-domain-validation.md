# Audit: FRONTEND-domain skill generation & validation

Date: 2026-09-10. Scope: thirteen skills — two generic (`SK-FE-001`
frontend-architecture, `SK-FE-004` web-accessibility) and eleven technology
skills (`SK-TECH-react`, `SK-TECH-nextjs`, `SK-TECH-vue`, `SK-TECH-nuxt`,
`SK-TECH-angular`, `SK-TECH-typescript`, `SK-TECH-web-standards`,
`SK-TECH-sass`, `SK-TECH-tailwindcss`, `SK-TECH-mui`, `SK-TECH-shadcn-ui`).
Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).

**Scope note:** the user's 13-item list ("Frontend Architect, React, Next.js,
Vue, Nuxt, Angular, TypeScript, HTML, CSS, Sass, Tailwind, MUI, shadcn/ui,
Accessibility") maps to 13 skills, not 14 — HTML and CSS collapse to the
single taxonomy-merged `SK-TECH-web-standards`, confirmed by the user
("Yes, proceed with 13") rather than assumed.

**Authorship note:** as with the three prior batches, the two generic skills
were authored directly by hand; the eleven technology skills were delegated
to parallel agents with pre-verified relationship data (`parents`,
`conflicts_with`, `related_skills`) and pre-verified version facts pulled
from `version-matrix.md`/`technology-decision-matrix.md`, then independently
re-verified on disk (not trusted from self-reports).

## Completed skills

| Skill | ID | Tier | Files | Citations in SKILL.md |
|---|---|---|---|---|
| [frontend-architecture](../skills/frontend-architecture/) | SK-FE-001 | A | yaml, SKILL.md, 1 reference | 6 |
| [web-accessibility](../skills/web-accessibility/) | SK-FE-004 | A | yaml, SKILL.md | 10 |
| [react](../skills/react/) | SK-TECH-react | B | yaml, SKILL.md | 32 |
| [nextjs](../skills/nextjs/) | SK-TECH-nextjs | B | yaml, SKILL.md | 34 |
| [vue](../skills/vue/) | SK-TECH-vue | B | yaml, SKILL.md, 1 reference | 48 |
| [nuxt](../skills/nuxt/) | SK-TECH-nuxt | B | yaml, SKILL.md | 22 |
| [angular](../skills/angular/) | SK-TECH-angular | B | yaml, SKILL.md | 47 |
| [typescript](../skills/typescript/) | SK-TECH-typescript | B | yaml, SKILL.md, 1 reference | 29 |
| [web-standards](../skills/web-standards/) | SK-TECH-web-standards | A | yaml, SKILL.md | 39 |
| [sass](../skills/sass/) | SK-TECH-sass | A | yaml, SKILL.md, 1 reference | 31 |
| [tailwindcss](../skills/tailwindcss/) | SK-TECH-tailwindcss | A | yaml, SKILL.md, 1 reference | 41 |
| [mui](../skills/mui/) | SK-TECH-mui | A | yaml, SKILL.md, 1 reference | 40 |
| [shadcn-ui](../skills/shadcn-ui/) | SK-TECH-shadcn-ui | B | yaml, SKILL.md | 27 |

All thirteen independently confirmed on disk (file existence, line counts,
directory contents) — not accepted from agent self-reports alone.

**Mechanical checks run and passed, all thirteen (scripted, not manual):**
- YAML validity for all 13 `skill.yaml` files.
- VR-1 (all always-required fields present) and technology-conditional
  fields (`parents`, `covered_versions`, `version_sensitive_claims`,
  `reverify_triggers`) present for all 11 technology skills.
- CE-1 (description ≤ 500 chars) — range 331–499; four skills
  (`nextjs`, `typescript`, `web-standards`, `tailwindcss`) landed within 9
  chars of the ceiling, compliant but worth noting for future batches to
  leave more headroom.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically for all 13, zero mismatches.
- **`depends_on_skills`-vs-`parents` conflation: zero recurrence**, the
  second consecutive batch (after BACKEND) where every technology skill
  correctly left `depends_on_skills: []` with specialization captured only
  in `parents` — confirmed by direct YAML inspection, not agent claims. The
  specification fix from the DATA-domain batch continues to hold.
- Conflict-cluster symmetry, checked programmatically: the
  `react`⊥`vue`⊥`angular` frontend-framework triangle, `nextjs`⊥`nuxt`
  meta-framework pair, and `mui`⊥`shadcn-ui` component-library pair are all
  symmetric — no one-directional conflicts found.
- VR-3 (every `parents`/`related_skills`/`conflicts_with` ID resolves to a
  real taxonomy entry) — **found and fixed one pre-existing taxonomy defect
  in the process** (below); all references resolve after the fix.
- `execution_tier`/`required_capabilities` consistency: 7 Tier B skills
  (react, nextjs, vue, nuxt, angular, typescript, shadcn-ui) with `shell`
  capability for build/CLI tooling; 6 Tier A skills (frontend-architecture,
  web-accessibility, web-standards, sass, tailwindcss, mui) as
  authoring/config skills with no fundamental shell dependency. `shadcn-ui`
  is correctly Tier B (its CLI is the primary interaction surface, unlike
  MUI's plain-install model) — this asymmetry between two otherwise-similar
  component-library skills is intentional, not an inconsistency.
- All relative links resolve.

### Taxonomy defect found and fixed

`core/taxonomy/skill-catalog.md`'s master technology table (§ tech-skill
catalog) still listed **two separate rows** — `SK-TECH-html` and
`SK-TECH-css` — annotated as "merged... see analysis," while
`taxonomy-analysis.md` §"Skills to merge" and two other cross-references
elsewhere in `skill-catalog.md` itself (the styling-systems and
web-accessibility generic-skill entries) already referenced the single
merged ID `SK-TECH-web-standards` as if it were canonical. This is a
pre-existing inconsistency from the taxonomy-design phase (predates this
batch), not an error introduced by any agent in this batch — the agents
correctly used `SK-TECH-web-standards`, consistent with the analysis
document and the majority of existing cross-references.

**Fix applied** (following this project's established "fix the source
document, not just the instance" pattern — same approach used for the
`depends_on_skills`/`parents` conflation): consolidated the two-row table
entry into a single `SK-TECH-web-standards` row, and corrected the one
stale `SK-TECH-html` reference in the `SK-FE-004` catalog entry's "Related"
list to `SK-TECH-web-standards`. Verified via cross-reference script that
all IDs across the full skill set now resolve.

## Unresolved questions

1. **Vue Router's v5.x status** — referenced only via an AI-summarized
   source extraction in `research/technologies/vue.md`, not a raw version
   table; the `vue` skill correctly marked this "Unresolved" rather than
   asserting it, both inline and in `version_sensitive_claims`.
2. **The Tailwind `@config`/`@plugin` legacy-JS-config bridge's gap**
   (does not support `corePlugins`/`safelist`/`separator`) — unconfirmed
   whether any 4.x patch after 4.0.0 closed this; flagged as a
   `reverify_trigger` in the `tailwindcss` skill rather than guessed at.
3. **TypeScript 7.1's Compiler API shape** — TypeScript 7.0 shipped with
   *no* programmatic Compiler API at all (a major, easy-to-miss fact,
   correctly surfaced prominently across Knowledge/Decision-framework/
   Anti-patterns/Performance in the `typescript` skill); 7.1's promised
   "completely different API" is unreleased and unspecified, correctly
   flagged as a `reverify_trigger` rather than speculated on.
4. **Angular's per-minor TypeScript-floor stability** — whether the
   `>=6.0.0 <6.1.0` window for Angular 22.0.x widens in later 22.x minors
   was not independently confirmed against `angular.dev/reference/versions`;
   flagged in the `angular` skill's unresolved list.
5. **Next.js's August 2026 security release CVE identifiers** — sourced
   only from a WebSearch summary in `research/technologies/nextjs.md`, not
   a direct advisory-page fetch; the `nextjs` skill states the fixed
   versions (16.3.3/15.5.24) without asserting unverified CVE IDs.
6. **Sass and LibSass's exact EOL date** — search-summarized (~October
   2025), not independently re-fetched; flagged as a `reverify_trigger` in
   the `sass` skill rather than stated as settled fact.

None of these six were load-bearing enough to block any skill — each is
correctly marked as a boundary of current research rather than papered over
with an invented answer, consistent with this project's source-grounding
discipline.

## Duplicated responsibilities

**None found at the engineering-content level.** The batch's structure
made duplication risk unusually high — three framework triples (React/Vue/
Angular; Next.js/Nuxt; MUI/shadcn-ui) sharing a comparison space — and every
skill correctly deferred instead of restating:

- `react`, `vue`, and `angular` all explicitly declined to repeat
  `frontend-architecture`'s existing React-vs-Vue-vs-Angular comparison
  (security-posture defaults, CVE profile, compiler story, test-runner
  recommendation), adding only framework-specific implementation depth
  (hooks/RSC mechanics for React; Composition API/SFC/reactivity-model split
  for Vue; DI/standalone-components/signals for Angular).
- `nextjs` and `nuxt` both declined to repeat `frontend-architecture`'s
  existing Next.js-vs-Nuxt comparison, adding only meta-framework-specific
  depth (App Router/Cache Components for Next.js; Nitro/routeRules for
  Nuxt).
- `mui` and `shadcn-ui` — since neither is a formal parent of the other —
  each lightly cited the shared `technology-decision-matrix.md` §8
  comparison rather than one restating the other's content, a different but
  equally sound resolution to the duplication risk given neither skill
  "owns" the pairing the way frontend-architecture owns the framework
  comparisons.
- `web-standards` explicitly deferred all accessibility-specific content to
  `web-accessibility` (which was authored first and already owns the
  semantic-HTML-for-a11y guidance), keeping its own scope to the broader
  HTML/CSS technology knowledge.
- `sass` and `tailwindcss` each stated the Sass/Tailwind-v4-incompatibility
  nuance precisely (a narrow, real technical incompatibility) without
  encoding it as a skill-level `conflicts_with`, consistent with this
  project's own dependency-architecture decision that the two are not
  alternatives at the skill level.

## Missing dependencies

Every technology skill in this batch forward-references at least one
not-yet-authored generic parent — this is expected and consistent with
prior batches (BACKEND was the first and only batch so far where all formal
parents already existed):

- `SK-FE-005` (rendering-strategy) — referenced by all 5 framework skills
  plus the two meta-framework skills (react, vue, angular, nextjs, nuxt).
- `SK-GROW-001` (seo-optimization) — referenced by nextjs, nuxt.
- `SK-FE-003` (styling-systems) — referenced by web-standards, sass,
  tailwindcss, mui, shadcn-ui.
- `SK-FE-002` (ui-ux-design) — referenced by mui, shadcn-ui.
- `SK-CONV-003` (code-quality) — referenced by typescript as its sole
  formal parent (a deliberate taxonomy positioning: TypeScript is a
  cross-cutting language-quality concern, not a frontend-specific one,
  despite being used almost universally in this batch's other skills).

All forward references are to real, catalog-confirmed IDs, not fabricated
placeholders — none of these skills invented content for their unauthored
parents.

## Potential corrections

1. **The taxonomy-table defect (§Taxonomy defect found and fixed above) was
   corrected in this batch**, not just flagged — consistent with this
   project's standing practice of fixing source documents rather than only
   working around instances of a problem.
2. **The `depends_on_skills`-vs-`parents` fix continues to hold with zero
   recurrence** across 11 independently-generated technology skills in this
   batch, the second consecutive batch confirming this. The rule appears
   durable; no further spec action needed unless a future batch regresses.
3. **Four skills' descriptions landed within 9 characters of the 500-char
   CE-1 ceiling** (nextjs 491, typescript 491, web-standards 499,
   tailwindcss 499) — not a violation, but tighter than ideal; future batch
   prompts could ask agents to target a lower ceiling (e.g. 450) to leave
   safety margin against future field additions.
4. **No skill in this batch was promoted to `final/`** — same standing gap
   as all three prior batches (no executable validator or `evaluations/`
   tests yet).

## Overall assessment

All thirteen skills are internally consistent with the specification,
taxonomy (after the one taxonomy-table fix), dependency architecture, and
routing architecture, well-grounded (6–48 citations per skill, with the two
generics intentionally lighter since their content is decision-framework-
heavy rather than citation-dense), and version-aware — including several
genuinely load-bearing version-sensitive findings correctly surfaced rather
than flattened or omitted: React's two-stage RSC CVE with distinct
fixed-version ranges per patch; Next.js's May 2026 coordinated release with
no direct patch for versions 13–14; Vue 2's full EOL and Vapor Mode's
not-yet-stable RC status (despite some secondary sources overstating its
readiness); Angular's unusually strict per-major TypeScript/Node
version-floor coupling; TypeScript 6.0's disruptive default-behavior changes
and 7.0's Compiler-API gap; Nuxt's precisely-scoped cross-user
payload-disclosure GHSA; Sass's dated `@import` deprecation timeline against
a fully-EOL Node Sass; Tailwind v4's hard browser-version floor and breaking
arbitrary-value syntax change; MUI's split active-patch-line policy (only
v9 current and v7 LTS receive patches); and shadcn/ui's structural
no-automatic-upgrade-path risk inherent to its copy-in-source distribution
model. The specification fix applied after the DATA-domain batch continues
to close the `depends_on_skills` conflation issue across a second
consecutive batch — reinforcing that fixing the spec, not just the
instances, compounds correctly.
