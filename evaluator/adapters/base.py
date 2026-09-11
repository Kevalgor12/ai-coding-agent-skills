"""
Abstract base class for agent adapters.

An agent adapter:
1. Takes a scenario + the skills to activate
2. Sets up the isolated fixture directory
3. Runs the agent on the scenario task
4. Returns a structured RunRecord

Keeping this interface abstract means the evaluator core (checker, scorer,
reporter) never contains agent-specific logic — a requirement from the user.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ..models import RunRecord, Scenario


class AgentAdapter(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Adapter target name, e.g. 'claude-code' or 'mock'."""

    @abstractmethod
    def run(
        self,
        scenario: Scenario,
        skill_ids: list[str],
        fixture_dir: Path,
        *,
        timeout: int = 300,
    ) -> RunRecord:
        """
        Execute the scenario against the agent in the given fixture directory.

        Parameters
        ----------
        scenario:    The scenario to execute.
        skill_ids:   Skill IDs the orchestrator decided to activate (from
                     scenario.activation_set.must_activate, optionally extended).
        fixture_dir: Pre-populated isolated workspace the agent should operate in.
        timeout:     Max seconds before the run is interrupted.

        Returns
        -------
        RunRecord with everything the evaluator needs to score assertions.
        Fields that could not be determined are left at their zero values;
        parse_errors lists any issues encountered.
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
