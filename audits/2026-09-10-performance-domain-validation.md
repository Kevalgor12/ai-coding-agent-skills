# Audit: PERFORMANCE-domain skill generation & validation

Date: 2026-09-10. Scope: three skills, all generic — `SK-DATA-003`
database-operations, `SK-DATA-004` caching-strategy, and `SK-QA-003`
performance-engineering. Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).
This batch closes both outstanding DATA-domain gaps first flagged in the
SEARCH-domain audit and repeated in the SECURITY-domain audit.

**Scope note:** the user's 10-item list ("Performance Architecture,
Frontend Performance, Backend Performance, Database Performance, Query
Optimization, Caching, Redis Performance, Network Performance, Load
Testing, Profiling") maps to 3 skills, not 10. `SK-QA-003`
performance-engineering (cross-cutting: profiling, caching, query tuning,
bundle size, connection pooling, scaling) absorbed "Performance
Architecture," "Frontend Performance," "Backend Performance," "Network
Performance," "Load Testing," and "Profiling" — none had independent
taxonomy entries. `SK-DATA-003` database-operations (indexing, query
optimization, transactions, pooling, replication) absorbed "Database
Performance" and "Query Optimization" directly by name. `SK-DATA-004`
caching-strategy (what/where/invalidation/TTLs, explicitly spanning
Redis/ORMs/Next-Nuxt-rendering/Docker-CI layers) absorbed "Caching" and
"Redis Performance" — the latter folding in since no standalone
Redis-performance skill exists; Redis's own tech-specific mechanics
already live in the already-authored `SK-TECH-redis`. Confirmed via
`AskUserQuestion` ("Yes, proceed with 3") rather than assumed. As a direct
side effect, this batch also closes both DATA-domain generics that were
never authored in the original DATA-domain batch and had since been
flagged as open forward-reference gaps by two consecutive audits (SEARCH,
SECURITY).

**Authorship note:** as with the SECURITY batch, this batch contains **no
technology skills to delegate** — all three are cross-cutting/DATA
generics with implementation depth owned by already-authored technology
skills (PostgreSQL/MySQL/MongoDB/ClickHouse for database-operations;
Redis for caching-strategy) rather than a new paired technology skill.
All three were authored directly by hand, grounded in
`performance-knowledge-map.md`'s full 18-section breakdown — the second
consecutive batch to read a full knowledge-map document end-to-end for
dedicated synthesis (after `security-knowledge-map.md` in the SECURITY
batch), rather than sampling it piecemeal as most prior batches' technology
skills had done.

## Completed skills

| Skill | ID | Tier | Files | `[Source:]` / `[Synthesis]` citations |
|---|---|---|---|---|
| [database-operations](../skills/database-operations/) | SK-DATA-003 | B | yaml, SKILL.md | 4 / 2 |
| [caching-strategy](../skills/caching-strategy/) | SK-DATA-004 | A | yaml, SKILL.md | 4 / 2 |
| [performance-engineering](../skills/performance-engineering/) | SK-QA-003 | B | yaml, SKILL.md | 2 / 4 |

All three independently confirmed on disk (file existence, line counts) —
self-authored by hand, so the "verify against agent self-report" step
doesn't apply; the YAML validity and field-presence checks were still run
and passed on all three files, matching the discipline established in the
SECURITY batch for self-authored work.

**Mechanical checks run and passed, all three (scripted, not manual):**
- YAML validity for all 3 `skill.yaml` files.
- VR-1 (all always-required fields present, including `depends_on_skills`
  present-and-empty).
- CE-1 (description ≤ 500 chars) — all three well within range.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically, zero mismatches.
- VR-3 (every `related_skills`/`conflicts_with` ID resolves to a real
  taxonomy entry) — all resolve cleanly, including the mutual
  cross-references between all three skills in this same batch, forward
  references to already-authored technology skills
  (`SK-TECH-postgresql`/`mysql`/`mongodb`/`clickhouse`/`redis`), and
  forward references to unauthored skills (`SK-QA-001` is actually
  authored — corrected below — `SK-CONV-004`, `SK-FE-005`, unauthored).
- `depends_on_skills: []` for all three — each skill hands off to the
  others via `related_skills` only; none of the three compose another's
  procedure as a hard inline sub-step, correctly distinguished from
  `git-workflow`'s genuine hard-composition precedent from the CONV/INFRA
  batch.
- `execution_tier` consistency: `database-operations` (B, shell needed to
  run `EXPLAIN`/query plans) and `performance-engineering` (B, shell
  needed for profiling/benchmarking tools) both Tier B;
  `caching-strategy` (A, advisory/design-level work) Tier A.
- All relative links resolve.

## Unresolved questions

1. **ClickHouse has no documented diagnostic/profiling tool equivalent to
   Postgres's `EXPLAIN` or MySQL's Performance Schema** in this library's
   research — stated as a real, explicit gap in
   `performance-engineering` rather than assumed to exist by parity with
   the other databases.
2. **OpenSearch's JVM-heap-sizing guidance is carried forward with the
   same inference caveat** already established when `opensearch` itself
   was authored in the SEARCH batch (documented guidance, not
   independently re-verified verbatim) — not re-asserted with more
   confidence here.
3. **Several performance figures cited in `performance-engineering` are
   explicitly flagged as vendor-reported, not independently corroborated**
   — the TypeScript-7/Vite-8/Tailwind-v4 native-rewrite speedup claims
   specifically carry this caveat in the skill's own Knowledge section,
   consistent with this library's standing discipline (already applied to
   these same figures when their respective technology skills were
   authored in the FRONTEND batch) of not presenting vendor benchmarks as
   independently verified.
4. **This library's research is explicitly silent on several categories a
   performance skill would normally cover** — general-purpose CDN
   vendors, message-queue/event-streaming performance (consistent with
   the Event-Driven-Architecture gap flagged in the REALTIME batch),
   load-balancer configuration, and Node.js runtime-level performance
   (V8 tuning, event-loop diagnostics) — all stated plainly in
   `performance-engineering` as gaps rather than improvised.

None of these four were load-bearing enough to block any skill.

## Duplicated responsibilities

**None found**, despite unusually high duplication risk given how
tightly the three skills interlock (caching often IS a database-
performance technique; performance-engineering's own scope explicitly
lists "caching, query tuning, connection pooling" as example
responsibilities that the other two skills actually own):

- `caching-strategy` explicitly defers database query optimization itself
  to `database-operations`, and defers Redis-specific implementation
  mechanics to the already-authored `redis` technology skill, while
  covering only the cache-layer-selection and invalidation-design
  concerns that are genuinely its own.
- `database-operations` explicitly defers caching-layer design to
  `caching-strategy` (its own non-activation condition names this split
  directly) and covers only indexing/N+1/transactions/pooling.
- `performance-engineering` explicitly states in its own Purpose & scope
  that it is "not a repeat of any single technology's own performance
  page," and its Knowledge section links out to `database-operations` and
  `caching-strategy` for the N+1, connection-pool, and Redis-as-
  connective-tissue patterns rather than re-explaining them — reproducing
  only a one-line pointer plus attribution, not the full pattern
  described elsewhere.
- All three skills' `related_skills` cross-reference each other, and each
  skill's own Knowledge section is scoped to content the other two don't
  already cover.

## Missing dependencies

- `database-operations` references `SK-DATA-001` (authored),
  `SK-DATA-004`/`SK-QA-003` (both authored within this same batch), and
  four already-authored database technology skills — no unauthored
  forward references.
- `caching-strategy` references `SK-DATA-003`/`SK-QA-003` (both authored
  within this same batch) and `SK-TECH-redis` (already authored) — no
  unauthored forward references.
- `performance-engineering` references `SK-QA-001` (testing-strategy,
  **already authored**, from the QA-domain batch), `SK-DATA-003`/
  `SK-DATA-004` (both authored within this same batch), and
  `SK-CONV-004`/`SK-FE-005` (both unauthored) — the only two genuine
  forward references in this entire batch.

This is the batch with the **second-fewest unauthored forward references**
of any batch so far (after CONV/INFRA's single reference), since two of
the three generics reference each other and the third mostly references
already-existing skills.

## Potential corrections

1. **This batch closes both standing DATA-domain gaps** flagged across
   two prior audits (SEARCH, SECURITY) — `SK-DATA-003` and `SK-DATA-004`
   were left unauthored in the original DATA-domain batch, and their
   recurring appearance as unauthored forward references is now resolved.
   No further DATA-domain follow-up is outstanding as of this batch.
2. **This is the second consecutive batch with zero technology-skill
   delegation**, following SECURITY — a correct reflection of these three
   skills' taxonomy design (cross-cutting/DATA-generic scope with
   implementation depth owned by already-authored technology skills)
   rather than a gap in coverage. Worth continuing to treat "no delegation
   needed" as an expected, not anomalous, batch shape whenever the
   confirmed taxonomy mapping resolves entirely to generics.
3. **The `[Synthesis: ...]`-tagged cross-cutting patterns in
   `performance-knowledge-map.md` §17 map almost one-to-one onto what
   `performance-engineering`'s Knowledge section needed** — this is the
   second batch (after SECURITY's use of `security-knowledge-map.md`'s
   own synthesis blocks) where a knowledge-map's own pre-written
   cross-cutting synthesis section served as the direct backbone for a
   generic skill's Knowledge section, rather than requiring fresh
   synthesis work. Worth treating as the expected pattern for any future
   cross-cutting generic consuming a knowledge-map document that has its
   own dedicated synthesis section.
4. **No skill in this batch was promoted to `final/`** — same standing
   gap as all ten prior batches.

## Overall assessment

All three skills are internally consistent with the specification,
taxonomy, dependency architecture, and routing architecture, and cleanly
partitioned despite covering adjacent, easily-conflated territory —
database-operations, caching-strategy, and performance-engineering each
own a genuinely distinct slice (data-access-layer mechanics; cache-layer/
invalidation design; cross-cutting diagnostic discipline and only-visible-
across-sources patterns) with explicit hand-offs rather than overlap. The
batch surfaces several genuinely load-bearing cross-cutting findings that
no single prior batch's technology skill fully captured: the "disable a
dev-mode default before shipping" pattern recurring identically across
Express's `NODE_ENV` and Mongoose's `autoIndex`; Redis functioning as
connective tissue across five independent, non-cross-referencing
integration points; N+1 avoidance converging on "batch or join" across
every data-access layer regardless of naming; connection-pool sizing
treated as a first-class quantified provisioning step across unrelated
stacks; the shared unbounded-send-buffer hazard across every real-time
transport; and the ecosystem-wide (but individually-unacknowledged) trend
of rewriting core JS/Node tooling in systems languages. This batch also
extends the SECURITY batch's precedent of reading a knowledge-map document
in full for dedicated synthesis, and — as a direct, welcome side effect of
correctly mapping the user's list against the taxonomy rather than
guessing — resolves the two longest-standing open forward-reference gaps
in this project.
