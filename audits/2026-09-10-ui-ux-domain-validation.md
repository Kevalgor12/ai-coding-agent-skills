# Audit: UI/UX-domain skill generation & validation

Date: 2026-09-10. Scope: two skills, both generic — `SK-FE-002`
ui-ux-design and `SK-FE-003` styling-systems. Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).
This batch completes the entire FE Layer-3 generic set except
`SK-FE-005` (rendering-strategy, not requested here).

**Scope note:** the user's 7-item list ("UI Architecture, UX Architecture,
Design Systems, Responsive Design, Accessibility, Interaction Design,
Frontend Design Review") maps to 2 skills, not 7 — and one item
("Accessibility") required no new work at all, since `SK-FE-004`
web-accessibility was already authored in the FRONTEND-domain batch.
"UI Architecture," "UX Architecture," "Interaction Design," and "Frontend
Design Review" all collapsed into `SK-FE-002` ui-ux-design — its own
taxonomy entry already names "layout, hierarchy, responsive behavior,
usability" as scope and its evaluation criteria literally reads "a
layout/hierarchy a designer would accept." "Design Systems" mapped more
precisely to `SK-FE-003` styling-systems rather than `SK-FE-002` — its
purpose explicitly names "design tokens, theming" and its Inputs list
"Design system/brand" directly, a closer match than ui-ux-design's more
behavioral/visual-judgment scope. "Responsive Design" split across both,
consistent with how the taxonomy itself already cross-references the two
skills as Related — ui-ux-design owns the UX/behavioral side, styling-
systems owns the technical token/breakpoint-strategy side. Confirmed via
`AskUserQuestion` ("Yes, proceed with 2") rather than assumed — this was
one of the harder mapping calls in the project so far, since "Design
Systems" and "Responsive Design" both had plausible claims on either
skill and the taxonomy's own cross-referencing made a purely mechanical
resolution insufficient without judgment.

**Authorship note:** as with SECURITY, PERFORMANCE, and SEO, this batch
contains **no technology skills to delegate** — both are Layer-3 generics
specialized entirely by already-authored technology skills (React/Vue/
Angular for ui-ux-design's component-level concerns; Tailwind/Sass/
web-standards/shadcn-ui/MUI for styling-systems), with no new tech
skill needed. Both authored directly by hand, grounded in
`concept-knowledge-map.md`'s Design-System/Responsive/Dark-Mode sections
and `technology-decision-matrix.md` §8–9 (both partially read in the
FRONTEND batch, now read specifically for these two skills' own Knowledge
sections rather than as supporting context for sibling technology skills).

## Completed skills

| Skill | ID | Tier | Files | `[Source:]` / `[Synthesis]` citations |
|---|---|---|---|---|
| [ui-ux-design](../skills/ui-ux-design/) | SK-FE-002 | A | yaml, SKILL.md | 3 / 0 |
| [styling-systems](../skills/styling-systems/) | SK-FE-003 | A | yaml, SKILL.md | 2 / 1 |

Both independently confirmed on disk (file existence, line counts) —
self-authored by hand; YAML validity and field-presence checks were still
run and passed on both files.

**Mechanical checks run and passed, both (scripted, not manual):**
- YAML validity for both `skill.yaml` files.
- VR-1 (all always-required fields present, including
  `depends_on_skills` present-and-empty).
- CE-1 (description ≤ 500 chars) — both well within range.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically.
- VR-3 (every `related_skills`/`conflicts_with` ID resolves to a real
  taxonomy entry) — all resolve cleanly, including mutual cross-references
  between the two skills in this same batch and references to five
  already-authored technology skills (`mui`, `tailwindcss`, `sass`,
  `web-standards`, `shadcn-ui`) plus `web-accessibility` (also already
  authored).
- `depends_on_skills: []` for both — no hard sub-step composition; each
  hands off to the other and to sibling technology skills via
  `related_skills` only.
- `execution_tier: A` for both — advisory/design-level work, consistent
  with their taxonomy-catalog Tier A designation (unlike `web-
  accessibility`'s dual A/C tier from the same FE domain, neither of
  these two skills carries a genuine Tier-C execution component).
- **Five already-authored technology skills** (`mui`, `tailwindcss`,
  `sass`, `web-standards`, `shadcn-ui`) **had forward-referenced
  `SK-FE-002`/`SK-FE-003` as unauthored parents when they were generated
  in the FRONTEND batch** — those forward references now resolve
  correctly with no edits needed to the five existing files, confirming
  the forward-reference pattern works as designed across a genuinely long
  gap (this batch landed several batches after the FRONTEND batch that
  first referenced these two IDs).
- All relative links resolve.

## Unresolved questions

None specific to this batch's own authored content — both skills'
Knowledge sections trace every substantive claim to
`concept-knowledge-map.md` or `technology-decision-matrix.md` without
needing to carry forward an "Unresolved" flag from the underlying
research. The one genuine boundary both skills state explicitly is a
**scope honesty statement, not an unresolved research question**:
`ui-ux-design`'s Purpose & scope section states plainly that this
library's research is technology-documentation-shaped, not an
independently deep UX-research corpus with usability-testing methodology
or quantitative design research — grounded content is limited to what
component-library/markup documentation actually covers, applied alongside
professional design judgment for the rest. This mirrors the honesty
pattern established by `deployment-release` (INFRA batch) and
`git-workflow` (CONV/INFRA batch) for skills whose grounding is real but
narrower than the skill's full scope would ideally warrant.

## Duplicated responsibilities

**None found**, despite a genuinely close split between the two skills on
two of the seven original user-list items (Design Systems, Responsive
Design):
- `ui-ux-design` explicitly scopes Responsive Design to the UX/behavioral
  side (does the layout work across viewports, are interaction states
  designed for each), while `styling-systems` scopes it to the technical
  token/breakpoint-strategy side (how a tool like Tailwind expresses
  responsive variants) — each skill's Knowledge section stays on its own
  side of that split, with `ui-ux-design`'s Decision framework item 4
  addressing viewport coverage and `styling-systems`' Knowledge section
  addressing Tailwind's `sm:`/`md:`/`lg:` variant-stacking mechanism
  specifically.
- `styling-systems` owns Design Systems' technical backbone (token
  structure, runtime-vs-build-time theming, component-library
  distribution models); `ui-ux-design` doesn't restate any of this,
  referencing `styling-systems` for implementation syntax instead.
- Both skills explicitly decline to repeat content already owned by the
  five sibling technology skills (mui, tailwindcss, sass, web-standards,
  shadcn-ui) and by `web-accessibility`, linking out rather than
  re-explaining.

## Missing dependencies

- `ui-ux-design` references `SK-FE-003`/`SK-FE-004` (both authored — the
  latter from an earlier batch, the former within this same batch) and
  two already-authored technology skills (`mui`, `shadcn-ui`) — no
  unauthored forward references.
- `styling-systems` references `SK-FE-002`/`SK-FE-004` (both authored)
  and five already-authored technology skills — no unauthored forward
  references.

This is the **first batch with zero unauthored forward references at
all** — every single cross-reference in both skills resolves to an
already-authored skill, either from an earlier batch or from within this
same batch.

## Potential corrections

1. **This is the fourth consecutive batch with no technology-skill
   delegation** (after SECURITY, PERFORMANCE, SEO) — for yet a third
   distinct underlying reason: SECURITY/PERFORMANCE were purely
   cross-cutting with no tech specialization at all; SEO was a taxonomy-
   level generic+tech merge; this batch is neither — it's two ordinary
   Layer-3 generics whose technology specializations simply happened to
   all be authored already, in an earlier batch (FRONTEND), before this
   generic-completing batch arrived. Worth explicitly naming this as a
   third distinct "no delegation" reason in the running pattern-tracking
   across audits: cross-cutting scope, taxonomy-level merge, or
   generic-arrives-after-its-specializations sequencing.
2. **The Design-Systems/Responsive-Design mapping ambiguity was
   genuinely harder to resolve than most prior batches' collapses** —
   unlike e.g. HTML+CSS (an explicit taxonomy merge) or API-Architect+REST
   (one clearly redundant synonym), this required weighing two
   plausible skill assignments against each other using the taxonomy's
   own Purpose/Inputs wording as tie-breaking evidence, then confirming
   with the user rather than resolving unilaterally. Worth treating this
   as the reference example for future ambiguous-split cases, where the
   two skills are already cross-referenced as Related in the taxonomy but
   neither is a clean 1:1 match for a user-list item.
3. **The forward-reference mechanism was validated end-to-end for the
   first time across a genuinely long batch gap** — five technology
   skills authored in the FRONTEND batch referenced these two IDs as
   unauthored parents, and those references now resolve correctly with
   zero edits needed, several batches later. Confirms the forward-
   reference design decision (cite the taxonomy ID now, let it resolve
   naturally as the catalog fills in) continues to hold under real,
   extended time gaps, not just adjacent-batch gaps.
4. **No skill in this batch was promoted to `final/`** — same standing
   gap as all twelve prior batches.

## Overall assessment

Both skills are internally consistent with the specification, taxonomy,
dependency architecture, and routing architecture, appropriately grounded
given their genuinely thinner research backing than most prior batches
(both skills state this honestly rather than inflating their citation
density), and cleanly partitioned across a genuinely ambiguous user-list
split. `ui-ux-design` correctly identifies native-HTML-element affordances
as the highest-leverage interaction-design decision (echoing, without
duplicating, `web-accessibility`'s own semantic-HTML framing from a
different angle — interaction-state cost, not accessibility compliance)
and states its own UX-research-depth boundary honestly. `styling-systems`
correctly identifies the runtime-vs-build-time theming split as the single
most consequential architectural decision in its scope, and surfaces the
MUI-vs-shadcn/ui patch-propagation trade-off (already covered in each of
those two technology skills individually) as a structural, cross-cutting
synthesis rather than restating either skill's own content. This batch is
also the first to close with zero remaining unauthored forward references
in either skill, and the first to concretely validate the forward-
reference pattern across a multi-batch time gap rather than just between
adjacent batches.
