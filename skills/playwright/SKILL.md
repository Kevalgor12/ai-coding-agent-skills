---
name: Playwright
description: >-
  Playwright implementation: @playwright/test fixture-based composition,
  APIRequestContext for server-only API testing, visual regression via
  pixelmatch, the stable component-testing model, and Docker deployment
  security (storageState leaks, root-vs-sandboxed posture). Use when the
  stack uses Playwright or the task needs E2E/browser/visual/component/API
  test implementation or Playwright Docker/CI setup. Not for test-layer
  selection (testing-strategy) or role-locator a11y framing.
spec_version: "1.0"
---

## Purpose & scope

Apply Playwright correctly and version-appropriately (`>=1.60 <=1.63`) for
browser-based E2E testing, server-only API testing, visual regression, and
component testing, plus its Docker deployment and security posture. This
skill specializes two Layer-3 parents and does not repeat their content:
[testing-strategy](../testing-strategy/SKILL.md) owns test-layer selection
(when to use unit/integration/e2e/component/visual at all);
[web-accessibility](../web-accessibility/SKILL.md) owns Playwright's
role-based Locators API and MCP accessibility-tree framing as an
accessibility signal. What follows is Playwright-specific implementation
depth beyond both.

## When to use / When not to use

**Use** when the stack has a `playwright.config.ts`/`.js` or
`@playwright/test` dependency, or the task needs E2E/browser/visual/
component/API test implementation, or Playwright's Docker/CI deployment is
being configured. **Do not use** to decide *whether* E2E/visual/component
testing is the right layer at all (route to testing-strategy), or for
role-based-locator accessibility guidance as an a11y signal (route to
web-accessibility). Also not for a stack using a different E2E tool with no
Playwright involvement underneath it.

## Knowledge

**Core package.** `@playwright/test` bundles the test runner, an
expect-based auto-retrying web-first assertion library, and reporting in
one package [Source: playwright.dev/docs/intro]. Test composition is
**fixture-based**, not purely hook-based: built-in fixtures (`page`,
`context`, `browser`, `browserName`, `request`) come out of the box, custom
fixtures are declared via `test.extend()` wrapping setup/teardown around
`await use()`, and fixtures can be test-scoped (default), worker-scoped
(`{ scope: 'worker' }`, shared across a worker's tests), or `{ auto: true }`
(run for every test without explicit reference) — "composability,
reusability, and on-demand setup" [Source: playwright.dev/docs/test-fixtures].

**API testing is a first-class, separate mode.** `APIRequestContext`
(the built-in `request` fixture, which respects `baseURL`/
`extraHTTPHeaders`, or a standalone `apiRequest.newContext()`) issues raw
HTTP requests with no browser involved — usable for pure API suites,
precondition setup, or post-UI-action server-side verification, and can
produce/consume `storageState()` to bridge API-obtained auth into a browser
context [Source: playwright.dev/docs/api-testing]. This is a real, distinct
capability, not just a browser-automation add-on.

**Visual regression.** `expect(page).toHaveScreenshot()` /
`toMatchSnapshot()` auto-generate baseline images on first run and diff on
subsequent runs using the `pixelmatch` algorithm, with a configurable
`maxDiffPixels` tolerance; snapshot filenames embed browser/platform
identifiers, and `stylePath` can inject CSS to hide non-deterministic
elements before capture [Source: playwright.dev/docs/test-snapshots].
Comparisons are sensitive to host OS, browser version, hardware, and
headless-vs-headed mode — reproducible baselines require matching the
environment they were generated in; this is a documented constraint, not a
bug [Source: playwright.dev/docs/test-snapshots].

**Component testing.** Mounts and tests individual UI components in a real
browser while the test itself runs in Node, via `fixtures.mount()` and a
"stories/galleries" model. **[Version-sensitive, `>=1.62`]** This model
became stable at **v1.62**, the same release that introduced it — the older
`@playwright/experimental-ct-react[-17]`/`-vue` packages are **[`>=1.63`]**
deprecated/no longer updated in its favor [Source:
playwright.dev/docs/test-components; playwright.dev/docs/release-notes].
Officially supported frameworks are React and Vue; accessing a component's
internal instance/methods from test code is unsupported.

**Docker deployment.** Official images are published per Ubuntu base
(22.04 "Jammy", 24.04 "Noble" — default/untagged, 26.04 "Resolute"), tagged
`mcr.microsoft.com/playwright:v<version>[-<codename>]`, e.g.
`v1.63.0-noble`. **Pin the image tag to the exact Playwright version** so
bundled browser binaries match the automation code's Playwright version —
a mismatch here is a real, common source of flaky/broken CI [Source:
playwright.dev/docs/docker]. **Alpine Linux is explicitly unsupported** as
a base image: "musl library incompatibility with browser builds" [Source:
playwright.dev/docs/docker]. Playwright also supports a remote **Playwright
Server** mode inside Docker (listening on a port, e.g. 3000) for
distributed/remote browser execution [Source: playwright.dev/docs/docker].

**Version grounding** (per `research/knowledge-maps/version-matrix.md`,
also in `research/technologies/playwright.md` §13): Node.js support is
"Latest 22.x, 24.x or 26.x"; OS support is Windows 11+/Server 2019+/WSL,
macOS 14+, Debian 12/13 or Ubuntu 22.04/24.04/26.04. **[`>=1.63`]** Ubuntu
20.04 is no longer supported. **[`>=1.62`]** Debian 11 end-of-support was
announced. **[`>=1.60`]** Several long-deprecated APIs were removed:
`Locator.ariaRef()`, the `handle` option on `exposeBinding()`, the `logger`
option on `connect()`/`connectOverCDP()`, and `context.videoPath()`/legacy
video-size options — a real, dated breaking-change list, not a hypothetical
one. **Unresolved:** macOS 13 WebKit support deprecation and
`route.continue()` losing the ability to override the `Cookie` header are
believed to date to **v1.52** per the source research's summarized fetch,
but this version tag is explicitly unconfirmed — do not state it as
settled fact.

## Decision framework

1. **Does this need a real browser at all, or only server-side
   verification?** If the check is purely "did the server do the right
   thing" (a webhook fired, a record was created, a response shape is
   correct), use `APIRequestContext` alone — it's faster and has no browser
   overhead. Reach for full browser automation only when user-facing
   rendering/interaction is actually what's under test.
2. **Root or non-root+seccomp for the Docker container?** If the
   automation touches **untrusted content** (scraping/crawling arbitrary
   sites), use a dedicated non-root user plus a seccomp security profile to
   keep Chromium's OS-level sandbox active — running as root disables that
   sandbox. If the container only runs **your own trusted test suite**,
   root without the extra hardening is acceptable per the docs [Source:
   playwright.dev/docs/docker]. Don't default to the heavier hardening
   where it isn't needed, and don't skip it where it is.
3. **Component testing or full E2E?** Component testing is warranted when
   the risk is genuinely isolated to one component's rendering/behavior and
   a real backend/routing context isn't relevant — it's cheaper and more
   targeted. Once the test needs to verify multi-component/page interaction
   or real navigation, that's E2E territory, not a component test stretched
   to cover it.
4. **Do nothing beyond the simplest option that catches the risk** — the
   over-engineering trap here is reaching for a full multi-browser E2E
   suite (or visual regression) when a fast `APIRequestContext` check or a
   component test already proves the behavior.

## Engineering rules

- Use locators resilient to DOM changes — prioritize role/text/label over
  CSS classes or XPath tied to structure; use codegen/VS Code extension to
  generate them [Source: playwright.dev/docs/best-practices].
- Use web-first assertions (`expect(locator).toBeVisible()`, etc.) that
  auto-wait and retry; never check an unretried `isVisible()` boolean
  manually [Source: playwright.dev/docs/best-practices].
- Reuse signed-in state via a one-time setup project persisting
  `storageState` rather than logging in per test; use per-worker unique
  accounts for tests that mutate shared server-side state [Source:
  playwright.dev/docs/auth].
- Mock third-party dependencies via the Network API (`route.fulfill()`,
  HAR replay) instead of hitting real third-party servers [Source:
  playwright.dev/docs/best-practices; playwright.dev/docs/network].
- Design tests so parallel workers never depend on shared execution order
  or shared mutable state; derive unique identifiers from `testInfo`
  metadata (e.g. `parallelIndex`), not hardcoded shared resources [Source:
  playwright.dev/docs/test-parallel].
- Pin the Docker image tag to the exact installed Playwright version
  **[`>=1.60 <=1.63`]**; never run an untagged/`latest` image against a
  pinned `package.json` version.
- Do not cache browser binaries between CI runs — restore time is
  comparable to fresh download time, and Linux OS-level dependencies can't
  be cached at all [Source: playwright.dev/docs/ci].

## Trade-offs

`APIRequestContext`-only testing is fast and has no browser overhead but
can't catch rendering/interaction bugs — use it only where the risk is
genuinely server-side. Full browser E2E catches real user-facing
regressions but is the slowest, most resource-heavy layer, and cross-
browser (Chromium/Firefox/WebKit) runs multiply that cost further.
Component testing sits between the two: cheaper than E2E, but only proves
one component's isolated behavior, not integration. Docker's non-root +
seccomp hardening adds setup complexity that's wasted effort for a trusted
own-suite container but is not optional for anything touching untrusted
content — match the posture to the actual trust boundary, don't apply the
heavier one everywhere by default.

## Anti-patterns

- **Committing `playwright/.auth` storageState files to version control**
  — these can carry live, impersonation-capable session cookies/headers
  [Source: playwright.dev/docs/auth]. Gitignore them.
- **Running Chromium as root in Docker against untrusted content** without
  the documented non-root-user + seccomp hardening — this silently
  disables the OS-level sandbox [Source: playwright.dev/docs/docker].
- **Adding `--no-sandbox`** to the Chromium launch flags — it "disables
  browser sandboxing for process types that normally use it and should not
  be added by default" [Source: playwright.dev/docs/docker]. Flag this if
  found in existing config.
- **Using an Alpine base image** for a Playwright Docker container — musl
  libc is incompatible with the bundled browser builds and this is
  explicitly unsupported [Source: playwright.dev/docs/docker].
- **Mismatched Docker image tag vs. installed Playwright version** (e.g.
  an untagged/`latest` image with a pinned older `package.json` version) —
  a real, common source of flaky/broken CI from browser/code version skew.
- **Reaching for full multi-browser E2E when `APIRequestContext` alone
  would prove the behavior** — the over-engineering trap for this domain;
  see Decision framework.
- **Caching browser binaries between CI runs** — explicitly discouraged;
  restore cost is comparable to fresh download, and Linux OS deps aren't
  cacheable regardless [Source: playwright.dev/docs/ci].

## Security

**`storageState` credential leak risk.** Browser state files persisted via
`storageState` "may contain sensitive cookies and headers that could be
used to impersonate you or your test account" [Source:
playwright.dev/docs/auth]. Keep `playwright/.auth` (or wherever
`storageState` is written) out of version control via `.gitignore`;
rotate/regenerate these files as credentials expire, since the setup
project that creates them does not auto-run in UI mode.

**Root vs. sandboxed Docker posture, by use case.** For automation against
**untrusted** content (web scraping/crawling arbitrary sites), official
guidance is a dedicated non-root user plus a seccomp security profile to
keep Chromium's OS-level sandbox active. For **trusted** code — your own
E2E suite against your own app — root without that extra hardening is
presented as acceptable [Source: playwright.dev/docs/docker]. This is a
real distinction to apply deliberately, not a one-size-fits-all rule: don't
under-harden a scraper, and don't over-harden a trusted test container.

**`--no-sandbox` as an explicit anti-pattern.** The Chromium
`--no-sandbox` flag "disables browser sandboxing for process types that
normally use it and should not be added by default" [Source:
playwright.dev/docs/docker] — flag this immediately if seen in existing
launch config or Dockerfiles.

**Playwright MCP's `browser_run_code_unsafe` signal.** Playwright MCP
ships a tool literally named `browser_run_code_unsafe`, signaling that
arbitrary-code-execution capability requires caution when an LLM agent is
driving the browser via MCP [Source: playwright.dev/mcp/introduction].
This naming is, per the source research, the extent of what's explicitly
documented on the fetched introduction page — no further security-warning
prose beyond the tool's own name was found; treat the tool name itself as
the operative warning and gate its use accordingly.

## Performance

Beyond the test-suite-runtime concerns testing-strategy already owns, the
Test runner's primary lever is **worker-based parallelism**: multiple OS
processes each with an isolated browser instance, configured via `workers`
(count or percentage string), with `fullyParallel` enabling parallel
execution within a file, not just across files [Source:
playwright.dev/docs/test-parallel]. In CI, official guidance is
`workers: 1` for stability/reproducibility on constrained runners, then
scale via **sharding** (`--shard=X/Y`) across machines rather than raising
in-job concurrency [Source: playwright.dev/docs/ci]. `retryStrategy:
'isolated'` runs retries after all other tests complete, reducing cross-
test interference; `maxFailures` bounds wasted CI time by stopping after N
failures [Source: playwright.dev/docs/api/class-testconfig]. Video
recording is off by default and only adds overhead when enabled, downscaled
to a max 800×800 by default [Source: playwright.dev/docs/videos]. No
numeric overhead figures for tracing/video/screenshot capture are
documented in the fetched pages.

## Testing

`@playwright/test` is itself the testing framework: bundled test runner,
expect-based web-first assertions (auto-waiting/retrying), and reporting in
one package [Source: playwright.dev/docs/intro]. Fixtures (test-scoped,
worker-scoped, or `{ auto: true }`) are the composition mechanism for setup/
teardown [Source: playwright.dev/docs/test-fixtures]. Beyond browser E2E,
`APIRequestContext` covers server-only API testing as a first-class mode
[Source: playwright.dev/docs/api-testing]. Deep test-layer-selection method
(when E2E/visual/component is the right layer at all) is owned by
[testing-strategy](../testing-strategy/SKILL.md); role-based-locator
accessibility framing is owned by
[web-accessibility](../web-accessibility/SKILL.md). For unit/mocking/
snapshot testing outside the browser, see the related
[jest-vitest](../jest-vitest/SKILL.md) technology skill — note that
Vitest's Browser Mode uses Playwright as a provider, a genuine documented
relationship between the two skills.

## Failure handling

- If no browser-automation capability and no MCP browser server is
  available, degrade to advisory-only: write/review Playwright test code
  and config without executing it, and state that explicitly rather than
  claiming a run occurred.
- If the Playwright version in use can't be determined, ask for it or
  state the version range (`>=1.60 <=1.63`) this guidance assumes; never
  assume "latest" silently.
- If a request needs test-layer-selection method or role-locator a11y
  framing, defer to testing-strategy/web-accessibility rather than
  restating their content.

## Escalation

**Tier-C capability fallback.** This skill requires `browser` as a
non-universal capability (Tier C — per the taxonomy, browser automation is
not universal across agents). When a direct browser-automation primitive
isn't available in the current environment, fall back to Playwright-via-
MCP (accessibility-tree-based browser control, e.g. on Claude Code) for
actually driving the browser. When neither a direct browser capability nor
an MCP browser server is available at all, degrade to advisory-only test
authoring — produce/review Playwright test code and config without
executing it, and say so explicitly rather than implying a run happened.

Additionally: running Chromium as root against untrusted content disables
the OS-level sandbox — flag this and recommend the documented non-root +
seccomp hardening before proceeding. A `storageState` file staged for
commit is flagged before proceeding, since it can carry live,
impersonation-capable session credentials.

## Outputs & verification

- **Outputs:** Playwright test code (E2E, API-only, component, or visual-
  regression) using fixtures and web-first assertions; `playwright.config.ts`
  or Docker deployment changes; analysis with version-tagged rationale.
- **Verify:** assertions are web-first/auto-retrying, not manually
  re-checked booleans; auth/state isolation matches the storageState-reuse
  or per-worker-account pattern where the suite mutates server state; any
  Docker deployment pins the image tag to the exact installed Playwright
  version; every version-tagged claim carries its applicable range.

## References

- [research/technologies/playwright.md](../../research/technologies/playwright.md) — primary source for all claims in this skill.
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md) — Playwright version-grounding table (§ Playwright).
- [testing-strategy](../testing-strategy/SKILL.md) — test-layer selection method (parent).
- [web-accessibility](../web-accessibility/SKILL.md) — role-based-locator a11y framing and MCP accessibility-tree integration (parent).
- [jest-vitest](../jest-vitest/SKILL.md) — related unit/component testing; Vitest Browser Mode uses Playwright as a provider.
