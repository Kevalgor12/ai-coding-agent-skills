---
name: OpenSearch
description: >-
  OpenSearch cluster architecture, index/mapping/analyzer design and
  mapping-explosion avoidance, the security plugin's auth surface (basic/
  JWT/OIDC/SAML/LDAP/Kerberos/client-cert) with RBAC/document-/field-level
  security, transport-vs-HTTP TLS and demo-cert replacement, and shard/JVM/
  thread-pool/circuit-breaker tuning. Use when the stack runs OpenSearch.
  Not for choosing a search engine (search-integration) or general
  observability instrumentation (a research gap in this library).
spec_version: "1.0"
---

## Purpose & scope

Apply OpenSearch correctly and version-appropriately once it is (or will be)
the search engine: cluster/node architecture, index/mapping/analyzer design,
the security plugin's authentication and access-control surface, and
shard/JVM/thread-pool/circuit-breaker performance tuning. The engine-selection
decision itself — DB-native FTS vs. a dedicated engine vs. vector search, and
the index-sync-with-source-of-truth risk that comes with choosing a dedicated
engine — is owned by the parent skill, `search-integration`
([`skills/search-integration/SKILL.md`](../search-integration/SKILL.md)); this
skill picks up once OpenSearch is the answer.

## When to use / When not to use

**Use** when the stack runs OpenSearch — an OpenSearch client, a connection
config, a Docker/Helm/Kubernetes-Operator deployment, or a task naming
OpenSearch or one of its features (k-NN, cluster manager node, security
plugin, Data Prepper, OpenSearch Dashboards, ISM, Query DSL). **Do not use**
when the engine choice is still open (route to `search-integration`); when
the task is actually about Elasticsearch (this library has no first-party
Elasticsearch research — do not improvise a comparison); when the task is
general application logging/metrics/tracing instrumentation unrelated to
OpenSearch's own log-analytics role (route to `observability`, a documented
research gap in this library — do not fabricate that content here); or when
a database already in use (PostgreSQL, Redis) already covers a simple
full-text need.

## Knowledge

**Cluster architecture.** A cluster is a set of interconnected nodes; nodes
take on distinct roles — **cluster manager** (coordination/state, the
successor term to "master node"), **data** (store and search index data),
**ingest** (run ingest pipelines before indexing), and **coordinating**
(route requests without storing data or managing state)
[Source: https://docs.opensearch.org/latest/tuning-your-cluster/]. An index
is a logical document container with a **mapping** (field types and
analyzers) and settings for shard/replica counts; each **shard** is a
self-contained Lucene index, and **replicas** provide redundancy and spread
search load across copies
[Source: https://docs.opensearch.org/latest/getting-started/concepts/].
Plugin-based extensibility is core to the architecture: k-NN (vector
search), neural search, ML Commons, SQL/PPL, index state management, and the
security plugin are all layered on the engine as plugins
[Source: https://docs.opensearch.org/latest/tools/]. The project ships
OpenSearch, **OpenSearch Dashboards** (visualization UI), and **Data
Prepper** (ingestion/transform collector) as separate, complementary
components alongside language clients
[Source: https://docs.opensearch.org/latest/about/].

**Index/mapping/analyzer mechanics.** Explicit mappings are recommended over
relying on dynamic mapping wherever possible, to avoid "mapping explosion" —
an index accumulating an excessive number of fields (commonly triggered by
highly variable document structures, e.g. logs or user-generated fields),
which degrades memory/performance/cluster stability
[Source: https://docs.opensearch.org/latest/mappings/mapping-explosion/].
Setting an index's dynamic mode to `"dynamic": "strict"` rejects documents
with unmapped fields, positively enforcing a fixed schema at the cost of
requiring all object structures upfront
[Source: https://docs.opensearch.org/latest/mappings/]. For high-cardinality
or variable nested JSON, the **flat object** field type treats a whole JSON
object as one field (subfields reachable via dot-path) instead of indexing
each subfield individually, sidestepping mapping explosion for that case
[Source: https://docs.opensearch.org/latest/mappings/supported-field-types/flat-object/].

**Three-tier version lifecycle.** As of this skill's research date, **1.x is
end-of-life** (maintenance ended 2025-05-06, unsupported); **2.x is in
maintenance-only mode** until 4.0 reaches GA, with 2.19.x patches scheduled
through December 2026 (latest patch 2.19.6, 2026-07-02); **3.x is the
actively-developed major**, currently at 3.8.0 (2026-08-04), with 3.9.0's RC
window Sep 15–29 2026 and 3.10.0's Nov 3–17 2026 — roughly an eight-week
minor-release cadence. Versions stay under maintenance until the next major
enters maintenance, or 1 year passes, whichever is longer; medium-or-higher
severity vulnerabilities are patched within 60 days of public disclosure in
actively-maintained versions
[Source: https://opensearch.org/releases/; research/knowledge-maps/version-matrix.md].
**Applies to:** the lifecycle staging above is a point-in-time snapshot (as of
2026-09); confirm current status against `opensearch.org/releases` before
advising on upgrade timing (a `reverify_trigger` for this skill).
**Version-sensitive (>=3.0):** OpenSearch 3.0 raised the minimum JDK to
**21** (a hard break from 1.x/2.x), upgraded the search core to **Apache
Lucene 10**, permanently disabled the Java Security Manager, and moved the
transport layer to Apache HttpClient 5.x
[Source: https://github.com/opensearch-project/OpenSearch/issues/3351].

**Security-plugin surface.** See the dedicated Security section below — this
is the single richest differentiator vs. a simpler DB-native FTS setup.

## Decision framework

1. **Authentication method — fit it to the deployment's identity
   infrastructure, don't default to basic auth.** The security plugin
   supports HTTP basic auth, JWT, OpenID Connect, SAML, Active Directory/
   LDAP, proxy-based auth, client-certificate auth, and Kerberos
   [Source: https://docs.opensearch.org/latest/security/]. An org already
   running LDAP/AD should integrate there rather than maintaining a separate
   internal user database; an org with an existing OIDC/SAML IdP should
   federate through it; basic auth (internal user DB) is defensible only for
   small/simple deployments without existing identity infrastructure.
2. **Shard strategy — size and count from the workload shape, not a
   default.** Search-latency-sensitive workloads (e.g. application search)
   fit **10–30 GB per shard**; write-heavy/analytics workloads (e.g. log
   processing) fit **30–50 GB per shard**
   [Source: https://opensearch.org/blog/optimize-opensearch-index-shard-size/].
   Too many small shards wastes JVM heap on per-shard metadata; too few
   large shards limits parallelization and risks relocation/recovery
   trouble. The blog is explicit that only performance testing with
   different shard counts determines the ideal count for a specific
   index/workload — treat the ranges as a starting point, not a formula.
3. **Benchmark before a mapping/query change reaches production, or state
   why not.** **OpenSearch Benchmark** is the official tool for validating
   cluster performance before/after upgrades or mapping/query changes
   [Source: https://docs.opensearch.org/latest/tools/benchmark/]. Skipping
   it is defensible for a low-risk, low-traffic change; skipping it silently
   for a change touching a production-scale index is not.
4. **Simplest first:** an explicit mapping with sensible field types and the
   documented defaults for the security plugin (enabled, real certs) covers
   most deployments — don't reach for custom analyzers, ISM policies, or
   cross-cluster replication before a concrete requirement calls for them.

## Workflow

1. Determine the OpenSearch major.minor version (cluster, image tag, or
   manifest) — required before recommending any version-gated feature
   (e.g. a >=3.0 capability).
2. Design the index mapping explicitly (field types, analyzers) rather than
   relying on dynamic mapping; apply `"dynamic": "strict"` or the flat-object
   type where document shape is variable or externally controlled.
3. Configure the security plugin: pick an authentication method fitting the
   deployment's identity infrastructure (decision-framework step 1), enable
   RBAC/document-/field-level security as required, and replace the demo TLS
   certificates before anything touches production.
4. Size shards from the workload shape (decision-framework step 2); tune
   thread-pool and circuit-breaker/admission-control settings, and separate
   index/search workloads if both are heavy.
5. Run **OpenSearch Benchmark** against a staging/representative cluster
   before a mapping/query change reaches production, or state explicitly why
   it's being skipped for a low-risk change.
6. Verify against the checks in Outputs & verification before declaring done.

## Engineering rules

- Define explicit mappings for known fields rather than relying on dynamic
  mapping, especially for logs or user-generated-content indices
  [Source: https://docs.opensearch.org/latest/mappings/mapping-explosion/].
- Match shard size to the workload (10–30GB search-latency-sensitive,
  30–50GB write-heavy/analytics), and validate with performance testing
  rather than assuming a fixed count
  [Source: https://opensearch.org/blog/optimize-opensearch-index-shard-size/].
- Never leave a production deployment on the bundled demo TLS certificates or
  with `plugins.security.disabled: true` — see Security below.
- Separate index (write) and search (read) workloads where cluster resources
  allow, to avoid resource contention
  [Source: https://docs.opensearch.org/latest/tuning-your-cluster/].
- Tag every version-specific recommendation (e.g. a >=3.0 feature) with the
  range it applies to; confirm the cluster's actual major.minor before
  giving version-gated guidance (rule VA-3).
- Don't restate `search-integration`'s engine-selection framework or the
  Elasticsearch-research-gap caveat — this skill assumes OpenSearch is
  already chosen.

## Trade-offs

Explicit mappings cost more upfront design effort than dynamic mapping but
avoid mapping explosion and its memory/stability fallout — worth it for any
index with variable or externally-controlled document shape. Smaller shards
(toward the 10GB end) improve search latency and parallelization but
increase per-shard heap overhead and cluster metadata load; larger shards
(toward 50GB) suit write-heavy ingestion but risk slower relocation/recovery
and coarser-grained parallelism. Enabling the full security-plugin surface
(RBAC, document/field-level security, audit logging) adds real operational
and debugging complexity over running with a simpler auth setup — justified
whenever the deployment has multi-tenant, compliance, or fine-grained
access-control requirements, overkill for a single-team internal cluster
with network-level isolation already in place.

## Anti-patterns

- **Leaving the bundled demo TLS certificates in a production deployment**
  — the docs call replacing them "critical," and running with defaults is
  treated as something to correct, not a valid choice
  [Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md].
- **Undersized/over-numerous or oversized shards for the workload shape** —
  too many small shards wastes heap on metadata; oversized shards risk
  relocation/recovery failures — both are documented anti-patterns, not
  just theoretical concerns
  [Source: https://opensearch.org/blog/optimize-opensearch-index-shard-size/].
- **Ignoring thread-pool and circuit-breaker/admission-control settings**
  and hitting out-of-memory failures under load instead of tuning
  deliberately for the expected concurrency and workload mix
  [Source: https://docs.opensearch.org/latest/tuning-your-cluster/].
- **Relying on unconstrained dynamic mapping** against highly variable
  document sources, producing mapping explosion
  [Source: https://docs.opensearch.org/latest/mappings/mapping-explosion/]
  — the domain's over-engineering-by-neglect trap: it's easier to let the
  cluster infer structure than to design it, until it silently degrades
  cluster stability.
- **Disabling the security plugin** (`plugins.security.disabled: true`) and
  leaving it off rather than treating it as a temporary, reverted state
  [Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md].

## Security

The security plugin's authentication backends: **HTTP basic auth, JWT,
OpenID Connect, SAML, Active Directory/LDAP, proxy-based auth, client
certificate auth, and Kerberos**
[Source: https://docs.opensearch.org/latest/security/]. Access control is
**role-based (RBAC)** with fine-grained capabilities: **document-level
security**, **field-level security**, **field masking**, user impersonation
controls, API key management, and anonymous-authentication options
[Source: https://docs.opensearch.org/latest/security/]. Audit logging is
supported with configurable field references and multiple storage backends
for compliance tracking; administration includes YAML-based backend config,
a `securityadmin` CLI tool, configuration versioning, and keystore
management for sensitive values
[Source: https://docs.opensearch.org/latest/security/].

**TLS is configured separately for two layers**: transport (node-to-node)
and HTTP (client-to-node), with self-signed-certificate support and
FIPS-compliance-oriented settings
[Source: https://docs.opensearch.org/latest/security/]. Certificate paths for
both layers (`pemcert`, `pemkey`, `pemtrustedcas`) are set in `opensearch.yml`;
authentication-backend setup lives in `config.yml` inside the
`opensearch-security` config directory
[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md].
**Custom (non-demo) certificates must be stored under
`<OPENSEARCH_HOME>/config/` with private keys at file mode `600` and public
certificates at `644`**, and configuration changes made via `config.yml` are
applied by running the bundled `securityadmin` script
[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md].
**Replacing the bundled demo certificates with trusted ones is explicitly
"critical" for production** — the docs frame running production on demo
certs as a real gap, not an acceptable default
[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md].
The security plugin can be disabled entirely via
`plugins.security.disabled: true` in `opensearch.yml`, but the docs present
this as an option to be reverted, not a supported production posture
[Source: https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md].
**Version-sensitive (>=3.0):** thread-context permission requirements for
header-manipulation methods tightened as part of the 3.0 breaking changes
[Source: https://github.com/opensearch-project/OpenSearch/issues/3351].
Deep cross-cutting threat modeling beyond this engine-specific surface is
owned by `security-engineering` — reference it, don't restate it here.

## Performance

Tuning is organized around three levers
[Source: https://docs.opensearch.org/latest/tuning-your-cluster/]:
**thread-pool settings** (concurrency), **circuit-breaker and admission-
control settings** (preventing out-of-memory conditions under load), and
**separating index (write) and search (read) workloads** to avoid resource
contention between ingestion and query traffic.

**Shard sizing** is a first-class lever: **10–30GB per shard** for
search-latency-sensitive workloads, **30–50GB per shard** for write-heavy/
analytics workloads; too many small shards wastes JVM heap on per-shard
metadata, too few large shards limits parallelization — only performance
testing different shard counts determines the ideal count for a given
index/workload
[Source: https://opensearch.org/blog/optimize-opensearch-index-shard-size/].

**JVM heap:** documented guidance, though the exact source page wasn't
independently re-verified verbatim in this library's research, points to
setting `-Xms` equal to `-Xmx` at roughly **50% of available system RAM**,
up to a practical **~32GB ceiling** (beyond which JVM compressed-oops
addressing stops applying, reducing memory efficiency), configured via
`config/jvm.options`
[Source: https://docs.opensearch.org/latest/tuning-your-cluster/ — treat as
inference per research/technologies/opensearch.md, not a verbatim-quoted
doc statement].

**OpenSearch Benchmark** is the official performance-testing tool: it runs
defined workloads against a cluster (pre-built or custom), supports corpus
generation, telemetry, target-throughput configuration, and distributed load
generation, and is the documented way to validate cluster performance before
and after upgrades or mapping/query changes
[Source: https://docs.opensearch.org/latest/tools/benchmark/]. Cross-cutting
performance method beyond these OpenSearch-specific levers is owned by
`performance-engineering` — referenced, not restated.

## Testing

The officially documented, JVM-ecosystem testing story is
**`opensearch-testcontainers`** — an official Testcontainers module
(`opensearch-project/opensearch-testcontainers`) that runs real OpenSearch
Docker containers inside JUnit 4/JUnit 5 integration-test suites
[Source: https://github.com/opensearch-project/opensearch-testcontainers].
**OpenSearch Benchmark** doubles as the closest official analogue to a
cluster-level performance-test framework (see Performance above)
[Source: https://docs.opensearch.org/latest/tools/benchmark/]. The Dev
Tools console (in OpenSearch Dashboards) and a **Query Profiler** are
documented as manual/exploratory query-validation aids, distinct from
automated testing
[Source: https://docs.opensearch.org/latest/troubleshoot/]. This library's
research is silent on an official testing story for non-JVM ecosystems
(e.g. a Python/Node-specific test-container equivalent) — do not invent one;
say the research doesn't cover it if asked. Cross-cutting test strategy is
owned by `testing-strategy` — referenced, not restated.

## Failure handling

- If the OpenSearch major.minor version cannot be determined, ask for it or
  explicitly state the version the guidance assumes — never assume "latest"
  silently (rule VA-3).
- If shell is unavailable or denied, degrade to advisory mapping/security/
  tuning config output and state that no cluster or testcontainer command
  was actually run.
- If the request is really about choosing a search engine, route to
  `search-integration` rather than assuming OpenSearch.
- If the request is Elasticsearch-specific, state plainly that this
  library has no first-party Elasticsearch research rather than answering
  as if the two engines are interchangeable.

## Escalation

- Replacing a production cluster's TLS certificates, or disabling the
  security plugin (`plugins.security.disabled: true`), is a trust-boundary
  change — flagged and confirmed before applying, never applied silently.
- A shard-count/topology change on an existing populated index requires
  reindexing — presented with trade-offs for explicit confirmation, not
  applied unilaterally.

## Outputs & verification

- **Outputs:** index/mapping/analyzer JSON or security-plugin/TLS/auth-
  backend configuration; thread-pool/circuit-breaker/shard-sizing settings;
  analysis with rationale and the OpenSearch version it applies to.
- **Verify:** shard size/count matches the workload shape (10–30GB vs.
  30–50GB), not a default; every version-specific claim is tagged with its
  range; a production-bound security config leaves neither demo TLS certs
  nor a disabled security plugin in place; a production-bound mapping/query
  change is checked against a benchmark or an explicit rationale for
  skipping one.

## References

- Source list: see `skill.yaml.source_references` (OpenSearch official
  docs and GitHub, retrieved 2026-09-10, via
  `research/technologies/opensearch.md` and
  `research/knowledge-maps/version-matrix.md`).
- [`skills/search-integration/SKILL.md`](../search-integration/SKILL.md) —
  parent skill; owns engine selection and index-sync-drift risk.
