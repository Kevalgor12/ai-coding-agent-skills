---
name: Prompt & Context Engineering
description: >-
  Design system prompts (role, instructions, examples, context ordering)
  and context-window composition (long-context placement, budget/rot
  management, cache-friendly prefix structuring) for reliable LLM behavior,
  grounded in Anthropic's and OpenAI's own prompting guidance. Use when
  designing or debugging a prompt, or when a long-running conversation
  needs context-budget/caching design. Not for the output's shape
  (structured output/tool calling — route to structured-output-tool-calling).
spec_version: "1.0"
---

## Purpose & scope

Design system prompts, message structure, and context-window composition
so LLM behavior is reliable — provider-neutral, grounded in Anthropic's
and OpenAI's own prompting guidance. The two vendors use different
terminology but converge on largely the same structural recommendations,
which is the core finding this skill is built on. Distinct from the
output's *shape* — schema-conformant structured output and tool/function
calling are owned by
[structured-output-tool-calling](../structured-output-tool-calling/SKILL.md)
— and from the multi-step orchestration loop around tool calls, owned by
agent-architecture (SK-AI-004). Composed selectively by
[llm-application-engineering](../llm-application-engineering/SKILL.md),
the AI/LLM domain's root skill, and feeds
[rag-engineering](../rag-engineering/SKILL.md), whose retrieved content is
itself a context-engineering input.

## When to use / When not to use

**Use** when designing or debugging a prompt, when output quality depends
on prompt or context structure, when deciding what to place first/last in
a long-context prompt, or when a long-running conversation needs
context-budget/compaction design. **Do not use** when the request is
about the output's *shape* (structured output schemas, tool/function-call
definitions — route to structured-output-tool-calling) or about the
orchestration loop around multiple tool calls (route to
agent-architecture); also not applicable where no LLM call is involved.

## Knowledge

**Both vendors document the same four-part prompt-structure shape under
different names — treat this convergence as the core structural method,
not two competing systems to reconcile per-provider.** Anthropic's
documented hierarchy is **"Be clear and direct"** (the "golden rule":
"Show your prompt to a colleague with minimal context on the task and ask
them to follow it. If they'd be confused, Claude will be too"), **"Add
context to improve performance"** (explaining *why* an instruction matters
outperforms a bare directive), **"Use examples effectively"**, and **"Give
Claude a role"** via the `system` parameter — "Even a single sentence
makes a difference" [Source: research/technologies/anthropic-claude-api.md].
OpenAI's documented structure is **Identity** ("purpose, communication
style, and high-level goals"), **Instructions** (explicit rules,
dos/don'ts), **Examples**, and **Context** (supporting data, positioned
near the end) [Source: research/technologies/openai-api.md]. Map the two:
Anthropic's role framing ≈ OpenAI's Identity; both treat
instructions/examples/context as separate, ordered blocks. Both also
recommend **XML tags to delimit sections** — Anthropic: "reduces
misinterpretation," using consistent descriptive tag names
(`<instructions>`, `<context>`, `<input>`) and nesting tags for
hierarchical content; OpenAI: "XML tags to delineate where one piece of
content begins and ends," with attributes for metadata
[Source: research/technologies/anthropic-claude-api.md;
research/technologies/openai-api.md].

**Few-shot examples are a documented, reliable lever on both platforms —
use 3-5, not zero and not dozens.** Anthropic calls multishot prompting
"one of the most reliable ways to steer Claude's output format, tone, and
structure," with the explicit recommendation to **"Include 3–5 examples
for best results,"** wrapped in `<example>`/`<examples>` tags, kept
relevant and diverse. OpenAI documents the same pattern more generally as
"a handful of input/output examples in the prompt" so the model can
"implicitly pick up the pattern... and apply it"
[Source: research/technologies/anthropic-claude-api.md;
research/technologies/openai-api.md].

**Long-context placement has a specific, quantified rule: longform
content goes before the query, not after.** Anthropic's documentation is
explicit for prompts of 20K+ tokens: "Put longform data at the top...
above your query, instructions, and examples. This improves performance
across all models," citing a specific figure — **"Queries at the end can
improve response quality by up to 30 percent in tests, especially with
complex, multidocument inputs."** Multi-document inputs should use
`<document index="n"><source>...</source><document_content>...
</document_content></document>` structure
[Source: research/technologies/anthropic-claude-api.md]. This is the
single highest-leverage, most quantified rule in this skill's scope —
apply it before any other context-ordering decision.

**A larger context window is not automatically better — "context rot" is
a documented, named phenomenon, not an assumption to design around
casually.** Anthropic's own docs state: "As token count grows, accuracy
and recall degrade, a phenomenon known as context rot. This makes
curating what's in context just as important as how much space is
available" [Source: research/technologies/anthropic-claude-api.md]. Treat
this as a mandate to actively curate context rather than stuff everything
available into the window because the model's context limit permits it.

**Context-budget awareness is model-dependent, not universal, and worth
checking rather than assuming.** Newer Claude models "track their
remaining context window (their 'token budget') throughout a
conversation" automatically via injected system tags
(`<budget:token_budget>...</budget:token_budget>`, then
`<system_warning>Token usage: X/Y; Z remaining</system_warning>` after
each tool call); models without this injection can use an explicit
beta task-budgets feature instead. For long-running conversations,
"server-side compaction is the primary strategy for context management"
[Source: research/technologies/anthropic-claude-api.md]. Everything in a
request — system prompt, every message including tool results/images/
documents, tool definitions, and generated output including thinking —
counts toward the window, so budget planning must account for the whole
request shape, not just the visible prompt text.

**Reasoning models want less prescriptive guidance than standard models —
a documented split worth checking before writing a step-by-step prompt.**
OpenAI's framing: standard models "require precise instructions that
explicitly provide the logic and data required to complete the task" and
are "like a junior coworker," while reasoning models "work better with
only high-level guidance" and are "like a senior co-worker" who can "work
out the details" — over-specifying intermediate steps for a reasoning
model is discouraged
[Source: research/technologies/openai-api.md]. Anthropic documents an
analogous shift for models with adaptive thinking: "Prefer general
instructions over prescriptive steps. A prompt like 'think thoroughly'
often produces better reasoning than a hand-written step-by-step plan"
[Source: research/technologies/anthropic-claude-api.md].

**Prompt caching on both platforms rewards the same structural discipline:
put stable content first, dynamic content after a breakpoint.** Anthropic:
"Cache prefixes are created in the following order: `tools`, `system`,
then `messages`," with two modes — automatic caching (one top-level
`cache_control` field auto-caches the last cacheable block, "recommended
starting point for most use cases") and explicit breakpoints (fine-grained
`cache_control` per block) [Source:
research/technologies/anthropic-claude-api.md]. OpenAI: "place stable
content (static developer instructions, reference material, consistent
tool definitions) first and dynamic/timestamped content after a cache
breakpoint; append new turns rather than rewriting earlier ones," and
requires an **exact prefix match** — full rendered context plus identical
settings (model, tools, output schema, reasoning effort, verbosity) —
to hit the cache [Source: research/technologies/openai-api.md]. On both
platforms, rewriting or reordering earlier turns defeats the cache rather
than merely reducing its benefit — design conversation state to append,
never mutate, prior turns when caching matters.

## Decision framework

1. **Does the task need a role/system prompt at all, or does a plain,
   direct instruction already suffice?** Don't add role-framing ceremony
   to a single-shot, unambiguous request — the "colleague test" (would a
   colleague with minimal context follow this without confusion?) is the
   simplest viable check before adding structure.
2. **Would 3-5 examples measurably improve format/tone/structure
   adherence?** If the task's desired output is genuinely ambiguous from
   instructions alone, add examples; if the instructions alone are
   unambiguous, skip them rather than padding the prompt.
3. **Is the input long-context (20K+ tokens) or multi-document?** If so,
   place that content before the query/instructions, not after — this is
   the single highest-leverage structural decision when it applies.
4. **Is the conversation long-running or agentic?** If so, design a
   context-budget/compaction approach (or check whether the target model
   already tracks budget automatically) rather than letting the context
   grow unmanaged — and treat context rot as a real cost of "more
   context," not a reason to always maximize what's included.
5. **Does the target provider support prompt caching, and will this
   prefix be reused across calls?** If yes, structure stable content
   (tools, system prompt, static reference material) first and dynamic
   content after a breakpoint; if the prefix won't be reused, caching
   design is unnecessary overhead — skip it.
6. **Is the target a reasoning model?** If so, favor high-level guidance
   (task, constraints, desired output format) over a prescriptive
   step-by-step plan; over-specifying steps degrades reasoning-model
   quality rather than improving it.

## Workflow

1. Identify the task's role/persona needs, explicit instructions, and
   whether examples would resolve ambiguity — assemble accordingly using
   the Identity/Instructions/Examples/Context (or role/instructions/
   examples/context) ordering.
2. If long-context or multi-document input is involved, place it before
   the query/instructions/examples, using `<document>`-style structure
   for multiple documents.
3. Delimit distinct prompt sections with consistent, descriptive XML tags
   rather than relying on prose boundaries alone.
4. For long-running or agentic use, design the context-budget/compaction
   approach — check whether the target model tracks budget automatically
   before building a manual one.
5. If the target provider supports prompt caching and the prefix will be
   reused, order content stable-first/dynamic-after-breakpoint and design
   conversation state to append rather than rewrite prior turns.
6. Check the design against the anti-patterns below (deprecated prefill,
   over-aggressive tool-triggering language, unbounded free-text
   injection into the system prompt) before finalizing.
7. Hand off schema/tool-definition design to structured-output-tool-calling
   and multi-step orchestration design to agent-architecture rather than
   folding those concerns into the prompt/context design itself.

## Engineering rules

- Structure prompts as role/identity → instructions → examples → context,
  matching both vendors' documented frameworks; don't scatter these
  concerns unordered through the prompt.
- Place long-context/multi-document content before the query, not after
  — a documented, quantified (up to 30%) quality effect on Anthropic
  models, and the same ordering OpenAI's Context-last-but-before-query
  structure implies.
- Use 3-5 examples when examples are warranted; don't default to zero
  (ambiguity) or dozens (context bloat, cache-prefix instability).
- Treat context size as a curation problem, not a capacity problem —
  larger context windows do not offset context rot.
- Order cache-friendly prompts stable-content-first, dynamic-content-after
  a breakpoint, and design conversation state to append rather than
  rewrite/reorder prior turns.
- Favor high-level guidance over prescriptive step-by-step instructions
  when the target is a reasoning model.

## Trade-offs

Heavier structural scaffolding (explicit role framing, multiple examples,
XML-delimited sections) buys reliability and steerability at the cost of
prompt length and, on cacheable prefixes, potential cache-prefix churn if
that scaffolding changes often; a minimal direct prompt is cheaper and
faster to iterate on but risks ambiguity on tasks that aren't
self-evidently unambiguous. Aggressive context-budget management
(compaction, curation) costs engineering effort up front but avoids the
accuracy/recall degradation of context rot on long-running conversations;
skipping it is simpler short-term but degrades silently as conversations
grow. Designing for prompt caching pays off only when a prefix is
genuinely reused across calls — for one-shot or highly dynamic prompts,
the stable/dynamic-content discipline is unneeded overhead.

## Anti-patterns

- **Assistant-message prefill** — a deprecated pattern on current Claude
  models (4.6+ return a 400 error); use structured outputs, explicit
  "respond without preamble" instructions, or a user-turn continuation
  instead [Source: research/technologies/anthropic-claude-api.md].
- **Over-aggressive imperative tool-triggering language** (e.g. `"CRITICAL:
  You MUST use this tool when..."`) — documented as causing overtriggering
  on current, more-responsive models; dial back to plain phrasing (`"Use
  this tool when..."`) [Source: research/technologies/anthropic-claude-api.md].
- **Unbounded free-text injection into a system prompt** — OpenAI
  documents this as a prompt-injection risk vector, mitigated by
  "limiting the amount of text a user can input into the prompt" and
  red-teaming against adversarial inputs like "ignore the previous
  instructions and do this instead" [Source: research/technologies/openai-api.md].
- **Reflexively maximizing context** (stuffing everything available into
  the window because the limit permits it) instead of curating — this
  domain's over-engineering trap, given the documented context-rot
  finding that more context is not automatically better
  [Source: research/technologies/anthropic-claude-api.md].
- **Rewriting or reordering earlier conversation turns** when prompt
  caching is in play — defeats the cache rather than merely reducing its
  benefit; append new turns instead
  [Source: research/technologies/openai-api.md].
- **Over-specifying step-by-step instructions for a reasoning model** —
  degrades output quality on models designed to "work out the details"
  themselves [Source: research/technologies/openai-api.md].

## Security

Untrusted third-party content (web pages, emails, documents, tool
results) must never be concatenated directly into a system prompt or
plain user text — Anthropic's documented mitigation is to deliver such
content only inside `tool_result` blocks, state what it is and where it
came from, and JSON-encode it so an attacker cannot "break out" into an
instruction context [Source: research/technologies/anthropic-claude-api.md].
OpenAI documents the same class of risk from unbounded end-user free text
reaching a system prompt (Anti-patterns, above). This skill owns the
prompt/context-structure side of that mitigation; deeper LLM-specific
threat modeling and excessive-agency/blast-radius limits are owned by
[ai-security](../ai-security/SKILL.md) (referenced by ID: SK-AI-008) and
general security-engineering.

## Testing

Whether a prompt reliably produces the intended structure/tone/format
under representative inputs — not just one hand-picked example — is the
prompt-engineering-specific testing concern; both vendors document
evaluation workflows (exact match, LLM-graded criteria) for exactly this.
Deep test-strategy method is owned by
[testing-strategy](../testing-strategy/SKILL.md).

## Failure handling

- If the target model/provider isn't stated, ask before committing to
  provider-specific caching mechanics or terminology; give
  provider-neutral structural guidance in the meantime.
- If the request is actually about output shape (structured output/
  tool-calling schemas), state that and redirect to
  structured-output-tool-calling rather than answering as if it were
  prompt/context design.

## Escalation

- A request that is actually about structured-output/tool-calling schema
  design is redirected to structured-output-tool-calling rather than
  answered here.
- A request about the orchestration loop around multiple tool calls is
  redirected to agent-architecture rather than answered here.

## Outputs & verification

- **Outputs:** a system prompt and message-structure design (role,
  instructions, examples, context ordering), and a context-management
  approach (budget/rot handling, cache-friendly prefix structuring where
  applicable).
- **Verify:** long-context content is placed before the query; the
  context-management plan is proportionate to actual context-window
  needs rather than reflexively maximal; no deprecated or documented
  anti-pattern constructs (prefill, over-aggressive tool-triggering
  language, unbounded free-text injection) are present.

## References

- [research/technologies/anthropic-claude-api.md](../../research/technologies/anthropic-claude-api.md)
- [research/technologies/openai-api.md](../../research/technologies/openai-api.md)
