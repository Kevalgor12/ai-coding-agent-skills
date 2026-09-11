# Codex adapter

Projects a canonical skill (`skill.yaml` + `SKILL.md`) into the file layout
OpenAI Codex discovers natively: a `SKILL.md` plus an optional
`agents/openai.yaml` invocation-policy sidecar. Implemented in
[`adapter.py`](./adapter.py); shares the loader/loss-manifest engine in
[`adapters/lib/`](../lib/). Grounded in
[`research/agent-ecosystems/codex.md`](../../research/agent-ecosystems/codex.md)
and the Codex subsection of
[`core/skill-specification/adapter-projection.md`](../../core/skill-specification/adapter-projection.md).

## 1. Supported capabilities

Natively, in `SKILL.md` frontmatter:

- **`name`** — carried through unchanged (`manifest.native("name")`).
- **`description`** — carried through unchanged (`manifest.native("description")`);
  this is also the implicit-invocation trigger signal Codex's skill index
  matches against (codex.md §1).

Everything else Codex has a documented slot for lives in the *optional*
`agents/openai.yaml` sidecar, not in `SKILL.md` frontmatter — Codex's own
`SKILL.md` schema only documents `name` + `description` (codex.md §1):

- **`activation_mode`** — when a skill is `manual`, the adapter writes
  `allow_implicit_invocation: false` into the sidecar, mapping onto Codex's
  documented explicit-vs-implicit invocation split (codex.md §1). When a
  skill is `auto` (the library default), Codex's own default behavior
  already matches — implicit invocation is on by default — so nothing needs
  to be written; the manifest still records `activation_mode` as `native`
  in both branches, since "no sidecar line" *is* the correct native
  representation of the default case, not an omission.
- **`required_capabilities`** — written as a `tool_dependencies:` list in
  the sidecar. Per the loss manifest note the adapter attaches
  (`lib/common.py`'s `capability_note` also puts the same information in
  the body as a fallback), this is recorded as *a declared need*, not a
  per-tool grant — Codex's actual tool-access enforcement is a separate
  mechanism (MCP `enabled_tools`/`default_tools_approval_mode`, or the
  built-in tool set), per codex.md §10 and §14 cross-ecosystem note 4.

The sidecar is emitted **only when one of those two conditions is actually
true** (`skill.activation_mode == "manual"` or `required_capabilities` is
non-empty) — not for every skill, per L-4 (don't invent config the
projection doesn't need). See §3 for what this looks like in practice
against this library's actual skill population.

## 2. Limitations

**`execution_tier` (the Tier C subagent-policy case) is deliberately not
auto-generated.** The adapter records it as `drop+note` unconditionally
(`adapter.py` lines 67–72), with this note attached to the loss manifest:

> Subagent policy for Tier C skills is a Codex-side configuration this
> adapter does not attempt to author automatically (research/agent-ecosystems/codex.md
> notes subagent policy exists but its exact schema needs re-verification
> before an adapter should generate it).

This is a known gap, not an oversight. Codex does have a real subagent
system — custom agents defined as TOML files under `~/.codex/agents/` or
`.codex/agents/` with `name`/`description`/`developer_instructions` plus
optional `model`, `sandbox_mode`, `skills.config`, etc. (codex.md §7) — but
mapping a canonical `execution_tier: C` skill onto that system is a
two-object translation (the skill file *and* a separate agent-definition
file), and the research pass flagged the exact subagent-definition schema
as needing independent re-verification before an adapter should generate
it speculatively. Per the Lossiness contract's L-4 ("don't invent a
target-native field the vendor doesn't document a use for"), this adapter
declines to guess at that schema rather than emit a `.codex/agents/*.toml`
file that might not match Codex's actual expectations. A Tier C skill
still projects successfully — it just runs as an ordinary (non-forked)
skill invocation on Codex until this gap is closed.

Two smaller, already-covered limitations worth naming explicitly:

- **`activation_conditions`** (glob/semantic triggers) has no documented
  Codex frontmatter field, so it is pushed into the body as a note rather
  than enforced structurally (`activation_conditions_note`, `manifest.body(...)`).
- **Governance-only fields** (`source_references`, `evaluation_criteria`,
  `depends_on_skills`, `skill_version`, etc.) are dropped from the
  projected frontmatter/sidecar entirely, per L-3 — their canonical home
  remains `skill.yaml`, and the projected body carries only a pointer back
  to that fact, not their content.

## 3. Packaging format

```
.agents/skills/<slug>/
├── SKILL.md                  # always emitted
└── agents/
    └── openai.yaml            # emitted only if activation_mode=manual
                                # or required_capabilities is non-empty
```

This is the same `.agents/skills/` root the adapter-projection matrix
identifies as the shared placement path across Codex, Cursor, Windsurf,
Antigravity, and VS Code (adapter-projection.md, "Common denominator").

**Worked example 1 — a skill with no `required_capabilities` and
`activation_mode: auto`.** For such a skill, `project()` would emit a
single file, `.agents/skills/<slug>/SKILL.md`, containing only the
`name`/`description` frontmatter plus the body (with its activation-guidance
and governance notes appended) — no `agents/` directory at all, since
neither trigger condition for the sidecar is met.

*Caveat on this example:* as of this snapshot, no skill actually in
`skills/` has an empty `required_capabilities` list — every skill in the
library declares at least `file-read`. Running the adapter today against,
e.g., `skills/git-conventions` (Tier A, `required_capabilities: [file-read]`,
`activation_mode: auto`) therefore *does* produce a sidecar:

```yaml
# .agents/skills/git-conventions/agents/openai.yaml
tool_dependencies:
  - file-read
```

So in current practice, given how this library populates
`required_capabilities`, the adapter emits a sidecar for every skill it
projects — the "no sidecar" branch is real and exercised by the code (and
by any future skill authored with zero declared capabilities), but no
example of it exists in the library's actual skill set today.

**Worked example 2 — a Tier B skill with richer `required_capabilities`.**
Running the adapter against `skills/containerization` (Tier B,
`required_capabilities: [file-read, file-write, shell]`, `activation_mode: auto`)
produces:

```yaml
# .agents/skills/containerization/agents/openai.yaml
tool_dependencies:
  - file-read
  - file-write
  - shell
```

And against a `manual`-activation skill, e.g. `skills/project-management`
(`activation_mode: manual`, `required_capabilities: [file-read, file-write, git]`):

```yaml
# .agents/skills/project-management/agents/openai.yaml
allow_implicit_invocation: false
tool_dependencies:
  - file-read
  - file-write
  - git
```

In every case, `SKILL.md`'s frontmatter is unaffected by the sidecar's
presence or absence — it always carries just `name` + `description`.

## 4. Loading behavior

Per codex.md §1, Codex scans for skills hierarchically across scopes —
repo `.agents/skills` (walking from CWD up to the git root), user
`$HOME/.agents/skills`, admin `/etc/codex/skills`, and a bundled system
tier — and builds a lightweight index of `name` + `description` only,
capped at ≤2% of context or 8,000 characters ("progressive disclosure").
The full `SKILL.md` body is loaded only once a skill is actually selected,
either explicitly (`$skill-name` in the CLI, `@skill-name` in ChatGPT, or a
sidebar picker) or implicitly, with the `description` field acting as the
match signal against the task at hand.

The `agents/openai.yaml` sidecar this adapter emits is consulted as part of
that same selection/invocation step: `allow_implicit_invocation: false`
suppresses the implicit path (matching the library's `activation_mode:
manual`), and a `skill_approval` control inside Codex's broader
`approval_policy` config can independently require user approval before any
skill — sidecar or not — actually runs (codex.md §1). There is also a
`skill_approval` **gate on trust**: project-level config, `AGENTS.md`, and
skills only load at all for projects Codex considers trusted; untrusted
projects silently fall back to user/system-scope skills only (codex.md §14)
— something to keep in mind when a projected skill "doesn't show up" in a
given repo.

One config-format note carried over from the per-target-specifics section
of `adapter-projection.md`, in case it becomes relevant to a future
capability that needs an MCP server: **Codex's MCP configuration is TOML**
(`~/.codex/config.toml` / `.codex/config.toml`, one `[mcp_servers.<name>]`
table per server — codex.md §10), not the JSON most other targets use. This
adapter does not itself emit any MCP server configuration — canonical
`required_capabilities` are projected only as the `tool_dependencies` list
in `agents/openai.yaml` — but an adapter change that ever needs to *wire up*
an actual MCP server for a skill would need to target that TOML file, not a
JSON one.

## 5. Compatibility assumptions

This adapter assumes Codex's documented `agents/openai.yaml` sidecar
actually supports two things, based on codex.md §1's description of the
file ("optional — invocation policy, tool deps, allow_implicit_invocation"):

- **`allow_implicit_invocation`** — the research doc names this field
  explicitly, so the adapter treats `allow_implicit_invocation: false` as a
  confirmed, spellable key for suppressing implicit invocation.
- **`tool_dependencies`** — the research doc only describes this
  conceptually ("tool deps"); it does not quote Codex's literal YAML key
  name or nesting shape for that field. This adapter's choice of a
  top-level `tool_dependencies:` list (one canonical capability name per
  line) is this library's own naming convention, not a verified quote from
  Codex documentation, and should be re-verified against Codex's actual
  `agents/openai.yaml` schema before being relied on for real
  enforcement — the loss-manifest note calls this out explicitly
  ("Codex's own policy enforcement is separate from this list").

The adapter also assumes canonical capability names (`file-read`,
`file-write`, `shell`, `git`, …) are meaningful to place in that list even
though Codex's own extension model for *custom* tools is MCP-only — there
is no generic "arbitrary tool" registration outside MCP plus Codex's fixed
built-in tool set (codex.md §4, §14 cross-ecosystem note 4). A capability
like `shell` is realized on Codex by its built-in Shell tool rather than an
MCP server, so `tool_dependencies` here is closer to a declarative
"this skill needs these capabilities to work" hint than an actual
tool-grant mechanism — consistent with how the matrix in
`adapter-projection.md` describes capability mapping generally as "the
highest-risk projection."

## 6. Version considerations

`adapter-projection.md`'s snapshot caveat (2026-09-09) applies to this
adapter without modification, and codex.md adds Codex-specific reasons the
caveat matters more than average here:

- Codex's own docs were mid-migration at research time: `developers.openai.com/codex/*`
  308-redirects to `learn.chatgpt.com/docs/*`, and the research doc flags
  that redirect as possibly non-permanent.
- The public skills catalogue repo (`github.com/openai/skills`) states it
  is being deprecated in favor of an "OpenAI Plugins" repository — seen
  only secondhand via one fetch, not cross-checked against a second
  official source (codex.md §1). If that consolidation changes how/where
  skills are distributed, it could affect the packaging conventions this
  adapter targets.
- The `apply_patch` file-edit tool's exact format could not be independently
  verified at research time (the GitHub doc page 404'd) — not directly
  relevant to this adapter's output, but a sign that Codex's own
  documentation surface was unstable at snapshot time.
- Most directly: the subagent/Tier C schema this adapter declines to guess
  at (§2 above) is exactly the kind of thing this caveat exists for — any
  future attempt to close that gap should start from current, not
  snapshot-date, Codex documentation.

Re-verify `agents/openai.yaml`'s actual schema (§5) and the subagent
TOML schema (§2) against live Codex documentation before trusting this
adapter's sidecar generation in a production pipeline targeting a Codex
release newer than this snapshot.
