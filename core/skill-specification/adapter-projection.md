# Adapter Projection

How a canonical skill (`skill.yaml` + `SKILL.md` + resources) projects into each
of the eight targets. This is the contract the per-target adapters in
[`adapters/`](../../adapters/) implement. Grounded in
[comparison.md](../../research/agent-ecosystems/comparison.md) and the
[agent-capability map](../../research/knowledge-maps/agent-capability-map.md).

**Snapshot caveat (2026-09-09):** vendor formats move fast (Windsurf→Devin
rebrand mid-migration; MCP Skills-over-MCP SEP-2640 accepted only 2026-09-03 and
pre-implementation). Every mapping below MUST be re-verified against current
vendor docs before an adapter is trusted. Fields are cited to the ecosystem
research where they came from.

## Projection model

An adapter is a pure function: **canonical skill → target artifact(s) + a
loss manifest**. It:

1. Reads `skill.yaml` (superset metadata) + `SKILL.md` body + resources.
2. Emits the target's native `SKILL.md` (or resource, for MCP) with **only the
   frontmatter keys that target understands**, renaming/mapping per the matrix.
3. Places artifacts at the target's expected path.
4. Applies any `adapter_hints.<target>` overrides.
5. Writes a **loss manifest**: every canonical field it could not represent
   natively, and how it compensated (moved into the body, or dropped). This
   makes lossiness explicit rather than silent — the failure mode VS Code itself
   exhibits when it ingests Claude hook matchers but doesn't enforce them.

The body (Tier-1 Markdown) is portable as-is across all targets; the divergence
is entirely in frontmatter, invocation config, path, and (for MCP) packaging.

## Common denominator

All six file-based vendors read: a directory containing `SKILL.md` with
`name` + `description` frontmatter + Markdown body, plus sibling resource
folders. `.agents/skills/<slug>/` is recognized by Cursor, Codex, Windsurf,
Antigravity, and VS Code, making it the best neutral authoring/placement path;
Claude Code uses `.claude/skills/` (and reads others via import). An adapter that
did nothing but place the canonical `SKILL.md` at `.agents/skills/<slug>/` would
already work at a basic level on five of the six — the matrix below is about
faithfully carrying the *richer* fields.

## Field-support & mapping matrix

Canonical field → native representation per target. "body" = adapter moves it
into the Markdown body (not natively supported as metadata). "drop+note" = not
representable; recorded in the loss manifest. Citations point at the ecosystem
research doc that documented the target's capability.

| Canonical | Claude Code | Cursor | Codex | Windsurf/Devin | Antigravity | VS Code | MCP (SEP-2640, provisional) | Custom |
|---|---|---|---|---|---|---|---|---|
| `name` | `name` | `name` | `name` | `name` | `name` (opt; defaults to folder) | `name` (≤64) | resource `name` | native |
| `description` | `description` | `description` | `description` | `description` | `description` (3rd-person) | `description` (≤1024) | resource `description` | native |
| body (Markdown) | SKILL.md body | body | body | body | body | body | `SKILL.md` resource text | native |
| `activation_mode: auto` | default (auto-invoke) | default | implicit (`allow_implicit_invocation`) | default | default | default | client-decided | native |
| `activation_mode: manual` | `disable-model-invocation` | `disable-model-invocation` | `agents/openai.yaml` policy | body note | body note | `disable-model-invocation` | client-decided | native |
| `activation_conditions` (globs) | `paths` | `paths` | body | body | Glob rule mode | `applyTo`-style / body | body | native |
| `required_capabilities`→tools | `allowed-tools`/`disallowed-tools` | body (no per-skill tool grant found) | `agents/openai.yaml` tool deps | body | tool requirements (skill-declared) | tool sets / body | via server tool decl | native |
| `execution_tier: C` fork/isolation | `context: fork` + `agent`/`background` | subagent (no `fork` documented) | subagent policy | subagent (Preview) | `invoke_subagent` | `context: fork` / `agents` frontmatter | n/a | native |
| `inputs`/arguments | `arguments` | body | `argument-hint`-like | body | body | `argument-hint` | resource params | native |
| `adapter_hints.<t>` | applied | applied | applied | applied | applied | applied | applied | applied |
| `source_references`, `version_*`, `evaluation_criteria`, `depends_on_skills`, `conflicts_with`, `failure_handling`, `escalation` | body + drop-from-frontmatter (metadata, not vendor-native) | same | same | same | same | same | resource metadata | native (full) |
| path | `.claude/skills/<slug>/` | `.cursor/` or `.agents/skills/<slug>/` | `.agents/skills/<slug>/` | `.windsurf/` or `.agents/skills/<slug>/` | `.agents/skills/` or `~/.gemini/config/skills/` | `.github/skills/` or `.agents/skills/<slug>/` | `skill://<path>/SKILL.md` + `skill://index.json` | adapter-defined |

Notes on the matrix:

- **Metadata-only fields** (`source_references`, `version_*`, `evaluation_criteria`,
  `depends_on_skills`, `conflicts_with`, `failure_handling`, `escalation`,
  `reverify_triggers`) are *not* native frontmatter in any file-based vendor.
  Adapters keep them in `skill.yaml` for library tooling and, where a fact needs
  to reach the model at runtime (e.g. a version caveat, a failure-handling rule),
  ensure it is present in the **body** (it already is, per §3 of the spec). They
  are otherwise dropped from the emitted frontmatter with a loss-manifest note —
  a benign loss, since they are library-governance data, not runtime instructions.
- **Capability/tool mapping is the highest-risk projection.** Canonical
  `required_capabilities` are *abstract*; the adapter must translate to each
  vendor's tool vocabulary (which the research found are mutually incompatible
  and non-portable). Where a vendor has no per-skill tool-grant mechanism
  (Cursor as documented), the requirement is expressed as a body instruction and
  enforced by the runtime `capability-adapter` skill (`SK-ORCH-002`), not by
  frontmatter.
- **`execution_tier: C` skills** (browser, container, MCP-db) cannot be assumed
  runnable everywhere: Claude Code and Windsurf have no built-in browser
  automation, so a Playwright-based skill's adapter MUST emit its
  `capability_fallbacks` (e.g. "Playwright via external MCP server") into the
  body for those targets.

## Per-target specifics

### Claude Code
Richest native surface — accepts the most canonical fields directly
(`allowed-tools`, `context: fork`, `agent`, `background`, `paths`, `arguments`,
`hooks`, `metadata`). Lowest lossiness. Path `.claude/skills/<slug>/`.
[claude-code.md §1,§7,§10]

### Cursor
`name`/`description`/`paths`/`disable-model-invocation` (+ cosmetic `icon`/`color`).
No documented per-skill tool grant → capability needs go to body. Recognizes
`.agents/skills/` and legacy `.claude/skills/`. [cursor.md §1]

### Codex
`name`/`description` + optional `agents/openai.yaml` for invocation policy
(`allow_implicit_invocation`) and tool deps. `.agents/skills/`. Note Codex's MCP
config is TOML, not JSON — relevant only if the skill declares an MCP server
dependency. [codex.md §1,§10]

### Windsurf / Devin
`name`/`description`, progressive disclosure, `.windsurf/skills/` or
`.agents/skills/`. Mid-migration (Cascade→Devin Local); Devin Local dropped
Workflows/Memories — a skill relying on those (none in this library do by design)
would not project. Re-verify before trusting. [windsurf.md]

### Antigravity
`description` required and **written third-person** (adapter reformats the
canonical description accordingly); `name` optional. Skills may declare system
prompts / tool requirements / subagent delegation. `.agents/skills/` or
`~/.gemini/config/skills/`. [antigravity.md §1]

### VS Code agents
`name` (≤64), `description` (≤1024), `argument-hint`, `user-invocable`,
`disable-model-invocation`, `context: fork`. Reads `.github/skills/`,
`.claude/skills/`, `.agents/skills/`. Its own docs note cross-vendor ingestion is
lossy (e.g. hook matchers parsed-not-enforced) — our loss manifest makes the same
honesty explicit. [vscode.md §1,§8]

### MCP-based agents (provisional)
Not a file format. Per SEP-2640, the adapter exposes the skill as MCP
**resources** under a `skill://<slug>/SKILL.md` URI with a `skill://index.json`
discovery entry, served via `skills/list`/`skills/get`/`read_skill`. **Provisional:**
SEP-2640 was Accepted 2026-09-03 and is pre-reference-implementation; this target
MUST be re-checked against the ratified extension before shipping. Coordinates
with the same agentskills.io content format, so the body/`SKILL.md` transfers
directly. [mcp.md §1]

### Custom coding agents
The canonical format *is* their contract. A custom agent either (a) consumes
`skill.yaml` + `SKILL.md` directly (full fidelity — the only zero-loss target
besides having the raw source), or (b) ships an adapter following this document.
The spec is the stable interface they build to.

## Lossiness contract

- **L-1** Every adapter MUST emit a loss manifest listing each canonical field
  it did not represent natively and how it compensated (body / drop).
- **L-2** An adapter MUST NOT silently drop a field that carries runtime meaning
  (a version caveat, a failure-handling rule, a security constraint). Such fields
  MUST appear in the projected body if not in frontmatter.
- **L-3** Library-governance fields (`evaluation_criteria`, `source_references`,
  `reverify_triggers`, dependency graph) MAY be dropped from the projection
  (they live in `skill.yaml` for tooling) but MUST be noted in the manifest.
- **L-4** An adapter MUST NOT invent a target-native field the vendor does not
  document (no speculative frontmatter keys) — when in doubt, put it in the body.
- **L-5** If a skill's `execution_tier: C` capability is unavailable on the
  target, the adapter MUST project the `capability_fallbacks` guidance into the
  body so the skill degrades gracefully rather than assuming a capability the
  agent lacks.
