---
name: Next.js
description: >-
  Next.js-specific implementation: App Router vs Pages Router mechanics,
  file-based routing conventions, the Cache Components/Partial Prerendering
  model, Server Actions, and CLI/upgrade paths. Use when the stack uses
  Next.js (next.config.js/.mjs/.ts, an app/ or pages/ directory, "next" in
  package.json) or the task names a Next.js feature. Next.js 13-14 have no
  direct patch for the May 2026 security advisories — version-check first.
  Not for open framework selection or generic SEO strategy.
spec_version: "1.0"
---

## Purpose & scope

Apply Next.js correctly for the version in use — App Router vs Pages Router
mechanics, file-based routing, the Cache Components/Partial Prerendering
model, Server Actions, and the CLI/upgrade path — including the
version-critical May 2026 security advisories. The framework-selection
decision and the Next.js-vs-Nuxt comparison belong to
[frontend-architecture](../frontend-architecture/SKILL.md) (`SK-FE-001`) and
are not repeated here; the rendering-mode decision method belongs to
`SK-FE-005` (not yet authored) and SEO mechanics to `SK-GROW-001` (not yet
authored).

## When to use / When not to use

**Use** when a `next.config.js/.mjs/.ts` file, `"next"` in `package.json`, or
an `app/`/`pages/` directory is present, or the task names a Next.js feature
(App Router, Server Actions, Cache Components, Turbopack, `proxy.ts`). **Do
not use** for a different meta-framework (Nuxt, Remix, SvelteKit, Astro —
route to that skill), an open framework/meta-framework choice (route to
`SK-FE-001`), generic React work with no Next.js-specific mechanism (route to
`SK-TECH-react`), or pure SEO strategy with no rendering-mechanism question
(route to `SK-GROW-001`).

## Knowledge

**Two routers coexist in one project** [Source:
https://nextjs.org/docs]: the **App Router** (newer; Server Components,
streaming, the latest React features) and the **Pages Router** (original,
still supported and maintained).

**The canary-vs-package.json React version split — easy to miss, and
security-relevant:** the App Router uses **React canary releases bundled by
Next.js itself** (stable React 19 changes plus newer framework-validated
features); the Pages Router uses **whatever React version the project's own
`package.json` declares** [Source:
https://nextjs.org/docs]. Practically: when verifying a React CVE fix (e.g.
the RSC deserialization CVEs frontend-architecture flags for React itself),
checking the project's `package.json` React version only tells you the truth
for Pages Router code — App Router code runs on whatever canary Next.js
bundled for that Next.js release, which must be checked separately.

**App Router file-system conventions** [Source:
https://nextjs.org/docs/app/getting-started/installation;
https://nextjs.org/docs/app/api-reference]: routes are determined by
folder/file structure under `app/` — `page.tsx` (route UI), `layout.tsx`
(shared UI; the **root layout is required** and must contain `<html>`/
`<body>`), `loading.tsx`, `error.tsx`, `not-found.js`, `default.js` (now
**required** in every parallel-route slot as of v16 — builds fail without it,
applies_to: >=16.0), `route.ts` (Route Handlers), and `proxy.ts` (renamed
from `middleware.ts` in v16, applies_to: >=16.0 — the Edge runtime is **not**
supported in `proxy`, it always runs on Node.js; projects needing Edge
middleware must stay on the deprecated `middleware.ts` for now).

**Server/Client Component mechanics** [Source:
https://nextjs.org/docs/app/getting-started/server-and-client-components]:
Server Components render to a serialized **RSC Payload**; on first load, HTML
shows a non-interactive preview, the RSC Payload reconciles the tree, then JS
hydrates Client Components; on subsequent client navigations the RSC Payload
is prefetched/cached and Client Components render entirely client-side. Once
a file has `"use client"`, all of its imports and directly rendered
components join the client bundle — but Server Components passed through as
`children`/props stay server-rendered. Props passed Server→Client must be
**serializable**; React Context requires a Client Component wrapper.

**Cache Components model** [Source:
https://nextjs.org/docs/app/getting-started/caching]: opt-in via
`cacheComponents: true`, built on the `"use cache"` directive, `<Suspense>`
boundaries, and explicit handling of runtime APIs (`cookies()`, `headers()`,
`searchParams`) and non-deterministic values (`Math.random()`, `Date.now()`,
`crypto.randomUUID()` — gated behind `connection()`). This produces **Partial
Prerendering (PPR)**: a static shell (cacheable/CDN-servable) combined with
Suspense fallbacks for content streamed at request time. Recommended pattern:
push `await` calls as far down the component tree as possible to maximize
the static shell [Source:
https://nextjs.org/docs/app/getting-started/caching].

**CLI specifics** [Source:
https://nextjs.org/docs/app/getting-started/upgrading;
https://nextjs.org/docs/app/api-reference/config/next-config-js]: `next
upgrade` requires Next.js **>=16.1.0** (earlier versions must run `npx
@next/codemod@canary upgrade latest`); `next typegen` (generates
`PageProps`/`LayoutProps`/`RouteContext` helpers) was introduced in **15.5**;
async `next.config.js` functions have been supported since **v12.1.0**; `next
build` no longer lints automatically as of v16 (the `next lint` command was
removed — use ESLint/Biome directly).

## Decision framework

**1. App Router vs Pages Router for a new project:**
- Default to the **App Router** for new work: it's where Server Components,
  Cache Components/PPR, and current framework development live.
- Stay on (or choose) the **Pages Router** only when there's a concrete
  reason: a large existing Pages Router investment where migration cost
  isn't justified yet, a dependency that assumes the Pages Router model, or a
  need to pin an exact React version outside Next.js's bundled App Router
  canary [Source: https://nextjs.org/docs].
- Both can coexist in one project during an incremental migration — an
  official App Router migration guide exists for this path [Source:
  https://nextjs.org/docs/app/guides/migrating].

**2. Static export vs full SSR/server deployment:**
- `output: 'export'` is sufficient when the route needs **none** of: Dynamic
  Routes with `dynamicParams: true` or without `generateStaticParams()`,
  Route Handlers relying on the incoming `Request`, `cookies()`, `rewrites`,
  `redirects`, `headers` config, `proxy.ts`, ISR, the default `next/image`
  server-based loader, Draft Mode, Server Actions, or Intercepting Routes
  [Source: https://nextjs.org/docs/app/guides/static-exports]. This fits pure
  content sites shippable to S3/Nginx/GitHub Pages with no backend.
- Full SSR (Node server, Docker, or an Adapter) is needed as soon as **any**
  of the above is required, or when Cache Components' Partial Prerendering
  (static shell + request-time streamed content) is the goal — PPR needs a
  server runtime, not static export.
- **Simplest first:** a route with no special directives already gets
  build-time prerendering automatically [Source:
  https://nextjs.org/docs/app/guides/production-checklist] — don't reach for
  `cacheComponents`/`"use cache"`/Suspense architecture on a page that's
  simply static.

## Workflow

1. Confirm the project's actual installed Next.js version before making any
   version-gated recommendation.
2. If the version is 13 or 14, flag the no-direct-patch situation from the
   May 2026 advisories immediately (see Security) before other work.
3. Determine App Router vs Pages Router per the decision framework above.
4. Determine whether static export is sufficient or a server runtime is
   required, per the decision framework above.
5. Implement using the correct file-system conventions and Server/Client
   Component boundaries for the router in play.
6. For data access, keep `"use server"` Server Action files thin and
   delegate to a `server-only`-gated function that performs
   auth/authorization and returns minimal DTOs — re-verify auth **inside**
   every Server Action, not just at the page/layout level, since Server
   Actions are independently reachable via direct POST [Source:
   https://nextjs.org/docs/app/guides/data-security].
7. Verify (below) before declaring done; hand off deep rendering-mode
   trade-offs to `SK-FE-005` and SEO mechanics to `SK-GROW-001` once authored.

## Engineering rules

- Never assume "latest" Next.js behavior; confirm the installed version
  before asserting a version-gated API/CLI/config claim.
- For App Router code, verify the React version via the bundled canary for
  that Next.js release — not the project's `package.json` (that only governs
  Pages Router).
- Keep data access behind a Data Access Layer / `server-only` boundary;
  don't scatter raw DB calls through Server/Client Components [Source:
  https://nextjs.org/docs/app/guides/data-security].
- Re-verify authentication **and** authorization inside every Server Action
  and Route Handler individually — a page- or layout-level check does not
  extend to Server Actions defined within it, and layouts don't re-render on
  navigation [Source: https://nextjs.org/docs/app/guides/data-security].
- Don't return full database objects/rows from a Server Component to a
  Client Component or from a Server Action response — pass only the minimal
  filtered shape needed [Source:
  https://nextjs.org/docs/app/guides/data-security].
- Use `proxy.ts` only for optimistic, cookie-only checks — never as the sole
  authorization gate, since it shouldn't hit the database on every request
  [Source: https://nextjs.org/docs/app/guides/authentication].
- In v16+, access `cookies()`/`headers()`/`draftMode()`/`params`/
  `searchParams` asynchronously only — the v15 synchronous shim is a hard
  error now; run the `next-async-request-api` codemod on migration
  (applies_to: >=16.0) [Source:
  https://nextjs.org/docs/app/guides/upgrading/version-16].

## Trade-offs

App Router's Server Components and Cache Components give finer caching
control and smaller client bundles by default, at the cost of a steeper
mental model (RSC Payload, serialization boundaries, `"use cache"`/Suspense
discipline) versus the Pages Router's simpler, more uniform
client-rendering-plus-`getServerSideProps` model. Static export trades away
an entire class of server-dependent features (Server Actions, ISR, Draft
Mode, dynamic `proxy.ts` logic) for the simplicity and low operational cost
of a pure static host.

## Anti-patterns

- **Running an unpatched Next.js 13 or 14 install without realizing there is
  no direct patch** for the May 2026 advisories — the only fix is upgrading
  to >=15.5.18 or >=16.2.6, not waiting for a 13.x/14.x point release
  (applies_to: 13.x, 14.x, all versions) [Source:
  https://vercel.com/changelog/next-js-may-2026-security-release].
- Trusting client-supplied values (`searchParams`, form data, headers) for
  an authorization decision without re-verifying server-side [Source:
  https://nextjs.org/docs/app/guides/data-security].
- Returning `null` from a layout or top-level component as the sole
  authorization gate — Next.js apps have multiple entry points that bypass a
  single layout-level check [Source:
  https://nextjs.org/docs/app/guides/data-security].
- Enabling nonce-based CSP without weighing that it **forces the entire
  route to dynamic rendering** — static optimization, ISR, and Partial
  Prerendering are all disabled under it [Source:
  https://nextjs.org/docs/app/guides/content-security-policy].
- Continuing to rely on synchronous `cookies()`/`headers()`/`params`/
  `searchParams` access after upgrading to v16 (applies_to: >=16.0) [Source:
  https://nextjs.org/docs/app/guides/upgrading/version-16].
- Adopting the full Cache Components/`"use cache"`/Suspense architecture for
  a page that's simply static — the domain's over-engineering trap; default
  build-time prerendering already covers that case for free.

## Security

**The May 2026 coordinated security release is the single most important
fact in this skill.** It patched **13 advisories** [Source:
https://vercel.com/changelog/next-js-may-2026-security-release]:
middleware/proxy authorization bypasses (segment-prefetch URL bypass, Pages
Router i18n path bypass, dynamic-route param injection bypass, cache
poisoning of proxy redirects — mostly High severity), denial-of-service
issues (an upstream RSC CVE, CVE-2026-23870, plus Cache Components
connection exhaustion and Image Optimization API abuse), one High-severity
SSRF in WebSocket upgrade handling, RSC response cache poisoning/collision
issues, and CSP-nonce/`beforeInteractive`-script XSS issues.

**Affected/patched versions, precisely:**
- **Next.js 13 and 14 — all versions — NO DIRECT PATCH.** The only
  remediation is upgrading to **15.5.18+** or **16.2.6+**.
- Next.js 15, versions <=15.5.17 → patched in **15.5.18**.
- Next.js 16, versions <=16.2.5 → patched in **16.2.6**.
- `react-server-dom-*`, versions 19.0-19.2 → patched to **19.0.6 / 19.1.7 /
  19.2.6**.

A subsequent August 2026 release (16.3.3 and 15.5.24) addressed two further
critical-severity vulnerabilities; `Unresolved: the specific CVE identifiers
for the August 2026 release were not independently verified against a
dedicated advisory page in the source research — treat this as a signal to
re-check current docs, not a specific claim to restate as fact.` [Source:
https://nextjs.org/blog].

**Zero Trust posture and built-in protections** [Source:
https://nextjs.org/docs/app/guides/data-security]: the `server-only` package
causes a build-time error if a module is imported into a Client Component;
Server Actions get encrypted, non-deterministic action IDs (cached max 14
days, regenerated per build) plus dead-code elimination of unreferenced
actions; an Origin-vs-Host check aborts mismatched requests
(`serverActions.allowedOrigins` whitelists additional origins for
reverse-proxy setups); Server Action closures are AES-encrypted per build
(`NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` pins a consistent key across
self-hosted multi-instance deployments).

**CSP/SRI timeline** [Source:
https://nextjs.org/docs/app/guides/content-security-policy]: nonce-based CSP
is generated per-request in `proxy.ts` and Next.js auto-applies it to
framework/page scripts; nonce/CSP-header parsing has been "recommended"
since **v13.4.20** (applies_to: >=13.4.20). SRI-based experimental CSP
(`experimental.sri.algorithm`) preserves static generation instead of
forcing dynamic rendering, but is **App Router only** and was added in
**v14.0.0** (applies_to: >=14.0.0, App Router only, experimental).

Security patches ship as part of both Active LTS and Maintenance LTS for **2
years** post-release [Source: https://nextjs.org/support-policy]. Deep
generic threat-modeling method is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md), not restated
here.

## Performance

**Turbopack is the default bundler for both `next dev` and `next build` as
of v16** (applies_to: >=16.0; Webpack remains available via `--webpack`)
[Source: https://nextjs.org/docs/app/guides/upgrading/version-16]. Concrete
16.3 vendor-reported numbers [Source: https://nextjs.org/blog/next-16-3]:
disk/FileSystem caching (default-on) plus new memory eviction cut long dev
session memory usage by up to **90%**; the FileSystem Cache makes repeat/CI
builds up to **5.5x faster**; replacing web streams with native Node.js
streams in the App Router rendering layer lets SSR handle **up to 22% more
requests under load**; `next build` can delegate type-checking to
`typescript@^7` via the opt-in `useTypeScriptCli` config for roughly **10x
faster type checking**; an experimental Rust-based React Compiler
(`experimental.turbopackRustReactCompiler`) cut `next dev`-to-ready-page time
by ~34% cold / ~46% warm in the vendor's own benchmark, but only with Babel
fully removed from the build.

Cache Components' static shell (PPR) can be served directly from a CDN
without hitting the origin server [Source:
https://nextjs.org/docs/app/getting-started/caching]. The `size`/`First Load
JS` build-output metrics were removed in v16 as "inaccurate in
server-driven architectures using RSC" — use Lighthouse or Vercel Analytics
instead (applies_to: >=16.0) [Source:
https://nextjs.org/docs/app/guides/upgrading/version-16]. Deep generic
performance method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

Next.js first-party documents setup guides for **four** tools: **Jest**,
**Vitest**, **Cypress**, and **Playwright** [Source:
https://nextjs.org/docs/app/guides/testing] — there is no single official
default among them. **Documented constraint:** "since `async` Server
Components are new to the React ecosystem, some tools do not fully support
them" — the docs recommend **End-to-End testing over Unit testing for async
Server Components** as the workaround, not a Next.js-specific limitation but
an ecosystem-level gap the docs explicitly flag [Source:
https://nextjs.org/docs/app/guides/testing]. New in 16.3: `@next/playwright`
ships an `instant()` helper for asserting exactly what UI is visible
instantly during a client navigation, guarding against a previously-instant
route regressing (e.g. a `cookies()` call landing in a shared header)
[Source: https://nextjs.org/blog/next-16-3]. Deep test-strategy method is
owned by [testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If the installed Next.js version can't be determined, ask for it or state
  the assumed version explicitly before giving version-gated guidance —
  never assume "latest" silently.
- If the project is on Next.js 13 or 14, state plainly that no direct patch
  exists and that upgrading to >=15.5.18 or >=16.2.6 is required, before
  continuing unrelated work.
- If shell is unavailable, degrade to advisory code/config output and state
  that `next build`/`next dev`/codemods were not actually run.

## Escalation

- A major-version upgrade (13→14→15→16) touching Server Actions, the
  `middleware`→`proxy` rename, or the caching-model change is a
  breaking-change set — present the upgrade-guide/codemod plan for explicit
  confirmation before running it against a production app.
- Discovering mid-task that a project runs unpatched Next.js 13/14 is a
  security-relevant finding — surface it explicitly, don't fold it silently
  into other work.

## Outputs & verification

- **Outputs:** App Router/Pages Router code, `next.config.js` changes,
  Server Actions/Route Handlers/`proxy.ts`, or a version/security analysis.
- **Verify:** App Router and Pages Router conventions aren't mixed in
  docs-warned ways; the correct React-version source (canary vs
  `package.json`) was used for the router in play; every version-gated claim
  matches the project's actual version; a proposed static export avoids
  features the docs list as unsupported under `output: 'export'`.

## References

- [research/technologies/nextjs.md](../../research/technologies/nextjs.md) —
  primary research source (full citation trail).
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md)
  §Next.js — version-floor table.
- [frontend-architecture](../frontend-architecture/SKILL.md) (`SK-FE-001`) —
  parent skill; owns the Next.js-vs-Nuxt comparison and framework-selection
  decision.
- Source list: see `skill.yaml.source_references` (Next.js official docs and
  the Vercel security changelog, retrieved 2026-09-10, via
  `research/technologies/nextjs.md`).
