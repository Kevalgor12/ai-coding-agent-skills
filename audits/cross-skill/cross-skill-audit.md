# Audit: Cross-Skill Review (Step 29)

Date: 2026-09-10. Scope: the whole 86-skill library **as a graph and as a
corpus** — the lens the skill-by-skill review of Step 28 structurally could
not apply. Model/effort per the master build plan: Opus, maximum.

This is **Step 29** of `AI_Coding_Agent_Skill_Library_Complete_Step_By_Step.md`.
It covers the plan's 19 named checks. Four companion documents hold the
detail for the checks that deserve their own treatment:

- [`dependency-audit.md`](dependency-audit.md) — checks 3, 4, and the VR-4 tension
- [`routing-audit.md`](routing-audit.md) — checks 7, 15, 16
- [`terminology-audit.md`](terminology-audit.md) — checks 9, 10
- [`context-audit.md`](context-audit.md) — check 8

## What this review did not re-derive

Step 28 (`audits/2026-09-10-individual-skill-review.md` + the seven batch
reports) is treated as established. Its open findings — the `nodejs`
fabricated version numbers, the three approved-but-unauthored skills, the
`redis`/`caching-strategy` and `opensearch`/`search-integration`
duplication, the MUI-vs-shadcn triple, the VR-4 layering tension, the
skill-catalog link artifact, the Tier-A/shell prose contradiction — are
carried forward, not re-found. Where this review adds evidence to one of
them, it says so explicitly. The still-open research gaps tracked in
`core/taxonomy/taxonomy-analysis.md#missing-capabilities` (resilience
patterns, async messaging, IaC-beyond-containers, API consumption) are
deliberate scope boundaries and are **not** counted as defects.

## Mechanical baseline re-verified independently

Before any judgement, every automatable rule was re-run across all 86
skills. All of the following are **clean, 0 violations**: VR-1 (required
fields), VR-2 (`skill.yaml` ↔ `SKILL.md` frontmatter equality, 3-key
frontmatter), VR-5 (`execution_tier` ↔ `required_capabilities`), VR-6
(activation/non-activation disjointness), VR-7 (no two skills share an
identical activation trigger), CE-1 (`description` ≤ 500 chars), CE-2
(every body ≤ 500 lines; max is `redis` at 472). The VR-5 fix from Step 27
and the field fixes from Step 28 both held. The one mechanical rule that
still fails is VR-3, for the reason Step 28 already documented, plus one
case it missed (X-05 below).

**The corpus is in good shape.** Almost everything below is a
*consistency-across-skills* defect rather than a defect inside any one
skill — which is exactly what a cross-skill pass should find, and is
evidence that the per-skill authoring discipline worked.

---

## Findings by severity

| Severity | Count | IDs |
|---|---|---|
| **High** | 6 | X-01, X-02, X-03, X-04, X-05, R-01 |
| **Medium** | 12 | X-06, X-07, X-08, X-09, X-10, X-11, X-12, D-01, R-02, R-03, T-01, T-02 |
| **Low** | 8 | X-13, X-14, X-15, X-16, D-02, R-04, T-03, C-02 |
| **Clean / positive** | 6 | X-17 … X-22 |

Inherited-and-still-open from Step 28 (not re-counted here): 1 Critical
(`nodejs` unsourced version claim), 3 High (unauthored `SK-FE-005` /
`SK-GROW-002` / `SK-TECH-graphql`), 3 Medium (parent↔child duplication ×3,
catalog-link artifact, Tier-A/shell prose contradiction).

---

# Check 1 — Duplicated responsibilities

### X-17 · Metadata-level duplication guard is clean *(positive)*

284 distinct `owned_knowledge` topics are declared across the 86 skills
with **zero exact collisions**, and no two topics were found asserting
ownership of the same concept under different words in the cross-cutting
areas most at risk (caching, indexing, N+1, injection, auth, migration,
testing, tracing). QR-2's machine-checkable half is fully satisfied. The
duplication Step 28 found is prose-level only, and both of its instances
are cases where the *parent* restates content the *child* explicitly owns
— so `owned_knowledge` correctly identifies who should keep it.

### X-06 · Parent-restates-child duplication, quantified — Medium

New evidence for a Step 28 finding, not a new finding. Counting technology
mentions inside each generic skill's body shows three Layer-3 parents
leaning disproportionately on one child:

| Parent | Dominant child | Mentions | Next-highest technology |
|---|---|---|---|
| `caching-strategy` (SK-DATA-004) | `redis` | 21 | Express, 6 |
| `search-integration` (SK-DATA-005) | `opensearch` | 16 | Redis / Elasticsearch, 8 |
| `styling-systems` (SK-FE-003) | `sass` 17 / `shadcn-ui` 16 / `tailwindcss` 15 | 48 combined | MUI, 9 |

`realtime-communication` shows the same shape (Socket.IO 23 vs. WebRTC 9),
which Step 28 did not flag.

**Recommendation (human decision, per the plan's "do not optimize for
fewer skills"):** do **not** merge anything. The child skills' own
`owned_knowledge` already claims these topics; the correct fix is a
one-directional edit to the four parents, replacing the restated
technology specifics with a reference by ID. Explicitly **not** a
restructuring: the parent/child split is doing its job, the parents were
just authored after their children and re-derived material rather than
citing it.

---

# Check 2 — Missing responsibilities

### X-01 · No skill owns debugging or bug-fixing — **High**

The single largest whole-corpus gap, and it is currently **untracked**.

- `core/dependency-architecture/workflows.md` defines 10 canonical
  workflow patterns. **#3 "Bug fixing" and #4 "Debugging" are two of
  them**, and neither has an owning skill. #4's entire diagnostic loop is
  unattributed; #3's "minimal fix" step is unattributed.
- A skill named `bug-fixing` and a skill named `debugging` are referenced
  **by name at 7 sites** across the core design docs — `rules.md` ER-5
  (×2), `matrices.md` escalation matrix (×2), `dependency-graph.md`,
  `workflows.md` (×2). Neither exists in `core/taxonomy/skill-catalog.md`
  or in `skills/`.
- `core/routing-architecture/README.md` lists `debug` as one of the twelve
  user intents the router classifies, and `examples.md` Example 5 selects
  a `⟳ debugging loop { … }` with no skill ID attached to it.
- `taxonomy-analysis.md#missing-capabilities` tracks five gaps
  (resilience, async messaging, IaC, product/project management, API
  consumption). Debugging/bug-fixing is not among them — so unlike every
  other gap in this library, it is neither filled nor disclosed.

This matters more than the count suggests: "fix this bug" and "why is this
broken" are among the most common tasks a coding agent receives, and the
router's completeness backstop (SR-10) cannot staff a stage no skill
covers.

**Recommendation (human decision):** three options, in order of my
preference.
1. **Author `SK-CONV-009 · debugging` (Layer 2).** Root-cause discipline —
   reproduce, hypothesize, instrument, narrow, confirm before fixing — is
   genuinely tech-neutral universal practice, sits naturally beside
   `refactoring` and `code-review`, and would give workflow #4 an owner
   and ER-5 a real target. Bug-*fixing* itself (workflow #3) is thin
   enough to fold in as this skill's hand-off half, or to leave to the
   build skills, since the actual fix is ordinary implementation.
2. **Decide the capability is deliberately out of scope** and add it to
   the missing-capabilities table with that reasoning, then strip the 7
   dangling `bug-fixing`/`debugging` references and re-attribute
   Example 5's loop.
3. Status quo — not recommended; the design docs currently promise a skill
   the library does not have.

### X-05 · A fourth approved-but-unauthored skill: `SK-TECH-vite` — **High**

Step 28 found three unauthored catalog entries by looking at what other
skills reference. `SK-TECH-vite` was missed because **nothing references
it** — which is precisely the failure mode a skill-by-skill review cannot
catch. It is an approved row in the Layer-4 table
(`skill-catalog.md:840`), parented to `INFRA-001, FE-001`, annotated "the
build-tool hub", and backed by a completed research doc
(`research/technologies/vite.md`). It has never been authored.

Full reconciliation of the catalog against `skills/`:

| Catalog ID | Authored? | Referenced from other skills | Status |
|---|---|---|---|
| `SK-FE-005` rendering-strategy | no | 12 files | Step 28, open |
| `SK-GROW-002` web-monetization | no | 2 files | Step 28, open |
| `SK-TECH-graphql` | no | 3 files (Step 28 said 1 — `openapi-swagger` also references it) | Step 28, open + undercounted |
| `SK-TECH-vite` | no | 0 | **new** |
| `SK-TECH-google-seo` | no | 0 | see X-11 |
| `SK-TECH-google-adsense` | no | 0 | see X-11 |

**Recommendation:** fold `SK-TECH-vite` into the same single decision
Step 28 asked for on the other three — author it, or remove the catalog
row and record why. Do not resolve it separately.

### X-07 · LLM vendor breadth is an untracked research gap — Medium

See check 18 (X-09). Listed here too because the missing-capabilities
table is where it belongs.

---

# Check 3 — Circular dependencies

**None.** 9 `depends_on_skills` edges across 5 skills, 0 cycles. Confirmed
independently. Full treatment in [`dependency-audit.md`](dependency-audit.md).

# Check 4 — Dependency explosions

**None in `depends_on_skills`** (max fan-out 4, max fan-in 2). I agree with
the pre-computed finding and did not manufacture one. `related_skills`
fan-out is the more meaningful signal and is assessed in
[`context-audit.md`](context-audit.md); it too is bounded (max 8), but the
routing architecture never states what a router should *do* with the field
— see C-01.

---

# Check 5 — Conflicting instructions

### X-03 · The conflict matrix and `conflicts_with` disagree, in both directions — **High**

`core/dependency-architecture/matrices.md#conflict-matrix` defines 9
mutually-exclusive clusters, and SR-4 makes conflict resolution a
*pre-selection* step. But SR-4's lookup is a prose table in a design doc,
while the machine-readable source a validator or router would actually
read is each skill's `conflicts_with` field. They do not match:

| Matrix cluster | Declared edges | Missing |
|---|---|---|
| Frontend framework (react/vue/angular) | 6/6 | — |
| Meta-framework (nextjs/nuxt) | 2/2 | — |
| SQL engine (postgresql/mysql) | 2/2 | — |
| SQL ORM (drizzle/prisma/typeorm) | 6/6 | — |
| ODM vs. ORM (mongoose ⊥ the three) | 6/6 | — |
| Component library (mui/shadcn-ui) | 2/2 | — |
| **Realtime transport** (socketio/webrtc/websocket-api) | **0/6** | **all** |
| **API paradigm** (api-design/graphql-api-design) | **0/2** | **all** |
| OLAP vs. OLTP (clickhouse ⊥ postgresql/mysql) | 2/6 | 4 — defensible, the matrix qualifies it "*as the same role*" |

Six of nine clusters are declared perfectly and symmetrically, which makes
the two zero-coverage clusters look like omissions rather than design.
Consequence: a "add realtime chat" task can co-activate three mutually
exclusive transports with nothing in the metadata to stop it — exactly the
over-activation the router exists to prevent.

The drift runs the other way too: the skills declare two clusters the
matrix does not contain — **runtime/language** (`go ⊥ nodejs ⊥ python`, 6
edges) and **Node framework** (`express ⊥ fastify`, 2 edges).

**Recommendation:** narrow and mechanical, but I did not apply it, because
adding `conflicts_with` edges changes routing behavior and the OLAP row
needs a judgement call on whether "same role" is expressible as a static
edge at all. Add the 8 missing realtime + API-paradigm edges to the
skills; add the runtime and Node-framework clusters to the matrix; then
make the matrix a *projection* of `conflicts_with` (as `matrices.md:4`
already claims it is — "All four are projections of the same edge set")
rather than an independently-maintained table.

### X-08 · `activation_mode` contradiction on the two mandated skills — Medium

`matrices.md` line 37-38 lists `code-commenting` and `code-quality` with
mode **`always`**, and its own key states "Only `code-commenting` and
`code-quality` are 'always'". Both skills declare
`activation_mode: auto` in `skill.yaml`. Every other mode claim in the
matrix matches (`project-management: manual` ✓, all Layer-0 `auto` ✓).

This lands on precisely the two skills `taxonomy-analysis.md` rules
first-class and mandated, and the difference is behavioral: `always` means
standing guidance attached to all code work, `auto` means model-triggered
per task. The spec (§2.3) defines all three values, so this is a real
either/or, not a naming quibble.

**Recommendation:** a ruling, not a patch — decide whether these two are
standing or triggered, then align the other artifact. My read is that
`always` matches the mandate ("attach to every code-producing skill") and
`auto` is the safer portability choice (not every host supports standing
skills); if `auto` wins, the matrix's claim and its key both need
rewriting, which is why I left it alone.

---

# Check 6 — Contradictory recommendations

### X-18 · No cross-skill factual contradictions found *(positive)*

Two independent passes:

- **Metadata.** Only 3 components appear in more than one skill's
  `covered_versions` (`postgresql`, `react`, `typescript`). All 3 are
  compatibility-floor statements from a dependent skill (e.g. `mui`'s
  "React 17/18/19+, `react-is` pinning required below 19") sitting
  alongside the owning skill's coverage range — complementary, not
  competing.
- **Prose.** Scanning every skill body for "current/latest/stable/LTS/as
  of" claims about a technology owned by a *different* skill returned no
  competing assertion. Where a skill needs a version fact it does not own,
  it defers (e.g. `legacy-modernization` on Angular's per-major floors,
  `fastify` explicitly refusing to state an unverified v6 Node floor).

The corpus is disciplined here. The only known factual defect remains
`nodejs`'s unsourced type-stripping version numbers (Step 28, Critical,
open).

---

# Check 7 — Routing ambiguity

Four genuine unresolved activation overlaps, plus the router's dependence
on catalog IDs that do not exist. Full treatment in
[`routing-audit.md`](routing-audit.md) (R-01 … R-06).

# Check 8 — Excessive context loading

Bounded in practice, with one specification gap (`related_skills` has no
routing rule) and one undocumented scaling ceiling (Tier-0 selection
already costs ~9.6K tokens). Full treatment in
[`context-audit.md`](context-audit.md) (C-01 … C-04).

# Checks 9 & 10 — Inconsistent terminology and outputs

Three real inconsistencies, one of which blocks a `[V]`-marked spec rule
from ever being validated. Full treatment in
[`terminology-audit.md`](terminology-audit.md) (T-01 … T-05).

---

# Check 11 — Inconsistent security requirements

### X-10 · Two security dimensions are stated by some database skills and omitted by comparable ones — Medium

Step 28 found one instance (`mysql` missing what `postgresql` states).
Reading all six database-family Layer-4 skills' `## Security` sections
side by side turns that into a matrix with two systematic gaps:

| Dimension | postgresql | mysql | mongodb | clickhouse | redis | opensearch |
|---|---|---|---|---|---|---|
| Authn mechanisms | ✅ | ✅ | ✅ | ⚠️ marked Unresolved | ✅ | ✅ |
| Authz / RBAC | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Row/field-level controls | ✅ RLS | ✅ states no equivalent | ✅ CSFLE/QE | ✅ Row Policies | n/a | ✅ DLS/FLS |
| **Injection / parameterization** | ✅ | ❌ | ✅ | ❌ | n/a | n/a |
| **Transport / TLS** | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| Encryption at rest | ❌ | ✅ | ✅ | partial | ❌ | ❌ |
| Audit logging | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |
| Defers depth to `SK-QA-002` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |

- **Injection/parameterization**: `postgresql` opens with "Parameterize all
  queries"; `mongodb` covers BSON injection and `$where`. `mysql` — the
  archetypal SQL-injection target — says nothing, and neither does
  `clickhouse`. Confirms and extends Step 28.
- **Transport/TLS**: `postgresql` (`ssl = on`, key `chmod 0600`,
  `clientcert=verify-full`), `mongodb`, and `opensearch` (two-layer TLS,
  cert file modes, the demo-certificate warning) all cover it. `mysql`,
  `clickhouse`, and `redis` do not — all three are network services with
  documented TLS support.
- **QR-2 deferral sentence**: present in four of six; `redis` and
  `opensearch` never point at `SK-QA-002` at all.

Encryption-at-rest and audit-logging asymmetries are *not* flagged as
defects — those genuinely differ per engine and each skill states what its
own docs state.

**Recommendation:** these are additive, sourced, single-paragraph
additions, but each requires reading the vendor's current docs to get
right (SG-2/SG-3 forbid asserting an unsourced config flag), so they are
authoring work, not an audit fix. Suggest a short follow-up pass with a
fixed six-dimension checklist so the *next* database skill can't drift.

### X-11 · `data-migration` has no Security section at all — Medium

It is the only Layer-3 DATA skill without one, and it is the skill that
touches populated production data: backfills over user records, `DROP` and
destructive `ALTER`, data transforms. §3.2 makes Security conditionally
required "when the skill touches a trust boundary/secret/untrusted input";
a backfill over a table of personal data plausibly qualifies. It also
references **neither** `SK-QA-002`, **nor** `SK-QA-001`, **nor**
`SK-CONV-007` anywhere in either file — the only edit-producing skill in
the library with none of the three.

Its `## Escalation` and destructive-operation discipline are excellent, so
this is a gap in cross-cutting linkage, not in care.

---

# Check 12 — Inconsistent testing requirements

### X-12 · `data-migration` produces runnable code and has no Testing section — Medium

Its declared outputs are `edit: migration-script` + `analysis:
rollout-plan`, and its body says it produces "a reversible migration
script (up/down)". §3.2 item 11 makes Testing required "when the skill
produces runnable code". Its `## Outputs & verification` verifies that "a
working rollback path exists" — an existence check, never an execution
check. Meanwhile `routing-architecture/examples.md` Example 4 explicitly
staffs "testing-strategy (migration up/down tests)" for exactly this
skill's workflow, and every comparable skill (`orm-integration`,
`database-operations`, `prisma`, `drizzle`, `typeorm`, `mongoose`) has a
Testing section.

**Recommendation:** add a Testing section covering the one thing that
distinguishes migration testing from ordinary testing — exercising the
`down` path against a copy of production-shaped data before the `up` path
is trusted — and reference `SK-QA-001` for surrounding discipline. Narrow
and safe, but it is new content, so flagged rather than written.

### X-13 · Testing-reference coverage otherwise consistent — Low

16 of 61 edit-producing skills never reference `SK-QA-001`. Reviewed
individually, 15 are legitimate: `git-workflow` and
`technical-documentation` produce no runnable code; `husky`,
`github-actions`, `grafana`, `prometheus` produce configuration whose
testing is the pipeline's concern; `code-commenting`/`code-quality` are
review lenses. `typescript` and `web-standards` are borderline (both
produce runnable code) but both are language/platform skills whose testing
belongs to the runner skills. Only `data-migration` (X-12) is a defect.

---

# Check 13 — Framework-specific leakage into generic skills

### X-19 · Generic skills present balanced alternatives, with three exceptions *(mostly positive)*

Counting technology mentions in every Layer-0-to-3 body: the dominant
pattern is a *balanced alternative set*, which is a decision framework
(QR-3-compliant) rather than leakage — `frontend-architecture`
(React 21 / Vue 14 / Angular 12 / Next 10 / Nuxt 8), `orm-integration`
(Prisma 17 / Drizzle 15 / TypeORM 13 / Mongoose 9), `backend-architecture`
(Express 18 / Fastify 16 / Node 5 / Go 5 / Python 5), `data-modeling`
(Mongo 8 / ClickHouse 8 / Postgres 6 / MySQL 4). No Layer-0-to-3 skill
quietly assumes a framework the way the check anticipated.

### X-14 · Three unified generic skills carry their unification silently — Medium

`taxonomy-analysis.md#skills-to-merge` deliberately unified
containerization↔Docker, ci-cd↔GitHub Actions, and seo↔Google, each with
an explicit reversal condition: "If the library later adds a second
implementation (e.g. GitLab CI, Podman), split the generic skill back out
then — noted so the merge is reversible by design."

**None of the three skill bodies states that condition, or acknowledges an
alternative implementation exists.** `containerization` mentions Docker 12
times and Podman/OCI/buildah zero times. `ci-cd-pipeline` is the best of
the three (GitHub Actions 3, plus AWS/Azure/GCP). The governance is real
but lives only in a design document a reader of the skill will never open.

`caching-strategy` (Redis 21 vs. next-highest 6) and
`realtime-communication` (Socket.IO 23 vs. WebRTC 9) show the same tilt
without even a declared unification — see X-06.

**Recommendation:** one sentence in each of the three unified skills'
Purpose & scope naming the unification and its reversal condition. This is
the cheapest possible fix for the library's most-stated principle, but it
is content authoring in five files, so recommended rather than applied.

---

# Check 14 — Generic assumptions inside technology skills

### X-20 · Clean — the inverse direction is well-disciplined *(positive)*

Scanning all 40 Layer-4 bodies for phrases naming method owned by a
Layer-3 parent (test-pyramid selection, measure-before-optimizing, threat
modeling, expand/contract, cache invalidation, N+1 method, normalization,
design tokens) and reading the hits in context: essentially every hit is a
**deferral sentence**, not a restatement. Representative:

- `prisma`: "Generic ORM method (N+1 avoidance, transaction handling, when
  to choose Prisma over another ORM) is owned by orm-integration;
  migration *safety* mechanics (expand/contract, backfill batching,
  rollback discipline) are owned by data-migration."
- `typeorm`: "…migration safety mechanics (expand/contract, backfill
  batching) are data-migration's. This skill supplies TypeORM's concrete,
  version-correct specifics on top of both."

All four ORM skills, and every database skill except `redis`/`opensearch`
(see X-10), carry an explicit `SK-QA-002` deferral. **The duplication in
this corpus runs parent→child, never child→parent** — the opposite of what
§2.5's documented historical incident warned about, which suggests that
lesson was internalized and the newer risk is authoring order.

---

# Check 15 — Missing escalation paths

### X-04 · 27 skills carry an escalation gate in the body and declare none in metadata — **High**

Every one of the 86 skills has a `## Escalation` body section. **27 have
an empty or absent `escalation` field in `skill.yaml`.** Zero have the
inverse problem. That one-directional pattern means this is a single
authoring-convention drift, not 27 independent oversights.

It matters because of two rules that interact:

- **ER-1** (`rules.md`): "The routing plan names every approval gate the
  task will hit *before* work starts, so the user isn't surprised
  mid-run."
- **CS-1** (`rules.md`): "Route on Tier-0 only. Selection uses `name` +
  `description` + activation/non-activation. **Never load a skill body**
  to decide whether to select it."

A gate that exists only in the body cannot be surfaced before the body
loads. **ER-1 is unimplementable for these 27 skills**, and the list is
not benign:

| Skill | Body escalation content | In the escalation matrix? |
|---|---|---|
| `deployment-release` | "Any production-affecting deployment action is guarded behind explicit confirmation — this is not optional"; blue-green/rolling change needs confirmation | **Yes** — `↑ human (confirm)` |
| `database-operations` | isolation-level or pool-resize change on a production DB needs confirmation | no |
| `ci-cd-pipeline` | pipeline change affecting production deployment needs confirmation | no |
| `containerization` | rootless-mode change on a production image needs confirmation | no |
| `caching-strategy`, `performance-engineering`, `backend-architecture`, `realtime-communication`, `search-integration`, `testing-strategy`, `frontend-architecture`, `styling-systems`, `ui-ux-design`, + 15 Layer-4 skills | varies | no |

`deployment-release` is the sharpest case: `matrices.md` names it as a
`↑ human` production gate, its body enforces one emphatically, and the
field the router reads is empty.

**Recommendation:** this is the closest thing in this audit to a
mechanical fix — mirroring existing body prose into the `escalation`
field, exactly as `failure_handling` already mirrors its section. I still
did **not** apply it, for two reasons: (1) 27 files is a mass edit, which
is how the parallel-edit risk Step 28 called out gets reintroduced; and
(2) the deeper question is whether the spec should make `escalation`
**required** rather than optional whenever the body has the section — a
spec change, not a content change. Recommend deciding the spec question
first, then sweeping all 27 in one pass with a validator behind it.

Further treatment (including which escalations *should* exist but do not,
in either place) is in [`routing-audit.md`](routing-audit.md).

---

# Check 16 — Missing review loops

Treated in [`routing-audit.md`](routing-audit.md) (R-04). Summary: the
review loop is architecturally real (ER-6, every workflow's `code-review
⤾`) but has **no Tier-0 representation** — `code-review`'s activation
conditions contain no signal that fires on completion of a build step in
the same run, and the router is required to route on Tier-0 only.

---

# Check 17 — Weak failure recovery

### X-21 · Clean, and notably strong *(positive)*

Every one of the 86 skills declares ≥2 `failure_handling` rules (mean 2.6,
max 5). No rule anywhere is a bare "ask the user"; no rule is under 70
characters; no skill's rule set consists solely of asking. The dominant
pattern is the capability-aware one the spec asks for — "degrade to
advisory and say so" appears in 23 skills, "advisory output" in 4 more —
and the second is a genuine domain-specific recovery (e.g.
`data-migration`: "If shell/migration-tool execution isn't available,
produce the migration script and rollout plan as advisory output, clearly
marked as not executed"). This check found nothing to report, which for a
corpus of 86 independently-authored skills is itself the finding.

---

# Check 18 — Vendor lock-in

### X-09 · The AI/LLM domain is a two-vendor duopoly with no acknowledged alternatives — Medium

Across **all eight** AI skills (`SK-AI-001` … `SK-AI-008`), a full-text
scan returns:

- Mentions of Anthropic: 62. Mentions of OpenAI: 60.
- Mentions of **any other provider** (Google/Gemini, Meta/Llama, Mistral,
  Cohere, Azure OpenAI, Bedrock, Vertex): **0**.
- Mentions of **open-weight or self-hosted deployment** (Llama, Mistral,
  Ollama, vLLM, "open-weight", "self-host", Hugging Face): **0**. (The
  single "self-hosted" hit in `agent-architecture` refers to a sandbox,
  not a model.)
- Mentions of **data residency, sovereignty, on-prem, or compliance** as a
  selection axis: **0**.

This lands hardest on `SK-AI-006 model-selection`, which
`skill-catalog.md:660` designates as "itself the vendor-neutral decision
layer." The skill is genuinely careful — it frames both vendors' lineups
as "worked examples of the method… snapshotted 2026-09-10… should be
re-verified", warns against calcifying model names, and its anti-patterns
lead with "treating this skill's specific tier names/prices as evergreen."
But its decision framework's step 2 is "**Start from the vendor's own
documented default tier**", which presupposes a hosted commercial API
vendor with a published tier lineup. Its four axes are capability, cost,
latency, and context window; for a large share of real selections the
binding constraint is a fifth axis — where the data is allowed to go —
and neither the framework nor the workflow has a branch for it.

This is **not** a fabrication problem, and the fix is not to invent Gemini
or Llama facts (SG-3 forbids exactly that). It is a *disclosure* problem:
the library discloses every other grounding limitation it has
(`observability` on resilience patterns, `realtime-communication` on
message brokers, `web-accessibility` on WCAG conformance depth,
`search-integration` on RAG) and this one it does not.

**Recommendation:**
1. Add "LLM providers beyond Anthropic/OpenAI; open-weight and
   self-hosted model deployment" to
   `taxonomy-analysis.md#missing-capabilities` as a tracked research gap,
   in the same form as the resilience and async-messaging entries.
2. Add a non-activation condition to `model-selection` in the house style
   — something equivalent to "selection among open-weight/self-hosted
   models, or a choice driven primarily by data-residency/compliance
   constraints — not grounded in this library's research, state the gap
   rather than extrapolating from hosted-API guidance."
3. Do **not** add unsourced facts about other providers.

### X-15 · Non-AI vendor assumptions are governed but silent — Low

Covered in X-14: Docker, GitHub Actions, and Google are declared
unifications with documented reversal conditions, so this is disclosure,
not lock-in. `deployment-release` names Vercel/AWS/Azure once each without
privileging any. No other vendor-neutrality violation found.

---

# Check 19 — Versioning problems

### X-02 · 50 stale "not yet authored" markers across 15 skills, 16 of them in routing metadata — **High**

Step 28 identified this pattern and fixed it in six technology skills. A
full-corpus classification shows the sweep was incomplete, and that it
missed the highest-impact field.

Classifying all 74 "not yet authored / once authored / forward reference"
sites by whether the referenced skill now exists:

| Class | Sites | Skills |
|---|---|---|
| **Stale** — the referenced skill *is* authored, the marker is false | **50** | 15 |
| Accurate — genuinely unauthored (`SK-FE-005`) | 13 | 6 |
| No resolvable target | 11 | 9 |

The 15 affected skills: `api-design`, `code-commenting`, `containerization`,
`data-migration`, `data-modeling`, `deployment-release`, `docker`,
`frontend-architecture`, `mui`, `nextjs`, `redis`, `sass`,
`search-integration`, `tailwindcss`, `web-standards`.

Three reasons this is High rather than cosmetic:

1. **16 of the 50 sit in `non_activation_conditions`** — the Tier-0 field
   CS-1 makes the *only* thing the router reads when deciding. A router
   reading `data-modeling`'s "route to database-operations, **not yet
   authored**" has been told its own routing target does not exist.
2. **One actively misroutes.** `search-integration`'s non-activation says
   the RAG/LLM layer on top of vector search is "a documented research gap
   in this library, not answered here." `SK-AI-005 rag-engineering` was
   authored on 2026-09-10 and owns exactly that. A user asking about RAG
   over their search index gets told the library has nothing, when it has
   a dedicated skill.
3. **One is inverted.** `deployment-release/SKILL.md:80` calls
   `SK-CONV-001` git-conventions "not yet authored" — git-conventions was
   the *first* skill in the build order (`taxonomy-analysis.md:78`). That
   marker was never true.

Also: `fastify`'s non-activation routes to "Express's [skill] when
authored"; `express` has been authored since.

**Recommendation:** a single mechanical sweep, and I deliberately did not
run it despite it being tempting — 50 edit sites across 15 skills is a
mass parallel edit, three of the fixes (X-02.2 above, `redis`'s three
`parents` comments, `docker`'s `parents` comment) require a judgement call
about what the corrected sentence should say rather than just deleting a
clause, and this step's mandate is surfacing architectural findings. What
*should* accompany the sweep is a repo-level guard: this is the second
consecutive audit to find the same class, because nothing re-checks
forward references when a skill lands.

### T-01 · Three competing version-tag syntaxes — Medium

VA-2 is marked `[V]` (mechanically validatable) and requires every
version-specific claim to be tagged. The spec never fixes the marker's
form, and the corpus has three, with **7 skills mixing two inside one
file**. Full detail in [`terminology-audit.md`](terminology-audit.md).

### X-16 · Stale skill counts in four design documents — Low

`dependency-graph.md:3` and `taxonomy-analysis.md` (×2) say **69 skills**;
`state-and-contract.md` (×2) and `self-review.md` (×4) say **83 skills**.
The library has **86**. The 69 is the design-time proposal (defensible in
`taxonomy-analysis.md`, less so stated flatly in `dependency-graph.md`);
the 83 is a snapshot from two steps ago. `examples.md:118` says "all 68
other skills". Cosmetic, but it is the sort of drift that makes a reader
distrust the counts that *do* matter.

### X-22 · Two stale READMEs flagged by the orchestrator self-review are now fixed *(positive)*

`self-review.md` Part 3 flagged `evaluations/README.md` ("Empty for now")
and `core/README.md` ("Empty for now"). Both have since been updated. Noted
so a future reviewer doesn't re-open them.

---

# Cross-cutting observation: the catalog is drifting from the library

Three findings above (X-01, X-05, X-03) and two in the routing audit
(R-01, R-02) share one root cause worth naming separately, because fixing
the symptoms individually will not fix it.

`core/taxonomy/skill-catalog.md` is the normative source the routing docs
cite ("Skill IDs per the taxonomy"), and it has diverged from `skills/` in
four ways at once:

1. **Count.** The catalog enumerates 92 entries (48 generic + 44
   technology rows). `taxonomy-analysis.md` says 69 proposed (31 + 38).
   86 are authored. Three totals, three documents, no reconciliation.
2. **Composition.** Six catalog IDs have no skill (X-05). Two of them
   (`SK-TECH-google-seo`, `SK-TECH-google-adsense`) appear as Layer-4
   *rows* while the merge table in the same taxonomy declares them
   unified into `SK-GROW-001`/`SK-GROW-002` — the catalog contradicts its
   own analysis document. Meanwhile `SK-TECH-docker` and
   `SK-TECH-github-actions` carry the identical "unified" annotation and
   *were* authored as separate skills. The unification decision was
   applied inconsistently, and the catalog records both outcomes as if
   they were the same.
3. **Vocabulary.** The catalog's per-skill `Dependencies:` field predates
   the dependency architecture and conflates four relationship types in
   one prose blob — hard composition, specialization (`parents`),
   "related", and abstract agent capability. Spec §2.5 now warns at
   unusual length that these MUST NOT be conflated, citing an incident
   where 7 of 9 technology skills got it wrong in a single batch. The
   catalog still speaks the pre-distinction language, which is a plausible
   root cause of that very incident.
4. **Content.** Catalog entries state responsibilities and evaluation
   requirements the authored skill does not visibly satisfy — e.g.
   `SK-QA-004`'s catalog eval requirement is "Produces structured logs
   with correlation IDs and metrics tied to stated SLOs", and the authored
   `observability` body never uses the phrases "structured logging" or
   "correlation ID" and mentions SLO once.

**Recommendation (the most architecturally significant in this audit):**
decide what the catalog *is*, now that 86 skills exist. Two coherent
answers:

- **(A) The catalog is a historical design record.** Freeze it, stamp it
  as design-time, and move the normative per-skill contract entirely into
  `skills/*/skill.yaml` + the spec. Update the routing docs to cite the
  skills, not the catalog. Cheapest, and honest.
- **(B) The catalog stays normative.** Then it must be reconciled: one
  authoritative count, no IDs without skills, the `Dependencies:` field
  split into the four fields the spec defines, and the eval requirements
  re-checked against what was actually authored. Expensive but keeps a
  single readable whole-library view — which has real value and is why
  this audit could be done at all.

I recommend **(A)**, with the whole-library view preserved by generating
an index from `skill.yaml` rather than hand-maintaining prose. But this is
squarely a human architectural decision and the plan's instruction is to
recommend, not restructure.

---

## What I fixed

**Nothing.** No file outside `audits/cross-skill/` was modified. Several
findings (X-02's 50 stale markers, X-04's 27 empty escalation fields,
X-03's 8 missing conflict edges) are individually narrow and mechanical,
but each is a mass edit whose correct form depends on a decision this step
is not authorized to make — and this step's stated purpose is surfacing
architectural findings for a human, with an explicitly higher bar for
direct fixes than Step 28 had.

## Limitations of this review

- I read `skill-catalog.md` in full and every core design document in
  full, but sampled skill bodies rather than reading all 86 — full bodies
  read for the AI cluster's decision layer, all six database skills'
  Security sections, `data-migration`, `observability`, and targeted
  sections elsewhere. Mechanical extraction (YAML across all 86, full-text
  regex across all 172 files) covered the rest, which is sound for
  structural claims and weaker for "is this paragraph good."
- Claims about routing *behavior* are claims about a specification. As
  `core/orchestrator/self-review.md` R-1 states plainly, nothing here is
  enforced by a runtime; there is no validator and `evaluations/` is a
  placeholder. Every routing finding is therefore "the written rules are
  inconsistent," not "the system behaves incorrectly" — the system has
  never run.
- I did not evaluate technology accuracy. Step 28 did that per-skill and
  found it uniformly strong; re-sampling it here would have duplicated
  work at the expense of the graph-level analysis only this step can do.
