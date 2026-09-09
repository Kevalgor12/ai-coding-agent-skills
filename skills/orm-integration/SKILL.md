---
name: ORM integration
description: >-
  Model relations through an ORM/ODM, avoid N+1 and other ORM pitfalls, handle
  transactions correctly, and choose between Mongoose/TypeORM/Prisma/Drizzle
  when that choice is open. Use when working through an ORM/ODM. Not for
  schema design itself (data-modeling), not for raw-SQL-only work with no ORM,
  and not for migration mechanics (data-migration).
spec_version: "1.0"
---

## Purpose & scope

Work through an ORM/ODM correctly regardless of which one — relation
modeling that avoids N+1, transactions that are actually atomic, and knowing
when the ORM is the wrong tool for a specific query. This skill also makes
the ORM-selection call when it's open. It assumes the schema itself is
already designed ([data-modeling](../data-modeling/SKILL.md)) and hands off
migration mechanics to [data-migration](../data-migration/SKILL.md). The
concrete, version-correct API of each ORM belongs to its technology skill;
this skill owns what's true *regardless* of which one is in use.

## When to use / When not to use

**Use** when code is being written/reviewed against an ORM/ODM, when an ORM
choice is open, or when N+1/relation-loading/transaction correctness is in
question. **Do not use** for raw-SQL-only work with no ORM in play, for
schema design itself, or for migration authoring/execution mechanics.

## Knowledge

**All four ORMs in this library's research target different footprints, not
just different syntax.** Mongoose is MongoDB-only (an ODM, not a SQL ORM);
TypeORM, Prisma, and Drizzle all target SQL databases via drivers, with
different underlying models — TypeORM offers both Active Record and Data
Mapper patterns; Prisma generates a type-safe client from a schema file (as
of Prisma 8, the schema is emitted as a JSON "contract"); Drizzle is
explicitly "headless," a thin SQL-proximity query builder — "if you know SQL,
you know Drizzle" [Source: technology-decision-matrix.md §1]. None of the
four publish a direct feature-comparison against the others — the
"alternative" relationships in this library's research are inferred from the
*absence* of a migration guide between them, not a documented head-to-head
[Source: technology-decision-matrix.md §1].

**N+1 mitigation is real but differently shaped per ORM**
[Source: technology-decision-matrix.md §1]:
- Mongoose: `.populate()` with `select` to limit fields; avoid `perDocumentLimit`.
- TypeORM: `leftJoinAndSelect`/`innerJoinAndSelect` or a `relations` object.
- Prisma: `include` for eager-load, or batch with `WHERE id IN (...)`.
- Drizzle: not documented as a dedicated N+1 feature — guidance instead centers on indexing foreign-key columns for relational-query performance.

**Injection defense differs in shape, and one has a real CVE worth knowing.**
Mongoose's `sanitizeFilter` is *off by default* and wraps `$`-prefixed keys;
**CVE-2026-42334** (CVSS 7.5) found it failed to recursively sanitize inside
`$nor`, allowing NoSQL injection even with the flag enabled — patched in
`^6.13.9`/`^7.8.9`/`^8.22.1`/`^9.1.6` [Source: technology-decision-matrix.md
§1; GHSA-wpg9-53fq-2r8h]. TypeORM, Prisma, and Drizzle all parameterize by
default, each with a documented raw-SQL escape hatch that is explicitly
flagged as the injection-risk surface if fed unsanitized input.

**Testing philosophy diverges enough that one script won't fit all four**
[Source: technology-decision-matrix.md §1, synthesis]: Mongoose's own docs
*explicitly discourage Jest* ("We strongly recommend using a different
testing framework, like Mocha"); Prisma documents Jest + `ts-jest` +
`jest-mock-extended` as its unit-test pattern; Drizzle documents **PGlite**
(an in-memory/persistent WASM Postgres, no Docker needed) plus
`drizzle.mock()` and `drizzle-seed`. Check which ORM is in play before
scaffolding tests for it.

**Know when to drop to raw SQL.** An ORM optimizes for the common case; a
genuinely complex query (a recursive CTE, a window function the query builder
doesn't expose cleanly) is often clearer and more correct written as raw
parameterized SQL through the ORM's escape hatch than forced into an awkward
ORM-only expression. This isn't a failure of the ORM — every one of the four
documents a raw-SQL path for exactly this reason.

Full ORM comparison table (injection defense, RLS support, caching,
performance framing, official test stance) is in
[references/orm-comparison.md](references/orm-comparison.md).

## Decision framework

1. **What store family is in play?** MongoDB → Mongoose is the only
   researched fit. SQL (Postgres/MySQL/SQLite, etc.) → TypeORM, Prisma, or
   Drizzle are all eligible.
2. **Among the SQL-targeting three, what does the project value most?**
   Maximum SQL proximity / minimal abstraction / edge-runtime footprint →
   Drizzle. A generated, type-safe client with a batteries-included migration
   workflow → Prisma. Flexibility between Active Record and Data Mapper
   patterns, or an existing TypeORM codebase → TypeORM. None of these is
   backed by a documented comparative performance number — don't manufacture
   one; the vendor-stated performance framing ("~90% of raw PostgreSQL
   throughput" for Prisma, "almost 0 overhead" for Drizzle) is
   self-referential, not comparative [Source: technology-decision-matrix.md §1].
3. **Does the codebase already use one?** Work within the existing choice
   unless the user explicitly asks to evaluate a switch — switching ORMs is
   expensive and disruptive; don't propose it opportunistically.
4. **Is this specific query actually well-served by the ORM, or should it be
   raw SQL?** If the ORM's abstraction is fighting the query more than
   helping it, use the documented raw-SQL escape hatch, parameterized.

## Workflow

1. Confirm the store family and existing ORM choice (if any).
2. If choosing an ORM, apply the decision framework and record the trade-off.
3. Model relations with the loading strategy that avoids N+1 for the actual access pattern.
4. Wrap multi-step writes that must be atomic in the ORM's transaction mechanism.
5. For a query the ORM handles awkwardly, drop to its raw-SQL escape hatch, parameterized — never string-built.
6. Hand off migration authoring to [data-migration](../data-migration/SKILL.md).

## Engineering rules

- Never introduce an N+1 pattern; use the ORM's documented eager-load/batch mechanism.
- Wrap atomic multi-step writes in a real transaction, not sequential independent calls.
- Any raw-SQL escape hatch is parameterized; never string-concatenated with user input.
- Don't propose switching ORMs opportunistically — that's a significant decision requiring explicit confirmation.
- Match the ORM's own documented testing approach rather than assuming one universal test setup works for all four.

## Trade-offs

A generated, type-safe client (Prisma) trades some runtime overhead and a
build step for strong guarantees and migration tooling. A near-zero-abstraction
query builder (Drizzle) trades some ergonomics for SQL transparency and edge
footprint. Active Record/Data Mapper flexibility (TypeORM) trades a larger
surface area for adaptability to different team preferences. None of these
trade-offs is free; pick based on what the project actually needs, not on
default familiarity.

## Anti-patterns

- **N+1 queries from naive relation access** — looping over a collection and
  querying per item instead of using the ORM's batch/eager-load mechanism.
- **Multi-step writes with no transaction** — an update that should be atomic
  left as separate calls, risking partial application on failure.
- **String-built raw SQL through an ORM's raw-query escape hatch** — defeats
  the parameterization the ORM otherwise provides by default.
- **Forcing every query through the ORM's abstraction** even when a query is
  clearly better expressed as raw SQL — the domain's overengineering trap
  here is abstraction purity over clarity.
- **Switching ORMs without being asked** — a disruptive, expensive change proposed opportunistically.

## Security

Mongoose's `sanitizeFilter` is off by default and had a real, patched CVE
(CVE-2026-42334) in its `$nor` handling — verify the patched version is in
use rather than assuming the flag alone is sufficient. TypeORM, Prisma, and
Drizzle all parameterize by default; their risk surface is specifically the
raw-query escape hatch, which must never receive unsanitized input
[Source: technology-decision-matrix.md §1]. Row-level security support also
differs sharply: Drizzle offers first-class RLS (`pgTable.withRLS()` +
`pgPolicy()`); Prisma implements it via a Client Extension pattern layered on
native Postgres RLS (v6/v7) with native RLS support added in Prisma 8; TypeORM
does not document it as a first-class feature [Source:
technology-decision-matrix.md §1]. Deep threat modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Query-result caching support differs: TypeORM has built-in `cache:true`
(Redis/IORedis or DB-table backed); Drizzle has an experimental
`.$withCache()`/global cache mode with Upstash Redis integration; Prisma has
no built-in result cache, instead offering "Query Insights" for slow-query
identification (Prisma Postgres only) [Source: technology-decision-matrix.md
§1]. None of the four's self-reported performance framing is a validated
comparative benchmark — treat vendor performance claims as directional, not authoritative.

## Testing

See §Knowledge — the four ORMs sit on genuinely different official testing
philosophies (Mongoose discourages Jest; Prisma documents a Jest-based mocking
pattern; Drizzle documents an embedded-Postgres pattern via PGlite; TypeORM
has no dedicated official testing guide at all, per the underlying research
[Source: technology-decision-matrix.md §1]). Check which ORM is in play
before assuming a test-setup pattern; deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If the store family isn't yet known, ask before recommending an ORM — the
  store gates eligibility (Mongoose is MongoDB-only).
- If an ORM is already in the codebase, work within it rather than proposing a switch unasked.

## Escalation

- Recommending a switch away from an existing ORM choice is surfaced with
  trade-offs for explicit user confirmation, never applied unilaterally.

## Outputs & verification

- **Outputs:** an ORM recommendation with trade-offs (when open), correctly
  modeled relations, and correct transaction handling.
- **Verify:** no N+1 pattern introduced; atomic writes are actually
  transactional; any raw-SQL escape hatch is parameterized.

## References

- [references/orm-comparison.md](references/orm-comparison.md) — Tier-2 full comparison table.
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
