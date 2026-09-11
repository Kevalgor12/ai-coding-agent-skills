# Real-World Evaluation — APIs: paginated, filterable product-catalog search

**Step 32 · Task 1 of 3 · Adversarial pattern: irrelevant skills present in the repository**

**Task statement (verbatim, per ST-1):**

> Design a paginated, filterable search API for our product catalog (REST, not GraphQL).

**Repository context:** the repo also contains (a) an unrelated, fully-built
**GraphQL API** for order management, and (b) an **OpenSearch cluster** already
configured for an unrelated full-text feature (support-ticket search). Neither
belongs to the product-catalog subsystem.

**Method.** I traced this task through `core/routing-architecture/routing-algorithm.md`
Phases 0–6 and `core/orchestrator/lifecycle.md` P0–P7, evaluating every candidate
against the **authored** `activation_conditions` / `non_activation_conditions` in
`skills/*/skill.yaml` — not against `core/taxonomy/skill-catalog.md`'s description
of them (same discipline as `audits/cross-skill/routing-audit.md:12`). Findings
already made in Step 28/29 are cited, not re-derived; what is new here is whether
*this* task actually triggers them.

**Standing caveat** (per `core/orchestrator/self-review.md`): no runtime executes
this. These are findings about a specification's behaviour under a traced
application of its own rules.

---

## Part 1 — The traced run

### P0 · Intake

- `task_statement` recorded verbatim. **User constraint extracted: "REST, not
  GraphQL"** — immutable, precedence-ladder rung 2 (`state-and-contract.md:99-104`).
  This is the single most load-bearing signal in the whole task and the router
  gets it for free; it does not have to infer the paradigm.
- Bounded signal scan (CS-6) returns: a GraphQL schema/server for order
  management; an OpenSearch client config/deployment manifest; a product-catalog
  data store (engine unnamed in the given context); REST routes.
- Intent = `build`; task type = **feature development** (workflow #2,
  `workflows.md:38-53`); complexity = `small`–`multi-step`; risk = `reversible-write`.
- **S-Gate 1** (intake security screen, `security-and-validation.md:64`): a
  public-ish list endpoint taking user-supplied filter parameters *is* an
  untrusted-input surface. This should classify positive and drive SR-5.

### P1 · Discovery — conflict-cluster resolution

The relevant cluster is **API paradigm** (`matrices.md:90`): `api-design(REST) ⊥
graphql-api-design`, scope "per endpoint". SR-4 requires resolving this *before*
selection, and lifecycle P1.2 scopes it "for the artifact under change"
(`lifecycle.md:98`). The artifact under change is a new REST endpoint. Resolution:
**REST**. GraphQL is out — correctly, and for the right reason.

Note for Part 2: the matrix declares this cluster, but **both**
`api-design/skill.yaml:61` and `graphql-api-design/skill.yaml:60` declare
`conflicts_with: []`. The cluster exists only in a prose table. See F1.4.

### P2 · Routing — per-skill adjudication

| Skill | Verdict | Grounds |
|---|---|---|
| `api-design` (SK-BE-002) | **INCLUDE** | `skill.yaml:29` "Designing or extending an HTTP/REST API" — direct match. Owns pagination (`skill.yaml:11-13`, `SKILL.md:96`). |
| `graphql-api-design` (SK-BE-003) | **EXCLUDE** | `skill.yaml:34` non-activation "REST/HTTP API design (route to api-design)" matches the signals; SR-2 is decisive (`rules.md:11-15`). The GraphQL API *elsewhere* in the repo never enters the calculation because Layer-3 skills are not detection-gated — they are task-gated. **Correctly guarded.** |
| `openapi-swagger` (SK-TECH-openapi-swagger) | **EXCLUDE** | `skill.yaml` non-activation: "REST resource/versioning/pagination contract design with no spec-tooling question (route to api-design)". Exact match. **Correctly guarded.** |
| `backend-architecture` (SK-BE-001) | **EXCLUDE** | non-activation: "the task is the HTTP/GraphQL contract itself with structure already settled (route to api-design/graphql-api-design)". **Correctly guarded.** |
| `performance-engineering` (SK-QA-003) | **EXCLUDE** | non-activation "No performance concern"; SR-5 admits it only on a stated perf concern/budget. None stated. Defensible — but see F1.2, because deep-offset pagination *is* a latent perf concern this exclusion then leaves unowned. |
| `search-integration` (SK-DATA-005) | **INCLUDE — false positive** | See F1.1. |
| `opensearch` (SK-TECH-opensearch) | **INCLUDE — false positive** | See F1.1. |
| `database-operations` (SK-DATA-003) | **EXCLUDE — wrong** | See F1.2. |
| `data-modeling` (SK-DATA-001) | borderline exclude | activation is "a new data model/schema is being designed" (`skill.yaml:30`); the catalog schema exists. Correct to exclude. |
| `security-engineering` (SK-QA-002) | **INCLUDE** | SR-5 + S-Gate 1: user-supplied filter/sort parameters are untrusted input. |
| `testing-strategy`, `code-quality`, `code-commenting` | INCLUDE | SR-5/SR-6: runnable code is produced. |
| `capability-adapter` (SK-ORCH-002) | INCLUDE (barrier) | SR-7 — but *only because* the two false positives are Tier B. See F1.1's context cost. |
| everything else (~72 skills) | EXCLUDE | SR-1 default-deny, recorded per SR-11. |

### P3–P6 · Plan shape

```
api-design  →  [security-engineering: filter/sort input validation]  →  implementation
   →  testing-strategy (⟳)  →  code-review ⤾ (quality ∥ comment ∥ security facets)
```

No gates (`reversible-write`, no destructive/outward/production step). D13
admission not required — correct proportionality (`lifecycle.md:191-205`).

**The honest summary of the trace:** the two *named* adversarial distractors
(GraphQL, OpenAPI tooling) are excluded cleanly and by explicit reciprocal
routing clauses. The failure is not where the task's framing pointed — it is in
the **search-integration → opensearch chain**, and, more seriously, in what the
correctly-minimal set *cannot* deliver.

---

## Part 2 — Findings

### F1.1 · `search-integration` and `opensearch` both activate on a bounded SQL filter task — **High**

**Finding.** Under a literal application of the routing algorithm, both skills
enter the selected set.

`search-integration/skill.yaml:36` — activation condition 1:

> "A feature needs full-text search, **faceted/filtered search**, or semantic/vector search"

The task says "**filterable** search … for our product catalog". That is a direct
textual match on "faceted/filtered search". Its guard,
`search-integration/skill.yaml:40`:

> "A simple indexed `WHERE`/lookup query suffices (route to database-operations, **not yet authored**)"

does **not** deterministically fire, for two independent reasons:

1. Phase 3 evaluates `matches(s.non_activation_conditions, signals)`
   (`routing-algorithm.md:54-57`). "A simple indexed `WHERE` suffices" is a
   *conclusion the skill would reach*, not a signal in the scan output. The
   router cannot evaluate it before doing the analysis the skill exists to do.
2. The clause tells the router its own routing target does not exist.
   `database-operations` **is authored** (`skills/database-operations/skill.yaml:2`).
   This is the exact instance class `audits/cross-skill/cross-skill-audit.md:597`
   (X-02) rated High precisely because "16 of the 50 sit in
   `non_activation_conditions` — the Tier-0 field CS-1 makes the *only* thing
   the router reads." **This task triggers it in practice.** A router told the
   off-ramp is unbuilt has a positive reason to keep the skill.

`opensearch/skill.yaml:36` — activation condition 1:

> "An OpenSearch client library, connection config, or Docker/Helm/Kubernetes-Operator deployment referencing OpenSearch **is present**"

The repo has exactly that — for support-ticket search. The condition is
**presence-scoped, not relevance-scoped**. The partial saving throw is
`opensearch/skill.yaml:41` ("The search-engine choice itself is still open →
route to SK-DATA-005"), which fires only if `search-integration` already
concluded the engine choice is open. That is a second-order rescue that depends
on the first false positive behaving correctly — not a guard.

**Cost when it fires.** `search-integration` is `execution_tier: B` with `shell`
(`skill.yaml:70-71`); `opensearch` likewise (`skill.yaml:75-76`). Their inclusion
therefore (a) arms the `capability-adapter` barrier (PR-3) on a task with no
executable step, (b) loads `opensearch`'s body — the largest Tier-0/Tier-1
payload in the DATA domain, with 20 source references, shard-sizing and
security-plugin content — and (c) invites `search-integration`'s owned
"engine-selection decision framework" (`skill.yaml:90`) to propose indexing the
product catalog into OpenSearch. That is an architecturally wrong answer
delivered with the library's full authority.

**Root cause — the structural one.** SR-3 (`rules.md:32-35`) is a *prohibition*:

> "Never activate a `SK-TECH-*` skill for a technology **absent** from the repo
> and unnamed in the request. Presence = a manifest entry, a driver import, a
> config file, a connection string, a file type, or an explicit mention."

It says presence is *necessary*. It never says presence is **not sufficient**.
Phase 2 repeats the same shape (`routing-algorithm.md:42-43`: "only these are
detection-eligible for Layer-4 activation"). The library *has* the missing
concept and applies it one rule over: `dependency-graph.md:176-178` —

> "Conflicts are **soft at repo scope** (a monorepo may contain both React and
> Vue apps) but **hard at decision scope** … `skill-router` resolves by detecting
> which is actually in play **for the current artifact**."

— and `lifecycle.md:98` scopes conflict resolution to "the artifact under
change". That artifact-scoping was never propagated from SR-4 to SR-3. The
result: a technology present *anywhere* in a repository is activation-eligible
for *every* task in it. `audits/cross-skill/routing-audit.md`'s R-04 examined
polyglot monorepos in the **exclusion** direction (`go`/`nodejs` mis-excluding
themselves); this is the same monorepo blind spot in the **inclusion** direction,
and it is unreported.

**Recommended correction** (three parts, smallest first):

1. **Mechanical, safe now:** fix `search-integration/skill.yaml:22` and `:40` and
   `data-modeling/skill.yaml:34` — `database-operations` exists. Part of X-02's
   recommended sweep; this task shows the sweep is not cosmetic.
2. **Rewrite the guard so it is signal-evaluable.** Replace
   `search-integration`'s "a simple indexed `WHERE`/lookup query suffices" with a
   test the router can apply from the scan: *"the query is an equality/range
   filter plus sort over structured columns of a single entity, with no relevance
   ranking, tokenization, stemming, fuzzy matching, or cross-entity free-text
   requirement (route to `database-operations` + `api-design`)."* Filtering is
   not searching; the current activation condition conflates them.
3. **Add SR-3b to `rules.md`:** *"Technology-skill presence is subsystem-scoped.
   A `SK-TECH-*` skill is eligible only where the detection signal belongs to the
   subsystem containing the artifact under change. A signal from an unrelated
   subsystem of the same repository is recorded as present-but-out-of-scope and
   does not make the skill eligible."* This is the generalization of
   `dependency-graph.md:176-178` from conflicts to activation, and it is the
   single highest-leverage fix surfaced by this task.

**Regression test requirement.** **Yes — a new scenario.** `evaluations/scenarios/`
was checked: `S07-product-search-injection-risk.md` is the closest and is
explicitly *not* this test — its repository signals (`S07:15-31`) deliberately
contain no OpenSearch, no GraphQL, and no second subsystem. No scenario in the
suite places an irrelevant-but-present technology in the repo. Propose
**S17 — irrelevant subsystem technologies present**: this task, with repo signals
stating the GraphQL order-management API and the configured OpenSearch cluster
for support-ticket search. Critical assertions: `SK-DATA-005` and
`SK-TECH-opensearch` appear in `routing_record.excluded[]` with a
subsystem-scope reason; `SK-ORCH-002` is *not* armed (no Tier-B step exists);
no engine-selection analysis is produced. This is the suite's missing
adversarial category.

---

### F1.2 · Nothing in the selected set owns pagination *correctness* — **High**

**Finding.** `api-design` is the only skill that owns pagination, and its entire
treatment of it is that it must exist:

- `skill.yaml:84` (verification) — "Pagination is specified for any list endpoint that can grow unbounded."
- `SKILL.md:96` (workflow step 5) — "Specify pagination for any list endpoint that can grow unbounded."
- `SKILL.md:104` (engineering rule) — same sentence again.
- `SKILL.md:120` (anti-pattern) — "Unbounded list endpoints with no pagination."

Four sites, one instruction. The words **cursor**, **keyset**, **offset**,
**seek**, and **stable sort key** appear **nowhere** in `api-design/SKILL.md` or
its `references/rest-vs-graphql.md`. So the composed guidance is silent on every
decision that actually determines whether the endpoint works:

- offset/`LIMIT…OFFSET` vs. cursor/keyset pagination;
- the deep-offset cost cliff (page 5,000 of a catalog scans and discards 100k rows);
- **result instability** — offset pagination over a catalog that is being written
  to silently skips and duplicates rows across pages, which for a *product
  catalog* is a user-visible correctness bug, not a performance nit;
- the requirement for a total-order sort key (`(sort_col, id)`) for a cursor to
  be well-defined;
- the composite index that must exist to support filter-then-sort, and the
  combinatorial limit on how many filter fields can be indexed.

**The asymmetry is the sharpest evidence.** `graphql-api-design/skill.yaml:82`
declares as a hard verification item:

> "List fields use **cursor-based pagination, not raw offset/limit**, unless there's a stated reason otherwise."

The GraphQL skill — the one this task explicitly rules out — carries strictly
stronger pagination guidance than the REST skill the task routes to. An engineer
who asked for GraphQL would get better pagination advice from this library than
one who asked for REST.

**Why the normal backstop does not catch it.** `database-operations` would be the
natural owner of the index/keyset half, and it is **excluded**, correctly per its
own metadata: all four of its activation conditions (`skill.yaml:29-33`) are
*symptom*-shaped — "Query performance **is a concern** (slow query, missing
index, full table scan)", "N+1 patterns **are suspected or present**",
"connection-pool **exhaustion**". It has no condition for *designing an access
path for a query pattern that does not exist yet*. So the skill that owns
"Index-strategy selection" (`skill.yaml:71`) cannot be activated by a design-time
task. `performance-engineering` is out by SR-5 for the same reason (no stated
budget). SR-10's completeness backstop (`rules.md:42-44`) then cannot fire: the
*stage* (implementation) is staffed by `api-design`, so the backstop sees no
hole — the hole is inside a staffed stage, which SR-10 does not inspect.

**Root cause.** Two things, compounding: (a) `api-design`'s pagination
`owned_knowledge` claim (`skill.yaml:75`) is broader than its authored content —
it claims the "pagination … design method" but supplies only an existence
requirement; (b) `database-operations` is authored as a *diagnostic* skill and
cannot be reached prospectively.

**Recommended correction.**

1. Add the pagination-strategy decision to `api-design`'s Decision framework
   (offset vs. cursor, keyed on: mutation rate of the collection, need for
   random page access, expected depth) and a matching `verification` item:
   *"For any collection that mutates while being paged, the pagination scheme is
   stable under concurrent insert/delete, or the instability is stated."* This is
   `api-design`'s own `owned_knowledge` — no QR-2 duplication risk.
2. Add a **design-time** activation condition to `database-operations`:
   *"A new query/access pattern is being designed and its index support has not
   been decided."* This is the narrower and more valuable of the two fixes,
   because it unblocks the skill for every greenfield-endpoint task in the
   library, not just this one.
3. Consider adding "filter-parameter contract design (allow-listed filterable
   and sortable fields, operator vocabulary, combination limits)" to
   `api-design` — the skill currently says **nothing** about filtering at all,
   which is half of this task's literal request. See also F1.3.

**Regression test requirement.** **Yes — fold into S17** as `major` assertions
rather than a separate scenario: the produced contract names a pagination
strategy *and* its stability property; an index/access-path decision is made or
explicitly deferred with a named owner. Filing it separately would create two
scenarios over the same task.

---

### F1.3 · Filter-parameter injection is caught, but only by a skill the task-shape barely admits — **Medium**

**Finding.** `security-engineering` activates on `skill.yaml:33` ("handling
untrusted input … or a trust boundary") — user-supplied filter/sort parameters
qualify, and S-Gate 4 (`security-and-validation.md:67`) makes the security review
facet mandatory. So injection *is* covered, and `S07`'s existing expected
behaviors already exercise that path for a search term.

The residual gap is narrower and real: this task's untrusted input is not only a
*value* (parameterizable) but an *identifier* — filter field names, sort column,
sort direction. Those cannot be bound as query parameters and must be
allow-listed. Nothing in `api-design` (which owns the contract where the
allow-list belongs) or `security-engineering` (whose `owned_knowledge`,
`skill.yaml:72-74`, is the threat-modeling *method*) states the identifier-vs-value
distinction. `S07`'s repository signals (`S07:18-21`) establish a parameterized-
placeholder convention, which the run would correctly follow — and which does
nothing for a dynamic `ORDER BY`.

**Severity Medium, not High:** the layered review (`skill.yaml:85`, "Defense is
layered") plus the mandatory facet means a competent run probably gets there. But
"probably, by general competence" is what a skill library exists to replace.

**Recommended correction.** Add one engineering rule to `api-design`: *"Filterable
and sortable fields are an explicit allow-list in the contract; a filter or sort
identifier is never interpolated from client input, because identifiers cannot be
parameterized."* Placed in `api-design` rather than `security-engineering` because
it is a contract-design obligation, and QR-2 forbids restating the injection
category in a non-owning skill.

**Regression test requirement.** **Extend S07** rather than adding a scenario —
add a `major` assertion that the run allow-lists sort/filter identifiers
separately from parameterizing values. S07's task statement already supports it
(`S07:9-11` filters by a user-supplied term); only the assertion list needs the
addition.

---

### F1.4 · The API-paradigm conflict cluster exists only in prose — **Medium** *(instance of X-03)*

**Finding.** `matrices.md:90` declares `api-design(REST) ⊥ graphql-api-design`.
Both skills declare `conflicts_with: []` (`api-design/skill.yaml:61`,
`graphql-api-design/skill.yaml:60`). `audits/cross-skill/cross-skill-audit.md:199`
(X-03) already scored this High library-wide and gave the count (0/2 declared
edges for this cluster).

**What this task adds.** The finding is *real but non-binding here*, and saying
so is the point of a real-world trace. The exclusion survives on the reciprocal
non-activation clauses (`graphql-api-design/skill.yaml:34`) plus the user's
explicit "REST, not GraphQL" constraint at precedence rung 2. SR-2 does the work
SR-4 was supposed to. The exposure is to a *host adapter*: `adapters/lib/skill_loader.py`
projects `skill.yaml`, not `matrices.md`, so a projected skill set carries no
API-paradigm exclusion at all — and a task without the explicit "not GraphQL"
constraint (e.g. "add a search API for the catalog") would lose the SR-2 rescue too.

**Recommended correction.** As X-03 recommends — add the 2 edges, and make
`matrices.md` a projection rather than a parallel table. Do not re-litigate; this
trace is evidence for X-03's priority, not a new finding.

**Regression test requirement.** **No new scenario.** Belongs to the X-03
remediation and its own validator check (VR-3-adjacent: matrix rows must be
backed by declared edges). A behavioral scenario cannot observe it on this task,
because the behaviour is correct here for other reasons.

---

### F1.5 · `api-design/SKILL.md:131` still says `authentication-authorization` is unauthored — **Low here** *(instance of X-02 / frontend-backend-generic.md:156)*

Already found and rated High in `audits/individual-skills/frontend-backend-generic.md:156`
(also `api-design/skill.yaml:19`, `:34`). **On this task it is Low**: the product
search endpoint has no auth-design question, so the false statement is never
consulted. Recorded to confirm the existing finding's remediation list is
complete, and to note that the same file's `:34` clause ("realtime-communication,
not yet authored") is stale too — `skills/realtime-communication/` exists.

---

## Part 3 — Dimension scorecard

| # | Dimension | Score | Evidence |
|---|---|---|---|
| 1 | Skill routing | **Poor** | The named distractors are excluded cleanly and reciprocally (GraphQL, OpenAPI, backend-architecture). But the *unnamed* ones — `search-integration`, `opensearch` — both activate (F1.1), and the skill that should have activated (`database-operations`) cannot (F1.2). Two false positives and one false negative on a four-skill task. |
| 2 | Dependency activation | **Adequate** | Conflict cluster resolved in the right direction; no cycles; layer-monotone. Weakened by the cluster having no declared edges (F1.4) and by SR-10 being unable to see an intra-stage hole (F1.2). |
| 3 | Context efficiency | **Poor** | The false positives are both Tier B, so they arm the `capability-adapter` barrier on a task with no executable step and pull `opensearch`'s large body — roughly a doubling of loaded context for zero task value (F1.1). |
| 4 | Implementation quality | **Poor** | The core deliverable is a pagination + filtering contract, and the library supplies one sentence about pagination and nothing about filtering (F1.2, F1.3). A correct-but-naive `LIMIT/OFFSET` design would pass every verification item `api-design` declares. |
| 5 | Security | **Good** | S-Gate 1 → SR-5 → `security-engineering` → mandatory S-Gate 4 facet is the cleanest chain in this trace. Residual identifier-vs-value gap is narrow (F1.3). |
| 6 | Testing | **Good** | SR-5 admits `testing-strategy` (runnable code produced); T-Gate 4 applies; `jest-vitest` would attach on detection. Nothing task-specific goes wrong. |
| 7 | Maintainability | **Good** | `api-design/SKILL.md:122` names the right over-engineering trap ("Choosing GraphQL by default 'for flexibility'"), and QR-4 compliance is real. The main over-engineering risk on this task comes *from* the library (F1.1's OpenSearch pull), not from the user. |
| 8 | Error handling | **Adequate** | `api-design/skill.yaml:79-81` degrades sensibly (ask, or hand to `data-modeling`). Untested on this task — nothing fails. The Tier-B false positives would, ironically, exercise the capability ladder correctly. |
| 9 | Convention adherence | **Good** | ST-5 convention detection is orthogonal here; the REST-vs-GraphQL user constraint is honored at precedence rung 2, which is exactly the mechanism ST-4/IC-7 specify. |
| 10 | Final outcome | **Adequate, trending poor** | An engineer gets a correct resource/error/versioning contract and a real injection review — genuine value. They also get a plausible, wrong suggestion to index the catalog into the support-ticket OpenSearch cluster, and no guidance on the two things they actually asked about. A senior engineer would catch both; a mid-level engineer would not. |

**Overall: partial.** The adversarial pattern the task was designed to probe
(named irrelevant paradigm/tooling) is defended well and by design. The pattern
it exposed by accident — *a technology that is genuinely present, in a subsystem
that is genuinely irrelevant* — is undefended, because SR-3 gates on presence and
the library's subsystem-scoping concept lives only in the conflict rules.
