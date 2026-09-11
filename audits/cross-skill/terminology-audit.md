# Terminology & Output-Contract Audit (Step 29)

Companion to [`cross-skill-audit.md`](cross-skill-audit.md). Covers check 9
(the same concept named differently across skills) and check 10
(similar skills declaring differently-shaped `outputs`) — grouped because
both are contract-shape consistency concerns, and both matter for the same
reason: `core/orchestrator/state-and-contract.md` builds its invocation
envelope by *reading* what a skill declared and produced, so inconsistent
vocabulary and inconsistent output shapes both degrade the same mechanism.

Context for the risk: 86 skills were authored across roughly 15 separate
batches over time, by different agents, in an order where later batches
could not see earlier ones' choices. Terminology drift is the expected
failure mode. **It mostly did not happen** — the findings below are three
real inconsistencies against a background of unusually uniform vocabulary.

---

## Part 1 — Terminology (check 9)

### T-01 · Three competing version-tag syntaxes, seven files mixing two — Medium

**The most consequential terminology finding, because it blocks a
`[V]`-marked rule from ever being validated.**

VA-2 requires that "any claim true only for some versions MUST be tagged
(inline in the body and in `version_sensitive_claims`) with the range it
holds for. Untagged version-specific claims FAIL." It is marked `[V]` —
mechanically checkable. But the specification never fixes the marker's
form, and the corpus grew three:

| Form | Example | Skills | Occurrences |
|---|---|---|---|
| `[Version-sensitive, >=X]` | `**[Version-sensitive, >=18]** \`oauth\` (SASL \`OAUTHBEARER\`)` | 13 | 59 |
| `**[Version-sensitive, …]**` (bolded whole marker) | `**[Version-sensitive, breaking change, >=8.0]**` | 7 | 32 |
| `Version-sensitive:` (prose lead-in, no brackets) | `Version-sensitive: Express 5 changed …` | 9 | 30 |

**Seven skills use two forms inside the same file**: `angular`,
`clickhouse`, `express`, `mongoose`, `mui`, `redis`, `typeorm`. Four use
only the bracketed form, three only the bare-prose form.

Why this is more than cosmetic:

- A validator implementing VA-2 has no anchor to match on. The bracketed
  forms are greppable; `Version-sensitive:` at the start of a sentence is
  not reliably distinguishable from ordinary prose.
- The bracketed form usually carries the range inline
  (`[Version-sensitive, >=8.0]`), which is what VA-2 actually demands; the
  prose form frequently does not, pushing the range into the following
  sentence where it cannot be extracted.
- Version awareness is one of this library's two headline anti-failure
  properties (the other being source grounding, whose marker — `[Source:
  …]` — is by contrast **perfectly uniform**: 1,622 occurrences across 74
  skills, zero variants, zero `(Source:` or lowercase forms). The
  contrast is instructive: `[Source:` was specified concretely by example
  in §3.2 item 3; `[Version-sensitive` never was.

**Recommendation:** pick one form — I recommend `[Version-sensitive, <range>]`,
the most-used and the only one that reliably carries the range inline —
write it into §3.2 and VA-2 the way `[Source: …]` already is, then
normalize the 62 non-conforming occurrences. The normalization is a
mechanical sweep, but it should follow the spec decision, not precede it.

### T-02 · Four interchangeable ways to mark a knowledge gap — Medium

"Mark unresolved, don't guess" is one of this project's most-cited working
rules, backed by `research/technologies/UNRESOLVED.md`. Thirty-three
skills mark a gap. They do it four ways:

| Form | Skills | Typical use |
|---|---|---|
| `**Unresolved**` / `Unresolved:` | 20 | a specific fact the research could not confirm |
| "research gap" | 7 | a whole capability the library has not researched |
| "documented gap" | 11 | same, referring to a tracked entry |
| "not researched" | 2 | same |

Six skills use two or three forms in one file (`clickhouse`, `express`,
`postgresql`, `realtime-communication`, `sass`, `search-integration`).

There is a *latent* distinction here that is worth preserving rather than
flattening: **`Unresolved` marks a fact this skill could not verify**
(e.g. `clickhouse`: "exact LDAP/Kerberos external-authenticator support…
only surfaced via search-result summaries… treat as needing
re-verification"), whereas **"research gap" marks a capability the library
has deliberately not covered** (e.g. `observability` on resilience
patterns). Those are genuinely different things with different remedies —
one needs a doc re-check, the other needs a research pass and a
`taxonomy-analysis.md` entry.

**Recommendation:** name the distinction rather than merging the terms.
Two canonical markers: `**Unresolved:**` for an unverified fact inside
scope, and `**Out of scope (research gap):**` for a capability outside it,
the latter required to link to the `taxonomy-analysis.md#missing-capabilities`
row. That would also have caught X-09 — the AI domain's vendor-breadth
limitation is disclosed nowhere in either form.

### T-03 · Minor variants, no action recommended — Low

Checked and found acceptable; recorded so a future reviewer does not
re-litigate them:

| Concept | Variants found | Verdict |
|---|---|---|
| Human gate | "explicit confirmation" (29 skills), "explicit user confirmation" (10), "human approval" (2) | Same meaning, all unambiguous. Not worth a sweep. |
| Capability degradation | "degrade to advisory" (23), "advisory output" (4), "advisory-only" (3) | Consistent enough; "degrade to advisory" is clearly dominant and the others read as its noun forms. |
| Untrusted data | "untrusted input" (6), "untrusted content" (6), "user input" (7), "user-supplied" (3) | The AI skills' "untrusted content" vs. AppSec's "untrusted input" is arguably a *useful* distinction (documents/tool results vs. request parameters). Leave. |
| Accessibility | "accessibility" (83 in 7 skills), "a11y" (6 in 3) | Both used, always in-context. Fine. |
| End-to-end tests | "end-to-end" (8 skills), "e2e" (3) | Fine. |
| Cross-cutting | "cross-cutting" — 48 uses, 34 skills, **zero variants** | Exemplary. |
| Layer-4 skills | "technology skill" (25 skills), "Layer-4 skill" (1), "tech skill" (1) | Dominant form is clear. |
| Parent | "parent skill" (21 skills), "Layer-3 parent" (1) | Fine. |
| N+1 | `N+1` — 39 uses, 8 skills, **zero case variants** | Exemplary. |

### T-04 · One place where terminology drift caused a coverage gap — Low

`observability` (SK-QA-004) never uses the phrases **"structured
logging"** or **"correlation ID"** anywhere in its body, and uses "SLO"
once. Its catalog entry's Responsibilities open with "Structured logging;
meaningful metrics; distributed tracing", and its catalog **evaluation
requirement** is:

> Produces structured logs with correlation IDs and metrics tied to
> stated SLOs, without logging secrets/PII

The body covers the underlying concepts well — signal selection, the
cardinality trap, PII-in-any-signal risk, OpenTelemetry's log/trace
auto-correlation — so this is not a missing capability. But an evaluation
written from the catalog's wording could not be shown to pass against the
skill's own vocabulary, and `evaluations/` is where these criteria are
supposed to become tests.

Notably, `llm-application-engineering` — which explicitly extends
`SK-QA-004` — *does* use "structured request/response logging" and
"request id". The child speaks the catalog's language; the parent does
not.

**Recommendation:** fold into the catalog reconciliation decision (main
audit, "the catalog is drifting"). If the catalog stops being normative,
the eval criteria should be re-derived from `skill.yaml.evaluation_criteria`
instead — which is the field the spec actually designates for this.

---

## Part 2 — Output contracts (check 10)

### T-05 · The `outputs.kind` enum is used as a two-value enum with sporadic exceptions — Medium

The spec defines five `kind` values: `edit`, `artifact`, `analysis`,
`data`, `command-run`. Across 204 output items in 86 skills:

| kind | uses | skills |
|---|---|---|
| `analysis` | 110 | most |
| `edit` | 87 | 61 |
| `command-run` | 5 | 5 |
| `artifact` | 2 | 1 |
| `data` | **0** | 0 |

Two problems follow.

**(a) `command-run` is declared by 5 of ~45 shell-capable skills doing
identical work.** `postgresql` and `redis` declare a `commands-run`
output; `clickhouse`, `python`, and `shadcn-ui` do too. But
`jest-vitest` (runs the test suite), `playwright` (runs browsers),
`docker` (builds images), `drizzle` / `prisma` / `typeorm` (run migration
CLIs), `opentelemetry`, `go`, and `data-migration` all declare
`shell` in `required_capabilities`, all execute commands as their core
function, and none declares a `command-run` output.

Five skills chose to model command execution as an output; forty chose not
to; nothing in the spec says which is right. This is the clearest
"similar skills declaring differently-shaped outputs for comparable work"
instance in the corpus.

**(b) `artifact` is effectively unused, and the `edit` / `artifact` line
is undrawn.** `project-management` is the only skill declaring
`artifact` (2 items). Meanwhile `ci-cd-pipeline` declares a newly-created
workflow YAML as `edit`, `containerization` declares a newly-created
Dockerfile and compose file as `edit`, `technical-documentation` declares
newly-written docs as `edit`, and `github-actions` declares
`edit: workflow-yaml`. Whether creating a new standalone file is an `edit`
or an `artifact` has no answer in the spec, and the corpus answered
"`edit`" 87 times and "`artifact`" twice — apparently by accident rather
than by rule.

`data` is never used at all, which may simply mean no skill produces
structured data — plausible, since even `analysis` outputs are prose.

**Why this matters beyond tidiness:** `core/orchestrator/state-and-contract.md`
R-2 already concedes that the invocation contract is "a normalization
schema, not a protocol" — the orchestrator *constructs* each skill's
return envelope by reading what it produced, guided by the declared
`outputs`. A `kind` enum whose values are applied inconsistently makes
that reconstruction less reliable in exactly the cases where it matters
most: a `command-run` that actually mutated state, versus an `analysis`
that only described one. This also connects to the same document's open
question 3 ("should the return envelope become a real emitted
structure?") — if it ever does, this enum is the vocabulary it inherits.

**Recommendation:** define the four live values by their *side effect*,
not their medium, in the spec — `edit` (mutates repository content),
`artifact` (produces a new standalone deliverable not part of the
codebase, e.g. an issue draft or a release note), `analysis` (produces no
side effect), `command-run` (executes something whose effect is outside
the repository) — and state whether `command-run` is required whenever
`shell` is in `required_capabilities`. Then normalize. This is a spec
decision first; the sweep is trivial afterwards.

### T-06 · Output naming conventions are perfectly uniform *(positive)*

All 204 output `name` values are kebab-case. Zero snake_case, zero
spaces, zero Title Case, zero exceptions across 86 independently-authored
skills. All 204 items carry exactly the three required keys
(`name`, `kind`, `description`) with no extras and no shape variation.

The only wrinkle is informational: 33 of the 40 technology skills declare
an output literally named `analysis` (alongside a more specific one such
as `version-compatibility-analysis` or `runner-choice`). It is uniform, so
it is not an inconsistency — but "analysis" carries no information about
*what* was analyzed, which slightly weakens the contract for the one thing
the orchestrator reads it for. Low priority; noted, not recommended for
change.

---

## Summary

| ID | Finding | Severity | Blocking a spec rule? |
|---|---|---|---|
| T-01 | Three version-sensitive marker syntaxes; 7 files mix two | Medium | **Yes — VA-2 `[V]`** |
| T-02 | Four gap-marking forms conflating "unverified fact" with "out of scope" | Medium | No, but weakens the project's core honesty convention |
| T-05 | `outputs.kind` used as a two-value enum; `command-run` in 5 of ~45 shell skills; `edit`/`artifact` line undrawn | Medium | No, but degrades the orchestrator's envelope reconstruction |
| T-04 | `observability`'s vocabulary doesn't match its own catalog eval criterion | Low | Affects `evaluations/` |
| T-03 | Minor synonym variants | Low | No — no action recommended |
| T-06 | Output naming 100% uniform | *positive* | — |

**Overall:** for a corpus authored in ~15 disconnected batches, the
vocabulary is far more consistent than expected. The `[Source: …]` marker
(1,622 uses, zero variants), `cross-cutting` (48 uses, zero variants),
`N+1` (39 uses, zero variants), and kebab-case output names (204 of 204)
are all evidence of strong convention transmission. **Every terminology
inconsistency found is in a place the specification declined to fix a
concrete form** — version markers, gap markers, and `kind` semantics are
each described by intent rather than by example, while `[Source:]`, which
*was* given by example, never drifted. That is the actionable lesson:
where this spec shows a form, authors follow it exactly; where it
describes one, they invent.
