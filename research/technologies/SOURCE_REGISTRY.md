# Source Registry

This file registers every official documentation source consulted while researching the 52 technologies in this Skill Library project. It exists so anyone auditing or extending a technology's research doc can see exactly which primary sources were used, without re-opening every individual `research/technologies/<slug>.md` file. Sources are grouped by technology in the order they were cited during research; the final section aggregates all distinct source domains across the whole project, ranked by how many technologies cite them.

## Angular

- https://angular.dev/overview -- What is Angular - core concepts, architecture overview, tooling summary
- https://angular.dev/reference/releases -- Versioning scheme, release cadence, LTS/support windows, current supported-versions table
- https://angular.dev/guide/components -- Component fundamentals, standalone-by-default behavior and the pre-v19 default
- https://angular.dev/guide/signals -- Signals core API: signal(), computed(), effect(), reactive contexts
- https://angular.dev/guide/di -- Dependency injection fundamentals, inject() function, services
- https://angular.dev/guide/di/creating-and-using-services -- @Injectable() vs the new v22 @Service() decorator, providedIn:'root'
- https://angular.dev/guide/zoneless -- Zoneless change detection: status, how to enable, relationship to OnPush/signals
- https://angular.dev/guide/templates -- Template syntax fundamentals, control flow, binding syntax, @defer mention
- https://angular.dev/guide/templates/defer -- @defer deferrable views: triggers, prefetch, placeholder/loading/error blocks
- https://angular.dev/guide/routing -- Angular Router: routes, outlets, links, guards, resolvers
- https://angular.dev/guide/forms -- Reactive vs template-driven forms, FormControl/FormGroup/FormArray, mention of Signal Forms
- https://angular.dev/essentials/signal-forms -- Signal Forms essentials: core API (form(), signal(), formField, validators)
- https://angular.dev/guide/http -- HttpClient overview: typed responses, interceptors, httpResource(), testing
- https://angular.dev/guide/signals/resource -- resource() and httpResource() APIs for async data in signal-based code
- https://angular.dev/ecosystem/rxjs-interop -- RxJS interop package: toSignal, toObservable, rxResource, takeUntilDestroyed
- https://angular.dev/best-practices/security -- Security guidance: sanitization, DomSanitizer bypass methods, XSRF, CSP, Trusted Types, AOT
- https://angular.dev/best-practices/runtime-performance -- Runtime performance guide topic overview: change detection, zoneless, profiling
- https://angular.dev/best-practices/images -- NgOptimizedImage directive: priority loading, srcset, fill mode, CDN loaders
- https://angular.dev/guide/testing -- Testing setup: Vitest as new default runner, Karma/Jasmine support, component harnesses
- https://angular.dev/tools/cli/deployment -- Deployment: ng build/ng deploy, CLI deploy builders, SPA server fallback, base href, CORS
- https://angular.dev/guide/ssr -- Server-side rendering: enabling SSR, rendering modes, server routes, browser API access
- https://angular.dev/guide/hydration -- DOM hydration, incremental hydration, event replay
- https://angular.dev/tools/devtools -- Angular DevTools: component tree, profiler, injector tree, router tree, dev-build-only limitation
- https://angular.dev/style-guide -- Official style guide: naming, file organization, DO/AVOID pattern table
- https://angular.dev/guide/ngmodules/overview -- NgModules: purpose, current recommendation status vs standalone components
- https://angular.dev/reference/configs/workspace-config -- angular.json workspace configuration structure and schema
- https://angular.dev/reference/versions -- Node.js/TypeScript/RxJS compatibility table and browser support (Baseline) policy
- https://angular.dev/reference/migrations -- List of 13 automated ng generate migration schematics
- https://angular.dev/update-guide -- Interactive Update Guide tool for generating version-upgrade instructions
- https://angular.dev/best-practices/error-handling -- ErrorHandler, global error listeners, startup error handling, TestBed error rethrowing
- https://angular.dev/errors/NG0100 -- Error Encyclopedia example page: NG0100 ExpressionChangedAfterItHasBeenCheckedError
- https://angular.dev/ecosystem/service-workers -- Angular service worker: PWA/offline caching, ngsw.json, HTTPS requirement, limited featureset
- https://angular.dev/api -- API reference organization: packages list, stability badges (Stable/Developer Preview/Experimental/Deprecated)
- https://angular.dev/ai/agent-skills -- Official Angular Agent Skills for AI coding agents: angular-developer and angular-new-app skills
- https://raw.githubusercontent.com/angular/angular/main/CHANGELOG.md -- Canonical raw CHANGELOG.md with full Breaking Changes sections for v20.0.0, v21.0.0, v22.0.0
- https://blog.angular.dev/announcing-angular-v22-c52bb83a4664 -- Official v22 announcement blog post: signal-first release framing, Signal Forms/Angular ARIA stabilization

## Anthropic Claude API (Messages API)

- https://platform.claude.com/docs/en/models/overview -- model lineup, comparison table, pricing summary, retirement commitments, Models API
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview -- when/how to prompt engineer, entry point
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices -- system prompts, XML tags, multishot, chain-of-thought, long-context prompting, agentic-system patterns, migration guidance
- https://platform.claude.com/docs/en/build-with-claude/context-windows -- context window sizes, context rot, context awareness, thinking-and-context-window interaction, overflow behavior
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview -- tool definitions, tool_choice, pricing, tool catalog
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works -- agentic loop mechanics, client vs server tool execution model
- https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons -- full stop_reason table, pause_turn handling
- https://platform.claude.com/docs/en/build-with-claude/prompt-caching -- cache breakpoints, TTL, pricing multipliers, minimum lengths
- https://platform.claude.com/docs/en/build-with-claude/thinking -- adaptive vs extended thinking, display modes, preservation rules, interleaved thinking
- https://platform.claude.com/docs/en/build-with-claude/effort -- effort levels, per-model defaults and guidance
- https://platform.claude.com/docs/en/build-with-claude/structured-outputs -- output_config.format, strict tool use, JSON Schema support matrix
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool -- computer use architecture, safety guidance, pricing
- https://platform.claude.com/docs/en/api/rate-limits -- spend limits, RPM/ITPM/OTPM, cache-aware limiting, tiers, response headers
- https://platform.claude.com/docs/en/api/errors -- HTTP error codes, error shape, request IDs, common validation errors
- https://platform.claude.com/docs/en/build-with-claude/streaming -- SSE event sequence, delta types, error events
- https://platform.claude.com/docs/en/api/versioning -- anthropic-version header contract and history
- https://platform.claude.com/docs/en/build-with-claude/batch-processing -- Message Batches API mechanics, limits, pricing
- https://platform.claude.com/docs/en/about-claude/model-deprecations -- deprecation policy, notice period, full lifecycle table, parameter deprecations
- https://platform.claude.com/docs/en/manage-claude/authentication -- API keys, Workload Identity Federation, App Attest
- https://platform.claude.com/docs/en/test-and-evaluate/develop-tests -- success criteria, eval design principles, grading methods
- https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks -- jailbreak/prompt-injection threat model and mitigations
- https://platform.claude.com/docs/en/cli-sdks-libraries/overview -- CLI, client SDKs, libraries/integrations, Agent SDK/Managed Agents disambiguation
- https://code.claude.com/docs/en/agent-sdk/overview -- Claude Agent SDK architecture, capabilities, comparison table (separate host from platform.claude.com)
- https://platform.claude.com/docs/en/managed-agents/overview -- Managed Agents architecture, core concepts, when to use, beta status, ZDR ineligibility
- https://platform.claude.com/docs/en/about-claude/pricing -- full pricing structure, tool/feature-specific pricing, Managed Agents billing
- https://platform.claude.com/docs/en/build-with-claude/vision -- image formats/limits, token cost, multi-image guidance, documented limitations
- https://docs.claude.com/en/docs/test-and-evaluate/eval-tool -- used only to confirm the 302 redirect to platform.claude.com (host-migration verification)

## ClickHouse

- https://clickhouse.com/docs -- Docs homepage / navigation structure
- https://clickhouse.com/docs/get-started/about/deployment-modes -- The five official deployment forms: Server, Cloud, CLI, clickhouse-local, chDB
- https://clickhouse.com/docs/architecture/introduction -- Replica/shard terminology and ClickHouse Keeper's coordination role
- https://clickhouse.com/docs/about-us/distinctive-features -- Distinctive architectural features
- https://clickhouse.com/docs/en/introduction/features_considered_disadvantages -- Official documented limitations (no full transactions, inefficient point queries, no low-latency row updates)
- https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree -- MergeTree engine internals: parts, granules, sparse index, partitioning
- https://clickhouse.com/docs/interfaces/overview -- Client interfaces/APIs: HTTP, native TCP, JDBC/ODBC/ADBC, gRPC, Arrow Flight
- https://clickhouse.com/docs/interfaces/mysql -- MySQL wire-protocol compatibility and its caveats
- https://clickhouse.com/docs/operations/configuration-files -- config.xml/users.xml, config.d overrides, YAML support, substitutions
- https://clickhouse.com/docs/guides/sre/network-ports -- Default network ports for all protocols
- https://clickhouse.com/docs/best-practices -- Index of official best-practice topics
- https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy -- Batch size and async insert guidance
- https://clickhouse.com/docs/best-practices/minimize-optimize-joins -- JOIN algorithm selection and anti-patterns
- https://clickhouse.com/docs/best-practices/choosing-a-partitioning-key -- Partitioning key guidance and over-partitioning anti-pattern
- https://clickhouse.com/docs/best-practices/use-data-skipping-indices-where-appropriate -- Data skipping index types and usage guidance
- https://clickhouse.com/docs/optimize/avoid-nullable-columns -- Why Nullable columns should be avoided
- https://clickhouse.com/docs/best-practices/avoid-mutations -- Why mutations should be avoided and alternatives
- https://clickhouse.com/docs/optimize/query-optimization -- Structured query optimization workflow (Diagnose/Isolate/Optimize)
- https://clickhouse.com/docs/operations/access-rights -- RBAC: users, roles, row policies, settings profiles, quotas
- https://clickhouse.com/docs/security-and-authentication -- Security documentation index (users/roles, ports, TLS, external auth)
- https://clickhouse.com/docs/troubleshooting -- Official troubleshooting guide for performance, memory, connection, config issues
- https://clickhouse.com/docs/guides/developer/debugging-memory-issues -- Memory-issue debugging guide
- https://clickhouse.com/docs/knowledgebase/useful-queries-for-troubleshooting -- Diagnostic SQL queries for troubleshooting
- https://clickhouse.com/docs/resources/develop-contribute/contribute/tests -- How ClickHouse's own codebase is tested (functional/integration/unit/stress/fuzz)
- https://clickhouse.com/docs/guides/generating-test-data -- Generating synthetic test data with ClickHouse SQL functions
- https://clickhouse.com/docs/operations/performance-test -- Official hardware performance-test script
- https://clickhouse.com/docs/operations/update -- Self-managed upgrade guide: rolling upgrades, downgrade limits, Keeper upgrade independence
- https://clickhouse.com/docs/migrations/postgresql/overview -- PostgreSQL-to-ClickHouse migration approaches (CDC vs bulk load)
- https://clickhouse.com/docs/migrations/postgresql -- PostgreSQL migration guide track index
- https://clickhouse.com/docs/resources/changelogs/oss/2026 -- 2026 changelog, source for 26.8 LTS breaking changes
- https://clickhouse.com/docs/faq/operations/production -- Guidance on choosing a production version; Stable vs LTS track philosophy
- https://clickhouse.com/docs/knowledgebase/maximum_number_of_tables_and_databases -- Recommended maximum databases/tables/partitions/parts per service
- https://clickhouse.com/docs/integrations -- Integration categories and Core/Partner/Community support tiers

## CSS (Cascading Style Sheets)

- https://developer.mozilla.org/en-US/docs/Web/CSS -- MDN CSS landing/overview page: module structure, guides, reference index
- https://www.w3.org/TR/css-2026/ -- W3C CSS Working Group Group Note: CSS Snapshot 2026, current state/tiers of CSS modules
- https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Cascade -- MDN guide to the CSS cascade algorithm (origin, importance, layers, specificity, order)
- https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity -- MDN guide to specificity calculation, :is()/:where() behavior, !important
- https://developer.mozilla.org/en-US/docs/Web/API/CSS_Object_Model -- MDN CSSOM overview: interfaces (CSSStyleSheet, CSSRule, etc.) and JS/CSS interaction
- https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_shadow_parts -- MDN guide to CSS/Shadow DOM integration: :host, ::part, ::slotted, exportparts
- https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_nesting -- MDN guide to native CSS nesting module, syntax, specificity gotchas
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@supports -- MDN reference for @supports feature queries and related functions
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@property -- MDN reference for @property at-rule (typed custom properties, Houdini)
- https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascading_variables/Using_custom_properties -- MDN guide to custom properties (CSS variables), var(), inheritance, limitations
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/box-sizing -- MDN reference for box-sizing property and border-box best-practice recommendation
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/will-change -- MDN reference for will-change: usage, performance guidance, overuse warnings
- https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Using -- MDN guide to CSS containment (contain property) for rendering performance
- https://web.dev/articles/content-visibility -- Google/Chrome team (web.dev) article on content-visibility rendering performance
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@container -- MDN reference for @container container queries, container-type, Baseline status
- https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Selectors/Privacy_and_:visited -- MDN guide on :visited selector history-sniffing privacy issue and browser mitigations
- https://web-platform-tests.org/test-suite-design.html -- Official web-platform-tests documentation describing the shared CSS conformance test suite
- https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Debugging_CSS -- MDN Learn guide: official CSS debugging workflow and DevTools usage
- https://firefox-source-docs.mozilla.org/devtools-user/page_inspector/how_to/examine_grid_layouts/index.html -- Firefox source docs on the DevTools CSS Grid Inspector
- https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Getting_started -- MDN Learn guide: how to attach CSS to a document (external/internal/inline)
- https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Syntax/Error_handling -- MDN guide to CSS's forward-compatible error-handling/parsing model
- https://developer.mozilla.org/en-US/docs/Glossary/Vendor_Prefix -- MDN glossary entry on vendor prefixes, current guidance to avoid them in production
- https://www.w3.org/2004/02/Process-20040205/tr.html -- W3C Recommendation Track process document: WD/CR/PR/REC maturity stages
- https://developer.mozilla.org/en-US/docs/Glossary/Baseline/Compatibility -- MDN glossary entry defining Baseline widely/newly/limited availability tiers
- https://en.wikipedia.org/wiki/MDN_Web_Docs -- Cited only for the general fact of MDN's 2025 front-end rebuild affecting URL structure, not as a technical CSS source

## Docker

- https://docs.docker.com/get-started/docker-overview/ -- Core concepts: images, containers, registries, Dockerfile
- https://docs.docker.com/engine/ -- Docker Engine architecture overview (dockerd, API, CLI client)
- https://docs.docker.com/engine/daemon/alternative-runtimes/ -- containerd/runc relationship and alternative runtime support (Wasmtime, gVisor, Kata, youki)
- https://docs.docker.com/engine/api/ -- Engine API versioning, SDKs, backward compatibility
- https://docs.docker.com/reference/ -- Overview of Docker's reference documentation surfaces (CLI, Compose CLI, Dockerfile, BuildKit)
- https://docs.docker.com/reference/cli/dockerd/ -- daemon.json configuration, storage/logging drivers, TLS options
- https://docs.docker.com/reference/dockerfile/ -- Dockerfile instruction reference, syntax directives, BuildKit-required features
- https://docs.docker.com/build/building/best-practices/ -- Official image-build best practices and anti-patterns
- https://docs.docker.com/build/cache/ -- Build cache mechanics and invalidation rules
- https://docs.docker.com/build/building/multi-platform/ -- Multi-platform builds: QEMU emulation, native builders, cross-compilation
- https://docs.docker.com/reference/build-checks/ -- docker build --check Dockerfile validation feature
- https://docs.docker.com/engine/security/ -- Security overview: namespaces, cgroups, capabilities, content trust, seccomp
- https://docs.docker.com/engine/security/rootless/ -- Rootless mode: how it works, requirements, installation
- https://docs.docker.com/engine/containers/resource_constraints/ -- CPU/memory resource constraint flags and OOM behavior
- https://docs.docker.com/engine/storage/ -- Storage drivers, volumes, bind mounts, tmpfs
- https://docs.docker.com/engine/network/ -- Networking drivers and default bridge network behavior
- https://docs.docker.com/engine/logging/configure/ -- Logging drivers, defaults, production log-rotation guidance
- https://docs.docker.com/engine/daemon/logs/ -- Enabling daemon debug logging
- https://docs.docker.com/engine/daemon/troubleshoot/ -- Docker daemon troubleshooting guidance
- https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/ -- Docker Desktop log locations (init.log on macOS/WSL2)
- https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/known-issues/ -- Docker Desktop known issues/limitations (Apple Silicon emulation, HyperKit, etc.)
- https://docs.docker.com/security/for-admins/hardened-desktop/enhanced-container-isolation/limitations/ -- Enhanced Container Isolation limitations (WSL2/kernel version requirements)
- https://docs.docker.com/reference/cli/docker/container/run/ -- docker run flags: healthcheck, restart policy, debugging flags
- https://docs.docker.com/engine/swarm/ -- Docker Swarm mode orchestration overview
- https://docs.docker.com/engine/install/ -- Docker Engine install platforms and patch-release compatibility statement
- https://docs.docker.com/engine/release-notes/29/ -- Docker Engine 29.x release notes: versions, dates, breaking changes, deprecations
- https://docs.docker.com/compose/ -- Docker Compose overview
- https://docs.docker.com/compose/migrate/ -- Official Compose V1-to-V2 deprecation/migration pointer page
- https://www.docker.com/blog/new-docker-compose-v2-and-v1-deprecation/ -- Official Docker blog post detailing Compose V1->V2 migration specifics and timeline
- https://github.com/docker/compose/releases -- Official Docker/Moby GitHub org repo: Compose version/release dates
- https://docs.docker.com/docker-hub/usage/pulls/ -- Docker Hub pull rate limits by account tier
- https://docs.docker.com/scout/ -- Docker Scout vulnerability scanning and SBOM analysis
- https://docs.docker.com/testcontainers/ -- Testcontainers official integration-testing documentation
- https://docs.docker.com/guides/testcontainers-cloud/ -- Testcontainers Cloud overview
- https://docs.docker.com/build/ci/github-actions/ -- Official Docker GitHub Actions for CI build/push integration
- https://docs.docker.com/subscription/desktop-license/ -- Docker Desktop licensing terms vs. Docker Engine open-source licensing

## Drizzle ORM

- https://orm.drizzle.team/docs/overview -- Core philosophy, design goals, supported dialects, headless/SQL-like positioning
- https://orm.drizzle.team/docs/get-started -- Installation, package names, database/driver options overview
- https://orm.drizzle.team/docs/latest-releases -- Docs-site release index (found stale relative to GitHub releases)
- https://orm.drizzle.team/docs/latest-releases/drizzle-orm-v1beta2 -- v1.0.0-beta.2 release notes, early v1 breaking-change warning
- https://orm.drizzle.team/docs/v0-v1-changes -- Full v0→v1 breaking changes and new features list
- https://orm.drizzle.team/docs/upgrade-v1 -- Official v0→v1 upgrade guide/steps
- https://orm.drizzle.team/roadmap -- v1 roadmap, feature status, completion indicator
- https://orm.drizzle.team/docs/sql-schema-declaration -- Schema definition (pgTable/mysqlTable/sqliteTable), organization patterns
- https://orm.drizzle.team/docs/rqb -- Relational Queries API (db.query, with clause, findMany/findFirst)
- https://orm.drizzle.team/docs/relations -- defineRelations API, relation types, indexing guidance
- https://orm.drizzle.team/docs/migrations -- Migration workflows: generate/migrate/push/pull, folder structure
- https://orm.drizzle.team/docs/drizzle-config-file -- drizzle.config.ts configuration options reference
- https://orm.drizzle.team/docs/transactions -- db.transaction() API, isolation levels, savepoints
- https://orm.drizzle.team/docs/connect-overview -- Full list of supported PostgreSQL drivers/providers
- https://orm.drizzle.team/docs/indexes-constraints -- index(), uniqueIndex(), primaryKey(), foreignKey(), check() APIs
- https://orm.drizzle.team/docs/goodies -- Logging, toSQL(), mock DB, type inference, introspection utilities
- https://orm.drizzle.team/docs/sql -- sql template, parameterization, sql.raw(), SQL-injection prevention
- https://orm.drizzle.team/docs/kit-overview -- drizzle-kit CLI command reference
- https://orm.drizzle.team/docs/seed-overview -- drizzle-seed deterministic test-data generation
- https://orm.drizzle.team/docs/batch-api -- db.batch() API, Neon HTTP driver support
- https://orm.drizzle.team/docs/cache -- Experimental caching layer, upstashCache, invalidation, gaps
- https://orm.drizzle.team/docs/perf-queries -- Prepared statements as primary documented performance technique
- https://orm.drizzle.team/docs/dynamic-query-building -- $dynamic() method for composable query builders
- https://orm.drizzle.team/docs/rls -- Row-Level Security: withRLS, pgPolicy, Neon/Supabase integration
- https://orm.drizzle.team/docs/views -- pgView, pgMaterializedView API
- https://orm.drizzle.team/docs/data-querying -- Core select/insert/update/delete CRUD API and operators
- https://orm.drizzle.team/docs/tutorials/drizzle-with-vercel-edge-functions -- Edge-runtime driver choice, env var setup, deployment mechanics
- https://orm.drizzle.team/docs/zod -- drizzle-zod createInsertSchema/createSelectSchema/createUpdateSchema
- https://orm.drizzle.team/docs/connect-pglite -- PGlite in-memory Postgres driver, testing-relevant setup
- https://orm.drizzle.team/docs/faq -- Documented gotchas: push vs generate, index-expression limitation
- https://orm.drizzle.team/docs/connect-neon -- Neon HTTP vs WebSocket driver transaction-support tradeoff
- https://registry.npmjs.org/drizzle-orm/latest -- Authoritative npm 'latest' dist-tag version (0.45.2)
- https://github.com/drizzle-team/drizzle-orm/releases -- Official GitHub releases list, more current than docs-site release index

## ECMAScript

- https://tc39.es/ecma262/ -- Living/next-edition ECMAScript specification, currently rendering as ECMAScript 2027 draft
- https://tc39.es/ecma262/2026/ -- Ratified ECMAScript 2026, 17th edition specification snapshot
- https://tc39.es/ecma262/multipage/overview.html -- Overview clause (4) and execution-model clauses (Realms, Execution Contexts, Jobs, Agents)
- https://tc39.es/ecma262/multipage/additional-ecmascript-features-for-web-browsers.html -- Annex B, legacy web-browser-only features, normative-optional elsewhere
- https://tc39.es/ecma262/multipage/host-layering-points.html -- Host hooks / host layering points (module loading, compile-string gating, etc.)
- https://tc39.es/ -- TC39 committee overview page
- https://tc39.es/process-document/ -- The TC39 Process document defining Stage 0-4 and the yearly release timeline
- https://ecma-international.org/publications-and-standards/standards/ecma-262/ -- ECMA-262 publication and edition history page
- https://ecma-international.org/publications-and-standards/standards/ecma-402/ -- ECMA-402 Internationalization API publication page
- https://github.com/tc39/ecma262 -- Spec source repository: build process and contribution pointers
- https://github.com/tc39/proposals -- Proposals tracking repository listing stage status
- https://github.com/tc39/proposals/blob/main/finished-proposals.md -- Ledger of Stage 4 finished proposals organized by target edition year
- https://github.com/tc39/proposal-shadowrealm -- ShadowRealm proposal (Stage 2.7) for same-thread sandboxing/isolation
- https://github.com/tc39/test262 -- Test262 official ECMAScript conformance test suite README
- https://github.com/tc39/test262/blob/main/INTERPRETING.md -- Guidance for interpreting Test262 test files
- https://github.com/tc39/test262/blob/main/CONTRIBUTING.md -- Guidance for contributing new Test262 tests

## Express

- https://expressjs.com/ -- Homepage / framework overview
- https://expressjs.com/en/starter/installing.html -- Installation steps, Node.js version requirements, TypeScript setup
- https://expressjs.com/en/starter/hello-world.html -- Minimal Hello World app (CommonJS/ESM/TypeScript)
- https://expressjs.com/en/starter/generator.html -- express-generator scaffolding tool usage and options
- https://expressjs.com/en/starter/faq.html -- FAQ: app structure, database/auth being out of scope, 404 handling, template engines
- https://expressjs.com/en/guide/routing.html -- Routing guide: route methods, paths, params, wildcards, Router
- https://expressjs.com/en/guide/writing-middleware.html -- Writing middleware functions, signature, configurable middleware pattern
- https://expressjs.com/en/guide/using-middleware.html -- The five middleware categories and built-in middleware
- https://expressjs.com/en/guide/error-handling.html -- Error handling: sync/async errors, default handler, custom error middleware
- https://expressjs.com/en/guide/using-template-engines.html -- Template engine configuration and Pug example
- https://expressjs.com/en/guide/database-integration.html -- Database driver integration guidance for 12 databases
- https://expressjs.com/en/guide/behind-proxies.html -- trust proxy setting and its effects on req.ip/hostname/protocol
- https://expressjs.com/en/guide/debugging.html -- Debugging guidance: DEBUG env var, Node inspector, diagnostics_channel
- https://expressjs.com/en/guide/migrating-4.html -- Express 3-to-4 migration guide
- https://expressjs.com/en/guide/migrating-5.html -- Express 4-to-5 migration guide with full breaking-change list and codemods
- https://expressjs.com/en/5x/api.html -- Express 5.x API reference overview
- https://expressjs.com/en/5x/api/application.html -- Application object: settings table, methods, properties, events
- https://expressjs.com/en/5x/api/request.html -- Request object properties and methods
- https://expressjs.com/en/5x/api/response.html -- Response object properties and methods
- https://expressjs.com/en/5x/api/router.html -- Router object constructor, options, and methods
- https://expressjs.com/en/5x/api/express.html -- express() module and built-in middleware (json/urlencoded/raw/text/static)
- https://expressjs.com/en/advanced/best-practice-performance.html -- Official production performance best practices
- https://expressjs.com/en/advanced/best-practice-security.html -- Official production security best practices
- https://expressjs.com/en/advanced/security-updates.html -- Historical CVE/security fix log by version
- https://expressjs.com/en/advanced/healthcheck-graceful-shutdown.html -- Health checks and graceful shutdown guidance
- https://expressjs.com/en/support/ -- Official version support policy table
- https://expressjs.com/en/resources/glossary.html -- Official terminology glossary
- https://expressjs.com/en/resources/middleware.html -- Directory of first-party expressjs-org middleware modules
- https://expressjs.com/en/blog/2026-05-18-a-new-look-for-express/ -- Official blog post on the 2026 site/docs redesign (Jekyll to Astro, versioned docs, llms.txt)
- https://registry.npmjs.org/express -- npm registry metadata used only to verify current version numbers and release dates

## Fastify

- https://fastify.dev/ -- Homepage — framework description, OpenJS Foundation affiliation, homepage performance benchmark numbers
- https://fastify.dev/docs/latest/ -- Docs introduction — doc structure (Reference vs Guides), sidebar taxonomy
- https://fastify.dev/docs/latest/Guides/Getting-Started/ -- Core concepts: Fastify instance, routes, schemas, plugins, decorators, async handlers, basic server example
- https://fastify.dev/docs/latest/Reference/Server/ -- Full server factory (Fastify()) configuration options reference
- https://fastify.dev/docs/latest/Reference/Lifecycle/ -- Request/response lifecycle and hook execution order
- https://fastify.dev/docs/latest/Reference/Encapsulation/ -- Encapsulation context and plugin architecture model
- https://fastify.dev/docs/latest/Reference/Plugins/ -- register() API, fastify-plugin, skip-override symbol
- https://fastify.dev/docs/latest/Reference/Hooks/ -- Full list of application and request/reply hooks with execution order
- https://fastify.dev/docs/latest/Reference/Decorators/ -- decorate/decorateRequest/decorateReply API, reference-type restriction, sync-only design
- https://fastify.dev/docs/latest/Reference/Routes/ -- Route shorthand methods, route options object, async handler behavior
- https://fastify.dev/docs/latest/Reference/Request/ -- Request object properties and API
- https://fastify.dev/docs/latest/Reference/Reply/ -- Reply object methods and API
- https://fastify.dev/docs/latest/Reference/Errors/ -- Error handling, default error serialization, setErrorHandler, FST_ERR_VALIDATION
- https://fastify.dev/docs/latest/Reference/Warnings/ -- FSTDEP/FSTWRN deprecation and warning codes
- https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/ -- Ajv-based validation and fast-json-stringify serialization system
- https://fastify.dev/docs/latest/Reference/Middleware/ -- Express/Connect middleware interop support and limitations
- https://fastify.dev/docs/latest/Reference/TypeScript/ -- TypeScript support, type providers, generics, declaration merging
- https://fastify.dev/docs/latest/Reference/LTS/ -- Official Long Term Support policy for Fastify major versions and Node.js compatibility
- https://fastify.dev/docs/latest/Guides/Recommendations/ -- Production recommendations: reverse proxy, Kubernetes binding, capacity planning, performance tips
- https://fastify.dev/docs/latest/Guides/Testing/ -- Official testing guidance: fastify.inject(), node:test, best practices
- https://fastify.dev/docs/latest/Guides/Serverless/ -- Serverless deployment guidance: AWS Lambda, GCF, Cloud Run, Vercel
- https://fastify.dev/docs/latest/Guides/Database/ -- Official database integration patterns and first-party DB plugins
- https://fastify.dev/docs/latest/Guides/Ecosystem/ -- Catalog of official @fastify/* plugins vs community plugins
- https://fastify.dev/docs/latest/Guides/Migration-Guide-V5/ -- Official V4→V5 breaking-changes migration guide
- https://fastify.dev/docs/latest/Guides/Migration-Guide-V4/ -- Official V3→V4 migration guide (existence confirmed, not deeply reviewed)
- https://fastify.dev/docs/latest/Guides/Migration-Guide-V3/ -- Official V2→V3 migration guide (existence confirmed, not deeply reviewed)
- https://fastify.dev/docs/latest/Guides/Prototype-Poisoning/ -- Historical guide on prototype pollution vulnerability class and hapi-derived mitigation
- https://fastify.dev/docs/latest/Guides/Benchmarking/ -- Official benchmarking methodology guidance (autocannon, branch-comparer)
- https://github.com/fastify/fastify/blob/main/SECURITY.md -- Official security vulnerability reporting policy and SLA
- https://github.com/fastify/fastify/releases -- GitHub releases listing, including v6.0.0-alpha series notes
- https://github.com/fastify/fastify/issues/1952 -- Historical GitHub issue documenting fastify.dev domain background
- https://registry.npmjs.org/fastify -- npm registry metadata for the official fastify package — used as primary source for precise release dates/dist-tags

## GitHub

- https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories -- Core repository concepts and terminology
- https://docs.github.com/en/get-started/using-github/github-flow -- GitHub Flow branching workflow
- https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-merge-methods-on-github -- Merge commit, squash, and rebase merge methods
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets -- Rulesets configuration, limits, and enforcement model
- https://docs.github.com/en/enterprise-cloud@latest/admin/overview/about-github-enterprise-cloud -- GitHub Enterprise Cloud architecture, data residency
- https://docs.github.com/en/migrations/using-github-enterprise-importer/understanding-github-enterprise-importer/about-github-enterprise-importer -- GitHub Enterprise Importer migration tool and supported sources
- https://docs.github.com/en/webhooks/about-webhooks -- Webhooks overview and event-driven model
- https://docs.github.com/en/rest/about-the-rest-api/about-the-rest-api -- REST API overview
- https://docs.github.com/en/rest/about-the-rest-api/api-versions -- REST API date-based versioning scheme and support policy
- https://docs.github.com/en/rest/about-the-rest-api/breaking-changes?apiVersion=2026-03-10 -- Full list of breaking changes in REST API version 2026-03-10
- https://docs.github.com/en/graphql -- GraphQL API overview
- https://docs.github.com/en/graphql/overview/resource-limitations -- GraphQL rate limits, node limits, timeouts
- https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps -- GitHub Apps vs OAuth Apps comparison
- https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries -- Webhook HMAC signature validation
- https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/testing-webhooks -- Webhook testing/debugging workflow with smee.io
- https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api -- REST API primary and secondary rate limits
- https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api -- REST API integration best practices
- https://docs.github.com/en/authentication -- Authentication methods overview
- https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-two-factor-authentication -- 2FA requirements and methods
- https://docs.github.com/en/code-security -- Security features overview (Dependabot, code/secret scanning, advisories)
- https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization -- Organization audit log
- https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories -- Repository best practices and anti-patterns
- https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github -- File and repository size limits
- https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages -- GitHub Pages deployment model
- https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages -- GitHub Packages registry support
- https://docs.github.com/en/rest/deployments/deployments -- Deployments API
- https://docs.github.com/en/enterprise-server@latest/admin/overview/about-upgrades-to-new-releases -- GHES release cadence and upgrade policy
- https://github.blog/changelog/2026-03-12-rest-api-version-2026-03-10-is-now-available/ -- Official changelog confirming REST API version 2026-03-10 release

## GitHub Actions (CI/CD)

- https://docs.github.com/en/actions/get-started/understand-github-actions -- Core concepts: workflows, events, jobs, steps, actions, runners
- https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions -- Full workflow YAML syntax reference (on, jobs, permissions, contexts, matrix, etc.)
- https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions -- Official security hardening guide: secrets, GITHUB_TOKEN, third-party actions, pull_request_target, self-hosted runner risk
- https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners -- Self-hosted runner architecture, scopes, and responsibility model
- https://docs.github.com/en/rest/actions -- REST API for Actions: endpoint category overview
- https://docs.github.com/en/actions/sharing-automations/reusing-workflows -- Reusable workflows syntax, inputs/outputs/secrets, nesting limits
- https://docs.github.com/en/actions/concepts/overview/usage-limits-billing-and-administration -- Usage limits: job/run duration, matrix size, API rate limits, cache limits, runner registration limits
- https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect -- OIDC token issuance and cloud provider trust configuration
- https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions -- action.yml metadata syntax for JS/Docker/composite actions
- https://docs.github.com/en/actions/learn-github-actions/contexts -- Available expression contexts and their scoping restrictions
- https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows -- Dependency caching strategy, restore-keys, eviction, security restrictions
- https://docs.github.com/en/actions/using-github-hosted-runners/using-larger-runners/about-larger-runners -- Larger runners: specs, billing model, use cases
- https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments -- Deployment environments, protection rules, environment-scoped secrets
- https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments -- Deployment object/status creation and deployment triggers
- https://docs.github.com/en/actions/tutorials/migrate-to-github-actions/automated-migrations -- GitHub Actions Importer official migration tool
- https://docs.github.com/en/actions/migrating-to-github-actions/manually-migrating-to-github-actions -- Manual migration concept mapping from other CI systems
- https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/enabling-debug-logging -- ACTIONS_STEP_DEBUG debug logging guidance
- https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/re-running-workflows-and-jobs -- Re-running workflows/jobs, including with debug logging
- https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions -- Billing model: per-minute rates, included minutes by plan, storage costs
- https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/ -- Official changelog: artifact actions v3 deprecation and v4 breaking changes
- https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/ -- Official changelog: Node.js 20 deprecation timeline on GitHub-hosted runners
- https://github.blog/changelog/2022-10-11-github-actions-deprecating-save-state-and-set-output-commands/ -- Official changelog: set-output/save-state workflow command deprecation (security fix)
- https://github.blog/changelog/2026-02-05-github-actions-early-february-2026-updates/ -- Self-hosted runner minimum version enforcement (v2.329.0) timeline
- https://github.blog/changelog/2026-02-05-github-actions-self-hosted-runner-minimum-version-enforcement-extended/ -- Confirms enforcement deadline extensions occur
- https://github.blog/changelog/2026-09-03-github-actions-early-september-2026-updates/ -- New REST endpoint for runner version deprecation dates
- https://github.blog/changelog/2026-06-11-github-enterprise-server-3-21-is-now-generally-available/ -- GHES 3.21 GA date
- https://docs.github.com/en/enterprise-server@3.17/admin/all-releases -- GHES versioned release model reference
- https://github.com/actions/runner -- Official open-source Actions Runner agent repo
- https://github.com/actions/download-artifact -- Confirms download-artifact v4+ unsupported on GHES
- https://github.com/actions/toolkit -- Actions Toolkit packages for authoring/unit-testing JS actions
- https://github.com/github/local-action -- Official local debugging utility for custom JS actions

## Go

- https://go.dev/doc/devel/release -- Release history: version numbers, dates, release/support policy
- https://go.dev/doc/go1.27 -- Go 1.27 official release notes (language, stdlib, tooling, breaking changes)
- https://go.dev/doc/go1.26 -- Go 1.26 official release notes (breaking changes, Green Tea GC, new packages)
- https://go.dev/doc/effective_go -- Canonical idioms/patterns guide (naming, error handling, concurrency, interfaces)
- https://go.dev/ref/spec -- The Go Programming Language Specification
- https://go.dev/doc/ -- Documentation index listing all official doc pages
- https://go.dev/ref/mod -- Go Modules reference (go.mod, MVS, GOPROXY, go.work)
- https://go.dev/doc/modules/gomod-ref -- go.mod file directive reference
- https://go.dev/security/ -- Security overview: policy, govulncheck, vulnerability database, fuzzing
- https://go.dev/doc/diagnostics -- Official diagnostics/profiling/tracing/debugging tooling guide
- https://go.dev/doc/gc-guide -- Garbage collector guide: GOGC, GOMEMLIMIT, tuning, memory model
- https://go.dev/doc/faq -- FAQ covering language design rationale, limitations, scheduler/compiler architecture
- https://go.dev/doc/install -- Official installation instructions per platform
- https://pkg.go.dev/testing -- testing package API reference
- https://go.dev/doc/articles/race_detector.html -- Data Race Detector documentation
- https://go.dev/doc/security/fips140 -- FIPS 140-3 compliance mode documentation
- https://go.dev/doc/pgo -- Profile-Guided Optimization documentation
- https://go.dev/doc/database/sql-injection -- Official SQL injection prevention guidance for database/sql
- https://go.dev/doc/code.html -- How Go code/packages/modules are organized
- https://go.dev/blog/docker -- Official Go blog post on deploying Go servers with Docker
- https://pkg.go.dev/cmd/go -- go command reference: environment variables, subcommands
- https://go.dev/doc/go1compat -- The Go 1 compatibility promise
- https://go.dev/doc/modules/major-version -- Guidance on developing a v2+ module major version
- https://go.dev/doc/articles/go_command.html -- Design philosophy of the go command

## Google AdSense

- https://support.google.com/adsense/?hl=en -- AdSense Help Center home -- canonical publisher-facing documentation hub.
- https://developers.google.com/adsense/ -- AdSense developer documentation hub (Management API, Platforms API).
- https://developers.google.com/adsense/management -- AdSense Management API overview page.
- https://developers.google.com/adsense/management/getting_started -- Getting-started guide: OAuth2 auth flow, project registration, client libraries.
- https://developers.google.com/adsense/management/release_notes -- Full version/changelog history of the AdSense Management API from v1 through current v2 (fetched directly, dated entries through 2026-02-05).
- https://developers.google.com/adsense/management/appendix/limits -- Documented rate limits, quotas, and report size caps for the Management API.
- https://developers.google.com/adsense/platforms/reference/rest -- REST reference for the separate AdSense Platform API (v1/v1alpha), used by AdSense-for-Platforms hosting partners.
- https://developers.google.com/adsense/platforms/api/getting-started -- Getting-started guide for the AdSense-for-Platforms API.
- https://developers.google.com/adsense/platforms/direct/ad-tags -- Ad-tag pattern reference specific to AdSense for Platforms (host parameter in script tag).
- https://developers.googleblog.com/2013/07/an-async-script-for-adsense-tagging/ -- Official Google Developers blog post introducing the async adsbygoogle.js tagging pattern.
- https://support.google.com/adsense/answer/9274634?hl=en -- About the AdSense code -- what it is, where it's placed, Auto ads/ad unit distinction.
- https://support.google.com/adsense/answer/9274019?hl=en -- Get and copy the AdSense code -- exact UI steps for Auto ads and per-ad-unit code.
- https://support.google.com/adsense/answer/32713?hl=en -- Ad code overview page.
- https://support.google.com/adsense/answer/9261805?hl=en -- About Auto ads -- how placement works, ad format categories, known implementation caveats.
- https://support.google.com/adsense/answer/9261307?hl=en -- Set up Auto ads on your site -- setup steps and timing (up to an hour to appear).
- https://support.google.com/adsense/answer/9261309?hl=en -- Set up Auto ads on your AMP site.
- https://support.google.com/adsense/answer/9579782?hl=en -- Insert ad code into the AMP version of a WordPress site.
- https://support.google.com/adsense/answer/9724?hl=en -- AdSense eligibility requirements (content quality, age, policy compliance).
- https://support.google.com/adsense/answer/48182?hl=en -- AdSense Program Policies -- invalid clicks, encouraging clicks, traffic sources, ad placement rules.
- https://support.google.com/adsense/answer/9485926?hl=en -- Overview of the Policy center -- detection, review-request workflow, documented detection limitations.
- https://support.google.com/adsense/answer/1208370?hl=en -- Resources to report Program Policy violations on other sites.
- https://support.google.com/adsense/troubleshooter/6082669?hl=en -- Policy troubleshooter -- guided diagnostic tool.
- https://support.google.com/adsense/answer/1348752?hl=en -- How Google prevents invalid traffic -- detection methodology, filtration behavior.
- https://support.google.com/adsense/answer/16737?hl=en -- Definition of invalid traffic.
- https://support.google.com/adsense/answer/16906718?hl=en -- Troubleshoot ad coverage issues.
- https://support.google.com/adsense/answer/13547173?hl=en -- Ad review center overview -- inspecting and blocking served ads.
- https://support.google.com/adsense/answer/12171612?hl=en -- Ads.txt guide -- format, purpose, Google seller entry format.
- https://support.google.com/adsense/answer/7679060?hl=en -- Ensure your ads.txt files can be crawled.
- https://support.google.com/adsense/troubleshooter/9556696?hl=en -- Ads.txt troubleshooter.
- https://support.google.com/adsense/answer/13996652?hl=en -- Improvements to site management -- real-time site verification and meta tag verification, introduced 2023-09-15 (directly fetched and confirmed).
- https://support.google.com/adsense/answer/16918505?hl=en -- How the Google Consent Management Platform (CMP) works -- certified-CMP/TCF requirement for EEA/UK/Switzerland (directly fetched and confirmed).
- https://support.google.com/adsense/answer/47333?hl=en -- Enter your payments information in AdSense.
- https://support.google.com/adsense/answer/1709871?hl=en -- Payment thresholds.
- https://support.google.com/adsense/answer/1709858?hl=en -- Steps to getting paid.
- https://support.google.com/adsense/answer/157667?hl=en -- Address verification (PIN) overview -- 3-attempt limit, 4-month deadline.
- https://support.google.com/adsense/answer/9668823?hl=en -- Fix problems with AdSense address verification (PIN).
- https://support.google.com/adsense/answer/2490070?hl=en -- Submit your US tax info to Google.
- https://support.google.com/adsense/answer/10735961?hl=en -- FAQs about submitting US tax info in AdSense.
- https://support.google.com/adsense/answer/10760404?hl=en -- Optimisation tips for your site and your ads -- performance/recommended-pattern guidance.
- https://support.google.com/adsense/answer/6084409?hl=en -- Link your Google Analytics 4 property with AdSense.
- https://support.google.com/analytics/answer/9691421?hl=en -- Connect Google Ad Manager to Google Analytics (related cross-product integration).
- https://support.google.com/admob/answer/9234653?hl=en -- Google Ad Manager, AdSense, and AdMob -- product-comparison/positioning page used for migration and limitations context.

## Google SEO (Google Search Central / Google Search)

- https://developers.google.com/search/docs/essentials -- Google Search Essentials overview: technical requirements, spam policies, best practices (formerly Webmaster Guidelines).
- https://developers.google.com/search/docs/essentials/technical -- Minimum technical requirements for a page to be eligible for indexing (public access, 200 status, indexable content).
- https://developers.google.com/search/docs/essentials/spam-policies -- Full taxonomy of Google Search spam policies and enforcement mechanisms (manual actions, reconsideration, EEA-specific handling).
- https://developers.google.com/search/docs/fundamentals/how-search-works -- Official explanation of the crawling, indexing, and serving/ranking pipeline.
- https://developers.google.com/search/docs/fundamentals/seo-starter-guide -- Official SEO Starter Guide covering titles, meta descriptions, URLs, headings, images, links, structured data, promotion.
- https://developers.google.com/search/docs/crawling-indexing/robots/intro -- robots.txt introduction: directives, purpose, and its limits as a content-hiding mechanism.
- https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap -- XML sitemap format, size/URL limits, extensions, and submission methods.
- https://developers.google.com/search/docs/crawling-indexing/canonicalization -- How Google clusters duplicate content and selects a canonical URL, and which signals it weighs.
- https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics -- JavaScript SEO: crawl/render/index pipeline, routing, soft 404 handling, caching behavior.
- https://developers.google.com/search/docs/crawling-indexing/mobile/mobile-sites-mobile-first-indexing -- Mobile-first indexing best practices: content/meta-tag/structured-data parity and lazy-load guidance.
- https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data -- Structured data formats (JSON-LD/Microdata/RDFa), guidelines, and testing tools.
- https://developers.google.com/search/docs/appearance/core-web-vitals -- Core Web Vitals metrics (LCP, INP, CLS) and their relationship to search ranking.
- https://developers.google.com/search/docs/specialty/international/localized-versions -- hreflang usage for localized/multilingual page variants, including x-default.
- https://developers.google.com/search/docs/monitor-debug/security/malware -- Malware/unwanted-software policy definitions, Security Issues report, and remediation path.
- https://developers.google.com/search/apis/indexing-api/v3/using-api -- Indexing API v3 endpoints, request/response format, batching, and content-type restrictions.
- https://developers.google.com/search/apis/indexing-api/v3/prereqs -- Indexing API setup prerequisites: service account, Search Console verification, OAuth token.
- https://developers.google.com/webmaster-tools/v1/api_reference_index -- Search Console API v1 service reference (Search Analytics, Sitemaps, Sites, URL Inspection).
- https://developers.google.com/webmaster-tools/limits -- Search Console API usage/quota limits (QPS/QPM/QPD, load quotas).
- https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data -- Search Analytics API row limits and query-cost guidance.
- https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history -- Official live status dashboard listing dated ranking/core/spam algorithm updates.

## Grafana

- https://grafana.com/docs/grafana/latest/introduction/ -- core concepts, what Grafana is
- https://grafana.com/docs/grafana/latest/dashboards/ -- dashboards/panels overview
- https://grafana.com/docs/grafana/latest/dashboards/variables/ -- template variables, types
- https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/ -- dashboard JSON model, V1/V2 resource schemas
- https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/ -- dashboard design best practices / anti-patterns
- https://grafana.com/docs/grafana/latest/datasources/ -- data source model, supported types
- https://grafana.com/docs/grafana/latest/datasources/prometheus/ -- Prometheus data source integration
- https://grafana.com/docs/grafana/latest/datasources/tempo/ -- Tempo data source integration
- https://grafana.com/docs/grafana/latest/fundamentals/exemplars/ -- exemplars, metrics-to-traces linking
- https://grafana.com/docs/grafana/latest/administration/plugin-management/ -- plugin system, types, sandboxing
- https://grafana.com/docs/grafana/latest/administration/roles-and-permissions/ -- org/team roles, RBAC, data source permissions
- https://grafana.com/docs/grafana/latest/administration/data-source-management/ -- query/resource caching, data source permission tiers
- https://grafana.com/docs/grafana/latest/administration/provisioning/ -- YAML-based provisioning of dashboards/data sources
- https://grafana.com/docs/grafana/latest/administration/organization-management/ -- multi-org isolation model
- https://grafana.com/docs/grafana/latest/administration/stats-and-license/ -- admin stats/diagnostics page
- https://grafana.com/docs/grafana/latest/developers/http_api/ -- HTTP API coverage, /api → /apis deprecation
- https://grafana.com/docs/grafana/latest/as-code/ -- dashboards-as-code tooling (Terraform, Ansible, Operator, Grizzly)
- https://grafana.com/docs/grafana/latest/alerting/ -- alerting landing page
- https://grafana.com/docs/grafana/latest/alerting/fundamentals/ -- alert rules, contact points, notification policies, Prometheus alerting model
- https://grafana.com/docs/grafana/latest/alerting/fundamentals/alertmanager/ -- built-in Grafana Alertmanager vs. external Alertmanager
- https://grafana.com/docs/grafana/latest/alerting/best-practices/ -- alert fatigue, threshold tuning, ownership
- https://grafana.com/docs/grafana/latest/alerting/set-up/migrating-alerts/ -- legacy-to-unified alerting migration
- https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/ -- grafana.ini structure, env var overrides, auth provider sections
- https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/ -- Docker deployment, images, env vars, compose example
- https://grafana.com/docs/grafana/latest/setup-grafana/installation/ -- Grafana Cloud vs. self-managed, sizing/caching note
- https://grafana.com/docs/grafana/latest/setup-grafana/set-up-for-high-availability/ -- HA architecture, shared DB, alerting HA semantics
- https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-database-encryption/ -- secret encryption, envelope encryption, KMS integration
- https://grafana.com/docs/grafana/latest/upgrade-guide/ -- general upgrade guidance
- https://grafana.com/docs/grafana/latest/upgrade-guide/when-to-upgrade/ -- release cadence, support windows, recommended upgrade strategy
- https://grafana.com/docs/grafana/latest/whatsnew/ -- release notes index, current version
- https://grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v13-0/ -- v13.0 breaking changes and deprecations
- https://grafana.com/docs/release-life-cycle/ -- feature maturity lifecycle (Experimental/Preview/GA)
- https://grafana.com/docs/grafana/latest/panels-visualizations/ -- panels/visualizations section index
- https://grafana.com/docs/grafana/latest/panels-visualizations/query-transform-data/ -- Query Inspector tool
- https://grafana.com/docs/grafana/latest/troubleshooting/ -- debug logging, log locations, common issues
- https://grafana.com/docs/grafana/latest/cli/ -- Grafana CLI command reference
- https://grafana.com/security/security-advisories/ -- published CVE advisories
- https://grafana.com/grafana/plugins/grafana-sentry-datasource/ -- official Sentry data source plugin
- https://grafana.com/docs/opentelemetry/ -- OpenTelemetry support strategy, LGTM-component naming (without the acronym)
- https://grafana.com/docs/grafana-cloud/send-data/otlp/ -- OTLP ingestion into Loki/Mimir/Tempo
- https://grafana.com/docs/loki/latest/get-started/ -- Loki overview (checked for LGTM-stack terminology; not found)

## GraphQL

- https://graphql.org/learn/ -- GraphQL introduction and learning hub
- https://graphql.org/learn/schema/ -- Type system / schema reference (object, scalar, enum, interface, union, input types, non-null/list modifiers)
- https://graphql.org/learn/queries/ -- Queries, arguments, aliases, variables, fragments, directives, __typename
- https://graphql.org/learn/execution/ -- Execution model, resolvers, root fields, trivial resolvers, async/list resolution
- https://graphql.org/learn/validation/ -- Query validation rules and timing
- https://graphql.org/learn/introspection/ -- __schema/__type introspection, use cases, production considerations
- https://graphql.org/learn/subscriptions/ -- Subscriptions: transport, scaling challenges, use cases
- https://graphql.org/learn/serving-over-http/ -- HTTP transport contract: endpoints, methods, headers, status codes
- https://graphql.org/learn/best-practices/ -- Index of best-practices guides and their scope/disclaimer
- https://graphql.org/learn/authorization/ -- Authorization best practices (business-logic-layer delegation)
- https://graphql.org/learn/pagination/ -- Cursor vs offset pagination, Relay connection spec
- https://graphql.org/learn/schema-design/ -- Nullability defaults, versionless schema evolution
- https://graphql.org/learn/security/ -- Security guidance: depth/breadth limits, complexity analysis, rate limiting, HTTPS/timeouts
- https://graphql.org/learn/performance/ -- N+1 problem, DataLoader batching, persisted queries, compression
- https://graphql.org/learn/caching/ -- Global unique ID / caching best practices
- https://graphql.org/learn/global-object-identification/ -- Node interface, node root field, plural identifying root fields (Relay-based)
- https://graphql.org/learn/thinking-in-graphs/ -- Domain modeling and business-logic-layer architecture guidance
- https://graphql.org/faq/ -- GraphQL Foundation governance, REST/SQL/state-management comparisons, documented non-goals
- https://spec.graphql.org/ -- Specification edition history and current release (September 2025) plus Working Draft
- https://github.com/graphql/graphql-spec/releases -- Spec release notes summaries across editions back to July 2015
- https://github.com/graphql/graphql-spec/blob/main/changelogs/September2025.md -- Detailed September 2025 spec changelog (OneOf inputs, schema coordinates, deprecation extensions, breaking non-null changes)
- https://www.graphql-js.org/docs/ -- graphql-js reference implementation overview, module structure, v17 status
- https://www.graphql-js.org/docs/getting-started/ -- graphql-js installation and minimal server example
- https://www.graphql-js.org/docs/constructing-types/ -- Programmatic schema construction API (GraphQLObjectType, GraphQLSchema, etc.)
- https://www.graphql-js.org/docs/going-to-production/ -- graphql-js production guidance: N+1, caching, error masking, introspection, observability
- https://www.graphql-js.org/upgrade-guides/v16-v17/ -- Official graphql-js v16→v17 upgrade guide with full breaking-change list
- https://graphql.org/blog/2026-06-15-introducing-graphql-js-v17/ -- Official blog post announcing graphql-js v17 (release date, features)

## HTML

- https://html.spec.whatwg.org/multipage/introduction.html -- Core concepts, design principles, WHATWG history, conformance-class model, presentational-markup guidance
- https://html.spec.whatwg.org/multipage/dom.html -- DOM data-model architecture: Document object, element interfaces, tree structure
- https://html.spec.whatwg.org/multipage/parsing.html -- HTML parsing algorithm: tokenization, tree construction, error recovery, encoding sniffing, quirks mode
- https://html.spec.whatwg.org/multipage/obsolete.html -- Obsolete/non-conforming elements and attributes with documented replacements (anti-patterns/migration)
- https://html.spec.whatwg.org/multipage/browsers.html -- Browsing-context security model: origins, document.domain warning, sandboxing, COOP
- https://html.spec.whatwg.org/multipage/urls-and-fetching.html -- Resource loading: lazy loading, fetch priority, CORS/credentials, referrer policy, nonce
- https://html.spec.whatwg.org/multipage/webappapis.html -- Web application APIs: scripting, realms, event loop, events, atob/btoa
- https://html.spec.whatwg.org/multipage/custom-elements.html -- Custom Elements API and Web Components integration
- https://html.spec.whatwg.org/multipage/infrastructure.html -- HTML vs XHTML namespace model, SVG/MathML namespace integration
- https://html.spec.whatwg.org/multipage/syntax.html -- DOCTYPE declaration syntax and requirements
- https://html.spec.whatwg.org/multipage/semantics.html -- Meta element: charset declaration rules and constraints
- https://html.spec.whatwg.org/multipage/iana.html -- text/html and application/xhtml+xml MIME type registration and serving requirements
- https://html.spec.whatwg.org/ -- Spec index page; used to confirm last-updated date for version-currency check
- https://whatwg.org/faq -- Living Standard versioning philosophy, snapshot/Review Draft model, backward-compatibility policy, WHATWG/W3C 2019 agreement
- https://validator.w3.org/nu/about.html -- Nu Html Checker (v.Nu) documentation: what it validates, usage modes, explicit non-certification disclaimer
- https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS -- HTML-relevant XSS attack vectors and prevention guidance (sinks, encoding, sanitization, Trusted Types, CSP)
- https://developer.mozilla.org/en-US/docs/Web/API/HTML_Sanitizer_API -- HTML Sanitizer API overview
- https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Accessibility/HTML -- Semantic HTML for accessibility: recommended patterns and div-itis/ARIA-misuse anti-patterns

## Husky

- https://typicode.github.io/husky/ -- Official docs homepage — overview, feature list, 'Used by' adoption list
- https://typicode.github.io/husky/get-started.html -- Official install and getting-started guide (npm/pnpm/yarn/bun, husky init)
- https://typicode.github.io/husky/how-to.html -- Official how-to guide — hook creation, skipping hooks, CI/Docker, monorepos, non-shell hooks, version managers, manual setup
- https://typicode.github.io/husky/troubleshoot.html -- Official troubleshooting guide — hooks not running, uninstall cleanup, Yarn/Windows TTY issue
- https://typicode.github.io/husky/migrate-from-v4.html -- Official v4-to-v9 migration guide
- https://github.com/typicode/husky -- Official GitHub repository (source of truth for docs, code, releases)
- https://raw.githubusercontent.com/typicode/husky/main/index.js -- Current install-routine source code (hook list, core.hooksPath logic, security check)
- https://raw.githubusercontent.com/typicode/husky/main/husky -- Current POSIX dispatcher shell script source (HUSKY=0/2, PATH handling, error messages)
- https://raw.githubusercontent.com/typicode/husky/main/bin.js -- Current CLI entrypoint source (init, deprecated add/set/uninstall/install commands)
- https://raw.githubusercontent.com/typicode/husky/main/index.d.ts -- TypeScript type declaration for the programmatic API
- https://raw.githubusercontent.com/typicode/husky/main/package.json -- Current package.json — version 9.1.7, engines, license, dependencies
- https://api.github.com/repos/typicode/husky/releases -- GitHub Releases API — release history and dates
- https://api.github.com/repos/typicode/husky/security-advisories -- GitHub Security Advisories API — confirmed empty for this repo
- https://api.github.com/repos/typicode/husky -- GitHub repo metadata API — commit activity, open issues, archived status
- https://blog.typicode.com/posts/husky-git-hooks-javascript-config/ -- Official maintainer blog — rationale for dropping JS-config hook generation (v6 redesign)
- https://blog.typicode.com/posts/husky-git-hooks-autoinstall/ -- Official maintainer blog — rationale for removing postinstall auto-install

## Jest

- https://jestjs.io/docs/getting-started -- Core concepts, zero-config setup, globals, Babel/TypeScript integration
- https://jestjs.io/docs/architecture -- Jest's (thin) architecture doc page, links to external creator materials
- https://jestjs.io/docs/configuration -- Full jest.config.js option reference with defaults
- https://jestjs.io/docs/cli -- CLI flags reference (--coverage, --watch, --ci, --shard, --detectOpenHandles, etc.)
- https://jestjs.io/docs/expect -- expect() matcher categories and asymmetric matchers
- https://jestjs.io/docs/mock-functions -- jest.fn/jest.mock/jest.spyOn mocking API and behaviors
- https://jestjs.io/docs/timer-mocks -- Fake timers API (useFakeTimers, advanceTimersByTime, etc.)
- https://jestjs.io/docs/snapshot-testing -- Snapshot testing mechanics and documented best practices/pitfalls
- https://jestjs.io/docs/code-transformation -- Transform pipeline, babel-jest, ts-jest, custom transformers
- https://jestjs.io/docs/setup-teardown -- beforeEach/afterEach/beforeAll/afterAll hook ordering
- https://jestjs.io/docs/tutorial-async -- Testing asynchronous code: promises, async/await, resolves/rejects
- https://jestjs.io/docs/troubleshooting -- Official debugging guidance: Node inspector, Chrome DevTools, VS Code
- https://jestjs.io/docs/ecmascript-modules -- Experimental native ESM support, limitations, jest.unstable_mockModule
- https://jestjs.io/docs/migration-guide -- Migrating to Jest from Jasmine/Mocha/AVA/Chai/Sinon/etc. via jest-codemods
- https://jestjs.io/docs/upgrading-to-jest30 -- Official v29→v30 upgrade guide with full breaking-change list
- https://jestjs.io/docs/testing-frameworks -- Community integration guides for React, Vue, Angular, Next.js, NestJS, etc.
- https://jestjs.io/docs/webpack -- Mapping webpack resolve config to Jest moduleNameMapper/moduleDirectories
- https://jestjs.io/versions -- Version history / docs archive index
- https://jestjs.io/blog/2025/06/04/jest-30 -- Jest 30 release blog: features, perf benchmarks, breaking changes
- https://jestjs.io/blog/2021/05/25/jest-27 -- Jest 27 release blog: default testEnvironment/timers/runner changes
- https://github.com/jestjs/jest -- Official monorepo: packages/ directory listing and CHANGELOG.md
- https://github.com/jestjs/jest/security/policy -- Official vulnerability disclosure/security policy
- https://registry.npmjs.org/jest -- npm registry metadata: current version, publish date, engines.node

## MongoDB

- https://www.mongodb.com/docs/ -- MongoDB documentation hub / landing page, confirms canonical docs host
- https://www.mongodb.com/docs/manual/core/document/ -- Core concepts: documents, BSON, _id field, dot notation, document size limits
- https://www.mongodb.com/docs/manual/crud/ -- CRUD API surface (insert/find/update/delete operations)
- https://www.mongodb.com/docs/manual/aggregation/ -- Aggregation pipeline framework, stages, memory limits
- https://www.mongodb.com/docs/manual/core/replica-set-architectures/ -- Replica set architecture: primary/secondary/arbiter, oplog, elections, topologies
- https://www.mongodb.com/docs/manual/sharding/ -- Sharded cluster architecture: shards, config servers, mongos, shard keys, balancer
- https://www.mongodb.com/docs/manual/core/wiredtiger/ -- WiredTiger storage engine: concurrency, compression, cache, journaling, checkpoints
- https://www.mongodb.com/docs/drivers/ -- Officially supported driver languages and compatibility references
- https://www.mongodb.com/docs/drivers/client-libraries-best-practices/ -- Driver-level security best practices (SRV strings, BSON injection, server-side JS)
- https://www.mongodb.com/docs/manual/reference/configuration-options/ -- mongod/mongos YAML configuration file reference
- https://www.mongodb.com/docs/manual/security/ -- Security features overview: auth mechanisms, RBAC, encryption, auditing
- https://www.mongodb.com/docs/manual/administration/security-checklist/ -- Official production security checklist
- https://www.mongodb.com/docs/manual/applications/indexes/ -- Indexing strategy guidance (ESR rule, index selection)
- https://www.mongodb.com/docs/manual/data-modeling/design-patterns/ -- Named recommended schema design patterns
- https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/ -- Named schema anti-patterns and detection tooling
- https://www.mongodb.com/docs/manual/data-modeling/schema-validation/specify-json-schema/ -- $jsonSchema document validation
- https://www.mongodb.com/docs/manual/core/transactions/ -- Multi-document ACID transactions: API, limitations, use cases
- https://www.mongodb.com/docs/manual/tutorial/upgrade-revision/ -- Major-version upgrade procedure and FCV mechanism
- https://www.mongodb.com/docs/relational-migrator/ -- Relational Migrator tool for RDBMS-to-MongoDB migration
- https://www.mongodb.com/docs/manual/reference/versioning/ -- Versioning scheme and current release model (major/minor/patch)
- https://www.mongodb.com/legal/support-policy/lifecycles -- Official server release lifecycle / EOL date table
- https://www.mongodb.com/docs/manual/release-notes/8.0/ -- MongoDB 8.0 release notes and patch history
- https://www.mongodb.com/docs/manual/release-notes/7.0/ -- MongoDB 7.0 release notes and patch history
- https://www.mongodb.com/docs/upcoming/release-notes/8.0-compatibility/ -- Itemized MongoDB 8.0 breaking/compatibility changes
- https://www.mongodb.com/docs/manual/reference/limits/ -- Full limits and thresholds reference
- https://www.mongodb.com/docs/manual/tutorial/manage-the-database-profiler/ -- Database profiler debugging tool
- https://www.mongodb.com/docs/manual/administration/analyzing-mongodb-performance/ -- serverStatus-based performance analysis guidance
- https://www.mongodb.com/docs/manual/installation/ -- Deployment/installation options overview
- https://www.mongodb.com/docs/manual/administration/production-notes/ -- Production notes: OS, filesystem, NUMA, networking, hardware tuning
- https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-deploy-docker/ -- Official Docker-based local Atlas deployment for dev/test
- https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-for-testing/ -- Replica set deployment tutorial for testing
- https://www.mongodb.com/docs/tools-and-connectors/ -- Tools, migrators, and connectors documentation hub
- https://www.mongodb.com/docs/kafka-connector/current/ -- MongoDB Connector for Apache Kafka
- https://www.mongodb.com/products/integrations/spark-connector -- MongoDB Connector for Apache Spark
- https://www.mongodb.com/products/integrations/connectors -- General connectors landing page (BI connectors, etc.)

## Mongoose (MongoDB Object Modeling for Node.js)

- https://mongoosejs.com/ -- Homepage: what Mongoose is, current version banner
- https://mongoosejs.com/docs/guide.html -- Schemas: SchemaTypes, methods, statics, virtuals, plugins, indexes, schema options
- https://mongoosejs.com/docs/models.html -- Models: compilation from schemas, CRUD statics, change streams, Views
- https://mongoosejs.com/docs/documents.html -- Documents: change tracking, save(), non-POJO behavior, toObject/toJSON
- https://mongoosejs.com/docs/connections.html -- Connections: connect/createConnection, pooling, events, multi-tenant patterns
- https://mongoosejs.com/docs/validation.html -- Validation: built-in/custom/async validators, ValidationError, unique caveat
- https://mongoosejs.com/docs/middleware.html -- Middleware/hooks: document, query, aggregate, model middleware; pre/post
- https://mongoosejs.com/docs/populate.html -- Population: refs, options, virtual populate, refPath, limitations
- https://mongoosejs.com/docs/transactions.html -- Transactions: sessions, withTransaction, parallelism restrictions
- https://mongoosejs.com/docs/typescript.html -- TypeScript bindings, HydratedDocument, ObjectId typing, limitations
- https://mongoosejs.com/docs/deprecations.html -- Currently documented deprecation (validateSync)
- https://mongoosejs.com/docs/queries.html -- Query object semantics, thenable behavior, cursors, aggregation caveats
- https://mongoosejs.com/docs/lean.html -- (404 at this path in v9 docs — canonical is /docs/tutorials/lean.html)
- https://mongoosejs.com/docs/tutorials/lean.html -- lean() queries: performance benefits and trade-offs
- https://mongoosejs.com/docs/subdocs.html -- Subdocuments: single nested vs array, save behavior, middleware order
- https://mongoosejs.com/docs/discriminators.html -- Discriminators: schema inheritance, discriminator keys, embedded discriminators
- https://mongoosejs.com/docs/version-support.html -- Major version support status and EOL dates for Mongoose 5-9
- https://mongoosejs.com/docs/compatibility.html -- MongoDB server version compatibility matrix per Mongoose major version
- https://mongoosejs.com/docs/migrating_to_9.html -- Full 8.x→9.x breaking changes list
- https://mongoosejs.com/docs/migration.html -- Migration guide index page
- https://mongoosejs.com/docs/migrating_to_8.html -- Headline of 7.x→8.x breaking changes (not deeply fetched)
- https://mongoosejs.com/docs/migrating_to_7.html -- Headline of 6.x→7.x breaking changes (not deeply fetched)
- https://mongoosejs.com/docs/migrating_to_6.html -- Headline of 5.x→6.x breaking changes (not deeply fetched)
- https://mongoosejs.com/docs/migrating_to_5.html -- Historical 4.x→5.x Node/MongoDB version requirements
- https://mongoosejs.com/docs/faq.html -- FAQ: connection errors, gotchas, debugging signatures, ObjectId validity
- https://mongoosejs.com/docs/api/mongoose.html -- mongoose.set() global config options reference
- https://mongoosejs.com/docs/api.html -- API surface index: Mongoose, Schema, Model, Document, Query, Aggregate, etc.
- https://mongoosejs.com/docs/jest.html -- Official Jest testing caveats and recommendation to prefer Mocha
- https://mongoosejs.com/docs/nextjs.html -- Next.js integration: connection caching, Edge Runtime non-support, ESM config
- https://mongoosejs.com/docs/change-streams.html -- Change streams: replica set requirement, watch(), event vs polling patterns
- https://mongoosejs.com/docs/lambda.html -- AWS Lambda deployment: connection reuse, callbackWaitsForEmptyEventLoop
- https://mongoosejs.com/docs/plugins.html -- Plugin ecosystem: schema.plugin(), official/community plugins, registry
- https://mongoosejs.com/docs/field-level-encryption.html -- MongoDB Client-Side Field Level Encryption integration (page confirmed, detail not fully extracted)
- https://github.com/Automattic/mongoose/security/advisories/GHSA-wpg9-53fq-2r8h -- CVE-2026-42334 advisory: sanitizeFilter $nor NoSQL injection bypass, affected/patched versions
- https://raw.githubusercontent.com/Automattic/mongoose/master/CHANGELOG.md -- Raw changelog: recent 8.x/9.x patch release notes, driver version bumps, performance fixes

## MUI (Material UI)

- https://mui.com/material-ui/ -- Overview / positioning page for Material UI
- https://mui.com/material-ui/getting-started/installation/ -- Install commands, peer dependencies, styling engine setup, fonts/icons
- https://mui.com/material-ui/getting-started/versions/ -- Version history table, semver policy, release cadence
- https://mui.com/material-ui/getting-started/faq/ -- Common gotchas, anti-patterns, legacy SSR troubleshooting
- https://mui.com/material-ui/getting-started/support/ -- Support channels and LTS framing (v7 as long-term support)
- https://mui.com/material-ui/customization/theming/ -- Theme structure, ThemeProvider/createTheme, CSS variables, TS module augmentation
- https://mui.com/material-ui/customization/palette/ -- Palette tokens, contrastThreshold, tonalOffset, colorSchemes, high-contrast support
- https://mui.com/material-ui/customization/how-to-customize/ -- sx prop, styled(), theme components key, GlobalStyles customization tiers
- https://mui.com/material-ui/guides/minimizing-bundle-size/ -- Path imports vs barrel imports, icon import performance, ESLint/VSCode enforcement
- https://mui.com/material-ui/guides/testing/ -- Official testing philosophy: Testing Library, avoid snapshot tests
- https://mui.com/material-ui/guides/server-rendering/ -- Express + Emotion SSR setup pattern
- https://mui.com/material-ui/guides/content-security-policy/ -- CSP nonce and directive requirements for Emotion-based styling
- https://mui.com/material-ui/migration/upgrade-to-v7/ -- v6->v7 breaking changes and codemods
- https://mui.com/material-ui/migration/upgrade-to-v9/ -- v7->v9 breaking changes and codemods
- https://mui.com/material-ui/migration/troubleshooting/ -- v4->v5 migration troubleshooting guide
- https://mui.com/material-ui/integrations/nextjs/ -- Next.js App Router and Pages Router integration setup
- https://mui.com/material-ui/integrations/interoperability/ -- Interop with plain CSS, CSS Modules, Tailwind, styled-components, Emotion, tss-react
- https://mui.com/material-ui/api/button/ -- Example component API reference page structure (props, CSS classes, slots)
- https://mui.com/system/screen-readers/ -- visuallyHidden accessibility utility
- https://mui.com/material-ui/discover-more/changelog/ -- Changelog page (points to GitHub CHANGELOG.md as source of truth)
- https://mui.com/blog/introducing-material-ui-v9/ -- Official v9.0 release blog post: date, breaking changes, new components, perf claims
- https://mui.com/blog/mui-next-js-app-router/ -- Announcement of v5.14.0 Next.js App Router / RSC support via 'use client'
- https://mui.com/blog/mui-product-comparison/ -- MUI ecosystem architecture: Base UI, Material UI, Joy UI, MUI System, MUI X layering
- https://github.com/mui/material-ui/blob/master/SECURITY.md -- Vulnerability reporting process and supported-version security patch policy
- https://registry.npmjs.org -- npm registry API queried for @mui/material dist-tags to confirm current published version

## MySQL

- https://dev.mysql.com/doc/refman/9.7/en/manual-info.html -- Confirms manual scope/version (9.7 through 9.7.2) and points to the release-model chapter.
- https://dev.mysql.com/doc/refman/9.7/en/mysql-releases.html -- Innovation vs LTS release model, version numbering scheme, upgrade/downgrade path rules.
- https://dev.mysql.com/doc/refman/9.7/en/ -- Full table of contents / structure of the current MySQL Reference Manual.
- https://dev.mysql.com/doc/refman/9.7/en/what-is-mysql.html -- Core concepts: relational model, client/server architecture, SQL, key features.
- https://dev.mysql.com/doc/refman/9.7/en/pluggable-storage-overview.html -- Pluggable storage engine architecture, server vs storage engine layers, available engines.
- https://dev.mysql.com/doc/refman/9.7/en/security.html -- Full security chapter: authentication plugins, access control, TLS/SSL, keyring, audit logging, data masking.
- https://dev.mysql.com/doc/refman/9.7/en/server-configuration.html -- Configuration mechanisms: option files, command-line options, system variables.
- https://dev.mysql.com/doc/refman/9.7/en/connectors-apis.html -- Official connectors (J, NET, ODBC, Python, Node.js, C++) and the C API.
- https://dev.mysql.com/doc/refman/9.7/en/optimization.html -- Full optimization chapter: indexing, EXPLAIN, InnoDB tuning, buffer pool, locking, monitoring.
- https://dev.mysql.com/doc/refman/9.7/en/upgrading.html -- General upgrade guidance and TOC for the upgrade process chapter.
- https://dev.mysql.com/doc/refman/9.7/en/upgrade-paths.html -- Exact supported/unsupported version-to-version upgrade paths.
- https://dev.mysql.com/doc/refman/9.7/en/replication.html -- Replication architecture: source/replica, binary/relay logs, GTID, semisync.
- https://dev.mysql.com/doc/refman/9.7/en/group-replication.html -- Group Replication architecture, single/multi-primary mode, InnoDB Cluster relationship.
- https://dev.mysql.com/doc/refman/9.7/en/docker-mysql-getting-started.html -- Official Docker deployment guidance, image source, volume/config persistence.
- https://dev.mysql.com/doc/refman/9.7/en/error-log.html -- Error log, general/slow query log, binary log as debugging facilities.
- https://dev.mysql.com/doc/refman/9.7/en/backup-and-recovery.html -- Backup methods (mysqldump, Enterprise Backup, Shell dump/load), PITR, HA alternatives.
- https://dev.mysql.com/doc/refman/9.7/en/column-count-limit.html -- General table column count (4096) and row size (65,535 byte) limits.
- https://dev.mysql.com/doc/refman/9.7/en/innodb-limits.html -- InnoDB-specific limits: columns/indexes per table, row size, tablespace size.
- https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-0.html -- Official 8.4.0 LTS release notes: comprehensive breaking/removed/deprecated changes list.
- https://dev.mysql.com/doc/extending-mysql/9.7/en/mysql-test-suite.html -- Description of MySQL's own internal test suite (mysql-test-run.pl, mysqltest).
- https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_INTRODUCTION.html -- Introduction to the MySQL test framework used for server development.
- https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_MYSQL_TEST_RUN_PL.html -- mysql-test-run.pl reference page.
- https://blogs.oracle.com/mysql/a-more-predictable-mysql-release-model-calendar-versions-lts-and-innovation -- Official Oracle MySQL blog announcing the switch to calendar-based (YY.M.P) versioning starting with 26.7.0.
- https://blogs.oracle.com/mysql/mysql-july-2026-ga-releases-now-available -- Official Oracle MySQL blog announcing the July 2026 GA release wave (26.7.0, 9.7.2 LTS, 8.4.11 LTS).
- https://www.mysql.com/support/eol-notice.html -- Official Oracle MySQL Product Support EOL announcements page.

## Next.js

- https://nextjs.org/docs -- Docs landing page: what Next.js is, App Router vs Pages Router, docs structure, current version
- https://nextjs.org/docs/app/getting-started/installation -- Install steps, system requirements, create-next-app defaults, AGENTS.md for AI agents
- https://nextjs.org/docs/app/getting-started/server-and-client-components -- Server/Client Component model, RSC payload, hydration, composition patterns
- https://nextjs.org/docs/app/getting-started/caching -- Cache Components model: use cache, Suspense, prerendering, prefetching, ISR
- https://nextjs.org/docs/architecture -- Architecture section index: accessibility, fast refresh, compiler, browsers
- https://nextjs.org/docs/architecture/supported-browsers -- Supported browsers, Browserslist defaults, polyfill behavior
- https://nextjs.org/docs/app/api-reference -- API reference structure: directives, components, file conventions, functions, config, CLI, adapters, edge, turbopack
- https://nextjs.org/docs/app/api-reference/config/next-config-js -- Full next.config.js option index and config-file mechanics
- https://nextjs.org/docs/app/api-reference/edge -- Edge Runtime supported/unsupported APIs and caveats
- https://nextjs.org/docs/app/api-reference/components/image -- next/image component reference (performance-relevant props/behavior)
- https://nextjs.org/docs/app/guides -- Full index of ~60 official Next.js guides
- https://nextjs.org/docs/app/guides/data-security -- Data Access Layer pattern, tainting, Server Actions security, anti-patterns
- https://nextjs.org/docs/app/guides/authentication -- Auth/session/authorization patterns and list of compatible auth libraries
- https://nextjs.org/docs/app/guides/content-security-policy -- CSP nonce and SRI setup, dynamic-rendering requirement, limitations
- https://nextjs.org/docs/app/guides/testing -- Official testing tool support: Jest, Vitest, Cypress, Playwright
- https://nextjs.org/docs/app/guides/debugging -- VS Code/WebStorm/browser DevTools debugging setup and --inspect usage
- https://nextjs.org/docs/app/guides/instrumentation -- instrumentation.ts / OpenTelemetry integration convention
- https://nextjs.org/docs/app/guides/production-checklist -- Production readiness recommendations across rendering, data, security, SEO
- https://nextjs.org/docs/app/guides/static-exports -- Static export configuration and full list of unsupported features
- https://nextjs.org/docs/app/guides/migrating -- Index of official framework-migration guides (App Router, CRA, Vite)
- https://nextjs.org/docs/app/getting-started/upgrading -- Version upgrade mechanics: next upgrade CLI, canary channel, version guides
- https://nextjs.org/docs/app/guides/upgrading/version-16 -- Full Next.js 16 breaking-change and migration guide
- https://nextjs.org/docs/app/getting-started/deploying -- Deployment options: Node server, Docker, static export, verified/other adapters
- https://nextjs.org/support-policy -- Official versioning, release cadence, and Active/Maintenance LTS policy
- https://nextjs.org/blog/next-16-3 -- Next.js 16.3 release notes: new APIs, Instant Navigations, experimental features
- https://vercel.com/changelog/next-js-may-2026-security-release -- May 2026 coordinated security release: 13 advisories, affected/patched versions, CVE-2026-23870

## Node.js

- https://raw.githubusercontent.com/nodejs/Release/main/README.md -- Official release schedule and policy: LTS/Current/Maintenance definitions, cadence, backport rules
- https://nodejs.org/en/about/previous-releases -- Release schedule table, cross-checked against the GitHub Release repo
- https://nodejs.org/en/download -- Current Current (v26.8.2) and LTS (v24.21.0) version numbers
- https://nodejs.org/en/blog/announcements/evolving-the-nodejs-release-schedule -- Official announcement of the v27+ annual release-cadence change (Alpha/Current/LTS timeline)
- https://nodejs.org/en/about/security -- Security policy: vulnerability reporting via HackerOne, disclosure process, embargo timeline
- https://nodejs.org/en/blog/vulnerability/july-2026-security-releases -- Worked example security release with full CVE list across 26.x/24.x/22.x
- https://nodejs.org/en/about/governance -- Project governance: Collaborators, Technical Steering Committee, OpenJS Foundation relationship
- https://nodejs.org/en/learn/getting-started/introduction-to-nodejs -- Core concepts/architecture overview: V8, single-threaded event loop, non-blocking I/O
- https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick -- Event loop phases, process.nextTick vs setImmediate
- https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop -- Official guidance on blocking-the-event-loop anti-patterns and mitigations
- https://nodejs.org/en/learn/getting-started/security-best-practices -- Documented vulnerability classes (ReDoS, prototype pollution, timing attacks, etc.) and mitigations
- https://nodejs.org/learn/getting-started/debugging -- --inspect/--inspect-brk, Chrome DevTools/IDE integration, inspector security caveats
- https://nodejs.org/en/learn/diagnostics/flame-graphs -- CPU profiling / flame graph guidance (--perf-basic-prof, 0x)
- https://nodejs.org/en/learn/diagnostics/memory/using-heap-profiler -- Heap profiling guidance (allocation timeline vs sampling profiler)
- https://nodejs.org/api/esm.html -- ECMAScript Modules implementation and CommonJS/ESM interop
- https://nodejs.org/api/packages.html -- package.json fields (type, main, exports, imports) and conditional exports
- https://nodejs.org/api/permissions.html -- Permission Model reference: flags, restricted resources, limitations
- https://nodejs.org/api/test.html -- node:test built-in test runner API and stance
- https://nodejs.org/api/worker_threads.html -- worker_threads module
- https://nodejs.org/api/cluster.html -- cluster module: primary/worker architecture, load-distribution caveats
- https://nodejs.org/api/cli.html -- CLI flags, NODE_OPTIONS, environment variables, TypeScript flags
- https://nodejs.org/api/diagnostics_channel.html -- diagnostics_channel module
- https://nodejs.org/api/util.html -- util module
- https://nodejs.org/api/fs.html -- fs module (callback/promise/sync API styles)
- https://nodejs.org/api/stream.html -- stream module: Readable/Writable/Duplex/Transform, backpressure, Web Streams interop
- https://nodejs.org/api/http.html -- http module: server/client, Agent/keep-alive
- https://nodejs.org/api/path.html -- path module: win32/posix namespaces
- https://nodejs.org/api/process.html -- process global object: env, argv, signals, report
- https://nodejs.org/api/typescript.html -- Native TypeScript type-stripping support, flags, and limitations
- https://nodejs.org/en/blog/release/v26.0.0 -- Node.js 26.0.0 official release notes (breaking changes, Temporal API, V8/Undici bumps)
- https://raw.githubusercontent.com/nodejs/node/main/doc/changelogs/CHANGELOG_V24.md -- Node.js 24.0.0 changelog: breaking changes, semver-major commits
- https://raw.githubusercontent.com/nodejs/node/main/doc/changelogs/CHANGELOG_V22.md -- Node.js 22.0.0 changelog: breaking changes, semver-major commits
- https://docs.libuv.org/en/v1.x/threadpool.html -- libuv thread pool internals: default size, UV_THREADPOOL_SIZE, which ops use it
- https://github.com/nodejs/corepack#readme -- Corepack (npm/Yarn/pnpm bridge): purpose, bundling history, deprecation from core at v25
- https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md -- Official Docker working group best practices: multi-stage builds, non-root user, PID 1 signal handling
- https://docs.npmjs.com/cli/v11/configuring-npm/npmrc -- npm's official .npmrc configuration hierarchy (four precedence levels)
- https://docs.npmjs.com/cli/v11/commands/npm-ci -- npm ci documentation: frozen-install contract, CI/deployment use case

## Nuxt

- https://nuxt.com/docs/4.x/getting-started/introduction -- Core concepts, mission statement, key features overview
- https://nuxt.com/docs/4.x/guide/directory-structure -- Top-level project directory/file structure overview (app/, server/, public/, etc.)
- https://nuxt.com/docs/4.x/guide/directory-structure/nuxt -- .nuxt/ generated build directory behavior
- https://nuxt.com/docs/4.x/guide/directory-structure/server -- server/ directory structure: api, routes, middleware, plugins, utils
- https://nuxt.com/docs/4.x/guide/concepts/server-engine -- Nitro server engine architecture and capabilities
- https://nuxt.com/docs/4.x/guide/concepts/rendering -- Universal/client-side/hybrid rendering modes, routeRules API, edge-side rendering
- https://nuxt.com/docs/4.x/guide/concepts/auto-imports -- Auto-import system for components/composables/utils, caveats
- https://nuxt.com/docs/4.x/guide/concepts/typescript -- TypeScript integration: type-checking, project references, strict mode
- https://nuxt.com/docs/4.x/guide/concepts/nuxt-lifecycle -- Server and client application lifecycle phases and hooks
- https://nuxt.com/docs/4.x/guide/going-further/experimental-features -- Full list of experimental config flags
- https://nuxt.com/docs/4.x/guide/going-further/layers -- Nuxt Layers: extends mechanism, priority order, limitations
- https://nuxt.com/docs/4.x/guide/going-further/modules -- Nuxt module system and authoring basics
- https://nuxt.com/docs/4.x/guide/going-further/debugging -- Official debugging guidance: sourcemaps, Node inspector, VS Code/JetBrains setup
- https://nuxt.com/docs/4.x/guide/best-practices/performance -- Performance best practices and anti-patterns
- https://nuxt.com/docs/4.x/guide/best-practices/plugins -- Plugin best practices and anti-patterns
- https://nuxt.com/docs/4.x/api/nuxt-config -- nuxt.config.ts configuration reference, major option categories
- https://nuxt.com/docs/4.x/api -- API reference section overview: components, composables, utils, commands
- https://nuxt.com/docs/4.x/getting-started/data-fetching -- Data fetching composables: useFetch, useAsyncData, $fetch, lazy variants
- https://nuxt.com/docs/4.x/getting-started/state-management -- useState composable, Pinia recommendation, anti-patterns
- https://nuxt.com/docs/4.x/getting-started/error-handling -- Error handling APIs: useError, createError, showError, NuxtErrorBoundary
- https://nuxt.com/docs/4.x/getting-started/testing -- @nuxt/test-utils: unit, e2e, component mounting, mocking utilities
- https://nuxt.com/docs/4.x/getting-started/deployment -- Deployment guide: Node server, static generation, presets, production notes
- https://nuxt.com/docs/4.x/getting-started/upgrade -- Upgrade guide: nuxt upgrade command, Nuxt 3→4 breaking changes, codemods, future.compatibilityVersion
- https://nuxt.com/docs/4.x/getting-started/installation -- Prerequisites: Node.js version requirements, package managers, IDE setup
- https://nuxt.com/docs/4.x/community/roadmap -- Official release cadence policy, semver policy, version support windows
- https://nuxt.com/blog/v4 -- Nuxt 4.0 release announcement: features and breaking changes summary
- https://nuxt.com/blog/v4-5-security -- Nuxt 4.5.1/3.21.10 security patch advisory: 8 vulnerabilities with CVE/GHSA IDs, severities, remediation
- https://nuxt.com/blog/nuxt2-eol -- Nuxt 2 end-of-life announcement and version-focus policy
- https://github.com/nuxt/nuxt/releases -- Official GitHub releases page: current version numbers and release dates
- https://nuxt.com/modules/security -- nuxt-security module listing page (used to confirm community, not core-team, maintainership)

## OpenAI API

- https://developers.openai.com/api/docs/guides/text -- Responses vs. Chat Completions, message roles, `instructions` parameter, prompt-object deprecation
- https://developers.openai.com/api/docs/guides/prompt-engineering -- prompt structure framework, few-shot, model-specific guidance, agentic/coding-task practices, model pinning
- https://developers.openai.com/api/docs/models -- current model lineup, context windows, pricing, knowledge cutoffs
- https://developers.openai.com/api/docs/guides/function-calling -- tool definitions, tool_choice, parallel tool calls, strict mode, best practices
- https://developers.openai.com/api/docs/guides/structured-outputs -- JSON Schema strict mode, relationship to function calling, refusals
- https://developers.openai.com/api/docs/guides/reasoning -- reasoning models, reasoning.effort levels, when to use reasoning vs. standard models
- https://developers.openai.com/api/docs/guides/prompt-caching -- cache mechanics, breakpoints, minimum tokens, TTL, cost model, monitoring
- https://developers.openai.com/api/docs/guides/agents -- Agents SDK loop, handoffs, agents-as-tools, guardrails, approval flows, state-management strategies
- https://developers.openai.com/api/docs/guides/tools -- built-in tools overview (web search, file search, tool search, function calling)
- https://developers.openai.com/api/docs/guides/tools-code-interpreter -- Code Interpreter, container/sandbox model, file support
- https://developers.openai.com/api/docs/guides/tools-file-search -- File Search tool, vector stores, customization options
- https://developers.openai.com/api/docs/guides/tools-web-search -- Web Search tool modes, citations, domain filtering, limitations
- https://developers.openai.com/api/docs/guides/evals -- Evals API workflow, grading, deprecation status
- https://developers.openai.com/api/docs/guides/safety-best-practices -- prompt injection, moderation, human-in-the-loop, safety identifiers
- https://developers.openai.com/api/docs/guides/moderation -- Moderation API, categories, cost, inline usage
- https://developers.openai.com/api/docs/guides/rate-limits -- RPM/TPM/etc., usage tiers, 429 handling, traffic ramping
- https://developers.openai.com/api/docs/guides/error-codes -- HTTP error codes, Python SDK exception types, retry guidance
- https://developers.openai.com/api/docs/guides/streaming-responses -- SSE streaming, event types, tool-call streaming, moderation limitation
- https://developers.openai.com/api/docs/libraries -- official SDKs by language, Agents SDK, Azure OpenAI compatibility
- https://developers.openai.com/api/docs/guides/batch -- Batch API workflow, turnaround, discount, limits
- https://developers.openai.com/api/docs/guides/images-vision -- image input methods, formats, detail levels, limitations
- https://developers.openai.com/api/docs/deprecations -- deprecation policy, notice periods, terminology, recent deprecations list
- https://developers.openai.com/api/docs/guides/migrate-to-responses -- Chat Completions → Responses migration guide, code differences, common errors, ZDR pattern
- https://developers.openai.com/api/docs/guides/conversation-state -- previous_response_id, context window composition, truncation, compaction references
- https://developers.openai.com/api/docs/pricing -- per-token pricing structure, cached input, Batch/Fast-mode/regional pricing modifiers
- https://developers.openai.com/api/docs/changelog -- dated changelog entries (Assistants API shutdown, GA announcements, pricing changes)
- https://developers.openai.com/api/reference/overview -- authentication (Bearer auth, API keys, org/project headers), base URL, request-ID headers

## OpenAPI

- https://spec.openapis.org/oas/v3.2.0.html -- OpenAPI Specification v3.2.0 — current stable spec text
- https://spec.openapis.org/oas/v3.1.0.html -- OpenAPI Specification v3.1.0 text
- https://www.openapis.org/ -- OpenAPI Initiative homepage
- https://www.openapis.org/faq -- Official FAQ (found to be stale re: current version)
- https://www.openapis.org/blog/2025/09/23/announcing-openapi-v3-2 -- Official announcement blog post for 3.2.0
- https://learn.openapis.org/ -- Learn OpenAPI companion documentation site, table of contents
- https://learn.openapis.org/introduction.html -- Core concepts / introduction to OAS and OADs
- https://learn.openapis.org/specification/structure.html -- Document structure of an OpenAPI Description
- https://learn.openapis.org/specification/security.html -- Describing API Security page
- https://learn.openapis.org/best-practices.html -- Official best practices page
- https://learn.openapis.org/upgrading/v3.0-to-v3.1.html -- Official 3.0→3.1 upgrade guide with breaking changes
- https://learn.openapis.org/upgrading/v3.1-to-v3.2.html -- Official 3.1→3.2 upgrade guide, states non-breaking
- https://learn.openapis.org/referencing/overview.html -- Referencing ($ref) overview
- https://learn.openapis.org/referencing/resolve.html -- Reference resolution vs removal semantics
- https://github.com/OAI/OpenAPI-Specification/releases -- Official GitHub Releases page for the spec repo
- https://api.github.com/repos/OAI/OpenAPI-Specification/releases -- GitHub Releases API used to confirm exact publish dates/versions
- https://spec.openapis.org/overlay/v1.0.0.html -- Overlay Specification v1.0.0
- https://spec.openapis.org/arazzo/v1.0.1.html -- Arazzo Specification v1.0.1
- https://spec.openapis.org/registry/ -- OAI registries (extensions, formats, media types, tag kinds)
- https://github.com/OAI/sig-moonwalk -- Moonwalk SIG repo — future OAS 4.0 effort

## OpenSearch

- https://docs.opensearch.org/latest/ -- Canonical current-version documentation hub
- https://docs.opensearch.org/latest/about/ -- What OpenSearch is; component overview (core, Dashboards, Data Prepper, Clients)
- https://docs.opensearch.org/latest/getting-started/concepts/ -- Core concept definitions: cluster, node, index, shard, replica, document, mapping
- https://docs.opensearch.org/latest/getting-started/intro/ -- Getting-started intro covering REST/Dev Tools usage and Query DSL
- https://docs.opensearch.org/latest/api-reference/ -- REST API reference index and category listing
- https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/ -- Configuration categories index (opensearch.yml, network, security, cluster, etc.)
- https://docs.opensearch.org/latest/tuning-your-cluster/ -- Cluster tuning: node roles, thread pools, circuit breakers, workload separation
- https://opensearch.org/blog/optimize-opensearch-index-shard-size/ -- Official project blog: shard sizing recommendations and rationale
- https://docs.opensearch.org/latest/mappings/mapping-explosion/ -- Mapping explosion cause, prevention, and mitigation guidance
- https://docs.opensearch.org/latest/mappings/supported-field-types/flat-object/ -- Flat object field type as an anti-mapping-explosion pattern
- https://docs.opensearch.org/latest/mappings/ -- Mappings overview including dynamic:strict behavior
- https://docs.opensearch.org/latest/security/ -- Security plugin: authentication backends, TLS, RBAC, audit logging
- https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_security/configuration/index.md -- Raw markdown source for security configuration (demo certs, plugins.security.disabled, securityadmin)
- https://docs.opensearch.org/latest/tools/ -- Tools/integrations index: clients, Data Prepper, Logstash, k-NN, Neural Search, ML Commons, Dashboards
- https://docs.opensearch.org/latest/tools/benchmark/ -- OpenSearch Benchmark performance-testing tool
- https://docs.opensearch.org/latest/troubleshoot/ -- Troubleshooting section: Dev Tools, Query Profiler, Grok Debugger, common issue areas
- https://docs.opensearch.org/latest/install-and-configure/install-opensearch/index/ -- Installation methods index (Docker, Helm, tarball, RPM, Deb, Windows, Operator, Ansible)
- https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/ -- Docker install page (vm.max_map_count, memory requirements) — content mostly via search-indexed summary
- https://docs.opensearch.org/latest/migrate-or-upgrade/ -- Migration/upgrade index: rolling upgrades, snapshot/restore, Migration Assistant, breaking-changes pointer
- https://docs.opensearch.org/latest/sql-and-ppl/limitation/ -- SQL/PPL plugin documented limitations
- https://opensearch.org/releases/ -- Release schedule, cadence, and maintenance/support policy
- https://raw.githubusercontent.com/opensearch-project/documentation-website/main/_about/version-history.md -- Full version-history table with release dates for every 1.x/2.x/3.x release
- https://github.com/opensearch-project/OpenSearch/issues/3351 -- Official project-tracked meta-issue listing OpenSearch 3.0 breaking changes
- https://github.com/opensearch-project/opensearch-testcontainers -- Official Testcontainers module for integration testing against real OpenSearch instances

## OpenTelemetry

- https://opentelemetry.io/docs/what-is-opentelemetry/ -- core definition, three pillars, explicit backend/frontend-out-of-scope statement, CNCF/merger history
- https://opentelemetry.io/docs/concepts/components/ -- API vs. SDK vs. Collector distinction
- https://opentelemetry.io/docs/concepts/signals/traces/ -- spans, trace context, span kind/status
- https://opentelemetry.io/docs/concepts/signals/metrics/ -- metric instruments, cardinality limits
- https://opentelemetry.io/docs/concepts/signals/logs/ -- logs signal, stability-by-language, log/trace correlation
- https://opentelemetry.io/docs/concepts/context-propagation/ -- W3C Trace Context, Baggage, propagation mechanics
- https://opentelemetry.io/docs/concepts/instrumentation/ -- zero-code vs. code-based instrumentation
- https://opentelemetry.io/docs/concepts/sampling/ -- head vs. tail sampling
- https://opentelemetry.io/docs/specs/otlp/ -- OTLP protocol, transports, ports, encoding, stability
- https://opentelemetry.io/docs/specs/semconv/ -- semantic conventions overview
- https://opentelemetry.io/docs/specs/semconv/general/naming/ -- attribute naming rules
- https://opentelemetry.io/docs/specs/semconv/resource/ -- resource semantic conventions (service.name, telemetry.sdk.*)
- https://opentelemetry.io/docs/specs/otel/versioning-and-stability/ -- versioning/stability guarantees, LTS windows
- https://opentelemetry.io/docs/specs/otel/compatibility/prometheus_and_openmetrics/ -- Prometheus/OpenMetrics translation rules
- https://opentelemetry.io/docs/languages/ -- per-language, per-signal stability matrix
- https://opentelemetry.io/docs/languages/js/getting-started/nodejs/ -- Node.js SDK setup, auto-instrumentation
- https://opentelemetry.io/docs/languages/js/instrumentation/ -- manual instrumentation API, testing-gap check
- https://opentelemetry.io/docs/languages/python/getting-started/ -- Python zero-code + manual instrumentation
- https://opentelemetry.io/docs/languages/go/getting-started/ -- Go SDK bootstrap, manual instrumentation emphasis
- https://opentelemetry.io/docs/languages/sdk-configuration/general/ -- OTEL_SERVICE_NAME, OTEL_TRACES_SAMPLER, OTEL_PROPAGATORS, etc.
- https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/ -- OTLP exporter env vars (endpoint/headers/timeout/protocol)
- https://opentelemetry.io/docs/collector/ -- Collector docs site map
- https://opentelemetry.io/docs/collector/architecture/ -- receivers/processors/exporters, pipelines, agent/gateway
- https://opentelemetry.io/docs/collector/configuration/ -- Collector YAML structure, env var substitution
- https://opentelemetry.io/docs/collector/deploy/ -- deployment pattern summaries (agent/gateway/other)
- https://opentelemetry.io/docs/collector/scaling/ -- scaling guidance, metrics to monitor, Target Allocator
- https://opentelemetry.io/docs/collector/resiliency/ -- sending queues, WAL persistence, Kafka message queue
- https://opentelemetry.io/docs/collector/troubleshooting/ -- debug exporter, internal telemetry, zPages
- https://opentelemetry.io/docs/security/ -- Collector security hub page
- https://opentelemetry.io/docs/security/config-best-practices/ -- secret storage, TLS/auth, localhost-binding default
- https://opentelemetry.io/docs/security/handling-sensitive-data/ -- data minimization, redaction/attribute/filter/transform processors, hashing caveat
- https://opentelemetry.io/docs/compatibility/migration/ -- OpenTracing shim, OpenCensus bridge, Jaeger migration
- https://opentelemetry.io/ecosystem/vendors/ -- vendor/backend directory (Grafana, Sentry, Prometheus, Jaeger, Datadog, etc.)
- https://opentelemetry.io/blog/2026/go-logs-api-sdk-rc/ -- Go Logs API/SDK release-candidate announcement
- https://github.com/open-telemetry -- organization page, multi-repo structure
- https://github.com/open-telemetry/opentelemetry-specification/releases -- spec release history
- https://github.com/open-telemetry/opentelemetry-collector/releases -- Collector core release history
- https://raw.githubusercontent.com/open-telemetry/opentelemetry-js/main/CHANGELOG.md -- JS SDK v2.0.0 breaking-change inventory
- https://github.com/open-telemetry/opentelemetry-js/releases -- JS SDK release history
- https://github.com/open-telemetry/opentelemetry-python/releases -- Python SDK release history
- https://github.com/open-telemetry/opentelemetry-go/releases -- Go SDK release history

## OWASP Top 10 for LLM Applications

- https://genai.owasp.org/ -- GenAI Security Project mission and outputs index
- https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ -- 2026 edition resource page, publish date, download
- https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/ -- 2025 edition resource page, project history, methodology
- https://genai.owasp.org/2026/09/01/owasp-genai-security-project-unveils-2026-top-10-for-llm-applications-new-agent-control-standard-and-sponsors-as-community-tops-30000-members/ -- 2026 announcement: rank changes, ACS, community stats
- https://genai.owasp.org/resource/owasp-genai-security-project-solutions-reference-guide-q2_q325/ -- Solutions Reference Guide description, publish date
- https://genai.owasp.org/resource/agent-control-standard-acs/ -- Agent Control Standard description, publish date
- https://genai.owasp.org/2025/01/22/announcing-the-owasp-gen-ai-red-teaming-guide/ -- Gen AI Red Teaming Guide announcement
- https://github.com/OWASP/www-project-top-10-for-large-language-model-applications -- legacy-archive notice, pointer to canonical repo
- https://github.com/GenAI-Security-Project/GenAI-LLM-Top10 -- canonical source repository structure, license
- https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/blob/main/OWASP%20Top%2010%20for%20LLM%20Applications%20Charter.md -- project charter: mission, governance, scope boundaries
- https://api.github.com/repos/GenAI-Security-Project/GenAI-LLM-Top10/contents/2026/final -- 2026 file listing (confirms canonical 10-item order)
- https://api.github.com/repos/GenAI-Security-Project/GenAI-LLM-Top10/contents/2025 -- 2025 file listing (confirms 2025 order)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM00_Preface.md -- 2026 preface: methodology, Agentic Top 10 boundary
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM01_PromptInjection.md -- Prompt Injection (2026)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM02_SensitiveInformationDisclosure.md -- Sensitive Information Disclosure (2026)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM03_ExcessiveAgency.md -- Excessive Agency (2026)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM04_SupplyChain.md -- Supply Chain (2026)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM05_DataModelPoisoning.md -- Data and Model Poisoning (2026)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM06_UnboundedConsumption.md -- Unbounded Consumption (2026)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM07_Misinformation.md -- Misinformation (2026)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM08_HiddenContextExposure.md -- Hidden Context Exposure (2026, renamed from System Prompt Leakage)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM09_VectorAndEmbeddingWeaknesses.md -- Vector and Embedding Weaknesses (2026)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLM10_ImproperOutputHandling.md -- Improper Output Handling (2026)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/Appendix_A_Related_Framework_Mappings.md -- cross-walk to nine external frameworks
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/Appendix_B_LLM_Application_Architecture_and_Threat_Modeling.md -- architecture/trust-boundary diagram (caption/alt-text only)
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/LLMZZ_Appendix_AISVS_Mapping.md -- AISVS relationship and mapping
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2026/final/references.md -- consolidated references, CWE/framework citations
- https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/2025/LLM00_Preface.md -- 2025 preface: history, methodology

## Playwright

- https://playwright.dev/docs/intro -- Overview, core concepts, system requirements (Node/OS support)
- https://playwright.dev/docs/release-notes -- Version history, breaking changes, latest features per release
- https://playwright.dev/docs/library -- Library API architecture: Browser/BrowserContext/Page hierarchy vs Test runner
- https://playwright.dev/docs/locators -- Locators concept, strict mode, recommended getBy* methods, Shadow DOM behavior
- https://playwright.dev/docs/actionability -- Auto-waiting/actionability checks before actions
- https://playwright.dev/docs/network -- Network interception/mocking, route/fulfill, HAR replay
- https://playwright.dev/docs/pom -- Page Object Model guidance
- https://playwright.dev/docs/best-practices -- Recommended patterns and anti-patterns
- https://playwright.dev/docs/ci -- CI setup, worker/sharding guidance, env vars, caching guidance
- https://playwright.dev/docs/docker -- Docker images, tags, security hardening, remote Playwright Server
- https://playwright.dev/docs/test-configuration -- playwright.config options
- https://playwright.dev/docs/api/class-testconfig -- TestConfig property reference (workers, timeout, retryStrategy, shard, maxFailures)
- https://playwright.dev/docs/auth -- Authentication/storageState patterns and security warning on state files
- https://playwright.dev/docs/test-parallel -- Worker/parallelism/sharding architecture
- https://playwright.dev/docs/test-typescript -- TypeScript support and tsconfig option restrictions
- https://playwright.dev/docs/browsers -- Supported browsers, release channels, binary management
- https://playwright.dev/docs/test-fixtures -- Fixture system: built-in, custom, worker vs test scope, auto fixtures
- https://playwright.dev/docs/test-components -- Component testing status, supported frameworks, limitations
- https://playwright.dev/docs/api-testing -- APIRequestContext for pure API testing
- https://playwright.dev/docs/debug -- Debugging tools: VS Code extension, Inspector, DevTools, DEBUG env vars
- https://playwright.dev/docs/trace-viewer-intro -- Trace Viewer debugging tool overview
- https://playwright.dev/docs/getting-started-vscode -- VS Code extension feature set
- https://playwright.dev/docs/puppeteer -- Official Puppeteer-to-Playwright migration guide
- https://playwright.dev/docs/protractor -- Official Protractor-to-Playwright migration guide
- https://playwright.dev/docs/test-reporters -- Built-in and third-party reporters
- https://playwright.dev/docs/test-snapshots -- Visual regression/screenshot testing, cross-platform caveats
- https://playwright.dev/docs/videos -- Video recording configuration
- https://playwright.dev/docs/emulation -- Device/geolocation/locale/timezone emulation options
- https://playwright.dev/docs/frames -- Iframe handling via frameLocator/Frame objects
- https://playwright.dev/mcp/introduction -- Official Playwright MCP server overview, architecture, tools
- https://github.com/microsoft/playwright/releases -- GitHub release tags (date accuracy unresolved)

## PostgreSQL

- https://www.postgresql.org/docs/current/release.html -- Release notes index / confirms current doc-versioning scheme
- https://www.postgresql.org/docs/current/release-18.html -- PostgreSQL 18 feature summary and breaking-change list
- https://www.postgresql.org/about/news/postgresql-18-released-3142/ -- PG18 GA announcement, incl. AIO performance claim
- https://www.postgresql.org/about/news/postgresql-186-1711-1615-1519-1424-and-19-beta-3-released-3365/ -- Aug 2026 combined minor-release + PG19 Beta 3 announcement
- https://www.postgresql.org/support/versioning/ -- Official versioning/support-window policy and current supported-version table
- https://www.postgresql.org/docs/current/tutorial-arch.html -- Client/server, process-per-connection architecture
- https://www.postgresql.org/docs/current/overview.html -- Internals overview chapter (query processing path) framing
- https://www.postgresql.org/docs/current/runtime-config.html -- Configuration file structure and how to set parameters
- https://www.postgresql.org/docs/current/wal-intro.html -- Write-ahead logging concept and rationale
- https://www.postgresql.org/docs/current/mvcc-intro.html -- MVCC concurrency control model
- https://www.postgresql.org/docs/current/transaction-iso.html -- Transaction isolation levels and PostgreSQL's implementation
- https://www.postgresql.org/docs/current/limits.html -- Documented hard limits (table size, columns, identifiers, etc.)
- https://www.postgresql.org/docs/current/auth-methods.html -- Authentication method catalog
- https://www.postgresql.org/docs/current/ssl-tcp.html -- TLS/SSL server configuration
- https://www.postgresql.org/docs/current/using-explain.html -- EXPLAIN / EXPLAIN ANALYZE usage for performance debugging
- https://www.postgresql.org/docs/current/routine-vacuuming.html -- VACUUM / autovacuum rationale and recommended practice
- https://www.postgresql.org/docs/current/ddl-rowsecurity.html -- Row-level security (RLS) policies
- https://www.postgresql.org/docs/current/app-pgdump.html -- pg_dump / pg_restore usage and backup guidance
- https://www.postgresql.org/docs/current/pgupgrade.html -- pg_upgrade process, modes, and limitations
- https://www.postgresql.org/docs/current/high-availability.html -- Replication / HA topologies and trade-offs
- https://www.postgresql.org/docs/current/external-interfaces.html -- Scope of officially-maintained client interfaces (libpq, ECPG)
- https://www.postgresql.org/docs/current/regress.html -- PostgreSQL's own internal regression-test framework
- https://www.postgresql.org/docs/current/indexes-types.html -- Index type catalog and use cases
- https://www.postgresql.org/docs/current/user-manag.html -- Roles and privilege model
- https://www.postgresql.org/docs/current/extend-extensions.html -- Extension packaging and CREATE EXTENSION mechanism
- https://www.postgresql.org/docs/current/runtime-config-logging.html -- Logging configuration parameters for debugging
- https://www.postgresql.org/docs/current/populate.html -- Bulk-load performance recommendations
- https://www.postgresql.org/docs/current/monitoring-stats.html -- Cumulative statistics views (pg_stat_*, pg_statio_*)
- https://www.postgresql.org/docs/current/fdwhandler.html -- Foreign Data Wrapper API for external data source integration
- https://www.postgresql.org/docs/current/installation.html -- Source-build installation chapter scope
- https://www.postgresql.org/docs/current/protocol.html -- Frontend/backend wire protocol as documented API surface
- https://www.postgresql.org/docs/current/datatype.html -- Built-in data type catalog

## Prisma

- https://www.prisma.io/docs/orm -- Canonical Prisma 8 (pre-GA) overview: contract-based architecture, three-step workflow, SPI-based extensible core
- https://www.prisma.io/docs/orm/v7/overview/introduction/what-is-prisma -- Prisma 7 (current stable) core concepts: schema, client, migrate
- https://www.prisma.io/docs/orm/v7/more/best-practices -- v7 official best practices: naming, indexing, connection pooling, security, anti-patterns
- https://www.prisma.io/docs/orm/reference/orm-client -- Prisma 8 ORM Client API reference: composable query DSL, terminals, mutation methods
- https://www.prisma.io/docs/cli -- Unified Prisma 8 CLI command reference
- https://www.prisma.io/docs/getting-started -- Prisma 8 getting-started / installation / init workflow
- https://www.prisma.io/changelog -- Official changelog, version history and dated release entries
- https://www.prisma.io/changelog.md -- Machine-readable changelog (same content as /changelog)
- https://github.com/prisma/orm/releases -- Authoritative release list with prerelease flags, used to confirm v8 is still RC not GA
- https://www.prisma.io/blog/the-next-evolution-of-prisma-orm -- Official announcement blog for the Prisma 8/Prisma Next rewrite, EA status, v7 production guidance, MongoDB roadmap
- https://www.prisma.io/blog/from-rust-to-typescript-a-new-chapter-for-prisma-orm -- Official blog explaining the Rust-to-TypeScript query engine architecture shift (v7 default)
- https://www.prisma.io/docs/orm/v6/prisma-client/setup-and-configuration/no-rust-engine -- v6-era docs showing Rust-free engine was Preview/opt-in before becoming v7 default
- https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7 -- Official v6→v7 upgrade guide: full breaking-changes list
- https://www.prisma.io/docs/orm/v7/reference/prisma-config-reference -- prisma.config.ts reference documentation
- https://www.prisma.io/docs/orm/v7/reference/system-requirements -- Node.js/TypeScript/OS system requirements per version
- https://www.prisma.io/docs/orm/v7/reference/supported-databases -- Full supported-database matrix with GA/Preview status
- https://www.prisma.io/docs/orm/v7/prisma-migrate/understanding-prisma-migrate/limitations-and-known-issues -- Documented Prisma Migrate limitations: provider portability, data loss on reset, PgBouncer, non-interactive envs
- https://www.prisma.io/docs/orm/v7/more/releases -- Release cadence, maturity levels (EA/Preview/GA), SemVer policy
- https://www.prisma.io/docs/orm/prisma-client/testing/unit-testing -- v7 unit testing guide: singleton/DI mocking patterns, jest-mock-extended
- https://www.prisma.io/docs/orm/prisma-client/testing/integration-testing -- Integration testing guidance (real DB, no mocking)
- https://www.prisma.io/docs/orm/prisma-client/deployment/deploy-prisma -- v7 deployment guide: traditional/serverless/edge paradigms and gotchas
- https://www.prisma.io/docs/orm/prisma-migrate/workflows/development-and-production -- migrate dev vs migrate deploy production workflow rules
- https://www.prisma.io/docs/orm/prisma-client/observability-and-logging/logging -- PrismaClient log level configuration
- https://www.prisma.io/docs/orm/prisma-client/debugging-and-troubleshooting/debugging -- DEBUG env var namespaces for troubleshooting
- https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/error-formatting -- Error formatting behavior, prod vs dev output
- https://www.prisma.io/docs/orm/reference/error-reference -- Prisma 8 error code reference
- https://www.prisma.io/docs/orm/prisma-client/client-extensions -- Client Extensions ($extends) API: model/client/query/result components
- https://www.prisma.io/docs/orm/prisma-client/queries/query-optimization-performance -- Query performance guidance: batching, relationLoadStrategy, common slow-query causes
- https://www.prisma.io/docs/orm/v7/prisma-client/setup-and-configuration/databases-connections/pgbouncer -- PgBouncer integration requirements (Transaction mode)
- https://www.prisma.io/docs/guides/frameworks/nextjs -- Official Next.js framework integration guide (current docs tree)
- https://www.prisma.io/docs/guides/frameworks/sveltekit -- Official SvelteKit framework integration guide
- https://www.prisma.io/docs/guides/frameworks/nuxt -- Official Nuxt framework integration guide
- https://www.prisma.io/docs/guides/frameworks/hono -- Official Hono/Cloudflare Workers edge integration guide
- https://www.prisma.io/docs/guides/v7/frameworks/nestjs -- v7-pinned NestJS integration guide
- https://www.prisma.io/docs/guides/integrations/neon-accelerate -- Neon + Prisma Accelerate integration guide
- https://www.prisma.io/docs/ai/tools/mcp-server -- Official Prisma MCP server docs: capabilities, supported AI clients, safety guardrails
- https://www.prisma.io/docs/llms.txt -- Official machine-readable documentation index used to map the current docs tree

## Prometheus

- https://prometheus.io/docs/introduction/overview/ -- core concepts, architecture, ecosystem components
- https://prometheus.io/docs/introduction/comparison/ -- pull-vs-push framing, architecture-independence stance vs. Graphite/InfluxDB/OpenTSDB/Nagios/Sensu
- https://prometheus.io/docs/introduction/faq/ -- pull-vs-push rationale, HA answer, scaling claims, logs-vs-metrics scoping, stability/semver policy
- https://prometheus.io/docs/introduction/release-cycle/ -- LTS policy, release cadence, LTS release table
- https://prometheus.io/docs/concepts/data_model/ -- time series/label data model, metric naming rules
- https://prometheus.io/docs/concepts/metric_types/ -- Counter/Gauge/Histogram/Summary, native vs. classic histograms
- https://prometheus.io/docs/concepts/jobs_instances/ -- job/instance model, auto-generated scrape metrics
- https://prometheus.io/docs/prometheus/latest/getting_started/ -- hello-world config, reload/shutdown signals
- https://prometheus.io/docs/prometheus/latest/configuration/configuration/ -- prometheus.yml structure, scrape_config, relabeling, remote_write, alertmanager_config, http_config
- https://prometheus.io/docs/prometheus/latest/configuration/https/ -- --web.config.file, TLS/basic-auth server config
- https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/ -- rule file/group syntax, promtool check rules
- https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/ -- for/keep_firing_for, templating
- https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/ -- promtool test rules format
- https://prometheus.io/docs/prometheus/latest/feature_flags/ -- experimental feature flag catalog
- https://prometheus.io/docs/prometheus/latest/federation/ -- /federate endpoint, hierarchical/cross-service federation
- https://prometheus.io/docs/prometheus/latest/http_sd/ -- HTTP service discovery contract
- https://prometheus.io/docs/prometheus/latest/management_api/ -- /-/healthy, /-/ready, /-/reload, /-/quit
- https://prometheus.io/docs/prometheus/latest/migration/ -- Prometheus 3.0 migration guide
- https://prometheus.io/docs/prometheus/latest/prometheus_agent/ -- Agent mode
- https://prometheus.io/docs/prometheus/latest/querying/basics/ -- PromQL selectors, modifiers, duration expressions, staleness
- https://prometheus.io/docs/prometheus/latest/querying/api/ -- HTTP API, OpenAPI spec, instant/range query params, remote read scalability
- https://prometheus.io/docs/prometheus/latest/stability/ -- API stability guarantees (stable vs. unstable surfaces for 3.x)
- https://prometheus.io/docs/prometheus/latest/storage/ -- local TSDB layout/compaction/retention, remote storage overview, backfilling
- https://prometheus.io/docs/prometheus/latest/command-line/prometheus/ -- server CLI flags (storage, web, query, rules)
- https://prometheus.io/docs/prometheus/latest/command-line/promtool/ -- promtool subcommands (check, test, tsdb, debug, query)
- https://prometheus.io/docs/alerting/latest/overview/ -- two-part alerting pipeline
- https://prometheus.io/docs/alerting/latest/high_availability/ -- Alertmanager gossip cluster design, fail-open, operational flags
- https://prometheus.io/docs/practices/naming/ -- metric/label naming conventions, high-cardinality-label caution, base units
- https://prometheus.io/docs/practices/rules/ -- recording-rule naming/aggregation conventions
- https://prometheus.io/docs/practices/alerting/ -- alerting philosophy and symptom-based design
- https://prometheus.io/docs/practices/remote_write/ -- remote-write queue architecture and tuning parameters
- https://prometheus.io/docs/instrumenting/exposition_formats/ -- Prometheus text exposition format
- https://prometheus.io/docs/instrumenting/pushing/ -- Pushgateway rationale
- https://prometheus.io/docs/operating/security/ -- security model, threat model, TLS/basic-auth, CSRF/CORS, disclosure policy
- https://prometheus.io/docs/operating/integrations/ -- remote storage integrations list (Thanos, Cortex, Grafana Mimir, etc.)
- https://prometheus.io/docs/visualization/grafana/ -- Grafana data source setup and integration detail
- https://prometheus.io/docs/guides/opentelemetry/ -- OTLP receiver configuration, target_info, translation strategies, delta handling
- https://raw.githubusercontent.com/prometheus/prometheus/main/CHANGELOG.md -- version/release-date confirmation, 3.0.0 and 3.14.0 change entries (project-maintained changelog, mirrored to GitHub)
- https://prometheus.io/sitemap.xml -- doc-tree version confirmation (3.14/3.13/3.5 version trees alongside `latest`)

## Python

- https://docs.python.org/3/ -- Documentation landing page; confirms doc host stability, current stable version, overall doc structure
- https://docs.python.org/3/reference/datamodel.html -- Language reference: object model, types/identity/value, special methods, descriptors
- https://docs.python.org/3/reference/import.html -- Import system architecture: finders, loaders, sys.modules cache, __pycache__
- https://docs.python.org/3/library/index.html -- Standard library index, the primary first-party API surface
- https://docs.python.org/3/library/exceptions.html -- Built-in exception hierarchy and exception chaining (raise ... from)
- https://docs.python.org/3/library/unittest.html -- unittest testing framework: TestCase, fixtures, discovery, assertions
- https://docs.python.org/3/library/doctest.html -- doctest module for docstring-embedded tests
- https://docs.python.org/3/library/pdb.html -- pdb interactive debugger, including 3.14 remote-attach (-p PID)
- https://docs.python.org/3/library/profile.html -- cProfile/profile deterministic performance profilers and pstats
- https://docs.python.org/3/library/typing.html -- typing module: type hints, generics, Protocol, TypedDict, PEP 695 syntax
- https://docs.python.org/3/library/asyncio.html -- asyncio event-loop/coroutine concurrency framework
- https://docs.python.org/3/library/venv.html -- venv virtual environment module: creation, activation, isolation semantics
- https://docs.python.org/3/library/2to3.html -- 2to3 tool reference page (fetch was inconclusive on current deprecation notice text)
- https://docs.python.org/3/library/security_warnings.html -- Consolidated security-considerations reference across pickle, ssl, subprocess, random, hashlib, etc.
- https://docs.python.org/3/library/sys.html#sys.setrecursionlimit -- Recursion limit documentation (stack-overflow protection)
- https://docs.python.org/3/library/logging.html -- logging module: thread-safety, shutdown, production configuration notes
- https://docs.python.org/3/using/cmdline.html -- CLI flags and PYTHON* environment variables for configuration/hardening
- https://docs.python.org/3/using/unix.html -- Official Unix installation/build-from-source guidance (make altinstall warning)
- https://docs.python.org/3/extending/extending.html -- C/C++ extension module authoring and embedding, Limited API/stable ABI
- https://docs.python.org/3/howto/free-threading-python.html -- Free-threaded (no-GIL) CPython HOWTO: enabling, performance, limitations
- https://docs.python.org/3/howto/perf_profiling.html -- Linux perf profiler integration HOWTO (3.12+)
- https://docs.python.org/3/howto/pyporting.html -- Python 2-to-3 porting HOWTO, noted as discontinued as of 3.11
- https://docs.python.org/3/howto/doanddont.html -- Idioms/anti-idioms HOWTO; fetch inconclusive on whether still present in current docs
- https://docs.python.org/3/glossary.html -- Glossary: GIL, EAFP/LBYL, CPython definitions
- https://docs.python.org/3/deprecations/index.html -- Forward-looking pending-removal index by target version
- https://docs.python.org/3/whatsnew/3.12.html -- Python 3.12 release notes: distutils removal, PEP 695/701/709/684/688/669
- https://docs.python.org/3/whatsnew/3.13.html -- Python 3.13 release notes: free-threading, JIT, 2to3 removal, new REPL
- https://docs.python.org/3/whatsnew/3.14.html -- Python 3.14 release notes: template strings, subinterpreters, GC revert, breaking changes
- https://docs.python.org/3/faq/design.html -- Design FAQ (goto, threading model discussion)
- https://devguide.python.org/versions/ -- Official CPython version-support table and PEP 602 release-cadence phase descriptions
- https://peps.python.org/pep-0703/ -- PEP 703: Making the GIL Optional — acceptance status and rationale
- https://peps.python.org/pep-0602/ -- PEP 602: Annual Release Cycle for Python
- https://peps.python.org/pep-2026/ -- PEP 2026: Calendar versioning for Python — rejected proposal
- https://peps.python.org/pep-0008/ -- PEP 8: Style Guide for Python Code
- https://packaging.python.org/en/latest/tutorials/packaging-projects/ -- PyPA packaging tutorial: pyproject.toml, build backends, build/twine workflow

## React

- https://react.dev/versions -- Version archiving policy and canonical docs host confirmation
- https://react.dev/learn -- Core concepts overview (components, JSX, props, state, hooks)
- https://react.dev/learn/thinking-in-react -- Official five-step architectural methodology
- https://react.dev/learn/render-and-commit -- Render/commit lifecycle (trigger, render, commit phases)
- https://react.dev/learn/preserving-and-resetting-state -- Reconciliation model: state tied to tree position, keys
- https://react.dev/reference/rsc/server-components -- React Server Components architecture, client/server boundary, semver caveats
- https://react.dev/reference/react -- Top-level API reference structure/index
- https://react.dev/reference/rules -- Rules of React (purity, hooks rules)
- https://react.dev/learn/you-might-not-need-an-effect -- Canonical useEffect anti-pattern catalog
- https://react.dev/reference/react-dom/components/common -- dangerouslySetInnerHTML XSS security guidance
- https://react.dev/reference/react/StrictMode -- StrictMode dev-only checks and debugging role
- https://react.dev/learn/start-a-new-react-project -- Officially recommended frameworks and deployment paths
- https://react.dev/learn/installation -- Project setup/configuration options
- https://react.dev/community/versioning-policy -- Semver policy, release channels (Latest/Canary/Experimental)
- https://react.dev/blog/2024/12/05/react-19 -- React 19 release notes: new APIs, features, deprecations
- https://react.dev/blog/2025/10/01/react-19-2 -- React 19.2 release notes: Activity, useEffectEvent, partial prerendering
- https://react.dev/blog/2024/04/25/react-19-upgrade-guide -- Full React 19 breaking-change and migration guide
- https://react.dev/learn/react-developer-tools -- Official debugging tool (React DevTools) install/usage
- https://react.dev/learn/typescript -- Official TypeScript integration guide
- https://react.dev/reference/react-compiler -- React Compiler overview
- https://react.dev/blog/2025/10/07/react-compiler-1 -- React Compiler v1.0 stable release, config, performance results
- https://react.dev/reference/react/Suspense -- Suspense documented limitations and performance batching behavior
- https://react.dev/reference/react/memo -- memo performance guidance, shallow-equality limitations
- https://react.dev/reference/react/useMemo -- useMemo guidance, caveats, non-guarantee semantics
- https://react.dev/reference/react/Component -- Error boundary implementation, class-component-only limitation
- https://react.dev/reference/react/act -- act() testing helper reference
- https://react.dev/warnings/react-dom-test-utils -- Deprecation of react-dom/test-utils in favor of Testing Library
- https://react.dev/warnings/react-test-renderer -- Deprecation of react-test-renderer
- https://react.dev/errors -- Minified production error decoder
- https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components -- Critical RCE vulnerability (CVE-2025-55182) in RSC, affected/fixed versions
- https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components -- Follow-up RSC vulnerabilities disclosure, incomplete initial patch
- https://react.dev/blog/2026/02/24/the-react-foundation -- React Foundation governance transition to Linux Foundation
- https://react.dev/blog/2025/02/14/sunsetting-create-react-app -- Official deprecation of Create React App
- https://registry.npmjs.org -- npm dist-tags for react package confirming current version numbers (queried via npm CLI)

## Redis

- https://redis.io/docs/latest/get-started/ -- Redis Open Source overview, use cases, deployment options, integration hub links
- https://redis.io/docs/latest/develop/data-types/ -- Full catalog of Redis data types (strings, hashes, JSON, streams, vector sets, probabilistic types, etc.)
- https://redis.io/docs/latest/operate/oss_and_stack/management/replication/ -- Master-replica replication architecture, PSYNC, diskless replication, writable-replica caveats
- https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/ -- Redis Cluster architecture: hash slots, cluster bus, consistency guarantees, cluster creation/upgrade/migration
- https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/ -- Redis Sentinel high-availability overview (partially captured — output exceeded size limit)
- https://redis.io/docs/latest/operate/oss_and_stack/management/security/ -- Security model, network security, protected mode, authentication, TLS, attack-surface notes
- https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/ -- Full ACL system: rules, categories, selectors, key permissions, password storage, Sentinel/replica ACL requirements
- https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/ -- RDB vs AOF persistence, multi-part AOF, backup procedures, new BACKUP command family (8.10+)
- https://redis.io/docs/latest/develop/reference/clients/ -- Client connection handling: limits, buffers, client eviction, timeouts, CLIENT command
- https://redis.io/docs/latest/develop/reference/eviction/ -- maxmemory, eviction policies (LRU/LFU/LRM/random/TTL), INFO-based cache diagnostics
- https://redis.io/docs/latest/develop/using-commands/transactions/ -- MULTI/EXEC/DISCARD/WATCH transaction semantics, error handling, no-rollback design
- https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/ -- Built-in latency monitoring subsystem, single-threaded architecture note
- https://redis.io/docs/latest/develop/reference/protocol-spec/ -- Full RESP2/RESP3 protocol specification, version history, data type encodings
- https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/ -- Official Docker deployment instructions
- https://redis.io/docs/latest/develop/clients/ -- Official client library catalog across nine languages plus OM libraries
- https://redis.io/docs/latest/develop/programmability/ -- Lua scripting and Redis Functions programmability model
- https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.0-release-notes/ -- Redis 8.0 release notes: breaking ACL changes, licensing, module consolidation, patch history through Feb 2026
- https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/ -- Official first-party tutorial cataloging 11 documented Redis anti-patterns with severity ratings
- https://redis.io/docs/latest/operate/kubernetes/ -- Redis Enterprise operator for Kubernetes deployment documentation
- https://redis.io/docs/latest/develop/tools/cli/ -- redis-cli full feature set: debugging modes, big-key/mem-key scanning, latency tools, Lua debugger
- https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/ -- redis-benchmark tool usage and documented performance-affecting factors
- https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/ -- Official version numbering scheme, release-type policy, and live supported-versions/EOL table
- https://redis.io/docs/latest/operate/oss_and_stack/install/upgrade/standalone/ -- Official standalone upgrade-to-Redis-8 procedure
- https://redis.io/docs/latest/develop/using-commands/pipelining/ -- Pipelining mechanics, RTT reduction, throughput benchmarks
- https://raw.githubusercontent.com/redis/redis/unstable/00-RELEASENOTES -- Redis GitHub repo release-notes file confirming 8.10-RC1/RC2 tag dates

## Sass

- https://sass-lang.com/documentation/ -- Main documentation site, structure/TOC, and reference version target (Dart Sass 1.104.0)
- https://sass-lang.com/documentation/syntax/ -- SCSS vs indented syntax explanation
- https://sass-lang.com/documentation/values/ -- SassScript data types (numbers, strings, colors, lists, maps, booleans, null, calculations, functions)
- https://sass-lang.com/documentation/at-rules/ -- Overview of all at-rules (@use, @forward, @import, @mixin, @function, @extend, @error, @warn, @debug, control flow)
- https://sass-lang.com/documentation/at-rules/use/ -- @use module system: namespaces, configuration with 'with', private members, differences from @import
- https://sass-lang.com/documentation/breaking-changes/ -- Index of all documented breaking changes with versions
- https://sass-lang.com/documentation/breaking-changes/import/ -- @import deprecation timeline and migration path
- https://sass-lang.com/documentation/modules/ -- List of built-in sass:* modules
- https://sass-lang.com/documentation/js-api/ -- JS API: compile/compileAsync/compileString, importers, legacy render() deprecation
- https://sass-lang.com/documentation/cli/dart-sass/ -- Dart Sass CLI usage, flags, source maps, deprecation-warning controls
- https://sass-lang.com/documentation/cli/migrator/ -- sass-migrator tool: module, division, color, if() migrations
- https://sass-lang.com/dart-sass/ -- Dart Sass overview: reference implementation status, distribution channels, Embedded Sass protocol
- https://sass-lang.com/install/ -- Installation methods across npm, standalone, Homebrew, Chocolatey, and ecosystem integrations
- https://sass-lang.com/blog/security-alert-tar-permissions/ -- Official security advisory: tar archive permission bug enabling privilege escalation
- https://sass-lang.com/blog/libsass-is-deprecated/ -- LibSass/Ruby Sass deprecation announcement (2020-10-26) and rationale
- https://sass-lang.com/blog/node-sass-is-end-of-life/ -- Node Sass end-of-life announcement (2024-07-24)
- https://github.com/sass/dart-sass/releases -- Dart Sass release history with dates and per-release behavioral/breaking notes
- https://sass-lang.com/blog/announcing-dart-sass/ -- Historical Dart Sass performance benchmarks vs Ruby Sass/LibSass (referenced via search summary)
- https://sass-lang.com/blog/node-fibers-discontinued/ -- Sync vs async render() performance note (referenced via search summary)

## Sentry

- https://docs.sentry.io/product/issues/ -- issue/event grouping, fingerprinting, quota-per-event model
- https://docs.sentry.io/concepts/key-terms/tracing/ -- tracing key terms: traces, spans, transactions
- https://docs.sentry.io/product/session-replay/ -- Session Replay product overview
- https://docs.sentry.io/product/explore/logs/ -- Sentry Logs product overview and retention-by-plan
- https://docs.sentry.io/platforms/javascript/guides/node/ -- Node.js SDK overview, install, init, capture
- https://docs.sentry.io/platforms/python/ -- Python SDK overview, install, init, capture
- https://docs.sentry.io/platforms/python/integrations/ -- Python SDK framework/library integrations
- https://docs.sentry.io/platforms/python/configuration/options/ -- Python SDK configuration options reference
- https://docs.sentry.io/platforms/javascript/guides/node/configuration/options/ -- JS/Node SDK configuration options reference
- https://docs.sentry.io/platforms/javascript/guides/node/configuration/releases/ -- release configuration and purpose
- https://docs.sentry.io/platforms/javascript/guides/node/configuration/sampling/ -- tracing sample-rate/sampler configuration
- https://docs.sentry.io/platforms/javascript/guides/node/configuration/environments/ -- environment option, enabled option, disabling the SDK
- https://docs.sentry.io/platforms/javascript/sourcemaps/ -- source map upload workflow, Debug IDs
- https://docs.sentry.io/platforms/javascript/guides/node/enriching-events/breadcrumbs/ -- breadcrumbs concept and API
- https://docs.sentry.io/platforms/javascript/guides/node/data-management/sensitive-data/ -- PII scrubbing guidance, beforeSend pattern
- https://docs.sentry.io/platforms/javascript/guides/node/performance/ -- SDK performance/high-throughput guidance
- https://docs.sentry.io/platforms/javascript/guides/node/profiling/ -- profiler overhead trade-off
- https://docs.sentry.io/platforms/javascript/guides/node/troubleshooting/ -- debug mode, "why isn't my error showing up" checklist
- https://docs.sentry.io/platforms/javascript/guides/node/migration/ -- JS SDK migration-guide series index
- https://docs.sentry.io/platforms/javascript/guides/node/migration/v7-to-v8/ -- v7→v8 breaking changes
- https://docs.sentry.io/platforms/javascript/guides/node/migration/v8-to-v9/ -- v8→v9 breaking changes
- https://docs.sentry.io/platforms/javascript/guides/node/migration/v9-to-v10/ -- v9→v10 breaking changes
- https://docs.sentry.io/platforms/javascript/guides/node/opentelemetry/ -- Node SDK/OpenTelemetry relationship
- https://docs.sentry.io/platforms/javascript/guides/nextjs/ -- official Next.js integration guide
- https://docs.sentry.io/platforms/javascript/guides/express/ -- official Express integration guide
- https://docs.sentry.io/platforms/javascript/guides/fastify/ -- official Fastify integration guide
- https://docs.sentry.io/product/sentry-basics/dsn-explainer/ -- DSN structure and public/secret status
- https://docs.sentry.io/product/relay/ -- Relay architecture and PII-scrubbing layering
- https://docs.sentry.io/product/data-management-settings/scrubbing/ -- server-side default and advanced data scrubbing
- https://docs.sentry.io/security-legal-pii/security/ -- security/compliance program index (SOC2, ISO 27001)
- https://docs.sentry.io/api/events/ -- Web API issue-management endpoints
- https://docs.sentry.io/product/releases/ -- release tracking, commit association, deploy notifications
- https://docs.sentry.io/product/releases/setup/release-automation/ -- CI/CD release-automation platform list
- https://docs.sentry.io/product/releases/setup/release-automation/github-actions/ -- getsentry/action-release GitHub Action
- https://docs.sentry.io/product/alerts/ -- alert rules, triggers/filters/actions, notification integrations
- https://docs.sentry.io/pricing/quotas/ -- quota consumption, sampling's effect on billable volume
- https://develop.sentry.dev/self-hosted/ -- self-hosted vs. SaaS deployment, licensing, minimum requirements
- https://github.com/getsentry/sentry-javascript/releases -- current JS SDK version (10.74.0 stable / 11.0.0-beta.2)
- https://pypi.org/project/sentry-sdk/ -- current Python SDK version (2.69.1) and Python-version classifiers

## shadcn/ui

- https://ui.shadcn.com/docs -- Introduction / core philosophy and five foundational principles
- https://ui.shadcn.com/docs/changelog -- Full dated changelog index used for version history and cadence
- https://ui.shadcn.com/docs/installation -- Framework installation overview (Next.js, Vite, Astro, Laravel, React Router, TanStack Start)
- https://ui.shadcn.com/docs/installation/next -- Next.js-specific installation guide
- https://ui.shadcn.com/docs/cli -- Full CLI command reference (init, add, build, migrate *, eject, mcp, etc.)
- https://ui.shadcn.com/docs/components-json -- components.json configuration schema
- https://ui.shadcn.com/docs/theming -- CSS-variable theming system and token conventions
- https://ui.shadcn.com/docs/dark-mode -- Per-framework dark mode guide index
- https://ui.shadcn.com/docs/registry -- Registry protocol overview
- https://ui.shadcn.com/docs/registry/registry-json -- registry.json schema for hosting custom registries
- https://ui.shadcn.com/docs/registry/authentication -- Private registry authentication patterns and security recommendations
- https://ui.shadcn.com/docs/registry/github -- GitHub-repo-as-registry integration
- https://ui.shadcn.com/docs/registry/faq -- Registry dependency naming, pinning, and versioning guidance
- https://ui.shadcn.com/docs/monorepo -- Turborepo monorepo setup guide
- https://ui.shadcn.com/docs/mcp -- MCP server setup for AI coding agent integration
- https://ui.shadcn.com/docs/components -- Component catalog overview page
- https://ui.shadcn.com/docs/components/button -- Example component API doc (Button props/variants)
- https://ui.shadcn.com/docs/forms/react-hook-form -- React Hook Form + Field component integration pattern
- https://ui.shadcn.com/docs/helpers/ai-sdk -- @shadcn/helpers AI SDK deterministic chat-testing integration
- https://ui.shadcn.com/docs/tailwind-v4 -- Tailwind v3→v4 migration guide with breaking-change details
- https://ui.shadcn.com/docs/react-19 -- React 19 peer-dependency compatibility and workarounds
- https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default -- Radix→Base UI default switch changelog entry
- https://ui.shadcn.com/docs/changelog/2026-03-cli-v4 -- CLI v4 release changelog entry
- https://ui.shadcn.com/docs/changelog/2026-09-cn -- cn utility package release changelog entry
- https://ui.shadcn.com/docs/changelog/2026-03-luma -- Luma style/preset changelog entry
- https://ui.shadcn.com/docs/changelog/2026-07-typeset -- shadcn/typeset changelog entry
- https://www.npmjs.com/package/shadcn -- Official npm distribution channel confirming current CLI version 4.21.0
- https://github.com/shadcn-ui/ui -- Official GitHub org repo and SECURITY.md vulnerability-reporting policy

## Socket.IO

- https://socket.io/docs/v4/ -- Introduction, core concepts, feature list
- https://socket.io/docs/v4/how-it-works/ -- Architecture: Engine.IO vs Socket.IO layering, transports, handshake
- https://socket.io/docs/v4/rooms/ -- Rooms API, caveats, disconnecting event
- https://socket.io/docs/v4/namespaces/ -- Namespaces, dynamic namespaces, security caveats
- https://socket.io/docs/v4/middlewares/ -- Server middleware, auth patterns, Express/engine.use integration
- https://socket.io/docs/v4/using-multiple-nodes/ -- Horizontal scaling, sticky sessions, adapters
- https://socket.io/docs/v4/redis-adapter/ -- Redis adapter setup, security, limitations
- https://socket.io/docs/v4/logging-and-debugging/ -- DEBUG env var and localStorage.debug usage
- https://socket.io/docs/v4/admin-ui/ -- Admin UI monitoring/debugging tool
- https://socket.io/docs/v4/server-api/ -- Server-side API reference
- https://socket.io/docs/v4/client-api/ -- Client-side API reference
- https://socket.io/docs/v4/emit-cheatsheet/ -- Emit/broadcast/acknowledgement patterns
- https://socket.io/docs/v4/server-options/ -- Server configuration option reference
- https://socket.io/docs/v4/client-options/ -- Client configuration option reference
- https://socket.io/docs/v4/typescript/ -- TypeScript typed-events pattern
- https://socket.io/docs/v4/testing/ -- Official testing guide (Mocha/Jest/Tape/Vitest)
- https://socket.io/docs/v4/reverse-proxy/ -- Reverse proxy / load balancer deployment configs
- https://socket.io/docs/v4/server-installation/ -- Server install, Node.js version floor
- https://socket.io/docs/v4/client-installation/ -- Client install, CDN, bundle sizes, browser support floor
- https://socket.io/docs/v4/handling-cors/ -- CORS configuration and its documented limitations
- https://socket.io/docs/v4/connection-state-recovery/ -- Connection state recovery feature and its limits
- https://socket.io/docs/v4/troubleshooting-connection-issues/ -- Official catalog of connection error signatures
- https://socket.io/docs/v4/migrating-from-3-x-to-4-0/ -- 3.x -> 4.0 breaking changes guide
- https://socket.io/docs/v4/migrating-from-2-x-to-3-0/ -- 2.x -> 3.0 breaking changes guide
- https://socket.io/docs/v4/changelog/ -- Version history / major milestones; verified 4.8.3 current
- https://socket.io/docs/v4/socket-io-protocol/ -- Wire protocol reference for implementers
- https://github.com/socketio/socket.io/releases -- GitHub releases for sub-packages (patch/security history)
- https://registry.npmjs.org/socket.io -- npm registry metadata, used only to corroborate version facts

## Swagger

- https://swagger.io/docs/ -- swagger.io docs landing page — product tile listing (Studio/Explore/Editor/UI/Portal), used for the documentation-host note
- https://swagger.io/tools/ -- Official tools index listing the open-source lineup (Editor, Codegen, UI, apidom, Core, Parser, JS) plus SwaggerHub
- https://swagger.io/tools/swagger-editor/ -- Official Swagger Editor product page — description and hosted editor.swagger.io reference
- https://github.com/swagger-api/swagger-ui -- Swagger UI GitHub repo README — core description, npm packages, version/compat info
- https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/installation.md -- Swagger UI installation doc (GitHub-hosted) — npm packages, CDN/unpkg, Docker install
- https://github.com/swagger-api/swagger-ui/blob/master/docs/development/setting-up.md -- Swagger UI development setup doc — prerequisites, local dev server
- https://github.com/swagger-api/swagger-ui/releases -- Swagger UI releases index — current stable version and patch cadence
- https://github.com/swagger-api/swagger-ui/releases/tag/v4.0.0 -- Swagger UI v4.0.0 release notes — React17/Redux4 breaking change
- https://github.com/swagger-api/swagger-ui/releases/tag/v5.0.0 -- Swagger UI v5.0.0 release notes — OpenAPI 3.1 support, Docker multi-platform, perf notes
- https://github.com/swagger-api/swagger-ui/security -- Swagger UI security policy — reporting process and EOL/support-window timeline per major version
- https://github.com/advisories/GHSA-qrmm-w75w-3wpx -- GitHub Security Advisory for Swagger UI SSRF/phishing via ?url param, fixed in 4.1.3
- https://swagger.io/docs/open-source-tools/swagger-ui/customization/plugin-api/ -- Swagger UI plugin API doc — Redux-based plugin architecture and extension points
- https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/ -- Swagger UI configuration reference — full JS init options table
- https://swagger.io/docs/open-source-tools/swagger-ui/usage/cors/ -- Swagger UI CORS usage/troubleshooting doc
- https://swagger.io/docs/open-source-tools/swagger-ui/usage/deep-linking/ -- Swagger UI deep-linking usage doc
- https://swagger.io/docs/open-source-tools/swagger-ui/usage/installation/ -- Swagger UI installation doc (swagger.io-hosted) — Docker env vars, dist folder
- https://swagger.io/docs/open-source-tools/swagger-ui/usage/limitations/ -- Swagger UI documented limitations — browser forbidden-header/cookie constraint
- https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/ -- Swagger UI OAuth2 usage doc — initOAuth() options and security warnings
- https://swagger.io/docs/open-source-tools/swagger-ui/usage/version-detection/ -- Swagger UI version-detection doc reference
- https://github.com/swagger-api/swagger-editor -- Swagger Editor GitHub repo README — install, Docker, build requirements, Scarf analytics
- https://github.com/swagger-api/swagger-codegen -- Swagger Codegen GitHub repo — 2.x/3.x parallel-line architecture
- https://github.com/swagger-api/swagger-codegen/blob/master/README.md -- Swagger Codegen README — CLI usage, supported languages, config, CI integration

## Tailwind CSS

- https://tailwindcss.com/docs/styling-with-utility-classes -- Core utility-first philosophy, state variants, arbitrary values, managing duplication, inline-style guidance
- https://tailwindcss.com/docs/theme -- @theme directive, theme variable namespaces, extending/overriding/resetting theme, CSS variable output
- https://tailwindcss.com/docs/detecting-classes-in-source-files -- Automatic content detection, @source directive, dynamic-class-name limitation, safelisting
- https://tailwindcss.com/docs/functions-and-directives -- Full at-rule/function reference: @theme, @source, @utility, @variant, @custom-variant, @apply, @reference, @config, @plugin, --spacing(), --alpha(), theme()
- https://tailwindcss.com/docs/adding-custom-styles -- @layer usage guidance, arbitrary values vs custom CSS, anti-pattern warning against component-class overuse
- https://tailwindcss.com/docs/dark-mode -- Default media-query dark mode, class/data-attribute toggle via @custom-variant, localStorage persistence pattern
- https://tailwindcss.com/docs/responsive-design -- Default breakpoint values, mobile-first approach, arbitrary breakpoints, container queries
- https://tailwindcss.com/docs/hover-focus-and-other-states -- Full taxonomy of state variants: pseudo-classes, pseudo-elements, media queries, attribute selectors, group/peer, child selectors
- https://tailwindcss.com/docs/colors -- Default color palette, opacity modifiers, color customization
- https://tailwindcss.com/docs/preflight -- Base style reset layer, what it resets, how to customize/disable
- https://tailwindcss.com/docs/compatibility -- Browser support requirements, Sass/Less/Stylus incompatibility, CSS Modules and scoped-style caveats
- https://tailwindcss.com/docs/editor-setup -- Official IntelliSense extension, Prettier plugin, JetBrains/Zed support
- https://tailwindcss.com/docs/upgrade-guide -- Full v3-to-v4 upgrade guide: automated tool, all renamed/removed utilities, breaking changes
- https://tailwindcss.com/docs/installation/using-vite -- Vite plugin installation and architecture
- https://tailwindcss.com/docs/installation/using-postcss -- PostCSS plugin installation
- https://tailwindcss.com/docs/installation/tailwind-cli -- Standalone CLI installation, watch mode, native binaries
- https://tailwindcss.com/docs/installation/play-cdn -- Play CDN dev-only warning and production alternatives
- https://tailwindcss.com/docs/installation/framework-guides -- List of all officially supported framework integration guides
- https://tailwindcss.com/docs/optimizing-for-production -- Confirmed 307 redirect to v3.tailwindcss.com, evidencing doc-host archival and no direct v4 equivalent page
- https://tailwindcss.com/blog/tailwindcss-v4 -- Official v4.0 announcement: engine rewrite, performance numbers, new features
- https://tailwindcss.com/blog/tailwindcss-v4-3 -- Official v4.3 announcement: scrollbar utilities, container-size queries, zoom/tab-size utilities
- https://github.com/tailwindlabs/tailwindcss/blob/main/CHANGELOG.md -- Official changelog with full version history, release dates, and breaking-change entries
- https://registry.npmjs.org/tailwindcss -- npm registry dist-tags used to confirm current stable version and v3-lts tag

## Three.js

- https://threejs.org/docs/ -- Official API reference index; category structure (Core vs Addons) and navigation.
- https://threejs.org/docs/llms.txt -- Official LLM-oriented documentation summary with first-party best-practice guidance (import maps, WebGL vs WebGPU choice, TSL usage).
- https://threejs.org/docs/llms-full.txt -- Official full-text LLM documentation dump including complete code examples and the entire TSL reference.
- https://threejs.org/docs/pages/Object3D.html.md -- Object3D API reference (base class for scene-graph objects).
- https://threejs.org/docs/pages/Scene.html.md -- Scene API reference.
- https://threejs.org/docs/pages/WebGLRenderer.html.md -- WebGLRenderer API reference: constructor options, properties, methods.
- https://threejs.org/docs/pages/WebGPURenderer.html.md -- WebGPURenderer API reference.
- https://threejs.org/docs/pages/Renderer.html.md -- Abstract Renderer base class API reference (parent of WebGPURenderer).
- https://threejs.org/docs/pages/BufferGeometry.html.md -- BufferGeometry API reference.
- https://threejs.org/docs/pages/Mesh.html.md -- Mesh API reference.
- https://threejs.org/docs/pages/Raycaster.html.md -- Raycaster API reference (mouse picking).
- https://threejs.org/docs/pages/Clock.html.md -- Clock API reference, showing its deprecation-since-r183 marker.
- https://threejs.org/docs/pages/Material.html.md -- Material base class API reference (dispose method, event).
- https://threejs.org/docs/pages/Texture.html.md -- Texture API reference (colorSpace, dispose).
- https://threejs.org/manual/#en/fundamentals -- Core-concepts tutorial: scene graph, renderer, camera, mesh/geometry/material, render loop.
- https://threejs.org/manual/#en/installation -- Official installation/configuration guide: npm+build-tool vs CDN+import-map, TypeScript types note, deployment basics.
- https://threejs.org/manual/#en/color-management -- Color Management guide: color spaces, ColorManagement.enabled, colorSpace properties.
- https://threejs.org/manual/#en/cleanup -- Resource disposal guide: dispose() patterns, ResourceTracker helper, memory-cost figures.
- https://threejs.org/manual/#en/debugging-javascript -- General JS debugging guidance for three.js apps (devtools, console, on-screen debug overlays).
- https://threejs.org/manual/#en/debugging-glsl -- GLSL-specific shader debugging techniques.
- https://threejs.org/manual/#en/rendering-on-demand -- Render-on-demand performance pattern vs continuous requestAnimationFrame loop.
- https://threejs.org/manual/#en/optimize-lots-of-objects -- Performance guide on merging geometry to reduce draw calls.
- https://threejs.org/manual/#en/webgpurenderer -- WebGPURenderer usage guide: architecture, TSL, migration limitations, WebGLRenderer maintenance-status statement.
- https://threejs.org/manual/#en/how-to-update-things -- Guide on mutating objects/geometries/materials at runtime, including needsUpdate and buffer-resize limitations.
- https://threejs.org/manual/#en/libraries-and-plugins -- Official list of community frameworks/libraries integrating with three.js (react-three-fiber, Threlte, physics engines, etc.).
- https://threejs.org/manual/#en/webgl-compatibility-check -- Official WebGL2 feature-detection pattern using the WebGL.js addon.
- https://github.com/mrdoob/three.js -- Repository root; source for package.json, SECURITY.md, CONTRIBUTING.md.
- https://github.com/mrdoob/three.js/releases -- Release list; used with the GitHub Releases API to establish ground-truth version/date data.
- https://github.com/mrdoob/three.js/releases/tag/r186 -- Current release's changelog (breaking changes, features, fixes).
- https://github.com/mrdoob/three.js/wiki/Migration-Guide -- Official version-to-version breaking-change/migration record, including the '10-release increments' upgrade policy.
- https://raw.githubusercontent.com/mrdoob/three.js/dev/SECURITY.md -- Official security vulnerability disclosure policy.
- https://raw.githubusercontent.com/mrdoob/three.js/dev/.github/CONTRIBUTING.md -- Contributor-facing testing/build instructions (npm run test, test-e2e).
- https://raw.githubusercontent.com/mrdoob/three.js/dev/package.json -- npm package manifest: version, module type, exports map (three, three/webgpu, three/tsl, three/addons).

## TypeORM

- https://typeorm.io/docs/getting-started/ -- Install requirements, core concepts, ActiveRecord vs DataMapper patterns
- https://typeorm.io/docs/entity/entities/ -- Entity/column/primary-key/inheritance reference
- https://typeorm.io/docs/data-source/data-source-options/ -- Full DataSource configuration option reference, including production warnings
- https://typeorm.io/docs/working-with-entity-manager/working-with-repository/ -- Repository/EntityManager API overview and relationship
- https://typeorm.io/docs/help/decorator-reference/ -- Full catalog of TypeORM decorators
- https://typeorm.io/docs/relations/relations/ -- Relation types, cascade options, and cascade security warning
- https://typeorm.io/docs/relations/eager-and-lazy-relations/ -- Eager/lazy relation semantics, restrictions, experimental status of lazy loading
- https://typeorm.io/docs/transactions/ -- Transaction API (callback + QueryRunner), isolation level support per database driver
- https://typeorm.io/docs/migrations/why/ -- Rationale for migrations over synchronize:true in production
- https://typeorm.io/docs/migrations/setup/ -- Migrations configuration options including migrationsTransactionMode
- https://typeorm.io/docs/migrations/executing/ -- Migration CLI commands (migration:run/revert) and TS execution wrappers
- https://typeorm.io/docs/query-builder/caching/ -- Query-result caching: default TTL, per-query config, storage backends
- https://typeorm.io/docs/performance-optimization/introduction/ -- Performance optimization topic index (N+1, caching, indexing, loading strategies)
- https://typeorm.io/docs/performance-optimization/pagination/ -- Offset vs cursor-based pagination guidance
- https://typeorm.io/docs/logging/ -- Logging/debugging configuration: logger types, log levels, DEBUG env var, slow-query logging
- https://typeorm.io/docs/help/supported-platforms/ -- Supported runtimes/platforms and per-platform limitations (Node, Browser, Cordova, NativeScript, etc.)
- https://typeorm.io/docs/releases/1.0/release-notes/ -- v1.0 breaking changes, new features, and security fixes
- https://typeorm.io/docs/releases/1.0/upgrading-from-0.3/ -- 0.3.x to 1.0 upgrade guide and @typeorm/codemod tool
- https://typeorm.io/blog/future-of-typeorm -- Official blog post on project governance/maintenance transition and roadmap framing
- https://github.com/typeorm/typeorm/releases -- Canonical release list and changelog bodies; used via GitHub REST API for verified publish timestamps
- https://github.com/typeorm/typeorm/security/policy -- Official vulnerability reporting process and security guarantee scope

## TypeScript

- https://www.typescriptlang.org/docs/ -- Documentation homepage/navigation; confirms typescriptlang.org is still the canonical docs host and links to the TS 7.0 announcement
- https://www.typescriptlang.org/docs/handbook/2/basic-types.html -- Core concepts: static type-checking, structural nature, type erasure at runtime, strictness flags
- https://www.typescriptlang.org/docs/handbook/type-compatibility.html -- Structural typing explanation and explicitly documented unsoundness (bivariance, excess-property checks)
- https://www.typescriptlang.org/docs/handbook/enums.html -- Enum caveats, ambient const enum pitfalls, recommended as-const alternative
- https://www.typescriptlang.org/docs/handbook/decorators.html -- Decorator patterns, experimentalDecorators flag, stage-3 decorators since TS 5.0, emitDecoratorMetadata
- https://www.typescriptlang.org/docs/handbook/modules/theory.html -- Module system architecture: host modeling, module/moduleResolution, output-relative import paths
- https://www.typescriptlang.org/docs/handbook/project-references.html -- Project references, composite/declaration config, tsc -b build mode
- https://www.typescriptlang.org/docs/handbook/integrating-with-build-tools.html -- Official integration guides for Babel, Webpack, Vite, Rollup, Gulp, Browserify, Grunt, Svelte, Jspm, MSBuild/NuGet
- https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html -- Official JS-to-TS incremental migration guide
- https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html -- JSDoc type-annotation tag support for plain JS files
- https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html -- Recommended patterns and anti-patterns for writing .d.ts declaration files
- https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html -- Official guidance for publishing typed npm packages, types field, @types dependencies
- https://www.typescriptlang.org/docs/handbook/babel-with-typescript.html -- Babel interoperability reference
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html -- TypeScript 5.9 release notes: import defer, module node20, ArrayBuffer breaking change
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html -- TypeScript 6.0 release notes: new strict/module/target defaults, removed/deprecated options
- https://www.typescriptlang.org/tsconfig/ -- Full tsconfig.json compiler options reference organized by category, with recommended and version-tagged options
- https://www.typescriptlang.org/download/ -- Official install instructions (npm/NuGet/VS extension) and current version confirmation
- https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/ -- Official TS 6.0 announcement: release date, defaults changed, bridge-to-7.0 framing, migration tools
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ -- Official TS 7.0 announcement: Go-native compiler rewrite, release date, perf benchmarks, no-API limitation, breaking changes
- https://github.com/microsoft/TypeScript/wiki/Architectural-Overview -- Official compiler architecture overview (Scanner/Parser/Binder/Checker/Emitter/Language Service), pre-7.0
- https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API -- Compiler API reference (createProgram, createSourceFile, transpileModule, LanguageService); flags itself as describing TS <=6.0 only
- https://github.com/microsoft/TypeScript/wiki/Performance -- Official performance tuning guidance, diagnostic flags, project-reference sizing advice
- https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals -- Official list of design goals and non-goals, including explicit non-goal of full type-system soundness
- https://github.com/microsoft/typescript/wiki/faq -- Official FAQ covering documented unsoundness (method bivariance) and structural typing edge cases
- https://code.visualstudio.com/docs/typescript/typescript-debugging -- Official VS Code documentation for debugging TypeScript with source maps and launch.json
- https://nodejs.org/api/typescript.html -- Node.js official docs on native TypeScript type-stripping support, versions, and limitations (cited for integration section only)
- https://www.npmjs.com/package/typescript -- Confirms current published npm version (7.0.2) at research time

## Vite

- https://vite.dev/guide/ -- Getting Started guide — core concepts, dev server + build overview
- https://vite.dev/guide/why -- Why Vite — architecture rationale, ecosystem and framework adoption, Rolldown framing
- https://vite.dev/guide/features -- Features guide — TS/JSX, CSS, assets, glob imports, build optimizations
- https://vite.dev/guide/migration -- Official v7→v8 migration guide — breaking changes and deprecations
- https://vite.dev/changes/ -- Forthcoming breaking-changes tracker gated behind the `future` config flag
- https://vite.dev/guide/performance -- Official performance guidance (resolve costs, barrel files, warmup, profiling)
- https://vite.dev/guide/troubleshooting -- Official troubleshooting/debugging guide
- https://vite.dev/guide/static-deploy -- Static deployment guide including base path and hosting platforms
- https://vite.dev/guide/backend-integration -- Backend integration guide (manifest.json, dev script injection)
- https://vite.dev/guide/api-environment -- Environment API guide, introduced in Vite 6
- https://vite.dev/guide/api-plugin -- Plugin API reference (hooks, ordering, apply/enforce)
- https://vite.dev/guide/api-javascript -- JavaScript API reference (createServer/build/preview/resolveConfig)
- https://vite.dev/guide/ssr -- SSR guide, including explicit low-level-API and evolving-API caveats
- https://vite.dev/guide/env-and-mode -- Env variable and mode handling, VITE_ prefix security note
- https://vite.dev/config/ -- Configuring Vite index — config file resolution and structure
- https://vite.dev/config/server-options -- Server options reference, including security-flagged options
- https://vite.dev/releases -- Release cadence and support-tier policy
- https://vite.dev/blog/announcing-vite8 -- Official Vite 8.0 release announcement blog post
- https://vite.dev/blog/announcing-vite8-beta -- Official Vite 8 beta announcement, introduces rolldown-vite package
- https://vitest.dev/guide/ -- Vitest getting-started/why page, same maintaining org, cited for Testing dimension
- https://devtools.vite.dev/guide/ -- Vite DevTools official sub-project overview
- https://devtools.vite.dev/vitest/ -- Vite DevTools Vitest integration docs
- https://v6.vite.dev/ -- Version-pinned Vite 6 docs snapshot, used to confirm doc-versioning structure
- https://v4.vite.dev/guide/ -- Version-pinned Vite 4 docs snapshot
- https://v3.vitejs.dev/guide/ -- Version-pinned Vite 3 docs snapshot under legacy vitejs.dev domain

## Vitest

- https://vitest.dev/guide/ -- Getting-started overview: what Vitest is, version/Node/Vite requirements
- https://vitest.dev/guide/why.html -- Design philosophy, origin story, Jest comparison rationale
- https://vitest.dev/guide/features.html -- Full feature list: watch mode, snapshots, mocking, browser mode, in-source testing, coverage
- https://vitest.dev/blog/vitest-5.html -- Official Vitest 5.0 release announcement: new features, performance work, breaking changes
- https://vitest.dev/guide/migration.html -- Migrating to Vitest 5.0: version requirements and detailed breaking-change list
- https://vitest.dev/guide/migration/jest.html -- Migrating from Jest to Vitest: API mapping and behavioral differences
- https://vitest.dev/guide/workspace.html -- Projects (formerly workspace) config for monorepos, deprecation note
- https://vitest.dev/config/ -- Configuration file resolution order, defineConfig/mergeConfig usage
- https://vitest.dev/config/api.html -- API server security: host binding, allowWrite/allowExec defaults and risks
- https://vitest.dev/guide/mocking.html -- vi mocking utilities, hoisting rules, best practices and pitfalls
- https://vitest.dev/guide/coverage.html -- Coverage providers (v8/Istanbul), config, ignore comments, performance trade-offs
- https://vitest.dev/guide/browser/ -- Browser Mode: providers, config, limitations, security notes on custom commands
- https://vitest.dev/guide/environment.html -- Built-in and custom test environments (node/jsdom/happy-dom/edge-runtime)
- https://vitest.dev/guide/improving-performance.html -- Pool selection, isolation, caching, sharding performance guidance
- https://vitest.dev/guide/debugging.html -- VS Code, IntelliJ, Node Inspector, and browser-mode debugging instructions
- https://vitest.dev/guide/common-errors.html -- Documented common errors/limitations with causes and fixes
- https://vitest.dev/guide/ide.html -- Official IDE integrations: VS Code extension, JetBrains, Wallaby.js
- https://vitest.dev/guide/cli.html -- CLI commands and flags reference
- https://vitest.dev/api/ -- API reference index: test/describe/expect/vi/hooks namespaces
- https://vitest.dev/guide/in-source.html -- In-source testing pattern, config, and production build-stripping guidance
- https://vitest.dev/releases.html -- Release cadence and version support/security-backport policy

## Vue.js

- https://vuejs.org/guide/introduction.html -- Core concepts, API styles (Options vs Composition), progressive-framework philosophy
- https://vuejs.org/guide/reusability/composables.html -- Composables pattern and reactivity best practices
- https://vuejs.org/guide/extras/composition-api-faq.html -- Composition API vs Options API rationale and tradeoffs
- https://vuejs.org/guide/extras/rendering-mechanism.html -- Compiler/VDOM architecture: patch flags, block tree, static hoisting
- https://vuejs.org/guide/extras/reactivity-in-depth.html -- Reactivity architecture (Proxy vs Object.defineProperty), limitations
- https://vuejs.org/guide/best-practices/security.html -- Full security guidance: XSS, v-html, URL/style/JS injection, CSRF
- https://vuejs.org/guide/best-practices/performance.html -- Performance guidance, profiling tools, computed() 3.4+ change detection
- https://vuejs.org/guide/scaling-up/testing.html -- Official testing tools/patterns (Vitest, Vue Test Utils, Cypress, Playwright)
- https://vuejs.org/guide/best-practices/production-deployment.html -- Production build requirements, CDN builds, error tracking
- https://vuejs.org/guide/scaling-up/ssr.html -- SSR architecture, hydration, limitations, production considerations
- https://vuejs.org/guide/typescript/overview.html -- TypeScript integration and tsconfig recommendations
- https://vuejs.org/api/sfc-script-setup.html -- script setup compiler macros with version-gated feature list
- https://vuejs.org/api/application.html -- Application API surface: createApp, app.config, plugins
- https://vuejs.org/guide/components/async.html -- Async components, defineAsyncComponent, lazy hydration strategies (3.5+)
- https://vuejs.org/guide/built-ins/suspense.html -- Suspense component API and its documented experimental status
- https://vuejs.org/guide/essentials/list.html -- List rendering caveats: array mutation detection, v-for/v-if anti-pattern
- https://vuejs.org/guide/components/registration.html -- Global vs local component registration tradeoffs
- https://vuejs.org/guide/reusability/plugins.html -- Plugin architecture and globalProperties anti-pattern warning
- https://vuejs.org/style-guide/ -- Official style guide priority-tier framework (A-D)
- https://vuejs.org/style-guide/rules-use-with-caution -- Documented Priority-D anti-patterns
- https://vuejs.org/guide/scaling-up/state-management.html -- State management guidance and Pinia recommendation
- https://vuejs.org/guide/scaling-up/tooling.html -- Official tooling: create-vue/Vite, IDE support, devtools, linting
- https://vuejs.org/guide/extras/web-components.html -- Web Components / Custom Elements bidirectional integration
- https://vuejs.org/about/releases -- Release cadence, semver policy, pre-release channels
- https://v3-migration.vuejs.org/ -- Vue 2 to Vue 3 migration guide overview and Migration Build
- https://v3-migration.vuejs.org/breaking-changes/ -- Full catalogue of Vue 2 to Vue 3 breaking changes
- https://github.com/vuejs/core/releases -- Recent release history and dates
- https://github.com/vuejs/core/releases/tag/v3.6.0-rc.1 -- Vapor Mode details and 3.6 pre-release status
- https://registry.npmjs.org/vue -- npm dist-tags confirming current stable/rc/beta/alpha/legacy versions
- https://devtools.vuejs.org/getting-started/features -- Official Vue Devtools debugging feature set
- https://router.vuejs.org/introduction.html -- Vue Router official status and integration
- https://pinia.vuejs.org/introduction.html -- Pinia official status as recommended state management

## WebRTC

- https://www.w3.org/TR/webrtc/ -- W3C Recommendation (WebRTC 1.0) — core spec, RTCPeerConnection, certificates/DTLS constraints
- https://w3c.github.io/webrtc-pc/ -- Living editor's draft of the WebRTC spec
- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API -- MDN WebRTC API umbrella page — core concepts, interface list
- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Session_lifetime -- MDN guide on signaling and session lifecycle (self-flagged as under construction)
- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Protocols -- MDN guide on SDP and the WebRTC protocol stack
- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Connectivity -- MDN guide on ICE/STUN/TURN connectivity establishment
- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling -- MDN worked example of a WebSocket-based signaling server
- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels -- MDN guide on RTCDataChannel, message size limits
- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Perfect_negotiation -- MDN guide describing the perfect-negotiation pattern
- https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/getStats -- MDN reference for getStats()/RTCStatsReport
- https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs -- MDN codec support matrix across browsers/versions
- https://webrtc.org/ -- webrtc.org project homepage (redesigned; banner points to archive)
- https://webrtc.org/getting-started/overview -- webrtc.org getting-started overview of media capture and RTCPeerConnection
- https://webrtc.org/getting-started/turn-server -- webrtc.org guide on TURN relay necessity/deployment
- https://webrtc.org/getting-started/unified-plan-transition-guide -- webrtc.org Plan B to Unified Plan migration/version-milestone guide
- https://webrtc.org/getting-started/testing -- webrtc.org testing guidance page
- https://webrtc.github.io/webrtc-org/ -- Archived previous version of the webrtc.org site
- https://webrtc.github.io/webrtc-org/native-code/ -- Archived page describing the native-code C++ library audience/purpose
- https://www.w3.org/groups/wg/webrtc/ -- W3C WebRTC Working Group charter page
- https://firefox-source-docs.mozilla.org/contributing/debugging/debugging_webrtc_calls.html -- Mozilla engineering docs on debugging WebRTC calls (about:webrtc, MOZ_LOG)
- https://github.com/webrtc/adapter -- adapter.js/webrtc-adapter README, noting repo is now a read-only fork

## WebSocket API

- https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API -- MDN WebSocket API overview — core concepts, WebSocketStream/WebTransport comparison, no-backpressure limitation
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket -- MDN WebSocket interface reference — properties, events, readyState
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket -- MDN WebSocket() constructor reference — url/protocols params, SecurityError
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/send -- MDN send() method reference — accepted data types, fire-and-forget behavior
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/close_event -- MDN close event reference
- https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent -- MDN CloseEvent interface reference
- https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code -- MDN close status code registry table
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocketStream -- MDN WebSocketStream (experimental, non-standard) reference
- https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications -- MDN client-implementation guide — bfcache pattern, wss recommendation, backpressure
- https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers -- MDN server-implementation guide — Origin checking, CSWH, reverse proxy pattern, ping/pong
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/connect-src -- MDN CSP connect-src directive reference
- https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/inspecting_web_sockets/index.html -- Firefox DevTools WebSocket frame inspector documentation
- https://websockets.spec.whatwg.org/ -- WHATWG WebSockets Living Standard — normative JS interface spec, Fetch-integrated handshake
- https://github.com/whatwg/websockets/commits/main -- WHATWG WebSockets spec repo commit history — used to confirm currency and date the http(s)-scheme change
- https://www.rfc-editor.org/rfc/rfc6455.html -- RFC 6455, The WebSocket Protocol (IETF) — normative wire protocol, handshake, framing, masking
- https://www.rfc-editor.org/rfc/rfc7692.html -- RFC 7692, Compression Extensions for WebSocket (permessage-deflate)
- https://www.rfc-editor.org/rfc/rfc8441.html -- RFC 8441, Bootstrapping WebSockets with HTTP/2
- https://nodejs.org/api/globals.html -- Node.js official docs — global WebSocket client class version history and flag

## All distinct source domains

Each domain below is counted once per technology that cites it (not once per URL), sorted by number of citing technologies, descending.

| Domain | Technologies citing it |
|---|---|
| github.com | 30 |
| raw.githubusercontent.com | 10 |
| registry.npmjs.org | 9 |
| developer.mozilla.org | 4 |
| api.github.com | 3 |
| firefox-source-docs.mozilla.org | 3 |
| nodejs.org | 3 |
| developers.google.com | 2 |
| docs.github.com | 2 |
| github.blog | 2 |
| vitest.dev | 2 |
| www.npmjs.com | 2 |
| www.w3.org | 2 |
| angular.dev | 1 |
| blog.angular.dev | 1 |
| blog.typicode.com | 1 |
| blogs.oracle.com | 1 |
| clickhouse.com | 1 |
| code.claude.com | 1 |
| code.visualstudio.com | 1 |
| dev.mysql.com | 1 |
| devblogs.microsoft.com | 1 |
| develop.sentry.dev | 1 |
| developers.googleblog.com | 1 |
| developers.openai.com | 1 |
| devguide.python.org | 1 |
| devtools.vite.dev | 1 |
| devtools.vuejs.org | 1 |
| docs.claude.com | 1 |
| docs.docker.com | 1 |
| docs.libuv.org | 1 |
| docs.npmjs.com | 1 |
| docs.opensearch.org | 1 |
| docs.python.org | 1 |
| docs.sentry.io | 1 |
| ecma-international.org | 1 |
| en.wikipedia.org | 1 |
| expressjs.com | 1 |
| fastify.dev | 1 |
| genai.owasp.org | 1 |
| go.dev | 1 |
| grafana.com | 1 |
| graphql.org | 1 |
| html.spec.whatwg.org | 1 |
| jestjs.io | 1 |
| learn.openapis.org | 1 |
| mongoosejs.com | 1 |
| mui.com | 1 |
| nextjs.org | 1 |
| nuxt.com | 1 |
| opensearch.org | 1 |
| opentelemetry.io | 1 |
| orm.drizzle.team | 1 |
| packaging.python.org | 1 |
| peps.python.org | 1 |
| pinia.vuejs.org | 1 |
| pkg.go.dev | 1 |
| platform.claude.com | 1 |
| playwright.dev | 1 |
| prometheus.io | 1 |
| pypi.org | 1 |
| react.dev | 1 |
| redis.io | 1 |
| router.vuejs.org | 1 |
| sass-lang.com | 1 |
| socket.io | 1 |
| spec.graphql.org | 1 |
| spec.openapis.org | 1 |
| status.search.google.com | 1 |
| support.google.com | 1 |
| swagger.io | 1 |
| tailwindcss.com | 1 |
| tc39.es | 1 |
| threejs.org | 1 |
| typeorm.io | 1 |
| typicode.github.io | 1 |
| ui.shadcn.com | 1 |
| v3-migration.vuejs.org | 1 |
| v3.vitejs.dev | 1 |
| v4.vite.dev | 1 |
| v6.vite.dev | 1 |
| validator.w3.org | 1 |
| vercel.com | 1 |
| vite.dev | 1 |
| vuejs.org | 1 |
| w3c.github.io | 1 |
| web-platform-tests.org | 1 |
| web.dev | 1 |
| webrtc.github.io | 1 |
| webrtc.org | 1 |
| websockets.spec.whatwg.org | 1 |
| whatwg.org | 1 |
| www.docker.com | 1 |
| www.graphql-js.org | 1 |
| www.mongodb.com | 1 |
| www.mysql.com | 1 |
| www.openapis.org | 1 |
| www.postgresql.org | 1 |
| www.prisma.io | 1 |
| www.rfc-editor.org | 1 |
| www.typescriptlang.org | 1 |
