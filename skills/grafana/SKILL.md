---
name: Grafana
description: >-
  Grafana-specific dashboard/panel/variable mechanics, data-source plugin
  model, unified alerting vs. Prometheus Alertmanager, and dashboards-as-
  code/provisioning. Use when the stack includes Grafana (grafana.ini,
  docker image grafana/grafana(-enterprise), provisioning/ dashboards,
  Grafana data-source config) or the task names Grafana dashboards/alerts.
  Not for generic observability method (use observability), PromQL/
  Prometheus internals, or OpenTelemetry instrumentation.
spec_version: "1.0"
---

## Purpose & scope

Apply Grafana correctly for the version in use as the visualization/
dashboarding/alerting layer over external data sources. The *method* for
choosing what to observe comes from the parent skill
([observability](../observability/SKILL.md), `SK-QA-004`); this skill
supplies Grafana's dashboard/panel/variable mechanics, its plugin-based
data-source model, unified alerting architecture, and provisioning-as-code.

## When to use / When not to use

**Use** when a Grafana config file (`grafana.ini`), Docker image
(`grafana/grafana` or `grafana/grafana-enterprise`), `provisioning/`
directory, or dashboard JSON is present, or the task names Grafana
dashboards, panels, variables, alerting, or data sources. **Do not use**
for PromQL/Prometheus server internals with no Grafana visualization
concern (route to [prometheus](../prometheus/SKILL.md)), OpenTelemetry
instrumentation with no Grafana concern (route to
[opentelemetry](../opentelemetry/SKILL.md)), or signal-selection/alert-
design method and cardinality/PII discipline in the abstract — that's owned
by [observability](../observability/SKILL.md); this skill does not repeat it.

## Knowledge

**Grafana is not a data store.** It queries external systems through a
plugin framework and renders results — "it queries, visualizes, alerts on,
and explores your metrics, logs, and traces wherever they are stored"
[Source: https://grafana.com/docs/grafana/latest/introduction/]. Documented
plugin-connected examples go beyond time-series backends to NoSQL/SQL
databases, Jira/ServiceNow, and GitLab
[Source: https://grafana.com/docs/grafana/latest/introduction/]. This is a
structural limitation, not a bug: a slow or unavailable data source degrades
or breaks the dashboard experience regardless of Grafana itself
[Source: https://grafana.com/docs/grafana/latest/datasources/].

**Dashboard/panel/variable model.** A **dashboard** is "a set of one or more
panels, organized and arranged into one or more rows or tabs"; a **panel**
is "the container that displays the visualization"
[Source: https://grafana.com/docs/grafana/latest/dashboards/]. Eight
documented **variable** types let dashboards be parameterized instead of
duplicated: Query, Custom, Text box, Constant, Data source, Interval,
Filters, Switch — including using a Data source variable to "reuse the same
dashboard across different clusters and monitoring backends"
[Source: https://grafana.com/docs/grafana/latest/dashboards/variables/].
Since v12.2.0, dashboard JSON has three coexisting representations —
pre-v12.2.0 Classic model, a V1 Resource (Classic wrapped in a
Kubernetes-style resource), and a V2 Resource (current schema, advanced
layouts/conditional rendering) — and as-code tooling is fully compatible
only with V2 [Source: https://grafana.com/docs/grafana/latest/dashboards/
build-dashboards/view-dashboard-json-model/] (applies_to: >=12.2.0).

**Data-source plugin model: no universal query language.** "A data source
in Grafana is a connection to a storage backend... such as a Prometheus
server, a Loki instance, a SQL database, or a cloud monitoring service."
Each data source exposes its own query editor — Grafana does not impose one
query language across sources
[Source: https://grafana.com/docs/grafana/latest/datasources/]. Built-in
categories span metrics/time-series (Prometheus, Graphite, InfluxDB,
CloudWatch, Azure Monitor, GCM, OpenTSDB), logs (Loki, Elasticsearch),
traces (Tempo, Jaeger, Zipkin), profiles (Parca, Pyroscope), SQL databases
(PostgreSQL, MySQL, MSSQL), and alerting (Alertmanager)
[Source: https://grafana.com/docs/grafana/latest/datasources/]. The
Prometheus data source is preinstalled; as of **13.2** it is packaged as a
standalone plugin rather than built into the Grafana codebase, so it can
update independently of full Grafana releases
[Source: https://grafana.com/docs/grafana/latest/datasources/prometheus/]
(applies_to: >=13.2).

**Unified alerting vs. Prometheus Alertmanager — a real, easy-to-conflate
distinction.** Grafana ships its own embedded **Grafana Alertmanager**
that "extends the Prometheus Alertmanager" rather than being a thin
passthrough; alerting can also forward to an **external** Alertmanager,
added as a data source, "to forward Grafana-managed alerts to the same
Alertmanager for unified notification handling"
[Source: https://grafana.com/docs/grafana/latest/alerting/fundamentals/
alertmanager/]. **Rule evaluation always happens inside Grafana itself**
(against any configured data source, not only Prometheus); **notification
routing/grouping/silencing** can be handled by either engine
[Source: https://grafana.com/docs/grafana/latest/alerting/fundamentals/].
Do not conflate "Grafana Alerting" with "Prometheus's Alertmanager" — they
are two distinct, swappable layers.

**Exemplars** are the concrete metric-to-trace linking mechanism: "a
specific trace representative of measurement taken in a given time
interval," surfaced as highlighted stars in Explore/dashboards and linking
onward into Tempo. Exemplars are currently **Prometheus-only** as a data
source [Source: https://grafana.com/docs/grafana/latest/fundamentals/
exemplars/].

**Provisioning-as-code.** File-based YAML provisioning under
`provisioning/datasources`, `provisioning/dashboards`,
`provisioning/plugins` is polled (>10s interval) or filesystem-watched
(<=10s) [Source: https://grafana.com/docs/grafana/latest/administration/
provisioning/]. Beyond that, Grafana documents a broader "as-code"
ecosystem — **Terraform**, **Ansible**, the **Grafana Operator**, and
**Grizzly** — for observability-as-code and infrastructure-as-code,
syncing to Git and deploying via CI/CD
[Source: https://grafana.com/docs/grafana/latest/as-code/].

**Feature maturity lifecycle vs. version-support window — two orthogonal
axes.** Separately from version support, Grafana Labs documents a
**feature maturity lifecycle**: Experimental ("Not supported; OSS users
can create issues in GitHub"), Private preview, Public preview
("enablement, configuration, and some troubleshooting support"), and
General Availability ("Fully supported / on-call" with SLA coverage)
[Source: https://grafana.com/docs/release-life-cycle/]. A release on a
fully-supported major/minor can still contain an Experimental-maturity
*feature* — check both axes before relying on something in production, not
just the version-support tier.

**Version-support policy** (distinct from the above): minor releases ship
every other month (features/bugfixes/security), major releases yearly
(April/May), patch releases at least monthly. Each minor is supported 9
months; the **final minor of a major gets 15 months** — a policy shaped
like LTS but **not branded "LTS" anywhere found in official docs**
[Source: https://grafana.com/docs/grafana/latest/upgrade-guide/
when-to-upgrade/] — treat "LTS" as informal shorthand, not an official term,
if you use it at all. Current line at research time: **Grafana 13**, 13.2
most recent documented minor [Source: https://grafana.com/docs/grafana/
latest/whatsnew/].

**Unresolved:** the widely-used "LGTM stack" acronym (Loki, Grafana, Tempo,
Mimir) was **not found verbatim** on any official grafana.com/docs page
checked in the underlying research, despite the four-component architecture
(plus Pyroscope for profiles) being fully documented under OpenTelemetry/
OTLP ingestion pages: OTLP data sent to Grafana is "converted to
Prometheus/Mimir, Loki, and Tempo" internally, and Grafana then queries
those backends like any other data source
[Source: https://grafana.com/docs/opentelemetry/]. Name the components
explicitly rather than citing "LGTM stack" as if it resolves to an official
docs anchor.

## Decision framework

1. **Simplest first:** for a single dashboard viewed by one team against one
   data source, plain UI-built dashboards or basic file-based provisioning
   is enough — don't reach for Terraform/Operator/Grizzly until multiple
   environments or teams need the same config reproduced and reviewed in
   Git.
2. **File-based provisioning vs. Terraform/Operator-based as-code:** choose
   file-based YAML provisioning when the team just needs dashboards/data
   sources to survive a redeploy from a single repo; choose Terraform,
   Ansible, the Grafana Operator, or Grizzly when dashboards/data sources
   must be managed alongside other infrastructure-as-code, across multiple
   Grafana instances, or need `plan`-style review before apply
   [Source: https://grafana.com/docs/grafana/latest/as-code/]. Both are
   real, documented paths; the docs do not state a universal preference
   (Unresolved, per research) — pick based on the team's existing IaC
   workflow, not a default.
3. **Built-in Grafana Alertmanager vs. external Alertmanager:** keep the
   built-in engine when Grafana is the only place alerts are defined and
   routed; forward to an external (e.g., standalone Prometheus)
   Alertmanager when notification routing must be shared with systems
   outside Grafana or an existing Alertmanager investment must be reused
   [Source: https://grafana.com/docs/grafana/latest/alerting/fundamentals/
   alertmanager/]. Rule evaluation stays in Grafana either way — don't
   present this as an evaluation-engine choice.
4. **Before relying on a specific feature in production**, check its
   maturity-lifecycle tier (Experimental/Preview/GA) independently of
   whether the Grafana version itself is under Full Support — a
   fully-supported version can still ship an Experimental feature with no
   SLA [Source: https://grafana.com/docs/release-life-cycle/].
5. **Do nothing / no dashboard-as-code branch:** if the team has one
   Grafana instance, few dashboards, and no multi-environment reproduction
   need, UI-authored dashboards with provisioning disabled are a
   legitimate simplest option — don't impose as-code tooling preemptively.

## Engineering rules

- Parameterize dashboards with variables (Query/Custom/Data source/etc.)
  instead of copy-pasting; a Data source variable lets one dashboard target
  multiple clusters/backends [Source: https://grafana.com/docs/grafana/
  latest/dashboards/variables/].
- Treat the provisioning file, not the live UI, as the source of truth for
  any provisioned dashboard — UI edits are discarded on the next
  provisioning sync unless the workflow explicitly accounts for
  `allowUiUpdates` [Source: https://grafana.com/docs/grafana/latest/
  administration/provisioning/].
- Address data sources by `uid`, not numeric `id` — the legacy id-based API
  is disabled by default as of Grafana **13.0** [Source: https://
  grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v13-0/]
  (applies_to: >=13.0.0).
- Keep panels focused and simple; don't cram unrelated queries into one
  panel/dashboard [Source: https://grafana.com/docs/grafana/latest/
  dashboards/build-dashboards/best-practices/].
- State which Grafana major.minor a piece of guidance targets; never assume
  "latest" silently, especially around alerting (v11.0.0 boundary) and
  v13.0.0 breaking changes.

## Trade-offs

Built-in Grafana Alertmanager is simpler to operate (one system, one UI)
but ties notification routing to Grafana; an external Alertmanager adds
operational surface but lets routing be shared across systems that don't
go through Grafana. File-based provisioning is lower-ceremony than
Terraform/Operator/Grizzly but lacks their plan/diff/rollback tooling and
doesn't scale as cleanly across many Grafana instances. Query/resource
caching speeds up dashboards with many concurrent viewers, but the benefit
is data-source-dependent: "some databases like Elasticsearch and
Prometheus cache queries themselves, so Grafana query caching does not
significantly improve performance" against them
[Source: https://grafana.com/docs/grafana/latest/administration/
data-source-management/].

## Anti-patterns

- **Manually editing a provisioned dashboard in the UI without updating its
  source-of-truth JSON.** "Grafana always overwrites the database dashboard
  with the one from the provisioning file" on the next sync, silently
  discarding the UI edit [Source: https://grafana.com/docs/grafana/latest/
  administration/provisioning/].
- **Copy-pasting dashboards instead of parameterizing with variables.**
  "Copying dashboards with no significant changes is not a good idea. You
  miss out on updates to the original dashboard" [Source: https://
  grafana.com/docs/grafana/latest/dashboards/build-dashboards/
  best-practices/].
- **Overloaded, unfocused panels** instead of panels kept "simple and
  focused on answering the question that you are asking" [Source: https://
  grafana.com/docs/grafana/latest/dashboards/build-dashboards/
  best-practices/] — the domain's over-engineering trap: one sprawling
  do-everything dashboard instead of composable, purpose-built ones.
- **Relying on numeric `id`-based data source API calls** instead of
  `uid`-based ones — disabled by default as of Grafana 13.0
  [Source: https://grafana.com/docs/grafana/latest/whatsnew/
  whats-new-in-v13-0/] (applies_to: >=13.0.0).

(Alert-fatigue causes and ownerless-alert anti-patterns are owned by
[observability](../observability/SKILL.md); not repeated here.)

## Security

Data-source secrets (credentials used to query data sources, send alert
notifications, etc.) are encrypted at rest using **envelope encryption**
since v9.0+: per-secret data encryption keys (DEKs) are themselves
encrypted by a key encryption key (KEK), defaulting to **AES-CFB**; Grafana
Enterprise supports external KMS integration (AWS KMS, Azure Key Vault,
Google Cloud KMS, HashiCorp Key Vault) and can switch the cipher mode to
**AES-GCM** [Source: https://grafana.com/docs/grafana/latest/setup-grafana/
configure-security/configure-database-encryption/].

Grafana Labs publishes CVE-numbered advisories; a documented critical
example is **CVE-2026-27876 (Critical, 9.1)** — remote code execution
"RCE on Grafana via sqlExpressions" [Source: https://grafana.com/security/
security-advisories/]. Treat CVE claims as time-sensitive: re-check the
advisories page before relying on any specific CVE status. Deep threat
modeling beyond Grafana-specific secret handling is owned by
`security-engineering` (`SK-QA-002`), referenced not restated.

## Performance

Query/resource caching (in-memory, Redis, Memcached) is Grafana's primary
documented dashboard-performance lever, reducing repeat load on the data
source when many viewers hit the same dashboard: "Grafana Enterprise
includes query caching, which can significantly reduce this multiplier
when many users view the same dashboard simultaneously"
[Source: https://grafana.com/docs/grafana/latest/setup-grafana/
installation/]. The benefit is data-source-dependent, not universal — see
Trade-offs. No documented Grafana-side (as opposed to data-source-side)
query-concurrency limit or dashboard/panel sizing guideline was found in
the underlying research (Unresolved). Broader cross-cutting performance
method is owned by `performance-engineering` (`SK-QA-003`).

## Testing

Genuinely thin in official docs: the Grafana CLI's command surface covers
only plugin management and admin tasks (e.g., `grafana cli plugins
install`, `grafana cli admin reset-admin-password`) — it does **not**
expose a documented dashboard/provisioning-config validation or dry-run
subcommand [Source: https://grafana.com/docs/grafana/latest/cli/]. Grafana
itself documents no first-party testing framework for dashboard JSON,
provisioning YAML, or alert-rule definitions; validation is left to
whichever as-code tool is used (e.g., `terraform plan` for Terraform-based
provisioning), which is outside Grafana's own docs. State this honestly
rather than inventing a testing story; verify a dashboard/alert change by
checking it renders/fires as expected in a non-production instance before
promoting it.

## Failure handling

- If the Grafana major.minor version cannot be determined, ask for it or
  state the version the guidance assumes — never assume "latest" silently,
  especially around the v11.0.0 alerting removal and v13.0.0 breaking
  changes.
- If shell is unavailable/denied, degrade to advisory dashboard JSON/
  provisioning YAML/alert-rule output and say that provisioning, CLI, or
  upgrade commands were not run.
- If the request is actually about signal-selection, alert-design method,
  or cardinality/PII discipline rather than Grafana mechanics, defer to
  [observability](../observability/SKILL.md) rather than restating its
  content here.

## Escalation

- **Crossing the legacy-alerting boundary** (any version <11.0.0 upgrading
  to >=11.0.0) requires explicit confirmation and a completed migration
  (Upgrade with Preview or Simple Upgrade) first: "Installing Grafana 11
  before upgrading your legacy alerts will result in your existing alerts
  becoming inaccessible or lost" [Source: https://grafana.com/docs/grafana/
  latest/alerting/set-up/migrating-alerts/] (applies_to: >=11.0.0).
- **Upgrading a v12.x instance with Git Sync enabled to v13.0.0** requires
  flagging a real, documented upgrade risk before proceeding: "A migration
  bug in v13.0.0 may cause dashboards and folders to be lost when upgrading
  from v12.x with Git Sync enabled" [Source: https://grafana.com/docs/
  grafana/latest/whatsnew/whats-new-in-v13-0/] (applies_to: =13.0.0,
  upgrading from >=12.0 with Git Sync enabled) — confirm a backup/rollback
  path exists before this specific upgrade.

## Outputs & verification

- **Outputs:** dashboard JSON/provisioning YAML or as-code (Terraform/
  Ansible/Grizzly) changes; alert-rule or notification-routing config;
  analysis of data-source/alerting/upgrade decisions with the version they
  apply to.
- **Verify:** a provisioned dashboard's source-of-truth file matches what's
  live (no silently-overwritten UI drift); dashboards use variables instead
  of copy-paste duplication; alerting recommendations correctly separate
  rule evaluation (always Grafana) from notification routing (Grafana
  Alertmanager or external); every version-specific claim is tagged with
  the range it holds for and matches the target version.

## References

- [research/technologies/grafana.md](../../research/technologies/grafana.md) — primary research source (82 citations, Sections 1–17 plus Unresolved Items)
- [observability](../observability/SKILL.md) — parent skill (signal-selection, alert-design method, cardinality/PII discipline)
- [prometheus](../prometheus/SKILL.md) — PromQL/scrape/Alertmanager internals (sibling; Prometheus is Grafana's preinstalled first-class data source)
- [opentelemetry](../opentelemetry/SKILL.md) — OTLP instrumentation ingested into Grafana's Loki/Tempo/Mimir components (sibling)
