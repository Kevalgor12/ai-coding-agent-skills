# Audit: Real-World Evaluation (Step 32)

Date: 2026-09-11. Scope: [`audits/real-world/`](real-world/) — a
principal-engineer-level evaluation of the whole Skill Library against 15
realistic engineering tasks (one per domain named in the master plan),
deliberately weaving in all 10 named adversarial patterns (ambiguous
requirements, contradictory instructions, outdated technology assumptions,
irrelevant skills, excessive context, legacy code, security-sensitive
changes, performance regressions, failed dependency, partial tool
failure) at least once each. This is **Step 32** of the master build
plan, model/effort Opus 5 / xhigh — the highest-reasoning-effort
evaluation step in the plan.

## What was built

Unlike Step 30 (behavioral scenarios, hypothetical by construction) and
Steps 28/29 (structural review of skill content in isolation), Step 32
actually **traces real tasks through the real skill files** — reading
each candidate skill's actual `activation_conditions`,
`non_activation_conditions`, `depends_on_skills`, `failure_handling`, and
`escalation` fields, and determining what a compliant orchestrator run
(per `core/orchestrator/`) would actually do, then critically evaluating
that trace across 10 dimensions (routing, dependency activation, context
efficiency, implementation quality, security, testing, maintainability,
error handling, convention adherence, final outcome).

| Component | Content |
|---|---|
| 5 parallel Opus agents, 3 domain tasks each | Frontend/Backend/Databases · APIs/Testing/Security · Performance/Git/CI-CD · Infrastructure/Search/Realtime · Documentation/AI-LLM/Multi-domain |
| `audits/real-world/*.md` × 15 | One file per task: routing trace with real file:line citations, findings (finding/severity/root cause/correction/regression-test-requirement), 10-dimension score table |
| `audits/real-world/synthesis.md` | Cross-cutting pattern analysis, scenario-ID reconciliation, independent re-verification record |

Each agent was briefed with the standing guardrails from Steps 27-31 (no
sub-agents, no git commands) and was required to check `audits/cross-skill/`
and `audits/2026-09-10-individual-skill-review.md` first, so findings build
on Steps 28/29 rather than re-deriving them — several files explicitly
confirm a known finding (X-02, X-03, X-04) is either "still live and now
proven task-critical" or "does not bite on this task," with evidence
either way.

## Verification performed

Per this project's standing discipline — never trust an agent's own
"success"/"finding" self-report — verification here had two layers:

1. **Mechanical severity count**, independent of any agent's self-reported
   tally: `grep -hoE '\*\*(Critical|High|Medium|Low)\*\*\s*$' audits/real-world/*.md | sort | uniq -c`.
   Result: **5 Critical, 39 High, 25 Medium, 2 Low — 71 findings total**
   across 15 files (8,121 lines). This superseded the individual agents'
   own tallies, which were consistent with this count but not identical
   in every file (a few "what the library gets right" or score-table
   headers looked finding-shaped to a naive count and had to be excluded).
2. **Direct file re-verification of 6 claims** — the "most significant
   finding" each of the 5 agents reported, plus one supporting claim — read
   directly against the cited `skill.yaml`/`core/` lines rather than
   accepted on the agent's word:
   - `core/orchestrator/state-and-contract.md:207-209` (IC-6 wording) — confirmed verbatim.
   - `skills/postgresql/skill.yaml:174-206` (`covered_versions`, `reverify_triggers`, `failure_handling`) — confirmed the version-floor gap exists exactly as described.
   - `skills/realtime-communication/skill.yaml:12,23,32` + `SKILL.md` + `references/transport-comparison.md` (SSE) — confirmed SSE is named in Tier-0 fields and reasoned about nowhere else.
   - `skills/requirements-engineering/skill.yaml:33` and `skills/solution-architecture/skill.yaml:37-39,115` (SR-2/contradiction gap) — confirmed both skills' non-activation wording excludes the contradictory-request case.
   - `skills/database-operations/skill.yaml:29-33` and `skills/data-modeling/skill.yaml:34` (M-06) — confirmed all four activation conditions are symptom-shaped, and confirmed the "not yet authored" cross-reference is still stale despite `database-operations` existing since Step 26/27.

   All six held up exactly as reported — no fabricated, exaggerated, or
   misattributed finding was found in this sample.
3. **Scenario-ID collision caught and reconciled.** All 5 agents, working
   in parallel and unaware of each other, independently proposed new
   `evaluations/scenarios/` entries starting at `S17` — the result was up
   to 5 different, unrelated proposed scenarios each claiming the same ID
   (`S17`, `S18`, `S19` collided worst). One agent caught this happening in
   real time mid-run and flagged it rather than silently colliding further.
   `synthesis.md` performs the reconciliation: 22 distinct proposed
   scenarios (after merging 2 pairs that turned out to be the same gap
   described from two tasks) assigned canonical IDs `S17`–`S38`, with a
   recommended build-first trio (`S23`, `S31`, `S37`) that would close all
   five Critical findings.

## Key findings (five Critical, synthesized in full in `real-world/synthesis.md`)

All five trace to the same underlying defect class, found independently
five times by five agents who could not see each other's work — a
**metadata-execution gap**: a routing/governance field
(`activation_conditions`, `covered_versions`, `verification`,
`non_activation_conditions`) is well-formed and passes every static
check this library's Steps 28-31 have run against it, and still fails to
do its job the one time it is traced through an actual task, because
either nothing downstream reads it under the condition that matters, or
its own wording excludes the case it exists to catch:

1. **G-5** — the library's strongest ambiguity-detection rule (SR-2)
   excludes the only two skills that could surface a self-contradictory
   request ("strict branch protection + allow force-push to main").
2. **F1-DB** — `covered_versions` is a disclosure field with no consumer;
   a request for a version below a skill's declared floor produces
   confidently-wrong, over-engineered guidance rather than a flagged gap.
3. **F2.1** — IC-6's "never claim untested work passed" downgrade cannot
   fire for 49 of 52 Tier B/C skills, because almost none declare a
   `verification` item whose *execution* actually depends on the capability.
4. **F3.1** — the exact decision a "fix insecure session storage" task is
   about (localStorage vs. httpOnly cookies) is owned by no skill; the
   skill that owns XSS is excluded from this task class by its own
   non-activation wording.
5. **M-06** — the live-auction stress test's core correctness problem
   (concurrent-bid race conditions) has no staffed owner: symptom-shaped
   activation conditions plus a stale "not yet authored" cross-reference
   (Step 29's X-02, confirmed still live) mean a compliant run ships with
   no isolation level and no row lock, and passes every review facet.

66 further findings (39 High, 25 Medium, 2 Low) are recorded in the 15
domain files, each with root cause, recommended correction, and a
regression-test-requirement pointing at a specific scenario (existing or
newly proposed).

## What the library gets right

Recorded explicitly in `synthesis.md` rather than only implied by
omission: routing correctly excludes obviously-wrong skills across every
task tested (no false-positive activation on GraphQL/Three.js/WebRTC by
name-matching), the capability degradation ladder (F2→R3→R4) engaged
correctly under simulated mid-run capability loss, CI/CD and security
content is technically strong wherever it does activate, and the
multi-domain stress test (a legacy Rails stack with no matching
technology skill, genuine requirements ambiguity, and deadline pressure
arguing against modernization) correctly avoided all three of its
deliberately-placed traps. The defects found concentrate in the *edges*
of routing — whether a skill fires at all — not in the technical
substance once a skill has correctly activated.

## Overall assessment

This step is the first point in the project where skill content was
traced through actual task execution rather than reviewed in isolation
(Steps 28-29) or checked for structural/lossiness compliance (Step 31).
That shift in method is what surfaced the metadata-execution gap pattern:
every field involved in the five Critical findings had already passed
Step 28's per-skill review and Step 29's cross-skill consistency audit,
because both of those passes checked whether fields were well-formed and
cross-referentially valid — neither asked whether a realistic task
actually reaches a field's positive branch. That is a new, mechanically
addable question for any future repeat of Steps 28/29 (a "reachability"
check), not a criticism of what those steps already did well.

No skill file, `core/` document, or `evaluations/` file was modified by
this step or by any of the 5 agents it dispatched — Step 32 is
audit-only, per the master plan's separation between evaluation (32) and
correction (33/34). The 16 files under `audits/real-world/` (15 domain
audits + synthesis) are the complete deliverable.
