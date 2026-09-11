---
name: LLM Evaluation
description: >-
  Build eval harnesses for LLM features and mitigate hallucination: design
  specific, measurable, achievable success criteria; pick a grading method
  matched to the task (exact-match, semantic-similarity/ROUGE, or
  LLM-as-judge with a different grader model). Maintain golden test cases;
  gate ship-readiness on eval regressions. Use when building/reviewing an
  LLM feature needing quality verification, or investigating suspected
  hallucination. Not general test authoring — route to testing-strategy.
spec_version: "1.0"
---

## Purpose & scope

Build evaluation harnesses for LLM-powered features and detect/mitigate
hallucination — provider- and platform-neutral. **The boundary against
[testing-strategy](../testing-strategy/SKILL.md) (SK-QA-001) is
structural, not a matter of degree**: general test authoring asserts a
deterministic output true or false (does the function return the right
value, does the endpoint return the right status code); LLM output is
instead *graded* against success criteria, because the same prompt can
produce many different fluent, plausible-looking, non-identical correct
(or incorrect) answers. That's why grading-method selection is this
skill's own owned knowledge rather than an extension of general testing
method. This skill ties back to SK-QA-001 for everything around the eval
itself — fixture design, CI gating, suite structure — rather than
restating it.

## When to use / When not to use

**Use** when building or reviewing an LLM feature that needs quality
verification before shipping, when a feature is exhibiting suspected
hallucination, or when a prompt/model change needs a regression gate
before shipping. **Do not use** for general (non-LLM-output) test
authoring — route to [testing-strategy](../testing-strategy/SKILL.md) — or
for output that is deterministic/non-generative and needs no grading
judgment.

## Knowledge

**Good success criteria share four documented properties.** Anthropic's
own guidance: criteria should be **specific** ("Instead of 'good
performance,' specify 'accurate sentiment classification'"),
**measurable** (quantitative metrics, or "well-defined qualitative
scales... consistently applied *along with* quantitative measures"),
**achievable** ("Your success metrics should not be unrealistic to
current frontier model capabilities"), and **relevant** ("Strong citation
accuracy might be critical for medical apps but less so for casual
chatbots") [Source: platform.claude.com/docs/en/test-and-evaluate/
develop-tests]. The same source documents eval-dimension categories worth
checking against explicitly rather than reflexively grading only
"correctness": task fidelity, consistency, relevance and coherence, tone
and style, privacy preservation, context utilization, latency, and price.

**Grading-method selection is task-shape-dependent, and the source
documents four methods with worked code**, not just one default:
**exact match** for categorical tasks (e.g. sentiment classification);
**cosine similarity** (SBERT sentence embeddings) for semantic
consistency; **ROUGE-L** — "the length of the longest common subsequence
between the candidate and reference summaries" — for summarization
relevance/coherence; and **LLM-based grading** (Likert scales, binary
classification, ordinal scales) for subjective criteria that resist a
fixed reference answer [Source: platform.claude.com/docs/en/
test-and-evaluate/develop-tests]. The explicit best practice attached to
the last method: "Generally best practice to use a different model to
evaluate than the model used to generate the evaluated output" — grading
with the same model risks the model rating its own blind spots as fine.
The same source also states a deliberately counterintuitive stance worth
carrying into golden-set design: "**Prioritize volume over quality**: More
questions with slightly lower signal automated grading is better than
fewer questions with high-quality human hand-graded evals" — and to
"design evals that mirror your real-world task distribution," explicitly
factoring in edge cases, structuring questions so they're gradable
automatically (multiple-choice, string match, code-graded, LLM-graded).

**Gating prompt/model changes behind eval checks before shipping is
documented discipline independent of any one platform.** OpenAI's guidance
states the general rule plainly: "add representative fixtures, tests, and
evaluation checks before changing production prompts" — prompt changes go
through the same test-before-ship discipline as code changes
[Source: developers.openai.com/api/docs/guides/prompt-engineering]. OpenAI
also documents a three-step eval workflow — describe the expected
behavior as an eval, run it against test inputs, analyze results and
iterate — structured as BDD-like (specify → implement → test) rather than
write-then-verify [Source: developers.openai.com/api/docs/guides/evals].
**Treat this as the documented pattern, not a specific tool
recommendation**: OpenAI's own Evals platform is itself being deprecated
— read-only by October 31, 2026, full shutdown by November 30, 2026 — with
docs pointing toward a Datasets feature whose API surface this research
did not independently verify [Source: developers.openai.com/api/docs/
deprecations]. Build the eval-before-ship habit; don't anchor the
implementation on a platform mid-sunset.

**Hallucination mitigation is a named, standard-documented risk category,
not an informal concern.** OWASP's LLM Top 10 (2026) defines
Misinformation as incorrect, incomplete, unsupported, or misleading
output that "appears credible," driven by hallucination, weak grounding,
overreliance on fluent/confident output, and "embedded trust in agentic
architectures without verification." The documented mitigation center of
gravity is verification-before-action: "Require outputs to be grounded in
authoritative and current sources," separate generation from execution via
claim-verification workflows, and validate tool-call arguments,
authorization, and preconditions/state independently of the model's own
assertions — plus logging "claims, evidence, and outcomes" to test
adversarial scenarios continuously [Source: OWASP LLM Top 10 (2026),
LLM07:2026 — Misinformation]. The standard names concrete scenario
categories worth checking a feature against directly: hallucinated
software dependencies, safety-critical omissions, false automation
triggers, cross-agent trust failures, and fabricated task-completion
reports in agentic pipelines.

## Decision framework

1. **What does "correct" mean for this feature, concretely?** Write
   success criteria that are specific, measurable, achievable, and
   relevant to the feature's actual stakes (per Knowledge above) — not a
   vague "good performance" bar, and not a bar unrealistic for current
   model capability.
2. **What shape is the task's correct answer?** A fixed categorical
   label → exact match. A semantically-equivalent-but-not-identical
   answer (paraphrase, summary) → cosine similarity or ROUGE-L. A
   subjective quality judgment (tone, helpfulness, coherence) with no
   single reference answer → LLM-as-judge, graded by a different model
   than the one generating the output under test.
3. **Do you have enough test cases, and do they mirror the real task
   distribution?** Prioritize volume of automatically-graded cases over a
   small hand-graded set; include edge cases deliberately rather than only
   the easy path.
4. **Does the feature's output get acted on (by a human or another
   agent/tool) without independent verification?** If so, that's where
   hallucination risk actually bites — design a claim-verification step
   (require grounding in authoritative/current sources; validate tool-call
   arguments/preconditions independently of the model's own assertions)
   rather than trusting fluent output.
5. **Is a prompt or model change about to ship without a regression
   check?** Gate it behind the eval suite first — the same test-before-ship
   discipline as any other production code change.
6. **Is this actually a general (non-LLM-output) testing question?** If
   the output under test is deterministic and needs no grading judgment,
   this is [testing-strategy](../testing-strategy/SKILL.md)'s scope, not
   this skill's.

## Workflow

1. Define success criteria for the feature: specific, measurable,
   achievable, relevant — pick the eval dimensions that actually matter
   (task fidelity, consistency, relevance/coherence, tone/style, privacy
   preservation, context utilization, latency, price).
2. Choose the grading method matched to the task shape (exact-match /
   cosine-similarity / ROUGE-L / LLM-as-judge); if LLM-as-judge, use a
   different model to grade than to generate.
3. Build or extend a golden test-case set that mirrors the real task
   distribution, including edge cases, prioritizing volume of
   automatically-graded cases.
4. Design hallucination-mitigation checks: grounding requirements, and a
   claim-verification step before any agentic action executes on the
   model's own assertions.
5. Wire the eval suite as a regression gate before shipping prompt or
   model changes.
6. Hand off fixture/CI-structure mechanics to
   [testing-strategy](../testing-strategy/SKILL.md) rather than
   reinventing them here.

## Engineering rules

- Write success criteria that are specific, measurable, achievable, and
  relevant — never a vague "good performance" bar.
- Match the grading method to the task shape; don't default to LLM-as-
  judge for a categorical task that exact-match already grades cheaply
  and deterministically.
- When using LLM-as-judge, grade with a different model than the one that
  generated the output under test.
- Prioritize volume of automatically-graded test cases over a small
  hand-graded set; mirror the real task distribution, including edge
  cases.
- Require grounding in authoritative/current sources and verify claims/
  tool-call arguments independently before an agent acts on them — never
  trust fluent output as a proxy for correct output.
- Gate prompt/model changes behind the eval suite before shipping, the
  same discipline as any other production code change.

## Trade-offs

Exact-match and embedding-similarity grading are cheap, deterministic,
and scale to large test-case volumes, but can't judge subjective quality
(tone, helpfulness) at all. LLM-as-judge grading covers subjective
criteria that no fixed reference answer can, at the cost of its own
noise/bias and added inference cost — mitigated, not eliminated, by
grading with a different model than the generator. A larger volume of
automatically-graded, slightly-lower-signal test cases is explicitly
favored over a small hand-graded set (per Anthropic's stated best
practice) because volume catches more of the real task distribution;
hand-grading a small set is higher-signal per case but risks missing
whole failure modes the small sample never exercises.

## Anti-patterns

- **Vague success criteria** ("the model should respond well") that give
  the grading method nothing measurable to check.
- **Using the same model to generate and to grade** — a documented
  best-practice violation that risks the model rating its own blind spots
  as acceptable.
- **Grading everything with LLM-as-judge by default** — the
  over-engineering trap for this domain: many tasks have a fixed correct
  answer that exact-match or ROUGE-L grades more cheaply and
  deterministically, with no judge-model noise at all.
- **Trusting fluent, confident output as a proxy for correct output**
  without a grounding or claim-verification step — the core mechanism
  OWASP's Misinformation entry names as driving hallucination-based harm.
- **Anchoring new eval-harness work on OpenAI's Evals platform
  specifically** — it is documented as being deprecated (read-only Oct 31
  2026, shutdown Nov 30 2026); use the documented workflow pattern with
  current tooling instead.
- **Treating this skill's scope as covering general (non-LLM-output) test
  authoring** — route that to
  [testing-strategy](../testing-strategy/SKILL.md).

## Security

Hallucination mitigation shades directly into security when unverified
LLM output triggers a real-world action: validating tool-call arguments,
authorization, and preconditions independently of the model's own
assertions (per OWASP LLM07:2026) is this skill's own content above.
Broader LLM-specific threat classes (prompt injection, excessive agency)
are owned by the AI-security skill in this domain, not restated here.

## Testing

This skill *is* the LLM-output-grading and hallucination-mitigation
method — see Knowledge and Decision framework above for its own content.
Surrounding test-suite structure, fixture design, and CI gating are owned
by [testing-strategy](../testing-strategy/SKILL.md); defer to it rather
than reinventing suite mechanics here.

## Failure handling

- If the feature's behavioral requirements aren't stated, ask what
  "correct" output looks like before proposing success criteria rather
  than inventing them.
- If asked to build the eval on OpenAI's Evals platform specifically,
  flag that it is being deprecated (read-only Oct 31 2026, shutdown Nov
  30 2026) and frame guidance as the documented pattern (describe the
  task, run test inputs, analyze/iterate), implementation-tool-agnostic,
  rather than recommending `v1/evals` for new work.
- If the request is actually general (non-LLM-output) test authoring,
  route to [testing-strategy](../testing-strategy/SKILL.md) rather than
  answering as if it were LLM-specific grading.

## Escalation

- A request for general (non-LLM-output) test-suite/CI discipline exceeds
  this skill's scope — defer to
  [testing-strategy](../testing-strategy/SKILL.md).

## Outputs & verification

- **Outputs:** an eval-harness design (success criteria, grading method,
  golden test cases) and hallucination-mitigation checks (grounding
  requirements, claim verification before an agent acts).
- **Verify:** success criteria are specific/measurable/achievable/
  relevant; the grading method matches the task type, with a different
  grading model than generating model when LLM-as-judge is used;
  hallucination-mitigation checks require grounding rather than trusting
  fluent-but-unverified output.

## References

- [research/technologies/anthropic-claude-api.md](../../research/technologies/anthropic-claude-api.md)
- [research/technologies/openai-api.md](../../research/technologies/openai-api.md)
- [research/technologies/owasp-llm-top10.md](../../research/technologies/owasp-llm-top10.md)
- [llm-application-engineering](../llm-application-engineering/SKILL.md)
- [testing-strategy](../testing-strategy/SKILL.md)
- [model-selection](../model-selection/SKILL.md)
