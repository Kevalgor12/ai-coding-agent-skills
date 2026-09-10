---
name: Fastify
description: >-
  Fastify-specific plugin system (register()/encapsulation), schema-driven
  validation/serialization (Ajv + fast-json-stringify), decorators
  (decorate/decorateRequest/decorateReply), the fixed request lifecycle/hooks,
  and the v4-to-v5 breaking changes. Use when fastify appears in
  package.json/imports or the task names Fastify specifically. Not for the
  Fastify-vs-Express choice itself (backend-architecture), generic HTTP
  contract design (api-design), or Node.js runtime mechanics (nodejs).
spec_version: "1.0"
---

## Purpose & scope

Apply Fastify correctly for the version in use: the plugin/encapsulation
system, schema-driven validation and serialization, decorators, the fixed
request lifecycle, and the documented v4-to-v5 breaking changes. The
Fastify-vs-Express *decision* and the generic backend-structure method
(layering, DI, graceful shutdown) belong to
[backend-architecture](../backend-architecture/SKILL.md) (`SK-BE-001`); the
generic HTTP/REST contract belongs to [api-design](../api-design/SKILL.md)
(`SK-BE-002`). This skill supplies the Fastify-specific implementation depth
underneath those decisions.

## When to use / When not to use

**Use** when `fastify` appears in `package.json`/an import, or the task names
a Fastify-specific mechanism (`register`, `decorate`, `addHook`,
`fastify.inject`, a `@fastify/*` plugin). **Do not use** for the
Fastify-vs-Express choice itself (route to `backend-architecture`), generic
HTTP contract design with no Fastify mechanism in question (route to
`api-design`), a different Node framework (route to that skill), or pure
Node.js runtime/event-loop questions with no Fastify API involved (route to
`nodejs`, `SK-TECH-nodejs`).

## Knowledge

**Plugin system and encapsulation.** Every `fastify.register(plugin, [opts])`
call creates a new child scope by default, forming a hierarchical (documented
as a directed acyclic graph) tree of **encapsulation contexts**: decorators,
hooks, and routes registered in a scope are visible to that scope and its
descendants only — not to siblings or ancestors [Source:
fastify.dev/docs/latest/Reference/Encapsulation/]. `register()` accepts
`prefix`, `logLevel`, and `logSerializers` at the register call, plus the full
options object passed through to the plugin itself [Source:
fastify.dev/docs/latest/Reference/Plugins/]. To deliberately **break**
encapsulation — making a plugin's decorators/hooks visible to its *parent*
scope — wrap it with `fastify-plugin`, or set `Symbol.for('skip-override')` on
the plugin function directly (the docs note the latter requires manually
maintaining compatibility) [Source:
fastify.dev/docs/latest/Reference/Plugins/]. `onRegister` fires before a
plugin's code executes, within its own encapsulated context [Source:
fastify.dev/docs/latest/Reference/Hooks/].

**Schema-driven validation/serialization.** Fastify compiles JSON Schemas
into specialized functions ahead of request handling rather than
interpreting them per request: **Ajv v8** compiles `querystring`/`params`/
`body`/`headers` schemas for validation, **fast-json-stringify** compiles
`response` schemas for serialization [Source:
fastify.dev/docs/latest/Reference/Validation-and-Serialization/]. Schemas can
be registered once and reused across routes via `fastify.addSchema()` to
avoid recompiling duplicates. `ajv` accepts `customOptions`/`plugins` for
tuning (e.g., `coerceTypes`); keep `allErrors` disabled unless the app
genuinely needs detailed per-field validation feedback — enabling it is a
documented performance cost [Source:
fastify.dev/docs/latest/Guides/Recommendations/]. **As of v5, full JSON
Schema is required** for these four schema slots — the `jsonShortHand`
convenience option was removed, so every schema needs an explicit `type` and
complete object shape (v4→v5, breaking) [Source:
fastify.dev/docs/latest/Guides/Migration-Guide-V5/].

**Decoration API.** `fastify.decorate(name, value, [deps])`,
`decorateRequest(name, value, [deps])`, and `decorateReply(name, value,
[deps])` attach reusable properties/functions to the instance, `Request`, or
`Reply`. The API is **synchronous only** by design: "Defining a decoration
asynchronously could result in the Fastify instance booting before the
decoration completes" [Source:
fastify.dev/docs/latest/Reference/Decorators/]. Reference-type values
(Array/Object) are **rejected outright** for Request/Reply decorators,
because a shared reference would leak mutation across requests — initialize
per-request object state in an `onRequest` hook instead, or use a
getter/setter [Source: fastify.dev/docs/latest/Reference/Decorators/]. For
performance, initialize a decorator with a value of the *shape* it will
eventually hold (e.g. `''` for a string, `null` as an object placeholder) so
the JS engine can optimize the object shape [Source:
fastify.dev/docs/latest/Reference/Decorators/].

**Fixed request lifecycle.** Every request flows through a defined hook
order: routing → `onRequest` → `preParsing` → body parsing →
`preValidation` → schema validation → `preHandler` → user handler →
`preSerialization` (skipped for string/buffer/stream/null payloads) →
`onSend` → response sent → `onResponse`, with `onError`, `onTimeout` (fires
on `connectionTimeout`), and `onRequestAbort` (client aborts mid-request) as
exception paths [Source: fastify.dev/docs/latest/Reference/Lifecycle/,
fastify.dev/docs/latest/Reference/Hooks/]. All hooks except `onClose` are
encapsulated (scoped) like everything else in the plugin tree. Calling
`reply.hijack()` at any point stops Fastify from running subsequent hooks or
auto-sending the response, handing full control to application code [Source:
fastify.dev/docs/latest/Reference/Lifecycle/] — as of **v5**, `reply.sent`
can no longer be mutated directly to achieve the same effect; `hijack()` is
now the only path [Source:
fastify.dev/docs/latest/Guides/Migration-Guide-V5/].

## Decision framework

1. **v6-alpha vs. stable v5 — which to build on?** v6 is pre-release
   (`6.0.0-alpha.0` through `alpha.3` as of the source research) and not yet
   suitable as production guidance [Source:
   fastify.dev/docs/latest/Reference/LTS/; GitHub releases]. Default to
   stable v5 for anything shipping to production. Track v6-alpha only if
   deliberately previewing upcoming breaking changes in a throwaway branch —
   and even then, treat its exact new Node.js floor as **Unresolved** (see
   Failure handling) rather than asserting a number.
2. **Plugin-based architecture vs. a flatter structure?** Fastify's
   encapsulation model rewards splitting a service into self-contained
   plugins (each owning its own routes/decorators/hooks) when the service has
   genuinely separable concerns (e.g. per-domain modules, a shared
   `@fastify/*` DB plugin per module). For a small service with one cohesive
   concern, a flat single-file or few-file structure is simpler and avoids
   the ceremony of `fastify-plugin`/`skip-override` boundary management —
   don't introduce plugin boundaries before there's more than one concern to
   separate.
3. **Break encapsulation (`fastify-plugin`) or keep it?** Keep the default
   (encapsulated) unless a plugin's decorators/hooks genuinely need to reach
   the parent scope (e.g. a shared logger/DB decorator every route needs).
   Reaching for `fastify-plugin` by default defeats the isolation the
   architecture is designed to provide.
4. **Response schemas: always, or only sometimes?** Define them wherever a
   route returns data with any field that shouldn't be exposed, or wherever
   throughput matters — the schema doubles as validation-of-output and a
   performance win. For a trivial internal route with a known-small,
   non-sensitive payload, skipping a response schema is a reasonable
   simplification, not a violation.

## Workflow

1. Confirm the installed Fastify major (v4/v5/v6-alpha) from
   `package.json`/lockfile before writing any version-sensitive code.
2. Design the plugin/encapsulation boundary for the feature: does it need its
   own scope, or does it belong in an existing one?
3. Define request/response JSON Schemas for the route(s) involved.
4. Wire any needed decorators (instance/request/reply) and hooks, respecting
   the fixed lifecycle order.
5. Set or confirm a `setErrorHandler` that sanitizes `>=500` errors (see
   Security) before the route ships.
6. Verify with `fastify.inject()` (see Testing).

## Engineering rules

- Determine the installed major version before using any v5-only API
  (`loggerInstance`, full-schema requirement, `Object.hasOwn()` on route
  params) — don't assume "latest" silently.
- Don't decorate `Request`/`Reply` with an Array/Object value directly; use
  an `onRequest` hook or a getter/setter for per-request object state.
- Don't mix async and callback styles within one plugin function — as of v5
  this is a hard error, not just a lint warning (`FSTWRN003`) [Source:
  fastify.dev/docs/latest/Reference/Warnings/,
  fastify.dev/docs/latest/Guides/Migration-Guide-V5/].
- Reach for `fastify-plugin` only when a plugin's decorators/hooks must be
  visible to the parent scope — not as a default habit.
- Register a `setErrorHandler` before any route can return a `>=500` error to
  a client (see Security).

## Anti-patterns

- **Wrapping every plugin in `fastify-plugin` "just in case."** This defeats
  the encapsulation model's isolation guarantees and makes it unclear which
  decorators/hooks are actually scoped — the domain's over-engineering trap
  (building a flatter, unencapsulated app in disguise while still paying
  plugin-registration overhead).
- **Decorating Request/Reply with a shared Array/Object** to hold per-request
  state — Fastify rejects this outright because the mutation would leak
  across concurrent requests [Source:
  fastify.dev/docs/latest/Reference/Decorators/].
- **Skipping response schemas on routes returning sensitive data**, relying
  on the handler to manually omit fields — loses both the serialization
  speedup and the "prevent accidental disclosure" property schemas provide
  [Source: fastify.dev/docs/latest/Reference/Validation-and-Serialization/].
- **Using generic Express/Connect-style middleware on hot paths** via
  `@fastify/express`/`@fastify/middie` instead of native hooks/plugins —
  middleware operates on the raw Node req/res, cannot call
  `reply.send()`/other Fastify-specific methods, and can't match
  parameterized or multi-segment wildcard paths the way native routes can
  [Source: fastify.dev/docs/latest/Reference/Middleware/].
- **Leaving Ajv's `allErrors: true` enabled by default** — a documented
  performance cost, not a security concern; enable it only when detailed
  per-field validation feedback is actually needed [Source:
  fastify.dev/docs/latest/Guides/Recommendations/].

## Security

Backend-architecture already notes that prototype-pollution protection is
on by default and that the default error handler forwards messages verbatim.
This section adds the concrete mechanics.

**Prototype-pollution knobs.** `onProtoPoisoning` and `onConstructorPoisoning`
both default to `'error'`, rejecting any JSON body containing `__proto__` or
`constructor` keys; each accepts `'error' | 'remove' | 'ignore'` if an
application has a documented reason to relax it [Source:
fastify.dev/docs/latest/Reference/Server/]. As of **v5**, the internal route
`parameters` object no longer inherits from `Object.prototype` at all,
closing a second surface — application code should switch to
`Object.hasOwn()` instead of `.hasOwnProperty()` when checking param keys
[Source: fastify.dev/docs/latest/Guides/Migration-Guide-V5/]. Relaxing either
option to `'ignore'` should be treated as a deliberate, reviewed exception,
not a default.

**Error-message leakage and `setErrorHandler`.** By default, Fastify
serializes errors to JSON (`statusCode`, `error`, `message`, optional `code`)
and does **not** vary this by environment — "error messages are forwarded
verbatim to clients" [Source: fastify.dev/docs/latest/Reference/Errors/].
Concretely, this means an unhandled DB-driver error reaching the client can
leak schema/query detail. Install a custom handler:

```javascript
fastify.setErrorHandler((error, request, reply) => {
  if (error.statusCode && error.statusCode < 500) {
    reply.send(error) // deliberate 4xx / FST_ERR_VALIDATION — safe to pass through
  } else {
    request.log.error(error)
    reply.code(500).send({ statusCode: 500, error: 'Internal Server Error' })
  }
})
```

[Source: fastify.dev/docs/latest/Reference/Errors/]. `allowErrorHandlerOverride`
(default `true`) governs whether `setErrorHandler` can be called more than
once in the same scope; doing so anyway is flagged by `FSTWRN004` as a
possible source of subtle bugs [Source:
fastify.dev/docs/latest/Reference/Warnings/]. Cross-cutting threat modeling
beyond these two Fastify-specific mechanisms is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md), not restated
here.

## Performance

Backend-architecture already covers the vendor-benchmark caveat — it is not
repeated here; do not cite a specific req/s figure as a settled ranking.
What's Fastify-specific: both Ajv (validation) and fast-json-stringify
(serialization) **compile** schemas into specialized functions ahead of
request handling rather than interpreting them at runtime, and schemas can be
deduplicated via `addSchema()` [Source:
fastify.dev/docs/latest/Reference/Validation-and-Serialization/]. Route
matching is faster for static/simple parametric routes than regex-based
ones; version constraints and async custom constraints both measurably
degrade routing performance and should be used judiciously [Source:
fastify.dev/docs/latest/Guides/Recommendations/]. Decorators should be
initialized with a placeholder of the correct type/shape (not `undefined`)
so the JS engine can optimize the resulting object shape [Source:
fastify.dev/docs/latest/Reference/Decorators/].

## Testing

Backend-architecture already notes `fastify.inject()` at a high level; this
is the concrete usage. `fastify.inject(options)`, built on
`light-my-request`, simulates an HTTP request **in-process with no real
socket**, and guarantees every registered plugin has finished booting before
the assertion runs [Source: fastify.dev/docs/latest/Guides/Testing/]:

```javascript
const response = await app.inject({ method: 'GET', url: '/' })
```

It accepts arbitrary methods, query params, payloads, headers, and cookies,
in both callback and async/await styles. `fastify.ready()` fully boots the
app (runs all plugin/boot logic) without binding a listening socket, useful
when a test needs a booted instance but not `inject()`'s request simulation.
Documented best practices: keep application-construction logic separate from
`listen()`/startup logic so a fresh app instance is easy to build per test;
always call `.close()` in teardown so DB connections and other external
resources are released; test a plugin in isolation by registering it into a
throwaway Fastify instance and exercising it via `.inject()` [Source:
fastify.dev/docs/latest/Guides/Testing/]. Deeper test-strategy method is
owned by [testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If the installed Fastify major cannot be determined, ask, or explicitly
  state the version the guidance assumes (default to stable v5 when truly
  unknown) — never silently assume "latest" (VA-3).
- If shell is unavailable, produce advisory route/plugin/schema code and
  state explicitly that `fastify.inject()` verification was not run.
- If asked about v6 specifics beyond what the source research confirms (in
  particular, its exact Node.js floor), say so explicitly rather than
  guessing a number — mark it Unresolved (see below).

## Escalation

- Upgrading a production service across the v4→v5 boundary touches Node.js
  runtime floor, logger configuration, and schema shape simultaneously —
  present the full breaking-change list (see References) and get explicit
  confirmation before applying it, rather than migrating unilaterally.

## Outputs & verification

- **Outputs:** version-correct route/plugin/schema/decorator/hook code; error
  handler and prototype-poisoning configuration; an analysis of which
  version-specific caveats apply.
- **Verify:** any version-sensitive API matches the confirmed installed
  major; a response schema exists wherever the route returns sensitive
  fields; a custom `setErrorHandler` exists before any route can leak
  `>=500` error detail; `fastify.inject()` exercises the change.

## References

- Source list: see `skill.yaml.source_references` (Fastify official docs,
  retrieved 2026-09-10, via `research/technologies/fastify.md`).
- [research/technologies/fastify.md](../../research/technologies/fastify.md) —
  full research pass, including the complete v4→v5 migration item list
  (§11/§13) and the Unresolved notes on the v6-alpha Node.js floor and
  canonical-docs-host cutover date.
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md) —
  Fastify row, Node.js runtime-floor cross-reference.
- [backend-architecture](../backend-architecture/SKILL.md) — the
  Fastify-vs-Express decision and generic backend-structure method.
- [api-design](../api-design/SKILL.md) — the generic HTTP/REST contract.

**Unresolved (carried from the source research, not guessed at here):**
the exact Node.js minimum for Fastify v6 is not confirmed — only that
`6.0.0-alpha.0` "raises the minimum Node.js version requirements" without a
stated number [Source: fastify.dev/docs/latest/Reference/LTS/; GitHub
releases]. Treat any specific v6 Node-floor number as unverified until the
stable release documents it.
