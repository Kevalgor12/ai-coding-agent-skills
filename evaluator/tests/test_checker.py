"""Tests for evaluator/checker.py"""

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from evaluator.checker import evaluate_check, CheckResult
from evaluator.config import VERDICT_PASS, VERDICT_FAIL, VERDICT_NOT_EVALUATED
from evaluator.models import (
    AssertionCheck,
    LedgerEntry,
    RoutingEntry,
    RunRecord,
    VerificationEntry,
)


def _record(**kwargs) -> RunRecord:
    defaults = dict(
        scenario_id="S01",
        task="test task",
        status="complete",
        routing_selected=[],
        routing_excluded=[],
        ledger=[],
        verification=[],
        commands_run=[],
        files_changed=[],
        output_text="",
        open_questions=[],
    )
    defaults.update(kwargs)
    return RunRecord(**defaults)


def _check(type: str, **params) -> AssertionCheck:
    return AssertionCheck(type=type, params=params)


class TestRoutingContains:
    def test_pass_when_present(self):
        record = _record(routing_selected=[RoutingEntry("SK-TECH-postgresql", "primary")])
        result = evaluate_check(_check("routing_contains", skill_id="SK-TECH-postgresql"), record)
        assert result.verdict == VERDICT_PASS

    def test_fail_when_absent(self):
        record = _record(routing_selected=[])
        result = evaluate_check(_check("routing_contains", skill_id="SK-TECH-postgresql"), record)
        assert result.verdict == VERDICT_FAIL
        assert "SK-TECH-postgresql" in result.evidence


class TestRoutingExcludes:
    def test_pass_when_absent(self):
        record = _record(routing_selected=[])
        result = evaluate_check(_check("routing_excludes", skill_id="SK-FE-001"), record)
        assert result.verdict == VERDICT_PASS

    def test_fail_when_present(self):
        record = _record(routing_selected=[RoutingEntry("SK-FE-001", "bad")])
        result = evaluate_check(_check("routing_excludes", skill_id="SK-FE-001"), record)
        assert result.verdict == VERDICT_FAIL


class TestLedgerContains:
    def test_pass_any_status(self):
        record = _record(ledger=[LedgerEntry("invocation", "SK-CONV-001", "complete", "")])
        result = evaluate_check(_check("ledger_contains", skill_id="SK-CONV-001"), record)
        assert result.verdict == VERDICT_PASS

    def test_pass_with_status_filter(self):
        record = _record(ledger=[LedgerEntry("invocation", "SK-CONV-001", "complete", "")])
        result = evaluate_check(_check("ledger_contains", skill_id="SK-CONV-001", status="complete"), record)
        assert result.verdict == VERDICT_PASS

    def test_fail_wrong_status(self):
        record = _record(ledger=[LedgerEntry("invocation", "SK-CONV-001", "failed", "")])
        result = evaluate_check(_check("ledger_contains", skill_id="SK-CONV-001", status="complete"), record)
        assert result.verdict == VERDICT_FAIL

    def test_fail_absent(self):
        record = _record(ledger=[])
        result = evaluate_check(_check("ledger_contains", skill_id="SK-CONV-001"), record)
        assert result.verdict == VERDICT_FAIL


class TestCommandRun:
    def test_pass_substring(self):
        record = _record(commands_run=["npm test --coverage"])
        result = evaluate_check(_check("command_run", pattern="npm test"), record)
        assert result.verdict == VERDICT_PASS

    def test_fail_absent(self):
        record = _record(commands_run=["git commit"])
        result = evaluate_check(_check("command_run", pattern="npm test"), record)
        assert result.verdict == VERDICT_FAIL

    def test_pass_regex(self):
        record = _record(commands_run=["pytest -v tests/"])
        result = evaluate_check(_check("command_run", pattern="py.*test", regex=True), record)
        assert result.verdict == VERDICT_PASS


class TestFileChanged:
    def test_pass_substring(self):
        record = _record(files_changed=["src/models/user.js"])
        result = evaluate_check(_check("file_changed", path="user.js"), record)
        assert result.verdict == VERDICT_PASS

    def test_fail_absent(self):
        record = _record(files_changed=["src/models/order.js"])
        result = evaluate_check(_check("file_changed", path="user.js"), record)
        assert result.verdict == VERDICT_FAIL


class TestStatusIs:
    def test_pass(self):
        record = _record(status="complete")
        result = evaluate_check(_check("status_is", value="complete"), record)
        assert result.verdict == VERDICT_PASS

    def test_fail(self):
        record = _record(status="partial")
        result = evaluate_check(_check("status_is", value="complete"), record)
        assert result.verdict == VERDICT_FAIL


class TestOutputPattern:
    def test_pass_regex(self):
        record = _record(output_text="GROUP BY o.id, o.order_date")
        result = evaluate_check(_check("output_pattern", pattern="GROUP BY", regex=True), record)
        assert result.verdict == VERDICT_PASS

    def test_fail_pattern_absent(self):
        record = _record(output_text="SELECT DISTINCT o.id FROM orders o")
        result = evaluate_check(_check("output_pattern", pattern="GROUP BY", regex=True), record)
        assert result.verdict == VERDICT_FAIL

    def test_case_insensitive(self):
        record = _record(output_text="group by o.id")
        result = evaluate_check(_check("output_pattern", pattern="GROUP BY", regex=True), record)
        assert result.verdict == VERDICT_PASS

    def test_negate_pass_when_absent(self):
        record = _record(output_text="GROUP BY o.id")
        result = evaluate_check(_check("output_pattern", pattern="PostgreSQL.*18", regex=True, negate=True), record)
        assert result.verdict == VERDICT_PASS

    def test_negate_fail_when_present(self):
        record = _record(output_text="Use PostgreSQL 18 async I/O for this")
        result = evaluate_check(_check("output_pattern", pattern="PostgreSQL.*18", regex=True, negate=True), record)
        assert result.verdict == VERDICT_FAIL


class TestNoEscalation:
    def test_pass_no_questions(self):
        record = _record(open_questions=[])
        result = evaluate_check(_check("no_escalation"), record)
        assert result.verdict == VERDICT_PASS

    def test_fail_with_questions(self):
        record = _record(open_questions=["Which schema should I use?"])
        result = evaluate_check(_check("no_escalation"), record)
        assert result.verdict == VERDICT_FAIL


class TestTestPassed:
    def test_pass(self):
        record = _record(verification=[VerificationEntry("test suite passes", "pass", "npm test green")])
        result = evaluate_check(_check("test_passed", item="test suite"), record)
        assert result.verdict == VERDICT_PASS

    def test_fail_item_not_found(self):
        record = _record(verification=[])
        result = evaluate_check(_check("test_passed", item="test suite"), record)
        assert result.verdict == VERDICT_FAIL

    def test_fail_item_not_pass(self):
        record = _record(verification=[VerificationEntry("test suite passes", "fail", "")])
        result = evaluate_check(_check("test_passed", item="test suite"), record)
        assert result.verdict == VERDICT_FAIL


class TestHumanReview:
    def test_always_not_evaluated(self):
        record = _record()
        result = evaluate_check(_check("human_review"), record)
        assert result.verdict == VERDICT_NOT_EVALUATED


class TestUnknownType:
    def test_unknown_type_not_evaluated(self):
        record = _record()
        result = evaluate_check(_check("nonexistent_check_type"), record)
        assert result.verdict == VERDICT_NOT_EVALUATED
