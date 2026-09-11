# Antigravity adapter

Projects a canonical skill (`skill.yaml` + `SKILL.md`) onto
[Google Antigravity](https://antigravity.google)'s native `SKILL.md` format.

**This is the one adapter in the library that performs an actual content
transformation, not just a field-name mapping.** Every other adapter renames
or relocates fields; this one rewrites the `description` text itself (wraps
it into third person) before emitting it. That rewrite is mechanical and
its scope is deliberately narrow — see "Limitations" below before relying
on the output verbatim.

Implementation: [`adapter.py`](./adapter.py). Shared engine:
[`adapters/lib/skill_loader.py`](../lib/skill_loader.py),
[`adapters/lib/loss_manifest.py`](../lib/loss_manifest.py),
[`adapters/lib/common.py`](../lib/common.py).

## 1. Supported capabilities

Antigravity's `SKILL.md` frontmatter has exactly two keys
(`research/agent-ecosystems/antigravity.md` §1), and the adapter maps both
natively:

| Canonical field | Antigravity frontmatter | Native? |
|---|---|---|
| `name` | `name` | Yes — optional for Antigravity (defaults to the folder name), but the adapter always writes it for clarity |
| `description` | `description` | Yes, but only after the adapter's third-person transformation (see §3) |
| body (Markdown) | `SKILL.md` body | Yes, passed through unchanged |

Everything else the canonical schema carries is either folded into the body
as a note, or dropped from frontmatter with a loss-manifest entry — see §2.

## 2. Limitations

### The third-person wrap is mechanical, not a verified rewrite

This project's canonical descriptions are written in the imperative/infinitive
mood ("Instrument systems for...", "Decide the architecture..."). Antigravity
requires (per its docs) that `description` be written in the third person.
Rather than attempt a grammatical rewrite, `to_third_person()` in
`adapter.py` wraps the original text under a fixed frame:

```python
def to_third_person(description: str) -> str:
    return f"This skill: {description}"
```

The function's docstring explains why, and is worth quoting in full because
it is the adapter's central honesty claim:

> Rewriting arbitrary imperative English into correct third-person prose in
> general requires real grammatical analysis (subject-verb agreement varies
> per verb) that this adapter does not attempt — a wrong guess (e.g. naively
> appending "s" to the first word) would silently produce ungrammatical or
> wrong-meaning text, which is worse than an honest, safe wrapper.
>
> Instead: wrap the existing description under a fixed third-person frame
> ("This skill: <description>"), which is grammatically valid for ANY input
> mood and preserves the original meaning exactly. This is flagged in the
> loss manifest as a mechanical wrap, not a verified natural-language
> rewrite — an author publishing to Antigravity should hand-polish the
> wrapped description before shipping.

In other words: the adapter chose a transformation that is *always
grammatically valid and always meaning-preserving*, at the cost of producing
prose ("This skill: Instrument systems for...") that reads more mechanically
than a hand-written third-person description would. It never inflects verbs,
never reorders clauses, and never tries to detect or repair a description
that is already third-person. The loss manifest records this on every
projection (`manifest.body("description", ...)`, action `body`, not
`native`) so the mechanical-wrap fact travels with the output rather than
being silently assumed.

### `required_capabilities` and `execution_tier` are both handled conservatively, but not identically

Both are flagged in `adapter.py` because Antigravity's exact native schema
for tool/capability requirements and for subagent-delegation configuration
(`invoke_subagent`) needs re-verification before an adapter should try to
author them directly (`research/agent-ecosystems/antigravity.md` §1, §7).
Concretely, in the current code:

- `required_capabilities` is pushed into the **body** via `capability_note()`
  — a generic, target-agnostic "Capability requirements" section listing
  what the skill needs and its fallbacks. The loss manifest records this as
  `body` with the note: *"Antigravity documents tool-requirement declaration
  but the exact schema needs re-verification... capability note kept in body
  as the safe fallback."*
- `execution_tier` (which is where a subagent-delegation intent like
  `execution_tier: C` would live) is **not** given a body note at all — the
  adapter records it as `drop+note` in the loss manifest: *"Subagent
  delegation (`invoke_subagent`) is documented but this adapter does not
  attempt to author that configuration automatically without a confirmed
  schema."* The asymmetry is deliberate: writing a plain-English capability
  note in the body carries no risk of inventing a wrong config shape, but
  writing anything resembling an `invoke_subagent` block would risk exactly
  the speculative-frontmatter problem the Lossiness contract's L-4 forbids
  (`core/skill-specification/adapter-projection.md`). Both are therefore
  "handled conservatively" in the sense that neither is silently lost
  without a manifest entry, but only one of them reaches the projected
  body text.

### Everything else

- `activation_mode: manual` skills get a body note flagging that Antigravity's
  invocation-policy mechanism for suppressing auto-invocation has not been
  confirmed at research time (`manifest.body("activation_mode", ...)`).
- `activation_conditions` / `non_activation_conditions` have no Antigravity
  frontmatter slot (no glob/semantic-condition field documented) and are
  always pushed into the body via `activation_conditions_note()`.
- Library-governance fields (`source_references`, `evaluation_criteria`,
  `depends_on_skills`, etc.) are dropped from frontmatter with a
  loss-manifest pointer back to the canonical `skill.yaml`, per L-3 — this
  mirrors every other adapter in the library and is not Antigravity-specific.

## 3. Packaging format

The adapter emits a single file at:

```
.agents/skills/<slug>/SKILL.md          # workspace-scoped
~/.gemini/config/skills/<slug>/SKILL.md # global/user-scoped (equivalent layout)
```

(`PATH_TEMPLATE` in `adapter.py`; both locations are documented in
`research/agent-ecosystems/antigravity.md` §1 and §11.) The adapter always
targets the workspace path; picking the global path instead is a deployment
decision outside the adapter's scope.

### Worked example

Canonical description, verbatim from `skills/observability/skill.yaml`:

> Instrument systems for logging, metrics, tracing, and error monitoring —
> choose the right signal(s) for the diagnostic need, avoid high-cardinality
> and PII-leakage pitfalls, and design actionable alerting. Use when making
> a system diagnosable in production or debugging a production issue.
> Explicitly does not cover resilience/fault-tolerance patterns (retries,
> circuit breakers), a separate, still-unresearched gap in this library.

Antigravity-projected `description` (output of `to_third_person()`,
unchanged apart from the prefix):

> This skill: Instrument systems for logging, metrics, tracing, and error
> monitoring — choose the right signal(s) for the diagnostic need, avoid
> high-cardinality and PII-leakage pitfalls, and design actionable alerting.
> Use when making a system diagnosable in production or debugging a
> production issue. Explicitly does not cover resilience/fault-tolerance
> patterns (retries, circuit breakers), a separate, still-unresearched gap
> in this library.

Side by side, the transformation is exactly: prepend `"This skill: "`.
Nothing else changes — no verb is re-conjugated, no clause is reordered, the
second and third sentences (already imperative/declarative, not first- or
second-person) are carried through untouched. This is precisely the
trade-off the docstring describes: grammatically safe for any input, but not
polished third-person prose. A human should read `"This skill: Instrument
systems for..."` before publishing and decide whether to hand-edit it into
something like *"Instruments systems for..."* or a fuller rewrite.

The emitted `SKILL.md` for this example would begin:

```markdown
---
name: Observability
description: This skill: Instrument systems for logging, metrics, tracing, and error monitoring — choose the right signal(s) for the diagnostic need, avoid high-cardinality and PII-leakage pitfalls, and design actionable alerting. Use when making a system diagnosable in production or debugging a production issue. Explicitly does not cover resilience/fault-tolerance patterns (retries, circuit breakers), a separate, still-unresearched gap in this library.
---
<SKILL.md body, unchanged, plus appended notes for activation/capability/governance fields>
```

## 4. Loading behavior

Per `research/agent-ecosystems/antigravity.md` §1 and §3, Antigravity
discovers and loads skills in three stages:

1. **Discovery** — at the start of every conversation, the agent is shown
   only the `name` + `description` metadata for every skill found under
   `.agents/skills/` (workspace) and `~/.gemini/config/skills/` (global).
   This is why the `description` text matters so much: it is the *only*
   signal the agent uses to decide relevance before reading anything else.
2. **Activation** — if the metadata looks relevant to the current task (or
   the user explicitly `@mentions` the skill), the agent reads the full
   `SKILL.md` body into context.
3. **Execution** — the agent follows the body's instructions while
   completing the task.

This is the same "progressive disclosure" pattern the project's core spec
already assumes (metadata cheap and always-loaded, body loaded on demand),
so the adapter does not need to do anything special to support it — it just
needs the `description` field to actually satisfy Antigravity's stated
format for that metadata pass, which is the whole reason the third-person
transformation exists.

Optional skill subdirectories (`scripts/`, `examples/`, `resources/`) are
documented but this adapter does not currently populate them; canonical
skills' `references/` resource files are not yet projected into Antigravity's
directory layout.

## 5. Compatibility assumptions

The adapter treats Antigravity's third-person requirement as unconditional:
every projected `description` gets wrapped, regardless of the skill's
canonical wording. This matches how `adapter-projection.md`'s field-mapping
matrix documents the target ("`description` (3rd-person)").

The research doc's own wording is slightly softer than "required," though,
and worth flagging: it describes `description` as "required, **should** be
written in third person with keywords that help the agent recognize
relevance" (`research/agent-ecosystems/antigravity.md` §1) — a style
recommendation for relevance-matching quality, not a stated hard validation
rule that Antigravity enforces or rejects non-conforming descriptions for.
The research doc gives no further nuance (e.g., no documented exception for
short descriptions, no confirmation of what happens if a description is left
in first/second person). The adapter's choice to apply the wrap
unconditionally is therefore a conservative reading of a "should," not a
confirmed hard requirement — consistent with optimizing for relevance-match
quality even where enforcement is unverified.

## 6. Version considerations

This mapping inherits the project-wide snapshot caveat from
`core/skill-specification/adapter-projection.md`: **"vendor formats move
fast... every mapping below MUST be re-verified against current vendor docs
before an adapter is trusted"** (dated 2026-09-09). The Antigravity research
doc itself captured specific product versions at research time (desktop app
2.0/docs-nav 2.12.2, CLI 1.1.25, SDK 0.1.16, IDE extension 2.5.5) and flags
several points as unconfirmed by direct page fetch (e.g. the exact
`SKILL.md` optional-subdirectory schema, the precise tool-requirement
declaration schema). None of this is guaranteed stable, and Antigravity's
own docs describe Skills as having *already* replaced an older mechanism
(Workflows) in a May 2026 migration — this ecosystem's extension points are
demonstrably still moving.

Concretely for this adapter:

- Re-verify the `name`/`description`-only frontmatter contract before
  trusting it against a newer Antigravity release.
- Re-verify the `required_capabilities` and `execution_tier`/`invoke_subagent`
  schemas (§2 above) before attempting to move either out of "conservative
  body note" / "dropped" status into real frontmatter.
- **Hand-review every Antigravity-projected `description` before publishing
  a skill.** The mechanical `"This skill: ..."` wrap is designed to
  prioritize safety and meaning-preservation over prose quality — it will
  never produce a grammatically broken or meaning-altered description, but
  it will also never produce prose as polished as a human (or a verified
  grammatical rewrite) would. Treat the wrapped output as a correct-but-rough
  draft, not a finished artifact.
