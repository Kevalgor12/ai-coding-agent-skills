# Fastify — Deep Technology Research

Research date: 2026-09-09. Primary source: official documentation at
**https://fastify.dev/docs/latest/** (the canonical docs host — see
"Canonical docs host" note below). Where a claim is version-specific it is
tagged explicitly. All claims are cited inline; anything not found in
official sources is marked "Not documented / could not verify" rather than
guessed.

## Canonical docs host

[Source: https://github.com/fastify/fastify/issues/1952] The Fastify project
discussed moving off the `.io` TLD as early as November 2019, and a
maintainer (Matteo Collina) already controlled the `fastify.dev` domain at
that time (with `fastify.dev` originally redirecting to `fastify.io`).
[Source: https://fastify.dev/] As of this research date, the Fastify
organization's official website and documentation are hosted at
**fastify.dev**, not the older `fastify.io`. Unresolved: the official docs
site did not surface an explicit "we moved from fastify.io on date X"
announcement page in the pages fetched during this research, so the exact
cutover date is not confirmed — only that fastify.dev is the current
canonical host as of 2026-09-09.

---

## 1. Core concepts

[Source: https://fastify.dev/] Fastify describes itself as "a fast and low
overhead web framework for Node.js," an OpenJS Foundation "At Large" project
maintained by a global team of lead maintainers and collaborators.

[Source: https://fastify.dev/docs/latest/Guides/Getting-Started/] A Fastify
application is built around a **Fastify instance**, created by calling the
default export (`Fastify({...})`), which is the central object used to
register routes, plugins, hooks, and decorators, and to configure server
behavior.

[Source: https://fastify.dev/docs/latest/Guides/Getting-Started/] Minimal
example shown in the official Getting Started guide:
```javascript
import Fastify from 'fastify'
const fastify = Fastify({ logger: true })
fastify.get('/', async (request, reply) => {
  return { hello: 'world' }
})
await fastify.listen({ port: 3000 })
```

[Source: https://fastify.dev/docs/latest/Guides/Getting-Started/] Core
building blocks documented:
- **Routes** — defined via shorthand methods (`fastify.get()`, `fastify.post()`, etc.) or the full `route()` API.
- **Schemas** — JSON Schema definitions attached to routes for request validation and response serialization; the docs state "Data validation is extremely important and a core concept of the framework."
- **Plugins** — the primary mechanism for organizing code and adding functionality, loaded via `register()`.
- **Decorators** — custom properties/functions attached to the Fastify instance, Request, or Reply objects for code reuse.
- **Request/Reply objects** — wrap the underlying Node.js `req`/`res`, exposing Fastify-specific conveniences (e.g., `request.body`, `reply.send()`).
- **Async/await** — natively supported; an async handler can simply `return` a value instead of calling `reply.send()`.

[Source: https://fastify.dev/docs/latest/Reference/Encapsulation/] A
foundational concept unique to Fastify's design is the **encapsulation
context**: it governs which decorators, hooks, and plugins are visible to a
given set of routes. Child contexts inherit from parents; parents cannot see
into children; sibling contexts cannot see each other.

## 2. Architecture

[Source: https://fastify.dev/docs/latest/Reference/Encapsulation/] Fastify's
plugin system forms a hierarchical (documented as a directed acyclic graph)
tree of encapsulation contexts. Each call to `fastify.register()` by default
creates a new child scope. Decorators, hooks, and routes registered inside a
scope are only visible within that scope and its descendants, not to
siblings or ancestors. This is enforced by the underlying plugin-loading
engine (Avvio, referenced implicitly by the docs' description of
promise/callback-based plugin completion) — [Inference, not confirmed in
docs: the specific library name "avvio" was recalled from general Fastify
knowledge; it was not explicitly named in the fetched Encapsulation page
text, so treat the library name as unconfirmed by this research pass].

[Source: https://fastify.dev/docs/latest/Reference/Plugins/] `fastify-plugin`
is the documented mechanism to deliberately **break** encapsulation, making
a plugin's decorators/hooks available to its parent scope rather than being
isolated. An alternative is setting `Symbol.for('skip-override')` on the
plugin function, though the docs note this requires manually maintaining
compatibility.

[Source: https://fastify.dev/docs/latest/Reference/Lifecycle/] Requests flow
through a fixed **lifecycle** of hooks in a defined order (see Section 3 /
Hooks below): routing → `onRequest` → `preParsing` → body parsing →
`preValidation` → schema validation → `preHandler` → user handler →
`preSerialization` → `onSend` → response sent → `onResponse`, with
`onError`, `onTimeout`, and `onRequestAbort` as exception paths. [Source:
https://fastify.dev/docs/latest/Reference/Lifecycle/] Calling
`reply.hijack()` at any point prevents Fastify from running subsequent hooks
or auto-sending the response, handing full control to application code.

[Source: https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/]
Architecturally, Fastify separates concerns into (a) an HTTP/routing layer,
(b) a schema-compilation layer using **Ajv v8** (validation) and
**fast-json-stringify** (serialization) that compiles JSON Schemas into
optimized functions ahead of use, and (c) the plugin/encapsulation layer
described above.

[Source: https://fastify.dev/docs/latest/Reference/Server/] The server
factory (`Fastify(options)`) can wrap Node's core `http`, `https`, or
`http2` modules, or accept a fully custom `serverFactory` function, meaning
Fastify's architecture treats the underlying transport as pluggable.

## 3. APIs

[Source: https://fastify.dev/docs/latest/Reference/Routes/] **Routing API**:
shorthand methods `fastify.get()`, `.post()`, `.put()`, `.delete()`,
`.patch()`, `.options()`, `.head()`, and `.all()`; full declarative form via
`fastify.route(options)`. Route option object supports `method`, `url`,
`schema`, `handler`, per-route lifecycle hooks (`onRequest`, `preParsing`,
`preValidation`, `preHandler`, `preSerialization`, `onSend`, `onResponse`),
`errorHandler`, `validatorCompiler`, `logLevel`, `logSerializers`,
`bodyLimit`, `handlerTimeout`, `config` (arbitrary metadata), and
`constraints` (e.g., host/version-based matching). An async handler that
returns a value has that value auto-sent as the reply unless the handler
explicitly awaits/returns `reply` itself (relevant to the "hijack" pattern).

[Source: https://fastify.dev/docs/latest/Reference/Request/] **Request API**
(selected): `request.query`, `.body`, `.params` (percent-decoded, "treat as
untrusted input" per the docs), `.headers`, `.raw` (underlying Node
`IncomingMessage`), `.server`, `.id`, `.log`, `.ip`, `.ips`, `.host`,
`.hostname`, `.port`, `.protocol`, `.method`, `.url`, `.originalUrl`,
`.mediaType`, `.is404`, `.socket`, `.signal` (an `AbortSignal`), and
`.routeOptions` (route config incl. schema, bodyLimit, handlerTimeout).
Validation helper methods: `getValidationFunction()`,
`compileValidationSchema()`, `validateInput()`.

[Source: https://fastify.dev/docs/latest/Reference/Reply/] **Reply API**
(selected): `.send(data)`, `.code(statusCode)`, `.header()/.headers()`,
`.type()`, `.getHeader()/.getHeaders()/.removeHeader()`, `.redirect(dest,
[code])` (default 302), `.callNotFound()`, `.serializer()`,
`.getSerializationFunction()`, `.compileSerializationSchema()`,
`.serializeInput()`, `.raw` (underlying `ServerResponse`), `.sent`,
`.elapsedTime`, `.statusCode`, `.trailer()/.hasTrailer()/.removeTrailer()`,
`.writeEarlyHints()`, `.hijack()`, and a `.then()` method allowing the reply
to be awaited Promise-like.

[Source: https://fastify.dev/docs/latest/Reference/Hooks/] **Hooks API**
(`fastify.addHook(name, fn)`). Request/reply hooks, in execution order:
`onRequest` → `preParsing` → `preValidation` → `preHandler` →
`preSerialization` (skipped for string/buffer/stream/null payloads) →
`onSend` → `onResponse`; plus `onError`, `onTimeout` (fires on
`connectionTimeout`), and `onRequestAbort` (fires when the client aborts
mid-request). Application-level hooks: `onReady` (serial, pre-listen),
`onListen`, `onClose`, `preClose`, `onRoute` (synchronous, fires on route
registration), and `onRegister` (fires before a plugin's code executes,
within its encapsulated context). All hooks except `onClose` are
encapsulated (scoped). Both callback (`done`) and async/await styles are
supported.

[Source: https://fastify.dev/docs/latest/Reference/Plugins/] **Plugins API**:
`fastify.register(plugin, [options])`. Recognized register-level options
include `prefix`, `logLevel`, `logSerializers`. The full options object is
also passed through to the plugin itself.

[Source: https://fastify.dev/docs/latest/Reference/Decorators/]
**Decorators API**: `fastify.decorate(name, value, [dependencies])`,
`decorateRequest(name, value, [dependencies])`,
`decorateReply(name, value, [dependencies])`. The API is synchronous by
design — "Defining a decoration asynchronously could result in the Fastify
instance booting before the decoration completes."

[Source: https://fastify.dev/docs/latest/Reference/Errors/] **Error handling
API**: `fastify.setErrorHandler(fn)`, a built-in `errorCodes` object
exposing 70+ documented internal error codes, and automatic `FST_ERR_VALIDATION`
errors for schema validation failures.

[Source: https://fastify.dev/docs/latest/Guides/Testing/] **Testing API**:
`fastify.inject(options)` (backed by `light-my-request`) for in-process HTTP
simulation without binding a real socket; `fastify.ready()` to fully boot
without listening; `fastify.close()` for teardown.

## 4. Configuration

[Source: https://fastify.dev/docs/latest/Reference/Server/] The Fastify
factory function accepts an options object. Documented options include
(non-exhaustive; grouped by the categories the reference page itself uses):

**Transport**: `http` (Node core `createServer` options), `http2`
(boolean), `https` (TLS options).

**Connection management**: `connectionTimeout` (default `0`),
`keepAliveTimeout` (default `72000` ms), `forceCloseConnections`
(boolean|`"idle"`, default `"idle"`), `maxRequestsPerSocket` (default `0`,
HTTP/1.1 only), `requestTimeout` (default `0`), `handlerTimeout` (default
`0`; application-level per-route-lifecycle timeout, overridable per route).

**Request handling**: `bodyLimit` (default `1048576` bytes / 1MB),
`onProtoPoisoning` (`'error'` default; `'error'|'remove'|'ignore'`),
`onConstructorPoisoning` (`'error'` default, same enum).

**Logging**: `logger` (boolean or Pino options object), `loggerInstance`
(custom Pino-compatible logger instance — see Section 13, this replaced
passing a custom instance via `logger` in v5), `disableRequestLogging`,
`logController`, `requestIdHeader`, `requestIdLogLabel` (default `'reqId'`,
documented as deprecated in favor of `logController`), `genReqId` (default:
monotonically increasing integers).

**Server behavior**: `serverFactory` (custom HTTP server factory function),
`trustProxy` (boolean/string/array/function, default `false`),
`pluginTimeout` (default `10000` ms), `return503OnClosing` (default
`true`).

**Query/URL**: `querystringParser` (default: `fast-querystring`),
`exposeHeadRoutes` (default `true`).

**Validation/serialization**: `ajv` (Ajv v8 config incl. `customOptions`,
`plugins`), `serializerOpts` (fast-json-stringify options).

**HTTP/2**: `http2SessionTimeout` (default `72000` ms).

**Error/URL handling**: `frameworkErrors` (custom handler for internal
errors like `FST_ERR_BAD_URL`), `clientErrorHandler`, `rewriteUrl`,
`allowErrorHandlerOverride` (default `true`).

**Router options** (nested under `routerOptions`): `allowUnsafeRegex`
(default `false`), `buildPrettyMeta`, `caseSensitive` (default `true`),
`constraints`, `defaultRoute`, `ignoreDuplicateSlashes` (default `false`),
`ignoreTrailingSlash` (default `false`), `maxParamLength` (default `100`),
`onBadUrl`, `onMaxParamLength`, `useSemicolonDelimiter` (default `false` —
**changed from a permissive default in earlier versions; see Section 11/13
migration notes**).

Unresolved: the exact default value and behavior of `useSemicolonDelimiter`
prior to v5 was described secondhand in the V5 migration guide (see Section
13) rather than directly verified on an older versioned Server reference
page; treat the "changed default" framing as sourced from the migration
guide specifically, not independently cross-checked against the v4 Server
reference.

[Source: https://fastify.dev/docs/latest/Reference/Server/] The factory
returns an instance exposing methods including `listen()`, `close()`,
`register()`, `addHook()`, `addSchema()`, `setErrorHandler()`,
`setNotFoundHandler()`, and `inject()`.

## 5. Recommended patterns

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/] **Run
behind a reverse proxy.** The docs state the team "strongly considers"
exposing a Fastify app directly to the internet "an anti-pattern and
extremely bad practice." A reverse proxy (Nginx or HAProxy, both with
example configs in the guide) should own TLS termination, load balancing,
static file serving, and multi-domain routing, leaving the app to handle
business logic only.

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/] **Prefer
Fastify-native hooks/plugins over generic middleware** on latency-sensitive
paths, and **prefer static/simple parametric routes over regex routes** for
performance; use route constraints (e.g. version constraints, async custom
constraints) judiciously since they degrade routing performance.

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/] **Define
response schemas** to accelerate JSON serialization via
fast-json-stringify, and **keep Ajv's `allErrors` disabled** by default,
enabling it only when detailed validation feedback is actually needed.

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/] **For
Kubernetes**, bind the app to `0.0.0.0` (Fastify's default bind is
`127.0.0.1`, which readiness probes typically cannot reach) or otherwise
configure probes to match the app's actual listen address.

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/] **Capacity
planning**: for low-latency workloads, allocate around 2 vCPUs per instance
(to leave headroom for GC); for high-throughput workloads, smaller/fractional
CPU allocations (the guide cites experiments where some API gateways
performed well on 100–200m vCPU) can be considered — but this should be
validated with load testing (k6, autocannon) rather than assumed.

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/] **Running
multiple Fastify instances in one Node.js process is explicitly endorsed**:
"It is perfectly fine to spin up several Fastify instances within the same
Node.js process," even under high load.

[Source: https://fastify.dev/docs/latest/Reference/Encapsulation/, https://fastify.dev/docs/latest/Reference/Plugins/]
**Use encapsulation deliberately**: keep plugins self-contained by default;
only reach for `fastify-plugin` when a plugin's decorators/hooks genuinely
need to be visible to the parent scope.

[Source: https://fastify.dev/docs/latest/Guides/Testing/] **Prefer
`fastify.inject()` over binding a real socket for tests** — it guarantees
all registered plugins have finished booting before assertions run, and
avoids the overhead/flakiness of real network calls.

[Source: https://fastify.dev/docs/latest/Guides/Database/] **For database
access**, either use an official `@fastify/*` plugin (mysql, postgres,
redis, mongodb) which decorates the instance with a ready-to-use client, or
follow the documented custom-plugin pattern: decorate the instance with the
connection and register an `onClose` hook to close it cleanly.

## 6. Anti-patterns

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/]
Explicitly called out anti-patterns: exposing the Fastify app directly to
the internet without a reverse proxy; implementing reverse-proxy-like
concerns (TLS termination, multi-domain routing) inside the application
itself; leaving `allErrors: true` enabled by default in Ajv (documented as
a performance cost, not a security issue); skipping response schemas
(loses serialization speed and the "prevent accidental disclosure of
sensitive information" benefit — see Validation section); overusing regex
or async/version route constraints on hot paths.

[Source: https://fastify.dev/docs/latest/Reference/Middleware/] Using
generic Express/Connect-style middleware on performance-sensitive paths is
discouraged relative to Fastify-native hooks/plugins — middleware is "not
supported out of the box and requires an external plugin" (`@fastify/express`
or `@fastify/middie`), and middleware **cannot** access Fastify-specific
Request/Reply methods (e.g. `reply.send()`) because those wrappers are
applied after the middleware phase; middleware also cannot match
parameterized or multi-segment wildcard paths the way Fastify routes can.

[Source: https://fastify.dev/docs/latest/Reference/Decorators/] Decorating
`Request`/`Reply` with **reference types (Array/Object) is rejected** by the
decorator API precisely because "any mutation will impact all requests,
potentially creating security vulnerabilities or memory leaks." The
documented fix is to initialize such state per-request in an `onRequest`
hook, or use getter/setter patterns.

[Source: https://fastify.dev/docs/latest/Reference/Warnings/] **Mixing
async and callback styles within a single plugin** is flagged by
`FSTWRN003` as a source of unhandled-rejection bugs; as of **v5**, mixing
these styles in one plugin is disallowed entirely (see Section 13).

[Source: https://fastify.dev/docs/latest/Reference/Warnings/] **Calling
`setErrorHandler` more than once in the same scope** is flagged by
`FSTWRN004` ("can introduce subtle bugs"); `allowErrorHandlerOverride`
(default `true`) governs whether this is even permitted.

[Source: https://fastify.dev/docs/latest/Guides/Migration-Guide-V5/]
**Mutating `reply.sent` directly is forbidden** as of v5 — use
`reply.hijack()` instead.

## 7. Security

[Source: https://fastify.dev/docs/latest/Reference/Server/] Fastify has
built-in, on-by-default protection against **prototype pollution** via JSON
body parsing: `onProtoPoisoning` and `onConstructorPoisoning` both default
to `'error'`, rejecting payloads containing `__proto__` or `constructor`
keys unless explicitly relaxed to `'remove'` or `'ignore'`.

[Source: https://fastify.dev/docs/latest/Guides/Prototype-Poisoning/] The
official Prototype Poisoning guide explains the underlying vulnerability
class (malicious `__proto__` keys surviving `JSON.parse()` and later
leaking into the prototype chain via operations like `Object.assign()`,
bypassing validation) and recounts how the hapi ecosystem — which
influenced Fastify's design — mitigated it with a hardened JSON parser.
Note: this specific guide page is historical/narrative (authored by Eran
Hammer) and does not itself document the `onProtoPoisoning`/
`onConstructorPoisoning` config knobs — those are documented on the Server
reference page instead (cited above). Unresolved: whether the
Prototype-Poisoning guide has been updated post-2019 was not established
from the fetched content alone.

[Source: https://fastify.dev/docs/latest/Guides/Migration-Guide-V5/] As of
**v5**, the internal `parameters` object used for route params **no longer
inherits from `Object.prototype`**, closing off another prototype-pollution
surface; application code should use `Object.hasOwn()` instead of
`.hasOwnProperty()` when checking param keys.

[Source: https://fastify.dev/docs/latest/Reference/Errors/] By default,
Fastify's error handler serializes errors to JSON with `statusCode`,
`error`, `message`, and optionally `code` — but **does not omit sensitive
detail by environment**: "error messages are forwarded verbatim to
clients," which can leak database schema/query details if an application
lets raw errors (e.g., a DB driver error) escape to the client. Fastify does
not itself distinguish dev vs. prod here — that is the application's
responsibility via `setErrorHandler`, sanitizing anything with
`statusCode >= 500` while letting deliberately-raised errors (`< 500`, or
validation errors carrying `FST_ERR_VALIDATION`) pass through as-is.

[Source: https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/]
Defining explicit **response schemas** is documented as a security control
as well as a performance one: it "can drastically increase throughput and
help prevent accidental disclosure of sensitive information," since only
schema-declared fields are serialized into the response.

[Source: https://github.com/fastify/fastify/blob/main/SECURITY.md] Official
vulnerability reporting is via the [GitHub Security
advisories](https://github.com/fastify/fastify/security/advisories/new)
page. Reporters must not self-assign/request CVEs (handled by the Fastify
Security Team) and must never demonstrate CI/CD-type vulnerabilities via
pull requests against Fastify repos. Documented SLA: triage within 4
business days; a 90-day window to develop and coordinate a patch; a 90-day
window to publication, with severity assessed via CVSS v3. If there's no
acknowledgment within 6 business days, reporters can escalate to the OpenJS
Foundation CNA at `security@lists.openjsf.org`. The policy explicitly
covers Fastify core and official (`@fastify/*`) plugins, and explicitly
**excludes** application-level code, third-party (non-`@fastify`)
dependencies, and deployments running with `insecureHTTPParser: true`. The
fetched policy text did not specify a version-support matrix for which
Fastify major lines receive security patches — see Section 12/LTS for that
(a separate document).

[Source: https://fastify.dev/docs/latest/Guides/Ecosystem/] Security-related
official plugins mentioned: `@fastify/helmet`, `@fastify/csrf-protection`,
`@fastify/cors`, `@fastify/rate-limit`, `@fastify/jwt`, `@fastify/auth`,
`@fastify/basic-auth`, `@fastify/bearer-auth`, `@fastify/passport`.

## 8. Performance

[Source: https://fastify.dev/] The official homepage cites a benchmark (run
against a specific Fastify version) putting **Fastify 5.11.3 at ~88,171
req/s**, ahead of listed comparators in the same benchmark: H3 2.0.1-rc.26
(~82,683 req/s), Hono 4.13.1 (~82,371 req/s), Hapi 21.4.10 (~59,754 req/s),
Express 5.2.1 (~57,936 req/s), Koa 3.2.1 (~57,214 req/s). The page
summarizes this as roughly "1.5x" Express's throughput and "around 88
thousand requests per second" for Fastify. [Inference, not confirmed in
docs: the exact benchmark methodology/hardware for these homepage numbers
was not shown in the fetched excerpt — treat these as vendor-published
marketing benchmark figures, not independently reproduced numbers.]

[Source: https://fastify.dev/docs/latest/Guides/Benchmarking/] For
first-party benchmarking of your own app/changes, the docs recommend
**autocannon** (an HTTP/1.1 load-testing tool written in Node), plus
`branch-comparer` (compare performance across git branches and/or Node.js
versions), `concurrently`, and `npx`. The guide frames benchmarking as a
methodology for measuring the effect of your own changes, not as a vehicle
for framework-vs-framework claims, and gives no specific throughput numbers
itself.

[Source: https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/]
Performance design choices: Ajv v8 and fast-json-stringify both **compile**
JSON Schemas into specialized functions ahead of request handling rather
than interpreting schemas at runtime; type coercion (e.g.
`coerceTypes: 'array'`) is applied as part of a custom Ajv configuration to
reduce manual data-shaping work; schemas can be shared/deduplicated via
`addSchema()`.

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/]
Route-matching performance guidance: prefer static and simple parametric
routes over regex-based routes; be judicious with constraints (version
constraints and async custom constraints both degrade routing performance).

[Source: https://fastify.dev/docs/latest/Reference/Decorators/] Decorator
performance guidance: initialize decorators with a value of the same
*shape*/type they'll eventually hold (e.g. empty string for a string,
`null` for an object placeholder) so the JS engine can better optimize
object shapes.

## 9. Testing

[Source: https://fastify.dev/docs/latest/Guides/Testing/] Fastify is
described as compatible with most Node.js testing frameworks; the official
guide's own examples use Node's built-in **`node:test`** runner, while
noting other frameworks are equally viable.

[Source: https://fastify.dev/docs/latest/Guides/Testing/] The primary,
documented testing primitive is **`fastify.inject(options)`**, built on
`light-my-request`, which simulates HTTP requests in-process without
opening a real socket. Documented benefit: "`.inject` ensures all
registered plugins have booted up and our application is ready to test."
It supports arbitrary methods, query params, payloads, custom headers, and
cookies, in both callback and Promise/async-await styles. Example pattern
shown:
```javascript
const response = await app.inject({ method: 'GET', url: '/' })
```

[Source: https://fastify.dev/docs/latest/Guides/Testing/] Alternative
documented approach: actually call `fastify.listen()` and drive it with a
real HTTP client (`undici`, native `fetch`, or SuperTest are named), or call
`fastify.ready()` to fully initialize the app (running all plugin/boot
logic) without binding a listening socket.

[Source: https://fastify.dev/docs/latest/Guides/Testing/] Documented best
practices: keep application-construction logic separate from
server-startup/listen logic so it's easy to build an app instance for
testing; always call `.close()` in teardown so external resources
(DB connections, etc.) are released; for `tap`-style runners, use `t.plan()`
to declare expected assertion counts; test plugins in isolation by
registering them into a throwaway Fastify instance and exercising them via
`.inject()`.

## 10. Deployment

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/] Standard
deployment guidance is to run Fastify **behind a reverse proxy** (Nginx or
HAProxy — sample configs given in the guide) rather than exposed directly.

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/] For
**Kubernetes**, bind to `0.0.0.0` (Fastify defaults to binding
`127.0.0.1`) so readiness/liveness probes on the pod's external interface
can actually reach the app; capacity planning guidance (2 vCPUs for
low-latency, fractional/1 vCPU for high-throughput) applies here too, to be
validated with k6/autocannon load tests.

[Source: https://fastify.dev/docs/latest/Guides/Serverless/] For
**serverless**, the official guide notes larger apps have slower cold-boot
times, and generally recommends **container-style "serverless"
platforms that handle concurrent requests and use Fastify's full feature
set** — Google Cloud Run, AWS Fargate, Azure Container Instances, and
Vercel are named — over pure FaaS where possible.
- **AWS Lambda**: API Gateway "does not support streams" and enforces a
  29-second response timeout; the docs point to `@fastify/aws-lambda`
  (Fastify-optimized) or `@h4ad/serverless-adapter` (broader AWS service
  coverage) as integration options.
- **Google Cloud Functions / Firebase**: the platform pre-parses the
  request body before Fastify sees it, so a custom `contentTypeParser` is
  required; without it, the docs warn of "the Fastify process remaining
  stuck and not processing any other requests."
- **Google Cloud Run**: minimal changes needed — runs as a standard
  container, must bind to the port/host Cloud Run provides.
- **Vercel**: has an official Fastify template and "Fluid compute" (blends
  serverless autoscaling with server-like concurrency).

[Source: https://fastify.dev/docs/latest/Guides/Serverless/] A stated
advantage of this model: local development runs unmodified Fastify with no
extra tooling; only the production deploy needs the adapter layer.

## 11. Migration

[Source: https://fastify.dev/docs/latest/Guides/Migration-Guide-V5/] The
official **V4 → V5 migration guide** documents (all **version-sensitive to
v5.x**, i.e. behavior differs from v4):
- **Node.js requirement raised to v20+** (v18 support dropped); rationale
  given: v20 has better `node:test` support and v18 was nearing Node's own
  LTS end (cited as April 30, 2025 in the guide).
- **Full JSON Schema required** for `querystring`/`params`/`body`/`response`
  — the `jsonShortHand` shorthand option was **removed**; schemas need
  explicit `type` and complete object definitions.
- **`logger` option no longer accepts a pre-built custom logger instance**
  — use the new **`loggerInstance`** option instead.
- **`useSemicolonDelimiter` now defaults to `false`** (RFC 3986-compliant),
  ending non-standard semicolon-as-query-delimiter support unless
  explicitly re-enabled.
- Route `parameters` object **no longer inherits `Object.prototype`**
  (security hardening) — use `Object.hasOwn()` in app code.
- **Type providers** now distinguish `ValidatorSchema` vs. `SerializerSchema`
  — custom type-provider packages need updating.
- **Removed**: `request.connection` (use `request.socket`),
  `reply.getResponseTime()` (use `reply.elapsedTime`).
- **Renamed/moved**: route metadata now under `request.routeOptions`
  instead of the deprecated `request.context`/`request.routeSchema`, etc.
- **`.listen()` requires the object-argument form** (`{ port: 8000 }`)
  instead of positional arguments.
- **`reply.redirect(url, code)` argument order reversed** vs. v4.
- **`reply.trailer()` callbacks must be async.**
- Custom `HEAD` routes must be **registered before** the matching `GET`
  route when `exposeHeadRoutes: true`.
- Non-standard HTTP methods (e.g. `PROPFIND`, `PROPPATCH`) are **no longer
  registered by default**, but can be re-added via `addHttpMethod()`.
- `fastify.hasRoute()` now requires the actual **route pattern**, not an
  example URL.
- Reference-type (`Array`/`Object`) **request/reply decorators are
  rejected** — use functions/getters or `onRequest`-hook-based
  initialization instead.
- **Plugins can no longer mix callback and Promise (async) styles** within
  a single plugin function.
- **`reply.sent` can no longer be mutated directly** — use
  `reply.hijack()`.
- Sending a **`DELETE` with an empty JSON body is no longer accepted.**
- Route **versioning constraint syntax changed**: use
  `constraints: { version: "..." }` instead of the old top-level `version`
  route option.
- `request.host`/`.hostname`/`.port` are now **distinct properties**
  (previously conflated).
- `getDefaultRoute`/`setDefaultRoute` methods were **removed**.
- JSON Schema `time`/`date-time` string formats now **enforce timezone
  presence**.

[Source: https://fastify.dev/docs/latest/Guides/Migration-Guide-V4/] A
separate official **V3 → V4 migration guide** exists (found via search but
not deeply fetched in this pass) — Unresolved: its specific content was not
reviewed in detail during this research; only its existence and URL are
confirmed.

[Source: https://fastify.dev/docs/latest/Guides/Migration-Guide-V3/] A
**V2 → V3 migration guide** also exists at this URL — same caveat: existence
confirmed, contents not reviewed in this pass.

Migrating *from a comparable alternative framework* (e.g., Express, Koa)
into Fastify: **Not documented / could not verify** — no dedicated
"migrating from Express" official guide was located during this research;
the closest related material is the Middleware reference explaining how
Express-style middleware can be run under Fastify via `@fastify/express` or
`@fastify/middie` as an interop/incremental-adoption path (see Section 16).

## 12. Version information

[Source: https://registry.npmjs.org/fastify (npm registry, the official
publish target for the `fastify` package maintained by the Fastify org —
used here as a primary source for release dates/tags since it is the
canonical distribution channel, cross-checked against
https://github.com/fastify/fastify/releases)] As of 2026-09-09:
- **Latest stable (`latest` dist-tag): v5.12.3**, published 2026-09-04.
- Recent v5.x release cadence sampled from registry timestamps: 5.8.0
  (2026-03-05) → 5.8.5 (2026-04-14) → 5.9.0 (2026-06-28) → 5.10.0
  (2026-07-05) → 5.11.0 (2026-07-30) → 5.11.1/5.11.2/5.11.3 (2026-08-03 to
  2026-08-08) → 5.12.0 (2026-08-13) → 5.12.1 (2026-08-18) → 5.12.2/5.12.3
  (2026-09-04). This shows Fastify ships **patch/minor releases roughly
  every 1–4 weeks** on the v5 line. [Inference, not confirmed in docs: this
  cadence observation is derived from raw npm timestamps rather than a
  documented release-cadence policy statement — no official page was found
  stating a fixed cadence commitment.]
- **v6 is in active pre-release**: `6.0.0-alpha.0` (2026-08-11) through
  `6.0.0-alpha.3` (2026-09-04), tracked under npm's `next` dist-tag. The v6
  alpha series is described (per GitHub release notes) as including several
  security fixes and, in `alpha.0`, removal of deprecated APIs plus raised
  minimum Node.js version requirements.
- Older still-tagged majors on npm: `three` → 3.29.5, `four` → 4.29.1 (dist-tags
  for the last releases of the v3 and v4 lines).

[Source: https://fastify.dev/docs/latest/Reference/LTS/] **LTS/support
policy** (official "Long Term Support" reference page): each Fastify major
release line is supported for a **minimum of 6 months from release**, and
receives **security-only updates for an additional 6 months** after the
*next* major version ships (i.e., roughly a 12-month total window per major,
split into "full support" then "security-only"). Major releases are tested
against **all Node.js release lines that are within the Node.js LTS
window** as of that Fastify release — implying only the latest patch of a
given Node LTS line is considered supported. **v4 is documented as retiring
2025-06-30.** **v5 supports Node.js v20+ only** (v18 dropped), justified by
v5's reliance on newer `node:test` capabilities. The LTS page also
documents that alternative Node-compatible runtimes (e.g. **NodeSource
N|Solid**) are tested against Fastify major releases by their own
maintenance teams, with N|Solid's LTS support scope aligned to the Fastify
release it was tested against.

[Source: https://fastify.dev/docs/latest/Reference/TypeScript/] The docs
state current documentation build corresponds to **v5.12.1** (a specific
patch snapshot referenced within the TypeScript reference page at fetch
time) — consistent with the "latest" docs tracking the v5.x line rather
than the in-progress v6 alphas. Unresolved: it isn't fully confirmed from
the pages fetched whether `/docs/latest/` is defined by the project to
always mean "latest **stable**" (currently v5) versus simply "the most
recently published docs build" — treat "latest" in this document as
meaning **v5.x** throughout, since all fetched `/docs/latest/` content
matched v5-era behavior (e.g., `loggerInstance`, `routerOptions`,
`handlerTimeout`) with no v6-only content observed.

## 13. Breaking changes

All items below are consolidated from the V5 migration guide (already
detailed in full in Section 11) — repeated here as a condensed
"what-broke" list, all **version-sensitive: v4 → v5**:
- Node.js **v18 support dropped**, v20+ required.
- `jsonShortHand` **removed**; full JSON Schema now mandatory for
  body/query/params/response.
- `logger` **no longer accepts a custom instance** — use `loggerInstance`.
- `useSemicolonDelimiter` **default flipped** from permissive to `false`.
- `request.connection` and `reply.getResponseTime()` **removed**.
- `.listen()` **positional-argument form removed** — object form required.
- `reply.redirect()` **argument order reversed**.
- Plugins **can no longer mix async/callback styles**.
- `reply.sent` **can no longer be set directly**.
- Empty-body `DELETE` requests **rejected** where previously accepted.
- Route **`version` option replaced** by `constraints: { version }`.
- **Array/Object decorators on Request/Reply rejected outright** (previously
  merely risky, now a hard error per the migration guide's framing).
- **Non-standard HTTP methods removed by default** (re-addable via
  `addHttpMethod()`).

[Source: https://fastify.dev/docs/latest/Reference/Warnings/] Beyond major-
version breaks, Fastify uses a **runtime deprecation-warning system**
(`FSTDEP0xx` codes, surfaced via Node's `--trace-warnings`/
`--trace-deprecation`) to telegraph upcoming removals ahead of the next
major. Documented codes captured in this research pass: `FSTDEP022`
(top-level router options deprecated in favor of `options.routerOptions`),
`FSTDEP023` (`disableRequestLogging` deprecated in favor of a
`LogController`), `FSTDEP024` (`requestIdLogLabel` deprecated, same
direction), `FSTDEP025` (adding an HTTP method that already exists without
`{ overrideExisting: true }` is deprecated). [Inference, not confirmed in
docs: the fetched Warnings page excerpt did not include the full list of
FSTDEP codes — only four were captured; there are very likely more
(FSTDEP001–FSTDEP0NN) that were not surfaced by the fetch/summarization
step. Treat this list as a **sample**, not exhaustive.] Similarly, only
three `FSTWRN0xx` codes were captured (`FSTWRN001`, `FSTWRN003`,
`FSTWRN004`) — `FSTWRN002` was not seen in the fetched excerpt, so its
existence/meaning is Unresolved from this pass.

[Source: https://github.com/fastify/fastify/releases] The **v6.0.0-alpha**
series (alpha.0 through alpha.3, Aug–Sep 2026) is stated to include
"several security fixes" and, per `alpha.0`, "removing deprecated APIs and
increasing minimum Node.js version requirements" — i.e., v6 is expected to
continue the pattern of dropping the FSTDEP-flagged surface area and
raising the Node.js floor again. Unresolved: the exact new Node.js minimum
for v6 was not confirmed in the fetched release notes excerpt, and v6 is
**pre-release (alpha)** as of this research date — not yet suitable to
document as stable/production guidance.

## 14. Limitations

[Source: https://fastify.dev/docs/latest/Reference/Middleware/] Fastify has
**no built-in Express/Connect-style middleware support** — it requires an
external plugin (`@fastify/express` or `@fastify/middie`). Even then,
middleware registered via `fastify.use()` operates on the raw Node
req/res (not the Fastify-wrapped Request/Reply), so it **cannot** call
Fastify-specific methods like `reply.send()`; and `fastify.use('/path',
middleware)` path-scoping **does not support parameterized routes**, and
wildcards cannot span multiple path segments.

[Source: https://fastify.dev/docs/latest/Reference/Decorators/] Request/Reply
decorators **cannot hold reference types** (Array/Object) — the API
rejects this outright to prevent cross-request state leakage; only
primitives, functions, or getters/setters are permitted directly, with
`onRequest`-hook-based initialization as the escape hatch for per-request
object state.

[Source: https://fastify.dev/docs/latest/Reference/Decorators/] The
decorator API is **synchronous only** — there is no way to await an async
decoration; async setup must instead be driven through the plugin/hook
system.

[Source: https://fastify.dev/docs/latest/Guides/Serverless/] On **AWS
Lambda via API Gateway**, streaming responses are not supported ("API
Gateway does not support streams"), and there's a hard **29-second**
response-time ceiling imposed by the platform, not by Fastify itself.

[Source: https://fastify.dev/docs/latest/Guides/Serverless/] On **Google
Cloud Functions/Firebase**, the platform pre-parses request bodies before
handing off to Fastify, which — without a custom `contentTypeParser`
workaround — can leave "the Fastify process remaining stuck and not
processing any other requests."

[Source: https://fastify.dev/docs/latest/Reference/Errors/] Fastify's
default error serialization **does not sanitize error messages for
production** — full `error.message` text reaches the client by default,
which the docs frame as something applications must handle themselves via
`setErrorHandler`, not something Fastify limits automatically.

## 15. Debugging

[Source: https://fastify.dev/docs/latest/Reference/Server/, https://fastify.dev/docs/latest/Reference/Warnings/]
No single dedicated "Debugging" guide page was located on fastify.dev during
this research (a targeted search for one returned no such page — see
Unresolved note below). Debugging-relevant official facts that were
confirmed:
- **Deprecation/warning tracing**: Node's own `--trace-warnings` and
  `--trace-deprecation` flags surface the `FSTDEP0xx`/`FSTWRN0xx` codes
  (Section 13) with stack context, per the Warnings reference page.
- **`printRoutes()`**: [Inference, not confirmed in docs: this was returned
  by a WebSearch summary as a debugging aid for visualizing the internal
  router tree, but the underlying fastify.dev page was not independently
  fetched and read in full during this pass — flag as unconfirmed
  pending direct verification.]
- **`frameworkErrors`** (Server reference, Section 4) lets an application
  intercept internal framework-level errors (e.g. `FST_ERR_BAD_URL`,
  `FST_ERR_ASYNC_CONSTRAINT`) for custom handling/logging.
- **`onError` hook** (Section 3/Hooks) is the documented place to add
  custom error logging separate from the final error-response handler.
- **Built-in logger**: the `logger`/`loggerInstance` options (Section 4)
  wire in Pino, Fastify's documented default logging library, as the
  primary observability/debugging surface for request-level logs.

Unresolved: whether fastify.dev hosts a dedicated "Debugging" guide (e.g.
covering `node --inspect`, VS Code launch configs, or a `debug`-namespace
usage) could not be confirmed — a WebSearch specifically for this returned
only tangential hits (a VS Code "Attach" debug-config mention surfaced via
search summarization, not verified against a primary fastify.dev page).
Treat "official debugging guidance" as **thin/could not fully verify**
beyond the warning-trace flags and hook/option mechanisms listed above.

## 16. Integration

[Source: https://fastify.dev/docs/latest/Guides/Database/] **Databases**:
official first-party plugins decorate the instance with a ready client —
`@fastify/mysql` (`fastify.mysql.query()`), `@fastify/postgres`
(`fastify.pg.query()`), `@fastify/redis` (`fastify.redis`),
`@fastify/mongodb` (`fastify.mongo.db.collection()`). The guide also shows
a documented custom-plugin pattern for wrapping other DB libraries/ORMs —
Knex, Prisma, and TypeORM are given as examples — via `fastify.decorate()`
plus an `onClose` hook for connection teardown, and mentions schema
migration tools (Postgrator for SQL, migrate-mongo for MongoDB) as
compatible options.

[Source: https://fastify.dev/docs/latest/Reference/Middleware/] **Express/
Connect middleware interop**: via `@fastify/express` (full Express
compatibility) or `@fastify/middie` (lighter/faster Express-style
middleware support) plus `fastify.use()`.

[Source: https://fastify.dev/docs/latest/Reference/TypeScript/] **TypeScript**:
first-class generics-based typing (`RouteGenericInterface` with `Body`,
`Querystring`, `Params`, `Headers`, `Reply`), with types propagating into
hooks like `preValidation`. Official **type providers** —
`@fastify/type-provider-json-schema-to-ts` and
`@fastify/type-provider-typebox` — derive TypeScript types directly from
JSON Schemas. Plugin authors extend Fastify's own types via TypeScript
declaration merging on `FastifyInstance`/`FastifyRequest`/`FastifyReply`;
`fastify-plugin` is recommended for correct type propagation. Requires
`@types/node`; `tsconfig` `target` should be `es2017`+ to avoid
deprecation warnings. Plain JS files can still get typed via JSDoc.

[Source: https://fastify.dev/docs/latest/Guides/Ecosystem/] **Documentation
tooling**: `@fastify/swagger`, `@fastify/swagger-ui`, `@fastify/openapi`.
**Auth**: `@fastify/auth`, `@fastify/basic-auth`, `@fastify/bearer-auth`,
`@fastify/jwt`, `@fastify/passport`. **Security middleware**:
`@fastify/helmet`, `@fastify/cors`, `@fastify/csrf-protection`,
`@fastify/rate-limit`, `@fastify/circuit-breaker`. **Request/response**:
`@fastify/cookie`, `@fastify/multipart`, `@fastify/formbody`,
`@fastify/compress`, `@fastify/etag`. **Static/proxying/realtime**:
`@fastify/static`, `@fastify/http-proxy`, `@fastify/websocket`,
`@fastify/sse`. **App structure**: `@fastify/autoload`, `@fastify/env`,
`@fastify/session`, `@fastify/view`. The docs distinguish these ~50+
Fastify-org-maintained "core" plugins from 200+ **community plugins**,
explicitly noting community plugins "are not maintained by the Fastify
team. Use them at your own discretion."

[Source: https://fastify.dev/docs/latest/Guides/Serverless/] **Deployment
platform integration** already detailed in Section 10: AWS Lambda (via
`@fastify/aws-lambda` or `@h4ad/serverless-adapter`), Google Cloud
Functions/Firebase (custom content-type parser required), Google Cloud
Run, Vercel (native template + "Fluid compute").

## 17. Production considerations

[Source: https://fastify.dev/docs/latest/Guides/Recommendations/]
Consolidating production guidance already detailed above: run behind a
reverse proxy for TLS/load-balancing/static-file duties; bind to `0.0.0.0`
(not the `127.0.0.1` default) so container orchestrators' health checks can
reach the app; size CPU allocation to the workload shape (favor more vCPU
per instance for low-latency, allow fractional/shared CPU for
high-throughput, but validate with load testing rather than assuming); it's
fine to run multiple Fastify instances inside one Node process for
resource-sharing; keep hot-path routes simple/static rather than
regex/constraint-heavy; define response schemas both for throughput and to
avoid leaking unintended fields.

[Source: https://fastify.dev/docs/latest/Reference/Server/] Production-
relevant server defaults worth calling out explicitly: `return503OnClosing`
defaults to `true` (in-flight/new requests get a 503 during graceful
shutdown rather than being accepted then dropped); `forceCloseConnections`
defaults to `"idle"` (only idle keep-alive sockets are force-closed on
`close()`, not active ones); `bodyLimit` defaults to 1MB — should be
reviewed for APIs accepting larger payloads; `pluginTimeout` (10s default)
bounds how long the app can take to boot before `listen()`/`ready()` fails.

[Source: https://fastify.dev/docs/latest/Reference/Errors/] Production
error-handling guidance: install a `setErrorHandler` that sanitizes any
`statusCode >= 500` error before it reaches the client, while allowing
deliberately-raised `< 500` errors and `FST_ERR_VALIDATION` errors through
unmodified — otherwise raw internal error text (including possible DB
query/schema detail) is sent to clients by default.

[Source: https://fastify.dev/docs/latest/Reference/LTS/] Production
version-support planning: track the 6-month "full support" + 6-month
"security-only" window per major version documented in the LTS reference,
and keep the Node.js runtime aligned to what the currently-deployed Fastify
major line was tested against (v5 → Node 20+; v4 line retiring 2025-06-30
per the docs, i.e., already past end-of-support as of this 2026-09-09
research date — **running Fastify v4 in production is therefore
documented as unsupported as of this research date**).

[Source: https://github.com/fastify/fastify/blob/main/SECURITY.md]
Production incident-response planning: know the official vulnerability-
reporting channel and documented SLA (triage ≤4 business days, patch
coordination + disclosure over up to ~90+90 days) so security findings in
Fastify itself or an `@fastify/*` plugin can be escalated correctly; note
that this policy explicitly does not cover your own application code or
third-party non-`@fastify` dependencies.
