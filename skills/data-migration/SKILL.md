---
name: Data migration
description: >-
  Author and run safe schema/data migrations on a populated database —
  reversible steps, zero-downtime expand/contract, backfill strategy, and
  guarding destructive operations behind confirmation. Use for a schema
  change on a database with existing data. Not for greenfield schema design
  (data-modeling) or broad technology/codebase modernization.
spec_version: "1.0"
---

## Purpose & scope

Change a schema that already has data on it, safely: reversible steps,
zero-downtime rollout where it matters, a real backfill strategy for large
tables, and destructive operations that never run without explicit
confirmation. This skill assumes the target shape is already decided
([data-modeling](../data-modeling/SKILL.md) or an ORM's schema definition via
[orm-integration](../orm-integration/SKILL.md)) — it owns getting there
safely, not deciding where "there" is. Broad technology/pattern
modernization beyond a single migration belongs to legacy-modernization (not
yet authored in this library).

## When to use / When not to use

**Use** for any schema change on a database that already holds data, or when
a version upgrade carries a breaking schema-relevant change. **Do not use**
for a greenfield schema with nothing to preserve (go straight to
data-modeling), or for a broad modernization effort spanning more than one
migration's worth of change.

## Knowledge

**A migration on live data is a live-fire operation.** The two failure modes
that matter are (1) irreversibility — you can't get back to the prior state
if something goes wrong, and (2) blocking — a migration that locks a table
long enough to cause an outage. Both are avoidable with discipline, not luck.

**Expand/contract is the standard pattern for zero-downtime schema changes.**
Rather than changing a column/table in place, add the new shape alongside the
old one (*expand*), migrate reads and writes to the new shape while both
exist, backfill existing data, then remove the old shape once nothing
references it (*contract*). Each phase is independently deployable and
reversible; collapsing expand and contract into one step is what turns a
routine migration into an outage risk.

**Large backfills must be batched.** Updating every row of a large populated
table in one statement holds a lock for the duration and can block
production traffic. Batch it — a bounded number of rows per transaction,
with a pause or rate limit between batches — even though it takes longer wall-clock.

**Version upgrades sometimes carry migration-relevant breaking changes that
aren't optional.** This library's research recorded several concrete ones
worth checking before assuming "just run the migration" is safe:

- **Prisma:** MongoDB support is **not available in Prisma 7** — the official
  docs explicitly instruct MongoDB users on Prisma to "continue using Prisma
  ORM v6 for now," with MongoDB support planned to return via Prisma 8
  [Source: version-matrix.md, Prisma]. A migration plan that assumes Prisma 7
  against a MongoDB target is broken before it starts.
- **Drizzle:** the v1 line removed Relational Queries v1 entirely (replaced
  by `defineRelations()`), and changed the migration folder structure —
  `journal.json` was eliminated and `drizzle-kit drop` was removed. Most
  production codebases are still on the 0.x line even though the live docs
  are already written for v1 — check which line is actually pinned before
  following current docs literally [Source: version-matrix.md, Drizzle ORM].
- **TypeORM:** v1.0.0 (2026-05-19) requires Node ≥ 20, drops the legacy
  `mysql` driver in favor of `mysql2` only, and switches the SQLite default
  to `better-sqlite3` — a migration touching driver-level behavior on an
  older TypeORM codebase should confirm the version line first
  [Source: version-matrix.md, TypeORM].
- **MySQL:** 8.4.0 removed (not deprecated) `AUTO_INCREMENT` on
  `FLOAT`/`DOUBLE` columns — tables using it **must be altered before
  upgrading**, or the table cannot be upgraded at all
  [Source: version-matrix.md, MySQL].

Full migration-relevant version detail (including MongoDB's
`featureCompatibilityVersion` sequencing and ClickHouse's node-skew limits)
is in [references/version-sensitive-migrations.md](references/version-sensitive-migrations.md).

## Decision framework

1. **Does this need zero downtime?** If the table is small or a maintenance
   window is acceptable, a simpler direct migration may be fine. If not,
   expand/contract is the default, not an optional refinement.
2. **Is the step reversible?** If yes, proceed with a stated rollback path.
   If genuinely not (e.g., a lossy data transform), that's the trigger for
   explicit human confirmation before running it — not a reason to skip planning a rollback, just an honest statement that none exists.
3. **How large is the table being backfilled?** Above a size where a single
   transaction would hold a meaningful lock, batch it.
4. **Does the target ORM/database version carry a relevant breaking change?**
   Check the version-sensitive facts (§Knowledge) before assuming current
   docs apply unmodified to the version actually pinned in the project.

## Workflow

1. Confirm the target schema (hand off to data-modeling if not yet decided).
2. Check for a version-specific migration caveat relevant to the ORM/database in play.
3. Design the expand/contract sequence (or confirm a simpler direct migration is safe).
4. Write the migration as reversible steps (up and down).
5. For large tables, batch the backfill.
6. Flag any irreversible/destructive step explicitly and stop for confirmation before it runs.
7. State the rollback plan alongside the migration, not as an afterthought.

## Engineering rules

- Every migration has a stated rollback path, or an explicit, honest
  statement of why one isn't possible.
- Backfills over populated tables are batched, never a single blocking pass.
- Never run a destructive step (DROP, data-losing ALTER, irreversible
  transform) without explicit user confirmation — regardless of technical capability to do so.
- Check version-sensitive migration caveats before trusting current docs against a pinned older version.
- Keep expand and contract as separate, independently deployable steps.

## Trade-offs

Expand/contract is safer and more deployable but takes more total steps and
calendar time than a direct in-place change. A direct migration is faster to
write but risks downtime and has no natural rollback boundary once applied.
Choose based on the table's size, traffic, and how much downtime is actually
tolerable — not by default to either extreme.

## Anti-patterns

- **Collapsing expand and contract into one deploy** — removing the old
  shape before every consumer has moved to the new one.
- **Single-transaction backfill on a large populated table** — locks the
  table for the duration, risking an outage.
- **A migration with no rollback path and no acknowledgment of that fact** —
  silently irreversible is worse than explicitly irreversible.
- **Assuming current docs apply to a pinned older version** without checking
  for a version-specific breaking change (see the Prisma/MongoDB and Drizzle
  examples in Knowledge) — this is the domain's overengineering-adjacent
  trap in reverse: under-checking, not over-building.
- **Running a destructive step because it was technically possible**, without confirmation.

## Failure handling

- If the target schema isn't clear, request it or hand off to data-modeling
  rather than migrating toward a guess.
- If shell/migration-tool execution isn't available, produce the migration
  script and rollout plan as advisory output, clearly marked as not executed.

## Escalation

- Any step that can lose data (a DROP, a destructive ALTER, an irreversible
  transform) requires explicit user confirmation before it runs — never
  executed automatically, even when the capability to run it exists.

## Outputs & verification

- **Outputs:** a reversible migration script (up/down) and an expand/contract
  rollout plan with rollback points.
- **Verify:** a working rollback path exists or its absence is explicitly
  stated; no data is dropped/overwritten without confirmation; large
  backfills are batched.

## References

- [references/version-sensitive-migrations.md](references/version-sensitive-migrations.md) — Tier-2 per-technology migration version caveats.
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md)
