"""
Coverage analysis — determines which skills have scenarios and assertion YAMLs.

Reads:
  - all skill.yaml files under skills/
  - all scenario Markdown files (via loader)
  - assertion YAML existence in evaluator/assertions/

Produces a CoverageReport summarising primary/boundary/no-coverage distribution.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .config import ASSERTIONS_DIR, SKILLS_DIR
from .loader import load_all_scenarios
from .models import CoverageReport, SkillCoverage


def _load_skill_meta() -> list[dict]:
    """Load id, slug, layer, domain from every skill.yaml."""
    # Prefer the adapters/lib loader if importable; fall back to manual YAML parse.
    try:
        _lib_dir = Path(__file__).resolve().parent.parent / "adapters" / "lib"
        if str(_lib_dir) not in sys.path:
            sys.path.insert(0, str(_lib_dir))
        from skill_loader import load  # type: ignore
        skills = []
        for p in sorted(SKILLS_DIR.rglob("skill.yaml")):
            try:
                s = load(p.parent)  # skill_loader.load() takes the directory
                skills.append({
                    "id": s.id,
                    "slug": s.slug,
                    "name": s.name,
                    "layer": int(s.yaml_data.get("layer", 0)),
                    "domain": s.yaml_data.get("domain", "unknown"),
                })
            except Exception:
                pass
        return skills
    except ImportError:
        pass

    # Fallback: raw YAML parse
    import yaml  # type: ignore
    skills = []
    for p in sorted(SKILLS_DIR.rglob("skill.yaml")):
        if p.is_dir():
            continue
        try:
            data = yaml.safe_load(p.read_text())
            skills.append({
                "id": data.get("id", ""),
                "slug": data.get("slug", ""),
                "name": data.get("name", ""),
                "layer": int(data.get("layer", 0)),
                "domain": data.get("domain", "unknown"),
            })
        except Exception:
            pass
    return skills


def build_coverage_report() -> CoverageReport:
    """Scan all skills and scenarios and return a CoverageReport."""
    skill_metas = _load_skill_meta()
    scenarios = load_all_scenarios()

    # Build reverse index: skill_id → scenario sets
    must_activate_map:     dict[str, list[str]] = {}
    must_not_activate_map: dict[str, list[str]] = {}
    acceptable_map:        dict[str, list[str]] = {}

    for sc in scenarios:
        sid = sc.scenario_id
        for skill_id in sc.activation_set.must_activate:
            must_activate_map.setdefault(skill_id, []).append(sid)
        for skill_id in sc.activation_set.must_not_activate:
            must_not_activate_map.setdefault(skill_id, []).append(sid)
        for skill_id in sc.activation_set.acceptable_either:
            acceptable_map.setdefault(skill_id, []).append(sid)

    by_skill: list[SkillCoverage] = []
    for meta in skill_metas:
        skill_id = meta["id"]
        has_yaml = (ASSERTIONS_DIR / f"S01.yaml").exists()  # check dir exists at minimum

        # Check whether any assertion YAML references this skill or if there's a dedicated file
        # We do a lightweight: does any S*.yaml exist in assertions dir?
        has_assertion_yaml = any(
            True
            for p in ASSERTIONS_DIR.glob("S*.yaml")
        ) if ASSERTIONS_DIR.exists() else False
        # More precise: does the skill appear in must_activate for a scenario that has a YAML?
        must_act_scenarios = must_activate_map.get(skill_id, [])
        has_assertion_yaml = any(
            (ASSERTIONS_DIR / f"{sid}.yaml").exists()
            for sid in must_act_scenarios
        )

        cov = SkillCoverage(
            skill_id=skill_id,
            skill_slug=meta["slug"],
            skill_name=meta["name"],
            layer=meta["layer"],
            domain=meta["domain"],
            scenarios_as_must_activate=must_activate_map.get(skill_id, []),
            scenarios_as_must_not_activate=must_not_activate_map.get(skill_id, []),
            scenarios_as_acceptable=acceptable_map.get(skill_id, []),
            has_any_scenario=(
                bool(must_activate_map.get(skill_id))
                or bool(must_not_activate_map.get(skill_id))
                or bool(acceptable_map.get(skill_id))
            ),
            has_assertion_yaml=has_assertion_yaml,
        )
        by_skill.append(cov)

    covered_primary  = sum(1 for s in by_skill if s.coverage_depth == "primary")
    covered_boundary = sum(1 for s in by_skill if s.coverage_depth == "boundary")
    uncovered        = sum(1 for s in by_skill if s.coverage_depth == "none")
    uncovered_skills = [s for s in by_skill if s.coverage_depth == "none"]

    return CoverageReport(
        total_skills=len(by_skill),
        covered_primary=covered_primary,
        covered_boundary=covered_boundary,
        uncovered=uncovered,
        by_skill=by_skill,
        uncovered_skills=uncovered_skills,
    )
