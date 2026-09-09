# Husky — Technology Research

Research date: 2026-09-09. Primary sources: `typicode.github.io/husky/*` (canonical docs host — confirmed current; the site is generated from `github.com/typicode/husky/tree/main/docs`, fetched here in raw Markdown form for citation precision), `github.com/typicode/husky` (official GitHub org repo — source code, releases, commit history), `blog.typicode.com` (official maintainer blog, cited for architecture/design rationale). Citation convention: `[Source: <url>]` for documented facts, `[Inference, not confirmed in docs]` for reasoning not explicitly stated, `Unresolved: ...` for genuine ambiguity across official sources, "Not documented / could not verify" where no authoritative official answer was found.

## IMPORTANT — version/maintenance status, read before the rest of this file

[Source: https://raw.githubusercontent.com/typicode/husky/main/package.json ; https://api.github.com/repos/typicode/husky/releases] The current stable published version is **v9.1.7**, released 2024-11-18. As of the research date (2026-09-09, ~22 months later), no newer npm release exists — the GitHub Releases API's most recent entry is still `v9.1.7`.

[Source: https://api.github.com/repos/typicode/husky (commit history)] The repository itself is not abandoned — commits continued into 2026 (most recent inspected: 2026-03-19), but recent commits are documentation/sponsor-page changes and a CI workflow update ("ci: remove Node.js 18, add 24 to Node.js CI workflow", 2025-10-10), not a new npm publish. **Unresolved: whether a v10.0.0 release is imminent.** The v9.x docs and deprecation warnings (see Section 13) explicitly reference "v10.0.0" as the version in which certain deprecated behaviors "WILL FAIL," but no v10 tag, branch-specific docs, or changelog entry was found as of this research date — treat v10 as announced-but-unreleased.

[Source: https://raw.githubusercontent.com/typicode/husky/main/package.json] Package metadata for the current stable release: `"type": "module"`, `"license": "MIT"`, `"engines": { "node": ">=18" }`, zero runtime dependencies, single bin entry `husky -> bin.js`.

---

## 1. Core concepts

[Source: https://typicode.github.io/husky/] Husky is described by its own docs as an "Ultra-fast modern native git hooks" tool that "enhances your commits and more 🐶" — it automatically lints commit messages, lints/formats code, and runs tests at Git lifecycle points (commit, push, etc.).

[Source: https://typicode.github.io/husky/] Stated feature set: "Just `2 kB` (gzipped) with no dependencies," runs in "~1ms," and works by using the native Git feature `core.hooksPath` rather than any custom wrapper mechanism.

[Source: https://typicode.github.io/husky/] Husky supports "[All 13 client-side Git hooks](https://git-scm.com/docs/githooks)." [Source: https://raw.githubusercontent.com/typicode/husky/main/index.js] The exact list of 13 hooks Husky's `init`/install routine wires up (read directly from the `index.js` source array) is: `pre-commit`, `pre-merge-commit`, `prepare-commit-msg`, `commit-msg`, `post-commit`, `applypatch-msg`, `pre-applypatch`, `post-applypatch`, `pre-rebase`, `post-rewrite`, `post-checkout`, `post-merge`, `pre-push`, `pre-auto-gc`.

[Source: https://typicode.github.io/husky/] Core design philosophy, quoting the docs' feature list: hooks "Adhere[] to Git's native hook organization," "Align[] with npm best practices using the `prepare` script," support "opt-in/opt-out options," "Can be globally disabled," and give "user-friendly error messages."

[Source: https://typicode.github.io/husky/get-started.html] The fundamental unit of configuration is a **file**, not a config-language entry: "Adding a hook is as simple as creating a file" — e.g., `echo "npm test" > .husky/pre-commit"`.

[Source: https://blog.typicode.com/posts/husky-git-hooks-javascript-config/] Historical/architectural rationale (from the official maintainer blog): pre-v6 Husky (`v0.x`–`v4.x`) generated Git hooks from a JavaScript config file (`.huskyrc.js`/`package.json` `"hooks"` key). This created a two-sources-of-truth problem — "Generating Git hooks from a JS config can get out of sync" — because `.git/hooks/` had to be kept in sync with the JS config independently. The blog credits Git 2.9's introduction of `core.hooksPath` (2016) as the enabling feature for the redesign, summarized by the author as: "Like holding a hammer with a plier 🛠️ to drive a nail… you only need the hammer 🔨" — i.e., use Git's own hook-directory mechanism directly instead of wrapping it in JS config.

## 2. Architecture

[Source: https://raw.githubusercontent.com/typicode/husky/main/index.js] Mechanically, Husky's install routine (invoked as `husky` or `husky <dir>`, default dir `.husky`) does the following, read directly from source: (1) if `HUSKY=0` env var is set, skip install; (2) refuse if the target directory string contains `..` (stated purpose: prevent installing into a parent directory for security reasons — see Section 7); (3) refuse if no `.git` directory is found; (4) run `git config core.hooksPath <dir>/_` to point Git at Husky's internal hooks folder; (5) create `<dir>/_/.gitignore` containing `*` (so the internal `_` folder isn't committed); (6) copy an internal dispatcher script (`husky`, the package's shell script) into `<dir>/_/h`; (7) write a thin shim file for each of the 13 supported hook names, each shim just sourcing the shared dispatcher (`. "$(dirname "$0")/h"`).

[Source: https://raw.githubusercontent.com/typicode/husky/main/husky] The shared dispatcher script (POSIX `sh`), read directly from source, does the following at hook execution time: (a) if `HUSKY=2`, enables shell trace mode (`set -x`) for debugging; (b) computes the actual user-facing hook file (e.g., `.husky/pre-commit`) from the invoked hook name; (c) exits silently (code 0) if that user hook file doesn't exist; (d) warns if the deprecated `~/.huskyrc` exists, telling the user to move code to `~/.config/husky/init.sh`; (e) sources the startup file at `${XDG_CONFIG_HOME:-$HOME/.config}/husky/init.sh` if present; (f) exits silently if `HUSKY=0`; (g) prepends `node_modules/.bin` to `PATH`; (h) executes the user's hook file with `sh -e`, passing through Git's original arguments (`"$@"`); (i) on non-zero exit, prints `"husky - $n script failed (code $c)"`, and specifically `"husky - command not found in PATH=$PATH"` when the exit code is 127.

[Source: https://typicode.github.io/husky/] This architecture means Husky itself has **no runtime presence during hook execution** beyond this thin POSIX dispatcher — the "install" step is a one-time `git config` mutation plus file scaffolding; actual hook execution is native Git invoking a shell script, with no Node.js process required unless the hook script itself calls `node`/`npm`/`npx`.

[Source: https://blog.typicode.com/posts/husky-git-hooks-autoinstall/] Architecturally, Husky **does not auto-install itself** as a side effect of `npm install` (this was true of a prior design and was deliberately removed — see Section 6/13 for the rationale). Installation is instead wired through the package-manager-native `prepare` lifecycle script (or `postinstall` for Yarn, which lacks `prepare` support), which the maintainer blog frames as more transparent and reliable than a silent `postinstall`-based auto-install, and as compatible with Yarn 2 zero-installs.

## 3. APIs

[Source: https://raw.githubusercontent.com/typicode/husky/main/bin.js] Husky's entire CLI surface is a single positional argument, read directly from the current `bin.js` source:
- `husky init` — [Source: https://typicode.github.io/husky/get-started.html] "simplifies setting up husky in a project. It creates a `pre-commit` script in `.husky/` and updates the `prepare` script in `package.json`." [Source: https://raw.githubusercontent.com/typicode/husky/main/bin.js] Per source, `init` specifically: sets `package.json`'s `scripts.prepare` to `"husky"` (preserving existing tab/space indentation style), runs the install routine, creates `.husky/pre-commit` containing `"<detected-package-manager> test\n"` (package manager name sniffed from the `npm_config_user_agent` env var, defaulting to `npm`).
- `husky` (no argument) or `husky <dir>` — runs the install routine described in Section 2 against `.husky` or a custom directory.
- `husky add`, `husky set`, `husky uninstall` — [Source: https://raw.githubusercontent.com/typicode/husky/main/bin.js] explicitly **DEPRECATED**: the CLI prints `"husky - <cmd> command is DEPRECATED"` and **exits with code 1** (hard failure, not just a warning) for these three subcommands.
- `husky install` — [Source: https://raw.githubusercontent.com/typicode/husky/main/bin.js] deprecated but **does not fail**: prints the deprecation warning to stderr, then proceeds to run the same install routine as bare `husky` (the `install` token itself is discarded and treated as no directory argument).

[Source: https://raw.githubusercontent.com/typicode/husky/main/index.d.ts] The programmatic/library API (`import husky from 'husky'`) is a single default export with the TypeScript signature `export default function (dir?: string): string;` — it runs the install routine documented in Section 2 and returns a human-readable status/result string (e.g., `''` on success, or a message like `'.git can't be found'`, `'git command not found'`, `'.. not allowed'`, `'HUSKY=0 skip install'` on early-exit/failure paths) rather than throwing.

[Source: https://typicode.github.io/husky/how-to.html] There is no dedicated "hook builder" API beyond file creation — hook files are plain shell scripts invoked positionally by Git with native Git hook arguments (e.g., `commit-msg` receives the commit-message file path as `$1`, replacing the old `HUSKY_GIT_PARAMS` mechanism — see Section 11).

## 4. Configuration

[Source: https://typicode.github.io/husky/get-started.html] Primary install-time configuration is the `prepare` script in `package.json`: `"prepare": "husky"` for npm/pnpm/bun; `"postinstall": "husky"` for Yarn (which "doesn't support prepare script"), optionally paired with `"prepack": "pinst --disable"` / `"postpack": "pinst --enable"` for packages published to npm (to avoid running the install hook for consumers of the published package).

[Source: https://typicode.github.io/husky/how-to.html] Hook behavior is configured per-hook by editing the plain-text file at `.husky/<hook-name>` (e.g., `.husky/pre-commit`), which may contain any POSIX-shell-compatible commands, including multiple lines and calls into other scripting languages via a wrapper (e.g., `node .husky/pre-commit.js`, documented under "Non-shell hooks").

[Source: https://typicode.github.io/husky/how-to.html] **Startup/init files** — Husky sources one of these (first match) before running any hook, in this documented priority: `$XDG_CONFIG_HOME/husky/init.sh`, then `~/.config/husky/init.sh`, then the deprecated `~/.huskyrc`. On Windows this resolves to `C:\Users\yourusername\.config\husky\init.sh`. This is the documented mechanism for making Node-version-manager shims (`nvm`, `fnm`, `asdf`, `volta`, etc.) available to hooks launched from GUI clients that don't source a shell profile.

[Source: https://typicode.github.io/husky/how-to.html] **Environment-variable configuration:**
- `HUSKY=0` — globally/temporarily disables both hook *installation* and hook *execution* (checked in both `index.js`'s install routine and the `husky` dispatcher script, per source read in Sections 2–3). Documented uses: skip a single command range (`export HUSKY=0 ... unset HUSKY`), disable permanently for a machine/GUI by exporting it from `~/.config/husky/init.sh`, or disable install on CI/Docker via a CI env var (e.g., GitHub Actions `env: HUSKY: 0`).
- `HUSKY=2` — [Source: https://raw.githubusercontent.com/typicode/husky/main/husky] (source-code-only; not called out in the prose docs) enables shell trace mode (`set -x`) in the dispatcher for debugging hook execution — see Section 15.
- Git's own `-n`/`--no-verify` flag — [Source: https://typicode.github.io/husky/how-to.html] skips hooks for a single Git command (e.g., `git commit -n`), independent of any Husky-specific variable.

[Source: https://typicode.github.io/husky/how-to.html] **Non-root-of-repo (monorepo/subfolder) configuration:** when `package.json` is not at the Git root, point the `prepare` script at a subfolder-relative `.husky` directory, e.g. `"prepare": "cd .. && husky frontend/.husky"`, and have the hook script itself `cd` back into the relevant subfolder before running commands.

## 5. Recommended patterns

[Source: https://typicode.github.io/husky/get-started.html] Use `husky init` as the recommended (not just supported) setup path over manual setup; manual setup is documented separately as a fallback ("Manual setup" section of How To) for cases `init` doesn't fit.

[Source: https://typicode.github.io/husky/get-started.html] Recommended lint-staged-adjacent pattern for a lightweight, dependency-free staged-file formatter, quoted directly from the docs:
```
# .husky/pre-commit
prettier $(git diff --cached --name-only --diff-filter=ACMR | sed 's| |\\ |g') --write --ignore-unknown
git update-index --again
```
The docs immediately note: "This is a basic but working example, check [lint-staged](https://github.com/lint-staged/lint-staged) if you need more" — i.e., Husky's own docs explicitly point to `lint-staged` as the recommended tool for anything beyond this trivial case, rather than Husky reimplementing staged-file filtering itself.

[Source: https://typicode.github.io/husky/how-to.html] For CI/production installs that skip devDependencies, the docs recommend either `"prepare": "husky || true"` (accepts the noisy "command not found" message) or a guarded `.husky/install.mjs` that early-exits when `NODE_ENV === 'production'` or `CI === 'true'` before dynamically importing `husky`, invoked via `"prepare": "node .husky/install.mjs"` — this is presented as the cleaner, silent alternative.

[Source: https://typicode.github.io/husky/how-to.html] For testing a hook without actually committing, temporarily add `exit 1` to the end of the hook script so the Git command aborts even on success, letting you inspect output without creating the commit.

[Source: https://typicode.github.io/husky/how-to.html] For teams mixing Windows and POSIX developers, keep hook scripts strictly POSIX `sh` compliant rather than assuming `bash`; if the whole team is on a platform with `bash`, the docs show wrapping bash-specific code in a heredoc (`bash << EOF ... EOF`) inside the POSIX entrypoint file as an escape hatch.

## 6. Anti-patterns

[Source: https://blog.typicode.com/posts/husky-git-hooks-autoinstall/] Auto-installing hooks as a `postinstall` side effect is presented as a rejected/removed anti-pattern: the maintainer blog cites npm's own guidance that "The only valid use of install or preinstall scripts is for compilation," reliability breakage from package-manager install caching (a failed auto-install wouldn't retry on a cached re-`install`), and package managers increasingly suppressing `postinstall` output (removing user feedback) as the reasons this approach was abandoned in favor of the explicit `prepare`-script model.

[Source: https://blog.typicode.com/posts/husky-git-hooks-javascript-config/] Maintaining hook logic in a separate JS config file (the pre-v6 `.huskyrc.js` model) that has to be kept in sync with `.git/hooks/` is presented as an architectural anti-pattern the redesign eliminated — "Generating Git hooks from a JS config can get out of sync," per the blog.

[Source: https://typicode.github.io/husky/troubleshoot.html] Naming hook files incorrectly (e.g., `precommit` or `pre-commit.sh` instead of exactly `pre-commit`) is documented as a common cause of hooks silently not running — Husky enforces exact Git hook naming, not a fuzzy match.

[Source: https://raw.githubusercontent.com/typicode/husky/main/index.js] Referencing a hooks directory outside the repo (any path containing `..`) is explicitly rejected by the install routine (`if (d.includes('..')) return '.. not allowed'`) — see Section 7 for the stated security rationale.

## 7. Security

[Source: https://typicode.github.io/husky/how-to.html] "Husky doesn't install in parent directories (`../`) for security reasons." [Source: https://raw.githubusercontent.com/typicode/husky/main/index.js] This is enforced in code: the install function returns the string `'.. not allowed'` and aborts if the target directory argument contains `..`, before any filesystem or `git config` mutation occurs.

[Source: https://raw.githubusercontent.com/typicode/husky/main/husky] Because the dispatcher prepends `node_modules/.bin` to `PATH` before executing the hook script (`export PATH="node_modules/.bin:$PATH"`), locally installed CLI tools (linters, formatters, test runners installed as devDependencies) are directly invocable by name from hook scripts without an `npx`/`./node_modules/.bin/` prefix. [Inference, not confirmed in docs] This also means a hook script executes with the ambient trust/PATH context of whatever `node_modules` are present in the working tree, so supply-chain-compromised devDependencies could execute code at commit/push time — the official docs do not discuss this risk explicitly; flagged here as a reasonable inference from the documented PATH behavior, not a documented warning.

[Source: https://api.github.com/repos/typicode/husky/security-advisories] No GitHub Security Advisories were found published against `typicode/husky` as of the research date (query returned an empty list).

No official docs page is specifically titled "Security" — the security-relevant content documented above is drawn from the "How To" install-directory constraint and source-code inspection, not from a dedicated security guide. Not documented / could not verify: any official guidance on hook-script code review, signing, or supply-chain mitigation beyond the parent-directory restriction.

## 8. Performance

[Source: https://typicode.github.io/husky/] Explicit, quantified performance claims from the official docs: package size "Just `2 kB` (gzipped) with no dependencies," and execution overhead "runs in `~1ms`" — attributed to using native `core.hooksPath` instead of a heavier wrapper mechanism.

[Source: https://blog.typicode.com/posts/husky-git-hooks-javascript-config/] The pre-v6 architecture (all hooks installed into `.git/hooks/`, each checking a JS config at runtime) is described as wasteful because "Node started unnecessarily for undefined hooks" — i.e., every configured Git hook paid a Node.js startup cost even when no user logic existed for that hook. The `core.hooksPath`-based redesign (v6+) avoids this: only hooks that have a corresponding non-empty file in `.husky/` do anything, and the dispatcher itself is plain POSIX `sh`, not Node.

[Source: https://api.github.com/repos/typicode/husky/releases (v9.1.1 entry, paraphrased from the release notes)] v9.1.1 added the ability to invoke locally installed package binaries directly by name inside hook scripts without an `npx` prefix, described in the release notes as an approximately 0.2-second performance improvement per invocation (avoiding `npx`'s own resolution overhead). Version-sensitive: this direct-invocation behavior is a v9.1.1+ feature, not present in earlier v9.0.x releases.

## 9. Testing

[Source: https://typicode.github.io/husky/how-to.html] The only officially documented technique for testing a hook without side effects is to temporarily append `exit 1` to the hook script, run the corresponding Git command (e.g., `git commit -m "testing pre-commit code"`), observe the hook's output, and confirm the Git operation was aborted ("A commit will not be created"), then remove the `exit 1` line.

Husky itself does not document or ship a dedicated testing framework, mocking utility, or CI-testing guide for hook scripts — hooks are treated as ordinary shell scripts, and testing them is documented as testing any shell script would be (manual invocation, `exit 1` guarding). Not documented / could not verify: any official guidance on unit-testing hook logic in isolation from Git, or on asserting hook behavior in a CI pipeline.

## 10. Deployment

Husky has no "deployment" concept of its own in the sense of a deployed service — it is a devDependency whose "deployment" is installation into each contributor's and CI runner's local Git configuration via the `prepare`/`postinstall` lifecycle script. The relevant documented concern is **not deploying/installing it where undesired**:

[Source: https://typicode.github.io/husky/how-to.html] "To avoid installing Git Hooks on CI servers or in Docker, use `HUSKY=0`," with a worked example for GitHub Actions (`env: HUSKY: 0`).

[Source: https://typicode.github.io/husky/how-to.html] For production-only installs (`--omit=dev`/`--production`) where Husky's devDependency itself isn't installed, the `prepare` script would otherwise fail with `command not found`; the documented fixes are `"prepare": "husky || true"` or the guarded `.husky/install.mjs` dynamic-import pattern described in Section 5.

## 11. Migration

[Source: https://typicode.github.io/husky/migrate-from-v4.html] Official migration guide covers **v4 → v9 (current major line)** only; no v5–v8 dedicated migration doc was found (v5–v8 are treated by the docs as part of the same "modern" `.husky/`-file-based model introduced at v6, per the architecture blog post). Documented v4→v9 changes:
- Config model: v4's `package.json` `"hooks"` object (or `.huskyrc.json`) is replaced by one file per hook under `.husky/`. Example given: v4 `"pre-commit": "npm test && npm run foo"` becomes a `.husky/pre-commit` file containing `npm test` and `npm run foo` on separate lines — "Note that you can now have commands on multiple lines."
- Locally installed binaries: v4 could reference a binary name directly (e.g., `"pre-commit": "jest"`) via its own resolution; in v9 the equivalent is just `jest` as a line in `.husky/pre-commit` (resolved via the `node_modules/.bin`-prepended `PATH`, per Section 2/7).
- Environment variables: `HUSKY_SKIP_HOOKS` → replaced by `HUSKY`; `HUSKY_SKIP_INSTALL` → replaced by `HUSKY`; `HUSKY_GIT_PARAMS` → **removed entirely**, replaced by native positional Git hook parameters (`$1`, `$2`, …) — worked example: v4 `"commit-msg": "commitlint -E HUSKY_GIT_PARAMS"` becomes v9 `.husky/commit-msg` containing `commitlint --edit $1`.

No official "migrating from a comparable alternative" (e.g., from `pre-commit` (Python), `lefthook`, or native raw Git hooks into Husky) guide was found — Not documented / could not verify.

## 12. Version information

[Source: https://raw.githubusercontent.com/typicode/husky/main/package.json ; https://api.github.com/repos/typicode/husky/releases] Current stable: **v9.1.7**, published 2024-11-18. Recent v9.1.x release history per the GitHub Releases API: v9.1.6 (2024-09-11, "Fixed incorrect generation of example pre-commit file"), v9.1.5 (2024-08-20, added `pre-merge-commit` hook support), v9.1.1 (2024-07-18, enabled direct package-binary invocation without `npx`, fixed `bunx husky init`, Windows workaround), v9.1.0 (2024-07-17), v9.0.11 (2024-02-13) down through v9.0.x patch releases in Jan–Feb 2024.

[Source: https://raw.githubusercontent.com/typicode/husky/main/package.json] `engines.node` for the current stable release is `>=18`. Version-sensitive: [Source: https://api.github.com/repos/typicode/husky (commit history, 2025-10-10 commit message)] a CI workflow commit titled "ci: remove Node.js 18, add 24 to Node.js CI workflow" post-dates the v9.1.7 release and suggests the *next* release's tested/supported Node range may shift upward from `>=18`, but **as of this research date no new npm version has been published reflecting that change** — the published `package.json`'s `engines` field still reads `>=18`. Unresolved: whether this CI change will land in a future 9.1.x patch or is being held for an unreleased v10.

No official LTS/support-window policy (in the sense of "version X is supported until date Y") was found for Husky — Not documented / could not verify. The project does not publish a support matrix; only the deprecation-then-removal pattern described in Section 13 (warn in v9.x, remove in v10.0.0) constitutes documented forward-compatibility signaling.

[Inference, not confirmed in docs] Given no release since November 2024 as of September 2026, and only documentation/CI-metadata commits in the repository's recent history, the project reads as being in low-activity/maintenance mode at the time of this research, though it remains unarchived and open-issue triage continues (108 open issues per the GitHub API at research time).

## 13. Breaking changes

[Source: https://raw.githubusercontent.com/typicode/husky/main/index.js] Per the current source, when Husky installs, if it detects the two legacy lines below still present in a hook file, it prints (verbatim, from the `msg` template literal in source):
```
husky - DEPRECATED

Please remove the following two lines from <file>:

#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

They WILL FAIL in v10.0.0
```
This confirms two concrete, officially-flagged breaking changes planned for **v10.0.0** (unreleased as of this research date, per Section 12): the shebang line `#!/usr/bin/env sh` and the sourcing line `. "$(dirname -- "$0")/_/husky.sh"`, both auto-stripped by Husky today as a courtesy but which "WILL FAIL" once v10.0.0 removes the compatibility shim.

[Source: https://typicode.github.io/husky/how-to.html] Separately and consistent with the above: "`~/.huskyrc` (deprecated)" is listed as a still-supported-but-deprecated startup-file location, with `~/.config/husky/init.sh` (or `$XDG_CONFIG_HOME/husky/init.sh`) as its replacement — [Source: https://raw.githubusercontent.com/typicode/husky/main/husky] the dispatcher script prints a runtime warning `"husky - '~/.huskyrc' is DEPRECATED, please move your code to ~/.config/husky/init.sh"` whenever that file is found, though no explicit removal version is stated for this specific deprecation (unlike the shebang/sourcing-line deprecation above, which is explicitly tied to v10.0.0).

[Source: https://raw.githubusercontent.com/typicode/husky/main/bin.js] Confirmed **already-breaking** (present-tense, in the current v9.1.7 CLI, not a future warning): the `husky add`, `husky set`, and `husky uninstall` subcommands print a deprecation message and **exit with a non-zero status (1)** — i.e., these v4/early-v9 commands are already hard-broken in the current release, not merely warned-about.

[Source: https://typicode.github.io/husky/migrate-from-v4.html] The v4→v9 major-version transition (see Section 11) is itself the largest documented breaking change in the project's history: config model moved from `package.json`/`.huskyrc.json` to per-hook files in `.husky/`, and `HUSKY_GIT_PARAMS`/`HUSKY_SKIP_HOOKS`/`HUSKY_SKIP_INSTALL` env vars were replaced/removed as described in Section 11.

## 14. Limitations

[Source: https://typicode.github.io/husky/how-to.html] Hook scripts must be POSIX `sh` compliant for cross-platform reliability — "not everyone has `bash`" (explicitly called out for Windows users), so Bash-specific syntax requires an explicit `bash << EOF ... EOF` wrapper rather than being usable directly as the hook's shebang/body.

[Source: https://typicode.github.io/husky/how-to.html] Husky will not install its hooks directory into a parent directory (`../`) of the current install location — documented as a deliberate limitation for security, not a bug (see Section 7).

[Source: https://typicode.github.io/husky/how-to.html] Yarn does not support the `prepare` lifecycle script, so Yarn users must use `postinstall` instead (plus `pinst` to suppress that hook when the package itself is published to npm) — this is a limitation of Yarn's lifecycle model that Husky's docs explicitly work around rather than something Husky itself can control.

[Source: https://typicode.github.io/husky/troubleshoot.html] Documented platform-specific limitation: Yarn on Windows under Git Bash can fail with a `stdin is not a tty` error; the only documented fix is a manual `winpty`/`/dev/tty` shell workaround the user must add to their own hook scripts (Section 15 has the full snippet) — i.e., this is not something Husky resolves automatically.

[Source: https://typicode.github.io/husky/how-to.html] GUI Git clients and hooks launched outside an interactive shell do not inherit a Node-version-manager-modified `PATH` by default, causing `command not found` errors for `node`/`npm`/etc.; Husky's only documented mitigation is the `init.sh` startup-file mechanism (Section 4), which requires the user to manually replicate their version manager's shell-init logic — this is not automatic.

[Source: https://raw.githubusercontent.com/typicode/husky/main/husky] Git version limitation: [Source: https://typicode.github.io/husky/troubleshoot.html] the troubleshooting guide states hooks not running may be because "your Git version is above `2.9`" is a prerequisite to check — implying Husky's `core.hooksPath`-based mechanism requires **Git ≥ 2.9** (the version that introduced `core.hooksPath`, per the architecture blog cited in Section 1), and will not function on older Git.

## 15. Debugging

[Source: https://typicode.github.io/husky/troubleshoot.html] Documented troubleshooting checklist for "Hooks not running": (1) verify the hook file name exactly matches a valid Git hook name (invalid examples explicitly called out: `precommit`, `pre-commit.sh`); (2) run `git config core.hooksPath` and confirm it points to `.husky/_` (or your custom hooks directory); (3) confirm the installed Git version is above `2.9`.

[Source: https://typicode.github.io/husky/troubleshoot.html] If hooks in `.git/hooks/` stop working after uninstalling Husky, the fix is `git config --unset core.hooksPath` — because Husky's install step repoints `core.hooksPath` away from the default `.git/hooks/` and uninstalling the package doesn't automatically revert that Git config setting.

[Source: https://raw.githubusercontent.com/typicode/husky/main/husky] Source-level (not prose-documented) debug mechanism: setting `HUSKY=2` before a Git command triggers `set -x` in the dispatcher script, tracing every shell command the dispatcher executes — useful for diagnosing `PATH`/environment issues at the exact point of hook invocation. This is present in the shipped dispatcher script but is **not mentioned anywhere in the prose documentation pages** fetched for this research — flagged as source-only, verify behavior against your installed version before relying on it in documentation-facing material.

[Source: https://raw.githubusercontent.com/typicode/husky/main/husky] The dispatcher also self-reports two specific failure signatures to stderr: a generic `"husky - <hook> script failed (code <N>)"` for any non-zero exit, and specifically `"husky - command not found in PATH=<value>"` when the exit code is exactly 127 (the POSIX "command not found" convention) — the latter message prints the resolved `PATH` inline, which is the documented starting point for diagnosing version-manager/PATH issues described in Section 4/14.

[Source: https://typicode.github.io/husky/troubleshoot.html] For the Windows + Git Bash + Yarn `stdin is not a tty` failure, the documented debug/fix workflow is to add a `.husky/common.sh` helper (`command_exists` check plus `exec < /dev/tty` when `winpty` is present and stdout is a TTY) and source it from any hook that shells out to `yarn`.

## 16. Integration

[Source: https://typicode.github.io/husky/get-started.html] Explicitly documented integration with **lint-staged**: the docs' own "staged files" example is described as "basic," directing readers to lint-staged "if you need more" — i.e., Husky is documented as the trigger mechanism, deliberately not the staged-file-filtering mechanism, with lint-staged as the recommended complement.

[Source: https://typicode.github.io/husky/migrate-from-v4.html] Explicitly documented integration with **commitlint** (`commitlint --edit $1` as the `commit-msg` hook body, replacing the old `HUSKY_GIT_PARAMS`-based invocation).

[Source: https://typicode.github.io/husky/how-to.html] Explicitly documented integration with **pinst** for Yarn-based packages that are themselves published to npm (`prepack`/`postpack` scripts toggling install-script behavior so consumers of the published package don't inherit the maintainer's Husky install).

[Source: https://typicode.github.io/husky/how-to.html] Explicitly documented package-manager integrations: npm, pnpm, Yarn, and Bun each have their own install/init/prepare command variants shown side-by-side in the docs' code-group tabs (Section 4 above has the exact commands per manager).

[Source: https://typicode.github.io/husky/how-to.html] Explicitly documented CI integration pattern: GitHub Actions, via the `HUSKY: 0` environment variable set in the workflow YAML (Section 10). No other CI system (GitLab CI, CircleCI, Jenkins, etc.) has a dedicated worked example in the fetched docs, though the underlying mechanism (`HUSKY=0` as a plain env var) is platform-agnostic — Not documented / could not verify for CI systems beyond GitHub Actions specifically.

[Source: https://typicode.github.io/husky/] "Used by" section lists large open-source consumers as evidence of ecosystem integration/adoption: vercel/next.js, vercel/hyper, webpack/webpack, angular/angular, facebook/docusaurus, microsoft/vscode, 11ty/eleventy, stylelint/stylelint, colinhacks/zod, rollup/rollup, tinyhttp/tinyhttp, and states Husky is used in "over 1.5M projects" on GitHub per the GitHub dependents graph linked from the docs.

## 17. Production considerations

[Source: https://typicode.github.io/husky/how-to.html] The primary documented production concern is **not installing Husky where it shouldn't run**: CI servers and Docker builds should set `HUSKY=0` to skip hook installation entirely, and production-only (`--omit=dev`) installs need the `prepare` script guarded (`husky || true`, or the `.husky/install.mjs` `NODE_ENV`/`CI`-checking pattern) so a missing devDependency doesn't fail the install step.

[Source: https://typicode.github.io/husky/how-to.html] For teams with a subset of contributors on Windows, the documented production-readiness concern is POSIX-shell compliance of every hook script (Section 14) plus the Yarn/Git-Bash TTY workaround (Section 15) — these are the two Windows-specific failure modes the docs call out as needing explicit handling before hooks can be relied on team-wide.

[Source: https://typicode.github.io/husky/how-to.html] For teams using Node version managers, the documented production-readiness step is populating `~/.config/husky/init.sh` (a machine-local, not repo-committed, file) with the version manager's shell-init code so that hooks triggered from GUI Git clients (which don't source a shell profile) can still resolve `node`. This is inherently a per-developer-machine setup step, not something the repository's committed `.husky/` files can fully solve on their own — [Inference, not confirmed in docs] teams likely need onboarding documentation of their own to ensure every contributor sets this up, since Husky cannot commit a machine-specific home-directory file into the repo.

[Source: https://typicode.github.io/husky/how-to.html] For monorepos or projects where `package.json` isn't at the Git root, production setup requires the non-default `prepare` script pattern (`cd .. && husky <subdir>/.husky`, Section 4) plus a matching `cd` at the top of every hook script — this is manual, per-project configuration rather than something `husky init` scaffolds automatically for non-root layouts.

No official docs page addresses production considerations like hook execution time budgets, monitoring hook failures across a team/fleet, or centrally enforcing that hooks aren't bypassed (`--no-verify` is always available to any local Git user, and the docs do not claim otherwise) — Not documented / could not verify. [Inference, not confirmed in docs] Because Husky hooks are client-side and can always be skipped locally with `--no-verify` or `HUSKY=0`, teams needing guaranteed enforcement (not just "same checks locally as in CI, as a convenience") would still need server-side checks (CI pipeline, branch protection) as the actual gate — the docs' "Used by" and integration content frames Husky purely as a local developer-experience/consistency tool, not a security or compliance control.
