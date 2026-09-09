# Planning heuristics (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here.

## Sequencing heuristics

- **De-risk early.** If step A's failure or a surprising result would change
  or invalidate later steps, do A first — even if it feels like a smaller or
  less "important" piece of the work.
- **Isolate risk, don't let it block.** If a step is risky but its outcome
  doesn't affect other steps' design, it can run in parallel with or after
  unrelated work rather than gating the whole plan.
- **Prefer the reversible step first when dependency order is otherwise a tie.**
  Between two independently-orderable steps, doing the cheaper-to-undo one
  first leaves more room to change course.
- **Group by shared verification, not just by theme.** Steps that can be
  verified together (e.g., by the same test run) are often worth sequencing
  adjacently even if not strictly dependent, to reduce context-switching cost.

## Identifying true dependencies (a quick test)

Ask: "if I did step B before step A, would B have to be redone once A is
done?" If yes, A is a real prerequisite of B. If B would simply have to
*wait* for something A produces but wouldn't need rework, that's often still
a dependency (data/artifact dependency). If neither applies, the steps are
independent — a candidate for parallel execution or free reordering.

## Risk-flagging calibration

Flag a step when at least one of these holds, not by gut feel alone:

- It touches something not yet verified to exist/behave as assumed (an
  external API's real behavior, an undocumented edge case).
- It requires a decision that wasn't actually settled in the approach (a gap
  surfaced during planning, not before).
- It's the team/agent's first time doing this specific thing in this codebase.
- Its failure would require redoing more than itself.

Don't flag a step just because it's the *biggest* one — size and risk are
different axes; a big, well-understood step is lower risk than a small,
novel one.

## When a plan is "too much plan"

Signs the planning has gone past proportional:

- The plan has more structure (phases, sub-phases, formal risk registers)
  than the underlying task has real complexity.
- Steps are being planned at a granularity finer than anyone will actually
  check off individually.
- The time spent planning is starting to rival the time the work itself would take.

When any of these show up, collapse back to a shorter list and get moving —
per the parent skill's proportionality principle.
