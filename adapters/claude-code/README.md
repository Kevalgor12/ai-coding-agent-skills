# Claude Code Adapter

Projects a canonical skill (`skill.yaml` + `SKILL.md` + resources) into Claude
Code's native `SKILL.md` format. Implementation: [`adapter.py`](./adapter.py),
built on the shared engine in [`adapters/lib/`](../lib/) (`skill_loader.py`,
`loss_manifest.py`, `common.py`). Per
[`core/skill-specification/adapter-projection.md`](../../core/skill-specification/adapter-projection.md),
Claude Code is documented as "the richest native target — lowest lossiness of
the six" file-based vendors, because it natively understands more of the
canonical schema (tool scoping, isolated-execution semantics, invocation
control) than any other target in this library. This document describes what
`adapter.py` actually does, not the full feature surface Claude Code exposes —
see Limitations below for the gap between the two.

Grounded in [`research/agent-ecosystems/claude-code.md`](../../research/agent-ecosystems/claude-code.md)
(research date 2026-09-09) and the Claude Code column of the field-mapping
matrix in `adapter-projection.md`.

## 1. Supported capabilities

`adapter.py`'s `project()` function natively represents these canonical
fields in Claude Code frontmatter (each recorded `manifest.native(...)` in the
loss manifest):

- **`name`** → frontmatter `name`. Passed through `truncate(skill.name, None)`
  — no length cap is applied, because (per the code's own comment) "Claude
  Code documents no hard name limit."
- **`description`** → frontmatter `description`. Same unlimited-length
  treatment. This is the field the research doc says drives Claude Code's
  automatic-invocation matching, so it is carried through verbatim.
- **`activation_mode`**:
  - `auto` → nothing is emitted; auto-invocation is Claude Code's own
    default, so the field is still recorded `native` in the manifest even
    though no frontmatter line is written.
  - `manual` → emits `disable-model-invocation: true`, matching the research
    doc's documented "only user can invoke via `/name`" semantics.
- **`required_capabilities` → `allowed-tools`**: a small, hard-coded map —
  `{"shell": "Bash", "file-read": "Read", "file-write": "Edit", "git": "Bash"}`
  — converts canonical capability names into Claude Code tool names. If one
  or more capabilities resolve, the adapter emits
  `allowed-tools: [Tool1, Tool2, ...]` and records `required_capabilities` as
  `native`.
- **`execution_tier: C` → `context: fork`**: emitted *only* when
  `skill.yaml`'s `adapter_hints.claude-code.fork` is explicitly truthy. The
  adapter never infers fork mode from `execution_tier: C` alone — see
  Limitations.
- **`adapter_hints.claude-code.allowed_tools`**: an author-supplied escape
  hatch. If a skill declares no `required_capabilities` that map through the
  built-in `tool_map` (i.e. `known_tools` is empty), but the skill's own
  `adapter_hints.claude-code.allowed_tools` list is set, that list is emitted
  as `allowed-tools` instead. This lets a skill author hand-declare Claude
  Code tool names (including MCP tool names like `mcp__server__tool`, which
  the built-in `tool_map` has no entry for) without the adapter guessing.
- **Body (Tier-1 Markdown)**: the canonical `SKILL.md` body is carried through
  unmodified and then appended to (see §3) — this is the portable layer the
  spec says is "portable as-is across all targets."

## 2. Limitations

Fields `adapter.py` does **not** project natively, and why (per the code and
the Lossiness contract L-1..L-5 in `adapter-projection.md`):

- **Governance-only fields** (from `adapters/lib/skill_loader.py`'s
  `GOVERNANCE_ONLY_FIELDS`): `source_references`, `last_verified`,
  `reverify_triggers`, `covered_versions`, `version_sensitive_claims`,
  `evaluation_criteria`, `depends_on_skills`, `conflicts_with`,
  `related_skills`, `failure_handling`, `escalation`, `verification`,
  `owned_knowledge`, `decision_framework_present`, `grounding`,
  `skill_version`, `spec_version`. Whichever of these a given skill actually
  populates gets `manifest.dropped(f, "Library-governance field; canonical
  source is skill.yaml.")` — dropped from frontmatter because no file-based
  vendor treats them as native metadata (L-3), but `governance_fields_note()`
  still appends a body pointer back to `skill.yaml` for each one so nothing
  disappears silently.
- **Capabilities with no tool-name mapping**: any `required_capabilities`
  entry outside `{shell, file-read, file-write, git}` — e.g. `browser`,
  `container`, `network`, `mcp-db` style capabilities — has no entry in the
  adapter's `tool_map`. Per the code's own comment, these are "left to the
  runtime capability-adapter skill (SK-ORCH-002) rather than guessed at here
  (L-4: don't invent a target-native field the vendor doesn't document a
  mapping for)." They are pushed into the body via `manifest.body(...)`, not
  dropped, satisfying L-2.
- **Tier C skills with no explicit `adapter_hints.claude-code.fork`**: the
  adapter does not default these to `context: fork`. Because
  `execution_tier` is a `RUNTIME_MEANINGFUL_FIELD`, it can't be silently
  dropped for a Tier C skill (L-2) — instead the adapter records a `body`
  loss-manifest entry noting "Tier C skill with no explicit
  adapter_hints.claude-code.fork — projected without context:fork; author
  should confirm this is intended." No `context: fork` line is written. (For
  Tier A/B skills, by contrast, `execution_tier` is genuinely `dropped` with
  no body note at all — the code's comment is "Tier A/B — no fork semantics
  needed," i.e. there's nothing runtime-meaningful to preserve.)
- **`activation_conditions` / `non_activation_conditions`**: always pushed
  into a body note (`activation_conditions_note`), never into frontmatter,
  regardless of `activation_mode`. The code's inline comment states why:
  "Claude Code has no glob-free semantic-condition frontmatter field for
  these" — Claude Code's only native conditional-activation mechanism is the
  glob-based `paths` field (per the research doc and the matrix), which this
  adapter does not populate, since the canonical `activation_conditions` are
  free-text semantic conditions, not path globs.
- **`inputs` / `outputs`**: `skill.yaml`'s `inputs` and `outputs` fields are
  not referenced anywhere in `adapter.py` — not projected into frontmatter,
  not pushed into a body note, and not recorded in the loss manifest at all.
  This is a real gap against the field-mapping matrix, which shows
  `inputs`/arguments mapping to Claude Code's native `arguments` frontmatter
  field — the current adapter implementation does not perform that mapping.
- **Other Claude-Code-native frontmatter the research doc documents but this
  adapter does not populate**: `paths` (glob auto-activation), `agent:` /
  `background:` (fork-mode agent selection — the adapter only ever emits bare
  `context: fork`, never these companions), `hooks`, `model`, `effort`,
  `metadata`, `license`, `compatibility`. None of these have a corresponding
  canonical field the adapter reads, so their absence isn't a lossiness-contract
  violation, but it does mean the adapter uses only a subset of Claude Code's
  documented Skill frontmatter surface.

## 3. Packaging format

**Path**: `PATH_TEMPLATE = ".claude/skills/{slug}/SKILL.md"` — one file per
skill, at `.claude/skills/<slug>/SKILL.md`, `slug` being the canonical skill's
directory name (`skill.slug`, e.g. `observability`).

**Frontmatter shape** (lines are assembled in this fixed order, then joined
and closed with a final `---`):

```
---
name: <skill.name>
description: <skill.description>
disable-model-invocation: true          # only if activation_mode == manual
allowed-tools: [Tool1, Tool2, ...]      # only if required_capabilities mapped, or hint fallback
context: fork                           # only if adapter_hints.claude-code.fork is truthy
---
```

**Body**: the canonical `SKILL.md` body, unmodified, with three note blocks
appended in this order: an "Activation guidance" note, a "Capability
requirements" note, and (if any governance-only fields are populated) a
"Library metadata" note.

**Worked example** — running `project()` against `skills/observability`
(`SK-QA-004`, `activation_mode: auto`, `execution_tier: B`,
`required_capabilities: [file-read, file-write, shell]`, no
`adapter_hints.claude-code`) would produce
`.claude/skills/observability/SKILL.md`:

```
---
name: Observability
description: Instrument systems for logging, metrics, tracing, and error monitoring — choose the right signal(s) for the diagnostic need, avoid high-cardinality and PII-leakage pitfalls, and design actionable alerting. Use when making a system diagnosable in production or debugging a production issue. Explicitly does not cover resilience/fault-tolerance patterns (retries, circuit breakers), a separate, still-unresearched gap in this library.
allowed-tools: [Read, Edit, Bash]
---

## Purpose & scope

Instrument systems with logging, metrics, tracing, and error monitoring so
production behavior is diagnosable — tool-neutral, specialized by
[opentelemetry](../opentelemetry/SKILL.md), [prometheus](../prometheus/SKILL.md),
...(original body, unmodified)...

## Activation guidance (library-defined, not natively enforced here)

- Making a system diagnosable in production
- Debugging a production issue that needs logging/metrics/tracing evidence
- Adding or reviewing an observability instrumentation layer
- NOT: Local/throwaway code with no production diagnosability need
- NOT: A request for resilience/fault-tolerance patterns (retries, circuit breakers, timeouts, bulkheads) rather than observability instrumentation — a separate, still-open research gap not covered here

## Capability requirements (enforced by SK-ORCH-002 at runtime, not this file)

- Requires: file-read, file-write, shell

## Library metadata (canonical source only)

- Full `source_references` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `last_verified` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `evaluation_criteria` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `related_skills` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `failure_handling` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `escalation` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `verification` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `owned_knowledge` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `decision_framework_present` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `grounding` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `skill_version` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- Full `spec_version` is defined in this skill's canonical `skill.yaml`, not reproduced here.
```

Note the `description` line is emitted as a single unwrapped line (valid
YAML, just long) — `skill.description` is already a folded scalar by the time
`yaml.safe_load` parses `skill.yaml`'s `>-` block, and the adapter does no
further wrapping.

Alongside the projected file, `project()` returns a `LossManifest` object
(see [`adapters/lib/loss_manifest.py`](../lib/loss_manifest.py)) recording
every field above as `native`, `body`, or `drop+note` — this manifest is a
separate artifact from the `SKILL.md`, not embedded in it.

## 4. Loading behavior

Per the research doc's Skills section:

- **Discovery locations**, in precedence order: Enterprise-managed
  `.claude/skills/` > Personal `~/.claude/skills/<name>/SKILL.md` (all local
  projects) > **Project `.claude/skills/<name>/SKILL.md`** (this adapter's
  target — loaded from the launch directory up to the repo root) > Bundled.
  Nested `<subdir>/.claude/skills/<name>/SKILL.md` also loads lazily when
  Claude reads files in that subdirectory.
- **Live reload**: Claude Code file-watches skill directories and
  auto-reloads them mid-session (with some exceptions for plugin-bundled
  skills, which need `/reload-plugins`).
- **Auto-invoke is the default**: Claude matches the user's request against
  the `description` of every loaded skill (a one-line index loaded at session
  start — not the full body) and decides whether to invoke it. This is why
  the adapter treats `activation_mode: auto` as needing no frontmatter at
  all — it's what Claude Code already does absent any override.
- **Manual mode**: setting `disable-model-invocation: true` (what this
  adapter emits for `activation_mode: manual`) restricts invocation to the
  user explicitly typing `/skill-name [args]` — Claude itself can no longer
  auto-trigger it.
- **Stacking**: up to 6 skills can be invoked in a single message (documented
  as of v2.1.199+).
- **Context persistence**: once invoked, the rendered `SKILL.md` body enters
  the conversation as a message and is not re-read on later turns. The
  skill-description index used for auto-invocation does not survive
  `/compact`; only skills already invoked get re-injected post-compact
  (capped at 5,000 tokens each, 25,000 total).

## 5. Compatibility assumptions

This adapter assumes a reasonably current Claude Code build that supports:

- `allowed-tools` as a scoped, per-skill tool grant — documented in the
  research doc as clearing after the next message (§1, §4).
- `disable-model-invocation: true` as the current, non-deprecated key for
  manual-only invocation (research doc §1, and the matrix's
  `activation_mode: manual` row).
- `context: fork` as valid Skill frontmatter for isolated/forked execution.
  **Note an extrapolation here**: every example in the research doc shows
  `context: fork` documented alongside `agent:` and `background:` as a
  trio ("`context: fork` + `agent:` + `background:` (run the skill in an
  isolated subagent)"). `adapter.py` only ever emits bare `context: fork`
  with no `agent:`/`background:` companions, which assumes Claude Code
  applies sensible defaults for those when omitted — this specific
  combination (fork with no explicit agent/background) is not directly
  confirmed by a documented example in the research pass.
- No enforced length ceiling on `name` or `description` — the adapter
  passes both through `truncate(..., None)`, i.e. never truncates. This
  matches the research doc's framing of `description` as merely
  "recommended" with no stated cap (contrast Claude Code's own docs being
  silent on a name/description limit, versus e.g. VS Code's documented
  ≤64/≤1024 character caps noted elsewhere in the matrix). If a future
  Claude Code release adds a length cap, this adapter would not enforce it
  and would emit an over-length field unchanged.
- Tool names `Bash`, `Read`, `Edit` remain the correct, stable built-in tool
  identifiers (research doc §4's tools-reference listing) — the `tool_map`
  hard-codes these three plus `git → Bash`.

## 6. Version considerations

`core/skill-specification/adapter-projection.md` carries a standing
**snapshot caveat (2026-09-09)**: "vendor formats move fast... every mapping
below MUST be re-verified against current vendor docs before an adapter is
trusted." For this specific target, that caveat cashes out as follows:

- The research doc itself (`research/agent-ecosystems/claude-code.md`, also
  dated 2026-09-09) opens by noting Anthropic **appears to be mid-migration**
  of its own documentation host, from `docs.claude.com/en/docs/claude-code/...`
  to `code.claude.com/docs/en/...` — i.e. the primary source this adapter is
  grounded in was itself flagged as being in flux at research time.
- Several features the research doc cites are pinned to specific Claude Code
  versions (skill stacking cap of 6 → v2.1.199+; `/skill-doctor` → v2.1.252+;
  `/import` cross-agent config carryover → v2.1.213+). `adapter.py` has no
  version gate or check of any kind — it assumes whatever Claude Code build
  consumes its output is at least that current. An older install may not
  honor everything this README describes.
- The research doc explicitly flags one relevant fact as **not fully
  verified**: the exact command for listing/managing subagents (possibly
  `/agents`) — irrelevant to this adapter's own output, but a sign of the
  broader caution the doc already recommends given how fast subagent/fork
  behavior (the mechanism behind `context: fork`) is evolving.
- The research doc's own "distinctly Claude-Code-specific" section singles
  out the SKILL.md frontmatter surface itself (`context: fork`, `agent:`,
  `background:`, `disable-model-invocation`, `paths`, `arguments`, the
  `$ARGUMENTS`/`${CLAUDE_*}` substitution vocabulary) as "a rich,
  Claude-Code-specific superset layered on top of the more minimal 'Agent
  Skills open standard'" — and separately notes that Anthropic's own claim
  that Skills "follow the Agent Skills open standard" was **not verified
  directly** against `agentskills.io` in this research pass. Before trusting
  this adapter's `allowed-tools`/`context: fork` behavior against a future
  Claude Code release, re-check both the current `code.claude.com/docs/en/skills`
  page and whether the open-standard claim still holds as described.
- Recommendation: before shipping any change to `adapter.py`, re-verify (a)
  the `allowed-tools` tool-name vocabulary (MCP tool names in particular,
  `mcp__server__tool`, are not in the adapter's hard-coded `tool_map` and
  rely entirely on the `adapter_hints` escape hatch), and (b) whether
  `context: fork` without an explicit `agent:`/`background:` pairing is
  still (or was ever) a documented, supported combination.
