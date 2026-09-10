---
name: Observability
description: >-
  Instrument systems for logging, metrics, tracing, and error monitoring —
  choose the right signal(s) for the diagnostic need, avoid high-cardinality
  and PII-leakage pitfalls, and design actionable alerting. Use when making
  a system diagnosable in production or debugging a production issue.
  Explicitly does not cover resilience/fault-tolerance patterns (retries,
  circuit breakers), a separate, still-unresearched gap in this library.
spec_version: "1.0"
---

## Purpose & scope

Instrument systems with logging, metrics, tracing, and error monitoring so
production behavior is diagnosable — tool-neutral, specialized by
[opentelemetry](../opentelemetry/SKILL.md), [prometheus](../prometheus/SKILL.md),
[grafana](../grafana/SKILL.md), and [sentry](../sentry/SKILL.md) for
implementation depth. **This skill was authored after closing a real,
documented research gap**: the original taxonomy design found near-zero
grounding for observability (only fragmentary Docker log-aggregation and
OpenSearch log-analytics content), and held the skill until a dedicated
research pass on these four technologies could ground it properly. **A
second, narrower gap remains explicitly open and is not covered here**:
application-level resilience/fault-tolerance patterns (retries, circuit
breakers, timeouts, bulkheads, graceful degradation) are a genuinely
different discipline from observability — visibility into behavior vs.
behavior under failure — and no resilience-pattern library or framework
has been researched in this library. This skill says so rather than
improvising resilience guidance to fill that separate gap.

## When to use / When not to use

**Use** when making a system diagnosable in production, debugging a
production issue that needs logging/metrics/tracing evidence, or adding/
reviewing an observability instrumentation layer. **Do not use** for
local/throwaway code with no production diagnosability need, or for a
resilience/fault-tolerance-pattern request — state that gap explicitly.

## Knowledge

**The three (now four) observability pillars have a real structural
boundary worth understanding before instrumenting anything: collection/
instrumentation is architecturally separate from storage/visualization.**
OpenTelemetry states this as a first-principle design choice: "OpenTelemetry
is not an observability backend itself. The backend (storage) and the
frontend (visualization) of telemetry data are intentionally left to other
tools" [Source: opentelemetry.io/docs/what-is-opentelemetry/]. This is why
this library's stack spans four separate technologies rather than one —
OpenTelemetry standardizes what gets collected and how it's transported
(OTLP), Prometheus and Grafana own metrics storage and visualization,
and Sentry owns error/trace/session-level product surfaces. Understanding
which technology owns which layer prevents reaching for the wrong tool.

**Metrics, traces, and logs each have a distinct data shape and a distinct
right use — matching the signal to the diagnostic question is the central
skill here.** A **trace** represents the path of one request through a
system, composed of **spans** (units of work, each carrying timing,
attributes, and a parent link) — use tracing when the question is "where
did this specific request spend its time, and what did it call?"
[Source: opentelemetry.io/docs/concepts/signals/traces/]. A **metric** is
a measurement captured at runtime via one of several instrument kinds
(Counter, Gauge, Histogram) — use metrics when the question is "how is
this aggregate behavior trending over time?", not for investigating one
specific request [Source: opentelemetry.io/docs/concepts/signals/metrics/;
prometheus.io/docs/concepts/metric_types/]. A **log** is a timestamped
text record — OpenTelemetry's own docs note logs have "the biggest
legacy" of the three signals since virtually every language already emits
some form of logging, and its logs support is explicitly designed to
augment existing logging output (auto-correlating logs and traces via
injected trace/span IDs) rather than replace it
[Source: opentelemetry.io/docs/concepts/signals/logs/]. **Error
monitoring** (Sentry's issue model) is a fifth, complementary lens:
individual error events are grouped into "issues" via fingerprinting, so
a recurring bug shows as one trackable problem rather than a flood of
raw events — while still consuming quota per-event, not per-issue
[Source: docs.sentry.io/product/issues/].

**High-cardinality attributes/labels are the single most consistently
warned-against mistake across every one of these four technologies —
independently, not as a shared documented pattern.** Prometheus's naming
guidance carries an explicit CAUTION: "Do not use labels to store
dimensions with high cardinality (many different label values), such as
user IDs, email addresses, or other unbounded sets of values"
[Source: prometheus.io/docs/practices/naming/], enforced operationally via
`sample_limit`/`label_limit`/`label_value_length_limit` scrape-config
guardrails that fail the whole scrape rather than silently truncate.
OpenTelemetry's metrics SDK enforces a **default cardinality limit of
2000** unique attribute-combinations per instrument specifically to
prevent unbounded memory growth
[Source: opentelemetry.io/docs/concepts/signals/metrics/]. **Neither
source frames this as a shared cross-tool pattern — it recurs because
unbounded-cardinality attributes genuinely break every time-series-shaped
storage system the same underlying way**, not because the tools copied
each other's guidance.

**PII/sensitive-data leakage into telemetry is a real, specifically-named
risk across every signal type, not just logs.** OpenTelemetry's own
Baggage-propagation docs warn explicitly against putting "sensitive
information (like user credentials, API keys, or PII) in baggage, as it
might be logged or sent to untrusted downstream services"
[Source: opentelemetry.io/docs/concepts/context-propagation/]. Sentry
enumerates concrete risk locations beyond the obvious ones: stack-local
variable values captured in stack frames, breadcrumbs, HTTP query
strings, and transaction names that embed user IDs — with the documented
mitigation being proactive scrubbing in `beforeSend`/`beforeSendTransaction`
hooks, "to ensure that sensitive data never leaves the local environment,"
rather than relying on server-side scrubbing alone
[Source: docs.sentry.io/platforms/javascript/guides/node/data-management/
sensitive-data/]. **Hashing is explicitly flagged as insufficient
anonymization** by OpenTelemetry's own security docs — "hashes are
reversible in practice if the input space is small and predictable" —
truncation or omission is the recommended alternative for genuinely
sensitive fields [Source: opentelemetry.io/docs/security/
handling-sensitive-data/].

**Alert design has documented, specific failure modes worth checking
against by name, not just "tune your thresholds."** Grafana's alerting
best-practices name alert fatigue's concrete causes precisely: alerting on
"internal component behavior" instead of "user-facing failures," omitting
a pending period (causing flapping-condition noise), and never pruning
stale rules — with the explicit fix "schedule regular reviews of existing
alerts. Remove alerts that don't lead to action." **Every alert must have
an owner**: "a team responsible for maintaining the alert and responding
when it fires" — an ownerless alert is itself the anti-pattern
[Source: grafana.com/docs/grafana/latest/alerting/best-practices/].

**Sample-rate/volume control is a cost-and-signal-quality lever across
this whole stack, not just a Sentry-specific billing concern.** Sentry's
own guidance: "start with a low value and gradually increase it as you
learn more about your traffic patterns and volume" rather than defaulting
to 100% capture in production, since quota is consumed by events, not
issues [Source: docs.sentry.io/platforms/javascript/guides/node/
configuration/sampling/]. OpenTelemetry documents head vs. tail sampling
as the analogous trace-level lever. Prometheus's own FAQ pushes back on
"doesn't scale" framing directly while still recommending federation/
remote-write once a single instance's retention or query load grows
beyond what local storage handles well.

## Decision framework

1. **What's the actual diagnostic question?** "Where did this one request
   spend its time" → tracing. "How is aggregate behavior trending" →
   metrics. "What broke, grouped by root cause" → error monitoring
   (issues). "What exactly happened, in detail, around this moment" →
   logs. Don't default to logging everything when a different signal
   answers the question more precisely.
2. **Does the proposed attribute/label have bounded cardinality?** Raw
   user IDs, full URLs with query strings, and other unbounded-value
   fields should never become metric labels or high-volume span
   attributes — check this before instrumenting, not after a storage
   incident.
3. **Could this field contain PII or a secret?** If so, scrub it
   proactively at the SDK/application boundary (before it's sent), not
   only at a downstream server-side layer — and never rely on hashing
   alone for genuinely sensitive fields.
4. **Does every alert have a clear owner and a stated action?** If an
   alert exists that nobody would act on, or that nobody owns, remove it
   rather than letting it contribute to alert fatigue.
5. **Is the actual request about resilience/fault-tolerance patterns**
   (retries, circuit breakers, timeouts) rather than instrumentation/
   diagnosability? If so, state that this exceeds this skill's grounded
   scope rather than improvising.

## Workflow

1. Identify the actual diagnostic question(s) the instrumentation needs
   to answer.
2. Choose the signal(s) — logging, metrics, tracing, error monitoring —
   matched to those questions, not reflexively all four.
3. Design attributes/labels checking for cardinality bounds before
   implementation.
4. Scrub PII/secrets proactively at the point of capture, not only
   downstream.
5. Design alerting with a clear owner and action per alert; prune
   ownerless or non-actionable alerts.
6. Tune sample rates deliberately for cost/signal-quality trade-offs
   rather than defaulting to full capture.
7. Hand off implementation syntax to the relevant technology skill
   (opentelemetry/prometheus/grafana/sentry).
8. State plainly if the actual need is resilience patterns, not
   observability.

## Engineering rules

- Match the signal (logging/metrics/tracing/error-monitoring) to the
  actual diagnostic question, not reflexively instrumenting everything.
- Never attach unbounded-cardinality values as metric labels or high-volume
  span attributes.
- Scrub PII/secrets proactively at the point of capture; never rely on
  hashing alone for sensitive fields.
- Every alert has a clear owner and a stated action; prune alerts that
  don't lead to action.
- Tune sample rates deliberately rather than defaulting to full capture
  in production.

## Trade-offs

Full-fidelity capture (100% sampling, verbose logging) buys complete
visibility at real storage/cost/performance overhead; sampling buys
sustainable cost at the risk of missing a rare event unless the sampling
strategy accounts for it (e.g. tail sampling keeping error/slow traces
even at low overall sampling rates). Centralizing on one vendor/product
(e.g. Sentry alone) is simpler to operate than composing OpenTelemetry +
Prometheus + Grafana + Sentry, at the cost of vendor lock-in for the
instrumentation layer specifically — OpenTelemetry's vendor-neutral
instrumentation is the documented mitigation for that lock-in risk.

## Anti-patterns

- **Instrumenting reflexively with every signal** instead of matching
  signal choice to the actual diagnostic question.
- **Unbounded-cardinality metric labels/attributes** (raw user IDs, full
  URLs with query strings) — the single most consistently, independently
  warned-against mistake across every technology in this domain.
- **Relying on hashing alone to anonymize sensitive attributes** —
  explicitly documented as reversible for small/predictable input spaces.
- **Ownerless or non-actionable alerts** left in place, contributing to
  alert fatigue.
- **Defaulting to 100% sampling in production** without considering cost/
  signal-quality trade-offs.
- **Answering a resilience/fault-tolerance-pattern request as if it were
  observability instrumentation** — the domain's specific overreach trap,
  given this library's documented, separate research gap there.

## Security

PII/secrets scrubbing at the point of capture (SDK-level `beforeSend`-
style hooks, not only server-side) is this skill's own security-relevant
content — see Knowledge above. Deep threat modeling is owned by
[security-engineering](../security-engineering/SKILL.md).

## Performance

Sample-rate tuning and cardinality control are this skill's own
performance-relevant levers for the observability layer itself. Broader
cross-cutting performance method is owned by
[performance-engineering](../performance-engineering/SKILL.md).

## Testing

Whether instrumentation actually captures what's needed (a traced request
actually produces a complete trace, an alert actually fires under the
condition it's meant to catch) is the observability-specific testing
concern — verify explicitly rather than assuming instrumentation works
because it compiles. Deep test-strategy method is owned by
[testing-strategy](../testing-strategy/SKILL.md).

## Failure handling

- If SLOs/failure modes of concern aren't stated, ask rather than
  instrument reflexively.
- If the request is actually about resilience/fault-tolerance patterns,
  state that gap explicitly rather than answering as if it were
  observability instrumentation.

## Escalation

- A request for resilience/fault-tolerance-pattern guidance (retries,
  circuit breakers, timeouts, bulkheads) is escalated as a research gap
  requiring a dedicated pass, not answered from general knowledge.

## Outputs & verification

- **Outputs:** an instrumentation plan (what to log/measure/trace and
  why), and applied logging/metrics/tracing instrumentation.
- **Verify:** no PII/secrets leak into telemetry; no unbounded-cardinality
  labels/attributes; every alert has an owner and a stated action.

## References

- [research/technologies/opentelemetry.md](../../research/technologies/opentelemetry.md)
- [research/technologies/prometheus.md](../../research/technologies/prometheus.md)
- [research/technologies/grafana.md](../../research/technologies/grafana.md)
- [research/technologies/sentry.md](../../research/technologies/sentry.md)
