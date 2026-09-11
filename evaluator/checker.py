"""
Assertion checker — evaluates machine-checkable AssertionCheck predicates against a RunRecord.

Each check type corresponds to an observable property of the run:

  routing_contains    skill_id present in routing_selected
  routing_excludes    skill_id absent from routing_selected
  ledger_contains     skill_id present in ledger with optional status filter
  command_run         regex/substring found in commands_run
  file_changed        path substring found in files_changed
  status_is           run record status equals value
  output_pattern      regex found in output_text
  no_escalation       open_questions is empty
  test_passed         VerificationEntry with item matching pattern + status==pass
  human_review        always returns not-evaluated (requires human)

These are deliberately low-level primitives. An assertion can compose multiple
checks; the assertion fails if any check fails (all checks must pass).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .config import (
    VERDICT_FAIL,
    VERDICT_NOT_EVALUATED,
    VERDICT_PASS,
)
from .models import AssertionCheck, RunRecord


@dataclass
class CheckResult:
    verdict: str       # pass | fail | not-evaluated
    evidence: str      # human-readable description of what was inspected


def _routing_selected_ids(record: RunRecord) -> set[str]:
    return {r.skill_id for r in record.routing_selected}


def check_routing_contains(check: AssertionCheck, record: RunRecord) -> CheckResult:
    skill_id = check.params.get("skill_id", "")
    selected = _routing_selected_ids(record)
    if skill_id in selected:
        return CheckResult(VERDICT_PASS, f"{skill_id} found in routing_selected")
    return CheckResult(VERDICT_FAIL, f"{skill_id} not in routing_selected (found: {sorted(selected)})")


def check_routing_excludes(check: AssertionCheck, record: RunRecord) -> CheckResult:
    skill_id = check.params.get("skill_id", "")
    selected = _routing_selected_ids(record)
    if skill_id not in selected:
        return CheckResult(VERDICT_PASS, f"{skill_id} absent from routing_selected")
    return CheckResult(VERDICT_FAIL, f"{skill_id} unexpectedly present in routing_selected")


def check_ledger_contains(check: AssertionCheck, record: RunRecord) -> CheckResult:
    skill_id = check.params.get("skill_id", "")
    required_status = check.params.get("status", "")  # optional status filter

    matching = [e for e in record.ledger if e.skill_id == skill_id]
    if not matching:
        return CheckResult(VERDICT_FAIL, f"No ledger entry for {skill_id}")

    if required_status:
        status_match = [e for e in matching if e.status == required_status]
        if not status_match:
            found_statuses = [e.status for e in matching]
            return CheckResult(
                VERDICT_FAIL,
                f"{skill_id} in ledger but status {found_statuses!r} != required {required_status!r}",
            )
        return CheckResult(VERDICT_PASS, f"{skill_id} ledger entry with status={required_status}")

    return CheckResult(VERDICT_PASS, f"{skill_id} found in ledger (status: {matching[0].status!r})")


def check_command_run(check: AssertionCheck, record: RunRecord) -> CheckResult:
    pattern = check.params.get("pattern", "")
    use_regex = check.params.get("regex", False)

    for cmd in record.commands_run:
        matched = (
            bool(re.search(pattern, cmd)) if use_regex else (pattern in cmd)
        )
        if matched:
            return CheckResult(VERDICT_PASS, f"Command matched {pattern!r}: {cmd!r}")

    return CheckResult(
        VERDICT_FAIL,
        f"No command matching {pattern!r} in commands_run ({len(record.commands_run)} entries)",
    )


def check_file_changed(check: AssertionCheck, record: RunRecord) -> CheckResult:
    path_substr = check.params.get("path", "")
    use_regex = check.params.get("regex", False)

    for f in record.files_changed:
        matched = (
            bool(re.search(path_substr, f)) if use_regex else (path_substr in f)
        )
        if matched:
            return CheckResult(VERDICT_PASS, f"File matched {path_substr!r}: {f!r}")

    return CheckResult(
        VERDICT_FAIL,
        f"No file matching {path_substr!r} in files_changed ({len(record.files_changed)} entries)",
    )


def check_status_is(check: AssertionCheck, record: RunRecord) -> CheckResult:
    expected = check.params.get("value", "")
    if record.status == expected:
        return CheckResult(VERDICT_PASS, f"run status == {expected!r}")
    return CheckResult(VERDICT_FAIL, f"run status {record.status!r} != expected {expected!r}")


def check_output_pattern(check: AssertionCheck, record: RunRecord) -> CheckResult:
    pattern = check.params.get("pattern", "")
    use_regex = check.params.get("regex", True)

    text = record.output_text
    if use_regex:
        matched = bool(re.search(pattern, text, re.IGNORECASE))
    else:
        matched = pattern.lower() in text.lower()

    if matched:
        return CheckResult(VERDICT_PASS, f"output matched {pattern!r}")
    return CheckResult(VERDICT_FAIL, f"output did not match {pattern!r}")


def check_no_escalation(check: AssertionCheck, record: RunRecord) -> CheckResult:
    if not record.open_questions:
        return CheckResult(VERDICT_PASS, "no open_questions (no escalation)")
    return CheckResult(
        VERDICT_FAIL,
        f"{len(record.open_questions)} open question(s): {record.open_questions[:3]}",
    )


def check_test_passed(check: AssertionCheck, record: RunRecord) -> CheckResult:
    item_pattern = check.params.get("item", "")
    use_regex = check.params.get("regex", False)

    matches = []
    for v in record.verification:
        hit = (
            bool(re.search(item_pattern, v.item)) if use_regex else (item_pattern in v.item)
        )
        if hit:
            matches.append(v)

    if not matches:
        return CheckResult(
            VERDICT_FAIL,
            f"No verification entry matching item={item_pattern!r}",
        )

    failed = [v for v in matches if v.status != "pass"]
    if failed:
        detail = "; ".join(f"{v.item}={v.status}" for v in failed[:3])
        return CheckResult(VERDICT_FAIL, f"Verification item(s) did not pass: {detail}")

    return CheckResult(VERDICT_PASS, f"All matching verification entries passed: {[v.item for v in matches]}")


def check_human_review(check: AssertionCheck, record: RunRecord) -> CheckResult:
    return CheckResult(VERDICT_NOT_EVALUATED, "requires human review")


# Registry maps check type → handler function
_HANDLERS = {
    "routing_contains":  check_routing_contains,
    "routing_excludes":  check_routing_excludes,
    "ledger_contains":   check_ledger_contains,
    "command_run":       check_command_run,
    "file_changed":      check_file_changed,
    "status_is":         check_status_is,
    "output_pattern":    check_output_pattern,
    "no_escalation":     check_no_escalation,
    "test_passed":       check_test_passed,
    "human_review":      check_human_review,
}


def evaluate_check(check: AssertionCheck, record: RunRecord) -> CheckResult:
    """Dispatch a single AssertionCheck to its handler."""
    handler = _HANDLERS.get(check.type)
    if handler is None:
        return CheckResult(
            VERDICT_NOT_EVALUATED,
            f"Unknown check type {check.type!r} — not evaluated",
        )
    try:
        return handler(check, record)
    except Exception as exc:
        return CheckResult(VERDICT_FAIL, f"Check raised {type(exc).__name__}: {exc}")
