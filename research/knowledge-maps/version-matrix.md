# Version Matrix

**Cross-technology version-compatibility facts across the 44 profiled technologies**

> **Snapshot date: 2026-09-09.** Every fact below is a snapshot in time drawn from the underlying per-technology research (`research/technologies/*.md`), which itself traces to official documentation fetched around that date. Version numbers, support windows, and "current stable" claims move fast — **re-verify against live sources before treating any specific number here as current**, especially anything marked with a release-candidate, beta, or "as of" qualifier.

## How to read this document

This is a knowledge map, not a skill. It contains no step-by-step instructions for an agent to follow — it exists to inform future skill design by surfacing where version floors, ceilings, and breaking changes create cross-technology coupling.

- **Source of each fact**: every row carries a citation back to the official documentation URL the underlying technology research cited, abbreviated to a short label (e.g. `react.dev`, `npm registry`, `GitHub releases`). The full URL is recoverable from the corresponding `research/technologies/<slug>.md` file, which is the traceability chain this document inherits.
- **`[Synthesis]`** marks a connection *I* drew by combining two or more separately-sourced facts that did not individually state the connection. These are inferences, not documented claims — treat them as hypotheses to verify, not facts.
- **`[Gap]`** marks a place where the underlying research is silent or thin on a version-compatibility question that would plausibly matter for skill design. This is called out explicitly rather than filled in with a plausible-sounding guess.
- Facts are organized **by the technology whose own documentation stated the constraint** (per the source doc's `versionCompatibility` array), with the **target/cross-referenced technology** named in its own column. A single technology can appear both as a "stating" section and as a "target" inside many other sections — see the cross-reference index below to find every place a given technology is *targeted* by another's version claim.

---

## Part 1 — Runtime floor cross-reference

The single most cross-cutting version constraint in this dataset is **the minimum Node.js version a JavaScript-ecosystem tool requires.** Because so many of the 44 technologies are Node-hosted (frameworks, ORMs, build tools, test runners), collecting these floors into one table is more useful than reading them one profile at a time — this is the literal "matrix" the underlying data supports most directly.

| Technology | Minimum Node.js | Notes | Source |
|---|---|---|---|
| Express 5.x | ≥ 18 | 4.x requires only ≥ 0.10; 3.x required ≥ 0.8.0 (EOL 2015); 2.x required ≥ 0.4.1 (EOL 2012) | expressjs.com |
| Express (`app.query()`) | ≥ 20.19.3 or ≥ 22.2.0 | Tied to Node's own HTTP QUERY method support, distinct from Express's own floor | expressjs.com |
| Express + TypeScript (`node src/app.ts` direct execution) | ≥ 22.18.0 (or ≥ 23.6.0 on v23) with TypeScript ≥ 5.8 | Distinct from Express's own Node floor | expressjs.com |
| Fastify v5 | ≥ 20 (v18 dropped) | Justified by v20's `node:test` support and v18 nearing Node's own LTS end (Apr 2025) | fastify.dev |
| Fastify v6 (pre-release) | Unconfirmed, likely raised further | 6.0.0-alpha line in progress as of research date | GitHub releases |
| Next.js | ≥ 20.9 (as of 16.3.4) | Node 18 dropped as of v16 | nextjs.org |
| Nuxt 4.x | 22.x or newer (even LTS lines recommended) | Stricter than Nuxt 3's original requirement; 22.19+ needed once bundled `jiti` is removed | nuxt.com |
| Angular 22.0.x | `^22.22.3 \|\| ^24.15.0 \|\| ^26.0.0` | v20.0.0 dropped Node 18 and Node 22.0–22.10 | angular.dev |
| Angular 20.x/21.x | `^20.19.0 \|\| ^22.12.0 \|\| ^24.0.0` | — | angular.dev |
| Vite 8 | 20.19+ or 22.12+ | Required for its ESM-only distribution without flags | vite.dev |
| Vitest 5.0 | ≥ 22.12.0 | Also requires Vite ≥ 6.4.0 | vitest.dev |
| Jest (30.5.1) | `^18.14.0 \|\| ^20.0.0 \|\| ^22.0.0 \|\| >=24.0.0` | v30 dropped Node 14, 16, 19, 21 | npm registry |
| Playwright | Node "latest 22.x, 24.x, or 26.x" | Reference/primary implementation is Node.js/TypeScript | playwright.dev |
| TypeORM (v1.0) | ≥ 20 | Node 16 and 18 no longer supported as of v1.0 (2026-05-19) | typeorm.io |
| Mongoose 9 | ≥ 20.19.0 | — | mongoosejs.com |
| Prisma v7 | `^20.19.0, ^22.12.0, or ^24.0.0` (Active/Maintenance LTS only) | Raised from v6's 16.13/18.x/20.x floors | prisma.io |
| Socket.IO | ≥ 10 | "Older versions are not supported anymore" | socket.io |
| Husky | ≥ 18 (per published `package.json`) | No hard runtime presence during hook execution beyond a shell dispatcher, unless the hook itself invokes node/npm/npx | GitHub (typicode/husky) |
| Node.js `WebSocket` global client | Introduced v21.0.0 (backported to 20.10.0), flag removed v22.0.0, stable as of v22.4.0 | Client-only — Node ships no built-in WebSocket *server* | nodejs.org |
| Node.js native TypeScript "type stripping" | Experimental v22.6.0 → default-on v23.6.0/22.18.0 → stable v25.2.0/24.12.0 → flag removed v26.0.0 | Ignores `tsconfig.json` entirely; no enum/namespace/decorator/`.tsx` support | nodejs.org |

**`[Synthesis]`** Combining these floors: a project that needs Express 5, Next.js 16, Vitest 5, and TypeORM 1.0 simultaneously has an *effective* Node floor of **22.12+**, not any single package's stated minimum — the binding constraint is whichever dependency demands the newest runtime. A skill that scaffolds a multi-package stack should compute the max of all floors, not just check the primary framework's documented minimum.

**`[Gap]`** Go and Python are not part of this Node-floor table since they run on their own toolchains — see their own sections below (Part 4) for language-runtime version facts.

---

## Part 2 — Frontend frameworks

### React

| Target | Constraint | Source |
|---|---|---|
| `react` (npm) | Current major 19 (Dec 2024); current minor 19.2 (Oct 2025); `latest` dist-tag 19.2.8; active backport line 19.0.8 | npm registry (2026-09-09) |
| React Compiler | Works best with React 19; also supports 17/18 via the `react-compiler-runtime` package plus a minimum-target-version compiler config | react.dev |
| TypeScript | React 19 upgrade requires `react@^19.0.0 react-dom@^19.0.0` plus matching `@types/react`/`@types/react-dom` installed with `--save-exact` | react.dev |
| `react-server-dom-webpack` / `-parcel` / `-turbopack` | CVE-2025-55182 (CVSS 10.0) affected 19.0, 19.1.0, 19.1.1, 19.2.0 — fixed in 19.0.1/19.1.2/19.2.1; follow-up CVE-2026-23864 affected 19.0.0-19.0.3, 19.1.0-19.1.3, 19.2.0-19.2.3 — actually fixed in 19.0.4/19.1.5/19.2.4 | react.dev security advisories |
| Expo | React Compiler pre-configured by default in Expo SDK 54+ | react.dev |
| React Native | React Native DevTools (full React DevTools + native element inspection) built into React Native 0.76+; earlier versions need the standalone `react-devtools` package | react.dev |
| React 18.3 | Official 18→19 migration requires first upgrading to the *final* 18.3 release to surface 19-relevant deprecation warnings | react.dev |

### Next.js

| Target | Constraint | Source |
|---|---|---|
| Node.js | ≥ 20.9 as of 16.3.4 (Node 18 dropped in v16) | nextjs.org |
| TypeScript | ≥ 5.1.0 minimum; TypeScript 7 (`typescript@^7`) is opt-in for the `useTypeScriptCli` config, giving ~10x faster type checking | nextjs.org |
| React | App Router uses React **canary** releases (stable React 19 changes + newer framework-validated features); Pages Router uses whatever version the project's `package.json` declares | nextjs.org |
| `react-server-dom-*` | Patched to 19.0.6 / 19.1.7 / 19.2.6 in the May 2026 coordinated security release | vercel.com/changelog |
| CSP/SRI support | SRI-based experimental CSP added in v14.0.0; nonce/CSP-header parsing "recommended" since v13.4.20 | nextjs.org |
| Static export | `next export` deprecated v13.3.0, removed v14.0.0, replaced by `output: 'export'`; App Router static-export (RSC + Route Handlers) added v13.4.0 | nextjs.org |
| `next upgrade` CLI | Requires Next.js ≥ 16.1.0; earlier versions need `npx @next/codemod@canary upgrade latest` | nextjs.org |
| Async `next.config.js` | Supported since v12.1.0 | nextjs.org |
| `next typegen` CLI | Introduced in 15.5 | nextjs.org |
| All versions 13–14 | Affected by the May 2026 security advisories with **no direct patch** — effectively forces upgrade to 15.5.18+ or 16.2.6+ | vercel.com/changelog |

### Vue

| Target | Constraint | Source |
|---|---|---|
| Vue 2 | EOL 2023-12-31 — no new features/fixes/security patches from the core team; 2.7.16 is the final published line | vuejs.org |
| ECMAScript (Proxy) | Vue 2 used `Object.defineProperty()` getters/setters "due to browser support limitations" on `Proxy`; Vue 3's `reactive()` uses native `Proxy` — a core architectural split between majors | vuejs.org |
| Reactive Props Destructure | Available starting Vue 3.5 | vuejs.org |
| `defineOptions()` / `defineSlots()` | Introduced Vue 3.3; `defineModel()` at 3.4 | vuejs.org |
| Lazy Hydration strategies | Introduced Vue 3.5 | vuejs.org |
| `computed()` change-detection (only re-trigger on actual value change) | Dated to Vue 3.4 — a within-major behavioral shift, not on the formal breaking-changes page | vuejs.org |
| Vapor Mode | Scoped to the 3.6 line; as of research date npm `latest` still pointed at 3.5.42 while 3.6.0 sat at rc.7 — **not yet stable** despite some secondary sources calling it confirmed | npm registry, GitHub releases |
| TypeScript | Vue's semver carve-out: bundled type definitions may ship incompatible changes in a Vue *minor* because TypeScript itself breaks between its own minors — pin the Vue minor and upgrade TS types deliberately | vuejs.org |
| Pinia | Vue 2 support discontinued in 2025; Pinia docs now focus on Vue 3 | pinia.vuejs.org |
| Vue Router | v4.x targets Vue 3, v3.x targets Vue 2; a v5.x is referenced but flagged unresolved/unverified | router.vuejs.org |

### Nuxt

| Target | Constraint | Source |
|---|---|---|
| Node.js | 22.x+ recommended (even LTS lines) for the current 4.x line — stricter than Nuxt 3's original requirement | nuxt.com |
| Node.js (3→4 upgrade) | 22.19+ required once bundled `jiti` is removed, since config/modules load via native Node TS/ESM support | nuxt.com |
| `hydrate-on-visible` | Available from v3.16+ | nuxt.com |
| Vite | `future.compatibilityVersion: 5` (Nuxt 5 preview behaviors) requires Nuxt 4.2+ | nuxt.com |
| SSR streaming (`experimental.ssrStreaming`) | Introduced 4.5.0+ | nuxt.com |
| Cross-user payload disclosure (GHSA-wm8w-6qjm-cv43) | Affects apps on 4.4.0+ using `cache`/`swr`/`isr` route rules on authenticated pages | nuxt.com/blog |
| Current releases (2026-09-09) | Nuxt 4.5.2 (2026-08-05, stable); Nuxt 3.21.11 (~2026-08-05, maintenance); Nuxt 3.x reached EOL 2026-07-31; Nuxt 5.x planned ~Q4 2026 with a Nitro v3 upgrade | nuxt.com/roadmap |

### Angular

| Target | Constraint | Source |
|---|---|---|
| TypeScript | 22.0.x: `>=6.0.0 <6.1.0`; 21.0.x–21.2.x: `>=5.9.0 <6.0.0`; 20.0.x–20.3.x: `>=5.8.0 <6.0.0` — each major raised the floor as a breaking change | angular.dev |
| Node.js | 22.0.x: `^22.22.3 \|\| ^24.15.0 \|\| ^26.0.0`; 20.x/21.x: `^20.19.0 \|\| ^22.12.0 \|\| ^24.0.0` | angular.dev |
| RxJS | 20.x–22.x all require `^6.5.3 \|\| ^7.4.0` | angular.dev |
| Zone.js | Zoneless is stable/default in v21+; in v20 required opt-in via `provideZonelessChangeDetection()` (renamed from the Experimental-tier `provideExperimentalZonelessChangeDetection`) | angular.dev |
| Standalone components | Default `false` before v19.0.0; standalone-by-default as of v19+ | angular.dev |
| OnPush change detection | Default for undefined `changeDetection` as of v22 (previously Zone-checked "Default") | GitHub changelog |
| Vitest | Default test runner for new CLI projects as of v21+ (replacing Karma) | angular.dev |
| Browser Baseline policy | v20+ targets "widely available" Baseline (30-month window from a per-major date), vs. the pre-v20 fixed "2 most recent versions" policy | angular.dev |
| Release cadence | Changed at v22: prior majors were 6-month/1–3 minors; v22+ targets a major every 12 months with 4–6 minors | angular.dev |

---

## Part 3 — Backend frameworks & runtimes

### Express

| Target | Constraint | Source |
|---|---|---|
| Node.js | 5.x ≥ 18; 4.x ≥ 0.10; 3.x ≥ 0.8.0 (EOL 2015); 2.x ≥ 0.4.1 (EOL 2012) | expressjs.com |
| Node.js (`app.query`) | ≥ 20.19.3 or ≥ 22.2.0 | expressjs.com |
| Node.js + TypeScript (native `.ts` execution) | ≥ 22.18.0 (or ≥ 23.6.0 on v23) with TypeScript ≥ 5.8 | expressjs.com |
| `path-to-regexp` | 5.x's route-matching engine is built on a newer version, introducing named-wildcard/brace-based optional-segment syntax that differs from 4.x route-path syntax | expressjs.com |
| npm dist-tags | `latest` = 5.2.1 (2025-12-01); `latest-4` = 4.22.2 (2026-05-11) — the 4.x line continues receiving patches after 5.x became default | npm registry |

### Fastify

| Target | Constraint | Source |
|---|---|---|
| Node.js | v5 requires ≥ 20 (v18 dropped) | fastify.dev |
| Node.js (LTS policy) | Each major supported ≥ 6 months from release + 6 months security-only after the next major ships; v4 retired 2025-06-30 (already past EOL as of the research date) | fastify.dev |
| Node.js (v6 pre-release) | 6.0.0-alpha.0–alpha.3 in progress; alpha.0 removes deprecated APIs and raises the minimum Node version (exact new floor unconfirmed) | GitHub releases |
| `useSemicolonDelimiter` default | `false` (RFC 3986-compliant) as of v5, vs. a more permissive v4 default | fastify.dev |
| `logger` option | No longer accepts a pre-built logger instance in v5 — use the new `loggerInstance` option | fastify.dev |
| TypeScript | Reference docs build correspond to v5.12.1; `tsconfig` target should be es2017+ to avoid deprecation warnings | fastify.dev |
| Alternative Node runtimes (e.g. NodeSource N\|Solid) | Tested against Fastify majors by their own maintainers, with LTS scope aligned to the Fastify release tested | fastify.dev |

---

## Part 4 — Programming languages

### Go

| Target | Constraint | Source |
|---|---|---|
| Generics (type parameters) | Introduced Go 1.18; generic methods added Go 1.27; self-referential generic type declarations legal as of Go 1.26 | go.dev/ref/spec |
| Module-aware mode | Default since Go 1.16; explicit `require` for transitive deps since Go 1.17; `go` directive mandatory as of Go 1.21+ (toolchains refuse to build a module declaring a newer Go than they implement) | go.dev |
| `GOMEMLIMIT` | Introduced Go 1.19 | go.dev/doc/gc-guide |
| PGO (Profile-Guided Optimization) | Required explicit opt-in before Go 1.21; auto-detected/default from 1.21 onward | go.dev/doc/pgo |
| Bootstrap requirement | Go 1.26 requires Go 1.24.6+ to build the toolchain from source | go.dev |
| macOS floor | Go 1.27 raised the minimum to macOS 13 Ventura (macOS 12 support, present through 1.26, dropped) | go.dev |
| PowerPC (`ppc64`, Linux) | Now generates ELFv2 binaries by default as of 1.27, requiring Linux 3.13+ | go.dev |
| Support policy | Each major supported until two newer majors ship (~12 months); as of research date, Go 1.26 and 1.27 are supported, Go 1.25 is not | go.dev/doc/devel/release |
| Go 1 compatibility promise | Source-level only (no binary guarantee) across the 1.x series, with documented exceptions (security fixes, spec-bug corrections, unkeyed struct literals, `unsafe`-using code, frozen `syscall` package, `import .` collisions) | go.dev/doc/go1compat |
| FIPS 140-3 mode | Go 1.24+ ships a Go Cryptographic Module; in FIPS mode `crypto/tls` is restricted to approved protocols/ciphers, unsupported on OpenBSD, Wasm, AIX, 32-bit Windows | go.dev/doc/security/fips140 |

### Python

| Target | Constraint | Source |
|---|---|---|
| GIL (free-threaded builds) | Disable-at-build (`--disable-gil`) + runtime toggle (`-X gil=0` / `PYTHON_GIL=0`) as of 3.13 (experimental, PEP 703); "officially supported" as of 3.14 (PEP 779), overhead reduced to ~5–10% | docs.python.org |
| Sub-interpreters | Own per-interpreter GIL at the C-API level since 3.12 (PEP 684); exposed at stdlib level via `concurrent.interpreters` + `InterpreterPoolExecutor` in 3.14 (PEP 734) | docs.python.org |
| PEP 695 generic syntax | Added 3.12; `TypeIs` added 3.13; older `TypeVar`-based syntax remains supported | docs.python.org |
| `distutils` | Removed from stdlib in 3.12 (PEP 632) — migrate to `setuptools` | docs.python.org |
| `2to3` / `lib2to3` | Removed entirely in 3.13 (deprecated since 3.11); the `pyporting.html` HOWTO itself discontinued as of 3.11 | docs.python.org |
| `ProcessPoolExecutor` default start method | Changes from `fork` to `forkserver` on non-macOS Unix as of 3.14 | docs.python.org |
| Incremental GC | Shipped in 3.14.0–3.14.4, reverted to 3.13's generational GC within the 3.14 bugfix series (3.14.5+) due to memory-pressure reports — **"Python 3.14" alone is not precise enough**; patch version matters | docs.python.org |
| iOS / Android / Emscripten support | iOS (Tier 3, PEP 730) and Android (Tier 3, PEP 738) landed 3.13; 3.14 added official Android binaries and re-elevated Emscripten to Tier 3 (PEP 776) after wasm32-emscripten lost officially-supported status in 3.13 | docs.python.org |
| Tail-call interpreter build (`--with-tail-call-interp`, 3.14) | Requires Clang 19+ on x86-64/AArch64 | docs.python.org |
| PEP 2026 (calendar versioning) | **Rejected** by the Steering Council — sequential 3.15, 3.16, … numbering continues, reportedly partly over wheel-filename/version-parsing ecosystem compatibility | peps.python.org |

---

## Part 5 — Databases (relational, NoSQL, OLAP, search, cache)

### PostgreSQL

| Target | Constraint | Source |
|---|---|---|
| Protocol version | 3.2 introduced in PostgreSQL 18 (256-bit cancel keys); 3.0 (PG 7.4+) remains supported for backward compatibility | postgresql.org |
| `pg_upgrade` | Supports upgrading from 9.2+ up to the current major; requires binary compatibility (32/64-bit, certain compile-time settings); cannot upgrade clusters with certain OID-reference pseudo-type columns | postgresql.org |
| Python | PG 18 raised the toolchain floor: Python ≥ 3.6.8 (up from 3.5.x), OpenSSL ≥ 1.1.1, LLVM ≥ 14; HP-PA/PA-RISC support dropped | postgresql.org |
| Support window | 5 years per major post-release; minor releases ≥ every 3 months. As of the research date, PG 14 is nearing EOL (2026-11-12), PG 19 is in Beta 3 (2026-08-13), PG 18 is the current stable baseline | postgresql.org |
| Post-upgrade `ANALYZE` | As of PG 18, `pg_upgrade` carries forward optimizer statistics, reducing the need for a full post-upgrade `ANALYZE` previously required | postgresql.org |

### MySQL

| Target | Constraint | Source |
|---|---|---|
| Versioning scheme | 9.7 is the last release on traditional MAJOR.MINOR.PATCH; starting **MySQL 26.7.0**, Innovation releases switch to calendar-based **YY.M.P** versioning | Oracle MySQL blog |
| Upgrade paths | Cannot skip a bugfix/LTS series (5.7 → 8.0 → 8.4, not 5.7 → 8.4 direct); Innovation-to-Innovation upgrades cannot skip across an LTS boundary | dev.mysql.com |
| AUTO_INCREMENT on FLOAT/DOUBLE | Removed (not just deprecated) as of 8.4.0 — tables using it must be altered *before* upgrading, or the table "cannot be upgraded" | dev.mysql.com |
| Support lifecycle | 5.7 → Oracle Lifetime Sustaining Support (EOL) as of 2023-10-25; 8.0 → Lifetime Sustaining Support as of 2026-04-21, with users pushed toward 8.4 LTS or 9.7 LTS | mysql.com/support |
| 8.4.0 breaking changes | Extensive and version-gated: replication SQL syntax renamed (`START SLAVE` → `START REPLICA`), `mysql_native_password` disabled by default, `default_authentication_plugin` removed, `SET_USER_ID` privilege removed, `authentication_fido*` → `authentication_webauthn`, keyring plugins → component equivalents, `--ssl`/`--admin-ssl`/`have_ssl`/`have_openssl` removed, `INFORMATION_SCHEMA.TABLESPACES` removed, `mysql_upgrade`/`mysqlpump`/`mysql_ssl_rsa_setup` removed | dev.mysql.com |
| Concurrent version lines (July 2026 GA wave) | MySQL 26.7.0 (Innovation), MySQL 9.7.2 LTS, and MySQL 8.4.11 LTS all current simultaneously — old and new numbering schemes coexist | Oracle MySQL blog |

### MongoDB

| Target | Constraint | Source |
|---|---|---|
| CPU instruction set | 5.0+ requires AVX (Intel Haswell+ / AMD Bulldozer+ / ARMv8.2-A+) | mongodb.com |
| Linux kernel | **Incompatible** with kernel 6.19–7.0.13 (TCMalloc incompatibility causing crashes, across *all* package forms including Docker images); fix is upgrading to 7.0.14+ | mongodb.com |
| Multi-document ACID transactions | Replica sets since 4.0; sharded clusters since 4.2 | mongodb.com |
| `featureCompatibilityVersion` (FCV) | Must be *fully* raised to the current version before upgrading binaries to a new major — restarting with a newer binary before FCV finishes upgrading can crash nodes | mongodb.com |
| Driver support | Drivers released more than 3 years after a server version's EOL date will not be compatible with that server version | mongodb.com/legal |
| Transparent Hugepages | Flips by version: enable as of MongoDB 8.0+, but *disable* on 7.0 and earlier | mongodb.com |
| Field names with dots/`$` | Allowed (with restrictions) as of MongoDB 5.0 | mongodb.com |
| Direct-to-shard DDL | As of 8.3, DDL operations and `applyOps` run only on `mongos` for *all* sharded clusters, tightening the 8.0 restriction | mongodb.com |
| Storage-engine transaction tickets | Dynamic auto-tuning algorithm as of 7.0, capped at 128 read / 128 write tickets | mongodb.com |
| Minor-release sequencing | Since 8.2, minor releases (8.2, 8.3, …) are production-suitable but may not support Atlas Live Migration/`mongosync`; upgrades through minors must be sequential, no skipping | mongodb.com |

### Mongoose

| Target | Constraint | Source |
|---|---|---|
| Node.js | ≥ 20.19.0 for Mongoose 9 | mongoosejs.com |
| MongoDB compatibility matrix | 8.x ↔ `^8.7.0\|^9.0.0`; 7.x ↔ `^7.4.0\|^8.0.0\|^9.0.0`; 6.x ↔ `^7.0.0\|^8.0.0\|^9.0.0`; 5.x/4.4.x/4.2.x ↔ `^6.0.0\|^7.0.0\|^8.0.0`; 4.0.x ↔ `^6.0.0\|^7.0.0\|^8.0.0<8.16.0`; 3.6.x ↔ `^6.0.0\|^7.0.0\|^8.0.0<8.8.0` | mongoosejs.com |
| TypeScript | Officially supported since Mongoose v5.11.0 | mongoosejs.com |
| CVE-2026-42334 (`sanitizeFilter` `$nor` bypass) | Affects `<6.13.9`, `7.0.0-7.8.8`, `8.0.0-8.22.0`, `9.0.0-9.1.5`; patched in `^6.13.9`/`^7.8.9`/`^8.22.1`/`^9.1.6` | GitHub Security Advisories |
| Underlying MongoDB driver | Bumped to 7.5 in Mongoose 9.8.0 (2026-07-20), to 7.2 in Mongoose 9.6.0 (2026-04-28) | GitHub CHANGELOG |
| Support windows | Mongoose 8's stated support window ("through 2026-02-01") is in documented **tension** with 8.24.x patches observed shipping past that date; Mongoose 6 EOL 2027-02-01 (security/requested-fix only until then); Mongoose 5 EOL 2024-03-01, no longer maintained | mongoosejs.com |
| `updatePipeline` | Defaults to disabled/opt-in starting Mongoose 9 (previously always-allowed) | mongoosejs.com |

### Drizzle ORM

| Target | Constraint | Source |
|---|---|---|
| npm dist-tags | `drizzle-orm` `latest` resolves to **0.45.2**; `v1.0.0-rc.4` is the newest GitHub release in an active rc line — most production codebases remain on v0.x even though the live docs are already rewritten for v1 APIs | npm registry |
| PostgreSQL | `unique()`'s `NULLS NOT DISTINCT` option specifically targets Postgres 15+ | orm.drizzle.team |
| Drizzle Kit | Versioning coupled to Drizzle ORM for the v1 transition — installed together via the `rc` tag during beta/rc | orm.drizzle.team |
| Relational Queries v1 (RQBv1) | Removed entirely in v1, replaced by `defineRelations()` (RQB v2) — v0.x examples using legacy `relations()` will not match current live docs | orm.drizzle.team |
| Migration folder structure (v3 format) | Changed in v1: `journal.json` eliminated, SQL files/snapshots grouped per-migration, `drizzle-kit drop` removed to prevent Git merge conflicts | orm.drizzle.team |

### Prisma

| Target | Constraint | Source |
|---|---|---|
| Node.js | v7 requires `^20.19.0, ^22.12.0, or ^24.0.0` (Active/Maintenance LTS only) — do not apply v7 minimums to a v6 project | prisma.io |
| TypeScript | v7 requires ≥ 5.4 (optional, TS-only); v6 required only ≥ 4.7 | prisma.io |
| MongoDB | **Not supported in v7** — docs explicitly instruct MongoDB users to "continue using Prisma ORM v6 for now"; support planned to return via Prisma 8 | prisma.io |
| Latest releases | 7.10.0 (2026-08-25) is the latest *stable*; 8.0.0-rc.8 (2026-08-26) is the latest release *overall* but remains an RC with no stable 8.0.0 GA — blog: "Prisma 7 is still the right choice for your production apps," 12 months of continued v7 support committed | GitHub releases, prisma.io/blog |
| SemVer policy (v3.x+) | MAJOR = breaking changes to GA features only; MINOR = backward-compatible additions (breaking only for opt-in Preview/Early-Access features); PATCH = backward-compatible fixes | prisma.io |
| Rust-free architecture (TS/WASM query compiler + driver adapters) | Preview under v6; GA as non-default option at v6.16.0; became the **v7.0.0 default** (2025-11-19) — do not assume Rust-free behavior on a v6.x project pinned to the classic engine | prisma.io |
| Multi-file schema (`prisma/schema/`) | Requires v6.7.0+; `prisma.config.ts` reached GA at v6.13.0 | prisma.io |
| Pagination method rename | Prisma 8 rc.7 renamed `take()`/`skip()` to `limit()`/`offset()`, **conflicting** with the current `orm-client` reference docs example still showing `take()` — an unresolved conflict between official sources pending v8.0.0 GA | GitHub releases |
| Supported databases | PostgreSQL 9.6–18, MySQL 5.6–8.4, MariaDB 10.0+/11.0+, SQL Server 2017/2019/2022, MongoDB 4.2+, CockroachDB 21.2.4+, SQLite — all GA; **Cloudflare D1 is Preview-status** | prisma.io |

### TypeORM

| Target | Constraint | Source |
|---|---|---|
| TypeScript | ≥ 4.5 with `experimentalDecorators` + `emitDecoratorMetadata` enabled — doc flags this figure as potentially stale given the pace of 2026 changes around the v1.0 line | typeorm.io |
| Node.js | v1.0.0 (2026-05-19) requires ≥ 20; Node 16/18 no longer supported; ES2023 is the minimum compile target | typeorm.io |
| MongoDB driver | v1.0 requires driver v7+; v5/v6 support dropped | typeorm.io |
| SQLite driver | `better-sqlite3` becomes the default as of v1.0; `sqlite3` no longer supported | typeorm.io |
| MySQL driver | Only `mysql2` supported as of v1.0; legacy `mysql` package dropped | typeorm.io |
| NativeScript | Requires 4.x+; Webpack bundling is compulsory since the raw `typeorm/browser` package is unbundled ES7 that won't run without it | typeorm.io |
| Version-boundary structure | v1.0.0 (2026-05-19) is the sole documented major-version boundary, billed as carrying breaking changes vs. the 0.3.x line, which continued receiving parallel backports (e.g. 0.3.31 on 2026-07-13) after 1.0.0 shipped | GitHub releases |

### ClickHouse

| Target | Constraint | Source |
|---|---|---|
| LTS releases | 26.8 (2026-08-27) is documented LTS; LTS ships twice yearly (historically March/August) with ≥ 1-year support, current + prior LTS overlapping | clickhouse.com/changelogs |
| Stable track | Monthly releases; three most recent get bug-fix support (support-duration figures flagged as needing re-verification); Stable is the documented default recommendation for production | clickhouse.com |
| `tokenbf_v1` / `ngrambf_v1` skip indices | Deprecated as of 26.2+ | clickhouse.com |
| `max_insert_threads` | Changed from `1` to `auto` in **26.8**, making `INSERT SELECT` parallelized by default — a breaking change affecting part creation and row ordering vs. prior versions | clickhouse.com/changelogs |
| Cluster node version skew | Downgrades supported only to versions < 1 year old (and only if no newer features were used); nodes differing by > 1 year risk instability — intermediate "stepping stone" versions recommended for large jumps | clickhouse.com |
| ClickHouse Keeper | Does not need lock-step upgrades with the server unless a security fix targets Keeper or Apache ZooKeeper specifically | clickhouse.com |

### Redis

| Target | Constraint | Source |
|---|---|---|
| RESP protocol | RESP2 standard since Redis 2.0; RESP3 opt-in since 6.0 (via `HELLO`); from Redis 7 onward both RESP2 and RESP3 clients can invoke all core commands (reply typing may differ) | redis.io |
| ACLs | Introduced in Redis 6; subcommand-level allow/block syntax + key-pattern read/write scoping (`~R`/`%W~`) arrived 7.0; ACL comment lines in external files arrived 8.8 | redis.io |
| Licensing / naming | As of **Redis 8.0** (May 2025): Community Edition renamed **Redis Open Source**, license changed to tri-license (RSALv2/SSPLv1/AGPLv3); 7.4/7.2 remain RSALv2/SSPLv1 (no AGPL option); 7.2 and earlier were BSD-3-Clause. Standalone RediSearch/RedisJSON/RedisTimeSeries/RedisBloom modules bundled into Redis itself as of 8.0 | redis.io release notes |
| Redis Cluster minimum topology | ≥ 3 master nodes minimally; production recommendation is 6 nodes (3 masters + 3 replicas) | redis.io |
| Kubernetes | The Enterprise operator targets CNCF-conformant Kubernetes specifically; no official Redis Open Source (non-Enterprise) Kubernetes deployment path was found | redis.io |
| ACL category widening (8.0) | `@read`/`@write`/`@dangerous`/`@admin`/`@slow`/`@fast` categories now include Search/JSON/time-series/Bloom/Cuckoo/Top-K/count-min/t-digest commands — **silently widens or narrows existing ACL rules**, an explicit breaking change requiring re-analysis on upgrade | redis.io release notes |

### OpenSearch

| Target | Constraint | Source |
|---|---|---|
| JDK | 3.0 requires JDK 21 minimum — a hard break from the 1.x/2.x Java baseline | GitHub issue #3351 |
| Apache Lucene | 3.0 upgraded the search core to Lucene 10 | GitHub issue #3351 |
| Apache HttpClient | 3.0 moved the transport layer to HttpClient 5.x, permanently disabled the Java Security Manager, realigned XContent/Jackson limits to Jackson 2.16.0 defaults, removed the `transport-nio` plugin | GitHub issue #3351 |
| Current stable | 3.8.0 (2026-08-04); 3.9.0 RC window Sep 15–29 2026; 3.10.0 RC window Nov 3–17 2026 — ~8-week minor cadence | opensearch.org/releases |
| Support lifecycle | 1.x EOL (maintenance ended 2025-05-06); 2.x in maintenance until 4.0 GA, with 2.19.x patches scheduled through Dec 2026 (latest patch 2.19.6, 2026-07-02); 3.x is the actively developed major | opensearch.org/releases |
| Support commitment | Versions stay under maintenance until the next major enters maintenance, or 1 year passes, whichever is longer; medium+ severity vulns patched within 60 days of public disclosure in actively maintained versions | opensearch.org/releases |

---

## Part 6 — Build tools & test runners

### Vite

| Target | Constraint | Source |
|---|---|---|
| Node.js | Vite 8 requires 20.19+ or 22.12+ for its ESM-only distribution without flags | vite.dev/blog |
| TypeScript | Type-definition changes can occur across Vite *minor* versions (tracking TypeScript's own evolution) — TS users should pin/lock the Vite minor when upgrading | vite.dev/releases |
| Environment API | Introduced in Vite 6; Vite 5 and earlier supported only two implicit environments (client, SSR) | vite.dev |
| Browser target baseline | v7→v8 migration moved `build.target` forward (Chrome/Edge 107→111, Firefox 104→114, Safari 16.0→16.4) to track Baseline Widely Available as of a January-2026 cutoff | vite.dev/migration |
| `rolldown-vite` (interim package) | "Implements Vite 7 with Rolldown, without other Vite 8 changes" — lets teams adopt the Rolldown bundler ahead of/instead of the full v8 upgrade | vite.dev/blog |

### Vitest

| Target | Constraint | Source |
|---|---|---|
| Vite / Node.js | Vitest 5.0 requires Vite ≥ 6.4.0 and Node.js ≥ 22.12.0 — older versions "unsupported and may cause unexpected errors" | vitest.dev |
| Security-patch backport window | Only vitest@5.0 (current stable) and vitest@4.1 (immediately preceding minor) receive backported security patches | vitest.dev/releases |
| V8 coverage-provider accuracy | Report accuracy "as good as with Istanbul" **since v3.2.0** specifically — a version-sensitive parity claim | vitest.dev |
| `workspace` config | Deprecated as of v3.2, replaced by `projects` (functionally equivalent) | vitest.dev |
| `vi.when()` / `toHaveBeenExhausted()` | New in v5.0 | vitest.dev/blog |
| Fake timers + Temporal API | As of v5.0, fake timers also mock the Temporal API via `@sinonjs/fake-timers` v15.4 | vitest.dev |
| Browser Mode | Requires ES modules, dynamic imports, `BroadcastChannel`; minimum browsers Chrome ≥ 87, Firefox ≥ 79, Safari ≥ 15.4, Edge ≥ 88 | vitest.dev |

### Jest

| Target | Constraint | Source |
|---|---|---|
| Node.js | 30.5.1 requires `^18.14.0 \|\| ^20.0.0 \|\| ^22.0.0 \|\| >=24.0.0` — v30 dropped Node 14, 16, 19, 21 | npm registry |
| TypeScript | v30 raised the minimum supported version to 5.4 | jestjs.io/blog |
| jsdom | v30's `jest-environment-jsdom` upgraded jsdom 21 → 26, introducing spec-compliance changes (e.g. `window.location` mocking) | jestjs.io/blog |
| ESM automocking + `__mocks__` | Only apply starting at **Node v24.9+**; native ESM overall remains experimental, depending on Node's `--experimental-vm-modules` flag | jestjs.io |
| Default test runner (v27) | Became `jest-circus` (previously `jest-jasmine2`); `testEnvironment` default changed `jsdom` → `node`; fake timers default changed `legacy` → `modern` | jestjs.io/blog |
| CLI flag rename | v30 renamed `--testPathPattern` → `--testPathPatterns` (now multi-pattern); removed deprecated `expect` matcher aliases (`toBeCalled`, `toBeCalledWith`, etc.) present through v29 | jestjs.io |
| `glob` dependency | v30 bumped to glob v10, with stricter brace-expansion/extglob handling that can change matching behavior for custom `testMatch`/`moduleNameMapper` patterns vs. prior majors | jestjs.io/blog |

### Playwright

| Target | Constraint | Source |
|---|---|---|
| Node.js | "Latest 22.x, 24.x or 26.x"; OS support: Windows 11+/Server 2019+/WSL, macOS 14+, Debian 12/13 or Ubuntu 22.04/24.04/26.04 | playwright.dev |
| v1.63 | Ubuntu 20.04 no longer supported; experimental component-testing packages (`@playwright/experimental-ct-react[-17]`, `-vue`) deprecated in favor of the stable component-testing model | playwright.dev |
| v1.62 | Debian 11 EOL announced; new stable component-testing model (stories/galleries + `fixtures.mount()`) introduced | playwright.dev |
| v1.60 | Removed several long-deprecated APIs (`Locator.ariaRef()`, `exposeBinding()`'s `handle` option, `logger` option on `connect()`/`connectOverCDP()`, `context.videoPath()`/legacy video-size options) | playwright.dev |
| macOS WebKit | (believed v1.52, unconfirmed) macOS 13 WebKit support deprecated; `route.continue()` lost the ability to override the `Cookie` header | playwright.dev |
| Docker images | Tagged per Playwright version + Ubuntu base (e.g. `v1.63.0-noble`) — pin the image tag to the exact Playwright version so bundled browsers match the automation code's version | playwright.dev |
| Alpine Linux | Explicitly **unsupported** as a Docker base (musl libc incompatibility with bundled browser builds) | playwright.dev |

---

## Part 7 — Styling & component libraries

### CSS (spec)

| Target | Constraint | Source |
|---|---|---|
| `box-sizing` | Baseline widely available since July 2015 | MDN |
| `@container` (container queries) | Baseline widely available, established Feb 2023 | MDN |
| `@property` | Baseline *newly* available since July 2024 — expect gaps on older browsers | MDN |
| `will-change` | Baseline widely available since Jan 2020 | MDN |
| CSS Nesting Module Level 1 | Comparatively new (MDN page carried a "last update November 2025" note) — check current browser-compat tables before production use; positioned as a native replacement for Sass/Less nesting | MDN |
| Post-CSS3 versioning | No single version number; CSSWG publishes an annual **CSS Snapshot** Group Note (2018/2023/2024/2025/2026 editions identified) as the closest "current state of CSS" reference, aimed at implementers not authors | w3.org |

### Sass

| Target | Constraint | Source |
|---|---|---|
| Legacy JS API (`render()`/`renderSync()`) | Deprecated but "will continue to be supported until the release of version 2.0.0 of the `sass` package" (not yet released) | sass-lang.com |
| `@import` | Deprecation warnings started at Dart Sass 1.80.0; deprecation period runs until **Dart Sass 3.0.0**, which will not release sooner than two years after 1.80.0 | sass-lang.com |
| Current reference target | Dart Sass 1.104.0 (as of 2026-09-09), with recent releases (1.103.1/1.103.0/1.102.0/1.101.7) shipping roughly every 1–4 weeks | sass-lang.com, GitHub releases |
| Tar-permissions security bug | Affected `sass-embedded` npm package before 1.54.5 and the RubyGems non-native package before 1.56.2 | sass-lang.com/blog |
| Breaking-changes catalogue | 25+ dated entries pinned to specific releases, e.g. adjacent compound selectors (1.100.0), legacy `if()` function (1.95.0), `@import` (1.80.0), legacy JS API/Color API deprecations (1.79.0) | sass-lang.com |
| Node Sass (LibSass wrapper) | Reached EOL 2024-07-24 — npm package deprecated, GitHub repo archived | sass-lang.com/blog |
| LibSass / Ruby Sass | Both declared deprecated 2020-10-26; LibSass reported (unconfirmed, search-summarized) to have had no commits since Dec 2023, EOL around Oct 2025 | sass-lang.com/blog |

### Tailwind CSS

| Target | Constraint | Source |
|---|---|---|
| Browser floor (v4.0) | Requires Safari 16.4+, Chrome 111+, Firefox 128+ due to dependence on `@property` and `color-mix()` — teams needing older-browser support must stay on **v3.4** | tailwindcss.com |
| Node.js (upgrade codemod) | `npx @tailwindcss/upgrade` (v3→v4 migration) requires Node.js 20+ | tailwindcss.com |
| npm dist-tags | `latest` = 4.3.3; `v3-lts` = 3.4.19 (patched as recently as 2025-12-10 — confirming ongoing v3-line backport support well over a year after v4.0) | npm registry |
| Default color palettes | v4.2.0 (2026-02-18) added four new palettes (mauve, olive, mist, taupe) that don't exist prior — code/snapshots referencing them fail on earlier v4.x or any v3.x | x.com (corroborated by tailwindcss.com/blog) |
| Arbitrary CSS-variable syntax | v4's `bg-(--brand-color)` replaced v3's bracket syntax `bg-[--brand-color]` — breaking syntax change between majors | tailwindcss.com |
| `@custom-variant` / `@variant` split | Stable as of v4.0; `@custom-variant` is a renamed form of an earlier pre-stable-v4-beta `@variant-for-definition` syntax | GitHub CHANGELOG |
| Legacy-JS-config compatibility bridge (`@config`/`@plugin`) | Does not support `corePlugins`, `safelist`, or `separator` options when bridging a v3-style config into v4.0; unconfirmed whether later 4.x patches expanded this | tailwindcss.com |

### shadcn/ui

| Target | Constraint | Source |
|---|---|---|
| CLI package | Current stable `shadcn` (no `-ui` suffix) is 4.21.0 on npm (2026-09-04); legacy `shadcn-ui` package name is deprecated/unmaintained | npmjs.com |
| Headless-primitive default | As of **July 2026**, newly scaffolded projects default to **Base UI** (v1.6.0, 6M+ weekly downloads) instead of Radix UI; Radix remains supported via `shadcn init -b radix` | ui.shadcn.com/changelog |
| Tailwind v3 + React 18 projects | Continue to work unchanged (non-breaking); only *new* projects default to Tailwind v4 + React 19 | ui.shadcn.com |
| React 19 + Next.js 15 | npm may surface peer-dependency errors for packages not yet declaring React 19 compatibility; Recharts specifically needs a `package.json` `overrides` pin to a `19.0.0-rc` build of `react-is`, then `npm install --legacy-peer-deps` | ui.shadcn.com |
| CLI major version 4 | Introduced March 2026 — added `shadcn/skills`, the Presets system, `--dry-run`/`--diff`/`--view` flags, `init --template` scaffolding, `--base` primitive-choice flag, `shadcn info`/`docs`, `registry:base` items, font registry items, `--monorepo` support | ui.shadcn.com/changelog |
| `cn` utility package | Released September 2026 with **no breaking changes** for existing projects — old `lib/utils.ts` (clsx + tailwind-merge) keeps working unmodified; migration via `migrate cn` is opt-in | ui.shadcn.com/changelog |
| Component style | `"new-york"` is current; `"default"` is deprecated — like `tailwind.baseColor`/`tailwind.cssVariables`, cannot be changed after `init` without reinstalling components | ui.shadcn.com |

### MUI (Material UI)

| Target | Constraint | Source |
|---|---|---|
| React | Peer support for 17.0.0+, 18.0.0+, 19.0.0+; React ≤18 apps must pin `react-is` to their installed React major via overrides since MUI's own code depends on `react-is@19` | mui.com |
| TypeScript | v6→v7 migration raised the minimum to 4.9 (from 4.7) | mui.com/migration |
| Next.js `optimizePackageImports` | Next.js 13.5+ auto-applies this for MUI, removing the need for manual path-import discipline | mui.com |
| RSC / App Router support | Introduced in v5.14.0 via `'use client'` on all components | mui.com/blog |
| Browser floor | v9 migration raised the minimum to Chrome 117+, Firefox 121+, Safari 17.0+ | mui.com/migration |
| Security-patch lines | Only v9.x (current stable) and v7.x (LTS line) receive patches — v6.x and earlier do not | GitHub SECURITY.md |
| Version numbering | Jumped from v7 directly to **v9** (skipping v8) to align numbering with MUI X, which as of v9 shares major-version numbers with Material UI | mui.com/blog |
| CSS-variables theming | Opt-in/experimental in v5, more central/refined through v6–v9; v9 adds `color-mix()`-based derived colors | mui.com |

---

## Part 8 — API spec tooling

### OpenAPI

| Target | Constraint | Source |
|---|---|---|
| JSON Schema | Full draft 2020-12 semantics apply only from **OAS 3.1.0 onward** (declared via `jsonSchemaDialect`); 3.0.x is JSON-Schema-*like* but diverges (`nullable`, boolean exclusive bounds) | spec.openapis.org |
| Current stable | 3.2.0 (2025-09-19); 3.1.2 patch published same day. The official FAQ page still states 3.1.1 as latest — **flagged as stale content** | GitHub Releases API |
| 3.1 → 3.2 | Explicitly non-breaking: "OpenAPI 3.2 does not introduce breaking changes. All existing 3.1 documents will work without modification." | learn.openapis.org |
| 3.0 → 3.1 | Breaking: removal of `nullable` in favor of JSON Schema type arrays, `exclusiveMinimum`/`exclusiveMaximum` from boolean modifiers to direct numeric values, `example` → `examples`, revised file-upload description patterns | learn.openapis.org |
| Maintained lines | Two parallel: 3.0.x (latest patch 3.0.4, 2024-10-24) and 3.1.x/3.2.x (3.1.2 and 3.2.0 both 2025-09-19; 3.1.1 was 2024-10-24) — no formal LTS/EOL policy found for older lines | openapis.org/faq |
| OAS 4.0 ("Moonwalk") | Early ADR-stage design, no planned release date; the OAI's SIG recommends continuing to use 3.x today, states a future goal (not yet built) of automated 3.x→4.0 upgrade | GitHub (OAI/sig-moonwalk) |

### Swagger

| Target | Constraint | Source |
|---|---|---|
| React / Redux | Swagger UI v4.0.0 requires React 17.x and Redux 4.x — the documented breaking change from v3.52.5 | GitHub releases |
| Node.js (Editor) | ≥ 12.22.0 minimum; ≥ 24.18.0/npm ≥ 11.16.0 recommended for development; GLIBC ≥ 2.29 needed for certain build steps | GitHub (swagger-editor) |
| OpenAPI 3.1.0 support | Added in Swagger UI v5.0.0 (June 2023), with full backward compatibility for older spec versions, plus JSON Schema 2020-12 keyword rendering | GitHub releases |
| Current major-line support | Swagger UI's current line (5.32.0) supports OpenAPI 2.0, all 3.0.x variants, 3.1.x, and 3.2.0 | GitHub (swagger-ui) |
| GHSA-qrmm-w75w-3wpx (SSRF via `?url`) | Affects `swagger-ui`/`swagger-ui-dist`/`swagger-ui-react` `< 4.1.3`; fixed at 4.1.3 by disabling query-string spec overrides by default | GitHub advisories |
| Docker images | Multi-platform images + `PORT_IPV6` env var added in v5.0.0 (June 2023) — not present in earlier images | GitHub releases |
| Swagger Codegen version lines | 3.x (Maven `io.swagger.codegen.v3`) supports OpenAPI 3.0.x; 2.x (Maven `io.swagger`) supports Swagger/OpenAPI 1.0/1.1/1.2/2.0 — **co-maintained parallel lines, not sequential versions** | GitHub (swagger-codegen) |
| Security-patch line | Only 5.x actively supported; 4.x EOL Aug 2023; 3.x EOL Nov 2021; 2.x EOL 2017 — no fixed-cadence LTS calendar, EOL tied to next-major release | GitHub SECURITY policy |

### GraphQL

| Target | Constraint | Source |
|---|---|---|
| Node.js | graphql-js v17 requires Node.js 22, 24, 25, or 26+ | graphql-js.org |
| TypeScript | graphql-js v17's type definitions target TypeScript 4.4+ | graphql-js.org |
| Current spec edition | "September 2025" (2025-09-03) is the current *ratified* edition; a Working Draft prerelease dated 2026-06-04 postdates it. Prior editions: October 2021, June 2018, October 2016, April 2016, October 2015, July 2015 | spec.graphql.org |
| graphql-js v17 | Released 2026-06-15; breaking vs. v16: `execute()` becomes the stable single-result executor, `GraphQLError` constructor requires `message` + `options`, deep/internal imports no longer semver-stable, `NODE_ENV` no longer implicitly drives development mode | graphql.org/blog, graphql-js.org |

---

## Part 9 — Realtime networking

### WebRTC

| Target | Constraint | Source |
|---|---|---|
| Spec status | WebRTC 1.0 reached W3C Recommendation 2025-03-13; the living editor's draft continues separately | w3.org |
| Working group charter | Chartered until 2026-09-30 as of the research date | w3.org |
| Plan B → Unified Plan SDP transition (Chrome) | M65 (experimental flag) → M69/Sept 2018 (GA, default still Plan B) → M72/Jan 2019 (default → Unified Plan) → M93 (Canary throws on `plan-b`) → M96 (throws across all channels including Stable) | webrtc.org |
| Codec support | AV1 at Chrome 113+/Firefox 136+; HEVC/H.265 at Chrome 136+ (values as captured on research date, subject to change) | MDN |
| Firefox for Android | Versions 68–72 lacked H.264 support "due to Google Play store requirements" | MDN |
| Safari VP8 | Added at Safari 12.1+ | MDN |
| `RTCPeerConnection.getStats()` | Baseline "Widely Available" since September 2017; the 3-argument legacy callback form is deprecated | MDN |
| `RTCDataChannel` max message size | 64 KB default absent explicit SDP `max-message-size`; "modern browsers" support at least 256 KB | MDN |

### Socket.IO

| Target | Constraint | Source |
|---|---|---|
| Node.js | ≥ 10 minimum for the server package | socket.io |
| Browser floor | IE9+; IE6/7/8 explicitly unsupported | socket.io |
| Heartbeat direction | As of v4.1.3, server-initiated pings (mitigates browser tab-throttling causing spurious disconnects) | socket.io |
| Express middleware support | `io.engine.use()` added in v4.6.0 | socket.io |
| `connectionStateRecovery`, `cleanupEmptyChildNamespaces`, `addTrailingSlash` | Added in v4.6.0 | socket.io |
| `InterServerEvents`, `serverSideEmit()` | Added in v4.1.0 | socket.io |
| `SocketData` typing, µWebSockets.js binding | Added in v4.4.0 | socket.io |
| WebTransport support | Added in v4.7.0 | socket.io |
| Redis Sharded Pub/Sub topology | Requires Redis 7.0+ | socket.io |
| Admin UI compatibility | Compatible with Socket.IO v4 servers and v3.1.0+ servers | socket.io |
| v3↔v4 client/server compatibility | The 3.x→4.0 breaking changes are **server-side only**; v3 and v4 clients remain protocol-compatible with each other | socket.io |
| `allowEIO3` option (default `false`) | Enables backward compatibility with Socket.IO v2 clients / Engine.IO v3 protocol | socket.io |

### WebSocket API

| Target | Constraint | Source |
|---|---|---|
| Spec | RFC 6455 published December 2011, status Internet Standard (STD 34); wire-negotiated via `Sec-WebSocket-Version: 13` | rfc-editor.org |
| `http`/`https` URL scheme acceptance | Auto-normalization to `ws`/`wss` began in a change dated May 2023 — older engines may not accept `http(s)://` URLs at all | GitHub (whatwg/websockets) |
| Baseline support | "Widely available," dating to July 2015 | MDN |
| `WebSocketStream` | Explicitly experimental/non-standard, one rendering engine only — not broadly available | MDN |
| Node.js | Global `WebSocket` client introduced v21.0.0 (backported to 20.10.0) behind `--experimental-websocket`; flag removed v22.0.0; stable as of v22.4.0. **Client-only** — Node ships no built-in WebSocket server | nodejs.org |
| RFC 7692 (permessage-deflate) / RFC 8441 (WebSockets over HTTP/2) | Published Dec 2015 / Sept 2018 respectively — both layer on top of RFC 6455 rather than superseding it | rfc-editor.org |
| WHATWG Living Standard | No version number by design; split into its own standalone Living Standard (separate from HTML) in 2021, actively maintained (most recent commit 2026-03-15 at research time) | websockets.spec.whatwg.org |

---

## Part 10 — 3D graphics, markup, VCS/CI, tooling, growth

### Three.js

| Target | Constraint | Source |
|---|---|---|
| Versioning scheme | No conventional semver — sequential "r-number" releases (r180, r186, …) map to npm minor versions (0.180.0, 0.186.0). Current stable: r186 / npm 0.186.0 | GitHub releases |
| WebGL floor | "WebGL 1 is not supported since r163" — `WebGLRenderer` requires WebGL 2 from r163 onward | threejs.org |
| Module loading | "As of r147, this is the only way to load three.js properly" — non-module global-namespace `<script>` loading obsolete since r147; legacy UMD/global builds removed at r160→r161 | threejs.org |
| Color-management overhaul | Multi-release rollout starting r152: `outputEncoding` → `outputColorSpace`, `Texture.encoding` → `Texture.colorSpace`, `ColorManagement.enabled` → `true` by default — the single largest visually-breaking change in the migration guide's history | GitHub wiki |
| `Clock` → `Timer` | Deprecated at the 182→183 transition; `Timer` itself moved into core as of 178→179 | GitHub wiki |
| Upgrade policy | No LTS line; official recommendation is to update in increments of 10 releases, since deprecation warnings last for 10 releases | GitHub wiki |
| CommonJS build | r186 release notes show "Deprecate CommonJS build" and "Remove minified builds," though the dev-branch `package.json` still lists a `require` export condition at research time — deprecated but not yet fully removed | GitHub API |

### HTML (spec)

| Target | Constraint | Source |
|---|---|---|
| Versioning model | Living Standard, no discrete version numbers; each commit is a frozen dated snapshot with a permanent URL; roughly every 6 months a snapshot becomes a formal "Review Draft" for patent-policy review | whatwg.org/faq |
| Snapshot as of research date | "Last Updated 7 September 2026" — re-verify against the live spec if precision matters | html.spec.whatwg.org |
| Superseded versioning | W3C's separately-published versioned "HTML5," "HTML 5.1," "HTML 5.2" Recommendations (through 2017) were discontinued per the 2019 WHATWG/W3C agreement in favor of the single Living Standard | whatwg.org/faq |
| DOCTYPE | `<!DOCTYPE html>` is uniform and is explicitly **not** a version indicator, regardless of where in the Living Standard's evolution a document targets | html.spec.whatwg.org |

### ECMAScript (spec)

| Target | Constraint | Source |
|---|---|---|
| Current ratified edition | 17th edition, **ECMAScript 2026**, released June 2026 (permanent snapshot at `tc39.es/ecma262/2026/`) | ecma-international.org |
| Living draft | The canonical no-year URL currently renders as the **ECMAScript 2027** draft — already past the ratified 2026 edition, accumulating Stage-4 proposals toward the 18th edition; not yet ratified as of 2026-09-09 | tc39.es |
| Publication history | 1st edition June 1997; edition 4 reserved but never published; editions 5–16 released annually 2009–2025 | ecma-international.org |
| ES2027-targeted Stage-4 proposals | Explicit Resource Management (`using`/`await using`), `Atomics.pause`, Joint Iteration, Temporal — Stage 4 but not yet in the ratified ES2026 standard | GitHub (tc39/proposals) |
| ECMA-402 (Intl API) | Versioned in step with ECMA-262 (e.g. ES2022 Intl API, 9th edition, complements ECMA-262 13th edition) | ecma-international.org |
| Annex B | Normative for web-browser hosts, normative-*optional* for non-browser hosts — host conformance requirements vary by host type/version, not uniform | tc39.es |

### TypeScript

| Target | Constraint | Source |
|---|---|---|
| TypeScript 7.0 (Go-native compiler rewrite) | Released 2026-07-08; ships with **no programmatic Compiler API at all**, delaying tools that embed the compiler (cited: Vue, Angular, Svelte tooling) until a planned TypeScript 7.1 | devblogs.microsoft.com |
| TypeScript 6.0 (2026-03-23) | Changed long-standing defaults: `strict`→`true`, `module`→`esnext`, `target`→floating `es2025`, `types`→`[]` (no longer auto-including `@types/*`), `noUncheckedSideEffectImports`→`true`, `libReplacement`→`false` — most Node.js projects now need explicit `"types": ["node"]` | devblogs.microsoft.com |
| Compiler API wiki page | Explicitly valid only for TypeScript 6.0 and earlier; 7.1 promised "a completely different API" | GitHub wiki |
| `noUncheckedSideEffectImports` / `rewriteRelativeImportExtensions` | Added in 5.6 / 5.7 respectively | typescriptlang.org |
| `ArrayBuffer` supertype removal (5.9) | `ArrayBuffer` no longer a supertype of typed-array types in `lib.d.ts` — can surface new errors around `Buffer`/`Uint8Array` interop | typescriptlang.org |
| Stage-3 ECMAScript decorators | Available (without `experimentalDecorators`) since 5.0, alongside the older flag-gated legacy decorator implementation | typescriptlang.org |
| `--module node20` | Added in 5.9; models Node 20 behavior and implies `target: es2023`, unlike `nodenext` which keeps evolving | typescriptlang.org |
| Migration sequencing | TS 7.0 deliberately adopts TS 6.0's new defaults/behavior for compatibility rather than introducing another wave of changes — the intended path is 6.0 first, then 7.0 | devblogs.microsoft.com |

### Docker

| Target | Constraint | Source |
|---|---|---|
| Docker Engine API | Current stable v1.56 (Engine 29.8); Engine 29.0.0 raised the minimum supported API to v1.44 (compatible with Engine 25.0+ clients); versions before v1.40 deprecated/unsupported | docs.docker.com |
| Go SDK | As of Engine 29.0.0, `github.com/docker/docker` module deprecated in favor of `github.com/moby/moby/client` and `github.com/moby/moby/api` — breaking change for Go SDK consumers | docs.docker.com |
| Docker Build Checks | Requires Buildx ≥ 0.15.0 and Dockerfile syntax ≥ 1.8, gated independently of the Engine version | docs.docker.com |
| Compose V2 build fields | `cache_to`/`no-cache`/`pull`/`secrets`/`tags` added vs. V1; `ssh` added in V2.4.0+; `platforms` (multi-arch, requires a `docker-container` Buildx driver) added in V2.11.0+ | docker.com/blog |
| Compose versioning | Independent of the Engine version number — latest found was Compose v5.4.0 alongside Engine 29.8 | GitHub releases |
| Enhanced Container Isolation (WSL2 backend) | Hard requires WSL ≥ 2.6 and Linux kernel ≥ 6.3.0 | docs.docker.com |
| cgroup v1 | Deprecated as of Engine 29.0.0, support continuing only until **May 2029** — signals new deployments should target cgroup v2 | docs.docker.com |
| Linux kernel floor | ≥ 3.10, verifiable via the documented `check-config.sh` | docs.docker.com |
| Rootless-mode network driver | Default changed to `gvisor-tap-vsock` as of Engine 29.5.0, alongside a private time namespace enabled by default for rootless containers | docs.docker.com |
| Docker Content Trust | Removed from the CLI as of Engine 29.0.0 — breaking change for `DOCKER_CONTENT_TRUST=1`/`docker trust` workflows | docs.docker.com |

### GitHub

| Target | Constraint | Source |
|---|---|---|
| REST API versioning | Date-versioned via `X-GitHub-Api-Version` header; current version 2026-03-10; requests omitting the header default to 2022-11-28; a superseded version stays supported ≥ 24 months after a new one ships | docs.github.com |
| GitHub Enterprise Importer (GEI) migration sources | GHES ≥ 3.4.1; Bitbucket Server/Data Center ≥ 5.14; Azure DevOps Cloud | docs.github.com |
| GHES release model | Quarterly feature releases; support covers ≥ 4 most recent releases with individually announced discontinuation dates (e.g. GHES 3.9 discontinued 2024-07-09; GHES 3.17 scheduled for 2026-09-22); discontinued versions get no further patches, including for critical security issues | docs.github.com |
| GraphQL API | Schema/changelog spans 2017–2026, evolving continuously rather than through discrete major/date versions like REST | docs.github.com |

### GitHub Actions (CI/CD)

| Target | Constraint | Source |
|---|---|---|
| JavaScript actions runtime | `runs.using` currently accepts `node20` or `node24`; Node 20 reaches upstream EOL April 2026; GitHub forces JS actions to Node 24 by default starting **2026-06-02** (opt-out via `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true`); complete removal of Node 20 from hosted runners scheduled **2026-09-16** | github.blog/changelog |
| Self-hosted runner minimum version | Runners below v2.329.0 lost the ability to run `./config.sh` starting **2026-03-16** (with a Feb 23–Mar 16, 2026 brownout period beforehand) — breaking for unmaintained self-hosted fleets | github.blog/changelog |
| `actions/upload-artifact` / `download-artifact` | v3 fully blocked/deprecated on GitHub.com as of **2025-01-30**; v4 changed artifacts from mutable to immutable and switched storage backends; `download-artifact@v4+` remains **unsupported on GHES**, forcing GHES users to stay on v3 there | github.blog/changelog, GitHub (actions/download-artifact) |
| GHES release model | Independent versioned-release cycle from GitHub.com's continuous deployment; GHES 3.21 GA as of 2026-06-11; general policy supports ≥ 4 most recent GHES feature releases | docs.github.com, github.blog/changelog |

### Husky

| Target | Constraint | Source |
|---|---|---|
| Node.js | Current stable v9.1.7 requires `engines.node >=18` per published `package.json` | GitHub (typicode/husky) |
| Git | Requires Git > 2.9 (the version that introduced `core.hooksPath`, which Husky's entire mechanism depends on) | typicode.github.io |
| Direct package-binary invocation | v9.1.1+ can invoke locally installed package binaries directly by name in hook scripts without an `npx` prefix, saving ~0.2s per invocation | GitHub releases |
| v10.0.0 (announced, unreleased) | Will remove the compatibility shim that currently auto-strips two legacy lines (shebang + sourcing line) from old hook files — those lines "WILL FAIL in v10.0.0" | GitHub (typicode/husky) |
| Node-version-range shift (unreleased) | A CI-workflow commit post-dating v9.1.7 ("remove Node.js 18, add 24") suggests the next release's supported Node range may shift upward from ≥18, but no new npm version had published this as of the research date | GitHub commit history |

### Google SEO

| Target | Constraint | Source |
|---|---|---|
| API versions | Search Console API is documented at v1; Indexing API is documented at v3 | developers.google.com |
| Core Web Vitals metric | INP (Interaction to Next Paint) is the *current* responsiveness metric, superseding the deprecated First Input Delay (FID) — any doc/tool still citing FID as a live ranking metric is out of date | developers.google.com |
| Docs freshness | Search Central pages carry per-page "last updated" timestamps (observed 2025-12-10 UTC during this research pass) rather than software version numbers — a drifting snapshot, not a permanent fact | developers.google.com |
| Ranking-algorithm changes | Roll out via named, dated core/spam/feature updates on a public status dashboard (e.g. Aug 2026 spam update, May 2026 core update) rather than installable version numbers — site owners cannot pin to an older ranking algorithm | status.search.google.com |

### Google AdSense

| Target | Constraint | Source |
|---|---|---|
| Management API | Current major v2 (initial release 2021-04-19), ongoing additive (non-breaking) updates through at least 2026-02-05. The v1.4→v2 jump was the major breaking-change boundary (removed deprecated v1.4 methods, restructured resource identification, discontinued AdMob/YouTube support within the API, limited report history to 3 years) | developers.google.com |
| Prior API versions | v1, v1.1, v1.2, v1.3, v1.4 all deprecated/sunset — v1.2/v1.3 sunset 2016-08-17, v1.4 sunset 2021-10-12 (dates via WebSearch snippets, not independently re-confirmed by direct fetch) | developers.google.com |
| AdSense Platform API | Available in v1 and v1alpha — a **parallel, separate** product/version line from the Management API's v2, not a predecessor/successor relationship | developers.google.com |
| Consumer-facing product versioning | No publicly numbered major version the way a software library has — behavior changes roll out via help-page updates and account notifications, not a versioned changelog | support.google.com |

---

## Part 11 — Cross-cutting synthesis

These are connections drawn by combining two or more independently-sourced facts above that neither source stated together. Labeled explicitly per this project's convention — treat as hypotheses, not documented claims.

- **`[Synthesis]`** *Effective Node.js floor compounds across a stack.* Part 1 shows individual package floors ranging from Node 18 (Husky, Express 5) to Node 22.12+ (Vitest 5, Prisma v7, Angular 22). A project combining several of these tools is bound by the **highest** floor in the set, not any single package's documented minimum — worth encoding explicitly in any skill that scaffolds a multi-tool stack, since checking only the "primary" framework's stated Node version would under-report the real requirement.

- **`[Synthesis]`** *The TypeScript 6.0/7.0 default-change wave lands on the same 2026 timeline as several frontend frameworks' own major bumps.* TypeScript 6.0 (2026-03-23, `strict`→true, `types`→`[]`) and 7.0 (2026-07-08, no Compiler API) both land within months of Angular 22 (TS floor `>=6.0.0 <6.1.0`), Vue's TS-minor carve-out warning, and shadcn/ui's Base UI default switch (July 2026) and `cn` package release (September 2026). None of the individual source docs cross-reference each other, but a skill authored in mid-to-late 2026 assuming "current TypeScript" needs to be explicit about which TS major it targets, since 7.0 shipping with zero Compiler API is a documented blocker for framework tooling (Vue/Angular/Svelte) that embeds it, per TypeScript's own release notes.

- **`[Synthesis]`** *MySQL's calendar-versioning switch (26.7.0) and Prisma's `take()`/`skip()`→`limit()`/`offset()` rename (8.0.0-rc.7) are both examples of an underlying pattern in this dataset: several actively-developed technologies changed a **naming/numbering convention itself**, not just a feature, in 2026.* Three.js's decade-long "no semver, r-number releases, update every 10" convention is a third instance of the same pattern — version-compatibility tooling that assumes semver-shaped version strings will misparse or mis-sequence at least three of the 44 technologies in this dataset (MySQL post-26.7.0, Three.js always, and any tool inspecting Prisma 8's pagination API surface across the rc line).

- **`[Synthesis]`** *Database driver/ORM version matrices are the densest coupling surface in this dataset.* Mongoose's MongoDB compatibility matrix (Part 5) and Drizzle/Prisma/TypeORM's per-database driver constraints (Parts 5 and elsewhere) together suggest that **ORM version choice is effectively a second, independent constraint on database version choice** — e.g. Prisma v7 dropping MongoDB support entirely (staying on v6 for MongoDB users) means "which Prisma major" and "which database" are not independently selectable facts for a MongoDB-backed project, something neither the Prisma nor MongoDB source doc states as a joint constraint.

---

## Part 12 — Notable gaps in the underlying research

Called out explicitly per this project's sourcing rules, rather than filled in with plausible-sounding content.

- **`[Gap]`** Several technologies profiled here are **specifications, not installable packages** (HTML, CSS, ECMAScript, WebRTC, WebSocket API, OpenAPI), and their `versionCompatibility` data is accordingly thin or entirely browser-support-table-shaped rather than package-version-shaped. This is expected given what they are, but it means this Version Matrix is structurally uneven — dense for ORMs/frameworks/databases, sparse for specs — and a reader should not infer that thin coverage here means the spec itself is under-versioned; it means package-style "version compatibility" is largely the wrong question for that row.
- **`[Gap]`** The compiled data is silent on version compatibility **between many of the cross-cutting technologies this project would most want for skill design** — e.g. no direct fact anywhere states which Playwright version pairs with which Vite version, or which Husky version is required for a given Node/npm/pnpm combination beyond Husky's own floor. Adjacency was inferred only where the source docs themselves stated it (e.g. Vitest requiring a specific Vite floor); where two technologies commonly co-occur but no doc states a joint constraint, this document does not manufacture one.
- **`[Gap]`** GitHub Actions' interaction with the *other* CI-relevant technologies in this dataset (Playwright's Docker images, Jest's coverage providers, Husky's pre-commit hooks) is not documented as a joint version constraint anywhere in the underlying research — each technology documents its own CI-adjacent behavior in isolation.
- **`[Gap]`** Several "current stable version" and "latest release" claims in the source data are themselves internally inconsistent or flagged as unresolved by the original researchers (Prisma 8's pagination-method rename conflicting with its own live reference docs; Vue's Vapor Mode stable/unstable status; Next.js's August 2026 security release CVEs not independently verified). These are preserved here as-is, with the original flag, rather than resolved one way or the other.
- **`[Gap]`** The compiled `agentCapabilities` profile (covering the seven AI coding-agent ecosystems) contains its own version-flavored facts — e.g. per-ecosystem Node.js requirements for MCP servers, hook fail-open/fail-closed defaults, sandbox tool minimums — but these were explicitly out of scope for this document, which is limited to the 44 *technology* profiles per the task definition. A companion agent-ecosystem version matrix, if useful, would need to be built as a separate document.

---

*Compiled from `research/technologies/*.md` (44 files) via the structured JSON extraction described in the project's knowledge-map workflow. Snapshot date 2026-09-09. Re-verify before treating any individual fact as current.*
