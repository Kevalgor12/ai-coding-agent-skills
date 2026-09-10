# Sentry — Deep Technology Reference

Research date: 2026-09-10. Primary source: official Sentry documentation hosted at
`docs.sentry.io` (SDK/platform guides under `/platforms/`, product guides under
`/product/`, API reference under `/api/`, security/compliance material under
`/security-legal-pii/`, and pricing/quota material under `/pricing/`). Supplemented
by `develop.sentry.dev` (Sentry's internal engineering/self-hosted documentation,
an official Sentry-maintained site distinct from the customer-facing docs.sentry.io)
for self-hosted deployment specifics not covered on docs.sentry.io itself, and by
two official package-registry pages — `github.com/getsentry/sentry-javascript/releases`
and `pypi.org/project/sentry-sdk/` — for current SDK version numbers, since
docs.sentry.io's own guide pages do not consistently pin an exact version number in
prose (mirroring how the Node.js reference in this corpus cites `github.com/nodejs`
release artifacts alongside `nodejs.org` prose docs).

Citation format per project convention: `[Source: <url>] <claim>.` Claims not
found in official docs are marked "Not documented / could not verify."
Uncertain claims are marked "Unresolved: …". Inferences are labeled
"[Inference, not confirmed in docs]".

---

## 1. Core Concepts

[Source: https://docs.sentry.io/product/issues/] Sentry's issue model groups individual error events into "issues": "A typical application sends a large number of events to Sentry. You can think of an issue as a single bug or problem with your app. To make them manageable, we group similar events into issues based on a fingerprint." This fingerprint-based grouping lets teams see "how frequently a problem is happening and how many users it's affecting" instead of triaging every raw event individually.

[Source: https://docs.sentry.io/product/issues/] Billing/quota is measured at the event level, not the issue level: "Your quota is consumed by events, not issues. Issues are generated from your accepted error or transaction events" — meaning a single recurring bug generates many billable events even though it displays as one issue.

[Source: https://docs.sentry.io/concepts/key-terms/tracing/] Sentry's performance/tracing model is built on **traces** ("a record of a series of connected events and operations coming from your application," identified by a shared trace ID across services) composed of **spans** ("a named, timed operation that represents a part of the application workflow"). The docs note that the older "transaction" concept — "a specific unit that represents any event that your application sends to Sentry, like loading a web page or processing an API call" — is being superseded by service-boundary "service spans," though transaction terminology still appears throughout the SDK configuration surface (Section 4).

[Source: https://docs.sentry.io/product/session-replay/] Session Replay is documented as a third distinct product surface: "video-like reproductions of real user sessions" that capture "clicks, navigations, network requests, console output, and errors — all in context and synced to a timeline," and that link back to the other two surfaces by connecting "Errors, traces, network requests, and console logs...to the replay timeline so you can correlate what happened in the UI with what happened under the hood."

[Source: https://docs.sentry.io/product/explore/logs/] A fourth, more recently documented surface is **Logs**: sending, viewing, and querying "logs and parameters sent from your applications within Sentry," with each log entry "trace-connected" — automatically linked to its active trace so an investigator sees the log alongside the spans, errors, and other logs from the same request. The docs frame this as complementary rather than a full application-log-management replacement: "not everything in your application generates an error or requires full tracing."

[Source: https://docs.sentry.io/product/issues/] Distinguishing error monitoring from performance monitoring in practice: issues can originate from either "accepted error or transaction events," meaning the Issues stream ingests both error-type and performance-regression-type problems, while Session Replay (above) and Logs sit alongside as separate, correlatable surfaces rather than being folded into the Issues stream itself.

---

## 2. Architecture

[Source: https://docs.sentry.io/platforms/javascript/guides/node/] The SDK is initialized as early as possible in the process lifecycle — via a dedicated `instrument.(js|mjs)` file required/imported before any other module — because "auto-instrumentation and modules like database monitoring, agent tracing, tracing may not work" if initialization happens too late; this ordering requirement is a direct architectural consequence of how the SDK installs its instrumentation hooks.

[Source: https://docs.sentry.io/product/relay/] Between the SDK and Sentry's backend sits an optional **Relay** layer: Relay "acts as a middle layer between your application and sentry.io," letting organizations route SDK traffic through a self-operated proxy before it reaches Sentry's SaaS infrastructure. Relay's documented roles include a third layer of PII scrubbing ("Sentry already scrubs PII in two places: In the SDK before sending the event" and "Upon arrival on Sentry's infrastructure" — Relay "scrubs data in a central place prior to sending it to Sentry"), improving "event response time in regions with low bandwidth or limited connectivity," and acting as a proxy for organizations that need custom domain restrictions.

[Source: https://develop.sentry.dev/self-hosted/] Sentry's deployment architecture splits into **Sentry SaaS** (sentry.io, hosted and operated by Sentry) and **self-hosted Sentry** (organization-operated, deployed via "Docker and Docker Compose, along with a bash-based install and upgrade script"), with self-hosted characterized as "the Business plan without any software limitations and no paid tier," minus billing/payment features and a small number of features that are "impossible to be hosted by most people" (see Section 10).

[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/] Architecturally, the Node/JavaScript SDK line is "powered by OpenTelemetry under the hood" as of major version 8, meaning span/trace collection is implemented on top of the OpenTelemetry SDK rather than a bespoke Sentry-only tracer — see Section 16 for the documented OpenTelemetry interoperability this enables.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/enriching-events/breadcrumbs/] Context capture at the SDK layer is built from three complementary mechanisms: **breadcrumbs** ("a trail of events that happened prior to an issue," automatically recorded by integrations — e.g. browser SDKs record "clicks and key presses on DOM elements, XHR/fetch requests, console API calls, and all location changes" — or manually via `Sentry.addBreadcrumb()`), **scope** (the request/execution-isolated container that breadcrumbs, tags, and user context attach to — see the `withIsolationScope()` API referenced in Section 11's v7→v8 notes), and **tags** (key/value context set alongside events, searchable in the Sentry UI).

---

## 3. APIs

[Source: https://docs.sentry.io/platforms/javascript/guides/node/] **Node.js SDK** (`@sentry/node`, installed via `npm install @sentry/node`): initialized with `Sentry.init({ dsn: ... })`. Automatic capture covers uncaught exceptions and unhandled promise rejections by default; manual capture uses `Sentry.captureException(e)` for handled errors. Minimum supported Node.js version is 18.0.0, with `18.19.0` or `19.9.0`+ recommended for full `TracingChannel`-based future functionality.

[Source: https://docs.sentry.io/platforms/python/] **Python SDK** (`sentry-sdk`, installed via `pip install "sentry-sdk"`, with documented `uv`/`poetry` install variants): initialized with `sentry_sdk.init({ dsn: ... })` as early as possible in the application lifecycle (inside an `async` function for async programs, to keep instrumentation correctly scoped). Automatic capture is done through per-library **integrations** — the docs state the SDK "automatically enables integrations for many popular libraries," capturing operations like HTTP requests and database queries as spans. Manual/custom instrumentation for frameworks without a bundled integration uses `sentry_sdk.start_transaction()`.

[Source: https://docs.sentry.io/platforms/python/integrations/] The Python SDK's integration model is explicit: "The Sentry SDK uses integrations to hook into the functionality of popular libraries to automatically instrument your application." Documented auto-enabled web-framework integrations include Django, Flask, FastAPI, AIOHTTP, Bottle, Falcon, Pyramid, Quart, Sanic, Starlette, and Tornado; auto-enabled task-queue integrations include Celery, ARQ, huey, and RQ; Apache Airflow, Beam, and Spark require manual configuration. Integrations can be explicitly configured, e.g. `FlaskIntegration(transaction_style="url")`.

[Source: https://docs.sentry.io/api/events/] Beyond the SDKs, Sentry publishes a **Web API** for programmatic issue management, documented under an "Events & Issues" section with (among others) "List a Project's Issues," "List an Organization's Issues," "List a Project's Error Events," "Update an Issue" (resolution/ignore-state changes), "Bulk Mutate a List of Issues," "Bulk Mutate an Organization's Issues," and corresponding removal endpoints ("Remove an Issue," "Bulk Remove a List/Organization's Issues"). Not documented / could not verify: the exact authentication-token scopes required per endpoint were not extracted from the fetched excerpt — see Section 17 for the one documented token type observed elsewhere (an "Organization Token" used for release creation via `SENTRY_AUTH_TOKEN`).

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/] Manual vs. automatic instrumentation is also a configuration-level distinction on the JS/Node SDK: automatic instrumentation is toggled via the `integrations` array (default `[]`, extended by functions like `nodeProfilingIntegration()`), while manual reporting hooks (`captureException`, `addBreadcrumb`, `beforeSend`) give full application-level control over what gets sent.

---

## 4. Configuration

[Source: https://docs.sentry.io/product/sentry-basics/dsn-explainer/] Every Sentry project is configured via a **DSN** (Data Source Name), structured as `{PROTOCOL}://{PUBLIC_KEY}:{SECRET_KEY}@{HOST}{PATH}/{PROJECT_ID}` (example: `https://public@sentry.example.com/1`). The `{SECRET_KEY}` segment is explicitly deprecated: "The secret part of the DSN is optional and effectively deprecated. While clients will still honor it, if supplied, future versions of Sentry will entirely ignore it." See Section 7 for the documented public/secret status of the DSN as a whole.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/] JS/Node SDK core options: `dsn` (string, env var `SENTRY_DSN`; "If this is not set, the SDK will not send any events"); `environment` (string, env var `SENTRY_ENVIRONMENT`, defaults to `development` or `production` "depending on whether the application is packaged"); `release` (string, env var `SENTRY_RELEASE`; "Release names are strings, but some formats are detected by Sentry and might be rendered differently"); `debug` (boolean, default `false`).

[Source: https://docs.sentry.io/platforms/python/configuration/options/] Python SDK equivalents mirror the JS surface field-for-field: `dsn` (str, default `None`, env var `SENTRY_DSN`); `environment` (str, default `"production"`, env var `SENTRY_ENVIRONMENT`, "freeform"); `release` (str, default `None`, env var `SENTRY_RELEASE`, with automatic best-effort detection but manual configuration recommended); `debug` (bool, default `False`, env var `SENTRY_DEBUG`).

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/] Error-sampling: `sampleRate` (number, default `1.0`, "Configures the sample rate for error events, in the range of `0.0` to `1.0`"). Performance-tracing sampling: `tracesSampleRate` (number, env var `SENTRY_TRACES_SAMPLE_RATE`, "a number between `0` and `1`, controlling the percentage chance a given transaction will be sent to Sentry") and `tracesSampler` (a function receiving `samplingContext`, returning a `number | boolean`, for per-transaction-type sampling decisions — see Section 5). [Source: https://docs.sentry.io/platforms/python/configuration/options/] The Python SDK exposes the identical pair as `sample_rate` (float, default `1.0`) and `traces_sample_rate` (float, default `None`, "controlling the percentage chance a given transaction will be sent to Sentry").

[Source: https://docs.sentry.io/platforms/python/configuration/options/] `max_breadcrumbs` (int, default `100`) caps retained breadcrumb count per event on the Python SDK; the docs advise being "mindful of Sentry's maximum payload size constraints" when raising it. Not documented / could not verify: the equivalent default limit was not located on the JS/Node options page in this research pass.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/] `sendDefaultPii` (boolean, default `false`) is explicitly called out as deprecated on the JS/Node SDK: "`sendDefaultPii` is deprecated and will be removed in the next major version (v11). Use [`dataCollection`] instead." [Source: https://docs.sentry.io/platforms/python/configuration/options/] The Python SDK's `send_default_pii` (bool, default `None`) remains the current mechanism there: "If this flag is enabled, certain personally identifiable information (PII) is added by active integrations."

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/environments/] An `enabled` option exists to gate SDK sending behavior, but the docs carry an explicit caveat covered fully in Section 6/9: setting `enabled: false` "doesn't prevent all overhead from Sentry instrumentation," and the docs instead recommend conditionally calling `Sentry.init()` itself to fully disable the SDK.

---

## 5. Recommended Patterns

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/releases/] A **release** is documented as "a version of your code that is deployed to an environment," configured at init time (`Sentry.init({ release: "my-project-name@2.3.12" })`), commonly sourced from `process.env.npm_package_version` or a build/CI-injected environment variable. Releases unlock two major capabilities: "applying source maps to minified JavaScript to view original, untransformed source code," and associating deployed code with commit history so Sentry can "determine issues and regressions introduced in a new release" and "predict which commit caused an issue and who is likely responsible."

[Source: https://docs.sentry.io/platforms/javascript/sourcemaps/] The source-map workflow for readable production stack traces is documented via three paths: the **Sentry Wizard** (`npx @sentry/wizard@latest`, which handles login/project selection, package installation, and build-tool configuration), dedicated **bundler plugins** for webpack, Rollup, Vite, and esbuild, and a **manual CLI upload** path (`sentry-cli`) for other toolchains. Association between uploaded source maps and deployed minified code defaults to **Debug IDs** injected into build output, with legacy methods documented as a fallback.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/enriching-events/breadcrumbs/] Recommended breadcrumb usage: rely on automatic breadcrumbs from integrations for baseline coverage, add manual breadcrumbs (`Sentry.addBreadcrumb({ category, message, level, data })`, levels `"fatal"|"error"|"warning"|"log"|"info"|"debug"`) at meaningful application checkpoints (the docs' own example logs an authentication event), and use the `beforeBreadcrumb` hook in `Sentry.init()` to filter or redact individual breadcrumbs before they attach to an event.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/sampling/] Recommended tracing pattern: use uniform `tracesSampleRate` for "an even cross-section of transactions, no matter where in your app or under what circumstances they occur," but switch to `tracesSampler` when different transaction types need different treatment — e.g. sampling authentication transactions at a higher rate than low-value, high-volume ones — since the sampler function can both "sample different transactions at different rates" and "filter out some transactions entirely." Distributed-trace sampling decisions are inherited by default: "Whatever a transaction's sampling decision, that decision will be passed to its child spans and from there to any transactions they subsequently cause in other services," with the docs recommending against overriding this ("a broken trace will not include all your services").

[Source: https://docs.sentry.io/product/releases/] For CI/CD integration, notifying Sentry of new releases and associating commit metadata is documented as easiest "using one of our repository integrations," with the docs naming supported CI/CD platforms (see Section 17) and a manual fallback process for unsupported ones. Releases also enable deploy notifications: teams can "receive email notifications when your code gets deployed."

---

## 6. Anti-Patterns

[Source: https://docs.sentry.io/platforms/javascript/guides/node/data-management/sensitive-data/] Capturing PII without scrubbing is flagged across several concrete event locations the docs enumerate as risk areas: stack-locals (variable values captured in stack frames), breadcrumbs (log statements and database queries), user context, HTTP context and query strings, transaction names that embed user IDs, and HTTP spans. The documented mitigation is to scrub proactively in the `beforeSend`/`beforeSendTransaction` hooks — "We recommend using these hooks in the SDKs to **scrub any data before it is sent**, to ensure that sensitive data never leaves the local environment" — rather than depend solely on server-side scrubbing after the fact (see Section 7).

[Source: https://docs.sentry.io/platforms/javascript/guides/node/troubleshooting/] Not configuring source maps correctly is a documented, diagnosable failure mode: symptoms include "Your deployed code is missing Debug IDs" and, separately, uploaded artifacts not being associated because they weren't uploaded before the error occurred ("source maps not applying") — both leaving production stack traces minified and effectively undebuggable, directly undercutting the release/source-map workflow in Section 5.

[Source: https://docs.sentry.io/product/issues/] [Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/sampling/] Excessive sample rates are an anti-pattern with a direct cost consequence, since "your quota is consumed by events, not issues" — every sampled error and transaction is a billable event — and the sampling docs' own guidance is to "start with a low value and gradually increase it as you learn more about your traffic patterns and volume" rather than defaulting to 100% capture in production.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/environments/] Assuming `enabled: false` fully eliminates Sentry's runtime footprint is an anti-pattern the docs explicitly warn against: "Setting this to `enabled: false` doesn't prevent all overhead from Sentry instrumentation" — the documented correct pattern for fully disabling the SDK (e.g. in local development) is conditionally skipping the `Sentry.init()` call itself, not merely flipping `enabled`.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/] Initializing Sentry after other modules are imported/required is a documented anti-pattern specific to the Node SDK's instrumentation model: doing so means "auto-instrumentation and modules like database monitoring, agent tracing, tracing may not work," since the SDK patches module internals at require/import time.

---

## 7. Security

[Source: https://docs.sentry.io/product/sentry-basics/dsn-explainer/] **DSNs are designed to be public, not secret**: "DSNs are safe to keep public because they only allow submission of new events and related event data; they do not allow read access to any information." This directly resolves the common confusion the task flagged — a DSN embedded in client-side JavaScript or a public repository is not, by itself, a credential leak in Sentry's threat model, because it grants write-only event-submission access.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/data-management/sensitive-data/] PII scrubbing is layered at multiple points. At the SDK layer, `beforeSend`/`beforeSendTransaction` hooks are the documented mechanism for redacting fields "before it is sent, to ensure that sensitive data never leaves the local environment" (e.g. `delete event.user.email`), and the docs recommend structural avoidance over reactive scrubbing where possible — e.g. `Sentry.setUser({ id: user.id })` instead of sending an email address, or hashing identifying context before attaching it as a tag.

[Source: https://docs.sentry.io/product/relay/] At the backend layer, the docs describe Sentry scrubbing PII "in two places: In the SDK before sending the event" and "Upon arrival on Sentry's infrastructure," with self-hosted **Relay** available as an optional third, organization-controlled layer that "scrubs data in a central place prior to sending it to Sentry" for organizations that cannot let PII leave their own infrastructure at all.

[Source: https://docs.sentry.io/product/data-management-settings/scrubbing/] Server-side, Sentry documents two configurable scrubbing surfaces: a baseline **default data scrubbing** applied automatically to incoming events, and an **Advanced Data Scrubbing** feature "as an alternative way to redact sensitive information just before it is saved in Sentry," with customizable rules. Not documented / could not verify: the precise, itemized list of field names/patterns redacted by the default scrubber (e.g. whether `password`, `token`, `secret`, and credit-card-shaped values are named explicitly) was not extracted from the fetched excerpt of this page — a deeper crawl of the linked "Server-Side Data Scrubbing" sub-page would be needed to confirm the exact default field list.

[Source: https://docs.sentry.io/security-legal-pii/security/] Sentry's security/compliance program is documented to include SOC 2, ISO 27001, and Privacy Shield certifications, alongside published material on IP ranges, SSL protocols/cipher suites, and data retention (linked from the security-and-legal index page). Unresolved: the specific SSL/TLS protocol versions and cipher suites, and the exact data-retention windows by plan, were referenced by link from this index page but not independently fetched in this research pass.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/] `sendDefaultPii` gates whether default request/IP/user data gets attached to events at all (default `false`) — a security-relevant default-deny posture, though as noted in Section 4 this option is deprecated in favor of `dataCollection` in the JS SDK's v11 line.

---

## 8. Performance

[Source: https://docs.sentry.io/platforms/javascript/guides/node/performance/] The docs do not publish quantified SDK overhead numbers (no documented "X% CPU" or "Y ms per request" figures were found); the closest documented guidance is qualitative: "If you're adopting Tracing in a high-throughput environment, we recommend testing prior to deployment to ensure that your service's performance characteristics maintain expectations." Not documented / could not verify: numeric benchmarks for stack-trace-capture or breadcrumb-recording overhead specifically.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/profiling/] Profiling carries a documented, named trade-off in its default ("eager") mode: the profiler runs continuously "even when no profiles are active—this is good because it makes calls to `startProfiler` faster with the tradeoff of constant CPU overhead" — an explicit always-on-cost-for-lower-latency design choice, though again without a quantified percentage.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/sampling/] Sampling strategy is the primary documented performance/cost lever for tracing specifically: uniform `tracesSampleRate` for even coverage, or a `tracesSampler` function to sample selectively by transaction type/context — see Sections 5 and 17 for the corresponding recommended-pattern and production-tuning guidance.

[Source: https://docs.sentry.io/pricing/quotas/] Sampling is described as the mechanism that most directly reduces event volume: "If a sample rate is defined for the SDK, the SDK evaluates whether this event should be sent as a representative fraction of events, effectively limiting the number of errors and transactions/spans you send to Sentry" — positioning SDK-side sampling as a performance-adjacent, quota-adjacent control simultaneously.

---

## 9. Testing

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/environments/] The documented pattern for suppressing Sentry during test runs is not a dedicated testing feature but a configuration idiom: conditionally skip `Sentry.init()` based on environment ("To disable Sentry completely, depending on environment, call `Sentry.init` conditionally"), since the `enabled: false` option alone is explicitly documented as insufficient to eliminate all SDK instrumentation overhead (Section 6).

[Source: https://docs.sentry.io/platforms/javascript/guides/node/troubleshooting/] `debug: true` (JS/Node) / `debug=True` (Python, per Section 4) is the documented mechanism for surfacing what the SDK is doing at runtime, useful both for local development debugging and for verifying test-environment suppression is actually taking effect: "Set `debug: true` in the `Sentry.init()` options and observe your console output when you start your application. The SDK may tell you why it is not sending any data."

Not documented / could not verify: no dedicated official guide for "testing Sentry-instrumented application code" (analogous to how nodejs.md documents `node:test`) was located — no official Jest/pytest/Mocha plugin, fixture, or first-party testing-library integration for asserting on captured Sentry events was found on docs.sentry.io in this research pass. The practical guidance that exists is the environment-gated-`init()` pattern above plus `beforeSend`/`beforeSendTransaction` hooks that could, in principle, be used to intercept events in a test harness — but no such pattern is documented explicitly for testing purposes.

---

## 10. Deployment

[Source: https://develop.sentry.dev/self-hosted/] Sentry ships as two deployment models. **SaaS** (sentry.io) is fully hosted by Sentry. **Self-hosted** Sentry is deployed by the organization itself via "Docker and Docker Compose, along with a bash-based install and upgrade script," with documented minimum resource requirements of "4 CPU Cores," "16 GB RAM + 16 GB swap," and "20 GB Free Disk Space." Installation is `git clone` the self-hosted repo, run `./install.sh`, then `docker compose up --wait`, exposing Sentry on port 9000 by default.

[Source: https://develop.sentry.dev/self-hosted/] Feature parity between the two models is documented as near-complete, with self-hosted characterized as "the Business plan without any software limitations and no paid tier." Documented gaps specific to self-hosted: billing/payment features (pricing tiers, spike protection, spend allocation), closed-source AI/ML features ("Seer and other AI & ML features, as these are currently closed source"), self-managed rather than Sentry-selected data storage location, and reduced stack-trace-resolution capability for mobile/gaming platforms "due to licensing restrictions with Apple, Sony, and Nintendo."

[Source: https://develop.sentry.dev/self-hosted/] Self-hosted Sentry is licensed under the **FSL (Functional Source License)**, a Fair Source license that "becomes literally open source under the Apache 2.0 license after 2 years" per version.

[Inference, not confirmed in docs] Because self-hosted Sentry's own installer is Docker-Compose-based, the multi-stage-build, non-root-user, and PID-1/init-wrapper container practices this library has already researched for Node.js/Docker (see `research/technologies/nodejs.md` Section 10) are relevant background for anyone operating a self-hosted Sentry stack, but docs.sentry.io/develop.sentry.dev do not themselves restate that Docker-best-practices guidance — it would need to be inferred/cross-applied, not cited as Sentry's own documented advice.

---

## 11. Migration

[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/] The JavaScript/Node SDK line publishes a per-major-version migration guide series: 4.x→5.x/6.x, 6.x→7.x, 7.x→8.x, 8.x→9.x, 9.x→10.x, and (per the version data in Section 12) a 10.x→11.x guide is now also published, indicating v11 has moved from beta toward general availability since this page was last generated.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/] **v7→v8**: adopted OpenTelemetry as the tracing engine under the hood ("You do not need to know or understand what OpenTelemetry is in order to use Sentry"); introduced the `instrument.js`-first initialization ordering requirement (Section 2/6); made performance auto-instrumentation automatic, removing `autoDiscoverNodePerformanceMonitoringIntegrations()`; revamped the custom tracing API, removing `startTransaction`/`span.startChild`; began deprecating the `Hub` API in favor of a new Scope API (`Hub`/`getCurrentHub()` retained but slated for later removal); required manual `Sentry.withIsolationScope()` wrapping for request isolation in non-HTTP contexts; raised the Node.js minimum to 14.18.0.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v8-to-v9/] **v8→v9**: raised the Node.js minimum to 18.0.0 (18.19.1+ for ESM-only SDKs) and the TypeScript minimum to 5.0.4; dropped support for Prisma below 6.x; removed the ability to drop spans in `beforeSendSpan`; removed `samplingContext.request` (replaced by `normalizedRequest`); changed `captureConsoleIntegration` to mark console messages as handled by default; stopped `requestDataIntegration` from auto-setting the user from `request.user` under Express; renamed `processThreadBreadcrumbIntegration` to `childProcessIntegration`; **removed the previous Metrics API entirely**; removed `transactionContext` from `samplingContext`; removed the `enableTracing` option (use `tracesSampleRate`); removed `autoSessionTracking`; removed `getCurrentHub()`/`Hub`/`getCurrentHubShim()`; removed `addOpenTelemetryInstrumentation()` (use the `openTelemetryInstrumentations` init option); removed `debugIntegration`, `sessionTimingIntegration`, `nestIntegration`, `setupNestErrorHandler()`; stopped publishing `@sentry/utils` (merged into `@sentry/core`); deprecated `@sentry/types`.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v9-to-v10/] **v9→v10**: removed `BaseClient` (use `Client`); removed `hasTracingEnabled` (use `hasSpansEnabled`); removed the internal `logger`/`Logger` exports from `@sentry/core` (use `debug`/`SentryDebugLogger`); moved `_experiments.enableLogs`/`_experiments.beforeSendLog` to top-level `Sentry.init()` options; bumped all OpenTelemetry dependencies to 2.x/0.20x.x and all OTel instrumentations to their latest versions (projects that cannot support OTel v2 are told to stay on v9 or use `@sentry/node-core`); renamed the AWS Lambda Layer identifier to `SentryNodeServerlessSDKv10`.

Not documented / could not verify: a Python SDK major-version migration guide (analogous to the JS `v7-to-v8`-style series) was not fetched in this research pass — Unresolved: whether `sentry-sdk`'s own major-version bumps (the package is currently at 2.x per Section 12) carry an equivalently detailed, itemized breaking-change guide was not confirmed.

---

## 12. Version Information

[Source: https://github.com/getsentry/sentry-javascript/releases] As of this research, the current stable release of the Sentry JavaScript SDK monorepo (covering `@sentry/node`, `@sentry/browser`, and framework packages) is **10.74.0** (released 2026-09-09), with a **11.0.0-beta.2** pre-release also published, indicating v11 is in active beta ahead of general availability.

[Source: https://pypi.org/project/sentry-sdk/] The current stable release of the Python SDK (`sentry-sdk` on PyPI) is **2.69.1** (released 2026-09-08). Its package classifiers declare support for Python 3.6 through 3.15 (`Requires-Python >=3.6`), though see Section 13 for the specific tightened minimums Sentry has applied to related tooling (e.g. Node.js/TypeScript minimums on the JS line) — no equivalent narrowed Python-version floor beyond the classifier list was found for `sentry-sdk` itself in this pass.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/] The JS/Node SDK's documented Node.js runtime requirement is a minimum of **18.0.0**, with `18.19.0`+ or `19.9.0`+ recommended "for optimal support and future `TracingChannel` features" — consistent with the v8→v9 migration guide's statement (Section 11) that Node 18.0.0 became the enforced floor starting at SDK v9.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v9-to-v10/] SDK v9→v10 additionally bumped the SDK's internal OpenTelemetry dependency floor to 2.x/0.20x.x — a version-compatibility constraint for anyone pinning OTel packages alongside the Sentry SDK rather than a language/runtime constraint per se.

Not documented / could not verify: docs.sentry.io does not appear to publish a single consolidated version-compatibility matrix (SDK version × language runtime version × framework version) in one place; the version floors documented above were assembled from the migration-guide series (Section 11) and the current-SDK install pages rather than one authoritative table.

---

## 13. Breaking Changes

VERSION SENSITIVITY — Sentry JavaScript/Node SDK v9.0.0, [Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v8-to-v9/]:
- Node.js minimum raised to 18.0.0; TypeScript minimum raised to 5.0.4; Prisma <6.x dropped.
- **Metrics API removed entirely** — the previously-shipped custom-metrics feature was deleted from the SDK, not merely deprecated.
- Multiple Hub-era APIs fully removed: `getCurrentHub()`, `Hub`, `getCurrentHubShim()`.
- `enableTracing` and `autoSessionTracking` options removed; `transactionContext` and `request` removed from `samplingContext` (the latter replaced by `normalizedRequest`).
- `@sentry/utils` stopped being published (folded into `@sentry/core`); `@sentry/types` deprecated.
- Behavioral default change: `captureConsoleIntegration`-captured console messages are now marked "handled" by default, changing how they're categorized/alerted on downstream.

VERSION SENSITIVITY — Sentry JavaScript/Node SDK v10.0.0, [Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v9-to-v10/]:
- `BaseClient` removed (use `Client`); `hasTracingEnabled` removed (use `hasSpansEnabled`).
- Internal `logger`/`Logger` exports removed from `@sentry/core`.
- Experimental log config (`_experiments.enableLogs`, `_experiments.beforeSendLog`) promoted out of the experimental namespace to top-level `Sentry.init()` options — a config-shape breaking change for anyone still nesting them under `_experiments`.
- OpenTelemetry dependency floor raised to 2.x/0.20x.x; projects unable to move to OTel v2 are directed to stay on v9 or adopt `@sentry/node-core`.
- AWS Lambda Layer renamed to `SentryNodeServerlessSDKv10`, breaking any pinned reference to the old layer name.

VERSION SENSITIVITY — Sentry JavaScript/Node SDK v8.0.0, [Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/]:
- Node.js minimum raised to 14.18.0.
- `startTransaction` and `span.startChild` removed from the custom tracing API (replaced by the revamped v8 tracing API).
- `autoDiscoverNodePerformanceMonitoringIntegrations()` removed (auto-instrumentation now automatic).
- Initialization-ordering requirement introduced: Sentry must be required/imported before any other package, or "auto-instrumentation and modules like database monitoring, agent tracing, tracing may not work."

Not documented / could not verify: a Python SDK breaking-changes list by major version was not independently fetched in this pass (see Section 11's unresolved item).

---

## 14. Limitations

[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v8-to-v9/] Sentry is **not** a general-purpose metrics platform in the Prometheus/OpenTelemetry-metrics sense: its own custom Metrics API was shipped and then "removed entirely" in the v8→v9 SDK migration, a documented retreat from that surface area rather than an expansion of it. [Source: https://docs.sentry.io/product/explore/logs/] Sentry's newer **Logs** feature is documented as trace-connected structured application logging, not a general log-aggregation/retention platform — retention is explicitly plan-tier-gated ("Developer: 7 days | Team: 14 days | Business: 30 days"), a materially shorter and coarser retention model than dedicated logging platforms typically offer. [Inference, not confirmed in docs] Taken together, these two facts support treating Sentry primarily as an error-monitoring/APM/session-replay platform with adjacent, narrower logging and no independent time-series-metrics product — but no single docs.sentry.io page states this positioning against Prometheus or OpenTelemetry Metrics by name; this framing is inferred from the two removal/scoping facts above, not quoted directly.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/sampling/] [Source: https://docs.sentry.io/pricing/quotas/] Sampling is a real, documented limitation on completeness: when `sampleRate`/`tracesSampleRate` is below `1.0`, only a fraction of errors/transactions is sent — "the SDK evaluates whether this event should be sent as a representative fraction of events" — meaning any specific individual error or trace may simply never reach Sentry by design, not due to a bug. [Source: https://docs.sentry.io/platforms/javascript/guides/node/troubleshooting/] Separately, event delivery can also silently stop for quota-exhaustion reasons unrelated to sampling: the documented troubleshooting checklist for "why isn't my error showing up" includes checking whether "You may have ran out of quota."

[Source: https://develop.sentry.dev/self-hosted/] Self-hosted deployments carry documented feature limitations relative to SaaS (Section 10): no billing/spend-management tooling, no closed-source AI/ML ("Seer") features, and licensing-restricted reduced stack-trace resolution for mobile/console gaming platforms due to third-party (Apple/Sony/Nintendo) licensing terms.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/environments/] The `enabled: false` option is a documented partial-only mitigation, not a full opt-out: it stops event sending but "doesn't prevent all overhead from Sentry instrumentation," a limitation directly relevant to environments (tests, benchmarks) that need zero SDK footprint (Section 9).

---

## 15. Debugging

[Source: https://docs.sentry.io/platforms/javascript/guides/node/troubleshooting/] The SDK's own debug mode is enabled via `debug: true` (JS/Node) / `debug=True` (Python): "The SDK may tell you why it is not sending any data" once console output is observed at startup.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/troubleshooting/] The documented troubleshooting sequence for "why isn't my error showing up in Sentry" is: (1) confirm a DSN is configured and passed to the `dsn` option in `Sentry.init()`; (2) if the DSN comes from an environment variable, confirm it's set in every relevant environment and correctly framework-prefixed (e.g. `NEXT_PUBLIC_` for values that must reach the Next.js client bundle); (3) "Check that you have disabled any ad-blockers," since browser ad-blockers commonly block Sentry's ingest endpoints; (4) check the Sentry Stats/Subscription pages for quota exhaustion.

[Source: https://docs.sentry.io/platforms/javascript/sourcemaps/] Source-map-specific debugging surfaces two named failure signatures: "Your deployed code is missing Debug IDs" (build output wasn't stamped with the Debug ID the SDK relies on for association) and source maps simply "not applying" because artifacts weren't uploaded to Sentry before the corresponding error occurred.

---

## 16. Integration

[Source: https://docs.sentry.io/platforms/javascript/guides/nextjs/] **Next.js**: official setup runs `npx @sentry/wizard@latest -i nextjs`, which can enable Error Monitoring, Tracing, and Session Replay during the wizard flow. It generates environment-scoped instrumentation files — `instrumentation-client.ts` (browser), `sentry.server.config.ts` (Node.js server), `sentry.edge.config.ts` (edge runtime) — registered through a central `instrumentation.ts`, and wraps `next.config.ts` in `withSentryConfig(...)` to enable automatic source-map upload, a **tunnel route** (`/sentry-tunnel`, to route SDK traffic around ad-blockers — connective tissue with the ad-blocker troubleshooting item in Section 15), organization/project slug configuration, an auth token for source-map upload, and silent mode for CI.

[Source: https://docs.sentry.io/platforms/javascript/guides/express/] **Express**: `npm install @sentry/node` (plus `@sentry/profiling-node` for profiling), with the same `instrument.js`-first ordering requirement (Section 2). Error handling is wired via `Sentry.setupExpressErrorHandler(app)`, which the docs say to "add ... after all routes, but before any other error-handling middlewares are defined." No separate `expressIntegration()` call is documented as required — Express instrumentation is picked up automatically once the SDK is initialized early enough.

[Source: https://docs.sentry.io/platforms/javascript/guides/fastify/] **Fastify**: identical package install and `instrument.js`-first ordering; ESM projects load it via `node --import ./instrument.mjs app.mjs` (requiring Node 18.19.0+, consistent with the version guidance in Section 12). Error handling is wired via `Sentry.setupFastifyErrorHandler(app)`, called after requiring Fastify.

[Source: https://docs.sentry.io/platforms/javascript/guides/node/opentelemetry/] **OpenTelemetry**: "The Sentry SDK uses OpenTelemetry under the hood" for the Node SDK line (consistent with the v7→v8 architecture change in Sections 2/11). Any existing OpenTelemetry instrumentation that emits spans "will automatically be picked up by Sentry without any further configuration." Even when Sentry's own tracing is not explicitly enabled, "Sentry still connects to OpenTelemetry under the hood to ensure that context isolation and trace propagation works correctly" — i.e., the OTel dependency is load-bearing for basic scope/context correctness, not only for span capture. Sentry sets up OpenTelemetry automatically by default but also documents supporting "your own OpenTelemetry setup" for teams that want to own that configuration directly — this is the specific, citable OTel-compatibility connective tissue relevant to the sibling OpenTelemetry research in this same batch.

---

## 17. Production Considerations

[Source: https://docs.sentry.io/pricing/quotas/] Sample-rate tuning is documented as a primary, efficient lever for cost control at scale: SDK-side sampling (`sampleRate`/`tracesSampleRate`/`tracesSampler`) is listed early among quota-management strategies, on the logic that it "effectively limit[s] the number of errors and transactions/spans you send to Sentry" before they ever become billable events; dedicated "Manage Your Error Quota" and "Manage Your Span Quota" guides are referenced for deeper tuning per event type.

[Source: https://docs.sentry.io/product/releases/setup/release-automation/github-actions/] For CI/CD-integrated release/deploy tracking, Sentry documents an official GitHub Action — `getsentry/action-release@v3` ("Sentry Release GitHub Action," described as automating "Sentry release management in GitHub with just one step") — requiring the environment/secret values `SENTRY_AUTH_TOKEN` (an Organization Token), `SENTRY_ORG`, and `SENTRY_PROJECT` (optionally `SENTRY_URL` for self-hosted instances), with a documented workflow shape:
```yml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
- name: Create Sentry release
  uses: getsentry/action-release@v3
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
    SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
  with:
    environment: production
    release: "v1.3.4"
```
[Source: https://docs.sentry.io/product/releases/] The action also accepts a `sourcemaps` parameter for uploading source maps as part of the same release step. [Inference, not confirmed in docs] This slots directly into the general GitHub Actions patterns already covered elsewhere in this library's research corpus — release creation as one job step gated on the same triggers (push to main, tag creation) a deployment workflow would already use — though Sentry's own docs describe the action in isolation rather than as part of a worked end-to-end deployment pipeline.

[Source: https://docs.sentry.io/product/releases/setup/release-automation/] Beyond GitHub Actions, Sentry documents release automation support for five additional CI/CD platforms: Bitbucket Pipelines, CircleCI, Jenkins, Netlify, and Travis CI, each via "repository integrations" that notify Sentry of new releases and supply commit metadata; unsupported platforms fall back to a documented manual commit-data-submission process.

[Source: https://docs.sentry.io/product/alerts/] Alert/notification routing is handled by a unified **Alerts** system (not split into separate "issue alerts" vs. "metric alerts" products per the fetched page): rules combine **Triggers** ("an action that must occur for the Alert to run," all issue-state-based, evaluated as `ANY`), **Filters** ("conditions that must be met for the Alert to run," groupable as `ANY` or `ALL`), and **Actions** ("run when triggers and filters match"). Documented notification integrations span chat (Slack, Microsoft Teams, Discord), email, on-call tooling (PagerDuty, Opsgenie), and issue trackers (Jira, Azure DevOps, Linear), plus generic webhooks — with the docs' own operational advice being to keep alerts "valuable and not too noisy" via deliberate filter/trigger scoping.

[Source: https://develop.sentry.dev/self-hosted/] For teams running self-hosted Sentry in production, the documented minimum footprint (4 CPU cores, 16 GB RAM + 16 GB swap, 20 GB free disk) is a starting-point sizing baseline, not a validated production-scale figure — the docs do not publish a separate, larger "production-scale" sizing table distinct from the install-time minimum in the excerpt fetched here.

---

## Unresolved Items (Summary)

- Unresolved: the precise, itemized list of field names/patterns redacted by Sentry's *default* server-side data scrubber (as opposed to the SDK-side `beforeSend` pattern and the opt-in Advanced Data Scrubbing rules, both of which are documented in detail) was not extracted from the fetched page content — [Source: https://docs.sentry.io/product/data-management-settings/scrubbing/] only confirms that such a default exists and that Advanced Data Scrubbing is a separate, configurable layer.
- Unresolved: a Python SDK (`sentry-sdk`) major-version migration guide, and a Python-specific breaking-changes history analogous to the detailed JS v7→v8/v8→v9/v9→v10 series documented in Sections 11 and 13, was not located/fetched in this research pass.
- Unresolved: the exact SSL/TLS protocol versions, cipher suites, and plan-by-plan data-retention windows referenced from the `security-legal-pii` index page were not independently fetched.
- Unresolved: whether docs.sentry.io publishes a single consolidated SDK-version × language-runtime × framework-version compatibility matrix; version floors here were assembled from multiple pages rather than one authoritative table.
- Not documented / could not verify: numeric SDK performance-overhead benchmarks (CPU/memory/latency cost of stack-trace capture, breadcrumb recording, or tracing) — only qualitative guidance ("test before high-throughput adoption") and one named trade-off (eager profiler mode's constant CPU overhead) were found.
- Not documented / could not verify: a dedicated official guide or first-party plugin for testing Sentry-instrumented application code (asserting on captured events in Jest/pytest/etc.) — the closest documented pattern is conditional `Sentry.init()` skipping plus `debug: true` for verifying that behavior.
- Not documented / could not verify: exact authentication-token scopes required per Sentry Web API endpoint (Section 3) beyond the one "Organization Token" reference found in the release-automation/GitHub Actions context.
- [Inference, not confirmed in docs] Sentry's positioning as "not a metrics/logging platform in the Prometheus/OpenTelemetry sense" (Section 14) is inferred from two separate documented facts — the SDK's Metrics API being removed entirely in v9, and Logs' plan-tier-gated 7/14/30-day retention — rather than from any single page that states this boundary explicitly by name-checking Prometheus or OpenTelemetry Metrics.
- Framework/OpenTelemetry connective tissue that **was** resolved with a direct quote (flagged here since the task called out its importance for the parallel OpenTelemetry research pass): [Source: https://docs.sentry.io/platforms/javascript/guides/node/opentelemetry/] "The Sentry SDK uses OpenTelemetry under the hood," existing OTel instrumentation is auto-picked-up, and Sentry still relies on OTel for context/trace-propagation correctness even when Sentry's own tracing is off; Next.js/Express/Fastify all have official, quoted Sentry integration guides (Section 16) with no gaps.

---

## Sources Consulted (full list)

- https://docs.sentry.io/product/issues/ — issue/event grouping, fingerprinting, quota-per-event model
- https://docs.sentry.io/concepts/key-terms/tracing/ — tracing key terms: traces, spans, transactions
- https://docs.sentry.io/product/session-replay/ — Session Replay product overview
- https://docs.sentry.io/product/explore/logs/ — Sentry Logs product overview and retention-by-plan
- https://docs.sentry.io/platforms/javascript/guides/node/ — Node.js SDK overview, install, init, capture
- https://docs.sentry.io/platforms/python/ — Python SDK overview, install, init, capture
- https://docs.sentry.io/platforms/python/integrations/ — Python SDK framework/library integrations
- https://docs.sentry.io/platforms/python/configuration/options/ — Python SDK configuration options reference
- https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/ — JS/Node SDK configuration options reference
- https://docs.sentry.io/platforms/javascript/guides/node/configuration/releases/ — release configuration and purpose
- https://docs.sentry.io/platforms/javascript/guides/node/configuration/sampling/ — tracing sample-rate/sampler configuration
- https://docs.sentry.io/platforms/javascript/guides/node/configuration/environments/ — environment option, enabled option, disabling the SDK
- https://docs.sentry.io/platforms/javascript/sourcemaps/ — source map upload workflow, Debug IDs
- https://docs.sentry.io/platforms/javascript/guides/node/enriching-events/breadcrumbs/ — breadcrumbs concept and API
- https://docs.sentry.io/platforms/javascript/guides/node/data-management/sensitive-data/ — PII scrubbing guidance, beforeSend pattern
- https://docs.sentry.io/platforms/javascript/guides/node/performance/ — SDK performance/high-throughput guidance
- https://docs.sentry.io/platforms/javascript/guides/node/profiling/ — profiler overhead trade-off
- https://docs.sentry.io/platforms/javascript/guides/node/troubleshooting/ — debug mode, "why isn't my error showing up" checklist
- https://docs.sentry.io/platforms/javascript/guides/node/migration/ — JS SDK migration-guide series index
- https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/ — v7→v8 breaking changes
- https://docs.sentry.io/platforms/javascript/guides/node/migration/v8-to-v9/ — v8→v9 breaking changes
- https://docs.sentry.io/platforms/javascript/guides/node/migration/v9-to-v10/ — v9→v10 breaking changes
- https://docs.sentry.io/platforms/javascript/guides/node/opentelemetry/ — Node SDK/OpenTelemetry relationship
- https://docs.sentry.io/platforms/javascript/guides/nextjs/ — official Next.js integration guide
- https://docs.sentry.io/platforms/javascript/guides/express/ — official Express integration guide
- https://docs.sentry.io/platforms/javascript/guides/fastify/ — official Fastify integration guide
- https://docs.sentry.io/product/sentry-basics/dsn-explainer/ — DSN structure and public/secret status
- https://docs.sentry.io/product/relay/ — Relay architecture and PII-scrubbing layering
- https://docs.sentry.io/product/data-management-settings/scrubbing/ — server-side default and advanced data scrubbing
- https://docs.sentry.io/security-legal-pii/security/ — security/compliance program index (SOC2, ISO 27001)
- https://docs.sentry.io/api/events/ — Web API issue-management endpoints
- https://docs.sentry.io/product/releases/ — release tracking, commit association, deploy notifications
- https://docs.sentry.io/product/releases/setup/release-automation/ — CI/CD release-automation platform list
- https://docs.sentry.io/product/releases/setup/release-automation/github-actions/ — getsentry/action-release GitHub Action
- https://docs.sentry.io/product/alerts/ — alert rules, triggers/filters/actions, notification integrations
- https://docs.sentry.io/pricing/quotas/ — quota consumption, sampling's effect on billable volume
- https://develop.sentry.dev/self-hosted/ — self-hosted vs. SaaS deployment, licensing, minimum requirements
- https://github.com/getsentry/sentry-javascript/releases — current JS SDK version (10.74.0 stable / 11.0.0-beta.2)
- https://pypi.org/project/sentry-sdk/ — current Python SDK version (2.69.1) and Python-version classifiers
