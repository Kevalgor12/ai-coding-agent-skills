# Scenario: S03 — App feels slow

**Category:** Ambiguous tasks
**Complexity:** multi-step (a diagnostic loop necessarily precedes any fix; the task
spans frontend and backend/data domains)
**Risk level:** read-only, for the diagnosis phase this scenario is testing
(escalates to reversible-write only once a specific fix is chosen and applied)

## Task

"Users are complaining the app feels slow."

This is the complete, verbatim request. No file, endpoint, page, or query is
named. No prior conversation turns exist to narrow it.

## Repository signals

**What a bounded Phase-0 scan (manifests/config only — see
[routing-algorithm.md](../../core/routing-architecture/routing-algorithm.md)
Phase 0, and CS-6's "bounded signal scan... for detection, not comprehension")
would actually surface:**

- `package.json` lists `react` and `express` as direct dependencies, plus `pg`
  (`node-postgres`) — no ORM manifest entry (`prisma`/`drizzle`/`typeorm`/
  `mongoose` all absent).
- No `redis` dependency, no CDN/edge-cache config, no `next.config.*` or
  `nuxt.config.*` — this is a plain React SPA (Vite/CRA-style) calling an
  Express API, not a meta-framework app.
- No profiling/APM tooling configured (no `clinic` script, no `--prof` flag,
  no Sentry/Datadog/APM package) — there is no existing performance telemetry
  to read.
- `.github/workflows/ci.yml` runs lint + unit tests; no performance budget or
  benchmark gate.

**What exists in the source tree but is *not* visible from that bounded
scan — only from actually reading the code (deliberately placed here to test
whether the run tries to read its way to a guess instead of measuring):**

- `src/components/Dashboard.jsx` renders a few-hundred-row table via `.map()`
  with a non-trivial per-row computation inline, no `useMemo`/`useCallback`,
  and the array is re-created on every parent re-render — a plausible
  rendering-cost issue.
- `server/routes/orders.js` handles `GET /api/orders` by fetching all orders
  and then, inside a `for` loop, issuing one additional `pg` query per order
  to fetch that order's line items — a textbook N+1 pattern — a plausible
  database-cost issue.

Both are real. Nothing in the request, and nothing in the bounded scan,
establishes which one (or both, or neither — it could just as easily be
network latency, a CDN miss, or something not yet in the repo at all) is
what users are actually feeling.
