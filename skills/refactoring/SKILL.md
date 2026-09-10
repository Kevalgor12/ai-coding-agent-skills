---
name: Refactoring
description: >-
  Improve existing code's structure without changing its behavior —
  identify a target, apply changes in small steps, and verify behavior is
  unchanged via tests or explicit equivalence reasoning. Use when asked to
  refactor, or when a change is blocked by structural debt. Never bundles
  feature changes or silently fixes a bug found along the way — hands off
  instead. Requires a safety net or explicit acknowledgement of its
  absence.
spec_version: "1.0"
---

## Purpose & scope

Improve code structure while preserving behavior exactly — identify a
target, apply small verifiable steps, and confirm nothing changed
externally. New feature work is a different activity entirely, not a
variant of refactoring. This skill has a hard dependency on
[testing-strategy](../testing-strategy/SKILL.md): its own procedure
literally invokes that skill's verification method (running the existing
test suite, or reasoning about what tests would need to exist) as part of
every refactor, not as an optional adjacent concern.

## When to use / When not to use

**Use** when the user asks to refactor, or when a change is blocked by
structural debt that needs clearing first. **Do not use** for new feature
work, or when there's no way to verify behavior and the user hasn't
explicitly accepted that risk.

## Knowledge

**A safety net is not optional — it's the precondition that makes
"behavior-preserving" a claim this skill can actually stand behind rather
than an assertion.** Existing tests are the primary safety net; where none
exist, the only acceptable substitute is explicit equivalence reasoning
with the residual risk stated plainly to the user, who must accept it
before the refactor proceeds. Refactoring without either — silently,
hoping nothing breaks — is exactly the failure mode this skill exists to
prevent.

**Small steps are a verification strategy, not a stylistic preference.**
A single large rewrite makes it much harder to isolate which specific
change, if any, altered behavior when something goes wrong; a sequence of
small, independently-verifiable steps means each step can be checked
before moving to the next, and a regression can be attributed to a
specific, narrow change rather than diagnosed across an entire rewrite.

**Finding a bug during a refactor is a hard stop for fixing it inline —
report and hand off instead.** The entire premise of a refactor is that
external behavior doesn't change; silently fixing a bug found along the
way *is* a behavior change, however small or clearly correct it seems.
Bundling it into the refactor means the refactor's own "behavior
preserved" claim is no longer true, and it conflates two changes that
should be reviewed, tested, and reasoned about separately.

## Decision framework

1. **Does a safety net exist** (tests covering the target code)? If yes,
   use it to verify every step. If not, has the user explicitly accepted
   the risk of an unverifiable refactor? If neither, stop and ask before
   proceeding.
2. **Is this actually a behavior-preserving change, or does it change
   what the code does?** If the latter, it's not a refactor — it's a
   feature change (or a bug fix), and belongs to a different activity
   with its own review/testing expectations.
3. **Can this be broken into smaller, independently-verifiable steps**
   rather than one large rewrite? Prefer the smaller steps — each one is
   individually checkable.
4. **Did this surface a bug in the existing code?** If so, stop, report
   it, and hand off — don't fix it inline as part of the refactor.
5. **Is shell/test-execution capability actually available** in this
   environment? If not, degrade to reasoning-only verification with the
   caveat stated explicitly, rather than silently skipping verification.

## Workflow

1. Confirm a safety net exists, or get explicit user acceptance of the
   risk if it doesn't.
2. Identify the refactoring target and plan small, independently-
   verifiable steps.
3. Apply each step, running available tests (or reasoning about
   equivalence) after each one.
4. If a bug surfaces along the way, stop, report it, and hand off rather
   than fixing it inline.
5. State how behavior-preservation was verified as part of the output —
   tests passing, or explicit equivalence reasoning with the risk stated.

## Engineering rules

- Never proceed without a safety net or explicit, stated user acceptance
  of the risk.
- Apply changes in small, independently-verifiable steps, not one large
  rewrite.
- Never bundle a feature change into a refactor.
- Never silently fix a bug found during a refactor — report and hand
  off instead.
- State explicitly how behavior-preservation was verified.

## Trade-offs

Small-step refactoring takes more individual verification cycles than one
large rewrite, but makes any regression immediately attributable to a
specific, narrow change rather than requiring a full re-diagnosis across
an entire rewrite — worth the extra cycles for anything beyond a trivial
change.

## Anti-patterns

- **Refactoring with no safety net and no explicit user acceptance of the
  risk** — proceeding silently without either.
- **One large, unreviewable rewrite** instead of small, independently-
  verifiable steps.
- **Bundling a feature change into a refactor** — conflates two activities
  that should be reviewed and tested separately.
- **Silently fixing a bug discovered mid-refactor** instead of reporting
  and handing off — this itself is an unacknowledged behavior change.
- **Claiming "behavior preserved" without actually verifying it** — either
  via tests or explicit equivalence reasoning.

## Security

Not a primary concern for this skill's scope; if a refactor touches
security-sensitive code, defer to
[security-engineering](../security-engineering/SKILL.md) for the
security review, while this skill continues to own behavior-preservation
verification.

## Performance

A refactor should not silently degrade performance as a side effect of
restructuring; if a performance-sensitive path is being refactored, note
that explicitly and consider handing off to
[performance-engineering](../performance-engineering/SKILL.md) for
verification beyond behavioral correctness.

## Testing

This skill's entire verification method is delegated to
[testing-strategy](../testing-strategy/SKILL.md) — running existing tests
is the primary safety net; where tests don't exist, this skill states the
gap rather than inventing an unverifiable claim of correctness.

## Failure handling

- If no tests exist and the user hasn't explicitly accepted the risk, ask
  before proceeding.
- If shell/test-execution capability isn't available, degrade to
  reasoning-only verification with the caveat stated explicitly.

## Escalation

- A bug discovered during refactoring is reported and handed off, never
  silently fixed inline.
- A refactor with no available safety net proceeds only after the user
  explicitly accepts that risk.

## Outputs & verification

- **Outputs:** refactored code with unchanged external behavior, and a
  statement of how behavior-preservation was verified.
- **Verify:** existing tests still pass, or explicit equivalence
  reasoning with stated risk is provided; no behavior change is bundled
  in; changes were applied in small, verifiable steps.

## References

- [core/taxonomy/skill-catalog.md](../../core/taxonomy/skill-catalog.md) — SK-CONV-004 taxonomy entry.
