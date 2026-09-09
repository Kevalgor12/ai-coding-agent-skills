# Skill Taxonomy — Overview & Design Contract

Status: **proposed taxonomy** (design only). No skill content exists yet.
Authored as the Principal-Architect design pass over the completed research in
[`research/agent-ecosystems/`](../../research/agent-ecosystems/),
[`research/technologies/`](../../research/technologies/), and
[`research/knowledge-maps/`](../../research/knowledge-maps/).

This directory defines **what skills the library should contain and how they
relate** — the organizing contract every future skill and adapter is built
against. It does not contain skill instructions (no `SKILL.md` bodies); those
come later, in [`skills/`](../../skills/).

## Files

- **README.md** (this file) — design principles, the layered model, the skill
  ID scheme, the per-skill specification schema, and the vendor-neutrality model.
- **[skill-catalog.md](skill-catalog.md)** — every proposed skill with its full
  specification (the 13 required fields). Generic skills get individual specs;
  technology-specific skills are defined via a shared template plus a
  per-technology parameter table.
- **[taxonomy-analysis.md](taxonomy-analysis.md)** — the required decision
  analysis: skills to create / merge / split / drop, missing capabilities, and
  the generic vs. technology-specific vs. orchestration vs. review classification.
  Also contains the two explicit rulings the brief demanded (Git conventions,
  code commenting).

## Why a taxonomy before any skill

Three findings from the research make the taxonomy the load-bearing decision,
not the individual skills:

1. **The skill *format* is converging; the skill *set* is not.** Six of seven
   agent ecosystems already claim to adopt the same `SKILL.md` / agentskills.io
   convention ([comparison.md, Headline finding](../../research/agent-ecosystems/comparison.md)).
   So the library's differentiation is not the file format — it is *which skills
   exist, how cleanly they are bounded, and how well they compose*. That is a
   taxonomy problem.
2. **Progressive disclosure makes boundaries a performance feature, not just an
   aesthetic one.** Every ecosystem loads only a skill's `name` + `description`
   up front and the body only on activation. Overlapping or vaguely-scoped
   skills therefore mis-trigger and waste context. Clear boundaries and correct
   activation are the same design goal.
3. **Execution capability is not portable; knowledge is.** The
   [agent-capability map](../../research/knowledge-maps/agent-capability-map.md)
   shows browser automation, Docker orchestration, and MCP config formats all
   vary per agent. A skill that hard-depends on one of these is not
   vendor-neutral. The taxonomy must separate *what to do* (portable) from *how
   the host agent executes it* (adapter-resolved).

## Design principles (and how each is enforced structurally)

| Principle | How the taxonomy enforces it |
|---|---|
| **Complete capability coverage** | Every capability named in the brief maps to at least one skill or is explicitly listed as a research-gap in [taxonomy-analysis.md](taxonomy-analysis.md#missing-capabilities). Nothing is silently dropped. |
| **Clear boundaries** | Each skill has an explicit `scope` and a `non-activation` field. Two skills may not both claim the same trigger. |
| **Composability** | Skills are layered (below). Higher layers *compose* lower ones via the `dependencies`/`related` fields rather than re-implementing them. |
| **Minimal duplication** | Cross-cutting concerns (security, performance, testing, comments) are single generic skills that technology skills *reference*, never re-document. |
| **Context efficiency** | Technology skills activate only on detection of that technology, so a Postgres task never loads the Three.js skill. Descriptions are written for precise triggering. |
| **Maintainability** | Version-sensitive facts live in the technology skills (which map 1:1 to a researched tech doc and its version registry entry), so a framework release only touches one skill. Generic skills hold version-stable engineering practice. |
| **Correct activation** | Every skill declares both activation *and* non-activation conditions, so the model can rule a skill out as confidently as rule it in. |
| **Vendor neutrality** | No skill body may name a host-agent tool. Capability requirements are declared abstractly and resolved by the orchestration layer / adapters. |

## The layered model

Skills are organized into five layers. **Composition flows downward**: a layer
may depend on skills in its own or a lower layer, never an upper one. This is
what keeps the graph acyclic and the boundaries clean.

```
Layer 0  Orchestration & Meta      route, compose, and adapt skills to the host agent
Layer 1  Discovery & Architecture  requirements, solution design, planning
Layer 2  Engineering Conventions   universal practice: git conventions, comments,
                                    code quality, refactoring, review, docs
Layer 3  Domain Capabilities       tech-neutral engineering per domain
                                    (frontend, backend, data, infra, quality, growth, AI)
Layer 4  Technology Specializations one per researched technology; specializes a
                                    Layer-3 skill with concrete, version-aware, cited detail
```

Worked example of composition — "build a paginated REST endpoint backed by
Postgres, in a Next.js app, with tests":

- Layer 1 `solution-architecture` frames the approach.
- Layer 3 `api-design` (REST/pagination/errors), `data-modeling`,
  `orm-integration`, `testing-strategy` supply the tech-neutral method.
- Layer 4 `nextjs`, `postgresql`, `drizzle` (or `prisma`/`typeorm`),
  `jest-vitest` supply the concrete, version-correct detail.
- Layer 2 `git-conventions` + `code-commenting` + `code-review` govern the
  output regardless of stack.
- Layer 0 `capability-adapter` checks the host agent can actually run the
  migration/test commands and, if not (e.g. no shell), degrades to
  advisory-only output instead of failing.

No single skill tries to know all of that. That is the point.

## Skill ID scheme

`SK-<DOMAIN>-<NNN>` — stable, opaque once assigned (a rename never changes the
ID). Domain codes:

| Code | Layer | Domain |
|---|---|---|
| `ORCH` | 0 | Orchestration & meta |
| `DISC` | 1 | Discovery, requirements, architecture, planning |
| `CONV` | 2 | Engineering conventions (universal practice) |
| `FE` | 3 | Frontend & UI/UX |
| `BE` | 3 | Backend & API & realtime |
| `DATA` | 3 | Databases, ORM, caching, search |
| `INFRA` | 3 | Infrastructure, containers, CI/CD, delivery |
| `QA` | 3 | Testing, security, performance, observability |
| `GROW` | 3 | SEO & monetization |
| `AI` | 3 | AI / LLM application engineering |
| `TECH` | 4 | Technology specializations (sub-keyed by slug) |

Technology skills use `SK-TECH-<slug>` (e.g. `SK-TECH-postgresql`) so the ID
carries the technology name directly and stays stable across recategorization.

## Per-skill specification schema

Every skill in the catalog is defined by these 13 fields (exactly the set the
brief requires), plus one supplementary field the research made non-optional:

1. **Unique ID** — `SK-…` per the scheme above.
2. **Name** — short, human-readable; also the basis of the eventual skill's
   trigger `description`.
3. **Purpose** — the one-sentence reason the skill exists.
4. **Scope** — what it *does* cover.
5. **Responsibilities** — the concrete behaviors it owns.
6. **Inputs** — what it expects to be given (task context, files, prior-skill output).
7. **Outputs** — what it produces (edits, artifacts, recommendations, structured data).
8. **Activation conditions** — when it *should* trigger.
9. **Non-activation conditions** — when it must *not* trigger (the boundary guard).
10. **Dependencies** — skills (or abstract agent capabilities) it relies on.
11. **Conflicts** — skills that must not co-activate, or whose output it overrides.
12. **Related skills** — commonly composed-with, but not a hard dependency.
13. **Evaluation requirements** — what an `evaluations/` test must prove before
    the skill is trusted (ties each skill to the eval harness).

Supplementary field (recorded where relevant, folded into *dependencies*):

- **Required agent capabilities** — abstract capabilities from the
  [agent-capability map](../../research/knowledge-maps/agent-capability-map.md)
  (e.g. "shell execution", "browser automation", "MCP DB access") that the host
  agent must have for the skill to *execute* rather than merely *advise*. This is
  the vendor-neutrality contract; the orchestration layer resolves it per target.

## Vendor-neutrality model (how a skill stays portable)

Every skill is written to one of three **execution tiers**, declared in its spec:

- **Tier A — Knowledge/advisory.** Produces guidance, review, or edits to files.
  Needs only file read/write, which all seven researched ecosystems have. Fully
  portable. (Most Layer 1–2 skills, and the advisory half of every skill.)
- **Tier B — CLI execution.** Needs shell command execution (run a build, a
  migration, a test). Shell exists in all seven ecosystems but sandbox/approval
  behavior differs; the skill must degrade to Tier A if shell is unavailable or
  denied. (Most Layer 3–4 build/test/db skills.)
- **Tier C — Specialized capability.** Needs a capability that is *not* universal
  — browser automation (Playwright), a database MCP server, container
  orchestration. The skill must declare this and the `capability-adapter`
  (`SK-ORCH-002`) must confirm availability or route to a documented fallback
  (e.g. Claude Code reaching Playwright only via an external MCP server).

A skill never names a host tool. "Run the test suite" is Tier B intent;
*whether* that is Claude Code's `Bash`, Cursor's shell tool, or a denied action
is resolved at runtime, not baked into the skill. This is the single rule that
makes the library portable across the six-plus ecosystems that share the
`SKILL.md` format but share almost no execution vocabulary.
