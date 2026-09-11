# Individual Skill Quality Review — Layer 0 Orchestration, Layer 1 Discovery, Layer 2 Conventions

Batch: `skill-router`, `capability-adapter`, `workflow-composer`, `requirements-engineering`,
`solution-architecture`, `technical-planning`, `project-management`, `code-commenting`,
`code-quality`, `code-review`, `git-conventions`, `git-workflow`, `legacy-modernization`,
`refactoring`, `technical-documentation` (15 skills).

Method: read `core/skill-specification/specification.md` in full, the catalog entries for
all 15 skills in `core/taxonomy/skill-catalog.md`, `skills/code-commenting/SKILL.md` as the
comment-quality yardstick, and `skills/observability/{skill.yaml,SKILL.md}` as the reference
template — then read every `skill.yaml` + `SKILL.md` in the batch in full, plus mechanical
cross-checks (frontmatter parity, activation/non-activation disjointness, library-wide
activation-trigger duplication, `conflicts_with` symmetry, `depends_on_skills` layer/ID
resolution) run against all 86 skills in the repository where relevant.

## Summary

| Skill | Critical | High | Medium | Low |
|---|---|---|---|---|
| skill-router | 0 | 0 | 0 | 0 |
| capability-adapter | 0 | 0 | 0 | 0 |
| workflow-composer | 0 | 0 | 0 | 0 |
| requirements-engineering | 0 | 0 | 0 | 0 |
| solution-architecture | 0 | 0 | 1 | 0 |
| technical-planning | 0 | 0 | 0 | 0 |
| project-management | 0 | 0 | 0 | 1 |
| code-commenting | 0 | 0 | 0 | 1 |
| code-quality | 0 | 0 | 1 | 0 |
| code-review | 1 | 0 | 1 | 0 |
| git-conventions | 0 | 0 | 0 | 1 |
| git-workflow | 0 | 0 | 0 | 2 |
| legacy-modernization | 1 | 0 | 0 | 0 |
| refactoring | 1 | 0 | 1 | 0 |
| technical-documentation | 0 | 0 | 0 | 3 |
| **Total** | **3** | **0** | **3** | **7** |

No skill in this batch has a High-severity finding, no `parents`/`depends_on_skills`
conflation, no VR-5 tier/capability mismatch, no VR-6 activation/non-activation overlap, no
VR-7 exact-string activation-trigger duplicate (checked library-wide), no asymmetric
`conflicts_with` (checked library-wide — no other skill in the repository declares a
conflict against any of these 15 IDs), no dangling cross-reference (every `depends_on_skills`
/ `related_skills` ID resolves to an authored skill), and no AI branding, marketing language,
or embedded code snippets requiring a comment-quality check (none of the 15 bodies contain a
fenced code block). The batch is, on the whole, unusually well-constructed — several files
even carry their own prior-audit-fix commentary (e.g. `solution-architecture`'s
`depends_on_skills` → `related_skills` correction, dated 2026-09-09) showing this ground has
already been gone over once carefully.

The one substantive, load-bearing defect is a **systemic VR-4 layer-ordering violation**
shared by three skills — see `code-review`, `refactoring`, and `legacy-modernization` below,
and the cross-batch discussion after the per-skill sections.

---

## skill-router (SK-ORCH-001)

No problems found. `depends_on_skills: []` matches the catalog ("Dependencies: None (Layer 0
root)"). `conflicts_with: []` matches ("Conflicts: None"). Activation/non-activation
conditions match the catalog's stated boundary against `solution-architecture`,
`technical-planning`, and `workflow-composer` precisely, and the SKILL.md body repeats and
sharpens that boundary in "When to use / When not to use," the decision framework, and the
anti-patterns list. `evaluation_criteria` and `failure_handling` are concrete and specific
(e.g. "no more than a stated bound of spurious selections," "never plan an unauthored skill").
Description is 391 chars (well under CE-1's 500). Body section order matches spec §3.2
exactly. Notably, this skill's own Escalation section explicitly names "an upward layer edge"
as a recognized "library defect" class — directly relevant to the finding under `code-review`/
`refactoring`/`legacy-modernization` below.

## capability-adapter (SK-ORCH-002)

No problems found. Empty `depends_on_skills`/`conflicts_with` both match the catalog. The
capability-resolution ladder (declared → observed → probed → asked → assumed-absent) and the
four-way decision table are concrete, testable, and consistent between `skill.yaml`'s
`evaluation_criteria` and the SKILL.md body. Correctly never names a host tool anywhere in its
own guidance (verified — no host-specific tool names appear in the body). Description 396
chars.

## workflow-composer (SK-ORCH-003)

No problems found. `depends_on_skills: [SK-ORCH-001]` matches the catalog's "Dependencies:
SK-ORCH-001" exactly, and both are Layer 0 — same-layer dependency, no VR-4 concern. Gate,
loop, and recovery-rung discipline are concrete and non-vacuous (denied-branch requirement,
budget-before-loop rule, named recovery ladder). Description 408 chars.

## requirements-engineering (SK-DISC-001)

No problems found. Empty `depends_on_skills`/`conflicts_with` match the catalog. The
requirement-vs-solution distinction, the non-functional-requirements checklist (correctly
offloaded to `references/nonfunctional-requirements-checklist.md`, which exists and has real
content), and the acceptance-criteria testability rule are all concrete. `grounding:
engineering-convention` is the correct classification (no external API/vendor claims are
made). Description 357 chars.

## solution-architecture (SK-DISC-002)

One problem found.

- **Issue:** Four cross-reference links in the SKILL.md body point at the generic catalog
  page instead of the actual sibling skill — `[authentication-authorization]`,
  `[caching-strategy]`, `[security-engineering]`, and `[observability]` in the Knowledge
  section, plus `[security-engineering]` again in Security, `[performance-engineering]` in
  Performance, and `[testing-strategy]` in Testing — all resolve to
  `../../core/taxonomy/skill-catalog.md` rather than e.g. `../security-engineering/SKILL.md`.
  All four target skills exist as real, authored directories with their own `SKILL.md`
  (confirmed). This is inconsistent with the reference template (`observability/SKILL.md`
  links `[security-engineering](../security-engineering/SKILL.md)` directly) and with this
  same file's own pattern elsewhere (`[requirements-engineering](../requirements-engineering/SKILL.md)`
  and `[technical-planning](../technical-planning/SKILL.md)` are both linked directly). A
  consuming agent following "deep threat modeling is owned by security-engineering" lands on
  a generic multi-hundred-line catalog page instead of the actual skill.
  **Severity: Medium** (real navigational degradation, not a VR violation — these are body
  prose links, not `skill.yaml` ID cross-references subject to VR-3).
  **Recommended correction:** point each link directly at the sibling skill's `SKILL.md`
  (e.g. `../security-engineering/SKILL.md`, `../performance-engineering/SKILL.md`,
  `../testing-strategy/SKILL.md`, `../observability/SKILL.md`,
  `../authentication-authorization/SKILL.md`, `../caching-strategy/SKILL.md`).

`depends_on_skills: []` (with the explicit 2026-09-09 policy-fix comment moving the
requirements-engineering relationship to `related_skills`) is the *correct* application of
the spec's `depends_on_skills`-vs-soft-prerequisite distinction (§2.5) — not a defect,
despite the catalog's "Dependencies: SK-DISC-001 (ideally)" phrasing suggesting a hard edge.
This is a genuine prior correction, not something to re-flag.

## technical-planning (SK-DISC-003)

No problems found. Empty `depends_on_skills` matches "Dependencies: None hard." The
distinction from `project-management` (planning vs. tracking) and from `workflow-composer`
(planning the engineering work vs. sequencing which skills activate) is stated clearly and
bidirectionally. `references/planning-heuristics.md` exists with real content. Description
405 chars.

## project-management (SK-DISC-004)

One problem found.

- **Issue:** In the Purpose & scope section, `[git-conventions]` and `[git-workflow]` both
  link to `../../core/taxonomy/skill-catalog.md` instead of their own `SKILL.md` files
  (`../git-conventions/SKILL.md`, `../git-workflow/SKILL.md`), both of which exist in this
  same batch. Same pattern as the `solution-architecture` finding above, at lower frequency
  (2 instances vs. 4). **Severity: Low.**
  **Recommended correction:** point both links directly at the sibling `SKILL.md` files.

`execution_tier: C` with `required_capabilities: [file-read, file-write, git]` and a
`capability_fallbacks.git` entry correctly satisfies VR-5 (Tier C ⇒ non-universal capability +
documented fallback), and matches the catalog's "Tier: A (advisory) / C (if it writes to a
tracker)" — the fallback entry *is* the declared Tier-A advisory behavior. `activation_mode:
manual` is a defensible, deliberately conservative choice for a skill whose catalog entry
flags it as "thin"/narrowly-grounded.

## code-commenting (SK-CONV-002)

One problem found.

- **Issue:** The Performance section reads, in its entirety, "Not applicable to this skill's
  scope." This is filler with zero actionable content — CE-4 states "a section with nothing
  to say MUST be omitted, not filled with filler," and Performance is an optional (O) section
  per spec §3.2 item 10. Compare to this same file's own Security section, which is also
  brief but states a real, checkable rule (comments must never embed a secret). **Severity:
  Low** (single-line section, zero functional impact, trivial fix).
  **Recommended correction:** delete the Performance section entirely.

This is the library's mandated, first-class reference skill for in-code commenting, and it
lives up to that role: the four concrete noise patterns (step narration, AI/tool signatures,
decorative banners, obvious restatement) are checkable, not vague, and "prefer deletion over
repair for a stale comment" is stated as a deliberate, load-bearing rule rather than a
stylistic preference. `depends_on_skills: []`/`conflicts_with: []` match the catalog.

## code-quality (SK-CONV-003)

One problem found.

- **Issue:** `grounding: mixed` with a single `source_references` entry that is itself
  `core/taxonomy/skill-catalog.md` — i.e., this skill's only "grounding" citation is the
  taxonomy's own design-spec entry describing this very skill, not external documentation or
  a synthesized research artifact. The spec defines `mixed` as combining `official-docs`
  (claims tracing to vendor/official documentation) with `engineering-convention`; citing only
  an internal catalog self-reference doesn't supply the `official-docs` component the `mixed`
  label implies, and the Knowledge section itself makes no vendor/API claims requiring
  grounding — it's pure engineering judgment throughout (naming, dead code, premature
  abstraction, duplication). **Severity: Medium** (a real categorization inaccuracy that could
  mislead a consuming agent into treating house judgment as externally-sourced authority;
  doesn't mechanically violate SG-1, which is worded for literal `official-docs`, not `mixed`).
  **Recommended correction:** change `grounding` to `engineering-convention` (matching
  `requirements-engineering`, `technical-planning`, and `project-management`, which correctly
  use this classification for the same reason — pure house-convention content, no external API
  surface) and drop the `source_references` block, or keep it but relabel it honestly as an
  internal cross-reference rather than grounding evidence.

Everything else is strong: the naming/dead-code/premature-abstraction/duplication engineering
rules are specific and actionable, the duplication-vs-superficial-similarity distinction in
Knowledge is a genuinely non-generic insight (QR-1), and the anti-pattern list names a real
over-engineering trap for the domain (premature abstraction) satisfying QR-4.

## code-review (SK-CONV-007)

Two problems found.

- **Issue 1 (Critical):** `depends_on_skills: [SK-QA-002, SK-QA-003, SK-CONV-002, SK-CONV-003]`.
  `SK-QA-002` (security-engineering) and `SK-QA-003` (performance-engineering) are both
  **Layer 3** (confirmed by reading their `skill.yaml`: `layer: 3`), while `code-review` is
  **Layer 2**. Spec §2.5 states `depends_on_skills` "MUST be same-or-lower taxonomy layer
  (acyclic)," and VR-4 states "a skill depends only on same-or-lower layers." A Layer-2 skill
  hard-depending on two Layer-3 skills is an **upward layer edge** — the exact defect class
  this batch's own `skill-router` SKILL.md names explicitly in its Escalation section: "A
  dependency cycle or an upward layer edge found while ordering escalates as a library
  defect." This is not a borderline reading: the skill's own prose doubles down on treating
  this as genuine hard composition, not a soft prerequisite — "it has hard dependencies on
  four sibling skills whose findings it delegates to rather than re-derives" — so this isn't a
  simple `depends_on_skills`/`related_skills` conflation fixable by re-labeling the edge as
  soft; the delegation genuinely is blocking, per-review, every time. The catalog itself
  specifies this same dependency set ("Dependencies: SK-QA-002, SK-QA-003, SK-CONV-002,
  SK-CONV-003 (delegated facets)"), so the tension is between the catalog's design intent and
  the spec's literal layer-ordering rule, not an authoring mistake local to this file.
  **Severity: Critical** (direct VR-4 violation, confirmed against actual `layer:` values, not
  assumed).
  **Recommended correction:** do **not** unilaterally strip the dependency — the skill's own
  documented design treats it as genuinely hard, and removing it would materially weaken the
  delegation guarantee this skill's Knowledge section calls its "most important discipline."
  This needs a decision above a single-skill fix: either (a) the taxonomy re-examines whether
  `SK-QA-001/002/003` (testing-strategy/security-engineering/performance-engineering) belong
  at Layer 2 given they're composed as hard dependencies by Layer-2 conventions skills in three
  separate places in this batch (see cross-batch note below), or (b) VR-4's layer-ordering rule
  is revised to permit a documented exception for cross-cutting QA delegation, or (c) these
  edges are downgraded to `related_skills` with the actual invocation handled as a documented,
  gracefully-degrading soft call (mirroring the `solution-architecture` →
  `requirements-engineering` fix already applied once in this same batch) — accepting that this
  changes the skill's stated guarantee from "always delegates" to "delegates when available."
  Any of these is an architectural decision, not a file-level typo fix, so it is reported here
  rather than applied.

- **Issue 2 (Medium):** Same `grounding: mixed` + sole-source-is-internal-catalog-self-citation
  pattern as `code-quality` (see above) — `source_references` contains only
  `core/taxonomy/skill-catalog.md`. **Recommended correction:** same as `code-quality` —
  reclassify as `engineering-convention`.

Setting the VR-4 issue aside, the delegation-not-duplication design is otherwise exemplary:
the skill states precisely which facet is its own undelegated responsibility (correctness
bugs — "no sibling skill is scoped to... does this code actually do what it's supposed to
do"), and the confirmed-vs-speculative and severity-ranking disciplines are concrete and
testable.

## git-conventions (SK-CONV-001)

One problem found.

- **Issue:** The Performance section reads, in its entirety, "Not applicable to this skill's
  scope." — identical filler pattern to `code-commenting`. **Severity: Low.**
  **Recommended correction:** delete the section.

Everything else here is strong and matches the catalog precisely: the convention-detection-
before-default ordering (`git log` → commitlint config → CONTRIBUTING/CLAUDE.md → branch
patterns) is stated as the single governing rule, matching the catalog's "Detect existing
convention first" responsibility verbatim in spirit; the default prefix set matches the
catalog's list exactly; "never fabricate a ticket ID, scope, or attribution" is enforced in
Engineering rules, Anti-patterns, Failure handling, and Outputs & verification consistently.
`grounding: mixed` here is correctly justified — the sole `source_reference` is
`research/technologies/github.md`, a real external-facing citation (GitHub Flow's isolated-
commit practice), unlike the internal-only citations flagged for `code-quality`/`code-review`/
`refactoring`.

## git-workflow (SK-CONV-008)

Two problems found.

- **Issue 1:** The Security section links `[security-engineering]` to
  `../../core/taxonomy/skill-catalog.md` instead of `../security-engineering/SKILL.md`. Same
  pattern as the `solution-architecture`/`project-management` findings above, single
  instance. **Severity: Low.**
  **Recommended correction:** point the link directly at `../security-engineering/SKILL.md`.

- **Issue 2:** The Performance section reads, in its entirety, "Not a primary concern for this
  skill's scope." — the same filler pattern as `code-commenting`/`git-conventions`, worded
  slightly differently but carrying no more actionable content. **Severity: Low.**
  **Recommended correction:** delete the section.

`depends_on_skills: [SK-CONV-001]` matches the catalog exactly and is same-layer (both Layer
2) — no VR-4 concern here. The honest statement that this library has no dedicated research
document for raw Git-CLI mechanics, only GitHub's own docs, and that the skill says so rather
than presenting undocumented judgment as researched fact, is a genuinely good practice worth
noting (SG-3 compliance by design). The destructive-operation confirmation-gating discipline
(force-push, `reset --hard`, history rewrite — no generalized prior approval) is concrete and
consistently repeated across Engineering rules, Anti-patterns, Escalation, and Outputs &
verification.

## legacy-modernization (SK-CONV-005)

One problem found.

- **Issue (Critical):** `depends_on_skills: [SK-CONV-004, SK-QA-001]`. `SK-CONV-004`
  (refactoring) is Layer 2, same as this skill — fine. `SK-QA-001` (testing-strategy) is
  **Layer 3** (confirmed: `layer: 3` in `testing-strategy/skill.yaml`), while
  `legacy-modernization` is Layer 2. This is the same upward-layer-edge VR-4 violation as
  `code-review`, and for the same reason: the skill's own Purpose & scope states this is a
  genuine hard dependency ("verification underlies every staged step"), matching the
  catalog's "Dependencies: SK-CONV-004, SK-QA-001." **Severity: Critical.**
  **Recommended correction:** same options as `code-review` above — this is not a single-file
  fix; see the cross-batch note below. Do not remove the edge unilaterally, since the skill's
  stated design treats it as genuinely blocking, not optional.

Aside from this, the skill is strong: the EOL-vs-merely-outdated urgency distinction, the
dependency-chain assessment requirement (a target's own breaking changes plus any coupled
version floor, e.g. Angular/TypeScript), and the rollback-point-per-stage discipline
(explicitly distinguished from "smaller steps" alone) are all concrete, non-generic content
grounded in real, cited version-matrix facts (React RSC CVE windows, Next.js 13-14 forced
upgrade, Vue 2 EOL).

## refactoring (SK-CONV-004)

Two problems found.

- **Issue 1 (Critical):** `depends_on_skills: [SK-QA-001]`. `SK-QA-001` (testing-strategy) is
  **Layer 3**; `refactoring` is Layer 2. Same upward-layer-edge VR-4 violation as
  `code-review`/`legacy-modernization`. The skill's own Purpose & scope states this
  unambiguously: "This skill has a hard dependency on testing-strategy: its own procedure
  literally invokes that skill's verification method... as part of every refactor, not as an
  optional adjacent concern" — ruling out a simple re-labeling to `related_skills` without
  changing the skill's stated guarantee. **Severity: Critical.**
  **Recommended correction:** same as the other two instances — a taxonomy/spec-level
  decision, not a local file fix; see cross-batch note.

- **Issue 2 (Medium):** Same `grounding: mixed` + sole-internal-catalog-self-citation pattern
  as `code-quality`/`code-review` — `source_references` contains only
  `core/taxonomy/skill-catalog.md`. **Recommended correction:** reclassify as
  `engineering-convention`.

The safety-net-is-not-optional framing, the small-steps-as-verification-strategy (not style)
argument, and the "finding a bug mid-refactor is a hard stop, never a silent fix" rule are all
concrete and consistently enforced across Decision framework, Engineering rules, Anti-patterns,
Escalation, and Outputs & verification — no vagueness anywhere in this file.

## technical-documentation (SK-CONV-006)

Three problems found, all Low.

- **Issue 1:** The Performance section reads, in its entirety, "Not applicable to this skill's
  scope." — same filler pattern as `code-commenting`/`git-conventions`.
  **Recommended correction:** delete the section.

- **Issue 2:** In Purpose & scope, `[project-management]` links to
  `../../core/taxonomy/skill-catalog.md` instead of `../project-management/SKILL.md`, which
  exists in this same batch. Same pattern as the other catalog-link findings above, single
  instance here.
  **Recommended correction:** point the link directly at `../project-management/SKILL.md`.

- **Issue 3:** Purpose & scope includes the parenthetical "(authored in the DISC-domain
  batch)" after the `project-management` reference. This is meta-commentary about this
  library's own internal authoring/generation process (batch numbering), not skill content a
  consuming agent needs — it reads as a leftover authoring note rather than deliberate skill
  guidance, and doesn't appear anywhere else in this batch's 15 files.
  **Recommended correction:** delete the parenthetical; the boundary statement itself
  ("changelog/release-notes drafting is already owned by project-management") is sufficient
  without it.

Aside from these three low-cost items, the content is solid: the GitHub-sourced
"skipping documentation is a named anti-pattern" claim carries a real citation, the
generate-from-source-to-structurally-eliminate-drift argument (using OpenAPI as the concrete
example) is a genuinely non-generic insight, and the ADR decision+rationale+alternatives
requirement is stated and reinforced consistently.

---

## Cross-batch note: the Layer-2 → Layer-3 dependency pattern

Three of this batch's fifteen skills — `code-review`, `refactoring`, and
`legacy-modernization`, all Layer 2 (Engineering Conventions) — declare `depends_on_skills`
edges into Layer 3 (Domain Capability) skills: `SK-QA-001` (testing-strategy), `SK-QA-002`
(security-engineering), and `SK-QA-003` (performance-engineering). Layer numbers were
confirmed directly from each target skill's `skill.yaml` (`layer: 3` in all three cases), not
assumed from the catalog's section headers alone. Per spec §2.5 and VR-4, `depends_on_skills`
must stay same-or-lower layer; all three edges go upward, which is the specific defect class
this batch's own `skill-router` SKILL.md names in its Escalation section ("a dependency cycle
or an upward layer edge found while ordering escalates as a library defect — it is never
silently broken to make the plan work").

This is not three independent authoring slips: in each case the skill's own prose explicitly
argues the dependency is a genuine, blocking, always-invoked composition — not the soft
"needs the output but degrades gracefully" relationship the spec reserves for
`related_skills`. It also matches the catalog's stated "Dependencies" line for all three
skills, so the catalog (this review's stated ground truth) mandates the same edges. That
combination — spec rule vs. catalog design intent vs. the skills' own stated architecture, all
pointing in different directions — is why this is reported rather than silently fixed in any
of the three files: removing the edges would contradict both the catalog and each skill's own
documented guarantee, while leaving them contradicts VR-4 as written. Resolving it requires a
decision at the taxonomy/spec level (re-layer the QA skills, add a documented VR-4 exception
for cross-cutting QA delegation, or formally accept the weaker "delegates when available"
framing across all three skills) rather than a per-file patch.

## Fixes applied

None. Per the review's critical-discipline constraint, no changes were made to any
`skill.yaml` or `SKILL.md` in this batch — every finding above (the VR-4 layer violations, the
catalog-link inconsistencies, the filler Performance sections, and the grounding
mislabeling) is reported with a recommended correction rather than applied, since each either
requires a decision beyond a single skill's scope (the VR-4 findings) or was judged narrow
enough to report cleanly without risking an unreviewed edit to files a fresh reviewer should
independently confirm.
