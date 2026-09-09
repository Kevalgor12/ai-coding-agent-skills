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

Per the [specification's conformance lifecycle](../core/skill-specification/specification.md#5-conformance--lifecycle),
a skill needs a passing mechanical validator, an `evaluations/` test, and an
`audits/` review before it is promoted to `final/`. None of the above have a
validator, evaluator, or adapter implementation yet — those are separate,
not-yet-built pieces of tooling (`core/` currently holds only the design
documents, no executable validator).
