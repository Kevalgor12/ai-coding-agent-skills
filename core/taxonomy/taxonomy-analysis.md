# Taxonomy Analysis & Decisions

The decision analysis the brief requires, over the catalog in
[skill-catalog.md](skill-catalog.md). Every determination traces to the
research in [`research/`](../../research/).

## Summary counts

- **Generic skills (Layers 0–3):** 31 proposed.
- **Technology skills (Layer 4):** 38 proposed, mapping the 44 researched
  technologies (6 folded via merges — see below).
- **Total proposed:** 69 skills.
- **Mandated first-class skills:** 2, both ruled in (`git-conventions`, `code-commenting`).
- **Merges applied:** 6 technology merges + 3 generic/tech unifications.
- **Non-promoted technologies:** 2 (`ECMAScript`, `GitHub`).
- **Skills flagged as research-gaps (create, but research first):** 3
  (`observability`, `llm-application-engineering`, plus the thin
  `project-management`).

---

## Mandated-skill rulings

The brief asked specifically whether two capabilities must be first-class skills.
**Both are ruled first-class**, and both are specified in full in the catalog.

### 1. Professional Git branch naming & commit messages → YES, first-class (`SK-CONV-001`)

**Ruling:** first-class, standalone, Layer-2. Not folded into a broader git skill.

**Why standalone rather than part of a general "git" skill:** the research shows
git concerns split into three genuinely distinct activation triggers —
*composing commit/branch text* (this skill), *git operations* (branching,
rebase, worktrees → `SK-CONV-008`), and *reviewing changes* (`SK-CONV-007`).
Bundling them would violate correct-activation (a "write a commit message"
request would needlessly load rebase/PR machinery) and clean boundaries.

**Required behaviors (as the brief specified, encoded in the spec):**
- Supports the professional prefix set: `feat`, `feature`, `fix`, `bugfix`,
  `hotfix`, `refactor`, `chore`, `docs`, `test`, `perf`, `ci`, `build`,
  `release`.
- **Respects an existing repository convention when one exists** — detection
  (git log, commitlint/Conventional-Commits config, contribution docs, branch
  patterns) runs *first*, and the detected convention overrides the default
  prefix set. This is encoded as a hard conflict rule: "the convention always
  wins."
- Concise imperative commit subjects; body only when it adds real context (also
  honors this project's own recorded preference for one-line messages).
- Never fabricates ticket IDs or attribution/signature lines the repo doesn't
  already use.

### 2. Human-readable code commenting → YES, first-class (`SK-CONV-002`)

**Ruling:** first-class, standalone, Layer-2, separate from
`technical-documentation` (`SK-CONV-006`) because in-code comments and prose
docs have different activation triggers and different failure modes.

**Required behaviors (as the brief specified, encoded in the spec):**
- **Requires** useful, natural comments: the *why*, non-obvious constraints,
  invariants, workarounds, surprising behavior.
- **Prevents**, explicitly: phase/step-narration comments; AI/tool signatures or
  attribution inside code; decorative comments (banner bars, separators);
  comments that merely restate obvious code.
- Matches the file's existing comment style; prefers deleting stale/redundant
  comments over "fixing" them.

Both rulings align with practices already baked into this project's own working
conventions, which is corroborating evidence they belong as durable, first-class
skills rather than ad-hoc guidance.

---

## Skills to create

The full catalog is the "to create" set. Recommended **build order** (by
dependency and leverage, not all at once):

1. **Conventions first (Layer 2):** `git-conventions`, `code-commenting`,
   `code-quality`, `code-review`. These apply to *every* other skill's output,
   are pure Tier-A (portable everywhere), and are the two mandated skills plus
   their closest neighbors — highest leverage, lowest risk, no research gaps.
2. **Orchestration core (Layer 0):** `skill-router`, `capability-adapter`.
   Needed before the library has enough skills to compose, and
   `capability-adapter` is what makes everything else vendor-neutral in practice.
3. **High-frequency domain skills (Layer 3):** `api-design`, `data-modeling`,
   `orm-integration`, `testing-strategy`, `frontend-architecture`,
   `security-engineering` — the domains most tasks touch.
4. **Their dominant technology specializations (Layer 4):** start with the
   technologies with the richest, least-caveated research and highest usage
   (`typescript`, `react`, `nextjs`, `postgresql`, one ORM, `jest-vitest`,
   `playwright`, `docker`).
5. **Remaining Layer-3 + Layer-4**, breadth-first by demand.
6. **Research-gap skills last**, and only after their prerequisite research
   exists (`observability`, `llm-application-engineering`).

## Skills to merge

Each merge is justified by the research (tight coupling, choose-one alternatives,
or a single dominant implementation) and serves minimal-duplication + context-efficiency.

| Merge | Into | Justification |
|---|---|---|
| OpenAPI + Swagger | `SK-TECH-openapi-swagger` | Swagger is *tooling for* the OpenAPI spec (research: "consumes and visualizes… rather than defining it"). Always used together; one activation trigger. |
| Jest + Vitest | `SK-TECH-jest-vitest` | Near-identical API surface (Vitest is Jest-compatible); a choose-one decision. One skill covers both and states the choice. |
| HTML + CSS | `SK-TECH-web-standards` | Both foundational web-platform primitives, almost always co-present; separate skills would co-trigger constantly. |
| ECMAScript | `SK-TECH-typescript` (+ code-quality) | A standalone ECMAScript skill has no distinct activation vs. TypeScript/JS. Folded, not dropped. |
| WebSocket API | mostly absorbed by `SK-BE-004` (realtime-communication) | The raw browser primitive is thin as a standalone; kept as a minimal tech skill only for its lifecycle/framing specifics, with the transport-selection judgment living in the generic skill. |
| Docker(generic) + containerization; GitHub Actions(generic) + ci-cd; Google SEO(generic) + seo-optimization; Google AdSense + web-monetization | respective unified skills | In *this* technology set each capability has a single dominant implementation, so a separate generic + tech skill would be pure duplication. If the library later adds a second implementation (e.g. GitLab CI, Podman), split the generic skill back out then — noted so the merge is reversible by design. |

## Skills to split

Broad capability areas from the brief that must **not** be single skills, because
one skill would have muddy boundaries and mis-trigger:

| Broad area | Split into | Why |
|---|---|---|
| "Git" | `git-conventions` + `git-workflow` + `code-review` | Three distinct activation triggers (text vs. operations vs. review) — see mandated ruling #1. |
| "Database" | `data-modeling` + `database-operations` + `caching-strategy` + `search-integration` + `data-migration` + per-DB tech skills | "Database" spans schema design, query tuning, caching, search, and migration — different tasks, different skills; each DB technology then specializes the relevant ones. |
| "API" | `api-design` (REST) + `graphql-api-design` + `authentication-authorization` + `SK-TECH-openapi-swagger` | REST and GraphQL have different failure modes; auth is cross-cutting; spec tooling is a tech skill. |
| "Testing" | `testing-strategy` (generic) + `SK-TECH-jest-vitest` + `SK-TECH-playwright` | Strategy (what to test at which layer) is version-stable and tech-neutral; tool specifics are version-sensitive tech skills. |
| "Frontend" | `frontend-architecture` + `ui-ux-design` + `styling-systems` + `web-accessibility` + `rendering-strategy` + framework tech skills | Distinct concerns with distinct triggers; a single "frontend" skill would load styling machinery for an architecture question. |
| "Infrastructure" | `containerization` + `ci-cd-pipeline` + `deployment-release` | Container authoring, pipeline design, and deploy/release are separate activities. |

## Unnecessary or non-promoted skills

Not created as standalone skills (avoiding duplication and mis-activation):

- **ECMAScript (standalone):** no distinct activation vs. TypeScript/JS. Folded
  into `SK-TECH-typescript`. Its research doc remains a reference.
- **GitHub (the platform, standalone):** its concerns are already owned by
  `git-workflow` (repos/branches/PRs), `ci-cd-pipeline` (Actions/deployments),
  `code-review` (PR review), and `project-management` (issues/releases). A
  standalone "GitHub" skill would duplicate all four and mis-trigger on any
  git task. Its research doc remains a reference.
- **A separate generic skill *plus* a tech skill** for Docker / GitHub Actions /
  Google SEO / AdSense — unified per the merge table above (single dominant
  implementation in this set).

Nothing from the research is *discarded* — non-promoted technologies keep their
research docs; they simply don't get a dedicated activating skill.

## Missing capabilities

Capabilities the brief named (or the research implies are needed) that the
current research does **not** adequately ground. These are surfaced rather than
faked — consistent with the project's "mark unresolved, don't guess" rule.

| Capability | Status | Action |
|---|---|---|
| **Observability** (logging/metrics/tracing/APM) | **Resolved 2026-09-10.** A dedicated research pass on OpenTelemetry, Prometheus, Grafana, and Sentry closed the original near-zero-grounding gap (`research/technologies/opentelemetry.md`, `prometheus.md`, `grafana.md`, `sentry.md`). | `SK-QA-004` authored, specialized by `SK-TECH-opentelemetry|prometheus|grafana|sentry`. |
| **Reliability / resilience patterns** (retries, circuit breakers, timeouts, bulkheads, graceful degradation) | Genuinely distinct from observability — no resilience-pattern library/framework (Polly/resilience4j/opossum-equivalent) has been researched. Surfaced as its own gap during the observability research pass rather than being folded in. | No skill yet; **add a dedicated research pass** if application-level resilience-pattern guidance is in scope, separate from the now-resolved observability pass. |
| **AI/LLM engineering** | Brief lists it; none of the 44 researched technologies covers LLM app-building. | Skill `SK-AI-001` proposed but flagged; needs research (the session's `claude-api` reference is a start, not library research). |
| **Async messaging / queues** (Kafka, RabbitMQ, SQS) | Concept map flagged: no broker beyond Redis pub/sub researched. | No skill yet; **add a research pass** if the library should cover event-driven/queue architectures. |
| **Authentication/authorization (unified)** | Concept map flagged auth as fragmented across JWT/OAuth2/MFA/session/RBAC with no unifying skill. | **Created** `SK-BE-005` to unify it — grounded in the fragments the research does have, but would benefit from dedicated auth research. |
| **Infrastructure-as-code beyond containers** (Terraform, Kubernetes) | K8s appears only as an integration *target* in the research, never researched itself. | No skill; **add research** if IaC/orchestration is in scope. |
| **Product/project management** | Brief lists it; only touchpoint is GitHub issues. | `SK-DISC-004` proposed but **thin**; scope it modestly until there's more grounding. |
| **API consumption/client-side integration** (vs. server design) | Research centers on API *design/serving*; consuming third-party APIs is thin. | Fold into `api-design`/tech skills for now; revisit if demand appears. |

## Classification (as the brief requested)

### Generic skills (technology-neutral)
All of Layers 0–3: `SK-ORCH-001..003`, `SK-DISC-001..004`, `SK-CONV-001..008`,
`SK-FE-001..005`, `SK-BE-001..005`, `SK-DATA-001..006`, `SK-INFRA-001..003`,
`SK-QA-001..004`, `SK-GROW-001..002`, `SK-AI-001`. These hold version-stable
engineering *method* and are the most portable across agents.

### Technology-specific skills
All of Layer 4 (`SK-TECH-*`, 38 skills). These hold version-sensitive,
citation-backed specifics and map 1:1 to a researched technology doc, so a
release only ever touches one skill. They *specialize* a generic skill; they
never re-implement its method.

### Orchestration skills
`SK-ORCH-001` (skill-router), `SK-ORCH-002` (capability-adapter — also the
vendor-neutrality enforcement point), `SK-ORCH-003` (workflow-composer). These
are what let many small skills behave as one coherent library and adapt to each
host agent's real capabilities.

### Review skills
Primary: `SK-CONV-007` (code-review — the general review skill). The taxonomy
treats "review" as a **facet** delivered by several skills rather than one
monolith: `SK-QA-002` (security review), `SK-QA-003` (performance review), and
the review halves of `SK-CONV-002`/`SK-CONV-003` (comment-noise and
code-quality review) all contribute findings that `code-review` aggregates and
ranks. This mirrors how the research found real agents structure review (a
general reviewer delegating to specialized lenses) and keeps each review kind
independently evaluable.

---

## Open decisions for human review before authoring begins

1. **Adopt vs. track agentskills.io.** The whole taxonomy assumes the `SKILL.md`
   convention six vendors cite. Confirm the library *adopts* that format (the
   research recommends reading the spec directly first — still unresolved from
   the ecosystem research).
2. **Depth of the generic/technology split.** This design creates ~69 skills. If
   that is too many to maintain initially, the build order above allows shipping
   Layers 0–2 + the top ~8 technology skills first and growing breadth-first —
   confirm that phasing is acceptable.
3. **Research-gap skills.** Confirm whether observability, LLM engineering, and
   async-messaging are in scope; if so, they need research passes before their
   skills can be authored honestly.
4. **Reversible merges.** The Docker/CI/SEO generic-plus-tech unifications assume
   one dominant implementation each; confirm that's acceptable, given they must
   be split if a second implementation is added later.
5. **`evaluations/` and `audits/` coupling.** Every skill's spec names an
   evaluation requirement; confirm the intent that no skill is promoted to
   `final/` until its eval exists and passes (this wires the taxonomy to the
   repo's existing `evaluations/` and `audits/` directories).
