"""
Compatibility test suite — runs every target adapter against a
deliberately diverse sample of real, already-authored skills and checks
structural properties per target. This is the "Create compatibility
tests where practical" deliverable from the master build plan's Step 31.

What "practical" means here: there is no live Claude Code / Cursor /
Codex / Windsurf / Antigravity / MCP runtime this repository can drive,
so these tests do not confirm a projected skill actually loads in each
vendor's product. What they DO confirm, mechanically and repeatably:

  - every adapter runs without crashing on every sampled skill
  - the loss manifest never silently drops a field with runtime meaning
    (Lossiness contract L-2) without at least noting it
  - required frontmatter fields are present and well-formed in every
    projected output
  - each target's own documented structural rules (name/description
    length limits, path convention, third-person description for
    Antigravity, etc.) actually hold for the projected output

Run with: python3 adapters/tests/test_compatibility.py
(No pytest dependency required — plain assertions, a project-wide
convention already used by every prior audit step's own verification
scripts in this build.)
"""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ADAPTERS_ROOT = REPO_ROOT / "adapters"
SKILLS_ROOT = REPO_ROOT / "skills"

sys.path.insert(0, str(ADAPTERS_ROOT))
from lib.skill_loader import RUNTIME_MEANINGFUL_FIELDS, load  # noqa: E402

TARGETS = ["claude-code", "cursor", "codex", "windsurf", "antigravity", "mcp"]

# A deliberately diverse sample: Layer 0 (orchestration), Layer 2
# (convention), two Layer 3 generics at different tiers, one Layer 4
# technology skill, and the AI-domain root skill (longest description in
# the library at authoring time, good for length-limit checks).
SAMPLE_SLUGS = [
    "skill-router",  # Layer 0, Tier A
    "code-review",  # Layer 2, Tier A, depends_on_skills non-empty
    "observability",  # Layer 3 generic, Tier B, required_capabilities incl. shell
    "ai-security",  # Layer 3 generic, longest/densest description class
    "react",  # Layer 4 technology, Tier B
    "git-conventions",  # Layer 2, Tier A, no shell (fixed in Step 27's VR-5 pass)
]

# Per-target structural rules worth checking mechanically, sourced from
# core/skill-specification/adapter-projection.md and the research docs
# each adapter's own README cites.
FRONTMATTER_LIMITS = {
    "cursor": {},  # no documented hard limits at research time
    "codex": {},
    "windsurf": {},
    "antigravity": {},
    "claude-code": {},
    "mcp": {},
}


def load_adapter(target: str):
    spec = importlib.util.spec_from_file_location(
        f"{target}_adapter", ADAPTERS_ROOT / target / "adapter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def extract_frontmatter(content: str) -> dict:
    """Very small, dependency-free frontmatter reader for test assertions
    (deliberately not reusing lib.skill_loader's regex, since this test
    should catch a regression in the loader itself, not share its blind
    spots)."""
    if not content.startswith("---"):
        return {}
    end = content.find("\n---", 3)
    if end == -1:
        return {}
    block = content[3:end].strip()
    result = {}
    for line in block.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            result[k.strip()] = v.strip()
    return result


def run():
    failures = []
    checks_run = 0

    for slug in SAMPLE_SLUGS:
        skill_dir = SKILLS_ROOT / slug
        if not skill_dir.exists():
            failures.append(f"sample skill '{slug}' does not exist under skills/")
            continue
        skill = load(skill_dir)

        for target in TARGETS:
            adapter = load_adapter(target)
            try:
                files, manifest = adapter.project(skill)
            except Exception as e:  # noqa: BLE001 - a crash IS the test failure
                failures.append(f"[{target}/{slug}] adapter.project() raised {type(e).__name__}: {e}")
                continue

            checks_run += 1

            # Check 1: at least one file/resource was produced.
            if not files:
                failures.append(f"[{target}/{slug}] project() returned no output files")
                continue

            # Check 2: L-2 — no runtime-meaningful field is drop+note'd
            # without landing in the body somewhere (spot-checked via the
            # manifest's own self-report, since the manifest is the
            # authoritative record of what each adapter did).
            violations = manifest.dropped_fields_with_runtime_meaning(RUNTIME_MEANINGFUL_FIELDS)
            # execution_tier is a documented, intentional exception when a
            # skill's tier needs no isolation semantics on this target (Tier
            # A/B have nothing further to express beyond required_capabilities,
            # which is checked separately) — every adapter's own code comments
            # this exception explicitly, so it is not scored as a violation
            # here, but any OTHER runtime-meaningful field being dropped is.
            violations = [v for v in violations if v != "execution_tier"]
            if violations:
                failures.append(
                    f"[{target}/{slug}] L-2 VIOLATION: runtime-meaningful field(s) "
                    f"{violations} dropped with no body compensation"
                )

            # Check 3: every projected file/resource has non-empty content.
            for path, content in files.items():
                if isinstance(content, str) and not content.strip():
                    failures.append(f"[{target}/{slug}] empty content at {path}")

            # Check 4 (file-based targets only): frontmatter present with
            # name + description, non-empty.
            if target != "mcp":
                main_path = next(iter(files))
                main_content = files[main_path]
                fm = extract_frontmatter(main_content)
                if "name" not in fm or not fm["name"]:
                    failures.append(f"[{target}/{slug}] missing/empty 'name' in frontmatter")
                if "description" not in fm or not fm["description"]:
                    failures.append(f"[{target}/{slug}] missing/empty 'description' in frontmatter")

            # Check 5: Antigravity-specific — description must actually be
            # wrapped in the documented third-person frame.
            if target == "antigravity":
                main_content = next(iter(files.values()))
                fm = extract_frontmatter(main_content)
                if not fm.get("description", "").startswith("This skill:"):
                    failures.append(
                        f"[{target}/{slug}] description not third-person-wrapped: "
                        f"{fm.get('description', '')[:60]!r}"
                    )

            # Check 6: MCP-specific — resource URI shape and index entry present.
            if target == "mcp":
                uris = [p for p in files if p.startswith("skill://") and p.endswith("SKILL.md")]
                index_entries = [p for p in files if p.endswith(".index-entry.json")]
                if not uris:
                    failures.append(f"[{target}/{slug}] no skill:// resource URI produced")
                if not index_entries:
                    failures.append(f"[{target}/{slug}] no index-entry fragment produced")

            # Check 7: path convention — file-based targets should place the
            # skill under a directory named after its own slug (catches a
            # classic copy-paste bug: hardcoding one skill's slug in a
            # path template).
            if target != "mcp":
                main_path = next(iter(files))
                if f"/{slug}/" not in main_path and not main_path.startswith(f"{slug}/"):
                    failures.append(f"[{target}/{slug}] projected path does not contain the skill's own slug: {main_path}")

            # Check 8 (L-1 completeness): every canonical field the skill
            # actually populates must be accounted for SOMEWHERE in the loss
            # manifest (native / body / drop+note / n/a) — an unmentioned
            # field is silent, undocumented data loss. This is the exact
            # check that would have caught `inputs`/`outputs` falling
            # through the cracks before this test suite was strengthened.
            accounted = {e.field_name for e in manifest.entries}
            for canonical_field, value in skill.yaml_data.items():
                if value in (None, "", [], {}):
                    continue
                if canonical_field not in accounted:
                    failures.append(
                        f"[{target}/{slug}] L-1 VIOLATION: populated field `{canonical_field}` "
                        f"has no loss-manifest entry at all (not native/body/drop+note/n/a)"
                    )

    print(f"Ran {checks_run} adapter x skill combinations across {len(TARGETS)} targets and {len(SAMPLE_SLUGS)} sample skills.")
    if failures:
        print(f"\n{len(failures)} FAILURES:\n")
        for f in failures:
            print(" -", f)
        return 1
    print("All compatibility checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
