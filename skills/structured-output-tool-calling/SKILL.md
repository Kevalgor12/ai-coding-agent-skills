---
name: Structured Output & Tool Calling
description: >-
  Design tool/function schemas and JSON-schema-constrained structured output
  so LLM responses and tool calls are schema-conformant — choose forcing
  semantics (auto/required/forced/none), respect each provider's JSON
  Schema support ceiling, and keep tool counts near the ~20 soft ceiling
  with dynamic loading for larger sets. Use when a feature needs
  schema-conformant output or the LLM to call external tools. Not the
  orchestration loop around tool calls (routes to agent-architecture).
spec_version: "1.0"
---

## Purpose & scope

Get reliable, schema-conformant structured output and tool/function calls
from an LLM — provider-neutral. Structured output and tool/function calling
are treated as one skill because both researched vendors implement them via
the same underlying enforcement mechanism: OpenAI documents that its
strict-mode function tools "use Structured Outputs internally," so the two
features "share one underlying enforcement engine" rather than being
unrelated capabilities. Covers tool-schema design, forcing semantics,
parallel tool calls, the tool-call round trip, and each platform's
documented JSON Schema support ceiling. Not the multi-step orchestration
loop *around* tool calls — that's
[agent-architecture](../agent-architecture/SKILL.md) — and not the prompt
design that surrounds a tool definition — that's
[prompt-context-engineering](../prompt-context-engineering/SKILL.md).

## When to use / When not to use

**Use** when a feature needs schema-conformant output for downstream
parsing, or needs the LLM to call external tools/functions. **Do not use**
when the output is unconstrained free text with no schema or tool involved,
or when the actual question is about the multi-step loop that sequences
several tool calls — route that to
[agent-architecture](../agent-architecture/SKILL.md).

## Knowledge

**Both platforms expose the same underlying enforcement mechanism under
different names.** Anthropic calls it **strict tool use** (`strict: true`
on a tool definition, "guarantee Claude's tool calls always match your
schema exactly") and **JSON outputs** (`output_config.format`), both
implemented via "constrained decoding," advertised as "Always valid: No
more `JSON.parse()` errors... No retries needed for schema violations"
[Source: platform.claude.com/docs/en/build-with-claude/structured-outputs].
OpenAI calls the non-tool form **Structured Outputs**
(`text: { format: { type: "json_schema", strict: true, schema: ... } }`)
and states the relationship to function calling explicitly: "Function
calling is useful when you are building an application that bridges the
models and functionality of your application," whereas Structured Outputs
suits cases where "you want to structure the model's output when it
responds to the user" directly — and `strict: true` function tools *use*
Structured Outputs internally, so the two "share one underlying enforcement
engine" [Source: developers.openai.com/api/docs/guides/structured-outputs].
Treat "is this calling something external?" vs. "is this just shaping the
final response?" as the question that decides which of the two you reach
for.

**Tool/function definition shape is nearly identical across vendors.**
Anthropic: `{"name", "description", "input_schema"}`, where `input_schema`
is standard JSON Schema (`type: "object"`, `properties`, `required`)
[Source: platform.claude.com/docs/en/agents-and-tools/tool-use/overview].
OpenAI: `type: "function"`, `name`, `description` ("details on when and how
to use the function"), a JSON-Schema `parameters` object, and an optional
`strict` boolean, with a worked example requiring `additionalProperties:
false` and every property listed in `required`
[Source: developers.openai.com/api/docs/guides/function-calling]. Both
vendors' own best-practice guidance is the same: write explicit
descriptions of purpose and each parameter's expected format, and apply
ordinary software-engineering naming/enum discipline to prevent invalid
states.

**Forcing semantics (`tool_choice`) line up conceptually but not
name-for-name.**

| Intent | Anthropic | OpenAI |
|---|---|---|
| Model decides | `{"type": "auto"}` (default) | `"auto"` (default) |
| Must call some tool | `{"type": "any"}` | `"required"` |
| Must call a specific tool | `{"type": "tool", "name": "..."}` | `{"type": "function", "name": "..."}` |
| No tool calls | `{"type": "none"}` | `"none"` |
| Restrict callable subset, keep full definitions cached | `disable_parallel_tool_use` caps at one call | `allowed_tools` narrows the callable subset while keeping full tool definitions in context for prompt-caching purposes |

[Source: platform.claude.com/docs/en/agents-and-tools/tool-use/overview;
developers.openai.com/api/docs/guides/function-calling]. Anthropic's
default `auto` is explicitly steerable via the system prompt — "a light
instruction increases tool use, a stronger one pushes further" — but the
same docs warn that on current models, aggressive tool-triggering language
is now an anti-pattern: "If your prompts were designed to reduce
undertriggering on tools... these models may now overtrigger. The fix is
to dial back the language"
[Source: platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices].
OpenAI documents parallel calls as the default on supported models
("beginning with GPT-5, functions can be called in parallel"); set
`parallel_tool_calls: false` to force at most one call per turn
[Source: developers.openai.com/api/docs/guides/function-calling].

**The tool-call round trip has the same shape on both platforms, with
different field names.** Anthropic: the assistant's `tool_use` block
(`{"type": "tool_use", "id": "toolu_...", "name": "...", "input": {...}}`)
is echoed back as `{"role": "assistant", "content": response.content}`,
followed by `{"role": "user", "content": [{"type": "tool_result",
"tool_use_id": "...", "content": "..."}]}`; multiple tool calls in one
turn are handled by returning all corresponding `tool_result` blocks
together
[Source: platform.claude.com/docs/en/agents-and-tools/tool-use/overview].
The full loop is documented as a five-step `while` pattern keyed on
`stop_reason`: send `tools` + message; Claude responds `stop_reason:
"tool_use"`; execute each tool and format `tool_result` blocks; send a new
request carrying those blocks; repeat while `stop_reason == "tool_use"`
[Source: platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works].
OpenAI's five-step flow is the same shape: send a prompt with available
tools; the model returns tool calls; the application executes them;
results are returned as `function_call_output` items referencing the
original `call_id`; the model produces a final response
[Source: developers.openai.com/api/docs/guides/function-calling]. A
documented OpenAI-specific failure mode: sending a `function_call_output`
without a matching `call_id` is named as a migration anti-pattern
[Source: developers.openai.com/api/docs/guides/migrate-to-responses].

**Each platform documents a hard JSON Schema support ceiling — designing
past it means the API silently won't enforce what you asked for.**
Anthropic supports basic types, `enum`, `const`, `anyOf`/`allOf`,
`$ref`/`$def`, several string `format`s, and `minItems` of 0 or 1; it does
**not** support recursive schemas, external `$ref`, numeric constraints
(`minimum`/`maximum`/`multipleOf`), string-length constraints, or any
`additionalProperties` value other than `false`
[Source: platform.claude.com/docs/en/build-with-claude/structured-outputs].
OpenAI's docs reference the same category of ceiling ("some features are
unavailable either for performance or technical reasons") without this
research pass having independently fetched OpenAI's full enumerated list —
treat OpenAI's exact ceiling as needing a docs check per schema rather than
assuming it matches Anthropic's list feature-for-feature
[Source: developers.openai.com/api/docs/guides/structured-outputs]. A
schema that needs a feature outside the target provider's documented
ceiling must either be restructured or have that constraint validated
out-of-band in application code — the provider's constrained decoding will
not enforce what it doesn't support.

**Tool-count discipline is documented near-identically by both vendors.**
OpenAI: "keep initial function count small (aim for fewer than 20)" and use
**tool search** for large, infrequently-used tool ecosystems
[Source: developers.openai.com/api/docs/guides/function-calling]. Anthropic
documents the same pattern as a distinct server-executed tool, `tool_search`
[Source: platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works].
A large static tool list both degrades tool-selection quality and burns
context-window/cache budget on rarely-used definitions.

## Decision framework

1. **Is this calling something external, or shaping the final response
   shown to the user?** External invocation (side effects, data lookups) →
   tool/function calling. Shaping the response the user/downstream code
   consumes directly, with nothing to execute → structured output
   (`output_config.format` / `text.format`).
2. **Does the task genuinely need a guaranteed call?** Default to `auto`.
   Only force (`any`/`required`, or a specific tool) when the task cannot
   proceed without a tool call — forcing by default causes the
   over-triggering both vendors warn against.
3. **Does the schema need a feature outside the target provider's
   documented JSON Schema ceiling** (recursive schemas, numeric/string-length
   constraints, external `$ref`)? If so, restructure the schema or move
   that validation into application code — don't assume the API enforces
   it.
4. **How many tools does this turn actually need?** Under ~20, a static
   list is fine. Approaching or exceeding it, design dynamic/tool-search
   loading instead of listing everything every turn.
5. **Simplest/do-nothing branch:** if the output is genuinely unconstrained
   free text with nothing to execute and no downstream parser, skip
   structured output and tool calling entirely.

## Workflow

1. Determine whether the task needs external tool/function invocation,
   schema-constrained output, or both.
2. Design the tool/function schema(s): clear name, a description of
   purpose and *when* to use it, and parameter docs as JSON Schema.
3. Choose forcing semantics (`auto`/`any`-or-`required`/forced-specific/
   `none`) and parallel-call setting matched to the task.
4. For non-tool structured output, design the JSON Schema for
   `output_config.format` / `text.format`, checking it against the target
   provider's documented ceiling.
5. Design the round trip: echo the `tool_use`/tool-call item back into
   message history, then supply the matching `tool_result`/
   `function_call_output`.
6. Count the tools active in this turn; if approaching ~20, design
   dynamic/tool-search loading instead.
7. If the task needs more than this single call — multiple sequential
   tool calls, branching, multi-agent handoff — hand off to
   [agent-architecture](../agent-architecture/SKILL.md).

## Engineering rules

- Match the mechanism to the need: tool/function calling for external
  invocation, structured output for shaping a direct response — don't use
  a forced tool call just to get schema-conformant text.
- Default `tool_choice` to `auto`; force a call only when the task cannot
  proceed without one.
- Never design a schema against a JSON Schema feature the target provider
  doesn't document support for; validate unsupported constraints
  out-of-band instead.
- Keep the active tool count near the ~20 soft ceiling; use dynamic/
  tool-search loading for larger tool ecosystems rather than listing
  every tool every turn.
- Write explicit, specific tool descriptions (purpose, parameter formats,
  when to use it) — schema enforcement guarantees shape, not correct tool
  *selection*.

## Trade-offs

Forcing a tool call (`any`/`required`, or a specific tool) guarantees the
call happens but risks an unnecessary call when the model would otherwise
have answered directly; `auto` gives the model judgment at the cost of
occasional under- or over-triggering that needs prompt tuning to correct.
A static tool list is simpler to reason about and cache than dynamic/
tool-search loading, but stops scaling cleanly once a tool ecosystem grows
past the ~20-tool range both vendors document as the soft ceiling.

## Anti-patterns

- **Forcing `tool_choice: any`/`required` by default** rather than only
  when the task genuinely cannot proceed without a call — both vendors'
  docs warn this causes over-triggering.
- **Loading every available tool into every turn** instead of respecting
  the ~20-tool soft ceiling and using dynamic/tool-search loading for
  larger ecosystems — the over-engineering trap in reverse: under-designed
  tool scoping, not over-designed orchestration.
- **Designing a schema against JSON Schema features the target provider
  doesn't document support for** (recursive schemas, numeric/string-length
  constraints, unsupported external `$ref`) and assuming the API enforces
  them anyway.
- **Building a dynamic tool-search/loading system for a handful of tools**
  well under the ~20-tool ceiling — the over-engineering trap in the other
  direction, adding indirection a static list would have handled.
- **Treating a `tool_result`/`function_call_output` as if it always came
  back schema-valid** without checking `stop_reason`/error fields — the
  round trip must handle a failed or malformed tool execution, not just
  the success path.

## Security

Untrusted content returned by a tool (a web page, a document, a third-party
API response) should be delivered to the model only inside `tool_result`/
`function_call_output` blocks, never folded into a system prompt or plain
user text block — Anthropic's guardrails documentation states Claude "is
trained to treat instructions that appear inside tool results with
appropriate skepticism," which only holds if untrusted content actually
lands there rather than elsewhere in the prompt
[Source: platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks].
Deeper threat modeling (input/output screening, least privilege, red-teaming)
is owned by [security-engineering](../security-engineering/SKILL.md).

## Performance

Keep tool definitions, their ordering, and their schemas stable across
calls — both platforms tie prompt-cache reuse to this. Anthropic builds
cache prefixes in a strict order, "`tools`, `system`, then `messages`"
[Source: platform.claude.com/docs/en/build-with-claude/prompt-caching].
OpenAI's guidance is explicit: "keep tool definitions/ordering/schemas
consistent across calls," narrowing which tools are *callable* via
`tool_choice: "none"` or `allowed_tools` without changing the definitions
that are *cached*
[Source: developers.openai.com/api/docs/guides/prompt-caching]. Broader
cross-cutting performance method is owned by
[performance-engineering](../performance-engineering/SKILL.md).

## Testing

Verify the round trip end-to-end against a real or fixture tool call and
result — not just that the schema compiles — and that structured output
actually validates against the declared schema on representative inputs,
including inputs likely to hit the provider's documented JSON Schema
ceiling. Deep test-strategy method is owned by
[testing-strategy](../testing-strategy/SKILL.md).

## Failure handling

- If the target provider/model isn't stated, ask rather than silently
  assume a JSON Schema ceiling or `tool_choice` vocabulary that may not
  apply.
- If the request is actually about the multi-step orchestration loop
  around tool calls rather than a single call's schema/round trip, say so
  and route to [agent-architecture](../agent-architecture/SKILL.md) rather
  than answering as if it were in scope.

## Escalation

- A request that is really about the agent orchestration loop around tool
  calls (not a single call's schema/round trip) is routed to
  [agent-architecture](../agent-architecture/SKILL.md) rather than
  answered here.

## Outputs & verification

- **Outputs:** a tool/function schema and/or structured-output schema
  design matched to the task and provider ceiling, plus the implemented
  tool-call round trip and forcing-semantics configuration.
- **Verify:** the schema stays within the target provider's documented
  JSON Schema ceiling; forcing semantics match the actual task need rather
  than defaulting to forced calls; the active tool count stays near the
  ~20 soft ceiling, with dynamic loading used above it.

## References

- [research/technologies/anthropic-claude-api.md](../../research/technologies/anthropic-claude-api.md)
- [research/technologies/openai-api.md](../../research/technologies/openai-api.md)
