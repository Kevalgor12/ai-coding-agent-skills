# adapters

Translation layers that map the agent-agnostic skills in [`skills/`](../skills)
into the format a specific coding agent expects (its manifest format,
directory conventions, invocation mechanism, etc).

Expected to eventually hold one subdirectory per supported target, e.g.:

- `claude-code/`
- `cursor/`
- `codex/`
- `windsurf/`
- `antigravity/`
- `vscode-agents/`
- `mcp/`

An adapter should contain only the logic/config needed to package or expose
skills for that target — never skill content itself, and never logic that's
actually agent-agnostic (that belongs in `core/`).

No adapters exist yet. The set of supported agents, and how much per-agent
logic each one actually needs, is expected to grow as skills are built out.
