"""
Promotion gate — determines whether a skill is eligible for promotion to v0.1.0.

Gate requirements (from evaluations/evaluation-spec.md § "Promotion requirements"):
  1. At least one scenario exists that must-activate this skill.
  2. That scenario has been executed (a RunRecord exists).
  3. All critical assertions pass.
  4. No critical security failures (weight=critical, dimension=7).
  5. ≥ 2/3 of major assertions pass.
  6. At least 1 human reviewer has signed off (i.e., human_review assertions not pending).
  7. No blocking regressions (not evaluated here — caller must supply).
  8. All VR-1–VR-9 structural checks pass (not re-evaluated here; assumed from prior audit).

Requirements 7 and 8 are pre-conditions the caller is expected to have verified.
This module evaluates requirements 1–6 from live ScenarioScore data.
"""

from __future__ import annotations

from .config import (
    PROMOTION_MIN_MAJOR_PASS_RATE,
    PROMOTION_REQUIRED_REVIEWS,
    VERDICT_FAIL,
    VERDICT_NOT_EVALUATED,
    VERDICT_PASS,
    WEIGHT_CRITICAL,
    WEIGHT_MAJOR,
)
from .models import (
    PromotionDecision,
    PromotionRequirement,
    ScenarioScore,
)


def _req(name: str, satisfied: bool, details: str) -> PromotionRequirement:
    return PromotionRequirement(name=name, satisfied=satisfied, details=details)


def evaluate_promotion(
    skill_id: str,
    skill_slug: str,
    scores: list[ScenarioScore],
    *,
    human_reviewers: int = 0,
) -> PromotionDecision:
    """
    Evaluate all promotion gate requirements for a skill.

    Parameters
    ----------
    skill_id:        e.g. "SK-DB-001"
    skill_slug:      e.g. "postgresql-deduplication"
    scores:          ScenarioScore objects for every scenario that must-activate this skill
    human_reviewers: number of human sign-offs recorded for this skill
    """
    gates: list[PromotionRequirement] = []

    # Gate 1: at least one scenario
    has_scenario = len(scores) > 0
    gates.append(_req(
        "scenario_exists",
        has_scenario,
        f"{len(scores)} scenario(s) defined" if has_scenario else "no scenarios defined",
    ))

    # Gate 2: scenario executed (run_record has a non-empty status)
    if has_scenario:
        executed = [s for s in scores if s.run_record.status]
        gates.append(_req(
            "scenario_executed",
            len(executed) > 0,
            f"{len(executed)}/{len(scores)} scenario(s) executed",
        ))
    else:
        gates.append(_req("scenario_executed", False, "no scenarios to execute"))

    # Gate 3: all critical assertions pass
    crit_verdicts = [
        v
        for s in scores
        for v in s.verdicts
        if v.assertion.weight == WEIGHT_CRITICAL
    ]
    crit_failed = [v for v in crit_verdicts if v.verdict == VERDICT_FAIL]
    all_crit_pass = len(crit_verdicts) > 0 and len(crit_failed) == 0
    gates.append(_req(
        "critical_assertions_pass",
        all_crit_pass,
        (
            f"all {len(crit_verdicts)} critical assertion(s) pass"
            if all_crit_pass
            else f"{len(crit_failed)}/{len(crit_verdicts)} critical assertion(s) failed: "
                 + ", ".join(v.assertion.assertion_id for v in crit_failed[:3])
        ),
    ))

    # Gate 4: no critical security failures (critical + dimension 7)
    crit_sec_failed = [
        v for v in crit_verdicts
        if v.verdict == VERDICT_FAIL and 7 in v.assertion.dimensions
    ]
    gates.append(_req(
        "no_critical_security_failures",
        len(crit_sec_failed) == 0,
        (
            "no critical security failures"
            if not crit_sec_failed
            else f"{len(crit_sec_failed)} critical security assertion(s) failed: "
                 + ", ".join(v.assertion.assertion_id for v in crit_sec_failed[:3])
        ),
    ))

    # Gate 5: ≥ 2/3 of major assertions pass
    major_verdicts = [
        v
        for s in scores
        for v in s.verdicts
        if v.assertion.weight == WEIGHT_MAJOR
    ]
    major_passed = sum(1 for v in major_verdicts if v.verdict == VERDICT_PASS)
    major_total = len(major_verdicts)
    major_rate = major_passed / major_total if major_total > 0 else 1.0
    major_ok = major_total == 0 or major_rate >= PROMOTION_MIN_MAJOR_PASS_RATE
    gates.append(_req(
        "major_pass_rate",
        major_ok,
        f"{major_passed}/{major_total} major assertions pass "
        f"(rate={major_rate:.0%}, required≥{PROMOTION_MIN_MAJOR_PASS_RATE:.0%})",
    ))

    # Gate 6: human reviewer sign-off
    # If any assertion requires human_review and is not-evaluated, we count it
    # against this gate unless the caller has supplied sign-offs.
    pending_human = sum(
        1 for s in scores for v in s.verdicts
        if v.needs_human_review and v.verdict == VERDICT_NOT_EVALUATED
    )
    human_ok = human_reviewers >= PROMOTION_REQUIRED_REVIEWS or pending_human == 0
    gates.append(_req(
        "human_reviewer_signoff",
        human_ok,
        (
            f"{human_reviewers} reviewer(s) signed off"
            if human_ok
            else f"{pending_human} human_review assertion(s) pending, {human_reviewers} reviewer(s)",
        ),
    ))

    # Overall eligibility
    eligible = all(g.satisfied for g in gates)
    blocking = next((g.name for g in gates if not g.satisfied), "")

    return PromotionDecision(
        skill_id=skill_id,
        skill_slug=skill_slug,
        eligible=eligible,
        gates=gates,
        blocking_reason=blocking,
        score=scores[0] if scores else None,
    )
