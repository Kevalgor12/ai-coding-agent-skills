# Version-sensitive migration facts (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Every fact traces to
[research/knowledge-maps/version-matrix.md](../../../research/knowledge-maps/version-matrix.md)
— re-verify against current vendor docs before relying on any of this, per
this project's snapshot-date caveat (research current as of 2026-09-09).

| Technology | Fact | Migration relevance |
|---|---|---|
| Prisma | MongoDB **not supported in v7**; docs instruct MongoDB users to stay on v6 until v8 restores support. | A migration plan for a MongoDB-backed Prisma project must confirm the Prisma major version before assuming v7-era migration commands apply. |
| Drizzle ORM | v1 removed Relational Queries v1 (`relations()`) entirely, replaced by `defineRelations()`; migration folder format changed (`journal.json` eliminated, `drizzle-kit drop` removed). Most production code is still on 0.x despite v1-era live docs. | Confirm which line (`0.x` vs `1.0.0-rc.*`) is actually pinned before following current docs literally — a 0.x project following v1 migration-folder guidance will break. |
| TypeORM | v1.0.0 (2026-05-19): requires Node ≥ 20; `mysql` driver dropped (only `mysql2` supported); SQLite default becomes `better-sqlite3`; MongoDB driver requires v7+. | A migration touching driver-level behavior on a pre-1.0 TypeORM codebase should not assume these requirements apply yet — confirm the version line. |
| MySQL | 8.4.0 **removed** (not deprecated) `AUTO_INCREMENT` on `FLOAT`/`DOUBLE` columns — affected tables must be altered *before* upgrading or the table cannot be upgraded. Also: cannot skip a bugfix/LTS series (5.7→8.0→8.4, not 5.7→8.4 direct). | Check for `FLOAT`/`DOUBLE` `AUTO_INCREMENT` usage before an 8.4+ upgrade; plan sequential upgrades, not version-skipping. |
| MongoDB | `featureCompatibilityVersion` (FCV) must be *fully* raised to the current version before upgrading binaries to a new major — restarting with a newer binary before FCV finishes can crash nodes. Minor-release upgrades must be sequential, no skipping (since 8.2). | Sequence FCV changes and binary upgrades carefully; don't skip minor versions when upgrading. |
| ClickHouse | Downgrades supported only to versions < 1 year old, and only if no newer features were used; large version jumps risk instability without an intermediate "stepping stone" version. | A ClickHouse schema/version migration spanning more than ~1 year of releases should plan an intermediate stop, not a direct jump. |

## Using this table

This is a **checklist to run before trusting current documentation
verbatim**, not a substitute for reading the actual migration guide for the
version pinned in the project. When in doubt about which version line a
project is actually on, check the lockfile/manifest rather than assuming
"latest" — several of these ORMs currently have live docs describing a newer
major version than what most production code actually runs.
