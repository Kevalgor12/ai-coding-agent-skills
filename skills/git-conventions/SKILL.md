---
name: Git conventions
description: >-
  Produce professional Git branch names and commit messages. Detects an
  existing repository convention first (git log, commitlint config,
  CONTRIBUTING/CLAUDE.md guidance, existing branch-name patterns) and
  conforms to it; applies a sane default prefix set only when no
  convention is detected. Use whenever a commit or branch is about to be
  created. Never fabricates a ticket ID, scope, or attribution the repo
  doesn't already use.
spec_version: "1.0"
---

## Purpose & scope

Produce the *text and structure* of Git branch names and commit messages —
nothing about branching strategy, rebasing, merges, or PR mechanics, which
belong to [git-workflow](../git-workflow/SKILL.md). This is a mandated,
first-class skill in this library: every code-producing skill composes with
it rather than inventing its own commit/branch conventions.

## When to use / When not to use

**Use** whenever a commit or branch is about to be created, or the user
asks for a commit message or branch name. **Do not use** when there's no
version control in the workspace, when the user has explicitly dictated an
exact message/branch (use theirs verbatim, don't rewrite it), or for
pushing/merging/rebasing/PR concerns (route to git-workflow).

## Knowledge

**Detecting an existing convention always comes before applying a
default — this is the single rule that governs everything else in this
skill.** Inspect, in order: recent `git log` for an observable pattern; any
`commitlint`/`.commitlintrc`/Conventional-Commits configuration; `CONTRIBUTING`
or `CLAUDE.md` guidance; and existing branch-name patterns. If any of these
reveal a convention, conform to it — the repository's own convention always
wins over this skill's default, with no exception.

**Only when no convention is detectable does the default prefix set
apply**: `feat`, `feature`, `fix`, `bugfix`, `hotfix`, `refactor`, `chore`,
`docs`, `test`, `perf`, `ci`, `build`, `release`. Choose the prefix that
actually matches the change — a `docs`-only change gets `docs`, not `feat`;
a dependency bump gets `chore` or `build`, not `fix`.

**Commit-message structure**: a concise, imperative subject line
("Add X", not "Added X" or "Adds X"); a body only when it adds real
context beyond what the subject and diff already convey — never a
decorative or auto-generated body by default, and never a body that just
restates the diff. This mirrors GitHub Flow's own documented practice of
isolated, complete commits — "put the variable rename in one commit and the
tests in another commit" — where each commit's message should describe one
coherent change, not a batch of unrelated ones
[Source: docs.github.com/en/get-started/using-github/github-flow].

**Branch-name structure**: lowercase, hyphenated, prefixed to match the
change type, short and descriptive — `fix/null-check-on-login`, not
`Fix_NullCheck` or `my-branch-2`.

**Never fabricate.** No invented scope, no fabricated ticket ID, no
signature/attribution line the repository's own convention doesn't already
use. If the repository's commits don't carry a co-author line, don't add
one; if there's no ticket-tracker integration evident in the history,
don't invent a ticket reference to look more "complete."

## Decision framework

1. **Is there a detectable convention?** Check `git log`, commitlint
   config, CONTRIBUTING/CLAUDE.md, and existing branch names, in that
   order. If yes, conform to it exactly — stop here, the default set below
   doesn't apply.
2. **Did the user explicitly dictate exact text?** If yes, use it verbatim
   for that one message/branch — this doesn't override the detected
   convention for anything else, just this specific instance.
3. **No convention detected and no explicit dictation?** Apply the default
   prefix set, choosing the prefix that actually matches the change type.
4. **Is the change type ambiguous** (e.g. a refactor that also fixes a
   latent bug)? Ask which prefix fits rather than guessing — a wrong
   prefix is a real, visible mistake in the commit history.

## Workflow

1. Inspect recent `git log`, commitlint/Conventional-Commits config, and
   CONTRIBUTING/CLAUDE.md guidance for an existing convention.
2. If found, conform to it. If not, and the user hasn't dictated exact
   text, apply the default prefix set.
3. Write a concise, imperative subject line matching the actual change.
4. Add a body only if it carries real context the subject/diff don't
   already convey.
5. For a branch name, apply the same prefix logic: lowercase, hyphenated,
   short, descriptive.
6. Never add a ticket reference, scope, or signature/attribution the
   repository's own history doesn't already use.

## Engineering rules

- Detected convention always wins over this skill's default — no
  exceptions.
- Never fabricate a ticket ID, scope, or attribution line.
- Subject lines are imperative and concise; bodies are added only when
  they carry real information.
- Branch names are lowercase, hyphenated, and prefixed to match the change
  type.
- When the user explicitly dictates exact text, use it verbatim rather
  than "improving" it.

## Trade-offs

None material — this is a low-cost, high-value convention-compliance skill
with no meaningful trade-off between following the detected convention and
inventing a "better" one; the detected convention should always win because
consistency within a repository's history matters more than any individual
message being marginally more polished.

## Anti-patterns

- **Imposing a default convention on a repo that already has one** — the
  single most damaging mistake this skill can make, since it fragments the
  commit history's consistency.
- **Vague, non-descriptive messages** ("update stuff", "fix bug", "wip") —
  reject and repair these rather than accepting them.
- **Decorative or auto-generated bodies by default** — a body should carry
  real information, not pad the message.
- **Fabricating a ticket reference or attribution line** the repo's own
  history doesn't already use — this misrepresents the change's actual
  provenance.
- **Rewriting text the user explicitly dictated** — if they gave an exact
  message, use it, don't "improve" it uninvited.

## Security

Not a primary concern for this skill's scope — it produces text, not code
or configuration with a security surface. Secrets should never appear in a
commit message or branch name; if a proposed message would reference
sensitive data, flag it rather than including it.

## Performance

Not applicable to this skill's scope.

## Testing

This skill's own "correctness" is verified by the evaluation criteria in
`skill.yaml` (convention detection and conformance across several scenario
types) rather than a runtime test suite — there's no application code to
test here.

## Failure handling

- If a detected convention and a stated user instruction conflict for one
  specific message/branch, the explicit user instruction wins for that
  instance — but the detected convention still applies elsewhere.
- If no convention is detectable and the change type is genuinely
  ambiguous, ask rather than guess.

## Escalation

- Force-push, history rewrites, or any destructive git operation are
  entirely out of this skill's scope — it produces text only, never
  executes destructive operations. Route to
  [git-workflow](../git-workflow/SKILL.md), which itself guards such
  operations behind explicit confirmation.

## Outputs & verification

- **Outputs:** a proposed (or, when authorized, actually created) branch
  name and/or commit message.
- **Verify:** a detected convention was conformed to rather than
  overridden; no fabricated ticket/scope/attribution; subject is concise
  and imperative.

## References

- [research/technologies/github.md](../../research/technologies/github.md) — GitHub Flow's isolated-commit practice.
