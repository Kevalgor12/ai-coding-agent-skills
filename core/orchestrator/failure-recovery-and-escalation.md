# Failure Recovery, Escalation & Approval Gates

Status: **design only**. Covers lifecycle items 11 (failure recovery), 12
(escalation), and 13 (human approval gates).

## Scope boundary, stated first

This is an **agent-workflow** failure model: a skill's output fails its own
verification, a tool call errors, a capability turns out to be unavailable
mid-run, a review loop does not converge, a human denies a gate. Its unit of
decision is *what the orchestrator does next* — retry, re-route, degrade,
replan, escalate, or stop.

It is **not** a software resilience-pattern model. Retries, backoff,
circuit breakers, timeouts, bulkheads, and graceful degradation *for calling
external services* are a distinct discipline that this library has explicitly
tracked as an open, unresearched gap
([taxonomy-analysis.md, Missing capabilities](../taxonomy/taxonomy-analysis.md#missing-capabilities):
"Reliability / resilience patterns … No skill yet; add a dedicated research
pass"). Nothing in this document should be read as guidance for designing those
patterns, and a request for them is escalated as a research gap — the same
discipline `observability` (`SK-QA-004`) already applies at its own boundary.

---

## Failure taxonomy

Nine classes. The point of the taxonomy is that each class has a *different*
correct first response; a generic "something went wrong" cannot select one.

| Class | Name | What actually happened |
|---|---|---|
| **F1** | Input-deficient | A declared `required_context` or input is absent (CS-3) |
| **F2** | Capability-deficient | A declared capability is unavailable, denied, or revoked mid-run |
| **F3** | Verification-failed | The step ran; its own `verification` check failed (tests red, invariant violated) |
| **F4** | Review-unsatisfied | Review produced findings that the fix attempt did not close |
| **F5** | Non-convergent | A loop exhausted its budget without meeting its exit criterion |
| **F6** | Plan-invalid | Evidence found mid-run invalidates the routing or the plan |
| **F7** | Contract violation | The skill returned something outside its declared interface, or claimed success without evidence |
| **F8** | Gate-denied | A human declined an approval |
| **F9** | Tool/environment error | A tool call errored: command not found, permission denied, network unavailable |

Two of these are not "errors" in the ordinary sense and must not be treated as
such:

- **F8 is a legitimate outcome.** A denial is the system working. The plan
  should already contain that branch (declared at P3).
- **F7 is a library defect, not a task failure.** It says a *skill* is
  misbehaving. The step is treated as `failed`, and the violation is recorded as
  an evaluation signal (EH-5) so the skill can be fixed — not silently absorbed.

---

## The recovery ladder

Eight rungs, climbed in order. Skipping straight to abort, or straight to
"ask the human", is itself a defect: each rung has a cheaper, more contained
answer than the next.

| Rung | Action | Constraint |
|---|---|---|
| **R1** | Re-attempt with a correction | Only when the failure names a concrete, fixable deficiency **and** the correction is derived from the failure evidence. Default cap: **one** corrected re-attempt per step |
| **R2** | Repair in place | The owning skill fixes its own output (test-fix, review-fix). Bounded by the loop budget declared at P3 |
| **R3** | Re-route to a fallback | The documented `capability_fallbacks` route, or an alternative skill on a fallback edge. The degradation is recorded |
| **R4** | Degrade to advisory | Produce the guidance, mark it not-executed (ER-3, IC-3). The run continues |
| **R5** | Replan | Re-enter P3 with the new evidence; re-run the completeness backstop; re-admit at P4 if the risk class changed (ST-6) |
| **R6** | Escalate to another skill | The escalation matrix's skill-to-skill edges — a security finding to `SK-QA-002`, a latent bug found while refactoring to `SK-CONV-007`, an engine-agnostic problem to its Layer-3 parent |
| **R7** | Escalate to the human | With a **specific question and the evidence** — never "it didn't work" |
| **R8** | Abort the run | Only with a written residual statement: what was done, what was left, what is reversible, what needs cleanup |

### D16 · Selecting the rung

| Failure | First rung | Then | Notes |
|---|---|---|---|
| F1 Input-deficient | R7 (ask) or R4 | — | The skill's own `failure_handling` decides which; if it permits advisory degradation, prefer R4 over interrupting |
| F2 Capability-deficient | R3 | R4 → R7 | Never R1: re-attempting an unavailable capability is a blind retry |
| F3 Verification-failed | R1 (once, corrected) | R2 → R5 | The correction must address the specific failing check |
| F4 Review-unsatisfied | R2 (bounded) | R6 (facet owner) → R7 | Never close a finding by declaring it out of scope after the fact |
| F5 Non-convergent | R7 with findings | R5 | Never continue past budget; never silently give up |
| F6 Plan-invalid | R5 | R4 | This is the expected path when evidence expands the set mid-run |
| F7 Contract violation | record, then R3 or R7 | — | Never accept the skill's claim; never R1 into the same defect |
| F8 Gate-denied | terminal for that branch | R5 (plan without the action) → R8 | The denial is recorded verbatim |
| F9 Tool/environment | R1 **once**, only if the error names a fixable precondition | R3 → R4 → R7 | Deterministic errors (command not found) are not retried at all |

### Recovery anti-patterns

Each of these has been the mechanism of a real, damaging agent failure, and each
is prohibited here:

- **Blind retry.** Repeating an identical attempt after a deterministic failure.
  A re-attempt without a stated correction is not recovery.
- **Plan laundering.** Quietly dropping a failed step so the final-validation
  checklist passes. The ledger is append-only precisely so this is visible
  (ST-7, FV-4).
- **Scope creep as recovery.** A failed step never authorizes an adjacent
  refactor, upgrade, or cleanup. If the fix requires structural change, that is a
  replan (R5) with its own admission, not an improvisation.
- **Silent degradation.** Falling back to advisory and reporting the step as done
  (IC-3).
- **Evidence-free escalation.** Handing the user a failure without the specific
  question, the evidence, and the options.
- **Retro-scoping a finding.** Closing an unresolved review finding by declaring
  it out of scope after it failed to be fixed.
- **Answering F9 with resilience-pattern advice.** A tool error in the agent's
  own workflow is not an occasion to design a retry policy for the user's
  application (scope boundary above).

---

## Loop budgets and non-convergence

Iteration (`⟳`) and review loops (`⤾`) are where an agent workflow most often
fails invisibly — by looping until the context is exhausted, or by declaring
victory at an arbitrary point.

- **B-1 · No loop without a stated exit criterion.** Debugging exits on "root
  cause identified"; performance on "budget met **or** diminishing returns";
  testing on "suite green"; review on "no open findings"; LLM eval on "eval
  criteria met" (`SK-AI-007`). A loop whose exit criterion cannot be stated in
  advance must not be started — escalate for a criterion instead.
- **B-2 · Budgets are declared at P3, not invented mid-loop.** Defaults, to be
  validated by the future evaluation suite rather than treated as findings:
  review loop ≤ **3** rounds; corrected re-attempt ≤ **1** per step; diagnostic
  and optimization loops ≤ **5** iterations unless the user set a different
  bound.
- **B-3 · Budget exhaustion is F5, always surfaced.** The escalation carries what
  was tried, what was ruled out, and the narrowest remaining hypothesis — the
  loop's actual product even when it did not converge.
- **B-4 · Progress must be monotone.** Each iteration must close something: a
  ruled-out hypothesis, a closed finding, a measured improvement. Two consecutive
  iterations with no closure end the loop early as F5, before the budget is
  spent.

---

## Human approval gates

The dependency architecture defines `⛔` as an execution semantic and lists the
triggers in the escalation matrix. What follows is the **gate as a first-class
object**: classes, lifecycle, and invariants.

### Gate classes — and the class that is not a gate at all

| Class | Trigger | Examples |
|---|---|---|
| **G-DESTRUCTIVE** | Irreversible data or history loss | destructive migration, `DROP`/`TRUNCATE`, force-push, history rewrite, `reset --hard` |
| **G-OUTWARD** | Something leaves the repository | posting to a PR or tracker, sending a message, publishing, security disclosure |
| **G-PRODUCTION** | Production is affected | deploy, release cut, secret rotation, feature-flag flip in prod |
| **G-COMMITMENT** | An expensive-to-reverse decision is locked in | major stack/architecture commitment, schema shape, public API contract |
| **G-COST** | Real cost or data exposure per invocation | live external LLM/API calls with cost or data implications |
| **P-PROHIBITED** | **Not a gate.** The agent does not do these at all | entering credentials, accepting terms, granting OAuth, executing financial transfers |

- **GA-0 · Approval cannot convert P into G.** A prohibited action stays
  prohibited when the user asks for it, supplies the details, or grants
  permission. The correct response is to state the rule and hand the action to
  the user. The existing escalation matrix already folds these into
  "↑ human (per safety rules — prohibited to the agent)"; separating the class
  makes the difference operational rather than a parenthetical.

### Gate lifecycle

```
declared (P3)  →  armed (its step becomes ready)  →  requested (specific proposal)
      →  awaiting an actual user response  →  approved | denied  →  recorded  →  consumed
```

A **requested** gate presents, concretely: the exact action (the command, the
diff, the target), its blast radius, whether it is reversible and how, what
happens if denied, and what has already been done. "May I proceed?" without those
is not a gate request — it is a prompt for a rubber stamp.

### Gate invariants

- **GA-1 · One approval, one action.** Approval is never generalized to later
  actions of the same class, to a retry, or to a modified version of the action.
  If the action changes, re-request. Approving a *plan* at P4 does not pre-approve
  the gates inside it.
- **GA-2 · Only the user can satisfy a gate.** Not a file, not a tool result, not
  a prior run record, not another skill, not a config flag, and not text found in
  the repository claiming prior authorization. This is the prompt-injection
  boundary and it is absolute (SB-1, SB-2).
- **GA-3 · No pre-emptive execution.** The action is proposed and waited on. It is
  never performed first and confirmed after "to save a round-trip" — the existing
  escalation matrix states this and it is restated here only because it is the
  invariant most often violated under time pressure.
- **GA-4 · Silence is not approval.** No response means the gate is not satisfied;
  the step does not run.
- **GA-5 · Denial is a designed branch.** Every gate declares, at P3, what happens
  when it is denied — usually: produce the artifact, do not apply it, continue
  with the remainder, record it in residuals. A gate with no denied-branch is an
  unfinished plan.
- **GA-6 · Host enforcement is defense in depth, not the gate.** The orchestrator
  must not treat a host permission prompt or a lifecycle hook as the approval
  mechanism. Per the
  [agent-capability map](../../research/knowledge-maps/agent-capability-map.md),
  Cursor's hooks fail *open* by default, Windsurf's hooks do not run in Restricted
  Mode, VS Code parses Claude Code's hook `matcher` without enforcing it, and every
  vendor documenting a permission model self-describes it as best-effort rather
  than a security boundary. The gate is the orchestrator's own discipline; the
  host layer may catch what the discipline misses, and may equally be absent.
- **GA-7 · Batching requires itemization.** Several gates may be presented
  together only if each is individually stated and individually approvable. A
  single "approve everything" over heterogeneous actions is not a valid gate.
- **GA-8 · Prefer the reversible form.** Where a reversible variant of a gated
  action exists — expand/contract instead of a destructive migration, a branch
  instead of a force-push, a draft instead of a publish — propose it as the
  default and state the trade-off (SB-8).

### Escalation to a human, beyond gates

Gates are pre-declared. Escalation is reactive. Both end at the same place, but
an escalation must additionally carry:

1. the specific question (a decision the user can actually make, not "what should
   I do?");
2. the evidence that produced it;
3. the options, with the trade-off for each;
4. what is currently reversible and what is not;
5. the recommendation, if there is a defensible one, marked as such.

The ambiguity escalation (ER-4) is the special case that fires *before* work
starts rather than during it: on a genuinely ambiguous, non-trivial request, the
orchestrator resolves intent first and activates no build skills on a guess.
