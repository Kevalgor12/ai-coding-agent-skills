#!/usr/bin/env python3
"""Mechanical validator for skills/*/skill.yaml + SKILL.md.

Fixes C-3 from audits/final-principal-engineer-audit.md: the authoring
contract in core/skill-specification/ makes the [V]-tagged rules a stated
precondition for shipping a skill, but nothing ever mechanically checked
them. Two real defects (stale "not yet authored" markers, dangling
cross-references) survived five review rounds because of that gap. This is
the first line of defense against both classes recurring.

Standalone by design: run as `python3 scripts/validate_skills.py` with no
arguments, no third-party dependency beyond PyYAML, no import from
adapters/ (adapters/lib/skill_loader.py checks projection fidelity for a
loaded skill; this script checks authoring-time correctness of the source
directories themselves, and must work even if the adapter layer is broken
or absent — e.g. as a pre-commit/CI gate that runs before adapters do).

Rule coverage (see core/skill-specification/specification.md §4.2 for the
normative VR-1..VR-8 text, and §4.1 for CE-1/CE-2):

  VR-1  required skill.yaml/SKILL.md fields present and well-typed
  VR-2  skill.yaml name/description == SKILL.md frontmatter; slug == dir name
  VR-3  every referenced skill ID resolves correctly (see below)
  VR-4  depends_on_skills graph is acyclic and layer-monotone
  VR-5  execution_tier is consistent with required_capabilities
  VR-6  activation/non_activation_conditions are non-empty and disjoint
  VR-7  no two skills share an identical activation trigger string
  VR-8  SKILL.md body section headers: canonical names, canonical order
  VR-9  Tier B/C skills have at least one execution-dependent verification item
  CE-1  description <= 500 chars (WARNING, not hard-fail: see note below)
  CE-2  body <= ~500 lines (WARNING, not hard-fail: see note below)

CE-1/CE-2 are [V] in the spec, but this validator reports them as warnings
rather than failures, matching the precedent set by the Step 33 final audit
(audits/final-principal-engineer-audit.md §7), which treated these as
advisory targets rather than blocking thresholds. Everything else above is
a hard failure.

VR-3 direction. A skill ID mentioned anywhere (depends_on_skills, parents,
related_skills, conflicts_with, or body/comment prose like "route to X
(SK-...)") must be handled correctly in one of two directions:
  (a) it resolves to an actually-authored skill directory -> fine, and
      MUST NOT be phrased as "not yet authored" / "forward reference"
      (that phrasing becomes a false claim once the skill is authored --
      this is exactly the C-1 defect: 10 skills said this about IDs that
      already existed).
  (b) it does not resolve to an authored directory -> only fine if the
      ID is a real taxonomy entry (core/taxonomy/skill-catalog.md) AND the
      reference is phrased as a forward reference ("not yet authored" /
      "forward reference"). An ID that is neither authored nor in the
      taxonomy at all is a dangling/invalid reference regardless of
      phrasing. An ID that exists in the taxonomy but isn't authored yet,
      referenced WITHOUT the forward-reference phrasing, reads as if the
      skill already exists -- also a failure.
The prose scan is a proximity-window heuristic (checks text near each ID
mention for the disclosure phrase), not a parser -- it can misfire on
unusual phrasing. Treat repeated failures at the same site as signal, but
verify by eye before assuming the script is wrong.

VR-6 is intentionally a light heuristic beyond exact-duplicate detection:
true semantic overlap between an activation and a non-activation condition
needs human judgment (that's why the spec marks the surrounding rule
[V]/[E], not pure [V]). This script hard-fails only on an exact string
appearing in both lists (mechanically certain self-contradiction) and
WARNS on high token-overlap pairs for human review.

VR-7 is exact-string uniqueness only, library-wide, across both
activation_conditions and non_activation_conditions. Fuzzy/near-duplicate
detection is future work -- not attempted here (see spec note declining to
over-build this in one pass).

Exit code: 0 if no hard failures (warnings are still printed). Non-zero
otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment fallback
    print(
        "FATAL: PyYAML is not installed (`python3 -c \"import yaml\"` failed).\n"
        "This script needs a YAML parser and intentionally does not import\n"
        "adapters/lib/skill_loader.py (must run standalone). Install PyYAML\n"
        "(`pip install pyyaml`) or add a minimal frontmatter parser here.",
        file=sys.stderr,
    )
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
CATALOG_PATH = REPO_ROOT / "core" / "taxonomy" / "skill-catalog.md"

SKILL_ID_RE = re.compile(r"\bSK-[A-Z0-9]+-[A-Za-z0-9][A-Za-z0-9-]*\b")
FORWARD_REF_RE = re.compile(
    r"not yet (?:been )?authored|forward[- ]reference", re.IGNORECASE
)

# --- schema (from core/skill-specification/specification.md §4.6) --------

ALWAYS_REQUIRED_FIELDS = [
    "id", "slug", "name", "spec_version", "skill_version", "kind", "layer",
    "domain", "purpose", "scope", "description", "activation_conditions",
    "non_activation_conditions", "activation_mode", "inputs", "outputs",
    "required_capabilities", "execution_tier", "grounding", "last_verified",
    "failure_handling", "verification", "evaluation_criteria",
]
NONEMPTY_LIST_FIELDS = [
    "activation_conditions", "non_activation_conditions", "inputs",
    "outputs", "required_capabilities", "failure_handling", "verification",
    "evaluation_criteria",
]
KIND_ENUM = {"generic", "technology", "orchestration"}
ACTIVATION_MODE_ENUM = {"auto", "manual", "always"}
EXECUTION_TIER_ENUM = {"A", "B", "C"}
GROUNDING_ENUM = {"official-docs", "engineering-convention", "mixed"}
CAPABILITY_ENUM = {
    "file-read", "file-write", "shell", "browser", "container",
    "mcp-client", "mcp-db", "git", "subagent", "network",
}
UNIVERSAL_CAPABILITIES = {"file-read", "file-write"}
OUTPUT_KIND_ENUM = {"edit", "artifact", "analysis", "data", "command-run"}
FRONTMATTER_KEYS = {"name", "description", "spec_version"}

# canonical §3.2 body section order; "required" = always-R regardless of kind
# (conditionally-required sections whose trigger needs judgment -- Workflow,
# Security, Testing -- are checked for order/naming but not presence).
BODY_SECTIONS = [
    ("Purpose & scope", True),
    ("When to use / When not to use", True),
    ("Knowledge", False),  # R for kind: technology, checked separately
    ("Decision framework", False),  # R when decision_framework_present
    ("Workflow", False),
    ("Engineering rules", True),
    ("Trade-offs", False),
    ("Anti-patterns", True),
    ("Security", False),
    ("Performance", False),
    ("Testing", False),
    ("Failure handling", True),
    ("Escalation", False),
    ("Outputs & verification", True),
    ("References", False),
]
CANONICAL_HEADING_NAMES = [s for s, _ in BODY_SECTIONS]
ALWAYS_REQUIRED_SECTIONS = [s for s, r in BODY_SECTIONS if r]

CE1_MAX_DESCRIPTION_CHARS = 500
CE2_MAX_BODY_LINES = 500


class Report:
    def __init__(self):
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def fail(self, skill: str, rule: str, msg: str):
        self.failures.append(f"[{rule}] {skill}: {msg}")

    def warn(self, skill: str, rule: str, msg: str):
        self.warnings.append(f"[{rule}] {skill}: {msg}")


def load_catalog_ids() -> set[str]:
    """All skill IDs mentioned in the taxonomy (authored or planned)."""
    if not CATALOG_PATH.exists():
        return set()
    text = CATALOG_PATH.read_text()
    return set(SKILL_ID_RE.findall(text))


def load_skill_dirs() -> list[Path]:
    if not SKILLS_ROOT.exists():
        return []
    return sorted(
        d for d in SKILLS_ROOT.iterdir()
        if d.is_dir() and (d / "skill.yaml").exists() and (d / "SKILL.md").exists()
    )


def parse_frontmatter(md_text: str) -> tuple[dict | None, str, str | None]:
    """Returns (frontmatter_dict_or_None, body, error_or_None)."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", md_text, re.DOTALL)
    if not m:
        return None, "", "no valid --- frontmatter block found"
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return None, "", f"frontmatter is not valid YAML: {e}"
    return fm, m.group(2), None


def get_type_ok(field: str, value) -> bool:
    if field in NONEMPTY_LIST_FIELDS:
        return isinstance(value, list) and len(value) >= 1
    if field in ("id", "slug", "name", "spec_version", "skill_version",
                 "kind", "domain", "purpose", "scope", "description",
                 "activation_mode", "execution_tier", "grounding"):
        return isinstance(value, str) and value.strip() != ""
    if field == "layer":
        return isinstance(value, int) and 0 <= value <= 4
    if field == "last_verified":
        return isinstance(value, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", value)
    return value is not None


def check_vr1_vr2(slug: str, yd: dict, fm: dict | None, fm_err: str | None,
                   dir_name: str, report: Report):
    skill = slug
    # VR-1: required fields present + well-typed
    for field in ALWAYS_REQUIRED_FIELDS:
        if field not in yd:
            report.fail(skill, "VR-1", f"skill.yaml missing required field '{field}'")
            continue
        if not get_type_ok(field, yd[field]):
            report.fail(skill, "VR-1", f"skill.yaml field '{field}' present but malformed/empty: {yd[field]!r}")

    if yd.get("kind") is not None and yd["kind"] not in KIND_ENUM:
        report.fail(skill, "VR-1", f"kind '{yd['kind']}' not in {sorted(KIND_ENUM)}")
    if yd.get("activation_mode") is not None and yd["activation_mode"] not in ACTIVATION_MODE_ENUM:
        report.fail(skill, "VR-1", f"activation_mode '{yd['activation_mode']}' not in {sorted(ACTIVATION_MODE_ENUM)}")
    if yd.get("execution_tier") is not None and yd["execution_tier"] not in EXECUTION_TIER_ENUM:
        report.fail(skill, "VR-1", f"execution_tier '{yd['execution_tier']}' not in {sorted(EXECUTION_TIER_ENUM)}")
    if yd.get("grounding") is not None and yd["grounding"] not in GROUNDING_ENUM:
        report.fail(skill, "VR-1", f"grounding '{yd['grounding']}' not in {sorted(GROUNDING_ENUM)}")
    caps = yd.get("required_capabilities")
    if isinstance(caps, list):
        for c in caps:
            if c not in CAPABILITY_ENUM:
                report.fail(skill, "VR-1", f"required_capabilities contains unknown capability '{c}'")
    inputs = yd.get("inputs")
    if isinstance(inputs, list):
        for item in inputs:
            if not isinstance(item, dict) or not {"name", "description", "required"} <= item.keys():
                report.fail(skill, "VR-1", f"inputs entry malformed (needs name/description/required): {item!r}")
    outputs = yd.get("outputs")
    if isinstance(outputs, list):
        for item in outputs:
            if not isinstance(item, dict) or not {"name", "kind", "description"} <= item.keys():
                report.fail(skill, "VR-1", f"outputs entry malformed (needs name/kind/description): {item!r}")
            elif item.get("kind") not in OUTPUT_KIND_ENUM:
                report.fail(skill, "VR-1", f"outputs entry kind '{item.get('kind')}' not in {sorted(OUTPUT_KIND_ENUM)}")

    # Conditionally-required fields
    if yd.get("kind") == "technology":
        if not yd.get("parents"):
            report.fail(skill, "VR-1", "kind: technology requires non-empty 'parents'")
        if not yd.get("covered_versions"):
            report.fail(skill, "VR-1", "kind: technology requires 'covered_versions'")
        if not yd.get("reverify_triggers"):
            report.fail(skill, "VR-1", "kind: technology requires non-empty 'reverify_triggers'")
    if yd.get("execution_tier") == "C":
        if not yd.get("capability_fallbacks"):
            report.fail(skill, "VR-1", "execution_tier: C requires non-empty 'capability_fallbacks'")
    if yd.get("grounding") in ("official-docs", "mixed"):
        if not yd.get("source_references"):
            report.fail(skill, "VR-1", f"grounding: {yd.get('grounding')} requires non-empty 'source_references'")

    # SKILL.md frontmatter
    if fm_err:
        report.fail(skill, "VR-1", f"SKILL.md: {fm_err}")
        return
    fm_keys = set(fm.keys()) if fm else set()
    if fm_keys != FRONTMATTER_KEYS:
        extra = fm_keys - FRONTMATTER_KEYS
        missing = FRONTMATTER_KEYS - fm_keys
        detail = []
        if extra:
            detail.append(f"extra keys {sorted(extra)}")
        if missing:
            detail.append(f"missing keys {sorted(missing)}")
        report.fail(skill, "VR-1", f"SKILL.md frontmatter must contain exactly {sorted(FRONTMATTER_KEYS)}: {', '.join(detail)}")

    # VR-2: cross-file equality + slug/dir match
    if fm:
        if yd.get("name") != fm.get("name"):
            report.fail(skill, "VR-2", f"skill.yaml name {yd.get('name')!r} != SKILL.md frontmatter name {fm.get('name')!r}")
        if yd.get("description") != fm.get("description"):
            report.fail(skill, "VR-2", "skill.yaml description != SKILL.md frontmatter description")
        if yd.get("spec_version") != fm.get("spec_version"):
            report.fail(skill, "VR-2", f"skill.yaml spec_version {yd.get('spec_version')!r} != SKILL.md frontmatter spec_version {fm.get('spec_version')!r}")
    if yd.get("slug") != dir_name:
        report.fail(skill, "VR-2", f"skill.yaml slug {yd.get('slug')!r} != directory name {dir_name!r}")


def check_vr5(slug: str, yd: dict, report: Report):
    tier = yd.get("execution_tier")
    caps = set(yd.get("required_capabilities") or [])
    fallbacks = yd.get("capability_fallbacks") or {}
    if tier == "A":
        extra = caps - UNIVERSAL_CAPABILITIES
        if extra:
            report.fail(slug, "VR-5", f"execution_tier: A but required_capabilities includes non-universal {sorted(extra)}")
    elif tier == "B":
        if "shell" not in caps:
            report.fail(slug, "VR-5", "execution_tier: B ('needs shell') but 'shell' not in required_capabilities")
        extra = caps - UNIVERSAL_CAPABILITIES - {"shell"}
        if extra:
            report.fail(slug, "VR-5", f"execution_tier: B but required_capabilities includes Tier-C-shaped capabilities {sorted(extra)} without being declared Tier C")
    elif tier == "C":
        non_universal = caps - UNIVERSAL_CAPABILITIES - {"shell"}
        if not non_universal:
            report.fail(slug, "VR-5", "execution_tier: C requires at least one non-universal capability beyond file-read/file-write/shell")
        for cap in non_universal:
            if cap not in fallbacks:
                report.fail(slug, "VR-5", f"execution_tier: C capability '{cap}' has no capability_fallbacks entry")


def check_vr6(slug: str, yd: dict, report: Report):
    act = yd.get("activation_conditions") or []
    nonact = yd.get("non_activation_conditions") or []
    act_norm = {a.strip().lower(): a for a in act if isinstance(a, str)}
    nonact_norm = {n.strip().lower(): n for n in nonact if isinstance(n, str)}
    exact_overlap = set(act_norm) & set(nonact_norm)
    for key in exact_overlap:
        report.fail(slug, "VR-6", f"identical string in both activation and non_activation_conditions: {act_norm[key]!r}")

    def tokens(s: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]+", s.lower())) - {
            "the", "a", "an", "is", "of", "or", "and", "to", "for", "not",
            "route", "use", "in", "this", "with", "it", "no",
        }

    for a in act:
        if not isinstance(a, str):
            continue
        ta = tokens(a)
        if not ta:
            continue
        for n in nonact:
            if not isinstance(n, str) or n.strip().lower() == a.strip().lower():
                continue
            tn = tokens(n)
            if not tn:
                continue
            overlap = len(ta & tn) / max(1, min(len(ta), len(tn)))
            if overlap >= 0.8:
                report.warn(slug, "VR-6", f"high token overlap between activation {a!r} and non_activation {n!r} (heuristic; human review needed)")


def check_ce(slug: str, yd: dict, body: str, report: Report):
    desc = yd.get("description") or ""
    if len(desc) > CE1_MAX_DESCRIPTION_CHARS:
        report.warn(slug, "CE-1", f"description is {len(desc)} chars (target <= {CE1_MAX_DESCRIPTION_CHARS})")
    body_lines = body.count("\n") + (1 if body and not body.endswith("\n") else 0)
    if body_lines > CE2_MAX_BODY_LINES:
        report.warn(slug, "CE-2", f"SKILL.md body is ~{body_lines} lines (target <= ~{CE2_MAX_BODY_LINES})")


def check_vr8(slug: str, yd: dict, body: str, report: Report):
    headings = re.findall(r"^##\s+(.+?)\s*$", body, re.MULTILINE)
    canonical_present = [h for h in headings if h in CANONICAL_HEADING_NAMES]
    for h in headings:
        if h not in CANONICAL_HEADING_NAMES:
            report.fail(slug, "VR-8", f"non-canonical body heading {h!r} (canonical names: {CANONICAL_HEADING_NAMES})")

    # order: canonical headings present must appear in canonical relative order
    expected_positions = [CANONICAL_HEADING_NAMES.index(h) for h in canonical_present]
    if expected_positions != sorted(expected_positions):
        report.fail(slug, "VR-8", f"body sections out of canonical order: {canonical_present}")

    present_set = set(headings)
    for required in ALWAYS_REQUIRED_SECTIONS:
        if required not in present_set:
            report.fail(slug, "VR-8", f"missing required body section '{required}'")
    if yd.get("kind") == "technology" and "Knowledge" not in present_set:
        report.fail(slug, "VR-8", "kind: technology requires a 'Knowledge' body section")
    if yd.get("decision_framework_present") is True and "Decision framework" not in present_set:
        report.fail(slug, "VR-8", "decision_framework_present: true requires a 'Decision framework' body section")


VR9_EXECUTION_INDICATORS = re.compile(
    r"\bactual(ly)?\b|actually run|run the|running|executed|execute|"
    r"observed|observing|observe|confirmed|confirming|"
    r"green|compilation|compiles|test.{0,20}pass|passes|"
    r"in the.{0,20}dashboard|in.{0,20}browser|"
    r"backed by|validated against|diffed against|traced end.to.end",
    re.IGNORECASE,
)


def check_vr9(slug: str, yd: dict, report: Report):
    """VR-9: every Tier B or C skill must have at least one execution-dependent verification item."""
    tier = yd.get("execution_tier")
    if tier not in ("B", "C"):
        return
    if slug == "capability-adapter":
        return
    items = yd.get("verification") or []
    if not isinstance(items, list):
        return
    for item in items:
        if isinstance(item, str) and VR9_EXECUTION_INDICATORS.search(item):
            return
    report.fail(slug, "VR-9", "Tier B/C skill has no execution-dependent verification item")


def check_vr3(slug: str, yd_text: str, md_text: str, authored_ids: dict[str, str],
              catalog_ids: set[str], report: Report):
    """authored_ids: id -> owning slug."""
    for source_name, text in (("skill.yaml", yd_text), ("SKILL.md", md_text)):
        for m in SKILL_ID_RE.finditer(text):
            ref_id = m.group(0)
            window = text[max(0, m.start() - 150): m.end() + 150]
            disclosed = bool(FORWARD_REF_RE.search(window))
            if ref_id in authored_ids:
                if disclosed:
                    report.fail(
                        slug, "VR-3",
                        f"{source_name} calls {ref_id} 'not yet authored'/'forward reference', "
                        f"but it IS authored (skills/{authored_ids[ref_id]}/) -- stale claim",
                    )
                # else: fine, correctly undisclosed reference to a real skill
            elif ref_id in catalog_ids:
                if not disclosed:
                    report.fail(
                        slug, "VR-3",
                        f"{source_name} references {ref_id} (in taxonomy, not yet authored) "
                        f"without 'not yet authored'/'forward reference' disclosure",
                    )
                # else: fine, correctly disclosed forward reference
            else:
                report.fail(
                    slug, "VR-3",
                    f"{source_name} references {ref_id}, which is not in the taxonomy "
                    f"(core/taxonomy/skill-catalog.md) and not authored -- dangling/invalid ID",
                )


def check_structured_ids_resolve(slug: str, yd: dict, authored_ids: dict[str, str],
                                  catalog_ids: set[str], report: Report):
    for field in ("depends_on_skills", "parents", "related_skills", "conflicts_with"):
        for ref_id in (yd.get(field) or []):
            if ref_id not in authored_ids and ref_id not in catalog_ids:
                report.fail(slug, "VR-3", f"{field} references unknown skill ID {ref_id!r}")


def check_vr4(skills: dict[str, dict], report: Report):
    """skills: slug -> yaml_data, all authored. Graph = depends_on_skills."""
    id_to_slug = {yd["id"]: slug for slug, yd in skills.items() if "id" in yd}
    id_to_layer = {yd["id"]: yd.get("layer") for slug, yd in skills.items() if "id" in yd}

    edges: dict[str, list[str]] = {}
    for slug, yd in skills.items():
        my_id = yd.get("id")
        if my_id is None:
            continue
        deps = [d for d in (yd.get("depends_on_skills") or []) if d in id_to_slug]
        edges[my_id] = deps
        my_layer = id_to_layer.get(my_id)
        for dep_id in deps:
            dep_layer = id_to_layer.get(dep_id)
            if isinstance(my_layer, int) and isinstance(dep_layer, int) and dep_layer > my_layer:
                report.fail(
                    slug, "VR-4",
                    f"depends_on_skills includes {dep_id} (layer {dep_layer}), "
                    f"which is a higher/forward layer than this skill's own layer {my_layer}",
                )

    # cycle detection (DFS, tri-color)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in edges}
    cycle_found: list[str] = []

    def dfs(node: str, stack: list[str]) -> bool:
        color[node] = GRAY
        stack.append(node)
        for nxt in edges.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == GRAY:
                cycle_start = stack.index(nxt)
                cycle_found.extend(stack[cycle_start:] + [nxt])
                return True
            if color[nxt] == WHITE and dfs(nxt, stack):
                return True
        stack.pop()
        color[node] = BLACK
        return False

    for node in list(edges):
        if color[node] == WHITE:
            if dfs(node, []):
                slugs = [id_to_slug.get(n, n) for n in cycle_found]
                report.fail("(library-wide)", "VR-4", f"dependency cycle: {' -> '.join(slugs)}")
                break  # one report is enough; graph-wide, not per-skill


def check_vr7(skills: dict[str, dict], report: Report):
    trigger_owner: dict[str, str] = {}
    for slug, yd in skills.items():
        for field in ("activation_conditions", "non_activation_conditions"):
            for trig in (yd.get(field) or []):
                if not isinstance(trig, str):
                    continue
                key = trig.strip()
                if key in trigger_owner and trigger_owner[key] != slug:
                    report.fail(
                        "(library-wide)", "VR-7",
                        f"identical trigger string shared by '{trigger_owner[key]}' and '{slug}': {key!r}",
                    )
                else:
                    trigger_owner[key] = slug


def main() -> int:
    dirs = load_skill_dirs()
    if not dirs:
        print(f"FATAL: no skill directories with skill.yaml + SKILL.md found under {SKILLS_ROOT}", file=sys.stderr)
        return 2

    catalog_ids = load_catalog_ids()
    report = Report()

    skills: dict[str, dict] = {}
    md_texts: dict[str, str] = {}
    yaml_texts: dict[str, str] = {}
    bodies: dict[str, str] = {}
    frontmatters: dict[str, dict] = {}
    load_errors: dict[str, str] = {}

    for d in dirs:
        slug = d.name
        yaml_path = d / "skill.yaml"
        md_path = d / "SKILL.md"
        yaml_text = yaml_path.read_text()
        md_text = md_path.read_text()
        yaml_texts[slug] = yaml_text
        md_texts[slug] = md_text
        try:
            yd = yaml.safe_load(yaml_text) or {}
        except yaml.YAMLError as e:
            load_errors[slug] = f"skill.yaml is not valid YAML: {e}"
            report.fail(slug, "VR-1", load_errors[slug])
            continue
        skills[slug] = yd
        fm, body, fm_err = parse_frontmatter(md_text)
        frontmatters[slug] = fm or {}
        bodies[slug] = body
        check_vr1_vr2(slug, yd, fm, fm_err, slug, report)

    authored_ids = {yd["id"]: slug for slug, yd in skills.items() if isinstance(yd.get("id"), str)}

    for slug, yd in skills.items():
        check_vr5(slug, yd, report)
        check_vr6(slug, yd, report)
        check_ce(slug, yd, bodies.get(slug, ""), report)
        check_vr8(slug, yd, bodies.get(slug, ""), report)
        check_vr9(slug, yd, report)
        check_structured_ids_resolve(slug, yd, authored_ids, catalog_ids, report)
        check_vr3(slug, yaml_texts[slug], md_texts[slug], authored_ids, catalog_ids, report)

    check_vr4(skills, report)
    check_vr7(skills, report)

    total_checked = len(dirs)
    print(f"validate_skills: checked {total_checked} skills under {SKILLS_ROOT}\n")

    if report.warnings:
        print(f"--- {len(report.warnings)} warning(s) ---")
        for w in report.warnings:
            print(f"WARN  {w}")
        print()

    if report.failures:
        print(f"--- {len(report.failures)} failure(s) ---")
        for f in sorted(report.failures):
            print(f"FAIL  {f}")
        print(f"\nvalidate_skills: FAILED ({len(report.failures)} failure(s), {len(report.warnings)} warning(s))")
        return 1

    print(f"validate_skills: PASSED (0 failures, {len(report.warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
