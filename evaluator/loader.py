"""
Load scenarios, expected-behaviors, and assertion YAML files.

The existing Markdown files in evaluations/scenarios/ and
evaluations/expected-behaviors/ are the canonical source of truth.
The assertion YAML files in evaluator/assertions/ add machine-checkable
predicate definitions alongside the prose assertions.

Parsing strategy:
- Scenario files: extract sections by heading
- Expected-behavior files: parse the Markdown assertion table
- Assertion YAMLs: load directly with PyYAML

None of these parsers require changing the existing Markdown format.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .config import (
    ASSERTIONS_DIR,
    EXPECTED_DIR,
    SCENARIOS_DIR,
)
import glob as _glob
from .models import (
    ActivationSet,
    Assertion,
    AssertionCheck,
    Scenario,
)


# ---------------------------------------------------------------------------
# Scenario loader
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
_SKILL_ID_RE = re.compile(r"`(SK-[A-Za-z0-9-]+)`")
_SCENARIO_ID_RE = re.compile(r"#\s+Scenario:\s+(S\d+)\s*—\s*(.+)")


def _extract_section(text: str, heading: str) -> str:
    """Return text between `heading` and the next same-or-higher heading."""
    pattern = re.compile(
        r"^#{1,3}\s+" + re.escape(heading) + r"\s*$(.+?)(?=^#{1,2}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(1).strip() if m else ""


def _extract_must_activate(text: str) -> list[str]:
    block_match = re.search(
        r"\*\*Must activate[:\*]*\*\*(.*?)(?=\*\*Must NOT|\*\*Uncertain|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not block_match:
        return []
    return _SKILL_ID_RE.findall(block_match.group(1))


def _extract_must_not_activate(text: str) -> list[str]:
    block_match = re.search(
        r"\*\*Must NOT activate[:\*]*\*\*(.*?)(?=\*\*Uncertain|\*\*Must activate|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not block_match:
        return []
    return _SKILL_ID_RE.findall(block_match.group(1))


def _extract_acceptable_either(text: str) -> list[str]:
    block_match = re.search(
        r"\*\*Uncertain / acceptable either way[:\*]*\*\*(.*?)(?=\*\*Must|\*\*\Z|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not block_match:
        return []
    return _SKILL_ID_RE.findall(block_match.group(1))


def _parse_header_field(text: str, field: str) -> str:
    m = re.search(r"\*\*" + re.escape(field) + r":\*\*\s*(.+)", text)
    return m.group(1).strip() if m else ""


def load_scenario(path: Path) -> Scenario:
    text = path.read_text()

    # Scenario ID + name from first heading
    id_match = _SCENARIO_ID_RE.search(text)
    scenario_id = id_match.group(1) if id_match else path.stem[:3].upper()
    name = id_match.group(2).strip() if id_match else path.stem

    category   = _parse_header_field(text, "Category")
    complexity  = _parse_header_field(text, "Complexity")
    risk_level  = _parse_header_field(text, "Risk level")
    task        = _extract_section(text, "Task")
    repo_sigs   = _extract_section(text, "Repository signals")
    act_text    = _extract_section(text, "Expected activation set")
    seq_text    = _extract_section(text, "Expected sequencing and parallelization")

    # If the scenario file has no activation set section, fall back to the
    # expected-behaviors file which always has it.
    if not act_text:
        eb_matches = list(EXPECTED_DIR.glob(f"{scenario_id}-*.md"))
        if eb_matches:
            act_text = eb_matches[0].read_text()

    activation_set = ActivationSet(
        must_activate=_extract_must_activate(act_text),
        must_not_activate=_extract_must_not_activate(act_text),
        acceptable_either=_extract_acceptable_either(act_text),
    )

    return Scenario(
        scenario_id=scenario_id,
        name=name,
        category=category,
        complexity=complexity,
        risk_level=risk_level,
        task=task,
        repository_signals=repo_sigs,
        activation_set=activation_set,
        sequencing_text=seq_text,
        source_file=path,
    )


def load_all_scenarios(scenarios_dir: Path = SCENARIOS_DIR) -> list[Scenario]:
    scenarios = []
    for p in sorted(scenarios_dir.glob("S*.md")):
        try:
            scenarios.append(load_scenario(p))
        except Exception as e:
            print(f"WARN: could not load scenario {p.name}: {e}")
    return scenarios


# ---------------------------------------------------------------------------
# Expected-behaviors loader (prose assertions from Markdown tables)
# ---------------------------------------------------------------------------

_TABLE_ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*([\d,\s\(\)A-Za-z/\-]+?)\s*\|\s*(critical|major|minor)\s*\|",
    re.IGNORECASE,
)
# Extract only the leading digits from a dimension cell like "1 (Correct skill activation)"
_DIMS_DIGITS_RE = re.compile(r"\d+")


def _extract_assertion_prose(path: Path) -> list[dict]:
    """Parse the assertion table from an expected-behaviors Markdown file.

    Returns a list of dicts with keys: number, prose, dimensions, weight.
    """
    results = []
    for line in path.read_text().splitlines():
        m = _TABLE_ROW_RE.match(line.strip())
        if not m:
            continue
        number = int(m.group(1))
        prose = m.group(2).strip()
        dims_raw = m.group(3).strip()
        weight = m.group(4).strip().lower()
        # dimensions may be "1" or "2, 8" or "1 (Correct skill activation)" or "3, 13"
        dims = [int(d) for d in _DIMS_DIGITS_RE.findall(dims_raw)]
        results.append({"number": number, "prose": prose, "dimensions": dims, "weight": weight})
    return results


# ---------------------------------------------------------------------------
# Assertion YAML loader
# ---------------------------------------------------------------------------

def _load_assertion_yaml(scenario_id: str) -> dict | None:
    path = ASSERTIONS_DIR / f"{scenario_id}.yaml"
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def load_assertions(scenario_id: str) -> list[Assertion]:
    """
    Load assertions for a scenario.

    Merges:
    - prose text from evaluations/expected-behaviors/S*.md
    - machine-checkable checks from evaluator/assertions/S*.yaml

    If no YAML exists for a scenario, every assertion is returned with
    evaluation_method=human_review and no machine checks.
    """
    # Find the expected-behaviors file
    matches = list(EXPECTED_DIR.glob(f"{scenario_id}-*.md"))
    if not matches:
        return []
    prose_data = _extract_assertion_prose(matches[0])

    # Load optional assertion YAML
    yaml_data = _load_assertion_yaml(scenario_id)
    yaml_by_number: dict[int, dict] = {}
    if yaml_data:
        for a in yaml_data.get("assertions", []):
            yaml_by_number[a["number"]] = a

    assertions = []
    for pd in prose_data:
        num = pd["number"]
        y = yaml_by_number.get(num, {})

        checks = []
        for c in y.get("checks", []):
            checks.append(AssertionCheck(type=c["type"], params={k: v for k, v in c.items() if k != "type"}))

        method = y.get("evaluation_method", "human_review")

        assertions.append(Assertion(
            assertion_id=f"{scenario_id}-A{num}",
            scenario_id=scenario_id,
            number=num,
            description=y.get("description", f"Assertion {num}"),
            prose=pd["prose"],
            weight=pd["weight"],
            dimensions=pd["dimensions"],
            evaluation_method=method,
            checks=checks,
            notes=y.get("notes", ""),
        ))

    return assertions
