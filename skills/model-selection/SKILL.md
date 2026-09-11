---
name: Model Selection
description: >-
  Choose the right LLM provider and model tier for a task's capability,
  cost, and latency needs — a vendor-neutral decision method, not a fixed
  recommendation, using Anthropic's and OpenAI's own tiering guidance as
  worked examples that go stale. Weighs capability vs. cost vs. latency vs.
  context-window against actual requirements; accounts for snapshot pinning
  and deprecation-notice practices. Use when choosing a model/provider/tier,
  or auditing whether a current model is oversized for its task.
spec_version: "1.0"
---

## Purpose & scope

Choose the right LLM provider and model tier for a task's actual
capability, cost, and latency requirements — a vendor-neutral decision
method, not a single-vendor recommendation, grounded in more than one
vendor's own documented tiering guidance. **The current model names,
prices, and context-window sizes cited below are worked examples of the
method, snapshotted 2026-09-10 from Anthropic's and OpenAI's own docs —
like the research docs themselves, they carry an explicit staleness
warning and should be re-verified against current vendor documentation
before being treated as fact, not calcified into a specific-model-name
recommendation.** This skill decides *which* model answers a call; it does
not design the prompt/context around that call
([prompt-context-engineering](../prompt-context-engineering/SKILL.md),
SK-AI-002), the tool schema or agent loop the call participates in
(SK-AI-003, SK-AI-004), or how the resulting output gets graded
([llm-evaluation](../llm-evaluation/SKILL.md), SK-AI-007).

## When to use / When not to use

**Use** when choosing which model/provider/tier a feature should call, or
when evaluating whether a currently-used model is appropriately sized
(over- or under-powered) for its task. **Do not use** when the model is
already fixed by an external constraint with no real choice to make (e.g.
a mandated single-vendor contract), or when the actual request is about
prompt/context design, tool-schema/agent-loop design, or eval-harness
design rather than which model to call — route those to
[llm-application-engineering](../llm-application-engineering/SKILL.md)'s
sub-disciplines (SK-AI-002, SK-AI-003/SK-AI-004) or
[llm-evaluation](../llm-evaluation/SKILL.md) (SK-AI-007) instead.

## Knowledge

**Every model choice trades off the same four axes — capability, cost,
latency, and context window — and both grounding vendors expose each axis
directly in their own docs rather than leaving it to guesswork.** The
worked examples below reflect each vendor's lineup as documented on
2026-09-10; treat every specific tier name and price as an illustration of
the method, not a fact to hardcode (see Purpose & scope).

**Capability tiers, worked example — Anthropic.** Anthropic documents four
active tiers with a stated default: "If you're unsure which model to use,
start with Claude Opus 5 for most workloads. Use Claude Fable 5.1 for
demanding reasoning and long-horizon agentic work, or when your evals on
Claude Opus 5 at higher effort still fall short"
[Source: platform.claude.com/docs/en/models/overview]. Each tier's own
page states a comparative-latency ranking (Fable 5.1: Slower; Opus 5:
Moderate; Sonnet 5: Fast; Haiku 4.5: Fastest) and current per-MTok
input/output pricing (Fable 5.1 $10/$50; Opus 5 $5/$25; Sonnet 5 $2/$10;
Haiku 4.5 $1/$5) [Source: platform.claude.com/docs/en/models/overview].
Anthropic's cost-optimization guidance restates the same tiering as a rule
of thumb: "Choose Haiku for simple tasks, Sonnet for most production
workloads, and Opus for the most complex reasoning"
[Source: platform.claude.com/docs/en/about-claude/pricing].

**Capability tiers, worked example — OpenAI.** OpenAI's current lineup is
`gpt-6-astra` ("our most capable model, built for the hardest end-to-end
work," $10/$50 per MTok) and the GPT-5.6 family — `gpt-5.6-sol`
("positioned for complex professional work," $4/$20), `gpt-5.6-terra`
("balances performance and cost efficiency," $2/$12), and `gpt-5.6-luna`
("optimized for cost-sensitive applications," $0.20/$1.20)
[Source: developers.openai.com/api/docs/models]. Independent of which
model is chosen, OpenAI exposes a second, orthogonal cost/quality lever:
`reasoning.effort`, with `medium` as "default for most workloads,
balancing quality and reliability against latency," escalating to
`high`/`xhigh`/`max` only for harder tasks, and the explicit instruction
to treat it "as a tuning knob, not the primary way to recover quality"
[Source: developers.openai.com/api/docs/guides/reasoning]. Anthropic
documents an analogous lever, `effort`, defaulting to `high` and
adjustable to `low`/`medium`/`xhigh`/`max`
[Source: platform.claude.com/docs/en/build-with-claude/effort] — on both
platforms, this secondary lever is often the cheaper first move before
jumping to a bigger model tier.

**Context window.** Anthropic's current 1M-context tier (Fable 5.1, Opus
5, Sonnet 5) and 200K-context tier (e.g. Haiku 4.5) each cap output at a
documented per-request maximum (128K and 64K tokens respectively)
[Source: platform.claude.com/docs/en/build-with-claude/context-windows].
Anthropic explicitly warns a bigger window is not automatically better:
"As token count grows, accuracy and recall degrade, a phenomenon known as
context rot. This makes curating what's in context just as important as
how much space is available"
[Source: platform.claude.com/docs/en/build-with-claude/context-windows] —
bounding context to what the task needs is itself part of tier selection,
not only a prompt-engineering concern (owned in depth by SK-AI-002).
OpenAI's current flagship and GPT-5.6 family share a roughly 1.05M-token
context window [Source: developers.openai.com/api/docs/models].

**Production model-snapshot pinning and deprecation-notice practices
differ by vendor and matter directly to model choice, not only to ongoing
maintenance.** Anthropic pins every model ID to a specific snapshot —
"Every Claude model ID is a pinned snapshot, including the dateless IDs
used from the 4.6 generation on"
[Source: platform.claude.com/docs/en/models/overview] — and documents
per-model retirement-date commitments; worked retirement examples show
roughly a two-month gap between an announced deprecation and the actual
retirement date (e.g. `claude-opus-4-1-20250805`: deprecated 2026-06-05,
retired 2026-08-05)
[Source: platform.claude.com/docs/en/about-claude/model-deprecations].
OpenAI documents an explicit, tiered notice-period policy instead of a
single number: generally-available models get "at least 6 months"
notice, specialized variants (chat/Codex/deep-research) get "at least 3
months," and models with `preview` in the name "may be retired with much
shorter notice," potentially as little as "2 weeks"
[Source: developers.openai.com/api/docs/deprecations]. Both vendors
converge on the same mitigation in different words — Anthropic's
dateless-but-pinned IDs, and OpenAI's explicit instruction to "pin
production applications to specific model snapshots"
[Source: developers.openai.com/api/docs/guides/prompt-engineering] — so
choosing a model for production use includes choosing how it will be
pinned and monitored for deprecation, not just which tier answers today's
request.

## Decision framework

1. **What does the task actually need?** State the capability requirement
   (simple classification/extraction vs. complex/long-horizon reasoning),
   the cost/latency budget, and the context-window need before touching a
   vendor's tier list.
2. **Start from the vendor's own documented default tier for the task's
   general shape** — don't jump to the flagship tier "to be safe." Read
   this as a reusable pattern ("start with the default, escalate for
   harder cases"), not as an endorsement of whichever specific tier
   currently holds that "default" label.
3. **Escalate one step, not to the top, when the default underdelivers —
   and reach for the secondary lever (effort / `reasoning.effort`) before
   a full model-tier jump.** Both vendors document this lever as cheaper
   than switching models outright.
4. **Match the context-window tier to the task's actual size need, not
   the largest available window.** A bigger window costs more and (per
   Anthropic's documented context-rot caution) is not free of accuracy
   risk either.
5. **For production use, decide the snapshot-pinning and
   deprecation-monitoring plan as part of the selection**, sized to the
   target vendor's documented notice-period practice (OpenAI's tiered
   6-month/3-month/2-week windows; Anthropic's per-model retirement-date
   commitments).
6. **State the trade-off explicitly in the output**: which axis was
   optimized for, and what was given up (e.g. "chose the mid tier —
   cheaper and faster than the flagship, accepting somewhat shallower
   reasoning depth — appropriate because the task is bounded
   classification, not open-ended reasoning").
7. **Simplest/do-nothing branch:** if an existing model already meets the
   requirement with headroom to spare, the correct selection is "keep the
   current model" — don't re-select just because a newer or more capable
   tier exists.

## Workflow

1. Gather the task's capability need, cost/latency budget, and
   context-window need.
2. List candidate providers/models actually available (respecting any
   existing vendor constraint).
3. Map the task's capability need to each candidate's tier lineup, using
   the vendor's own default-tier guidance as the starting point.
4. Compare per-request cost and comparative latency across the
   shortlisted tiers for the task's expected token volume.
5. Check context-window fit against the task's actual input/output size.
6. For a production choice, decide the model-snapshot-pinning and
   deprecation-monitoring plan.
7. State the selection and the explicit trade-off rationale.

## Engineering rules

- Don't default to the most capable/expensive tier reflexively — start
  from the vendor's own documented default and escalate only when the
  task's actual requirement demands it.
- Prefer the secondary cost/quality lever (effort / `reasoning.effort`)
  over a full model-tier jump when it's available and sufficient.
- Match context-window tier to the task's actual size need; a larger
  window is not automatically better and isn't free.
- Pin production model choices to a specific snapshot ID, and track the
  target vendor's deprecation-notice timeline rather than discovering
  retirement at the sunset date.
- Treat every model name/price in this skill's Knowledge section as a
  worked example to re-verify against current vendor docs, not as a
  durable fact.

## Trade-offs

Flagship/most-capable tiers buy headroom on hard reasoning tasks at real
per-token cost and latency cost; cheaper/faster tiers buy throughput and
lower spend at the risk of under-delivering on tasks that genuinely need
deeper reasoning. Pinning a specific model snapshot buys predictable
behavior at the cost of manually tracking and migrating off retiring
snapshots on the vendor's notice-period timeline; resolving to a
rolling/"latest" alias where a vendor offers one buys less migration
overhead at the cost of silent behavior drift.

## Anti-patterns

- **Defaulting to the flagship/most expensive tier "to be safe"** for
  every call, regardless of the task's actual requirement — this domain's
  specific over-engineering trap.
- **Hardcoding a hand-picked model name as a permanent choice** with no
  pinning/deprecation-monitoring plan, then discovering retirement at the
  sunset date.
- **Treating a bigger context window as strictly better** rather than
  sized to the task, ignoring both its cost and (per Anthropic's
  documented context-rot caution) its accuracy implications.
- **Reaching for a bigger model tier to fix a quality problem that the
  secondary effort/`reasoning.effort` lever would fix more cheaply.**
- **Treating this skill's specific tier names/prices as evergreen** rather
  than as the worked examples they are — the single most likely way this
  skill itself goes stale.

## Failure handling

- If the task's cost/latency budget or capability need isn't stated, ask
  rather than defaulting reflexively to the most capable/expensive tier.
- If the model is genuinely fixed by an external constraint, say so and
  skip the selection exercise rather than manufacturing a choice.

## Escalation

- If a task's real requirement is too ambiguous to justify one tier over
  another, escalate to the requester for a concrete capability/cost/
  latency bar rather than guessing.

## Outputs & verification

- **Outputs:** a model/provider/tier selection, and the explicit
  capability/cost/latency/context-window rationale behind it (including a
  production pinning/deprecation-monitoring plan when relevant).
- **Verify:** the selection is proportionate to the stated requirement,
  not defaulted to the most capable/expensive tier; the rationale names
  the trade-off explicitly; any cited model name/price is flagged as a
  re-verify-before-trusting worked example.

## References

- [research/technologies/anthropic-claude-api.md](../../research/technologies/anthropic-claude-api.md)
- [research/technologies/openai-api.md](../../research/technologies/openai-api.md)
