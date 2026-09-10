# Scenario: S14 — test suite shell capability loss

**Category:** Failure scenarios
**Complexity:** multi-step
**Risk level:** reversible-write

## Task

> Run the test suite and fix any failing tests.

## Repository signals

- `package.json` has a `"test": "jest"` script; `jest.config.js` present;
  spec files under `__tests__/` and co-located `*.test.js` files.
- At session start, shell/terminal execution is granted (the run begins
  Tier B: the agent can actually invoke `npm test`).
- Running the suite at the outset shows **3 failing tests**, each with a
  distinct, legible cause (e.g. a changed function signature, a stale
  snapshot, an off-by-one in a date helper) — nothing requiring design
  work, just fixes.

This scenario additionally stipulates a **run-time event**, not a repo file
signal: after the first failing test is fixed and shell-verified green, the
run's shell/execution capability is revoked before the remaining two
failing tests are addressed. (Realistic trigger, either is acceptable to
assume: the host's permission mode changes mid-session from
execute-allowed to plan-only, or the remainder of the task is handed to a
sub-agent invoked without shell access.) No fallback test-execution tool
(no MCP test-runner, no CI trigger the agent can invoke and observe) is
present in this environment.
