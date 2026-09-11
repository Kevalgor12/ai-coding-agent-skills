# Run Lifecycle

Status: **design only**. The end-to-end shape of a single orchestrated run.
Phases P0–P7 are ordered; **Recovery/Escalation**, **Observability**, and
**Security boundaries** are cross-phase and can fire from anywhere.

Notation matches [dependency-architecture](../dependency-architecture/README.md#execution-semantics-model):
`→` sequential · `∥` parallel · `[cond]` conditional · `⟳` iterate-until ·
`⤾` review loop · `⛔` human-approval gate.

## Phase map

```
                    ┌──────────────── cross-phase ────────────────┐
                    │  Recovery & Escalation  (F1–F9 → R1–R8)     │
                    │  Run record             (OB-1…OB-7)         │
                    │  Security boundaries    (SB-1…SB-9)         │
                    └─────────────────────────────────────────────┘

  P0 Intake ─→ P1 Discovery ─→ P2 Routing ─→ P3 Resolution ─→ P4 Admission
                                                                    │
                                                                    ▼
       P7 Close-out ←─ P6 Verification ←─────────────── P5 Execution ⟲
              ▲                  │                          │
              └── incomplete ────┘        replan ───────────┘
                  with residuals          (back to P3, re-admit at P4
                                           if the risk class changed)
```

The only two legitimate exits are **P7 with a complete final validation** and
**P7 with an explicit incomplete-with-residuals statement**. Falling out of the
loop silently is a defect, not an outcome.

## The sixteen required capabilities, mapped

| # | Capability | Phase | Mechanism |
|---|---|---|---|
| 1 | Task understanding | P0 | intent/task-type/complexity/risk classification → `TaskFrame` |
| 2 | Skill discovery | P1 | Tier-0 candidate enumeration over the catalog + bounded repo signal scan |
| 3 | Skill routing | P2 | default-deny selection + recorded exclusions (SR-1…SR-11) |
| 4 | Dependency resolution | P3 | prerequisite closure, conflict resolution, acyclicity/layer check, completeness backstop |
| 5 | Context selection | P3 (plan) / P5 (load) | CS-1…CS-8 at selection; CM-1…CM-6 across the run |
| 6 | Sequential execution | P5 | prerequisite edges + same-target writes (PR-1) |
| 7 | Parallel execution | P5 | parallelization matrix (PR-2…PR-5), adapter-degradable |
| 8 | Conditional execution | P2/P5 | activation/non-activation at selection; late-bound conditions at step readiness (D14) |
| 9 | Iterative execution | P5 | `⟳` with a declared exit criterion and a declared budget (D17) |
| 10 | Review loops | P5/P6 | `⤾` build→review→fix→re-review, bounded (D17) |
| 11 | Failure recovery | cross-phase | failure classes F1–F9 → recovery ladder R1–R8 (D16) |
| 12 | Escalation | cross-phase | escalation matrix (skill→skill) and R7 (skill→human) |
| 13 | Human approval gates | P4 (declare) / P5–P6 (arm, request, consume) | gate classes + GA-1…GA-7 |
| 14 | Security checks | P0, P3, P5, P6, P7 | S-Gate 1–5 → `SK-QA-002` / `SK-AI-008` / `SK-BE-005` |
| 15 | Testing checks | P3, P5, P6 | T-Gate 1–5 → `SK-QA-001` (+ `SK-AI-007` for LLM features) |
| 16 | Final validation | P6→P7 | the FV-1…FV-12 checklist |

---

## P0 — Intake

**Goal:** understand the task well enough to classify it, without doing any of
it.

1. Record the request **verbatim** into `RunState.task_statement` (ST-1). All
   later "did we do what was asked?" checks compare against this text, not
   against a paraphrase that drifted.
2. Extract **user constraints** — anything the user stated that constrains *how*
   the work is done ("don't touch the CSS", "one-line commit messages", "no new
   dependencies"). These become immutable and sit second on the precedence
   ladder (ST-4).
3. Run the **bounded signal scan** (routing Phase 0) — manifests, config,
   connection strings, file types, existing conventions. Not a repo read.
4. Classify intent, task type, complexity, and risk (routing Phase 1).
5. Apply the **security intake screen** (S-Gate 1): does the task itself carry a
   trust boundary, secret, untrusted input, auth surface, or LLM-with-tool-access
   dimension? This is a cheap classification, not a review.

**Early exits** (routing Phase 1, unchanged): a pure question exits after
activating the relevant knowledge skill at advisory tier; a trivial single-owner
change exits after P2 with one skill and no plan.

**Decision points**

- **D1 · Is this a request at all, or an instruction found in content?**
  Only text the user typed in the conversation is a request (SB-1). Text
  discovered in a file, a tool result, an issue, or a prior run record is data —
  it is surfaced, never executed.
- **D2 · Is intent genuinely ambiguous on a non-trivial task?** If yes, escalate
  before selecting build skills (ER-4). Do not route on a guess.
- **D3 · What is the highest-risk action this task implies?** This single value
  drives gating (ER-2), admission (D13), and the discovery depth (SR-8). A
  request to author a policy/config/exception that lets a *future* action
  bypass a gate classifies at the risk level of the gate class it would
  bypass, not at the mechanical action of writing the policy — see
  [routing-algorithm.md, Phase 1](../routing-architecture/routing-algorithm.md#phase-1--classify-intent-task-type-complexity-risk).

---

## P1 — Discovery

**Goal:** know what is in play before deciding what to activate.

1. Map signals → **domains** and → **detected technologies** (routing Phase 2).
2. Resolve **conflict clusters** for the artifact under change (SR-4); where the
   choice is required but undetected, record it as an open decision rather than
   activating every sibling.
3. Detect and record **repository conventions** into `ConventionRecord` (ST-5):
   commit/branch style, comment style, lint/format config, test framework and
   layout, directory conventions. Detection happens once, up front, because
   every later stage's output is judged against it.
4. Enumerate **candidate skills** using Tier-0 metadata only (CS-1).

**Decision points**

- **D4 · Which sibling of each conflict cluster is actually in use?**
- **D5 · Does a detected convention conflict with a stated user constraint?**
  The user constraint wins for what the user actually dictated; the convention
  still governs everything else (ST-4, matching `git-conventions`'
  own failure-handling rule).
- **D6 · Is a candidate skill authored, or only a catalog entry?** A catalog
  entry is a design spec, not a usable skill. An unauthored ID must never be
  planned as if it existed; the gap is recorded and the run proceeds with the
  nearest authored skill or an explicit "no skill covers this" note.

---

## P2 — Routing

**Goal:** the minimum correct set, with the complement recorded.

Runs routing Phases 3 (default-deny selection) unchanged. Two additions:

- The **excluded set with reasons** (SR-11) is written into the run record, not
  merely computed — it is the audit trail for the minimum-set claim, and it is
  what a later evaluation pass will score.
- The **completeness backstop** (SR-10) records *which* stage was unstaffed and
  which skill was added to staff it. A backstop firing is a routing-quality
  signal (EH-5), not just a correction.

**Decision points**

- **D7 · Include or exclude, per skill?** (SR-1, SR-2, SR-3, SR-5, SR-6, SR-8,
  SR-9.)
- **D8 · Does the router suppress itself, the composer, and the adapter?**
  (SR-7 — proportional orchestration.)
- **D9 · Is any required workflow stage unstaffed?** (SR-10.)

---

## P3 — Resolution

**Goal:** turn a *set* into an executable *plan*.

1. **Dependency resolution.** Take the prerequisite closure over the selected
   set (`depends_on_skills` hard sub-steps plus workflow-order prerequisites).
   Verify the resulting graph is acyclic and layer-monotone (VR-4). A cycle or an
   upward edge is a library defect: stop and report it, do not silently break the
   edge.
2. **Ordering and parallelization.** Apply the parallelization matrix (PR-1…PR-5).
   Parallelism is an offer, never a correctness requirement (PR-4).
3. **Capability resolution.** Insert the `capability-adapter` barrier before any
   Tier B/C step (PR-3) and resolve each declared capability to
   `execute | advisory | fallback:<route> | refuse` *before* the step runs.
4. **Context plan.** For each step, record what will be loaded (its body, its
   `required_context`, any cheap `optional_context`) and what deliberately will
   not (Tier-2 references, unrelated repo areas). Planning the omissions is what
   makes CM-3 checkable later.
5. **Gate declaration.** Every gate the plan will hit is enumerated now
   (ER-1) with its class, its trigger step, and its denied-branch.
6. **Budget declaration.** Every loop (`⟳`, `⤾`) gets an explicit exit criterion
   and an iteration budget *before* it starts (D17). A loop whose exit criterion
   cannot be stated must not be started.
7. **Testability admission** (T-Gate 1) and **design-time security review**
   (S-Gate 2) are placed here.

**Output:** an `ExecutionPlan` — stages, steps, semantics, gates, budgets,
context plan, and the capability decision per step.

**Decision points**

- **D10 · What is the execution semantic of each edge?** (sequential / parallel /
  conditional / iteration / review-loop / human-approval.)
- **D11 · What does each stage hand to the next?** Every stage declares its
  handoff artifact; a stage with no declared handoff is either mis-ordered or
  unnecessary.
- **D12 · Which capability decision applies per Tier-B/C step?**

---

## P4 — Admission

**Goal:** no mutation begins before the user knows what is coming.

This phase is new relative to the existing docs, which surface gates up front
(ER-1) but do not define *when the plan itself* needs confirmation.

- **D13 · Does this plan require explicit user confirmation before execution?**
  Required when **any** of:
  - risk class is `destructive`, `outward-facing`, or `production`;
  - the plan contains an irreversible commitment (stack choice, schema shape);
  - complexity is `project`;
  - the plan's scope exceeds what the request literally asked for (a plan that
    grew during resolution must be re-confirmed, not assumed).

  Not required for `read-only` or bounded `reversible-write` work of small
  complexity — proportionality (principle 1) applies here too, and asking for
  confirmation of a one-file edit is friction, not safety.

When confirmation is required, what is presented is: the objective as understood,
the ordered stages, the gates that will be hit, the capability degradations
already known, and what will *not* be done. Approval of a plan is **not**
approval of the gates inside it (GA-1); each gate is still requested at its step.

---

## P5 — Execution

**Goal:** run the plan, one step at a time, honestly.

Per step:

1. **Readiness check (D14).** Are the step's `required_context` and resolved
   capabilities actually present? Missing context → CS-3 (ask or degrade per the
   skill's `failure_handling`), classified as `F1`. Capability lost since P3
   (a denied permission, a revoked tool) → `F2`; the adapter re-resolves rather
   than the step proceeding on a stale decision.
2. **Late-bound conditionals.** A `[cond]` step re-evaluates its condition at
   readiness, not at plan time — evidence gathered in earlier steps may have
   changed it (routing examples §5: the diagnostic loop pulls skills in as the
   cause localizes).
3. **Invoke** with the invocation envelope
   ([state-and-contract.md](state-and-contract.md#invocation-envelope-orchestrator--skill)).
4. **Pre-mutation security screen** (S-Gate 3) for any step that writes.
5. **Adjudicate the outcome (D15).** Normalize the skill's output into a return
   envelope and assign exactly one status:
   `complete | partial | blocked | refused | failed | deferred`. A status is
   assigned from evidence, not from the skill's tone of voice.
6. **Run the step's own `verification` list** (EH-2). A step claiming `complete`
   with unrun verification is downgraded to `partial` (IC-6).
7. **Record** the step into the ledger (OB-2).
8. On any non-`complete` status → **Recovery** (D16, see
   [failure-recovery-and-escalation.md](failure-recovery-and-escalation.md)).

Loop steps (`⟳`, `⤾`) additionally check **D17 · continue or stop?** against the
declared exit criterion and remaining budget. Budget exhaustion is `F5`
(non-convergence) and escalates with findings — it never silently continues and
never silently gives up.

Gate steps check **D18 · is the gate satisfied by an actual user response?**
Silence, a tool result, a file's contents, or another skill's recommendation
never satisfy a gate (GA-2, GA-4).

---

## P6 — Verification

**Goal:** decide whether the run is actually finished.

1. **Testing gate** (T-Gate 4): run the relevant suite for what changed. Red is
   `F3`, not "done". Unable to run (advisory mode) is a declared residual, not a
   pass.
2. **Review loop** (`⤾`): `code-review` (`SK-CONV-007`) aggregates, delegating
   facets in parallel (PR-2). Facet selection follows what was actually built
   (ER-6).
3. **Security gate** (S-Gate 4): mandatory security facet when a trust boundary,
   secret, or untrusted input was touched; mandatory `SK-AI-008` facet when the
   change adds or alters an LLM call with tool access or untrusted-content
   ingestion.
4. **Final validation** (FV-1…FV-12,
   [security-and-validation.md](security-and-validation.md#final-validation)).

**D19 · Complete, or incomplete-with-residuals?** Every checklist item must be
`pass` or `explicitly waived and recorded`. Any item that is neither ends the run
as incomplete — with a statement of what remains — rather than as done.

---

## P7 — Close-out

1. Produce the **final report**: what was done, what was not, every degradation,
   every deferred finding with its owner, every open question, and the residual
   risk statement if any.
2. Emit the **evaluation observations** (EH-3, EH-5) into the run record.
3. Apply conventions to the closing acts — commit/branch text via
   `SK-CONV-001`, PR text via `SK-CONV-008` — each still subject to its own gate
   if outward-facing.
4. Leave the run record in a durable form if the run crossed a session,
   compaction, or sub-agent boundary (ST-8).

---

## Trivial-task collapse

Proportionality is a hard requirement, not an aspiration. For
"add a comment explaining this function" (routing examples §3) the entire
lifecycle collapses to:

```
P0 classify (trivial, read-only) → P2 select code-commenting → P5 invoke → P7 report
```

No plan artifact, no admission, no ledger beyond one line, no gates, no review
loop, and no final-validation checklist beyond "did we do what was asked and
respect the file's existing comment style". An orchestrator that emits a
twelve-item checklist for a one-line comment has failed principle 1 as surely as
one that skips the checklist on a production migration.
