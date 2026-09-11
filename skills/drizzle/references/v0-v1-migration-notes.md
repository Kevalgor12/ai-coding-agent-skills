# Drizzle v0 → v1 migration notes (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Every fact traces to
[research/technologies/drizzle.md §11–13](../../../research/technologies/drizzle.md)
— re-verify against current vendor docs before relying on any of this, per
this project's snapshot-date caveat (research current as of 2026-09-09).

**Framing:** everything below applies only to a project actually crossing the
v0.x → v1.0.0(-beta/rc) boundary. Since the npm `latest` tag is still 0.45.2,
most deployed Drizzle codebases have not crossed it yet, and pre-v1 APIs
(`relations()`, `.enableRLS()`, `getTableColumns()`, the global `casing`
option, chained `.array().array()`) remain correct for those projects — they
only "break" once a project actually upgrades
[Source: https://orm.drizzle.team/docs/v0-v1-changes].

## Official upgrade path

[Source: https://orm.drizzle.team/docs/upgrade-v1]

1. Install the `rc` (or `beta`) dist-tag of both packages together:
   `npm i drizzle-orm@rc drizzle-kit@rc` — Drizzle Kit's versioning is
   coupled to Drizzle ORM specifically for this transition.
2. Run `drizzle-kit up` to convert the legacy flat migration-folder format
   into the new v3 per-migration-folder structure.
3. Work through the breaking-changes list below and update application code
   accordingly.

No automated codemods are documented for this upgrade — it is described as a
manual, code-review-driven process
[Source: https://orm.drizzle.team/docs/upgrade-v1]. Codebases using legacy
Relational Queries (RQBv1) need an additional, separately-documented
migration to the v2 relational-query system, with distinct upgrade paths for
schema definitions vs. query call sites
[Source: https://orm.drizzle.team/docs/upgrade-v1]. The upgrade guide quotes
the beta.2 release notes directly as an explicit warning that this is not a
routine minor bump: "We've introduced a lot of changes in this version, and
something will definitely break"
[Source: https://orm.drizzle.team/docs/latest-releases/drizzle-orm-v1beta2].

## Full breaking-change list (v0 → v1)

[Source: https://orm.drizzle.team/docs/v0-v1-changes]

| Area | v0.x | v1.0.0(-rc) |
|---|---|---|
| Relational Queries | `relations()` + RQBv1 | `defineRelations(schema, (r) => ({...}))` (RQBv2); RQBv1 removed entirely |
| RLS enabling | `.enableRLS()` | `pgTable.withRLS('users', {...})` |
| Column naming convention | global `drizzle({ casing: 'camelCase' })` | table-level `snakeCase.table(...)` / `camelCase.table(...)`, applying to tables, views, materialized views, and schemas |
| Multidimensional arrays | chained `.array().array()` | string notation `column.array('[][]')` / `column.array('[][][]')` |
| `.generatedAlwaysAs()` | accepted raw string values | only accepts SQL expressions (`` sql`...` `` or a callback); raw strings rejected |
| Column-introspection utility | `getTableColumns()` | `getColumns()` |
| Migration folder format | flat `migration.sql` + `snapshot.json`, tracked via `journal.json` | v3 format: `journal.json` eliminated; SQL files and snapshots grouped per-migration folder; migrations matched by folder name, not timestamp |
| `drizzle-kit drop` | present | removed — the flat structure it operated on caused Git merge conflicts, which the new per-folder format is designed to avoid |
| Migrations tracking table | — | gains `name` and `applied_at` columns |
| `push`/`pull` schema scope | defaulted to `public` only | manages all schemas by default; `schemaFilter` gained glob-pattern support (e.g. `['public', 'app_*']`) |
| `push --strict` | opt-in strict confirmation flag | flag removed; strict confirmation is now the default; `--force` bypasses the prompt |
| Validator packages | `drizzle-zod` / `drizzle-valibot` as separate deps | folded directly into `drizzle-orm`; legacy Typebox support moved to `drizzle-orm/typebox-legacy` |
| Config loader | `esbuild-register` | `tsx`, plus top-level `await` support in `drizzle.config.ts` |

**Non-breaking v1 additions accompanying this transition**
[Source: https://orm.drizzle.team/docs/v0-v1-changes]: JIT Mappers (opt-in
compiled row mappers via `jit: true`, matching raw-driver performance), a
"Codecs" driver-aware transformation layer, new MSSQL/CockroachDB dialects
plus a NetlifyDB driver, Effect ecosystem integration (`@effect/sql-pg`
driver, `drizzle-orm/effect-schema`), SQL comment tagging (sqlcommenter-style,
e.g. `db.select().from(users).comment("tag_name")`), and column aliasing via
`.as()` (e.g. `users.age.as('ageOfUser')`).

## Internal architecture changes bundled into v1

[Source: https://orm.drizzle.team/docs/latest-releases/drizzle-orm-v1beta2,
https://orm.drizzle.team/docs/upgrade-v1] Drizzle Kit's introspection engine
was rewritten, reportedly reducing schema-introspection time from "10
seconds to under 1 second." The migrator now uses "DDL snapshots" plus
"commutativity checks" to detect non-commutative (order-dependent,
merge-conflicting) migrations across branches — aimed specifically at teams
generating migrations independently on parallel branches, to catch a
merge that would silently produce an inconsistent migration history.

## Unresolved items relevant to an upgrade

- **Runtime `casing` option status**: `docs/v0-v1-changes` describes the
  global `drizzle({ casing: 'camelCase' })` option as "replaced" by
  table-level builders, but whether it is fully removed in v1 or kept as a
  deprecated fallback was not independently confirmed against a directly
  fetched v1 API reference page
  [Source: https://orm.drizzle.team/docs/drizzle-config-file] — verify
  against current docs before relying on either behavior during an upgrade.
- **A `1.0.0-rc.5`-style build tag** was referenced by a third-party
  package-index/security-scanner site during the underlying research pass,
  suggesting the rc line may have advanced past `rc.4`; this was not
  independently confirmed against the official GitHub releases page or npm
  registry as a formally tagged release, and is noted only as a signal that
  the line was still moving, not as a confirmed version
  [Source: https://github.com/drizzle-team/drizzle-orm/releases].
- **`orm.drizzle.team/docs/latest-releases` staleness**: as fetched during
  the underlying research, this index page only listed entries through
  `v1.0.0-beta.2`, not the newer beta/rc releases visible on GitHub —
  treat `github.com/drizzle-team/drizzle-orm/releases` as the more current
  version-history source until this is confirmed fixed
  [Source: https://orm.drizzle.team/docs/latest-releases].

## Using this reference

Before starting an upgrade, confirm the project's actual pinned version via
`package.json`/the lockfile rather than the live docs. Read the official
`upgrade-v1` guide directly at time of use — this table is a checklist for
what to expect, not a substitute for the current, authoritative page.
