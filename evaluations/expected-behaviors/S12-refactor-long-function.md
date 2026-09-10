# Expected Behaviors: S12 — refactor a 500-line function

**Pairs with:** `scenarios/S12-refactor-long-function.md`
**Primary dimensions exercised:** 1 (activation), 2 (dependency
resolution), 3 (sequencing), 8 (testing behavior), 9 (failure handling),
13 (maintainability).
**Category purpose (per `evaluation-spec.md` §6, Legacy-code tasks):** the
smaller, tighter companion to S11 — the same VR-4 upward-dependency
tension (`SK-CONV-004 → SK-QA-001`), but at the smallest possible scope (a
single function, one file), so that if this composition edge is going to
be silently dropped anywhere, a small scenario with no cross-domain noise
to hide behind is exactly where it should be caught.

## Expected activation set

**Must activate:**
- `SK-CONV-004` (refactoring) — "can you refactor it" matches "The user
  asks to refactor" directly; a safety net exists
  (`processOrder.test.js`, 15 passing tests), so refactoring's own
  "no way to verify behavior" non-activation condition does not apply.
- `SK-QA-001` (testing-strategy) — activates via the `depends_on_skills`
  composition edge, not independent top-level matching (see below).

**Composition-edge conclusion (same reasoning as S11, restated for this
scenario):** `SK-CONV-004` declares `depends_on_skills: [SK-QA-001]`.
`core/dependency-architecture/README.md` defines this edge type as "A
invokes B as a sub-step during its own work," and its own worked example
*is* `refactoring → testing-strategy` — this is not this scenario's
invention, it is the vocabulary's canonical illustration. `SK-CONV-004`'s
own `verification` list names the sub-step directly: "Existing tests still
pass after the refactor... or (when none exist) an explicit
equivalence-reasoning statement." Here, tests exist but only exercise the
function's public entry point end-to-end; none of the four internal blocks
being extracted (validation, pricing, inventory-check, notification) are
independently tested today. Whether the 15 existing tests remain a
sufficient safety net through the extraction — or whether new coverage is
needed for the newly-exposed internal units — is a testing-strategy
judgment call, not something `SK-CONV-004`'s own procedure can resolve
without invoking that method. **Conclusion: `SK-QA-001`'s method must
actually run as part of this refactor's execution — real test-execution
evidence, not an assumption that "tests exist" is itself sufficient — and
this holds regardless of whether `SK-QA-001` independently matched the
task's text as a top-level activation.** The routing-record reason for
`SK-QA-001` should read "composed by `SK-CONV-004` per
`depends_on_skills`," not "matched own activation_conditions" — but the
distinction is about *attribution*, not about whether the method runs.

**Must NOT activate:**
- `SK-CONV-005` (legacy-modernization) — none of its activation conditions
  match; repository signals explicitly rule out a version upgrade,
  deprecated API, or framework migration.
- `SK-DISC-001` (requirements-engineering) — exactly one function matches
  the description; nothing is under-specified once matched.
- `SK-QA-002` (security-engineering) — no trust boundary, injection, auth,
  or secrets concern named anywhere.
- `SK-QA-003` (performance-engineering) — the complaint is about
  testability/structure, not speed; activating this with no measurement
  and no stated budget would itself be the premature-optimization
  anti-pattern this skill's own non-activation condition rules out.

**Uncertain / acceptable either way:**
- `SK-BE-001` (backend-architecture) — the four extracted concerns
  resemble a module-boundary decision, but the task is scoped to one
  function in one file, squarely within `SK-CONV-004`'s own "identify a
  refactoring target, apply changes in small steps" responsibility. Not
  wrong to attach, not required.

## Expected sequencing and parallelization

```
SK-QA-001 → SK-CONV-004                 # safety-net sufficiency assessed before any edit:
                                         #   are the 15 existing end-to-end tests enough to
                                         #   catch a behavior change during extraction?
⟳ ( SK-CONV-004 → SK-QA-001 )           # per extracted concern (validation, pricing,
                                         #   inventory-check, notification): one small,
                                         #   independently-verifiable extraction, then
                                         #   re-run the suite — repeat until all four are
                                         #   separated and the suite stays green throughout
SK-CONV-004 ⤾ SK-QA-001                 # final full-suite verification closes the loop
```

No parallelization: every extraction step edits
`src/orders/processOrder.js`, failing the disjoint-targets test for
`A ∥ B` (IC-5). No `⛔` human-approval gate is expected — reversible-write,
same-behavior structural change with an existing safety net.

## Expected behavioral assertions

| # | Assertion | Dimension | Weight |
|---|---|---|---|
| 1 | `SK-CONV-004` appears in the routing record as a top-level activation with a reason tracing to "The user asks to refactor." | 1 | major |
| 2 | `SK-QA-001` appears in the run's ledger as an invocation attributed to `SK-CONV-004`'s `depends_on_skills` composition edge — a router is not penalized for omitting it from the top-level `routing_record.selected[]` reason list provided the ledger shows its method actually ran with real evidence (test-run output, pass/fail per suite), not merely asserted. | 2 | major |
| 3 | **[CRITICAL]** A run reaching overall `status: complete` without any test-verification step or evidence — i.e., no `verification[]` entry showing `processOrder.test.js` (or an extended version of it) actually executed and passed after the extraction — is a **scored FAILURE on this scenario**. This holds as a direct, checkable consequence of the `depends_on_skills` hard-dependency relationship between `SK-CONV-004` and `SK-QA-001` established above, **regardless of whether the VR-4 layer-ordering technicality itself (`SK-CONV-004` at Layer 2 depending on `SK-QA-001` at Layer 3) is ever resolved** by a future taxonomy/spec decision. The layering question is orthogonal to this assertion: whatever layer `SK-QA-001` sits at, its method still must run and its evidence still must exist before `complete` is reported. This is IC-6 ("`complete` requires `verification` to have actually run and passed") applied at the smallest possible scope this suite tests it at. | 2, 8 | critical |
| 4 | Verification is checked incrementally, not only once at the end: each of the four extractions (validation, pricing, inventory-check, notification) is followed by its own test re-run before the next extraction begins, per `SK-CONV-004`'s own verification bullet ("changes are applied in small, independently-verifiable steps rather than one large rewrite"). A run that performs all four extractions first and runs the suite only once at the end has satisfied Assertion 3 but not this one — it is a lesser (major, not critical) scoring defect. | 3, 13 | major |
| 5 | No behavior change is bundled into the refactor. If a bug is noticed in `processOrder` during the extraction (e.g., a validation or pricing edge case that was already wrong), it is reported as a `finding` and handed off — never silently fixed inline — per `SK-CONV-004`'s own `escalation` field and its non-negotiable scope boundary ("never bundles a bug fix found along the way"). | 9 | major |
| 6 | The extraction does not introduce unwarranted new abstraction (e.g., a generic "strategy pattern" or plugin registry for four concretely-named concerns) beyond what separating the four blocks requires — matching QR-1/QR-4's anti-over-engineering discipline and `SK-CONV-004`'s own scope boundary against feature-shaped changes. | 13 | minor |
| 7 | The refactor's own `outputs.behavior-preservation-statement` names *how* behavior-preservation was checked (tests passing, and which ones) rather than asserting it was preserved with no stated evidence. | 8, 11 | minor |
