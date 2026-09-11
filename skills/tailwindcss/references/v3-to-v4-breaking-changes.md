# Tailwind CSS v3 → v4 breaking-change catalogue (Tier-2)

Loaded on demand from [`SKILL.md`](../SKILL.md). Source for every row:
[Source: https://tailwindcss.com/docs/upgrade-guide] unless a row states
otherwise. All items apply to the v3.4 → v4.0+ major-version boundary.
Run the official codemod (`npx @tailwindcss/upgrade`, requires Node.js 20+)
on a fresh branch and review every diff — it is documented as automating
most of this, not guaranteeing correctness unreviewed.

| Area | v3 | v4 |
|---|---|---|
| Browser support floor | No `@property`/`color-mix()` dependency | Requires Safari 16.4+, Chrome 111+, Firefox 128+; stay on v3.4 if you need older browsers |
| CSS import | `@tailwind base; @tailwind components; @tailwind utilities;` | Single `@import "tailwindcss";` |
| PostCSS plugin package | `tailwindcss` used directly as the PostCSS plugin | Separate `@tailwindcss/postcss` package |
| Config file | `tailwind.config.js`, auto-detected | Not auto-detected — must be explicitly loaded via `@config "path";`; `resolveConfig()` JS helper removed entirely (use `getComputedStyle()` to read theme values from JS) |
| Opacity utilities | `bg-opacity-*`, `text-opacity-*`, `border-opacity-*` | Removed — use the `/opacity` modifier, e.g. `bg-black/50` |
| Flex utilities | `flex-shrink-*`, `flex-grow-*` | `shrink-*`, `grow-*` |
| Text overflow | `overflow-ellipsis` | `text-ellipsis` |
| Box decoration | `decoration-slice` | `box-decoration-slice` |
| Shadow/blur/rounded scale | `shadow-sm`, `shadow`, ... | Scale shifted one step: `shadow-xs`, `shadow-sm`, ...; same shift applied to `blur-*`, `rounded-*`, `drop-shadow-*`/`backdrop-blur-*` |
| Outline | Bare `outline` = `outline-style: solid`; `focus:outline-none` | Bare `outline` removed (numeric utilities imply style directly); `focus:outline-hidden` (preserves visibility in forced-colors mode) |
| Ring default | Bare `ring` = 3px `blue-500` | Bare `ring` = 1px `currentColor`; use `ring-3 ring-blue-500` to restore the old look |
| `space-x-*`/`space-y-*`/`divide-*` selector | `:not([hidden]) ~ :not([hidden])` | `:not(:last-child)` (performance-motivated; not identical in all DOM structures) |
| Default border/ring color | `gray-200` border, `blue-500` ring | `currentColor` for both — markup relying on the old implicit default renders differently unless colors are made explicit |
| `!important` modifier | Leading `!flex` | Trailing `flex!` |
| Custom utility authoring | `@layer utilities { .tab-4 { ... } }` | Dedicated `@utility tab-4 { ... }` at-rule |
| `*` child-variant stacking order | `first:*:pt-0` | `*:first:pt-0` |
| Arbitrary CSS-variable value | `bg-[--brand-color]` | `bg-(--brand-color)` |
| Comma-containing arbitrary values | `grid-cols-[max-content,auto]` | `grid-cols-[max-content_auto]` (underscore for space, to disambiguate from Tailwind's own comma grammar) |
| `hover:` variant | Applies unconditionally | Gated by `@media (hover: hover)` by default (avoids sticky-hover on touch); restore old behavior via `@custom-variant hover (&:hover);` |
| Transform utilities | Required base `transform` class; e.g. `focus:transform-none` | `rotate-*`/`scale-*`/`translate-*` are independent; reset via e.g. `focus:scale-none` |
| Preflight base styles | Hardcoded `gray-400` placeholder color; button `cursor: pointer`; `<dialog>` unreset margins | 50%-opacity `currentColor`-style placeholder text; button `cursor: default`; `<dialog>` margins reset; `hidden` attribute now takes CSS priority over conflicting `display` utilities |
| `@apply` in scoped `<style>`/CSS Modules | Implicit global theme visibility | Requires explicit `@reference "path";` import, or use plain `var(--color-red-500)` |
| Preprocessor support | Sass/Less/Stylus commonly layered alongside Tailwind | Explicitly **not supported** for use alongside Tailwind — Tailwind + Lightning CSS handles imports, nesting, variables, `min()`/`max()`/`round()` math natively [Source: https://tailwindcss.com/docs/compatibility; research/knowledge-maps/technology-decision-matrix.md §9] |
| Gradient stop preservation | `from-*`/`via-*`/`to-*` needed full re-specification per variant | Gradient stops preserved across variants |
| Gradient utility name | `bg-gradient-*` | `bg-linear-*` (part of the expanded linear/radial/conic gradient API) [Inference, not confirmed as an explicit "breaking changes" bullet in the upgrade guide — flagged lower-confidence per research/technologies/tailwind.md §13; verify against current docs before relying on it] |

## Config-file migration specifics

[Source: https://tailwindcss.com/docs/functions-and-directives] The JS-config
compatibility bridge (`@config "../../tailwind.config.js";`) lets a v4
project keep loading a legacy v3 config incrementally, and `@plugin "name";`
loads a legacy JS plugin (e.g. `@tailwindcss/typography`) — but `corePlugins`,
`safelist`, and `separator` options are **not supported** through this
bridge in v4.0. **Unresolved:** whether later 4.x patches (up to the current
4.3.3) expanded this support was not confirmed in the fetched docs
[Source: research/technologies/tailwind.md §4, §14]. Do not assert either
way — say "verify against current docs" if this gap is load-bearing for a
migration plan.

## Node/tooling requirement

[Source: https://tailwindcss.com/docs/upgrade-guide] `npx @tailwindcss/upgrade`
requires **Node.js 20+**. It automates dependency updates, config-file
migration (JS config → CSS `@theme`, where mechanically translatable), and
template-file class-name updates for the renames above — but the guide
itself recommends running it on a fresh branch and reviewing every diff
rather than trusting it as fully automatic.
