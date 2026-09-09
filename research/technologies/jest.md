# Jest — Technology Research

Research date: 2026-09-09. Primary source: `jestjs.io` (the canonical, current Jest docs host — confirmed live and actively maintained). Supplementary authoritative sources: `github.com/jestjs/jest` (the official monorepo — note the GitHub organization is **`jestjs`**, not the historical `facebook`/`jestjs` legacy path; Jest is governed under the **OpenJS Foundation**, per its own blog/getting-started framing and its GitHub security policy referencing "the OpenJS Foundation CNA"), `registry.npmjs.org/jest` (official npm registry metadata, used only to confirm version/engines facts, not as a documentation citation), `archive.jestjs.io` and `jestjs.io/versions` (official archived-docs hosts for older major versions). Citation convention: `[Source: <url>] <claim>.` for documented facts, `[Inference, not confirmed in docs]` for reasoning not explicitly stated, `Not documented / could not verify` where no authoritative answer was found, `Unresolved: ...` where confidence is genuinely low.

**Doc host note:** [Source: https://jestjs.io/] No migration away from `jestjs.io` was found; it is the live, current docs host. Older major versions (22.x–24.x) are archived at `archive.jestjs.io`, and Jest 25–29.x line snapshots are reachable via a version picker at `jestjs.io/versions` (with a note that 29.6-and-older docs are served from a Netlify-hosted archive mirror). [Source: https://github.com/jestjs/jest] The GitHub organization itself is `jestjs/jest`; historically Jest's repo lived under `facebook/jest` — this run observed the canonical repo already at `jestjs/jest`, consistent with Jest's OpenJS Foundation governance, though the exact date of the org-rename was not independently verified from an official changelog entry. [Unresolved: exact date/announcement of the `facebook/jest` → `jestjs/jest` GitHub org transfer was not located in the fetched pages; the transfer itself is evidenced only by the current canonical URL and by `package.json`'s `repository.url` field on npm.]

**Version snapshot at research time:** [Source: https://registry.npmjs.org/jest] npm's `latest` dist-tag for the `jest` package is **30.5.1**, published 2026-09-01. [Source: https://registry.npmjs.org/jest] The published `engines.node` requirement for this version is `^18.14.0 || ^20.0.0 || ^22.0.0 || >=24.0.0`.

---

## 1. Core Concepts

[Source: https://jestjs.io/docs/getting-started] Jest is described as a JavaScript testing framework focused on simplicity, maintained under the OpenJS Foundation, that works with projects using Babel, TypeScript, Node, React, Angular, Vue, and more.

[Source: https://jestjs.io/docs/getting-started] Core built-in globals used to author tests: `test()` (alias `it()`), `describe()` for grouping, and `expect()` with chainable matchers (e.g., `.toBe()`) for assertions.

[Source: https://jestjs.io/docs/getting-started] Jest ships "zero configuration" for many JS projects — `npm install --save-dev jest`, add a `"test": "jest"` script to `package.json`, then `npm test` runs it. Test files are auto-discovered by filename convention (e.g. `*.test.js`, `*.spec.js`, or files in `__tests__/` directories).

[Source: https://jestjs.io/docs/getting-started] Jest automatically sets `process.env.NODE_ENV` to `'test'` when running.

[Source: https://jestjs.io/docs/getting-started] Jest automatically uses `babel-jest` for transformation when a Babel configuration exists in the project; TypeScript is supported either via Babel, via the community package `ts-jest`, or by using type definitions from `@jest/globals`/`@types/jest`.

[Source: https://jestjs.io/docs/snapshot-testing] A signature Jest feature is **snapshot testing** — capturing a serializable representation of a value/component's output into a committed `.snap` file and comparing future runs against it, to catch unintended changes.

[Source: https://jestjs.io/docs/mock-functions] Another signature feature is **built-in mocking** — `jest.fn()` for standalone mock functions, `jest.mock()` for module-level mocking (with automocking support), and `jest.spyOn()` for spying on existing object methods — without requiring a separate mocking library.

[Source: https://jestjs.io/docs/setup-teardown] Jest provides lifecycle hooks (`beforeEach`, `afterEach`, `beforeAll`, `afterAll`) and `describe()` blocks for scoping setup/teardown logic per test or per group of tests.

---

## 2. Architecture

[Source: https://jestjs.io/docs/architecture] Jest's own "Architecture" doc page is largely a pointer to external material — it links to a video explaining "how Jest works, its architecture, and how it's split into reusable packages," a video on building a testing framework from scratch, and a written guide by Jest's original creator at `cpojer.net/posts/building-a-javascript-testing-framework` (not an `jestjs.io`-hosted page, so not used here as a primary citation for specific architectural claims). The one explicit, directly-stated claim from the page itself is that **Jest is built as a modular platform composed of independent, reusable packages** that can be used together or separately.

[Source: https://github.com/jestjs/jest packages directory listing, retrieved 2026-09-09] The monorepo (`jestjs/jest`) is organized as a set of scoped packages under `packages/`, including (non-exhaustive, as observed at research time): `jest` (the umbrella CLI package), `jest-cli`, `jest-core`, `jest-config`, `jest-runtime`, `jest-circus` (the default test runner/framework since Jest 27), `jest-jasmine2` (legacy/optional test runner), `jest-runner` (orchestrates per-test-file worker execution), `jest-worker` (parallel worker-process pool), `jest-resolve` / `jest-resolve-dependencies` (module resolution), `jest-haste-map` (fast file-system/module map, originally from Facebook's Haste), `jest-environment-node` / `jest-environment-jsdom` / `jest-environment-jsdom-abstract` / `jest-environment` (pluggable test environments), `jest-snapshot` / `jest-snapshot-utils` (snapshot testing), `expect` / `expect-utils` (assertion library, usable standalone), `jest-mock` (mock function implementation), `jest-fake-timers` (fake timer implementation), `jest-transform` (code transformation pipeline), `babel-jest` / `babel-plugin-jest-hoist` / `babel-preset-jest` (default Babel-based transform, including the hoisting transform that moves `jest.mock()` calls above imports), `jest-watcher` (watch-mode UI), `jest-reporters`, `jest-changed-files`, `jest-test-sequencer`, `pretty-format` (snapshot/error-message serialization), and others.

[Source: https://jestjs.io/docs/code-transformation] Architecturally, source files are transformed **on-demand** at `require`/`import` evaluation time (not pre-bundled ahead of time), and transform outputs are cached, invalidated by source content and configuration changes.

[Source: https://jestjs.io/docs/cli, https://jestjs.io/docs/configuration] Test execution is parallelized across **worker processes** (`jest-worker`); `maxWorkers` controls the pool size (default: CPU core count minus one, for the main process, in normal — non-CI-single-run — mode; accepts a percentage string like `'50%'`). `--runInBand` forces serial, single-process execution (used for debugging).

[Source: https://jestjs.io/docs/configuration] Each **test environment** (`testEnvironment: 'node' | 'jsdom' | <custom path>`) provides the global object a test file runs against (e.g. jsdom's simulated `window`/`document` vs. Node's bare global scope); custom environments are pluggable via a module path.

[VERSION-SENSITIVE, Source: https://jestjs.io/blog/2021/05/25/jest-27] As of Jest 27, the default test **runner** is `jest-circus` (previously the default was `jest-jasmine2`, a fork of Jasmine 2.0); `jest-jasmine2` remains available/configurable via `testRunner`.

---

## 3. APIs

### Global test API
[Source: https://jestjs.io/docs/getting-started, https://jestjs.io/docs/setup-teardown] `test()`/`it()` (with `.only`, `.skip`, `.todo`, `.each`, `.concurrent` modifiers), `describe()` (with `.only`, `.skip`, `.each`), `beforeEach()`, `afterEach()`, `beforeAll()`, `afterAll()`.

### `expect` / matchers
[Source: https://jestjs.io/docs/expect] Categories with representative matchers:
- **Equality**: `.toBe()` (referential/`Object.is`), `.toEqual()` (deep equality), `.toStrictEqual()` (deep equality plus type/undefined-property/array-sparseness strictness)
- **Truthiness**: `.toBeTruthy()`, `.toBeFalsy()`, `.toBeNull()`, `.toBeDefined()`, `.toBeUndefined()`
- **Numbers**: `.toBeCloseTo()`, `.toBeGreaterThan()`, `.toBeGreaterThanOrEqual()`, `.toBeLessThan()`, `.toBeLessThanOrEqual()`, `.toBeNaN()`
- **Strings**: `.toMatch()`
- **Arrays/Iterables**: `.toContain()`, `.toContainEqual()`, `.toHaveLength()`
- **Objects**: `.toHaveProperty()`, `.toMatchObject()`
- **Exceptions**: `.toThrow()`, `.toThrowErrorMatchingSnapshot()`, `.toThrowErrorMatchingInlineSnapshot()`
- **Mock functions**: `.toHaveBeenCalled()`, `.toHaveBeenCalledTimes()`, `.toHaveBeenCalledWith()`, `.toHaveBeenLastCalledWith()`, `.toHaveReturned()`, `.toHaveReturnedWith()`
- **Asymmetric matchers**: `expect.anything()`, `expect.any(constructor)`, `expect.stringContaining()`, `expect.stringMatching()`, `expect.objectContaining()`, `expect.arrayContaining()`, `expect.closeTo()`, and (new in v30) `expect.arrayOf()` — see Breaking Changes.
- **Snapshots**: `.toMatchSnapshot()`, `.toMatchInlineSnapshot()`
- **Modifiers**: `.not`, `.resolves`, `.rejects`

### Mock functions API
[Source: https://jestjs.io/docs/mock-functions] `jest.fn(implementation?)` creates a mock function; every mock exposes a `.mock` object with `.calls`, `.results`, `.instances`, `.contexts`, and `.lastCall`. Configuration methods: `.mockReturnValue()`/`.mockReturnValueOnce()`, `.mockImplementation()`/`.mockImplementationOnce()`, `.mockReturnThis()`, `.mockName()`. [Source: https://jestjs.io/docs/mock-functions] `jest.mock(moduleName, factory?)` mocks an entire module (auto-mocked if no factory given); `jest.requireActual(moduleName)` retrieves the real, unmocked module (used for partial mocking); `jest.spyOn(object, methodName)` wraps an existing method while tracking calls, and can be restored via `.mockRestore()`. [Source: https://github.com/jestjs/jest CHANGELOG, https://jestjs.io/blog/2025/06/04/jest-30] **New in v30.5.0**: `mockFn.whenCalledWith(...)` for per-argument return-value configuration. [VERSION-SENSITIVE]

### Fake timers API
[Source: https://jestjs.io/docs/timer-mocks] `jest.useFakeTimers(options?)` / `jest.useRealTimers()`; `jest.runAllTimers()`, `jest.runOnlyPendingTimers()`, `jest.advanceTimersByTime(ms)`, `jest.clearAllTimers()`; options include `timerLimit` and `doNotFake: string[]` (to exclude specific timer-related globals from faking). [Source: https://jestjs.io/blog/2025/06/04/jest-30] **New in v30**: `jest.advanceTimersToNextFrame()` — advances pending `requestAnimationFrame` callbacks to the next frame boundary, ported from `@sinonjs/fake-timers` v13. [VERSION-SENSITIVE]

### Module transform API
[Source: https://jestjs.io/docs/code-transformation] Custom transformers implement `process(sourceText, sourcePath, options)` (sync, returns `{code, map?}`) and/or `processAsync()` (for native ESM `import`/`import()`), plus `getCacheKey()` (cache invalidation) and an optional `canInstrument` flag (coverage-instrumentation support).

### CLI
[Source: https://jestjs.io/docs/cli] Selected flags: `--watch` / `--watchAll`, `--runInBand`/`-i`, `--onlyChanged`/`-o`, `--onlyFailures`/`-f`, `--coverage`/`--collectCoverage`, `--coverageProvider=<babel|v8>`, `--testNamePattern=<regex>`/`-t`, `--testPathPatterns=<regex>` (renamed from `--testPathPattern` in v30 — see Breaking Changes), `--ci`, `--shard=<i>/<n>`, `--maxWorkers=<n|%>`, `--detectOpenHandles`, `--debug`, `--verbose`, `--config`/`-c`, `--env=<environment>`, `--updateSnapshot`/`-u`, `--forceExit`, `--bail[=<n>]`/`-b`, `--clearCache`, `--listTests`, `--json`, `--showConfig`.

### ESM-specific API
[Source: https://jestjs.io/docs/ecmascript-modules] `jest.unstable_mockModule(moduleName, factory)` — the ESM-compatible equivalent of `jest.mock()` (must be paired with dynamic `import()` after the mock is registered, since static imports are evaluated before `jest.mock` hoisting can apply). `import.meta.jest` — alternate way to access the `jest` object under native ESM, alongside importing `jest` from `@jest/globals`. [Source: https://jestjs.io/blog/2025/06/04/jest-30] **New in v30**: `jest.unstable_unmockModule()` for finer-grained unmocking control, plus `jest.onGenerateMock(callback)` for hooking automock generation.

### Getting-started CLI scaffolding
[Source: https://jestjs.io/docs/getting-started, https://jestjs.io/docs/upgrading-to-jest30] The former `jest --init` interactive config generator has been **removed in v30**; the documented replacement is `npm init jest@latest` / `yarn create jest` / `pnpm create jest`. [VERSION-SENSITIVE]

---

## 4. Configuration

[Source: https://jestjs.io/docs/configuration] Configuration is read from (in order of Jest's own resolution): a `jest.config.js|ts|mjs|mts|cjs|cts|json` file, a `"jest"` key in `package.json`, or an explicit `--config` CLI flag. [Source: https://jestjs.io/blog/2025/06/04/jest-30] **New in v30**: Jest config files may be authored in **TypeScript** natively.

Selected options (non-exhaustive; grouped by area), all `[Source: https://jestjs.io/docs/configuration]` unless otherwise noted:

**Core / execution**: `automock` (boolean, default `false`), `bail` (number|boolean, default `0` — stop after N failing test suites; documented as a root/global-only option, ignored inside individual `projects` entries per GitHub PR discussion), `cacheDirectory` (default an OS tmp path), `clearMocks`/`resetMocks`/`restoreMocks` (booleans, default `false`), `displayName` (string or object, labels test output — used heavily with `projects`), `errorOnDeprecated` (boolean, default `false`), `globals` (object, default `{}`), `injectGlobals` (boolean, default `true`), `maxConcurrency` (number, default `5` — caps `test.concurrent`), `maxWorkers` (number or percentage string, default CPU-count-minus-one), `rootDir`, `roots` (default `["<rootDir>"]`), `verbose` (boolean, default `false`), `testTimeout` (number, default `5000` ms).

**Module resolution**: `moduleDirectories` (default `["node_modules"]`), `moduleFileExtensions` (default includes `js, mjs, cjs, jsx, ts, mts, cts, tsx, json, node` — `.mts`/`.cts` added as defaults in v30, see Breaking Changes), `moduleNameMapper` (object mapping regex → module path/array of paths, for stubbing assets like images/CSS), `modulePathIgnorePatterns`, `modulePaths`, `resolver` (custom resolver module path — Jest 30 uses `unrs-resolver` internally for faster resolution, per the v30 blog post).

**Test discovery**: `testMatch` (glob array, default `["**/__tests__/**/*.?([mc])[jt]s?(x)", "**/?(*.)+(spec|test).?([mc])[jt]s?(x)"]`), `testRegex`, `testPathIgnorePatterns` (default `["/node_modules/"]`), `testRunner` (default `"jest-circus/runner"`), `testSequencer` (default `"@jest/test-sequencer"`), `testFailureExitCode` (default `1`).

**Environment**: `testEnvironment` (default `"node"` — see version note below), `testEnvironmentOptions` (object; jsdom example fields include `html`, `url`, `userAgent`).

**Transformation**: `transform` (object mapping regex → transformer module, default `{"\\.[jt]sx?$": "babel-jest"}`), `transformIgnorePatterns` (default `["/node_modules/", "\\.pnp\\.[^\\/]+$"]`), `extensionsToTreatAsEsm` (default `[]`).

**Setup/teardown**: `setupFiles` (run before the test framework loads), `setupFilesAfterEnv` (run after the framework is set up — v30 allows these to be/use async functions or top-level `await`, see Breaking Changes), `globalSetup`, `globalTeardown`.

**Coverage**: `collectCoverage` (boolean, default `false`), `collectCoverageFrom` (glob array), `coverageDirectory`, `coveragePathIgnorePatterns` (default `["/node_modules/"]`), `coverageProvider` (`"babel"` or `"v8"`, default `"babel"` per the fetched docs — flag as version-sensitive since Jest has changed coverage-related defaults across majors and this specific default should be re-verified against the exact minor in use), `coverageReporters` (default `["clover", "json", "lcov", "text"]`), `coverageThreshold` (object of per-metric minimums).

**Snapshots**: `snapshotFormat` (default `{escapeString: false, printBasicPrototype: false}`), `snapshotResolver`, `snapshotSerializers`.

**Preset / multi-project**: `preset`, `projects` (array of per-project config objects/paths, each can specify its own `runner`, e.g. `jest-runner-eslint`, enabling running e.g. tests and lint as separate "projects" in one invocation).

**Timers/async**: `fakeTimers` (object; e.g. `{doNotFake: [...], timerLimit, enableGlobally}`), `waitForUnhandledRejections` (boolean — new in v30, see Breaking Changes).

**Watch mode**: `watchPathIgnorePatterns`, `watchPlugins`, `watchman` (boolean, default `true`).

**Misc**: `dependencyExtractor`, `forceCoverageMatch`, `haste` (Haste module-map config), `prettierPath` (default `"prettier"`), `randomize` (boolean, default `false` — randomizes test order), `showSeed` (boolean, default `false`), `runtime` (default `"jest-runtime"`), `runner` (default `"jest-runner"`), `sandboxInjectedGlobals`, and (per the v30 blog/changelog) `workerIdleMemoryLimit` and `workerGracefulExitTimeout` for worker memory/exit management. [Source: https://jestjs.io/blog/2025/06/04/jest-30] `testEnvironmentOptions.globalsCleanup` (`'on' | 'soft' | 'off'`) — new in v30, controls cleanup of environment globals between test files; `'soft'` is the current default with `'on'` flagged as "the future default."

[VERSION-SENSITIVE, Source: https://jestjs.io/blog/2021/05/25/jest-27] `testEnvironment` default changed from `"jsdom"` (pre-v27) to `"node"` (v27+), because jsdom has performance overhead and isn't needed for non-DOM tests; projects needing DOM APIs must explicitly set `testEnvironment: "jsdom"` (and install `jest-environment-jsdom` as a separate package, since v27 also stopped bundling jsdom by default per the same blog post's framing — [Inference, not confirmed explicitly in the fetched excerpt] that the package must be installed separately, though the blog text fetched did not explicitly confirm the separate-install requirement in the excerpt retrieved). Fake timers also defaulted to the "modern" implementation starting in v27 (previously "legacy"), configurable via `jest.useFakeTimers('legacy')` or `timers: 'legacy'`.

---

## 5. Recommended Patterns

[Source: https://jestjs.io/docs/snapshot-testing] Treat snapshots as code: commit them to version control, review them in code review like any other diff, and keep them **short and focused** rather than large/unfocused (the docs specifically recommend tools like `eslint-plugin-jest`'s `no-large-snapshots` rule to enforce this).

[Source: https://jestjs.io/docs/snapshot-testing] Ensure snapshot tests are deterministic — mock non-deterministic values (e.g., `Date.now = jest.fn(() => 1_482_363_367_071)`) and use **property matchers** (e.g. `expect(user).toMatchSnapshot({createdAt: expect.any(Date), id: expect.any(Number)})`) for fields that legitimately vary between runs.

[Source: https://jestjs.io/docs/snapshot-testing] Use descriptive snapshot names/hints rather than vague ones, to make failures self-explanatory in review.

[Source: https://jestjs.io/docs/mock-functions] Prefer injecting test values directly over implementing real logic inside mock implementations; use `.mockName()` to make failure output clearer; prefer `jest.requireActual()` for partial-mocking a module rather than reimplementing the whole module surface.

[Source: https://jestjs.io/docs/testing-asynchronous-code (fetched via https://jestjs.io/docs/tutorial-async)] Always `return` or `await` promises inside async tests, and pair with `expect.assertions(n)` to guard against a test silently passing because its assertion callback never actually ran (e.g. inside a `.then()`/`.catch()` that Jest didn't wait for).

[Source: https://jestjs.io/docs/setup-teardown] Scope `beforeEach`/`afterEach`/`beforeAll`/`afterAll` inside `describe()` blocks when setup is only relevant to a subset of tests, rather than applying global top-level hooks to unrelated tests.

[Source: https://jestjs.io/docs/setup-teardown] Use `test.only()` to isolate a single failing test when debugging suspected test-interdependency/state-leak issues.

[Source: https://jestjs.io/docs/code-transformation] Always implement `getCacheKey()` on custom transformers to avoid wasteful re-transpilation; use `--no-cache` only during transformer development.

[Source: https://jestjs.io/docs/webpack] For CSS Modules under Jest, use `identity-obj-proxy` via `moduleNameMapper` so class-name assertions/snapshots remain meaningful (`styles.foobar === 'foobar'`) rather than resolving to opaque hashes.

---

## 6. Anti-Patterns

[Source: https://jestjs.io/docs/snapshot-testing] Blindly regenerating/accepting failing snapshots (`--updateSnapshot`) without inspecting *why* they changed is called out — the docs frame snapshot failures as a signal to fix the root cause first, not just approve the diff.

[Source: https://jestjs.io/docs/snapshot-testing] Relying on CI to auto-update snapshots is a documented pitfall — snapshots are explicitly **not** auto-written in `--ci` mode; a missing/mismatched snapshot fails the build instead, by design (see CI section of CLI docs).

[Source: https://jestjs.io/docs/testing-asynchronous-code (via tutorial-async)] Not returning/awaiting a promise from an async test is called out as a correctness pitfall: Jest can finish (and report the test as passing) before the promise settles and its assertions actually execute.

[Source: https://github.com/jestjs/jest CHANGELOG / https://jestjs.io/blog/2025/06/04/jest-30] Relying on deprecated `expect` matcher aliases (`toBeCalled`, `toBeCalledWith`, `lastCalledWith`, `nthCalledWith`, `toReturn`, `toReturnTimes`, `toReturnWith`, `lastReturnedWith`, `nthReturnedWith`, `toThrowError`) is now a hard break as of v30 — these aliases were **removed**, not merely deprecated. [VERSION-SENSITIVE: only applies from v30 onward; they existed as working aliases through v29.]

[Source: https://jestjs.io/docs/upgrading-to-jest30] Reaching into Jest's internal module paths (e.g. `require('jest-runner/build/testWorker')`) instead of Jest's public API surface is flagged as fragile — v30's internal bundling of each package into single files broke such unofficial deep imports.

---

## 7. Security

[Source: https://github.com/jestjs/jest/security/policy] Jest's security policy requests that vulnerabilities be reported **privately** via GitHub's "Report a vulnerability" form on the repository's Security tab rather than as public issues, including: affected project/repo and version(s), impact and component(s) involved, reproduction steps/PoC if available, and contact/credit preference. If no acknowledgement arrives within 6 business days (or no private security contact can be found), reporters may escalate to the OpenJS Foundation CNA at `security@lists.openjsf.org`; a further escalation path exists if the project acknowledges but goes 14+ days without follow-up engagement. Once fixed, the project states it will "publish a security advisory (and CVE via the OpenJS CNA when applicable)," and credits reporters by default unless anonymity is requested.

[Source: https://jestjs.io/docs/configuration] Beyond the vulnerability-reporting policy, `jestjs.io`'s own docs do not present a dedicated "security" guide for using Jest (e.g., no documented guidance on sandboxing test code, executing untrusted test files, or securing CI credentials used during test runs). Not documented / could not verify: any Jest-specific guidance on running tests against untrusted/third-party code, isolating test-environment globals from the host OS beyond what jsdom/node environment sandboxing inherently provides, or supply-chain security recommendations for transform/reporter/watch plugins (which execute arbitrary code inside the Jest process).

---

## 8. Performance

[Source: https://jestjs.io/blog/2025/06/04/jest-30] Jest 30 is presented as measurably faster and leaner than v29: module resolution was rewritten on top of `unrs-resolver` for more standards-compliant, faster resolution; a cited real-world TypeScript-app benchmark showed **~37% faster** server tests (~1350s → ~850s) and **~77% lower memory usage** (7.8 GB → 1.8 GB) after upgrading. [VERSION-SENSITIVE: specific to the v30 release and the cited benchmark app; not a universal guarantee.]

[Source: https://jestjs.io/docs/cli, https://jestjs.io/docs/configuration] Parallelism is controlled via `maxWorkers` (worker-process pool size, default CPU-cores-minus-one; accepts absolute numbers or percentages like `'50%'`); `--runInBand`/`-i` disables parallelism entirely (useful for debugging, not for normal throughput). `maxConcurrency` (default `5`) caps how many `test.concurrent` tests run concurrently within a single test file/worker.

[Source: https://jestjs.io/blog/2025/06/04/jest-30, per changelog summary] `workerIdleMemoryLimit` and `workerGracefulExitTimeout` exist as configuration knobs to manage worker memory growth/exit behavior — useful for large suites where workers can leak memory across many test files.

[Source: https://jestjs.io/docs/cli] `--detectOpenHandles` carries an explicitly documented performance penalty and is intended for diagnosing dangling handles (unclosed timers/servers/connections) preventing clean process exit, not for routine runs.

[Source: https://jestjs.io/docs/configuration] `slowTestThreshold` (default `5` seconds) flags individual slow tests in output; `bail` (stop after N failing suites) can shorten CI feedback loops by skipping the remainder of a run once failures are detected.

[VERSION-SENSITIVE, Source: https://jestjs.io/blog/2021/05/25/jest-27] Since v27, `testEnvironment` defaults to `node` rather than `jsdom` specifically because jsdom carries meaningful per-test performance overhead that's unnecessary for non-DOM code — a documented performance-motivated default change.

---

## 9. Testing

*(This dimension is effectively Jest's entire subject matter — Jest is a testing framework — so this section documents Jest's own test-authoring model rather than "how to test Jest" as external software.)*

[Source: https://jestjs.io/docs/getting-started] Basic unit test shape: `test('description', () => { expect(actual).toBe(expected); })`, auto-discovered via filename convention.

[Source: https://jestjs.io/docs/setup-teardown] Execution model: all `describe()` blocks are evaluated first (synchronously, to build the test tree), then tests run serially in encountered order; hook nesting order is outer `beforeEach` → inner `beforeEach` → test body → inner `afterEach` → outer `afterEach`, with `afterAll` hooks in nested scopes running in reverse declaration order.

[Source: https://jestjs.io/docs/testing-asynchronous-code (via tutorial-async)] Async test patterns: returning a promise, `async`/`await`, `.resolves`/`.rejects` matchers, and callback-style error handling via `try/catch` inside an `async` test function — paired with `expect.assertions(n)` to guard against assertions inside unreached callback branches.

[Source: https://jestjs.io/docs/mock-functions] Manual mocks live in a `__mocks__/` directory adjacent to the mocked module for node_modules packages, or adjacent to the source file for user modules, and are picked up automatically once `jest.mock(moduleName)` is called (for node_modules packages, some manual-mock scenarios require the explicit `jest.mock()` call; user-module manual mocks in some configurations are picked up without an explicit call — the exact automatic-vs-explicit distinction by mock location was described in general terms in the source but not exhaustively re-verified against the current doc's precise wording, so treat the precise auto-application rule per location as **Unresolved: exact automatic-application semantics for manual mocks by directory location (node_modules vs. user modules) should be re-checked against the current `https://jestjs.io/docs/manual-mocks` page text before relying on it exactly**).

[Source: https://jestjs.io/docs/timer-mocks] Fake timers (`jest.useFakeTimers()`) let time-dependent code (timeouts, intervals, `requestAnimationFrame`) be tested deterministically without real elapsed time, via `runAllTimers()`, `runOnlyPendingTimers()`, `advanceTimersByTime()`, and (v30+) `advanceTimersToNextFrame()`.

[Source: https://jestjs.io/docs/configuration, https://jestjs.io/docs/cli] Coverage collection (`--coverage`/`collectCoverage`) instruments code via either `babel` (default) or `v8` coverage providers, with configurable thresholds (`coverageThreshold`) that can fail a run if not met.

---

## 10. Deployment

Not directly applicable in the conventional sense — Jest is a developer-time/CI-time testing tool, not something an application deploys to production. [Source: https://jestjs.io/docs/cli] The closest analogue documented is running Jest inside CI pipelines: `--ci` mode changes behavior around snapshots (new/mismatched snapshots fail the run instead of being written), and `--shard=<i>/<n>` supports splitting a large suite across parallel CI machines/jobs. [Source: https://jestjs.io/docs/configuration] `testResultsProcessor` and `reporters` allow piping Jest's results into external CI reporting/analytics tooling. No dedicated official "Continuous Integration" doc page was found at the expected `jestjs.io/docs/continuous-integration` URL (returned 404 at research time); CI guidance is embedded within the CLI and configuration docs rather than as a standalone page.

---

## 11. Migration

[Source: https://jestjs.io/docs/migration-guide] Jest's official migration guide covers moving *to* Jest from other test frameworks/libraries: **Jasmine** (and Jasmine-like APIs, including Mocha — described as "mostly compatible," making direct migration comparatively easy), **Mocha**, **AVA**, **Expect.js** (by Automattic), **Chai**, **proxyquire**, **Should.js**, **Tape**, and **Sinon**. For most of these, the documented path is the community tool **`jest-codemods`** (`npx jest-codemods`, built on `jscodeshift`) which automatically transforms existing test code. For Chai specifically, the guide notes users can keep using Chai assertions alongside Jest, but recommends trying Jest's built-in `expect` assertions/failure messages instead.

[Source: https://jestjs.io/docs/upgrading-to-jest30] For **upgrading Jest itself** (v29 → v30), the official upgrade guide documents: minimum Node.js and TypeScript version bumps, removed matcher aliases, the `--testPathPattern` → `--testPathPatterns` CLI rename, removal of `jest --init` (replaced by `npm init jest@latest` etc.), removal of `jest.genMockFromModule` (replaced by `jest.createMockFromModule`), removed TypeScript types (`MockFunctionMetadata`, `MockFunctionMetadataType`, `SpyInstance` → replaced by `jest.Spied<T>`), case-sensitive module-path matching for `jest.mock()` (previously case-insensitive on some filesystems), new default file extensions affecting `moduleFileExtensions`/`testMatch`/`testRegex` (`.mjs`, `.cjs`, `.mts`, `.cts`), changed custom `TestSequencer` signatures (now receiving `globalConfig` and `contexts`), a `Runtime` constructor now requiring a `globalConfig` parameter, and a glob-engine upgrade (glob v10) that can change brace-expansion/extglob matching behavior in custom patterns. Full details in Breaking Changes below.

---

## 12. Version Information

[Source: https://registry.npmjs.org/jest] Current stable version as of 2026-09-09: **30.5.1** (published 2026-09-01). [Source: https://registry.npmjs.org/jest] The `next` dist-tag at time of research pointed to `30.0.0-rc.1` — [Inference, not confirmed in docs] this `next` tag value looks stale relative to `latest` being 30.5.1, suggesting the `next` pre-release tag has not been actively updated since before the 30.0.0 stable release, rather than reflecting an upcoming v31 pre-release; treat this as **Unresolved: whether Jest has any v31 pre-release work in progress was not confirmed** from the fetched registry data alone.

[Source: https://github.com/jestjs/jest/blob/main/CHANGELOG.md] Release cadence around the v30 line, most-recent-first as observed: 30.5.1 → 30.5.0 → 30.4.2 → 30.4.1 → 30.4.0 → 30.3.0 → 30.2.0 → 30.1.x → 30.0.0, indicating roughly monthly-or-more-frequent minor/patch releases within a major line. [VERSION-SENSITIVE: this cadence describes the v30.x line specifically; not necessarily representative of prior majors.]

[Source: https://jestjs.io/versions] The docs site's version picker shows "Next" (unreleased/main), the current stable line (30.5.x at research time), prior 30.x minors, and the 29.7 line as the last of the previous major, with 29.6-and-older docs served from an archived Netlify mirror, and pre-25.x lines (24.x, 23.x, 22.x) served from `archive.jestjs.io`.

[Source: https://registry.npmjs.org/jest] `engines.node` for 30.5.1 is `^18.14.0 || ^20.0.0 || ^22.0.0 || >=24.0.0`. Not documented / could not verify: an explicit "LTS" or formal support-window policy (e.g., "we support the last N majors for M months") on `jestjs.io` itself — no such support-window statement was found in the fetched pages; Jest's practical support signal is which Node majors remain in its `engines` field per release, not a stated LTS policy of Jest's own versions.

---

## 13. Breaking Changes

All items below are `[Source: https://jestjs.io/blog/2025/06/04/jest-30]` and/or `[Source: https://jestjs.io/docs/upgrading-to-jest30]`, and are **version-sensitive to the v29 → v30 major transition** specifically:

- **Runtime requirements**: Dropped Node.js 14, 16, 19, and 21 (engines field requires `^18.14.0 || ^20.0.0 || ^22.0.0 || >=24.0.0`); minimum TypeScript raised to **5.4**; `jest-environment-jsdom` upgraded from jsdom 21 to **jsdom 26** (documented as introducing jsdom spec-compliance changes, e.g. to `window.location` mocking, with a workaround via `@jest/environment-jsdom-abstract` or a linked community patch).
- **Removed `expect` matcher aliases**: `toBeCalled`, `toBeCalledTimes`, `toBeCalledWith`, `lastCalledWith`, `nthCalledWith`, `toReturn`, `toReturnTimes`, `toReturnWith`, `lastReturnedWith`, `nthReturnedWith`, `toThrowError` — all removed; use their canonical `toHaveBeen...`/`toThrow` equivalents (auto-fixable via `eslint-plugin-jest`'s `no-alias-methods` rule).
- **Matcher semantics**: non-enumerable object properties are now excluded by default from matchers like `toEqual`/`objectContaining`; TypeScript typing for `toHaveBeenCalledWith` is stricter and may surface new type errors.
- **CLI**: `--testPathPattern` renamed to `--testPathPatterns` (now accepting multiple patterns); `jest --init` removed (replaced by `npm init jest@latest`/`yarn create jest`/`pnpm create jest`); CLI flags requiring arguments must include explicit values; custom `--filter` implementations must return `{filtered: Array<string>}`.
- **Module/mock APIs**: `jest.genMockFromModule` removed, replaced by `jest.createMockFromModule`; TypeScript types `MockFunctionMetadata`, `MockFunctionMetadataType`, `SpyInstance` removed, replaced by `jest.Spied<T>`; module-path matching for `jest.mock()` is now case-sensitive.
- **Default file extensions**: `moduleFileExtensions` now defaults to include `.mts`/`.cts`; default `testMatch`/`testRegex` now also recognize `.mjs`, `.cjs`, `.mts`, `.cts` files as potential test files — projects with such files not intended as tests need explicit config adjustment.
- **Async handling**: Jest now waits an additional event-loop turn before failing on a promise rejection, to avoid false positives for rejections that are handled asynchronously (governed by the new `waitForUnhandledRejections` config, enabled by default per the upgrade guide — note this default value differs slightly from the earlier `configuration`-doc default table fetched, which listed `waitForUnhandledRejections` default as `false`; **flagging as Unresolved: the upgrade guide's summarized text and the configuration reference table disagree on this option's default — verify directly against `https://jestjs.io/docs/configuration#waitforunhandledrejections-boolean` before depending on the exact default**).
- **Custom `TestSequencer`**: now receives additional `globalConfig` and `contexts` arguments — custom implementations must be updated.
- **`Runtime` constructor**: now requires a `globalConfig` parameter when constructed programmatically.
- **Snapshots**: error `cause` property now included in snapshots; React empty-string (`""`) children no longer rendered in snapshot output; `ArrayBuffer`/`DataView` now print in a more human-readable format; deprecated `goo.gl` short-link references in old snapshot format required snapshot regeneration.
- **Internal bundling**: each Jest package is now bundled into a single file internally (for faster startup) — this breaks unofficial deep imports into Jest's internal module structure (e.g. `require('jest-runner/build/testWorker')`); only the public API surface is guaranteed stable.
- **Dependency upgrade**: glob engine bumped to v10, with stricter brace-expansion/extglob handling that can change matching behavior for custom `testMatch`/`moduleNameMapper`/glob-based patterns.

[Source: https://jestjs.io/blog/2025/06/04/jest-30] New (additive, non-breaking) v30 features worth tracking for version-sensitivity when reading examples from older tutorials: `using spy = jest.spyOn(...)` (explicit-resource-management-based auto-restoring spies), `expect.arrayOf()` asymmetric matcher, `test.each`'s `%$` placeholder (injects the test-case index), configurable retries via `jest.retryTimes(n, {waitBeforeRetry, retryImmediately})`, `jest.unstable_unmockModule()`, `jest.onGenerateMock(callback)`, custom object serialization via a `SERIALIZABLE_PROPERTIES` static, and async `setupFilesAfterEnv` support (top-level `await` / async default exports).

[VERSION-SENSITIVE, Source: https://jestjs.io/blog/2021/05/25/jest-27] For historical context, the prior major-defaults shift was **v27** (2021): `testEnvironment` default `jsdom` → `node`; fake timers default `legacy` → `modern`; default test runner `jest-jasmine2` → `jest-circus`. Examples/tutorials predating v27 may assume jsdom-by-default and should not be trusted for current defaults.

---

## 14. Limitations

[Source: https://jestjs.io/docs/ecmascript-modules] Native ECMAScript Modules (ESM) support is explicitly labeled **experimental**: it depends on Node's own `--experimental-vm-modules` flag (itself an experimental Node API as of the Node version referenced in the docs, v18.8.0), requires disabling/adjusting the default transform (`transform: {}`), and carries documented caveats — static imports are evaluated before `jest.mock()` hoisting can run (requiring `jest.unstable_mockModule()` + dynamic `import()` instead of the normal `jest.mock()` flow for ESM), and WebAssembly `*.wasm` imports have their own caveat around `--experimental-wasm-modules`. [Source: https://jestjs.io/docs/ecmascript-modules] Automocking and `__mocks__`-directory mocks for ESM only apply starting at **Node v24.9+**. [VERSION-SENSITIVE]

[Source: https://jestjs.io/docs/code-transformation] `node_modules` is **not transpiled by default** (governed by `transformIgnorePatterns`), which is a common source of "SyntaxError: Cannot use import statement outside a module" failures when a dependency ships untranspiled ESM — the documented fix is adjusting `transformIgnorePatterns` to allow specific packages through.

[Source: https://jestjs.io/docs/cli] `--detectOpenHandles` is explicitly documented as carrying a "performance penalty," implying it is not suitable to run on every CI invocation, only for diagnosis.

[Source: https://jestjs.io/docs/configuration] `bail` is documented as effective only at the root/global config level — per a linked GitHub PR discussion, it is ignored when set inside individual `projects` sub-configs. [Unresolved: this specific `projects`-scoping limitation for `bail` was found via a GitHub PR reference in search results rather than being independently re-confirmed against the current live `configuration` doc page text — flagging for re-verification.]

Not documented / could not verify: any hard limits on test-suite size, maximum worker count, or maximum snapshot file size beyond the general "keep snapshots small" style recommendation.

---

## 15. Debugging

[Source: https://jestjs.io/docs/troubleshooting] Official debugging guidance centers on Node's built-in inspector: insert a `debugger;` statement in a test, then run `node --inspect-brk node_modules/.bin/jest --runInBand [args]` (Windows: `node --inspect-brk ./node_modules/jest/bin/jest.js --runInBand`). `--runInBand` is required so Jest runs in a single process rather than spawning workers, making the single inspector session meaningful.

[Source: https://jestjs.io/docs/troubleshooting] **Chrome DevTools workflow**: run the above command, open `chrome://inspect` in Chrome, click "Open Dedicated DevTools for Node," click the shown `localhost:9229` address, then continue execution past Jest's own initial breakpoint until the test's `debugger;` statement is hit.

[Source: https://jestjs.io/docs/troubleshooting] **VS Code**: either an "attach" launch config (attaching to a manually-started `--inspect-brk` process on port 9229) or an "auto-launch" config that runs Jest directly via `runtimeArgs: ["--inspect-brk", "${workspaceRoot}/node_modules/.bin/jest", "--runInBand"]`; a Windows-specific path variant and a Create-React-App-specific variant (invoking `react-scripts test --runInBand --no-cache --env=jsdom --watchAll=false`) are both given as concrete examples.

[Source: https://jestjs.io/docs/troubleshooting] WebStorm is noted as having built-in Jest support (IDE-native debugging), without further elaboration on `jestjs.io` itself.

[Source: https://jestjs.io/docs/cli] `--verbose` (individual test result hierarchy in output), `--noStackTrace` (suppress stack traces), `--showConfig` (print resolved config and exit), and `--debug` (print Jest config debugging info) are additional CLI-level debugging/diagnostic aids beyond the interactive-debugger workflow.

---

## 16. Integration

[Source: https://jestjs.io/docs/testing-frameworks] Jest is framed as a "universal testing platform," with community-maintained integration guides (not first-party Jest docs, but linked from `jestjs.io`) for: **React** (via React Testing Library, referencing guides by Kent C. Dodds), **Vue.js** (Vue's official testing tooling), **Angular**/**AngularJS** (Jest as an alternative to Karma), **Express** (paired with Supertest for API testing), **Next.js** (linking to Next.js's own official Jest setup docs), **NestJS** (documented in NestJS's own fundamentals docs), **Hapi.js**, **Gatsby**, and state-management libraries **Redux** and **MobX**. [Inference, not confirmed in docs: the exact current URL for this page was not independently re-verified beyond the summarized fetch, since a direct re-fetch of `jestjs.io/docs/ecosystem` returned 404 — the community-integration content actually lives under `jestjs.io/docs/testing-frameworks`, not a separate "ecosystem" page.]

[Source: https://jestjs.io/docs/webpack] Jest documents explicit config-level mapping from webpack concepts to Jest equivalents for teams migrating a webpack-bundled app to Jest-based testing: `webpack.resolve.extensions` → `moduleFileExtensions`, `webpack.resolve.modules` → `moduleDirectories`, `webpack.resolve.roots` → `modulePaths`, `webpack.resolve.alias` → `moduleNameMapper`; static assets (images, fonts, media) and CSS/LESS are stubbed via `moduleNameMapper` pointing at manual mock files (e.g. `fileMock.js` returning a string stub, `styleMock.js` returning `{}`), with `identity-obj-proxy` recommended specifically for CSS Modules class-name fidelity.

[Source: https://jestjs.io/docs/code-transformation] Babel integration is first-party and default (`babel-jest`, with `babel-preset-jest` injecting Jest's mock-hoisting Babel plugin automatically unless `excludeJestPreset: true` is set); TypeScript integration is either via Babel's TS preset (type-stripping only, no type-checking) or the separately-maintained community package `ts-jest` (which does perform type-checking during transform).

[Source: https://jestjs.io/docs/migration-guide] Integration with other assertion/mocking libraries during migration: Chai (assertions), Sinon (spies/mocks), proxyquire — all listed as tools `jest-codemods` can help migrate away from, implying Jest is not designed to be a drop-in *addition* alongside these but rather a full replacement, though Chai is explicitly noted as usable alongside Jest if a team chooses not to migrate assertions.

---

## 17. Production Considerations

Largely not applicable in the traditional sense: [Inference, not confirmed in docs] Jest is exclusively a development/CI-time tool — it does not ship as part of, or run inside, a deployed production application, so "production considerations" for Jest itself mean considerations for **using Jest reliably in CI/build pipelines**, not for a production runtime.

[Source: https://jestjs.io/docs/cli] `--ci` mode is the primary production/CI-facing behavioral switch: it changes snapshot behavior so that new or mismatched snapshots **fail** the run rather than being silently written, preventing accidental snapshot drift from being committed by an automated pipeline.

[Source: https://jestjs.io/docs/cli] `--shard=<shardIndex>/<shardCount>` is documented for splitting a large test suite across multiple CI machines/jobs to parallelize wall-clock time in pipelines.

[Source: https://jestjs.io/docs/configuration] `testFailureExitCode` (default `1`) governs the process exit code on failure, relevant for CI systems gating merges/deploys on Jest's exit status. `bail` (stop after N failing suites) is a documented lever for fast-fail CI behavior.

[Source: https://jestjs.io/docs/cli] `--forceExit` is documented as a way to force the process to exit after tests complete even if handles remain open — implicitly a workaround rather than a fix, since it can mask genuine resource leaks; the companion `--detectOpenHandles` flag exists to diagnose those leaks instead of papering over them.

[Source: https://jestjs.io/docs/security/policy (github)] From a supply-chain/production-pipeline-security angle, the only Jest-specific guidance found is the vulnerability-disclosure policy covered in the Security section above; no dedicated "hardening your CI's Jest invocation" guidance was found on `jestjs.io`.

---

## Sources consulted (official only)

- https://jestjs.io/docs/getting-started
- https://jestjs.io/docs/architecture
- https://jestjs.io/docs/configuration
- https://jestjs.io/docs/cli
- https://jestjs.io/docs/expect
- https://jestjs.io/docs/mock-functions
- https://jestjs.io/docs/timer-mocks
- https://jestjs.io/docs/snapshot-testing
- https://jestjs.io/docs/code-transformation
- https://jestjs.io/docs/setup-teardown
- https://jestjs.io/docs/tutorial-async (Testing Asynchronous Code)
- https://jestjs.io/docs/troubleshooting
- https://jestjs.io/docs/ecmascript-modules
- https://jestjs.io/docs/migration-guide
- https://jestjs.io/docs/upgrading-to-jest30
- https://jestjs.io/docs/testing-frameworks
- https://jestjs.io/docs/webpack
- https://jestjs.io/versions
- https://jestjs.io/blog/2025/06/04/jest-30
- https://jestjs.io/blog/2021/05/25/jest-27
- https://github.com/jestjs/jest (packages directory / CHANGELOG.md)
- https://github.com/jestjs/jest/security/policy
- https://registry.npmjs.org/jest (npm registry metadata: version, engines, publish date)

Pages that returned 404 / could not be fetched at their expected URL (noted so future runs don't re-waste effort): `jestjs.io/docs/ecosystem`, `jestjs.io/docs/environment`, `jestjs.io/docs/asynchronous`, `jestjs.io/docs/continuous-integration`.
