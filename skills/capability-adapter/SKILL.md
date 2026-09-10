---
name: Capability adapter
description: >-
  Reconcile a skill's declared capability requirements against what the host
  agent can actually do, and decide execute, degrade-to-advisory, documented
  fallback, or not-possible-here — before the skill acts. Use when any Tier B or
  Tier C skill is about to act, or when a capability is denied or revoked
  mid-run. Not when every active skill is Tier A. Never reports an unexecuted
  action as executed.
spec_version: "1.0"
---

## Purpose & scope

This skill is the library's **vendor-neutrality enforcement point**. A skill
declares what it needs abstractly — shell, browser, container, MCP client or
database access, git, sub-agent delegation, network. This skill decides what that
means on the host actually running, *before* the skill acts, so that no Tier B or
Tier C step ever runs blind.

It is a **barrier**, not a participant: nothing parallel crosses it, and it does
none of the work it gates. Which skills run is
[skill-router](../skill-router/SKILL.md); how they are staged is
[workflow-composer](../workflow-composer/SKILL.md).

## When to use / When not to use

**Use** when a Tier B or Tier C skill is about to act; when a capability is
denied, revoked, or discovered unavailable partway through a run; when a step
requests parallelism or delegation the host may not support; or when guidance
must be written for an unknown host.

**Do not use** when every active skill is Tier A — there is nothing to adapt.
Do not use to decide *which* skills to activate, to stage a workflow, or to
configure a specific host agent's settings.

## Knowledge

**Execution capability is not portable; knowledge is.** This is the premise the
whole library rests on. Only a skill's name, description, and Markdown body are
guaranteed to work across every researched host; everything execution-related is
a vendor-specific extension somewhere, and must degrade rather than fail.

**No host exposes a unified capability-discovery surface.** Skills, rules,
sub-agents, hooks, and MCP tools each have separate per-mechanism discovery in
every ecosystem researched. There is no single introspection call that answers
"can I run a container here?" This is the constraint that forces the resolution
ladder below: capability presence is *inferred from evidence*, never queried.

**The capabilities that are genuinely non-uniform**, and therefore the ones that
actually need adapting:

- **Browser automation / GUI interaction** — absent as a built-in in some hosts
  entirely; where present it varies from a first-class tool to a sub-agent, and
  in at least one host it is community-reported as configured-but-not-exposed.
- **Container execution** — no researched ecosystem documents a first-class
  container primitive distinct from shell. Everywhere it exists at all, it is
  plain shell wrapping the container CLI, so its availability must be verified,
  not assumed from the presence of shell.
- **Structured database access over MCP** — MCP client support is broad, but the
  config format is not portable (one ecosystem uses TOML where the rest use
  JSON), one caps total active tools, and one cannot sandbox MCP servers on a
  major platform.
- **Semantic repository search** — roughly half the researched hosts keep no
  standing index and reach the repository purely through grep/read calls.
- **Cross-session memory** — the least standardized capability researched:
  actively removed in one host's new default agent, unconfirmed in another.
- **Sub-agent delegation** — supported broadly, but whether a delegate inherits
  the parent's conversation is an unresolved cross-vendor fork (one inherits
  verbatim, one inherits nothing, others start fresh), and nesting caps differ by
  an order of magnitude.
- **Shell** — present everywhere, but gated by permission models every vendor
  self-describes as best-effort, and sandbox boundaries that in at least one host
  do not cover web, connector, MCP, or browser tools.

**Trust gating silently narrows capability.** In several hosts, an untrusted or
unopened workspace disables project-scoped configuration, skills, or MCP servers
outright. A capability that exists in the product may still be absent in *this*
session, which is why the ladder's lowest-cost rungs are about this session's
observed reality rather than the product's documentation.

## Decision framework

**The capability-resolution ladder** — climb only as far as needed, and stop at
the first rung that yields evidence:

1. **Declared** — the user or the environment has already stated it (a stated
   sandbox mode, an explicit "there is no shell here"). Cheapest and most
   reliable.
2. **Observed** — the capability has already been exercised successfully in this
   session. Strong evidence; costs nothing.
3. **Probed** — a single cheap, read-only, non-destructive action that would
   succeed only if the capability exists. Permitted only when the probe itself is
   free of side effects, cost, and outward effect.
4. **Asked** — ask the user about the environment. Correct whenever the probe
   would be destructive, costly, or outward-facing, and whenever the answer
   changes the plan materially.
5. **Assumed absent** — the terminal rung. When nothing above yields evidence,
   assume the capability is **not** available and take the fallback.

Rung 5 is deliberately conservative: assuming absence costs a degraded step,
while assuming presence produces a step that claims to have done something it did
not do. Those are not symmetric errors.

**The four-way decision**, once the ladder has produced evidence:

| Decision | When | What the step must then do |
|---|---|---|
| **Execute** | The capability is present (rung 1–3 evidence) and permitted | Proceed normally |
| **Fallback** | Absent, but the library documents a route (an MCP bridge, a shell-wrapped CLI, an alternative skill) | Proceed by the documented route; record the substitution |
| **Degrade to advisory** | Absent, no route, but the work still has value as guidance | Produce the guidance; mark every affected output unexecuted and unverified |
| **Not possible here** | Absent, no route, and guidance would be misleading | Say so, with the reason and what the user would need to change |

**Parallelism is a capability too.** A workflow may *request* parallelism; this
skill decides whether the host can deliver it and degrades it to sequential when
it cannot. Because nesting caps and history-inheritance behavior differ per host
and cannot be discovered at runtime, prefer sequential whenever the host's limits
are unknown. Correctness must never depend on parallelism — only speed does.

## Workflow

1. Collect each about-to-act skill's `required_capabilities`, `execution_tier`,
   and documented `capability_fallbacks`.
2. For each capability, climb the resolution ladder until evidence appears; stop
   at the first rung that yields it.
3. Make the four-way decision **per step**, using the step's concrete action —
   not per capability in the abstract, since the same capability may be permitted
   for one action and denied for another.
4. Where the decision is fallback or degrade, record precisely what will go
   unexecuted or unverified.
5. Downgrade any requested parallelism the host cannot deliver.
6. Emit the capability decision and the degradation record together, before the
   step runs.
7. Re-decide at step readiness if anything changed — a denied permission or a
   revoked tool invalidates an earlier decision.
8. Keep every emitted requirement abstract. Never name a host agent's tool.

## Engineering rules

- Decide **before** the step acts, never after it fails.
- Assume absence when evidence is unobtainable; never assume presence.
- Probe only with read-only, non-destructive, cheap actions — otherwise ask.
- Record every degradation with its downstream consequence.
- Never report an unexecuted action as executed, and never let a downstream stage
  or the final report imply it.
- Re-decide when a capability is denied or revoked mid-run; a stale decision is
  not a decision.
- Prefer the documented fallback over an improvised substitute; if no route is
  documented, say not-possible-here rather than inventing one.
- Express every capability abstractly; no host tool names in skill guidance.
- Do not infer one capability from another — shell availability does not imply
  container availability, and MCP client support does not imply a database server
  is connected.

## Trade-offs

The conservative default (assume absent) costs real capability: a host that could
have run the tests gets an advisory answer because nothing proved the shell
existed. The alternative — optimistic assumption — produces the library's worst
possible failure, a confident claim about work that never happened. The trade is
made deliberately in favor of honesty, and the ladder's cheap rungs exist
specifically to keep the conservative default from firing often.

Probing reduces that cost but is not free: a probe is a side-effecting action in a
system whose permission models are best-effort, so the restriction to read-only,
non-destructive, cheap probes is a hard boundary rather than a preference.

## Anti-patterns

- **Optimistic capability assumption** — proceeding because the capability
  usually exists.
- **Reporting advisory output as executed work** — the single most damaging
  failure this skill exists to prevent.
- **Capability inference** — concluding container support from shell support, or
  database access from MCP client support.
- **Naming a host tool in guidance** — the portability rule this skill enforces
  for every other skill; violating it here would be self-defeating.
- **Destructive probing** — running a real migration, a real deploy, or an
  outward-facing call to find out whether it is possible.
- **Deciding once and never re-checking** — treating a P3 capability decision as
  valid after a permission was denied at P5.
- **Over-adapting** — inserting the barrier when every active skill is Tier A,
  which is this domain's own over-engineering trap.

## Security

Capability decisions sit directly on the safety path. Two rules are absolute:
a permission denial is a decision to respect, never an obstacle to route around
with an alternative tool or an escalated mode; and a probe must never be the
thing that performs the risky action. Host permission and sandbox layers are
best-effort by every vendor's own description, so this skill treats them as
signals about intent, not as a security boundary it can lean on. Deep threat
modeling is owned by [security-engineering](../security-engineering/SKILL.md).

## Failure handling

- If a capability cannot be confirmed and cannot be cheaply probed, ask; if
  asking is not possible, assume absent and take the fallback.
- If no documented fallback exists, report not-possible-here with the reason
  rather than improvising a substitute.
- If a capability is revoked or denied mid-run, re-decide the step rather than
  letting it proceed on the earlier decision.
- If a probe would itself be destructive, outward-facing, or costly, do not
  probe — ask.

## Escalation

- A missing capability with no documented fallback escalates as not-possible-here
  with its reason, rather than degrading silently.
- A capability whose presence is uncertain and unprobeable escalates to the user
  as a question about the environment.
- A denied permission blocking a required step escalates with the specific
  action, why it is needed, and what happens if it stays denied.

## Outputs & verification

- **Outputs:** a per-step capability decision (execute / fallback / advisory /
  not-possible-here) with its evidence and ladder rung, and a degradation record
  stating what consequently goes unexecuted or unverified.
- **Verify:** no step reported as executed without the capability; every
  degradation recorded with its consequence; every decision naming its evidence;
  no host tool named; every probe read-only and cheap.

## References

- [research/knowledge-maps/agent-capability-map.md](../../research/knowledge-maps/agent-capability-map.md)
  — per-capability support and gaps across the seven researched ecosystems.
- [core/taxonomy/README.md](../../core/taxonomy/README.md) — the execution-tier
  model and the vendor-neutrality contract.
- [core/dependency-architecture/dependency-graph.md](../../core/dependency-architecture/dependency-graph.md)
  — the documented fallback edges resolved at this barrier.
- [core/orchestrator/lifecycle.md](../../core/orchestrator/lifecycle.md) — the
  barrier at P3 and the step-readiness re-check at P5.
- [core/skill-specification/adapter-projection.md](../../core/skill-specification/adapter-projection.md)
  — how canonical skills project into each target, and the loss manifest.
