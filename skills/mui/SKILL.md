---
name: MUI (Material UI)
description: >-
  MUI (Material UI) component library — Emotion-based CSS-in-JS via the sx
  prop, theming (createTheme()/ThemeProvider/CSS-variables mode), and RSC/App
  Router integration (AppRouterCacheProvider). Use when @mui/material,
  @mui/icons-material, or @emotion/react+styled appear, or the task names MUI
  or Material UI. Not for shadcn/ui (route to that skill), generic
  styling-system choice (styling-systems), or UI/UX design judgment
  independent of a library (ui-ux-design).
spec_version: "1.0"
---

## Purpose & scope

Apply MUI (Material UI) correctly for the version actually installed —
Emotion-based CSS-in-JS theming, the `sx` prop, `styled()`, CSS-variables
theming, and RSC/App Router integration. The general styling-system method
(design tokens, theming architecture, dark-mode strategy as a discipline)
belongs to `styling-systems` (`SK-FE-003`); general UI/UX
design judgment belongs to `ui-ux-design` (`SK-FE-002`).
This skill supplies what's MUI-specific: the `sx` prop and `styled()` API,
`createTheme()`/`ThemeProvider`, the Emotion styling engine and its CSP
requirements, and the security-patch-line policy that makes "which major
version is installed" a load-bearing question for this library.

## When to use / When not to use

**Use** when `@mui/material`, `@mui/icons-material`, `@mui/material-nextjs`,
or `@mui/system` appear in the codebase, or the task names MUI/Material UI
specifically. **Do not use** when the project uses shadcn/ui, Chakra UI, Ant
Design, or another component library instead (route to that library's
skill — MUI and `shadcn/ui` are alternatives for the same UI layer, not
composable choices for the same component), for a generic styling-system or
design-token decision with no library chosen yet (`styling-systems`), or for
UI/UX design judgment independent of a specific library (`ui-ux-design`).

## Knowledge

**Theming is centered on `createTheme()`/`ThemeProvider`.** A theme object —
covering `palette`, `typography`, `spacing`, `breakpoints`, `components`
(per-component default props/style overrides/variants), `zIndex`, and
`transitions` — is created via `createTheme()` and distributed through the
tree by a React-Context-based `ThemeProvider`; `useTheme()` reads it back
inside custom components [Source:
https://mui.com/material-ui/customization/theming/]. The default palette
ships six semantic intents (`primary`/`secondary`/`error`/`warning`/`info`/
`success`), each with `main`/`light`/`dark`/`contrastText`; missing tokens
are auto-derived from `main` via `augmentColor` [Source:
https://mui.com/material-ui/customization/theming/].

**The `sx` prop is MUI's signature one-off styling API** — Emotion-based
CSS-in-JS written directly on component props, including responsive
breakpoint syntax, avoiding a separate stylesheet for one-off styling
[Source: https://mui.com/material-ui/]. Components are self-contained and
inject only the styles they need [Source: https://mui.com/material-ui/].
Emotion (`@emotion/react` + `@emotion/styled`) is the default, recommended
styling engine; `styled-components` is a documented alternative via
`@mui/styled-engine-sc`, but the docs explicitly warn it "is not compatible
with server-rendered Material UI projects" due to Babel plugin limitations —
Emotion is required for SSR [Source:
https://mui.com/material-ui/getting-started/installation/].

**CSS-variables theming is the opt-in runtime-switching mode.**
`cssVariables: true` (paired with `colorSchemes: { light: true, dark: true }`)
generates CSS custom properties (e.g. `--mui-palette-primary-main`), enabling
color-scheme switching without a React re-render of the theme subtree
[Source: https://mui.com/material-ui/customization/theming/]. This mode was
introduced **opt-in/experimental in v5** and became a more central, refined
part of the theming story through v6–v9 [Version-sensitive: opt-in from v5,
refined v6–v9] [Source: https://mui.com/material-ui/customization/theming/].
With it enabled, the *theme object itself* stops varying between modes at the
JS level — components read `theme.vars.*` instead — so code that inspects
`theme.palette.mode` at runtime for conditional logic needs to be adapted
[Source: https://mui.com/material-ui/customization/theming/,
https://mui.com/material-ui/migration/upgrade-to-v7/].

**RSC/App Router support shipped in v5.14.0.** Every MUI, Base UI, Joy UI,
and MUI System component ships with `"use client"` — MUI components are
inherently Client Components and cannot render as React Server Components
[Source: https://mui.com/material-ui/integrations/nextjs/]. [Version-sensitive:
>=5.14.0] [Source: https://mui.com/blog/mui-next-js-app-router/]. For the
Next.js App Router, wrap `app/layout.tsx` in `AppRouterCacheProvider` (from
`@mui/material-nextjs`) so Emotion-generated CSS streams into `<head>` and
avoids a flash of unstyled content; the Pages Router needs the older
`AppCacheProvider` + `@emotion/server` pattern instead [Source:
https://mui.com/material-ui/integrations/nextjs/].

Full v7 and v9 breaking-change detail (codemods, removed APIs,
`slots`/`slotProps` migration) is in
[`references/migration-v7-v9-breaking-changes.md`](references/migration-v7-v9-breaking-changes.md) —
loaded only when a migration task needs it (context-efficiency rule CE-3).

## Decision framework

1. **Simplest first (anti-overengineering):** if the app is small, has no
   real theming/design-system need, or the team is already committed to
   utility-first CSS, plain CSS/CSS Modules or a lighter utility layer
   (Tailwind) may cover the need without adopting a full component library at
   all — don't reach for MUI (or any component library) by default.
2. **MUI vs. shadcn/ui — structurally different models, not a quality
   ranking.** No source states a direct security or performance ranking
   between them; the difference is architectural [Source:
   research/knowledge-maps/technology-decision-matrix.md §8]:
   - **Distribution:** MUI is an installed npm dependency
     (`@mui/material`) that upgrades via `npm update`; shadcn/ui copies
     component source directly into the project via its CLI — not a
     dependency at all [Source:
     research/knowledge-maps/technology-decision-matrix.md §8].
   - **Styling engine / CSP:** MUI's Emotion CSS-in-JS requires CSP nonce
     plumbing (see Security below); shadcn/ui has no CSS-in-JS runtime to
     nonce [Source: https://mui.com/material-ui/guides/content-security-policy/;
     research/knowledge-maps/technology-decision-matrix.md §8].
   - **Patch propagation:** MUI's installed-dependency model means a
     security fix reaches the app via a routine version bump; shadcn/ui's
     copied-source model means a security fix upstream in its registry does
     **not** automatically propagate to a project that already copied the
     component — that project must reapply the fix itself [Source:
     research/knowledge-maps/technology-decision-matrix.md §8]. Choose MUI
     when centralized upstream patching matters more than full code
     ownership; choose shadcn/ui when full control/no black-box dependency
     matters more than automatic patch propagation.
   - **Prerequisite:** shadcn/ui needs Tailwind CSS already in place; MUI
     does not.
3. **Customization scope: `sx` vs. `styled()` vs. theme `components` vs.
   `GlobalStyles`.** MUI documents these narrowest-to-broadest, in order
   [Source: https://mui.com/material-ui/customization/how-to-customize/]:
   - `sx` prop — one-off instance styling only. Cheap for small property
     counts; avoid for highly dynamic, ever-changing values (see
     Performance).
   - `styled()` — a reusable, theme-aware custom component used in more than
     one place.
   - Theme `components` key (`styleOverrides`/`variants`) — app-wide,
     consistent styling of a component everywhere it appears.
   - `GlobalStyles` — baseline HTML-element styling; hoist to a static
     constant to avoid recalculation on every render.
   Do not reach for the theme `components` key or `GlobalStyles` for a
   one-off tweak, and do not reach for repeated inline `sx` overrides where a
   `styled()` component or a theme override would remove the duplication.
4. **CSS-variables theming mode: adopt when runtime mode-switching
   performance matters** (e.g. frequent light/dark toggling in a
   performance-sensitive UI) or when SSR consistency benefits from
   CSS-native switching; skip it for a simple app with one fixed theme where
   the added `theme.vars.*` indirection isn't worth it.

## Engineering rules

- Confirm the installed `@mui/material` major version before writing or
  trusting any version-sensitive API (`Grid` vs. `GridLegacy`,
  `slots`/`slotProps` vs. `components`/`componentsProps`) — see Knowledge and
  [`references/migration-v7-v9-breaking-changes.md`](references/migration-v7-v9-breaking-changes.md).
- Use path (deep) imports, not named/barrel imports, especially for icons:
  `import Delete from '@mui/icons-material/Delete'`, not
  `import { Delete } from '@mui/icons-material'` — enforce with an ESLint
  `no-restricted-imports` rule [Source:
  https://mui.com/material-ui/guides/minimizing-bundle-size/]. Skip this
  discipline only when the project is on Next.js >=13.5, whose
  `optimizePackageImports` auto-applies the equivalent optimization
  [Version-sensitive: Next.js >=13.5] [Source:
  https://mui.com/material-ui/guides/minimizing-bundle-size/].
- Never apply styles directly to a bare global state class name (e.g.
  `.Mui-selected { }`); always combine it with a component-scoped class to
  avoid unintended cross-component side effects [Source:
  https://mui.com/material-ui/getting-started/faq/].
- Prefer CSS-based styling (`sx`/`styled`) over raw inline `style` props for
  dynamic values — CSS gives auto-prefixing, media-query support, and
  keyframe support that inline styles lack [Source:
  https://mui.com/material-ui/getting-started/faq/].
- Pin `react-is` to the installed React major via package-manager overrides
  on any React <=18 project — MUI's own code depends on `react-is@19`
  [Version-sensitive: React 17.0.0+/18.0.0+ peer support] [Source:
  https://mui.com/material-ui/migration/upgrade-to-v7/].
- Wrap Next.js App Router apps in `AppRouterCacheProvider`; wrap Pages Router
  apps in `AppCacheProvider` — omitting either causes a flash of unstyled
  content [Source: https://mui.com/material-ui/integrations/nextjs/].

## Trade-offs

MUI's Emotion-based CSS-in-JS gives runtime theming flexibility (dynamic
`sx` values, CSS-variables mode switching without a re-render) at the cost of
CSP configuration overhead that a copy-source, non-CSS-in-JS library like
shadcn/ui doesn't have. Being an installed npm dependency means routine
`npm update`-driven patching, but also means the app inherits whatever v7/v9
breaking-change surface the library ships — a project on the unpatched v6.x
line trades API stability for a real, current security exposure (see
Security).

## Anti-patterns

- **Named/barrel imports from `@mui/icons-material`** — up to **6x slower**
  dev-server startup/rebuild vs. path imports, because the barrel re-exports
  a very large number of modules [Source:
  https://mui.com/material-ui/guides/minimizing-bundle-size/]. This is the
  domain's over-engineering-adjacent trap: it costs nothing in production
  (modern bundlers tree-shake), so treat it as a dev-workflow discipline, not
  a bundle-size emergency (see Performance).
- **Calling a style/theme hook outside `<ThemeProvider>`** — causes runtime
  errors reading theme properties that don't exist on an empty theme
  [Source: https://mui.com/material-ui/migration/troubleshooting/].
- **Multiple instances of the styling library/class-name generator in one
  bundle** (mixed dependency versions) — causes theme-propagation bugs and
  class-name collisions; fix via dependency deduplication (`npm ls`, bundler
  aliasing) [Source: https://mui.com/material-ui/migration/troubleshooting/].
- **Passing a React ref where a DOM node is required** — `Portal`/`Popper`
  need an actual DOM node, not a ref object [Source:
  https://mui.com/material-ui/getting-started/faq/].
- **Using `React.Fragment` as the child of `Fade`/`Grow`/`Slide`/`Zoom`** —
  these transition components need a ref-forwarding real DOM-node child
  [Source: https://mui.com/material-ui/getting-started/faq/].
- **Treating v9's vendor-reported perf numbers as an independent benchmark**
  when deciding whether to upgrade — see Performance.

## Security

**CSP nonce requirements are a real, precise production deployment gotcha.**
Emotion injects `<style>` tags, requiring a `style-src-elem 'nonce-<base64>'`
directive matched to a per-request nonce passed through Emotion's
`CacheProvider`. Some components additionally use inline style *attributes*
for dynamic values (positioning, CSS custom properties), which requires
`style-src-attr 'unsafe-inline'` as well — the docs explicitly caveat that
this directive "doesn't create a vulnerability" by itself but "reduces
defense layers" if markup injection exists elsewhere, i.e. it is not a
substitute for output sanitization. `InitColorSchemeScript` (used for the
CSS-variables/dark-mode setup) needs a `script-src 'nonce-<base64>'` because
it renders an inline `<script>` [Source:
https://mui.com/material-ui/guides/content-security-policy/]. Strict-CSP
deployments cannot fully avoid `style-src-attr 'unsafe-inline'` under current
MUI internals [Source: https://mui.com/material-ui/guides/content-security-policy/] —
plan CSP headers accordingly rather than assuming a nonce-only policy works
unmodified, and surface the `'unsafe-inline'` acceptance to the user (see
Escalation).

**Only v9.x (current) and v7.x (LTS) receive security patches.** Version
6.x and earlier are **not** receiving security patches under this policy
[Version-sensitive: state as of the v9 release cycle; will shift as new
majors ship] [Source:
https://github.com/mui/material-ui/blob/master/SECURITY.md]. This is a real,
current risk: any project pinned to v6.x or earlier is running an unpatched
line, not merely an outdated-but-safe one — flag it explicitly rather than
treating "which major to upgrade to" as a purely stylistic question.

**MUI's installed-dependency model vs. shadcn/ui's copy-source model
changes how a patch reaches production** — see the Decision framework above
[Source: research/knowledge-maps/technology-decision-matrix.md §8]. Beyond
CSP and the patch-line policy, no dedicated MUI documentation on XSS or
supply-chain security was found; report vulnerabilities to
`security@mui.com` per MUI's SECURITY.md rather than a public GitHub issue
[Source: https://github.com/mui/material-ui/blob/master/SECURITY.md]. Deeper
cross-cutting threat modeling (injection, secrets, transport) is owned by
`SK-QA-002`, not restated here.

## Performance

**Barrel-import slowdown is a dev-time concern, not a production bundle-size
problem.** The docs frame path-vs-barrel imports primarily as a
development-server startup/rebuild-speed issue, explicitly noting "modern
bundlers already tree-shake unused code in production builds" [Source:
https://mui.com/material-ui/guides/minimizing-bundle-size/] — don't
overstate this as a production bundle bloat risk; it's a dev-workflow cost
(see Anti-patterns for the 6x figure).

**The `sx` prop carries runtime CSS-in-JS overhead** that scales with the
number of CSS properties passed — negligible for small property counts
(<5). For highly dynamic values changing on every render, use inline CSS
custom properties instead of passing an ever-changing object to `sx`, to
avoid inserting new `<style>` tags on every render [Source:
https://mui.com/material-ui/customization/theming/ via mui.com/system's `sx`
prop documentation].

**v9's performance claims are vendor-reported, not independently
reproduced.** MUI's own blog states v9 achieves "a roughly 3% bundle size
reduction compared to v7" and "30% performance gains for heavy `sx` prop
usage" [Version-sensitive: v9-vs-v7 comparative figures, MUI blog, not
independently verified in the underlying research] [Source:
https://mui.com/blog/introducing-material-ui-v9/] — cite these as MUI's own
claim when relevant, not as an independently confirmed benchmark.

CSS-variables theming (`cssVariables: true`) is itself a runtime performance
feature: switching color scheme becomes a CSS custom-property swap rather
than a React re-render of the theme subtree [Source:
https://mui.com/material-ui/customization/theming/]. `AppRouterCacheProvider`
exists specifically to avoid FOUC by streaming Emotion-generated CSS into
`<head>` server-side [Source: https://mui.com/material-ui/integrations/nextjs/].
Deeper cross-cutting performance method is owned by `SK-QA-003`.

## Testing

**Official guidance is unusually specific: test the application, not MUI
internals.** "It's generally recommended to test your application without
tying the tests too closely to Material UI" [Source:
https://mui.com/material-ui/guides/testing/]. `@testing-library/react` is
explicitly recommended, praised for querying by role/semantics (`input`,
`[role="textbox"]`) rather than by MUI-specific component or class names,
making tests robust to internal MUI changes [Source:
https://mui.com/material-ui/guides/testing/]. **Snapshot testing is
explicitly discouraged**, citing the argument that snapshot tests "might be
misleading for React component tests" [Source:
https://mui.com/material-ui/guides/testing/] — do not default to snapshot
tests for MUI-based components even though it's a common React pattern
elsewhere. Cross-cutting test strategy is owned by `SK-QA-001`.

## Failure handling

- If the installed `@mui/material` major version can't be determined, ask
  for it or explicitly state the version the guidance assumes — never
  silently assume "v9/latest," since v6-and-earlier carries an unpatched-
  security-line risk and the API surface differs materially (VA-3).
- If shell is unavailable (this skill's execution tier is A), produce
  advisory component/theme/config code and state plainly that no dev-server
  or build was run to verify an import-speed or bundle-size claim.
- If the project is pinned to v6.x or earlier, state the unpatched-line risk
  explicitly rather than proceeding as if the version were a routine
  stylistic choice.

## Escalation

- Continuing development on, or newly adopting, an unpatched v6-or-earlier
  `@mui/material` line for a production app requires explicit user
  acknowledgment before proceeding.
- Accepting `style-src-attr 'unsafe-inline'` in a strict-CSP production
  deployment should be surfaced to the user for explicit sign-off, not
  silently included in generated CSP configuration.

## Outputs & verification

- **Outputs:** version-correct component/theme code, `sx`/`styled()`/theme-
  override customization, CSS-variables theming setup, SSR/RSC integration
  config, CSP directive configuration, or an analysis/decision (version-line
  determination, MUI-vs-shadcn/ui, or a customization-scope choice).
- **Verify:** every version-sensitive API used matches the confirmed
  installed major version; any CSP output includes the `style-src-elem`
  nonce and notes `style-src-attr 'unsafe-inline'`/`InitColorSchemeScript`
  nonce needs where applicable; any patch-line/browser-floor/peer-dependency
  claim is tagged with the version range it holds for.

## References

- [`references/migration-v7-v9-breaking-changes.md`](references/migration-v7-v9-breaking-changes.md) —
  Tier-2: full v6→v7 and v7→v9 breaking-change lists and codemods.
- Source list: see `skill.yaml.source_references` (mui.com official docs,
  the `mui/material-ui` GitHub SECURITY.md, and npm registry, retrieved
  2026-09-10, via `research/technologies/mui.md`).
- [research/knowledge-maps/technology-decision-matrix.md §8](../../research/knowledge-maps/technology-decision-matrix.md) —
  the MUI-vs-shadcn/ui structural comparison (distribution model, CSP,
  patch policy, bundle-size lever, testing guidance) referenced, not
  restated, in Decision framework and Security above.
