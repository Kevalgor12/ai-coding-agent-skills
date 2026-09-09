# Canonical Skill Specification

Spec version: **1.0** (proposed). Status: **design only** — this defines the
format every library skill must follow; it does not author any skill.

This is the contract layer for the whole library. It defines a single,
vendor-neutral source-of-truth format for a skill, and the rules that make a
skill valid, high-quality, source-grounded, version-aware, and context-efficient
— so that one authored skill can be *projected* (by [`adapters/`](../../adapters/))
into the native format of Claude Code, Cursor, Codex, Windsurf, Antigravity, VS
Code agents, MCP-based agents, and custom agents.

Grounded in the completed research: the `SKILL.md` / agentskills.io convergence
across six vendors, three-level progressive disclosure, and the per-vendor
frontmatter divergence that forces a *lossy adapter* model
([comparison.md](../../research/agent-ecosystems/comparison.md),
[agent-capability-map.md](../../research/knowledge-maps/agent-capability-map.md)).
It builds directly on the [skill taxonomy](../taxonomy/) (skill IDs, layers,
execution tiers A/B/C).

## Files

- **README.md** (this file) — model, layout, loading tiers, how prevention is enforced.
- **[specification.md](specification.md)** — the normative spec: `skill.yaml`
  metadata schema, `SKILL.md` body structure, required/optional fields, and the
  five rulesets (validation, quality, source-grounding, version-awareness,
  context-efficiency).
- **[adapter-projection.md](adapter-projection.md)** — how the canonical format
  projects to each of the eight targets, the field-support matrix, and the
  documented-lossiness contract.
- **[examples/minimal/](examples/minimal/)** — the smallest skill that passes validation.
- **[examples/complex/](examples/complex/)** — a full-featured technology skill exercising every field.

> The two example skills are **illustrative renderings of the format**, not
> authored library skills. Their knowledge content is deliberately abbreviated;
> they exist to demonstrate the specification and serve as validator fixtures.

## The core idea: one source, many projections

A skill is authored **once** in a canonical directory (lives in
[`skills/`](../../skills/)). It is never authored per-vendor. Each target agent
gets a **projection** produced by that target's adapter:

```
   skills/<slug>/            (canonical source of truth — authored once)
        │
        ▼   per-target adapter reads skill.yaml + SKILL.md body,
            emits the target's native frontmatter subset + resource layout
        ├─▶ Claude Code   (.claude/skills/<slug>/SKILL.md, rich frontmatter)
        ├─▶ Cursor        (.cursor/ or .agents/skills/<slug>/…)
        ├─▶ Codex         (.agents/skills/<slug>/… + optional agents/openai.yaml)
        ├─▶ Windsurf      (.windsurf/ or .agents/skills/<slug>/…)
        ├─▶ Antigravity   (.agents/skills/ or ~/.gemini/config/skills/…)
        ├─▶ VS Code       (.github/skills/ or .agents/skills/<slug>/…)
        ├─▶ MCP           (skill:// resource per SEP-2640 — provisional)
        └─▶ custom        (consumes the canonical format directly)
```

Why a canonical source rather than authoring `SKILL.md` directly: the six
vendors share the *name+description+body* core but diverge on everything else
(Claude Code's `context:fork`/`allowed-tools`, Cursor's `paths`, VS Code's
`argument-hint`, Codex's `agents/openai.yaml`, MCP's `skill://` resources). A
single hand-authored `SKILL.md` cannot carry all of that without breaking on
targets that don't understand a given key. The canonical `skill.yaml` carries
the full superset; each adapter emits only what its target supports and records
what it dropped (see the lossiness contract).

## Canonical skill directory layout

```
<slug>/
  skill.yaml         REQUIRED  All metadata (identity, activation, capability tier,
                               dependencies, source refs, version info, eval criteria,
                               adapter hints). The authoring source of truth.
  SKILL.md           REQUIRED  Minimal frontmatter (name, description, spec_version)
                               + the structured instruction body (Tier-1 sections).
  references/        optional  Tier-2 deep knowledge, loaded on demand only.
  examples/          optional  Tier-2 worked examples, loaded on demand only.
  scripts/           optional  Executable helpers the skill may run (Tier B/C).
  assets/            optional  Templates/fixtures the skill references.
```

`name` + `description` also live in `SKILL.md` frontmatter (the one thing every
vendor reads); `skill.yaml` is the complete record and the adapter's input.
The two must agree — a validation rule enforces it.

## Three loading tiers (the context-efficiency backbone)

Every content dimension the brief lists is assigned to exactly one tier. This is
how the spec supports ~28 dimensions *and* prevents unnecessary context loading —
they are not all loaded at once. This mirrors the universal three-level
progressive disclosure the research found in every ecosystem.

| Tier | Loaded when | Carries | Budget |
|---|---|---|---|
| **0 — Metadata** | Always (trigger time) | `name`, `description` only (everything else in `skill.yaml` is adapter/tooling config, not model context) | `description` ≤ 500 chars |
| **1 — Body** | On activation | `SKILL.md` body sections: purpose/scope, when-to-use/not, essential knowledge, decision framework, workflow, engineering rules, trade-offs, anti-patterns, essential security/perf/testing, failure handling, escalation, outputs/verification | body ≤ ~500 lines (target); overflow → Tier 2 |
| **2 — Resources** | On demand, only if the body references them | `references/` (deep knowledge, large tables, full source citations), `examples/` (worked examples), `scripts/`, `assets/` | unbounded, but never auto-loaded |

**Dimension → tier map** (the brief's list, placed):

- **Tier 0:** identity, purpose (compressed into `description`), scope (compressed), activation conditions, non-activation conditions, version information, execution tier / required capabilities.
- **Tier 1:** expertise, knowledge (essential subset), decision framework, workflow, engineering rules, trade-offs, anti-patterns, security (essential), performance (essential), testing (essential), failure handling, escalation, inputs, required context, optional context, outputs, verification, dependencies, conflicts.
- **Tier 2:** knowledge (deep), examples, source references (full list), plus any large security/performance/testing reference material.

`skill.yaml` records the *authoritative, machine-readable* copy of every
metadata dimension (inputs, dependencies, source refs, eval criteria, etc.) for
tooling and adapters; the Tier-1 body carries the *human/agent-readable*
working form of the Tier-1 dimensions. They are two views of the same skill, and
validation checks they don't contradict.

## How the eight "must prevent" failures are structurally prevented

Each is tied to a specific rule in [specification.md](specification.md); summary:

| Must prevent | Prevented by |
|---|---|
| Generic advice | Source-grounding rules + mandatory `scope`/`non-activation` + decision-framework-not-opinion requirement; evals test output specificity. |
| Unnecessary verbosity | Tiering (heavy content → Tier 2) + Tier-0/1 length budgets + a quality rule. |
| Duplicated knowledge | Single-owner rule: cross-cutting knowledge lives in one skill; others reference by skill ID, never copy. |
| Hallucinated APIs | Every technology API/config/behavior claim MUST carry a source reference traceable to official docs via `research/`; unsourced API claims fail validation. |
| Outdated assumptions | Version-awareness rules: covered-version range, per-claim version tags, last-verified date, re-verify triggers. |
| Technology bias | Generic (Layer-3) skills MUST stay tech-neutral; where alternatives exist, present a decision framework, not a default favorite. |
| Overengineering | Quality rule requiring the minimal solution + mandatory "simplest option / do nothing" branch in the decision framework + a domain over-engineering entry in anti-patterns. |
| Unnecessary context loading | Tiering + activation/non-activation precision so skills don't over-trigger + ban on inlining Tier-2 material in the body. |

See [specification.md](specification.md) for the normative rule text and how each
rule is checked (mechanical validator vs. eval vs. human audit).
