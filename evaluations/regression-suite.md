# Regression Suite

Status: **first content**. Defines when and how this evaluation suite
should be re-run, so it does what a regression suite is for — catching
that something that used to behave correctly has stopped, not just
confirming the state at the moment it was written.

## Current coverage (honest baseline)

16 scenarios across the 8 required categories (`simple` ×2, `ambiguous` ×2,
`multi-skill` ×2, `security-sensitive` ×2, `performance-sensitive` ×2,
`legacy-code` ×2, `failure` ×2, `conflicting-requirement` ×2). 77 of the
86 authored skills appear somewhere in the suite — as a required
activation, a correctly-required exclusion, or an explicitly-named
uncertain/acceptable-either-way case. This is breadth-of-mention, not
depth-of-testing: most skills appear in exactly one or two scenarios, and
9 skills (mostly narrow technology specializations with no scenario
currently exercising their specific domain — e.g. several observability
and infra technology skills) appear in none. **This is not full coverage
of the library, and this document does not claim it is.** Extending
coverage is explicitly future work (see "Growing the suite" below), not a
gap to paper over.

## What triggers a re-run

A re-run of the affected scenario(s) — not necessarily the whole
suite — is warranted whenever:

1. **A skill named in a scenario's activation set changes** — its
   `activation_conditions`, `non_activation_conditions`, `scope`,
   `depends_on_skills`, `parents`, or `conflicts_with` field is edited.
   This is the direct analogue of a technology skill's own
   `reverify_triggers` field (VA-4), applied to the evaluation suite
   instead of to a single skill's factual claims.
2. **A new skill is authored** that could plausibly compete for
   activation in an existing scenario's repository/task context — even if
   the new skill is unrelated to the scenario's original intent, a
   keyword or technology-detection overlap can silently change what a
   compliant router should select. Check new skills against the existing
   16 scenarios' "Repository signals" sections specifically, since those
   are what a detection-gated router keys off of.
3. **`core/taxonomy/skill-catalog.md`, `core/dependency-architecture/`, or
   `core/routing-architecture/` change** — several scenarios (S05
   especially) directly formalize named examples or rules from these
   documents; a change there can invalidate the expected sequencing or
   activation set without any scenario file itself being edited.
4. **`core/orchestrator/` changes** — the invocation/return envelope
   shape, the six statuses, the recovery ladder (F1–F9/R1–R8), the gate
   classes (GA-0…GA-8), or the precedence ladder. Scenarios S13/S14
   (failure classes) and S15 (precedence ladder) are keyed directly to
   specific named rules in these documents and will silently go stale if
   those rules are renumbered or redefined without a corresponding
   scenario update.
5. **A cross-skill audit finds a new instance of an already-tracked
   pattern.** Two corrections were already needed in this suite before it
   was even committed (S06's `SK-BE-005`→`SK-QA-002` edge was
   mischaracterized as composition when the catalog's "Dependencies:"
   line — already flagged in `audits/cross-skill/cross-skill-audit.md` as
   imprecise — was taken at face value). Any future audit finding of the
   same "catalog says X, `skill.yaml` says Y" class should trigger a
   grep across `evaluations/expected-behaviors/` for the same catalog
   line, since the scenario authors necessarily leaned on the catalog as
   a primary source and may have inherited the same imprecision
   elsewhere.

## How to run a scenario today (no harness exists)

Per `evaluation-spec.md`'s honest-scope section, there is no executable
test runner. Running a scenario means:

1. Take a scenario's `scenarios/<id>.md` file (task + repository signals)
   **without** looking at its paired `expected-behaviors/<id>.md` file.
2. Work through the task as a router/orchestrator would, using the actual,
   current skill files in `skills/` as the instructions — either a human
   reviewer role-playing the orchestrator, or an agent explicitly briefed
   to do so (and, per this project's own standing discipline throughout
   its build, an agent doing this should not have the expected-behaviors
   file in its context, for the same reason a student doesn't see the
   answer key while sitting the exam).
3. Record the actual activation set, sequencing, gate decisions, and
   return-envelope-shaped outcomes produced.
4. Only then open the matching `expected-behaviors/<id>.md` file and score
   per `scoring.md`.

## Tracking results over time

Record each suite run as a dated entry, mirroring this project's own
`research/technologies/VERSION_REGISTRY.md` dated-fact convention rather
than inventing a new logging format:

```
## <YYYY-MM-DD> — <what changed since the last run, if anything>

| Scenario | Verdict | Critical | Major | Minor | Notes |
|---|---|---|---|---|---|
| S01 | complete | 1/1 | 3/3 | 2/2 | — |
| ... | | | | | |

Critical-failure list: <scenarios that failed, with the specific assertion>
Regressions since last run: <scenarios that were complete/partial and are now worse>
Newly passing since last run: <scenarios that improved>
```

A regression — a scenario that scored `complete` or `partial` in a prior
run and scores worse now, with no corresponding intentional change to the
skill(s) involved — is the single most important signal this document
exists to produce. A library that only ever adds skills without a
regression check has no way to know whether skill N+1's authoring quietly
broke skill N's activation boundary (exactly the class of finding
`audits/cross-skill/cross-skill-audit.md` X-03/X-14 already surfaced by
hand, once, for the whole library — a regression suite's job is to keep
surfacing it, not to have surfaced it once).

## Growing the suite

Priority order for new scenarios, given the current coverage gap:

1. **The 9 currently-unexercised skills** — check `core/taxonomy/skill-catalog.md`
   for which ones and whether an existing scenario could be extended to
   include them (cheaper) or a new scenario is warranted (only if the
   skill's domain doesn't fit naturally into an existing one).
2. **The findings `audits/cross-skill/cross-skill-audit.md` recommended
   for a human decision but did not resolve** — several of these (the
   VR-4 layer-monotonicity tension, the realtime-transport
   `conflicts_with` gap, the missing debugging/bug-fixing skill) are
   exactly the kind of thing a scenario can test empirically once a
   decision is made, turning an architectural finding into a standing
   regression check against re-occurrence.
3. **Any new domain this library adds** (per the master build plan's
   later steps) should get at least one scenario in whichever of the 8
   categories fits before that domain is considered "done," not as an
   afterthought.

## Relationship to the orchestrator's evaluation hooks

`core/orchestrator/observability-and-evaluation.md` names five hooks
(EH-1 through EH-5) and states plainly that most are inert until "a
fixture format and a harness to run them" (EH-4) exists. This suite's
`scenarios/`+`expected-behaviors/` pairs are that fixture format — each
pair is shaped so a future harness could, in principle, feed a real run's
`(skill, invocation envelope, return envelope, observed criteria)` tuples
against a scenario's assertions automatically. Building that harness
remains explicitly out of scope for this step (per `evaluation-spec.md`'s
honest-scope section) — this document describes the manual process that
is possible today, and the shape that would let it stop being manual
later.
