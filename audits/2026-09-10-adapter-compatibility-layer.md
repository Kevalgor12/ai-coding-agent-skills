# Audit: Agent Compatibility & Adapter Layer (Step 31)

Date: 2026-09-10. Scope: the agent compatibility/adaptation layer under
[`adapters/`](../adapters/), implementing the projection model already
designed in `core/skill-specification/adapter-projection.md` (Phase A of
this project). This is **Step 31** of the master build plan, model/effort
Sonnet 5 / High. Target adapters, per the plan: Claude Code, Cursor,
Codex, Windsurf, Antigravity, Generic/MCP.

## What was built

Unlike Steps 27/30 (design + prose content) and Steps 28/29 (review of
existing content), this step produces **working code**: a shared
projection engine plus one adapter module per target, actually executed
against all 86 real skills in this library, not just described in prose.

| Component | Content |
|---|---|
| `adapters/lib/skill_loader.py` | The single place that parses `skill.yaml`+`SKILL.md`; every adapter imports it rather than re-parsing |
| `adapters/lib/loss_manifest.py` | Shared loss-manifest report format (native / body / drop+note / n/a) |
| `adapters/lib/common.py` | Shared helpers (activation-condition notes, capability notes, governance-field sweep, identity-field sweep) used by all 6 adapters |
| `adapters/<target>/adapter.py` × 6 | One projection module per target, each implementing `project(skill) -> (files, loss_manifest)` |
| `adapters/<target>/README.md` × 6 | The 6 required documentation aspects per target (capabilities, limitations, packaging, loading, compatibility assumptions, version considerations) |
| `adapters/tests/test_compatibility.py` | Runs all 6 adapters against a diverse skill sample; checks for crashes, L-1/L-2 lossiness-contract compliance, and target-specific structural rules |

Grounded entirely in pre-existing design work: the field-mapping matrix,
per-target specifics, and lossiness contract (L-1 through L-5) all come
from `core/skill-specification/adapter-projection.md`, itself grounded in
`research/agent-ecosystems/`'s 7 per-vendor research docs. No new vendor
research was needed or performed — this step's job was implementation,
not discovery.

## Verification performed (and what it found)

This step is unusual among this project's build steps in that its own
test suite caught real, self-authored bugs before commit — the kind of
finding earlier steps' audits caught in *already-shipped* content. Here,
the bugs never shipped, because the test existed before the commit did.

1. **Initial run (6-skill sample, basic checks):** all 36 combinations
   passed, but only checked for crashes and L-2 (no silent drop of
   runtime-meaningful fields).
2. **First real bug, found by the Claude Code README-writing agent
   reading the code closely rather than trusting the task brief**:
   `inputs`/`outputs` were never referenced anywhere in any of the 6
   adapters — not projected, not even recorded in the loss manifest. Fixed
   by adding a real `inputs` → `arguments` mapping for Claude Code (per
   the design matrix) and a body-note fallback for the other 5 targets,
   plus extending the shared engine with `IDENTITY_ONLY_FIELDS`
   (`id`/`slug`/`kind`/`layer`/`domain` — internal taxonomy metadata,
   never meant for projection) and `BODY_DERIVED_FIELDS`
   (`purpose`/`scope`/`expertise` — already carried verbatim inside the
   body's own required sections), both of which had the same "silently
   unaccounted" problem once looked for.
3. **Strengthened the test suite itself** with an L-1 completeness check:
   every canonical field a sampled skill actually populates must appear
   *somewhere* in that projection's loss manifest — the literal
   "every canonical field" requirement L-1 states, made mechanically
   enforced rather than aspirational.
4. **That stronger check immediately found four more real gaps**, at
   library-wide scale (86 skills × 6 targets = 516 combinations checked):
   - `non_activation_conditions` was rendered into the body correctly but
     never separately recorded in the manifest (only `activation_conditions`
     was) — affecting every skill with a non-empty `non_activation_conditions`
     field, i.e. nearly all 86.
   - The MCP adapter never handled `activation_mode` at all — a plain
     omission, not a deliberate design choice.
   - `parents`, `required_context`, `optional_context`, and `adapter_hints`
     were canonical fields this step's initial engine design had missed
     entirely from its governance-field list.
   - `capability_fallbacks` (present on Tier C skills like `playwright`)
     was rendered into the body via the same note as `required_capabilities`
     but never given its own manifest entry.
5. **All fixed**, with one non-trivial design correction along the way:
   `adapter_hints` is *not* purely governance-only, because Claude Code's
   own adapter actually consumes it (it changes emitted `allowed-tools`/
   `context: fork`). A blanket "governance field → always drop+note" rule
   would have made Claude Code's manifest self-contradictory (claiming a
   field was dropped while visibly using it). Fixed by adding a guard
   (`record_governance_fields`) that only sweeps a field into `drop+note`
   if no earlier, more-specific manifest entry already claimed it — letting
   every adapter share one governance-sweep call safely, including the one
   adapter where a "governance" field isn't actually inert.
6. **Final state, independently re-verified**: all 86 skills × all 6
   targets (516 combinations) produce a projection with zero crashes,
   zero L-1 gaps (every populated canonical field accounted for), and
   zero L-2 violations (no runtime-meaningful field silently dropped).

## Documentation review

Each of the 6 per-target READMEs was written by a separate agent reading
that target's actual, already-tested `adapter.py` plus its
`research/agent-ecosystems/<target>.md` source — not from a shared
template filled in blind. Two agents (Claude Code, Antigravity) caught
and correctly resolved discrepancies between my own delegation brief's
simplifications and what the code actually does, documenting the real
behavior rather than the brief's gloss — flagged here as a positive
pattern, not corrected as an error. Two stale cross-references in the
Cursor README (written before the `capability_fallbacks`/`required_capabilities`
manifest-labeling fix landed) were caught and corrected directly.

Per-target fidelity, as documented and independently confirmed against
the actual test output:

| Target | Native fields | Notable limitation |
|---|---|---|
| Claude Code | name, description, activation_mode, required_capabilities (mapped), inputs (partial), adapter_hints (when used) | Richest surface; still no `paths`/`hooks`/`model` support |
| Cursor | name, description, activation_mode | No per-skill tool-grant mechanism at all — capabilities always body-only |
| Codex | name, description; activation_mode/capabilities via optional sidecar | Tier C subagent policy deliberately unimplemented (unconfirmed schema) |
| Windsurf/Devin | name, description | Most conservative of the six — mid-vendor-rebrand at research time |
| Antigravity | name; description (mechanically third-person-wrapped) | The one adapter that transforms content, not just field names — flagged for mandatory human review before publishing |
| MCP | name, description (as resource metadata) | Structurally different (resource URI, not file path); lowest confidence — target spec had no reference implementation at research time |

## Overall assessment

This step's central discipline — never trust an adapter's own code
without an independent, executable check — caught real defects that a
prose-only review would very plausibly have missed, since the bugs were
all sins of *omission* (a field silently never mentioned) rather than
factual errors in what was written. The L-1 completeness check added
partway through this step is now a standing, reusable mechanism: any
future canonical field added to `skill.yaml` that isn't wired into
`lib/skill_loader.py`'s field lists or an adapter's own logic will be
caught the next time `test_compatibility.py` runs, rather than silently
degrading every projection's completeness. No vendor-specific behavior
was introduced into any canonical skill file — every one of the 86
skills in `skills/` is byte-for-byte unchanged by this step; the
adaptation logic lives entirely in `adapters/`, as the master plan
requires.
