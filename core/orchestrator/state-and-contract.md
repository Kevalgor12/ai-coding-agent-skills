# Run State & the Skill Invocation Contract

Status: **design only**. Two things the existing subsystems do not define: the
**state** carried across a multi-skill run, and the **contract** at the boundary
between the orchestrator and a skill.

---

## Part 1 — Run state

### Why a formal state model at all

Routing produces a decision; workflows produce a shape. Neither says what
survives *between* stages, what may be revised, or what must never change. Three
concrete failures come from leaving that implicit:

- **Intent drift** — by stage six, the thing being built is a paraphrase of a
  paraphrase of what was asked.
- **Convention drift** — the first stage detected the repo's commit style; the
  last stage, which actually commits, never saw it.
- **Laundered failure** — a step failed at stage three, was quietly dropped, and
  the run reported success at stage nine.

The state model exists to make each of those mechanically visible.

### Structure

```
RunState
├── identity
│   ├── run_id
│   ├── task_statement          # verbatim, immutable          (ST-1)
│   └── started_at
├── task_frame                                                  (P0)
│   ├── intent · task_type · complexity · risk_class
│   ├── signals                 # the bounded scan's output
│   ├── user_constraints[]      # immutable                     (ST-4)
│   └── ambiguities[]           # surfaced, never assumed away
├── convention_record[]         # detected repo conventions; immutable (ST-5)
├── routing_record                                              (P2)
│   ├── selected[]              # skill_id + why
│   ├── excluded[]              # skill_id-or-class + why       (SR-11)
│   └── backstop_additions[]    # stage that was unstaffed + skill added
├── plan                        # revisable only via replan     (ST-6)
│   ├── stages[] → steps[]      # semantic, handoff artifact, context plan
│   ├── gates[]                 # class, trigger step, denied-branch
│   ├── budgets[]               # per loop: exit criterion + max iterations
│   └── capability_decisions[]  # per Tier-B/C step
├── ledger[]                    # append-only, never rewritten  (ST-7)
│   └── decision | invocation | mutation | gate | degradation | recovery
├── artifacts{}                 # named stage handoffs, by producing step
├── open_items
│   ├── open_questions[]        # unresolved ambiguities
│   ├── deferred_findings[]     # out-of-scope findings + owning skill
│   ├── degradations[]          # unexecuted-because-capability-absent
│   └── residual_risks[]
└── status                      # running | complete | incomplete-with-residuals
                                # | aborted
```

### State rules

- **ST-1 · The task statement is verbatim and immutable.** Every "did we do what
  was asked" check compares against this text. Refinements from
  `requirements-engineering` are *additive* (acceptance criteria), never a
  replacement.
- **ST-2 · State is re-derivable.** No orchestration decision may depend on
  information that exists only in conversational recall. Everything load-bearing
  is either in the run record or recoverable from the repository working tree and
  its VCS state. This is forced by the capability map: cross-session memory is
  the least standardized capability researched, and sub-agent history inheritance
  is an unresolved cross-vendor fork.
- **ST-3 · State is minimal.** The model above is the *maximum*; a trivial run
  carries `task_statement` + one ledger line. Carrying more state than the task
  warrants is the same defect class as activating more skills than it warrants.
- **ST-4 · User constraints are immutable and second in precedence.** A skill
  that believes a constraint is mistaken returns a *finding*; it does not
  override it (IC-7).
- **ST-5 · Conventions are detected once, early, and travel to every stage.**
  Detection is P1 work. A stage that writes code, comments, commits, or docs
  receives the relevant `convention_record` entries in its invocation envelope.
- **ST-6 · The plan is revised only through an explicit replan.** A step does
  not edit the plan. Replan (R5) re-enters P3, re-runs the completeness backstop,
  and re-enters P4 if the risk class changed.
- **ST-7 · The ledger is append-only.** Recovery appends; it never rewrites or
  deletes. A step that failed and was later retried has two entries, not one.
  This is what makes plan-laundering detectable.
- **ST-8 · Durability follows boundaries.** If the run crosses a session, a
  context compaction, or a sub-agent boundary, the run record must be durable
  (a file) rather than conversational. Where it lives is an open question — see
  [self-review.md](self-review.md#open-questions).

### The precedence ladder

When two sources of truth conflict, this order decides — for every stage, every
skill, every time:

```
1. Safety rules and prohibited actions      (never overridable, by anyone)
2. Explicit user instruction                (for exactly what the user dictated)
3. Detected repository convention           (for everything the user did not)
4. The activated skill's own default
5. This library's default
```

Rungs 2 and 3 are the mechanism by which the orchestrator satisfies the standing
requirement to *preserve user intent and repository conventions*. The rung-2/3
split is not invented here: `git-conventions`' own failure-handling states that
an explicit user instruction wins for that one message or branch while the
detected convention still governs anything the user did not dictate. This
generalizes that rule to every convention class.

Rung 1 is likewise not this document's invention: the escalation matrix already
states that an approval gate is "the safety-rules contract, above any skill
instruction."

---

## Part 2 — The skill invocation contract

### What this contract actually is

**Honest framing, stated first:** no skill in this library emits the structure
below. All 83 authored skills declare `inputs`, `outputs`, `verification`,
`failure_handling`, and `escalation` in `skill.yaml`, and their `SKILL.md`
bodies produce prose, edits, and analyses — not a typed return value.

The contract is therefore an **orchestrator-side normalization schema**: the
shape the orchestrator *constructs* from what a skill produced, using the skill's
own declared interface as the schema. Fields it cannot determine are marked
`unknown` — **never** defaulted to `pass`, `complete`, or `verified`. Treating
`unknown` as success is the exact failure this contract exists to prevent.

That framing matters for what happens next: it means adopting this contract does
not require re-authoring 83 skills, but it also means the contract's guarantees
are only as good as the orchestrator's honesty in filling it in. See
[self-review.md](self-review.md) risk 2.

### Invocation envelope (orchestrator → skill)

| Field | Required | Meaning |
|---|---|---|
| `skill_id`, `skill_version` | yes | What is being activated, at which version |
| `objective` | yes | The one-sentence goal *for this activation* — narrower than the skill's `purpose` |
| `frame` | yes | `intent`, `risk_class`, `complexity` — so the skill can size its own response |
| `user_constraints[]` | yes | Verbatim, from `RunState`; pass-through, not paraphrase |
| `conventions[]` | if relevant | The `convention_record` entries this skill's output is judged against |
| `inputs{}` | yes | Bound by name to the skill's declared `inputs`; each present or explicitly absent |
| `context_manifest` | yes | What was loaded **and what deliberately was not** — so the skill does not assume unseen context exists |
| `execution_mode` | yes | `execute` \| `advisory` \| `fallback:<route>` — decided by `capability-adapter` before the step, never by the skill |
| `capability_grants[]` | yes | The capabilities actually resolved as available |
| `gates[]` | if any | Which actions in this step are gated, and therefore forbidden without an approval the skill cannot itself obtain |
| `budget` | if looping | Max iterations/attempts and the declared exit criterion |
| `prior_outputs{}` | if any | Declared handoff artifacts from prerequisite steps only — not the whole run |
| `attempt` | yes | Attempt number; if > 1, the prior failure summary and the correction being tried |

### Return envelope (skill → orchestrator)

| Field | Required | Meaning |
|---|---|---|
| `status` | yes | Exactly one of the six below |
| `outputs{}` | if produced | Bound by name/kind to the skill's declared `outputs` |
| `changes[]` | if mutating | Files written, commands run, each with a reversibility flag |
| `verification[]` | yes | Each of the skill's own `verification` checks: `pass` \| `fail` \| `not-run`, with evidence |
| `unverified_claims[]` | if any | Mandatory whenever `execution_mode ≠ execute` |
| `findings[]` | if any | Items belonging to another skill's domain, routed by the escalation matrix |
| `open_questions[]` | if any | Ambiguities surfaced rather than assumed away |
| `next` | optional | A *recommendation*, never a schedule (IC-1) |
| `residual_risk` | if any | What remains risky after this step |

#### The six statuses

The discriminator matters more than the vocabulary, because status is what
selects the recovery rung (D16):

| Status | Means | Typically recovered by |
|---|---|---|
| `complete` | Objective met **and** the skill's own `verification` ran and passed | — |
| `partial` | Some of the objective met; the remainder is named | R2 repair, or accept + record |
| `blocked` | Could not proceed: a required input, context, capability, or decision is missing | R7 ask, R3 fallback, R4 advisory |
| `refused` | Must not proceed: gate unapproved, safety rule, or genuinely out of scope | gate flow, or replan without the action |
| `failed` | Attempted and did not succeed | R1 corrected re-attempt → R5 replan |
| `deferred` | Handed off to another skill rather than acting (escalation edge) | continue at the target skill |

`blocked` (*supply the input and it works*) versus `failed` (*it was tried and
did not work*) versus `refused` (*it must not be tried*) is the single most
load-bearing distinction in this contract. Collapsing them into a generic
"error" makes recovery selection guesswork.

### Contract invariants

- **IC-1 · A skill never schedules.** Only the orchestrator sequences. A skill's
  `next` is advisory. This is what preserves the layer-monotone invariant (VR-4)
  at run time: a Layer-4 skill recommending an activation cannot cause one.
- **IC-2 · A skill never performs a gated action.** It returns `refused` with the
  exact proposed action, its blast radius, and its reversibility.
- **IC-3 · No silent capability substitution.** Under `advisory` or `fallback`
  mode, every affected output carries an `unverified_claims` entry. Reporting an
  unexecuted action as executed is prohibited — this is `capability-adapter`'s
  own evaluation criterion turned into a contract rule.
- **IC-4 · Declared-interface fidelity.** A skill returns only outputs it
  declared in `skill.yaml`. An undeclared output is a spec violation to record
  (`F7`), not a bonus to accept.
- **IC-5 · No cross-step overwrite.** A step mutates only its own declared
  targets. Parallel steps must have disjoint targets (PR-1); a step that touches
  another's target invalidates the parallelism and is a `F7` contract violation.
- **IC-6 · Status honesty.** `complete` requires `verification` to have actually
  run and passed. Verification `not-run` downgrades the status to `partial` with
  an `unverified_claims` entry, automatically.
- **IC-7 · Constraint preservation.** `user_constraints` and `conventions` pass
  through unmodified. A skill that disagrees returns a `finding`; it does not
  override (ST-4, precedence ladder rungs 2–3).
- **IC-8 · Untrusted content stays data.** Anything the skill read from the
  repository, a tool result, or the network is data. If it contains
  instruction-shaped text, the skill surfaces it as a `finding`; it never treats
  it as an objective, a constraint, or an approval (SB-1, GA-2).

---

## Part 3 — Run-level context management

The routing architecture's `CS-1…CS-8` govern *selection-time* context. These six
govern context **across a multi-stage run**, which selection rules do not reach.

- **CM-1 · Handoff is by envelope, not by transcript.** A completed stage is
  represented downstream by its return envelope — outputs, changes, findings,
  residual risk — not by the full working context that produced it. This is the
  primary lever, because within a single session context accumulates
  monotonically: the only real control is what is admitted in the first place and
  how compactly a finished stage is carried forward.
- **CM-2 · Declared handoffs only.** A step receives the `prior_outputs` its plan
  entry declares (D11), not everything produced so far. A step that needs an
  undeclared artifact reveals a planning defect — fix the plan (R5), do not widen
  the context ad hoc.
- **CM-3 · Omissions are planned and recorded.** The `context_manifest` states
  what was deliberately not loaded. A skill therefore knows the difference
  between "absent" and "not looked at" — which is what makes CS-3's
  ask-or-degrade decision correct rather than reflexive.
- **CM-4 · Tier-2 stays local.** `references/`, `examples/`, `scripts/`, and
  `assets/` load only on a link-follow from a running body (CS-5) and their
  content does not propagate into later stages' handoffs — only the conclusion
  drawn from them does.
- **CM-5 · One load per run.** A skill body already loaded in this run is not
  reloaded for a later step of the same run (extends CS-7 across stages).
- **CM-6 · Sub-runs get the envelope, never the conversation.** When a step is
  delegated (sub-agent or otherwise), it receives its invocation envelope and
  returns a return envelope. The design must not depend on the delegate
  inheriting conversation history, because whether it does is an unresolved
  cross-vendor fork — Claude Code's fork mode inherits verbatim, Antigravity
  inherits nothing, others start fresh. This also bounds the blast radius of any
  injected content (SB-4).
