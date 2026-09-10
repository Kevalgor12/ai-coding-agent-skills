# Audit: CONV/INFRA-domain (Git & CI) skill generation & validation

Date: 2026-09-10. Scope: five skills — three generic (`SK-CONV-001`
git-conventions, `SK-CONV-008` git-workflow, `SK-INFRA-002`
ci-cd-pipeline) and two technology skills (`SK-TECH-github-actions`,
`SK-TECH-husky`). Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).
This batch also closes `SK-INFRA-002`, the one taxonomy-defined
Infrastructure generic left unauthored after the prior INFRA-domain batch.

**Scope note:** the user's 7-item list ("Git, GitHub, Branch & Commit
Conventions, GitHub Actions, CI/CD, Husky, Release Engineering") maps to 5
skills, not 7. "Git"→`SK-CONV-008` (git-workflow: branching/merge/rebase/
worktree/PR operations), "Branch & Commit Conventions"→`SK-CONV-001`
(git-conventions, the mandated first-class skill for commit/branch *text*),
"GitHub Actions"→`SK-TECH-github-actions`, "CI/CD"→`SK-INFRA-002`
(ci-cd-pipeline), "Husky"→`SK-TECH-husky` all mapped cleanly. "GitHub" (the
platform) is explicitly **not** a standalone taxonomy skill by design —
`taxonomy-analysis.md` rules it out, since its concerns already split
across git-workflow, ci-cd-pipeline, code-review (not yet authored), and
project-management (`SK-DISC-004`, already authored), and a standalone
skill would duplicate all four and mis-trigger on any git task. "Release
Engineering" maps to `SK-INFRA-003` (deployment-release), already authored
in the prior INFRA-domain batch. Confirmed via `AskUserQuestion` ("Yes,
proceed with 5") rather than assumed.

**Authorship note:** as with all seven prior batches, the three generic
skills were authored directly by hand; the two technology skills were
delegated to parallel agents with pre-verified relationship data
(`parents`, `conflicts_with`, `related_skills`) and pre-verified version/
security/performance facts pulled from `version-matrix.md`/
`security-knowledge-map.md`/`performance-knowledge-map.md`/
`integration-map.md`, then independently re-verified on disk (not trusted
from the self-report alone) — this verification step caught a real defect
in this batch (see below), reinforcing why it's a standing practice rather
than a formality.

## Completed skills

| Skill | ID | Tier | Files | Citations in SKILL.md |
|---|---|---|---|---|
| [git-conventions](../skills/git-conventions/) | SK-CONV-001 | A | yaml, SKILL.md | 1 |
| [git-workflow](../skills/git-workflow/) | SK-CONV-008 | B | yaml, SKILL.md | 3 |
| [ci-cd-pipeline](../skills/ci-cd-pipeline/) | SK-INFRA-002 | A | yaml, SKILL.md | 3 |
| [github-actions](../skills/github-actions/) | SK-TECH-github-actions | A | yaml, SKILL.md | 15 |
| [husky](../skills/husky/) | SK-TECH-husky | B | yaml, SKILL.md | 14 |

All five independently confirmed on disk (file existence, line counts) —
not accepted from either agent's self-report alone.

**Mechanical checks run and passed, all five (scripted, not manual), after
one fix (below):**
- YAML validity for all 5 `skill.yaml` files — one genuine parse error
  found and fixed (see "Defect found and fixed").
- VR-1 (all always-required fields present) and technology-conditional
  fields (`parents`, `covered_versions`, `version_sensitive_claims`,
  `reverify_triggers`) present for both technology skills.
- CE-1 (description ≤ 500 chars) — all five within range; `husky` at
  495/500 is a repeat of the standing "leave more headroom" note from
  recent batches.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically, zero mismatches, including after the `github-actions`
  fix.
- **`depends_on_skills`-vs-`parents` conflation: zero recurrence** for
  both technology skills — the sixth consecutive batch (BACKEND, FRONTEND,
  REALTIME, SEARCH, INFRA, now this one) where every technology skill
  correctly left `depends_on_skills` empty of anything already captured in
  `parents`.
- **A deliberate, correct exception to that pattern**: `git-workflow`
  (`SK-CONV-008`, `kind: generic`) sets `depends_on_skills: [SK-CONV-001]`.
  This is NOT the historical bug — `git-workflow` has no `parents` field at
  all (generic skills don't specialize anything), and the relationship is
  genuine hard sub-step composition: whenever git-workflow's own procedure
  creates a branch or commit as part of an operation (a merge, a PR), it
  literally invokes git-conventions' procedure to produce that text. This
  is the first batch in this project with a clean, correct positive example
  of `depends_on_skills` in use between two peer generic skills, rather
  than only negative examples of what NOT to put there.
- VR-3 (every `parents`/`related_skills`/`conflicts_with`/
  `depends_on_skills` ID resolves to a real taxonomy entry) — all resolve
  cleanly.
- `conflicts_with: []` for both technology skills — correct: GitHub Actions
  is the only CI/CD platform profiled in this research (the decision matrix
  explicitly notes no first-party Jenkins/CircleCI/GitLab CI data exists),
  and Husky is the only Git-hooks-manager technology profiled (no
  pre-commit/lefthook/simple-git-hooks data exists) — the same
  "don't invent a conflict with an unresearched technology" discipline now
  extended to a fourth domain (after REALTIME, SEARCH, INFRA).
- `execution_tier` consistency: `git-conventions`, `ci-cd-pipeline`, and
  `github-actions` are Tier A (advisory/config-authoring, with execution
  explicitly stated as external — this library's capability map found no
  ecosystem that drives GitHub Actions natively); `git-workflow` and
  `husky` are Tier B (both require actual shell/git execution to install
  hooks or perform git operations).
- All relative links resolve.

### Defect found and fixed

`skills/github-actions/skill.yaml` failed to parse: a `verification` list
item (line 185) began its plain YAML scalar directly with a backtick
(`` ` ``) — one of the characters the YAML spec reserves and disallows at
the start of a plain scalar (along with `@`). This is a **new failure
mode** for this project, distinct from every previously-caught defect
(field conflation, taxonomy-table inconsistency, missing required field):
a syntactically invalid YAML file that would fail at parse time for any
downstream tool, not merely a semantic/content issue a validator would
flag. Caught by this batch's standard "verify on disk, don't trust the
self-report" step (a `python3 -c "yaml.safe_load(...)"` check), even though
the authoring agent's own self-report claimed the file "parses as valid
YAML" — the agent's own earlier self-check evidently ran before this
specific line was in its final form, or missed it. **Fixed** by quoting the
scalar in double quotes. Separately, the same file also omitted
`depends_on_skills` entirely (not even present as an empty list) — an
always-required field per VR-1 — likely because the authoring agent,
warned heavily against the depends_on_skills/parents conflation, over-
corrected toward omitting the field rather than setting it to `[]`. Fixed
by adding `depends_on_skills: []`.

## Unresolved questions

1. **GitHub Actions' `set-output`/`save-state` hard-removal date** — the
   research confirms the 2022-10-11 deprecation announcement but could not
   re-confirm whether hard removal has actually happened as of the research
   date; the skill states this precisely rather than asserting a resolved
   timeline.
2. **GitHub Actions has no single "product version" to pin** —
   `covered_versions` honestly states this (continuously-deployed SaaS)
   and instead pins the dated sub-component boundaries that actually carry
   version-sensitivity (artifact-action v3→v4, node20→node24 runtime,
   self-hosted runner agent ≥2.329.0).
3. **Husky has no dedicated official security page** — only the `..`-path-
   rejection rule is officially documented; the `node_modules/.bin`
   PATH-trust risk is stated as the research's own inference, not an
   official claim, and the skill preserves that distinction rather than
   presenting it with false certainty.
4. **`git-workflow`'s research boundary is stated as a structural fact**,
   similar to how `deployment-release` handled its own thin grounding in
   the prior INFRA batch: this library has no dedicated official research
   document for Git the CLI tool itself, only GitHub's own documentation
   (GitHub Flow, merge methods, rulesets) — pure git-plumbing mechanics not
   covered by GitHub's docs are grounded in general engineering discipline,
   stated as such rather than presented as researched fact.

None of these four were load-bearing enough to block any skill.

## Duplicated responsibilities

**None found.** `github-actions` explicitly declined to repeat
`ci-cd-pipeline`'s general secrets/token/caching/matrix-strategy
principles, adding only GitHub-Actions-specific mechanics (workflow YAML
structure, reusable-workflow composition, concrete `::add-mask::`/
permissions-block syntax) plus three genuinely new sections the parent
doesn't cover at all (self-hosted-runner risk, cache-poisoning on
`pull_request_target`, the `set-output`/`save-state` log-injection fix).
`husky` explicitly declined to repeat either of its two parents' content —
`ci-cd-pipeline`'s pipeline-design method or `git-conventions`'s
text-convention rules — adding only Husky's own hook-mechanism depth
(the `core.hooksPath` install mechanism, per-package-manager wiring, the
"trigger not filter" boundary vs. lint-staged). `git-conventions` and
`git-workflow` stayed cleanly separated per their own scope split (text vs.
operations), with `git-workflow` correctly delegating text composition
back to `git-conventions` via `depends_on_skills` rather than duplicating
it inline.

## Missing dependencies

- `git-conventions` has no unauthored forward references — its only
  related skill (`SK-CONV-008` git-workflow) is authored within this same
  batch.
- `git-workflow` references `SK-INFRA-002` (authored within this same
  batch) and `SK-DISC-004` (already authored, from the DISC batch) — no
  unauthored forward references, beyond its intentional hard dependency on
  the now-authored `SK-CONV-001`.
- `ci-cd-pipeline` references `SK-INFRA-001` (authored), `SK-CONV-008` and
  `SK-TECH-husky` (both authored within this same batch), `SK-DISC-004`
  (already authored) — and `SK-QA-001` (testing-strategy), which remains
  unauthored, the only genuine forward reference in this batch's generics.
- `github-actions` and `husky` forward-reference each other — both
  authored within this same batch, so neither is actually a forward
  reference to an unauthored skill by the time the batch completes.

Only one unauthored forward reference exists in this entire batch
(`ci-cd-pipeline`→`SK-QA-001`) — the smallest count of any batch so far,
since most of this batch's own cross-references resolved to skills
authored either earlier in this project or within this same batch. It does
not fabricate content for the missing skill.

## Potential corrections

1. **The `depends_on_skills`-vs-`parents` fix continues to hold with zero
   recurrence for technology skills** across a sixth consecutive batch —
   AND this batch produced the project's first clean positive example of
   correct `depends_on_skills` usage between two generic skills
   (`git-workflow`→`git-conventions`), worth keeping as the reference
   example for any future batch that needs a real (not just
   forbidden-pattern) illustration of hard sub-step composition.
2. **A new defect class was caught this batch: invalid YAML syntax**
   (backtick starting a plain scalar), not just semantic/spec-conformance
   issues. This wasn't caught by the authoring agent's own claimed
   self-check — worth tightening the standard self-check instruction in
   future prompts to explicitly re-run the YAML parse check as the very
   last step before reporting done, since a late edit can silently
   reintroduce a syntax error after an earlier successful parse.
3. **An omitted (not merely empty) `depends_on_skills` field** was also
   caught in the same file — likely an over-correction from an agent
   heavily warned against the historical conflation bug. Worth noting for
   future prompts: explicitly state that the field must be *present and
   set to `[]`* when there's nothing to put in it, not omitted, since
   omission also fails VR-1.
4. **The "don't invent a conflict with an unresearched technology"
   discipline now spans four domains** (REALTIME, SEARCH, INFRA, and now
   this CONV/INFRA batch) — a settled project-wide norm at this point.
5. **No skill in this batch was promoted to `final/`** — same standing gap
   as all seven prior batches.

## Overall assessment

All five skills are internally consistent with the specification, taxonomy,
dependency architecture, and routing architecture, appropriately grounded
(1–15 citations, with the two hand-authored git-practice skills
deliberately light on citation since their content is largely professional
practice/GitHub-Flow-adjacent rather than deep technical research), and
version-aware where the research supports it: GitHub Actions' artifact-
storage v3→v4 boundary with its precise blocking date, the node20→node24
runtime forced migration, self-hosted-runner agent version enforcement, and
Husky's Git>2.9 floor plus the announced-but-unreleased v10.0.0 legacy-shim
removal were all correctly surfaced with precise version ranges rather than
flattened. This batch also produced two structurally notable outcomes
worth carrying forward: the first genuine, correct use of
`depends_on_skills` for hard composition between two peer generic skills
(not just another instance of avoiding the historical anti-pattern), and
the first YAML *syntax* defect caught in this project (as opposed to
semantic/spec-conformance defects), both found only because this batch's
independent-verification discipline caught what an agent's own self-report
claimed was already correct.
