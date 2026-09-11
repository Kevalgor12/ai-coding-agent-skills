---
name: Sass
description: >-
  Sass-specific stylesheet authoring: the @use/@forward module system,
  mixins, functions, selector inheritance (@extend), control flow, and
  built-in sass:* modules, using Dart Sass (the only actively maintained
  implementation). Use when .scss/.sass files, a sass/sass-embedded
  dependency, or a Sass-specific construct is present, or the task names
  Sass/SCSS. Not for Less/Stylus/plain CSS, framework component-styling
  APIs, or Tailwind-only utility-class work with no Sass files involved.
spec_version: "1.0"
---

## Purpose & scope

Apply Sass correctly and version-appropriately: the `@use`/`@forward` module
system, mixins, selector inheritance, built-in `sass:*` modules, and
migrating off the deprecated `@import` syntax and the end-of-life
LibSass/Node Sass/Ruby Sass implementations onto Dart Sass. The generic
styling-architecture method (design tokens, scoping strategy, whether to use
a preprocessor at all) comes from the parent skill `SK-FE-003`
(styling-systems). This skill supplies the Sass-language and
Dart-Sass-specific detail.

## When to use / When not to use

**Use** when `.scss`/`.sass` files, a `sass`/`sass-embedded` dependency, a
bundler's Sass-preprocessing config, or a Sass-specific construct (`@use`,
`@mixin`, `@extend`, `sass:math`, etc.) is present, or the task names
Sass/SCSS — including migrating a legacy `node-sass`/`libsass`/`ruby-sass`
dependency.

**Do not use** for Less/Stylus/plain CSS with no Sass files present (route to
that tool or `SK-TECH-web-standards`), a UI framework's own
component-styling API (route to that framework's skill), or generic
styling-architecture decisions with no Sass in play yet (route to
`SK-FE-003`).

**Sass and Tailwind CSS nuance:** the two are not mutually exclusive at the
project level — utility classes plus authored, preprocessed CSS is a
legitimate combination, and this library does not treat them as conflicting
skills (`conflicts_with: []`). What *is* true, narrowly: Tailwind v4 itself
declines to support using Sass (or Less/Stylus) as a preprocessing step
ahead of it — its docs state such preprocessors are "not supported" and
unnecessary, since Tailwind's own toolchain (Lightning CSS) now performs the
preprocessor-like jobs (imports, nesting, variables, math) they used to
handle [Source: https://tailwindcss.com/docs/compatibility, via
research/technologies/tailwind.md]. That is a build-order/integration
constraint on one specific pipeline pattern (Sass-as-a-step-before-Tailwind),
not a reason to treat "a project uses Sass" and "a project uses Tailwind" as
incompatible choices in general.

## Knowledge

- **Two syntaxes, one language:** SCSS (`.scss`, brace/semicolon, CSS-superset,
  more popular) and the indented syntax (`.sass`, whitespace-significant).
  Both support identical language features. [Source: https://sass-lang.com/documentation/syntax/]
- **The module system (`@use`/`@forward`) is the current recommendation for
  all new code**, replacing `@import`. Each module is loaded and evaluated
  exactly once per compilation regardless of how many times it's referenced;
  members are namespaced by default from the last URL path segment
  (`@use "src/corners"` → `corners.$var`); `@use "src/corners" as c` renames
  the namespace; `@use "..." as *` loads unnamespaced but the docs caution to
  use it "cautiously" due to collision risk. `@use` rules must appear before
  any other rules (aside from `@forward`) — position-constrained at the top
  of a file, unlike `@import`. [Source: https://sass-lang.com/documentation/at-rules/use/]
- **Module configuration:** a module declares configurable variables with
  `!default`; consumers override at load time with
  `@use 'library' with ($variable: value, ...)`. Configuration only applies on
  a module's *first* load in a compilation — it cannot be reconfigured
  differently by two different loaders in the same compile; design around a
  single central config entrypoint. [Source: https://sass-lang.com/documentation/at-rules/use/]
- **Mixins/functions/extend/control flow:** `@mixin`/`@include` (reusable
  style chunks), `@function` (custom SassScript functions), `@extend`
  (selector inheritance), `@if`/`@else`/`@for`/`@each`/`@while` (control
  flow), `@error`/`@warn`/`@debug` (diagnostics). [Source: https://sass-lang.com/documentation/at-rules/]
- **Built-in `sass:*` modules** (loaded via `@use "sass:<name>"`): `sass:math`,
  `sass:string`, `sass:color`, `sass:list`, `sass:map`, `sass:selector`, and
  `sass:meta` (introspection — `get-function()`, `call()`,
  `feature-exists()`, type predicates). Prefer these over legacy global
  functions/operators (e.g. `math.div()` over `/`-as-division, which is
  deprecated). [Source: https://sass-lang.com/documentation/modules/]
- **`@import` is deprecated on a long, dated track, not removed today.**
  Deprecation warnings started at Dart Sass **1.80.0**; the deprecation
  period runs until Dart Sass **3.0.0**, which "will not release sooner than
  two years after version 1.80.0" — eventually `@import` will be treated as
  plain-CSS `@import` only. `@import` still compiles and works right now.
  [VERSION-SENSITIVE: >=1.80.0, through the window ending no earlier than two
  years post-1.80.0.] [Source: https://sass-lang.com/documentation/breaking-changes/import/]
- **Implementations:** Dart Sass is the sole actively-developed, reference
  implementation ("gets new features before any other implementation").
  LibSass and Ruby Sass were both declared deprecated 2020-10-26; Node Sass
  (the LibSass Node wrapper) reached end-of-life **2024-07-24** — npm package
  deprecated, GitHub repo archived. [Source: https://sass-lang.com/dart-sass/]
  [Source: https://sass-lang.com/blog/node-sass-is-end-of-life/]
- **Distribution:** standalone CLI (Dart VM), a Dart library via pub.dev, and
  two npm packages — `sass` (pure JS, most portable) and `sass-embedded`
  (native Dart VM subprocess via the Embedded Sass protocol, generally
  faster, restricted to supported OS/arch). [Source: https://sass-lang.com/dart-sass/]
  [Source: https://sass-lang.com/documentation/js-api/]
- **Current reference target: Dart Sass 1.104.0** (as of 2026-09-09), with
  recent releases (1.103.1/1.103.0/1.102.0/1.101.7) shipping roughly every
  1-4 weeks — an actively, rapidly maintained project; treat "latest" as a
  moving target. [Source: https://sass-lang.com/documentation/]
  [Source: https://github.com/sass/dart-sass/releases]

> A fuller, dated breaking-changes table (25+ entries) lives in
> [`references/breaking-changes.md`](references/breaking-changes.md) — loaded
> only when a specific version-gated behavior needs checking (context-efficiency
> rule CE-3).

## Decision framework

1. **Simplest first (anti-overengineering):** does the project actually need
   a preprocessor? Modern native CSS (nesting, custom properties, container
   queries) covers a growing share of what Sass historically provided.
   Reach for Sass when the project needs its module system, mixins/functions,
   or an existing Sass codebase already exists — not by default.
2. **`@use`/`@forward` vs. `@import` for new code:** always `@use`/`@forward`
   for anything new. `@import` pollutes global scope, requires manual
   namespace-collision avoidance, and re-compiles the same file repeatedly if
   imported more than once — all problems the module system solves — and it
   is on a dated deprecation track (warnings since 1.80.0, removal no sooner
   than two years after that, at Dart Sass 3.0.0). [Source: https://sass-lang.com/documentation/at-rules/use/]
   For an *existing* `@import`-based codebase, don't do a disruptive big-bang
   rewrite by default: use `sass-migrator module [--migrate-deps]` for an
   automated, reviewable conversion, and use `--quiet-deps`/`--silence-deprecation`
   to manage third-party warning noise in the interim without silencing
   first-party warnings. [Source: https://sass-lang.com/documentation/cli/migrator/]
   [Source: https://sass-lang.com/documentation/cli/dart-sass/]
3. **Dart Sass vs. any remaining legacy implementation:** there is no live
   alternative — LibSass, Ruby Sass, and Node Sass are all deprecated/EOL and
   receive best-effort-or-no further fixes. If a repo still depends on one,
   the decision is not "which implementation" but "migrate to Dart Sass,
   and on what timeline," weighed against the size of the custom-function/
   importer surface that has to be ported. [Source: https://sass-lang.com/blog/libsass-is-deprecated/]
   [Source: https://sass-lang.com/blog/node-sass-is-end-of-life/]
4. **`sass` vs. `sass-embedded` npm package:** `sass-embedded` is generally
   faster (native Dart VM subprocess) but restricted to supported OS/arch
   combinations; `sass` (pure JS) is the more portable default. Choose
   `sass-embedded` when compile performance is a measured bottleneck and the
   target platforms are supported, not by default. [Source: https://sass-lang.com/documentation/js-api/]
5. **Sync vs. async JS API:** prefer `compile()`/`compileString()`
   (synchronous) — the docs state the async variants are "much slower" and
   exist specifically to support async custom importers/functions, not for
   general use. [Source: https://sass-lang.com/documentation/js-api/]

## Workflow

1. Determine the current Sass setup: syntax (`.scss`/`.sass`), build
   integration (CLI, bundler loader, JS/Dart API), package (`sass` vs.
   `sass-embedded` vs. a legacy implementation), and Dart Sass version.
2. For new stylesheets: structure with `@use`/`@forward`, `!default` +
   `with(...)` for themeable configuration, and namespaced member access.
3. For an `@import`-migration task: run `sass-migrator module --dry-run`
   first, review the diff, then apply; flag the run for confirmation if it
   touches the whole repository (see Escalation).
4. For a legacy-implementation migration (Node Sass/LibSass/Ruby Sass →
   Dart Sass): confirm no custom C++/Ruby extension points are relied on,
   swap the dependency, and re-run the build to confirm the module-system
   surface compiles (module system is Dart-Sass-only).
5. Verify (below) before declaring done.

## Engineering rules

- Default new code to `@use`/`@forward`; use `@import` only to match an
  existing codebase pending a scheduled migration, never as a fresh choice.
- Use `!default` + `with(...)` for themeable/configurable libraries, not ad
  hoc variable overrides after the fact.
- Use `@use "..." as *` sparingly — the docs' own "cautiously" framing signals
  real collision risk, not a stylistic preference.
- Prefer namespaced `sass:*` module functions (`math.div()`, etc.) over
  legacy global operators/functions that are on the deprecation list.
- Prefer synchronous compilation (`compile`/`compileString`) unless async
  custom importers/functions are genuinely needed.
- Treat any `node-sass`/`libsass`/`ruby-sass` dependency found in a repo as a
  migration item, not a stable baseline — they are EOL/deprecated with no
  further feature development and reduced security-patch assurance.

## Trade-offs

- `@use`/`@forward` requires namespacing member access and a top-of-file
  placement discipline `@import` didn't enforce — more upfront structure, in
  exchange for avoiding global-namespace collisions and redundant
  recompilation. Worth it for anything beyond a trivial single-file
  stylesheet; genuinely optional for a truly tiny project that will never
  grow partials.
- `sass-embedded` trades portability (fewer supported OS/arch combos) for
  compile speed; `sass` (pure JS) trades some speed for running anywhere
  Node.js does.
- A Sass module system in general trades build-step complexity (a compile
  step, a toolchain to keep patched — see Security) for authoring ergonomics
  (mixins, functions, module composition) that modern native CSS only
  partially replicates.

## Anti-patterns

- **Still using Node Sass (or LibSass/Ruby Sass) in 2026** — it is fully
  end-of-life (npm package deprecated, GitHub repo archived since
  2024-07-24) and cannot support the module system at all; this is the
  domain's over-engineering/under-maintenance trap in reverse — clinging to
  legacy tooling rather than adopting the actively developed replacement.
  [Source: https://sass-lang.com/blog/node-sass-is-end-of-life/]
- Starting new code with `@import` "because that's what the rest of the repo
  uses" without a stated migration plan — the deprecation is real and dated,
  not hypothetical. [Source: https://sass-lang.com/documentation/breaking-changes/import/]
- Reaching for `@use "..." as *` by default instead of a real namespace —
  invites silent name collisions as the codebase grows.
- Choosing the async JS API for perceived "modernness" rather than because
  async importers/functions are actually needed — it is documented as
  measurably slower. [Source: https://sass-lang.com/documentation/js-api/]
- Reaching for a full Sass toolchain when the project's needs are fully
  covered by modern native CSS nesting/custom properties/container queries —
  an unnecessary build-step dependency for no remaining benefit.

## Security

- **Tar-permissions vulnerability (the one officially documented Sass
  security incident):** standalone `.tar.gz` release archives (Dart Sass,
  Dart Sass Embedded, Sass Migrator) and specifically the **`sass-embedded`
  npm package before 1.54.5** and the **RubyGems non-native package before
  1.56.2** shipped with incorrect Unix file permissions (757/654 instead of
  755/644), due to a decimal-to-octal conversion bug in the `cli_pkg`
  release tool. Impact: "executable files could be overwritten by all users,
  not just the owner," enabling local privilege escalation against a
  root-owned install extracted from an affected archive. Fix: `cli_pkg`
  2.1.7 plus republished, corrected `.tar.gz` archives; affected installs
  needed to be deleted and reinstalled. **Users who installed via the npm
  `sass` package, Homebrew, or Chocolatey were stated to be unaffected.**
  [VERSION-SENSITIVE: sass-embedded npm <1.54.5; RubyGems non-native
  <1.56.2.] [Source: https://sass-lang.com/blog/security-alert-tar-permissions/]
- LibSass and Node Sass are maintained (per their 2020 deprecation
  announcement) only "on a best-effort basis, including fixing major bugs
  and security issues" — meaning reduced security-patch assurance relative
  to Dart Sass, and for Node Sass specifically, none at all post-EOL
  (2024-07-24, repo archived). [Source: https://sass-lang.com/blog/libsass-is-deprecated/]
- Unresolved: no dedicated general "security considerations" page (untrusted
  Sass input, custom-function/importer sandboxing, supply-chain guidance)
  was found in the official docs. Because custom JS/Dart functions and
  importers can execute arbitrary host code, treat compiling untrusted Sass
  source together with untrusted custom functions/importers as executing
  untrusted code — this specific framing is an inference, not stated in the
  official docs. For the general secrets/injection/trust-boundary threat
  model, defer to `SK-QA-002` (not restated here).

## Performance

- Dart Sass runs on the Dart VM; the docs describe this as providing "a
  substantial performance boost even for JavaScript" via the compiled-to-JS
  `sass` package, with `sass-embedded` (native Dart VM subprocess via the
  Embedded Sass protocol) faster still. [Source: https://sass-lang.com/dart-sass/]
- Synchronous compilation is documented as faster than asynchronous; the
  legacy async `render()` is separately noted as "2-3x slower than
  `renderSync()`." [Source: https://sass-lang.com/documentation/js-api/]
  [Source: https://sass-lang.com/blog/node-fibers-discontinued/]
- **Vendor-benchmark caveat:** the oft-cited "Dart Sass ~5-10x faster than
  Ruby Sass, ~1.5x slower than LibSass" figures come from the Sass team's own
  original Dart Sass announcement — a point-in-time, vendor-sourced
  comparison, not independently re-verified, and not a claim about current
  releases. Do not present it as current or independent fact; re-benchmark
  against the actual versions in play if compile performance genuinely
  matters. [Source: https://sass-lang.com/blog/announcing-dart-sass/ —
  marked in the underlying research as inferred/search-summarized, not
  independently re-fetched]
- The module system's load-once-per-file semantics is itself a documented
  performance property: `@use`/`@forward` avoid the redundant recompilation
  repeated `@import`s of the same file could cause. [Source: https://sass-lang.com/documentation/at-rules/use/]
- Cross-cutting performance method (measurement, profiling discipline)
  is owned by `SK-QA-003`, not restated here.

## Testing

- **Documented gap:** the official Sass documentation does not present a
  dedicated "Testing" section or an officially maintained testing framework
  for Sass stylesheets. `sass:meta`'s introspection functions
  (`feature-exists()`, `get-function()`, `call()`, type predicates) are the
  closest documented building block, but the docs frame `sass:meta` as
  exposing "the details of Sass's inner workings" — introspection, not a
  test framework. [Source: https://sass-lang.com/documentation/modules/]
- Community tools (e.g. the `true` package) exist for Sass unit testing but
  are not part of the official documentation surveyed here — out of scope
  for this skill's grounded claims; verify current docs/registry state
  before recommending one.
- For CSS output correctness, prefer testing at the compiled-CSS or
  visual-regression layer (owned by `SK-QA-001`) over trying to unit-test
  Sass source directly, given the absence of an official framework.

## Failure handling

- If it is unclear whether a codebase can tolerate the `@import`
  deprecation-warning noise from a bulk migration, default to recommending
  `@use`/`@forward` for new code and leave existing `@import` in place
  pending a scheduled migration — never silently rewrite the whole tree
  (rule VA-3, no silent "latest" assumption).
- If the project's build-tool integration (CLI, bundler loader, JS/Dart API)
  cannot be determined, ask or state the assumption rather than guessing.
- If shell is unavailable, produce advisory `.scss`/`.sass` edits and
  configuration recommendations, and state explicitly that compilation was
  not verified.

## Escalation

- Bulk-migrating a large legacy `@import` codebase to `@use`/`@forward` via
  `sass-migrator` is flagged for confirmation before running — namespacing
  changes are a breaking, repository-wide edit.
- A still-present `node-sass`/`libsass`/`ruby-sass` dependency is flagged to
  the user as EOL/deprecated with a recommended Dart Sass migration path,
  rather than silently left in place or silently swapped without notice.

## Outputs & verification

- **Outputs:** new/modified `.scss`/`.sass` stylesheets, `@import`-to-
  `@use`/`@forward` migration edits, and analysis (module-system vs. legacy
  choice, implementation migration, package choice) with the version each
  claim applies to.
- **Verify:** new code uses `@use`/`@forward` unless matching legacy code
  pending migration; every version-specific claim is tagged with its range;
  built-in module usage matches documented function names; any remaining
  Node Sass/LibSass/Ruby Sass dependency is identified and flagged rather
  than treated as equivalent to Dart Sass.

## References

- [`references/breaking-changes.md`](references/breaking-changes.md) — Tier-2
  dated breaking-changes table (25+ entries) and recent point-release
  behavioral changes.
- Source list: see `skill.yaml.source_references` (Sass official
  documentation and sass-lang.com blog, retrieved 2026-09-10, via
  `research/technologies/sass.md` and `research/knowledge-maps/version-matrix.md`).
