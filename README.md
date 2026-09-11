# ai-coding-agent-skills

A professional, reusable **Skill Library** for AI coding agents.

This repository *is* the product: a versioned, maintainable collection of
reusable engineering skills that can be consumed by coding agents such as
Claude Code, Cursor, Codex, Windsurf, Antigravity, VS Code agents,
MCP-based agents, and future/custom agents.

This is not an application, a SaaS product, a website, or a demo. There is no
runtime, no service, and no UI. What ships is the content of this repository.

## Status

**v0.1.0 — initial release.** 88 skills authored, organized across 5 layers
and 12 domains. All skills pass the mechanical validator
([`scripts/validate_skills.py`](scripts/validate_skills.py) — VR-1 through
VR-9). Six adapter targets are implemented and tested (36/36 compatibility
combinations pass). The library has passed a final principal-engineer audit and
a full regression suite (Step 35). See [`final/RELEASE.md`](final/RELEASE.md)
for the complete release report.

Individual skills carry status `authored, not yet validated/evaluated` because
per-skill live-agent evaluation (the final promotion gate to `final/`) requires
tooling not yet built. The skills are usable immediately through the adapter
layer; the promotion gate is a quality ratchet for the `final/` directory,
not a gate on consumption.

## Repository structure

```
core/          Agent-agnostic contract layer (skill schema, shared
               conventions, validation logic). No skill content.
skills/        The library itself — individual, reusable skills, each
               self-contained and agent-agnostic.
adapters/      Per-agent translation layers that package skills/ into the
               format a specific target agent expects.
research/      Background research and design rationale behind decisions
               made in core/, skills/, and adapters/. Not shipped.
evaluations/   Test harnesses and benchmarks that measure whether a skill
               actually works, and track results across versions.
audits/        Quality, security, and correctness review records for
               skills — separate from whether a skill is effective.
examples/      Worked examples of consuming this library from a given
               agent. Not skills themselves.
final/         Release-ready skill snapshots that have passed evaluation
               and audit, as opposed to skills still in development.
```

Each directory contains its own `README.md` with a more detailed
description of what belongs there and how it relates to the others. The
intended dependency direction is:

```
research  ─┐
            ├─▶  core  ─▶  skills  ─▶  evaluations / audits  ─▶  final
            │              │
            │              ▼
            └────────▶  adapters  ─▶  examples
```

`core/` defines the contract. `skills/` is written against that contract.
`adapters/` exposes `skills/` to specific agents. `evaluations/` and
`audits/` gate what's allowed to reach `final/`. `research/` and `examples/`
are supporting material that inform and demonstrate the rest, but are never
themselves shipped as skill content.

## Versioning

This project follows [Semantic Versioning](https://semver.org/). The
current version is tracked in [`VERSION`](VERSION); changes are recorded in
[`CHANGELOG.md`](CHANGELOG.md). How individual skills inside `skills/` are
versioned relative to the library as a whole is not yet decided — see
"Open architectural decisions" below.

## How to consume this library

### Pick your agent target

Each supported agent has its own adapter in [`adapters/`](adapters/). The
adapter handles skill discovery, loading, and format translation for that
target. Start there:

| Agent | Adapter |
|---|---|
| Claude Code | [`adapters/claude-code/`](adapters/claude-code/) |
| Cursor | [`adapters/cursor/`](adapters/cursor/) |
| GitHub Copilot / Codex | [`adapters/codex/`](adapters/codex/) |
| Windsurf | [`adapters/windsurf/`](adapters/windsurf/) |
| Antigravity | [`adapters/antigravity/`](adapters/antigravity/) |
| MCP-based agents | [`adapters/mcp/`](adapters/mcp/) |

### Understand the skill structure

Every skill lives under [`skills/<slug>/`](skills/) and contains:

- `skill.yaml` — machine-readable metadata (ID, activation conditions,
  inputs/outputs, dependencies, capabilities, verification criteria)
- `SKILL.md` — the human-readable method the agent should follow
- `references/` — per-skill reference notes (version-sensitive details,
  decision matrices) when present

### Route skills correctly

The orchestrator ([`core/orchestrator/`](core/orchestrator/)) and routing
algorithm ([`core/routing-architecture/`](core/routing-architecture/)) define
how an agent selects skills for a given task. Read
[`core/orchestrator/lifecycle.md`](core/orchestrator/lifecycle.md) for the
full decision flow, and
[`core/routing-architecture/routing-algorithm.md`](core/routing-architecture/routing-algorithm.md)
for the routing rules.

### Browse the skill catalog

[`core/taxonomy/skill-catalog.md`](core/taxonomy/skill-catalog.md) lists all
88 skills organized by domain and layer.
[`final/manifest.json`](final/manifest.json) is the machine-readable version
for programmatic consumers.

## Contributing skills

Skills are added deliberately, following the schema in
[`core/skill-specification/specification.md`](core/skill-specification/specification.md).
Run [`scripts/validate_skills.py`](scripts/validate_skills.py) after authoring
to confirm the skill passes VR-1 through VR-9 before opening a pull request.

## Versioning

This project follows [Semantic Versioning](https://semver.org/). The current
version is tracked in [`VERSION`](VERSION); changes are recorded in
[`CHANGELOG.md`](CHANGELOG.md).

## License

[MIT](LICENSE)
