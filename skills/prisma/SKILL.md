---
name: Prisma
description: >-
  Prisma's schema-to-generated-client model, Prisma Migrate, driver
  adapters/Rust-free architecture, and the v6-vs-v7-vs-v8(RC) version split —
  critically, MongoDB is unsupported in v7. Use when the stack has a
  schema.prisma/prisma.config.ts file, @prisma/client, or the task names
  Prisma. Not for other ORMs, generic ORM patterns (orm-integration), or
  migration safety mechanics (data-migration).
spec_version: "1.0"
---

## Purpose & scope

Apply Prisma correctly for the major version actually pinned in the project:
the schema-file-to-generated-client model, Prisma Migrate, driver
adapters/the Rust-free architecture, and the version-gated differences across
v6, v7, and the v8 release-candidate line. Generic ORM method (N+1 avoidance,
transaction handling, when to choose Prisma over another ORM) is owned by
[orm-integration](../orm-integration/SKILL.md); migration *safety* mechanics
(expand/contract, backfill batching, rollback discipline) are owned by
[data-migration](../data-migration/SKILL.md). This skill assumes Prisma has
already been chosen and the store family is already known.

## When to use / When not to use

**Use** when a `schema.prisma` file, a `prisma/schema/` directory, a
`prisma.config.ts`, or `@prisma/client`/`@prisma/adapter-*` is present, or the
task names Prisma. **Do not use** for a different ORM with no Prisma present,
for ORM-agnostic patterns (route to `orm-integration`), or for migration
safety mechanics independent of Prisma's own CLI (route to `data-migration`).

**Load-bearing fact for activation:** if the store is MongoDB, this skill
still activates, but its guidance must target **v6**, not v7 — MongoDB is not
supported in Prisma ORM v7 at all, and the official docs explicitly instruct
MongoDB users to "continue using Prisma ORM v6 for now" [Source:
prisma.io/docs/guides/upgrade-prisma-orm/v7]. A recommendation that assumes
"use the latest stable Prisma" without checking the store first is wrong for
every MongoDB-backed project until v8 restores support.

## Knowledge

**The core model (v6/v7, current production shape):** a `schema.prisma` file
(or, since **v6.7.0**, multiple `.prisma` files under `prisma/schema/`)
written in Prisma Schema Language declares `datasource` and `generator`
blocks plus data models; `prisma generate` derives **Prisma Client**, a
generated, type-safe query builder, from that schema; **Prisma Migrate**
turns schema diffs into versioned SQL migration files [Source:
prisma.io/docs/orm/v7/overview/introduction/what-is-prisma]. Naming
convention: PascalCase singular model names, camelCase fields; `@map`/`@@map`
let the PSL-facing name diverge from the underlying DB column/table name
[Source: prisma.io/docs/orm/v7/more/best-practices].

**Prisma 8 (pre-GA) reconceives this as a "contract":** instead of a
generated client *package*, the schema is emitted as a JSON document plus
TypeScript types that the app, migration tooling, and coding agents all read
[Source: prisma.io/docs]. Queries move from `prisma.user.findMany({ where:
{...} })` nested-object calls to a chained builder — `db.orm.public.User
.where(...).include(...).orderBy(...).take(10).all()` [Source:
prisma.io/docs/orm/reference/orm-client]. **Unresolved:** that exact example
still shows `take()`/`skip()`, but the `v8.0.0-rc.7` changelog entry renamed
pagination to `limit()`/`offset()` — these two official sources currently
disagree, and which shape ships in the final v8.0.0 GA is not settled. Verify
against the exact `prisma` version pinned before writing v8 pagination code
[Source: GitHub Releases, v8.0.0-rc.7 entry; research/technologies/prisma.md
§3, §13].

**Rust-free / driver-adapter architecture:** as of **v7.0.0** (2025-11-19),
Prisma's *default* architecture dropped the Rust query-engine binary; queries
compile to SQL via a TypeScript/WASM query compiler, and connectivity comes
from explicit per-database driver adapters (e.g. `@prisma/adapter-pg`)
wrapping a Node.js driver you supply, instead of Prisma opening its own
native connection [Source: prisma.io/blog/from-rust-to-typescript-a-new-chapter-for-prisma-orm].
This existed only as an opt-in Preview/Early-Access feature under v6, reached
GA as a non-default option at **v6.16.0**, and only became the *default* at
v7.0.0 [Source: prisma.io/docs/orm/v6/prisma-client/setup-and-configuration/no-rust-engine].
Do not assume Rust-free behavior for a project pinned to v6.x on the classic
engine.

**v7's other breaking shape changes worth knowing before editing a v7
project:** ESM required; generator `provider` renamed `prisma-client-js` →
`prisma-client` with `output` now mandatory; connection URLs (`url`,
`directUrl`, `shadowDatabaseUrl`) move into `prisma.config.ts` and env vars
are **not** auto-loaded; the middleware API was removed in favor of Client
Extensions (`$extends`); `migrate dev`/`db push` no longer auto-run `prisma
generate` [Source: prisma.io/docs/guides/upgrade-prisma-orm/v7].

**Supported databases (v7, all GA unless noted):** PostgreSQL 9.6–18, MySQL
5.6–8.4, MariaDB 10.0+/11.0+, SQL Server 2017/2019/2022, MongoDB 4.2+ (v6
only — see above), CockroachDB 21.2.4+, SQLite; **Cloudflare D1 is
Preview-status** [Source: prisma.io/docs/orm/v7/reference/supported-databases].

## Decision framework

1. **Which Prisma major line?** MongoDB store → v6 is the only currently
   viable line; v7 dropped MongoDB outright. Every other supported database →
   v7 is the current production recommendation. v8 is release-candidate only
   (`rc.8` as of 2026-08-26, no stable `8.0.0` GA) — don't target it for
   anything shipping to production; the official blog itself says "Prisma 7
   is still the right choice for your production apps" with 12 months of
   committed v7 support [Source: prisma.io/blog/the-next-evolution-of-prisma-orm].
2. **Is the generated-client model worth its build step here?** Prisma trades
   a codegen step (and, on v7, mandatory driver-adapter wiring) for
   compile-time-checked queries and a built-in migration tool. If the project
   instead wants SQL-proximity with zero codegen — e.g. an edge function with
   a tight cold-start budget — that trade favors Drizzle, a call already made
   by `orm-integration`'s ORM-selection framework. This skill assumes Prisma
   is the settled choice and focuses on using it correctly.
3. **Rust-free (driver-adapter) or classic engine?** Any v7 project gets
   Rust-free by default. A v6 project should not assume WASM/driver-adapter
   behavior unless it explicitly opted in at `>=6.16.0`.
4. **Multi-file schema / `prisma.config.ts`?** Only available at `>=6.7.0`
   and `>=6.13.0` respectively — a smaller v6.x project below those floors
   keeps a single `schema.prisma` and env-var-driven configuration.

## Workflow

1. Determine the pinned Prisma major version (package.json/lockfile) and the
   target database — this gates whether v7 is even eligible (MongoDB → stop,
   use v6).
2. Author/edit `schema.prisma` (or `prisma/schema/*.prisma` at v6.7.0+) —
   `datasource`, `generator`, and model blocks.
3. On v7, confirm the driver adapter is instantiated and `prisma.config.ts`
   holds the connection URLs — env vars are not auto-loaded.
4. Run `prisma generate` explicitly (v7 does not auto-run it after `migrate
   dev`/`db push`).
5. In development, `prisma migrate dev` to create and apply a migration; in
   production, only `prisma migrate deploy` against already-committed
   migration files [Source: prisma.io/docs/orm/prisma-migrate/workflows/development-and-production].
6. Hand off migration *safety* sequencing (expand/contract, backfill
   batching, rollback points) to [data-migration](../data-migration/SKILL.md).

## Engineering rules

- Reuse a single global `PrismaClient` instance; never instantiate a new one
  per request — exhausts the DB connection pool [Source:
  prisma.io/docs/orm/v7/more/best-practices].
- On v7, wire an explicit driver adapter and `prisma.config.ts` — the bare
  `datasource { provider = ... url = env(...) }` block alone is no longer
  sufficient.
- Never run `prisma migrate dev` or `prisma db push` against production —
  only `prisma migrate deploy` [Source: prisma.io/docs/orm/v7/more/best-practices].
- Never replay one database provider's migration history against a different
  provider after switching — migration SQL is provider-specific; delete
  `prisma/migrations` and regenerate [Source: prisma.io/docs/orm/v7/prisma-migrate/understanding-prisma-migrate/limitations-and-known-issues].
- Before recommending any v8/RC feature, state that it is pre-GA and confirm
  the pinned version — don't silently assume "latest" docs apply.

## Trade-offs

**v6 classic engine vs. v7 default Rust-free:** the classic engine needs no
driver-adapter wiring but ships a native Rust binary dependency
(platform-specific builds, no WASM/edge runtimes); the Rust-free path removes
that binary and unlocks edge runtimes (Cloudflare Workers, Bun, Deno) but
requires explicit driver-adapter instantiation [Source:
prisma.io/blog/from-rust-to-typescript-a-new-chapter-for-prisma-orm].

**Staying on v7 vs. adopting v8 early:** v8's contract model and native RLS
are architecturally ahead, but the API is still moving between RCs (the
pagination rename above is a concrete example) — production stability today
costs waiting on v8's roadmap items (native RLS, MongoDB's return) until GA.

## Anti-patterns

- **Assuming MongoDB works against the latest stable Prisma release.** It
  doesn't — v7 has no MongoDB support at all; a MongoDB project must stay on
  v6 [Source: prisma.io/docs/guides/upgrade-prisma-orm/v7].
- **Feeding unsanitized/user-derived input to `$queryRawUnsafe` or
  `$executeRawUnsafe`** — these bypass Prisma's default parameterization by
  design; only tagged-template `$queryRaw`/`$executeRaw` with parameters are
  safe for dynamic input [Source: prisma.io/docs/orm/v7/more/best-practices].
- **Multiple `PrismaClient` instances** instead of one reused global instance.
- **`prisma migrate dev`/`db push` in production** — both can drop/reset data
  on detected drift; only `migrate deploy` belongs there.
- **Overengineering trap:** adopting Prisma 8 RC APIs (the contract model,
  the chained query DSL) for production code before a stable `8.0.0` GA
  exists, or hand-building custom connection-pool configuration that the v7
  driver adapter/`prisma.config.ts` already handles — chasing the newest
  architecture before it's stable, or reinventing what the current stable
  line already provides.

## Security

Prisma's query API parameterizes by default; the injection-risk surface is
specifically `$queryRawUnsafe`/`$executeRawUnsafe` fed unsanitized input
[Source: prisma.io/docs/orm/v7/more/best-practices]. Prisma performs no input
validation itself — sanitizing user input before it reaches Prisma is the
application's responsibility (Zod is named as a common pairing, not a bundled
feature). **Row-level security** is a Client Extension pattern layered on
native Postgres RLS in v6/v7 (enable RLS via a custom migration, scope
queries per-tenant through the extension, and ensure the app's DB role is not
`BYPASSRLS`-privileged) — not a first-class schema attribute until Prisma 8,
which introduces native RLS as a declared contract feature (pre-GA, not yet
independently verified in depth) [Source: github.com/prisma/prisma-client-extensions;
prisma.io/docs/orm/prisma-client/client-extensions; prisma.io/docs]. v7
driver adapters also enforce SSL certificate validation by default — a
self-signed/invalid cert now errors unless explicitly configured otherwise, a
behavior change from v6 [Source: prisma.io/docs/orm/v7/prisma-client/setup-and-configuration/databases-connections].
Deeper threat-modeling method is owned by security-engineering, not restated
here.

## Performance

Prisma's own vendor-benchmarked claim of "~90% of raw PostgreSQL query
throughput" for Prisma 8 has no published methodology, dataset, or
independent reproduction surfaced in this library's research — treat it as a
directional vendor claim, not a verified benchmark [Source:
prisma.io/docs; technology-decision-matrix.md §1]. For actual slow-query
diagnosis, **Query Insights** (built into Prisma Postgres) identifies
expensive queries out-of-the-box for raw SQL, with one extra setup step for
Prisma-ORM-originated queries; it replaces the earlier "Prisma Optimize"
product [Source: prisma.io/docs/query-insights]. For high concurrency, an
external pooler (PgBouncer) is recommended and **must run in Transaction
mode** — the default pooling mode causes `"prepared statement 's0' already
exists"` errors [Source: prisma.io/docs/orm/prisma-client/setup-and-configuration/databases-connections/pgbouncer].
As of v7, pool size/timeout is configured per driver adapter (the underlying
Node.js driver's own options), not via connection-string query parameters as
in earlier versions — version-sensitive change.

## Testing

The documented v7 unit-test pattern: **Jest + `ts-jest` + `jest-mock-extended`**
(docs pin `^2.0.4`), using `mockDeep()` to create a deep mock of
`PrismaClient`, `mockReset()` between tests, and `DeepMockProxy` for type
safety — in either a **singleton** setup (one mocked instance reset per
test) or **dependency injection** (a mocked context passed as a parameter,
built fresh per test via a factory) [Source:
prisma.io/docs/orm/prisma-client/testing/unit-testing]. **Integration
testing** against a real database with test data is documented as a separate,
complementary approach — it exercises real component interaction rather than
mocking the client, and is not a substitute for the unit-test pattern above
[Source: prisma.io/docs/orm/prisma-client/testing/integration-testing]. This
guidance is explicitly scoped to v7 in the source docs; re-verify before
assuming it applies unchanged to v6 or v8.

## Failure handling

- If the pinned Prisma major version is unknown, check package.json/lockfile
  or ask — do not assume v7 behavior.
- If the store is MongoDB, confirm the project is (or will be) pinned to v6
  before proceeding.
- If shell is unavailable, produce advisory schema/migration output and state
  that `prisma generate`/`migrate`/`db push` was not executed.

## Escalation

- `prisma migrate reset` (or any command that drops/recreates the database)
  requires explicit user confirmation before running — defer to
  `data-migration`'s rollout discipline; `migrate dev`/`db push` must never be
  proposed against production.

## Outputs & verification

- **Outputs:** version-correct schema/client code, a Prisma Migrate
  migration (or advisory plan), and version/architecture analysis.
- **Verify:** every API/CLI/config claim matches the pinned major version; a
  MongoDB-backed project's guidance targets v6 only; any raw-SQL escape hatch
  is parameterized; production migration guidance uses only `migrate deploy`.

## References

- [research/technologies/prisma.md](../../research/technologies/prisma.md) — primary research source (all `[Source: ...]` markers above resolve here).
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md) — Prisma row (version floors, MongoDB gap, pagination-rename conflict).
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md) — §1 ORM comparison.
- [orm-integration](../orm-integration/SKILL.md) and its [orm-comparison.md](../orm-integration/references/orm-comparison.md) — generic ORM method and the cross-ORM comparison table.
- [data-migration](../data-migration/SKILL.md) and its [version-sensitive-migrations.md](../data-migration/references/version-sensitive-migrations.md) — migration safety mechanics and the MongoDB-in-v7 caveat as a worked example.
- Full source list: `skill.yaml.source_references`.
