---
name: Nuxt
description: >-
  Nuxt-specific implementation: Nitro server engine, file-based routing from
  app/pages/, auto-imports/module system, routeRules caching, Nuxt 3→4
  migration, and the GHSA-wm8w-6qjm-cv43 cross-user payload-disclosure
  advisory. Use when the repo has a nuxt.config.ts, depends on "nuxt", or
  the task names Nuxt/Nitro. Not for the Next.js-vs-Nuxt framework choice
  (frontend-architecture) or generic Vue questions (SK-TECH-vue).
spec_version: "1.0"
---

## Purpose & scope

Apply Nuxt correctly for the version in use — the Nitro server engine,
file-based routing, auto-imports, and per-route caching via `routeRules`.
The framework-selection decision (Next.js vs. Nuxt, or React/Vue/Angular)
and the general meta-framework comparison are owned by
[frontend-architecture](../frontend-architecture/SKILL.md) (`SK-FE-001`) —
not repeated here. Vue-the-base-framework specifics (SFCs, reactivity,
template escaping) belong to `SK-TECH-vue`. This skill supplies only what's
specific to Nuxt's own implementation once Nuxt is the framework in use.

## When to use / When not to use

**Use** when a `nuxt.config.ts`/`.js` file is present, `package.json`
depends on `"nuxt"`, the `nuxi` CLI is in play, or the task names Nuxt,
Nitro, or a Nuxt-specific API (`useFetch`, `useAsyncData`, `routeRules`,
`server/api`, `definePageMeta`). **Do not use** when no Nuxt manifest is
present and the task doesn't name Nuxt (route to `SK-TECH-vue` or
`SK-FE-001`), when the task is about Next.js or another React
meta-framework (route to `SK-TECH-nextjs`), or when the
framework/meta-framework choice is still open (route to `SK-FE-001`).

## Knowledge

**Nitro is Nuxt's dedicated server engine**, not an optional add-on: it
provides cross-platform runtime support (Node.js, browsers, service
workers, and more), serverless-readiness out of the box, automatic
code-splitting, a standalone `.output` distribution independent of
`node_modules`, and a global `$fetch` helper that short-circuits network
calls when running server-side. The docs describe the combination as making
Nuxt "a hybrid framework for the JAMstack." [Source:
https://nuxt.com/docs/4.x/guide/concepts/server-engine] Inside `server/`,
Nitro splits by directory and filename convention: `server/api/` routes are
auto-prefixed with `/api` (`hello.ts` → `/api/hello`); `server/routes/`
routes are not prefixed; `server/middleware/` handlers run before routes
(inspect/extend the request, don't return a response); `server/plugins/`
are Nitro lifecycle plugins; `server/utils/` holds shared server helpers.
All handlers use `defineEventHandler()`/`eventHandler()`, support dynamic
segments (`[name].ts`) and HTTP-method-suffixed filenames (`.get`, `.post`,
etc.), and can return plain objects that are auto-JSON-serialized. [Source:
https://nuxt.com/docs/4.x/guide/directory-structure/server]

**File-based routing lives under `app/pages/`** [VERSION-SENSITIVE: Nuxt
4.x directory layout]. Nuxt 4 introduced an `app/` directory as the
project's main source root — `srcDir` now defaults to `app/`, and the `~`
alias points to `app/` instead of the project root; components, layouts,
pages, composables, middleware, and plugins all live under it. In Nuxt 3
these directories sat at the project root instead. Old-structure projects
are still auto-detected, but migrating is recommended for build performance
and IDE type-safety. [Source:
https://nuxt.com/docs/4.x/guide/directory-structure; Source:
https://nuxt.com/docs/4.x/getting-started/upgrade]

**Auto-import and auto-registration are foundational, not cosmetic.**
Components (`app/components/`), composables (`app/composables/`), and
utilities (`app/utils/`) are available throughout the app with no explicit
`import`, alongside Vue's own reactivity APIs and Nuxt's built-in
composables; the mechanism preserves typings/IDE completion and only
includes what production code actually uses (tree-shaken). An `#imports`
alias is available where an explicit import is preferred. This is
configurable: `imports: { autoImport: false }` disables auto-imports
entirely; `imports: { scan: false }` disables scanning of custom project
code while keeping framework auto-imports, with the documented caveat that
doing so "breaks the layer system's override feature"; setting
`components.dirs: []` disables component auto-registration. Auto-imported
`ref`/`computed` values are still **not** auto-unwrapped in templates —
`.value` is still required there. Most built-in composables require a valid
Nuxt context (setup function, plugin, or middleware) and throw "Nuxt
instance is unavailable" if called outside one — e.g., after a stray
`await` inside an async callback that loses context. [Source:
https://nuxt.com/docs/4.x/guide/concepts/auto-imports] **Modules** are the
packaged extension of this same mechanism: functions that run sequentially
during `nuxt dev`/`nuxt build`, hooking into Nuxt's config and hook system
via `@nuxt/kit` to add plugins, components, composables, and server routes
as independently publishable npm packages, without patching Nuxt core.
[Source: https://nuxt.com/docs/4.x/guide/going-further/modules]

**`routeRules` (in `nuxt.config.ts`) is the per-route rendering/caching
control surface**, keyed by route glob, supporting: `redirect`, `ssr`
(bool), `cors` (bool), `headers` (object), `swr` (number|bool —
stale-while-revalidate), `isr` (number|bool — incremental static
regeneration, for platforms like Netlify/Vercel), `prerender` (bool),
`noScripts` (bool), and `appMiddleware` (string|string[]|Record —
controls which app middleware runs for matching routes). Hybrid
rendering/route rules are **unavailable** when the output is produced via
the static `nuxt generate` command, and route rules deploy natively to
Netlify/Vercel platform rules when detected. [Source:
https://nuxt.com/docs/4.x/guide/concepts/rendering] Before applying `cache`,
`swr`, or `isr` to any route, see **Security** below — this exact mechanism
is the surface of a High-severity, precisely version-scoped advisory.

## Decision framework

1. **Is this route's data authenticated or per-user?** If yes, do not apply
   `cache`/`swr`/`isr` route rules to it without first confirming the app
   is on a patched Nuxt version (≥4.5.1, or ≥3.21.10 on the maintenance
   line) **and** that CDN/edge caches were purged after upgrading — the
   documented GHSA-wm8w-6qjm-cv43 cross-user payload disclosure (Security,
   below). If unsure, default to no caching mode for that route (`ssr: true`,
   no `cache`/`swr`/`isr`) — the simplest, safest choice.
2. **Is the app currently on Nuxt 3.x?** State plainly that the 3.x line
   reached end-of-life 2026-07-31 and receives no further bug/security
   fixes [Source: https://nuxt.com/docs/4.x/community/roadmap]. Recommend
   the 3→4 upgrade path (official Codemod recipe) rather than continuing
   new work on an unmaintained line, weighed honestly against real
   migration cost: the `app/` directory restructure and the Node 22.19+
   requirement once bundled `jiti` is removed. [Source:
   https://nuxt.com/docs/4.x/getting-started/upgrade]
3. **Does a route actually need per-route caching?** Prefer the default
   Universal Rendering with no `routeRules` entry (simplest — do nothing)
   unless there's a measured latency/cost need for `swr`/`isr`/`prerender`.
   Don't add hybrid-rendering caching speculatively; it's also the surface
   of the GHSA above, so unjustified caching is both an over-engineering
   and a security-hygiene issue here.
4. **Is a capability best built as a composable, a plugin, or a module?**
   Prefer composables for anything that doesn't need to hook Nuxt's
   build/dev lifecycle (plugins run during hydration and cost render
   performance); reserve modules for genuinely reusable, publishable
   cross-project functionality, not one-off app logic.

## Workflow

1. Determine the Nuxt major/patch version and Node.js version actually in
   use (`nuxt.config.ts`, `package.json`, lockfile).
2. If on 3.x, flag EOL status explicitly and confirm whether an upgrade is
   in scope for this task before proceeding.
3. For any route serving authenticated/per-user data, check
   GHSA-wm8w-6qjm-cv43 applicability before enabling `cache`/`swr`/`isr`.
4. Implement using `app/pages/` file-based routing, auto-imported
   composables/components, and `server/api`/`server/routes` for backend
   logic — not a hand-rolled router or a separate backend framework.
5. Configure `routeRules` per-route only where a real caching/rendering
   need exists (Decision framework, step 3).
6. Verify via `nuxi typecheck`/`nuxi analyze` and the appropriate Vitest
   layout (Testing, below) before declaring done.

## Engineering rules

- Use `app/pages/` file-based routing and the `server/api`/`server/routes`
  split (auto-`/api`-prefixed vs. not) rather than hand-rolling a router or
  a second backend framework inside the same app.
- Never hand-edit generated `.nuxt/` files — it's a git-ignored,
  auto-regenerated development build directory; inspect it via Nuxt
  DevTools' "Virtual Files" tab instead. [Source:
  https://nuxt.com/docs/4.x/guide/directory-structure/nuxt]
- Wrap shared reactive state in a composable backed by `useState` rather
  than exporting a bare module-level `ref`/`reactive` — the latter leaks
  state across concurrent SSR requests, a correctness and memory-leak risk.
- Rely on auto-imports for components/composables/utils; reach for the
  `#imports` alias only when an explicit import is genuinely needed.
- Favor composables over plugins for anything that doesn't require Nuxt's
  build lifecycle; for unavoidable async plugins, set `parallel: true` so
  they load concurrently instead of blocking sequentially.
- Treat a remote layer's dependencies as isolated
  (`node_modules/.c12/<layer>/node_modules/`, invisible to the consumer's
  own tooling/ESLint) and use relative or named aliases inside a layer, not
  `~`/`@` — those resolve against the *consumer* project, not the layer.
  [Source: https://nuxt.com/docs/4.x/guide/going-further/layers]

## Trade-offs

Nitro's multi-target deployment model (Node server, serverless, edge from
one codebase via presets) trades a slightly more layered mental model for
genuine platform portability versus hand-writing deploy-target-specific
server code. Layers give monorepo/multi-app config and directory sharing
beyond what a plain npm package module offers, but isolate their
dependencies in a way that breaks some tooling (ESLint can't resolve a
layer's own deps) — worth it for genuinely shared partial apps, overkill
for a single app that just wants a shared component library (a module or
plain package fits better there).

## Anti-patterns

- **Enabling `cache`/`swr`/`isr` route rules on an authenticated page
  without checking GHSA-wm8w-6qjm-cv43 and purging CDN/edge caches after
  patching** — the single highest-severity Nuxt-specific trap this skill
  guards against.
- Exporting a bare module-level `ref`/`reactive` as shared state instead of
  wrapping it in `useState` — cross-request state leakage under SSR.
  [Source: https://nuxt.com/docs/4.x/getting-started/state-management]
- Calling `$fetch` directly in a component's `setup()` for initial data,
  which can fetch twice (server during SSR, again client-side during
  hydration) instead of using `useFetch`/`useAsyncData`. [Source:
  https://nuxt.com/docs/4.x/getting-started/data-fetching]
- Treating every reusable behavior as a plugin — the domain's
  over-engineering trap; plugins run during hydration, and too many
  expensive ones directly hurts render performance. Prefer composables.
  [Source: https://nuxt.com/docs/4.x/guide/best-practices/plugins]
- Continuing to build new features on Nuxt 3.x past its 2026-07-31 EOL
  without a tracked upgrade plan, as though it were still an actively
  maintained option.

## Security

**GHSA-wm8w-6qjm-cv43 (High) — cross-user payload disclosure.**
[VERSION-SENSITIVE: affects Nuxt ≥4.4.0, fixed in 4.5.1; the 3.21.x
maintenance line was also affected, fixed in 3.21.10.] Apps using `cache`,
`swr`, or `isr` route rules **specifically on authenticated pages** could
serve a cached `_payload.json` response containing one user's data to a
*different* user. [Source: https://nuxt.com/blog/v4-5-security]
Remediation is not just "upgrade the package": run `npx nuxt upgrade
--dedupe`, confirm the lockfile pulls the patched version, and **purge
upstream CDN/edge caches** for any previously cached authenticated
route — already-cached leaked payloads survive a code upgrade alone, since
the stale cache entries themselves keep serving the wrong user's data until
purged. [Source: https://nuxt.com/blog/v4-5-security] Treat any route rule
of `cache`/`swr`/`isr` on an authenticated page as unsafe by default until
both conditions (patched version, purged cache) are explicitly confirmed.

The same July 2026 patch batch (4.5.1/3.21.10, plus `@nuxt/devtools 3.3.1`)
fixed seven other advisories; the most relevant beyond what
[frontend-architecture](../frontend-architecture/SKILL.md) already notes:

- **GHSA-9473-5f9j-94wq** (High) — server-side RCE via server-island props
  when `vue.runtimeCompiler` is enabled (off by default) combined with
  dynamic component resolution; attacker-controlled template keys in island
  props could execute arbitrary code in the Nitro process.
- **GHSA-48hr-524c-v5w3** (Medium) — unauthorized component instantiation:
  server islands forwarding undeclared props onto a polymorphic root
  element let attackers pass arbitrary HTML elements/component names.
  Remediation: explicitly declare accepted island props or set
  `inheritAttrs: false`.
- **GHSA-hxvh-4h3w-prp9** (High) — route-rule authorization bypass:
  case-insensitive routing let uppercase-cased `routeRules`/`appMiddleware`
  auth checks be bypassed (a regression from an earlier patch,
  CVE-2026-53721). Remediation: set `router.options.sensitive: true` if
  case-sensitive route matching is relied on for authorization.
- **GHSA-hxcr-hm88-mpq6** / **GHSA-9pgf-384g-p7mv** (High) — denial of
  service against apps using server components/islands via the
  `/__nuxt_island` endpoint: unauthenticated requests could crash the
  server via `v-for` expansion over a prop or oversized request bodies.
- **GHSA-279x-mwfv-vcqv** (Critical, development-only) — Nuxt DevTools RCE:
  an unauthenticated RPC method exposed over the Vite HMR socket during
  `nuxt dev` (with DevTools enabled) allowed arbitrary command execution;
  explicitly does not affect production deployments.

[Source: https://nuxt.com/blog/v4-5-security]

A **security-headers module** ("nuxt-security" — CSP, rate limiting, XSS
protection, CORS, X-Powered-By removal, optional CSRF) is listed on the
official Nuxt Modules directory, but it is **community-maintained**
(maintainer: Baroshem, ~30 contributors), not a Nuxt-core-team package —
worth flagging explicitly since its prominent listing on nuxt.com makes
that easy to assume incorrectly. [Source:
https://nuxt.com/modules/security] Deep cross-cutting threat modeling
(injection, secrets, transport) is owned by `SK-QA-002`, not restated here.

## Performance

Nuxt 4.5 [VERSION-SENSITIVE: 4.5.0, 2026-07-18] shipped Vite 8 support and
Rspack 2 via Rsbuild as documented alternative builders (the `builder`
config key still defaults to Vite), plus **experimental SSR streaming**
(`experimental.ssrStreaming`, opt-in) aimed at reducing Time to First Byte
by streaming HTML rather than buffering the full server render. [Source:
https://nuxt.com/docs/4.x/getting-started/upgrade; Source:
https://nuxt.com/docs/4.x/api/nuxt-config] `routeRules`
(`swr`/`isr`/`prerender`) remain the primary per-route
performance/cost/freshness lever — confirm the Security section above
before applying any of them to a route serving authenticated data. [Source:
https://nuxt.com/docs/4.x/guide/concepts/rendering] Deep cross-cutting
performance method is owned by `SK-QA-003`, not restated here.

## Testing

Nuxt's overall testing story (Vitest-only for the Nuxt runtime environment,
via `@nuxt/test-utils`) is already noted at the frontend-architecture
level; the Nuxt-specific layout detail: split tests into `test/nuxt/`
(run inside the actual Nuxt runtime environment — full context, slower) and
`test/unit/` (plain Node — fast, for logic with no Nuxt-context
dependency), configured via `defineVitestProject` in `vitest.config.ts`.
[Source: https://nuxt.com/docs/4.x/getting-started/testing] **Documented
hard constraint: a Nuxt-runtime test and an E2E-style test cannot coexist
in the same file** — separate them by file (e.g., a `.nuxt.spec.ts` naming
convention) or by environment directive; also avoid mutating global state
inside Nuxt-environment tests. [Source:
https://nuxt.com/docs/4.x/getting-started/testing] Component/test helpers:
`mountSuspended` (mount any Vue component inside the Nuxt environment, with
async-setup support), `renderSuspended` (Testing-Library render with Nuxt
injections available), `mockNuxtImport` (mock an auto-import — usable only
once per mocked import per test file), `mockComponent` (swap in a
test-double component), `registerEndpoint` (stand up a mock Nitro endpoint
returning fixture data). [Source:
https://nuxt.com/docs/4.x/getting-started/testing] Deep test-strategy
method is owned by `SK-QA-001`.

## Failure handling

- If the Nuxt major/patch version cannot be determined from
  `nuxt.config.ts`/`package.json`/lockfile, ask or explicitly state the
  version the guidance assumes — never assume "latest" silently.
- If shell is unavailable/denied, degrade to advisory config/code output
  and state that `nuxi` commands (build/typecheck/analyze) or a CDN cache
  purge were not executed.
- If a repo is still on Nuxt 3.x, state explicitly that the line is past
  EOL (2026-07-31) and receiving no further fixes, rather than treating it
  as a currently supported option.

## Escalation

- Enabling `cache`/`swr`/`isr` route rules on any page that reads
  authenticated/per-user data requires explicit confirmation that the
  GHSA-wm8w-6qjm-cv43 exposure has been considered (patched version + cache
  purge) before applying.
- A Nuxt 3→4 migration touching the directory structure (the `app/`
  restructure) is presented as a plan for confirmation before any bulk file
  moves are made.

## Outputs & verification

- **Outputs:** version-correct Nuxt code, server routes, or
  `nuxt.config.ts` changes (`routeRules`, modules, experimental/future
  flags); or a GHSA-aware caching-safety assessment / Nuxt 3→4 upgrade
  plan.
- **Verify:** any proposed `cache`/`swr`/`isr` route rule either touches
  only non-authenticated data, or explicitly addresses
  GHSA-wm8w-6qjm-cv43's patch-level and cache-purge remediation;
  file-based-routing and auto-import conventions are used instead of a
  hand-rolled equivalent; every version-specific claim is tagged with the
  range it holds for.

## References

- Source list: see `skill.yaml.source_references` (Nuxt official docs and
  the `v4.5 security` blog post, retrieved 2026-09-10, via
  `research/technologies/nuxt.md`).
- [research/technologies/nuxt.md](../../research/technologies/nuxt.md) —
  the primary research source this skill is grounded in.
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md) —
  Nuxt version-sensitivity entries.
- [frontend-architecture/references/framework-comparison.md](../frontend-architecture/references/framework-comparison.md) —
  the Next.js-vs-Nuxt comparison (owned by `SK-FE-001`, not duplicated here).
