# Grafana — Deep Technology Reference

Research date: 2026-09-10. Primary source: the official Grafana documentation hosted
at `grafana.com/docs/grafana/latest/` (introduction, dashboards, panels-visualizations,
datasources, alerting, administration, setup-grafana, developers, upgrade-guide, and
whatsnew subtrees). Supplemented by Grafana Labs' official security-advisories page
(`grafana.com/security/security-advisories/`), the Grafana plugin catalog
(`grafana.com/grafana/plugins/`), and adjacent official docs for the LGTM-stack
components this task requires documenting as integration points — Loki
(`grafana.com/docs/loki/latest/`) and the OpenTelemetry/OTLP ingestion docs under
`grafana.com/docs/opentelemetry/` and `grafana.com/docs/grafana-cloud/send-data/otlp/`.
Several deep pages 404'd against direct URL guesses during this pass (Grafana's docs
site restructures paths across versions); where a page could not be located, that gap
is marked explicitly rather than filled with invented specifics.

Citation format per project convention: `[Source: <url>] <claim>.` Claims not found in
official docs are marked "Not documented / could not verify." Uncertain claims are
marked "Unresolved: …". Inferences are labeled "[Inference, not confirmed in docs]".

---

## 1. Core Concepts

[Source: https://grafana.com/docs/grafana/latest/introduction/] Grafana enables you to "query, visualize, alert on, and explore your metrics, logs, and traces wherever they are stored" — it is a visualization and analytics platform, not a data store itself; it queries external systems and renders the results.

[Source: https://grafana.com/docs/grafana/latest/introduction/] Grafana connects to data sources through a plugin framework, with documented examples spanning "NoSQL/SQL databases, ticketing tools like Jira or ServiceNow, and CI/CD tooling like GitLab" in addition to the time-series/logs/traces backends that dominate observability use cases.

[Source: https://grafana.com/docs/grafana/latest/dashboards/] A **dashboard** is "a set of one or more panels, organized and arranged into one or more rows or tabs, that provide an at-a-glance view of related information." A **panel** is "the container that displays the visualization and provides you with various controls to manipulate it" — panels retrieve and transform raw data from data sources into a visual representation.

[Source: https://grafana.com/docs/grafana/latest/dashboards/variables/] A **variable** is "a placeholder for a value that you can use in dashboard queries, panel titles, links, and other dashboard elements." Grafana documents eight variable types: **Query** (values come from a data source query — server names, metric names, label values), **Custom** (a manually defined fixed list), **Text box** (free-form viewer input), **Constant** (a reusable value viewers don't change), **Data source** (switches which data source instance a panel queries), **Interval** (lets viewers change a time-grouping/aggregation interval), **Filters** (key/value filtering across a dashboard), and **Switch** (toggles between two configured values).

[Source: https://grafana.com/docs/grafana/latest/datasources/] "A data source in Grafana is a connection to a storage backend that holds your data, such as a Prometheus server, a Loki instance, a SQL database, or a cloud monitoring service." "Grafana comes with built-in support for many data sources. If you need other data sources, you can also install one of the many data source plugins." Each data source exposes its own **query editor**, "a customized user interface that helps you write queries that take advantage of its unique capabilities" — Grafana does not impose one universal query language across sources.

[Source: https://grafana.com/docs/grafana/latest/datasources/] Documented built-in/first-party data source categories: metrics/time-series (Prometheus, Graphite, InfluxDB, AWS CloudWatch, Azure Monitor, Google Cloud Monitoring, OpenTSDB), logs (Loki, Elasticsearch), traces (Tempo, Jaeger, Zipkin), profiles (Parca, Pyroscope), SQL databases (PostgreSQL, MySQL, Microsoft SQL Server), and alerting (Alertmanager).

---

## 2. Architecture

[Source: https://grafana.com/docs/grafana/latest/administration/plugin-management/] Grafana's extensibility model is built on three plugin types: **Panel plugins** ("make it easy to create and add any kind of visualization"), **Data source plugins** ("allow you to pull data from various data sources such as databases, APIs, log files, and so on, and display it... in Grafana"), and **App plugins** ("enable the bundling of data sources, panels, dashboards, and Grafana pages into a cohesive experience").

[Source: https://grafana.com/docs/grafana/latest/administration/plugin-management/] Plugins have a frontend/backend split: the **Plugin Frontend Sandbox** feature "securely isolate[s] plugin frontend code from the main Grafana application" so that, when active, "plugins run in a separate JavaScript context" and cannot modify core Grafana UI or interfere with other plugins. Backend-to-backend plugin communication is separately gated: "the frontends of installed plugins [can] directly communicate locally with the backends of other installed plugins" only when an administrator enables it.

[Source: https://grafana.com/docs/grafana/latest/datasources/] The data-source proxy/query model is the architectural mechanism that lets one Grafana instance visualize many different backend systems simultaneously: each configured data source is an independent plugin instance with its own connection details and query editor, and a single dashboard's panels can each target a different data source (Prometheus for one panel, Loki for another, a SQL database for a third) within the same page.

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/set-up-for-high-availability/] For multi-node deployments, Grafana's default persistence is a single embedded SQLite database ("Grafana uses an embedded sqlite3 database to store users, dashboards, and other persistent data by default"); a shared external database (MySQL or Postgres) is required so that multiple Grafana server processes can share dashboard/user state behind a load balancer in an "active-active architecture."

[Source: https://grafana.com/docs/grafana/latest/administration/data-source-management/] Query caching is architecturally a layer in front of the data-source query path: results are cached and served back to identical subsequent queries without re-hitting the data source, with pluggable cache backends (in-memory, Redis, Memcached).

Not documented / could not verify: a single canonical page diagramming Grafana's internal frontend/backend/database process architecture (e.g., an explicit "how a request flows from browser to data source" diagram) was not located at a stable URL in this research pass; the architectural picture above is assembled from the plugin-management, data-sources, and HA documentation rather than one dedicated architecture page.

---

## 3. APIs

[Source: https://grafana.com/docs/grafana/latest/developers/http_api/] Grafana exposes an HTTP API covering: Dashboards (management, versions, permissions, search, public sharing), Data Sources (configuration, permissions, LBAC rules), Alerting (the "Grafana Alerts HTTP API" plus an "Alerting Provisioning HTTP API"), Users and Teams (including team sync), Organizations, Access Control (RBAC), and additional resources — annotations, correlations, library elements, preferences, query history, reporting, service accounts, snapshots, and SSO settings.

[Source: https://grafana.com/docs/grafana/latest/developers/http_api/] VERSION SENSITIVITY: "Starting in Grafana 13, `/api` endpoints are being deprecated in favor of the `/apis` route," though the documentation states legacy `/api` endpoints remain fully operational during the transition — this is a real, current architectural migration, not a historical one, and any skill built against the HTTP API should note that `/apis` is the forward-looking base path.

[Source: https://grafana.com/docs/grafana/latest/administration/plugin-management/] The plugin API is the documented mechanism for building custom data-source and panel plugins that extend the API surface described in Section 2; plugin installation itself is exposed both through the Administration UI and, per Section 10, via the `GF_PLUGINS_PREINSTALL` environment variable for Docker deployments.

Not documented / could not verify: the specific authentication mechanisms accepted by the HTTP API (API tokens, service accounts, basic auth) were not confirmed with quoted text from `developers/http_api/` itself in this pass — the page enumerates API groups but the fetched excerpt did not include an explicit authentication section; Grafana's service-account and API-key documentation (referenced under Administration in Section 7) is the more likely authoritative source and should be consulted directly for exact header/token format.

Unresolved: whether "dashboards as code" workflows (Section 5) are documented as using the HTTP API's dashboard-update endpoints directly, versus exclusively going through file-based provisioning (Section 4) or the newer Terraform/Grizzly/Operator tooling — the docs describe both paths existing but do not explicitly state which is "recommended" for CI-driven dashboard publishing versus the other.

---

## 4. Configuration

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/] Default settings live in `<WORKING DIRECTORY>/conf/defaults.ini`, which the docs explicitly warn not to edit directly. Custom configuration is OS-specific: Linux (deb/RPM) uses `/etc/grafana/grafana.ini`; macOS uses `/opt/homebrew/etc/grafana/grafana.ini` or `/usr/local/etc/grafana/grafana.ini`; Windows uses a `custom.ini` copied from `sample.ini`; Docker deployments are documented to use environment variables instead of an ini file.

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/] Configuration is layered in this precedence order: (1) `defaults.ini`, (2) the custom config file (`custom.ini`/`grafana.ini`), (3) environment variables (override the file), (4) command-line arguments (highest precedence). Environment-variable overrides follow the pattern `GF_<SECTION NAME>_<KEY>`, with section names uppercased and periods/dashes replaced by underscores — e.g., `[auth.google]` becomes `GF_AUTH_GOOGLE_`.

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/] Documented authentication-provider sections in `grafana.ini` include `[auth.anonymous]`, `[auth.github]`, `[auth.gitlab]`, `[auth.google]`, `[auth.azuread]` (Entra ID OAuth2), `[auth.okta]`, `[auth.generic_oauth]`, `[auth.basic]`, `[auth.proxy]`, `[auth.ldap]`, and `[auth.jwt]` — each with its own dedicated provider-setup documentation page. Not documented / could not verify: this fetch did not surface an explicit `[auth.saml]` section, though SAML is referenced elsewhere in Grafana's security-advisory history (Section 7), implying SAML support exists (likely as an Enterprise feature) even though this pass didn't confirm its exact ini section name from `configure-grafana/` itself.

[Source: https://grafana.com/docs/grafana/latest/administration/provisioning/] Grafana has "an active provisioning system that uses configuration files" — YAML, not the UI — for data sources, dashboards, and plugins, organized under `provisioning/datasources`, `provisioning/dashboards`, and `provisioning/plugins` directories respectively. Dashboard JSON files are polled or watched based on `updateIntervalSeconds`: "More than 10 seconds: Grafana polls the path at that interval. 10 seconds or less: Grafana watches the filesystem for changes."

[Source: https://grafana.com/docs/grafana/latest/administration/provisioning/] Provisioned dashboards can still be edited through the UI if `allowUiUpdates: true` is set — "if... you make changes to a provisioned dashboard, when you save the dashboard, Grafana persists the changes" — but with a critical caveat: "Grafana always overwrites the database dashboard with the one from the provisioning file" whenever the source file updates, regardless of UI-made changes in between. If `allowUiUpdates` is false, users attempting to save get a "Cannot save provisioned dashboard" dialog.

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/] Docker environment-variable configuration follows the same `GF_` prefix pattern as native installs, e.g. `-e "GF_LOG_LEVEL=debug"`; plugin pre-installation is available via `GF_PLUGINS_PREINSTALL=grafana-clock-panel@1.0.1`.

---

## 5. Recommended Patterns

[Source: https://grafana.com/docs/grafana/latest/administration/provisioning/] Config-file-based provisioning of dashboards and data sources (Section 4) is Grafana's own documented mechanism for keeping dashboard/data-source definitions in version control rather than only in the live database — the polling/watching behavior and the `allowUiUpdates` gate exist specifically to reconcile a Git-tracked source of truth with a running Grafana instance.

[Source: https://grafana.com/docs/grafana/latest/as-code/] Beyond file-based provisioning, Grafana documents a broader "as-code" ecosystem distinguishing **observability as code** (versioning and automating dashboard/alerting configuration) from **infrastructure as code** (declaratively creating/managing Grafana resources via config). Documented tools: **Terraform**, **Ansible**, the **Grafana Operator**, and **Grizzly**. The documented workflow pattern: "Track changes, collaborate, and roll back updates using Git and GitHub, or other remote sources," syncing a Grafana instance's configuration to a Git repository and automating deployment via CI/CD.

[Source: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/] VERSION SENSITIVITY: As of Grafana v12.2.0+, dashboards have moved from a single "Classic model" JSON schema to a versioned resource model — a **V1 Resource** ("the Classic dashboard schema formatted as a Kubernetes-style resource") and a **V2 Resource** ("the current schema, supporting new features such as advanced layouts and conditional rendering"). The docs note "[Observability as Code] works with both versions of the JSON model, but it's fully compatible with version 2" — implying V1/Classic dashboards may have narrower as-code tooling support going forward.

[Source: https://grafana.com/docs/grafana/latest/dashboards/variables/] The documented pattern for reusable, templated dashboards: "Prevent sprawl by using template variables. For example, you don't need a separate dashboard for each node, you can use query variables," and "you can make the data source a template variable too, so you can reuse the same dashboard across different clusters and monitoring backends." Variables "allow you to single-source dashboards," reducing duplication and maintenance burden.

[Source: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/] Explicit anti-dashboard-duplication guidance: "Copying dashboards with no significant changes is not a good idea. You miss out on updates to the original dashboard, such as documentation changes, bug fixes, or additions to metrics." Where a copy exists only to customize a view, the recommended pattern instead is "maintaining a link to the master dashboard and customizing the view with URL parameters."

[Source: https://grafana.com/docs/grafana/latest/alerting/fundamentals/] **Precise distinction between Grafana Alerting and Prometheus Alertmanager** (explicitly required by this task): Grafana Alerting is "Built on the Prometheus alerting model." [Source: alertmanager fundamentals docs, reached via https://grafana.com/docs/grafana/latest/alerting/fundamentals/alertmanager/] Grafana ships its own embedded engine — "Grafana includes a built-in **Grafana Alertmanager** to handle notifications" — which "extends the Prometheus Alertmanager" rather than being a thin passthrough to it. Grafana Alerting can *also* be configured to send notifications to an **external** Alertmanager (including a standalone Prometheus Alertmanager), by adding it as a data source and enabling it on the Alerting Settings page, to "forward Grafana-managed alerts to the same Alertmanager for unified notification handling." So: Grafana's alert **rule evaluation** always happens inside Grafana itself (against any configured data source, not just Prometheus), while **notification routing/grouping/silencing** can be handled either by the built-in Grafana Alertmanager or delegated to an external Alertmanager — these are two distinct, swappable layers, and conflating "Grafana Alerting" with "Prometheus's Alertmanager" is the precise point of confusion this section is documenting against.

[Source: https://grafana.com/docs/grafana/latest/alerting/best-practices/] Documented alert-rule-design patterns: use **notification grouping** ("consolidates related alerts into a single notification" — "without alert grouping, responders can receive many notifications for the same underlying problem"); set a **pending period** ("how long a condition must remain true before firing") to avoid flapping; prefer **percentile-based** thresholds over simple averages for latency/error measurement ("percentiles are often more useful than averages"); and design alerts to "detect user-facing failures, not internal component behavior," written "for the first responder, not the person who created the alert," with annotations linking to dashboards/runbooks.

[Source: https://grafana.com/docs/grafana/latest/administration/data-source-management/] Query-and-resource caching is a documented recommended pattern for dashboards with many simultaneous viewers/panels: cached results are served for identical repeat queries, though the docs caveat that "some databases like Elasticsearch and Prometheus cache queries themselves, so Grafana query caching does not significantly improve performance" against those specific backends.

---

## 6. Anti-Patterns

[Source: https://grafana.com/docs/grafana/latest/administration/provisioning/] Manually editing a provisioned dashboard in the UI without also updating its source-of-truth JSON file is a documented drift trap: changes persist locally only until the provisioning file next updates, at which point "Grafana always overwrites the database dashboard with the one from the provisioning file" — silently discarding the UI edit. The anti-pattern is treating the UI as the source of truth for a dashboard that provisioning also manages.

[Source: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/] Copy-pasting dashboards instead of parameterizing them with variables is an explicit anti-pattern: "Copying dashboards with no significant changes is not a good idea. You miss out on updates to the original dashboard" — teams accumulate diverging, unmaintained forks instead of one variable-driven dashboard.

[Source: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/] Overloaded, unfocused panels are called out directly: "Keep your graphs simple and focused on answering the question that you are asking," and dashboards should "be easy to interpret" for "other users and future you (when you're trying to figure out what broke at 2 AM)" — implying the anti-pattern of a single sprawling dashboard crammed with unrelated panels instead of composable, purpose-built ones.

[Source: https://grafana.com/docs/grafana/latest/alerting/best-practices/] Alert fatigue is documented as an anti-pattern with named causes and fixes: alerting on "internal component behavior" instead of "user-facing failures"; omitting a **pending period**, causing flapping-condition noise; and never pruning stale rules — the docs recommend to "schedule regular reviews of existing alerts. Remove alerts that don't lead to action." Alerts without a clear owner are also flagged: "Every alert must have an owner: a team responsible for maintaining the alert and responding when it fires" — ownerless alerts are implicitly the anti-pattern.

[Source: https://grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v13-0/] Relying on numeric data-source `id`-based API calls instead of `uid`-based ones is now an explicitly deprecated/disabled-by-default pattern as of Grafana 13.0 ("Deprecated numeric `id`-based data source APIs are now disabled by default; use `uid` instead") — a concrete example of an anti-pattern the product itself has started blocking rather than merely discouraging.

---

## 7. Security

[Source: https://grafana.com/docs/grafana/latest/administration/roles-and-permissions/] Access control is organization-scoped: "All Grafana users belong to at least one organization." Three core organization roles exist with hierarchical permissions: **Viewer** ("Can view dashboards, playlists, and query data sources"), **Editor** ("Can view and edit dashboards, folders, and playlists"), and **Organization Administrator** ("Has access to all organization resources, including dashboards, users, and teams"). These role permissions apply globally across an organization's resources unless overridden by more granular dashboard/folder permissions, which take precedence: "The dashboard permissions you specify override the organization permissions you assign to the user."

[Source: https://grafana.com/docs/grafana/latest/administration/roles-and-permissions/] **Teams** group users for shared "dashboard and data source permission needs," with per-member Member/Admin designations. **RBAC** (Enterprise) "provides you a way of granting, changing, and revoking user read and write access to Grafana resources, such as users, reports, and authentication" — a finer-grained model than the three core roles. **Data source permissions** (Enterprise) let admins "restrict data source query permissions to specific Users, Service Accounts, and Teams," with three levels: Query (can query only), Edit (query + edit config + delete), and Admin (query + edit + change permissions).

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-database-encryption/] Data-source credentials and other secrets are encrypted at rest: Grafana encrypts "secrets, which are used to query data sources, send alert notifications, and perform other functions within Grafana," by default using **AES** in **CFB mode (AES-CFB)**. Since v9.0+, Grafana defaults to **envelope encryption**: per-secret **data encryption keys (DEKs)** are themselves encrypted by a single **key encryption key (KEK)**, rather than one flat key protecting every secret directly (disableable via the `disableEnvelopeEncryption` feature toggle). Grafana Enterprise supports external **KMS integration** — AWS KMS, Azure Key Vault, Google Cloud KMS, HashiCorp Key Vault — where "Grafana does not directly store your encryption key. Instead, Grafana stores KMS credentials and the identifier of the key," and Enterprise deployments can switch the cipher mode to **AES-GCM**.

[Source: https://grafana.com/security/security-advisories/] Grafana Labs publishes CVE-numbered security advisories with severity scores on a dedicated advisories page. Concrete recent documented examples encountered in this pass: **CVE-2026-19516 (Critical, 9.1)** — "Grafana MCP server-side request forgery via X-Grafana-URL header" in the `grafana_api_request` function; **CVE-2026-27876 (Critical, 9.1)** — "RCE on Grafana via sqlExpressions," a remote code execution vulnerability; **CVE-2025-41115 (Critical, 10.0)** — "Incorrect privilege assignment" affecting Grafana Enterprise; **CVE-2026-14199 (High, 7.1)** — "Session takeover via Auth Proxy cache key collision" in Grafana Enterprise; **CVE-2026-12704 (Medium, 6.8)** — "SAML assertion replay via skipped InResponseTo validation" affecting Grafana Enterprise; **CVE-2026-19475 (Medium, 6.5)** — a PostgreSQL data source issue where the `$__timeGroup` macro could cause memory exhaustion. The advisory stream spans Grafana OSS, Enterprise, individual data-source plugins, and adjacent Grafana Labs products (e.g., CVE-2026-75889 affecting Grafana Alloy).

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/] TLS/SAML/LDAP/OAuth2 authentication is documented per-provider under dedicated `grafana.ini` sections (Section 4); a Server Administrator role sits above the per-organization Admin role for instance-wide administration (referenced via the Stats-and-License admin page in Section 17).

Unresolved: whether Grafana publishes an aggregate historical CVE count or a documented, time-bound disclosure SLA (comparable to, say, Node.js's "72-hour embargo, 5-day acknowledgment" policy documented in this corpus's nodejs.md) was not confirmed — the security-advisories page in this pass rendered as a list of individual advisories without a stated disclosure-process narrative; consult `grafana.com/security/` directly for any such policy page.

---

## 8. Performance

[Source: https://grafana.com/docs/grafana/latest/administration/data-source-management/] Query and resource caching is Grafana's primary documented dashboard-performance lever: cached results are keyed effectively by query, with cache duration derived from panel granularity — "time range / max data points" — e.g., a panel showing 1000 data points across a 7-day range refreshes its cache roughly every 10 minutes. Cache backends: in-memory, Redis, Memcached. Benefits cited: faster dashboard loads, reduced downstream API cost/rate-limit exposure. Caveat: "some databases like Elasticsearch and Prometheus cache queries themselves, so Grafana query caching does not significantly improve performance" against those specific backends — caching benefit is data-source-dependent, not universal.

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/installation/] Query caching is called out specifically as a dashboard-concurrency performance mitigation: "Grafana Enterprise includes query caching, which can significantly reduce this multiplier when many users view the same dashboard simultaneously" — i.e., without caching, N concurrent viewers of one dashboard roughly multiply data-source query load by N; caching decouples viewer count from data-source load for identical, cache-hit queries.

Not documented / could not verify: this pass did not locate a dedicated "how many panels/queries per dashboard is too many" sizing guideline, nor a documented Grafana-server-side (not data-source-side) query concurrency limit; the `setup-grafana/installation/requirements/` URL guessed for sizing guidance 404'd in this pass and was not relocated to a working path.

---

## 9. Testing

[Source: https://grafana.com/docs/grafana/latest/cli/] The Grafana CLI's documented command surface is limited to **plugin management** (`grafana cli plugins list-remote|install|ls|update-all|remove`) and **admin** tasks (`grafana cli admin reset-admin-password`, `grafana cli admin data-migration encrypt-datasource-passwords`) — it does not expose a documented dashboard/provisioning-config validation or dry-run subcommand.

Not documented / could not verify: Grafana's official documentation does not describe a first-party testing framework or CLI-driven validation step for dashboard-as-code JSON, provisioning YAML, or alert-rule definitions comparable to (for example) a linter or `--dry-run` flag. The `as-code/` page (Section 5) names third-party tooling — Terraform, Ansible, the Grafana Operator, Grizzly — as the documented path for version-controlled dashboards, and those tools carry their own independent testing/validation stories (e.g., `terraform plan`) that are outside Grafana's own docs. This is a genuinely thin area of the official documentation, stated honestly rather than inferred: consult each as-code tool's own docs for how it tests/validates before applying.

---

## 10. Deployment

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/] Official Docker images: `grafana/grafana-enterprise` ("The recommended and default edition of Grafana is Grafana Enterprise. It is free and includes all the features of the OSS edition.") and `grafana/grafana` (OSS-only). Environment variables use the `GF_` prefix (same mapping rules as native `grafana.ini` overrides, Section 4). Persistent storage is documented via named Docker volumes (`--volume grafana-storage:/var/lib/grafana`) or bind mounts, the latter requiring the container to "start... with a user with permission to access and write to the directory you map."

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/] Documented docker-compose pattern:
```yaml
services:
  grafana:
    image: grafana/grafana-enterprise
    container_name: grafana
    restart: unless-stopped
    environment:
      - GF_SERVER_ROOT_URL=http://my.grafana.server/
      - GF_PLUGINS_PREINSTALL=grafana-clock-panel
    ports:
      - '3000:3000'
    volumes:
      - 'grafana_storage:/var/lib/grafana'
volumes:
  grafana_storage: {}
```
[Inference, not confirmed in docs] This library already maintains deep general Docker research (see `research/technologies/docker.md` if present in this corpus) covering multi-stage builds, non-root users, and container lifecycle concerns broadly; the Grafana-specific delta documented here is limited to image names, the `GF_`-prefixed env-var convention, and the `/var/lib/grafana` persistence path — general container hardening guidance should be cross-referenced from that separate research rather than duplicated here.

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/installation/] Grafana Cloud is documented as the managed alternative to self-hosting: "You can use Grafana Cloud to avoid installing, maintaining, and scaling your own instance of Grafana," with a free tier offering "free forever access to 10k metrics, 50GB logs, 50GB traces, 500VUh k6 testing & more." Not documented / could not verify: this pass did not find a page directly and comprehensively comparing self-managed OSS vs. Grafana Enterprise (self-managed) vs. Grafana Cloud feature-by-feature; the installation guide's framing is "self-manage, or use Cloud to avoid self-managing" rather than a three-way feature matrix.

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/set-up-for-high-availability/] High-availability guidance: run multiple Grafana server nodes behind a load balancer in "an active-active architecture," backed by a shared MySQL or Postgres database (replacing the default embedded SQLite). Session affinity is unnecessary because "Grafana uses auth token strategy with database by default... a load balancer can send a user to any Grafana server without having to log in on each server." The load balancer needs "a listener that responds to a shared cluster hostname" and may optionally do SSL termination.

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/set-up-for-high-availability/] Alerting HA has a documented, distinct behavior from general HA: "To prevent duplicate alerts in Grafana high availability, additional steps are required" — the alerting engine "preserves the semantics of legacy dashboard alerting by executing all alerts on every server and by sending notifications only once per alert," i.e., every HA node evaluates every rule, but notification de-duplication (not query-load distribution) is what HA alerting provides.

---

## 11. Migration

[Source: https://grafana.com/docs/grafana/latest/upgrade-guide/] General upgrade philosophy: "We recommend that you upgrade Grafana often to stay current with the latest fixes and enhancements," and "Because Grafana upgrades are backward compatible, the upgrade process is straightforward, and dashboards and graphs will not change." "You can upgrade to any of the supported releases from any supported release" — i.e., Grafana does not document a mandatory sequential-version upgrade path for the general case (contrast with the alerting migration below, which is version-gated).

[Source: https://grafana.com/docs/grafana/latest/alerting/set-up/migrating-alerts/] The single most significant documented Grafana migration — **legacy dashboard alerting → unified alerting** — is version-gated and destructive if mishandled: "Legacy alerting will be removed in Grafana v11.0.0. Grafana v10.4 is the last version that offers legacy alerting," and "Installing Grafana 11 before upgrading your legacy alerts will result in your existing alerts becoming inaccessible or lost." Two documented automatic-migration paths: **Upgrade with Preview** (v10.3.0+, recommended — "a safe and controlled preview environment where you can review and adjust your upgraded alerts before fully enabling Grafana Alerting") and **Simple Upgrade** (v9.0.0+, a "one-step upgrade method" for straightforward deployments). The migration is documented as "non-destructive and can be rolled back easily" via `custom.ini` reconfiguration.

[Source: https://grafana.com/docs/grafana/latest/alerting/set-up/migrating-alerts/] Documented semantic changes surfaced by the legacy→unified alerting migration: alert rules may move folders to match dashboard permissions (since unified alerting follows folder permissions, not dashboard permissions); the legacy "Keep Last State" no-data option has no unified equivalent and auto-converts to NoData/Error with an automatic 1-year silence; Hipchat and Sensu notification channels are unsupported and must be manually reassigned; and Prometheus "Both" query type is unsupported, auto-converting to "Range."

[Source: https://grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v13-0/] A separate, currently-relevant migration risk: "A migration bug in v13.0.0 may cause dashboards and folders to be lost when upgrading from v12.x with Git Sync enabled" — documented under Unified Storage for Folders and Dashboards, illustrating that even within the "generally backward compatible" upgrade philosophy, specific version transitions can carry real data-loss risk that must be checked per-release.

---

## 12. Version Information

[Source: https://grafana.com/docs/grafana/latest/upgrade-guide/when-to-upgrade/] Documented release cadence: **minor releases** ship "every other month," including new features, bug fixes, and security patches; **major releases** ship "once yearly (April/May)," accompanied by dedicated upgrade guides; **patch releases** ship "at least monthly," containing only bug fixes and security patches for supported versions.

[Source: https://grafana.com/docs/grafana/latest/upgrade-guide/when-to-upgrade/] Documented support-window policy: each minor release is supported for **9 months** after launch; the **final minor release of a major version** gets extended support of **15 months**. Support has three tiers — **Full Support** (current major version), **Patch Support** (older minor releases within window, fixes only), and **Not Supported** (past end-of-life). Security releases append `+security` to the version string to signal "the indicated version PLUS the security fix"; high-severity vulnerabilities trigger ad-hoc out-of-cycle releases, and "all supported versions receive security patches until their end-of-life date."

[Source: https://grafana.com/docs/grafana/latest/upgrade-guide/when-to-upgrade/] Grafana's own recommended production strategy is explicitly the bi-monthly minor-release cadence: "Our recommended strategy. It combines up-to-date, secure releases with access to latest features as soon as they're released" — favored for minimizing changelog-review burden and preserving plugin compatibility while staying current on security fixes.

[Source: https://grafana.com/docs/grafana/latest/whatsnew/] As of this research pass, the current release line is **Grafana 13**, with 13.2 the most recent documented minor release (What's New pages exist for 13.0–13.2; v12 shows 5 documented minor releases, v11 shows 7).

[Source: https://grafana.com/docs/release-life-cycle/] Separately from the version-support-window policy above, Grafana Labs documents a **feature maturity lifecycle** independent of version numbers: **Experimental** ("Not supported; OSS users can create issues in GitHub"), **Private preview**, **Public preview** ("enablement, configuration, and some troubleshooting" support), and **General Availability** ("Fully supported / on-call" with SLA coverage) — relevant when evaluating whether a specific Grafana *feature* (as opposed to the product's version line) is production-ready, since GA and version-support status are two orthogonal maturity axes.

Not documented / could not verify: this pass found no explicit "LTS" (Long-Term Support) branding in Grafana's own docs comparable to Node.js's LTS lines (nodejs.md, Section 12) — the closest analog is the "final minor release of a major version gets 15 months of support" policy above, which functions similarly but is not labeled "LTS" in the source material found.

---

## 13. Breaking Changes

VERSION SENSITIVITY — Grafana 13.0, [Source: https://grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v13-0/]:
- **Image Renderer plugin support fully removed** — "it no longer works for rendering screenshots or scheduled reports"; default rendering authentication switched from opaque tokens to JWTs.
- **CLI command surface changed**: `grafana-cli` and `grafana-server` (hyphenated, standalone commands) removed; replaced by `grafana cli` and `grafana server` subcommands.
- **Deprecated numeric `id`-based data source APIs disabled by default** — `uid`-based addressing is now required (see Section 6).
- **HTTP compression default flipped**: `enable_gzip`, "previously disabled by default... Starting in Grafana v13.0, this setting is enabled by default."
- **Alertmanager status endpoint permission changed**: now requires the `alert.notifications.system-status:read` permission instead of the prior legacy permission; several deprecated legacy Alertmanager configuration API endpoints removed or restricted.
- **RBAC enforcement tightened** for custom roles and UID-scoped data source permissions.
- Auditing defaults changed for `log_datasource_query_request_body`/`log_datasource_query_response_body`; duplicated `grafana_caching_items`/`grafana_caching_size` metrics removed from Query Caching; the TwinMaker SceneViewer panel became unavailable due to the React 19 upgrade removing APIs it depended on; several deprecated `@grafana/ui` components (`Graph`, `GraphWithLegend`, `GraphContextMenu`, and related) were removed.
- **Migration-risk bug**: "A migration bug in v13.0.0 may cause dashboards and folders to be lost when upgrading from v12.x with Git Sync enabled" (Section 11).
- **Deprecations flagged for future removal**: `@grafana/runtime`'s `config.apps`/`config.panels` properties (scheduled for removal in 13.2.0); the `/api` path itself (in favor of `/apis`, Section 3); several `go_sql_stats`/`grafana_database_conn` metrics (replaced by standardized `go_sql` metrics).

VERSION SENSITIVITY — Grafana 11.0.0, [Source: https://grafana.com/docs/grafana/latest/alerting/set-up/migrating-alerts/]: **Legacy dashboard alerting was removed entirely** in v11.0.0 (v10.4 was the last version supporting it); this is the single largest breaking change in Grafana's recent history, since it changes the alerting data model, folder-permission semantics, and notification-channel compatibility for every dashboard using the legacy system (full detail in Section 11).

Not documented / could not verify: a consolidated cross-version "all breaking changes since v8" index page was not located; per-version detail for releases prior to v13.0 (e.g., specific v12.x breaking changes) would need to be pulled from that version's own `whatsnew/whats-new-in-v12-X/` page directly, none of which were individually re-fetched in this pass beyond the v13.0 page and the alerting-migration page.

---

## 14. Limitations

[Source: https://grafana.com/docs/grafana/latest/datasources/] Grafana's foundational, architecture-level limitation (central to this entire reference): it stores no observability data of its own — every dashboard, panel, and alert rule is entirely dependent on the configured data source being reachable and performant at query time. A slow or unavailable Prometheus/Loki/Tempo/SQL backend degrades or breaks the Grafana experience regardless of anything Grafana itself does; this is a structural consequence of Grafana's role as a visualization layer, not a bug.

[Source: https://grafana.com/docs/grafana/latest/administration/data-source-management/] Query caching's benefit is explicitly data-source-dependent and not a universal performance fix: "some databases like Elasticsearch and Prometheus cache queries themselves, so Grafana query caching does not significantly improve performance" against them — meaning the documented performance lever from Section 8 has real, named exceptions.

[Source: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/] The dashboard JSON model now has **three coexisting representations** to reason about — the pre-v12.2.0 "Classic model," the "V1 Resource" (Classic model wrapped in a Kubernetes-style resource envelope), and the "V2 Resource" (current schema, new layout/conditional-rendering features) — with as-code tooling only "fully compatible with version 2." This is a documented source of schema complexity: a dashboard JSON file's exact shape now depends on which resource version produced/consumes it, and tooling built against one version may not transparently handle another.

[Source: https://grafana.com/docs/grafana/latest/administration/organization-management/] Multi-organization isolation has a hard documented boundary: "The member of one organization cannot view dashboards assigned to another organization" — cross-organization dashboard sharing is not natively supported; only users, instance-wide configuration, and Enterprise licenses are shared across organizations, while "Dashboards, data sources, annotations, folders, Teams, and Alerts, are isolated within each organization."

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/set-up-for-high-availability/] Alerting HA does not distribute alert-evaluation load across a cluster — every node evaluates every rule ("executing all alerts on every server"); HA for alerting solves notification duplication, not query/compute load distribution, which is a real limitation for very large rule counts on HA deployments.

---

## 15. Debugging

[Source: https://grafana.com/docs/grafana/latest/panels-visualizations/query-transform-data/] The **Query Inspector** is the documented tool for debugging a panel's actual query: opened via the "Query inspector" button in the footer of the panel editor pane, it lets a user "view and optimize your query" — inspecting exactly what was sent to the data source and what came back, to debug unexpected panel behavior. Not documented / could not verify: the exact set of tabs the Query Inspector exposes (e.g., separate "Query"/"Panel JSON"/"Stats"/"JSON"/"Data" tabs) was not confirmed with quoted text in this pass beyond the general "view and optimize your query" description.

[Source: https://grafana.com/docs/grafana/latest/troubleshooting/] Logs are written to `/var/log/grafana/grafana.log` on Unix systems, or `<grafana_install_dir>/data/log` on other platforms. Debug-level logging is enabled by changing the log level in the Grafana configuration file (`[log]` section), with additional CLI-specific debug-logging guidance documented separately. Documented troubleshooting topics include: **transformation ordering issues** ("Order of transformations matters" — each transformation processes the previous transformation's output, not the original dataset); **image-rendering font problems** for server-side PNG rendering (missing text traced to missing font packages, e.g. `fontconfig`, `freetype`, `urw-fonts` on RPM-based systems); and **CPU/memory bottlenecks**, for which the docs point to a dedicated "Configure profiling and tracing to troubleshoot Grafana" guide.

[Source: https://grafana.com/docs/grafana/latest/administration/stats-and-license/] Administration > General > **Stats and license** (requires the Grafana Admin flag) surfaces instance-wide diagnostic counters useful for operational debugging: user counts by role, active users/sessions, dashboard/organization/playlist/snapshot/alert counts, and — separately — the effective applied configuration (file + environment-variable-derived settings) under the adjacent Settings tab, useful for confirming what config value is actually in effect versus what's in `grafana.ini`.

Not documented / could not verify: a dedicated frontend/browser-console debugging guide, or a documented `--debug`/verbose startup flag list beyond the `[log]`-section level change, was not located as a single consolidated page in this pass.

---

## 16. Integration

[Source: https://grafana.com/docs/grafana/latest/datasources/prometheus/] **Prometheus integration (the single most important integration point per this task's brief):** "The Prometheus data source is preinstalled in Grafana, so you don't need to install it manually." VERSION SENSITIVITY: as of Grafana 13.2, "it's packaged as a standalone plugin rather than built into the Grafana codebase," allowing the Prometheus data source to be updated independently of full Grafana releases. Querying is done via "PromQL in the query editor, or... Metrics Drilldown to explore metrics without writing queries." The Prometheus data source's feature matrix documents support for **exemplars** and for **alerting**.

[Source: https://grafana.com/docs/grafana/latest/fundamentals/exemplars/] **Exemplars** are the documented mechanism linking Prometheus metrics to Tempo traces: "A specific trace representative of measurement taken in a given time interval... While metrics excel at giving you an aggregated view of your system, traces give you a fine-grained view of a single request; exemplars are a way to link the two." Exemplars are currently documented as **Prometheus-only** as a data source, surfaced as highlighted stars in Explore and on dashboards, and can link onward into Grafana Tempo for trace-level investigation — this is the concrete, named cross-signal correlation path from Prometheus metrics to distributed tracing inside Grafana.

[Source: https://grafana.com/docs/grafana/latest/alerting/fundamentals/] and [Source: alertmanager fundamentals, https://grafana.com/docs/grafana/latest/alerting/fundamentals/alertmanager/] Grafana's alert **rules** can evaluate against Prometheus (or any configured data source) directly, while **notification delivery** can be handled by Grafana's own built-in Alertmanager (which "extends the Prometheus Alertmanager") or forwarded to an external, standalone Prometheus Alertmanager — see Section 5 for the full precise distinction this task specifically asked to be documented accurately.

[Source: https://grafana.com/docs/opentelemetry/] **OpenTelemetry / "LGTM stack" integration:** Grafana Labs states "Grafana Labs supports OpenTelemetry as a core part of our observability strategy. We offer a comprehensive observability stack that helps you collect, ingest, store, analyze, and visualize telemetry data." The docs name the components individually — "Send OTLP data from your instrumentation or pipeline to Grafana Cloud or self-managed Grafana Loki, Grafana Mimir, and Grafana Tempo" — plus Grafana Pyroscope for continuous profiling. [Source: https://grafana.com/docs/grafana-cloud/send-data/otlp/] For OTLP ingestion specifically, "Grafana Cloud supports ingestion of metrics, logs, and traces through OTLP," and OpenTelemetry data is "converted to Prometheus/Mimir, Loki, and Tempo" internally — i.e., OTLP data is normalized into each backend's native format (Prometheus-remote-write-compatible for Mimir, log lines for Loki, spans for Tempo) rather than Grafana itself storing OTLP natively; Grafana (the visualization layer) then queries those three backends the same way it queries any other data source.

Unresolved: the literal marketing term **"LGTM stack"** (Loki, Grafana, Tempo, Mimir) was **not found verbatim** on any official `grafana.com/docs/` page fetched in this research pass, despite being a widely used shorthand in the observability community and in Grafana Labs' own blog/marketing content. The official docs describe the same four-component architecture (Loki + Grafana + Tempo + Mimir, plus Pyroscope for profiles) without using the LGTM acronym in the specific pages checked (`/docs/opentelemetry/`, `/docs/grafana-cloud/send-data/otlp/`, `/docs/loki/latest/get-started/`). Treat "LGTM stack" as a widely-used but not confirmed-in-current-docs term for skill-authoring purposes — describe the four components explicitly rather than relying on the acronym resolving to an official, linkable docs page.

[Source: https://grafana.com/docs/grafana/latest/datasources/tempo/] **Tempo integration:** Tempo is "a high-volume, minimal-dependency distributed tracing backend from Grafana Labs." Through the Tempo data source, Grafana lets users "search and visualize traces, correlate traces with logs, metrics, and profiles, and monitor service dependencies with the Service Graph," query via **TraceQL**, and use a timeline viewer with span filtering. Not documented / could not verify: this Tempo-datasource page fetch did not itself state that Tempo's trace format is OpenTelemetry-based; that fact is established instead via the OpenTelemetry docs cited above, which name Tempo as one of the three OTLP-consuming backends.

[Source: https://grafana.com/grafana/plugins/grafana-sentry-datasource/] **Sentry integration:** Grafana Labs publishes an official (not community) **Sentry data source plugin** — "Grafana Labs" is listed as both developer and publisher — which lets users "query and visualize Sentry data within Grafana." Documented requirements: Grafana v10.4.0+ and an active Sentry account; version 2.2.6 was the most recently observed release in this pass. The plugin page references dedicated documentation for "configuration, query types, template variables, and troubleshooting" for the Sentry integration specifically.

[Source: https://grafana.com/docs/grafana/latest/datasources/] Beyond the observability-specific integrations above, Grafana documents dozens of other first-party and community data-source plugins spanning cloud-provider monitoring (AWS CloudWatch, Azure Monitor, Google Cloud Monitoring), log platforms (Elasticsearch, in addition to Loki), SQL databases (PostgreSQL, MySQL, Microsoft SQL Server), and continuous-profiling backends (Parca, Pyroscope) — the plugin model (Section 1–2) is the single unifying integration mechanism across all of them.

---

## 17. Production Considerations

[Source: https://grafana.com/docs/grafana/latest/administration/organization-management/] Dashboard/data-source governance at scale is primarily organization- and folder-scoped: "Multiple organizations are easier and cheaper to manage than multiple instances of Grafana," with dashboards, data sources, folders, teams, and alerts isolated per-organization while users and instance config are shared. Not documented / could not verify: this pass did not find a dedicated "how to structure folders/teams for a growing engineering org" governance playbook beyond the isolation-boundary facts above and the general roles/permissions and RBAC documentation in Section 7 — teams and folder permissions (Section 7) are the documented primitives or governance, but no worked "reference org structure" example was located.

[Source: https://grafana.com/docs/grafana/latest/alerting/best-practices/] Alert-rule ownership is explicitly a documented production practice, not left implicit: "Every alert must have an owner: a team responsible for maintaining the alert and responding when it fires," paired with scheduled review cycles to prune alerts that "don't lead to action" — directly applicable to keeping a large, multi-team alert-rule set maintainable rather than accumulating unowned noise.

[Source: https://grafana.com/docs/grafana/latest/administration/data-source-management/] Data-source access control at scale is handled via the Query/Edit/Admin permission tiers (Enterprise), scoped to specific Users, Service Accounts, or Teams (Section 7) — the documented mechanism for e.g. restricting which teams can query a sensitive production database data source versus a public-metrics one.

[Source: https://grafana.com/docs/grafana/latest/upgrade-guide/when-to-upgrade/] For production version management: adopt the bi-monthly-minor-release cadence Grafana itself recommends (Section 12), track the `+security`-suffixed release stream for out-of-band security patches, and budget for the annual major-version upgrade window (April/May) using that release's dedicated upgrade guide — given the documented precedent of real migration risk even within "backward compatible" majors (the v13.0 Git-Sync dashboard-loss bug, Section 11).

[Source: https://grafana.com/docs/grafana/latest/setup-grafana/set-up-for-high-availability/] For production HA: externalize the database (MySQL/Postgres) before scaling beyond one node, since the default embedded SQLite cannot be shared; plan alerting capacity knowing every HA node evaluates every alert rule (no rule-level sharding), so alert-rule count — not just dashboard/query load — factors into per-node sizing.

[Source: https://grafana.com/docs/grafana/latest/administration/plugin-management/] Production plugin governance: prefer the Plugin Frontend Sandbox where available to isolate third-party panel/data-source plugin code from the core Grafana UI, and treat backend-to-backend plugin communication (disabled by default) as an explicit, admin-gated capability rather than an assumed one.

---

## Unresolved Items (Summary)

- Whether "dashboards as code" workflows are documented as primarily using the HTTP API's dashboard-update endpoints versus exclusively file-based provisioning or third-party as-code tools (Section 3) — the docs describe multiple coexisting paths without a stated preference.
- Exact HTTP API authentication mechanisms (API tokens vs. service accounts vs. basic auth) were not confirmed with quoted text from the `developers/http_api/` page itself (Section 3).
- Whether `[auth.saml]` (or Enterprise-specific SAML config) has its own documented `grafana.ini` section name — SAML's existence is implied by a security advisory (Section 7) but its exact configuration surface was not directly confirmed (Section 4).
- Whether Grafana publishes an aggregate/historical CVE count or an explicit disclosure-process SLA (acknowledgment/embargo timelines) comparable to Node.js's documented policy (Section 7).
- The precise set of tabs/data exposed by the Query Inspector tool (Section 15) — confirmed only at the level of "lets you view and optimize your query," not itemized tab-by-tab.
- **The literal term "LGTM stack" was not found verbatim in any official grafana.com/docs page fetched in this pass** (Section 16) — the four-component architecture (Loki, Grafana, Tempo, Mimir) is fully documented under OpenTelemetry/OTLP ingestion pages, just not under that acronym; skill authors should describe the components explicitly rather than assuming "LGTM stack" resolves to a specific official docs anchor.
- Whether Tempo's trace data format is explicitly documented as OpenTelemetry-based on the Tempo data-source page itself (Section 16) — this fact was established via the separate OpenTelemetry/OTLP docs rather than the Tempo page directly.
- No dedicated "reference org/folder structure for a growing engineering team" governance playbook was located beyond the isolation-boundary and RBAC primitives (Section 17).
- Dashboard/query sizing guidance (how many panels or concurrent queries is "too many" for a single Grafana instance) — the specific `installation/requirements/` URL guessed for this returned 404 and was not relocated (Section 8).

---

## Sources Consulted (deduplicated)

- https://grafana.com/docs/grafana/latest/introduction/ — core concepts, what Grafana is
- https://grafana.com/docs/grafana/latest/dashboards/ — dashboards/panels overview
- https://grafana.com/docs/grafana/latest/dashboards/variables/ — template variables, types
- https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/ — dashboard JSON model, V1/V2 resource schemas
- https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/ — dashboard design best practices / anti-patterns
- https://grafana.com/docs/grafana/latest/datasources/ — data source model, supported types
- https://grafana.com/docs/grafana/latest/datasources/prometheus/ — Prometheus data source integration
- https://grafana.com/docs/grafana/latest/datasources/tempo/ — Tempo data source integration
- https://grafana.com/docs/grafana/latest/fundamentals/exemplars/ — exemplars, metrics-to-traces linking
- https://grafana.com/docs/grafana/latest/administration/plugin-management/ — plugin system, types, sandboxing
- https://grafana.com/docs/grafana/latest/administration/roles-and-permissions/ — org/team roles, RBAC, data source permissions
- https://grafana.com/docs/grafana/latest/administration/data-source-management/ — query/resource caching, data source permission tiers
- https://grafana.com/docs/grafana/latest/administration/provisioning/ — YAML-based provisioning of dashboards/data sources
- https://grafana.com/docs/grafana/latest/administration/organization-management/ — multi-org isolation model
- https://grafana.com/docs/grafana/latest/administration/stats-and-license/ — admin stats/diagnostics page
- https://grafana.com/docs/grafana/latest/developers/http_api/ — HTTP API coverage, /api → /apis deprecation
- https://grafana.com/docs/grafana/latest/as-code/ — dashboards-as-code tooling (Terraform, Ansible, Operator, Grizzly)
- https://grafana.com/docs/grafana/latest/alerting/ — alerting landing page
- https://grafana.com/docs/grafana/latest/alerting/fundamentals/ — alert rules, contact points, notification policies, Prometheus alerting model
- https://grafana.com/docs/grafana/latest/alerting/fundamentals/alertmanager/ — built-in Grafana Alertmanager vs. external Alertmanager
- https://grafana.com/docs/grafana/latest/alerting/best-practices/ — alert fatigue, threshold tuning, ownership
- https://grafana.com/docs/grafana/latest/alerting/set-up/migrating-alerts/ — legacy-to-unified alerting migration
- https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/ — grafana.ini structure, env var overrides, auth provider sections
- https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/ — Docker deployment, images, env vars, compose example
- https://grafana.com/docs/grafana/latest/setup-grafana/installation/ — Grafana Cloud vs. self-managed, sizing/caching note
- https://grafana.com/docs/grafana/latest/setup-grafana/set-up-for-high-availability/ — HA architecture, shared DB, alerting HA semantics
- https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-database-encryption/ — secret encryption, envelope encryption, KMS integration
- https://grafana.com/docs/grafana/latest/upgrade-guide/ — general upgrade guidance
- https://grafana.com/docs/grafana/latest/upgrade-guide/when-to-upgrade/ — release cadence, support windows, recommended upgrade strategy
- https://grafana.com/docs/grafana/latest/whatsnew/ — release notes index, current version
- https://grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v13-0/ — v13.0 breaking changes and deprecations
- https://grafana.com/docs/release-life-cycle/ — feature maturity lifecycle (Experimental/Preview/GA)
- https://grafana.com/docs/grafana/latest/panels-visualizations/ — panels/visualizations section index
- https://grafana.com/docs/grafana/latest/panels-visualizations/query-transform-data/ — Query Inspector tool
- https://grafana.com/docs/grafana/latest/troubleshooting/ — debug logging, log locations, common issues
- https://grafana.com/docs/grafana/latest/cli/ — Grafana CLI command reference
- https://grafana.com/security/security-advisories/ — published CVE advisories
- https://grafana.com/grafana/plugins/grafana-sentry-datasource/ — official Sentry data source plugin
- https://grafana.com/docs/opentelemetry/ — OpenTelemetry support strategy, LGTM-component naming (without the acronym)
- https://grafana.com/docs/grafana-cloud/send-data/otlp/ — OTLP ingestion into Loki/Mimir/Tempo
- https://grafana.com/docs/loki/latest/get-started/ — Loki overview (checked for LGTM-stack terminology; not found)
