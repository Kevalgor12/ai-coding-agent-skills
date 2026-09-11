# Prisma — Technology Research

Research date: 2026-09-09. Primary sources: `prisma.io/docs/*` (canonical docs host — confirmed current, no migration observed), `prisma.io/changelog`, `prisma.io/blog/*` (official Prisma company blog), `github.com/prisma/orm` (official GitHub org repo, release history via GitHub API). Citation convention: `[Source: <url>]` for documented facts, `[Inference, not confirmed in docs]` for reasoning, `Unresolved: ...` for genuine ambiguity found in official sources, "Not documented / could not verify" where no authoritative official answer was found.

## IMPORTANT — read this before anything else in this file: Prisma is mid-major-version-transition right now

As of the research date (2026-09-09), Prisma is in an unusually disruptive state that materially affects every other section below:

- [Source: https://github.com/prisma/orm/releases (GitHub Releases API)] The latest **stable, non-prerelease** release is `7.10.0`, published 2026-08-25.
- [Source: https://github.com/prisma/orm/releases (GitHub Releases API)] The latest overall release is `v8.0.0-rc.8`, published 2026-08-26, explicitly flagged `prerelease: true` by GitHub. No `8.0.0` stable/GA tag exists in the release list as of the research date.
- [Source: https://www.prisma.io/changelog] The changelog's most recent entries (through 2026-08-28) show Prisma 8 features and Prisma Compute rolling out progressively across mid-to-late 2026, but **no entry announces a Prisma 8.0.0 stable/GA release**.
- [Source: https://www.prisma.io/blog/the-next-evolution-of-prisma-orm] Prisma's own announcement blog post states Prisma 8 (referred to during development as "Prisma Next") is a ground-up TypeScript rewrite, was in **Early Access** at time of writing, and explicitly says: *"Prisma 7 is still the right choice for your production apps."* The team committed to **12 months of continued Prisma 7 support** from that announcement.
- [Source: https://www.prisma.io/docs/orm] Despite the above, the **default/canonical docs URL** (`prisma.io/docs/orm`, and `prisma.io/docs/getting-started`) currently presents **Prisma 8** as the primary experience — with `/orm/v7` and `/orm/v6` demoted to explicitly version-pinned legacy paths.

**Unresolved: the maturity state of Prisma 8 is contradictory across official sources as of this research date.** The docs site's information architecture treats v8 as "the current thing," while the GitHub release list (the most mechanically verifiable source) still tags every v8 build as a release candidate, and the official blog explicitly directs production users to v7. This document therefore treats **Prisma 7 as the current production-recommended version** and documents **Prisma 8 separately and explicitly labeled as pre-GA / architecturally distinct**, per dimension, rather than silently merging the two. Any skill built on top of this research should re-check `github.com/prisma/orm/releases` for a non-prerelease `8.x.x` tag before assuming Prisma 8 is safe for production use.

---

## 1. Core concepts

[Source: https://www.prisma.io/docs/orm/v7/overview/introduction/what-is-prisma, https://www.prisma.io/docs/orm/v7/more/best-practices] Prisma ORM (v7, current production version) is a Node.js/TypeScript ORM built around three components: (1) the **Prisma Schema** (`schema.prisma`, written in Prisma Schema Language / PSL) that declares data models and a datasource, (2) **Prisma Client**, a generated, type-safe query builder derived from that schema, and (3) **Prisma Migrate**, a migration tool that turns schema changes into versioned SQL migration files.

[Source: https://www.prisma.io/docs/orm/v7/more/best-practices] Naming convention: PascalCase singular for model names, camelCase for field names; `@map`/`@@map` attributes let the PSL-facing name diverge from the underlying database column/table name (e.g., to match a legacy database's snake_case convention).

[Source: https://www.prisma.io/docs/orm] **Prisma 8 (pre-GA)** reconceives the core workflow: instead of generating a client *package*, "Prisma 8 emits the schema as a **contract**: a JSON document plus TypeScript types that your application, the migration tools, and coding agents all read." [Inference, not confirmed in docs] This appears to replace "codegen you import" with "a build artifact everything reads," but the precise mechanics of how the contract is consumed at runtime were not independently verified beyond the docs' own summary language.

[Source: https://www.prisma.io/docs/orm] Prisma 8's three-step workflow, per the docs' own framing: (1) author the schema in PSL *or* TypeScript, (2) "emit" the contract via a lightweight build step, (3) query against the typed contract using a composable query DSL.

[Source: https://www.prisma.io/docs/orm/reference/orm-client] In Prisma 8, queries are built through model accessors — `db.orm.public.User` for PostgreSQL (PSL model name under the schema namespace) or `db.orm.users` for MongoDB (lowercase plural collection name) — chained with builder methods (`where()`, `select()`, `include()`, `orderBy()`, `take()`, `skip()`) and resolved by a terminal call (`.all()`, `.first()`, `.aggregate()`, etc.). This is a materially different call shape from v6/v7's `prisma.user.findMany({ where: {...} })` nested-object style.

---

## 2. Architecture

[Source: https://www.prisma.io/blog/from-rust-to-typescript-a-new-chapter-for-prisma-orm, https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7] **As of v7.0.0 (Nov 2025), Prisma ORM's default architecture dropped the Rust-based query engine binary.** Queries now compile to SQL via a TypeScript/WebAssembly query compiler, and database connectivity is provided by explicit, per-database **driver adapters** (e.g., `@prisma/adapter-pg` for PostgreSQL) that wrap a Node.js driver you supply, rather than Prisma's engine opening its own native connection. [Source: WebSearch summary of official blog, not independently fetched verbatim] The stated rationale is eliminating a Rust↔JS serialization boundary for large result sets, and removing the native-binary dependency so Prisma can run in WASM-capable edge/serverless runtimes (Cloudflare Workers, Bun, Deno were named).

[Source: https://www.prisma.io/docs/orm/v6/prisma-client/setup-and-configuration/no-rust-engine] The Rust-free architecture existed as an **opt-in Preview/Early Access feature under Prisma ORM v6** before becoming the v7 default — version-sensitive: do not assume Rust-free behavior for a project pinned to v6.x with the classic engine.

[Source: https://www.prisma.io/docs/orm/v7/more/best-practices] Since **v6.7.0**, schemas can be split across multiple `.prisma` files in a single `prisma/schema/` directory instead of one monolithic `schema.prisma` — version-sensitive, not available pre-6.7.

[Source: https://www.prisma.io/docs/orm] **Prisma 8 (pre-GA)** architecture: the docs describe "a minimal core exposed via a public SPI [service provider interface], with databases and features implemented as extensions" — an explicit shift toward an extensible/composable core rather than a monolithic engine. The docs also claim Prisma 8 is benchmarked at "approximately 90% the speed of raw PostgreSQL" — Unresolved: no benchmark methodology, dataset, or independent reproduction was surfaced in the fetched summary, so this figure should be treated as a vendor claim pending the underlying benchmark page.

[Source: https://www.prisma.io/docs/orm] Prisma 8's migration system is described as **graph-based**, using schema-state hashes instead of linear timestamp ordering, intended to auto-resolve branch conflicts and make partial migration failures safely retryable. This is architecturally distinct from v6/v7 Prisma Migrate's linear, timestamp-directory migration history (see Section 11).

---

## 3. APIs

### Prisma Client (v6/v7 — current production shape)

[Source: https://www.prisma.io/docs/orm/v7/more/best-practices, https://www.prisma.io/docs/orm/prisma-client/client-extensions] Standard CRUD surface: `findUnique`, `findMany`, `findFirst`, `create`, `update`, `upsert`, `delete`, and batch variants `createMany`, `updateMany`, `deleteMany` — the batch variants "automatically run as transactions, so all writes either succeed together or are rolled back" [Source: https://www.prisma.io/docs/orm/v7/more/best-practices]. Relations are eagerly loaded via `include`, and field projection via `select` (whitelist) or `omit` (blacklist).

[Source: https://www.prisma.io/docs/orm/prisma-client/client-extensions] **Client Extensions** (`$extends`) let you augment Prisma Client with four component types: `model` (add custom methods to a model), `client` (add methods to the top-level client), `query` (hook into the query lifecycle to modify an incoming query or its result), and `result` (add computed, type-safe fields to query results). This is the documented replacement for the removed v6 middleware API (see Section 13).

### Prisma 8 ORM Client (pre-GA — architecturally distinct)

[Source: https://www.prisma.io/docs/orm/reference/orm-client] Composable, chained query-builder DSL rather than nested-object arguments. Key methods, **PostgreSQL vs. MongoDB support differs per method** (table reproduced from docs' own comparison):

| Feature | PostgreSQL | MongoDB |
|---|---|---|
| `where()` enforcement on mutations | Type-only | Runtime-enforced; throws if omitted |
| `include()` refinement (nested filter/sort/paginate) | Full `Collection` access | Plain `$lookup`; no refinement |
| Atomic updates | Yes (`UPDATE...RETURNING`) | No — capture IDs, update, re-read |
| `distinct()` / `distinctOn()` | Supported | Not supported |
| `cursor()` pagination | Supported | Not supported |
| `aggregate()` / `groupBy()` | Supported | Not documented in fetched summary |

[Source: https://www.prisma.io/docs/orm/reference/orm-client] Example chained query:
```typescript
const users = await db.orm.public.User
  .where((u) => u.kind.eq('admin'))
  .include('posts', (posts) => posts.where((p) => p.priority.eq('urgent')).count())
  .orderBy((u) => u.email.asc())
  .take(10)
  .all();
```
Version-sensitive: `take`/`skip` naming — [Source: GitHub Releases, v8.0.0-rc.7 entry] pagination was renamed from `take`/`skip` to `limit`/`offset` at some point in the v8 release-candidate cycle (rc.7, 2026-08-25). **Unresolved: whether the final v8.0.0 GA API uses `take`/`skip` (as shown in the docs example fetched above) or `limit`/`offset` (per the rc.7 changelog entry) — these two official sources conflict, likely because the docs snapshot and the rc.7 changelog entry are from different points in an actively-changing RC cycle.** Verify against the exact `prisma` version pinned before writing code against this API.

### CLI

[Source: https://www.prisma.io/docs/cli] Prisma 8 ships a **single unified binary** covering both ORM commands and platform commands (Prisma Composer, Prisma Compute, Prisma Postgres, object storage). ORM-relevant commands: `orm init`, `contract emit` (generate contract artifacts), `contract infer` (infer schema from existing DB), `contract format`, `migration plan`, `migration status`, `db migrate`, `db sign`/`db verify`. [Source: GitHub Releases, v8.0.0-rc.2] The legacy `prisma-next` preview binary was retired in favor of this unified CLI during the RC cycle.

[Source: https://www.prisma.io/docs/orm/v7/more/upgrades (via upgrade guide), https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7] Prisma 7's CLI retains the classic verb-first shape: `prisma generate`, `prisma migrate dev`, `prisma migrate deploy`, `prisma migrate reset`, `prisma db push`, `prisma db seed`, `prisma db execute`, `prisma studio`. **v7 removed** the `--skip-generate` flag (from `migrate dev`/`db push`) and `--skip-seed` flag (from `migrate dev`); `migrate dev`/`db push` **no longer auto-run `prisma generate`** — it must be invoked explicitly.

---

## 4. Configuration

[Source: https://www.prisma.io/docs/orm/v7/reference/prisma-config-reference] **`prisma.config.ts`** is, as of v7, the canonical TypeScript configuration file for the Prisma CLI — created automatically by `prisma init`. It configures schema location, migrations path, seed script, and (new in v7) **datasource connection URLs** (`url`, `directUrl`, `shadowDatabaseUrl`), which in v7 live in this file rather than being resolved purely from environment variables inside `schema.prisma`. [Source: https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7] Explicitly noted: "Environment variables are not loaded by default" in v7 — projects relying on implicit `.env` loading (as in v5/v6) must adjust.

[Source: https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7] v7 generator block changed provider from `prisma-client-js` to `prisma-client`, and the `output` field became **mandatory** (no longer defaults to `node_modules/.prisma/client`):
```prisma
generator client {
  provider = "prisma-client"
  output   = "./generated/prisma"
}
```
Import paths change accordingly (e.g., `from "./generated/prisma/client"`).

[Source: https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7] v7 requires **explicit driver adapters** — traditional `datasource { provider = "postgresql" url = env("DATABASE_URL") }`-only configuration is replaced by instantiating an adapter (e.g., `PrismaPg` from `@prisma/adapter-pg`, `PrismaBetterSqlite3`) and passing it to the client constructor.

[Source: https://www.prisma.io/docs/getting-started] Prisma 8 config: `orm init` writes `prisma.config.ts`, a starter "contract" file, and `db.ts` under `src/prisma/`.

---

## 5. Recommended patterns

[Source: https://www.prisma.io/docs/orm/v7/more/best-practices]
- **Single global `PrismaClient` instance**, reused across the app — multiple instances exhaust the DB connection pool. In serverless, instantiate outside the handler for warm-invocation reuse; in dev, guard against hot-reload creating duplicate instances via a global variable.
- **Prevent N+1 queries**: use `include` to eager-load relations in one query, or batch with `WHERE id IN (...)` instead of per-row loop queries.
- **Field selection**: use `select` to whitelist or `omit` to blacklist fields, reducing payload size and avoiding accidental sensitive-field exposure.
- **Cursor-based pagination** for large/growing datasets — "scales better because it uses indexed columns to find the starting position instead of traversing skipped rows"; offset pagination is acceptable only for small datasets needing arbitrary page jumps.
- **Batch mutations** (`createMany`/`updateMany`/`deleteMany`) run as transactions automatically.
- **Index fields used in `where`, `orderBy`, and relation scalar fields** — especially important for databases without enforced foreign keys (PlanetScale named explicitly), where "Prisma ORM emulates relations and you should manually add indexes on relation scalar fields" to avoid full table scans.
- **Enums for finite value sets**, plain strings reserved for frequently-changing/user-generated values to avoid constant schema migrations.
- Prefer generated Prisma types over hand-duplicated interfaces.

[Source: https://www.prisma.io/docs/orm/prisma-client/queries/query-optimization-performance] Setting `relationLoadStrategy: "join"` makes Prisma execute a relation fetch as a single SQL join rather than separate queries. [Version-sensitive: Unresolved — which major version(s) this option is available/default in was not confirmed; treat as needing per-version verification.]

---

## 6. Anti-patterns

[Source: https://www.prisma.io/docs/orm/v7/more/best-practices] Documented explicitly as things to avoid:
- Creating multiple `PrismaClient` instances (exhausts connection pool).
- N+1 query patterns (fetching related rows one-by-one inside a loop).
- String-concatenating user input into raw SQL.
- Using `prisma migrate dev` or `prisma db push` in production (see Section 10).
- Calling `$disconnect()` on every serverless invocation.

[Source: https://www.prisma.io/docs/orm/v7/prisma-migrate/understanding-prisma-migrate/limitations-and-known-issues] Reusing the same migration history across different database providers (e.g., PostgreSQL migrations replayed against SQLite) — migration SQL is provider-specific and not portable; switching providers requires deleting `prisma/migrations` and regenerating history.

---

## 7. Security

[Source: https://www.prisma.io/docs/orm/v7/more/best-practices] Prisma's query API uses parameterized queries/prepared statements by default, which is the documented SQL-injection mitigation for standard model queries. For raw SQL (`$queryRaw`/`$executeRaw`), the docs direct use of tagged templates or parameterized inputs; `$queryRawUnsafe`/`$executeRawUnsafe` are flagged as injection-risk if fed unsanitized input — "Never concatenate user input into SQL strings."

[Source: https://www.prisma.io/docs/orm/v7/more/best-practices] Prisma does **not** perform input validation itself — the docs state validation/sanitization of user input before it reaches Prisma is the application's responsibility (Zod is named as a commonly paired library, though this is a suggestion, not a bundled feature).

[Source: https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/error-formatting] Error formatting is environment-sensitive: by default Prisma Client pretty-prints error stacks (ANSI codes) with fix suggestions; when `NODE_ENV=production`, only the minimal error is printed — relevant to avoid leaking schema/query internals in production error output.

[Source: https://github.com/prisma/prisma-client-extensions (row-level-security example directory), https://www.prisma.io/docs/orm/prisma-client/client-extensions] **Row-Level Security (RLS)** with Prisma is documented via a **Client Extension pattern** (community/official example repo under the `prisma` GitHub org), not a first-class schema attribute in v6/v7: you enable Postgres RLS via a custom migration and use a client extension to scope queries per-tenant, connecting as a non-superuser role (Postgres `BYPASSRLS`-privileged roles bypass RLS entirely, so the app's DB role must not have that attribute). [Inference, not confirmed in docs] This is an application-level pattern layered on top of Postgres's native RLS, not a Prisma-managed security primitive in v6/v7.

[Source: https://www.prisma.io/docs] Prisma 8 (pre-GA) is documented as introducing **native RLS policies as a declared schema/contract feature** — version-sensitive and not yet independently verified in depth since it sits behind the same pre-GA uncertainty flagged in the top section.

[Source: https://www.prisma.io/docs/orm/v7/prisma-client/setup-and-configuration/databases-connections] SSL: v7 driver adapters enforce SSL certificate validation by default; connecting to a database with an invalid/self-signed certificate now errors unless the adapter is explicitly configured with `ssl: { rejectUnauthorized: false }` or a proper certificate is supplied — this is a **v7 behavior change** from v6 (see Section 13).

[Source: https://www.prisma.io/docs/ai/tools/mcp-server] The official Prisma MCP server includes a documented safety guardrail: it detects when an AI agent attempts a destructive command (example given: `prisma migrate reset --force`) and requires explicit user consent before proceeding.

---

## 8. Performance

[Source: https://www.prisma.io/docs/orm/prisma-client/queries/query-optimization-performance] Documented common causes of slow queries: over-fetching data, missing indexes, no caching of repeated queries, full table scans. Recommended mitigations: bulk operations in batches (example given: insert 50,000 records in batches of 1,000 rather than 50,000 individual inserts) rather than row-by-row writes; single global `PrismaClient` instance to avoid connection-pool exhaustion, especially in serverless/edge.

[Source: https://www.prisma.io/docs/query-insights (per llms.txt index), https://www.prisma.io/docs] **Query Insights** (built into Prisma Postgres) is the current, documented tool for identifying slow/expensive queries — it works out-of-the-box for raw SQL and needs one extra setup step to see Prisma-ORM-originated queries. [Source: WebSearch summary] Query Insights is stated to **replace Prisma Optimize** (a previously separate, Early-Access-then-GA product) and ships at no extra cost with Prisma Postgres — version-sensitive/product-lineage note: if older material references "Prisma Optimize," that is the predecessor product name.

[Source: https://www.prisma.io/docs/orm/v7/prisma-client/setup-and-configuration/databases-connections/connection-pool, https://www.prisma.io/docs/orm/v7/prisma-client/setup-and-configuration/databases-connections/pgbouncer] For high-concurrency workloads, an external connection pooler (PgBouncer named explicitly) is recommended to avoid exhausting the database's own connection limit; **PgBouncer must run in Transaction mode** for Prisma Client to work reliably with it. As of v7, pool size/timeout/other pool behavior is configured **per driver adapter** (via the underlying Node.js driver's own options), not via connection-string query parameters as in earlier versions — version-sensitive change.

[Source: https://www.prisma.io/docs/orm] Prisma 8's claimed "~90% of raw PostgreSQL" query throughput is a vendor benchmark claim; **Unresolved** — methodology not verified (see Section 2).

---

## 9. Testing

[Source: https://www.prisma.io/docs/orm/prisma-client/testing/unit-testing] **This guidance is explicitly scoped to Prisma ORM v7** in the fetched page. Two documented mocking patterns for unit tests:
1. **Singleton pattern** — a single mocked `PrismaClient` instance configured in a test setup file, reset before each test.
2. **Dependency injection** — a mocked context object (containing the client) passed as a function parameter, created fresh per test via a factory.

Recommended library: **`jest-mock-extended`** (docs pin `^2.0.4`), providing `mockDeep()` to create a deep mock of the Prisma Client, `mockReset()` to clear mocks between tests, and a `DeepMockProxy` type for type safety. Stack assumed: Jest + `ts-jest`.

[Source: https://www.prisma.io/docs/orm/prisma-client/testing/integration-testing] **Integration testing** is documented as a separate, complementary approach that exercises real component interaction and requires an actual database with test data available (i.e., does not mock the client) — contrasted directly against the unit-testing/mocking approach above.

---

## 10. Deployment

[Source: https://www.prisma.io/docs/orm/prisma-client/deployment/deploy-prisma] **This guidance is explicitly scoped to Prisma ORM v7** in the fetched page. Three deployment paradigms documented:
1. **Traditional servers** (PaaS: Heroku, Koyeb, Render; Kubernetes/Docker; VMs/bare metal) — one long-running Node.js process serving concurrent requests.
2. **Serverless functions** (AWS Lambda, Azure Functions; Vercel named) — a process starts per request/batch, handling one request at a time; "warm starts" may reuse a container with an already-open DB connection.
3. **Edge functions** — serverless, geographically distributed, with a narrower runtime API surface than traditional/serverless Node.

[Source: https://www.prisma.io/docs/orm/prisma-client/deployment/deploy-prisma] Documented gotchas: code outside the serverless handler stays initialized across invocations (this is the basis for the "instantiate client once, outside the handler" pattern); AWS has separate, documented platform-specific deployment caveats; migrations must be coordinated as part of the deploy process, not run ad hoc from developer machines.

[Source: https://www.prisma.io/docs/orm/v7/more/best-practices, https://www.prisma.io/docs/orm/prisma-migrate/workflows/development-and-production] **Production migration rule, stated unambiguously**: use **only** `prisma migrate deploy` in production, applying already-committed migration files; never `prisma migrate dev` (interactive, can prompt for destructive resets) or `prisma db push` (schema-sync without a migration history) in production.

[Source: https://www.prisma.io/docs] **Prisma Compute** — a first-party TypeScript app hosting product tied to the Prisma 8 ecosystem — reached general availability per the changelog entry dated 2026-08-28 ("Prisma Compute is now generally available"). This is a separate product from Prisma ORM itself; [Inference, not confirmed in docs] it appears positioned as an integrated deploy target specifically for Prisma-8-contract-based apps, with per-branch Prisma Postgres databases. Not verified whether Prisma Compute has any dependency on Prisma 8 reaching ORM-level GA.

---

## 11. Migration

### a) Upgrading between major ORM versions (v6 → v7)

[Source: https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7] Prerequisites: Node.js `^20.19.0`/`^22.12.0`/`^24.0.0` minimum (v6 required Node 16.13/18.x/20.x — raised minimums), TypeScript ≥5.4 (v6 required ≥4.7). Documented breaking changes:
- Project must be ESM (`"type": "module"` in `package.json`); `tsconfig.json` needs ESNext modules + bundler resolution.
- Generator `provider` changes `prisma-client-js` → `prisma-client`; `output` becomes mandatory.
- All databases require an explicit **driver adapter** package (e.g. `@prisma/adapter-pg`); the old bare `datasource` connection-only configuration is insufficient alone.
- `prisma.config.ts` becomes the home for connection URLs (`url`, `directUrl`, `shadowDatabaseUrl`); env vars are **not** auto-loaded.
- Client **middleware API removed** — replace with Client Extensions (`$extends`, query component).
- **Metrics preview feature removed.**
- **Automatic seeding removed** — v6 and earlier auto-ran the seed script after `migrate dev`/`migrate reset`; v7 requires running `prisma db seed` explicitly.
- CLI flags removed: `--skip-generate`, `--skip-seed`.
- `prisma db execute` no longer accepts `--schema`/`--url` flags; `prisma migrate diff` options replaced with `--from-config-datasource`/`--to-config-datasource`.
- Mapped-enum value behavior changed to use schema names rather than mapped DB values (matching v6's actual behavior — described as a correction).
- SSL certificates: invalid certs now error by default (see Section 7).
- **MongoDB is not yet supported in v7** — the docs explicitly instruct MongoDB users to "continue using Prisma ORM v6 for now." This is a hard version-fork: teams on MongoDB cannot currently move past v6 without losing MongoDB support, pending v8.

### b) Upgrading v7 → v8 (pre-GA)

[Source: https://www.prisma.io/blog/the-next-evolution-of-prisma-orm] At the time of the announcement blog post, "migration guidance will become available" once Prisma 8 reaches GA — **no finalized v7→v8 upgrade guide was located** as of the research date. [Source: GitHub Releases, `7.10.0` entry] A `@prisma/prisma7` **compatibility package** exists, described as enabling Prisma 7 to run alongside Prisma 8 — [Inference, not confirmed in docs] likely an interim bridge for incremental adoption/testing, but its exact mechanics were not independently confirmed beyond the release-note title.

[Source: https://www.prisma.io/blog/the-next-evolution-of-prisma-orm] MongoDB's re-introduction is explicitly tied to Prisma 8, not v7: "MongoDB support will come through Prisma 8, not Prisma 7," developed in collaboration with MongoDB for aggregation and field-level-encryption support.

### c) Migrating from other ORMs to Prisma

Not documented / could not verify — no official Prisma migration guide from a specific competing ORM (e.g., TypeORM, Sequelize, Drizzle) was located in this research pass. If such guides exist they were not surfaced by search; do not assume Prisma publishes one without checking `prisma.io/docs` directly.

---

## 12. Version information

[Source: https://github.com/prisma/orm/releases, verified via GitHub Releases API] As of 2026-09-09:
- **Latest stable (non-prerelease):** `7.10.0` (2026-08-25).
- **Latest overall (prerelease):** `v8.0.0-rc.8` (2026-08-26) — no stable `8.0.0` exists yet.
- Recent stable v7 patch cadence observed: `7.9.0` (2026-07-21) → `7.9.1` (2026-07-27) → `7.10.0` (2026-08-25).

[Source: https://www.prisma.io/docs/orm/v7/more/releases] **Release cadence**: "Prisma ORM typically releases new versions every two weeks," though the docs note this can shift for internal reasons. All release notes are published on GitHub.

[Source: https://www.prisma.io/docs/orm/v7/more/releases] **Maturity levels / SemVer policy**, documented explicitly:
- **Early Access** → cutting-edge, API may still shift materially based on feedback.
- **Preview** → validated direction/stability, "mostly stable unless stated otherwise," opt-in via flags.
- **General Availability (GA)** → stable, production-ready, extensively tested.
- SemVer applies from v3.x.x onward: MAJOR = breaking changes to GA features only; MINOR = backward-compatible additions, and breaking changes are permitted in MINOR releases **only** for opt-in Preview/Early-Access features; PATCH = backward-compatible fixes. Opt-in breaking changes graduate to GA only in a new MAJOR release.

[Source: https://www.prisma.io/changelog, https://www.prisma.io/docs] Major version chronology reconstructed from changelog/docs:
- v5 line: Prisma Postgres entered Early Access (~Nov 2024 per changelog entry), Prisma Pulse reached GA earlier in the v5 line.
- **v6.0.0** — updated minimum TypeScript/Node.js versions.
- **v6.1.0** — tracing Preview feature became stable.
- **v6.2.0** — `omit` API reached GA.
- **v6.4.0** — Prisma Postgres reached GA.
- **v6.7.0** — multi-file schema support.
- **v6.13.0** — `prisma.config.ts` reached GA.
- **v6.16.0** — Rust-free ORM + driver adapters reached GA (as an available, non-default option).
- **v7.0.0** (2025-11-19) — Rust-free Prisma Client becomes the **default**.
- v7.3.0–v7.7.0 (Jan–Apr 2026) — WASM query-compiler performance work, query caching layer, nested transaction savepoints, `prisma bootstrap` command for Prisma Postgres.
- **v8.0.0-rc.1 → rc.8** (Aug 2026) — active release-candidate cycle for the TypeScript-rewrite architecture; not GA as of this research date.

[Source: https://www.prisma.io/docs/orm/v7/reference/system-requirements] v7 system requirements: Node.js `^20.19.0`, `^22.12.0`, or `^24.0.0` (Active LTS/Maintenance LTS lines only); TypeScript ≥5.4 (optional, TS projects only); Yarn ≥1.19.2 if using Yarn 1. OS: macOS 10.15+, Windows (needs MSVC++ Redistributable 2015+), most Linux (glibc 2.19+/AMD64 Debian, 2.17+ RHEL; glibc 2.24+ ARM64; needs OpenSSL 1.0.x/1.1.x/3.x, zlib, libgcc). [Source: same page, comparative note] v6 required lower minimums: Node 16.13/18.x/20.x, TypeScript ≥4.7 — version-sensitive, do not apply v7 minimums to a v6 project's engines field.

---

## 13. Breaking changes

Consolidated from Sections 4 and 11 (v6→v7, the only fully-documented major-version transition as of this research date):
- [Source: https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7] ESM required; `prisma-client-js` generator renamed to `prisma-client` with mandatory `output`; explicit driver adapters required for every database; connection URLs move into `prisma.config.ts` (env vars no longer auto-loaded); middleware API removed (use Client Extensions); Metrics preview feature removed; automatic post-migration seeding removed; `--skip-generate`/`--skip-seed` flags removed; `migrate dev`/`db push` no longer auto-run `generate`; `db execute` loses `--schema`/`--url` flags; `migrate diff` gains `--from-config-datasource`/`--to-config-datasource` in place of prior flags; mapped-enum value resolution changed; invalid SSL certs now error by default; MongoDB unsupported in v7 (stay on v6).
- [Source: GitHub Releases, v8.0.0-rc.2] Retired the `prisma-next` binary for a unified `prisma` CLI; "major API changes to aggregates and constraints" (exact scope not detailed in the fetched release-note summary — **Unresolved**, recommend reading the rc.2 release notes directly before relying on aggregate/constraint behavior).
- [Source: GitHub Releases, v8.0.0-rc.6] PostgreSQL temporal columns moved to explicit `Temporal` representations or plain text (i.e., a type-mapping change for date/time columns) — **Unresolved**: exact before/after mapping not confirmed beyond the release-note title.
- [Source: GitHub Releases, v8.0.0-rc.7] Pagination renamed `take`/`skip` → `limit`/`offset` — but conflicts with the current `orm-client` reference docs example, which still shows `take()` (see Section 3's flagged Unresolved item).

---

## 14. Limitations

[Source: https://www.prisma.io/docs/orm/v7/prisma-migrate/understanding-prisma-migrate/limitations-and-known-issues]
- Prisma Migrate does not support MongoDB.
- Migration files are provider-specific and not portable across database providers (PostgreSQL migration SQL will not run against SQLite/MySQL, etc.); switching providers requires deleting the `prisma/migrations` folder and regenerating history from scratch.
- `prisma migrate dev`/`migrate reset` will drop-and-recreate the database on detected drift or migration conflicts, causing full data loss in that environment; mitigated only by a configured seed script to repopulate afterward, not by preserving existing data.
- PgBouncer, in the default pooling mode, causes `"prepared statement 's0' already exists"` errors — must be configured in Transaction mode.
- `prisma migrate dev` is unsupported / warns in non-interactive environments (e.g., default `docker run` without `-it`).

[Source: https://www.prisma.io/docs/orm/v7/reference/supported-databases] Database support is not uniform: **Cloudflare D1 is explicitly Preview-status** (all other listed databases — PostgreSQL 9.6–18, MySQL 5.6/5.7/8.0/8.4, MariaDB 10.0+/11.0+, SQL Server 2017/2019/2022, MongoDB 4.2+, CockroachDB 21.2.4+, SQLite, plus managed variants: AWS Aurora/Aurora Serverless excluding Data API, Azure SQL, CockroachDB-as-a-Service, MongoDB Atlas, Neon, PlanetScale, Aiven — are presented as GA without qualification).

[Source: https://www.prisma.io/blog/the-next-evolution-of-prisma-orm] Prisma 8, as of the announcement, does not yet support MongoDB either during its Early Access phase (MongoDB support was framed as a Prisma-8-cycle goal, not necessarily present from the first RC) — **Unresolved: exact rc at which MongoDB support lands in the v8 line was not confirmed.**

---

## 15. Debugging

[Source: https://www.prisma.io/docs/orm/prisma-client/observability-and-logging/logging] `PrismaClient`'s `log` constructor option accepts an array of log levels (`"query"`, `"info"`, `"warn"`, `"error"`) to print engine/query activity to stdout (or route to event handlers for custom logging).

[Source: https://www.prisma.io/docs/orm/prisma-client/debugging-and-troubleshooting/debugging] The `DEBUG` environment variable enables namespaced debug output — e.g. `prisma:engine` (engine debug messages), `prisma:client` (client runtime debug messages), or `prisma*` (everything).

[Source: https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/error-formatting] Error formatting is pretty-printed with ANSI escape codes and fix suggestions by default; under `NODE_ENV=production`, only the minimal error is printed (see Section 7 for the security implication).

[Source: https://www.prisma.io/docs/orm/reference/error-reference] A dedicated **Prisma 8 error reference** page exists cataloging error codes for the v8 line; a comparable v6-era error reference exists at a separate `/orm/v6/reference/errors` path — version-sensitive, make sure to consult the reference matching the pinned major version, since error codes/shapes are not guaranteed stable across the v6/v7/v8 line given the v7 architecture change and v8 rewrite.

---

## 16. Integration

[Source: https://www.prisma.io/docs/guides/frameworks/nextjs, https://www.prisma.io/docs/guides/frameworks/sveltekit, https://www.prisma.io/docs/guides/frameworks/nuxt, https://www.prisma.io/docs/guides/frameworks/hono] Official first-party framework guides exist (current, Prisma-8-era doc tree) for **Next.js**, **SvelteKit**, **Nuxt**, and **Hono** (the last specifically for Cloudflare Workers/edge deployment). [Source: https://www.prisma.io/docs/guides/v7/frameworks/nestjs] A **v7-pinned NestJS guide** also exists separately (`/guides/v7/frameworks/nestjs`), reflecting the docs' general pattern of maintaining parallel version-scoped guide trees.

[Source: https://www.prisma.io/docs/orm/prisma-client/client-extensions] Prisma is positioned to integrate with validation libraries (Zod named for input validation, as a recommendation rather than a bundled dependency) via ordinary application-code composition, not a first-party Prisma-Zod bridge package documented in the fetched pages.

[Source: https://www.prisma.io/docs/ai/tools/mcp-server] Prisma publishes an **official MCP server** (`https://mcp.prisma.io/mcp`) giving LLM-based coding agents/tools API access to Prisma Postgres database management (create/list/delete databases, connection strings, backups/restore, schema introspection, SQL execution, S3-compatible object storage, and natural-language doc search). Documented supported clients: VS Code, Cursor, Windsurf, Claude (Desktop/Web/Code), ChatGPT, Gemini CLI, Warp, fx, Codex — each with its own MCP config file location (e.g., `.vscode/mcp.json`, `~/.cursor/mcp.json`).

[Source: https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/databases-connections/pgbouncer] Documented integration with **PgBouncer** as an external connection pooler, required to run in Transaction mode.

[Source: https://www.prisma.io/docs/guides/integrations/neon-accelerate] Documented integration guide combining **Neon** (serverless Postgres) with **Prisma Accelerate** (connection pooling/global cache product).

[Source: WebSearch summary of https://www.prisma.io/docs/postgres, https://www.prisma.io/docs/accelerate] Product-line relationships as documented: **Prisma Accelerate** is a managed connection pool + global cache, usable standalone with any external database or bundled automatically with **Prisma Postgres** (Prisma's own managed Postgres offering). **Prisma Compute** is a newer, separate TypeScript-app-hosting product (GA per the 2026-08-28 changelog entry) where each branch of a Compute project can provision its own Prisma Postgres database. [Inference, not confirmed in docs] Prisma Pulse (real-time database event streaming) appears to be an older, distinct product from the same family; its current relationship to the Prisma 8 / Compute lineup was **not confirmed** in this research pass — Unresolved.

---

## 17. Production considerations

[Source: https://www.prisma.io/docs/orm/v7/more/best-practices, https://www.prisma.io/docs/orm/prisma-migrate/workflows/development-and-production] Core production rules, stated directly by the docs: single reused `PrismaClient` instance; `prisma migrate deploy` only (never `migrate dev`/`db push`) against production databases; disable verbose query logging in production except when actively debugging a specific issue (logging has a documented performance cost); use an external pooler (PgBouncer, or Prisma Accelerate/Prisma Postgres's built-in pooling) under high concurrency, particularly serverless/edge, to avoid exhausting the database's own connection ceiling.

[Source: https://www.prisma.io/docs/orm/prisma-client/deployment/deploy-prisma] Deployment topology affects connection-lifecycle design: traditional long-running servers can hold a stable connection pool for the app's lifetime; serverless functions must account for cold starts (new connections) vs. warm starts (reused container/connection) and should avoid disconnecting on every invocation; edge functions face a further-reduced runtime API surface that constrains which drivers/adapters are usable.

[Source: https://www.prisma.io/docs/orm/v7/reference/system-requirements] Production deployments must match the Node.js/TypeScript minimums for the pinned Prisma major version (v7 needs Active/Maintenance LTS Node ^20.19/^22.12/^24.0 — deploying v7 on an older Node LTS that has since aged out is unsupported) and satisfy the platform-native dependency list on Linux (OpenSSL, zlib, libgcc, glibc floor per architecture/distro).

[Source: https://www.prisma.io/changelog] **Prisma Compute reaching GA (2026-08-28)** is the newest first-party production deployment path tied to the Prisma 8 ecosystem; as flagged throughout this document, teams should independently confirm ORM-level v8 GA status before treating Prisma-8-contract-based apps as production-ready, separately from Compute's own GA status as a hosting product.

