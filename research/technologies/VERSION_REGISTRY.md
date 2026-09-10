# Version Registry

This file registers every version-sensitive fact captured while researching the 52 technologies in this Skill Library project -- specific release numbers, dates, deprecations, breaking-change milestones, and support-window boundaries that a skill or agent should be aware of before treating guidance as current. Facts are grouped by technology in the order captured during research.

## Angular

- v22 (current stable, released 2026-06-03) -- New components default to ChangeDetectionStrategy.OnPush; TypeScript <6.0 unsupported; @Service() decorator introduced; Signal Forms and @angular/aria stabilized; withFetch and reportProgress deprecated in HttpClient; ChangeDetectorRef.checkNoChanges, createNgModuleRef, ComponentFactoryResolver removed
- v21 (LTS, released 2025-11-19) -- Zoneless change detection became stable and default; Vitest became the default test runner for new CLI projects; Signal Forms introduced experimentally; server bootstrap requires BootstrapContext; TypeScript <5.9 unsupported; UpgradeAdapter removed
- v20 (LTS, released 2025-05-28) -- provideExperimentalZonelessChangeDetection renamed to provideZonelessChangeDetection (Experimental->Developer Preview); afterRender renamed to afterEveryRender; browser support policy switched to 30-month Baseline model; TypeScript <5.8 and Node 18/22.0-22.10 unsupported; InjectFlags removed
- v19 -- Standalone became the default for the `standalone` component option (previously defaulted to false pre-19.0.0)
- v18 (referenced, not independently deep-verified) -- Event Replay for hydration became available, per a WebFetch summary of the hydration guide
- pre-v22 (all majors) -- 6-month major release cycle with 1-3 minors per major and an 18-24 month-ish support window; v22 changed cadence to ~12-month majors with 4-6 minors and a formal 24-month (12 Active + 12 LTS) support window

## Anthropic Claude API (Messages API)

- Current model lineup (four active tiers): Claude Fable 5.1 (`claude-fable-5-1`), Claude Opus 5 (`claude-opus-5`), Claude Sonnet 5 (`claude-sonnet-5`), Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) -- docs default recommendation is Opus 5 for most workloads, Fable 5.1 for demanding reasoning/long-horizon agentic work. Legacy-but-available: Fable 5, Opus 4.8/4.7/4.6/4.5, Sonnet 4.6/4.5.
- `anthropic-version` header contract: `2023-06-01` is current (incremental streaming deltas, named SSE events, removed `data: [DONE]` sentinel and legacy `exception`/`truncated` values); `2023-01-01` was the initial release. Previous versions are deprecated and may be unavailable for new users.
- Model-ID versioning changed at the 4.6 generation: from Claude 4.6 onward, dateless model-ID strings (e.g. `claude-opus-5`) are themselves pinned snapshots, not aliases over a hidden dated ID (pre-4.6 models use the alias-over-dated-ID pattern).
- Retirement commitments (Anthropic-operated platforms; Bedrock/Google Cloud set their own): Fable 5.1 not sooner than 2027-09-01; Opus 5 not sooner than 2027-07-24; Sonnet 5 not sooner than 2027-06-30; Opus 4.8 not sooner than 2027-05-28; Opus 4.7 not sooner than 2027-04-16; Sonnet 4.6 not sooner than 2027-02-17; Opus 4.6 not sooner than 2027-02-05; Haiku 4.5 not sooner than 2026-10-15.
- Sonnet 5's $2/$10-per-MTok launch pricing was introductory through August 31, 2026 but was made permanent -- a previously-announced increase to $3/$15 was retracted rather than taking effect.
- Tokenizer change at Claude 4.7+: ~30% more tokens for the same text versus the pre-4.7 tokenizer -- a breaking change for any hardcoded token-budget math, not a request-shape error.
- Breaking changes on current models: assistant-message prefill removed (Claude 4.6+); manual/extended thinking (`thinking.type.enabled`) removed on Claude 4.7+ (400 error; use `adaptive` + `output_config.effort`); sampling parameters (`temperature`/`top_p`/`top_k`) rejected as non-default on Opus 4.7+; thinking cannot be disabled at all on Fable 5.1/Mythos 5.1/Fable 5/Mythos 5/Mythos Preview.

## ClickHouse

- 26.8 (LTS) -- Released 2026-08-27; current LTS at research time. Source: changelogs/oss/2026.
- 26.3 (believed LTS) -- Released 2026-03-26 per search metadata only, not independently confirmed via a fetched docs page — flagged as inference.
- 26.8 breaking changes -- X-ClickHouse-Format header now overrides FORMAT/path extension; max_insert_threads default changed 1→auto; JSONEachRow unquoted numbers now parsed as Unix timestamps for DateTime; library dictionary source removed; Arrow-library-based reader/writer removed; PostgreSQL/MaterializedPostgreSQL engines now respect remote_url_allow_hosts; arrayIntersect/arraySymmetricDifference duplicate-handling changed.
- 26.2+ -- tokenbf_v1/ngrambf_v1 skip-index types documented as deprecated.
- Calendar versioning scheme -- Year.Month.Patch.Build format, ongoing as of research date; new minor Stable release ~monthly, LTS designation ~twice yearly (historically March/August).

## CSS (Cascading Style Sheets)

- box-sizing -- Baseline widely available since July 2015
- @container (container queries) -- Baseline widely available, established February 2023
- @property -- Baseline newly available since July 2024 -- recent, expect older-browser gaps
- will-change -- Baseline widely available since January 2020
- CSS Snapshot Group Notes -- Published roughly annually by CSSWG (2018, 2023, 2024, 2025, 2026 editions found); closest thing to an official 'current CSS version' statement, aimed at implementers not authors
- CSS Nesting Module Level 1 -- Comparatively new native feature; MDN page shows a November 2025 last-update note and advises checking compat tables before production use

## Docker

- Docker Engine 29.8.0 (released 2026-09-03) -- Current stable Engine release at time of research; part of 29.x series (started 29.0.0 on 2025-11-10)
- Docker Engine 29.0.0 -- Introduced major breaking changes: min Engine API raised to v1.44, github.com/docker/docker Go module deprecated in favor of moby/moby, ARMv6/Raspbian-32-bit dropped, cgroup v1 deprecated (supported until May 2029), Docker Content Trust removed from CLI, containerd image store became default
- Engine API v1.56 -- Current stable Engine HTTP API version, paired with Engine 29.8; minimum supported API version is v1.44 as of Engine 29.0.0
- Docker Compose v5.4.0 (2026-08-03) -- Current Compose release per official GitHub releases; Compose versioning is independent of Engine versioning
- Compose V1 vs V2 -- V1 (Python, docker-compose) reached end-of-life/deprecated June-July 2023, removed from Docker Desktop; V2 (Go, docker compose subcommand) is current. File format mostly compatible except top-level version: field is deprecated in V2
- Buildx >= 0.15.0 / Dockerfile syntax >= 1.8 -- Minimum versions required for docker build --check (Build Checks) feature
- Engine 29.5.0 -- Changed rootless mode's default network driver to gvisor-tap-vsock and enabled private time namespace by default for rootless containers
- Engine 29.7.0 -- Made the 'image' mount type non-experimental; added experimental embedded-containerd feature
- WSL >= 2.6 / kernel >= 6.3.0 -- Hard minimum requirement for Enhanced Container Isolation (ECI) on the WSL2 Docker Desktop backend

## Drizzle ORM

- 0.45.2 -- Current npm 'latest' dist-tag as of 2026-09-09 — the version installed by default `npm install drizzle-orm`; most production code targets this v0.x line.
- 1.0.0-rc.4 -- Newest confirmed tagged GitHub release (June 27, 2026) in the v1.0.0 release-candidate line; v1 is not yet stable/latest on npm as of research date.
- 1.0.0-rc.1 through rc.4, beta.18-22 -- Active beta/rc release train through March-June 2026, several releases per month — fast-moving pre-1.0 development pace.
- v0.x -> v1.x (any) -- Major breaking-change boundary: RQBv1 removed (defineRelations replaces it), global casing option replaced by table-level snakeCase/camelCase builders, .enableRLS() replaced by withRLS(), getTableColumns() renamed getColumns(), array().array() chaining replaced by array('[][]') string notation, migration folder format changed (journal.json removed), push default schema scope changed from public-only to all schemas, push --strict flag removed.
- PostgreSQL 15+ -- Required for the `NULLS NOT DISTINCT` option on unique() constraints, per the indexes-constraints docs.

## ECMAScript

- ECMAScript 2026 (17th edition, ECMA-262) -- Current ratified/published standard as of research date (2026-09-09); released June 2026, per ecma-international.org
- ECMAScript 2027 (living draft, 18th edition in progress) -- The canonical tc39.es/ecma262/ URL (no year) already renders this in-progress draft; not yet ratified. Contains Explicit Resource Management, Atomics.pause, Joint Iteration, Temporal as Stage 4
- ECMAScript 2025 (16th edition) -- Prior ratified edition, June 2025; added Set methods, Float16 typed arrays, JSON modules, import attributes, RegExp modifiers, duplicate named capture groups, ArrayBuffer.transfer
- ECMAScript 2024 (15th edition) -- Added Promise.withResolvers, Array/Map grouping, resizable ArrayBuffers, RegExp v flag, Atomics.waitAsync, well-formed Unicode strings, change-array-by-copy methods
- ShadowRealm proposal — Stage 2.7 -- Not yet part of any ratified ECMA-262 edition as of research date; provides same-thread sandboxing/isolation if it reaches Stage 4

## Express

- 5.2.1 (current latest, published 2025-12-01) -- Current stable/default npm dist-tag; requires Node.js >= 18
- 4.22.2 (current latest-4, published 2026-05-11) -- 4.x line still receives patch releases after 5.x became default latest; requires Node.js >= 0.10
- 5.x route-path syntax -- Named wildcards required (*splat/{*splat}), brace-based optional segments, array-based path alternatives -- differs from 4.x's /*, :file.:ext?, [a|b] syntax
- 5.x express.urlencoded() -- extended option now defaults to false, was true in 4.x
- 5.x req.body/req.query -- req.body is undefined (not {}) when unparsed; req.query is a read-only getter with default parser changed from extended to simple
- 5.x async error handling -- rejected promises/thrown errors from async handlers auto-forward to next(err); manual .catch(next) no longer needed
- app.query() / HTTP QUERY method -- Requires Node.js >= 20.19.3 or >= 22.2.0, tied to Node's own QUERY method support, independent of Express's own minimum
- TypeScript direct execution (node src/app.ts) -- Requires Node.js >= 22.18.0 (or >=23.6.0 on v23 line) with TypeScript >= 5.8 -- a Node.js feature, not an Express feature
- Debug namespace 'router' vs 'express:router' -- 5.x moved router debug logs to a separate 'router'/'router:*' namespace; 4.x used 'express:router'

## Fastify

- v5.12.3 (latest stable, npm dist-tag "latest", published 2026-09-04) -- Current stable release as of research date 2026-09-09; requires Node.js v20+
- v6.0.0-alpha.0 through alpha.3 (npm dist-tag "next", Aug 11 – Sep 4 2026) -- Active pre-release major version; includes security fixes, removes deprecated APIs, raises minimum Node.js version further; not production-ready
- v5.x line -- Requires Node.js v20+ (dropped v18); introduced loggerInstance, routerOptions nesting, handlerTimeout, full-JSON-Schema requirement (jsonShortHand removed), useSemicolonDelimiter default flipped to false, reference-type Request/Reply decorators rejected, mixed async/callback plugins disallowed
- v4.x line -- Documented as retiring 2025-06-30 per official LTS page — already past end-of-support as of this 2026-09-09 research date
- v3.x line -- npm dist-tag "three" -> 3.29.5, last release of that line; TypeScript generic-based typing was introduced in v3 per TypeScript reference page

## GitHub

- REST API 2026-03-10 -- Current dated REST API version at research time; first calendar version to include breaking changes
- REST API 2022-11-28 -- Default version used when X-GitHub-Api-Version header is omitted; baseline of date-based versioning with no breaking changes
- GHES quarterly feature releases -- GHES ships quarterly feature releases plus interim patch releases; support model covers at least the 4 most recent feature releases, each with an individually announced discontinuation date
- 2FA mandate effective March 2023 -- GitHub began requiring 2FA for code-contributing users on GitHub.com in group-by-group 45-day rollout waves starting March 2023

## GitHub Actions (CI/CD)

- actions/runner v2.329.0 -- Minimum enforced self-hosted runner version as of March 16, 2026 (brownout period Feb 23-Mar 16, 2026); enforcement deadlines have been extended before, and the precise latest patch version as of Sept 2026 could not be confidently pinned (marked Unresolved).
- Node.js 20 -> Node.js 24 (JS action runtime) -- Node 20 EOL upstream April 2026; GitHub forces JS actions to Node 24 by default starting June 2, 2026 (opt-out flag available during transition); Node 20 fully removed from GitHub-hosted runners September 16, 2026 -- imminent relative to this research's 2026-09-09 date.
- actions/upload-artifact & download-artifact v3 -> v4 -- v3 fully blocked on GitHub.com as of January 30, 2025. v4 changed artifacts to immutable, changed download directory/merge behavior, and uses a ~10x faster backend. download-artifact v4+ remains unsupported on GHES (must stay on v3 there).
- set-output / save-state workflow commands -- Deprecated Oct 11, 2022 (security fix for log-injection); original May 2023 removal date was postponed given usage volume. Current hard-removal status not re-confirmed live in this pass -- marked Unresolved.
- GitHub Enterprise Server (GHES) 3.14-3.21 -- GHES follows independent versioned releases distinct from GitHub.com's continuous deployment; 3.21 GA'd June 11, 2026. Specific EOL dates for 3.14/3.16/3.17 found via search only, not directly fetched -- flagged Unresolved, verify against live release table.

## Go

- 1.27.0 (released 2026-08-19) -- Current stable major release at time of research; added generic methods, encoding/json/v2, crypto/mldsa, removed several TLS GODEBUG opt-outs, macOS 13+ required
- 1.26.0 (released 2026-02-10) -- Previous major release, still in support window; Green Tea GC became default, self-referential generics allowed, cmd/doc removed
- 1.25.0 (released 2025-08-12) -- Fell out of the two-release security-support window once 1.27 shipped
- 1.21+ -- go.mod 'go' directive became mandatory/enforced; module graph pruning behavior tied to go 1.17+ lines
- 1.20 -- Profile-Guided Optimization (PGO) introduced, opt-in only
- 1.21 -- PGO became auto-detected/on-by-default when default.pgo is present
- 1.18 -- Generics (type parameters) and native fuzzing introduced
- 1.19 -- GOMEMLIMIT introduced
- 1.24 -- FIPS 140-3 Go Cryptographic Module (v1.0.0) introduced and CMVP certified
- 1.17 -- Module graph pruning and lazy module loading introduced
- 1.16 -- Module-aware mode became the default over GOPATH mode

## Google AdSense

- AdSense Management API v2 (current, released 2021-04-19) -- Breaking change vs v1.4: removed deprecated methods, restructured resource `name` identification, removed `kind` field, renamed many resource fields, dropped AdMob/YouTube support, capped report history to 3 years. Receiving ongoing additive updates through at least 2026-02-05.
- AdSense Management API v1 -> v1.1 -> v1.2 -> v1.3 -> v1.4 -- All deprecated/sunset: v1.2/v1.3 sunset 2016-08-17 (source: search-derived from Google Ads Developer Blog title, not independently re-fetched); v1.4 sunset 2021-10-12 (source: search-derived from Google Groups adsense-api announcement title, not independently re-fetched).
- AdSense Platform API v1 / v1alpha -- Separate, parallel product/API from the Management API -- for AdSense-for-Platforms hosting partners, not a predecessor/successor version relationship to Management API v2.
- AdSense product/UI (Auto ads, ad code, account features) -- No publicly documented version number or changelog -- Not documented / could not verify a versioned release process for the consumer-facing product; changes ship via individual help-page updates (e.g. 'Auto ads now works through any AdSense ad unit code').
- Site verification / site management improvements -- Version-dated feature: real-time site-ownership verification and meta-tag verification method both introduced 2023-09-15 per support.google.com/adsense/answer/13996652.

## Google SEO (Google Search Central / Google Search)

- Docs snapshot: last-updated 2025-12-10 UTC (multiple pages) -- Google Search Central docs are continuously updated, not semantically versioned; this is the footer date observed on several fetched pages as of research date 2026-09-09.
- Search Console API v1 -- Search Analytics, Sitemaps, Sites, URL Inspection services.
- Indexing API v3 -- Restricted to JobPosting and BroadcastEvent(VideoObject) content types only.
- Core Web Vitals: INP + LCP + CLS (current trio) -- INP (Interaction to Next Paint, <200ms) is the current responsiveness metric; industry-reported to have replaced First Input Delay (FID) in March 2024. Current official CWV page shows no FID reference, consistent with retirement, though no explicit migration notice was found on the page itself.
- Named ranking updates through 2026-08-18 -- Per official status.search.google.com history: August 2026 spam update, June 2026 spam update, May 2026 core update, March 2026 core update, March 2026 spam update, February 2026 Discover update. This list will be superseded by future entries on the same live page.

## Grafana

- Grafana 13 (current major, 13.2 most recent minor) -- Minor releases ship every other month; majors ship yearly (April/May); patches at least monthly. Each minor supported 9 months; the final minor of a major line gets 15 months. No "LTS" branding found despite the similar-shaped policy.
- Grafana 13.0.0 -- Image Renderer plugin support fully removed; `grafana-cli`/`grafana-server` hyphenated commands replaced by `grafana cli`/`grafana server` subcommands; deprecated numeric `id`-based data source APIs disabled by default (uid-based required); `enable_gzip` HTTP compression flipped to enabled by default; Alertmanager status endpoint now requires `alert.notifications.system-status:read`.
- Grafana 11.0.0 -- Legacy dashboard alerting removed entirely (v10.4 was the last version supporting it) -- the single largest recent breaking change, altering the alerting data model, folder permissions, and notification-channel compatibility for every dashboard on the legacy system.
- Grafana 13.2.0 (scheduled) -- `@grafana/runtime`'s `config.apps`/`config.panels` properties scheduled for removal.
- Feature maturity lifecycle (version-independent) -- Experimental / Private preview / Public preview / General Availability, orthogonal to the version-support-window policy above; a GA-version release can still contain an Experimental-maturity feature.

## GraphQL

- GraphQL Specification — September 2025 edition -- Current ratified spec edition, released 2025-09-03; a newer Working Draft (prerelease) dated 2026-06-04 exists beyond it. Prior editions: October 2021, June 2018, October 2016, April 2016, October 2015, July 2015.
- graphql-js v17 -- Official JS/TS reference implementation, released 2026-06-15. Requires Node.js 22/24/25/26+ and TypeScript 4.4+. Numerous breaking API changes vs v16 (see Breaking changes section) — execute() semantics, GraphQLError constructor, removed helpers, non-stable deep imports, etc.
- Spec September 2025 vs October 2021 -- Non-nullable-ing of includeDeprecated and @deprecated's reason argument, subscription root @skip/@include restriction, and OneOf Input Objects / schema coordinates / extended deprecation support are all new since October 2021 — code or tooling built against the October 2021 edition's assumptions may need updating.

## HTML

- Living Standard (no version numbers) -- HTML is published as a continuously-updated WHATWG Living Standard rather than discrete numbered releases; dated frozen snapshots and periodic (~6-month) Review Drafts substitute for version numbers. [Source: https://whatwg.org/faq]
- Snapshot dated 7 September 2026 -- The one-page spec at html.spec.whatwg.org carried a 'Last Updated 7 September 2026' stamp at research time (2026-09-09) — confirms the spec is under active, near-daily revision; any specific claim tied to a snapshot date should be re-verified against the live spec if precision matters. [Source: https://html.spec.whatwg.org/]
- Pre-2019 W3C 'HTML5'/'HTML 5.1'/'HTML 5.2' Recommendations (historical, superseded) -- The W3C previously published separate versioned Recommendations through 2017; the 2019 WHATWG/W3C agreement discontinued this model in favor of the single Living Standard. Content still describing 'HTML5' as a fixed target reflects this now-superseded era. [Source: https://whatwg.org/faq]

## Husky

- v9.1.7 (current stable, released 2024-11-18) -- No newer npm release found as of research date 2026-09-09, ~22 months later; treat as the current production version
- v10.0.0 (announced, unreleased) -- Docs/source explicitly warn that the deprecated shebang line and '. "$(dirname -- "$0")/_/husky.sh"' sourcing line 'WILL FAIL in v10.0.0'; no v10 tag exists yet
- v9.1.1 (2024-07-18) -- Introduced direct invocation of locally installed package binaries in hook scripts without an npx prefix (~0.2s faster per call); not present in earlier v9.0.x
- v9.1.5 (2024-08-20) -- Added support for the pre-merge-commit hook
- v6 (Jan 2021) vs pre-v6 (v0-v4) -- Major architecture shift: pre-v6 generated hooks from a JS config file (.huskyrc.js/package.json 'hooks' key) with all-hooks-installed-and-checked-at-runtime; v6+ uses core.hooksPath with one file per hook in .husky/, and only hooks with a non-empty file execute
- engines.node >=18 (current package.json) -- A 2025-10-10 CI commit removed Node 18 and added Node 24 to the test matrix, suggesting a future release may raise the minimum, but the published package.json still states >=18 as of research date
- husky install / husky add / husky set / husky uninstall -- add/set/uninstall are deprecated AND hard-fail (exit code 1) in the current v9.1.7 CLI; 'install' is deprecated but still functions (prints a warning, proceeds)

## Jest

- 30.5.1 -- Current npm 'latest' as of 2026-09-01 (research date 2026-09-09); engines.node = ^18.14.0 || ^20.0.0 || ^22.0.0 || >=24.0.0
- 30.0.0 -- Major breaking release (2025-06-04): dropped Node 14/16/19/21, min TypeScript 5.4, jsdom 21→26, removed expect matcher aliases, --testPathPattern→--testPathPatterns, removed jest --init, unrs-resolver adoption
- 27.0.0 -- Prior major-defaults shift (2021): testEnvironment default jsdom→node, fake timers legacy→modern, default test runner jest-jasmine2→jest-circus

## MongoDB

- 8.3 -- Current stable major/minor release per official lifecycle page; GA May 2026, EOL Oct 31 2029. Patch-level docs snapshots cited elsewhere (8.0.30, 7.0.41) are dated Sept 2026.
- 8.2 -- First minor release downloadable for self-managed Community/Enterprise (previously Rapid Releases were Atlas-only); reached EOL July 31 2026; sequential-upgrade-only, no Atlas Live Migration/mongosync support.
- 8.0 -- Major release, GA Oct 2024, EOL extended to Oct 31 2029 (5-year window). Introduces breaking null/undefined query semantics change, majority write-concern timing change, direct-to-shard command restrictions, TCMalloc per-CPU-cache upgrade. Also: Transparent Hugepages should be enabled (flipped from prior guidance).
- 8.3 -- Further tightens sharded-cluster rule so DDL and applyOps run only via mongos.
- 7.0 -- Major release, GA Aug 2023, EOL extended to Aug 31 2027 (4-year window). Docs page for this version is patch-changelog-oriented rather than a curated breaking-changes summary; MongoDB 7.0 and earlier should have Transparent Hugepages disabled.
- 7.0 (storage engine) -- WiredTiger introduces dynamic read/write ticket concurrency algorithm (max 128/128), replacing static ticket config.
- 6.0 -- Prior major release, GA July 2022, EOL July 31 2025 (already past EOL as of research date).
- 5.0 -- Introduced Stable API and quarterly Rapid Release cadence (Atlas-only until 8.2); IP-only replica set member configs began failing startup validation (DNS hostnames required); AVX CPU instruction set became required; snapshot history retention became configurable.
- 5.1 -- Cluster Wide Write Concern (CWWC) became mandatory when adding shards.
- 4.2 -- Multi-document ACID transactions extended to sharded clusters (transactions on replica sets since 4.0).
- 9.0 -- GA status unconfirmed — see Unresolved items; PPA/packaging activity referenced in a mongosh-adjacent release note as of Aug 2026 but no official 9.0 release-notes page was located.

## Mongoose (MongoDB Object Modeling for Node.js)

- 9.9.5 -- Current stable version at research time (2026-09-09), released 2026-09-04
- 9.x (Node.js requirement) -- Mongoose 9 requires Node.js >= 20.19.0
- 9.x (middleware) -- Pre-middleware hooks no longer receive a next() callback param; async/Promise-only, breaking change from 8.x
- 9.x (TypeScript) -- FilterQuery renamed to QueryFilter with stricter type enforcement
- 9.x (UUID) -- UUID schema fields now return bson.UUID objects instead of strings
- 9.9.5 (deprecation) -- Document.prototype.validateSync() deprecated, slated for removal in not-yet-released Mongoose 10
- <6.13.9, 7.0.0-7.8.8, 8.0.0-8.22.0, 9.0.0-9.1.5 -- Vulnerable to CVE-2026-42334 (sanitizeFilter $nor bypass); patched in ^6.13.9, ^7.8.9, ^8.22.1, ^9.1.6
- 5.11.0 -- First version with officially supported TypeScript bindings
- 8.x -- Released 2023-10-31; docs state support 'through February 1, 2026' but patch releases (8.24.x) observed continuing past that date per CHANGELOG - Unresolved tension
- 6.x -- Limited maintenance (security + requested bug fixes only); EOL 2027-02-01
- 5.x -- End of life since 2024-03-01
- 9.8.0 / 9.6.0 -- Bundled MongoDB Node.js driver bumped to 7.5 (9.8.0) and 7.2 (9.6.0) respectively

## MUI (Material UI)

- 9.4.0 (npm latest, published 2026-08-27) -- Current stable @mui/material release as of research date 2026-09-09.
- 9.0.0 (2026-04-08) -- Major version jump directly from v7 to v9, skipping v8, to align major-version numbering with MUI X. Introduced NumberField, Menubar, slots/slotProps consolidation, removed GridLegacy, raised min browser support to Chrome 117+/Firefox 121+/Safari 17+.
- 7.0.0 (March 2025 per versions page; blog cites 2025-03-26) -- Documented long-term-support (LTS) line, still receiving security/regression patches alongside v9.x. Introduced package export restructuring, Grid->GridLegacy rename with Grid2 promoted to Grid, TypeScript min raised to 4.9.
- 5.14.0 -- First version where all Material UI components shipped the "use client" directive, adding Next.js App Router / React Server Components compatibility.
- 5.x -> 9.x -- CSS-variables theming (cssVariables: true) introduced in v5 as opt-in, refined in v9 to generate color-mix()-based derived palette values.
- React 17/18/19 -- All three React majors are supported as peer deps; React <=18 apps must pin react-is to their installed React version via package-manager overrides because Material UI depends on react-is@19 internally.

## MySQL

- 9.7 (LTS) -- Current LTS line per old sequential numbering; manual explicitly documents itself as covering '9.7, through release 9.7.2'. This is also the last release using MAJOR.MINOR.PATCH sequential numbering.
- 8.4 (LTS) -- Prior LTS line; contains major breaking changes vs 8.0 (replica terminology, mysql_native_password default-off, utility removals, AUTO_INCREMENT on FLOAT/DOUBLE removed, etc.). Latest known patch as of July 2026 GA wave: 8.4.11.
- 26.7.0 (Innovation) -- First release under the new calendar-based YY.M.P versioning scheme (announced ~June 2026), released after 9.7 LTS. Represents a fundamental change to how MySQL version numbers should be interpreted going forward.
- 8.0 -- Moved to Oracle Lifetime Sustaining Support (effectively EOL for mainstream purposes) April 21, 2026, per official EOL notice. Users directed to upgrade to 8.4 LTS or 9.7 LTS.
- 5.7 -- Moved to Oracle Lifetime Sustaining Support October 25, 2023. Cannot upgrade directly to 8.4+; must pass through 8.0 first (LTS series cannot be skipped).
- Innovation vs LTS track (introduced with 8.0.x era, formalized by 8.4) -- LTS = 5yr premier + 3yr extended support (8 years total), bugfixes/security only after first release in the series. Innovation = new features/deprecations/removals, supported only until next Innovation release ships (~quarterly historically).

## Next.js

- 16.3.4 -- Current stable version at research time (2026-09-09); 16.3 line released Aug 3, 2026
- 16.x -- Active LTS as of Oct 21, 2025 release; Turbopack default, async-API sync access removed, middleware renamed to proxy (loses Edge runtime), next/image security-hardened defaults, AMP/next-lint/runtime-config removed, Node.js 20.9+ and TypeScript 5.1.0+ now required
- 15.x -- Maintenance LTS as of research time (released Oct 21, 2024); 2-year maintenance window per official support policy; still receives critical bug fixes and security patches only
- 13-14.x -- All versions affected by May 2026 security advisories with no direct patch; must upgrade to 15.5.18+ or 16.2.6+
- 15.1 -- Introduced experimental unstable_getResponseFromNextConfig() config-testing utility
- 15.5 -- Introduced next typegen CLI command generating PageProps/LayoutProps/RouteContext type helpers
- 16.1.0 -- Minimum version supporting the new `next upgrade` CLI command; earlier versions must use the codemod package instead
- 16.3 -- Added Instant Navigations suite (Partial Prefetching, Instant Insights, Navigation Inspector, ISR upgrade-in-background), next/root-params, catchError custom error boundaries, import.meta.glob, Turbopack FileSystem Cache and memory eviction enabled by default, optional TypeScript 7 type-checking
- 14.0.0 -- next export command fully removed (replaced by output:'export' config); experimental SRI-based CSP support added
- 13.4.0 -- App Router static-export support (RSC + Route Handlers) added
- 13.3.0 -- next export deprecated in favor of output:'export'

## Node.js

- v26.8.2 (Current) -- Current release as of research date (2026-09-10), per nodejs.org/en/download
- v24.21.0 (Active LTS) -- Current LTS release as of research date, per nodejs.org/en/download
- v22.x "Jod" -- Initial release 2024-04-24, Active LTS started 2024-10-29, Maintenance started 2025-10-21, EOL 2027-04-30; now in Maintenance LTS
- v24.x "Krypton" -- Initial release 2025-05-06, Active LTS started 2025-10-28, Maintenance starts 2026-10-20, EOL 2028-04-30; currently Active LTS
- v26.x -- Initial release 2026-05-05, Active LTS starts 2026-10-28, Maintenance starts 2027-10-20, EOL 2029-04-30; currently Current, last release under the pre-v27 six-month/odd-even cadence
- v25.x, v23.x, v21.x (odd-numbered) -- Never received LTS status; each became unsupported roughly 6 months after release per the legacy cadence, and all are EOL as of research date
- Node.js 27+ cadence change (announced 2026-03-10, takes effect Oct 2026) -- Twice-yearly cadence and odd/even LTS split retired in favor of one major release per year: a 6-month Alpha channel (Oct-Mar, semver-major changes allowed), 6-month Current (Apr-Oct), then 30 months of LTS (36 months total support). Node.js 27 begins Alpha Oct 2026, expected Current April 2027, LTS Oct 2027, EOL ~April 2030.
- v26.0.0 (2026-05-05) breaking changes -- Fully removed: crypto.createCipher()/createDecipher(), http.Server.prototype.writeHeader(), legacy _stream_* internal modules, --experimental-transform-types flag; Temporal API enabled by default; V8 bumped to 14.6.202.33, Undici to 8.0.2, NODE_MODULE_VERSION to 147; GCC 13.2+/Python 3.10+ now required to build
- v24.0.0 (2025-05-06) breaking changes -- MSVC removed (ClangCL now required on Windows); macOS 13.5+/Xcode 16.1+ required; --experimental-permission renamed to --permission; SlowBuffer, tls.createSecurePair, fs.Dirent.path removed; node:test test()/t.test() no longer return promises (auto-await added); V8 bumped to 13.6, npm bundled version bumped to npm 11
- v22.0.0 (2024-04-24) breaking changes -- require()-ing synchronous ESM graphs supported; WebSocket client enabled by default as a global; default stream highWaterMark increased; Import Assertions (assert syntax) dropped in favor of Import Attributes (with syntax); V8 bumped to 12.4.254.14 enabling Maglev JIT; --watch marked stable; node --run <script> added
- Permission Model (node:permissions) -- Introduced v20.0.0 (--experimental-permission), flag renamed to --permission in v24.0.0, Stable as of v23.5.0/v22.13.0
- node:test built-in test runner -- Available since v18.0.0, became Stable in v20.0.0
- Native TypeScript type stripping -- Added v22.6.0; --experimental-transform-types added v22.7.0; enabled by default v23.6.0/v22.18.0; became Stable v25.2.0/v24.12.0; --experimental-transform-types flag removed entirely in v26.0.0 (--no-strip-types added same release)
- import.meta.filename/import.meta.dirname -- Added v21.2.0, became stable v24.0.0; import.meta.main added v24.2.0
- --env-file flag -- Added v20.6.0, became stable v24.10.0/v22.21.0; --env-file-if-exists added v22.9.0
- Corepack (npm/Yarn/pnpm bridge) -- Bundled with Node.js from v14.19.0 up to (but not including) v25.0.0; must be installed separately (npm install -g corepack) on Node.js 25.0.0+
- libuv thread pool -- Default size 4, configurable via UV_THREADPOOL_SIZE up to a maximum of 1024 (raised from 128 in libuv 1.30.0); pool threads gained an 8 MB stack in libuv 1.45.0 (bundled from Node.js 20), which also changed timer-vs-poll-phase ordering
- CVE-2026-58043 (HIGH, July 29 2026 security release) -- Permission Model path-matching bug allowing over-grant of filesystem access across radix-tree prefix boundaries under --permission, patched in v26.5.1/v24.18.1/v22.23.2 alongside 10 other CVEs (CVE-2026-56846/56847/56848/56850/58039/58040/58041/58042/58044/58045)

## Nuxt

- 4.5.2 (2026-08-05) -- Latest stable Nuxt release as of research date, per official GitHub releases page
- 4.0 (2025-07-16) -- Nuxt 4 major release: introduced app/ directory restructure, new data-fetching layer, TS project references
- 4.2+ -- Minimum version required to opt into future.compatibilityVersion: 5 preview of Nuxt 5 behaviors
- 3.16+ -- hydrate-on-visible lazy hydration attribute became available
- 4.4.0+ -- Threshold above which the cross-user payload disclosure vuln (GHSA-wm8w-6qjm-cv43) applied to cache/swr/isr route rules on authenticated pages
- 4.5.0 (2026-07-18) -- Added Vite 8, Rspack 2/Rsbuild, experimental SSR streaming, stable error-code system, useLayout composable, named views
- 4.5.1 / 3.21.10 (2026-07-27) -- Security patch release fixing 8 advisories including a critical DevTools RCE and high-severity server-island RCE
- 3.x EOL 2026-07-31 -- Nuxt 3 reached end-of-life; no more bug/security fixes
- Node.js 22.x+ -- Minimum Node version for current stable Nuxt 4.x line; Node 22.19+ specifically required post-jiti-removal in the 3→4 upgrade
- 5.x ~Q4 2026 (forward-looking, unreleased) -- Planned next major, includes Nitro v3; not yet stable at research time so breaking-changes list is preview-only

## OpenAI API

- Documentation host migration: `platform.openai.com/docs/*` 301-redirects to `developers.openai.com/api/docs/*` (confirmed via direct fetch); the API reference itself lives under `developers.openai.com/api/reference/`.
- Current flagship model lineup, per the models page at research time: `gpt-6-astra` ("GPT-6 Astra," 1.05M-token context, 128K max output, $10/$50 per MTok, knowledge cutoff April 30, 2026) and the GPT-5.6 family -- `gpt-5.6-sol` ($4/$20/MTok), `gpt-5.6-terra` ($2/$12/MTok), `gpt-5.6-luna` ($0.20/$1.20/MTok) -- all sharing a 1.05M-token context window and February 16, 2026 knowledge cutoff.
- **Assistants API retired August 26, 2026**, migration target is the Responses API plus the Conversations API for persistent state -- fully superseded, not merely deprecated toward an unspecified successor.
- **Evals platform being deprecated**: read-only by October 31, 2026, full shutdown November 30, 2026; documented replacement is an unreleased "Datasets" feature. Agent Builder shuts down the same date (November 30, 2026).
- Model-snapshot deprecations with concrete dates: GPT-5/o3 snapshots (`gpt-5-2025-08-07`, `o3-2025-04-16`) deprecated June 11, 2026, retiring December 11, 2026 (successor `gpt-5.6-sol`); legacy GPT models (`gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`, older o1/o3 variants) deprecated April 22, 2026, retiring October 23, 2026; legacy transcription models deprecated August 26, 2026, retiring February 26, 2027; legacy audio/realtime model families deprecated July 20, 2026, retiring January 20, 2027.
- Deprecation-notice policy is tiered: generally-available models get at least 6 months' notice; specialized variants (chat/Codex/deep-research) get at least 3 months; `preview`-named models may get as little as 2 weeks.
- **Strict-mode default flip**: Responses API attempts strict schema mode by default; Chat Completions defaults to non-strict -- a request that succeeded pre-migration with slightly malformed tool arguments can start failing purely from this default change.
- Pricing/naming changes outside the deprecation cadence: July 30, 2026 update cut GPT-5.6 Luna cost 80% and Terra cost 20%, and renamed "Priority processing" to "Fast mode."
- Prompt objects (`v1/prompts`) being wound down: de-emphasized beginning June 3, 2026, scheduled shutdown November 30, 2026 -- documented replacement is storing prompts in application source control.

## OpenAPI

- 3.2.0 -- Current stable, published 2025-09-19. Non-breaking upgrade from 3.1.x per official guide. Adds structured/nested tags, query HTTP method, additionalOperations, streaming media types (SSE/JSONL/json-seq/multipart), OAuth2 Device Flow, oauth2MetadataUrl, $self field, discriminator defaultMapping.
- 3.1.2 -- Patch release, also published 2025-09-19 alongside 3.2.0; editorial/clarification only per release naming convention (not independently line-verified — CHANGELOG fetch 404'd).
- 3.1.1 -- Published 2024-10-24. Still listed as 'latest' on the official FAQ page as of this research pass, which is stale relative to 3.2.0.
- 3.0.4 -- Patch release for the 3.0.x line, published 2024-10-24 (same day as 3.1.1); 3.0.x remains a separately maintained line alongside 3.1.x/3.2.x.
- 3.1.0 -- Published 2021-02-16. Breaking change from 3.0.x: removed boolean `nullable`, changed exclusiveMinimum/Maximum from boolean to numeric, example→examples, revised file-upload description patterns, added full JSON Schema 2020-12 alignment via jsonSchemaDialect.
- 3.0.0 -- Published 2017-07-26, the first OAI-governed release after separating from Swagger 2.0 (SmartBear donation, OAI formed Nov 2015).
- 4.0 (Moonwalk, unreleased) -- In early Architectural-Design-Record stage, no formal spec text yet, no release date. OAI explicitly recommends using 3.x today. Will include a planned (not yet built) automated 3.x→4.0 upgrade tool.

## OpenSearch

- 3.8.0 -- Current stable release as of 2026-09-09 research date, released 04 Aug 2026 per official version-history table
- 3.0.0 -- Major breaking-change release (06 May 2025): minimum JDK raised to 21, Lucene upgraded to 10, Java Security Manager permanently disabled, transport layer moved to Apache HttpClient 5.x, transport-nio plugin removed, 512-byte doc-ID limit enforced consistently in bulk API
- 2.19.x -- Latest 2.x maintenance line; 2.19.6 released 02 Jul 2026; 2.x stays in maintenance until 4.0 reaches GA
- 1.x -- End-of-life; maintenance ended 6 May 2025 per official releases/support policy page

## OpenTelemetry

- No single unified "OpenTelemetry version" -- API, SDK, Semantic Conventions, and contrib components each version independently under SemVer 2.0.0; stability is tracked per-signal, not per-SDK, so a language's traces can be Stable while its logs are still Development in the same package release.
- Per-language, per-signal stability matrix (as of research date) -- Traces: Stable in C++/.NET/Go/Java/JS/PHP/Python/Ruby/Swift, Beta in Rust, Development in Kotlin. Metrics: Stable in C++/.NET/Go/Java/JS/PHP, Development in Erlang-Elixir/Ruby/Swift, Beta in Rust. Logs: Stable in C++/.NET/PHP only, Release Candidate in Go, Development in Java/JS/Python/Ruby/Swift/Kotlin, Beta in Rust.
- Stability guarantees once a component is Stable -- API: minimum 3 years of support after the next major ships. SDK/contrib: minimum 1 year each. Minor upgrades within a stable major line are guaranteed non-breaking.
- OpenTelemetry JS SDK v2.0.0 -- Minimum Node.js raised to `^18.19.0 || >=20.6.0` (drops 14/16/early 18-20); minimum TypeScript raised to 5.0.4; `parentSpanId` replaced by `parentSpanContext`; `instrumentationLibrary` renamed `instrumentationScope`; `Resource` class made private in favor of factory functions.
- OpenCensus repository archival (2023-07-31) -- Hard breaking change for any project still directly depending on OpenCensus client libraries; the documented OpenCensus bridge is the only forward-compatible migration path.
- Approximate current releases (exact dates unconfirmed, re-verify before relying on them) -- Collector core/contrib ~v1.66.0/v0.160.0; JS SDK ~v2.11.0; Python ~v1.44.0/v0.65b0; Go ~v1.46.0 stable with v1.47.0-rc.1 (Logs API/SDK) in testing.

## OWASP Top 10 for LLM Applications

- **Current edition is the OWASP GenAI LLM Top 10 2026 (v1.0), published August 2026**, superseding the OWASP Top 10 for LLM Applications 2025 (v2.0, published November 17, 2024), which itself superseded the original 2023 v1.0/v1.1 list. Any skill built from this research should be re-checked when a 2027 edition ships.
- 8 of the 10 risk entries changed rank or name between the 2025 and 2026 editions; only Prompt Injection (1st) and Sensitive Information Disclosure (2nd) held their exact position. Largest moves: **Excessive Agency jumped from 6th (2025) to 3rd (2026)**; **Improper Output Handling dropped from 5th (2025) to 10th (2026)**.
- **"System Prompt Leakage" (LLM07:2025) was renamed and rescoped to "Hidden Context Exposure" (LLM08:2026)** -- broadened from just the system prompt to any hidden, non-user-facing context (RAG-injected policy, tool schemas) reaching the model, with regulated-data leakage and agentic amplification concerns explicitly carved back out to LLM02/LLM03.
- 2026 methodology change: the list now blends incident-data validation (7,714 real incidents reviewed, 6,639 classifiable) with community/practitioner judgment, weighted 25% data / 75% judgment -- a deliberate, documented choice to keep incident data advisory rather than authoritative.
- Original 2023 v1.0/v1.1 PDF URLs (`owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/...`) return HTTP 404 at research time; canonical hosting has moved to `genai.owasp.org` and the `GenAI-Security-Project/GenAI-LLM-Top10` GitHub repository (the original `OWASP/` org repository is now a legacy archive pointer only).

## Playwright

- 1.63 -- Current stable as of 2026-09-09. Added test locks, cross-frame locators, locator.visible(), aria/screen snapshots in traces. Removed support for Ubuntu 20.04. Deprecated experimental component-testing packages (@playwright/experimental-ct-react/-vue) in favor of new stable stories/galleries model with fixtures.mount().
- 1.62 -- Introduced new stable component testing model, AbortSignal support for cancelling operations, WebP screenshot format, Reporter.preprocess() custom filtering, isolated retry strategy. Debian 11 end-of-support announced.
- 1.61 -- Added WebAuthn passkey support, Web Storage API (localStorage/sessionStorage) fixtures, new video modes (on-all-retries, retain-on-failure-and-retries).
- 1.60 -- Removed long-deprecated APIs: Locator.ariaRef(), handle option on exposeBinding(), logger option on connect()/connectOverCDP(), legacy context.videoPath()/video-size options. Added HAR recording as first-class tracing API and Drop API for drag-and-drop.
- ~1.52 (unconfirmed) -- Per summarized release-notes fetch: macOS 13 WebKit support deprecated; route.continue() lost ability to override Cookie header. Exact version tag not independently re-verified against a dated entry -- flagged unresolved.

## PostgreSQL

- 18 (current stable, e.g. 18.6) -- Baseline for 'current' docs as of research date 2026-09-09; introduced AIO subsystem, B-tree skip scan, uuidv7(), OAuth auth, checksums-on-by-default, and numerous breaking changes (see doc section 13)
- 19 Beta 3 -- Released 2026-08-13, still pre-GA as of research date; exact GA date and final breaking-changes list not yet published
- 17.11, 16.15, 15.19, 14.24 -- Current minor releases of still-supported prior major versions as of Aug 2026; PG14 EOL is documented as 2026-11-12, roughly 2 months after this research date
- Protocol 3.2 -- Wire protocol version introduced in PG18 (256-bit cancel keys); protocol 3.0 from PG 7.4+ still supported for backward compatibility
- md5 auth deprecated as of v18 -- CREATE ROLE/ALTER ROLE now warn on md5 passwords; no removal version number given in docs yet

## Prisma

- 7.10.0 (latest stable, 2026-08-25) -- Current production-recommended Prisma ORM release per official blog guidance; Rust-free/driver-adapter architecture is default; requires prisma.config.ts, explicit driver adapters, ESM; MongoDB NOT supported
- v8.0.0-rc.1 through rc.8 (Aug 2026, all flagged prerelease) -- Active release-candidate cycle for the ground-up TypeScript rewrite (contract-based schema, chained query DSL, graph-based migrations); no stable 8.0.0 exists yet as of research date; official blog explicitly says v7 remains the production choice
- v7.0.0 (2025-11-19) -- Made the Rust-free TypeScript/WASM query engine + driver adapters the DEFAULT architecture (was opt-in Preview under v6.16.0+)
- v6.x line -- Last version line supporting MongoDB; also last version with the classic prisma-client-js generator, implicit env var loading, and pre-driver-adapter datasource config; TS >=4.7 / Node 16.13-20.x minimums
- v6.7.0 -- Introduced multi-file schema support (prisma/schema/ directory)
- v6.13.0 -- prisma.config.ts reached GA
- v6.16.0 -- Rust-free ORM and driver adapters reached GA as an available (non-default) option
- v3.x.x onward -- SemVer policy in effect: MAJOR breaks only GA features, MINOR can break opt-in Preview/EA features only

## Prometheus

- 3.14.0 -- Current stable release as of 2026-08-17, confirmed via the project's own maintained changelog and the doc-tree sitemap (which independently lists version-pinned trees for 3.14/3.13/3.5).
- SemVer since 1.0.0 -- Breaking changes indicated by major-version increments; Prometheus is now on its 3.x line (3.0.0 released 2024-11-14).
- LTS policy -- New minor release cycle every 6 weeks; regular minors stop receiving bugfixes after that window. Designated LTS releases get bug/security/doc fixes for one year. Documented LTS lines: 2.37 (2022-07-14, EOL 2023-07-31), 2.45 (2023-06-23, EOL 2024-07-31), 2.53 (2024-06-16, EOL 2025-07-31) -- all EOL at research time -- plus 3.5 (2025-07-14, supported until 2026-07-31) and 3.13 (2026-07-01, supported until 2027-07-31), both Supported at research time.
- Prometheus 3.0.0 (2024-11-14) -- First major version in 7 years. Removed `discovery.k8s.io/v1beta1` EndpointSlice and `networking.k8s.io/v1beta1` Ingress support in Kubernetes SD; removed deprecated `storage.tsdb.allow-overlapping-blocks`/`alertmanager.timeout`/`storage.tsdb.retention` flags; complete web UI rewrite (old UI recoverable via `--enable-feature=old-ui`, missing exemplar display and heatmaps at 3.0).
- TSDB on-disk format (v2.55 boundary) -- A Prometheus v3 TSDB can only be read by Prometheus v2.55+; downgrading below v2.55 loses persistent TSDB data. Docs recommend upgrading to 2.55 first, confirming stability, before jumping to v3.
- PromQL v2→v3 semantic changes -- The `.` regex metacharacter began matching newlines (affects any `.*`/`.+` pattern in queries or relabel rules); range-selector/lookback boundary semantics changed from closed-closed to open-closed.
- Log format change at v3 -- Switched from `go-kit/log` to Go's standard `log/slog`, changing the on-disk/stdout log line format -- a breaking change for anything parsing Prometheus's own log output.
- API stability for 3.x -- Query language/data model, alerting/recording rules, exposition format, v1 HTTP API (excluding experimental endpoints), config file format (excluding SD/remote read/write), and the OTLP receiver endpoint are all documented Stable. Explicitly unstable: `double_exponential_smoothing`, remote read, server-side HTTPS/basic-auth, most SD integrations, internal Go package APIs, the exact on-disk TSDB format, and log-line format.

## Python

- 3.14.7 -- Current stable release as of research date 2026-09-09 (docs.python.org landing page last-updated stamp: 2026-09-08)
- 3.15 -- In release-candidate stage at research time; GA expected ~October 2026 per annual PEP 602 cadence
- 3.13 -- Introduced free-threaded (no-GIL) CPython experimentally (PEP 703) and experimental JIT (PEP 744); 2to3/lib2to3 removed; iOS/Android Tier 3 support added
- 3.12 -- distutils removed (PEP 632); per-interpreter GIL (PEP 684); PEP 695 generic syntax; comprehension inlining (PEP 709, ~2x faster); sys.monitoring (PEP 669); perf profiler integration added
- 3.14.5+ -- Mid-cycle patch-level behavioral revert: incremental GC (shipped in 3.14.0-3.14.4) reverted back to generational GC due to production memory-pressure reports — patch version matters, not just minor version
- 3.14 -- Free-threading officially supported (PEP 779); template strings (PEP 750); deferred annotation evaluation (PEP 649/749); subinterpreters in stdlib (PEP 734); safe remote debugger attach (PEP 768); tail-call interpreter; int()/__trunc__ and NotImplemented-bool breaking changes; ProcessPoolExecutor default start method changed to forkserver on non-macOS Unix
- 3.11 -- pyporting.html Python-2-to-3 porting HOWTO discontinued as of this version (archived copy remains under 3.10 docs branch only)
- pre-3.13 vs 3.13+ -- Bugfix-to-security-phase transition is 18 months for releases before 3.13, but 2 years for 3.13 and later, even though total 5-year support window is unchanged

## React

- 19.0 (Dec 5, 2024) -- Current major version baseline; introduced Actions/useActionState/useFormStatus/useOptimistic, use(), ref-as-prop, native document metadata/stylesheets, react-dom/static, RSC stable (app-facing)
- 19.2 (Oct 1, 2025) -- Current minor; added Activity component, useEffectEvent, cacheSignal, partial pre-rendering, Chrome DevTools performance tracks, useId prefix change (:r: -> _r_), React Compiler reached v1.0 same week
- 19.2.8 (npm latest, ~July 2026 per GitHub release title) -- Current patch per npm dist-tags as of research date 2026-09-09
- 19.0.1 / 19.1.2 / 19.2.1 -- First-round security patches for critical RSC RCE CVE-2025-55182 (Dec 3, 2025) — later found incomplete
- 19.0.4 / 19.1.5 / 19.2.4 -- Second-round, actually-complete security patches for RSC DoS/source-exposure CVEs (Dec 11, 2025); apps on the Dec-3 patch versions were still vulnerable
- 18.3.1 (last 18.x release per search snippet) -- Recommended intermediate upgrade step before jumping 18->19, to surface deprecation warnings first
- React 17 -> 18 (March 2022) -- Separate official upgrade guide exists (react.dev/blog/2022/03/08/react-18-upgrade-guide) but was not fetched in full in this research pass — flagged Unresolved
- React Compiler v1.0 (Oct 7, 2025) -- First stable release; works with React 17+ (17/18 need react-compiler-runtime + target config), pre-wired into new Vite/Next.js/Expo SDK 54+ scaffolds

## Redis

- 8.10 -- Current latest Standard-release GA version per the official supported-versions table at research time (2026-09-09); EOL not yet set
- 8.0 -- Major version boundary with documented breaking changes: rename to 'Redis Open Source', tri-license (RSALv2/SSPLv1/AGPLv3), Search/JSON/Time-series/probabilistic types bundled into core, and a breaking ACL-category widening/narrowing change
- 8.4 -- Introduced atomic SET IFEQ/IFNE/IFDEQ/IFDNE and DELEX compare-and-set/delete commands for strings
- 8.6 -- Introduced LRM (Least Recently Modified) eviction policy
- 8.10.0 -- Introduced the new online BACKUP command family and preload-file restore option
- 7.0 -- Major feature/behavior boundary: Redis Functions, ACL subcommand allow/block and selectors, read-only script commands, client eviction (maxmemory-clients), multi-part AOF format, acl-pubsub-default flips to resetchannels
- 7.0.1 -- Tightened read-only-script semantics (PUBLISH/SPUBLISH/PFCOUNT now count as writes; no-writes flag implies allow-oom)
- 6.0 -- ACLs introduced as the recommended auth mechanism; RESP3 experimental opt-in support added
- 6.0.9 -- Fixed: expired keys now correctly abort a WATCHed transaction
- 4.0 -- Sub-replica replication streaming and writable-replica TTL-eviction parity introduced
- 3.2.0 -- Protected mode auto-enables under default config with no password

## Sass

- 1.104.0 -- Current documentation reference target as of 2026-09-09 (released 2026-09-03); colors now clamp NaN/negative-zero/infinity per CSS spec
- 1.103.0/1.103.1 -- Released 2026-08-20; color-space conversions now preserve 'analogous sets' of missing channels per CSS spec
- 1.101.0 -- Node package importer resolution of import-only file variants changed, may break code relying on old order
- 1.100.0 -- 'Adjacent compound selectors' breaking change introduced
- 1.80.0 -- @import deprecation warnings begin; full removal not before ~2 years later, targeted for Dart Sass 3.0.0
- 1.79.0 -- Legacy JS API deprecated; Color API and color-function deprecations begin
- 3.0.0 (future/unreleased) -- Target version for full @import removal; commitment states it will not release sooner than 2 years after 1.80.0
- 2.0.0 of npm 'sass' package (future/unreleased) -- Target for removal of legacy render()/renderSync() JS API

## Sentry

- JS SDK 10.74.0 (stable, released 2026-09-09) -- Current stable release of the JavaScript SDK monorepo (`@sentry/node`, `@sentry/browser`, framework packages); 11.0.0-beta.2 also published, indicating v11 is in active beta.
- Python SDK 2.69.1 (released 2026-09-08) -- Current stable `sentry-sdk` release on PyPI; classifiers declare Python 3.6-3.15 support, no narrower floor found for the SDK itself.
- Node.js runtime floor (JS/Node SDK) -- Minimum 18.0.0, with 18.19.0+ or 19.9.0+ recommended "for optimal support and future TracingChannel features."
- SDK v9.0.0 -- Node.js minimum raised to 18.0.0; TypeScript minimum raised to 5.0.4; Prisma <6.x dropped; **Metrics API removed entirely** (not merely deprecated); Hub-era APIs (`getCurrentHub()`, `Hub`, `getCurrentHubShim()`) fully removed; `@sentry/utils` folded into `@sentry/core`.
- SDK v10.0.0 -- `BaseClient` removed (use `Client`); `hasTracingEnabled` removed (use `hasSpansEnabled`); OpenTelemetry dependency floor raised to 2.x/0.20x.x (projects unable to move to OTel v2 must stay on v9 or adopt `@sentry/node-core`); AWS Lambda Layer renamed to `SentryNodeServerlessSDKv10`.
- SDK v8.0.0 -- Node.js minimum raised to 14.18.0; `startTransaction`/`span.startChild` removed from the custom tracing API; initialization-ordering requirement introduced (Sentry must be imported before any other package).
- No consolidated SDK×runtime×framework compatibility matrix -- Version floors were assembled from the migration-guide series and current-install pages rather than one authoritative table; re-derive per-project rather than assuming a single source covers it.

## shadcn/ui

- shadcn CLI 4.21.0 (npm, current as of 2026-09-09) -- Actively maintained package is named `shadcn` (no -ui suffix); legacy `shadcn-ui` npm package is deprecated/unmaintained (~2 years stale)
- CLI v4 line (from March 2026) -- Introduced shadcn/skills, Presets system, --dry-run/--diff/--view, --base flag, registry:base items, --monorepo
- Base UI default (from July 2026) -- New projects default to Base UI instead of Radix UI as the headless primitive library; opt back into Radix via `init -b radix`; not forced/breaking for existing apps
- Tailwind v4 (default for new projects from ~Feb 2025) -- Existing Tailwind v3 + React 18 projects unaffected; migration requires @theme inline, forwardRef removal, data-slot attributes, Toast→Sonner, style default→new-york
- cn package (from September 2026) -- Replaces hand-rolled clsx+tailwind-merge lib/utils.ts; non-breaking, opt-in via `migrate cn`
- style: "new-york" vs "default" -- "default" style is deprecated; style field is immutable after project init

## Socket.IO

- 4.8.3 (Dec 23, 2025) -- Current stable server release; verified live against the changelog page during this research pass
- 4.0.0 (March 2021) -- Full TypeScript rewrite; server-side breaking changes only, protocol-compatible with v3 clients
- 4.1.0 -- Added serverSideEmit() and InterServerEvents TS generic
- 4.1.3 -- Heartbeat direction changed to server-initiated pings to mitigate browser tab-throttling disconnects
- 4.4.0 -- Added SocketData TS generic, uWebSockets.js engine binding, io.engine.use() Express-style middleware
- 4.6.0 -- Added connectionStateRecovery, cleanupEmptyChildNamespaces, addTrailingSlash options
- 4.7.0 -- Added WebTransport support
- 3.0 -- CORS disabled by default (was implicit-allow in 2.x); maxHttpBufferSize default cut 100MB->1MB; perMessageDeflate disabled by default; several API renames (error->connect_error, Namespace.clients()->allSockets() now async, Socket.rooms object->Set); IE8/Node 8 support dropped
- Node.js >=10 (server) -- Documented minimum supported Node version for the socket.io server package
- IE9+ (client) -- Documented minimum supported browser; IE6/7/8 explicitly unsupported
- Redis 7.0+ -- Required specifically for sharded Pub/Sub topology in the Redis adapter, not for the adapter generally

## Swagger

- Swagger UI 5.32.15 (2026-09-04) -- Current stable per GitHub releases page as of research date; README separately states 5.32.0, an unresolved minor discrepancy attributed to README staleness
- Swagger UI 5.x line -- Actively supported/patched; supports OpenAPI 2.0, 3.0.x, 3.1.x, 3.2.0
- Swagger UI 4.x -- EOL for security patches August 2023; requires React 17.x/Redux 4.x (breaking change introduced in v4.0.0, Nov 2021)
- Swagger UI 3.x -- EOL November 2021
- Swagger UI 2.x -- EOL 2017
- Swagger UI < 4.1.3 -- Vulnerable to GHSA-qrmm-w75w-3wpx (?url param SSRF/phishing vector); fixed by disabling query-string spec override by default in 4.1.3 (Dec 2021)
- Swagger UI v5.0.0 (2023-06-12) -- Added OpenAPI 3.1.0 support, JSON Schema 2020-12 keyword rendering, multi-platform Docker images, PORT_IPV6 env var; no breaking config changes enumerated in release notes
- Swagger Codegen 3.0.71 (2025-07-03) vs 2.4.46 (2025-06-30) -- Two parallel, independently versioned major lines (not sequential) — 3.x targets OpenAPI 3.0.x, 2.x targets Swagger/OpenAPI 1.0-2.0
- Swagger Editor Node.js requirement -- Floor is Node >=12.22.0; currently recommended dev versions are Node >=24.18.0 and npm >=11.16.0

## Tailwind CSS

- 4.3.3 -- Current stable release per npm 'latest' dist-tag, released 2026-07-16 per official changelog
- 4.0.0 -- First v4 stable release, 2025-01-21 — major architectural rewrite (Oxide/Lightning CSS engine), CSS-first @theme config, raised browser floor to Safari 16.4+/Chrome 111+/Firefox 128+, dropped Sass/Less/Stylus support
- 4.1.0 -- Released 2025-04-01 — text-shadow, mask utilities, and other additions per blog title (not deeply investigated beyond changelog date)
- 4.2.0 -- Released 2026-02-18 — added mauve/olive/mist/taupe color palettes, new webpack plugin, logical-property block-start/end utilities
- 4.3.0 -- Released 2026-05-08 — scrollbar utilities, @container-size queries, zoom-*/tab-* utilities, enhanced @variant (stacked/compound), --default() for functional custom utilities
- 3.4.19 -- Latest patch on the v3 line (npm 'v3-lts' dist-tag), released 2025-12-10 — confirms Tailwind Labs continues to backport fixes to v3 nearly a year after v4.0 shipped, though no formally documented LTS policy/end-date was found
- 3.0.0 / 3.4.0 -- v3.0.0 released 2021-12-09; v3.4.0 released 2023-12-19 — cited for major-version timeline context only, not deeply researched

## Three.js

- r186 / npm 0.186.0 -- Current stable version as of research date 2026-09-09; published 2026-09-08 per GitHub Releases API. Confirmed against package.json on the dev branch.
- r163 -- WebGLRenderer dropped WebGL 1 support; WebGL 2 required from this release onward.
- r147 -- Classic non-module <script src> global-namespace loading became unsupported; ES6 modules + import maps became the only supported loading method; examples/js (non-module) directory removed in favor of examples/jsm.
- r152 onward (multi-release rollout) -- Major Color Management overhaul: Texture.encoding/outputEncoding replaced by colorSpace/outputColorSpace; ColorManagement.enabled defaults to true; sRGBEncoding/LinearEncoding renamed to SRGBColorSpace/LinearSRGBColorSpace.
- r160 -> r161 -- Legacy build/three.js and build/three.min.js UMD/global build files removed from distribution.
- r180 -> r181 -- PBR indirect specular and energy conservation math changed (visual appearance change for existing rough materials); API docs switched to JSDoc-generated system; internationalization (i18n) dropped, docs became English-only.
- r181 -> r182 -- PCFSoftShadowMap deprecated for WebGLRenderer (use PCFShadowMap).
- r182 -> r183 -- Clock class deprecated in favor of Timer; PostProcessing renamed to RenderPipeline; WebGLCubeRenderTarget no longer usable with WebGPURenderer.
- r183 -> r184 -- FileLoader.load()/ImageBitmapLoader.load() stopped returning a value (callback-only); FBXLoader began auto-converting +Z-up models to +Y-up.
- r185 -> r186 -- Object3D gained dispose(); PCFSoftShadowMap fully removed for WebGPURenderer; BufferGeometryUtils.toTrianglesDrawMode() now mutates geometry in-place instead of cloning; Source renamed to TextureSource; CommonJS build and minified builds deprecated/removed per changelog (though package.json still exposes a cjs require path).
- 186 -> 187 (in-progress, per wiki at fetch time) -- WebGLRenderer.setViewport()/setScissor() will no longer scale by pixel ratio when a render target is bound.

## TypeORM

- 1.1.1 -- Current stable release, published 2026-09-01 per GitHub Releases API. Patch/fix release: version-comparison fix, many-to-many inverse FK CASCADE default, relation-value resolution inside embedded entities, cache/query-runner leak fixes.
- 1.1.0 -- Published 2026-07-13. Added distinct-count query support, fixed multiple recursive-CTE problems, tree-entity schema propagation fixes, stricter where-criteria validation on update/delete.
- 1.0.0 -- Published 2026-05-19. First 1.x major, carries documented breaking changes: Node.js 20+ required, DataSource replaces Connection, findOneById/findByIds/exist removed, string select/relations syntax removed, IoC container removed, mysql2-only/better-sqlite3-only/Mongo-driver-v7+-only, invalidWhereValuesBehavior now defaults to throw, non-nullable relations default to INNER JOIN.
- 0.3.31 -- Published 2026-07-13, same day as 1.1.0 — a backport release on the legacy 0.3.x line, showing parallel maintenance continued past the 1.0 cutover. No official end-of-support date found for 0.3.x.
- TypeScript 4.5+ -- Stated minimum in Getting Started docs; flagged as possibly stale given rapid 2026 changes around the v1.0 line, not independently re-verified against the live page.
- Node.js 20+ -- Hard requirement as of v1.0.0 (Node 16/18 support dropped); CI currently tests Node 20 and 24 per Supported Platforms page.

## TypeScript

- 7.0.2 (current, npm) -- Current published stable version as of 2026-09-09 per npmjs.com; TypeScript 7.0 line is the Go-native compiler rewrite released 2026-07-08
- 7.0 -- Complete compiler rewrite in Go ('tsgo'); ships with NO programmatic Compiler API (deferred to 7.1); removed target:es5, baseUrl; rootDir now defaults to './'; adopts 6.0's defaults
- 6.0 -- Released 2026-03-23 as a deliberate bridge release to 7.0; changed defaults: strict=true, module=esnext, target=es2025 (floating), types=[]; removed target:es5, --outFile, AMD/UMD/SystemJS modules, moduleResolution classic; deprecated baseUrl and moduleResolution node
- 5.9 -- Preceded 6.0; introduced leaner tsc --init defaults, --module node20, import defer syntax; breaking change: ArrayBuffer no longer supertype of typed arrays in lib.d.ts
- 5.0 -- Stage-3 ECMAScript decorators became usable without experimentalDecorators flag, per decorators.html cross-reference
- 5.6 / 5.7 -- tsconfig reference notes noUncheckedSideEffectImports added in 5.6, rewriteRelativeImportExtensions added in 5.7
- <=6.0 (Compiler API) -- The entire documented programmatic Compiler API (createProgram, createSourceFile, transpileModule, LanguageService) is explicitly flagged by the official wiki as describing '6.0 and earlier' only; 7.1 will have a completely different API
- Node.js v22.6.0 to v26.0.0 -- Node's native TS type-stripping: experimental from v22.6.0, default-on from v23.6.0/v22.18.0, stable from v25.2.0/v24.12.0, flag removed (standard) in v26.0.0 -- this is Node's own version timeline, not TypeScript's

## Vite

- v8.2.2 (current stable) -- Latest patch of the current major as observed in this research pass; support tiers place it in the 'regular patches' tier per vite.dev/releases
- v8.0 (major) -- Released ~March 12, 2026 (date via WebFetch summary, not independently re-verified). Introduced Rolldown as the unified Rust bundler replacing esbuild+Rollup, Oxc replacing esbuild for JS transform/minify, Lightning CSS as default CSS minifier, raised default build.target baseline, changed CJS default-import interop, integrated Devtools, resolve.tsconfigPaths option, requires Node 20.19+/22.12+
- v7.x -- Prior major; vite@7.3 sits in the 'important fixes and security patches' support tier alongside vite@8.1 per the rolling support policy
- v6.x -- Introduced the Environment API generalizing beyond the old client/SSR-only model; vite@6.4 is in the security-patches-only support tier
- rolldown-vite (separate npm package) -- Implements Vite 7 behavior but with the Rolldown bundler, without the rest of the v8 changes — an interim adoption path

## Vitest

- 5.0.0 (released 2026-09-03) -- Current stable major as of this research (2026-09-09). Requires Vite >=6.4.0, Node >=22.12.0. clearMocks defaults true; vi.mock/unmock/hoisted must be module-scope only; bench() rewritten as test-context fixture; vi.mock UI requires token auth; report artifacts consolidated under .vitest/; worker/concurrency IDs now 1-based; fake timers mock Temporal API; unawaited async assertions now fail tests.
- 4.1 -- Immediately prior minor; per official releases policy this is the only other version still receiving security-patch backports. Since 4.1, setting api.host off localhost disables UI save/run buttons as a hardening measure.
- 3.2 -- workspace config key deprecated in favor of projects (functionally equivalent) -- relevant when migrating configs older than 3.2.
- 3.2.0 (coverage) -- V8 coverage-provider report accuracy documented as reaching parity with Istanbul starting from this version.

## Vue.js

- 3.5.42 -- Current npm 'latest' dist-tag stable release as of 2026-09-09 research date
- 3.6.0-rc.7 -- Newest pre-release (Sep 4 2026) on the npm 'rc' dist-tag; introduces Vapor Mode, feature-complete per release notes but still explicitly recommended only for partial adoption / small apps, not full production - not yet promoted to 'latest'
- 3.4 -- computed() only re-triggers dependent effects when its return value actually changes, not on every re-evaluation
- 3.3 -- defineOptions() and defineSlots() compiler macros introduced in script setup
- 3.4 (defineModel) -- defineModel() compiler macro introduced for two-way v-model bindings in script setup
- 3.5 -- Reactive Props Destructure (destructured defineProps() bindings stay reactive) and lazy-hydration strategies (hydrateOnIdle/Visible/MediaQuery/Interaction) introduced
- 2.7.16 -- Final/legacy Vue 2 npm version; Vue 2 reached end of official support Dec 31 2023
- Vue 2 vs Vue 3 reactivity -- Vue 2 used Object.defineProperty getter/setters exclusively (Proxy unsupported in target browsers); Vue 3 uses native Proxy for reactive() - a core architectural difference, not just a version bump

## WebRTC

- W3C Recommendation, published 13 March 2025 -- Current canonical spec status/date for WebRTC 1.0; no semantic vX.Y.Z version exists for the spec as a whole
- Chrome M72 (Jan 2019) -- Unified Plan SDP semantics became the default (was previously Plan B)
- Chrome M93 (Canary) / M96 (Stable, all channels) -- Explicitly requesting sdpSemantics: 'plan-b' throws an exception rather than silently falling back
- Data channel max message size: 64 KB default, >=256 KB in 'modern browsers' -- Governed by SDP max-message-size attribute (RFC 8841) absent explicit negotiation
- Safari 12.1+ -- Point where VP8 support was added
- Firefox for Android 68-72 -- Lacked H.264 support due to Google Play store requirements
- Chrome 113+, Firefox 136+ -- AV1 video codec support, as captured on 2026-09-09
- Chrome 136+ -- HEVC/H.265 support, as captured on 2026-09-09
- W3C WebRTC WG charter through 30 September 2026 -- As observed on research date 2026-09-09; charters are commonly renewed

## WebSocket API

- RFC 6455 (Dec 2011, Internet Standard STD 34) -- Normative wire protocol; Sec-WebSocket-Version: 13; never superseded/revised by a later RFC
- WHATWG WebSockets Living Standard (no version number, split from HTML Standard in 2021) -- Governs the browser-implemented JS interface and Fetch-integrated handshake; actively maintained (commits as recent as 2026-03-15)
- WebSocket() constructor http(s)-scheme acceptance -- Added to spec ~May 2023; earlier engines/docs should assume only ws/wss schemes accepted, not http/https auto-normalization
- MDN WebSocket interface: Baseline Widely available since July 2015 -- Stable, broadly supported browser API surface
- WebSocketStream -- Experimental/non-standard, single rendering engine support as of research date — not production-ready
- Node.js global WebSocket (client-only) -- Added v21.0.0 / backported v20.10.0 behind --experimental-websocket; flag requirement removed v22.0.0; marked stable/no-longer-experimental v22.4.0
- RFC 7692 permessage-deflate (Dec 2015) and RFC 8441 WebSockets-over-HTTP/2 (Sep 2018) -- Companion extension RFCs layered on top of RFC 6455, not replacements

## Technologies with no captured version-sensitive facts

None -- every researched technology has at least one captured version-sensitive fact.
