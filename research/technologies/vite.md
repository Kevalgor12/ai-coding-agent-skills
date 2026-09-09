# Vite

Research date: 2026-09-09. Primary official documentation host: **vite.dev** (the project migrated its canonical docs from vitejs.dev to vite.dev; the old `vitejs.dev` domain now redirects/aliases to `vite.dev`, and version-pinned docs live at subdomains like `v6.vite.dev`, `v4.vite.dev`, etc. `main.vite.dev` hosts docs built from the unreleased `main` branch). [Source: https://vite.dev/guide/] This claim about the domain move is based on search-result evidence of `v6.vite.dev` / `v3.vitejs.dev` / `main.vite.dev` existing side by side with `vite.dev`; Unresolved: the exact date of the vitejs.dev → vite.dev migration was not directly confirmed in the fetched pages.

---

## 1. Core concepts

[Source: https://vite.dev/guide/] Vite is a build tool that aims to provide a faster and leaner development experience for modern web projects. Vite ("quick" in French) consists of two major parts: (1) a dev server that provides rich feature enhancements over native ES modules (ESM), including extremely fast Hot Module Replacement (HMR), and (2) a build command that bundles code for production.

[Source: https://vite.dev/guide/why] Vite's origin problem: traditional JS-based bundlers process an entire application before serving anything, causing "painfully slow dev server startups, sluggish hot updates, and long production build times" as projects grow.

[Source: https://vite.dev/guide/why] Vite's solution splits work into two categories:
- **Dependencies**: mostly static during development; pre-bundled once using fast native tooling (esbuild historically, Rolldown/Oxc in current major) so they are ready instantly.
- **Source code**: often not plain JavaScript and needs transforming, and is edited very often; only needs to be transformed when actually requested. Source is served on-demand over native ESM — the browser loads only what it needs for the current page, and Vite transforms each file as it's requested.

[Source: https://vite.dev/guide/why] [VERSION-SENSITIVE — current major] For production, Vite now uses a unified Rust-based bundler called **Rolldown** (replacing the prior esbuild + Rollup combination), creating "one consistent pipeline from development to production."

[Source: https://vite.dev/guide/] [VERSION-SENSITIVE — current major, v8.x] The tool is described as "opinionated and comes with sensible defaults out of the box," while remaining highly extensible via a Plugin API and JavaScript API with full TypeScript typing support.

---

## 2. Architecture

[Source: https://vite.dev/guide/why] Two-part architecture:
1. **Dependency pre-bundling** — third-party dependencies (which change infrequently) are pre-bundled once using fast native tooling so they're ready instantly, converting CommonJS/UMD deps to ESM and batching many small modules into fewer HTTP requests.
2. **On-demand native-ESM source serving** — application source code is served on-demand over native ESM; the browser requests only what the current page needs, and Vite transforms each file as it is requested. This is why Vite's dev server cold start is close to instantaneous regardless of application size, since modules load dynamically rather than requiring upfront bundling.

[Source: https://vite.dev/guide/why] [VERSION-SENSITIVE — current major] For production builds Vite evolved from using separate tools (esbuild for transforms/pre-bundling, Rollup for bundling) to Rolldown, a single Rust-based bundler, unifying the dev and build pipelines.

[Source: https://vite.dev/guide/api-environment] [VERSION-SENSITIVE — introduced Vite 6] Vite 6 introduced the **Environment API**, a formalized abstraction for multiple execution contexts (e.g. `client`, `ssr`, `edge`) within a single dev/build process. Vite 5 and earlier supported only two implicit environments (client and SSR); modern apps often need more (browser, Node server, edge runtime like Cloudflare Workers). Environments are configured through the `environments` config option; each has its own dev environment (module runner that fetches/evaluates transformed code, potentially in a custom runtime like `workerd`) and build environment (separate production bundling config), and can inherit defaults while overriding runtime-specific settings (e.g., `noExternal: true` for edge).

[Source: https://vite.dev/guide/api-plugin] The plugin system extends Rolldown's plugin interface (Rollup-compatible) with Vite-specific hooks. Standard build hooks (`options`, `buildStart`, `resolveId`, `load`, `transform`, `buildEnd`, `closeBundle`) run in both dev and production; `moduleParsed` is unavailable in dev for performance reasons, and Rollup output-generation hooks don't run in dev mode. Vite-specific hooks include `config`, `configResolved`, `configureServer`, `transformIndexHtml`, and `handleHotUpdate`.

[Source: https://vite.dev/guide/backend-integration] For non-SPA/backend-rendered setups, Vite integrates via a three-phase model: dev-time script injection pointing at the Vite dev server (`<script type="module" src="http://localhost:5173/@vite/client">`), a production build emitting a `.vite/manifest.json` mapping source entries to hashed output files, and backend template logic that reads the manifest to emit correct `<script>`/`<link>` tags (including CSS and `modulepreload` for transitive imports).

---

## 3. APIs

[Source: https://vite.dev/guide/api-javascript] Vite exposes a programmatic JavaScript API with four primary functions:
- **`createServer(inlineConfig)`** — async function that starts a dev server instance and returns a `ViteDevServer` with methods for starting the server, managing the file watcher, and driving HMR. Warning: avoid running `createServer` and `build` in the same Node.js process without properly separating `NODE_ENV`/mode, since they can interfere with each other.
- **`build(inlineConfig)`** — async function that compiles the project for production, using Rolldown for bundling, and returns build output for programmatic inspection.
- **`preview(inlineConfig)`** — starts a lightweight static server to preview a production build locally, with its own port/auto-open options.
- **`resolveConfig(inlineConfig, command, ...)`** — resolves and merges the user's Vite config with defaults; requires specifying build vs. serve context so environment-appropriate defaults apply.
- Supporting utilities: `mergeConfig`, `loadEnv`, `normalizePath`.

[Source: https://vite.dev/guide/api-plugin] **Plugin API**: a Vite plugin is a factory function returning an object with a required `name` and optional hooks. `enforce: 'pre' | 'post'` controls ordering relative to Vite's core plugins; `apply: 'build' | 'serve'` (or a function) restricts when a plugin runs, e.g. to exclude SSR builds.
- `config(userConfig, env)` — mutate/return config before resolution.
- `configResolved(resolvedConfig)` — read the final resolved config (e.g., branch on `command === 'build'`).
- `configureServer(server)` — add custom Connect middleware to the dev server; can return a function to inject post-middleware.
- `transformIndexHtml` — dedicated HTML-transform hook (string replace or tag injection with position control).
- `handleHotUpdate` — custom HMR handling: filter affected modules, trigger full reload, or send custom HMR events.

[Source: https://vite.dev/guide/migration] [VERSION-SENSITIVE — v8] New/changed APIs in the v7→v8 migration: `build()` now throws a `BundleError` that wraps individual errors in an `.errors` array; plugin `load()`/`transform()` hooks should return `moduleType: 'js'` when converting content to JavaScript; `transformWithEsbuild()` is deprecated in favor of `transformWithOxc()`; several hooks (`shouldTransformCachedModule`, `resolveImportMeta`, `renderDynamicImport`) were removed; `import.meta.hot.accept()` no longer accepts URLs (an id must be passed instead).

[Source: https://vite.dev/config/] Config file itself is effectively an API surface: it can export a plain object, or a function receiving `{ command, mode, isSsrBuild, isPreview }` (sync or async) to compute config conditionally.

---

## 4. Configuration

[Source: https://vite.dev/config/] Vite automatically resolves a config file named `vite.config.js` (JS and TS extensions supported) in the project root; a custom path can be set via the `--config` CLI flag. Config files must be resolvable as ESM by Node (via `.mjs` extension or `"type": "module"` in `package.json`), or `.mts`/`.cts` equivalents per the troubleshooting guide's ESM-only guidance. [Source: https://vite.dev/guide/troubleshooting]

[Source: https://vite.dev/config/] Config can be a plain object, or a function of `{ command, mode, isSsrBuild, isPreview }` returning config (enabling different settings for `serve` vs `build`), and this function can be async for dynamic config generation.

[Source: https://vite.dev/config/] Env-variable handling in config: Vite deliberately defers loading `.env*` files until *after* config resolution, so environment variables used inside `vite.config.js` itself must already exist in `process.env`, or the config must explicitly call the exported `loadEnv` helper to read `.env*` files early (e.g., to set `server.port` or drive plugin behavior).

[Source: https://vite.dev/config/] Top-level configuration is organized into categories referenced from the config index: Shared Options, Server Options, Build Options, Preview Options, Dependency Optimization Options, SSR Options, Worker Options.

[Source: https://vite.dev/config/server-options] Server-security-relevant options (see Section 7 Security for detail): `server.fs.strict`, `server.fs.allow`, `server.fs.deny`, `server.cors`, `server.allowedHosts`, `server.headers`, `server.origin`.

[Source: https://vite.dev/guide/env-and-mode] `.env` file hierarchy loaded in this precedence: `.env` (always), `.env.local` (always, git-ignored), `.env.[mode]`, `.env.[mode].local` (mode-specific, git-ignored) — mode-specific files take precedence over generic ones. Only variables prefixed `VITE_` are exposed to client code after bundling; everything else is stripped. `--mode` CLI flag selects custom modes (e.g. `staging`) distinct from `NODE_ENV`.

[Source: https://vite.dev/guide/migration] [VERSION-SENSITIVE — v8] Deprecated config keys with replacements (old keys still work via automatic conversion but are deprecated and slated for future removal): `build.rollupOptions` → `build.rolldownOptions`; `worker.rollupOptions` → `worker.rolldownOptions`; `optimizeDeps.esbuildOptions` → `optimizeDeps.rolldownOptions`; `esbuild.*` → `oxc.*` (note: JSX config changes shape, e.g. the string `'automatic'` becomes an object `{ runtime: 'automatic' }`). `build.rollupOptions.watch.chokidar` option was removed entirely. Rollup output formats `'system'` and `'amd'` are no longer supported.

[Source: https://vite.dev/guide/migration] [VERSION-SENSITIVE — v8] New/changed defaults: `build.target` browser baseline moved forward (Chrome/Edge 107→111, Firefox 104→114, Safari 16.0→16.4) to track Baseline Widely Available as of a fixed January-2026 date for this major. A `resolve.tsconfigPaths` boolean was added (built-in tsconfig path-alias support), off by default due to a small performance cost. A `legacy.inconsistentCjsInterop: true` escape hatch exists to restore pre-v8 CJS default-import behavior.

[Source: https://vite.dev/changes/] Vite documents a "Migration/Breaking Changes" tracking page (`/changes/`) listing changes gated behind a `future` config option ahead of formal removal, e.g. `this.environment` availability in plugin hooks, the HMR `hotUpdate` plugin hook, and SSR moving to the `ModuleRunner` API — plus "under consideration" experimental proposals (per-environment APIs, shared plugins during build). Deprecation/usage warnings are intended to guide users through these transitions.

---

## 5. Recommended patterns

[Source: https://vite.dev/guide/performance] Use explicit file extensions in imports (e.g. `import './Component.jsx'` rather than `import './Component'`) to avoid extra filesystem resolution checks against `resolve.extensions` — "the more implicit imports you have, the more time it adds up to resolve the paths."

[Source: https://vite.dev/guide/performance] Avoid barrel files (re-export index files): importing a single API from a barrel forces all files re-exported by that barrel to be fetched and transformed even if unused. Prefer direct imports, e.g. `import { slash } from './utils/slash.js'`.

[Source: https://vite.dev/guide/performance] Use `server.warmup` to pre-transform frequently used files and eliminate import waterfalls, improving initial page load during dev.

[Source: https://vite.dev/guide/performance] Prefer native CSS over heavy preprocessors where possible, and avoid converting SVGs into framework components unnecessarily, to reduce transform overhead.

[Source: https://vite.dev/guide/performance] Disable interfering browser extensions during development, and disable the browser devtools' disk cache setting, since both can slow requests/reloads.

[Source: https://vite.dev/guide/static-deploy] Set `base` correctly for the deployment target (e.g. `'/<REPO>/'` for a GitHub Pages project site) before building.

[Source: https://vite.dev/guide/backend-integration] For backend-integrated (non-SPA) setups, use the generated `.vite/manifest.json` to drive server-side template rendering of asset tags rather than hardcoding hashed filenames.

[Source: https://vite.dev/guide/ssr] For SSR, prefer checking the "Awesome Vite" registry of higher-level SSR plugins/frameworks (e.g. those built on the Environment API) before hand-rolling SSR directly on Vite's low-level `ssrLoadModule` API, since that low-level API is explicitly documented as meant for library/framework authors.

---

## 6. Anti-patterns

[Source: https://vite.dev/guide/env-and-mode] Do not put secrets/API keys into `VITE_`-prefixed env vars — anything with that prefix is exposed in client-side bundled source. "VITE_* variables should not contain sensitive information such as API keys." Handle secrets via a backend/edge function instead.

[Source: https://vite.dev/guide/api-javascript] Do not run `createServer` and `build` in the same Node.js process without properly separating environment/mode state (`NODE_ENV`) — they can interfere with each other.

[Source: https://vite.dev/config/server-options] Do not set `server.cors: true` broadly, and never add wildcard/top-level-domain entries to `server.allowedHosts` (e.g. a bare `.com`) — both are explicitly flagged as dangerous, enabling arbitrary sites to read dev-server source/content or enabling DNS-rebinding attacks.

[Source: https://vite.dev/guide/static-deploy] Do not treat `vite preview` as a production server — it's documented as "a local static web server" for verifying a build locally, not a production-grade server.

[Source: https://vite.dev/guide/troubleshooting] Do not open built output directly via `file://` — this triggers CORS errors; serve it over `http://`, e.g. via `vite preview`.

---

## 7. Security

[Source: https://vite.dev/config/server-options] `server.fs.strict` restricts the dev server from serving files outside the project/workspace root; enabled by default (since Vite 2.7 per the fetched summary — [VERSION-SENSITIVE], flagged for confirmation) — [Inference, not confirmed in docs: exact version the default flipped was reported by the fetch summary but not independently re-verified against the raw doc text]. Requests for files outside the allowed set return a 403.

[Source: https://vite.dev/config/server-options] `server.fs.allow` is an allowlist of directories the dev server may serve via the `/@fs/` endpoint; the docs recommend using the `searchForWorkspaceRoot` utility to keep automatic workspace-root detection while layering custom rules on top.

[Source: https://vite.dev/config/server-options] `server.fs.deny` is a blocklist with higher priority than `fs.allow`, and by default restricts sensitive files (env files, certificates, `.git`) — but this deny filter does **not** apply to the `public` directory, since public-dir files are served unfiltered by design.

[Source: https://vite.dev/config/server-options] `server.cors` (DANGER, per docs): setting it to `true` "allows any website to send requests to your dev server and download your source code and content." Default behavior restricts to localhost/127.0.0.1.

[Source: https://vite.dev/config/server-options] `server.allowedHosts` (DANGER, per docs): permissive configuration enables DNS-rebinding attacks that let an attacker's site download dev-server source/content; the docs specifically warn never to add bare top-level domains (e.g. `.com`) since anyone can register a domain under it.

[Source: https://vite.dev/config/server-options] `server.headers` lets you set custom response headers on the dev server; `server.origin` sets the origin used for generated asset URLs during dev (relevant when the dev server sits behind a reverse proxy or non-standard host setup).

[Source: https://vite.dev/guide/env-and-mode] Client-exposed env vars (the `VITE_` prefix mechanism) are a security-relevant design point: anything so prefixed ends up readable in shipped client bundles.

---

## 8. Performance

[Source: https://vite.dev/guide/why] Dev-server cold start is near-instant regardless of app size because source is served/transformed on demand over native ESM rather than bundled up front; dependencies are pre-bundled once for fast, cached retrieval.

[Source: https://vite.dev/blog/announcing-vite8] [VERSION-SENSITIVE — v8] Production build performance claim: "Vite 8 ships with Rolldown as its single, unified, Rust-based bundler, delivering up to 10-30x faster builds" versus the prior Rollup-based pipeline. Cited real-world examples: Linear's build dropped from 46s to 6s; Beehiiv reported a 64% build-time reduction. [Inference, not confirmed independently: these are third-party-reported figures relayed via the official blog post per the fetch summary; exact methodology not verified from primary text.]

[Source: https://vite.dev/guide/performance] Documented performance levers: reduce implicit/extension-less imports (extra resolve-time filesystem checks), avoid barrel files (unnecessary transform of unused re-exported modules), use `server.warmup` to pre-transform hot files, prefer native CSS over heavy preprocessors, avoid unnecessary SVG-to-component conversion, and disable interfering browser extensions/devtools disk cache during dev.

[Source: https://vite.dev/guide/performance] Profiling tooling: `vite --profile` (dev) or `vite build --profile` generates CPU profiles inspectable at speedscope.app; `vite-plugin-inspect` is recommended to find plugin/middleware bottlenecks.

[Source: https://vite.dev/guide/features] Production build features aimed at runtime performance: automatic CSS code splitting, preload-directive generation, async-chunk-loading optimization to reduce network round trips, and an optional import-map based optimization to improve cache hit rates.

---

## 9. Testing

[Source: https://vite.dev/guide/why] Vite's own docs note that ecosystem tools are built directly on top of it for testing/dev tooling: "Tools like Vitest and Storybook built on it too, extending Vite's reach beyond app bundling."

Vite itself does not ship a built-in test runner; the officially adjacent, same-org project is **Vitest** (vitest.dev, maintained by the same core team) [Source: https://vitest.dev/guide/] — described there as "a next generation testing framework powered by Vite" that reuses `vite.config.*`, so existing Vite plugins/config work out of the box, letting dev/build/test share one pipeline and one config file, with Jest-API compatibility for easy migration. Note: vitest.dev is a distinct official documentation site from vite.dev (separate `vitest-dev` GitHub org, same maintaining team) — cited here as an official adjacent source per the task's "official GitHub org repos" allowance, not as vite.dev content itself.

[Source: https://vite.dev/guide/troubleshooting] Testing/verification-adjacent tooling mentioned in Vite's own troubleshooting docs: `vite-plugin-inspect` for diagnosing plugin/transform behavior, and `vite --debug hmr` for logging HMR/circular-dependency issues during iterative development.

[Source: https://devtools.vite.dev/vitest/] [VERSION-SENSITIVE] Vite DevTools (a separate official `@vitejs`-scoped devtools framework) ships a built-in Vitest integration (`@vitejs/devtools-vitest`) that surfaces the Vitest UI inside the DevTools dock, letting users run/watch the test suite without leaving DevTools.

Unresolved: whether vite.dev's main guide has a dedicated "Testing" page distinct from the ecosystem-tooling mention in `/guide/why` was not confirmed — the fetched pages only surfaced testing coverage via the `why` page and the separate vitest.dev/devtools.vite.dev properties.

---

## 10. Deployment

[Source: https://vite.dev/guide/static-deploy] Core workflow: configure `base` in `vite.config.js` to match the deployment URL path (e.g. `'/<REPO>/'` for a GitHub Pages project page); run `npm run build` (or equivalent) to produce optimized static output in `dist` (configurable via `build.outDir`); use `vite preview` to serve the build locally at `http://localhost:4173` for verification before deploying — explicitly documented as a local static server, not for production use.

[Source: https://vite.dev/guide/static-deploy] Platform-specific guides are documented for: GitHub Pages (via GitHub Actions), GitLab Pages, Cloudflare Pages, Netlify, Vercel, Azure Static Web Apps, Render, Google Firebase, Surge, Flightcontrol, Zephyr Cloud, and others — most via Git-integrated auto-detection of Vite projects, others via CLI-based deploys.

[Source: https://vite.dev/guide/backend-integration] For non-static/backend-rendered deployments, production deploy involves shipping the built `dist` assets plus `.vite/manifest.json`, with the backend template layer reading the manifest to emit correct hashed asset tags (including transitive CSS and `modulepreload` links).

[Source: https://vite.dev/guide/ssr] For SSR deployments, production requires separate client and server builds; at runtime, `ssrLoadModule` (used in dev) is replaced by direct imports from the pre-built server bundle, removing the dev-server dependency in production.

---

## 11. Migration

[Source: https://vite.dev/guide/migration] Vite publishes an official "Migration from v7" guide covering the v7→v8 major upgrade — the current major-version migration path as of this research. [VERSION-SENSITIVE — this entire section reflects the v7→v8 transition only.] Key points (also itemized in Sections 3–4):
- Browser baseline target bump (Chrome/Edge 107→111, Firefox 104→114, Safari 16.0→16.4).
- Rolldown + Oxc replace Rollup + esbuild for bundling/transforms/minification (JS minify via Oxc Minifier; CSS minify via Lightning CSS by default, with an opt-out back to esbuild by installing it as a devDependency).
- `optimizeDeps.esbuildOptions` deprecated → `optimizeDeps.rolldownOptions` (automatic conversion supported, including minify/tree-shaking/resolution option mapping).
- `esbuild` config option deprecated → `oxc` (JSX shape changes from string to object form); Oxc does not yet lower native decorators — documented workaround is using a Babel or SWC plugin configured with Rolldown.
- CommonJS interop default-import rule changed: default import now equals `module.exports` when the importer is ESM-format or `module.exports.__esModule` isn't `true`; otherwise it accesses `module.exports.default`. This can break existing CJS-import code; `legacy.inconsistentCjsInterop: true` restores old behavior temporarily.
- `resolve.mainFields`-based format resolution is now consistently respected; automatic `browser`/`module` field sniffing was removed.
- `build.rollupOptions`/`worker.rollupOptions` deprecated → `build.rolldownOptions`/`worker.rolldownOptions`.
- `build()` throws `BundleError` (wraps individual errors in `.errors`); `transformWithEsbuild()` deprecated → `transformWithOxc()`.
- Removed: rollup output formats `'system'`/`'amd'`; hooks `shouldTransformCachedModule`, `resolveImportMeta`, `renderDynamicImport`; `build.rollupOptions.watch.chokidar`; `import.meta.hot.accept()` accepting URLs (must pass an id).

[Source: https://vite.dev/guide/migration] Older major-version migration guides (v6→v7, v5→v6, etc.) are documented on the version-pinned doc sites (e.g. content historically linked from `vite.dev/guide/migration` for prior majors); the current fetch only surfaced the v7→v8 guide as the "live" migration page — Unresolved: full content of pre-v7 migration guides was not independently fetched in this research pass.

[Source: https://vite.dev/blog/announcing-vite8-beta] Vite also separately documents a `rolldown-vite` npm package as an interim/alternate distribution: it "implements Vite 7 with Rolldown, without other Vite 8 changes" — i.e., a way to adopt the Rolldown bundler ahead of/instead of the full v8 upgrade. [VERSION-SENSITIVE]

There is no comparable "migrating from webpack/Parcel/CRA to Vite" official guide surfaced in this research — Not documented / could not verify within the pages fetched (community/ecosystem guides may exist but are outside the official-docs-only scope of this research).

---

## 12. Version information

[Source: https://vite.dev/guide/] [Source: https://vite.dev/releases] Current stable version as of this research: **v8.2.2**. Vite 8.0 was released [Source: https://vite.dev/blog/announcing-vite8] on **March 12, 2026** per the fetched summary [Inference, not confirmed by re-reading raw text: exact date relayed by the fetch tool's summarization, not independently cross-checked against the raw blog HTML].

[Source: https://vite.dev/releases] Release cadence:
- Patch releases: "released as needed (usually every week)."
- Minor releases: "always contain new features and are released as needed," with beta pre-releases roughly every two months.
- Major releases: occur "usually every year" and "generally align with Node.js EOL schedule."

[Source: https://vite.dev/releases] Support/maintenance tiers (as observed at research time): the current minor (`vite@8.2`) gets regular patches; the previous major's latest minor and the current major's previous minor (`vite@7.3`, `vite@8.1`) get important fixes and security patches; the second-to-last major's latest minor (`vite@6.4`, and `vite@8.0` itself) get security-patches-only. This is a rolling policy tied to whichever versions are current at any given time, not fixed version numbers.

[Source: https://vite.dev/releases] TypeScript type-definition changes can occur across minor versions (to track TypeScript's own evolution); the docs recommend TypeScript users pin/lock the Vite minor version when upgrading to avoid unexpected type breaks.

[Source: https://vite.dev/blog/announcing-vite8] Node.js requirement for Vite 8: **Node.js 20.19+ or 22.12+** (needed to support the package's ESM-only distribution without flags). [VERSION-SENSITIVE — this requirement applies to the v8 line; earlier majors had lower Node floors, not independently re-verified here for exact prior thresholds — Unresolved.]

[Source: https://vite.dev/blog/announcing-vite8] Install-size trade-off noted for v8: roughly 15 MB larger than v7, mostly attributable to Lightning CSS (~10 MB) and Rolldown (~5 MB) as bundled native dependencies.

Version-pinned documentation exists for prior majors at subdomains, e.g. `v6.vite.dev`, `v4.vite.dev`, `v3.vitejs.dev` [Source: https://v6.vite.dev/] [Source: https://v4.vite.dev/guide/] [Source: https://v3.vitejs.dev/guide/] — confirming Vite maintains historical major-version doc snapshots rather than only a single "latest" doc tree.

---

## 13. Breaking changes

See Section 11 (Migration) for the full itemized v7→v8 breaking-change list per the official migration guide — duplicated here at a summary level per the requested document structure:

[Source: https://vite.dev/guide/migration] [VERSION-SENSITIVE — v8] Breaking in v8: bundler/transform engine swap (Rollup+esbuild → Rolldown+Oxc) with associated config-key renames; CJS default-import interop semantics changed; `browser`/`module` field auto-sniffing removed; several plugin hooks and Rollup output formats removed; `import.meta.hot.accept()` URL-argument support removed; raised default `build.target` browser baseline.

[Source: https://vite.dev/changes/] Ahead of the *next* major, Vite documents forthcoming breaking changes gated behind an explicit `future` config flag so they can be opted into early: changes to `this.environment` availability in hooks, the HMR `hotUpdate` plugin hook, and SSR moving onto the `ModuleRunner` API. The docs state deprecation/usage warnings will "guide you where possible," and that the team is proactively reaching out to framework/plugin authors ahead of the change. As of this fetch, the page notes "No past changes yet" logged under the formal breaking-changes tracker for the upcoming major, i.e. this tracking mechanism itself is new. [VERSION-SENSITIVE — describes intent for the release after v8, not yet finalized.]

---

## 14. Limitations

[Source: https://vite.dev/guide/ssr] Vite's native `ssrLoadModule`/SSR API is explicitly documented as "a low-level API meant for library and framework authors," not as a turnkey end-user SSR solution — users are directed to higher-level SSR plugins/frameworks in the Awesome Vite registry.

[Source: https://vite.dev/guide/ssr] SSR is stated to be actively evolving: "Vite is working on an improved SSR API with the Environment API," signaling the current low-level SSR surface is not a stable long-term target.

[Source: https://vite.dev/guide/ssr] SSR build target defaults to Node.js; running the server in a Web Worker or other non-Node runtime requires manual `ssr.target` configuration — it is not automatic.

[Source: https://vite.dev/guide/migration] [VERSION-SENSITIVE — v8] Documented specific limitation: Oxc (which replaces esbuild for JS transforms in v8) "doesn't yet lower native decorators" — a workaround (Babel or SWC plugin under Rolldown) is required for decorator-heavy codebases.

[Source: https://vite.dev/guide/troubleshooting] Documented environment-specific limitations: Linux file-descriptor limits can stall dev-server requests on large projects (requires `ulimit`/`sysctl` tuning); file-watcher `ENOSPC` errors occur when `fs.inotify.max_user_watches` is exceeded; WSL2 has known file-watching limitations affecting HMR; case-mismatched import paths break HMR detection; circular dependencies force full reloads instead of granular HMR.

[Source: https://vite.dev/config/server-options] `server.fs.deny`'s sensitive-file blocklist explicitly does not apply to the `public` directory — files placed there are always served unfiltered, which is a documented constraint rather than a bug.

---

## 15. Debugging

[Source: https://vite.dev/guide/troubleshooting] Official troubleshooting guide covers: CLI path issues on Windows with special characters (workaround: switch package manager or avoid the character); ESM-only config-loading errors (fix: add `"type": "module"` to `package.json` or use `.mjs`/`.mts`); dev-server stalls from Linux fd limits; `ENOSPC` file-watch errors; self-signed TLS cert issues breaking caching; HMR failures from case-mismatched imports, WSL2 watch limitations, and circular deps forcing full reload; build-output CORS errors from `file://` access (use `vite preview` over http instead); dynamic-import failures from version skew, flaky networks, or browser extensions.

[Source: https://vite.dev/guide/troubleshooting] Debugging tooling: `vite --profile --open` (dev) or `vite build --profile` (build) generate CPU profiles viewable at speedscope.app; `vite-plugin-inspect` is recommended for inspecting plugin/middleware performance; `vite --debug hmr` enables verbose HMR logging, including circular-dependency paths.

[Source: https://vite.dev/blog/announcing-vite8] [VERSION-SENSITIVE — v8] Vite 8 ships an **Integrated Devtools** flag providing "a powerful suite of debugging and analysis tools directly from your dev server," plus **browser console forwarding** to the dev terminal — called out as "useful for AI coding agents" per the fetched official blog summary.

[Source: https://devtools.vite.dev/guide/] Vite DevTools (`@vitejs`-scoped, separate official site) is described as "a devtools framework for the Vite ecosystem" providing shared infrastructure (unified dock, type-safe RPC, shared state, flexible UI hosting) so individual diagnostic tools (including the Vitest integration) compose into one UI.

---

## 16. Integration

[Source: https://vite.dev/guide/features] Built-in support/integration points: bare module resolution and pre-bundling for npm dependencies; TypeScript/JSX/TSX transpilation without type-checking; CSS (imports with HMR, CSS Modules, Sass/Less/Stylus preprocessors, PostCSS, automatic `@import` inlining and URL rebasing); static asset and JSON imports; WebAssembly and Web Worker imports; `import.meta.glob` for multi-module filesystem imports (lazy or eager).

[Source: https://vite.dev/guide/why] Framework integration is called out explicitly: "Nuxt, SvelteKit, Astro, React Router, Analog, SolidStart, and others chose Vite as their foundation." Vite maintains official first-party plugins for Vue and React, with other frameworks supported via community/official plugins.

[Source: https://vite.dev/guide/why] Backend framework integration: "Backend frameworks like Laravel and Ruby on Rails integrated Vite for their frontend asset pipelines," referencing Laravel's own Vite docs and the community `vite_ruby` project.

[Source: https://vite.dev/guide/backend-integration] Generic backend-integration mechanism (framework-agnostic): dev-time `@vite/client` script injection plus either dev-server proxying or `server.origin` configuration; production-time consumption of `.vite/manifest.json` to emit correct asset tags.

[Source: https://vite.dev/guide/why] Ecosystem tooling built directly on Vite: Vitest (testing) and Storybook (component workshop), described as "extending Vite's reach beyond app bundling." Rolldown is described as the unifying bundler effort: "written in Rust for native speed, and compatible with the same plugin API," aligning Vite's dev and build tool internals.

[Source: https://vite.dev/guide/why] The Vite team runs `vite-ecosystem-ci`, which "tests major ecosystem projects against every Vite change" — an official CI process for validating cross-project compatibility ahead of releases.

---

## 17. Production considerations

[Source: https://vite.dev/guide/features] Production builds automatically apply CSS code splitting, generate preload directives, and optimize async chunk loading to reduce network round-trips, plus an optional import-map-based optimization to improve cache-hit rates.

[Source: https://vite.dev/guide/migration] [VERSION-SENSITIVE — v8] Default production `build.target` now tracks Baseline Widely Available browsers as of a January-2026 cutoff for this major (Chrome/Edge 111+, Firefox 114+, Safari 16.4+) — teams needing to support older browsers must explicitly lower `build.target`.

[Source: https://vite.dev/guide/static-deploy] `vite preview` must not be used as the production server — it is explicitly scoped to local verification of a production build only; real deployments should use one of the documented static/host-specific deployment paths or a proper application/edge server.

[Source: https://vite.dev/guide/env-and-mode] Production secrets must never be placed in `VITE_`-prefixed variables since those are compiled into publicly-readable client bundles; secret handling belongs server-side/edge-side.

[Source: https://vite.dev/config/server-options] Security-relevant dev-server hardening options (`server.fs.strict`, `server.fs.allow`/`deny`, `server.cors`, `server.allowedHosts`) are dev-server-only concerns but are documented with explicit DANGER warnings because a misconfigured dev server left reachable can leak source/content or be DNS-rebinding-attacked — relevant to teams running Vite dev servers on shared/exposed networks (e.g. CI preview environments, cloud IDEs).

[Source: https://vite.dev/guide/ssr] For SSR in production, the dev-only `ssrLoadModule` path is replaced by direct imports from the separately-built server bundle — teams must build both a client and a server bundle as part of their production pipeline, not just one.

[Source: https://vite.dev/blog/announcing-vite8] [VERSION-SENSITIVE — v8] Install-size increase (~15 MB, from bundled Lightning CSS and Rolldown native binaries) is a documented production/CI consideration — e.g. affects Docker image size or CI cache size for teams installing `node_modules` in build pipelines.

---

## Summary of sources cited

- https://vite.dev/guide/ — Getting Started / core concepts
- https://vite.dev/guide/why — Why Vite, architecture rationale, ecosystem framing
- https://vite.dev/guide/features — Feature list (CSS, assets, glob imports, build optimizations)
- https://vite.dev/guide/migration — v7→v8 migration guide (breaking changes, deprecations)
- https://vite.dev/changes/ — Forthcoming breaking-changes tracker (`future` flag)
- https://vite.dev/guide/performance — Official performance guidance
- https://vite.dev/guide/troubleshooting — Official troubleshooting/debugging guide
- https://vite.dev/guide/static-deploy — Static deployment guide
- https://vite.dev/guide/backend-integration — Backend integration guide (manifest, entries)
- https://vite.dev/guide/api-environment — Environment API (Vite 6+)
- https://vite.dev/guide/api-plugin — Plugin API
- https://vite.dev/guide/api-javascript — JavaScript API
- https://vite.dev/guide/ssr — SSR guide and limitations
- https://vite.dev/guide/env-and-mode — Env vars and modes
- https://vite.dev/config/ — Configuring Vite (index)
- https://vite.dev/config/server-options — Server options (security-relevant)
- https://vite.dev/releases — Release cadence and support policy
- https://vite.dev/blog/announcing-vite8 — Vite 8.0 announcement (official blog)
- https://vite.dev/blog/announcing-vite8-beta — Vite 8 beta announcement (rolldown-vite)
- https://vitest.dev/guide/ — Vitest ("Why Vitest" / getting started), same maintaining org, cited for the Testing dimension
- https://devtools.vite.dev/guide/ and https://devtools.vite.dev/vitest/ — official Vite DevTools sub-project docs
- https://v6.vite.dev/, https://v4.vite.dev/guide/, https://v3.vitejs.dev/guide/ — version-pinned prior-major doc snapshots (used only to confirm documentation-versioning structure)
