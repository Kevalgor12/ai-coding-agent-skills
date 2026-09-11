"""Tests for evaluator/coverage.py"""

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from evaluator.coverage import build_coverage_report


class TestBuildCoverageReport:
    def test_returns_coverage_report(self):
        report = build_coverage_report()
        assert report.total_skills > 0

    def test_counts_sum_correctly(self):
        report = build_coverage_report()
        assert report.covered_primary + report.covered_boundary + report.uncovered == report.total_skills

    def test_has_skill_entries(self):
        report = build_coverage_report()
        assert len(report.by_skill) == report.total_skills

    def test_sk_tech_postgresql_has_primary_coverage(self):
        report = build_coverage_report()
        pg = next((s for s in report.by_skill if s.skill_id == "SK-TECH-postgresql"), None)
        if pg is None:
            pytest.skip("SK-TECH-postgresql not in library")
        assert pg.coverage_depth == "primary", f"Expected primary, got {pg.coverage_depth}"

    def test_sk_conv_001_has_coverage(self):
        report = build_coverage_report()
        skill = next((s for s in report.by_skill if s.skill_id == "SK-CONV-001"), None)
        if skill is None:
            pytest.skip("SK-CONV-001 not in library")
        assert skill.has_any_scenario

    def test_total_skills_near_88(self):
        report = build_coverage_report()
        assert 80 <= report.total_skills <= 100, f"Expected ~88 skills, got {report.total_skills}"
