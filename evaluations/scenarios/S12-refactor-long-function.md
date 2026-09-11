# Scenario: S12 — Refactor a 500-line function

**Category:** Legacy-code tasks
**Complexity:** small (a single, bounded target — one function, one file —
with no cross-domain spread; the test is about *process discipline* within
a small scope, not about scale)
**Risk level:** reversible-write (code edits only, fully revertible via VCS)

## Task

"This function is 500 lines long and hard to test, can you refactor it?"

This is the complete, verbatim request. No file path is named explicitly,
but exactly one function in the repo matches the description.

## Repository signals

- `src/orders/processOrder.js` exports a single function `processOrder(...)`,
  roughly 500 lines, mixing input validation, pricing calculation, an
  inventory-check side effect, and email-notification dispatch inline, with
  deeply nested conditionals throughout. No internal helper is separately
  exported — everything is reachable only through the one entry point.
- `tests/orders/processOrder.test.js` exists and currently passes: ~15 unit
  tests exercising `processOrder`'s public entry point end-to-end (inputs in,
  observable outputs/side-effect calls asserted). None of the internal logic
  blocks (validation, pricing, inventory check, notification) are tested in
  isolation, since none are currently exposed to test individually.
- `package.json`: plain JavaScript/Node project, `jest` already configured
  as the test runner. No TypeScript, no other framework-specific tooling
  relevant to this function.
- `.github/workflows/ci.yml` runs `npm test` on every PR; the suite is
  currently green.
- Nothing in the repo signals a version upgrade, a deprecated API, or a
  framework migration anywhere near this function — this is a same-version,
  same-stack structural complaint about one function's shape, not a
  modernization task.

## Expected activation set

**Must activate:**
- `SK-CONV-004` (refactoring) — the task's own words are "can you refactor
  it," matching the activation condition "The user asks to refactor"
  directly, and a safety net exists (`processOrder.test.js`, 15 passing
  tests), so the "no way to verify behavior" non-activation condition does
  not apply.
- `SK-QA-001` (testing-strategy) — activates via `SK-CONV-004`'s
  `related_skills` link and `SK-CONV-004`'s own verification requirements,
  not as an independent top-level activation. See "Verification grounding"
  below.

**Verification grounding.** `SK-CONV-004` lists `SK-QA-001` in
`related_skills` (not `depends_on_skills` — the VR-4 layer-monotone rule
bars a Layer 2 skill from hard-composing a Layer 3 skill). The behavioral
requirement for test-based behavior-preservation is instead enforced
directly through `SK-CONV-004`'s own `verification` section, which
includes the execution-dependent item: "The test suite is actually run
after the refactor (not just reviewed for structure) and produces a green
result, confirming behavior is preserved in the real execution
environment." Deciding *whether* the 15 existing end-to-end tests are a
sufficient safety net for extracting four previously-untested internal
blocks (validation, pricing, inventory-check, notification) out of one
function — versus needing new tests for the newly-exposed units — is
itself a testing-strategy judgment that `SK-QA-001` (via `related_skills`)
is the appropriate resource for. Conclusion, stated explicitly: `SK-QA-001`
should appear in the run's ledger with a reason of "testing-strategy
input, composed with `SK-CONV-004` via `related_skills`" — not as a
top-level independent activation. IC-6 ("`complete` requires
`verification` to have actually run and passed") makes the test-run
requirement binding at completion time.

**Must NOT activate:**
- `SK-CONV-005` (legacy-modernization) — none of its activation conditions
  (major-version upgrade, modernizing outdated patterns, migrating off a
  deprecated approach) match; the repository signals explicitly rule this
  out ("no version upgrade, no deprecated API, no framework migration").
- `SK-DISC-001` (requirements-engineering) — exactly one function in the
  repo matches the description; the request, while short, is unambiguous
  once matched to `processOrder`. Nothing here is under-specified in the
  way that would warrant this skill.
- `SK-QA-002` (security-engineering) — nothing in the task or signals
  names a trust boundary, injection, auth, or secrets concern.
- `SK-QA-003` (performance-engineering) — the complaint is about
  testability/structure ("hard to test"), not speed; activating a
  performance skill here with no measurement and no stated budget would be
  exactly the premature-optimization anti-pattern `SK-QA-003`'s own
  non-activation condition rules out.

**Uncertain / acceptable either way:**
- `SK-BE-001` (backend-architecture) — `processOrder` is business/backend
  logic, and one could argue the four extracted concerns (validation,
  pricing, inventory, notification) resemble a module-boundary decision.
  But the task is scoped to one function in one file, well within
  `SK-CONV-004`'s own "identify a refactoring target, apply changes in
  small steps" responsibility; a router that also attaches
  `SK-BE-001` is not wrong, but it is not required for a bounded,
  single-function extraction.

## Expected sequencing and parallelization

```
SK-QA-001 → SK-CONV-004                 # safety-net assessed first: are the 15 existing
                                         #   end-to-end tests sufficient to catch a behavior
                                         #   change during extraction, before any edit is made
⟳ ( SK-CONV-004 → SK-QA-001 )           # per extracted concern (validation, then pricing, then
                                         #   inventory-check, then notification): apply one small,
                                         #   independently-verifiable extraction, then re-run the
                                         #   test suite — repeat until all four are separated and
                                         #   the suite stays green throughout
SK-CONV-004 ⤾ SK-QA-001                 # final full-suite verification closes the review/fix loop
```

No parallelization applies: every extraction step edits the same file
(`src/orders/processOrder.js`), which fails the disjoint-targets test for
`A ∥ B` (IC-5), and each extraction must be verified before the next is
attempted (small, independently-verifiable steps, not a single large
rewrite). No human-approval gate (`⛔`) is expected — this is a
reversible-write, same-behavior structural change with an existing safety
net, not a destructive or production-affecting action.
