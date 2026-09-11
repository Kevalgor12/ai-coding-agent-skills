"""
Claude Code adapter — runs the `claude` CLI on an isolated fixture directory and
parses the structured run record emitted by the agent.

Agent-specific execution is isolated here so the evaluator core (checker, scorer,
reporter) stays vendor-neutral.

Run record protocol
-------------------
The adapter invokes Claude Code with:

  claude --print -- "<task>"

and captures stdout.  The agent is expected to emit a structured JSON block
delimited by markers:

  <<<EVAL_RUN_RECORD>>>
  { ... JSON matching RunRecord schema ... }
  <<<END_EVAL_RUN_RECORD>>>

If that block is absent the adapter falls back to heuristic parsing (grepping
stdout for keywords), marks parse_errors, and returns a best-effort RunRecord.

Fixture setup
-------------
The adapter copies (or symlinks) the fixture skeleton for the scenario into a
fresh temp directory inside the provided fixture_dir, ensuring each run gets an
isolated, reproducible starting state.

Timeout
-------
The default is 300 s.  Increase for multi-skill scenarios.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from ..models import (
    LedgerEntry,
    RoutingEntry,
    RunRecord,
    Scenario,
    VerificationEntry,
)
from .base import AgentAdapter


_RECORD_START = "<<<EVAL_RUN_RECORD>>>"
_RECORD_END   = "<<<END_EVAL_RUN_RECORD>>>"
_RECORD_RE    = re.compile(
    r"<<<EVAL_RUN_RECORD>>>\s*(.*?)\s*<<<END_EVAL_RUN_RECORD>>>",
    re.DOTALL,
)


def _try_extract_json(text: str) -> dict | None:
    m = _RECORD_RE.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def _routing_from_dict(d: dict) -> RoutingEntry:
    return RoutingEntry(skill_id=d.get("skill_id", ""), reason=d.get("reason", ""))


def _ledger_from_dict(d: dict) -> LedgerEntry:
    return LedgerEntry(
        entry_type=d.get("entry_type", ""),
        skill_id=d.get("skill_id", ""),
        status=d.get("status", ""),
        reason=d.get("reason", ""),
        details=d.get("details", {}),
    )


def _verification_from_dict(d: dict) -> VerificationEntry:
    return VerificationEntry(
        item=d.get("item", ""),
        status=d.get("status", ""),
        evidence=d.get("evidence", ""),
    )


def _parse_run_record(scenario_id: str, task: str, raw: str, fixture_dir: Path) -> RunRecord:
    """Parse agent stdout into a RunRecord. Falls back to heuristic on missing block."""
    parse_errors: list[str] = []
    data = _try_extract_json(raw)

    if data is None:
        parse_errors.append(
            "No structured run record block found in agent output. "
            "Heuristic parse only — most assertion checks will be not-evaluated."
        )
        return RunRecord(
            scenario_id=scenario_id,
            task=task,
            status="",
            output_text=raw,
            raw_agent_output=raw,
            fixture_dir=fixture_dir,
            parse_errors=parse_errors,
        )

    return RunRecord(
        scenario_id=scenario_id,
        task=task,
        status=data.get("status", ""),
        routing_selected=[_routing_from_dict(r) for r in data.get("routing_selected", [])],
        routing_excluded=[_routing_from_dict(r) for r in data.get("routing_excluded", [])],
        ledger=[_ledger_from_dict(e) for e in data.get("ledger", [])],
        verification=[_verification_from_dict(v) for v in data.get("verification", [])],
        commands_run=data.get("commands_run", []),
        files_changed=data.get("files_changed", []),
        output_text=data.get("output_text", raw),
        outputs=data.get("outputs", {}),
        open_questions=data.get("open_questions", []),
        unverified_claims=data.get("unverified_claims", []),
        findings=data.get("findings", []),
        fixture_dir=fixture_dir,
        raw_agent_output=raw,
        parse_errors=parse_errors,
    )


class ClaudeCodeAdapter(AgentAdapter):
    """
    Adapter that drives Claude Code (the `claude` CLI) on isolated fixture repos.

    The adapter:
    1. Copies the scenario fixture skeleton into a fresh temp dir.
    2. Injects the skill invocation context (CLAUDE.md / skill prompt prefix).
    3. Runs `claude --print -- "<task>"` with a timeout.
    4. Parses the structured run record from stdout.
    5. Cleans up the temp dir (unless `keep_fixtures=True`).
    """

    def __init__(
        self,
        *,
        claude_bin: str = "claude",
        keep_fixtures: bool = False,
    ) -> None:
        self._claude_bin = claude_bin
        self._keep_fixtures = keep_fixtures

    @property
    def name(self) -> str:
        return "claude-code"

    def _prepare_workspace(self, scenario: Scenario, fixture_dir: Path) -> Path:
        """Copy fixture skeleton to a fresh temp directory and return the path."""
        workspace = Path(tempfile.mkdtemp(prefix=f"eval_{scenario.scenario_id}_"))

        # If a fixture skeleton exists for this scenario, copy it
        skeleton = fixture_dir / scenario.scenario_id
        if skeleton.exists():
            shutil.copytree(skeleton, workspace, dirs_exist_ok=True)

        return workspace

    def _build_prompt(self, scenario: Scenario, skill_ids: list[str]) -> str:
        """Build the full prompt to pass to claude --print."""
        skill_context = ", ".join(skill_ids) if skill_ids else "(auto-detect)"
        return (
            f"[EVAL] scenario={scenario.scenario_id} skills={skill_context}\n\n"
            f"{scenario.task}\n\n"
            "After completing the task, emit a structured run record as follows:\n"
            f"{_RECORD_START}\n"
            '{"status": "complete|partial|blocked|failed", '
            '"routing_selected": [{"skill_id": "SK-...", "reason": "..."}], '
            '"routing_excluded": [{"skill_id": "SK-...", "reason": "..."}], '
            '"ledger": [{"entry_type": "invocation", "skill_id": "SK-...", "status": "complete", "reason": "..."}], '
            '"verification": [{"item": "...", "status": "pass|fail", "evidence": "..."}], '
            '"commands_run": ["..."], '
            '"files_changed": ["..."], '
            '"output_text": "...", '
            '"open_questions": [], '
            '"unverified_claims": [], '
            '"findings": []}\n'
            f"{_RECORD_END}"
        )

    def run(
        self,
        scenario: Scenario,
        skill_ids: list[str],
        fixture_dir: Path,
        *,
        timeout: int = 300,
    ) -> RunRecord:
        workspace = self._prepare_workspace(scenario, fixture_dir)
        try:
            prompt = self._build_prompt(scenario, skill_ids)
            result = subprocess.run(
                [self._claude_bin, "--print", "--", prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(workspace),
            )
            raw = result.stdout
            if result.returncode != 0:
                raw += f"\n[stderr]: {result.stderr}"

            record = _parse_run_record(scenario.scenario_id, scenario.task, raw, workspace)

            # Supplement files_changed from actual FS diff when record is sparse
            if not record.files_changed and workspace.exists():
                changed = [
                    str(p.relative_to(workspace))
                    for p in workspace.rglob("*")
                    if p.is_file()
                ]
                if changed:
                    record.files_changed = changed

            return record
        finally:
            if not self._keep_fixtures and workspace.exists():
                shutil.rmtree(workspace, ignore_errors=True)
