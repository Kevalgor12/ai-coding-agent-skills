# Final Principal-Engineer Audit — Architecture · Taxonomy · Skill Specification · Dependency Graph · Routing · Activation

Step 33. Categories 1–6 of 26. Read-only: no file in `core/`, `skills/`,
`adapters/`, or `evaluations/` was modified by this pass.

Sibling Step-33 reports cover categories 7–10/15, 11–14/19–20, 16–18/24–25,
and 21–23/26. Where a finding of mine touches theirs, it is cross-referenced
and the *distinct* angle is stated rather than restated.

## Method

1. Read the prior audits that touch these categories in full:
   `2026-09-10-individual-skill-review.md`, all five `cross-skill/` files
   (`dependency-audit.md` and `routing-audit.md` are directly in scope),
   `real-world/synthesis.md`, and the three completed Step-33 sibling reports.
2. Re-verified every prior finding in scope **mechanically against the current
   working tree** — a purpose-written parser loaded all 86 `skill.yaml` files
   and all 86 `SKILL.md` frontmatter/body structures and re-ran VR-1 through
   VR-8, the full reference graph, cycle detection over two edge families,
   layer monotonicity, the catalog↔skill parent diff, exact-match and
   Jaccard-fuzzy VR-6/VR-7 checks, and a marker sweep over every Tier-0 field.
3. Then read the `core/` design documents themselves —
   `taxonomy/` (3 files), `skill-specification/` (3 files + 2 examples),
   `routing-architecture/` (4 files), `dependency-architecture/` (4 files),
   `orchestrator/` (7 files) — plus `adapters/lib/skill_loader.py` and a
   directed sample of ~30 `skill.yaml`/`SKILL.md` pairs, looking for defects in
   these six categories that no prior pass could have caught, because no prior
   pass was scoped as the last gate before release.

**Corpus as it actually stands:** 86 skills (46 generic, 40 technology), 3 at
Layer 0, 4 at Layer 1, 8 at Layer 2, 31 at Layer 3, 40 at Layer 4. 294
activation conditions, 9 `depends_on_skills` edges, 68 `parents` edges, 245
`related_skills` edges, 32 `conflicts_with` edges.

## Verification items (all six categories)

| Item | Result |
|---|---|
| Unnecessary AI branding in `core/` or sampled skill files | **Clean.** Every vendor name found in `core/` (Claude Code, Cursor, Windsurf, Codex, Antigravity, VS Code) is a capability-map-grounded portability statement, an adapter-target enumeration, or an `adapter_hints` key — all legitimate for a vendor-neutral library that must name its targets. No promotional or authorship branding. |
| Removal of legitimate attribution/provenance | **None.** 83 of 86 skills carry `source_references` with `url`/`title`/`via`/`retrieved`; the 3 that do not are exactly the 3 `grounding: engineering-convention` skills, which SG-4 exempts. No `source_ref` field was found stripped. |
| Comments explain WHY, not WHAT | **Clean in the sampled set.** The inline `#` comments in `skill.yaml` files explain design rationale (e.g. `angular/skill.yaml:73-74` explains *why* the parent relationship is not also a `depends_on_skills` edge, citing `specification.md §2.5`). None restate the adjacent line. |
| Phase/Step build-process comments bleeding into skill or design content | **None.** A regex sweep for `^#?\s*(step\|phase)\s+[0-9]` across `core/` and `skills/` returns zero hits. The only step-history references are in `audits/`, where they are legitimate. |

One caveat on the third row, recorded because it is adjacent to the spirit of
the check: `skill-catalog.md` lines 812, 824–827 carry
`**Added post-hoc (2026-09-10)**` annotations inside normative taxonomy rows.
These are build-history notes in design content rather than in `audits/`. They
are defensible (they explain *why* a row's research is younger than its
siblings') and are not step numbers, so I do not raise them as a finding —
but a future taxonomy edit should move the provenance into the row's Notes
prose rather than a bolded build-event marker.

---

# 1. Architecture

The layered design (Layer 0–4), the `core/` directory structure, and the
separation of concerns between `core/`, `skills/`, `adapters/`, `evaluations/`,
`research/`, `audits/`.

## 1.1 Prior findings re-verified

| Prior finding | Source | Status now |
|---|---|---|
| `core/README.md` ends *"Empty for now — no schema or validation logic has been defined yet"* | `cross-skill-audit.md:666-667` said it "**has since been updated**"; Step-33 docs sibling `DOC-N1` says it is still stale | **The cross-skill audit was wrong; the docs sibling is right.** `core/README.md:21` still reads verbatim *"Empty for now — no schema or validation logic has been defined yet."* Step 29's claim that it "has since been updated" does not hold against the current tree. Ownership of the staleness class stays with the docs sibling (`DOC-N1`, Blocker); the architecture-specific slice is my §1.4 below. |
| X-16 — stale skill counts in four design documents | `cross-skill-audit.md:656`; docs sibling confirms 7 sites in 4 files | **Confirmed still live.** Extended in §2.2 (T-1): the taxonomy's counts are not merely stale, they contradict the catalog they summarize. |
| The layered model itself (Layer 0–4, composition flows downward) | `taxonomy/README.md:64-79` | **Sound and honored.** Zero cycles across `depends_on_skills` alone *and* across `depends_on_skills ∪ parents`, verified by independent DFS. The model is the healthiest structural asset in the library; the defects below are at its seams, not in it. |

## 1.2 A-1 · The skill is not the unit of distribution the architecture says it is — **High**

**Finding.** `README.md:52-55` declares the intended dependency direction as
`research ─▶ core ─▶ skills`, and states that `research/` and `examples/`
*"are supporting material that inform and demonstrate the rest, but are never
themselves shipped as skill content."* The actual corpus inverts both halves:

- **212 outbound Markdown links from `SKILL.md` bodies point back up into
  `core/` (89 links) and `research/` (123 links)**, across **73 of the 86
  skills**. `skills/solution-architecture/SKILL.md` alone has 16;
  `skills/workflow-composer/SKILL.md` has 8; `skills/skill-router/SKILL.md`
  has 7.
- **83 of 86 skills' `source_references[].via` fields resolve into
  `research/…`** — which is exactly what SG-1 requires (*"every entry MUST
  resolve through a `research/…` file to an official documentation URL"*).

All 212 links resolve correctly **in-repo** (verified: zero broken relative
links). The defect appears at projection. `adapters/lib/skill_loader.py:140-174`
loads exactly three things from a skill: `skill.yaml`, `SKILL.md`, and files
under `references/`. The body is carried through verbatim (`body=m.group(2)`,
copied as-is by every adapter). Nothing rewrites, inlines, or vendors a
`../../core/` or `../../research/` path. So the moment a skill directory is
installed into a host agent — which is precisely what the `SKILL.md` convention
exists for, and what `adapters/` produces — every one of those 212 links
dangles, and the SG-1 provenance chain that 83 skills depend on becomes
unresolvable at the only place it matters: where an agent is deciding whether
to trust a technical claim.

The architectural statement and the corpus therefore disagree in two directions
at once: `research/` **is** shipped (as the load-bearing half of every
citation), and `skills/` **does** depend on `core/` at read time rather than
only at authoring time. `skills/skill-router/SKILL.md:23` is the clearest
instance — *"Full design: [routing-architecture] (the algorithm and rule
sets)"* — a Layer-0 skill deferring its own normative content to a document
the consumer will not have.

**Root cause.** `core/` and `research/` were treated as a monorepo-internal
concern during authoring, and the spec's §1 table (`skill.yaml` + `SKILL.md` +
`references/`) was never reconciled with the fact that 73 skills cite outside
that boundary. No step owned "what does a consumer actually receive."

**Recommended correction.** A decision, not an edit, and it should be made
before release:
- **(a)** Declare the whole repository the unit of distribution, and say so in
  `README.md` and `specification.md §1` — replacing "never themselves shipped"
  with an explicit statement that `research/` is the provenance store a skill's
  citations resolve against. Cheapest; makes the adapters' output a
  *repo-relative* artifact rather than a portable one, which should then be
  stated in `adapters/README.md`.
- **(b)** Have the adapters vendor cited `research/` excerpts and `core/` rule
  text into each projected skill's `references/`, and rewrite links. Correct,
  but it is real adapter work and a loss-manifest change.
- **(c)** Restrict `SKILL.md` bodies to in-skill links only (a new `[V]` rule),
  moving cross-repo pointers into `skill.yaml` metadata where the adapter
  already records them as governance-only. Cleanest long-term, ~73 files
  touched.

I recommend (a) for this release and (b) as the tracked follow-up, because (a)
is honest immediately and (c) would strip genuinely useful rationale links from
the in-repo reading experience.

## 1.3 A-2 · No precedence rule between `core/` design documents and skill bodies — **Medium**

**Finding.** Three of the five `core/` subdirectories open by declaring
themselves non-normative-by-status: `taxonomy/README.md:3` (*"Status:
**proposed taxonomy** (design only)"*), `routing-architecture/README.md:3`
(*"Status: **design only**"*), `orchestrator/README.md:3` (*"Status: **design
only**"*). Meanwhile `skill-specification/specification.md:1` declares itself
`(normative)`.

But `skills/skill-router/SKILL.md:23` and `:232-243` route the reader *to* the
"design only" routing and orchestrator documents for the rules it operates by,
and `skills/angular/skill.yaml:73` cites `specification.md §2.5` as binding.
There is no document anywhere that says which wins when a `core/` design
document and an authored skill body disagree. This is not hypothetical: §5.2
(RT-1) below documents four documents stating the same early-exit rule in three
mutually inconsistent forms, with no tiebreaker.

**Root cause.** `core/` was authored as design-ahead-of-implementation and the
status lines were never revisited once skills started citing those documents as
their specification.

**Recommended correction.** Add a short precedence clause to `core/README.md`:
the specification is normative; the taxonomy catalog is normative for IDs and
`parents`; the routing/orchestrator/dependency documents are normative for the
rules they define (SR/CS/PR/ER/D/F/R/GA/SB/FV/OB), and a skill body that
contradicts one of them is a defect in the skill, not a local override. Then
replace the three "design only" status lines, which now understate the
documents' authority.

## 1.4 A-3 · `core/README.md` is not an index of `core/` — **Low**

**Finding.** The contract layer's entry point lists four things `core/` is
*"Expected to eventually hold"* and names none of its five actual
subdirectories (`taxonomy/`, `skill-specification/`, `routing-architecture/`,
`dependency-architecture/`, `orchestrator/` — ~4,400 lines of design across 21
files). A reader entering `core/` is told it is empty.

The staleness class is the docs sibling's (`DOC-N1`, Blocker). The
architecture-specific consequence, which is mine: `core/` is the only one of
the seven top-level directories whose README is also its *structural map*, and
its absence is why A-2's precedence question has nowhere to live. When
`DOC-N1` is fixed, `core/README.md` should get a subdirectory table and the
precedence clause together, not just a status-line rewrite.

**Severity Low** in isolation, but it is the natural landing site for A-2's
correction.

---

# 2. Taxonomy

The 5-layer taxonomy, `core/taxonomy/skill-catalog.md` and
`taxonomy-analysis.md`, the ID scheme, and whether the catalog reflects what is
authored.

## 2.1 Prior findings re-verified

| Prior finding | Status now | Evidence |
|---|---|---|
| **X-05** — six catalog IDs with no authored skill | **Confirmed still live, exactly six.** | Catalog-defined, not authored: `SK-FE-005` (`skill-catalog.md:341`), `SK-GROW-002` (`:631`), and four technology-table rows — `SK-TECH-graphql` (`:833`), `SK-TECH-vite` (`:840`), `SK-TECH-google-seo` (`:843`), `SK-TECH-google-adsense` (`:844`). Machine-diffed catalog headings and table rows against all 86 authored `id:` values. |
| **X-16** — stale skill counts (69 / 83) | **Confirmed still live**, and worse than "stale" — see T-1. | `taxonomy-analysis.md:9-12,197` |
| Catalog `parents` ↔ authored `parents` drift | **No drift. This is a clean positive and it is worth stating.** | All **40 of 40** technology skills' `parents` lists match the catalog's technology-table Parent column **exactly**, element-for-element and in order. Machine-diffed. Whatever else is stale in the taxonomy, the single most consequential taxonomy↔skill binding is perfect. |
| ID-scheme conformance | **Clean, 86/86.** | Every generic skill matches `SK-<DOMAIN>-<NNN>` with the domain code equal to its `domain` field; every Layer-4 skill matches `SK-TECH-<slug>`. Zero duplicate IDs. Zero slug/directory mismatches. |

## 2.2 T-1 · The taxonomy's two defining documents state incompatible skill counts — **High**

**Finding.** This goes past X-16's "stale counts." `taxonomy-analysis.md:9-12`
opens with:

> - **Generic skills (Layers 0–3):** 31 proposed.
> - **Technology skills (Layer 4):** 38 proposed, mapping the 44 researched
>   technologies (6 folded via merges — see below).
> - **Total proposed:** 69 skills.

Three numbers, and all three are contradicted by the catalog **in the same
directory**:

| | `taxonomy-analysis.md` says | `skill-catalog.md` actually defines | Actually authored |
|---|---|---|---|
| Generic (L0–L3) | 31 | **48** (3 ORCH + 4 DISC + 8 CONV + 5 FE + 5 BE + 6 DATA + 3 INFRA + 4 QA + 2 GROW + 8 AI) | **46** |
| Technology (L4) | 38 | **44** table rows | **40** |
| Total | 69 | **92** | **86** |

The technology figure is not a rounding drift — it is an arithmetic error that
was true once and was invalidated by the catalog's own later edits. "38 = 44
researched − 6 merges" is correct arithmetic, but the catalog's table already
*applies* those merges (`openapi-swagger`, `jest-vitest`, `web-standards` are
single rows) and then adds four post-hoc observability technologies
(`skill-catalog.md:824-827`) and `nodejs` (`:812`). The table is 44 rows
post-merge; the analysis says 38 post-merge. They cannot both be right.

The generic figure is off by 17 because the same file documents, at
`:152`, that `SK-AI-001` *"was decomposed … into 8 skills"* — and never
returned to line 9 to add the seven.

**Why this is High and not Low.** `taxonomy-analysis.md` is not a summary
document; `taxonomy/README.md:22-26` designates it as the file that holds *"the
required decision analysis: skills to create / merge / split / drop"* and *"the
two explicit rulings the brief demanded."* Its open decision #2
(`:198-200`) asks a human to confirm whether *"~69 skills"* is a sustainable
maintenance load — a question the human would answer differently at 86, and
very differently at the 92 the catalog implies. A governance document that
misstates the size of the thing being governed by 25% is not a typo; the
decision it was written to support cannot be made from it.

**Root cause.** The summary block is a derived value maintained by hand, and
two subsequent taxonomy expansions (the AI decomposition, the observability
research pass) updated the body of the same file without updating its head.

**Recommended correction.** Replace the four summary bullets with counts
derived from the catalog, and state both numbers where they differ (*"92
catalogued, 86 authored, 6 open — see the gap table"*). Then re-read open
decision #2 against the real number before treating it as answered.

## 2.3 T-2 · The taxonomy still presents itself as a pre-authoring gate that was never closed — **Medium**

**Finding.** `taxonomy/README.md:3` reads, verbatim, today:

> Status: **proposed taxonomy** (design only). No skill content exists yet.

86 skills exist. And `taxonomy-analysis.md:191-210` closes with *"Open
decisions for human review **before authoring begins**"* — five decisions,
none marked resolved, including:

- **#1** *"Adopt vs. track agentskills.io. The whole taxonomy assumes the
  `SKILL.md` convention six vendors cite. Confirm the library **adopts** that
  format (the research recommends reading the spec directly first — **still
  unresolved**…)."* The library has since built 86 skills, 6 adapters, and a
  compatibility test suite on that format.
- **#2** the maintenance-load question, which T-1 shows was posed against a
  wrong number.
- **#5** *"confirm the intent that no skill is promoted to `final/` until its
  eval exists and passes."* `final/` is empty and `evaluations/` now holds 16
  scenarios — so the policy is being followed de facto but was never ratified.

**Root cause.** The taxonomy was authored as a gate. The gate was walked past
rather than opened, and nothing wrote down that the walk-past was deliberate.

**Recommended correction.** Update the status line, and convert the five open
decisions into a resolutions table stating how each was in fact decided and
where (build order → Steps 26–28; format adoption → `adapters/`; `final/`
policy → `specification.md §5`). Decisions that were made implicitly are still
decisions; leaving them labelled "open" makes the design record unreadable as
to what is settled.

## 2.4 T-3 · Three Layer-4 skills specialize a Layer-2 parent, contradicting the layer contract — **Medium**

**Finding.** `taxonomy/README.md:77-78` defines Layer 4 as *"Technology
Specializations — one per researched technology; **specializes a Layer-3
skill**."* `specification.md §2.1` repeats it: `parents` is *"the **Layer-3**
skill(s) it specializes."* Three skills do not:

| Skill | `parents` | Target layer |
|---|---|---|
| `SK-TECH-typescript` (`skills/typescript/skill.yaml`) | `SK-CONV-003` code-quality | **2** |
| `SK-TECH-husky` (`skills/husky/skill.yaml`) | `SK-INFRA-002`, `SK-CONV-001` git-conventions | 3, **2** |
| `SK-TECH-openapi-swagger` (`skills/openapi-swagger/skill.yaml`) | `SK-BE-002`, `SK-CONV-006` technical-documentation | 3, **2** |

All three match the catalog exactly, so the skills are not at fault — the
catalog mandates these parents (`skill-catalog.md:817,839,832`) and the layer
contract forbids them.

**Why this is not merely pedantic.** `cross-skill/dependency-audit.md:182-188`
*rejects* Option A for fixing the VR-4 problem — re-layering the QA skills to
Layer 2 — with the explicit reason that it would create `parents` edges running
Layer-4 → Layer-2, *"skipping a layer."* That argument is load-bearing in the
recommendation that the library currently intends to adopt (Option C), and it
is falsified by three edges that already exist. Either layer-skipping `parents`
edges are acceptable — in which case Option A's rejection needs a different
reason — or they are not, in which case three skills and three catalog rows are
non-conforming. The library cannot have it both ways, and the VR-4 decision in
§4.3 depends on which way it goes.

**Root cause.** The layer contract was written for the common case (a
technology specializing a domain capability) and never extended to the three
technologies whose genuine parent is a *convention*, not a domain — which is a
real and defensible category the model simply does not have a slot for.

**Recommended correction.** Amend `taxonomy/README.md`'s Layer-4 line and
`specification.md §2.1` to *"specializes one or more lower-layer generic skills
(normally Layer 3; Layer 2 where the technology specializes a convention rather
than a domain capability)"*, and record the three instances in
`taxonomy-analysis.md`. Then remove the "skipping a layer" argument from the
VR-4 Option-A rejection and re-decide on the remaining grounds, which are
independently sufficient.

---

# 3. Skill specification

The canonical `skill.yaml` + `SKILL.md` + `references/` format, and whether all
86 skills conform.

## 3.1 Prior findings re-verified — and a large clean result

No prior audit ran VR-8 (body section order and required-section presence)
mechanically. I did, across all 86 `SKILL.md` files, against
`specification.md §3.2`'s fixed 15-section order and the kind-conditional
requirements. Combined with re-running VR-1/VR-2/VR-5 and the §4.1
context-efficiency limits, the conformance result is:

| Rule | Result across 86 skills |
|---|---|
| **VR-1** all required fields present and non-empty | **86/86 pass.** Zero missing. Also: zero non-spec fields anywhere in the corpus — every key in every `skill.yaml` is in `specification.md §2`'s schema. |
| **VR-2** name/description parity with `SKILL.md`, slug = directory | **86/86 pass.** Every frontmatter block has exactly the three permitted keys; every `name` and `description` matches `skill.yaml` byte-for-byte after whitespace normalization. |
| **VR-5** `execution_tier` ↔ `required_capabilities` | **86/86 pass.** No Tier-A skill declares a non-universal capability; every Tier-C skill declares one *and* a matching `capability_fallbacks` entry. (The VR-5 defect corrected in Step 27 across 10 skills has not regressed.) |
| **VR-8** body order + required sections | **86/86 in order.** One non-canonical heading (§3.3). |
| Conditional fields (`parents` for technology, `covered_versions`/`reverify_triggers` for technology, `source_references` for official-docs/mixed, `capability_fallbacks` for Tier C) | **86/86 pass.** |
| **CE-1** `description` ≤ 500 chars, `name` ≤ 64 | **86/86 pass.** |
| **CE-2** body ≤ ~500 lines | **86/86 pass.** Zero bodies exceed 500 lines. |

This is a genuinely strong conformance result and it should be stated as
plainly as the defects: the *format* is not where this library's risk lives.
Notably, §2.5's `parents`-vs-`depends_on_skills` distinction — which the spec
itself records as having been violated by 7 of 9 skills in one early batch — is
now honored **86/86**, with zero skills listing a parent in
`depends_on_skills`.

## 3.2 S-1 · The mechanical validator the specification requires does not exist — **High**

**Finding.** `specification.md` tags **27 rules** `[V]` — *"mechanical
validator (schema/lint — pass/fail, automatable)"* (`:7`) — and `§5`
Conformance & lifecycle makes running it a hard precondition:

> 2. Run the mechanical validator (all **[V]** rules) — must pass.
> …
> 5. Only after 2–4 pass may the skill be projected by adapters and promoted to
>    `final/`.

There is no validator in the repository. The only Python is
`adapters/{6 targets}/adapter.py`, `adapters/lib/*.py`, and
`adapters/tests/test_compatibility.py`; a grep for `validat` across all `.py`
files returns zero hits. `core/README.md:9-10` lists *"Shared validation logic
(e.g. 'does this skill conform to the schema')"* as one of `core/`'s four
responsibilities, and `core/` contains no code at all.
`orchestrator/README.md:26-28` states the gap honestly (*"The mechanical
validator and the evaluation suite that would enforce them are separate,
not-yet-built pieces of work"*) — but `evaluations/` has since been built, and
the validator has not.

**Why this is High rather than a tracked TODO.** The two live `[V]` failures in
this report are *exactly* what a validator catches on its first run and a human
reviewer misses for five audit rounds:

- **VR-3** — 9 unresolved ID references (§4.2). Found by Step 28, re-found by
  Step 29, re-found by Step 32, re-found independently by two Step-33 siblings,
  and still present. A 20-line reference-resolution check would have failed the
  build the day it was introduced.
- **VR-4** — 4 layer-monotonicity violations (§4.3). Found by Step 28, analyzed
  at length in Step 29, still present.

Every one of those five human passes cost more than writing the validator. And
because `§5` conditions adapter projection and `final/` promotion on a
validator run that cannot happen, the library's stated conformance lifecycle is
currently unsatisfiable as written — which means "this skill is conformant" is
not a checkable claim about any of the 86.

**Root cause.** `[V]` was used as a *classification* of rules rather than a
commitment to implement the checker, and no build step owned it.

**Recommended correction.** Write it. The checks in this audit's instrument
script are the specification: reference resolution, layer monotonicity, cycle
detection over both edge families, required/conditional field presence,
tier↔capability consistency, frontmatter parity, VR-6 disjointness, VR-7
library-wide trigger uniqueness, and VR-8 section order. It is a few hundred
lines against `skills/*/skill.yaml`, it is the missing `core/` deliverable its
own README already promises, and it converts the recurring cost of these audits
into a one-time cost. This is the single highest-leverage correction available
in my six categories.

## 3.3 S-2 · One non-canonical body heading (VR-8) — **Low**

`skills/typescript/SKILL.md` uses `## Knowledge (essential)` where
`specification.md §3.2` fixes the heading as `## Knowledge`. It is the only
deviation in 86 files. It is cosmetic for a human reader and a hard failure for
a section-order validator, which is the point: the deviation is invisible
today only because S-1's validator does not exist.

**Correction.** Rename the heading. If the parenthetical carries meaning, it
belongs in the first line of the section.

## 3.4 S-3 · Two empty `references/` directories — **Low**

`skills/graphql-api-design/references/` and `skills/web-accessibility/references/`
exist on disk and are empty. Git does not track empty directories, so they are
untracked local artifacts rather than committed content — no `SKILL.md` links
into them (verified: zero broken `references/` links across all 86 bodies), and
`skill_loader.py:162-165` would emit an empty `resource_files` list.

Harmless as-is, but `specification.md §1` makes `references/` the Tier-2
contract, and an empty one is a half-finished intent — both skills are ones
whose bodies are dense enough to plausibly want Tier-2 content. Worth a
deliberate decision (populate or remove) rather than leaving the directories as
ambient state.

---

# 4. Dependency graph

`depends_on_skills` vs `parents` discipline, VR-4, and the actual graph across
all 86 skills.

## 4.1 Prior findings re-verified

| Prior finding | Status now |
|---|---|
| **Zero circular dependencies** (`dependency-audit.md:35-60`) | **Confirmed independently.** DFS over `depends_on_skills` (9 edges, 8 nodes): 0 cycles. DFS over `depends_on_skills ∪ parents` (77 edges): 0 cycles. VR-4's acyclicity half holds absolutely. |
| **No dependency explosions** (`:64-85`) | **Confirmed.** Max hard fan-out 4 (`code-review`), max fan-in 2 (`SK-QA-001`), 81 of 86 skills declare no hard dependency. |
| **D-01** — 3 catalog `Dependencies:` lines overstate the edge | **Confirmed still live.** `data-migration`'s `related_skills` remains `[SK-DATA-001, SK-DATA-002]`; `authentication-authorization` and `deployment-release` likewise unchanged. Step 29's recommendation (fix the catalog, not the skills) is still the right one and has not been applied. |
| **D-02** — `data-migration` is missing the safety-net dependency `refactoring` has | **Confirmed still live.** `skills/data-migration/skill.yaml:59` — `related_skills: [SK-DATA-001, SK-DATA-002]`; `SK-QA-001` appears in no field. |
| **X-03** — conflict matrix and `conflicts_with` disagree in both directions | **Confirmed still live, both directions.** Matrix clusters with **zero** implementing edges: Realtime transport (`webrtc ⊥ socketio ⊥ websocket-api`, 0/6), API paradigm (`api-design ⊥ graphql-api-design`, 0/2), OLAP-vs-OLTP (`clickhouse ⊥ postgresql/mysql`, 0/4 — `clickhouse` declares no conflicts at all). Conversely the runtime cluster `go ⊥ nodejs ⊥ python` has all 6 edges declared and appears nowhere in `matrices.md#conflict-matrix`. |
| `conflicts_with` symmetry | **Clean positive, not previously checked.** All 32 edges across 18 skills are reciprocated; zero asymmetric declarations. |
| `parents`/`depends_on_skills` conflation (§2.5) | **Clean positive.** Zero skills list a `parents` target in `depends_on_skills`. |

## 4.2 DG-1 · Nine `parents`/`related_skills` references resolve to no authored skill — VR-3 — **Critical**

*This finding is structurally mine (category 4) and is formally owned here.
Two Step-33 siblings independently flagged it; I verified it directly and
independently rather than inheriting it.*

**Finding, verified.** A reference-resolution pass over `parents`,
`depends_on_skills`, `related_skills`, and `conflicts_with` across all 86
`skill.yaml` files finds exactly **9 references to 3 IDs that no authored skill
provides**:

| Missing ID | Site | Field |
|---|---|---|
| `SK-FE-005` | `skills/angular/skill.yaml:9` | `parents` |
| `SK-FE-005` | `skills/nextjs/skill.yaml:9` | `parents` |
| `SK-FE-005` | `skills/nuxt/skill.yaml:9` | `parents` |
| `SK-FE-005` | `skills/react/skill.yaml:9` | `parents` |
| `SK-FE-005` | `skills/vue/skill.yaml:9` | `parents` |
| `SK-FE-005` | `skills/performance-engineering/skill.yaml:57` | `related_skills` |
| `SK-FE-005` | `skills/seo-optimization/skill.yaml:59` | `related_skills` |
| `SK-GROW-002` | `skills/seo-optimization/skill.yaml:59` | `related_skills` |
| `SK-TECH-graphql` | `skills/graphql-api-design/skill.yaml:59` | `related_skills` |

No other reference in the corpus fails to resolve. The count matches both
sibling reports exactly.

**Why Critical.** VR-3 is a `[V]` rule; these are 9 hard failures of it. The
five `parents` sites are the severe subset, because `parents` is
**conditionally required** for `kind: technology` (`specification.md §2.1`) and
is the edge that says *where a technology skill's method comes from*. Five of
the library's most-used skills — React, Next.js, Vue, Nuxt, Angular, i.e. the
entire frontend framework surface — each declare that half their method is
inherited from a skill that does not exist. The consequence is documented, not
theoretical: `routing-architecture/examples.md` Examples 2 and 5 — **both of
the two examples the project brief specifically mandated** — place
`rendering-strategy` in the **selected** set (`:74`, `:161`), so the library's
own worked proofs that routing produces correct sets describe routings it
cannot produce (`routing-audit.md` R-01).

The one mitigating fact, and it is a real one: every affected skill carries an
explicit inline comment disclosing the forward reference. This is honest
authorship, not concealment. But an honest dangling pointer is still a dangling
pointer, and the honesty lives in a `#` comment that no consumer of the
metadata reads.

**Root cause.** A deliberate forward-reference convention adopted during
authoring (author the technology skill before its generic parent, annotate the
gap, resolve later) that no step was ever assigned to close. It survived five
review rounds because each round correctly classified it as "one decision, not
N patches" and then no step made the decision.

**Recommended correction — and a constraint the prior audits did not surface.**
Step 28 framed this as Option A (author the three skills) vs Option B (drop the
references). **Option B is not freely available for `SK-FE-005`.**
`taxonomy-analysis.md:121` lists `rendering-strategy` as one of the six
mandatory split targets for the "Frontend" capability area, with the stated
reason that a single frontend skill *"would load styling machinery for an
architecture question."* Dropping `SK-FE-005` therefore reopens a ruled taxonomy
split, and — per `routing-audit.md:79-83` — leaves the SSR/SSG/ISR rendering-mode
decision with no owner, which Step 32 independently re-derived as a live gap
(scenario `S18`, *rendering-mode-decision-no-owner*).

So:
- **`SK-FE-005` rendering-strategy: author it.** It is referenced 7 times, it is
  a mandated split target, it owns a decision five framework skills explicitly
  disclaim, and both mandated routing examples need it. This is the single
  highest-value unit of new authoring left in the library.
- **`SK-GROW-002` web-monetization** (1 reference, catalog-marked *"(thin)"*)
  and **`SK-TECH-graphql`** (1 reference; `SK-BE-003 graphql-api-design` already
  covers schema/resolver design): drop both references and mark both catalog
  entries `deferred — not planned for this release`. Dropping 2 `related_skills`
  entries costs nothing; `related_skills` is an affinity hint with no hard
  semantics.

Either way, `examples.md` must be re-run afterward (R-01) — a dropped or
authored `SK-FE-005` changes two of the eight worked routings.

## 4.3 DG-2 · Four `depends_on_skills` edges violate layer monotonicity — VR-4 — **High**

**Confirmed still live**, exactly as `dependency-audit.md:132-148` reports, and
re-derived independently:

```
SK-CONV-007 code-review          (L2) → SK-QA-002 security-engineering    (L3)
SK-CONV-007 code-review          (L2) → SK-QA-003 performance-engineering (L3)
SK-CONV-005 legacy-modernization (L2) → SK-QA-001 testing-strategy        (L3)
SK-CONV-004 refactoring          (L2) → SK-QA-001 testing-strategy        (L3)
```

`specification.md` VR-4 (*"a skill depends only on same-or-lower layers"*) and
§2.5 (*"MUST be same-or-lower taxonomy layer"*) both forbid these. Step 29's
analysis — that the edges are correct and the rule is over-strict, and that
VR-4 should be split into VR-4a (acyclicity, absolute) and VR-4b (monotonicity
with a declared cross-cutting exception) — is sound and I endorse it without
modification.

**I raise the severity from Step 29's Medium to High**, for one reason Step 29
did not have in view: it treated this as an open design question, which was
correct at Step 29. At Step 33 it is a shipped library that fails its own
normative `[V]` rule on four edges, with no validator to detect it (S-1) and no
documented exception to excuse it. The defect is no longer "a rule needs
refining"; it is "the conformance claim is false and nothing in the repository
records that." Either fix is cheap — implement Option C's VR-4a/VR-4b split, or,
if that is deferred, add one paragraph to `specification.md §4.2` naming these
four edges as a known, accepted, reviewed exception. What is not acceptable is
shipping with an unqualified `[V]` rule the corpus violates.

**Cross-reference:** T-3 shows that Option A's rejection rests partly on an
argument (layer-skipping `parents` edges are disallowed) that three existing
skills already falsify. The VR-4 decision should be re-checked against T-3
before it is executed.

## 4.4 DG-3 · Conflict matrix ↔ `conflicts_with` divergence — **High** (re-verified X-03)

Confirmed above. I add one consequence X-03 did not draw, which raises my
confidence in its High rating: the **realtime transport** cluster (0 of 6 edges
declared) is the cluster `routing-architecture/examples.md:75` depends on. That
example writes the realtime branch as `realtime-communication → (socketio |
websocket-api)` — the `|` denoting a resolved choose-one. SR-4 resolves conflict
clusters *before* selection, and its lookup is the matrix; but the router's
machine-readable source is `conflicts_with`, which declares no relationship
among the three transports at all. On any realtime task, the three transport
skills all pass SR-3 detection independently and nothing in the skill metadata
excludes two of them. This is over-activation on exactly the capability the
brief's second mandated example is built around.

**Correction.** Declare the 12 missing edges in the three unimplemented
clusters, and add the runtime cluster to the matrix — with R-04's
"same service/artifact" scoping applied so the fix does not import R-04's
polyglot self-exclusion bug into three more clusters.

## 4.5 DG-4 · Four technology skills are referenced by no other skill — **Low**

`SK-TECH-docker`, `SK-TECH-opensearch`, `SK-TECH-threejs`, and
`SK-TECH-webrtc` appear in **zero** `parents`, `depends_on_skills`,
`related_skills`, or `conflicts_with` field of any of the other 85 skills. Every
other skill in the library has at least one inbound edge.

Three of the four are explicable (`threejs` and `webrtc` are genuinely
specialized leaves; `opensearch` is one of several search back-ends). The
outlier is **`docker`**: `containerization` (`SK-INFRA-001`) is its declared
parent and `taxonomy-analysis.md:108` records the two as *"unified"* — yet
`containerization` does not list `SK-TECH-docker` in `related_skills`, while
every comparable Layer-3 hub does list its specializations (`styling-systems`
lists 5, `observability` lists 4, `database-operations` lists 4). The
asymmetry means the standard "hub lists its specializations" table-of-contents
pattern has a hole exactly where the taxonomy says the coupling is tightest.

**Correction.** Add `SK-TECH-docker` to `containerization`'s `related_skills`;
leave the other three, and record in `dependency-architecture/README.md` that
inbound-edge-free technology leaves are expected, so a future graph check does
not flag them.

---

# 5. Routing

`core/routing-architecture/`, SR-1…SR-11 / CS-1…CS-8 / PR-1…PR-5 / ER-1…ER-6,
and whether the routing logic is coherent and complete.

## 5.1 Prior findings re-verified

Every Step-29 routing finding was re-checked against the authored metadata, not
against the audit's description of it.

| Prior finding | Status now | Evidence |
|---|---|---|
| **R-01** · examples select/exclude 6 non-existent skills; both mandated examples affected | **Confirmed still live.** | `examples.md:74` and `:161` place `rendering-strategy` in **selected** sets; `:38,66,92` exclude `rendering-strategy`/`web-monetization`/`google-seo`/`google-adsense`. `:119` still reads *"effectively all 68 other skills"* — there are 85. |
| **R-02** · the `debug` intent has no skill to route to | **Confirmed still live.** No skill in the 86 has a `debug`/`bug-fixing` identity. `routing-algorithm.md:22` still classifies `debug` as one of 12 intents; `rules.md:115-116` ER-5 still points twice at `bug-fixing`; `examples.md:159` still selects an unattributed `⟳ debugging loop` with no skill ID. |
| **R-03a** · `code-quality` ⟷ `refactoring` unresolved, with a safety consequence | **Confirmed still live, verbatim.** `code-quality` non-activation is only `["A throwaway snippet", "…quick spike…"]`; `refactoring` non-activation is only `["New feature work…", "No way to verify behavior…"]`. Neither names the other. The safety-net asymmetry (`refactoring` hard-depends on `SK-QA-001`, `code-quality` does not) is real. |
| **R-03b** · `observability` ⟷ `performance-engineering` unresolved | **Confirmed still live.** `observability` non-activation covers local code and resilience patterns only; `performance-engineering` non-activation covers DB/caching only. Neither mentions the other. |
| **R-03c** · `web-accessibility` absent from ER-6's review facets | **Confirmed still live.** `rules.md:118-122` ER-6 names quality, comment, security, performance facets; no UI/a11y facet. |
| **R-03d** · `legacy-modernization` → `data-migration` guard is one-directional | **Confirmed still live.** `data-migration/skill.yaml:33` routes out to `legacy-modernization`; the reverse clause is absent. |
| **R-04** · `go`/`nodejs` runtime guards self-exclude on polyglot repos under SR-2 | **Confirmed still live, verbatim.** `go`: *"The stack uses Node.js or Python (route to that runtime's skill)"* — unscoped. `nodejs`: *"The stack runs on Go, Python, or another non-Node runtime"* — unscoped. `python`: *"…with **no Python component**"* — correctly scoped. The correct wording exists in the library and two of three siblings do not use it. |
| **R-05 / X-04** · ER-1 unimplementable for 27 skills | **Confirmed still live, exactly 27, mechanically.** 27 of 86 skills have an empty/absent `escalation` field; **all 27** have a substantive `## Escalation` body section (>60 chars of real content). Zero skills have the inverse. Includes `deployment-release` (the production-deploy gate), `database-operations`, `ci-cd-pipeline`, `containerization`. |
| **R-06** · review loop has no Tier-0 trigger | **Confirmed still live** as to the gap — `code-review` activation remains `["A change is up for review", "The user asks for a code review", "A pre-merge gate is in play"]`, none of which fires on *a skill in this run just produced an edit*. **But its stated blocker is incorrect** — see §6.4 (AC-3). |
| **G-5** (Step 32, Critical) · SR-2 excludes the only skills that can surface a self-contradictory request | **Confirmed still live, verbatim.** `requirements-engineering/skill.yaml:33` — *"The requirements are already explicit, unambiguous, and narrowly scoped"* — is worded per-clause, so a conjunction of two individually-clear, mutually-inconsistent instructions satisfies it and SR-2 excludes the skill. |
| **VR-6 / VR-7 hold exactly** (`routing-audit.md:39-41`) | **Confirmed, and strengthened** — see §6.1. |
| The router skill body faithfully implements the core rule sets | **Largely confirmed** — `skills/skill-router/SKILL.md` reproduces SR-1/2/3/5/6/8/9/10/11, CS-1/2/5, ER-1/4/5 in prose, plus the D6 authored-vs-catalog check. **One divergence** — RT-1 below. |

## 5.2 RT-1 · The trivial-task early exit bypasses gate declaration and the capability barrier, and is stated in three mutually inconsistent forms — **Critical**

**Finding.** Four documents state the trivial-task early exit. None of them
conditions it on **risk**, and they do not agree with each other on what it
skips:

| Source | What it says the trivial path skips |
|---|---|
| `routing-algorithm.md:36-38` (Phase 1 early exits) | *"activate the one owning skill (+ conventions if it writes code); **skip discovery and the composer**. Stop after ordering."* |
| `routing-algorithm.md:120-122` (decision tree) | *"activate the one owning skill … **Skip discovery + composer**. ─▶ ORDER ─▶ END"* |
| `orchestrator/lifecycle.md:76-78` | *"a trivial single-owner change **exits after P2** with one skill and no plan."* |
| `skills/skill-router/SKILL.md:82-83` | *"Activate the one owning skill, plus conventions if it writes code, and stop. **No discovery, no composer, no adapter.**"* |

Three different scopes for one rule. The router skill's form is the broadest —
it explicitly bans the capability adapter — and it is the form an agent will
actually read, because the skill body is what loads at runtime while the `core/`
documents are (per A-2) "design only."

**The consequence is a safety defect, not a style inconsistency.** In the
decision tree at `routing-algorithm.md:109-153`, the trivial exit is placed at
line 120 — **before** the risk branch (`:142`, *"Complexity ≥ multi-step OR risk
≥ destructive?"*), **before** the adapter barrier (`:146`), and **before**
`:151`'s *"insert ⤾ review · ⛔ gates."* In the lifecycle, exiting after P2 skips
**P4 entirely**, which is where `lifecycle.md:162-163` places gate declaration
(*"Every gate the plan will hit is enumerated now"*) and D12/D13 (per-step
capability decision; plan admission).

`rules.md:103-106` ER-2 states that destructive, outward-facing, and production
actions *"require explicit human approval — **a hard stop, non-overridable by
any skill** (safety-rules contract)."* The trivial exit overrides it, not by
permitting the action, but by exiting before the phase that would have named
the gate — and `skill-router`'s own Engineering rules (`SKILL.md:145`) still
assert *"Surface every approval gate the task will hit before work starts,"*
which the path it just took cannot do.

Complexity and risk are **independent axes** in this architecture
(`README.md:45,47` lists them as determinations 3 and 5), and the exit is keyed
only on the first. Concrete instances that classify as trivial-single-owner and
destructive simultaneously:

- *"Drop the `sessions_old` table."* → single owner `data-migration`, trivial,
  **destructive**. `matrices.md#escalation-matrix` has an explicit
  `data-migration → destructive migration ↑ human` row.
- *"Force-push my branch."* → single owner `git-workflow`, trivial,
  **destructive** (history rewrite). Also an explicit matrix row.
- *"Run the migration."* → Tier B; the adapter barrier is skipped outright under
  the router skill's formulation, so a host without shell produces
  advisory-shaped output with no capability negotiation.

The worked example at `lifecycle.md:286-300` is *"add a comment explaining this
function"* and is annotated `(trivial, **read-only**)` — which is the correct
case and shows the authors had the right instance in mind. The rule they wrote
around it simply does not carry the `read-only` qualifier the example relies on.

**Root cause.** Proportionality (`orchestrator/README.md:111-114`, principle 1)
is a genuinely important design goal, and it was expressed as a *complexity*
predicate in the routing layer before the *risk* axis was fully separated out in
the orchestrator layer. The four statements then drifted because no document
owns the canonical form (A-2).

**Recommended correction.** Three edits, all small, all mechanical:
1. Add a risk guard to the predicate in all four sites: *"a trivial
   single-owner change **whose risk class is read-only or reversible-write**
   exits after P2."* A trivial task at `destructive` or above takes the normal
   path from P3 onward.
2. Make the four statements identical, and make `skill-router/SKILL.md`'s the
   derived one. In particular, delete *"no adapter"* — SR-7 already conditions
   the adapter on Tier B/C, which is the correct and narrower rule, and a
   trivial Tier-B task needs the barrier.
3. Add the corresponding guard to `lifecycle.md`'s Trivial-task collapse
   section so the `(trivial, read-only)` annotation in the example becomes a
   stated precondition rather than an incidental property.

**Severity Critical** — this is the only finding in my six categories where a
correct-by-design safety control (ER-2, declared non-overridable) is silently
defeated by another correct-by-design control (proportionality), on task shapes
that are common rather than exotic. It should block release absent the
one-clause guard above, which is cheap enough that "mitigate and ship" is not
obviously preferable to "fix and ship."

## 5.3 RT-2 · The default-deny architecture presumes an arbiter the metadata never establishes — **High**

**Finding.** The entire routing model is written as though a router runs first
and arbitrates. But nothing in the skill metadata, the adapter projection, or
the host-agent contract establishes that:

- **`skill-router` is an ordinary `activation_mode: auto` skill.** 85 of 86
  skills are `auto`; the one exception is `project-management` (`manual`). No
  skill uses `always`. So in a host agent's progressive-disclosure model — which
  `taxonomy/README.md:41-43` correctly identifies as the universal mechanism
  (*"Every ecosystem loads only a skill's `name` + `description` up front"*) —
  `skill-router` competes for selection against 85 peers on description match,
  exactly like `postgresql` does.
- **Its own non-activation stands it down on the cases that need it most.**
  `skills/skill-router/skill.yaml:37` — *"A single, unambiguous skill clearly
  owns the task — let it trigger directly."* Determining that a single skill
  clearly owns a task **is the routing decision**. The router is instructed to
  exclude itself based on a conclusion only it can reach. Under SR-2
  (non-activation is decisive), this is not a soft hint.
- **The adapters project no precedence.** `adapters/lib/skill_loader.py:116-117`
  exposes `activation_mode` and each adapter maps it to a per-vendor invocation
  flag, but there is no ordering, priority, or "consult first" concept anywhere
  in the projection — `SK-ORCH-001` lands in the target as one skill among 86.
- **`layer: 0` is explicitly not projected.** `skill_loader.py:74` lists `layer`
  in `IDENTITY_ONLY_FIELDS` — *"never meant to be projected into any target's
  frontmatter or body (a consuming agent doesn't need to see a skill's Layer
  number)."* That reasoning is right for a domain skill and wrong for the
  orchestration layer: Layer 0 is the *only* place the layer number carries
  runtime meaning, and it is discarded.

So the library's central claim — *"activate the minimum appropriate skill set"*
via default-deny (`routing-architecture/README.md:11`) — rests on a component
that has no mechanism to run first, and that tells itself not to run on
single-owner tasks. `core/orchestrator/README.md:14-18` is admirably honest
that *"There is no scheduler… The consuming agent **is** the runtime"* — but it
then assumes the host enacts the discipline *"by loading three Layer-0 skills"*,
without specifying how those three come to be loaded ahead of the other 83.

**Root cause.** The orchestrator layer was designed as a discipline and the
skill layer as a corpus, and the bootstrapping handshake between them — how the
host is told to consult the router first — was never assigned to either.

**Recommended correction.** A design decision, and it belongs in this release:
1. Set `skill-router` and `capability-adapter` to `activation_mode: always`
   (the enum value exists, `specification.md §2.3`: *"`always` (standing)"*, and
   is currently used by nothing). `always` is exactly what a standing arbiter
   needs, and each adapter already has to map the enum.
2. Rewrite `skill-router`'s first non-activation condition so it is a
   *post-routing* suppression rather than a *pre-routing* exclusion — e.g.
   *"After classification, the final set is a single skill — suppress further
   routing involvement and let that skill run"* — which is what SR-7 actually
   says and what the body's decision-framework step 11 already describes.
3. State the bootstrapping contract explicitly in `adapters/README.md` and
   `orchestrator/README.md`: what a host must do for the discipline to hold, and
   what degrades if it does not.

Without (1) and (2) the default-deny model is aspirational rather than
operative, and every routing finding in this report is downstream of a mechanism
that may never engage.

## 5.4 RT-3 · SR-4's lookup table is not Tier-0 metadata, contradicting CS-1 — **Medium**

**Finding.** `rules.md:20-24` SR-4 resolves conflict clusters *before*
selection, and its lookup is
`../dependency-architecture/matrices.md#conflict-matrix` — a prose table in a
`core/` design document. `rules.md:53-54` CS-1 states: *"Selection uses `name` +
`description` + activation/non-activation. **Never load a skill body** to decide
whether to select it."* The conflict matrix is neither Tier-0 metadata nor a
skill body; it is a third source with no place in the model, and CS-1 makes no
provision for it.

This is defensible in practice — the router's *own* body is legitimately loaded,
and `skill-router/SKILL.md:240-241` lists `matrices.md` in its References — but
it means the library has **two independent encodings of the same fact**
(`matrices.md#conflict-matrix` and 86 `conflicts_with` fields) with no stated
precedence, and DG-3 proves they have already diverged in both directions.

**Root cause.** `conflicts_with` was specified as a per-skill field and the
matrix as a routing lookup, and neither was declared derived from the other.

**Recommended correction.** Declare `conflicts_with` the single source of truth
and `matrices.md#conflict-matrix` a generated view of it — then regenerate the
matrix, which mechanically resolves DG-3's divergence in one direction and
surfaces the 12 missing edges as diffs. Add a CS-rule permitting the router to
consult library-level lookup tables carried in its own body, so SR-4 stops
contradicting CS-1 on a technicality.

---

# 6. Activation

`activation_conditions` / `non_activation_conditions` / `activation_mode` across
all 86 skills; VR-6 and VR-7.

## 6.1 Prior findings re-verified

| Prior finding | Status now |
|---|---|
| **VR-6** — activation and non-activation sets disjoint | **Confirmed clean, 86/86**, and strengthened beyond the prior exact-match check. I additionally ran a fuzzy content-word Jaccard comparison across all 294 activation conditions and all non-activation conditions within each skill. Only one pair exceeds 0.55 similarity: `code-review`'s *"A change is up for review"* vs *"No change exists to review"* (J=0.67) — a correct logical negation, not an overlap. VR-6 holds substantively, not just literally. |
| **VR-7** — no two skills share an identical activation trigger | **Confirmed clean, 86/86**, likewise strengthened. Fuzzy comparison across all 42,921 cross-skill activation-condition pairs surfaces exactly two above J=0.60, both structural-template similarity with distinct semantics (`drizzle.config.ts` vs `nuxt.config.ts` file-presence; MySQL-dialect vs PostgreSQL-dialect ORM detection). No genuine trigger collision exists in the library. |
| **M-06** (Step 32, Critical) — `database-operations`' activation conditions are all symptom-shaped | **Confirmed still live, verbatim.** `skills/database-operations/skill.yaml:29-33` — all four conditions require the *request text* to already name the symptom (*"slow query"*, *"N+1 … suspected"*, *"pool … exhaustion"*, *"isolation-level decision is needed"*). A greenfield feature with an implicit concurrency requirement reaches none of them. |
| **F1-DB / F3.1** (Step 32, Critical) — coverage-range and session-storage gaps | **Confirmed still live.** `security-engineering/skill.yaml:35` non-activation — *"No trust boundary or sensitive data is involved"* plus a route-out to `authentication-authorization` — is unchanged, so F3.1's gap persists. |
| **X-02** — stale "not yet authored" markers | **Confirmed still live, and larger than Step 32 scoped it** — 60 marker lines across 32 files. The overall staleness class is owned by the Step-33 adapters sibling (`R18-1`/`M24-4`, 17 annotations). **The routing-critical subset is mine — see AC-1.** |

## 6.2 AC-1 · Ten false "not yet authored" markers sit inside `non_activation_conditions` — the one field SR-2 makes decisive — **Critical**

**Finding, and the distinct angle.** Both Step-33 siblings correctly identified
the stale-marker class as a documentation-accuracy defect. It is also, in a
specific and much smaller subset, a **routing-correctness defect**, and that
subset is the load-bearing one.

A sweep of every Tier-0 field (`name`, `description`, `activation_conditions`,
`non_activation_conditions`) across all 86 skills finds **10 markers inside
`non_activation_conditions` that declare an authored skill unauthored**:

| Site | The condition, verbatim | Named target | Actually |
|---|---|---|---|
| `api-design/skill.yaml:34` | *"Realtime/bidirectional transport design (route to realtime-communication, not yet authored)"* | `realtime-communication` | **`SK-BE-004`, authored** |
| `containerization/skill.yaml:37` | *"CI/CD pipeline design itself … (route to ci-cd-pipeline, not yet authored)"* | `ci-cd-pipeline` | **`SK-INFRA-002`, authored** |
| `data-migration/skill.yaml:33` | *"… broad technology/pattern modernization … (route to legacy-modernization, not yet authored)"* | `legacy-modernization` | **`SK-CONV-005`, authored** |
| `data-modeling/skill.yaml:34` | *"The schema is fixed and the task is query/index tuning against it (route to database-operations, not yet authored)"* | `database-operations` | **`SK-DATA-003`, authored** |
| `deployment-release/skill.yaml:41` | *"CI/CD pipeline definition itself … (route to ci-cd-pipeline, not yet authored)"* | `ci-cd-pipeline` | **authored** |
| `docker/skill.yaml:44` | *"Deep cross-cutting security threat modeling … (route to security-engineering, SK-QA-002, not yet authored)"* | `security-engineering` | **`SK-QA-002`, authored** |
| `frontend-architecture/skill.yaml:33` | *"Pure styling work with structure already settled (route to styling-systems, not yet authored)"* | `styling-systems` | **`SK-FE-003`, authored** |
| `mui/skill.yaml:44` | *"… generic styling-system or design-token choice … (route to styling-systems, not yet authored)"* | `styling-systems` | **authored** |
| `mui/skill.yaml:45` | *"… UI/UX design judgment … (route to ui-ux-design, not yet authored)"* | `ui-ux-design` | **`SK-FE-002`, authored** |
| `search-integration/skill.yaml:40` | *"A simple indexed `WHERE`/lookup query suffices (route to database-operations, not yet authored)"* | `database-operations` | **authored** |

(Exactly one marker in the field is *correct*: `vue/skill.yaml:43`, which names
`SK-FE-005` — genuinely unauthored per DG-1.)

**Why this is a routing defect and not a stale comment.** These are not `#`
comments. They are the *string values the router reads*, in the field the
architecture gives decisive authority:

- **CS-1** restricts selection to Tier-0: `name` + `description` +
  activation/non-activation. These strings are inside that boundary; nothing
  else the router may read contradicts them.
- **SR-2** makes non-activation decisive: *"If a skill's non-activation
  conditions match the signals, exclude it — even if its activation also
  matches."* So the router acts on this exact text.
- **D6** (`lifecycle.md:114-117`) then tells the orchestrator what to do with
  the claim: *"Is a candidate skill authored, or only a catalog entry? A catalog
  entry is a design spec, not a usable skill. **An unauthored ID must never be
  planned as if it existed**; the gap is recorded and the run proceeds with the
  nearest authored skill or an explicit 'no skill covers this' note."*
- **`skill-router`'s own Engineering rules** (`SKILL.md:143-144`) repeat it as a
  hard rule: *"Never plan an unauthored skill: a taxonomy catalog entry is a
  design spec, not a usable skill — verify the skill directory exists before
  planning it,"* and its `failure_handling` (`SKILL.md:208-209`) prescribes the
  degradation: *"If a candidate skill exists only as a catalog entry, record the
  gap and **route to the nearest authored skill**."*

Put together: the router reads a decisive Tier-0 field, is told by it that the
correct hand-off target does not exist, and is instructed by three separate
normative rules to record a gap and degrade to something else. The library's
own safety machinery converts a false label into the wrong action, reliably.

**This failure mode is worse than DG-1's.** DG-1's nine dangling references
fail *closed* — the ID resolves to nothing, D6 fires correctly, and the run
records an honest gap. AC-1 fails *open*: the skill exists, is correct, and is
ready, and the metadata tells the router to route around it. Ten working edges
are silently downgraded, and nothing in the run record will say so, because
from the router's point of view it followed D6 correctly.

The consequence is not speculative. Step 32's **M-06** — one of the five
Critical findings — traces a live-auction task in which the bid handler ships
with no isolation level and no row lock, and names as one of its two proximate
causes *"a stale `data-modeling` cross-reference ('not yet authored')"* — i.e.
row 4 of the table above, `data-modeling/skill.yaml:34`, on the
`data-modeling → database-operations` edge. That is one of the ten, demonstrated
end-to-end on a real task. The other nine sit on edges of the same kind,
including `docker → security-engineering` (the container security hand-off) and
`deployment-release → ci-cd-pipeline` (the deploy/pipeline boundary).

**Root cause.** The forward-reference authoring convention (see DG-1) was
applied inside `non_activation_conditions` — a runtime field — as though it were
a comment, and no back-fill pass ran when the referenced skills were
subsequently authored. The convention was sound; its placement was not.

**Recommended correction.** Delete the four words from all ten sites. This is a
mechanical edit with no design decision attached, no behavior change beyond
restoring the intended route, and no risk. It should be the *first* correction
applied in Step 34.

Then close the class structurally, because 60 marker lines remain across the
corpus (the adapters sibling's `M24-4` owns the other 50): add a `[V]` rule —
call it **VR-10** — *"No Tier-0 field (`description`, `activation_conditions`,
`non_activation_conditions`) may assert the authoring status of another skill;
authoring status is derived from the corpus, never declared."* The router already
has D6 to determine authoring status from the filesystem; a skill asserting it in
metadata is asserting a fact it cannot keep true. One validator check (S-1)
prevents every recurrence.

## 6.3 AC-2 · `activation_mode` carries no architectural information — **Medium**

**Finding.** The enum is `auto | manual | always` (`specification.md §2.3`).
Across 86 skills the distribution is **85 `auto`, 1 `manual`
(`project-management`), 0 `always`**. A field that is constant across 98.8% of
the corpus is not carrying information, and two of its three values are doing no
work.

Two specific consequences:

- **The three Layer-0 orchestration skills are `auto`, identically to
  `postgresql`.** As RT-2 develops, `always` is precisely the semantic a
  standing arbiter needs, it exists in the spec, and it is unused. The
  architecture's only mechanism for expressing "this skill is structurally
  different from a domain skill" is `layer: 0` — which `skill_loader.py:74`
  deliberately does not project.
- **`capability-adapter` is the clearest `always` candidate and is `auto`.**
  Its first activation condition (`skill.yaml:32`) is *"A Tier B or Tier C skill
  is about to act"* — a run-state predicate, not a task-text or repo signal. A
  standing skill evaluating run state on every step is exactly what `always`
  describes; `auto` describes description-match selection at intake, which is
  not how this skill works.

**Root cause.** `activation_mode` was specified as a per-vendor invocation-flag
carrier (its stated purpose in §2.3) and never used as a design lever, so every
skill took the default.

**Recommended correction.** Land it with RT-2: set `skill-router` and
`capability-adapter` to `always`, and add a one-line rationale in
`specification.md §2.3` for when each value applies, so the next 86 skills do
not all default again. If the decision is instead that `always` is not
projectable across the six adapter targets, say so in the spec and remove the
value — an enum member no skill may use is worse than no enum member.

## 6.4 AC-3 · A prior finding's stated blocker is incorrect (correction, not a new defect)

`routing-audit.md:369-372` (R-06) recommends giving `code-review` a Tier-0
trigger for the run-internal case, then states the blocker:

> That is a run-state-dependent trigger, which is a new *kind* of activation
> signal for this library (**all 86 skills currently trigger on task text or
> repo signals**), so it is a design decision rather than a field edit.

**The parenthetical is false, and it makes R-06 look harder than it is.** Three
skills already use run-state activation triggers:

- `capability-adapter/skill.yaml:32-34` — *"A Tier B or Tier C skill is about to
  act"*; *"A declared capability is denied, revoked, or discovered unavailable
  **partway through a run**"*; *"A workflow step requests parallelism … the host
  may not support."*
- `workflow-composer/skill.yaml:34-35` — *"**A stage did not succeed** and the
  run needs a recovery decision"*; *"**A run is approaching completion** and
  needs final validation."*
- `skill-router/skill.yaml:35` — *"**Evidence found mid-run** suggests the
  active skill set is wrong or incomplete."*

So the precedent exists, in the Layer-0 skills, in the same field. R-06's
recommended fix — add an activation condition to `code-review` equivalent to
*"a skill in the current run has produced an edit that has not yet been
reviewed"* — is a **field edit consistent with existing library convention**,
not a new activation paradigm requiring a design decision. R-06's severity
(Medium) is right; its cost estimate is wrong, and correcting it materially
improves the case for fixing it in Step 34 rather than deferring it.

I record this rather than bury it because the brief asks explicitly which prior
findings were incorrect, and because an overstated implementation cost is how a
correct Medium finding gets deferred indefinitely.

---

# Findings summary

**New findings from this pass (15):**

| ID | Category | Finding | Severity |
|---|---|---|---|
| RT-1 | 5 Routing | Trivial-task early exit bypasses gate declaration and the capability barrier; stated in 3 inconsistent forms; no risk guard | **Critical** |
| AC-1 | 6 Activation | 10 false "not yet authored" markers inside `non_activation_conditions`, the field SR-2 makes decisive; defeats D6 | **Critical** |
| A-1 | 1 Architecture | 212 `skills/`→`core/`+`research/` back-edges break on adapter projection; inverts the declared dependency direction; breaks SG-1 provenance at the consumption site | **High** |
| T-1 | 2 Taxonomy | `taxonomy-analysis.md` counts (31/38/69) contradict `skill-catalog.md` (48/44/92) and reality (46/40/86) | **High** |
| S-1 | 3 Specification | The `[V]` mechanical validator required by §5 does not exist; 27 `[V]` rules unenforced; 2 live `[V]` failures shipped | **High** |
| RT-2 | 5 Routing | Default-deny presumes an arbiter no metadata establishes; `skill-router` is `auto` and self-excludes on single-owner tasks | **High** |
| A-2 | 1 Architecture | No precedence rule between "design only" `core/` documents and skill bodies | Medium |
| T-2 | 2 Taxonomy | Taxonomy still labelled pre-authoring; 5 "open decisions before authoring begins" never closed | Medium |
| T-3 | 2 Taxonomy | 3 Layer-4 skills have Layer-2 `parents`, contradicting the layer contract *and* the argument used to reject VR-4 Option A | Medium |
| RT-3 | 5 Routing | SR-4's lookup is a `core/` prose table, not Tier-0 — contradicts CS-1; two unsynchronized encodings of conflicts | Medium |
| AC-2 | 6 Activation | `activation_mode` is 85/86 constant; `always` unused where it is the correct semantic | Medium |
| A-3 | 1 Architecture | `core/README.md` is not an index of `core/`; no home for the precedence rule | Low |
| S-2 | 3 Specification | `typescript/SKILL.md` non-canonical `## Knowledge (essential)` heading (VR-8) | Low |
| S-3 | 3 Specification | Two empty untracked `references/` directories | Low |
| DG-4 | 4 Dependencies | 4 technology skills have zero inbound edges; `containerization` omits `docker` from `related_skills` | Low |

**Prior findings re-verified as still live and carried forward (17):**
DG-1 (VR-3, **Critical**, formally owned here) · M-06 (**Critical**) ·
G-5 (**Critical**) · DG-2 (VR-4, **High**, severity raised from Medium) ·
DG-3 (X-03, **High**) · X-05 (**High**) · R-01 (**High**) · R-02 (**High**) ·
R-05/X-04 (**High**) · DG-4′ D-01 (Medium) · D-02 (Medium) · R-03a (Medium) ·
R-03b (Medium) · R-03c (Medium) · R-04 (Medium) · R-06 (Medium, cost estimate
corrected — AC-3) · R-03d (Low).

**Prior findings found incorrect:** two. `cross-skill-audit.md:666-667`'s claim
that `core/README.md` *"has since been updated"* is false (§1.1).
`routing-audit.md:370`'s claim that no skill uses a run-state activation trigger
is false (§6.4).

**Totals across all 32 findings recorded:** Blocker 0 · **Critical 5** ·
**High 10** · Medium 12 · Low 5.

---

# Release-readiness contribution

**On the evidence in these six categories alone, I would block release** — but
narrowly, and with a short, fully-specified path to unblocking.

The reason is not the volume of findings. The format conformance is excellent
(VR-1, VR-2, VR-5, VR-8, CE-1, CE-2 all pass 86/86; zero cycles; zero VR-6 or
VR-7 violations even under fuzzy comparison; all 40 technology skills'
`parents` match the catalog exactly; `conflicts_with` fully symmetric; §2.5's
parents-vs-dependencies discipline honored 86/86 after an early batch violated
it 7-of-9). The layered model is sound, the default-deny routing model is well
reasoned, and the cross-routing discipline in `non_activation_conditions` is
better than I expected to find. This library's technical substance is not in
question.

I would block for three specific things. First, **two Critical defects in the
routing and activation layer that are active, not latent**: RT-1 lets a
correctly-designed, explicitly non-overridable safety gate be skipped on common
task shapes ("drop this table", "force-push this branch") because the early exit
is keyed on complexity and never on risk; and AC-1 puts ten false
"unauthored" assertions inside the exact field SR-2 makes decisive, causing the
router to route *around* ten working skills — a failure that is already
demonstrated end-to-end by Step 32's M-06 on the `data-modeling →
database-operations` edge, and that sits on the container-security and
deployment-pipeline edges too. Both fail in the direction that produces
confident, well-formed, wrong output, which is the failure mode this library's
entire gate-and-exclusion architecture exists to prevent.

Second, **the library fails two of its own normative `[V]` rules** (VR-3 on 9
sites, VR-4 on 4 edges) while the mechanical validator that `specification.md
§5` makes a precondition for adapter projection and `final/` promotion does not
exist (S-1). That combination means "conformant" is not a checkable claim about
any of the 86 skills, and it is why the same two defects have now survived five
consecutive review rounds. For a library explicitly intended for serious
production software engineering, an unenforceable conformance claim is itself
the defect.

Third, **RT-2**: the default-deny router — the mechanism every other routing
guarantee in this report depends on — has no established way to run first, and
tells itself to stand down on single-owner tasks. If that handshake never
engages in a real host, the routing architecture is a well-specified design that
does not execute, and none of the other routing findings matter in the way the
documents assume.

What makes this a *narrow* block rather than a deep one: the corrections are
small and almost entirely mechanical. AC-1 is deleting four words from ten
lines. RT-1 is one risk clause propagated to four sites plus deleting *"no
adapter"*. DG-1 is one authoring decision (`SK-FE-005`) plus dropping two
`related_skills` entries. DG-2 is either Step 29's already-designed VR-4a/VR-4b
split or one honest paragraph naming four accepted exceptions. RT-2 is two
`activation_mode` values and one rewritten non-activation condition. T-1, T-2,
A-2, A-3 are documentation edits to files that already contain the right
content. Only S-1 is genuine new engineering, and it is a few hundred lines that
would have caught DG-1, DG-2, S-2, and AC-1's whole class automatically — the
highest-leverage work left in the library by a wide margin.

I would ship this after a bounded Step-34 correction pass covering the five
Critical findings, DG-2, S-1, and RT-2. I would not ship it before one, and I
would not accept "documented mitigation" in place of fixing RT-1 or AC-1, since
both are cheaper to fix than to describe.
