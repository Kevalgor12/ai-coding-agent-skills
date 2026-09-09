# ORM/ODM comparison (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Condensed from
[technology-decision-matrix.md §1](../../../research/knowledge-maps/technology-decision-matrix.md)
— consult that document for the full citation trail.

| | Mongoose | TypeORM | Prisma | Drizzle ORM |
|---|---|---|---|---|
| Target database | MongoDB only | Any SQL DB (driver-dependent) | Any SQL DB via driver adapters | PostgreSQL, MySQL, SQLite (+ MSSQL/CockroachDB/SingleStore) |
| Core model | Schema/Model/Document, Active Record | Active Record *and* Data Mapper (developer's choice) | Schema file → generated type-safe client | Headless SQL-proximity query builder |
| Injection defense | `sanitizeFilter` (off by default) | Parameterized on all drivers (schema/DDL paths, v1.0+) | Parameterized by default; raw-query methods flagged as risk surface | Automatic parameterization; `sql.raw()` explicitly warned against for user data |
| Known CVE | **CVE-2026-42334** — `sanitizeFilter` `$nor` bypass, patched `^6.13.9`/`^7.8.9`/`^8.22.1`/`^9.1.6` | none reported in source data | none reported in source data | none reported in source data |
| Row-level security | N/A (document model) | not a documented first-class feature | Client Extension pattern (v6/v7); native as of v8 | First-class: `pgTable.withRLS()` + `pgPolicy()`, Neon/Supabase integrations |
| N+1 mitigation | `.populate()` + `select` | `leftJoinAndSelect`/`relations` | `include`, or batch with `WHERE id IN (...)` | Not a dedicated feature; index FK columns |
| Query-result caching | N/A documented | `cache:true`, Redis/IORedis or DB-table backed | No built-in cache; "Query Insights" (Prisma Postgres) | Experimental `.$withCache()`, Upstash Redis |
| Official test stance | **Discourages Jest** explicitly | No dedicated official testing guide | Jest + `ts-jest` + `jest-mock-extended` | PGlite (WASM Postgres) + `drizzle.mock()` + `drizzle-seed` |

**Unresolved (per the source research):** none of the four make a direct,
apples-to-apples performance claim against a named competitor — Prisma's
"~90% of raw PostgreSQL" and Drizzle's "almost 0 overhead" are both
self-referential vendor framing, not independent comparative benchmarks. Do
not present a ranked performance claim between these ORMs as researched fact.

## Choosing quickly

- **Data is in MongoDB** → Mongoose is the only researched fit.
- **Want maximum SQL transparency, minimal abstraction, edge/serverless
  footprint** → Drizzle.
- **Want a generated type-safe client with an opinionated, batteries-included
  migration workflow** → Prisma (but see [data-migration](../../data-migration/SKILL.md)
  for the MongoDB-support version caveat).
- **Want Active Record/Data Mapper flexibility, or already have a TypeORM codebase** → TypeORM.
