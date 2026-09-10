# Scenario: S01 — PostgreSQL duplicate-rows query bug

**Category:** Simple tasks
**Complexity:** small
**Risk level:** reversible-write

## Task

> Fix this PostgreSQL query — the `/api/customers/:id/orders` endpoint is
> returning the same order multiple times.
>
> ```sql
> SELECT o.id, o.order_date, o.status, c.name AS customer_name
> FROM orders o
> JOIN customers c ON c.id = o.customer_id
> JOIN order_items oi ON oi.order_id = o.id
> WHERE c.id = $1
> ORDER BY o.order_date DESC;
> ```
>
> Each order shows up once per item in it — a 3-item order shows up 3 times
> in the response. It should return one row per order, and the response
> still needs an item count per order.

This is a direct instance of the routing architecture's own mandated
example (`core/routing-architecture/README.md`: *"Fix this PostgreSQL
query" must not pull in frontend, SEO, UI/UX, Three.js, WebRTC, or
documentation skills*), grounded in a concrete, realistic bug: an
unaggregated one-to-many `JOIN` (`orders` → `order_items`) fanning out the
base row.

## Repository signals

- `backend/package.json` — Node.js + Express + `pg` (raw SQL client, no
  ORM: no `prisma`/`drizzle`/`typeorm`/`mongoose` dependency present).
- `backend/src/repositories/ordersRepository.js` — contains the buggy query
  shown above, called from `backend/src/routes/orders.js`.
- `frontend/package.json` — a separate, unrelated React 18 SPA
  (`react`, `react-dom`, `react-router-dom`, `react-scripts`/CRA), with
  `frontend/src/pages/OrdersPage.jsx` consuming this endpoint. Nothing
  under `frontend/` is touched by this task.
- `.git/` present with a small existing commit history.
- No test files for `ordersRepository.js` or `routes/orders.js` (no
  existing coverage for this endpoint).
- No CI config, no Docker/deployment config, no SEO/meta-tag setup, no
  Three.js/WebGL code, no WebSocket/WebRTC/realtime code anywhere in the
  repo.
- A `README.md` exists at the repo root but is not referenced by the task.

## Expected activation set

**Must activate:**
- `SK-TECH-postgresql` — activation condition: "This technology is
  detected in the repo (manifest/config/imports/file types) **or** named
  in the task." Both hold: PostgreSQL is named explicitly, and the `pg`
  driver plus the raw-SQL repository file are detected.

**Must NOT activate** (deliberately generous list a naive keyword- or
file-presence-based router might pull in from this repo's other stacks):
- `SK-FE-001` (frontend-architecture) — non-activation: "backend work."
- `SK-TECH-react` — React *is* detected in `frontend/package.json`, so a
  detection-only router (SR-3 alone) would wrongly include it; SR-1's
  second conjunct ("*and* the task type needs it") fails, since no
  frontend file is touched by this fix.
- `SK-FE-002` (ui-ux-design) — non-activation: "Non-visual/backend tasks."
- `SK-FE-004` (web-accessibility) — non-activation: "Backend/non-UI work."
- `SK-GROW-001` (seo-optimization) — no indexability/search-visibility
  concern in play; one of the routing README's own named exclusions for
  this exact canonical example.
- `SK-TECH-threejs` — absent from the repo and unnamed in the request;
  SR-3's detection gate fails outright.
- `SK-TECH-webrtc` / `SK-BE-004` (realtime-communication) — no realtime
  transport present or requested; SR-3/activation-condition fails.
- `SK-CONV-006` (technical-documentation) — this is the exact skill
  `rules.md` names as the worked example of SR-2 ("the rule that keeps
  `technical-documentation` out of 'fix this query'").
- `SK-CONV-001` (git-conventions) — no commit or branch is being requested;
  activation conditions unmet.
- `SK-CONV-004` (refactoring) — refactoring's scope requires a
  *behavior-preserving* transformation; this fix deliberately changes
  output behavior (removes duplicate rows), so it is definitionally not a
  refactor.
- `SK-CONV-007` (code-review) — no review, diff, or pre-merge gate was
  requested.
- `SK-QA-003` (performance-engineering) — non-activation: "No performance
  concern." The bug is row-duplication from an unaggregated `JOIN`, not a
  stated slowness/budget problem.
- `SK-DATA-001` (data-modeling) — non-activation: "Query optimization only
  (route to `SK-DATA-003`)"; no schema/data-model redesign is requested.
- `SK-DATA-002` (orm-integration) — SR-3: no ORM is present in the repo
  (raw `pg` queries) or named in the task.
- `SK-BE-001` (backend-architecture) — activation condition
  ("Building/structuring a backend service") is not met by a single query
  fix; non-activation covers "pure DB modeling," and this is narrower
  still — pure DB *querying*.

**Uncertain / acceptable either way:**
- `SK-DATA-003` (database-operations) — its activation conditions name
  "query performance, transactions, indexing, or pooling." A duplicate-row
  bug from an unaggregated `JOIN` is a correctness issue, not squarely one
  of those four. A router that includes it (reading "operate a database
  well" broadly) and one that omits it (reading the stated activation text
  narrowly) are both defensible — do not score either choice as an error.
- `SK-CONV-002` (code-commenting) / `SK-CONV-003` (code-quality) — the fix
  does edit source code (SR-6: these "engage when code is written/edited"),
  so a router that pulls one or both in to comment on the non-obvious
  JOIN-fanout reasoning, or to keep the rewritten query idiomatic, is
  defensible; so is a router that treats a five-line query fix as too small
  to warrant either.
- `SK-QA-001` (testing-strategy) — "a change needs coverage" could apply,
  since there's no existing test for this endpoint. A router that adds a
  regression test is defensible; so is one that treats this narrowly-worded
  bug-fix request as out of scope for new test authorship.

## Expected sequencing and parallelization

Single required skill. Per SR-7 (orchestration minimalism), the router
self-suppresses: no `workflow-composer` (single-stage task), no discovery
skills (SR-8: this is a bounded single-file change, not multi-domain or
high-risk). `SK-TECH-postgresql` inherits its execution tier from its
Layer-3 parents (`database-operations` is Tier B), so per PR-3
`capability-adapter` runs as a barrier immediately before it, resolving
shell/DB-execute capability so the corrected query can actually be run
(not just reasoned about):

```
capability-adapter → SK-TECH-postgresql
```

No `A ∥ B` parallel opportunity exists — one skill, one file, one target.
