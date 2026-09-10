# Sentry JavaScript/Node SDK — major-version breaking-change history (v7→v8→v9→v10)

Tier-2 deep reference. Loaded on demand from [`../SKILL.md`](../SKILL.md); not
part of the Tier-1 body per context-efficiency rule CE-3. Every entry below
carries the same `[Source: <url>]` markers used in `skill.yaml.source_references`
and traces to `research/technologies/sentry.md` (Sections 11 and 13).

No single consolidated SDK-version × runtime × framework compatibility matrix
exists on `docs.sentry.io`; this table was assembled from the migration-guide
series plus the current-install pages
[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/].
Treat that as a real, standing documentation gap, not an oversight in this
research.

## v7 → v8

[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/]

- Adopted OpenTelemetry as the tracing engine under the hood: "You do not need
  to know or understand what OpenTelemetry is in order to use Sentry."
- Introduced the `instrument.js`-first initialization-ordering requirement:
  Sentry must be required/imported before any other package, or
  "auto-instrumentation and modules like database monitoring, agent tracing,
  tracing may not work."
- Made performance auto-instrumentation automatic; removed
  `autoDiscoverNodePerformanceMonitoringIntegrations()`.
- Revamped the custom tracing API: removed `startTransaction` and
  `span.startChild`.
- Began deprecating the `Hub` API in favor of a new Scope API (`Hub`/
  `getCurrentHub()` retained in v8 but slated for later removal).
- Required manual `Sentry.withIsolationScope()` wrapping for request
  isolation in non-HTTP contexts.
- Raised the Node.js minimum to 14.18.0.

## v8 → v9

[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v8-to-v9/]

- Raised the Node.js minimum to 18.0.0 (18.19.1+ for ESM-only SDKs) and the
  TypeScript minimum to 5.0.4.
- Dropped support for Prisma below 6.x.
- Removed the ability to drop spans in `beforeSendSpan`.
- Removed `samplingContext.request` (replaced by `normalizedRequest`) and
  `transactionContext` from `samplingContext`.
- Changed `captureConsoleIntegration` to mark console messages as "handled"
  by default — a behavioral default change affecting downstream
  categorization/alerting, not just an API removal.
- Stopped `requestDataIntegration` from auto-setting the user from
  `request.user` under Express.
- Renamed `processThreadBreadcrumbIntegration` to `childProcessIntegration`.
- **Removed the previous Metrics API entirely** — a real, significant
  product-boundary change (the strongest evidence Sentry is not a
  Prometheus-style metrics platform), not a mere deprecation.
- Removed the `enableTracing` option (use `tracesSampleRate`); removed
  `autoSessionTracking`.
- Removed `getCurrentHub()`, `Hub`, `getCurrentHubShim()` (full removal of
  the Hub-era API line begun in v8).
- Removed `addOpenTelemetryInstrumentation()` (use the
  `openTelemetryInstrumentations` init option).
- Removed `debugIntegration`, `sessionTimingIntegration`, `nestIntegration`,
  `setupNestErrorHandler()`.
- Stopped publishing `@sentry/utils` (folded into `@sentry/core`); deprecated
  `@sentry/types`.

## v9 → v10

[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v9-to-v10/]

- Removed `BaseClient` (use `Client`).
- Removed `hasTracingEnabled` (use `hasSpansEnabled`).
- Removed the internal `logger`/`Logger` exports from `@sentry/core` (use
  `debug`/`SentryDebugLogger`).
- Moved experimental log config (`_experiments.enableLogs`,
  `_experiments.beforeSendLog`) to top-level `Sentry.init()` options — a
  config-shape breaking change for anyone still nesting them under
  `_experiments`.
- Bumped the SDK's internal OpenTelemetry dependency floor to **2.x/0.20x.x**
  and all OTel instrumentations to their latest versions; projects that
  cannot support OTel v2 are told to stay on v9 or use `@sentry/node-core`.
- Renamed the AWS Lambda Layer identifier to `SentryNodeServerlessSDKv10`,
  breaking any pinned reference to the old layer name.

## Unresolved

- Unresolved: a Python SDK (`sentry-sdk`) major-version migration guide, and
  a Python-specific breaking-changes history analogous to the series above,
  was not located in the underlying research pass
  [Source: research/technologies/sentry.md, Section 11/13]. `sentry-sdk`'s
  current version (2.69.1) implies at least one prior major bump (1.x→2.x),
  but its itemized breaking-change content is not confirmed.
