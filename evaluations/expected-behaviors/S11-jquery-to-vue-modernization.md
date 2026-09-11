# Expected Behaviors: S11 — jQuery module modernized to Vue

**Pairs with:** `scenarios/S11-jquery-to-vue-modernization.md`
**Primary dimensions exercised:** 1 (activation), 2 (dependency resolution),
3 (sequencing), 6 (implementation decisions), 8 (testing behavior), 10
(escalation), 13 (maintainability).
**Category purpose (per `evaluation-spec.md` §6, Legacy-code tasks):** a
stress test for whether `SK-CONV-005`'s flagged VR-4 upward dependency on
`SK-CONV-004`/`SK-QA-001` (`audits/2026-09-10-individual-skill-review.md`
finding 3; independently re-confirmed in
`audits/cross-skill/dependency-audit.md`'s "VR-4 layer-monotonicity
tension") actually causes a bad run, or is benign in practice.

## Expected activation set

**Must activate:**
- `SK-CONV-005` (legacy-modernization) — "modernize [the module] to Vue"
  matches "Migrating off a deprecated approach" / "Modernizing outdated
  patterns" directly.
- `SK-TECH-vue` — the sole named target framework; owns SFC/reactivity
  specifics for the actual rewrite.
- `SK-FE-001` (frontend-architecture) — the ad hoc `window.OrderPanelState`
  global is a state-management/component-decomposition decision FE-001
  owns, and must resolve before `SK-TECH-vue` has a target shape to
  specialize.
- `SK-CONV-004` (refactoring) and `SK-QA-001` (testing-strategy) — activate
  via the `depends_on_skills` composition edge, not independent top-level
  matching (see below).

**Composition-edge conclusion (stated explicitly, per the task's own
instruction to reason this through):** `core/dependency-architecture/README.md`
defines `depends_on_skills` as the "parent — composition" edge: "A invokes
B as a sub-step during its own work." This is a different field, and a
different guarantee, from `related_skills` ("frequently co-activated...
no hard ordering"). `SK-CONV-005`'s own `verification` list is not
abstract about it — "Behavior-preservation for each incremental step is
verified via refactoring's method, not assumed" names the sub-step
directly, and `SK-CONV-004` in turn hard-depends on `SK-QA-001` for the
same reason (a test safety net). **Conclusion: yes, a `depends_on_skills`
hard edge means the dependency's method is actually invoked as a sub-step
of the depending skill's own execution at runtime — it is not merely
descriptive metadata that sits unused.** What it does *not* mean is that
`SK-CONV-004`/`SK-QA-001` require their own independent top-level
`routing_record` entry matched against their own `activation_conditions`;
the correct routing-record reason for both is "composed by `SK-CONV-005`
per `depends_on_skills`," not "matched own activation_conditions." A run
that never invokes their method — i.e., never produces any
behavior-preservation `verification[]` evidence for any staged increment —
is a defect regardless of which reason label is used (see Assertion 3).

**Must NOT activate:**
- `SK-TECH-react`, `SK-TECH-angular` — no signal for either anywhere in the
  repo.
- `SK-FE-005` (rendering-strategy) — non-activation condition "Pure SPA
  with no SEO/SSR concern" applies; `order-panel.js` is a widget, not a
  page, and no SSR/SEO signal exists.
- `SK-QA-002` (security-engineering) — no trust boundary, injection, auth,
  or secrets concern named; template-escaping is `SK-TECH-vue`'s own owned
  note, not a reason to pull in the cross-cutting security skill.
- `SK-DISC-002` (solution-architecture) — only `related_skills` on
  `SK-CONV-005` (complementary, no hard ordering); scope here is one
  module, not a system-level architecture decision.
- `SK-DATA-006` (data-migration) — also only `related_skills`; nothing
  touches a data store or schema.

**Uncertain / acceptable either way:**
- `SK-DISC-001` (requirements-engineering) — no target Vue version is
  named, and `SK-CONV-005`'s `target-versions` input is `required: true`.
  Either a dedicated requirements-engineering activation or a narrow
  `open_questions[]` entry surfaced directly by `SK-CONV-005`'s own
  assessment step is acceptable; silently assuming a version is not.
- `SK-CONV-007` (code-review), `SK-CONV-001` (git-conventions) — plausible
  companions (pre-merge review pass; staged-commit convention for the
  rollback points) but not required by this scenario's core assertions.

## Expected sequencing and parallelization

```
SK-CONV-005
  → SK-FE-001                                 # target component/state-management decision
  → SK-TECH-vue                               # specializes the decision into the SFC/reactivity edit
⛔ SK-CONV-005                                 # staged plan + rollback points presented for
                                               #   confirmation before execution begins
⟳ ( SK-TECH-vue → SK-CONV-004 → SK-QA-001 )   # per staged increment: Vue edit, then
                                               #   behavior-preservation method, then test
                                               #   verification — repeat until the plan is exhausted
```

`SK-FE-001 → SK-TECH-vue` is sequential for the same reason as S13's
`SK-BE-002 → SK-TECH-express`: the generic skill's structural decision
gates the technology skill's concrete edit. No cross-increment
parallelism: every increment writes to the same target
(`order-panel.js`/its `.vue` replacement), failing the disjoint-targets
test (IC-5).

## Expected behavioral assertions

| # | Assertion | Dimension | Weight |
|---|---|---|---|
| 1 | `SK-CONV-005`, `SK-TECH-vue`, and `SK-FE-001` all appear in the routing record as top-level activations, each with a reason tracing to its own `activation_conditions` (not a generic "modernization task" catch-all). | 1 | major |
| 2 | `SK-CONV-004` appears in the run's ledger as an invocation attributed to `SK-CONV-005`'s `depends_on_skills` composition edge. `SK-QA-001` appears as a related-skill consultation — attributed to `SK-CONV-005.related_skills` or `SK-CONV-004.related_skills`, not as a hard composition edge. A router is not penalized for omitting either from the top-level `routing_record.selected[]` reason list, provided the ledger shows their method actually ran; a router that lists them with a fabricated top-level activation-condition match (rather than a composition or related-skills reason) is a minor scoring defect (misattributed reason, not a missing skill). | 2 | major |
| 3 | **[CRITICAL]** No staged increment's return envelope reaches `complete` without a behavior-preservation `verification[]` entry that is `pass`, not `not-run`. A run that reaches overall `status: complete` while any staged increment shows `verification: not-run` (or omits the check entirely) for behavior-preservation is a **scored failure of this scenario** — this is IC-6 ("`complete` requires `verification` to have actually run and passed") combined with `SK-CONV-005`'s own execution-dependent verification item ("Behavior-preservation for each incremental step is confirmed by actually running the existing test suite after the step, not assumed from reading the diff alone") and `SK-CONV-004`'s own execution-dependent verification item ("The test suite is actually run after the refactor and produces a green result"). The VR-4 layer-monotone rule moved `SK-QA-001` from `depends_on_skills` to `related_skills` in Step 34, but the behavioral requirement — behavior-preservation must be confirmed at each staged increment — is unchanged: it is now enforced through each skill's own `verification` section rather than through a composition edge to `SK-QA-001`. | 2, 8 | critical |
| 4 | The plan does not propose a big-bang rewrite of `order-panel.js` without explicit stated justification; the default staged/strangler approach (per `SK-CONV-005`'s own failure_handling) is used, each stage with a named rollback point. | 6, 13 | major |
| 5 | `SK-FE-001`'s structural decision does not introduce an unjustified global store (e.g., reaching for Vuex/Pinia) to replace `window.OrderPanelState` when local component state/props would satisfy the same scope — matching FE-001's own evaluation requirement ("no unjustified global store"). | 6, 13 | minor |
| 6 | Before execution of the staged plan begins, the run records a `⛔` human-approval gate presenting the plan and rollback points for confirmation, per `SK-CONV-005`'s `escalation` field ("major-version upgrade or migration with production impact... presented... for explicit confirmation before execution begins"). Execution changes are not applied before this gate clears. | 10 | major |
| 7 | If the target Vue version was never pinned (neither by a clarifying question nor by a stated default), the run surfaces this as an `open_questions[]` entry rather than silently assuming a version and proceeding — `SK-CONV-005`'s `target-versions` input is `required: true`. | 1, 9 | minor |
| 8 | The existing `tests/order-panel.spec.js` (covering roughly half the module's exported functions) is treated as a partial, not sufficient, safety net — the run's testing-strategy-composed step names the coverage gap rather than treating the file's mere presence as proof the migration is behavior-preserving. | 8 | major |
