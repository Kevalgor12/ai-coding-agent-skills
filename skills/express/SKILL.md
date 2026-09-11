---
name: Express
description: >-
  Express-specific middleware pipeline, routing API (app/router/request/response
  objects), and the 4.x-vs-5.x path-to-regexp route-syntax break. Use when the
  stack is Express (require/import express, express.Router(), app.listen) or
  the task names Express specifically. Not for generic backend structuring
  (backend-architecture), the Fastify-vs-Express framework choice (already
  covered there), or other Node frameworks (Fastify, Koa, Hapi).
spec_version: "1.0"
---

## Purpose & scope

Apply Express correctly and version-appropriately: the middleware pipeline,
the routing API, error handling, and the 4.x/5.x route-syntax break. The
generic backend-structuring method (layering, DI, graceful shutdown) comes
from [backend-architecture](../backend-architecture/SKILL.md); the HTTP
contract method (resources, status codes, pagination) comes from
[api-design](../api-design/SKILL.md); the Fastify-vs-Express framework
comparison is already owned by backend-architecture and is **not** repeated
here. This skill runs on Node.js — for event-loop/runtime specifics beneath
Express, see the Node.js skill (`SK-TECH-nodejs`).

## When to use / When not to use

**Use** when the stack is Express (`require`/`import express`, `app.listen`,
`express.Router()`, `express` in `package.json`) or the task names Express
specifically (adding middleware, fixing routing/error handling, migrating
4.x→5.x, hardening an Express app). **Do not use** when no framework is
chosen yet (route to `backend-architecture`), when the Fastify-vs-Express
choice itself is what's being made (already handled there), or when the
stack is Fastify, Koa, Hapi, or a non-Node runtime.

## Knowledge

**The middleware pipeline is Express's central request-handling model.**
Every request passes through an ordered stack of middleware bound via
`app.use()`/`app.METHOD()` (application-level) or `router.use()`/
`router.METHOD()` (router-level); each function receives `(req, res, next)`
and must either end the response or call `next()` — one that does neither
hangs the request. [Source: https://expressjs.com/en/guide/writing-middleware.html,
https://expressjs.com/en/guide/using-middleware.html] Express recognizes five
middleware categories: application-level, router-level, error-handling
(4-argument `(err, req, res, next)`), built-in (`express.static/json/
urlencoded/raw/text`), and third-party. [Source: https://expressjs.com/en/guide/using-middleware.html]
Registration order is execution order, and error-handling middleware must be
registered *last* to catch errors from everything above it. [Source:
https://expressjs.com/en/guide/error-handling.html]

**Routing API.** `app.METHOD(path, ...cb)` covers every HTTP verb Express
recognizes, including non-standard ones (`checkout`, `merge`, `purge`,
`query`); `express.Router(options)` (`caseSensitive`, `mergeParams`, `strict`)
creates a mountable "mini-application" attached via `app.use(path, router)`,
which strips the mount path from what the sub-router sees. `app.route(path)`/
`router.route(path)` return a chainable `Route` for defining multiple verbs
on one path. An Express app can itself be mounted as middleware inside a
parent app (`app.use('/admin', subApp)`), firing a `mount` event. [Source:
https://expressjs.com/en/5x/api/application.html, https://expressjs.com/en/5x/api/router.html]
`app.query(path, callback)` (routes the HTTP `QUERY` method) needs Node.js
>=20.19.3 or >=22.2.0 — stricter than Express 5.x's own Node.js >=18 floor.
[Source: https://expressjs.com/en/5x/api/application.html] [Version-sensitive: 5.x only]

**The 4.x→5.x route-syntax break (path-to-regexp).** Express 5.x's route
matcher runs on a newer `path-to-regexp`: wildcards must be named (`*splat`
or `{*splat}`, not bare `/*`), optional segments use brace syntax
(`{.:ext}`, `{/:id}`), multiple path alternatives are arrays instead of
`[a|b]` character-class syntax, and more characters (`()[]?+!`) must be
escaped. [Source: https://expressjs.com/en/guide/routing.html,
https://expressjs.com/en/guide/migrating-5.html] [Version-sensitive: 5.x
only — a genuine breaking change for any 4.x app with non-trivial route
patterns] Official codemods exist (`npx codemod@latest
@expressjs/v5-migration-recipe`, plus per-change codemods) rather than
requiring hand-porting every route. [Source: https://expressjs.com/en/guide/migrating-5.html]
Full before/after table: [`references/route-syntax-migration.md`](references/route-syntax-migration.md).

Alongside the route-syntax change, 5.x also flips `express.urlencoded()`'s
`extended` default to `false` (was `true`), leaves `req.body` `undefined`
(not `{}`) when unparsed, makes `req.query` a read-only getter with default
parser `"simple"` (was `"extended"`), and auto-forwards rejected/thrown
`async` errors to `next(err)` (no more `.catch(next)` boilerplate). [Source:
https://expressjs.com/en/guide/migrating-5.html] [Version-sensitive: 5.x only]

**Node.js floors are version-line-specific, not one Express-wide number:**
5.x requires Node.js >=18; 4.x requires Node.js >=0.10; 3.x (EOL 2015)
required Node.js >=0.8.0; 2.x (EOL 2012) required Node.js >=0.4.1. [Source:
https://expressjs.com/en/support/] Both 4.x and 5.x are simultaneously live:
npm's `latest` dist-tag is 5.2.1 (2025-12-01) and `latest-4` is 4.22.2
(2026-05-11) — 4.x keeps receiving patches after 5.x became the npm default.
[Source: research/technologies/express.md §12, npm registry] Native
execution of `.ts` files (`node src/app.ts`, no build step) needs Node.js
>=22.18.0 (or >=23.6.0 on v23) with TypeScript >=5.8 — a Node.js
type-stripping capability, not an Express feature, so it applies regardless
of the Express major version. [Source: https://expressjs.com/en/starter/installing.html]

## Decision framework

1. **New project, Express already chosen — which major line?** 5.x is the
   current npm default and reduces a class of silent bugs (auto async-error
   forwarding, `undefined` `req.body` instead of a misleadingly-populated
   `{}`), but 4.x is not legacy — it's still actively patched
   (`latest-4` = 4.22.2). For a genuinely new codebase with no dependency
   pinned to 4.x-only middleware, prefer 5.x. [Source:
   https://expressjs.com/en/guide/migrating-5.html]
2. **Existing 4.x app with real route patterns?** Don't upgrade
   opportunistically. The path-to-regexp rewrite is a real breaking change —
   run the official codemod recipe, then manually verify every route using
   `/*`, `:ext?`, or `[a|b]` alternation before merging. See
   [`references/route-syntax-migration.md`](references/route-syntax-migration.md).
3. **Native `.ts` execution vs. a build step?** Only viable when Node.js
   >=22.18.0 (or >=23.6.0 on v23) and TypeScript >=5.8 are both available.
   [Source: https://expressjs.com/en/starter/installing.html] On an older
   Node/TS pin, or when the deploy target needs bundling/minification/a
   non-Node runtime, keep a build step (`tsc`/`esbuild`/`tsx`). Don't add a
   build step "for future-proofing" when the runtime already supports native
   execution and the deploy target is Node itself — that's unnecessary
   tooling for no benefit.
4. **Simplest first:** Express is deliberately unopinionated about structure,
   database access, and auth [Source: https://expressjs.com/en/starter/faq.html]
   — don't reach for a custom DI container or routing abstraction before
   `express.Router()` module-splitting plus factory-function middleware
   prove insufficient.

## Workflow

1. Confirm the project's Express major version and Node.js version
   (`package.json`/lockfile) before writing route or middleware code —
   syntax and defaults differ by major line.
2. For new middleware, use the factory-function pattern
   (`module.exports = (options) => (req, res, next) => { ...; next(); }`) so
   options are configurable, mirroring `cookie-session`/`compression`.
   [Source: https://expressjs.com/en/guide/writing-middleware.html]
3. For new route groups, create an `express.Router()` per resource/module and
   mount it (`app.use('/resource', router)`); pass `mergeParams: true` only
   when the sub-router needs the parent route's captured params. [Source:
   https://expressjs.com/en/guide/routing.html]
4. Register error-handling middleware (4-arg signature) after every other
   `app.use()`/route registration; on 5.x let `async` handlers throw/reject
   instead of hand-writing `.catch(next)`. [Source: https://expressjs.com/en/guide/error-handling.html]
5. Add a catch-all 404 handler at the very bottom of the stack — 404s are not
   errors in Express and bypass error-handling middleware. [Source:
   https://expressjs.com/en/starter/faq.html]
6. If migrating 4.x→5.x: run the official codemod recipe, then manually fix
   remaining route patterns and re-check any code that assumed
   `req.body === {}` when unparsed or `extended: true` parsing.
7. Verify against the checks below before declaring done.

## Engineering rules

- Always call `next()` (or end the response) in every middleware that
  doesn't terminate the cycle — a missing `next()` hangs the request.
  [Source: https://expressjs.com/en/guide/writing-middleware.html]
- Register error-handling middleware last, after all other middleware/routes.
  [Source: https://expressjs.com/en/guide/error-handling.html]
- On Express 5.x, don't hand-write `.catch(next)` for every `async` handler
  — rejected/thrown errors are forwarded automatically; reserve manual
  `next(err)` for non-async promise chains and callback-based APIs. [Source:
  https://expressjs.com/en/guide/error-handling.html] [Version-sensitive:
  automatic forwarding is 5.x only]
- Match route-path syntax to the actual major version in use — don't write
  5.x brace/named-wildcard syntax against a 4.x app, or vice versa. [Source:
  https://expressjs.com/en/guide/routing.html]
- Validate/allow-list any user-supplied redirect target before calling
  `res.redirect()`/`res.location()` (see Security). [Source:
  https://expressjs.com/en/advanced/best-practice-security.html]
- Set `NODE_ENV=production` before deploying — it changes caching and
  error-verbosity behavior, not just throughput (see Performance/Security).

## Trade-offs

Express's unopinionated design — no bundled database layer, auth scheme, or
mandated app structure [Source: https://expressjs.com/en/starter/faq.html] —
buys fast initial setup with little to learn, at the cost of every
structural and hardening decision (validation, sessions, security headers)
being deferred to the developer and third-party packages rather than
enforced by the framework. 5.x's stricter defaults (`undefined` `req.body`,
read-only `req.query`, automatic async-error forwarding) close off a class
of silent bugs compared to 4.x, at the cost of the route-syntax migration
effort for any existing non-trivial 4.x routes.

## Anti-patterns

- Forgetting to call `next()` or end the response in a middleware, hanging
  the request. [Source: https://expressjs.com/en/guide/writing-middleware.html]
- Registering error-handling middleware before other routes instead of last
  — it won't catch errors from anything registered after it. [Source:
  https://expressjs.com/en/guide/error-handling.html]
- Expecting error-handling middleware to catch 404s — Express doesn't treat
  404s as errors; use an explicit catch-all at the bottom of the stack.
  [Source: https://expressjs.com/en/starter/faq.html]
- Using synchronous functions in a request-handling path — they block the
  single event loop for all concurrent requests. [Source:
  https://expressjs.com/en/advanced/best-practice-performance.html]
- Listening for `uncaughtException` as an error-handling strategy — the docs
  call this "dangerous and unreliable... the app is in an undefined state."
  [Source: https://expressjs.com/en/advanced/best-practice-performance.html]
- Leaving the default `connect.sid` session-cookie name in production —
  eases automated fingerprinting. [Source: https://expressjs.com/en/advanced/best-practice-security.html]
- Porting 4.x route strings (`/*`, `:file.:ext?`, `[a|b]`) into a 5.x app
  unchanged and assuming they still match the same requests. [Source:
  https://expressjs.com/en/guide/migrating-5.html]
- **Over-engineering trap:** building a custom plugin/DI framework on top of
  Express before `express.Router()` plus factory-function middleware prove
  insufficient — Express is deliberately unstructured by design [Source:
  https://expressjs.com/en/starter/faq.html]; don't impose heavy structure
  prematurely.

## Security

- **CVE-2024-43796** (XSS in `res.redirect`) — fixed in **4.20.0**. [Source:
  https://expressjs.com/en/advanced/security-updates.html] [Version-sensitive:
  4.x versions before 4.20.0 are vulnerable; 4.20.0+ and all 5.x lines
  postdate the fix]
- **CVE-2024-29041** (open-redirect in `res.location()`/`res.redirect()`) —
  fixed in **4.19.0/4.19.1**. [Source: https://expressjs.com/en/advanced/security-updates.html]
  [Version-sensitive: 4.x versions before 4.19.0 are vulnerable]
- Unresolved: a third-party source (npm registry search results, not an
  `expressjs.com` page) describes a filed CVE referenced as
  "CVE-2024-51999," tied to the 5.2.0→5.2.1 patch, as ultimately "rejected...
  not a genuine vulnerability." This could not be confirmed against an
  official `expressjs.com` security page in the underlying research —
  treat the identifier and its "rejected" status as **Unresolved**, not
  settled fact. [Source: research/technologies/express.md §7, cross-checked
  via registry.npmjs.org/express]
- Hardening beyond the two confirmed CVEs: `helmet` for security headers
  plus `app.disable('x-powered-by')`; explicit allow-list validation of any
  redirect target before `res.redirect()`; rename the default `connect.sid`
  session-cookie name and set `secure`/`httpOnly` on session cookies
  (`express-session`, preferred over `cookie-session` for anything beyond
  small data); `rate-limiter-flexible` against brute-force login attempts;
  correct `trust proxy` configuration (the outermost proxy must strip
  inbound `X-Forwarded-*` headers before Express trusts `req.ip`/
  `req.protocol`). [Source: https://expressjs.com/en/advanced/best-practice-security.html,
  https://expressjs.com/en/guide/behind-proxies.html] Deep threat-modeling
  method is owned by security-engineering — not restated here.

## Performance

`NODE_ENV=production` is the single biggest documented lever: it enables
view-template caching (`view cache` defaults to `true` only in production)
and CSS caching, and produces less verbose error output — Express's own
benchmark cites roughly a 3x throughput improvement. [Source:
https://expressjs.com/en/advanced/best-practice-performance.html,
https://expressjs.com/en/5x/api/application.html] This applies the same
across 4.x and 5.x. Deep performance method (profiling, load testing) is
owned by performance-engineering.

## Testing

Real documented gap: `expressjs.com` has **no official first-party testing
guide** — no dedicated "Testing" page exists under Guide or Advanced Topics.
`supertest` is the community-standard HTTP-assertion library for testing
Express apps, but it is not maintained under the `expressjs` GitHub
organization and is not cited by `expressjs.com` — it is a de facto, not an
official, standard. [Source: research/technologies/express.md §9, cross-
referenced against https://expressjs.com/en/resources/middleware.html, which
lists official middleware but no testing library] Deep test-strategy method
is owned by testing-strategy (`SK-QA-001`).

## Failure handling

- If the Express major version (4.x vs. 5.x) cannot be determined, ask or
  state explicitly which version the guidance assumes — never silently
  assume "latest"/5.x, since 4.x is still actively maintained and widely
  deployed.
- If shell is unavailable, output advisory code/config edits and state that
  install/build/test commands were not run.

## Escalation

- Upgrading a production service from 4.x to 5.x is a breaking-change
  migration (route syntax, `req.body`/`req.query` defaults) — present the
  migration plan and codemod-generated diff for explicit confirmation before
  merging; never apply it silently as part of an unrelated change.

## Outputs & verification

- **Outputs:** version-correct Express middleware/route/error-handler code,
  4.x-to-5.x migration notes when relevant, and hardening config.
- **Verify:** route-path syntax matches the actual major version in use;
  error-handling middleware is registered last; any security recommendation
  cites a specific CVE/fixed-version rather than a vague "update your
  dependencies."

## References

- [`references/route-syntax-migration.md`](references/route-syntax-migration.md)
  — Tier-2 4.x-to-5.x route-syntax and breaking-change table.
- Source list: see `skill.yaml.source_references` (expressjs.com official
  docs, retrieved 2026-09-10, via `research/technologies/express.md`).
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md)
  — Part 1 and Part 3 (Express) for the cross-technology Node.js floor table.
