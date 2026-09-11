# Final Principal-Engineer Audit

Date: 2026-09-11. Scope: the entire AI Coding-Agent Skill Library, all 26
categories named in the master plan, assuming this library will be used
in serious production software engineering. This is **Step 33**, model
Opus 5 / Max — the final gate before corrections (Step 34) are implemented.

This document is the required single deliverable
(`audits/final-principal-engineer-audit.md`). It synthesizes 5 detailed
category-cluster reports (6,164 lines combined) produced by 5 parallel
Opus agents, plus independent verification performed directly by this
session. The 5 detailed reports live at
[`audits/final-principal-engineer-audit/`](final-principal-engineer-audit/)
and are the evidentiary backing for every claim below — this document
deduplicates, cross-checks, and renders a verdict; it does not repeat
their full evidence inline.

| Report | Categories | Findings |
|---|---|---|
| [`architecture-taxonomy-spec-deps-routing-activation.md`](final-principal-engineer-audit/architecture-taxonomy-spec-deps-routing-activation.md) | 1–6 | 32 |
| [`context-quality-techaccuracy-versions-docs.md`](final-principal-engineer-audit/context-quality-techaccuracy-versions-docs.md) | 7–10, 15 | 31 |
| [`security-testing-performance-observability-failurerecovery-approval.md`](final-principal-engineer-audit/security-testing-performance-observability-failurerecovery-approval.md) | 11–14, 19–20 | 27 |
| [`adapters-evalsuite-realworldeval-maintainability-extensibility.md`](final-principal-engineer-audit/adapters-evalsuite-realworldeval-maintainability-extensibility.md) | 16–18, 24–25 | 24 |
| [`git-comments-legal-vendorneutrality.md`](final-principal-engineer-audit/git-comments-legal-vendorneutrality.md) | 21–23, 26 | 16 |

**Raw combined total: 130 findings** (1 Blocker · 14 Critical · 37 High ·
48 Medium · 30 Low), before deduplication. Several of the most severe
findings were reported independently by 2–3 of the 5 clusters from
different angles — Part 2 below consolidates those into single entries so
the same underlying defect isn't counted or fixed twice.

## Process note (disclosed, not hidden)

Two process events during this step, recorded here because a final
principal-engineer audit that hid its own process defects would
contradict the standard it's applying to the library:

1. **Two of the 5 agents stalled mid-run with zero output** (a session
   interruption, not a content failure — their transcripts stopped
   growing at the identical millisecond the other 3 finished, then never
   resumed). Caught by the user questioning the lack of progress, not by
   this session's own monitoring. Both were cleanly retried from scratch
   (no partial file existed to preserve) and completed normally on retry.
2. **One agent (security/testing/performance cluster) ran `git status --short`**,
   one command outside its "no git commands" brief. It self-disclosed
   this unprompted in its completion report. The command is read-only and
   mutated nothing (confirmed: it was used only to verify the working
   tree had no unexpected changes). Recorded here for completeness, not
   treated as a finding against the library itself.

## Explicit verification checklist (master plan requirement)

| Item | Result |
|---|---|
| No unnecessary AI branding | **1 violation** — commit `31e3438`'s body carries a `Co-Authored-By: Claude Sonnet 5` trailer (GIT-01, High — see Part 2). Elsewhere clean: no AI branding in skill/core/adapter content; the AI-generated-content mentions in `code-commenting` and `seo-optimization` are confirmed legitimate subject matter (those skills are *about* AI-generated-content anti-patterns), not branding. |
| No AI/LLM fingerprints in branch names or commits | **Clean** except the one commit above. All 32 branch names (local + remote) are vendor-neutral and descriptive. |
| No unnecessary AI branding in comments | **Clean.** Zero banners, zero AI signatures found across sampled `core/`, `adapters/`, and skill files. |
| No removal of legitimate attribution or provenance | **Clean.** 854/854 `source_references` entries structurally valid; all resolve to real `research/` content; diffing every post-authoring edit commit found exactly one removed `[Source:]` line, verified as a reflow that preserved the citation verbatim. |
| No unnecessary Phase/Step comments | **Confirmed, larger than my own pre-check found.** My own mechanical grep before dispatch found 3 sites; the adapters-cluster report found the true count is **12 sites across 6 files**, including the opening paragraph of `adapters/README.md` — a shipped component doc that frames itself by this project's internal step number rather than describing what it does (GIT-05/DOC-05, Low-to-Medium — see Part 2). |
| Comments explain WHY rather than restating code | **Passes.** Sampled 15–20 files across `core/`, `adapters/`, and skill domains; no WHAT-only comments found. The only `// Step 1:`-style narration comments in the entire corpus are inside `code-commenting`'s own body, quoted there as the documented anti-pattern. |

## Part 1 — Deduplicated release-blocking findings

These are the findings that either (a) were independently found by 2 or
more of the 5 clusters — the strongest form of evidence this process
produces — or (b) were confirmed by direct re-verification in this
session to have a proven real-world bad outcome via Step 32. Each is
listed once, with every report that found it credited.

### BLOCKER

**B-1 · The repository's default branch (`main`) presents as an empty,
unbuilt scaffold.** `main` is 32 commits behind every feature branch; its
`README.md` still reads *"Status: Scaffold only. No skills have been
written yet."* Anyone cloning the repo at its default branch — which is
the normal way to evaluate a project — sees no evidence the library
exists. Found independently by the git-conventions cluster (as a
process/hygiene observation) and the context/quality cluster (DOC-N1,
rated Blocker on the grounds that a library which cannot be found by a
normal clone is not a library that can be evaluated, let alone shipped).
*Root cause:* every step in this project's 33-step build history has
worked on a feature branch and stopped at "ready for you to push" —
nothing in the process ever merges back to `main`. *Correction:* merge
(or fast-forward, since history is fully linear with zero merge commits)
the accumulated work into `main` before any release claim is made. This
is a git operation with real blast radius (rewriting the default branch
everyone else's clone tracks) — **requires explicit user decision**, not
an autonomous fix.

### CRITICAL

**C-1 · Ten authored skills are falsely marked "not yet authored" across
roughly 50 citation sites in 25+ skill files, in the exact metadata field
the router treats as authoritative for exclusion.** Independently
verified directly by this session (see below) and found by 3 of the 5
clusters from different angles (architecture cluster's AC-1; context/
quality cluster's CE-N1; adapters cluster's cross-reference to the same
pattern). Direct verification in this session confirmed the precise
scope: `authentication-authorization`, `ci-cd-pipeline`,
`database-operations`, `legacy-modernization`, `realtime-communication`,
`security-engineering`, `seo-optimization`, `styling-systems`,
`technical-documentation`, and `ui-ux-design` all exist as fully authored
skills, yet are still described as "not yet authored" in `parents`
comments, `non_activation_conditions`, and body prose across dozens of
sibling skills (e.g. `data-modeling/skill.yaml:34`, `docker/skill.yaml:44`,
`mui/skill.yaml:44-45`, `frontend-architecture/skill.yaml:33`, and ~45
more sites). This is the field `skill-router`'s SR-2 and CS-1 treat as
decisive, and the lifecycle/failure-handling rules explicitly instruct
the router to degrade away from any skill marked this way — so a
well-formed router reliably routes *away* from skills that actually
exist. **This is not hypothetical**: Step 32's Critical finding M-06 (the
live-auction stress test) traced a concrete bad outcome — a bid handler
shipped with no isolation level or row lock — directly to one of these
ten lines (`data-modeling/skill.yaml:34`). *Root cause:* no mechanical
validator exists to catch a stale forward-reference once its target ships
(see C-3). *Correction:* a scripted find-replace removing the false
qualifier from all ~50 sites — the architecture cluster estimated this at
"deleting four words from ten lines" per distinct skill name, i.e. a
half-day mechanical fix with no design risk, not a redesign.

**C-2 · The gate/risk taxonomy is defined entirely over actions being
performed, never over policies that authorize a future bypass of a
control — confirmed as a single shared defect underlying at least 4
independently-found findings across 2 steps.** Step 32 found this 3
times from 3 different tasks (`git-conflicting-conventions.md`'s G-9,
`security-session-storage.md`'s F3.3, and a third occurrence recorded as
P-5). Step 33's security/testing/performance cluster re-derived it
independently as GATE-1 and traced it through 10 separate library
controls — the risk-class vocabulary, admission rules D3/D13, ER-2
gating, all 5 gate classes, the gate lifecycle's arming condition, GA-8,
all 5 S-Gates, and FV-7/FV-9 — showing it is one wrong premise repeated
ten times, not ten separate defects. Independently confirmed by this
session: all 5 gate classes (`G-DESTRUCTIVE`, `G-OUTWARD`, `G-PRODUCTION`,
`G-COMMITMENT`, `G-COST` — `core/orchestrator/failure-recovery-and-escalation.md:146-150`)
are triggered by an action happening now (a `DROP`, a force-push, a
deploy, a cost-incurring call) — none are triggered by *authoring a
policy that will let a future action skip a gate*. A request like "allow
force-push to main for hotfixes" doesn't itself drop, push, deploy, post,
or cost anything at authoring time, so it trips no gate — the bypass is
pre-approved before the action it protects against ever occurs.
*Correction:* the security cluster's own assessment is the right one to
defer to here — it warns that G-9's originally proposed `G-POLICY` fix
closes only about a third of the gap, since the same blind spot recurs
independently in the risk vocabulary, D3/D13 admission, and FV-7/FV-9;
Step 34 should treat this as one taxonomy-level fix (gate on "does this
authorize a future ungated action," not only "is this action itself
gated"), not four separate patches.

**C-3 · No mechanical validator exists, despite the specification
requiring one as a precondition for shipping.** `core/skill-specification/`'s
own spec makes a `[V]`-tagged mechanical validation pass a stated
precondition for projection and `final/` promotion (27 `[V]` rules are
defined), but no such validator exists anywhere in the repository — the
only executable code in the project is the adapter layer, which checks
projection fidelity, not authoring-time correctness. This is the
structural reason C-1 and the VR-3 gap (C-4) survived five prior review
rounds (Steps 27, 28, 29, 31, 32) without being mechanically caught —
every prior catch was a human/agent reading skills closely, not a script
that runs on every commit. Found by the architecture cluster (S-1) and
corroborated by the adapters cluster's independent observation that "the
only Python in the repo is the 11-file adapter layer." *Correction:* Step
34 should treat writing this validator as the highest-leverage single
piece of work in the whole correction pass — it would have caught C-1 and
C-4 automatically and prevents their recurrence, rather than requiring a
sixth manual audit round to catch a seventh instance.

**C-4 · Nine sites reference three skill IDs that do not exist**
(`SK-FE-005` ×7, `SK-GROW-002`, `SK-TECH-graphql`), 5 of them in the
`parents` field of React, Next.js, Vue, Nuxt, and Angular — breaking the
taxonomy hierarchy for five flagship technology skills. First found at
Step 28 (titled there "the single most significant cross-cutting
finding") and deferred at every step since (29, 30, 31, 32). Independently
re-confirmed by 3 of the 5 Step-33 clusters (architecture cluster's DG-1,
context/quality cluster, adapters cluster's M24-3/M24-2) and directly
verified in this session (`rendering-strategy` does not exist as a
directory; `styling-systems`, `ui-ux-design`, etc. do — see C-1's
verification). Distinct from C-1: C-1 is false-negative staleness
(claiming something doesn't exist when it does); C-4 is the mirror case
(referencing something that genuinely doesn't exist, as if it did) —
running C-1's fix in reverse would not resolve this one. *Correction:*
`SK-GROW-002` and `SK-TECH-graphql` references need either authoring the
missing skill or removing the reference; `SK-FE-005` (rendering-strategy)
is worse — `taxonomy-analysis.md:121` makes it a *mandated* split target,
so removing the reference isn't available; it must be authored. This
should be scoped as new content work in Step 34's plan, not a mechanical
fix like C-1.

**C-5 · IC-6's "never claim untested work passed" downgrade is
structurally inert for effectively all Tier B/C skills.** First found at
Step 32 (F2.1: "3 of 52"). Step 33's security cluster re-verified under a
stricter, more defensible criterion (an item only counts if its
*execution*, not just its presence, depends on the capability) and found
the true count is **0 of 52** — all three previously-credited items have
disjunctive escapes that let them be satisfied without ever running
anything. This means Step 32's own regression-test priority (its proposed
`VR-9` rule) was calibrated against a too-generous baseline and should be
recalibrated to "0 of 52," which is a stronger, not weaker, case for
prioritizing the fix. *Correction:* as Step 32 recommended — add `VR-9`
(a Tier B/C skill must declare at least one execution-dependent
`verification` item) — now confirmed as addressing 100% of the affected
population, not 94%.

### Other convergent High findings worth naming at this level

- **The mechanical-validator gap (C-3) also explains why 13 list items
  across 12 skills silently parse as YAML *mappings* instead of strings**
  (4 verification items, 1 escalation entry, 3 shell-degradation clauses)
  — every prior "YAML parses" check passed because none checked item
  *types*. Found only by the security/testing cluster; flagged here
  because it's the same root cause as C-3, discovered independently.
- **F3.1 (Step 32) reconfirmed exactly** — the localStorage-vs-httpOnly-cookie
  decision in a session-storage security fix is still owned by no skill,
  and `security-engineering` is still excluded from that task class by
  its own `non_activation_conditions` wording. No change since Step 32;
  listed here because it remains unfixed and is squarely in scope for
  Step 34.
- **AI-attribution trailer in pushed history (GIT-01, High)** — commit
  `31e3438` is the only commit in 33 with a message body, and that body
  is `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`. Traceable
  to a documented Step 27 incident (an agent autonomously ran `git commit`
  with its own default template before the "no git commands" delegation
  rule existed). **Requires an explicit user decision — this audit does
  not recommend autonomously rewriting published history.** The git
  cluster's report notes the cheapest real remedy: if `main` is finally
  brought current via squash-merge (see B-1) rather than fast-forward,
  the trailer never reaches the branch a release would actually be cut
  from, without needing to rewrite the branch where it already lives.

## Part 2 — Category-by-category summary (all 26)

Full detail, evidence, and the remaining ~40 High/Medium/Low findings not
elevated to Part 1 are in the 5 linked reports. Brief status per category:

| # | Category | Status | Detail |
|---|---|---|---|
| 1 | Architecture | Sound layering; no structural findings above High | [arch. report §1](final-principal-engineer-audit/architecture-taxonomy-spec-deps-routing-activation.md) |
| 2 | Taxonomy | Catalog accuracy issues (stale counts, 7 sites) — Medium | same, §2 |
| 3 | Skill specification | C-3 (no validator) is the headline issue | same, §3 |
| 4 | Dependency graph | C-1 and C-4 both live here | same, §4 |
| 5 | Routing | C-1's routing consequence; RT-1 (new): trivial-task early exit bypasses gate declaration, Critical | same, §5 |
| 6 | Activation | VR-6/VR-7 hold library-wide; no new Critical beyond C-1 | same, §6 |
| 7 | Context efficiency | Mechanically re-verified: body/description length targets hold library-wide | [context report §7](final-principal-engineer-audit/context-quality-techaccuracy-versions-docs.md) |
| 8 | Skill quality | QR-4 anti-pattern requirement missing in 9 skills (High), clustered in security/infra | same, §8 |
| 9 | Technology accuracy | `nodejs`'s unsupported version claim (Critical, first found Step 28, still live) | same, §9 |
| 10 | Version awareness | **0 of 40** version-scoped skills handle a below-floor version request (Critical) — generalizes Step 32's single-skill `postgresql` finding to the whole library | same, §10 |
| 11 | Security | F3.1 (Part 1); SEC-1 (CSRF gap) is a second release-blocking item per the security cluster | [sec. report §11](final-principal-engineer-audit/security-testing-performance-observability-failurerecovery-approval.md) |
| 12 | Testing | C-5 (Part 1) | same, §12 |
| 13 | Performance | 4 findings, none above High; strongest content encountered in this audit per the cluster's own note | same, §13 |
| 14 | Observability | Hooks EH-1–EH-5 are real but 8 skills gained an unguarded capability barrier as a side effect of the Step 27 VR-5 fix (OBS-4, High, previously unrecorded interaction) | same, §14 |
| 15 | Documentation | B-1 (Part 1); several READMEs understate what's built (denies eval suite/adapter layer exist) | context report §15 |
| 16 | Agent adapters | Test suite re-run against the full current tree (86×6=516 combinations): **passes, zero failures**; one High (loss manifest asserts a false negative about `failure_handling`) | [adapters report §16](final-principal-engineer-audit/adapters-evalsuite-realworldeval-maintainability-extensibility.md) |
| 17 | Evaluation suite | Step 32's scenario-ID reconciliation holds up under scrutiny; S05's sequencing graph depends on the still-missing `SK-FE-005` (ties to C-4) | same, §17 |
| 18 | Real-world evaluation | Step 32 meta-audited and confirmed sound: totals reproduce exactly, citations verbatim, severity not inflated; one scope-estimate correction (17 stale sites, not "one line") | same, §18 |
| 19 | Failure recovery | C-2 (Part 1); F1-F9 has no class for a genuinely self-contradictory request, confirmed | sec. report §19 |
| 20 | Human approval boundaries | C-2 (Part 1) is this category's core finding | sec. report §20 |
| 21 | Git/commit/branch conventions | B-1, GIT-01 (Part 1); branch naming otherwise clean and consistent | [git report](final-principal-engineer-audit/git-comments-legal-vendorneutrality.md) |
| 22 | Human code-comment policy | Clean — passes the explicit checklist above | same |
| 23 | Legal/provenance preservation | Clean — 854/854 `source_references` valid, provenance chain intact through every edit pass | same |
| 24 | Maintainability | A new contributor authoring skill #87 would rely on tribal knowledge not written down anywhere (High) | adapters report §24 |
| 25 | Extensibility | A 7th adapter target is genuinely cheap to add; the lossiness contract has no action for hard truncation (Medium gap) | adapters report §25 |
| 26 | Vendor neutrality | `git-conventions` hardcodes `CLAUDE.md` as *the* agent-instruction file in shared body content copied verbatim to 5 non-Claude adapter targets (High); 34 skills advertise VS Code support with no VS Code adapter built | git report |

## What the library gets right

Worth stating plainly, not just implied by the findings above: the
adapter layer passes its full compatibility suite against the current
86-skill, 6-target matrix with zero failures. Provenance and attribution
survived five separate edit passes (Steps 28, 29, 31, and this step's own
review) with a single, verified-harmless exception. Comment hygiene is
clean throughout. Branch-naming discipline held for all 32 branches
across 7 build phases. The technical substance of the guidance — once a
skill correctly activates — held under every mechanical check this and
the prior step could devise, including checks specifically designed to
find fabrication. Every defect elevated to Part 1 is a defect in the
library's *self-description or self-governance* (a stale metadata field,
an unenforced validation rule, a taxonomy gap in what triggers a gate) —
none is a defect in the technical correctness of what a correctly-routed
skill actually tells an engineer to do. That is the more tractable half
of the two possible failure modes for a project like this, and it is the
half this library is actually in.

## Release recommendation

**NOT READY.**

Five Critical findings and one Blocker are currently live, three of which
(C-1, C-2, C-5) have already been shown — not hypothesized — to produce a
concrete bad outcome via Step 32's real-task tracing. A production
engineering team relying on this library today would hit the auction
concurrency bug (C-1/M-06), get a technically-correct-looking but
unenforceable branch-protection policy (C-2/G-5), and could ship untested
code marked complete (C-5) — not as edge cases, but as the modal outcome
for tasks that touch those paths.

This verdict should not read as "extensive rework required." Read Part 1
again with an eye to effort, not severity: C-1 is a scripted find-replace
across ~50 known sites. C-4's routing half is the same. C-3 is one new
validator script, not a redesign, and once it exists it structurally
prevents C-1 and C-4's *recurrence* rather than just their current
instances. C-5 is one new specification rule (`VR-9`) plus adding one
verification line to each of 52 skills. B-1 is a fast-forward merge,
pending the user's explicit decision on the one commit it would carry
forward with it. Only C-2 (the gate taxonomy) is genuine design work,
and even there the security cluster's own report scopes it as one
taxonomy-level correction, not a rewrite of the orchestrator.

**Recommended path to READY WITH CONDITIONS**, for Step 34: close C-1
through C-5 and B-1 (all six release-blocking items above) — none
requires touching the approved architecture, per the master plan's Step
34 rule 4. Everything in Part 2 rated High or below can reasonably ship
under documented conditions (tracked as known issues) rather than
blocking a release, since none of them has a demonstrated real-task
failure mode the way the six blocking items do.
