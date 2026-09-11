# Final Principal-Engineer Audit (Step 33) — Adapters, Evaluation Suite, Real-World Evaluation, Maintainability, Extensibility

Date: 2026-09-11. Model/effort: Opus 5 / Max. Scope: categories 16, 17, 18, 24, 25
of the 26-category Step 33 audit. Read-only; no file outside this one was modified
and no git command was run.

Three of these five categories are **audits of this project's own prior audits**
(Steps 30, 31, 32). The posture below is deliberately adversarial toward that prior
work. Where prior work holds up under independent execution, that is stated as
plainly as where it does not.

**Method.** Every claim below is backed by a command actually run against the
current tree or a `file:line` citation actually opened. Where I reproduce a prior
audit's own stated command, I report what it returns *today*, not what that audit
reported at the time.

---

## Findings summary

| Severity | Count |
|---|---|
| Blocker | 0 |
| Critical | 2 |
| High | 7 |
| Medium | 11 |
| Low | 4 |
| **Total** | **24** |

The two Critical findings are a single causal pair: the library's authoring
contract mandates a mechanical validator that does not exist, and the specific
validation rule that validator would enforce (VR-3) is violated in nine places in
shipped skill metadata — a defect first reported in Step 28 and still live.

---

## 16. Agent adapters — meta-audit of Step 31

### Verification actually performed

The committed suite passes against the current tree:

```
$ python3 adapters/tests/test_compatibility.py
Ran 36 adapter x skill combinations across 6 targets and 6 sample skills.
All compatibility checks passed.
EXIT=0
```

I then re-ran the suite's own L-1/L-2 logic across the **entire** library rather
than its 6-skill sample:

```
skills loaded: 86
combos: 516 failures: 0
```

**All 86 skills × 6 targets project cleanly, with zero L-1 gaps and zero L-2
violations.** Step 31's central claim survives independent re-execution. That is a
genuinely strong result and should be recorded as such.

I also diffed the current `skill.yaml` schema against the adapter engine's four
field lists — the specific gap the brief asked me to look for (new fields
introduced by Step 26's 8 AI/LLM skills or Step 27's 3 orchestrator skills):

```
union of GOVERNANCE_ONLY + RUNTIME_MEANINGFUL + IDENTITY_ONLY + BODY_DERIVED = 36
fields in skills but NOT in any list: ['activation_mode', 'description', 'name']
fields in lists but NOT in any skill: []
```

The three unlisted fields are the three every adapter maps natively. **No new
canonical field has been introduced that the engine does not account for.** The
suspected drift does not exist. (One false lead worth recording so it is not
re-investigated: `grep` finds `capability_fallbacks` in 14 skill files but only 2
declare it as a top-level key — the other 12 are explanatory YAML comments stating
why no fallback block is needed. The adapter's top-level-only read is correct.)

### A16-1 · The loss manifest ships a factually false statement into all 516 projections — **High**

**Finding.** `governance_fields_note()` (`adapters/lib/common.py:71-74`) appends to
every projected body:

> Full `failure_handling` is defined in this skill's canonical `skill.yaml`, not reproduced here.

Verified emitted output for `cursor`/`react`:

```
failure_handling   drop+note  Library-governance field; canonical source is skill.yaml.
escalation         drop+note  Library-governance field; canonical source is skill.yaml.
verification       drop+note  Library-governance field; canonical source is skill.yaml.
covered_versions   drop+note  Library-governance field; canonical source is skill.yaml.
```

The statement is false for at least five fields. Every one of the 86 skills has a
`## Failure handling`, `## Escalation`, and `## Outputs & verification` section in
its `SKILL.md` body (86/86 confirmed by heading scan), and that body is copied
verbatim into the projection. Version caveats likewise appear inline in the body
with `applies_to:` markers (`skills/react/SKILL.md:112,127,291,301-303`). So the
projected artifact contains a `## Failure handling` section and, a few lines later,
a note asserting that the failure-handling content is not reproduced there.

**Root cause.** `BODY_DERIVED_FIELDS` (`adapters/lib/skill_loader.py:85`) contains
only `purpose`/`scope`/`expertise`. The five body-mirrored fields above were
classified into `GOVERNANCE_ONLY_FIELDS` instead, which routes them through the
blanket drop+note sweep. The classification captures where the *authoritative*
copy lives but not that a working copy already survives projection.

**Why it matters beyond tidiness.** The loss manifest is the entire honesty
mechanism of the adapter layer — its stated purpose is to make lossiness explicit
rather than silent. Here it does the inverse: it fabricates a loss that did not
occur, inside the artifact the consuming agent reads. An agent that trusts the note
has been told to disregard, or go hunting behind, content that is directly in front
of it.

**Recommended correction.** Move `failure_handling`, `escalation`, `verification`,
`covered_versions`, and `version_sensitive_claims` into a body-mirrored class
(either extend `BODY_DERIVED_FIELDS` or add a third action), and change their note
to state what is actually true: the working form is in the body; the structured
form is in `skill.yaml`.

### A16-2 · The mechanical L-2 check is structurally weaker than the written L-2 contract — **High**

**Finding.** L-2 (`core/skill-specification/adapter-projection.md:146-148`) reads:

> An adapter MUST NOT silently drop a field that carries runtime meaning (a version
> caveat, a failure-handling rule, a security constraint).

`RUNTIME_MEANINGFUL_FIELDS` (`adapters/lib/skill_loader.py:56-64`) is
`activation_conditions`, `non_activation_conditions`, `required_capabilities`,
`execution_tier`, `capability_fallbacks`, `inputs`, `outputs`. It does **not**
include `failure_handling`, `escalation`, `verification`, `covered_versions`, or
`version_sensitive_claims` — i.e. it omits the two categories L-2's own sentence
names as examples ("a version caveat, a failure-handling rule").

`dropped_fields_with_runtime_meaning()` (`adapters/lib/loss_manifest.py:65-72`)
only flags entries whose `field_name` is in that tuple. **The L-2 test therefore
cannot fire for the exact examples L-2 exists to protect.**

There is no live violation today: all 86 skills mirror these fields in the body, so
the substance survives. But the guard is absent. A future skill that omits its
`## Failure handling` section — a `§3.2` body-structure violation with no validator
to catch it (see M24-2) — would have its failure-handling rule genuinely dropped by
all six adapters, and `test_compatibility.py` would report "All compatibility checks
passed."

**Root cause.** The engine's field taxonomy was built around "where does the
authoritative copy live," and the L-2 check was then defined over that taxonomy
rather than over L-2's own wording.

**Recommended correction.** Fixing A16-1 largely fixes this: once the five fields
are classified as body-mirrored, add a companion assertion that their body section
is actually present, so the claim "it survives in the body" is enforced rather than
assumed.

### A16-3 · Step 31's audit claims a library-wide standing guard; the committed test covers 6 of 86 skills — **High**

**Finding.** `audits/2026-09-10-adapter-compatibility-layer.md:60-61` and `:84-87`
describe the L-1 completeness check as running at "86 skills × 6 targets = 516
combinations," and `:120-125` concludes:

> any future canonical field added to `skill.yaml` that isn't wired into
> `lib/skill_loader.py`'s field lists or an adapter's own logic will be caught the
> next time `test_compatibility.py` runs

The committed test does not do this. `SAMPLE_SLUGS` (`adapters/tests/test_compatibility.py:44-51`)
is six skills, and Check 8 (`:189-197`) iterates `skill.yaml_data.items()` for
those six only. The suite's own output confirms it: "Ran 36 adapter x skill
combinations across 6 targets and 6 sample skills."

The 516-combination run was a manual verification performed *during* Step 31. It
was real — I reproduced it and it still passes — but it is not what the repository
runs. A new 87th skill introducing a new canonical field would not be sampled, and
the audit's stated guarantee would not hold.

**Root cause.** A one-off verification and a standing regression guard were
conflated in the audit's own prose.

**Recommended correction.** Change `SAMPLE_SLUGS` to a full `load_all(SKILLS_ROOT)`
sweep for Checks 1-3 and 8 (it completes in well under a second for 516
combinations), retaining the curated sample only where per-target structural checks
genuinely need a hand-picked skill. This makes the audit's claim true of the
artifact.

### A16-4 · Vendor length-limit enforcement is entirely vestigial, and the test docstring claims otherwise — **Medium**

**Finding.** Three linked pieces of dead machinery:

1. `FRONTMATTER_LIMITS` (`adapters/tests/test_compatibility.py:56-63`) is a dict of
   six empty dicts. `grep -rn "FRONTMATTER_LIMITS" .` returns exactly one match —
   its own definition. Nothing reads it.
2. `truncate(text, max_length)` (`adapters/lib/common.py:10-14`) is called at eight
   sites across five adapters, and **every call passes `None`** — an unconditional
   no-op.
3. `adapters/claude-code/adapter.py:34,37` assign `name_truncated` and
   `desc_truncated` and never use them. The loss manifest has no action for
   truncation at all (`grep -rn "truncat" adapters/lib/loss_manifest.py` → 0 matches).

Meanwhile the suite's docstring (`adapters/tests/test_compatibility.py:17-19`)
states it confirms "each target's own documented structural rules (name/description
length limits, path convention, third-person description for Antigravity, etc.)
actually hold." Path convention and the Antigravity rule are genuinely checked
(Checks 5 and 7). Length limits are not checked anywhere.

No live breakage: longest `description` in the library is 499 chars
(`web-standards`, `tailwindcss`), 0 skills exceed 500, and CE-1 caps it at 500.
But the CE-1 cap is a library rule, not a vendor rule, and nothing ties them.

**This is precisely the "metadata says X but nothing consumes X" pattern Step 32
named — found inside the auditor.** That is worth stating explicitly, because it
is independent corroboration that Step 32's pattern is real rather than post-hoc
(see finding R18 assessment).

**Root cause.** Limit-handling was scaffolded for the targets that document limits;
none of the six built targets does, so the scaffolding was never wired up, and the
docstring was written from the plan rather than the code.

**Recommended correction.** Either delete `FRONTMATTER_LIMITS` and the unused
truncation flags and correct the docstring, or populate the limits and enforce them
(the latter becomes mandatory if a VS Code adapter is ever built — see X25-2).

### A16-5 · `LossEntry.action` type comment omits a value the class itself emits — **Low**

`adapters/lib/loss_manifest.py:18` documents `action: str  # "native" | "body" | "drop+note"`,
but `not_applicable()` (`:39-47`) appends `"n/a"`. Four actions exist; three are
documented. One-line fix.

### A16-6 · Build-step references in adapter code — confirmed real, and unresolvable — **Low**

All three sites the orchestrating session's grep flagged are real:

```
adapters/lib/skill_loader.py:8:the master build plan's Step 31 instructions: the knowledge of what a
adapters/tests/test_compatibility.py:5:tests where practical" deliverable from the master build plan's Step 31.
adapters/tests/test_compatibility.py:50:    "git-conventions",  # Layer 2, Tier A, no shell (fixed in Step 27's VR-5 pass)
```

**Assessment, as requested — is there a legitimate reason a maintainer would need
"Step 27" a year from now?** No, because *the master build plan is not in this
repository.* `find . -iname "*build-plan*" -o -iname "*master-plan*"` returns
nothing; the phrase appears only inside `audits/` files that cite it. Every "Step N"
reference in shipped code is therefore unresolvable by any reader who does not have
the originating conversation — the definition of tribal knowledge.

The *content* around each reference is load-bearing and should stay. At
`skill_loader.py:8` the durable fact is the do-not-duplicate-skill-knowledge rule.
At `test_compatibility.py:50` the durable fact is the genuinely useful one — this
skill is in the sample as a regression guard for a Tier-A-with-no-shell case — and
it has a citable in-repo anchor: **VR-5** (`core/skill-specification/specification.md:176`).

**Recommended correction.** Keep the reasoning, drop the step numbers; at `:50`
cite VR-5 instead of "Step 27's VR-5 pass."

**Verified clean in this category:** no AI branding anywhere in
`skills/`, `core/`, `adapters/`, `evaluations/` (grep for generated-by/authored-by/
as-an-AI-model patterns → 0 matches). Attribution/provenance intact: 83/86 skills
carry `source_references`; the 3 that do not (`project-management`,
`requirements-engineering`, `technical-planning`) are all `grounding:
engineering-convention`, exempt under SG-4.

---

## 17. Evaluation suite — Step 30

### What holds up

`scoring.md:4-6` makes a precise, checkable claim: "117 assertions total: 36
critical, 54 major, 27 minor." Counted mechanically across all 16
`expected-behaviors/` files:

```
WEIGHT TAG COUNTS: {'critical': 36, 'major': 54, 'minor': 27} TOTAL= 117
```

**Exact match.** All 16 `scenarios/` files have a matching `expected-behaviors/`
file (0 unpaired either way). Every assertion row carries a `Dimension` column, so
`scoring.md:120-122`'s per-dimension aggregation is executable rather than
aspirational. `scoring.md` itself is the strongest single document in this part of
the repo — its refusal to emit a headline percentage (`:129-147`) and its explicit
anti-gaming rule on `not-applicable` (`:55-61`) are well-judged.

### E17-1 · S05's expected sequencing graph requires a skill that does not exist — **High**

**Finding.** `evaluations/expected-behaviors/S05-realtime-multiplayer-browser-game.md:144`
specifies the expected execution graph:

```
SK-FE-001 → SK-TECH-threejs → SK-FE-005
```

and `:74-76` lists `SK-FE-005` (rendering-strategy) under "Conditional /
deferred-but-expected." `SK-FE-005` is not in `skills/` — the FE domain runs
`SK-FE-001` through `SK-FE-004` only (verified against all 86 IDs).

A scenario whose answer key positions a nonexistent skill in the expected graph
cannot be scored as written: no run can activate it, so the assertion is
permanently unsatisfiable in one direction and vacuous in the other.

**Root cause.** Shared with M24-3 — the scenario author worked from
`core/taxonomy/skill-catalog.md`, which defines `SK-FE-005` as an approved entry
(`:341`). The catalog is a superset of what was built, and nothing marks which
entries are built.

**Recommended correction.** Bound to the M24-3 decision. Under Option A (author
`SK-FE-005`) S05 becomes correct as written. Under Option B, S05's graph and
`:74-76` must be amended in the same pass.

### E17-2 · Seven "must NOT activate" distractors name skills that do not exist, making those assertions vacuous — **Medium**

**Finding.** A full scan of skill-ID references in `evaluations/` against the 86
real IDs returns 8 unknown IDs:

```
SK-FE-005              S03, S05, S06, S09, S11
SK-GROW-002            S05, S06
SK-INFRA-email         S06
SK-TECH-google-adsense S05
SK-TECH-google-seo     S05
SK-TECH-graphql        S05, S06
SK-TECH-sendgrid       S06
SK-TECH-vite           S09
```

Excluding S05's activation-side use (E17-1), the remainder sit in **"Must NOT
activate"** lists — e.g.
`expected-behaviors/S09-dashboard-n-plus-one-bottleneck.md:44` excludes
`SK-FE-005` as "the same distractor class as `SK-TECH-vite`," and neither exists.

A distractor that does not exist cannot be falsely activated. These assertions read
as over-activation tests and are automatically satisfied by every possible run.
They inflate the suite's apparent rigor without adding discriminating power.

**Recommended correction.** Replace each phantom distractor with a real skill that
a keyword-driven router would plausibly mis-select on that task, or delete the row.
Do not simply leave them pending the M24-3 decision — `SK-TECH-google-seo`,
`SK-TECH-sendgrid`, `SK-INFRA-email`, and `SK-TECH-vite` are not even catalog
entries, so no future authoring pass will make them real.

### E17-3 · `evaluation-spec.md`'s scenario schema contradicts the files and itself — **Medium**

**Finding.** `evaluation-spec.md:81-124` presents a fenced "Scenario schema" that
every `scenarios/` file supposedly follows, including `## Expected activation set`,
`## Expected sequencing and parallelization`, and `## Expected behavioral
assertions`. Checked mechanically:

- 13 of 16 `scenarios/` files omit all three answer-key sections.
- S01, S11, S12 omit only `## Expected behavioral assertions` — i.e. they **do**
  carry `## Expected activation set` in the un-keyed file.

The very next paragraph (`:126-132`) states the opposite of the schema block: the
split exists "so a scenario can be handed to an agent under test **without** the
answer key attached in the same file."

So the spec documents a schema no file fully follows, contradicts itself two
paragraphs later, and three scenario files leak part of the answer key — which
defeats the stated purpose of the split for exactly those three.

**Root cause.** The schema block was written before the scenarios/expected-behaviors
split was introduced and was never reconciled.

**Recommended correction.** Split the schema block into two — the `scenarios/`
schema (metadata + Task + Repository signals) and the `expected-behaviors/` schema
(the three answer-key sections + weights + dimensions) — and strip the leaked
sections from S01, S11, S12.

### E17-4 · Dimension coverage is heavily skewed; per-dimension aggregation is meaningless for three dimensions — **Medium**

Assertions per dimension across all 16 scenarios:

```
Dim  1: 24 (13 scenarios)      Dim  9: 27 (11)
Dim  2: 10 ( 8)                Dim 10:  8 ( 7)
Dim  3:  5 ( 4)                Dim 11: 22 (10)
Dim  4:  5 ( 4)                Dim 12:  3 ( 3)
Dim  5:  2 ( 2)                Dim 13:  6 ( 4)
Dim  6: 12 ( 8)                Dim 14:  1 ( 1)
Dim  7: 10 ( 5)                Dim 15:  1 ( 1)
Dim  8:  8 ( 5)
```

All 15 dimensions have non-zero coverage, so `evaluation-spec.md:32-51`'s claim is
literally true. But dimension 14 (performance reasoning) and 15 (documentation
quality) have **one assertion each, in one scenario each**, and dimension 5
(context usage) has two. `scoring.md:120-124` promises a "per-dimension breakdown"
that answers "is the library weak at security behavior specifically" — for
dimensions 5, 14, and 15 that breakdown is a single coin flip, not a signal.

Dimension 14 is the sharper problem: the suite has a dedicated **Performance-sensitive
category** with two scenarios (S03, S09), yet the performance-reasoning dimension
those scenarios exist to exercise carries one assertion library-wide.

**Recommended correction.** Set a floor (e.g. ≥3 assertions across ≥2 scenarios per
dimension) and add performance-reasoning assertions to S03/S09, which already have
the right setup. Step 32's proposed S33/S34 would address dimension 15.

### E17-5 · The S17-S38 reconciliation is sound in mechanism but has no anchor in `evaluations/` — **Medium**

**Assessment of the reconciliation itself (as requested).** The reconciliation at
`audits/real-world/synthesis.md:157-210` is methodologically sound. It correctly
diagnoses the cause (five parallel agents each allocating from S17), assigns one
canonical ID per *distinct* scenario rather than per proposing file, documents the
source file and original ID for every row so the mapping is auditable, merges two
pairs that were the same underlying gap seen from different tasks (S17, S19), and
correctly excludes one item that is a `reverify_triggers` condition rather than a
behavioral assertion (`:196-200`). It is also honest that it reconciles rather than
authors (`:202-210`). I found no ID collision or mis-merge in the table.

Three weaknesses:

1. **The reservation is recorded only in `audits/`.** Nothing under `evaluations/`
   records that S17-S38 are taken. A future author working from
   `evaluations/README.md` + the 16 existing files — the natural place to look —
   would allocate S17 again. That is the identical failure mode this reconciliation
   exists to repair, one directory over.
2. **S18 (rendering-mode-decision-no-owner) cannot be authored before M24-3 is
   decided.** Its subject is the absence of `SK-FE-005`; if Option A is taken and
   the skill is authored, the scenario's premise dissolves. The table does not note
   this dependency, and S18 is not among the three it recommends building first.
3. **The "Priority signal" column is empty for 17 of 22 rows.** A column that is
   populated five times is a note, not a field.

**Recommended correction.** Add an ID-reservation table to `evaluations/README.md`
(or a `scenario-ids.md`) that is the allocation authority; annotate S18's dependency
on the M24-3 decision.

---

## 18. Real-world evaluation — meta-audit of Step 32

### Reproduction of Step 32's own claims

**Finding totals.** `synthesis.md:21-31` publishes the exact command it used. Re-run
today:

```
$ grep -hoE '\*\*(Critical|High|Medium|Low)\*\*\s*$' audits/real-world/*.md | sort | uniq -c
      5 **Critical**
     39 **High**
      2 **Low**
     25 **Medium**
```

Exactly the published 5 / 39 / 25 / 2 = 71. The count is honest and reproducible,
and the decision to key off severity tags rather than agent self-report
(`:14-19`) is the right one.

**Citation spot-checks.** Five citations across three files, opened directly:

| Citation | Verdict |
|---|---|
| `skills/frontend-architecture/skill.yaml:25-26` — "Not for styling specifics, accessibility depth, or the SSR/SSG rendering-mode decision" | verbatim |
| `skills/nextjs/skill.yaml:17-19` — "the rendering-mode decision method comes from SK-FE-005 (not yet authored)" | verbatim |
| `skills/react/skill.yaml:19-21` — "the broader SSR/SSG/CSR rendering-mode decision comes from SK-FE-005 … not yet authored" | verbatim |
| `skills/skill-router/skill.yaml:102` — "If a candidate skill exists only as a taxonomy catalog entry and has not been authored, record the gap and route to the nearest authored skill" | verbatim |
| `skills/performance-engineering/skill.yaml:35-36` — symptom-gated activation | verbatim |

**Quantitative claim check (Critical F2.1).** `testing-payment-module.md:142-146`
claims 52 Tier B/C skills, of which only 3 have an execution-requiring
`verification` item. Tier count verifies exactly:

```
Tier B/C skills: 52  (Step 32 claims 52)
```

**Severity calibration.** 39 High out of 71 is High-heavy in the abstract, but
sampling the High headings shows they are a genuinely coherent class — "no skill
owns X," "a routing field cannot reach X" — i.e. gaps that degrade output on real
tasks without producing unsafe behavior. That maps correctly onto the High
definition (significant, fix soon, does not itself block release). I found **no
inflation**. I found one probable *deflation*: `frontend-product-listing.md:204`
rates the `SK-FE-005` gap **High**, while Step 28 called the same defect "the single
most significant cross-cutting finding." The "(instance of an inherited finding)"
tag makes High defensible for a re-discovery, but the underlying defect is Critical
(see M24-3).

**The "metadata-execution gap" framing.** It holds, and it is not overclaimed
pattern-matching. Two independent reasons:

1. The five instances at `synthesis.md:88-94` share a specific, non-trivial shape —
   a field that is well-formed and cross-referentially valid, yet either has no
   downstream consumer under the condition that matters, or is worded so as to
   exclude its own motivating case. That is narrower and more falsifiable than a
   generic "some things don't work."
2. **The pattern generalizes predictively to code Step 32 never examined.** Looking
   for the same shape in `adapters/` — outside Step 32's scope — surfaced two fresh
   instances: `FRONTMATTER_LIMITS` declared and never read (A16-4), and
   `RUNTIME_MEANINGFUL_FIELDS` omitting the fields L-2's own text names (A16-2). A
   pattern that predicts defects in a corpus it was not derived from is a real
   pattern.

Step 32 is, on this evidence, the highest-quality audit step in the project.
The two findings below are its residual gaps, not a rebuttal.

### R18-1 · Step 32 under-generalized the stale "not yet authored" class by roughly twenty-fold — **High**

**Finding.** `synthesis.md:230-236` lists as priority #1 a "mechanically-cheap"
fix: `data-modeling/skill.yaml:34`'s stale "not yet authored" cross-reference, "one
line."

The class is far larger. Scanning every `skill.yaml` and `SKILL.md` for the phrase
and resolving the IDs named on the same line against the 86 real IDs:

```
SAME-LINE stale sites: 21 in 15 files
  unambiguously stale (every ID on the line exists): 17
  mixed (line names one real + one genuinely-missing skill):  4
```

Verified examples, opened individually:

- `skills/redis/skill.yaml:9` — `parents: [SK-DATA-004, SK-BE-004, SK-DATA-005]   # caching-strategy, realtime-communication, search-integration (all forward references — not yet authored in this library)` — **all three exist.**
- `skills/docker/skill.yaml:9` — `parents: [SK-INFRA-001, SK-QA-002]   # containerization; security-engineering (not yet authored)` — **security-engineering exists.**
- `skills/mui/skill.yaml:24` — styling-systems and ui-ux-design "not yet authored" — **both exist.**
- `skills/sass/skill.yaml:9`, `skills/tailwindcss/skill.yaml:9`, `skills/web-standards/skill.yaml:28` — `SK-FE-003` "not yet authored" — **exists.**
- `skills/nuxt/skill.yaml:9` and `skills/nextjs/skill.yaml:19` — `SK-GROW-001` "not yet authored" — **exists.**

**The sharpest evidence that this was missed rather than scoped out:** Step 32
quoted `skills/nextjs/skill.yaml:17-19` verbatim at
`frontend-product-listing.md:214-215` to establish the `SK-FE-005` gap. The line it
quoted *also* says "SEO mechanics come from SK-GROW-001 (not yet authored)" — and
`SK-GROW-001` (seo-optimization) has existed since Step 26. A second instance of the
class was inside the quoted text and went unremarked.

**Why it matters.** These annotations sit in `parents` comments — the field that
encodes the taxonomy hierarchy. A maintainer or agent reading `redis/skill.yaml`
is told its three parents are unwritten when all three are authored, which
suppresses exactly the cross-skill references the library's single-owner rule (QR-2)
depends on.

**Root cause.** Layer-4 technology skills were authored before their Layer-3
parents; the forward-reference annotations were correct when written and were never
swept when the parents landed. No mechanism exists to detect a comment that has gone
stale (see M24-2).

**Recommended correction.** Treat this as one sweep, not one line. Re-run the scan
above and correct all 17 unambiguous sites; the 4 mixed lines need the
`SK-FE-005`-specific clause retained and the rest removed.

### R18-2 · F2.1's stated criteria do not reproduce its stated result — **Low**

**Finding.** `testing-payment-module.md:142-145` states the method as: verification
items "whose wording requires execution (run / executed / benchmark / green /
passes)," yielding 3 skills. Applying that exact word list literally yields **6**:

```
data-migration ['run'], git-workflow ['executed'], opensearch ['benchmark'],
performance-engineering ['benchmark'], sentry ['run'], typescript ['run']
```

Inspecting the three extras, Step 32's **exclusions are correct**:
`data-migration` ("not run as a single blocking operation") and `sentry` ("run
before the corresponding deploy") use "run" descriptively about the code's
behavior, not about executing a check. `typescript` is the genuinely interesting
one — *"`tsc --noEmit` … is **proposed or run** to confirm a change actually
type-checks"* — whose disjunction provides an explicit execution-free escape hatch,
arguably a *stronger* illustration of F2.1 than the three cited.

So the finding's conclusion is sound and its judgment was better than a keyword
match. The defect is reproducibility: a reader following the stated method gets a
different number and may conclude the finding is overstated.

**Recommended correction.** Restate the method as semantic classification with the
keyword list as a starting filter, and cite `typescript`'s "proposed or run" as a
worked boundary case.

---

## 24. Maintainability — could a new contributor add an 87th skill correctly?

**Short answer: no, not from what is written down.** The authoring *contract*
(`core/skill-specification/specification.md`) is genuinely excellent — 38 fields
specified, 15 body sections with R/C/O status, five rulesets with `[V]`/`[A]`/`[E]`
enforcement tags, and two worked examples. The *process* around it is broken at
three points a contributor hits in their first ten minutes.

### M24-2 · The mandatory mechanical validator does not exist — **Critical**

**Finding.** `specification.md:216-222` defines the conformance lifecycle:

> 2. Run the mechanical validator (all **[V]** rules) — must pass.

There is no validator. Every Python file in the repository:

```
$ find . -name "*.py" -not -path "./.git/*"
./adapters/antigravity/adapter.py
./adapters/claude-code/adapter.py
./adapters/codex/adapter.py
./adapters/cursor/adapter.py
./adapters/lib/common.py
./adapters/lib/__init__.py
./adapters/lib/loss_manifest.py
./adapters/lib/skill_loader.py
./adapters/mcp/adapter.py
./adapters/tests/test_compatibility.py
./adapters/windsurf/adapter.py
```

All eleven are the Step 31 adapter layer. There is no `tools/`, `scripts/`, `bin/`,
or `validator/` directory. `skills/README.md:110-112` confirms it in prose: "None of
the above have a validator, evaluator, or adapter implementation yet."

Step 2 of the three-step authoring contract is therefore unexecutable. A
conscientious new contributor cannot comply, and has no way to know their skill is
wrong before submitting it.

**This is not theoretical.** The absence has a measurable cost in the current tree:
9 VR-3 violations (M24-3) and 17 stale cross-reference annotations (R18-1) are all
`[V]`-class defects sitting in shipped metadata, undetected across 30 build steps,
because the thing designed to detect them was never built. The 15 domain-validation
audits in `audits/` each assert "VR-3 … all resolve" — those were human passes, and
they missed it.

**Root cause.** `core/` was scoped as design-only ("no executable validator"), and
no later step took ownership of building it. The adapter layer is the project's only
executable artifact, and it was scoped to projection, not validation — yet it
already contains most of what a validator needs (`lib/skill_loader.py` parses every
skill; `load_all()` walks the library).

**Recommended correction.** Build a `[V]`-rule validator. VR-1/VR-2/VR-3/VR-5/VR-6/VR-8
are all mechanically checkable and several are ~10 lines each on top of
`skill_loader.load_all()` — I implemented ad-hoc versions of VR-3 and VR-5 during
this audit in a few lines apiece. Until it exists, `specification.md:218` should not
state a step that cannot be performed.

### M24-3 · Nine live VR-3 violations in shipped metadata, known since Step 28 and unresolved — **Critical**

**Finding.** VR-3 (`specification.md:174`) requires that
`depends_on_skills`/`related_skills`/`conflicts_with`/`parents` reference existing
skill IDs. Checked mechanically across all 86 skills:

```
VR-3 VIOLATIONS (built skill -> nonexistent ID): 9
  SK-FE-005       <- SK-TECH-react.parents, SK-TECH-nextjs.parents,
                     SK-TECH-vue.parents, SK-TECH-nuxt.parents,
                     SK-TECH-angular.parents,
                     SK-GROW-001.related_skills, SK-QA-003.related_skills
  SK-GROW-002     <- SK-GROW-001.related_skills
  SK-TECH-graphql <- SK-BE-003.related_skills
```

Five of the seven `SK-FE-005` references are in **`parents`** — the load-bearing
taxonomy-hierarchy field — on five of the most heavily-used technology skills in the
library. React, Next.js, Vue, Nuxt, and Angular each declare a parent that does not
exist.

`SK-FE-005` and `SK-GROW-002` are approved catalog entries
(`core/taxonomy/skill-catalog.md:341`, `:631`) that were never authored; the catalog
does not distinguish built entries from backlog entries. They additionally propagate
into `core/routing-architecture/examples.md:38,74,159,161`,
`core/dependency-architecture/dependency-graph.md:78,93,110,112`, and five
evaluation scenarios (E17-1, E17-2).

**Status.** `audits/2026-09-10-individual-skill-review.md:100-133` found this in
Step 28, titled it "Approved but unauthored skills (the single most significant
cross-cutting finding)," counted exactly the same 9 sites, laid out Option A (author
the three skills; `SK-FE-005` alone resolves 7 of 9) versus Option B (strip the
references), and explicitly deferred: "Not resolved in this step." Steps 29, 30, 31,
and 32 did not resolve it either. Step 32 re-derived it from a live task trace
(`frontend-product-listing.md:204-243`) and added the important observation that the
gap is *wider* than the missing skill, because `frontend-architecture` and `nextjs`
deliberately carved the rendering-mode decision out of their own scope in deference
to a skill that never arrived.

I am raising it from Step 28's implicit rating to **Critical** on three grounds: it
is a violation of a normative `[V]` rule in shipped content; it breaks the taxonomy
hierarchy of five flagship skills; and it has now survived five consecutive audit
steps, each of which correctly identified it and deferred it. It is Step 33's to
close.

**Recommended correction.** Take Option A or Option B and apply it in one pass
across all nine sites plus the four `core/` documents plus the five evaluation
files. If Option B, `frontend-architecture/skill.yaml:25-26` and
`nextjs/skill.yaml:17-19` must be *widened* in the same pass, not merely
de-referenced, or the rendering-mode decision stays orphaned (Step 32's point, and
it is correct).

### M24-1 · The repository's front door tells a new contributor the project is empty and closed — **High**

**Finding.** Root `README.md`, the first file any contributor opens:

- `:13-17` — "## Status — Scaffold only. No skills have been written yet. The
  directory structure and initial files exist so that skill authoring can begin on a
  stable foundation." There are 86 authored skills.
- `:66-70` — "## Contributing skills — Not yet — the schema in `core/` needs to
  exist first." The schema exists, is version 1.0, and is 240 lines.

A contributor who reads only the README concludes there is nothing to contribute to
and no process to follow. Both statements were true at commit time (2026-09-09) and
neither was updated across 30 build steps.

**Recommended correction.** Rewrite `## Status` and `## Contributing skills` to
describe the current state, and point the latter at `specification.md:214-222` plus
the two worked examples. This is the single highest-leverage maintainability fix in
this category.

### M24-4 · Seventeen stale "not yet authored" annotations across fifteen files — **High**

Same defect as R18-1, recorded here because it is a maintainability defect in
`skills/`, not only a gap in Step 32's coverage. Evidence and recommendation as
above. A contributor reading `redis/skill.yaml:9` is told its three parents are
unwritten; all three are authored, and QR-2 requires referencing them.

### M24-5 · The architectural-decision record points at an inaccessible conversation — **Medium**

`README.md:72-77`:

> See the end of the initial-scaffold conversation/PR for the full list of decisions
> that should be reviewed before skill authoring begins (license choice, `skills/`
> vs `final/` promotion mechanism, per-skill versioning strategy, adapter
> granularity, and skill schema ownership).

Five open architectural decisions are recorded by pointer to a conversation that is
not in the repository. This is the brief's "tribal knowledge accumulated across this
project's own build steps that isn't written down anywhere a new contributor would
find it," in its literal form. At least two of the five (promotion mechanism,
per-skill versioning) are things a contributor adding an 87th skill must know:
`final/` exists but is empty, and every one of the 86 skills is stamped "authored,
not yet validated/evaluated," so no worked example of promotion exists either.

`README.md:79-83` compounds it — the MIT license is flagged as needing confirmation
"before the library is opened up to external contributors."

**Recommended correction.** Inline the five decisions as an ADR section or
`docs/decisions.md` with current status for each.

### M24-6 · `skills/README.md` denies the existence of the adapter layer — **Medium**

`skills/README.md:109-112`: "None of the above have a validator, evaluator, or
adapter implementation yet — those are separate, not-yet-built pieces of tooling."
Six adapters and a passing compatibility suite have existed since Step 31. The
validator and evaluator halves of that sentence are still accurate (M24-2); the
adapter half is not. (Positive: the file's skill table is exactly in sync — 86 rows,
zero listed-not-on-disk, zero on-disk-not-listed.)

### M24-7 · `CHANGELOG.md` and `VERSION` are frozen at the scaffold commit — **Medium**

`VERSION` is `0.1.0`; `CHANGELOG.md`'s newest entry is `[0.1.0] - 2026-09-09`, whose
body reads "No skills, schemas, or adapters implemented yet." `[Unreleased]` is
empty. Thirty build steps — the entire specification, 86 skills, the orchestrator,
the adapter layer, the evaluation suite — are unrecorded, while `README.md:58-64`
commits the project to Semantic Versioning and points at both files. A contributor
has no way to learn what changed when.

### M24-8 · No single authoring entry point — **Medium**

There is no `CONTRIBUTING.md`. The authoring contract is distributed across
`specification.md` §1-§5, `core/skill-specification/README.md`, `skills/README.md`,
`core/taxonomy/skill-catalog.md` (which ID to claim), and the two `examples/`
skills — none of which links to the others as a sequence, and two of which are
actively misleading (M24-1, M24-6). The pieces are individually good; there is no
path through them.

**Combined recommendation for this category.** One `CONTRIBUTING.md` that sequences:
claim an ID from the catalog → copy `examples/minimal/` → fill `skill.yaml` per
`specification.md` §2 → write `SKILL.md` per §3.2 → run the validator (once M24-2 is
fixed) → add an `evaluations/` scenario → register in `skills/README.md`. Fixing
M24-1 and writing this file would move this category from "no" to "yes."

---

## 25. Extensibility

### Adding a 7th adapter target — the claim tested

`adapters/README.md:32-37` claims the design "already accommodates" a 7th/8th
adapter (VS Code, Custom). I reasoned this through concretely against the existing
six as a template. **The claim substantially holds, with one real gap.**

What a VS Code adapter would need, and whether it exists:

| Requirement | Status |
|---|---|
| Field-mapping specification | **Exists** — `adapter-projection.md:51-64` has a full VS Code column (`name` ≤64, `description` ≤1024, `argument-hint`, `user-invocable`, `disable-model-invocation`, `context: fork`), plus per-target prose at `:120-125` |
| Vendor research to ground it | **Exists** — `research/agent-ecosystems/vscode.md` |
| Code template | **Exists** — `adapters/cursor/adapter.py` is 76 lines: `TARGET`, `PATH_TEMPLATE`, one `project()` calling seven shared helpers |
| Shared engine reuse | **Exists** — `lib/skill_loader.py`, `lib/loss_manifest.py`, `lib/common.py` are target-agnostic; no change needed |
| Loss-manifest support for its lossiness | **Partially missing** — see X25-2 |
| Registration in the test suite | **Manual** — see X25-3 |

The per-target README contract (six documented aspects, `adapters/README.md:66-73`)
is clear and reusable. Structurally, a competent contributor could produce a working
7th adapter in an afternoon. That is a genuine architectural success and the shared-
engine rule (`:39-49`) is the reason.

### X25-2 · VS Code is the only target with hard field limits, and the lossiness contract has no concept of truncation — **Medium**

**Finding.** Of the eight designed targets, VS Code is the only one with documented
hard limits: `name` ≤64, `description` ≤1024 (`adapter-projection.md:53-54,121`). A
VS Code adapter would therefore be the **first** target that must actually truncate.
It would find the machinery half-built (A16-4): `truncate()` exists but is called
with `None` at all eight existing sites; `FRONTMATTER_LIMITS` is an empty, unread
dict; `claude-code/adapter.py:34,37` capture truncation flags and discard them.

More fundamentally, **the lossiness contract has no action for partial loss.**
`LossManifest` offers `native` / `body` / `drop+note` / `n/a`
(`lib/loss_manifest.py:27-47`). A truncated description is none of these — it is
natively represented *and* lossy. L-1 through L-5 (`adapter-projection.md:142-157`)
likewise treat loss as binary. So the 7th adapter cannot be written without
extending the contract itself, which is the one thing `adapters/README.md:32-37`
implies is unnecessary.

Current headroom masks it: the longest description in the library is 499 chars and
the longest name is 26, both far inside VS Code's limits. But the limits differ from
CE-1's 500-char cap by a factor of two, and nothing ties the library rule to the
vendor rule.

**Recommended correction.** Add a `truncated` action to `LossManifest` and an L-6
clause covering representable-but-lossy projection; populate `FRONTMATTER_LIMITS`
and enforce it in the test suite. This is cheap now and blocking later.

### X25-1 · Four documents advertise eight targets; six exist, and only one of the four says so — **Medium**

**Finding.** `adapter-projection.md:2-3` opens "How a canonical skill … projects into
each of the **eight** targets" and its matrix carries complete VS Code and Custom
columns. `core/skill-specification/README.md:10-11` and `:44-57` list all eight,
including a `└─▶ VS Code` branch in the projection diagram. Root `README.md:6-8`
tells consumers the library "can be consumed by coding agents such as … **VS Code
agents**, MCP-based agents, and future/custom agents."

Only `adapters/README.md:32-37` states the truth — that VS Code and Custom "weren't
in the plan's required list" and are not built. That disclosure lives in the one
file a consumer is least likely to read before deciding whether the library supports
their agent.

("Custom" is a different case and is honestly handled: `adapter-projection.md:136-140`
correctly explains that the canonical format *is* the contract for a custom agent,
so "no adapter" is the design, not a gap.)

**Recommended correction.** Add a one-line status marker to the matrix header and to
`skill-specification/README.md`'s diagram distinguishing built targets from designed-
but-unbuilt ones, and qualify root `README.md:6-8`.

### X25-3 · No target registry; adding an adapter requires editing the test suite — **Low**

`TARGETS` is a hardcoded list at `adapters/tests/test_compatibility.py:38`, and
`adapters/README.md`'s structure diagram (`:13-30`) hardcodes the same six. There is
no discovery mechanism (e.g. globbing `adapters/*/adapter.py`) and no documented
"how to add a target" procedure anywhere. A contributor adding a 7th adapter must
infer that the test file needs editing. Minor, but it is the one place the
otherwise-clean extension path has an undocumented step.

**Recommended correction.** Derive `TARGETS` by globbing for `adapters/*/adapter.py`,
and add a short "Adding a target" section to `adapters/README.md`.

### Adding a taxonomy layer or domain — verified low-cost

`layer` and `domain` are in `IDENTITY_ONLY_FIELDS`
(`adapters/lib/skill_loader.py:74`) and are recorded as `n/a` in every manifest
("Internal taxonomy/identity metadata; not meaningful to a consuming agent"). No
adapter branches on either value — confirmed by reading all six `project()`
functions. **Adding a Layer 5 or a new domain therefore costs nothing in the adapter
layer**, which is the correct design and a real strength.

The cost lands entirely in `core/`: `skill-catalog.md`, `taxonomy-analysis.md`, the
dependency graph and matrices, and the routing rules would each need extension, and
VR-4 (layer-monotone dependencies) would need its ordering updated. That is
appropriate — taxonomy is a `core/` concern — but it is undocumented as a procedure,
the same gap as M24-8.

---

## Release-readiness contribution

Across my five categories the library's **executable** layer is in materially better
shape than its **process** layer. The adapter engine is the strongest artifact in
the repository: it projects all 86 skills across all 6 targets with zero L-1 gaps
and zero L-2 violations under independent re-execution, its shared-engine design
genuinely makes a 7th target cheap, and its field taxonomy has not drifted despite
11 skills being added since it was written. Step 32 is the strongest audit: its
published totals reproduce exactly, five of five sampled citations are verbatim, its
quantitative claims verify, its severity calibration shows no inflation, and its
"metadata-execution gap" framing is a real pattern — demonstrated by the fact that
it predicted two further defects in adapter code Step 32 never looked at. The
evaluation suite's scoring model is rigorous and its published assertion counts
match the corpus exactly.

The blocking problems are in how this library would be *maintained and extended*,
not in what it currently does. Two Critical findings form one causal chain: the
authoring contract mandates a mechanical validator at step 2 of 3, that validator
was never built, and in its absence nine violations of a normative `[V]` rule sit in
shipped metadata — five of them in the `parents` field of React, Next.js, Vue, Nuxt,
and Angular, which each declare a parent skill that does not exist. That defect was
correctly identified in Step 28, explicitly deferred, and then re-identified and
deferred again in Steps 29 through 32. It cannot be deferred past Step 33 without
the deferral itself becoming the release risk. The same missing validator explains
seventeen stale "not yet authored" annotations that Step 32 under-scoped as a
one-line fix, and it is why five evaluation scenarios reference skills that do not
exist — including one (S05) whose expected sequencing graph is unsatisfiable as
written.

**My recommendation for release readiness:** not ready, but the gap is narrow and
almost entirely mechanical. Resolve M24-3 with a single decision applied across all
nine metadata sites plus the four `core/` documents and five evaluation files;
build the `[V]`-rule validator (VR-1/2/3/5/6/8 are each roughly ten lines on top of
the existing `skill_loader.load_all()`, as demonstrated by the ad-hoc checks run for
this audit) and wire it beside the adapter suite; sweep the seventeen stale
annotations; and rewrite the root README's Status and Contributing sections, which
currently tell every prospective contributor that the project is an empty scaffold
not accepting contributions. None of these require new design work, and none touch
skill content. The seven High findings should follow but do not block. On the
explicit verification items I found nothing to correct: no AI branding anywhere in
`skills/`, `core/`, `adapters/`, or `evaluations/`; attribution and provenance
intact (83/86 skills carry `source_references`, the three exceptions correctly
exempt under SG-4); and the only Step/Phase references in shipped content are the
three confirmed sites in adapter code, whose surrounding reasoning is load-bearing
but whose step numbers are not — the master build plan is not in this repository, so
every "Step N" citation in shipped code is unresolvable to any future reader.
