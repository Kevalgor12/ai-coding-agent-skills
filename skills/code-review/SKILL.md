---
name: Code review
description: >-
  Review a change for correctness, quality, security, and convention
  adherence — find correctness bugs directly, delegate security/perf
  findings to their domain skills, check comment and code-quality
  convention adherence, rank findings by severity, and distinguish
  confirmed from speculative issues. Use when a change is up for review,
  the user asks for a review, or as a pre-merge gate. Not for authoring
  net-new code.
spec_version: "1.0"
---

## Purpose & scope

Review a diff/PR/changeset for correctness, quality, security, and
convention adherence, aggregating findings into ranked, actionable output.
This is the general review skill — it has hard dependencies on four
sibling skills whose findings it delegates to rather than re-derives:
[security-engineering](../security-engineering/SKILL.md) (security
findings), [performance-engineering](../performance-engineering/SKILL.md)
(performance findings), [code-commenting](../code-commenting/SKILL.md)
(comment-convention adherence), and
[code-quality](../code-quality/SKILL.md) (structural-quality convention
adherence). This skill's own, non-delegated job is finding correctness
bugs directly and aggregating/ranking the full set of findings — including
the delegated ones — into one coherent review.

## When to use / When not to use

**Use** when a change is up for review, the user asks for a review, or as
a pre-merge gate. **Do not use** for authoring net-new code (the build
skills own that, though they may self-check), or when there's no change
to review.

## Knowledge

**Delegation, not duplication, is the structural design of this skill —
and getting this wrong (re-deriving security/performance findings
independently) is the most likely way this skill drifts from correct
behavior over time.** Security and performance are each large, evolving
domains with their own dedicated skills, source-grounded knowledge maps,
and decision frameworks — re-implementing even a subset of that logic
inside a review pass risks the review giving different, potentially
stale or inconsistent, guidance than the dedicated skill would. This
skill's job is to *invoke* security-engineering and performance-
engineering for their respective facets and *aggregate* the result, not
to reason about injection risk or query-plan cost independently.

**Correctness-bug-finding is this skill's one genuinely undelegated
responsibility, and it's the part no other skill in this library owns.**
No sibling skill is scoped to "does this code actually do what it's
supposed to do, correctly, given the stated intent" — that's squarely
this skill's own territory, distinct from security (does it introduce a
vulnerability), performance (is it slow), quality (is it well-structured),
or comments (does it explain itself well). A change can be secure,
performant, well-structured, and well-commented while still being
*wrong* — that's the gap this skill fills.

**Ranking by severity and distinguishing confirmed from speculative
findings are both load-bearing, not cosmetic presentation choices.** An
undifferentiated list of findings — mixing a definite null-pointer bug
with a maybe-relevant style nitpick — forces the reader to do the
triage this skill should have already done. A finding presented as
confirmed when it's actually a hypothesis ("this might cause an issue
if...") misleads the reviewer's trust calibration for every other finding
in the same review; distinguishing the two explicitly is what keeps that
trust calibrated correctly across many reviews over time.

## Decision framework

1. **Is this a correctness bug** (the code doesn't do what it's supposed
   to, given the stated intent)? If so, this skill finds and reports it
   directly.
2. **Does this finding belong to security, performance, comment-
   convention, or code-quality-convention territory?** If so, delegate to
   the relevant skill rather than adjudicating it independently — this is
   the single most important discipline this skill has.
3. **Is this finding actually confirmed, or a plausible-but-unverified
   hypothesis?** Mark it accordingly — never present a hypothesis as a
   confirmed defect.
4. **What's this finding's actual severity** relative to the others in
   this review? Rank explicitly rather than presenting an undifferentiated
   list.
5. **Is PR-posting capability actually available** in this environment
   (Tier C, not uniform per this library's capability map)? If not,
   report findings directly rather than claiming to have posted them.

## Workflow

1. Read the diff/PR/changeset and repo conventions.
2. Find correctness bugs directly — this skill's own, undelegated
   responsibility.
3. Invoke security-engineering and performance-engineering for their
   respective facets; invoke code-commenting and code-quality for
   convention-adherence checks.
4. Aggregate all findings (direct + delegated) into one list.
5. Rank by severity; mark each as confirmed or speculative.
6. Report the findings, posting to the PR where the host allows (Tier C),
   otherwise reporting directly.

## Engineering rules

- Delegate security/performance findings to their domain skills; never
  re-derive that logic independently.
- Delegate comment-convention and code-quality-convention checks to
  code-commenting/code-quality rather than applying an ad hoc standard.
- Rank findings by severity explicitly.
- Mark every finding confirmed or speculative — never blur the two.
- Focus this skill's own direct-finding effort on correctness bugs, the
  one facet no sibling skill owns.

## Trade-offs

Delegating to sibling skills costs an extra invocation per review compared
to a single monolithic review pass, but keeps each domain's logic in one
place — a security-relevant change in guidance only needs to update
security-engineering, not every skill that touches security-adjacent
code.

## Anti-patterns

- **Re-deriving security or performance analysis independently** instead
  of delegating to security-engineering/performance-engineering.
- **Applying an ad hoc comment or code-quality standard** instead of
  delegating to code-commenting/code-quality.
- **Presenting findings as an undifferentiated list** with no severity
  ranking.
- **Presenting a speculative hypothesis as a confirmed defect** — misleads
  trust calibration across the whole review.
- **Reviewing net-new code as if it were an existing changeset** — that's
  the build skills' own self-check territory, not this skill's.

## Security

Security findings are entirely delegated to
[security-engineering](../security-engineering/SKILL.md) — this skill
invokes and aggregates rather than re-deriving security analysis.

## Performance

Performance findings are entirely delegated to
[performance-engineering](../performance-engineering/SKILL.md) — this
skill invokes and aggregates rather than re-deriving performance analysis.

## Testing

Whether a change actually has adequate test coverage is itself a
correctness-adjacent finding this skill can surface directly, pointing to
[testing-strategy](../testing-strategy/SKILL.md) for the deeper
layer-selection method rather than re-deriving it.

## Failure handling

- If a finding could plausibly belong to a delegated skill's domain,
  route it there rather than adjudicating it independently.
- If PR-posting capability isn't available, degrade to reporting findings
  directly rather than claiming to have posted them.

## Escalation

- A finding indicating an actively-exploitable security issue is
  escalated immediately per security-engineering's own escalation rule,
  not queued as a routine review comment.
- PR-posting is Tier C and not uniform across agent hosts — state the
  constraint rather than assuming posting capability exists.

## Outputs & verification

- **Outputs:** actionable, severity-ranked findings, distinguishing
  confirmed from speculative, optionally posted as PR comments where the
  host allows.
- **Verify:** every finding is ranked and marked confirmed/speculative;
  security/performance findings are delegated, not re-derived; comment/
  quality checks route through their own skills.

## References

- [core/taxonomy/skill-catalog.md](../../core/taxonomy/skill-catalog.md) — SK-CONV-007 taxonomy entry.
