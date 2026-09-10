---
name: Jest & Vitest
description: >-
  Jest- and Vitest-specific mocking/spying, snapshot testing, fake timers,
  coverage providers, and the Jest-vs-Vitest choice, including version-gated
  breaking changes (Jest v27/v30, Vitest v3.2/v5.0). Use when the stack uses
  Jest or Vitest, or the task is choosing between them. Not for test-layer
  strategy (testing-strategy) or browser/E2E automation (playwright).
spec_version: "1.0"
---

## Purpose & scope

This is a **merged, choose-one skill**: Jest and Vitest are treated as one
technology skill, not two competitors, because Vitest is explicitly designed
as a Jest-compatible drop-in with a near-identical mocking/snapshot API
surface [Source: https://vitest.dev/guide/why.html] — the taxonomy's own
merge rationale (near-identical API, pick one per project). This skill
covers Jest- and Vitest-specific API mechanics, configuration, CLI, coverage
providers, and version-gated breaking changes, and specializes
[testing-strategy](../testing-strategy/SKILL.md), which already owns the
tech-neutral test-pyramid/layer-selection method, fixture-isolation
principles, and the snapshot-testing tension — none of that is repeated
here.

## When to use / When not to use

**Use** when the stack has Jest or Vitest as a dependency or config file
present, code imports Jest globals or Vitest's `vi`, or the task is choosing
between the two for a project. **Do not use** for deciding *which test
layer(s)* to write at all (testing-strategy owns that), for browser/E2E/
visual automation via Playwright with no Jest/Vitest unit layer in question
(route to [playwright](../playwright/SKILL.md)), or for other runners
(Mocha, AVA, `node:test`, pytest) with no Jest/Vitest involvement.

## Knowledge

**Mocking API surfaces (near-identical by design):**
- Jest: `jest.fn(implementation?)` creates a mock; every mock exposes
  `.mock.calls`/`.results`/`.instances`/`.contexts`/`.lastCall`.
  `jest.mock(moduleName, factory?)` mocks a whole module (automocked if no
  factory); `jest.requireActual()` retrieves the real module for partial
  mocking; `jest.spyOn(object, methodName)` wraps an existing method,
  restorable via `.mockRestore()` — no separate mocking library required
  [Source: https://jestjs.io/docs/mock-functions].
- Vitest: the `vi` helper (imported from `vitest`, or global when
  `globals: true`) exposes `vi.fn()`, `vi.mock()` (hoisted to file top),
  `vi.spyOn()`, `vi.stubGlobal()`, `vi.setSystemTime()`, `vi.stubEnv()` —
  Jest-compatible mocking positioned explicitly as an easy migration target
  [Source: https://vitest.dev/guide/mocking.html]. **New in v5.0**:
  `vi.when()` for conditional mocking with deep-equality/asymmetric-matcher
  argument matching, plus `toHaveBeenExhausted()` to verify all registered
  `vi.when()` behaviors were consumed [Source:
  https://vitest.dev/blog/vitest-5.html]. As of v5.0, `vi.mock()`/
  `vi.unmock()`/`vi.hoisted()` must sit at module scope, not inside
  functions/`describe` blocks — `vi.doMock()`/`vi.doUnmock()` remain usable
  elsewhere [Source: https://vitest.dev/guide/migration.html].
- A real semantic gap, not just a naming difference: Jest's module-mock
  factory return value is treated as the default export
  (`jest.mock('./path', () => 'hello')`), while Vitest requires an explicit
  export shape (`vi.mock('./path', () => ({ default: 'hello' }))`), and
  neither tool's `__mocks__`-directory auto-mocking behaves identically —
  Vitest requires an explicit `vi.mock()` call even with a `__mocks__` file
  present [Source: https://vitest.dev/guide/migration/jest.html].

**Snapshot testing:** both ship Jest-compatible snapshot testing
(`.toMatchSnapshot()` / `.toMatchInlineSnapshot()`) [Source:
https://jestjs.io/docs/snapshot-testing; https://vitest.dev/guide/why.html].
Jest's own guidance: treat snapshots as code (commit, review, keep short —
`eslint-plugin-jest`'s `no-large-snapshots` rule enforces this), and use
property matchers (e.g. `expect(user).toMatchSnapshot({createdAt:
expect.any(Date)})`) for legitimately-varying fields [Source:
https://jestjs.io/docs/snapshot-testing].

**`--ci` snapshot-write suppression (a real safety behavior):** in Jest's
`--ci` mode, new or mismatched snapshots are **not** auto-written — a
missing/mismatched snapshot fails the build instead, by design, so CI can't
silently accept drifted snapshots [Source:
https://jestjs.io/docs/cli].

**Fake timers:** Jest — `jest.useFakeTimers(options?)`,
`jest.runAllTimers()`, `jest.runOnlyPendingTimers()`,
`jest.advanceTimersByTime(ms)`; **new in v30**,
`jest.advanceTimersToNextFrame()` for `requestAnimationFrame` callbacks
[Source: https://jestjs.io/docs/timer-mocks]. Vitest — `vi.setSystemTime()`
for fake system time [Source: https://vitest.dev/guide/mocking.html]; **as
of v5.0**, Vitest's fake timers also mock the Temporal API via
`@sinonjs/fake-timers` v15.4 [Source:
https://vitest.dev/guide/migration.html].

**TypeScript integration — a real, meaningful distinction:** Jest's
TypeScript path is either Babel's preset (type-**stripping** only, no
type-checking) or the community package `ts-jest`, which performs actual
TypeScript **type-checking** during transformation [Source:
https://jestjs.io/docs/code-transformation]. Vitest instead offers **type
testing** via `expect-type` (`expectTypeOf`, `assertType`) to catch
TypeScript type regressions in the suite itself — genuinely distinct
tooling, not a like-for-like substitute for `ts-jest`'s build-time checking
[Source: https://vitest.dev/guide/features.html].

**Vitest-only differentiators:** in-source (Rust-style) testing via
`import.meta.vitest`, recommended for small unit-testable utility functions
and prototyping, not for components/E2E — test code must be stripped from
production bundles via bundler `define` replacement [Source:
https://vitest.dev/guide/in-source.html]. Browser Mode runs tests inside a
real browser via **Playwright** (recommended provider), WebdriverIO, or a
lightweight Preview provider — see [playwright](../playwright/SKILL.md) for
Playwright itself [Source: https://vitest.dev/guide/browser/].

**Coverage providers:** Jest supports `babel` (default) or `v8`
(`--coverageProvider`) [Source: https://jestjs.io/docs/configuration].
Vitest supports `v8` or `istanbul`; the V8 provider has no pre-transpile
step (faster, lower memory) and its report accuracy is "as good as with
Istanbul" **specifically since v3.2.0** — do not assume that parity held for
earlier V8-provider versions [Source:
https://vitest.dev/guide/coverage.html].

**Documentation gap worth knowing:** TypeScript's own official build-tools
integration page does not cover Jest, Mocha, Vitest, or Playwright at all —
only Babel/Browserify/Gulp/Webpack/Rollup/Vite/Grunt/Svelte/Jspm/MSBuild are
listed there, so TS-integration guidance for either runner has to come from
the runner's own docs, not TypeScript's [Source: testing-knowledge-map.md,
corroborating research/technologies/typescript.md].

## Decision framework

The choice is **Jest vs. Vitest for a given project**, and the strongest
signal is what the project's *other* official docs already say — this is
not a "Vitest is always better" story:

1. **Does the framework already in the stack have documented runner
   guidance?** This is the primary signal, and it points different ways for
   different stacks:
   - **Away from Jest, explicitly**: Mongoose's own docs state "We strongly
     recommend using a different testing framework, like Mocha" [Source:
     research/technologies/mongoose.md, corroborating
     https://mongoosejs.com/docs/jest.html].
   - **Toward Jest, explicitly**: Prisma officially recommends Jest (paired
     with `jest-mock-extended` for mocking the client) [Source:
     testing-knowledge-map.md, corroborating research/technologies/prisma.md].
   - **Toward Vitest**: Vue, Angular, and Nuxt all default to or recommend
     Vitest [Source: testing-knowledge-map.md §3; angular.dev per
     research/knowledge-maps/version-matrix.md — Vitest is Angular's default
     test runner for new CLI projects as of v21+, replacing Karma].
   - **No single recommendation**: Next.js documents *both* Jest and Vitest
     as official first-party options [Source: testing-knowledge-map.md §3].
   If the stack's own framework has a stated position, follow it rather than
   a personal default — a skill scaffolding tests cannot use one universal
   choice across all of them.
2. **Is TypeScript type-checking during test transformation itself a
   requirement** (not just running TS test files, but catching type errors
   as part of the test run)? `ts-jest` does this; Vitest does not — Vitest's
   `expect-type` catches type regressions written into the suite, which is
   a different guarantee. Neither is strictly better; pick based on which
   guarantee the project actually needs.
3. **Is the project already on Vite** (or would benefit from reusing
   `vite.config.*`, existing Vite plugins, and Vite's dev-server transform
   pipeline)? Vitest reuses that configuration directly, which is the reason
   migration from a Vite-based Jest setup to Vitest is easy [Source:
   https://vitest.dev/guide/why.html; https://vitest.dev/guide/migration/jest.html].
4. **Does the suite need in-browser component testing or true visual
   regression via a real browser engine?** Vitest's Browser Mode (via
   Playwright as a provider) is the more direct path; Jest has no
   first-party equivalent.
5. **Simplest/do-nothing option**: if a working Jest (or Vitest) suite
   already exists, is green, and nothing above points the other way, keep
   it — migrating a healthy suite for its own sake is not warranted by
   either tool's own documentation.

## Workflow

1. Identify the runner already in use (or confirm none exists yet) via
   `package.json` dependencies and config files (`jest.config.*`, `"jest"`
   key, `vitest.config.*`).
2. If choosing fresh, apply the decision framework above — check the
   stack's own framework docs first.
3. Confirm the pinned/target version against `covered_versions` below;
   flag any version-gated behavior change that applies (Jest v27/v30,
   Vitest v3.2/v5.0).
4. Write mocks/spies/fake-timers/snapshots using the runner's native API
   (do not translate Jest idioms into Vitest verbatim without checking the
   semantic differences noted in Knowledge — e.g. mock-factory export
   shape).
5. Configure coverage provider and thresholds appropriate to the runtime
   (V8 for speed, Istanbul/Babel where broader runtime compatibility or
   file-scoped instrumentation is needed).
6. For CI, confirm snapshot behavior is safe by default (Jest's `--ci` mode)
   and that the suite runs in single-pass mode, not watch mode.

## Engineering rules

- State which runner (and version) the guidance targets before making an
  API/config claim — Jest v27/v30 and Vitest v3.2/v5.0 changed defaults
  materially enough that untagged advice can be actively wrong.
- Check the project's own framework documentation for a stated runner
  preference before defaulting to either tool (Mongoose vs. Prisma vs.
  Vue/Angular/Nuxt vs. Next.js's dual support all differ).
- Use `ts-jest` when type-checking during the test run itself is required;
  don't assume Babel's TS preset provides the same guarantee — it only
  strips types.
- Run Jest in `--ci` mode in CI so snapshot drift fails the build instead of
  silently writing new snapshots.
- Treat Jest's mock-factory default-export convention and Vitest's explicit
  export-shape requirement as genuinely different, not a drop-in swap, when
  migrating `jest.mock()` calls to `vi.mock()`.

## Trade-offs

Jest's Babel-based TS preset is faster to set up but only strips types;
`ts-jest` adds real type-checking at the cost of slower transformation.
Vitest's reuse of `vite.config.*` avoids duplicated transform/config logic
when the app already builds with Vite, but offers less guidance for
non-Vite-based projects, where the Jest ecosystem's broader integration
guides (React, Vue, Angular, Express+Supertest, Next.js, NestJS, and more
[Source: https://jestjs.io/docs/testing-frameworks]) may be more directly
applicable. Vitest's V8 coverage provider is faster and lower-memory but its
accuracy parity with Istanbul is a v3.2.0+ claim specifically — pinning an
older Vitest keeps that trade-off unresolved.

## Anti-patterns

- **Using Jest against Mongoose despite Mongoose's own explicit
  discouragement** ("We strongly recommend using a different testing
  framework, like Mocha") — following a default instead of the stack's own
  documented guidance [Source: research/technologies/mongoose.md].
- **Relying on Vitest's V8-coverage-accuracy claim on a pre-3.2.0 Vitest** —
  the "as good as Istanbul" parity is version-gated, not a general property
  of the V8 provider [Source: https://vitest.dev/guide/coverage.html].
- **Hitting Jest v30's glob-matching behavior change unexpectedly** — v30
  bumped the `glob` dependency to v10 with stricter brace-expansion/extglob
  handling, which can silently change which files match a custom
  `testMatch`/`moduleNameMapper` pattern that worked under v29 [Source:
  https://jestjs.io/blog/2025/06/04/jest-30].
- **Translating `jest.mock()` calls to `vi.mock()` verbatim** without
  accounting for the differing mock-factory export-shape convention — a
  common source of "works in Jest, silently wrong in Vitest" migration bugs
  [Source: https://vitest.dev/guide/migration/jest.html].
- **Over-engineering trap**: reaching for a full runner migration (Jest to
  Vitest or vice versa) on a healthy, green suite with no framework-level
  signal pointing that way — the decision framework's do-nothing branch
  exists for exactly this case.

## Security

Beyond the general testing hygiene already owned by
[testing-strategy](../testing-strategy/SKILL.md) (never embed real secrets
in fixtures), the research surfaces one Vitest-specific trust-boundary
detail: Vitest's UI/API server binds to `localhost` only by default; if
`api.host` is set to anything else, Vitest defaults `allowWrite` and
`allowExec` to `false` as a protective measure, because `allowWrite` lets
anyone who can reach the API run arbitrary code on the machine and
`allowExec` controls test execution via the UI [Source:
https://vitest.dev/config/api.html]. Do not re-enable those flags on a
network-exposed host without understanding that implication. No comparable
Jest-specific security guidance beyond its vulnerability-disclosure policy
was found in the research; deeper threat modeling is owned by
`security-engineering`.

## Performance

Vitest ships **Tinybench**-powered benchmarking via `bench()`; **as of
v5.0**, `bench` was rewritten as a test-context fixture invoked inside
`test()` calls, giving benchmarks access to fixtures, hooks, retries, and
assertions (a breaking change from the pre-5.0 standalone `bench()` API)
[Source: https://vitest.dev/blog/vitest-5.html]. Jest has no equivalent
first-party benchmarking API — its performance levers are `maxWorkers`
(worker-process pool size), `--runInBand` (disable parallelism, for
debugging only), and the coverage-provider choice itself: `v8` has no
pre-transpile step, `babel` (default) does [Source:
https://jestjs.io/docs/cli; https://jestjs.io/docs/configuration]. Vitest
similarly trades pool choice (`forks` default for compatibility, `threads`
for speed, `vmThreads` for DOM-heavy suites) against native-module
compatibility risk [Source:
https://vitest.dev/guide/improving-performance.html]. Deeper cross-cutting
performance method is owned by `performance-engineering`.

## Testing

This skill's own "testing" content is the mocking/snapshot/fake-timer API
mechanics already covered in Knowledge above. One meta-concern worth
naming: when changing shared Jest/Vitest config (`moduleNameMapper`,
`testMatch`, coverage thresholds), verify the change against an actual
run rather than reasoning about glob patterns in the abstract — Jest v30's
glob-matching change (see Anti-patterns) is a concrete example of config
that looked correct but silently stopped matching intended files.

## Failure handling

- If neither the runner nor its version is known, ask, or state the
  `covered_versions` range the guidance assumes — Jest's v27/v30 defaults
  and Vitest's v3.2/v5.0 behavior differ materially enough to make
  "current" guidance wrong for an older pin.
- If the task is choosing a runner and the framework already in the stack
  has documented official guidance (Mongoose, Prisma, Vue, Angular, Nuxt,
  Next.js), surface that guidance rather than defaulting to a personal
  preference.
- If shell is unavailable, degrade to advisory test/config output and say
  the suite was not actually run.

## Escalation

None beyond the standard failure-handling above — this skill has no
destructive or production-impacting actions of its own to gate.

## Outputs & verification

- **Outputs:** test code (mocks/fixtures/config), a runner-choice
  recommendation with rationale, and migration notes when moving a suite
  between the two.
- **Verify:** every API/config/CLI claim traces to a cited source and the
  correct tool; every version-specific claim is tagged with its range;
  snapshot assertions are paired with deterministic setup (mocked
  clocks/IDs or property matchers), not asserted against non-deterministic
  output.

## References

- [research/technologies/jest.md](../../research/technologies/jest.md)
- [research/technologies/vitest.md](../../research/technologies/vitest.md)
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md)
- [research/knowledge-maps/testing-knowledge-map.md](../../research/knowledge-maps/testing-knowledge-map.md)
- [testing-strategy](../testing-strategy/SKILL.md) — parent skill (layer
  selection, fixture isolation, snapshot-testing tension)
- [playwright](../playwright/SKILL.md) — related skill (E2E/browser;
  Vitest's Browser Mode uses Playwright as a provider)
