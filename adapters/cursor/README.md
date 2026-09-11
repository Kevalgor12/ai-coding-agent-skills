# Cursor adapter

Projects a canonical skill (`skill.yaml` + `SKILL.md`) into the format Cursor's
"Agent Skills" feature reads. Implementation: [`adapter.py`](./adapter.py).
Built on the shared engine in [`adapters/lib/`](../lib/) (`skill_loader.py`,
`loss_manifest.py`, `common.py`) — this adapter contains only Cursor-specific
projection logic, not skill-parsing logic.

## 1. Supported capabilities

`adapter.py` natively projects three canonical fields into Cursor's own
frontmatter dialect:

- **`name`** → frontmatter `name:`. Passed through unmodified (`truncate(...,
  None)` — no length cap is applied, since none is documented for Cursor).
- **`description`** → frontmatter `description:`. Same unmodified pass-through.
- **`activation_mode`** → when the canonical skill is `manual`, the adapter
  emits `disable-model-invocation: true`, which the research doc documents as
  the field that "forces explicit `/skill-name` invocation only, disabling
  automatic model-triggered use" (`research/agent-ecosystems/cursor.md` §1).
  When the canonical mode is `auto` (the default), no frontmatter key is
  needed — Cursor's own default behavior (automatic, description-driven
  activation) already matches — so the adapter emits nothing extra and still
  records the mapping as `native` in the loss manifest, since "rely on the
  target's own default" is a faithful, lossless projection of `auto`.

Both outcomes are recorded via `manifest.native(...)` in `project()`, matching
the field-mapping matrix's Cursor column in
`core/skill-specification/adapter-projection.md` (`name` → `name`,
`description` → `description`, `activation_mode: auto` → default,
`activation_mode: manual` → `disable-model-invocation`).

The Markdown body (Tier-1 content) is carried through byte-for-byte via
`skill.body`, per the spec's "body is portable as-is across all targets"
principle — Cursor needs no body transformation.

## 2. Limitations

The adapter's own module docstring states the central limitation plainly:

> Cursor has no documented per-skill tool-grant mechanism, so capability
> requirements go to the body rather than frontmatter (unlike Claude Code's
> `allowed-tools`).

Concretely, two canonical fields that Claude Code's adapter can place natively
in frontmatter have no frontmatter home in Cursor and are pushed to the body
instead:

- **`required_capabilities`** — `project()` calls `manifest.dropped(...)` with
  the note: *"Cursor has no documented per-skill tool-grant mechanism
  (research/agent-ecosystems/cursor.md §1); capability note lives in body,
  enforced by SK-ORCH-002 at runtime, not by Cursor itself."* The research doc
  backs this up directly: Cursor's documented built-in tools (file search, web
  search, read/edit files, run shell commands, browser control, image
  generation) are global agent capabilities, not something a `SKILL.md` file
  can scope per-skill — extensibility instead routes through MCP server
  registration (`cursor.md` §4, §10), which is a different mechanism entirely
  from a skill declaring "I need shell access." The requirement text itself is
  still written into the body via `capability_note()`, so the instruction
  reaches the model at runtime even without frontmatter enforcement — per the
  spec's L-2 rule that runtime-meaningful fields must never be silently
  dropped.
- **`execution_tier: C`** (fork/isolation) — also `manifest.dropped(...)`, with
  the note: *"No documented subagent/fork frontmatter field for Cursor; Tier C
  skills run without isolation here."* Cursor does have a Subagents feature
  (`cursor.md` §7 — Explore/Bash/Browser built-ins, plus custom `.cursor/
  agents/` definitions with a `readonly` flag), but nothing in the research
  ties a `SKILL.md` frontmatter key to spawning a subagent or forked context
  the way Claude Code's `context: fork` does — so this adapter does not invent
  one (per L-4: "MUST NOT invent a target-native field the vendor does not
  document").

This mirrors the field-mapping matrix's Cursor column in
`adapter-projection.md` exactly: `required_capabilities` → *"body (no
per-skill tool grant found)"*, `execution_tier: C` → *"subagent (no `fork`
documented)"*.

Other things this adapter does not attempt to project because Cursor has no
documented native slot for them: `inputs`/arguments (matrix marks these
"body" for Cursor too, though the current `project()` implementation does not
yet append an explicit inputs note — only `activation_conditions` and
capability requirements get dedicated body notes), and the full set of
library-governance fields (see §5 below).

## 3. Packaging format

**Path template:** `.agents/skills/<slug>/SKILL.md`, per
`PATH_TEMPLATE = ".agents/skills/{slug}/SKILL.md"` in `adapter.py`. The code
comment on that line notes the legacy fallback: `.cursor/skills/{slug}/
SKILL.md`. This matches both the research doc (`cursor.md` §1: discovery
locations are `.agents/skills/`, `.cursor/skills/`, plus user-level
equivalents and legacy `.claude/skills/`/`.codex/skills/` compatibility
paths) and `adapter-projection.md`'s "Common denominator" section, which
identifies `.agents/skills/<slug>/` as the neutral placement path recognized
by Cursor (among others), making it the adapter's primary target rather than
the more Cursor-specific `.cursor/` path.

**Frontmatter shape produced:**

```
---
name: <skill.name>
description: <skill.description>
disable-model-invocation: true   # only present if activation_mode == "manual"
---
<body><activation-conditions note><capability note><governance-fields note>
```

**Worked example** — running `project()` against `skills/observability`
(activation_mode `auto`, `required_capabilities: [file-read, file-write,
shell]`, `execution_tier: B`, several governance fields populated such as
`source_references`, `last_verified`, `owned_knowledge`,
`decision_framework_present`, `failure_handling`, `verification`,
`escalation`, `evaluation_criteria`, `related_skills`) would produce a single
output entry:

- **Path:** `.agents/skills/observability/SKILL.md`
- **Frontmatter:** just `name: Observability` and the full `description:`
  string copied verbatim — no `disable-model-invocation` line, since this
  skill's `activation_mode` is `auto`.
- **Body:** the skill's own Tier-1 Markdown content, unmodified, followed by
  three appended notes (via `lib/common.py`'s `body_note()` helper, each
  rendered as a `##`-headed bullet list):
  1. *"Activation guidance (library-defined, not natively enforced here)"* —
     listing the skill's `activation_conditions` bullets plus its
     `non_activation_conditions` prefixed `NOT:`.
  2. *"Capability requirements (enforced by SK-ORCH-002 at runtime, not this
     file)"* — `Requires: file-read, file-write, shell` (no
     `capability_fallbacks` are declared on this skill, so no further lines).
  3. *"Library metadata (canonical source only)"* — one bullet per populated
     governance-only field, e.g. *"Full `source_references` is defined in
     this skill's canonical `skill.yaml`, not reproduced here."*
- **Loss manifest** for this skill/target pair: `native` for `name`,
  `description`, and `activation_mode`; `body` for `activation_conditions`
  and `required_capabilities` (both actually land in the projected body via
  a note, so the manifest records them as `body`, not `drop+note`); `drop+note`
  for `execution_tier` (Tier A/B carries no separate isolation semantics
  beyond what `required_capabilities`' own body note already states) and each
  present governance-only field (`source_references`, `last_verified`,
  `owned_knowledge`, `decision_framework_present`, `failure_handling`,
  `verification`, `escalation`, `evaluation_criteria`, `related_skills`).

Note `execution_tier: B` on this particular example does not itself trigger
the isolation-specific loss note in `capability_note()`/the "Limitations"
section above — the adapter's `manifest.dropped("execution_tier", ...)` call
runs unconditionally for every skill, since Cursor has no fork/isolation
frontmatter slot regardless of which tier a skill declares; the practical
consequence (running without isolation) only matters for Tier C skills.

## 4. Loading behavior

Per `research/agent-ecosystems/cursor.md` §1 and §13: Cursor auto-scans a
fixed set of skill directories at startup with no manual registration step
beyond placing files correctly — project-level `.agents/skills/` and
`.cursor/skills/`, user/global-level `~/.agents/skills/` and
`~/.cursor/skills/`, plus legacy compatibility paths `.claude/skills/` and
`.codex/skills/`. Nested skill directories are supported for monorepos, with
each nested skill scoped to its containing directory (and, per the research
doc, that scoping cannot be manually overridden).

Once loaded, activation follows three paths (`cursor.md` §1): automatic
(the agent evaluates relevance from context against the skill's
`description`), manual (typing `/skill-name` for one message — the path this
adapter's `disable-model-invocation: true` output forces exclusively), and
Custom Modes (keeping a skill active for a whole session via a keyboard
shortcut). A documented limitation worth flagging for consumers of this
adapter's output: Cloud/Background Agents cannot see unsynced local skills or
anything under `~/.agents/skills/` — only project-level skills (or a
pre-baked worker image) reliably reach them, which is one more reason this
adapter defaults to the project-level `.agents/skills/<slug>/` path rather
than a user-level one.

## 5. Compatibility assumptions

This adapter assumes Cursor's Agent Skills frontmatter dialect as documented
in `cursor.md` §1: `name`, `description`, `paths` (glob restriction),
`disable-model-invocation`, and the cosmetic `icon`/`color` pair (used only
for Custom Mode badges).

**Deliberate omission:** `adapter.py` does not emit `icon` or `color`. This is
intentional, not an oversight — the canonical skill schema has no equivalent
field to project (there is no cosmetic-badge concept anywhere in
`skill.yaml`), and per the research doc these two fields are purely cosmetic
UI decoration for Custom Mode badges, carrying no runtime or activation
meaning. They fall outside every lossiness-contract obligation (L-1 through
L-5 all concern fields that exist on the canonical side and need
representation or an honest drop-note on the target side) precisely because
there is nothing canonical to lose here — this is scope the adapter never
had, not a gap in it.

The adapter also assumes the `paths` glob-restriction field exists (per
`cursor.md` §1 and the matrix's `activation_conditions` → `paths` row for
Cursor) but does not currently emit it — canonical `activation_conditions`
are natural-language bullets (e.g. "Making a system diagnosable in
production"), not file globs, so there is no faithful automatic mapping from
the canonical field to Cursor's `paths` syntax; the adapter instead keeps
`activation_conditions` as a body note (`manifest.body("activation_conditions",
...)`), which is a conservative, spec-compliant choice (any glob-shaped
canonical field would need explicit `adapter_hints.cursor` authoring, not
adapter guesswork — consistent with L-4).

## 6. Version considerations

`core/skill-specification/adapter-projection.md` carries a blanket **Snapshot
caveat (2026-09-09)**: vendor formats move fast, and "every mapping below MUST
be re-verified against current vendor docs before an adapter is trusted."
That caveat applies in full to this adapter — and Cursor is one of the
targets where it is least safe to assume stability:

- `research/agent-ecosystems/cursor.md` records that Cursor's Agent Skills
  feature itself is **very new** — it shipped in Cursor 2.4, dated January
  22, 2026 (`cursor.md` §1, citing the 2.4 changelog), only weeks before this
  research pass (2026-09-09) and this adapter's build. A feature this young
  is exactly the kind of surface likely to gain fields quickly.
- The research doc explicitly documents a **built-in migration tool**,
  `/migrate-to-skills`, that converts legacy "dynamic" rules and slash
  commands into the Skills format — a strong signal that Cursor is still
  actively consolidating multiple mechanisms (rules, commands, skills) into
  one, which makes near-term frontmatter changes plausible.
- Most relevant to this adapter's central limitation: the research doc gives
  no indication one way or the other about whether a **per-skill tool-grant
  mechanism** is planned. Cursor's current tool-approval model (`cursor.md`
  §4, §14) is global/session-level (Run Modes, allowlists, per-call approval),
  explicitly framed by Cursor's own docs as "best-effort guardrails... not a
  hard security boundary" — nothing suggests an imminent per-skill grant
  field, but nothing rules it out either, and if Cursor ever ships one, this
  adapter's `required_capabilities` → body-note mapping (and the
  corresponding row in `adapter-projection.md`'s matrix) would need to be
  revisited to promote that field from a body note to native frontmatter.
- Similarly, Cursor's Subagents feature (`cursor.md` §7) is also documented as
  recent and evolving (custom `.cursor/agents/` definitions, `readonly` and
  `is_background` flags, nesting restricted to one level) — if a future
  Cursor version ties `SKILL.md` frontmatter directly to subagent/fork
  invocation, the `execution_tier: C` → drop+note mapping would likewise need
  re-verification rather than being assumed permanent.

Until such re-verification happens, this adapter should be treated as
accurate to the 2026-09-09 research snapshot only.
