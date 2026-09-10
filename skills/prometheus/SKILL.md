---
name: Prometheus
description: >-
  Prometheus-specific PromQL, scrape/relabel config, the four metric
  types (Counter/Gauge/Histogram/Summary, native vs. classic
  histograms), cardinality guardrails, non-HA storage architecture,
  Alertmanager HA, and promtool testing. Use when prometheus.yml, a
  Prometheus server, /metrics scraping, PromQL, or Alertmanager is in
  play. Not for OpenTelemetry instrumentation, Grafana dashboards, or
  generic signal-selection/alert-design method (SK-QA-004).
spec_version: "1.0"
---

## Purpose & scope

Apply Prometheus correctly and version-appropriately: PromQL mechanics,
precise metric-type semantics, scrape/cardinality configuration, and its
single-node storage/HA architecture. The cross-technology *method* (which
signal to reach for, cardinality/PII discipline as a concept, alert-design
philosophy) comes from the parent skill,
[observability](../observability/SKILL.md) (`SK-QA-004`); this skill
supplies Prometheus's own implementation depth on top of it.

## When to use / When not to use

**Use** when a `prometheus.yml` config, a running Prometheus server, a
scraped `/metrics` endpoint, PromQL, Alertmanager, or `promtool` is in
play, or the task instruments a client library for Prometheus scraping.
**Do not use** when there is no Prometheus component in the stack and
none is requested; for OpenTelemetry instrumentation/collector work with
no Prometheus backend (route to `SK-TECH-opentelemetry`); for Grafana
dashboard/panel authoring rather than the Prometheus server or PromQL
itself (route to `SK-TECH-grafana`); or for generic signal-selection/
cardinality/alert-design method with no Prometheus specifics (route to
`SK-QA-004`).

## Knowledge

**Pull over push, with one accommodation.** "Time series collection
happens via a pull model over HTTP" — pull is the default and primary
model [Source: https://prometheus.io/docs/introduction/overview/]. The
Pushgateway exists only for short-lived batch jobs that cannot be
scraped normally: batch jobs push metrics *to* the Pushgateway, and the
Pushgateway itself is then scraped like any other target
[Source: https://prometheus.io/docs/instrumenting/pushing/]. Do not use
the Pushgateway as a general ingestion path for long-running services.

**The four metric types, precisely.** [Source: https://prometheus.io/docs/concepts/metric_types/]
**Counter** — "can only increase or be reset to zero on restart." Never
use it for a value that can decrease; use a **Gauge** instead, which "can
arbitrarily go up and down." **Histogram** records observations into
buckets and comes in two forms: **native histograms** (dynamic buckets,
exposed as a composite sample, "generally much more efficient... allow
much higher resolution, do not require explicit configuration of bucket
boundaries," recommended over classic histograms when the instrumentation
library supports them — currently Go and Java) and **classic histograms**
(multiple plain float series: `_bucket{le=...}`, `_sum`, `_count`). A
hybrid, Native Histograms with Custom Bucket boundaries (NHCB), lets
Prometheus ingest classic-histogram data into the more efficient native
storage representation. **Summary** also computes quantiles, but does so
client-side over a sliding window — unlike histogram buckets, summary
quantiles are **not aggregatable across instances**, a real and easy-to-miss
distinction when choosing between the two for a value queried across a
fleet.

**Not clustered, not natively HA — a defining architectural fact, not a
gap to work around.** "A limitation of local storage is that it is not
clustered or replicated. Thus, it is not arbitrarily scalable or durable
in the face of drive or node outages and should be managed like any other
single node database" [Source: https://prometheus.io/docs/prometheus/latest/storage/].
HA is achieved by running "identical Prometheus servers on two or more
separate machines," with deduplication of the resulting redundant data
handled by systems like Thanos or by remote-write-capable long-term-storage
backends, not by Prometheus itself
[Source: https://prometheus.io/docs/introduction/faq/]. Beyond a single
node, the documented paths are **federation** (`/federate`, for
hierarchical or cross-service aggregation across tens of datacenters)
[Source: https://prometheus.io/docs/prometheus/latest/federation/] and
**remote-write/remote-read** to a dedicated long-term-storage backend —
Thanos, Cortex, and Grafana Mimir are all named explicitly as documented
integrations [Source: https://prometheus.io/docs/operating/integrations/].

**PromQL basics.** A query is either an instant query (one point in time)
or a range query (equally-spaced steps); selectors filter by label match
(`=`, `!=`, `=~`, `!~`, regexes fully anchored, RE2 syntax); range vectors
append a bracketed duration, e.g. `http_requests_total[5m]`; the `offset`
and `@` modifiers shift or pin evaluation time; subqueries
(`<query>[<range>:<resolution>]`) run an instant query repeatedly over a
range [Source: https://prometheus.io/docs/prometheus/latest/querying/basics/].
Staleness uses the newest sample within a lookback window (default 5m,
`--query.lookback-delta`); build ad-hoc queries in tabular view first and
pre-record expensive expressions as recording rules rather than running
large aggregations live — "expressions that aggregate over many time
series will generate load on the server even if the output is only a
small number of time series" (same source).

Deep PromQL/config mechanics (relabeling action reference, remote-write
queue tuning, OTLP translation-strategy values) live in
[research/technologies/prometheus.md](../../research/technologies/prometheus.md)
— loaded only when needed.

## Decision framework

1. **Native vs. classic histograms:** if the instrumentation library
   supports native histograms (currently Go and Java), prefer them — they
   are more efficient, higher-resolution, and don't require pre-configuring
   bucket boundaries. Otherwise, use classic histograms and set bucket
   boundaries deliberately from the actual latency/size distribution, not
   a copied default.
2. **Counter vs. Gauge:** if the value can ever decrease (concurrent
   requests, memory usage, queue depth), it is a Gauge, never a Counter.
3. **Histogram vs. Summary:** if quantiles need to be aggregated across
   instances (the normal case for a fleet), use a Histogram — Summary
   quantiles are computed client-side and cannot be combined.
4. **Single-node retention vs. federation/remote-write:** start with
   local storage; Prometheus itself pushes back on "doesn't scale"
   framing and documents running reliably with tens of millions of active
   series on one instance. Reach for federation when you need
   cross-datacenter aggregation, and for remote-write to Thanos/Cortex/
   Mimir specifically when you need durability beyond a single node or
   retention longer than local disk can reasonably hold — not by default.
5. **Version gate before any v2->v3 upgrade:** confirm the exact current
   version. If below v2.55, upgrade to 2.55 first and confirm stability;
   only then move to v3 — going straight from an older v2.x to v3 risks
   losing persistent TSDB data on any later downgrade attempt.

## Workflow

1. Determine the Prometheus major/minor version in use (or state the
   assumed version) before recommending anything version-gated.
2. For instrumentation: pick the metric type from the value's actual
   semantics (Decision framework above), not habit.
3. For scrape configs: set `sample_limit`/`label_limit`/
   `label_name_length_limit`/`label_value_length_limit`/`target_limit`
   alongside any new job, so a cardinality blowup fails the scrape loudly
   instead of silently growing the TSDB.
4. For rules: write the rule, then write a `promtool test rules` case for
   it before considering it done (Testing, below).
5. For HA/scale needs: apply the Decision framework's step 4 rather than
   defaulting to "add more Prometheus."
6. Verify (Outputs & verification) before declaring done.

## Engineering rules

- Never use a Counter for a value that can decrease — use a Gauge.
- Prefer native histograms over classic histograms wherever the client
  library supports them (currently Go, Java).
- Never choose Summary when quantiles need to be aggregated across
  instances — use a Histogram instead.
- Set per-scrape-config cardinality limits (`sample_limit`, `label_limit`,
  `label_name_length_limit`, `label_value_length_limit`, `target_limit`)
  on any job with realistic cardinality risk; they fail the whole scrape
  rather than silently truncating, which is the point.
- Configure every Alertmanager instance directly in Prometheus's
  `alerting.alertmanagers`; never put a load balancer in front of an
  Alertmanager cluster.
- Never grow local retention indefinitely as a substitute for federation
  or remote-write once durability or cross-node query needs actually
  require it.

## Trade-offs

Native histograms are more efficient and higher-resolution than classic
histograms but are only supported by a subset of client libraries (Go,
Java) at present — classic histograms remain the necessary choice
elsewhere, at the cost of manually chosen, statically-configured bucket
boundaries. Running Prometheus as a single-node, non-clustered system is
operationally simple and matches its documented design, but pushes the
durability/HA burden onto redundant independent replicas plus an external
deduplicating system (Thanos) or a remote-write backend (Cortex/Mimir) —
composing more moving parts than a clustered database would need, in
exchange for the isolation benefit the docs cite: independent servers
"may also give you better reliability and failure isolation"
[Source: https://prometheus.io/docs/introduction/comparison/].

## Anti-patterns

- **Treating local storage as arbitrarily durable/scalable** — it is
  explicitly documented as not clustered or replicated and should be
  "managed like any other single node database."
- **Putting a load balancer in front of Prometheus-to-Alertmanager
  traffic** — the documented guidance is explicit: "Don't use a load
  balancer / Configure all instances in Prometheus"
  [Source: https://prometheus.io/docs/alerting/latest/high_availability/];
  a load balancer reintroduces the single point of failure the HA design
  eliminates and breaks the peer-position-based deduplication the cluster
  relies on.
- **Using Summary where cross-instance aggregation is needed** — its
  quantiles are computed client-side and are not aggregatable, unlike
  histogram buckets.
- **Growing local retention indefinitely instead of using federation/
  remote-write** once durability or multi-node query needs genuinely
  exceed what a single node should carry — the domain's own
  over-engineering trap runs in both directions: reaching for a
  distributed long-term-storage stack (Thanos/Cortex/Mimir) before a
  single well-sized instance's retention and query load actually require
  it is equally a mistake, since Prometheus documents running reliably
  with tens of millions of active series on one instance.
- **Exposing Prometheus's HTTP endpoints directly to the public internet**
  (see Security).

## Security

Prometheus's own security-model page states endpoints including
`/metrics`, API endpoints, and Go's `/pprof` "should not be exposed to
publicly accessible networks like the internet... unless you know what
you are doing and have taken appropriate measures," because it is "easily
possible to overload and ultimately DoS servers with requests to these
endpoints" [Source: https://prometheus.io/docs/operating/security/].
Native TLS/basic-auth support exists but is documented as experimental:
"Prometheus supports basic authentication and TLS. This is experimental
and might change in the future," configured via a separate
`--web.config.file` re-read on every request
[Source: https://prometheus.io/docs/prometheus/latest/configuration/https/].
The threat model presumes "untrusted users have access to the Prometheus
HTTP endpoint" get read access to all time-series data, while only
trusted users should be able to change config/rule files; the
administrative API (`--web.enable-admin-api`) and lifecycle endpoints
(`--web.enable-lifecycle`) are disabled by default for this reason
[Source: https://prometheus.io/docs/operating/security/]. Untrusted input
interpolated into PromQL (e.g. console-template parameters) must be
escaped to prevent label-matcher injection (same source). Broader
cross-cutting threat modeling is owned by `SK-QA-002`, not restated here.

## Performance

Beyond the parent skill's cardinality/sample-rate synthesis, Prometheus's
own config-level guardrails are the concrete lever: `sample_limit`,
`label_limit`, `label_name_length_limit`, `label_value_length_limit`, and
`target_limit` on each scrape config all **fail the entire scrape** rather
than silently truncating once exceeded
[Source: https://prometheus.io/docs/prometheus/latest/configuration/configuration/].
`promtool check metrics --extended` performs cardinality analysis against
a metrics payload; `promtool tsdb analyze` analyzes "churn, label pair
cardinality and compaction efficiency" directly against an on-disk TSDB
[Source: https://prometheus.io/docs/prometheus/latest/command-line/promtool/].
When ingestion volume needs to shrink, prefer reducing the number of
scraped series over lengthening the scrape interval — compression makes
per-series overhead, not raw sample count, the dominant cost driver
[Source: https://prometheus.io/docs/prometheus/latest/storage/]. Beyond a
single node's capacity, federation and remote-write to a long-term-storage
backend (Thanos/Cortex/Grafana Mimir) are the documented scaling paths
(see Knowledge, above) — deeper cross-cutting performance method is owned
by `SK-QA-003`.

## Testing

`promtool test rules` is Prometheus's actual, documented answer to
testing alerting and recording rules
[Source: https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/].
A test file (`promtool test rules test.yml`) declares `rule_files` under
test, an `evaluation_interval`, and a list of `tests`; each test group
supplies `input_series` using a compact notation (e.g. `'-2+4x3'` expands
to four samples starting at -2, incrementing by 4) and asserts either
`alert_rule_test` cases (the exact set of firing alerts with expected
labels/annotations at a given `eval_time`) or `promql_expr_test` cases
(expected samples for an arbitrary PromQL expression at a given
`eval_time`). A `start_timestamp` anchors `time()` so tests are fully
deterministic. `promtool check rules`/`promtool check config` validate
syntax offline before a rule or config file is ever loaded by a live
server, and `promtool check service-discovery` reports the targets a
given job would resolve to, including relabeling — useful for debugging
relabel logic without a live scrape. No first-party
`prometheus.io`-hosted container/Docker deployment best-practices guide
was found in this skill's research (unlike, e.g., Node.js's dedicated
working-group document); treat container packaging as ordinary
Dockerfile practice (`SK-TECH-docker`) rather than expecting
Prometheus-specific container guidance.

## Failure handling

- If the Prometheus version in use is unknown, ask or explicitly state
  the assumed version — never assume "latest" silently — and flag the
  v2.55/v3.0 TSDB-read-compatibility boundary before recommending any
  upgrade.
- If shell is unavailable, output advisory config/PromQL/promtool text
  and state that it was not actually executed.
- If the request is actually generic signal-selection or alert-design
  philosophy with no Prometheus specifics, defer to `SK-QA-004` rather
  than restating it.

## Escalation

- A v2.x -> v3.0 upgrade plan requires explicit confirmation of the
  current version before proceeding, given the documented risk of
  irreversibly losing persistent TSDB data if the server is below v2.55.

## Outputs & verification

- **Outputs:** version-correct scrape/relabel/rule config, PromQL
  queries, or analysis (metric-type choice, cardinality guardrails, HA/
  federation stance, upgrade risk).
- **Verify:** every version-specific claim states its range (especially
  the TSDB v2.55 boundary and the v2->v3 PromQL regex/lookback semantic
  changes); any proposed Alertmanager HA config lists every instance
  directly in Prometheus, never behind a load balancer; any scrape config
  with realistic cardinality risk sets the relevant limit fields.

## References

- [research/technologies/prometheus.md](../../research/technologies/prometheus.md) — full research doc (93 citations).
- Source list: see `skill.yaml.source_references` (Prometheus official
  docs, retrieved 2026-09-10).
- Parent: [observability](../observability/SKILL.md) (`SK-QA-004`).
- Related: `SK-TECH-opentelemetry` (OTLP source feeding Prometheus's
  receiver), `SK-TECH-grafana` (native Prometheus data source since
  Grafana 2.5.0).
