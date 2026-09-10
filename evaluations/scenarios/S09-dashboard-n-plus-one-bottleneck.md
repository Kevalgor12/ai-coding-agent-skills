# Scenario: S09 — Dashboard N+1 bottleneck, already measured

**Category:** Performance-sensitive tasks

**Complexity:** small (single domain, single confirmed cause — the diagnostic
work is already done; what remains is scoping and applying one fix, not a
multi-stage diagnostic loop)

**Risk level:** reversible-write (a query-path code edit; no destructive or
outward-facing action)

## Task

"Our internal analytics dashboard takes about 8 seconds to load. I profiled
it with clinic.js — the flamegraph shows 6.1 of the 8 seconds are spent
inside `GET /api/dashboard/customer-orders`, all of it in `pg.query` calls
made from a `for` loop that issues one query per customer to fetch that
customer's order history. Please fix the performance problem."

This is the complete, verbatim request. Unlike S03 ("app feels slow," no
cause established), the dominant cause is already named and already backed
by a cited profiling artifact — the open question this scenario tests is not
*whether* to measure, but *what to do with a measurement that's already in
hand*.

## Repository signals

**Corroborating the stated measurement (what a router would find on
inspection, not just take on the user's word):**

- `perf/clinic-flamegraph-2026-09-08.md` — a checked-in profiling summary:
  6.1s of the 8.02s total request time is attributed to `pg.query`,
  called 240 times (once per customer row) from within
  `server/routes/dashboard.js`.
- `server/routes/dashboard.js` — `GET /api/dashboard/customer-orders`
  fetches all customers, then inside a `for` loop calls
  `await pool.query('SELECT * FROM orders WHERE customer_id = $1', [c.id])`
  once per customer — matches the profile exactly; a textbook N+1 pattern.
- `package.json` — `express`, `pg`, `react`, `vite` as direct dependencies.
  No ORM manifest entry. No `redis` dependency. No `cache-manager` or
  `node-cache` dependency.

**Present in the repo, real, but *not* implicated by the 6.1s/8.02s
profile — the distractor set this scenario is built to test resistance
to:**

- `src/components/CustomerAvatar.jsx` renders customer photos via `<img
  src=... />` with no `loading="lazy"` attribute — a plausible, real,
  generically-recommended image-loading optimization.
- `vite.config.js` has no `manualChunks`/code-splitting configuration — a
  plausible, real, generically-recommended bundling optimization.
- No cache layer exists anywhere in the stack (no Redis, no HTTP cache
  headers on any route) — caching is a plausible, real, generically-
  recommended lever for a slow endpoint.
- The flamegraph in `perf/clinic-flamegraph-2026-09-08.md` shows these
  three items combined account for well under 2% of the profiled request
  time — none of them is the measured bottleneck.

## Expected activation set

**Must activate:** `performance-engineering` (SK-QA-003), `database-operations`
(SK-DATA-003), `capability-adapter` (SK-ORCH-002)

**Must NOT activate (as the fix / in any `changes[]` entry):** `caching-strategy`
(SK-DATA-004), `SK-TECH-redis`, `SK-TECH-vite`, `SK-FE-005` (rendering-strategy)

**Uncertain / acceptable either way:** `testing-strategy` (SK-QA-001) proposing
a regression test for the fixed endpoint

## Expected sequencing and parallelization

```
capability-adapter (barrier)
  → performance-engineering { confirm the cited profile actually shows
       pg.query as dominant (6.1/8.02s); check against known cross-stack
       patterns (N+1) per its own decision framework step 2 }
  → database-operations { own the actual fix — batch the per-customer
       query into a single JOIN/WHERE-IN, per its "indexing/N+1/pooling"
       ownership }
  → [optional] testing-strategy { regression test asserting one query,
       not N, is issued for the endpoint }
  → code-review ⤾ (performance facet)
```

No `[cond]` branch exists here the way S03 has one — the measurement already
resolved which branch applies. The failure mode this scenario targets is
the run re-opening that resolved question and treating the distractor set
as equally live candidates.

## Expected behavioral assertions

See `expected-behaviors/S09-dashboard-n-plus-one-bottleneck.md` for the
full graded list.
