"""
Antigravity adapter.

Field mapping per core/skill-specification/adapter-projection.md's matrix
and research/agent-ecosystems/antigravity.md. The one target-specific
transformation this adapter actually performs (rather than only mapping
field names) is Antigravity's documented requirement that `description`
be written in the third person.
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

TARGET = "antigravity"
PATH_TEMPLATE = ".agents/skills/{slug}/SKILL.md"  # or ~/.gemini/config/skills/{slug}/SKILL.md


def to_third_person(description: str) -> str:
    """Mechanical, grammar-agnostic third-person wrapping.

    This project's canonical descriptions are written in the imperative/
    infinitive mood ("Decide the architecture...", "Instrument systems
    for..."), matching this library's own house style. Antigravity
    requires third person. Rewriting arbitrary imperative English into
    correct third-person prose in general requires real grammatical
    analysis (subject-verb agreement varies per verb) that this adapter
    does not attempt — a wrong guess (e.g. naively appending "s" to the
    first word) would silently produce ungrammatical or wrong-meaning
    text, which is worse than an honest, safe wrapper.

    Instead: wrap the existing description under a fixed third-person
    frame ("This skill: <description>"), which is grammatically valid
    for ANY input mood and preserves the original meaning exactly. This
    is flagged in the loss manifest as a mechanical wrap, not a verified
    natural-language rewrite — an author publishing to Antigravity should
    hand-polish the wrapped description before shipping.
    """
    return f"This skill: {description}"


def project(skill: Skill) -> tuple:
    manifest = LossManifest(target=TARGET, skill_id=skill.id)

    name, _ = truncate(skill.name, None)  # optional for Antigravity; included for clarity
    manifest.native("name")

    description = to_third_person(skill.description)
    manifest.body(
        "description",
        "Mechanically wrapped into third person ('This skill: ...') to satisfy Antigravity's "
        "documented requirement (research/agent-ecosystems/antigravity.md §1). This is a safe, "
        "grammar-agnostic wrap, NOT a verified natural-language rewrite — hand-review before "
        "publishing.",
    )

    frontmatter = f"---\nname: {name}\ndescription: {description}\n---\n"

    body = skill.body
    if skill.activation_mode == "manual":
        body += (
            "\n\n## Activation note\n\nThis skill is manual-invocation-only in its "
            "canonical definition; confirm Antigravity's invocation-policy mechanism "
            "before treating it as auto-invocable.\n"
        )
        manifest.body("activation_mode", "No confirmed native manual-invocation control at research time.")
    else:
        manifest.native("activation_mode")

    body += activation_conditions_note(skill)
    record_activation_conditions(skill, manifest, "No glob/semantic-condition frontmatter field documented; kept in body.")
    body += capability_note(skill)
    record_capability_fallbacks(skill, manifest)
    manifest.body(
        "required_capabilities",
        "Antigravity documents tool-requirement declaration but the exact schema needs "
        "re-verification (research/agent-ecosystems/antigravity.md §1); capability note "
        "kept in body as the safe fallback.",
    )
    manifest.dropped(
        "execution_tier",
        "Subagent delegation (invoke_subagent) is documented but this adapter does not "
        "attempt to author that configuration automatically without a confirmed schema.",
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
