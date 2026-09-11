"""
Generic/MCP adapter.

Per core/skill-specification/adapter-projection.md: MCP is not a file
format. Per SEP-2640 (Accepted 2026-09-03, pre-reference-implementation
at research time — research/agent-ecosystems/mcp.md), a skill is exposed
as an MCP *resource* under a `skill://<slug>/SKILL.md` URI, discoverable
via a `skill://index.json` manifest, served through `skills/list` /
`skills/get` / `read_skill`. This is the one target where "path" means a
resource URI, not a filesystem path, and where a second, aggregate
artifact (the index) exists alongside each skill's own resource — every
other adapter in this library projects one skill to one file tree with no
cross-skill artifact.

**Provisional target** (per the source doc's own caveat): re-verify
against the ratified SEP-2640 extension before trusting this adapter in
production.
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
)
from lib.loss_manifest import LossManifest
from lib.skill_loader import Skill

TARGET = "mcp"


def resource_uri(slug: str) -> str:
    return f"skill://{slug}/SKILL.md"


def project(skill: Skill) -> tuple:
    manifest = LossManifest(target=TARGET, skill_id=skill.id)
    manifest.native("name")  # resource `name`
    manifest.native("description")  # resource `description`

    body = skill.body
    if skill.activation_mode == "manual":
        body += (
            "\n\n## Activation note\n\nThis skill is manual-invocation-only in its "
            "canonical definition. MCP's `skills/get`/`read_skill` model is "
            "client-initiated retrieval, not a model-triggered auto-invoke — "
            "the manual/auto distinction is largely moot for this target, since "
            "the calling client always explicitly requests the resource.\n"
        )
        manifest.body(
            "activation_mode",
            "No auto-invoke concept applies to client-initiated resource retrieval; "
            "noted in body for completeness rather than silently unaccounted.",
        )
    else:
        manifest.not_applicable(
            "activation_mode",
            "MCP resources are always explicitly retrieved by the client; there is no "
            "model-triggered auto-invoke distinction to encode for the `auto` default.",
        )
    body += activation_conditions_note(skill)
    record_activation_conditions(skill, manifest, "No MCP-native semantic-condition field documented; kept in resource body.")
    body += capability_note(skill)
    record_capability_fallbacks(skill, manifest)
    manifest.body(
        "required_capabilities",
        "Per-tool capability declaration under MCP is a server-side tool declaration, not a "
        "per-skill-resource field — noted in the resource body; left for the serving MCP "
        "server's own tool manifest to actually grant.",
    )
    manifest.dropped(
        "execution_tier",
        "MCP resources have no isolation/fork concept of their own — n/a per the projection matrix.",
    )
    body += inputs_outputs_note(skill)
    if skill.yaml_data.get("inputs"):
        manifest.body("inputs", "No MCP resource-metadata field for declared inputs; kept in resource body.")
    if skill.yaml_data.get("outputs"):
        manifest.body("outputs", "No MCP resource-metadata field for declared outputs; kept in resource body.")
    body += governance_fields_note(skill)
    record_governance_fields(skill, manifest)
    record_identity_and_body_derived_fields(skill, manifest)

    uri = resource_uri(skill.slug)
    index_entry = {
        "uri": uri,
        "name": skill.name,
        "description": skill.description,
    }

    # The single-skill artifact set: the resource body plus this skill's own
    # index-entry fragment. Aggregating fragments into one skill://index.json
    # across all skills is the caller's job (see tests/ for a worked example),
    # since one adapter call only knows about the one skill it was given.
    return {uri: body, f"{uri}.index-entry.json": index_entry}, manifest
