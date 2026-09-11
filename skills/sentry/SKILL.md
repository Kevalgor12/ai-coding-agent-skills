---
name: Sentry
description: >-
  Sentry-specific error monitoring, tracing, Session Replay, and trace-connected
  Logs — SDK init ordering, DSN mechanics, release/source-map workflow, layered
  PII scrubbing, and the JS SDK's OpenTelemetry-backed tracing (v8+). Use when
  @sentry/* (Node/browser/framework) or Python sentry-sdk is present, or the
  task names Sentry, fingerprinting, Session Replay, or Sentry Logs. Not for
  generic observability method or metrics/dashboards (use prometheus/grafana).
spec_version: "1.0"
---

## Purpose & scope

Apply Sentry correctly and version-appropriately: SDK architecture and
initialization ordering, the four product surfaces (errors, tracing, Session
Replay, Logs), DSN mechanics, the release/source-map workflow, and the JS
SDK's deep OpenTelemetry dependency. The generic signal-selection method,
PII-scrubbing pattern, and sampling-tuning guidance come from the parent skill
([observability](../observability/SKILL.md), `SK-QA-004`) and are not
repeated here — this skill adds Sentry-specific implementation depth only.

## When to use / When not to use

**Use** when an `@sentry/*` package or the Python `sentry-sdk` is present, a
Sentry DSN is configured, or the task names Sentry, issue fingerprinting,
Session Replay, Sentry Logs, release/source-map upload, or a Sentry SDK
migration. **Do not use** for generic observability method with no Sentry SDK
involved (`SK-QA-004`), metrics storage/PromQL (`SK-TECH-prometheus`),
dashboarding (`SK-TECH-grafana`), or vendor-neutral instrumentation design
with Sentry absent from the stack (`SK-TECH-opentelemetry`).

## Knowledge

**Four product surfaces, not one.** Errors are grouped into **issues** via
fingerprinting (owned by the parent skill). Tracing is built on **traces**
composed of **spans**; the older "transaction" concept is being superseded by
service-boundary "service spans," though transaction terminology still
appears throughout the SDK configuration surface
[Source: https://docs.sentry.io/concepts/key-terms/tracing/]. **Session
Replay** is a distinct third surface: "video-like reproductions of real user
sessions" capturing clicks, navigations, network requests, console output,
and errors, correlatable back to the errors/traces timeline
[Source: https://docs.sentry.io/product/session-replay/]. **Logs** are a
fourth, more recent surface: each log entry is "trace-connected" —
automatically linked to its active trace — and the docs frame this as
complementary, not a full application-log-management replacement: "not
everything in your application generates an error or requires full tracing"
[Source: https://docs.sentry.io/product/explore/logs/].

**The Sentry↔OpenTelemetry relationship is deep, not a passing integration.**
"The Sentry SDK uses OpenTelemetry under the hood" for the JS/Node line since
v8 — span/trace collection runs on top of the OTel SDK rather than a bespoke
tracer [Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/].
Existing OpenTelemetry instrumentation "will automatically be picked up by
Sentry without any further configuration," and even with Sentry's own tracing
turned off, "Sentry still connects to OpenTelemetry under the hood to ensure
that context isolation and trace propagation works correctly" — the OTel
dependency is load-bearing for basic scope/context correctness, not only span
capture [Source: https://docs.sentry.io/platforms/javascript/guides/node/opentelemetry/].
Sentry sets up OpenTelemetry automatically by default but also supports "your
own OpenTelemetry setup" for teams that want to own that configuration
directly (same source). See [`SK-TECH-opentelemetry`](../opentelemetry/SKILL.md)
for the standard itself. Official, directly-quoted Sentry integration guides
exist for Next.js, Express, and Fastify
[Source: https://docs.sentry.io/platforms/javascript/guides/nextjs/]
[Source: https://docs.sentry.io/platforms/javascript/guides/express/]
[Source: https://docs.sentry.io/platforms/javascript/guides/fastify/].

**DSN mechanics.** A DSN has the shape
`{PROTOCOL}://{PUBLIC_KEY}:{SECRET_KEY}@{HOST}{PATH}/{PROJECT_ID}`; the
`{SECRET_KEY}` segment is deprecated and ignored by current Sentry versions
[Source: https://docs.sentry.io/product/sentry-basics/dsn-explainer/]. See
Security below for the public/secret status this resolves.

**Release/source-map workflow.** A **release** is "a version of your code
that is deployed to an environment," set via `Sentry.init({ release })` and
commonly sourced from `process.env.npm_package_version` or CI
[Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/releases/].
Releases unlock source-map application to minified stack traces and commit
association for regression attribution (same source). The source-map upload
path defaults to **Debug IDs** injected into build output, via the Sentry
Wizard, dedicated bundler plugins (webpack/Rollup/Vite/esbuild), or a manual
`sentry-cli` upload
[Source: https://docs.sentry.io/platforms/javascript/sourcemaps/]. CI/CD
automation is documented via the official `getsentry/action-release@v3`
GitHub Action (requiring `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT`)
[Source: https://docs.sentry.io/product/releases/setup/release-automation/github-actions/],
with additional repository-integration support for Bitbucket Pipelines,
CircleCI, Jenkins, Netlify, and Travis CI
[Source: https://docs.sentry.io/product/releases/setup/release-automation/].

**PII-scrubbing architecture (layers, beyond the parent's general pattern).**
Scrubbing happens at up to three points: SDK-level `beforeSend`/
`beforeSendTransaction` hooks (redact before anything leaves the local
environment), server-side default scrubbing on arrival, and an optional
**Advanced Data Scrubbing** layer with customizable rules
[Source: https://docs.sentry.io/product/data-management-settings/scrubbing/].
An optional, organization-operated **Relay** component sits between the SDK
and Sentry's backend as a third layer, "scrub[bing] data in a central place
prior to sending it to Sentry" for organizations that cannot let PII leave
their own infrastructure at all
[Source: https://docs.sentry.io/product/relay/]. Unresolved: the exact
itemized list of field names/patterns redacted by the *default* server-side
scrubber was not extractable from the fetched docs
[Source: https://docs.sentry.io/product/data-management-settings/scrubbing/] —
do not invent this list; verify against current docs before relying on it.

**SDK major-version history.** JS SDK v9 **removed the Metrics API
entirely** (not deprecated) — the strongest documented evidence Sentry is not
a Prometheus-style metrics platform — and v10 **raised the SDK's internal
OpenTelemetry dependency floor to 2.x/0.20x.x**, directing projects that
cannot adopt OTel v2 to stay on v9 or use `@sentry/node-core`
[Source: https://docs.sentry.io/platforms/javascript/guides/node/migration/v9-to-v10/].
Current stable is JS SDK **10.74.0** (2026-09-09), with **11.0.0-beta.2**
in active beta; Python SDK is **2.69.1** on PyPI
[Source: https://github.com/getsentry/sentry-javascript/releases]
[Source: https://pypi.org/project/sentry-sdk/]. The full v7→v8→v9→v10
itemized breaking-change table lives in
[`references/js-sdk-breaking-changes.md`](references/js-sdk-breaking-changes.md)
(Tier-2 — loaded on demand).

## Decision framework

1. **Is Sentry's own tracing sufficient, or is OpenTelemetry's broader reach
   needed?** Sentry's tracing runs on OTel internally and auto-picks-up
   existing OTel instrumentation — for a Sentry-only stack with standard
   framework integrations, Sentry's own SDK setup is sufficient. Reach for a
   dedicated `SK-TECH-opentelemetry` setup when the org needs vendor-neutral
   instrumentation portable across backends, or spans from services/libraries
   Sentry doesn't auto-instrument.
2. **Sample-rate tuning under quota-per-event billing.** Every sampled error
   and transaction/span is a billable event regardless of issue grouping —
   start low and raise `sampleRate`/`tracesSampleRate` deliberately as
   traffic patterns become known, or use `tracesSampler` when different
   transaction types warrant different rates (e.g. auth flows sampled higher
   than high-volume low-value routes). Do not default to 100% in production.
3. **Eager vs. lazy profiling mode.** Eager (default) mode runs the profiler
   continuously, even with no active profiles, trading a constant CPU
   overhead for faster `startProfiler` calls
   [Source: https://docs.sentry.io/platforms/javascript/guides/node/profiling/].
   Prefer eager mode only where that latency matters and the CPU budget
   absorbs it; otherwise use a lazier/conditional profiling trigger.
4. **Simplest first:** if the actual need is "know when something breaks in
   production," SDK defaults (auto exception capture, default sampling) plus
   the framework error-handler wiring are often sufficient — don't reach for
   Session Replay, Logs, or custom tracing until a specific diagnostic gap
   justifies the added surface and quota cost.

## Engineering rules

- Initialize the SDK (`instrument.(js|mjs)`, imported/required first) before
  any other module import — required for auto-instrumentation to work, not
  merely a style preference.
- Wire the framework-specific error handler after routes but before other
  error middleware (`Sentry.setupExpressErrorHandler(app)`,
  `Sentry.setupFastifyErrorHandler(app)`), per the official integration
  guides.
- Set `release` at init time from a CI/build-injected version, not a
  hardcoded string, so source maps and commit association resolve correctly.
- Upload source maps (Debug IDs) as part of the same deploy that ships the
  build, before the corresponding error can occur — uploading after the fact
  leaves stack traces unresolved.
- Treat the DSN as public-safe to commit/embed, but treat `SENTRY_AUTH_TOKEN`
  (used for release creation and source-map upload) as a real secret.

## Trade-offs

Running Sentry's own OTel-backed tracing is simpler to operate (one SDK, one
init call) than standing up a separate OpenTelemetry Collector pipeline, at
the cost of coupling instrumentation lifecycle to Sentry's SDK release cadence
(e.g. the v10 OTel-v2 floor bump forces a coordinated upgrade). Eager
profiling trades constant CPU overhead for lower per-call latency; lazy/
conditional profiling avoids the standing cost but adds first-call latency
when profiling starts.

## Anti-patterns

- **Assuming `enabled: false` fully disables the SDK.** The docs are
  explicit: "Setting this to `enabled: false` doesn't prevent all overhead
  from Sentry instrumentation"
  [Source: https://docs.sentry.io/platforms/javascript/guides/node/configuration/environments/].
  The correct pattern for a zero-footprint environment (local dev, most test
  runs) is conditionally skipping the `Sentry.init()` call itself.
- **Initializing Sentry after other modules are imported/required.** Breaks
  auto-instrumentation for database monitoring, agent tracing, and tracing
  generally, since the SDK patches module internals at require/import time
  [Source: https://docs.sentry.io/platforms/javascript/guides/node/].
- **Treating Sentry as a general metrics or log-aggregation backend.** The
  Metrics API was removed entirely in v9 (not deprecated), and Logs retention
  is plan-tier-gated (7/14/30 days by tier) rather than a full log-management
  replacement — reach for `SK-TECH-prometheus`/dedicated log storage instead.
- **Shipping a release without uploading Debug IDs first**, or uploading
  source maps after the error already occurred — both leave production stack
  traces minified and undebuggable
  [Source: https://docs.sentry.io/platforms/javascript/guides/node/troubleshooting/].

## Security

**DSNs are designed to be public, not secret**: "DSNs are safe to keep public
because they only allow submission of new events and related event data; they
do not allow read access to any information"
[Source: https://docs.sentry.io/product/sentry-basics/dsn-explainer/]. A DSN
embedded in client-side JavaScript or a public repository is not, by itself,
a credential leak in Sentry's threat model — it grants write-only event
submission. This is distinct from `SENTRY_AUTH_TOKEN`, which is a real
credential and must be handled as a secret (see Engineering rules). PII
scrubbing is layered — SDK-level `beforeSend`/`beforeSendTransaction`,
server-side default scrubbing, an optional Advanced Data Scrubbing layer, and
an optional self-hosted Relay proxy as a third layer (see Knowledge above);
the exact default-scrubbed field list is Unresolved — verify against current
docs rather than assuming a specific list. Deeper cross-cutting threat
modeling is owned by `SK-QA-002` (security-engineering), not restated here.

## Performance

No numeric SDK performance-overhead benchmarks (CPU/memory/latency cost of
stack-trace capture, breadcrumb recording, or tracing) are documented; the
closest guidance is qualitative: "test prior to deployment" before adopting
tracing in a high-throughput environment
[Source: https://docs.sentry.io/platforms/javascript/guides/node/performance/].
The one named, specific trade-off is profiling's eager mode carrying a
constant CPU overhead in exchange for faster `startProfiler` calls
[Source: https://docs.sentry.io/platforms/javascript/guides/node/profiling/]
(see Decision framework #3). Sample-rate tuning is the primary lever for both
cost and event volume, since quota is consumed per-event
[Source: https://docs.sentry.io/pricing/quotas/] — deeper sampling-tuning
method is owned by the parent skill (`SK-QA-004`).

## Testing

No dedicated official guide or first-party Jest/pytest plugin exists for
testing Sentry-instrumented code. The documented pattern is conditionally
skipping `Sentry.init()` in test/local environments (the `enabled: false`
option alone is explicitly insufficient — see Anti-patterns), combined with
`debug: true` to verify at runtime that the SDK is (or isn't) sending data:
"The SDK may tell you why it is not sending any data"
[Source: https://docs.sentry.io/platforms/javascript/guides/node/troubleshooting/].
State this honestly as the real documented answer rather than implying a
richer first-party testing story exists. Broader test-strategy method is
owned by `SK-QA-001`.

## Failure handling

- If the Sentry SDK/version in use can't be determined, ask or explicitly
  state the version range the guidance assumes (JS SDK 8.x-10.x current
  stable, v11 in beta; Python SDK 2.x) rather than assuming "latest" silently.
- If shell is unavailable, output advisory `Sentry.init()`/`sentry_sdk.init()`
  config and CI workflow snippets, and state that no CLI upload, release
  creation, or migration was actually executed.

## Escalation

- A DSN rotation or organization/project-level security-setting change
  requires explicit user confirmation before execution.
- A request to use Sentry as a general-purpose metrics or log-management
  backend is escalated back to `SK-QA-004`/`SK-TECH-prometheus` rather than
  improvised, since Sentry's own Metrics API was removed and Logs retention
  is plan-tier-gated.

## Outputs & verification

- **Outputs:** SDK init/config (with correct instrument-first ordering),
  release/source-map CI wiring, and analysis of version-compatibility or
  migration impact.
- **Verify:** initialization precedes all other imports; PII-scrubbing hooks
  exist before `sendDefaultPii`/user-context is enabled; Debug IDs are
  uploaded before the corresponding deploy; every version-specific claim is
  tagged with the SDK range it applies to.

## References

- [`references/js-sdk-breaking-changes.md`](references/js-sdk-breaking-changes.md) — full v7→v8→v9→v10 itemized breaking-change table (Tier-2).
- Source list: see `skill.yaml.source_references` (Sentry official docs at `docs.sentry.io`/`develop.sentry.dev`, plus `github.com/getsentry/sentry-javascript/releases` and `pypi.org/project/sentry-sdk/` for version numbers; all retrieved 2026-09-10, via `research/technologies/sentry.md`).
- Parent skill: [observability](../observability/SKILL.md) (`SK-QA-004`) — signal-selection method, PII-scrubbing pattern, sampling-tuning guidance owned there, not repeated here.
- Related: [opentelemetry](../opentelemetry/SKILL.md) (`SK-TECH-opentelemetry`) — the instrumentation standard Sentry's JS SDK runs on internally since v8.
