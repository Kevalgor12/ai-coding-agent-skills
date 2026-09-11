# Matrices

The four lookup tables. Notation per [README](README.md#execution-semantics-model).
All four are projections of the same edge set as the [dependency graph](dependency-graph.md).

---

## Activation matrix

For each skill (grouped): activation **mode** (auto / manual / always),
the primary **trigger**, whether it is **conditional** (only under a condition),
and whether it is **iterative** (runs in a loop). "always" = standing guidance
attached to relevant work, not literally every turn.

### Layer 0 — Orchestration

| Skill | Mode | Primary trigger | Conditional | Iterative |
|---|---|---|---|---|
| skill-router | auto | multi-domain or ambiguous task | — | — |
| capability-adapter | auto | a Tier B/C skill is about to act (barrier) | yes (only if B/C present) | — |
| workflow-composer | auto | multi-stage task | yes (multi-stage only) | — |

### Layer 1 — Discovery

| Skill | Mode | Primary trigger | Conditional | Iterative |
|---|---|---|---|---|
| requirements-engineering | auto | under-specified / high-stakes task | yes | — |
| solution-architecture | auto | new system/feature, open tech choice | yes | — |
| technical-planning | auto | multi-step implementation | yes | — |
| project-management | manual | tracking / release-notes requested | yes | — |

### Layer 2 — Conventions

| Skill | Mode | Primary trigger | Conditional | Iterative |
|---|---|---|---|---|
| git-conventions | auto | commit/branch about to be created | — | — |
| code-commenting | always | writing/editing source | — | — |
| code-quality | always | writing non-trivial code | — | — |
| refactoring | auto | refactor requested / structural debt blocks work | yes | yes (small steps) |
| legacy-modernization | auto | major upgrade / outdated pattern | yes | yes (per increment) |
| technical-documentation | auto | public interface changed / docs requested | yes | — |
| code-review | auto | a change is up for review | — | yes (review loop) |
| git-workflow | auto | branch/merge/rebase/PR op | yes | — |

### Layer 3 — Domain + QA (conditional on the domain being in play)

| Skill group | Mode | Primary trigger | Conditional | Iterative |
|---|---|---|---|---|
| FE-001..005 (frontend/UI/styling/a11y/rendering) | auto | frontend/UI work detected | yes | — |
| BE-001..004 (backend/api/graphql/realtime) | auto | backend/API/realtime work | yes | — |
| authentication-authorization (BE-005) | auto | a trust boundary/auth is involved | yes | — |
| DATA-001..006 (modeling/orm/ops/cache/search/migration) | auto | data-layer work | yes | migration/ops may iterate |
| INFRA-001..003 (container/ci-cd/deploy) | auto | infra/delivery work | yes | — |
| testing-strategy (QA-001) | auto | writing tests / coverage needed | yes | yes (test-fix loop) |
| security-engineering (QA-002) | auto | trust boundary / secret / untrusted input / security review | yes | yes (remediation loop) |
| performance-engineering (QA-003) | auto | perf problem or budget | yes | yes (measure loop) |
| observability (QA-004) | auto | production diagnosability / prod incident | yes | — |
| GROW-001 seo | auto | public web + search visibility matters | yes | — |
| GROW-002 monetization | auto | ad integration | yes | — |
| AI-001 llm-application-engineering | auto | feature calls an LLM | yes | yes (eval loop) |

### Layer 4 — Technology (all conditional on detection)

| Group | Mode | Primary trigger | Conditional | Iterative |
|---|---|---|---|---|
| all 38 SK-TECH-* | auto | that technology detected (manifest/config/imports/file types) **or** named | **yes** (never load if the tech is absent) | inherits parent (e.g. perf/migration loops) |

**Key activation rules (from the spec):** every Layer-3/4 skill is
*conditional* — it must not load when its domain/technology is absent
(context-efficiency rule CE-5). Only `code-commenting` and `code-quality` are
"always" (they attach to any code work). Only Layer-0 orchestration is
unconditional-but-gated (router always considers, but self-suppresses on
single-skill tasks).

---

## Conflict matrix

Pairs that must not co-activate **for the same decision/artifact** (symmetric).
`⊥` = mutually exclusive; resolve by detecting which is actually in use.

| Cluster | Members (⊥ within cluster) | Scope of conflict |
|---|---|---|
| Frontend framework | react ⊥ vue ⊥ angular | one component/app |
| Meta-framework | nextjs ⊥ nuxt | one app |
| SQL engine (OLTP) | postgresql ⊥ mysql | one primary datastore decision |
| OLAP vs OLTP | clickhouse ⊥ (postgresql/mysql) *as the same role* | complementary if different roles |
| SQL ORM | drizzle ⊥ prisma ⊥ typeorm | one data-access layer |
| Document ODM vs SQL ORM | mongoose ⊥ (drizzle/prisma/typeorm) | one datastore family |
| API paradigm | api-design(REST) ⊥ graphql-api-design | per endpoint |
| Component library | mui ⊥ shadcn-ui | one design-system choice |
| Realtime transport | webrtc ⊥ socketio ⊥ websocket-api *for the same channel* | one channel |

Non-conflicts worth stating (commonly *co-exist*, not exclusive):

- `tailwindcss` + `sass` + `web-standards(css)` — can coexist (utility + authored CSS).
- `postgresql` + `redis` — complementary (store + cache), never a conflict.
- `docker` + `github-actions` — complementary (build + pipeline).
- REST + GraphQL in one repo (different endpoints) — not a conflict; only per-endpoint.

**Precedence, not conflict:** `git-conventions` yields to a *detected repository
convention*; that is a precedence rule inside the skill, not a skill-vs-skill
conflict. Similarly a technology skill yields to `skill-router`'s detection of
which sibling is actually in use.

---

## Parallelization matrix

Whether two activations may run concurrently. Rule of thumb, then specifics.

**Serialize when** (any of):
- a **prerequisite** edge connects them (`A → B`);
- they **write the same files / same artifact** (edit conflict);
- one is `capability-adapter` gating the other (barrier);
- a **review loop** requires the build to finish first.

**Parallelize when** all hold: no data dependency, no shared mutable target,
both available under the host's concurrency (sub-agent) support.

| Set | Parallel-safe? | Why |
|---|---|---|
| Review facets (code-review's security ∥ performance ∥ quality ∥ comment checks) | **yes** | all read the same diff, write no shared state |
| Independent module builds (e.g. frontend app ∥ separate backend service) | **yes** | disjoint files |
| Multiple technology *reads/analysis* (e.g. inspect postgres schema ∥ inspect redis usage) | **yes** | read-only |
| Discovery phase (requirements → architecture → planning) | **no** | strict prerequisite chain |
| data-modeling ∥ orm-integration | **no** | orm depends on model |
| implementation ∥ its own tests-for-that-code | **no** (usually) | tests need the code; but test *scaffolding* can be parallel |
| capability-adapter ∥ any Tier B/C skill | **no** | barrier before |
| two skills editing the same file | **no** | edit conflict |
| seo-optimization ∥ web-accessibility (both audit rendered pages) | **yes** | independent audits |
| fan-out over many files (e.g. add a header to N files) | **yes** | disjoint targets |

**Host caveat:** parallelism is *offered*, not guaranteed. Sub-agent support and
history-inheritance vary per agent (capability map §8), and Cursor caps nesting
at one level while Antigravity allows ten. `workflow-composer` requests
parallelism; `capability-adapter` degrades it to sequential where the host can't
deliver it — the workflow's correctness never depends on parallelism, only its
speed.

---

## Escalation matrix

Skill → escalation trigger → target. `↑ human` = requires explicit user approval
(non-overridable, safety-rule-driven). `↑ <skill>` = hand off to another skill.

| Skill | Trigger | Escalates to |
|---|---|---|
| data-migration | destructive migration (data loss) | ↑ human (confirm) |
| git-workflow | force-push / history rewrite / reset --hard | ↑ human (confirm) |
| deployment-release | production deploy / release cut | ↑ human (confirm) |
| project-management, code-review | post to PR / external tracker (outward-facing) | ↑ human (confirm) |
| any skill | accept terms / grant OAuth / enter credentials | ↑ human (per safety rules — prohibited to the agent) |
| solution-architecture | a requirement gap or contradiction surfaces | ↑ requirements-engineering (or human) |
| refactoring | discovers a latent bug | ↑ code-review / bug-fixing (don't silently fix) |
| debugging | root cause identified | ↑ bug-fixing (apply the fix) |
| code-review | security-relevant finding | ↑ security-engineering |
| code-review | performance-relevant finding | ↑ performance-engineering |
| any technology skill | the problem is engine-agnostic | ↑ its Layer-3 parent |
| any Tier B/C skill | required capability absent | ↑ capability-adapter (fallback) then degrade/advise |
| security-engineering | secrets exposed / rotation needed | ↑ human (rotation is outward-facing) |
| llm-application-engineering | needs a live external LLM call with cost/data implications | ↑ human (confirm) |

**Approval gate is a hard stop:** a skill at a `↑ human` gate produces the
proposed action and *waits*; it never performs the gated action to "save a
round-trip." This is the safety-rules contract, above any skill instruction.
