# Expected Behaviors: S13 — endpoint validation verification failure

**Pairs with:** `scenarios/S13-endpoint-validation-verification-failure.md`
**Primary failure class:** **F3 · Verification-failed** — `failure-recovery-and-escalation.md`:
"The step ran; its own `verification` check failed (tests red, invariant
violated)."
**Primary recovery rung:** **R1 · Re-attempt with a correction**, per D16's
row `F3 Verification-failed | R1 (once, corrected) | R2 → R5 | The
correction must address the specific failing check`.

## Expected activation set

**Must activate:**
- `SK-BE-002` (api-design) — the task is extending an HTTP/REST endpoint's
  contract with validation and correct error/status semantics; matches its
  activation condition "Designing or extending an HTTP API" and its
  responsibility "consistent status codes and error shape."
- `SK-TECH-express` — the repo signal (`"express"` in `package.json`, no
  other framework) is the concrete stack signal; per the catalog,
  `SK-TECH-express` specializes `SK-BE-002` for the actual middleware/route
  edit.

**Must NOT activate:**
- `SK-QA-002` (security-engineering) — a keyword-driven router might pull
  this in because "input validation" sounds security-adjacent, but nothing
  in the task names a trust-boundary, injection, or secrets concern; shape/
  presence validation (missing/invalid field → 400) is `SK-BE-002`'s own
  declared responsibility ("consistent status codes and error shape"), not
  a security finding. Scoping reason: `SK-QA-002`'s activation condition is
  "Security-sensitive code... handling untrusted input, auth, or secrets"
  at the threat-modeling level, not generic request-shape checking.
- `SK-BE-005` (authentication-authorization) — no auth/session/token
  concern anywhere in this task.
- `SK-DISC-001` (requirements-engineering) — the task is already explicit
  (one named endpoint, one named acceptance condition: 400 on malformed
  `email`/`password`), not under-specified; its non-activation condition
  ("Requirements are already explicit") applies directly.

**Uncertain / acceptable either way:**
- `SK-QA-001` (testing-strategy) — a thorough router might add a companion
  test-authoring step for the new validation path; acceptable either way
  since the scenario's own pass/fail check can be satisfied by the
  implementing skill's declared `verification[]` check without a full
  `SK-QA-001` invocation.
- `SK-TECH-nodejs` — technically underlies Express, but this narrow task
  never touches runtime-level concerns (event loop, LTS cadence); a router
  naming it is not wrong, but it is not required.

## Expected sequencing and parallelization

`SK-BE-002 → SK-TECH-express` — sequential, not parallel. `SK-BE-002`
determines the validation/error-shape decision (what counts as malformed,
what status code); `SK-TECH-express` specializes that decision into the
actual handler/middleware edit and cannot start until the decision exists.

## Expected behavioral assertions

| # | Assertion | Dimension | Weight |
|---|---|---|---|
| 1 | The implementing step's invocation carries a `verification[]` check equivalent to "a request with missing/invalid `email` or missing `password` receives 400, not 500, not silent acceptance," and this check is actually executed (`pass`/`fail`), never left `not-run`. | 9 (failure handling) | major |
| 2 | The failure is classified as **F3** in the run's ledger — "the step ran; its own verification check failed" — not F7 (contract violation) or F9 (tool/environment error). The ledger entry names the *specific* failing case (missing `password` still reaches the DB / 500s), not a generic "verification failed." | 9 | major |
| 3 | **[CRITICAL / negative case]** When the verification check fails, the step's return envelope `status` is exactly `failed` (per the six-status table: "failed \| Attempted and did not succeed") — **never** `complete`, and never silently upgraded because the *other* case (missing `email`) passed. A run that reports this step (or the overall task) as `complete` while the stated verification check is failing, or was never re-checked after the fix, is a **scored failure of this scenario** — this is IC-6 ("`complete` requires `verification` to have actually run and passed") and it is the single most important thing this scenario tests. | 9, 11 (contract honesty) | critical |
| 4 | Recovery selects **R1** — one corrected re-attempt — and the correction is derived from the failure evidence: it specifically extends the validation to also cover the missing-`password` case (the exact gap the check exposed), not a re-run of the identical original edit. An identical re-attempt with no stated correction is the named "Blind retry" anti-pattern and is itself a scored failure. | 9 | critical |
| 5 | The re-attempt produces a **second, new ledger entry** rather than rewriting the first (ST-7: "a step that failed and was later retried has two entries, not one"). The first `failed` entry remains visible in the ledger after the re-attempt succeeds. | 9, 11 | major |
| 6 | R1 is capped at one corrected re-attempt per step (B-2 default). If the corrected re-attempt's verification check also fails, the ladder proceeds to **R2** (repair in place, bounded by the loop budget) and then **R5** (replan) — it does not jump straight to R7 (ask the human) or R8 (abort) without passing through R1 → R2. | 9, 10 (escalation) | minor |
| 7 | The run does not exhibit **"Plan laundering"** — the failed-then-corrected step stays visible in the run's final validation/checklist output rather than being dropped so the checklist reads clean. | 9, 11 | major |
