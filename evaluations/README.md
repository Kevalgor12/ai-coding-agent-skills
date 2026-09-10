# evaluations

The behavioral evaluation suite for the Skill Library — task scenarios,
expected behaviors, and scoring used to measure whether a skill actually
causes an agent to behave correctly, not just whether its prose reads well.

This is about measuring the library's *effectiveness*. Compliance/safety/
quality review of a skill's own content belongs in
[`audits/`](../audits) instead.

## Files

- **[`evaluation-spec.md`](evaluation-spec.md)** — the 15 behavioral
  dimensions evaluated, the scenario/expected-behavior schema, the 8
  required scenario categories, and this suite's honest scope (no
  executable harness exists yet — see below).
- **[`scenarios/`](scenarios/)** — 16 task scenarios (task + repository
  signals + expected activation set + expected sequencing, no answer key),
  2 per required category.
- **[`expected-behaviors/`](expected-behaviors/)** — the paired, graded
  assertion list per scenario, one file per scenario under the same base
  filename.
- **[`scoring.md`](scoring.md)** — how an assertion list becomes a scenario
  verdict (`complete`/`partial`/`failed`/`blocked`) and a suite-level
  summary.
- **[`regression-suite.md`](regression-suite.md)** — what triggers a
  re-run, how to run a scenario today (manually — no harness exists), how
  to track results over time, and where the suite's coverage gaps are.

## Status

First content authored 2026-09-10 (Step 30 of this project's master build
plan). No executable test runner exists — running a scenario today means a
human, or an agent explicitly briefed to role-play the orchestrator,
works through the task using the real skill files, then scores the result
against the matching `expected-behaviors/` file. Coverage is partial: 77
of 86 authored skills appear somewhere across the 16 scenarios; extending
coverage and building an automated harness are both named as future work
in `regression-suite.md`, not silently assumed done.
