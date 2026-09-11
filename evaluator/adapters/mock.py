"""
Mock adapter — returns a pre-scripted RunRecord without invoking any agent.

Use cases:
- Self-testing the evaluator checker/scorer pipeline
- CI smoke tests that must not require a live agent
- Baseline regression: "does the evaluator produce the right score for a known good run?"

Usage:
    record = RunRecord(scenario_id="S01", task="...", status="complete",
                       routing_selected=[RoutingEntry("SK-DB-001", "primary")],
                       ...)
    adapter = MockAdapter(record)
    result = adapter.run(scenario, skill_ids, fixture_dir)
    assert result is record  # same object returned
"""

from __future__ import annotations

from pathlib import Path

from ..models import RunRecord, Scenario, RoutingEntry, LedgerEntry, VerificationEntry
from .base import AgentAdapter


class MockAdapter(AgentAdapter):
    """
    Returns a caller-supplied RunRecord (or a minimal auto-generated one) without
    running any agent or touching the filesystem.
    """

    def __init__(self, run_record: RunRecord | None = None) -> None:
        self._record = run_record

    @property
    def name(self) -> str:
        return "mock"

    def run(
        self,
        scenario: Scenario,
        skill_ids: list[str],
        fixture_dir: Path,
        *,
        timeout: int = 300,
    ) -> RunRecord:
        if self._record is not None:
            return self._record

        # Auto-generate a minimal "all skills routed, status=complete" record.
        # This gives caller a valid RunRecord without having to construct one manually.
        routing = [RoutingEntry(skill_id=sid, reason="mock-auto") for sid in skill_ids]
        ledger = [
            LedgerEntry(
                entry_type="invocation",
                skill_id=sid,
                status="complete",
                reason="mock-auto",
            )
            for sid in skill_ids
        ]
        return RunRecord(
            scenario_id=scenario.scenario_id,
            task=scenario.task,
            status="complete",
            routing_selected=routing,
            routing_excluded=[],
            ledger=ledger,
            verification=[],
            commands_run=[],
            files_changed=[],
            output_text="[mock output]",
            outputs={},
            open_questions=[],
            unverified_claims=[],
            findings=[],
            fixture_dir=fixture_dir,
            raw_agent_output="",
            parse_errors=[],
        )
