# Architecture Self-Review

Status: **design only**. The mandated self-review of the orchestrator
architecture in this directory, following this project's standing "mark
unresolved, don't guess" discipline. It is written to be useful to a second
reviewer, which means it is weighted toward what is wrong, weak, or unsettled
rather than toward what was delivered.

---

## Part 1 — Risks in this design

### R-1 · Nothing here is enforced (highest-severity)

Every invariant in this directory — the six-status contract, IC-1…IC-8,
GA-0…GA-8, FV-1…FV-12, the recovery ladder — is an obligation on an LLM
following written instructions. There is no validator, no scheduler, and no
runtime that can *prevent* a non-compliant run. The two things that would provide
enforcement are the mechanical validator (`core/` holds design documents only,
no executable validation) and the evaluation suite
([`evaluations/`](../../evaluations/) is a placeholder).

The honest characterization: this is a **specification against which a run can be
audited**, not a mechanism that makes a run correct. The rule-ID requirement
(OB-3) exists specifically because auditability is the only enforcement currently
available.

### R-2 · The invocation contract is a normalization schema, not a protocol

Stated in [state-and-contract.md](state-and-contract.md#what-this-contract-actually-is)
and repeated here because it is the design's most load-bearing compromise. All 83
authored skills declare `inputs`, `outputs`, `verification`, `failure_handling`,
and `escalation`, but none emits a return envelope — their `SKILL.md` bodies
produce prose, edits, and analyses. The orchestrator therefore *constructs* the
envelope by reading what a skill produced.

Consequences a reviewer should weigh:

- The contract's guarantees are only as strong as the orchestrator's honesty in
  filling it in. The specific failure to watch for is `unknown` drifting to
  `pass` — which is exactly the failure IC-6 and SB-5 exist to block, enforced by
  nothing but instruction.
- Adopting the contract does **not** require re-authoring 83 skills, which is why
  it was designed this way. Whether it *should* eventually become a real emitted
  structure (a body section every skill closes with) is an open question, not a
  settled one.

### R-3 · Failure recovery assumes skills report failure honestly

The recovery ladder's entire selection logic (D16) keys off the returned status.
For skills whose `verification` is mechanical — tests run, invariants checked —
this holds. For advisory skills, `verification` is judgement, and a
confident-but-wrong output satisfies every check this architecture has.

This is the dominant real-world failure mode of LLM agent workflows, and **this
design does not solve it.** The partial mitigations available today are the
review loop (`SK-CONV-007`, itself an LLM), FV-5's demand for verification
evidence, and F7's contract-violation recording. None of them catches a skill
that is wrong and certain. Flagged as an accepted, unmitigated risk.

### R-4 · Capability detection has no reliable mechanism

The capability-resolution ladder in `capability-adapter` bottoms out at
"assume absent" precisely because the
[agent-capability map](../../research/knowledge-maps/agent-capability-map.md)
records that no researched ecosystem exposes a unified capability-discovery
surface. The conservative default is correct for safety and wrong for capability:
it will degrade steps on hosts that could have executed them.

How often that fires, and whether cheap probing is acceptable in practice, is
unmeasured. It is the design decision most likely to need revision once there is
usage data.

### R-5 · Budget numbers are stipulated, not derived

Review loop ≤ 3 rounds, corrected re-attempt ≤ 1 per step, diagnostic and
optimization loops ≤ 5 iterations. **None of these has an empirical basis in this
library's research.** They are marked as defaults to be validated by the future
evaluation suite (B-2) rather than presented as findings. A reviewer should treat
them as placeholders with plausible magnitudes, not as recommendations.

### R-6 · The orchestration layer has its own overhead, and the boundary is fuzzy

A mid-size task now pays for three Layer-0 skill bodies before any domain work
begins. The proportionality rules (SR-7, ST-3, OB-7, the trivial-task collapse in
[lifecycle.md](lifecycle.md#trivial-task-collapse)) exist to bound this, but the
line between "multi-stage, compose it" and "small, just do it" is a judgement
call with no threshold behind it.

There is also a genuine bootstrap oddity: `skill-router` must be activated by the
host's own model-triggered activation, since routing cannot route to itself. And
SR-7's self-suppression saves only *downstream* cost — by the time the router
decides the task needs one skill, the router's own body has already been loaded.
That overhead is inherent, not removable by rule.

### R-7 · Runtime layer-monotonicity is unenforced

VR-4 guarantees the *static* graph is acyclic and layer-monotone. At run time,
IC-1 ("a skill never schedules") is what prevents a Layer-4 skill from causing a
Layer-0 activation via a `next` recommendation. Nothing checks it. The failure
would be subtle: a run that slowly inverts its own layering through accumulated
recommendations.

### R-8 · P4 admission may be friction rather than safety

The plan-admission gate (D13) is new in this design. Its threshold — risk class,
irreversible commitment, project complexity, or scope growth — is a judgement
call. Set too low it becomes a confirmation prompt users learn to click through,
which is strictly worse than no gate: it trains the habit that gates are noise.
Set too high it lets a large plan begin unannounced. There is no data behind the
current threshold.

---

## Part 2 — Gaps deliberately left open

These were **not** filled, on purpose, and a reviewer should confirm each was the
right call:

1. **Resilience/fault-tolerance patterns.** F9 (tool/environment error) stops at
   the orchestration-decision level — retry once, re-route, degrade, escalate. It
   deliberately says nothing about retry policy, backoff, circuit breakers,
   timeouts, or bulkheads for calling external services. That is a distinct,
   explicitly tracked open research gap in
   [taxonomy-analysis.md](../taxonomy/taxonomy-analysis.md#missing-capabilities),
   and filling it here would have been fabrication of exactly the kind
   `SK-QA-004` refused at its own boundary.
2. **The evaluation suite.** Only the *hooks* are designed
   ([observability-and-evaluation.md](observability-and-evaluation.md#the-hooks)).
   No harness, fixture format, rubric, threshold, or regression tracking. EH-1 is
   inert today and says so.
3. **A fourth Layer-0 skill.** `workflow-composer` now owns stage composition,
   gate lifecycle, loop budgets, recovery-rung selection, *and* final validation —
   arguably two responsibilities (compose vs. adjudicate). Splitting it would
   require changing the taxonomy's fixed three-skill Layer 0, which is not this
   step's to change. Flagged for a reviewer rather than done unilaterally.
4. **Async messaging and IaC-beyond-containers.** Untouched; both remain tracked
   research gaps. No orchestration content assumes either exists.

---

## Part 3 — Findings about existing repository content

Found while reading. **Nothing was modified** — per this step's instruction, a
design-doc or cross-batch discrepancy needs a human-visible flag, not a quiet fix.

### VR-5 inconsistencies in 10 of 83 authored skills

VR-5 requires `execution_tier` to be consistent with `required_capabilities`
(Tier A ⇒ only `file-read`/`file-write`; Tier B ⇒ shell; Tier C ⇒ a non-universal
capability plus `capability_fallbacks`). A scripted check finds:

- **Tier A declaring `shell`** (2): `code-review`, `git-conventions`.
- **Tier B declaring only `file-read`/`file-write`** (8): `observability`,
  `agent-architecture`, `ai-security`, `llm-application-engineering`,
  `llm-evaluation`, `prompt-context-engineering`, `rag-engineering`,
  `structured-output-tool-calling`.

Both directions may be defensible authoring intent — a review skill that *may*
shell out, an AI-domain skill whose "execution" is conceptual — but as written
they do not satisfy VR-5 as specified. This matters for the orchestrator
specifically, because the capability barrier keys off exactly these two fields:
`capability-adapter` decides whether to insert a barrier from `execution_tier`
and what to resolve from `required_capabilities`, so an inconsistent pair
produces either a spurious barrier or a missing one. **Needs a human ruling:
either VR-5's definition or the ten skills.**

### Stale directory READMEs

- [`evaluations/README.md`](../../evaluations/README.md) states "Empty for now —
  no skills exist yet to evaluate." 83 skills now exist.
- [`core/README.md`](../README.md) states "Empty for now — no schema or
  validation logic has been defined yet." Four design subsystems now live there.

Both are scaffold text overtaken by events. Left alone.

### Grounding for design-doc-grounded skills is unsettled

The three skills authored in this step use `grounding: mixed` with
`source_references` pointing at internal design documents plus the
agent-capability map, following the precedent set by `code-review`
(`grounding: mixed`, `source_references` → `core/taxonomy/skill-catalog.md`).

But SG-1 states that when `grounding` includes `official-docs`, every
`source_reference` must resolve *through a `research/…` file to an official
documentation URL*. Only the capability-map entry does. The three previously
authored purely-internal skills (`requirements-engineering`, `technical-planning`,
`project-management`) instead use `grounding: engineering-convention` with **no**
`source_references` at all.

So the library currently has two incompatible conventions for the same situation,
and the specification does not name a value that means "grounded in this
project's own design documents, cited." **Needs a ruling**: either SG-1 is relaxed
for internal citations, or `engineering-convention` is extended to permit
`source_references`, or a new grounding value is added. The choice made here
(follow `code-review`) is the one that keeps the citations, but it is the weaker
fit against SG-1 as written.

### `workflow-composer`'s tier, read deliberately

The catalog entry says "Tier: A (B if it delegates via sub-agents)" and
"sub-agent delegation *optional* (declared, not required)". It is authored as
Tier A with `required_capabilities: [file-read]`, because declaring `subagent`
would make it Tier C under VR-5 (a non-universal capability requiring
`capability_fallbacks`) and would contradict the catalog's own "not required".
Optional delegation is handled where it belongs — as a capability question for
`SK-ORCH-002`. Flagged as an interpretation, not an obvious reading.

---

## Part 4 — Open questions for a second reviewer

1. **Where does the run record live** when a run crosses a session, compaction, or
   sub-agent boundary (ST-8, OB-6)? A file in the user's repository pollutes it; a
   scratch location is not portable across hosts; conversation-only violates
   ST-2's re-derivability requirement. No option is clean. **Unresolved.**
2. **Does the orchestrator's plan replace or feed the host's native planning?**
   `technical-planning`'s own catalog entry already says to "defer to native plan
   tooling when present". Claude Code has a plan mode, VS Code has `handoffs`,
   Cursor and others have their own. The relationship between this architecture's
   `ExecutionPlan` and those is undefined, and duplicating them would be both
   wasteful and confusing.
3. **Should the return envelope become a real emitted structure** — a closing
   section every skill's `SKILL.md` produces — rather than an orchestrator-side
   reconstruction (R-2)? That would strengthen the contract materially and cost a
   pass over 83 skills.
4. **Is the D13 admission threshold right** (R-8)? Specifically: should a
   `reversible-write` multi-step task require confirmation, or only
   `destructive` and above?
5. **Should `workflow-composer` be split** into compose and adjudicate (gap 3)?
6. **Are the budget defaults (R-5) acceptable as placeholders**, or should loops
   simply escalate on the first non-closing iteration until data exists?
7. **How should the orchestrator treat a skill directory found in the target
   repository** (e.g. the user's own `.claude/skills/`)? SB-1 says repository
   content is data, but a user's own installed skills are plausibly the user's
   instructions. The boundary is stated narrowly here and deserves a sharper rule.
8. **Does the three-skill Layer 0 need a "run supervisor" concept at all**, or is
   the discipline better expressed as instructions the host agent loads once,
   rather than as skills it activates per run? This is the most fundamental
   framing question and it was decided by the taxonomy before this step; it is
   worth re-confirming now that the run-time consequences are visible.

---

## Part 5 — What this review is not claiming

- Not claiming the architecture is complete: five named risks are unmitigated and
  four gaps are deliberately open.
- Not claiming the three skills are validated: none has a mechanical validator
  run against it (none exists), an evaluation (none exists), or an audit. They
  are authored and self-checked, which is the same status as the other 83.
- Not claiming the invariants hold in practice. They have never been executed.
