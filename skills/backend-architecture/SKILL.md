---
name: Backend architecture
description: >-
  Structure a backend service — layering, middleware/interceptor design,
  dependency injection, error handling, graceful shutdown — and choose a
  runtime/framework when that choice is open. Use when building or
  structuring a backend service. Not for the HTTP/GraphQL contract itself, or
  for the data layer.
spec_version: "1.0"
---

## Purpose & scope

Structure how a backend service is put together — layers, middleware,
dependency injection, error handling, and shutdown — and choose the
runtime/framework when that's still open. This skill decides *how the
service is organized*; it does not decide the HTTP/GraphQL contract itself
([api-design](../api-design/SKILL.md) /
[graphql-api-design](../graphql-api-design/SKILL.md)) or the data layer
([data-modeling](../data-modeling/SKILL.md)).

## When to use / When not to use

**Use** when building or structuring a backend service, or when a runtime/
framework choice is genuinely open. **Do not use** for frontend-only work,
for the HTTP/GraphQL contract once structure is settled, or for pure
data-modeling with no service-layer question.

## Knowledge

**Fastify and Express make different default trade-offs, not just different
syntax** [Source: technology-decision-matrix.md §3]. Fastify builds
schema-driven validation/serialization in as a core feature (Ajv + `fast-json-stringify`
compile schemas ahead of request handling, and the compiled response schema
doubles as a security control against accidental field disclosure) and
defaults to on-by-default prototype-pollution protection. Express has no
schema-enforcement mechanism and relies on app-level middleware (`helmet`,
`express-session`, `rate-limiter-flexible`) for equivalent hardening — but
Express's default error handler is environment-aware (full stack trace only
when `NODE_ENV` isn't `production`), while Fastify's default handler forwards
error messages verbatim to clients unless the app sets a custom
`setErrorHandler`. Neither is strictly "more secure" — they push different
responsibilities to the framework vs. the application.

**Vendor-published performance numbers are not independent benchmarks.**
Fastify's own homepage benchmark claims ~88,171 req/s vs. Express's ~57,936
(both self-run, "not independently reproduced" per the underlying research)
[Source: technology-decision-matrix.md §3]. Treat this as directional
marketing, not a verified ranking — don't cite "Fastify is 1.5x faster" as
settled fact.

**Testing story differs materially.** Fastify documents `fastify.inject()`
(built on `light-my-request`) — in-process request simulation with no real
socket, guaranteeing all plugins have booted before the test runs. Express
has **no official first-party testing guide**; `supertest` is
community-standard but not Express-org-maintained, so it's excluded from
this project's official-source citations [Source: technology-decision-matrix.md
§3]. This is a real, documented gap worth stating plainly rather than
assuming Express has first-party test tooling equivalent to Fastify's.

**Runtime choice is a separate axis from framework choice.** Node.js
(Express/Fastify), Go, and Python represent genuinely different
concurrency/deployment models — goroutines and explicit multi-value error
returns (Go) vs. an event-loop single-thread-plus-worker-pool model with
CommonJS/ESM module duality (Node.js) vs. a GIL-constrained interpreter with
process-based parallelism as the default escape hatch (Python, though
free-threaded builds are becoming officially supported as of 3.14 — see the
[python](../python/SKILL.md) skill for detail). None of this project's
research states a comparative performance ranking across these three
runtimes for equivalent workloads — don't manufacture one.

## Decision framework

1. **Is a runtime/framework already in place?** Work within it unless the
   user explicitly asks to evaluate a switch — switching backend
   runtimes is expensive and disruptive.
2. **Node.js vs. Go vs. Python — what does the team actually know, and what
   does the workload need?** CPU-bound, highly concurrent workloads often
   favor Go's goroutine model; teams already fluent in Python's ecosystem
   (esp. where the service overlaps with data/AI work) may reasonably prefer
   it despite the GIL; Node.js suits I/O-bound services and teams already
   invested in a JS/TS stack end-to-end. None of these is a universally
   correct default — pick based on the actual constraint, not habit.
3. **Within Node.js, Fastify vs. Express?** Want built-in schema validation/
   serialization as a first-class feature, explicit plugin/DI ergonomics, and
   an official in-process test primitive → Fastify. Want the largest
   ecosystem, maximal middleware compatibility, and don't need schema
   enforcement at the framework level → Express, with `helmet` and friends
   layered on for hardening.
4. **How should errors be handled?** Consistently, at one place in the
   layering (a central error-handling middleware/interceptor), not scattered
   per-route — and environment-aware (don't leak stack traces to production clients).
5. **Does shutdown release what it's holding?** In-flight requests should
   drain, connections should close, before the process exits — abrupt
   termination under load is a reliability bug waiting to happen.

## Workflow

1. Confirm whether a runtime/framework choice is open; if not, work within
   the existing one.
2. If open, apply the decision framework and record the trade-off, citing
   the Fastify/Express comparison where relevant.
3. Design layering: transport (routes/handlers) → business logic → data
   access, with no business logic living in the transport layer.
4. Design middleware/interceptor chain and dependency injection approach.
5. Design centralized, environment-aware error handling.
6. Design graceful shutdown (drain in-flight work, close connections).
7. Hand off the HTTP/GraphQL contract to api-design/graphql-api-design, and
   the data layer to data-modeling.

## Engineering rules

- Keep business logic out of the transport layer.
- Handle errors in one consistent place, environment-aware (no stack traces to production clients).
- Design for graceful shutdown from the start, not as an afterthought.
- Don't propose a runtime/framework switch unasked.
- Don't cite a vendor's self-published benchmark as an independent, settled performance ranking.

## Trade-offs

Fastify's schema-driven validation/serialization buys built-in security and
performance guarantees at the cost of a smaller ecosystem than Express's.
Express's larger ecosystem and looser structure buy flexibility at the cost
of needing more app-level hardening decisions made explicitly. Go's explicit
error handling and goroutines buy predictable concurrency at the cost of more
verbose control flow than exception-based languages. Python's ecosystem
breadth (especially for AI/data-adjacent services) trades against the GIL's
CPU-bound-concurrency ceiling, though free-threaded builds are changing this
(see the python skill for the current state).

## Anti-patterns

- **Scattering error handling per-route** instead of centralizing it — the
  domain's most common structural drift.
- **Business logic embedded in route handlers/middleware**, making it
  untestable without spinning up the whole HTTP layer.
- **No graceful shutdown** — killing the process without draining in-flight requests.
- **Treating a vendor benchmark as an independent performance verdict.**
- **Switching runtimes/frameworks opportunistically** rather than for a stated reason.
- **Building a plugin/middleware abstraction layer before more than one framework is actually in play** — the domain's overengineering trap.

## Security

Fastify's default error handler forwards messages verbatim to clients
(potentially leaking schema/query detail) unless a custom `setErrorHandler`
is set; Express's default handler is environment-aware by default. Express
has named, patched CVEs worth knowing (CVE-2024-43796, XSS in `res.redirect`;
CVE-2024-29041, open-redirect in `res.location`/`res.redirect`) [Source:
technology-decision-matrix.md §3]; verify a patched version is in use rather
than assuming an old pin is safe. Deep threat modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Fastify compiles validation/serialization schemas ahead of request handling
rather than interpreting them per-request; Express's own docs recommend
`NODE_ENV=production` for template/view caching, citing roughly 3x
improvement from their own benchmarks [Source: technology-decision-matrix.md
§3]. Both frameworks document running behind a reverse proxy in production —
Fastify's own docs call running it directly on the internet "an anti-pattern
and extremely bad practice." Deep performance method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

Fastify: `fastify.inject()`, in-process, no real socket, all plugins
guaranteed booted. Express: no official first-party testing guide exists;
community tooling (`supertest`) is the de facto standard but not officially
maintained by the Express org [Source: technology-decision-matrix.md §3].
Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If requirements are too thin to support a runtime/framework decision,
  request them or hand off to requirements-engineering.
- If a service already has a runtime/framework, work within it unless a switch is explicitly requested.

## Escalation

- A runtime/framework switch for an existing production service is a
  significant, hard-to-reverse decision — presented with trade-offs for
  explicit confirmation, never applied unilaterally.

## Outputs & verification

- **Outputs:** a runtime/framework recommendation with trade-offs (when
  open), and a service structure (layering, middleware, DI, error handling,
  shutdown).
- **Verify:** errors are handled consistently and environment-aware; shutdown
  drains held resources; any framework recommendation cites real,
  research-backed differentiators.

## References

- [references/nodejs-go-python-comparison.md](references/nodejs-go-python-comparison.md) — Tier-2 runtime comparison notes.
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
