---
name: Git workflow
description: >-
  Manage branching strategy, history hygiene, safe merges/rebases,
  worktrees, and pull-request mechanics. Guards risky operations
  (force-push, reset --hard, history rewrites) behind explicit
  confirmation. Use for branch creation, merge/rebase, PR management, or
  worktree isolation. Not for commit/branch text itself, which is
  git-conventions' scope.
spec_version: "1.0"
---

## Purpose & scope

Manage the *operations* of version control — branching model, merges,
rebases, worktrees, and pull-request mechanics — as distinct from the
*text* of commits and branches, which belongs to
[git-conventions](../git-conventions/SKILL.md). **A real research boundary
stated honestly**: this library has no dedicated official research document
for Git the CLI tool itself — the only researched Git-adjacent source is
GitHub's own documentation, which covers GitHub Flow, PR merge methods, and
repository rulesets in real depth, but not raw `git` plumbing mechanics
(reflog recovery, interactive-rebase internals, etc.) as an independently
cited source. Where this skill draws on general engineering discipline
rather than a cited research document, it says so rather than presenting
that judgment as researched fact.

## When to use / When not to use

**Use** for branch creation as part of a workflow decision, merges,
rebases, pull-request management, or worktree isolation. **Do not use**
for composing commit/branch text with no operational decision involved
(route to git-conventions), or when no version control system is present.

## Knowledge

**GitHub Flow is the one documented, named branching model this library's
research actually covers** [Source: docs.github.com/en/get-started/
using-github/github-flow]: create a branch → make isolated, complete
commits ("put the variable rename in one commit and the tests in another
commit") → open a pull request → address review via additional commits →
merge → delete the branch. It's described as "lightweight" and
applicable broadly, not tied to a specific team size or release cadence.
Other named branching models (Git Flow, trunk-based development) are not
independently researched in this library — don't present a comparison
between them as grounded fact; if a repo already uses one of them,
detect and follow it rather than assuming GitHub Flow is the default.

**Three merge methods are documented on GitHub, each with a real, distinct
history shape** [Source: docs.github.com/en/pull-requests/collaborating-
with-pull-requests/incorporating-changes-from-a-pull-request/
about-merge-methods-on-github]: **merge commit** (default — every
source-branch commit plus a new merge commit lands on the base branch, the
most complete but noisiest history), **squash and merge** (all PR commits
collapse into one commit on the base branch — cleaner, linear history, but
loses the individual-commit granularity), and **rebase and merge** (every
PR commit is individually replayed onto the base branch without a merge
commit — resembles a fast-forward, but rewrites commit metadata in the
process). Which method fits depends on whether the team values
individual-commit history (merge commit), a clean linear log (squash), or
both linearity and per-commit granularity (rebase) — there's no
universally-correct default; check what the repo already uses before
picking one.

**Rulesets govern what operations are even possible on a protected
branch** [Source: docs.github.com/en/repositories/configuring-branches-
and-merges-in-your-repository/managing-rulesets/about-rulesets]: a
"named list of rules that applies to a repository or to multiple
repositories," controlling push access, force-push permission, branch
deletion, signed-commit requirements, and (for push rulesets)
file-extension/path/size restrictions. Before proposing a force-push,
history rewrite, or branch deletion, check whether a ruleset would simply
reject it — that's a real, host-enforced constraint independent of this
skill's own confirmation-gating discipline.

**Worktrees enable genuinely parallel work on the same repository** —
isolating a task on a separate checkout without disturbing the primary
working tree's state, useful specifically when multiple lines of work need
to coexist without stashing/switching-branch overhead.

## Decision framework

1. **Does the repo already have a branching model (GitHub Flow, Git Flow,
   trunk-based) or merge-method preference?** If detectable from history,
   CONTRIBUTING docs, or repository settings, follow it rather than
   imposing a default.
2. **Is the operation destructive** (force-push, `reset --hard`, history
   rewrite, branch deletion with unmerged work)? If yes, it requires
   explicit confirmation for that specific instance — no exceptions, and a
   prior approval for one such action does not generalize to the next.
3. **Would a repository ruleset simply reject the operation anyway?**
   Check before proposing a force-push or destructive operation on a
   protected branch — this is a real constraint, not just this skill's own
   caution.
4. **Does the task need worktree isolation** (parallel work without
   disturbing the primary checkout)? If so, use a worktree rather than
   juggling stash/branch-switch overhead.
5. **Is PR automation actually available in this environment?** This
   library's own capability map found no uniform PR-automation primitive
   across agent hosts — verify rather than assume, and degrade to advisory
   guidance when it isn't available.

## Workflow

1. Check repo state (branch, working-tree status, remote-tracking) before
   any operation that could discard uncommitted work.
2. Detect the repo's branching model/merge-method preference if one exists;
   follow it.
3. For a new branch or commit involved in this operation, hand off to
   [git-conventions](../git-conventions/SKILL.md) for the actual text.
4. For any destructive operation, stop and get explicit confirmation for
   that specific instance before proceeding.
5. For PR management, open/update with a clear title/description and the
   correct base branch, when host PR automation is available; otherwise
   produce advisory guidance describing what should happen.
6. For parallel work, use a worktree rather than stashing/switching.

## Engineering rules

- Follow the repo's detected branching model/merge-method preference
  rather than imposing a default.
- Never execute a destructive operation (force-push, `reset --hard`,
  history rewrite, unmerged-branch deletion) without explicit confirmation
  for that specific action.
- Run `git status` (and check for anything worth stashing/committing)
  before any command that could discard uncommitted work.
- Hand off commit/branch text composition to git-conventions rather than
  inventing it inline.
- State plainly when PR automation isn't available in the current
  environment rather than assuming it is.

## Trade-offs

Merge-commit history is the most complete but noisiest; squash-and-merge
is the cleanest but loses individual-commit granularity; rebase-and-merge
gets both linearity and granularity at the cost of rewritten commit
metadata. Worktrees buy true parallelism at the cost of extra disk usage
and an additional checkout to keep track of, versus the simpler (but
serialized) stash/branch-switch approach.

## Anti-patterns

- **Imposing GitHub Flow (or any branching model) on a repo that already
  has its own convention** — detect first, always.
- **Treating a prior force-push/destructive-operation approval as
  standing authorization** for the next one — each instance needs its own
  explicit confirmation.
- **Proposing a force-push or history rewrite without checking whether a
  repository ruleset would reject it outright** — wasted effort and a
  misleading plan.
- **Assuming PR automation is available** without verifying — this
  library's capability map found no uniform primitive across agent hosts.
- **Composing commit/branch text inline** instead of handing off to
  git-conventions — duplicates that skill's responsibility and risks
  drifting from the repo's detected convention.

## Security

Rulesets can enforce signed-commit requirements and restrict force-push/
deletion at the host level — a real, host-enforced security control
independent of this skill's own confirmation-gating discipline. Destructive
operations (force-push, history rewrite) are a real risk surface for losing
work or overwriting a collaborator's changes; the confirmation-gating rule
above is this skill's primary control against that risk. Deep threat
modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Not a primary concern for this skill's scope.

## Testing

Not applicable in the conventional sense — this skill's own correctness is
verified by whether it correctly detects existing conventions and
correctly gates destructive operations (see `skill.yaml`'s evaluation
criteria), not by a runtime test suite.

## Failure handling

- If the repo's branching model isn't clear from history/config, ask
  rather than impose one.
- If PR automation or host capability isn't available in the current
  environment, degrade to advisory guidance (the operation described, not
  performed) rather than silently failing or claiming success.

## Escalation

- Force-push, `reset --hard`, and any other history-destroying operation
  require explicit per-action confirmation — a prior approval does not
  generalize to a later instance, per this library's standing safety
  discipline.
- PR automation capability varies across agent hosts; state the
  constraint explicitly rather than assuming it's available.

## Outputs & verification

- **Outputs:** the branch/merge/rebase/worktree/PR operation performed, or
  advisory guidance when execution isn't authorized or isn't possible.
- **Verify:** no destructive operation executed without explicit
  per-instance confirmation; a repo's own branching/merge-method
  convention was followed, not overridden.

## References

- [research/technologies/github.md](../../research/technologies/github.md) — GitHub Flow, PR merge methods, rulesets.
