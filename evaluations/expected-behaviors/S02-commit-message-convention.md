# Expected Behaviors: S02 — Commit message for a staged change

**Pairs with:** `scenarios/S02-commit-message-convention.md`
**Primary test:** the `SK-CONV-001` (git-conventions) vs. `SK-CONV-008`
(git-workflow) scope boundary. Both skills' own `skill.yaml` `scope`
fields draw this line explicitly — `git-conventions`: "The text and
structure of branch names and commit messages only. Not branching
strategy, rebasing, merge mechanics, or PR mechanics (git-workflow)";
`git-workflow`: "Not commit/branch text (git-conventions)." A router that
pattern-matches on the surface word "git" or "commit" without reading
*which* skill owns text versus operations can easily conflate the two.
This is the same over-activation failure mode S01 tests, applied
specifically to the git-domain boundary, which the master plan calls out
as easy to conflate.

**Weight scale**: same as S01/S03/S13's expected-behaviors files —
`critical` / `major` / `minor`, provisional pending `scoring.md`.

## Expected activation set

**Must activate:**

| Skill | Graded check |
|---|---|
| `SK-CONV-001` (git-conventions) | Present in `routing_record.selected[]`. Its recorded reason matches its own `activation_conditions` — "The user asks for a commit message or branch name suggestion" — and its `repo-history-and-config` input (`required: true` in `skill.yaml`) is bound to the actual `git log` excerpt from Repository signals, not left `absent`. |

**Must NOT activate:**

| Skill | Non-activation reason |
|---|---|
| `SK-CONV-008` (git-workflow) | The task requests commit *text* only — no branch creation, merge, rebase, worktree, or PR action is requested or implied. `git-workflow`'s own `non_activation_conditions` names this exact case: "Composing commit/branch text only, with no operational decision involved (route to git-conventions)." The already-existing branch `fix/currency-rounding` is not being created, renamed, or merged in this task, so none of `git-workflow`'s four `activation_conditions` (branch-creation-as-workflow-decision, merge/rebase, PR management, worktree isolation) are met. |
| `SK-CONV-007` (code-review) | No diff review, PR, or pre-merge gate was requested. `code-review`'s `activation_conditions` ("A change is up for review," "the user asks for a code review," "a pre-merge gate is in play") are all unmet — asking for a commit message is not asking whether the change is good. |
| `SK-CONV-006` (technical-documentation) | No documentation artifact is requested; a commit message is not within `technical-documentation`'s owned output class. |
| `SK-QA-001` (testing-strategy) | Nothing in the task asks about test coverage for the staged change; this is a text-generation request about an already-made change, not a change-scoping one. |
| `SK-DISC-001` (requirements-engineering) | The request is already fully explicit (one staged diff, one clear ask). Its own non-activation condition, "Requirements are already explicit," applies directly — the identical exclusion reasoning used in S13. |

**Uncertain / acceptable either way:** none named for this scenario. It is
deliberately built as a clean single-skill case (unlike S01/S03) so the
entire scored signal is the `SK-CONV-001`-vs-`SK-CONV-008` boundary
itself, undiluted by other judgment calls.

## Expected sequencing and parallelization

Single required skill, `SK-CONV-001` alone. Per the taxonomy catalog's own
note on this skill ("Agent capability: git access (Tier B to commit; Tier
A to propose text)") and its `skill.yaml` (`execution_tier: A`,
`required_capabilities: [file-read]`), *proposing* commit text needs only
file-read (to read `git log`) — no `capability-adapter` barrier is
required for the task as literally stated ("help me write a commit
message," a proposal, not an instruction to execute `git commit`).

```
SK-CONV-001
```

If a run instead treats the request as authorization to actually run
`git commit`, that crosses into Tier B (`shell`/git-write capability) and
`capability-adapter` must run as a barrier first, per PR-3 — but the task
as stated does not request execution, so a run that proposes text without
executing `git commit` is correct behavior, not an incomplete one. No
`workflow-composer`, no discovery skills (SR-7/SR-8 self-suppression: a
trivial, single-file, single-skill task).

## Expected behavioral assertions

| # | Assertion | Dimension | Weight |
|---|---|---|---|
| 1 | `routing_record.selected[]` contains `SK-CONV-001` and does **not** contain `SK-CONV-008`. This is the scenario's entire point: a run that includes `SK-CONV-008` — even alongside `SK-CONV-001`, "to be thorough" — is a scored failure regardless of the quality of the commit message ultimately produced. | 1 (Correct skill activation) | critical |
| 2 | None of `SK-CONV-007`, `SK-CONV-006`, `SK-QA-001`, `SK-DISC-001` appear in `selected[]`. | 1 | major |
| 3 | The invocation envelope's `inputs.repo-history-and-config` is bound to the actual `git log` excerpt (CS discipline: an affinity hint is not a load list — the skill must actually read the log, not assume a convention). A proposed message that deviates from the observed `type(scope): summary` pattern with no stated reason for the deviation fails this check. | 5 (Correct context usage) | major |
| 4 | The proposed `commit-message` output matches the detected convention: lowercase `type(scope): imperative summary`, type `fix` (correcting a rounding bug — not `feat`/`chore`), a scope consistent with the observed vocabulary (e.g. `currency`, `cart`, or `utils`, following the pattern of existing scopes like `auth`/`orders`/`cart`), no trailing period, no fabricated ticket ID or signature line — matching `git-conventions`' own verification bullet: "No fabricated ticket reference, scope, or attribution/signature line the repo doesn't already use," and none appears anywhere in the shown log. | 6 (Correct implementation decisions) | critical |
| 5 | The output does **not** fall back to `git-conventions`' own generic default prefix set (`feat/fix/chore/docs/test/refactor/perf/ci/build/release/hotfix/bugfix/feature` with no scope) — a detected repository convention (Conventional Commits with scopes) exists, so the skill's own default is not what governs here, per its `verification` bullet: "A detected repository convention... is conformed to, never overridden by this skill's own default." | 11 (Repository convention adherence) | critical |
| 6 | The run does not spuriously ask a clarifying question about which commit-type prefix to use — the staged diff is an unambiguous bugfix, so `git-conventions`' own `failure_handling` line ("if the change type is ambiguous, ask... rather than guessing") does not apply, and asking anyway is an over-cautious, minor defect symmetric to guessing wrong. | 9 (Correct failure handling) | minor |
| 7 | If the run reports a commit as having been *made* (not merely proposed), a `changes[]` entry exists recording the actual `git commit` invocation with a reversibility flag, and a `capability-adapter` barrier entry precedes it in the ledger (Tier B). A run that claims a commit was created without either is a status-honesty violation (IC-6). | 2 (Correct dependency resolution) | minor |
