# Performance Knowledge Map

Synthesized from `research/technologies/*.md` (44 technologies) via the pre-extracted data file `kmap_performance.json`. Organized by **performance concern category**, cross-referencing which technologies are involved. All facts are drawn only from the source data; citations are preserved verbatim. Sections marked "Not covered" reflect genuine silence in the underlying research, not omission.

---

## 1. Caching Strategy

### 1.1 Query-result / ORM-level caching

| Technology | Note | Citation |
|---|---|---|
| TypeORM | `cache:true` (default 1000ms lifetime), per-query override via `.cache(ms)` or named cache-ID+TTL; storage backends: default DB table, Redis/IORedis, IORedis Cluster, or custom `QueryResultCache`. | `[Source: https://typeorm.io/docs/query-builder/caching/]` |
| TypeORM | For production, a dedicated Redis/IORedis (or Cluster) store is recommended over the default DB-table store; `ignoreErrors` lets queries fall through to the live DB if the cache backend fails, preserving availability. | `[Source: https://typeorm.io/docs/query-builder/caching/]` |
| Drizzle ORM | Experimental caching layer, opt-in per-query (`.$withCache()`) or global, integrates with Upstash Redis via `upstashCache()`; mutations auto-invalidate affected cached queries by default. | `[Source: https://orm.drizzle.team/docs/cache]` |
| Prisma | Absence of caching is named as one of the documented common causes of slow queries, alongside over-fetching, missing indexes, and full table scans. | `[Source: https://www.prisma.io/docs/orm/prisma-client/queries/query-optimization-performance]` |
| Prisma | Query Insights (built into Prisma Postgres) identifies slow/expensive queries — works out-of-the-box for raw SQL, one extra setup step for ORM-originated queries; replaces the earlier Prisma Optimize product. | `[Source: https://www.prisma.io/docs/query-insights (per llms.txt index), https://www.prisma.io/docs]` |

**Not covered:** Mongoose, MySQL, and MongoDB's own docs (as extracted here) do not describe a query-result caching layer of their own — MongoDB and MySQL's caching-relevant material is about connection/index tuning, not a result cache.

### 1.2 Application / HTTP-layer caching

| Technology | Note | Citation |
|---|---|---|
| Express | Recommends gzip compression via the `compression` middleware, or better, at the reverse-proxy layer (Nginx/HAProxy) for high-traffic sites; reverse proxy also offloads static file serving, TLS, and caching. | `[Source: https://expressjs.com/en/advanced/best-practice-performance.html]` |
| Express | Recommends caching request results at the reverse-proxy/edge layer (Varnish, Nginx) rather than in the Express process itself. | `[Source: https://expressjs.com/en/advanced/best-practice-performance.html]` |
| Express | Redis recommended as an externalized session store so the app can remain stateless behind clustering/load balancing, and as a general caching layer. | `[Source: https://expressjs.com/en/advanced/best-practice-performance.html]` |
| Express | View engines cache the *compiled* template but still re-render (execute) it on every request; the `view cache` app setting defaults to `true` only in production. | `[Source: https://expressjs.com/en/guide/using-template-engines.html]` |
| GraphQL (graphql-js) | Recommended multi-layer caching for production deployments: resolver-level caching, HTTP/CDN caching via persisted queries, schema-build caching, and request-scoped/external caches such as Redis for larger systems. | `[Source: https://www.graphql-js.org/docs/going-to-production/]` |
| GraphQL | Persisted queries (sending a hash instead of full query text) shrink payloads and enable HTTP/CDN caching of otherwise-uncacheable POST requests. | `[Source: https://graphql.org/learn/performance/]` |
| Nuxt | `useFetch`/`useAsyncData` avoid duplicate SSR+client requests by serializing server-fetched data into the payload, unlike raw `$fetch` calls inside `setup()`. | `[Source: https://nuxt.com/docs/4.x/getting-started/data-fetching]` |
| Nuxt | Hybrid rendering via `routeRules` (`swr`, `isr`, `prerender`, `ssr:false` per route) is a core caching/scaling lever; deploys natively to Netlify/Vercel platform rules when detected, but is unavailable under static `nuxt generate`. | `[Source: https://nuxt.com/docs/4.x/guide/concepts/rendering]` |
| Next.js | Cache Components produce a static shell (PPR) servable directly from a CDN without hitting the upstream server; Partial Prefetching lets `<Link>` prefetch just the App Shell by default. | `[Source: https://nextjs.org/docs/app/getting-started/caching]` |

### 1.3 Redis as caching infrastructure (its own performance characteristics)

| Note | Citation |
|---|---|
| Pipelining — batching multiple commands into one write, reading replies afterward — is the recommended way to reduce RTT overhead, documented as giving up to a **10x increase in ops/sec**. | `[Source: https://redis.io/docs/latest/develop/using-commands/pipelining/]` |
| Redis is fundamentally single-threaded for command execution, favoring fast single-core CPU over core count; Redis 8.0 introduced multi-core I/O threading (`io-threads`) that parallelizes I/O while command execution stays single-threaded. | `[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/]` |
| Unix domain sockets provide up to ~50% more throughput than TCP loopback on Linux, with the benefit shrinking as pipeline length grows. | `[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/]` |
| Throughput roughly halves going from ~100 to ~30,000 concurrent connections — relevant to connection-pooling design for any client. | `[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/]` |
| Redis runs measurably slower on VMs than bare metal, mostly due to `fork()` and I/O differences rather than raw compute. | `[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/]` |

### 1.4 Build/tooling caching

| Technology | Note | Citation |
|---|---|---|
| Docker | Build performance centers on layer caching: any changed instruction invalidates that layer and every subsequent one; recommended pattern orders rarely-changing instructions (dependency install) before frequently-changing ones (`COPY . .`). | `[Source: https://docs.docker.com/build/cache/]` |
| Docker | BuildKit cache mounts (`RUN --mount=type=cache`) persist package-manager/dependency caches across builds; bind mounts are more efficient than `COPY` for build-context-only files. | `[Source: https://docs.docker.com/build/building/best-practices/] [Source: https://docs.docker.com/build/cache/]` |
| GitHub Actions | Dependency caching via `actions/cache` is the primary documented lever to reduce workflow run time; caches unused for 7 days are evicted, with a default 10GB per-repo cap and LRU eviction. | `[Source: https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows]` |
| Vitest | v5.0 performance work: a filesystem module cache persists transformed modules across runs; inline projects share the Vite server; faster VM pools via compiled-code reuse. | `[Source: https://vitest.dev/blog/vitest-5.html]` |
| TypeScript | `--incremental` persists compile state across runs; project references (`composite`/`references`, `tsc -b`) improve build time and editor memory for large multi-package codebases. | `[Source: https://github.com/microsoft/TypeScript/wiki/Performance; https://www.typescriptlang.org/docs/handbook/project-references.html]` |
| Google SEO | Google aggressively caches JS resources, so fingerprinted filenames (e.g. `main.2bb85551.js`) are needed to ensure updated resources are re-fetched rather than served stale. | `[Source: https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics]` |

---

## 2. Query Optimization & N+1 Risk

The N+1 problem — one query followed by N per-row follow-up queries — is documented, independently, at essentially every data-access layer in this dataset, each with a structurally similar but implementation-specific fix.

| Technology | N+1 / query-shape note | Citation |
|---|---|---|
| Mongoose | Populate performance: use `select` to limit fields on populated docs, avoid `perDocumentLimit` (issues one query per parent document instead of a single batched query), consider denormalizing frequently-populated fields. | `[Source: https://mongoosejs.com/docs/populate.html]` |
| TypeORM | To avoid N+1, use `leftJoinAndSelect`/`innerJoinAndSelect` (or the `relations` object syntax on `find*`) to fetch related rows in one query; the docs name N+1 and under-use of indexing/caching as the common performance failure modes. | `[Source: https://typeorm.io/docs/performance-optimization/introduction/]` |
| TypeORM | Eager relations default to LEFT JOIN but TypeORM automatically switches to INNER JOIN when the relation is `nullable:false` and owns the join column — a documented micro-optimization. | `[Source: https://typeorm.io/docs/relations/eager-and-lazy-relations/]` |
| Prisma | Use `include` to eager-load relations in one query, or batch with `WHERE id IN (...)` instead of per-row loop queries; `relationLoadStrategy:'join'` executes a relation fetch as a single SQL join instead of separate queries (version availability unconfirmed). | `[Source: https://www.prisma.io/docs/orm/v7/more/best-practices]` |
| Prisma | For databases without enforced foreign keys (PlanetScale named explicitly), Prisma emulates relations and developers must manually add indexes on relation scalar fields to avoid full table scans. | `[Source: https://www.prisma.io/docs/orm/v7/more/best-practices]` |
| GraphQL | The N+1 problem is documented as the most common GraphQL performance issue, arising from the per-field resolver execution model. | `[Source: https://graphql.org/learn/performance/]` |
| GraphQL / DataLoader | DataLoader-style batching coalesces same-tick requests for related data into a single batched backend call, fixing N+1. | `[Source: https://graphql.org/learn/performance/]` |
| GraphQL | Nesting list fields compounds query cost, producing exponential blow-up in returned data volume relative to query size — motivating depth limits even when batching is in place. | `[Source: https://graphql.org/learn/security/]` |
| MongoDB | Excessive `$lookup` use (cross-collection joins) is a documented anti-pattern signaling data that should likely be denormalized/restructured instead, since MongoDB's design favors embedding over joins. | `[Source: https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/]` |

**[Synthesis]** Combining the Mongoose, TypeORM, Prisma, and GraphQL rows above: four independently-documented data layers converge on the same underlying fix pattern — "batch or join instead of iterate" — even though each names it differently (populate+`select`, `leftJoinAndSelect`, `include`/`relationLoadStrategy`, DataLoader). None of the individual sources frames this as a cross-stack pattern; it is only visible when the four are placed side by side.

---

## 3. Indexing

| Technology | Note | Citation |
|---|---|---|
| PostgreSQL | Index type choice is workload-specific and materially affects performance: B-tree (equality/range/sort), GIN (contains-queries over arrays/jsonb/full-text), GiST (geometric/nearest-neighbor), BRIN (large physically-correlated tables), Hash (pure equality). | `[Source: https://www.postgresql.org/docs/current/indexes-types.html]` |
| PostgreSQL | PostgreSQL 18 adds B-tree "skip scan" support for multicolumn indexes, plus an async I/O subsystem improving sequential/bitmap heap scans and vacuum (up to 3x reading from storage, per the release announcement). | `[Source: https://www.postgresql.org/docs/current/release-18.html] and [Source: https://www.postgresql.org/about/news/postgresql-18-released-3142/]` |
| MongoDB | Indexes are the primary performance lever for queries but add write overhead (every insert/update/delete must update matching indexes) and consume memory; the ESR (Equality, Sort, Range) rule governs compound index field ordering. | `[Source: https://www.mongodb.com/docs/manual/applications/indexes/]` |
| Mongoose | `autoIndex` (default enabled) auto-builds every declared index on connect; docs explicitly recommend disabling it in production to avoid performance degradation from index builds on large collections. | `[Source: https://mongoosejs.com/docs/connections.html]` |
| MySQL | Indexing strategy guidance covers B-Tree vs. hash indexes, multi-column indexes, invisible indexes, and descending indexes as levers for query performance. | `[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html]` |
| MySQL | Relying on full table scans instead of appropriate indexes, and using overly wide/inefficient data types, are documented inefficiencies the optimizer's Database Structure/Data Type Optimization sections exist to correct. | `[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html]` |
| Drizzle ORM | Relational query performance guidance centers on indexing: index FK columns on the "many" side of one-to-many relations, index the FK in the target table for one-to-one relations, use both individual and composite indexes for many-to-many junction tables. | `[Source: https://orm.drizzle.team/docs/relations]` |
| Prisma | Missing indexes named as one of the documented common causes of slow queries. | `[Source: https://www.prisma.io/docs/orm/prisma-client/queries/query-optimization-performance]` |
| ClickHouse | The primary key produces a sparse index (one mark per ~8,192-row granule, not per row), keeping primary keys of huge datasets small enough to stay resident in memory while still enabling fast on-disk access. | `[Source: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree]` |
| ClickHouse | Partitioning enables skipping whole irrelevant partitions per query, but the docs explicitly caution that "partitioning does not speed up queries" in general — it is primarily a data-management tool. | `[Source: https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree]` |
| ClickHouse | `minmax`, `set(N)`, `text`, and `bloom_filter` skip indices are a secondary performance layer applied only *after* primary-key/materialized-view optimization; a misaligned skip index adds overhead without benefit. | `[Source: https://clickhouse.com/docs/best-practices/use-data-skipping-indices-where-appropriate]` |
| ClickHouse | `Nullable(T)` stores a hidden `UInt8` is-null mask processed on every access, costing extra storage and "almost always negatively affects performance"; a sensible default value is recommended instead. | `[Source: https://clickhouse.com/docs/optimize/avoid-nullable-columns]` |

---

## 4. Connection Pooling & Client Lifecycle

| Technology | Note | Citation |
|---|---|---|
| Mongoose | `maxPoolSize` (default 100) / `minPoolSize` tuning affects concurrency for slow queries and avoids cold-pool slowdowns after idle periods. | `[Source: https://mongoosejs.com/docs/connections.html]` |
| Mongoose (AWS Lambda) | Documented connection-reuse pattern: cache connection/promise in module scope, set `callbackWaitsForEmptyEventLoop = false`, bound `serverSelectionTimeoutMS`. | `[Source: https://mongoosejs.com/docs/lambda.html]` |
| MongoDB | Connection pool sizing guidance: size the pool at roughly **110–115% of typical concurrent request volume**; low ulimits on file descriptors/processes cause failed connections and outages. | `[Source: https://www.mongodb.com/docs/manual/administration/production-notes/]` |
| Prisma | For high-concurrency workloads an external connection pooler (PgBouncer named) is recommended to avoid exhausting the database's own connection limit; PgBouncer must run in **Transaction mode** for Prisma Client to work reliably (default pooling mode causes "prepared statement s0 already exists" errors). | `[Source: https://www.prisma.io/docs/orm/v7/prisma-client/setup-and-configuration/databases-connections/pgbouncer]` |
| Prisma | A single global `PrismaClient` instance must be reused across the app — multiple instances exhaust the DB connection pool; in serverless, instantiate outside the handler for warm-invocation reuse. | `[Source: https://www.prisma.io/docs/orm/v7/more/best-practices]` |
| Go | `database/sql` exposes connection-pool tuning as a documented integration point relevant to SQL database (e.g. PostgreSQL) performance. | `[Source: https://go.dev/doc/database/index]` |
| Redis | Throughput roughly halves going from ~100 to ~30,000 concurrent connections — relevant to any client's pool-sizing design. | `[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/]` |

**[Synthesis]** Connection-pool right-sizing is independently, and quantitatively, addressed for MongoDB/Mongoose (110–115% of concurrency), Prisma+PgBouncer (external pooler required, specific mode), and Go's `database/sql` — none of these cross-reference each other, but together they indicate pool-size tuning is a first-class step in provisioning any database-backed service regardless of language or ORM.

---

## 5. Bundle Size, Code Splitting & Tree-Shaking

| Technology | Note | Citation |
|---|---|---|
| Next.js | Polyfills (`fetch()`, `URL`, `Object.assign()`) are only shipped to browsers that need them, reducing bundle payload for the majority of global web traffic. | `[Source: https://nextjs.org/docs/architecture/supported-browsers]` |
| Next.js | Bundle-size analysis recommended via `@next/bundle-analyzer` (Webpack) or the Turbopack bundle analyzer, plus third-party tools (Import Cost, Package Phobia, Bundle Phobia, bundlejs). | `[Source: https://nextjs.org/docs/app/guides/production-checklist]` |
| Next.js | `size`/`First Load JS` build-output metrics were removed in v16 because the team found them inaccurate for RSC-based server-driven architectures; Chrome Lighthouse or Vercel Analytics recommended instead. | `[Source: https://nextjs.org/docs/app/guides/upgrading/version-16]` |
| Vue | Tree-shaking unused Vue APIs saves ~14kb (min+gzip); precompiling templates (so the runtime compiler isn't shipped) saves another ~14kb; ESM-friendly dependency builds (e.g. `lodash-es` over `lodash`) recommended for tree-shaking. | `[Source: https://vuejs.org/guide/best-practices/performance.html]` |
| Vue | `petite-vue` (~6kb) is named as a no-build-step alternative for progressive-enhancement scenarios where full Vue's bundle weight is undesirable. | `[Source: https://vuejs.org/guide/best-practices/performance.html]` |
| Vue | Vue-authored Web Components carry a baseline ~16kb runtime-size cost when shipped via `defineCustomElement()`. | `[Source: https://vuejs.org/guide/extras/web-components.html]` |
| Angular | `@defer` is Angular's primary lazy-loading/code-splitting template primitive, reducing initial bundle size via idle/viewport/interaction/hover/timer/immediate triggers plus prefetching; only standalone components/directives/pipes are eligible. | `[Source: https://angular.dev/guide/templates/defer]` |
| MUI (Material UI) | Named/barrel imports from `@mui/icons-material` cause dev-server startup/rebuild slowdowns of "up to six times" versus path (deep) imports — framed as a *development-time* concern, not a production bundle-size problem, since modern bundlers already tree-shake production builds. | `[Source: https://mui.com/material-ui/guides/minimizing-bundle-size/]` |
| MUI | The `sx` prop carries runtime CSS-in-JS overhead scaling with the number of CSS properties passed (negligible under 5); for highly dynamic values, official guidance recommends inline CSS custom properties over an ever-changing `sx` object to avoid inserting new `<style>` tags each render. | `[Source: https://mui.com/system (the-sx-prop.md via GitHub mirror)]` |
| MUI | Material UI v9 claims ~3% bundle-size reduction vs v7 and 30% performance gains for heavy `sx` usage, from removing deprecated props/system-prop plumbing and duplicate-CSS-rule cleanup. | `[Source: https://mui.com/blog/introducing-material-ui-v9/]` |
| Tailwind CSS | The zero-runtime, ahead-of-time generation model means Tailwind ships a single static stylesheet with no client-side style computation/injection overhead, outside dev-only Play CDN mode. | `[Source: https://tailwindcss.com/docs/styling-with-utility-classes]` |
| Tailwind CSS | The Play CDN's runtime style-injection approach is worse for payload size (JS runtime vs. compiled CSS file) and can cause flash-of-unstyled-content for elements added after initial load. | `[Source: https://tailwindcss.com/docs/installation/play-cdn (indirectly, via community/search-derived context)]` |
| shadcn/ui | Since Tailwind v4 adoption, there is no CSS-in-JS runtime: styling is Tailwind utility classes processed at build time, and components use `data-slot` attributes rather than `React.forwardRef` wrapper overhead. | `[Source: https://ui.shadcn.com/docs/tailwind-v4]` |
| shadcn/ui | Because only the components a project actually installs exist in that project's source tree, there is architecturally no library-wide runtime or unused-component bundle cost to opt out of (framed as a philosophy implication, not a benchmarked claim). | `[Source: https://ui.shadcn.com/docs]` |
| Socket.IO | Documented client bundle sizes: unminified/debug build 34.7kB gzip vs. minified production build 14.7kB min+gzip vs. msgpack-parser variant 15.3kB min+gzip; production deployments should use the minified build. | `[Source: https://socket.io/docs/v4/client-installation/]` |
| Socket.IO | The `debug` npm package used for internal logging adds ~4KB minified/gzipped; excluded from the slim browser build, and `webpack-remove-debug` is suggested for stripping it from custom builds. | `[Source: https://socket.io/docs/v4/logging-and-debugging/]` |
| Vite | Production build features (automatic CSS code splitting, preload-directive generation, async-chunk-loading optimization, optional import-map optimization) reduce network round trips and improve cache-hit rates. | `[Source: https://vite.dev/guide/features]` |
| Vite | Explicit file extensions in imports avoid extra filesystem resolution checks; avoiding barrel files avoids fetching/transforming unused re-exported modules; `server.warmup` pre-transforms frequently used files to eliminate import waterfalls. | `[Source: https://vite.dev/guide/performance]` |
| Swagger | Choosing the bundler-friendly `swagger-ui` npm module over the pre-bundled, non-tree-shaken `swagger-ui-dist` is a documented client-payload-size consideration. | `[Source: https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/installation.md]` |
| HTML | The `loading` attribute (`lazy`/`eager`, default `eager`) on img/iframe-class elements formally defers resource fetch until scroll-margin conditions are met. | `[Source: https://html.spec.whatwg.org/multipage/urls-and-fetching.html]` |
| HTML | The `fetchpriority` attribute (`high`/`low`/`auto`) signals a resource's relative fetch priority to the browser's scheduler. | `[Source: https://html.spec.whatwg.org/multipage/urls-and-fetching.html]` |

---

## 6. Horizontal Scaling & Statelessness

| Technology | Note | Citation |
|---|---|---|
| Express | Recommended production pattern runs one process per CPU core via clustering (PM2 / Node.js cluster module), requiring the application to be kept stateless. | `[Source: https://expressjs.com/en/advanced/best-practice-performance.html]` |
| Express | Redis recommended as an externalized session store precisely so the app can remain stateless behind clustering/load balancing. | `[Source: https://expressjs.com/en/advanced/best-practice-performance.html]` |
| MongoDB | For write-heavy workloads, the documented scaling recommendation is **sharding** across multiple `mongod` instances rather than vertical scaling alone. | `[Source: https://www.mongodb.com/docs/manual/administration/analyzing-mongodb-performance/]` |
| Fastify | Capacity planning guidance: ~2 vCPUs per instance for low-latency workloads (GC headroom); smaller/fractional CPU allocations can suffice for high-throughput workloads, validated via load testing (k6, autocannon). | `[Source: https://fastify.dev/docs/latest/Guides/Recommendations/]` |
| Socket.IO | Official `@socket.io/redis-adapter` integration (redis or ioredis client, pub+sub pair, or sharded Pub/Sub on Redis 7.0+) for cross-process broadcast in multi-node deployments. | `[Source: https://socket.io/docs/v4/redis-adapter/]` |
| Socket.IO | Documented officially-supported adapters for multi-node deployments and connection-state recovery on MongoDB and PostgreSQL. | `[Source: https://socket.io/docs/v4/using-multiple-nodes/]` |
| Socket.IO | Documented reverse-proxy/load-balancer integration (Google Cloud Load Balancer) with worked timeout and sticky-session configuration guidance. | `[Source: https://socket.io/docs/v4/reverse-proxy/, https://socket.io/docs/v4/using-multiple-nodes/]` |
| OpenSearch | Performance tuning is organized around thread pool settings, circuit breaker/admission control settings (to prevent OOM), and separating index (write) and search (read) workloads to avoid resource contention. | `[Source: https://docs.opensearch.org/latest/tuning-your-cluster/]` |
| GitHub Actions | Matrix strategies (`strategy.matrix`) parallelize independent test/build permutations across multiple runners simultaneously; `max-parallel` throttles concurrency, `fail-fast` (default true) cancels remaining jobs on first failure. | `[Source: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions]` |
| GitHub Actions | Concurrency and queueing limits act as an upper bound on achievable parallelism per account/plan; hitting them manifests as queued rather than immediately-running jobs. | `[Source: https://docs.github.com/en/actions/concepts/overview/usage-limits-billing-and-administration]` |
| GitHub Actions | GitHub-managed larger runners provide more RAM/CPU/disk (and, for some configs, GPU acceleration) versus standard hosted runners, billed only for execution minutes with no idle cost. | `[Source: https://docs.github.com/en/actions/using-github-hosted-runners/using-larger-runners/about-larger-runners]` |
| Playwright | Primary performance lever is worker-based parallelism: independent OS processes each running an isolated browser instance, configurable via `workers`, with `fullyParallel` enabling intra-file parallel execution. | `[Source: https://playwright.dev/docs/test-parallel]` |
| Playwright | Official CI guidance sets `workers: 1` on constrained runners for stability/reproducibility, then scales throughput via sharding (`--shard=X/Y`) across CI jobs/machines rather than raising in-job concurrency. | `[Source: https://playwright.dev/docs/ci]` |

---

## 7. CDN / Edge Delivery

| Technology | Note | Citation |
|---|---|---|
| Next.js | Cache Components produce a static shell (PPR) servable directly from a CDN without hitting the upstream server. | `[Source: https://nextjs.org/docs/app/getting-started/caching]` |
| Next.js | Nonce-based CSP forces an entire route into dynamic rendering, disabling static optimization and ISR, and is explicitly incompatible with Partial Prerendering (PPR) — a documented performance-security tradeoff. | `[Source: https://nextjs.org/docs/app/guides/content-security-policy]` |
| Nuxt | Hybrid rendering via `routeRules` deploys natively to Netlify/Vercel platform rules when detected. | `[Source: https://nuxt.com/docs/4.x/guide/concepts/rendering]` |
| GraphQL | Persisted queries enable HTTP/CDN caching of otherwise-uncacheable POST requests. | `[Source: https://graphql.org/learn/performance/]` |
| Angular | `NgOptimizedImage` targets Largest Contentful Paint via priority loading, `fetchpriority=high`, preload link generation under SSR, and automatic responsive `srcset` generation, integrating with major CDN image loaders (Cloudinary, Imgix, ImageKit, Netlify, Cloudflare). | `[Source: https://angular.dev/best-practices/images]` |
| Google SEO | Google Search evaluates page experience using three Core Web Vitals thresholds — LCP ≤2.5s, INP <200ms, CLS <0.1 — and states these align with what core ranking systems reward. | `[Source: https://developers.google.com/search/docs/appearance/core-web-vitals]` |
| Google SEO | Crawl rate is deliberately throttled by Google per site to avoid overloading the server — a server-load consideration distinct from Core Web Vitals client-experience metrics. | `[Source: https://developers.google.com/search/docs/fundamentals/how-search-works]` |
| Google SEO | The canonical page in a duplicate cluster is crawled more frequently while duplicates are crawled less, reducing server load. | `[Source: https://developers.google.com/search/docs/crawling-indexing/canonicalization]` |
| Google AdSense | Google ties ad performance to site performance: publishers are directed to use PageSpeed Insights/Web Vitals on the premise a faster, higher-quality site sustains higher ad revenue over time. | `[Source: https://support.google.com/adsense/answer/10760404?hl=en]` |
| Google AdSense | The ad-loading script is designed to load asynchronously (`<script async src=...adsbygoogle.js>`) specifically so it does not block rendering of the rest of the page. | `[Source: https://developers.googleblog.com/2013/07/an-async-script-for-adsense-tagging/]` |
| Three.js | The no-build-tool installation path uses an import map pointing at the jsDelivr CDN (`https://cdn.jsdelivr.net/npm/three@<version>/build/three.module.js`). | `[Source: https://threejs.org/manual/#en/installation]` |
| HTML | The `crossorigin` attribute controls CORS/credentials mode for cross-origin resource requests, relevant to caching behavior and whether a resource can be reused across contexts. | `[Source: https://html.spec.whatwg.org/multipage/urls-and-fetching.html]` |

**Notably thin:** No source in this dataset documents a general-purpose CDN product (Cloudflare, Fastly, CloudFront, Akamai) directly — CDN behavior appears only indirectly, via framework-level static-shell/edge-rule features (Next.js, Nuxt) or image-loader integrations (Angular). Treat CDN-vendor-specific configuration as **not covered**.

---

## 8. Real-Time Transport Overhead

| Technology | Note | Citation |
|---|---|---|
| WebSocket API | The core documented performance limitation of plain WebSocket is the **absence of backpressure**: fast producers can overrun a slow consumer, causing unbounded memory growth or CPU saturation; `WebSocketStream` (via the Streams API) is designed specifically to close this gap. | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API]` |
| WebSocket API | `bufferedAmount` — bytes queued by `send()` but not yet transmitted — is the one performance-relevant introspection point on WebSocket, and polling/checking it is the manual mitigation available to callers wanting to avoid runaway internal buffering. | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket]` |
| WebSocket API | permessage-deflate compression reduces on-wire payload size; disabling context takeover trades worse compression for lower per-connection server memory retained between messages; RFC 7692 recommends an LZ77 window of at least 1,024 bytes for compression to be useful. | `[Source: https://www.rfc-editor.org/rfc/rfc7692.html]` |
| WebSocket API | Because a single WebSocket connection is one long-lived TCP stream, it avoids the per-request overhead (new TCP/TLS handshake, HTTP headers) that repeated HTTP polling would incur — the protocol's foundational performance rationale, though RFC 6455 itself provides no throughput/latency benchmarks. | `[Source: https://www.rfc-editor.org/rfc/rfc6455.html]` |
| Socket.IO | WebSocket has materially lower per-message overhead than HTTP long-polling (which repeats HTTP headers per request); WebTransport is documented as the most efficient transport especially in environments prone to packet loss, though availability is limited. | `[Source: https://socket.io/docs/v4/how-it-works/]` |
| Socket.IO | `socket.volatile.emit()` is the documented mechanism for performance-sensitive, loss-tolerant messages, trading reliability for reduced buffering/backpressure. | `[Source: https://socket.io/docs/v4/emit-cheatsheet/]` |
| Socket.IO | WebSocket permessage-deflate compression defaults to `false` while long-polling `httpCompression` defaults to `true` — compression is not uniform by default, an explicit CPU-vs-bandwidth tradeoff. | `[Source: https://socket.io/docs/v4/server-options/]` |
| Socket.IO | Optional native add-ons `bufferutil`/`utf-8-validate` speed up WebSocket frame operations under the default `ws` engine (falls back to pure-JS if absent); binding to µWebSockets.js (v4.4.0+) is a higher-throughput alternative engine; `@socket.io/bun-engine` exists for Bun-specific optimization. | `[Source: https://socket.io/docs/v4/server-installation/]` |
| WebRTC | `getStats()`/`RTCStatsReport` is the documented mechanism for real-time performance telemetry (bitrate, loss, RTT, jitter, candidate-pair state). | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/getStats]` |
| WebRTC | Outbound data-channel data is auto-buffered; apps should monitor buffered amount via the `bufferedamountlow` event, and keep messages moderately small to avoid head-of-line blocking across channels sharing an SCTP association (absent RFC 8260 message interleaving). | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Using_data_channels]` |
| WebRTC | Codec choice is a performance lever: AV1 and VP9 are named as more bandwidth-efficient than VP8/H.264 at equivalent quality. | `[Source: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs]` |
| Mongoose | `Model.watch()` opens a MongoDB change stream, requiring a replica set or sharded cluster — an infrastructure prerequisite for any real-time change-notification pattern built on Mongoose. | `[Source: https://mongoosejs.com/docs/change-streams.html]` |

**[Synthesis]** Combining the WebSocket API's "no backpressure" limitation with Socket.IO's `volatile.emit()` and the WebRTC data-channel `bufferedamountlow` guidance: every real-time transport layer in this dataset independently re-derives the same problem (an unbounded/unmonitored send buffer) and the same class of fix (either monitor buffered amount and back off, or explicitly opt into lossy/volatile delivery) — none of the individual docs frame this as a shared transport-layer pattern.

---

## 9. Build & Compile Performance

| Technology | Note | Citation |
|---|---|---|
| TypeScript | TypeScript 7.0's Go-native compiler reports **8x–12x speedups** on full builds vs TS 6.x (VS Code's own codebase: 10.6s vs 125.7s), memory down 6–26% depending on project (vendor-reported, not independently corroborated). | `[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/]` |
| TypeScript | Prefer interface extension over intersection types: interface relationships are cached by the checker, intersections are not cached as a whole. | `[Source: https://github.com/microsoft/TypeScript/wiki/Performance]` |
| TypeScript | Base-type/inheritance hierarchies are recommended over large union types because union type comparison is pairwise/quadratic in cost. | `[Source: https://github.com/microsoft/TypeScript/wiki/Performance]` |
| TypeScript | `skipLibCheck: true` skips re-type-checking third-party `.d.ts` files for faster builds, at the cost of not catching some library-declaration inconsistencies. | `[Source: https://github.com/microsoft/TypeScript/wiki/Performance]` |
| TypeScript | `fork-ts-checker-webpack-plugin` runs type-checking asynchronously off Webpack's main emit path; `isolatedModules` lets per-file transpilers (Babel etc.) skip full-program semantic analysis for speed. | `[Source: https://github.com/microsoft/TypeScript/wiki/Performance]` |
| TypeScript | Misconfigured/missing include-exclude glob patterns (e.g. bare `node_modules` instead of `**/node_modules`) are a frequent, avoidable cause of slow compiles and editor slowness. | `[Source: https://github.com/microsoft/TypeScript/wiki/Performance]` |
| TypeScript | The `--stableTypeOrdering` migration flag (ahead of TS 7.0's deterministic ordering) is documented as potentially causing "~25% type-checking slowdown" when enabled. | `[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/]` |
| Vite | Vite 8's unified Rust-based bundler Rolldown delivers "up to 10–30x faster builds" vs the prior Rollup-based pipeline (Linear's build dropped from 46s to 6s; Beehiiv reported a 64% build-time reduction). | `[Source: https://vite.dev/blog/announcing-vite8]` |
| Vite | Preferring native CSS over heavy preprocessors like Sass reduces transform overhead during dev/build. | `[Source: https://vite.dev/guide/performance]` |
| Vite | Vite 8's install size is ~15MB larger than v7, mostly from bundled Lightning CSS (~10MB) and Rolldown (~5MB) native dependencies — a documented consideration for Docker image size and CI cache size. | `[Source: https://vite.dev/blog/announcing-vite8]` |
| Tailwind CSS | v4's rewritten ("Oxide"/Rust) engine: full builds up to ~3.78–5x faster, incremental builds adding new CSS up to ~8.8x faster, incremental no-new-CSS rebuilds up to ~182x faster (microseconds vs milliseconds). | `[Source: https://tailwindcss.com/blog/tailwindcss-v4]` |
| Tailwind CSS | Content-detection watch-mode scanning explicitly skips `.gitignore`'d directories (e.g. `node_modules`, `.git`) rather than walking their full contents. | `[Source: https://tailwindcss.com/docs/detecting-classes-in-source-files]` |
| Tailwind CSS | Combining Tailwind with CSS Modules causes slower build times because "Tailwind runs per module" under that setup, versus a single global stylesheet pass. | `[Source: https://tailwindcss.com/docs/compatibility]` |
| Next.js | Turbopack (default bundler since v16) disk/FileSystem caching plus memory eviction cut dev-server RAM usage up to ~90% and made repeat/CI builds up to 5.5x faster in vendor-reported cases. | `[Source: https://nextjs.org/blog/next-16-3]` |
| Next.js | Replacing web streams with native Node.js streams in the App Router rendering layer let SSR handle up to 22% more requests under load. | `[Source: https://nextjs.org/blog/next-16-3]` |
| Next.js | `next build` can optionally delegate type-checking to TypeScript 7 (`typescript@^7`, `useTypeScriptCli` config) for roughly 10x faster type checking. | `[Source: https://nextjs.org/blog/next-16-3]` |
| Next.js | An experimental Rust-based, Babel-free React Compiler running inside Turbopack cuts `next dev`-to-ready-page time by ~34% cold / ~46% warm, but only if Babel is fully removed from the build. | `[Source: https://nextjs.org/blog/next-16-3]` |
| Sass | Dart Sass compiled to pure JS (the `sass` npm package) provides "a substantial performance boost even for JavaScript"; `sass-embedded` is faster still, running a native Dart VM subprocess. | `[Source: https://sass-lang.com/dart-sass/]` |
| Sass | Synchronous JS API compilation (`compile`/`compileString`) is documented as faster than the asynchronous variants; async exists only to support async custom importers/functions and is "much slower." | `[Source: https://sass-lang.com/documentation/js-api/]` |
| Sass | The legacy async `render()` API is noted as 2–3x slower than `renderSync()`. | `[Source: https://sass-lang.com/blog/node-fibers-discontinued/]` |
| Sass | Historical point-in-time benchmark: Dart Sass ~5–10x faster than Ruby Sass and ~1.5x slower than LibSass for large stylesheets at the time of Dart Sass's original announcement (not a current-version guarantee). | `[Source: https://sass-lang.com/blog/announcing-dart-sass/]` |
| Docker | Multi-platform builds can use QEMU emulation (no Dockerfile changes but much slower for compute-heavy tasks), multiple native builder nodes, or cross-compilation via `BUILDPLATFORM`/`TARGETPLATFORM`; Docker Build Cloud offers managed multi-node builders as an alternative to self-hosting. | `[Source: https://docs.docker.com/build/building/multi-platform/]` |
| Docker | On Apple Silicon, images without native ARM64 support run under QEMU emulation as "best effort" only — emulated containers run slower, use more memory, and `inotify`-based filesystem change notifications do not work under emulation. | `[Source: https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/known-issues/]` |
| Swagger | Swagger Editor documents an out-of-memory build failure fixed by raising Node's heap size (`NODE_OPTIONS="--max_old_space_size=4096"`) when bundling with webpack. | `[Source: https://github.com/swagger-api/swagger-editor]` |
| React | React Compiler (stable v1.0, Oct 7 2025), a build-time Babel plugin, automatically memoizes components/values; Meta-internal production results: initial loads/cross-page navigation improved up to 12%, some interactions up to 2.5x faster, memory neutral. | `[Source: https://react.dev/blog/2025/10/07/react-compiler-1]` |

**[Synthesis]** TypeScript (Go-native compiler), Vite (Rolldown/Rust), and Tailwind CSS (Oxide/Rust) have each, independently, rewritten their core compile pipeline in a systems language and report large (3x–30x) speedups. No single source frames this as an ecosystem trend, but placed together they indicate a broader pattern of JS-tooling migrating CPU-bound compile work off the JS/Node execution model — relevant context for any skill guiding build-tool version upgrades or tool selection.

---

## 10. Runtime, GC & Memory Management

| Technology | Note | Citation |
|---|---|---|
| Go | `GOGC` (default 100) trades memory for CPU in the GC cost model: doubling `GOGC` roughly doubles heap overhead but roughly halves GC CPU cost, and vice versa. | `[Source: https://go.dev/doc/gc-guide]` |
| Go | Green Tea GC (Go 1.26 default) reduces GC overhead by 10–40% (up to an additional ~10% on newer CPU platforms); `io.ReadAll` became ~2x faster with ~50% less allocation, and cgo call overhead dropped ~30% in the same release. | `[Source: https://go.dev/doc/go1.26]` |
| Go | Profile-Guided Optimization (PGO), auto-detected by default since Go 1.21, produced roughly 2–14% performance improvement across representative Go programs as of Go 1.22, primarily via more aggressive inlining. | `[Source: https://go.dev/doc/pgo]` |
| Go | On Linux, for large-heap (≥1 GiB) production workloads, enabling Transparent Huge Pages yields up to ~10% throughput improvement with ~1–2% memory overhead; small heaps may waste up to ~50% extra memory under THP. | `[Source: https://go.dev/doc/gc-guide]` |
| Go | The data race detector (`-race`) carries documented overhead of ~5–10x memory and ~2–20x execution-time slowdown, implying it is a testing/CI-time tool rather than a production configuration. | `[Source: https://go.dev/doc/articles/race_detector.html]` |
| Python | Python 3.12 performance changes: list/dict/set comprehensions inlined (~2x faster, PEP 709); `isinstance()` checks against `typing.Protocol` classes 2–20x faster; asyncio up to 75% faster in some operations; `super()` compiles to a dedicated bytecode. | `[Source: https://docs.python.org/3/whatsnew/3.12.html]` |
| Python | An experimental JIT compiler (PEP 744) was introduced in 3.13 giving "modest" gains; as of 3.14 official macOS/Windows binaries include the experimental JIT. | `[Source: https://docs.python.org/3/whatsnew/3.13.html and https://docs.python.org/3/whatsnew/3.14.html]` |
| Python | Free-threaded (no-GIL) builds carry single-threaded overhead documented as roughly 1–8% depending on platform/workload as of 3.13, narrowed to "roughly 5–10%" in 3.14; they also use more memory (larger object headers, immortal interned strings, mimalloc overhead). | `[Source: https://docs.python.org/3/howto/free-threading-python.html and https://docs.python.org/3/whatsnew/3.14.html]` |
| Python | Python 3.14's opt-in tail-call interpreter loop (`--with-tail-call-interp`, requires Clang 19+ on x86-64/AArch64) shows a geometric mean of 3–5% faster on the pyperformance suite. | `[Source: https://docs.python.org/3/whatsnew/3.14.html]` |
| Python | The GIL limits true multi-core parallelism for standard CPython threads; Python 3.12 (PEP 684) gave sub-interpreters their own independent per-interpreter GIL, and 3.14 (PEP 734) exposed this at the stdlib level via `concurrent.interpreters`. | `[Source: https://docs.python.org/3/whatsnew/3.12.html and https://docs.python.org/3/whatsnew/3.14.html]` |
| Redis | Redis is fundamentally single-threaded for command execution, favoring fast single-core CPU performance over core count; Redis 8.0 introduced a multi-core I/O threading implementation (`io-threads`) that parallelizes I/O handling even though command execution logic remains single-threaded. | `[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/]` |
| Three.js | "Each 1024x1024 texture takes 4 to 6meg of memory" once decompressed for GPU use regardless of on-disk compressed size, motivating explicit disposal patterns. | `[Source: https://threejs.org/manual/#en/cleanup]` |
| Three.js | For static scenes, "rendering continuously is a waste of the device's power and if the user is on portable device it wastes the user's battery" — render-on-demand recommended instead of continuous `requestAnimationFrame`. | `[Source: https://threejs.org/manual/#en/rendering-on-demand]` |
| Three.js | `renderer.info` holds GPU memory/draw-call statistics and resets every render call by default; docs recommend `renderer.info.autoReset = false` plus manual `reset()` for multi-pass (post-processing) rendering. | `[Source: https://threejs.org/docs/pages/WebGLRenderer.html.md]` |

---

## 11. Rendering & Reactivity Performance (Frontend Frameworks)

| Technology | Note | Citation |
|---|---|---|
| React | `memo` skips re-rendering when props are shallowly equal (`Object.is` per-prop); new object/array/function literals created fresh each parent render defeat `memo` even with unchanged contents; it is never a guarantee and does not prevent re-renders from the component's own state or consumed context changes. | `[Source: https://react.dev/reference/react/memo]` |
| React | `useMemo` is recommended only for calculations empirically shown slow (rule-of-thumb roughly ≥1ms measured on a representative/slower device in production mode) with rarely-changing dependencies; not a semantic guarantee since React may discard cached values. | `[Source: https://react.dev/reference/react/useMemo]` |
| React | React reveals suspended content at most once every 300ms from the last reveal so multiple boundaries appear together; in 19.2 this batching was extended to SSR and uses a heuristic that stops batching as the page nears the ~2.5s LCP threshold. | `[Source: https://react.dev/reference/react/Suspense]` |
| React | React 19.2 added a Scheduler Track and a Components Track to Chrome DevTools' Performance panel specifically for profiling React apps. | `[Source: https://react.dev/blog/2025/10/01/react-19-2]` |
| React | Resource preloading APIs `prefetchDNS`, `preconnect`, `preload`, `preinit` (React 19) let apps imperatively hint the browser to fetch scripts/fonts/stylesheets/connections ahead of when they're rendered. | `[Source: https://react.dev/blog/2024/12/05/react-19]` |
| Vue | Compiler-Informed Virtual DOM optimizations (Cache Static hoisting via `innerHTML`, bitwise Patch Flags, Tree Flattening into per-block dynamic-node arrays) let the patch algorithm skip static subtrees and avoid full diffing. | `[Source: https://vuejs.org/guide/extras/rendering-mechanism.html]` |
| Vue | The same compiler optimizations accelerate SSR hydration, achieving "partial hydration at the template level" since only block nodes and their dynamic descendants are traversed. | `[Source: https://vuejs.org/guide/extras/rendering-mechanism.html]` |
| Vue | Lists of "1000+ items" should be virtualized using community libraries (vue-virtual-scroller etc.) since Vue ships no first-party virtualization primitive. | `[Source: https://vuejs.org/guide/best-practices/performance.html]` |
| Vue | `shallowRef()`/`shallowReactive()` avoid deep-reactivity overhead for very large, effectively-immutable datasets, at the cost of losing reactivity to in-place nested mutation. | `[Source: https://vuejs.org/guide/best-practices/performance.html]` |
| Vue | As of Vue 3.4, `computed()` only re-triggers dependents when its return value actually changed (not on every re-evaluation), reducing needless downstream re-renders. | `[Source: https://vuejs.org/guide/best-practices/performance.html]` |
| Vue | Recommended profiling: PageSpeed Insights/WebPageTest for field profiling; Chrome DevTools' Performance panel (with `app.config.performance = true`) and Vue Devtools' profiling feature for local/dev profiling; LCP and INP are the named Core Web Vitals to track. | `[Source: https://vuejs.org/guide/best-practices/performance.html]` |
| Vue | Production SSR requires planning for server CPU load (string rendering is CPU-intensive at scale) and a caching strategy; avoid pure client-rendered SPAs for load-sensitive pages — use SSR or SSG instead. | `[Source: https://vuejs.org/guide/scaling-up/ssr.html] / [Source: https://vuejs.org/guide/best-practices/performance.html]` |
| Angular | As of v22, components with an undefined `changeDetection` property now default to `OnPush` (previously Zone-checked "Default"), limiting re-render checks to inputs/signal changes/events rather than every zone-detected tick. | `[Source: https://raw.githubusercontent.com/angular/angular/main/CHANGELOG.md (v22.0.0 entry)]` |
| Angular | Zoneless (stable/default v21+) is explicitly framed as a performance feature yielding fewer unnecessary change-detection cycles and "improved Core Web Vitals" from removing Zone.js's monkey-patch overhead. | `[Source: https://angular.dev/guide/zoneless]` |
| Angular | Per-route Server/Client/Prerender rendering-mode selection is a documented performance/architecture lever, alongside automatic transfer of cached HTTP GET/HEAD responses from server to browser during hydration to avoid redundant initial-load requests. | `[Source: https://angular.dev/guide/ssr]` |
| CSS | Containment (the `contain` property) lets authors declare a subtree independent from the rest of the page so the browser can skip layout/paint/style work outside that subtree when only the subtree changes. | `[Source: https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Using]` |
| CSS | `content-visibility: auto` builds on containment to skip layout and paint for off-screen content while keeping it in the DOM/accessibility tree (unlike `display:none`); web.dev reports up to a **7x** rendering-performance improvement on initial load for long, chunked pages. | `[Source: https://web.dev/articles/content-visibility]` |
| CSS | `will-change` is an explicit rendering-optimization hint, but MDN warns overuse causes excessive memory consumption and slower rendering rather than improving it — should be applied only as a targeted, temporary, last-resort fix and removed afterward. | `[Source: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/will-change]` |
| CSS | An element must have `container-type` set (establishing size containment) before it can be queried via `@container` — container queries are a containment-driven performance mechanism, not just a layout convenience. | `[Source: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@container]` |
| Three.js | "Every Mesh you create...represents 1 or more requests by the system to draw something. Drawing 2 things has more overhead than drawing 1" — documented mitigation is merging geometry via `BufferGeometryUtils.mergeGeometries()`. | `[Source: https://threejs.org/manual/#en/optimize-lots-of-objects]` |
| Three.js | Toggling "structural" material properties (texture presence, fog, vertex colors, morphing, shadow map, alpha test) after first render forces `material.needsUpdate = true` and a full shader-program recompile, documented as "quite slow" and worse on Windows (DirectX shader compilation slower than OpenGL). | `[Source: https://threejs.org/manual/#en/how-to-update-things]` |
| Three.js | `logarithmicDepthBuffer` uses `gl_FragDepth` if available, which disables the Early Fragment Test optimization and can decrease performance for huge-scale scenes. | `[Source: https://threejs.org/docs/pages/WebGLRenderer.html.md]` |

---

## 12. Bulk Data, Batch Writes & Pagination

| Technology | Note | Citation |
|---|---|---|
| Prisma | Recommended mitigation for slow bulk writes: batched bulk operations (e.g. inserting 50,000 records in batches of 1,000) rather than row-by-row writes. | `[Source: https://www.prisma.io/docs/orm/prisma-client/queries/query-optimization-performance]` |
| Prisma | Cursor-based pagination is recommended for large/growing datasets because it uses indexed columns to find the starting position instead of traversing skipped rows; offset pagination is acceptable only for small datasets needing arbitrary page jumps. | `[Source: https://www.prisma.io/docs/orm/v7/more/best-practices]` |
| TypeORM | Cursor-based pagination is recommended over plain offset/limit pagination for "more efficient handling of dynamic data" on large or frequently changing result sets. | `[Source: https://typeorm.io/docs/performance-optimization/pagination/]` |
| Mongoose | `save()` on an existing document sends an `updateOne()` containing only modified paths, not the full document, as an efficiency property of Mongoose's change tracking. | `[Source: https://mongoosejs.com/docs/documents.html]` |
| PostgreSQL | Bulk-load performance guidance (COPY over INSERT, deferred index/FK creation, larger `maintenance_work_mem`/`max_wal_size`) is a distinct performance topic from steady-state query tuning. | `[Source: https://www.postgresql.org/docs/current/populate.html]` |
| MySQL | Bulk data loading techniques are recommended over row-by-row inserts for large data imports, alongside redo-log tuning for bulk-load/DDL-heavy workloads. | `[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html]` |
| ClickHouse | Batch inserts of 10,000–100,000 rows (minimum ~1,000) at roughly 1 insert/sec are recommended; frequent small inserts create excess parts and background-merge pressure; async inserts (`async_insert=1, wait_for_async_insert=1`) shift buffering to the server for high-cardinality small-payload producers. | `[Source: https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy]` |

---

## 13. Analytical / OLAP-Scale Query Performance

| Technology | Note | Citation |
|---|---|---|
| MongoDB | Aggregation pipeline stages default to a 100MB per-stage memory limit; `allowDiskUse` permits spilling to disk for larger operations, but only `$bucket`, `$bucketAuto`, `$group`, `$setWindowFields`, `$sort`, and `$sortByCount` can spill. | `[Source: https://www.mongodb.com/docs/manual/aggregation/]` |
| ClickHouse | JOIN performance depends on deliberately choosing an algorithm (direct/dictionary, parallel hash, grace hash, partial merge, sort-merge) by table size/memory budget, keeping JOIN count to roughly 3–4 per query, and avoiding disk-spilling joins which "significantly degrades performance." | `[Source: https://clickhouse.com/docs/best-practices/minimize-optimize-joins]` |
| ClickHouse | Approximate distinct-count and quantile/median functions are a documented performance/accuracy trade-off mechanism for very large datasets. | `[Source: https://clickhouse.com/docs/about-us/distinctive-features]` |
| OpenSearch | Shard sizing is a first-class performance lever: 10–30GB shards recommended for search-latency-sensitive workloads, 30–50GB for write-heavy/analytics workloads; too many small shards wastes JVM heap on per-shard metadata, too few large shards limits parallelization. | `[Source: https://opensearch.org/blog/optimize-opensearch-index-shard-size/]` |
| OpenSearch | JVM heap should be set to roughly 50% of available system RAM with `-Xms` equal to `-Xmx`, up to a practical ~32GB ceiling to preserve compressed-oops efficiency (configured via `config/jvm.options`). | `[Inference from opensearch.md, not an explicit doc statement — search-indexed snippets corroborate but full page body was not retrieved verbatim]` |
| OpenSearch | OpenSearch Benchmark is the official performance-testing tool: runs defined workloads against a cluster, supports custom workloads, corpus generation, telemetry, target-throughput config, and distributed load generation. | `[Source: https://docs.opensearch.org/latest/tools/benchmark/]` |
| PostgreSQL | Synchronous replication guarantees no data loss on failover but may significantly impact performance (>50% slowdown over slow networks); asynchronous replication has minimal performance impact but risks data loss/stale reads. | `[Source: https://www.postgresql.org/docs/current/high-availability.html]` |

---

## 14. API Payload & Schema Compilation Performance

| Technology | Note | Citation |
|---|---|---|
| Fastify | Ajv v8 and fast-json-stringify both compile JSON Schemas into specialized functions ahead of request handling rather than interpreting schemas at runtime; schemas can be shared/deduplicated via `addSchema()`. | `[Source: https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/]` |
| Fastify | Defining response schemas accelerates JSON serialization via fast-json-stringify; keeping Ajv's `allErrors` disabled by default avoids a documented performance cost. | `[Source: https://fastify.dev/docs/latest/Guides/Recommendations/]` |
| Fastify | Route-matching performance guidance: prefer static/simple parametric routes over regex-based routes; version constraints and async custom constraints degrade routing performance. | `[Source: https://fastify.dev/docs/latest/Guides/Recommendations/]` |
| Fastify | Homepage benchmark: Fastify 5.11.3 ~88,171 req/s vs Express 5.2.1 ~57,936 req/s, Koa ~57,214, Hapi ~59,754, H3 ~82,683, Hono ~82,371 — roughly 1.5x Express's throughput; flagged as vendor-published marketing figures, not independently reproduced. | `[Source: https://fastify.dev/]` |
| GraphQL | Response compression (GZIP) is recommended since GraphQL's JSON/text payloads compress well. | `[Source: https://graphql.org/learn/performance/]` |
| OpenAPI | No dedicated performance section exists for the specification itself (a static document format, not runnable software); the one performance-adjacent point is a tooling-capability constraint: tools that resolve `$ref` in-memory as a graph can process any valid OAD, while tools that resolve by physically substituting references can only handle documents whose reference structure forms a tree. | `[Source: https://learn.openapis.org/referencing/resolve.html]` |
| Swagger | Swagger UI v5.0.0 release notes cite performance optimizations for sub-tree expansion in complex schemas, indicating deeply-nested-schema rendering is an actively tuned performance area. | `[Source: https://github.com/swagger-api/swagger-ui/releases/tag/v5.0.0]` |

---

## 15. Testing & CI/CD Performance

| Technology | Note | Citation |
|---|---|---|
| Jest | Jest 30 rewrote module resolution on `unrs-resolver`; a cited real-world TypeScript-app benchmark showed ~37% faster server tests (~1350s to ~850s) and ~77% lower memory usage (7.8GB to 1.8GB) after upgrading from v29. | `[Source: https://jestjs.io/blog/2025/06/04/jest-30] [VERSION-SENSITIVE]` |
| Jest | Test execution is parallelized across worker processes via `jest-worker`; `maxWorkers` controls pool size (default CPU-cores-minus-one); `--runInBand` disables parallelism entirely for debugging at the cost of throughput. | `[Source: https://jestjs.io/docs/cli, https://jestjs.io/docs/configuration]` |
| Jest | `--detectOpenHandles` carries an explicitly documented performance penalty, intended only for diagnosing dangling handles, not routine runs. | `[Source: https://jestjs.io/docs/cli]` |
| Jest | Since Jest 27, `testEnvironment` defaults to `'node'` instead of `'jsdom'` specifically because jsdom carries meaningful per-test performance overhead unnecessary for non-DOM code. | `[VERSION-SENSITIVE, Source: https://jestjs.io/blog/2021/05/25/jest-27]` |
| Vitest | Pool choice is the primary performance lever: `forks` (default, safest, can be slower), `threads` (often faster, more native-module/timer edge cases), `vmThreads` (best amortized cost for DOM-heavy suites but isolation cannot be disabled). | `[Source: https://vitest.dev/guide/improving-performance.html]` |
| Vitest | Disabling test isolation improves speed for suites that reliably clean up their own state, but isolation cannot be turned off under `vmThreads`. | `[Source: https://vitest.dev/guide/improving-performance.html]` |
| Vitest | Coverage provider trade-off: V8 provider has no pre-transpile step (faster, lower memory, limited to V8-based runtimes) with report accuracy "as good as with Istanbul (since Vitest v3.2.0)"; Istanbul instruments source before execution (works on any JS runtime, higher memory overhead). | `[Source: https://vitest.dev/guide/coverage.html]` |
| Vitest | `--shard=X/Y` combined with `--reporter=blob` and a later `--merge-reports` step distributes large suites across parallel CI machines. | `[Source: https://vitest.dev/guide/cli.html]` |
| Vitest | `happy-dom` is recommended over `jsdom` when full DOM fidelity isn't required because it is cheaper to instantiate. | `[Source: https://vitest.dev/guide/improving-performance.html]` |
| Playwright | Video recording is off by default and adds overhead only when enabled; default recorded video dimensions are downscaled to a max of 800x800 to control file size. | `[Source: https://playwright.dev/docs/videos]` |
| Playwright | Auto-waiting/actionability checks trade a small configurable per-action wait budget for reduced flakiness versus fixed `sleep()`-style waits. | `[Source: https://playwright.dev/docs/actionability]` |
| Playwright | `retryStrategy: 'isolated'` runs retries after all other tests complete to reduce cross-test interference; `maxFailures` bounds wasted CI time by stopping after N failures. | `[Source: https://playwright.dev/docs/api/class-testconfig]` |
| Playwright | Recommended container flags for Chromium stability include `--init` (avoid zombie processes) and `--ipc=host` (shared-memory stability), affecting reliability more than raw speed. | `[Source: https://playwright.dev/docs/docker]` |
| Angular | Running tests in Node.js with jsdom or happy-dom for DOM emulation speeds up execution by avoiding real-browser overhead compared to Karma's real-browser test execution. | `[Source: https://angular.dev/guide/testing]` |
| Husky | Package size "Just 2kB (gzipped) with no dependencies," execution overhead "runs in ~1ms," attributed to using native `core.hooksPath` instead of a heavier wrapper mechanism. | `[Source: https://typicode.github.io/husky/]` |
| Husky | The pre-v6 architecture (all hooks installed into `.git/hooks/`, each checking a JS config at runtime) was wasteful because "Node started unnecessarily for undefined hooks" — every configured Git hook paid a Node.js startup cost even with no user logic for that hook. | `[Source: https://blog.typicode.com/posts/husky-git-hooks-javascript-config/]` |
| Husky | v9.1.1 added invoking locally installed package binaries directly by name inside hook scripts without an `npx` prefix — an approximately 0.2-second performance improvement per invocation. | `[Source: https://api.github.com/repos/typicode/husky/releases (v9.1.1 entry, paraphrased from the release notes)]` |
| GitHub Actions | `actions/upload-artifact` and `download-artifact` v4 introduced a new content-addressable storage backend, making artifact downloads "10x faster on average" versus v3. | `[Source: https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/]` |

---

## 16. Profiling, Monitoring & Benchmarking Tooling

| Technology | Note | Citation |
|---|---|---|
| PostgreSQL | `EXPLAIN` / `EXPLAIN (ANALYZE, BUFFERS)` is the documented primary tool for diagnosing query performance, comparing estimated vs. actual row counts and buffer hit/read counts. | `[Source: https://www.postgresql.org/docs/current/using-explain.html]` |
| PostgreSQL | Ongoing performance monitoring relies on `pg_stat_activity`, `pg_stat_user_tables`/`indexes`, `pg_statio_*`, and `pg_stat_io` (expanded in v18) views. | `[Source: https://www.postgresql.org/docs/current/monitoring-stats.html]` |
| MySQL | `EXPLAIN` (including extended/JSON formats) is named as the primary tool for understanding optimizer execution plans, with optimizer hints and index hints as the mechanism for overriding suboptimal plans. | `[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html]` |
| MySQL | Performance Schema and the MySQL `sys` schema (convenience views over Performance Schema) are the documented facilities for runtime performance monitoring, distinct from `EXPLAIN`'s static plan analysis. | `[Source: https://dev.mysql.com/doc/refman/9.7/en/optimization.html]` |
| Python | `cProfile` (C-extension, low overhead) and `profile` (pure Python, higher overhead) are the standard deterministic profilers, post-processed via `pstats.Stats`; docs distinguish profiling from benchmarking (`timeit`). | `[Source: https://docs.python.org/3/library/profile.html]` |
| Python | Python 3.12 introduced `sys.monitoring` (PEP 669), a low-overhead event-monitoring API so debuggers/profilers/coverage tools no longer need the much higher-overhead `sys.settrace()`. | `[Source: https://docs.python.org/3/whatsnew/3.12.html]` |
| Python | CPython can interoperate with the Linux `perf` profiler (Python-level symbols in perf output) as of Python 3.12+, via `-X perf`/`-X perf_jit` or `PYTHONPERFSUPPORT=1`. | `[Source: https://docs.python.org/3/howto/perf_profiling.html]` |
| Go | The data race detector (`-race`) is the primary Go-native concurrency-correctness profiling tool, at documented cost of ~5–10x memory and ~2–20x execution-time slowdown. | `[Source: https://go.dev/doc/articles/race_detector.html]` |
| Fastify | First-party benchmarking recommends `autocannon` plus `branch-comparer` to measure the performance effect of an app's own changes across git branches / Node.js versions. | `[Source: https://fastify.dev/docs/latest/Guides/Benchmarking/]` |
| Redis | `getStats()`-equivalent tooling: the docs' latency-monitor and benchmarks pages are the primary official performance-diagnosis references (single-threaded model, connection scaling, VM-vs-bare-metal). | `[Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency-monitor/] / [Source: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/]` |
| WebRTC | `getStats()`/`RTCStatsReport` provides per-connection and per-sender/receiver stats: bitrate, loss, RTT, jitter, candidate-pair state. | `[Source: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/getStats]` |
| Vue | Chrome DevTools' Performance panel (with `app.config.performance = true` emitting Vue-specific markers) and Vue Devtools' profiling feature are the recommended local/dev profiling tools; PageSpeed Insights/WebPageTest for field profiling. | `[Source: https://vuejs.org/guide/best-practices/performance.html]` |
| React | Chrome DevTools' Scheduler Track (work by priority) and Components Track (render/effect timing), added in React 19.2, are purpose-built for profiling React apps. | `[Source: https://react.dev/blog/2025/10/01/react-19-2]` |
| TypeScript | `tsc --generateTrace` output is documented as analyzable with the official `@typescript/analyze-trace` tool or Chrome DevTools' trace viewer. | `[Source: https://github.com/microsoft/TypeScript/wiki/Performance]` |
| OpenSearch | OpenSearch Benchmark is the official performance-testing tool, used to validate cluster performance before/after upgrades or mapping/query changes. | `[Source: https://docs.opensearch.org/latest/tools/benchmark/]` |
| GitHub | REST API primary rate limits: unauthenticated 60/hour; authenticated (PAT) 5,000/hour; GHEC 15,000/hour; Git LFS separate limits (300/min unauthenticated, 3,000/min authenticated). | `[Source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api]` |
| GitHub | Secondary rate limits cap concurrent requests at 100, enforce a 900 points/minute per-endpoint minimum, and a CPU-time budget of 90 seconds CPU time per 60 seconds wall time; exposed via `x-ratelimit-*` headers. | `[Source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api]` |
| GitHub | GraphQL API is point-based: standard users get 5,000 points/hour, secondary limit 2,000 points/minute; queries cannot exceed 500,000 total nodes; execution capped at 10 seconds. | `[Source: https://docs.github.com/en/graphql/overview/resource-limitations]` |
| GitHub | Conditional requests (ETag/`If-None-Match`, `Last-Modified`/`If-Modified-Since`) avoid consuming primary rate limit on unchanged resources; serial (not concurrent) mutating requests, spaced ≥1 second apart, avoid secondary rate limits. | `[Source: https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api]` |
| GitHub | Repositories should ideally be less than 1GB (less than 5GB strongly recommended) to avoid degrading GitHub's own infrastructure performance; `github/git-sizer` is the documented audit tool. | `[Source: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github]` |

**Not covered:** ClickHouse's data in this dataset offers no dedicated query-profiling/EXPLAIN-equivalent tooling note beyond the indexing/JOIN/insert-strategy guidance already listed elsewhere.

---

## 17. Cross-Cutting Synthesis: Patterns Visible Only Across Sources

These are inferences drawn by combining two or more individually-stated facts; none of the underlying sources states the pattern itself.

1. **Redis as universal connective tissue.** TypeORM's Redis/IORedis query-cache backend, Drizzle's Upstash Redis caching layer, Express's Redis session/cache recommendation, graphql-js's Redis external-cache mention, and Socket.IO's `@socket.io/redis-adapter` for cross-process broadcast are five independent integration points across data, API, and real-time layers that all reach for the same technology. **[Synthesis: combining these five facts — none of which reference each other — shows Redis functioning as the default cross-layer performance/coordination primitive across most of this stack.]**

2. **"Fix the N+1" recurs at every data-access layer with a different name.** See Section 2 — Mongoose's `select`/avoid-`perDocumentLimit`, TypeORM's `leftJoinAndSelect`, Prisma's `include`/`relationLoadStrategy:'join'`, and GraphQL's DataLoader are the same underlying fix restated per-technology.

3. **"Disable a development-mode default before shipping" recurs across unrelated stacks.** Express's `NODE_ENV=production` (~3x perf per Express's own benchmark), Mongoose's `autoIndex` (recommended off in production), and Three.js's `debug.checkShaderErrors` (recommended off in production) are three independent instances of the same architectural pattern: a convenience default that measurably costs performance and must be explicitly turned off for production. **[Synthesis: this is not stated as a shared pattern by any of the three sources.]**

4. **Sync beats async for CPU-bound compile/transform work, repeatedly.** Sass's synchronous JS API is documented faster than its async variants (with the legacy `render()` 2–3x slower than `renderSync()`), and Vitest's `forks` pool (safe, can be slower) vs `threads`/`vmThreads` tradeoff echoes the same sync/async-overhead theme in a different tool. **[Synthesis: independently documented per-tool, but the shape of the tradeoff — async plumbing costs throughput even when it doesn't change correctness — repeats.]**

5. **Native/systems-language rewrites are an ecosystem-wide trend, not an isolated event.** See Section 9's synthesis note — TypeScript (Go), Vite (Rust/Rolldown), and Tailwind CSS (Rust/Oxide) each independently made this move with similar-shaped 3x–30x speedup claims.

6. **Connection-pool sizing is treated as a first-class provisioning step regardless of stack.** See Section 4's synthesis note — MongoDB/Mongoose, Prisma+PgBouncer, and Go's `database/sql` all carry dedicated, quantified pool-sizing guidance.

7. **Real-time transports converge on the same "unbounded send buffer" hazard.** See Section 8's synthesis note — WebSocket API's lack of backpressure, Socket.IO's `volatile.emit()`, and WebRTC's `bufferedamountlow` event all name variations of the same problem.

---

## 18. What This Data Does Not Cover

Stated explicitly per the task instructions rather than inferred:

- **General-purpose CDN vendors** (Cloudflare, Fastly, CloudFront, Akamai) are not documented as standalone technologies in this dataset — CDN behavior surfaces only through framework-level edge features (Next.js Cache Components, Nuxt `routeRules`) or image-loader integrations (Angular `NgOptimizedImage`).
- **Message queues / event streaming performance** (Kafka, RabbitMQ, SQS) — MongoDB's Kafka Connector integration is listed under `integratesWith` but carries no performance-specific note in this extraction.
- **Load balancer configuration performance** beyond Express's high-level recommendation to offload to Nginx/HAProxy/Varnish and Socket.IO's sticky-session guidance — no dedicated load-balancer technology appears in this dataset.
- **ClickHouse query-plan/EXPLAIN tooling** — indexing, JOIN, and insert-strategy guidance is present, but no diagnostic/profiling tool equivalent to Postgres's `EXPLAIN` or MySQL's Performance Schema is documented for it here.
- **Node.js runtime-level performance** (V8 tuning, event-loop diagnostics) is not present as its own technology entry in this dataset; Node.js appears only as an integration target for other technologies (Fastify, Express, Sass, TypeScript, WebSocket API, Husky).
- **HTML/OpenAPI specs are explicitly self-described as performance-silent.** The HTML Living Standard "does not itself publish network-level performance benchmarks or numeric performance targets" `[Source: https://html.spec.whatwg.org/multipage/introduction.html]`, and OpenAPI "No dedicated performance section exists for the specification itself (it is a static document format, not runnable software)" `[Source: https://learn.openapis.org/referencing/resolve.html]`.
- **ECMAScript** performance content is limited to a meta-observation: "ECMA-262 specifies observable language semantics only, not performance characteristics; actual execution strategy... is fully implementation-defined and left to individual engines" `[Inference from ecmascript.md, not an explicit doc statement]` — i.e., the spec itself is deliberately performance-silent by design.
