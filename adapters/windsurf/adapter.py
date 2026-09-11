"""
Windsurf / Devin adapter.

Field mapping per core/skill-specification/adapter-projection.md's matrix
and research/agent-ecosystems/windsurf.md. Flagged there as mid-migration
(Cascade -> Devin Local) at research time — this adapter targets the
documented file-based convention and notes the migration risk explicitly
rather than guessing which side of the rebrand a given deployment is on.
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

TARGET = "windsurf"
PATH_TEMPLATE = ".agents/skills/{slug}/SKILL.md"  # legacy fallback: .windsurf/skills/{slug}/SKILL.md


def project(skill: Skill) -> tuple:
    manifest = LossManifest(target=TARGET, skill_id=skill.id)

    name, _ = truncate(skill.name, None)
    manifest.native("name")
    description, _ = truncate(skill.description, None)
    manifest.native("description")

    frontmatter = f"---\nname: {name}\ndescription: {description}\n---\n"

    body = skill.body
    if skill.activation_mode == "manual":
        body += (
            "\n\n## Activation note\n\n"
            "This skill is manual-invocation-only in its canonical definition. "
            "No Windsurf-documented equivalent to Claude Code's "
            "`disable-model-invocation` was confirmed at research time — treat "
            "this skill as auto-invocable here until re-verified, and prefer "
            "explicit user invocation where the host supports it.\n"
        )
        manifest.body(
            "activation_mode",
            "No confirmed native manual-invocation control for Windsurf/Devin at research time; "
            "downgraded to a body warning rather than assumed-native.",
        )
    else:
        manifest.native("activation_mode")

    body += activation_conditions_note(skill)
    record_activation_conditions(skill, manifest, "No glob/semantic-condition frontmatter field documented; kept in body.")
    body += capability_note(skill)
    record_capability_fallbacks(skill, manifest)
    manifest.body(
        "required_capabilities",
        "No documented per-skill tool-grant mechanism for Windsurf/Devin at research time; "
        "capability note lives in body only.",
    )
    manifest.dropped(
        "execution_tier",
        "Devin Local subagent support was documented as 'Preview' at research time "
        "(research/agent-ecosystems/windsurf.md) — not assumed available.",
    )
    body += inputs_outputs_note(skill)
    if skill.yaml_data.get("inputs"):
        manifest.body("inputs", "No native frontmatter field; kept in body.")
    if skill.yaml_data.get("outputs"):
        manifest.body("outputs", "No native frontmatter field; kept in body.")
    body += governance_fields_note(skill)
    record_governance_fields(skill, manifest)
    record_identity_and_body_derived_fields(skill, manifest)

    path = PATH_TEMPLATE.format(slug=skill.slug)
    return {path: frontmatter + body}, manifest
