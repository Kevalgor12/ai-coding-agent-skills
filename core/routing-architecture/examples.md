# Routing Examples

Worked routings. Each shows the twelve determinations, the **selected** set
(ordered/parallel-annotated), the **excluded** set with reasons (the "unnecessary
skills" determination — shown explicitly, per SR-11), context, review, and
escalation. Notation: `→` sequential · `∥` parallel · `⤾` review loop · `⛔` approval gate.

Skill IDs per the [taxonomy](../taxonomy/skill-catalog.md).

---

## Example 1 — "Fix this PostgreSQL query." (the tight case)

| Determination | Value |
|---|---|
| Intent | fix / optimize |
| Task type | performance-optimization (scoped) |
| Complexity | small (single query) |
| Technologies | PostgreSQL (from `postgres://` / `pg` / the word "PostgreSQL") |
| Risk | read-only → reversible-write (a query/index change) |

**Selected (minimum set):**

```
capability-adapter (barrier: is shell available to run EXPLAIN?)
  → performance-engineering        (query is a perf concern → SR-5)
  ∥ postgresql (SK-TECH-postgresql) (detected → SR-3; specializes database-operations)
  → [code-review: performance facet only] ⤾
```

Router self-suppresses `workflow-composer` (few stages) and skips discovery
(SR-8: bounded fix). `git-conventions` attaches only if a commit is actually made.

**Excluded (unnecessary) — with reasons:**

| Excluded | Reason |
|---|---|
| frontend-architecture, ui-ux-design, styling-systems, web-accessibility, rendering-strategy, react/vue/angular/nextjs/nuxt, three.js, tailwind/sass/mui/shadcn, html/css | no frontend/UI signal (SR-1); many list "non-frontend work" in non-activation (SR-2) |
| seo-optimization, web-monetization | no public-web/monetization signal |
| realtime-communication, socketio, webrtc, websocket-api | no realtime signal |
| technical-documentation | pure code task, its non-activation routes it out (SR-2) |
| requirements/architecture/planning | bounded fix, not a project (SR-8) |
| orm-integration, drizzle/prisma/typeorm/mongoose | no ORM in the query task (raw SQL); undetected (SR-3) |
| mysql, mongodb, clickhouse, redis, opensearch | not the engine in use (SR-3/SR-4) |
| security-engineering | no trust boundary/secret/untrusted input in a read query (SR-5) — *would* activate if the query concatenated untrusted input |

**Context:** the query text + (optional) `EXPLAIN` output + PG major version.
Nothing else. **Review:** performance facet only. **Escalation:** none unless a
destructive change (e.g. dropping an index) → `⛔`.

> This is the case the brief calls out: the unrelated frontend/SEO/UI/Three.js/
> WebRTC/documentation skills are all explicitly excluded, each with a reason.

---

## Example 2 — "Build a realtime multiplayer browser game." (the broad case)

| Determination | Value |
|---|---|
| Intent | build |
| Task type | greenfield development |
| Complexity | project (multi-domain) |
| Technologies | browser game → Three.js (rendering) [if named/chosen]; a realtime transport (WebSocket/Socket.IO); a backend; a datastore |
| Risk | reversible-write → production (eventual deploy) |

**Selected:**

```
requirements-engineering
  → solution-architecture              ⛔ (major stack commitment — confirm)
  → technical-planning
  → capability-adapter (barrier for the Tier-B/C build/test steps)
  → [parallel scaffolding]
        frontend-architecture → three.js → rendering-strategy
        ∥ backend-architecture → realtime-communication → (socketio | websocket-api)
        ∥ data-modeling → (chosen datastore tech)
  → authentication-authorization      (multiplayer identity → trust boundary, SR-5)
  → performance-engineering           (realtime latency budget, SR-5)
  → security-engineering              (multiplayer = untrusted clients, SR-5)
  → testing-strategy → (jest-vitest ∥ playwright)     (runnable code, SR-5)
  → code-review ⤾  (security ∥ performance ∥ quality ∥ comment facets, parallel)
  → git-conventions + git-workflow → PR ⛔
  → ci-cd-pipeline → containerization → deployment-release ⛔ (first prod deploy)
```

Conventions (`code-commenting`, `code-quality`) attach throughout.

**Excluded (unnecessary) — with reasons:**

| Excluded | Reason |
|---|---|
| seo-optimization, google-seo | a realtime game canvas is not SEO-driven content (no signal); would activate only if a marketing site were in scope |
| web-monetization, google-adsense | no monetization in the request |
| graphql-api-design, openapi-swagger | realtime transport chosen over request/response API; not indicated (SR-1) |
| orm-integration + prisma/drizzle/typeorm/mongoose | only activate once a datastore *needing* an ORM is chosen in architecture; deferred, not assumed |
| search-integration, opensearch, clickhouse | no search/analytics requirement |
| mui, shadcn-ui, tailwind (unless UI chrome is specced) | game canvas ≠ component-library UI; activate only if HUD/menus need them |
| legacy-modernization, refactoring, data-migration | greenfield — nothing to modernize/migrate |
| llm-application-engineering | no LLM feature |

**Context:** requirements + architecture decisions drive later context; each tech
skill loads its body only when its stage runs (CS-2). **Review:** all four facets.
**Escalation:** architecture commitment, PR post, and prod deploy are `⛔` gates,
surfaced up front (ER-1).

> Matches the brief's "may activate" list (requirements, architecture, frontend,
> Three.js, realtime, WebSocket/Socket.IO, backend, database, testing, security,
> performance) while *excluding* the skills the task doesn't imply.

---

## Example 3 — "Add a comment explaining what this function does." (trivial)

| Determinations | build/edit · simple · trivial · TypeScript (say) · read-only |

**Selected:** `code-commenting` only. Router self-suppresses everything else
(SR-7): no composer, no adapter (Tier A), no discovery, no review loop for a
one-line comment. **Excluded:** effectively all 68 other skills — default-deny on
a trivial single-owner task. **Escalation:** none.

> Demonstrates the low end: the same router that staffed 15 skills for the game
> staffs exactly one here.

---

## Example 4 — "Migrate our Prisma schema to add tenant_id with row-level security."

| Determinations | migrate · migration workflow · multi-step · Prisma + PostgreSQL (detected) · **destructive** (schema change on populated DB) |

**Selected:**

```
technical-planning (expand/contract)
  → data-migration → prisma (SK-TECH-prisma) ∥ postgresql (RLS specifics)
  → authentication-authorization (RLS is an authz mechanism → SR-5)
  → security-engineering (tenant isolation = trust boundary → SR-5)
  → testing-strategy (migration up/down tests)
  → capability-adapter (barrier: shell to run the migration)
  → code-review ⤾ (security facet mandatory)
  → apply migration ⛔ (destructive / data-affecting — human approval, ER-2)
```

**Excluded:** all frontend, realtime, SEO, search, container/CI (unless deploy is
asked), `drizzle`/`typeorm` (SR-4: Prisma is the detected ORM), `mysql`/`mongodb`
(SR-3). **Escalation:** the destructive apply is a hard `⛔`; the router surfaces
it up front (ER-1).

> Shows conflict resolution (Prisma wins its cluster) + a destructive-action gate.

---

## Example 5 — "Why is our Next.js page slow to load?" (debugging + perf)

| Determinations | debug→optimize · debugging then performance-optimization · multi-step · Next.js + React (detected) · read-only (diagnosis first) |

**Selected:**

```
⟳ debugging loop { hypothesize → measure (rendering-strategy, bundle, data-fetch) → narrow }
  → performance-engineering (dominant cost)
  ∥ nextjs (SK-TECH-nextjs) → rendering-strategy (SSR/ISR/streaming, hydration cost)
  → [fix] → testing-strategy (guard the regression)
  → code-review ⤾ (performance facet)
```

**Excluded:** backend/data skills unless the measurement points there (added
*then*, not up front — SR-1); SEO (not asked), Three.js/realtime (no signal),
security (no trust-boundary change). **Escalation:** none until a prod deploy.

> Iteration is the defining semantic; the router doesn't pre-commit to a cause —
> it activates the diagnostic loop and lets evidence pull in further skills.

---

## Example 6 — "Review this PR." (review-only, no build)

| Determinations | review · review workflow · varies · techs from the diff · read-only (+ outward-facing if posting) |

**Selected:** `code-review` (aggregator) delegating, **in parallel**,
`security-engineering` ∥ `performance-engineering` ∥ `code-quality` ∥
`code-commenting` facets, plus `git-conventions` (checks commit/branch text). Tech
skills load only for technologies present in the diff (SR-3). **Excluded:** all
build/discovery skills — reviewing is not authoring (each build skill's
non-activation covers this, SR-2). **Escalation:** posting findings to the PR is
outward-facing → `⛔` (ER-2).

---

## Example 7 — "Set up CI to run our tests on every push." (infra-only)

| Determinations | build/config · (part of) greenfield/feature infra · small · GitHub Actions + the repo's test runner (detected) · reversible-write |

**Selected:** `ci-cd-pipeline` → `github-actions` (SK-TECH), composing
`testing-strategy` (what to gate on) and referencing `jest-vitest`/`playwright`
if detected. `git-workflow` if it touches branch protection. **Excluded:** all
frontend/UI, data, realtime, SEO, security-*unless* secrets/OIDC are configured
(then `security-engineering` for least-privilege, SR-5). **Escalation:** none for
authoring config; the capability map notes no agent drives Actions natively, so
execution is external (advisory).

---

## Example 8 — "Make it better." (ambiguous — escalate before building)

| Determinations | intent **ambiguous** · unknown · unknown · unknown · unknown |

**Selected:** `skill-router` → **escalate to `requirements-engineering` / the
user** (ER-4). No build skills are selected until intent is clarified. **Excluded:**
everything else, pending clarification. **Escalation:** the ambiguity itself — the
router asks what "better" means rather than guessing a direction and activating a
speculative skill set.

> The correctness guard: on genuine ambiguity the router refuses to over-activate
> on a guess; it resolves intent first.

---

## What the examples demonstrate collectively

- The **same mechanism** yields 1 skill (Ex. 3), a tight 3–4 (Ex. 1), and a broad
  15+ (Ex. 2) — driven by default-deny + detection + completeness backstop.
- **Exclusions are always explicit and reasoned** (SR-11), which is what makes the
  minimum-set claim auditable rather than aspirational.
- **Risk drives gates** (Ex. 2, 4, 6) and **ambiguity drives escalation** (Ex. 8),
  independent of which domain skills are selected.
- **Evidence can expand the set mid-run** (Ex. 5) — routing is not frozen at
  intake; the debugging/perf loops pull in skills as the cause localizes.
