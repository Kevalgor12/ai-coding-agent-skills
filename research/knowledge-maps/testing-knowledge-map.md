# Testing Knowledge Map

Source data: pre-extracted `testingRelationships` fields for 44 researched technologies (`research/technologies/*.md`), covering only the parts of that research relevant to testing. This map organizes those facts by **test layer/approach** rather than by technology, cross-referencing which tools (Playwright, Jest, Vitest, and others) are documented — by whose official docs — for testing which technology. Every claim below carries its source citation verbatim from the underlying data. Inferences drawn by combining two or more separately-stated facts are labeled `[Synthesis: ...]`; inferences already present in the source data (typically flagged there as "not an explicit doc statement") are reproduced with that same caveat intact.

**A note on the "empty testingRelationships" instruction:** none of the 44 technology objects in this data file literally carries an empty `testingRelationships: []` array — each has at least one entry. However, a substantial number of those entries are themselves *gap notices*: the entry's own content is "no official testing guidance was found for X," often explicitly marked `[Inference from *.md, not an explicit doc statement]`. Functionally these technologies have the same evidentiary status an empty array would have (no first-party testing methodology on record), so they are surfaced explicitly in the **Notable Gaps** section below rather than being silently folded into the tables as if they were well-documented.

---

## 1. Unit Testing

| Technology | Documented unit-testing approach | Citation |
|---|---|---|
| Jest | Self-contained: built-in mocking (`jest.fn`/`jest.mock`/`jest.spyOn`), snapshot testing, fake timers — no separate mocking library required | `[Source: https://jestjs.io/docs/mock-functions, https://jestjs.io/docs/snapshot-testing, https://jestjs.io/docs/timer-mocks]` |
| Jest | `ts-jest` performs TypeScript type-checking during transformation (vs. Babel's type-stripping-only preset) | `[Source: https://jestjs.io/docs/code-transformation]` |
| Vitest | Jest-compatible mocking (`vi.fn`/`vi.mock`/`vi.spyOn`) and Jest-compatible snapshot testing — positioned as a near-drop-in Jest replacement | `[Source: https://vitest.dev/guide/features.html]` |
| Vitest | In-source (Rust-style) testing via `import.meta.vitest`, recommended for small unit-testable utility functions | `[Source: https://vitest.dev/guide/in-source.html]` |
| Vitest | Type testing via `expect-type` (`expectTypeOf`, `assertType`) catches TypeScript type regressions in the suite | `[Source: https://vitest.dev/guide/features.html]` |
| Go | `testing` package (`T`/`B`/`F`/`M` types; `TestXxx`/`BenchmarkXxx`/`ExampleXxx`/`FuzzXxx` signatures) discovered by `go test` | `[Source: https://pkg.go.dev/testing]` |
| Go | Table-driven tests with subtests via `t.Run` (`/`-separated names, selectable via `-run`) is the documented idiom | `[Source: https://go.dev/doc/effective_go]` |
| Python | `unittest` — standard-library xUnit-style framework: `TestCase`, `assert*` family, fixtures, `addCleanup()`/`enterContext()` (3.11+), `subTest()`, `python -m unittest discover` | `[Source: https://docs.python.org/3/library/unittest.html]` |
| Python | `IsolatedAsyncioTestCase` (3.8+) for testing `async def` test methods under `unittest` | `[Source: https://docs.python.org/3/library/unittest.html]` |
| Python | `doctest` executes `>>>`-prompted examples in docstrings, checking output — doubles as regression test and documentation | `[Source: https://docs.python.org/3/library/doctest.html]` |
| Python | pytest is explicitly **out of scope** for docs.python.org — official docs do not cover third-party runners (pytest, nose2, hypothesis) | `[Source: python.md Section 9, citing absence in docs.python.org]` |
| Prisma | Jest + ts-jest + `jest-mock-extended` (pinned `^2.0.4`), using `mockDeep()`/`mockReset()`/`DeepMockProxy` to deep-mock `PrismaClient` via singleton or DI patterns (scoped to Prisma ORM v7) | `[Source: https://www.prisma.io/docs/orm/prisma-client/testing/unit-testing]` |
| Drizzle ORM | `drizzle.mock()` creates a typed DB instance with no real connection — documented as "ideal for testing" | `[Source: https://orm.drizzle.team/docs/goodies]` |
| Drizzle ORM | `drizzle-seed` generates deterministic, reproducible fake data via a seedable PRNG, framed for "testing, development, and debugging" (with documented limits on composite constraints / non-unique generators) | `[Source: https://orm.drizzle.team/docs/seed-overview]` |
| Nuxt | Unit testing is **Vitest-only** for the Nuxt runtime environment (`defineVitestProject` in `vitest.config.ts`); `test/nuxt/` runs in the Nuxt runtime, `test/unit/` runs in plain Node for speed | `[Source: https://nuxt.com/docs/4.x/getting-started/testing]` |
| Vue | Vitest is the official unit-testing recommendation for isolated functions/composables/modules — "created and maintained by members of the Vue / Vite team" | `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |
| Angular | Vitest is now the **default** test runner for new Angular CLI projects (v21+), replacing Karma; runs in Node via jsdom or happy-dom | `[Source: https://angular.dev/guide/testing]` |
| ClickHouse | Unit tests are isolated library/class-level tests, built via the `ENABLE_TESTS` CMake option and run with `ninja test`, largely using **gtest** | `[Source: https://clickhouse.com/docs/resources/develop-contribute/contribute/tests]` |
| Vite | Vitest reuses `vite.config.*` so existing Vite plugins/config work out of the box, with Jest-API compatibility for migration | `[Source: https://vitest.dev/guide/]` |

**No official application-level unit-testing methodology found:** TypeORM (no dedicated official Testing guide — see Notable Gaps), TypeScript (does not ship or endorse a testing framework), Sass, Tailwind CSS, MySQL (own test suite is for the server, not applications), PostgreSQL (application-level testing is out of official-docs scope), Redis (no first-party test double / unit-testing integration guide).

---

## 2. Integration Testing

| Technology | Documented integration-testing approach | Citation |
|---|---|---|
| Docker | **Testcontainers** is documented as the pattern for integration tests against real dependency containers (databases, message brokers) rather than mocks — containers start before tests, tear down after regardless of outcome; **Testcontainers Cloud** runs them remotely to cut local/CI resource pressure | `[Source: https://docs.docker.com/testcontainers/] [Source: https://docs.docker.com/guides/testcontainers-cloud/]` |
| Docker | `docker compose` lifecycle commands (`up`, `down`, `logs`, `exec`) support exercising a full multi-service stack consistently across dev/staging/prod/CI — functioning as an integration-test harness | `[Source: https://docs.docker.com/compose/]` |
| Prisma | Integration testing is documented as a separate, complementary approach exercising real component interaction against an actual database with test data, contrasted directly against the unit-testing/mocking approach | `[Source: https://www.prisma.io/docs/orm/prisma-client/testing/integration-testing]` |
| Drizzle ORM | **PGlite** ("Postgres in WASM," ~2.6MB gzipped) is an officially documented Drizzle-connectable Postgres implementation, runnable in Node.js/Bun/browser without a Linux VM or Docker, usable in-memory (ephemeral) or persisted — its zero-external-dependency design is the documented mechanism making it test-suitable | `[Source: https://orm.drizzle.team/docs/connect-pglite]` |
| Mongoose | For replica-set-dependent features (change streams, transactions), docs recommend `mongodb-memory-server` or `run-rs` for local testing; MongoDB Atlas is recommended for production | `[Source: https://mongoosejs.com/docs/change-streams.html]` |
| MongoDB | Officially documents deploying a self-managed replica set specifically for testing/development, as a lighter-weight, non-production topology | `[Source: https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-for-testing/]` |
| MongoDB | Ships and documents the `mongodb/mongodb-atlas-local` Docker image for a local Atlas-compatible deployment for dev/testing, with a documented Docker Compose pattern (Docker Desktop v4.31+ / Engine v27.0+, 2GB RAM / 2 CPU, port 27017 free). Does **not** mention Testcontainers on this page. | `[Source: https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-deploy-docker/]` |
| ClickHouse | Integration tests are Docker-based and multi-container, testing clustered ClickHouse plus external systems like MySQL/PostgreSQL/MongoDB, including network-partition/packet-drop emulation | `[Source: https://clickhouse.com/docs/resources/develop-contribute/contribute/tests]` |
| OpenSearch | Maintains an official **opensearch-testcontainers** GitHub repository — a Testcontainers module to spin up real OpenSearch Docker containers in integration tests, for use with JUnit 4/5 in JVM-based suites | `[Source: https://github.com/opensearch-project/opensearch-testcontainers]` |
| Fastify | Alternative to in-process `inject()`: actually call `fastify.listen()` and drive it with a real HTTP client (undici, native fetch, or SuperTest named), or call `fastify.ready()` to fully initialize without binding a socket | `[Source: https://fastify.dev/docs/latest/Guides/Testing/]` |
| Socket.IO | Documented pattern: create a plain Node `http.Server`, attach a Socket.IO `Server`, listen on an ephemeral port, then create a `socket.io-client` connection to test against it, with lifecycle hooks for setup/teardown | `[Source: https://socket.io/docs/v4/testing/]` |
| OpenAPI | Best-practices guidance recommends wiring the OpenAPI Description (OAD) into automated CI to verify implementation code matches the spec and vice versa — using the spec as a contract-testing source of truth (see also Section 7) | `[Source: https://learn.openapis.org/best-practices.html]` |
| WebSocket API | MDN's closest official testing guidance is a worked client/server ping-pong echo example (source at github.com/mdn/dom-examples) — a manual integration-testing reference implementation, not a framework | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications]` |
| GitHub | Webhook testing workflow: `smee.io` as a public proxy URL plus the `smee-client` npm package forward deliveries to a local server, verified at three checkpoints (GitHub delivery confirmation, smee.io receipt, local-server processing); the UI also supports **redelivering** a past webhook for repeat/regression testing | `[Source: https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/testing-webhooks]` |

**Documented but explicitly acknowledged as a gap for application-level integration testing:** PostgreSQL ("No official PostgreSQL-maintained equivalent to 'testcontainers'... left to ecosystem tooling" — `[Source: postgresql.md Section 9, 'Not documented / could not verify' note]`); Redis (no first-party Testcontainers module or in-memory test double found — `[Source: https://redis.io/docs/latest/develop/programmability/]`); MySQL (own test suite scoped to the server codebase, not applications — `[Source: https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_MYSQL_TEST_RUN_PL.html]`).

---

## 3. End-to-End / Browser Testing

| Technology | Documented E2E approach | Named tools | Citation |
|---|---|---|---|
| Playwright | `@playwright/test` bundles the test runner, an expect-based auto-retrying web-first assertion library, and reporting in one package; test composition is **fixture-based** (test-scoped, worker-scoped, or auto-run) for "composability, reusability, and on-demand setup" | — | `[Source: https://playwright.dev/docs/intro]`, `[Source: https://playwright.dev/docs/test-fixtures]` |
| Playwright | API testing (server-only, no browser) is first-class via `APIRequestContext` — usable for pure API suites, precondition setup, or post-UI-action server-side verification | — | `[Source: https://playwright.dev/docs/api-testing]` |
| Nuxt | E2E testing supports **Vitest, Jest, Cucumber, and Playwright** as runners via a `setup()` helper wiring `beforeAll`/`beforeEach`/`afterEach`/`afterAll`; `createPage(url)` gives a configured Playwright browser page, with browser-mode support via `@vitest/browser-playwright` and a first-class `@nuxt/test-utils/playwright` integration | Vitest, Jest, Cucumber, Playwright | `[Source: https://nuxt.com/docs/4.x/getting-started/testing]` |
| Next.js | Officially documents first-party setup guides for **Jest and Vitest** (unit), **Cypress** (E2E/component), and **Playwright** (E2E); distinguishes five conceptual test types (Unit, Component, Integration, E2E, Snapshot) | Jest, Vitest, Cypress, Playwright | `[Source: https://nextjs.org/docs/app/guides/testing]` |
| Next.js | New `@next/playwright` package (v16.3) ships an `instant()` helper asserting exactly what UI is visible instantly during client navigation, guarding against regressions (e.g. a `cookies()` call landing in a shared header) | Playwright | `[Source: https://nextjs.org/blog/next-16-3]` |
| Next.js | Async Server Components are new to the React ecosystem and some testing tools don't fully support them; docs explicitly recommend **End-to-End Testing over Unit Testing** as a workaround for async components | — (recommends E2E generally) | `[Source: https://nextjs.org/docs/app/guides/testing]` |
| Vue | E2E testing is recommended via **Playwright** (cross-browser: Chromium, WebKit, Firefox; praised for debugging) or **Cypress** (graphical UI, component-testing crossover) | Playwright, Cypress | `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |
| Angular | Real-browser testing remains available via providers like **Playwright** or **WebdriverIO**, for browser-specific API coverage/debugging alongside the default Vitest setup | Playwright, WebdriverIO | `[Source: https://angular.dev/guide/testing]` |
| Vitest | Browser Mode runs tests directly inside a real browser via **Playwright** (recommended), **WebdriverIO**, or a lightweight Preview provider, with native `window`/`document` access and (v5.0) a Trace View for step-by-step replay | Playwright, WebdriverIO | `[Source: https://vitest.dev/guide/browser/]` |
| React | Docs recommend "continuous end-to-end testing" before/while adopting the React Compiler, treating a solid pre-existing test suite as a prerequisite for confident adoption | — | `[Source: https://react.dev/blog/2025/10/07/react-compiler-1]` |
| Three.js | The project's own e2e suite "can take quite a long time and installs ~200 MB Chromium browser," and is "primarily intended to be run only by GitHub Actions" — this is contributor-facing (library) e2e testing, not app-developer guidance | Chromium (via GitHub Actions) | `[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/.github/CONTRIBUTING.md]` |
| WebRTC | Official CI/headless testing: Chrome flags (`--use-fake-ui-for-media-stream`, `--use-file-for-fake-audio-capture`/`--use-file-for-fake-video-capture`, `--headless`, `--mute-audio`, `--allow-file-access-from-files`) run WebRTC code without real devices or permission prompts | Chrome | `[Source: https://webrtc.org/getting-started/testing]` |
| WebRTC | Firefox equivalent: `media.navigator.streams.fake: true` and `media.navigator.permission.disabled: true` prefs, plus cache/update-disabling prefs | Firefox | `[Source: https://webrtc.org/getting-started/testing]` |

`[Synthesis: combining Vitest's Browser Mode using Playwright/WebdriverIO as providers, Angular's use of the same two tools for real-browser testing, and Nuxt/Next.js/Vue all listing Playwright as their E2E recommendation — Playwright and, to a lesser extent, WebdriverIO function as the de facto shared browser-automation backends underneath several higher-level test runners across this dataset, not just as standalone E2E tools in their own right.]`

---

## 4. Component Testing

| Technology | Documented component-testing approach | Citation |
|---|---|---|
| Playwright | Mounts and tests individual UI components in a real browser while the test runs in Node; officially supported frameworks are **React and Vue** via the stable `fixtures.mount()` model (no longer experimental) | `[Source: https://playwright.dev/docs/test-components]` |
| Vitest | Component testing is supported for **Vue/React/Svelte/Lit/Marko** via Browser Mode | `[Source: https://vitest.dev/guide/features.html]` |
| React | `react-test-renderer` and `react-dom/test-utils` are **deprecated** — the former implements its own renderer environment that doesn't match real usage and promotes testing implementation details; official recommended replacement is `@testing-library/react` (or `@testing-library/react-native`) | `[Source: https://react.dev/warnings/react-test-renderer]` |
| React | `act` ensures updates from a test interaction are applied to the DOM before assertions run; as of React 19, moved from `react-dom/test-utils` into the `react` package itself, with a codemod (`npx codemod@latest react/19/replace-act-import`) | `[Source: https://react.dev/reference/react/act]` |
| Vue | Component testing (props, events, slots, styles, lifecycle, user interaction) recommended via **Vitest + `@vue/test-utils`** (official low-level mounting library, fast Node-based) or **Cypress Component Testing** (real-browser, catches style/layout issues); `@testing-library/vue` named as a community user-centric alternative | `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |
| Vue | Composables using lifecycle hooks or `provide`/`inject` need a `withSetup()` test helper invoking the composable inside a throwaway `createApp({setup(){...}}).mount(...)`, then explicitly `app.unmount()`s afterward | `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |
| Nuxt | Component/testing helpers: `mountSuspended`, `renderSuspended` (via Testing Library), `mockNuxtImport` (once per mocked import per test file), `mockComponent`, `registerEndpoint` (mock Nitro endpoint) | `[Source: https://nuxt.com/docs/4.x/getting-started/testing]` |
| Angular | Provides component test harnesses as a first-class testing utility, with documented guides for harness overview, usage, custom harness creation, and additional test-environment support | `[Source: https://angular.dev/guide/testing]` |
| Angular | Reactive forms are directly/synchronously testable without rendering the UI; template-driven forms require more familiarity with change-detection cycles due to async data flow via `NgModel` | `[Source: https://angular.dev/guide/forms]` |
| MUI (Material UI) | `@testing-library/react` is the explicitly recommended tool — praised for querying by role/semantics (e.g. `input`, `[role="textbox"]`) rather than MUI component/class names, making tests robust to internal MUI changes; official guidance is to test the application, not MUI internals | `[Source: https://mui.com/material-ui/guides/testing/]` |

---

## 5. Visual / Snapshot Regression Testing

| Technology | Documented approach | Citation |
|---|---|---|
| Playwright | `expect(page).toHaveScreenshot()` / `toMatchSnapshot()` auto-generate baselines and diff using the **pixelmatch** algorithm, with a configurable `maxDiffPixels` tolerance | `[Source: https://playwright.dev/docs/test-snapshots]` |
| Jest | Ships built-in snapshot testing as a first-party feature | `[Source: https://jestjs.io/docs/snapshot-testing]` |
| Jest | In `--ci` mode, snapshots are **not** auto-written; a missing/mismatched snapshot fails the build by design, preventing CI from silently accepting drifted snapshots | `[Source: https://jestjs.io/docs/cli]` |
| Vitest | Provides Jest-compatible snapshot testing | `[Source: https://vitest.dev/guide/features.html]` |
| MUI (Material UI) | Snapshot testing is **explicitly discouraged**, citing Kent C. Dodds' argument that snapshot tests "might be misleading for React component tests" — yet internally, the MUI project itself uses **visual regression testing powered by Argos CI** | `[Source: https://mui.com/material-ui/guides/testing/]` |
| Vue | Recommends against relying exclusively on snapshot testing as a testing principle | `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |
| Three.js | Screenshot-comparison is the project's own e2e strategy: "It's good to also add an example and screenshot for it... for end-to-end testing"; r186 changelog shows active work on GPU-native unit tests for TSL and screenshot-based example regression testing | `[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/.github/CONTRIBUTING.md]` |
| Tailwind CSS | Consuming frameworks typically validate Tailwind's output indirectly via visual regression / snapshot testing of rendered markup / E2E testing — but this pattern is not something Tailwind's own docs describe or endorse | `[Inference from tailwind.md, not an explicit doc statement]` |

`[Synthesis: combining MUI's explicit discouragement of snapshot testing for its own guidance to app developers with its own internal use of Argos-CI visual regression, and Vue's parallel "don't rely exclusively on snapshots" principle — two frameworks in this dataset converge on the same view: DOM/JSON snapshot testing is considered lower-value than either semantic (role-based) assertions or true pixel-level visual regression, even though both are colloquially called "snapshot testing."]`

---

## 6. Load / Performance Testing

| Technology | Documented tool/approach | Citation |
|---|---|---|
| Redis | `redis-benchmark` is the official load/performance-testing utility, simulating N concurrent clients issuing M total requests, including targeting a subset of command types | `[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/]` |
| OpenSearch | **OpenSearch Benchmark** is the closest official analogue to a testing framework at the cluster-operations level, used for load/performance testing | `[Source: https://docs.opensearch.org/latest/tools/benchmark/]` |
| ClickHouse | An official hardware performance-test script can benchmark a server "without installation of ClickHouse packages" — useful both as a performance and pre-deployment testing tool | `[Source: https://clickhouse.com/docs/operations/performance-test]` |
| Vitest | Benchmarking via **Tinybench**; v5.0 rewrote `bench` as a test-context fixture invoked within `test()` calls, giving benchmarks access to fixtures, hooks, retries, and assertions | `[Source: https://vitest.dev/blog/vitest-5.html]` |
| Go | Standard `testing` package's `B` type / `BenchmarkXxx` function convention supports benchmarks natively alongside tests | `[Source: https://pkg.go.dev/testing]` |

---

## 7. Contract / Schema / Conformance Testing

| Technology | Documented approach | Citation |
|---|---|---|
| OpenAPI | Mock servers generated from a machine-readable OpenAPI Description are described as a primary use case, returning example responses to support early integration testing before the real implementation exists | `[Source: https://learn.openapis.org/introduction.html]` |
| OpenAPI | Best-practices guidance recommends wiring the OAD into automated CI to verify implementation code matches the OpenAPI description and vice versa — i.e. using the spec itself as a contract-testing source of truth | `[Source: https://learn.openapis.org/best-practices.html]` |
| ECMAScript | **Test262** is the official conformance test suite, formally referenced by ECMA TR/104 and included in ECMA-414, with over 50,000 individual test files (as of a May 2025 count) covering most spec pseudo-code algorithms and grammar productions | `[Source: https://github.com/tc39/test262]` |
| ECMAScript | Test262 conformance is load-bearing in standardization itself: **Stage 4 entrance criteria explicitly require** Test262 acceptance tests plus two independent implementations passing them before a feature is folded into a yearly edition | `[Source: https://tc39.es/process-document/]` |
| WebRTC | The W3C spec references an implementation report and a **Web Platform Tests (WPT)**-based test suite used to validate cross-browser conformance at Recommendation time | `[Source: https://www.w3.org/TR/webrtc/]` |
| CSS | Conformance testing infrastructure lives in the shared **web-platform-tests (WPT)** repository (`css/` directory), used by browser vendors to verify implementations match the spec — this is browser-conformance testing, not application testing | `[Source: https://web-platform-tests.org/test-suite-design.html]` |
| HTML | The **Nu Html Checker (v.Nu)** validates markup for accessibility, usability, interoperability, security, syntax, parsing/error-handling, and content-model/attribute-value violations; usable via web UI, DOM-checking bookmarklet (JSON output), CLI/batch, and Grunt/Gulp plugins | `[Source: https://validator.w3.org/nu/about.html]` |
| HTML | The checker's own docs caution it "should not be used as a means to attempt to unilaterally enforce pass/fail conformance," and a zero-error result today is no guarantee of zero errors later since its rule set expands over time | `[Source: https://validator.w3.org/nu/about.html]` |
| CSS | MDN's author-facing validation guidance centers on the **W3C CSS Validator** and **W3C HTML Validator** as first-line tools to catch syntax errors, since invalid CSS otherwise fails silently | `[Source: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Debugging_CSS]` |
| Google SEO | The **Rich Results Test** is the official tool for validating structured-data markup before/after deployment, with post-deployment monitoring via the Rich result status report in Search Console | `[Source: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data]` |

---

## 8. Other Notable / Specialized Testing Approaches

Facts that don't map cleanly onto the seven layers above but are documented and worth preserving:

- **Fuzz testing (Go):** Native fuzz testing (`testing.F`, `go test -fuzz`) integrated into the standard toolchain since Go 1.18, also exercised continuously via OSS-Fuzz. `[Source: https://go.dev/security/]`
- **Race detection (Go):** The `-race` flag on `go test`/`go run`/`go build`/`go install` integrates the Data Race Detector to instrument memory accesses for concurrent unsynchronized access detection. `[Source: https://go.dev/doc/articles/race_detector.html]`
- **Application-wide coverage (Go):** A dedicated official doc covers coverage-testing *whole applications*, distinct from per-package `go test -cover`. `[Source: https://go.dev/doc/build-cover]`
- **Coverage tooling (Vitest):** v8 or Istanbul providers, with HTML/html-spa/lcov/JSON/custom reporters. `[Source: https://vitest.dev/guide/coverage.html]`
- **Coverage tooling (Jest):** `--coverage`/`collectCoverage` instruments via babel or v8 providers, with configurable `coverageThreshold` that can fail a run. `[Source: https://jestjs.io/docs/configuration, https://jestjs.io/docs/cli]`
- **Manual mocks (Jest):** Live in a `__mocks__/` directory, used with `jest.mock()`; exact auto-application semantics by location flagged as unresolved in the source doc. `[Source: https://jestjs.io/docs/mock-functions] (Unresolved per jest.md Testing section)`
- **Reporters (Playwright):** Built-in reporters cover local dev (`list`), CI-compact (`dot`, default on CI), machine-readable (`json`, `junit`), self-contained visual (`html`), sharded-report merging (`blob`), and profiling (`perfetto`); named third-party reporters: Allure, ReportPortal, Monocart. `[Source: https://playwright.dev/docs/test-reporters]`
- **Type checking is separate from test running (Playwright):** the test runner does not perform type checking itself; a separate `tsc` invocation is the documented way to catch type errors alongside running tests. `[Source: https://playwright.dev/docs/test-typescript]`
- **Sanitizers / static analysis (ClickHouse):** Sanitizer runs (ASan/TSan/MSan/UBSan), fuzzing (libFuzzer plus random SQL-query generation), a Thread Fuzzer, and static analysis (clang-tidy, clang-static-analyzer, shellcheck). `[Source: https://clickhouse.com/docs/resources/develop-contribute/contribute/tests]`
- **Functional (reference-diff) tests (ClickHouse):** `.sql`/`.sh` scripts under `tests/queries` run against a live server and compared to reference results — mandatory for every testable code change, subcategorized into fast/minimal, stateless, and sequential. `[Source: https://clickhouse.com/docs/resources/develop-contribute/contribute/tests]`
- **Ad-hoc/scripted testing (Redis):** `redis-cli` supports piping command files, `-r`/`-i` for repeated execution, `--pipe` for raw-protocol bulk injection, `-x`/`-X` for stdin-as-argument — useful for scripted setup/teardown in test fixtures. `[Source: https://redis.io/docs/latest/develop/tools/cli/]`
- **Lua script testing (Redis):** `redis-cli --eval <file>` runs a script file directly; `redis-cli --ldb` (with `--ldb-sync-mode`) launches the official Lua debugger (since Redis 3.2). `[Source: https://redis.io/docs/latest/develop/programmability/]`
- **Docker Build Checks:** `docker build --check` functions as an advanced lint/dry-run pass over a Dockerfile without producing build output (requires Buildx ≥0.15.0, Dockerfile syntax ≥1.8). `[Source: https://docs.docker.com/reference/build-checks/]`
- **Container health checks (Docker):** The `HEALTHCHECK` Dockerfile instruction defines an in-container command Docker runs periodically, surfaced via `docker ps`/`docker inspect`, configurable via `docker run --health-*` flags. `[Source: https://docs.docker.com/reference/dockerfile/]`
- **CI build/test automation (Docker):** Official GitHub Actions (`docker/build-push-action`, `docker/setup-buildx-action`, `docker/login-action`, `docker/metadata-action`, `docker/setup-qemu-action`) are documented for composing a CI pipeline that builds and validates an image on every push/PR before merge. `[Source: https://docs.docker.com/build/ci/github-actions/]`
- **Hook testing (Husky):** The only officially documented technique for testing a Git hook without side effects is to temporarily append `exit 1` to the hook script, run the corresponding Git command, observe the output, confirm the operation aborted, then remove the `exit 1` line. `[Source: https://typicode.github.io/husky/how-to.html]` Husky does not ship or document a dedicated testing framework, mocking utility, or CI-testing guide for hooks — they are treated as ordinary shell scripts. `[Source: research/technologies/husky.md, Section 9 — no official testing-framework doc found]`
- **Custom GitHub Action testing:** GitHub's `actions/toolkit` repo documents unit-testing action logic with standard JS test frameworks (its own CI uses Jest) against `@actions/core`/`@actions/github`, decoupled from actually running inside an Actions job. `[Source: https://github.com/actions/toolkit]` GitHub also publishes **github/local-action**, a VS Code-usable utility for running/debugging a custom JS action locally by emulating core Actions Toolkit functionality without an actual workflow run. `[Source: https://github.com/github/local-action]` No official GitHub-maintained tool exists for running full workflows locally end-to-end — the widely used community tool for that (`nektos/act`) is not GitHub-maintained. `[Source: research/technologies/github-actions.md, section 9, 'Not documented / could not verify' note]`
- **DevTools-based inspection (WebSocket API):** Firefox DevTools' Network Monitor has a dedicated WebSocket frame inspector (filter `WS`/HTTP 101, live frame table with Data/Size/Time/OpCode/MaskBit/FinBit, filter by All/Sent/Received/Control), with automatic pretty-printing for known sub-protocol payloads including JSON, **Socket.IO**, SignalR, STOMP, and WAMP. `[Source: https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/inspecting_web_sockets/index.html]`
- **SEO indexing/rendering verification (Google SEO):** The URL Inspection tool in Search Console checks live indexing status, confirms the HTTP status Google received, and shows how Googlebot rendered the page. `[Source: https://developers.google.com/search/docs/essentials/technical]` For JS-rendered pages, testing must verify the rendered DOM (post-JS execution), not just the raw server response, since Google indexes post-render HTML. `[Source: https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics]` The `site:` search operator is a documented quick manual check for whether a URL is already indexed. `[Source: https://developers.google.com/search/docs/fundamentals/seo-starter-guide]` Google cautions that SEO change impact takes weeks to months to assess, recommending Search Console Performance-report comparisons (filtered by URL) over months rather than immediate signal. `[Source: https://developers.google.com/search/docs/fundamentals/seo-starter-guide]`
- **Ad-serving validation (Google AdSense):** The Ad review center inspects ads actually served (creative/metadata/metrics, filter by network/type, block by image upload). `[Source: https://support.google.com/adsense/answer/13547173?hl=en]` Dedicated troubleshooters exist (ads.txt troubleshooter, Policy troubleshooter). `[Source: https://support.google.com/adsense/troubleshooter/9556696?hl=en]` The Policy center is an ongoing compliance-validation surface but explicitly caveats that review "can't detect every issue" — not an exhaustive compliance test. `[Source: https://support.google.com/adsense/answer/9485926?hl=en]` No official sandbox/staging mode for fake test ads was found; AdSense appears to serve only live ads, and policy explicitly prohibits clicking one's own live ads even for testing. `[Inference from google-adsense.md, not an explicit doc statement]`
- **Chat-UI deterministic testing (shadcn/ui):** `@shadcn/helpers`'s AI SDK integration lets developers script an AI conversation and stream it through `useChat` with no model, API route, or network calls — explicitly framed as enabling deterministic chat-UI testing in CI "with no network calls, token spend, or flaky model output." `[Source: https://ui.shadcn.com/docs/helpers/ai-sdk]`
- **Migration validation (GitHub):** GitHub Enterprise Importer documents support for trial migrations to validate an org/repo migration path before the real cutover, plus detailed error logging that lets a migration continue past non-critical failures for later inspection. `[Source: https://docs.github.com/en/migrations/using-github-enterprise-importer/understanding-github-enterprise-importer/about-github-enterprise-importer]`

---

## Tool Cross-Reference: Playwright, Jest, Vitest, and others

### Playwright
| Consuming technology | Role documented | Citation |
|---|---|---|
| Nuxt | One of 4 official E2E runners; `createPage()` gives a configured Playwright page; first-class `@nuxt/test-utils/playwright` integration | `[Source: https://nuxt.com/docs/4.x/getting-started/testing]` |
| Next.js | Official first-party E2E setup guide; new `@next/playwright` package (16.3) with `instant()` helper | `[Source: https://nextjs.org/docs/app/guides/testing]`, `[Source: https://nextjs.org/blog/next-16-3]` |
| Vue | Recommended for E2E (cross-browser, praised for debugging) | `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |
| Angular | Available real-browser testing provider alongside default Vitest | `[Source: https://angular.dev/guide/testing]` |
| Vitest | Recommended provider for Browser Mode | `[Source: https://vitest.dev/guide/browser/]` |
| Playwright (self) | Full framework: test runner, fixtures, API testing, component testing (React/Vue), visual regression, reporters, `tsc`-based type checking | multiple, see Sections 3–5 above |

### Jest
| Consuming technology | Role documented | Citation |
|---|---|---|
| Mongoose | **Explicitly discouraged** — "We strongly recommend using a different testing framework, like Mocha"; if used anyway, requires `testEnvironment: 'node'`, avoiding fake timers, `resetModules: false`, `SUPPRESS_JEST_WARNINGS=1` | `[Source: https://mongoosejs.com/docs/jest.html]` |
| Prisma | Officially recommended for unit testing (with `jest-mock-extended`) | `[Source: https://www.prisma.io/docs/orm/prisma-client/testing/unit-testing]` |
| Nuxt | One of 4 official E2E runners | `[Source: https://nuxt.com/docs/4.x/getting-started/testing]` |
| Next.js | Official first-party unit-testing setup guide | `[Source: https://nextjs.org/docs/app/guides/testing]` |
| Vue | Alternative unit-test runner via community `vite-jest` adapter — **not** first-line recommendation (Vitest is) | `[Source: https://vuejs.org/guide/scaling-up/tooling.html]` |
| Socket.IO | Official testing guide demonstrates the identical pattern in Jest, Mocha, Tape, and Vitest | `[Source: https://socket.io/docs/v4/testing/]` |
| Husky | Migration guide example: `"pre-commit": "jest"` (v4) becomes a plain `jest` line in `.husky/pre-commit` | `[Source: https://typicode.github.io/husky/migrate-from-v4.html]` |
| TypeScript | **No** Jest integration documented on typescriptlang.org's build-tools page (Babel, Browserify, Gulp, Webpack, Rollup, Vite, Grunt, Svelte, Jspm, MSBuild/NuGet are covered; Jest/Mocha/Vitest/Playwright are not) | `[Source: https://www.typescriptlang.org/docs/handbook/integrating-with-build-tools.html]` |
| Vite | Cited for its Jest-API compatibility as the reason Vitest migration is easy | `[Source: https://vitest.dev/guide/]` |
| GitHub Actions | `actions/toolkit`'s own CI uses tools such as Jest for unit-testing custom JS action logic | `[Source: https://github.com/actions/toolkit]` |
| Express | Supertest (community, not expressjs.com-maintained) is the documented Jest pairing for Express API testing — per Jest's own docs, not Express's | `[Source: https://jestjs.io/docs/testing-frameworks]` (Express side: `[Source: research/technologies/express.md Section 9]`) |
| React | React Testing Library is the community-documented Jest pairing for React components (per Jest's docs, not React's) | `[Source: https://jestjs.io/docs/testing-frameworks]` |
| shadcn/ui | **No official guide** for unit-testing installed components with Jest | `[Inference from shadcn-ui.md, not an explicit doc statement]` |
| Jest (self) | Built-in mocking, snapshot testing, fake timers, coverage (babel/v8 providers + `coverageThreshold`), manual mocks via `__mocks__/`, `--ci` snapshot-write suppression | multiple, see Sections 1 and 5 above |

### Vitest
| Consuming technology | Role documented | Citation |
|---|---|---|
| Nuxt | The **only** supported unit-test runner for the Nuxt runtime environment; also one of 4 official E2E runners | `[Source: https://nuxt.com/docs/4.x/getting-started/testing]` |
| Next.js | Official first-party unit-testing setup guide | `[Source: https://nextjs.org/docs/app/guides/testing]` |
| Vue | **First-line official recommendation** for unit testing, "created and maintained by members of the Vue / Vite team" | `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |
| Angular | **Default** test runner for new Angular CLI projects (v21+), replacing Karma | `[Source: https://angular.dev/guide/testing]` |
| Drizzle ORM | Community (not first-party) pairing with PGlite as the de facto in-memory Postgres testing story | `[Inference from drizzle.md, not an explicit doc statement]` |
| Socket.IO | Official testing guide demonstrates the identical pattern in Vitest, Mocha, Jest, and Tape | `[Source: https://socket.io/docs/v4/testing/]` |
| Vite | Vitest is "a next generation testing framework powered by Vite," reusing Vite config/plugins | `[Source: https://vitest.dev/guide/]`; also has a built-in DevTools integration (`@vitejs/devtools-vitest`) | `[Source: https://devtools.vite.dev/vitest/]` |
| shadcn/ui | **No official guide** for unit-testing installed components with Vitest | `[Inference from shadcn-ui.md, not an explicit doc statement]` |
| Vitest (self) | Browser Mode (Playwright/WebdriverIO), coverage (v8/Istanbul), type testing (expect-type), benchmarking (Tinybench), component testing (Vue/React/Svelte/Lit/Marko), in-source testing, Jest migration mapping | multiple, see Sections 1, 3, 5, 6 above |

### Other named testing tools worth tracking
| Tool | Where documented | Citation |
|---|---|---|
| Cypress | Next.js official E2E/component setup guide; Vue's recommended component-testing (Cypress Component Testing) and E2E alternative | `[Source: https://nextjs.org/docs/app/guides/testing]`, `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |
| `@testing-library/react` | React's official recommended replacement for deprecated `react-test-renderer`; MUI's explicitly recommended tool; Jest docs' community-documented React pairing | `[Source: https://react.dev/warnings/react-test-renderer]`, `[Source: https://mui.com/material-ui/guides/testing/]`, `[Source: https://jestjs.io/docs/testing-frameworks]` |
| `@testing-library/vue` | Named as a community user-centric alternative to `@vue/test-utils`; used in Vue's minimal Vitest setup example (`npm install -D vitest happy-dom @testing-library/vue`) | `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |
| `@vue/test-utils` | Vue's official low-level component-mounting library, fast Node-based | `[Source: https://vuejs.org/guide/scaling-up/testing.html]` |
| WebdriverIO | Angular real-browser testing provider; Vitest Browser Mode provider | `[Source: https://angular.dev/guide/testing]`, `[Source: https://vitest.dev/guide/browser/]` |
| Testcontainers | Docker's documented integration-testing pattern; OpenSearch's official `opensearch-testcontainers` module (JUnit 4/5) | `[Source: https://docs.docker.com/testcontainers/]`, `[Source: https://github.com/opensearch-project/opensearch-testcontainers]` |
| Supertest | Documented Jest pairing for Express (per Jest's docs); alternative real-HTTP-client option named in Fastify's testing guide | `[Source: https://jestjs.io/docs/testing-frameworks]`, `[Source: https://fastify.dev/docs/latest/Guides/Testing/]` — **not** an official Express-maintained tool: `[Source: research/technologies/express.md Section 9]` |
| gtest | ClickHouse's unit-testing framework (via CMake `ENABLE_TESTS` + `ninja test`) | `[Source: https://clickhouse.com/docs/resources/develop-contribute/contribute/tests]` |
| `node:test` | Fastify's own guide examples use Node's built-in test runner | `[Source: https://fastify.dev/docs/latest/Guides/Testing/]` |
| Test262 | ECMAScript's official conformance suite, load-bearing for TC39 Stage 4 | `[Source: https://github.com/tc39/test262]`, `[Source: https://tc39.es/process-document/]` |
| Web Platform Tests (WPT) | Conformance testing shared infra for WebRTC (referenced by the W3C spec) and CSS (`css/` directory) | `[Source: https://www.w3.org/TR/webrtc/]`, `[Source: https://web-platform-tests.org/test-suite-design.html]` |
| Argos CI | MUI's internal visual-regression testing tool | `[Source: https://mui.com/material-ui/guides/testing/]` |
| Storybook | Built directly on top of Vite, extending it into component-workshop tooling (test-adjacent, not itself a test runner in this data) | `[Source: https://vite.dev/guide/why]` |

---

## Notable Gaps: No First-Party Testing Guidance Documented

These technologies have `testingRelationships` entries whose content is itself a documented (or inferred) **absence** of official testing guidance — surfaced explicitly per the task instructions rather than silently omitted:

| Technology | Nature of the gap | Citation |
|---|---|---|
| **PostgreSQL** | No application-level testing methodology (ephemeral test DBs, transactional isolation, fixtures) documented; no official equivalent to Testcontainers or ephemeral-DB-for-CI story — left to ecosystem tooling | `[Inference from postgresql.md, not an explicit doc statement]`; `[Source: postgresql.md Section 9, 'Not documented / could not verify' note]` |
| **MySQL** | Reference manual has no first-party guidance on testing applications against MySQL (ephemeral DBs, fixtures, transactional isolation); own test suite (`mysql-test-run.pl`) is scoped to the server codebase itself | `[Source: https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_MYSQL_TEST_RUN_PL.html]` |
| **MongoDB** | Driver best-practices page is security-scoped only, no unit/integration methodology; official confirmation of in-memory test servers (e.g. `mongodb-memory-server`) could not be found — only community forum discussion | `[Source: https://www.mongodb.com/docs/drivers/client-libraries-best-practices/]`; `[Inference from mongodb.md, not an explicit doc statement]` |
| **TypeORM** | No dedicated official "Testing" guide on typeorm.io at all; all discovered guidance (Jest patterns, in-memory SQLite, repository mocking, `MockTypeORM`) is third-party/community | `[Inference from typeorm.md, not an explicit doc statement]` |
| **Express** | expressjs.com publishes no official first-party testing guide; supertest is community-maintained, not under the expressjs GitHub org | `[Source: research/technologies/express.md Section 9, citing absence of official coverage across expressjs.com]` |
| **TypeScript** | Official Handbook/Reference has no dedicated page on unit testing, test runners, or testing patterns; TypeScript does not ship or endorse a testing framework; build-tools integration page omits Jest/Vitest/Playwright entirely | `[Source: Section 9 of typescript.md]`; `[Source: https://www.typescriptlang.org/docs/handbook/integrating-with-build-tools.html]` |
| **Redis** | No official "testing your application against Redis" guide found: no first-party in-memory test double, no first-party Testcontainers module, no first-party unit-testing framework integration guide | `[Source: https://redis.io/docs/latest/develop/programmability/]` |
| **GraphQL** | No official GraphQL or graphql-js testing methodology guide located; `www.graphql-js.org/docs/testing/` returned **HTTP 404** during research, and no equivalent page exists on graphql.org | `[Inference from graphql.md] (underlying gap documented at [Source: https://www.graphql-js.org/docs/testing/] returning 404)` |
| **HTML** | The spec does not define unit/integration/E2E testing methodology for HTML documents/applications — delegated to unnamed separate ecosystems (browser automation, accessibility-testing tools) | `[Source: https://html.spec.whatwg.org/multipage/introduction.html]` |
| **WebSocket API** | No official unit/integration-testing framework, mocking library, or WHATWG/IETF-endorsed conformance test suite for API *consumers* was found (browser-engine conformance testing is out of scope for application developers) | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API]` |
| **Sass** | No dedicated "Testing" section or officially maintained testing framework; `sass:meta` introspection module is the closest building block but is framed as inner-workings introspection, not a test framework. Community tool `true` exists but is not part of official docs | `[Source: sass.md §9 Testing]`; `[Inference, not confirmed in docs]` |
| **Tailwind CSS** | No dedicated first-party testing guide; as a build-time CSS-generation tool it has no runtime component behavior to unit-test. Closest first-party QA tooling is editor-time IntelliSense linting, not an automated test suite | `[Inference from tailwind.md, not an explicit doc statement]`; `[Source: https://tailwindcss.com/docs/editor-setup]` |
| **Three.js** | No official first-party guide for how *application developers* (as opposed to library contributors) should unit-test or visually-regression-test their own three.js-based apps (headless-WebGL harnesses, canvas pixel-diffing, WebGPU CI strategies) | `[Inference from threejs.md, not an explicit doc statement]` |
| **ClickHouse** | Documented testing content covers testing ClickHouse's own server code, not client application code against it; no official application-facing test-container/mocking guide located | `[Source: https://clickhouse.com/docs/resources/develop-contribute/contribute/tests — gap noted in doc]` |
| **Swagger** | Could not confirm official unit-test or Cypress E2E invocation commands for Swagger UI's own test suite; expected `CONTRIBUTING.md` returned 404 during research | `[Source: swagger.md research note]` |
| **shadcn/ui** | No dedicated general "Testing" guide for UI components — no official guidance on unit-testing installed components with Vitest, Jest, or Testing Library, and no official visual-regression tooling (the one exception is the narrow AI-SDK chat-mocking helper, see Section 8) | `[Inference from shadcn-ui.md, not an explicit doc statement]` |
| **Google AdSense** | No official staging/sandbox mode for serving fake/test ads found; appears to serve only live ads, and policy prohibits clicking one's own live ads even for testing purposes — constraining how testing can be done at all | `[Inference from google-adsense.md, not an explicit doc statement]` |
| **GitHub Actions** | No official GitHub-maintained tool for running full workflows locally end-to-end; the widely used community tool for that (`nektos/act`) is not GitHub-maintained | `[Source: research/technologies/github-actions.md, section 9, 'Not documented / could not verify' note]` |
| **Python (pytest specifically)** | docs.python.org does not document third-party test runners/frameworks (pytest, nose2, hypothesis) at all — explicitly out of scope, even though pytest is arguably the de facto standard in the wider ecosystem | `[Source: python.md Section 9, citing absence in docs.python.org]` |

`[Synthesis: combining the PostgreSQL, MySQL, and Redis gap entries — all three foundational data-layer technologies in this dataset explicitly lack a first-party "how to test your app against me" story, uniformly deferring that responsibility to ORMs, drivers, or ecosystem tooling (e.g. Testcontainers, which is itself only Docker-documented, not database-vendor-documented). Combined with TypeORM's similarly absent official testing guide, an application built on Postgres/MySQL/Redis via TypeORM would have zero official first-party testing documentation to draw on at any layer of that stack — only Drizzle ORM (PGlite) and Prisma (Jest + jest-mock-extended) break this pattern among the ORMs surveyed.]`

---

## Summary Observations

- **Playwright and Vitest are the two most cross-cutting testing tools** in this dataset: Playwright is independently recommended (by official docs) for E2E testing in Nuxt, Next.js, Vue, and Angular, and additionally sits *underneath* Vitest's own Browser Mode — making it the shared browser-automation layer for multiple frameworks' testing stories at once (see Section 3 synthesis).
- **Jest's status is split**: strongly recommended by Prisma; used as one of several official options by Nuxt, Next.js, and Socket.IO; explicitly *discouraged* by Mongoose ("recommend using a different testing framework, like Mocha"); and conspicuously *absent* from TypeScript's own official build-tools integration guide despite `ts-jest` existing in the wider ecosystem.
- **Vitest has become the default** for two major frameworks independently — Vue (via Vite-team authorship) and Angular (CLI v21+, replacing Karma) — while remaining Nuxt's only supported runtime-environment test runner.
- **Database/infrastructure technologies (PostgreSQL, MySQL, Redis, ClickHouse for app code) systematically lack first-party application-testing guidance**, in contrast to newer ORMs (Prisma, Drizzle) and to Docker/MongoDB/OpenSearch, which do document first-party or first-party-adjacent containerized-testing patterns (Testcontainers, `mongodb-atlas-local`, `opensearch-testcontainers`).
- **Snapshot/DOM-diffing testing is treated skeptically by frameworks that have an official opinion on it** (MUI discourages it explicitly; Vue warns against relying on it exclusively), while true pixel-level visual regression (Playwright's `toHaveScreenshot()`, MUI's internal Argos CI use, Three.js's screenshot-comparison e2e strategy) is treated as the more trustworthy sibling.
- Several technologies (TypeScript, HTML, CSS, Sass, Tailwind, WebSocket API) are **language/spec/tooling layers that structurally have no runtime behavior of their own to test**, and their gaps reflect that rather than an oversight — worth distinguishing from technologies (Redis, MySQL, PostgreSQL, GraphQL) that *do* have runtime behavior but simply lack documented first-party testing guidance for it.
