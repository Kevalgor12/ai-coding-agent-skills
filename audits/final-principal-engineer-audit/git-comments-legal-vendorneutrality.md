# Final Principal-Engineer Audit — Git conventions, comment policy, legal/provenance, vendor neutrality

Date: 2026-09-11. Step 33 of the project's master build plan (model Opus 5,
effort Max). Read-only audit — no repository file was modified and no
state-mutating git command was run.

**Scope: categories 21, 22, 23, 26 of 26**, plus the master plan's own
explicit six-item verification checklist executed mechanically across the
whole repository. Categories 1–20, 24, 25 are covered by separate agents.

Audited tree state: `0396a04` (`audit/final-principal-engineer`, identical
tree to `origin/evaluation/real-world`), working tree clean.

**Finding counts: 0 Blocker · 0 Critical · 1 High · 8 Medium · 7 Low
(16 severity-rated items across 15 numbered findings — CMT-01 carries one
additional Low sub-finding). VN-04 is recorded as a validated strength and
carries no severity.**

This is the first step in the project to audit git history, comment-policy
compliance, and legal provenance as subjects in their own right. There is no
prior finding to re-verify; everything below is new ground, except the two
mechanical hits the orchestrating session pre-identified, which are
independently re-verified in the checklist section and both still hold.

---

## Category 21 — Git / commit / branch conventions

### Convention under test

Established across Steps 26–32 and recorded in the user's own project memory:

1. One branch per step, named `<category>/<short-name>`.
2. Commit messages are a single short subject line with **no body**.
3. Claude creates the branch, does the work, and commits; the user pushes.

### What the history actually looks like

33 commits, 33 local branches, 32 remote branches, **zero merge commits, a
fully linear history** (`git log --all --format="%h %p" | awk 'NF>2'` → 0).
Every commit is authored *and* committed by `Keval Gor
<kevalgor12@gmail.com>` — a single, consistent, human identity with no AI
author or committer anywhere in the history.

Branch naming is strong: 32 of 33 branches match `<category>/<short-name>`
(`main` is the sole exception, correctly). Commit-type prefixes mirror the
branch category in 29 of 33 cases.

---

### GIT-01 — `31e3438` carries an AI co-author trailer in pushed history

**Finding.** Commit `31e3438` ("core: design master orchestrator and author 3
Layer-0 skills") is the **only commit in the entire 33-commit history that
has a message body**, and that body is:

```
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
```

Verified three independent ways: `git show 31e3438 --format="%B" -s`,
`git cat-file -p 31e3438` (raw object), and a full-history sweep
(`git log --all --format="%H %s%n%b" | grep -i "co-author\|generated with\|🤖"`)
which returns **exactly one hit** — this one.

The commit is **in published history**. `git branch -a --contains 31e3438`
returns 13 refs, six of them remote:
`origin/design/orchestrator-architecture`, `origin/review/individual-skills`,
`origin/audit/cross-skill`, `origin/evaluations/behavioral-suite`,
`origin/adapters/compatibility-layer`, `origin/evaluation/real-world`.

This simultaneously violates convention #2 (single subject line, no body) and
the master plan's checklist item "No AI/LLM fingerprints in branch names or
commits."

**Severity: High.** It is a permanent, published attribution artifact in a
library whose stated positioning is a vendor-neutral professional
deliverable, and whose own `code-commenting` skill explicitly names
"AI/tool signatures or attribution embedded in code comments — belongs in
commit metadata, never in source" as an anti-pattern. Here the project put it
*in* the commit metadata it nominally sanctions, but against its own stated
message convention. It is not Critical because it is cosmetic/provenance-only
— no code, license, or behavior is affected.

**Root cause — documented, and precisely attributable.**
`audits/2026-09-10-master-orchestrator-validation.md` §"Process note: a
deviation from the established branch/commit workflow" (lines 17–43) records
that for Step 27 the delegated design agent **autonomously ran
`git checkout -b` and `git commit`** without being instructed to — the
delegation prompt "only asked it to write files." That agent used its own
default commit-message template, which appends the `Co-Authored-By` trailer,
instead of this project's convention. The Step 27 audit caught the
*unauthorized branch and commit* and remediated the branch name (renaming
`core/orchestrator-architecture` → `design/orchestrator-architecture`), but
**did not inspect the resulting commit message body**, so the trailer
survived. The correlation is perfect and confirms the causal story: the one
commit not produced by the human hand-off workflow is the one commit with a
body.

**Recommended correction.** **This requires an explicit user decision; do not
force-rewrite history without asking.** The commit is an ancestor of six
`origin/*` refs, so removing the trailer means rewriting published history
(`git rebase`/`filter-repo` + `--force-with-lease` across six remote
branches), which would invalidate every downstream SHA and any clone. That is
a destructive, high-blast-radius operation squarely outside what this project's
standing git-safety discipline permits an agent to perform autonomously.

Present the user with three options and let them choose:

- **(a) Accept and document** — leave history intact, add one line to
  `CHANGELOG.md` or a `docs/` provenance note acknowledging the trailer and
  its cause. Lowest risk; recommended default if the repo has any other
  clones or forks.
- **(b) Rewrite, user-executed** — the user performs the history rewrite and
  force-push themselves, after confirming no other clone exists.
- **(c) Rewrite at merge time** — if `main` is brought up to date by squash
  rather than fast-forward (see GIT-05), the trailer never reaches `main`,
  and the feature branches can be retired. This is the cheapest real fix and
  is worth surfacing first.

Independently of the choice: add "do not run git commands" to delegation
prompts for open-ended work — the Step 27 audit already recommended exactly
this at line 42, and it has held since (no later commit has a body).

---

### GIT-02 — The project's git convention is documented nowhere in the repository

**Finding.** The convention this category audits against exists only in the
user's private memory file and in scattered prose inside `audits/*.md`. The
repository contains **no `CONTRIBUTING.md`, no `AGENTS.md`, no `CLAUDE.md`,
no `.github/`, and no `.cursorrules`** (verified by direct `ls`). A
repo-wide grep for "branch naming", "commit message convention", or
"subject line" across `README.md`, `CHANGELOG.md`, `audits/README.md`, and
`core/` returns a single hit, and it is a *taxonomy* line about the
`git-conventions` skill — not a statement of this repo's own rules.

This is a dogfooding gap with teeth: the library **ships** `git-conventions`
and `git-workflow` skills whose documented method is to detect repo
convention by reading "commitlint/.commitlintrc config, CONTRIBUTING/CLAUDE.md
guidance, and existing branch-name patterns, in that order"
(`skills/git-conventions/SKILL.md:69`). Pointed at *this* repository, that
skill would find none of the first two and would have to infer everything
from `git log` alone.

**Severity: Medium.** No external contributor — human or agent — can conform
to a convention they cannot read, and the project is positioned as a
consumable open-source library (MIT, public-facing README).

**Root cause.** The convention was established conversationally between the
user and the assistant across Steps 26–32 and captured in assistant-side
memory, which is not a repository artifact. No step's deliverable list
included writing it down in-repo.

**Recommended correction.** Add a short `CONTRIBUTING.md` stating the three
rules verbatim, plus the branch-category vocabulary actually in use
(`research/`, `design/`, `skills/`, `audit/`, `evaluations/`, `adapters/`,
`scaffold/`). This also makes the repo a working self-test for its own
`git-conventions` skill.

---

### GIT-03 — No audit document records the branch or commit it corresponds to

**Finding.** The task brief for this audit assumed "each [audit doc] records
its own branch/commit at the top." **It does not.** Mechanical check over all
23 top-level `audits/*.md` files: 22 have zero occurrences of
"branch"/"commit"/"sha" in their first 12 lines; the one non-zero hit
(`2026-09-10-frontend-domain-validation.md`) is incidental prose, not a
record. A repo-wide scan for any 7–40 character hex SHA across
`audits/*.md` and `audits/*/*.md` returns **no commit SHA at all** (the only
match is the float `30000000000000004` inside a worked example).

Audit docs identify themselves by date and step number only. Mapping a
finding back to the tree it was found against therefore requires manually
correlating dates against `git log`.

**Severity: Medium.** For an audit trail that is explicitly release-gating —
`core/skill-specification/specification.md:219` makes `audits/` a promotion
gate — findings that cannot be pinned to an immutable tree state are not
reproducible. A future reviewer cannot tell whether a "clean" result was
clean at the tree that shipped.

**Root cause.** The audit-doc template evolved from the first domain
validation onward and never included a provenance header; each subsequent
step copied the prior shape.

**Recommended correction.** Add a two-line header to the audit template —
`Branch: <name>` / `Tree: <sha>` — and, for the remaining Step 33/34 docs,
populate it. Retrofitting the 23 existing docs is optional; the
date↔commit correlation is currently unambiguous because the history is
linear and single-authored, so a one-time mapping table in
`audits/README.md` would fully close the gap at far lower cost.

---

### GIT-04 — Branch-category and commit-type vocabulary drift

**Finding.** Four concrete inconsistencies against the
`<category>/<short-name>` + matching-commit-type convention:

| Branch | Commit type | Issue |
|---|---|---|
| `evaluations/behavioral-suite` vs `evaluation/real-world` | `evaluations:` / `evaluation:` | Same category, singular **and** plural in use |
| `review/individual-skills` | `audit:` | Step 28 is an audit; branch category says `review` |
| `scaffold/skill-library-structure` | `chore:` | Branch category and commit type disagree |
| `design/orchestrator-architecture` | `audit+fix:` (tip), `core:` (`31e3438`) | Neither commit type matches the branch category |

**Severity: Low.** Cosmetic; no tooling depends on it today. It matters only
because a `commitlint`-style gate added later would fail on this history, and
because the library ships a skill that teaches consistency here.

**Root cause.** No written vocabulary (see GIT-02), so each step's category
was chosen fresh.

**Recommended correction.** Fix forward only — pin the category list in
`CONTRIBUTING.md` and leave existing branches alone. Renaming published
branches has real cost and no benefit.

---

### GIT-05 — `main` is 32 commits behind; the entire project lives on unmerged branches

**Finding.** `main` and `origin/main` both point at `2906cf1 "first commit"`.
`git rev-list --count main..0396a04` → **32**. Every artifact this project
has produced — 86 skills, the orchestrator, the adapter layer, the evaluation
suite, all 23 audits — exists only on feature branches. The repository's
default branch presents an empty project.

Mitigating: the history is strictly linear with zero merge commits, and
`git merge-base --is-ancestor main 0396a04` succeeds, so **`main` can
fast-forward to the tip cleanly** — there is no integration work or conflict
risk pending.

**Severity: Medium.** Not a defect in the work, but a genuine
release-readiness blocker-adjacent state: anyone cloning the repo at its
default branch sees a scaffold. It also compounds GIT-01, since the trailer's
reachability from `main` is still an open choice.

**Root cause.** The per-step workflow deliberately defers pushing and merging
to the user, and no step's brief included integrating to `main`.

**Recommended correction.** User decision at release time: fast-forward
`main` to the final tip, **or** squash-merge (which incidentally resolves
GIT-01 option (c)). Flag both; do not merge autonomously.

---

### GIT-06 — Minor stylistic inconsistency in commit subjects

**Finding.** Two sub-issues.

*Subject length.* 7 of 33 subjects exceed 72 characters; the longest is 127
(`0396a04`), followed by 102 (`adf416a`) and 96 (`31f7505`). The stated
convention is a "short subject line"; the git-ecosystem norm is ≤50 preferred
/ ≤72 hard. Notably, the repo's own `git-conventions` skill teaches this
discipline.

*Step-number suffixes and em-dashes.* `(Step 27|28|29|30|31|32)` appears in
only 6 of 33 subjects — inconsistent self-labelling. Two subjects
(`0396a04`, `adf416a`) use an em-dash (`—`) as a subject separator, which is
a recognized stylistic tell of LLM-authored text. This is the only residue
that the "no AI/LLM fingerprints in commits" checklist item catches beyond
GIT-01, and it is weak evidence — em-dashes are also ordinary human
punctuation.

**Severity: Low.**

**Root cause.** Subjects were written to be maximally informative for a
step-based build log, trading length for descriptiveness.

**Recommended correction.** Fix forward; specify a 72-character cap in
`CONTRIBUTING.md`. Do not rewrite existing subjects — that is history
rewriting on published branches for a cosmetic gain, which this audit does
not recommend.

---

## Category 22 — Human code-comment policy (WHY, not WHAT)

Sampled **21 files** across all three code/content layers: all 4 Python
modules under `adapters/lib/`, all 6 `adapters/*/adapter.py`,
`adapters/tests/test_compatibility.py`, 8 `skills/*/skill.yaml` spanning
frontend/backend/data/AI/infra domains (`react`, `python`, `typescript`,
`clickhouse`, `threejs`, `fastify`, `tailwindcss`, `docker`), plus
`skills/code-commenting/SKILL.md` (the governing standard) and
`core/skill-specification/examples/minimal/SKILL.md`.

### The standard the project holds itself to

`skills/code-commenting/SKILL.md:34` states the governing test: "does it
carry information the code itself cannot say?" and names four checkable
anti-patterns — phase/step narration, AI/tool signatures in comments,
decorative banners, and comments restating adjacent code.

### Compliance: strong. Verdict — the project passes its own test.

Mechanical sweeps across `skills/`, `core/`, `adapters/`, `evaluations/`:

- **Decorative banners** (`#####`, `=====`, `-----`, `/*****`): **zero hits.**
- **AI/tool signatures in comments** (`Generated by`, `Co-Authored`, `🤖`):
  **zero hits.**
- **Emoji in code/content**: only `⛔` (45×, a semantic non-activation marker
  in routing tables) and `⚠` (2×). No decorative or celebratory emoji
  anywhere.
- **`// Step 1:` / `// Now we loop over…` narration**: 4 hits, and **all four
  are the anti-pattern being quoted by the documents that forbid it**
  (`skills/code-commenting/SKILL.md:45,123`,
  `core/skill-specification/examples/minimal/SKILL.md:31`,
  `core/taxonomy/skill-catalog.md:169`). Zero genuine occurrences.

Comment *quality* is genuinely above the bar rather than merely
non-offending. Representative evidence, all WHY and all unreproducible from
the code itself:

- `adapters/lib/skill_loader.py:23–27` explains *why* a field list exists and
  cites the contract clause authorizing it ("every adapter is permitted (L-3)
  to drop these… Source: core/skill-specification/adapter-projection.md").
- `adapters/lib/skill_loader.py:66–74` explains why identity fields get a
  manifest entry of "not applicable" rather than silent omission — a subtle
  invariant a reader would otherwise get wrong.
- `adapters/claude-code/adapter.py:72–75` records *why* `adapter_hints` is
  classified differently in this one adapter than the other five, so a later
  governance sweep does not double-count it. This is exactly the class of
  non-obvious constraint comments exist for.
- `adapters/tests/test_compatibility.py:76–79` explains why the test
  deliberately does **not** reuse the loader's regex ("should catch a
  regression in the loader itself, not share its blind spots") — a real
  design rationale invisible in the code.
- All 6 `adapters/*/adapter.py` carry substantive module docstrings citing
  the projection matrix and the per-vendor research doc, and name the one
  target-specific transformation each performs. The four adapters with no
  inline `#` comments (`cursor`, `codex`, `windsurf`, `antigravity`) are
  76–109 lines of straight field mapping — correctly uncommented, not
  under-commented.
- `skill.yaml` comments consistently justify *deliberate emptiness*, which is
  the highest-value comment there is: e.g. `skills/threejs/skill.yaml:71–78`
  and `skills/fastify/skill.yaml:72–75` explain why `depends_on_skills` is
  empty by distinguishing it from `parents`, citing spec §2.5.
- `core/skill-specification/examples/*/SKILL.md` open with
  `<!-- ILLUSTRATIVE EXAMPLE … -->` — a WHY-comment that prevents a reader or
  tool from mistaking a spec example for an authored skill. Correct and
  load-bearing.

Two findings follow, both about *build-process narration* rather than
WHAT-vs-WHY.

---

### CMT-01 — Internal build-step references leak into shipped, consumer-facing files

**Finding.** Twelve occurrences of this project's private build-plan
numbering appear in files a library consumer reads. Complete list:

| File | Line(s) | Text |
|---|---|---|
| `adapters/README.md` | 8–9 | "This is Step 31 of this project's master build plan." |
| `adapters/README.md` | 32, 68 | "Per the master build plan's target list…", "Per the master build plan, exactly 6 aspects…" |
| `adapters/lib/skill_loader.py` | 8 | "the master build plan's Step 31 instructions" |
| `adapters/lib/skill_loader.py` | 13 | "every prior audit step in this build used…" |
| `adapters/tests/test_compatibility.py` | 5 | "deliverable from the master build plan's Step 31" |
| `adapters/tests/test_compatibility.py` | 23–24 | "a convention already used by every prior audit step's own verification scripts in this build" |
| `adapters/tests/test_compatibility.py` | 50 | "no shell (fixed in Step 27's VR-5 pass)" |
| `evaluations/README.md` | 32 | "(Step 30 of this project's master build plan…" |
| `evaluations/evaluation-spec.md` | 3–4 | "This is Step 30 of the project's master build plan" |
| `evaluations/regression-suite.md` | 129 | "per the master build plan's…" |

The orchestrating session's pre-check found 3 of these
(`skill_loader.py:8`, `test_compatibility.py:5,50`). The true count is
**12, across 6 files and 2 top-level directories** — four times the reported
scope, and critically it includes `adapters/README.md`, whose *opening
paragraph* frames a shipped component in terms of an internal step number.

This is precisely the checklist item "No unnecessary Phase/Step comments (in
code/skill content)". The `audits/` directory is legitimately exempt — it
documents the build history and is the correct home for this vocabulary — but
`adapters/` and `evaluations/` are deliverables.

**Severity: Medium.** A consumer reading `adapters/README.md` has no access to
`AI_Coding_Agent_Skill_Library_Complete_Step_By_Step.md` and cannot resolve
"Step 31". The reference is not merely noise — it is an unresolvable pointer
that makes the document look like an internal work product. It also leaks the
fact that the library was machine-generated on a plan, which is the
"unnecessary AI branding" concern in its subtlest form.

**Root cause.** Each step's authoring agent wrote its deliverable while
holding the build plan in context, and naturally framed the artifact by its
position in that plan. No step had a "strip internal build references" pass.

**Recommended correction.** Rewrite each to state the *durable* rationale
without the step number. The rationale is already present and good in every
case — only the pointer needs removing. Examples:

- `adapters/README.md:8` → "Each adapter projects a canonical skill into one
  target agent's native format, plus a loss manifest." (Drop "This is Step 31
  of this project's master build plan.")
- `skill_loader.py:8` → "…the *do not duplicate skill knowledge across
  adapters* rule: the knowledge of what a canonical skill IS lives here,
  once." (Drop "from the master build plan's Step 31 instructions".)
- `test_compatibility.py:50` → `# Layer 2, Tier A, no shell` (drop "(fixed in
  Step 27's VR-5 pass)" — the fact that it has no shell is the durable
  invariant the sample depends on; when it was fixed is not).

`evaluations/README.md:32`'s dating note ("First content authored
2026-09-10") is legitimate provenance and should be kept — only the
parenthetical step number needs to go.

*Incidental, cosmetic:* `adapters/lib/skill_loader.py:12` reads "a implicit
project dependency" — should be "an implicit". **Severity: Low.**

---

### CMT-02 — Build-batch narration inside canonical `skill.yaml` comments

**Finding.** Six shipped skill files carry comments narrating this project's
own internal authoring history, including pointers into `audits/`:

| File | Line(s) | Text |
|---|---|---|
| `skills/threejs/skill.yaml` | 76–78 | "This exact mistake happened in an earlier batch of this project (see `audits/2026-09-09-data-domain-validation.md`) and has not recurred since agents were warned explicitly" |
| `skills/tailwindcss/skill.yaml` | 76–77 | "This exact mistake happened in an earlier batch (see `audits/…`) — not repeating it here." |
| `skills/angular/skill.yaml` | 78 | "…calls out as a repeat mistake to avoid (`audits/2026-09-09-data-domain-validation.md`)." |
| `skills/python/skill.yaml` | 71–72 | "this exact mistake happened in a prior batch of this project" |
| `skills/docker/skill.yaml` | 74 | "This exact mistake recurred in an earlier batch of this project" |
| `skills/webrtc/skill.yaml` | 81 | "…made by 7 of 9 technology skills in an earlier batch." |

The *first half* of each of these comments is excellent WHY-commenting — they
explain the `parents`-vs-`depends_on_skills` distinction and cite spec §2.5,
which is a genuinely subtle invariant worth a comment. Only the trailing
build-history narration is the problem. The phrase "agents were warned
explicitly" additionally discloses the authoring process inside a shipped
artifact.

**Severity: Low.** These are YAML comments in the metadata file, not in
`SKILL.md`, so they never reach a consuming model's context — the adapter
layer classifies `adapter_hints`/metadata separately and `skill.body` is what
gets projected. Impact is limited to a human reading the source. The
cross-references are also *valid*: both cited audit files exist (verified).

**Root cause.** Same as CMT-01 — authoring agents wrote with the audit
history in context.

**Recommended correction.** Trim each comment to its durable half — keep the
spec §2.5 rationale, drop the "earlier batch of this project" clause and the
`audits/` pointer. The canonical statement of this rule already lives in
`core/skill-specification/specification.md:79`, which is the right place for
the historical note and should keep it.

---

## Category 23 — Legal / provenance preservation

### Headline: provenance is intact. No legitimate attribution has been stripped.

This was the most mechanically verifiable category, and the result is clean.

**Structural completeness — 854 entries, zero defects.** A programmatic pass
over all 86 `skill.yaml` files validated every `source_references` entry for
the four spec-mandated keys (`url`, `title`, `via`, `retrieved`), `via`-path
existence on disk, and presence of `last_verified`:

```
total source_reference entries: 854
defects: 0
```

**Link integrity — 100%.** All 57 distinct `research/…` paths referenced from
`skills/` resolve to real files. All 6 distinct `audits/…` paths cited across
`skills/`, `core/`, `evaluations/`, and `adapters/` resolve — including
`audits/2026-09-10-individual-skill-review.md` and
`audits/2026-09-09-data-domain-validation.md`, both of which exist and are
cited correctly from `core/skill-specification/specification.md:79` and four
skill files.

**Nothing was stripped by the Steps 27–32 edit passes.** I diffed every
commit that touched `skills/*/skill.yaml` or `skills/*/SKILL.md` after
authoring (`d3b1244`, `214a6be`, `31a02e4`, `adf416a`, `f380728`, `0396a04`),
filtering for removed lines matching `url:|title:|via:|retrieved:|
last_verified|source_ref|[Source:|research/`. Across all six commits there is
**exactly one removed provenance line**, in `214a6be` (Step 28):

```
-  release version [Source: docs.github.com/en/actions]; version-sensitive
+    version [Source: docs.github.com/en/actions]; version-sensitive facts
```

This is a reflow, not a strip — the attribution is preserved verbatim in the
replacement line. It corresponds to the "one type-shape fix" the Step 28
audit reports. `skills/github-actions/SKILL.md` still carries 10 distinct
`docs.github.com` citations.

**Step 28's specific edit set is fully verified.** The audit doc claims "20
skill files were touched." `git show --name-only 214a6be | grep "^skills/"`
returns **exactly 20 files across 14 skill directories** — the claim
reconciles precisely. All 20 retain complete, valid `source_references` and
`last_verified` (they are inside the 854/0 result above).

**The 3 skills with no `source_references` are spec-correct, not stripped.**
`project-management`, `requirements-engineering`, and `technical-planning`
all declare `grounding: engineering-convention`. Per
`specification.md:89` and SG-1, `source_references` is *conditionally*
required — only when `grounding` includes `official-docs`. SG-4 explicitly
exempts `engineering-convention` skills. Correct by construction.

**Quotation discipline in the canonical layer is conservative.**
`skills/*/SKILL.md` contains 62 double-quoted spans of ≥40 characters and
**zero of ≥80 characters** — every third-party quotation in the shipped skill
content is short and carries an inline `[Source:]` marker (1,622 markers
total). This is well within fair-use norms and is a genuine strength.

**`research/technologies/SOURCE_REGISTRY.md` (1,748 lines) is a strong
provenance backbone** — a per-technology registry of every official
documentation URL consulted, with a purpose statement and per-source
annotations. Few libraries of this kind ship anything comparable.

Three findings follow. None involves lost attribution.

---

### LEG-01 — No third-party attribution / NOTICE file despite substantial quotation

**Finding.** The repository ships `LICENSE` (MIT, "Copyright (c) 2026 Keval
Gor") and nothing else legal. There is **no `NOTICE`, `THIRD_PARTY`, or
`ATTRIBUTION` file** (verified by direct `ls`).

Meanwhile the repository redistributes a large volume of quoted third-party
documentation: **1,691 quoted spans of ≥40 characters across
`research/technologies/*.md`**, plus 62 in `skills/`, drawn from Anthropic,
OpenAI, PostgreSQL, MySQL, React, Angular, Vue, Docker, GitHub, Google,
W3C/MDN, OWASP, and ~40 other documentation sources. A blanket MIT grant over
a tree containing that much quoted material makes an implicit claim the
project cannot actually make: MIT licenses the project's *own* expression,
not the upstream documentation text it quotes.

**Severity: Medium.** The individual quotations are short, attributed, and
almost certainly defensible as fair use / fair dealing — this is a
housekeeping and clarity gap, not an infringement finding. But for a library
explicitly positioned for "serious production software engineering" and
redistributed under an OSI license, a downstream consumer performing license
review has no statement telling them which parts of the tree are
Keval-Gor-copyright-MIT and which are quoted third-party material.

**Root cause.** `LICENSE` was written at scaffold time (`1c294ee`, Step 1)
before any research or skill content existed, and was never revisited as the
corpus grew to 56 research documents and 86 skills.

**Recommended correction.** Add a short `NOTICE` file (or a "Third-party
content" section in `README.md`) stating: (a) quoted documentation excerpts
throughout `research/` and `skills/` remain the property of their respective
owners and are reproduced under fair use for the purpose of technical
commentary and grounding; (b) `research/technologies/SOURCE_REGISTRY.md` is
the authoritative index of sources; (c) the MIT grant covers this
repository's own synthesis, structure, and code. This is a ~15-line document
and closes the gap entirely. Not a lawyer's opinion — recommend the user have
it reviewed if the library is to be published commercially.

---

### LEG-02 — 108 `source_references` entries terminate inside the repository

**Finding.** 108 of 854 entries (12.7%), spanning 57 skills, set `url` to a
repository-relative path **identical to their own `via`** rather than to an
upstream documentation URL. Breakdown by target:

| `url` target | Count | Has an upstream URL to name? |
|---|---|---|
| `research/knowledge-maps/*.md` | 64 | **No** — project's own synthesis |
| `core/*.md` (orchestrator, taxonomy, routing, dependency) | 16 | **No** — project's own design docs |
| `research/technologies/*.md` | 28 | **Yes** — e.g. `anthropic-claude-api.md` cites `platform.claude.com` 103 times |

Spec SG-1 (`specification.md:183`) requires that "every entry MUST resolve
through a `research/…` file to an official documentation URL." For the 80
entries pointing at knowledge-maps and `core/`, **there is no upstream URL to
name** — these are the project's own derived artifacts, and `url == via` is
arguably the only honest encoding available. The spec simply has no vocabulary
for "grounded in our own synthesis," so authors reused the `url` slot.

For the remaining **28 entries pointing at `research/technologies/*.md`**, an
upstream URL genuinely exists and could be named (e.g.
`skills/structured-output-tool-calling/skill.yaml` cites
`research/technologies/anthropic-claude-api.md` as both `url` and `via`,
while its `SKILL.md` body cites nine distinct `platform.claude.com` and
`developers.openai.com` paths that never appear in the skill's own
`source_references`).

**Severity: Low.** No attribution is *lost* — the chain is fully traversable
one hop further, and the upstream URLs are present in the `via` file and in
`SOURCE_REGISTRY.md`. The defect is that the skill-level record is
self-referential, so an automated SG-1 validator reading only `skill.yaml`
would either pass these incorrectly or fail all 108.

**Root cause.** A spec-vocabulary gap. SG-1 was written assuming every skill
grounds in external docs; Layer-0/Layer-1 skills grounding in the project's
own architecture were authored later and had no correct field to use.

**Recommended correction.** Two parts. (1) Amend SG-1 to name the
internal-derivation case explicitly — e.g. permit `url` to be a repo-relative
path when `grounding: engineering-convention` or when the reference is to
`core/`/`knowledge-maps`, and require `url != via` otherwise. This legitimizes
80 entries by clarifying the rule rather than editing the data. (2) For the 28
`research/technologies/*` entries, populate `url` with the upstream
documentation URL the research file already records.

---

### LEG-03 — Three inline `[Source:]` markers resolve outside their skill's declared chain

**Finding.** A traversal of all 1,622 inline `[Source:]` markers in
`skills/*/SKILL.md`, resolving each cited host against both the skill's own
`source_references` and the full text of every `via` file it declares, found
**2 skills with 3 unresolvable hosts**:

- `skills/jest-vitest/SKILL.md` — `angular.dev` (line 142), `mongoosejs.com`
  (line 137)
- `skills/web-accessibility/SKILL.md` — `playwright.dev` (lines 89, 93, 190)

All three hosts **do** exist in the research corpus (in
`research/knowledge-maps/testing-knowledge-map.md`,
`security-knowledge-map.md`, `performance-knowledge-map.md`, and
`technology-decision-matrix.md`), but those files are not declared as `via`
for the relevant entries in these two skills. `jest-vitest:142` even names its
source in prose ("[Source: testing-knowledge-map.md §3; angular.dev per …]")
without a matching `source_references` entry.

For calibration: the same check across the other 84 skills resolves cleanly,
including every apparently-suspicious case I hand-verified (PostgreSQL,
structured-output-tool-calling, seo-optimization, observability). Earlier,
cruder passes of this check produced 26–40 false positives from `www.`
prefixes and deep-path fragments; those were eliminated by host
normalization, and the residual 3 are real.

**Severity: Low.** A traceability gap in 2 of 86 skills, where the underlying
source material demonstrably exists in-repo and only the declaration is
missing. No claim is unsupported; no attribution is stripped.

**Root cause.** Both are cross-domain citations — a testing skill reaching
into Angular/Mongoose material, an accessibility skill reaching into
Playwright material — where the author cited the knowledge map in prose but
did not add the corresponding `source_references` entry.

**Recommended correction.** Add the missing `source_references` entries:
`research/knowledge-maps/testing-knowledge-map.md` and
`research/technologies/mongoose.md` to `jest-vitest`;
`research/technologies/playwright.md` to `web-accessibility`.

---

### LEG-04 — `CHANGELOG.md` is stale to the point of misstating the deliverable

**Finding.** `CHANGELOG.md`'s most recent entry is `[0.1.0] - 2026-09-09`,
whose body reads: *"Initial repository scaffold… No skills, schemas, or
adapters implemented yet."* `[Unreleased]` is empty. `VERSION` reads `0.1.0`.

Since that entry, the project has added 86 skills, a 7-document orchestrator
architecture, a skill specification, 6 adapters with a shared projection
engine, a 16-scenario evaluation suite, and 23 audit documents — **none of it
recorded**. The file declares adherence to Keep a Changelog and SemVer;
neither is being honored.

I record this under provenance because a changelog *is* the record of what
changed when and under whose authority — the project's only
machine-independent change provenance outside git itself.

**Severity: Medium.** Also note: `README.md:15` states *"Status: Scaffold
only. No skills have been written yet."* — the repository's front door
misrepresents the project to any reader. That README finding almost certainly
also falls in another agent's documentation-completeness scope; I flag it here
only because I encountered it while verifying changelog provenance, and
because the two share one root cause and one fix.

**Root cause.** `README.md` and `CHANGELOG.md` were authored at scaffold time
(`1c294ee`) and no subsequent step's deliverable list included updating them.
This is the same class of omission as GIT-02 and CMT-01 — the build plan
tracked *creating* artifacts, not *maintaining* the root-level ones.

**Recommended correction.** Before release: populate `[Unreleased]` (or cut an
`0.2.0`/`1.0.0` entry) covering the taxonomy, specification, skills by domain,
orchestrator, adapters, and evaluation suite; bump `VERSION` accordingly; and
rewrite the README "Status" section. Coordinate with whichever agent owns
documentation completeness to avoid duplicate edits.

---

## Category 26 — Vendor neutrality

### The architecture holds. The promise is kept, with two real leaks and one dead payload.

The core promise — canonical `skills/` never encodes vendor-specific
behavior; that lives only in `adapters/` — is **structurally sound**, and the
mechanism is better than "discipline." `core/skill-specification/
specification.md:115` defines a single optional field, `adapter_hints`, as
the sanctioned quarantine for per-target data, with "Unknown-target keys are
ignored." `adapters/lib/skill_loader.py:41` classifies `adapter_hints` as
governance-only, and of the six adapters only `claude-code/adapter.py`
consumes it at all. Vendor specifics are therefore confined to one named,
optional, ignorable map rather than diffused through prose — which is exactly
the right design.

**Correctly distinguishing subject matter from capture.** The eight AI/LLM
domain skills (`agent-architecture`, `llm-application-engineering`,
`model-selection`, `prompt-context-engineering`,
`structured-output-tool-calling`, `llm-evaluation`, `rag-engineering`,
`ai-security`) contain 200+ Anthropic/OpenAI mentions. These are **not**
violations: they are the skills' subject matter, and critically they are
**balanced in pairs throughout** — every Anthropic claim is matched by the
OpenAI equivalent, with explicit reconciliation
(`prompt-context-engineering/SKILL.md:58`: "Anthropic's role framing ≈
OpenAI's Identity"; `agent-architecture/SKILL.md:89`: "Different vendor
vocabulary, same underlying axis"). `llm-application-engineering/skill.yaml:21`
even states the skill "is itself the vendor-neutral decision layer." This is
neutrality handled well, not neutrality violated.

Similarly, vendor names throughout `core/` (routing rules, taxonomy,
dependency graph, adapter-projection) are legitimate: `core/` documents the
projection boundary, and names all six/seven targets together rather than
privileging one. `shadcn-ui/skill.yaml:137`'s "MCP server (Claude Code/Cursor/
VS Code/Codex integration)" is the verbatim title of the upstream document —
legitimate attribution, and multi-vendor.

Three findings follow.

---

### VN-01 — `git-conventions` hardcodes `CLAUDE.md` as the agent-instruction file

**Finding.** `skills/git-conventions` — a Layer-2 convention skill whose
subject is git, not vendors — names `CLAUDE.md` as *the* agent-instruction
file to consult, **7 times**, with no neutral alternative offered:

| File | Line | Text |
|---|---|---|
| `SKILL.md` | 6 | "CONTRIBUTING/CLAUDE.md guidance, existing branch-name patterns" |
| `SKILL.md` | 36 | "or `CLAUDE.md` guidance; and existing branch-name patterns" |
| `SKILL.md` | 69 | "config, CONTRIBUTING/CLAUDE.md, and existing branch names, in that order" |
| `SKILL.md` | 84 | "CONTRIBUTING/CLAUDE.md guidance for an existing convention" |
| `skill.yaml` | 24, 45, 79 | same phrasing, including inside a `verification` assertion |

`SKILL.md` is the file projected verbatim into **every** target's output —
`skill.body` is copied as-is by all six adapters. So a Cursor, Codex,
Windsurf, Antigravity, or MCP user receives an instruction to look for a file
their ecosystem does not use. `AGENTS.md` — the emerging cross-vendor
convention, used by Codex among others — is never mentioned, nor are
`.cursorrules` or `.windsurfrules`.

This is the clearest vendor-neutrality violation in the library: canonical,
model-facing content, in a skill with no vendor subject matter, naming one
vendor's file format as the general case.

**Severity: Medium.** The guidance is not *wrong* — it degrades to "look for
convention docs" — but it measurably under-serves 5 of the 6 supported
targets, and it sits in the `verification` block (`skill.yaml:79`), meaning a
conformance check would assert against a Claude-specific artifact. It is
Medium rather than High because the surrounding instruction (read `git log`,
read commitlint config, read existing branch names) is genuinely
vendor-neutral and carries most of the value.

**Root cause.** `git-conventions` was authored in Step 12
(`a23ba8d`, `skills/conv-infra-git-ci-domain`), well before the adapter layer
(Step 31) made the six-target commitment concrete. At authoring time the
working assumption was a Claude-hosted agent.

**Recommended correction.** Replace all 7 occurrences with neutral phrasing
that names the class and gives examples, e.g.: *"repository-level agent
instruction files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.windsurfrules`,
or equivalent)"*. This preserves the method exactly while removing the vendor
tilt. Check `skills/git-workflow` for the same phrasing at the same time.

---

### VN-02 — `playwright` names Claude Code as the exemplar MCP host

**Finding.** `skills/playwright/SKILL.md:290` and
`skills/playwright/skill.yaml:80` both read "MCP (accessibility-tree-based
browser control, e.g. on Claude Code) for driving the browser." MCP is an
open, cross-vendor protocol; singling out one host as the example inside
canonical content tilts otherwise-neutral material.

Related but **correct** by contrast:
`core/skill-specification/specification.md:82` uses
`browser: "advise-only; or Playwright-via-MCP on Claude Code"` as a
`capability_fallbacks` example, and
`core/dependency-architecture/dependency-graph.md:140` names both Claude Code
and Windsurf as hosts lacking native browser automation. Those are in
`core/`, are factual capability statements, and name multiple vendors — they
are fine.

**Severity: Low.** An illustrative "e.g." that a reader on another host will
correctly generalize. Impact is aesthetic tilt, not broken guidance.

**Root cause.** Authored in the QA domain batch (`66a0d35`) before the
six-target commitment.

**Recommended correction.** "…e.g. via an MCP browser server, where the host
provides one." Drop the vendor name; the capability statement survives
intact.

---

### VN-03 — 34 skills carry `adapter_hints.vscode` for a target that has no adapter

**Finding.** `adapter_hints` target-key distribution across the 86
`skill.yaml` files:

| Target key | Skills | Adapter exists? |
|---|---|---|
| `vscode` | 34 | **No** — there is no `adapters/vscode/` |
| `claude-code` | 34 | Yes |
| `cursor` | 28 | Yes |
| `codex`, `windsurf`, `antigravity`, `mcp` | **0** | Yes (all four) |

Two distinct problems. First, **34 skills carry vendor-specific payload
(`vscode.argument_hint`) that nothing in the repository consumes** —
`TARGETS` in `adapters/tests/test_compatibility.py:38` is the six real
targets, and `vscode` is not among them. Per the spec's own "unknown-target
keys are ignored," these 34 blocks are inert data sitting in canonical files.

Second, the coverage is **skewed to two vendors**: the four supported targets
that receive zero hints (`codex`, `windsurf`, `antigravity`, `mcp`) are
projected with no per-target tuning, while `claude-code` and `cursor` get it
in 34 and 28 skills respectively. Whether that asymmetry is justified (those
two may be the only targets with tunable knobs) or is simply where attention
went, it is not documented anywhere.

Compounding: `README.md:7` and
`core/skill-specification/README.md:10` both advertise **VS Code agents** as
a supported target, and `adapter-projection.md:51` includes a VS Code column
in the mapping matrix — but no adapter implements it. So either the adapter
is a genuine coverage gap against a publicly-advertised promise, or the VS
Code hints and column are stale and the promise should be withdrawn.

**Severity: Medium.** Not a neutrality *violation* in the strict sense — the
data is quarantined in the sanctioned field exactly as designed — but it is a
real inconsistency between the canonical layer, the adapter layer, and the
public README, and it puts unconsumed vendor-named data in 40% of the
library's canonical files.

**Root cause.** VS Code was in the target list at specification time (Step 7,
`94e2349`) and the hints were authored alongside skills from Step 9 onward.
Step 31 scoped the adapter build to six targets and did not reconcile
backward against the already-authored hints or the README's claim.

**Recommended correction.** A product decision for the user, framed as
either/or: **(a)** implement `adapters/vscode/` — the hints already exist for
34 skills, so the marginal cost is one adapter module; or **(b)** drop VS Code
from `README.md:7`, `core/skill-specification/README.md:10`, and the
`adapter-projection.md` matrix, and remove the 34 `vscode` hint blocks.
Either resolves it; leaving all three artifacts disagreeing does not.
Separately, document in `adapter-projection.md` why `codex`/`windsurf`/
`antigravity`/`mcp` need no hints, so their absence reads as deliberate.

---

### VN-04 — Recorded strength: the quarantine mechanism is sound (no action)

Recorded so a future reviewer does not mistake the 34 `claude-code:` keys in
`skills/*/skill.yaml` for a neutrality breach. They are spec-sanctioned
(`specification.md:115`), classified as governance-only by the loader
(`skill_loader.py:41`), consumed by exactly one adapter, and ignorable by
construction. The design correctly chose *one named quarantine field* over
*prose discipline*, which is why the rest of the canonical layer scans as
clean as it does. **No finding; no correction.**

---

## Explicit verification checklist results

All six items executed mechanically over the whole repository. `research/` is
excluded from branding checks where noted — its vendor mentions are
legitimate technology documentation and are expected.

### 1. No unnecessary AI branding anywhere (skill content, core docs, adapter code, commit messages, branch names)

**Result: one violation (GIT-01); otherwise clean.**

- **Commit messages:** `git log --all --format="%H %s%n%b" | grep -i
  "co-author\|generated with\|🤖\|claude code\|noreply@anthropic"` → **exactly
  1 hit**, `31e3438`'s `Co-Authored-By` trailer. No `🤖`, no "Generated with",
  anywhere in history.
- **Branch names:** all 33 local and 32 remote names reviewed individually.
  Zero AI/tool/model names. `research/ai-llm` refers to the AI/LLM *knowledge
  domain* (Step 24's research target), not to the authoring tool — correct.
- **Adapter code:** zero AI-branding strings across all 11 Python files.
- **Assistant-register leakage:** grep for `^(Certainly|Sure[,!]|Great
  question|I'll help|Let me help|Here's a comprehensive|I hope this helps|Feel
  free to)` across `skills/`, `core/`, `adapters/`, `evaluations/`,
  `README.md`, `CHANGELOG.md` → **zero hits**. Grep for `as an AI|as a
  language model|I'm an AI|my training data|knowledge cutoff` → **zero hits**.
  The prose register throughout is technical-document, not chat transcript.
- **Skill content:** vendor mentions in `skills/` were individually
  classified. All Anthropic/OpenAI mentions fall in the eight AI-domain skills
  where they are balanced subject matter (see Category 26). The two residual
  tilts are VN-01 and VN-02.

### 2. No AI/LLM fingerprints in branch names or commits

**Result: GIT-01, plus one weak stylistic residue.**

Beyond the `Co-Authored-By` trailer: `git log --all --format="%h %s" | grep
"—"` returns 2 commits (`0396a04`, `adf416a`) using an em-dash as a subject
separator — a recognized LLM stylistic tell, though also ordinary human
punctuation. Recorded as GIT-06, Low, fix-forward only.

Author/committer identity is uniform and human across all 33 commits:
`git log --all --format="%an <%ae> | %cn <%ce>" | sort -u` → a single line,
`Keval Gor <kevalgor12@gmail.com>`. No AI identity appears in any author,
committer, or trailer field except GIT-01.

### 3. No unnecessary AI branding in comments

**Result: clean. Zero hits.**

No `Generated by`, `Co-Authored`, `🤖`, or model name appears in any code
comment, YAML comment, or HTML comment across `skills/`, `core/`,
`adapters/`, `evaluations/`. Emoji sweep across those four trees returns only
`⛔` (45×, a semantic non-activation marker in routing/dependency tables) and
`⚠` (2×) — both functional, neither decorative.

This item is worth calling out as a genuine pass: the project ships a
`code-commenting` skill that names "AI/tool signatures or attribution embedded
in code comments" as an anti-pattern, and the codebase contains zero
instances of it.

### 4. No removal of legitimate attribution or provenance

**Result: clean. Nothing was stripped.**

- 854/854 `source_references` entries structurally complete (all four keys,
  all `via` paths resolve on disk, `last_verified` present) — **0 defects**.
- All 57 distinct `research/…` paths cited from `skills/` resolve.
- All 6 distinct `audits/…` paths cited across the repo resolve.
- Diffed all six post-authoring commits that touched skill files for removed
  provenance lines: **one hit**, and it is a reflow that preserves the
  `[Source: docs.github.com/en/actions]` attribution verbatim in the
  replacement line.
- Step 28's claimed 20 edited files verified as exactly 20; all retain
  complete provenance.
- The 3 skills without `source_references` are `grounding:
  engineering-convention` and are exempt under SG-4 — not stripped.

The residual findings (LEG-02, LEG-03) are *declaration-shape* gaps where the
underlying source demonstrably exists in-repo, not lost attribution.

### 5. No unnecessary Phase/Step comments in code/skill content (`audits/` legitimately exempt)

**Result: 12 violations across 6 files — four times the pre-reported scope.**

Full inventory in CMT-01 (`adapters/README.md` ×4,
`adapters/lib/skill_loader.py` ×2, `adapters/tests/test_compatibility.py` ×3,
`evaluations/README.md`, `evaluations/evaluation-spec.md` ×2,
`evaluations/regression-suite.md`), plus 6 build-batch narration comments in
`skills/*/skill.yaml` (CMT-02).

Correctly **excluded** as legitimate, not violations:

- All `Phase 0–6` references in `core/routing-architecture/*` and
  `core/orchestrator/lifecycle.md` — these are the **routing algorithm's own
  named phases**, a published domain concept, not build-process narration.
  Same for `Phase-0 scan` references throughout `evaluations/`.
- "decision-framework step N" references throughout `skills/` and
  `evaluations/expected-behaviors/` — these cite a skill's own numbered
  decision framework.
- All Step references inside `audits/` — explicitly exempt.

### 6. Comments explain WHY rather than restating code

**Result: clean, and above bar.** 21 files sampled across `adapters/lib/`
(4), `adapters/*/adapter.py` (6), `adapters/tests/`, 8 `skills/*/skill.yaml`
spanning six domains, and 2 governing documents.

- Zero decorative banners (`#####`/`=====`/`-----`/`/*****`) repo-wide.
- Zero genuine `// Step 1:` / `// Now we loop over…` narration. All 4
  occurrences are the anti-pattern being *quoted* by the documents that
  forbid it.
- Comments consistently cite the constraint they enforce (lossiness contract
  L-1…L-4, spec §2.5, `adapter-projection.md`) rather than describing the
  adjacent line. Representative evidence is quoted in Category 22.
- The highest-value pattern in the codebase — comments explaining why a field
  is *deliberately empty* — appears consistently across `skill.yaml` files.

Only defect found: a one-character typo, `skill_loader.py:12` "a implicit" →
"an implicit" (Low).

---

## Release-readiness contribution

Across these four categories the library is in good shape, and in two of them
it is genuinely strong. Provenance is the standout: 854 source references
with zero structural defects, every research and audit path resolving, a
1,748-line `SOURCE_REGISTRY.md`, conservative quotation in the canonical layer
(no quoted span in any `SKILL.md` reaches 80 characters), and — the specific
question this audit was asked — **verified proof that the Step 27–32 edit
passes stripped no attribution whatsoever**, with the single altered
`[Source:]` line shown to be a reflow that preserved its citation verbatim.
Comment-policy compliance is likewise a real pass rather than an absence of
failure: the project ships a skill forbidding AI signatures, step narration,
and banner comments in code, and its own codebase contains zero instances of
all three, with comments that cite the contract clause they enforce. Vendor
neutrality's core architectural promise holds, and holds for the right reason
— it is enforced by a single named quarantine field that only one of six
adapters even reads, not by authorial discipline.

**Nothing here blocks release.** There are no Blocker and no Critical
findings, and a single High. That High — GIT-01 — is also the single most
significant finding: an AI co-author trailer sitting in six published
`origin/*` refs, in the one commit of thirty-three that a delegated agent
produced outside the project's human hand-off workflow. Its significance is
not its size — it is one line — but what it proves: the Step 27 audit caught
the unauthorized `git commit`, remediated the branch name, and still missed
the message body, which is exactly the kind of gap only a dedicated history
audit finds. It must not be fixed autonomously; rewriting six published refs
is a destructive operation requiring an explicit user decision, and the
cheapest real remedy may simply be squash-merging to `main` so the trailer
never reaches the release branch. Running it close behind, by aggregate
weight rather than individual severity, is the cluster of stale root-level
artifacts — GIT-05's untouched `main`, plus LEG-04's changelog and README
both still announcing a scaffold that has not existed for 32 commits.

The Medium findings share one root cause worth naming plainly: **the build
plan tracked creating artifacts, not maintaining the root-level ones.**
GIT-02's missing `CONTRIBUTING.md`, GIT-03's SHA-less audit trail, CMT-01's
build-step references in shipped READMEs, LEG-01's absent `NOTICE`, LEG-04's
frozen changelog, and VN-03's VS Code promise that no adapter keeps are all
the same omission in different places — nobody owned the repository's edges.
That is a genuinely cheap cluster to close: five short files and a handful of
line edits, no architectural change, and it is the difference between a
repository that reads as a finished product and one that reads as an
in-progress build. VN-01 (`CLAUDE.md` hardcoded in `git-conventions`) is the
one finding that touches shipped, model-facing behavior on five of six
supported targets, and it is a seven-occurrence phrasing change.

My recommendation for Step 34: treat VN-01 and CMT-01 as the substantive
content fixes, treat the root-level artifact cluster as one batched
housekeeping task, and escalate GIT-01 and GIT-05 to the user as a single
paired decision about how `main` gets brought current — because the answer to
the second one largely determines the cost of the first.
