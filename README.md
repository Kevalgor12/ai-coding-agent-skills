# ai-coding-agent-skills

A professional, reusable **Skill Library** for AI coding agents.

This repository *is* the product: a versioned, maintainable collection of
reusable engineering skills that can be consumed by coding agents such as
Claude Code, Cursor, Codex, Windsurf, Antigravity, VS Code agents,
MCP-based agents, and future/custom agents.

This is not an application, a SaaS product, a website, or a demo. There is no
runtime, no service, and no UI. What ships is the content of this repository.

## Status

Scaffold only. No skills have been written yet. The directory structure and
initial files exist so that skill authoring can begin on a stable foundation,
not the other way around.

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

## Contributing skills

Not yet — the schema in `core/` needs to exist first. Skills are added
deliberately and individually once that foundation is in place, not
generated in bulk.

## Open architectural decisions

See the end of the initial-scaffold conversation/PR for the full list of
decisions that should be reviewed before skill authoring begins (license
choice, `skills/` vs `final/` promotion mechanism, per-skill versioning
strategy, adapter granularity, and skill schema ownership).

## License

[MIT](LICENSE) — see the "Open architectural decisions" note above; this
choice should be explicitly confirmed before the library is opened up to
external contributors or consumers.
