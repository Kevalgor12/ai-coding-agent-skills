# Expected Behaviors: S01 — PostgreSQL duplicate-rows query bug

**Pairs with:** `scenarios/S01-postgresql-duplicate-rows.md`
**Primary test:** over-activation avoidance. Per `evaluation-spec.md`'s
category interpretation of "Simple tasks" — "a single, unambiguous skill
clearly owns the task... the main failure mode here is false-positive
activation, not a missing skill." A run that correctly activates
`SK-TECH-postgresql` but also pulls in even one skill from the Must-NOT-
activate list has failed this scenario's central point, independent of
whether the query fix itself is correct. A secondary, equally load-bearing
test is whether the fix is a *real* deduplication (aggregation or window
function preserving the required item count), not a cosmetic patch — see
the dimension-6 assertion below.

**Weight scale** (provisional — `scoring.md` does not yet exist, same
caveat as S03/S13's expected-behaviors files): `critical` = the assertion
this scenario exists to test; `major` = a supporting correctness check;
`minor` = a sanity/scope check that would be surprising to fail but isn't
the point.

## Expected activation set — graded

The scenario file's own "Expected activation set" section already states
the reasons; this restates each as what must be mechanically checkable in
`routing_record`.

**Must activate (1 required):**

| Skill | Graded check |
|---|---|
| `SK-TECH-postgresql` | Present in `routing_record.selected[]`. Its recorded reason cites at least one of its own `skill.yaml` `activation_conditions` — PostgreSQL named in the task text, and/or the `pg` driver plus the raw-SQL repository file detected — not a generic "database task" rationale. |

**Must NOT activate (the scenario's full exclusion list — none of these
IDs may appear in `routing_record.selected[]`):** `SK-FE-001`,
`SK-TECH-react`, `SK-FE-002`, `SK-FE-004`, `SK-GROW-001`,
`SK-TECH-threejs`, `SK-TECH-webrtc`, `SK-BE-004`, `SK-CONV-006`,
`SK-CONV-001`, `SK-CONV-004`, `SK-CONV-007`, `SK-QA-003`, `SK-DATA-001`,
`SK-DATA-002`, `SK-BE-001`.

The graded check is strictly non-membership in `selected[]`. Per SR-11's
completeness-backstop discipline a well-formed run *also* records each in
`routing_record.excluded[]` with a matching reason, but a run that omits
some of them from `excluded[]` (silent non-consideration, as opposed to
considered-and-rejected) is not itself scored as an error here — only
appearing in `selected[]` is. `SK-TECH-react` is the single most important
entry to check: it *is* detected in `frontend/package.json`, so a
detection-only router (applying SR-3 alone, without SR-1's second conjunct
— "and the task type needs it") is the specific false-positive this
scenario is built to catch.

**Uncertain / acceptable either way (do not score as an error in either
direction):** `SK-DATA-003` (database-operations), `SK-CONV-002`
(code-commenting), `SK-CONV-003` (code-quality), `SK-QA-001`
(testing-strategy) — see the scenario file for the per-skill reasoning.
A run is not penalized whether it includes or excludes any of these four.

## Expected sequencing and parallelization — graded

The ledger shows a `capability-adapter` invocation (PR-3 barrier)
immediately preceding `SK-TECH-postgresql`'s own invocation entry,
resolving shell/DB-execute capability — this follows directly from
`SK-TECH-postgresql`'s own `skill.yaml`: `execution_tier: B`,
`required_capabilities: [file-read, file-write, shell]`. No
`workflow-composer` entry appears anywhere in `routing_record` or `plan`
(SR-7 self-suppression: single-stage task). No discovery-skill entries
appear (SR-8: this is a bounded single-file change, not multi-domain or
high-risk). No `A ∥ B` parallel edge is recorded in `plan.stages` — one
skill, one file, one target, matching the scenario's own statement that
"no parallel opportunity exists."

```
capability-adapter → SK-TECH-postgresql
```

A run that invokes `SK-TECH-postgresql` without a preceding
`capability-adapter` ledger entry, when the fix is reported as *executed*
against a real database (not just proposed), is a scored defect — it
means `execution_mode` was decided by the skill itself rather than by the
adapter, violating the invocation contract's own field (`execution_mode`
is "decided by `capability-adapter` before the step, never by the
skill" — `state-and-contract.md` Part 2).

## Expected behavioral assertions

| # | Assertion | Dimension | Weight |
|---|---|---|---|
| 1 | `routing_record.selected[]` contains exactly `SK-TECH-postgresql` as the required skill (plus, optionally, `capability-adapter` as the PR-3 barrier) — none of the 16 named Must-NOT-activate IDs appear in it. | 1 (Correct skill activation) | critical |
| 2 | `SK-TECH-react`, specifically, is absent from `selected[]` despite being detectable in `frontend/package.json` — the router's stated reason for excluding it (if `excluded[]` records one) cites "no frontend file touched by this fix," not "React not present," since React *is* present. | 1 | critical |
| 3 | `capability-adapter` appears in the ledger as a barrier immediately before `SK-TECH-postgresql`'s invocation entry whenever `execution_mode` is `execute` (the fix is actually run against a database, not merely proposed) — matching `SK-TECH-postgresql`'s declared `execution_tier: B`. | 2 (Correct dependency resolution) | major |
| 4 | No stage in `plan.stages` other than the capability-adapter barrier and `SK-TECH-postgresql` itself; no `A ∥ B` edge recorded. | 3 (Correct sequencing) | minor |
| 5 | The returned fix (`outputs.index-or-query-change` and/or a `changes[]` entry touching `ordersRepository.js`) actually deduplicates: one row per distinct `orders.id`, produced via aggregation (`GROUP BY o.id, o.order_date, o.status, c.name`) or an equivalent window function (e.g. `COUNT(*) OVER (PARTITION BY o.id)` with row de-duplication) — not `SELECT DISTINCT o.id, o.order_date, o.status, c.name` alone, which would silently drop the required item count. | 6 (Correct implementation decisions) | critical |
| 6 | The fix's output includes an item-count-per-order field (e.g. `COUNT(oi.id) AS item_count`), satisfying the task's explicit requirement ("the response still needs an item count per order"). A fix that returns one row per order but omits the count is a scored failure of this assertion even though it satisfies assertion 5. | 6 | critical |
| 7 | The fix preserves the original query's filter (`WHERE c.id = $1`) and ordering (`ORDER BY o.order_date DESC`) — the dedup change is scoped to the `SELECT`/`GROUP BY` clause, not a rewrite that silently drops or reorders behavior the task didn't ask to change. | 6 | major |
| 8 | If `capability-adapter` reports shell/DB-execute capability unavailable, `execution_mode` is `advisory` or `fallback`, and the return envelope carries an `unverified_claims[]` entry stating the corrected query was not actually run against a database — matching `SK-TECH-postgresql`'s own `failure_handling`: "If shell is unavailable or denied, degrade to advisory... and state that the migration/EXPLAIN was not actually run." A run that reports `status: complete` in this situation without that entry violates IC-6 (status honesty). | 9 (Correct failure handling) | major |
| 9 | No escalation/approval gate fires for this change. `SK-TECH-postgresql`'s own `escalation` field scopes confirmation-gating to destructive migrations (`DROP`, data-losing `ALTER`) and untrusted `pg_restore`; this is a non-destructive `SELECT` rewrite, so a run that pauses for approval here is an over-gating defect, symmetric to the over-activation failure mode this scenario centers on. | 10 (Correct escalation) | minor |
| 10 | No version-gated PostgreSQL-18-only claim (OAuth2 auth, async I/O, protocol 3.2) is invoked to justify or frame this fix — `GROUP BY`/aggregate functions and window functions are available across the skill's full `covered_versions` range (`>=14 <=18`), so no version caveat is needed, and none should be fabricated. | 12 (Technology-specific accuracy) | minor |
| 11 | The fix stays scoped to the one query/repository file (`ordersRepository.js`); no new ORM dependency, caching layer, or schema migration is introduced to solve a five-line query bug (QR-1: no unnecessary abstraction for the size of the problem). | 13 (Maintainability) | minor |
