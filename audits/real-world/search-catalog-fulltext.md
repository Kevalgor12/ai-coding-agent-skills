# Real-World Evaluation — Search / full-text over a product catalog

**Step 32** of the master build plan. Date: 2026-09-11. Domain: Search.
Adversarial pattern: **none** — this is the clean-baseline task, evaluated
normally. Its purpose is a maintainability / over-engineering stress test
(dimension 7) on `search-integration`, which has not been probed this way
before.

**Method and caveats** as stated in
[`infrastructure-legacy-deploy.md`](infrastructure-legacy-deploy.md): worked as
the orchestrator in `core/orchestrator/`, routing per
`core/routing-architecture/`, reading actual skill files. Severity is this
project's Critical/High/Medium/Low audit convention. Step 28 and Step 29
findings are cited, not re-derived.

---

## The task

> "Add full-text search to our product catalog so users can search by product
> name and description."

**Repository signals:** a PostgreSQL-backed catalog (`postgres://` connection
string / `pg`-family driver present). A `products` table with `name` and
`description` columns, already populated. **No existing search infrastructure**
of any kind — no OpenSearch/Elasticsearch client, no `redis` search usage, no
vector store. Data and query scale are **not stated** anywhere in the request or
inferable from the manifest.

---

## Trace

### P0 — Intake

- **Intent**: `build` (add a capability). **Task type**: workflow pattern
  **#2 Feature development** (`workflows.md:38-53`).
- **Complexity**: `multi-step` — an engine decision, a schema change on a
  populated table, a query surface, and verification.
- **Risk class** (D3): `reversible-write`. Nothing destructive, outward-facing,
  or production-affecting is inherent to the task; the schema change is additive
  and revertible.
- **S-Gate 1** (`security-and-validation.md:64`): **yes** — a user-supplied
  search term is untrusted input crossing into a query. This is what admits
  `SK-QA-002` under SR-5.
- **D13 / P4**: plan confirmation is **not** required (neither `destructive`,
  `outward-facing`, `production`, nor `project` complexity). Proportionality
  (`README.md` principle 1) applies; asking for plan approval here would be
  friction, not safety. Correct.

### P1 — Discovery

Domains: DATA (search, modeling, migration), BE (the query surface), QA
(security, testing), TECH (postgresql, plus whatever ORM is present).

**Conflict clusters (D4).** The SQL-engine cluster resolves cleanly —
`postgres://` detected, so `mysql`/`mongodb`/`clickhouse` are out (SR-4). The
**ORM cluster is undetected**: the signals say "PostgreSQL-backed" without
naming Prisma / Drizzle / TypeORM. `skill-router`'s own failure-handling
(`skill.yaml:101`; `SKILL.md:205-207`) is the correct response — "activate the
generic Layer-3 skill and raise the choice as a decision rather than activating
every sibling" — backed by its anti-pattern "Speculative breadth"
(`SKILL.md:164`). A compliant run therefore activates `orm-integration` at most,
not four ORM skills. **This is the router's design working, and it works here.**

### P2 — Routing

**Selected:**

| Skill | Fires on |
|---|---|
| `SK-DATA-005` search-integration | activation 1 + 2 (`skill.yaml:36-37`) — "A feature needs full-text search…"; "The search-engine choice is open (database-native FTS vs. dedicated engine vs. vector search)". Verbatim match on both. |
| `SK-TECH-postgresql` | activation 1 (`skill.yaml:30`) — a `postgres://` string or PG driver present; also activation 3 (`:32`), which names `tsvector` explicitly as a PG-specific feature |
| `SK-DATA-006` data-migration | activation 1 (`skill.yaml`) — "A schema change is needed on a database that already has data". **Late-bound — see RWS-02.** |
| `SK-QA-002` security-engineering | activation 1 — untrusted input into a query (S-Gate 1) |
| `SK-QA-001` testing-strategy | runnable code produced (SR-5), T-Gate 1 |
| `SK-BE-002` api-design | a search endpoint's contract (query param, pagination, response shape) is being added |

**Correctly excluded — the over-activation candidates:**

- **`SK-TECH-opensearch`** — SR-3 is decisive. No OpenSearch signal exists in
  the repo and the request names no engine, so it is **not detection-eligible**.
  It cannot be activated regardless of how the decision lands, and if the
  decision landed on a dedicated engine it would enter via replan (R5), not at
  routing time. *The single most important exclusion in this task, and the
  mechanism that produces it is structural rather than judgemental.*
- `SK-TECH-redis` — no Redis signal; and `search-integration`'s own knowledge
  frames Redis's search role as one of three options, not a default.
- `SK-AI-001` / `SK-AI-005` — no LLM or RAG dimension. Note both are in
  `search-integration`'s `related_skills` (`skill.yaml:67`); per
  `context-audit.md`'s proposed **CS-9**, being listed as related is not a
  reason to load. The absence of CS-9 as a written rule (C-01) is the only thing
  standing between this task and ~36K tokens of AI bodies; here the default-deny
  rule (SR-1) carries it, as C-01 predicted it would.
- `SK-DATA-004` caching-strategy — no caching concern stated.

### P3 — Resolution

Prerequisite ordering (`dependency-graph.md:75-77`): `data-modeling →
data-migration`, `data-modeling → database-operations`. The composed shape:

```
SK-DATA-005 (engine decision)
  → [cond, DB-native branch] SK-DATA-006 (tsvector column + GIN index migration)
  → SK-TECH-postgresql (index type, query construction)  ∥  SK-QA-002 (untrusted term)
  → SK-BE-002 (endpoint contract)
  → SK-QA-001 (⟳ test-fix)
  → code-review ⤾ (security facet mandatory, S-Gate 4)
```

`SK-QA-002` runs parallel to the query-construction step per PR-2 (both read the
same design; no shared mutable target) — the same shape S07's expected-behaviors
already uses for the analogous pairing.

### P5 — The decision itself

`search-integration`'s body loads (CS-2) and its Decision framework step 1
executes:

> "**Does a database already in use (PostgreSQL, Redis) already cover the
> need?** If the requirement is full-text search at moderate scale with no need
> for a separate cluster, DB-native FTS avoids the sync-drift risk and an
> entirely new operational surface — **don't reach for a dedicated engine by
> default**." — `SKILL.md:80-84`

It hands off to `postgresql`, whose Decision framework step 4 says the same
thing from the engine side:

> "`tsvector`/`tsquery` + GIN covers moderate full-text needs without operating a
> second system. Escalate to a dedicated engine (`SK-DATA-005`) only once
> relevance-tuning or scale requirements exceed what GIN-backed FTS documents
> supporting — **don't add a search engine 'in case.'**" — `postgresql/SKILL.md:129-133`

**Verdict on the assigned question: the library defaults correctly to
PostgreSQL FTS and does not over-engineer.** See "What works" below for the full
count of independent guards. The defects found are elsewhere.

---

## Findings

### RWS-01 · The DB-native branch's own new risk — a schema change on a populated table — has no declared handoff, while the branch the skill argues against has five — **High**

**Finding.** `search-integration` is thorough about the failure mode introduced
by the option it recommends **against**, and silent about the one introduced by
the option it recommends **for**.

Index-sync drift (the dedicated-engine branch's risk) is staffed in five
separate places:

| Site | Content |
|---|---|
| `SKILL.md:69-76` | Knowledge — "the structural risk unique to a dedicated search engine that DB-native FTS doesn't have" |
| `SKILL.md:94-97` | Decision framework step 4 — design the sync strategy *before* implementation |
| `SKILL.md:124-126` | Engineering rule 2 |
| `SKILL.md:153-155` | Anti-pattern 2 — "the single most common way a dedicated-engine search index silently goes stale" |
| `skill.yaml:99` | `verification` item 1 |

Choosing DB-native FTS on **this** repo introduces its own specific, real risk:
adding a `tsvector` column (or a generated column) and a GIN index to an
**already-populated** `products` table is a schema change plus a backfill plus
an index build. That is `data-migration`'s entire domain. It is staffed in
**zero** places:

- `search-integration`'s Workflow (`SKILL.md:103-118`) — step 3 designs the
  index/analyzer/mapping structure and step 4 designs sync *only* "if a
  dedicated engine or vector store is chosen"; the DB-native branch goes
  straight from step 3 to step 7's handoff.
- `related_skills` (`skill.yaml:67`) = `[SK-DATA-001, SK-TECH-postgresql,
  SK-TECH-redis, SK-AI-001, SK-AI-005]` — **`SK-DATA-006` is absent**, while two
  AI skills that have nothing to do with this task are present.
- `outputs` (`skill.yaml:58-64`) are two `analysis` artifacts. No migration
  artifact is declared, so D11 ("what does each stage hand to the next?") has
  nothing to bind.

**Why this is more than a missing cross-reference.** `data-migration`'s
activation condition 1 ("A schema change is needed on a database that already
has data") is only *knowable* after `search-integration`'s decision framework
picks the DB-native branch — which happens at **P5**, not at P2 routing time.
That makes it a late-bound conditional (D14, `lifecycle.md:221-224`) requiring an
`F6` (plan-invalid) → `R5` (replan) transition
(`failure-recovery-and-escalation.md:80`). The architecture supports this
exactly; what is missing is anything that would *prompt* it. A run that never
notices the schema-change dimension produces a design, not a defect it can
detect — which is the worst class of miss, because the completeness backstop
(SR-10) only re-walks the *chosen workflow's* stages, and "migration" is not a
stage of workflow #2.

**Root cause.** The skill was authored around its own most interesting insight
(index-sync drift is the dedicated engine's unique cost) and the DB-native
branch was framed as the *absence* of that cost rather than as an option with
costs of its own.

**Recommended correction.** Two narrow edits to `search-integration`:

1. add `SK-DATA-006` to `related_skills`;
2. add a Workflow step mirroring step 4's shape: *"If the DB-native branch is
   chosen and the source table is already populated, the index/column addition
   is a schema change on live data — hand off to `SK-DATA-006` for
   expand/contract sequencing, backfill batching, and the rollback path. The
   DB-native branch avoids sync drift; it does not avoid migration risk."*

**Regression test requirement.** **New scenario required.** Verified against
`evaluations/scenarios/`: `SK-DATA-005` appears in three scenarios (S05, S06,
S07) and in **all three it is a required *exclusion***. No scenario anywhere
exercises it as a positive activation, so its decision framework has never been
scored. Proposed **`S18 — full-text search over a populated product catalog`**,
category **Multi-skill tasks** (it spans DATA + BE + QA and exercises sequencing),
with this as a `critical` assertion: when the DB-native branch is chosen, the
plan contains a migration stage with a declared rollback path before the index
is created — a run that emits `CREATE INDEX` with no migration stage fails the
scenario.

---

### RWS-02 · `CREATE INDEX CONCURRENTLY` appears nowhere in the corpus — **High**

**Finding.** `grep -i "CONCURRENTLY\|ACCESS EXCLUSIVE"` across `skills/` returns
**zero** hits. For this task — the most common way anyone adds Postgres FTS to a
live catalog — that is a production-affecting omission.

- `data-migration` owns the right *general* discipline and states it well:
  "Large backfills must be batched" (`SKILL.md:47-50`), engineering rule
  (`:109`), anti-pattern "Single-transaction backfill on a large populated
  table — locks the table" (`:127`), `verification` (`skill.yaml:83`). But every
  one of these is framed for **DML** — `UPDATE`-every-row. A `CREATE INDEX` is
  **DDL** with a different lock class, and batching does not apply to it.
- `postgresql` owns PG index specifics: index types (`SKILL.md:57-63`), Decision
  framework step 2 on matching index type to access pattern (`:118-124`), and it
  *does* name a lock-related anti-pattern — routine `VACUUM FULL`, "markedly
  slower and takes an exclusive table lock" (`:204-206`). So the skill
  demonstrably reasons about lock classes. It never applies that reasoning to
  index creation.
- Consequence, concretely: a compliant run following the library's guidance can
  produce a migration whose `CREATE INDEX ... USING GIN (search_vector)` takes
  an `ACCESS EXCLUSIVE` lock on `products` and blocks every write for the
  duration of the build. On a catalog of any size that is a write outage during
  a change the user was told is additive and reversible.

**Root cause.** The DDL-lock class sits at the same seam RWS-01 identifies:
`data-migration` owns "migration safety" generically, `postgresql` owns "PG
index specifics", and *online index creation* is both at once. Neither
`owned_knowledge` list claims it (`postgresql/skill.yaml:209` claims
"PostgreSQL full-text search (tsvector/tsquery + GIN) usage"; nothing claims
index-build concurrency).

**Recommended correction.** One sourced paragraph in `postgresql` — it owns
index specifics and already cites `postgresql.org/docs/current/` index pages, so
SG-2 is satisfiable without new research scope. It must carry the real caveats,
not just the flag: `CONCURRENTLY` cannot run inside a transaction block (which
matters because most migration tools wrap each migration in one), and a failed
concurrent build leaves an `INVALID` index that must be dropped and retried.
Plus a one-line cross-reference from `data-migration` that DDL index creation is
a distinct lock class from a batched backfill.

**Regression test requirement.** Fold into the same proposed **S18** as a
`major` assertion: the migration artifact either uses a non-blocking index build
or explicitly records why a blocking one is acceptable for this table. Note this
assertion is checkable from `changes[]` without prose matching, per
`evaluation-spec.md:53-79`.

---

### RWS-03 · The decision framework's pivot — "moderate scale" — is unquantified in both skills, and the skill's own `verification` demands a citation it cannot supply — Medium

**Finding.** Both sides of the engine decision turn on the same undefined word:

- `search-integration/SKILL.md:81-82`: "full-text search at **moderate scale**
  with no need for a separate cluster".
- `postgresql/SKILL.md:130-133`: "covers **moderate** full-text needs… escalate
  … once relevance-tuning or scale requirements **exceed what GIN-backed FTS
  documents supporting**."

Nothing in `search-integration`, `postgresql`, `opensearch`, or
`research/knowledge-maps/` states any threshold — rows, index size, QPS, p95
latency, corpus size — at which PG FTS stops being adequate, nor what GIN-backed
FTS "documents supporting." Meanwhile the skill's own contract demands
precisely that material:

- `required_context` (`skill.yaml:53`): "Expected index size and query
  volume/latency requirements" — information the *user* must supply.
- `verification` (`skill.yaml:101`): "An engine recommendation **cites the
  documented differentiators where research exists**."

The asymmetry is measurable: the branch the skill argues *against* is
quantified in the same file — "10–30GB shards for search-latency-sensitive
workloads, 30–50GB for write-heavy/analytics" (`SKILL.md:64-67`). The branch it
argues *for* has no number anywhere.

**Consequence for this task.** The user stated no scale, so
`failure_handling` rule 1 (`skill.yaml:95`) fires: "If the search requirement …
expected scale … is too thin to support an engine decision, request it rather
than assuming a default." That is correct behavior and I do not fault it. But
once the user answers — "about 40,000 products" — the skill has **no criterion
to apply the answer to**. The right recommendation (PG FTS) is reached by the
skill's default-to-simple posture, not by its stated decision rule. The
framework is directionally sound and operationally unfalsifiable.

This also creates a mild internal tension: `failure_handling` says *request the
scale rather than assuming a default*, while the Decision framework *is* a
default-to-simple rule that does not actually consume a scale figure. A run
could reasonably conclude the clarifying question is ceremonial.

**Root cause.** `search-integration`'s grounding is `mixed` and its search-engine
sources (`skill.yaml:75-86`) are the decision matrix, the performance map's
OpenSearch sections, and the concept map. None of the three contains a
PG-FTS-scale-ceiling datum, and SG-3 correctly forbade inventing one. The defect
is that the skill asserted a *pivot* on a quantity its research does not
contain, instead of disclosing the gap the way it discloses the Elasticsearch
gap two paragraphs earlier (`SKILL.md:50-57`, and again in `verification`:
"states plainly where research is thin").

**Recommended correction.** Replace "moderate scale" with the honest form the
same skill already uses elsewhere: state that **no documented crossover
threshold exists in this library's research**, and give a measurable escalation
trigger instead of an adjective — e.g. *"escalate to a dedicated engine on a
measured p95 against a stated latency budget, or on a stated relevance
requirement PG's ranking cannot express — not on row count, for which this
library has no documented threshold."* That is both truthful and more
actionable than the current wording.

**Regression test requirement.** Fold into **S18** as a `major` assertion: the
engine recommendation either cites a documented differentiator or explicitly
records that no documented scale threshold exists — a recommendation that
asserts "this is moderate scale, so PG FTS" with no basis fails, **even though
the conclusion is correct**. This is exactly the `scoring.md:44-47` discipline
("Partial or 'spirit of the rule' matches are not `pass`") and it is the
assertion that distinguishes a well-reasoned run from a lucky one.

---

### RWS-04 · The PG-specific injection-and-robustness surface of FTS is not covered — Medium

**Finding.** The security dimension is *half* handled.

What works: `SK-QA-002` activates correctly on untrusted input, and
`postgresql`'s Security section opens with "Parameterize all queries"
(`SKILL.md`, Security bullet 1) before deferring depth to `SK-QA-002` per QR-2.
So classic SQL injection through the search term is closed. S07's expected
behaviors already formalize this pattern for the substring-match case.

What is missing is PG-FTS-specific and is not an injection issue but a
correctness one that *looks* like a security issue in production:
`to_tsquery()` parses a **tsquery expression language** and raises a syntax
error on arbitrary user text (`&`, `|`, `!`, `:`, unbalanced parentheses).
`plainto_tsquery()` and `websearch_to_tsquery()` exist precisely to accept raw
user input safely. A parameterized `to_tsquery($1)` is injection-safe **and
will 500 on a user typing `a & b` or an apostrophe-laden product name.**

`grep -i "plainto_tsquery\|websearch_to_tsquery"` across `skills/` returns
**zero** hits. `tsvector`/`tsquery` appear only as *type names*
(`postgresql/SKILL.md:70, 129`; `skill.yaml:209`). The library therefore gives
correct injection guidance and no guidance on the query constructor, which is
the specific thing that makes or breaks a user-facing PG FTS endpoint.

**Root cause.** `postgresql`'s FTS knowledge is one sentence
(`SKILL.md:70-72`) — enough to support the *decision* (step 4) but not the
*implementation*. The skill's FTS coverage is sized for the escalation question,
not for the build.

**Recommended correction.** Extend `postgresql`'s Full-text search knowledge
bullet with the constructor distinction and a sourced pointer to
`postgresql.org/docs/current/textsearch-controls.html`, plus an anti-pattern:
"Feeding raw user input to `to_tsquery()` — it parses an operator syntax and
errors on ordinary text; `plainto_tsquery`/`websearch_to_tsquery` are the
user-input-safe constructors." Approximately four lines; it stays inside the
skill's existing `owned_knowledge` claim.

**Regression test requirement.** Fold into **S18** as a `major` assertion, and
flag the relationship to **S07** explicitly in the scenario header. S07 and S18
are deliberate twins: S07 asserts `SK-DATA-005` must **not** fire for name-only
substring matching (`expected-behaviors/S07:37-41`); S18 is the true-positive
case where it **must** fire. The pair is what actually validates the
"simple `WHERE` lookup vs. genuine full-text" boundary in both directions, and
neither half is sufficient alone.

---

### RWS-05 · `search-integration` declares no `escalation` field — Medium, but **does not bite on this task**

**Finding.** Verified: `search-integration/skill.yaml` has no `escalation:` key,
while `SKILL.md:199-207` carries two real gates — a search-engine switch on an
existing production index (a **G-COMMITMENT** class gate,
`failure-recovery-and-escalation.md:149`) and the RAG research-gap escalation.
This is X-04 / R-05, instance confirmed.

**Honest assessment of the bite: nil, here.** Neither gate arms on this task —
there is no existing production index to switch away from, and no RAG request.
The structural defect (ER-1 cannot enumerate a gate that lives only in a body
CS-1 forbids loading) is real, but this task never reaches it. Recorded so a
reader does not over-weight it, and as evidence that X-04's severity is
genuinely task-shape-dependent — contrast
[`infrastructure-legacy-deploy.md`](infrastructure-legacy-deploy.md) RWI-03,
where the same defect lands on a `production`-risk plan and does bite.

**Recommended correction.** Per X-04: resolve the spec question (should
`escalation` be required when the body has the section?) and sweep all 27 behind
a validator. Not a per-file fix.

**Regression test requirement.** **No new scenario for this instance.** A
scenario that exercises it would need an existing production search index and a
switch request — a different task. If coverage is wanted, it belongs in the
conflicting-requirement category alongside S16, not in S18.

---

### RWS-06 · Two stale Tier-0 markers in `search-integration`, one of them an intra-file contradiction — Low, **not triggered**

**Finding.** X-02 already flagged `search-integration`; this evaluation confirms
both sites and adds one observation X-02 did not make.

- `skill.yaml:40`, non-activation 1: "A simple indexed `WHERE`/lookup query
  suffices (route to database-operations, **not yet authored**)."
  `SK-DATA-003` is authored. **Not triggered here**: the user named "full-text
  search" over two columns including free-text `description`, which the
  "simple indexed `WHERE`" condition does not match, so SR-2 does not exclude
  `search-integration`. The false marker is inert on this task; it would bite on
  a borderline request where the router *did* want to route out.
- `skill.yaml:41`, non-activation 2: the RAG/LLM layer is "a documented research
  gap in this library, not answered here" — while **line 67 of the same file**
  lists `SK-AI-005` (rag-engineering, authored, and the owner of exactly that
  layer) in `related_skills`. X-02 noted the marker is stale; the sharper point
  is that **the file contradicts itself 26 lines apart**, so a reader has no way
  to tell which statement is current. Also repeated in `SKILL.md:19-25`,
  `:90-93`, `:131-133`, `:161-163`, `:205-207` — six sites, all asserting a gap
  that a sibling skill fills. **Not triggered here**: no RAG dimension exists in
  this task.

**Recommended correction.** Part of X-02's single mechanical sweep. The RAG
sites need judgement (the correct replacement is a route-to-`SK-AI-005` clause,
not a deletion), which is why X-02 declined to apply them.

**Regression test requirement.** **No new scenario.** Mechanically validatable
(VR-3 family, extended to prose references) and already inside the sweep X-02
requested.

---

## What works (recorded so a later reviewer does not re-open it)

**The anti-over-engineering guard on this decision is the strongest I found
across the three tasks**, and it is guarded redundantly — five independent
statements, in two skills, any one of which would produce the right answer:

1. `search-integration` Decision framework step 1 — check the existing database
   first; "don't reach for a dedicated engine by default" (`SKILL.md:80-84`).
2. Engineering rule 1 — "Don't reach for a dedicated search engine when DB-native
   FTS on a database already in use would satisfy the requirement" (`:122-123`).
3. Anti-pattern 1 — "Standing up a dedicated search engine before checking
   whether the database already in use covers the need — an unjustified new
   operational surface" (`:150-152`). This satisfies QR-4's requirement that
   anti-patterns name the domain's over-engineering trap, and names the *right*
   one.
4. Trade-offs (`:137-146`) — states the dedicated engine's costs concretely (a
   second data copy, an additional cluster) rather than as a vague caution.
5. `postgresql` Decision framework step 4 — the same conclusion from the engine
   side, ending "don't add a search engine 'in case.'" (`SKILL.md:129-133`), plus
   step 1's standing "Simplest first (anti-overengineering)" rule (`:115-117`).

Two further positives:

- **SR-3 makes the correct answer structural, not judgemental.** `opensearch` is
  not detection-eligible in a repo with no OpenSearch signal, so over-activation
  is prevented by the routing mechanism before any decision framework runs. This
  is the detection-gating discipline `routing-audit.md` praised, doing the work.
- **The skill refuses to fabricate an Elasticsearch comparison** (`SKILL.md:50-57`,
  `:129-130`, `verification` item 3), which is the exact honesty pattern RWS-03
  argues should have been applied to the scale threshold as well. The discipline
  exists in the file; it was just not applied uniformly.

---

## Score

| # | Dimension | Verdict | Why |
|---|---|---|---|
| 1 | Skill routing | **Strong** | Both `search-integration` activation conditions match verbatim; `opensearch` excluded structurally by SR-3; the undetected ORM cluster is raised as a decision rather than activated broadly. No over-activation. |
| 2 | Dependency activation | **Weak** | The one prerequisite this task actually needs — `data-migration` for a populated-table schema change — is not reachable from `search-integration`'s declared edges, and only becomes knowable at P5 (RWS-01). |
| 3 | Context efficiency | **Strong** | ~3 generic + 1 technology body, stage-scoped. `opensearch` (the largest search body) never loads. `related_skills`' two AI entries are correctly not pulled, though only by inference from SR-1 (C-01 remains unwritten). |
| 4 | Implementation quality | **Adequate** | The engine choice, index type (GIN), and sync reasoning are right. The build-level specifics that determine whether the feature actually works — the query constructor (RWS-04) and a non-blocking index build (RWS-02) — are absent. |
| 5 | Security | **Adequate** | S-Gate 1 classifies correctly, `SK-QA-002` activates, parameterization is stated by the owning skill. The FTS-specific `to_tsquery` failure mode is uncovered (RWS-04) but is a robustness rather than an injection defect. |
| 6 | Testing | **Good** | T-Gate 1 staffs verification; `search-integration`'s Testing section names the two search-specific concerns (index-sync correctness, relevance regression) that generic testing would miss. |
| 7 | Maintainability | **Strong** | The dimension this task was chosen to stress. Five independent guards steer to the simpler option; QR-4 is satisfied with the correct domain-specific trap named. **No over-engineering risk found.** |
| 8 | Error handling | **Good** | `failure_handling` correctly requests the missing scale rather than assuming (`skill.yaml:95`), and correctly refuses to answer a RAG request as a search question. Undercut only by there being no criterion to apply the answer to (RWS-03). |
| 9 | Convention adherence | **Good** | Nothing contested; the existing query convention (parameterized placeholders, per S07's established pattern) would be followed under the precedence ladder rung 3. |
| 10 | Final outcome | **Adequate** | A real engineer gets the right architectural answer, cheaply and with good reasoning — and a migration that may lock the catalog's writes, and an endpoint that 500s on an apostrophe. The decision is well served; the build is not. |

**Summary:** High ×2 (RWS-01, RWS-02), Medium ×3 (RWS-03, RWS-04, RWS-05),
Low ×1 (RWS-06, not triggered).

The headline is a shape worth naming: **`search-integration` de-risks the branch
it recommends against and leaves the branch it recommends for unguarded.** The
over-engineering guard the brief asked me to stress-test is genuinely strong;
the cost was paid on the other side, where choosing the simple option was
treated as the end of the reasoning rather than the start of a different set of
risks.
