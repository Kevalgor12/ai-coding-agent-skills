# adapters

Translation layers that map the agent-agnostic skills in [`skills/`](../skills)
into the format a specific coding agent expects (its manifest format,
directory conventions, invocation mechanism, etc). Implements the projection
model designed in
[`core/skill-specification/adapter-projection.md`](../core/skill-specification/adapter-projection.md):
**canonical skill → target artifact(s) + a loss manifest**. This is Step 31
of this project's master build plan.

## Structure

```
adapters/
├── lib/                    — shared engine every per-target adapter builds on
│   ├── skill_loader.py     — the ONLY place that parses skill.yaml + SKILL.md
│   ├── loss_manifest.py    — the shared loss-manifest report format
│   └── common.py           — small helpers shared across all 6 targets
├── tests/
│   └── test_compatibility.py  — runs every adapter against real skills, checks
│                                 structural correctness and lossiness-contract
│                                 compliance (no live vendor runtime exists to
│                                 test against — see each target's own README)
├── claude-code/adapter.py + README.md
├── cursor/adapter.py + README.md
├── codex/adapter.py + README.md
├── windsurf/adapter.py + README.md
├── antigravity/adapter.py + README.md
└── mcp/adapter.py + README.md
```

Per the master build plan's target list, this covers 6 targets: Claude Code,
Cursor, Codex, Windsurf (Devin), Antigravity, and Generic/MCP.
`adapter-projection.md`'s own design additionally covers VS Code agents and
"Custom" coding agents as a stable-contract fallback — not built here since
they weren't in the plan's required list, but the design already
accommodates them if a 7th/8th adapter is ever warranted.

## The shared-engine rule

**No per-target adapter re-parses a skill or re-implements another
adapter's field-mapping logic.** `lib/skill_loader.py` is the one place
that knows how to read a canonical skill; every `adapter.py` imports it. A
canonical field that has no vendor-native representation on a given target
still gets an explicit, non-silent entry in that target's loss
manifest — this is `lib/loss_manifest.py`'s job, and it's the same report
shape across all 6 targets, not six independently-invented formats. This
is the literal implementation of the master plan's "do not duplicate the
actual skill knowledge across adapters" instruction.

## Running the compatibility tests

```bash
python3 adapters/tests/test_compatibility.py
```

No `pytest` dependency — plain assertions, the same convention this
project's other verification scripts have used throughout its build. The
suite checks, across a diverse sample of real skills and all 6 targets:
no adapter crashes, no runtime-meaningful field is silently dropped
(Lossiness contract L-2), every populated canonical field is accounted
for somewhere in the loss manifest (L-1), required frontmatter is
present and well-formed, and each target's own documented quirks
(Antigravity's third-person description, MCP's resource-URI shape) hold.

## What each per-target `README.md` documents

Per the master build plan, exactly 6 aspects per target: supported
capabilities, limitations, packaging format, loading behavior,
compatibility assumptions, and version considerations — the last of
these restating `adapter-projection.md`'s own snapshot-date caveat
(vendor formats move fast; re-verify before trusting an adapter in
production) specifically for that target's documented feature set.

## Vendor-neutrality boundary

An adapter contains only the logic/config needed to package or expose
skills for its one target — never skill content itself (that always
comes from `skills/`, loaded once via `lib/skill_loader.py`), and never
logic that's actually agent-agnostic (that belongs in `core/`). No
vendor-specific behavior was introduced into any canonical skill file to
make this layer work — every skill in `skills/` is unchanged by this step.
