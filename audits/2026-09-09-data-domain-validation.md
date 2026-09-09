# Audit: DATA-domain skill generation & validation

Date: 2026-09-09. Scope: the twelve skills generated in this batch — three
generic (`SK-DATA-001` data-modeling, `SK-DATA-002` orm-integration,
`SK-DATA-006` data-migration) and nine technology skills (`SK-TECH-postgresql`,
`SK-TECH-mysql`, `SK-TECH-mongodb`, `SK-TECH-mongoose`, `SK-TECH-drizzle`,
`SK-TECH-prisma`, `SK-TECH-typeorm`, `SK-TECH-clickhouse`, `SK-TECH-redis`).
Also includes one carry-forward fix to `solution-architecture` from the prior
batch. Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).

**Authorship note:** the three generic skills were authored directly by hand
(they set the boundaries everything else must respect). The nine technology
skills were delegated to nine parallel agents, each given the exact
relationship data (parents/conflicts/related), pre-verified version facts,
and the mandatory files to read — this was judged appropriate because
technology-skill authoring is fundamentally "restructure already-cited
research into the spec format," not open judgment, unlike the generic
skills or the taxonomy/dependency work. Every agent's output was
independently re-verified on disk (file existence, line counts, YAML
validity) rather than trusted from its self-report, per the standing lesson
from an earlier incident in this project where agents falsely claimed
success without writing files.

## Completed skills

| Skill | ID | Files | Citations in SKILL.md |
|---|---|---|---|
| [data-modeling](../skills/data-modeling/) | SK-DATA-001 | yaml, SKILL.md, 1 reference | 8 |
| [orm-integration](../skills/orm-integration/) | SK-DATA-002 | yaml, SKILL.md, 1 reference | 10 |
| [data-migration](../skills/data-migration/) | SK-DATA-006 | yaml, SKILL.md, 1 reference | 4 |
| [postgresql](../skills/postgresql/) | SK-TECH-postgresql | yaml, SKILL.md | 40 |
| [mysql](../skills/mysql/) | SK-TECH-mysql | yaml, SKILL.md, 1 reference | 39 |
| [mongodb](../skills/mongodb/) | SK-TECH-mongodb | yaml, SKILL.md | 47 |
| [mongoose](../skills/mongoose/) | SK-TECH-mongoose | yaml, SKILL.md, 1 reference | 42 |
| [drizzle](../skills/drizzle/) | SK-TECH-drizzle | yaml, SKILL.md, 1 reference | 34 |
| [prisma](../skills/prisma/) | SK-TECH-prisma | yaml, SKILL.md | 27 |
| [typeorm](../skills/typeorm/) | SK-TECH-typeorm | yaml, SKILL.md | 29 |
| [clickhouse](../skills/clickhouse/) | SK-TECH-clickhouse | yaml, SKILL.md | 36 |
| [redis](../skills/redis/) | SK-TECH-redis | yaml, SKILL.md, 1 reference | 50 |

All twelve independently confirmed on disk (not just from agent self-reports)
with substantial content — 4 references files created only where the agent
judged real Tier-2 material existed (mysql, mongoose, drizzle, redis); the
other 8 correctly stayed single-file per the context-efficiency "don't create
a references file just to have one" rule.

**Mechanical checks run and passed, all twelve:**
- YAML validity (all parse cleanly).
- VR-2 (`skill.yaml` name/slug match `SKILL.md` frontmatter and directory name).
- CE-1 (`description` ≤ 500 chars) — range 344–487 chars.
- VR-8 (body section order matches spec §3.2, verified as a subsequence match, not just presence).
- VR-1 (all "always required" fields present) and technology-conditional
  fields (`parents`, `covered_versions`, `reverify_triggers`,
  `source_references`) present for all 9 technology skills.
- VR-5 (`execution_tier`/`required_capabilities` consistency) — all Tier B with `[file-read, file-write, shell]`, correctly excluding Tier-C-only capabilities.
- VR-3 (every cross-referenced ID — `parents`/`depends_on_skills`/`related_skills`/`conflicts_with` — resolves to a real taxonomy ID) — verified against all 81 taxonomy IDs.
- Conflict-cluster symmetry (`mongoose`/`drizzle`/`prisma`/`typeorm` all list each other back) — no asymmetric conflicts found.
- All relative links (`SKILL.md`/`skill.yaml` → `references/…`, `core/…`, sibling skills) resolve.

## Unresolved questions

1. **Resolved this batch, but confirm the resolution is final:** the
   `depends_on_skills`-vs-`parents` ambiguity flagged as Unresolved Question
   #1 in the DISC-domain audit recurred here — independently, across 7 of the
   9 technology-skill agents (see Potential corrections #1). That this exact
   conflation happened seven times without coordination is strong evidence
   it's a genuine specification gap, not one agent's mistake. I applied the
   same policy fix I'd already made to `solution-architecture` (specialization
   → `parents` only; `depends_on_skills` → true hard composition only) — but
   this is the second time the fix has been applied ad hoc during validation
   rather than the specification itself being amended to state the rule
   explicitly. Recommend adding an explicit sentence to
   `specification.md` §2.5 before the next batch, so it stops recurring.
2. **`typeorm` and (partially) `drizzle` omitted uncertain claims rather than
   marking them "Unresolved:"**, while the other 10 skills used explicit
   markers. Both are defensible (omission is at least as safe as flagging),
   but it's an inconsistency in house style worth deciding on explicitly:
   should every skill be required to surface an "Unresolved" list even when
   empty, for auditability, or is silent omission acceptable?
3. **Is `mongodb`'s `conflicts_with: []` correct?** I instructed this
   deliberately (polyglot persistence makes MongoDB non-exclusive with
   PostgreSQL/MySQL, per the architecture-patterns reference), but the
   technology-decision-matrix.md groups all four databases as one decision
   point. Flagging so a maintainer can confirm this reading is intended
   rather than an oversight.
4. **`redis`'s SKILL.md is 472 lines**, close to the ~500-line CE-2 target,
   reflecting genuine breadth (Redis is documented as spanning 4 real roles:
   cache, pub/sub, search/vector, data-structure store). Worth watching if
   future revisions push it over the line — at that point some of the
   4-role breadth might belong in a Tier-2 reference instead.

## Duplicated responsibilities

**None found at the engineering-content level.** Every technology skill's
agent was explicitly given its parent skill(s) to read and instructed not to
repeat their content — spot-checks (e.g., `mongoose`/`drizzle`/`prisma`/
`typeorm` all explicitly state they're deferring N+1/transaction-handling
method to `orm-integration`, and PostgreSQL/MySQL/MongoDB/ClickHouse all
defer schema-design method to `data-modeling`) confirm this held. Each
skill's Security/Performance/Testing sections cite *its own* technology's
specific facts rather than restating cross-cutting method.

**One redundancy found and fixed** (not content duplication, a
specification-level one): see Potential corrections #1 below —
`depends_on_skills` duplicating `parents` in 7 of 9 technology skills.

## Missing dependencies

Technology skills whose **formal taxonomy parents are not yet authored** in
this library (expected — this batch's scope was fixed by the user's approved
ID list, which didn't include every DATA-domain generic skill):

| Skill | Unauthored parent(s) |
|---|---|
| postgresql | `SK-DATA-003` (database-operations), `SK-DATA-005` (search-integration) |
| mysql | `SK-DATA-003` (database-operations) |
| mongodb | `SK-DATA-005` (search-integration) |
| clickhouse | `SK-DATA-003` (database-operations) — **its only formal parent; clickhouse currently has zero authored parents** |
| redis | `SK-DATA-004` (caching-strategy), `SK-BE-004` (realtime-communication), `SK-DATA-005` (search-integration) — **all three unauthored; redis currently has zero authored parents** |

`clickhouse` and `redis` are the two skills most exposed by this gap — both
were instructed to stay self-contained and comprehensive precisely because
they can't yet lean on a parent for depth. Once `database-operations`,
`caching-strategy`, `realtime-communication`, and `search-integration` are
authored, these five skills' `Knowledge`/`Performance` sections should be
revisited to confirm nothing they currently state directly should move up
into the new parent to avoid duplication going forward.

## Potential corrections

1. **Fixed in this pass: `depends_on_skills` duplicating `parents`.** 7 of 9
   technology skills (`postgresql`, `mysql`, `mongodb`, `mongoose`, `drizzle`,
   `prisma`, `typeorm`) had their exact `parents` list also populated into
   `depends_on_skills` — pure redundancy, confirmed by set comparison (zero
   entries in `depends_on_skills` that weren't already in `parents`). Cleared
   `depends_on_skills` to `[]` in all 7, consistent with the same fix already
   applied to `solution-architecture` in the prior batch's audit. `clickhouse`
   and `redis` did not exhibit this (plausibly because their real parents
   don't exist as files yet, so there was nothing concrete for an agent to
   point `depends_on_skills` at).
2. **`SK-DATA-001` (data-modeling)'s `related_skills` includes `SK-DISC-002`**
   (solution-architecture) — a reasonable addition (data-modeling is
   typically invoked in service of an architecture decision) but, like the
   DISC-domain batch's similar addition, goes beyond what the original
   taxonomy catalog entry literally listed. Flagged for visibility, not
   recommended against.
3. **`clickhouse` and `redis` relate to `SK-DATA-001` (data-modeling) as a
   `related_skill` even though it is not their formal taxonomy parent.** This
   was a deliberate instruction (both need *some* schema/key-design framing
   even though their real parents are unauthored) and is clearly distinct
   from a fabricated `parents` claim — `parents` correctly lists only their
   real taxonomy-assigned parents. Flagged so the distinction is visible on review.
4. **Version-sensitive facts are dense and, in a few cases, actively
   contradictory within the vendor's own docs** (Prisma 8's `take()`/`skip()`
   vs. `limit()`/`offset()` rename conflicting with its own reference docs;
   Drizzle's live docs already describing v1 APIs while most production code
   runs 0.x). Both skills correctly surfaced these as open tensions rather
   than picking a side — worth highlighting as a genuine strength of this
   batch, not a gap, since it's exactly what the "do not fabricate" policy
   is for.
5. **No skill in this batch was promoted to `final/`** — same as the
   DISC-domain batch, this requires a mechanical validator (still doesn't
   exist as executable tooling) and `evaluations/` tests (not yet written).

## Overall assessment

All twelve skills are internally consistent with the specification, taxonomy,
dependency architecture, and routing architecture, well-grounded (every
technology skill cites `research/technologies/<slug>.md` directly, with 27–50
inline citations each — spot-checked for real, non-boilerplate content), and
version-aware (every technology skill states its `covered_versions` and
tags version-gated claims explicitly, including several genuinely difficult
cases: MySQL's mid-transition versioning scheme, Prisma's MongoDB-only-on-v6
gap, Drizzle's v0-stable/v1-rc split, TypeORM's simultaneously-live 0.3.x/1.0
lines). One real specification gap recurred and was fixed consistently
(`depends_on_skills` vs. `parents`); recommend closing it permanently by
amending `specification.md` rather than continuing to catch it at audit time.
