# Nuxt — Deep Technology Research

Research date: 2026-09-09. Primary source: official documentation at
**https://nuxt.com/docs/** (the canonical docs host). The docs are
version-scoped in the URL path (`/docs/4.x/...` for the current stable
major, `/docs/3.x/...` for the prior major). Where a claim is
version-specific it is tagged explicitly. All claims are cited inline;
anything not found in official sources is marked "Not documented / could
not verify" rather than guessed.

## Canonical docs host

[Source: https://nuxt.com/docs/4.x/getting-started/introduction] Nuxt's
official documentation is hosted at **nuxt.com/docs**, with version-specific
paths (e.g., `4.x`, `3.x`). There is no evidence found during this research
that the docs host has moved recently — `nuxt.com` appears to be the
long-standing canonical host. [Source:
https://nuxt.com/docs/4.x/community/roadmap] The docs also reference a
"nightly release channel" for pre-release testing, and an in-development
Nuxt 5 documented under the same `nuxt.com` domain (version path not yet
confirmed at research time). Unresolved: whether a distinct `5.x` docs path
already exists at research time was not directly verified.

---

## 1. Core concepts

[Source: https://nuxt.com/docs/4.x/getting-started/introduction] Nuxt
describes its mission as making "web development intuitive and performant
with a great Developer Experience in mind." It is a free, open-source
framework built on top of **Vue.js**.

[Source: https://nuxt.com/docs/4.x/getting-started/introduction] Nuxt lets
developers "start writing `.vue` files from the beginning while enjoying
hot module replacement in development and a performant application in
production with server-side rendering by default." It emphasizes vendor
independence — deployable "everywhere, even on the edge."

[Source: https://nuxt.com/docs/4.x/getting-started/introduction] Key
documented features:
- File-based routing from the `app/pages/` directory.
- Automatic code-splitting to reduce initial load.
- Built-in server-side rendering (SSR) without manual configuration.
- Auto-imports for components and composables.
- Zero-config TypeScript support.
- A server engine (**Nitro**) that generates API routes from `server/api/`
  and enables deployment across Node.js, serverless, and edge runtimes.

[Source: https://nuxt.com/docs/4.x/getting-started/introduction] Documented
benefits of SSR-by-default: faster initial page load, improved SEO
indexing, reduced client-side processing for low-powered devices, better
accessibility, and easier server-side caching.

[Source: https://nuxt.com/docs/4.x/guide/concepts/rendering] Nuxt's
rendering model is built around three modes — **Universal Rendering**
(SSR + hydration, the default), **Client-Side Rendering** (`ssr: false`),
and **Hybrid Rendering** (per-route rules). See Section 2/8 for detail.

[Source: https://nuxt.com/docs/4.x/guide/concepts/auto-imports] **Auto-imports**
are a foundational concept: components (`app/components/`), composables
(`app/composables/`), and utilities (`app/utils/`) are made available
throughout the app without explicit `import` statements, alongside Vue's
own reactivity APIs and Nuxt-specific composables. The mechanism preserves
typings and IDE completions, and only includes what is actually used in
production code (tree-shaken). Auto-imports are exposed under a `#imports`
alias for cases where an explicit import is preferred.

[Source: https://nuxt.com/docs/4.x/guide/concepts/server-engine] **Nitro**
is "a dedicated server engine" built to power Nuxt, providing cross-platform
support (Node.js, browsers, service workers, and more), serverless-readiness
out of the box, automatic code-splitting, a standalone `.output` server
distribution independent of `node_modules`, and a global `$fetch` helper
that short-circuits network calls when running server-side. The docs
describe this combination as making Nuxt "a hybrid framework for the
JAMstack."

[Source: https://nuxt.com/docs/4.x/guide/going-further/modules] **Modules**
are the primary extension mechanism: functions that run sequentially during
`nuxt dev`/`nuxt build`, letting third parties hook into config and Nuxt's
hook system to add plugins, components, composables, and server routes as
publishable npm packages, without modifying Nuxt core.

[Source: https://nuxt.com/docs/4.x/guide/going-further/layers] **Layers**
let a project "share and reuse partial Nuxt applications" from a monorepo,
git repository, or npm package — a distinct concept from modules, aimed at
sharing whole directory structures/config rather than packaged
functionality.

## 2. Architecture

[Source: https://nuxt.com/docs/4.x/guide/directory-structure] [VERSION-SENSITIVE:
Nuxt 4.x] The default project layout centers on an **`app/`** directory as
"the main directory of the Nuxt application," holding components, layouts,
pages, composables, middleware, plugins, and assets. Alongside it at the
project root: **`server/`** (Nitro backend code), **`public/`** (static
files served verbatim), **`shared/`** (code usable in both the Vue app and
the Nitro server), **`test/`** (recommended location for unit/Nuxt-runtime/e2e
tests), **`modules/`** (local Nuxt modules), **`layers/`** (shared/reusable
partial apps), plus root files `nuxt.config.ts`, `.nuxtrc`, and
`.nuxtignore`. The **`content/`** directory is enabled specifically by the
(separate) Nuxt Content module.

[Source: https://nuxt.com/docs/4.x/getting-started/upgrade]
[VERSION-SENSITIVE: this app/ layout is new as of Nuxt 4; Nuxt 3 used the
project root itself as the default `srcDir`.] In Nuxt 3, `assets/`,
`components/`, `composables/`, `layouts/`, `middleware/`, `pages/`, `app.vue`,
`app.config.ts`, `error.vue`, and `plugins/` lived at the project root. In
Nuxt 4, `srcDir` defaults to `app/`, and the `~` alias points to `app/`
instead of the project root. Old-structure projects are still
auto-detected, but the docs recommend migrating for performance and IDE
type-safety benefits.

[Source: https://nuxt.com/docs/4.x/guide/directory-structure/nuxt] The
**`.nuxt/`** directory is a development-only, auto-regenerated build
directory (Vue app assembly, generated type/config files); it should be
git-ignored and not manually edited. Its generated contents can be
inspected via Nuxt DevTools' "Virtual Files" tab.

[Source: https://nuxt.com/docs/4.x/guide/directory-structure/server]
**`server/`** subdirectories: `server/api/` (routes auto-prefixed with
`/api`, e.g. `hello.ts` → `/api/hello`), `server/routes/` (routes without
the `/api` prefix), `server/middleware/` (request handlers run before
routes; inspect/extend requests, don't return a response), `server/plugins/`
(Nitro lifecycle plugins), and `server/utils/` (shared server helper
functions). All handlers use `defineEventHandler()`/`eventHandler()`;
filenames support dynamic segments (`[name].ts`) and HTTP-method suffixes
(`.get`, `.post`, `.put`, `.delete`, etc.).

[Source: https://nuxt.com/docs/4.x/guide/concepts/nuxt-lifecycle] Nuxt's
**application lifecycle** runs in two phases:
- **Server**: server plugins run once at startup (init Nitro, register
  hooks) → server middleware runs per-request → app plugins load the
  Vue/Nuxt instance (`app:created` hook) → route `validate` (from
  `definePageMeta`) → app (route) middleware → page/component render with
  data fetching (`useFetch`/`useAsyncData`) → HTML is generated
  (`app:rendered`, `render:html` hooks).
- **Client**: client-only plugins (`.client` suffix) load → route
  re-validation → app middleware re-runs → the Vue app mounts and hydrates
  onto the server-rendered DOM (`app:beforeMount`, `app:mounted` hooks) →
  normal Vue component lifecycle (`onMounted`, etc.) proceeds. The docs
  state this two-phase design exists to keep "consistency between the data
  on the server and the client" and avoid hydration errors.

[Source: https://nuxt.com/docs/4.x/guide/going-further/layers] Layer
**resolution priority**: your own project files first, then layers
auto-scanned from `~~/layers` (sorted alphabetically, Z overriding A), then
layers listed under `extends` (first-listed having highest priority among
extends). Each layer is structured like a normal Nuxt app and requires its
own `nuxt.config.ts`; components/composables/layouts/middleware/pages/
plugins/utils/server endpoints/app config are auto-scanned and merged.
Documented limitation: dependencies of a remote layer are isolated under
`node_modules/.c12/layer_name/node_modules/`, invisible to the consuming
project's own package manager/tools (e.g., ESLint can't see them); global
aliases (`~/`, `@/`) inside a layer resolve against the *consumer* project,
not the layer itself, so layers should use relative paths or named aliases.

[Source: https://nuxt.com/docs/4.x/guide/going-further/modules] Modules
integrate at build/dev start via Nuxt's hook system and `@nuxt/kit` utility
functions, letting them add plugins, components, composables, and server
routes; they are typically published to npm as independent, reusable
packages.

## 3. APIs

[Source: https://nuxt.com/docs/4.x/api] The official API Reference is
organized into: **Components** (built-in components — pages/layouts/head
management, e.g. `<ClientOnly>`), **Composables** (data-fetching, head
management, etc., e.g. `useAppConfig`), **Utils** (navigation, error
handling, etc., e.g. `$fetch`), **Commands** (Nuxt CLI — init, analyze,
build, dev, preview...), and **Advanced** (framework internals such as
lifecycle hooks), plus dedicated references for **Nuxt Kit** (module
authoring) and **Nuxt Configuration**.

[Source: https://nuxt.com/docs/4.x/getting-started/data-fetching] **Data
fetching composables**:
- **`$fetch`** — the foundational request utility; simplest, but not
  SSR-duplicate-safe on its own.
- **`useFetch`** — an SSR-safe wrapper around `$fetch`; "fetches data only
  once in universal rendering," avoiding duplicate server+client requests
  by serializing server-fetched data into the payload (accessible via
  `useNuxtApp().payload`).
- **`useAsyncData`** — more fine-grained control than `useFetch`; wraps
  arbitrary async logic, suited to third-party SDKs/custom query layers.
- **`useLazyFetch`** / **`useLazyAsyncData`** — lazy variants that don't
  block navigation.
- Key shared options: `lazy`, `server` (set `false` for client-only),
  `pick` (select payload fields to shrink payload size), `watch` (re-run on
  reactive dependency change), `immediate` (default `true`).
- Calls sharing the same **key** share underlying refs; handler function,
  transform, and deep-watch settings must match across such calls, while
  `server`, `lazy`, and `immediate` may differ. `refresh`/`execute` trigger
  manual re-fetch.
- Documented anti-pattern: don't call `$fetch` alone inside `setup()` for
  initial data — "It is recommended to use `$fetch` for client-side
  interactions (event-based) or combined with `useAsyncData`."

[Source: https://nuxt.com/docs/4.x/getting-started/state-management]
**`useState(key, init?)`** is documented as "an SSR-friendly `ref`
replacement" for cross-component shared state, keyed and payload-serialized.
State must be JSON-serializable (no classes/functions/symbols). Anti-pattern
called out explicitly: defining reactive state as a top-level module export
(e.g. `export const myState = ref({})`) creates state shared across
*all* server requests, risking cross-request leakage; wrap state instead in
a composable like `const useX = () => useState('x')`.

[Source: https://nuxt.com/docs/4.x/getting-started/state-management] For
larger apps, **Pinia** is called out as "the official Vue recommendation"
for state management, installable via `npx nuxt module add pinia`. Nuxt
otherwise remains unopinionated about state libraries, and mentions Harlem
(immutable state) and XState (state machines) as alternatives.

[Source: https://nuxt.com/docs/4.x/getting-started/error-handling]
**Error-handling APIs**: `useError()` (reactive ref to the current
global error), `createError({ statusCode, message, fatal, ... })` (throws a
full-screen error page server-side; throws a non-fatal error client-side
unless `fatal: true`), `showError()` (docs recommend `throw createError()`
instead where possible), `clearError()` (clears error state, optionally
redirects). Error page customization via an `error.vue` file alongside
`app.vue`. The `<NuxtErrorBoundary>` component catches errors within its
default slot without tearing down the whole page, rendering an `#error`
slot instead. Documented error sources: Vue rendering lifecycle errors,
app startup/plugin/hook errors, Nitro server errors, and JS chunk-loading
failures (e.g., after a redeploy).

[Source: https://nuxt.com/docs/4.x/guide/concepts/rendering] **Route Rules**
API (`routeRules` in `nuxt.config.ts`), keyed by route glob, supporting:
`redirect`, `ssr` (bool), `cors` (bool), `headers` (object), `swr`
(number|bool — stale-while-revalidate), `isr` (number|bool — incremental
static regeneration, for platforms like Netlify/Vercel), `prerender`
(bool), `noScripts` (bool), and `appMiddleware` (string|string[]|Record —
controls which app middleware runs for matching routes).

[Source: https://nuxt.com/docs/4.x/guide/going-further/debugging] **Debugging
tooling**: `nuxt dev --inspect` launches the Node inspector (documented
limitation: "The Node.js and Chrome processes need to be run on the same
platform. This doesn't work inside of Docker."); sourcemaps default on for
server builds and client dev, configurable via `sourcemap: { server, client }`.

[Source: https://nuxt.com/docs/4.x/guide/directory-structure/server]
**`defineEventHandler()`** (Nitro/H3) is the core server-route API;
handlers receive an `event` object and can return plain objects
(auto-JSON-serialized).

## 4. Configuration

[Source: https://nuxt.com/docs/4.x/api/nuxt-config] Central config file is
**`nuxt.config.ts`**, authored via `defineNuxtConfig({...})`. Major
documented top-level keys: `alias` (custom path aliases), `app` (baseURL,
CDN URL, head defaults, page transitions, root element), `build` (bundle
analysis, transpilation, template generation), `builder` (bundler choice:
Vite [default], webpack, Rspack, or custom), `components` (auto-registration
of components, default-scans `~/components`), `css` (global stylesheets —
CSS/SCSS/Sass etc., loaded on every page), `debug` (verbose hook
name/timing/argument logging), `dir` (override default directory names),
`modules` (array of Nuxt modules, loaded in order — config-declared first,
then `~/modules/`), `nitro` (Nitro/server runtime config, including
`preset`), `pages` (enable/disable vue-router integration; glob patterns
for route generation), `plugins` (auto-loaded from `~/plugins/`, with
client-only/server-only variants), `runtimeConfig` (env-driven config;
private keys server-only, `public` keys exposed to the client),
`ssr` (toggle SSR vs. SPA/static), `typescript` (strict mode,
build-time type-checking, tsconfig customization), `vite`
(pass-through Vite config, with `$client`/`$server` environment
overrides), and `vue` (Vue compiler options, runtime-compiler inclusion,
asset URL transforms).

[Source: https://nuxt.com/docs/4.x/guide/going-further/experimental-features]
An **`experimental`** config namespace exposes many opt-in features,
including (non-exhaustive; enable via `experimental: { featureName: true }`
in `nuxt.config.ts`): `alwaysRunFetchOnKeyChange`, `extractAsyncDataHandlers`,
`restoreState`, `sharedPrerenderData`, `purgeCachedData`,
`granularCachedData`, `ssrStreaming`, `viewTransition`, `navigationRepaint`,
`headNext`, `typedPages`, `inlineRouteRules`, `early404`, `componentIslands`,
`normalizeComponentNames`/`normalizePageNames`, `asyncContext`, `decorators`,
`typescriptPlugin`.

[Source: https://nuxt.com/docs/4.x/getting-started/upgrade] A **`future`**
config namespace exists for staged opt-in to next-major behavior — e.g.
`future.compatibilityVersion: 5` opts a Nuxt 4.2+ project into (documented
as of research date) Nuxt 5 behaviors: Vite Environment API, case-sensitive
routing, normalized page names, comment-node placeholders for client-only
components, Vue Options API disabled by default, typed pages enabled by
default, and stricter TypeScript imports. [VERSION-SENSITIVE: requires
Nuxt 4.2+; Nuxt 5 itself was not yet released as stable at research time —
see Section 12.]

[Source: https://nuxt.com/docs/4.x/guide/concepts/auto-imports] Auto-import
behavior is configurable: `imports: { autoImport: false }` disables
auto-imports entirely; `imports: { scan: false }` disables scanning of
custom project code while keeping framework auto-imports (documented
caveat: this "breaks the layer system's override feature"). Component
auto-registration can be disabled by setting `components.dirs` to `[]`.

[Source: https://nuxt.com/docs/4.x/getting-started/deployment] Deployment
preset is configurable via `nitro: { preset: 'node-server' }` in
`nuxt.config.ts` or the `NITRO_PRESET` environment variable at build time.

[Source: https://nuxt.com/docs/4.x/getting-started/deployment] Runtime
environment variables recognized by the Node server output: `NITRO_PORT` /
`PORT` (default 3000), `NITRO_HOST` / `HOST` (default `0.0.0.0`),
`NITRO_SSL_CERT` / `NITRO_SSL_KEY` (HTTPS — docs recommend only behind a
reverse proxy), and `NUXT_APP_BASE_URL` / `app.baseURL` for subpath
deployments.

## 5. Recommended patterns

[Source: https://nuxt.com/docs/4.x/getting-started/data-fetching] Use
`useFetch`/`useAsyncData` for initial component data (SSR-safe, dedupes
server/client fetches); reserve raw `$fetch` for client-side, event-driven
calls.

[Source: https://nuxt.com/docs/4.x/getting-started/state-management] Wrap
shared state in a composable (`const useX = () => useState('x', () => ...)`)
rather than exporting a bare module-level `ref`.

[Source: https://nuxt.com/docs/4.x/guide/best-practices/plugins] "Whenever
possible, favor composition over plugins" — many utilities are better
implemented as composables than as plugins, since plugins run during
hydration and a large number of expensive plugins directly hurts render
performance. For unavoidable async plugins, set `parallel: true` so they
load concurrently rather than blocking sequentially.

[Source: https://nuxt.com/docs/4.x/guide/best-practices/performance]
Recommended performance patterns: prefix components `Lazy` for dynamic
import; audit `package.json` for unused dependencies; use `nuxi analyze` to
inspect the production bundle; use `hydrate-on-visible` for lazy hydration
of non-critical components [VERSION-SENSITIVE: available Nuxt v3.16+]; use
`<NuxtImg>`/Nuxt Image for responsive, format-converted, lazy-loaded
images, marking above-the-fold images `fetchPriority="high"`/`loading="eager"`
and below-fold ones `loading="lazy"`/`fetchpriority="low"`; rely on
`<NuxtLink>`'s automatic viewport-based prefetching; use Nuxt Fonts for
self-hosted, layout-shift-minimizing font loading.

[Source: https://nuxt.com/docs/4.x/guide/concepts/typescript] Recommended
TypeScript pattern: don't hand-edit the generated `.nuxt/tsconfig*.json`
files — extend/override TypeScript settings via `nuxt.config.ts`'s
`typescript` key instead, and enable `typescript.typeCheck: true` (with
`vue-tsc`/`typescript` installed) or run `npx nuxt typecheck` for CI-time
checking, since type-checking is off by default for dev/build performance.

[Source: https://nuxt.com/docs/4.x/getting-started/error-handling]
Recommended pattern: use `onErrorCaptured` in component setup, the
`vue:error` Nuxt hook in plugins for global handling, and
`<NuxtErrorBoundary>` for localized/non-fatal error containment rather than
tearing down the whole page.

## 6. Anti-patterns

[Source: https://nuxt.com/docs/4.x/getting-started/data-fetching] Calling
`$fetch` directly inside a component's `setup()` for initial data can cause
the fetch to run twice (once server-side during SSR, once again client-side
during hydration) — use `useFetch`/`useAsyncData` instead. Related caveat:
triggering Pinia store actions from inside `useAsyncData` can cause
unintended repeated executions.

[Source: https://nuxt.com/docs/4.x/getting-started/state-management]
Defining reactive state as a top-level exported `ref`/`reactive` (outside a
composable/`useState`) is called out as creating state shared across all
server requests — a correctness and memory-leak risk in SSR.

[Source: https://nuxt.com/docs/4.x/guide/best-practices/plugins] Overusing
plugins — especially ones with expensive initialization — is called out as
a documented anti-pattern that harms rendering performance; prefer
composables.

[Source: https://nuxt.com/docs/4.x/guide/best-practices/performance]
Documented performance anti-patterns: trying to load everything at once
instead of progressive enhancement; neglecting Vue-level optimizations
(`shallowRef`, `v-memo`, `v-once`) in favor of only Nuxt-level ones;
inconsistent team coding patterns undermining performance stability.

[Source: https://nuxt.com/docs/4.x/guide/concepts/auto-imports] Calling
composables that require Nuxt context (most built-ins) outside a valid
context — plugin, route middleware, or component `setup()` — throws "Nuxt
instance is unavailable"; e.g. calling them inside an async callback after
an `await` can lose context.

[Source: https://nuxt.com/docs/4.x/blog/v4-5-security via
https://nuxt.com/blog/v4-5-security] Passing untrusted/undeclared props
into server-island components with polymorphic ("as"-style) root elements
is a documented security anti-pattern (see Section 7) — islands should
explicitly declare accepted props or set `inheritAttrs: false`.

Not documented / could not verify: a single consolidated "Anti-Patterns"
doc page was not found; the anti-patterns above are drawn from statements
embedded across the Data Fetching, State Management, Plugins, and
Performance best-practice pages, plus the v4.5 security advisory.

## 7. Security

[Source: https://nuxt.com/blog/v4-5-security] Nuxt publishes security fixes
via dedicated blog posts and GitHub Security Advisories (GHSA IDs). The
July 2026 patch release (**Nuxt 4.5.1** / **3.21.10**, plus
**@nuxt/devtools 3.3.1**) fixed eight advisories, summarized here as a
concrete, version-tagged example of Nuxt's security surface and process:

1. **GHSA-9473-5f9j-94wq** (High) — Server-side RCE via server-island
   props when `vue.runtimeCompiler` is enabled (off by default) combined
   with dynamic component resolution; attacker-controlled template keys in
   island props could execute arbitrary code in the Nitro process.
2. **GHSA-48hr-524c-v5w3** (Medium) — Unauthorized component instantiation:
   server islands forwarding undeclared props onto a polymorphic root
   element let attackers pass arbitrary HTML elements/component names.
3. **GHSA-hxvh-4h3w-prp9** (High) — Route-rule authorization bypass: case
   -insensitive routing let uppercase-cased `routeRules`/`appMiddleware`
   auth checks be bypassed; noted as a regression from an earlier patch
   (CVE-2026-53721).
4. **GHSA-hxcr-hm88-mpq6** / **GHSA-9pgf-384g-p7mv** (High) — Denial of
   service against apps using server components/islands via the
   `/__nuxt_island` endpoint: unauthenticated requests could crash the
   server via `v-for` expansion over a prop or oversized request bodies.
5. **GHSA-wm8w-6qjm-cv43** (High) — Cross-user payload disclosure:
   [VERSION-SENSITIVE: Nuxt 4.4.0+] apps using `cache`, `swr`, or `isr`
   route rules on authenticated pages could serve a cached `_payload.json`
   response to a different user; remediation requires purging CDN/edge
   caches after upgrading, not just upgrading the package.
6. **GHSA-7c4v-fwgw-9rf7** (Low) — Dev server path disclosure: a dev server
   bound to a network interface on an untrusted network exposed a Chrome
   DevTools endpoint leaking the project path and workspace UUID.
7. **GHSA-279x-mwfv-vcqv** (Critical, development-only) — Nuxt DevTools RCE:
   an unauthenticated RPC method exposed over the Vite HMR socket during
   `nuxt dev` (with DevTools enabled) allowed arbitrary command execution;
   explicitly does not affect production deployments.

[Source: https://nuxt.com/blog/v4-5-security] Official remediation guidance:
run `npx nuxt upgrade --dedupe`; confirm the lockfile pulls
`@nuxt/devtools@3.3.1`; purge upstream CDN/edge caches for previously
cached authenticated pages; explicitly declare island props or set
`inheritAttrs: false`; set `router.options.sensitive: true` if
case-sensitive route matching is intentionally relied upon for
authorization.

[Source: https://nuxt.com/modules/security] A **security-headers module**
("nuxt-security," OWASP Top 10/Helmet-based — CSP, rate limiting, XSS
protection, CORS, X-Powered-By removal, optional CSRF protection) is listed
in the official Nuxt Modules directory at nuxt.com/modules/security. This
is a **community-maintained module** (maintainer: Baroshem, ~30
contributors), not an official Nuxt-team package — flagged here explicitly
since it is easy to mistake for core-team-maintained given its prominent
listing on nuxt.com.

Not documented / could not verify: a single consolidated, general-purpose
"Security" guide page (equivalent to, e.g., Express's security best
practices doc) was not located on nuxt.com/docs during this research pass;
Nuxt's official security content found is advisory/patch-note-driven
(GHSA-tagged blog posts) rather than a standing best-practices page.

## 8. Performance

[Source: https://nuxt.com/docs/4.x/guide/best-practices/performance]
Documented performance guidance (see Section 5 for the recommended-pattern
framing) covers: lazy-loading components (`Lazy` prefix), dependency/bundle
auditing, `nuxi analyze` for bundle visualization, progressive
enhancement, lazy hydration via `hydrate-on-visible`
[VERSION-SENSITIVE: v3.16+], Nuxt Image for responsive/optimized images
with priority hints, `<NuxtLink>`'s automatic prefetch-on-visibility, Nuxt
Fonts for self-hosted fonts with fallback-metric generation to reduce CLS,
and `useFetch`/`useAsyncData` to avoid duplicate SSR/client requests.
Documented profiling tools: **Nuxi Analyze**, **Nuxt DevTools**, Chrome
DevTools, PageSpeed Insights, Web Page Test.

[Source: https://nuxt.com/docs/4.x/guide/concepts/rendering] Hybrid
rendering (per-route caching via `routeRules`: `swr`, `isr`, `prerender`,
`ssr: false` for specific routes) is documented as a core performance lever
— letting different routes use different rendering/caching strategies
instead of a single app-wide mode. Documented constraint: hybrid
rendering/route rules are unavailable when using the static `nuxt generate`
command output. Route rules deploy natively to Netlify/Vercel platform
rules when detected.

[Source: https://devtools.nuxt.com/guide/features (surfaced via WebSearch,
not independently WebFetched in full during this pass — flagged)] **Nuxt
DevTools** ships a Timeline (component render/update/init timing), Assets
panel (raw file sizes), Render Tree, and a Hooks tab (time spent per hook,
client/server, listener counts) for performance diagnosis. Unresolved:
this page was located via search-result summary rather than a direct
WebFetch read during this research pass, so treat the specific feature list
as lower-confidence pending direct verification.

[Source: https://nuxt.com/docs/4.x/getting-started/upgrade] Nuxt 4.5
introduced **experimental SSR streaming** (`experimental.ssrStreaming`) to
improve Time to First Byte. [VERSION-SENSITIVE: Nuxt 4.5.0+, experimental.]

## 9. Testing

[Source: https://nuxt.com/docs/4.x/getting-started/testing] Official
testing support is provided by **`@nuxt/test-utils`**, described as "a
library of test utilities and configuration that currently powers the
tests we use on Nuxt itself."

**Unit testing**: Vitest-only for the Nuxt runtime environment; configured
via `vitest.config.ts` using `defineVitestProject`. Recommended layout:
tests in `test/nuxt/` run inside the Nuxt runtime environment; tests in
`test/unit/` run in plain Node for speed. Built-in DOM mocks:
`intersectionObserver` (on by default), `indexedDB` (off by default).
Runtime environment choice between `happy-dom` and `jsdom`, set via
`environmentOptions` in `vitest.config.ts`.

**E2E testing**: supports Vitest, Jest, Cucumber, and Playwright as
runners, via a `setup()` helper that wires up `beforeAll`/`beforeEach`/
`afterEach`/`afterAll`.

**Component/testing helpers**: `mountSuspended` (mount any Vue component
inside the Nuxt environment, with async setup support); `renderSuspended`
(render via Testing Library with Nuxt injections available);
`mockNuxtImport` (mock an auto-import — documented limit: usable once per
mocked import per test file); `mockComponent` (swap in a test-double
component); `registerEndpoint` (stand up a mock Nitro endpoint returning
fixture data); `createPage(url)` (spin up a configured Playwright browser
page). Browser-mode support via `@vitest/browser-playwright` (`page.render()`)
and a first-class Playwright Test integration via
`@nuxt/test-utils/playwright`.

**TypeScript**: tests under `test/nuxt/` or `tests/nuxt/` automatically get
Nuxt path aliases (`~/`, `@/`, `#imports`) and auto-import type awareness.

**Documented constraints**: Nuxt-runtime tests and E2E-style tests cannot
coexist in the same file — separate them by file (e.g. `.nuxt.spec.ts`) or
environment directive; avoid mutating global state within Nuxt-environment
tests.

## 10. Deployment

[Source: https://nuxt.com/docs/4.x/getting-started/deployment] Three
documented deployment shapes: **Node.js server**, **static site
generation**, and **serverless/edge (CDN)**.

**Node.js server**: `nuxt build` emits `.output/server/index.mjs` as the
entry point; run with `NODE_ENV=production node .output/server/index.mjs`.
The docs stress explicitly setting `NODE_ENV=production` to suppress
development-mode warning noise. Runtime env vars: `NITRO_PORT`/`PORT`
(default 3000), `NITRO_HOST`/`HOST` (default `0.0.0.0`),
`NITRO_SSL_CERT`/`NITRO_SSL_KEY` (HTTPS — documented as recommended only
behind a reverse proxy). PM2 process management is documented via an
`ecosystem.config.cjs`, including cluster mode.

**Static hosting**: `nuxt generate` with `ssr: true` (default) pre-renders
routes at build time and emits `/200.html` and `/404.html` fallbacks for
dynamic-route and error handling; with `ssr: false`, output is a bare
`<div id="__nuxt"></div>` SPA shell (loses SEO benefit, works for pure
client apps).

**Presets**: configured via `nitro: { preset: 'node-server' }` in
`nuxt.config.ts` or `NITRO_PRESET=node-server nuxt build`; the full preset
catalog is documented on Nitro's own deployment docs (linked from, but not
duplicated within, the Nuxt deployment page).

**Production notes documented**: on Cloudflare, disable "Rocket Loader™"
and "Email Address Obfuscation" — both are called out as causing script
injection / hydration errors; for subpath deployments, set `app.baseURL`
or the `NUXT_APP_BASE_URL` env var.

[Source: https://nuxt.com/docs/4.x/guide/concepts/rendering] **Edge-Side
Rendering (ESR)** is documented as a deployment target (not a distinct
rendering mode): zero-config on Cloudflare Pages; `NITRO_PRESET=vercel-edge`
for Vercel; `NITRO_PRESET=netlify-edge` for Netlify Edge Functions. ESR
composes with hybrid rendering/route rules and Nitro's Node/Deno/Cloudflare
Workers cross-platform support.

## 11. Migration

[Source: https://nuxt.com/docs/4.x/getting-started/upgrade] **Upgrading to
latest**: `npx nuxt upgrade` (or the yarn/pnpm equivalent); a nightly
release channel exists for testing pre-release builds.

[Source: https://nuxt.com/docs/4.x/getting-started/upgrade]
**Nuxt 3 → Nuxt 4** [VERSION-SENSITIVE], key documented breaking changes:
- **New directory structure** (largest-impact change): create an `app/`
  directory and move `assets/`, `components/`, `composables/`, `layouts/`,
  `middleware/`, `pages/`, `plugins/`, `app.vue`, `app.config.ts`,
  `error.vue` into it; `srcDir` now defaults to `app/`; `~` now points to
  `app/` not the project root. Old layout is still auto-detected but
  migration is recommended for perf/IDE benefits.
- **jiti no longer bundled** (medium impact): `nuxt.config.ts` and modules
  now load via native Node TS/ESM support; requires **Node 22.19+**;
  relative config imports need explicit extensions (`'./plugin'` →
  `'./plugin.ts'`); config files must use only "erasable" TypeScript
  syntax; `jiti` can optionally be installed as a fallback dependency.
- **Vite Environment API migration** (medium impact): environment-specific
  `extendViteConfig()` usage should move to unified Vite plugins using
  `applyToEnvironment()`/`configEnvironment()` hooks; `server`/`client`
  plugin-registration options are deprecated.
- **Data-fetching layer reorganization**: `useAsyncData`/`useFetch` calls
  sharing a key now share refs automatically; `getCachedData` receives a
  context object describing the fetch cause; reactive keys trigger
  automatic refetch; data is cleaned up on unmount.
- **Data reactivity change** (minor impact): `data` returned from
  `useAsyncData`/`useFetch` is now a `shallowRef` (previously `ref`);
  opt into deep reactivity with `{ deep: true }`.
- **Directory scanning**: `middleware/` child folders now scan for `index`
  files, matching existing `plugins/` behavior.
- **TypeScript config splitting** (minor impact): separate
  `.nuxt/tsconfig.app.json` / `tsconfig.server.json` / `tsconfig.node.json`
  / `tsconfig.shared.json`; opt-in project references for per-context type
  checking.
- **Other changes**: component names normalized to match route names;
  `error.data` auto-parsed; only Vue component styles are inlined (not
  global CSS); page metadata is scanned after the `pages:extend` hook; SPA
  loading templates render outside the app root; `window.__NUXT__` is
  removed in favor of `useNuxtApp().payload`; TypeScript `baseUrl` is no
  longer used for alias resolution.

[Source: https://nuxt.com/docs/4.x/getting-started/upgrade] **Migration
tooling**: an official Codemod recipe automates the bulk of the migration —
`npx codemod@0.18.7 nuxt/4/migration-recipe` — plus individual codemods for
file-structure moves, dedupe-value changes, watch-path changes,
data/error-default changes, and component-reactivity changes.

[Source: https://nuxt.com/docs/4.x/getting-started/upgrade] **Testing Nuxt
5 pre-release from Nuxt 4**: set `future.compatibilityVersion: 5` in
`nuxt.config.ts` [VERSION-SENSITIVE: requires Nuxt 4.2+] to opt into
upcoming Nuxt 5 behaviors ahead of the actual major release — Vite
Environment API, case-sensitive routing, normalized page names,
comment-node placeholders for client-only components, Vue Options API
disabled by default, typed pages on by default, stricter TypeScript
imports.

[Source: https://nuxt.com/docs/4.x/getting-started/upgrade] A **Nuxt 2 →
Nuxt 3+** migration guide is also referenced by the upgrade docs, described
as covering breaking changes with step-by-step instructions and
backward-compatibility configuration options; full content of that specific
guide was not independently re-fetched in this pass beyond confirming its
existence. Unresolved: exact current URL/full content of the Nuxt 2→3
guide not independently re-verified word-for-word in this research pass.

[Source: https://nuxt.com/blog/nuxt2-eol] **Nuxt 2 end of life**: Nuxt 3 has
been the default/recommended version since November 16, 2022; the Nuxt team
is no longer investing in Nuxt 2 and directs teams unable to migrate toward
third-party (HeroDevs "Never-Ending Support") commercial extended support.

Not covered: Nuxt's official docs are framework-upgrade-focused (2→3, 3→4,
4→5-preview); no official docs page for migrating *from a different
framework* (e.g., "migrating from Next.js to Nuxt") was located during this
research pass — Not documented / could not verify.

## 12. Version information

[Source: https://github.com/nuxt/nuxt/releases] As of this research date
(2026-09-09), the latest documented stable releases are **Nuxt 4.5.2**
(released 2026-08-05) and, on the maintenance-only v3 line, **Nuxt 3.21.11**
(also ~2026-08-05, one of the final v3 releases before its EOL).

[Source: https://nuxt.com/docs/4.x/community/roadmap] Documented release
policy: **major** releases targeted roughly yearly; **minor** releases
roughly monthly; **patch** releases roughly weekly. Nuxt follows semantic
versioning; breaking changes are disallowed in patch/minor releases except
inside features explicitly marked `experimental`. No formal "LTS" label is
used — instead, each major version is guaranteed a minimum support window
of **6 months after the next major version ships**, with a guaranteed
upgrade path between every pair of consecutive majors.

[Source: https://nuxt.com/docs/4.x/community/roadmap] Documented version
timeline: **Nuxt 4.x** (current stable) released 2025-07-16; **Nuxt 3.x**
reached end-of-life **2026-07-31** (no longer receiving bug/security
fixes); **Nuxt 2.x**/**1.x** are unmaintained; **Nuxt 5.x** is
[VERSION-SENSITIVE / forward-looking, subject to change] scheduled for
roughly Q4 2026, planned to include a Nitro v3 upgrade, with the Nuxt
4→5 transition deliberately split to phase in breaking changes gradually
(Nuxt 4 focused on stability; Nuxt 5 following closely behind).

[Source: https://nuxt.com/docs/4.x/getting-started/upgrade]
[VERSION-SENSITIVE: Nuxt 4.5.0, 2026-07-18] Nuxt 4.5 ("the biggest release
in a while" per search-derived summaries — see caveat below) shipped Vite 8
support, Rspack 2 via Rsbuild, experimental SSR streaming, a stable error
-code system, a new `useLayout` composable, and named views. Unresolved:
this specific characterization ("biggest release in a while") was
surfaced via WebSearch summarization of nuxt.com content rather than a
direct WebFetch quote confirmed word-for-word in this pass; treat the
superlative framing as unconfirmed, though the underlying feature list is
corroborated by the GitHub Releases page and the upgrade-guide fetch.

[Source: https://nuxt.com/docs/4.x/getting-started/installation] Minimum
supported **Node.js** version for the current stable line: **22.x or
newer** (even-numbered LTS lines recommended, e.g. 22 or 24).
[VERSION-SENSITIVE: Nuxt 4.x] Note this is a stricter requirement than
Nuxt 3 originally had (Nuxt 3→4 upgrade notes separately flag Node
22.19+ as required once `jiti` is no longer bundled — see Section 11).

## 13. Breaking changes

[Source: https://nuxt.com/docs/4.x/getting-started/upgrade] Nuxt 3→4
breaking changes are enumerated in full in Section 11 (Migration); the
highest-impact ones are the `app/` directory restructure, the removal of
bundled `jiti` (raising the Node requirement and changing config-loading
behavior), the Vite Environment API migration for module authors, and the
`useAsyncData`/`useFetch` `data` ref becoming `shallowRef` by default.

[Source: https://nuxt.com/blog/v4] Additional Nuxt 4.0 breaking changes
called out in the release announcement: Nuxt 2 compatibility removed from
`@nuxt/kit` (affects module authors specifically, not app authors);
various legacy/deprecated utilities cleaned out; the new stricter
TypeScript project-reference setup may surface type errors that were
previously hidden. The announcement recommends `npx nuxt upgrade --dedupe`
plus the Codemod tooling (Section 11), and states Nuxt 3 continued to
receive maintenance support into 2026 (see Section 12 for the confirmed
2026-07-31 EOL date, which is more precise than the "January 2026" figure
that appeared in one WebFetch summary of the v4 blog post — flagged as an
**inconsistency**: Unresolved — one summarized fetch of nuxt.com/blog/v4
stated Nuxt 3 support ran "through January 2026," while the Roadmap page
and the dedicated Nuxt-3-EOL discussion both state 2026-07-31; the Roadmap
page's explicit EOL date is treated as authoritative here since it's the
more specific, dedicated source, but the discrepancy itself should be
noted rather than silently resolved).

[Source: https://nuxt.com/blog/v4-5-security] The July 2026 security patch
line (4.5.1/3.21.10) itself introduced no *new* breaking API changes but
did change default security-relevant behavior around case-sensitive route
matching (opt-in via `router.options.sensitive: true` for apps that relied
on the old case-insensitive-bypass behavior) — see Section 7.

Not documented / could not verify: a consolidated Nuxt 4→5 breaking-changes
list was not available as stable/finalized documentation at research time,
since Nuxt 5 had not shipped as stable; only the opt-in
`future.compatibilityVersion: 5` preview behaviors (Section 4/11) are
documented so far, and those are explicitly framed as subject to change
before the final release.

## 14. Limitations

[Source: https://nuxt.com/docs/4.x/guide/going-further/debugging] Node
inspector debugging (`nuxt dev --inspect`) is documented as **not working
inside Docker**, since it requires the Node.js and Chrome processes to run
on the same platform.

[Source: https://nuxt.com/docs/4.x/guide/going-further/layers] Layers:
remote-layer dependencies are isolated in a nested `node_modules/.c12/...`
path invisible to the consuming project's package manager/tooling (e.g.
ESLint cannot resolve them); global path aliases inside a layer resolve
against the consumer app, not the layer's own files.

[Source: https://nuxt.com/docs/4.x/guide/concepts/rendering] Hybrid
rendering / `routeRules` are documented as **unavailable** when the output
is produced via the static `nuxt generate` command.

[Source: https://nuxt.com/docs/4.x/guide/concepts/auto-imports] Auto
-imported `ref`/`computed` values are **not** auto-unwrapped inside
component templates — `.value` access is still required in that context.
Most built-in composables require a valid Nuxt "context" (setup function,
plugin, or middleware) and throw "Nuxt instance is unavailable" if called
outside one (e.g. after a stray `await` inside an async function without
`asyncContext`).

[Source: https://nuxt.com/docs/4.x/getting-started/testing] `@nuxt/test-utils`'s
runtime-environment unit tests and its E2E utilities are documented as
**unable to coexist in the same test file**.

[Source: https://nuxt.com/docs/4.x/getting-started/installation] Node.js
**22.x+** is a hard minimum for the current stable line (Section 12) — this
is a documented environmental constraint, not a soft recommendation.

Not documented / could not verify: no single "Known Limitations" reference
page was located; the items above are limitations stated inline across
multiple docs pages rather than centralized.

## 15. Debugging

[Source: https://nuxt.com/docs/4.x/guide/going-further/debugging] Official
guidance covers **browser and IDE debugging**. Sourcemaps are on by
default for server builds and client dev mode; explicit control via
`sourcemap: { server: true, client: true }` in `nuxt.config.ts`.

**Node inspector**: `nuxt dev --inspect` starts the Node debugger; a
Node.js icon then appears in Chrome DevTools for attaching. Documented
limitation: doesn't work inside Docker (processes must share a platform).

**VS Code**: documented launch-config pattern — a Chrome launch config
pointed at `http://localhost:3000` for client debugging, a Node launch
config running `nuxt/bin/nuxt.mjs dev` for server debugging, and a compound
"fullstack: nuxt" configuration to run both together; optionally set
`"userDataDir": false` to reuse existing browser extensions.

**JetBrains IDEs**: a `nuxt.run.xml` run-configuration file at the project
root, combining a JavaScript debug config (Chrome, `http://localhost:3000`)
and a Node.js config (`nuxt.mjs dev`) into a compound run configuration.

[Source: https://nuxt.com/docs/4.x/guide/directory-structure/nuxt] **Nuxt
DevTools** exposes a "Virtual Files" tab for inspecting the generated
`.nuxt/` output without manually opening the (git-ignored, auto-regenerated)
directory.

[Source: https://nuxt.com/docs/4.x/api/nuxt-config] The `debug` config
option enables verbose logging of hook names, timings, and arguments for
diagnosing lifecycle/hook issues.

Unresolved: the Nuxt DevTools feature set for debugging (Timeline,
Render Tree, Hooks tab, Assets panel) referenced in Section 8 comes from a
`devtools.nuxt.com` page located via WebSearch summary rather than a
direct WebFetch of the full page content in this pass — treat the exact
feature names as lower-confidence pending direct verification, though the
existence of Nuxt DevTools itself and its role in debugging/inspection is
corroborated by multiple official docs pages referencing it directly (e.g.,
the `.nuxt/` Virtual Files tab, above).

## 16. Integration

[Source: https://nuxt.com/docs/4.x/guide/going-further/modules] Nuxt's
primary integration mechanism for third-party tools/ecosystems is the
**module system**: modules hook into Nuxt's config and lifecycle hooks to
wire in Vue plugins, CMS platforms, server routes, components, and more, as
independently publishable npm packages, without needing to fork or patch
Nuxt core. `@nuxt/kit` provides the module-authoring API surface referenced
by the API docs (Section 3).

[Source: https://nuxt.com/docs/4.x/getting-started/state-management]
**Pinia** integration is explicitly documented as "the official Vue
recommendation" for state management, added via `npx nuxt module add pinia`
(installs and registers the `@pinia/nuxt` module).

[Source: https://nuxt.com/docs/4.x/guide/concepts/typescript] **TypeScript**
is a first-class, zero-config integration: auto-generated, project
-referenced tsconfigs per context (app/server/shared/node); optional
type-checked builds via `vue-tsc`.

[Source: https://nuxt.com/docs/4.x/guide/best-practices/performance]
Official **image**, **font**, and **script** integrations are documented as
first-party modules: Nuxt Image (`<NuxtImg>`), Nuxt Fonts, and Nuxt Scripts,
each addressed directly in the performance best-practices guide as the
recommended integration path for those concerns (rather than hand-rolled
solutions).

[Source: https://nuxt.com/modules/security] The Nuxt Modules directory at
nuxt.com/modules catalogs both official and community integrations
(TailwindCSS via `@nuxtjs/tailwindcss`, Pinia via `@pinia/nuxt`, security
headers via community `nuxt-security`, etc.) — but, as flagged in Section 7,
listing on this directory does not by itself imply Nuxt-core-team
maintenance; each module's own page states its maintainer.

[Source: https://nuxt.com/docs/4.x/getting-started/deployment] **Deployment
-platform integration** is handled through Nitro presets (Vercel, Netlify,
Cloudflare Pages/Workers, Deno, AWS, and plain Node — full catalog lives on
Nitro's own docs, linked from but not duplicated in the Nuxt deployment
page), auto-detected in many cases or explicitly set via `nitro.preset` /
`NITRO_PRESET`.

[Source: https://nuxt.com/docs/4.x/guide/directory-structure/server]
**Server-side integration** (databases, external APIs, auth) is done
through `server/` (Nitro/H3) — `defineEventHandler()`-based routes/
middleware/plugins/utils — rather than a separate backend framework.

## 17. Production considerations

[Source: https://nuxt.com/docs/4.x/getting-started/deployment] Explicitly
set `NODE_ENV=production` when running the Node server output, to avoid
development-mode warning noise in production logs. Configure
`NITRO_PORT`/`HOST` and TLS via `NITRO_SSL_CERT`/`NITRO_SSL_KEY` (docs
recommend TLS termination at a reverse proxy rather than directly in
Nitro for most deployments). Use PM2 (`ecosystem.config.cjs`, cluster
mode) or an equivalent process manager for resilience/scaling. On
Cloudflare specifically, disable "Rocket Loader™" and "Email Address
Obfuscation," which the docs identify as causes of script injection and
hydration mismatches in production.

[Source: https://nuxt.com/blog/v4-5-security] Production security posture
requires more than "upgrade the package": the July 2026 advisory batch
specifically calls out that fixing the cross-user payload-disclosure issue
(GHSA-wm8w-6qjm-cv43) also requires **purging CDN/edge caches**
post-upgrade to remove already-leaked cached payloads — an operational
step beyond a code/dependency bump.

[Source: https://nuxt.com/docs/4.x/guide/concepts/rendering] Choosing a
rendering/caching strategy per route via `routeRules` (`swr`, `isr`,
`prerender`, `ssr: false`) is presented as a production-scaling lever,
letting teams balance infra cost, freshness, and latency per route rather
than committing the whole app to one strategy.

[Source: https://nuxt.com/docs/4.x/guide/best-practices/performance]
Recommended production-monitoring/verification tools: PageSpeed Insights
and WebPageTest (in addition to Nuxt-specific tools like Nuxi Analyze and
Nuxt DevTools, which are primarily dev-time).

[Source: https://nuxt.com/docs/4.x/getting-started/deployment] For
subpath-hosted production deployments, `app.baseURL` (or the
`NUXT_APP_BASE_URL` env var) must be set correctly or asset/route
resolution will break in production despite working locally at the root
path.

---

## Summary of sourcing caveats for this document

- Several WebFetch calls against nuxt.com returned tool-generated
  paraphrase/summary rather than verbatim text (WebFetch runs a secondary
  model over fetched content); direct quotes above are reproduced only
  where the fetch tool itself returned quoted text from the page. Anywhere
  a claim's precision matters (exact wording, exact numbers), this is
  flagged inline as Unresolved or version-tagged.
- A small number of facts (Nuxt DevTools' specific feature-panel names;
  the "biggest release in a while" characterization of 4.5) were sourced
  via WebSearch result summaries referencing nuxt.com/devtools.nuxt.com
  content rather than a direct WebFetch read of the full page in this pass,
  and are flagged as such at point of use.
- Version numbers (4.5.2, 3.21.11, release dates) are sourced from the
  official `github.com/nuxt/nuxt` releases page, which is the canonical
  GitHub org repository for the project and is treated as an official
  source per this project's sourcing rules.
