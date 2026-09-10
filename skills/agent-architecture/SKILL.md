---
name: Agent Architecture
description: >-
  Architect multi-step, tool-using LLM agent loops — the orchestration layer
  above a single tool call. Covers agent-loop/termination design, conversation
  state-management strategy, hand-rolled-loop vs. managed-framework choice,
  and multi-agent composition (handoffs, subagents) where supported. Use when
  a feature needs an LLM to autonomously sequence multiple tool calls or
  sub-tasks. Not a single tool call (structured-output-tool-calling) or
  bounding agent authority/blast radius (ai-security).
spec_version: "1.0"
---

## Purpose & scope

Architect the orchestration layer above a single tool call: the loop that
lets an LLM autonomously sequence multiple tool calls or sub-tasks, the
state-management strategy that carries it across turns, and — where the task
genuinely warrants it — multi-agent composition. Provider-neutral across
Anthropic's and OpenAI's documented build paths. Distinct from
[structured-output-tool-calling](../structured-output-tool-calling/SKILL.md)
(a single tool call's schema and round trip) and from bounding what the
agent is authorized to do, which is [ai-security](../ai-security/SKILL.md)'s
job.

## When to use / When not to use

**Use** when a feature requires an LLM to autonomously sequence multiple
tool calls or sub-tasks: designing or reviewing a multi-step tool-execution
loop and its termination conditions, choosing between a hand-rolled loop and
a managed agent framework/runtime, choosing a conversation-state strategy
across agent turns, or designing multi-agent composition (handoffs,
subagents, agents-as-tools). **Do not use** when a single tool call or single
structured-output response would answer the need — route to
[structured-output-tool-calling](../structured-output-tool-calling/SKILL.md)
instead — or when the actual concern is restricting what the agent is
allowed to do (blast radius, permissions, excessive agency) — route to
[ai-security](../ai-security/SKILL.md).

## Knowledge

**Both vendors independently document the same core shape: a while-loop
keyed on a stop condition, invoked either by hand or by a runner.**
Anthropic's client-tool agentic loop is a five-step `while` loop keyed on
`stop_reason`: send `tools` plus the user message; Claude responds with
`stop_reason: "tool_use"` and one or more `tool_use` blocks; execute each
tool and format outputs as `tool_result` blocks; send a new request carrying
prior messages, the assistant's response, and the `tool_result` blocks; and
repeat while `stop_reason == "tool_use"`
[Source: research/technologies/anthropic-claude-api.md, §2]. OpenAI's Agents
SDK runner performs an analogous per-turn loop internally: "Call the current
agent's model with the prepared input" → "Inspect the model output" →
execute any tool calls and continue → switch agents if the model handed off
→ return once the run reaches "a final answer with no more tool work"
[Source: research/technologies/openai-api.md, §2]. The difference that
matters for architecture is *who writes the loop*: Anthropic's is the loop
you write yourself against the raw Messages API; OpenAI's is what its
Agents SDK's runner writes for you — the same control-vs-convenience split
both vendors draw explicitly (see Decision framework).

**Server-side loops exist independently of your own loop, and they have
documented iteration caps you must design around.** Anthropic's
server-executed tools (`web_search`, `code_execution`, and others) run their
own internal loop inside Anthropic's infrastructure — "A single request from
your application might trigger several web searches or code executions
before a response comes back" [Source:
research/technologies/anthropic-claude-api.md, §2]. When that server-side
loop hits its cap, the response carries `stop_reason: "pause_turn"`,
documented as: "Returned when the server-side sampling loop reaches its
iteration limit while executing server tools such as web search. The
default limit is 10 iterations per request" [Source:
research/technologies/anthropic-claude-api.md, §2]. A loop that treats
`pause_turn` as a terminal error rather than a resumable state will
silently truncate long-running server-tool work.

**Four documented Anthropic build paths, two documented OpenAI tiers — same
underlying control-vs-convenience axis.** Anthropic documents four explicit
options with a stated comparison: the **Claude Agent SDK** for "Building an
agent without implementing the tool loop yourself"; the **Claude Code CLI**
for interactive development or one-off terminal tasks; the **Client SDK
with your own loop** for "Calling the API directly and implementing the
tool loop yourself"; and **Managed Agents** for "Running long-running or
asynchronous agents without managing your own sandbox or session
infrastructure" [Source: research/technologies/anthropic-claude-api.md,
§11]. OpenAI draws the same line with two tiers: the **Agents SDK** when you
want "the SDK to manage the agent loop and recurring orchestration such as
repeated tool calls or branching," versus the raw **Responses API** when the
application needs "direct loop control and custom routing logic" [Source:
research/technologies/openai-api.md, §2]. Different vendor vocabulary, same
axis: how much of the loop do you want to own.

**Managed Agents has four core concepts worth knowing before reaching for
it.** Anthropic's Managed Agents architecture is **Agent** (model, system
prompt, tools, MCP servers, skills — created once, referenced by ID across
sessions), **Environment** (an Anthropic-managed cloud sandbox, or a
self-hosted sandbox), **Session** (a running agent instance in an
environment), and **Events** (user turns, tool results, and status updates
exchanged over server-sent events, with server-side-persisted history)
[Source: research/technologies/anthropic-claude-api.md, §11]. It is
explicitly in beta, and because it is "stateful by design" it is "not
currently eligible for Zero Data Retention... or HIPAA Business Associate
Agreement (BAA) coverage" [Source:
research/technologies/anthropic-claude-api.md, §11] — a real constraint to
weigh, not a footnote, for any regulated workload.

**State-management strategy is a genuine four-way choice, documented by
OpenAI, with a specific mixing hazard.** The Agents SDK documents four
strategies for persisting conversation state across turns: application-held
`result.history`/`to_input_list()` (small chats, maximum control); an
SDK-managed `session` backed by application storage (persistent, resumable
runs); the OpenAI Conversations API via `conversationId` (shared,
server-managed state); and the Responses API's `previousResponseId`
(lightweight response-to-response continuation) [Source:
research/technologies/openai-api.md, §2]. The documented warning applies
regardless of which pair you're combining: "Mixing local replay with
server-managed state can duplicate context unless you are deliberately
reconciling both layers" [Source: research/technologies/openai-api.md, §2].

**Multi-agent composition has two documented OpenAI patterns and one
increasingly-automatic Anthropic behavior — with a shared caution against
over-delegating.** OpenAI documents **handoffs** ("agents transfer
responsibility to specialists") and **agents-as-tools** (a manager agent
invokes specialist agents as reusable callable tools, composed
hierarchically) [Source: research/technologies/openai-api.md, §2].
Anthropic's newer models increasingly self-initiate subagent delegation:
"These models can recognize when tasks would benefit from delegating work
to specialized subagents and do so proactively without requiring explicit
instruction" — but the same guidance cautions that some models "may spawn
them in situations where a simpler, direct approach would suffice" [Source:
research/technologies/anthropic-claude-api.md, §5]. That caution is the
concrete guard against over-decomposing a task a single agent could handle.

**Approval/pause states are paused runs, not new turns — and miscounting
this breaks your own bounds.** OpenAI documents this distinction explicitly:
"Treat approvals as paused runs, not as new turns" — resuming requires
resolving `interruptions` and continuing from saved `state`, not starting a
fresh run, which is what keeps turn counts and server-side continuation IDs
consistent [Source: research/technologies/openai-api.md, §2]. A loop design
that instead restarts a fresh turn on every approval will double-count
against whatever step or cost limits it's supposed to enforce.

## Decision framework

1. **Does this genuinely need multi-step orchestration, or would a single
   tool call answer it?** If the task resolves with one tool call or one
   structured-output response, don't build a loop — route to
   [structured-output-tool-calling](../structured-output-tool-calling/SKILL.md).
2. **Who should own the loop?** Apply each vendor's own documented split:
   hand-roll it (Anthropic's Client SDK / OpenAI's raw Responses API) when
   the task needs "direct loop control and custom routing logic"; use a
   managed framework (Claude Agent SDK / OpenAI Agents SDK) when you want
   the SDK to own "the agent loop and recurring orchestration"; reach for a
   fully managed runtime (Anthropic Managed Agents) only when you also need
   to avoid owning sandbox/session infrastructure for long-running or async
   work — and weigh its beta status and ZDR/HIPAA ineligibility as real
   constraints.
3. **What state-management strategy fits?** Choose per OpenAI's four
   documented options — app-held history for small chats needing maximum
   control, an SDK session for resumable runs, the Conversations API for
   shared server-managed state, or `previousResponseId` for lightweight
   continuation — and never mix local replay with server-managed state
   without deliberately reconciling both.
4. **Does the task genuinely decompose into specialist roles?** Only then
   design multi-agent composition (handoffs, agents-as-tools, subagents).
   Both vendors' documented guidance cautions against delegating a task a
   single agent could complete directly.
5. **What bounds the loop?** Every loop needs an explicit termination
   condition — a `stop_reason`/output check, an iteration or step cap
   (Anthropic's own server-side loop defaults to 10 iterations, a useful
   reference point), a cost ceiling, or a combination — designed in
   coordination with [ai-security](../ai-security/SKILL.md) wherever the
   loop's tools carry real-world effects.
6. **Simplest viable option:** no loop at all, if the task doesn't actually
   require autonomous multi-step tool sequencing. Don't reach for agent
   orchestration by default.

## Workflow

1. Confirm the task genuinely needs multi-step tool orchestration; if not,
   route to structured-output-tool-calling instead.
2. Choose loop ownership — hand-rolled, managed framework, or fully managed
   runtime — per the target vendor's documented criteria.
3. Design the loop's termination condition(s) explicitly, before writing
   any implementation.
4. Choose a state-management/persistence strategy matching the task's
   control, resumability, and state-sharing needs.
5. Design multi-agent composition only if the task decomposes into genuine
   specialist roles.
6. Set autonomy bounds (step/recursion/cost limits) and hand off
   authorization/blast-radius design to ai-security.
7. Implement, deferring a single tool call's schema/round-trip mechanics to
   structured-output-tool-calling and prompt/context design to
   prompt-context-engineering.

## Engineering rules

- Every agent loop has an explicit termination condition designed before
  implementation — never an open-ended loop relying on the model to "just
  stop."
- Match loop ownership (hand-rolled vs. managed framework vs. fully managed
  runtime) to the documented control-vs-convenience trade-off, not habit.
- Never mix local conversation-replay state with server-managed state
  without deliberately reconciling both.
- Treat approval/pause states as paused runs to resume, not new turns to
  restart — miscounting this corrupts both step limits and cost tracking.
- Add multi-agent composition only when the task genuinely decomposes into
  specialist roles; don't delegate simple tasks to subagents by default.
- Bound autonomy (steps/recursion/cost) and coordinate the authorization
  boundary with ai-security rather than deciding it here.

## Trade-offs

A hand-rolled loop buys full control over routing, state, and retries at
the cost of building and maintaining tool-execution and error-handling
logic yourself. A managed framework buys faster delivery and built-in
handoff/session/guardrail machinery at the cost of less control over the
loop's internals. A fully managed runtime (Managed Agents) buys freedom
from sandbox/session infrastructure entirely at the cost of vendor
lock-in, beta-status risk, and — per Anthropic's own documentation —
ineligibility for Zero Data Retention or HIPAA BAA coverage, since it is
stateful by design.

## Anti-patterns

- **An agent loop with no explicit termination condition**, relying on the
  model to stop on its own rather than a designed `stop_reason`/step check.
- **Reaching for multi-agent/subagent composition on a task a single agent
  could complete directly** — the specific over-engineering trap both
  vendors' documented guidance cautions against.
- **Treating an approval/pause state as a new turn instead of a resumed
  run**, corrupting step and cost accounting.
- **Mixing local conversation replay with server-managed state** without
  reconciling them, silently duplicating context.
- **Defaulting to a fully managed runtime for a task a simple hand-rolled
  loop (or no loop) would handle**, incurring unnecessary infrastructure
  cost and lock-in.

## Security

Bounding what the loop's tools are authorized to do — blast radius,
permission scoping, step/recursion/cost limits as an attack surface — is
owned by [ai-security](../ai-security/SKILL.md); this skill designs the
loop and its bounds, and coordinates with ai-security on the security
implications rather than deciding them independently. Broader,
non-LLM-specific security review is owned by
[security-engineering](../security-engineering/SKILL.md).

## Performance

Loop length is a direct cost and latency lever: every iteration re-sends
accumulated conversation history as input tokens, so an unbounded or
poorly terminated loop compounds both. Anthropic's documented server-side
default of 10 iterations for its own tool-execution loop is a concrete
reference point for setting your own step caps. Deeper cost/latency
trade-off method (caching, effort/reasoning tuning) is owned by
[llm-application-engineering](../llm-application-engineering/SKILL.md) and
[performance-engineering](../performance-engineering/SKILL.md).

## Failure handling

- If the target platform/vendor isn't stated, ask rather than assume one
  vendor's loop semantics, stop-reason vocabulary, or state-persistence
  API.
- If the task is actually a single tool call or single structured-output
  response, decline to add orchestration and route to
  structured-output-tool-calling rather than building a loop reflexively.

## Escalation

- A request that is really about restricting what tools/actions the agent
  may take (authorization, blast radius, excessive agency) is escalated to
  ai-security rather than answered as loop design.

## Outputs & verification

- **Outputs:** an agent-loop design (with explicit termination/step-limit
  conditions and loop ownership), a state-management strategy, and — where
  implementation is in scope — the applied orchestration code.
- **Verify:** the loop has an explicit termination condition; autonomy is
  bounded and coordinated with ai-security wherever tools carry real-world
  effects; multi-agent composition is justified by genuine task
  decomposition rather than added reflexively.

## References

- [research/technologies/anthropic-claude-api.md](../../research/technologies/anthropic-claude-api.md)
- [research/technologies/openai-api.md](../../research/technologies/openai-api.md)
- [structured-output-tool-calling](../structured-output-tool-calling/SKILL.md)
- [prompt-context-engineering](../prompt-context-engineering/SKILL.md)
- [ai-security](../ai-security/SKILL.md)
