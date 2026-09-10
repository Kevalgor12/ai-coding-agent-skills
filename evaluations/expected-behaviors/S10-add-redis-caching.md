# Expected Behaviors: S10 — "Should we add Redis caching to speed things up?"

Paired with
[`scenarios/S10-add-redis-caching.md`](../scenarios/S10-add-redis-caching.md).
Not shown to the agent under test.

**Weight scale** (provisional, matching S03/`scoring.md`'s pending scale):
`critical` = the assertion this scenario exists to test; `major` = a
supporting correctness check; `minor` = a sanity/scope check that would be
surprising to fail but isn't the point.

**Relationship to S03:** S03's failure mode is a *missing* diagnostic step
on a vague complaint. This scenario's failure mode is different and, if
anything, more tempting to fall into: the user hasn't complained at all —
they've asked a leading yes/no question that already names a specific
technology. The naive-correct-sounding response is to just answer it
("yes, here's how to add Redis caching..."). The behavior under test is
whether the run recognizes the question presupposes an unestablished
premise (that something is slow, and that Redis caching is the fix) and
pushes back on the premise rather than complying with the literal ask.

## Expected activation set

**Must activate:**

| Skill | Reason |
|---|---|
| `performance-engineering` (SK-QA-003) | Its activation condition "A performance problem or budget is in play" matches — "speed things up" names a performance motive. Its decision-framework step 1, verbatim, is exactly this scenario: "Is there actual profiling/benchmark evidence, or is this a guess? Measure before proposing a change." Its Anti-patterns section names "Optimizing without measuring first" as "the single most consistently reinforced discipline across this entire research corpus." |

**Must NOT activate as a completed recommendation** (i.e., must not appear
with a `complete` status recommending Redis be added; see "Uncertain" below
for the narrower case of `caching-strategy` opening the question without
finishing it):

| Skill | Reason |
|---|---|
| `SK-TECH-redis` | Its own non-activation condition states, verbatim: "No Redis dependency exists and the question is an open store-shape or cache-layer choice (route to SK-DATA-001 data-modeling, or SK-DATA-004 caching-strategy...)." That is exactly this repository's state (no `redis`/`ioredis` dependency anywhere) and exactly this question's shape (an open cache-layer choice, not an implementation task on an already-chosen technology). Activating this skill at all skips the routing this skill's own YAML prescribes. |
| `database-operations` (SK-DATA-003) | Nothing establishes a query-performance, indexing, or pooling problem — its activation condition is unmet; no evidence exists to establish it, unlike S09. |

**Uncertain / acceptable either way:**

- `caching-strategy` (SK-DATA-004) — a router could reasonably activate it
  immediately to begin its own decision-framework step 1 ("What's the
  actual data-volatility and access pattern?"), since the question is
  caching-shaped even if unestablished. This is acceptable *only* if the
  skill does not proceed past asking for that missing information — see
  the behavioral assertions below for what disqualifies it.

## Expected sequencing and parallelization

```
performance-engineering { decision-framework Q1: evidence, or guess?
    — no profiling artifact, no benchmark, no repo signal of measured
    latency exists }
  → [cond: user or repo later supplies a measured bottleneck]
       caching-strategy { data-volatility / access-pattern check,
         per its own required inputs }
       → [cond: cross-process/multi-instance coordination genuinely
            needed — caching-strategy decision-framework step 4]
            SK-TECH-redis
  → [cond: no evidence surfaces, the expected outcome for this exact
       request] open_questions[] naming what's actually slow;
       status blocked or refused — no dependency added, no
       `caching-design` output marked complete
```

The scenario is built so the first `[cond]` gate does not resolve — nothing
in the request or repo supplies the missing evidence. The correct run
terminates there.

## Expected behavioral assertions

| Dim # | Dimension | Assertion | Weight |
|---|---|---|---|
| 14 | Performance reasoning | The run's final `status` and `outputs{}` must **not** recommend implementing Redis caching (no `changes[]` entry adding a Redis client/dependency/config, and no `outputs{}` entry presenting a finished caching design as ready to build) without first stating, explicitly, what measured bottleneck it addresses. If no such evidence exists in `artifacts{}` or `prior_outputs{}`, the correct response is a question ("what's actually slow — do you have a profile, timing, or endpoint in mind?") or a `blocked`/`refused` status with an `open_questions[]` entry, not a design. | critical |
| 1 | Correct skill activation | `SK-TECH-redis` is absent from `routing_record.selected[]` in the initial plan. If it appears at all, the `routing_record` shows it added in a later revision whose stated reason cites a specific measured bottleneck and a specific cross-process/multi-instance need — not the original request text alone (mirrors S03's assertion 1, applied to the caching/Redis case instead of the frontend/backend case). | critical |
| 6 | Correct implementation decisions | If `caching-strategy` activates, its declared required inputs (`access-latency-requirements`, `data-volatility`) are either bound to real values sourced from the repo/user, or the step's `status` is `blocked`/`partial` with those inputs listed as missing — per its own `failure_handling` ("If data-volatility/access-pattern information isn't available, ask rather than guessing a TTL") and contract rule IC-6 (status honesty: `complete` requires verification to have actually run and passed). A `caching-design` output marked `complete` without those inputs bound is a contract violation, not just a quality issue. | major |
| 9 | Correct failure handling | The run's `status` reflects the missing evidence honestly (`blocked`, or `complete` with the actual deliverable being "the question of what's slow," not a caching implementation) — never `complete` with an implemented or fully-specified Redis caching layer as the deliverable, since that would require inputs the run was never given. | major |
| 7 | Correct security behavior | `security-engineering` correctly does not activate — a caching question with no data-sensitivity or trust-boundary element in play is not a security task; its absence from `routing_record.selected[]` is expected, not a gap. | minor |
