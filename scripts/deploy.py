#!/usr/bin/env python3
"""
Deploy canonical skills from this library into a target project, projected
into the file format a specific coding agent (Claude Code, Cursor, Codex,
Windsurf, Antigravity) or a generic MCP server expects.

This is the missing "make it actually usable" step on top of adapters/ —
adapters/*/adapter.py know how to project ONE skill; this script loads every
skill (or a filtered subset) from skills/, projects each through the chosen
adapter(s), and writes the resulting files under a destination project root.

Usage
-----
# Deploy the whole library into a new project for Claude Code
python3 scripts/deploy.py --target claude-code --dest ~/projects/my-app

# Deploy only a few skills
python3 scripts/deploy.py --target claude-code --dest . --skills react,postgresql,testing-strategy

# Deploy for every supported target at once (writes to each target's own path)
python3 scripts/deploy.py --target all --dest ~/projects/my-app

# Dry run — show what would be written without touching disk
python3 scripts/deploy.py --target cursor --dest . --dry-run

# Also write a loss-manifest report (what each adapter dropped/pushed to body)
python3 scripts/deploy.py --target claude-code --dest . --manifest-out manifest.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADAPTERS_ROOT = REPO_ROOT / "adapters"
SKILLS_ROOT = REPO_ROOT / "skills"

sys.path.insert(0, str(ADAPTERS_ROOT))
from lib.skill_loader import load_all  # noqa: E402

ALL_TARGETS = ["claude-code", "cursor", "codex", "windsurf", "antigravity", "mcp"]


def _load_adapter(target: str):
    spec = importlib.util.spec_from_file_location(
        f"{target}_adapter", ADAPTERS_ROOT / target / "adapter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _deploy_mcp(dest: Path, skills, *, dry_run: bool = False) -> list[dict]:
    """MCP has no filesystem projection of its own — project() returns a
    skill:// resource URI (not a path) and an index-entry dict (not text).
    Per the adapter's own docstring, aggregating index fragments across
    skills into one skill://index.json is the caller's job; this bundles
    everything into a single mcp_export.json under dest instead of trying
    to write skill:// URIs as filesystem paths."""
    adapter = _load_adapter("mcp")
    resources = {}
    index = []
    records = []

    for skill in skills:
        files, manifest = adapter.project(skill)
        for key, value in files.items():
            if key.endswith(".index-entry.json"):
                index.append(value)
            else:
                resources[key] = value
        records.append({
            "skill": skill.slug,
            "target": "mcp",
            "path": "mcp_export.json",
            "manifest": [
                {"field": e.field_name, "action": e.action, "note": e.note}
                for e in manifest.entries
            ],
        })

    if not dry_run:
        out_path = dest / "mcp_export.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({"index": index, "resources": resources}, indent=2))

    return records


def deploy(target: str, dest: Path, skills, *, dry_run: bool = False, seen: dict | None = None) -> list[dict]:
    """Project every skill through one target adapter and write files under dest.
    Returns a list of {skill, path, manifest} records for reporting.

    `seen` (rel_path -> (target, content)) is shared across a `--target all` run:
    several targets (cursor/codex/windsurf) intentionally converge on the same
    `.agents/skills/` path per adapter-projection.md's "common denominator"
    design. When two targets would write DIFFERENT content to the same path,
    that's a silent-overwrite risk worth a loud warning rather than a silent
    last-write-wins — see e.g. project-management's activation_mode: manual,
    where the codex adapter currently drops disable-model-invocation that
    cursor emits."""
    if target == "mcp":
        return _deploy_mcp(dest, skills, dry_run=dry_run)

    adapter = _load_adapter(target)
    records = []

    for skill in skills:
        files, manifest = adapter.project(skill)
        for rel_path, content in files.items():
            if seen is not None and rel_path in seen:
                prev_target, prev_content = seen[rel_path]
                if prev_content != content:
                    print(
                        f"WARNING: {target} and {prev_target} write DIFFERENT content to "
                        f"{rel_path} — {target} overwrites {prev_target}'s output. "
                        f"Deploy these targets separately (into different --dest dirs) if both matter.",
                        file=sys.stderr,
                    )
            if seen is not None:
                seen[rel_path] = (target, content)

            out_path = dest / rel_path
            if not dry_run:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(content)
            records.append({
                "skill": skill.slug,
                "target": target,
                "path": str(out_path if not dry_run else rel_path),
                "manifest": [
                    {"field": e.field_name, "action": e.action, "note": e.note}
                    for e in manifest.entries
                ],
            })

    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", required=True, choices=ALL_TARGETS + ["all"],
                         help="Coding agent to deploy for")
    parser.add_argument("--dest", required=True, type=Path,
                         help="Destination project root (skills are written under its .claude/, .agents/, etc.)")
    parser.add_argument("--skills", default=None,
                         help="Comma-separated skill slugs to deploy (default: all skills in the library)")
    parser.add_argument("--dry-run", action="store_true",
                         help="Show what would be written without touching disk")
    parser.add_argument("--manifest-out", type=Path, default=None,
                         help="Write a JSON loss-manifest report to this path")
    args = parser.parse_args()

    all_skills = load_all(SKILLS_ROOT)
    if args.skills:
        wanted = set(s.strip() for s in args.skills.split(","))
        skills = [s for s in all_skills if s.slug in wanted]
        missing = wanted - {s.slug for s in skills}
        if missing:
            print(f"ERROR: unknown skill slug(s): {sorted(missing)}", file=sys.stderr)
            sys.exit(1)
    else:
        skills = all_skills

    targets = ALL_TARGETS if args.target == "all" else [args.target]

    dest = args.dest.expanduser().resolve()
    if not args.dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    all_records = []
    seen: dict = {}
    for target in targets:
        records = deploy(target, dest, skills, dry_run=args.dry_run, seen=seen)
        all_records += records
        verb = "Would write" if args.dry_run else "Wrote"
        print(f"[{target}] {verb} {len(records)} file(s) for {len(skills)} skill(s)")

    if args.manifest_out:
        args.manifest_out.write_text(json.dumps(all_records, indent=2))
        print(f"Loss manifest written: {args.manifest_out}")

    if not args.dry_run:
        print(f"\nDone. Skills deployed to: {dest}")
        if "claude-code" in targets:
            print(f"  Claude Code will auto-discover them under {dest}/.claude/skills/")
        if any(t in targets for t in ("cursor", "codex", "windsurf")):
            print(f"  Cursor/Codex/Windsurf will auto-discover them under {dest}/.agents/skills/")
        if "antigravity" in targets:
            print(f"  Antigravity will auto-discover them under {dest}/.agents/skills/")


if __name__ == "__main__":
    main()
