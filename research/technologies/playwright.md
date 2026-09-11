# Playwright — Technology Research

Research date: 2026-09-09. Primary source: `playwright.dev` (the canonical official Playwright documentation host for the Node.js/TypeScript library and Playwright Test runner — confirmed current). Secondary official sources used where the main docs site did not cover a topic: `github.com/microsoft/playwright` (source repo / releases), `playwright.dev/mcp/*` (official docs for the Playwright MCP server, also maintained by the Playwright/Microsoft team). Citation convention: `[Source: <url>] <claim>.` for documented facts, `[Inference, not confirmed in docs]` for reasoning not explicitly stated, and "Not documented / could not verify" where no official source was found. `Unresolved:` flags items with conflicting or uncertain information.

**Scope note**: Playwright ships official bindings for Node.js/TypeScript, Python, Java, and .NET, each with its own docs subsite (`playwright.dev/python`, `/java`, `/dotnet`). This research focuses primarily on the canonical Node.js/TypeScript docs at `playwright.dev/docs/*`, since that is the primary/reference implementation, and notes cross-language points where relevant.

---

## 1. Core concepts

[Source: https://playwright.dev/docs/intro] Playwright Test is described as "an end-to-end test framework for modern web apps," combining test runner, assertion library, and reporting tooling into a single package (`@playwright/test`).

[Source: https://playwright.dev/docs/intro] Playwright supports cross-browser, cross-platform, cross-language automation: it drives Chromium, WebKit, and Firefox, on Windows, Linux, and macOS, either headless or headed, and officially supports test authoring in TypeScript, JavaScript, Python, .NET, and Java.

[Source: https://playwright.dev/docs/intro] Core capabilities highlighted on the intro page include: auto-wait/retry-ability of actions, native mobile emulation of Chrome for Android and Mobile Safari, "Trace Viewer" for post-run debugging, and a full test isolation model per test.

[Source: https://playwright.dev/docs/locators] **Locators** are the central object model for interacting with the page: "a way to find element(s) on the page at any moment" — a locator captures how to find an element and re-resolves it against the live DOM on every use, rather than capturing a single DOM handle at creation time. This underlies auto-waiting and retry-ability.

[Source: https://playwright.dev/docs/locators] Locators operate in **strict mode** by default: an operation implying a single target element throws an exception if the locator resolves to more than one DOM element. Multi-element operations (e.g. `.count()`) are exempt from strict mode.

[Source: https://playwright.dev/docs/actionability] Before performing an action (click, fill, etc.), Playwright runs **actionability checks** on the target element: Visible, Stable (same bounding box across two consecutive animation frames), Enabled, and Receives Events (is the actual hit-target, not obscured). Different actions require different subsets of these checks — e.g. `locator.click()` requires all four; `locator.fill()` requires Visible, Enabled, and Editable but not Stable; `dispatchEvent()` bypasses all checks.

[Source: https://playwright.dev/docs/library] The Library (non-Test) API exposes a three-tier object hierarchy: **Browser** (a launched browser process) → **BrowserContext** (an isolated, incognito-like environment within a browser) → **Page** (a single tab/document). Each level is created and torn down explicitly by the caller in Library usage (`chromium.launch()` → `browser.newContext()` → `context.newPage()`), whereas the Test runner provisions and tears these down automatically via fixtures.

[Source: https://playwright.dev/docs/api-testing] Playwright also exposes an **APIRequestContext** for pure HTTP API testing independent of any browser page, usable via the built-in `request` fixture (which respects `baseURL`/`extraHTTPHeaders` config) or a standalone `apiRequest.newContext()`.

## 2. Architecture

[Source: https://playwright.dev/docs/puppeteer] Playwright is explicitly cross-browser by design — the official Puppeteer migration guide states Playwright supports Chromium, Firefox, and WebKit, versus Puppeteer's Chromium-only scope, as a primary architectural differentiator.

[Source: https://playwright.dev/docs/browsers] Playwright does not simply automate whatever browser happens to be installed on the host; it ships and manages patched/pinned browser builds: Chromium builds are "pre-release Chromium builds," ahead of the current Chromium Stable; Firefox builds are patched versions close to Firefox Stable; WebKit builds are built from the latest WebKit main branch, ahead of the version Safari ships. Browser binaries download to an OS-specific cache directory (e.g. `~/.cache/ms-playwright` on Linux), configurable via `PLAYWRIGHT_BROWSERS_PATH`, with automatic garbage collection of unused versions.

[Source: https://playwright.dev/docs/browsers] Beyond the bundled open-source engines, Playwright can also drive branded release channels — `chrome`, `chrome-beta`, `chrome-canary`, `chrome-dev` and `msedge`, `msedge-beta`, `msedge-canary`, `msedge-dev` — using the machine's installed browser rather than a Playwright-managed binary.

[Source: https://playwright.dev/docs/library] Library architecture requires explicit resource lifecycle management (manual `browser.close()`/`context.close()`), while `@playwright/test` provides this automatically via its fixture system, making the Test package the officially recommended approach for end-to-end testing.

[Source: https://playwright.dev/docs/test-fixtures] The Test runner's architecture is built around a **fixture** dependency-injection system: built-in fixtures (`page`, `context`, `browser`, `browserName`, `request`) are provided out of the box; custom fixtures are declared via `test.extend()`, wrapping setup/teardown around an `await use()` call; fixtures can be test-scoped (default, per test) or worker-scoped (`{ scope: 'worker' }`, shared across tests in one worker process), and can be marked `{ auto: true }` to run for every test without explicit reference.

[Source: https://playwright.dev/docs/test-parallel] Test-runner execution architecture: the runner spawns independent OS worker processes, each holding its own browser instance/environment; by default test *files* run in parallel across workers while tests *within* a file run sequentially, unless `fullyParallel` or `test.describe.configure({ mode: 'parallel' })` is used; workers are reused across files for speed but recycled after a failure to guarantee a clean environment for subsequent tests.

[Source: https://playwright.dev/docs/frames] Frame/iframe architecture: a Page can contain multiple Frame objects (main frame plus nested iframes); frame-scoped interaction is done either via `page.frameLocator()` (recommended, returns a FrameLocator that can be queried like a Locator) or by obtaining a `Frame` object directly via `page.frame()` and calling standard page-like methods on it.

[Source: https://playwright.dev/docs/locators] Locators pierce **open** Shadow DOM by default for CSS/text/role-based locating; [Inference, not confirmed in a single fetched excerpt but consistent with docs cross-reference] locating by XPath does not pierce shadow roots, and closed-mode shadow roots are not supported by any locator strategy — this is documented on the official Locators page.

## 3. APIs

[Source: https://playwright.dev/docs/library] The **Library API** (used outside the Test runner) is organized around `chromium`/`firefox`/`webkit` launchers → `Browser` → `BrowserContext` → `Page`, called as plain async Node.js/Python/Java/.NET code (`node script.js`), with no built-in assertion or retry-aware expect layer — only standard language assertions.

[Source: https://playwright.dev/docs/api-testing] The **APIRequestContext** API (`request` fixture in Test, or `apiRequest.newContext()` standalone) issues raw HTTP requests, supports context-linked requests (sharing cookies with a BrowserContext) or fully isolated requests, and can produce/consume `storageState()` to bridge API-obtained auth into a browser context.

[Source: https://playwright.dev/docs/locators] The **Locators API** surface prioritizes user-facing, accessibility-oriented queries: `getByRole()`, `getByText()`, `getByLabel()`, `getByPlaceholder()`, `getByAltText()`, `getByTitle()`, and `getByTestId()`; these can be chained/filtered (`.filter()`, `.and()`, `.or()`, `.visible()` as of a recent release) to narrow matches, and `.first()`/`.last()`/`.nth()` opt out of strict mode (discouraged as pages evolve).

[Source: https://playwright.dev/docs/network] The **Network API** centers on `page.route()`/`context.route()` for interception, with `route.fulfill()` to serve mocked responses, `route.continue()` to forward (optionally modified) requests, `route.abort()` to block requests, plus `page.on('request'/'response')` events, `page.waitForResponse()`, HAR-file-based mocking/replay, and native WebSocket inspection/mocking.

[Source: https://playwright.dev/docs/test-reporters] The **Reporter API** ships built-in reporters — `list`, `line`, `dot` (default on CI), `html`, `blob` (for merging sharded reports), `json`, `junit`, `github` (Actions annotations), and a `perfetto` trace-event-format reporter — plus a documented custom-Reporter interface for third-party/bespoke reporting; officially-listed third-party reporters include Allure, ReportPortal, and Monocart.

[Source: https://playwright.dev/mcp/introduction] **Playwright MCP** exposes browser automation as a Model Context Protocol server for LLM agents, distinct from the Test/Library APIs: it operates on accessibility-tree snapshots rather than screenshots or DOM dumps ("structured text output that LLMs parse naturally, far cheaper than DOM dumps or screenshots"), assigns each element a stable reference id for deterministic interaction, and groups 70+ tools into capability sets (core navigation/click/type/tabs/dialogs/file-upload, network mocking/offline simulation, storage manipulation, testing/assertion utilities, dev tools like tracing and code execution, and an optional coordinate-based "vision mode").

## 4. Configuration

[Source: https://playwright.dev/docs/test-configuration] Test-runner configuration lives in `playwright.config.ts`/`.js`. Documented top-level options include: `testDir` (test file root), `testMatch`/`testIgnore` (glob/regex filters), `fullyParallel` (parallelize across all files, not just within), `workers` (concurrency, accepts a number or a percentage string like `'50%'`), `timeout` (per-test default 30s, covering the test function plus fixtures and `beforeEach`), `retries` (auto-retry count, typically set for CI), `forbidOnly` (fail the run if `test.only` is left in committed code), `projects` (multiple named configurations, e.g. one per browser), `reporter`, `outputDir` (screenshots/videos/traces location), `globalSetup`/`globalTeardown`, and `webServer` (auto-launch a dev server for the test run, with `command`, `url`, `reuseExistingServer`).

[Source: https://playwright.dev/docs/test-configuration] Assertion-related configuration: `expect.timeout` (default 5s wait for web-first assertion conditions), plus `toHaveScreenshot`/`toMatchSnapshot` visual-comparison tolerance settings (pixel diff count/ratio).

[Source: https://playwright.dev/docs/api/class-testconfig] Additional `TestConfig` properties: `globalTimeout` (hard cap on total suite run time — useful in CI to bound broken setups), `retryStrategy` (`'isolated'` mode runs retries after other tests complete, reducing interference), `shard` (`{ total, current }` for splitting a run across machines), and `maxFailures` (abort the run after N failures to save CI time).

[Source: https://playwright.dev/docs/test-typescript] TypeScript config is auto-discovered: Playwright walks up the directory tree for the nearest `tsconfig.json`/`jsconfig.json` (overridable via CLI or `playwright.config.ts`), but only honors a restricted set of compiler options — `allowJs`, `baseUrl`, `paths`, `references`, and `extends`. Playwright transforms TypeScript to JS at run time but does **not** type-check; running `tsc` separately is the documented recommendation for type safety.

[Source: https://playwright.dev/docs/emulation] Per-project or per-test `use` options cover browser/environment emulation: device presets (viewport, user agent, touch, `isMobile`), `geolocation` + `permissions` (e.g. notifications), `locale`/`timezoneId`, `colorScheme`, custom `userAgent`, `offline` mode, and disabling JavaScript. Note: locale/timezone emulation affects in-browser behavior only, not the Node.js test-runner process's own locale/clock.

[Source: https://playwright.dev/docs/videos] Video-capture configuration (`video` option) supports `'off'`, `'on'`, `'retain-on-failure'` (keep only failures), and `'on-first-retry'`; videos default to a downscaled 800×800 max, and are only finalized/saved once the owning BrowserContext is closed.

[Source: https://playwright.dev/docs/browsers] `PLAYWRIGHT_BROWSERS_PATH` environment variable relocates the browser-binary cache; a "hermetic install" pattern (binaries stored inside `node_modules`) is also documented as an alternative to the shared user-level cache.

## 5. Recommended patterns

[Source: https://playwright.dev/docs/best-practices] Use locators resilient to DOM changes, prioritizing user-facing attributes (role, text, label) over CSS classes or XPath tied to DOM structure; use codegen or the VS Code extension to generate correct locators.

[Source: https://playwright.dev/docs/best-practices] Use **web-first assertions** (e.g. `expect(locator).toBeVisible()`) that auto-wait and retry, rather than manual, non-awaited checks like an unretried `isVisible()` call; use soft assertions to collect multiple failures without stopping a test early.

[Source: https://playwright.dev/docs/best-practices] Test user-visible behavior, not implementation details; keep every test fully isolated (independent data/storage/cookies); use hooks to reduce repetition without breaking isolation; reuse signed-in state via a setup project rather than logging in per test.

[Source: https://playwright.dev/docs/best-practices] Mock third-party dependencies via the Network API instead of hitting real third-party servers; don't test external links/servers you don't control; test across all three engines (Chromium, Firefox, WebKit); keep Playwright itself up to date; run the suite on every commit/PR in CI; use parallelism and sharding to keep CI fast; when installing browsers in CI, install only the ones actually needed rather than all of them.

[Source: https://playwright.dev/docs/pom] Use the **Page Object Model** pattern at scale: a helper class per app section/page wraps its locators as properties and exposes higher-level action methods, centralizing selector maintenance and giving tests a higher-level, more maintainable API.

[Source: https://playwright.dev/docs/auth] For authentication, prefer a one-time setup project that authenticates and persists `storageState` to `playwright/.auth/*.json` (gitignored), reused across the suite. For tests that mutate server-side state, use per-worker unique accounts (a worker-scoped fixture keyed on `testInfo.parallelIndex`); for multi-role scenarios, maintain separate storage-state files per role and select via `test.use({ storageState: ... })` or separate `BrowserContext`s. Prefer API-based login over UI login when it's faster.

[Source: https://playwright.dev/docs/network] Prefer HAR-based or `route.fulfill()`-based network mocking over hitting live third-party/backend systems for deterministic, fast tests.

[Source: https://playwright.dev/docs/test-parallel] Design tests so parallel workers never depend on shared execution order or shared mutable state; derive any unique identifiers from test metadata (e.g. worker index) rather than hardcoding shared resources.

## 6. Anti-patterns

[Source: https://playwright.dev/docs/best-practices] Avoid CSS-class or XPath selectors that depend on DOM structure, and avoid asserting on implementation details (function names, internal array shapes, etc.) instead of user-visible behavior.

[Source: https://playwright.dev/docs/best-practices] Don't use manual, non-awaited assertions (e.g. calling `isVisible()` and checking the boolean immediately) — this skips Playwright's built-in retry logic and produces flaky tests.

[Source: https://playwright.dev/docs/best-practices] Don't test third-party servers/external links you don't control; don't install every browser in CI when only a subset is needed (wastes CI time).

[Source: https://playwright.dev/docs/ci] Caching browser binaries between CI runs is explicitly discouraged: "Caching browser binaries is not recommended, since the amount of time it takes to restore the cache is comparable to the time it takes to download the binaries," and OS-level dependencies on Linux cannot be cached at all.

[Source: https://playwright.dev/docs/test-components] For component testing, accessing a component's internal methods/instance from test code is "neither recommended nor supported" — tests should observe components only from a user-facing perspective.

[Source: https://playwright.dev/docs/frames] Treating an iframe's contents as directly queryable from `page`-level locators is a documented anti-pattern/misunderstanding: an iframe is a separate document, and page-level actions operate on the main frame only — content must be scoped via `page.frameLocator()` or `locator.contentFrame()`.

## 7. Security

[Source: https://playwright.dev/docs/docker] For running Playwright-driven code against **untrusted** content (e.g. web scraping/crawling of arbitrary sites), official Docker guidance recommends a dedicated non-root user plus a seccomp security profile to keep Chromium's OS-level sandbox active; running as root disables the Chromium sandbox. For **trusted** code (your own e2e test suite), root without the extra hardening is presented as acceptable.

[Source: https://playwright.dev/docs/docker] The `--no-sandbox` Chromium flag "disables browser sandboxing for process types that normally use it and should not be added by default."

[Source: https://playwright.dev/docs/auth] `storageState` files can contain live session cookies/headers: "The browser state file may contain sensitive cookies and headers that could be used to impersonate you or your test account" — the docs direct users to keep these out of version control (`playwright/.auth` should be gitignored).

[Source: https://playwright.dev/mcp/introduction] Playwright MCP ships a tool literally named `browser_run_code_unsafe`, signaling that arbitrary code execution capability requires caution; beyond the naming convention itself, the fetched introduction page provided no further explicit security-warning prose. Unresolved: whether a fuller security-guidance section exists elsewhere in the Playwright MCP docs (e.g. under `playwright.dev/mcp/configuration/*`) was not directly fetched/confirmed in this research pass.

[Inference, not confirmed in docs] Do not rely on `--allowed-origins`/`--blocked-origins`-style allow/deny-list configuration as a hard security boundary, since such lists can typically be bypassed via DNS rebinding or HTTP redirects; this general web-security caveat was surfaced via secondary (non-playwright.dev) sources during research and is flagged here as unconfirmed against an official playwright.dev/mcp page in this pass — treat as **Unresolved** pending direct citation.

## 8. Performance

[Source: https://playwright.dev/docs/test-parallel] The Test runner's primary performance lever is worker-based parallelism: multiple OS processes each running an isolated browser instance, configurable via `workers` (count or percentage), with `fullyParallel` enabling parallel execution of tests within a file (not just across files).

[Source: https://playwright.dev/docs/ci] In CI, official guidance is to set `workers: 1` for stability/reproducibility on constrained runners, then scale out via **sharding** (`--shard=X/Y`) across multiple CI jobs/machines rather than raising in-job concurrency.

[Source: https://playwright.dev/docs/api/class-testconfig] `retryStrategy: 'isolated'` runs retries after all other tests complete, reducing cross-test interference/contention during retries; `maxFailures` bounds wasted CI time by stopping after N failures.

[Source: https://playwright.dev/docs/videos] Video recording is off by default and adds overhead only when enabled; default recorded video dimensions are downscaled to a maximum of 800×800 to control file size. No numeric performance-overhead figures are given for tracing/video/screenshot capture in the fetched pages.

[Source: https://playwright.dev/docs/actionability] Auto-waiting/actionability checks (visible/stable/enabled/receives-events) are performed before actions with a configurable timeout, trading a small per-action wait budget for reduced flakiness versus fixed `sleep()`-style waits; exceeding the timeout raises `TimeoutError`.

[Source: https://playwright.dev/docs/docker] Recommended container flags for Chromium stability include `--init` (avoid zombie processes) and `--ipc=host` (Chromium shared-memory stability) — these affect reliability more than raw speed but are documented under the same operational-tuning guidance.

## 9. Testing

[Source: https://playwright.dev/docs/intro] `@playwright/test` is itself the testing framework in question — it bundles the test runner, an expect-based assertion library with auto-retrying "web-first assertions," and reporting.

[Source: https://playwright.dev/docs/test-fixtures] Test composition is fixture-based (see Architecture) rather than purely hook-based, enabling "composability, reusability, and on-demand setup."

[Source: https://playwright.dev/docs/api-testing] API testing (server-only, no browser) is a first-class, separate mode via `APIRequestContext`, usable for pure API test suites, precondition setup, or post-UI-action server-side verification.

[Source: https://playwright.dev/docs/test-components] **Component testing** (mounting and testing individual UI components in a real browser while the test itself runs in Node) is officially supported and, as of the current docs, is no longer experimental: it uses the stable `@playwright/test` package with a `fixtures.mount()` fixture and a "stories/galleries" model. [Version-sensitive] The older experimental packages `@playwright/experimental-ct-react`, `@playwright/experimental-ct-react17`, and `@playwright/experimental-ct-vue` have been discontinued/are no longer updated as of v1.63 in favor of this stable model. Officially supported frameworks are React and Vue, but the docs state the approach is framework-agnostic ("if your dev server can render it, Playwright can test it") given an implemented gallery contract. Accessing a component's internal instance/methods from test code is unsupported.

[Source: https://playwright.dev/docs/test-snapshots] Visual regression testing is built in via `expect(page).toHaveScreenshot()` (and `toMatchSnapshot()` for text/binary data), auto-generating baseline images on first run and diffing on subsequent runs using the `pixelmatch` algorithm with a configurable `maxDiffPixels` tolerance; snapshot filenames embed browser/platform identifiers to accommodate cross-platform rendering differences, and `stylePath` can inject CSS to hide non-deterministic elements before capture.

[Source: https://playwright.dev/docs/test-reporters] Built-in reporters cover local development (`list` default), CI-compact (`dot`, default on CI), machine-readable (`json`, `junit`), self-contained visual (`html`), sharded-report-merging (`blob`), and performance-profiling (`perfetto`) use cases.

[Source: https://playwright.dev/docs/test-typescript] Type checking is not performed by the test runner itself; a separate `tsc` invocation is the documented way to catch type errors alongside running tests.

## 10. Deployment

[Source: https://playwright.dev/docs/docker] Official Docker images are published per-Ubuntu-base — Ubuntu 22.04 ("Jammy"), 24.04 ("Noble", the default/untagged base), and 26.04 ("Resolute") — tagged as `mcr.microsoft.com/playwright:v<version>[-<codename>]`, e.g. `v1.63.0-noble`. Alpine Linux is explicitly unsupported: "musl library incompatibility with browser builds." Guidance is to always pin the image tag to a specific Playwright version so bundled browser binaries match the test/automation code's Playwright version.

[Source: https://playwright.dev/docs/docker] Playwright also supports running a remote **Playwright Server** inside Docker (listening on a port, e.g. 3000) that client processes connect to over the network for distributed/remote browser execution, rather than launching browsers locally in every environment.

[Source: https://playwright.dev/docs/ci] Official CI guidance frames a standard 3-step pipeline: (1) provision environment — either the official Docker image or `npx playwright install --with-deps` for system deps; (2) `npm ci`; (3) `npx playwright test`. Documented example integrations include GitHub Actions, Azure Pipelines, CircleCI, GitLab CI, and Jenkins, typically uploading the HTML report as a CI artifact and optionally sharding across parallel jobs.

[Source: https://playwright.dev/docs/ci] Documented CI-relevant environment variables include `CI=true` (flags CI environment, affecting some Playwright defaults), `PLAYWRIGHT_TEST_BASE_URL` (overrides base URL for tests), and `DEBUG=pw:browser` (verbose browser-launch logging for troubleshooting CI failures).

## 11. Migration

[Source: https://playwright.dev/docs/puppeteer] Official **Puppeteer → Playwright** migration guide: highlights cross-browser support (vs. Puppeteer's Chromium-only scope) as the core motivation; documents concrete API renames/changes such as `setViewport` → `setViewportSize`, `networkidle2` collapsing into a general `networkidle` wait state (noted as "not useful, thanks to auto-waiting"), `waitForXPath()` folding into the unified `waitForSelector()`-style approach, `createIncognitoBrowserContext()` → `newContext()`, and a general push from `ElementHandle`-based code toward Locator objects and web-first assertions. Cookie management moves from page-level to context-level.

[Source: https://playwright.dev/docs/protractor] Official **Protractor → Playwright** migration guide exists (`playwright.dev/docs/protractor`); a defining benefit cited is eliminating the need for `webdriver-manager`/Selenium WebDriver as an intermediary. (Not deeply fetched in this pass beyond confirming its existence and headline claim — Unresolved: full API-mapping detail from this page was not extracted.)

[Source: https://playwright.dev/docs/release-notes] Major/minor-version upgrade guidance is delivered inline in the release notes themselves rather than via a single consolidated "upgrade guide" page: e.g. after upgrading to a given version, users are told to rerun their suite, and if failing, to regenerate visual snapshots and adjust code depending on removed/changed APIs (PDF-viewer- and extension-related changes were called out for one such upgrade). There is no dedicated "Migrating between major Playwright versions" page distinct from the release notes, because Playwright has not shipped a 2.0 — it has stayed on a `1.x` line with incremental minor releases that occasionally remove long-deprecated APIs (treated by the project as its mechanism for breaking changes rather than a major-version bump). [Inference, not confirmed in docs: the absence of any `2.x` release and the fact breaking removals happen within `1.x` minors is drawn from the release-notes content actually fetched, not from an explicit "we do not use semver-breaking major versions" policy statement — Unresolved: no dedicated official versioning-policy page was found/fetched confirming this as deliberate policy.]

[Source: https://playwright.dev/docs/test-components] Migrating **off** the deprecated `@playwright/experimental-ct-react`/`-react17`/`-vue` packages onto the stable `@playwright/test` component-testing model (stories/galleries + `fixtures.mount()`) is a documented, version-sensitive migration as of v1.63.

## 12. Version information

[Source: https://playwright.dev/docs/release-notes] Current stable line as of this research date (2026-09-09) is **v1.63** (with prior minors v1.62, v1.61, v1.60, … back through v1.41 all listed on the release-notes page as the historical minor sequence within the `1.x` line).

[Source: https://github.com/microsoft/playwright/releases] The GitHub Releases page lists v1.63.0, v1.62.1, v1.62.0, v1.61.1, v1.61.0, v1.60.0 as the most recent tags. **Unresolved**: the exact publish dates could not be reliably confirmed — an automated fetch of this page returned dates in "2024," which contradicts other evidence (a separate web search of secondary/non-official sources placed v1.60 in May 2026, v1.61 in June 2026, and v1.62 in July 2026, consistent with the stated current date of September 2026 and a v1.63 current release). The month/day figures were consistent across both fetches but the year field is in conflict, most likely due to a tool/summarization artifact rather than an actual 2024 release — treat exact dates as unconfirmed pending a direct, verbatim read of the GitHub releases page or npm registry timestamps.

[Source: https://playwright.dev/docs/intro] Documented Node.js support: "latest 22.x, 24.x or 26.x." Documented OS support: Windows 11+/Windows Server 2019+/WSL, macOS 14 (Sonoma) or later, and Debian 12/13 or Ubuntu 22.04/24.04/26.04 (x86-64 or arm64).

[Source: https://playwright.dev/docs/browsers] Bundled/managed browser versions track ahead of their public-release counterparts (pre-release Chromium, patched near-Stable Firefox, latest WebKit main) and are updated with every Playwright release, rather than following an independent versioning scheme of their own.

[Inference, not confirmed in docs] Release cadence appears to be roughly every 4–6 weeks based on the minor-version dates gathered (this pattern was not confirmed via an explicit official cadence statement — Unresolved, see note above on date-source conflict). No official LTS/support-window policy page was found; Playwright does not appear to designate any release as long-term-supported — each new minor is the documented recommendation to move to ("keep Playwright itself up to date" per Best Practices). Not documented / could not verify: any formal deprecation/EOL timeline for older `1.x` minors.

## 13. Breaking changes

[Source: https://playwright.dev/docs/release-notes] **v1.63**: Ubuntu 20.04 is no longer supported. The experimental component-testing packages (`@playwright/experimental-ct-react`, `@playwright/experimental-ct-vue`) are deprecated/no longer updated in favor of the new stable component-testing model.

[Source: https://playwright.dev/docs/release-notes] **v1.62**: Debian 11 support end-of-support was announced. New component-testing model (stories/galleries + `fixtures.mount()`) introduced as the stable replacement path.

[Source: https://playwright.dev/docs/release-notes] **v1.60**: Several long-deprecated APIs were removed: `Locator.ariaRef()`, the `handle` option on `exposeBinding()`, the `logger` option on browser `connect()`/`connectOverCDP()` methods, and `context.videoPath()`/associated legacy video-size options.

[Source: https://playwright.dev/docs/release-notes] Earlier documented breaking change (version not precisely re-confirmed in this pass beyond the summarized fetch, believed **v1.52** per the fetched summary): macOS 13 WebKit support was deprecated ("macOS 13 is now deprecated and will no longer receive WebKit updates"), and `route.continue()` lost the ability to override the `Cookie` header. [Unresolved: the exact version tag for the macOS 13/Cookie-header changes should be re-verified directly against the dated release-notes entry rather than relied on solely from the summarized fetch used here.]

[Source: https://playwright.dev/docs/release-notes] After any version bump, official guidance is: rerun the suite; if it fails, expect to need to regenerate visual snapshots and adjust code around any removed/changed APIs called out in that version's notes (PDF-viewer and browser-extension-related behavior was cited as one example category of change).

## 14. Limitations

[Source: https://playwright.dev/docs/frames] An iframe is a separate document; page-level locators/actions do not automatically see inside it — content must be explicitly scoped via `page.frameLocator()` or `locator.contentFrame()`. Not documented in the fetched Frames page: explicit language about cross-origin iframe restrictions (the page did not address this in the content retrieved).

[Source: https://playwright.dev/docs/locators] Locating by XPath does not pierce Shadow DOM boundaries; closed-mode Shadow DOM roots are not accessible to any Playwright locator strategy (open shadow roots are pierced automatically by role/text/CSS locators).

[Source: https://playwright.dev/docs/browsers] Browser engines Playwright ships are patched/pinned builds, not identical to what end users run in production browsers (pre-release Chromium ahead of Stable, WebKit ahead of the Safari release it derives from) — this is a documented, deliberate trade-off (catching issues before public browser updates land) but also means Playwright's Chromium/WebKit are not byte-identical to the exact browser version a real end user has installed.

[Source: https://playwright.dev/docs/test-components] Component testing does not support introspecting a component's internal instance or calling its internal methods from test code — only user-facing DOM/behavior is testable. Story identifiers are plain strings, so renaming a story is a runtime failure, not a compile-time one.

[Source: https://playwright.dev/docs/test-snapshots] Visual/screenshot comparisons are sensitive to host OS, browser version, hardware, power source, headless-vs-headed mode, and other rendering-environment factors — reproducible visual baselines require matching the environment the baseline was generated in; this is a documented constraint, not a bug.

[Source: https://playwright.dev/docs/docker] Alpine Linux base images are unsupported due to musl libc incompatibility with the bundled browser builds.

## 15. Debugging

[Source: https://playwright.dev/docs/debug] Official debugging surfaces: the **VS Code extension** (inline error messages with expected/received values and a full call log, live locator highlighting, breakpoints, step-through); the **Playwright Inspector** (step through actions via a toolbar, live-edit locators mid-run, view actionability-check logs showing visible/enabled/stable status); the **Trace Viewer** (navigate forward/backward through recorded actions, see what happened visually at each step); browser **DevTools** access via `PWDEBUG=console` (exposes a `playwright` object in the console for selector queries) combined with `page.pause()`; verbose API logging via `DEBUG=pw:api`; and plain **headed mode** (`headless: false`) optionally combined with `slowMo` for visual observation.

[Source: https://playwright.dev/docs/trace-viewer-intro] The **Trace Viewer** replays a recorded trace with step-by-step navigation, inline console logs, network activity, before/after screenshots per action, and live DOM snapshots that can be opened in real browser DevTools for HTML/CSS inspection. Traces are conventionally configured to record automatically on CI retries and are accessed by clicking the trace icon in the HTML report.

[Source: https://playwright.dev/docs/ci] `DEBUG=pw:browser` environment variable specifically surfaces browser-launch failure diagnostics, useful for CI-only launch problems.

[Source: https://playwright.dev/docs/getting-started-vscode] The VS Code extension additionally offers CodeGen-based test recording/generation, per-project (per-browser) test selection, trace-viewer integration inside the editor, and can suggest AI-assisted fixes for failing tests.

## 16. Integration

[Source: https://playwright.dev/docs/ci] Documented CI integrations: GitHub Actions, Azure Pipelines, CircleCI, GitLab CI, Jenkins — via either the official Docker image or `npx playwright install --with-deps` plus `npx playwright test`.

[Source: https://playwright.dev/docs/docker] Docker integration via `mcr.microsoft.com/playwright` images (per-Ubuntu-codename tags) for both local containerized test runs and a network-addressable remote Playwright Server mode.

[Source: https://playwright.dev/docs/getting-started-vscode] Editor integration via the official Playwright VS Code extension (test running/debugging/CodeGen/trace-viewer inline).

[Source: https://playwright.dev/docs/test-typescript] Language-tooling integration: automatic `tsconfig.json`/`jsconfig.json` discovery (restricted option subset), enabling TS path-mapping in tests without extra build configuration.

[Source: https://playwright.dev/docs/test-reporters] Reporting-tool integration: built-in JSON/JUnit output for third-party CI/dashboard ingestion, plus a documented custom-Reporter API and named third-party reporters (Allure, ReportPortal, Monocart, mail reporter).

[Source: https://playwright.dev/mcp/introduction] **AI-agent integration** via the official Playwright MCP server (`@playwright/mcp`), installable as an MCP server (`npx @playwright/mcp@latest`) for MCP-compatible clients including VS Code, Cursor, Windsurf, and Claude Desktop; it exposes accessibility-snapshot-based browser control, network mocking/offline simulation, storage manipulation, and tracing/code-execution tools to LLM agents, and supports options such as `--shared-browser-context` to share one browser context across multiple connected clients. [Source: https://playwright.dev/docs/getting-started-mcp] A getting-started-with-MCP page also exists under the main docs tree (and per-language variants for Python/Java/.NET), indicating first-class, officially maintained documentation for this integration path — consistent with Playwright's stated ambition to serve both traditional test automation and AI-coding-agent tool use.

[Source: https://playwright.dev/docs/network] Third-party backend/API mocking integration via route interception and HAR-file replay, allowing tests to run independent of live third-party services.

## 17. Production considerations

[Source: https://playwright.dev/docs/docker] For production-adjacent, non-test use (e.g., scraping/automation services processing untrusted external content), official guidance calls for container hardening: dedicated non-root user + seccomp profile to preserve the Chromium sandbox, `--init` to reap zombie processes, and `--ipc=host` for Chromium shared-memory stability; pin the Docker image tag to an exact Playwright version so browser binaries match the automation code.

[Source: https://playwright.dev/docs/ci] For CI reliability at scale: pin `workers: 1` on CI runners for reproducibility, then scale throughput via sharding across machines rather than raising per-runner concurrency; avoid caching browser binaries (restore-time cost is comparable to fresh download time, and Linux OS deps aren't cacheable at all).

[Source: https://playwright.dev/docs/auth] For production test-suite operation involving authenticated flows: never commit `storageState` files (they can carry live, impersonation-capable session cookies/headers); rotate/regenerate them as credentials expire (the docs specifically note the setup project does not auto-run in UI mode, so periodic manual re-auth is needed there); use per-worker distinct accounts when tests mutate shared server state to avoid cross-test contamination in a production-like staging environment.

[Source: https://playwright.dev/docs/best-practices] Run the full cross-browser suite (Chromium, Firefox, WebKit) on every commit/PR against a staging environment with a controlled test database, rather than only spot-checking one engine.

[Source: https://playwright.dev/docs/test-snapshots] For production visual-regression pipelines, keep the screenshot-generating environment (OS, browser version, headless/headed mode, power source) consistent between baseline creation and comparison runs, since rendering can otherwise drift and produce false-positive diffs.

---

## Notes on documentation host

[Source: https://playwright.dev/docs/intro] `playwright.dev` is confirmed as the current, canonical documentation host for the Node.js/TypeScript Playwright library and Test runner as of this research date; per-language docs are hosted at predictable subpaths (`/python`, `/java`, `/dotnet`) rather than separate domains. The Playwright MCP server has its own first-class docs section at `playwright.dev/mcp/*`, also part of the same canonical host — no host migration was found or indicated.
