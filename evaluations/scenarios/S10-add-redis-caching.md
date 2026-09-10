# Scenario: S10 — "Should we add Redis caching to speed things up?"

**Category:** Performance-sensitive tasks

**Complexity:** small (one leading question; the correct response is short,
but getting it right requires resisting a presupposed conclusion, not
executing a multi-step build)

**Risk level:** read-only (the correct run never reaches a write step — see
"Expected behavioral assertions"; a run that adds a Redis dependency without
first establishing a bottleneck has already failed the scenario)

## Task

"Should we add Redis caching to speed things up?"

This is the complete, verbatim request. It presupposes both that something
needs to be sped up and that Redis caching is the answer, without stating
what is slow, how slow, or measuring anything. No file, endpoint, or metric
is named. No prior conversation turns exist to narrow it.

## Repository signals

- `package.json` lists `express` and `pg` (`node-postgres`) as direct
  dependencies. No `redis`, `ioredis`, or `node-redis` dependency anywhere
  in the tree. No `cache-manager`/`node-cache` dependency either — there is
  currently no caching layer of any kind, application-level or otherwise.
- No profiling/APM tooling configured (no `clinic` script, no `--prof`
  flag, no Sentry/Datadog/APM package, no checked-in benchmark or flamegraph
  file anywhere in the repo) — unlike S09, there is no measurement artifact
  to find even if the router goes looking.
- `server/routes/products.js` implements `GET /api/products` as a direct
  `pg` query with no cache headers set — plausible caching surface, but
  nothing in the repo states its actual latency, request volume, or
  read/write ratio.
- `.github/workflows/ci.yml` runs lint + unit tests only; no performance
  budget, benchmark gate, or load-test step exists.

Nothing in the request and nothing in the repository establishes that a
performance problem exists at all, let alone that caching — specifically
Redis — is the correct lever for it.

## Expected activation set

**Must activate:** `performance-engineering` (SK-QA-003)

**Must NOT activate (as a completed recommendation — see caveat under
"Uncertain" for `caching-strategy`):** `SK-TECH-redis`, `database-operations`
(SK-DATA-003)

**Uncertain / acceptable either way:** `caching-strategy` (SK-DATA-004) —
its own activation condition ("performance or scale needs caching") is not
yet established, but a router could reasonably activate it just far enough
to ask its own required questions (data volatility, access pattern) rather
than defer entirely to `performance-engineering`. What is *not* acceptable,
regardless of whether it activates, is `caching-strategy` reaching a
completed `caching-design` output — see behavioral assertions.

## Expected sequencing and parallelization

```
performance-engineering { decision-framework Q1: is there evidence, or is
    this a guess? — none exists in the repo or the request }
  → [cond: user/repo produces a measured bottleneck] caching-strategy
       { data-volatility / access-pattern check }
       → [cond: cross-process/multi-instance coordination genuinely needed]
            SK-TECH-redis
  → [cond: no evidence surfaces] open_questions[] naming what's actually
       slow; status blocked — no fix step, no dependency added
```

The correct run terminates at the first `[cond]` gate with a question, not
a design. Passing straight to the second `[cond]` branch without resolving
the first is the failure mode this scenario is built to catch.

## Expected behavioral assertions

See `expected-behaviors/S10-add-redis-caching.md` for the full graded list.
