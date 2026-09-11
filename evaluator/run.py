#!/usr/bin/env python3
"""
Evaluation runner CLI.

Usage
-----
# Run one scenario with the mock adapter (no live agent required)
python3 evaluator/run.py --scenario S01 --adapter mock

# Run all scenarios with the mock adapter
python3 evaluator/run.py --adapter mock

# Run a specific scenario with Claude Code (requires `claude` CLI in PATH)
python3 evaluator/run.py --scenario S12 --adapter claude-code

# Coverage report only (no run)
python3 evaluator/run.py --coverage

# Promotion gate check for one skill
python3 evaluator/run.py --promote SK-DB-001 --adapter mock

Flags
-----
--scenario  S01, S12, ...  (default: all)
--adapter   mock | claude-code  (default: mock)
--coverage  print coverage report and exit
--promote   SKILL_ID  check promotion gate for one skill
--timeout   seconds per scenario run (default: 300)
--keep      keep fixture workspaces after run (for debugging)
--results   path to results dir (default: evaluations/results/)
--json      emit machine-readable JSON to stdout
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running from repo root: python3 evaluator/run.py
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from evaluator.adapters.claude_code import ClaudeCodeAdapter
from evaluator.adapters.mock import MockAdapter
from evaluator.config import (
    ADAPTER_CLAUDE_CODE,
    ADAPTER_MOCK,
    FIXTURES_DIR,
    RESULTS_DIR,
)
from evaluator.coverage import build_coverage_report
from evaluator.loader import load_all_scenarios, load_assertions
from evaluator.promotion import evaluate_promotion
from evaluator.reporter import write_coverage_report, write_promotion_report, write_scenario_report
from evaluator.scorer import score_scenario


# ---------------------------------------------------------------------------
# Adapter factory
# ---------------------------------------------------------------------------

def _make_adapter(name: str, *, keep: bool = False):
    if name == ADAPTER_MOCK:
        return MockAdapter()
    if name == ADAPTER_CLAUDE_CODE:
        return ClaudeCodeAdapter(keep_fixtures=keep)
    print(f"ERROR: unknown adapter {name!r} — choose 'mock' or 'claude-code'", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Core run logic
# ---------------------------------------------------------------------------

def run_scenario(scenario_id: str, adapter, timeout: int, results_dir: Path) -> dict:
    """Run one scenario and write reports. Returns a summary dict."""
    from evaluator.loader import load_scenario, SCENARIOS_DIR
    import evaluator.config as cfg

    # Load scenario
    matches = list(cfg.SCENARIOS_DIR.glob(f"{scenario_id}-*.md"))
    if not matches:
        return {"scenario_id": scenario_id, "error": "scenario file not found"}

    scenario = load_scenario(matches[0])
    assertions = load_assertions(scenario_id)

    if not assertions:
        return {
            "scenario_id": scenario_id,
            "warning": "no assertions loaded (no expected-behaviors file or empty table)",
        }

    # Run the adapter
    skill_ids = scenario.activation_set.must_activate
    record = adapter.run(scenario, skill_ids, FIXTURES_DIR, timeout=timeout)

    # Score
    score = score_scenario(scenario, assertions, record)

    # Write reports
    json_path, md_path = write_scenario_report(score, results_dir)

    return {
        "scenario_id": scenario_id,
        "outcome": score.outcome,
        "critical": f"{score.critical_passed}/{score.critical_total}",
        "major": f"{score.major_passed}/{score.major_total}",
        "minor": f"{score.minor_passed}/{score.minor_total}",
        "human_review_pending": score.has_human_review_pending,
        "report": str(md_path),
        "failed": [v.assertion.assertion_id for v in score.failed_assertions],
    }


def run_all(scenario_filter: str | None, adapter, timeout: int, results_dir: Path) -> list[dict]:
    scenarios = load_all_scenarios()
    if scenario_filter:
        scenarios = [s for s in scenarios if s.scenario_id == scenario_filter]
        if not scenarios:
            print(f"ERROR: scenario {scenario_filter!r} not found", file=sys.stderr)
            sys.exit(1)

    results = []
    for scenario in scenarios:
        summary = run_scenario(scenario.scenario_id, adapter, timeout, results_dir)
        results.append(summary)
        outcome = summary.get("outcome", summary.get("error", "?"))
        crit = summary.get("critical", "?/?")
        print(f"  {scenario.scenario_id}  {outcome:10}  crit={crit}")
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Skill Library evaluation runner")
    parser.add_argument("--scenario", metavar="SNN", help="Run only this scenario ID")
    parser.add_argument("--adapter", default="mock", choices=["mock", "claude-code"])
    parser.add_argument("--coverage", action="store_true", help="Print coverage report and exit")
    parser.add_argument("--promote", metavar="SKILL_ID", help="Check promotion gate for a skill")
    parser.add_argument("--timeout", type=int, default=300, metavar="SECS")
    parser.add_argument("--keep", action="store_true", help="Keep fixture workspaces")
    parser.add_argument("--results", default=str(RESULTS_DIR), metavar="DIR")
    parser.add_argument("--json", action="store_true", dest="emit_json")
    args = parser.parse_args()

    results_dir = Path(args.results)
    results_dir.mkdir(parents=True, exist_ok=True)

    # --- Coverage only ---
    if args.coverage:
        report = build_coverage_report()
        out = write_coverage_report(report, results_dir)
        print(f"Coverage: {report.covered_primary}/{report.total_skills} primary, "
              f"{report.covered_boundary} boundary, {report.uncovered} uncovered")
        print(f"Report written: {out}")
        if report.uncovered_skills:
            print(f"\nUncovered skills ({report.uncovered}):")
            for s in report.uncovered_skills[:20]:
                print(f"  {s.skill_id}  {s.skill_slug}  L{s.layer}")
        return

    adapter = _make_adapter(args.adapter, keep=args.keep)

    # --- Promotion gate for one skill ---
    if args.promote:
        skill_id = args.promote
        # Load all scenarios that must-activate this skill
        all_scenarios = load_all_scenarios()
        skill_scenarios = [s for s in all_scenarios if skill_id in s.activation_set.must_activate]

        if not skill_scenarios:
            print(f"No scenarios found that must-activate {skill_id}")
            sys.exit(0)

        scores = []
        for sc in skill_scenarios:
            assertions = load_assertions(sc.scenario_id)
            record = adapter.run(sc, sc.activation_set.must_activate, FIXTURES_DIR, timeout=args.timeout)
            scores.append(score_scenario(sc, assertions, record))

        decision = evaluate_promotion(skill_id, skill_id.lower(), scores)
        out = write_promotion_report([decision], results_dir)

        print(f"\nPromotion decision for {skill_id}: {'ELIGIBLE' if decision.eligible else 'NOT ELIGIBLE'}")
        for g in decision.gates:
            icon = "OK" if g.satisfied else "FAIL"
            print(f"  [{icon}] {g.name}: {g.details}")
        if not decision.eligible:
            print(f"\nBlocking gate: {decision.blocking_reason}")
        return

    # --- Run scenarios ---
    print(f"Running {'scenario ' + args.scenario if args.scenario else 'all scenarios'} "
          f"with adapter={args.adapter}")

    summaries = run_all(args.scenario, adapter, args.timeout, results_dir)

    if args.emit_json:
        print(json.dumps(summaries, indent=2))
        return

    # Summary table
    outcomes = [s.get("outcome", "error") for s in summaries]
    total = len(outcomes)
    complete = outcomes.count("complete")
    partial = outcomes.count("partial")
    failed = outcomes.count("failed")
    blocked = outcomes.count("blocked")

    print(f"\nSummary: {total} scenario(s) — "
          f"complete={complete}, partial={partial}, failed={failed}, blocked={blocked}")
    print(f"Results written to: {results_dir}")


if __name__ == "__main__":
    main()
