---
name: Husky
description: >-
  Husky-specific Git hooks mechanics: the core.hooksPath install
  mechanism, per-package-manager install wiring (prepare for npm/pnpm/
  Bun vs. Yarn's postinstall), and Husky's scope as a hook trigger, not a
  staged-file filter (pair with lint-staged for that). Use when a repo
  has or needs a .husky/ directory, a husky devDependency, or a
  prepare/postinstall script invoking husky, or when hooks aren't firing.
  Not for CI/CD pipeline design or commit-message/branch-name text
  conventions themselves.
spec_version: "1.0"
---

## Purpose & scope

Install, configure, and troubleshoot Git hooks with Husky — the
`core.hooksPath` mechanism, per-package-manager install wiring, and
Husky's deliberate scope as a hook *trigger*. Pipeline design belongs to
[ci-cd-pipeline](../ci-cd-pipeline/SKILL.md); commit-message/branch-name
*text* conventions belong to [git-conventions](../git-conventions/SKILL.md)
— Husky is the mechanism that fires a `commit-msg` hook (e.g. invoking
`commitlint`) to enforce whatever text convention is already in place, it
does not define that convention itself.

## When to use / When not to use

**Use** when a repo has or needs a `.husky/` directory, a `husky`
devDependency, a `prepare`/`postinstall` script invoking `husky`, or when
hooks aren't firing and the cause may be install/config-level. **Do not
use** for CI/CD pipeline design itself (route to ci-cd-pipeline), for
commit-message/branch-name text content (route to git-conventions), for a
non-Husky hooks manager with no Husky present (no researched grounding for
alternatives in this library), or for staged-file-specific filtering logic
(that's lint-staged's scope).

## Knowledge

**The entire mechanism is one `git config` call.** Husky's install routine
runs `git config core.hooksPath <dir>/_`, repointing Git's native hook
lookup at Husky's internal hooks folder [Source:
https://raw.githubusercontent.com/typicode/husky/main/index.js]. There is
no wrapper daemon or custom hook engine — Git itself invokes the hook
files natively; Husky just tells Git where to look.

**Git floor: > 2.9, precisely because that's what `core.hooksPath` needs.**
Git 2.9 introduced `core.hooksPath`; without it, Husky's entire mechanism
has nothing to hook into and simply cannot function. The official
troubleshooting guide lists confirming Git is above 2.9 as a checklist item
for "hooks not running" [Source:
https://typicode.github.io/husky/troubleshoot.html].

**Installing Husky needs Node >=18; a hook *running* does not need Node at
all**, unless the hook script itself invokes `node`/`npm`/`npx`. The
published `package.json` declares `engines.node: ">=18"` for the `husky`
CLI/install routine [Source:
https://raw.githubusercontent.com/typicode/husky/main/package.json]. But
at execution time, Git invokes a thin POSIX `sh` dispatcher that sources
the user's hook file directly with `sh -e` — no Node process is started
unless that hook file's own commands call into Node tooling [Source:
https://raw.githubusercontent.com/typicode/husky/main/husky].

**Install wiring differs by package manager.** npm, pnpm, and Bun wire
Husky through the standard `prepare` lifecycle script (`"prepare": "husky"`).
Yarn does not support `prepare`, so Yarn projects use `"postinstall": "husky"`
instead; a package that itself uses Husky and is *published* to npm should
additionally pair Yarn's `postinstall` with `prepack`/`postpack` scripts
toggling `pinst`, so consumers installing the published package don't
inherit the maintainer's own hook install [Source:
https://typicode.github.io/husky/get-started.html;
https://typicode.github.io/husky/how-to.html].

**Husky is a trigger, not a staged-file filter.** Husky's own docs describe
their staged-file `pre-commit` example (running `prettier` over
`git diff --cached --name-only`) as "a basic but working example," and
explicitly say "check lint-staged if you need more" [Source:
https://typicode.github.io/husky/get-started.html]. Husky fires the hook;
selective staged-file filtering is deliberately left to lint-staged.

**Commit-msg integration with commitlint is a one-line file.** The
documented v9 pattern is a `.husky/commit-msg` file containing
`commitlint --edit $1`, using Git's native positional hook argument
(`$1` = the commit-message file path) — this replaces the old v4-era
`HUSKY_GIT_PARAMS` mechanism entirely [Source:
https://typicode.github.io/husky/migrate-from-v4.html]. This is the
concrete mechanism that connects Husky to whatever commit-message
convention [git-conventions](../git-conventions/SKILL.md) determines
should apply — Husky doesn't decide the convention, it just runs the
linter that enforces it.

**v10.0.0 will remove the v4-legacy compatibility shim (announced,
unreleased as of research date 2026-09-09).** Today, Husky auto-strips two
legacy lines it finds in an old hook file — the shebang `#!/usr/bin/env sh`
and the sourcing line `. "$(dirname -- "$0")/_/husky.sh"` — printing a
deprecation warning that these lines "WILL FAIL in v10.0.0" [Source:
https://raw.githubusercontent.com/typicode/husky/main/index.js]. Anyone
with hook files still carrying those two lines from a v4-era migration
needs to actually remove them before v10.0.0 ships, not rely on the shim
indefinitely.

**CI should skip hook installation, not just tolerate it.** The documented
pattern is `HUSKY=0` as a workflow environment variable (e.g. GitHub
Actions `env: HUSKY: 0`), checked in both the install routine and the
dispatcher [Source: https://typicode.github.io/husky/how-to.html].
Installing hooks in CI is pointless — no interactive `git commit`/`git push`
happens there for the hooks to guard.

**`~/.config/husky/init.sh` fixes the "works in terminal, fails from GUI
client" symptom.** GUI Git clients often launch hooks without sourcing a
shell profile, so a `nvm`/`fnm`/`asdf`/`volta` shim never makes it onto
`PATH`. Husky sources `${XDG_CONFIG_HOME:-$HOME/.config}/husky/init.sh`
(a machine-local, not repo-committed file) before running any hook,
specifically so a version manager's shell-init code can be replicated
there [Source: https://typicode.github.io/husky/how-to.html].

## Decision framework

1. **Husky alone, or Husky + lint-staged?** If the need is "run the full
   lint/test suite on every commit," Husky alone is sufficient — add the
   command as a `.husky/pre-commit` line. If the need is "lint/format only
   the staged files," don't hand-roll the `git diff --cached` filtering
   Husky's own docs call "basic" — pair with lint-staged, exactly as Husky's
   docs direct.
2. **Do existing hook files need v4-cleanup now?** If any `.husky/*` file
   still contains the legacy shebang + sourcing lines, migrate them before
   v10.0.0 ships — don't lean on the compatibility shim as if it's
   permanent; it's explicitly scheduled for removal.
3. **`prepare` or `postinstall`?** Determined by package manager, not
   preference: npm/pnpm/Bun → `prepare`; Yarn → `postinstall` (plus
   `pinst` if the package is itself published). Get this wrong and hooks
   silently never install for that package manager's users.
4. **Simplest first:** if the repo has no hooks at all and just needs "run
   tests before commit," `husky init` plus a one-line `.husky/pre-commit`
   is the whole solution — don't reach for a heavier hooks framework the
   task doesn't need.

## Workflow

1. Confirm the package manager in use (npm, pnpm, Yarn, or Bun) — this
   decides `prepare` vs. `postinstall` wiring.
2. Run `husky init` (or wire `prepare`/`postinstall` manually) so
   `git config core.hooksPath` gets set on install.
3. Add or edit the specific `.husky/<hook-name>` file, using the exact Git
   hook name (`pre-commit`, `commit-msg`, `pre-push`, etc.) — not a
   fuzzy variant.
4. For staged-file-specific behavior, delegate to lint-staged rather than
   hand-rolling the filter in the hook file.
5. For commit-message enforcement, write `.husky/commit-msg` containing
   `commitlint --edit $1`.
6. If this hook set shouldn't install on CI, ensure the CI workflow sets
   `HUSKY=0`.
7. If any hook file still carries v4-era shebang/sourcing lines, remove
   them now rather than deferring to the shim.
8. Verify per the checks below before declaring done.

## Engineering rules

- Hook file names must exactly match a valid Git hook name — no
  `precommit`, no `pre-commit.sh`.
- Use `prepare` for npm/pnpm/Bun; use `postinstall` (+ `pinst` if
  published) for Yarn — never assume `prepare` works universally.
- Don't reimplement staged-file filtering inside a raw Husky hook; pair
  with lint-staged once the need goes past "run this on every commit."
- Keep hook scripts POSIX `sh` compliant (not bash-specific) unless the
  whole team is confirmed to have `bash`, since the dispatcher invokes
  hooks with `sh -e`.
- Set `HUSKY=0` in CI workflows that don't need hook installation.

## Trade-offs

Husky alone (no lint-staged) is simpler to set up and has one fewer
dependency, but its own docs frame that as adequate only for coarse,
whole-repo checks — anything needing staged-file precision pays for that
simplicity with either false-positives (linting unstaged files) or a
hand-rolled `git diff --cached` filter reinventing what lint-staged already
does. Wiring `prepare` for a package that's itself published to npm without
guarding it (`husky || true` or a `NODE_ENV`/`CI`-checking install script)
trades a small amount of setup friction for consumers not seeing a broken
`prepare` step when `husky` isn't in their `node_modules` (production/
`--omit=dev` installs).

## Anti-patterns

- **Relying on Husky alone for staged-file-specific linting** instead of
  pairing with lint-staged — Husky's own docs call the raw approach
  "basic" and explicitly point elsewhere for anything more.
- **Leaving legacy v4-era hook files unmigrated** (shebang + sourcing
  lines) and assuming the compatibility shim will always strip them — it
  is explicitly scheduled for removal in v10.0.0.
- **Installing hooks in CI without `HUSKY=0`** — wastes setup time on
  hooks that guard interactive operations CI never performs.
- **Wiring `prepare` for a Yarn project** (or `postinstall` for npm/pnpm/
  Bun) without checking which lifecycle script the package manager
  actually supports — the hooks silently never install for the mismatched
  manager.
- **Publishing a package that uses Husky without guarding the install
  install/publish scripts** (`pinst`, `prepack`/`postpack`) — consumers
  inherit a maintainer-only dev tool as a broken or unwanted install step.

## Security

Husky's install routine explicitly refuses to target a parent directory
(any path containing `..`), stated as a deliberate security measure
[Source: https://typicode.github.io/husky/how-to.html;
https://raw.githubusercontent.com/typicode/husky/main/index.js]. Beyond
that, the official docs have no dedicated security page. One real,
research-flagged (not officially documented) consideration: the dispatcher
prepends `node_modules/.bin` to `PATH` before running a hook [Source:
https://raw.githubusercontent.com/typicode/husky/main/husky], so a hook
script runs with the ambient trust of whatever is in the working tree's
`node_modules` — a supply-chain-compromised devDependency could execute
code at commit/push time. This is a reasonable inference from documented
PATH behavior, not an officially stated warning. Also note hooks are
always locally bypassable (`git commit -n` / `HUSKY=0`) — Husky is a
developer-experience convenience, not an enforcement boundary; genuine
enforcement still needs server-side checks (CI, branch protection), which
is [ci-cd-pipeline](../ci-cd-pipeline/SKILL.md)'s concern, not Husky's.

## Performance

Husky itself adds negligible footprint: the package is "2 kB (gzipped)"
with no runtime dependencies, and install/dispatch overhead is documented
as "~1ms," attributed to using native `core.hooksPath` rather than a
heavier wrapper [Source: https://typicode.github.io/husky/]. Concretely:
a hook's actual execution time is whatever the hook's own commands take —
Husky's dispatcher itself has no Node runtime presence at execution time
unless the hook script invokes `node`/`npm`/`npx`, so a pure-shell hook
(e.g. a single `prettier` or `eslint` invocation) pays no extra Node
startup cost beyond what that tool itself requires.

## Testing

Husky ships no dedicated testing framework or mocking utility for hook
scripts, and the official docs treat hooks as ordinary shell scripts:
the only documented technique is to temporarily append `exit 1` to the
end of a hook file, run the corresponding Git command, observe the
output, confirm the operation was aborted, then remove the `exit 1` line
[Source: https://typicode.github.io/husky/how-to.html]. There is no
official guidance on unit-testing hook logic in isolation or asserting
hook behavior inside a CI pipeline — state this plainly rather than
implying a testing story that doesn't exist.

## Failure handling

- If the installed Git version can't be confirmed as >2.9, state that
  Husky's mechanism requires it and verify rather than assuming it's met.
- If shell access is unavailable, degrade to advisory: propose the
  `.husky/<hook>` file contents and the `package.json` script change as
  edits, and say plainly that install (the actual `git config
  core.hooksPath` mutation) was not run.
- If the package manager can't be determined, ask rather than guessing
  `prepare` vs. `postinstall` wiring.

## Escalation

- If hooks need to be a genuine enforcement boundary (not just local
  developer convenience), say so explicitly and hand off to
  [ci-cd-pipeline](../ci-cd-pipeline/SKILL.md) for the server-side gate —
  Husky hooks are always locally bypassable and the docs don't claim
  otherwise.

## Outputs & verification

- **Outputs:** `.husky/<hook-name>` file(s) and the `package.json` install
  script (`prepare` or `postinstall`) wiring them up.
- **Verify:** the hook file name exactly matches a Git hook name; `git
  config core.hooksPath` resolves to Husky's directory after install; the
  install script matches the package manager in use; CI workflows that
  shouldn't install hooks set `HUSKY=0`; no legacy v4-era shebang/sourcing
  lines remain unmigrated.

## References

- [research/technologies/husky.md](../../research/technologies/husky.md) — primary research source, cited throughout.
- [ci-cd-pipeline](../ci-cd-pipeline/SKILL.md) — parent; server-side pipeline gating that complements Husky's local hooks.
- [git-conventions](../git-conventions/SKILL.md) — parent; the commit-message/branch-name text convention that a Husky `commit-msg` hook enforces.
