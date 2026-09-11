# Real-World Evaluation — Performance regression after a known deploy

**Step 32 · Task 1 of 3 · Domain: Performance · Adversarial pattern: performance regressions**

Date: 2026-09-11. Method per [`evaluations/regression-suite.md`](../../evaluations/regression-suite.md)
"How to run a scenario today": the task was worked through as the orchestrator
specified in [`core/orchestrator/`](../../core/orchestrator/), routing against the
actual `skill.yaml`/`SKILL.md` files in [`skills/`](../../skills/), and only then
evaluated. Severity vocabulary is this project's audit convention
(Critical / High / Medium / Low), not the eval suite's `critical`/`major`/`minor`
assertion weights.

> **Note on proposed scenario IDs.** Other Step-32 real-world evaluations were
> written into this directory in parallel and independently propose scenarios
> numbered from `S17`. The proposed scenario below should be identified by its
> **slug** — `dashboard-regression-after-known-deploy` — and assigned its numeric
> ID when it is actually authored into
> [`evaluations/scenarios/`](../../evaluations/scenarios/), after de-duplicating
> against every sibling file in this directory.

## The task

> "Our admin dashboard used to load in under a second; after last week's deploy
> it now takes 6 seconds. Fix it."

**Repository context.** `git log` shows a recent commit adding an "audit trail"
feature that logs every admin action. The deploy coincides with the regression.
No profiling data exists yet.

**What makes this adversarial.** The request is *not* a generic slow-page
complaint. It carries three high-value facts a senior engineer would act on
immediately: a known-good baseline (<1s), a measured current value (6s), and a
time boundary with a single identifiable change behind it. The question this
evaluation answers is whether the library's guidance uses that structure, or
flattens it into "a performance complaint."

---

## What actually happens — the traced run

### P0 · Intake ([lifecycle.md:57-90](../../core/orchestrator/lifecycle.md))

- **ST-1.** Task statement recorded verbatim.
- **User constraints (ST-4).** None stated. "Fix it" implies a mutation is
  wanted, not diagnosis alone.
- **Bounded signal scan** (routing Phase 0,
  [routing-algorithm.md:13-19](../../core/routing-architecture/routing-algorithm.md)).
  The enumerated categories are dependency manifests, config files, connection
  strings / driver imports, file types present, and — line 18 — "existing
  conventions (`git log`, commitlint config)". **`git log` is read here, and only
  for commit-message style.** Nothing in Phase 0, in CS-6
  ([rules.md:64-65](../../core/routing-architecture/rules.md)), or in the
  orchestrator's P0/P1 instructs the scan to read *what changed* across a stated
  time boundary. See **P-2**.
- **Classification (routing Phase 1).** Intent = `optimize`. Task type =
  performance-optimization (workflow pattern #7,
  [workflows.md:120-133](../../core/dependency-architecture/workflows.md)).
  Complexity = small→multi-step. Risk = read-only → reversible-write (a code
  edit); `production` only if the run is also asked to deploy, which it is not.
- **S-Gate 1 · security intake screen**
  ([security-and-validation.md:64](../../core/orchestrator/security-and-validation.md)).
  "Does the task carry a trust boundary, secret, untrusted input, auth surface,
  or LLM-with-tool-access dimension?" An *admin* dashboard whose regression is
  caused by an *audit trail of admin actions* is a privileged surface carrying a
  compliance-shaped control. A literal reading of SR-5's trigger list
  ("trust boundary/secret/untrusted input",
  [rules.md:25-28](../../core/routing-architecture/rules.md)) does not name it.
  See **P-5**.
- **D2 · is intent genuinely ambiguous?** No — correctly. The request is
  well-specified. `requirements-engineering` is correctly excluded on its own
  `non_activation_conditions`
  ([requirements-engineering/skill.yaml:33](../../skills/requirements-engineering/skill.yaml)):
  "The requirements are already explicit, unambiguous, and narrowly scoped."
  **This is correct behavior and the library gets it right.**

### P1 · Discovery

- Domains: backend + data (a server-rendered or API-backed admin view), possibly
  frontend. Technologies: only those actually detected (SR-3,
  [rules.md:16-19](../../core/routing-architecture/rules.md)) — the scenario
  supplies no manifest, so the technology set stays minimal and every Layer-4
  skill for an undetected stack is correctly excluded.
- Conflict clusters: none forced.
- **D6 · is a candidate skill authored?**
  ([lifecycle.md:115-117](../../core/orchestrator/lifecycle.md)) The intent shape
  here is genuinely *debug-then-optimize* — the same shape
  [examples.md:152-172](../../core/routing-architecture/examples.md) uses for
  Example 5. Workflow #4 (debugging) and workflow #3 (bug fixing) have no
  authored skill. This is already established as **X-01**
  ([cross-skill-audit.md:107](../cross-skill/cross-skill-audit.md)) and **R-02**
  ([routing-audit.md:85](../cross-skill/routing-audit.md)); it is not re-derived
  here, but it has a *specific consequence on this task* that neither finding
  named — see **P-4**.

### P2 · Routing — the selected set

Applying default-deny selection (SR-1) with the cross-cutting conditionals
(SR-5), conventions (SR-6), discovery proportionality (SR-8), and the Tier-B
barrier (PR-3):

```
capability-adapter            (barrier — performance-engineering is execution_tier: B,
                               required_capabilities: [file-read, file-write, shell])
  → performance-engineering   (SR-5: a performance problem is in play;
                               skill.yaml:35 "A performance problem or budget is in play")
  ∥ [cond] database-operations (activates only if the symptom localizes to query
                               performance — skill.yaml:29-33; late-bound per D14)
  → [fix]
  → testing-strategy          (SR-5: runnable code is produced)
  → code-review ⤾             (performance facet only, ER-6)
  → git-conventions           (attaches only at the commit, SR-6)
```

**Correctly excluded** (spot-checked against the classes SR-11 requires be
recorded): all frontend/UI/styling/a11y skills, SEO and monetization, all
realtime transports, all AI/LLM skills, `technical-documentation`,
`legacy-modernization`, `refactoring`, `data-migration`, every Layer-4
technology skill for an undetected technology, and all three discovery skills
(SR-8 — this is a bounded fix, not a project). `observability` is a defensible
either-way call: its activation includes "Debugging a production issue that needs
logging/metrics/tracing evidence"
([observability/skill.yaml:34](../../skills/observability/skill.yaml)), and the
`observability` ⟷ `performance-engineering` overlap is already tracked as
**R-03b** ([routing-audit.md:148](../cross-skill/routing-audit.md)).

**Routing verdict: the selected set is right.** The defects on this task are not
in *which* skills activate — they are in what the activated skills then tell the
agent to do, and in a signal that never reaches routing at all.

### P5 · Execution — what `performance-engineering` actually instructs

This is the heart of the evaluation. Reading the skill's own content:

| Where | What it says |
|---|---|
| [SKILL.md:133-136](../../skills/performance-engineering/SKILL.md) | Decision framework **step 1**: "Is there actual profiling/benchmark evidence, or is this a guess? **Measure before proposing a change**" |
| [SKILL.md:137-141](../../skills/performance-engineering/SKILL.md) | Step 2: "Does the symptom match a known cross-stack pattern (a dev-mode default left on, connection-pool exhaustion, real-time backpressure, an N+1 pattern)? **Check these first — they're cheap** to rule in or out" |
| [SKILL.md:142-149](../../skills/performance-engineering/SKILL.md) | Steps 3–4: dominance check; lever selection (caching vs. tuning vs. scaling) |
| [SKILL.md:157-158](../../skills/performance-engineering/SKILL.md) | Workflow **step 1**: "Gather profiling/benchmark evidence for the actual symptom." |
| [SKILL.md:171-172](../../skills/performance-engineering/SKILL.md) | Engineering rule: "Measure before optimizing; **never** propose a change without evidence it addresses the actual bottleneck." |
| [skill.yaml:77](../../skills/performance-engineering/skill.yaml) | `failure_handling`: "If no profiling/benchmark evidence is available, **gather it before proposing a change** rather than guessing at the bottleneck." |
| [skill.yaml:81](../../skills/performance-engineering/skill.yaml) | `verification`: "The identified dominant cost is backed by evidence (a profile, a benchmark, **a measured symptom**), not a guess." |

Across all five decision-framework steps, the five workflow steps, the five
engineering rules, the three `failure_handling` branches, the three
`verification` items and the three `evaluation_criteria`, **not one asks what
changed.** The word "regression" does not appear in the skill at all. Verified
across the whole library: `git bisect` appears in no skill file; "regression"
appears only in testing senses (visual regression, regression test, regression
gate); no skill's activation conditions, decision framework, or workflow
references a recent diff, a deploy boundary, or change attribution.

So the composed guidance is: *no profiling data exists → go get profiling data.*
Since `performance-engineering` is Tier B and the capability-adapter barrier may
well resolve to `advisory` (no shell against a production admin dashboard under
realistic load), the most likely terminal state is R4 degrade-to-advisory
([failure-recovery-and-escalation.md:66](../../core/orchestrator/failure-recovery-and-escalation.md)):
a correct, well-written explanation of *how to profile*, delivered instead of the
fix, while a 30-second `git show` of the audit-trail commit would very likely
reveal a synchronous write-per-admin-action on the request path.

**Two partial mitigations, stated fairly:**

1. `verification` ([skill.yaml:81](../../skills/performance-engineering/skill.yaml))
   admits "a measured symptom" as evidence. The user *gave* one (1s → 6s). So the
   skill does not strictly require a profiler run before acting, and a careful
   agent can proceed. This is a real design strength.
2. Decision-framework step 2 has exactly the right *shape* — a cheap, high-yield
   check performed before deep diagnosis. Its catalogue happens to include
   "an N+1 pattern," and an audit-trail-per-admin-action feature is plausibly
   N+1-shaped. An agent may therefore land on the right answer. But it lands
   there by pattern-matching a fixed list, not by attributing the regression to
   the change — and if the audit trail's cost is a synchronous HTTP call to a log
   sink, a serialized JSON blob per row, or an unindexed insert, none of the four
   listed patterns matches and the heuristic yields nothing.

There is also an unresolved internal tension. Engineering rule 1 forbids
proposing any change "without evidence it addresses the actual bottleneck";
step 2 instructs checking four specific hypotheses *before* such evidence exists.
The skill does not state how the absolutism and the heuristic reconcile, which is
precisely the ambiguity that decides whether an agent feels licensed to look at
the diff first.

---

## Findings

### P-1 · No skill treats "regression correlated with an identifiable change" as a diagnostic signal — **High**

**Finding.** `performance-engineering` routes every performance complaint
through the same measure-first funnel regardless of whether a specific causal
change is already suspected. Its decision framework
([SKILL.md:133-153](../../skills/performance-engineering/SKILL.md)), workflow
([SKILL.md:157-167](../../skills/performance-engineering/SKILL.md)), engineering
rules ([SKILL.md:171-181](../../skills/performance-engineering/SKILL.md)),
`failure_handling` and `verification`
([skill.yaml:76-83](../../skills/performance-engineering/skill.yaml)) contain no
change-attribution step. Library-wide, no skill mentions bisection, a deploy
boundary, or reading the recent diff as a diagnostic move.

**Root cause.** The skill was authored from
[`research/knowledge-maps/performance-knowledge-map.md`](../../research/knowledge-maps/performance-knowledge-map.md),
whose §16/§17 synthesis is organized by *technology-specific profiling tooling*
and *cross-stack symptom patterns*. Change attribution is a VCS-and-process
discipline, not a technology fact, so it had no source to enter through. The
knowledge map's own §18 ("What this data does not cover") is reproduced in the
skill ([SKILL.md:118-130](../../skills/performance-engineering/SKILL.md)) and
lists CDN vendors, message queues, load balancers and Node runtime internals —
it does not list change attribution, so the gap is not even declared as a gap.

**Recommended correction.** Insert a step into the decision framework, ahead of
the profiling step, and mirror it in the workflow and `verification`:

> **0. Is this a *regression* — was there a known-good state, and is there an
> identifiable change between then and now?** If yes, the cheapest and
> highest-signal evidence is the diff across that boundary (the deploy, the
> release tag, the merge). Read it before reaching for a profiler. A change
> correlated in time with the onset is evidence, not a guess — it is the
> narrowest hypothesis available, and confirming or eliminating it costs
> minutes. Profile when there is no such boundary, or when the diff does not
> explain the magnitude.

Add a matching `verification` item ("where a regression boundary exists, the
change across it was inspected before generic profiling was proposed") and add
`regression-boundary` to `inputs` (see **P-3**). This does not weaken
measure-before-optimizing: the diff *is* the measurement of what changed, and the
magnitude still has to be confirmed against the 1s→6s symptom.

**Regression test requirement.** **New scenario required.** Checked
[`evaluations/scenarios/`](../../evaluations/scenarios/): the two
performance-sensitive scenarios are S03 ("app feels slow" — no cause, no
baseline, no boundary; tests whether the run refuses to guess) and S09 (N+1
already measured and profiled; tests what to do with a measurement in hand).
**Neither covers the middle case: a baseline, a symptom, and a time-correlated
change, with no profile.** Propose `S17 — dashboard regression after a known
deploy`, category *performance-sensitive*, with a `critical` assertion that the
run inspects the change across the stated boundary before proposing generic
profiling, and a `major` assertion that it does not report `complete` on an
advisory "here is how to profile" when a cheaper decisive check was available.

---

### P-2 · The bounded signal scan cannot see the change that caused the regression — **High**

**Finding.** Phase 0's signal categories
([routing-algorithm.md:13-19](../../core/routing-architecture/routing-algorithm.md))
are manifests, config files, connection strings/driver imports, file types, and
"existing conventions (`git log`, commitlint config)". The one place VCS history
is read, it is read for commit-message *style*. CS-6
([rules.md:64-65](../../core/routing-architecture/rules.md)) reinforces the
bound: "the repo scan reads manifests/config/entrypoints, not the whole tree;
it's for detection, not comprehension." Consequently the single most load-bearing
repository fact in this scenario — that a commit adding an audit trail landed
last week — is **not in the signal set the router routes on**, and therefore
cannot influence routing even in principle.

This is architecturally more serious than P-1: P-1 is a skill-content gap that a
skill edit fixes; P-2 means the orchestrator's own intake is structurally blind
to change history whenever a request names a temporal boundary.

**Root cause.** The signal taxonomy was designed for *stack detection* — "which
technologies are present" — because that is what SR-3 needs. Detection of
*change* is a different question that the taxonomy was never extended to cover,
and CS-8's preference for cheap deterministic signals
([rules.md:67-69](../../core/routing-architecture/rules.md)) would actually
*favour* it: `git log --since` and `git show` are as deterministic and as cheap as
reading `package.json`.

**Recommended correction.** Add a conditional sixth signal category to Phase 0
and to lifecycle P0 step 3: *when the request names a temporal boundary or a
state change ("after the deploy", "since Friday", "it used to", "it worked
before", "since we upgraded"), read the bounded change set across that boundary
(`git log --oneline --since`, and `git show --stat` on the candidates) as part of
the scan.* Keep it bounded exactly as the other categories are — commit subjects
and changed-file statistics, not full diffs; the full diff loads at P5 if the
selected skill asks for it (CS-5 discipline). Record the boundary in
`RunState.task_frame.signals` so downstream stages can bind it.

**Regression test requirement.** Covered by the same proposed `S17` — its
"Repository signals" section should state the git log explicitly and the
expected-behaviors file should carry a `critical` assertion that the routing
record's `signals` includes the recent-change set. No existing scenario asserts
anything about VCS history as a signal (S02 uses `git log` only for commit
convention detection, which is exactly the narrow use P-2 is about).

---

### P-3 · The regression context has no declared input slot to bind to — **Medium**

**Finding.** `performance-engineering`'s declared `inputs`
([skill.yaml:44-50](../../skills/performance-engineering/skill.yaml)) are
`perf-symptom-or-target` (required) and `profiling-data` (optional). The
invocation envelope specifies `inputs{}` as "Bound by name to the skill's
declared `inputs`; each present or explicitly absent"
([state-and-contract.md:148](../../core/orchestrator/state-and-contract.md)),
and CM-2 states "A step receives the `prior_outputs` its plan entry declares, not
everything produced so far… do not widen the context ad hoc"
([state-and-contract.md:234-237](../../core/orchestrator/state-and-contract.md)).
The fact "an audit-trail commit landed last week" has no name to bind to. An
orchestrator following CM-2 strictly has no sanctioned way to hand it over; one
that hands it over anyway is widening context ad hoc.

Relatedly, `activation_conditions[1]`
([skill.yaml:35-36](../../skills/performance-engineering/skill.yaml)) reads "A
diagnostic (profiling, benchmarking) is needed before optimizing" — the
activation condition itself presumes the diagnostic *modality*, foreclosing
change attribution before the skill body is ever loaded. Because the router works
on Tier-0 only (CS-1), this framing is doing real work at selection time.

**Root cause.** `inputs` were derived from the skill's own workflow, which is
profiling-centric (P-1's root cause), so the interface inherited the same blind
spot. This is the same *class* as **X-04** (a thing that exists only in the body
being invisible to the layer that needs it,
[cross-skill-audit.md:463](../cross-skill/cross-skill-audit.md)), arriving
through the `inputs` field rather than the `escalation` field.

**Recommended correction.** Add to `inputs`:

```yaml
  - name: regression-boundary
    description: >-
      If the symptom is a regression, the known-good state and the change set
      between it and now (deploy, release tag, merge, upgrade).
    required: false
```

and generalise `activation_conditions[1]` to "A diagnostic is needed before
optimizing (profiling, benchmarking, **or attributing a regression to a
change**)".

**Regression test requirement.** Folded into `S17`; assert as `major` that the
invocation envelope for `performance-engineering` carries the regression boundary
as a bound input rather than as unstructured prose.

---

### P-4 · The missing debugging skill has a specific, un-named consequence here — **Medium**

**Finding.** This builds on **X-01** / **R-02** (no skill owns debugging or
bug-fixing) rather than re-deriving them. The consequence those findings did not
name: workflow #7 (performance optimization,
[workflows.md:120-133](../../core/dependency-architecture/workflows.md)) opens
with "measure/profile (establish the baseline and the dominant cost)", while
workflow #4 (debugging, [workflows.md:71-86](../../core/dependency-architecture/workflows.md))
opens with "reproduce → ⟳ { hypothesize → instrument/observe → narrow }". A
regression-shaped performance task needs workflow #4's *shape* (narrow to the
cause, cheapest hypothesis first) applied to workflow #7's *domain*. With
workflow #4 unstaffed, the router has only #7 available, and **#7 hard-codes
profiling as the first move.** The gap is therefore not merely "an intent with no
skill to route to" — it is "the only routable workflow silently imposes the wrong
opening move on a whole class of task."

[`examples.md:152-172`](../../core/routing-architecture/examples.md) (Example 5,
"Why is our Next.js page slow to load?") composes exactly the right shape —
`⟳ debugging loop { … } → performance-engineering` — and R-02 already notes that
loop carries no skill ID. This task shows what the unattributed loop costs in
practice.

**Root cause.** As X-01 established: the taxonomy never allocated a debugging
owner, and the workflow patterns were written as if one existed.

**Recommended correction.** No new recommendation — X-01's own recommendation
(author `SK-CONV-009 · debugging`) is the fix. This evaluation adds one
requirement to that skill's eventual spec: its decision framework must open with
change attribution ("is there a known-good state and an identifiable change?")
before instrumentation, and it must declare an escalation edge to
`performance-engineering` for the case where the cause is localized but the
remedy is a performance trade-off.

**Regression test requirement.** No new scenario. Once X-01 is resolved,
`regression-suite.md`'s trigger 2 ("a new skill is authored that could plausibly
compete for activation in an existing scenario") requires re-running S03 and S09;
the proposed `S17` should be added to that re-run set.

---

### P-5 · Degrading an audit trail for performance passes without a security owner — **Medium**

**Finding.** The plausible fixes here — batch the audit write, make it async,
sample it, drop fields, or move it off the request path — all degrade a control
with security and compliance meaning. `performance-engineering` handles this
*correctly at its own boundary*: its Security section
([SKILL.md:206-211](../../skills/performance-engineering/SKILL.md)) says "where
performance tuning intersects security (e.g. disabling a rate limit for
throughput), flag the trade-off and defer to security-engineering." That is a
genuine strength and the right instinct.

The problem is the receiving end. `security-engineering`'s
`activation_conditions`
([security-engineering/skill.yaml:32-36](../../skills/security-engineering/skill.yaml))
are: security-sensitive code handling untrusted input, secrets, or a trust
boundary; an explicitly requested security review; a dependency/supply-chain
check; a documented CVE range. SR-5 gives the router the same three triggers
([rules.md:25-26](../../core/routing-architecture/rules.md)). An admin audit log
is none of them on a literal reading — it is an *integrity/accountability*
control, not an input-validation or secret-handling one. So the hand-off target
exists but the router has no hook to activate it, and S-Gate 4's mandatory
security facet ([security-and-validation.md:67](../../core/orchestrator/security-and-validation.md))
is keyed to the same three triggers.

Separately: **no skill in this library owns audit/compliance logging.** Verified
by grep — "audit log"/"audit trail" appears only inside `opensearch` and
`mongoose` as incidental technology content. `observability` explicitly scopes
itself to production *diagnosability*
([observability/skill.yaml:10-22](../../skills/observability/skill.yaml)), which
is a different purpose from a tamper-evident record of privileged actions.

**Root cause.** SR-5's trigger list was derived from the AppSec categories in
[`security-knowledge-map.md`](../../research/knowledge-maps/security-knowledge-map.md),
which is organized around injection, secrets, and authn/authz. Accountability and
audit-integrity controls are a fourth category the map does not carry, so neither
the skill nor the routing rule names them.

**Recommended correction.** Two parts, both small:

1. Extend SR-5's `security-engineering` trigger and the skill's
   `activation_conditions` with "or a change that weakens an existing security
   control (audit/access logging, rate limiting, validation, isolation)." This is
   the trigger `performance-engineering`'s own Security section already assumes
   exists.
2. Record "audit/compliance logging" in
   [`taxonomy-analysis.md`](../../core/taxonomy/taxonomy-analysis.md)'s *Missing
   capabilities* section alongside the existing reliability/resilience and
   IaC/Kubernetes gaps, so it is a declared gap rather than a silent one. Do not
   author a skill for it without a research pass — that would violate the
   library's own grounding discipline.

**Regression test requirement.** Add as a `major` assertion inside the proposed
`S17` rather than a separate scenario: the run flags that the proposed fix
weakens an audit control and either activates `security-engineering` or records
the trade-off as a residual risk (FV-12). Checked: no existing scenario covers a
performance fix that degrades a security control — S07 and S08 are
security-sensitive tasks, not performance tasks with security side effects.

---

### P-6 · Workflow #7 has no regression-guard step, and the routing examples say it should — **Medium**

**Finding.** Workflow #3 (bug fixing) requires "regression test (testing-strategy:
add a test that fails before, passes after)"
([workflows.md:64](../../core/dependency-architecture/workflows.md)), and T-Gate 3
makes it a status rule: "A bug fix carries a test that fails before and passes
after. A fix with no such test is `partial`, not `complete`"
([security-and-validation.md:98](../../core/orchestrator/security-and-validation.md)).
Workflow #7 (performance optimization,
[workflows.md:120-133](../../core/dependency-architecture/workflows.md)) has
**no verification step at all** — it runs measure → ⟳ optimize → `code-review ⤾`
→ optional deploy. Meanwhile
[`examples.md:163`](../../core/routing-architecture/examples.md) routes exactly
this shape as "→ [fix] → testing-strategy (guard the regression)".

So: the normative workflow omits the guard, a worked example in the same
subsystem includes it, and T-Gate 3 is keyed to the phrase "a bug fix" — which a
run that classified this task as workflow #7 has no reason to believe applies.
A performance regression fixed with no benchmark or budget assertion is a
regression that will silently return.

**Root cause.** The ten workflow patterns were authored as domain shapes; the
testing gates were authored later, in the orchestrator layer, and keyed to the
*intent word* ("bug fix") rather than to the invariant underneath it ("a
previously-working behavior was restored"). The examples file was written against
the intent rather than the workflow table, and the two were never reconciled.

**Recommended correction.** Add a verification step to workflow #7 between the
optimization loop and `code-review`: "→ testing-strategy (lock the restored
budget: a benchmark or performance assertion that fails at the regressed value
and passes at the target)". Then generalise T-Gate 3 from "A bug fix carries a
test that fails before and passes after" to "**A fix that restores a previously
working behavior — functional or performance —** carries a check that fails
before and passes after."

**Regression test requirement.** `major` assertion inside the proposed `S17`:
the run's plan contains a regression-guard step and the run does not reach
`complete` without it (or records it as an explicit residual per FV-6). Checked:
S09 — the only scenario with an applied performance fix — is worth re-reading
against this once `S17` is authored, per `regression-suite.md` trigger 3
(a change to `core/dependency-architecture/` invalidates expected sequencing).

---

## What the library gets right on this task

Stated deliberately, because the findings above are not the whole picture:

- **Routing precision is excellent.** The excluded set is large, correct, and
  mechanically derivable: no frontend, SEO, realtime, AI, documentation, or
  undetected-technology skill has any path in. Default-deny plus SR-3 does
  exactly what it claims.
- **`requirements-engineering` is correctly *not* activated.** Its
  `non_activation_conditions[0]` fires precisely as designed. Compare Task 2 and
  Task 3 of this evaluation, where the same field fires when it should not — the
  field is well-written for well-specified requests and badly calibrated for
  contradictory or under-parameterized ones.
- **The anti-over-engineering guards are strong and would prevent the common
  failure.** "Refuse to micro-optimize a component that isn't the measured
  dominant cost"
  ([skill.yaml:82](../../skills/performance-engineering/skill.yaml)) and decision
  step 4's "Don't reach for the familiar lever without checking it matches the
  actual cause" ([SKILL.md:146-149](../../skills/performance-engineering/SKILL.md))
  would together stop the classic bad outcome here — bolting Redis onto a
  dashboard whose real problem is a synchronous write per request.
- **The cross-boundary hand-off to security is written correctly** even though
  the receiving skill will not route (P-5). The instinct and the sentence are
  both right.
- **The capability barrier is honest.** Tier B + `required_capabilities:
  [file-read, file-write, shell]` means the adapter resolves *before* the step,
  so an advisory-mode profiling recommendation is marked unexecuted (IC-3) rather
  than reported as done.

---

## Dimension scoring

Scale: 5 = the library's guidance is what a principal engineer would want;
3 = usable but with a real gap; 1 = the guidance actively leads the run wrong.

| # | Dimension | Score | Basis |
|---|---|---|---|
| 1 | Skill routing | 3 / 5 | The right skills activate and the exclusions are clean, but the decisive repository signal never enters routing (P-2) and the debug-shaped intent has no owner (P-4) |
| 2 | Dependency activation | 4 / 5 | Capability-adapter barrier, `performance-engineering → database-operations` hand-off, `code-review` performance facet all correctly sequenced; loses a point for the unstaffed diagnostic stage |
| 3 | Context efficiency | 4 / 5 | Tight set, Tier-0 selection, lazy bodies — but the *cheapest* decisive context (`git show` on one commit) is not in the context plan (P-2, P-3) |
| 4 | Implementation quality | 2 / 5 | The guidance funnels to "go profile" when a minutes-long diff read almost certainly dominates; the right answer is reachable only by luck via the fixed cross-stack-pattern list (P-1) |
| 5 | Security | 2 / 5 | The trade-off is correctly flagged by `performance-engineering`, but `security-engineering` will not route in, and no skill owns audit/compliance logging (P-5) |
| 6 | Testing | 2 / 5 | Workflow #7 carries no regression guard and T-Gate 3 is keyed to "a bug fix"; a perf regression could be fixed with nothing locking the restored budget (P-6) |
| 7 | Maintainability | 4 / 5 | Strong anti-over-engineering discipline; refuses non-bottleneck micro-optimization and familiar-lever reaching |
| 8 | Error handling | 4 / 5 | F1/F2 → R4 degrade-to-advisory is well-specified; B-1's stated exit criterion for the optimization loop ("budget met **or** diminishing returns") is present and correct |
| 9 | Repository convention adherence | 4 / 5 | ST-5 detect-once-and-carry works; `git-conventions` attaches correctly at commit time with a `perf:`/`fix:` prefix from the detected history |
| 10 | Final outcome | 2 / 5 | A real engineer gets a methodologically impeccable answer to the wrong question, and would most likely have to supply "it was the audit-trail commit" themselves |

**Task verdict: `partial`.** The routing layer performs well; the performance
skill's decision framework is not sophisticated enough to use regression context
as a signal, and the orchestrator's intake cannot see that context in the first
place.
