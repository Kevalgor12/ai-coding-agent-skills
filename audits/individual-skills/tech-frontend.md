# Individual Skill Review — Frontend Technology Skills

Batch: `react`, `nextjs`, `vue`, `nuxt`, `angular`, `typescript`, `web-standards`, `sass`, `tailwindcss`, `mui`, `shadcn-ui`, `threejs` (12 skills, Layer 4, `kind: technology`). Part of Step 28 (Individual Skill Review). This report was compiled directly from six sub-reviews (react+nextjs, vue+nuxt, web-standards+sass+tailwindcss, threejs, angular+typescript, mui+shadcn-ui), each of which read the full spec, the taxonomy catalog, the code-commenting philosophy, and every skill's own cited `research/technologies/*.md` doc, spot-checking specific factual claims rather than trusting citations at face value.

## Summary table

| Skill | Critical | High | Medium | Low |
|---|---|---|---|---|
| react | 1 (shared) | 0 | 0 | 1 |
| nextjs | 1 (shared) | 1 | 0 | 2 |
| vue | 0 | 1 (shared) | 0 | 2 |
| nuxt | 0 | 1 (shared) | 3 | 1 |
| web-standards | 0 | 1 (shared) | 1 | 2 |
| sass | 0 | 1 (shared) | 1 | 1 |
| tailwindcss | 0 | 2 (1 shared) | 0 | 1 |
| angular | 0 | 1 | 2 | 3 |
| typescript | 0 | 0 | 2 | 3 |
| mui | 0 | 1 (shared) | 2 | 3 |
| shadcn-ui | 0 | 1 (shared) | 3 | 3 |
| threejs | 0 | 0 | 2 | 3 |

"(shared)" marks the two repo-wide cross-cutting defects below, counted once per affected skill.

## Cross-cutting finding #1 — `SK-FE-005` (rendering-strategy) referenced but never authored (Critical, VR-3)

`react`, `nextjs`, `vue`, `angular`, `nuxt` all declare `parents: [..., SK-FE-005, ...]`. **No skill with id `SK-FE-005` exists anywhere in the repo** (confirmed via `grep -rh "^id: " skills/*/skill.yaml` — existing FE-domain IDs stop at SK-FE-004). Every one of these skills' own authors left an explicit inline comment acknowledging this ("not yet authored") — a deliberate, honestly-disclosed forward reference, not an oversight — but as currently written each skill still individually fails VR-3 (every `parents`/`depends_on_skills`/`related_skills`/`conflicts_with` reference must resolve to an existing skill ID).

**This is a repo-wide, architecture-level gap, not a per-skill defect** — it needs one decision (author `SK-FE-005`, or drop the forward reference from all five skills until it exists), not five independent patches. Not fixed by any reviewer, correctly reported instead.

## Cross-cutting finding #2 — stale "not yet authored" claims about now-real skills (High, all instances)

Distinct from finding #1: these are skills whose forward-referenced parent **has since been authored**, but the referencing skill's text was never updated. Found in:

- `web-standards`, `sass`, `tailwindcss` — all three still claim `SK-FE-003` (styling-systems) is "not yet authored." It exists, fully authored, and already links back to all three. `sass/skill.yaml` even has a `reverify_triggers` entry for exactly this event that has already fired, unactioned.
- `nuxt` — a stale comment claims `SK-GROW-001` (seo-optimization) is "not yet authored." It exists (authored in a later, separate batch).
- `mui`, `shadcn-ui` — both still claim `SK-FE-003` (styling-systems) and `SK-FE-002` (ui-ux-design) are "not yet authored." Both exist. Worse: `styling-systems` has since independently authored its **own** "MUI vs. shadcn/ui" decision framework covering the same distribution-model/CSP/patch-propagation comparison both `mui` and `shadcn-ui` already carry — producing a genuine three-way QR-2 content duplication, not just a stale comment (see per-skill findings below).

None of these were fixed by the reviewing agents (each judged the correction as requiring editorial judgment about what to trim/re-link, not a mechanical one-line fix) — all reported with recommended corrections. Given how many times this exact pattern recurred across the whole Step 28 review (this batch, plus separately in `api-design`, `database-operations`/`search-integration` references, `redis`, `opensearch`, `python`, `nodejs` — see the other batch reports), this is the single most pervasive defect class found in this entire review pass and merits one dedicated repo-wide sweep rather than per-skill patches.

## Per-skill findings

### react
- **[Critical, shared]** `parents` includes nonexistent `SK-FE-005` — see cross-cutting #1.
- **[Low]** `source_references[].retrieved: "2026-09-10"` vs. `research/technologies/react.md`'s own `Research date: 2026-09-09` — one-day offset, appears to be an accepted batch-wide dating convention (same pattern in opentelemetry/sentry), not a unique defect.
- No other issues. Technology-accuracy spot-check came back completely clean (CVE-2025-55182→CVE-2026-23864 two-stage disclosure, `act()` relocation, `useId` prefix change, React Compiler v1.0 details — all verbatim-match the research doc). Boundary against `nextjs` is clean (verified by diffing RSC-related content directly — zero overlap).

### nextjs
- **[Critical, shared]** `parents` includes nonexistent `SK-FE-005` — see cross-cutting #1.
- **[High]** `covered_versions.nextjs` has no upper bound and conflates "minimum patched version" with "version range this skill's content is correct for" (`">=15.5.18 (or >=16.2.6) recommended given the May 2026 forced-upgrade advisory"` vs. the spec's own example shape `">=16 <=17"`). Research confirms current stable is 16.3.4, and the body extensively documents 16.3-specific behavior not reflected in the stated range. Recommend an explicit dual range, e.g. `">=15.5.18 <=15.5.x (patched Maintenance LTS) or >=16.2.6 <=16.3.4 (Active LTS)"`.
- **[Low]** `description` at 491/500 chars — compliant but very little editing headroom.
- **[Low]** Same one-day `retrieved`-date offset as react.
- No other issues. The May-2026 13-advisory coordinated security release (exact CVE, patched versions) matches the research doc precisely, including correctly carrying forward the research doc's own "Unresolved" flag on the August 2026 follow-up rather than inventing a CVE ID for it.

### vue
- No Critical or High issues. Vapor Mode (pre-stable, RC) is handled correctly — the skill explicitly refuses to treat secondary-source "confirmed stable" claims as fact, deferring to the RC status the research doc documents. All version-gated claims (3.5.42 stable/3.6.0-rc.7, `defineOptions`/`defineSlots`/`defineModel()` version gates, Vue 2 EOL, reactivity-model split) match the research doc verbatim.
- **[Low]** `covered_versions` floor of `>=3.3` is narrower than strictly necessary (Composition API core works on any 3.x) — defensible, not wrong.
- **[Low]** `description` at 490/500 chars — tight margin.

### nuxt
- **[High, shared]** Stale "not yet authored" comment for `SK-GROW-001` — see cross-cutting #2.
- **[Medium]** Three Engineering-rules bullets state facts without their own inline `[Source: ...]` marker, though the same facts are sourced elsewhere in the same document (a real but mitigated SG-2 gap).
- **[Medium]** No explicit coverage of Nuxt's own "Universal Rendering" concept, despite the taxonomy catalog note calling it out by name and the research doc naming it as one of three Nuxt-specific rendering modes.
- **[Medium, cross-skill, attributable elsewhere]** `frontend-architecture/SKILL.md` line 61 states Nuxt's v4.5 security post named "four" advisories; the actual count (per `research/technologies/nuxt.md` and nuxt's own correct accounting) is **eight**. This is a factual error in a file *outside* this skill's own scope — correctly flagged for follow-up in `frontend-architecture` rather than fixed here.
- **[Low]** Security section says "seven other advisories" but names only six distinct GHSA IDs (omits one Low-severity dev-server-only item) — a completeness nit, not a false count claim.

### web-standards
- **[High, shared]** Stale "not yet authored" claims for `SK-FE-003` — see cross-cutting #2.
- **[Medium]** The Decision framework is 100% CSS content with zero HTML-specific decision points — may be a legitimate imbalance (HTML-accessibility decisions correctly deferred to `SK-FE-004`) rather than a defect.
- **[Low]** No `Workflow` section, unlike sibling `sass`/`tailwindcss` (may be defensible under CE-4 for a knowledge-heavy skill).
- **[Low]** Empty `adapter_hints: {}` unlike sibling skills and reference templates.
- Positive: verdict on "is this a coherent HTML+CSS merge, or two bolted-together halves" is **coherent, not bolted together** — Knowledge/Engineering-rules/Anti-patterns are genuinely unified lists, not two concatenated sections, and the skill explicitly de-duplicates against `SK-FE-004` (accessibility) rather than restating it. All Baseline-status claims verified verbatim against `css.md`/`html.md`.

### sass
- **[High, shared]** Stale "not yet authored" claim for `SK-FE-003`, with an already-fired-but-unactioned `reverify_triggers` entry specifically for this — see cross-cutting #2.
- **[Medium]** Internal contradiction: declares `execution_tier: A` / `required_capabilities: [file-read, file-write]` (no shell), but `failure_handling` describes a "if shell is unavailable" hedge implying a shell-dependent code path that doesn't actually exist for this skill (its `adapter_hints` correctly stays `[Read, Edit]`, so practical exposure is low — the prose is inconsistent, not the capability grant).
- **[Low]** `required_context: []` populated as empty where a sibling skill populates it — stylistic only.
- No technology-accuracy issues found — every version-sensitive claim (Dart Sass 1.104.0, `@import` deprecation timeline, tar-permissions CVE ranges, Node Sass/LibSass/Ruby Sass EOL dates) matches the research doc exactly, including preserved inference-hedges.

### tailwindcss
- **[High, shared]** Stale "not yet authored" claim for `SK-FE-003` — see cross-cutting #2.
- **[High]** Concrete same-file contradiction: `execution_tier: A` with a comment stating shell-requiring work (running the build or the `@tailwindcss/upgrade` codemod) is "outside this skill's required capabilities" — but `adapter_hints.claude-code.allowed_tools` grants `Bash` explicitly for that exact codemod/build use case. Recommend either reclassifying to Tier B with `shell` added, or removing the `Bash` grant and keeping migration purely advisory (matching sass's more conservative treatment of its own CLI-driven workflow).
- **[Low]** Missing the "SK-FE-003 authored" `reverify_triggers` entry that sibling `sass` has.
- No technology-accuracy issues found — current-version claims, browser floor, color-palette additions, the `@config`/`@plugin` bridge's unsupported-options list, and the lower-confidence `bg-gradient-*`→`bg-linear-*` rename are all correctly sourced and correctly hedged where the research itself is uncertain.

### angular
- **[High]** VA-2 gap: three inline version-tagged claims in `SKILL.md` (`@Service()` decorator v22, `resource()`/`httpResource()` stabilization v22, Vitest-as-default v21+) are not mirrored into `skill.yaml.version_sensitive_claims`, which spec VA-2 requires (tagged both inline **and** in the structured field).
- **[Medium]** `parents` includes nonexistent `SK-FE-005` — see cross-cutting #1 (same underlying issue, counted once there).
- **[Medium]** Inconsistent cross-reference style within the same file — Testing section cites the owning skill by ID (`SK-QA-001`), but Security/Performance cite by slug instead of ID, deviating from the spec's modeled phrasing.
- **[Low]** `covered_versions` upper bound (`<=22.1`) slightly undersells the actually-verified-current patch (research records v22.1.5 live at research time).
- **[Low]** Same one-day `retrieved`-date offset as other skills in this batch.
- **[Low]** Testing section states a Vitest-stabilization version boundary without carrying the research doc's own explicit hedge that this exact boundary "was not independently re-verified."
- No other issues — all other spot-checked facts (TS/Node/RxJS version-floor table, zoneless rename history, CSP header text, `bypassSecurityTrust*` warning) match precisely.

### typescript
- **[Medium]** Security/Performance/Testing sections never name the owning skill by ID or slug (just "the cross-cutting security skill," etc.) — weaker than the spec's modeled phrasing and weaker than this batch's own `angular` practice.
- **[Medium]** No hyperlink anywhere in the body (including References) to the parent skill (`SK-CONV-003`/code-quality) — `angular`'s References section, by contrast, correctly links its parents.
- **[Low]** `covered_versions` upper bound (`<=7.0`) reads as covering only exactly 7.0.0 where the actual current published version is 7.0.2 — `<=7.0.x` would be clearer.
- **[Low]** Same one-day `retrieved`-date offset.
- **[Low]** Heading "Knowledge (essential)" deviates from the spec's canonical "Knowledge" heading and from this batch's own `angular` practice.
- Positive: this is the cleanest VA-2 compliance in the whole batch — every inline version-tagged claim is fully mirrored in `version_sensitive_claims`, in direct contrast to angular's gap above. No duplication found between typescript and angular in either direction.
- A spec-clarity question was raised (not a defect): whether VR-4's "same-or-lower layer" constraint textually governs `parents` as well as `depends_on_skills`. Concluded it textually governs only `depends_on_skills` (given §2.5's sharp categorical distinction and VR-4's own "depends" wording), and is moot for this skill either way (`SK-CONV-003`, Layer 2, is lower than Layer 4 under either reading) — flagged as a spec-wording improvement opportunity, not a live defect.

### mui
- **[High, shared]** Stale "not yet authored" claims for `SK-FE-003`/`SK-FE-002` — see cross-cutting #2.
- **[High]** QR-2 duplication: the "MUI vs. shadcn/ui" distribution-model/CSP/patch-propagation comparison is now independently restated in three places — `mui`'s own Decision framework, `shadcn-ui`'s own Decision framework, and `styling-systems`'s (now-existing) Knowledge/Decision-framework sections — all ultimately tracing to the same `technology-decision-matrix.md §8` source. Recommend trimming both `mui` and `shadcn-ui`'s copies to a pointer at `styling-systems`'s decision framework, keeping only per-library implementation depth in each.
- **[Medium]** `covered_versions` upper bound (`<=9.0`) excludes the actual current npm `latest` (9.4.0, confirmed in the skill's own cited research) — the Security section correctly states "v9.x (current)" is patched, contradicting the narrower `covered_versions` ceiling.
- **[Medium]** Missing `Workflow` section despite MUI usage being a genuine multi-step procedure (confirm version → pick styling API → configure CSP → wrap SSR/RSC provider) — sibling `shadcn-ui` has one for a comparably procedural task.
- **[Low]** `related_skills: []` while the parent `styling-systems` already lists `SK-TECH-mui` back — one-way asymmetry (not wrong, `parents` already captures it, but inconsistent with `shadcn-ui`'s practice).
- **[Low]** Inline `#` rationale comments in `skill.yaml` deviate from the `opentelemetry`/`sentry` reference-template style (some of these comments are also the stale claims above).
- Positive: CSP-nonce mechanism, security-patch-line policy, and vendor-performance-claim hedging all check out precisely against the research doc. `depends_on_skills: []` correctly left empty despite two parents.

### shadcn-ui
- **[High, shared]** Stale "not yet authored" claims for `SK-FE-003`/`SK-FE-002`, plus the same three-way MUI-vs-shadcn duplication as `mui` above (the duplication is even more literal here — a full 6-row comparison table restated near-verbatim) — see cross-cutting #2 and mui's High finding.
- **[Medium]** Tailwind CSS's status as a genuine hard prerequisite is currently signaled only implicitly (via `non_activation_conditions` and a passing `optional_context` mention), never as an explicit `required_context` item, despite being architecturally load-bearing (components are literal Tailwind-utility-class consumers with no CSS-in-JS fallback).
- **[Medium]** `failure_handling` has no rule for "Tailwind isn't actually configured" as a runtime case — relies entirely on the non-activation gate having already filtered it out.
- **[Low]** Several Engineering-rules bullets restate facts sourced earlier in Knowledge without their own inline `[Source: ...]` marker on the restating line (SG-2 completeness gap, mitigated by being sourced nearby).
- **[Low]** Same inline-comment style deviation as mui.
- Positive/verified-correct: `depends_on_skills: []` + `related_skills: [SK-TECH-tailwindcss]` for the Tailwind relationship is the **correct** categorization, not a miscategorization — reviewed in detail against spec §2.5's test (does the skill's own execution *invoke* Tailwind's method as a sub-step? No — it needs Tailwind to already be present, which is exactly the `required_context`/`related_skills`/non-activation-gate pattern the spec prescribes for a hard prerequisite the skill doesn't itself set up). Supply-chain/pinning guidance, CLI command surface, and version-gated defaults (Base UI since July 2026, `new-york` current) all check out precisely against the research doc, including correctly-flagged inferences.

### threejs
- **[Medium]** `source_references` schema misuse: four entries point `url` at internal `research/knowledge-maps/*.md` files instead of an external official documentation URL (spec §2.6 defines `url` as the actual target, `via` as the citing research file — here both fields are the same internal file). Unique to threejs among the skills checked in this batch; the underlying cited content is accurate, this is a field-shape issue, not a factual error.
- **[Medium]** Same execution_tier/capability contradiction pattern as `tailwindcss`: declares `execution_tier: A` / no-shell, but `failure_handling` references "if shell is unavailable" and `adapter_hints` grants `Bash` for running a dev server/build.
- **[Low]** Decision-framework bullets restate sourced claims without their own inline marker (mitigated, same pattern as elsewhere in this batch).
- **[Low]** One activation-condition bullet doesn't name "Three.js" explicitly in isolation (relies on the paired non-activation condition for disambiguation — coherent together, but not self-sufficient alone).
- **[Low, informational]** `skill-catalog.md`'s SK-FE-001 entry doesn't list `SK-TECH-threejs` among its specializing tech skills — a catalog completeness gap, not a defect in the threejs files themselves.
- Positive: threejs's r-number (non-semver) versioning caveat is handled correctly and is the strongest part of the skill — every `reverify_trigger` is phrased in terms of actual r-number-release events rather than a meaningless "next major version" trigger, and `covered_versions` uses prose to state the versioning scheme itself rather than forcing a fake semver-shaped range. No fabricated APIs/flags found anywhere; Security/Performance sections correctly preserve the research doc's own "Unresolved" flags rather than inventing content.

## Overall assessment

No Critical, skill-content-level defects were found in this batch beyond the shared `SK-FE-005` non-existence issue (an architecture-level gap, not any one skill's authoring error). Technology accuracy is uniformly strong across all 12 skills — every reviewer's spot-check against the corresponding `research/technologies/*.md` doc came back clean, with version-sensitive uncertainty consistently preserved rather than papered over. The dominant, recurring theme is **staleness relative to the rest of the library**: skills authored early in the FRONTEND-domain batch, before several of their own forward-referenced parents (`SK-FE-003`, `SK-FE-005`) or siblings (`SK-GROW-001`) existed, were never revisited once those skills landed — producing both factually wrong "not yet authored" claims and, in the mui/shadcn-ui/styling-systems case, genuine content triplication. A second recurring pattern — `execution_tier: A` declarations contradicted by shell-implying `failure_handling`/`adapter_hints` language (sass, tailwindcss, threejs) — suggests the Tier-A/Tier-B boundary needs a clearer authoring checklist, similar to how the required_capabilities/execution_tier VR-5 defect was caught and fixed in the immediately preceding step.
