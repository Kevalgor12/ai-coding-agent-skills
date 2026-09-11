# Final Principal-Engineer Audit — Context Efficiency, Skill Quality, Technology Accuracy, Version Awareness, Documentation

Date: 2026-09-11. Categories 7, 8, 9, 10, 15 of 26. Read-only: no file in
`skills/`, `core/`, `adapters/`, `evaluations/`, or `research/` was modified,
and no git command was run.

**Method.** For every prior finding on record touching these five categories,
the claim was re-executed against the current working tree rather than
accepted from the prior report. Where a prior audit reported a count, the
count was recomputed. Beyond re-verification, six whole-corpus mechanical
sweeps were run that no prior step ran in this form: CE-2 line counts across
all 86 bodies, CE-1 description lengths across all 86 (both files),
`covered_versions`-vs-`failure_handling` coverage across all 40
version-scoped skills, URL-into-research-file resolution for all 854
`source_references` entries, QR-4 anti-pattern-section semantics across all
86 (keyword pre-filter, then manual reading of the 25 that failed it), and a
forward-reference-resolution sweep across all cross-reference prose.

Scripts used are throwaway and live in this session's scratchpad; every
number below is reproducible from the file paths cited.

---

## 1. Context efficiency (CE-1, CE-2, CE-3, Tier-2 deferral)

### Prior findings re-verified

| Prior finding | Source | Status now |
|---|---|---|
| CE-2: all 86 bodies under the ~500-line ceiling; mean 277, median 278, max 472 (`redis`), min 129 (`project-management`) | `context-audit.md`:23-26 | **Confirmed, reproduced exactly.** My independent `wc -l` sweep returns max 472 `redis`, min 129 `project-management`. **0 of 86 exceed 500 lines; 0 exceed 550.** The next four are `react` 433, `opentelemetry` 412, `angular` 408, `tailwindcss` 383. |
| CE-1: corpus well inside the 500-char `description` cap | `context-audit.md`:118 | **Confirmed and tightened.** **0 of 86 exceed 500 chars** in either `skill.yaml` or `SKILL.md` frontmatter; corpus max is 499. Additionally **86/86 descriptions are byte-identical between the two files** (VR-2's description clause is clean). |
| C-01 — `related_skills` appears in every skill and in zero routing rules; recommended adding rule CS-9 | `context-audit.md`:36-87 | **Confirmed still live, and now worse.** `core/routing-architecture/rules.md` defines CS-1 through CS-8 only; the string `CS-9` appears nowhere under `core/`. Meanwhile `evaluations/evaluation-spec.md` now cites CS-9 twice (`:41`, `:77`) as established grounding — see DOC-N3. |
| C-02 — Tier-0 selection cost (~9,600 tokens) and its scaling ceiling undocumented | `context-audit.md`:91-128 | **Confirmed still live.** No skill count, token figure, or hierarchical-routing threshold appears in `core/routing-architecture/README.md`. |
| C-03 / C-04 — lazy stage-scoped loading holds; cost profile correctly inverted (frequent skills small, large skills detection-gated) | `context-audit.md`:132-190 | **Confirmed.** The five Layer-2 conventions are still among the smallest: `refactoring` 169, `git-conventions` 174, `code-commenting` 178, `code-review` 179, `code-quality` 180. The four largest are still all Layer-4 detection-gated technology skills. |
| Tier-2 discipline good; 28 files, none auto-loaded | `context-audit.md`:28-32 | **Confirmed, with one new wrinkle** (CE-N2): 28 files but **30** `references/` directories. |
| F4-FE — `frontend-architecture/skill.yaml:33` still says "route to styling-systems, **not yet authored**" | `frontend-product-listing.md`:313-334 | **Confirmed still live, verbatim.** `styling-systems` exists as `SK-FE-003`. |
| Step 32 scored frontend-product-listing "Context efficiency: **Fail**" (`threejs`/`socketio` loadable on a task touching neither) | `frontend-product-listing.md`:375 | **Confirmed still live.** Quantified: `threejs` 329 lines + `socketio` 337 lines ≈ 666 lines (~17K tokens) loadable on a product-listing task. The non-activation clauses at `threejs/skill.yaml:40` and `socketio/skill.yaml:39` are unchanged and still absence-scoped. (Routing remediation is another agent's category; recorded here as the confirmed *context* consequence.) |

**Mechanically clean, stated as results rather than impressions:**

- CE-2: **0 of 86** `SKILL.md` bodies exceed 500 lines.
- CE-1: **0 of 86** descriptions exceed 500 chars (max 499).
- CE-3: **0** code blocks of ≥30 lines anywhere in the 86 bodies; exactly **1** inline table of ≥8 rows (`shadcn-ui`). The "don't inline Tier-2 bulk" rule is respected essentially perfectly.
- CE-6: **0** broken `references/` links from any body; no body auto-loads Tier-2.
- Body structure: all 9 always-required sections present in **86/86**.

### New findings

#### CE-N1 · Stale forward references are a context-cost defect, not only a metadata one — **High**

**Finding.** Prior audits treated the "not yet authored" markers as a
*hygiene* problem (X-02: "a wrong sentence"). A full sweep of the
cross-reference prose shows they are also the **stated authoring rationale
for the library's largest bodies**, and therefore the direct cause of the
duplication findings that have been tracked separately since Step 28.

Classifying every forward-reference site by whether the target now exists:

| Referenced skill | Exists? | Skills still calling it unauthored |
|---|---|---|
| `SK-FE-003` styling-systems | **yes** | `web-standards`, `sass`, `frontend-architecture`, `mui`, `tailwindcss` |
| `SK-DATA-004` caching-strategy | **yes** | `redis` |
| `SK-BE-004` realtime-communication | **yes** | `redis`, `api-design` |
| `SK-DATA-005` search-integration | **yes** | `redis` |
| `SK-DATA-003` database-operations | **yes** | `data-modeling`, `search-integration` |
| `SK-INFRA-002` ci-cd-pipeline | **yes** | `deployment-release`, `containerization` |
| `SK-QA-002` security-engineering | **yes** | `docker` |
| `SK-FE-002` ui-ux-design | **yes** | `mui` |
| `SK-GROW-001` seo-optimization | **yes** | `nextjs`, `nuxt` |
| `SK-CONV-005` legacy-modernization | **yes** | `data-migration` |
| `SK-CONV-006` technical-documentation | **yes** | `code-commenting` |
| `SK-CONV-001` git-conventions | **yes** | `deployment-release` (never was true) |
| `SK-BE-005` authentication-authorization | **yes** | `api-design` |
| `SK-FE-005` rendering-strategy | **no** | `react`, `angular`, `vue`, `nuxt`, `nextjs`, `seo-optimization`, `caching-strategy` — *legitimate* |

**16 skills carry a false marker; exactly one referenced skill (`SK-FE-005`)
is genuinely unauthored.**

The context consequence is explicit in the text. `redis` — the library's
single largest body at 472 lines — states its own sizing rationale at
`skills/redis/SKILL.md:27-30`:

> All three are **forward references, not yet authored anywhere in this
> library**, so this skill stays self-contained and comprehensive on Redis's
> own facts rather than assuming depth it can't yet borrow from them.

All three of those parents (`caching-strategy`, `realtime-communication`,
`search-integration`) are authored and on disk. The same sentence pattern
appears in `sass`, `tailwindcss`, `mui`, `web-standards` and `docker`. This
is not a wrong sentence — it is a **design decision made on a false premise
and never revisited**, and it is precisely why `caching-strategy` restates
Redis pipelining facts (QR-N-prior, §2) and why `styling-systems` re-derives
the MUI-vs-shadcn comparison its two children own.

**Root cause.** X-02's root cause, one level deeper: nothing re-checks
forward references when a referenced skill lands, *and* skills authored
under an absence encoded that absence as scope rather than as a pointer.
The build order created the premise; no step ever retired it.

**Recommended correction.** The mechanical sweep X-02 already recommended
(16 skills), but with an explicit second pass the prior recommendation did
not name: for each of the 6 skills that cite absence as a *self-containment
rationale* (`redis`, `sass`, `tailwindcss`, `mui`, `web-standards`,
`docker`), the corrected sentence must decide whether the content stays or
moves — deleting the clause alone leaves the duplicated content in place
with its justification removed. Pair with the repo-level guard X-02 asked
for ("no Tier-0 field names a resolvable skill ID with an unauthored
qualifier"), which would have caught all 16 automatically.

#### CE-N2 · Two empty `references/` directories ship in the library — **Low**

**Finding.** `skills/graphql-api-design/references/` and
`skills/web-accessibility/references/` exist and contain zero files. The
corpus has 30 `references/` directories holding 28 files.

**Root cause.** Scaffolded Tier-2 directories for planned content that was
never written, or content that moved inline and left the directory behind.

**Recommended correction.** Delete both directories, or add the intended
file. No body links into either, so there is no broken reference — the cost
is that any adapter or validator enumerating Tier-2 resources sees a
declared-but-empty tier. Confirm against `adapters/lib/skill_loader.py`
before deleting, in case an empty directory is load-bearing there.

---

## 2. Skill quality (QR-1, QR-2, QR-4, writing quality)

### Prior findings re-verified

| Prior finding | Source | Status now |
|---|---|---|
| X-17 — 284 `owned_knowledge` topics, zero exact collisions; QR-2's machine-checkable half satisfied | `cross-skill-audit.md` | **Confirmed** (not re-derived independently; the three named prose-level exceptions below were re-verified directly instead). |
| X-06 / Step 28 #1 — `caching-strategy` restates `redis`'s technology-specific facts from the same primary source | `cross-skill-audit.md`, `individual-skill-review.md`:133-143 | **Confirmed still live.** `skills/caching-strategy/SKILL.md:70-77` carries Redis pipelining/single-thread performance claims citing `redis.io/docs/latest/develop/using-commands/pipelining/` — the same primary source `redis` cites, for content `redis`'s `owned_knowledge` claims. Mitigated but not removed by the hand-off at `:135-136`. |
| X-06 / Step 28 #1 — `search-integration` restates `opensearch`'s shard-sizing numerics | same | **Confirmed still live.** `skills/search-integration/SKILL.md:64-67` states "10–30GB shards", a technology-specific numeric fact owned by `opensearch`. |
| Step 28 #2 — triple duplication of the MUI-vs-shadcn/ui comparison across `mui`, `shadcn-ui`, `styling-systems` | `individual-skill-review.md`:144-148 | **Confirmed still live.** `skills/styling-systems/SKILL.md:52-66` re-derives the distribution-model and patch-propagation trade-off in full before deferring at `:66`. |
| Step 28 #4 — "roughly 20+ skills" link to `core/taxonomy/skill-catalog.md` where they mean a sibling `SKILL.md` | `individual-skill-review.md`:160-169 | **Confirmed still live and larger than reported:** **28 `SKILL.md` files, 68 links.** See QR-N2. |
| QR-4 asserted as satisfied library-wide ("the anti-over-engineering trap every skill's Anti-patterns section is required to name") | `evaluation-spec.md`:49 | **Incorrect as stated.** See QR-N1. |

### New findings

#### QR-N1 · Nine skills' Anti-patterns sections name no over-engineering trap, and they cluster in exactly the domains where over-engineering is most expensive — **High**

**Finding.** QR-4 has two clauses: the decision framework must include the
simplest viable option, **and** "anti-patterns MUST name at least one
over-engineering trap for the domain"
(`core/skill-specification/specification.md:202`). The second clause was
checked mechanically (keyword pre-filter over each body's Anti-patterns
section, 25 candidates) and then by reading all 25 sections in full, since
keyword matching is a weak proxy for QR-4.

**Result: 86 of 86 skills have an Anti-patterns section. 9 name no
over-engineering trap at all:**

| Skill | What its 5 anti-patterns actually are |
|---|---|
| `authentication-authorization` | 5 under-engineering / security-omission traps |
| `ci-cd-pipeline` | 5 under-engineering / security traps |
| `containerization` | 5 correctness / perf / security traps |
| `deployment-release` | 5 correctness / honesty / confirmation traps |
| `husky` | 5 misconfiguration traps |
| `security-engineering` | 5 insufficient-defense traps |
| `seo-optimization` | 6 correctness traps |
| `sentry` | 4 correctness traps |
| `webrtc` | 5 correctness traps |

`git-workflow` is borderline (its "imposing a branching model" item is an
over-*imposition* trap, not a complexity trap) and is not counted above.

`webrtc` does not merely omit the trap — its final item **inverts** it:
*"TURN deployment is a baseline requirement, not an edge-case optimization"*
(`skills/webrtc/SKILL.md`, Anti-patterns). Every item in that section pushes
toward more machinery. A skill whose Anti-patterns section exclusively
argues for more engineering supplies no counterweight at all.

The 77 that pass do so clearly and are worth naming as the standard:
`caching-strategy` ("Reaching for Redis reflexively"), `testing-strategy`
("E2E-testing everything" *and* its inverse "Unit-testing trivial getters"),
`search-integration` ("Standing up a dedicated search engine before checking
whether the database already in use covers the need"), `styling-systems`
("Adding runtime theming machinery for a fixed single brand"),
`legacy-modernization` ("Proposing a big-bang rewrite"),
`performance-engineering` ("Micro-optimizing a component that isn't the
actual bottleneck").

**Root cause.** Domain instinct, applied uniformly and therefore
systematically wrong in one direction. All nine misses are
security/infrastructure/operations skills, where the author's mental model
of "what goes wrong" is *insufficiency* — an unrotated secret, a missing
TURN server, a too-permissive token. In those domains the anti-pattern list
writes itself as a list of omissions, and nobody asked the second question.
But these are also the domains where over-engineering is most expensive to
unwind: an over-built auth scheme, a CI pipeline with gates nobody can pass,
a five-signal observability stack on a three-service system. The library's
anti-over-engineering guarantee is weakest exactly where it is worth most.

**Consequence beyond the rule.** `evaluations/evaluation-spec.md:49` grounds
behavioral dimension 13 (Maintainability) in "the anti-over-engineering trap
every skill's Anti-patterns section is required to name (QR-4)". For these
nine skills that grounding does not exist, so a dimension-13 assertion
against any of them cannot be scored as the spec intends.

**Recommended correction.** Add one over-engineering trap to each of the
nine Anti-patterns sections. These are authoring edits, not architecture,
and the shape is available from the passing 77. Candidates, offered as
starting points rather than final text: `authentication-authorization` —
building a custom permission DSL where three roles and a middleware check
suffice; `ci-cd-pipeline` — adding stages/environments the team has no
capacity to keep green; `containerization` — multi-stage builds and
distroless bases on a service with one dependency; `deployment-release` —
canary infrastructure for a service with no traffic to split;
`security-engineering` — a threat model for assets the system does not hold;
`webrtc` — a full SFU where a two-peer mesh is the actual requirement;
`sentry` — instrumenting every span on a service whose errors are already
one stack trace deep. Re-check `git-workflow` in the same pass.

#### QR-N2 · 68 cross-reference links across 28 skills send the reader to the taxonomy catalog instead of the sibling skill — **Medium**

**Finding.** Step 28 estimated "roughly 20+ skills"; the mechanical count is
**28 `SKILL.md` files carrying 68 such links**: `api-design`,
`authentication-authorization`, `backend-architecture`, `ci-cd-pipeline`,
`code-quality`, `code-review`, `containerization`, `data-modeling`,
`deployment-release`, `fastify`, `frontend-architecture`, `git-workflow`,
`graphql-api-design`, `mongoose`, `nextjs`, `orm-integration`,
`project-management`, `react`, `realtime-communication`, `refactoring`,
`requirements-engineering`, `search-integration`, `security-engineering`,
`solution-architecture`, `technical-documentation`, `testing-strategy`,
`threejs`, `web-accessibility`.

These sit in the Security / Performance / Testing sections — the places
where a skill defers to `SK-QA-001/002/003` — so the reader following a
deferral lands on a 169-line taxonomy catalog rather than on the skill that
owns the answer. The link resolves, so VR-3 never flagged it.

**Root cause.** A templating artifact propagated across the authoring
batches; fixed piecemeal by individual Step 28 reviewers (5 in
`tech-infra-qa-realtime`, 2 in `openapi-swagger`) and never swept.

**Recommended correction.** One mechanical sweep rewriting
`core/taxonomy/skill-catalog.md` targets to `../<slug>/SKILL.md` based on
the skill named in the link text. Low risk — the link text already names the
intended target in nearly every instance. This is the single
highest-count, lowest-risk correction available in these five categories.

#### QR-N3 · One section-name deviation breaks VR-8 uniformity — **Low**

**Finding.** `skills/typescript/SKILL.md` uses `## Knowledge (essential)`
where the other 85 use `## Knowledge`. The spec names the section
"Knowledge" (`specification.md:143`); VR-8 requires body section presence
and order to match §3.2.

**Root cause.** An author echoing the spec's descriptive gloss ("Essential
facts only") into the heading itself.

**Recommended correction.** Rename to `## Knowledge`. Trivial, but it is the
one heading in 86 files that a mechanical VR-8 validator would trip on, so
it is worth clearing before the validator is built rather than after.

**Writing quality across the sample read (positive).** Roughly 20 bodies
were read in whole or in substantial part (`redis`, `postgresql`, `nodejs`,
`caching-strategy`, `search-integration`, `styling-systems`,
`performance-engineering`, `testing-strategy`, `webrtc`, `sentry`,
`tailwindcss`, `observability`, `security-engineering`, `refactoring`,
`technical-documentation`, `ui-ux-design`, `seo-optimization`,
`legacy-modernization`, `containerization`, `git-conventions`). QR-1 holds
throughout: no section read as advice that would apply to "any software"
without the skill's context. The anti-pattern entries in particular are
consistently concrete and consequence-bearing ("Copying source before
installing dependencies — invalidates the dependency-install cache layer on
every source change"), not generic maxims. Prose is compressed and says each
thing once; QR-5 is not at risk anywhere I looked.

---

## 3. Technology accuracy (SG-1, SG-2, SG-3)

### Prior findings re-verified

| Prior finding | Source | Status now |
|---|---|---|
| **Critical, explicitly NOT fixed** — `nodejs`'s `version_sensitive_claims` states native TypeScript type-stripping reached "Stable >=25.2.0/24.12.0"; neither number appears in the cited research doc | `individual-skill-review.md`:89-98 | **Confirmed still live, unmitigated, carried through five audit rounds.** See TA-N1. |
| "Technology accuracy across the 40 Layer-4 skills is uniformly strong… only one genuine fabricated-fact defect in the entire 86-skill corpus" | `individual-skill-review.md`:187-192 | **Confirmed by independent mechanical check.** No second unsupported-source defect was found; see the SG-1 sweep below. |
| Two missing `source_references` entries added (`search-integration`, `testing-strategy`) | `individual-skill-review.md`:84-85 | **Confirmed resolved** — both now carry populated `source_references`. |
| SG-1: `grounding: official-docs` ⇒ `source_references` non-empty | spec `:183` | **Clean: 0 violations of the non-empty clause** across all 86. |

**The SG-1 provenance sweep — the strongest result in this audit.** All 854
`source_references` entries across the 86 skills were resolved end to end:

- **854/854** `via:` paths point at a file that exists on disk (68 distinct
  research files).
- **275/275** `source_ref:` lines inside `version_sensitive_claims` name
  research paths that exist.
- Of the 746 entries whose `url:` is an external documentation URL,
  **746 — 100% — appear verbatim in the `research/` file they claim to come
  from.** Zero broken provenance chains.

This is the explicit verification item on attribution: **no legitimate
attribution or provenance has been removed, and none is fabricated.** The
one defect below (TA-N1) is not a broken chain — the chain resolves; the
*claim* asserts more than the file at the end of it says.

SG-3 is also mechanically satisfied: **40 of 40** technology skills carry
explicit "verify against current docs"/re-verification hedging. SG-2 marker
density across the 40 technology skills runs from 14 (`husky`) to 58 (`go`),
median 34 — no technology skill is carrying API claims with a bare handful
of markers.

### New findings

#### TA-N1 · `nodejs` asserts two version numbers that appear nowhere in its cited source, and the skill's own verification rule cannot detect it — **Critical** *(inherited, re-confirmed at the final gate)*

**Finding.** `skills/nodejs/skill.yaml:197`:

```
applies_to: "experimental >=22.6.0; default-on >=23.6.0/22.18.0; Stable >=25.2.0/24.12.0; --no-strip-types added in 26.0.0"
source_ref: "research/technologies/nodejs.md §1/§4/§13, https://nodejs.org/api/typescript.html"
```

`research/technologies/nodejs.md` was read in full for every type-stripping
passage (lines 56, 96, 120, 172, 212, 273). It supports **v22.6.0**
(type-stripping introduced), **v23.6.0/v22.18.0** (`--input-type` values
updated), and **v26.0.0** (`--no-strip-types` added). It makes **no
stability claim of any kind**, and the strings `25.2` and `24.12` do not
occur anywhere in the file. Three of the four version assertions trace; the
fourth — the one that tells a reader the feature is production-ready — does
not.

**Root cause, and why it survived five rounds of review.** This is Step 32's
"metadata-execution gap" thesis instantiated inside the grounding rules
themselves. The skill's own `verification[0]` reads *"Any Node.js version
claim is tagged with the release line/range it applies to"*
(`skill.yaml:218`). The claim **is** tagged. VA-2 passes. SG-1 passes — the
`via` file exists and the external URL resolves into it. `last_verified:
"2026-09-10"` is present, so VA-4 passes. Every mechanical check in the
library returns green on a claim whose content is unsupported, because no
rule compares the *assertion* to the *text* of the source. SG-3 is the rule
that would catch it, and SG-3 is marked `[A]` — audit-only, human judgment.
Step 28 exercised that judgment correctly, flagged it Critical, and
explicitly deferred it; Steps 29–32 ran cross-skill, adapter and real-world
passes that had no reason to revisit a single `applies_to` string.

**Recommended correction.** One of two, before release, not both:

1. Re-verify against `https://nodejs.org/api/typescript.html` and, if the
   stability milestone is confirmed, add it to
   `research/technologies/nodejs.md` first so the chain is real — then the
   skill claim inherits a genuine source.
2. If it cannot be confirmed, replace the segment with the marker the
   research corpus already uses for this situation.
   `research/technologies/nodejs.md:19` documents the convention:
   *"Uncertain claims are marked 'Unresolved: …'"*. The corrected
   `applies_to` would end at `--no-strip-types added in 26.0.0` with an
   `Unresolved:` note on the stability milestone.

Option 2 is available today and requires no external lookup. Shipping the
string as-is is the only outcome that should be excluded — it is the
library's single instance of a technology claim stated more confidently than
its evidence, in a library whose entire value proposition is that it does
not do that.

#### TA-N2 · 16 `source_references` entries route provenance through `core/` design documents instead of `research/`, closing the chain inside the project — **Medium**

**Finding.** The spec types the field precisely: `via` is *"the `research/…`
file that cites it"* (`specification.md:89`), and SG-1 requires every entry
to *"resolve through a `research/…` file to an official documentation URL"*
(`:183`). Sixteen entries across seven skills set `via` to a `core/`
document — this project's own design output:

| Skill | `core/` documents cited as provenance |
|---|---|
| `workflow-composer` | `dependency-architecture/matrices.md`, `dependency-architecture/workflows.md`, `orchestrator/failure-recovery-and-escalation.md`, `orchestrator/lifecycle.md`, `orchestrator/security-and-validation.md` |
| `skill-router` | `dependency-architecture/matrices.md`, `orchestrator/lifecycle.md`, `routing-architecture/routing-algorithm.md`, `routing-architecture/rules.md` |
| `capability-adapter` | `dependency-architecture/dependency-graph.md`, `orchestrator/lifecycle.md`, `taxonomy/README.md` |
| `code-commenting` | `taxonomy/taxonomy-analysis.md` |
| `code-quality`, `code-review`, `refactoring` | `taxonomy/skill-catalog.md` (one each) |

For the three Layer-0 orchestration skills this is *substantively* honest —
their subject matter genuinely is this library's own design, and citing
`core/` is more accurate than inventing an external source would be. The
defect is that the schema has no way to say so: `grounding` offers only
`official-docs`, `engineering-convention`, and `mixed`, and all seven of
these skills are declared `mixed`, which asserts a partial external chain
that does not exist.

**Root cause.** A missing enum value. The spec anticipated
externally-grounded and convention-grounded skills, not skills grounded in
the library's own contract layer — which only became a category when Layer 0
was authored at Step 27, well after the spec was fixed.

**Recommended correction.** Preferred: add a `grounding` value (e.g.
`internal-design`) with an SG-4-style exemption, and a matching `via`
type-widening in §2, then re-declare the three orchestration skills. Cheaper
alternative: leave `grounding: mixed` and add one sentence to SG-1 allowing
`core/` as a terminal `via` for `layer: 0` skills. Either way the four
Layer-2 conventions skills (`code-commenting`, `code-quality`, `code-review`,
`refactoring`) should be looked at separately — three of their four
citations point at `core/taxonomy/skill-catalog.md`, which is the same
wrong-target artifact as QR-N2 and is probably a mislink rather than a
deliberate self-citation.

#### TA-N3 · 42 skills have no external source URL at all; 16 of them declare `grounding: official-docs` — **Low**

**Finding.** 42 of 86 skills have `source_references` in which **every**
entry's `url` is a repo path rather than an external URL. Sixteen of those
declare `grounding: official-docs`: `agent-architecture`, `ai-security`,
`authentication-authorization`, `caching-strategy`, `database-operations`,
`llm-application-engineering`, `llm-evaluation`, `model-selection`,
`observability`, `performance-engineering`, `prompt-context-engineering`,
`rag-engineering`, `security-engineering`, `seo-optimization`,
`structured-output-tool-calling`, `styling-systems`.

This is defensible in substance — each points at a `research/` file that
does itself cite official documentation, so the chain reaches official docs
in two hops rather than one. It is recorded as Low because SG-1's literal
wording ("every entry MUST resolve *through* a research file *to* an
official documentation URL") is arguably satisfied by the two-hop reading,
and nothing here is unsourced. It matters only for a future mechanical
SG-1 validator, which will need to be told explicitly that a repo-path
`url` with a research `via` is conformant, or it will report 108
false positives on day one.

**Recommended correction.** Add one clarifying sentence to SG-1 stating that
a `source_references` entry may name a `research/` file directly as its
`url`, in which case conformance is checked against that file's own
citations. Documentation of existing intent, not a content change.

---

## 4. Version awareness (VA-1, VA-2, VA-4, VA-5)

### Prior findings re-verified

| Prior finding | Source | Status now |
|---|---|---|
| **F1-DB (Critical)** — `postgresql`'s `covered_versions: ">=14 <=18"` has no consumer; `failure_handling` covers only *undeterminable* version, and all four `reverify_triggers` point forward | `databases-users-migration.md`:142-180, re-verified in `synthesis.md`:48-53 | **Confirmed still live, and the pattern is universal — see VA-N1.** |
| Proposed rule **VA-6** (coverage-deficient version handling) and failure class **F10** | `synthesis.md`:241 | **Not adopted.** `VA-6` and `F10` appear nowhere outside `audits/`. Expected — Step 33 is the correction step — but recorded so the gate is explicit. |
| **T-01** — three competing version-tag syntaxes, "7 skills mixing two inside one file" | `cross-skill-audit.md`, `terminology-audit.md` | **Confirmed still live; my count is 9.** `[Version-sensitive, …]` 59 occurrences, bold `**[…]**` 38, inline parenthetical 10. Skills mixing ≥2 syntaxes: `angular`, `clickhouse`, `playwright`, `postgresql`, `python`, `redis`, `socketio`, `typeorm`, `webrtc`. (The delta from 7 to 9 is regex-definition drift, not necessarily regression; the finding is unchanged.) |
| VA-1 — technology skills must declare `covered_versions` + `reverify_triggers` | spec `:191` | **Clean: 40/40.** Exactly the 40 `kind: technology` skills declare both; the 46 generic skills correctly declare neither. |
| VA-4 — `last_verified` present | spec `:194` | **Clean: 86/86.** But see VA-N3. |
| `github-actions`'s `covered_versions` type-shape fix (Step 28 Critical, fixed) | `individual-skill-review.md`:73-76 | **Confirmed resolved** — it is now a map. |

### New findings

#### VA-N1 · F1-DB is not a `postgresql` defect — 0 of 40 version-scoped skills handle a below-floor request — **Critical**

**Finding.** The step brief asked whether the F1-DB pattern repeats beyond
`postgresql`. It does not merely repeat: **`postgresql` is the entire
population, not an instance of it.**

Mechanical result across all 40 skills carrying `covered_versions`:

| Check | Result |
|---|---|
| Skills declaring `covered_versions` | **40 of 86** (exactly the `kind: technology` set) |
| …with any `failure_handling` item addressing a request **below/outside** the declared range | **0 of 40** |
| …with any `SKILL.md` body text addressing a below-floor request | **0 of 40** (3 bodies matched the keyword pattern — `angular`, `go`, `nextjs` — all discussing EOL status of *covered* versions, not out-of-range requests) |
| …with a `failure_handling` item addressing an **unknown/undeterminable** version | **37 of 40** |
| `reverify_triggers` items across the 40 | **153 total; 0 of 153 fire on a request below the floor** |

The 10 `reverify_triggers` items that mention older versions at all
(`express`, `grafana`, `mongoose`, `mysql`, `nodejs`, `openapi-swagger`,
`sass`, `vue`) all watch for *EOL-status changes to versions already inside
coverage* — the field is a staleness watch by design, and correctly so. The
defect is not that `reverify_triggers` fails to do this; it is that **no
other field does either.**

So the library declares its knowledge boundary 40 times, with real precision
(`">=14 <=18"`, `">=26.2 <=26.8"`, `">=3.12 <=3.14"`), and has no mechanism
anywhere that reads the boundary when a request lands outside it. The
37-of-40 unknown-version handling shows the authors were thinking carefully
about version uncertainty — they covered the case where the version *cannot
be established* and uniformly missed the case where it is established and
out of range, which is the more dangerous of the two because it produces a
confident answer rather than a question.

**Root cause.** Exactly as `databases-users-migration.md`:165-169 diagnosed,
now shown to be structural: `covered_versions` was specified as a
**disclosure** field. Every rule that touches it (VA-1, VA-2, VA-4, SG-5) is
about keeping the skill's own claims honest; none matches the skill against
a request. Because the field's *purpose* was disclosure, forty authors
independently wrote forty conformant skills and not one of them wrote a
guard — this was never an authoring lapse, it is the specification behaving
as written.

**Recommended correction.** Adopt Step 32's proposed **VA-6** and **F10**,
and treat the `failure_handling` mirroring as a mechanical derivation across
all 40 rather than a per-skill authoring task — the text is derivable from
`covered_versions` itself:

> If the version in use is determinable and falls outside
> `covered_versions`, state that this skill's guidance is out of range
> before answering, and either restrict the answer to claims taggable as
> applicable to the version in use, or decline and escalate as a research
> gap.

Two points the prior write-up did not make that bear on how this is
implemented. First, the library already contains a correctly-worded
instance — `legacy-modernization/skill.yaml:80` — so VA-6's wording can be
lifted from existing house style rather than invented. Second, adding VA-6
without also making it `[V]`-checkable leaves it in the same position
`covered_versions` is in now: well-formed, uniformly declared, and read by
nothing. The rule should ship with the validator check, not before it.

#### VA-N2 · `last_verified` records the research date, not a verification date, so VA-4's staleness clock cannot distinguish the two — **Medium**

**Finding.** All 86 `last_verified` values are `2026-09-09` (16) or
`2026-09-10` (70) — identical to the dates
`research/technologies/README.md` declares for the research snapshot and its
two follow-up passes. No skill's `last_verified` is independent of when its
research was gathered.

This makes the field unable to express the thing VA-4 needs: *the skill's
claims were checked against the source on date D*. TA-N1 is the
demonstration. `nodejs` carries `last_verified: "2026-09-10"` while
asserting two version numbers that are not in its research file — the field
truthfully records that the research is one day old and says nothing about
whether the skill matches it, which is the only question a staleness check
cares about.

**Root cause.** The field was populated during authoring by copying the
research snapshot date, and the spec's definition (`:194`, "`last_verified`
present") does not say what event the date records.

**Recommended correction.** Define the field in `specification.md` §2 as
recording the date the *skill's claims* were last checked against the cited
sources, distinct from the research snapshot date (which
`research/technologies/README.md` already tracks independently). Then, when
the TA-N1 re-verification runs, `nodejs` gets a new date and the field
starts carrying information. Changing 86 dates today would be
counterproductive; changing the definition and letting dates diverge
naturally is the correct move.

#### VA-N3 · `shadcn-ui` declares a version range with no unknown-version handling — **Low**

**Finding.** 37 of the 40 version-scoped skills handle an undeterminable
version in `failure_handling`. Of the three that do not, `github-actions`
and `web-standards` are legitimate exemptions — both cover continuously
released products with no discrete version (their `covered_versions` say so
explicitly). `shadcn-ui` is not: it declares `shadcn_cli: ">=4.0 <=4.21"`, a
real bounded range, and its `failure_handling` addresses unknown
`components.json` state (correctly citing VA-3) but never an unknown CLI
version.

**Root cause.** The skill's authoring attention went to the immutable
post-init style/primitive hazard, which is genuinely the sharper trap; the
version question was crowded out.

**Recommended correction.** Add one `failure_handling` item in the house
pattern the other 37 use. It should be folded into the VA-N1 sweep rather
than done standalone.

---

## 5. Documentation (all READMEs)

Every README in the repository was read in full: `README.md`,
`skills/README.md`, `core/README.md` plus the four `core/*/README.md`,
`adapters/README.md` plus all six per-target READMEs, `evaluations/README.md`,
`research/README.md`, `research/technologies/README.md`, `audits/README.md`,
`examples/README.md`, `final/README.md` — 21 files.

### Prior findings re-verified

| Prior finding | Source | Status now |
|---|---|---|
| **X-16** — stale skill counts in four design documents (69 / 83) | `cross-skill-audit.md` | **Confirmed still live. 7 sites in 4 files:** `core/orchestrator/self-review.md:43,171,226` ("83 skills"), `core/orchestrator/state-and-contract.md:135` ("83 skills"), `core/dependency-architecture/dependency-graph.md:3` ("69 skills"), `core/taxonomy/taxonomy-analysis.md:12,197` ("69 skills"). Actual: 86. |
| Adapter per-target READMEs must document exactly 6 aspects including version considerations | `adapters/README.md`, `2026-09-10-adapter-compatibility-layer.md` | **Confirmed accurate.** All six targets carry numbered sections 1–6 ending in "Version considerations". The additional non-numbered headings in `claude-code`, `mcp` and `windsurf` are inside fenced example blocks — verified programmatically, not a structural defect. |
| `evaluations/` suite: 16 scenarios, 16 paired expected-behaviors, no harness | `evaluation-spec.md`:172-186, `evaluations/README.md` | **Confirmed accurate on disk** (16 + 16), and honestly scoped. |

**The one count check the brief asked for specifically:** `skills/README.md`
says neither "86 skills" nor a stale number — it carries a 86-row table
instead. The table was diffed against disk: **86 rows, 86 skill directories,
exact set match in both directions, no drift.** The skill inventory is
accurate. The problem is everything around it (DOC-N2).

### New findings

#### DOC-N1 · Six top-level READMEs still describe an empty scaffold; the repository's front door states the product does not exist — **Blocker**

**Finding.** Six of the repository's structural READMEs were written at
scaffold time and never updated. They are not merely stale — each asserts
the absence of content that is now the bulk of the repository:

| File | Text on disk | Reality |
|---|---|---|
| `README.md:15-17` | *"**Status.** Scaffold only. No skills have been written yet."* | 86 authored skills |
| `README.md:68-70` | *"**Contributing skills.** Not yet — the schema in `core/` needs to exist first."* | `core/skill-specification/specification.md`, 222 lines, complete |
| `core/README.md` (last line) | *"Empty for now — no schema or validation logic has been defined yet."* | 5 subdirectories, ~20 design documents |
| `research/README.md` (last line) | *"Empty for now."* | 68 files cited 854 times from `skills/`; 52 technologies |
| `audits/README.md` (last line) | *"Empty for now — no skills exist yet to audit."* | 30+ audit documents across 4 subdirectories |
| `examples/README.md` (last line) | *"Empty for now — no skills or adapters exist yet to demonstrate."* | `examples/` is indeed empty, but 86 skills and 6 adapters exist |
| `final/README.md` (last line) | *"Empty for now — no skills exist yet to promote."* | `final/` is indeed empty, but the stated reason is false |

`research/README.md` directly contradicts its own child:
`research/technologies/README.md` opens by documenting 52 researched
technologies with a dated snapshot caveat, while its parent says the
directory is empty.

**Why Blocker rather than High.** The root `README.md` states at line 5
*"This repository **is** the product"* and at line 11 *"What ships is the
content of this repository."* Under the repository's own definition of what
it ships, a Status section reading "No skills have been written yet" is not
a documentation lag — it is a false statement about the deliverable, in the
first screen of the first file any consumer, contributor, or evaluator
opens. No release can go out over it. It is also, uniquely among the
findings in this report, a defect that costs nothing to fix and requires no
judgment call.

**Root cause.** These seven files were authored in the scaffold step to
describe *intent*, in the future/absent tense. Every subsequent step
(authoring, taxonomy, orchestration, evaluation, adapters, five audit
rounds) added content beneath them, and none had "update the directory
README" in its brief. The per-directory READMEs that *were* authored
alongside real content — `adapters/README.md`, `evaluations/README.md`,
`research/technologies/README.md` — are accurate, current and well written,
which confirms the gap is the scaffold-era cohort specifically, not a
general documentation-discipline problem.

**Recommended correction.** Rewrite the seven statements above. Concretely:
root `README.md` Status becomes a real status (86 skills, 6 adapters, an
evaluation suite of 16 scenarios, no executable validator or harness, no
promotions to `final/`) and Contributing points at
`core/skill-specification/specification.md`; `core/`, `research/` and
`audits/` READMEs get a two-line inventory replacing "Empty for now";
`examples/` and `final/` keep "empty" but correct the *reason* (nothing has
been promoted / no worked examples written yet — not "no skills exist"),
because in `final/`'s case the reason is the release gate itself. Add a
short "Status" line to each so the next drift is visible.

#### DOC-N2 · `skills/README.md` states that no evaluator and no adapter implementation exist — **High**

**Finding.** `skills/README.md:108-112` closes with:

> None of the above have a validator, evaluator, or adapter implementation
> yet — those are separate, not-yet-built pieces of tooling (`core/`
> currently holds only the design documents, no executable validator).

Of the three claims, one is true and two are false. **Validator:** true, no
executable validator exists. **Evaluator:** false —
`evaluations/scenarios/` (16 files) and `evaluations/expected-behaviors/`
(16 files) plus `scoring.md` and `regression-suite.md` were built at Step 30.
**Adapter:** false — `adapters/` holds six target implementations, a shared
`lib/` (8 files, including the single-parse-point `skill_loader.py`), and
`tests/test_compatibility.py`.

Compounding it, the Status column reads *"authored, not yet
validated/evaluated"* for **all 86 rows**, unchanged after per-skill review
(Step 28), cross-skill audit (Step 29), evaluation-suite construction
(Step 30), adapter compatibility testing (Step 31), and real-world
evaluation (Step 32). The `evaluations/README.md` honestly records that 77
of 86 skills appear somewhere in the 16 scenarios — a fact this table
flatly contradicts for those 77.

**Root cause.** The same scaffold-tense problem as DOC-N1, plus a Status
column whose vocabulary has no value for "reviewed and audited but not
promoted" — the only states it can express are "authored" and the implied
"promoted", so nothing that happened in Steps 28–32 was expressible in it.

**Recommended correction.** Rewrite the closing paragraph to name what
exists (evaluation suite: yes, non-executable; adapters: yes, 6 targets;
validator: no). Replace the Status column's single value with the actual
lifecycle position — the spec's own conformance ladder
(`specification.md:216-221`) already defines the stages (authored →
validator-passed → evaluated → audited → promoted), so the column should use
those terms and can be filled truthfully today for all 86.

#### DOC-N3 · `evaluation-spec.md` grounds two of its fifteen dimensions in rules that were recommended but never adopted, or that are not universally true — **Medium**

**Finding.** The brief asked whether the behavioral vocabulary is still
accurate. Two of the fifteen dimension groundings do not hold:

- **Dimension 5 (Correct context usage)** is grounded in
  *"`audits/cross-skill/context-audit.md`'s CS-9 (an affinity hint is not a
  load list)"* (`evaluation-spec.md:41`), and CS-9 is invoked again at
  `:77`. **CS-9 does not exist as a rule.** It is a *recommendation* in a
  Step 29 audit; `core/routing-architecture/rules.md` defines CS-1 through
  CS-8 and stops. The spec cites an audit's proposal as if it were part of
  the contract layer, which is also a citation across the dependency
  direction the root README declares (`audits/` gates `skills/`; it does not
  supply `core/`'s rules).
- **Dimension 13 (Maintainability)** is grounded in *"the
  anti-over-engineering trap every skill's Anti-patterns section is required
  to name (QR-4)"* (`:49`). QR-4 does require it; nine skills do not have
  it (QR-N1), so the dimension has no anchor when scored against those nine.

**Root cause.** Step 30 was authored two steps after Step 29 and reasonably
read a well-argued audit recommendation as settled. Nothing in the process
distinguishes "recommended in an audit" from "adopted into `core/`", and no
step between them adopted CS-9.

**Recommended correction.** Adopt CS-9 into
`core/routing-architecture/rules.md` — Step 29 called it "the highest
value-per-word change in this entire audit" and it is one sentence — then
re-point `evaluation-spec.md:41` at `rules.md` rather than at the audit. If
CS-9 is instead rejected, dimension 5's grounding must be rewritten. For
dimension 13, fixing QR-N1's nine skills restores the grounding without
touching the spec.

#### DOC-N4 · The release gate's definition is a dangling pointer to a conversation — **Medium**

**Finding.** `README.md:72-77` heads a section "Open architectural
decisions" whose entire content is:

> See the end of the initial-scaffold conversation/PR for the full list of
> decisions that should be reviewed before skill authoring begins (license
> choice, `skills/` vs `final/` promotion mechanism, per-skill versioning
> strategy, adapter granularity, and skill schema ownership).

`final/README.md` then defers to it: *"the exact promotion criteria and
mechanism … have not been decided yet — see the architectural-decisions note
in the root README.md."* And `README.md:81-83` defers the license question
to it as well, despite `LICENSE` being present on disk (MIT, © 2026 Keval
Gor).

So the mechanism that decides what reaches `final/` — the repository's
release gate, and the thing this entire audit is a gate for — is defined
nowhere in the repository. It points at an unreferenceable artifact, and the
one file whose job is to explain promotion points back at the pointer.

**Root cause.** A scaffold-time placeholder that was load-bearing and never
replaced; three of its five listed decisions (license, schema ownership,
adapter granularity) have in fact been made since, in `LICENSE`,
`core/skill-specification/`, and `adapters/README.md` respectively, without
the placeholder being retired.

**Recommended correction.** Replace the section with the decisions as
actually resolved, and move the two that remain open (promotion mechanism,
per-skill versioning — note `skill_version` is uniformly `0.1.0` across all
86 while `VERSION` is also `0.1.0`, so the relationship is undefined in
practice as well as on paper) into a tracked location that is part of the
repository. `final/README.md` should then state the criteria rather than
forward to them.

#### DOC-N5 · Build-process narration leaks into shipped documentation and adapter source — **Low**

**Finding.** The explicit verification item — no unnecessary Phase/Step
build-process references in skill or doc content — passes cleanly where it
matters most and fails at the edges.

**`skills/` is completely clean: 0 occurrences** of "master build plan",
"Step NN", or build-phase narration across all 172 skill files. That is the
important result.

Outside `skills/`, 9 occurrences remain in non-audit content:
`adapters/README.md` (×4: "This is Step 31 of this project's master build
plan" and three further references), `evaluations/README.md` (×1, "Step 30"),
`evaluations/evaluation-spec.md` (×1, "This is Step 30 of the project's
master build plan"), `evaluations/regression-suite.md` (×1),
`adapters/lib/skill_loader.py` (×1), `adapters/tests/test_compatibility.py`
(×2). A consumer of the library has no access to the build plan, so these
reference an artifact they cannot read.

**Explicitly not a defect:** the "Phase 0" through "Phase 6" references in
`core/routing-architecture/routing-algorithm.md`, `rules.md`,
`core/orchestrator/lifecycle.md`, and two evaluation scenario files are the
**routing algorithm's own phases** — legitimate domain content that happens
to share vocabulary with build-process narration. They should not be swept.

**Root cause.** Documents authored as step deliverables described themselves
as such.

**Recommended correction.** Replace "This is Step 31 of this project's
master build plan" with what the reader needs ("the per-target adapter
layer"). Nine edits, no content change. Also worth noting as a **positive**:
the AI-branding sweep returned **0 hits** across all skill files and all
READMEs — no "generated by", no co-author trailers, no tool attribution, no
AI-assistant branding anywhere in shipped content. The `code-commenting`
skill names AI attribution in code comments as an anti-pattern and the
library obeys its own rule.

---

## Release-readiness contribution

Across these five categories the library's *substance* is in strong shape
and its *self-description* is not. The mechanical results are genuinely
good, and several are better than the prior audits claimed: CE-1 and CE-2
are clean at 0 violations in 86 with real headroom, CE-3 is clean to the
point of being exemplary (one table, zero large code blocks in 24,000 lines
of body text), the body structure is uniform across all 86, and the
provenance chain — the thing most likely to be quietly rotten in a
citation-dense library — is intact at **746 of 746 external URLs resolving
verbatim into the research file each one names**. No attribution has been
stripped, no source fabricated, and SG-3 hedging is present in 40 of 40
technology skills. The explicit verification items on AI branding and on
build-process narration inside skills both pass at zero.

What should gate the release is narrower and sharper than that picture
suggests. **One Blocker:** six scaffold-era READMEs, including the root, tell
every reader that the product does not exist — under the repository's own
"this repository *is* the product" framing that is a false statement about
the deliverable in the first file anyone opens, and it costs nothing to fix.
**Two Criticals,** both of which are cases where the library's own
verification machinery returns green on a defect it was built to catch:
`nodejs` asserts a stability milestone absent from its cited source while
passing VA-2, VA-4 and SG-1, and — the finding I would put first — all
**40 of 40** version-scoped skills declare a knowledge boundary that
**nothing in the library reads when a request falls below it**. F1-DB was
recorded as a `postgresql` defect; it is the specification behaving exactly
as written, forty times over. Neither Critical is an authoring lapse, which
is why five prior rounds did not catch them: both are rules that are
well-formed, uniformly applied, and inert.

The three High findings share one root cause worth naming for Step 33's
sequencing. Sixteen skills still describe authored siblings as unwritten,
and in six of them that false premise is the *stated rationale* for the
skill's own size and self-containment — which makes the stale-marker sweep
(catalogued since Step 29 as hygiene) the upstream fix for the duplication
findings tracked separately since Step 28, and therefore worth doing before
them rather than after. QR-N1's nine missing over-engineering traps cluster
entirely in security and infrastructure domains, where the counterweight is
worth the most. And `skills/README.md` denies the existence of the adapter
and evaluation layers that Steps 30 and 31 built.

My recommendation for Step 33's ordering within these categories: the
Blocker first (an afternoon, zero judgment required), then VA-6 mirrored
mechanically across the 40 — shipped *with* its validator check, not before
it, or it joins `covered_versions` as a second well-formed field with no
consumer. Then `nodejs`, where declining to confirm and marking the claim
`Unresolved:` per the research corpus's own convention is an acceptable
outcome and available today. Then the two mechanical sweeps (16 stale
markers, 68 mislinks) that together are the largest defect count in this
report at the lowest risk per edit. None of the Medium or Low findings
should hold a release.

**Contribution to the release decision: not ready, but close, and the gap is
almost entirely repairable by mechanical means.** Nothing found here
suggests the skill content itself is wrong — the technical substance held
under every check I could mechanize, including the ones designed to find
fabrication. The risk that remains is concentrated in fields that describe
the library rather than in the guidance the library gives, which is the
better of the two places for a final gate to find its remaining work.

---

### Findings index

| ID | Finding | Severity |
|---|---|---|
| DOC-N1 | Six scaffold-era READMEs describe an empty repository; root README says no skills exist | **Blocker** |
| TA-N1 | `nodejs` asserts "Stable >=25.2.0/24.12.0", absent from its cited research; passes every mechanical rule | **Critical** |
| VA-N1 | 0 of 40 version-scoped skills handle a request below `covered_versions`; F1-DB is the whole population | **Critical** |
| CE-N1 | 16 skills call authored siblings unauthored; 6 cite that as their self-containment rationale | **High** |
| QR-N1 | 9 skills' Anti-patterns name no over-engineering trap (QR-4), clustered in security/infra | **High** |
| DOC-N2 | `skills/README.md` denies the existence of the evaluation suite and the adapter layer | **High** |
| QR-N2 | 68 links across 28 skills point at the taxonomy catalog instead of the sibling skill | **Medium** |
| TA-N2 | 16 `source_references` route provenance through `core/`, closing the chain inside the project | **Medium** |
| VA-N2 | `last_verified` records the research date, not a verification date | **Medium** |
| DOC-N3 | `evaluation-spec.md` grounds dimensions 5 and 13 in an unadopted rule and a false universal | **Medium** |
| DOC-N4 | The `final/` promotion gate is defined only by a pointer to an unreachable conversation | **Medium** |
| CE-N2 | Two empty `references/` directories ship in the library | **Low** |
| QR-N3 | `typescript` uses `## Knowledge (essential)`, breaking VR-8 uniformity across 86 | **Low** |
| TA-N3 | 42 skills have no external source URL; 16 declare `grounding: official-docs` | **Low** |
| VA-N3 | `shadcn-ui` declares a version range with no unknown-version `failure_handling` | **Low** |
| DOC-N5 | Build-process narration in 9 sites outside `skills/` (`skills/` itself is clean) | **Low** |

**Confirmed still live from prior audits** (re-verified, not re-counted as
new): C-01 (CS-9 unadopted), C-02 (Tier-0 ceiling undocumented), F4-FE
(stale marker in `frontend-architecture`), X-02 (stale markers, 16 skills),
X-06 and Step 28 #1/#2 (three prose duplications), Step 28 #4 (catalog
mislinks), X-16 (stale skill counts, 7 sites), T-01 (three version-tag
syntaxes, 9 skills mixing), F1-DB, Step 28's `nodejs` Critical, and the
9-site VR-3 gap (`SK-FE-005` ×7, `SK-GROW-002`, `SK-TECH-graphql`).

**Resolved since being reported:** `github-actions`'s `covered_versions`
type shape; `drizzle`'s missing `## Workflow` section; the two missing
`source_references` in `search-integration` and `testing-strategy`; the six
technology skills swept for stale markers at Step 28 (`nodejs`, `python`,
`postgresql`, `mysql`, `mongodb`, `clickhouse` — none reappears in CE-N1's
list of 16).

**Prior findings that were incorrect as stated:** `evaluation-spec.md:49`'s
premise that every skill names an anti-over-engineering trap (false for 9);
Step 28 #4's estimate of "roughly 20+ skills" (actual 28 skills / 68 links);
`context-audit.md`'s count of 28 Tier-2 files "across 26 skills" (28 files
across 28 skills, in 30 directories — two are empty).
