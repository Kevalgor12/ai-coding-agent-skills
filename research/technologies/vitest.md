# Vitest — Technology Research

Research date: 2026-09-09. Primary source: `vitest.dev` (the canonical official Vitest documentation host — confirmed current, no evidence of a host migration). Secondary official sources: `github.com/vitest-dev/vitest` (source repo and releases, used only for the `releases.html`/blog-linked material already covered by `vitest.dev`). Citation convention: `[Source: <url>] <claim>.` for documented facts, `[Inference, not confirmed in docs]` for reasoning not explicitly stated in a fetched page, and "Not documented / could not verify" where no official source was found during this research pass. `Unresolved:` flags items with conflicting or ambiguous information across fetched pages.

**Version context note**: [Source: https://vitest.dev/blog/vitest-5.html] Vitest 5.0 was released 2026-09-03 — six days before this research date — making the documentation site's "current" branch reflect a very recently shipped major version. Some third-party aggregators (not cited here) still reference v5.0.0-beta.1; the stable v5.0.0 release is what `vitest.dev`'s main docs describe as of this research date. [Source: https://vitest.dev/releases.html] Regular patches continue for `vitest@5.0`; important fixes and security patches are backported to `vitest@4.1`.

---

## 1. Core concepts

[Source: https://vitest.dev/guide/] Vitest (pronounced "veetest") is described as "a next generation testing framework powered by Vite," enabling unit tests to be written and executed for JavaScript/TypeScript projects using Vite's transformation pipeline and configuration.

[Source: https://vitest.dev/guide/why.html] Vitest was created to fill a gap in the Vite ecosystem: Vite had a strong dev/build story but no native testing solution, and "existing options like Jest were created in a different context," resulting in duplicated configuration and transform logic between the app build and the test run. Vitest's core design insight is reusing Vite's dev server and `vite.config.js` for test-file transformation, so the same plugins/resolvers/config apply to dev, build, and test.

[Source: https://vitest.dev/guide/why.html] Despite being Vite-native, Vitest provides "a compatible API that allows you to use it as a drop-in replacement in most projects," including Jest-compatible mocking and snapshot testing, to ease migration.

[Source: https://vitest.dev/guide/features.html] Test files are conventionally identified by `.test.` or `.spec.` filename markers. Core capabilities include: smart/instant watch mode ("like HMR for tests"), Jest-compatible snapshot testing, built-in Chai assertions with a Jest `expect`-compatible API, Jest-compatible mocking via the `vi` object, out-of-the-box TypeScript/JSX/ESM (including top-level await) support, parallel execution via multiple processes/worker threads, concurrent tests via `.concurrent`, file isolation, component testing (Vue/React/Svelte/Lit/Marko and more), native Browser Mode, in-source (Rust-style) testing, benchmarking via Tinybench, type testing via `expect-type`, coverage via v8 or Istanbul, multi-project ("Projects") support for monorepos, and CI sharding.

[Source: https://vitest.dev/guide/] Vitest 5.0 (the version this research reflects) requires Vite >= 6.4.0 and Node.js >= 22.12.0. [Version-sensitive: these are the v5.0 minimum requirements; earlier majors had lower Node/Vite floors — see §11/§12/§13.]

## 2. Architecture

[Source: https://vitest.dev/guide/why.html] Architecturally, Vitest is layered directly on top of Vite: it shares Vite's plugin API and module transformation pipeline rather than reimplementing a separate transform/resolve step, giving "first-class integration with Vite" for both test authors and Vite plugin maintainers.

[Source: https://vitest.dev/guide/improving-performance.html] Test execution runs inside one of three selectable "pools": `forks` (default — spawns child processes via Node's `child_process`, chosen for compatibility, avoiding hanging-process and native-addon segfault issues), `threads` (uses Node's `worker_threads` API for parallelism, often faster than `forks` but with more native-module/timer edge cases), and `vmThreads` (creates a fresh VM context and `window` per file without full environment-recreation cost, suited to DOM-heavy suites; test isolation cannot be disabled under `vmThreads`).

[Source: https://vitest.dev/blog/vitest-5.html] In v5.0, inline "projects" share the Vite server, and a filesystem module cache persists transformed modules on disk for reuse across runs — both are performance-oriented architecture changes to the transform/execution pipeline.

[Source: https://vitest.dev/guide/environment.html] Test files execute inside a selectable "environment" abstraction — `node` (default), `jsdom`, `happy-dom`, `edge-runtime`, or a custom environment package (`vitest-environment-${name}`) implementing an `Environment` interface with `setupVM()`/`setup()`/`teardown()` hooks — which determines what browser-like globals (if any) are injected into the test's execution context.

[Source: https://vitest.dev/guide/workspace.html] For multi-package/monorepo architectures, Vitest runs multiple test "projects" within a single process; each project can have its own resolve/plugins/environment/browser config while inline projects inherit root config by default (v5.0 behavior — see §11).

## 3. APIs

[Source: https://vitest.dev/api/] The API reference is organized into: core test APIs (`test`/`it`, `describe`, hooks, mocks, `vi`, `expect`, `expectTypeOf`, `assert`, `assertType`), Browser Mode APIs (React/Vue/Svelte render helpers, DOM context, locators, browser-specific assertions, commands), and advanced APIs (runner/config internals, test project and spec management, reporter interfaces, plugin system, metadata/artifact handling).

[Source: https://vitest.dev/api/] Hook lifecycle methods documented include `beforeEach`, `afterEach`, `beforeAll`, `afterAll`, and — notably — `aroundEach` and `aroundAll`. [Version-sensitive: `aroundEach`/`aroundAll` were surfaced in the v5.0-era API docs fetched for this research; could not verify the exact version they were introduced in from the pages fetched, so treat their availability in versions prior to 5.0 as unconfirmed.]

[Source: https://vitest.dev/api/] Parametrized/data-driven testing is supported via `test.each` and `test.for`; per-test fixtures and custom context are supported via `test.extend`; concurrent execution is supported per-test via `.concurrent`.

[Source: https://vitest.dev/guide/mocking.html] The `vi` helper (imported from `vitest`, or available globally when `globals: true` is configured) exposes mocking utilities: `vi.fn()` (mock functions), `vi.mock()` (whole-module mocking, hoisted to the top of the file), `vi.spyOn()` (spies on object/class methods), `vi.stubGlobal()` (global variable mocking), `vi.setSystemTime()` (fake system time), `vi.stubEnv()` (environment variable mocking, paired with `unstubEnvs` config).

[Source: https://vitest.dev/blog/vitest-5.html] v5.0 adds a new `vi.when()` API for conditional mocking with deep-equality argument matching and asymmetric matchers, plus a `toHaveBeenExhausted()` assertion to verify all registered `vi.when()` behaviors were consumed. [Version-sensitive: new in v5.0.]

[Source: https://vitest.dev/guide/cli.html] CLI commands: `vitest` (watch mode in dev / run mode in CI, auto-detected), `vitest run` (single run, no watch), `vitest watch` / `vitest dev` (explicit watch alias), `vitest related` (runs only tests covering a given list of source files — static imports only, not dynamic), `vitest bench` (runs benchmark tests only), `vitest init <name>` (scaffolds config; currently supports `browser`), `vitest list` (prints matching tests, with `--json`/`--filesOnly`), `vitest doctor` (measures performance under alternative configs and recommends optimizations). Key flags: `--run`, `--coverage.provider`, `--reporter`, `--pool`, `--project`, `--testTimeout` (default 5000ms), `--bail`, `--retry.count`, `--maxWorkers`, `--shard`, and the new (v5.0) `--repeats` flag for flaky-test hunting.

[Source: https://vitest.dev/guide/cli.html] `vitest list` "now parses files statically by default, replacing the previous behavior that relied on running the test files" — [Version-sensitive: this static-parsing default is a v5.0 change per the blog post at https://vitest.dev/blog/vitest-5.html.]

## 4. Configuration

[Source: https://vitest.dev/config/] Vitest resolves configuration by searching, in order, for `vitest.config.{ts,mts,cts,js,mjs,cjs}` and then `vite.config.{ts,mts,cts,js,mjs,cjs}` in the project root, with an explicit `--config <path>` CLI flag overriding both. A dedicated `vitest.config.*` file always takes precedence over `vite.config.*` when both exist.

[Source: https://vitest.dev/config/] Two setup styles are documented: with Vite as a dependency, use `defineConfig` from `'vite'` with a `test: {...}` field (plus a `/// <reference types="vitest/config" />` triple-slash directive for typing); without a direct Vite dependency, import `defineConfig` from `'vitest/config'` directly.

[Source: https://vitest.dev/config/] `mergeConfig()` combines a Vitest-specific config with an existing Vite config (supports both static objects and function-form Vite configs). `configDefaults` is exported for extending Vitest's own defaults. All ordinary Vite config keys (`define`, `resolve.alias`, plugins, etc.) apply at the top level, outside the `test` block, and are reused automatically by Vitest.

[Source: https://vitest.dev/config/] `process.env.VITEST` (or a config `mode` check) can be used to branch configuration conditionally between the app build and the test run. Setting `VITEST_SKIP_INSTALL_CHECKS=1` disables Vitest's automatic dependency-install prompts.

[Source: https://vitest.dev/guide/environment.html] Environment can be set project-wide via `test.environment` (`node` default, `jsdom`, `happy-dom`, `edge-runtime`, custom) or per-file via a `// @vitest-environment jsdom`-style control comment.

[Source: https://vitest.dev/guide/coverage.html] Coverage is configured under `test.coverage`, with `provider: 'v8' | 'istanbul' | 'custom'`, plus `coverage.include`/`coverage.exclude` glob patterns (only imported files appear in reports by default; `include` is needed to surface uncovered files). Run via `vitest run --coverage`.

[Source: https://vitest.dev/guide/workspace.html] Multi-package configuration uses `projects` (glob patterns like `projects: ['packages/*']`, inline project objects, or references to project-specific config files such as `vitest.config.unit.ts`). Coverage, reporters, and snapshot path resolution must be defined only at the root config level, not inside individual projects.

[Source: https://vitest.dev/blog/vitest-5.html] v5.0 configuration changes: `clearMocks` now defaults to `true` (runs `vi.clearAllMocks()` before every test — set `clearMocks: false` to restore prior behavior); a new `injectCjsGlobals` option disables CJS-global injection into ES modules; a new `coverage.autoAttachSubprocess` option tracks child-process coverage; generated report/artifact output now consolidates under a single `.vitest/` directory (e.g. screenshots default to `.vitest/attachments/failure-screenshots/`). [Version-sensitive: all four are v5.0 default/behavior changes.]

[Source: https://vitest.dev/guide/in-source.html] In-source testing is enabled via `test.includeSource: ['src/**/*.{js,ts}']`, with tests written inside `if (import.meta.vitest)` blocks using `const { it, expect } = import.meta.vitest`.

## 5. Recommended patterns

[Source: https://vitest.dev/guide/mocking.html] "Always remember to clear or restore mocks before or after each test run to undo mock state changes between runs" — documented as essential mocking hygiene. (Note: as of v5.0 `clearMocks: true` is now the default, per §4, reducing the need for manual clearing in new projects.)

[Source: https://vitest.dev/guide/improving-performance.html] Recommended performance patterns: profile first using Vitest's built-in duration breakdown (environment/import/transform/tests/setup phases) before optimizing; prefer `happy-dom` over `jsdom` when full DOM fidelity isn't required (cheaper to instantiate); enable filesystem module caching (`fsModuleCache`) to persist transformed files between reruns; set `NODE_COMPILE_CACHE` for bytecode reuse; scope `test.dir` to exclude unrelated folders; disable test isolation for suites that reliably clean up their own state, to speed up runs; prefer `threads` pool over the default `forks` pool for raw speed when compatibility allows, or `vmThreads` for DOM-heavy suites; use `--shard=X/Y` with `--reporter=blob` plus `--merge-reports` to distribute large suites across CI machines.

[Source: https://vitest.dev/guide/mocking.html] Recommended approach by mocking scenario: exported functions → `vi.mock()` or `vi.spyOn()`; class implementations → a fake class using `vi.fn()`/`vi.spyOn()`; partial module mocking → `vi.mock()` with the spread operator to retain unmocked exports; cached/singleton objects → a cache pattern inside the mock factory; globals → `vi.stubGlobal()`; system time → `vi.setSystemTime()`; environment variables → `vi.stubEnv()` with the `unstubEnvs` config option.

[Source: https://vitest.dev/guide/in-source.html] In-source testing is recommended for small unit-testable utility functions and prototyping; separate test files are recommended for components or end-to-end scenarios.

[Source: https://vitest.dev/guide/debugging.html] When debugging, use `--test-timeout=0` (prevent timeout while paused at a breakpoint) and `--no-file-parallelism` (avoid parallel execution interfering with a single debug session).

## 6. Anti-patterns

[Source: https://vitest.dev/guide/mocking.html] Documented pitfall: with partial module mocking, "if `original` calls `mocked` internally, it will always call the function defined in the module, not in the mock factory" — i.e., internal same-module calls bypass the mock factory's replacement, a common source of confusion.

[Source: https://vitest.dev/guide/migration.html] As of v5.0, calls to `vi.mock()`, `vi.unmock()`, and `vi.hoisted()` must sit at module scope (not inside functions or `describe` blocks) — placing them elsewhere is now an anti-pattern/breaking usage; the dynamic equivalents `vi.doMock()`/`vi.doUnmock()` remain usable in non-module-scope locations. [Version-sensitive: this scoping restriction is new/tightened in v5.0.]

[Source: https://vitest.dev/guide/common-errors.html] Documented anti-pattern: calling an async function without `await`, which is flagged as "Unhandled Promise Rejection" — the fix is to `await` the promise or use `expect().rejects`. [Source: https://vitest.dev/blog/vitest-5.html] As of v5.0, unawaited asynchronous assertions now fail the test outright (stricter than prior versions), reinforcing this as an anti-pattern to avoid.

[Source: https://vitest.dev/guide/common-errors.html] Setting `process.env.TZ` inside a setup file or test "has no effect on `Date` in `pool: 'threads'`" — documented as a common misconfiguration; timezone must be set before workers start, or a fork-based pool used instead.

[Source: https://vitest.dev/guide/common-errors.html] Relying on Node's native `fetch` together with `pool: 'threads'` is called out as a cause of "Failed to Terminate Worker" errors — documented as something to avoid or work around by switching to `pool: 'forks'` or `'vmForks'`.

## 7. Security

[Source: https://vitest.dev/config/api.html] Vitest's API server (used by the UI/IDE integrations) does not expose itself to the network by default — it listens on `localhost` only.

[Source: https://vitest.dev/config/api.html] If `api.host` is manually set to anything other than `localhost`/`127.0.0.1`, Vitest automatically sets both `api.allowWrite` and `api.allowExec` to `false` as a protective default; overriding these back to `true` while exposed to the network requires the operator to explicitly understand the security implications, since `allowWrite` "gives anyone who can connect to the API the ability to run any arbitrary code on your machine" (via saving test files/snapshots/browser attachments) and `allowExec` controls test execution via the UI, including indirect code-execution pathways through the Chrome DevTools Protocol.

[Source: https://vitest.dev/blog/vitest-5.html; corroborated via WebSearch of vitest.dev pages] Since Vitest 4.1, setting `api.host` to anything other than `localhost` disables the UI's buttons to save code or run tests, as a security hardening measure. [Version-sensitive: this specific UI-button gating is described as a 4.1-era change.]

[Source: https://vitest.dev/guide/browser/] Browser Mode custom commands run in the Vitest Node process and "can access local files, environment variables, network services, and databases." Vitest's own built-in file commands validate paths against Vite's `server.fs` restrictions, but user-authored custom commands do not automatically inherit those protections and require manual input validation — documented as a security responsibility placed on the command author.

[Source: https://vitest.dev/releases.html] Security patches are backported only to the current stable minor (`vitest@5.0`) and the immediately preceding minor (`vitest@4.1`); versions older than that are described as no longer receiving security fixes, which is itself a security-relevant operational fact for teams pinning old Vitest versions.

## 8. Performance

[Source: https://vitest.dev/guide/improving-performance.html] Pool choice is the primary performance lever: `forks` (default, safest for compatibility but can be slower), `threads` (often faster, more native-module/timer edge cases), `vmThreads` (best amortized cost for DOM-heavy suites via a shared VM context per file, but cannot disable isolation).

[Source: https://vitest.dev/guide/improving-performance.html] Disabling test isolation "will improve the speed of your tests" for suites that don't rely on isolation to reset shared state between files — but isolation cannot be turned off under `vmThreads` (use `threads` instead if isolation-off + VM reuse is desired). [Note: this is guidance, not a universal recommendation — teams must confirm their tests don't depend on isolation.]

[Source: https://vitest.dev/blog/vitest-5.html] v5.0 performance work: inline projects sharing the Vite server (reduced transform overhead), a filesystem module cache persisting transformed modules across runs, faster VM pools via compiled-code reuse and module-graph prewarming, Browser Mode prebundled runtime and adaptive session opening, and bundled dependencies to shrink `node_modules` size/resolution time. [Version-sensitive: all listed as v5.0-specific improvements relative to prior majors.]

[Source: https://vitest.dev/guide/coverage.html] Coverage-provider performance trade-off: V8 provider has "no pre-transpile step" (faster, lower memory, limited to V8-based runtimes) with report accuracy "as good as with Istanbul (since Vitest v3.2.0)" [version-sensitive parity claim]; Istanbul instruments source before execution (works on any JS runtime, higher memory overhead, but can be scoped to specific files to reduce cost on large codebases).

[Source: https://vitest.dev/guide/cli.html] `--shard=X/Y` combined with `--reporter=blob` and a later `--merge-reports` step is the documented mechanism for distributing large suites across parallel CI machines.

## 9. Testing

[Source: https://vitest.dev/guide/] Vitest is itself the unit-testing tool for JS/TS projects — "testing" as a dimension here covers how Vitest supports testing others' code rather than how Vitest is tested internally (which is Not documented / could not verify from the pages fetched — that would live in the vitest-dev/vitest contributor docs, not the user-facing docs surveyed here).

[Source: https://vitest.dev/guide/features.html] Supported testing modes/styles: standard unit tests (`test`/`it`, `describe`), snapshot testing (Jest-compatible), type testing via `expect-type` (`expectTypeOf`, `assertType`) to catch TypeScript type regressions, benchmarking via Tinybench (rewritten in v5.0 — see below), component testing for Vue/React/Svelte/Lit/Marko via Browser Mode, and in-source testing embedded in implementation files.

[Source: https://vitest.dev/blog/vitest-5.html] v5.0 rewrites benchmarking: `bench` is now a test-context fixture invoked within `test()` calls (rather than a standalone module-scope API), giving benchmarks access to fixtures, hooks, retries, and assertions; results support baseline comparison via `bench.from()`. [Version-sensitive: breaking change from pre-5.0 `bench()` usage — see §13.]

[Source: https://vitest.dev/guide/coverage.html] Coverage-based test-quality reporting is supported via `vitest run --coverage` with `v8` or `istanbul` providers, HTML/`html-spa`/`lcov`/JSON/custom reporters, and inline ignore comments (`/* v8 ignore if -- @preserve */`, `/* istanbul ignore start -- @preserve */ ... /* istanbul ignore stop -- @preserve */`) — the `@preserve` marker is required so TypeScript/esbuild transpilation doesn't strip the ignore comment.

[Source: https://vitest.dev/guide/browser/] Browser Mode testing runs tests directly inside a real browser (via Playwright, WebdriverIO, or a lightweight "Preview" provider) with native access to `window`/`document`, supporting visual regression testing and (v5.0) a Trace View recording "every interaction, assertion, and `page.mark`" with DOM snapshots for step-by-step replay in the browser UI, Vitest UI, and HTML reporter.

## 10. Deployment

[Source: https://vitest.dev/guide/cli.html] Vitest defaults to `vitest run` (single pass, no watch) automatically when run in a CI environment, and to watch mode in an interactive terminal — this CI-detection behavior is the primary "deployment" consideration for running Vitest in automated pipelines. Not documented / could not verify beyond this: Vitest's docs did not surface a dedicated "Deployment" guide page (Vitest is a dev/test-time tool, not a runtime service one deploys) — the closest first-party equivalents are the CI-oriented CLI flags (`--shard`, `--reporter=blob`, `--merge-reports`) and the coverage/reporter configuration covered in §4/§8.

[Source: https://vitest.dev/config/api.html] Where Vitest's UI/API server is run in a shared or CI/dev-container context accessible over a network (rather than purely local), the documented guidance is to keep `api.host` at `localhost`/`127.0.0.1`; if it must be exposed, `allowWrite`/`allowExec` default to disabled and should generally stay disabled (see §7).

## 11. Migration

[Source: https://vitest.dev/guide/migration.html] Migrating to Vitest 5.0 requires Vite >= 6.4.0 and Node.js >= 22.12.0; older versions "are unsupported and may cause unexpected errors."

[Source: https://vitest.dev/guide/migration.html] Documented v5.0 breaking changes for existing Vitest users (upgrading from v4.x): (1) `clearMocks` now defaults to `true` (`vi.clearAllMocks()` runs before every test) — set `clearMocks: false` to restore prior behavior; (2) the `-t` CLI test-name-pattern flag now matches the full suite-chain-plus-test-name joined by `' > '` rather than by spaces, so patterns like `'math adds'` must become `'math > adds'`; (3) inline projects now inherit root config by default (previously required explicit `extends: true`); (4) `vi.mock()`/`vi.unmock()`/`vi.hoisted()` calls must be at module scope, not inside functions/`describe` blocks (dynamic `vi.doMock`/`vi.doUnmock` remain flexible); (5) mocked classes now inherit from the real implementation's prototype, fixing `instanceof` checks and instance method availability; (6) the `bench()` API moved from module scope to a test-context fixture inside `test()`, with substantially changed comparison/reporter configuration; (7) Vitest UI now requires token authentication (browsers receive an authenticated URL automatically); (8) fake timers now also mock the Temporal API alongside `Date` (via `@sinonjs/fake-timers` v15.4).

[Source: https://vitest.dev/guide/migration.html] Additional v5.0 Browser Mode breaking changes: locators now serialize as objects with `selector` and `locator` properties; locators require exact text matches by default (previously loose); `toHaveTextContent` now performs strict equality (use the new `toMatchTextContent` for partial/regex matching); `render()` from `vitest-browser-vue` and `vitest-browser-svelte` is now async.

[Source: https://vitest.dev/guide/migration.html] Further v5.0 changes: generated report/artifact directories consolidate to a single `.vitest/` directory (e.g. screenshots default to `.vitest/attachments/failure-screenshots/`); worker and concurrency IDs are now 1-based (previously 0-based); coverage glob patterns now match paths relative to project root rather than using loose "contains" matching; several previously-deprecated entry points were removed entirely (specific removed entry points not enumerated in the fetched page — Not documented / could not verify the full list from this pass).

[Source: https://vitest.dev/guide/workspace.html] The `workspace` configuration concept was deprecated as of v3.2 and replaced by `projects` (functionally equivalent) — a version-sensitive rename relevant to anyone migrating configs written against v3.1 or earlier.

[Source: https://vitest.dev/guide/migration/jest.html] Migrating from Jest to Vitest: globals (`describe`/`it`/`expect`, etc.) are not enabled by default in Vitest — set `test.globals: true` or import them explicitly from `'vitest'`. Module-mock factory semantics differ: `jest.mock('./path', () => 'hello')` treats the return value as the default export, while Vitest's `vi.mock('./path', () => ({ default: 'hello' }))` requires an explicit export shape. Auto-mocking via `__mocks__` directories does not activate automatically — `vi.mock()` must be explicitly called. API renames: `jest.requireActual()` → `vi.importActual()`; `jest.setTimeout()` → `vi.setConfig({ testTimeout: ... })`; `jest.replaceProperty()` → `vi.stubEnv()`/`vi.spyOn()`. Callback-style tests (`it('x', (done) => {...})`) are not supported — must convert to Promise/async-await style. Hooks can now return teardown functions (a syntax consideration if a Jest hook previously returned something else for other reasons). Test hierarchy separators use `' > '` rather than spaces (affecting `-t` filtering, as also noted for the v4→v5 migration). Worker-identifying env vars are `VITEST_POOL_ID`/`VITEST_WORKER_ID`, replacing Jest's `JEST_WORKER_ID`. Vue snapshot serialization requires installing/configuring `jest-serializer-vue` separately; custom snapshot matchers import from `Snapshots` in `vitest` rather than `jest-snapshot`; Jest namespace type imports must shift to direct `vitest` imports.

## 12. Version information

[Source: https://vitest.dev/blog/vitest-5.html] Current stable major version (as of this research date, 2026-09-09): **Vitest 5.0**, released 2026-09-03, requiring Vite >= 6.4.0 and Node.js >= 22.12.0.

[Source: https://vitest.dev/releases.html] Release cadence, as stated in the official releases page: patch releases roughly weekly as needed; minor releases roughly every ~2 months (with a beta phase); major releases roughly yearly, timed to align with Vite's and Node.js's own EOL/support cycles, preceded by an extended beta-testing period.

[Source: https://vitest.dev/releases.html] Support/maintenance policy: the current minor of the latest major (`vitest@5.0`) receives ongoing regular patches; the previous major's latest minor (`vitest@4.1`) receives important fixes and security-patch backports only; versions older than that are unsupported. [Source: https://vitest.dev/releases.html] The page directs users to `github.com/vitest-dev/vitest/releases` for a comprehensive historical version/date table — that granular history was not independently re-verified line-by-line in this research pass. Not documented / could not verify: an explicit LTS designation or fixed EOL calendar date for any given major (the policy described is relative — "current major" and "previous major," not calendar-anchored) — this is a general release-cadence description, not a formal LTS table.

[Source: https://vitest.dev/blog/vitest-4-1.html title, surfaced via WebSearch] Vitest 4.1 exists as a distinct minor release predating 5.0 and is the version currently receiving security backports per §7/§12 above; the full content of the 4.1 announcement blog post itself was not fetched in this research pass, so specifics of what 4.1 introduced are Not documented / could not verify beyond its role as the security-backport target.

## 13. Breaking changes

[Source: https://vitest.dev/guide/migration.html and https://vitest.dev/blog/vitest-5.html] All items below are Vitest 5.0 breaking changes relative to the prior major (v4.x) — see the detailed list already given in §11, summarized here for reference: `clearMocks` defaults to `true`; `-t` pattern matching uses `' > '` suite-chain joins; inline projects inherit root config by default; `vi.mock()`/`vi.unmock()`/`vi.hoisted()` must be module-scope only; mocked classes inherit the real prototype (fixing `instanceof`); `bench()` moved to a test-context fixture with a new comparison/reporter shape; Vitest UI requires token auth; fake timers also mock the Temporal API; Browser Mode locators serialize differently and require exact matches by default; `toHaveTextContent` is now strict-equality (use `toMatchTextContent` for partial matches); framework `render()` helpers (`vitest-browser-vue`, `vitest-browser-svelte`) are now async; report/artifact directories consolidate under `.vitest/`; worker/concurrency IDs are now 1-based; coverage glob matching is now root-relative rather than "contains"-based; unawaited async assertions now fail tests; `expect.poll()` rejects on timeout and accepts an `AbortSignal`.

[Source: https://vitest.dev/guide/workspace.html] Separately, the `workspace` config key was deprecated in favor of `projects` as of v3.2 — a breaking-in-spirit rename (not removed as of the docs fetched, described as "functionally the same," but flagged in the migration-relevant docs).

[Unresolved: the exact list of "several deprecated entry points removed entirely" in v5.0, referenced by https://vitest.dev/guide/migration.html, was not itemized on the fetched page — could not verify which specific entry points these are without a deeper GitHub changelog pass beyond this research's scope.]

## 14. Limitations

[Source: https://vitest.dev/guide/common-errors.html] "CommonJS source code is not fully supported" — the module runner has incomplete CommonJS semantics; documented workarounds are disabling `experimental.viteModuleRunner` or externalizing CommonJS packages via `server.deps.inline`.

[Source: https://vitest.dev/guide/common-errors.html] Native Node.js addon modules "may fail in threaded environments due to lack of thread safety," causing segfaults under thread-based pools; switching to `pool: 'forks'` is the documented resolution — an inherent limitation of thread-based execution with non-thread-safe native code.

[Source: https://vitest.dev/guide/common-errors.html] `process.env.TZ` set inside a setup file/test "has no effect on `Date` in `pool: 'threads'`" — timezone must be set before worker threads start, or a fork-based pool used, documented as a limitation of the threads pool specifically.

[Source: https://vitest.dev/guide/browser/] In Browser Mode, thread-blocking dialogs (`alert`, `confirm`, `print`) "cannot be used natively as they prevent communication with the page." Module-export spying (`vi.spyOn()` on a module's exports) is restricted in Browser Mode because "the browser's native ESM module namespace cannot be reconfigured like Node.js does." Browser compatibility requires ES modules, dynamic imports, and `BroadcastChannel` support — minimum browser versions documented as Chrome >= 87, Firefox >= 79, Safari >= 15.4, Edge >= 88.

[Source: https://vitest.dev/guide/in-source.html] In-source testing has "a limitation when using assertion functions such as `assert`" (the fetched page did not fully elaborate the workaround inline, pointing to the API docs) — [Unresolved: the precise nature/scope of this `assert`-in-in-source-tests limitation was not fully captured from the page excerpt fetched].

[Source: https://vitest.dev/guide/workspace.html] Within a `projects` (workspace) setup, coverage, reporters, and snapshot path resolution are restricted to root-level configuration only — individual projects cannot override these, a documented structural limitation of the multi-project architecture.

## 15. Debugging

[Source: https://vitest.dev/guide/debugging.html] General recommendation: run with `--test-timeout=0` (disable timeouts while paused at a breakpoint) and `--no-file-parallelism` (avoid parallel test execution interfering with a single debug session).

[Source: https://vitest.dev/guide/debugging.html] VS Code: the official Vitest extension provides a "Debug Tests" button; alternatively, open a JavaScript Debug Terminal and run the test command directly. A documented manual `.vscode/launch.json` config: `{"type": "node", "request": "launch", "name": "Debug Current Test File", "program": "${workspaceRoot}/node_modules/vitest/vitest.mjs", "args": ["run", "${relativeFile}"]}`, triggered via F5.

[Source: https://vitest.dev/guide/debugging.html] Browser Mode debugging: use `--inspect-brk` with `--browser --no-file-parallelism`; Vitest defaults to port 9229, customizable via e.g. `--inspect-brk=127.0.0.1:3000`. VS Code compound configurations can attach to both the Node process and Chrome simultaneously.

[Source: https://vitest.dev/guide/debugging.html] Node Inspector / Chrome DevTools: `vitest --inspect-brk --no-file-parallelism` pauses execution for connection via `chrome://inspect`; `--isolate false` is recommended in watch mode to keep the debugger connection alive across reruns.

[Source: https://vitest.dev/guide/debugging.html] IntelliJ IDEA: create a Vitest run configuration pointing at the project root, then run in debug mode.

[Source: https://vitest.dev/guide/common-errors.html] The "Common Errors" page itself functions as an official debugging aid, documenting symptom → cause → fix for: module-resolution failures ("Cannot find module"), worker-termination failures, segfaults/native-code errors, timezone-in-workers issues, unhandled promise rejections, unresolved custom package conditions, packages that "fail to load in Vitest but work in your app," and incomplete CommonJS support.

## 16. Integration

[Source: https://vitest.dev/guide/ide.html] Official/documented editor integrations: the official VS Code extension (marketplace: `vitest.explorer`, source at `github.com/vitest-dev/vscode`); built-in Vitest support in JetBrains IDEs (WebStorm, PhpStorm, IntelliJ IDEA Ultimate); third-party Wallaby.js integration (VS Code, JetBrains, Visual Studio, Sublime Text) that runs tests live as you type.

[Source: https://vitest.dev/guide/browser/] Browser Mode integrates with three automation providers: Playwright (recommended, parallel execution, chromium/firefox/webkit), WebdriverIO (chrome/firefox/edge/safari), and a lightweight "Preview" provider (not recommended for CI, visualization only). Component-testing integration is documented for React, Vue, Svelte, Lit, and Marko, each requiring a framework-specific plugin.

[Source: https://vitest.dev/guide/why.html] Because Vitest reuses Vite's config/plugin pipeline, it integrates transparently with any Vite plugin ecosystem (framework plugins, path-alias resolvers, etc.) without separate test-specific tooling for the transform layer.

[Source: https://vitest.dev/guide/migration/jest.html] Jest-ecosystem integration/migration compatibility is explicitly documented (see §11) — Vitest is positioned as a near-drop-in replacement for Jest-based projects, including `expect`-API compatibility and a documented mapping of Jest APIs to Vitest equivalents.

[Source: https://vitest.dev/guide/coverage.html] Coverage integrates with two backend providers (v8, Istanbul) and multiple report formats (`html`, `html-spa`, `lcov`, JSON, JUnit, custom reporters via package name or local path), with HTML reports integrating directly into the Vitest UI.

## 17. Production considerations

[Source: https://vitest.dev/config/api.html] The single most explicit "production"-flavored consideration in the official docs is that Vitest's UI/API server must not be exposed to an untrusted network — see §7 for the `api.host`/`allowWrite`/`allowExec` defaults and risks. This is squarely about CI/shared-environment exposure rather than "production deployment" in the traditional sense, since Vitest itself is a development/test-time tool, not a service that runs in a deployed production application.

[Source: https://vitest.dev/guide/in-source.html] For teams using in-source testing, a production consideration is explicitly documented: test code embedded via `import.meta.vitest` must be stripped from production bundles using bundler `define` replacement (`{ 'import.meta.vitest': 'undefined' }` for Vite; documented equivalents given for Rolldown, Rollup, unbuild, and webpack) so dead-code elimination removes the test blocks from shipped code.

[Source: https://vitest.dev/releases.html] Production-adjacent maintenance consideration: only the current minor of the latest major and the previous major's latest minor receive security patches (§7/§12) — teams running Vitest in CI/production-adjacent pipelines on older majors are, per official policy, outside the security-patch window and should plan upgrades accordingly.

[Source: https://vitest.dev/guide/improving-performance.html] For CI/production-pipeline throughput, the officially recommended levers are pool selection (`forks` vs `threads` vs `vmThreads`), isolation toggling, filesystem/module caching, and sharding (`--shard`/`--reporter=blob`/`--merge-reports`) — see §8.
