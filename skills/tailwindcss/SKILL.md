---
name: Tailwind CSS
description: >-
  Tailwind CSS utility-first styling: v4's CSS-first @theme config, Oxide
  engine, content detection, arbitrary-value/variant syntax, and the
  v3-vs-v4 browser-floor/migration decision. Use when the stack has a
  tailwind.config.js, "@import \"tailwindcss\"", a Tailwind dependency, or
  utility-class markup, or the task names Tailwind/@theme/utility-first CSS.
  Not for generic styling-system architecture (styling-systems), Sass syntax
  with no Tailwind involved (sass), or shadcn/ui mechanics (shadcn-ui).
spec_version: "1.0"
---

## Purpose & scope

Apply Tailwind CSS correctly for the version in use — utility-class
composition, v4's CSS-first `@theme` configuration and Oxide engine, content
detection, and the v3→v4 migration/browser-floor decision. The *method* for
architecting a project's broader styling system (design tokens, theming
strategy, whether a utility framework is warranted at all) comes from the
parent skill (`SK-FE-003` styling-systems, not yet authored in this
library); this skill supplies Tailwind's concrete facts on top of that
method.

## When to use / When not to use

**Use** when a `tailwind.config.js`/`.ts`, an `@import "tailwindcss";` CSS
entry, or a `@tailwindcss/vite`/`postcss`/`cli` dependency is present, or the
task names Tailwind, utility-first CSS, or a Tailwind-specific mechanism
(`@theme`, `@utility`, `@custom-variant`, the Oxide engine, content
detection). **Do not use** for generic styling-system architecture with no
framework chosen yet (route to `SK-FE-003` styling-systems), Sass-specific
syntax/module-system work with no Tailwind involved (route to
`SK-TECH-sass`), or shadcn/ui component/registry mechanics beyond Tailwind's
own utilities (route to `SK-TECH-shadcn-ui`).

**Tailwind and Sass are not mutually exclusive as project-level choices** —
a codebase can consult both skills (e.g. Sass owns one legacy area while
Tailwind is adopted elsewhere, or a migration is in flight between them).
What *is* real and narrow: **Tailwind v4 itself does not support using Sass
(or Less/Stylus) as a preprocessing step alongside it** — Tailwind's own
toolchain (via Lightning CSS) now performs the imports/nesting/variables/math
jobs those preprocessors used to do
[Source: https://tailwindcss.com/docs/compatibility;
research/knowledge-maps/technology-decision-matrix.md §9]. Treat this as a
specific "don't run Sass as a build step feeding into Tailwind v4" fact, not
a broad philosophical incompatibility between the two technologies — which is
why this skill does not declare `SK-TECH-sass` a `conflicts_with` entry.

## Knowledge

**Utility-first model.** Tailwind styles elements by composing many
single-purpose utility classes (`flex`, `pt-4`, `text-center`) directly in
markup rather than custom CSS classes; each utility styles one concern and
only applies when its condition (a `hover:`/`lg:` variant) is met
[Source: https://tailwindcss.com/docs/styling-with-utility-classes]. Variants
stack by prefixing — state, responsive breakpoints, dark mode, and
structural selectors (`group-hover:`, `data-*:`, `aria-*:`) can all combine
on one class [Source: https://tailwindcss.com/docs/styling-with-utility-classes].

**Zero-runtime, ahead-of-time generation.** Tailwind is not a runtime
CSS-in-JS framework: it scans source files as plain text for
class-name-shaped tokens, generates CSS only for classes actually matched,
and ships a single static stylesheet with no client-side runtime cost
[Source: https://tailwindcss.com/docs/detecting-classes-in-source-files;
https://tailwindcss.com/docs/installation/using-vite].

**v4 architecture — the Rust "Oxide" engine.** v4.0 shipped a ground-up
engine rewrite (community/press name "Oxide," largely Rust), leaning on
native modern CSS rather than reimplementing preprocessor behavior in JS:
**cascade layers** (`@layer`), registered custom properties via `@property`
(enabling animatable gradients and CSS-native inherited defaults), and
`color-mix()` for opacity/alpha composition
[Source: https://tailwindcss.com/blog/tailwindcss-v4]. **[VERSION-SENSITIVE,
applies_to >=4.0]** This is exactly why v4.0 raises the browser floor to
**Safari 16.4+, Chrome 111+, Firefox 128+** — teams needing older-browser
support must stay on **v3.4**
[Source: https://tailwindcss.com/docs/upgrade-guide;
research/knowledge-maps/version-matrix.md]. This is a hard compatibility
gate, not a soft recommendation.

**CSS theme variables (`@theme`).** v4 centers configuration on the
`@theme` CSS block instead of a JS config object: every design token
(`--color-*`, `--font-*`, `--spacing-*`, etc.) is a real CSS custom property
emitted onto `:root`, and utilities are generated dynamically from whichever
theme namespaces/variables exist
[Source: https://tailwindcss.com/docs/theme]. `@theme inline` bakes in a
referenced variable's value directly (for tokens that must react to a
`:root`/`[data-theme]` switch, e.g. dark-mode colors); `--*: initial;` clears
the entire default theme for a fully custom design system
[Source: https://tailwindcss.com/docs/theme].

**Content detection.** v4 scans the project heuristically at build time
(`.gitignore`-aware, auto-excluding `node_modules`/binaries/lockfiles)
instead of requiring a `content: []` glob array; `@source` registers extra
paths or disables auto-detection
[Source: https://tailwindcss.com/docs/detecting-classes-in-source-files].
This scanner is a **static-text heuristic, not a real parser** — it cannot
resolve runtime string interpolation (see Anti-patterns).

**Arbitrary values and variables — breaking syntax change.**
**[VERSION-SENSITIVE, applies_to: v3.x bracket form vs. >=4.0 parenthesis
form]** v3's `bg-[--brand-color]` (bracket syntax for referencing an
existing CSS custom property) was replaced in v4 by `bg-(--brand-color)`
(parenthesis syntax) [Source: https://tailwindcss.com/docs/theme;
https://tailwindcss.com/docs/upgrade-guide]. Square-bracket syntax remains
for one-off literal values (`bg-[#316ff6]`)
[Source: https://tailwindcss.com/docs/styling-with-utility-classes].

**`@custom-variant` / `@variant` split.** `@variant name { ... }` applies an
existing variant conditionally inside custom CSS; `@custom-variant name
(...)` defines a new one (e.g. redefining `dark` to key off a class instead
of `prefers-color-scheme`). This split has been stable since v4.0;
`@custom-variant` is the renamed form of an earlier `@variant`-for-definition
syntax used briefly in pre-stable v4 betas
[Source: https://github.com/tailwindlabs/tailwindcss/blob/main/CHANGELOG.md
(4.0.0-beta.10)].

**Legacy-JS-config bridge is partial.** `@config "path/to/tailwind.config.js";`
and `@plugin "name";` let a v4 project load a v3-style JS config/plugin for
incremental migration — but **`corePlugins`, `safelist`, and `separator`
options are not supported** through this bridge in v4.0
[Source: https://tailwindcss.com/docs/functions-and-directives;
research/knowledge-maps/version-matrix.md]. **Unresolved:** whether later
4.x patches (current stable is 4.3.3) expanded this support was not
confirmed in the underlying research — say "verify against current docs"
rather than assert either way.

**Default color palettes are not stable across the v4 line.**
**[VERSION-SENSITIVE, applies_to: >=4.2.0]** v4.2.0 (2026-02-18) added four
new default color palettes — **mauve, olive, mist, taupe** — that do not
exist in any earlier v4.x release or in v3.x
[Source: https://tailwindcss.com/blog/tailwindcss-v4-3;
research/knowledge-maps/version-matrix.md]. Code or snapshots referencing
these palettes will fail on an earlier v4.x install or any v3.x project —
check the installed version before using them.

> Deep material (the full documented v3→v4 breaking-change table) lives in
> [`references/v3-to-v4-breaking-changes.md`](references/v3-to-v4-breaking-changes.md)
> — loaded only when needed (context-efficiency rule CE-3).

## Decision framework

1. **v3.4 vs. v4, given the browser floor (real trade-off, not a default):**
   v4 brings the Oxide engine's throughput and the CSS-first `@theme` model,
   but hard-requires Safari 16.4+/Chrome 111+/Firefox 128+
   [Source: https://tailwindcss.com/docs/upgrade-guide]. If the project's
   actual analytics/support matrix includes browsers below that floor,
   **v3.4 is the correct choice**, not a "just upgrade" default — the
   official guide itself sanctions staying on v3.4 for this reason. If the
   floor is unknown, ask before assuming v4 (see Failure handling).
2. **Utility-first-in-markup vs. component-library-with-Tailwind-underneath:**
   composing utilities directly in markup is Tailwind's own preferred
   pattern for one-off/product-specific UI
   [Source: https://tailwindcss.com/docs/styling-with-utility-classes]. When
   a project needs a broad, pre-built, accessible component set (dialogs,
   comboboxes, data tables) rather than hand-composing every primitive, a
   Tailwind-based component library such as `SK-TECH-shadcn-ui` is the
   documented alternative — it copies Tailwind-styled source into the
   project rather than adding a separate styling engine. Neither is a
   universal default: a small marketing site rarely needs a component
   library; a design-system-heavy app rarely wants to hand-roll every
   primitive from scratch.
3. **Simplest first (anti-overengineering):** for a handful of static pages
   with no design-system ambition, plain CSS/no framework at all can be the
   right call — Tailwind's own duplication-management guidance ranks
   template loops and multi-cursor editing *above* reaching for any
   component/utility abstraction
   [Source: https://tailwindcss.com/docs/styling-with-utility-classes].
   Don't introduce Tailwind (or any styling framework) as a default before
   confirming the project's styling surface actually justifies it.
4. **Custom CSS escape hatch:** when duplication does need addressing beyond
   markup-level tricks, the documented priority order is template loops →
   multi-cursor editing → framework component/template-partial extraction →
   `@layer components` only as a last resort for genuinely reusable,
   multi-property patterns
   [Source: https://tailwindcss.com/docs/adding-custom-styles].

## Workflow

1. Determine the installed/target Tailwind major-minor version and the
   project's browser support matrix before writing any version-sensitive
   guidance.
2. Choose the install path matching the build tool: `@tailwindcss/vite`
   (tightest integration for Vite-based tooling), `@tailwindcss/postcss`
   (PostCSS-centric pipelines, e.g. Next.js/Angular), or the standalone
   `@tailwindcss/cli` (no Node.js required, prebuilt native binaries)
   [Source: https://tailwindcss.com/docs/installation/using-vite;
   https://tailwindcss.com/docs/installation/using-postcss;
   https://tailwindcss.com/docs/installation/tailwind-cli].
3. For v4, configure tokens in an `@theme` block (extend, override, or reset
   namespaces as needed) rather than a JS config object
   [Source: https://tailwindcss.com/docs/theme].
4. Compose utility classes directly in markup; extract a framework
   component/template partial once duplication crosses file boundaries,
   reserving `@layer components` for genuinely complex, reusable patterns
   [Source: https://tailwindcss.com/docs/adding-custom-styles].
5. For a v3→v4 migration, run `npx @tailwindcss/upgrade` (Node.js 20+) on a
   fresh branch and review every diff before merging
   [Source: https://tailwindcss.com/docs/upgrade-guide]; consult
   [references/v3-to-v4-breaking-changes.md](references/v3-to-v4-breaking-changes.md)
   for the full rename/syntax table.
6. Verify (below) before declaring done.

## Engineering rules

- Never dynamically construct a Tailwind class-name string (e.g.
  `` `bg-${color}-600` ``) — the content scanner cannot resolve runtime
  interpolation and will silently omit the class in production; use a
  static lookup map instead
  [Source: https://tailwindcss.com/docs/detecting-classes-in-source-files].
- State the Tailwind major version any guidance targets; never assume
  "latest" behavior implicitly (v3.4 and v4.x are both live and differ in
  config model and arbitrary-value syntax).
- Before recommending v4.2.0+ color palettes (mauve/olive/mist/taupe),
  confirm the installed version is actually >=4.2.0.
- Prefer utility composition and framework-component extraction over
  `@layer components` for anything short of a genuinely complex, reusable
  pattern [Source: https://tailwindcss.com/docs/adding-custom-styles].
- Never ship the Play CDN (`cdn.tailwindcss.com`) in a production build —
  it is dev-only by explicit documentation (see Security/Performance)
  [Source: https://tailwindcss.com/docs/installation/play-cdn].
- Before a v3→v4 migration, run the official codemod on a branch and review
  every diff — do not hand-translate the full breaking-change surface from
  memory [Source: https://tailwindcss.com/docs/upgrade-guide].

## Trade-offs

- Utility-first markup avoids inventing class names and keeps changes
  localized, but visually verbose markup is the direct cost — teams used to
  semantic class names need an adjustment period
  [Source: https://tailwindcss.com/docs/styling-with-utility-classes].
- v4's Oxide engine and CSS-first `@theme` model are faster and simpler to
  reason about, but the raised browser floor (Safari 16.4+/Chrome
  111+/Firefox 128+) is a real, non-negotiable cost for products with an
  older-browser audience — v3.4 remains the correct choice there
  [Source: https://tailwindcss.com/docs/upgrade-guide].
- A Tailwind-based component library (shadcn/ui) trades some setup
  uniformity and "it just looks right by default" for the copy-in
  supply-chain model's own maintenance burden (patches must be manually
  re-pulled per project) — see `SK-TECH-shadcn-ui` for that specific
  trade-off; not restated here.

## Anti-patterns

- **Dynamically constructing class-name strings** (`` `text-${size}` ``) —
  documented as *broken*, not just discouraged: the static scanner cannot
  detect it, so the utility silently never generates
  [Source: https://tailwindcss.com/docs/detecting-classes-in-source-files].
- **Referencing v4.2.0+ color palettes (mauve, olive, mist, taupe) in code
  or snapshots meant to also run on an earlier v4.x install or any v3.x
  project** — a concrete, version-specific breakage, not a hypothetical one
  [Source: research/knowledge-maps/version-matrix.md;
  https://tailwindcss.com/blog/tailwindcss-v4-3].
- **Habitually reaching for `@layer components`/custom CSS classes** for
  things composable from utilities directly — an outdated instinct the docs
  explicitly redirect away from
  [Source: https://tailwindcss.com/docs/adding-custom-styles].
- **Writing conflicting utilities on one element** (e.g. `class="grid
  flex"`) and assuming source order in the `class` string decides the
  winner — generated-stylesheet cascade-layer order decides it instead, not
  attribute-write order
  [Source: https://tailwindcss.com/docs/styling-with-utility-classes].
- **Relying on v3's implicit border/ring defaults** (`gray-200` border,
  3px `blue-500` ring) after migrating to v4, where the implicit default is
  `currentColor`/1px — renders silently wrong until colors are made
  explicit [Source: https://tailwindcss.com/docs/upgrade-guide].
- **Combining Tailwind with CSS Modules or Sass/Less/Stylus as the primary
  styling mechanism in v4** — discouraged/unsupported respectively; see
  When to use / When not to use and Security for the precise scope of the
  Sass incompatibility [Source: https://tailwindcss.com/docs/compatibility].

## Security

The one Tailwind-documented security-adjacent guidance concerns the **Play
CDN**: it is flagged unsuitable for production, but for stated **performance**
reasons (large JS payload vs. a compiled CSS file; runtime style application
causing flash-of-unstyled-content) — the docs stop short of calling it a
security risk [Source: https://tailwindcss.com/docs/installation/play-cdn].
Keep that distinction precise: this is a performance-driven production-fitness
rule, not a documented vulnerability.

Because the content-detection scanner requires complete, static class-name
strings to exist verbatim in source and refuses to synthesize classes from
interpolated input, untrusted runtime data concatenated into a `class`
attribute cannot cause Tailwind to *generate new CSS* at build time — a
structural side-effect of the scanner, not a claim the docs make in security
terms [Source: https://tailwindcss.com/docs/detecting-classes-in-source-files;
Inference, not confirmed in docs as a security property]. For the full
threat model (injection, secrets, transport, CSP), defer to `SK-QA-002` —
Tailwind's official docs do not publish a dedicated CSP/XSS guide, so nothing
Tailwind-specific is owned here beyond the two notes above.

## Performance

v4's rewritten engine reports specific throughput numbers versus v3: full
builds up to **~3.78–5x faster**, incremental builds adding new CSS up to
**~8.8x faster**, and no-new-CSS incremental rebuilds up to **~182x faster**
(microseconds vs. milliseconds)
[Source: https://tailwindcss.com/blog/tailwindcss-v4]. **Flag these as
vendor-reported**: they are Tailwind Labs' own v4.0-vs-v3 announcement
benchmarks, not independently reproduced, and not necessarily representative
of intra-v4 patch-to-patch deltas.

The zero-runtime, ahead-of-time model is itself a performance property —
only CSS for classes actually used ships, with no client-side style
computation at runtime outside the dev-only Play CDN mode
[Source: https://tailwindcss.com/docs/styling-with-utility-classes]. Avoid
combining Tailwind with CSS Modules specifically: the docs note Tailwind then
runs per-module, slowing builds versus a single global stylesheet pass
[Source: https://tailwindcss.com/docs/compatibility]. Deeper cross-cutting
performance method is owned by `SK-QA-003`.

## Testing

**Documented gap:** Tailwind's official docs contain no dedicated
first-party testing guide — no `/docs/testing` page exists, matching its
nature as a build-time CSS-generation tool with no component *behavior* to
unit-test [Source: research/technologies/tailwind.md §9, "Not documented /
could not verify"]. The closest first-party QA tooling is **editor-time
linting** via the official IntelliSense extension, which flags
invalid/unrecognized utility usage as you type, not an automated test suite
[Source: https://tailwindcss.com/docs/editor-setup]. Application-level
verification of Tailwind's output belongs to the consuming framework's own
testing approach (visual regression, snapshot, or end-to-end browser
testing); deep test-strategy method is owned by `SK-QA-001`.

## Failure handling

- If the target browser support matrix is unknown, ask for it or explicitly
  state that v4's floor is assumed — never silently assume v4 support for
  an unstated audience.
- If the installed Tailwind major/minor version cannot be determined, ask
  or state the assumed version, since syntax (arbitrary-value bracket vs.
  parenthesis) and available palettes differ across the live v3.4/v4.x
  lines.
- If shell/build execution is unavailable, degrade to advisory class/config
  edits and state that the codemod or a real build was not run.

## Escalation

- A v3→v4 upgrade touching a shared/production config requires explicit
  user confirmation before running the codemod — it rewrites config and
  template files project-wide, and the official guide itself recommends
  reviewing every diff before merging.
- Removing/bypassing an existing Sass (or Less/Stylus) preprocessing step to
  adopt Tailwind v4 requires explicit user confirmation, since this is a
  real (if narrow) incompatibility, not a purely mechanical change.

## Outputs & verification

- **Outputs:** version-correct utility-class markup, `@theme`/config
  changes, a reviewed v3→v4 migration, or an analysis (version choice,
  utility-first-vs-component-library, browser-floor) with rationale and the
  version it applies to.
- **Verify:** every version-specific claim is tagged with its range; a
  migration was run via the official codemod with diffs reviewed, not
  hand-guessed; no class-name string is dynamically constructed; v4.2.0+
  palettes are not referenced unless the installed version is confirmed
  >=4.2.0.

## References

- [`references/v3-to-v4-breaking-changes.md`](references/v3-to-v4-breaking-changes.md)
  — Tier-2: the full documented v3→v4 rename/syntax/config-bridge table.
- Source list: see `skill.yaml.source_references` (Tailwind CSS official
  docs/blog, the `tailwindlabs/tailwindcss` CHANGELOG, and npm registry
  metadata, retrieved 2026-09-10, via `research/technologies/tailwind.md`,
  `research/knowledge-maps/version-matrix.md`, and
  `research/knowledge-maps/technology-decision-matrix.md`).

**Unresolved (carried from research, do not paper over):**
- Whether the `@config`/`@plugin` legacy bridge's `corePlugins`/`safelist`/
  `separator` gap has been closed in any 4.x patch after 4.0.0 (current
  stable 4.3.3) was not confirmed — verify against current docs before
  treating it as fixed or still-broken.
- Whether Tailwind Labs has a *formally documented* v3-LTS end-of-life date
  (versus an informal, ongoing best-effort backport pattern evidenced by the
  `v3-lts` npm dist-tag and a 2025-12-10 patch) was not confirmed from an
  official statement.
- Whether `@tailwindcss/postcss` still requires a separately configured
  `autoprefixer` plugin in any edge case was not independently re-verified
  against a raw fetch of the PostCSS install page.
