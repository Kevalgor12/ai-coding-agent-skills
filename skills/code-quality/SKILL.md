---
name: Code quality
description: >-
  Enforce clean, readable, idiomatic code — meaningful naming, appropriate
  function/module size, cohesion, avoiding dead code and duplication and
  premature abstraction, language-idiomatic structure. Use when writing
  non-trivial code or a quality pass is requested. Not for correctness
  bugs (code-review) or performance (performance-engineering).
spec_version: "1.0"
---

## Purpose & scope

Enforce structural/readability code quality — naming, size, cohesion,
dead-code and duplication avoidance — independent of language, specialized
by each Layer-4 language/technology skill for idiom. Correctness bugs
belong to [code-review](../code-review/SKILL.md); performance belongs to
[performance-engineering](../performance-engineering/SKILL.md).

## When to use / When not to use

**Use** when writing non-trivial code, a quality pass is requested, or
dead code/duplication/over-abstraction is suspected. **Do not use** for an
explicitly-accepted throwaway spike or quick prototype.

## Knowledge

**Naming should be meaningful and specific enough that it eliminates the
need for a comment explaining what a thing is** — this is the direct
handoff point to [code-commenting](../code-commenting/SKILL.md): good
naming and structure are why most code needs few comments in the first
place. A variable named `data` or a function named `process` communicates
nothing a reader couldn't already infer from the type signature; a name
that captures the actual domain concept does real work.

**Dead code and premature abstraction are two failure modes in opposite
directions, and both need active vigilance, not just one or the other.**
Dead code (unreachable branches, unused exports, commented-out blocks left
"just in case") accumulates silently and misleads readers about what
actually runs. Premature abstraction — an interface, a config option, a
generic layer built for a hypothetical future need that hasn't
materialized — is the opposite mistake: complexity paid for upfront with
no current benefit. Both should be actively removed/avoided, and neither
is more acceptable than the other just because it "might be needed later."

**Duplication reduction requires distinguishing genuine repeated logic
from superficially similar but semantically distinct code — collapsing
the wrong kind of "duplication" creates a false abstraction that's worse
than the repetition it replaced.** Two functions that happen to look
similar today but represent genuinely different business rules will drift
apart over time; forcing them into one shared implementation couples
unrelated concerns and makes future changes harder, not easier. Only
consolidate duplication that represents the *same* logic expressed twice,
not merely similar-looking code.

**Function/module size and cohesion are about matching structure to
actual responsibility boundaries, not hitting an arbitrary line-count
target.** A function should do one coherent thing; when it does several
unrelated things, that's a cohesion problem regardless of line count, and
a long function that does one genuinely complex thing coherently isn't
automatically a quality problem just because it's long.

## Decision framework

1. **Does this name communicate the actual domain concept**, or is it
   generic enough that a comment would be needed to explain it? If the
   latter, improve the name rather than adding a comment to compensate.
2. **Is this code actually dead** (unreachable, unused, commented-out with
   no stated reason)? If so, remove it — don't leave it "just in case"
   without an explicit, stated reason for keeping it.
3. **Is this abstraction solving a problem that exists now, or a
   hypothetical future one?** If the latter, it's premature — build the
   concrete case first, generalize when a second real need appears.
4. **Is this apparent duplication actually the same logic, or superficially
   similar but semantically distinct?** Only consolidate the former;
   forcing the latter into a shared abstraction creates a false coupling.
5. **Does this function/module do one coherent thing?** If it does several
   unrelated things, that's a cohesion problem worth splitting — regardless
   of whether it's short or long.

## Workflow

1. Check naming for specificity and domain-accuracy before anything else
   — it's the cheapest, highest-leverage quality lever.
2. Scan for dead code (unreachable, unused, stale commented-out blocks)
   and remove it.
3. Check for premature abstraction — a layer/interface/config option with
   no current concrete need — and simplify it back to what's actually
   used.
4. Check apparent duplication for whether it's genuinely the same logic
   before consolidating.
5. Check function/module boundaries against actual cohesion, not an
   arbitrary size target.
6. Apply language-idiomatic structure per the relevant Layer-4 technology
   skill.

## Engineering rules

- Names communicate the actual domain concept, not a generic placeholder.
- Dead code is removed, not left "just in case" without a stated reason.
- No abstraction is added for a hypothetical future need — build the
  concrete case first.
- Only consolidate duplication that's genuinely the same logic, never
  superficially similar but semantically distinct code.
- Function/module boundaries track actual cohesion, not an arbitrary
  line-count target.

## Trade-offs

Consolidating genuine duplication reduces maintenance surface at the cost
of an added layer of indirection to navigate — worth it only when the
logic really is the same and likely to change together. Splitting a large
function into smaller pieces can improve readability but can also
fragment a genuinely coherent single operation across multiple call sites
— judge by cohesion, not size alone.

## Anti-patterns

- **Generic, non-specific naming** (`data`, `process`, `handler`) that
  requires a comment to explain what it actually is.
- **Dead code left in place "just in case"** without a stated reason.
- **Premature abstraction** — an interface/config layer built for a
  hypothetical future need with no current concrete case.
- **Forcing superficially similar but semantically distinct code into one
  shared abstraction** — creates false coupling that makes future changes
  harder.
- **Splitting a genuinely coherent function purely to hit a line-count
  target**, fragmenting one operation across multiple call sites for no
  cohesion benefit.

## Security

Not a primary concern for this skill's scope; where a quality issue
overlaps a security concern (e.g. a dead code path that was actually a
disabled security check), flag it to
[security-engineering](../security-engineering/SKILL.md) rather than
silently removing it.

## Performance

Not a primary concern for this skill's scope; deep performance method is
owned by
[performance-engineering](../performance-engineering/SKILL.md). Code
quality and performance can trade off (a more "elegant" abstraction
sometimes costs runtime overhead) — when they conflict, state the
trade-off rather than assuming quality always wins.

## Testing

This skill's own correctness is verified by its evaluation criteria in
`skill.yaml` (fixture-based quality-improvement scenarios) rather than a
runtime test suite. Verifying that a quality-motivated change (e.g.
consolidating duplication) doesn't alter behavior is
[refactoring](../refactoring/SKILL.md)'s concern, not this skill's own.

## Failure handling

- If the code is an explicitly-accepted throwaway spike, don't impose
  production-quality standards uninvited.
- If a quality issue is genuinely a judgment call between two reasonable
  structures, state the trade-off rather than asserting one is
  objectively correct.

## Escalation

- A large-scale structural change beyond the immediate quality pass's
  scope is flagged for explicit scoping/confirmation rather than expanded
  into unilaterally.

## Outputs & verification

- **Outputs:** cleaner code, or quality findings (naming, structure, dead
  code, duplication, over-abstraction) with rationale.
- **Verify:** naming is meaningful; no unexplained dead code remains; no
  new premature abstraction is introduced; genuine duplication is
  consolidated, superficial similarity is not.

## References

- [core/taxonomy/skill-catalog.md](../../core/taxonomy/skill-catalog.md) — SK-CONV-003 taxonomy entry.
