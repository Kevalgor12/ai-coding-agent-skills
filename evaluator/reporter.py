"""
Reporter — writes evaluation results as structured JSON and human-readable Markdown.

Output paths (per RESULTS_DIR):
  results/{scenario_id}/run_{timestamp}.json       full machine-readable record
  results/{scenario_id}/run_{timestamp}.md         human-readable summary
  results/coverage_report.md                       skill coverage table
  results/promotion_decisions.json                 all promotion gate results
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import RESULTS_DIR, VERDICT_FAIL, VERDICT_NOT_EVALUATED
from .models import (
    AssertionVerdict,
    CoverageReport,
    PromotionDecision,
    ScenarioScore,
    SkillCoverage,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _dataclass_to_dict(obj: Any) -> Any:
    """Convert dataclass (possibly nested) to plain dict, skipping Path objects."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _dataclass_to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, (list, tuple)):
        return [_dataclass_to_dict(i) for i in obj]
    if isinstance(obj, Path):
        return str(obj)
    return obj


def _verdict_icon(verdict: str) -> str:
    return {"pass": "PASS", "fail": "FAIL", "not-evaluated": "PEND", "not-applicable": "N/A"}.get(verdict, verdict)


# ---------------------------------------------------------------------------
# Scenario report
# ---------------------------------------------------------------------------

def write_scenario_report(score: ScenarioScore, results_dir: Path = RESULTS_DIR) -> tuple[Path, Path]:
    """Write JSON + Markdown reports for one scenario score. Returns (json_path, md_path)."""
    timestamp = _now_iso()
    scenario_dir = _ensure_dir(results_dir / score.scenario.scenario_id)

    # --- JSON ---
    json_path = scenario_dir / f"run_{timestamp}.json"
    payload = {
        "schema_version": "1.0",
        "generated": timestamp,
        "scenario_id": score.scenario.scenario_id,
        "scenario_name": score.scenario.name,
        "outcome": score.outcome,
        "critical_passed": score.critical_passed,
        "critical_total": score.critical_total,
        "major_passed": score.major_passed,
        "major_total": score.major_total,
        "minor_passed": score.minor_passed,
        "minor_total": score.minor_total,
        "has_human_review_pending": score.has_human_review_pending,
        "run_record": {
            "scenario_id": score.run_record.scenario_id,
            "status": score.run_record.status,
            "routing_selected": [
                {"skill_id": r.skill_id, "reason": r.reason}
                for r in score.run_record.routing_selected
            ],
            "files_changed": score.run_record.files_changed,
            "commands_run": score.run_record.commands_run,
            "open_questions": score.run_record.open_questions,
            "parse_errors": score.run_record.parse_errors,
        },
        "verdicts": [
            {
                "assertion_id": v.assertion.assertion_id,
                "number": v.assertion.number,
                "weight": v.assertion.weight,
                "verdict": v.verdict,
                "evidence": v.evidence,
                "reason": v.reason,
                "needs_human_review": v.needs_human_review,
            }
            for v in score.verdicts
        ],
    }
    json_path.write_text(json.dumps(payload, indent=2))

    # --- Markdown ---
    md_path = scenario_dir / f"run_{timestamp}.md"
    lines = [
        f"# {score.scenario.scenario_id} — {score.scenario.name}",
        f"",
        f"**Outcome:** `{score.outcome.upper()}`  ",
        f"**Run:** {timestamp}  ",
        f"**Critical:** {score.critical_passed}/{score.critical_total}  ",
        f"**Major:** {score.major_passed}/{score.major_total}  ",
        f"**Minor:** {score.minor_passed}/{score.minor_total}  ",
        f"",
        "## Assertions",
        "",
        "| # | Weight | Verdict | Summary |",
        "|---|--------|---------|---------|",
    ]
    for v in score.verdicts:
        icon = _verdict_icon(v.verdict)
        lines.append(
            f"| {v.assertion.number} | {v.assertion.weight} | {icon} | {v.assertion.prose[:80]} |"
        )

    if score.failed_assertions:
        lines += ["", "## Failed assertions", ""]
        for v in score.failed_assertions:
            lines += [
                f"### {v.assertion.assertion_id} ({v.assertion.weight})",
                "",
                f"**Prose:** {v.assertion.prose}",
                "",
                f"**Evidence:**",
                "```",
                v.evidence,
                "```",
                "",
            ]

    if score.not_evaluated:
        lines += ["", "## Pending human review", ""]
        for v in score.not_evaluated:
            if v.needs_human_review:
                lines.append(f"- **{v.assertion.assertion_id}**: {v.assertion.prose[:100]}")

    if score.run_record.parse_errors:
        lines += ["", "## Parser warnings", ""]
        for err in score.run_record.parse_errors:
            lines.append(f"- {err}")

    md_path.write_text("\n".join(lines) + "\n")
    return json_path, md_path


# ---------------------------------------------------------------------------
# Coverage report
# ---------------------------------------------------------------------------

def write_coverage_report(report: CoverageReport, results_dir: Path = RESULTS_DIR) -> Path:
    """Write a Markdown coverage table to results/coverage_report.md."""
    _ensure_dir(results_dir)
    out = results_dir / "coverage_report.md"

    lines = [
        "# Skill Coverage Report",
        "",
        f"**Total skills:** {report.total_skills}  ",
        f"**Primary coverage:** {report.covered_primary} ({report.covered_primary / max(report.total_skills,1):.0%})  ",
        f"**Boundary coverage:** {report.covered_boundary}  ",
        f"**Uncovered:** {report.uncovered}  ",
        "",
        "## Coverage by skill",
        "",
        "| Skill ID | Slug | Layer | Domain | Depth | Primary scenarios | Assertion YAML |",
        "|----------|------|-------|--------|-------|-------------------|----------------|",
    ]
    for s in report.by_skill:
        scenarios = ", ".join(s.scenarios_as_must_activate[:3]) or "—"
        yaml_flag = "yes" if s.has_assertion_yaml else "no"
        lines.append(
            f"| {s.skill_id} | {s.skill_slug} | {s.layer} | {s.domain} "
            f"| {s.coverage_depth} | {scenarios} | {yaml_flag} |"
        )

    if report.uncovered_skills:
        lines += ["", "## Uncovered skills (no scenarios at all)", ""]
        for s in report.uncovered_skills:
            lines.append(f"- **{s.skill_id}** `{s.skill_slug}` (L{s.layer}, {s.domain})")

    out.write_text("\n".join(lines) + "\n")
    return out


# ---------------------------------------------------------------------------
# Promotion decisions report
# ---------------------------------------------------------------------------

def write_promotion_report(
    decisions: list[PromotionDecision],
    results_dir: Path = RESULTS_DIR,
) -> Path:
    """Write results/promotion_decisions.json."""
    _ensure_dir(results_dir)
    out = results_dir / "promotion_decisions.json"

    payload = {
        "schema_version": "1.0",
        "generated": _now_iso(),
        "decisions": [
            {
                "skill_id": d.skill_id,
                "skill_slug": d.skill_slug,
                "eligible": d.eligible,
                "blocking_reason": d.blocking_reason,
                "gates": [
                    {"name": g.name, "satisfied": g.satisfied, "details": g.details}
                    for g in d.gates
                ],
            }
            for d in decisions
        ],
    }
    out.write_text(json.dumps(payload, indent=2))
    return out
