"""
Data models for the evaluation runner.

Grounded in the vocabulary from:
- core/orchestrator/state-and-contract.md  (RunState, invocation/return envelope)
- evaluations/scoring.md                   (assertion weights, scenario verdicts)
- evaluations/evaluation-spec.md           (dimensions 1-15, 8 categories)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Scenario description (loaded from evaluations/scenarios/)
# ---------------------------------------------------------------------------

@dataclass
class ActivationSet:
    must_activate: list[str]     # skill IDs
    must_not_activate: list[str] # skill IDs
    acceptable_either: list[str] # skill IDs — never scored as error in either direction


@dataclass
class Scenario:
    scenario_id: str             # "S01", "S12", etc.
    name: str                    # short name from the heading
    category: str                # one of the 8 categories
    complexity: str              # trivial | small | multi-step | project
    risk_level: str              # read-only | reversible-write | destructive | ...
    task: str                    # verbatim task text
    repository_signals: str      # raw text of the "Repository signals" section
    activation_set: ActivationSet
    sequencing_text: str         # raw text of the "Expected sequencing" section
    source_file: Path


# ---------------------------------------------------------------------------
# Assertion (loaded from evaluator/assertions/*.yaml, paired with scenario)
# ---------------------------------------------------------------------------

@dataclass
class AssertionCheck:
    """One machine-checkable predicate within an assertion."""
    type: str           # routing_contains | routing_excludes | ledger_contains |
                        # command_run | file_changed | status_is | output_pattern |
                        # no_escalation | test_passed | human_review
    params: dict        # predicate-specific params (skill_id, pattern, value, ...)


@dataclass
class Assertion:
    assertion_id: str         # "S01-A1", etc.
    scenario_id: str
    number: int               # matches the # column in expected-behaviors/
    description: str          # short description for display
    prose: str                # full assertion text from expected-behaviors/
    weight: str               # critical | major | minor
    dimensions: list[int]     # 1-15 from evaluation-spec.md
    evaluation_method: str    # observation | human_review | structural
    checks: list[AssertionCheck] = field(default_factory=list)
    notes: str = ""


# ---------------------------------------------------------------------------
# Run record (produced by an agent adapter)
# Mirrors state-and-contract.md's RunState + return envelope shape.
# ---------------------------------------------------------------------------

@dataclass
class RoutingEntry:
    skill_id: str
    reason: str


@dataclass
class LedgerEntry:
    entry_type: str      # invocation | decision | gate | mutation | degradation | recovery
    skill_id: str = ""
    status: str = ""     # complete | partial | blocked | refused | failed | deferred
    reason: str = ""
    details: dict = field(default_factory=dict)


@dataclass
class VerificationEntry:
    item: str
    status: str          # pass | fail | not-run
    evidence: str = ""


@dataclass
class RunRecord:
    """
    Structured record produced by the agent adapter after a scenario run.
    Built from the agent's self-reported routing decisions + observed filesystem state.
    Fields marked REQUIRED are needed to score most assertions.
    """
    scenario_id: str
    task: str                                           # verbatim task given to agent
    status: str = ""                                    # REQUIRED: complete|partial|blocked|...
    routing_selected: list[RoutingEntry] = field(default_factory=list)   # REQUIRED
    routing_excluded: list[RoutingEntry] = field(default_factory=list)
    ledger: list[LedgerEntry] = field(default_factory=list)
    verification: list[VerificationEntry] = field(default_factory=list)
    commands_run: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    output_text: str = ""          # raw agent stdout
    outputs: dict = field(default_factory=dict)  # declared output fields
    open_questions: list[str] = field(default_factory=list)
    unverified_claims: list[str] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)
    fixture_dir: Path | None = None
    raw_agent_output: str = ""
    parse_errors: list[str] = field(default_factory=list)  # issues found when parsing agent output


# ---------------------------------------------------------------------------
# Assertion verdict
# ---------------------------------------------------------------------------

@dataclass
class AssertionVerdict:
    assertion: Assertion
    verdict: str            # pass | fail | not-applicable | not-evaluated
    evidence: str = ""      # what we checked and found
    reason: str = ""        # why this verdict was reached
    needs_human_review: bool = False


# ---------------------------------------------------------------------------
# Scenario score
# ---------------------------------------------------------------------------

@dataclass
class ScenarioScore:
    scenario: Scenario
    run_record: RunRecord
    verdicts: list[AssertionVerdict]
    outcome: str           # complete | partial | failed | blocked
    critical_passed: int = 0
    critical_total: int = 0
    major_passed: int = 0
    major_total: int = 0
    minor_passed: int = 0
    minor_total: int = 0
    failed_assertions: list[AssertionVerdict] = field(default_factory=list)
    not_applicable: list[AssertionVerdict] = field(default_factory=list)
    not_evaluated: list[AssertionVerdict] = field(default_factory=list)

    @property
    def has_human_review_pending(self) -> bool:
        return any(v.needs_human_review for v in self.verdicts)


# ---------------------------------------------------------------------------
# Promotion check
# ---------------------------------------------------------------------------

@dataclass
class PromotionRequirement:
    name: str
    satisfied: bool
    details: str


@dataclass
class PromotionDecision:
    skill_id: str
    skill_slug: str
    eligible: bool              # True only if ALL required gates pass
    gates: list[PromotionRequirement]
    blocking_reason: str = ""   # first unsatisfied required gate
    score: ScenarioScore | None = None


# ---------------------------------------------------------------------------
# Skill coverage report
# ---------------------------------------------------------------------------

@dataclass
class SkillCoverage:
    skill_id: str
    skill_slug: str
    skill_name: str
    layer: int
    domain: str
    scenarios_as_must_activate: list[str]     # scenario IDs
    scenarios_as_must_not_activate: list[str]
    scenarios_as_acceptable: list[str]
    has_any_scenario: bool
    has_assertion_yaml: bool

    @property
    def coverage_depth(self) -> str:
        if self.scenarios_as_must_activate:
            return "primary"    # directly tested as required activation
        if self.scenarios_as_must_not_activate or self.scenarios_as_acceptable:
            return "boundary"   # tested as an exclusion or uncertain case
        return "none"


@dataclass
class CoverageReport:
    total_skills: int
    covered_primary: int      # has at least one must-activate scenario
    covered_boundary: int     # appears only as exclusion/uncertain
    uncovered: int            # no scenario at all
    by_skill: list[SkillCoverage]
    uncovered_skills: list[SkillCoverage]
