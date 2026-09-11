# Windsurf / Devin adapter

Projects a canonical skill (`skill.yaml` + `SKILL.md` + resources) onto the
Windsurf/Devin Desktop "Skills" file format. Implementation:
[`adapter.py`](adapter.py). Field mapping and citations:
[`core/skill-specification/adapter-projection.md`](../../core/skill-specification/adapter-projection.md#windsurf--devin),
grounded in [`research/agent-ecosystems/windsurf.md`](../../research/agent-ecosystems/windsurf.md).

**Read this first:** at research time (2026-09-09), "Windsurf" was mid-rebrand
to Devin Desktop, with two overlapping agent runtimes live in the same
product — the legacy **Cascade** agent and the newer **Devin Local** agent —
and the vendor's own documentation domain (`docs.windsurf.com`) 307-redirecting
wholesale to `docs.devin.ai`. That instability is the reason this is the most
conservative (highest-lossiness) of the six file-based adapters in this
library: every field below that isn't asserted "native" was downgraded
specifically because the research could not confirm a stable mechanism on
either side of the rebrand, not because of an arbitrary choice to be
cautious. Where the other five adapters can point at one settled vendor
surface, this one is deliberately hedging against two runtimes that don't
fully agree with each other.

## 1. Supported capabilities

Only two canonical fields are asserted as natively supported, both citing the
Skills feature documented for **both** agents (Cascade and Devin Local list
Skills explicitly under "Supported" — `windsurf.md` lines 17, 28):

| Canonical field | Native representation |
|---|---|
| `name` | YAML frontmatter `name` key |
| `description` | YAML frontmatter `description` key |
| body (Markdown) | `SKILL.md` body, verbatim |
| `activation_mode: auto` | Default behavior — Cascade "matches request against skill descriptions" automatically (`windsurf.md` line 24); Devin Local inherits Skills support with no documented change to this default |

`adapter.py` reflects this directly: `name`/`description` are always marked
`manifest.native(...)`, and `activation_mode` is marked native only in the
`auto` (default) branch.

## 2. Limitations

Everything else the canonical schema can express is either pushed into the
Markdown body or dropped from frontmatter entirely, per the loss-manifest
contract (`core/skill-specification/adapter-projection.md`, Lossiness
contract L-1..L-5):

- **`activation_mode: manual`** — downgraded to a body-level warning rather
  than asserted as a native manual-invocation control. Claude Code, Cursor,
  and VS Code all map this to a documented `disable-model-invocation` field;
  the research found no Windsurf/Devin equivalent at research time (no such
  key appears anywhere in the Skills, Rules, or Workflows documentation
  surveyed in `windsurf.md`). Rather than guess at an undocumented frontmatter
  key — which the Lossiness contract's L-4 explicitly forbids ("MUST NOT
  invent a target-native field the vendor does not document") — the adapter
  appends an "## Activation note" section to the body telling the skill
  (and a human reader) that it should be treated as auto-invocable here until
  re-verified, and that `@skill-name` manual invocation is available as a
  weaker substitute. The loss manifest records this as a `body` action, not
  `native`.
- **`activation_conditions` / `non_activation_conditions`** — no
  glob/semantic-condition frontmatter field is documented for Windsurf
  Skills (unlike Cursor/Claude Code's `paths`, or AGENTS.md's directory-glob
  behavior, which is a *separate* mechanism from Skills). Rendered into the
  body via the shared `activation_conditions_note()` helper; recorded in the
  manifest as `body`.
- **`required_capabilities`** — dropped from frontmatter entirely
  (`manifest.dropped(...)`). No documented per-skill tool-grant mechanism for
  Windsurf/Devin Skills was found at research time — the field-mapping matrix
  lists this cell the same way for Windsurf/Devin as for Cursor (`body (no
  per-skill tool grant found)`). A capability note still lands in the body
  (via `capability_note()`) so the requirement isn't silently lost per L-2,
  but it is enforced only by convention / the runtime `capability-adapter`
  skill, never by the host.
- **`execution_tier`** (fork/subagent isolation) — also dropped, with a note
  citing that Devin Local's subagent support was documented as
  **"Subagents (Preview)"** at research time (`windsurf.md` lines 109-113,
  197) — i.e. still a beta toggle, not a GA mechanism an adapter should
  assume is present. Cascade (the other live runtime) has no user-facing
  delegation mechanism at all, only an internal planning sub-model
  (`windsurf.md` line 116). With neither runtime offering a confirmed stable
  surface, the adapter does not assert this field.
- **Governance-only fields** (`source_references`, `version_*`,
  `evaluation_criteria`, `depends_on_skills`, `conflicts_with`,
  `failure_handling`, `escalation`, etc.) — dropped from frontmatter like on
  every other target (they have no vendor-native home anywhere), each with a
  `governance_fields_note()` pointer back to `skill.yaml` per L-3.

Net effect: of the canonical fields with a matrix cell, only `name`,
`description`, and (conditionally) `activation_mode` ever reach `native` in
this adapter's loss manifest — every other populated field resolves to
`body` or `drop+note`. That is a strictly higher body/drop ratio than
Cursor, Codex, Claude Code, Antigravity, or VS Code, which is what makes this
the most conservative of the six.

## 3. Packaging format

```
PATH_TEMPLATE = ".agents/skills/{slug}/SKILL.md"
```

The adapter targets the vendor-neutral `.agents/skills/<slug>/SKILL.md`
convention — per `adapter-projection.md`'s "Common denominator" section,
this path is recognized by Windsurf alongside Cursor, Codex, Antigravity, and
VS Code. The legacy, Windsurf-specific fallback location is
`.windsurf/skills/<slug>/SKILL.md` (workspace-scoped; still read per
`windsurf.md` line 21/158) — noted in a comment in `adapter.py` but not the
path the adapter emits to, since `.agents/skills/` is the more future-proof
choice given the rebrand.

Emitted file shape: a `---`-delimited YAML frontmatter block with exactly
`name` and `description`, followed by the skill's Markdown body plus any
appended body notes (activation note, activation-conditions note,
capability note, governance-fields note — in that order).

**Worked example.** Projecting the `project-management` skill
(`skills/project-management/skill.yaml`, `activation_mode: manual`) produces
`.agents/skills/project-management/SKILL.md`:

```markdown
---
name: Project management
description: >-
  Frame work as issues/milestones, summarize status, and draft changelog or
  release-note entries for a longer-running effort. Use when an effort spans
  more than a single change and needs tracking, or when release notes are
  requested. Not for a one-off change, not for commit/branch text
  (git-conventions), and not for git operations (git-workflow).
---

## Purpose & scope
... (original SKILL.md body) ...

## Activation note

This skill is manual-invocation-only in its canonical definition. No
Windsurf-documented equivalent to Claude Code's `disable-model-invocation`
was confirmed at research time — treat this skill as auto-invocable here
until re-verified, and prefer explicit user invocation where the host
supports it.

## Activation guidance (library-defined, not natively enforced here)

- The effort is long-running or multi-session and benefits from tracked status
- The user asks for issue/milestone framing, a status summary, or release notes/changelog
- A completed change needs a changelog entry
- NOT: A one-off, single-session change with nothing to track over time
- NOT: No issue tracker or changelog convention is in use and none was requested
- NOT: The ask is about commit/branch text (route to git-conventions) or git operations/PR mechanics (route to git-workflow)

## Capability requirements (enforced by SK-ORCH-002 at runtime, not this file)

- No special capabilities required.

## Library metadata (canonical source only)

- Full `skill_version` is defined in this skill's canonical `skill.yaml`, not reproduced here.
- ...
```

The corresponding loss manifest for this projection records `name` and
`description` as `native`; `activation_mode`, `activation_conditions`, and
`required_capabilities` as `body`; `execution_tier` as `drop+note`; and each
populated governance field as `drop+note`.

## 4. Loading behavior

Per `windsurf.md`'s Skills section (lines 17-26), the host uses
**progressive disclosure**: it loads only a skill's `name` and `description`
into its always-on index up front (cheap, low context cost), and defers
loading the full `SKILL.md` body and any sibling resource files until it
either decides to invoke the skill or the user explicitly `@mentions` it by
name. This is why the adapter is careful to keep `name`/`description`
faithful and self-sufficient in frontmatter — they are the *only* content
the host reasons over before deciding whether to pull in the rest.

Discovery is hierarchical across three scopes, each documented for the
legacy `.windsurf/skills/` location and inferred to carry over to
`.agents/skills/` given the "Common denominator" path in
`adapter-projection.md`:

- **Workspace** — `.windsurf/skills/<name>/` (committed to the repo, team-shared)
- **Global** — `~/.codeium/windsurf/skills/<name>/` (per-user, all workspaces, not committed)
- **System** — OS-specific enterprise-managed, read-only paths (e.g.
  `/etc/windsurf/skills/` on Linux/WSL)

Both live agents recognize Skills as a category (Cascade natively; Devin
Local lists Skills under "Supported" per `windsurf.md` line 28), so this
adapter's output is not tied to one side of the rebrand for *loading* —
only the finer-grained fields in §2 are where the two runtimes' documented
surfaces diverge or go unconfirmed.

## 5. Compatibility assumptions

The single largest compatibility risk this adapter carries is architectural,
not field-level: **Devin Local (the default agent for new tabs going
forward) explicitly dropped Workflows and Memories** — both listed under
"Unsupported" in the Devin Local capability list (`windsurf.md` lines
105, 141, 188), where they were previously legacy-Cascade features. A
canonical skill that assumed either of those mechanisms — e.g. one whose
body instructed the host to "save this as a Workflow" or "store this as a
Memory for next session" — would not project correctly through this
adapter: there is no frontmatter field for Workflows/Memories to be
downgraded to, and no body-note fallback would restore the missing runtime
behavior, since the *behavior itself* is gone on the newer agent.

This library's skills do not currently exercise this risk: no skill in this
library relies on Workflows or Memories, by design (skills are authored
against the vendor-neutral canonical schema in `core/skill-specification/`,
which has no such primitives). This section documents the risk as a
**standing constraint on any future skill authored against this adapter**,
not a defect in the adapter or in any skill that exists today. If a future
skill is authored with a dependency on session-persistent memory or a
manually-triggered multi-step command template, this adapter would need to
be revisited before it could safely project that skill.

## 6. Version considerations

This target carries the **strongest version-considerations caveat of the six
adapters in this library**, for a concrete, dated reason rather than general
caution:

- At research time (2026-09-09), `docs.windsurf.com` had already begun
  wholesale 307-redirecting to `docs.devin.ai` — the "Windsurf" brand's own
  documentation no longer hosts independent content (`windsurf.md` lines 5,
  9-11).
- Two non-interoperable agent runtimes (Cascade and Devin Local) are live
  simultaneously in the same product, with different permission models,
  different supported-feature lists, and an unresolved precedence order
  between overlapping on-disk conventions (`.windsurf/` vs `.devin/` paths) —
  the research doc explicitly flags this as "not a stable, finalized
  configuration hierarchy" (`windsurf.md` line 168).
- `core/skill-specification/adapter-projection.md`'s own snapshot caveat
  singles out this target by name — "vendor formats move fast
  (Windsurf→Devin rebrand mid-migration...)" — ahead of the general
  re-verify-everything instruction that applies to all targets.

Given that, treat every path, frontmatter assumption, and dropped/native
classification in this adapter as **provisional pending a fresh check
against current Windsurf/Devin Desktop docs**, more urgently than for the
other five targets in this library (Claude Code, Cursor, Codex, Antigravity,
VS Code) — none of which were flagged as being mid-rebrand at research
time. Concretely, before trusting this adapter in a live integration:
confirm which of Cascade or Devin Local (or both) the target deployment
actually runs, confirm whether `.agents/skills/` is genuinely read by
whichever agent is active (this adapter assumes so per the matrix's "Common
denominator," but that assumption predates the rebrand settling), and
re-check whether a documented manual-invocation control or per-skill
capability grant has since appeared — either would let a future revision of
this adapter promote fields this README currently lists under §2 back to
native.
