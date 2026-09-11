# Changelog

## Step 34 — Final corrections (2026-09-11)

Implements all six blocking items from the Step 33 principal-engineer audit
(`audits/final-principal-engineer-audit.md`, verdict: NOT READY) that had to
clear before this library could be considered production-ready.

### C-1 · Stale "not yet authored" markers removed (~50 sites, ~25 files)

Forward-reference labels written when skills were authored survived five review
rounds because no mechanical check existed. Once the referenced skills were
authored, the labels became false claims. Removed from: angular, caching-strategy,
deployment-release, frontend-architecture, mui, nextjs, nuxt, opensearch, react,
redis, search-integration, shadcn-ui, vue, and all files referencing
rendering-strategy, graphql, git-conventions, shadcn-ui, or observability as
"not yet authored."

### C-2 · Gate taxonomy blind spot: policy-authorizing requests

Root cause: D3 (risk classification) keyed off the mechanical action (writing a
config file = `reversible-write`), not the action the config *authorizes*. A
request to add a force-push exemption to branch-protection rules classified as
`reversible-write` and never reached D13, gate declaration, or FV-9 — the bypass
shipped having passed every check.

Fix: routing-algorithm.md Phase 1, lifecycle.md D3, failure-recovery-and-escalation.md
gate-class table + new invariant GA-0.1, and security-and-validation.md FV-9 all
updated. A policy/config/exception that lets a future action bypass a gate now
classifies at the gate class it bypasses, not at the mechanical edit class.

### C-3 · Missing mechanical validator

`scripts/validate_skills.py` — first automated check of the authoring contract.
Covers VR-1 (required fields), VR-2 (name/description/slug consistency),
VR-3 (cross-reference resolution + stale-forward-reference detection),
VR-4 (acyclic + layer-monotone dependency graph), VR-5 (execution_tier vs.
required_capabilities), VR-6 (activation/non_activation disjoint), VR-7
(no duplicate activation triggers), VR-8 (SKILL.md canonical section order),
and VR-9 (Tier B/C execution-dependent verification). CE-1/CE-2 reported as
warnings. Runs clean (0 failures) against the full 88-skill tree.

### C-4 · VR-3 gap: two unresolved forward references

Authored two new skills that 11 existing skills forward-referenced:

- **skills/rendering-strategy/** (`SK-FE-005`, Layer 3, generic) — tech-neutral
  CSR/SSR/SSG/ISR/streaming-SSR rendering-mode selection. Specialized by the
  React/Next.js/Vue/Nuxt/Angular technology skills, which own each framework's
  concrete implementation mechanics.

- **skills/graphql/** (`SK-TECH-graphql`, Layer 4, technology) — graphql-js
  schema/resolver implementation, DataLoader N+1 prevention, subscriptions,
  typed codegen, federation vs. stitching, persisted queries. Specializes
  graphql-api-design (SK-BE-003).

Also resolved: SK-GROW-002 forward-reference disclosure in seo-optimization;
VR-3 auto-cleared for graphql-api-design and openapi-swagger once
`skills/graphql/` was authored.

### C-5 · Execution-dependent verification (VR-9)

The original audits found that IC-6 ("complete requires verification to have
actually run") was effectively inert for Tier B/C skills whose verification
items were all static code-review properties. A skill that requires shell
execution should have at least one verification item that is only satisfiable
by actually running something and observing a live result.

Added VR-9 to `core/skill-specification/specification.md` and to the validator.
Added at least one execution-dependent verification item to all 52 Tier B/C
skills (37 were already done in prior sessions; 15 added in this step for
refactoring, search-integration, sentry, shadcn-ui, socketio,
structured-output-tool-calling, testing-strategy, typeorm, typescript, vue,
webrtc, websocket-api, and the 3 skills whose existing items did not satisfy
the heuristic).

### Additional mechanical fixes caught by the new validator

- **VR-4**: Moved SK-QA-001/SK-QA-002/SK-QA-003 from `depends_on_skills` to
  `related_skills` in code-review, legacy-modernization, and refactoring —
  these are conditional escalation targets, not unconditional hard sub-steps.
- **VR-7**: Resolved duplicate trigger string shared by mongodb and mysql.
- **VR-8**: Renamed non-canonical section heading `Knowledge (essential)` →
  `Knowledge` in typescript/SKILL.md.

### Adapter test suite

`python3 adapters/tests/test_compatibility.py` — 36 combinations (6 targets ×
6 sample skills), all passed. No adapter regressions from the skill corrections.
