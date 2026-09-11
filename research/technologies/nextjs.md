# Next.js — Deep Technology Research

Research date: 2026-09-09. Primary source: the official Next.js documentation hosted at **https://nextjs.org/docs** (canonical host unchanged — no migration observed; the docs are also mirrored version-locally inside a project's `node_modules/next/dist/docs/` starting in recent releases, see Version Information). All citations below point to the specific page fetched on the research date; page content is versioned and may change with future Next.js releases (`lastUpdated` dates are noted inline where relevant).

Current stable version at research time: **Next.js 16.3.4** (16.3 released August 3rd 2026). [Source: https://nextjs.org/blog/next-16-3] All claims are tagged with version sensitivity where the docs indicate the behavior is new, changed, or removed in a specific version.

---

## 1. Core Concepts

[Source: https://nextjs.org/docs] Next.js is described as "a React framework for building full-stack web applications." It uses React Components for UI and adds framework-level features — automatic bundler/compiler configuration, routing, rendering, and data-fetching primitives — so developers don't have to hand-assemble these from lower-level tools.

[Source: https://nextjs.org/docs] Next.js ships **two routing systems** that can coexist in one project, switchable via a docs-site toggle:
- **App Router** (the newer router): supports the latest React features and Server Components; the App Router uses **React canary releases built in**, which include all stable React 19 changes plus newer framework-validated features.
- **Pages Router**: the original router, still supported and maintained; it uses whatever React version is declared in the project's own `package.json`.

[Source: https://nextjs.org/docs/app/getting-started/server-and-client-components] By default, layouts and pages in the App Router are **React Server Components**, which run on the server, can fetch data directly, and stream results to the client. **Client Components** (opted into via the `"use client"` directive) run in the browser (and are also pre-rendered on the server for the first load) and are used for interactivity, state, effects, and browser-only APIs.

[Source: https://nextjs.org/docs/app/getting-started/server-and-client-components] Key mechanics of the Server/Client model:
- On the server, Server Components render into a serialized **React Server Component (RSC) Payload**; Client Components and the RSC Payload are used to prerender HTML.
- On first client load: HTML shows an immediate non-interactive preview → RSC Payload reconciles the Server/Client component tree → JavaScript hydrates Client Components.
- On subsequent client-side navigations, the RSC Payload is prefetched/cached and Client Components render entirely client-side without full server HTML.
- Once a file has `"use client"`, all of its imports and directly rendered components are included in the client bundle — but Server Components passed as `children`/props are rendered server-side and passed through, not pulled into the client bundle.
- Props passed from Server → Client Components must be **serializable** by React.
- React Context is not supported directly in Server Components; a Client Component wrapper is required for providers.

[Source: https://nextjs.org/docs/app/getting-started/installation] File-system routing underlies the App Router: routes are determined by folder/file structure inside an `app/` directory, using conventions like `page.tsx` (route UI), `layout.tsx` (shared UI, the root layout is required and must contain `<html>`/`<body>`), `loading.tsx`, `error.tsx`, `route.ts` (Route Handlers), etc.

[Source: https://nextjs.org/docs/app/getting-started/caching] **Cache Components** (opt-in via `cacheComponents: true` in `next.config`) is presented as the current/forward-looking caching and rendering model, built around the `"use cache"` directive, `<Suspense>` boundaries, and explicit handling of runtime APIs (`cookies()`, `headers()`, `searchParams`) and non-deterministic values (`Math.random()`, `Date.now()`, `crypto.randomUUID()`). This produces **Partial Prerendering (PPR)**: a static "shell" combining prerendered/cached content with Suspense fallbacks for content that streams at request time.

[Source: https://nextjs.org/docs/app/guides/caching-without-cache-components] `Unresolved: not directly fetched, but referenced by other pages as the "Previous Model"` — Next.js docs describe a separate, older caching model (fetch cache options, `unstable_cache`, route segment configs) for projects not using Cache Components. Since this project's citation rule requires fetching the actual page, treat the previous-model mechanics as **not independently verified** here beyond what related pages describe; see Section 8 (Performance) for what was directly confirmed.

---

## 2. Architecture

[Source: https://nextjs.org/docs/architecture] The official "Architecture" section of the docs (distinct from Getting Started/Guides/API Reference) covers: **Accessibility** (built-in a11y features), **Fast Refresh** (hot-module-reload experience for instantaneous feedback on component edits), **Next.js Compiler** (Rust-based compiler that transforms/minifies the app), and **Supported Browsers** (browser support and which JS features are polyfilled).

[Source: https://nextjs.org/docs/architecture/supported-browsers] Next.js targets **modern browsers with zero configuration**: Chrome 111+, Edge 111+, Firefox 111+, Safari 16.4+ (matches the default Browserslist config it injects: `["chrome 111", "edge 111", "firefox 111", "safari 16.4"]`). It auto-injects targeted polyfills (`fetch()`, `URL`, `Object.assign()`) only for browsers that need them, and supports modern JS (async/await, optional chaining, nullish coalescing, class fields, dynamic `import()`) out of the box.

[Source: https://nextjs.org/docs/app/getting-started/server-and-client-components] Rendering pipeline architecture (App Router): route-segment-level rendering split into chunks (including parallel route slots) → Server Components render to RSC Payload → HTML is prerendered from Client Components + RSC Payload → client hydrates.

[Source: https://nextjs.org/blog/next-16-3] **Turbopack** (Rust-based bundler) is the default bundler as of Next.js 16 (see Section 13, Breaking Changes) for both `next dev` and `next build`; Webpack remains available via `--webpack`. 16.3 adds Turbopack **disk/FileSystem caching** (used by both dev and build, reported 5.5x faster repeat CI builds in one case) and **memory eviction** (reported up to ~90% dev-server RAM reduction in the examples given).

[Source: https://nextjs.org/docs/app/api-reference/edge] Next.js has **two server runtimes**: the **Node.js Runtime** (default, full Node.js API access, used for application rendering) and the **Edge Runtime** (a restricted, Web-standard-API-only runtime used specifically by `proxy.ts` — see Section 14, Limitations, for its constraints).

[Inference, not confirmed in docs] The overall architecture — file-system routing → Server/Client Component split → RSC Payload serialization → streaming HTML with Suspense boundaries → client-side router cache for subsequent navigations — is consistent with what all the fetched pages describe, but no single fetched page presents this as one unified "architecture diagram"; the description above is synthesized from the Core Concepts, Caching, and Server/Client Components pages cited throughout.

---

## 3. APIs

[Source: https://nextjs.org/docs/app/api-reference] The official API Reference (App Router) is organized into these top-level categories:
- **Directives** — e.g. `"use client"`, `"use server"`, `"use cache"` (and variants `"use cache: private"`, `"use cache: remote"`) — "how React and Next.js directives define client entry points, Server Functions, and cached output."
- **Components** — built-in components, e.g. `next/image` (`<Image>`), `<Link>`, `<Script>`, `<Font>`.
- **File-system conventions** — e.g. `layout.js`, `page.js`, `route.js`, `loading.js`, `error.js`, `not-found.js`, `default.js`, `proxy.js` (formerly `middleware.js`), `instrumentation.js`, parallel/intercepting routes, `public/` folder, `src/` folder.
- **Functions** — e.g. `cookies()`, `headers()`, `draftMode()`, `redirect()`, `notFound()`, `revalidateTag()`, `updateTag()`, `refresh()`, `cacheLife()`, `cacheTag()`, `connection()`, `generateStaticParams()`, `generateMetadata()`, `generateSitemaps()`, `useReportWebVitals()`, `next/root-params`.
- **Configuration** — `next.config.js` options (see Section 4).
- **CLI** — `next dev`, `next build`, `next start`, `next upgrade`, `next typegen`, `create-next-app`.
- **Adapters** — the Build Adapters API for deployment platforms.
- **Edge Runtime** — the restricted runtime reference.
- **Turbopack** — bundler-specific configuration/reference (e.g. `import.meta.glob`).

[Source: https://nextjs.org/blog/next-16-3] Notable APIs newly introduced/stabilized in **16.3** (version-sensitive, ≥16.3 only unless noted):
- `next/root-params` — a new function (`lang()` style) for reading root-level dynamic params (e.g. `[lang]`) from any Server Component without prop-drilling; supported in Server Components at 16.3, with Route Handlers/Server Actions support "planned for a future release." This **replaces** the removed `unstable_rootParams` (see Section 13).
- `catchError` (from `next/error`) — a custom error-boundary API that, unlike plain React error boundaries, doesn't interfere with `notFound()`/`redirect()`, and exposes a `retry()` function that can re-render failed Server Components.
- `useOffline` hook (from `next/offline`) — reports connectivity state; paired with the experimental `experimental.useOffline` config flag for automatic retry of failed fetches/Server Actions on reconnect.
- `import.meta.glob` — a Vite-compatible glob-import API newly supported by Turbopack.

[Source: https://nextjs.org/docs/app/guides/upgrading/version-16] APIs stabilized in Next.js **16** (dropping `unstable_` prefixes): `cacheLife`, `cacheTag` (now imported as `cacheLife`/`cacheTag` from `next/cache` without the `unstable_` prefix). New Server Actions cache-control APIs: `revalidateTag(tag, cacheLifeProfile)` (now **requires** a second `cacheLife` profile argument — the single-argument form is deprecated and errors under TypeScript), `updateTag()` (read-your-writes semantics), `refresh()` (refreshes the client router from a Server Action).

[Source: https://nextjs.org/docs/app/api-reference/config/next-config-js] `next/experimental/testing/server` exposes `unstable_getResponseFromNextConfig()` (since **Next.js 15.1**) — an experimental unit-testing utility that runs a `next.config.js`'s `headers`/`redirects`/`rewrites` functions against a synthetic request and returns a `NextResponse`; explicitly noted to *not* account for proxy or filesystem routes, so results can diverge from production.

---

## 4. Configuration

[Source: https://nextjs.org/docs/app/api-reference/config/next-config-js] Configuration lives in `next.config.js` (or `.mjs` for ESM, or `.ts` for TypeScript — note: `.cjs`/`.cts` extensions are explicitly **not supported**), exporting a default object, function, or async function `(phase, { defaultConfig }) => config`. `phase` values (e.g. `PHASE_DEVELOPMENT_SERVER`) are importable from `next/constants` to branch config by build phase. Async config functions have been supported **since Next.js 12.1.0**.

[Source: https://nextjs.org/docs/app/api-reference/config/next-config-js] The docs list roughly 65 distinct top-level config keys as of the research date, spanning: routing/deployment (`basePath`, `assetPrefix`, `trailingSlash`, `output`, `distDir`, `deploymentId`), caching (`cacheComponents`, `cacheHandlers`, `cacheLife`, `cacheMaxMemorySize`, `expireTime`, `staleTimes`), images (`images`), Turbopack (`turbopack`, `turbopackChunking`, `turbopackFileSystemCache`, `turbopackMemoryEviction`, `turbopackRustReactCompiler`, `turbopack.ignoreIssue`, `turbopackLocalPostcssConfig`), security/headers (`headers`, `redirects`, `rewrites`, `poweredByHeader`, `crossOrigin`), React behavior (`reactCompiler`, `reactStrictMode`, `reactMaxHeadersLength`), TypeScript (`typescript`, `useTypeScriptCli`), and many more (full list captured under Section 3 references). Full canonical list: https://nextjs.org/docs/app/api-reference/config/next-config-js.

[Source: https://nextjs.org/docs/app/guides/upgrading/version-16] **[Version-sensitive, changed in v16]** The `turbopack` config option moved from `experimental.turbopack` (Next.js 15) to a **top-level** `turbopack` key (Next.js 16). `serverRuntimeConfig`/`publicRuntimeConfig` (config-based runtime env vars) were **removed** in v16 — replaced by direct `process.env` access in Server Components and `NEXT_PUBLIC_`-prefixed vars for client access. The `eslint` config key was removed (linting is no longer run by `next build`). `experimental.dynamicIO` and `experimental.useCache` were removed in favor of top-level `cacheComponents`. `experimental_ppr` route segment config was removed in favor of `cacheComponents`.

[Source: https://nextjs.org/docs/app/getting-started/upgrading] Config files can also be validated/tested indirectly via the `next typegen` CLI command (introduced in **Next.js 15.5**), which generates type helpers `PageProps`, `LayoutProps`, `RouteContext`.

---

## 5. Recommended Patterns

[Source: https://nextjs.org/docs/app/guides/data-security] The docs recommend picking **one** of three data-fetching approaches per project and not mixing them: (1) **External HTTP APIs** with a Zero Trust model — for existing large apps/organizations; (2) a **Data Access Layer (DAL)** — recommended for **new projects**: a server-only internal library that performs authorization checks and returns minimal Data Transfer Objects (DTOs), memoized with React's `cache()`; (3) **Component-level data access** — for prototypes only, explicitly flagged as easy to misuse (see Anti-Patterns).

[Source: https://nextjs.org/docs/app/guides/data-security] Recommended mutation pattern: keep `"use server"` Server Action files thin, delegate to a `server-only` DAL function that performs auth/authorization and returns filtered data; re-verify authentication **and** authorization inside every Server Action (not just at the page/layout level), since Server Actions are independently reachable via direct POST requests.

[Source: https://nextjs.org/docs/app/getting-started/caching] Recommended Cache Components patterns: use `'use cache'` + `cacheLife()` for data or UI that can be shared across users; wrap runtime-dependent reads (`cookies()`, `headers()`, `searchParams`) in `<Suspense>`; **push `await` calls (params, cookies, data fetches) as far down the component tree as possible** ("maximizing the static shell") so more of a route can be prerendered; use `connection()` before non-deterministic calls (`Math.random()`, `Date.now()`, `crypto.randomUUID()`) that must vary per request.

[Source: https://nextjs.org/docs/app/guides/authentication] Recommended auth pattern: three-layer model (Authentication → Session Management → Authorization); use `<form>` + Server Actions + `useActionState` for sign-up/login; validate all form input server-side with a schema library (Zod/Valibot/Yup are named as examples, not endorsements); store sessions in `httpOnly`, `secure`, `sameSite: 'lax'` cookies; centralize authorization in a DAL with a memoized `verifySession()`; use Proxy (`proxy.ts`) only for **optimistic** (cookie-only) checks, never for the sole line of defense, since Proxy shouldn't hit the database on every request (including prefetches).

[Source: https://nextjs.org/docs/app/guides/production-checklist] Recommended during-development patterns: use `<Link>` for prefetching, wrap Request-time API usage (`cookies`, `searchParams`) in `<Suspense>` deliberately, keep `"use client"` boundaries as small/deep as possible to minimize client JS, use the Font module and `<Image>`/`<Script>` components for automatic optimization, add `app/global-error.tsx` and `app/global-not-found.tsx` for consistent fallback UI.

[Source: https://nextjs.org/docs/app/guides/upgrading/version-16] The Next.js team's own recommended upgrade **pattern** is now to hand the upgrade to an AI coding agent, pointed at version-matched bundled docs (`node_modules/next/dist/docs/`) and the official upgrade-guide page, with an explicit prompt template provided in the docs.

---

## 6. Anti-Patterns

[Source: https://nextjs.org/docs/app/guides/data-security] Explicitly documented anti-patterns:
- **Passing entire raw database records from a Server Component to a Client Component** — "This exposes all the fields in userData to the client." The docs show the exact bad code (`<Profile user={userData} />` passing a full SQL row) and the fix (sanitize/select only public fields first).
- **Accepting/trusting a wide, unfiltered `user: User` prop type in a Client Component** — encourages passing everything the type allows, which invites the leak above.
- **Trusting client-supplied values (`searchParams`, form data, headers) for authorization decisions** without re-verifying server-side — shown concretely as `if ((await searchParams).isAdmin === 'true') return <AdminPanel />` labeled explicitly **BAD**.
- **Returning full database objects from Server Actions** to the client instead of a minimal `{ success: true }`-style shape.
- **Triggering mutations (cookie deletion, cache revalidation) as a side effect during rendering** instead of inside a Server Action — Next.js explicitly prevents setting cookies or revalidating inside render to avoid this.
- **Relying on a page-level or layout-level auth check to protect Server Actions or nested route segments** — "A page-level authentication check does not extend to the Server Actions defined within it," and layouts "do not re-render on navigation," so an auth check placed only in a layout will not re-run on every route change and does not stop nested segments/parallel-route slots from rendering.
- **Returning `null` from a layout or top-level component as the sole authorization gate** — explicitly called out as **not recommended** since Next.js apps have multiple entry points that bypass this.
- **Mixing data-fetching approaches** (HTTP APIs, DAL, component-level) within one codebase — the docs recommend picking one to keep expectations clear for developers and security auditors.

[Source: https://nextjs.org/docs/app/guides/upgrading/version-16] **[Version-sensitive: v16]** Continuing to rely on synchronous access to `cookies()`, `headers()`, `draftMode()`, `params`, or `searchParams` is now a hard error in v16 (it was a deprecated-but-working compatibility shim in v15) — an anti-pattern to avoid going forward; a codemod exists to auto-migrate.

[Source: https://nextjs.org/docs/app/guides/content-security-policy] Anti-pattern: enabling nonce-based CSP without understanding it **forces the entire route to dynamic rendering** — "Static optimization and Incremental Static Regeneration (ISR) are disabled" and "Partial Prerendering (PPR) is incompatible with nonce-based CSP." Applying nonces broadly without weighing this tradeoff is called out as a performance risk.

[Inference, not confirmed in docs] The general shape of these documented anti-patterns (broad prop types leaking data, trusting client input, single-layer auth checks) mirrors common web-security anti-patterns generally, but the specific code-level examples above are drawn directly from the Data Security guide, not inferred.

---

## 7. Security

[Source: https://nextjs.org/docs/app/guides/data-security] Next.js documents a **Zero Trust** posture for Server Components, since RSCs change where/how data is accessed relative to a traditional client-only frontend. Core mechanisms:
- **`server-only` package** — causes a **build-time error** if a module marked `import 'server-only'` is imported into a Client Component; Next.js handles this internally (the actual npm package contents aren't used, but installing it avoids lint/dependency-check false positives). A companion `client-only` package exists for the inverse.
- **React Taint APIs** (`experimental_taintObjectReference`, `experimental_taintUniqueValue`), enabled via `experimental.taint` in `next.config.js`, prevent tainted objects/values from being passed to the client — described as a **defense-in-depth** layer, not a substitute for filtering data in the DAL.
- **Server Actions built-in protections**: encrypted, non-deterministic action IDs (recalculated periodically, cached max **14 days**, regenerated on new builds); **dead-code elimination** removes unused (unreferenced) Server Actions from the client bundle so they don't become public endpoints.
- **Server Actions origin check**: compares the `Origin` header to `Host` (or `X-Forwarded-Host`); mismatched requests are aborted. For reverse-proxy/multi-domain setups, `serverActions.allowedOrigins` in `next.config.js` whitelists additional origins.
- **Closures in Server Actions are automatically encrypted** — a new AES key is generated per build; `process.env.NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` (base64, decoded to 16/24/32 bytes) can pin a consistent key across self-hosted multi-instance deployments, generable via `openssl rand -base64 32`.
- Server Actions only accept `POST`, and modern browsers default cookies to `SameSite`, which the docs say prevents "most CSRF vulnerabilities."

[Source: https://nextjs.org/docs/app/guides/content-security-policy] CSP guidance: generate a fresh nonce per request in `proxy.ts`, set it in both the `Content-Security-Policy` response header and a custom request header (`x-nonce`) for reading in Server Components; Next.js auto-applies the nonce to framework/page scripts once it can parse the CSP header. Nonces **require dynamic rendering** (no static pages) — see Limitations. An experimental alternative, **Subresource Integrity (SRI)** hash-based CSP (`experimental.sri.algorithm`, e.g. `'sha256'`), preserves static generation but is explicitly experimental and **App Router only** — "Not supported in Pages Router." **[Version-sensitive]** SRI experimental support added in **v14.0.0**; nonce/CSP-header parsing "recommended" from **v13.4.20**.

[Source: https://vercel.com/changelog/next-js-may-2026-security-release] The **May 2026 coordinated security release** patched **13 advisories** across: middleware/proxy authorization bypass (segment-prefetch URL bypass, Pages Router i18n path bypass, dynamic-route param injection bypass, cache poisoning of proxy redirects — mostly **High** severity), denial of service (an upstream React Server Components CVE — **CVE-2026-23870** — plus Cache Components connection exhaustion and Image Optimization API abuse), one **High**-severity SSRF in WebSocket upgrade handling, RSC response cache poisoning/collision issues, and CSP-nonce / `beforeInteractive`-script XSS issues. Affected/patched versions: Next.js 13–14 (all versions affected) → upgrade to **15.5.18** or **16.2.6**; Next.js 15 ≤15.5.17 → **15.5.18**; Next.js 16 ≤16.2.5 → **16.2.6**; `react-server-dom-*` 19.0–19.2 → 19.0.6 / 19.1.7 / 19.2.6.

[Source: https://nextjs.org/blog] A **subsequent August 2026 security release** (16.3.3 and 15.5.24) addressed **two additional critical-severity vulnerabilities** [Source: WebSearch summary of https://vercel.com/changelog and https://nextjs.org/blog — the specific advisory page was not independently fetched; treat the exact CVE identifiers for this August release as **Unresolved: could not verify without fetching the specific August 2026 advisory page**].

[Source: https://nextjs.org/support-policy] Security patches are explicitly part of both **Active LTS** (bundled with regular feature/bugfix releases) and **Maintenance LTS** (where they are one of only two categories of change still shipped, alongside critical bug fixes) for **2 years** after a major version's initial release. "Rare exceptions" — out-of-policy security patches for versions outside the LTS window — may be released "depending on severity."

[Source: https://nextjs.org/docs/app/guides/data-security] Auditing checklist explicitly given for security reviews: verify an isolated DAL exists and that DB packages/env vars aren't imported outside it; check `"use client"` prop types for over-broad/sensitive data; check `"use server"` files for input validation, re-authorization, ownership/authorization checks (not just authentication), filtered return values, and DAL delegation; treat dynamic route params (`[param]`) as user input requiring validation; give `proxy.ts` and `route.ts` extra scrutiny and "Penetration Testing or Vulnerability Scanning regularly."

---

## 8. Performance

[Source: https://nextjs.org/blog/next-16-3] Turbopack (default bundler since v16) performance improvements confirmed by the vendor for **16.3**: dev-server memory usage cut "up to 90%" in long sessions via disk caching (introduced 16.1) plus new memory eviction (both default-on); repeat/CI builds up to **5.5x faster** via a new default-on FileSystem Cache; server-side rendering handles **up to 22% more requests under load** after replacing web streams with native Node.js streams in the App Router rendering layer; `next build` can optionally use **TypeScript 7** for ~10x faster type checking (`useTypeScriptCli` config, opt-in by installing `typescript@^7`); prefetch payload bundling reduces the number of prefetch requests (`prefetchInlining` config).

[Source: https://nextjs.org/docs/app/guides/production-checklist] Documented **automatic** optimizations requiring no configuration: Server Components (zero client-JS impact by default), automatic route-segment code-splitting, `<Link>` viewport-triggered prefetching, build-time prerendering with opt-in Dynamic Rendering, and multi-layer caching (data requests, rendered Server/Client Component output, static assets).

[Source: https://nextjs.org/docs/app/guides/production-checklist] Recommended before-production performance workflow: run `next build` + `next start` locally to approximate production; run **Lighthouse** in incognito plus real field Core Web Vitals data; use the `useReportWebVitals` hook to ship Web Vitals to analytics; analyze bundles with `@next/bundle-analyzer` (Webpack) or the Turbopack bundle analyzer, and third-party size tools (Import Cost, Package Phobia, Bundle Phobia, bundlejs).

[Source: https://nextjs.org/docs/app/getting-started/caching] Core performance mechanic of the current model: Cache Components produces a **static shell (PPR)** that "can be served directly from a CDN, without going through to the upstream server," making direct navigations instant; **Partial Prefetching** (16.3 default-eligible, config: `partialPrefetching`) lets `<Link>` prefetch just the App Shell by default, or the full URL-specific content with `prefetch={true}`.

[Source: https://nextjs.org/docs/app/guides/upgrading/version-16] **[Version-sensitive: v16]** The `size`/`First Load JS` metrics were **removed** from `next build` output because the team found them "inaccurate in server-driven architectures using React Server Components" — both Turbopack and Webpack disagreed on how to account for Client Component payload. Chrome Lighthouse or Vercel Analytics are recommended instead.

[Source: https://nextjs.org/docs/architecture/supported-browsers] Bundle-size performance mechanic: polyfills (`fetch()`, `URL`, `Object.assign()`) are only shipped to browsers that need them — "the majority of the web traffic globally will not download these polyfills."

[Source: https://nextjs.org/blog/next-16-3] Experimental performance feature: a **Rust-based (native, Babel-free) React Compiler** running inside Turbopack (`experimental.turbopackRustReactCompiler`), reported to cut `next dev`-to-ready-page time by ~34% cold / ~46% warm in the vendor's v0 benchmark — but only if Babel is fully removed from the build; smaller gains if Babel is still used for other transforms.

---

## 9. Testing

[Source: https://nextjs.org/docs/app/guides/testing] Next.js officially documents setup guides for **four** testing tools: **Jest** (unit/snapshot testing), **Vitest** (unit testing), **Cypress** (E2E and component testing), and **Playwright** (E2E testing). The overview page defines five test types the framework distinguishes conceptually: Unit, Component, Integration, End-to-End (E2E), and Snapshot testing.

[Source: https://nextjs.org/docs/app/guides/testing] **Explicit caveat**: "Since `async` Server Components are new to the React ecosystem, some tools do not fully support them. In the meantime, we recommend using End-to-End Testing over Unit Testing for `async` components." This is a direct, documented limitation of the current unit-testing tool ecosystem relative to Server Components, not a Next.js-specific restriction.

[Source: https://nextjs.org/blog/next-16-3] **[New in 16.3]** A `@next/playwright` package ships an `instant()` test helper for writing Playwright regression tests that assert exactly what UI is visible instantly during a client navigation (guarding against a previously-instant route becoming slow due to a refactor, e.g. a `cookies()` call landing in a shared header, or a `<Suspense>` boundary moving).

[Source: https://nextjs.org/docs/app/api-reference/config/next-config-js] **[Since Next.js 15.1]** `next/experimental/testing/server` exposes `unstable_getResponseFromNextConfig()` for unit-testing `headers`/`redirects`/`rewrites` functions defined in `next.config.js` directly, with the caveat that it does not account for proxy or filesystem routing, so results can diverge from production behavior.

[Unresolved: whether Next.js documents any first-party mocking utilities for Server Actions, Route Handlers, or the App Router request context beyond the config-testing helper above — none were found in the pages fetched, and time did not permit fetching the individual Jest/Playwright/Cypress/Vitest setup subpages in full.]

---

## 10. Deployment

[Source: https://nextjs.org/docs/app/getting-started/deploying] Four documented deployment paths, with a feature-support table:

| Deployment Option | Feature Support |
|---|---|
| Node.js server | All |
| Docker container | All |
| Static export | Limited |
| Adapters | Varies (verified adapters run the compatibility test suite) |

- **Node.js server**: any provider supporting Node.js; `next build` + `next start`; supports "all Next.js features"; a custom server is possible as an "eject" option. Named community templates: Flightcontrol, Railway, Replit, Hostinger.
- **Docker**: any Docker-capable host/orchestrator (Kubernetes included); "supports all Next.js features"; official example templates for standalone output, static export in a container, and multi-environment configs; **note**: for local development on Mac/Windows, the docs recommend `npm run dev` over Docker for performance. Named platform guides: DigitalOcean, Fly.io, Google Cloud Run, Render, SST.
- **Static export** (`output: 'export'` in `next.config.js`): produces plain HTML/CSS/JS deployable to any static host (S3, Nginx, Apache, GitHub Pages); explicitly **does not support** features requiring a server (full list in Section 14, Limitations).
- **Adapters**: the **Deployment Adapter API** (`adapterPath` config) lets platforms customize the Next.js build/output. "**Verified adapters**" are open source, run the full Next.js compatibility test suite, and are hosted under the Next.js GitHub org — currently **Vercel** and **Bun**. Cloudflare and Netlify are noted as building verified adapters but currently ship their own (unverified-by-Next.js-team) integrations. Other listed integrations (unverified): Appwrite Sites, AWS Amplify Hosting, Cloudflare, Deno Deploy, Firebase App Hosting, Netlify.

[Source: https://nextjs.org/docs/app/guides/static-exports] Static export mechanics: `next build` writes an `out/` folder (or a custom `distDir`) with one HTML file per route; Server Components run at build time like traditional SSG; Route Handlers must be explicitly marked `export const dynamic = 'force-static'` and only support `GET`; `next/image` needs a **custom loader** (default optimization loader is unsupported in export mode) — example given for Cloudinary. **[Version-sensitive]** `next export` was **deprecated in v13.3.0** and fully **removed in v14.0.0** in favor of the `output: 'export'` config; App Router static-export support (RSC + Route Handlers) was added in **v13.4.0**.

[Source: https://nextjs.org/docs/app/guides/debugging] Firsthand confirmation that `--inspect` remote debugging is relevant to containerized deployment: `--inspect=0.0.0.0` is explicitly called out for "remote debugging access outside localhost, such as when running the app in a Docker container."

---

## 11. Migration

Next.js's official migration coverage splits into two kinds, both documented:

**A. Upgrading between Next.js major versions** [Source: https://nextjs.org/docs/app/getting-started/upgrading]:
- `next upgrade` CLI command (**[Version-sensitive: requires ≥16.1.0]**; versions before 16.1.0 must instead run `npx @next/codemod@canary upgrade latest`).
- Manual path: `npm i next@latest react@latest react-dom@latest eslint-config-next@latest`.
- Canary channel: `npm i next@canary`, documented as the way to try features (e.g. `forbidden`/`unauthorized` auth primitives) ahead of stable release.
- Individual version guides exist for **14→ (v14 guide covers 13→14)**, **15 (14→15)**, and **16 (15→16)**: https://nextjs.org/docs/app/guides/upgrading/version-14, .../version-15, .../version-16.
- The team's now-**recommended** upgrade method is delegating to an AI coding agent with a supplied prompt template that reads version-matched bundled docs and follows the specific version's upgrade guide as "source of truth," running codemods, then verifying with dev/build/browser checks.

**B. Migrating from other frameworks/routers to Next.js** [Source: https://nextjs.org/docs/app/guides/migrating]: three official guides — **App Router migration** (Pages Router → App Router, within Next.js itself), **Create React App → Next.js**, and **Vite → Next.js**. [Unresolved: guide content for these three pages was not individually fetched in full; only the index listing was confirmed. Do not assume specific migration steps beyond the page titles/descriptions captured.]

**Codemods** [Source: https://nextjs.org/docs/app/guides/upgrading/version-16]: `@next/codemod` (canary channel) provides automated migrations, confirmed examples include: `upgrade latest` (general major-version upgrade), `next-lint-to-eslint-cli` (migrate off the removed `next lint` command), `next-async-request-api` (migrate remaining synchronous `params`/`searchParams`/`cookies()`/`headers()`/`draftMode()` usage to async), and `agents-md` (scaffolds/updates the `AGENTS.md` file used to ground AI coding agents in version-matched docs). The v16 `upgrade` codemod specifically also updates `next.config.js` to the new top-level `turbopack` key, migrates `middleware` → `proxy` naming, and strips `unstable_` prefixes from now-stable APIs — but the docs note it "does not run every migration codemod," so `next-async-request-api` must be run separately if needed.

[Source: https://nextjs.org/docs/app/guides/migrating-to-cache-components] Referenced (not independently fetched in full) as the dedicated guide for migrating an existing app's route-segment-config-based caching to the `cacheComponents` model.

---

## 12. Version Information

[Source: https://nextjs.org/blog/next-16-3] **Current stable version at research time: 16.3.4** (16.3 line published August 3rd, 2026; the specific `.4` patch reflects the `version:` frontmatter stamped on docs pages fetched on 2026-09-09). [Version-sensitive — this is a snapshot; check `nextjs.org/blog` for anything newer.]

[Source: https://nextjs.org/support-policy] **Versioning model**: canary channel gets **daily** pre-release builds with internal testing; stable releases are promoted from canary when the team judges them ready; **major versions** are released "periodically" — concrete recent examples given: **v16 released Oct 21, 2025**, **v15 released Oct 21, 2024** (implying roughly a 12-month major-version cadence in that instance, though the policy text does not commit to a fixed interval).

[Source: https://nextjs.org/support-policy] **LTS model** — this is the officially documented support-window structure:
- **Active LTS**: from release until the *next* major version ships; receives new features, regular bug fixes, performance improvements, and security patches (delivered as semver-minor/patch releases).
- **Maintenance LTS**: **2 years** following a major version's initial release; receives *only* critical bug fixes and essential security patches (still shipped as semver-minor releases, even for breaking fixes), explicitly to reduce regression risk.
- Current table given by the docs: **16.x — released Oct 21, 2025 — Active LTS**; **15.x — released Oct 21, 2024 — Maintenance LTS**.
- Official recommendation: "serve production applications with either the latest **Active** or **Maintenance** LTS release."
- "Rare exceptions" allow out-of-policy security patches for versions outside this window depending on severity.

[Inference, not confirmed in docs] Applying the 2-year Maintenance LTS window to the stated dates implies Next.js 14.x's Maintenance LTS period (if it followed the same policy retroactively) would be expected to have ended around two years after its own initial release; the exact date of Next.js 14's initial release was not fetched/confirmed in this research pass, so this is not asserted as fact.

[Source: https://nextjs.org/docs/app/getting-started/installation] Minimum supported tooling **as of 16.3.4**: **Node.js 20.9+**, TypeScript **5.1.0+**; supported OSes macOS/Windows(incl. WSL)/Linux; supported browsers Chrome 111+/Edge 111+/Firefox 111+/Safari 16.4+.

[Source: https://nextjs.org/blog/next-16-3] "This is our biggest update to the framework since Next.js 16.0 came out last November [2025]" — corroborates the Oct/Nov 2025 timing of the v16.0 release window.

---

## 13. Breaking Changes

All items below are from the **official Next.js 16 upgrade guide** [Source: https://nextjs.org/docs/app/guides/upgrading/version-16] and are explicitly labeled **"Breaking change"** or presented as removals in that document. **[Version-sensitive: these apply specifically to the 15→16 major-version transition.]**

- **Async Request APIs fully enforced**: `cookies()`, `headers()`, `draftMode()`, `params` (in `layout.js`/`page.js`/`route.js`/`default.js`/`opengraph-image`/`twitter-image`/`icon`/`apple-icon`), and `searchParams` (in `page.js`) can now **only** be accessed asynchronously — the v15 synchronous compatibility shim is fully removed. Codemod: `next-async-request-api`.
- **Async `params`/`id` for image-generation and sitemap functions**: `opengraph-image`, `twitter-image`, `icon`, `apple-icon`'s default export now receives `params`/`id` as Promises (though `generateImageMetadata` itself still receives synchronous `params`); `sitemap`'s `id` (from `generateSitemaps`) is now a Promise.
- **Turbopack is the default bundler** for both `next dev` and `next build` — no more `--turbopack` flag needed. A project with a **custom Webpack config will fail `next build`** unless it opts into `--turbopack` (ignoring the webpack config), migrates the config to Turbopack-compatible options, or explicitly opts back to Webpack with `--webpack`.
- **`experimental.turbopack` config moved** to a top-level `turbopack` key.
- **Turbopack does not support the legacy Sass tilde (`~`) import prefix** that Webpack allowed (`@import '~bootstrap/...'`); must switch to bare specifiers or use `turbopack.resolveAlias`.
- **`revalidateTag` now requires a second `cacheLife` profile argument** — the single-arg form produces a TypeScript error.
- **Partial Prerendering (PPR) experimental flag/route-segment config removed** (`experimental.ppr`, `experimental_ppr`) — replaced by the stable top-level `cacheComponents` flag, with a materially different underlying model ("PPR in Next.js 16 works differently than in Next.js 15 canaries").
- **`middleware` file/function renamed to `proxy`** — `middleware.ts`/`.js` must be renamed to `proxy.ts`/`.js`, and the exported function renamed from `middleware` to `proxy`. **The Edge runtime is not supported in `proxy`** — `proxy` always runs on the Node.js runtime and this is not configurable; projects that need the Edge runtime must keep using `middleware` (deprecated) for now. Config keys renamed accordingly, e.g. `skipMiddlewareUrlNormalize` → `skipProxyUrlNormalize`.
- **`next/image` changes**: local image sources with query strings now require `images.localPatterns[].search` config (anti-enumeration-attack hardening); `images.minimumCacheTTL` default changed from **60 seconds → 4 hours (14400s)**; `16` removed from the default `images.imageSizes` array; `images.qualities` default changed from "all qualities allowed" to **`[75]` only** (out-of-range `quality` props are coerced to the nearest allowed value); a new `images.dangerouslyAllowLocalIP` flag (default off) blocks local-IP image optimization by default as an SSRF mitigation; `images.maximumRedirects` default changed from unlimited → **3**; `next/legacy/image` is **deprecated**; `images.domains` is **deprecated** in favor of `images.remotePatterns`.
- **Concurrent `dev`/`build`**: `next dev` and `next build` now use **separate output directories** (`next dev` → `.next/dev`), and a lockfile now prevents multiple simultaneous `next dev`/`next build` instances on the same project.
- **Parallel routes now require an explicit `default.js`** in every slot — builds **fail** without one (previously optional).
- **`@next/eslint-plugin-next` defaults to ESLint Flat Config** format.
- **`scroll-behavior: smooth` is no longer auto-overridden** by Next.js during SPA navigations by default; the old auto-override behavior requires opting in via `data-scroll-behavior="smooth"` on `<html>`.
- **`size`/`First Load JS` build-output metrics removed** (see Performance section for rationale).
- **`next dev` no longer double-loads the config file**; a side effect is that checking `process.argv.includes('dev')` inside `next.config.js` now returns `false` during `next dev` (use `NODE_ENV === 'development'` or the `phase` argument instead). `typegen` and `build` remain visible in `process.argv`.
- **Removals**: all AMP support (config, `next/amp`, `useAmp`, per-page `amp` export); the **`next lint` command** (use ESLint/Biome CLI directly — `next build` no longer lints automatically); `serverRuntimeConfig`/`publicRuntimeConfig`; `devIndicators.appIsrStatus`/`buildActivity`/`buildActivityPosition` (the indicator itself remains); `experimental.dynamicIO`/`experimental.useCache` (→ `cacheComponents`); `unstable_rootParams` (→ `next/root-params`).
- **Requirements bump**: minimum **Node.js 20.9.0** (Node 18 no longer supported); minimum **TypeScript 5.1.0**.

[Source: https://vercel.com/changelog/next-js-may-2026-security-release] Separately (not a major-version change, but a notable forced-upgrade event): the **May 2026 coordinated security release** effectively required all Next.js 13/14 users to move to 15.5.18+ or 16.2.6+, since 13/14 received no direct patch and "all versions" of 13–14 were listed as affected.

---

## 14. Limitations

[Source: https://nextjs.org/docs/app/guides/static-exports] **Static export (`output: 'export'`) explicitly does not support**: Dynamic Routes with `dynamicParams: true`; Dynamic Routes without `generateStaticParams()`; Route Handlers that rely on the incoming `Request`; `cookies()`; `rewrites`; `redirects`; `headers` config; `proxy.ts`; Incremental Static Regeneration; `next/image`'s default (server-based) loader (a custom loader is required); Draft Mode; Server Actions; Intercepting Routes. Attempting any of these under `next dev` with static export enabled errors the same way as `export const dynamic = 'error'` would.

[Source: https://nextjs.org/docs/app/api-reference/edge] **Edge Runtime explicitly does not support**: native Node.js APIs (e.g. filesystem read/write); calling `require()` directly (ES Modules required instead — `node_modules` packages are usable only if they're pure ESM and avoid native Node APIs); Incremental Static Regeneration; and specific JS features are hard-disabled: `eval`, `new Function(evalString)`, `WebAssembly.compile`, `WebAssembly.instantiate` (a `proxy.ts` `unstable_allowDynamic` glob config can selectively relax the eval-detection check for specific files/packages, but execution of a genuinely dynamic-eval statement on the Edge "will throw and cause a runtime error" regardless).

[Source: https://nextjs.org/docs/app/guides/content-security-policy] Nonce-based CSP **forces dynamic rendering for every page using it**: static optimization and ISR are disabled, pages can't be CDN-cached without extra config, and **Partial Prerendering (PPR) is explicitly incompatible with nonce-based CSP** "since static shell scripts won't have access to the nonce." The documented alternative, SRI-based CSP, is **experimental** and **App Router only**, cannot handle dynamically generated scripts, and "may change or be removed."

[Source: https://nextjs.org/docs/app/guides/testing] Async Server Components are "new to the React ecosystem," and "some [testing] tools do not fully support them" — an ecosystem-level limitation the docs explicitly flag, recommending E2E over unit testing for async components as a workaround.

[Source: https://nextjs.org/docs/app/guides/upgrading/version-16] The Edge runtime is unavailable in `proxy.ts` (v16+) — projects that specifically need Edge-runtime middleware must stay on the deprecated `middleware.ts` convention "for now," pending "further edge runtime instructions" the docs say will follow "in a minor release." This is a currently-open gap, not a resolved feature.

[Source: https://nextjs.org/docs/app/api-reference/config/next-config-js] `unstable_getResponseFromNextConfig()` (config unit-testing helper) is explicitly caveated: it "only considers `next.config.js` fields and does not consider proxy or filesystem routes, so the result in production may be different than the unit test" — a documented fidelity gap in the official testing tool itself.

---

## 15. Debugging

[Source: https://nextjs.org/docs/app/guides/debugging] Officially documented debugging tooling, all attach to standard Node.js/browser debug protocols ("Any debugger that can attach to Node.js can also be used"):

- **VS Code**: a documented `.vscode/launch.json` template with four configurations — "Next.js: debug server-side" (`node-terminal`, runs `npm run dev -- --inspect`), "Next.js: debug client-side" (Chrome), "Next.js: debug client-side (Firefox)" (requires the Firefox Debugger extension), and "Next.js: debug full stack" (`node`, launches `next` directly with `--inspect`, auto-opens a browser via `serverReadyAction`, configurable `debugWithEdge`/`debugWithChrome`). Monorepo/Turborepo setups need an added `"cwd"` field.
- **JetBrains WebStorm**: a `JavaScript Debug` run configuration pointed at `http://localhost:3000`.
- **Browser DevTools (Chrome/Firefox)**: client-side debugging via the Sources/Debugger tab, `debugger` statements, or manual breakpoints (source paths appear under `webpack://_N_E/./`). **React Developer Tools** browser extension is recommended for component/props/state inspection and perf issues.
- **Server-side debugging via `--inspect`**: `next dev --inspect` (or `NODE_OPTIONS=--inspect-brk next dev` for break-on-start) exposes a Node inspector; connect via `chrome://inspect` (Chrome) or `about:debugging` (Firefox). `--inspect=0.0.0.0` is documented specifically for remote/containerized debugging.
- **Error-overlay-to-DevTools bridge**: the Next.js dev error overlay shows a Node.js icon (under the version indicator) that copies a DevTools inspector URL to the clipboard for jumping straight into the failing server process.
- **Windows-specific note**: the docs explicitly recommend disabling Windows Defender for the project during development, citing reported major Fast Refresh slowdowns from per-file-read scanning — flagged as "a known issue, not related to Next.js" but one that "does affect Next.js development."

[Source: https://nextjs.org/docs/app/getting-started/caching] Framework-native debugging aid distinct from IDE tooling: the **dev overlay** surfaces specific "insights" when Cache Components rules are violated during prerendering — named examples include **blocking-route**, **blocking-prerender-random**, **blocking-prerender-current-time**, and **blocking-prerender-crypto** — each insight links to a fix walkthrough (e.g. "wrap in Suspense," "add `use cache`," "call `connection()`").

[Source: https://nextjs.org/blog/next-16-3] **[New in 16.3]** Two purpose-built DevTools panels for the new caching/navigation model: **Instant Insights** (auto-surfaces navigations that aren't instant) and the **Navigation Inspector** (lets a developer pause a navigation at its loading shell to see exactly what content the user would see, useful because Next.js disables prefetching in development by default, making shell content otherwise hard to inspect).

---

## 16. Integration

[Source: https://nextjs.org/docs/app/guides] The Guides index lists 60+ integration/use-case guides; confirmed titles relevant to "adjacent tooling" integration include: Analytics, Authentication, Authentication with Cache Components, Content Security Policy, CSS-in-JS, Data Security, Environment Variables, Forms, Internationalization, JSON-LD, MDX, Multi-tenant, Multi-zones, OpenTelemetry, Sass, Scripts (third-party script loading), Self-Hosting, Tailwind CSS v3, Third Party Libraries.

[Source: https://nextjs.org/docs/app/guides/authentication] **Auth library integrations** — Next.js documents that it does *not* mandate a specific auth solution but lists these under "Auth Libraries" as Next.js-compatible: **Auth0, Better Auth, Clerk, Descope, Kinde, Logto, NextAuth.js (Auth.js), Ory, Stack Auth, Supabase, Stytch, WorkOS**, plus **session-management-only** libraries **Iron Session** and **Jose**. All are external links from the official docs, not deep first-party integrations, and the docs explicitly recommend using one of these "for increased security and simplicity" over a hand-rolled scheme.

[Source: https://nextjs.org/docs/app/guides/instrumentation] **OpenTelemetry integration**: an `instrumentation.ts`/`.js` file at the project root (or inside `src/`) exporting a `register()` function that runs once per new server instance before it handles requests. The officially shown example uses `@vercel/otel`'s `registerOTel('next-app')`. `NEXT_RUNTIME` env var (`'nodejs'` | `'edge'`) lets `register()` conditionally import runtime-specific instrumentation code, since `register()` runs in **all** environments including Edge.

[Source: https://nextjs.org/docs/app/guides/content-security-policy] **Third-party script integration example**: `@next/third-parties/google`'s `<GoogleTagManager>` component accepting a `nonce` prop read from the request-scoped `x-nonce` header — shown as the canonical pattern for combining CSP nonces with third-party scripts.

[Source: https://nextjs.org/docs/app/getting-started/deploying] **Platform integrations**: verified adapters (Vercel, Bun) vs. unverified-but-documented platform integrations (Cloudflare, Netlify, Appwrite Sites, AWS Amplify Hosting, Deno Deploy, Firebase App Hosting) — see Section 10 for detail.

[Source: https://nextjs.org/docs/app/getting-started/installation] **Linter integration**: first-class support for **either ESLint or Biome** as of the current defaults (`create-next-app` prompts for a choice); `next build` **no longer runs linting automatically as of Next.js 16** — linting must be invoked via package.json scripts (`eslint` / `biome check`).

[Source: https://nextjs.org/docs/app/guides/testing] **Test-runner integrations**: official first-party setup guides for Jest, Vitest, Cypress, and Playwright (see Section 9).

[Source: https://nextjs.org/docs/app/guides] **TypeScript 7 integration** (new, 16.3): `next build` can delegate type-checking to a locally installed `typescript@^7` via the `useTypeScriptCli` config for faster builds — see Performance.

---

## 17. Production Considerations

[Source: https://nextjs.org/docs/app/guides/production-checklist] Official production-readiness recommendations grouped by theme:
- **Routing/rendering**: use layouts for partial rendering on navigation; handle 404s and catch-all errors with custom pages; be deliberate about `"use client"` boundary placement; be aware that Request-time APIs (`cookies`, `searchParams`) can opt an entire route — or, if used in the Root Layout, the **entire application** — into Dynamic Rendering unless wrapped in `<Suspense>`.
- **Data fetching/caching**: prefer Server Components for data fetching; use Route Handlers to expose data to Client Components but **avoid calling Route Handlers from Server Components** (an unnecessary extra server hop); use Loading UI/Suspense for streaming; fetch in parallel where possible; verify caching status of non-`fetch` data requests (wrap with `unstable_cache` where relevant in the previous caching model).
- **UI/accessibility**: use Server Actions for form handling/validation; add `app/global-error.tsx` and `app/global-not-found.tsx`; use the Font Module, `<Image>`, and `<Script>` components for automatic optimization; use `eslint-plugin-jsx-a11y` (built-in) to catch accessibility issues.
- **Security**: apply tainting for sensitive server data; re-verify auth/authorization inside every Server Action (not layout/page-level alone); move DB access into a `server-only` DAL; consider rate limiting for expensive operations; ensure `.env.*` files are gitignored and only `NEXT_PUBLIC_`-prefixed vars are exposed to the client; consider a CSP.
- **SEO/metadata**: use the Metadata API, generate Open Graph images, and generate sitemaps/robots files.
- **Type safety**: use TypeScript plus the built-in TypeScript plugin/type checker.

[Source: https://nextjs.org/docs/app/guides/self-hosting] Self-hosting is a distinct documented concern from generic Node/Docker deployment — referenced by multiple pages (e.g., the Server Actions encryption-key section explicitly points self-hosted multi-instance deployers to the Self-Hosting guide's "Server functions encryption key" section, and the Caching page points there for "configuring the server cache" / "Caching and ISR"). [Unresolved: the Self-Hosting guide's full content was not independently fetched in this research pass — only cross-references from other pages were captured. Do not assume specifics of self-hosting configuration beyond what's cited elsewhere in this document (the `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` env var, and the general Node.js/Docker deployment paths in Section 10).]

[Source: https://nextjs.org/support-policy] Production version-support guidance: run either the current **Active LTS** or a still-supported **Maintenance LTS** major version; Maintenance LTS majors get security/critical-fix coverage for **2 years** post-release, after which they fall outside the documented support window (with only "rare exception" patches possible).

[Source: https://vercel.com/changelog/next-js-may-2026-security-release] Operationally, the vendor runs **coordinated, advance-notice security releases** — "roughly once a month, advance notice of upcoming security releases is published on the Next.js blog, with each announcement including the expected release timeline and highest anticipated severity" [as summarized from https://nextjs.org/blog/next-security-release-program in WebSearch results; the dedicated program page itself was not independently fetched in full — treat the "roughly once a month" cadence claim as **Unresolved: sourced from a search-engine summary of an official blog post, not a direct fetch of that post**]. Production operators should therefore treat prompt patch application as a standing operational requirement, not a one-time upgrade task.

[Source: https://nextjs.org/docs/app/guides/production-checklist] The docs frame "before going to production" as materially different from "during development": run a real `next build && next start` locally, not just `next dev`, before shipping — since dev-mode behavior (e.g., disabled prefetching, different caching) does not represent production performance.

---

## Summary of Sources Consulted

All sources below are official — either `nextjs.org` documentation/blog pages or the Vercel changelog for Next.js security releases (Vercel is the maintaining organization). No blog, forum, or community source was used as a primary citation; where a `WebSearch` result summary (rather than a direct page fetch) was the only available source for a claim, that claim is explicitly flagged inline as sourced from a search summary rather than a direct fetch.

## Unresolved Items (consolidated)

1. The exact CVE identifier(s) and advisory detail for the **August 2026** Next.js security release (16.3.3 / 15.5.24, "two critical severity vulnerabilities") — only a WebSearch summary was obtained, the dedicated advisory page was not fetched.
2. The "roughly once a month" security-release cadence claim is sourced from a WebSearch summary of `nextjs.org/blog/next-security-release-program`, not a direct fetch of that page.
3. Full content of the three dedicated Migration guides (App Router migration, CRA→Next.js, Vite→Next.js) — only titles/descriptions from the index page were confirmed.
4. Full content of the Self-Hosting guide (`/docs/app/guides/self-hosting`) — only cross-references from other pages were captured, not the page itself.
5. Whether Next.js documents first-party mocking utilities for Server Actions/Route Handlers/App Router request context beyond the experimental `next.config.js`-testing helper — no direct evidence found either way in pages fetched.
6. The precise mechanics of the "previous" (non-Cache-Components) caching model (`caching-without-cache-components` guide) were not independently fetched; this document relies on other pages' references to it rather than its own content.
7. Whether `nextjs.org/docs` has moved hosts recently: **no evidence of a move was found** — all fetched pages resolved normally at `nextjs.org/docs/...` on the research date, and the docs explicitly describe being additionally mirrored inside `node_modules/next/dist/docs/` per-install (a distribution mechanism, not a canonical-host change).
