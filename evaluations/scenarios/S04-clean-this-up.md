# Scenario: S04 — "Can you clean this up?"

**Category:** Ambiguous tasks
**Complexity:** unknown — cannot be classified from the request; the object of
"clean up" is unstated, so scope (one function? one file? the codebase?)
cannot be sized. This mirrors
[routing-architecture/examples.md](../../core/routing-architecture/examples.md)
Example 8 ("Make it better."), which the router itself classifies as
`unknown` across every determination rather than guessing a value.
**Risk level:** unknown — for the same reason; risk depends entirely on what
"this" and "clean up" turn out to mean, neither of which is stated.

## Task

"Can you clean this up?"

This is the entire, verbatim opening message of a fresh session — there are
no prior turns in this conversation to draw on, no file was discussed
before it, and no code block or path accompanies the request.

## Repository signals

- This is the first message of a new session: no file is open, no diff is in
  progress, and nothing was pasted or attached alongside the request.
- `git status` is clean — no staged or unstaged changes exist — so there is
  no in-progress edit or diff that "this" could plausibly be pointing at.
- The repository is mid-sized and contains several roughly-equally-plausible
  cleanup candidates, none singled out by recency, an open editor tab, or a
  referenced ticket:
  - `src/legacy/callbacks.js` — deeply nested, old-style Node callback code
    (a plausible `legacy-modernization`/`refactoring` target).
  - `src/utils/helpers.js` — a 40-function grab-bag file with inconsistent
    naming and several unused (dead) exports (a plausible `code-quality`/
    `refactoring` target).
  - `scripts/build.sh` — a shell script containing large commented-out
    blocks of dead code (a "cleanup" of a different kind entirely, unrelated
    to the two candidates above).
- No `TODO`/`FIXME` marker, issue-tracker reference, or recent commit message
  (checked via `git log -5`, which shows unrelated feature commits, none
  mentioning cleanup) points at any one of these over the others.
