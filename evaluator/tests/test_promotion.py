"""Tests for evaluator/promotion.py"""

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from evaluator.promotion import evaluate_promotion
from evaluator.config import VERDICT_FAIL, VERDICT_PASS, VERDICT_NOT_EVALUATED
from evaluator.models import (
    ActivationSet,
    Assertion,
    AssertionVerdict,
    RunRecord,
    Scenario,
    ScenarioScore,
)


def _scenario() -> Scenario:
    return Scenario(
        scenario_id="S01",
        name="Test",
        category="simple",
        complexity="small",
        risk_level="read-only",
        task="test",
        repository_signals="",
        activation_set=ActivationSet([], [], []),
        sequencing_text="",
        source_file=Path("."),
    )


def _record() -> RunRecord:
    return RunRecord(scenario_id="S01", task="test", status="complete")


def _assertion(weight: str, dim: list[int] | None = None) -> Assertion:
    return Assertion(
        assertion_id="S01-A1",
        scenario_id="S01",
        number=1,
        description="test",
        prose="test",
        weight=weight,
        dimensions=dim or [1],
        evaluation_method="observation",
        checks=[],
    )


def _verdict(assertion, verdict_str, needs_human=False) -> AssertionVerdict:
    return AssertionVerdict(
        assertion=assertion,
        verdict=verdict_str,
        evidence="test",
        reason="test",
        needs_human_review=needs_human,
    )


def _score(verdicts: list[AssertionVerdict], outcome: str = "complete") -> ScenarioScore:
    crit_pass = sum(1 for v in verdicts if v.assertion.weight == "critical" and v.verdict == VERDICT_PASS)
    crit_total = sum(1 for v in verdicts if v.assertion.weight == "critical")
    maj_pass = sum(1 for v in verdicts if v.assertion.weight == "major" and v.verdict == VERDICT_PASS)
    maj_total = sum(1 for v in verdicts if v.assertion.weight == "major")
    return ScenarioScore(
        scenario=_scenario(),
        run_record=_record(),
        verdicts=verdicts,
        outcome=outcome,
        critical_passed=crit_pass,
        critical_total=crit_total,
        major_passed=maj_pass,
        major_total=maj_total,
    )


class TestEvaluatePromotion:
    def test_no_scenarios_not_eligible(self):
        decision = evaluate_promotion("SK-DB-001", "db-skill", [])
        assert not decision.eligible
        assert decision.blocking_reason == "scenario_exists"

    def test_all_pass_eligible(self):
        a = _assertion("critical")
        v = _verdict(a, VERDICT_PASS)
        score = _score([v])
        decision = evaluate_promotion("SK-DB-001", "db-skill", [score], human_reviewers=1)
        assert decision.eligible

    def test_critical_fail_not_eligible(self):
        a = _assertion("critical")
        v = _verdict(a, VERDICT_FAIL)
        score = _score([v], outcome="failed")
        decision = evaluate_promotion("SK-DB-001", "db-skill", [score], human_reviewers=1)
        assert not decision.eligible
        assert decision.blocking_reason == "critical_assertions_pass"

    def test_critical_security_fail_blocks(self):
        a = _assertion("critical", dim=[7])  # dimension 7 = security
        v = _verdict(a, VERDICT_FAIL)
        score = _score([v], outcome="failed")
        decision = evaluate_promotion("SK-DB-001", "db-skill", [score], human_reviewers=1)
        assert not decision.eligible
        assert "critical_assertions_pass" in decision.blocking_reason or "critical_security" in decision.blocking_reason

    def test_major_fail_rate_blocks(self):
        a_crit = _assertion("critical")
        v_crit = _verdict(a_crit, VERDICT_PASS)
        # 1/3 major pass rate — below threshold
        majors = [_assertion("major") for _ in range(3)]
        major_verdicts = [_verdict(majors[0], VERDICT_PASS)] + [_verdict(m, VERDICT_FAIL) for m in majors[1:]]
        score = _score([v_crit] + major_verdicts, outcome="partial")
        decision = evaluate_promotion("SK-DB-001", "db-skill", [score], human_reviewers=1)
        assert not decision.eligible
        assert decision.blocking_reason == "major_pass_rate"

    def test_human_review_pending_blocks(self):
        a = _assertion("critical")
        v = _verdict(a, VERDICT_PASS)
        # Add a not-evaluated assertion with human review needed
        a_hr = _assertion("minor")
        v_hr = AssertionVerdict(
            assertion=a_hr,
            verdict=VERDICT_NOT_EVALUATED,
            evidence="",
            reason="",
            needs_human_review=True,
        )
        score = _score([v, v_hr])
        decision = evaluate_promotion("SK-DB-001", "db-skill", [score], human_reviewers=0)
        assert not decision.eligible
        assert decision.blocking_reason == "human_reviewer_signoff"

    def test_gates_all_listed(self):
        a = _assertion("critical")
        v = _verdict(a, VERDICT_PASS)
        score = _score([v])
        decision = evaluate_promotion("SK-DB-001", "db-skill", [score], human_reviewers=1)
        gate_names = {g.name for g in decision.gates}
        assert "scenario_exists" in gate_names
        assert "critical_assertions_pass" in gate_names
        assert "major_pass_rate" in gate_names
        assert "human_reviewer_signoff" in gate_names
