# Expected Behaviors: S09 — Dashboard N+1 bottleneck, already measured

Paired with
[`scenarios/S09-dashboard-n-plus-one-bottleneck.md`](../scenarios/S09-dashboard-n-plus-one-bottleneck.md).
Not shown to the agent under test.

**Weight scale** (provisional, matching S03/`scoring.md`'s pending scale):
`critical` = the assertion this scenario exists to test; `major` = a
supporting correctness check; `minor` = a sanity/scope check that would be
surprising to fail but isn't the point.

**Relationship to S03:** S03 tests whether `performance-engineering`
activates at all and refuses to guess before measuring. This scenario
starts *after* that question is already settled — the measurement is a
given repository fact — and tests the next failure mode: once evidence
exists, does the run **use it to scope the fix**, or does it treat the
evidence as a ticket to also sweep in every other plausible-looking
performance idea sitting in the same file tree (lazy-loading images,
code-splitting, adding a cache)? A run that re-runs the S03-style
"gather evidence" loop here, ignoring the profile already provided, is
also a failure — it demonstrates the discipline was memorized as
"always ask for a profile" rather than "act on the profile once you have
one."

## Expected activation set

**Must activate:**

| Skill | Reason |
|---|---|
| `performance-engineering` (SK-QA-003) | Its verification bullet "The identified dominant cost is backed by evidence... not a guess" and decision-framework step 3 ("Is the identified cost actually dominant?") apply directly: the run must confirm the cited 6.1/8.02s profile before treating N+1 as confirmed, rather than skipping straight to a fix. Its own scope statement explicitly routes the *depth* of an N+1 fix to `database-operations`, so this skill's role here is confirmation + hand-off, not authoring the fix itself. |
| `database-operations` (SK-DATA-003) | Both `performance-engineering`'s scope ("Database-specific performance (indexing, N+1, connection pooling) is owned by database-operations") and the skill-catalog entry ("Query performance... indexing... in play") match once the profile names the query loop as dominant — this is the SK-DATA-003 activation condition being *satisfied by evidence*, the exact contrast case to S03 (where the same skill was correctly excluded for lack of evidence). |
| `capability-adapter` (SK-ORCH-002) | Barrier: `database-operations` is `execution_tier: B` (needs shell to run/verify the query change); the adapter resolves capability before that step executes, per SR-7/PR-3. |

**Must NOT activate (as a fix, i.e. must not appear in any `changes[]`
entry; may legitimately appear in `open_questions[]` or a `deferred_findings[]`
entry as an unmeasured, optional follow-up):**

| Skill | Reason |
|---|---|
| `caching-strategy` (SK-DATA-004) | Non-activation condition "no caching need" applies — the profile identifies a redundant-query-count problem, which a JOIN/batch fix eliminates at the source; wrapping the N+1 loop in a cache instead would paper over the measured cause rather than address it, contradicting `performance-engineering`'s decision-framework step 4 ("Is the right lever caching, tuning, or scaling? ... Don't reach for the familiar lever without checking it matches the actual cause.") and `caching-strategy`'s own Anti-pattern "Reaching for Redis reflexively for scale that doesn't actually need cross-process coordination." |
| `SK-TECH-redis` | No `redis` dependency exists in the repo and nothing in the profile implicates a caching need — matches this skill's own non-activation condition verbatim: "No Redis dependency exists and the question is an open store-shape or cache-layer choice." |
| `SK-TECH-vite` | The `vite.config.js` code-splitting gap is real but the flamegraph attributes well under 2% of request time to anything outside `pg.query`; activating a build-tool skill here is exactly "micro-optimizing a component that isn't the measured bottleneck," `performance-engineering`'s own named Anti-pattern. |
| `SK-FE-005` (rendering-strategy) | Non-activation condition "pure SPA with no SEO/SSR concern" applies, and nothing about image `loading="lazy"` implicates a rendering-mode decision; this is the same distractor class as `SK-TECH-vite`. |

**Uncertain / acceptable either way:**

- `testing-strategy` (SK-QA-001) proposing a regression test that asserts
  the endpoint now issues a bounded/constant number of queries rather than
  one per customer — reasonable either as part of this run or flagged as a
  follow-up; not the behavior under test.

## Expected sequencing and parallelization

```
capability-adapter (barrier)
  → performance-engineering { verify profile: 6.1/8.02s in pg.query,
       240 calls, one per customer — confirms N+1 per known cross-stack
       pattern, decision-framework step 2 }
  → database-operations { replace the per-customer loop with a single
       batched query (JOIN or WHERE customer_id = ANY($1)) }
  → [optional] testing-strategy ⟳ (query-count regression test)
  → code-review ⤾ (performance facet)
```

No `[cond]` branching over "which cause" exists — that question was
resolved by the given measurement, not by this run. A run that
re-introduces a `[cond]` branch across image-loading / code-splitting /
caching options, as if the cause were still open, has failed the scenario
regardless of which option it ultimately picks.

## Expected behavioral assertions

| Dim # | Dimension | Assertion | Weight |
|---|---|---|---|
| 14 | Performance reasoning | `changes[]` contains exactly one functional edit class: a rewrite of the per-customer query loop in `server/routes/dashboard.js` into a single batched query. No `changes[]` entry touches `src/components/CustomerAvatar.jsx`, `vite.config.js`, or introduces a cache/Redis dependency. This is the scenario's core test — evidence-scoped fix vs. grab-bag fix. | critical |
| 14 | Performance reasoning | `verification[]` includes "the identified dominant cost is backed by evidence" scored `pass`, with the evidence citing the specific figures in `perf/clinic-flamegraph-2026-09-08.md` (6.1s / 8.02s / 240 calls) — not a restated guess and not a re-request for profiling data that already exists in the repo. | critical |
| 1 | Correct skill activation | `routing_record.selected[]` includes `database-operations` with a reason citing the profile's `pg.query` attribution (not the raw request text) — the positive-case mirror of S03's assertion that the same skill must NOT activate without evidence. `caching-strategy` and `SK-TECH-redis` are absent from `routing_record.selected[]`, or if present, are recorded in `excluded[]` with the non-activation reason above (SR-11). | critical |
| 6 | Correct implementation decisions | If the run's `findings[]` or `open_questions[]` mentions the image-loading or code-splitting gaps at all, they are recorded as `deferred_findings[]` (out-of-scope, unmeasured) rather than folded into the required fix — per CM-2/IC-4, a step returns only the outputs it was asked for. | major |
| 13 | Maintainability | The batched-query fix does not introduce a new abstraction (e.g. a generic query-batching utility, an ORM, a cache wrapper) beyond what's needed to eliminate the loop — QR-1, no unnecessary abstraction for a single fixed endpoint. | minor |
