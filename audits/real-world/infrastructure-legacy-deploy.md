# Real-World Evaluation — Infrastructure / Legacy deployment modernization

**Step 32** of the master build plan. Date: 2026-09-11. Domain: Infrastructure.
Adversarial pattern: **legacy code**.

**Method.** Worked as the orchestrator specified in [`core/orchestrator/`](../../core/orchestrator/),
routing per [`core/routing-architecture/`](../../core/routing-architecture/) and
sequencing per [`core/dependency-architecture/`](../../core/dependency-architecture/),
reading the actual `skill.yaml`/`SKILL.md` files rather than the catalog's
description of them. Severity vocabulary is this project's audit convention
(Critical / High / Medium / Low), not `evaluations/scoring.md`'s
critical/major/minor assertion weights.

**Standing caveat**, per [`core/orchestrator/self-review.md`](../../core/orchestrator/self-review.md)
R-1 and `audits/cross-skill/routing-audit.md`: nothing here is enforced by a
runtime. These are findings about what a *compliant* run would and would not
reach, given the text that is actually in the files.

**Not re-derived.** Step 28 (`audits/2026-09-10-individual-skill-review.md`) and
Step 29 (`audits/cross-skill/`) are treated as established. Where a Step-29
finding (X-02, X-04, R-05, R-06) is implicated, this document evaluates
**whether it actually bites on this task**, and cites it rather than re-finding it.

---

## The task

> "Modernize our deployment setup — we're still using a hand-written Dockerfile
> from 3 years ago and manual SSH deploys, no CI/CD."

**Repository signals** (the bounded Phase-0 scan, `routing-algorithm.md:9-19`):

- `Dockerfile` present, hand-written, ~3 years old; base image is a
  known-EOL Node line. Single-stage, runs as root, `COPY . .` before
  `npm install`.
- `package.json` present (Node/Express service).
- No `.github/workflows/`, no `.gitlab-ci.yml`, no pipeline config of any kind.
- No `compose.yaml`.
- Deploy is a documented manual `ssh` + `docker run` procedure in the README.

---

## Trace

### P0 — Intake

- **Intent** (`routing-algorithm.md:23-24`): `modernize` — one of the twelve
  named intents.
- **Task type**: workflow pattern **#9 Legacy modernization**
  (`workflows.md:151-163`), which explicitly builds on #5 (refactoring) and
  #6 (migration).
- **Complexity**: `multi-step` → `project` (three distinct delivery artifacts:
  image, pipeline, deploy path).
- **Risk class** (D3, `lifecycle.md:88-89`): **production**. The task's end
  state is automated production deployment. This single value drives D13
  admission and ER-2 gating.
- **S-Gate 1** (`security-and-validation.md:64`): the task carries a **secret**
  dimension — replacing manual SSH deploys means deploy credentials move into
  a pipeline. This is what admits `security-engineering` under SR-5.

### P1 — Discovery

Domains in play: INFRA (all three skills), CONV (modernization), TECH
(nodejs, docker, github-actions), QA (security, testing).
No conflict cluster is contested: `docker` is the only container engine
profiled and `github-actions` the only CI platform (`github-actions`
non-activation explicitly declines Jenkins/CircleCI/GitLab CI as
"not researched or grounded in this library").

### P2 — Routing (default-deny, Tier-0 only)

**Selected:**

| Skill | Fires on |
|---|---|
| `SK-INFRA-001` containerization | activation 1 + 3 (`skill.yaml:32,34`) — "authoring/reviewing a Dockerfile"; "an existing image's size, build-cache efficiency, or security posture needs review" |
| `SK-INFRA-002` ci-cd-pipeline | activation 1 (`skill.yaml:34`) — "Setting up CI/CD for a project that doesn't have it" — verbatim match |
| `SK-INFRA-003` deployment-release | activation 1 + 3 (`skill.yaml:35,37`) — deploying to an environment; existing deployment's rollback path needs review |
| `SK-CONV-005` legacy-modernization | activation 2 + 3 (`skill.yaml:33-34`) — "Modernizing outdated patterns" / "Migrating off a deprecated approach" |
| `SK-TECH-github-actions` | activation 1 (`skill.yaml`) — a workflow file "is being authored" |
| `SK-TECH-nodejs` | activation 1 (`skill.yaml:35`) — `package.json` present |
| `SK-QA-002` security-engineering | activation 1 — CI secret handling is a trust-boundary/secret concern (SR-5 + S-Gate 1) |
| `SK-QA-001` testing-strategy | pulled in as a hard dependency, see P3 |
| `SK-CONV-004` refactoring | pulled in as a hard dependency, see P3 |

**Correctly excluded:** `SK-TECH-docker` — and this is the interesting
exclusion. All five of its activation conditions (`docker/skill.yaml:36-40`)
are **Docker-Engine/API/Buildx/Compose version-gate** questions, and its
non-activation condition 1 (`:42`) routes "General Dockerfile/image authoring,
layer-caching order, multi-stage structure, or non-root defaults with no
Docker-Engine/API/Compose-version-specific question" to `containerization`.
Under SR-2 this is decisive. **`docker` is correctly not selected.**

Also excluded, correctly: all frontend, data, realtime, AI, SEO, and search
skills (no signal), `husky` (no local-hook concern), `data-migration`
(no database in scope).

### P3 — Resolution

- `legacy-modernization` carries `depends_on_skills: [SK-CONV-004, SK-QA-001]`
  (`skill.yaml:58`) — a **hard** composition edge, so `refactoring` and
  `testing-strategy` enter the plan by prerequisite closure, not by their own
  activation.
- Prerequisite chain (`dependency-graph.md:80`):
  `ci-cd-pipeline → containerization`… in fact `deployment-release ⇐ ci-cd-pipeline`,
  and `ci-cd-pipeline` composes `testing-strategy`.
- **T-Gate 2** (`security-and-validation.md:97`): refactoring requires a green
  baseline. The repo has no CI and (per signals) no verified suite, so the
  unverifiable-behavior-preservation risk must be flagged and confirmed.
  This fires correctly.
- **T-Gate 1**: a verification step must be staffed, or its impossibility
  declared up front at P4.
- **Gate declaration (ER-1, `lifecycle.md:163-164`)**: every gate the plan will
  hit is enumerated *now*. This is where the run breaks — see **RWI-03**.

### P4 — Admission

D13 (`lifecycle.md:191-197`) requires explicit confirmation: risk class is
`production` **and** complexity is `project`. Two independent triggers. The
admission card must present the ordered stages, the gates, and known
degradations.

### P5–P7

Execution proceeds `legacy-modernization` (assess) → `containerization`
(image) → `ci-cd-pipeline` (pipeline) → `deployment-release` (cutover, ⛔) with
`code-review ⤾` after the build stages and `security-engineering` as a
mandatory S-Gate 4 facet (secrets touched).

**Known Step-29 finding that does *not* bite here:** R-06 (review loop has no
Tier-0 trigger) used "Add a Dockerfile for this service" as its worked case,
where SR-7 suppresses the composer. Here complexity is `project`, so SR-7 does
**not** self-suppress, `workflow-composer` engages, and every workflow pattern
inserts `code-review ⤾`. R-06 is real but inert on this task shape.

---

## Findings

### RWI-01 · The EOL base image is owned by no skill that activates — **High**

**Finding.** The task's most concrete piece of technical debt — a base image on
an end-of-life Node line — is not reachable from any activated skill's
declared content.

- `docker` correctly does **not** activate (above), and correctly carries no
  base-image-currency content: its Knowledge (`SKILL.md:45-93`), Decision
  framework (`:95-127`), Engineering rules (`:129-153`) and Anti-patterns
  (`:155-175`) are entirely about *Docker's own* version gates (Engine API
  floor, Go SDK module path, Build Checks, Compose fields, cgroup v1, ECI).
  Nothing about the *contents* of the image it builds. **This answers the
  question the step brief posed: `docker/skill.yaml` does not flag the
  EOL-base-image risk, and it is right not to — the defect is elsewhere.**
- `containerization` **does** activate and owns the Dockerfile. Its base-image
  guidance is: workflow step 2, "Choose a base image and design the instruction
  order for cache efficiency" (`SKILL.md:108`); `description` "small base"
  (`:5`); `optional_context` "base-image policy" (`skill.yaml:51`);
  `failure_handling` "…rather than guessing a base image" (`:87`). Every
  mention is about **size, cache order, or entrypoint** — never support status.
- Its `verification` list (`skill.yaml:89-92`) has exactly three items:
  non-root, layer order, multi-stage. Its `evaluation_criteria` (`:93-96`)
  likewise. **A run can satisfy `containerization` completely while shipping an
  EOL base image**, because the skill's own pass/fail contract has no item the
  EOL image could fail.
- Corpus-wide: `grep -i "base.image"` across `skills/` returns 12 sites, none
  of which is a currency or support-status rule.

The concept *does* exist in the library — in `legacy-modernization`, which is
excellent on it: Decision framework step 2, "**Is the current state merely
outdated, or fully unsupported/EOL** (no security patches at all)? The latter
changes the urgency of the plan, not just its scope" (`SKILL.md:76-78`);
Anti-pattern 2 (`:129-130`); Security section (`:141-144`). But every worked
example in its Knowledge section (`:34-52`) is a **framework** version
(React RSC CVEs, Next.js 13-14, Angular's TypeScript floor, Vue 2 EOL), its
single `source_reference` is the version matrix's framework rows, and nothing
in it names a container base image. Whether a real run makes the leap from
"modernize the deployment setup" to "the `FROM` tag is an unsupported runtime"
depends on inference, not on any stated rule.

**Root cause.** The `containerization ⟷ docker` unification (`X-14`) split the
container domain by *engine-specific vs. engine-agnostic*, but base-image
currency is neither — it is a property of the **image's payload**, which
falls between the generic skill's "authoring method" scope and the technology
skill's "Docker mechanics" scope. Neither skill's `scope` field claims it, so
neither author wrote it.

**Recommended correction.** Add to `containerization`, mirroring the house
pattern that `openapi-swagger` already demonstrates (activation "assess CVE/EOL
exposure"; `required_context` "the version currently deployed — needed to
assess CVE/EOL exposure"; `escalation` on an EOL line; `verification`;
`evaluation_criteria` — five fields all carrying the discipline):

1. a `required_context` entry — "the base image's tag and its upstream support
   status (actively patched / maintenance / EOL)";
2. a Decision-framework step before the existing step 1 — "Is the base image on
   an actively-supported line? An EOL base image is an unpatched-vulnerability
   floor no layering or hardening choice above it can raise";
3. a `verification` item — "the base image is on a currently-supported upstream
   line, or the exception is explicitly stated";
4. a cross-reference by ID to `SK-CONV-005`'s outdated-vs-EOL urgency
   distinction rather than restating it (QR-2).

This is content authoring in one file, not a restructuring.

**Regression test requirement.** **New scenario required.**
`evaluations/scenarios/` has no scenario in which `SK-INFRA-001/002/003` is the
*subject* — they appear only as tail stages of S05 and as explicit exclusions
in S06 — and `SK-TECH-docker` and `SK-TECH-github-actions` appear in **zero**
scenarios (they are among the 9 uncovered skills `regression-suite.md:17-19`
already admits). Proposed `S17 — legacy Dockerfile and no CI/CD`, category
**Legacy-code tasks**, with a `critical` assertion: the run's final report names
the EOL base image as a distinct finding with its own remediation, and
`SK-INFRA-001`'s return envelope carries a `verification[]` entry for base-image
currency that is `pass`/`fail`, never absent.

---

### RWI-02 · Image scanning falls through the mutual hand-off between `containerization` and `ci-cd-pipeline` — Medium

**Finding.** The one mechanism that could catch an EOL base image indirectly is
a vulnerability scan, and it is never wired into anything standing.

- `containerization` workflow step 6: "**If** image scanning is available, run
  it and address findings before treating the image as production-ready"
  (`SKILL.md:116-117`) — conditional, Tier-B, one-shot.
- `ci-cd-pipeline`'s Decision framework (5 steps), Workflow (8 steps),
  Engineering rules (5), `verification` (`skill.yaml:88-91`) and
  `evaluation_criteria` (`:92-95`) contain **no scan stage of any kind**. Its
  Security section covers secrets, OIDC, token scope, and action pinning only.
- `github-actions`: `grep -i "dependabot|codeql|scan|trivy|scout|vulnerab"` over
  its body returns **zero** hits, despite the library's own
  `security-engineering/references/vulnerability-watch-list.md:45` listing
  GitHub's Dependabot/CodeQL/secret-scanning as documented capabilities.
- The two skills hand off to each other across exactly this hole:
  `containerization/SKILL.md:119-120` defers "how it gets built/tested/pushed
  automatically" to ci-cd-pipeline; `ci-cd-pipeline/SKILL.md:125` defers
  "image-authoring specifics" to containerization. Scanning is neither, and
  lands in neither.

Secondarily: even a working scan reports **CVEs**, not EOL-ness. "This image
has N known vulnerabilities" and "this runtime will never receive another
security patch" are different claims with different remediations.

**Root cause.** `ci-cd-pipeline`'s `owned_knowledge` (`skill.yaml:80-82`) is
"pipeline stage-sequencing and gating method" + "OIDC and least-privilege token
design". Security *scanning as a pipeline gate* was not claimed by anyone, so
the stage-sequencing skill sequences no such stage.

**Recommended correction.** Add one Decision-framework step and one Workflow
step to `ci-cd-pipeline` — "which scans gate the merge (dependency/SCA, secret,
image), and do they block or report?" — deferring the *content* of findings to
`SK-QA-002` (QR-2). It belongs in `ci-cd-pipeline` rather than
`github-actions` because it is platform-agnostic gating design, which is
exactly that skill's declared scope.

**Regression test requirement.** Covered by the same proposed **S17** as a
`major` assertion: the produced pipeline includes at least one security-gating
stage, or explicitly records the decision not to and why.

---

### RWI-03 · `deployment-release` is a production gate with an empty `escalation` field, on the one task where it matters most — **High**

**Finding.** This is X-04 / R-05's sharpest instance, and it **does** bite here.
Verified mechanically: `containerization`, `ci-cd-pipeline`,
`deployment-release`, and `docker` **all four** have zero `escalation:` keys in
`skill.yaml`, while all four carry substantive `## Escalation` body sections.
For comparison, `postgresql` (`skill.yaml:219`) does declare one.

The bite is traceable:

- Risk class here is `production` (P0/D3).
- `matrices.md:152` names `deployment-release → production deploy → ↑ human (confirm)`.
- Its body enforces it emphatically: workflow step 7, "Any production-affecting
  action is presented for explicit confirmation before execution — never applied
  unilaterally"; and `skill.yaml:96` places the same rule in `verification`.
- **But** ER-1 (`rules.md:99-101`) requires the plan to name every gate *before
  work starts*, and CS-1 (`rules.md:53-55`) forbids loading a body to decide.
  `verification` is not a Tier-0 field either. So at P3 step 5 and P4/D13 —
  the exact moments the architecture designates for gate enumeration — the
  orchestrator has **no** machine-readable evidence that a G-PRODUCTION gate
  exists on this plan.

The gate is not *lost* (it surfaces at P5 when the body loads), but it surfaces
**after admission**, which is precisely the failure ER-1 was written to prevent.
For a plan whose entire purpose is to automate production deploys, that is the
worst possible skill to have this defect on.

**Root cause.** Authoring-convention drift across 27 skills (X-04), not an
oversight on this file. The deeper question X-04 raised — whether the spec
should make `escalation` **required** whenever the body has the section —
remains the right one.

**Recommended correction.** Per X-04, decide the spec question first, then sweep
all 27 in one pass behind a validator. If a partial fix is wanted sooner,
`deployment-release` is the single highest-value file: mirroring its body prose
into `escalation` is two lines and closes the one gate `matrices.md` already
names normatively.

**Regression test requirement.** **New scenario required**, and it is
partially distinct from S17's activation focus. Fold into **S17** as a
`critical` assertion: the P4 admission presentation enumerates the
G-PRODUCTION gate on the deploy step *before* any mutation, and the run's ledger
shows a matching recorded approval before the cutover (FV-9). Score `blocked`
rather than `pass` if no gate record was kept.

---

### RWI-04 · Three stale Tier-0 "not yet authored" markers sit on the exact hand-off edges this task traverses — Medium

**Finding.** X-02 counted 50 stale markers across 15 skills and noted that 16 of
them sit in `non_activation_conditions`, the only field CS-1 lets the router
read. This task traverses three of them, which is a materially worse
concentration than the corpus average:

| Site | Text | Reality |
|---|---|---|
| `containerization/skill.yaml:37` | "…route to ci-cd-pipeline, **not yet authored**" | `skills/ci-cd-pipeline/` is authored |
| `deployment-release/skill.yaml:41` | "…route to ci-cd-pipeline, **not yet authored**" | authored |
| `docker/skill.yaml:44` | "…route to security-engineering, SK-QA-002, **not yet authored**" | authored |

Plus `docker/skill.yaml:9` (`parents` comment), `containerization/skill.yaml:20`
and `SKILL.md:20,119`, `deployment-release/skill.yaml:16` and `SKILL.md:18,80`
(the last of which calls `SK-CONV-001` git-conventions unauthored — X-02's
"inverted" case, since git-conventions was the *first* skill built).

Why this concentration matters more than the raw count: this is a
**three-skill hand-off task** (image → pipeline → deploy), and two of the three
hand-off edges are marked non-existent, while the third marker sits on the
escalation target (`security-engineering`) that the EOL/supply-chain question
would route to. D6 (`lifecycle.md:116-117`) asks "is a candidate skill authored,
or only a catalog entry?" — here the router has *affirmative, false* evidence
that the answer is no, and `skill-router`'s own failure-handling rule ("If a
candidate skill exists only as a catalog entry, record the gap and route to the
nearest authored skill", `SKILL.md`) would fire wrongly.

**Root cause.** Per X-02: nothing re-checks forward references when a skill
lands. Second consecutive audit to find the class.

**Recommended correction.** X-02's recommended single mechanical sweep, plus the
repo-level guard it asked for. No new judgement needed for these three sites —
all are pure deletions of a false clause.

**Regression test requirement.** **No new scenario.** This is mechanically
checkable (a validator asserting every skill ID named in prose resolves to
`skills/<slug>/`) and belongs in the VR-3 family, not in a behavioral suite.
`regression-suite.md:54-60`'s trigger 5 ("a cross-skill audit finds a new
instance of an already-tracked pattern") already covers re-running affected
scenarios once the sweep lands.

---

### RWI-05 · `legacy-modernization` requires a `target-versions` input and has no `failure_handling` rule for its absence — Medium

**Finding.** `legacy-modernization/skill.yaml:44-46` declares
`target-versions` with `required: true`; `required_context` (`:47-49`) demands
"the current state and the target state" plus "documented breaking changes
between them". The user named no target — not for the base image, not for the
CI platform, not for the deploy strategy.

That is an `F1` (input-deficient) at P5 readiness. D16
(`failure-recovery-and-escalation.md:75`) resolves F1 as "**R7 (ask) or R4** —
**the skill's own `failure_handling` decides which**; if it permits advisory
degradation, prefer R4 over interrupting."

`legacy-modernization`'s `failure_handling` (`skill.yaml:79-81`) has exactly two
rules: (a) the target technology's breaking-change data isn't in this library's
research, (b) a big-bang rewrite is proposed. **Neither is "the user named no
target."** The rung selection D16 delegates to the skill is therefore
undetermined on the skill whose activation this entire task hinges on.

The library elsewhere handles this exact case well and consistently:
`docker/skill.yaml:183` ("If the version cannot be determined, ask for it or
state the version the guidance assumes before making a version-gated claim;
never assume 'latest' silently"), and the same rule shape appears in
`postgresql`, `nodejs`, and `openapi-swagger`. The skill missing it is the one
whose *entire method* is version-gap assessment.

**Root cause.** `failure_handling` was authored against the skill's *knowledge*
risks (ungrounded research, rewrite pressure) rather than against its *declared
inputs*. No validation rule cross-checks `required: true` inputs against
`failure_handling` coverage.

**Recommended correction.** One rule: "If the target state/version is not
stated, propose a defensible target (the current supported line for each
component in the dependency chain) and confirm it before planning stages; never
assume 'latest' silently." Note this correction also closes RWI-01 partially —
a rule that computes the current supported line per component in the dependency
chain would surface the Node base image.

**Regression test requirement.** **Already covered behaviorally — but at the
wrong weight and against the wrong artifact.** S11 (`jquery-to-vue-modernization`)
exercises the identical shape: "No target Vue version is named"
(`scenarios/S11:16-17`), and `expected-behaviors/S11:67-71` names
`SK-CONV-005`'s `required: true` `target-versions` input explicitly, with
assertion 7 requiring the unpinned target to surface as an `open_questions[]`
entry rather than being silently assumed.

Two refinements, not a new scenario:

1. **Re-weight S11 assertion 7 from `minor` to `major`.** Per `scoring.md`,
   `minor` "does not by itself change a scenario's verdict." Silently assuming a
   migration target on a production-impacting upgrade is not a precision point —
   it is the behavior D16 exists to select a rung for.
2. **The underlying defect is not scenario-shaped and should not be chased with
   one.** S11 tests whether a *run* asks; RWI-05 is that the *skill file* gives
   D16 no rung to pick. That is a `failure_handling`-completeness check —
   "every `required: true` input has a `failure_handling` rule for its absence" —
   which is mechanically validatable across all 86 skills and belongs in the VR
   family, not in a behavioral suite. The S17 scenario proposed above should
   **not** duplicate it.

---

### RWI-06 · No signal, and no skill's activation, connects a Dockerfile `FROM` tag to a runtime support calendar — Medium

**Finding.** Three independent layers each miss the link:

1. **The scan.** `routing-algorithm.md:14` does list `Dockerfile` among the
   config files the Phase-0 scan reads. But CS-6 (`rules.md:67-69`) scopes it:
   "the repo scan reads manifests/config/entrypoints, not the whole tree; **it's
   for detection, not comprehension.**" Evaluating `FROM node:<tag>` against
   Node's release-line calendar is comprehension. The rule that bounds context
   cost also bounds this detection out of existence.
2. **Activation.** No skill in the corpus declares an activation condition
   keyed on base-image currency. `nodejs`'s condition 3 — "A Node.js
   version/upgrade/**EOL**/security-release question **is asked**"
   (`skill.yaml:37`) — is *question*-triggered, not signal-triggered. Nobody
   asks. (`nodejs` still activates via condition 1 on `package.json`, but
   activating it does not cause the `FROM` tag to be read.)
3. **The one near-link.** `nodejs/skill.yaml:53` declares
   `existing-node-target` as "The Node.js version(s) already targeted
   (package.json `engines`, `.nvmrc`, CI matrix, **Docker base image tag**)" —
   the single field in the entire corpus connecting a Docker base image tag to
   Node version policy. It is `required: false`, and it sits on a skill that
   does not own the Dockerfile.

**Root cause.** A routing-architecture/skill-corpus seam of exactly the shape
`routing-audit.md`'s closing observation named: a rule written in one layer
without a counterpart in the metadata the rule must read — here, inverted (a
signal that *should* exist in skill metadata and does not).

**Recommended correction.** Prefer the skill-side fix (RWI-01) over widening
CS-6. Adding a `required_context` item to `containerization` makes the base
image's support status something the *skill* asks for at P5 readiness, which
costs nothing at routing time and does not erode the CS-6 boundary.

**Regression test requirement.** Covered by **S17**. The scenario's "Repository
signals" section should state the base image tag explicitly (the suite's own
convention — see S11's signals) so the assertion is checkable without requiring
the evaluator to assume comprehension the scan doesn't perform.

---

### RWI-07 · `legacy-modernization`'s verification method does not map to configuration artifacts — Medium

**Finding.** `evaluation-spec.md:156-161` names legacy-code scenarios as the
stress test for whether the VR-4 upward-dependency tension "actually causes a
bad run in practice or is benign." On this task the **VR-4 tension itself is
benign** — the two edges (`legacy-modernization → refactoring`,
`→ testing-strategy`) are acyclic, intentional, and exactly the cross-cutting
QA delegation `dependency-audit.md`'s Option C would legitimize.

The *composition semantics* are what misfire. `legacy-modernization`'s workflow
step 4 (`SKILL.md:96-97`) is "Apply each stage using **refactoring's
behavior-preservation discipline, verified via testing-strategy**", and
Decision-framework step 5 (`:85-87`) makes it mandatory: "Is each staged step
itself behavior-preserving, verified the same way a refactor would be?"

The artifacts here are a `Dockerfile`, a workflow YAML, and a deploy procedure.
There is no test suite whose greenness demonstrates a Dockerfile's behavior is
preserved, and the repo has no CI at all — so T-Gate 2's green baseline is
definitionally absent. The skill offers **no branch** for "the thing being
modernized is configuration/infrastructure rather than code", so a compliant run
either (a) flags unverifiable behavior preservation and proceeds — which is the
*honest* outcome and arguably a positive — or (b) invents a verification story.

Calling this Medium rather than Low because the correct verification for this
task class does exist and is specific: build the image and assert it starts and
serves; run the pipeline on a branch; deploy to a non-production environment and
exercise the rollback path. `deployment-release`'s own `verification`
(`skill.yaml:94`) already says "A rollback path is explicit and **actually
working**, not assumed" — the right check exists in a sibling skill and
`legacy-modernization` never reaches for it.

**Root cause.** `legacy-modernization` was authored for code modernization (all
its worked examples are framework upgrades) and its hard dependencies encode
that assumption structurally, via `depends_on_skills`.

**Recommended correction.** Add a Decision-framework branch: "Is the artifact
being modernized code, or configuration/infrastructure? For the latter,
behavior preservation is demonstrated by exercising the artifact
(build → run → rollback), not by a code test suite — defer to the owning INFRA
skill's `verification` rather than to `SK-CONV-004`'s." No dependency change
required.

**Regression test requirement.** **New scenario required** — and this is the
strongest single reason S17 should exist as its own file rather than as an
extension of S11. S11 is a code-modernization legacy scenario; **no scenario in
the suite exercises legacy modernization of a non-code artifact**, which is
exactly the branch this finding says is missing. Category: **Legacy-code tasks**
(the suite would then carry 3 in that category, which is fine —
`regression-suite.md` sets 2-per-category as a floor, not a cap).

---

## What works (recorded so a later reviewer does not re-open it)

- **The INFRA hand-off partition is clean.** All three skills carry reciprocal
  cross-routing non-activation clauses that partition image-authoring /
  pipeline-design / deploy-strategy with no overlap and no gap in *scope*
  (`containerization:36-38`, `ci-cd-pipeline:37-40`, `deployment-release:38-41`).
  This is the cross-routing discipline `routing-audit.md` praised, working.
- **`docker`'s narrow, version-gated activation is correct and valuable.** It
  keeps a 279-line technology body out of a task that does not need it (CS-2),
  and its non-activation names the right owner. Over-activation does not occur.
- **`ci-cd-pipeline` addresses the security debt the user did not ask about,
  proportionately.** Decision-framework step 2 makes OIDC-over-static-keys the
  default posture, not a case-by-case call (`SKILL.md`; `skill.yaml:90`). The
  user asked to remove manual SSH deploys for *convenience*; the library
  converts that into a credential-posture improvement without being asked and
  without over-reaching. This is dimension 5 working well.
- **`deployment-release` declares its own grounding thinness** (`skill.yaml:17-23`,
  `evaluation_criteria:99`) — a model of the honesty discipline, and directly
  relevant here since rolling-vs-blue-green for this service is exactly the kind
  of advice a less careful library would fabricate.
- **`workflow-composer` is correctly engaged** (complexity `project`), so R-06's
  suppression hole does not open.

---

## Score

| # | Dimension | Verdict | Why |
|---|---|---|---|
| 1 | Skill routing | **Good** | All four owning skills fire on verbatim activation matches; `docker` correctly excluded by SR-2; no over-activation observed. Marred only by RWI-04's false markers on the traversed edges. |
| 2 | Dependency activation | **Good** | `legacy-modernization`'s hard edges pull `refactoring` + `testing-strategy` correctly; `deployment-release ⇐ ci-cd-pipeline` sequences right. The VR-4 tension is benign here (RWI-07). |
| 3 | Context efficiency | **Good** | ~4 generic bodies + 2 technology bodies, stage-scoped per CS-2; `docker`'s 279 lines never load. Proportionate to a project-complexity task. |
| 4 | Implementation quality | **Adequate** | Multi-stage / non-root / cache-order modernization is correct and complete; the base-image half of "modernize" is missed (RWI-01). Half the stated debt is addressed well. |
| 5 | Security | **Weak** | OIDC and token scoping are a genuine unrequested win, but the EOL base image — the largest standing security exposure in the repo — is caught by nothing (RWI-01), and no scan gate is designed (RWI-02). |
| 6 | Testing | **Adequate** | T-Gate 1/2 fire correctly and the missing green baseline is flagged honestly; but the verification method offered does not fit the artifacts (RWI-07). |
| 7 | Maintainability | **Good** | `legacy-modernization` defaults to incremental with rollback points and requires justification for a rewrite; `deployment-release` refuses to fabricate strategy depth. No over-engineering trap observed. |
| 8 | Error handling | **Adequate** | The corpus-wide `failure_handling` strength (X-21) holds, but the one gap is on the pivotal skill (RWI-05) and leaves D16's rung selection undetermined. |
| 9 | Convention adherence | **Good** | No repo conventions are contested; `git-conventions` attaches correctly at P7 for the commit; FV-3 checkable. |
| 10 | Final outcome | **Adequate** | A real engineer gets a correct multi-stage image, a sound OIDC pipeline, and an honest deploy plan — and would still be running an unsupported Node runtime in production, with no gate having told them so, and with the production-deploy approval surfacing later than the architecture intends (RWI-03). |

**Summary:** High ×2 (RWI-01, RWI-03), Medium ×5 (RWI-02, RWI-04, RWI-05,
RWI-06, RWI-07). The routing is genuinely good; the gap is content ownership at
the seam between two deliberately-unified skills, plus one metadata defect
(X-04) landing on the worst possible file for this task class.
