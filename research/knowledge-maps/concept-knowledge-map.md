# Concept Knowledge Map

This map inverts the per-technology research: instead of "what does React do," it answers
**"what technologies touch caching?"**, **"what implements realtime communication?"**, or
**"what touches row-level security?"** — spanning unrelated categories (databases, frontend
frameworks, testing tools, CI/CD, styling, SEO).

**Source and method.** Built from a pre-trimmed extract of `research/technologies/*.md`
covering 44 technologies, each with a `category`, `coreConcepts`, and `relatedConcepts` list.
This document groups by engineering concept, normalizing near-duplicate phrasings (e.g. "SSR"
and "server-side rendering" become one entry). Every fact traces back to a technology's
`relatedConcepts` field; because the trimmed data file does not carry per-field citations, each
row is cited uniformly as `[research/technologies/<slug>.md, relatedConcepts]`. No relationship
below was invented — if a technology isn't listed under a concept, the source data didn't
relate it to that concept. Passages marked **[Synthesis: ...]** are inferences this document
draws by combining two or more individually-stated facts; they are not present verbatim in the
source data and should be read as informed connections, not extracted facts.

**Scope note.** 7 AI coding-agent ecosystem write-ups (`research/agent-ecosystems/*.md`) exist
in this project but were *not* part of the data file supplied for this map — the 44-technology
extract is the entire input. Nothing below draws on the agent-ecosystem research.

---

## Contents

- [A. Data Persistence & Databases](#a-data-persistence--databases)
- [B. APIs, Schemas & Contracts](#b-apis-schemas--contracts)
- [C. Rendering, Frontend Architecture & State](#c-rendering-frontend-architecture--state)
- [D. Styling, Design Systems & UI Components](#d-styling-design-systems--ui-components)
- [E. Realtime, Networking & Communication](#e-realtime-networking--communication)
- [F. Type Systems & Language Design](#f-type-systems--language-design)
- [G. Software Architecture Patterns](#g-software-architecture-patterns)
- [H. Testing & Quality Automation](#h-testing--quality-automation)
- [I. DevOps, CI/CD, Build & Containerization](#i-devops-cicd-build--containerization)
- [J. Security & Access Control](#j-security--access-control)
- [K. SEO, Growth & Monetization](#k-seo-growth--monetization)
- [L. Cross-Cutting Synthesis](#l-cross-cutting-synthesis)
- [M. Singleton / Technology-Specific Concepts](#m-singleton--technology-specific-concepts)
- [N. Gaps & Silences in the Data](#n-gaps--silences-in-the-data)

---

## A. Data Persistence & Databases

### ORM / Object-(Relational|Document) Mapping — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| Mongoose | Object-**document** mapping layer over MongoDB (Schema/Model/Document/Population) | [research/technologies/mongoose.md, relatedConcepts] |
| TypeORM | ORM supporting both Active Record and Data Mapper patterns simultaneously | [research/technologies/typeorm.md, relatedConcepts] |
| Prisma | ORM built around a generated, type-safe query builder derived from a schema | [research/technologies/prisma.md, relatedConcepts] |
| Drizzle ORM | Headless "if you know SQL, you know Drizzle" TypeScript ORM | [research/technologies/drizzle-orm.md, relatedConcepts] |

### Schema Validation — 8 technologies

| Technology | How it relates | Source |
|---|---|---|
| Mongoose | Schema defines document shape and enforces types (SchemaTypes) | [research/technologies/mongoose.md, relatedConcepts] |
| MongoDB | Native schema validation feature despite flexible schema model | [research/technologies/mongodb.md, relatedConcepts] |
| Fastify | JSON Schema drives both request/response validation and serialization | [research/technologies/fastify.md, relatedConcepts] |
| Drizzle ORM | Schema validation listed alongside its TypeScript-schema-as-source-of-truth model | [research/technologies/drizzle-orm.md, relatedConcepts] |
| OpenAPI | JSON Schema validation is a named related concept of the spec format | [research/technologies/openapi.md, relatedConcepts] |
| GraphQL | Strong type system/schema validates operations before execution | [research/technologies/graphql.md, relatedConcepts] |
| Swagger | Swagger Editor validates OpenAPI-spec syntax live as the user types | [research/technologies/swagger.md, relatedConcepts] |
| OpenSearch | Mapping defines field types/analyzers per index, schema-validation-like role | [research/technologies/opensearch.md, relatedConcepts] |

### Connection Pooling — 9 technologies

| Technology | How it relates | Source |
|---|---|---|
| Mongoose | Manages a pooled connection to MongoDB | [research/technologies/mongoose.md, relatedConcepts] |
| MongoDB | Server-side support for pooled client connections | [research/technologies/mongodb.md, relatedConcepts] |
| Fastify | Related concept for backend services holding DB connections | [research/technologies/fastify.md, relatedConcepts] |
| TypeORM | Pools connections beneath its EntityManager/Repository abstractions | [research/technologies/typeorm.md, relatedConcepts] |
| Prisma | Prisma Client manages a connection pool to the datasource | [research/technologies/prisma.md, relatedConcepts] |
| Drizzle ORM | Pooling relevant despite Drizzle's zero-runtime-dependency footprint | [research/technologies/drizzle-orm.md, relatedConcepts] |
| Go | Related to Go's DB-driver-level connection handling | [research/technologies/go.md, relatedConcepts] |
| Redis | Client-side connection pooling to the in-memory server | [research/technologies/redis.md, relatedConcepts] |
| ClickHouse | Connection pooling paired explicitly with wire-protocol emulation | [research/technologies/clickhouse.md, relatedConcepts] |

### NoSQL / Document Data Model — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Mongoose | Provides the ODM layer specifically for a NoSQL (document) database | [research/technologies/mongoose.md, relatedConcepts] |
| MongoDB | The document-oriented data model (BSON) is the database itself | [research/technologies/mongodb.md, relatedConcepts] |

### Relational Database / SQL — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| MySQL | Canonical RDBMS; data lives in related tables accessed via SQL | [research/technologies/mysql.md, relatedConcepts] |
| ClickHouse | Offers SQL compatibility as an interface over its columnar/OLAP engine | [research/technologies/clickhouse.md, relatedConcepts] |

*Note: PostgreSQL's entry does not list "relational database" as a related-concept string in
the trimmed data (its core concepts describe MVCC, WAL, and its type system instead), so it is
omitted here to avoid inventing a relationship not present in the source — see Part N.*

### ACID Transactions — 6 technologies

| Technology | How it relates | Source |
|---|---|---|
| Mongoose | Related concept for multi-document write consistency | [research/technologies/mongoose.md, relatedConcepts] |
| PostgreSQL | Full ACID guarantees underpinned by MVCC and WAL | [research/technologies/postgresql.md, relatedConcepts] |
| MongoDB | Multi-document ACID transactions supported natively | [research/technologies/mongodb.md, relatedConcepts] |
| TypeORM | Transaction management sits atop the EntityManager | [research/technologies/typeorm.md, relatedConcepts] |
| Redis | Offers **atomic** transactions via MULTI/EXEC/DISCARD/WATCH — lighter than full ACID | [research/technologies/redis.md, relatedConcepts] |
| MySQL | ACID transactions are a core RDBMS guarantee | [research/technologies/mysql.md, relatedConcepts] |

### Database Migrations / Schema Evolution — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| TypeORM | Schema migrations plus schema synchronization as an alternate mode | [research/technologies/typeorm.md, relatedConcepts] |
| Prisma | Prisma Migrate turns schema changes into versioned SQL migration files | [research/technologies/prisma.md, relatedConcepts] |
| Drizzle ORM | TypeScript schema is the single source of truth for generated migrations | [research/technologies/drizzle-orm.md, relatedConcepts] |
| MySQL | Schema/version upgrade management as an operational concern | [research/technologies/mysql.md, relatedConcepts] |

### Query Optimization & Planning — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| PostgreSQL | SQL query planning/optimization plus index-based optimization | [research/technologies/postgresql.md, relatedConcepts] |
| Prisma | Prisma Client's generated queries are a related optimization surface | [research/technologies/prisma.md, relatedConcepts] |
| MySQL | Query optimization is core to the RDBMS engine | [research/technologies/mysql.md, relatedConcepts] |

### N+1 Query Problem — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| TypeORM | Named directly as a related concept (a classic ORM pitfall) | [research/technologies/typeorm.md, relatedConcepts] |
| Prisma | "N+1 query prevention" listed as a related concept | [research/technologies/prisma.md, relatedConcepts] |
| GraphQL | "N+1 query problem / request batching" tied to resolver-per-field execution | [research/technologies/graphql.md, relatedConcepts] |

### Caching — 8 technologies (spans DB, frontend rendering, and CI layers)

| Technology | How it relates | Source |
|---|---|---|
| TypeORM | Query result caching as a built-in feature | [research/technologies/typeorm.md, relatedConcepts] |
| Drizzle ORM | Caching listed among its related concepts | [research/technologies/drizzle-orm.md, relatedConcepts] |
| Redis | Canonical in-memory cache; one of Redis's headline use cases | [research/technologies/redis.md, relatedConcepts] |
| Next.js | Caching is core to its rendering/data model | [research/technologies/nextjs.md, relatedConcepts] |
| Nuxt | Stale-while-revalidate caching pattern for rendered/fetched content | [research/technologies/nuxt.md, relatedConcepts] |
| GraphQL | Caching listed as related to query response handling | [research/technologies/graphql.md, relatedConcepts] |
| Docker | Build/layer caching speeds up image builds | [research/technologies/docker.md, relatedConcepts] |
| GitHub Actions | Dependency caching speeds up workflow runs | [research/technologies/github-actions.md, relatedConcepts] |

### Database Replication — 5 technologies

| Technology | How it relates | Source |
|---|---|---|
| PostgreSQL | Physical and logical replication for HA and PITR | [research/technologies/postgresql.md, relatedConcepts] |
| MongoDB | Replica sets for redundancy | [research/technologies/mongodb.md, relatedConcepts] |
| MySQL | Replication as a standard HA building block | [research/technologies/mysql.md, relatedConcepts] |
| ClickHouse | Asynchronous multi-master replication across replicas | [research/technologies/clickhouse.md, relatedConcepts] |
| Redis | Leader-follower replication | [research/technologies/redis.md, relatedConcepts] |

### Sharding / Horizontal Scaling — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| MongoDB | Horizontal scaling via sharding is a named related concept | [research/technologies/mongodb.md, relatedConcepts] |
| OpenSearch | Shards distribute an index's data across nodes for horizontal scaling | [research/technologies/opensearch.md, relatedConcepts] |
| Redis | Horizontal sharding for scaling beyond one node's RAM | [research/technologies/redis.md, relatedConcepts] |
| Socket.IO | "Horizontal scaling" listed for scaling realtime connections across servers | [research/technologies/socketio.md, relatedConcepts] |

### Full-Text Search — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| PostgreSQL | Built-in full-text search capability | [research/technologies/postgresql.md, relatedConcepts] |
| Redis | Full-text search among its multi-model capabilities | [research/technologies/redis.md, relatedConcepts] |
| OpenSearch | Full-text search is the platform's primary purpose | [research/technologies/opensearch.md, relatedConcepts] |

### Vector / Semantic Search — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Redis | Vector similarity search; Redis doubles as a vector database | [research/technologies/redis.md, relatedConcepts] |
| OpenSearch | Semantic/vector search alongside classic full-text search | [research/technologies/opensearch.md, relatedConcepts] |

### Aggregation Pipeline / OLAP Analytics — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| MongoDB | Aggregation framework: $match/$group/$unwind/$sort/$lookup/$merge/$out pipelines | [research/technologies/mongodb.md, relatedConcepts] |
| ClickHouse | Purpose-built column-oriented DBMS for OLAP analytical queries | [research/technologies/clickhouse.md, relatedConcepts] |

### Indexing Strategy — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| PostgreSQL | Index-based query optimization is a named related concept | [research/technologies/postgresql.md, relatedConcepts] |
| MySQL | Indexing strategy as a core performance lever | [research/technologies/mysql.md, relatedConcepts] |
| ClickHouse | Uses sparse indexing rather than dense B-tree indexes | [research/technologies/clickhouse.md, relatedConcepts] |

### Distributed Query Processing — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| ClickHouse | Distributed query processing across replica/shard topology | [research/technologies/clickhouse.md, relatedConcepts] |
| OpenSearch | Distributed search and analytics across a cluster of nodes | [research/technologies/opensearch.md, relatedConcepts] |

### Row-Level Security — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| PostgreSQL | Native row-level security policies | [research/technologies/postgresql.md, relatedConcepts] |
| Prisma | Row-level security listed as a related concept (works with DB-native RLS) | [research/technologies/prisma.md, relatedConcepts] |
| Drizzle ORM | Row-level security listed as a related concept | [research/technologies/drizzle-orm.md, relatedConcepts] |

### Encryption at Rest — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| MongoDB | Encryption at rest plus field-level encryption | [research/technologies/mongodb.md, relatedConcepts] |
| MySQL | Encryption at rest / key management | [research/technologies/mysql.md, relatedConcepts] |

### Backup & Restore / Point-in-Time Recovery — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| PostgreSQL | WAL underpins point-in-time recovery and crash recovery | [research/technologies/postgresql.md, relatedConcepts] |
| MySQL | Database backup and recovery, including PITR | [research/technologies/mysql.md, relatedConcepts] |

---

## B. APIs, Schemas & Contracts

### REST API — 7 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Built for building REST APIs with schema-based validation | [research/technologies/fastify.md, relatedConcepts] |
| Docker | Docker Engine exposes a REST API alongside the CLI | [research/technologies/docker.md, relatedConcepts] |
| OpenAPI | Describes REST API design as its primary use case | [research/technologies/openapi.md, relatedConcepts] |
| OpenSearch | REST API is the primary client interface | [research/technologies/opensearch.md, relatedConcepts] |
| Swagger | Tooling built around REST APIs described via OpenAPI | [research/technologies/swagger.md, relatedConcepts] |
| GitHub | REST API alongside its GraphQL API | [research/technologies/github.md, relatedConcepts] |
| Google AdSense | AdSense Management API is a REST reporting/management API | [research/technologies/google-adsense.md, relatedConcepts] |

### API Specification / Description Format — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| OpenAPI | Is itself the vendor-neutral, machine-readable API description format | [research/technologies/openapi.md, relatedConcepts] |
| Swagger | Consumes and visualizes the OpenAPI/Swagger spec rather than defining it | [research/technologies/swagger.md, relatedConcepts] |

### API Documentation Generation — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Generates OpenAPI documentation from route schemas | [research/technologies/fastify.md, relatedConcepts] |
| OpenAPI | Enables auto-generated docs as one of its stated purposes | [research/technologies/openapi.md, relatedConcepts] |
| Swagger | Swagger UI renders interactive, browsable docs directly from an OpenAPI document | [research/technologies/swagger.md, relatedConcepts] |

### Code Generation (schema/API-driven) — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| Prisma | Schema-driven code generation produces the type-safe Prisma Client | [research/technologies/prisma.md, relatedConcepts] |
| OpenAPI | Enables server/client codegen from the API description | [research/technologies/openapi.md, relatedConcepts] |
| Swagger | Swagger Codegen generates client SDKs and server stubs from a spec | [research/technologies/swagger.md, relatedConcepts] |
| shadcn/ui | A scaffolding CLI generates component code into the consumer's project | [research/technologies/shadcn-ui.md, relatedConcepts] |

### Mock Server Generation — 1 technology (see Part M)

### OAuth2 / Authorization Flows — 5 technologies

| Technology | How it relates | Source |
|---|---|---|
| OpenAPI | Declarative API security scheme description covers OAuth2 flows | [research/technologies/openapi.md, relatedConcepts] |
| Swagger | OAuth2 authorization flow listed as a related concept | [research/technologies/swagger.md, relatedConcepts] |
| GitHub | OAuth authorization for third-party app access | [research/technologies/github.md, relatedConcepts] |
| Google SEO | OAuth 2.0 authentication for Search Console / related Google APIs | [research/technologies/google-seo.md, relatedConcepts] |
| Google AdSense | OAuth2 authentication required for the Management API | [research/technologies/google-adsense.md, relatedConcepts] |

### GraphQL Query Language — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| GraphQL | Is itself the client-specified-response-shape query language | [research/technologies/graphql.md, relatedConcepts] |
| GitHub | Offers a GraphQL API as an alternative to its REST API | [research/technologies/github.md, relatedConcepts] |

### Cursor-Based Pagination — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Prisma | Cursor-based pagination listed as a related concept | [research/technologies/prisma.md, relatedConcepts] |
| GraphQL | Cursor-based pagination is a common connection-pattern idiom | [research/technologies/graphql.md, relatedConcepts] |

---

## C. Rendering, Frontend Architecture & State

### Server-Side Rendering (SSR) — 9 technologies

| Technology | How it relates | Source |
|---|---|---|
| Express | Server-side rendering via template engines | [research/technologies/express.md, relatedConcepts] |
| React | SSR is a named related concept of the rendering model | [research/technologies/react.md, relatedConcepts] |
| Nuxt | Universal Rendering (SSR + hydration) is Nuxt's default mode | [research/technologies/nuxt.md, relatedConcepts] |
| Next.js | React Server Components stream server-rendered output to the client | [research/technologies/nextjs.md, relatedConcepts] |
| Vue | Server-side rendering supported as one of Vue's deployment modes | [research/technologies/vue.md, relatedConcepts] |
| Angular | Server-side rendering paired with hydration/event replay | [research/technologies/angular.md, relatedConcepts] |
| MUI | Server-side rendering compatibility listed as a related concept | [research/technologies/mui-material-ui.md, relatedConcepts] |
| Vite | Server-side rendering supported via its dev/build pipeline | [research/technologies/vite.md, relatedConcepts] |
| Google SEO | Server-side rendering relevant to how Googlebot indexes JS-rendered pages | [research/technologies/google-seo.md, relatedConcepts] |

### Static Site Generation (SSG) — 7 technologies

| Technology | How it relates | Source |
|---|---|---|
| React | SSG listed as a related rendering strategy | [research/technologies/react.md, relatedConcepts] |
| Nuxt | Static site generation is one of Nuxt's rendering modes | [research/technologies/nuxt.md, relatedConcepts] |
| Next.js | Static site generation supported alongside SSR/ISR | [research/technologies/nextjs.md, relatedConcepts] |
| Vue | Static site generation listed as a related concept | [research/technologies/vue.md, relatedConcepts] |
| Angular | Static site generation listed as a related concept | [research/technologies/angular.md, relatedConcepts] |
| Vite | Static site generation supported via its build pipeline | [research/technologies/vite.md, relatedConcepts] |
| Three.js | "Static site deployment" listed for shipping WebGL scenes as static assets | [research/technologies/threejs.md, relatedConcepts] |

### Hydration — 5 technologies

| Technology | How it relates | Source |
|---|---|---|
| React | Hydration listed as a related concept of SSR | [research/technologies/react.md, relatedConcepts] |
| Nuxt | Hydration is the second half of Universal Rendering | [research/technologies/nuxt.md, relatedConcepts] |
| Next.js | Hydration reconciles the RSC payload against the prerendered HTML | [research/technologies/nextjs.md, relatedConcepts] |
| Vue | "SSR hydration" listed explicitly | [research/technologies/vue.md, relatedConcepts] |
| Angular | Hydration and Event Replay reuse the server-rendered DOM | [research/technologies/angular.md, relatedConcepts] |

### Incremental Static Regeneration (ISR) — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Nuxt | Incremental static regeneration listed as a related concept | [research/technologies/nuxt.md, relatedConcepts] |
| Next.js | Incremental static regeneration is a named rendering strategy | [research/technologies/nextjs.md, relatedConcepts] |

### Streaming Rendering — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| React | Streaming rendering listed as a related concept | [research/technologies/react.md, relatedConcepts] |
| Next.js | Streaming listed, tied to the Suspense/PPR model | [research/technologies/nextjs.md, relatedConcepts] |

### Client-Side Rendering — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Three.js | Client-side rendering of WebGL/WebGPU scenes in the browser | [research/technologies/threejs.md, relatedConcepts] |
| Google SEO | Client-side rendering relevant to how Google's indexer executes JS | [research/technologies/google-seo.md, relatedConcepts] |

### Component-Based Architecture — 6 technologies

| Technology | How it relates | Source |
|---|---|---|
| React | Component-based UI architecture is the framework's foundation | [research/technologies/react.md, relatedConcepts] |
| Nuxt | Component-based architecture (auto-imported, tree-shaken) | [research/technologies/nuxt.md, relatedConcepts] |
| Next.js | Component-based UI listed as a related concept | [research/technologies/nextjs.md, relatedConcepts] |
| Vue | Component-based architecture built on Single-File Components | [research/technologies/vue.md, relatedConcepts] |
| Angular | Component-based architecture (TypeScript class + template + selector) | [research/technologies/angular.md, relatedConcepts] |
| Tailwind CSS | "Component-based UI reuse" listed for extracting repeated utility patterns | [research/technologies/tailwind-css.md, relatedConcepts] |

### Reactive State Management — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Nuxt | State management listed as a related concept | [research/technologies/nuxt.md, relatedConcepts] |
| Vue | Reactive state management via Proxy-based reactivity primitives | [research/technologies/vue.md, relatedConcepts] |
| Angular | Reactive state management, notably via Signals | [research/technologies/angular.md, relatedConcepts] |

### Virtual DOM / Reconciliation — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| React | Reconciliation / tree diffing is React's core update mechanism | [research/technologies/react.md, relatedConcepts] |
| Vue | Virtual DOM listed as a related concept | [research/technologies/vue.md, relatedConcepts] |

### Code Splitting / Lazy Loading — 5 technologies

| Technology | How it relates | Source |
|---|---|---|
| Nuxt | Automatic code-splitting for reduced initial load | [research/technologies/nuxt.md, relatedConcepts] |
| Next.js | Code splitting listed as a related concept | [research/technologies/nextjs.md, relatedConcepts] |
| Vue | Code splitting / lazy loading listed as a related concept | [research/technologies/vue.md, relatedConcepts] |
| Angular | Code splitting / lazy loading listed as a related concept | [research/technologies/angular.md, relatedConcepts] |
| HTML | Native `lazy loading` (e.g. images/iframes) at the markup level | [research/technologies/html.md, relatedConcepts] |

### File-Based / Client-Side Routing — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Nuxt | File-based routing from `app/pages/` | [research/technologies/nuxt.md, relatedConcepts] |
| Next.js | File-system routing via `app/` directory conventions | [research/technologies/nextjs.md, relatedConcepts] |
| Angular | Client-side routing via the Angular Router (Routes/Outlets/Links) | [research/technologies/angular.md, relatedConcepts] |

---

## D. Styling, Design Systems & UI Components

### Design System / Theming — 5 technologies

| Technology | How it relates | Source |
|---|---|---|
| MUI | Centralized theming via `ThemeProvider` distributing a theme object | [research/technologies/mui-material-ui.md, relatedConcepts] |
| Tailwind CSS | Design system tokens are the basis of its utility classes | [research/technologies/tailwind-css.md, relatedConcepts] |
| shadcn/ui | Design system delivered as copy-in source rather than a package | [research/technologies/shadcn-ui.md, relatedConcepts] |
| Sass | "Variables and theming" via SassScript variables (compile-time, not runtime) | [research/technologies/sass.md, relatedConcepts] |
| CSS | Theming via design tokens (CSS custom properties) natively | [research/technologies/css.md, relatedConcepts] |

### Responsive Design — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| MUI | Responsive design listed as a related concept | [research/technologies/mui-material-ui.md, relatedConcepts] |
| Tailwind CSS | Responsive breakpoint variants (`sm:`, `md:`, `lg:`) stack on utility classes | [research/technologies/tailwind-css.md, relatedConcepts] |
| CSS | Responsive design listed as a related concept | [research/technologies/css.md, relatedConcepts] |
| Google AdSense | Responsive design relevant to adaptive auto ad placement | [research/technologies/google-adsense.md, relatedConcepts] |

### Dark Mode Theming — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Tailwind CSS | `dark:` variant stacks with state/responsive variants on one class | [research/technologies/tailwind-css.md, relatedConcepts] |
| shadcn/ui | Dark mode theming listed as a related concept | [research/technologies/shadcn-ui.md, relatedConcepts] |

### Accessibility (a11y) — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| HTML | Accessibility listed as a related concept of semantic markup | [research/technologies/html.md, relatedConcepts] |
| MUI | Accessibility listed as a related concept | [research/technologies/mui-material-ui.md, relatedConcepts] |
| shadcn/ui | Accessibility (a11y) semantics listed as a related concept | [research/technologies/shadcn-ui.md, relatedConcepts] |
| Playwright | Accessibility-tree-based automation drives its locator/action model | [research/technologies/playwright.md, relatedConcepts] |

### Component Library — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| MUI | Is itself an open-source React component library (Material Design) | [research/technologies/mui-material-ui.md, relatedConcepts] |
| shadcn/ui | Positions itself as a code-distribution platform, explicitly *not* an installable component library — an intentional contrast to MUI's model | [research/technologies/shadcn-ui.md, relatedConcepts] |

### Tree Shaking — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Vue | Tree-shaking listed as a related concept | [research/technologies/vue.md, relatedConcepts] |
| MUI | Tree shaking listed as a related concept | [research/technologies/mui-material-ui.md, relatedConcepts] |
| Tailwind CSS | Content-detection scans source files and tree-shakes unused utility classes | [research/technologies/tailwind-css.md, relatedConcepts] |

### Form Validation — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Angular | Reactive Forms, Template-Driven Forms, and Signal Forms all handle validation | [research/technologies/angular.md, relatedConcepts] |
| shadcn/ui | Form validation listed as a related concept | [research/technologies/shadcn-ui.md, relatedConcepts] |

### Content Security Policy (CSP) — 4 technologies

*(Also see Part J — Security.)*

| Technology | How it relates | Source |
|---|---|---|
| Next.js | Content security policy listed as a related concept | [research/technologies/nextjs.md, relatedConcepts] |
| Angular | Content security policy listed as a related concept | [research/technologies/angular.md, relatedConcepts] |
| HTML | Content security policy is a markup/header-level enforcement mechanism | [research/technologies/html.md, relatedConcepts] |
| MUI | Content security policy listed as a related concept (relevant to CSS-in-JS `nonce` handling) | [research/technologies/mui-material-ui.md, relatedConcepts] |

### Cross-Site Scripting (XSS) Prevention — 4 technologies

*(Also see Part J — Security.)*

| Technology | How it relates | Source |
|---|---|---|
| React | XSS prevention / output sanitization built into JSX rendering | [research/technologies/react.md, relatedConcepts] |
| Vue | XSS prevention / output escaping in template rendering | [research/technologies/vue.md, relatedConcepts] |
| HTML | Cross-site scripting (XSS) prevention listed as a related concept | [research/technologies/html.md, relatedConcepts] |
| Swagger | XSS sanitization relevant to rendering untrusted API descriptions in Swagger UI | [research/technologies/swagger.md, relatedConcepts] |

### Web Components / Custom Elements — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Vue | Custom elements / web components interoperability listed | [research/technologies/vue.md, relatedConcepts] |
| HTML | Custom elements are a native HTML extensibility mechanism | [research/technologies/html.md, relatedConcepts] |

### Progressive Enhancement / Feature Detection — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Nuxt | Progressive enhancement listed as a related concept | [research/technologies/nuxt.md, relatedConcepts] |
| Three.js | Feature detection / progressive enhancement for WebGL/WebGPU capability gaps | [research/technologies/threejs.md, relatedConcepts] |
| CSS | Progressive enhancement / feature detection listed as a related concept | [research/technologies/css.md, relatedConcepts] |

---

## E. Realtime, Networking & Communication

### Realtime Communication — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| WebRTC | Peer-to-peer audio/video/data communication is WebRTC's core purpose | [research/technologies/webrtc.md, relatedConcepts] |
| WebSocket API | Two-way interactive communication without polling | [research/technologies/websocket-api.md, relatedConcepts] |
| Socket.IO | Bidirectional, low-latency, event-based client-server communication | [research/technologies/socketio.md, relatedConcepts] |
| GraphQL | Subscriptions provide long-lived, real-time operations | [research/technologies/graphql.md, relatedConcepts] |

### Bidirectional / Full-Duplex Communication — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| WebSocket API | Full-duplex, bidirectional communication over one persistent TCP connection | [research/technologies/websocket-api.md, relatedConcepts] |
| Socket.IO | Bidirectional communication built atop WebSocket (and fallback transports) | [research/technologies/socketio.md, relatedConcepts] |

### Publish/Subscribe Messaging — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Redis | Publish/subscribe messaging is one of Redis's core capabilities | [research/technologies/redis.md, relatedConcepts] |
| Socket.IO | Publish-subscribe messaging listed alongside event-driven messaging | [research/technologies/socketio.md, relatedConcepts] |

### Connection Lifecycle Management — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| WebSocket API | Explicit readyState state machine: CONNECTING → OPEN → CLOSING → CLOSED | [research/technologies/websocket-api.md, relatedConcepts] |
| Socket.IO | Connection state recovery after automatic reconnection | [research/technologies/socketio.md, relatedConcepts] |

### Reverse Proxy / Load Balancing — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Deployed behind a reverse proxy pattern in production | [research/technologies/fastify.md, relatedConcepts] |
| Express | Reverse proxy / load balancing listed as a related concept | [research/technologies/express.md, relatedConcepts] |
| MySQL | Connection routing / load balancing across replicas | [research/technologies/mysql.md, relatedConcepts] |
| Socket.IO | Reverse proxy / load balancer deployment; needs sticky sessions | [research/technologies/socketio.md, relatedConcepts] |

### Serverless / Edge Deployment — 5 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Serverless deployment listed as a related concept | [research/technologies/fastify.md, relatedConcepts] |
| Prisma | Serverless/edge runtime compatibility, notably via WASM query compilation | [research/technologies/prisma.md, relatedConcepts] |
| Drizzle ORM | Zero-dependency footprint makes it serverless/edge-ready | [research/technologies/drizzle-orm.md, relatedConcepts] |
| Nuxt | Edge computing via the Nitro server engine | [research/technologies/nuxt.md, relatedConcepts] |
| Next.js | Edge computing listed as a related concept | [research/technologies/nextjs.md, relatedConcepts] |

---

## F. Type Systems & Language Design

### Type Safety — 18 technologies (the single most cross-cutting concept in this dataset)

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Type safety listed as a related concept | [research/technologies/fastify.md, relatedConcepts] |
| TypeORM | Type safety listed as a related concept | [research/technologies/typeorm.md, relatedConcepts] |
| Prisma | Prisma Client is a generated, type-safe query builder | [research/technologies/prisma.md, relatedConcepts] |
| Drizzle ORM | Type safety derived from the TypeScript schema as source of truth | [research/technologies/drizzle-orm.md, relatedConcepts] |
| Express | Type safety via community type definitions (not built-in) | [research/technologies/express.md, relatedConcepts] |
| React | Type safety listed as a related concept | [research/technologies/react.md, relatedConcepts] |
| Python | Type safety is opt-in and static-only — not enforced at runtime | [research/technologies/python.md, relatedConcepts] |
| Nuxt | Zero-config TypeScript support drives type safety | [research/technologies/nuxt.md, relatedConcepts] |
| Next.js | Type safety listed as a related concept | [research/technologies/nextjs.md, relatedConcepts] |
| Vue | Type safety listed as a related concept | [research/technologies/vue.md, relatedConcepts] |
| Three.js | Type safety via community-maintained type definitions | [research/technologies/threejs.md, relatedConcepts] |
| Angular | Type safety listed as a related concept | [research/technologies/angular.md, relatedConcepts] |
| TypeScript | Is itself the static type-checker superset that provides type safety to JS | [research/technologies/typescript.md, relatedConcepts] |
| GraphQL | Type safety flows from its strong schema/type system | [research/technologies/graphql.md, relatedConcepts] |
| MUI | Type safety listed as a related concept | [research/technologies/mui-material-ui.md, relatedConcepts] |
| CSS | Type safety listed as a related concept (tooling-dependent, e.g. typed CSS modules) | [research/technologies/css.md, relatedConcepts] |
| Vite | Type safety listed as a related concept | [research/technologies/vite.md, relatedConcepts] |
| Socket.IO | Type safety listed as a related concept | [research/technologies/socketio.md, relatedConcepts] |

**[Synthesis:** combining TypeScript's role as *the* static type-checker with its appearance as a
related concept across nearly every ORM (TypeORM, Prisma, Drizzle), every major frontend
framework (React, Vue, Angular, Next.js, Nuxt), and even a graphics library (Three.js) and a
realtime library (Socket.IO), the data shows TypeScript functioning as connective tissue across
this entire technology landscape rather than a "frontend language" — 17 of the other 43
technologies in this dataset list type safety as a related concept, and TypeScript is the only
technology whose core purpose *is* that concept.]

### Static Typing / Structural Typing — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Go | Statically/strongly typed with structural (implicit) interface satisfaction | [research/technologies/go.md, relatedConcepts] |
| TypeScript | Static type checking; also a structural (duck-typed) type system | [research/technologies/typescript.md, relatedConcepts] |

**[Synthesis:** Go and TypeScript both list "structural typing" independently, even though they
sit in entirely different categories (programming-language vs. language-spec) and are used in
unrelated layers of a typical stack (backend services vs. compile-time JS tooling) — the data
suggests structural typing is a design choice that recurs even when languages aren't related by
lineage.]

### Concurrency Model — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Go | Goroutines and channels as first-class concurrency primitives | [research/technologies/go.md, relatedConcepts] |
| Python | Concurrency listed as a related concept (constrained by the GIL per its core concepts) | [research/technologies/python.md, relatedConcepts] |
| ECMAScript | Concurrency model via jobs/microtask queues and shared-memory agents | [research/technologies/ecmascript.md, relatedConcepts] |

### Garbage Collection / Memory Management — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Go | Garbage collection listed as a related concept | [research/technologies/go.md, relatedConcepts] |
| Python | Garbage collection / memory management listed as a related concept | [research/technologies/python.md, relatedConcepts] |

### Package / Dependency Management — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Go | Module dependency management is a core Go tooling concern | [research/technologies/go.md, relatedConcepts] |
| Python | Package management and dependency isolation via virtual environments | [research/technologies/python.md, relatedConcepts] |
| Husky | npm lifecycle scripts (`prepare`) are how Husky installs itself | [research/technologies/husky.md, relatedConcepts] |

### Performance Profiling / Optimization — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Go | Profile-guided optimization as a build/runtime concept | [research/technologies/go.md, relatedConcepts] |
| Python | Profiling and performance analysis listed as a related concept | [research/technologies/python.md, relatedConcepts] |

### Module System — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Sass | Module system / namespacing via `@use`/`@forward`/`@import` | [research/technologies/sass.md, relatedConcepts] |
| ECMAScript | Module system and dynamic `import()` are part of the language spec | [research/technologies/ecmascript.md, relatedConcepts] |
| Vite | ES Modules (ESM) are the transformation/serving unit for its dev server | [research/technologies/vite.md, relatedConcepts] |

### Internationalization (i18n) — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Google SEO | Internationalization / localization via `hreflang` | [research/technologies/google-seo.md, relatedConcepts] |
| ECMAScript | Internationalization (i18n) listed as a related concept | [research/technologies/ecmascript.md, relatedConcepts] |

---

## G. Software Architecture Patterns

### Middleware / Interceptor Pattern (HTTP & ORM hooks) — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| Mongoose | Middleware (pre/post hooks) on document, query, aggregate, and model operations | [research/technologies/mongoose.md, relatedConcepts] |
| Fastify | Middleware and lifecycle hooks listed as related concepts | [research/technologies/fastify.md, relatedConcepts] |
| Express | Middleware pipeline architecture is Express's central request-handling model | [research/technologies/express.md, relatedConcepts] |
| Socket.IO | Middleware-based authentication for connection handshakes | [research/technologies/socketio.md, relatedConcepts] |

**[Synthesis:** the "middleware" pattern recurs at two different layers of a typical stack —
Mongoose applies it to *data* operations (pre/post save hooks) while Express, Fastify, and
Socket.IO apply the same request/response-pipeline idea to *network* operations — the data
doesn't state this explicitly but the shared vocabulary across an ODM and three
network-facing libraries points to one interceptor pattern reused at different altitudes.]

### Plugin / Extension Architecture — 5 technologies

| Technology | How it relates | Source |
|---|---|---|
| PostgreSQL | `CREATE EXTENSION` as a first-class packaging mechanism for types/functions/index methods | [research/technologies/postgresql.md, relatedConcepts] |
| Fastify | Plugins registered via `register()` are the primary code-organization mechanism | [research/technologies/fastify.md, relatedConcepts] |
| MySQL | Pluggable storage engine architecture | [research/technologies/mysql.md, relatedConcepts] |
| Swagger | Plugin architecture listed as a related concept | [research/technologies/swagger.md, relatedConcepts] |
| Vite | Plugin API extends its opinionated defaults | [research/technologies/vite.md, relatedConcepts] |

### Dependency Injection — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Dependency injection via decoration onto instance/Request/Reply | [research/technologies/fastify.md, relatedConcepts] |
| Angular | Dependency injection (`inject()`, hierarchical injectors) is a core Angular pattern | [research/technologies/angular.md, relatedConcepts] |
| Playwright | Fixture-based dependency injection supplies test context (Browser/Context/Page) | [research/technologies/playwright.md, relatedConcepts] |

### Client/Server Architecture — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| PostgreSQL | Connection-per-process client/server architecture | [research/technologies/postgresql.md, relatedConcepts] |
| Docker | Docker Engine is a client-server system (dockerd daemon + CLI client) | [research/technologies/docker.md, relatedConcepts] |

### Explicit Error Handling & Exception Propagation — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Go | Explicit error handling via multi-value `(value, error)` returns | [research/technologies/go.md, relatedConcepts] |
| Python | Exception handling and error propagation via `raise ... from` chaining | [research/technologies/python.md, relatedConcepts] |

**[Synthesis:** Go and Python are the two general-purpose programming languages in this dataset,
and they arrive at opposite philosophies for the same problem — Go's related concepts describe
explicit multi-value error returns (no exceptions), while Python's describe exception-based
propagation — making them a natural point of comparison for anyone choosing a backend language,
even though neither technology's write-up frames it as a contrast.]

### Graceful Shutdown — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Graceful shutdown listed as a related concept | [research/technologies/fastify.md, relatedConcepts] |
| Express | Graceful shutdown listed as a related concept | [research/technologies/express.md, relatedConcepts] |

---

## H. Testing & Quality Automation

### Test Automation (general) — 12 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Test automation listed as a related concept | [research/technologies/fastify.md, relatedConcepts] |
| React | Test automation listed as a related concept | [research/technologies/react.md, relatedConcepts] |
| Python | Test automation listed as a related concept | [research/technologies/python.md, relatedConcepts] |
| Vue | Test automation listed as a related concept | [research/technologies/vue.md, relatedConcepts] |
| Next.js | Test automation listed as a related concept | [research/technologies/nextjs.md, relatedConcepts] |
| Angular | Test automation listed as a related concept | [research/technologies/angular.md, relatedConcepts] |
| Socket.IO | Test automation listed as a related concept | [research/technologies/socketio.md, relatedConcepts] |
| Husky | Test automation triggered via pre-commit/pre-push hooks | [research/technologies/husky.md, relatedConcepts] |
| Playwright | Combines test runner, assertion library, and reporting | [research/technologies/playwright.md, relatedConcepts] |
| Vitest | Test automation listed as a related concept | [research/technologies/vitest.md, relatedConcepts] |
| Jest | Test automation listed as a related concept | [research/technologies/jest.md, relatedConcepts] |
| GitHub Actions | Test automation listed as a related concept (runs test suites as CI jobs) | [research/technologies/github-actions.md, relatedConcepts] |

### Unit Testing / Mocking & Stubbing — spans 4+ technologies

| Technology | How it relates | Source |
|---|---|---|
| Prisma | Unit test mocking listed as a related concept | [research/technologies/prisma.md, relatedConcepts] |
| Vitest | Jest-compatible mocking via the `vi` object; unit testing is a core use case | [research/technologies/vitest.md, relatedConcepts] |
| Jest | Built-in mocking (`jest.fn()`, `jest.mock()`, `jest.spyOn()`) and test doubles | [research/technologies/jest.md, relatedConcepts] |
| Playwright | Network request interception/mocking for isolating tests from real backends | [research/technologies/playwright.md, relatedConcepts] |

### Snapshot Testing — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Vitest | Snapshot testing listed as a related concept (Jest-compatible) | [research/technologies/vitest.md, relatedConcepts] |
| Jest | Snapshot testing (output compared against committed `.snap` files) | [research/technologies/jest.md, relatedConcepts] |

### Code Coverage — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Vitest | Code coverage listed as a related concept | [research/technologies/vitest.md, relatedConcepts] |
| Jest | Code coverage listed as a related concept | [research/technologies/jest.md, relatedConcepts] |

### Test Parallelization / Sharding — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Playwright | Parallel test execution and test sharding listed as related concepts | [research/technologies/playwright.md, relatedConcepts] |
| Vitest | Test parallelization / sharding across multiple execution pools | [research/technologies/vitest.md, relatedConcepts] |
| Jest | Parallel test execution listed as a related concept | [research/technologies/jest.md, relatedConcepts] |

### End-to-End / Browser Automation Testing — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Playwright | End-to-end testing and browser automation are its core purpose | [research/technologies/playwright.md, relatedConcepts] |
| Vitest | Browser-based testing via its native Browser Mode | [research/technologies/vitest.md, relatedConcepts] |

### Component Testing — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Playwright | Component testing listed as a related concept | [research/technologies/playwright.md, relatedConcepts] |
| Vitest | Component testing listed as a related concept | [research/technologies/vitest.md, relatedConcepts] |

### Visual Regression Testing — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Three.js | Screenshot-based visual regression testing for rendered WebGL scenes | [research/technologies/threejs.md, relatedConcepts] |
| Playwright | Visual regression testing listed as a related concept | [research/technologies/playwright.md, relatedConcepts] |

### Integration Testing — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Prisma | Integration testing listed as a related concept | [research/technologies/prisma.md, relatedConcepts] |
| Docker | Integration testing against real dependencies (spun up in containers) | [research/technologies/docker.md, relatedConcepts] |

### Monorepo / Workspace Test Configuration — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Vitest | Multi-project (Projects) support for monorepo/workspace test configuration | [research/technologies/vitest.md, relatedConcepts] |
| shadcn/ui | Monorepo workspace management listed as a related concept | [research/technologies/shadcn-ui.md, relatedConcepts] |

### Load Testing / Benchmarking — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Load testing / benchmarking listed as a related concept (Fastify is marketed on throughput) | [research/technologies/fastify.md, relatedConcepts] |
| Vitest | Benchmarking is a built-in feature | [research/technologies/vitest.md, relatedConcepts] |

---

## I. DevOps, CI/CD, Build & Containerization

### CI/CD Automation — 6 technologies

| Technology | How it relates | Source |
|---|---|---|
| Docker | CI/CD automation listed as a related concept | [research/technologies/docker.md, relatedConcepts] |
| Husky | CI/CD automation listed as a related concept (complements local pre-commit hooks) | [research/technologies/husky.md, relatedConcepts] |
| GitHub | CI/CD automation via webhooks and the Deployments API | [research/technologies/github.md, relatedConcepts] |
| Playwright | CI/CD automation listed as a related concept | [research/technologies/playwright.md, relatedConcepts] |
| Jest | CI/CD automation listed as a related concept | [research/technologies/jest.md, relatedConcepts] |
| GitHub Actions | Is itself GitHub's native CI/CD automation platform | [research/technologies/github-actions.md, relatedConcepts] |

### Containerization — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Containerization listed as a related concept (deployment target) | [research/technologies/fastify.md, relatedConcepts] |
| Docker | Is itself the containerization platform (Image/Container/Registry/Engine) | [research/technologies/docker.md, relatedConcepts] |
| MySQL | Containerization listed as a related concept | [research/technologies/mysql.md, relatedConcepts] |
| GitHub Actions | Containerization listed as a related concept (containerized runners/jobs) | [research/technologies/github-actions.md, relatedConcepts] |

### Build Tooling / Bundling — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Three.js | Module bundling required to ship WebGL applications | [research/technologies/threejs.md, relatedConcepts] |
| Vite | Code bundling for production builds (via Rolldown/Oxc) | [research/technologies/vite.md, relatedConcepts] |
| GitHub Actions | Build automation listed as a related concept | [research/technologies/github-actions.md, relatedConcepts] |

### Hot Module Replacement (HMR) — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Nuxt | Hot module replacement listed as a related concept | [research/technologies/nuxt.md, relatedConcepts] |
| Vitest | "HMR-style" instant watch mode described as "like HMR for tests" | [research/technologies/vitest.md, relatedConcepts] |
| Vite | Fast HMR over native ESM is Vite's core dev-server value proposition | [research/technologies/vite.md, relatedConcepts] |

### Git Hooks / Pre-Commit Automation — 1 technology (see Part M)

### Vulnerability Scanning — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Docker | Vulnerability scanning and SBOM analysis for images | [research/technologies/docker.md, relatedConcepts] |
| GitHub | Dependency vulnerability scanning listed as a related concept | [research/technologies/github.md, relatedConcepts] |

### Least-Privilege Execution — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Docker | Rootless / least-privilege execution listed as a related concept | [research/technologies/docker.md, relatedConcepts] |
| GitHub Actions | Least-privilege access control listed as a related concept | [research/technologies/github-actions.md, relatedConcepts] |

### Secrets Management / OIDC — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| GitHub | Secret scanning listed as a related concept | [research/technologies/github.md, relatedConcepts] |
| GitHub Actions | OIDC authentication and secrets management listed as related concepts | [research/technologies/github-actions.md, relatedConcepts] |

### Package Registry / Artifact Hosting — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| GitHub | Package registry / artifact hosting listed as a related concept | [research/technologies/github.md, relatedConcepts] |
| GitHub Actions | Artifact storage listed as a related concept | [research/technologies/github-actions.md, relatedConcepts] |

### Webhook / Event-Driven Integration — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| GitHub | Webhook event-driven integration listed as a related concept | [research/technologies/github.md, relatedConcepts] |
| GitHub Actions | Event-driven automation is the workflow trigger model itself | [research/technologies/github-actions.md, relatedConcepts] |

---

## J. Security & Access Control

### Role-Based Access Control (RBAC) — 6 technologies

| Technology | How it relates | Source |
|---|---|---|
| PostgreSQL | Native role-based access control | [research/technologies/postgresql.md, relatedConcepts] |
| MongoDB | Role-based access control (RBAC) listed as a related concept | [research/technologies/mongodb.md, relatedConcepts] |
| MySQL | Role-based access control listed as a related concept | [research/technologies/mysql.md, relatedConcepts] |
| ClickHouse | SQL-based role-based access control | [research/technologies/clickhouse.md, relatedConcepts] |
| OpenSearch | Role-based access control (RBAC) listed as a related concept | [research/technologies/opensearch.md, relatedConcepts] |
| Redis | Access control lists (ACL) — Redis's own name for its RBAC-equivalent | [research/technologies/redis.md, relatedConcepts] |

### Encryption in Transit (TLS/SSL) — 5 technologies

| Technology | How it relates | Source |
|---|---|---|
| PostgreSQL | TLS/SSL encryption listed as a related concept | [research/technologies/postgresql.md, relatedConcepts] |
| MongoDB | Encryption in transit (TLS/SSL) listed as a related concept | [research/technologies/mongodb.md, relatedConcepts] |
| MySQL | Encrypted connections (TLS/SSL) listed as a related concept | [research/technologies/mysql.md, relatedConcepts] |
| Redis | TLS encryption in transit listed as a related concept | [research/technologies/redis.md, relatedConcepts] |
| WebRTC | Encrypted media transport is mandatory for peer connections | [research/technologies/webrtc.md, relatedConcepts] |

### Prepared Statements / SQL Injection Mitigation — 3 technologies

| Technology | How it relates | Source |
|---|---|---|
| Prisma | Parameterized queries / SQL injection mitigation listed as a related concept | [research/technologies/prisma.md, relatedConcepts] |
| Drizzle ORM | Prepared statements listed as a related concept | [research/technologies/drizzle-orm.md, relatedConcepts] |
| Go | SQL injection prevention via parameterized queries listed as a related concept | [research/technologies/go.md, relatedConcepts] |

**[Synthesis:** the same SQL-injection defense (parameterization) is listed independently for a
general-purpose language (Go, at the `database/sql` driver level) and two Node.js ORMs (Prisma,
Drizzle) — suggesting this is a concern addressed at multiple layers of a typical stack rather
than solved once and forgotten, i.e. an ORM's parameterization doesn't make a raw-SQL escape
hatch or a different-language service automatically safe.]

### Rate Limiting — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | Rate limiting listed as a related concept | [research/technologies/fastify.md, relatedConcepts] |
| GitHub | API rate limiting listed as a related concept | [research/technologies/github.md, relatedConcepts] |
| Google SEO | API rate limiting and quotas (Search Console / indexing APIs) | [research/technologies/google-seo.md, relatedConcepts] |
| Google AdSense | Rate limiting listed as a related concept (Management API) | [research/technologies/google-adsense.md, relatedConcepts] |

### CORS (Cross-Origin Resource Sharing) — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | CORS handling listed as a related concept | [research/technologies/fastify.md, relatedConcepts] |
| Swagger | CORS listed as a related concept (Swagger UI calling APIs cross-origin) | [research/technologies/swagger.md, relatedConcepts] |

### JWT / Token Authentication — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| Fastify | JWT authentication listed as a related concept | [research/technologies/fastify.md, relatedConcepts] |
| Socket.IO | Middleware-based authentication commonly implemented with JWTs | [research/technologies/socketio.md, relatedConcepts] |

### Same-Origin Security Policy — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| WebSocket API | Same-origin security policy listed as a related concept | [research/technologies/websocket-api.md, relatedConcepts] |
| HTML | Same-origin security policy listed as a related concept | [research/technologies/html.md, relatedConcepts] |

### Audit Logging — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| MySQL | Audit logging listed as a related concept | [research/technologies/mysql.md, relatedConcepts] |
| GitHub | Audit logging listed as a related concept | [research/technologies/github.md, relatedConcepts] |

### Multi-Factor / Two-Factor Authentication — 2 technologies

| Technology | How it relates | Source |
|---|---|---|
| MySQL | Multi-factor authentication listed as a related concept | [research/technologies/mysql.md, relatedConcepts] |
| GitHub | Two-factor authentication listed as a related concept | [research/technologies/github.md, relatedConcepts] |

### Cross-Site Request Forgery (CSRF) Protection — 1 technology (see Part M)

---

## K. SEO, Growth & Monetization

### SEO (Search Engine Optimization) — 4 technologies

| Technology | How it relates | Source |
|---|---|---|
| Nuxt | SEO listed as a related concept | [research/technologies/nuxt.md, relatedConcepts] |
| Next.js | SEO listed as a related concept | [research/technologies/nextjs.md, relatedConcepts] |
| Google SEO | Is itself the subject: crawling → indexing → serving pipeline | [research/technologies/google-seo.md, relatedConcepts] |
| Google AdSense | SEO listed as a related concept (site quality intersects with ad eligibility) | [research/technologies/google-adsense.md, relatedConcepts] |

**[Synthesis:** Nuxt and Next.js both list SSR/SSG/hydration *and* SEO as related concepts,
while Google SEO's own write-up separately lists server-side rendering and client-side
rendering among its related concepts (tied to Googlebot's JS-executing indexer) — combining
these independently-stated facts shows why these frameworks market their rendering modes on SEO
grounds: the rendering-strategy choice and the indexability outcome are two ends of the same
mechanism, even though no single technology's entry states that connection directly.]

### Web Crawling & Indexing — 1 technology (see Part M)

### Ad Monetization — 1 technology (see Part M)

---

## L. Cross-Cutting Synthesis

These are inferences built by combining two or more individually-stated facts from the data;
none of them is asserted directly by any single technology's `relatedConcepts` entry.

1. **TypeScript as connective tissue, not a frontend language.** [Synthesis: see Part F —
   Type Safety.] 17 of the other 43 technologies list "type safety" as a related concept,
   spanning ORMs, backend frameworks, frontend frameworks, a 3D graphics library, and a realtime
   library — a broader reach than any other single concept in this dataset except Test
   Automation and Connection Pooling.

2. **The interceptor/middleware pattern repeats at the data layer and the network layer.**
   [Synthesis: see Part G.] Mongoose's document-level middleware/hooks and Express/Fastify/
   Socket.IO's request-pipeline middleware are structurally the same pattern (a chain of
   functions intercepting an operation) applied to different objects — the data lists them as
   separate related concepts per technology, but never states the structural parallel.

3. **SQL injection defense is layered, not centralized.** [Synthesis: see Part J.] Go
   (`database/sql` parameterization), Prisma, and Drizzle ORM each independently list
   parameterized-query defenses — meaning a stack combining a Go service with a Node ORM has
   this defense duplicated at two different layers, which is a resilience property the data
   doesn't state but that follows from combining the three entries.

4. **Rendering-mode choice and SEO outcome are the same mechanism seen from two sides.**
   [Synthesis: see Part K.] Next.js/Nuxt's SSR+SEO pairing and Google SEO's own SSR/CSR-aware
   crawling/indexing pipeline describe the same JS-execution-during-indexing mechanism from the
   framework side and the search-engine side respectively.

5. **Go and Python represent opposite error-handling philosophies among the dataset's two
   general-purpose languages.** [Synthesis: see Part G.] Go's explicit multi-value
   `(value, error)` returns and Python's exception-chaining (`__cause__`/`__context__`) are
   listed as each language's respective related concept for the same underlying problem
   (propagating failure), with no shared vocabulary between the two entries — the contrast is
   only visible by placing them side by side.

6. **Serverless/edge compatibility clusters around zero-dependency, WASM-friendly tooling.**
   [Synthesis: combining Prisma's "WebAssembly query compilation" + "serverless/edge runtime
   compatibility" with Drizzle's "zero runtime dependencies... serverless-ready footprint" and
   Nuxt/Next.js's "edge computing."] Newer-generation ORMs and meta-frameworks in this dataset
   converge on the same deployment target (edge functions), each solving it differently — Prisma
   via WASM compilation, Drizzle via having near-zero footprint to begin with, and the two
   meta-frameworks via routing individual functions to edge runtimes.

---

## M. Singleton / Technology-Specific Concepts

Concepts that appear in only **one** technology's `relatedConcepts` list in this dataset. Listed
for completeness (per the "list every technology that relates to each concept" requirement) but
grouped compactly by source technology rather than given individual sections, since a
single-technology concept doesn't yet answer a cross-cutting "what touches X" question — it may
simply mean no other researched technology happens to touch it.

| Technology | Singleton concept(s) | Source |
|---|---|---|
| Mongoose | Change tracking; type casting; schema inheritance (discriminators) | [research/technologies/mongoose.md, relatedConcepts] |
| PostgreSQL | Write-ahead logging / durability; crash recovery (paired concept, see Backup & Restore in Part A) | [research/technologies/postgresql.md, relatedConcepts] |
| MongoDB | Schema flexibility (notable as a near-opposite of Schema Validation, which MongoDB *also* lists) | [research/technologies/mongodb.md, relatedConcepts] |
| Fastify | JSON serialization; prototype pollution protection | [research/technologies/fastify.md, relatedConcepts] |
| Prisma | WebAssembly query compilation; driver adapter pattern | [research/technologies/prisma.md, relatedConcepts] |
| Express | Request/response lifecycle; session management; process clustering; static file serving | [research/technologies/express.md, relatedConcepts] |
| React | Unidirectional data flow; declarative UI rendering; error boundary fault isolation; semantic versioning; automated code migration (codemods) | [research/technologies/react.md, relatedConcepts] |
| Go | Generics/type parameters; cross-compilation; fuzz testing; data race detection; FIPS 140-3 cryptographic compliance | [research/technologies/go.md, relatedConcepts] |
| Python | Object-oriented programming | [research/technologies/python.md, relatedConcepts] |
| Nuxt | Auto-import / auto-registration | [research/technologies/nuxt.md, relatedConcepts] |
| Vue | Single-page application; list virtualization | [research/technologies/vue.md, relatedConcepts] |
| Three.js | Shader programming; GPU resource management; render/animation loop; scene graph architecture | [research/technologies/threejs.md, relatedConcepts] |
| Angular | Change detection; CSRF protection | [research/technologies/angular.md, relatedConcepts] |
| TypeScript | Gradual typing / incremental adoption; type definitions/declaration files; IDE language service (LSP) tooling; language superset / source-to-source compilation | [research/technologies/typescript.md, relatedConcepts] |
| ClickHouse | Data compression; approximate query processing; materialized views; partitioning and partition pruning; columnar storage; change data capture (CDC) | [research/technologies/clickhouse.md, relatedConcepts] |
| Redis | In-memory data storage as an architecture (vs. cache as a use case); eviction policies; TTL/key expiration; optimistic locking; pipelining/batched requests; geospatial indexing; probabilistic data structures | [research/technologies/redis.md, relatedConcepts] |
| WebRTC | Peer-to-peer networking / NAT traversal; media capture and streaming; session negotiation / offer-answer signaling; browser web standard API | [research/technologies/webrtc.md, relatedConcepts] |
| OpenAPI | API contract testing; declarative API security scheme description; multi-step API workflow description; design-first API development | [research/technologies/openapi.md, relatedConcepts] |
| WebSocket API | Persistent connection; protocol upgrade handshake; message framing; backpressure/flow control | [research/technologies/websocket-api.md, relatedConcepts] |
| GraphQL | Authorization (field-level); schema introspection / API discovery; API versioning avoidance via schema evolution | [research/technologies/graphql.md, relatedConcepts] |
| HTML | Semantic markup; DOM manipulation; resource fetch prioritization; character encoding detection; MIME type content negotiation; iframe sandboxing / cross-origin isolation; markup conformance validation/linting; error-tolerant parsing | [research/technologies/html.md, relatedConcepts] |
| MUI | CSS-in-JS | [research/technologies/mui-material-ui.md, relatedConcepts] |
| Swagger | API design and editing tooling; server stub scaffolding; template-driven code generation | [research/technologies/swagger.md, relatedConcepts] |
| Sass | Mixins and reusable style chunks; selector inheritance; control flow in stylesheets; source maps; minification/compressed output; deprecation management; REPL/interactive debugging | [research/technologies/sass.md, relatedConcepts] |
| Tailwind CSS | Utility-first styling; zero-runtime CSS generation; cascade layers | [research/technologies/tailwind-css.md, relatedConcepts] |
| Husky | Commit message linting; code formatting automation; developer workflow tooling | [research/technologies/husky.md, relatedConcepts] |
| CSS | Style encapsulation/scoping; rendering performance optimization; browser conformance testing | [research/technologies/css.md, relatedConcepts] |
| GitHub | Version control; branch-based workflow; code review; issue tracking; static site hosting; static analysis/code scanning; self-hosted vs SaaS deployment | [research/technologies/github.md, relatedConcepts] |
| Playwright | Auto-waiting / retry-ability | [research/technologies/playwright.md, relatedConcepts] |
| Vitest | In-source testing | [research/technologies/vitest.md, relatedConcepts] |
| shadcn/ui | Headless UI primitives; supply-chain dependency pinning | [research/technologies/shadcn-ui.md, relatedConcepts] |
| Google SEO | Web crawling; search indexing; ranking algorithms; structured data; canonicalization/duplicate content resolution; mobile-first indexing; web performance monitoring (Core Web Vitals); spam/abuse policy enforcement; sitemap protocol | [research/technologies/google-seo.md, relatedConcepts] |
| ECMAScript | Strict mode; prototype-based object model; host environment abstraction (host hooks); reflection and metaprogramming; sandboxing / code isolation; backward compatibility guarantees | [research/technologies/ecmascript.md, relatedConcepts] |
| Jest | Assertion library; fake timers; test runner; module resolution | [research/technologies/jest.md, relatedConcepts] |
| GitHub Actions | YAML-based configuration; reusable workflow composition; infrastructure as code; deployment automation | [research/technologies/github-actions.md, relatedConcepts] |
| Vite | Dev server tooling | [research/technologies/vite.md, relatedConcepts] |
| Google AdSense | Client library / SDK; consent management; asynchronous script loading | [research/technologies/google-adsense.md, relatedConcepts] |

---

## N. Gaps & Silences in the Data

Per the task instructions, gaps are stated explicitly rather than filled in:

- **PostgreSQL's `relatedConcepts` never uses the literal phrase "relational database"** or "SQL
  query language," even though its core concepts are unmistakably an RDBMS (MVCC, WAL, SQL
  transaction isolation levels). Only MySQL and ClickHouse use that literal phrasing. This is
  almost certainly an artifact of how the source research phrased PostgreSQL's related-concepts
  list, not a claim that PostgreSQL isn't relational — flagged here so the omission from the
  "Relational Database / SQL" table (Part A) isn't mistaken for a factual claim.
- **No technology in this dataset lists a "distributed tracing" or "observability/logging"
  concept** beyond OpenSearch's "log analytics"/"real-time application monitoring" and Docker's
  "log aggregation." Given how central observability tooling is to production systems, its near-
  total absence from this 44-technology extract is notable — it may mean the underlying research
  simply didn't cover an APM/tracing tool, not that none of these technologies touch logging.
- **No message-queue/broker technology beyond Redis's pub/sub is present** — there is no
  Kafka, RabbitMQ, or SQS entry in the source data, so "message queuing" in Part A is a single
  Redis-only mention rather than a genuinely cross-cutting concept, despite queuing being a
  common need alongside the caching/realtime technologies that *are* well covered.
- **Authentication is fragmented across many single- or double-mention concepts** (JWT, OAuth2,
  MFA/2FA, session management, middleware-based auth) rather than one unified "authentication"
  concept in the source data — this map preserves that fragmentation rather than merging it,
  since collapsing JWT and OAuth2 into one bucket would blur a real distinction (token format vs.
  authorization flow) that the underlying research kept separate.
- **CSS-in-JS appears only under MUI**, even though Tailwind CSS, Sass, and plain CSS are all
  covered — the data doesn't state whether this is because CSS-in-JS is considered MUI-specific
  by the underlying research or because the other styling technologies' write-ups simply didn't
  list it as a related concept. Treat it as thin coverage, not a claim that Tailwind/Sass have no
  relationship to CSS-in-JS.
- **The 7 AI coding-agent ecosystem write-ups (`research/agent-ecosystems/*.md`) are entirely
  absent from this map** because they were not included in the data file supplied for this
  specific task (see Scope note at the top). Any concept map spanning agent-ecosystem concepts
  (e.g. tool-calling, sandboxing, context management) would require a separate pass over that
  research.
