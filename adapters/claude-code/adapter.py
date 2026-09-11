"""
Claude Code adapter.

Field mapping per core/skill-specification/adapter-projection.md's matrix
and research/agent-ecosystems/claude-code.md. This is the richest native
target — lowest lossiness of the six.
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

TARGET = "claude-code"
PATH_TEMPLATE = ".claude/skills/{slug}/SKILL.md"


def project(skill: Skill) -> tuple:
    manifest = LossManifest(target=TARGET, skill_id=skill.id)

    name, name_truncated = truncate(skill.name, None)  # Claude Code documents no hard name limit
    manifest.native("name")

    description, desc_truncated = truncate(skill.description, None)
    manifest.native("description")

    frontmatter_lines = ["---", f"name: {name}", f"description: {description}"]

    if skill.activation_mode == "manual":
        frontmatter_lines.append("disable-model-invocation: true")
        manifest.native("activation_mode")
    else:
        manifest.native("activation_mode")  # auto = Claude Code's own default, nothing to emit

    # required_capabilities -> allowed-tools, where the capability maps onto a
    # known Claude Code tool name. Capabilities without a direct tool-name
    # equivalent (e.g. "browser" when no MCP browser tool is configured) are
    # left to the runtime capability-adapter skill (SK-ORCH-002) rather than
    # guessed at here (L-4: don't invent a target-native field the vendor
    # doesn't document a mapping for).
    tool_map = {"shell": "Bash", "file-read": "Read", "file-write": "Edit", "git": "Bash"}
    caps = skill.yaml_data.get("required_capabilities") or []
    known_tools = [tool_map[c] for c in caps if c in tool_map]
    unmapped = [c for c in caps if c not in tool_map]
    if known_tools:
        frontmatter_lines.append(f"allowed-tools: [{', '.join(known_tools)}]")
        manifest.native("required_capabilities")
    if unmapped:
        manifest.body(
            "required_capabilities",
            f"{unmapped} have no direct Claude Code tool-name mapping; "
            "left for SK-ORCH-002 to resolve at runtime.",
        )

    # execution_tier: C -> context: fork, when adapter_hints declares it explicitly.
    all_hints = skill.yaml_data.get("adapter_hints") or {}
    hints = all_hints.get("claude-code", {})
    if hints:
        # adapter_hints IS consumed here (it changes this adapter's own
        # output below), unlike the other 5 targets where it's pure
        # unused governance data — record that distinction explicitly so
        # the later governance sweep doesn't also mark it drop+note.
        manifest.native("adapter_hints")
    if hints.get("fork"):
        frontmatter_lines.append("context: fork")
        manifest.native("execution_tier")
    elif skill.yaml_data.get("execution_tier") == "C":
        manifest.body(
            "execution_tier",
            "Tier C skill with no explicit adapter_hints.claude-code.fork — "
            "projected without context:fork; author should confirm this is intended.",
        )
    else:
        manifest.dropped("execution_tier", "Tier A/B — no fork semantics needed.")

    if hints.get("allowed_tools") and not known_tools:
        frontmatter_lines.append(f"allowed-tools: [{', '.join(hints['allowed_tools'])}]")

    # inputs -> arguments (Claude Code documents a native `arguments` field
    # per adapter-projection.md's matrix). outputs has no vendor-documented
    # frontmatter equivalent anywhere in the six targets, so it always goes
    # to a body note regardless of target.
    inputs = skill.yaml_data.get("inputs") or []
    if inputs:
        arg_names = [i["name"] for i in inputs if i.get("required")]
        if arg_names:
            frontmatter_lines.append(f"arguments: [{', '.join(arg_names)}]")
        manifest.native("inputs") if arg_names else manifest.body(
            "inputs", "Only required inputs map to `arguments`; optional inputs noted in body."
        )
    outputs = skill.yaml_data.get("outputs") or []
    if outputs:
        manifest.body("outputs", "No vendor-documented frontmatter field for declared outputs on any of the six targets; kept in body.")

    frontmatter_lines.append("---")
    frontmatter = "\n".join(frontmatter_lines) + "\n"

    body = skill.body
    body += activation_conditions_note(skill)
    record_activation_conditions(skill, manifest, "Claude Code has no glob-free semantic-condition frontmatter field for these; kept in body.")
    body += capability_note(skill)
    record_capability_fallbacks(skill, manifest)
    body += inputs_outputs_note(skill)
    body += governance_fields_note(skill)
    record_governance_fields(skill, manifest)
    record_identity_and_body_derived_fields(skill, manifest)

    path = PATH_TEMPLATE.format(slug=skill.slug)
    return {path: frontmatter + body}, manifest
