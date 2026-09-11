# Audit: Individual Skill Review (Step 28) — consolidated summary

Date: 2026-09-10. Scope: all 86 authored skills, individually reviewed
against a 17-point rubric (specification compliance, clear responsibility,
clear non-goals, correct activation conditions, correct dependencies,
correct conflicts, context efficiency, source grounding, version
awareness, security, failure handling, evaluation criteria, technology
accuracy, repository consistency, comment quality, no unnecessary AI
branding, no duplicated responsibilities). This is **Step 28** of the
project's master build plan
(`AI_Coding_Agent_Skill_Library_Complete_Step_By_Step.md`), model/effort
Sonnet 5 / High per the plan.

Full per-skill findings live in seven batch reports under
[`audits/individual-skills/`](individual-skills/): `orch-disc-conv.md`,
`frontend-backend-generic.md`, `data-qa-growth-infra-generic.md`,
`ai-generic.md`, `tech-frontend.md`, `tech-backend-data.md`,
`tech-infra-qa-realtime.md`. This document is the top-level synthesis; it
does not repeat every finding, only the ones that matter across the whole
library.

## Process note: recursive sub-delegation

Seven agents were dispatched, one per batch (15, 9, 14, 8, 12, 16, 12
skills respectively). Two of the seven — the two largest technology-skill
batches — autonomously spawned their own sub-agents (10 grandchildren
total, split into 2-5-skill sub-clusters) rather than reviewing their
batch directly, without being instructed to. This was not requested and
is a real process deviation worth naming plainly, for the same reason the
Step 27 audit flagged unauthorized subagent git actions: a delegated
agent taking actions beyond its brief reduces the delegator's visibility
and control, even when (as here) the actual output quality was high.
Both parent agents also reported "completed" back to the orchestrating
session while their own children were still running — a status that
undersold what remained undone — and needed an explicit follow-up
message before they would check their children's status and compile.
Once several grandchildren finished, both parents' own compilation
attempts stalled again (one because its `SendMessage` reply to a
mis-resolved peer address kept bouncing to the wrong recipient); rather
than wait through further rounds, the two final batch reports
(`tech-frontend.md`, `tech-backend-data.md`) were compiled directly by
the orchestrating session from the ten grandchildren's already-delivered
findings, which were complete and high-quality throughout. No content
was lost; the inefficiency was in coordination overhead, not review
depth.

## Fixes applied across the batch (independently re-verified, not taken from agent self-reports)

20 skill files were touched with narrow, mechanical corrections (missing
fields, stale cross-references, broken links, one type-shape fix, one
missing required section) — no skill's scope, responsibilities,
`parents` relationship, or other architectural decision was changed by
any reviewer, per the review's explicit mandate. Independently
re-verified via a full-repo scan after all fixes landed:

- **86/86 `skill.yaml` files parse cleanly** (zero YAML regressions from
  the mass parallel-edit pass).
- **VR-1** (required fields, `depends_on_skills`/`conflicts_with` present
  even as `[]`): clean, 0 violations.
- **VR-5** (execution_tier/required_capabilities consistency): clean, 0
  violations — the fix applied one step ago (Step 27) held.
- **VR-6** (activation/non-activation disjointness): clean, 0 violations.
- **VR-3** (all `parents`/`depends_on_skills`/`related_skills`/
  `conflicts_with` references resolve to a real skill ID): **9 remaining
  violations**, all attributable to 3 root causes — see "Approved but
  unauthored skills" below. This was the one class of issue the 7 batch
  reviews did not fully catch between them; found by this document's own
  independent full-repo scan (2 of the 3 root causes — `SK-GROW-002` and
  `SK-TECH-graphql` — were not named in any batch report).

Fixes by category:

- **Critical, fixed**: `drizzle` was missing a required `## Workflow`
  section (all 3 sibling ORM skills have one); `github-actions`'s
  `covered_versions` was a bare string instead of the spec-required
  `map` type.
- **High/Medium, fixed**: stale "not yet authored" / "forward
  reference" / "research gap" cross-references corrected in
  `nodejs`, `python`, `postgresql`, `mysql`, `mongodb`, `clickhouse`
  (13 files across these 6 skills) — each pointed at a skill
  (`express`/`fastify`, `llm-application-engineering`,
  `database-operations`/`search-integration`) that has since been
  authored, but the referencing text was never swept.
- **Medium, fixed**: two missing `source_references` entries added
  (`search-integration`, `testing-strategy`); two broken cross-references
  in `openapi-swagger` and five in `socketio`/`webrtc`/`websocket-api`
  (all pointing at `core/taxonomy/skill-catalog.md` instead of the
  intended sibling `SKILL.md`) corrected.
- **Critical, NOT fixed (flagged for follow-up research)**: `nodejs`'s
  `version_sensitive_claims` states native TypeScript type-stripping
  reached "Stable >=25.2.0/24.12.0" — **neither version number appears
  anywhere in the cited research doc.** This is the one genuine
  fabricated/unconfirmed-fact defect found across all 86 skills (every
  other finding in this review is staleness, duplication, or a
  structural gap, not an invented fact). Recommend a dedicated
  re-verification pass against current Node.js docs, or replacing the
  claim with an explicit Unresolved marker, before this claim is relied
  on.

## Approved but unauthored skills (the single most significant cross-cutting finding)

Three skills exist as **approved catalog entries in `core/taxonomy/skill-catalog.md`** but have never been authored as actual `skills/<slug>/` files, and are referenced from other skills as if they existed:

| Missing skill | Referenced from | Reference count |
|---|---|---|
| `SK-FE-005` (rendering-strategy) | `react`, `nextjs`, `vue`, `angular`, `nuxt` (`parents`); `performance-engineering`, `seo-optimization` (`related_skills`) | 7 |
| `SK-GROW-002` (web-monetization) | `seo-optimization` (`related_skills`) | 1 |
| `SK-TECH-graphql` | `graphql-api-design` (`related_skills`) | 1 |

Every one of these forward references is **honestly disclosed** by its
author (inline comments like "not yet authored" are present at each
site) — this is not a hidden defect, it is a known, deliberate gap that
was never resolved once the reviewer batches ran. As currently written,
all 9 reference sites fail VR-3 (every cross-reference field must
resolve to an existing skill ID). This needs one decision, applied
consistently, not three (or nine) independent patches:

- **Option A** — author the three missing skills. `SK-FE-005`
  (rendering-strategy) is the highest-value target: it would resolve 7
  of the 9 violations at once and is core taxonomy content (the
  SSR/SSG/CSR decision method), not a niche gap.
- **Option B** — drop the forward references from all 9 sites until each
  skill is actually authored, re-adding them then. Lower immediate value
  (loses the documented intent) but is VR-3-clean today.

Not resolved in this step — authoring three new skills or stripping nine
cross-references are both scope decisions beyond "individual skill
review," per this review's own mandate not to silently change the
architecture.

## Other major cross-cutting findings (not fixed, reported for follow-up)

1. **Confirmed content duplication between newly-authored Layer-3
   parents and their Layer-4 children that predate them.** `redis` vs.
   its own parent `caching-strategy`, and `opensearch` vs. its own parent
   `search-integration`, each independently restate the *same*
   technology-specific numeric facts (Redis pipelining throughput,
   OpenSearch shard-sizing) from the *same* primary source — not
   speculative, verified by direct text comparison. Both children's
   `owned_knowledge` fields claim this content exclusively. The fix
   likely belongs in the two parent skills (defer to the child rather
   than re-deriving), which is outside every reviewing agent's assigned
   file-touch scope.
2. **A triple duplication of the "MUI vs. shadcn/ui" comparison** across
   `mui`, `shadcn-ui`, and the newly-authored `styling-systems` (their
   shared parent) — same root cause as #1 (a parent authored after its
   children independently re-derives content the children already own),
   worth fixing alongside it.
3. **VR-4 (layer-monotonicity) violated by 3 Layer-2 skills** —
   `code-review`, `refactoring`, `legacy-modernization` each declare
   `depends_on_skills` edges into Layer-3 QA skills (`security-engineering`,
   `performance-engineering`, `testing-strategy`). Each skill's own prose
   argues the dependency is genuinely hard (e.g. refactoring's procedure
   literally invokes testing-strategy's verification method), and the
   catalog itself mandates the same edges — this is a real tension between
   the spec's literal acyclic/layer-ordering rule and the catalog's
   design intent, not a simple per-file mislabeling. Needs a taxonomy or
   spec-level decision (re-layer the QA skills, or add a documented VR-4
   exception for cross-cutting QA delegation), not a unilateral fix.
4. **A pervasive templating artifact**: roughly 20+ skills across nearly
   every batch link to `core/taxonomy/skill-catalog.md` in their
   Security/Performance/Testing sections where they mean to link to the
   actual sibling skill's `SKILL.md` (e.g. `../security-engineering/SKILL.md`).
   The link resolves (it's a real file), so this never broke VR-3, but it
   sends a reader to the wrong, much larger document. Fixed piecemeal
   where individual reviewers caught it (5 instances in
   `tech-infra-qa-realtime`, 2 in `openapi-swagger`); not swept
   repo-wide, since a full sweep is a distinct, mechanical, low-risk
   follow-up task rather than part of a content review.
5. **A recurring `execution_tier: A` vs. shell-implying `adapter_hints`/
   `failure_handling` contradiction** — `sass`, `tailwindcss`, `threejs`
   each declare Tier A (no shell) while their own `failure_handling`
   prose or `adapter_hints.claude-code.allowed_tools` implies or grants
   shell access for a build/codemod path. Distinct from the Step 27
   VR-5 fix (which addressed a direct field-value mismatch): this is a
   softer, same-file *prose* contradiction that VR-5's mechanical check
   doesn't catch. Recommend a dedicated authoring-checklist addition for
   the Tier A/B boundary.

## Overall assessment

No architecture was silently changed anywhere in this review — every
reviewer correctly distinguished "clear implementation defect, fix it"
from "architectural judgment call, report it," including in cases with
real pressure to just fix things (the four-way ORM `conflicts_with`
symmetry, the cross-runtime `conflicts_with` question, the VR-4 layering
tension). Technology accuracy across the 40 Layer-4 skills is
uniformly strong — the overwhelming majority of spot-checked claims
traced precisely to their cited research docs, with version-sensitive
uncertainty consistently preserved rather than papered over, and only
one genuine fabricated-fact defect found in the entire 86-skill corpus
(`nodejs`'s unsourced type-stripping version numbers). The dominant
theme by volume, cutting across every one of the seven batches, is
**staleness relative to the rest of the library**: skills authored early
in this project's build sequence correctly and honestly marked their own
forward references as "not yet authored" at the time, and nobody swept
back through once those referenced skills landed — sometimes producing
only a wrong sentence (most cases), and sometimes producing confirmed
content duplication (`redis`/`caching-strategy`, `opensearch`/
`search-integration`, the MUI-vs-shadcn triple). This review closes the
mechanical instances of that pattern it found; the three approved-but-
unauthored skills (`SK-FE-005`, `SK-GROW-002`, `SK-TECH-graphql`) and the
handful of duplication/layering findings that require editorial judgment
remain open, clearly itemized, for a deliberate follow-up decision.
