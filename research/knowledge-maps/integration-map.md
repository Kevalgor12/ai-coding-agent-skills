# Integration Map

How the 44 researched technologies connect to one another: hard dependencies, documented complementary pairings, and concrete integration mechanics — organized into clusters, with every fact traced back to the source citation captured during the underlying per-technology research (`research/technologies/*.md`).

**Scope and method.** This map draws exclusively from `kmap_integration.json`, a pre-extracted summary of `dependsOn` / `complementaryWith` / `integratesWith` / `commonCombinations` fields for the 44 surveyed technologies. Nothing below is invented — where the source data is silent or only inferential, that is stated explicitly. Citations are reproduced verbatim in brackets, including the data set's own `[Inference from X.md, not an explicit doc statement]` markers, which mean the underlying per-technology research flagged a plausible-but-undocumented connection rather than citing a primary source. My own cross-cutting observations (combining two or more facts that individually didn't state the connection) are separately labeled **[Synthesis]**.

**Relationship key** — `Depends on` = hard technical/runtime requirement; `Complementary` = commonly paired, officially recommended, or documented as working well together without one requiring the other; `Integrates via` = the concrete mechanism (plugin, adapter, API, protocol) that makes the pairing work.

---

## 1. Language & Runtime Substrate

The foundational layer nearly everything else in this corpus sits on top of.

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| ECMAScript → Node.js | Depends on | ECMA-262 defines no I/O, standard library, or execution environment; it explicitly relies on a host (browser, or a server runtime such as Node.js/Deno/Bun) to supply these. | `[Source: https://tc39.es/ecma262/multipage/overview.html]` |
| TypeScript → ECMAScript | Depends on | TypeScript is a syntactic/semantic superset of JS/ECMAScript and compiles to plain JS; type annotations are compile-time-only. | `[Source: https://www.typescriptlang.org/docs/handbook/2/basic-types.html]` |
| TypeScript → Node.js | Depends on (inferred) | Documented install routes run `tsc` via npm/npx, implying a Node.js/npm environment for the tooling itself; not stated verbatim. | `[Inference from typescript.md, not an explicit doc statement]` |
| TypeScript ↔ Node.js | Complementary | Node.js documents native, built-in "type stripping" support for running `.ts` files directly without a separate build step. | `[Source: https://nodejs.org/api/typescript.html]` |
| TypeScript ↔ Node.js | Integrates via | Node's type-stripping matured from experimental (v22.6.0) → default (v23.6.0/22.18.0) → stable (v25.2.0/24.12.0) → flag removed (v26.0.0). | `[Source: https://nodejs.org/api/typescript.html]` |
| HTML ↔ ECMAScript | Integrates via | `<script>` element, `javascript:` URLs, and event-handler content attributes; formally defines classic vs. module script processing (including module types for CSS, JSON, text, WebAssembly). | `[Source: https://html.spec.whatwg.org/multipage/webappapis.html]` |
| HTML ↔ CSS | Complementary / Integrates via | HTML discourages presentational markup, directing authors to CSS; both share the same namespaced DOM tree regardless of HTML vs. XML serialization. | `[Source: https://html.spec.whatwg.org/multipage/introduction.html]` / `[Source: https://html.spec.whatwg.org/multipage/infrastructure.html#html-vs-xhtml]` |
| CSS → HTML | Depends on | CSS is a stylesheet language for HTML/XML/SVG/MathML/XHTML documents — it has nothing to style without markup. | `[Source: https://developer.mozilla.org/en-US/docs/Web/CSS]` |
| CSS ↔ ECMAScript | Integrates via | CSSOM (`document.styleSheets`, `element.style`, `window.getComputedStyle()`, `CSSStyleSheet.insertRule()/.deleteRule()`) plus CSS Typed OM is the documented JS integration surface. | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/CSS_Object_Model]` |
| ECMAScript ↔ HTML | Integrates via | WHATWG's HTML spec uses the `hostDefined` parameter of `HostLoadImportedModule` to set correct fetch destinations for constructs like `<link rel="preload" as="...">`. | `[Source: https://tc39.es/ecma262/multipage/host-layering-points.html]` |
| ECMAScript ↔ ECMA-402 (Intl) | Integrates via | `Intl.DateTimeFormat`, `Intl.NumberFormat`, `Intl.Collator`, etc. are not defined in ECMA-262 itself but in the companion ECMA-402 standard, maintained by the same TC39 committee and versioned in step. | `[Source: https://ecma-international.org/publications-and-standards/standards/ecma-402/]` |
| Go → C compiler (via cgo) | Depends on | The Data Race Detector (`-race`) requires cgo and an installed C compiler; cgo interop generally requires a C toolchain. | `[Source: https://go.dev/doc/articles/race_detector.html]` |
| Go ↔ C | Integrates via | cgo lets Go code call C libraries and vice versa. | `[Source: https://go.dev/blog/c-go-cgo]` |
| Python ↔ C | Integrates via | CPython's C API (`Python.h`, `PyObject*`, `PyModuleDef`/multi-phase init, `PyInit_<name>()`) is the documented mechanism for extension modules and for embedding CPython in a C/C++ host; a Limited API/stable ABI (`Py_LIMITED_API`) lets a compiled extension target a minimum Python version. | `[Source: https://docs.python.org/3/extending/extending.html]` |
| Python ↔ Linux perf | Integrates via | `sys.activate_stack_trampoline("perf")`, `-X perf`/`-X perf_jit`, or `PYTHONPERFSUPPORT=1` let Python-level function names appear in `perf` output. | `[Source: https://docs.python.org/3/howto/perf_profiling.html]` |

---

## 2. Frontend Frameworks & Build Tooling

### 2.1 React ecosystem

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| React ↔ TypeScript | Complementary / Integrates via | Officially supported: `@types/react`/`@types/react-dom`, a `tsconfig` with a valid `jsx` option, `.tsx` files. React 19 changed `useRef()` typing, `ReactElement` props typing, and replaced the global `JSX` namespace with scoped `React.JSX`. | `[Source: https://react.dev/learn/typescript]` |
| React ↔ Vite | Complementary / Integrates via | One of three officially recommended build tools (with Parcel, RSbuild) for a from-scratch React app; React Compiler is pre-wired into `create-vite` scaffolds; official first-party Vite plugin exists. | `[Source: https://react.dev/learn/build-a-react-app-from-scratch]`, `[Source: https://react.dev/blog/2025/10/07/react-compiler-1]`, `[Source: https://vite.dev/guide/why]` |
| Next.js → React | Depends on | Next.js is built on and requires React Components; App Router additionally bundles React canary releases, Pages Router uses whatever React version is in `package.json`. | `[Source: https://nextjs.org/docs]` |
| Next.js ↔ React | Integrates via | Server/Client Component model, RSC Payload serialization, and hydration are direct React integration mechanics. | `[Source: https://nextjs.org/docs/app/getting-started/server-and-client-components]` |
| React ↔ Next.js | Complementary | Named as the framework taking "full advantage of React's architecture" for full-stack apps, with the most complete Server Components + Suspense implementation among recommended frameworks. | `[Source: https://react.dev/learn/start-a-new-react-project]` |
| React ↔ ESLint | Integrates via | `eslint-plugin-react-hooks` is the recommended Rules-of-React enforcement tool; Compiler-powered rules (`set-state-in-render`, `set-state-in-effect`, `refs`) ship inside it via `reactHooks.configs.flat.recommended`. | `[Source: https://react.dev/blog/2025/10/07/react-compiler-1]` |
| React ↔ Babel | Integrates via | React Compiler is distributed as a Babel plugin (`babel-plugin-react-compiler`); a first-party SWC (non-Babel) integration is unresolved in the docs. | `[Source: https://react.dev/blog/2025/10/07/react-compiler-1]` |
| React ↔ HTML | Integrates via | React 19 added native document metadata (rendering `<title>`, `<link>`, `<meta>` directly inside components, auto-hoisted to `<head>`) and full custom-elements (Web Components) support. | `[Source: https://react.dev/blog/2024/12/05/react-19]` |
| React ↔ CSS | Integrates via | Native stylesheet support via `<link rel="stylesheet" precedence="...">` with automatic insertion-order management, introduced in React 19. | `[Source: https://react.dev/blog/2024/12/05/react-19]` |
| React ↔ Next.js (security) | Integrates via | Named among frameworks affected by the Dec 2025 RSC CVE-2025-55182 (patched Next.js minor lines 14.2.35 through 16.1.5). | `[Source: https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components]` |

### 2.2 Next.js

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Next.js → Node.js | Depends on | Node.js Runtime is the default server runtime; minimum supported version is Node.js 20.9+ as of 16.3.4 (Node 18 dropped since v16). | `[Source: https://nextjs.org/docs/app/api-reference/edge]` / `[Source: https://nextjs.org/docs/app/getting-started/installation]` |
| Next.js ↔ TypeScript | Complementary / Integrates via | Documented production-considerations recommendation, min. version 5.1.0+, `next typegen` (generates `PageProps`/`LayoutProps`/`RouteContext` helpers), opt-in `typescript@^7` delegation via `useTypeScriptCli`. | `[Source: https://nextjs.org/docs/app/guides/production-checklist]`, `[Source: https://nextjs.org/docs/app/getting-started/installation]`, `[Source: https://nextjs.org/docs/app/getting-started/upgrading]` |
| Next.js ↔ Docker | Complementary / Integrates via | One of four documented deployment paths, supporting "all Next.js features," with official example templates for standalone output and multi-environment configs. | `[Source: https://nextjs.org/docs/app/getting-started/deploying]` |
| Next.js ↔ Sass | Complementary / Integrates via | Dedicated official integration guide; Turbopack has specific (breaking) behavior around Sass tilde imports. | `[Source: https://nextjs.org/docs/app/guides]` |
| Next.js ↔ Tailwind CSS | Complementary / Integrates via | Dedicated official Tailwind CSS v3 integration guide; also explicitly named a good fit for the `@tailwindcss/postcss` path; `@tailwindcss/turbopack` in active development specifically for Next.js's Turbopack bundler. | `[Source: https://nextjs.org/docs/app/guides]`, `[Source: https://github.com/tailwindlabs/tailwindcss (Unreleased CHANGELOG section)]` |
| Next.js ↔ Jest / Vitest / Playwright | Integrates via | Official first-party setup guides for all three; a new `@next/playwright` package (16.3) ships an `instant()` test helper for instant-navigation UI. | `[Source: https://nextjs.org/docs/app/guides/testing]`, `[Source: https://nextjs.org/blog/next-16-3]` |
| Next.js ↔ GitHub | Integrates via | Verified deployment Adapters (Vercel, Bun) are hosted under the Next.js GitHub org; GitHub Pages is a valid static-export hosting target. | `[Source: https://nextjs.org/docs/app/getting-started/deploying]` |
| Next.js ↔ WebSocket API | Integrates via | The May 2026 coordinated security release patched a High-severity SSRF vulnerability specifically in Next.js's WebSocket upgrade handling. | `[Source: https://vercel.com/changelog/next-js-may-2026-security-release]` |
| Next.js ↔ OpenTelemetry | Integrates via | `instrumentation.ts/.js` `register()` integrates OpenTelemetry (officially shown example uses `@vercel/otel`'s `registerOTel`), running in both Node.js and Edge environments. | `[Source: https://nextjs.org/docs/app/guides/instrumentation]` |

### 2.3 Vue / Nuxt ecosystem

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Vue → Node.js | Depends on | SSR deployment explicitly requires a Node.js server process; rendering-to-string is CPU-intensive and SSR output is not deployable as static files (unlike SSG). | `[Source: https://vuejs.org/guide/scaling-up/ssr.html]` |
| Vue → ECMAScript | Depends on | Vue 3's `reactive()` relies on native ES Proxy objects; Vue 2 used `Object.defineProperty()` instead "due to browser support limitations," making native Proxy support a version-sensitive dependency of Vue 3's reactivity model. | `[Source: https://vuejs.org/guide/extras/reactivity-in-depth.html]` |
| Vue ↔ Vite | Complementary / Integrates via | Vite is the recommended build tool/dev server; `create-vue` scaffolding produces Vite-based projects; `@vitejs/plugin-vue` compiles SFCs, replacing the now maintenance-mode Vue CLI (webpack-based). | `[Source: https://vuejs.org/guide/scaling-up/tooling.html]` |
| Vue ↔ TypeScript | Complementary / Integrates via | First-class: bundled type declarations, `defineComponent()`/`<script setup lang="ts">`, `vue-tsc` for CLI/CI type-checking, "Vue - Official" (Volar) VS Code extension superseding Vetur. | `[Source: https://vuejs.org/guide/typescript/overview.html]` |
| Nuxt → Vue | Depends on | Nuxt is "a free and open source framework" built on top of Vue.js; `.vue` files, Vue reactivity APIs, and the Vue component lifecycle are foundational. | `[Source: https://nuxt.com/docs/4.x/getting-started/introduction]` |
| Nuxt → Node.js | Depends on | Minimum supported Node.js for the current stable Nuxt 4.x line is 22.x or newer (even-numbered LTS lines recommended) — a hard requirement. | `[Source: https://nuxt.com/docs/4.x/getting-started/installation]` |
| Vue ↔ Nuxt | Complementary | Nuxt is "the recommended" meta-framework for SSR/SSG production use, handling client/server build coordination, routing, state, and hydration on top of Vue core. | `[Source: https://vuejs.org/guide/scaling-up/ssr.html]` |
| Nuxt ↔ TypeScript | Complementary / Integrates via | Zero-config: auto-generated, project-referenced `tsconfig`s per context (app/server/shared/node), optional type-checked builds via `vue-tsc` / `npx nuxt typecheck`. | `[Source: https://nuxt.com/docs/4.x/guide/concepts/typescript]` |
| Nuxt ↔ Vite | Complementary / Integrates via | Vite is the default builder (configurable to webpack, Rspack, or custom); Nuxt 4.5 shipped Vite 8 support and a Vite Environment API migration for module authors. | `[Source: https://nuxt.com/docs/4.x/api/nuxt-config]` |
| Nuxt ↔ Tailwind CSS | Complementary / Integrates via | Catalogued in the Nuxt Modules directory via `@nuxtjs/tailwindcss`. | `[Source: https://nuxt.com/modules/security]` |
| Vue ↔ Vue Router | Complementary / Integrates via | "The official router for Vue.js," installed via `app.use(router)`; nested routes, navigation guards, transition integration. | `[Source: https://router.vuejs.org/introduction.html]` |
| Vue ↔ Pinia | Complementary / Integrates via | Official state-management library recommended over Vuex; Composition-API-style API, Devtools integration, HMR, SSR support. | `[Source: https://vuejs.org/guide/scaling-up/state-management.html]` |
| Nuxt ↔ Pinia | Integrates via | Called out as "the official Vue recommendation" for state management in Nuxt, installable via `npx nuxt module add pinia` (registers `@pinia/nuxt`). | `[Source: https://nuxt.com/docs/4.x/getting-started/state-management]` |
| Vue ↔ VitePress | Integrates via | Named specifically as the SSG option for docs/content sites, built on Vue. | `[Source: https://vuejs.org/guide/scaling-up/ssr.html]` |
| Vue ↔ Laravel | Integrates via | Laravel ships an official Vite plugin for backend-framework + Vue asset-pipeline integration. | `[Source: https://vuejs.org/guide/scaling-up/tooling.html]` |
| Vue ↔ Web Components | Integrates via | Bidirectional: Vue consumes native custom elements (`compilerOptions.isCustomElement`) and authors custom elements from Vue components via `defineCustomElement()`; 100% score on the "Custom Elements Everywhere" suite for consumption-side interop. | `[Source: https://vuejs.org/guide/extras/web-components.html]` |
| Vue ↔ Sentry / Bugsnag | Integrates via | Both have official Vue-specific error-tracking integration guides, wired through `app.config.errorHandler`. | `[Source: https://vuejs.org/guide/best-practices/production-deployment.html]` |
| Nuxt ↔ GitHub | Integrates via | Security fixes published via GitHub Security Advisories (GHSA IDs); version/release info sourced from `github.com/nuxt/nuxt` releases. | `[Source: https://github.com/nuxt/nuxt/releases]` |

### 2.4 Angular

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Angular → TypeScript | Depends on | Angular is Google's TypeScript-based framework; engine compatibility pins exact TS ranges per major (e.g. Angular 22.0.x requires TS ≥6.0.0 <6.1.0); v20/v21/v22 each raised the minimum TS version as a breaking change. | `[Source: https://angular.dev/reference/versions]` |
| Angular → RxJS | Depends on | Requires RxJS `^6.5.3 \|\| ^7.4.0` across Angular 20.x–22.x; RxJS interop (`toSignal`/`toObservable`/`rxResource`) is a core Angular API surface. | `[Source: https://angular.dev/reference/versions]` |
| Angular → Node.js | Depends on | Engine compatibility pins required Node.js ranges per major (e.g. 22.0.x requires `^22.22.3 \|\| ^24.15.0 \|\| ^26.0.0`); v20.0.0 dropped Node v18 and Node 22.0–22.10. | `[Source: https://angular.dev/reference/versions]` |
| Angular ↔ Vite | Complementary | The modern Angular build pipeline uses Vite and esbuild for fast compilation, replacing the older Webpack-based toolchain. | `[Source: https://angular.dev/overview]` |
| Angular ↔ RxJS | Integrates via | First-class `@angular/core/rxjs-interop` package: `toSignal()`, `toObservable()`, `rxResource()`, `takeUntilDestroyed()` bridge Signals and Observables. | `[Source: https://angular.dev/ecosystem/rxjs-interop]` |
| Angular ↔ Vitest | Integrates via | Vitest is now the default test runner for new Angular CLI projects (v21+), replacing Karma, running in Node.js with jsdom or happy-dom. | `[Source: https://angular.dev/guide/testing]` |
| Angular ↔ Playwright | Complementary / Integrates via | Real-browser testing remains available via providers like Playwright or WebdriverIO alongside the default Vitest+jsdom setup. | `[Source: https://angular.dev/guide/testing]` |
| Angular ↔ Angular Material / CDK | Integrates via | Officially-maintained companion component/UI-primitives library, including as a documented "special dependency" in the interactive Update Guide. | `[Source: https://angular.dev/guide/ngmodules/overview]` |
| Angular ↔ AngularJS | Integrates via | The upgrade package (`ngUpgrade`, with `upgrade/static` as the current entry point) supports hybrid apps mixing legacy AngularJS 1.x and modern Angular. | `[Source: https://angular.dev/best-practices/security]` |
| Angular ↔ GitHub | Integrates via | Angular CLI documents automatic GitHub Pages deploy via `ng add angular-cli-ghpages`; canonical breaking-changes record is the `angular/angular` GitHub repo's `CHANGELOG.md`. | `[Source: https://angular.dev/tools/cli/deployment]` |
| Angular ↔ Gemini CLI | Integrates via | Angular officially publishes "Agent Skills" for AI coding agents as of the v22 era, with documented supported tools including Gemini CLI and Antigravity, plus community installers like `skills.sh`. | `[Source: https://angular.dev/ai/agent-skills]` |
| Angular ↔ Docker | Not documented | Not explicitly named in the underlying research for containerized deployment. | `[Inference from angular.md, not an explicit doc statement]` |
| Angular ↔ Jest | Not documented | Only Vitest, Karma/Jasmine, Playwright and WebdriverIO are documented as Angular test runners; Jest is not named. | `[Inference from angular.md, not an explicit doc statement]` |
| Angular ↔ GitHub Actions | Not documented | Production deployment/build guidance implies typical CI/CD usage but no specific GitHub Actions integration is documented. | `[Inference from angular.md, not an explicit doc statement]` |

### 2.5 Vite (the build-tool hub)

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Vite → Node.js | Depends on | Vite 8 requires Node.js 20.19+ or 22.12+ to support its ESM-only distribution without flags. | `[Source: https://vite.dev/blog/announcing-vite8]` |
| Vite → ECMAScript | Depends on | Dev-server and source-serving model depends on native ES modules; config files must be resolvable as ESM by Node (via `.mjs` or `"type": "module"`). | `[Source: https://vite.dev/config/]` / `[Source: https://vite.dev/guide/troubleshooting]` |
| Vite ↔ Vitest | Complementary / Depends on (Vitest side) | Vitest is layered directly on top of Vite, reusing `vite.config.*` so dev/build/test share one pipeline and one config file; Vitest 5.0 requires Vite ≥6.4.0. | `[Source: https://vite.dev/guide/why]` / `[Source: https://vitest.dev/guide/]` |
| Vite ↔ TypeScript | Complementary / Integrates via | Full TS typing on the Plugin/JS API; config files may use `.ts`/`.mts`/`.cts`; built-in TS/JSX/TSX transpilation without type-checking (a separate `tsc` run is needed for type errors). | `[Source: https://vite.dev/guide/]`, `[Source: https://vite.dev/config/]`, `[Source: https://vite.dev/guide/features]`, `[Source: https://www.typescriptlang.org/docs/handbook/integrating-with-build-tools.html]` |
| Vite ↔ Sass | Complementary / Integrates via | Built-in CSS-preprocessor support for Sass (also Less, Stylus) with automatic `@import` inlining and URL rebasing — documented by the Vite project itself, not sass-lang.com. | `[Source: https://vite.dev/guide/features]` / `[Source: sass.md §16 Integration]` |
| Vite ↔ CSS | Integrates via | Imports with HMR, CSS Modules, PostCSS, automatic CSS code splitting. | `[Source: https://vite.dev/guide/features]` |
| Vite ↔ HTML | Integrates via | Dedicated `transformIndexHtml` plugin hook, plus dev-time `<script type="module">` injection into HTML for non-SPA backend integration. | `[Source: https://vite.dev/guide/api-plugin]` / `[Source: https://vite.dev/guide/backend-integration]` |
| Vite ↔ GitHub / GitHub Actions | Integrates via | Official static-deploy guide for GitHub Pages (via GitHub Actions), including setting `base` to the repo path. | `[Source: https://vite.dev/guide/static-deploy]` |
| Vite ↔ ECMAScript | Integrates via | Dependency pre-bundling converts CommonJS/UMD dependencies to ESM; source is served on-demand over native ESM. | `[Source: https://vite.dev/guide/why]` |

---

## 3. ORM / Database Cluster

### 3.1 ORMs

| ORM | Depends on | Databases integrated | Cache backend | TypeScript | Notes / citation |
|---|---|---|---|---|---|
| **Mongoose** | MongoDB (built on the official MongoDB Node.js driver; change streams/transactions need a replica set or sharded cluster) `[Source: https://mongoosejs.com/docs/connections.html]`; Node.js ≥20.19.0 (v9) `[Source: https://mongoosejs.com/docs/migrating_to_9.html]` | MongoDB only | — | Officially supported since v5.11.0 (`Schema<T>`, `model<T>()`, `HydratedDocument<T>`, `QueryFilter`) `[Source: https://mongoosejs.com/docs/typescript.html]` | Official Next.js integration guide (connection caching, hot-reload-safe model registration, ESM/webpack fixes) `[Source: https://mongoosejs.com/docs/nextjs.html]`; official AWS Lambda connection-reuse pattern `[Source: https://mongoosejs.com/docs/lambda.html]` |
| **TypeORM** | TypeScript ≥4.5 + `reflect-metadata` (decorator metadata) `[Source: https://typeorm.io/docs/getting-started/]`; Node.js 20+ (v1.0) `[Source: https://typeorm.io/docs/releases/1.0/release-notes/]` | PostgreSQL, MySQL/MariaDB (mysql2 driver only as of v1.0), MongoDB (own `MongoRepository`), Microsoft SQL Server, SQLite (better-sqlite3 default as of v1.0), Electron runtime | Redis / IORedis / IORedis Cluster for query-result caching `[Source: https://typeorm.io/docs/query-builder/caching/]` | Decorator-based entity/column/relation API built on TS decorators (JS also usable) `[Source: https://typeorm.io/docs/getting-started/]` | Docker: migration glob explicitly covers `.ts`/`.js` to support compiled-JS-in-prod / TS-in-dev deployments `[Source: https://typeorm.io/docs/migrations/setup/]`; built-in IoC container removed in v1.0 — docs point to external DI (TypeDI, NestJS) as the replacement path, mechanics undocumented `[Source: https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/]` |
| **Prisma** | Node.js `^20.19.0/^22.12.0/^24.0.0` (v7) `[Source: https://www.prisma.io/docs/orm/v7/reference/system-requirements]`; TypeScript ≥5.4 (v7) `[Source: https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7]`; explicit per-DB driver adapter (e.g. `@prisma/adapter-pg`) as of v7 rather than a native connection `[Source: https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7]` | PostgreSQL (most extensively supported, 9.6–18, GA) `[Source: https://www.prisma.io/docs/orm/v7/reference/supported-databases]`; MySQL (5.6/5.7/8.0/8.4, GA); MongoDB (4.2+/Atlas, supported in v6, dropped in v7, re-introduced in Prisma 8 via collaboration with MongoDB) `[Source: https://www.prisma.io/blog/the-next-evolution-of-prisma-orm]` | — | Optional; Prisma 8 schemas can be authored directly in TypeScript | Next.js official first-party framework guide `[Source: https://www.prisma.io/docs/guides/frameworks/nextjs]`; Docker/Kubernetes named as a traditional-server deployment path, and `prisma migrate dev` warns in non-interactive `docker run` without `-it` `[Source: https://www.prisma.io/docs/orm/prisma-client/deployment/deploy-prisma]` |
| **Drizzle ORM** | A supplied database driver (node-postgres, postgres.js, mysql2, better-sqlite3, or an HTTP/WebSocket serverless driver) — Drizzle compiles to parameterized SQL but implements no network protocol or pool of its own `[Source: https://orm.drizzle.team/docs/overview]`; TypeScript schema is the single source of truth for both query typing and migration generation `[Source: https://orm.drizzle.team/docs/sql-schema-declaration]` | PostgreSQL (most feature-complete dialect — only one with documented RLS support via `withRLS()`/`pgPolicy()`, plus `NULLS NOT DISTINCT`, materialized views) `[Source: https://orm.drizzle.team/docs/rls]`; MySQL; and, via drivers, Neon, Vercel Postgres, PlanetScale, Cloudflare D1, Turso/libSQL, AWS Data API, Supabase, Xata, PGlite, Nile, Netlify Database, Bun SQL `[Source: https://orm.drizzle.team/docs/connect-overview]` | Built-in `upstashCache()` helper integrates the experimental caching layer with Upstash Redis (env vars or `{url, token}`, TTL, hash-expiration) `[Source: https://orm.drizzle.team/docs/cache]` | Schema authored directly in TS via dialect-specific table builders | `drizzle-zod` generates Zod schemas from table definitions (folded into `drizzle-orm` itself as of v1) `[Source: https://orm.drizzle.team/docs/zod]`; `drizzle-kit export` can output SQL DDL for external migration tools like Atlas `[Source: https://orm.drizzle.team/docs/migrations]`; new Effect ecosystem integration in v1 (`@effect/sql-pg`, `drizzle-orm/effect-schema`) `[Source: https://orm.drizzle.team/docs/v0-v1-changes]` |

Notes flagged as thin/unconfirmed in the data itself:
- Prisma ↔ GraphQL: "Not explicitly named in this document as a pairing." `[Inference from prisma.md, not an explicit doc statement]`
- Prisma ↔ GitHub Actions (CI/CD): "Not explicitly named in the document as a CI integration." `[Inference from prisma.md, not an explicit doc statement]`
- Drizzle ↔ Vitest: community usage (GitHub discussions in `drizzle-team/drizzle-orm`) treats PGlite as the de facto in-memory testing story for Postgres-targeting Drizzle+Vitest projects, but this is not an explicit official docs recommendation. `[Inference from drizzle.md, not an explicit doc statement]`

### 3.2 Databases

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| PostgreSQL → TCP/IP | Depends on | Client/server architecture communicates over TCP/IP (or Unix domain sockets); frontend/backend wire protocol (default port 5432) runs over this transport. | `[Source: https://www.postgresql.org/docs/current/tutorial-arch.html]` |
| PostgreSQL ↔ Docker | Complementary (inferred) | The widely-used `postgres` Docker Hub image (Docker's Official Images program, with PostgreSQL community involvement) is the common containerized-deployment path, though not postgresql.org-authored/first-party. | `[Inference from postgresql.md, not an explicit doc statement]` |
| PostgreSQL ↔ Python / Go | Integrates via | Named as external, community/vendor-maintained language drivers (e.g. `psycopg` for Python) — not maintained by the PostgreSQL Global Development Group; Python ≥3.6.8 is also a required build-toolchain component for building PostgreSQL itself. | `[Source: https://www.postgresql.org/docs/current/external-interfaces.html]` |
| MySQL ↔ Docker | Complementary / Integrates via | Officially distributed via Oracle Container Registry (`mysql/community-server`); documented container lifecycle, volume-mounted data/config persistence; official images are Linux-only. | `[Source: https://dev.mysql.com/doc/refman/9.7/en/docker-mysql-getting-started.html]` |
| MySQL ↔ OpenSSL / LDAP / Kerberos / OpenID Connect / WebAuthn | Integrates via | TLS/SSL certificate management (via MySQL utilities or OpenSSL) and documented authentication plugins for external identity systems; `authentication_webauthn` replaced `authentication_fido*` as of 8.4.0. | `[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html]`, `[Source: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html]` |
| MySQL ↔ AWS KMS / HashiCorp Vault | Integrates via | Documented Keyring backends for at-rest encryption key management. | `[Source: https://dev.mysql.com/doc/refman/9.7/en/security.html]` |
| MySQL ↔ JDBC / ODBC | Integrates via | Official Connector/J (JDBC) and Connector/ODBC implement the respective language-agnostic standards. | `[Source: https://dev.mysql.com/doc/refman/9.7/en/connectors-apis.html]` |
| MongoDB ↔ Mongoose / Prisma | Complementary | MongoDB's own docs list both as community-maintained libraries built on top of the official drivers, distinct from officially supported drivers. | `[Source: https://www.mongodb.com/docs/drivers/]` |
| MongoDB ↔ Docker | Complementary / Integrates via | Officially ships and documents the `mongodb/mongodb-atlas-local` image for local Atlas-compatible dev/test (Docker Desktop v4.31+ or Engine v27.0+), plus Enterprise Edition support. | `[Source: https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-deploy-docker/]` |
| MongoDB ↔ Go / Python / TypeScript | Integrates via | Officially develops and supports first-party drivers for these among 13 total. | `[Source: https://www.mongodb.com/docs/drivers/]` |
| MongoDB ↔ Apache Kafka | Integrates via | Officially maintained MongoDB Connector for Apache Kafka (Confluent-verified), usable as sink or source publishing change-stream events as Kafka topics. | `[Source: https://www.mongodb.com/docs/kafka-connector/current/]` |
| MongoDB ↔ Apache Spark | Integrates via | Officially maintained Connector for Apache Spark exposing Scala/Java/Python/R libraries, materializing MongoDB data as DataFrames/Datasets. | `[Source: https://www.mongodb.com/products/integrations/spark-connector]` |
| MongoDB ↔ Power BI / Tableau | Integrates via | Officially documented (Power BI: Microsoft-certified) connectors for Atlas enabling live-data querying / native BI features. | `[Source: https://www.mongodb.com/products/integrations/connectors]` |
| MongoDB ↔ Kubernetes / Terraform | Integrates via | Atlas Kubernetes Operator (managed) and separate on-premises Controllers for Kubernetes Operator; Atlas Terraform provider for IaC. (Both named as documented, though outside the 44-technology canonical list.) | `[Source: https://www.mongodb.com/docs/manual/installation/]` |
| Redis → Lua | Depends on | Redis's programmability model runs through an embedded, sandboxed Lua 5.1 interpreter — "Redis's only supported scripting engine" (EVAL/EVALSHA, Functions FUNCTION LOAD/FCALL). | `[Source: https://redis.io/docs/latest/develop/programmability/]` |
| Redis ↔ PostgreSQL | Complementary | Docs use PostgreSQL as the durability benchmark for combined RDB+AOF persistence ("comparable to what PostgreSQL can provide"), implying Redis commonly deploys alongside a durable primary store rather than as sole store. | `[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/]` |
| Redis ↔ Docker | Complementary / Integrates via | Official Docker image, documented minimal invocation, custom config via derived Dockerfile or bind-mounted directory, bind-mounted data volume for persistence; recommended environment to practice upgrades before production. | `[Source: https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/]` |
| Redis ↔ Kubernetes | Integrates via | Officially documented path is the Redis Enterprise operator (CRDs: REC, REDB, REAADB) targeting CNCF-conformant distributions, with quick-start, Helm, and OpenShift-specific options. | `[Source: https://redis.io/docs/latest/operate/kubernetes/]` |
| Redis ↔ Python / Go / TypeScript | Integrates via | First-party clients: `redis-py` (plus RedisVL for vector/AI workloads and an OM library) for Python; `go-redis` for Go; `node-redis`/`ioredis` for JS/TS, with a documented `ioredis` → `node-redis` migration guide reflecting `node-redis` as currently recommended. | `[Source: https://redis.io/docs/latest/develop/clients/]` |
| ClickHouse ↔ PostgreSQL | Complementary | Distinct official migration track: Postgres framed as OLTP, ClickHouse as OLAP; real-time CDC (ClickPipes or PeerDB) or manual bulk load recommended for moving analytical workloads. | `[Source: https://clickhouse.com/docs/migrations/postgresql/overview]` |
| ClickHouse ↔ MySQL | Complementary / Integrates via | ClickHouse implements MySQL wire-protocol compatibility (default port 3306 on Cloud, 9004 self-managed) so MySQL-only BI clients can connect; a dedicated migration track is referenced in site navigation. | `[Source: https://clickhouse.com/docs/interfaces/mysql]` |
| ClickHouse ↔ PostgreSQL (wire protocol) | Integrates via | Separate PostgreSQL wire-protocol emulation interface (default port 9005), plus a `postgresql` table function/engine for direct querying/bulk load and ClickPipes/PeerDB for CDC sync. | `[Source: https://clickhouse.com/docs/guides/sre/network-ports]` |
| ClickHouse ↔ MongoDB | Complementary | ClickHouse's own integration test suite is Docker-based and multi-container, testing clustered ClickHouse alongside MySQL, PostgreSQL, and MongoDB. | `[Source: https://clickhouse.com/docs/resources/develop-contribute/contribute/tests]` |
| ClickHouse ↔ Python / Go | Complementary / Integrates via | `chDB` (embedded ClickHouse engine) is documented as primarily for Python (Pandas/Arrow integration) but also supports Go, Rust, Node.js, and Bun. | `[Source: https://clickhouse.com/docs/get-started/about/deployment-modes]` |
| ClickHouse ↔ Apache ZooKeeper | Integrates via | ClickHouse Keeper, which coordinates data replication and distributed DDL, is described as compatible with the Apache ZooKeeper protocol/API. | `[Source: https://clickhouse.com/docs/architecture/introduction]` |
| ClickHouse ↔ Apache Arrow | Integrates via | Apache Arrow Flight support; `chDB` integrates with Arrow alongside Pandas; 26.8 changelog replaced the Arrow-library-based reader/writer with ClickHouse's native Arrow implementation. | `[Source: https://clickhouse.com/docs/interfaces/overview]` |
| ClickHouse ↔ gRPC | Integrates via | Custom gRPC protocol as an RPC-style network interface, dedicated port 9100. | `[Source: https://clickhouse.com/docs/interfaces/overview]` |
| ClickHouse ↔ Docker | Complementary / Integrates via | Official integration tests run ClickHouse in Docker-based, multi-container setups (network-partition/packet-drop emulation) alongside external systems. | `[Source: https://clickhouse.com/docs/resources/develop-contribute/contribute/tests]` |
| ClickHouse ↔ Kubernetes | Integrates via | A Kubernetes Operator for ClickHouse is documented as an official product (confirmed via a TLS-configuration sub-page). | `[Source: https://clickhouse.com — confirmed via a fetched TLS-configuration sub-page]` |
| ClickHouse ↔ Prometheus | Integrates via | Dedicated Prometheus metrics port (9363) documented among ClickHouse's default network ports. | `[Source: https://clickhouse.com/docs/guides/sre/network-ports]` |

---

## 4. Backend Frameworks

### 4.1 Express

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Express → Node.js | Depends on | "A fast, unopinionated, minimalist web framework for Node.js"; minimum version is major-line-specific (5.x requires ≥18, 4.x requires ≥0.10). | `[Source: https://expressjs.com/]` |
| Express → Node.js http/https | Depends on | `app.listen()` is documented shorthand for `http.createServer(app).listen(...)`; the http/https modules are needed directly only for running both HTTP and HTTPS servers or integrating with something like Socket.IO. | `[Source: https://expressjs.com/en/starter/hello-world.html]` |
| Express ↔ MongoDB / Mongoose | Complementary / Integrates via | Official database-integration guide covers connecting via the `mongodb` driver, recommending Mongoose as the ODM/object-model layer on top. | `[Source: https://expressjs.com/en/guide/database-integration.html]` |
| Express ↔ MySQL / PostgreSQL | Integrates via | Official guide documents connecting via the `mysql` driver and via `pg-promise`, respectively. | `[Source: https://expressjs.com/en/guide/database-integration.html]` |
| Express ↔ Redis | Complementary / Integrates via | Recommended distributed session store for clustered/load-balanced deployments (via the `redis` driver) and for distributed/response caching. | `[Source: https://expressjs.com/en/guide/database-integration.html]`, `[Source: https://expressjs.com/en/advanced/best-practice-performance.html]` |
| Express ↔ TypeScript | Complementary / Integrates via | TS project setup is documented (tsconfig, native `.ts` execution requirements) though Express's own runtime is plain JS; type-level integration via `@types/express`/`@types/node`, no first-party TS build tooling. | `[Source: https://expressjs.com/en/starter/installing.html]` |
| Express ↔ Socket.IO | Complementary / Integrates via | Docs note the http/https modules are needed directly if integrating with something like Socket.IO; Express-style HTTP middleware (e.g. `express-session`, `helmet`) is reused via `io.engine.use()` since v4.6.0. | `[Source: https://expressjs.com/en/starter/hello-world.html]` / `[Source: https://socket.io/docs/v4/middlewares/]` |
| Express ↔ Elasticsearch | Integrates via | Official database-integration guide documents connecting via the `elasticsearch` package. | `[Source: https://expressjs.com/en/guide/database-integration.html]` |
| Express ↔ Node.js diagnostics_channel | Integrates via | Can subscribe to HTTP lifecycle events (`http.server.request.start`, `http.server.response.finish`) without patching Express. | `[Source: https://expressjs.com/en/guide/debugging.html]` |
| Express ↔ GraphQL | Complementary / Integrates via | `graphql-js`'s getting-started path explicitly documents Express as the recommended next step for serving GraphQL over HTTP after the bare `graphql()` function example. | `[Source: https://www.graphql-js.org/docs/getting-started/]` |
| Express ↔ Jest | Complementary / Integrates via | Community integration guides pair Jest with Supertest for Express API testing. | `[Source: https://jestjs.io/docs/testing-frameworks]` |
| Express ↔ shadcn/ui | Integrates via | Used as one of two worked server-side registry-authentication examples (alongside Next.js) for private component registries. | `[Source: https://ui.shadcn.com/docs/registry/authentication]` |
| Express ↔ MUI | Complementary / Integrates via | Official SSR guide documents a from-scratch Express + Emotion server-rendering pattern (shared theme file, middleware rendering to string, `createEmotionServer` critical-CSS extraction, client hydration). | `[Source: https://mui.com/material-ui/guides/server-rendering/]` |

### 4.2 Fastify

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Fastify → Node.js | Depends on | Server factory wraps Node's core `http`, `https`, or `http2` modules (or a custom `serverFactory`); as of v5, Node.js v20+ required (v18 dropped). | `[Source: https://fastify.dev/docs/latest/Reference/Server/]` / `[Source: https://fastify.dev/docs/latest/Guides/Migration-Guide-V5/]` |
| Fastify → Ajv | Depends on | Schema-compilation layer uses Ajv v8 to compile JSON Schemas into optimized validation functions ahead of request handling; configurable via the `ajv` server option (`customOptions`, `plugins`). | `[Source: https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/]` |
| Fastify → fast-json-stringify | Depends on | Used to compile JSON Schemas into optimized serialization functions ahead of use. | `[Source: https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/]` |
| Fastify ↔ PostgreSQL / MySQL / MongoDB / Redis | Complementary / Integrates via | Official plugins: `@fastify/postgres` (`fastify.pg.query()`), `@fastify/mysql` (`fastify.mysql.query()`), `@fastify/mongodb` (`fastify.mongo.db.collection()`, with `migrate-mongo` cited as a compatible migration tool), `@fastify/redis` (`fastify.redis`). | `[Source: https://fastify.dev/docs/latest/Guides/Database/]` |
| Fastify ↔ Prisma / TypeORM / Knex | Complementary / Integrates via | Given as example ORMs/DB libraries wrapped via the documented custom-plugin pattern (`fastify.decorate()` plus an `onClose` hook). | `[Source: https://fastify.dev/docs/latest/Guides/Database/]` |
| Fastify ↔ TypeScript | Complementary | First-class generics-based typing (`RouteGenericInterface`) with types propagating into hooks; official type providers derive types from JSON Schemas. | `[Source: https://fastify.dev/docs/latest/Reference/TypeScript/]` |
| Fastify ↔ @fastify/express / @fastify/middie | Integrates via | Official plugins providing Express/Connect middleware interop via `fastify.use()`. | `[Source: https://fastify.dev/docs/latest/Reference/Middleware/]` |
| Fastify ↔ Pino | Integrates via | `logger`/`loggerInstance` options wire in Pino as Fastify's documented default logging library. | `[Source: https://fastify.dev/docs/latest/Guides/Debugging (Reference/Server + Reference/Warnings sections)]` |
| Fastify ↔ light-my-request | Integrates via | `fastify.inject()` is built on `light-my-request` for in-process HTTP simulation in tests. | `[Source: https://fastify.dev/docs/latest/Guides/Testing/]` |
| Fastify ↔ @fastify/aws-lambda / @h4ad/serverless-adapter | Integrates via | Integration options for running Fastify on AWS Lambda behind API Gateway. | `[Source: https://fastify.dev/docs/latest/Guides/Serverless/]` |
| Fastify ↔ OpenAPI / Swagger | Complementary / Integrates via | `@fastify/openapi`, `@fastify/swagger`, and `@fastify/swagger-ui` are listed among documentation-tooling plugins. | `[Source: https://fastify.dev/docs/latest/Guides/Ecosystem/]` |
| Fastify ↔ security plugins | Integrates via | `@fastify/helmet`, `@fastify/cors`, `@fastify/csrf-protection`, `@fastify/rate-limit`, `@fastify/jwt`, `@fastify/auth`, `@fastify/basic-auth`, `@fastify/bearer-auth`, `@fastify/passport`. | `[Source: https://fastify.dev/docs/latest/Guides/Ecosystem/]` |
| Fastify ↔ core plugins | Integrates via | `@fastify/cookie`, `@fastify/multipart`, `@fastify/formbody`, `@fastify/compress`, `@fastify/etag`, `@fastify/static`, `@fastify/http-proxy`, `@fastify/websocket`, `@fastify/sse`, `@fastify/autoload`, `@fastify/env`, `@fastify/session`, `@fastify/view`. | `[Source: https://fastify.dev/docs/latest/Guides/Ecosystem/]` |
| Fastify ↔ autocannon / undici | Integrates via | `autocannon` is the recommended first-party HTTP/1.1 load-testing tool; `undici` is named as a real HTTP client for driving a listening Fastify instance in tests. | `[Source: https://fastify.dev/docs/latest/Guides/Benchmarking/]` / `[Source: https://fastify.dev/docs/latest/Guides/Testing/]` |
| Fastify ↔ Docker | Complementary | Recommended serverless/production deployment targets (Google Cloud Run, AWS Fargate, Azure Container Instances) run Fastify as a standard container; Vercel has an official Fastify template. | `[Source: https://fastify.dev/docs/latest/Guides/Serverless/]` |

### 4.3 GraphQL

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| GraphQL (graphql-js) → Node.js | Depends on | The official JS/TS reference implementation requires Node.js 22, 24, 25, or 26+. | `[Source: https://www.graphql-js.org/upgrade-guides/v16-v17/]` |
| GraphQL → JSON | Depends on | Responses are serialized as JSON; the documented HTTP transport contract specifies a JSON request body (`{ query, variables?, operationName? }`) and JSON response shape. | `[Source: https://graphql.org/learn/execution/]` / `[Source: https://graphql.org/learn/serving-over-http/]` |
| GraphQL ↔ DataLoader | Integrates via | Facebook's batching/caching utility is the documented integration point for solving the N+1 problem at the resolver layer. | `[Source: https://graphql.org/learn/performance/]` |
| GraphQL ↔ Relay | Integrates via | Global Object Identification (`Node` interface + `node(id)`) and the Relay connection spec for cursor pagination are documented as built specifically for Relay client interoperability. | `[Source: https://graphql.org/learn/global-object-identification/]` / `[Source: https://graphql.org/learn/pagination/]` |
| GraphQL ↔ GraphiQL | Integrates via | The introspection API (`__schema`, `__type`) is documented as the basis for tools like GraphiQL and schema-aware codegen. | `[Source: https://graphql.org/learn/introspection/]` |
| GraphQL ↔ Redis | Complementary / Integrates via | For larger systems, request-scoped or external caches such as Redis are suggested as an additional caching layer. | `[Source: https://www.graphql-js.org/docs/going-to-production/]` |
| GraphQL ↔ Pino / Winston | Integrates via | Named as example structured-logging libraries for graphql-js observability. | `[Source: https://www.graphql-js.org/docs/going-to-production/]` |
| GraphQL ↔ Prometheus / OpenTelemetry | Integrates via | Named as example metrics/tracing integrations, connected via v17+ Node.js diagnostics-channel lifecycle events. | `[Source: https://www.graphql-js.org/docs/going-to-production/]` |
| GraphQL ↔ WebSocket | Integrates via | Subscriptions commonly use WebSockets (via community-maintained subprotocols) as a transport, though the spec does not mandate one. | `[Source: https://graphql.org/learn/subscriptions/]` |
| GraphQL ↔ REST | Integrates via | Common pattern: a GraphQL server whose root-field resolvers internally call existing REST endpoints, adopting GraphQL as a facade over legacy REST services. | `[Source: https://graphql.org/faq/]` |
| GraphQL ↔ TypeScript | Complementary | graphql-js ships TS type definitions targeting TypeScript 4.4+; the reference implementation's docs/ecosystem are JS/TS-centric. | `[Source: https://www.graphql-js.org/upgrade-guides/v16-v17/]` |
| GitHub ↔ GraphQL | Complementary / Integrates via | GitHub publishes a first-party GraphQL API alongside REST, with a dedicated REST-to-GraphQL migration guide, offering "more precise and flexible queries than the GitHub REST API." | `[Source: https://docs.github.com/en/graphql]` |
| MUI ↔ GraphQL | Not documented | Not mentioned in the researched Material UI documentation as an integration point. | `[Inference from mui.md, not an explicit doc statement]` |

---

## 5. Realtime Networking

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| WebSocket API → TCP | Depends on | RFC 6455 defines the WebSocket Protocol as providing full-duplex, bidirectional communication over a single TCP connection. | `[Source: https://www.rfc-editor.org/rfc/rfc6455.html]` |
| WebSocket API → HTTP | Depends on | Begins with an HTTP-compatible opening handshake (GET + `Upgrade: websocket`, answered by `101 Switching Protocols`) before switching to the framing protocol. | `[Source: https://www.rfc-editor.org/rfc/rfc6455.html]` |
| WebSocket API → TLS | Depends on | The `wss` URI scheme is TLS-encrypted (conventionally port 443); masking is required even over `wss` as a distinct wire-level protection, not a substitute for TLS confidentiality. | `[Source: https://www.rfc-editor.org/rfc/rfc6455.html]` |
| WebSocket API ↔ Node.js | Complementary / Integrates via | Node.js ships a browser-compatible global `WebSocket` client class as the official integration point for consuming WebSocket servers server-side (client-only — Node.js does not ship a built-in WebSocket server). MDN lists Node.js server libraries `ws`, Socket.IO, SocketCluster, WebSocket-Node, Total.js as illustrative options. | `[Source: https://nodejs.org/api/globals.html]` / `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API]` |
| WebSocket API ↔ Socket.IO | Complementary / Integrates via | Because RFC 6455/WHATWG don't mandate reconnection, exponential backoff, or delivery guarantees, production systems typically adopt a userland library such as Socket.IO layered on top. Listed by MDN as one illustrative Node.js-ecosystem implementation, not endorsed as official. | `[Inference from websocket-api.md, not an explicit doc statement]` / `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API]` |
| WebSocket API ↔ Python / Go | Integrates via | MDN lists Flask-SocketIO and Django Channels (Python) and Gorilla WebSocket (Go) as example server implementations. | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API]` |
| WebSocket API ↔ HTTP/2 | Integrates via | RFC 8441 defines WebSockets over HTTP/2 using Extended CONNECT and a `:protocol` pseudo-header, tunneling WebSocket framing inside a single HTTP/2 stream, gated by `SETTINGS_ENABLE_CONNECT_PROTOCOL`. | `[Source: https://www.rfc-editor.org/rfc/rfc8441.html]` |
| WebSocket API ↔ Content Security Policy | Integrates via | The `connect-src` CSP directive explicitly lists WebSocket among the APIs it controls; the constructor throws `SecurityError` if the target URL is blocked by CSP. | `[Source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/connect-src]` |
| Socket.IO → Node.js | Depends on | Server package requires Node.js; minimum supported version is Node.js 10 ("older versions are not supported anymore"), current LTS recommended. | `[Source: https://socket.io/docs/v4/server-installation/]` |
| Socket.IO → HTTP | Depends on | Engine.IO transport layer is built on HTTP long-polling as the initial, most broadly compatible connection method; handshake/upgrade occurs over HTTP/1.1. | `[Source: https://socket.io/docs/v4/how-it-works/]` |
| Socket.IO ↔ Redis | Complementary / Integrates via | Redis is the primary documented shared adapter for cross-process broadcasting in multi-server deployments, via `@socket.io/redis-adapter` (pub+sub client pairs, or sharded Pub/Sub on Redis 7.0+). | `[Source: https://socket.io/docs/v4/redis-adapter/]` |
| Socket.IO ↔ MongoDB / PostgreSQL | Complementary / Integrates via | Officially documented shared-adapter backends for multi-node deployments alongside Redis and cloud pub/sub services; MongoDB additionally supports connection state recovery (unlike the plain Redis Pub/Sub adapter). | `[Source: https://socket.io/docs/v4/using-multiple-nodes/]` / `[Source: https://socket.io/docs/v4/connection-state-recovery/]` |
| Socket.IO ↔ Express | Complementary / Integrates via | Express-style HTTP middleware (e.g. `express-session`, `helmet`) is reused via `io.engine.use()` since v4.6.0. | `[Source: https://socket.io/docs/v4/middlewares/]` |
| Socket.IO ↔ TypeScript | Complementary | First-class TS support since v3 (typed `ServerToClientEvents`/`ClientToServerEvents`/`InterServerEvents`/`SocketData` generics); the v4.0 rewrite is itself a full TypeScript rewrite; interfaces extended in v4.1.0/v4.4.0. | `[Source: https://socket.io/docs/v4/typescript/]` |
| Socket.IO ↔ Jest / Vitest | Integrates via | Official testing guide demonstrates the identical test pattern implemented in Jest, Vitest, Mocha, and Tape across CommonJS/ESM/TypeScript variants. | `[Source: https://socket.io/docs/v4/testing/]` |
| Socket.IO ↔ Google Cloud Load Balancer | Integrates via | Documented reverse-proxy/load-balancer integration with worked timeout and sticky-session configuration guidance. | `[Source: https://socket.io/docs/v4/reverse-proxy/]` / `[Source: https://socket.io/docs/v4/using-multiple-nodes/]` |
| Socket.IO ↔ Docker | Not fully documented (inferred) | Kubernetes nginx-ingress sticky-session configuration is documented for multi-node deployments, implying containerized scenarios, though not stated as a direct Docker doc. | `[Inference from socketio.md, not an explicit doc statement]` |
| WebRTC → TURN relay server | Depends on | "A server is required for relaying the traffic between peers" because a direct socket is often not possible due to NATs/firewalls; deployable self-hosted (e.g. coturn) or via a managed provider. | `[Source: https://webrtc.org/getting-started/turn-server]` |
| WebRTC → application-chosen signaling transport | Depends on | Signaling (SDP offer/answer, ICE candidate exchange) is explicitly not defined by the WebRTC spec; applications must supply their own transport. | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime]` |
| WebRTC → STUN/TURN/ICE | Depends on | ICE (with STUN for server-reflexive candidates, TURN for relay candidates) is a key building block for NAT traversal and connection establishment. | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API]` |
| WebRTC → DTLS-SRTP | Depends on | The spec mandates DTLS-SRTP for media transport as a non-optional security requirement. | `[Source: https://www.w3.org/TR/webrtc/]` |
| WebRTC → Media Capture and Streams API | Depends on / Integrates via | Camera/microphone access is governed by the separate Media Capture and Streams API's permission model; `navigator.mediaDevices.getUserMedia()`/`getDisplayMedia()` feed media into MediaStreams attached to a peer connection. | `[Source: https://www.w3.org/TR/webrtc/]` / `[Source: https://webrtc.org/getting-started/overview]` |
| WebRTC ↔ WebSocket API | Complementary / Integrates via | Documented as one common signaling transport for exchanging SDP/ICE messages; MDN's worked signaling example uses a WebSocket-based Node.js signaling server. | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API]` |
| WebRTC ↔ Web Workers | Complementary / Integrates via | Integrates with Web Workers/`TransformStream` for the Encoded Transforms (insertable streams) feature (`RTCRtpScriptTransform`, `RTCEncodedVideoFrame`/`RTCEncodedAudioFrame`), processing encoded frame data off the main thread. | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API]` |
| WebRTC ↔ SIP / XMPP | Integrates via | Noted as alternative signaling protocols/services an application could use instead of a custom WebSocket signaling server, though not detailed in the guide. | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling]` |
| WebRTC ↔ coturn | Integrates via | Named as a self-hosted TURN relay implementation option in the official getting-started TURN-server guide. | `[Source: https://webrtc.org/getting-started/turn-server]` |
| WebRTC ↔ adapter.js / webrtc-adapter | Integrates via | Official WebRTC-org GitHub shim insulating applications from spec changes and cross-browser prefix differences; the repo is now a read-only fork, distributed as the `webrtc-adapter` npm package. | `[Source: https://github.com/webrtc/adapter]` |

---

## 6. API Spec Tooling (OpenAPI / Swagger)

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| OpenAPI → JSON Schema (draft 2020-12) | Depends on | Since OAS 3.1.0, Schema Objects use full JSON Schema draft 2020-12 semantics (declarable via `jsonSchemaDialect`); 3.0.x used a JSON-Schema-like but not fully compliant subset. | `[Source: https://spec.openapis.org/oas/v3.1.0.html]` |
| OpenAPI → HTTP (and HTTP-like protocols) | Depends on | OAS is a format for describing HTTP-based and HTTP-like remote APIs (e.g. WebSocket, CoAP) rather than being protocol-agnostic. | `[Source: https://learn.openapis.org/introduction.html]` |
| OpenAPI ↔ Swagger | Depends on (Swagger side) / Integrates via | Swagger UI/Editor/Codegen consume an OpenAPI-compliant (or legacy Swagger 2.0-compliant) definition document as required input — they visualize/act on the spec, not define it. OAS was itself derived from the donated Swagger 2.0 spec, maintained separately as OpenAPI by the OAI since 2016. | `[Source: https://github.com/swagger-api/swagger-ui]` / `[Source: https://learn.openapis.org/introduction.html]` |
| OpenAPI ↔ Overlay Specification | Integrates via | OAI's own companion spec (v1.0.0, 2024-10-17) for non-invasively layering JSONPath-driven changes onto an OpenAPI Description without editing the source document. | `[Source: https://spec.openapis.org/overlay/v1.0.0.html]` |
| OpenAPI ↔ Arazzo Specification | Integrates via | OAI's own companion spec (v1.0.1, 2025-01-16) for describing multi-step API workflows built on top of one or more OpenAPI descriptions. | `[Source: https://spec.openapis.org/arazzo/v1.0.1.html]` |
| OpenAPI ↔ OAuth2 / OpenID Connect | Integrates via | Security Scheme Object supports `oauth2` (multiple flows/grant types, plus Device Authorization Flow in 3.2.0) and `openIdConnect` (discovery-document based) under `components.securitySchemes`. | `[Source: https://learn.openapis.org/specification/security.html]` |
| OpenAPI ↔ GitHub Actions | Complementary | Best-practices guidance recommends wiring the OpenAPI Description into automated CI processes, e.g. verifying implementation code and description stay consistent. | `[Source: https://learn.openapis.org/best-practices.html]` |
| Swagger → React | Depends on | Swagger UI v4.0.0 requires React 17.x (and Redux 4.x) as an underlying dependency. | `[Source: https://github.com/swagger-api/swagger-ui/releases/tag/v4.0.0]` |
| Swagger → Node.js | Depends on | Swagger Editor requires Node.js ≥12.22.0 minimum to install/build (≥24.18.0 recommended). | `[Source: https://github.com/swagger-api/swagger-editor]` |
| Swagger ↔ React | Complementary | `swagger-ui-react` is an official npm package providing a React component wrapper for embedding Swagger UI. | `[Source: https://github.com/swagger-api/swagger-ui]` |
| Swagger ↔ Docker | Complementary | Swagger UI, Editor, and Codegen each publish official pre-built Docker images (`docker.swagger.io/swaggerapi/swagger-ui`) as a documented deployment path. | `[Source: https://swagger.io/docs/open-source-tools/swagger-ui/usage/installation/]` |
| Swagger ↔ GitHub Actions | Complementary / Integrates via | Swagger Codegen documents CI integration via GitHub Actions workflows (alongside Maven/Gradle) for auto-generating SDKs/stubs. | `[Source: https://github.com/swagger-api/swagger-codegen/blob/master/README.md]` |
| Swagger ↔ TypeScript | Complementary | Documented supported output language for Swagger Codegen's client-SDK generation. | `[Source: https://github.com/swagger-api/swagger-codegen/blob/master/README.md]` |
| Swagger ↔ OAuth2 providers | Integrates via | Swagger UI's `initOAuth()` integrates with external OAuth2 identity providers/authorization servers for the "Authorize" button flow (authorization-code grant with optional PKCE; Basic-auth token exchange). | `[Source: https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/]` |
| Swagger ↔ DOMPurify | Integrates via | Swagger UI uses DOMPurify for markdown sanitization; patch v5.32.15 scoped the DOMPurify instance to avoid mutating global state on a host page. | `[Source: https://github.com/swagger-api/swagger-ui/releases (v5.32.15 entry, 2026-09-04)]` |
| Swagger ↔ Maven / webpack / highlight.js / Scarf | Integrates via | Codegen built/packaged via Maven (separate group IDs for 2.x/3.x lines); Editor bundled with webpack; UI's `syntaxHighlight.theme` selects a highlight.js theme (default "agate"); Editor optionally reports analytics via Scarf. | `[Source: https://github.com/swagger-api/swagger-codegen]`, `[Source: https://github.com/swagger-api/swagger-editor]`, `[Source: https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/]` |

---

## 7. Styling & UI Component Libraries

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Sass → Dart | Depends on | Dart Sass (the reference implementation) runs on the Dart VM for speed and can also be compiled to pure JavaScript. | `[Source: https://sass-lang.com/dart-sass/]` |
| Sass ↔ Node.js | Integrates via | npm packages `sass` (pure JS compiled from Dart) and `sass-embedded` (native Dart VM subprocess) expose a modern JS API and a legacy Node-Sass-compatible API. | `[Source: https://sass-lang.com/dart-sass/]` |
| Sass ↔ Go / Java / Ruby / Rust / .NET | Integrates via | Official/community wrapper packages for the language-agnostic Embedded Sass protocol exist for these languages, letting other runtimes talk directly to the Dart VM for compilation. | `[Source: https://sass-lang.com/dart-sass/]` |
| Sass ↔ Vite | Integrates via | Vite's built-in Sass preprocessing is a real integration point, maintained and documented by the Vite project itself, not officially documented on sass-lang.com. | `[Source: sass.md §16 Integration]` |
| Sass ↔ Gradle / Maven | Integrates via | Community-maintained Java bindings include Gradle and Maven plugins for build integration. | `[Source: https://sass-lang.com/install/]` |
| Tailwind CSS → Lightning CSS | Depends on | Tailwind v4 delegates CSS nesting flattening and other output normalization internally to Lightning CSS — the explicit reason Sass/Less/Stylus-style nesting is unnecessary in v4. | `[Source: https://tailwindcss.com/docs/compatibility]` |
| Tailwind CSS → Node.js | Depends on | The official v3→v4 upgrade codemod (`npx @tailwindcss/upgrade`) requires Node.js 20+ (standalone CLI ships prebuilt native binaries and does not strictly require Node.js otherwise). | `[Source: https://tailwindcss.com/docs/upgrade-guide]` |
| Tailwind CSS → modern browser CSS engine support | Depends on | v4.0 requires browsers supporting `@property` and `color-mix()`: Safari 16.4+, Chrome 111+, Firefox 128+; teams needing older-browser support must stay on v3.4. | `[Source: https://tailwindcss.com/docs/upgrade-guide]` |
| Tailwind CSS ↔ Vite | Complementary / Integrates via | `@tailwindcss/vite` is described as the tightest/most-performant first-party integration path, underlying several framework guides (SvelteKit, Nuxt, SolidJS, React Router). | `[Source: https://tailwindcss.com/docs/installation/using-vite]` |
| Tailwind CSS ↔ PostCSS | Integrates via | `@tailwindcss/postcss` is the official PostCSS plugin (replacing v3's `tailwindcss` + separate `autoprefixer` entries), used by PostCSS-centric build tools such as Next.js and Angular. | `[Source: https://tailwindcss.com/docs/installation/using-postcss]` |
| Tailwind CSS ↔ Next.js / Angular / Nuxt | Complementary / Integrates via | Each has an official first-party Tailwind installation guide; Next.js/Angular fit the `@tailwindcss/postcss` path, Nuxt builds on `@tailwindcss/vite`; a dedicated `@tailwindcss/turbopack` package is in active development for Next.js's Turbopack bundler. | `[Source: https://tailwindcss.com/docs/installation/using-postcss]`, `[Source: https://tailwindcss.com/docs/installation/using-vite]`, `[Source: https://github.com/tailwindlabs/tailwindcss (Unreleased CHANGELOG section, retrieved 2026-09-09)]` |
| Tailwind CSS ↔ React | Complementary | Extracting framework components (docs' example uses a React `VacationCard` component) is the officially preferred mechanism for reusable UI patterns over custom CSS classes. | `[Source: https://tailwindcss.com/docs/components/registration]` |
| Tailwind CSS ↔ Vue | Complementary | Official first-party Tailwind installation guide for Nuxt (Vue-based); Vue SFC `<style>` blocks are a documented (if not primary) integration point via `@reference`. | `[Source: https://tailwindcss.com/docs/installation/framework-guides]` |
| Tailwind CSS ↔ Prettier | Integrates via | `prettier-plugin-tailwindcss` is the official Prettier plugin for automatic utility class-order sorting. | `[Source: https://github.com/tailwindlabs/prettier-plugin-tailwindcss]` |
| Tailwind CSS ↔ VS Code | Integrates via | `bradlc.vscode-tailwindcss` is the official IntelliSense extension (autocomplete, linting, hover previews of compiled CSS); also works in Cursor, with Zed/JetBrains having their own built-in support. | `[Source: https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss]` |
| Tailwind CSS ↔ Docker | Complementary / Integrates via | The standalone CLI's prebuilt native (including musl/Linux-compatible) binaries remove a Node.js runtime dependency, relevant for minimal container images. | `[Source: https://tailwindcss.com/docs/installation/tailwind-cli]` |
| MUI → React | Depends on | Material UI is a React component library; documented peer dependency support for React 17.0.0+, 18.0.0+, 19.0.0+; all components ship as React Client Components (`'use client'`). | `[Source: https://mui.com/material-ui/getting-started/installation/]` |
| MUI ↔ Emotion | Integrates via | Default CSS-in-JS styling engine (`@emotion/react` + `@emotion/styled`), used natively for `css()`/`styled()` and theme sharing; required for SSR compatibility. | `[Source: https://mui.com/material-ui/getting-started/installation/]` |
| MUI ↔ styled-components | Integrates via | Documented alternative styling engine via the `@mui/styled-engine-sc` adapter package, recommended to cut bundle size in non-SSR apps. | `[Source: https://mui.com/material-ui/getting-started/installation/]` |
| MUI ↔ Next.js | Complementary / Integrates via | `AppRouterCacheProvider` (App Router) or `AppCacheProvider` (Pages Router) from `@mui/material-nextjs` streams Emotion CSS to avoid FOUC; Next.js 13.5+ auto-applies `optimizePackageImports` for MUI. | `[Source: https://mui.com/material-ui/integrations/nextjs/]` |
| MUI ↔ Tailwind CSS | Complementary / Integrates via | Documented interoperability: disable Tailwind's preflight, configure `'important'`, adjust CSS injection order via `StyledEngineProvider` to use Tailwind v3 alongside MUI. | `[Source: https://mui.com/material-ui/integrations/interoperability/]` |
| MUI ↔ TypeScript | Integrates via | TS module augmentation is the documented mechanism for extending `Theme`/`ThemeOptions` types; minimum supported TypeScript raised to v4.9 in the v7 migration. | `[Source: https://mui.com/material-ui/getting-started/installation/]` |
| shadcn/ui → Tailwind CSS | Depends on | shadcn/ui's architecture is a CLI tool + a registry protocol + Tailwind CSS as the styling engine, with CSS variables as the theming layer — components are plain styled `.tsx` files, not a runtime UI package. | `[Source: https://ui.shadcn.com/docs]` |
| shadcn/ui → React | Depends on (inferred) | Distributes React (`.tsx`) component source; framework guides, the React 18→19 migration section, and `forwardRef`/`data-slot` patterns presuppose a React host, though no single sentence states "requires React." | `[Inference from shadcn-ui.md, not an explicit doc statement]` |
| shadcn/ui → Base UI / Radix UI | Depends on | As of July 2026, newly scaffolded projects default to Base UI as the underlying headless-primitive library; Radix UI (the long-standing pre-July-2026 default) remains fully supported via `shadcn init -b radix`. | `[Source: https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default]` |
| shadcn/ui ↔ React Hook Form / Zod | Complementary / Integrates via | Officially documented forms pattern combines React Hook Form (`useForm`, `<Controller>`) with Zod validation via `zodResolver`, composed with shadcn's own `<Field>` component system. | `[Source: https://ui.shadcn.com/docs/forms/react-hook-form]` |
| shadcn/ui ↔ TanStack Form / Formisch | Integrates via | Listed alongside React Hook Form as documented form-integration targets. | `[Source: https://ui.shadcn.com/docs/components]` |
| shadcn/ui ↔ Next.js / Vite / TanStack Start / Laravel / React Router / Astro | Complementary / Integrates via | Officially documented framework integrations, each with a dedicated install guide. | `[Source: https://ui.shadcn.com/docs/installation]` |
| shadcn/ui ↔ Express | Integrates via | One of two worked server-side registry-authentication examples (alongside Next.js) for private component registries. | `[Source: https://ui.shadcn.com/docs/registry/authentication]` |
| shadcn/ui ↔ Turborepo | Complementary / Integrates via | Officially documented/scaffolded monorepo build tool, splitting a shared `packages/ui` workspace from app-level workspaces. | `[Source: https://ui.shadcn.com/docs/monorepo]` |
| shadcn/ui ↔ GitHub | Complementary / Integrates via | Component/design-system registries can be hosted directly from a GitHub repository ("GitHub Registries"); private repos supported via authenticated URLs since August 2026. | `[Source: https://ui.shadcn.com/docs/registry/github]` |
| shadcn/ui ↔ Model Context Protocol (MCP) / Claude Code | Integrates via | Ships an MCP server so AI coding agents can browse, search, and install components via natural language, configured via `shadcn mcp init --client <name>`; documented client integration for Claude Code writes `.mcp.json`. | `[Source: https://ui.shadcn.com/docs/mcp]` |
| shadcn/ui ↔ Vercel AI SDK | Integrates via | `@shadcn/helpers/ai-sdk` lets developers script deterministic chat conversations through `useChat` with no live model or network calls. | `[Source: https://ui.shadcn.com/docs/helpers/ai-sdk]` |
| CSS ↔ Web Components | Integrates via | Explicit style-encapsulation boundaries around Shadow DOM via `:host`, `:host()`, `:host-context()`, `::slotted()`, the `part`/`exportparts` HTML attributes, and `::part()`. | `[Source: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_shadow_parts]` |
| CSS ↔ web-platform-tests (WPT) / W3C CSS Validator / Firefox DevTools | Integrates via | CSS WG conformance tests live inside the shared WPT repo (primarily `css/`); the W3C Validator is MDN's recommended first-line syntax checker; Firefox DevTools is the reference implementation for MDN's CSS debugging workflow (Rules view, Layout view, live editing, Grid Inspector). | `[Source: https://web-platform-tests.org/test-suite-design.html]`, `[Source: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Debugging_CSS]` |
| HTML ↔ SVG / MathML | Integrates via | Both are foreign-content namespaces embeddable directly in an HTML document; the infrastructure spec references the SVG namespace as a dependency of the HTML namespace model. | `[Source: https://html.spec.whatwg.org/multipage/infrastructure.html#html-vs-xhtml]` |
| HTML ↔ WebAssembly | Integrates via | HTML's module script processing model documents module types for CSS, JSON, text, and WebAssembly beyond plain JS modules. | `[Source: https://html.spec.whatwg.org/multipage/webappapis.html]` |
| HTML ↔ Web Components (Custom Elements API) | Integrates via | `customElements.define()` lets author/framework-defined elements participate in the same DOM tree, lifecycle, and form-submission model as native elements — the extension point most JS frameworks/design systems use to add custom tags. | `[Source: https://html.spec.whatwg.org/multipage/custom-elements.html]` |
| HTML ↔ Content Security Policy / DOMPurify / HTML Sanitizer API | Integrates via | CSP is HTTP-header-driven and cross-referenced by MDN's HTML-security guidance as layered XSS defense; MDN names DOMPurify ("recommended by many experts including OWASP") for sanitizing untrusted HTML; the HTML Sanitizer API is a purpose-built browser alternative/complement. | `[Source: https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS]`, `[Source: https://developer.mozilla.org/en-US/docs/Web/API/HTML_Sanitizer_API]` |
| HTML ↔ Nu Html Checker (v.Nu) | Integrates via | The documented conformance-checking tool for HTML — web UI, bookmarklet, CLI, Grunt/Gulp plugins. | `[Source: https://validator.w3.org/nu/about.html]` |

---

## 8. Testing Tools

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Jest → Node.js | Depends on | Jest 30.5.1's `engines.node` is `^18.14.0 \|\| ^20.0.0 \|\| ^22.0.0 \|\| >=24.0.0`; runs as a Node.js CLI/process, worker pool (`jest-worker`) spawns Node worker processes. | `[Source: https://registry.npmjs.org/jest]` |
| Jest ↔ React / Vue / Angular | Complementary | Documented as working with all three; React via React Testing Library guides, Vue via its official testing tooling as a community path, Angular as a community alternative to Karma. | `[Source: https://jestjs.io/docs/getting-started]` / `[Source: https://jestjs.io/docs/testing-frameworks]` |
| Jest ↔ TypeScript | Complementary / Integrates via | Supported via Babel's TS preset (type-stripping only) or the community `ts-jest` package (which type-checks). | `[Source: https://jestjs.io/docs/getting-started]` |
| Jest ↔ Express | Complementary / Integrates via | Community guides pair Jest with Supertest for Express API testing. | `[Source: https://jestjs.io/docs/testing-frameworks]` |
| Jest ↔ Next.js | Complementary | Jest docs link to Next.js's own official Jest setup docs as a first-party-adjacent integration. | `[Source: https://jestjs.io/docs/testing-frameworks]` |
| Jest ↔ Babel | Integrates via | First-party default transform: `babel-jest` used automatically when a Babel config exists, `babel-preset-jest` injecting the `jest.mock()` hoisting plugin (`babel-plugin-jest-hoist`) unless `excludeJestPreset` is set. | `[Source: https://jestjs.io/docs/code-transformation]` |
| Jest ↔ webpack | Integrates via | Documents explicit config-mapping from webpack concepts (`resolve.extensions`, `resolve.modules`, `resolve.roots`, `resolve.alias`) to Jest equivalents (`moduleFileExtensions`, `moduleDirectories`, `modulePaths`, `moduleNameMapper`). | `[Source: https://jestjs.io/docs/webpack]` |
| Jest ↔ ESLint | Integrates via | `eslint-plugin-jest` referenced for enforcing snapshot-size limits (`no-large-snapshots`) and auto-fixing deprecated matcher aliases (`no-alias-methods`). | `[Source: https://jestjs.io/docs/snapshot-testing]` / `[Source: https://jestjs.io/blog/2025/06/04/jest-30]` |
| Jest ↔ jsdom | Integrates via | `testEnvironment: 'jsdom'` is a pluggable environment via `jest-environment-jsdom` (not bundled by default since v27); Jest 30 upgraded jsdom 21→26. | `[Source: https://jestjs.io/docs/configuration]` / `[Source: https://jestjs.io/blog/2025/06/04/jest-30]` |
| Jest ↔ VS Code / Chrome DevTools / WebStorm | Integrates via | VS Code: `attach` launch config (port 9229) or auto-launch running `--inspect-brk --runInBand`; Chrome DevTools: same flags, attach via `chrome://inspect`; WebStorm: built-in support. | `[Source: https://jestjs.io/docs/troubleshooting]` |
| Jest ↔ jest-codemods | Integrates via | Community tool (built on `jscodeshift`) that transforms existing test code when migrating to Jest from Jasmine, Mocha, AVA, Chai, Sinon, Tape, etc. | `[Source: https://jestjs.io/docs/migration-guide]` |
| Mongoose ↔ Jest | Complementary / Integrates via | Explicit official compatibility caveats page (`testEnvironment: 'node'`, avoid fake timers, avoid `globalSetup` for DB connections, `resetModules: false`); Mocha officially recommended as the alternative test runner. | `[Source: https://mongoosejs.com/docs/jest.html]` |
| Mongoose ↔ mongodb-memory-server / run-rs | Integrates via | Recommended for local testing of replica-set-dependent features like change streams and transactions. | `[Source: https://mongoosejs.com/docs/change-streams.html]` |
| Prisma ↔ Jest | Complementary / Integrates via | Recommended unit-testing stack (Jest + `ts-jest`) with `jest-mock-extended` (^2.0.4) for deep-mocking `PrismaClient`. | `[Source: https://www.prisma.io/docs/orm/prisma-client/testing/unit-testing]` |
| Vitest → Vite | Depends on | Layered directly on top of Vite, sharing its plugin API and module transformation pipeline instead of reimplementing a separate transform/resolve step; Vitest 5.0 requires Vite ≥6.4.0. | `[Source: https://vitest.dev/guide/why.html]` / `[Source: https://vitest.dev/guide/]` |
| Vitest → Node.js | Depends on | Vitest 5.0 requires Node.js ≥22.12.0. | `[Source: https://vitest.dev/guide/]` |
| Vitest ↔ Playwright | Complementary / Integrates via | Playwright is the recommended Browser Mode automation provider for running Vitest tests in real browsers (parallel across chromium/firefox/webkit). | `[Source: https://vitest.dev/guide/browser/]` |
| Vitest ↔ Jest | Integrates via | Documents an explicit API-compatibility and migration mapping (`expect` API, `jest.mock`→`vi.mock`, `jest.requireActual`→`vi.importActual`, etc.). | `[Source: https://vitest.dev/guide/migration/jest.html]` |
| Vitest ↔ React / Vue | Complementary / Integrates via | Component testing for both via Browser Mode, requiring a framework-specific plugin (`vitest-browser-vue` for Vue, now async in v5.0). | `[Source: https://vitest.dev/guide/features.html]` / `[Source: https://vitest.dev/guide/browser/]` / `[Source: https://vitest.dev/guide/migration.html]` |
| Vitest ↔ TypeScript | Complementary | Out-of-the-box TS support plus dedicated type testing (`expectTypeOf`/`assertType` via `expect-type`) to catch type regressions. | `[Source: https://vitest.dev/guide/features.html]` |
| Vitest ↔ GitHub | Integrates via | Official Vitest VS Code extension source is hosted at `github.com/vitest-dev/vscode`; Vitest's own source/releases at `github.com/vitest-dev/vitest`. | `[Source: https://vitest.dev/guide/ide.html]` |
| Playwright → Node.js | Depends on | Documents required Node.js support as "latest 22.x, 24.x or 26.x"; Node.js/TypeScript docs are the primary/reference implementation. | `[Source: https://playwright.dev/docs/intro]` |
| Playwright ↔ TypeScript | Complementary / Integrates via | Auto-discovers `tsconfig.json`/`jsconfig.json` (restricted option subset), transforms TS to JS at runtime (no type-checking — running `tsc` separately is the documented complement for type safety). | `[Source: https://playwright.dev/docs/test-typescript]` |
| Playwright ↔ Docker | Complementary / Integrates via | Official per-Ubuntu-codename images (`mcr.microsoft.com/playwright`) for both local containerized runs and a network-addressable remote Playwright Server mode. | `[Source: https://playwright.dev/docs/docker]` |
| Playwright ↔ GitHub Actions | Complementary / Integrates via | Documented CI integration; a built-in `github` reporter produces GitHub Actions annotations. | `[Source: https://playwright.dev/docs/test-reporters]` / `[Source: https://playwright.dev/docs/ci]` |
| Playwright ↔ React / Vue | Complementary / Integrates via | Component testing officially supports mounting and testing both via `fixtures.mount()` in the stable component-testing model. | `[Source: https://playwright.dev/docs/test-components]` |
| Playwright ↔ Model Context Protocol (MCP) | Integrates via | Playwright MCP server (`@playwright/mcp`) exposes browser automation as an MCP server for LLM agents, installable for MCP-compatible clients including VS Code, Cursor, Windsurf, and Claude Desktop. | `[Source: https://playwright.dev/mcp/introduction]` |
| Nuxt ↔ Vitest / Playwright / Jest | Complementary / Integrates via | `@nuxt/test-utils` configures Vitest specifically for Nuxt-runtime unit tests via `defineVitestProject`; Playwright has a first-class `@nuxt/test-utils/playwright` integration with a `createPage(url)` helper; Jest, Vitest, Cucumber, and Playwright are all supported E2E runners via `setup()`. | `[Source: https://nuxt.com/docs/4.x/getting-started/testing]` |
| Vue ↔ Vitest / Playwright / Cypress / Jest | Complementary / Integrates via | Vitest ("created and maintained by members of the Vue / Vite team") is the official unit/component recommendation; Playwright is an official E2E recommendation (cross-browser, praised for debugging); Cypress is named for both component testing and E2E with a graphical UI; Jest is only a community alternative via a `vite-jest` adapter. | `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |

---

## 9. Containerization & CI/CD

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Docker → containerd | Depends on | Under the `dockerd` daemon, Docker Engine uses containerd to manage the container lifecycle (create/start/stop). | `[Source: https://docs.docker.com/engine/daemon/alternative-runtimes/]` |
| Docker → runc | Depends on | containerd by default uses `runc` as the low-level OCI-runtime-spec implementation that actually creates and runs containers. | `[Source: https://docs.docker.com/engine/daemon/alternative-runtimes/]` |
| Docker → Linux kernel | Depends on | Isolation is built from kernel primitives — namespaces (pid, net, ipc, mnt, uts; present since ~kernel 2.6.15–2.6.26) and cgroups (since kernel 2.6.24); the daemon documents a minimum kernel version of 3.10. | `[Source: https://docs.docker.com/engine/security/]` / `[Source: https://docs.docker.com/engine/daemon/troubleshoot/]` |
| Docker ↔ GitHub Actions | Complementary / Integrates via | First-party actions: `docker/build-push-action`, `docker/setup-buildx-action`, `docker/login-action`, `docker/metadata-action`, `docker/setup-qemu-action`, plus Buildx Bake support for multi-target build configs. | `[Source: https://docs.docker.com/build/ci/github-actions/]` |
| Docker ↔ Testcontainers | Complementary / Integrates via | Documented pattern for writing integration tests against real dependency containers (databases, message brokers) rather than mocks, with a companion Testcontainers Cloud product for remote execution. | `[Source: https://docs.docker.com/testcontainers/]` / `[Source: https://docs.docker.com/guides/testcontainers-cloud/]` |
| Docker ↔ Kubernetes | Integrates via | Docker Desktop offers an integrated single-node Kubernetes cluster as an alternative orchestration target to Swarm. | `[Source: https://docs.docker.com/engine/swarm/]` |
| Docker ↔ Go / Python | Integrates via | An official Docker Engine API SDK is documented for both Go and Python (with automatic API-version negotiation for Go); Docker Compose V2 is written in Go, Compose V1 (now superseded) was Python-based. | `[Source: https://docs.docker.com/engine/api/]` / `[Source: https://docs.docker.com/compose/migrate/]` |
| Docker ↔ Docker Scout | Integrates via | Integrates with Docker Hub repositories for automatic image analysis, `docker scout` CLI subcommands, and Docker Hardened Images scanning. | `[Source: https://docs.docker.com/scout/]` |
| Docker ↔ AppArmor / SELinux / GRSEC / TOMOYO | Integrates via | Namespace/cgroup/capability isolation is documented as compatible with and layered on top of host Linux Security Modules and mandatory access control frameworks. | `[Source: https://docs.docker.com/engine/security/]` |
| Docker ↔ Wasmtime / gVisor / Kata Containers / youki | Integrates via | Alternative container runtimes integrate at the containerd-shim layer, selectable via `docker run --runtime` without daemon reconfiguration; `youki` (a Rust runc reimplementation) requires explicit daemon reconfiguration as it is not a native containerd-shim runtime. | `[Source: https://docs.docker.com/engine/daemon/alternative-runtimes/]` |
| Docker ↔ QEMU | Integrates via | Used for multi-platform build emulation (no Dockerfile changes, but slower than native) and Apple Silicon emulation of non-native-ARM64 images. | `[Source: https://docs.docker.com/build/building/multi-platform/]` / `[Source: https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/known-issues/]` |
| Docker ↔ syslog / journald / fluentd / Splunk / AWS CloudWatch / Google Cloud Logging | Integrates via | External log aggregation integrates via documented Docker logging drivers (syslog, journald, gelf, fluentd, awslogs, splunk, gcplogs, Windows etwlogs), configurable daemon-wide or per-container. | `[Source: https://docs.docker.com/engine/logging/configure/]` |
| GitHub Actions → GitHub | Depends on | Workflows are YAML files checked into `.github/workflows` and picked up by GitHub's Actions service on a matching repository/GitHub event — the product is inseparable from a GitHub repo. | `[Source: https://docs.github.com/en/actions/get-started/understand-github-actions]` |
| GitHub Actions → Node.js | Depends on | JavaScript actions declare `runs.using` as `node20` or `node24` — custom JS actions execute on a specific Node.js runtime version shipped by the runner. | `[Source: https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions]` |
| GitHub Actions → Docker | Depends on | Docker container actions (`using: docker`) require a Dockerfile or registry image reference to run the action. | `[Source: https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions]` |
| GitHub Actions ↔ GitHub | Complementary | Integrates natively with repository secrets/variables, branch protection/rulesets (as required-check gates), Environments, Packages (shared artifact/cache storage billing), code scanning, and Dependabot-triggered workflows. | `[Source: https://docs.github.com/en/actions]` |
| GitHub Actions ↔ AWS / Azure / GCP / HashiCorp Vault | Integrates via | GitHub documents OIDC-based integration patterns for each, enabling credential-free cloud deployment from workflows. | `[Source: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect]` |
| GitHub Actions ↔ VS Code | Integrates via | `github/local-action` is documented as usable in VS Code for running and debugging a custom JavaScript action locally. | `[Source: https://github.com/github/local-action]` |
| GitHub Actions ↔ npm | Integrates via | The Actions Toolkit (`@actions/core`, `@actions/github`, etc.) is published as npm packages under `actions/toolkit` for JS action authors. | `[Source: https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions]` |
| GitHub → Git | Depends on (inferred) | GitHub's repository/branch/fork/clone/merge/pull-request model and SSH-key authentication ("a secure channel over an unsecured network") are fundamentally Git concepts, though the doc does not state "GitHub requires Git" verbatim. | `[Inference from github.md, not an explicit doc statement]` |
| GitHub ↔ Docker | Complementary / Integrates via | GitHub Packages supports Docker/OCI container images as one of its per-registry publishing targets. | `[Source: https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages]` |
| GitHub ↔ npm | Integrates via | GitHub Packages supports npm publishing via `package.json`, and `GITHUB_TOKEN`/personal access tokens with `read:packages` scope for auth. | `[Source: https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages]` |
| GitHub ↔ smee.io / smee-client | Integrates via | Documented local webhook development pattern: smee.io as a public proxy URL plus the `smee-client` npm package to forward deliveries to a local dev server. | `[Source: https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/testing-webhooks]` |
| GitHub ↔ GitHub CLI | Integrates via | Documented as the recommended tool (over the API) for running GitHub Enterprise Importer migrations for most users. | `[Source: https://docs.github.com/en/migrations/using-github-enterprise-importer/understanding-github-enterprise-importer/about-github-enterprise-importer]` |
| GitHub ↔ CodeQL | Integrates via | Code scanning's default/advanced setup uses CodeQL analysis, plus supports third-party SARIF upload. | `[Source: https://docs.github.com/en/code-security]` |
| GitHub ↔ Git LFS | Integrates via | Recommended for tracking large binary files instead of committing them directly, required beyond the 100 MiB hard-block threshold for pushes; has its own separate rate limits (300/min unauthenticated, 3,000/min authenticated). | `[Source: https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories]` |
| GitHub ↔ Docker (webhooks/Deployments API) | Complementary | Webhooks/Deployments API are documented as the integration surface CI/CD tooling (including Actions) consumes to react to GitHub events; the Deployments API fires a `deployment` webhook event external systems report status back to. | `[Source: https://docs.github.com/en/webhooks/about-webhooks]` / `[Source: https://docs.github.com/en/rest/deployments/deployments]` |
| Husky → Git | Depends on | Husky's entire mechanism is built on Git's native `core.hooksPath` feature; the troubleshooting guide lists "your Git version is above 2.9" (which introduced `core.hooksPath`) as a prerequisite. | `[Source: https://typicode.github.io/husky/troubleshoot.html]` |
| Husky → Node.js | Depends on | Package metadata declares `engines.node >=18` for installing/running the Husky CLI via npm; Husky has no runtime presence during hook execution beyond a POSIX shell dispatcher unless the hook script itself invokes node/npm/npx. | `[Source: https://raw.githubusercontent.com/typicode/husky/main/package.json]` |
| Husky → npm | Depends on | Installation is wired through the package-manager-native `prepare` lifecycle script (npm, pnpm, Bun) or `postinstall` for Yarn, which lacks `prepare` support. | `[Source: https://blog.typicode.com/posts/husky-git-hooks-autoinstall/]` |
| Husky ↔ lint-staged | Complementary / Integrates via | Husky's docs describe their staged-file pre-commit example as "basic" and explicitly direct readers to lint-staged "if you need more" — Husky is the trigger mechanism, deliberately not the staged-file-filtering mechanism. | `[Source: https://typicode.github.io/husky/get-started.html]` |
| Husky ↔ commitlint | Complementary / Integrates via | Documented commit-msg hook integration: `.husky/commit-msg` containing `commitlint --edit $1`, replacing the old `HUSKY_GIT_PARAMS`-based invocation from v4. | `[Source: https://typicode.github.io/husky/migrate-from-v4.html]` |
| Husky ↔ GitHub Actions | Complementary / Integrates via | Documented CI integration pattern via `HUSKY: 0` set in workflow YAML, to skip hook installation on CI runners. | `[Source: https://typicode.github.io/husky/how-to.html]` |
| Husky ↔ pinst | Complementary / Integrates via | For Yarn-based packages published to npm, `prepack`/`postpack` scripts toggling `pinst` are documented so consumers don't inherit the maintainer's Husky install. | `[Source: https://typicode.github.io/husky/how-to.html]` |
| Husky ↔ Git (mechanism) | Integrates via | Husky's install routine runs `git config core.hooksPath <dir>/_` to repoint Git's native hook lookup at Husky's internal hooks folder — this is the entire mechanism. | `[Source: https://raw.githubusercontent.com/typicode/husky/main/index.js]` |
| Husky ↔ Node version managers (nvm, fnm, asdf, volta) | Integrates via | The `~/.config/husky/init.sh` startup-file mechanism is documented specifically to make version-manager shims available to hooks launched from GUI Git clients that don't source a shell profile. | `[Source: https://typicode.github.io/husky/how-to.html]` |
| Three.js ↔ GitHub Actions | Complementary / Integrates via | Three.js's own end-to-end test suite (`npm run test-e2e`) is documented as "primarily intended to be run only by GitHub Actions" due to its ~200MB Chromium install. | `[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/.github/CONTRIBUTING.md]` |
| OpenSearch ↔ Docker / Kubernetes / Ansible | Complementary / Integrates via | Docker is a documented installation method (with `vm.max_map_count ≥262144` host tuning and Docker Desktop memory guidance); Kubernetes via Helm and a dedicated OpenSearch Kubernetes Operator; an Ansible playbook is also a documented install method. Officially-maintained `opensearch-testcontainers` runs real OpenSearch Docker containers inside JUnit 4/5 suites. | `[Source: https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/]`, `[Source: https://docs.opensearch.org/latest/install-and-configure/install-opensearch/index/]`, `[Source: https://github.com/opensearch-project/opensearch-testcontainers]` |
| Go ↔ Docker | Complementary / Integrates via | Official Go blog documents deploying Go servers via Docker (`golang` base image, `golang:onbuild` variant, `docker run`/Docker Hub Automated Builds). | `[Source: https://go.dev/blog/docker]` |
| Go ↔ GitHub Actions | Not documented | Not explicitly named in the underlying research as a CI integration; inferred only from `go test`/`govulncheck` being CI-friendly command-line tools commonly wired into GitHub Actions workflows. | `[Inference from go.md, not an explicit doc statement]` |
| Go ↔ proxy.golang.org (module proxy) | Integrates via | `GOPROXY` defaults to `https://proxy.golang.org` as the documented integration point between the `go` command and external module-hosting infrastructure, with `GOPRIVATE`/`GONOPROXY` routing private-module fetches around it. | `[Source: https://go.dev/ref/mod]` |
| Go ↔ Gin (web framework) | Integrates via | Go's official tutorial set includes building a RESTful API with the third-party Gin web framework — a documented integration path for HTTP services outside the standard library. | `[Source: https://go.dev/doc/tutorial/web-service-gin.html]` |
| Go ↔ OSS-Fuzz | Integrates via | Go's native fuzz testing (`testing.F`, `go test -fuzz`) is exercised continuously via OSS-Fuzz. | `[Source: https://go.dev/security/]` |
| Go ↔ VS Code | Integrates via | `govulncheck` is integrated into the VS Code Go extension; the Go language server `gopls` powers editor features across LSP-speaking editors. | `[Source: https://go.dev/security/]` |
| Python ↔ Docker | Complementary (inferred) | The widely used `python` Docker Hub image (a Docker Official Image) is the de facto containerization path for Python deployment, though not docs.python.org-authored/first-party — a documented gap analogous to the one flagged for PostgreSQL. | `[Inference from python.md, not an explicit doc statement]` |

---

## 10. 3D Graphics (Three.js)

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Three.js → WebGL 2 | Depends on | `WebGLRenderer` "uses WebGL 2 to display scenes," and "WebGL 1 is not supported since r163" — a WebGL 2-capable browser/device is required to function at all. | `[Source: https://threejs.org/docs/pages/WebGLRenderer.html.md]` |
| Three.js → WebGPU (with WebGL 2 fallback) | Depends on | `WebGPURenderer` uses a pluggable Backend: "By default, the renderer tries to use a WebGPU backend if the browser supports WebGPU. If not, WebGPURenderer falls back to a WebGL 2 backend." | `[Source: https://threejs.org/docs/pages/WebGPURenderer.html.md]` |
| Three.js → ECMAScript modules / import maps | Depends on | "As of r147, this is the only way to load three.js properly" — non-module global-namespace `<script>` loading is obsolete since r147. | `[Source: https://threejs.org/manual/#en/fundamentals]` |
| Three.js → browser requestAnimationFrame API | Depends on | The documented render-loop pattern is built directly on `requestAnimationFrame` (or the renderer's own `setAnimationLoop` wrapper). | `[Source: https://threejs.org/manual/#en/fundamentals]` |
| Three.js ↔ Vite | Complementary | The manual's canonical build-tool example: `npm install --save-dev vite` as part of the recommended NPM + build tool path, `npx vite`/`npm run dev` for local development. | `[Source: https://threejs.org/manual/#en/installation]` |
| Three.js ↔ TypeScript | Complementary | "Community-maintained TypeScript type definitions for three.js are available" — not first-party. | `[Source: https://threejs.org/manual/#en/installation]` |
| Three.js ↔ React (react-three-fiber) | Complementary / Integrates via | The manual explicitly lists react-three-fiber ("React components for 3D graphics built on Three") as an approved community framework-wrapper integration. | `[Source: https://threejs.org/manual/#en/libraries-and-plugins]` |
| Three.js ↔ Vue (TresJS) | Complementary / Integrates via | The manual lists TresJS as an approved community framework wrapper for using three.js from Vue. | `[Source: https://threejs.org/manual/#en/libraries-and-plugins]` |
| Three.js ↔ WebXR | Integrates via | Both `WebGLRenderer` (via `.xr`/`WebXRManager`) and `WebGPURenderer` document WebXR integration; the r186 changelog shows active WebXR/WebGPURenderer work (MSAA support, camera-selection fixes). | `[Source: https://threejs.org/manual/#en/webgpurenderer]` |
| Three.js ↔ glTF (GLTFLoader) | Integrates via | First-party official loader integration pattern for external 3D assets: `import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'`. | `[Source: https://threejs.org/docs/llms-full.txt "Loading a GLTF Model" example]` |
| Three.js ↔ jsDelivr CDN | Integrates via | The no-build-tool installation path uses an import map pointing at `https://cdn.jsdelivr.net/npm/three@<version>/build/three.module.js`. | `[Source: https://threejs.org/manual/#en/installation]` |
| Three.js ↔ physics engines (cannon-es, rapier, ammo.js, Jolt) | Integrates via | Manual lists these as officially-linked (community-maintained) physics-engine integrations. | `[Source: https://threejs.org/manual/#en/libraries-and-plugins]` |
| Three.js ↔ GitHub Actions | Complementary / Integrates via | Three.js's own e2e test suite (`npm run test-e2e`) is documented as intended to run via GitHub Actions specifically, due to its ~200MB Chromium install. | `[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/.github/CONTRIBUTING.md]` |

---

## 11. Growth / SEO / Ads

| Pair | Relationship | Nature | Citation |
|---|---|---|---|
| Google SEO → OAuth 2.0 | Depends on | Indexing API requires enabling the API in Google Cloud, creating a service account, verifying site ownership in Search Console, and obtaining an OAuth 2.0 access token. | `[Source: https://developers.google.com/search/apis/indexing-api/v3/prereqs]` |
| Google SEO → Google Cloud | Depends on | Both the Indexing API and Search Console API require Google Cloud project setup and service-account/OAuth authentication. | `[Source: https://developers.google.com/search/apis/indexing-api/v3/prereqs]` |
| Google SEO → HTTP/200 status code | Depends on | Production pages must return an HTTP 200 status to be eligible for indexing; error pages including soft 404s are excluded. | `[Source: https://developers.google.com/search/docs/essentials/technical]` |
| Google SEO ↔ HTML | Complementary / Integrates via | Structured data (JSON-LD, Microdata, or RDFa) is usable regardless of underlying site framework provided it appears in the rendered DOM; configured via `<script>` (JSON-LD), HTML tag attributes (Microdata), or an HTML5 attribute extension (RDFa); `hreflang` and `rel=canonical` are implemented via HTML `<link>` tags. | `[Source: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data]` |
| Google SEO ↔ WebSub | Integrates via | Sitemap submission supports WebSub for Atom/RSS feed-based sitemap submission as an alternative to manual/API submission. | `[Source: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap]` |
| Google SEO ↔ robots.txt | Integrates via | robots.txt directives (`user-agent`, `disallow`, `allow`, `sitemap`) govern crawler access; Google documents how it interprets the robots.txt specification. | `[Source: https://developers.google.com/search/docs/crawling-indexing/robots/intro]` |
| Google AdSense → HTML / JavaScript | Depends on | Publishers must have HTML source access to embed the AdSense script tag (pasted into `<head>`); ad-serving runs via a client-side JS snippet (`adsbygoogle.js`, from `pagead2.googlesyndication.com`). | `[Source: https://support.google.com/adsense/answer/9274634?hl=en]` |
| Google AdSense → OAuth2 | Depends on | The AdSense Management API is REST and OAuth2-authenticated; requires registering a project in Google API Console and generating OAuth2 Client ID credentials. | `[Source: https://developers.google.com/adsense/management/getting_started]` |
| Google AdSense → IAB TCF | Depends on | For EEA/UK/Switzerland traffic, publishers must use a Google-certified Consent Management Platform integrating with the IAB Transparency and Consent Framework before AdSense can serve personalized ads. | `[Source: https://support.google.com/adsense/answer/16918505?hl=en]` |
| Google AdSense ↔ Google SEO | Complementary | Google's own optimization guidance directs publishers to the SEO Starter Guide to grow qualified traffic — framing better traffic, not just more ads, as the sustainable revenue lever. | `[Source: https://support.google.com/adsense/answer/10760404?hl=en]` |
| Google AdSense ↔ AdMob | Complementary | AdSense (web), Ad Manager (multi-demand web), and AdMob (mobile in-app) are a complementary product trio publishers may combine or migrate between, rather than competitors; AdSense itself does not serve mobile in-app inventory. | `[Source: https://support.google.com/admob/answer/9234653?hl=en]` |
| Google AdSense ↔ WordPress | Complementary / Integrates via | AdSense/Auto ads code has dedicated WordPress-specific (and WordPress-AMP) placement instructions distinct from generic HTML integration. | `[Source: https://support.google.com/adsense/answer/9579782?hl=en]` |
| Google AdSense ↔ Google Analytics 4 (GA4) | Integrates via | Publishers can link a GA4 property with AdSense — shared IDs, automatically collected events, and data joining, configured under GA4 Admin → Product links → Google AdSense Links (requires Admin role in AdSense, Editor role in GA4). | `[Source: https://support.google.com/adsense/answer/6084409?hl=en / 14333766]` |
| Google AdSense ↔ AMP | Integrates via | Dedicated Auto-ads-for-AMP script (`amp-auto-ads` library) and a dedicated AMP-compatible manual ad-unit creation flow, distinct from standard HTML pages. | `[Source: https://support.google.com/adsense/answer/9261309?hl=en / 9579782?hl=en]` |
| Google AdSense ↔ ads.txt | Integrates via | Publishers create a plaintext `ads.txt` file at their site root declaring authorized sellers (`google.com` plus a `pub-` ID), which Google's crawler must be able to access. | `[Source: https://support.google.com/adsense/answer/12171612?hl=en]` |
| Google AdSense ↔ Google Ad Manager | Integrates via | A parallel GA4 integration exists for Ad Manager (revenue data surfaced in GA4's Advertising → Publishing → Publisher ads report), documented as related but separate from the AdSense↔GA4 integration. | `[Source: https://support.google.com/analytics/answer/9691421?hl=en]` |

---

## 12. Named Common Combinations

Every `commonCombinations` entry present in the data, verbatim, grouped by the technology whose research surfaced it. No `commonCombinations` were present for the remaining 33 technologies in this dataset — that silence is reported as-is rather than filled in.

**Drizzle ORM**
- Next.js + Neon/Vercel Postgres serverless edge stack
- Next.js + Neon Postgres (Todo app tutorial pairing)

**React**
- React Router (v7) paired with Vite to form a full-stack framework
- Next.js App Router as a full-stack React framework deployable to Node.js/Docker or as a static export
- Expo for universal Android/iOS/web apps sharing one React-based codebase

**Nuxt**
- JAMstack (Nitro described as making Nuxt "a hybrid framework for the JAMstack")

**Vue**
- Vue + Vite + TypeScript project scaffold (via create-vue, with optional routing/state-management/testing/linting selections)

**Three.js**
- Three.js + Vite (recommended NPM + build-tool static-site setup)
- Three.js + React via react-three-fiber
- Three.js + Vue via TresJS
- Three.js + import maps + CDN (no-build-tool static hosting)

**Docker**
- Docker Compose multi-container application stack (compose.yaml defining services/networks/volumes)
- Docker + GitHub Actions CI/CD build-and-push pipeline
- Testcontainers-based integration testing against real containerized dependencies

**ClickHouse**
- Postgres-to-ClickHouse CDC pipeline (PostgreSQL + ClickPipes or PeerDB + ClickHouse) for real-time analytics on data captured from an OLTP source

**OpenSearch**
- OpenSearch + OpenSearch Dashboards + Data Prepper integrated observability/search stack
- Logstash-to-OpenSearch data ingestion pipeline

**GraphQL**
- GraphQL server as a facade proxying legacy REST APIs
- graphql-js served over HTTP via Express

**Tailwind CSS**
- Vite-based framework stack: SvelteKit, Nuxt, SolidJS, and React Router all build their Tailwind integration on top of the first-party `@tailwindcss/vite` plugin since those frameworks are themselves Vite-based

**Husky**
- Husky pre-commit hook + lint-staged for staged-file formatting
- Husky commit-msg hook + commitlint for commit message linting

**Jest**
- Jest + React Testing Library for React component testing
- Jest + Supertest for Express API testing
- Jest + ts-jest (or Babel TS preset) for TypeScript test transformation
- Jest + jsdom test environment for DOM-dependent frontend tests

**Vite**
- Vite + Vitest unified dev/build/test pipeline sharing one config file
- Vite-powered meta-frameworks (Nuxt, SvelteKit, Astro, SolidStart, Analog, React Router built on Vite)
- Backend-integrated frontend asset pipeline (Laravel / Ruby on Rails consuming Vite's manifest.json)

**Google AdSense**
- AdSense + Google Analytics 4 (GA4) revenue reporting
- AdSense + AMP (amp-auto-ads)
- AdSense + WordPress
- AdSense + Google SEO for traffic growth

---

## 13. Cross-Cutting Synthesis

The following observations combine two or more individually-cited facts from the sections above into a connection the underlying research did not state directly. Each is explicitly labeled as a synthesis, not a sourced fact.

- **[Synthesis]** Vite is the build-tool hub of the entire frontend cluster in this data set: it is a `dependsOn`/`complementaryWith` target of React, Vue, Nuxt, Angular, Three.js, Tailwind CSS, and Sass, and is itself the hard dependency of Vitest. No other build tool in the corpus (webpack, Rollup, Browserify, Gulp, Grunt — all only named as TypeScript integration targets) accumulates this many first-party framework/library plugins.
- **[Synthesis]** TypeScript functions as connective tissue rather than an isolated pairing: it is named in the `dependsOn` or `complementaryWith` lists of React, Next.js, Vue, Nuxt, Angular, all four ORMs (Mongoose, TypeORM, Prisma, Drizzle), Fastify, Socket.IO, GraphQL, MUI, shadcn/ui, Vite, Vitest, Playwright, and Jest. The one place a technology is a hard `dependsOn` for TypeScript itself (rather than the reverse) is Angular, which pins exact TS version ranges per major release.
- **[Synthesis]** Redis recurs in two structurally different roles across the corpus: as a *cache backend* (TypeORM query-result caching, Drizzle's `upstashCache()`, GraphQL production caching) and as a *pub/sub broadcast/session layer* (Socket.IO's redis-adapter for multi-node fan-out, Express session storage, Fastify's `@fastify/redis` plugin). A skill library organizing "add Redis" as a single generic capability would miss that these are two distinct integration patterns with different official adapters.
- **[Synthesis]** Docker is the default deployment substrate across nearly every category surveyed — databases (Postgres, MySQL, MongoDB, Redis, ClickHouse, OpenSearch all ship official images), backend frameworks (Fastify, Next.js, Prisma/TypeORM's compiled-JS-for-Docker migration pattern), testing tools (Playwright's `mcr.microsoft.com/playwright` images, Docker+Testcontainers), and CI/CD (GitHub Actions' first-party Docker actions). This makes Docker one of the highest-leverage "connector" technologies in the whole map even though no single technology formally depends on it.
- **[Synthesis]** An emerging MCP (Model Context Protocol) integration pattern appears independently in two unrelated parts of the data — Playwright (`@playwright/mcp` for browser automation) and shadcn/ui (`shadcn mcp init` for component-registry access, plus Claude Code as a named client) — without either technology's research cross-referencing the other. Combined with Angular's separately-documented "Agent Skills" for AI coding agents (Gemini CLI, Antigravity), this suggests AI-agent-facing integration surfaces are becoming a standard extension point across otherwise-unrelated tool categories, not a one-off feature of any single project.
- **[Synthesis]** Express appears as the common integration target for three otherwise-separate technologies that each independently chose it as their reference HTTP-serving example: graphql-js ("recommended next step" after the bare `graphql()` function), MUI (official from-scratch SSR guide), and shadcn/ui (one of two worked server-side registry-auth examples). This positions Express as a default "glue" framework in the documentation ecosystem even for tools that are not themselves backend frameworks.
- **[Synthesis]** The ORM cluster shows a consistent split on MongoDB support: Mongoose treats it as the *only* target (built specifically for it), while TypeORM, Prisma, and Drizzle each treat PostgreSQL as their most fully-featured dialect and MongoDB as a secondary, sometimes version-gated target (Prisma explicitly dropped and re-added Mongo support between v6/v7/v8). A skill recommending "pick an ORM" should not treat MongoDB support as uniform across TypeORM/Prisma/Drizzle.
- **[Synthesis]** Two independent "wire-protocol emulation" patterns appear in the data for connecting a new system to old client tooling without a native driver: ClickHouse emulates both the MySQL wire protocol and a PostgreSQL wire protocol so that existing MySQL/Postgres BI clients can connect unmodified, mirroring how MongoDB's Kafka/Spark connectors let existing streaming/analytics tooling consume MongoDB data without a bespoke integration on the analytics side.

---

## 14. Explicitly Flagged Data Gaps

Per the underlying research's own inference markers, these connections are plausible but were **not found as explicit documentation statements** in the source material — listed here rather than silently treated as confirmed integrations:

| Technology pair | What the data says |
|---|---|
| Prisma ↔ GraphQL | "Not explicitly named in this document as a pairing." |
| Prisma ↔ GitHub Actions (CI/CD) | "Not explicitly named in the document as a CI integration." |
| Drizzle ORM ↔ Vitest | Community usage (GitHub discussions) treats PGlite as the de facto in-memory testing story for Postgres+Drizzle+Vitest, but this is not an explicit official docs recommendation. |
| MUI ↔ GraphQL | "Not mentioned in the researched Material UI documentation as an integration point." |
| Angular ↔ Docker | "Not explicitly named in the doc for containerized deployment." |
| Angular ↔ Jest | "Not named as a supported Angular test runner in the doc; only Vitest, Karma/Jasmine, Playwright and WebdriverIO are documented." |
| Angular ↔ GitHub Actions (CI/CD) | "Not explicitly named as a CI integration in the doc." |
| Go ↔ GitHub Actions (CI/CD) | "Not explicitly named in go.md as a CI integration; inferred only from `go test`/`govulncheck` being CI-friendly tools commonly wired into GitHub Actions workflows." |
| PostgreSQL ↔ Docker | Framed by the researcher as an inference from the widely-used Docker Hub `postgres` image, explicitly noted as not a postgresql.org-authored/first-party artifact. |
| Python ↔ Docker | Same pattern as PostgreSQL — the `python` Docker Hub image is the de facto path but not docs.python.org-authored, "a documented gap analogous to one the project's PostgreSQL research also flagged." |
| Socket.IO ↔ Docker | Inferred only from Kubernetes nginx-ingress sticky-session configuration being documented for multi-node Socket.IO deployments; not a direct Docker statement. |
| WebSocket API ↔ Socket.IO | The specific claim that production systems "typically adopt a userland library such as Socket.IO" to fill RFC 6455's gaps (reconnection, backoff, delivery guarantees) is the researcher's own inference, not an explicit spec or MDN statement. |
| TypeScript ↔ Node.js (dependency framing) | The framing "TypeScript needs a Node.js/npm environment to run its own tooling" is an inference from the documented `npm install`/`npx tsc` install routes, not a verbatim doc statement. |
| GitHub → Git | "GitHub requires Git" is not stated as an explicit sentence in GitHub's own docs, even though the repository/branch/fork/merge/PR model presupposes it. |
| shadcn/ui → React | No single sentence in the shadcn/ui documentation states "requires React" outright, even though the component source, framework guides, and React 18→19 migration notes all presuppose a React host. |

No data was found in this file connecting any of the 44 technologies to: Kubernetes as a first-class researched technology (it appears only as a named *target* inside MongoDB's, Redis's, ClickHouse's, OpenSearch's, and Docker's own integration lists, never as a technology with its own `{technology, dependsOn, ...}` record in this data set); nor to any CSS framework other than Tailwind CSS and Sass. Both are noted here rather than assumed absent from the broader research corpus — this map only reflects what `kmap_integration.json` contains.
