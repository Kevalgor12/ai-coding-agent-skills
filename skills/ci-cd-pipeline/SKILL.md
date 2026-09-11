---
name: CI/CD pipeline
description: >-
  Design a CI/CD pipeline — stage sequencing (build/test/lint/deploy),
  dependency caching, secrets via OIDC rather than static long-lived keys,
  least-privilege tokens, and reusable workflow structure. Use when
  setting up or changing CI/CD. Not for containerization itself or for
  deployment/release strategy, which are separate skills — and not
  assumed to be directly executable, since this library's capability map
  found no ecosystem that drives GitHub Actions natively.
spec_version: "1.0"
---

## Purpose & scope

Design CI/CD pipeline stages, caching, and secrets/token handling —
independent of platform, though in this library's research GitHub Actions
is the only profiled implementation, so the paired
[github-actions](../github-actions/SKILL.md) technology skill adds
implementation depth rather than covering a meaningfully different
platform. Containerizing the app itself belongs to
[containerization](../containerization/SKILL.md); deployment/release
strategy running inside the pipeline belongs to
[deployment-release](../deployment-release/SKILL.md). **This skill does not
assume it can execute a pipeline directly** — this library's own capability
map found no ecosystem that drives GitHub Actions (or any CI platform)
natively; treat pipeline execution as external, and state that constraint
rather than assuming it away.

## When to use / When not to use

**Use** when setting up CI/CD for a project that lacks it, changing an
existing pipeline's stages/caching/secrets, or reviewing a pipeline's
security posture. **Do not use** for a local-only workflow with no CI in
scope, for containerizing the app itself, or for deployment/release
strategy running inside the pipeline.

## Knowledge

**Secrets should never appear as plaintext in pipeline configuration, and
automatic log redaction is explicitly documented as best-effort, not
guaranteed** [Source: docs.github.com/en/actions/security-for-github-
actions/security-guides/security-hardening-for-github-actions]. Registered
secrets are the mechanism; when a runtime value needs masking beyond what's
registered as a secret, an explicit masking directive is required. A real,
easy-to-miss corollary: **treating a structured blob (JSON/XML/YAML) as a
single secret is discouraged**, since log redaction does exact-string
matching — an encoded or transformed derivative of that value won't be
reliably masked. Each derived value that could leak should itself be a
registered secret, not just its parent blob.

**Least-privilege tokens are the default posture, not an opt-in
hardening step.** A pipeline's default token should carry read-only
content access at minimum, elevated only per-job when a specific step
genuinely needs write access; third-party actions/steps should be pinned
to an immutable reference (a full-length commit SHA, not a mutable tag or
branch) — documented as "currently the only way to use an action as an
immutable release" [Source: docs.github.com/en/actions/security-for-
github-actions/security-guides/security-hardening-for-github-actions].

**OIDC replaces long-lived static cloud credentials with per-job,
auto-expiring tokens** — a workflow authenticates to a cloud provider
(AWS, Azure, GCP, HashiCorp Vault) by exchanging a short-lived JWT for
short-lived cloud credentials, eliminating the need to store long-lived
cloud secrets in the CI platform at all [Source: docs.github.com/en/
actions/security-for-github-actions/security-hardening-your-deployments/
about-security-hardening-with-openid-connect]. This is the default-
preferred mechanism for any deploy step reaching a supporting cloud
provider — reach for static keys only when the target genuinely doesn't
support OIDC.

**Dependency caching is the primary documented lever for pipeline speed**,
with real, concrete limits worth designing around rather than discovering
by surprise: caches unused for 7 days are evicted, and there's a default
per-repository cap (10GB) with LRU eviction once exceeded [Source via
performance-knowledge-map.md]. A pipeline relying on a cache that silently
falls outside these bounds degrades to uncached performance without an
obvious error — worth stating in the pipeline's own documentation, not
just assuming the cache will always hit.

**Matrix strategies parallelize independent build/test permutations across
runners simultaneously** — `max-parallel` throttles concurrency,
`fail-fast` (default true) cancels the remaining matrix jobs on first
failure. Concurrency/queueing limits act as a hard upper bound on
achievable parallelism per account/plan; hitting them manifests as queued,
not immediately-running, jobs — a real capacity constraint distinct from
the pipeline's own design [Source via performance-knowledge-map.md].

## Decision framework

1. **What gates the merge?** Tests, lint, and build should block merge by
   default — a pipeline that runs these advisory-only when they're meant
   to gate is a common, easy-to-miss design mistake.
2. **Does the deploy target support OIDC?** If yes, use it by default over
   static long-lived keys — this isn't a case-by-case judgment call, it's
   the default posture unless the target genuinely doesn't support it.
3. **What's the minimum token scope each job actually needs?** Default to
   read-only content access; elevate only the specific job that needs
   write access, rather than granting broad permissions to the whole
   pipeline by default.
4. **Is dependency caching designed around its real limits** (7-day
   eviction, per-repo size cap, LRU once exceeded)? A cache key strategy
   that silently falls outside these bounds degrades performance without
   an obvious signal.
5. **Would a matrix strategy meaningfully parallelize this pipeline's
   build/test permutations**, and does `fail-fast`'s default (cancel
   remaining jobs on first failure) match what's actually wanted, or does
   this pipeline need visibility into every permutation's result even
   after one fails?

## Workflow

1. Confirm the repo's build/test/lint commands.
2. Design stage sequencing so tests/lint/build gate the merge.
3. Design caching around dependency-install steps, accounting for the
   platform's real cache-size/eviction limits.
4. Design secrets handling: OIDC by default for supporting cloud targets,
   registered secrets (never plaintext) otherwise, with each
   individually-sensitive derived value registered separately from any
   structured blob it came from.
5. Scope tokens least-privilege by default, elevated only per-job as
   needed; pin third-party actions/steps to immutable references.
6. If independent build/test permutations exist, consider a matrix
   strategy, deciding deliberately on `fail-fast` behavior.
7. Hand off to containerization for image-authoring specifics, and to
   deployment-release for the deploy step's own strategy, rather than
   designing those inline here.
8. State plainly that this skill authors pipeline configuration but does
   not assume it can execute the pipeline directly.

## Engineering rules

- Tests/lint/build gate the merge by default; a pipeline that runs them
  advisory-only should be a deliberate, stated choice, not an oversight.
- OIDC over static long-lived keys whenever the target supports it.
- Tokens scoped least-privilege by default; third-party actions/steps
  pinned to immutable references, not mutable tags.
- Each individually-sensitive value gets its own registered secret, not
  just the structured blob it's embedded in.
- Design caching around the platform's real size/eviction limits, not an
  assumption of unlimited cache.

## Trade-offs

Matrix strategies buy parallelism at the cost of consuming more concurrent
runner capacity (hitting account/plan concurrency limits sooner).
`fail-fast: true` (the default) buys faster feedback on the first failure
at the cost of losing visibility into whether other matrix permutations
would have also failed. OIDC buys eliminating long-lived cloud secrets at
the cost of requiring the target platform to support OIDC federation in the
first place — not every deploy target does.

## Anti-patterns

- **Running tests/lint/build as advisory-only** when they're meant to gate
  the merge — a silent, easy-to-miss pipeline design mistake.
- **Storing plaintext secrets in workflow config**, or treating a
  structured blob as a single secret when its derived values also need
  independent masking.
- **Granting broad, ungated token permissions by default** instead of
  least-privilege, per-job elevation.
- **Pinning third-party actions/steps to a mutable tag or branch** instead
  of an immutable commit-SHA reference.
- **Assuming unlimited cache capacity** without accounting for the
  platform's real 7-day eviction / size-cap / LRU behavior.

## Security

Secrets are never plaintext in configuration; automatic log redaction is
best-effort, not guaranteed, so individually-sensitive derived values need
their own registered secret rather than relying on a parent blob's
redaction. OIDC replaces long-lived cloud credentials with per-job
auto-expiring tokens for supporting targets. Tokens default to
least-privilege, elevated only per-job; third-party actions/steps are
pinned to immutable commit-SHA references. Deep threat modeling is owned
by [security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Dependency caching is the primary lever, designed around real platform
limits (7-day eviction, size cap, LRU) rather than assumed unlimited.
Matrix strategies parallelize independent permutations, bounded by
account/plan concurrency limits. Deep performance method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

The pipeline's own job is largely *to run* tests/lint/build as gates —
this skill designs that gating structure; the actual test strategy being
gated is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If build/test/lint commands aren't yet established, request them rather
  than guessing a pipeline structure.
- If an existing pipeline is in place, work within its structure unless a
  rework is explicitly requested.

## Escalation

- A pipeline change affecting production deployment (not just build/test
  gating) is presented with trade-offs for explicit confirmation, since it
  can have real production impact.
- Pipeline execution capability varies across agent hosts — this skill
  authors configuration; actually running the pipeline is external and
  should be stated as such rather than assumed.

## Outputs & verification

- **Outputs:** pipeline configuration (stages, caching, secrets/OIDC
  handling, token scoping).
- **Verify:** tests/lint/build actually gate the merge; secrets use OIDC
  where supported, never plaintext; tokens are least-privilege by default.

## References

- [research/knowledge-maps/security-knowledge-map.md](../../research/knowledge-maps/security-knowledge-map.md)
- [research/knowledge-maps/performance-knowledge-map.md](../../research/knowledge-maps/performance-knowledge-map.md)
