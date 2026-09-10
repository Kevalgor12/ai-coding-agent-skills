# Individual skill quality review — AI/LLM generic domain (Layer 3)

Date: 2026-09-10. Step 28 of the master build plan: individual quality
review of every generated skill, this file covering the batch of 8
Layer-3 AI/LLM generic skills authored in Step 26 (`SK-AI-001`–`SK-AI-008`)
and capability-fixed in Step 27: `agent-architecture`, `ai-security`,
`llm-application-engineering`, `llm-evaluation`, `model-selection`,
`prompt-context-engineering`, `rag-engineering`,
`structured-output-tool-calling`.

Reviewed against `core/skill-specification/specification.md` (all VR/CE/SG/
QR rules), `core/taxonomy/skill-catalog.md` (the AI/LLM section's approved
catalog entries and merge rationale), `skills/code-commenting/SKILL.md`
(comment-quality yardstick), `skills/observability/{skill.yaml,SKILL.md}`
(reference template), and the three grounding research docs
(`research/technologies/anthropic-claude-api.md`,
`research/technologies/openai-api.md`,
`research/technologies/owasp-llm-top10.md`) with spot-checked factual
claims. All 8 `skill.yaml` files parse as valid YAML. No files were edited
during this review — see "Why nothing was fixed" at the end.

## Summary

| Skill | Critical | High | Medium | Low |
|---|---|---|---|---|
| agent-architecture | 0 | 1 | 0 | 1 |
| ai-security | 0 | 1 | 1 | 1 |
| llm-application-engineering | 0 | 1 | 0 | 0 |
| llm-evaluation | 0 | 0 | 0 | 1 |
| model-selection | 0 | 0 | 1 | 1 |
| prompt-context-engineering | 0 | 0 | 0 | 1 |
| rag-engineering | 0 | 0 | 1 | 1 |
| structured-output-tool-calling | 0 | 0 | 1 | 0 |
| **Total** | **0** | **2** (+1 shared*) | **4** | **6** |

\* The High finding on `llm-application-engineering` is a duplication
finding whose "victims" (`agent-architecture`, `model-selection`) are not
themselves at fault; it is counted once, against the duplicator.

No Critical findings. Every skill passed VR-1 (required fields present),
VR-2 (yaml/SKILL.md frontmatter parity — `name`/`description`/`slug` all
match exactly), VR-3 (every `related_skills`/`conflicts_with` ID resolves
to a real skill), VR-4 (all `depends_on_skills: []`, trivially acyclic),
VR-5 (the Step 27 `shell` capability fix landed correctly on all 7 skills
that needed it, and `model-selection` correctly stays Tier A / no-`shell`
since it produces no code), VR-6 (activation/non-activation disjoint),
CE-1 (all descriptions ≤500 chars, though several are unusually close to
the ceiling — see Low findings), and `related_skills` on every one of the
8 skills matches the catalog's own `Related:` field **verbatim**, field
for field. `depends_on_skills: []` and `conflicts_with: []` on all 8 match
the catalog exactly, confirming check #5/#6 hold with no deviation.

---

## agent-architecture

**High — missing `Testing` body section despite an R condition being met.**
The spec (`specification.md` §3.2, item 11) makes `Testing` **R** "when
the skill produces runnable code." This skill's `outputs` includes
`orchestration-implementation` (`kind: edit`, described as "Agent loop,
state-management, and multi-agent composition **code** applied to the
codebase") — a code-producing output, same shape as
`skills/observability/skill.yaml`'s `instrumentation-changes` output,
which is exactly why `observability`'s `SKILL.md` carries a `Testing`
section. `agent-architecture/SKILL.md` has no `Testing` section at all
(order: Anti-patterns → Security → Performance → Failure handling,
skipping straight past it). A consuming agent implementing an agent loop
from this skill gets no guidance on verifying the loop's termination
condition actually fires, that step/cost limits are actually enforced, or
that state-management doesn't duplicate context — exactly the kind of
check this skill's own `verification` list in `skill.yaml` states but
never gives body-level guidance for.
*Fix:* add a `Testing` section (between Performance and Failure handling)
covering: verifying the loop terminates under the designed condition
(not just "eventually"), exercising the `pause_turn`/approval-resume path
without double-counting steps, and testing state-management strategy
switches don't silently duplicate context — referencing
[testing-strategy](../../skills/testing-strategy/SKILL.md) for suite
mechanics per this project's own "essential rules; depth → reference"
convention.

**Low — description sits 5 characters from the CE-1 500-char ceiling**
(495/500). Not a violation, but any future one-word addition (e.g.
tightening wording elsewhere in this batch, which tends to lengthen
descriptions) will silently overflow CE-1 unless someone notices. *Fix:*
none required now; worth trimming a few words for headroom next time this
file is touched.

No other problems found. Scope/non-goals are precise and match the
catalog; activation/non-activation conditions correctly route single-call
work to `structured-output-tool-calling` and authorization/blast-radius
work to `ai-security`; the four-build-path and state-management content is
accurately sourced (spot-checked against `anthropic-claude-api.md` §2/§11
and `openai-api.md` §2 — quotes match verbatim); the Security section
correctly defers to `ai-security` rather than restating it.

---

## ai-security

**High — missing `Testing` body section despite an R condition being met.**
Same defect class as `agent-architecture`, for the same structural reason:
`outputs` includes `mitigations` (`kind: edit`, "Blast-radius-bounding
mitigations **applied** or proposed... "), a code-producing output when
mitigations are applied rather than only proposed (e.g. adding
context-aware output encoding, parameterized-query fixes, or a
least-privilege credential change). `ai-security/SKILL.md` has no
`Testing` section (order jumps from Security straight to Failure
handling, also skipping Performance — Performance's omission is fine,
it's Optional, but Testing's is not given the edit-output condition).
*Fix:* add a `Testing` section covering: validating a mitigation with
**adaptive** (defense-spec-disclosed) red-teaming rather than only
naive/static testing — the skill's own single most load-bearing empirical
finding (the "static near-zero / adaptive 90%+" gap) belongs here as much
as in Knowledge/Decision framework, since it's literally the discipline
for testing this skill's own output.

**Medium — `owned_knowledge` ambiguity with `rag-engineering` over
"authorize inside the retrieval query."** `ai-security/skill.yaml`
`owned_knowledge` lists *"The authorize-inside-the-retrieval-query pattern
(document/chunk-level authorization enforced at index-query time, not
filtered post-retrieval)"* verbatim as something **this skill** owns.
`rag-engineering/skill.yaml` `owned_knowledge` independently lists
*"Retrieval-authorization-ordering discipline (authorize inside the
query, not post-filter)"* as something **it** owns — and both skills'
`SKILL.md` Knowledge sections state the substantive content directly
(not just a cross-reference), each with their own citation to
`owasp-llm-top10.md` LLM09/LLM02/§8. Per spec §2.7, `owned_knowledge`
exists specifically "to enable the no-duplication check" — two skills
both claiming ownership of the same topic defeats that check's purpose,
even though in this case the actual cross-referencing prose is
reasonable (`rag-engineering`'s Escalation section does correctly route
a found violation "coordinated with SK-AI-008"). This is a metadata
consistency gap, not a prose-quality one. *Fix:* pick one owner (the
catalog's own `rag-engineering` scope note — "this skill owns... two
risks the OWASP LLM Top 10 research documents directly... retrieval-
authorization ordering (LLM09, LLM02)" — suggests `rag-engineering`
should be the sole owner) and have `ai-security` reference it by ID in
`owned_knowledge` instead of re-listing the same pattern as its own.

**Low — description sits 6 characters from the CE-1 ceiling** (494/500).
Same class of finding as `agent-architecture`; no action required now.

No overclaiming found — the one thing this skill's own catalog entry and
this audit's brief specifically called out as a Critical risk. The
skill states *"no reliable prevention mechanism exists today"* verbatim
from the source and consistently frames every mitigation as
blast-radius-bounding, never as prevention, throughout Knowledge,
Decision framework, Engineering rules, and Anti-patterns. This is the
single most important correctness property this skill needed to get
right, and it does.

---

## llm-application-engineering

**High — substantial verbatim duplication of content owned by
`agent-architecture` and `model-selection`, rather than referencing it by
ID.** The spec's QR-2 rule is explicit: "a topic listed in another
skill's `owned_knowledge` MUST be referenced by ID, not restated." Two
concrete instances found in this skill's Knowledge section:

1. **Model-tier defaults**, owned by `model-selection`
   (`owned_knowledge`: *"The capability-vs-cost-vs-latency-vs-context-
   window selection method itself... current tiers are worked examples
   only and will go stale"*). `llm-application-engineering/SKILL.md`
   restates the **exact same quote**, word for word, with the same
   citation, that `model-selection/SKILL.md` also carries: *"If you're
   unsure which model to use, start with Claude Opus 5 for most
   workloads. Use Claude Fable 5.1 for demanding reasoning and
   long-horizon agentic work, or when your evals on Claude Opus 5 at
   higher effort still fall short"* [Source: platform.claude.com/docs/en/
   models/overview] — plus the full `gpt-6-astra`/`gpt-5.6-sol`/
   `gpt-5.6-terra`/`gpt-5.6-luna` tier breakdown, also duplicated
   verbatim.
2. **The four Anthropic build-time options and OpenAI's Agents-SDK-vs-
   raw-Responses-API split**, owned by `agent-architecture`
   (`owned_knowledge`: *"Hand-rolled-loop vs. managed-framework vs.
   fully-managed-runtime decision method, per each vendor's own
   documented control-vs-convenience criteria"*). `llm-application-
   engineering/SKILL.md` restates the same four Anthropic options
   (Messages API/client SDK, Claude Agent SDK, Claude Code CLI, Managed
   Agents) with the same quotes ("Building an agent without implementing
   the tool loop yourself", "Running long-running or asynchronous
   agents without managing your own sandbox or session infrastructure")
   that `agent-architecture/SKILL.md` also carries almost verbatim.

This is exactly the failure mode QR-2 exists to prevent: if either
`model-selection`'s pricing worked-examples or `agent-architecture`'s
build-path framing is updated later (both are explicitly flagged in this
project as time-sensitive/worked-example content), the duplicate copy in
`llm-application-engineering` will silently drift out of sync — the
precise staleness risk `model-selection`'s own scope field warns about
("will go stale — re-verify... before quoting a specific price or tier
name"), now duplicated into a second file that carries no such warning
on its own copy of the same figures. Some summary-level context in a
composition/root skill is legitimate and expected (it needs enough
signal to decide whether a sub-discipline applies), but this goes past
summary into restating the sub-skills' own cited worked examples.
*Fix:* compress both passages to a one-line pointer ("Anthropic
documents four build-time options from hand-rolled to fully managed —
see `agent-architecture` for the criteria" / "both vendors document a
default-then-escalate tiering pattern — see `model-selection` for
current tiers and the staleness caveat"), keeping only the decision
signal (*that* a fork/choice exists) rather than the sourced specifics
(*what* the current options/prices are).

No other problems found. The observability-extension design (folding
LLM-call logging into `SK-QA-004` rather than a ninth skill) is stated
clearly and matches the catalog's own stated rationale; the over-
engineering check (declining agent-architecture/RAG when a single
structured-output call suffices) is concrete and correctly sourced to
both vendors' own overtrigger warnings.

---

## llm-evaluation

No problems found beyond the one shared low-severity note below. Section
order and required/optional sections are all correct for this skill's
`outputs` shape (no `edit`-kind output, so `Testing` is not required by
§3.2's condition — but the skill includes one anyway with real content,
which is permitted and appropriate here since it *is* the LLM-output-
grading method itself). The testing-strategy boundary is explicit and
correctly structural ("LLM output is *graded*... general test authoring
asserts deterministic output true or false"), and `testing-strategy`'s
own `related_skills` independently lists `SK-AI-007` back, confirming the
boundary is agreed on both sides. The OpenAI Evals-platform-deprecation
framing (read-only Oct 31 2026, shutdown Nov 30 2026) is accurately
sourced and correctly treated as a caveat on tooling, not on the
underlying eval-before-ship discipline. Grading-method claims (exact
match / cosine similarity / ROUGE-L / LLM-as-judge, "prioritize volume
over quality," different-model-grades-than-generates) all verified
verbatim against `anthropic-claude-api.md` §9.

**Low — description sits 6 characters from the CE-1 ceiling** (494/500).

---

## model-selection

**Medium — description sits 2 characters from the CE-1 500-char hard
ceiling** (498/500). This crosses from a stylistic nitpick into a
practical maintenance risk: at 2 characters of headroom, essentially any
future word choice (fixing a typo to a longer correct spelling, adding a
single clarifying word) will silently violate a **mechanical validator**
rule (CE-1 is `[V]`), and the failure mode is invisible without running
the validator — nobody editing prose reads it as "500 characters," so
this is more fragile than a normal near-limit case. *Fix:* trim ~10-15
characters of headroom now while the file is otherwise untouched, e.g.
tightening "using Anthropic's and OpenAI's own tiering guidance as worked
examples that go stale" to something a few words shorter.

**Low — the version-awareness framing (check #9) is genuinely strong but
uses prose discipline rather than the spec's formal `version_sensitive_claims`
field.** Verified present and repeated, not merely claimed: the `scope`
field, the `description`, and the SKILL.md's Purpose & scope, Knowledge,
Engineering rules, and Anti-patterns sections all independently restate
that every model name/price is "a worked example... snapshotted
2026-09-10... will go stale." This satisfies the *intent* of VA-2/VA-3
thoroughly. However, `skill.yaml` does not populate the optional
`version_sensitive_claims` list (each: `claim`, `applies_to`, `source_ref`)
that the spec designed specifically for this situation — a skill whose
entire Knowledge section is built from dated pricing/tier/deprecation
facts is close to the canonical use case for that field. *Fix (optional,
not required — the field is `O`):* populate `version_sensitive_claims`
with the pricing/tier-name/context-window figures already called out in
prose, each tagged `applies_to: "as of 2026-09-10, re-verify before use"`.

No other problems found. This is the one skill in the batch not touched
by the Step 27 `shell`-capability fix, and correctly so: its
`required_capabilities: [file-read, file-write]` / `execution_tier: A`
pairing is VR-5-consistent (Tier A ⇒ only file-read/file-write) and
matches its `outputs` shape (both `kind: analysis`, no code produced) —
the Step 27 fix was correctly scoped to exclude it. Pricing/tier figures
for both vendors spot-checked verbatim against `anthropic-claude-api.md`
§1/§8/§12 and `openai-api.md` §4/§12 with no discrepancies found.

---

## prompt-context-engineering

No problems found beyond the shared low-severity note. Both vendors'
prompt-structure frameworks (Anthropic's Be-clear-and-direct/Add-context/
Examples/Role vs. OpenAI's Identity/Instructions/Examples/Context) are
accurately reconciled and cited; the long-context-placement "up to 30
percent" figure, the context-rot quote, and the prompt-caching mechanics
(cache-prefix order, exact-prefix-match requirement) all verified
verbatim against the research docs. The Security section correctly
narrows to the prompt/context-structure side of untrusted-content
handling and defers deeper threat modeling to `ai-security`
(cited by ID, `SK-AI-008`) rather than restating it.

**Low — description sits 10 characters from the CE-1 ceiling** (490/500).

---

## rag-engineering

**Medium — a stale cross-reference in `search-integration` (SK-DATA-005,
outside this batch) misdirects RAG-layer requests away from this skill.**
`search-integration/skill.yaml`'s `non_activation_conditions` states:
*"The request is really about the RAG/LLM-application layer built on top
of vector search (**llm-application-engineering**) — a documented
research gap in this library, not answered here."* That routing target is
stale: at the time `search-integration` was authored, the entire AI/LLM
domain was one placeholder skill (`SK-AI-001`, per this domain's own
taxonomy-design audit, `audits/2026-09-10-ai-llm-domain-validation.md`)
and RAG genuinely was an unresearched gap. Since Step 26, that placeholder
was decomposed into 8 skills, and `rag-engineering` (`SK-AI-005`) now
explicitly, specifically owns "the RAG pattern" per the catalog — yet
`search-integration`'s non-activation text still names the *root* skill
(`llm-application-engineering`) rather than the specific one
(`rag-engineering`). Notably, `search-integration`'s `related_skills`
list *was* updated to include `SK-AI-005` alongside `SK-AI-001`, so the
prose text is the only part left stale — a partial update. A user
reading `search-integration`'s non-activation guidance today would be
routed one hop short of the skill that actually owns the RAG pattern.
This finding is reported here because it affects `rag-engineering`'s
discoverability/boundary correctness, but the fix belongs in
`search-integration`, which is **outside this batch's scope** and was
therefore not edited. *Fix (for whoever owns `SK-DATA-005`):* update
`search-integration/skill.yaml`'s `non_activation_conditions` (and the
matching prose in `search-integration/SKILL.md`, if present) to name
`rag-engineering` instead of, or in addition to, `llm-application-
engineering`.

(See also the `ai-security` section above for the related `owned_knowledge`
overlap between `ai-security` and this skill over the
authorize-inside-the-retrieval-query pattern — not double-counted here.)

**Low — description sits 4 characters from the CE-1 ceiling** (496/500).

No other problems found. The boundary against `search-integration`
itself (engine selection/indexing/relevance tuning stays there; RAG
pattern + retrieval-authorization-ordering + embedding-store sensitivity
stays here) is stated clearly and correctly from this skill's own side.
The two OWASP-sourced claims this skill is built on — cross-tenant
leakage via post-search authorization, and 50–70%/92% embedding-inversion
recovery rates — were verified verbatim against `owasp-llm-top10.md`
§6/§9 with no discrepancy.

---

## structured-output-tool-calling

**Medium — the forcing-semantics comparison table conflates two
different Anthropic/OpenAI mechanisms under one "Intent" row.** The
Knowledge section's table pairs the intent *"Restrict callable subset,
keep full definitions cached"* with Anthropic's `disable_parallel_tool_use`
in one column and OpenAI's `allowed_tools` in the other. Per the cited
research (`anthropic-claude-api.md` §3), `disable_parallel_tool_use` only
*"cap[s] the turn at one tool call"* — it does not restrict *which*
tools are callable, and the research doc never claims it interacts with
caching at all. OpenAI's `allowed_tools`, by contrast, genuinely does
what the row's intent label says: *"restrict the callable subset while
keeping full definitions in context for prompt-caching purposes"*
(`openai-api.md` §3). These are two different mechanisms — "how many
calls can happen this turn" vs. "which specific tools are callable this
turn, cache-preserving" — placed in the same row implies Anthropic has a
documented equivalent to OpenAI's `allowed_tools`, which the cited
research does not support. This is a mischaracterized cross-vendor
parity mapping, not a fabricated API (both cited facts are individually
accurate; only their pairing is wrong), but it would mislead a reader
into reaching for `disable_parallel_tool_use` to solve a
tool-subset-restriction problem it doesn't solve. *Fix:* split the row —
either add a genuine "no documented Anthropic equivalent" note for the
subset-restriction intent, or relabel the `disable_parallel_tool_use` row
with its actual intent ("cap the turn at one tool call") rather than
reusing OpenAI's `allowed_tools` intent label for it.

No other problems found. The "shared underlying enforcement engine"
framing (Anthropic's strict tool use / `output_config.format` and
OpenAI's Structured Outputs, both constrained decoding) is accurately
sourced; the JSON Schema ceiling list (no recursive schemas, no numeric/
string-length constraints, `additionalProperties: false` required) and
the ~20-tool soft-ceiling/`tool_search` discipline both verified verbatim
against the research. The `Testing` section is present and appropriate
given this skill's `edit`-kind `round-trip-implementation` output — this
is the correct pattern the two `High` findings above (`agent-architecture`,
`ai-security`) should also follow.

---

## Why nothing was fixed

Every finding in this review is either (a) a content-authorship gap
(missing `Testing` section content, a duplicated-content passage that
needs rewriting to a pointer, a mischaracterized table row) that requires
editorial judgment rather than a mechanical one-line correction, (b) a
metadata-ownership ambiguity that requires picking a single owner rather
than a clear "this is wrong, that is right" fix, or (c) located in a file
outside this batch (`search-integration`). None matches the audit's
explicit fix-now list (missing required field, YAML syntax error, a CE-1
overflow *in fact occurring*, a `depends_on_skills`/`parents` conflation,
a VR-5 tier/capability mismatch, or a `related_skills`/`conflicts_with`
entry pointing at a nonexistent skill ID) — all of which this batch
passes cleanly. Accordingly no `skill.yaml` or `SKILL.md` file in this
batch was modified, and no post-edit `yaml.safe_load` confirmation was
needed.
