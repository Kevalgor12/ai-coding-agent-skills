"""
Cursor adapter.

Field mapping per core/skill-specification/adapter-projection.md's matrix
and research/agent-ecosystems/cursor.md. Cursor has no documented
per-skill tool-grant mechanism, so capability requirements go to the body
rather than frontmatter (unlike Claude Code's allowed-tools).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.common import (
    activation_conditions_note,
    capability_note,
    governance_fields_note,
    inputs_outputs_note,
    record_activation_conditions,
    record_capability_fallbacks,
    record_governance_fields,
    record_identity_and_body_derived_fields,
    truncate,
)
from lib.loss_manifest import LossManifest
from lib.skill_loader import Skill

TARGET = "cursor"
PATH_TEMPLATE = ".agents/skills/{slug}/SKILL.md"  # legacy fallback: .cursor/skills/{slug}/SKILL.md


def project(skill: Skill) -> tuple:
    manifest = LossManifest(target=TARGET, skill_id=skill.id)

    name, _ = truncate(skill.name, None)
    manifest.native("name")
    description, _ = truncate(skill.description, None)
    manifest.native("description")

    frontmatter_lines = ["---", f"name: {name}", f"description: {description}"]

    if skill.activation_mode == "manual":
        frontmatter_lines.append("disable-model-invocation: true")
        manifest.native("activation_mode")
    else:
        manifest.native("activation_mode")

    frontmatter_lines.append("---")
    frontmatter = "\n".join(frontmatter_lines) + "\n"

    body = skill.body
    body += activation_conditions_note(skill)
    record_activation_conditions(skill, manifest, "No glob/semantic-condition frontmatter field documented; kept in body.")
    body += capability_note(skill)
    record_capability_fallbacks(skill, manifest)
    manifest.body(
        "required_capabilities",
        "Cursor has no documented per-skill tool-grant mechanism (research/agent-ecosystems/cursor.md §1); "
        "capability note lives in body, enforced by SK-ORCH-002 at runtime, not by Cursor itself.",
    )
    manifest.dropped(
        "execution_tier",
        "No documented subagent/fork frontmatter field for Cursor; Tier C skills run without isolation here.",
    )
    io_note = inputs_outputs_note(skill)
    body += io_note
    if skill.yaml_data.get("inputs"):
        manifest.body("inputs", "No native frontmatter field; kept in body.")
    if skill.yaml_data.get("outputs"):
        manifest.body("outputs", "No native frontmatter field; kept in body.")
    body += governance_fields_note(skill)
    record_governance_fields(skill, manifest)
    record_identity_and_body_derived_fields(skill, manifest)

    path = PATH_TEMPLATE.format(slug=skill.slug)
    return {path: frontmatter + body}, manifest
