# Skill Specification (normative)

Spec version **1.0**. Keywords **MUST / SHOULD / MAY** are used in the RFC-2119
sense. Every skill in [`skills/`](../../skills/) MUST conform. Conformance is
checked at three levels, noted per rule:

- **[V]** mechanical validator (schema/lint — pass/fail, automatable).
- **[E]** evaluation ([`evaluations/`](../../evaluations/) — proven by tests).
- **[A]** human/audit review ([`audits/`](../../audits/) — judgement).

---

## 1. Canonical directory & files

A skill is a directory named by its `slug`, containing:

| Path | Required | Purpose |
|---|---|---|
| `skill.yaml` | MUST | Full metadata (§2). Authoring source of truth; adapter input. |
| `SKILL.md` | MUST | Minimal frontmatter + Tier-1 body (§3). |
| `references/` | MAY | Tier-2 deep knowledge (loaded on demand). |
| `examples/` | MAY | Tier-2 worked examples (loaded on demand). |
| `scripts/`, `assets/` | MAY | Executable helpers / templates the skill references. |

---

## 2. `skill.yaml` — metadata schema

Fields are grouped by concern. **R** = required, **O** = optional,
**C** = conditionally required (condition stated).

### 2.1 Identity

| Field | R/O | Type | Rule |
|---|---|---|---|
| `id` | R | string | Taxonomy ID `SK-…` (matches [taxonomy](../taxonomy/)). Immutable once assigned. **[V]** |
| `slug` | R | string | kebab-case, matches directory name, unique in the library. **[V]** |
| `name` | R | string | Human-readable; ≤ 64 chars (VS Code ceiling). MUST equal `SKILL.md` frontmatter `name`. **[V]** |
| `spec_version` | R | string | The spec version this skill targets (e.g. `"1.0"`). **[V]** |
| `skill_version` | R | string | Semver of the skill itself; bump on any content change. **[V]** |
| `kind` | R | enum | `generic` \| `technology` \| `orchestration`. **[V]** |
| `layer` | R | enum | Taxonomy layer `0`–`4`. **[V]** |
| `domain` | R | string | Domain code from the taxonomy (`CONV`, `DATA`, `TECH`, …). **[V]** |
| `parents` | C | list<id> | Required for `kind: technology` (the Layer-3 skill(s) it specializes). **[V]** |

### 2.2 Purpose, scope, expertise

| Field | R/O | Type | Rule |
|---|---|---|---|
| `purpose` | R | string | One sentence: why the skill exists. **[V]** length; **[A]** meaning. |
| `scope` | R | string | What it covers. **[V]** |
| `expertise` | O | string | The role/persona lens (e.g. "database performance engineer"). |
| `description` | R | string | The Tier-0 trigger string (§4.1). ≤ 500 chars. MUST equal `SKILL.md` frontmatter `description`. **[V]** |

### 2.3 Activation

| Field | R/O | Type | Rule |
|---|---|---|---|
| `activation_conditions` | R | list<string> | Concrete signals that SHOULD trigger the skill (task intents, detected files/manifests, keywords). ≥ 1. **[V]**/**[E]** |
| `non_activation_conditions` | R | list<string> | Concrete signals that MUST prevent triggering (the boundary guard). ≥ 1. **[V]**/**[E]** |
| `activation_mode` | R | enum | `auto` (model-triggered) \| `manual` (invoke only) \| `always` (standing). Maps to per-vendor invocation flags (§adapter). **[V]** |

### 2.4 Interface (inputs / context / outputs)

| Field | R/O | Type | Rule |
|---|---|---|---|
| `inputs` | R | list<item> | What the skill expects (task context, files, prior-skill output). Each: `name`, `description`, `required: bool`. **[V]** |
| `required_context` | O | list<string> | Context that MUST be present to run (e.g. "a package manifest", "a failing test"). If absent → failure handling (§2.8). |
| `optional_context` | O | list<string> | Context that improves output if present but isn't required. |
| `outputs` | R | list<item> | What it produces. Each: `name`, `kind` (`edit`\|`artifact`\|`analysis`\|`data`\|`command-run`), `description`. **[V]** |

### 2.5 Composition (dependencies / conflicts)

| Field | R/O | Type | Rule |
|---|---|---|---|
| `depends_on_skills` | O | list<id> | Skills this one composes as a hard, blocking sub-step of its own execution. MUST be same-or-lower taxonomy layer (acyclic). **[V]** |
| `related_skills` | O | list<id> | Commonly composed-with, not a hard dependency. **[V]** exist. |
| `conflicts_with` | O | list<id> | Skills that must not co-activate for the same decision. **[V]** |
| `parents` | C | list<id> | (Defined in §2.1 Identity, repeated here for contrast.) The generic skill(s) a `kind: technology` skill specializes. This is a **different relationship** from `depends_on_skills` and the two MUST NOT be conflated: `parents` says "I am a more specific version of that skill's method"; `depends_on_skills` says "I invoke that *other* skill as a sub-step while I run." A technology skill specializing a generic parent does **not** also need that parent in `depends_on_skills` — listing it there is redundant and asserts a stronger claim (hard blocking invocation) than specialization actually is. If a relationship is "I need that skill's *output* to already exist, but I degrade gracefully if it doesn't," it belongs in `required_context` + `failure_handling` + `related_skills`, not `depends_on_skills` either — reserve `depends_on_skills` for true hard composition (e.g. a review skill that always delegates a security check to `security-engineering` as part of its own execution). **[A]** (this distinction was violated identically by 7 of 9 technology skills authored in one batch before this rule was written explicitly — see `audits/2026-09-09-data-domain-validation.md` — so treat repeat occurrences as a sign this section needs to be read, not independently re-derived per skill.)
| `required_capabilities` | R | list<enum> | Abstract agent capabilities from the [capability map](../../research/knowledge-maps/agent-capability-map.md): `file-read`, `file-write`, `shell`, `browser`, `container`, `mcp-client`, `mcp-db`, `git`, `subagent`, `network`. **[V]** |
| `execution_tier` | R | enum | `A` (advisory/file only) \| `B` (needs shell) \| `C` (needs a non-universal capability). MUST be consistent with `required_capabilities`. **[V]** |
| `capability_fallbacks` | C | map | Required when `execution_tier: C`. For each non-universal capability, the documented fallback (e.g. `browser: "advise-only; or Playwright-via-MCP on Claude Code"`). **[V]**/**[A]** |

### 2.6 Grounding & version-awareness

| Field | R/O | Type | Rule |
|---|---|---|---|
| `grounding` | R | enum | `official-docs` (claims trace to vendor/official documentation via `research/`) \| `engineering-convention` (grounded in the taxonomy/house conventions, no external API surface) \| `mixed`. **[V]** |
| `source_references` | C | list<ref> | Required when `grounding` includes `official-docs`. Each: `url`, `title`, `via` (the `research/…` file that cites it), `retrieved` (ISO date). **[V]** |
| `covered_versions` | C | map | Required for `kind: technology`. Per component: the version/range this skill's content is correct for (e.g. `postgresql: ">=16 <=17"`). **[V]** |
| `version_sensitive_claims` | O | list<claim> | Claims that hold only for a version/range. Each: `claim`, `applies_to` (version range), `source_ref`. Mirrors [VERSION_REGISTRY](../../research/technologies/VERSION_REGISTRY.md). **[V]**/**[A]** |
| `last_verified` | R | ISO date | When the skill's factual content was last checked against sources. **[V]** |
| `reverify_triggers` | C | list<string> | Required for `kind: technology`: events that invalidate the skill (e.g. "a new PostgreSQL major release", "Drizzle v1 GA"). **[A]** |

### 2.7 Quality controls (the "must prevent" hooks, machine-declarable parts)

| Field | R/O | Type | Rule |
|---|---|---|---|
| `owned_knowledge` | O | list<string> | Topics this skill is the single owner of (others must reference, not copy). Enables the no-duplication check. **[V]** cross-skill. |
| `decision_framework_present` | C | bool | MUST be `true` when the skill's domain has real alternatives (all Layer-3 generic skills, most technology-choice skills) — the anti-tech-bias / anti-overengineering guard. **[V]** presence; **[A]** quality. |

### 2.8 Failure, escalation, evaluation

| Field | R/O | Type | Rule |
|---|---|---|---|
| `failure_handling` | R | list<rule> | What to do when required context/capability is missing or a step fails (e.g. "no shell → degrade to advisory and say so"). ≥ 1. **[V]**/**[E]** |
| `escalation` | O | list<rule> | When to stop and defer to a human or another skill (e.g. "destructive migration → require confirmation"). |
| `verification` | R | list<check> | How the skill's own output is checked (tests to run, invariants to confirm). ≥ 1. **[V]**/**[E]** |
| `evaluation_criteria` | R | list<criterion> | What an `evaluations/` test MUST prove before the skill reaches `final/`. ≥ 1, each testable. **[V]** presence; **[E]** the eval itself. |

### 2.9 Adapter hints

| Field | R/O | Type | Rule |
|---|---|---|---|
| `adapter_hints` | O | map | Per-target overrides the projection uses (e.g. `claude-code.allowed_tools`, `cursor.paths`, `vscode.argument_hint`, `codex.allow_implicit_invocation`). Unknown-target keys are ignored. See [adapter-projection.md](adapter-projection.md). |

---

## 3. `SKILL.md` — body structure

`SKILL.md` = minimal frontmatter + Tier-1 body.

### 3.1 Frontmatter (the only universally-read metadata)

```yaml
---
name: <equals skill.yaml name>
description: <equals skill.yaml description>
spec_version: "1.0"
---
```

MUST contain exactly these three keys and no more (richer per-vendor keys are
emitted by the adapter, never hand-authored here). **[V]**

### 3.2 Body sections (fixed order; Tier-1)

Sections marked R MUST be present with real content; O MAY be omitted; a section
with nothing to say MUST be omitted, not filled with filler (context-efficiency).

1. **Purpose & scope** — R. 1–3 sentences. Mirrors `skill.yaml`.
2. **When to use / When not to use** — R. Human-readable form of activation/non-activation.
3. **Knowledge** — C (R for technology skills). Essential facts only; deep material → `references/` with a link. Every technology API/config claim MUST carry an inline source marker resolvable to `skill.yaml.source_references`.
4. **Decision framework** — C (R when `decision_framework_present: true`). How to choose among options, including the simplest/do-nothing branch. MUST NOT state a single default where real alternatives exist (anti-tech-bias).
5. **Workflow** — C (R when the skill performs a procedure). Ordered steps.
6. **Engineering rules** — R. The concrete do/don't rules. ≥ 1.
7. **Trade-offs** — O. Costs/benefits of the recommended approach vs. alternatives.
8. **Anti-patterns** — R. What to avoid, including at least one over-engineering pitfall for the domain.
9. **Security** — C (R when the skill touches a trust boundary/secret/untrusted input). Essential rules only; cross-cutting depth → reference `SK-QA-002`, don't restate it.
10. **Performance** — O. Essential rules; depth → reference `SK-QA-003`.
11. **Testing** — C (R when the skill produces runnable code). Essential rules; depth → reference `SK-QA-001` and tool skills.
12. **Failure handling** — R. Mirrors `skill.yaml.failure_handling`.
13. **Escalation** — O. When to stop and defer.
14. **Outputs & verification** — R. What it produces and how to check it.
15. **References** — C (R when `references/`/`source_references` exist). Links to Tier-2 files and the source list.

---

## 4. Rulesets

### 4.1 Context-efficiency rules

- **CE-1 [V]** `description` ≤ 500 chars and MUST encode *what the skill does* + *when it triggers* (so the model can select it without loading the body). It MUST NOT be marketing prose.
- **CE-2 [V]/[A]** `SKILL.md` body SHOULD be ≤ ~500 lines. Content exceeding this MUST move to `references/`.
- **CE-3 [V]** The body MUST NOT inline material that belongs in Tier 2 (large tables, exhaustive examples, full changelogs). Link to `references/` instead.
- **CE-4 [A]** Every body section MUST earn its place; omit empty/filler sections rather than pad (§3.2).
- **CE-5 [E]** Activation/non-activation MUST be precise enough that the skill does not load for out-of-scope tasks (measured by false-activation rate in evals).
- **CE-6 [V]** Tier-2 resources MUST NOT be auto-loaded; the body references them so they load only when needed.

### 4.2 Validation rules (mechanical)

- **VR-1** All required fields (§2, §3) present and well-typed. 
- **VR-2** `skill.yaml.name`/`description` equal `SKILL.md` frontmatter; `slug` equals directory name.
- **VR-3** `id` matches the taxonomy; `depends_on_skills`/`related_skills`/`conflicts_with`/`parents` reference existing skill IDs.
- **VR-4** Dependency graph is acyclic and respects layer ordering (a skill depends only on same-or-lower layers).
- **VR-5** `execution_tier` is consistent with `required_capabilities` (Tier A ⇒ only `file-read`/`file-write`; Tier C ⇒ at least one non-universal capability and a `capability_fallbacks` entry for it).
- **VR-6** `activation_conditions` and `non_activation_conditions` are non-empty and disjoint (no signal appears in both).
- **VR-7** No two skills share an identical activation trigger (uniqueness across the library).
- **VR-8** Body section order and required-section presence match §3.2 for the skill's `kind`.

### 4.3 Source-grounding rules (anti-hallucination)

- **SG-1 [V]** If `grounding` includes `official-docs`, `source_references` MUST be non-empty and every entry MUST resolve through a `research/…` file to an official documentation URL.
- **SG-2 [V]/[A]** Every claim in the body about a technology's **API, configuration, CLI, or documented behavior** MUST carry an inline source marker resolvable to a `source_references` entry. A technology-API claim with no traceable source FAILS.
- **SG-3 [A]** A skill MUST NOT state an API/flag/option that does not appear in a cited source (the concrete hallucination guard). When unsure, the skill MUST say "verify against current docs" rather than assert.
- **SG-4 [V]** `grounding: engineering-convention` skills (e.g. `code-commenting`) are exempt from SG-1/SG-2 for practice guidance but MUST NOT then make technology-API claims; if they do, those claims fall under SG-2.
- **SG-5 [A]** Examples in `examples/` MUST be runnable/accurate against `covered_versions`, not illustrative pseudo-code presented as real.

### 4.4 Version-awareness rules (anti-outdated)

- **VA-1 [V]** `kind: technology` skills MUST declare `covered_versions` and `reverify_triggers`.
- **VA-2 [V]/[A]** Any claim true only for some versions MUST be tagged (inline in the body and in `version_sensitive_claims`) with the range it holds for. Untagged version-specific claims FAIL.
- **VA-3 [A]** A skill MUST NOT assume "latest" behavior implicitly; it states the version its guidance targets.
- **VA-4 [V]** `last_verified` present; **[A]** stale skills (past a re-verify trigger or a policy age) are flagged for re-verification before promotion to `final/`.
- **VA-5 [A]** Where the research recorded a version caveat (e.g. Prisma v8 doc contradiction, Drizzle v1 RC vs v0.x, MySQL calendar-versioning switch), the skill MUST carry that caveat, not paper over it.

### 4.5 Quality rules (anti-generic / anti-verbose / anti-duplication / anti-bias / anti-overengineering)

- **QR-1 [A]/[E]** No generic advice: guidance MUST be specific to the skill's scope and actionable; content that would apply to "any software" without the skill's context is disallowed.
- **QR-2 [V]/[A]** No duplicated knowledge: a topic listed in another skill's `owned_knowledge` MUST be referenced by ID, not restated. Cross-cutting concerns (security, performance, testing) are owned by `SK-QA-002/003/001` and referenced, never copied into technology skills.
- **QR-3 [A]** No technology bias: `kind: generic` skills MUST NOT hardcode a specific technology as the default; where alternatives exist they present a decision framework (QR ties to `decision_framework_present`).
- **QR-4 [A]** No overengineering: the decision framework MUST include the simplest viable option (including "do nothing"); anti-patterns MUST name at least one over-engineering trap for the domain.
- **QR-5 [A]** No unnecessary verbosity: prose is compressed; the body says each thing once; Tier-2 holds the long tail (ties to CE-2/CE-3).
- **QR-6 [E]** Output specificity: evals MUST demonstrate the skill produces concrete, correct, scope-appropriate output on seeded tasks — the empirical backstop for QR-1.

### 4.6 Required vs optional fields — quick reference

- **Always required:** `id`, `slug`, `name`, `spec_version`, `skill_version`, `kind`, `layer`, `domain`, `purpose`, `scope`, `description`, `activation_conditions`, `non_activation_conditions`, `activation_mode`, `inputs`, `outputs`, `required_capabilities`, `execution_tier`, `grounding`, `last_verified`, `failure_handling`, `verification`, `evaluation_criteria`; and `SKILL.md` with its 3-key frontmatter + the R body sections for the skill's kind.
- **Conditionally required:** `parents` (technology), `capability_fallbacks` (tier C), `source_references` (official-docs), `covered_versions`+`reverify_triggers` (technology), `decision_framework_present`=true (domains with alternatives).
- **Optional:** `expertise`, `required_context`, `optional_context`, `depends_on_skills`, `related_skills`, `conflicts_with`, `version_sensitive_claims`, `owned_knowledge`, `escalation`, `adapter_hints`, and the O body sections.

---

## 5. Conformance & lifecycle

1. Author `skill.yaml` + `SKILL.md` (+ Tier-2 as needed) in `skills/<slug>/`.
2. Run the mechanical validator (all **[V]** rules) — must pass.
3. Write the `evaluations/` test proving `evaluation_criteria` (all **[E]** rules).
4. Audit (all **[A]** rules) recorded in `audits/`.
5. Only after 2–4 pass may the skill be projected by adapters and promoted to
   `final/`. This wires the spec to the repo's existing `evaluations/`,
   `audits/`, and `final/` directories.
