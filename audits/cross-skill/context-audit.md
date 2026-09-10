# Context-Loading Audit (Step 29)

Companion to [`cross-skill-audit.md`](cross-skill-audit.md). Covers check 8:
skills or clusters whose combined `related_skills` fan-out or body size
would load an unreasonable amount of context for a routine task — and,
more importantly, whether the lazy-loading model in
`core/routing-architecture/README.md` actually keeps that in check *in
practice* or only in theory.

Token figures are `bytes / 4`, the standard rough estimate. They are for
comparing magnitudes, not for budgeting.

---

## The corpus, measured

| Tier | What | Size | ≈ tokens |
|---|---|---|---|
| **Tier 0** | all 86 `name` + `description`, always available for selection | 37.4 KB | **~9,600** |
| **Tier 1** | all 86 `SKILL.md` bodies | 1,292 KB | ~330,700 |
| **Tier 2** | 28 files under `references/` across 26 skills | 132 KB | ~33,800 |

Body sizes: mean 277 lines, median 278, max 472 (`redis`), min 129
(`project-management`). **All 86 are under CE-2's ~500-line ceiling**, with
`redis` (472), `react` (433), `opentelemetry` (412), and `angular` (408)
closest to it. No skill needs splitting on size grounds.

Tier-2 discipline is good and conservative: 30 skills carry a Tier-2
directory, holding 28 files in total — nearly all of them a single
`references/` file per skill, largest 8.5 KB (`mongoose`) — and none is
auto-loaded. Fifty-six skills have no Tier-2 at all, which is the right
answer when there is no long tail, per CE-4.

---

## C-01 · `related_skills` exists in every skill and in no routing rule — Medium

**The one place the lazy-loading model is genuinely unspecified.**

`core/routing-architecture/` — README, routing-algorithm, rules, examples —
mentions `related_skills` **zero times** across all four files. The spec
(§2.5) defines it as "Commonly composed-with, not a hard dependency"; the
dependency architecture types it as a symmetric *complementary* edge. But
the context-selection rules cover Tier-0 (CS-1), bodies (CS-2),
`required_context` (CS-3), `optional_context` (CS-4), Tier-2 (CS-5), the
repo scan (CS-6), reloading (CS-7), and signal cost (CS-8) — and never say
what a router should do when a selected skill lists seven others as
related.

The field is a plausible attractor for exactly the behavior the
architecture is built to prevent. If "related" were read as "also load":

| Skill | related | Body + all related bodies | ≈ tokens |
|---|---|---|---|
| `llm-application-engineering` | 8 | 142 KB | ~36,400 |
| `styling-systems` | 7 | 130 KB | ~33,200 |
| `database-operations` | 7 | 125 KB | ~31,900 |
| `observability` | 6 | 113 KB | ~28,900 |
| `containerization` | 5 | 105 KB | ~26,900 |
| `testing-strategy` | 6 | 91 KB | ~23,200 |

~36K tokens to answer "should this feature use RAG?" would be an outright
failure of the design's stated economy.

**It almost certainly will not happen**, because SR-1 (default-deny) and
CS-2 (bodies load when their stage runs) both argue against it, and
`SK-AI-001`'s own description says it "composes SK-AI-002–008
**selectively**". The intent is unambiguous. But the guarantee currently
rests on inference from two other rules rather than on a rule about this
field — and every one of these hubs lists its *own specializations* as
related, which is precisely the set an over-eager reader would pull in.

Note also that the fan-out itself is **not** the problem and should not be
reduced: `styling-systems` listing its five styling technologies and
`observability` listing its four observability technologies is an
honest table of contents for a Layer-3 hub. Trimming these lists to make a
number smaller would destroy real information to fix a rule gap.

**Recommendation:** add one context-selection rule.

> **CS-9 · `related_skills` is an affinity hint, not a load list.** A
> skill's `related_skills` are evaluated by the normal default-deny
> selection rules on their own merits. Being listed as related is never by
> itself a reason to select a skill or load its body.

One sentence. It is the highest value-per-word change in this entire
audit, and it is the only reason check 8 is not a clean pass.

---

## C-02 · Tier-0 selection cost is real and its scaling ceiling is undocumented — Low

Operating principle 1 says "Route on metadata, not bodies… This is the
context-efficiency backbone: **selection is cheap**." At 86 skills,
selection costs **~9,600 tokens** of always-resident Tier-0 metadata
before the router has made a single decision, plus the router's own body
(~5.5 KB, ~1,400 tokens — and `self-review.md` R-6 already notes that even
SR-7's self-suppression cannot avoid this, since the router's body is
loaded by the time it decides).

That is fine today — roughly 5% of a 200K window — and "cheap" is a fair
description. The finding is that the cost is **linear in library size and
nowhere stated**:

| Library size | Tier-0 cost, extrapolating at the current mean of ~445 chars/skill |
|---|---|
| 86 (today) | ~9,600 tokens |
| 120 | ~13,400 |
| 200 | ~22,300 |
| 300 | ~33,400 |

The taxonomy already anticipates growth (four tracked research gaps, each
implying new skills; `taxonomy-analysis.md` open decision 2 explicitly
asks whether ~69 skills is too many to maintain). At ~200 skills, routing
overhead alone approaches the cost of the entire "fix this query" worked
example.

CE-1 caps `description` at 500 chars, which bounds the per-skill cost —
and the corpus is well inside it, so there is no violation. But nothing
bounds the *aggregate*, and no document names a size at which flat Tier-0
selection stops being the right mechanism (hierarchical routing by domain,
or a two-stage router, being the usual answers).

**Recommendation:** record the number and the ceiling in
`routing-architecture/README.md` alongside operating principle 1 — "at N
skills, Tier-0 selection costs ~X tokens; above roughly Y, selection
should become hierarchical." Documentation, not redesign. Low severity
because the current figure is genuinely fine.

---

## C-03 · Does the model hold in practice? Three worked routings, costed *(positive)*

Taking the routing architecture's own examples and pricing the Tier-1
bodies each would load:

| Example | Skills selected | Tier-1 loaded | ≈ tokens | Verdict |
|---|---|---|---|---|
| Ex. 1 — "Fix this PostgreSQL query" | 4 (`capability-adapter`, `performance-engineering`, `postgresql`, `code-review` perf facet) | 53 KB | ~13,500 | **Proportionate.** 4% of the corpus for a scoped fix. `postgresql` alone is 24 KB of it — a technology skill earning its keep. |
| Ex. 7 — "Set up CI to run tests on push" | 4 | 61 KB | ~15,700 | **Proportionate**, though `testing-strategy`'s body loads to decide "what to gate on" — arguably more than the task needs. |
| Ex. 2 — "Build a realtime multiplayer browser game" | 27 (incl. conventions + orchestration) | 328 KB | ~84,000 | **Large but defensible.** It is a whole-project task spanning 8 domains, and CS-2 means those 27 bodies load *across the run's stages*, never simultaneously. |
| Ex. 3 — "Add a comment explaining this function" | 1 (`code-commenting`) | 6 KB | ~1,500 | **Excellent.** The low end works. |

Two observations:

- **The stage-scoped loading in CS-2 is what makes Ex. 2 acceptable.** If
  all 27 bodies loaded at routing time it would be ~84K tokens before any
  work; because they load per stage, peak concurrent load is a handful of
  skills. The mechanism is correct, and it is the reason the answer to
  check 8 is "no explosion."
- **The floor is ~9,600 + the router's body,** so even Ex. 3 pays ~11K
  tokens of overhead to load a 1.5K-token skill. SR-7's self-suppression
  reduces *downstream* cost only. This is the R-6 concern from the
  orchestrator self-review, now quantified: **for trivial tasks,
  orchestration overhead is roughly 7× the useful payload.** Not a defect
  — some fixed cost is unavoidable for model-triggered selection — but
  worth having a number attached to it.

## C-04 · No skill or cluster carries disproportionate weight for its scope *(positive)*

Checking the specific concern the master plan names — skills whose body
size is out of proportion to their actual task scope:

- **The largest bodies are all Layer-4 technology skills** (`redis` 472
  lines, `react` 433, `opentelemetry` 412, `angular` 408, `github-actions`
  382). That is the correct place for length: they hold version-sensitive,
  citation-dense material (`redis` alone carries 5 `owned_knowledge`
  topics and one of the densest `[Source:]` markings in the corpus), and they only
  load when their technology is detected (SR-3). A long body behind a
  narrow detection gate is cheap.
- **The generic skills that load most often are the shortest.**
  `code-commenting` (178 lines), `code-quality` (180), `code-review`
  (179), `git-conventions` (174), `refactoring` (169) — the five Layer-2
  conventions that attach to nearly every code task — rank 4th, 7th, 9th,
  10th and 11th **smallest** of all 86. Whether by design or good instinct, the cost
  profile is inverted in exactly the right direction: **frequently-loaded
  skills are small; large skills are rarely loaded.**
- **Layer 1 discovery skills** (`project-management` 129,
  `technical-planning` 162, `requirements-engineering` 169,
  `solution-architecture` 205) are also small, which matters because SR-8
  engages them on any non-trivial project.
- **No cluster compounds.** The densest realistic co-activation is the
  database cluster on a data task: `database-operations` (209) +
  `postgresql` (326) + `data-modeling` (205) ≈ 740 lines / ~19K tokens.
  The frontend cluster (`frontend-architecture` 187 + `react` 433 +
  `styling-systems` 229 + `tailwindcss` 383) ≈ 1,232 lines / ~30K tokens,
  and SR-4's conflict resolution guarantees only one framework and one
  styling tool from each cluster ever co-activate.

No split is recommended on context-cost grounds.

---

## Summary

| ID | Finding | Severity | Recommendation |
|---|---|---|---|
| C-01 | `related_skills` appears in every skill and in **zero** routing rules; worst case reads as ~36K tokens of bodies | Medium | Add **CS-9** (one sentence). Do not trim the lists. |
| C-02 | Tier-0 selection costs ~9,600 tokens and scales linearly with no documented ceiling | Low | Record the number and the threshold in the routing README |
| C-03 | Lazy stage-scoped loading holds on all four worked examples | *positive* | — |
| C-04 | Cost profile is correctly inverted: frequent skills small, large skills detection-gated | *positive* | — |

**Verdict on the question the plan actually asks** — does the default-deny,
lazy-loading model keep context in check *in practice* or only in theory?

**In practice, with one specification hole.** The measured profile is
genuinely good and not accidental: CE-2 is respected by all 86 skills,
Tier-2 is small and never auto-loaded, technology skills are
detection-gated, and the skills that load most often are the smallest in
the library. The three worked routings cost what they should. The single
hole is that the one field capable of causing an explosion —
`related_skills` — is the one field the routing architecture never
mentions, so the model's success there currently depends on a reader
inferring the right behavior from two adjacent rules rather than reading
it.
