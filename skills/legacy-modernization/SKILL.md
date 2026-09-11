---
name: Legacy modernization
description: >-
  Safely evolve legacy code toward current practice and supported
  versions — assess current vs. target state, plan incremental steps with
  rollback points, and apply breaking-change migrations using researched
  version data. Use when upgrading a major version, modernizing outdated
  patterns, or migrating off a deprecated approach. Avoids big-bang
  rewrites unless justified. Not for greenfield code or a routine
  no-breaking-changes minor bump.
spec_version: "1.0"
---

## Purpose & scope

Safely evolve legacy code toward current, supported versions and
practice — assess the gap, plan incrementally with rollback points, and
apply migrations grounded in this library's version-matrix and per-
technology breaking-change research. This skill has hard dependencies on
[refactoring](../refactoring/SKILL.md) (each incremental modernization
step is itself a behavior-preserving transformation, verified the same
way) and [testing-strategy](../testing-strategy/SKILL.md) (verification
underlies every staged step).

## When to use / When not to use

**Use** when upgrading a major version, modernizing outdated patterns, or
migrating off a deprecated approach. **Do not use** for greenfield code
with no legacy state to assess, or a routine minor-version bump with no
breaking changes.

## Knowledge

**"Assess current vs. target state" is genuinely archaeological work, and
this library's technology skills already document real, concrete examples
of what that assessment needs to surface.** A major-version upgrade isn't
a single fact to check — it's a set of independently-documented breaking
changes, each with its own precise version range. React's RSC CVEs
affected specific, narrow version windows (19.0-19.2.0 for the initial
CVE, with a follow-up patch that was itself incomplete for a second,
overlapping range) — assessing "am I affected" requires checking the
exact version in use against the exact affected range, not just "am I on
React 19." Next.js's May 2026 coordinated release affected **all** of
versions 13-14 with **no direct patch**, forcing an upgrade path rather
than a simple point release. Angular's per-major TypeScript/Node floor
coupling means an Angular major upgrade can be blocked by a TypeScript
version that also needs upgrading first — the dependency chain itself is
part of the assessment, not just the target technology's own version
[Source via version-matrix.md]. **The assessment step is where migration
plans succeed or fail** — skipping it in favor of jumping straight to
"upgrade and see what breaks" is exactly the big-bang-rewrite risk this
skill exists to avoid.

**Some "legacy" states are not just outdated but fully unsupported, and
that changes the modernization urgency, not just its scope.** Vue 2
reached full EOL (2023-12-31) — no new features, fixes, or security
patches from the core team at all. An app still on Vue 2 isn't behind on
convenience features; it's running on a completely unmaintained major
version with no security-patch path. This is a different, more urgent
category of "legacy" than a supported-but-old minor version, and the
modernization plan should reflect that urgency difference explicitly.

**Rollback points are what make incremental migration actually safer than
a big-bang rewrite, not just slower.** A staged migration with no
verified rollback point at each stage has the same all-or-nothing risk
profile as a rewrite, just spread out over more time — the safety benefit
of "incremental" comes specifically from being able to stop and revert at
any verified checkpoint, not from the mere fact of taking smaller steps.

## Decision framework

1. **What's the actual gap between current and target state**, including
   the full dependency chain (a target technology's own breaking changes,
   plus any coupled dependency version floors it requires)? Assess this
   fully before planning steps.
2. **Is the current state merely outdated, or fully unsupported/EOL** (no
   security patches at all)? The latter changes the urgency of the plan,
   not just its scope.
3. **Does this library's research actually cover the target technology's
   breaking-change data?** If not, state that gap rather than inventing
   migration guidance for an ungrounded technology.
4. **Can this be staged incrementally with verified rollback points at
   each stage**, or is a big-bang rewrite actually justified? Default to
   incremental; require explicit justification for a rewrite.
5. **Is each staged step itself behavior-preserving**, verified the same
   way a refactor would be? Apply refactoring's verification discipline to
   every step, not just the final result.

## Workflow

1. Assess current vs. target state fully, including the dependency chain,
   using this library's version-matrix and per-technology breaking-change
   data where the technology is covered.
2. Determine urgency (outdated-but-supported vs. fully unsupported/EOL).
3. Plan incremental stages, each with a verified rollback point.
4. Apply each stage using refactoring's behavior-preservation discipline,
   verified via testing-strategy.
5. State explicitly any breaking-change data this library's research
   doesn't cover for the target technology.
6. Present the staged plan with rollback points for confirmation before
   execution begins on anything production-impacting.

## Engineering rules

- Assess the full dependency chain, not just the target technology's own
  version, before planning.
- Distinguish outdated-but-supported from fully unsupported/EOL —
  urgency differs.
- Default to incremental, staged migration with rollback points; require
  explicit justification for a big-bang rewrite.
- Verify each staged step's behavior-preservation the same way a refactor
  would be verified.
- State plainly when this library's research doesn't cover the target
  technology's breaking changes.

## Trade-offs

Incremental migration with rollback points takes longer in wall-clock time
than a big-bang rewrite but keeps the system in a working, revertible
state throughout — a real safety benefit for anything with production
impact. A big-bang rewrite can be faster when genuinely justified (e.g.
the incremental path is architecturally impossible), but loses the
ability to stop and revert partway through.

## Anti-patterns

- **Jumping straight to "upgrade and see what breaks"** instead of
  assessing the documented breaking-change gap first.
- **Treating an EOL/fully-unsupported legacy state with the same urgency
  as a merely-outdated one.**
- **Proposing a big-bang rewrite without explicit justification** — the
  default is incremental with rollback points.
- **Staging a migration into smaller steps with no actual rollback point
  at each stage** — this has the same all-or-nothing risk as a rewrite,
  just spread out.
- **Inventing migration guidance for a technology this library's research
  doesn't cover** instead of stating the gap.

## Security

An EOL/fully-unsupported legacy dependency carries an unpatched-
vulnerability risk that compounds over time — flag this explicitly as a
security-relevant urgency factor, deferring deep threat assessment to
[security-engineering](../security-engineering/SKILL.md).

## Performance

Not a primary concern for this skill's scope beyond noting when a
modernization target also carries a documented performance improvement
(a version upgrade that happens to also improve performance); deep
performance method is owned by
[performance-engineering](../performance-engineering/SKILL.md).

## Testing

Every staged modernization step is verified via
[testing-strategy](../testing-strategy/SKILL.md)'s method, the same way a
refactor's behavior-preservation is verified — this skill does not invent
a separate verification approach.

## Failure handling

- If the target technology's breaking-change data isn't covered by this
  library's research, state that gap rather than inventing migration
  guidance.
- If a big-bang rewrite is proposed, require explicit justification
  before proceeding.

## Escalation

- A major-version upgrade or migration with production impact is
  presented with the staged plan and rollback points for explicit
  confirmation before execution begins.
- A proposed big-bang rewrite requires explicit justification and
  confirmation, given it's a harder-to-reverse choice than staged
  migration.

## Outputs & verification

- **Outputs:** a staged modernization plan (addressing documented
  breaking changes, sequenced with verification/rollback points), and/or
  applied incremental changes.
- **Verify:** every documented breaking change is addressed; each stage
  has a rollback point; each step's behavior-preservation is verified,
  not assumed.

## References

- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md)
