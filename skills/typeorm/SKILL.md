---
name: TypeORM
description: >-
  TypeORM's DataSource/EntityManager/Repository/QueryRunner architecture,
  Active Record vs Data Mapper choice, decorator-driven entities, per-driver
  isolation levels, and the live 0.3.x-vs-1.0 version split (Node>=20,
  mysql2-only, better-sqlite3 default, Mongo driver v7+). Use when the stack
  uses TypeORM specifically. Not for ORM/ODM selection or cross-ORM
  N+1/transaction method (orm-integration), and not for migration safety
  mechanics (data-migration).
spec_version: "1.0"
---

## Purpose & scope

Apply TypeORM correctly and version-appropriately: its Active Record/Data
Mapper duality, its `DataSource`/`EntityManager`/`Repository`/`QueryRunner`
architecture, and — critically — the fact that TypeORM currently ships as
**two simultaneously live version lines** (0.3.x and 1.0+) rather than one
settled current version. The generic ORM method (N+1 avoidance, transaction
discipline, ORM/ODM selection) is [orm-integration](../orm-integration/SKILL.md)'s;
migration safety mechanics (expand/contract, backfill batching) are
[data-migration](../data-migration/SKILL.md)'s. This skill supplies
TypeORM's concrete, version-correct specifics on top of both.

## When to use / When not to use

**Use** when the `typeorm` package, `@Entity`/`@Column` decorators, or a
`DataSource` config is present, or the task names TypeORM specifically
(Active Record vs. Data Mapper, `EntityManager`/`Repository`/`QueryRunner`,
or the 0.3.x-to-1.0 boundary). **Do not use** for ORM/ODM selection itself or
cross-ORM N+1/transaction method with no TypeORM-specific API involved (route
to orm-integration), or for migration safety mechanics with no TypeORM API
question (route to data-migration).

## Knowledge

**Pattern choice is explicit, not implicit.** TypeORM supports Active Record
and Data Mapper simultaneously and lets the developer choose how database
logic is written [Source: https://typeorm.io/docs/getting-started/]. Under
Data Mapper, all operations go through an `EntityManager` (all entities) or a
`Repository` (scoped to one entity type, obtained via
`dataSource.getRepository(Entity)`) [Source:
https://typeorm.io/docs/working-with-entity-manager/working-with-repository/].
Under Active Record, entity classes extend a base class and call methods like
`.save()` on themselves directly [Source:
https://typeorm.io/docs/getting-started/]. orm-integration already covers the
cross-ORM N+1/caching comparison for TypeORM among the other three ORMs —
what follows is specific to TypeORM's own architecture and not restated
there.

**Architecture beyond Repository/EntityManager:** `DataSource` is the sole
connection/config entry point as of v1.0 (the legacy `Connection` class was
removed) [Source: https://typeorm.io/docs/getting-started/;
https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/]. `QueryRunner`
provides a single dedicated connection and is what transactions are organized
around — "a single transaction can only be established on a single query
runner," and manually created query runners must be explicitly `.release()`d
[Source: https://typeorm.io/docs/transactions/]. TypeORM also ships
`TreeRepository` (for `@Tree`-marked entities) and `MongoRepository`
(MongoDB-specific) as repository subtypes [Source:
https://typeorm.io/docs/working-with-entity-manager/working-with-repository/].

**Entity/column features beyond the basics:** composite primary keys via
multiple `@PrimaryColumn()` decorators; generated columns
(`@Generated("uuid")`/`@Generated("increment")`); vector columns for
embeddings and spatial (well-known-text) columns on supported databases; and
entity inheritance, where a base class's columns are inherited into concrete
entities [Source: https://typeorm.io/docs/entity/entities/].

**Isolation-level support is driver-dependent and enforced.** TypeORM throws
if an unsupported isolation level is requested for the active driver.
Documented per-driver support: Postgres/MySQL/MariaDB/SAP HANA (READ
UNCOMMITTED–SERIALIZABLE); MS SQL Server (adds SNAPSHOT); Oracle (READ
COMMITTED and SERIALIZABLE only); CockroachDB (READ COMMITTED/REPEATABLE
READ/SERIALIZABLE, SERIALIZABLE default); Google Spanner (REPEATABLE
READ/SERIALIZABLE); SQLite (READ UNCOMMITTED and SERIALIZABLE only); Aurora
MySQL via the RDS Data API supports no isolation levels at all [Source:
https://typeorm.io/docs/transactions/].

**The v1.0/0.3.x split is a live fork, not a completed migration.** v1.0.0
(2026-05-19) is the sole documented major-version boundary and is billed as
carrying breaking changes vs. 0.3.x — but the 0.3.x line kept receiving
parallel backports (e.g. 0.3.31 on 2026-07-13) *after* 1.0.0 shipped, and no
official end-of-support date for 0.3.x has been published [Source:
https://github.com/typeorm/typeorm/releases]. Both lines are simultaneously
live; confirm which one a codebase is actually pinned to before applying
either line's guidance. **[Version-sensitive: 0.3.x remains actively
backported as of 2026-09-09, with no announced sunset.]**

**v1.0 breaking changes worth knowing beyond the driver swaps.**
data-migration already documents the driver-level v1.0 changes (Node>=20,
`mysql2`-only, `better-sqlite3` default, Mongo driver v7+) as a worked
migration example — not repeated here. Additional API-level changes:
`findOneById()`, `findByIds()`, and `exist()` are removed in favor of
`findOneBy()`, `findBy()` + `In()`, and `exists()`; string-based
`select`/`relations` arrays and the find-options `join` property are removed
in favor of object-syntax `relations` (LEFT JOIN) or QueryBuilder (other join
types); QueryBuilder's `printSql()`/`onConflict()`/`setNativeParameters()`
are removed in favor of `getSql()`/`orIgnore()`/`orUpdate()`; non-nullable
relations now default to `INNER JOIN` instead of `LEFT JOIN`;
`invalidWhereValuesBehavior` now defaults to `throw`, so `null`/`undefined`
in a `where` condition errors instead of silently matching nothing; the
built-in IoC container is removed (integrate TypeDI/NestJS externally); and
an automated codemod (`npx @typeorm/codemod v1 src/`) mechanizes most of this
[Source: https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/;
https://typeorm.io/docs/releases/1.0/release-notes/]. **[Version-sensitive:
0.3.x → 1.0.0 boundary, effective 2026-05-19.]**

**Platform reach beyond Node.js** includes Browser (via `sql.js`),
Cordova/Ionic, Expo, NativeScript, React Native, and Electron, each with its
own caveats — e.g. NativeScript requires 4.x+ and compulsory Webpack
bundling, since the raw `typeorm/browser` package is unbundled ES7 that
"will NOT run as it is" without a bundler [Source:
https://typeorm.io/docs/help/supported-platforms/]. **[Version-sensitive:
NativeScript 4.x+ requirement.]**

**Project governance is a live consideration for new production adoption.**
TypeORM's own blog states maintenance "had slowed significantly" in recent
years and describes a governance transition (new lead maintainers, a planned
non-profit foundation, sponsor-funded developers) — self-reported, not
independently corroborated elsewhere [Source:
https://typeorm.io/blog/future-of-typeorm].

## Decision framework

1. **Active Record vs. Data Mapper — pick per project convention, don't mix
   arbitrarily.** Data Mapper (`EntityManager`/`Repository`) keeps
   persistence logic out of entity classes and suits larger, more
   test-driven codebases; Active Record (`.save()` on the entity itself) is
   lower-ceremony for small apps/scripts where the extra separation isn't
   paying for itself [Source: https://typeorm.io/docs/getting-started/]. If
   the codebase already picked one, stay in it — don't propose a mid-project
   switch opportunistically (mirrors orm-integration's anti-switching rule).
2. **Simplest first, greenfield case:** Active Record with `synchronize:
   true` in local dev only is the lowest-ceremony start — but `synchronize`
   / `dropSchema` must never run against a database holding real data
   [Source: https://typeorm.io/docs/data-source/data-source-options/;
   https://typeorm.io/docs/migrations/why/]; move to migrations
   (data-migration) as soon as there's data worth preserving.
3. **Adopt v1.0 now, or stay on 0.3.x?** Both lines are simultaneously live
   with no announced 0.3.x end-of-support date, so staying on 0.3.x is a
   legitimate choice — not laziness — when: the project can't yet move to
   Node >=20, depends on the removed `mysql` (not `mysql2`) driver or
   `sqlite3`, or has no active need for a v1.0-only feature (`valuesFromSelect()`,
   Postgres partial indexes, SQLite `jsonb`, `await using` support). Move to
   1.0+ when starting greenfield, when already on Node>=20 with
   `mysql2`/`better-sqlite3`, or when a specific v1.0 feature is actually
   needed — and use `@typeorm/codemod` to cut manual rework [Source:
   https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/]. Don't upgrade
   opportunistically inside an unrelated task; this is codebase-wide (see
   Escalation).
4. **Isolation level:** set a sensible `isolationLevel` default at the
   DataSource level and override per-transaction only when a specific
   correctness requirement demands it (e.g. `SERIALIZABLE` for an
   invariant-sensitive write) — confirm the active driver actually supports
   the requested level first (Knowledge), rather than assuming portability
   across drivers [Source: https://typeorm.io/docs/transactions/].

## Workflow

1. Determine which TypeORM line the codebase is pinned to (0.3.x or 1.x) and
   its Node.js major version — this gates which API/driver guidance applies.
2. Determine the existing pattern (Active Record or Data Mapper) if the
   codebase already has one; don't force a switch.
3. For entity/relation work, use the version-correct find-options syntax
   (object `relations`, not string arrays, on 1.x) and avoid N+1 via
   `leftJoinAndSelect`/the `relations` object (cross-ORM method owned by
   orm-integration).
4. For transactional work, use the callback-scoped `dataSource.transaction(...)`
   API and the transactional entity manager it provides — never the global
   manager inside that callback [Source:
   https://typeorm.io/docs/transactions/].
5. For schema changes on populated data, hand off to data-migration; never
   rely on `synchronize: true` once real data exists.
6. If a version-line question or a v1.0 breaking change surfaces, check
   Knowledge above before assuming current typeorm.io docs describe the
   pinned version's actual behavior.

## Engineering rules

- Confirm the TypeORM version line before naming a Repository/QueryBuilder
  method — `findOneById`/`findByIds`/`exist()` (0.3.x) and
  `findOneBy`/`findBy`+`In()`/`exists()` (1.x) are not interchangeable
  [Source: https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/].
- Never enable `synchronize: true` or `dropSchema: true` against a database
  holding real data — both are explicitly documented as data-loss-prone
  [Source: https://typeorm.io/docs/data-source/data-source-options/].
- Inside `dataSource.transaction(callback)`, use only the transactional
  entity manager the callback provides — never the global manager [Source:
  https://typeorm.io/docs/transactions/].
- Don't set `eager: true` on both sides of the same relationship — TypeORM
  disallows it [Source:
  https://typeorm.io/docs/relations/eager-and-lazy-relations/].
- Treat lazy relations (`Promise<T>`-typed properties) as
  experimental/non-standard, not a default choice — the docs flag them as
  such [Source: https://typeorm.io/docs/relations/eager-and-lazy-relations/].
- Load a relation explicitly before relying on cascade-remove — TypeORM only
  cascades populated relations [Source:
  https://typeorm.io/docs/relations/relations/].
- Verify a requested isolation level is supported by the active driver before
  using it — TypeORM throws on an unsupported level rather than silently
  degrading [Source: https://typeorm.io/docs/transactions/].

## Trade-offs

Active Record is less ceremony but couples persistence to the entity class
and is harder to unit-test in isolation from the database; Data Mapper adds a
layer (`Repository`/`EntityManager`) but keeps entities as plain data shapes,
which pays off as the codebase grows. Staying on 0.3.x avoids the Node>=20 /
driver-swap migration cost but forgoes v1.0's extended parameterization/escaping
on schema-introspection and DDL paths and its `invalidWhereValuesBehavior`
safety default; moving to 1.0+ gains those but requires the Node floor and
driver changes to already be true for the project.

## Anti-patterns

- **Applying v1.0 driver/API requirements (`mysql2`-only, `better-sqlite3`
  default, `findOneBy`) to a codebase actually pinned to 0.3.x — or the
  reverse**, assuming 0.3.x's `findOneById`/string-array find-options still
  work on a 1.x install. Both lines are live simultaneously; confirm which
  one is pinned before giving guidance — this is the version-boundary trap
  specific to this skill.
- **Assuming TypeORM's parameterization covers identifier or
  SQL-expression-position input.** Its security guarantee is scoped to data
  values through documented APIs; identifier/expression-position input and
  hostile schema/config control are explicitly out of scope per TypeORM's own
  security policy — treating the ORM as a blanket injection shield is the
  over-trusting version of this trap (see Security).
- **Mixing the global `EntityManager`/`Repository` into code meant to run
  inside a transaction** — silently breaks the transaction boundary; the
  docs call this out directly.
- **Leaving `synchronize: true` enabled past local development.**
- **Reaching for Data Mapper's full Repository ceremony on a five-table
  script, or Active Record on a large multi-team codebase that needs entities
  kept as plain data** — pick the pattern for the project's actual size, not
  by default to whichever tutorial was read first (this domain's
  over-engineering trap, in both directions).

## Security

Parameterized queries and escaped identifiers are used across all drivers for
schema-introspection and DDL methods as of v1.0 — a hardening the release
notes frame as new relative to earlier 0.3.x scope [Source:
https://typeorm.io/docs/releases/1.0/release-notes/]. **The guarantee is
explicitly scoped to data values, not identifiers or SQL-expression
positions**: TypeORM's own security policy lists untrusted input in
identifier/SQL-expression positions, hostile schema definitions/configuration
control, and bypasses of optional runtime validation guards as out of scope —
the developer's responsibility, not TypeORM's [Source:
https://github.com/typeorm/typeorm/security/policy].
`invalidWhereValuesBehavior: throw` (v1.0 default) is itself a
security-relevant change: `null`/`undefined` in a `where` clause now errors
instead of silently matching unintended rows [Source:
https://typeorm.io/docs/releases/1.0/release-notes/]. Cross-cutting threat
modeling is owned by security-engineering (referenced from orm-integration);
not restated here.

## Performance

Prefer cursor-based pagination over offset/`limit`+`offset` for large or
frequently-changing result sets — the docs recommend it for "more efficient
handling of dynamic data" [Source:
https://typeorm.io/docs/performance-optimization/pagination/]. Query-result
caching (`cache: true`; the cross-ORM comparison already lives in
orm-integration) defaults to a 1000ms lifetime and can be overridden per
query (`.cache(60000)`, or a named cache ID + TTL for selective invalidation
via `queryResultCache.remove()`); production deployments should prefer a
Redis/IORedis(Cluster) backend over the default database-table store, with
`ignoreErrors` set so a cache-layer outage degrades to direct queries instead
of failing requests [Source: https://typeorm.io/docs/query-builder/caching/].
Cross-cutting performance method is owned by the testing/QA skill referenced
from orm-integration; not restated here.

## Testing

No dedicated official TypeORM testing guide exists on typeorm.io — direct
navigation and targeted search both came up empty during this skill's
underlying research pass; any Jest/in-memory-SQLite guidance in circulation
is third-party/community-sourced, not official (research/technologies/typeorm.md
§9). Treat a pattern like an in-memory `better-sqlite3` DataSource with
`synchronize: true` for integration tests as a plausible inference from
adjacent documented features (the SQLite default driver, `synchronize`), not
an officially endorsed testing pattern — say so explicitly if proposing it.
Test-strategy ownership itself belongs to the testing/QA skill referenced
from orm-integration; not restated here.

## Failure handling

- If the TypeORM version line (0.3.x vs. 1.x) is unknown, ask or check
  `package.json` before giving Repository/QueryBuilder/driver guidance — the
  two lines have materially different API surfaces.
- If shell is unavailable, produce advisory entity/DataSource/migration code
  and state that it was not run against a real DataSource.

## Escalation

- Recommending an upgrade from 0.3.x to 1.x is a codebase-wide breaking
  change (Node floor, driver swaps, removed APIs) — surface the concrete diff
  and get explicit confirmation before applying the codemod or hand-editing.

## Outputs & verification

- **Outputs:** entity/Repository/QueryBuilder code correct for the pinned
  version line, DataSource/migration configuration, and (when relevant) a
  0.3.x-to-1.0 upgrade analysis.
- **Verify:** any named Repository/QueryBuilder API matches the version line
  in use; the relation-loading strategy avoids N+1 without `eager: true` on
  both sides of a relation; `synchronize`/`dropSchema` are never left `true`
  for a production target.

## References

- [research/technologies/typeorm.md](../../research/technologies/typeorm.md) — primary research source for this skill.
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md) — TypeORM version-boundary row.
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md) — §1 cross-ORM comparison (owned by orm-integration).
- Source list: see `skill.yaml.source_references` (TypeORM official docs and GitHub, retrieved 2026-09-09).
