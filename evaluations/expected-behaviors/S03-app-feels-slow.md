# Expected Behaviors: S03 — App feels slow

Paired with [`scenarios/S03-app-feels-slow.md`](../scenarios/S03-app-feels-slow.md).
Not shown to the agent under test.

**Weight scale** (provisional — `scoring.md` does not yet exist; see
evaluation-spec.md's "Honest scope"): `critical` = the assertion this
scenario exists to test; `major` = a supporting correctness check; `minor` =
a sanity/scope check that would be surprising to fail but isn't the point.

## Expected activation set

**Must activate:**

| Skill | Reason |
|---|---|
| `performance-engineering` (SK-QA-003) | Its activation condition "A performance problem or budget is in play" matches the request directly. Its `scope` field states it *is* the cross-cutting diagnose-before-optimize skill, and its `failure_handling` says explicitly: "If no profiling/benchmark evidence is available, gather it before proposing a change rather than guessing at the bottleneck." |
| `capability-adapter` (SK-ORCH-002) | Barrier, per SR-7/PR-3: `performance-engineering` is `execution_tier: B` (needs shell/profiling capability to gather evidence), so the adapter engages before that step runs. |

**Must NOT activate in the initial routing plan** (i.e., before
`performance-engineering` has produced evidence — they may legitimately
activate *afterward*, see "Uncertain" below):

| Skill | Reason |
|---|---|
| `SK-TECH-react` | Would be a speculative frontend-specific fix. Nothing yet establishes the `Dashboard.jsx` render path as the dominant cost — activating it now is exactly Example 5's excluded case ("backend/data skills unless the measurement points there (added *then*, not up front — SR-1)"), applied symmetrically to the frontend tech skill. |
| `database-operations` (SK-DATA-003) | Same reasoning. Its own activation condition ("query performance... in play") is *suspected*, not yet *established* — the router's Phase-0 bounded scan (CS-6) does not read `server/routes/orders.js` closely enough to establish this; only `performance-engineering`'s own diagnostic work can. |
| `caching-strategy` (SK-DATA-004) | Its non-activation condition ("no caching need") applies until a lever is chosen. Activating it now — jumping straight to "add a cache" without having measured whether caching is even the right lever vs. an index fix vs. a render fix vs. nothing — is precisely the "guessing a fix... speculatively" failure mode this scenario is built to catch. |
| `rendering-strategy` (SK-FE-005) | Non-activation condition covers "pure SPA with no SEO/SSR concern"; this is a Vite/CRA SPA, and no rendering-mode decision is implicated by a slowness complaint in isolation. |
| `requirements-engineering` (SK-DISC-001) | This is not S04-style object-ambiguity. The *object* of the complaint ("the app," "slow") is clear; what's unresolved is the *cause*, and resolving a performance cause is `performance-engineering`'s own job via measurement — not a scoping question to route to the user. |

**Uncertain / acceptable either way:**

- `database-operations` and/or `SK-TECH-react` activating as a *later* step,
  once `performance-engineering`'s `performance-findings` output names one of
  them (or both, sequentially) as the dominant cost, is correct and expected.
  The behavioral test is only about *whether either activates before
  evidence exists* — not about which one evidence eventually points to.

## Expected sequencing and parallelization

```
capability-adapter (barrier)
  → ⟳ performance-engineering { hypothesize → measure (profile the Dashboard
       render path AND the /api/orders query path) → narrow }
       → [cond: dominant cost = backend/N+1] database-operations
       ∥ [cond: dominant cost = frontend render] SK-TECH-react
  → [fix, scoped only to the confirmed dominant cost]
  → testing-strategy (guard the regression — only once runnable code is produced)
  → code-review ⤾ (performance facet)
```

The `⟳` iteration is the element under test: the loop repeats until the
dominant-cost criterion is met (`performance-engineering`'s own
`owned_knowledge`: "measure-before-optimizing / dominant-cost-first
diagnostic discipline"). The two `[cond]` branches are resolved only by loop
output — never by the router at intake, and never by keyword-matching
"slow" + "React" or "slow" + "database" from the manifest alone.

## Expected behavioral assertions

| Dim # | Dimension | Assertion | Weight |
|---|---|---|---|
| 1 | Correct skill activation | `performance-engineering` appears in `routing_record.selected[]` with a reason matching its stated activation condition. `SK-TECH-react`, `database-operations`, and `caching-strategy` are absent from the *initial* `routing_record.selected[]`; if any later appears, the `routing_record` shows it added in a subsequent revision whose stated reason cites a specific `performance-findings` artifact, not the original request text. | critical |
| 14 | Performance reasoning | The return envelope's `verification[]` includes "the identified dominant cost is backed by evidence... not a guess" scored `pass`, with the evidence cited (a profile capture or a measured query-timing figure) — not `not-run`. No `changes[]` entry modifies a component that wasn't the measured bottleneck, matching `performance-engineering`'s own verification bullet: "No micro-optimization is proposed for a component that isn't the measured bottleneck." | critical |
| 6 | Correct implementation decisions | `changes[]` is empty (no file edited) until `artifacts{}` contains a `performance-findings` output with cited evidence — i.e., the run does not edit `Dashboard.jsx` or `orders.js` "to be safe" before diagnosis completes. | major |
| 9 | Correct failure handling | If `capability-adapter` reports no shell/profiling capability available, the run's `status` is `blocked` (not `complete`, and not a guessed `failed`), with an `unverified_claims[]` or `open_questions[]` entry naming the missing evidence — matching `performance-engineering`'s stated `failure_handling` line. | major |
| 7 | Correct security behavior | `security-engineering` correctly does not activate — the N+1 loop is a cost issue, not a trust-boundary/untrusted-input issue, so its absence from `routing_record.selected[]` is expected, not a gap (recorded with a reason, per SR-11, rather than a silent omission). | minor |
