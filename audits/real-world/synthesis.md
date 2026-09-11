# Step 32 — Real-World Evaluation: Synthesis

Date: 2026-09-11. Scope: consolidates 15 domain-task audits produced by 5
parallel agents, each tracing 3 realistic engineering tasks through the
actual skill library (routing, dependency activation, orchestrator
lifecycle) rather than describing hypothetical behavior. Covers all 15
domains and all 10 adversarial patterns named in the master plan's Step
32 prompt, one occurrence of each pattern at minimum. This document does
the synthesis work the plan requires after the parallel fan-out: dedupe
cross-cutting patterns, reconcile a scenario-ID collision the parallel
agents could not see coming, and independently re-verify a sample of the
highest-stakes claims before they're treated as established.

## Method note: mechanical count over self-report

Per this project's standing discipline (established after incidents in
Steps 27/28), the finding totals below are a **grep-mechanical count**
against the 15 files' actual severity tags, not a sum of each agent's own
self-reported tally:

```
grep -hoE '\*\*(Critical|High|Medium|Low)\*\*\s*$' audits/real-world/*.md | sort | uniq -c
```

| Severity | Count |
|---|---|
| Critical | 5 |
| High | 39 |
| Medium | 25 |
| Low | 2 |
| **Total** | **71** |

(A handful of additional `### `-headed sections in the source files are
score tables, appendices, or "what the library gets right" call-outs, not
findings — the mechanical count above excludes them by construction,
since it keys off the severity tag every actual finding carries.)

## Independent re-verification performed

Before treating any agent's "most significant finding" as established,
six of them were checked directly against the files they cite, not taken
on the agent's word:

1. **IC-6 wording** (`core/orchestrator/state-and-contract.md:207-209`) —
   confirmed verbatim: *"`complete` requires `verification` to have
   actually run and passed. Verification `not-run` downgrades the status
   to `partial`... automatically."*
2. **`postgresql` version coverage** (`skills/postgresql/skill.yaml:174-206`)
   — confirmed `covered_versions: ">=14 <=18"`; confirmed all four
   `reverify_triggers` point forward (new major GA, md5 removal, pg_upgrade
   range change, new protocol); confirmed `failure_handling`'s three items
   cover unknown-version, no-shell, and no-EXPLAIN-output — none cover a
   *known* version below the declared floor.
3. **`realtime-communication` SSE claim** — confirmed SSE is named at
   `skill.yaml:12,23,32` (purpose/description/activation_conditions);
   confirmed `references/transport-comparison.md` and the decision-framework
   prose in `SKILL.md` (e.g. line 66's "the three transports") reason about
   exactly three transports, never SSE.
4. **`requirements-engineering` non-activation** — confirmed
   `skill.yaml:33`: *"The requirements are already explicit, unambiguous,
   and narrowly scoped"* — confirmed this is worded per-clause, not
   per-request, so a request that is a conjunction of two individually-clear
   clauses satisfies it.
5. **`solution-architecture` contradiction-escalation** — confirmed it is
   the only skill library-wide with contradiction-handling escalation text
   (`skill.yaml:115`); confirmed its own `non_activation_conditions`
   (`skill.yaml:37-39`) also excludes an already-fixed-stack request.
6. **`database-operations` activation conditions** (`skill.yaml:29-33`) —
   confirmed all four are symptom-shaped ("slow query," "N+1 suspected")
   with no domain-property trigger; confirmed `data-modeling/skill.yaml:34`
   still reads *"route to database-operations, **not yet authored**"* even
   though `database-operations` has existed since Step 26/27 — Step 29's
   X-02 finding, still live, now shown to sit on a task-critical edge.

All six held up exactly as reported. No fabricated or exaggerated finding
was found in this sample, which is a meaningfully larger and more
consequential check than a spot-check nod — these are the six findings
each agent independently flagged as the single most important thing it
found, and every one survived direct file-level scrutiny.

## The cross-cutting pattern: a metadata-execution gap

Read together, the five agents' independent "most significant findings"
are not five unrelated defects — they are the same defect class, found
five times over, in five parts of the library that never talk to each
other:

| Agent's top finding | The metadata that exists | Why it doesn't fire |
|---|---|---|
| IC-6 structurally inert (testing/security) | `verification` lists on 52 Tier B/C skills | Only 3 of 52 declare an item whose *execution* actually requires shell — the rest are static properties, so `not-run` never triggers the downgrade |
| `covered_versions` has no consumer (databases) | `postgresql`'s declared `>=14 <=18` range | `reverify_triggers` and `failure_handling` both only watch for drift *forward* in time; nothing watches for a request *below* the floor |
| SR-2 excludes the contradiction-catchers (git) | `requirements-engineering`'s and `solution-architecture`'s own contradiction-handling content | Both skills' `non_activation_conditions` are worded clause-by-clause, so a conjunction of two individually-clear instructions never reaches either skill |
| SSE named but unreasoned (realtime) | `realtime-communication`'s Tier-0 `activation_conditions` lists SSE as selectable | The decision framework, Tier-2 reference, and underlying research corpus only ever cover three transports — SSE was named in the field a router reads and nowhere else |
| `database-operations` unreachable on this task (multi-domain) | Four `activation_conditions` | All four are phrased as symptoms present in request text, not properties of a domain, so a fresh feature request with an implicit concurrency requirement never surfaces them |

The common shape: **a governance/routing field is well-formed, internally
consistent, and passes every static check this library has run against it
in Steps 28–31 — and still fails to do its job the one time it's traced
through an actual task**, because either (a) nothing downstream actually
reads it under the condition that matters, or (b) its own wording excludes
the case it exists to catch. Steps 28 and 29 checked whether these fields
were *well-formed and cross-referentially valid*. Step 31's adapter test
suite showed that even well-formed fields can be silently unprojected
end-to-end. Step 32 is the first pass that actually *executes* a routing
decision against a concrete task, and every execution trace surfaced at
least one field that is correct on paper and inert in practice. This is
the same category of lesson Step 31 learned about its own test suite
(a crash-only check missed four real omissions; only a completeness check
found them) — applied one layer up, to the skill content itself rather
than the adapter code that projects it.

**Recommended structural response**, beyond the individual corrections
listed in each file: add a mechanical **"reachability" check** to the
cross-skill audit process (a Step-29-style pass, not a new skill) that,
for every `activation_condition`/`non_activation_condition`/`covered_*`
field, asks not "is this well-formed" but "does at least one realistic
task actually reach this field's positive branch, and does at least one
downstream consumer act differently because of it." Steps 28/29 already
have the infrastructure (per-skill and cross-skill audit passes) to run
this the next time either is repeated — it does not require new machinery,
only a new question.

## Five Critical findings

1. **G-5 — SR-2 excludes the only skills that can surface a self-contradictory
   request** (`git-conflicting-conventions.md`). "Strict branch protection +
   allow force-push to main for hotfixes" passes through unflagged because
   both individual clauses are unambiguous; no F-class, gate, or precedence
   rule exists for a request that is coherent clause-by-clause and
   self-defeating as a whole.
2. **F1-DB — `covered_versions` is a disclosure field with no consumer**
   (`databases-users-migration.md`). A PG12 request, one version outside
   the declared `>=14 <=18` range, produces a needlessly over-engineered
   multi-phase migration for what is, since PG11, a catalog-only change —
   verified independently above.
3. **F2.1 — IC-6's honesty downgrade is structurally inert for 49 of 52
   Tier B/C skills** (`testing-payment-module.md`). A test suite that is
   never executed once can still be reported `complete`, because almost no
   skill declares a `verification` item whose *execution* actually depends
   on the capability being present.
4. **M-06 — the auction task's core correctness problem has no staffed
   owner** (`multidomain-live-auction.md`). `database-operations`'
   symptom-shaped activation conditions plus a stale `data-modeling`
   cross-reference ("not yet authored" — Step 29 X-02, confirmed still
   live) mean a compliant run ships a bid handler with no isolation level,
   no row lock, and no close-instant semantics, passing every review facet.
5. **F3.1 — the localStorage-vs-httpOnly-cookie decision is owned by no
   skill, and the skill that owns XSS is routed out by SR-2**
   (`security-session-storage.md`). The exact defect this task asks to fix
   (script-readable session tokens) sits in a gap between
   `authentication-authorization` (which owns session mechanisms but not
   the storage-location/XSS-exposure tradeoff in depth) and
   `security-engineering` (which owns XSS but is excluded from this task
   class by its own non-activation wording) — no skill is left holding the
   specific decision the task is about.

## Scenario-ID reconciliation

Five agents worked in parallel, each unaware of the others' output, and
each independently proposed new `evaluations/scenarios/` entries starting
at `S17` (the next free ID after the suite's existing S01–S16). The result
was **the same ID claimed by 4-5 different, unrelated proposed scenarios**
— `S17`, `S18`, and `S19` each mean up to five different things across the
15 files. One agent (frontend/backend/database batch) caught this happening
in real time and flagged it explicitly rather than silently colliding.

This reconciliation assigns one canonical ID per **distinct** proposed
scenario, merging two pairs that turned out to be the same underlying gap
described from two different tasks:

| Canonical ID | Name | Source file(s) | Category | Priority signal |
|---|---|---|---|---|
| S17 | broad-footprint-repo-narrow-task | frontend (`S17`) + apis (`S17`, second variant: GraphQL/OpenSearch) | Simple / excessive-context | — |
| S18 | rendering-mode-decision-no-owner | frontend (`S18`) | Ambiguous | — |
| S19 | design-time-performance-no-measurement | frontend (`S19`) + backend (explicit fold request, second variant: CSV batch size) | Performance-sensitive | — |
| S20 | verification-step-unstaffed | backend (`S20`) | Failure | — |
| S21 | implementation-choice-raises-risk-class | backend (`S21`) | Security-sensitive | — |
| S22 | ci-pipeline-over-knowingly-flaky-suite | cicd (`S19`) | Ambiguous | — |
| S23 | strict-branch-protection-force-push-exemption | git (`S18`) | Conflicting-requirement | build early — closes the Critical G-5 gap |
| S24 | legacy-dockerfile-no-cicd | infrastructure (`S17`) | Legacy-code | — |
| S25 | dashboard-regression-after-known-deploy | performance (`S17`) | Performance-sensitive | — |
| S26 | one-way-live-status-push | realtime (`S19`) | Simple / multi-skill | — |
| S27 | new-realtime-channel-repo-already-has-two | realtime (`S20`) | Conflicting-requirement | sibling to existing S16 |
| S28 | fulltext-search-over-populated-catalog | search (`S18`) | Performance / maintainability | — |
| S29 | changing-live-authentication-mechanism | security (`S19`) | Security-sensitive | — |
| S30 | first-tests-untested-module-shell-lost-before-execution | testing (`S18`) | Failure | distinct from existing S14 |
| S31 | technology-version-outside-declared-coverage | databases (`S22`) | Failure | closes the Critical F1-DB gap |
| S32 | migration-shape-proportional-to-engine-behavior | databases (`S23`) | Legacy-code | — |
| S33 | api-docs-and-stale-readme | documentation (`S17`) | Multi-skill | suite currently has zero documentation scenarios |
| S34 | readme-setup-unverifiable | documentation (`S18`) | Failure | — |
| S35 | rag-support-chatbot-human-fallback | ai-llm (`S19`) | Multi-skill | — |
| S36 | auction-on-unsupported-stack | multi-domain (`S20`) | Multi-skill | — |
| S37 | concurrent-bid-contention | multi-domain (`S21`) | Multi-skill | **highest single value** — its own author's explicit recommendation ("build this one first"); closes Critical M-06 |
| S38 | modernization-mentioned-not-requested | multi-domain (`S22`) | Legacy-code | — |

Plus one item that is **not** a scenario by design: `ai-llm-support-chatbot.md`
correctly identifies `rag-engineering`'s hosted-retrieval-surface gap as a
`reverify_triggers`-style staleness condition, not a behavioral assertion —
it belongs in `evaluations/regression-suite.md` as a trigger, not as a
17th–38th scenario file.

**This document performs the reconciliation, not the authoring.** Per the
master plan, Step 32's deliverable per task is a
finding/severity/root-cause/correction/**regression-test-requirement** — a
recommendation of what should be tested, not the scenario file itself.
Authoring 22 new scenario pairs (44 files, on the scale of Step 30's own
16-scenario, ~40-agent-hour effort) is out of this step's scope and is
recorded here as prioritized backlog for a future evaluation-suite
expansion pass. If only three are built before then, build **S23**, **S31**,
and **S37** — each closes one of the five Critical findings above.

## What the library gets right (worth stating, not just gaps)

Every one of the 15 files includes an explicit "what the library gets
right" pass, and the pattern across all 15 is consistent: **routing
correctly excludes obviously-wrong skills** (GraphQL/Three.js/WebRTC are
never falsely activated by name-based over-matching), **the capability
ladder (F2→R3→R4) is genuinely well-designed** and engages correctly under
simulated mid-run capability loss, **CI/CD and security content is
technically strong** where it does activate, and **the multi-domain stress
test correctly avoided all three of its baits** (no Rails-flavored
Express advice, no unrequested modernization, gates fire on real risk).
The defects found are concentrated in the *edges* of routing — the
metadata fields that decide whether a skill fires at all — not in the
technical substance once a skill has correctly activated. That is a
narrower, more tractable failure surface than "the guidance is wrong,"
and it is the right place for a routing-focused library's remaining risk
to live.

## Recommended priority order (for Step 33)

1. Fix the two mechanically-cheap items first: `data-modeling/skill.yaml:34`'s
   stale "not yet authored" cross-reference (one line; Step 29 X-02,
   proven task-critical by M-06), and `database-operations`'
   `activation_conditions` (add a domain-property trigger, e.g. "the task
   involves concurrent writes to shared state").
2. Add proposed rule **VA-6** (coverage-deficient version handling) and
   failure class **F10** (topically-in-scope, knowledge-range-excluded) to
   `core/orchestrator/`, and extend `postgresql`'s (and by the same pattern,
   every version-scoped skill's) `failure_handling` to cover a request
   *below* `covered_versions`, not only "version unknown."
3. Add proposed rule **VR-9** (a Tier B/C skill must declare at least one
   `verification` item whose execution genuinely depends on the declared
   capability) so IC-6 has something to downgrade on library-wide, not
   only in the 3 skills that already qualify.
4. Narrow `requirements-engineering`'s and `solution-architecture`'s
   `non_activation_conditions` so a request that is a conjunction of two
   individually-unambiguous, mutually-inconsistent clauses is recognized
   as *not* "already explicit, unambiguous, and narrowly scoped" — closing
   the SR-2 gap at its source rather than adding a special case elsewhere.
5. Either give `realtime-communication` real SSE reasoning (decision
   framework + Tier-2 reference row) or remove it from the three Tier-0
   fields that currently advertise it as selectable — the mismatch between
   what routing sees and what the skill can actually reason about is the
   defect, and either fix closes it.
6. Build scenarios **S23**, **S31**, **S37** (see reconciliation table) as
   the minimum regression coverage for the five Critical findings.

## Scope discipline note

No skill file, `core/` document, or `evaluations/` file was modified by
this step or by any of its 5 dispatched agents — Step 32 is audit-only,
consistent with the master plan's separation between evaluation (Step 32)
and correction (Step 33/34). All 15 domain-task files plus this synthesis
are the complete Step 32 deliverable.
