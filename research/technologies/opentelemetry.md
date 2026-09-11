# OpenTelemetry — Deep Technology Reference

Research date: 2026-09-10. Primary source: official OpenTelemetry documentation hosted
at `opentelemetry.io/docs/` (concepts under `/docs/concepts/`, language SDKs under
`/docs/languages/`, Collector under `/docs/collector/`, specification under
`/docs/specs/otel/` and `/docs/specs/semconv/`, security under `/docs/security/`).
Because OpenTelemetry is explicitly a multi-repository CNCF project — the spec, the
Collector, and each language SDK are versioned and released independently — this
research also cites the `github.com/open-telemetry` organization directly
(`opentelemetry-specification`, `opentelemetry-collector`,
`opentelemetry-collector-contrib`, `opentelemetry-js`, `opentelemetry-python`,
`opentelemetry-go`, `semantic-conventions`, `opentelemetry-proto`) for release,
governance, and changelog material that `opentelemetry.io` itself does not host or
does not keep current. Where a fetched GitHub release page returned an ambiguous or
apparently-mis-rendered year in this session's tooling, the specific calendar date is
treated as low-confidence and flagged rather than asserted (see Section 12/Unresolved).

Citation format per project convention: `[Source: <url>] <claim>.` Claims not found
in official docs are marked "Not documented / could not verify." Uncertain claims
are marked "Unresolved: …". Inferences are labeled "[Inference, not confirmed in
docs]".

---

## 1. Core Concepts

[Source: https://opentelemetry.io/docs/what-is-opentelemetry/] OpenTelemetry is described as an observability framework and toolkit for generating, collecting, and exporting telemetry data (traces, metrics, and logs); it is explicitly "**open source**, as well as **vendor- and tool-agnostic**," meaning it is designed to be used with any observability backend rather than one vendor's proprietary format.

[Source: https://opentelemetry.io/docs/what-is-opentelemetry/] OpenTelemetry states plainly: "**OpenTelemetry is not an observability backend itself**. The backend (storage) and the frontend (visualization) of telemetry data are intentionally left to other tools." This boundary — instrumentation/collection standard, not storage/visualization product — is foundational and recurs throughout this document (see Section 14).

[Source: https://opentelemetry.io/docs/what-is-opentelemetry/] OpenTelemetry is a Cloud Native Computing Foundation (CNCF) project, formed as a merger of two earlier, competing instrumentation standards, OpenTracing and OpenCensus, into a single specification (see Section 11 for the migration implications of this history).

[Source: https://opentelemetry.io/docs/concepts/components/] The project is layered into three architecturally distinct pieces: the **API** — "Defines data types and operations for generating and correlating tracing, metrics, and logging data" — the **SDK** — "Defines requirements for a language-specific implementation of the API. Configuration, data processing, and exporting concepts are also defined here" — and the **Collector**, described as "a vendor-agnostic proxy that can receive, process, and export telemetry data," which runs as a standalone infrastructure component rather than embedded in application code. The API and SDK live *inside* an instrumented application; the Collector sits *between* applications and observability backends.

[Source: https://opentelemetry.io/docs/concepts/signals/traces/] A **trace** represents "the path of a request through your application." A **span** — the fundamental building block of a trace — "represents a unit of work or operation," and carries a name, start/end timestamps, parent span ID, trace context, attributes, events, links, and a status. Trace context (Trace ID, span ID, trace flags, trace state) is immutable once a span is created and is what allows spans generated in different processes/services to be correlated into one trace.

[Source: https://opentelemetry.io/docs/concepts/signals/traces/] Span **kind** classifies a span's role in a distributed operation — `Client`, `Server`, `Internal`, `Producer`, or `Consumer` (e.g. a client span represents "a synchronous outgoing remote call such as an HTTP request or database call"). Span **status** is one of `Unset` (default), `Error`, or `Ok`.

[Source: https://opentelemetry.io/docs/concepts/signals/metrics/] A **metric** is "a measurement of a service captured at runtime." Measurements are captured via **metric instruments** created by a `Meter` (itself created by a `MeterProvider`); seven instrument kinds are defined: Counter, Asynchronous Counter, UpDownCounter, Asynchronous UpDownCounter, Gauge, Asynchronous Gauge, and Histogram (a "client-side aggregation of values, such as request latencies"). A default **cardinality limit of 2000** unique attribute-combinations per instrument exists specifically to prevent unbounded memory growth (see Section 6).

[Source: https://opentelemetry.io/docs/concepts/signals/logs/] A **log** is defined as "a timestamped text record, either structured (recommended) or unstructured, with optional metadata." The docs note logs have "the biggest legacy" of the three signals because virtually every language/framework already emits some form of logging; OpenTelemetry's logs support is explicitly designed to work with existing logging output rather than replace it, and "automatically correlates your logs and traces" when auto-instrumentation is active by injecting trace/span IDs into log records.

[Source: https://opentelemetry.io/docs/concepts/context-propagation/] Context Propagation is "the core concept that enables Distributed Tracing" — a Context object carries correlation information (trace ID, span ID) that is serialized/deserialized as a request crosses service boundaries, letting a downstream service create a child span belonging to the same trace as the upstream caller. The default propagation format is the **W3C Trace Context** standard, carried in a `traceparent` HTTP header of the form `<version>-<trace-id>-<parent-id>-<trace-flags>` (e.g. `00-a0892f3577b34da6a3ce929d0e0e4736-f03067aa0ba902b7-01`). **Baggage** is a separate mechanism for propagating arbitrary key-value pairs across the same boundaries; the docs explicitly warn: "avoid putting sensitive information (like user credentials, API keys, or PII) in baggage, as it might be logged or sent to untrusted downstream services."

[Source: https://opentelemetry.io/docs/specs/otlp/] **OTLP** (the OpenTelemetry Protocol) is the wire protocol used to move telemetry from SDKs/Collectors to Collectors/backends. It is **Stable for the trace, metric, and log signals** (and still Development for the newer profiles signal). It supports gRPC (Protobuf, default port **4317**) and HTTP (binary or JSON-encoded Protobuf, default port **4318**) transports.

[Source: https://github.com/open-telemetry] The `github.com/open-telemetry` GitHub organization hosts OpenTelemetry as a genuinely multi-repository project: `opentelemetry-specification` ("Specifications for OpenTelemetry"), `opentelemetry-proto` (the OTLP wire-format Protobuf/gRPC definitions), `semantic-conventions` ("standards for generating consistent, accessible telemetry"), `opentelemetry-collector` and `opentelemetry-collector-contrib` (core vs. community-contributed Collector components), `community` (cross-project governance/contribution material), plus one repository per language SDK (`opentelemetry-js`, `opentelemetry-python`, `opentelemetry-go`, `opentelemetry-java`, etc.) — each independently versioned and released (see Section 12).

---

## 2. Architecture

[Source: https://opentelemetry.io/docs/concepts/components/] The end-to-end telemetry pipeline flows: instrumentation (auto- or manually-written) generates data via the **API**; the **SDK** processes it (sampling, batching, resource attachment) and hands it to an **exporter**; the exporter sends it either directly to a backend or, more commonly in production, to a standalone **Collector**; the Collector further processes and re-exports it to one or more observability **backends**.

[Source: https://opentelemetry.io/docs/collector/architecture/] The Collector itself is "an executable file that can receive telemetry, process it, and export it to multiple targets, such as observability backends," built from three composable component types: **Receivers** ("typically listen on a network port and receive telemetry data," though some pull/scrape instead), **Processors** (which "can transform the data before forwarding it, such as adding or removing attributes from spans," and can also drop or synthesize data), and **Exporters** ("typically forward the data they get to a destination on a network"). [Source: https://opentelemetry.io/docs/collector/configuration/] A fourth component type, **Connectors**, acts as both an exporter and a receiver simultaneously, bridging one pipeline's output into another pipeline's input.

[Source: https://opentelemetry.io/docs/collector/architecture/] Data moves through configured **pipelines**, each defining "a path that data follows in the Collector: from reception, to processing (or modification), and finally to export," with separate pipelines definable per signal type (traces/metrics/logs). Multiple receivers can feed one pipeline; multiple exporters can fan data out from one pipeline; and if the same receiver instance is referenced by more than one pipeline, it feeds all of them synchronously from a single instance (a documented source of cross-pipeline coupling/blocking risk).

[Source: https://opentelemetry.io/docs/collector/architecture/] Two baseline deployment topologies are documented: **Agent** deployment runs a Collector "as a daemon on individual VMs or containers, collecting telemetry from local applications," independent of the instrumented application's own library/language; **Gateway** deployment runs a centrally-positioned Collector (or a fleet behind a load balancer) that receives and aggregates telemetry from many agents/apps before exporting onward to backends (elaborated in Sections 10/17).

[Source: https://opentelemetry.io/docs/concepts/instrumentation/] Two instrumentation approaches are documented as complementary rather than sequential: **zero-code** (a.k.a. auto-) instrumentation, described as "great for getting started, or when you can't modify the application you need to get telemetry out of," which yields telemetry from libraries and the runtime environment without source changes; and **code-based** (manual) instrumentation, which "allow[s] you to get deeper insight and rich telemetry from your application itself." The docs state directly: "You can use both solutions simultaneously" — auto-instrumentation is not framed as a stepping-stone that manual instrumentation later replaces, but as a permanent complementary layer.

---

## 3. APIs

[Source: https://opentelemetry.io/docs/languages/js/getting-started/nodejs/] **Node.js**: The `@opentelemetry/sdk-node` package (`NodeSDK`) is the entry point; auto-instrumentation is added via `@opentelemetry/auto-instrumentations-node`'s `getNodeAutoInstrumentations()`. A minimal setup:
```typescript
const sdk = new NodeSDK({
  traceExporter: new ConsoleSpanExporter(),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new ConsoleMetricExporter(),
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});
sdk.start();
```
loaded before application code via Node's `--import` flag: `node --import ./instrumentation.mjs app.js`. Core packages: `@opentelemetry/api` (the language API), `@opentelemetry/sdk-node`, `@opentelemetry/sdk-trace-node`, `@opentelemetry/sdk-metrics`.

[Source: https://opentelemetry.io/docs/languages/python/getting-started/] **Python**: `pip install opentelemetry-distro` plus `opentelemetry-bootstrap -a install` (which auto-installs the framework-specific instrumentor packages detected in the environment) enables zero-code instrumentation via a CLI wrapper: `opentelemetry-instrument --traces_exporter console --service_name dice-server flask run -p 8080`. Manual instrumentation uses the API directly:
```python
from opentelemetry import trace
tracer = trace.get_tracer("diceroller.tracer")
with tracer.start_as_current_span("roll") as span:
    res = randint(1, 6)
    span.set_attribute("roll.value", res)
```
and similarly `from opentelemetry import metrics; meter = metrics.get_meter(...); counter = meter.create_counter(...)`. With `opentelemetry-exporter-otlp` installed, auto-instrumentation defaults to exporting via OTLP/gRPC to `localhost:4317`.

[Source: https://opentelemetry.io/docs/languages/go/getting-started/] **Go**: Go has no bytecode-level auto-instrumentation agent comparable to Java's or Node's; instrumentation is either manual or provided by an instrumentation *library* wrapping a specific dependency (e.g. `otelhttp.NewHandler()` around an `http.Handler`). Applications explicitly bootstrap trace/meter/logger providers (a documented `setupOTelSDK` pattern), and are responsible for calling its returned shutdown function. The `autoexport` package can configure exporters purely from environment variables (`OTEL_TRACES_EXPORTER`, `OTEL_METRICS_EXPORTER`, `OTEL_LOGS_EXPORTER`, `OTEL_EXPORTER_OTLP_ENDPOINT`) rather than hardcoding exporter construction. Docs note explicitly: "Instrumentation libraries capture telemetry at the edges of your systems, such as inbound and outbound HTTP requests, but they don't capture what's going on in your application" — manual spans/metrics are required for in-application logic in Go far more often than in languages with agent-based auto-instrumentation.

[Source: https://opentelemetry.io/docs/specs/otlp/] **OTLP wire protocol** (shared across all languages): gRPC transport uses unary `Export*ServiceRequest` calls over Protobuf, with clients able to pipeline concurrent requests for higher throughput; HTTP transport uses HTTP POST with binary (`Content-Type: application/x-protobuf`) or JSON-encoded Protobuf bodies — "Implementations MAY use HTTP/1.1 or HTTP/2 transports. Implementations that use HTTP/2 transport SHOULD fallback to HTTP/1.1 transport if HTTP/2 connection cannot be established." In JSON encoding, trace/span IDs are hex strings (not base64) and enums are encoded as integers, both deviations from default proto3 JSON mapping.

---

## 4. Configuration

[Source: https://opentelemetry.io/docs/languages/sdk-configuration/general/] Standardized cross-language environment variables (support varies per-language SDK): `OTEL_SERVICE_NAME` (default `unknown_service`, sets the `service.name` resource attribute, takes precedence over the same key inside `OTEL_RESOURCE_ATTRIBUTES`); `OTEL_RESOURCE_ATTRIBUTES` (comma-separated `key1=value1,key2=value2`); `OTEL_TRACES_SAMPLER` (default `parentbased_always_on`; other values include `always_on`, `always_off`, `traceidratio`, `jaeger_remote`, `xray`) with `OTEL_TRACES_SAMPLER_ARG` for sampler-specific parameters (e.g. a 0–1 ratio, or `endpoint=http://localhost:14250,pollingIntervalMs=5000` for `jaeger_remote`); `OTEL_PROPAGATORS` (default `tracecontext,baggage`; also `b3`, `b3multi`, `jaeger`, `xray`, `ottrace`); and per-signal exporter selectors `OTEL_TRACES_EXPORTER`/`OTEL_METRICS_EXPORTER`/`OTEL_LOGS_EXPORTER` (default `otlp` for all three; also `jaeger`/`zipkin`/`console`/`none` for traces, `prometheus`/`console`/`none` for metrics, `console`/`none` for logs).

[Source: https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/] Standardized OTLP-exporter environment variables: `OTEL_EXPORTER_OTLP_ENDPOINT` (a base endpoint for all signals — gRPC default `http://localhost:4317`, HTTP default `http://localhost:4318`) and its per-signal overrides `OTEL_EXPORTER_OTLP_{TRACES,METRICS,LOGS,PROFILES}_ENDPOINT` (HTTP defaults append the signal path, e.g. `http://localhost:4318/v1/traces`); `OTEL_EXPORTER_OTLP_HEADERS` and per-signal variants for auth/metadata headers; `OTEL_EXPORTER_OTLP_TIMEOUT` (default `10000` ms) and per-signal variants; and `OTEL_EXPORTER_OTLP_PROTOCOL` (`grpc`, `http/protobuf`, or `http/json`; default is documented as "SDK-dependent, but will typically be either `http/protobuf` or `grpc`").

[Source: https://opentelemetry.io/docs/specs/semconv/resource/] Resource configuration: `service.name` is a required resource attribute that "MAY be configurable via a dedicated environment variable" and effectively "MUST be provided" one way or another; `telemetry.sdk.name`, `telemetry.sdk.language`, and `telemetry.sdk.version` are required attributes the SDK itself sets automatically (identifying that the data came from an OpenTelemetry SDK, which language, and which version); `telemetry.distro.name` is recommended for auto-instrumentation distributions, which "SHOULD set [it] to a string starting with `opentelemetry-`."

[Source: https://opentelemetry.io/docs/collector/configuration/] Collector configuration is YAML, structured around the four component classes (receivers, processors, exporters, connectors) declared under top-level keys, wired together under a `service` section's `pipelines` (per-signal receiver→processor→exporter chains), `extensions` (e.g. health check, zPages), and `telemetry` (the Collector's own self-observability) subsections. Environment-variable substitution is built in: `${env:VARIABLE_NAME}`, with a bash-style default fallback `${env:DB_KEY:-default-value}`, and `$$` to escape a literal `$`.

---

## 5. Recommended Patterns

[Source: https://opentelemetry.io/docs/specs/semconv/general/naming/] **Semantic conventions naming** is the primary standardization mechanism and a major documented differentiator of OpenTelemetry: "Use namespacing. Delimit the namespaces using a dot character. For example `service.version` denotes the service version where `service` is the namespace and `version` is an attribute in that namespace." Within a namespace component, multi-word names use snake_case (`http.response.status_code`), and namespaces should nest hierarchically (`telemetry.sdk.name`) rather than flattening into underscore-joined names (`http_response.status` is called out as an anti-example).

[Source: https://opentelemetry.io/docs/concepts/instrumentation/] Recommended pattern: layer **zero-code (auto) instrumentation first** for baseline, library/framework-level telemetry, then add **manual instrumentation** for application-specific logic the auto layer cannot see — the two are documented as intended to run together, not as alternatives to choose between once.

[Source: https://opentelemetry.io/docs/concepts/context-propagation/] Recommended pattern for distributed systems: rely on the default **W3C Trace Context** propagator (`traceparent` header) for cross-service correlation rather than a vendor-specific header format, and reserve **Baggage** strictly for non-sensitive, low-cardinality contextual key-value data — never credentials, PII, or API keys, since Baggage values are propagated onward and may be logged or sent to untrusted downstream services.

[Source: https://opentelemetry.io/docs/security/handling-sensitive-data/] Recommended pattern for telemetry data minimization: "Only collect data that serves an observability purpose" and "Avoid collecting personal information unless absolutely necessary" — a preventative, instrument-time discipline rather than a purely downstream, Collector-side scrubbing discipline (though the latter is also documented; see Section 7).

[Source: https://opentelemetry.io/docs/collector/resiliency/] Recommended pattern for Collector pipeline resilience: "Always Use Sending Queues" — an in-memory (optionally disk-backed via write-ahead log) buffer with exponential-backoff-and-jitter retry, so a transient backend outage doesn't immediately drop data, combined with active monitoring of queue-size and refused-span metrics to catch saturation early (see Section 17).

---

## 6. Anti-Patterns

[Source: https://opentelemetry.io/docs/concepts/signals/metrics/] High-cardinality metric attributes are an explicit anti-pattern the SDK itself guards against via a **default cardinality limit of 2000** unique attribute-combinations per instrument — exceeding it triggers the SDK's own overflow handling rather than letting memory grow unbounded, implying that attaching unbounded-cardinality values (raw user IDs, full URLs with query strings, timestamps) as metric attributes is a documented pitfall.

[Source: https://opentelemetry.io/docs/languages/] Relying on **Experimental-status semantic conventions** in production is flagged directly: "Regardless of an API/SDK's status, if your instrumentation relies on semantic conventions marked as Experimental, your data flow might be subject to breaking changes" — i.e., an application can be built on a Stable SDK yet still be exposed to attribute-naming churn if the specific conventions it emits (e.g. certain database or messaging conventions) haven't themselves stabilized.

[Source: https://opentelemetry.io/docs/collector/scaling/] Naively adding Collector replicas to fix a throughput problem is an anti-pattern when the bottleneck is downstream: "adding Collectors to the cluster won't help without scaling up the database" if the backend itself is saturated, and can be actively counterproductive — "adding more Collectors might cause a harmful side effect" — when the constraint is network-connection saturation rather than Collector CPU/memory.

[Source: https://opentelemetry.io/docs/security/config-best-practices/] Binding Collector receiver endpoints to `0.0.0.0` (all interfaces) rather than `localhost` or a specific pod/host IP is called out as a denial-of-service anti-pattern (mapped to CWE-1327); the Collector's own default was changed to bind to `localhost` starting in version 0.110.0 specifically to close this gap by default.

[Source: https://opentelemetry.io/docs/security/handling-sensitive-data/] Treating hashing as sufficient anonymization for sensitive attributes is an anti-pattern the docs explicitly warn against: "Hashing the ID or name of a user may not provide the level of anonymization you need, since hashes are reversible in practice if the input space is small and predictable" — truncation or omission is recommended over hashing for genuinely sensitive fields like IP addresses.

[Source: https://opentelemetry.io/docs/collector/scaling/] Load-balancing tail-sampling or otherwise stateful Collector deployments with a plain L4/connection-based load balancer is an anti-pattern: without a load-balancing exporter upstream to route consistently by trace ID, spans belonging to the same trace can be split across independent Collector instances, producing "traces missing spans" once tail-sampling decisions are made per-instance on incomplete data.

---

## 7. Security

[Source: https://opentelemetry.io/docs/security/] The Collector security documentation frames three core concerns: protecting telemetry that "shouldn't but might contain sensitive information, such as personally identifiable information (PII), application-specific data, or network traffic patterns"; preventing data tampering "that makes telemetry unreliable and disrupts incident responses"; and defending "against denial of service (DoS) attacks." It links out to dedicated hosting best-practices, configuration best-practices, and sensitive-data-handling pages, plus community vulnerability-disclosure and CVE-tracking pages.

[Source: https://opentelemetry.io/docs/security/config-best-practices/] Collector configuration itself is treated as sensitive material: "The Collector's configuration might contain sensitive information including: Authentication information such as API tokens. TLS certificates including private keys," which should be stored "securely such as on an encrypted filesystem or secret store," with environment-variable expansion (Section 4) as the documented mechanism for injecting such secrets without hardcoding them. "Your OTel Collector configuration should include encryption and authentication" for data in transit — TLS certificate configuration and the Collector's built-in authentication extensions are the documented mechanisms.

[Source: https://opentelemetry.io/docs/security/config-best-practices/] For DoS resistance: "try to always use specific interfaces, such as a pod's IP, or `localhost` instead of `0.0.0.0`"; as of Collector version 0.110.0, all server components default to binding `localhost` rather than all interfaces, directly addressing CWE-1327. Least-privilege guidance recommends avoiding root-user execution for the Collector process.

[Source: https://opentelemetry.io/docs/security/handling-sensitive-data/] "OpenTelemetry collects telemetry data but can't determine what data is sensitive in your specific context on its own" — responsibility for compliance and PII protection is documented as belonging to the implementer, not something OpenTelemetry enforces automatically. Documented Collector-side mitigations: the **attribute processor** (remove/modify/hash specific attributes — e.g. hash `user.email` while deleting `user.full_name`), the **filter processor** (drop entire spans/metrics matching sensitive criteria), the **redaction processor** ("delete[s] span, log, and metric datapoint attributes that don't match a list of allowed attributes" and "masks attribute values that match a blocked value list," e.g. to obfuscate credit-card numbers), and the **transform processor** (regex-based transformation). A documented alternative to hashing for values like IP addresses is truncation — "dropping the last octet of IPv4 or the last 80 bits of IPv6."

Not documented / could not verify: a dedicated OpenTelemetry-specific guide to authenticating the Collector *to* a downstream backend (as opposed to authenticating clients *to* the Collector) beyond the general "configure the exporter's TLS/auth extension" pointer; backend-specific auth (e.g. a vendor's API-key header) is necessarily documented per-backend rather than by OpenTelemetry itself, consistent with OpenTelemetry's scope boundary (Section 14).

---

## 8. Performance

[Source: https://opentelemetry.io/docs/concepts/sampling/] **Head sampling** — most commonly Consistent Probability Sampling, deciding per-trace-ID at the start of collection whether to keep a trace (e.g. keep 5%) — is "easy to understand, configure, and implement efficiently anywhere in the pipeline," but "cannot sample based on complete trace data," so it cannot guarantee capturing e.g. every trace containing an error. **Tail sampling** evaluates most/all spans of a trace before deciding, enabling policies like "sample all traces containing errors" or attribute/latency-based rules, at the cost of "stateful, resource-intensive infrastructure" and ongoing rule-maintenance overhead as the system evolves.

[Source: https://opentelemetry.io/docs/concepts/signals/metrics/] The metrics SDK's default cardinality limit (2000 unique attribute-sets per instrument) is itself a documented performance safeguard against unbounded memory growth from high-cardinality instrumentation (cross-reference Section 6).

[Source: https://opentelemetry.io/docs/collector/resiliency/] Sending queues provide buffering plus "a retry mechanism with exponential backoff and jitter" that "will repeatedly attempt to send the buffered data after waiting intervals," retrying for up to 5 minutes by default before the oldest queued data is dropped — a documented throughput/durability tradeoff knob, tunable against "expected load, memory/disk resources, and acceptable endpoint downtime."

[Source: https://opentelemetry.io/docs/collector/scaling/] Collector-side performance signals to monitor: `otelcol_processor_refused_spans` (memory-limiter rejections — indicates the Collector needs to scale up); `otelcol_exporter_queue_size` vs. `otelcol_exporter_queue_capacity` (documented guidance: "Monitor queue size and consider scaling up when it reaches 60-70% of capacity"); and, for Prometheus-receiver scrape workloads, whether "the time to finish scraping all targets often becomes critically close to the scrape interval."

Not documented / could not verify: this research pass did not extract concrete numeric SDK-instrumentation-overhead benchmarks (e.g. added per-request latency in microseconds) from `opentelemetry.io/docs/collector/benchmarks/`; that page exists in the docs' navigation (Section 10's site-map fetch) but its contents were not independently fetched in this pass.

---

## 9. Testing

Not documented / could not verify, and this appears to be a genuine, real gap in the same shape flagged as a possibility in the research brief: the official Node.js instrumentation page (`https://opentelemetry.io/docs/languages/js/instrumentation/`) was fetched specifically looking for guidance on testing instrumented code (e.g. an in-memory span exporter for asserting on emitted spans in unit tests) and **no such guidance was present** on that page — it covers `tracer.startActiveSpan()`, nested/child spans, attributes, and context utilities (`getActiveSpan()`, `getSpan()`), but not a testing workflow. A general web search for OpenTelemetry's documented testing guidance did not surface a dedicated `opentelemetry.io` testing guide either.

[Inference, not confirmed in docs] Language SDKs are widely known in the broader ecosystem to ship in-memory/no-op exporters usable for test assertions (e.g. an `InMemorySpanExporter` class exists in OpenTelemetry JS's `@opentelemetry/sdk-trace-base` package, per its public API surface), but this research pass could not locate an official `opentelemetry.io` documentation page walking through *how* to use such a component to test instrumented application code, so this is flagged as an inference rather than a documented claim.

Unresolved: whether a dedicated "testing your instrumentation" guide exists elsewhere on `opentelemetry.io` (e.g. under a language's own docs tree beyond the Node.js instrumentation page checked here) was not fully ruled out — only the most likely landing page was checked before this gap was accepted as the finding, consistent with the task's guidance to report this honestly rather than force a citation.

---

## 10. Deployment

[Source: https://opentelemetry.io/docs/collector/] The Collector docs enumerate dedicated pages for Quick Start, Install, **Deploy** ("Patterns you can apply to deploy the OpenTelemetry Collector"), Configuration, Components (registry of receivers/processors/exporters/connectors/extensions), Management ("how to manage your OpenTelemetry Collector deployment at scale"), Distributions, Internal Telemetry, Troubleshooting, **Scaling**, Transforming Telemetry, Architecture, Extend, Benchmarks, Registry, and Resiliency — reflecting that deployment/operations is one of the most heavily documented areas of the whole project, consistent with the Collector being the one piece of OpenTelemetry that is genuinely infrastructure rather than embedded library code.

[Source: https://opentelemetry.io/docs/collector/deploy/] The Deploy page's own framing: the Collector is "a single binary that you can deploy in different ways for different use cases," and documents (at minimum) an **Agent** pattern ("Send signals to Collectors and then export to backends" — i.e., a local Collector per host/pod) and a **Gateway** pattern ("send signals first to a single OTLP endpoint and then to backends" — i.e., a centralized, possibly load-balanced tier), alongside other unspecified variations; this research pass did not retrieve the full pros/cons breakdown for each pattern beyond their one-line framing (see Unresolved).

[Source: https://opentelemetry.io/docs/collector/configuration/] Deployable Collector configuration is plain YAML with environment-variable substitution (Section 4), making it naturally suited to container/Kubernetes ConfigMap-style deployment, though this research pass did not separately verify a dedicated Kubernetes Operator deployment guide's contents.

Not documented / could not verify (this pass): the full content of `/docs/collector/deploy/`'s pros/cons comparison table, and the contents of `/docs/collector/distributions/` (core vs. `opentelemetry-collector-contrib` vs. a custom build via the OpenTelemetry Collector Builder) beyond their existence as a documented topic in the site's navigation.

---

## 11. Migration

[Source: https://opentelemetry.io/docs/compatibility/migration/] "OpenTelemetry was created as a merger of OpenTracing and OpenCensus," and "one of the key goals of the OpenTelemetry project is to provide backward compatibility with both projects and a migration story for existing users" — dedicated migration guides exist for both predecessor projects rather than leaving adopters to reverse-engineer a path.

[Source: https://opentelemetry.io/docs/compatibility/migration/] **OpenTracing**: OpenTelemetry provides a shim layer implementing the OpenTracing API on top of the OpenTelemetry API, letting OpenTracing-instrumented code run unmodified against an OpenTelemetry SDK/exporter pipeline.

[Source: https://opentelemetry.io/docs/compatibility/migration/] **OpenCensus**: OpenTelemetry documents having reached feature parity with OpenCensus across C++, .NET, Go, Java, JavaScript, PHP, and Python; an OpenCensus **bridge** ingests OpenCensus-emitted metrics/traces into an OpenTelemetry SDK pipeline, and the documented migration path for library authors is to announce the transition, adopt the bridge, migrate unit tests onto OpenTelemetry-based tooling, and then migrate instrumentation line-by-line. OpenCensus's own GitHub repositories (with one Python exception) were archived on July 31, 2023, formally ending upstream OpenCensus development and making the bridge the primary supported path forward for any remaining OpenCensus-instrumented code.

[Source: https://opentelemetry.io/docs/compatibility/migration/] **Jaeger**: "The Jaeger community deprecated their client libraries and recommends migrating to the OpenTelemetry APIs, SDKs and instrumentations," and separately, "The Jaeger backend can receive trace data using the OpenTelemetry Protocol (OTLP) since v1.35" — meaning a Jaeger-based deployment can switch its *client-side* instrumentation to OpenTelemetry while continuing to send data to an existing Jaeger *backend* via OTLP, decoupling the two migration steps.

[Source: https://raw.githubusercontent.com/open-telemetry/opentelemetry-js/main/CHANGELOG.md] Migrating a JavaScript codebase across an OpenTelemetry JS **major** version boundary (e.g. onto SDK v2.x) is a real, documented undertaking rather than a drop-in bump — see Section 13 for the specific breaking-change inventory pulled from the v2.0.0 changelog entry, which spans minimum-Node/TypeScript-version bumps, renamed/relocated types (`parentSpanId`→`parentSpanContext`, `instrumentationLibrary`→`instrumentationScope`), and removed provider/registration methods.

---

## 12. Version Information

[Source: https://opentelemetry.io/docs/specs/otel/versioning-and-stability/] OpenTelemetry follows Semantic Versioning 2.0.0, but with **independent version numbers for the API, SDK, Semantic Conventions, and contrib components** — there is no single unified "OpenTelemetry version." Stability is also tracked **per signal, not per SDK as a whole**: "All signal components MAY become stable together, or MAY transition to stability component-by-component. The API MUST become stable before the other components" — so, for example, a language's traces API/SDK can be Stable while that same language's logs API/SDK is still in Development, inside the very same package release.

[Source: https://opentelemetry.io/docs/languages/] The documented per-language, per-signal stability matrix (as fetched): **Traces** — Stable in C++, .NET, Go, Java, JavaScript, PHP, Python, Ruby, Swift; Beta in Rust; Development in Kotlin. **Metrics** — Stable in C++, .NET, Go, Java, JavaScript, PHP; Development in Erlang/Elixir, Ruby, Swift; Beta in Rust. **Logs** — Stable in C++, .NET, PHP only; Release Candidate in Go; Development in Java, JavaScript, Python, Ruby, Swift, Kotlin; Beta in Rust. **Profiles** — Development in Java only; unsupported elsewhere at the time of research. [Source: https://opentelemetry.io/blog/2026/go-logs-api-sdk-rc/] Confirming the Go logs row: Go's Logs API/SDK reached release-candidate status (`v1.47.0-rc.1`) as "the final stage before we provide stable v1 compatibility guarantees," with the project explicitly citing logging's placement "on an application's hottest paths" and the difficulty of correcting an API "after it is stable" as the reason for an extended RC/testing window before full stabilization.

[Source: https://opentelemetry.io/docs/specs/otel/versioning-and-stability/] Long-term support commitments once a component is Stable: the **API** receives a minimum of three years of support (bug fixes and security patches) after the *next* major version ships; the **SDK** and **contrib** packages each receive a minimum of one year. The project also commits that "It MUST always be possible to upgrade to the latest minor version of the OpenTelemetry SDK, without creating compilation or runtime errors" — i.e., minor upgrades within a stable major line are guaranteed non-breaking.

VERSION SENSITIVITY: [Source: https://github.com/open-telemetry/opentelemetry-collector/releases] and [Source: https://github.com/open-telemetry/opentelemetry-js/releases] and [Source: https://github.com/open-telemetry/opentelemetry-python/releases] and [Source: https://github.com/open-telemetry/opentelemetry-go/releases] — at the time of this research, the most recent tagged releases observed were: Collector core/contrib around **v1.66.0 / v0.160.0**; OpenTelemetry JS SDK around **v2.11.0**; OpenTelemetry Python around **v1.44.0 / v0.65b0**; OpenTelemetry Go around **v1.46.0** stable (with **v1.47.0-rc.1** in release-candidate testing for the Logs API/SDK, per the blog post above). **Unresolved**: the exact calendar dates for these releases could not be pinned down reliably in this research pass — GitHub's release pages rendered ambiguous or apparently-inconsistent years across separate fetches in this session's tooling, so specific day-level dates are intentionally omitted here; treat the version numbers above as approximately current to this research date (2026-09-10) and re-verify exact dates directly against each repository's Releases page before relying on them.

---

## 13. Breaking Changes

[Source: https://raw.githubusercontent.com/open-telemetry/opentelemetry-js/main/CHANGELOG.md] OpenTelemetry JS SDK **v2.0.0** breaking changes (a worked example of a major-version migration, cross-referenced in Section 11): minimum supported Node.js raised to `^18.19.0 || >=20.6.0` (dropping Node 14, 16, and early 18/20), minimum TypeScript raised to 5.0.4, and the compilation target raised to ES2022 from ES2017. API/type changes: `parentSpanId` replaced by `parentSpanContext` on `Span`/`ReadableSpan`; `instrumentationLibrary` renamed to `instrumentationScope` across multiple classes; the `Resource` class made private in favor of `resourceFromAttributes()`/`defaultResource()`/`emptyResource()` factory functions. Metrics SDK changes: the deprecated `type` field on `MetricDescriptor` removed; `MeterProvider.addMetricReader()` removed in favor of constructor options; `View`/`Aggregation` types replaced by `ViewOptions`/`AggregationOption`. Core/provider changes: deprecated `getEnv()`/`getEnvWithoutDefaults()` removed; deprecated samplers removed from core (relocated to `sdk-trace-base`); `IdGenerator`/`RandomIdGenerator` removed from core; environment-variable-based propagator configuration removed; `BasicTracerProvider.addSpanProcessor()` and `.register()` removed in favor of constructor options.

[Source: https://opentelemetry.io/docs/languages/] The documented Experimental-semantic-conventions caveat (Section 6) is itself a standing, structural breaking-change risk: an SDK or API being Stable does not protect an application from attribute-shape changes in whichever *semantic conventions* it happens to emit if those conventions are still Experimental — this is a distinct axis of breaking-change exposure from the SDK/API version itself.

[Source: https://opentelemetry.io/docs/compatibility/migration/] OpenCensus repository archival (July 31, 2023) is a hard breaking change for any project still directly depending on OpenCensus client libraries: no further upstream fixes will land, making the documented bridge (Section 11) the only forward-compatible path rather than one option among several.

Not documented / could not verify: a consolidated, cross-language "breaking changes by version" index analogous to a single project's changelog was not located; because the API, SDK, Collector, and each language implementation version independently (Section 12), breaking-change history is necessarily scattered across each repository's own `CHANGELOG.md`/release notes rather than centralized on `opentelemetry.io`.

---

## 14. Limitations

[Source: https://opentelemetry.io/docs/what-is-opentelemetry/] The single most consequential, explicitly documented limitation: "**OpenTelemetry is not an observability backend itself**. The backend (storage) and the frontend (visualization) of telemetry data are intentionally left to other tools." OpenTelemetry standardizes *instrumentation and transport* (API, SDK, OTLP, Collector) but deliberately ships no storage engine, query language, dashboarding, or alerting layer — a production deployment always needs a separate backend (Prometheus, Grafana, Jaeger, or a commercial APM vendor; see Section 16) to actually store and visualize the data OpenTelemetry collects.

[Source: https://opentelemetry.io/docs/concepts/signals/logs/] Signal maturity is uneven and language-dependent: as documented in Section 12, Logs is Stable in only three languages (C++, .NET, PHP) versus Traces being Stable in nine — a team standardizing on OpenTelemetry logging in, e.g., Python or JavaScript today is building on a Development-status signal, with the stability and non-breaking guarantees of Section 12 not yet applying.

[Source: https://opentelemetry.io/docs/collector/scaling/] The Collector cannot compensate for a downstream bottleneck: "adding Collectors to the cluster won't help without scaling up the database" — Collector-side horizontal scaling only helps when the Collector tier itself (not the backend, not the network) is the constrained resource.

[Source: https://opentelemetry.io/docs/security/handling-sensitive-data/] "OpenTelemetry collects telemetry data but can't determine what data is sensitive in your specific context on its own" — it provides mechanisms (redaction/attribute/filter processors) but no automatic PII detection; sensitive-data compliance is documented as entirely the implementer's responsibility.

[Source: https://opentelemetry.io/docs/languages/js/instrumentation/] As covered in Section 9, no official first-party guidance for testing instrumented application code was located during this research pass — a documented (by absence) gap for teams trying to write unit/integration tests that assert on emitted spans/metrics.

---

## 15. Debugging

[Source: https://opentelemetry.io/docs/collector/troubleshooting/] The **debug exporter** is the primary documented tool for confirming Collector pipeline health: it "can confirm that the Collector is receiving, processing, and exporting data," and with `verbosity: detailed` prints the full telemetry payload passing through a pipeline to the Collector's own log output.

[Source: https://opentelemetry.io/docs/collector/troubleshooting/] The Collector exposes its own **internal telemetry** (metrics and logs about its own performance) for operators to "configure and use the Collector's own internal telemetry to monitor its performance," and the **zPages** extension, "exposed locally on port 55679," provides a live-inspection UI without external tooling — specifically "The TraceZ page, exposed at `/debug/tracez`, is useful for debugging trace operations, such as: Latency issues[,] Deadlocks and instrumentation problems[, and] Errors."

[Source: https://opentelemetry.io/docs/collector/troubleshooting/] Baseline recommended troubleshooting workflow: check "the Collector's logs as well as zPages for potential issues" first — configuration errors, network failures, and component-level failures are documented as typically surfacing there before deeper investigation is needed.

Not documented / could not verify: language-SDK-side debugging tooling (e.g. an application-level equivalent of the Collector's debug exporter, or a documented "my spans aren't showing up" application-side troubleshooting checklist) was not located as a dedicated page in this research pass; the debugging material found is Collector-centric.

---

## 16. Integration

[Source: https://opentelemetry.io/docs/specs/otel/compatibility/prometheus_and_openmetrics/] **Prometheus** is OpenTelemetry's most precisely documented backend integration. Ingestion direction (Prometheus/OpenMetrics → OTLP): the Collector's Prometheus receiver scrapes Prometheus text exposition format, Prometheus protobuf format, or OpenMetrics text format. Export direction (OTLP → Prometheus): a Prometheus **remote-write** exporter or a Prometheus pull-style exporter (exposing a `/metrics` endpoint for Prometheus itself to scrape). Naming translation rules are formally specified: "The Name of an OTLP metric MUST be added as the Prometheus Metric Name," conformed to Prometheus's naming regex, with discouraged characters replaced by underscores and a `_total` suffix added by default to monotonic sums; unit strings are converted through a documented lookup table to UCUM abbreviations (`seconds`→`s`, `bytes`→`By`); OTLP Sum (`is_monotonic: true`) maps to Prometheus Counter and vice versa, OTLP Gauge maps to Prometheus Gauge and vice versa, and both Standard and Native Histogram types have documented bidirectional conversion rules. Resource attributes (`service.name`, `service.instance.id`) are required "to ensure Prometheus exporters can disambiguate metrics," and are carried via a synthesized `target_info` metric; `otel_scope_`-prefixed labels round-trip OpenTelemetry's instrumentation-scope metadata.

[Source: https://opentelemetry.io/ecosystem/vendors/] **Grafana**: listed on OpenTelemetry's official vendor/ecosystem page as offering both open-source and commercial products with OpenTelemetry support; the vendor page does not itself carry the technical integration steps (those live on Grafana's own documentation, which is out of scope for this opentelemetry.io-grounded research pass — see Unresolved below). [Inference, not confirmed in docs] Grafana's own stack (Tempo for traces, Mimir/Prometheus for metrics, Loki for logs) is widely known to natively ingest OTLP, which is architecturally consistent with the OTLP-stability and Prometheus-compatibility facts documented above, but this specific integration path was not itself confirmed on an opentelemetry.io page in this pass.

[Source: https://opentelemetry.io/ecosystem/vendors/] **Sentry**: also listed on the same official vendor/ecosystem page as an "error tracking and performance monitoring" platform with OTLP integration. As with Grafana, the vendor listing itself is the extent of what `opentelemetry.io` documents about this integration — the technical specifics of how Sentry ingests OTLP traces/errors are necessarily hosted on Sentry's own documentation (`docs.sentry.io`), not on `opentelemetry.io`, consistent with OpenTelemetry's documented scope boundary that it standardizes emission/transport, not backend behavior (Section 14).

Not documented / could not verify: neither a Grafana-specific nor a Sentry-specific *integration guide* (as opposed to a one-line vendor-directory listing) was located on `opentelemetry.io` itself in this research pass. **This is a load-bearing gap for the parallel observability research effort**: the connective tissue between OpenTelemetry and these two backends is, per OpenTelemetry's own documented scope, genuinely owned by each backend's own documentation rather than by opentelemetry.io — any skill built on top of this research that needs Grafana- or Sentry-specific configuration detail should be grounded in Grafana's/Sentry's own official docs (out of this research task's scope), not treated as if OpenTelemetry itself documents it.

[Source: https://opentelemetry.io/docs/compatibility/migration/] **Jaeger**: OTLP ingestion support "since v1.35" on the Jaeger backend side, and deprecated native Jaeger client libraries on the instrumentation side (Section 11) — the most complete non-Prometheus backend integration story found in this pass.

---

## 17. Production Considerations

[Source: https://opentelemetry.io/docs/concepts/sampling/] Sampling strategy is the primary documented cost-control lever at scale: head sampling for simplicity and low overhead everywhere in the pipeline, versus tail sampling (via the Collector's tail-sampling processor) when error-guaranteed-capture or latency-based selection is required, accepting the added stateful-infrastructure cost that tail sampling requires (Section 8).

[Source: https://opentelemetry.io/docs/collector/scaling/] Collector scaling for production is component-type-specific: **stateless** components (most receivers/processors/exporters) scale behind a load balancer, preferring **L7** for gRPC-based OTLP traffic because "standard L4 load balancers might establish a persistent connection to a single backend," defeating horizontal scaling; **scraping** workloads (Prometheus receiver) scale via the **Target Allocator**, which distributes scrape targets across Collector replicas to avoid duplicate scraping; **stateful** components (e.g. tail sampling, which must see every span of a trace to decide) require a load-balancing exporter upstream to consistently route all spans of a given trace to the same downstream instance.

[Source: https://opentelemetry.io/docs/collector/resiliency/] For durability at production scale: in-memory sending queues (fast, but lost on crash) can be upgraded to **disk-backed write-ahead-log (WAL) queues** ("when the Collector restarts, it reads the data from the WAL and resumes attempts to send it") for crash resilience, or to an external **message queue** (e.g. Kafka) between an ingest tier and a processing/gateway tier, so a downed gateway Collector doesn't lose data — messages simply accumulate in the topic "up to Kafka's retention limits."

[Source: https://opentelemetry.io/docs/specs/semconv/general/naming/] For a growing engineering organization, **semantic-convention governance** is the documented mechanism for keeping telemetry consistent across many teams/services: adopting the namespaced, dot-delimited, snake_case-within-namespace naming rules organization-wide (rather than ad hoc per-team attribute names) is what makes cross-service correlation and shared dashboards/queries viable at scale — and (per Section 12/13) tracking which specific conventions a codebase depends on are still Experimental is part of that governance, since Experimental conventions carry standing breaking-change risk independent of the SDK's own stability.

[Source: https://opentelemetry.io/docs/security/config-best-practices/] Production security baseline: encrypted secret storage for Collector configuration secrets, TLS+authentication on all Collector network endpoints, `localhost`/specific-interface binding rather than `0.0.0.0` (default since Collector 0.110.0), and least-privilege (non-root) execution — the same controls documented in Section 7, restated here as the production checklist.

[Source: https://opentelemetry.io/docs/security/handling-sensitive-data/] Production telemetry pipelines should apply data-minimization at the instrumentation layer first (don't emit what you don't need) and Collector-side redaction/attribute/filter processors as a second layer, rather than relying on either alone — the documented guidance frames these as complementary, not redundant.

---

## Unresolved Items (Summary)

- Exact calendar release dates for the current Collector, JS, Python, and Go SDK releases (Section 12) — version numbers were captured with reasonable confidence, but this session's tooling returned apparently-inconsistent years across separate fetches of the same GitHub release pages, so specific dates were deliberately omitted rather than asserted.
- Whether a dedicated official "testing your OpenTelemetry instrumentation" guide exists anywhere on `opentelemetry.io` beyond the Node.js instrumentation page checked (Section 9) — the most likely single page was checked and found not to cover testing, but the full site was not exhaustively searched.
- The full pros/cons comparison table on `/docs/collector/deploy/` and the full contents of `/docs/collector/distributions/` (Section 10) — only the pages' framing/table-of-contents was retrieved, not their complete body content.
- Numeric SDK-instrumentation performance overhead (e.g. added per-request latency) from `/docs/collector/benchmarks/` (Section 8) — page exists in the docs but was not fetched in this pass.
- **Grafana- and Sentry-specific technical integration detail** (Section 16) — `opentelemetry.io`'s own vendor/ecosystem page confirms both are OTLP-compatible backends but does not itself document the integration mechanics; that material lives on each vendor's own documentation site, outside this task's opentelemetry.io-grounded scope. Flagging this explicitly since the task noted this connective tissue matters for the other three parallel observability research docs.
- A consolidated, cross-repository OpenTelemetry governance page (CNCF Governance Committee, Technical Committee, per-language SIGs) was not found at `/docs/specs/otel/`; only the multi-repo *structure* (Section 1) was confirmed via `github.com/open-telemetry` directly, not the formal governance/decision-making process.

---

## Sources Consulted (deduplicated)

- https://opentelemetry.io/docs/what-is-opentelemetry/ — core definition, three pillars, explicit backend/frontend-out-of-scope statement, CNCF/merger history
- https://opentelemetry.io/docs/concepts/components/ — API vs. SDK vs. Collector distinction
- https://opentelemetry.io/docs/concepts/signals/traces/ — spans, trace context, span kind/status
- https://opentelemetry.io/docs/concepts/signals/metrics/ — metric instruments, cardinality limits
- https://opentelemetry.io/docs/concepts/signals/logs/ — logs signal, stability-by-language, log/trace correlation
- https://opentelemetry.io/docs/concepts/context-propagation/ — W3C Trace Context, Baggage, propagation mechanics
- https://opentelemetry.io/docs/concepts/instrumentation/ — zero-code vs. code-based instrumentation
- https://opentelemetry.io/docs/concepts/sampling/ — head vs. tail sampling
- https://opentelemetry.io/docs/specs/otlp/ — OTLP protocol, transports, ports, encoding, stability
- https://opentelemetry.io/docs/specs/semconv/ — semantic conventions overview
- https://opentelemetry.io/docs/specs/semconv/general/naming/ — attribute naming rules
- https://opentelemetry.io/docs/specs/semconv/resource/ — resource semantic conventions (service.name, telemetry.sdk.*)
- https://opentelemetry.io/docs/specs/otel/versioning-and-stability/ — versioning/stability guarantees, LTS windows
- https://opentelemetry.io/docs/specs/otel/compatibility/prometheus_and_openmetrics/ — Prometheus/OpenMetrics translation rules
- https://opentelemetry.io/docs/languages/ — per-language, per-signal stability matrix
- https://opentelemetry.io/docs/languages/js/getting-started/nodejs/ — Node.js SDK setup, auto-instrumentation
- https://opentelemetry.io/docs/languages/js/instrumentation/ — manual instrumentation API, testing-gap check
- https://opentelemetry.io/docs/languages/python/getting-started/ — Python zero-code + manual instrumentation
- https://opentelemetry.io/docs/languages/go/getting-started/ — Go SDK bootstrap, manual instrumentation emphasis
- https://opentelemetry.io/docs/languages/sdk-configuration/general/ — OTEL_SERVICE_NAME, OTEL_TRACES_SAMPLER, OTEL_PROPAGATORS, etc.
- https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/ — OTLP exporter env vars (endpoint/headers/timeout/protocol)
- https://opentelemetry.io/docs/collector/ — Collector docs site map
- https://opentelemetry.io/docs/collector/architecture/ — receivers/processors/exporters, pipelines, agent/gateway
- https://opentelemetry.io/docs/collector/configuration/ — Collector YAML structure, env var substitution
- https://opentelemetry.io/docs/collector/deploy/ — deployment pattern summaries (agent/gateway/other)
- https://opentelemetry.io/docs/collector/scaling/ — scaling guidance, metrics to monitor, Target Allocator
- https://opentelemetry.io/docs/collector/resiliency/ — sending queues, WAL persistence, Kafka message queue
- https://opentelemetry.io/docs/collector/troubleshooting/ — debug exporter, internal telemetry, zPages
- https://opentelemetry.io/docs/security/ — Collector security hub page
- https://opentelemetry.io/docs/security/config-best-practices/ — secret storage, TLS/auth, localhost-binding default
- https://opentelemetry.io/docs/security/handling-sensitive-data/ — data minimization, redaction/attribute/filter/transform processors, hashing caveat
- https://opentelemetry.io/docs/compatibility/migration/ — OpenTracing shim, OpenCensus bridge, Jaeger migration
- https://opentelemetry.io/ecosystem/vendors/ — vendor/backend directory (Grafana, Sentry, Prometheus, Jaeger, Datadog, etc.)
- https://opentelemetry.io/blog/2026/go-logs-api-sdk-rc/ — Go Logs API/SDK release-candidate announcement
- https://github.com/open-telemetry — organization page, multi-repo structure
- https://github.com/open-telemetry/opentelemetry-specification/releases — spec release history
- https://github.com/open-telemetry/opentelemetry-collector/releases — Collector core release history
- https://raw.githubusercontent.com/open-telemetry/opentelemetry-js/main/CHANGELOG.md — JS SDK v2.0.0 breaking-change inventory
- https://github.com/open-telemetry/opentelemetry-js/releases — JS SDK release history
- https://github.com/open-telemetry/opentelemetry-python/releases — Python SDK release history
- https://github.com/open-telemetry/opentelemetry-go/releases — Go SDK release history
