# skills

The library's actual content: individual, reusable engineering skills for AI
coding agents.

Each skill is expected to live in its own subdirectory here, following
whatever manifest/schema is defined in [`core/`](../core). A skill directory
is expected to be self-contained: its own instructions, metadata, and any
supporting files it needs, independent of which agent will eventually
consume it.

Skills are added deliberately, one at a time (or in small approved batches),
following the schema in [`core/skill-specification/`](../core/skill-specification/),
not generated speculatively or in bulk.

## Current skills

| Skill | ID | Domain | Status |
|---|---|---|---|
| [requirements-engineering](requirements-engineering/) | `SK-DISC-001` | Discovery | authored, not yet validated/evaluated |
| [solution-architecture](solution-architecture/) | `SK-DISC-002` | Discovery | authored, not yet validated/evaluated |
| [technical-planning](technical-planning/) | `SK-DISC-003` | Discovery | authored, not yet validated/evaluated |
| [project-management](project-management/) | `SK-DISC-004` | Discovery | authored, not yet validated/evaluated |
| [data-modeling](data-modeling/) | `SK-DATA-001` | Data (generic) | authored, not yet validated/evaluated |
| [orm-integration](orm-integration/) | `SK-DATA-002` | Data (generic) | authored, not yet validated/evaluated |
| [data-migration](data-migration/) | `SK-DATA-006` | Data (generic) | authored, not yet validated/evaluated |
| [postgresql](postgresql/) | `SK-TECH-postgresql` | Data (technology) | authored, not yet validated/evaluated |
| [mysql](mysql/) | `SK-TECH-mysql` | Data (technology) | authored, not yet validated/evaluated |
| [mongodb](mongodb/) | `SK-TECH-mongodb` | Data (technology) | authored, not yet validated/evaluated |
| [mongoose](mongoose/) | `SK-TECH-mongoose` | Data (technology) | authored, not yet validated/evaluated |
| [drizzle](drizzle/) | `SK-TECH-drizzle` | Data (technology) | authored, not yet validated/evaluated |
| [prisma](prisma/) | `SK-TECH-prisma` | Data (technology) | authored, not yet validated/evaluated |
| [typeorm](typeorm/) | `SK-TECH-typeorm` | Data (technology) | authored, not yet validated/evaluated |
| [clickhouse](clickhouse/) | `SK-TECH-clickhouse` | Data (technology) | authored, not yet validated/evaluated |
| [redis](redis/) | `SK-TECH-redis` | Data (technology) | authored, not yet validated/evaluated |
| [backend-architecture](backend-architecture/) | `SK-BE-001` | Backend (generic) | authored, not yet validated/evaluated |
| [api-design](api-design/) | `SK-BE-002` | Backend (generic) | authored, not yet validated/evaluated |
| [graphql-api-design](graphql-api-design/) | `SK-BE-003` | Backend (generic) | authored, not yet validated/evaluated |
| [nodejs](nodejs/) | `SK-TECH-nodejs` | Backend (technology) | authored, not yet validated/evaluated — added to the taxonomy post-hoc (2026-09-10) |
| [graphql](graphql/) | `SK-TECH-graphql` | Backend (technology) | authored, not yet validated/evaluated |
| [express](express/) | `SK-TECH-express` | Backend (technology) | authored, not yet validated/evaluated |
| [fastify](fastify/) | `SK-TECH-fastify` | Backend (technology) | authored, not yet validated/evaluated |
| [go](go/) | `SK-TECH-go` | Backend (technology) | authored, not yet validated/evaluated |
| [python](python/) | `SK-TECH-python` | Backend (technology) | authored, not yet validated/evaluated |
| [openapi-swagger](openapi-swagger/) | `SK-TECH-openapi-swagger` | Backend (technology) | authored, not yet validated/evaluated |
| [frontend-architecture](frontend-architecture/) | `SK-FE-001` | Frontend (generic) | authored, not yet validated/evaluated |
| [rendering-strategy](rendering-strategy/) | `SK-FE-005` | Frontend (generic) | authored, not yet validated/evaluated |
| [web-accessibility](web-accessibility/) | `SK-FE-004` | Frontend (generic) | authored, not yet validated/evaluated |
| [react](react/) | `SK-TECH-react` | Frontend (technology) | authored, not yet validated/evaluated |
| [nextjs](nextjs/) | `SK-TECH-nextjs` | Frontend (technology) | authored, not yet validated/evaluated |
| [vue](vue/) | `SK-TECH-vue` | Frontend (technology) | authored, not yet validated/evaluated |
| [nuxt](nuxt/) | `SK-TECH-nuxt` | Frontend (technology) | authored, not yet validated/evaluated |
| [angular](angular/) | `SK-TECH-angular` | Frontend (technology) | authored, not yet validated/evaluated |
| [typescript](typescript/) | `SK-TECH-typescript` | Frontend (technology) | authored, not yet validated/evaluated |
| [web-standards](web-standards/) | `SK-TECH-web-standards` | Frontend (technology) | authored, not yet validated/evaluated — merged HTML+CSS per taxonomy analysis |
| [sass](sass/) | `SK-TECH-sass` | Frontend (technology) | authored, not yet validated/evaluated |
| [tailwindcss](tailwindcss/) | `SK-TECH-tailwindcss` | Frontend (technology) | authored, not yet validated/evaluated |
| [mui](mui/) | `SK-TECH-mui` | Frontend (technology) | authored, not yet validated/evaluated |
| [shadcn-ui](shadcn-ui/) | `SK-TECH-shadcn-ui` | Frontend (technology) | authored, not yet validated/evaluated |
| [realtime-communication](realtime-communication/) | `SK-BE-004` | Backend/Realtime (generic) | authored, not yet validated/evaluated |
| [threejs](threejs/) | `SK-TECH-threejs` | Frontend (technology) | authored, not yet validated/evaluated |
| [websocket-api](websocket-api/) | `SK-TECH-websocket-api` | Backend/Realtime (technology) | authored, not yet validated/evaluated |
| [socketio](socketio/) | `SK-TECH-socketio` | Backend/Realtime (technology) | authored, not yet validated/evaluated |
| [webrtc](webrtc/) | `SK-TECH-webrtc` | Backend/Realtime (technology) | authored, not yet validated/evaluated |
| [search-integration](search-integration/) | `SK-DATA-005` | Data (generic) | authored, not yet validated/evaluated |
| [opensearch](opensearch/) | `SK-TECH-opensearch` | Data (technology) | authored, not yet validated/evaluated |
| [containerization](containerization/) | `SK-INFRA-001` | Infrastructure (generic) | authored, not yet validated/evaluated |
| [deployment-release](deployment-release/) | `SK-INFRA-003` | Infrastructure (generic) | authored, not yet validated/evaluated |
| [docker](docker/) | `SK-TECH-docker` | Infrastructure (technology) | authored, not yet validated/evaluated |
| [git-conventions](git-conventions/) | `SK-CONV-001` | Conventions (generic, mandated first-class) | authored, not yet validated/evaluated |
| [git-workflow](git-workflow/) | `SK-CONV-008` | Conventions (generic) | authored, not yet validated/evaluated |
| [ci-cd-pipeline](ci-cd-pipeline/) | `SK-INFRA-002` | Infrastructure (generic) | authored, not yet validated/evaluated |
| [github-actions](github-actions/) | `SK-TECH-github-actions` | Infrastructure (technology) | authored, not yet validated/evaluated |
| [husky](husky/) | `SK-TECH-husky` | Infrastructure (technology) | authored, not yet validated/evaluated |
| [testing-strategy](testing-strategy/) | `SK-QA-001` | QA (generic) | authored, not yet validated/evaluated |
| [jest-vitest](jest-vitest/) | `SK-TECH-jest-vitest` | QA (technology) | authored, not yet validated/evaluated |
| [playwright](playwright/) | `SK-TECH-playwright` | QA (technology) | authored, not yet validated/evaluated |
| [security-engineering](security-engineering/) | `SK-QA-002` | QA (generic) | authored, not yet validated/evaluated |
| [authentication-authorization](authentication-authorization/) | `SK-BE-005` | Backend (generic) | authored, not yet validated/evaluated |
| [database-operations](database-operations/) | `SK-DATA-003` | Data (generic) | authored, not yet validated/evaluated |
| [caching-strategy](caching-strategy/) | `SK-DATA-004` | Data (generic) | authored, not yet validated/evaluated |
| [performance-engineering](performance-engineering/) | `SK-QA-003` | QA (generic) | authored, not yet validated/evaluated |
| [seo-optimization](seo-optimization/) | `SK-GROW-001` | Growth (generic, unified with Google SEO tech content) | authored, not yet validated/evaluated |
| [ui-ux-design](ui-ux-design/) | `SK-FE-002` | Frontend (generic) | authored, not yet validated/evaluated |
| [styling-systems](styling-systems/) | `SK-FE-003` | Frontend (generic) | authored, not yet validated/evaluated |
| [code-commenting](code-commenting/) | `SK-CONV-002` | Conventions (generic, mandated first-class) | authored, not yet validated/evaluated |
| [code-quality](code-quality/) | `SK-CONV-003` | Conventions (generic) | authored, not yet validated/evaluated |
| [refactoring](refactoring/) | `SK-CONV-004` | Conventions (generic) | authored, not yet validated/evaluated |
| [legacy-modernization](legacy-modernization/) | `SK-CONV-005` | Conventions (generic) | authored, not yet validated/evaluated |
| [code-review](code-review/) | `SK-CONV-007` | Conventions (generic) | authored, not yet validated/evaluated |
| [technical-documentation](technical-documentation/) | `SK-CONV-006` | Conventions (generic) | authored, not yet validated/evaluated |
| [observability](observability/) | `SK-QA-004` | QA (generic) | authored, not yet validated/evaluated — closes a research gap held from taxonomy design |
| [opentelemetry](opentelemetry/) | `SK-TECH-opentelemetry` | QA (technology) | authored, not yet validated/evaluated |
| [prometheus](prometheus/) | `SK-TECH-prometheus` | QA (technology) | authored, not yet validated/evaluated |
| [grafana](grafana/) | `SK-TECH-grafana` | QA (technology) | authored, not yet validated/evaluated |
| [sentry](sentry/) | `SK-TECH-sentry` | QA (technology) | authored, not yet validated/evaluated |
| [llm-application-engineering](llm-application-engineering/) | `SK-AI-001` | AI/LLM (generic, root) | authored, not yet validated/evaluated — closes a research gap held from taxonomy design |
| [prompt-context-engineering](prompt-context-engineering/) | `SK-AI-002` | AI/LLM (generic) | authored, not yet validated/evaluated |
| [structured-output-tool-calling](structured-output-tool-calling/) | `SK-AI-003` | AI/LLM (generic) | authored, not yet validated/evaluated |
| [agent-architecture](agent-architecture/) | `SK-AI-004` | AI/LLM (generic) | authored, not yet validated/evaluated |
| [rag-engineering](rag-engineering/) | `SK-AI-005` | AI/LLM (generic) | authored, not yet validated/evaluated |
| [model-selection](model-selection/) | `SK-AI-006` | AI/LLM (generic) | authored, not yet validated/evaluated |
| [llm-evaluation](llm-evaluation/) | `SK-AI-007` | AI/LLM (generic) | authored, not yet validated/evaluated |
| [ai-security](ai-security/) | `SK-AI-008` | AI/LLM (generic) | authored, not yet validated/evaluated |
| [skill-router](skill-router/) | `SK-ORCH-001` | Orchestration (Layer 0) | authored, not yet validated/evaluated — reference implementation of [core/orchestrator/](../core/orchestrator/) |
| [capability-adapter](capability-adapter/) | `SK-ORCH-002` | Orchestration (Layer 0) | authored, not yet validated/evaluated — the vendor-neutrality enforcement point |
| [workflow-composer](workflow-composer/) | `SK-ORCH-003` | Orchestration (Layer 0) | authored, not yet validated/evaluated — hard-composes `SK-ORCH-001` |

Per the [specification's conformance lifecycle](../core/skill-specification/specification.md#5-conformance--lifecycle),
a skill needs a passing mechanical validator, an `evaluations/` test, and an
`audits/` review before it is promoted to `final/`. None of the above have a
validator, evaluator, or adapter implementation yet — those are separate,
not-yet-built pieces of tooling (`core/` currently holds only the design
documents, no executable validator).
