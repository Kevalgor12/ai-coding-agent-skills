# Audit: CODE-QUALITY-domain skill generation & validation

Date: 2026-09-10. Scope: five skills, all generic — `SK-CONV-002`
code-commenting, `SK-CONV-003` code-quality, `SK-CONV-004` refactoring,
`SK-CONV-005` legacy-modernization, `SK-CONV-007` code-review. Validated
against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).
This batch authors `SK-CONV-002`, the second of this library's two
mandated first-class skills — `SK-CONV-001` (git-conventions) was
authored in the CONV/INFRA-domain batch; this batch closes the pair.

**Scope note:** the user's 9-item list ("Code Review, Code Quality,
Refactoring, Generated-Code Cleanup, Dead Code Detection, Duplication
Reduction, Legacy Code Archaeology, Modernization, Human Code
Commenting") maps to 5 skills, not 9. "Code Review"→`SK-CONV-007`, "Code
Quality"→`SK-CONV-003`, "Refactoring"→`SK-CONV-004`, and "Human Code
Commenting"→`SK-CONV-002` all mapped directly by name. "Legacy Code
Archaeology" and "Modernization" both collapsed into the single
`SK-CONV-005` legacy-modernization — its first documented responsibility
is literally "assess current vs. target state," the archaeology half of
the pairing. "Generated-Code Cleanup," "Dead Code Detection," and
"Duplication Reduction" had no independent taxonomy entries: dead code is
explicitly named in code-quality's own responsibilities; duplication
reduction is fundamentally a refactoring activity (consolidating
behavior-identical code without changing it); generated-code cleanup
(AI/tool signatures, phase-narration comments) is explicitly named in
code-commenting's own responsibilities. Confirmed via `AskUserQuestion`
("Yes, proceed with 5") rather than assumed.

**Authorship note:** as with SECURITY, PERFORMANCE, SEO, and UI/UX, this
batch contains **no technology skills to delegate** — all five are
Layer-2 (Conventions) generics, language- and technology-agnostic by
design, specialized only implicitly by whichever Layer-4 skill's idiom
applies to the code in question. All five authored directly by hand.
Grounding is intentionally light and practice-based for four of the five
(consistent with `git-conventions`/`git-workflow`'s precedent from the
CONV/INFRA batch, since software-engineering practice — not a researched
technology's official documentation — is the appropriate grounding for
"how to write a comment" or "how to structure a code review"); the fifth
(`legacy-modernization`) draws concretely on version-matrix.md's
already-gathered cross-technology breaking-change data as illustrative,
citable examples of what its "assess the gap" step actually needs to
surface.

## Completed skills

| Skill | ID | Tier | Files | Citations in SKILL.md |
|---|---|---|---|---|
| [code-commenting](../skills/code-commenting/) | SK-CONV-002 | A | yaml, SKILL.md | 0 |
| [code-quality](../skills/code-quality/) | SK-CONV-003 | A | yaml, SKILL.md | 0 |
| [refactoring](../skills/refactoring/) | SK-CONV-004 | B | yaml, SKILL.md | 0 |
| [legacy-modernization](../skills/legacy-modernization/) | SK-CONV-005 | B | yaml, SKILL.md | 1 |
| [code-review](../skills/code-review/) | SK-CONV-007 | A | yaml, SKILL.md | 0 |

All five independently confirmed on disk (file existence, line counts) —
self-authored by hand; YAML validity and field-presence checks were still
run and passed on all five files.

**Mechanical checks run and passed, all five (scripted, not manual):**
- YAML validity for all 5 `skill.yaml` files.
- VR-1 (all always-required fields present, including `depends_on_skills`
  present — either `[]` or populated, never omitted).
- CE-1 (description ≤ 500 chars) — all five well within range.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically, zero mismatches.
- VR-3 (every `depends_on_skills`/`related_skills`/`conflicts_with` ID
  resolves to a real taxonomy entry) — all resolve cleanly, with zero
  unauthored forward references across all five skills (every referenced
  ID — `SK-QA-001`/`002`/`003`, `SK-CONV-001`/`004`/`008`, `SK-DISC-002`,
  `SK-DATA-006` — is already authored, either from an earlier batch or
  from within this same batch).
- All relative links resolve.

### `depends_on_skills` — three genuine hard-composition cases, the richest set in this project

This batch produced the project's richest set of correct
`depends_on_skills` usage, extending the single positive precedent
(`git-workflow`→`git-conventions`, CONV/INFRA batch) to three more cases,
one of them multi-dependency:

- `refactoring` → `[SK-QA-001]` (testing-strategy): refactoring's own
  procedure literally invokes testing-strategy's verification method as
  part of every refactor, not as an optional adjacent concern.
- `legacy-modernization` → `[SK-CONV-004, SK-QA-001]` (refactoring,
  testing-strategy): each staged modernization step is itself a
  behavior-preserving transformation, verified the same way a refactor
  is — a genuine two-skill hard composition.
- `code-review` → `[SK-QA-002, SK-QA-003, SK-CONV-002, SK-CONV-003]`
  (security-engineering, performance-engineering, code-commenting,
  code-quality): the richest single case in this project — code-review's
  own procedure explicitly delegates four separate specialized facets
  rather than re-deriving any of their logic, matching its taxonomy
  entry's own "delegated facets" language precisely.

All three were verified programmatically to contain no self-reference and
no circular dependency (`refactoring`→`testing-strategy` is a leaf;
`legacy-modernization`→`refactoring`+`testing-strategy` has no cycle back;
`code-review`'s four dependencies are all independent of each other and of
`code-review` itself).

## Unresolved questions

None specific to this batch's own authored content. All five skills'
factual claims trace either to the taxonomy's own catalog entries
(itself the authoritative source for these mandated/practice-based
skills) or, for `legacy-modernization` specifically, to already-verified
version-matrix.md facts carried forward from earlier batches (React RSC
CVE version ranges, Next.js's forced-upgrade advisory, Angular's per-
major TS/Node coupling, Vue 2's EOL) — no new uncertain claims were
introduced.

## Duplicated responsibilities

**None found**, and this batch had the highest inherent duplication risk
of any batch so far given how tightly the five skills interlock by
design (code-review explicitly delegates to two of the other four; code-
quality and code-commenting are both "related" to nearly every other
skill in the set; refactoring and legacy-modernization share a direct
dependency chain):
- `code-review` explicitly delegates security/performance/comment/
  quality-convention findings rather than re-deriving any of that logic,
  reserving only correctness-bug-finding as its own undelegated
  responsibility — its Knowledge section states this delegation
  discipline as the central organizing principle of the skill, not an
  incidental detail.
- `refactoring` and `legacy-modernization` stay cleanly separated: the
  former owns behavior-preserving transformation and its verification
  discipline; the latter owns the broader current-vs-target-state
  assessment and staged-planning layer, explicitly reusing refactoring's
  verification method for each individual step rather than inventing a
  separate one.
- `code-quality` and `code-commenting` stay separated along the same line
  the taxonomy itself draws: code-commenting owns comment content/
  placement, code-quality owns naming/structure/dead-code/duplication —
  each skill's Knowledge section references the boundary explicitly
  (code-quality's naming discipline is framed as "why most code needs
  few comments in the first place," directly citing code-commenting
  without restating its content).

## Missing dependencies

**Zero unauthored forward references across all five skills** — every
`depends_on_skills`/`related_skills` ID resolves to an already-authored
skill. This is the second batch in a row with this property (after
UI/UX's `ui-ux-design`/`styling-systems`), and the first batch where it
holds across five skills with a genuinely dense internal dependency graph
rather than just two loosely-coupled skills.

## Potential corrections

1. **This batch closes the second and final mandated first-class skill**
   (`SK-CONV-002` code-commenting) — both skills the taxonomy's original
   ruling singled out for "extra depth" specification (`SK-CONV-001`
   git-conventions, authored in CONV/INFRA; `SK-CONV-002` code-commenting,
   authored here) are now complete. No further mandated-skill gap remains
   in this project.
2. **The `depends_on_skills` pattern moved from a single positive
   precedent to a small, internally-consistent cluster of three cases in
   one batch**, including the project's first multi-dependency case
   (`code-review`'s four-skill delegation). This is a stronger validation
   of the pattern than any single prior instance — worth treating the
   whole cluster, not just `git-workflow`'s original example, as the
   reference set for future batches that need genuine hard-composition
   examples.
3. **This is the fifth consecutive batch with no technology-skill
   delegation** (after SECURITY, PERFORMANCE, SEO, UI/UX) — for the same
   underlying reason as UI/UX (Layer-2 generics with no dedicated
   technology specialization by design, language-agnostic rather than
   tied to a specific researched technology). The running tally of
   distinct "no delegation" reasons across this project now stands at
   four: cross-cutting scope (SECURITY, PERFORMANCE), taxonomy-level
   merge (SEO), generic-arrives-after-specializations sequencing (part of
   UI/UX), and language-agnostic-practice scope (this batch and the other
   part of UI/UX).
4. **No skill in this batch was promoted to `final/`** — same standing
   gap as all thirteen prior batches.

## Overall assessment

All five skills are internally consistent with the specification,
taxonomy, dependency architecture, and routing architecture, and — as a
direct consequence of being authored together in one batch with a real
internal dependency graph — the cleanest-partitioned set of interlocking
skills in this project so far, with zero content duplication despite the
highest structural coupling of any batch. The batch's most significant
structural contribution is validating `depends_on_skills` as a genuinely
reusable pattern rather than a one-off: three new correct cases,
including the project's first multi-dependency delegation
(`code-review`'s four sibling skills), all verified free of cycles or
self-reference. `legacy-modernization` in particular demonstrates that a
practice-based Layer-2 skill can still draw concrete, citable grounding
from this library's existing technology research (version-matrix.md's
breaking-change data) without needing its own dedicated technology
research pass — reusing what six-plus prior batches already gathered
rather than re-deriving it. This batch also closes the last open item
from this project's original taxonomy-design mandate: both first-class
skills (git-conventions, code-commenting) are now authored, complete, and
cross-referenced correctly with each other and with the rest of the
Conventions layer.
