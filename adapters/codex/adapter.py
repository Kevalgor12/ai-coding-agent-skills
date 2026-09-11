"""
Codex adapter.

Field mapping per core/skill-specification/adapter-projection.md's matrix
and research/agent-ecosystems/codex.md. Codex supports an optional
sidecar `agents/openai.yaml` for invocation policy and tool dependencies —
this adapter emits that sidecar only when the skill's manual activation
mode or required_capabilities actually need it, per L-4 (don't invent
frontmatter/config the vendor doesn't document a use for).
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

TARGET = "codex"
PATH_TEMPLATE = ".agents/skills/{slug}/SKILL.md"
POLICY_PATH_TEMPLATE = ".agents/skills/{slug}/agents/openai.yaml"


def project(skill: Skill) -> tuple:
    manifest = LossManifest(target=TARGET, skill_id=skill.id)

    name, _ = truncate(skill.name, None)
    manifest.native("name")
    description, _ = truncate(skill.description, None)
    manifest.native("description")

    frontmatter = f"---\nname: {name}\ndescription: {description}\n---\n"

    body = skill.body
    body += activation_conditions_note(skill)
    record_activation_conditions(skill, manifest, "No glob/semantic-condition frontmatter field documented for Codex; kept in body.")
    body += capability_note(skill)
    record_capability_fallbacks(skill, manifest)
    body += inputs_outputs_note(skill)
    if skill.yaml_data.get("inputs"):
        manifest.body("inputs", "No native frontmatter field; kept in body.")
    if skill.yaml_data.get("outputs"):
        manifest.body("outputs", "No native frontmatter field; kept in body.")
    body += governance_fields_note(skill)
    record_governance_fields(skill, manifest)
    record_identity_and_body_derived_fields(skill, manifest)

    files = {PATH_TEMPLATE.format(slug=skill.slug): frontmatter + body}

    policy_lines = []
    if skill.activation_mode == "manual":
        policy_lines.append("allow_implicit_invocation: false")
        manifest.native("activation_mode")
    else:
        manifest.native("activation_mode")

    caps = skill.yaml_data.get("required_capabilities") or []
    if caps:
        policy_lines.append("tool_dependencies:")
        for c in caps:
            policy_lines.append(f"  - {c}")
        manifest.body(
            "required_capabilities",
            "Listed under tool_dependencies in agents/openai.yaml as a declared need, "
            "not a per-tool grant — Codex's own policy enforcement is separate from this list "
            "(research/agent-ecosystems/codex.md §10).",
        )

    if policy_lines:
        files[POLICY_PATH_TEMPLATE.format(slug=skill.slug)] = "\n".join(policy_lines) + "\n"

    manifest.dropped(
        "execution_tier",
        "Subagent policy for Tier C skills is a Codex-side configuration this adapter does not "
        "attempt to author automatically (research/agent-ecosystems/codex.md notes subagent policy "
        "exists but its exact schema needs re-verification before an adapter should generate it).",
    )

    return files, manifest
