# Real-World Evaluation — Databases: NOT NULL column on a 50M-row `users` table

Step 32 of the master build plan. Adversarial pattern: **outdated technology
assumptions**. Date: 2026-09-11. Method per the step brief: trace the run from
the actual `skill.yaml` fields, then evaluate whether the library's own
version-awareness discipline (VA-1…VA-5, `covered_versions`,
`reverify_triggers`) handles a request that falls *outside* a skill's declared
coverage.

**Standing caveat:** nothing here is enforced by a runtime (`self-review.md`
R-1). Findings are about written rules and written metadata.

> **Scenario-ID note.** The `S17`+ identifiers proposed below are allocated
> within this file's scope only. Sibling Step 32 real-world audits were written
> in parallel and independently propose `S17`/`S18`/`S19`, so **every new
> scenario ID across `audits/real-world/` needs one reconciliation pass before
> any scenario file is created.** Treat the IDs here as placeholders; the
> findings and assertions they carry are what matter.

## Task and repository signals

> Migrate our `users` table to add a `NOT NULL` column with a default value —
> the table has 50 million rows in production.
>
> Current version: **PostgreSQL 12.**

Classification: intent `migrate`; task type **migration** (`workflows.md` #6);
complexity `multi-step`; risk **`production`** — the highest class in the ladder
below `destructive`, and both are arguably in play. D3 (`lifecycle.md`:88) sets
this at intake; D13 (`lifecycle.md`:191) makes P4 admission mandatory ("risk
class is destructive, outward-facing, **or production**"); ER-1 (`rules.md:99`)
requires the gates be named before work starts.

**This part the architecture gets right, and it should be said first.** Risk
classification, mandatory plan admission, and up-front gate declaration all fire
correctly and for the correct reason, with no ambiguity in the rules.

---

## Routing trace

### Included

| Skill | Matching condition | Cite |
|---|---|---|
| `data-migration` SK-DATA-006 | "A schema change is needed on a database that already has data" / "The user asks to migrate, backfill, or evolve an existing schema" | `skills/data-migration/skill.yaml:28-29` |
| `testing-strategy` SK-QA-001 | SR-5 — a migration script is runnable code | `rules.md:25` |
| `capability-adapter` SK-ORCH-002 | `data-migration` is Tier B (shell to run the migration) | `skills/capability-adapter/skill.yaml:35` |
| `workflow-composer` SK-ORCH-003 | multi-stage with gates | `skills/workflow-composer/skill.yaml:34-35` |
| conventions (`code-commenting`, `code-quality`, `git-conventions`) | SR-6 | `rules.md:30` |

`data-migration` is the right owner and is a genuinely good skill for this task.
Its Knowledge section names both failure modes correctly — *"(1) irreversibility
… and (2) blocking — a migration that locks a table long enough to cause an
outage"* (`skills/data-migration/SKILL.md:35-37`) — and its rollback,
expand/contract and batching disciplines are all on point for a 50M-row table.

### Excluded — including the one that matters

| Skill | Why excluded | Cite |
|---|---|---|
| `data-modeling` SK-DATA-001 | non_activation[2]: "The task is migrating an already-populated database to a new shape (route to data-migration)" | `skills/data-modeling/skill.yaml:36` |
| `database-operations` SK-DATA-003 | no activation match — all four conditions are query-perf / isolation / pool / N+1 | `skills/database-operations/skill.yaml:30-33` |
| `legacy-modernization` SK-CONV-005 | no activation match — the user is not upgrading a version or modernizing a pattern | `skills/legacy-modernization/skill.yaml:32-34` |
| `orm-integration`, `prisma`/`drizzle`/`typeorm` | SR-3, undetected | — |
| **`postgresql` SK-TECH-postgresql** | **non_activation[3]** | `skills/postgresql/skill.yaml:38` |

That last row is the pivot of this whole trace:

```
postgresql  activation[2]      : "The task names PostgreSQL or a PG-specific feature…"   :32
            non_activation[3]  : "The task is safely evolving an already-populated
                                  schema's migration process, not PostgreSQL feature
                                  usage (route to SK-DATA-006)"                          :38
```

The task is *exactly* "safely evolving an already-populated schema's migration
process." SR-2 — "Non-activation is decisive… exclude it even if its activation
also matches" (`rules.md:13`) — excludes `postgresql`.

**Consequence:** the only skill in the library that carries `covered_versions`,
`version_sensitive_claims` and `reverify_triggers` for PostgreSQL is routed off
this task by its own metadata. The version-coverage question the step brief asks
about is therefore never even reached — not because the coverage check failed,
but because the skill that owns the coverage data was excluded one phase
earlier.

---

## The coverage question, evaluated on its own terms

Suppose `postgresql` *had* activated (it is a plausible routing on activation[2]
if the phrase "PostgreSQL 12" is weighted over the migration framing). What
then?

**1. PG12 is outside the declared coverage.**
`covered_versions: postgresql: ">=14 <=18"` (`skills/postgresql/skill.yaml:174`).
The body restates it: *"This skill's guidance targets **PostgreSQL 14–18**;
treat anything marked `>=18` as inapplicable on older majors still in support"*
(`skills/postgresql/SKILL.md:104-106`). Note the tail qualifier — the sentence
addresses majors *still in support*, and says nothing about a major below the
floor.

**2. PG12 is outside the library's own documented support window.**
`research/technologies/postgresql.md:157` records the five-year policy; its
version table (`:161-167`) starts at PG14 (EOL 2026-11-12). PG12 reached GA in
October 2019, so its EOL was November 2024 — roughly 22 months before this
task's date. The research doc does not list PG12 at all, and no skill states
what to do about a version below the table.

**3. Nothing in the skill handles a known-but-out-of-range version.**
`failure_handling` covers the *unknown*-version case only: *"If the PostgreSQL
major version **cannot be determined**, ask for it or explicitly state the
version the guidance assumes"* (`skill.yaml:216`). Here the version is
determined; it is simply outside the range. VA-3 (`specification.md:193`) is
satisfied — nothing is assuming "latest." VA-4 (`:194`) is about `last_verified`
and staleness relative to `reverify_triggers`, and **all four of `postgresql`'s
triggers point forward**: PG19 reaching GA, an md5 removal version, a
`pg_upgrade` compatibility change, a new protocol version
(`skill.yaml:199-202`). None fires when an *older* version is requested.

**4. Nothing in `core/` handles it either.** The failure taxonomy
(`failure-recovery-and-escalation.md`:33-41) has no class for it: F1 is
input-deficient (the input is present), F7 is a contract violation (the skill is
not misbehaving), F6 is plan-invalidating evidence. `capability-adapter`'s four
activation conditions (`skills/capability-adapter/skill.yaml:35-38`) are all
about *host* capability, never about a skill's *knowledge* coverage.
`skill-router`'s failure_handling (`:100-103`) covers ambiguity, conflict
clusters, unauthored skills and an unavailable signal scan — not this.

**5. The library contains the right instruction, in the wrong skill.**
`legacy-modernization`'s failure_handling[0]: *"If the target technology's
breaking-change data isn't covered by this library's research, state that gap
rather than inventing migration guidance"*
(`skills/legacy-modernization/skill.yaml:80`). That is precisely correct — and
it sits in a Layer-2 skill whose activation conditions do not fire on this task.

---

## Findings

### F1-DB · No skill or rule handles a request outside a technology skill's `covered_versions` — **Critical**

**Finding.** PG12 falls outside `postgresql`'s `covered_versions`
(`>=14 <=18`) and outside the library's own researched support table. Three
layers each fail to notice, independently:

- the **skill**: no `non_activation_condition` mentions version range; the
  version-related `failure_handling` rule covers only *undeterminable* versions
  (`skill.yaml:216`);
- the **version-awareness rules**: VA-1…VA-5 require declaring coverage
  (`covered_versions`), tagging claims (`version_sensitive_claims`), and
  re-verifying against `reverify_triggers` — but **no rule says what to do when a
  request falls outside the declared coverage.** VA-4's staleness discipline is
  entirely forward-looking;
- the **orchestrator**: F1–F9 has no class for "topically in scope, outside the
  declared knowledge range," and `capability-adapter` resolves host capability,
  not knowledge coverage.

The silent-proceed branch is therefore the default path. This is the risk
`self-review.md` R-3 names and explicitly declines to mitigate — *"a
confident-but-wrong output satisfies every check this architecture has"* — here
instantiated with a concrete trigger rather than as an abstract worry.

**Root cause.** `covered_versions` was designed as a **disclosure** field (what
this skill's content is correct for) and is never read as a **guard** (refuse or
flag outside it). Every rule that touches it — VA-1, VA-2, VA-4, SG-5 — is about
keeping the skill's own claims honest and current, not about matching the
skill against a request. The field has no consumer.

**Recommended correction.** Two changes, of which the first is small and the
second is architectural:

1. **A new version-awareness rule, `VA-6 [V]/[A]`:** *"When the version in use
   is determinable and falls outside a technology skill's `covered_versions`,
   the skill states that its guidance is out of range before answering, and
   either (a) restricts itself to claims it can tag as applicable to the version
   in use, or (b) declines and escalates as a research gap."* Mirror it into
   each technology skill's `failure_handling` — 40 skills, but mechanically
   derivable from `covered_versions`, and `legacy-modernization:80` is already
   the house-style sentence to copy.
2. **A tenth failure class, `F10 · Coverage-deficient`**, in
   `failure-recovery-and-escalation.md`, with a D16 row of `R7` (escalate with
   the evidence — the declared range, the version in use, and what is and is not
   safe to say) falling through to `R4` (advisory, explicitly caveated). It is
   genuinely distinct from F1: the input is present and valid, the *skill* is out
   of range, which is the inverse direction and needs the inverse response.

**Regression test requirement.** Not covered — `evaluations/scenarios/` S01–S16
contains no out-of-coverage case. S01 is a PostgreSQL scenario but tests
over-activation on a simple query fix; S11 (jQuery→Vue) is a modernization
scenario where the target is *in* coverage. **New scenario required: `S22 —
technology version outside declared coverage`**, category 7 (Failure scenarios).
Critical assertion: the run's record contains an explicit statement that the
stated version is outside the activated skill's `covered_versions`, *before* any
version-gated recommendation is made — and no `version_sensitive_claim` from
outside the applicable range is applied without its range tag.

---

### F2-DB · SR-2 excludes the only version-aware skill from exactly the task class where version-awareness decides the answer — **High**

**Finding.** `postgresql`'s non_activation[3] (`skill.yaml:38`) routes migration
work to `SK-DATA-006` and, under SR-2, that exclusion is decisive. But
`data-migration` is engine-agnostic by design: its `covered_versions` field does
not exist (it is `kind: generic`), its version-sensitive Knowledge is entirely
ORM-specific — Prisma/MongoDB, Drizzle v1, TypeORM v1, MySQL 8.4
(`skills/data-migration/SKILL.md` §Knowledge) — and its Tier-2 reference
`references/version-sensitive-migrations.md` contains **no PostgreSQL entry at
all**.

So the clause's premise — that "migration process" and "PostgreSQL feature
usage" are separable — is false for this task. Whether `ALTER TABLE … ADD COLUMN
… NOT NULL DEFAULT` is a catalog-only operation or a full table rewrite *is* the
migration process on a 50M-row table, and it is an engine- and version-gated
fact.

This is the third variant of a pattern this evaluation found in all three
domains: a non-activation clause written as a clean topical hand-off, where the
routed-to skill does not own the decisive fact.
[`frontend-product-listing.md`](frontend-product-listing.md) F1-FE found guards
too *weak* to exclude; this one is too *strong*, and excludes the skill that was
needed.

**Root cause.** Non-activation clauses are authored as scope statements about
the *skill*, and validated for disjointness (VR-6) and non-duplication (VR-7),
but never against the question "does the skill I am routing to actually own the
knowledge this task turns on?" There is no rule requiring a routing target to be
checked for coverage of the routed case.

**Recommended correction.** Re-scope `postgresql`'s non_activation[3] to hand
off the *process* while retaining the *engine facts*:
*"The task is the rollout discipline of an already-populated schema migration
(sequencing, rollback, batching) — that process is owned by SK-DATA-006; this
skill still supplies the PostgreSQL-specific locking and DDL-behavior facts the
process depends on."* That phrasing already exists in the corpus —
`realtime-communication`'s non_activation[1]
(`skills/realtime-communication/skill.yaml:36`) uses exactly this
"route-the-schema-but-keep-the-judgement" construction. This is a routing-
behavior change, so it is a decision, not a fix.

**Regression test requirement.** Fold into **S22** as a `critical` assertion
rather than a separate scenario: *`SK-TECH-postgresql` appears in
`routing_record.selected[]`, not `excluded[]`, on a PostgreSQL migration task
whose correctness depends on engine-specific DDL behavior.* Same repository
setup, same task; scoring both the exclusion and the coverage check in one
scenario is cheaper and tests the interaction, which is where the real failure
lives.

---

### F3-DB · The library's generic migration guidance produces an over-engineered answer here, and nothing can catch it — **High**

**Finding.** *(This finding uses engineering knowledge external to the library
to judge the outcome, and says so explicitly — the fact below is **not** sourced
anywhere in this repository, which is itself half the finding.)*

Since PostgreSQL 11, `ALTER TABLE … ADD COLUMN … NOT NULL DEFAULT <non-volatile
expression>` stores the default in the catalog and does **not** rewrite the
table; the operation takes a brief `ACCESS EXCLUSIVE` lock for the catalog
update and is effectively O(1) regardless of row count. On PG12, therefore, the
correct answer to this task is a single statement plus a `lock_timeout` and a
retry, and no backfill at all.

What the library's activated skill actually says, followed verbatim:

- Decision framework step 1: *"Does this need zero downtime? … If not,
  expand/contract is the default, not an optional refinement"*
  (`skills/data-migration/SKILL.md:83-85`).
- Decision framework step 3 + engineering rule: *"How large is the table being
  backfilled? Above a size where a single transaction would hold a meaningful
  lock, batch it"* / *"Backfills over populated tables are batched, never a
  single blocking pass"* (`:89-91`, `:109`).
- Anti-patterns: *"Single-transaction backfill on a large populated table"*
  (`:127-128`).

Fifty million rows, production, zero-downtime need: every branch points at a
multi-phase expand/contract migration with a batched backfill — more steps, more
production touches, and more rollback surface than the problem requires. The
guidance is not wrong in general; it is wrong *here*, and the library has no way
to know that, because a full-corpus grep for `NOT NULL`, `table rewrite`,
`ACCESS EXCLUSIVE`, `lock_timeout` and `add column` returns **zero hits in any
skill**.

Worse, the missing fact belongs to PG**11** — *below* `postgresql`'s declared
floor of 14. So this is not only "PG12 is uncovered"; the DDL-behavior
inflection point that decides the task predates the covered range entirely and
is absent from the skill for every version it does cover.

`data-migration`'s own anti-pattern list names the shape of this failure —
*"this is the domain's overengineering-adjacent trap in reverse:
under-checking, not over-building"* (`SKILL.md:131-134`) — but the check it
prescribes is "check version-sensitive migration caveats," and the caveats it
supplies are all ORM-level.

**Root cause.** Two compounding gaps: (a) `postgresql`'s `owned_knowledge`
(`skill.yaml:205-210`) covers MVCC/VACUUM, index types, isolation, RLS, FTS and
replication, but not **DDL locking behavior** — a first-order operational topic
for any populated database; (b) `data-migration`'s version-sensitive knowledge
is ORM-shaped because the ORM skills were authored around it, and no engine
skill ever contributed its DDL facts upward.

**Recommended correction.** Add DDL-lock behavior to `postgresql`'s
`owned_knowledge` and body, sourced from the PostgreSQL `ALTER TABLE` docs — the
fast-default path, the operations that do and do not rewrite, and `lock_timeout`
discipline — with per-version tags per VA-2. Extending `covered_versions` below
14 is **not** recommended: the honest move is to document the inflection point
with its range tag and leave the floor where the research supports it.

**Regression test requirement.** Distinct from S22 — this is a *content* gap,
not a routing or coverage-guard gap, and it needs the implementation-quality
dimension rather than the failure dimension. **New scenario recommended: `S23 —
migration shape proportional to the actual engine behavior`**, category 6
(Legacy-code tasks) or 5. Critical assertion: the proposed migration's step
count is justified against the engine's documented DDL behavior for the version
in use, rather than defaulting to expand/contract on table size alone.

---

### F4-DB · `data-migration`'s escalation gate is scoped to data loss; this task's risk is availability loss — **Medium**

**Finding.** The declared escalation is *"Any step that can lose data (a DROP, a
destructive ALTER, an irreversible transform) requires explicit user
confirmation"* (`skills/data-migration/skill.yaml:85`;
`SKILL.md:146-148`). Adding a `NOT NULL` column with a default loses no data. If
it triggers a table rewrite on a 50M-row production table, it holds `ACCESS
EXCLUSIVE` for minutes-to-hours — a production outage, not a data loss.

The gate class exists: G-PRODUCTION covers "production is affected"
(`failure-recovery-and-escalation.md`:148), and the orchestrator's D13 admission
fires on the `production` risk class. But the *skill's own* escalation field —
the thing a router reads under ER-1, and the thing an agent reads when it is
inside the skill — names only the data-loss trigger. The skill's body knows
better: blocking is failure mode (2) in its own Knowledge section
(`SKILL.md:35-37`). This is a content-level instance of the metadata/body
desync `cross-skill-audit.md` X-04 found structurally.

**Root cause.** The escalation field was authored against `matrices.md`'s
escalation-matrix row for `data-migration`, which reads "destructive migration
(data loss) ↑ human (confirm)" (`matrices.md:150`). The matrix row is itself
data-loss-scoped, so the skill faithfully reproduced an incomplete source.

**Recommended correction.** Extend both. `matrices.md`'s row should read
"destructive **or availability-affecting** migration"; `data-migration`'s
`escalation` should gain: *"A migration step that can hold a blocking lock on a
populated production table requires explicit confirmation with the expected lock
duration stated, even when no data is lost."* Note this makes GA-8 ("prefer the
reversible form", `failure-recovery-and-escalation.md`:204) applicable, which it
currently is not, since GA-8 keys off destructiveness.

**Regression test requirement.** Fold into **S23** as a `major` assertion — the
same task exercises it, and the gate and the shape are the same decision.

---

### F5-DB · The one correct out-of-coverage instruction lives in a skill this task cannot activate — **Medium**

**Finding.** `legacy-modernization`'s failure_handling[0] (`skill.yaml:80`) is
the library's only rule of the form "if our research doesn't cover it, say so
rather than inventing guidance." Its activation conditions
(`skill.yaml:32-34` — upgrading a major version, modernizing outdated patterns,
migrating off a deprecated approach) do not fire on "add a column." Running an
EOL database arguably *is* "a deprecated approach," but the *task* is not that,
and SR-1's default-deny correctly keeps it out.

Separately, `data-migration`'s non_activation[1] routes broad modernization to
"legacy-modernization, **not yet authored**"
(`skills/data-migration/skill.yaml:33`) — a stale X-02 marker in a Tier-0 field,
telling the router its escape hatch does not exist. `legacy-modernization` has
been authored since.

**Root cause.** The out-of-coverage discipline was treated as a
modernization-specific concern rather than a library-wide one.

**Recommended correction.** Generalize it via F1-DB's VA-6 rather than by
widening `legacy-modernization`'s activation — widening it would over-activate a
heavyweight Layer-2 skill on routine work. Sweep the stale marker with X-02.

**Regression test requirement.** No new scenario; covered by S22's critical
assertion and, for the stale marker, by the validator rule recommended in
[`frontend-product-listing.md`](frontend-product-listing.md) F4-FE.

---

### F6-DB · `data-migration` still has no testing linkage, and this is the task where it costs most — **Medium** *(instance of D-02 / X-12)*

**Finding.** `dependency-audit.md` D-02 recommended adding
`depends_on_skills: [SK-QA-001]` to `data-migration`, mirroring `refactoring`;
`cross-skill-audit.md` X-12 found it has no `## Testing` section. Both remain
open (`skills/data-migration/skill.yaml:57-58`: `related_skills: [SK-DATA-001,
SK-DATA-002]`, no `SK-QA-001` anywhere). Its verification is an *existence*
check — "a working rollback path **exists** or its absence is explicitly stated"
(`skill.yaml:81`) — never an execution check.

On this task that is the difference between a rollback plan and a rollback that
works: the `down` path for a `NOT NULL` column on 50M rows must be exercised
against production-shaped data before the `up` path is trusted, and nothing in
the activated set requires it. `routing-architecture/examples.md:138` already
staffs "testing-strategy (migration up/down tests)" for exactly this workflow —
the routing docs assume an edge the metadata does not carry.

**Root cause.** D-02's, unchanged.

**Recommended correction.** D-02's and X-12's, unchanged — they should land
together, and this task is additional evidence for prioritising them.

**Regression test requirement.** Fold into **S23** as a `major` assertion
(`SK-QA-001` is staffed and its verification covers the `down` path). Note the
interaction with [`backend-bulk-import.md`](backend-bulk-import.md) F2-BE: even
when staffed, `SK-QA-001` cannot currently declare that the migration test was
not actually executed.

---

## Scoring

| # | Dimension | Verdict | Note |
|---|---|---|---|
| 1 | Skill routing | **Fail** | `postgresql` excluded by its own non-activation on the one task class where engine facts decide the answer (F2-DB) |
| 2 | Dependency activation | **Partial** | `data-migration` correctly owns it, but has no edge to `SK-QA-001` (F6-DB) |
| 3 | Context efficiency | **Pass** | A tight set; if anything too tight |
| 4 | Implementation quality | **Fail** | Guidance points at expand/contract + batched backfill for an operation that needs neither on PG11+ (F3-DB) |
| 5 | Security | **Partial** | `users` is a PII table; `data-migration` still has no Security section (X-11, open) and nothing routes to `SK-QA-002` |
| 6 | Testing | **Partial** | SR-5 staffs `testing-strategy`; verification of the `down` path is required by no activated skill |
| 7 | Maintainability | **Fail** | The library's default answer is materially more complex than the problem requires — the over-engineering trap, reached by following the guidance correctly |
| 8 | Error handling | **Fail** | No skill and no failure class handles out-of-coverage versions (F1-DB) |
| 9 | Repo conventions | **Pass** | Conventions attach normally; nothing task-specific |
| 10 | Final outcome | **Fail** | An engineer following this library on this task gets correct process discipline, correct gating, and a migration plan several times larger than necessary — with no signal that the guidance is outside its own declared version range |

**Summary:** this task fails worse than the other two, and for a more
interesting reason. Nothing malfunctions: the router applies SR-2 correctly, the
risk class and gates are right, and `data-migration` gives accurate generic
advice. The failure is that `covered_versions` — the library's central
anti-outdatedness device — is a **disclosure with no consumer**: no rule reads
it, no failure class fires on it, and the one skill carrying the right
out-of-coverage instruction is not activated. The library's own honest framing
of this risk (`self-review.md` R-3, accepted and unmitigated) is confirmed
here with a concrete trigger.
