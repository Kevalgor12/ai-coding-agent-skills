"""
Scorer — converts per-assertion CheckResults into AssertionVerdicts and ScenarioScores.

Scoring rules from evaluations/scoring.md:
  - critical:  one failure → scenario outcome = failed
  - major:     deduction; ≥ 2/3 must pass for outcome to reach complete
  - minor:     tracked, does not affect outcome

Scenario outcomes:
  complete  — all critical+major pass
  partial   — all critical pass, ≥1 major fails
  failed    — any critical fails
  blocked   — evaluator cannot determine critical pass/fail (all critical = not-evaluated)
"""

from __future__ import annotations

from .checker import evaluate_check
from .config import (
    OUTCOME_BLOCKED,
    OUTCOME_COMPLETE,
    OUTCOME_FAILED,
    OUTCOME_PARTIAL,
    PROMOTION_MIN_MAJOR_PASS_RATE,
    VERDICT_FAIL,
    VERDICT_NOT_EVALUATED,
    VERDICT_PASS,
    WEIGHT_CRITICAL,
    WEIGHT_MAJOR,
    WEIGHT_MINOR,
)
from .models import (
    Assertion,
    AssertionVerdict,
    RunRecord,
    Scenario,
    ScenarioScore,
)


def score_assertion(assertion: Assertion, record: RunRecord) -> AssertionVerdict:
    """
    Evaluate all checks for one assertion and produce a single verdict.

    - If there are no machine checks → not-evaluated (human review required)
    - If any check returns fail → verdict = fail
    - If any check returns not-evaluated and none returned fail → not-evaluated
    - If all checks pass → pass
    """
    if not assertion.checks:
        return AssertionVerdict(
            assertion=assertion,
            verdict=VERDICT_NOT_EVALUATED,
            evidence="no machine checks — human review required",
            reason="evaluation_method=human_review or no checks defined",
            needs_human_review=True,
        )

    results = [evaluate_check(c, record) for c in assertion.checks]
    evidence_parts = [f"[{c.verdict}] {c.evidence}" for c in results]
    evidence = "\n".join(evidence_parts)

    failed = [r for r in results if r.verdict == VERDICT_FAIL]
    not_evaluated = [r for r in results if r.verdict == VERDICT_NOT_EVALUATED]

    if failed:
        return AssertionVerdict(
            assertion=assertion,
            verdict=VERDICT_FAIL,
            evidence=evidence,
            reason=f"{len(failed)} check(s) failed",
            needs_human_review=False,
        )

    if not_evaluated:
        return AssertionVerdict(
            assertion=assertion,
            verdict=VERDICT_NOT_EVALUATED,
            evidence=evidence,
            reason=f"{len(not_evaluated)} check(s) not evaluated",
            needs_human_review=any(
                c.type == "human_review" for c in assertion.checks
            ),
        )

    return AssertionVerdict(
        assertion=assertion,
        verdict=VERDICT_PASS,
        evidence=evidence,
        reason=f"all {len(results)} check(s) passed",
        needs_human_review=False,
    )


def score_scenario(
    scenario: Scenario,
    assertions: list[Assertion],
    record: RunRecord,
) -> ScenarioScore:
    """Score all assertions and determine the scenario-level outcome."""
    verdicts = [score_assertion(a, record) for a in assertions]

    # Partition by weight
    crits  = [v for v in verdicts if v.assertion.weight == WEIGHT_CRITICAL]
    majors = [v for v in verdicts if v.assertion.weight == WEIGHT_MAJOR]
    minors = [v for v in verdicts if v.assertion.weight == WEIGHT_MINOR]

    def _pass(v: AssertionVerdict) -> bool:
        return v.verdict == VERDICT_PASS

    crit_passed  = sum(1 for v in crits  if _pass(v))
    crit_total   = len(crits)
    major_passed = sum(1 for v in majors if _pass(v))
    major_total  = len(majors)
    minor_passed = sum(1 for v in minors if _pass(v))
    minor_total  = len(minors)

    crit_failed      = [v for v in crits if v.verdict == VERDICT_FAIL]
    crit_not_eval    = [v for v in crits if v.verdict == VERDICT_NOT_EVALUATED]

    # Determine outcome
    if crit_failed:
        outcome = OUTCOME_FAILED
    elif crit_not_eval and crit_passed == 0:
        # Cannot evaluate any critical assertions — blocked
        outcome = OUTCOME_BLOCKED
    elif major_total == 0 or (major_total > 0 and major_passed / major_total >= PROMOTION_MIN_MAJOR_PASS_RATE):
        outcome = OUTCOME_COMPLETE
    else:
        outcome = OUTCOME_PARTIAL

    failed_assertions = [v for v in verdicts if v.verdict == VERDICT_FAIL]
    not_applicable = [v for v in verdicts if v.verdict == "not-applicable"]
    not_evaluated = [v for v in verdicts if v.verdict == VERDICT_NOT_EVALUATED]

    return ScenarioScore(
        scenario=scenario,
        run_record=record,
        verdicts=verdicts,
        outcome=outcome,
        critical_passed=crit_passed,
        critical_total=crit_total,
        major_passed=major_passed,
        major_total=major_total,
        minor_passed=minor_passed,
        minor_total=minor_total,
        failed_assertions=failed_assertions,
        not_applicable=not_applicable,
        not_evaluated=not_evaluated,
    )
