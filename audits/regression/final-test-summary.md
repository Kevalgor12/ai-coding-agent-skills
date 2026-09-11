# Step 35 — Final test summary

**Date:** 2026-09-11
**Branch:** `regression/step-35`
**Purpose:** Confirm Step 34 corrections introduced no regressions before final packaging (Step 36).

## Test results at a glance

| Check | Result |
|---|---|
| Mechanical validator (VR-1–VR-9, CE-1/CE-2) | 0 failures / 88 skills |
| Adapter compatibility suite | 36/36 pass |
| Behavioral scenarios S01–S08 | 8/8 PASS |
| Behavioral scenarios S09–S16 | 6/8 PASS, 2 regressions found and **fixed** |
| **Overall** | **PASS (all issues resolved)** |

## What was tested

### Automated checks

- **`scripts/validate_skills.py`** — run against all 88 skills on the `regression/step-35`
  branch. Checks VR-1 (required fields), VR-2 (name/description/slug consistency),
  VR-3 (cross-reference resolution + stale forward-reference detection), VR-4 (acyclic +
  layer-monotone dependency graph), VR-5 (execution_tier vs. required_capabilities), VR-6
  (activation/non_activation disjoint), VR-7 (no duplicate triggers), VR-8 (canonical
  section order), VR-9 (Tier B/C execution-dependent verification). Result: 0 failures.

- **`adapters/tests/test_compatibility.py`** — 36 combinations across 6 adapter targets
  (claude-code, cursor, vscode, copilot, windsurf, devin) and 6 sample skills, confirming
  the adapter engine handles all Step 34 skill corrections without regressions. Result:
  36/36 pass.

### Behavioral evaluation

All 16 scenarios from `evaluations/scenarios/` were re-evaluated against the Step 34
changes, focusing on:

1. **New skills that could trigger false activations**: `rendering-strategy` (SK-FE-005)
   and `graphql` (SK-TECH-graphql). Checked each scenario's repo signals against the new
   skills' activation/non-activation conditions. No false positives found.

2. **VR-4 dependency graph changes**: `SK-QA-001`, `SK-QA-002`, `SK-QA-003` moved from
   `depends_on_skills` to `related_skills` in `code-review`, `refactoring`, and
   `legacy-modernization`. Checked all scenarios that cite these skills' dependency chains.

3. **C-2 gate changes** (GA-0.1 + D3/FV-9 updates): Verified that S15 (the most
   gate-sensitive scenario) still passes and that GA-0.1 does not affect any other scenario's
   gate reasoning.

4. **VR-3/VR-8 stale-text cleanup**: Spot-checked scenarios referencing skills that had
   stale text removed. No evaluation-layer effects found.

## Regressions found and fixed

Two evaluation-suite documents had stale YAML quotes that would have caused evaluators to
apply incorrect scoring criteria. Both were identified in the behavioral pass and fixed before
commit. See `regression-report.md` for full details.

**Characterization:** documentation regressions in evaluation files, not behavioral regressions
in skill logic. The behavioral requirements (behavior-preservation tests must actually run and
be green) are unchanged — only the derivation mechanism in the evaluation documents was updated
to match current skill YAML.

## Readiness assessment

Step 34 corrections are **regression-free** at both the automated and behavioral levels.
The library is ready for Step 36 (final packaging).

### What is confirmed clean

- All 88 skills pass the mechanical validator
- All adapter targets handle current skill files correctly
- All 16 behavioral evaluation scenarios reflect the current skill YAML accurately
- No evaluation document quotes stale YAML values
- The 2 behavioral requirements most at risk from the VR-4 fix (behavior-preservation testing
  in `refactoring` and `legacy-modernization`) are still enforced — now through each skill's
  own execution-dependent `verification` section and IC-6, which is the architecturally
  correct enforcement point for a library that prohibits cross-layer `depends_on_skills` edges

### What is not covered by this pass

- Live agent execution against real tasks (the evaluation suite tests routing/scoring
  discipline, not live agent output)
- Skills not covered by the 16 scenarios (40+ skills have no dedicated scenario yet)
- Adapter targets beyond the 6 in the compatibility suite
