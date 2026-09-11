"""
Shared skill loader — the single place that knows how to read a canonical
skill directory (skill.yaml + SKILL.md + resources).

Every per-target adapter imports Skill.load() rather than re-parsing
skill.yaml/SKILL.md itself. This is the concrete implementation of the
"do not duplicate the actual skill knowledge across adapters" rule from
the master build plan's Step 31 instructions: the knowledge of what a
canonical skill IS lives here, once; each adapter only knows how to
project that knowledge onto its own target's format.

No third-party dependencies beyond PyYAML (already a implicit project
dependency — every prior audit step in this build used
`python3 -c "import yaml; ..."` directly).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Fields that are library-governance data with no runtime meaning to a
# consuming agent — every adapter is permitted (L-3) to drop these from
# native frontmatter, provided they are recorded in the loss manifest.
# Source: core/skill-specification/adapter-projection.md, Lossiness
# contract L-3 and the "Metadata-only fields" note under the mapping matrix.
GOVERNANCE_ONLY_FIELDS = (
    "source_references",
    "last_verified",
    "reverify_triggers",
    "covered_versions",
    "version_sensitive_claims",
    "evaluation_criteria",
    "depends_on_skills",
    "conflicts_with",
    "related_skills",
    "parents",
    "required_context",
    "optional_context",
    "adapter_hints",
    "failure_handling",
    "escalation",
    "verification",
    "owned_knowledge",
    "decision_framework_present",
    "grounding",
    "skill_version",
    "spec_version",
)

# Fields that carry meaning a consuming agent needs AT RUNTIME, even if a
# target has no native frontmatter slot for them. Per L-2, an adapter must
# not silently drop these — if there's no native slot, they must appear in
# the projected body instead.
RUNTIME_MEANINGFUL_FIELDS = (
    "activation_conditions",
    "non_activation_conditions",
    "required_capabilities",
    "execution_tier",
    "capability_fallbacks",
    "inputs",
    "outputs",
)

# Internal taxonomy/identity metadata: used by this library's own routing,
# catalog, and validation tooling, but never meant to be projected into any
# target's frontmatter or body (a consuming agent doesn't need to see a
# skill's Layer number or taxonomy domain to use it correctly). Every
# adapter still records these in its loss manifest (per L-1's literal "every
# canonical field" requirement) rather than silently omitting them, but the
# recorded action is always "not applicable to projection" rather than
# "native"/"body"/"drop+note".
IDENTITY_ONLY_FIELDS = ("id", "slug", "kind", "layer", "domain")

# Fields whose substance is already required to appear, in prose form,
# inside the skill's own SKILL.md body (per core/skill-specification/
# specification.md §3.2's required body sections — every skill's body has
# its own "Purpose & scope" section derived from these, its own "Failure
# handling"/"Escalation" sections, etc.). Since `skill.body` is copied
# into every projected output as-is, these fields' meaning already survives
# projection without any separate frontmatter or body-note action needed —
# but per L-1 they still get an explicit manifest entry stating exactly
# that, rather than being silently absent from the manifest.
BODY_DERIVED_FIELDS = ("purpose", "scope", "expertise")


@dataclass
class Skill:
    """In-memory representation of one canonical skill, loaded once."""

    slug: str
    yaml_data: dict
    frontmatter: dict  # SKILL.md's own 3-key frontmatter (name/description/spec_version)
    body: str  # SKILL.md content AFTER the frontmatter block
    source_dir: Path
    resource_files: list = field(default_factory=list)  # relative paths under references/ etc.

    @property
    def id(self) -> str:
        return self.yaml_data["id"]

    @property
    def name(self) -> str:
        return self.yaml_data["name"]

    @property
    def description(self) -> str:
        return self.yaml_data["description"]

    @property
    def kind(self) -> str:
        return self.yaml_data["kind"]

    @property
    def activation_mode(self) -> str:
        return self.yaml_data.get("activation_mode", "auto")

    def governance_only_present(self) -> list:
        """Which GOVERNANCE_ONLY_FIELDS this skill actually populates (non-empty)."""
        present = []
        for f in GOVERNANCE_ONLY_FIELDS:
            v = self.yaml_data.get(f)
            if v not in (None, "", [], {}):
                present.append(f)
        return present

    def runtime_meaningful_present(self) -> list:
        present = []
        for f in RUNTIME_MEANINGFUL_FIELDS:
            v = self.yaml_data.get(f)
            if v not in (None, "", [], {}):
                present.append(f)
        return present


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def load(skill_dir: Path | str) -> Skill:
    """Load one canonical skill directory into a Skill object.

    Raises FileNotFoundError / yaml.YAMLError on malformed input rather
    than silently producing a partial Skill — an adapter should never
    project from a skill it could not fully parse (this mirrors the
    project-wide "never trust, always independently verify" discipline
    applied to the loader itself).
    """
    skill_dir = Path(skill_dir)
    yaml_path = skill_dir / "skill.yaml"
    md_path = skill_dir / "SKILL.md"

    yaml_data = yaml.safe_load(yaml_path.read_text())
    raw_md = md_path.read_text()

    m = _FRONTMATTER_RE.match(raw_md)
    if not m:
        raise ValueError(f"{md_path}: no valid --- frontmatter block found")
    frontmatter = yaml.safe_load(m.group(1))
    body = m.group(2)

    resources = []
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        resources = [str(p.relative_to(skill_dir)) for p in refs_dir.rglob("*") if p.is_file()]

    return Skill(
        slug=skill_dir.name,
        yaml_data=yaml_data,
        frontmatter=frontmatter,
        body=body,
        source_dir=skill_dir,
        resource_files=resources,
    )


def load_all(skills_root: Path | str) -> list:
    """Load every skill under skills_root (used by the compatibility test suite)."""
    skills_root = Path(skills_root)
    out = []
    for d in sorted(skills_root.iterdir()):
        if (d / "skill.yaml").exists():
            out.append(load(d))
    return out
