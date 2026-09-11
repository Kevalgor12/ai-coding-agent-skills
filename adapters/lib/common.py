"""
Small helpers shared by every per-target adapter, so the mechanical bits
(truncation, body-note formatting) are written once rather than
reimplemented six times.
"""

from .skill_loader import BODY_DERIVED_FIELDS, IDENTITY_ONLY_FIELDS, Skill


def truncate(text: str, max_length: int | None) -> tuple:
    """Returns (possibly-truncated text, was_truncated)."""
    if max_length is None or len(text) <= max_length:
        return text, False
    return text[: max_length - 1].rstrip() + "…", True


def body_note(title: str, lines: list) -> str:
    """A consistently-formatted note block appended to a projected body for
    a field the target has no native frontmatter slot for (per L-2)."""
    body = f"\n\n## {title}\n\n"
    body += "\n".join(f"- {line}" for line in lines)
    return body + "\n"


def activation_conditions_note(skill: Skill) -> str:
    lines = list(skill.yaml_data.get("activation_conditions") or [])
    lines += [f"NOT: {c}" for c in (skill.yaml_data.get("non_activation_conditions") or [])]
    return body_note("Activation guidance (library-defined, not natively enforced here)", lines)


def record_activation_conditions(skill: Skill, manifest, note: str) -> None:
    """Both `activation_conditions` and `non_activation_conditions` are
    rendered together into one body block by `activation_conditions_note`
    — this records BOTH canonical field names against that single action,
    so neither is silently missing from the manifest (a bug this suite's
    own L-1 completeness test caught: only the first field name was being
    recorded, leaving `non_activation_conditions` unaccounted)."""
    manifest.body("activation_conditions", note)
    if skill.yaml_data.get("non_activation_conditions"):
        manifest.body("non_activation_conditions", note)


def capability_note(skill: Skill) -> str:
    caps = skill.yaml_data.get("required_capabilities") or []
    fallbacks = skill.yaml_data.get("capability_fallbacks") or {}
    lines = [f"Requires: {', '.join(caps)}" if caps else "No special capabilities required."]
    for cap, fb in fallbacks.items():
        lines.append(f"If `{cap}` unavailable: {fb}")
    return body_note("Capability requirements (enforced by SK-ORCH-002 at runtime, not this file)", lines)


def record_capability_fallbacks(skill: Skill, manifest) -> None:
    """`capability_fallbacks` is rendered into the same body block
    `capability_note` produces alongside `required_capabilities`, but is a
    distinct canonical field and needs its own manifest entry (an L-1 gap
    this suite's own completeness test caught, affecting every Tier C
    skill that declares fallbacks, e.g. `playwright`)."""
    if skill.yaml_data.get("capability_fallbacks"):
        manifest.body(
            "capability_fallbacks",
            "Rendered inside the same capability-requirements body note as required_capabilities.",
        )


def governance_fields_note(skill: Skill) -> str:
    """L-3: governance-only fields dropped from frontmatter still get a
    pointer back to the canonical source, so nothing vanishes silently."""
    present = skill.governance_only_present()
    if not present:
        return ""
    lines = [
        f"Full `{f}` is defined in this skill's canonical `skill.yaml`, not reproduced here."
        for f in present
    ]
    return body_note("Library metadata (canonical source only)", lines)


def record_governance_fields(skill: Skill, manifest) -> None:
    """Records every populated GOVERNANCE_ONLY_FIELDS entry as `drop+note`,
    EXCEPT any field an adapter already recorded under a different action
    earlier in its own `project()` (e.g. `adapter_hints`, which Claude
    Code's adapter actually consumes and should record as `native`/`body`,
    not `drop+note`). This guard is what makes it safe for every adapter to
    share one governance-sweep call without a consuming adapter's own,
    earlier, more-specific entry for the same field being silently
    overwritten or duplicated/contradicted."""
    already = {e.field_name for e in manifest.entries}
    for f in skill.governance_only_present():
        if f not in already:
            manifest.dropped(f, "Library-governance field; canonical source is skill.yaml.")


def record_identity_and_body_derived_fields(skill: Skill, manifest) -> None:
    """Every adapter calls this once per skill so `id`/`slug`/`kind`/`layer`/
    `domain` (internal taxonomy identity — never projected to any target)
    and `purpose`/`scope`/`expertise` (already carried verbatim inside
    `skill.body`'s own required sections) both get an explicit, non-silent
    manifest entry, per L-1's "every canonical field" requirement — without
    every adapter re-deriving this same reasoning independently."""
    for f in IDENTITY_ONLY_FIELDS:
        manifest.not_applicable(f, "Internal taxonomy/identity metadata; not meaningful to a consuming agent.")
    for f in BODY_DERIVED_FIELDS:
        manifest.not_applicable(
            f,
            f"`{f}` is not separately projected — its content already appears verbatim inside "
            "the skill's own body (e.g. the required 'Purpose & scope' section), which is "
            "copied into the projected output as-is.",
        )


def inputs_outputs_note(skill: Skill) -> str:
    lines = []
    for inp in skill.yaml_data.get("inputs") or []:
        req = "required" if inp.get("required") else "optional"
        lines.append(f"Input `{inp.get('name')}` ({req}): {inp.get('description', '')}")
    for out in skill.yaml_data.get("outputs") or []:
        lines.append(f"Output `{out.get('name')}` ({out.get('kind', '')}): {out.get('description', '')}")
    if not lines:
        return ""
    return body_note("Declared inputs / outputs", lines)
