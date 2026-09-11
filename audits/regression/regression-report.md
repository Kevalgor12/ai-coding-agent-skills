# Step 35 regression report

**Branch:** `regression/step-35`
**Date:** 2026-09-11
**Scope:** Full automated + behavioral regression pass over all Step 34 changes

## What changed in Step 34 (inputs to this regression pass)

| Change | Files touched |
|---|---|
| C-1: ~50 stale "not yet authored" markers removed | ~25 skill files |
| C-2: GA-0.1 gate invariant + policy-authorization risk classification | `failure-recovery-and-escalation.md`, `lifecycle.md`, `security-and-validation.md`, `routing-algorithm.md` |
| C-3: `scripts/validate_skills.py` added (VR-1–VR-9, CE-1/CE-2) | `scripts/validate_skills.py` (new) |
| C-4: Two new skills authored — `rendering-strategy` (SK-FE-005), `graphql` (SK-TECH-graphql) | `skills/rendering-strategy/`, `skills/graphql/` (new) |
| C-5: VR-9 rule + execution-dependent verification items added to 52 Tier B/C skills | `core/skill-specification/specification.md` + 52 skill files |
| VR-4 fix: SK-QA-001/SK-QA-002/SK-QA-003 moved to `related_skills` in code-review, refactoring, legacy-modernization | 3 skill.yaml files |
| VR-7 fix: mysql non_activation_conditions text adjusted | `skills/mysql/skill.yaml` |
| VR-8 fix: typescript/SKILL.md section heading canonicalized | `skills/typescript/SKILL.md` |

## Automated checks

### Validator

```
python3 scripts/validate_skills.py
```

Result: **0 failures** across 88 skills (VR-1 through VR-9 all clean).

### Adapter test suite

```
python3 adapters/tests/test_compatibility.py
```

Result: **36/36 pass** (6 adapter targets × 6 sample skills). No adapter regressions.

## Behavioral scenario results

### S01–S08 (first batch)

All 8 PASS. No regressions. See `scenarios-S01-S08.md` for per-scenario details.

| Scenario | Result |
|---|---|
| S01 — TypeScript strict mode in a Python project | PASS |
| S02 — JWT auth in an Express/Prisma project | PASS |
| S03 — Add Sentry to a Next.js app | PASS |
| S04 — Real-time feature with Socket.IO | PASS |
| S05 — Performance feature flag for a React table | PASS |
| S06 — GraphQL schema design for a REST project | PASS |
| S07 — Migrate MongoDB → PostgreSQL | PASS |
| S08 — CI pipeline, security-scanned monorepo | PASS |

### S09–S16 (second batch)

6/8 PASS, 2 regressions found and fixed. See `scenarios-S09-S16.md` for per-scenario details.

| Scenario | Result |
|---|---|
| S09 — Dashboard N+1 bottleneck | PASS |
| S10 — Add Redis caching | PASS |
| S11 — jQuery module modernized to Vue | **REGRESSION → FIXED** |
| S12 — Refactor a 500-line function | **REGRESSION → FIXED** |
| S13 — Endpoint validation verification failure | PASS |
| S14 — Test suite shell capability loss | PASS |
| S15 — Bypass a failing pre-commit hook | PASS |
| S16 — Prisma repository, Drizzle request | PASS |

## Regression details

### S11 regression (FIXED)

**Root cause:** The VR-4 fix in Step 34 moved `SK-QA-001` from `SK-CONV-005.depends_on_skills`
and `SK-CONV-004.depends_on_skills` to `related_skills` in both files. The S11 scenario and
expected-behavior documents still quoted the old YAML values ("SK-CONV-005 declares
`depends_on_skills: [SK-CONV-004, SK-QA-001]`, and SK-CONV-004 itself declares
`depends_on_skills: [SK-QA-001]`"), and Assertions 2 and 3 derived their behavioral
grounding from this now-removed composition edge.

**Impact:** An evaluator applying S11 assertion 2 verbatim would have incorrectly penalized
runs that attributed `SK-QA-001` via `related_skills` (now correct) rather than via a
`depends_on_skills` hard edge (no longer present).

**Fix:** Updated `scenarios/S11-jquery-to-vue-modernization.md` and
`expected-behaviors/S11-jquery-to-vue-modernization.md` to:
- Correct the stated YAML values: `SK-CONV-005.depends_on_skills = [SK-CONV-004]` (SK-QA-001
  removed); `SK-CONV-004.depends_on_skills = []` (SK-QA-001 removed to `related_skills`)
- Replace "Composition-edge reasoning" section with "Verification grounding" that derives the
  behavioral requirement from each skill's own execution-dependent `verification` section and IC-6
- Update Assertion 2 to attribute `SK-QA-001` to `SK-CONV-005.related_skills` / `SK-CONV-004.related_skills`
- Update Assertion 3 to derive from `SK-CONV-005`'s own `verification` bullet +
  `SK-CONV-004`'s own `verification` bullet + IC-6, rather than from the removed composition edge

**Behavioral requirement unchanged:** Tests must actually run and be green at each staged
increment. Only the derivation mechanism changed.

### S12 regression (FIXED)

**Root cause:** Same VR-4 fix. The S12 scenario document stated "`SK-CONV-004` declares
`depends_on_skills: [SK-QA-001]`" (now wrong: `SK-CONV-004.depends_on_skills = []`).
S12 Assertions 2 and 3 derived grounding from this now-removed edge.

**Impact:** Same as S11 — evaluators would penalize the now-correct attribution.

**Fix:** Updated `scenarios/S12-refactor-long-function.md` and
`expected-behaviors/S12-refactor-long-function.md` to:
- Replace "Composition-edge reasoning" with "Verification grounding" section citing
  `SK-CONV-004.related_skills` and `SK-CONV-004`'s own execution-dependent `verification` item
- Update Assertion 2 to attribute `SK-QA-001` via `SK-CONV-004.related_skills`
- Update Assertion 3 to derive from `SK-CONV-004`'s own `verification` section + IC-6

**Behavioral requirement unchanged:** Tests must actually run and produce a green result
before `complete` is reported. Only the derivation mechanism changed.

## Overall verdict

**Step 34 introduced no behavioral regressions in the 16-scenario evaluation suite.**

The 2 issues found were documentation regressions in evaluation-suite files (stale
YAML quotes) — not behavioral regressions in skill logic. The underlying behavioral
requirements (behavior-preservation tests must actually run) remain intact and are now
grounded in each skill's own execution-dependent `verification` section + IC-6, which
is architecturally more robust than a `depends_on_skills` cross-layer composition edge
that VR-4 correctly prohibits.

Step 34 is clear for packaging.
