"""Tests for evaluator/scorer.py"""

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from evaluator.scorer import score_assertion, score_scenario
from evaluator.config import (
    OUTCOME_BLOCKED,
    OUTCOME_COMPLETE,
    OUTCOME_FAILED,
    OUTCOME_PARTIAL,
    VERDICT_FAIL,
    VERDICT_NOT_EVALUATED,
    VERDICT_PASS,
)
from evaluator.models import (
    ActivationSet,
    Assertion,
    AssertionCheck,
    LedgerEntry,
    RoutingEntry,
    RunRecord,
    Scenario,
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


def _assertion(weight: str, checks=None, method="observation") -> Assertion:
    return Assertion(
        assertion_id="S01-A1",
        scenario_id="S01",
        number=1,
        description="test",
        prose="test assertion",
        weight=weight,
        dimensions=[1],
        evaluation_method=method,
        checks=checks or [],
    )


def _record(routing_selected=None, status="complete") -> RunRecord:
    return RunRecord(
        scenario_id="S01",
        task="test",
        status=status,
        routing_selected=routing_selected or [],
    )


class TestScoreAssertion:
    def test_no_checks_human_review(self):
        a = _assertion("critical", checks=[], method="human_review")
        verdict = score_assertion(a, _record())
        assert verdict.verdict == VERDICT_NOT_EVALUATED
        assert verdict.needs_human_review

    def test_passing_check(self):
        a = _assertion("critical", checks=[
            AssertionCheck("routing_contains", {"skill_id": "SK-DB-001"})
        ])
        record = _record(routing_selected=[RoutingEntry("SK-DB-001", "test")])
        verdict = score_assertion(a, record)
        assert verdict.verdict == VERDICT_PASS

    def test_failing_check(self):
        a = _assertion("critical", checks=[
            AssertionCheck("routing_contains", {"skill_id": "SK-DB-001"})
        ])
        record = _record(routing_selected=[])
        verdict = score_assertion(a, record)
        assert verdict.verdict == VERDICT_FAIL

    def test_one_fail_dominates_others(self):
        a = _assertion("critical", checks=[
            AssertionCheck("status_is", {"value": "complete"}),
            AssertionCheck("routing_contains", {"skill_id": "SK-MISSING"})
        ])
        record = _record(status="complete")
        verdict = score_assertion(a, record)
        assert verdict.verdict == VERDICT_FAIL


class TestScoreScenario:
    def _make_assertion(self, number, weight, check_type, **check_params):
        checks = [AssertionCheck(check_type, check_params)] if check_type else []
        return Assertion(
            assertion_id=f"S01-A{number}",
            scenario_id="S01",
            number=number,
            description=f"assertion {number}",
            prose="...",
            weight=weight,
            dimensions=[1],
            evaluation_method="observation",
            checks=checks,
        )

    def test_all_pass_complete(self):
        assertions = [
            self._make_assertion(1, "critical", "status_is", value="complete"),
            self._make_assertion(2, "major", "status_is", value="complete"),
        ]
        record = _record(status="complete")
        score = score_scenario(_scenario(), assertions, record)
        assert score.outcome == OUTCOME_COMPLETE
        assert score.critical_passed == 1
        assert score.major_passed == 1

    def test_critical_fail_gives_failed(self):
        assertions = [
            self._make_assertion(1, "critical", "routing_contains", skill_id="SK-MISSING"),
        ]
        score = score_scenario(_scenario(), assertions, _record())
        assert score.outcome == OUTCOME_FAILED
        assert score.critical_passed == 0

    def test_major_fail_gives_partial(self):
        assertions = [
            self._make_assertion(1, "critical", "status_is", value="complete"),
            self._make_assertion(2, "major", "routing_contains", skill_id="SK-MISSING"),
            self._make_assertion(3, "major", "routing_contains", skill_id="SK-MISSING"),
        ]
        record = _record(status="complete")
        score = score_scenario(_scenario(), assertions, record)
        assert score.outcome == OUTCOME_PARTIAL

    def test_no_critical_all_not_evaluated_gives_blocked(self):
        assertions = [
            Assertion(
                assertion_id="S01-A1",
                scenario_id="S01",
                number=1,
                description="test",
                prose="test",
                weight="critical",
                dimensions=[1],
                evaluation_method="human_review",
                checks=[],
            )
        ]
        score = score_scenario(_scenario(), assertions, _record())
        assert score.outcome == OUTCOME_BLOCKED

    def test_human_review_pending_property(self):
        assertions = [
            Assertion(
                assertion_id="S01-A1",
                scenario_id="S01",
                number=1,
                description="test",
                prose="test",
                weight="minor",
                dimensions=[1],
                evaluation_method="human_review",
                checks=[],
            )
        ]
        score = score_scenario(_scenario(), assertions, _record())
        assert score.has_human_review_pending
