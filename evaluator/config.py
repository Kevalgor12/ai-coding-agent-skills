"""
Central path and constant definitions for the evaluation runner.
Import from here rather than hardcoding paths in individual modules.
"""

from pathlib import Path

# Repo root — two levels up from this file (evaluator/config.py → evaluator/ → repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent

SKILLS_DIR        = REPO_ROOT / "skills"
SCENARIOS_DIR     = REPO_ROOT / "evaluations" / "scenarios"
EXPECTED_DIR      = REPO_ROOT / "evaluations" / "expected-behaviors"
ASSERTIONS_DIR    = Path(__file__).resolve().parent / "assertions"
FIXTURES_DIR      = Path(__file__).resolve().parent / "fixtures"
ADAPTERS_LIB_DIR  = REPO_ROOT / "adapters" / "lib"

# Where per-run evidence and reports are written
RESULTS_DIR       = REPO_ROOT / "evaluations" / "results"

# Supported adapter target names
ADAPTER_CLAUDE_CODE = "claude-code"
ADAPTER_MOCK        = "mock"

# Assertion evaluation methods
METHOD_OBSERVATION   = "observation"   # machine-checkable against run record + FS
METHOD_HUMAN_REVIEW  = "human_review"  # requires a human reviewer
METHOD_STRUCTURAL    = "structural"    # pure run-record structure check

# Assertion verdict values (per scoring.md)
VERDICT_PASS            = "pass"
VERDICT_FAIL            = "fail"
VERDICT_NOT_APPLICABLE  = "not-applicable"
VERDICT_NOT_EVALUATED   = "not-evaluated"  # human_review pending or adapter blocked

# Scenario-level outcomes (mirrors the six-status model from state-and-contract.md)
OUTCOME_COMPLETE  = "complete"
OUTCOME_PARTIAL   = "partial"
OUTCOME_FAILED    = "failed"
OUTCOME_BLOCKED   = "blocked"

# Assertion weights
WEIGHT_CRITICAL = "critical"
WEIGHT_MAJOR    = "major"
WEIGHT_MINOR    = "minor"

# Promotion gate thresholds
PROMOTION_MIN_MAJOR_PASS_RATE = 2 / 3   # ≥ 2/3 of major assertions must pass
PROMOTION_REQUIRED_REVIEWS    = 1        # at least 1 human reviewer sign-off
