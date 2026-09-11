---
name: AI Security
description: >-
  Defend LLM-powered applications against threats specific to or amplified
  by LLM use — prompt injection, excessive agency, sensitive-info
  disclosure, LLM-specific supply-chain risk — grounded in the OWASP GenAI
  LLM Top 10 (2026). Frames defense as bounding blast radius, not
  prevention: no reliable prompt-injection prevention exists today. Use
  reviewing/designing an LLM feature with tool access, untrusted-content
  ingestion, or user exposure. Traditional AppSec routes to
  security-engineering.
spec_version: "1.0"
---

## Purpose & scope

Defend LLM-powered applications against threat classes that are specific
to, or meaningfully amplified by, LLM use — prompt injection, excessive
agency, sensitive-information disclosure via model/embedding channels, and
LLM-specific supply-chain risk — grounded directly in the **OWASP GenAI LLM
Top 10 (2026)**. This is genuinely distinct from
[security-engineering](../security-engineering/SKILL.md) (SK-QA-002), which
owns traditional AppSec (injection, XSS, CORS/CSRF, SSRF, secrets,
transport, sandboxing, supply-chain, DoS, disclosure) — the OWASP GenAI
project's own charter scopes its list to risks "specific to or meaningfully
amplified by the use of large language models, rather than general
application security issues" [Source: owasp-llm-top10.md §1/§11]. **State
this up front, the way it must be stated in every assessment this skill
produces: prompt injection has no architectural equivalent to a
parameterized-query code/data boundary** — an LLM "treat[s] system prompt,
user input, retrieved documents, tool outputs, conversation history, and
memory as a single token stream, with no enforced trust boundary" [Source:
owasp-llm-top10.md §4] — and the standard itself states **"no reliable
prevention mechanism exists today"** [Source: owasp-llm-top10.md §4]. This
skill therefore frames defense as **bounding blast radius**, never as
promising complete prevention.

## When to use / When not to use

**Use** when reviewing or designing an LLM feature with tool access,
untrusted-content ingestion, or user-facing exposure; when an explicit
security review of an LLM-powered system is requested; when deciding how
much autonomy/authorization an LLM agent should carry; or when assessing
LLM-specific supply-chain risk (model/adapter provenance, quantization
effects). **Do not use** for a traditional, non-LLM-specific AppSec concern
with no LLM-specific amplification — route to
[security-engineering](../security-engineering/SKILL.md) — or for
auth/authz design with no LLM dimension, which belongs to
authentication-authorization.

## Knowledge

**Why prompt injection is structurally different from SQL injection.**
Classic injection has a clean, enforceable code/data boundary — a
parameterized query. An LLM has none: system prompt, user input, retrieved
documents, tool outputs, conversation history, and memory are "a single
token stream, with no enforced trust boundary," and "both are tokens on the
same stream" [Source: owasp-llm-top10.md §4]. The injected content doesn't
need to look like an attack to a human — "a poisoned wiki page, an issue
title, a tool response, an image, or a line written into long-term memory
all reach the same token stream" [Source: owasp-llm-top10.md §4]. Direct
injection is a user (or attacker with user access) crafting adversarial
input; indirect injection is the model ingesting external content — web
pages, emails, tool responses, RAG passages — that carries attacker
instructions the user never supplied or saw, at trust levels spanning
"untrusted public sources to semi-trusted third-party content to
trusted-but-compromised internal systems" [Source: owasp-llm-top10.md §4].
Anthropic documents the same split as jailbreaks/direct injection (the
application's own user is the adversary) versus indirect injection (a
trusted user, but Claude processes adversarial third-party content)
[Source: anthropic-claude-api.md §7].

**The mitigation catalog, and its documented limits — present every one of
these honestly, never as a solved problem.** Role/capability constraints in
system prompts are partial: "attackers can infer and bypass" them.
Output-schema validation catches format violations but "miss[es] malicious
content in valid structures." Provenance-labeled channels separating data
from instructions are bypassable under adaptive attack — "StruQ failed when
attackers knew the marking scheme." Human confirmation for
privileged/irreversible actions degrades under "approval fatigue and
invisible-character spoofing." Unicode stripping "doesn't stop visible
payloads or future steganographic classes" [Source: owasp-llm-top10.md §4].
The two load-bearing patterns that hold up best are **least-privilege
architecture** — credentials held in application code, never handed to the
model, with a deterministic policy engine re-validating authorization at
the moment of execution rather than trusting the model's stated intent
[Source: owasp-llm-top10.md §4, §8] — and putting **untrusted content only
in tool results**, never in system prompts or plain user text: "Claude is
trained to treat instructions that appear inside tool results with
appropriate skepticism," and untrusted payloads should be JSON-encoded so
"an attacker cannot close a quote or tag to 'break out' into an instruction
context" [Source: anthropic-claude-api.md §7]. Both OpenAI and Anthropic
converge on the same operational habit: red-team by asking "can someone
easily redirect the feature via prompt injections" [Source: openai-api.md
§7], and treat human review as the default posture "especially critical in
high-stakes domains, and for code generation" [Source: openai-api.md §7].

**Excessive agency's three root causes.** [Source: owasp-llm-top10.md §6]
**Excessive functionality** — a tool exposes more than the task needs
(delete/modify access where only read is required, reachable debug tools,
open-ended tools that "fail to filter instructions properly"). **Excessive
permissions** — the tool's downstream credentials outstrip need: "An LLM
tool that is designed to perform operations in the context of an individual
user accesses downstream systems with a generic high-privileged identity"
instead of impersonating that specific user, so any agent compromise
inherits the shared credential's full privilege. **Excessive autonomy** —
the application "fails to independently verify and approve high-impact
actions," letting the model's own output serve as final authorization.
Mitigation: minimize tools and per-tool functionality; minimize downstream
permissions; track user authorization so actions execute in the specific
user's context, not a shared service identity; require human approval for
high-impact actions; and enforce **complete mediation** — authorization
decided by external, deterministic policy logic, never by the LLM's own
judgment [Source: owasp-llm-top10.md §6]. The document's own synthesis ties
this back to LLM01: "prompt-injection incidents became severe because the
injection landed inside a system whose tools, scopes, or
output-rendering capabilities let the compromised model act on the
attacker's behalf at the user's privilege level" [Source:
owasp-llm-top10.md §4] — injection is the trigger, excessive agency is what
turns it into damage.

**Output-handling discipline mirrors traditional injection defense, almost
verbatim.** Improper Output Handling means trusting the model's output
*shape* without verification, whether or not the content is malicious,
hallucinated, or benign [Source: owasp-llm-top10.md §6]. The documented
fix is zero-trust validation of every LLM response as though it were
untrusted user input: context-aware encoding per destination (HTML,
JavaScript, SQL each get their own encoding, not one generic sanitizer),
and — the clearest point of continuity with traditional AppSec found in the
whole standard — **parameterized database queries specifically**, applied
to LLM-generated SQL the same way they're applied to any other
user-adjacent query text [Source: owasp-llm-top10.md §6, §11]. A worked
scenario makes the stakes concrete: "a user requests a query to delete all
database tables. If the crafted query from the LLM is not scrutinized, then
all database tables will be deleted" [Source: owasp-llm-top10.md §6].

**The adaptive-vs-static red-teaming gap is the standard's single most
quotable, load-bearing empirical fact.** Static/naive testing of
prompt-injection defenses "showed near-zero success," while adaptive
testing — where the red team is given the defense's full specification in
advance — "exceeded 90% against most recent defenses" [Source:
owasp-llm-top10.md §4, §10]. A team that ships every documented LLM01
mitigation and validates only with naive red-teaming can walk away with
unjustified confidence [Source: owasp-llm-top10.md §14]. This is why
production programs should budget for defense-in-depth plus **ongoing**
adaptive red-teaming, not a point-in-time control checklist [Source:
owasp-llm-top10.md §16].

**Other Top 10 categories worth naming even when not the primary finding.**
Sensitive Information Disclosure (LLM02) spans training-time memorization,
inference-time leakage, pipeline-time carry-over into fine-tuned artifacts,
and observation-time side channels (timing/size metadata alone can leak
conversation topics) — with "authorize before retrieval: enforce document-
and chunk-level authorization inside the index query" as its own repeated
Tier-1 mitigation [Source: owasp-llm-top10.md §5]. Hidden Context Exposure
(LLM08, renamed from System Prompt Leakage) treats system prompts, tool
schemas, and RAG-injected policy as **discoverable by default** — "hidden
context should not be relied on as the primary mechanism for controlling
model behavior," and "critical controls such as privilege separation,
authorization bounds checks, and similar must not be delegated to the LLM"
[Source: owasp-llm-top10.md §2, §8]. Vector and Embedding Weaknesses (LLM09)
documents embedding-inversion recovery rates of "roughly 50–70% of words...
to 92% exact reconstruction of short 32-token inputs" — meaning an
embeddings-only backup is a source-document breach, not a reduced-severity
one [Source: owasp-llm-top10.md §2, §9]. Supply Chain (LLM04) extends
beyond code dependencies to model/adapter provenance: models resolved by a
mutable tag or author/repo name rather than an immutable, signed digest are
swappable after the fact, and quantization is specifically documented as
able to hide attacker-chosen behavior invisible at full precision — "the
full-precision model evaluates benignly while the quantized artifact
exhibits attacker-chosen behavior" [Source: owasp-llm-top10.md §7].

## Decision framework

1. **Is this actually LLM-specific, or general AppSec?** If the risk exists
   and is fully mitigated the same way with or without an LLM in the loop,
   it belongs to [security-engineering](../security-engineering/SKILL.md),
   not here.
2. **Where does untrusted content enter, and where does it currently
   live?** If external content (web pages, emails, tool results, RAG
   passages) is blended into a system prompt or plain user text rather than
   confined to a clearly-delineated, skepticism-flagged channel (e.g. a
   tool-result block), that placement is itself the finding.
3. **What can the model actually cause to happen, and at whose privilege?**
   Trace from the injection/hallucination surface through to the
   downstream credential and action — severity is bounded by agency, not by
   the injection itself.
4. **Which of the three excessive-agency root causes applies?** Excess
   functionality (the tool can do more than needed), excess permissions
   (shared high-privilege identity instead of per-user scoping), or excess
   autonomy (no independent approval gate for high-impact actions) — name
   the specific one(s), not "the agent has too much power" generically.
5. **Is a high-impact or irreversible action gated on deterministic policy
   or human approval, or only on the model's own stated intent?** If the
   latter, that is excessive autonomy regardless of how well-worded the
   system prompt is.
6. **Would the proposed mitigation survive adaptive red-teaming, or only
   naive testing?** If the answer isn't known, say so and recommend
   adaptive testing rather than asserting the mitigation is sufficient.
7. **Does the simplest option — narrowing the tool/data surface instead of
   adding another filter layer — resolve this?** Removing a capability
   (e.g. dropping send/delete access) is often a stronger, cheaper fix than
   layering another classifier on top of a capability that shouldn't exist.

## Workflow

1. Identify the LLM feature's tool/data access surface and every point
   where untrusted external content can reach the model.
2. Map each identified risk to its OWASP LLM Top 10 (2026) category —
   don't leave a finding uncategorized.
3. Check whether untrusted content is confined to a clearly-delineated,
   skepticism-flagged channel, never blended into system-level
   instructions.
4. Check whether credentials/authorization live in deterministic
   application code, re-validated at execution time, rather than being
   inferred from the model's own output.
5. Check each of the three excessive-agency root causes against the
   agent's actual tool/permission/autonomy configuration.
6. For any LLM-generated query or code reaching a downstream system,
   confirm it still flows through parameterized queries / context-aware
   output encoding.
7. Propose mitigations as blast-radius-bounding, with the specific
   documented limitation of each named — never as complete prevention.
8. Recommend adaptive red-teaming (defense specification disclosed to the
   red team) as the validation method for prompt-injection-class
   mitigations, not naive/static testing alone.

## Engineering rules

- Never state or imply that a prompt-injection mitigation is complete —
  the standard itself documents none as reliable prevention.
- Untrusted external content (web pages, emails, tool results, RAG
  passages) goes only in clearly-delineated, skepticism-flagged channels
  (e.g. tool-result blocks with a stated content policy), never blended
  into system-level instructions or plain user text.
- Credentials and authorization decisions live in deterministic
  application code re-validated at execution time — never delegated to the
  model's own stated intent.
- High-impact or irreversible agent actions require human approval or an
  independent policy check before execution.
- LLM-generated queries/code reaching a downstream system still flow
  through parameterized queries and context-aware output encoding, per
  destination.
- Treat hidden context (system prompts, tool schemas) as discoverable by
  default; its disclosure alone must cause no material harm.
- Validate prompt-injection mitigations with adaptive red-teaming (full
  defense spec disclosed to the red team), not naive/static testing alone.
- Authorize inside the retrieval query (document/chunk-level, at
  index-query time) for any RAG/vector-store access — never filter
  results after retrieval.

## Trade-offs

Narrowing tool functionality/permissions is cheaper and more reliable than
adding another semantic filter on top of an overly capable tool — every
semantic-filter-based mitigation the standard documents (role constraints,
multimodal filtering, provenance labeling) is immediately followed by a
documented adaptive-attack bypass [Source: owasp-llm-top10.md §9]. Human
approval for high-impact actions adds friction and is vulnerable to
approval fatigue at scale, but remains the strongest available backstop
where autonomous execution would be irreversible. Defense-in-depth (several
partial mitigations layered) costs more to build and maintain than any
single control, but is the standard's own implicit recommendation given
that no single documented mitigation is sufficient alone.

## Anti-patterns

- **Claiming a prompt-injection mitigation is complete** — the standard is
  explicit that "no reliable prevention mechanism exists today"; frame
  every mitigation as blast-radius-bounding instead.
- **Validating prompt-injection defenses with only naive/static
  red-teaming** — the documented gap between static (near-zero success)
  and adaptive (90%+ success) testing means this produces unjustified
  confidence.
- **Blending untrusted external content into a system prompt or plain user
  text** instead of a clearly-delineated tool-result-style channel.
- **Authenticating an agent's downstream tool calls with a shared
  high-privileged identity** instead of the specific end user's own scoped
  credentials — converts one agent compromise into a blast radius covering
  every user the shared credential can act for.
- **Filtering RAG/vector-store results for authorization after retrieval**
  instead of enforcing it inside the index query itself.
- **Treating an embeddings-only backup as lower-sensitivity than the
  source documents** — documented inversion rates make this a
  source-document breach, not a reduced-severity one.
- **Over-engineering trap for this domain**: reaching for a heavier
  semantic-classifier stack as the primary defense when narrowing the
  tool/data surface (removing the capability outright) would close the gap
  more reliably and more cheaply.
- **Answering a traditional, non-LLM-specific AppSec question as if it
  were in this skill's scope** — route it to
  [security-engineering](../security-engineering/SKILL.md) instead.

## Security

This skill's entire content is LLM-specific security. Traditional AppSec
(injection, XSS, CORS/CSRF, SSRF, secrets, transport, sandboxing,
non-LLM supply-chain, DoS, disclosure) is owned by
[security-engineering](../security-engineering/SKILL.md) — reference it,
don't restate it. Agent-loop/orchestration design that this skill's
excessive-agency findings bound is owned by
[agent-architecture](../agent-architecture/SKILL.md). Prompt/context
structure that this skill's untrusted-content-channel guidance constrains
is owned by
[llm-application-engineering](../llm-application-engineering/SKILL.md).
Retrieval-authorization and embedding-sensitivity depth is owned by
[rag-engineering](../rag-engineering/SKILL.md).

## Failure handling

- If the LLM feature's tool/data access surface isn't described, ask
  rather than assume a worst-case or best-case posture.
- If asked to certify a mitigation as complete prevention (especially for
  prompt injection), state the standard's own documented limitation
  instead of overclaiming.
- If the request is a traditional AppSec concern with no LLM-specific
  amplification, route it to security-engineering rather than answering as
  if it were in scope here.

## Escalation

- A finding involving an LLM agent with simultaneous access to untrusted
  input, sensitive data, and state-changing capability (the standard's
  "Rule of Two" coincidence) is escalated for per-action approval design,
  not treated as a routine finding.
- A request to certify prompt-injection defenses as complete is escalated
  back to the requester with the standard's own documented adaptive-testing
  gap, not silently accepted.

## Outputs & verification

- **Outputs:** a threat assessment mapping identified risks to the
  applicable OWASP LLM Top 10 (2026) categories, and blast-radius-bounding
  mitigations matched to each.
- **Verify:** every finding maps to a specific category; no mitigation is
  presented as complete prevention where the source documents it as
  partial; untrusted content never lands in system-level instructions;
  high-impact/irreversible actions are gated on human approval or
  deterministic policy, not model intent.

## References

- [research/technologies/owasp-llm-top10.md](../../research/technologies/owasp-llm-top10.md)
- [research/technologies/anthropic-claude-api.md](../../research/technologies/anthropic-claude-api.md)
- [research/technologies/openai-api.md](../../research/technologies/openai-api.md)
