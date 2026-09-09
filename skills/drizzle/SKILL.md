---
name: Drizzle ORM
description: >-
  Drizzle ORM-specific schema (pgTable/mysqlTable/sqliteTable), the query
  builder and Relational Queries API, drizzle-kit migrations, and RLS
  (withRLS()+pgPolicy()). Use when drizzle-orm/drizzle-kit or a
  drizzle.config.ts is present, or the task names Drizzle. Critical: npm
  "latest" is 0.45.2 but the live docs already target v1.0.0-rc — confirm the
  installed line before trusting current docs. Not for other ORMs (route to
  their skill) or ORM-neutral method (orm-integration).
spec_version: "1.0"
---

## Purpose & scope

Apply Drizzle ORM correctly for the line actually installed — schema
declaration, the query builder, Relational Queries, drizzle-kit migrations,
and RLS. The general ORM method (N+1 avoidance, transactions, ORM selection)
comes from [orm-integration](../orm-integration/SKILL.md); general migration
safety (expand/contract, backfill batching) comes from
[data-migration](../data-migration/SKILL.md). This skill supplies what's
specific to Drizzle — most importantly, the fact that its API surface is
**currently split across two live version lines that don't match**.

## When to use / When not to use

**Use** when `drizzle-orm`/`drizzle-kit` or a `drizzle.config.ts` is present,
or the task names Drizzle specifically. **Do not use** for Prisma/TypeORM/
Mongoose (route to that technology skill), for ORM-neutral method with no ORM
chosen yet (`orm-integration`), or for migration-safety mechanics that don't
touch Drizzle-specific tooling (`data-migration`).

## Knowledge

**The single fact that governs everything else in this skill:** as of the
research date, the npm `latest` dist-tag for `drizzle-orm` resolves to
**0.45.2** (the stable 0.x line), while **v1.0.0 is only at release-candidate
stage** (`1.0.0-rc.4` is the newest tagged GitHub release) [Source:
https://registry.npmjs.org/drizzle-orm/latest;
https://github.com/drizzle-team/drizzle-orm/releases]. Most production
Drizzle codebases are still on 0.x — but the **live documentation site
(`orm.drizzle.team`) has already been substantially rewritten to describe v1
APIs**, with v0-specific docs largely superseded rather than kept as an
archived version. Reading the current docs and writing code against a 0.x
project without checking the pinned version is a guaranteed source of
API-mismatch bugs. Always confirm the installed line from `package.json`/the
lockfile before trusting a doc page verbatim.

**Core model: headless and SQL-proximity, not schema-file-and-generated-client.**
Drizzle describes itself as "a headless TypeScript ORM with a head" — the
schema is authored directly in TypeScript (`pgTable`/`mysqlTable`/
`sqliteTable`), and that TypeScript *is* the source of truth for both type
inference and generated migrations, with no separate schema-DSL file or
codegen step [Source: https://orm.drizzle.team/docs/overview,
https://orm.drizzle.team/docs/sql-schema-declaration]. Its stated design
philosophy is "if you know SQL, you know Drizzle" — the query builder mirrors
SQL syntax rather than hiding it behind an unfamiliar entity model [Source:
https://orm.drizzle.team/docs/overview]. Architecturally it compiles typed
calls into parameterized SQL and hands them to whichever driver was supplied
at `drizzle()` init; it implements no network protocol or pooling of its own,
delegating that to the driver (`node-postgres`, `postgres.js`, Neon HTTP/WS,
etc.) [Source: https://orm.drizzle.team/docs/overview,
https://orm.drizzle.team/docs/connect-overview]. This is also the mechanism
behind its edge/serverless story: HTTP/WebSocket driver adapters (Neon,
Vercel Postgres, PlanetScale, Cloudflare D1, Turso) let the same ORM surface
run in a stateless edge function, not just a long-lived Node process [Source:
https://orm.drizzle.team/docs/connect-overview].

**Two querying models, and relations are application-level.** The SQL-like
builder (`db.select()/.insert()/.update()/.delete()`) coexists with the
Relational Queries API (`db.query.<table>.findMany()/findFirst()`) for
ergonomic nested fetches that still compile to one SQL statement [Source:
https://orm.drizzle.team/docs/rqb]. Relations are declared separately from
the schema and are an application-level concept — they don't require or
enforce a foreign key at the database level [Source:
https://orm.drizzle.team/docs/relations]. Relation loading is explicit and
opt-in per query via `with`; nothing lazy-loads on property access
[Inference, not confirmed in docs — orm.drizzle.team/docs/relations,
/docs/rqb].

**The v0-vs-v1 relations API is the sharpest version fork in the library.**
0.x uses `relations()` + Relational Queries v1 (RQBv1). v1 removes RQBv1
**entirely**, replacing it with `defineRelations(schema, (r) => ({...}))`
using `r.one`/`r.many` builders (RQBv2) [Source:
https://orm.drizzle.team/docs/v0-v1-changes]. Code copied from current
tutorials/docs into a 0.x project will use an API that doesn't exist there,
and vice versa. Other v1-only renames: `pgTable.withRLS()` replaces
`.enableRLS()`; `getColumns()` replaces `getTableColumns()`; table-level
`snakeCase.table(...)`/`camelCase.table(...)` replace the global
`drizzle({ casing: ... })` option; `column.array('[][]')` string notation
replaces chained `.array().array()` [Source:
https://orm.drizzle.team/docs/v0-v1-changes]. Full breaking-change list and
the official upgrade path (`drizzle-orm@rc`/`drizzle-kit@rc`, then
`drizzle-kit up` to convert migration folders, then a manual — not
codemod-automated — code pass) is at
[references/v0-v1-migration-notes.md](references/v0-v1-migration-notes.md).

**Migration workflow: pick deliberately, and `push` is not for production.**
`drizzle-kit pull` introspects an existing DB into TypeScript
(database-first); codebase-first splits into `push` (direct sync, no SQL
artifact — local/prototyping only) and `generate` + `migrate` (versioned SQL
files reviewed and committed — the team/production path) [Source:
https://orm.drizzle.team/docs/migrations]. The FAQ states explicitly that
`push` is **not recommended for production databases** [Source:
https://orm.drizzle.team/docs/faq]. `push` also cannot detect changes to an
*existing* index's expression, `.where()` clause, or operator class — it
silently fails to regenerate that SQL, requiring `generate` or a manual
comment-out/push/uncomment workaround [Source:
https://orm.drizzle.team/docs/faq]. Generated migrations previously lived as
flat `migration.sql` + `snapshot.json` pairs tracked by a `journal.json`; v1
changed this to a per-migration-folder "v3 format" with `journal.json`
eliminated and `drizzle-kit drop` removed specifically to stop Git merge
conflicts [Source: https://orm.drizzle.team/docs/v0-v1-changes] — this is the
same fact `data-migration`'s reference table already documents; it is not
repeated in depth here.

## Decision framework

This extends `orm-integration`'s ORM-selection framework
(`SK-DATA-002`) with Drizzle-specific calls; it does not re-litigate the
Mongoose/TypeORM/Prisma/Drizzle comparison itself.

1. **New project — which line to target?** Default to the 0.x stable line
   unless the project can tolerate a pre-GA API (rc releases still ship
   frequently, and the docs themselves warn "something will definitely
   break" on the v1 jump [Source:
   https://orm.drizzle.team/docs/latest-releases/drizzle-orm-v1beta2]). Take
   1.0.0-rc only when the project explicitly wants v1-only features (native
   MSSQL/CockroachDB, JIT Mappers, the rewritten introspection engine) and
   accepts RC-stability risk. Do not pick a line based on what the live docs
   happen to show — that reasoning silently commits a new project to
   pre-release code.
2. **Existing project — never guess the line.** Read `package.json`/the
   lockfile. If it's ambiguous (e.g. a caret range spanning the 0.x→1.x
   boundary), ask rather than assume "latest."
3. **When is raw SQL-proximity (Drizzle) actually preferred over a
   generated-client model (Prisma)?** When the team already thinks in SQL and
   wants to see exactly what will execute (`.toSQL()` on any builder chain
   confirms this before running it [Source:
   https://orm.drizzle.team/docs/goodies]), when the deployment target is
   edge/serverless and a zero-codegen-step, HTTP-driver-friendly library
   matters, or when RLS needs to be a first-class schema construct rather
   than a Client Extension layered on top. Prefer Prisma's generated client
   instead when the team wants a strongly-typed, batteries-included
   migration workflow and is fine with a build/codegen step — see
   `orm-integration`'s full comparison for the rest of that trade-off; it is
   not restated here.
4. **Simplest first:** for local iteration, `push` is genuinely the fastest
   loop — just never let it reach a database that matters.

## Engineering rules

- Confirm the installed Drizzle line before writing or trusting any
  version-sensitive API (`defineRelations()` vs. `relations()`, `withRLS()`
  vs. `enableRLS()`, `getColumns()` vs. `getTableColumns()`).
- Use `generate` + `migrate` for any migration touching a database with real
  data; reserve `push` for local/prototyping only [Source:
  https://orm.drizzle.team/docs/faq].
- Prefer the `` sql`` `` tagged template over `sql.raw()` whenever any part of
  a raw-SQL fragment includes user-controllable input; `sql.raw()` is for
  trusted, statically-known fragments only [Source:
  https://orm.drizzle.team/docs/sql].
- Index foreign-key columns supporting Relational Queries — Drizzle has no
  dedicated N+1-avoidance feature, so relational-query performance is
  effectively an indexing discipline, not an ORM setting [Source:
  https://orm.drizzle.team/docs/relations].
- Treat `.$withCache()`/global cache mode as experimental — it doesn't cover
  raw queries, transactions, RQB, the AWS Data API driver, or views [Source:
  https://orm.drizzle.team/docs/cache]; don't rely on it as the caching layer
  for an entire application.

## Trade-offs

Drizzle's SQL-proximity model trades some ergonomic sugar (no automatic
lazy-loading, no generated client) for transparency — every query is
inspectable via `.toSQL()` and the mental model stays close to the SQL that
actually runs. Being mid-transition to v1 is itself a trade-off right now:
adopting 0.x is the safe, boring choice with a large body of matching
examples, but the project will eventually need the v0→v1 migration effort
described above; adopting 1.0.0-rc now front-loads that migration cost but
accepts pre-GA instability in the interim.

## Anti-patterns

- **Following current `orm.drizzle.team` docs/examples verbatim against a
  0.x-pinned project** — the single most likely Drizzle-specific mistake
  right now, since the live docs already describe v1 (`defineRelations()`,
  `withRLS()`, etc.) while most installed code is 0.x [Source:
  https://orm.drizzle.team/docs/v0-v1-changes]. Always check the pinned
  version first.
- **Running `drizzle-kit push` against a production database** — explicitly
  discouraged by the official FAQ; it skips the reviewable, versioned SQL
  artifact `generate`+`migrate` produces [Source:
  https://orm.drizzle.team/docs/faq].
- **Modifying an existing index's expression/`.where()`/operator class and
  expecting `push` to pick it up** — it won't; use `generate` or the
  documented comment-out/push/uncomment workaround [Source:
  https://orm.drizzle.team/docs/faq].
- **Interpolating user input into `sql.raw()`** — bypasses parameterization
  entirely and is explicitly called out as unsafe [Source:
  https://orm.drizzle.team/docs/sql].
- **Over-indexing "for the query builder" without checking the actual access
  pattern** — the domain's over-engineering trap here is treating Drizzle's
  SQL-proximity as license to hand-tune indexes speculatively rather than
  from an observed plan; the same discipline `SK-TECH-postgresql` states for
  raw Postgres applies unchanged through Drizzle.

## Security

RLS is a first-class, documented Drizzle feature on PostgreSQL: `v1`'s
`pgTable.withRLS(...)` (0.x: `.enableRLS()`) plus `pgPolicy()` — configurable
by `as` (permissive/restrictive), `for` (all/select/insert/update/delete),
`to`, and `using`/`withCheck` — with provider helpers for Neon
(`crudPolicy()`, `authenticatedRole`, `anonymousRole`, `authUid()`) and
Supabase (`authenticatedRole`, `serviceRole`, `anonRole`, `authUsers`,
`authUid()`) to wire policies into each provider's JWT-claims model [Source:
https://orm.drizzle.team/docs/rls]. Postgres' own default-deny applies once
RLS is enabled with no policy attached [Source:
https://orm.drizzle.team/docs/rls]. This is stronger first-class support than
Prisma (Client Extension pattern on native RLS through v7, native as of v8)
or TypeORM (not documented as first-class) — see `orm-integration` for that
comparison; not restated here.

`sql.raw()` is the specific injection-risk surface: it bypasses
parameterization entirely and the docs say plainly "never use ... for
user-provided data" [Source: https://orm.drizzle.team/docs/sql]. Everything
else — the `` sql`` `` template and standard query-builder methods — is
parameterized automatically. Cross-cutting threat modeling beyond this is
owned by `SK-QA-002`, referenced not restated.

## Performance

Drizzle's own framing is "a thin TypeScript layer on top of SQL with almost 0
overhead" [Source: https://orm.drizzle.team/docs/overview] — **treat this as
vendor positioning, not an independent benchmark**: no official comparative
figures against another ORM were found, and the underlying research
explicitly flags this and Prisma's "~90% of raw PostgreSQL throughput" claim
as both self-referential, not comparative [Source:
research/knowledge-maps/technology-decision-matrix.md §1]. The one
documented, concrete performance technique is prepared statements
(`.prepare()` + `sql.placeholder()`), which avoid re-parsing the same SQL
shape on repeated calls [Source:
https://orm.drizzle.team/docs/perf-queries]. The experimental caching layer
(`.$withCache()`, `upstashCache()`) auto-invalidates on mutation but
explicitly excludes raw queries, transactions, RQB, the AWS Data API driver,
and views [Source: https://orm.drizzle.team/docs/cache] — not a drop-in cache
for a whole application's query surface. Deeper cross-cutting performance
method is owned by `SK-QA-003`.

## Testing

Drizzle's officially documented test story is genuinely different from a
mocking-first approach: **PGlite** — "Postgres in WASM," runs in Node/Bun/the
browser with no Docker or Linux VM required, usable in-memory (ephemeral) or
with file-system/IndexedDB persistence — is the documented Postgres
implementation Drizzle connects to for tests [Source:
https://orm.drizzle.team/docs/connect-pglite]. Pair it with `drizzle.mock()`
for a typed `db` instance with no real connection (unit tests that need
correct typing without hitting a database) [Source:
https://orm.drizzle.team/docs/goodies], and `drizzle-seed` for deterministic,
reproducible fake data (`seed(db, { table1, table2 })`, `.refine()` for
per-table customization, `reset()` for dialect-specific clearing) [Source:
https://orm.drizzle.team/docs/seed-overview]. Note `drizzle-seed`'s
documented gaps: `with`'s type inference exposes all schema tables rather
than narrowing to valid targets, composite constraints sharing columns across
two constraints aren't supported, and non-unique generators need explicit
`isUnique` [Source: https://orm.drizzle.team/docs/seed-overview]. This
diverges sharply from Prisma's Jest-mocking-first pattern and Mongoose's
explicit anti-Jest guidance — see `orm-integration` for that cross-ORM
contrast; test-strategy method itself is owned by `SK-QA-001`.

## Failure handling

- If the installed Drizzle line can't be determined, ask rather than assume —
  applying v1 syntax to a 0.x project (or vice versa) produces code that
  won't compile/run.
- If shell is unavailable, produce advisory schema/migration/RLS-policy code
  and state plainly that `drizzle-kit` was not executed to generate or apply it.

## Escalation

- Applying a migration to a database that already has data defers to
  `data-migration`'s (`SK-DATA-006`) destructive-operation confirmation
  discipline — this skill does not add a separate gate on top of it.

## Outputs & verification

- **Outputs:** version-line-correct schema/query/relation code, a
  drizzle-kit migration or RLS policy, or an analysis of which v0-vs-v1
  caveats apply.
- **Verify:** every version-sensitive API used matches the confirmed
  installed line; any migration assumes the correct folder format for the
  installed drizzle-kit version; any `sql.raw()` usage carries only trusted
  input.

## References

- [references/v0-v1-migration-notes.md](references/v0-v1-migration-notes.md) — Tier-2: the full v0→v1 breaking-change list and official upgrade path.
- Source list: see `skill.yaml.source_references` (orm.drizzle.team official
  docs, npm registry, and GitHub releases, retrieved 2026-09-09, via
  `research/technologies/drizzle.md`).
- [research/knowledge-maps/technology-decision-matrix.md §1](../../research/knowledge-maps/technology-decision-matrix.md) — cross-ORM comparison (owned by `orm-integration`).
- [data-migration/references/version-sensitive-migrations.md](../data-migration/references/version-sensitive-migrations.md) — the migration-folder-format caveat as documented for migration planning.
