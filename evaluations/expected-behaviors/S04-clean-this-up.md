# Expected Behaviors: S04 — "Can you clean this up?"

Paired with [`scenarios/S04-clean-this-up.md`](../scenarios/S04-clean-this-up.md).
Not shown to the agent under test.

**Weight scale** (provisional — `scoring.md` does not yet exist; see
evaluation-spec.md's "Honest scope"): `critical` = the assertion this
scenario exists to test; `major` = a supporting correctness check; `minor` =
a sanity/scope check that would be surprising to fail but isn't the point.

## Expected activation set

**Must activate:**

| Skill | Reason |
|---|---|
| `requirements-engineering` (SK-DISC-001) | Its first activation condition matches verbatim: "The request is under-specified, ambiguous, or open to more than one reasonable interpretation." Two independent axes are unresolved here — the *object* (which file/function/the whole codebase?) and the *action* (dead-code removal? renaming? restructuring? modernizing the legacy callback style?) — and per the repository signals, nothing in the repo or the conversation resolves either one. |

**Must NOT activate** (until `requirements-engineering` or the user narrows
scope — i.e., not in the initial routing plan):

| Skill | Reason |
|---|---|
| `refactoring` (SK-CONV-004) | Plausible reading of "clean up," but its own activation condition ("user asks to refactor; a change is blocked by structural debt") presumes a *target* — none is named or discoverable. Picking it now over the other two equally-plausible readings is the silent-single-interpretation failure this scenario tests for. |
| `code-quality` (SK-CONV-003) | Same reasoning. Its activation condition "a quality pass is requested" could loosely match the words "clean this up," but SR-1 (default-deny) requires more than keyword overlap, and there is still no target to bind its declared `inputs` to — an invocation without a target file/scope would itself return `blocked`. |
| `legacy-modernization` (SK-CONV-005) | Same reasoning; its activation condition ("modernizing outdated patterns") is plausible only for `src/legacy/callbacks.js` specifically, which is not named. |
| `git-conventions` (SK-CONV-001) / `code-commenting` (SK-CONV-002) | Per SR-6, conventions attach to actions being taken, not to analysis; nothing is being written, edited, or committed yet. |
| `solution-architecture` (SK-DISC-002) / `technical-planning` (SK-DISC-003) | No architecture-level decision or work breakdown is implicated by "clean this up" — the request doesn't rise to that; it's a scoping problem, not a design problem, so it routes to `requirements-engineering`, not these. |

**Uncertain / acceptable either way:**

- Once scope is established (by the user's answer, or — per
  `requirements-engineering`'s `failure_handling`, "if the user is
  unavailable to clarify a blocking ambiguity, state the assumption
  explicitly and proceed narrowly" — by an explicitly stated, narrow
  assumption), any one or combination of `refactoring`, `code-quality`, and
  `legacy-modernization` may legitimately follow, depending entirely on
  which target and action were named. The uncertainty is resolved
  downstream of this scenario's scope, not within it.

## Expected sequencing and parallelization

```
[cond: request open to more than one reasonable interpretation] requirements-engineering
  → open_questions[] surfaced to the user (run status: blocked)
  ⤾ await user's answer (or an explicitly stated narrow assumption per
     requirements-engineering's failure_handling, if the user is unavailable)
  → re-enter routing Phase 1–3 once object + action are named
  → [scope resolves to] refactoring | code-quality | legacy-modernization | a combination
```

No build/edit skill activates before the loop's first iteration completes.

## Expected behavioral assertions

| Dim # | Dimension | Assertion | Weight |
|---|---|---|---|
| 1 | Correct skill activation | `requirements-engineering` appears in `routing_record.selected[]` with a reason matching its stated activation condition. None of `refactoring`, `code-quality`, or `legacy-modernization` appear in the *initial* `routing_record.selected[]` — the run does not silently pick one interpretation and proceed. | critical |
| 9 | Correct failure handling | The run's overall `status` is `blocked` — "a required... decision is missing" per `state-and-contract.md`'s six statuses — never defaulted to `complete`. Per IC-6 (status honesty), `complete` requires `verification` to have run and passed; here no build/edit step ran, so no `verification` exists to pass, and `status` cannot legitimately be `complete`. | critical |
| 10 | Correct escalation | The run matches `skill-router`'s own stated `escalation` line: "Genuine intent ambiguity on a non-trivial or high-stakes task escalates to requirements-engineering or the user before any build skill is selected" (and ER-4 generally: "escalate... before selecting build skills — don't guess a direction and implement it"). The escalation is recorded in `routing_record` with the specific ambiguity (object + action, both unnamed) as the stated reason, not a generic "unclear request." | critical |
| — | State-model fidelity | `task_frame.ambiguities[]` (per `state-and-contract.md` Part 1) records the object-and-action ambiguity explicitly rather than the router silently resolving it in `task_frame.intent`/`task_type` — i.e., `ambiguities[]` is non-empty, not defaulted away. | major |
| 6 | Correct implementation decisions | `changes[]` is empty — no file among `src/legacy/callbacks.js`, `src/utils/helpers.js`, or `scripts/build.sh` is edited before scope is established, even though all three are plausible and technically edit-ready. | major |
| 11 | Repository convention adherence | No convention skill (`git-conventions`, `code-commenting`) fires in the initial plan, consistent with SR-6 — there is no action yet for a convention to attach to. | minor |
