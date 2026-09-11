# Audit: INFRA-domain skill generation & validation

Date: 2026-09-10. Scope: three skills — two generic (`SK-INFRA-001`
containerization, `SK-INFRA-003` deployment-release) and one technology
skill (`SK-TECH-docker`). Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).

**Scope note:** the user's 5-item list ("Docker, Container Architecture,
Deployment, Environment Management, Infrastructure Architecture") maps to
3 skills, not 5. "Docker"→`SK-TECH-docker`, "Container Architecture"→
`SK-INFRA-001` (containerization), "Deployment"→`SK-INFRA-003`
(deployment-release) all mapped unambiguously. "Environment Management" is
already a named responsibility inside `SK-INFRA-003`'s scope ("manage
env/config per environment"), not a separate skill. "Infrastructure
Architecture" did not map cleanly to anything — it could have meant the
taxonomy's third INFRA generic (`SK-INFRA-002` ci-cd-pipeline) or the
documented IaC/orchestration-beyond-containers research gap (Terraform,
Kubernetes — flagged in `taxonomy-analysis.md` as needing a dedicated
research pass, no skill exists). Surfaced via `AskUserQuestion` rather than
assumed; the user chose the research-gap interpretation, so `SK-INFRA-002`
was excluded from this batch entirely (neither generated nor treated as a
"held" item — simply out of scope this time), and the IaC/Kubernetes gap
remains a standing, undecided item pending a future research pass, distinct
from the already-flagged Node.js/EDA gaps in the same category.

**Authorship note:** as with all six prior batches, the two generic skills
were authored directly by hand; the one technology skill was delegated to
an agent with pre-verified relationship data (`parents`, `conflicts_with`,
`related_skills`) and pre-verified version/security/performance facts
pulled from `version-matrix.md`/`security-knowledge-map.md`/
`performance-knowledge-map.md`/`integration-map.md`, then independently
re-verified on disk (not trusted from the self-report alone).

## Completed skills

| Skill | ID | Tier | Files | Citations in SKILL.md |
|---|---|---|---|---|
| [containerization](../skills/containerization/) | SK-INFRA-001 | B | yaml, SKILL.md | 6 |
| [deployment-release](../skills/deployment-release/) | SK-INFRA-003 | A | yaml, SKILL.md | 4 |
| [docker](../skills/docker/) | SK-TECH-docker | B | yaml, SKILL.md | 27 |

All three independently confirmed on disk (file existence, line counts) —
not accepted from the agent's self-report alone.

**Mechanical checks run and passed, all three (scripted, not manual):**
- YAML validity for all 3 `skill.yaml` files.
- VR-1 (all always-required fields present) and technology-conditional
  fields (`parents`, `covered_versions`, `version_sensitive_claims`,
  `reverify_triggers`) present for `docker`.
- CE-1 (description ≤ 500 chars) — all three well within range.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically, zero mismatches.
- **`depends_on_skills`-vs-`parents` conflation: zero recurrence**, the
  fifth consecutive batch (after BACKEND, FRONTEND, REALTIME, SEARCH)
  where the technology skill correctly left `depends_on_skills: []` with
  specialization captured only in `parents: [SK-INFRA-001, SK-QA-002]`.
- VR-3 (every `parents`/`related_skills`/`conflicts_with` ID resolves to a
  real taxonomy entry) — all resolve cleanly, including forward references
  to `SK-INFRA-002` (ci-cd-pipeline, unauthored — out of scope this batch,
  not a research gap itself), `SK-QA-002` (security-engineering,
  unauthored), `SK-CONV-001`/`SK-CONV-005` (unauthored), and `SK-QA-004`
  (observability, a documented research-gap skill).
- `conflicts_with: []` for `docker` — correct: Docker is the only
  container-engine technology actually profiled in this library's
  research; no alternative (e.g. Podman) has researched grounding. Same
  "don't invent a conflict with an unresearched technology" discipline
  established across the REALTIME and SEARCH batches, now extended to a
  third domain.
- `execution_tier`/`required_capabilities` consistency: `containerization`
  and `docker` are both Tier B with `shell` (correct — building/running
  containers is inherently a shell-execution concern); `deployment-release`
  is Tier A (planning/config authorship), with its real Tier-C execution
  constraint (host- and infrastructure-specific, not guaranteed available
  in every agent environment) stated explicitly in its Escalation section
  rather than encoded in the single `execution_tier` field — the same
  resolution pattern used for `web-accessibility`'s dual-tier catalog entry
  in the FRONTEND batch.
- The agent correctly removed its pre-created empty `references/`
  directory rather than leaving an unused artifact.
- All relative links resolve.

## Unresolved questions

1. **Docker's Compose V1→V2 container-naming behavior** — the underlying
   research flags an unverified inference here; not pulled into the
   authored skill since it wasn't load-bearing for the skill's declared
   scope, but noted by the authoring agent as a gap in the source material.
2. **No single consolidated Docker breaking-changes page across majors**
   exists in the research — the `docker` skill's Failure Handling section
   correctly instructs falling back to "verify against current Engine
   release notes" given this documented absence, rather than presenting
   a false sense of completeness.
3. **`deployment-release`'s research thinness is stated as the skill's own
   central honesty boundary**, not merely an aside — this library has no
   dedicated, vendor-neutral rolling/blue-green/canary methodology
   document; what exists is scattered framework-specific deployment notes
   (Next.js/Vercel/Docker, Vue's Node-server SSR requirement, Angular's
   GitHub Pages CLI command, Fastify's serverless targets, Socket.IO's
   sticky-session constraint). The skill explicitly flags its own
   strategy-selection framework as general engineering judgment rather
   than a researched claim — the first skill in this project to carry that
   distinction as a first-class, repeated statement throughout its body
   (Knowledge, Engineering rules, Anti-patterns) rather than a single
   caveat.
4. **Angular's containerized-deployment story with Docker specifically is
   not documented** in this library's research (an inference gap per
   `integration-map.md`, not a confirmed absence) — stated as such in
   `deployment-release` rather than assumed either way.

None of these four were load-bearing enough to block any skill — each is a
correctly-surfaced boundary of current research.

## Duplicated responsibilities

**None found.** `docker` explicitly declined to repeat
`containerization`'s general image-authoring, layer-caching, root-daemon
security model, rootless-mode-vs-`userns-remap` distinction, and
multi-platform QEMU-vs-native-builder trade-off, adding only Docker-specific
implementation depth (Engine API versioning, the Go SDK module migration,
Build Checks' independent Buildx/syntax gate, Compose V2's per-field
version gates, cgroup v1's long-tail deprecation, Enhanced Container
Isolation's WSL2/kernel floor). `deployment-release` and `containerization`
also stayed cleanly separated — the former explicitly routes image-authoring
questions back to the latter and vice versa, with no content overlap
between the two generics' Knowledge sections.

## Missing dependencies

- `containerization` forward-references `SK-INFRA-002` (ci-cd-pipeline) and
  `SK-QA-002` (security-engineering), both unauthored.
- `deployment-release` forward-references `SK-INFRA-002`, `SK-CONV-001`,
  `SK-CONV-005`, and `SK-QA-004` (observability, the documented research-gap
  skill), all unauthored.
- `docker` forward-references `SK-QA-002`, unauthored.

None of these fabricate content for the missing skills — all are handled as
non-fabricated forward references, consistent with every prior batch's
pattern (e.g. `python`→`SK-AI-001`, `opensearch`→`SK-QA-004` in earlier
batches).

## Potential corrections

1. **The `depends_on_skills`-vs-`parents` fix continues to hold with zero
   recurrence** across a fifth consecutive batch. No further spec action
   needed.
2. **The "don't invent a conflict with an unresearched technology"
   discipline now spans three domains** (REALTIME's transport triad,
   SEARCH's Elasticsearch gap, and now INFRA's Docker/Podman gap) — worth
   treating as a settled project-wide norm rather than a per-batch
   judgment call at this point.
3. **`deployment-release` is this project's most explicit example yet of a
   skill stating its own research-thinness as a structural feature, not a
   single caveat** — the "general engineering judgment, not a researched
   claim" framing repeats across Knowledge, Engineering rules, and
   Anti-patterns sections. Worth citing as the reference pattern for any
   future skill authored against genuinely thin grounding (per the
   catalog's own "Thin" flags on other entries), rather than each future
   batch re-deriving how to phrase that honesty.
4. **`SK-INFRA-002` (ci-cd-pipeline) remains unauthored** and was
   deliberately excluded from this batch (not generated, not treated as a
   held/deferred research-gap item — simply out of scope per the user's
   chosen interpretation of "Infrastructure Architecture"). A future batch
   naming CI/CD, GitHub Actions, or pipeline design explicitly would close
   this gap the normal way.
5. **The IaC/orchestration-beyond-containers gap (Terraform, Kubernetes)
   remains open and undecided** — genuinely different in status from the
   Node.js and Event-Driven-Architecture gaps (which the user explicitly
   chose to hold/defer): this one was simply routed around by choosing the
   other interpretation of "Infrastructure Architecture," so it's neither
   accepted-and-pending nor rejected — worth a future explicit ask if IaC/
   orchestration coverage becomes relevant.
6. **No skill in this batch was promoted to `final/`** — same standing gap
   as all six prior batches (no executable validator or `evaluations/`
   tests yet).

## Overall assessment

All three skills are internally consistent with the specification,
taxonomy, dependency architecture, and routing architecture, appropriately
grounded (4–27 citations, with `deployment-release`'s 4 being deliberately
light given its own stated research-thinness rather than an authoring
gap), and version-aware where the research supports it: Docker's Engine
API v1.44 floor and pre-v1.40-unsupported boundary, the Go SDK module
migration, Compose V2's per-field version gates, cgroup v1's deprecation
running through May 2029, and Enhanced Container Isolation's WSL2/kernel
floor were all correctly surfaced with precise version ranges. The batch's
most notable structural outcome is `deployment-release`'s honest framing of
its own thin grounding — a genuinely different failure mode than a gap in
what the *agent* found (the agents found everything the research contains;
the research itself is simply thinner here than in other domains) — and
the skill treats that as a first-class fact to state repeatedly rather than
a single disclaimer buried in one section. The batch also extended two
established disciplines cleanly into a new domain: declining to invent a
`conflicts_with` relationship for an unresearched alternative (Podman), and
resolving a dual-tier catalog entry (`A (plan) / C (execute)`) the same way
`web-accessibility` did in the FRONTEND batch — picking the primary tier
for `execution_tier` and stating the secondary constraint in prose.
