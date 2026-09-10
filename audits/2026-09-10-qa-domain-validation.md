# Audit: QA-domain skill generation & validation

Date: 2026-09-10. Scope: three skills — one generic (`SK-QA-001`
testing-strategy) and two technology skills (`SK-TECH-jest-vitest`,
`SK-TECH-playwright`). Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).

**Scope note:** the user's 10-item list ("QA Architecture, Testing
Strategy, Manual Testing, Automation Testing, Playwright, Jest, Vitest,
Integration Testing, E2E Testing, Test Data") maps to 3 skills, not 10.
The taxonomy has exactly one QA-testing generic — `SK-QA-001`
testing-strategy — whose scope already explicitly names
"unit/integration/e2e/component/visual/contract/load" as the layers it
covers. "QA Architecture," "Testing Strategy," "Manual Testing,"
"Automation Testing," "Integration Testing," and "E2E Testing" all
collapsed into it; none had independent taxonomy entries or research
grounding as distinct skills. "Test Data" likewise had no dedicated
research (only passing mentions under Prisma's/Redis's own docs) and
folded into testing-strategy's fixture/isolation responsibilities.
"Playwright"→`SK-TECH-playwright`; "Jest"+"Vitest"→the single
taxonomy-merged `SK-TECH-jest-vitest` (same HTML+CSS-style, choose-one
merge pattern as two earlier batches). Confirmed via `AskUserQuestion`
("Yes, proceed with 3") rather than assumed — the second-largest
single-batch collapse of this project so far (10→3, after SEARCH's 5→2).

**Authorship note:** as with all eight prior batches, the generic skill
was authored directly by hand; the two technology skills were delegated to
parallel agents with pre-verified relationship data and pre-verified
version/security/performance facts pulled from `testing-knowledge-map.md`/
`version-matrix.md`/`security-knowledge-map.md`/`technology-decision-
matrix.md`, then independently re-verified on disk. This batch's prompts
also explicitly required each agent to run a YAML parse check as its own
literal final step (not just claim one), directly in response to the
`github-actions` YAML-syntax defect caught in the immediately prior batch —
both agents complied and both files parsed cleanly on independent
re-verification.

## Completed skills

| Skill | ID | Tier | Files | Citations in SKILL.md |
|---|---|---|---|---|
| [testing-strategy](../skills/testing-strategy/) | SK-QA-001 | B | yaml, SKILL.md | 7 |
| [jest-vitest](../skills/jest-vitest/) | SK-TECH-jest-vitest | B | yaml, SKILL.md | 33 |
| [playwright](../skills/playwright/) | SK-TECH-playwright | C | yaml, SKILL.md | 32 |

All three independently confirmed on disk (file existence, line counts,
and an independent YAML re-parse of both technology skills) — not accepted
from either agent's self-report alone, though this is the first batch
where both agents' own claimed self-checks (YAML validity, field presence)
held up under re-verification without a defect, closing the loop opened by
the `github-actions` incident in the prior batch.

**Mechanical checks run and passed, all three (scripted, not manual):**
- YAML validity for all 3 `skill.yaml` files — both technology skills
  re-parsed cleanly on independent verification.
- VR-1 (all always-required fields present, including `depends_on_skills`
  present-and-empty rather than omitted) and technology-conditional fields
  (`parents`, `covered_versions`, `version_sensitive_claims`,
  `reverify_triggers`) present for both technology skills — the explicit
  "field must be present, not omitted" instruction (added after the prior
  batch's `github-actions` omission) held for both agents this time.
- CE-1 (description ≤ 500 chars) — all three within range; `playwright` at
  482/500 is a continuation of the standing "leave more headroom" note.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically, zero mismatches.
- **`depends_on_skills`-vs-`parents` conflation: zero recurrence**, the
  seventh consecutive batch where every technology skill correctly left
  `depends_on_skills: []` with specialization captured only in `parents`
  (`[SK-QA-001]` for jest-vitest; `[SK-QA-001, SK-FE-004]` for playwright).
- VR-3 (every `parents`/`related_skills`/`conflicts_with` ID resolves to a
  real taxonomy entry) — all resolve cleanly.
- `conflicts_with: []` for both technology skills, for two different, both
  correct reasons: `jest-vitest` because Jest and Vitest are ONE merged
  skill (a choose-one decision within the same skill, not two skills in
  conflict) rather than the "don't invent a conflict with an unresearched
  alternative" pattern seen in prior batches; `playwright` because no
  independently-researched alternative E2E tool exists in this library
  (Cypress/WebdriverIO appear only as names inside other technologies' own
  docs, never as their own researched technology) — correctly extending
  the now-standard discipline to a fifth domain.
- **VR-5 (Tier-C capability consistency) self-corrected mid-authoring**:
  the `playwright` agent caught that the prompt's literal
  `required_capabilities` list didn't actually satisfy VR-5's Tier-C rule
  (at least one non-universal capability with a matching
  `capability_fallbacks` entry) and added `browser` plus a
  `capability_fallbacks.browser` entry (Playwright-via-MCP, then
  advisory-only degrade) to make the skill internally consistent with the
  spec, flagging the deviation explicitly in its own report rather than
  silently diverging from instructions. This is the first batch where an
  agent caught and fixed a specification-consistency issue in its own
  instructions rather than a human/architect catching it downstream.
- All relative links resolve.

## Unresolved questions

1. **`jest-vitest`**: two genuinely uncertain items from the source
   research were deliberately excluded rather than asserted — Jest's exact
   `__mocks__` auto-application semantics by directory location, and a
   discrepancy between Jest's upgrade guide and its config docs over the
   `waitForUnhandledRejections` default value. Neither was load-bearing for
   this skill's required grounded facts, so omission (not a papered-over
   guess) was the correct call.
2. **`playwright`**: the macOS 13 WebKit-deprecation version (believed
   v1.52, per the source research's own uncertainty flag) and the
   `route.continue()` Cookie-header-override removal are both marked
   "Unresolved" in both `skill.yaml` and `SKILL.md`, preserving the source
   research's own stated lack of confidence rather than presenting it as
   settled.
3. **`testing-strategy`**: the test pyramid itself is explicitly framed as
   "a working framework for organizing what *is* documented, layer by
   layer" rather than a researched universal law — the skill states
   plainly that layer-by-layer coverage across this library's 44
   technologies is highly uneven, not that a pyramid methodology was itself
   independently validated by the research.

None of these were load-bearing enough to block any skill.

## Duplicated responsibilities

**None found**, despite this batch's structure carrying real duplication
risk (two technology skills both specializing the same generic, and
`playwright` additionally sharing a second parent with an
already-authored skill from an earlier batch):

- `jest-vitest` and `playwright` both explicitly declined to repeat
  `testing-strategy`'s layer-selection decision framework, the "many
  technologies have no documented testing methodology" finding, and the
  visual-snapshot-testing tension (MUI/Vue both cautioning against
  snapshot-only testing) — adding only their own tool-specific mechanics.
- `playwright` additionally declined to repeat
  [web-accessibility](../skills/web-accessibility/SKILL.md)'s existing
  content on Playwright's role-based Locators API (`getByRole()` etc.) as
  an accessibility signal and its MCP accessibility-tree integration —
  correctly recognizing this as already-owned content from a *different*
  domain's batch (FRONTEND) rather than treating it as fair game to
  restate just because it's the same underlying tool.
- `jest-vitest` is framed throughout as ONE skill for a choose-one
  decision, not two skills describing overlapping tools — the "near-
  identical API by design" framing from the taxonomy's own merge rationale
  is stated explicitly rather than left implicit.

## Missing dependencies

- `testing-strategy` references `SK-CONV-004` and `SK-CONV-007` (both
  unauthored) alongside `SK-QA-003` (unauthored, performance-engineering)
  in `related_skills` — all handled as non-fabricated forward references.
- `jest-vitest` and `playwright` forward-reference each other — both
  authored within this same batch, so neither is a genuine forward
  reference by the time the batch completes.
- `playwright`'s two formal parents (`SK-QA-001`, `SK-FE-004`) were both
  already authored by the time this skill was generated — no unauthored
  parent references.

## Potential corrections

1. **The `depends_on_skills`-vs-`parents` fix and the "field must be
   present, not omitted" fix both held across this batch** — the second
   consecutive batch confirming the omission fix specifically, following
   its introduction immediately after the prior batch's `github-actions`
   defect. Both fixes now read as durable.
2. **The mandatory-final-YAML-parse-check instruction, added directly in
   response to the prior batch's syntax defect, worked as intended** —
   both agents ran it and reported the result, and independent
   re-verification found no defect in either file. Worth keeping as a
   standing instruction in all future technology-skill delegation prompts,
   not just a one-off response to that incident.
3. **The `playwright` agent's self-correction on Tier-C capability
   consistency is worth treating as a positive precedent**: rather than
   silently complying with an instruction that would have produced a
   spec-inconsistent skill, it caught the gap, fixed it, and reported the
   deviation transparently. Future prompts specifying `required_capabilities`
   for a Tier-C skill should double-check this project's own VR-5 rule is
   actually satisfied before handing it to an agent, rather than relying on
   the agent to catch an authoring-prompt error.
4. **No skill in this batch was promoted to `final/`** — same standing gap
   as all eight prior batches.

## Overall assessment

All three skills are internally consistent with the specification,
taxonomy, dependency architecture, and routing architecture, well-grounded
(7–33 citations, with the generic's lighter count reflecting its
decision-framework/synthesis-heavy content rather than an authoring gap),
and version-aware: Jest's v27 default-behavior overhaul and v30's Node/TS/
jsdom/CLI/glob changes, Vitest's v5.0 Vite/Node floor and narrow two-minor
security-backport window, and Playwright's Alpine-incompatibility/
Docker-image-pinning requirements and v1.60 API-removal list were all
correctly surfaced with precise version ranges. This batch is also the
clearest evidence yet that this project's standing "verify on disk, don't
trust the self-report" and "fix the spec/prompt, not just the instance"
disciplines compound correctly: the two defect classes caught in the
immediately prior batch (YAML syntax errors, omitted required fields) were
explicitly guarded against in this batch's prompts and did not recur, and
a third, previously-uncaught class (an authoring instruction that would
have produced a spec-inconsistent Tier-C skill) was caught and
self-corrected by the delegated agent itself rather than surfacing only at
the audit stage.
