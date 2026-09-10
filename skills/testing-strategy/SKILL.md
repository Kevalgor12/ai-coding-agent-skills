---
name: Testing strategy
description: >-
  Decide what to test at which layer (unit/integration/e2e/component/
  visual/contract/load), design test data and fixture isolation, and
  structure a suite accordingly. Use when writing tests, deciding test
  strategy, or a change needs coverage. Tool specifics come from
  jest-vitest/playwright. Not for manual QA process or test-case
  management, which this library hasn't researched.
spec_version: "1.0"
---

## Purpose & scope

Decide which test layer(s) a given risk actually needs, and structure the
resulting suite — tool-neutral, with implementation depth specialized by
[jest-vitest](../jest-vitest/SKILL.md) (unit/component/snapshot) and
[playwright](../playwright/SKILL.md) (E2E/browser/visual/API). Test data
and fixture isolation are covered here as part of structure, not as a
separate concern. **Manual QA process and test-case-management workflow
are explicitly out of scope** — this library's research spans automated-
testing methodology across 44 technologies, with no independent grounding
for manual-testing process; a request for that depth gets stated as a gap,
not answered from general knowledge.

## When to use / When not to use

**Use** when writing tests, deciding test strategy for a project, or
reviewing an existing suite's layer distribution/isolation/fixture design.
**Do not use** for explicitly throwaway code the user has said doesn't
need tests, or for manual QA process/test-case management.

## Knowledge

**The test pyramid isn't a researched universal law in this library's
data — it's a working framework for organizing what *is* documented, layer
by layer.** What the research actually shows is highly uneven, real
first-party guidance per layer across 44 technologies:

- **Unit testing**: Jest and Vitest both ship self-contained mocking/
  snapshot/fake-timer tooling with no separate library required
  [Source: jestjs.io/docs/mock-functions; vitest.dev/guide/features.html].
  Go's `testing` package and table-driven tests via `t.Run` is the
  documented idiom [Source: pkg.go.dev/testing]. Python's stdlib
  `unittest` is official; **pytest is explicitly out of scope for
  docs.python.org** despite being the de facto ecosystem standard
  [Source: python.md §9] — a real, easy-to-miss gap between "official"
  and "actually used."
- **Integration testing**: Docker's Testcontainers pattern (real dependency
  containers, not mocks, torn down regardless of outcome) is the shared
  mechanism underneath several technologies' own integration-testing
  stories (OpenSearch's official `opensearch-testcontainers` module;
  ClickHouse's own Docker-based multi-container tests)
  [Source: docs.docker.com/testcontainers/]. Drizzle's PGlite ("Postgres
  in WASM," zero external dependency) and Prisma's real-database
  integration-testing guide are the two ORMs in this dataset with an
  actual first-party integration-testing story.
- **E2E/browser testing**: Playwright is the *de facto shared
  browser-automation backend* underneath several higher-level test
  runners in this dataset, not just a standalone tool — Vitest's Browser
  Mode uses it as a provider, Angular offers it alongside its default
  Vitest setup, and Nuxt/Next.js/Vue all name it as their E2E
  recommendation [Synthesis, testing-knowledge-map.md §3].
- **Component testing**: framework-specific — Playwright's `fixtures.mount()`
  (React/Vue, stable), Vitest's Browser Mode (Vue/React/Svelte/Lit/Marko),
  React's `@testing-library/react` as the official replacement for the now-
  **deprecated** `react-test-renderer` [Source: react.dev/warnings/
  react-test-renderer].
- **Visual/snapshot regression**: a real, documented tension exists here —
  MUI explicitly *discourages* snapshot testing for app developers while
  using visual regression (Argos CI) internally itself; Vue likewise
  recommends against relying exclusively on snapshots
  [Synthesis, testing-knowledge-map.md §5]. Treat DOM/JSON snapshot
  testing and true pixel-level visual regression as two different things
  colloquially both called "snapshot testing" — they have different value.
- **Load/performance testing**: `redis-benchmark`, OpenSearch Benchmark,
  ClickHouse's hardware performance-test script, and Vitest's Tinybench-
  powered `bench()` are each technology's own first-party tool — there's
  no cross-technology load-testing standard documented in this dataset.
- **Contract/conformance testing**: OpenAPI's own best-practice guidance
  recommends wiring the spec itself into CI as a contract-testing source
  of truth [Source: learn.openapis.org/best-practices.html]; ECMAScript's
  Test262 suite is load-bearing for TC39 Stage 4 entry itself, not just
  advisory.

**A substantial number of technologies in this library's research have NO
first-party testing methodology documented at all** — this is a real,
recurring finding, not a research gap on this project's part. PostgreSQL,
MySQL, Redis, TypeORM, Express, TypeScript, GraphQL, and several others
explicitly lack an official "how to test your app against me" guide
[Source: testing-knowledge-map.md — Notable Gaps]. **A synthesis worth
internalizing**: an application built on Postgres/MySQL/Redis via TypeORM
specifically would have *zero* official first-party testing documentation
at any layer of that stack — only Drizzle (PGlite) and Prisma
(Jest + jest-mock-extended) break this pattern among the ORMs this library
researched. State this gap plainly when it applies rather than inventing
an official-sounding methodology that doesn't exist.

**Different ORMs document genuinely different testing philosophies, not
just different tool preferences** [Synthesis, technology-decision-
matrix.md §1]: Mongoose explicitly steers users *away* from Jest ("We
strongly recommend using a different testing framework, like Mocha");
Prisma leans on mocking the client; Drizzle leans on running a real (if
embedded) database. A skill scaffolding "add tests for this ORM" cannot
use one universal setup script across all of them without checking which
ORM is actually in use first.

## Decision framework

1. **What's actually at risk in this change?** Data integrity, user-facing
   behavior, an integration boundary, and a pure internal calculation all
   warrant different layers — match the layer to the actual risk, not a
   reflexive default.
2. **Does the target technology have a documented first-party testing
   methodology?** If not (a real, common finding — see Knowledge above),
   say so and recommend ecosystem tooling (Testcontainers, community
   adapters) rather than presenting an invented methodology as official.
3. **Is this a pure logic/calculation with no external dependency?** Unit
   test it in isolation — the cheapest, fastest, most deterministic layer.
4. **Does this cross a real integration boundary** (a database, another
   service, a realtime transport)? Integration test against something real
   (or a documented in-process/embedded substitute like PGlite) rather than
   mocking the boundary away entirely.
5. **Is this user-facing behavior spanning multiple components/pages?**
   E2E, using whichever browser-automation tool the stack already uses.
6. **Would a snapshot test actually catch a meaningful regression, or just
   generate diff noise on every unrelated change?** If the latter, prefer a
   semantic (role-based) assertion or true visual regression over a raw
   DOM/JSON snapshot.
7. **Is test data isolated and torn down explicitly?** A test that leaves
   state behind for the next test to trip over is a determinism bug
   waiting to happen — design fixture setup/teardown deliberately, don't
   leave it implicit.

## Workflow

1. Identify what's actually at risk in the change.
2. Match risk to the appropriate layer(s) using the decision framework.
3. Check whether the target technology has a documented first-party
   testing methodology; state the gap if not.
4. Design test data/fixtures for isolation — explicit setup and teardown,
   no shared mutable state between tests, no order-dependence.
5. Write the tests, deferring tool-specific mechanics to
   [jest-vitest](../jest-vitest/SKILL.md) or
   [playwright](../playwright/SKILL.md) as appropriate.
6. Verify determinism — run the affected tests more than once mentally
   (or actually) to catch order-dependence or timing flakiness before
   calling the work done.

## Engineering rules

- Match test layer to actual risk; don't default to one layer for
  everything (no e2e-for-everything, no unit-testing-a-getter).
- State plainly when a technology has no documented first-party testing
  methodology, rather than inventing one.
- Design test data/fixture isolation explicitly — setup and teardown are
  part of the test, not an afterthought.
- Check an ORM/framework's own documented testing philosophy before
  scaffolding tests for it — they genuinely differ (Mongoose vs. Prisma
  vs. Drizzle), so one universal script doesn't fit all of them.
- Prefer semantic/role-based or true visual-regression assertions over
  raw DOM/JSON snapshots where the latter would just generate diff noise.

## Trade-offs

Unit tests are fast and deterministic but don't catch integration-boundary
bugs. Integration tests catch those bugs but run slower and need real (or
embedded) dependencies. E2E tests catch genuine user-facing regressions but
are the slowest and most brittle layer — overusing it for logic that a
unit test would catch just as well wastes CI time and adds flakiness
surface. Snapshot testing is cheap to write but can devolve into
low-value diff-approval noise if applied indiscriminately, as MUI's and
Vue's own documented caution reflects.

## Anti-patterns

- **E2E-testing everything** — the most expensive, slowest, most brittle
  layer used where a unit or integration test would catch the same bug for
  a fraction of the cost.
- **Unit-testing trivial getters/pure pass-throughs** — the inverse
  mistake, adding maintenance burden for zero real risk coverage.
- **Inventing an official testing methodology for a technology that
  documents none** — this library's research found this gap real and
  common (PostgreSQL, MySQL, Redis, TypeORM, Express, TypeScript,
  GraphQL, and more); say so instead.
- **Leaving test data/fixtures to leak between tests** — a silent
  determinism bug that manifests as intermittent, hard-to-reproduce
  failures.
- **Relying exclusively on snapshot tests** for behavior that a semantic
  assertion or true visual-regression check would verify more meaningfully
  — both MUI and Vue's own docs caution against this.

## Security

Test fixtures/data should never embed real secrets or production data;
Playwright's own documented caution about `storageState` files containing
live session cookies is a concrete instance of this general risk — keep
auth-state fixtures out of version control. Deep threat modeling is owned
by [security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Test-suite runtime is itself a real engineering cost — layer selection
(not over-relying on the slowest layer) is the primary lever this skill
owns; tool-specific performance mechanics (parallelization, watch-mode,
caching) belong to jest-vitest/playwright. Deep performance method is
owned by [performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

This skill *is* the testing-strategy method — see Knowledge and Decision
framework above for its own content. Tool-specific mechanics are owned by
[jest-vitest](../jest-vitest/SKILL.md) (unit/component/snapshot) and
[playwright](../playwright/SKILL.md) (E2E/browser/visual/API).

## Failure handling

- If the risk profile of a change isn't clear, ask what's actually at
  risk rather than defaulting to a blanket layer choice.
- If the target technology has no documented first-party testing
  methodology, state that gap explicitly and recommend ecosystem tooling
  rather than inventing an official-sounding methodology.

## Escalation

- A request for manual QA process or test-case-management workflow
  exceeds this skill's grounded scope — state that rather than improvising
  generic QA-process advice from outside this library's research.

## Outputs & verification

- **Outputs:** a test plan (which layer(s), and why) and the actual tests,
  structured for isolation and determinism.
- **Verify:** layer choice matches actual risk; tests are isolated and
  deterministic; test data/fixtures are explicitly set up and torn down.

## References

- [research/knowledge-maps/testing-knowledge-map.md](../../research/knowledge-maps/testing-knowledge-map.md)
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
