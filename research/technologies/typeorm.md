# TypeORM — Deep Technology Research

Research date: 2026-09-09. Primary source: official documentation at **typeorm.io** (confirmed live and canonical as of this research — no host migration observed). Secondary official sources: the `typeorm/typeorm` GitHub organization (releases, changelog, security policy) and the official TypeORM blog (`typeorm.io/blog`). No non-official sources (blogs, Stack Overflow, GitBook mirrors, `typeorm.biunav.com`, `orkhan.gitbook.io`, etc.) are cited as primary evidence anywhere below — those surfaced in search results only as pointers toward the official pages, which were then fetched directly.

Citation format used throughout: `[Source: <url>] <claim>.`

---

## 1. Core Concepts

[Source: https://typeorm.io/docs/getting-started/] TypeORM is described as an ORM that runs in Node.js, Browser, Cordova, Ionic, React Native, NativeScript, Expo, and Electron platforms, supporting both TypeScript and JavaScript.

[Source: https://typeorm.io/docs/getting-started/] It targets projects "from small applications with a few tables to large scale enterprise applications with multiple databases," and lists supported databases as Google Spanner, Microsoft SQL Server, MongoDB, MySQL/MariaDB, Oracle, Postgres, SAP HANA, and SQLite, "as well as derived databases and different drivers."

[Source: https://typeorm.io/docs/getting-started/] TypeORM is unusual among JS ORMs in supporting both the **Active Record** and **Data Mapper** patterns simultaneously, letting a developer choose how they want to write database logic.

[Source: https://typeorm.io/docs/working-with-entity-manager/working-with-repository/] Under the Data Mapper pattern, database operations go through an `EntityManager` or a `Repository` (a manager scoped to one entity type); the docs state "Repository is just like EntityManager but its operations are limited to a concrete entity," and a repository is obtained via `dataSource.getRepository(Entity)`.

[Source: https://typeorm.io/docs/getting-started/] Under Active Record, entity classes extend a base class and call database methods (e.g. `.save()`) directly on themselves.

[Source: https://typeorm.io/docs/getting-started/] Requirements to install and use TypeORM: TypeScript 4.5+ (with `experimentalDecorators` and `emitDecoratorMetadata` enabled in `tsconfig.json`), the `reflect-metadata` shim, the `typeorm` package itself, and an appropriate database driver package. [Inference, not confirmed in docs: this TS-version figure may lag the site's live copy given how fast the project has been moving through 1.0 in 2026 — treat "4.5+" as a floor, not a currently-verified minimum, and re-check the live Getting Started page before relying on it.]

[Source: https://typeorm.io/docs/entity/entities/] An **entity** is a class decorated with `@Entity()` that maps to a database table; every entity requires at least one primary column, declared with `@PrimaryColumn()` (manual value) or `@PrimaryGeneratedColumn()` (auto-increment or `"uuid"` strategy). Composite primary keys are supported by combining multiple `@PrimaryColumn()` decorators.

[Source: https://typeorm.io/docs/entity/entities/] Column types include standard SQL types (varchar, int, boolean, decimal, etc.), `enum` (Postgres/MySQL), `simple-array`, `simple-json`, generated columns (`@Generated("uuid")` / `@Generated("increment")`), and — as of the current docs — vector columns for embeddings and spatial (well-known-text) columns on supported databases.

[Source: https://typeorm.io/docs/entity/entities/] Entity inheritance is supported: a base class holding shared columns (e.g. `id`, timestamps) can be extended by concrete entities, and "all columns from parent entities will be inherited and created in final entities."

---

## 2. Architecture

Not documented / could not verify: TypeORM's official docs do not appear to publish a single dedicated "architecture overview" page (a direct fetch of `typeorm.io/docs/architecture/architecture-overview/` returned HTTP 404, and a site-scoped search turned up no equivalent page). The architectural picture below is assembled from the API/reference pages that do exist, not from one canonical diagram.

[Source: https://typeorm.io/docs/getting-started/] **DataSource** is the top-level object that holds connection/configuration options and initializes the link to the database; as of v1.0 it is the sole connection entry point (see Section 13 — the legacy `Connection` class was removed).

[Source: https://typeorm.io/docs/working-with-entity-manager/working-with-repository/] **EntityManager** operates across all entities in a data source; **Repository** wraps an `EntityManager` scoped to one entity, and TypeORM additionally ships **TreeRepository** (for entities marked `@Tree`) and **MongoRepository** (MongoDB-specific) as repository subtypes.

[Source: https://typeorm.io/docs/transactions/] **QueryRunner** provides a single, dedicated database connection; "transactions are organized using query runners" and "a single transaction can only be established on a single query runner." Manually created query runners must be explicitly `.release()`d.

[Source: https://typeorm.io/docs/logging/] TypeORM ships pluggable **Logger** implementations (`advanced-console`, `simple-console`, `formatted-console`, `file`, `debug`) that can be swapped via configuration or replaced with a custom class implementing the `Logger` interface or extending `AbstractLogger`.

[Source: https://typeorm.io/docs/entity/entities/] Entity/column/relation metadata is derived from TypeScript decorators (`@Entity`, `@Column`, `@OneToMany`, etc.) at class-definition time via `reflect-metadata`, and this metadata is what the schema synchronizer and QueryBuilder consume.

[Source: https://typeorm.io/docs/help/decorator-reference/] Per-database driver implementations sit underneath the DataSource — the docs maintain separate per-driver pages (e.g. a MongoDB driver page, a Microsoft SQL Server driver page), consistent with a driver-abstraction layer, though the internal driver interface itself is not documented as a page in its own right in the pages retrieved for this research. Unresolved: whether TypeORM publishes a formal internal driver-interface/plugin-authoring document was not confirmed — none surfaced in search or direct navigation during this research pass.

---

## 3. APIs

[Source: https://typeorm.io/docs/working-with-entity-manager/working-with-repository/] The **Repository API** (and by extension `EntityManager`, which exposes the same shape) is the primary CRUD surface; documented method names encountered include `findOneBy()` and `save()`, with the docs pointing to a dedicated "Repository APIs" reference page for the full method list. Unresolved: the complete enumerated method list (all `find*` variants, `upsert`, `increment`/`decrement`, `softDelete`/`restore`, `count`, etc.) was not individually fetched and verified in this pass; do not assume completeness from the summary above.

[Source: https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/] As of v1.0, `findOneById()`, `findByIds()`, and `exist()` are removed from the Repository API; use `findOneBy()`, `findBy()` with the `In()` operator, and `exists()` respectively. **[Version-sensitive: breaking change effective v1.0.0, 2026-05-19.]**

[Source: https://typeorm.io/docs/help/decorator-reference/] The **decorator API** is extensive and covers: entity decorators (`@Entity`, `@ViewEntity`); column decorators (`@Column`, `@PrimaryColumn`, `@PrimaryGeneratedColumn`, `@ObjectIdColumn` (MongoDB only), `@CreateDateColumn`, `@UpdateDateColumn`, `@DeleteDateColumn`, `@VersionColumn`, `@Generated`, `@VirtualColumn`); relation decorators (`@OneToOne`, `@ManyToOne`, `@OneToMany`, `@ManyToMany`, `@JoinColumn`, `@JoinTable`, `@RelationId`); entity-lifecycle listener decorators (`@AfterLoad`, `@BeforeInsert`, `@AfterInsert`, `@BeforeUpdate`, `@AfterUpdate`, `@BeforeRemove`, `@AfterRemove`, `@BeforeSoftRemove`, `@AfterSoftRemove`, `@BeforeRecover`, `@AfterRecover`, `@EventSubscriber`); and schema decorators (`@Index`, `@Unique`, `@Check`, `@Exclusion` (Postgres only), `@ForeignKey`).

[Source: https://typeorm.io/docs/query-builder/caching/] **QueryBuilder** exposes `getMany()`, `getOne()`, `getRawMany()`, `getRawOne()`, and `getCount()` as terminal query-execution methods, each cacheable via `.cache()`.

[Source: https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/] As of v1.0, QueryBuilder's `printSql()`, `onConflict()`, and `setNativeParameters()` methods are removed; use `getSql()` for SQL inspection and `orIgnore()`/`orUpdate()` for upsert/conflict handling. **[Version-sensitive: breaking change effective v1.0.0.]**

[Source: https://typeorm.io/docs/releases/1.0/release-notes/] v1.0 QueryBuilder adds `valuesFromSelect()` to support `INSERT INTO ... SELECT FROM ...`, plus a `returning` option for update/upsert and an `ifExists` parameter on all "drop" methods. **[Version-sensitive: new in v1.0.0.]**

[Source: https://typeorm.io/docs/transactions/] Transaction API surface: `dataSource.transaction(callback)` / `dataSource.manager.transaction(callback)` (callback-scoped, recommended), and the lower-level `QueryRunner` methods `connect()`, `startTransaction()`, `commitTransaction()`, `rollbackTransaction()`, `release()`.

[Source: https://typeorm.io/docs/migrations/executing/] **CLI API**: `typeorm migration:run -- -d <path-to-datasource-config>` and `typeorm migration:revert`. These "only work on `.js` files"; for TypeScript projects the docs specify `npx typeorm-ts-node-commonjs migration:run ...` (CommonJS) or `npx typeorm-ts-node-esm migration:run ...` (ESM).

---

## 4. Configuration

All entries below are `DataSource` options unless noted, drawn from [Source: https://typeorm.io/docs/data-source/data-source-options/] unless a different URL is cited inline.

- `type` (required) — database driver, e.g. `mysql`, `postgres`, `mongodb`, `oracle`, `mssql`, etc.
- `host`, `port`, `username`, `password`, `database` — standard connection credentials.
- `entities` — classes and/or glob paths for entity discovery.
- `entityPrefix` — prefixes all generated table names.
- `entitySkipConstructor` — skips the entity's constructor when TypeORM builds instances from query results.
- `synchronize` — auto-creates/updates the database schema to match entities on startup. **"Be careful with this option and don't use this in production - otherwise you can lose production data."**
- `dropSchema` — drops the schema each time the data source initializes. **"Don't use this in production - otherwise you'll lose all production data."**
- `migrations` — migration classes/glob paths to load.
- `migrationsRun` — auto-runs pending migrations on data source initialization.
- `migrationsTableName` — overrides the default `migrations` bookkeeping table name.
- `migrationsTransactionMode` — controls whether migrations run inside a transaction: `all` (default, one transaction wraps every migration), `each` (one transaction per migration), or `none`. [Source: https://typeorm.io/docs/migrations/setup/]
- `logging` — enable logging; accepts `true`, `"all"`, or an array of levels (`query`, `error`, `schema`, `warn`, `info`, `log`). [Source: https://typeorm.io/docs/logging/]
- `logger` — selects a built-in logger (`advanced-console` default, `simple-console`, `formatted-console`, `file`, `debug`) or a custom implementation. [Source: https://typeorm.io/docs/logging/]
- `maxQueryExecutionTime` — logs any query exceeding this millisecond threshold as slow. [Source: https://typeorm.io/docs/logging/]
- `poolSize` — maximum number of active pooled connections.
- `extra` — driver-native escape hatch for options TypeORM doesn't model directly (e.g. `pg` pool tuning: `max`, `min`, `idleTimeoutMillis`, `connectionTimeoutMillis`). [Inference, not confirmed in docs: the exact `extra` sub-keys are driver-specific and were not individually verified per driver in this pass — treat the pg example as illustrative, not exhaustive.]
- `cache` — enables query-result caching (see Section 8). [Source: https://typeorm.io/docs/query-builder/caching/]
- `subscribers` — event subscriber classes/paths.
- `namingStrategy` — custom table/column naming logic.
- `isolationLevel` — sets a data-source-level default transaction isolation level, overridable per-transaction call. [Source: https://typeorm.io/docs/transactions/]
- `invalidWhereValuesBehavior` — as of v1.0, defaults to `throw`: passing `null`/`undefined` into a `where` condition now throws rather than being silently ignored. **[Version-sensitive: behavioral default changed in v1.0.0; pre-1.0 behavior differed.]** [Source: https://typeorm.io/docs/releases/1.0/release-notes/]

[Source: https://typeorm.io/docs/migrations/setup/] To use migrations at all, `synchronize` must be set to `false` — the docs frame this as mandatory, since automatic sync and migration-driven schema management conflict.

---

## 5. Recommended Patterns

[Source: https://typeorm.io/docs/migrations/why/] Once an application has real data in production, use **migrations**, not `synchronize: true`: *"it is unsafe to use `synchronize: true` for schema synchronization on production once you get data in your database."* The docs illustrate this with a worked example of renaming a production column safely via a migration rather than relying on auto-sync.

[Source: https://typeorm.io/docs/transactions/] For transactional work, prefer the callback-scoped API — `dataSource.transaction(async (transactionalEntityManager) => {...})` — over manually driving a `QueryRunner`, and *"DO NOT USE GLOBAL ENTITY MANAGER. All operations MUST be executed using the provided transactional entity manager"* inside that callback.

[Source: https://typeorm.io/docs/performance-optimization/introduction/] To avoid the N+1 query problem, use `leftJoinAndSelect`/`innerJoinAndSelect` (or the `relations` object syntax on `find*` calls) to fetch related rows in one query instead of triggering per-row follow-up queries.

[Source: https://typeorm.io/docs/relations/eager-and-lazy-relations/] Use `relationLoadStrategy: "query"` when you want eager-style automatic loading without SQL joins (loads related data as separate queries instead), and use `loadEagerRelations: false` to selectively disable eager loading for a specific query.

[Source: https://typeorm.io/docs/performance-optimization/pagination/] For large or frequently changing result sets, the docs recommend cursor-based pagination over plain offset/`limit`+`offset` pagination for "more efficient handling of dynamic data."

[Source: https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/] As of v1.0, use object-syntax `select`/`relations` on `find*` options rather than string arrays (string-based syntax was removed); for the `join` option specifically, use the `relations` object for LEFT JOINs or switch to QueryBuilder for INNER JOIN / other join types. **[Version-sensitive: v1.0.0 breaking change.]**

[Source: https://typeorm.io/docs/migrations/setup/] Use glob patterns covering both `.ts` and `.js` for the `migrations` option (e.g. `[__dirname + "/migrations/**/*{.js,.ts}"]`) so the same configuration works in development (ts-node) and in compiled Docker/production builds.

---

## 6. Anti-Patterns

[Source: https://typeorm.io/docs/relations/relations/] Relying heavily on `cascade` is called out as risky: *"Cascades may seem like a good and easy way to work with relations, but they may also bring bugs and security issues when some undesired object is being saved into the database."* The docs also note cascades are less explicit than manual `.save()` calls per entity.

[Source: https://typeorm.io/docs/relations/relations/] Cascade removal has a footgun: TypeORM only removes *populated* (loaded) relations, so a developer must explicitly load a relation before it will be cascade-removed — an easy-to-miss requirement.

[Source: https://typeorm.io/docs/relations/eager-and-lazy-relations/] Lazy relations (properties typed as `Promise<T>`) are explicitly flagged: *"a non-standard technique and considered experimental in TypeORM"* — the docs warn developers coming from statically-typed-language ORMs (Java, PHP) where lazy loading is transparent to be cautious, since in TypeORM it requires awaiting a promise.

[Source: https://typeorm.io/docs/relations/eager-and-lazy-relations/] Setting `eager: true` on both sides of the same relationship is disallowed: *"Eager relations can only be used on one side of the relationship, using `eager: true` on both sides of relationship is disallowed."*

[Source: https://typeorm.io/docs/data-source/data-source-options/] Leaving `synchronize: true` or `dropSchema: true` enabled outside of local development is explicitly called out as data-loss-prone in production (see exact quotes in Section 4).

[Source: https://typeorm.io/docs/transactions/] Mixing the global (non-transactional) `EntityManager`/`Repository` into code that's meant to run inside a transaction is explicitly disallowed by the docs' guidance (see Section 5 quote) — doing so silently breaks the transaction boundary.

---

## 7. Security

[Source: https://github.com/typeorm/typeorm/security/policy] TypeORM's security policy asks that vulnerabilities **not** be disclosed through public channels; reporters should use GitHub Security Advisories (`github.com/typeorm/typeorm/security/advisories/new`) or email `support@typeorm.io`, including vulnerability type, affected files, reproduction steps, and impact.

[Source: https://github.com/typeorm/typeorm/security/policy] The security guarantee is explicitly scoped to **data values only**. In-scope: untrusted data reaching queries unescaped through documented APIs; parameter-binding/escaping defects in drivers; database-derived content causing prototype pollution or code execution. **Out of scope**: untrusted input used in identifier or SQL-expression positions (the docs treat this as the developer's responsibility), hostile schema definitions/configuration control, and bypasses of optional runtime validation guards.

[Source: https://github.com/typeorm/typeorm/security/policy] Maintainers target an initial acknowledgment within 72 hours, then work fixes in private forks toward coordinated disclosure and CVE assignment where warranted. Not documented / could not verify: the policy page as fetched does not specify which released version lines (e.g. 0.3.x vs 1.x) currently receive security backports.

[Source: https://typeorm.io/docs/releases/1.0/release-notes/] v1.0 states: *"Parameterized queries and escaped identifiers now used across all drivers for schema introspection and DDL methods, preventing SQL injection."* It also documents new runtime validation for QueryBuilder `orderBy` conditions and for `.limit()` values on Update/SoftDelete query builders. **[Version-sensitive: these hardenings are new in v1.0.0 — earlier 0.3.x releases did not have this exact scope of parameterization for schema-introspection/DDL paths, per the release notes' own framing of it as a change.]**

[Source: https://typeorm.io/docs/data-source/data-source-options/] `invalidWhereValuesBehavior` defaulting to `throw` as of v1.0 (Section 4) is itself a security-relevant change: it prevents `null`/`undefined` values from silently matching unintended rows in `where` clauses. **[Version-sensitive: v1.0.0 default change.]**

Unresolved: whether any specific CVEs have been published against TypeORM and, if so, their IDs and affected version ranges — no CVE identifiers were surfaced by the official pages fetched in this research pass. Do not treat this as "TypeORM has no known CVEs"; it means this research did not locate an official CVE list to cite.

---

## 8. Performance

[Source: https://typeorm.io/docs/performance-optimization/introduction/] The docs frame performance work around four goals: reducing the number of SQL queries sent to the database, optimizing complex queries, using caching/indexing to speed up retrieval, and choosing efficient loading strategies — and name the N+1 query problem and under-use of indexing/caching as the common failure modes.

[Source: https://typeorm.io/docs/relations/eager-and-lazy-relations/] Eager relations default to `LEFT JOIN`, but TypeORM automatically switches to `INNER JOIN` when the relation is `nullable: false` and owns the join column (`ManyToOne`, or the owning side of `OneToOne`) — a documented micro-optimization.

[Source: https://typeorm.io/docs/performance-optimization/pagination/] Two pagination approaches are documented: offset-based (`.limit()` + `.offset()`), and cursor-based pagination, recommended for "more efficient handling of dynamic data" over plain offset pagination at scale.

[Source: https://typeorm.io/docs/query-builder/caching/] Query-result caching: enable with `cache: true` in data source options (this provisions a `query-result-cache` table on schema sync by default); default cache lifetime is **1000 ms**. Per-query overrides: `.cache(60000)` on QueryBuilder, or a cache ID + TTL pair like `.cache("users_admins", 25000)` for named/selectively-invalidatable cache entries via `queryResultCache.remove()`. `getMany()`, `getOne()`, `getRawMany()`, `getRawOne()`, `getCount()`, and repository `find*` methods can all be cached.

[Source: https://typeorm.io/docs/query-builder/caching/] Cache storage backends documented: the default database table, Redis/IORedis, IORedis Cluster, or a fully custom provider implementing the `QueryResultCache` interface. An `ignoreErrors` option lets a query fall through to the live database if the cache backend itself fails, preserving availability.

[Source: https://typeorm.io/docs/performance-optimization/introduction/] The performance section's own navigation groups sub-topics as: Query Builder, Indexes, Lazy and Eager Loading, Query Hints, Pagination, and Caching. Not documented / could not verify: this research did not individually fetch the Indexes and Query Hints sub-pages, so their specific content is not captured here beyond their existence as documented topics.

Not documented / could not verify: no connection-pooling-specific guidance (pool sizing recommendations, warm-up strategy, serverless/edge cold-start guidance) was found under the Performance section itself — pooling knobs exist only as configuration options (Section 4), not as a dedicated performance-tuning narrative in the pages retrieved.

---

## 9. Testing

Not documented / could not verify: no dedicated official "Testing" guide was found on typeorm.io during this research (direct navigation and targeted search both came up empty for an official testing/mocking page). All testing guidance discovered (Jest patterns, SQLite in-memory test databases, repository mocking) originated from third-party community sources (Medium posts, GitHub gists, community packages like "MockTypeORM"), which per this project's sourcing rules cannot be cited as primary claims here.

[Inference, not confirmed in docs] Because the docs do document `better-sqlite3` as the default SQLite driver as of v1.0 (Section 13) and document `synchronize`/`dropSchema` as schema-management tools (Section 4), an in-memory SQLite data source with `synchronize: true` is a plausible pattern for integration testing — but this is an inference from adjacent documented features, not a claim the official docs make about testing specifically.

---

## 10. Deployment

Not documented / could not verify: TypeORM's official docs do not appear to have a single dedicated "Deployment" guide (no such page was found via direct navigation or search).

[Source: https://typeorm.io/docs/migrations/setup/] Deployment-relevant configuration does exist piecemeal: the `migrations` glob pattern is documented as supporting both `.ts` and `.js` extensions specifically to support "Docker deployments" where compiled JS runs in production while TS runs in local dev.

[Source: https://typeorm.io/docs/migrations/executing/] `migration:run`/`migration:revert` CLI commands "only work on `.js` files" — meaning a TypeScript project must either compile migrations before running them in a deployed environment, or invoke them through the `typeorm-ts-node-commonjs` / `typeorm-ts-node-esm` wrapper binaries the docs document for TS execution.

[Source: https://typeorm.io/docs/data-source/data-source-options/] `migrationsRun` can auto-apply pending migrations at data-source initialization — a documented option relevant to deploy-time migration automation, though the docs do not editorialize on whether to use auto-run vs. an explicit CI/CD migration step.

---

## 11. Migration (Version Upgrades)

TypeORM's docs cover this dimension as *upgrading between TypeORM major versions* (0.3.x → 1.0), not as migrating from a comparable alternative ORM — no official "migrating from Sequelize/Prisma/etc." guide was found.

[Source: https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/] An automated codemod is provided: `npx @typeorm/codemod v1 src/` to mechanically apply most of the mechanical renames/removals below.

[Source: https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/] Key documented upgrade steps 0.3.x → 1.0:
- Node.js 20+ now required; ES2023 minimum target.
- `Connection`/`ConnectionOptions` → `DataSource`; `createConnection()` → `new DataSource(options).initialize()`; `.close()` → `.destroy()`.
- Global convenience functions (`getRepository()`, `createQueryBuilder()`, etc.) removed — use instance methods off a `DataSource`.
- `findOneById()`, `findByIds()`, `exist()` → `findOneBy()`, `findBy()` + `In()`, `exists()`.
- Find-options `join` property removed — use `relations` object syntax (LEFT JOIN) or QueryBuilder (other join types); string-based `select`/`relations` arrays must become object syntax.
- QueryBuilder `printSql()`, `onConflict()`, `setNativeParameters()` removed — use `getSql()`, `orIgnore()`/`orUpdate()`.
- Default behavior change: `null`/`undefined` in `where` conditions now throws by default instead of being silently ignored.
- Driver-specific: MySQL drops `connectorPackage` and some deprecated column options; SQLite requires `better-sqlite3` instead of `sqlite3`; MongoDB requires driver v7+.
- The built-in IoC container is removed entirely — integrate with an external DI framework (e.g. TypeDI, NestJS) or use the `DataSource` directly.

**[Version-sensitive: everything in this section applies specifically to the 0.3.x → 1.0.0 transition, effective with the 1.0.0 release on 2026-05-19.]**

[Source: https://typeorm.io/docs/migrations/why/] Separately (and this is the more commonly meant sense of "migration" for an ORM), TypeORM's core migrations feature — writing/generating/running SQL migration files to evolve a live schema — is the documented alternative to `synchronize: true` once a database holds real data; see Sections 4 and 5 for the mechanics.

---

## 12. Version Information

[Source: https://github.com/typeorm/typeorm/releases] Per the GitHub Releases API (`api.github.com/repos/typeorm/typeorm/releases`), the most recent published releases as of this research (2026-09-09) are:

| Version | Published (UTC) | Line |
|---|---|---|
| **1.1.1** | 2026-09-01 | current stable (1.x) |
| 1.1.0 | 2026-07-13 | 1.x |
| 0.3.31 | 2026-07-13 | 0.3.x (parallel/backport line) |
| **1.0.0** | 2026-05-19 | first 1.x major, breaking changes |
| 0.3.30 | 2026-05-18 | 0.3.x |
| 0.3.29 | 2026-05-08 | 0.3.x |
| 0.3.28 | 2025-12-03 | 0.3.x |
| 0.3.27 | 2025-09-19 | 0.3.x |
| 0.3.26 | 2025-08-18 | 0.3.x |
| 0.3.25 | 2025-06-19 | 0.3.x |
| 0.3.24 | 2025-05-14 | 0.3.x |
| 0.3.23 | 2025-05-07 | 0.3.x |
| 0.3.22 | 2025-04-03 | 0.3.x |
| 0.3.21 | 2025-03-03 | 0.3.x |
| 0.3.20 | 2024-01-26 | 0.3.x |

[Inference, not confirmed in docs] Cadence over the observed window is irregular but roughly monthly-to-quarterly for 0.3.x patch releases, with 1.x releases so far appearing roughly every ~1–2 months since the 1.0.0 launch; this is a pattern observed in the release timestamps above, not a cadence TypeORM's docs commit to in writing.

[Source: https://github.com/typeorm/typeorm/releases] The 0.3.x line continued receiving backported fixes (0.3.31) even after 1.0.0 shipped, indicating the maintainers ran a parallel-maintenance window around the 1.0 cutover rather than an immediate hard cutoff. Not documented / could not verify: no official statement of *how long* 0.3.x will continue receiving backports, or a formal end-of-support date, was found — there is no documented LTS/support-window policy for TypeORM as of this research.

[Source: https://typeorm.io/docs/releases/1.0/release-notes/] v1.0.0 is explicitly billed as carrying breaking changes, with dedicated release-notes and upgrade-guide pages (Sections 11 and 13) — consistent with SemVer major-version semantics, though the docs do not explicitly claim to follow SemVer as a stated policy in the pages retrieved.

---

## 13. Breaking Changes

All items below are the documented breaking changes for the **1.0.0** release (2026-05-19), the only major version boundary TypeORM's docs currently describe.

**Platform requirements** [Source: https://typeorm.io/docs/releases/1.0/release-notes/]: Node.js 20+ required (Node 16 and 18 no longer supported); ES2023 minimum compile target; the Buffer polyfill for non-Node platforms was removed, and binary data on browser/Deno/Bun is now represented as `Uint8Array` instead.

**Driver changes** [Source: https://typeorm.io/docs/releases/1.0/release-notes/]:
- MySQL: only `mysql2` supported; the legacy `mysql` package dropped.
- SQLite: `better-sqlite3` becomes the default driver; `sqlite3` no longer supported.
- MongoDB: driver v7+ required; v5/v6 support dropped.
- MS SQL Server: `domain` connection option removed; isolation-level string format changed from `READ_COMMITTED` to `"READ COMMITTED"`.
- SAP HANA: deprecated connection aliases removed.
- Expo driver deprecated; legacy Redis client support removed.

**Removed APIs** [Source: https://typeorm.io/docs/releases/1.0/release-notes/ and https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/]: `Connection`/`ConnectionOptions` (→ `DataSource`), `ConnectionManager` and global convenience functions (`createConnection`, `getConnection`, etc.), the `.connection` property (renamed `.dataSource`), `findByIds`/`findOneById` (→ `findBy`+`In()`/`findOneBy`), the `@RelationCount` decorator, the built-in IoC container, QueryBuilder's `printSql()`/`onConflict()`/`setNativeParameters()`, and string-based `select`/`relations` syntax (→ object syntax).

**Behavioral changes** [Source: https://typeorm.io/docs/releases/1.0/release-notes/]: non-nullable relations now default to `INNER JOIN` instead of `LEFT JOIN`; `invalidWhereValuesBehavior` now defaults to `throw` (null/undefined in `where` conditions now errors instead of being silently ignored); config-file and log-path resolution switched from the `app-root-path` package to `process.cwd()`.

**New in the same release** (for context, not itself breaking) [Source: https://typeorm.io/docs/releases/1.0/release-notes/]: `valuesFromSelect()` for `INSERT INTO ... SELECT FROM`, a `returning` option for update/upsert, `ifExists` on all drop methods, `await using` explicit-resource-management support, Postgres partial indexes and `ALTER TYPE ... ADD VALUE` enum changes, SQLite `jsonb` column support, and the `@typeorm/codemod` automated-migration package.

[Source: https://github.com/typeorm/typeorm/releases] Subsequent 1.x releases (1.1.0, 1.1.1) documented in their own changelogs are additive/fix releases (distinct-count query support, recursive-CTE fixes, cache/query-runner leak fixes, many-to-many cascade-default fix, version-comparison fix) — no further breaking changes have been documented past 1.0.0 as of 1.1.1 (2026-09-01).

---

## 14. Limitations

[Source: https://typeorm.io/docs/help/supported-platforms/] Node.js: "currently each commit is tested on Node.js 20 and 24" — Node 20+ required as of v1.0 (Section 13).

[Source: https://typeorm.io/docs/help/supported-platforms/] Browser: uses `sql.js`; requires Webpack configuration with `NormalModuleReplacementPlugin` and manual inclusion of `reflect-metadata` in the HTML page.

[Source: https://typeorm.io/docs/help/supported-platforms/] Cordova/Ionic: *"Currently no support for transactions when using the cordova-sqlite-storage plugin."* Ionic additionally requires a custom Webpack config.

[Source: https://typeorm.io/docs/help/supported-platforms/] NativeScript: requires NativeScript 4.x+; *"using webpack is compulsory"* — the raw `typeorm/browser` package is unbundled ES7 with import/export and "will NOT run as it is" without bundling; must be run via `tns run --bundle`.

[Source: https://typeorm.io/docs/help/supported-platforms/] Expo: relies on the Expo SQLite API. React Native: uses the `react-native-sqlite-storage` plugin.

[Source: https://typeorm.io/docs/relations/eager-and-lazy-relations/] `eager: true` cannot be set on both sides of the same relationship simultaneously — disallowed by design.

[Source: https://typeorm.io/docs/relations/eager-and-lazy-relations/] Lazy relations are explicitly labeled experimental/non-standard for TypeORM (Section 6), not a fully-supported first-class feature on par with eager loading.

[Source: https://typeorm.io/docs/transactions/] Isolation-level support is driver-dependent and TypeORM enforces this: *"TypeORM will throw an error if you request an unsupported level."* Documented per-driver support: Postgres/MySQL/MariaDB/SAP HANA support READ UNCOMMITTED–SERIALIZABLE; MS SQL Server additionally supports SNAPSHOT; Oracle supports only READ COMMITTED and SERIALIZABLE; CockroachDB supports READ COMMITTED/REPEATABLE READ/SERIALIZABLE (SERIALIZABLE default); Google Spanner supports REPEATABLE READ/SERIALIZABLE; SQLite supports only READ UNCOMMITTED and SERIALIZABLE. Aurora MySQL via the RDS Data API does not support isolation levels at all, "due to transport limitations with the stateless RDS Data API."

[Source: https://github.com/typeorm/typeorm/security/policy] The security model explicitly does *not* guarantee protection against untrusted input used in identifier/SQL-expression positions, or against hostile schema/config control — these are documented as the developer's responsibility, not TypeORM's (Section 7).

---

## 15. Debugging

[Source: https://typeorm.io/docs/logging/] Set `logging: true` (or an array of specific levels, or `logging: "all"`) in DataSource options to enable query/error logging. Documented levels: `query`, `error`, `schema`, `warn`, `info`, `log`.

[Source: https://typeorm.io/docs/logging/] Built-in loggers: `advanced-console` (default; colorized, SQL-syntax-highlighted), `simple-console` (same, no color), `formatted-console` (formats SQL via `@sqltools/formatter` for readability), `file` (writes to `ormlogs.log` by default, or a configured path), and `debug` (integrates with the `debug` npm package; enable via the `DEBUG=typeorm:*` environment variable).

[Source: https://typeorm.io/docs/logging/] `maxQueryExecutionTime` (ms) flags slow queries: the docs' own example — "This code will log all queries which run for more than `1 second`" — sets it to `1000`.

[Source: https://typeorm.io/docs/logging/] Custom loggers are built by implementing the `Logger` interface or extending `AbstractLogger`; request-scoped context can be attached via `QueryRunner.data` and surfaced in log output.

---

## 16. Integration

[Source: https://typeorm.io/docs/getting-started/] Officially documented database targets: MySQL/MariaDB, PostgreSQL, SQLite, Microsoft SQL Server, Oracle, SAP HANA, MongoDB, Google Spanner, and CockroachDB (the last inferred from its appearance as a distinct isolation-level/driver entry in Section 14, and from CockroachDB-specific fixes appearing in the 1.0/1.1 changelogs) — each documented driver has its own reference page under `typeorm.io/docs/drivers/` (e.g. a MongoDB driver page and a Microsoft SQL Server driver page were both directly observed to exist).

[Source: https://typeorm.io/docs/help/supported-platforms/] Officially documented runtime/platform targets beyond plain Node.js: Browser (via `sql.js`), Capacitor, Cordova/Ionic, Expo, NativeScript, React Native, and Electron (per Section 1) — each with its own caveats (Section 14).

[Source: https://typeorm.io/docs/query-builder/caching/] Cache-layer integration: Redis and IORedis Cluster are documented first-class cache-store backends alongside the default database-table store (Section 8).

Not documented / could not verify: TypeORM's own docs (typeorm.io) do not appear to carry a dedicated "Usage with Express" or "Usage with NestJS" integration guide. NestJS's official `@nestjs/typeorm` integration is documented on NestJS's own site, not TypeORM's — per this project's sourcing rules, that is a separate project's documentation and is not cited here as an official TypeORM claim. If a future skill needs NestJS+TypeORM specifics, that should be sourced from NestJS's own official docs, not inferred from TypeORM's.

[Source: https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/] The built-in dependency-injection container was removed in v1.0; the docs point toward external DI frameworks (naming TypeDI and NestJS) as the replacement integration path, without documenting the integration mechanics themselves on typeorm.io.

---

## 17. Production Considerations

[Source: https://typeorm.io/docs/migrations/why/] Do not run `synchronize: true` against a production database with real data — use migrations (Sections 4, 5, 11).

[Source: https://typeorm.io/docs/data-source/data-source-options/] Do not run `dropSchema: true` in production — it destroys all data on data-source initialization.

[Source: https://typeorm.io/docs/query-builder/caching/] For production-scale query caching, prefer a dedicated Redis/IORedis (or IORedis Cluster) cache store over the default database-table cache store, and use the `ignoreErrors` option so a cache-layer outage degrades to direct DB queries rather than failing requests.

[Source: https://typeorm.io/docs/migrations/setup/ and https://typeorm.io/docs/migrations/executing/] For production/CI deployment, migrations should be compiled to `.js` (the `migration:run`/`migration:revert` CLI only operates on `.js` files) or run through the documented `typeorm-ts-node-commonjs`/`typeorm-ts-node-esm` wrappers; `migrationsRun` can automate applying pending migrations at startup if that fits the deployment's operational model.

[Source: https://github.com/typeorm/typeorm/security/policy] Production deployments relying on TypeORM for SQL-injection protection should note the documented scope boundary: TypeORM's guarantees cover parameter/value escaping through documented APIs, not identifier/SQL-expression positions built from untrusted input — raw/dynamic SQL fragments remain the application's responsibility to sanitize (Sections 7, 14).

[Source: https://typeorm.io/blog/future-of-typeorm] Project governance/maintenance is a live, documented consideration for anyone evaluating TypeORM for new production work: the official blog states that TypeORM's maintenance "had slowed significantly" in recent years, and that Michael Bromley and David Hoeck (via a company called Elevantiq) are now leading the project, with a plan to establish a non-profit foundation under the Commons Conservancy, governed by a seven-member board plus a stakeholder Working Group, and to fund two full-time developers via corporate sponsorship (naming the OSS Pledge as one funding channel). [Inference, not confirmed beyond the blog post itself: this is a self-reported governance transition from the project's own blog, not independently corroborated in this research pass — treat it as the project's own account of its health and trajectory, useful context for a production-adoption risk assessment.]

[Source: https://typeorm.io/docs/transactions/] For write-heavy or invariant-sensitive production workloads, isolation-level selection is a documented per-driver decision (Section 14) — the default isolation level can be set once at the DataSource level (`isolationLevel` option) and overridden per-transaction where stronger guarantees (e.g. `SERIALIZABLE`) are needed.

---

## Sources Cited (deduplicated)

- https://typeorm.io/ — homepage/marketing overview
- https://typeorm.io/docs/getting-started/ — install requirements, core concepts, ActiveRecord/DataMapper
- https://typeorm.io/docs/entity/entities/ — entity/column/primary-key/inheritance reference
- https://typeorm.io/docs/data-source/data-source-options/ — full DataSource configuration reference
- https://typeorm.io/docs/working-with-entity-manager/working-with-repository/ — Repository/EntityManager API overview
- https://typeorm.io/docs/help/decorator-reference/ — full decorator catalog
- https://typeorm.io/docs/relations/relations/ — relation types, cascades, security caveat
- https://typeorm.io/docs/relations/eager-and-lazy-relations/ — eager/lazy relation semantics and restrictions
- https://typeorm.io/docs/transactions/ — transaction API, isolation levels per driver
- https://typeorm.io/docs/migrations/why/ — rationale for migrations over synchronize
- https://typeorm.io/docs/migrations/setup/ — migrations configuration options
- https://typeorm.io/docs/migrations/executing/ — migration CLI commands
- https://typeorm.io/docs/query-builder/caching/ — query-result caching
- https://typeorm.io/docs/performance-optimization/introduction/ — performance-topic index
- https://typeorm.io/docs/performance-optimization/pagination/ — pagination strategies
- https://typeorm.io/docs/logging/ — logging/debugging configuration
- https://typeorm.io/docs/help/supported-platforms/ — supported runtimes and per-platform limitations
- https://typeorm.io/docs/releases/1.0/release-notes/ — v1.0 breaking changes, features, security fixes
- https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/ — 0.3→1.0 upgrade guide and codemod
- https://typeorm.io/blog/future-of-typeorm — project governance/maintenance transition, roadmap framing
- https://github.com/typeorm/typeorm/releases — canonical release list and per-release changelog bodies (used via GitHub REST API for verified publish timestamps)
- https://github.com/typeorm/typeorm/security/policy — vulnerability reporting process and security scope

---

## Explicitly Unresolved Items

- Exact current minimum TypeScript version (docs state 4.5+; not re-verified as current given rapid 2026 changes around the v1.0 line).
- Whether TypeORM publishes a formal internal driver-interface/plugin-authoring document.
- The complete enumerated Repository/EntityManager method list (only a subset was directly verified from fetched pages).
- Which released version line(s) currently receive security backports per official policy (not stated on the security policy page as fetched).
- Any officially assigned CVE identifiers against TypeORM (none surfaced in official sources during this pass).
- Official 0.3.x end-of-support date / formal LTS window (no such policy page was found).
- Full content of the "Indexes" and "Query Hints" performance sub-pages (referenced by the performance index page but not individually fetched).
