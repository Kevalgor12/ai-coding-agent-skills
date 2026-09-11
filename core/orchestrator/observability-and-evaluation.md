# Orchestrator Observability & Evaluation Hooks

Status: **design only**. Two distinct concerns that are easy to conflate:

1. **Orchestrator observability** — what the orchestrator records about **its own
   decisions**, so a run can be audited after the fact.
2. **Evaluation hooks** — where the orchestrator touches each activated skill's
   `evaluation_criteria` field, and — honestly — how little that can mean until
   the evaluation suite exists.

## What this is *not*

This is **not** application observability. Logging, metrics, tracing, error
monitoring, signal selection, cardinality discipline, PII scrubbing, and alert
design are owned by `observability` (`SK-QA-004`) and its four technology
specializations, and are referenced here rather than restated (QR-2 —
`SK-QA-004` declares those topics in `owned_knowledge`).

The distinction in one line: `SK-QA-004` makes **the user's system** diagnosable
in production; this document makes **the run** reviewable afterwards. They share
one rule only — do not put secrets or PII in the record (SB-7) — and that rule is
`SK-QA-004`'s, cited not copied.

---

## Part 1 — The run record

### What it contains

The record is the `ledger` from
[state-and-contract.md](state-and-contract.md#structure): append-only, one entry
per orchestration event.

| Entry type | Records |
|---|---|
| `decision` | Decision point ID (D1…D19), the inputs considered, the outcome, **and the rule ID applied** (SR-3, CS-5, PR-1, ER-2, VR-4, GA-1, …) |
| `selection` | The selected set and the excluded set with reasons (SR-11), plus any completeness-backstop addition and the stage it staffed |
| `invocation` | Skill ID and version, objective, `execution_mode`, and the returned status |
| `mutation` | Files written, commands run, each with a reversibility flag |
| `gate` | Gate class, the exact action proposed, the user's response **verbatim**, and the timestamp |
| `degradation` | The capability decision, the fallback route taken, and what consequently went unverified |
| `recovery` | Failure class (F1–F9), the rung chosen (R1–R8), and the outcome |
| `evaluation` | The observations described in Part 2 |

### Rules

- **OB-1 · Record decisions, not narration.** The record exists to answer "why did
  it activate that skill / skip that step / run that command", not to replay the
  agent's monologue.
- **OB-2 · Every step produces exactly one invocation entry and one outcome.** A
  re-attempt produces a second pair, never an edit to the first (ST-7).
- **OB-3 · Every decision names its rule.** A decision entry with no rule ID is an
  unaudited judgement call and is marked as such. This is the cheapest available
  proxy for "was this run governed or improvised", and it is what makes an audit
  possible without re-running the task.
- **OB-4 · Exclusions are as recorded as inclusions.** The minimum-set claim
  (SR-11) is only auditable if the complement is written down; this extends that
  discipline from routing to the whole run.
- **OB-5 · No secrets, no PII, no bulk file contents.** Refer to locations, not
  values (SB-7). Scrubbing method is `SK-QA-004`'s.
- **OB-6 · Durability follows boundaries.** In-conversation is sufficient for a
  single-session run. If the run crosses a session, a compaction, or a sub-agent
  boundary, the record must be durable — because state must be re-derivable
  (ST-2, ST-8) and conversational recall is not portable across hosts.
- **OB-7 · The record is proportional.** A trivial task's record is one line:
  the skill selected and why. Emitting a structured ledger for a one-line comment
  fails the same proportionality principle as over-activation does.

### What the user sees

The record is for auditability; it is not a progress narration. By default the
user sees:

- the plan and its gates, **up front** (ER-1) — and only when the plan warranted
  admission at all (D13);
- each gate request, when it arrives;
- the final report at P7.

Everything else stays in the record unless asked for. A user who wants the
reasoning can ask for it; a user who did not ask should not have to read it.

---

## Part 2 — Evaluation hooks

### The honest scope

Every `skill.yaml` in this library carries an `evaluation_criteria` list (a
required field, ≥ 1 testable criterion). What does **not** exist:

- any test harness, fixture set, scoring rubric, threshold, or recorded result —
  [`evaluations/`](../../evaluations/) holds a placeholder README and no
  evaluation content;
- any executable mechanical validator — `core/` holds design documents only;
- any skill promoted to `final/` — the specification's conformance lifecycle
  requires a passing validator, a passing evaluation, and an audit before
  promotion, and **no skill in the library has met that bar**.

Building that suite is separate, later work. What this document contributes is
the set of **hooks** — where the orchestrator would touch evaluation, what it can
honestly do today at each, and what shape the data must take so the future suite
can consume it.

### The hooks

| Hook | Where | What it does today | What it needs |
|---|---|---|---|
| **EH-1** · Pre-activation eligibility | P2, before relying on a skill | **Inert.** No eval results exist, so the orchestrator cannot prefer a proven skill over an unproven one. Consequence today: **treat every skill as unproven** and never present its output as validated-by-evaluation | An eval result registry + promotion state per skill |
| **EH-2** · Post-invocation self-check | P5, at step close | **Active.** Run the skill's own `verification` list against what it returned; a `not-run` check downgrades `complete` to `partial` (IC-6). This is the runtime use of an already-populated field | — |
| **EH-3** · Criteria observation | P5, at step close | **Active, but observation only.** Record, per activated skill, whether each `evaluation_criteria` item was *observable* in this run and, if so, whether it appeared satisfied | A rubric, to turn observations into scores |
| **EH-4** · Fixture export | P7 | **Active.** Shape the record so each `(skill, invocation envelope, return envelope, observed criteria)` tuple is extractable as a candidate eval fixture | A fixture format and a harness to run them |
| **EH-5** · Routing-quality signals | P2 and P5 | **Active.** Record the two measurable routing errors: a **false activation** (a skill activated and immediately returned `deferred`/out-of-scope) and a **missed activation** (the completeness backstop had to add a skill, or evidence pulled one in mid-run). Also record `F7` contract violations | A baseline to compare against |

### EH-3 in particular: observation is not evaluation

A single production run is **not** an evaluation. It has no controlled fixture,
no expected output, no repetition, and no variance analysis. Recording that a
criterion "appeared satisfied" is a data point for a future suite — it is not
evidence that the skill passes.

The orchestrator must therefore never state, imply, or let a report suggest that
a skill "passed its evaluation criteria" on the basis of a run. The permissible
statement is the narrow one: *this run produced output consistent with criterion
N*. This distinction is the same one `SK-AI-007` (llm-evaluation) draws for
LLM output generally, and it applies with full force to the library evaluating
itself.

### Why EH-5 is worth the cost even now

The specification's own context-efficiency rule CE-5 makes false-activation rate
the measure of activation precision, and the routing architecture's central claim
is that it produces the *minimum correct* set. Both are currently unmeasured
assertions. False and missed activations are cheap to record at run time and are
exactly the data that would let a future evaluation pass test the claim rather
than restate it. Recording them now costs almost nothing and is the difference
between a suite that can be built later and one that has to start from zero.
