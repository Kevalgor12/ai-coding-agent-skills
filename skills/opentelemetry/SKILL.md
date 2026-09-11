---
name: OpenTelemetry
description: >-
  OpenTelemetry-specific instrumentation via the API/SDK and Collector —
  OTLP protocol, W3C Trace Context propagation, semantic conventions, and
  the per-language/per-signal stability matrix (e.g. JS/Python logs still
  Development). Use when instrumenting code with OpenTelemetry or
  configuring/deploying the Collector. Not for signal-selection method or
  cardinality/PII/alerting synthesis (use observability), or
  backend-specific config (use prometheus/grafana/sentry).
spec_version: "1.0"
---

## Purpose & scope

Instrument code with the OpenTelemetry API/SDK and operate the
OpenTelemetry Collector correctly for the specific per-language,
per-signal stability level actually in use. The generic method for
*which signal to use and why*, cardinality/PII discipline, and
alert-design belong to the parent skill,
[observability](../observability/SKILL.md) (`SK-QA-004`) — this skill
adds OpenTelemetry's own implementation mechanics on top of that.

## When to use / When not to use

**Use** when instrumenting a service with the OpenTelemetry API/SDK
(traces, metrics, or logs), configuring/deploying/troubleshooting the
Collector, or migrating instrumentation off OpenTracing/OpenCensus.
**Do not use** for deciding which signal fits a diagnostic need or
designing alerting/cardinality/PII discipline in the abstract (that's
`observability`); for Prometheus-only PromQL/scrape-config work with no
OpenTelemetry involved (`prometheus`); for Grafana dashboards/alerting
with no OTLP ingestion (`grafana`); or for Sentry SDK/issue-triage work
not going through OpenTelemetry (`sentry`).

## Knowledge

**Architecture — three distinct pieces, two of them inside your
application and one outside it.** The **API** "defines data types and
operations for generating and correlating tracing, metrics, and logging
data"; the **SDK** "defines requirements for a language-specific
implementation of the API" (configuration, processing, exporting); the
**Collector** is "a vendor-agnostic proxy that can receive, process, and
export telemetry data," running as a standalone infrastructure
component, not embedded in application code
[Source: https://opentelemetry.io/docs/concepts/components/]. Data flows:
instrumentation (auto- or manual) generates data via the API → the SDK
processes it (sampling, batching, resource attachment) and hands it to
an exporter → the exporter sends it to a backend directly or, more
commonly in production, to a Collector, which further processes and
re-exports it [Source: https://opentelemetry.io/docs/concepts/components/].
Two instrumentation approaches are documented as **complementary, not
sequential**: zero-code (auto-) instrumentation for baseline
library/framework telemetry without source changes, and code-based
(manual) instrumentation for application-specific logic the auto layer
can't see — "You can use both solutions simultaneously"
[Source: https://opentelemetry.io/docs/concepts/instrumentation/].

**OTLP is the wire protocol, Stable for the signals that matter.** OTLP
moves telemetry from SDKs/Collectors to Collectors/backends. It is
Stable for trace, metric, and log signals (still Development for the
newer profiles signal), and supports gRPC (Protobuf, default port
**4317**) and HTTP (binary or JSON-encoded Protobuf, default port
**4318**) [Source: https://opentelemetry.io/docs/specs/otlp/]. Over HTTP,
implementations SHOULD fall back to HTTP/1.1 if HTTP/2 can't be
established, and JSON encoding deviates from default proto3 JSON mapping
(trace/span IDs are hex strings, enums are integers)
[Source: https://opentelemetry.io/docs/specs/otlp/]. Standardized
env vars configure exporters without code changes: `OTEL_EXPORTER_OTLP_ENDPOINT`
(gRPC default `http://localhost:4317`, HTTP default `http://localhost:4318`),
per-signal endpoint/header/timeout overrides, and `OTEL_EXPORTER_OTLP_PROTOCOL`
[Source: https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/].

**Context propagation defaults to W3C Trace Context; Baggage is a
separate, higher-risk mechanism.** A Context object carries trace/span
IDs across service boundaries so a downstream service can create a
child span in the same trace. The default propagator is **W3C Trace
Context**, carried in a `traceparent` header of the form
`<version>-<trace-id>-<parent-id>-<trace-flags>`
[Source: https://opentelemetry.io/docs/concepts/context-propagation/].
**Baggage** is a separate mechanism for propagating arbitrary key-value
pairs across the same boundaries — the docs explicitly warn to "avoid
putting sensitive information (like user credentials, API keys, or PII)
in baggage, as it might be logged or sent to untrusted downstream
services" [Source: https://opentelemetry.io/docs/concepts/context-propagation/].

**Semantic conventions are the standardization layer, and their
stability is tracked separately from the SDK's.** Naming rules: use
dot-delimited namespacing (`service.version`) with snake_case within a
namespace component (`http.response.status_code`), nesting
hierarchically rather than flattening
[Source: https://opentelemetry.io/docs/specs/semconv/general/naming/].
Critically, an SDK being Stable does not make the specific conventions
it emits Stable — see Anti-patterns.

**The per-language, per-signal stability matrix — this is the single
most consequential version-awareness fact for this skill.**
OpenTelemetry follows SemVer 2.0.0 but with **independent version
numbers for the API, SDK, Semantic Conventions, and contrib
components** — there is no single unified "OpenTelemetry version."
Stability is tracked **per signal, not per SDK as a whole**: "The API
MUST become stable before the other components," and a language's
traces can be Stable while its logs are still Development inside the
same package release
[Source: https://opentelemetry.io/docs/specs/otel/versioning-and-stability/].
As documented (state applies as of this research, 2026-09-10):

| Signal | Stable | Notably not-yet-Stable |
|---|---|---|
| Traces | C++, .NET, Go, Java, JavaScript, PHP, Python, Ruby, Swift | Rust (Beta), Kotlin (Development) |
| Metrics | C++, .NET, Go, Java, JavaScript, PHP | Erlang/Elixir, Ruby, Swift (Development); Rust (Beta) |
| Logs | **C++, .NET, PHP only** | Go (Release Candidate, v1.47.0-rc.1); Java, JavaScript, Python, Ruby, Swift, Kotlin (Development); Rust (Beta) |

[Source: https://opentelemetry.io/docs/languages/;
https://opentelemetry.io/blog/2026/go-logs-api-sdk-rc/] **Applicable
range: current per-language SDK releases as of 2026-09-10 — re-verify
before relying on this, since Go Logs is actively moving toward stable
v1.** This matters concretely for this library: **JavaScript and Python
— languages used heavily elsewhere in this skill set — have Stable
traces/metrics but Development-status logs.** Treat OTel-based logging
in JS/Python as not yet covered by the non-breaking-minor-upgrade
guarantee; traces/metrics in those languages are. Once Stable, a
component gets real guarantees: the API gets a minimum of 3 years of
support after the *next* major ships, SDK/contrib each get a minimum of
1 year, and minor upgrades within a stable major line are guaranteed
non-breaking
[Source: https://opentelemetry.io/docs/specs/otel/versioning-and-stability/].
Approximate current releases at research time: Collector core/contrib
~v1.66.0/v0.160.0, JS SDK ~v2.11.0, Python ~v1.44.0/v0.65b0, Go ~v1.46.0
stable with v1.47.0-rc.1 (Logs) in release-candidate testing
[Source: https://github.com/open-telemetry/opentelemetry-collector/releases;
https://github.com/open-telemetry/opentelemetry-js/releases;
https://github.com/open-telemetry/opentelemetry-python/releases;
https://github.com/open-telemetry/opentelemetry-go/releases]. **Unresolved:
exact calendar release dates for these could not be reliably confirmed in
the underlying research** — GitHub's release pages rendered
inconsistent years across fetches; treat the version numbers as
approximately current to 2026-09-10 and re-verify against each
repository's Releases page before depending on a specific date.

**Collector: four component types wired into per-signal pipelines.**
**Receivers** typically listen on a network port (some pull/scrape
instead); **Processors** transform data in flight (add/remove
attributes, filter, batch); **Exporters** forward data onward;
**Connectors** act as both an exporter and a receiver, bridging one
pipeline's output into another's input
[Source: https://opentelemetry.io/docs/collector/architecture/;
https://opentelemetry.io/docs/collector/configuration/]. If the same
receiver instance is referenced by more than one pipeline, it feeds all
of them synchronously from a single instance — a documented source of
cross-pipeline coupling/blocking risk
[Source: https://opentelemetry.io/docs/collector/architecture/].
Configuration is YAML with built-in env-var substitution
(`${env:VAR}`, `${env:VAR:-default}`, `$$` to escape a literal `$`)
[Source: https://opentelemetry.io/docs/collector/configuration/].

## Decision framework

1. **Zero-code vs. manual instrumentation for a given migration:**
   default to layering zero-code (auto-) instrumentation first for
   baseline library/framework coverage — it requires no source changes
   and works even when you can't modify the target application — then
   add manual instrumentation only for application-specific logic the
   auto layer can't see. These are documented as permanently
   complementary, not a stepping-stone relationship; don't plan to "rip
   out" auto-instrumentation once manual instrumentation exists
   [Source: https://opentelemetry.io/docs/concepts/instrumentation/].
   For Go specifically, there is no bytecode-level auto-instrumentation
   agent comparable to Java's/Node's — expect to write more manual
   spans/metrics for in-application logic
   [Source: https://opentelemetry.io/docs/languages/go/getting-started/].
2. **Should you rely on a given semantic convention in production?**
   Check its individual stability, not just the SDK's. If the specific
   convention (e.g. certain database/messaging conventions) is still
   Experimental, using it carries standing breaking-change exposure even
   on an otherwise-Stable SDK/API
   [Source: https://opentelemetry.io/docs/languages/]. The simplest safe
   default is to prefer Stable-marked conventions for anything you plan
   to build dashboards/alerts against long-term, and treat Experimental
   ones as subject to change.
3. **Collector deployment topology — agent vs. gateway, sized to actual
   scale:** for a single service or small deployment, a local **Agent**
   Collector per host/pod (or skipping the Collector and exporting
   straight to a backend) is the simplest viable option — don't stand up
   a centralized Collector tier before you have a reason to. Move to a
   **Gateway** topology (centralized, load-balanced Collector tier) when
   you need cross-service aggregation, centralized processing/sampling
   policy, or tail-sampling that requires seeing all spans of a trace in
   one place
   [Source: https://opentelemetry.io/docs/collector/deploy/;
   https://opentelemetry.io/docs/collector/architecture/]. If you choose
   gateway + tail sampling, you need a load-balancing exporter that
   routes consistently by trace ID upstream of the gateway tier — a
   plain L4 load balancer will split traces across instances and break
   tail-sampling decisions (see Anti-patterns).
4. **Do nothing / stay on existing tooling:** if the team already has a
   working, vendor-specific instrumentation layer and no cross-vendor
   portability or multi-backend need exists, introducing OpenTelemetry
   is not automatically justified — weigh the migration cost (see
   Migration/Breaking-changes) against the vendor-neutrality benefit
   before recommending adoption.

## Engineering rules

- State which per-language, per-signal stability level your
  instrumentation guidance targets — never assume "logs work the same
  as traces" across languages (VA-3).
- Set `service.name` (and other required resource attributes) explicitly
  rather than relying on the `unknown_service` default
  [Source: https://opentelemetry.io/docs/languages/sdk-configuration/general/].
- Use the standardized `OTEL_EXPORTER_OTLP_*` env vars for exporter
  config over hardcoded endpoints where the language SDK supports them
  [Source: https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/].
- Follow semantic-conventions naming (dot-namespaced, snake_case within
  a namespace) for any custom attributes, so they compose with standard
  dashboards/queries
  [Source: https://opentelemetry.io/docs/specs/semconv/general/naming/].
- Reserve Baggage strictly for non-sensitive, low-cardinality contextual
  data — never credentials, PII, or API keys
  [Source: https://opentelemetry.io/docs/concepts/context-propagation/].
- Always configure a sending queue on Collector exporters rather than
  relying on synchronous, unbuffered export
  [Source: https://opentelemetry.io/docs/collector/resiliency/].

## Trade-offs

Zero-code instrumentation is fast to adopt and requires no source
changes, but only sees library/framework/runtime-level telemetry —
manual instrumentation is more work but is the only way to capture
application-specific business logic
[Source: https://opentelemetry.io/docs/concepts/instrumentation/]. A
Gateway Collector topology centralizes processing/sampling policy and
enables tail sampling, at the cost of an extra infrastructure tier to
run, secure, and scale correctly (including the L7-load-balancing and
trace-ID-routing requirements below) versus a simpler Agent-only or
direct-export topology
[Source: https://opentelemetry.io/docs/collector/deploy/;
https://opentelemetry.io/docs/collector/scaling/]. Head sampling is
cheap and simple everywhere in the pipeline but can't guarantee
capturing every error trace; tail sampling can guarantee that but
requires stateful, resource-intensive infrastructure
[Source: https://opentelemetry.io/docs/concepts/sampling/].

## Anti-patterns

- **Binding Collector receiver endpoints to `0.0.0.0`** instead of
  `localhost` or a specific interface — a documented denial-of-service
  anti-pattern (CWE-1327); the Collector's own default changed to
  `localhost` starting in **v0.110.0** specifically to close this gap
  [Source: https://opentelemetry.io/docs/security/config-best-practices/].
- **Relying on Experimental-status semantic conventions in production**
  as if SDK stability protected you from their churn — it doesn't: "if
  your instrumentation relies on semantic conventions marked as
  Experimental, your data flow might be subject to breaking changes"
  regardless of API/SDK status
  [Source: https://opentelemetry.io/docs/languages/].
- **Naively adding Collector replicas to fix a throughput problem**
  without checking where the actual bottleneck is: "adding Collectors to
  the cluster won't help without scaling up the database" if the
  backend is saturated, and can be actively counterproductive —"adding
  more Collectors might cause a harmful side effect" — under
  network-connection-saturation constraints
  [Source: https://opentelemetry.io/docs/collector/scaling/].
- **Load-balancing a stateful tail-sampling Collector deployment with a
  plain L4 load balancer**: without a load-balancing exporter routing
  consistently by trace ID upstream, spans of the same trace can be
  split across independent Collector instances, producing traces
  missing spans once tail-sampling decisions are made on incomplete
  per-instance data
  [Source: https://opentelemetry.io/docs/collector/scaling/].
- **Standing up a centralized Gateway Collector tier before you need
  one** (over-engineering trap) — a single service with no
  cross-service aggregation or tail-sampling need is well served by
  direct export or a simple Agent deployment; don't add the Gateway tier
  "for later" [Source: https://opentelemetry.io/docs/collector/deploy/].
- **Treating hashing as sufficient anonymization** for sensitive
  attributes — see Security.

## Security

Binding Collector receivers to `0.0.0.0` is the concrete, named
DoS anti-pattern here (CWE-1327): "try to always use specific
interfaces, such as a pod's IP, or `localhost` instead of `0.0.0.0`";
as of Collector **v0.110.0**, all server components default to
`localhost` rather than all interfaces
[Source: https://opentelemetry.io/docs/security/config-best-practices/].
Collector configuration itself holds sensitive material — API tokens,
TLS private keys — and should be stored on an encrypted filesystem or
secret store, injected via the built-in env-var substitution rather than
hardcoded; endpoints should use TLS plus the Collector's authentication
extensions
[Source: https://opentelemetry.io/docs/security/config-best-practices/].
"OpenTelemetry collects telemetry data but can't determine what data is
sensitive in your specific context on its own" — PII compliance is the
implementer's responsibility, not something OpenTelemetry enforces
automatically; documented Collector-side mitigations are the
**attribute processor** (remove/modify/hash attributes), **filter
processor** (drop matching spans/metrics), **redaction processor**
(allow-list attributes, mask blocked values), and **transform
processor** (regex-based transforms)
[Source: https://opentelemetry.io/docs/security/handling-sensitive-data/].
**Hashing is explicitly flagged as insufficient anonymization**:
"hashes are reversible in practice if the input space is small and
predictable" — truncation or omission (e.g. dropping the last octet of
an IPv4 address, or the last 80 bits of IPv6) is the recommended
alternative for genuinely sensitive fields
[Source: https://opentelemetry.io/docs/security/handling-sensitive-data/].
Deeper cross-cutting threat modeling is owned by `SK-QA-002`
(security-engineering) and the parent observability skill's PII-scrubbing
discipline — not restated here.

## Performance

Collector scaling is component-type-specific: stateless
receivers/processors/exporters scale behind a load balancer, preferring
**L7** for gRPC OTLP traffic since a standard L4 balancer may pin a
persistent connection to one backend, defeating horizontal scaling;
Prometheus-receiver scrape workloads scale via the **Target Allocator**
to avoid duplicate scraping; stateful components (tail sampling) require
a trace-ID-consistent load-balancing exporter upstream
[Source: https://opentelemetry.io/docs/collector/scaling/]. Signals to
watch: `otelcol_processor_refused_spans` (memory-limiter rejections —
scale up), and `otelcol_exporter_queue_size` vs.
`otelcol_exporter_queue_capacity` — "consider scaling up when it reaches
60-70% of capacity"
[Source: https://opentelemetry.io/docs/collector/scaling/]. **Sending
queues** buffer export with exponential-backoff-and-jitter retry, by
default retrying for up to 5 minutes before dropping the oldest queued
data — tune the queue against expected load, memory/disk budget, and
acceptable endpoint downtime
[Source: https://opentelemetry.io/docs/collector/resiliency/]. For
durability beyond an in-memory queue (lost on crash), a disk-backed
write-ahead-log (WAL) queue lets the Collector resume pending sends
after a restart, or an external message queue (e.g. Kafka) between
ingest and processing tiers absorbs a downed gateway Collector without
data loss, accumulating up to the topic's retention limit
[Source: https://opentelemetry.io/docs/collector/resiliency/]. Note this
is the Collector's *own* internal pipeline resiliency — not an
application-level resilience pattern (retries/circuit breakers), which
the parent observability skill explicitly does not cover either.
Broader cross-cutting performance method is owned by `SK-QA-003`.

## Testing

**Real, documented gap: no dedicated official "testing your
OpenTelemetry instrumentation" guide was found.** The Node.js
instrumentation page covers `tracer.startActiveSpan()`, nested spans,
attributes, and context utilities, but not a testing workflow, and a
broader search did not surface a dedicated `opentelemetry.io` testing
guide either
[Source: https://opentelemetry.io/docs/languages/js/instrumentation/].
Language SDKs are widely known in the broader ecosystem to ship
in-memory/no-op exporters usable for test assertions (e.g. an
`InMemorySpanExporter` in OpenTelemetry JS's `@opentelemetry/sdk-trace-base`),
but this is an inference from the package's public surface, not a
documented, official testing walkthrough — verify against current
per-language docs before relying on a specific test-exporter API.
**Unresolved:** whether a dedicated official testing guide exists
elsewhere on `opentelemetry.io` (beyond the Node.js instrumentation page
checked) was not fully ruled out; only the most likely landing page was
checked before accepting this as a real gap. General test-strategy
method is owned by `SK-QA-001`.

## Failure handling

- If the target language/runtime isn't stated, ask before proposing
  instrumentation — package names, auto-instrumentation availability,
  and signal stability all differ per language.
- If shell is unavailable/denied, output advisory instrumentation
  code/Collector YAML and state explicitly that it was not run or
  validated.
- If a claim depends on the exact current release version and the
  pinned version is unknown, state the guidance's assumed version range
  rather than asserting "latest" (VA-3).

## Escalation

- A Collector config change affecting a shared/production pipeline
  (e.g. relaxing a receiver bind address, changing sampling that affects
  retention/cost elsewhere) requires explicit user confirmation before
  applying.
- A project still directly depending on OpenCensus is escalated to
  confirm migration scope before proceeding — OpenCensus repositories
  were archived 2023-07-31, so the documented bridge is the only
  forward-compatible path, not a simple config change
  [Source: https://opentelemetry.io/docs/compatibility/migration/].

## Outputs & verification

- **Outputs:** API/SDK instrumentation (auto and/or manual) added to the
  target service; Collector YAML configuration for the chosen topology;
  a stability/version-applicability analysis or migration plan.
- **Verify:** `service.name` and required resource attributes are set;
  any Experimental-status semantic convention in use is flagged; no
  Collector receiver is bound to `0.0.0.0` without explicit
  justification; every signal-stability claim matches the actual
  language/signal in use, not an assumption.

## References

- [research/technologies/opentelemetry.md](../../research/technologies/opentelemetry.md) —
  full research pass (335 lines, 82 citations); source list for every
  claim above.
- Parent skill: [observability](../observability/SKILL.md) (`SK-QA-004`) —
  signal-selection method, cardinality/PII discipline, alert design.
- Related: `prometheus` (OTLP receiver into Prometheus), `grafana`
  (OTLP-ingestion visualization layer), `sentry` (JS SDK runs on
  OpenTelemetry internally since v8) — integration mechanics for each
  live in that technology's own skill, since `opentelemetry.io` itself
  documents these only as a one-line vendor listing, not integration
  detail
  [Source: https://opentelemetry.io/ecosystem/vendors/].
