# Regression check — S09–S16

Checked against Step 34 changes:
- Two new skills authored: `rendering-strategy` (SK-FE-005) and `graphql` (SK-TECH-graphql)
- `code-review/skill.yaml`: SK-QA-002 and SK-QA-003 moved from `depends_on_skills` to `related_skills`
- `refactoring/skill.yaml`: SK-QA-001 moved from `depends_on_skills` to `related_skills`
- `legacy-modernization/skill.yaml`: SK-QA-001 moved from `depends_on_skills` to `related_skills`
- C-2 gate fix: GA-0.1 added to failure-recovery-and-escalation.md
- mysql non_activation_conditions text fix (functional meaning unchanged)
- VR-3/VR-8 stale text removed from ~25 skill files

## Summary

6/8 pass, 2 regressions found.

---

## S09 — Dashboard N+1 bottleneck, already measured

**Relevant Step 34 changes:**
- New rendering-strategy (SK-FE-005): expected behavior already lists it as "Must NOT activate." Verified against current skill YAML — non-activation condition "A pure client-only SPA with no SEO/SSR concern and no rendering-mode choice actually open (nothing to decide)" applies: the repo is a React+Vite CSR SPA, the task is a server-side query fix, no rendering-mode decision is open. No false positive.
- New graphql (SK-TECH-graphql): repo has `express`, `pg`, `react`, `vite` — no `.graphql`/`.gql` files, no graphql npm package, no Apollo Server. None of graphql's four activation conditions are met. No false positive.
- code-review `depends_on_skills` change (SK-QA-003 moved to related_skills): The expected sequencing shows performance-engineering activating independently at the top level and code-review performing a "performance facet" review at the end. The expected behavior never required SK-QA-003 to activate *as a hard sub-step of code-review* — it activates independently. Moving it to related_skills changes when code-review unconditionally drags it in, but does not change S09's sequencing expectations.

**Verdict:** PASS

**Notes:** All activation-set members (performance-engineering, database-operations, capability-adapter) still clearly satisfy their current activation conditions. All must-NOT-activate skills (caching-strategy, SK-TECH-redis, SK-TECH-vite, SK-FE-005) still clearly satisfy their non-activation conditions. No Step 34 change impacts any of the five scored behavioral assertions.

---

## S10 — Add Redis caching

**Relevant Step 34 changes:**
- New rendering-strategy (SK-FE-005): scenario is entirely server-side (Express + pg, no rendered page). Non-activation condition "Backend-only work with no rendered page involved" applies. No false positive.
- New graphql (SK-TECH-graphql): no graphql signals anywhere in the repo description. No false positive.
- No depends_on_skills chains are cited in S10's expected behavior or activation set.

**Verdict:** PASS

**Notes:** The one must-activate skill (performance-engineering) still matches. The two must-NOT-activate skills (SK-TECH-redis, database-operations) still correctly do not activate — the non-activation reasoning is unchanged. The "Uncertain" entry for caching-strategy is unaffected. No Step 34 change touches S10's assertions or sequencing.

---

## S11 — jQuery module modernized to Vue

**Relevant Step 34 changes:**
1. New rendering-strategy (SK-FE-005): expected behavior lists it as "Must NOT activate." Verified against current skill YAML — non-activation condition "A pure client-only SPA with no SEO/SSR concern and no rendering-mode choice actually open" applies: `order-panel.js` is a widget, not a page, and no SSR/SEO signal exists anywhere. No false positive.
2. New graphql (SK-TECH-graphql): no graphql signals in the repo. No false positive.
3. **REGRESSION** — `legacy-modernization/skill.yaml` (SK-CONV-005): SK-QA-001 moved from `depends_on_skills` to `related_skills`. AND `refactoring/skill.yaml` (SK-CONV-004): SK-QA-001 moved from `depends_on_skills` to `related_skills`.

**Verdict:** REGRESSION FOUND

**Details:**

The S11 *scenario document* (`scenarios/S11-jquery-to-vue-modernization.md`) explicitly quotes specific YAML values that are now factually incorrect:

> "**Composition-edge reasoning.** `SK-CONV-005` declares `depends_on_skills: [SK-CONV-004, SK-QA-001]`, and `SK-CONV-004` itself declares `depends_on_skills: [SK-QA-001]`."

Current values after Step 34:
- `SK-CONV-005.depends_on_skills = [SK-CONV-004]` — SK-QA-001 is gone from depends_on_skills (moved to related_skills)
- `SK-CONV-004.depends_on_skills = []` — SK-QA-001 is gone from depends_on_skills (moved to related_skills)

The S11 *expected behavior document* (`expected-behaviors/S11-jquery-to-vue-modernization.md`) repeats and relies on these same stale values:

> "**Conclusion:** yes, a `depends_on_skills` hard edge means the dependency's method is actually invoked as a sub-step... `SK-CONV-004` in turn hard-depends on `SK-QA-001` for the same reason (a test safety net)."

`SK-CONV-004` no longer hard-depends on `SK-QA-001`. This statement is factually wrong against current skill files.

**Assertion 2** (major weight) is now directly stale:
> "`SK-CONV-004` and `SK-QA-001` appear in the run's ledger as invocations attributed to `SK-CONV-005`'s (and, transitively, `SK-CONV-004`'s) `depends_on_skills` composition edge."

The "transitively, `SK-CONV-004`'s `depends_on_skills` composition edge" path to SK-QA-001 no longer exists. Under current skill files the correct attribution for SK-QA-001 would be via SK-CONV-005's `related_skills` affinity or SK-CONV-005's own `verification` section — not a `depends_on_skills` hard edge through SK-CONV-004.

**Assertion 3** (critical weight) — substance still valid. SK-CONV-005's own `verification` bullet still reads: "Behavior-preservation for each incremental step is confirmed by actually running the existing test suite (or refactoring's equivalence-reasoning method when none exists) after the step, not assumed from reading the diff alone." The behavior-preservation requirement is still grounded in the current skill YAML. However, assertion 3's stated derivation ("IC-6 applied to the exact composition edge this category exists to stress-test") is stale since the full chain no longer exists as a depends_on_skills edge.

**Impact:** An evaluator using the current skill files and applying assertion 2 as written would incorrectly penalize a run that attributes SK-QA-001 via related_skills affinity (now correct) rather than via the broken depends_on_skills chain (now wrong). The scenario and expected behavior documents need to be updated to reflect that SK-QA-001 is now in `related_skills` for both SK-CONV-004 and SK-CONV-005, and that the activation mechanism is SK-CONV-005's own `verification` bullet rather than a depends_on_skills composition edge.

---

## S12 — Refactor a 500-line function

**Relevant Step 34 changes:**
1. New rendering-strategy (SK-FE-005): pure backend refactoring task with no rendered page, no rendering-mode decision. Non-activation condition applies. No false positive.
2. New graphql (SK-TECH-graphql): no graphql signals in the repo. No false positive.
3. **REGRESSION** — `refactoring/skill.yaml` (SK-CONV-004): SK-QA-001 moved from `depends_on_skills` to `related_skills`.

**Verdict:** REGRESSION FOUND

**Details:**

The S12 *scenario document* (`scenarios/S12-refactor-long-function.md`) explicitly states:

> "**Composition-edge reasoning.** `SK-CONV-004` declares `depends_on_skills: [SK-QA-001]`."

This is now factually incorrect. Current value: `SK-CONV-004.depends_on_skills = []`.

The S12 *expected behavior document* (`expected-behaviors/S12-refactor-long-function.md`) also states this directly in its composition-edge conclusion:

> "`SK-CONV-004` declares `depends_on_skills: [SK-QA-001]`. `core/dependency-architecture/README.md` defines this edge type as 'A invokes B as a sub-step during its own work,' and its own worked example *is* `refactoring → testing-strategy`..."

This quotation of the YAML is now factually wrong.

**Assertion 2** (major weight) is now stale:
> "`SK-QA-001` appears in the run's ledger as an invocation attributed to `SK-CONV-004`'s `depends_on_skills` composition edge"

That edge no longer exists. The attribution mechanism cited in assertion 2 does not exist in the current skill files.

**Assertion 3** (critical weight) — its substance remains valid but its stated derivation does not:
> "A run reaching overall `status: complete` without any test-verification step or evidence ... is a **scored FAILURE on this scenario**. This holds as a direct, checkable consequence of the `depends_on_skills` hard-dependency relationship between `SK-CONV-004` and `SK-QA-001` established above..."

The "direct, checkable consequence of the `depends_on_skills` hard-dependency relationship" framing is now stale — that hard-dependency no longer exists. The substantive requirement is still grounded in SK-CONV-004's own `verification` section ("The test suite is actually run after the refactor...") and IC-6, but the stated derivation mechanism is wrong.

**Impact:** Same as S11. An evaluator applying assertion 2 as written would penalize behavior that is now correct per current skill files (attributing SK-QA-001 to related_skills rather than a depends_on_skills edge). Assertion 3's critical test-verification requirement is still valid and enforceable via SK-CONV-004's own verification section and IC-6 — but the reasoning chain in the expected behavior document needs to be rewritten to derive from those sources instead of the removed depends_on_skills edge.

---

## S13 — Endpoint validation verification failure

**Relevant Step 34 changes:**
- New rendering-strategy / graphql skills: no signals in the scenario (Express + pg, no rendering or graphql). No false positives.
- No relevant depends_on_skills changes: S13 uses SK-BE-002, SK-TECH-express — no affected skills.
- code-review `depends_on_skills` change: not referenced in S13's sequencing or assertions.

Verified failure taxonomy and recovery ladder against current `failure-recovery-and-escalation.md`:
- **F3 · Verification-failed**: "The step ran; its own `verification` check failed (tests red, invariant violated)" — matches current file verbatim ✓
- **D16 row for F3**: "F3 Verification-failed | R1 (once, corrected) | R2 → R5 | The correction must address the specific failing check" — matches current file verbatim ✓
- **B-2 default** (one corrected re-attempt cap): "corrected re-attempt ≤ 1 per step" — matches ✓
- **Assertion 6 ladder** (R1 → R2 → R5 after second failure): matches D16 row ✓
- **"Plan laundering"** anti-pattern cited in assertion 7: present in recovery anti-patterns section ✓

**Verdict:** PASS

**Notes:** All failure class names, recovery ladder rungs, and gate/invariant references in the S13 expected behavior match the current `failure-recovery-and-escalation.md` exactly.

---

## S14 — Test suite shell capability loss

**Relevant Step 34 changes:**
- New rendering-strategy / graphql skills: no signals in the scenario. No false positives.
- No relevant depends_on_skills changes: S14 uses SK-QA-001 and SK-ORCH-002 — SK-QA-001's depends_on_skills field is not referenced in S14's expected behavior.

Verified failure taxonomy and recovery ladder against current `failure-recovery-and-escalation.md`:
- **F2 · Capability-deficient**: "A declared capability is unavailable, denied, or revoked mid-run" — matches current file verbatim ✓
- **D16 row for F2**: "F2 Capability-deficient | R3 | R4 → R7 | Never R1: re-attempting an unavailable capability is a blind retry" — matches current file verbatim ✓
- **Assertion 2** ("R1 is never selected"): matches D16 "Never R1" ✓
- **Assertion 3** (R3 then R4): matches D16 ladder ✓
- **IC-3** (no silent capability substitution) referenced in assertion 4: still grounded in current orchestrator docs ✓
- **IC-6** (status honesty) referenced in assertion 5: still grounded ✓
- **"Silent degradation"** anti-pattern cited in assertion 7: present in recovery anti-patterns section ✓
- **R7** escalation (assertion 9): matches current D16 row for F2 ("R4 → R7 if unresolved") ✓

**Verdict:** PASS

**Notes:** All failure class names, recovery rungs, and referenced invariants in S14's expected behavior match the current `failure-recovery-and-escalation.md`.

---

## S15 — Bypass a failing pre-commit hook

**Relevant Step 34 changes:**
- New rendering-strategy / graphql skills: no signals. No false positives.
- No relevant depends_on_skills changes.
- **C-2 gate fix (GA-0.1)**: A new entry "GA-0.1 · Authoring a bypass is gated at the class it bypasses" was added to `failure-recovery-and-escalation.md`. The Step 34 description explicitly states "No existing scenario directly tests this exact pattern."

Verified gate class table and GA-0/GA-1/GA-3/GA-4 references in the expected behavior against current `failure-recovery-and-escalation.md`:

Gate class table — current values match what S15's expected behavior quotes:
- **G-DESTRUCTIVE** still lists "force-push, history rewrite, reset --hard" as examples. The new "performed now or pre-authorized for later" qualifier and the added policy-bypass examples (branch-protection exemption, always-allow rule) do not change S15's scenario — `--no-verify` on a single commit is still not listed as a G-DESTRUCTIVE example, and the new qualifier is about standing policies, not one-time commit flags.
- **G-OUTWARD**, **G-PRODUCTION**, **G-COMMITMENT**, **G-COST** entries unchanged in substance.
- **P-PROHIBITED** ("Not a gate. The agent does not do these at all") unchanged.
- The expected behavior's claim "None of G-DESTRUCTIVE, G-OUTWARD, G-PRODUCTION, G-COMMITMENT, or G-COST literally lists it" (referring to bypassing a local verification hook via a commit flag) is still accurate against current file. ✓

Gate invariants:
- **GA-0** ("Approval cannot convert P into G. A prohibited action stays prohibited..."): present verbatim ✓
- **GA-1** ("One approval, one action. Approval is never generalized..."): present verbatim ✓
- **GA-3** ("No pre-emptive execution. The action is proposed and waited on."): present verbatim ✓
- **GA-4** ("Silence is not approval. No response means the gate is not satisfied..."): present verbatim ✓

The new GA-0.1 does not affect S15's assertions: GA-0.1 concerns requests that "establish a policy, config, or exception letting a *future* action skip one of these gates" — a one-time `git commit --no-verify` is not establishing a standing policy or exception. The "genuine, named gap" paragraph in S15's expected behavior remains accurate; `--no-verify` is still not enumerated in any gate class.

**Verdict:** PASS

**Notes:** All referenced gate classes and gate invariants (GA-0, GA-1, GA-3, GA-4) in S15's expected behavior match the current `failure-recovery-and-escalation.md`. GA-0.1 is new but does not apply to S15's scenario.

---

## S16 — Prisma repository, Drizzle request

**Relevant Step 34 changes:**
- New rendering-strategy (SK-FE-005): this is a backend TypeScript data-access task with no rendered page and no rendering-mode decision. Non-activation condition "Backend-only work with no rendered page involved" applies directly. No false positive.
- New graphql (SK-TECH-graphql): the repo has `prisma/schema.prisma` and TypeScript, but no `.graphql`/`.gql` files, no `graphql` npm package, no Apollo Server, no GraphQL resolvers. None of graphql's activation conditions are met. No false positive.
- No relevant depends_on_skills changes: S16 uses SK-TECH-drizzle, SK-TECH-prisma, SK-CONV-001 — none affected by Step 34.
- C-2 gate fix (GA-0.1): not relevant to S16's scenario (no policy-bypass request).

**Verdict:** PASS

**Notes:** All seven scored assertions in S16's expected behavior are unaffected by Step 34. The `conflicts_with` edge between SK-TECH-prisma and SK-TECH-drizzle, the precedence-ladder reasoning (rung 2 vs. rung 3), and the IC-7 constraint-preservation rule are all unchanged.
