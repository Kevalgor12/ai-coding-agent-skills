# Sass

Research date: 2026-09-09. Primary source: official Sass documentation at https://sass-lang.com/documentation/ (canonical docs host; no evidence of a recent host migration was found — the site is still served from sass-lang.com and states copyright "2006–2026 the Sass team", hosted on Netlify, source on GitHub under the `sass` GitHub org).

Note on scope: "Sass" today effectively means the language plus its reference implementation, **Dart Sass**. The two older implementations, LibSass (a C/C++ library) and Ruby Sass, are both officially deprecated/discontinued (see Version information and Migration below). Documentation below is drawn from sass-lang.com's Documentation, Blog, and GitHub release pages for `sass/dart-sass`.

---

## 1. Core concepts

[Source: https://sass-lang.com/documentation/] "Sass is a stylesheet language that's compiled to CSS. It allows you to use variables, nested rules, mixins, functions, and more, all with a fully CSS-compatible syntax."

[Source: https://sass-lang.com/documentation/syntax/] Sass supports two syntaxes:
- **SCSS** (`.scss`) — "a superset of CSS, which means essentially all valid CSS is valid SCSS as well." Uses braces and semicolons like CSS; this is the more popular syntax.
- **Indented syntax** (`.sass`) — Sass's original syntax; uses indentation instead of braces/semicolons ("any time you'd write curly braces in CSS or SCSS, you can just indent one level deeper... any time a line ends in a place where a statement can end, that counts as a semicolon"). Both syntaxes support identical language features — the difference is purely stylistic.

[Source: https://sass-lang.com/documentation/values/] Core SassScript data types: numbers (with or without units), strings (quoted or unquoted), colors (hex, named, or function-based like `rgb()`/`hsl()`), lists (space- or comma-separated, optionally bracketed), maps (key-value pairs), booleans (`true`/`false`), `null` (a singleton), calculations (e.g. `calc()` values used dynamically), and functions (first-class function references via `get-function()`/`call()`).

[Source: https://sass-lang.com/documentation/at-rules/] Core language constructs are exposed as at-rules: `@use`/`@forward`/`@import` (module loading), `@mixin`/`@include` (reusable style chunks), `@function` (custom SassScript functions), `@extend` (selector inheritance), `@error`/`@warn`/`@debug` (diagnostics), and `@if`/`@else`/`@for`/`@each`/`@while` (control flow).

[Source: https://sass-lang.com/documentation/at-rules/use/] Variables, interpolation (`#{}`), nesting, and the parent selector (`&`) are foundational features covered under Style Rules, Variables, and Interpolation in the docs (dedicated pages exist for each — Not fully expanded here beyond what was fetched, but these are documented core-language topics per the site's own table of contents).

## 2. Architecture

[Source: https://sass-lang.com/dart-sass/] Dart Sass is described as "the primary implementation of Sass, which means it gets new features before any other implementation." It runs on the Dart VM for speed and can also be compiled to pure JavaScript.

[Source: https://sass-lang.com/dart-sass/] Distribution/architecture channels:
- **Standalone CLI executable** powered by the Dart VM.
- **Dart library** via pub.dev (add `sass` to `pubspec.yaml`) for use inside Dart programs, with custom function/importer support.
- **npm packages**: `sass` (pure JS compiled from Dart) and `sass-embedded` (a native executable that talks to a Dart VM subprocess via the **Embedded Sass protocol** for higher performance), both exposing a modern JS API and legacy Node Sass–compatible API.
- **Embedded Sass protocol**: a language-agnostic protocol letting "any programming language communicate directly with the Dart VM" for compilation; official/community wrapper packages exist for Go, Java, Ruby, Rust, and .NET.

[Source: https://sass-lang.com/blog/announcing-dart-sass/] [Inference from search-summarized content, not independently re-verified against the primary text] Early benchmarks cited by the Sass team indicated Dart Sass was roughly 5–10x faster than Ruby Sass and about 1.5x slower than LibSass for large stylesheets at the time of that announcement — version-specific historical claim, not necessarily true of current releases.

[Source: https://sass-lang.com/documentation/at-rules/use/] The module system (`@use`/`@forward`) is itself an architectural feature: each module/file is loaded and evaluated exactly once per compilation regardless of how many times it's referenced, with member namespacing by default derived from the last URL path component.

## 3. APIs

### JavaScript API
[Source: https://sass-lang.com/documentation/js-api/] Modern entry points: `compile()` and `compileAsync()` (compile from a file path) and `compileString()`/`compileStringAsync()` (compile from a string), each accepting an `Options`/`StringOptions` object controlling output style, custom importers, custom functions, source maps, etc. "The asynchronous variants are much slower, but they allow custom importers and functions to run asynchronously."

[Source: https://sass-lang.com/documentation/js-api/] Custom importers are supported, including a built-in `NodePackageImporter` for Node-style package resolution (`pkg:` URLs).

[Source: https://sass-lang.com/documentation/js-api/] The legacy `render()`/`renderSync()` API remains available for backward compatibility but is deprecated; the docs state it "will continue to be supported until the release of version 2.0.0 of the sass package." [VERSION-SENSITIVE: legacy API removal is tied to a future `sass` npm package 2.0.0, not yet released as of the docs snapshot used here.]

[Source: https://sass-lang.com/documentation/js-api/] Package choice tradeoff: `sass` (pure JS, most portable) vs. `sass-embedded` (native Dart VM subprocess via Embedded protocol, generally faster, restricted to supported OS/arch combinations).

### CLI
[Source: https://sass-lang.com/documentation/cli/dart-sass/] Two compile modes: one-to-one (`sass <input.scss> [output.css]`) and many-to-many (`sass <input>:<output> <input-dir>:<output-dir> ...`). Key flags: `--watch`/`-w` (recompile on change), `--style` (`expanded` default or `compressed`), `--load-path`/`-I` (add stylesheet search directories, repeatable), `--source-map-urls` (`relative` default or `absolute`), `--embed-source-map`, `--embed-sources`, `--no-source-map`, `--stdin`, `--indented` (parse stdin as indented syntax), `--pkg-importer=node` (Node-style package resolution), `--error-css` (emit CSS describing compile errors), `--update` (only recompile changed files), `--poll` (manual change polling for remote/network filesystems), `--interactive`/`-i` (SassScript REPL), `--quiet`/`-q` (suppress warnings).

### Sass Migrator (separate CLI tool)
[Source: https://sass-lang.com/documentation/cli/migrator/] `sass-migrator <migration> <entrypoint...>` with subcommands: `module` (converts `@import` to `@use`/`@forward`, handles namespacing and `with` overrides), `division` (converts `/`-as-division to `math.div()`, with a `--pessimistic` mode), `color` (updates legacy color functions to color-space-aware equivalents), and an `if()`-function migration (converts the old SassScript `if()` behavior). Common flags: `--migrate-deps` (also migrate dependencies), `--dry-run`, `--verbose`.

### Built-in module functions
[Source: https://sass-lang.com/documentation/modules/] Seven built-in modules, each loaded via `@use "sass:<name>"`: `sass:math` (numeric functions), `sass:string` (string combine/search/split), `sass:color` (generate/transform colors, e.g. theming), `sass:list` (access/modify list values), `sass:map` (key/value lookups and manipulation), `sass:selector` ("Sass's powerful selector engine" exposed programmatically), `sass:meta` ("exposes the details of Sass's inner workings" — introspection, e.g. `get-function()`, `call()`, `feature-exists()`, type-checking).

## 4. Configuration

[Source: https://sass-lang.com/documentation/at-rules/use/] Module-level configuration: a module declares configurable variables with `!default`; consumers override them at load time with `@use 'library' with ($variable: value, ...)`. Configuration only applies on a module's *first* load in a compilation — every subsequent `@use`/`@import` of that module reuses the already-configured instance, so config values are effectively global-once-set per compilation.

[Source: https://sass-lang.com/documentation/at-rules/use/] Namespacing configuration: `@use "src/corners"` defaults to namespace `corners` (last URL segment); `@use "src/corners" as c` renames it; `@use "src/corners" as *` loads members unnamespaced (docs caution to use this "cautiously" due to collision risk). Private members are prefixed with `-` or `_` and are excluded from a module's public API.

[Source: https://sass-lang.com/documentation/js-api/] Compiler configuration is primarily done through JS API `Options`/`StringOptions` objects (output style, source maps, importers, custom functions) or, for the CLI, through command-line flags — Not documented: a dedicated project-level config file (e.g. no `.sassrc`) in the official docs; configuration is code- or flag-driven, not file-driven, per what was retrieved.

[Source: https://sass-lang.com/documentation/cli/dart-sass/] Deprecation-warning verbosity is configurable via `--quiet-deps` (suppress warnings from dependencies), `--verbose` (show all deprecation warnings, not just the first of each type), and `--silence-deprecation` (suppress specific named deprecations) — noted specifically in the context of `@import` deprecation warnings.

## 5. Recommended patterns

[Source: https://sass-lang.com/documentation/at-rules/use/] Use `@use`/`@forward` (the module system) rather than `@import` for all new code — this is Dart Sass's own current recommendation, since `@use` scopes members to the importing file (avoiding global-namespace pollution), loads each file only once (avoiding duplicate CSS output and redundant recompilation), and requires namespacing member access (`namespace.$var`, `namespace.mixin()`), which the docs frame as solving the naming-collision and unclear-dependency problems inherent to `@import`.

[Source: https://sass-lang.com/documentation/at-rules/use/] Use `!default` + `with (...)` configuration for building themeable libraries rather than ad hoc variable overrides.

[Source: https://sass-lang.com/documentation/modules/] Prefer built-in `sass:*` modules (e.g. `sass:math` functions like `math.div()`) over legacy global functions/operators (e.g. `/` for division) since many legacy globals are deprecated in favor of namespaced module functions (see Breaking changes).

[Source: https://sass-lang.com/documentation/cli/dart-sass/] Use `--watch` during development and `--style=compressed` for production output, per the CLI's documented style options.

[Source: https://sass-lang.com/dart-sass/] Prefer the `sass` or `sass-embedded` npm packages (Dart Sass) over LibSass/Node Sass-based tooling, since Dart Sass is the actively developed reference implementation that receives new features first.

## 6. Anti-patterns

[Source: https://sass-lang.com/documentation/at-rules/use/] Relying on `@import` for new code is effectively documented as an anti-pattern going forward: the docs describe `@import`'s problems as manual namespacing burden, global-scope pollution, and repeated re-compilation of the same file, all of which motivated the module system. `@import` itself is deprecated (see Breaking changes) and only Dart Sass still supports it during the deprecation window.

[Source: https://sass-lang.com/documentation/at-rules/use/] Overusing `@use "..." as *` (unnamespaced/wildcard loading) is called out as something to use "cautiously," implying it is discouraged as a general pattern due to name-collision risk.

[Source: https://sass-lang.com/documentation/js-api/] Choosing the async JS API (`compileAsync`/`compileStringAsync`) purely for speed is an anti-pattern per the docs' own framing — "the asynchronous variants are much slower" — async should only be chosen when async importers/functions are actually needed.

[Source: https://sass-lang.com/blog/libsass-is-deprecated/] Continuing to build new tooling on LibSass/Node Sass is discouraged: the Sass team states there is "not enough engineering bandwidth behind LibSass to keep it up-to-date with the latest developments in the Sass language" and that shared libraries "cannot adopt the modern module system" while depending on LibSass.

## 7. Security

[Source: https://sass-lang.com/blog/security-alert-tar-permissions/] The one officially documented Sass security incident: standalone `.tar.gz` release archives (Dart Sass, Dart Sass Embedded, Sass Migrator) and the `sass-embedded` npm package (before 1.54.5) / RubyGems non-native package (before 1.56.2) shipped with incorrect Unix file permissions (757/654 instead of 755/644) due to a decimal-to-octal conversion bug in the `cli_pkg` release tool. Impact: "executable files could be overwritten by all users, not just the owner," enabling privilege escalation by any local low-privileged user against a root-owned install extracted from the affected archive. Fix: `cli_pkg` 2.1.7 plus republished, corrected `.tar.gz` archives; users in the affected install paths were told to delete and reinstall Sass. Users who installed via the npm `sass` package, Homebrew, or Chocolatey were stated to be unaffected.

[Source: https://sass-lang.com/blog/libsass-is-deprecated/] LibSass and Node Sass are stated to be maintained only "on a best-effort basis, including fixing major bugs and security issues" post-deprecation (as of the 2020 announcement) — implying reduced security-patch assurance for those implementations relative to Dart Sass. Node Sass has since reached end-of-life entirely (see Version information).

Not documented / could not verify: a dedicated general "security considerations" or "threat model" page (e.g. guidance on evaluating untrusted Sass input, custom-function/importer sandboxing, or supply-chain guidance) was not found on sass-lang.com in the pages retrieved. [Inference, not confirmed in docs] Because Sass compiles user-supplied stylesheets to CSS and supports `@error`/custom JS functions/importers that can execute arbitrary host code, compiling untrusted Sass source with untrusted custom functions/importers should be treated as executing untrusted code — but this specific guidance is not stated in the official docs retrieved and is flagged here only as an inference.

## 8. Performance

[Source: https://sass-lang.com/dart-sass/] Dart Sass leverages the Dart VM, described as providing "a substantial performance boost even for JavaScript" via the compiled-to-JS `sass` package, and greater performance still via `sass-embedded`, which runs a native Dart VM subprocess through the Embedded Sass protocol.

[Source: https://sass-lang.com/documentation/js-api/] Synchronous compilation (`compile`/`compileString`) is documented as faster than asynchronous (`compileAsync`/`compileStringAsync`); async exists specifically to support async custom importers/functions, at a real speed cost ("much slower").

[Source: https://sass-lang.com/blog/announcing-dart-sass/] [Inference, historical/version-specific claim as summarized via search, not independently re-fetched in full] At Dart Sass's original announcement, early benchmarks reportedly showed it ~5–10x faster than Ruby Sass and ~1.5x slower than LibSass for large stylesheets — a point-in-time comparison, not a current-version guarantee.

[Source: https://sass-lang.com/blog/node-fibers-discontinued/] [Summarized via search result, not independently re-fetched] The asynchronous legacy `render()` in Dart Sass is noted to be "2-3x slower than renderSync()" — reinforcing the general sync-vs-async performance tradeoff documented across the JS API pages.

[Source: https://sass-lang.com/documentation/at-rules/use/] The module system's load-once-per-file semantics is itself a documented performance property: `@use`/`@forward` avoid the redundant recompilation that repeated `@import`s of the same file could cause.

## 9. Testing

Not documented / could not verify: the official Sass documentation (as crawled) does not present a dedicated "Testing" section or an officially maintained testing framework for Sass stylesheets. The `sass:meta` module (introspection: `feature-exists()`, `get-function()`, `call()`, type predicates) is the closest documented building block that could underpin test authoring, but the docs describe it as an inner-workings/introspection module, not a test framework. [Inference, not confirmed in docs] Community tools (e.g. the `true` package) exist for Sass unit testing but are not part of sass-lang.com's official documentation and are out of scope for this citation-only survey.

## 10. Deployment

[Source: https://sass-lang.com/install/] Documented installation/distribution channels: `npm install -g sass` (or as a project devDependency) for the pure-JS implementation; standalone platform executables (ZIP for Windows, `.tar.gz` for Mac/Linux) from GitHub releases, added to `PATH`; Homebrew (`brew install sass/sass/sass`) on Mac/Linux; Chocolatey (`choco install sass`) on Windows; the `sass-embedded` npm package (faster, Windows/Mac/Linux only) as an alternative to `sass`.

[Source: https://sass-lang.com/install/] Community-maintained wrappers/build integrations mentioned: Ruby, Swift, and Java bindings, including Gradle and Maven plugins; desktop GUI compilers CodeKit (Mac, paid) and Prepros (Mac/Windows/Linux, paid).

[Source: https://sass-lang.com/install/] The install page is explicitly installation-focused rather than a deployment/production-rollout guide; it directs users to "go and play" and consult learning resources afterward — no dedicated CI/CD or production-deployment guidance section was found on sass-lang.com in the pages retrieved. Not documented / could not verify beyond what's summarized above.

## 11. Migration

### From `@import` to the module system
[Source: https://sass-lang.com/documentation/breaking-changes/import/] `@import` began emitting deprecation warnings starting in Dart Sass 1.80.0 [VERSION-SENSITIVE]. The deprecation period runs "until Dart Sass 3.0.0, which will not release sooner than two years after version 1.80.0"; eventually `@import` rules will be treated as plain-CSS `@import` only. The `sass-migrator module [--migrate-deps]` command automates conversion to `@use`/`@forward`; a `--built-in-only` flag exists to migrate only built-in function calls.

### From LibSass / Node Sass to Dart Sass
[Source: https://sass-lang.com/blog/libsass-is-deprecated/] Officially recommended migration path (announced 2020-10-26): move to Dart Sass, since LibSass/Node Sass will not receive new language features (LibSass's last new feature was added November 2018 per that post) and cannot support the module system.
[Source: https://sass-lang.com/blog/node-sass-is-end-of-life/] Node Sass reached end-of-life as of 2024-07-24: "The npm package has been marked as deprecated, and the GitHub repository has been archived." Official recommendation: "migrate to the primary implementation, Dart Sass, instead."

### Division operator migration
[Source: https://sass-lang.com/documentation/cli/migrator/] `sass-migrator division` converts legacy `/`-as-division usage to `math.div()`, with a `--pessimistic` flag to convert only operations verifiably known to be division (this pairs with the `/`-division deprecation tracked on the breaking-changes page).

### Color API migration
[Source: https://sass-lang.com/documentation/cli/migrator/] `sass-migrator color` updates legacy global color functions to their color-space-aware, module-based equivalents (relevant to the 1.79.0 "Color functions"/"Color API deprecations" breaking changes, see below).

## 12. Version information

[Source: https://sass-lang.com/documentation/] The documentation's reference target as of this research date is **Dart Sass 1.104.0**.
[Source: https://github.com/sass/dart-sass/releases] Recent Dart Sass release history (all dates as published on GitHub releases): 1.104.0 (2026-09-03), 1.103.1 (2026-08-20), 1.103.0 (2026-08-20), 1.102.0 (2026-07-25), 1.101.7 (2026-07-23). [VERSION-SENSITIVE: current as of 2026-09-09; Sass ships frequent patch/minor releases, roughly every 1–4 weeks based on this sample, so treat "latest" as a moving target.]

[Source: https://sass-lang.com/dart-sass/] Dart Sass is explicitly the "primary implementation" and reference implementation of the Sass language — it receives new language features first.

[Source: https://sass-lang.com/blog/libsass-is-deprecated/] LibSass and Ruby Sass are both deprecated implementations (announced 2020-10-26); [Source: search-summarized, sass-lang.com content, not independently re-fetched in full] LibSass has had no repository commits since December 2023 and is reported to have reached end-of-life around October 2025 — Unresolved: the exact LibSass EOL date/announcement was surfaced only via a search-engine summary of sass-lang.com content and was not independently re-fetched and quoted from the primary page in this session, so treat the October 2025 date as unconfirmed pending direct verification.

[Source: https://sass-lang.com/blog/node-sass-is-end-of-life/] Node Sass (the LibSass Node.js wrapper) reached end-of-life 2024-07-24; npm package deprecated, GitHub repo archived.

Not documented / could not verify: Sass does not appear to publish a formal "LTS" support-window policy comparable to e.g. Node.js LTS — the docs describe deprecation *periods* for specific features (tied to future major-version removals) rather than a blanket support calendar for old Dart Sass minor/major versions themselves.

## 13. Breaking changes

[Source: https://sass-lang.com/documentation/breaking-changes/] The official Breaking Changes index lists 25+ dated entries. Most recent entries retrieved (version = first version to deprecate/warn, per Dart Sass release numbering) [ALL VERSION-SENSITIVE]:
- **Adjacent compound selectors** — Dart Sass 1.100.0
- **Additional plain CSS function names** — Dart Sass 1.98.0
- **Legacy `if()` function** — Dart Sass 1.95.0
- **Private variables in `with`** — Dart Sass 1.92.0
- **Misplaced rest arguments** — Dart Sass 1.91.0
- **`type()` function** — Dart Sass 1.86.0
- **`@import`** — Dart Sass 1.80.0 (see Migration section)
- **Legacy JS API** — Dart Sass 1.79.0
- **Color API deprecations** — Dart Sass 1.79.0
- **Color functions** — Dart Sass 1.79.0
- **`meta.feature-exists()` function** — Dart Sass 1.78.0
- **Mixed declarations with nested rules** — Dart Sass 1.77.7
- **Functions/Mixins beginning with `--`** — Dart Sass 1.76.0
- **`abs()` with percentage units** — Dart Sass 1.65.0
- **`null` alpha channel in `SassColor()`** — Dart Sass 1.64.3
- **Default export loading in JS** — Dart Sass 1.63.0
- **Duplicate variable flags** — Dart Sass 1.62.0
(Older entries from 1.0.0–1.55.0 covering selectors, operators, and CSS custom-property syntax are also listed on the page but were not individually re-fetched in this session.)

[Source: https://github.com/sass/dart-sass/releases] Recent point-release behavioral changes: **1.104.0** — "Colors now convert the special values NaN and negative zero, as well as infinity and negative infinity for polar-hue channels, to 0 as per the CSS spec," and negative zero now serializes as `-0` in calculation contexts. **1.103.0** — color-space conversions now "preserve 'analogous sets' of missing channels during conversions, per the CSS spec," changing output for some conversions that previously zero-filled missing channels. **1.101.0** — fixed how the Node package importer resolves import-only file variants, which the release notes flag as a potential behavior break for code relying on the old resolution order.

[Source: https://sass-lang.com/documentation/breaking-changes/import/] `@import` deprecation warnings began in 1.80.0; full removal (treating `@import` as plain CSS only) is targeted for Dart Sass 3.0.0, "which will not release sooner than two years after version 1.80.0" [VERSION-SENSITIVE, forward-looking commitment, not yet in effect as of 1.104.0].

## 14. Limitations

[Source: https://sass-lang.com/documentation/at-rules/use/] `@use` rules must appear before any other rules in a stylesheet (aside from `@forward`) — i.e., module loading is position-constrained at the top of a file, unlike the more flexible (nestable) placement historically allowed for `@import`.

[Source: https://sass-lang.com/documentation/at-rules/use/] Module configuration (`with (...)`) only applies the first time a module is loaded in a given compilation; a module cannot be reconfigured differently by two different loaders within the same compile, which the docs frame as a constraint to design around (e.g. via a single central "config" entrypoint) rather than a bug.

[Source: https://sass-lang.com/documentation/at-rules/use/] Only Dart Sass currently supports `@use`/`@forward` — this is a documented cross-implementation limitation (though LibSass/Ruby Sass are now deprecated/EOL, so this is largely moot going forward).

Not documented / could not verify: explicit numeric limits (e.g. maximum recursion depth for `@function`/`@mixin`, maximum nesting depth, maximum selector length) were not found in the pages retrieved in this session.

## 15. Debugging

[Source: https://sass-lang.com/documentation/at-rules/] `@debug` — "prints a message for debugging purposes" during compilation. `@warn` — "prints a warning without stopping compilation entirely," intended for surfacing non-fatal issues (e.g. deprecated mixin usage) to stylesheet consumers. `@error` — "causes compilation to fail with an error message," used for asserting invalid input/state.

[Source: https://sass-lang.com/documentation/cli/dart-sass/] CLI debugging/diagnostic aids: `--interactive`/`-i` starts a SassScript REPL for testing expressions; `--error-css` emits CSS that visually surfaces the compile error in-browser rather than just failing the build; `--verbose` shows all deprecation warnings (not just first-occurrence-per-type); `--quiet`/`-q` suppresses warnings when they're not wanted.

[Source: https://sass-lang.com/documentation/cli/dart-sass/] Source maps: `--source-map-urls` (`relative`/`absolute`), `--embed-source-map`, `--embed-sources`, and `--no-source-map` control generation of debugging source maps that map compiled CSS back to original Sass source — the primary documented mechanism for debugging compiled output in browser devtools.

[Source: https://sass-lang.com/documentation/modules/] `sass:meta`'s introspection functions (e.g. `feature-exists()`, type-checking, `inspect()`-style utilities implied by "exposes the details of Sass's inner workings") support debugging library/mixin behavior at compile time.

## 16. Integration

[Source: https://sass-lang.com/dart-sass/] Dart Sass documents multiple integration surfaces: a Dart library (pub.dev, for Dart/Flutter tooling), npm packages (`sass`, `sass-embedded`) for JavaScript/Node.js tooling, and the language-agnostic **Embedded Sass protocol**, with wrapper packages for Go, Java, Ruby, Rust, and .NET enabling integration from those ecosystems' own build pipelines.

[Source: https://sass-lang.com/install/] Documented ecosystem integrations: Gradle and Maven plugins (Java/JVM build tools), Homebrew/Chocolatey system package managers, and GUI compilers (CodeKit, Prepros).

[Source: https://sass-lang.com/documentation/js-api/] JS API custom importers (including `NodePackageImporter`) are the documented integration point for resolving Sass partials from npm-installed packages (`pkg:` scheme), which is how bundler integrations (e.g. build-tool loaders) are expected to resolve Sass files from `node_modules`.

Not documented / could not verify: sass-lang.com does not appear to officially document specific third-party bundler plugins (e.g. webpack's `sass-loader`, Vite's built-in Sass preprocessing) in the pages retrieved — those integrations are maintained and documented by the respective bundler projects, not by the Sass team, so they are out of scope for "official docs" citation here.

## 17. Production considerations

[Source: https://sass-lang.com/documentation/cli/dart-sass/] Use `--style=compressed` to minify output CSS for production builds (vs. the human-readable `expanded` default).

[Source: https://sass-lang.com/blog/security-alert-tar-permissions/] For standalone-archive installs specifically, verify install integrity/permissions post-extraction given the documented historical tar-permissions incident, or prefer npm/Homebrew/Chocolatey installs, which the Sass team stated were unaffected by that specific issue.

[Source: https://sass-lang.com/dart-sass/] For performance-sensitive production builds under Node.js, prefer `sass-embedded` over the pure-JS `sass` package where the target OS/architecture is supported, since it wraps the faster native Dart VM via the Embedded Sass protocol.

[Source: https://sass-lang.com/documentation/breaking-changes/import/] Because `@import` is in an active, multi-year deprecation window (warnings since 1.80.0, removal not before roughly two years after that, targeted for Dart Sass 3.0.0), production codebases still using `@import` should plan a migration (via `sass-migrator module`) before that removal lands, and can use `--quiet-deps`/`--silence-deprecation` in the interim to manage warning noise from third-party dependencies without silencing warnings from first-party code.

[Source: https://sass-lang.com/blog/node-sass-is-end-of-life/] Production systems still depending on Node Sass should migrate to Dart Sass, since Node Sass's npm package is deprecated and its repository archived (no further security or bug fixes expected).
