# Audit: DOCUMENTATION-domain skill generation & validation

Date: 2026-09-10. Scope: one skill, generic — `SK-CONV-006`
technical-documentation. Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).

**Scope note:** the user's 6-item list ("Technical Writing, README, API
Documentation, Architecture Documentation, Developer Documentation,
Changelog") maps to 1 new skill. "Technical Writing," "README," "API
Documentation," "Architecture Documentation" (ADRs are literally named in
the taxonomy entry), and "Developer Documentation" all collapsed into
`SK-CONV-006` technical-documentation directly. "Changelog" required no
new work at all — it's already an explicit, named responsibility of the
already-authored `SK-DISC-004` project-management skill ("maintain
status; draft release notes/changelogs," with changelog-drafting
literally in its evaluation criteria from the DISC-domain batch).
Confirmed via `AskUserQuestion` ("Yes, proceed with 1") rather than
assumed.

**Authorship note:** as with CODE-QUALITY, this batch's one skill is a
Layer-2 (Conventions) generic authored directly by hand, no technology
skill to delegate for the generic content itself — though notably,
`openapi-swagger` (authored in the BACKEND-domain batch) already carries
`SK-CONV-006` as a **formal parent** (`parents: [SK-BE-002, SK-CONV-006]`),
confirming this skill was always intended to have at least one real
technology specialization, unlike most other CODE-QUALITY-batch skills.
That specialization already exists and required no changes — its forward
reference to the then-unauthored `SK-CONV-006` now resolves correctly,
the third consecutive batch (after CODE-QUALITY, UI/UX) to confirm the
forward-reference pattern holding across a real time gap.

## Completed skills

| Skill | ID | Tier | Files | Citations in SKILL.md |
|---|---|---|---|---|
| [technical-documentation](../skills/technical-documentation/) | SK-CONV-006 | A | yaml, SKILL.md | 2 |

Independently confirmed on disk (file existence, line count) — self-
authored by hand; YAML validity and field-presence checks were run and
caught one real defect (below), fixed, then re-verified passing.

**Mechanical checks run and passed, after one fix:**
- YAML validity for `skill.yaml`.
- VR-1 (all always-required fields present, including `depends_on_skills`
  present-and-empty).
- **CE-1 (description ≤ 500 chars) initially failed at 505 chars** — a
  genuine, if minor, spec violation caught by the standard validation
  script, not a formatting or content-quality issue. Trimmed to 446
  chars, with the SKILL.md frontmatter updated to match verbatim, and
  re-verified passing.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically after the description fix.
- VR-3 (every `related_skills`/`conflicts_with` ID resolves to a real
  taxonomy entry) — all resolve cleanly, including references to
  `SK-CONV-002` (code-commenting, authored in the immediately prior
  batch), `SK-BE-002` (api-design, already authored), `SK-TECH-openapi-
  swagger` (already authored, and the skill that already formally
  specializes this one), and `SK-DISC-004` (project-management, already
  authored — the skill this one explicitly defers changelog-drafting to).
- `depends_on_skills: []` — correct; this skill hands off to
  code-commenting and project-management via `related_skills` only, no
  hard sub-step composition.
- All relative links resolve.

## Unresolved questions

None specific to this batch's own authored content. Every substantive
claim traces either to `research/technologies/github.md`'s documented
repository best-practices (the concrete README/LICENSE/CITATION/
SECURITY.md/contribution-guidelines list, and the documented anti-pattern
of skipping documentation entirely) or to this project's own established
engineering discipline (docs-match-behavior, generate-from-source-where-
possible, ADR structure) — no research-boundary caveat was needed.

## Duplicated responsibilities

**None found.** The skill explicitly declines to cover in-code comments
(routed to [code-commenting](../skills/code-commenting/SKILL.md), authored
in the immediately prior batch) or changelog/release-notes drafting
(already owned by `project-management`, stated as a non-activation
condition rather than re-derived). Its relationship with the already-
authored `openapi-swagger` is structured correctly in the other
direction — `openapi-swagger` specializes this skill (formal `parents`
relationship) for the specific case where an OpenAPI spec itself doubles
as documentation, and this skill's own Knowledge section cites that exact
pattern as its lead example of "generate documentation from source" without
restating `openapi-swagger`'s own implementation-level content.

## Missing dependencies

None — every `related_skills` reference resolves to an already-authored
skill (`SK-CONV-002`, `SK-BE-002`, `SK-TECH-openapi-swagger`,
`SK-DISC-004`). This is the third consecutive batch with zero unauthored
forward references (after UI/UX and CODE-QUALITY).

## Potential corrections

1. **A real CE-1 violation was caught and fixed this batch** — the
   description field exceeded the 500-character limit by 5 characters on
   first draft. This is a minor, mechanical defect class distinct from
   the more structurally significant ones caught in earlier batches (the
   `github-actions` YAML syntax error and omitted `depends_on_skills`
   field from the CONV/INFRA batch) — but it reinforces the same
   underlying lesson: the scripted validation pass catches real issues
   even in self-authored, carefully-written content, not just delegated-
   agent output. Worth continuing to run the full validation script
   unconditionally, regardless of whether a skill was self-authored or
   delegated.
2. **`SK-CONV-006`'s pre-existing formal-parent relationship with
   `openapi-swagger`** (set correctly by that skill's own author back in
   the BACKEND-domain batch, well before this skill existed) is a clean
   confirmation that the taxonomy's Layer-2-generic-with-Layer-4-
   specialization pattern (already established for `SK-CONV-003`
   code-quality specialized by TypeScript) extends correctly to
   documentation as well, and that authoring generics *after* their
   specializations continues to resolve correctly with zero edits needed
   to the already-existing specialization.
3. **No skill in this batch was promoted to `final/`** — same standing
   gap as all fourteen prior batches.

## Overall assessment

The skill is internally consistent with the specification (after the
description-length fix), taxonomy, dependency architecture, and routing
architecture, appropriately grounded in GitHub's own documented repository
best-practices for the concrete baseline (README/LICENSE/CITATION/
SECURITY.md/contribution guidelines) and in established engineering
discipline for the rest (docs-match-behavior, generate-from-source,
ADR structure), and cleanly bounded against two adjacent, already-
authored skills (code-commenting for in-code comments, project-management
for changelogs) without restating either. The generate-from-source
principle is grounded concretely in this library's own OpenAPI research —
citing `openapi-swagger`'s own specialization of this skill as the lead
example rather than an abstract claim. This batch also reinforces two
standing project disciplines: the mechanical validation pass catching a
real defect even in careful self-authored content, and the forward-
reference pattern (here, in reverse — a specialization existing before
its generic parent) continuing to resolve correctly across real time
gaps.
