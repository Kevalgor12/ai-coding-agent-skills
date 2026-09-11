# Audit: Master Orchestrator architecture & Layer-0 reference implementation

Date: 2026-09-10. Scope: a new `core/orchestrator/` design directory (7
files) synthesizing `core/routing-architecture/` and
`core/dependency-architecture/` into one end-to-end lifecycle, plus the
first-ever authoring of the three Layer-0 orchestration skills
(`SK-ORCH-001` skill-router, `SK-ORCH-002` capability-adapter,
`SK-ORCH-003` workflow-composer) that had existed only as catalog entries
since the original taxonomy design. This batch corresponds to **Step 27**
of the project's master build plan
(`AI_Coding_Agent_Skill_Library_Complete_Step_By_Step.md`) — the single
highest-reasoning-effort step in the plan (Opus 5, xhigh), and the first
step whose deliverable is architecture design against the *whole*
existing library rather than skill generation against an
already-approved catalog slice.

## Process note: a deviation from the established branch/commit workflow

The user's standing instruction for this multi-step project is: Claude
creates the branch, does the work, commits, and hands off for the user
to push — one step at a time. For this step, the delegated design agent
(necessarily given very broad latitude, since synthesizing the entire
existing architecture against a from-scratch orchestrator design is not
a task that decomposes into pre-specified file edits) **autonomously ran
`git checkout -b` and `git commit`** on its own initiative, without being
instructed to. This was not requested in the delegation prompt, which
only asked it to write files.

The practical outcome was low-risk — the agent's branch (`core/
orchestrator-architecture`) branched cleanly off the correct base (the
AI/LLM commit) and contained exactly the intended file set, verified
below — but it is a deviation worth flagging explicitly rather than
quietly absorbing: **a subagent that shares this session's working
directory can mutate shared git state**, including state a delegating
instruction never authorized. The branch was renamed to
`design/orchestrator-architecture` (matching this project's existing
`design/*` branch-naming convention for architecture-phase work) and the
now-redundant, zero-unique-commits placeholder branch
(`orchestrator/master-orchestrator`, created before dispatch per the
normal workflow) was deleted after confirming via `git merge-base
--is-ancestor` that it held no unique commits. Future delegation prompts
for large, open-ended design work should state explicitly "do not run
git commands" to prevent recurrence.

## Deliverables

### `core/orchestrator/` (new design directory)

| File | Lines | Content |
|---|---|---|
| [README.md](../core/orchestrator/README.md) | 126 | Framing, synthesis map against the two existing subsystems, rule-prefix index, 5 operating principles |
| [lifecycle.md](../core/orchestrator/lifecycle.md) | 300 | 8 phases (P0 Intake → P7 Close-out) covering all 16 brief items; decision points D1–D19; trivial-task collapse |
| [state-and-contract.md](../core/orchestrator/state-and-contract.md) | 251 | `RunState` model (ST-1…ST-8), a precedence ladder (safety > user instruction > repo convention > skill default > library default), the skill invocation/return envelope (IC-1…IC-8), context-management rules (CM-1…CM-6) |
| [failure-recovery-and-escalation.md](../core/orchestrator/failure-recovery-and-escalation.md) | 223 | Failure classes F1–F9, an 8-rung recovery ladder, loop budgets, gate classes, human-approval-gate design (GA-0…GA-8) |
| [security-and-validation.md](../core/orchestrator/security-and-validation.md) | 140 | Orchestrator security boundaries (SB-1…SB-9), security/testing gates routing to `SK-QA-002`/`SK-AI-008`/`SK-QA-001`/`SK-AI-007`, final-validation checklist (FV-1…FV-12) |
| [observability-and-evaluation.md](../core/orchestrator/observability-and-evaluation.md) | 136 | Run-record ledger (explicitly scoped apart from `SK-QA-004`'s domain), evaluation hooks honestly scoped against the not-yet-built evaluation suite |
| [self-review.md](../core/orchestrator/self-review.md) | 252 | The mandated architecture self-review — see below |

Independently verified: `lifecycle.md` and `README.md` cross-reference
`routing-architecture`/`dependency-architecture` rather than restating
their content (5 cross-links checked); `core/routing-architecture/`,
`core/dependency-architecture/`, `core/skill-specification/`, and
`core/taxonomy/` were confirmed unmodified, matching the instruction that
any discrepancy found there should be flagged, not silently edited.

### Three Layer-0 skills (reference implementation)

| Skill | ID | Tier | Files |
|---|---|---|---|
| [skill-router](../skills/skill-router/) | SK-ORCH-001 | A | yaml, SKILL.md |
| [capability-adapter](../skills/capability-adapter/) | SK-ORCH-002 | A | yaml, SKILL.md |
| [workflow-composer](../skills/workflow-composer/) | SK-ORCH-003 | A | yaml, SKILL.md |

All `kind: generic`, `layer: 0`, `domain: ORCH`. Independently verified
(not taken from the agent's self-report):

- All required fields present per VR-1; `depends_on_skills`/
  `conflicts_with` explicit.
- **`depends_on_skills` correctness, the project's standing
  zero-tolerance discipline**: `workflow-composer.depends_on_skills:
  [SK-ORCH-001]` — a genuine hard composition (the composer always
  consults the router's output), correctly distinguished from mere
  relatedness. `skill-router` and `capability-adapter` both `[]`,
  matching the catalog's "Dependencies: None" for both.
- No `parents` field on any of the three (correctly not technology
  skills).
- CE-1: description lengths 391 / 396 / 408 chars, all ≤500.
- VR-2: `SKILL.md` frontmatter has exactly the 3 required keys, byte-
  identical `name`/`description`/`spec_version` to `skill.yaml`, for all
  three.
- YAML self-checks: all three parse cleanly.

## A cross-batch defect found and fixed during this step

The delegated design agent's own self-review (see below) surfaced a
finding while reading the existing skill corpus for grounding: **10 of
the 83 previously-authored skills have an `execution_tier` /
`required_capabilities` inconsistency** against the specification's own
field definition (`execution_tier`: "`A` (advisory/file only) | `B`
(needs shell) | `C` (needs a non-universal capability)").

This was **independently re-verified from scratch** (not taken from the
agent's report) by scripting a full-repo scan against VR-5's rule plus
the tier field's own definition, and by checking the *distribution* of
`required_capabilities` values within each tier across all 86 skills —
confirming the flagged 10 are genuine outliers against an
overwhelmingly consistent pattern (82% of Tier B skills already declare
`shell`; the remaining 3 Tier-A skills that aren't `[file-read,
file-write]` are `[file-read]`-only, none declare `shell`):

- **8 Tier-B skills declaring only `[file-read, file-write]`** (missing
  `shell`): `observability` (Step 23) and 7 of the 8 AI/LLM skills from
  Step 26 — `agent-architecture`, `ai-security`,
  `llm-application-engineering`, `llm-evaluation`,
  `prompt-context-engineering`, `rag-engineering`,
  `structured-output-tool-calling`. (`model-selection`, Tier A, was
  unaffected.)
- **2 Tier-A skills declaring `shell`** (pre-dating this project's
  master-plan-driven phase): `code-review`, `git-conventions`.

**Fix applied, direction determined by re-reading each skill's own
documented purpose/scope, not by mechanically forcing tier-conformance**:
the 8 Tier-B skills had `shell` added to `required_capabilities` (each
one's scope genuinely involves implementing/testing code, not just
producing analysis — e.g. `rag-engineering`'s pipeline implementation,
`ai-security`'s mitigation implementation); the 2 Tier-A skills had
`shell` *removed* (neither `code-review`'s diff-analysis-and-report
scope nor `git-conventions`' message/branch-name-generation scope
documents any need to execute commands — `git-workflow`, a separate
skill, owns the actual git *operations*). Re-verified after the fix:
**zero VR-5 inconsistencies remain across all 86 skills, zero YAML parse
failures.** `SKILL.md` prose for all 10 skills was checked and contains
no capability claims contradicted by the fix.

This defect had already been present across two previously-committed-
and-pushed batches (Observability, AI/LLM) without being caught by
either batch's own verification pass — a gap in this project's own
verification discipline (prior passes checked CE-1, VR-1 field presence,
`depends_on_skills`/`parents` correctness, and YAML validity, but not
VR-5 tier/capability consistency) now closed by adding this check to the
verification routine going forward.

## Unresolved questions (from the mandated self-review, not resolved here)

The self-review ([self-review.md](../core/orchestrator/self-review.md))
is unusually candid and should be read in full rather than summarized
away; its highest-severity finding is structural, not a wording nit:

1. **Nothing in this design is enforced** — every rule is an obligation
   on an LLM following instructions; there is no validator or runtime
   that can prevent a non-compliant run. This is stated as the design's
   central honest limitation, not papered over.
2. **The skill invocation contract is a normalization schema, not a
   protocol** — no skill emits a structured return value; the
   orchestrator reconstructs one from a skill's prose output. Flagged as
   the design's most load-bearing compromise.
3. **Failure recovery assumes skills report failure honestly** — a
   confident-but-wrong advisory output satisfies every check this
   architecture has. Named as an accepted, unmitigated risk, not solved.
4. **The grounding convention for design-doc-grounded skills is
   unsettled**: this step's three skills follow `code-review`'s
   precedent (`grounding: mixed` + internal `source_references`), but
   three earlier Discovery skills use `grounding: engineering-convention`
   with no `source_references` for the same situation, and the
   specification names no value that unambiguously fits either. **Left
   as a flagged, unresolved specification ambiguity** rather than
   resolved unilaterally in this step — it doesn't block this step's
   correctness and deserves a deliberate ruling, not a quiet precedent-
   setting choice buried in an unrelated commit.
5. Two directory READMEs (`evaluations/README.md`, `core/README.md`)
   are stale scaffold text overtaken by events (e.g. "no skills exist
   yet to evaluate" with 86 now existing) — left alone, since fixing
   them belongs to the later steps that actually build those subsystems
   (Step 30 for evaluations, in particular).
6. Eight further open architectural questions are recorded in the
   self-review's Part 4 (run-record persistence across session/
   compaction boundaries, the relationship between this architecture's
   `ExecutionPlan` and a host's own native planning UI, whether the
   return envelope should become a real emitted structure, the P4
   admission-gate threshold, whether `workflow-composer` should split,
   whether the loop-budget numbers are acceptable placeholders, how to
   treat a target repository's own installed skills, and whether a
   three-skill Layer 0 is the right framing at all) — none resolved here,
   consistent with "mark unresolved, don't guess."

None of these affect the correctness of what was verified above (the
three skills are internally consistent and spec-compliant); they are
open design questions for a future review pass, most naturally Step 29
(Cross-Skill Audit) or Step 33 (Final Principal Engineer Audit).

## Duplicated responsibilities

**None found.** `core/orchestrator/` explicitly builds on, cross-links
to, and does not restate `routing-architecture`'s 12 determinations or
`dependency-architecture`'s 8-edge-type vocabulary and execution-
semantics model. `observability-and-evaluation.md`'s run-record ledger
is explicitly scoped apart from `SK-QA-004` (observability)'s domain —
the orchestrator observes its own routing/execution decisions, not
application-level system behavior.

## Missing dependencies

None — `skill-router`'s `related_skills` references `SK-DISC-001..003`
(all pre-existing), `capability-adapter`'s references `SK-ORCH-001/003`,
`workflow-composer`'s references `SK-ORCH-002`, `SK-DISC-003`,
`SK-CONV-007`, `SK-QA-001` — all confirmed to exist on disk.

## Overall assessment

The orchestrator architecture is a genuine synthesis, not a restatement:
it closes real gaps the existing routing/dependency docs left open (a
formal state model, an invocation contract, a failure-recovery ladder
distinct from software resilience patterns, security/testing gate
points, an honestly-scoped evaluation-hook design) while correctly
declining to fabricate content for this library's still-open research
gaps (resilience patterns, the evaluation suite itself). The mandated
self-review is the strongest evidence of quality in this batch — it
argues against its own design's completeness with specific, load-bearing
findings rather than performing a rubber-stamp pass, continuing this
project's "mark unresolved, don't guess" discipline at the architecture
level, not just the skill-content level. The incidental discovery and
fix of a real, two-batch-spanning VR-5 defect (10 skills) is this
step's second most significant outcome: a concrete demonstration that
architecture-level work surfaces defects skill-level batches miss, and a
correction to this project's own verification routine (VR-5
tier/capability consistency is now a standing check) rather than a
one-off patch.
