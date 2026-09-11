# Real-World Evaluation — AI/LLM: RAG support chatbot with human fallback

Date: 2026-09-11. Step 32 of the project's master build plan. Domain: **AI/LLM**.
Adversarial pattern: **outdated technology assumptions** — the eight `SK-AI-*`
skills carry `last_verified: "2026-09-10"`, one day before this evaluation, so
the question is not whether they have *gone* stale but whether they are already
showing staleness *pressure* and whether their own mitigations are evenly
applied.

**Method.** Routed against real Tier-0 metadata per CS-1, then loaded the bodies
of the skills a compliant run activates, and traced workflow pattern #10 (AI
feature development, `workflows.md:165-183`) end to end. This is the **first time
the eight AI skills have been evaluated as a composed chain against one real
task** — Step 28 reviewed each in isolation, Step 29 analysed the corpus as a
graph. Three of the findings below are only visible from the composed view.

**Not re-derived.** Step 28 and Step 29 findings are treated as settled. Where
this trace produces a new *consequence* of one — or, in one case, **corrects**
one — it says so explicitly.

---

## The task

> Add a customer-support chatbot feature that uses an LLM to answer questions
> from our product documentation (RAG), with a fallback to human support for
> anything it's not confident about.

**Repository context.** A web app with existing product documentation in markdown
files. No existing AI/LLM features.

---

## Trace

### P0 — Intake

| Determination | Value | Basis |
|---|---|---|
| Intent | `build` | — |
| Task type | **workflow #10 — AI feature development** | `workflows.md:165` |
| Complexity | project (spans AI, data/search, frontend, QA, infra) | — |
| Risk | reversible-write → **production**; plus **G-COST** (live external LLM calls) | `failure-recovery-and-escalation.md:150` |
| **S-Gate 1** | **fires on three of five dimensions**: untrusted input (customer questions), user-facing exposure, LLM-with-content-ingestion. No tool access, no secrets in the feature itself. | `security-and-validation.md:64` |

Signal scan: web-app manifest; markdown docs corpus; **no** AI SDK dependency,
**no** vector store, **no** embedding pipeline, **no** eval harness.

### P1 — Discovery

Conflict clusters: none declared — all eight `SK-AI-*` skills carry
`conflicts_with: []`. Two decisions are *required but undetected*, so SR-4
applies: activate the generic decision layer and raise the choice, do not
activate every sibling.

- **Model/provider/tier** → generic owner is `model-selection` (SK-AI-006), which
  *is* the decision layer. Correct by construction.
- **Retrieval engine / vector store** → generic owner is `search-integration`
  (SK-DATA-005). **This is where routing breaks — see A-01.**

### P2 — Routing

**Selected.**

| Skill | Activation condition matched |
|---|---|
| `llm-application-engineering` SK-AI-001 | "Starting a new LLM-powered feature" (skill.yaml) — the domain root |
| `rag-engineering` SK-AI-005 | "A feature needs LLM output grounded in a specific document/data corpus rather than the model's own knowledge" — near-verbatim match |
| `prompt-context-engineering` SK-AI-002 | "Output quality depends on prompt or context structure" — RAG context injection |
| `model-selection` SK-AI-006 | "Choosing which model/provider/tier a feature should call" — nothing is fixed |
| `llm-evaluation` SK-AI-007 | "Building or reviewing an LLM feature that needs quality verification before shipping"; also "A feature is exhibiting suspected hallucination" via the confidence requirement |
| `ai-security` SK-AI-008 | "Reviewing or designing an LLM feature with tool access, **untrusted-content ingestion, or user-facing exposure**" — two of three; **mandatory** review facet per S-Gate 4 |
| `security-engineering` SK-QA-002 | SR-5 — untrusted input; S-Gate 4 routes non-LLM-specific AppSec here even inside an LLM feature |
| `requirements-engineering` SK-DISC-001 | SR-8 + "The request implies but doesn't state a constraint" — the confidence requirement is entirely unspecified |
| `solution-architecture` SK-DISC-002 | "A significant technology choice is open" — vector store, hosted-vs-self-managed retrieval, provider. ⛔ G-COMMITMENT |
| `technical-planning`, `workflow-composer`, `capability-adapter`, `skill-router` | multi-stage, Tier B present |
| `testing-strategy` SK-QA-001 | runnable code; T-Gate 5 defers *acceptance* to SK-AI-007 but suite mechanics stay here |
| `observability` SK-QA-004 | production diagnosability; SK-AI-001 owns the LLM-call logging plan itself and defers the rest |
| `frontend-architecture` + detected FE stack | the chat widget |
| `code-commenting`, `code-quality`, `git-conventions`, `git-workflow`, `code-review` | SR-6 / ER-6 |

**Correctly excluded.**

| Excluded | Reason |
|---|---|
| `agent-architecture` SK-AI-004 | `SK-AI-001` DF#3 requires "the LLM to autonomously sequence multiple tool calls or sub-tasks across turns"; a retrieve-then-answer chatbot does not. Its Anti-pattern 1 names reflexive composition as "the domain's specific over-engineering trap" and Anti-pattern 2 names the "API is agentic by default" framing as the exact overtriggering risk. **This is a non-obvious correct call** — "support chatbot" is precisely the phrase that tempts an agent loop. |
| `structured-output-tool-calling` SK-AI-003 | No schema-conformance requirement is stated at intake. *Uncertain / acceptable either way* — and note it becomes necessary if the human-fallback signal is implemented as a machine-readable flag (see A-02). |
| `redis`, `opensearch`, `clickhouse`, `mongodb` | SR-3 — undetected, and SR-4 says raise the vector-store choice as a decision rather than activating every candidate |
| `caching-strategy` | prompt caching is owned by `SK-AI-002`; no other caching signal |
| `web-accessibility` | **should not be excluded.** A chat widget is user-facing UI; R-03c established that `web-accessibility`'s trigger is "an accessibility audit or review is *requested*", so it silently omits. Confirmed instance of a known Medium finding, not re-counted. |
| `search-integration` SK-DATA-005 | **excluded by SR-2 — and this is the defect.** See A-01. |

### Sequencing (workflow #10)

```
requirements-engineering (incl. eval/acceptance definition — not vibes)
  → solution-architecture ⛔ G-COMMITMENT (vector store, provider, hosted-vs-self)
  → technical-planning
  → capability-adapter (barrier: Tier B throughout the AI cluster)
  → llm-application-engineering: compose the sub-disciplines
       → model-selection
       → rag-engineering ∥ prompt-context-engineering
       → implementation
  → ⟳ eval loop { llm-evaluation harness → adjust prompt/retrieval } until criteria met
  → code-review ⤾ (security ∥ ai-security ∥ performance ∥ quality ∥ comment facets)
  → [first live external LLM call ⛔ G-COST]   ← declared in core/, owned by no skill (A-03)
  → deployment-release ⛔ G-PRODUCTION
```

---

## Findings

### A-01 · A three-skill cross-routing cycle strands the retrieval-engine decision — **High**

**Finding.** The vector-store / retrieval-engine decision — one of the two
irreversible technology commitments in this task — ends up owned by nobody,
because three skills route it to each other in a closed loop.

| Hop | Site | Text |
|---|---|---|
| 1 | `rag-engineering/SKILL.md:137-142` (DF#2) | "Is the retrieval infrastructure itself already decided, or open? **If open, that decision belongs to search-integration (SK-DATA-005)** — don't re-litigate engine choice here." Repeated at Workflow step 2 (:172-174) and Engineering rule 5 (:207-208). |
| 2 | `search-integration/skill.yaml:41` (`non_activation_conditions`) | "The request is really about the RAG/LLM-application layer built on top of vector search (llm-application-engineering) — **a documented research gap in this library, not answered here**." |
| 3 | `llm-application-engineering/SKILL.md:138-140` (DF#4) | "Does the feature need output grounded in a specific retrievable corpus…? → **rag-engineering**." |

Apply SR-2 — "Non-activation is decisive. If a skill's non-activation conditions
match the signals, exclude it — even if its activation also matches." This task
*is* the RAG layer, so `search-integration`'s non-activation matches and the
skill is **excluded** — even though its activation conditions match too ("A
feature needs … semantic/vector search"; "The search-engine choice is open
(database-native FTS vs. dedicated engine vs. vector search)").

So the only skill in the library that owns *"database-native FTS vs. dedicated
engine vs. vector store," index/mapping design, relevance tuning, and index-sync
strategy* is routed out of the only task shape that needs all four, and routed to
a skill that routes straight back.

**New consequence of a known finding.** Step 29's X-02 (consequence 2) identified
this marker as stale and framed the harm as a misleading message: "A user asking
about RAG over their search index gets told the library has nothing, when it has
a dedicated skill." The composed trace shows a materially worse consequence:
it is an **under-activation on a required workflow stage**, and SR-10's
completeness backstop cannot repair it, because the skill the backstop would add
is the one SR-2 just excluded. The marker text is **still present in the live
files** at nine sites (`search-integration/skill.yaml:22-24,32,40,41,97,104`;
`SKILL.md:9,19-21,32,90,131,161-163,196,205`) — two of them in
`non_activation_conditions`, the Tier-0 field CS-1 makes the only thing the
router reads.

**Root cause.** `search-integration` was authored before `rag-engineering`
existed. The guard it correctly wrote to avoid fabricating RAG content became, on
the day `SK-AI-005` landed, a guard against the skill that now owns RAG. Nobody
swept back — the same authoring-order pattern Step 28 named as the corpus's
dominant theme.

**Recommended correction.** Rewrite the non-activation from the *gap* form to the
*scope* form: "RAG-pipeline design (chunking, context injection, grounding,
generation) is owned by `rag-engineering` (SK-AI-005); this skill still owns the
retrieval-engine and index decisions underneath it." Add `SK-AI-005` to
`related_skills`. Symmetrically, tighten `rag-engineering` DF#2 so it *requests*
the engine decision as an open item rather than assuming routing will carry it.

**Regression test.** **Yes — new scenario.** No RAG scenario exists in
`evaluations/scenarios/`; `S08-refund-agent-tool-access` is the only AI scenario
and it is about *tool authority*, not retrieval. Propose
`S19-rag-support-chatbot`, category *Multi-skill tasks*. Assert
`search-integration` appears in the **must activate** set, and that the plan
carries a named, still-open retrieval-engine decision under a G-COMMITMENT gate.

---

### A-02 · The stated "fallback to human support when not confident" requirement is not addressed by any skill in the library — **High**

**This is the most significant finding of this task.** The user stated one
requirement more concretely than any other, and it is the one the library cannot
staff.

**Finding.** A full-text search of all eight `SK-AI-*` files for
`confiden|abstain|"I don't know"|human handoff|human-in-the-loop|fall back to a human|refuse to answer|uncertain|calibrat`
returns six hits, **none of which is design guidance**:

- `ai-security/SKILL.md:95` — human review as a *posture* for agent actions.
- `ai-security/SKILL.md:144`, `llm-evaluation/SKILL.md:99,208` — fluent/confident
  output named as a *hazard*, not a signal to act on.
- `ai-security/SKILL.md:274`, and one `source_references` title.

A repo-wide search of all 86 `SKILL.md` files for
`human (agent|support|operator)|hand off to a person|support ticket|deflect`
returns **zero**.

What the library has is adjacent but structurally different:

| Library content | Why it doesn't cover this |
|---|---|
| `llm-evaluation` DF#4 (SKILL.md:130-135): "Does the feature's output get acted on (by a human or another agent/tool) **without independent verification**? … design a claim-verification step … validate tool-call arguments/preconditions independently" | The mitigation shape is **verification before an action executes**. A support chatbot's output is not an action — it is an answer a customer reads. There is no tool call to validate and no precondition to check. The OWASP LLM07 framing the skill correctly imports (SKILL.md:95-111) is agentic-pipeline-shaped and does not reach the read-only-answer case. |
| `rag-engineering` retrieval jamming (SKILL.md:99-103): "a single engineered 'blocker' document causes the LLM to refuse answers … retrieval-quality monitoring should watch for anomalous refusal rates" | Refusal appears **only as an attack symptom to monitor**, never as a designed behaviour to build. The skill knows refusal exists and models it exclusively as something going wrong. |
| `rag-engineering` decision framework (SKILL.md:131-168), seven steps | Covers need / infrastructure / chunking / authorization-ordering / embedding sensitivity / hosted-vs-self / injection surface. **No low-recall branch.** No retrieval score threshold, no reranking, no requirement that the generated answer cite the chunk it came from — which is the cheapest available confidence proxy and is absent. |
| `llm-evaluation` eval dimensions (SKILL.md:52-54) | task fidelity, consistency, relevance/coherence, tone/style, privacy preservation, context utilization, latency, price. **No out-of-corpus / unanswerable-question class**, so the eval harness will never measure the behaviour the user asked for. |

**Consequence.** A fully compliant run produces a well-secured, well-evaluated,
correctly-authorized RAG pipeline that will answer confidently and fluently about
anything the corpus does not cover — because nothing in the composed guidance
requires an abstention path, a sufficiency signal, or an escalation channel. The
feature ships missing its stated acceptance criterion, and `llm-evaluation`'s own
harness will report green, because no eval dimension covers it.

**Root cause — and why Step 28 could not have caught it.** The AI cluster is
organised around *constructing the LLM call*: prompt, schema, retrieval, model,
eval, security. Answer-confidence and escalation-to-human is a **product-behaviour**
concern that sits across four skills at once — `rag-engineering` owns the trigger
(insufficient retrieval), `prompt-context-engineering` owns instructing the model
to abstain, `llm-evaluation` owns measuring the false-answer rate,
`structured-output-tool-calling` owns emitting a machine-readable `needs_human`
signal. Because it belongs to all four, it was authored into none. **QR-2's
no-duplication discipline has a blind spot at exactly this shape**: a
cross-cutting *behaviour* with no natural single owner is the one thing a
per-skill review cannot detect, because no individual skill is deficient against
its own scope.

**Recommended correction.** Give it one owner rather than four fragments.
`rag-engineering` is the right home, because the trigger is its stage. Add a
decision-framework step:

> **What does this pipeline do when retrieval returns nothing sufficiently
> relevant?** State the sufficiency signal, the abstention behaviour, and the
> escalation path. A pipeline with no low-recall branch will answer out-of-corpus
> questions confidently — the failure mode is indistinguishable from success at
> generation time.

Add the matching `verification` entry ("a non-answer path exists and is
reachable"). Add one eval dimension to `llm-evaluation` — out-of-corpus /
unanswerable-question refusal rate — alongside the existing eight. **Do not
fabricate threshold values**: per SG-2/SG-3 the guidance is that the branch must
exist and be measured, not what the number should be.

**Regression test.** **Yes — new scenario, and the highest-value one produced by
this entire Step 32 evaluation.** Fold into `S19-rag-support-chatbot`. Assert
three things: (a) the requirements artifact contains an abstention criterion;
(b) the eval design includes an out-of-corpus case class; (c) the pipeline design
names a non-answer path with an escalation channel. Not covered by anything in
`evaluations/scenarios/` today.

---

### A-03 · The G-COST approval gate for live LLM calls has no Tier-0 owner anywhere in the library — **High**

**Finding.** Three core documents declare this gate, and no skill implements it.

| Document | Text |
|---|---|
| `core/dependency-architecture/matrices.md:163` | `llm-application-engineering` \| needs a live external LLM call with cost/data implications \| **↑ human (confirm)** |
| `core/orchestrator/failure-recovery-and-escalation.md:150` | **G-COST** — "Real cost or data exposure per invocation \| live external LLM/API calls with cost or data implications" |
| `core/dependency-architecture/workflows.md:176` | "→ [live external LLM call with cost/data implications ⛔ human]" |

`skills/llm-application-engineering/skill.yaml`'s `escalation:` field contains
exactly two entries, **both pure routing statements**: "A request already fully
scoped to one SK-AI-002–SK-AI-008 sub-discipline is routed there directly" and
"A request that is really a general (non-LLM-call) observability need is routed
to SK-QA-004 directly." Its `## Escalation` body section carries the same two and
nothing more. Neither field nor body mentions cost, data exposure, confirmation,
approval, or a gate — a `grep -i "cost\|confirm\|human\|approval\|gate"` over the
whole `skill.yaml` returns four hits, all in observability-plan prose about
token/cost *tracking*.

A field-scoped scan of all 86 `skill.yaml` `escalation:` blocks for "cost"
returns four skills — `graphql-api-design`, `model-selection`, `opentelemetry`,
`webrtc` — and none is this gate (`model-selection`'s concerns an unstated
cost/latency *bar*, not an approval). `grep -rn "G-COST"` across the repository
returns exactly two sites, both in `core/`; **no skill references the class**.

**Consequence.** ER-1 — "the routing plan names every approval gate the task will
hit *before* work starts, so the user isn't surprised mid-run" — cannot be
satisfied for the one gate class unique to this task type. A compliant run stands
up a paid third-party integration that transmits customer support questions to an
external vendor, and never asks.

**This corrects a Step 29 finding.** `audits/cross-skill/routing-audit.md`'s R-05
table audits the escalation matrix row by row and marks this row
"✅ declared". It is not declared, in either the field or the body. The
verification that produced that row appears to have matched on the skill having a
non-empty `escalation` field rather than on its content. Recording this because
R-05's value rests on that table being trustworthy, and because the same method
was used for the other twelve rows.

**Root cause.** Identical in shape to R-02 and R-05: *a rule written in one layer
with no counterpart in the layer that must read it.* The escalation matrix was
authored in the dependency-architecture step; `SK-AI-001` was authored in a later
domain batch; nothing re-checked matrix rows against skills that landed
afterwards.

**Recommended correction.** Add to both the `escalation` field and the
`## Escalation` section of `llm-application-engineering`:

> Standing up a live external LLM integration carries per-invocation cost and
> transmits application and user data to a third party. The first live call, and
> any change that materially alters cost or data exposure, require explicit user
> confirmation (G-COST).

Then re-verify every one of the thirteen escalation-matrix rows against the
authored skills' actual field *content*, not field presence.

**Regression test.** **Yes**, folded into `S19`. Assert the routing plan
enumerates a G-COST gate before any live-call step, and that the gate is
requested with the concrete proposal (provider, per-call data sent, estimated
volume) per the gate-request standard in `failure-recovery-and-escalation.md`.

---

### A-04 · Staleness pressure is already visible, and the cluster's own mitigations are unevenly applied — **Medium**

This is the dimension the task specifically probes. One day past
`last_verified: "2026-09-10"`, the cluster divides cleanly into three groups.

**Exemplary — leave alone.**

- `model-selection` (SK-AI-006) carries **no `covered_versions` and no
  `version_sensitive_claims` block at all**, and instead frames every concrete
  lineup fact as a worked example. Its `verification` requires: "Any current
  model name/price cited is flagged as a worked example to re-verify against
  current vendor docs, not asserted as durably current." Its anti-patterns lead
  with treating tier names and prices as evergreen. Its decision framework
  (SKILL.md) is expressed as a *pattern* — "start from the vendor's own documented
  default tier… escalate one step, not to the top… reach for the effort lever
  before a full tier jump" — that survives any lineup change. For the
  fastest-moving facts in the entire library, this is the right design and should
  be the template.
- `llm-evaluation` (SK-AI-007) refuses to anchor on OpenAI's Evals platform,
  states its deprecation dates inline (SKILL.md:87-93), carries the matching
  anti-pattern (:211-214) *and* the matching `failure_handling` rule, and tells
  the reader to keep the workflow pattern and drop the tool. Three independent
  sites, all consistent.

**Not handled — a real gap.**

- `rag-engineering` (SK-AI-005) asserts a specific hosted-product surface as
  current fact: "OpenAI's Responses API ships a hosted File Search tool that
  performs 'semantic and keyword search' against **vector stores** (files uploaded
  via the Files API, added to a vector store, referenced by `vector_store_ids`),
  requiring no retrieval-side implementation code" (SKILL.md:118-129) — and DF#6
  makes **hosted-vs-self-managed a first-class architectural decision resting on
  it**. Unlike its two siblings, the skill carries **no `reverify_triggers`** for
  that product surface and no "worked example, re-verify" framing. A hosted
  retrieval product's API shape is at least as volatile as a model tier name, and
  here it is load-bearing for an irreversible commitment. This is the clearest
  case in the cluster of a mitigation the library already knows how to apply and
  did not apply.

**Structural, already tracked.**

- X-09 (Step 29) established the Anthropic/OpenAI duopoly across all eight AI
  skills — 62 and 60 mentions, **zero** for any other provider, zero for
  open-weight/self-hosted, zero for data residency as a selection axis — and
  recommended a tracked research gap plus a `model-selection` non-activation
  clause. Still open. Not re-counted, but this trace adds the composed-chain
  consequence X-09 predicted: for a *customer-support* chatbot the missing axis
  bites twice over, because customer questions are third-party personal data, so
  data residency is a first-order selection constraint — and
  `requirements-engineering`'s own NFR checklist explicitly prompts for it
  (`references/nonfunctional-requirements-checklist.md:17`: "data residency").
  Discovery therefore *raises* a constraint that `model-selection`'s four axes
  (capability, cost, latency, context window) have no branch for. The two skills
  are wired to produce a requirement the next skill cannot consume.

**Recommended correction.** Add `reverify_triggers` to `rag-engineering` covering
a change to either vendor's hosted-retrieval surface, and apply
`model-selection`'s "worked example — re-verify" framing to SKILL.md:118-129.
X-09's recommendations remain as written.

**Regression test.** **No new scenario.** This is a re-verification trigger, not a
behavioural assertion — record it in `evaluations/regression-suite.md` as a
trigger condition rather than in `scenarios/`.

---

### A-05 · Nobody owns "the corpus is markdown files in the repo" as an ingestion and sync problem — **Medium**

**Finding.** The corpus is living documentation inside the repository. Someone
edits a markdown file and the chatbot must stop quoting the old text. Index-sync
strategy is explicitly within `search-integration`'s stated scope — and
`search-integration` is excluded by A-01. `rag-engineering` owns chunking and
embedding-model choice (DF#3) but explicitly disclaims the index layer (DF#2,
Engineering rule 5). So the selected set contains nobody who owns ingestion
triggering, re-embedding on change, or stale-index detection.

For a support chatbot answering from product docs, index staleness is the
dominant *operational* failure mode, and it is the precise analogue of the
doc-rot problem `technical-documentation` is built around — with the same
consequence (a confident, wrong answer) and none of the same guidance.

**Root cause.** Same as A-01: the excluded skill is the one that owns index-sync.
Recorded separately because it is the concrete operational cost of A-01 rather
than a restatement of it.

**Recommended correction.** Resolved by A-01's fix; no independent change needed.

**Regression test.** Fold into `S19` as an assertion: the design names an
index-refresh trigger tied to corpus changes.

---

## What the library gets right here

This domain is, on the evidence of this trace, the **strongest cluster in the
library on security and the strongest on scope discipline**.

- **Anti-over-composition works, and it is the non-obvious call.**
  `llm-application-engineering`'s decision framework walks eight sub-disciplines
  and explicitly declines two, with Anti-pattern 1 naming reflexive composition
  as "the domain's specific over-engineering trap" and Anti-pattern 2 naming the
  "the API is agentic by default" framing as the exact overtriggering risk
  (SKILL.md:207-214). Keeping `agent-architecture` out of a "support chatbot" is
  the correct answer and the one most agents would get wrong.
- **Security composition is genuinely complete.** `rag-engineering`'s
  authorize-inside-the-retrieval-query rule (SKILL.md:61-77, DF#4) is grounded in
  two independent OWASP entries and is directly load-bearing here, because a
  product-documentation corpus is very often part-internal. Its embedding-store
  sensitivity rule (DF#5, with the 92%-inversion evidence) is the kind of claim
  most guidance omits entirely. Retrieved chunks are correctly typed as an
  indirect-prompt-injection surface (DF#7) and handed to `SK-AI-008`, whose
  facet S-Gate 4 makes **mandatory**, not optional. Nothing in this chain is
  hand-waved.
- **`related_skills` fan-out behaves.** `llm-application-engineering` is
  `context-audit.md`'s C-01 worst case — 8 related skills, ~36K tokens if "related"
  were read as "load." The composed trace shows the intended behaviour actually
  occurring: the decision framework evaluates eight and selects six. This is
  evidence *for* C-01's recommended CS-9 rather than against it — the correct
  behaviour happens because `SK-AI-001`'s body says "selectively," not because a
  routing rule requires it.
- **T-Gate 5 is correctly distinct from T-Gate 4.** The library understands that
  LLM acceptance is an eval loop over non-deterministic output rather than a
  boolean suite, states the boundary structurally rather than as a matter of
  degree (`llm-evaluation/SKILL.md:17-28`), and routes suite mechanics back to
  `SK-QA-001` without restating them.

---

## Score

| # | Dimension | Score | Note |
|---|---|---|---|
| 1 | Skill routing | **3 / 5** | Six AI skills selected correctly and `agent-architecture` correctly declined; −2 for A-01, which excludes a skill the task requires and creates a routing cycle. |
| 2 | Dependency activation | **4 / 5** | Workflow #10's sequencing is right, and `depends_on_skills: []` across the AI cluster is the correct call (composition here is selective, not hard). −1 for A-01's broken handoff edge. |
| 3 | Context efficiency | **4 / 5** | Six of eight AI bodies for a project-complexity AI feature is proportional, and the selective-composition mechanism demonstrably works. |
| 4 | Implementation quality | **2 / 5** | The single most concretely-stated feature requirement is unaddressed by any skill (A-02), and the eval harness will not measure it. |
| 5 | Security | **5 / 5** | The strongest dimension in this entire Step 32 evaluation. Authorization ordering, embedding-store sensitivity, indirect injection, mandatory `SK-AI-008` facet, PII scrubbing at capture. |
| 6 | Testing | **4 / 5** | T-Gate 5, the eval loop, golden-set design, grading-method selection, the different-grader-model rule, the regression gate — all correct. −1 for the missing out-of-corpus case class (A-02). |
| 7 | Maintainability | **5 / 5** | Explicit anti-over-composition; the simplest-viable branch is stated as real; `model-selection` and `llm-evaluation` both refuse to calcify volatile facts. |
| 8 | Error handling | **2 / 5** | A-02's missing low-recall branch *is* a runtime failure branch; A-03's missing gate leaves a cost/data action ungated. Both are the composed chain's blind spots. |
| 9 | Repository convention adherence | **4 / 5** | ST-5 conventions travel; the markdown corpus is consumed, not rewritten; commit/PR conventions attach correctly. |
| 10 | Final outcome | **3 / 5** | A secure, evaluable, well-scoped RAG pipeline — that answers out-of-corpus questions confidently, never escalates to a human, and never asks permission to spend money or send customer data to a vendor. |
| | **Total** | **36 / 50** | |

**One-line verdict.** The library builds this feature **safely and does not build
the feature that was asked for**: the security and evaluation composition is the
best in the corpus, and the one requirement the user spelled out — "fallback to
human support for anything it's not confident about" — has no owner in 86 skills.

**Did the composed view expose something Step 28's isolated review could not?**
Yes, three times. A-01 (a cycle is only visible with three skills in hand), A-02
(no individual skill is deficient against its own scope — the gap exists *between*
four correct skills), and A-03 (a gate declared in `core/` with no skill
counterpart, which also corrects a Step 29 verification). All three are
structurally invisible to a per-skill review.

---

## Proposed regression scenarios

| ID | Name | Category | Covers | Already covered? |
|---|---|---|---|---|
| `S19` | rag-support-chatbot-human-fallback | Multi-skill tasks | A-01, A-02, A-03, A-05 | **No** — `S08-refund-agent-tool-access` is the only AI scenario and covers tool authority, not retrieval or answer confidence |
| — | `rag-engineering` hosted-retrieval surface | *(regression-suite trigger, not a scenario)* | A-04 | **No** — add as a re-verification trigger in `evaluations/regression-suite.md` |
