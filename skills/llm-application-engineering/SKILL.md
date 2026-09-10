---
name: LLM Application Engineering
description: >-
  Decide which AI/LLM disciplines a feature needs — prompt/context
  engineering, structured output/tool calling, agent architecture, RAG,
  model selection, evaluation, AI security — and how they compose; own the
  LLM-call observability plan (prompt/completion logging with secret/PII
  scrubbing, token/cost/latency tracking) as a lightweight extension of
  general observability. Use when starting a new LLM-powered feature and
  deciding its overall shape before implementation.
spec_version: "1.0"
---

## Purpose & scope

Decide the architecture of an LLM-powered feature — which AI/LLM
disciplines apply and how they compose — and own lightweight LLM-call
observability. This is the AI/LLM domain's root skill: it composes
[prompt-context-engineering](../prompt-context-engineering/SKILL.md),
[structured-output-tool-calling](../structured-output-tool-calling/SKILL.md),
[agent-architecture](../agent-architecture/SKILL.md),
[rag-engineering](../rag-engineering/SKILL.md),
[model-selection](../model-selection/SKILL.md),
[llm-evaluation](../llm-evaluation/SKILL.md), and
[ai-security](../ai-security/SKILL.md) selectively rather than
reimplementing them, and has no dominant single LLM-provider technology to
specialize into — model selection is itself the vendor-neutral decision
layer, grounded in both Anthropic's and OpenAI's documented guidance.
LLM-call observability (prompt/completion logging, token/cost tracking,
per-call latency) is owned here as a lightweight extension of
[observability](../observability/SKILL.md), not as a separate skill:
research into both vendors' documentation found no LLM-specific
observability concern deep enough to warrant a ninth AI-domain skill.

## When to use / When not to use

**Use** when starting a new LLM-powered feature, or deciding its overall
shape before implementation. **Do not use** when there's no LLM in the
feature, when the request is already scoped to one specific sub-discipline
(route directly to the matching skill above), or when the observability
need is general application observability with nothing LLM-call-specific
about it (route to [observability](../observability/SKILL.md) directly).

## Knowledge

**Both researched vendors document more than one way to build the
"loop" layer, and which one applies is the first fork in the composition
decision.** Anthropic documents four distinct build-time options with
explicit "when to use" guidance: the **Messages API/client SDK** ("Calling
the API directly and implementing the tool loop yourself"), the **Claude
Agent SDK** ("Building an agent without implementing the tool loop
yourself" — gives "the same tools, agent loop, and context management that
power Claude Code," Python/TypeScript only), the **Claude Code CLI**
("interactive development or... one-off tasks from a terminal"), and
**Managed Agents** ("Running long-running or asynchronous agents without
managing your own sandbox or session infrastructure" — Anthropic runs the
agent and the sandbox) [Source: code.claude.com/docs/en/agent-sdk/overview;
platform.claude.com/docs/en/managed-agents/overview]. OpenAI's Responses
API is documented as **"agentic by default"**: "a single API call can let
the model invoke multiple tools — web search, file search, code
interpreter, computer use, remote MCP servers, and custom functions — in
the course of producing one response," with a separate **Agents SDK**
reserved for when "the SDK [should] manage the agent loop and recurring
orchestration such as repeated tool calls or branching," versus the raw
Responses API when the application needs "direct loop control and custom
routing logic" instead [Source: developers.openai.com/api/docs/guides/
migrate-to-responses; developers.openai.com/api/docs/guides/agents]. This
fork is exactly the signal for whether [agent-architecture]
(../agent-architecture/SKILL.md) applies at all, or whether a single
[structured-output-tool-calling](../structured-output-tool-calling/SKILL.md)
call is the whole feature.

**Both vendors independently warn against over-reaching for multi-step
orchestration.** Anthropic's own prompting guidance notes that current
models "recognize when tasks would benefit from delegating work to
specialized subagents and do so proactively," but cautions they "may spawn
them in situations where a simpler, direct approach would suffice"
[Source: platform.claude.com/docs/en/build-with-claude/
prompt-engineering/claude-prompting-best-practices]. This is the same
overreach this skill's own over-engineering check exists to catch —
reaching for agent-architecture or RAG composition before confirming the
feature actually needs multi-step autonomy or corpus grounding.

**Model-tier selection has a documented default-then-escalate pattern on
both platforms, which is the input SK-AI-006 needs from this skill's
composition decision.** Anthropic: "If you're unsure which model to use,
start with Claude Opus 5 for most workloads. Use Claude Fable 5.1 for
demanding reasoning and long-horizon agentic work, or when your evals on
Claude Opus 5 at higher effort still fall short" [Source:
platform.claude.com/docs/en/models/overview]. OpenAI's `reasoning.effort`
parameter documents an analogous escalation ladder (`none`/`low`/`medium`
default/`high`/`xhigh`/`max`), and its model lineup is itself tiered by
task weight — `gpt-6-astra` ("our most capable model, built for the
hardest end-to-end work") down through `gpt-5.6-sol` ("complex
professional work"), `gpt-5.6-terra` ("balances performance and cost
efficiency"), and `gpt-5.6-luna` ("optimized for cost-sensitive
applications") [Source: developers.openai.com/api/docs/guides/reasoning;
developers.openai.com/api/docs/models]. This skill doesn't make the model
choice itself — it flags that the feature needs one and hands off to
model-selection.

**LLM-call observability is a genuinely different logging surface than
typical application logs, which is why it's an extension of SK-QA-004
rather than something SK-QA-004 already covers by default.** A prompt or
completion routinely carries full free-text user input, retrieved
documents, and tool-call arguments — a richer, higher-risk surface for
secret/PII leakage than a typical structured log line. Both vendors
document the token-usage fields this observability plan should capture
for cost tracking: Anthropic's streaming `usage` field in `message_delta`
events is explicitly "*cumulative*" per turn [Source:
platform.claude.com/docs/en/build-with-claude/streaming], and every
response carries a `request-id` header for correlating a specific call
with logs/support [Source: platform.claude.com/docs/en/api/rate-limits].
OpenAI exposes `usage.input_tokens_details.cached_tokens` and
`.cache_write_tokens` alongside a dedicated Prompt Caching Dashboard/
Diagnostics tool for understanding per-call cache behavior, and every
response carries an `x-request-id` header plus an optional caller-supplied
`X-Client-Request-Id` for the same correlation purpose [Source:
developers.openai.com/api/docs/guides/prompt-caching;
developers.openai.com/api/reference/overview]. Neither vendor documents a
first-class "redact this field before logging" API knob — scrubbing is an
application-side discipline in both doc sets, which is exactly what this
skill's observability plan must design explicitly rather than assume.

## Decision framework

Walk this checklist against the feature requirement; compose only the
sub-disciplines with a genuine signal, and state which ones were declined:

1. **Does output quality depend on prompt structure or context-window
   composition?** → [prompt-context-engineering](../prompt-context-engineering/SKILL.md).
2. **Does the feature need schema-conformant output, or a tool/function
   call?** → [structured-output-tool-calling](../structured-output-tool-calling/SKILL.md).
   If this is the whole feature, stop here — do not add agent-architecture.
3. **Does the feature need the LLM to autonomously sequence multiple tool
   calls or sub-tasks across turns**, per the build-path fork above? →
   [agent-architecture](../agent-architecture/SKILL.md).
4. **Does the feature need output grounded in a specific retrievable
   corpus**, rather than the model's own knowledge? →
   [rag-engineering](../rag-engineering/SKILL.md).
5. **Is the model/provider/tier still open to choose?** →
   [model-selection](../model-selection/SKILL.md), applying the vendors'
   own default-then-escalate pattern rather than defaulting to the most
   capable/expensive tier.
6. **Does the feature need quality verification before shipping, or is
   hallucination suspected?** → [llm-evaluation](../llm-evaluation/SKILL.md).
7. **Does the feature have tool access, untrusted-content ingestion, or
   user-facing exposure that needs threat review?** →
   [ai-security](../ai-security/SKILL.md).
8. **Always**: design the LLM-call observability plan (this skill's own
   responsibility, not delegated) — see Knowledge above.

The simplest-viable branch is real: a feature that's one structured-output
call to a fixed model needs only step 2 (and maybe step 1) plus the
observability plan — not a full eight-skill composition.

## Workflow

1. Read the feature requirement; note what's already fixed (provider,
   model, existing prompts/tools) versus still open.
2. Walk the decision-framework checklist against each SK-AI-002–SK-AI-008
   signal.
3. For each sub-discipline that applies, record it and defer its detailed
   design to that skill — don't reimplement its content here.
4. Sequence the applicable sub-disciplines (model selection typically
   informs the others; context engineering underlies structured-output and
   agent design; agent-architecture builds on structured-output/tool
   calling).
5. Design the LLM-call observability plan: what to log per call (prompt,
   completion, tool arguments, token counts, latency, request ID), scrub
   proactively at the point of capture, and track cost via each vendor's
   documented usage fields.
6. State explicitly which sub-disciplines were declined and why, flagging
   any over-engineering signal before handing off.

## Engineering rules

- Only compose the sub-disciplines the feature's requirements actually
  signal for; state explicitly which ones were declined and why.
- Always produce the LLM-call observability plan, even when no other
  sub-discipline applies — every LLM call warrants a logging/cost/latency
  design, not just multi-step or tool-using ones.
- Scrub prompts, completions, tool arguments, and retrieved documents for
  secrets/PII at the point of capture, the same discipline SK-QA-004
  requires for general logs, extended to this richer free-text surface.
- Resolve the build-path fork (single call vs. agent loop, hand-rolled vs.
  managed framework) before routing to agent-architecture, using each
  vendor's own documented "when to use" criteria rather than a hunch.
- Treat model selection as a low-cost, vendor-neutral decision to resolve
  early, since it changes the assumptions the other sub-disciplines design
  against.

## Trade-offs

Composing every applicable sub-discipline up front costs more design time
than shipping a single structured-output call, but under-composing (e.g.
skipping model-selection or the observability plan because "it's just an
API call") defers cost/quality/security risk to production instead of
design time. The lightweight-extension choice for observability (folding
into SK-QA-004 rather than authoring a dedicated AI-observability skill)
trades some LLM-specific depth for avoiding a ninth skill's worth of
duplicated logging/alerting method that the research didn't find grounds
for.

## Anti-patterns

- **Reflexively composing every sub-discipline** (agent-architecture + RAG
  + a full eval harness) for a feature that's really a single
  structured-output call — the domain's specific over-engineering trap,
  named directly in this skill's own catalog responsibility.
- **Reaching for a "the API is agentic by default" framing** (or a
  managed-agent product) as a reason to add agent-architecture, without
  confirming the feature actually needs multi-step autonomous tool
  sequencing — both vendors document this exact overtriggering risk.
- **Skipping the LLM-call observability plan** because the feature is "just
  an API call" — token/cost/latency risk exists on every LLM call, not
  only multi-step or tool-using ones.
- **Logging raw prompts, completions, or tool arguments unscrubbed**,
  treating LLM-call logs as lower-risk than other application logs when
  they typically carry more free-text user/document content.
- **Deciding model tier from vendor marketing framing** rather than the
  documented default-then-escalate criteria, and defaulting to the most
  capable/expensive tier without checking whether the task needs it.

## Security

LLM-call logs are a trust-boundary surface: prompts, completions, and tool
arguments routinely carry user-supplied free text, retrieved documents,
and embedded content that can contain PII, secrets, or prompt-injection
payloads. Scrub proactively at the point of capture — this skill's own
observability-plan responsibility, extending SK-QA-004's general
discipline to this richer surface. Deep LLM-specific threat modeling
(prompt injection, excessive agency, retrieval-authorization risk) is
owned by [ai-security](../ai-security/SKILL.md); this skill flags when a
feature needs that review rather than reimplementing it.

## Performance

Token/cost/latency tracking is this skill's own performance-relevant
content for the LLM-call layer — see Knowledge above for the specific
usage/cache fields both vendors document. Broader cross-cutting
performance method is owned by
[performance-engineering](../performance-engineering/SKILL.md).

## Failure handling

- If the feature requirement doesn't state enough to determine which
  sub-disciplines apply, ask rather than composing all of them
  reflexively.
- If the request is already fully scoped to one specific sub-discipline,
  do not re-decide architecture here — hand off directly to the matching
  SK-AI-002–SK-AI-008 skill.

## Escalation

- A request already fully scoped to one SK-AI-002–SK-AI-008 sub-discipline
  is routed there directly rather than re-decided at the root.
- A request that is really general (non-LLM-call) observability, with
  nothing LLM-specific about it, is routed to
  [observability](../observability/SKILL.md) directly.

## Outputs & verification

- **Outputs:** an LLM feature architecture (which sub-disciplines apply,
  why, and in what sequence, including declined ones), and an LLM-call
  observability plan (what to log/measure and why).
- **Verify:** every included sub-discipline maps to a concrete signal in
  the requirement, not reflexive inclusion; declined sub-disciplines are
  stated explicitly; no unscrubbed secrets/PII appear in the observability
  plan's logging design.

## References

- [research/technologies/anthropic-claude-api.md](../../research/technologies/anthropic-claude-api.md)
- [research/technologies/openai-api.md](../../research/technologies/openai-api.md)
