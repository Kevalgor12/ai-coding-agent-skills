---
name: Deployment & release
description: >-
  Plan and execute deployments and releases — choose a deployment strategy
  (rolling/blue-green/canary), manage per-environment configuration, ensure
  a working rollback path, and coordinate release tagging/versioning. Use
  when deploying or cutting a release. Not for local development, and
  honest that this library's deployment-strategy research is thinner than
  its other domains — grounded mainly in scattered framework-specific
  deployment notes, not a dedicated methodology doc.
spec_version: "1.0"
---

## Purpose & scope

Plan deployment strategy, per-environment configuration, rollback, and
release-tagging coordination — beyond both the CI/CD pipeline definition
itself (ci-cd-pipeline) and image
authoring ([containerization](../containerization/SKILL.md)). **This
skill is explicit about a real boundary**: this library's research does
not contain a dedicated, vendor-neutral rolling/blue-green/canary
deployment-strategy methodology document — what exists is a scattering of
framework-specific and edge-deployment notes (Next.js's four documented
deployment paths including Docker, Vue's Node.js-server SSR requirement,
Angular CLI's `ng add angular-cli-ghpages` command, Fastify's serverless
target recommendations). Where a request needs deployment-methodology depth
this library hasn't researched — a specific cloud provider's native
deployment primitives, for instance — this skill says so rather than
inventing generic DevOps advice from general knowledge.

## When to use / When not to use

**Use** when deploying an application or service, cutting a release, or
reviewing an existing deployment's rollback path/environment-config
separation. **Do not use** for local development only, for image authoring
itself once deployment strategy is settled, or for the CI/CD pipeline
definition distinct from the deployment/release strategy running inside it.

## Knowledge

**This library's deployment-strategy grounding is thin, and that's stated
here rather than papered over.** No researched technology in this library
publishes a dedicated rolling/blue-green/canary comparison or methodology
guide — the closest material is framework-specific deployment-path
documentation, which is useful for *how a specific stack gets deployed* but
doesn't answer *which deployment strategy fits a given risk profile* with
research-backed depth. Treat the strategy-selection guidance below as
general engineering judgment, explicitly not as something this library's
research independently corroborates the way, say, the REALTIME batch's
transport comparison does.

**What the research does document, framework by framework:**

- **Next.js** documents four deployment paths, one of which is Docker,
  "supporting all Next.js features," with official example templates for
  standalone output and multi-environment configs
  [Source: nextjs.org/docs/app/getting-started/deploying].
- **Vue's SSR deployment explicitly requires a Node.js server process** —
  rendering-to-string is CPU-intensive, and SSR output is *not* deployable
  as static files, unlike SSG. This is a real, structural constraint: an
  SSR-rendered Vue app cannot be deployed the same way a static-export app
  can [Source: vuejs.org/guide/scaling-up/ssr.html].
- **Angular CLI documents an automatic GitHub Pages deploy** via
  `ng add angular-cli-ghpages` [Source: angular.dev/tools/cli/deployment].
  Angular's containerized-deployment story with Docker specifically is
  **not documented** in this library's research — an inference gap, not a
  confirmed absence.
- **Fastify's documented production deployment targets** include reverse
  proxies and serverless platforms (Google Cloud Run, AWS Fargate, Azure
  Container Instances, with an official Vercel template)
  [Source via integration-map.md — Fastify ↔ Docker].
- **Socket.IO's multi-node deployment requires sticky sessions** at the
  reverse-proxy/load-balancer layer — a real, documented constraint on
  deployment topology for any realtime feature, not specific to any one
  cloud provider [Source: socket.io docs, via realtime-communication's own
  research already cited in this library].

**Release-tagging/versioning coordination** is a workflow-discipline
concern that overlaps with this library's Git-conventions skill
(`SK-CONV-001`) — this skill owns the *deployment*
sequencing (when a tagged release actually rolls out), while the
conventions skill owns the *tagging/commit* discipline itself.

## Decision framework

1. **What's the actual risk tolerance for this deployment?** A
   low-risk-tolerance target (production, customer-facing) warrants a
   strategy with a fast, reliable rollback path (blue-green, or canary with
   automated rollback triggers) over a bare rolling update with no
   built-in reversal.
2. **Does the stack have a documented, framework-native deployment path
   already?** (Next.js↔Vercel/Docker, Vue SSR's Node-server requirement,
   Angular's GitHub Pages CLI command, Fastify's serverless targets) — if
   so, start from that rather than reinventing a generic strategy the
   framework doesn't actually support well.
3. **Is environment-specific configuration actually separated from the
   artifact**, or would deploying the same build to staging vs. production
   require rebuilding it? Config should be injected per-environment, not
   baked into a shared artifact.
4. **Is the rollback path actually working, not just assumed?** A
   deployment strategy without a verified rollback path is not a complete
   plan.
5. **Does this request need deployment-methodology depth beyond what this
   library has researched** (e.g. a specific cloud provider's native
   deployment service)? If so, say so explicitly rather than fabricating
   provider-specific guidance from general knowledge.

## Workflow

1. Confirm the target environment(s) and their risk tolerance.
2. Check whether the stack has a documented, framework-native deployment
   path to start from.
3. Choose a deployment strategy matching the risk tolerance, stating
   plainly that this library's own research doesn't independently
   corroborate a rolling-vs-blue-green-vs-canary comparison — this is
   general engineering judgment, not a researched claim.
4. Design per-environment configuration separation.
5. Verify (not just assume) a working rollback path.
6. Coordinate release tagging/versioning with the deployment sequence.
7. Any production-affecting action is presented for explicit confirmation
   before execution — never applied unilaterally.

## Engineering rules

- State plainly when this skill's guidance is general engineering judgment
  rather than something this library's research corroborates — don't
  present the strategy-selection framework as more grounded than it is.
- Separate environment-specific configuration from the artifact; never bake
  per-environment values into a shared build.
- Verify the rollback path actually works before calling a deployment plan
  complete.
- Start from a stack's documented, framework-native deployment path when
  one exists, rather than a generic strategy the framework doesn't support.
- Never execute a production-affecting deployment action without explicit
  user confirmation.

## Trade-offs

Rolling updates are the simplest to set up but offer the weakest rollback
story (a bad release is already partially live before it's caught).
Blue-green deployment buys instant rollback (switch traffic back to the old
environment) at the cost of running two full environments simultaneously.
Canary deployment buys the ability to catch problems on a small fraction of
traffic before a full rollout, at the cost of more deployment-pipeline
complexity (traffic-splitting, automated health checks/rollback triggers).

## Anti-patterns

- **Presenting this skill's rolling/blue-green/canary framework as
  research-backed** when it's general engineering judgment — this
  library's research doesn't independently corroborate a strategy
  comparison the way other domains' comparisons are grounded.
- **Baking per-environment config into a shared artifact**, forcing a
  rebuild to change environments.
- **Calling a deployment plan complete without verifying the rollback path
  actually works.**
- **Deploying an SSR Vue app as if it were static output** — SSR output
  requires a Node.js server process and is not deployable as static files.
- **Executing a production-affecting deployment action without explicit
  confirmation** — the domain's highest-stakes anti-pattern, given
  deployment actions are frequently hard to reverse.

## Security

Secrets/credentials used during deployment (registry auth, cloud
provider credentials) should never be embedded in the artifact or committed
to config; OIDC-based credential-free deployment (where the target platform
supports it) is preferable to long-lived static keys — this overlaps with
[ci-cd-pipeline](../../core/taxonomy/skill-catalog.md)'s own scope
more than it's a deployment-release-specific concern. Deep threat
modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Not this skill's primary concern; deployment-strategy choice can affect
perceived availability during a rollout (blue-green/canary minimize
user-facing disruption vs. a bare rolling update), but deep performance
method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

Whether a deployment succeeded and whether the rollback path actually works
are the two deployment-specific testing concerns — both should be verified
explicitly (e.g. a smoke test post-deploy, a rehearsed rollback) rather than
assumed. Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If the target environment(s)/risk tolerance are too thin to support a
  strategy decision, request them rather than assuming a default.
- If a deployment/release setup already exists, work within it unless a
  change is explicitly requested.
- If the request needs deployment-methodology depth this library hasn't
  researched (a specific cloud provider's native primitives), state that
  gap explicitly.

## Escalation

- **Any production-affecting deployment action is guarded behind explicit
  confirmation** — this is not optional. Actual execution is also
  frequently host- and infrastructure-specific in a way this skill cannot
  guarantee it can perform directly (the planning/config output is
  advisory; execution may require capabilities — direct cloud-provider
  access, deployment-platform CLIs — not available in every agent
  environment); state that constraint rather than assuming execution
  capability exists.
- A deployment-strategy change for an existing production service (e.g.
  moving from rolling to blue-green) is a significant, hard-to-reverse
  operational decision — presented with trade-offs for explicit
  confirmation.

## Outputs & verification

- **Outputs:** a deployment-strategy recommendation with trade-offs (when
  open, and honestly caveated as general judgment rather than researched
  fact), and a release plan/config (environment separation, rollback path,
  tagging coordination).
- **Verify:** the rollback path is actually working, not assumed;
  environment config is separated from the artifact; any
  production-affecting action is confirmed explicitly before execution.

## References

- [research/knowledge-maps/integration-map.md](../../research/knowledge-maps/integration-map.md)
