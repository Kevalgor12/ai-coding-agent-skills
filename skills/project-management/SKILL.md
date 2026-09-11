---
name: Project management
description: >-
  Frame work as issues/milestones, summarize status, and draft changelog or
  release-note entries for a longer-running effort. Use when an effort spans
  more than a single change and needs tracking, or when release notes are
  requested. Not for a one-off change, not for commit/branch text
  (git-conventions), and not for git operations (git-workflow).
spec_version: "1.0"
---

## Purpose & scope

Keep a longer effort's status legible: frame work as issues/milestones,
summarize where things stand, and draft changelog/release-note entries that
match what actually happened. This skill is deliberately scoped narrow — the
library's research grounds GitHub issue tracking specifically, not a general
project-management methodology, so this skill doesn't invent process beyond
what's actually supported. It is not commit/branch text
([git-conventions](../../core/taxonomy/skill-catalog.md)), not git
operations or PR mechanics
([git-workflow](../../core/taxonomy/skill-catalog.md)), and not the task plan
itself ([technical-planning](../technical-planning/SKILL.md)).

## When to use / When not to use

**Use** when an effort spans more than one session and benefits from tracked
status, or when the user asks for issue/milestone framing, a status summary,
or release notes/a changelog entry for something that just shipped. **Do not
use** for a one-off change with nothing to track over time, when no tracker
or changelog convention exists and none was requested (don't invent process
the project doesn't have), or for commit/branch text or git operations —
route those to their owning skills.

## Knowledge

**Tracking has a real cost.** Every issue filed, every status update
written, is something someone has to read and something that can go stale.
The senior-engineer judgment here isn't "track everything for visibility" —
it's tracking what's actually worth the overhead and skipping the rest. A
single-session bug fix doesn't need a milestone; a multi-week effort with
several contributors probably does.

**A changelog entry describes what happened, not what was intended.**
Drafting it from the actual diff/change (not from the original plan) avoids
the common failure of a changelog that describes a feature more grandly or
differently than what actually shipped.

**An issue is written for someone without your context.** If it only makes
sense to someone who was in the current conversation, it isn't done — a good
issue draft states the goal, the relevant constraints, and enough context to
pick the work up cold.

Templates for issues, status summaries, and changelog entries are in
[references/pm-templates.md](references/pm-templates.md).

## Decision framework

1. **Is this worth tracking at all?** A change contained to one session with
   no future reference need doesn't need an issue. Effort spanning sessions,
   multiple contributors, or with a real "is this done yet" question benefits
   from tracking. Default to *not* tracking; track when the overhead earns its keep.
2. **Issue, milestone, or just a status note?** A single trackable unit of
   work → an issue. A group of related issues with a shared goal → a
   milestone. A quick "where are we" ask → a status summary, no artifact needed.
3. **Can this actually be filed, or only drafted?** Check tracker/git access
   before promising a filed issue; if unavailable, produce the draft and say
   so plainly (see Failure handling) rather than claiming an action that didn't happen.

## Workflow

1. Determine whether the work is actually worth tracking (§Decision framework); if not, say so and stop.
2. For a new issue: state the goal, constraints, and enough context for someone else to pick it up.
3. For a status summary: state what's done, what's in progress, and what's
   blocked — concisely, not a narrative retelling.
4. For a changelog entry: draft it from the actual change, matching its real
   scope and user-facing effect, not the original ambition for it.
5. If a tracker is accessible and the user has confirmed posting, file it;
   otherwise present the draft as advisory text.

## Engineering rules

- Don't manufacture tracking overhead for work that doesn't need it.
- Write issues for a reader with no access to the current conversation.
- Draft changelog entries from what shipped, not from what was planned.
- Never claim something was filed/posted when it wasn't — say clearly when output is a draft, not a completed action.

## Trade-offs

More tracking gives better visibility into a longer effort's status but costs
maintenance (stale issues, status updates nobody reads). Less tracking is
cheaper but risks losing context on why decisions were made once a session ends.
Calibrate to the effort's actual length and number of participants.

## Anti-patterns

- **Tracking everything** — filing an issue for a five-minute fix. This is
  the domain's overengineering trap: process that costs more than the work it tracks.
- **Changelog entries that oversell the change** — describing a small fix as
  a feature, or omitting a user-facing behavior change because it wasn't the
  "main point" of the work.
- **Issues only the author could act on** — missing the context a fresh reader would need.
- **Claiming a filing that didn't happen** because tracker access wasn't actually available.

## Failure handling

- If no tracker/GitHub write access is available, produce the drafted
  issue/milestone/changelog text as advisory output, clearly labeled as not
  yet filed, rather than claiming it was filed (Tier-A fallback behavior).
- If the work is too small to be worth tracking, say so rather than
  manufacturing an issue for it.

## Escalation

- Posting to an external tracker or PR is outward-facing and requires
  explicit user confirmation before it happens; absent that, the drafted text
  is handed to the user to post themselves.

## Outputs & verification

- **Outputs:** an issue/milestone draft, a status summary, and/or a changelog/
  release-note entry.
- **Verify:** the changelog entry matches the actual change, not an idealized
  version of it; an issue draft is actionable by someone without the current
  conversation's context.

## References

- [references/pm-templates.md](references/pm-templates.md) — Tier-2 issue/status/changelog templates.
