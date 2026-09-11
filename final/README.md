# final

Release artifacts for the AI Coding-Agent Skill Library.

## Contents

| File | Description |
|---|---|
| [`manifest.json`](manifest.json) | Machine-readable index of all 88 skills — IDs, slugs, layers, domains, execution tiers, dependency edges |
| [`RELEASE.md`](RELEASE.md) | Full release report: version, pre-condition checklist, test status, audit status, supported agents, known limitations |

## Skill promotion

Individual skills reside in [`skills/`](../skills/) and carry status
`authored, not yet validated/evaluated`. Promotion to this directory requires:

1. Passing the mechanical validator (`scripts/validate_skills.py`) — all 88
   currently pass
2. A dedicated evaluation scenario in `evaluations/` — 16 scenarios exist
   covering representative skills; the remaining 40+ are pending
3. A passing run of the behavioral evaluation suite
4. An `audits/` review pass for the specific skill

The validator gate (requirement 1) is satisfied for the whole library.
Requirements 2–4 require per-skill execution tooling not yet built. Skills are
usable now through the adapter layer; the promotion gate exists to give
consumers a quality signal, not to block consumption.

See [`RELEASE.md`](RELEASE.md) for full status details.
