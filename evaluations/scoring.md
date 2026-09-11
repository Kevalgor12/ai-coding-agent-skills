# Scoring

Status: **first content**. Defines how a run of a scenario becomes a score,
formalizing the `critical`/`major`/`minor` weight vocabulary every one of
the 16 scenarios in `expected-behaviors/` already uses (117 assertions
total: 36 critical, 54 major, 27 minor) — this document did not exist when
those files were written, so they each carried a locally-consistent but
undeclared version of this scheme. Nothing below required changing any
scenario's weight assignments; they already agree with each other.

## What is being scored

Per `evaluation-spec.md`, a scenario's `expected-behaviors/` file is a list
of **behavioral assertions**, each checkable against what a run actually
did — its activation set, its invocation/return envelopes
(`core/orchestrator/state-and-contract.md` Part 2), its gate records, its
recovery-ladder choices — never against the prose a model happened to
generate. Scoring a run means checking each assertion in the matching
`expected-behaviors/` file against the run's actual record and marking it
`pass`, `fail`, or `not-applicable` (an assertion can be N/A if the run
never reached the state it presupposes — e.g. a recovery-ladder assertion
is N/A if the failure it responds to never occurred because an earlier
step was itself scored `fail`).

## The three-tier weight vocabulary

| Weight | Meaning | Effect on scenario score |
|---|---|---|
| **critical** | The assertion tests the scenario's core behavioral claim — the one thing this scenario exists to check (e.g. S01: does the router avoid over-activating on a simple query fix; S13: does a failed verification check actually block `complete` status). | **A single failed `critical` assertion fails the whole scenario**, regardless of how many `major`/`minor` assertions passed. This mirrors IC-6 (status honesty) at the meta level: a scenario cannot be scored "mostly passing" if its central claim is false. |
| **major** | A real, meaningfully-scored behavioral requirement that isn't the scenario's central claim but still reflects one of the 15 dimensions in `evaluation-spec.md` (e.g. correct sequencing, a specific security caveat, a specific escalation path). | Each failed `major` assertion counts as one deduction (see scenario scoring below). A scenario with all `critical` assertions passing but several `major` failures is `partial`, not `pass`. |
| **minor** | A real but lower-stakes check — often a completeness or precision point (e.g. S09's distractor-avoidance, S15's "don't cite the wrong rung even if the eventual behavior is right"). | Tracked and reported, but does not by itself change a scenario's `pass`/`partial`/`fail` verdict — it affects tie-breaking between two otherwise-equal runs (see below) and is aggregate-tracked across the suite for `regression-suite.md`'s trend view. |

This mirrors, deliberately, the orchestrator's own six-status model
(`complete`/`partial`/`blocked`/`refused`/`failed`/`deferred`) rather than
introducing a fourth vocabulary: a scenario's verdict is stated using the
**same status words** a real run would carry, not a separate
pass/fail/score-out-of-10 system. See "Scenario verdict" below.

## Assertion-level scoring

For each assertion in an `expected-behaviors/` file:

1. **Locate the evidence.** Every well-formed assertion names what to check
   (a `routing_record` entry, a return-envelope field, a gate record, a
   recovery-ladder rung). Find that evidence in the run's actual record.
2. **Score `pass`** if the evidence matches the assertion exactly as
   stated. Partial or "spirit of the rule" matches are not `pass` — this is
   the same IC-6 discipline the orchestrator itself applies: no unearned
   credit.
3. **Score `fail`** if the evidence contradicts the assertion, or if the
   assertion's presupposed evidence is simply absent when it should exist
   (e.g. assertion says "the security step's `verification[]` includes an
   injection-risk check" and no such entry exists at all — that is a
   `fail`, not `not-applicable`).
4. **Score `not-applicable`** only when the run's actual path genuinely
   never reaches the state the assertion presupposes, AND that divergence
   is itself explainable by an earlier, correctly-scored decision (e.g. a
   recovery-rung assertion is N/A if the step it would have recovered
   never failed). An assertion marked N/A to avoid scoring an inconvenient
   failure is itself a scoring error — when in doubt, score `fail` and
   explain why, rather than N/A.
5. **Uncertain/acceptable-either-way skills** (a category several
   scenarios name explicitly, e.g. S01's `database-operations`) are not
   independently scored as pass/fail for inclusion or exclusion — a run is
   never penalized for going either way on a skill in this category. Any
   assertion that *does* penalize a specific choice on an explicitly-named
   uncertain skill is itself miscalibrated and should be corrected in the
   scenario file, not enforced as written.

## Scenario verdict

A scenario's overall verdict uses the same six-status vocabulary as a
skill invocation, applied to the whole scenario:

| Verdict | Condition |
|---|---|
| **complete** | Every `critical` assertion passes, and every `major` assertion passes. |
| **partial** | Every `critical` assertion passes, but at least one `major` assertion fails. |
| **failed** | At least one `critical` assertion fails. |
| **blocked** | The evaluator cannot determine pass/fail for one or more `critical` assertions because the run's record is incomplete or ambiguous (e.g. no gate record was kept, so a gate-related critical assertion can't be checked either way) — this is a defect in the *run's own record-keeping* (OB-1 through OB-7), not automatically a content failure, and should be reported as `blocked` rather than guessed at in either direction. |

`refused` and `deferred` are not scenario verdicts — they are things a
*step inside* a scenario can legitimately do (and several scenarios expect
exactly this, e.g. S08's refund action should be `refused`-until-gated).
The scenario verdict is about whether the **overall run's behavior matched
the expected-behaviors file**, not whether any individual step's own
status word was `complete`.

Minor-assertion failures are recorded but do not change the verdict; they
are surfaced separately (see below) so two runs that both reach
`complete` are still distinguishable by precision.

## Reporting a scored run

A scored run should be recorded as:

```
Scenario: <id>
Verdict: complete | partial | failed | blocked
Critical: <n passed> / <n total>
Major:    <n passed> / <n total>
Minor:    <n passed> / <n total>
Failed assertions: <list, with the assertion text and what evidence contradicted it>
N/A assertions: <list, with the one-sentence reason each was genuinely inapplicable>
```

This is intentionally the same shape as this project's own audit findings
(`audits/individual-skills/*.md`, `audits/cross-skill/*.md`) — a run's
scoring output should be as inspectable and citable as this library's own
review process has been throughout its build.

## Suite-level aggregation

A suite run (all 16 scenarios) is summarized as:

- **Pass rate**: fraction of scenarios reaching `complete`.
- **Critical-failure list**: every scenario that reached `failed`, with its
  specific failed critical assertion(s) — this is the list a maintainer
  reads first.
- **Per-dimension breakdown**: since every assertion is tagged with one or
  more of the 15 dimensions from `evaluation-spec.md`, aggregate pass rate
  *per dimension* across all 16 scenarios — this answers "is the library
  weak at security behavior specifically, or at sequencing specifically,"
  not just "is scenario 7 broken."
- **Per-category breakdown**: aggregate by the 8 scenario categories, since
  a library that's strong on simple tasks but weak on conflicting-requirement
  handling is a different problem than the reverse.

## What this scoring method deliberately does not do

- **It does not produce a single numeric score for the whole library.** A
  single number (e.g. "87% pass rate") invites exactly the kind of
  false precision `core/orchestrator/observability-and-evaluation.md`'s
  EH-3 section already warned against for individual runs ("a single
  production run is not an evaluation... it is a data point for a future
  suite"). The critical-failure list and per-dimension breakdown are the
  actionable outputs; a headline percentage is not.
- **It does not average across scenarios of different weight.** A suite
  where 15 scenarios are `complete` and 1 is `failed` on a `critical`
  security assertion is not "94% healthy" — it has one finding that needs
  fixing before anything else, exactly as this project's own audits have
  never averaged Critical findings away against a large count of clean
  skills.
- **It does not claim statistical confidence from one run.** Per EH-3, a
  single scored run is an *observation*, not proof a skill "passes its
  evaluation criteria" in general. `regression-suite.md` covers what
  repeated scoring over time is for.
