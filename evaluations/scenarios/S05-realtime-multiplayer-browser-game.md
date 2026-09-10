# Scenario: S05 — realtime multiplayer browser game

**Category:** Multi-skill tasks
**Complexity:** project
**Risk level:** reversible-write (the build itself) → production (first deploy is a separately gated step)

## Task

> Build a realtime multiplayer browser game.

## Repository signals

- Empty/near-empty repository: no `package.json` (or an empty one with just a
  `name` field), no `src/`, no existing frontend or backend code, no test
  files, no CI config, no `Dockerfile`.
- No stack has been named or chosen anywhere in the request: no language,
  framework, rendering library, realtime transport, or datastore is
  specified. This is a genuine open-tech-choice greenfield task, not
  implementation within an already-fixed architecture.
- No existing auth system, no existing realtime channel, nothing to
  modernize or migrate.
- The request is exactly the routing architecture's own canonical broad
  example. `core/routing-architecture/README.md` states, as its
  under-activation illustration: *""Build a realtime multiplayer browser
  game" must reach requirements, architecture, frontend, Three.js, realtime
  transport, backend, database, testing, security, and performance."*
  `core/routing-architecture/examples.md` Example 2 already works this
  request through the twelve determinations and a selected/excluded set.
  This scenario formalizes that same request into the evaluation suite's
  scenario schema so it is gradable against the six-status return-envelope
  contract, not just narratively described.
