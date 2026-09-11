# Individual Skill Quality Review — Data / QA / Growth / Infrastructure (Generic Layer-3)

Batch: `caching-strategy`, `data-migration`, `data-modeling`, `database-operations`,
`orm-integration`, `search-integration`, `observability`, `performance-engineering`,
`security-engineering`, `testing-strategy`, `seo-optimization`, `ci-cd-pipeline`,
`containerization`, `deployment-release` (14 skills — Step 28 of the master build plan).

Reviewed against `core/skill-specification/specification.md` (spec v1.0), the
approved catalog entries in `core/taxonomy/skill-catalog.md`, and
`skills/code-commenting/SKILL.md` as the comment-quality yardstick.
`skills/observability/skill.yaml` + `SKILL.md` used as the most-recently-audited
reference template.

Two narrow, mechanical fixes were applied during this review (see per-skill
notes): a missing `source_references` entry in `search-integration/skill.yaml`
and in `testing-strategy/skill.yaml`, in each case for a research file already
cited inline in the body and already listed in the `SKILL.md` References
section but absent from `skill.yaml`. Both files were re-validated with
`python3 -c "import yaml; yaml.safe_load(open(...))"` after editing (both
passed). No other files were modified — all other findings below are reported
only, per the audit's "do not silently change architecture/content" mandate.

## Summary

| Skill | Critical | High | Medium | Low |
|---|---|---|---|---|
| caching-strategy | 0 | 0 | 0 | 0 |
| data-migration | 0 | 2 | 0 | 0 |
| data-modeling | 0 | 0 | 0 | 1 |
| database-operations | 0 | 0 | 0 | 0 |
| orm-integration | 0 | 0 | 0 | 2 |
| search-integration | 0 | 0 | 1 | 1 |
| observability | 0 | 0 | 0 | 0 |
| performance-engineering | 0 | 0 | 0 | 0 |
| security-engineering | 0 | 1 | 0 | 1 |
| testing-strategy | 0 | 0 | 1 | 1 |
| seo-optimization | 0 | 1 | 0 | 0 |
| ci-cd-pipeline | 0 | 1 | 0 | 1 |
| containerization | 0 | 1 | 0 | 1 |
| deployment-release | 0 | 1 | 0 | 1 |
| **Total** | **0** | **7** | **2** | **9** |

No VR-1 through VR-8 violations, no CE-1 overflow, no `depends_on_skills`/`parents`
conflation, no VR-5 tier/capability mismatch, and no nonexistent-ID or asymmetric
`conflicts_with` references were found anywhere in this batch — all 14 skills are
`kind: generic` with empty `conflicts_with` and empty `depends_on_skills`, which
is correct per the catalog (none of the 14 catalog entries name a conflict, and
none describe a genuine hard blocking sub-step composition). All 14 pass
frontmatter/`skill.yaml` parity (VR-2), all required fields are present (VR-1),
all body sections follow the exact §3.2 order for a generic skill (VR-8), and no
description exceeds CE-1's 500-char cap (max observed: 477 chars,
`deployment-release`). None of the 14 skills embeds a code snippet, so check #15
(comment-quality) does not apply to this batch.

The most significant, recurring finding is a **QR-4 gap** (anti-patterns must
name at least one over-engineering trap for the domain): 6 of 14 skills
(`data-migration`, `security-engineering`, `seo-optimization`, `ci-cd-pipeline`,
`containerization`, `deployment-release`) list only under-doing/insufficient-
protection anti-patterns, with no entry describing unnecessary complexity added
for the domain. See each skill's section below.

---

## caching-strategy (SK-DATA-004)

No problems found. Activation/non-activation conditions, dependencies, and
`related_skills` match the catalog entry precisely; the caching-vs-database-
operations and caching-vs-performance-engineering boundaries are explicit and
correctly upheld; all cross-reference links in Security/Performance/Testing
sections resolve to the correct sibling skill; Anti-patterns includes a clear
over-engineering trap ("Reaching for Redis reflexively for scale that doesn't
actually need cross-process coordination").

## data-migration (SK-DATA-006)

1. **Missing required "Testing" body section.** *Severity: High.* Per spec
   §3.2 rule 11, "Testing" is Conditionally Required ("R when the skill
   produces runnable code"). `data-migration`'s own declared output
   (`migration-script`, `kind: edit`) is literally runnable code (a migration
   script with up/down steps), yet `SKILL.md` has no "Testing" section at all
   — it jumps from Anti-patterns straight to Failure handling. This is a
   genuine gap in coverage that matters concretely for this skill's domain:
   e.g. "test the migration and its down-path against a staging copy of
   production data before running it live" is exactly the kind of content
   this section exists to hold, and it is currently absent.
   **Recommended correction:** add a "Testing" section (after Performance, or
   directly after Anti-patterns since Performance is correctly omitted)
   stating the migration-specific testing discipline: verify both up and down
   paths against a representative (non-production) data copy, and verify a
   batched backfill's idempotency/resumability before running it against the
   full table.
2. **Anti-patterns section has no over-engineering trap (QR-4).** *Severity:
   High.* Spec rule 4.5 QR-4: "anti-patterns MUST name at least one
   over-engineering trap for the domain." All five listed anti-patterns are
   under-doing/insufficient-safety mistakes (collapsing expand/contract,
   unbatched backfill, no rollback path, trusting current docs against a
   pinned old version, running a destructive step without confirmation). The
   fourth entry explicitly self-labels as "the domain's overengineering-
   adjacent trap **in reverse**: under-checking, not over-building" —
   i.e. the author was aware no true over-engineering trap was present and
   noted the gap rather than filling it.
   **Recommended correction:** add an anti-pattern such as "Defaulting to a
   full expand/contract rollout (multi-phase, dual-write, staged rollback
   points) for a low-risk change on a small table where a single maintenance-
   window migration would be safe and far simpler" — mirroring the Decision
   framework's own item 1 ("if the table is small or a maintenance window is
   acceptable, a simpler direct migration may be fine"), which currently has
   no matching Anti-patterns counterpart.

## data-modeling (SK-DATA-001)

1. **Misdirected cross-reference links (Security, Testing sections).**
   *Severity: Low.* The Security section's link text reads
   `[security-engineering](../../core/taxonomy/skill-catalog.md)` and the
   Testing section's reads
   `[testing-strategy](../../core/taxonomy/skill-catalog.md)` — both resolve
   to a real file (the whole taxonomy catalog exists at that path), so this
   is not a hard 404, but the link text names one specific sibling skill
   while the href points at an unrelated, much larger document instead of
   that skill's own `SKILL.md`. Every other correctly-linked skill in this
   batch (e.g. `caching-strategy`, `database-operations`) points these same
   two references at `../security-engineering/SKILL.md` and
   `../testing-strategy/SKILL.md` respectively.
   **Recommended correction:** change both hrefs to
   `../security-engineering/SKILL.md` and `../testing-strategy/SKILL.md`.

## database-operations (SK-DATA-003)

No problems found. Activation/non-activation, dependencies, and
`related_skills` match the catalog; all Security/Performance/Testing
cross-reference links correctly resolve to the sibling skill files; Knowledge
section is well-grounded with inline source markers for every technology
claim; Anti-patterns list is reasonable for the domain (the "adding an index
without a query-plan justification" entry functions as this domain's
over-engineering/unjustified-optimization trap).

## orm-integration (SK-DATA-002)

1. **Misdirected cross-reference links (Security, Testing sections).**
   *Severity: Low.* Same pattern as `data-modeling`: both links' hrefs point
   to `../../core/taxonomy/skill-catalog.md` instead of
   `../security-engineering/SKILL.md` and `../testing-strategy/SKILL.md`.
   **Recommended correction:** same as above — repoint both hrefs to the
   sibling skill files.
2. **`related_skills` omits a catalog-named related skill.** *Severity: Low.*
   The catalog's own entry for `SK-DATA-002` states `**Related:** SK-DATA-001,
   SK-DATA-003` (data-modeling, database-operations). `skill.yaml`'s
   `related_skills` is `[SK-DATA-001, SK-DATA-006]` — it includes
   `SK-DATA-006` (data-migration, which the catalog places under
   "Dependencies," not "Related," for this skill) but omits `SK-DATA-003`
   (database-operations), which the catalog explicitly names as related.
   Both are plausibly relevant, so this is not wrong so much as an
   incomplete match to the catalog's stated relation set.
   **Recommended correction:** add `SK-DATA-003` to `related_skills`.

## search-integration (SK-DATA-005)

1. **Missing `source_references` entry — fixed during this audit.**
   *Severity: Medium (resolved).* `SKILL.md`'s Knowledge section cites
   `[Source: concept-knowledge-map.md — Full-Text Search / Vector-Semantic
   Search sections]` and the References section links
   `research/knowledge-maps/concept-knowledge-map.md`, but `skill.yaml`'s
   `source_references` only listed `technology-decision-matrix.md` and
   `performance-knowledge-map.md` — the cited file had no matching
   `source_references` entry, an SG-1/SG-2 gap (an inline source marker not
   resolvable to a `source_references` entry). **Fix applied:** added a
   `concept-knowledge-map.md` entry to `skill.yaml.source_references`
   (url/title/via/retrieved, consistent with the file's existing entries).
   Re-validated with `python3 -c "import yaml; yaml.safe_load(...)"` — clean
   parse confirmed.
2. **Misdirected cross-reference links (Security, Performance, Testing
   sections).** *Severity: Low.* Same pattern as above — all three links'
   hrefs point to `../../core/taxonomy/skill-catalog.md` instead of
   `../security-engineering/SKILL.md`, `../performance-engineering/SKILL.md`,
   and `../testing-strategy/SKILL.md` respectively.
   **Recommended correction:** repoint all three hrefs to the sibling skill
   files.

## observability (SK-QA-004)

Re-verified in full (not skipped, per instructions), despite being audited
one step ago with a `required_capabilities` fix already applied. No problems
found. `execution_tier: B` with `required_capabilities: [file-read,
file-write, shell]` is internally consistent (VR-5). The resilience/
fault-tolerance-pattern exclusion is upheld precisely and consistently across
`purpose`, `scope`, `description`, `non_activation_conditions`,
`failure_handling`, `escalation`, and the body's own "When to use / When not
to use" and Anti-patterns sections — this remains the project's strongest
reference example of a well-stated non-goal. All cross-reference links
resolve correctly to sibling skill files. Anti-patterns includes an explicit
over-engineering trap ("Instrumenting reflexively with every signal instead
of matching signal choice to the actual diagnostic question").

## performance-engineering (SK-QA-003)

No problems found. Scope boundaries against `database-operations` and
`caching-strategy` are explicit and consistently upheld in both `skill.yaml`
and `SKILL.md`. All cross-reference links resolve correctly. Anti-patterns'
"micro-optimizing a component that isn't the actual bottleneck" functions as
this domain's over-engineering-adjacent trap (wasted optimization effort),
satisfying QR-4's intent.

## security-engineering (SK-QA-002)

1. **Anti-patterns section has no over-engineering trap (QR-4).** *Severity:
   High.* All five anti-patterns are under-protection failures (single-layer
   defense, treating a CVE as permanently fixed, assuming a copied-code
   dependency auto-updates, leaving `NODE_ENV` misconfigured, a
   client-exposed secret-naming mistake). None names a security-domain
   equivalent of over-engineering — e.g. adding defense-in-depth layers or
   compliance controls disproportionate to the actual threat model, which
   this skill's own Trade-offs section gestures at ("layered defense costs
   more implementation effort... worth the cost for injection/XSS-class
   risks") without ever stating the inverse anti-pattern of over-applying it
   where the threat doesn't warrant it. This is a notable gap precisely
   because this is the skill most responsible for teaching proportionate,
   evidence-based mitigation rather than reflexive hardening.
   **Recommended correction:** add an anti-pattern such as "Applying
   maximal layered defense (extra sanitization passes, blanket
   introspection-disabling, broad allowlisting) to a boundary with no
   identified untrusted input, instead of threat-modeling from the actual
   trust boundary first" — which mirrors the Decision framework's own item 1
   ("threat-model from that boundary, not from an assumed worst/best case").
2. **Misdirected cross-reference link (Performance section).** *Severity:
   Low.* The Performance section's link
   `[performance-engineering](../../core/taxonomy/skill-catalog.md)` should
   be `../performance-engineering/SKILL.md`.

## testing-strategy (SK-QA-001)

1. **Missing `source_references` entry — fixed during this audit.**
   *Severity: Medium (resolved).* `SKILL.md`'s Knowledge section cites
   `[Synthesis, technology-decision-matrix.md §1]` (the ORM
   testing-philosophy divergence discussion) and the References section
   links `research/knowledge-maps/technology-decision-matrix.md`, but
   `skill.yaml`'s `source_references` only listed `testing-knowledge-map.md`
   — an SG-1/SG-2 gap. **Fix applied:** added a
   `technology-decision-matrix.md` entry to
   `skill.yaml.source_references`. Re-validated with
   `python3 -c "import yaml; yaml.safe_load(...)"` — clean parse confirmed.
2. **Misdirected cross-reference links (Security, Performance sections).**
   *Severity: Low.* Both hrefs point to
   `../../core/taxonomy/skill-catalog.md` instead of
   `../security-engineering/SKILL.md` and `../performance-engineering/SKILL.md`.

## seo-optimization (SK-GROW-001)

1. **Anti-patterns section has no over-engineering trap (QR-4).** *Severity:
   High.* All six anti-patterns are correctness/policy-violation mistakes
   (assuming raw HTML is indexed, misusing robots.txt, over-trusting
   `rel="canonical"`, fragment-based routing, scaled/AI-generated content,
   interaction-gated lazy loading). None addresses over-engineering the SEO
   work itself — e.g. implementing every possible structured-data type
   speculatively, or chasing marginal/undocumented ranking signals at
   disproportionate engineering cost, which this skill's own Failure
   handling rule already gestures at ("if a claim isn't directly documented,
   state that it's unresolved rather than asserting a specific number")
   without the matching Anti-patterns entry.
   **Recommended correction:** add an anti-pattern such as "Implementing
   every structured-data type or SEO signal speculatively, without a
   specific rich-result/ranking goal driving each one — partial/unused
   markup adds maintenance cost without eligibility benefit, since all
   required properties for a type must be present to qualify at all."
   All other checks pass cleanly: activation/non-activation match the
   catalog, the Google-SEO/`SK-TECH-google-seo` merge is stated honestly and
   correctly, the Core-Web-Vitals/`performance-engineering` and
   rendering-mode/`rendering-strategy` boundaries are explicit, and all
   cross-reference links resolve to the correct sibling files.

## ci-cd-pipeline (SK-INFRA-002)

1. **Anti-patterns section has no over-engineering trap (QR-4).** *Severity:
   High.* All five anti-patterns are under-doing/insecure-default mistakes
   (advisory-only gating, plaintext secrets, broad token permissions,
   mutable-tag action pinning, unbounded-cache assumptions). None addresses
   unnecessary pipeline complexity — e.g. building an elaborate matrix
   strategy or a stack of reusable workflows for a small project that gains
   nothing from them.
   **Recommended correction:** add an anti-pattern such as "Building a
   multi-dimension matrix strategy or a deep reusable-workflow hierarchy for
   a project with a single build target and no real permutation to
   parallelize — added pipeline complexity with no corresponding speed or
   coverage benefit."
2. **Misdirected cross-reference links (Security, Performance, Testing
   sections).** *Severity: Low.* All three hrefs point to
   `../../core/taxonomy/skill-catalog.md` instead of the sibling skill files
   (`../security-engineering/SKILL.md`, `../performance-engineering/SKILL.md`,
   `../testing-strategy/SKILL.md`).

## containerization (SK-INFRA-001)

1. **Anti-patterns section has no over-engineering trap (QR-4).** *Severity:
   High.* All five anti-patterns are under-doing/misconfiguration mistakes
   (bad layer order, running as root, relying on removed Content Trust
   tooling, conflating rootless mode with `userns-remap`, defaulting to QEMU
   for heavy builds). None addresses unnecessary image/build complexity —
   e.g. a needless multi-stage build for a single-file static app, or
   standing up a full compose stack of local dependencies a given task
   doesn't actually touch.
   **Recommended correction:** add an anti-pattern such as "Standing up a
   full local compose stack (database, cache, search engine) for a task that
   only touches one of those dependencies, or adding multi-stage build
   complexity to an image with no build toolchain to strip out in the first
   place."
2. **Misdirected cross-reference links (Security, Performance, Testing
   sections).** *Severity: Low.* Same pattern — all three hrefs point to
   `../../core/taxonomy/skill-catalog.md` instead of the sibling skill files.

## deployment-release (SK-INFRA-003)

1. **Anti-patterns section has no over-engineering trap (QR-4).** *Severity:
   High.* All five anti-patterns are under-doing/honesty-adjacent mistakes
   (overclaiming research grounding, baked-in config, unverified rollback,
   deploying SSR output as static, unconfirmed production actions). None
   addresses unnecessary deployment complexity — e.g. reaching for canary or
   blue-green deployment (both of which this skill's own Trade-offs section
   describes as costing "more deployment-pipeline complexity" or "running
   two full environments simultaneously") for a low-traffic internal service
   where a plain rolling update with a working rollback would be sufficient.
   **Recommended correction:** add an anti-pattern such as "Choosing
   canary or blue-green deployment for a low-traffic or low-risk service
   that a simpler rolling update with a verified rollback path would serve
   just as well — added environment/traffic-splitting complexity with no
   proportionate risk-reduction benefit."
2. **Misdirected cross-reference links (Security ×2, Performance, Testing
   sections).** *Severity: Low.* The Security section has two misdirected
   links in the same paragraph — `[ci-cd-pipeline](../../core/taxonomy/
   skill-catalog.md)` and `[security-engineering](../../core/taxonomy/
   skill-catalog.md)` — plus the Performance and Testing sections, four
   occurrences total. All four should point to the sibling skill files
   (`../ci-cd-pipeline/SKILL.md`, `../security-engineering/SKILL.md`,
   `../performance-engineering/SKILL.md`, `../testing-strategy/SKILL.md`).

---

## Notes on checks that produced no batch-wide findings

- **Duplicated responsibilities (#17):** no overlap found. The
  data-modeling/orm-integration/database-operations/data-migration cluster,
  the caching-strategy/performance-engineering boundary, and the
  ci-cd-pipeline/containerization/deployment-release cluster all state
  mutually-exclusive `non_activation_conditions` that correctly route to
  each other, and each skill's Knowledge/Workflow content stays inside its
  own stated boundary rather than re-deriving a sibling's material.
- **Security recommendations (#10):** `security-engineering`,
  `database-operations`, and `data-migration` were read with particular
  scrutiny per the task's instruction; no insecure recommendation or missing
  caveat was found (parameterized-query discipline, layered XSS defense,
  CVE re-verification caveats, destructive-migration confirmation gating,
  and the `pg_dump`/restore untrusted-source warning are all present and
  correctly stated).
- **AI branding (#16):** no instance of "As an AI," marketing language, or
  vendor-specific branding was found in any of the 14 skills.
- **Comment quality (#15):** none of the 14 `SKILL.md` files contains a
  fenced code block, so this check does not apply to this batch.
