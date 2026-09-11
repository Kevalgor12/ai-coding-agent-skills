# scripts/

## validate_skills.py

Mechanical validator for every `skills/<slug>/skill.yaml` + `SKILL.md` pair
against the `[V]`-tagged rules in
[`core/skill-specification/specification.md`](../core/skill-specification/specification.md)
(§4.2 `VR-1`..`VR-8`, §4.1 `CE-1`/`CE-2`). Standalone: no CLI arguments, no
dependency beyond PyYAML, does not import `adapters/` (adapters check
projection fidelity of an already-loaded skill; this checks authoring-time
correctness of the source directories, independently of the adapter layer).

```
python3 scripts/validate_skills.py
```

Exit code 0 = no hard failures. Non-zero = at least one hard failure
(details printed to stdout). Suitable as a pre-commit/CI gate.

### Checks implemented

| Rule | What it checks | Severity |
|---|---|---|
| VR-1 | Every always-required `skill.yaml`/`SKILL.md` field is present and well-typed (incl. conditionally-required fields: `parents`/`covered_versions`/`reverify_triggers` for `kind: technology`, `capability_fallbacks` for Tier C, `source_references` for `official-docs`/`mixed` grounding). `SKILL.md` frontmatter must contain exactly `name`/`description`/`spec_version`. | fail |
| VR-2 | `skill.yaml.name`/`description`/`spec_version` equal `SKILL.md` frontmatter; `slug` equals the directory name. | fail |
| VR-3 | Every skill ID referenced in `depends_on_skills`/`parents`/`related_skills`/`conflicts_with`, and every `SK-...` ID mentioned in body/comment prose, resolves correctly: authored IDs must not be called "not yet authored"/"forward reference" (the C-1 defect pattern); IDs that are genuinely unauthored must carry that disclosure and must exist in the taxonomy catalog; an ID absent from both the authored set and the taxonomy catalog is a dangling/invalid reference. The prose half is a proximity-window text heuristic, not a parser — see the script's module docstring for its limits. | fail |
| VR-4 | The `depends_on_skills` graph (all 86 skills) is acyclic and layer-monotone (a dependency's `layer` must be same-or-lower, never higher, than the depending skill's own `layer`). | fail |
| VR-5 | `execution_tier` is consistent with `required_capabilities` (A ⇒ only `file-read`/`file-write`; B ⇒ `shell` present, nothing Tier-C-shaped; C ⇒ a non-universal capability plus a matching `capability_fallbacks` entry). | fail |
| VR-6 | `activation_conditions`/`non_activation_conditions` non-empty; an identical string in both is a hard fail. High token-overlap pairs are a warning only — true semantic contradiction needs human judgment, so this stays a heuristic by design (see docstring). | fail (exact) / warn (fuzzy) |
| VR-7 | No two skills, anywhere in the library, declare the identical activation or non-activation trigger string (exact match only — fuzzy matching is future work, deliberately not built here). | fail |
| VR-8 | `SKILL.md` body `##` headings use only the canonical §3.2 names, appear in canonical relative order, and the always-required sections (Purpose & scope, When to use/not, Engineering rules, Anti-patterns, Failure handling, Outputs & verification) are present — plus Knowledge for `kind: technology` and Decision framework when `decision_framework_present: true`. | fail |
| CE-1 | `description` length ≤ 500 chars. | warn |
| CE-2 | `SKILL.md` body length ≤ ~500 lines. | warn |

CE-1/CE-2 are marked `[V]` in the spec but reported as warnings here,
matching the advisory treatment the Step 33 final audit
(`audits/final-principal-engineer-audit.md` §7) already gave them — everything
else above is a hard failure.

### Deliberately not implemented

- **SG-\*/VA-\*/QR-\*** (source-grounding, version-awareness, quality rules) —
  spec-marked `[A]`/`[E]`, not `[V]`; they require judging whether a claim is
  actually true against current docs, which is not mechanical.
- **CE-3/CE-4/CE-5/CE-6** — same reason (needs judgment about what "belongs"
  in Tier 2, or eval-suite data this script doesn't have).
- Fuzzy/near-duplicate trigger matching for VR-7, and true semantic overlap
  detection for VR-6 — both explicitly deferred; see the rule table above and
  the script's module docstring.
