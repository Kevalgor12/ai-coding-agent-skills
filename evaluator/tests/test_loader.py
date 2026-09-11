"""Tests for evaluator/loader.py"""

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from evaluator.loader import load_all_scenarios, load_assertions, load_scenario
from evaluator.config import SCENARIOS_DIR, EXPECTED_DIR, ASSERTIONS_DIR


class TestLoadScenario:
    def test_load_s01(self):
        path = next(SCENARIOS_DIR.glob("S01-*.md"), None)
        if path is None:
            pytest.skip("S01 scenario file not found")
        sc = load_scenario(path)
        assert sc.scenario_id == "S01"
        assert sc.name
        assert sc.task

    def test_activation_set_extracted(self):
        path = next(SCENARIOS_DIR.glob("S02-*.md"), None)
        if path is None:
            pytest.skip("S02 scenario file not found")
        sc = load_scenario(path)
        assert "SK-CONV-001" in sc.activation_set.must_activate

    def test_must_not_activate_extracted(self):
        path = next(SCENARIOS_DIR.glob("S02-*.md"), None)
        if path is None:
            pytest.skip("S02 scenario file not found")
        sc = load_scenario(path)
        assert "SK-CONV-008" in sc.activation_set.must_not_activate

    def test_load_all_scenarios(self):
        scenarios = load_all_scenarios()
        assert len(scenarios) >= 1, "Should load at least one scenario"

    def test_scenario_ids_unique(self):
        scenarios = load_all_scenarios()
        ids = [s.scenario_id for s in scenarios]
        assert len(ids) == len(set(ids)), "Scenario IDs must be unique"

    def test_16_scenarios(self):
        scenarios = load_all_scenarios()
        assert len(scenarios) == 16, f"Expected 16 scenarios, got {len(scenarios)}"


class TestLoadAssertions:
    def test_load_s01_assertions(self):
        assertions = load_assertions("S01")
        assert len(assertions) == 11, f"S01 should have 11 assertions, got {len(assertions)}"

    def test_assertion_weights(self):
        assertions = load_assertions("S01")
        weights = {a.weight for a in assertions}
        assert "critical" in weights
        assert "major" in weights or "minor" in weights

    def test_assertion_ids_unique(self):
        assertions = load_assertions("S01")
        ids = [a.assertion_id for a in assertions]
        assert len(ids) == len(set(ids))

    def test_yaml_checks_loaded(self):
        assertions = load_assertions("S01")
        # S01.yaml exists, so at least some assertions should have machine checks
        with_checks = [a for a in assertions if a.checks]
        assert len(with_checks) > 0, "S01 YAML should provide some machine checks"

    def test_s02_assertions(self):
        assertions = load_assertions("S02")
        assert len(assertions) == 7

    def test_missing_scenario_returns_empty(self):
        assertions = load_assertions("S99")
        assert assertions == []
