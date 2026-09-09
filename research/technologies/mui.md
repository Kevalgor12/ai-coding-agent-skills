# MUI (Material UI)

Deep reference research on **Material UI** (the `@mui/material` package, part of
the broader **MUI** organization/ecosystem), the open-source React component
library implementing Google's Material Design. Primary source is the official
documentation site **mui.com/material-ui**, supplemented by the official
`mui/material-ui` GitHub repository (CHANGELOG.md, SECURITY.md), the official
MUI blog (`mui.com/blog`), and the npm registry (the official distribution
channel for the `@mui/material` package). Research date: **2026-09-09**.

## 0. Canonical docs host and how to read this document

[Source: https://mui.com/material-ui/] The canonical, current documentation
host for Material UI is **https://mui.com/material-ui/**. This is distinct
from the sibling docs sections `mui.com/base-ui/` (headless components),
`mui.com/joy-ui/` (an alternative, non-Material-Design styled library), and
`mui.com/x/` (MUI X — advanced/commercial components such as Data Grid, Date
and Time Pickers, Charts). No canonical-host migration was found for Material
UI itself during this research; older major versions remain archived at
version-prefixed subdomains (e.g. `v6.mui.com`, `v4.mui.com`, `v3.mui.com`,
`v1.mui.com`), a pattern visible in search results throughout this research
(`v6.mui.com`, `v7.mui.com` were both observed as live archives during
research).

[Source: https://registry.npmjs.org (npm dist-tags for the `@mui/material`
package, queried 2026-09-09)] The npm registry reports `latest: 9.4.0`
(published 2026-08-27) and `next: 9.0.0-beta.1`. This document is based
primarily on the **v9 docs** (the current major version as of the research
date — see §12) but draws on v7 migration/troubleshooting docs where the v9
docs point back to them, since v7 is documented as an actively supported
long-term-support line (§12).

[Inference, not confirmed in docs] Because MUI's docs site serves the
*current* major version at the root domain and rewrites in place (similar to
many docs sites), some content fetched via search-engine caches or AI
summarization tools during this research may reflect slightly different
wording than what a live browser render shows; where a claim could not be
corroborated by a second independent fetch, this is noted inline.

---

## 1. Core concepts

[Source: https://mui.com/material-ui/] Material UI is described as "an
open-source React component library that implements Google's Material
Design," providing production-ready components — the docs cite **40+**
(overview page) to **50+** (blog ecosystem post) foundational building blocks
such as Button, TextField, Table, Alert, and Tooltip.

[Source: https://mui.com/material-ui/] Components are **self-contained** and
"will only inject the styles they need to display" — i.e., styling is
co-located with the component and applied on demand rather than as one large
global stylesheet.

[Source: https://mui.com/material-ui/customization/theming/] **Theming** is
central: a `ThemeProvider` (React Context-based) distributes a theme object —
created via `createTheme()` — down the component tree. The theme covers
**palette**, **typography**, **spacing**, **breakpoints**, **components**
(default props/style overrides/variants per component), **z-index**, and
**transitions**.

[Source: https://mui.com/material-ui/customization/palette/] The default
**palette** ships six semantic color intents — `primary`, `secondary`,
`error`, `warning`, `info`, `success` — each with `main`, `light`, `dark`,
and `contrastText` tokens; missing tokens are auto-derived from `main` via
the `augmentColor` utility, using a configurable `contrastThreshold` (default
3, i.e. WCAG AA-ish; can be raised to 4.5 for stricter WCAG AA text contrast)
and `tonalOffset` (default 0.2).

[Source: https://mui.com/material-ui/] The **`sx` prop** is described as the
library's signature one-off styling API: an "elegant" way to write
theme-aware CSS (including responsive breakpoints) directly on component
props, avoiding "context switching" between JS and separate stylesheets.

[Source: https://mui.com/material-ui/customization/theming/] **CSS
variables**: setting `cssVariables: true` in the theme configuration
generates CSS custom properties (e.g. `--mui-palette-primary-main`),
enabling runtime theme switching (e.g., dark mode) without React
re-renders. [Version-sensitive] This CSS-variables theming model was
introduced as an opt-in/experimental feature in Material UI v5 and
became a more central, refined part of the theming story by v6–v9 (see
§13 for the v9 `color-mix()` refinement).

[Source: https://mui.com/blog/mui-product-comparison/] Ecosystem
positioning: **Base UI** is the headless/unstyled foundation layer; **Material
UI** and **Joy UI** are styled component libraries built on top of that
foundation (Material UI implements Material Design; Joy UI is "an
alternative to Material UI for designs that don't adhere to Material Design
specifications"); **MUI System** is a cross-cutting CSS-utilities layer
(the `sx` prop mechanism) usable with any of the styled libraries; **MUI X**
is a separate, more advanced/commercial component layer (Data Grid,
Date/Time Pickers, Charts, etc.) documented at `mui.com/x`. [Source:
https://mui.com/blog/mui-product-comparison/] The blog post also notes
"future versions [of] Material UI will also be built with Base UI as the
foundation" — [Inference, not confirmed in docs] implying Material UI's
internal implementation is migrating toward the Base UI primitive layer over
time, though the docs fetched did not specify a target version for this.

---

## 2. Architecture

[Source: https://mui.com/blog/mui-product-comparison/] Material UI's
architecture is layered: **Base UI** (headless behavior/accessibility
primitives) → **Material UI** (Material-Design-styled components built on
that foundation) → **MUI System** (cross-cutting styling utilities / `sx`
prop, usable independent of which styled component library sits on top).
MUI X is a parallel, separate package family for advanced/data-heavy
components, not a dependency of Material UI itself.

[Source: https://mui.com/material-ui/getting-started/installation/] The
**styling engine** is pluggable: **Emotion** is the default (installed via
`@emotion/react` + `@emotion/styled` alongside `@mui/material`), and
**styled-components** is a documented alternative (via the
`@mui/styled-engine-sc` adapter package). [Source:
https://mui.com/material-ui/getting-started/installation/] The docs
explicitly warn that "styled-components is not compatible with
server-rendered Material UI projects" due to Babel plugin limitations —
Emotion is the recommended/default choice, especially for SSR apps.

[Source: https://mui.com/material-ui/integrations/interoperability/] Under
the hood, Material UI's CSS-in-JS output can coexist with other styling
approaches (plain CSS, CSS Modules, Tailwind CSS, styled-components,
Emotion, JSS-successor `tss-react`) via `StyledEngineProvider` (controls CSS
injection order) and custom Emotion cache configuration.

[Source: https://mui.com/material-ui/api/button/] Each component ships with
a documented API surface: **props**, **CSS classes** (global state classes
like `.Mui-disabled`, `.Mui-selected`, and component-scoped classes like
`.MuiButton-root`), and (for composite components) **slots**/**slotProps**
for overriding internal sub-elements — this "slot" architecture is the
mechanism by which Material UI exposes internal DOM structure for
customization without needing to fork components.

[Source: https://mui.com/material-ui/integrations/nextjs/] For frameworks
using React Server Components (Next.js App Router), all Material UI, Base
UI, Joy UI, and MUI System components ship with the `"use client"` directive
— i.e., **Material UI components are inherently Client Components** and
cannot be rendered as React Server Components. [Source:
https://mui.com/blog/mui-next-js-app-router/] This App-Router compatibility
was introduced with **Material UI v5.14.0** [version-sensitive].

---

## 3. APIs

[Source: https://mui.com/material-ui/api/button/] The component API
reference pages (one per component, e.g. `/material-ui/api/button/`) are
structured as: **Demos** (links to usage examples), **Import** (import
statement), **Props** (full prop table with type, default, and description),
**CSS classes** (state/slot class names), and **Source code** (GitHub link).
Representative Button props: `children` (node), `color` (`'inherit' |
'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning' | string`,
default `'primary'`), `variant` (`'contained' | 'outlined' | 'text' |
string`, default `'text'`), `size` (`'small' | 'medium' | 'large' | string`,
default `'medium'`), `disabled` (bool, default `false`), `loading` (bool |
null), `startIcon`/`endIcon` (node).

[Source: https://mui.com/material-ui/customization/how-to-customize/] Theme
default props for a component are set under the theme's `components` key,
namespaced by component name (e.g. `MuiButton.defaultProps` /
`MuiButton.styleOverrides` / `MuiButton.variants`) — this is itself part of
the public theming API surface, not just runtime component props.

[Source: https://mui.com/material-ui/customization/theming/] **`createTheme(options)`**
is the primary theme-construction API, returning a complete `Theme` object
from partial `ThemeOptions`. **`ThemeProvider`** (React context provider)
and **`useTheme()`** (hook for reading the active theme in custom
components) round out the core theming API.

[Source: https://mui.com/material-ui/customization/how-to-customize/] The
**`styled()`** utility (re-exported from `@mui/material/styles`, built on the
configured styling engine) is the API for creating new, theme-aware,
reusable styled components — supports dynamic CSS driven by props and CSS
custom properties for runtime style switching.

[Source: https://mui.com/system/screen-readers/] **`visuallyHidden`**
(importable from `@mui/utils`) is a small accessibility utility: a
`React.CSSProperties` style object that hides content visually while
keeping it available to assistive technology.

[Source: https://mui.com/material-ui/getting-started/faq/] **`clsx`** is
documented as the recommended utility (a Material UI dependency) for
conditionally composing `className` strings.

---

## 4. Configuration

[Source: https://mui.com/material-ui/customization/theming/] Theme
configuration keys include `palette` (see §1), `typography` (font
family/sizes/weights), `spacing` (base unit for margin/padding scale —
`theme.spacing(n)`), `breakpoints` (responsive thresholds, default keys
`xs`/`sm`/`md`/`lg`/`xl`), `components` (per-component `defaultProps`,
`styleOverrides`, `variants`), `zIndex`, and `transitions`.
`responsiveFontSizes()` is a helper that accepts a `breakpoints` option
array, defaulting to `['sm', 'md', 'lg']`.

[Source: https://mui.com/material-ui/customization/palette/] `colorSchemes:
{ light: true, dark: true }` is the documented configuration shape for
defining both a light and dark palette simultaneously (paired with the
CSS-variables theming mode from §1).

[Source: https://mui.com/material-ui/customization/palette/] Windows
High-Contrast-mode support can be configured via `enhanceHighContrast()`,
which maps to CSS system color keywords for guaranteed contrast.

[Source: https://mui.com/material-ui/getting-started/installation/]
**TypeScript module augmentation** is the documented mechanism to extend the
`Theme`/`ThemeOptions` types with custom variables — declaring the
augmentation is required for type safety when adding non-default theme
properties (§1, §4).

[Source: https://mui.com/material-ui/getting-started/installation/] Install
configuration: default styling engine via `npm install @mui/material
@emotion/react @emotion/styled`; the alternative styled-components engine via
`npm install @mui/material @mui/styled-engine-sc styled-components`. Fonts
(Roboto, via `@fontsource/roboto` or Google Fonts CDN `<link>` tags) and
icons (`@mui/icons-material`, or Google Fonts CDN) are separate,
opt-in installs. [Source: https://mui.com/material-ui/getting-started/installation/]
A CDN-based install path exists for prototyping but is explicitly "not
recommended" for production due to loading the entire library.

[Source: https://mui.com/material-ui/guides/content-security-policy/] CSP
configuration is a first-class, documented configuration concern: Emotion
injects `<style>` tags requiring a `style-src-elem 'nonce-<base64>'`
directive matched to a per-request nonce passed through Emotion's
`CacheProvider`; some components use inline style *attributes* for dynamic
values, requiring `style-src-attr 'unsafe-inline'`; and `InitColorSchemeScript`
(used for the CSS-variables/dark-mode setup) needs `script-src
'nonce-<base64>'` because it renders an inline `<script>`.

---

## 5. Recommended patterns

[Source: https://mui.com/material-ui/customization/how-to-customize/] MUI
documents four customization approaches, in order of narrowest to broadest
recommended scope: **(1)** the `sx` prop for one-off instance styling
(including nested-selector overrides like `'& .MuiSlider-thumb': {...}` and
state classes like `.Mui-disabled` — the docs explicitly warn "Never apply
styles directly to state class names" in isolation; always combine with a
component class to avoid unintended global side effects); **(2)** the
`styled()` utility for reusable custom components; **(3)** the theme's
`components` key (`styleOverrides` + `variants`) for global, app-wide
consistency; **(4)** `GlobalStyles` for baseline HTML-element styling
(recommended to be hoisted to a static constant to avoid unnecessary style
recalculation on every render).

[Source: https://mui.com/material-ui/guides/testing/] The recommended
testing pattern is to **test applications, not Material UI internals** —
i.e., avoid coupling tests to Material UI's implementation details. Use
`@testing-library/react` and query by semantic role/element (e.g. `input`,
`[role="textbox"]`) rather than by MUI-specific component/class names, which
makes tests more robust to internal MUI changes.

[Source: https://mui.com/material-ui/guides/minimizing-bundle-size/] The
recommended import pattern is **path (deep) imports** rather than
named/barrel imports, especially for icons: `import Button from
'@mui/material/Button'` and `import Delete from
'@mui/icons-material/Delete'`, rather than `import { Button } from
'@mui/material'` / `import { Delete } from '@mui/icons-material'`. The docs
frame this primarily as a **development-time** (dev-server startup/rebuild
speed) concern rather than a production bundle-size concern, since "modern
bundlers already tree-shake unused code in production builds."

[Source: https://mui.com/material-ui/guides/minimizing-bundle-size/]
Enforcement patterns recommended: an ESLint `no-restricted-imports` rule
blocking top-level barrel imports, and a VS Code
`typescript.preferences.autoImportSpecifierExcludeRegexes` setting to stop
editors auto-importing from barrels. [Source:
https://mui.com/material-ui/guides/minimizing-bundle-size/] Next.js 13.5+
automatically applies this optimization via `optimizePackageImports`,
removing the need for manual per-import discipline in that framework.
[Version-sensitive: Next.js ≥13.5.]

[Source: https://mui.com/material-ui/integrations/nextjs/] For Next.js App
Router, the recommended pattern is wrapping the app in
`AppRouterCacheProvider` (from `@mui/material-nextjs`) inside
`app/layout.tsx`, so Emotion-generated CSS is collected and streamed into
`<head>` correctly rather than causing a flash of unstyled content (FOUC).

---

## 6. Anti-patterns

[Source: https://mui.com/material-ui/getting-started/faq/] **Applying styles
directly to global state class names** (e.g. writing a bare `.Mui-selected {
}` rule) is called out as something to avoid — combine state classes with a
component-scoped class to prevent unintended cross-component side effects.

[Source: https://mui.com/material-ui/getting-started/faq/] **Preferring
inline styles over CSS-based styling for dynamic values** is discouraged:
the docs recommend CSS-based approaches (via `sx`/`styled`) over raw inline
`style` props because CSS gives auto-prefixing, easier debugging, media
query support, and keyframe animation support that inline styles lack.

[Source: https://mui.com/material-ui/getting-started/faq/] **Passing a ref
where a DOM node is required** — components like `Portal` and `Popper`
specifically need an actual DOM node argument (not a React ref object) for
correct timing/re-render behavior; passing a ref object where a node is
expected is a documented gotcha.

[Source: https://mui.com/material-ui/migration/troubleshooting/] **Multiple
instances of the styling library/class-name generator in one bundle**
(historically a JSS-era v4 issue, still relevant when mixing dependency
versions) causes theme-propagation bugs, class name collisions, and CSS
specificity bugs — the fix is deduplication (`npm ls`, webpack aliasing) to
guarantee a single instance.

[Source: https://mui.com/material-ui/migration/troubleshooting/] **Calling
style/theme hooks outside of `<ThemeProvider>`** (e.g. a `makeStyles`-family
hook called in a component rendered outside the provider tree) causes
runtime errors like "Cannot read property 'drawer'" because the hook reads
theme properties that don't exist on the default/empty theme.

[Source: https://mui.com/material-ui/guides/minimizing-bundle-size/]
**Named/barrel imports from `@mui/icons-material`** are called out
explicitly as a severe anti-pattern for dev performance — "up to six times
slower" dev startup/rebuild vs. path imports, because the icons package
barrel re-exports a very large number of modules.

[Source: https://mui.com/material-ui/getting-started/faq/] Using
`React.Fragment` (rather than a real DOM node) as the child of transition
components (`Fade`, `Grow`, `Slide`, `Zoom`) is a documented anti-pattern
that causes "Cannot read property scrollTop of null" — these components need
a ref-forwarding DOM-node child.

---

## 7. Security

[Source: https://github.com/mui/material-ui/blob/master/SECURITY.md]
Security vulnerabilities should be reported privately to **security@mui.com**
rather than via public GitHub issues.

[Source: https://github.com/mui/material-ui/blob/master/SECURITY.md] Two
version lines currently receive security patches: **v9.x** (current stable,
released 2026-04-08) and **v7.x** (released 2025-03-26, documented as the
long-term-support line — "support for security issues and regressions").
Versions 6.x and earlier are **not** receiving security patches per this
policy. [Version-sensitive — this support matrix reflects the state as of
the v9 release cycle and will shift as new majors ship.]

[Source: https://mui.com/material-ui/guides/content-security-policy/]
Material UI documents first-class CSP support as a security-adjacent
configuration concern (see §4 for directive details): Emotion-injected
`<style>` elements need a matching `nonce`; some components require
`style-src-attr 'unsafe-inline'` for dynamic inline style *attributes*
(positioning, CSS custom properties); `InitColorSchemeScript` needs a
`script-src` nonce because it renders an inline script. The docs explicitly
caveat that `style-src-attr 'unsafe-inline'` "doesn't create a
vulnerability" by itself but "reduces defense layers" if markup injection
already exists elsewhere in the app — i.e., it is not a substitute for
proper output sanitization.

[Inference, not confirmed in docs] No dedicated Material UI documentation
page on XSS, dependency-vetting, or supply-chain security beyond the
SECURITY.md reporting/patch-support policy and the CSP guide was found
during this research; Material UI's security surface as documented is
narrowly scoped to (a) vulnerability reporting/patch policy and (b) CSP
configuration for its CSS-in-JS injection model.

---

## 8. Performance

[Source: https://mui.com/material-ui/guides/minimizing-bundle-size/] Bundle
size / dev-server performance guidance centers on avoiding barrel imports
(see §5); the docs state modern bundlers tree-shake production builds fine,
so the main documented cost of barrel imports is **development-time**
(startup and rebuild speed), not final bundle size — a nuance worth
preserving rather than treating barrel imports as a production bundle-size
problem across the board.

[Source: https://github.com/mui/material-ui/blob/master/docs/data/system/getting-started/the-sx-prop/the-sx-prop.md
via mui.com/system] The `sx` prop carries **runtime CSS-in-JS overhead**;
official guidance states the overhead scales with the number of CSS
properties passed, is negligible for small property counts (<5), and — for
highly dynamic values that change on every render — recommends using
**inline CSS custom properties** rather than passing an ever-changing object
to `sx`, to avoid inserting new `<style>` tags into the DOM on each render.

[Source: https://mui.com/blog/introducing-material-ui-v9/] Material UI v9
claims measured performance work: "a roughly 3% bundle size reduction
compared to v7" from removing deprecated props/system-prop plumbing, plus
"30% performance gains for heavy `sx` prop usage" and duplicate-CSS-rule
cleanup. [Version-sensitive: these are v9-vs-v7 comparative figures from the
MUI blog, not independently reproduced in this research.]

[Source: https://mui.com/material-ui/customization/theming/] The
CSS-variables theming mode (`cssVariables: true`) is positioned as a runtime
performance feature: switching color scheme (e.g. light/dark) becomes a CSS
custom-property swap rather than a React re-render of the whole theme
subtree.

[Source: https://mui.com/material-ui/integrations/nextjs/] `AppRouterCacheProvider`
exists specifically to avoid a documented performance/UX problem — flash of
unstyled content (FOUC) — by collecting Emotion-generated CSS server-side
during Next.js streaming and injecting it before the client sees unstyled
markup.

---

## 9. Testing

[Source: https://mui.com/material-ui/guides/testing/] Official guidance:
"It's generally recommended to test your application without tying the
tests too closely to Material UI" — i.e., prefer black-box, user-facing
assertions over MUI-implementation-detail assertions.

[Source: https://mui.com/material-ui/guides/testing/] **`@testing-library/react`**
is the explicitly recommended tool, praised for having "a first-class API"
for querying by role/semantics (e.g., `input`, `[role="textbox"]`) rather
than by MUI component or class name — this makes tests more robust against
internal MUI changes (e.g., added wrapper elements/context providers).

[Source: https://mui.com/material-ui/guides/testing/] **Snapshot testing is
explicitly discouraged**, citing Kent C. Dodds' argument that snapshot tests
"might be misleading for React component tests."

[Source: https://mui.com/material-ui/guides/testing/] Internally, the MUI
project itself uses visual regression testing powered by **Argos CI**, with
further detail pointed to in the project's own test README on GitHub (not
independently fetched in this research).

[Inference, not confirmed in docs] Cypress or other end-to-end tools were
not documented on the official testing guide page fetched during this
research (the page centers on Testing Library); any Cypress-specific MUI
guidance, if it exists, was not found via official docs during this
research pass.

---

## 10. Deployment

[Not documented / could not verify as a dedicated section] Material UI has
no standalone "deployment" guide analogous to a framework's — it is a UI
component library consumed inside a host app's own build/deploy pipeline
(Next.js, Vite, CRA-successor tooling, etc.), so deployment concerns are
governed by the *host framework's* deployment docs, not Material UI's.
[Inference, not confirmed in docs] The closest documented deployment-adjacent
concerns are: (a) bundle-size/tree-shaking guidance (§5, §8), (b) SSR setup
(Express + Emotion cache extraction, or Next.js `AppRouterCacheProvider`)
(§16), and (c) the explicit recommendation against CDN-based production
installs (§4) — none of these constitute a full deployment guide.

[Source: https://mui.com/material-ui/guides/server-rendering/] The official
SSR guide documents a three-phase Express-based deployment pattern: (1)
build one shared theme file used by both server and client, (2) an Express
middleware renders the app to an HTML string, extracting critical CSS via
`createEmotionServer` and injecting it into the response `<head>` (to avoid
FOUC), (3) the client hydrates the server-rendered markup. [Source:
https://mui.com/material-ui/guides/server-rendering/] The guide notes this
is specifically an Express + Emotion example and does not cover Next.js App
Router specifics or styled-components SSR compatibility on that page (see
§16 for the dedicated Next.js integration doc, which does cover App Router).

---

## 11. Migration

[Source: https://mui.com/material-ui/migration/upgrade-to-v7/] **v6 → v7**
breaking changes: deep imports beyond one path segment are no longer
supported (e.g. must import `createTheme` from `@mui/material/styles`, not a
deeper subpath); the legacy `Grid` was renamed to `GridLegacy` and the new
`Grid2` became the primary `Grid` (codemod: `npx @mui/codemod@latest
v7.0.0/grid-props <path>`); `InputLabel`'s `size="normal"` became
`size="medium"` (codemod: `npx @mui/codemod@latest
v7.0.0/input-label-size-normal-medium <path>`); removed deprecated APIs
(`createMuiTheme` → `createTheme`, `Hidden` → `sx`/`useMediaQuery`,
`experimentalStyled` → `styled`, Dialog/Modal `onBackdropClick` → `onClose`
reason check, `StepButtonIcon` type → `StepButtonProps['icon']`); several
`@mui/lab` components (Alert, Autocomplete, Rating, Skeleton, etc.) moved
into `@mui/material` proper (codemod: `npx @mui/codemod@latest
v7.0.0/lab-removed-components <path>`); minimum **TypeScript raised to v4.9**
(from v4.7); React ≤18 apps must pin `react-is` to their installed React
version via package-manager `overrides`, because Material UI itself depends
on `react-is@19`. [Source: https://mui.com/material-ui/migration/upgrade-to-v7/]
With CSS variables enabled, "the theme no longer changes between modes" —
components read `theme.vars.*` instead, for performance.

[Source: https://mui.com/material-ui/migration/upgrade-to-v9/] **v7 → v9**
breaking changes (Material UI's major version jumped from v7 directly to v9,
skipping v8, to align numbering with the rest of the MUI product suite —
confirmed by the blog post's framing of v9 as "part of a coordinated effort
across the entire product suite," though the FAQ-level "why v8 specifically
was skipped" reasoning was not found in the docs fetched — [Unresolved: the
exact rationale/announcement for skipping v8 specifically was not located in
the official docs pages retrieved]): `GridLegacy` is fully **removed** (must
migrate to the `size` prop on `Grid`, dropping the `item` prop and the
`xs`/`sm`/`md`/`lg`/`xl` boolean-breakpoint props); `Grid` no longer accepts
`direction="column"`/`"column-reverse"` — use `Stack` for vertical layouts
instead; `Dialog`/`Modal`'s `disableEscapeKeyDown` prop is **removed** — use
the `reason` argument in `onClose` instead; `ButtonBase` keyboard/click event
bubbling behavior changed (Enter/Space-triggered clicks now bubble properly;
keyboard handlers no longer fire on disabled non-native buttons); the
`components`/`componentsProps` prop pattern is replaced by `slots`/`slotProps`
across most components (e.g. `PaperProps` → `slotProps.paper`), with codemods
available via `npx @mui/codemod@latest deprecations/[component-name]-props
<path>`; minimum supported browsers raised to **Chrome 117+, Firefox 121+,
Safari 17.0+**; layout components (`Box`, `Typography`, `Stack`, etc.) no
longer accept direct system props (`mt`, `mr`, etc. as top-level props) — use
the `sx` prop instead.

[Source: https://mui.com/material-ui/migration/troubleshooting/] Separately
documented **v4 → v5** troubleshooting (older but still officially
maintained on the docs site): missing `StyledEngineProvider` or lingering
`@material-ui/core` (v4 package name) dependencies cause broken styles
(check via `npm ls @material-ui/core`); Storybook 6.x needs an Emotion
webpack alias fix (`@emotion/core` → `@emotion/react`); color imports must
use named imports (`import { red } from '@mui/material/colors'`, not a deep
default import) — codemod: `npx @mui/codemod@latest v5.0.0/optimal-imports
<path>`; `makeStyles`-based hooks called outside `<ThemeProvider>` throw
theme-property errors.

[Source: https://mui.com/material-ui/getting-started/faq/] The docs also
flag legacy (pre-v5, JSS-era) SSR issues as historical/legacy troubleshooting
items: multiple styling-library instances in one bundle, missing
`StylesProvider`, reusing one JSS `sheets` instance across multiple SSR
requests (must create a fresh one per request), and hydration mismatches
from mismatched MUI versions/`NODE_ENV` between server and client — these
are explicitly marked "[Legacy]" in the FAQ, i.e. not applicable to current
Emotion-based v5+ setups.

[Not documented / could not verify] No official migration guide *from* a
comparable alternative library (e.g. Ant Design, Chakra UI, Bootstrap) into
Material UI was found; MUI's migration docs are scoped to upgrading between
Material UI's own major versions (and from the legacy `@material-ui/*`
package names to `@mui/*`).

---

## 12. Version information

[Source: https://registry.npmjs.org, queried 2026-09-09] Current stable
`@mui/material` version: **9.4.0**, published **2026-08-27**. `next` dist-tag:
`9.0.0-beta.1` (pre-release channel).

[Source: https://mui.com/material-ui/getting-started/versions/] Major
version history: v0 (legacy) → v1 (May 2018) → v3 (September 2018) → v4 (May
2019) → v5 (September 2021) → v6 (August 2024) → v7 (March 2025) → v9 (April
2026, current stable). No v2 or v8 line was listed for Material UI itself in
the versions table fetched — [Unresolved: whether "v8" was ever released for
Material UI specifically, briefly, or was skipped entirely as part of the
MUI-X version-alignment effort, was not conclusively confirmed by the pages
fetched; the v9 blog post frames the jump as an ecosystem-wide alignment but
does not state definitively whether an internal/unreleased v8 existed].

[Source: https://mui.com/blog/introducing-material-ui-v9/] v9.0.0 released
**Wednesday, April 8, 2026**.

[Source: https://mui.com/material-ui/getting-started/versions/] Versioning
follows **Semantic Versioning 2.0.0** (`major.minor.patch`). Documented
cadence: **major** releases approximately every ~12 months; **minor**
releases multiple times per major cycle; **patch** releases monthly or
as-needed for urgent fixes.

[Source: https://github.com/mui/material-ui/blob/master/SECURITY.md]
Support/EOL policy (functions as MUI's closest analogue to an LTS policy):
v9.x (current) and v7.x (designated long-term support — "security issues and
regressions") both receive security patches; v6.x and older do not. [Source:
https://mui.com/material-ui/getting-started/support/] The support page
independently corroborates: v9.0.0 has continuous support, v7.0.0 has
"Long-term support (Support for security issues and regressions)."

[Source: https://mui.com/material-ui/getting-started/installation/] Peer
dependency support: **React 17.0.0+, 18.0.0+, and 19.0.0+**; React ≤18 apps
must additionally pin `react-is` to match their installed React major
version (package-manager `overrides`) because Material UI's own code depends
on `react-is@19`.

---

## 13. Breaking changes

(Full breaking-change details are in §11; this section summarizes the
highest-impact items per major version, tagged by version.)

[Version-sensitive: v7] [Source: https://mui.com/material-ui/migration/upgrade-to-v7/]
Package export/import restructuring (only shallow imports supported);
`Grid` → `GridLegacy` rename with `Grid2` promoted to `Grid`;
`InputLabel size="normal"` → `"medium"`; several deprecated top-level APIs
removed (`createMuiTheme`, `Hidden`, `experimentalStyled`); `@mui/lab`
components folded into `@mui/material`; TypeScript minimum raised to 4.9.

[Version-sensitive: v9] [Source: https://mui.com/material-ui/migration/upgrade-to-v9/]
`GridLegacy` fully removed; `Grid` loses `direction="column"`/`"column-reverse"`
support; `Dialog`/`Modal`'s `disableEscapeKeyDown` removed in favor of
`onClose`'s `reason` argument; `components`/`componentsProps` → `slots`/`slotProps`
migration across the library; system props removed from `Box`/`Typography`/`Stack`
(use `sx`); minimum browser support raised to Chrome 117+/Firefox 121+/Safari 17+;
`ButtonBase` keyboard-event bubbling behavior changed.

[Version-sensitive: v9] [Source: https://mui.com/blog/introducing-material-ui-v9/]
Non-breaking but notable: CSS variables now generate `color-mix()`-based
derived colors (more precise palette derivation); Backdrop no longer applies
`aria-hidden` by default; Autocomplete no longer opens its menu on
right-click; roving-tabindex keyboard navigation improved for Stepper, Tabs,
MenuList.

[Version-sensitive: v5, historical] [Source: https://mui.com/material-ui/migration/troubleshooting/]
The v4→v5 transition (package rename `@material-ui/core` → `@mui/material`,
JSS → Emotion default styling engine, `makeStyles`/`withStyles` deprecated in
favor of `styled`/`sx`) remains documented as the largest historical
breaking change, still covered in the current troubleshooting guide because
of its long tail of migration issues.

---

## 14. Limitations

[Source: https://mui.com/material-ui/integrations/nextjs/, https://mui.com/blog/mui-next-js-app-router/]
All Material UI components ship with `"use client"` — they **cannot** be
rendered as React Server Components; every Material UI subtree in an RSC
framework is client-side JavaScript.

[Source: https://mui.com/material-ui/getting-started/installation/]
**styled-components is not compatible with server-rendered Material UI
projects**, per the official installation guide, due to Babel plugin
limitations — Emotion is required for SSR.

[Source: https://mui.com/material-ui/getting-started/faq/] `Portal`/`Popper`
require an actual DOM node (not a React ref object) for certain props —
documented as a hard API constraint, not just a style preference.

[Source: https://mui.com/material-ui/customization/theming/, §11] With CSS
variables enabled, the *theme object itself* stops varying between color
modes at the JS level ("the theme no longer changes between modes") —
components must read `theme.vars.*`; code that inspects `theme.palette.mode`
or similar at runtime for conditional logic needs to be adapted to this
model. [Inference, not confirmed in docs] This is a documented behavioral
constraint of opting into `cssVariables: true`, not a general limitation of
Material UI theming as a whole.

[Source: https://mui.com/material-ui/guides/content-security-policy/] Strict
CSP deployments cannot fully avoid `'unsafe-inline'` for `style-src-attr`
under current Material UI internals, because some components apply dynamic
values via inline style *attributes* — the docs frame this as an accepted,
documented trade-off rather than a bug.

[Source: https://mui.com/material-ui/guides/minimizing-bundle-size/] Barrel
imports from `@mui/icons-material` cause severe (up to 6x) development-server
slowdowns — an ongoing, documented tooling limitation that requires
discipline (path imports, ESLint rule, editor config) to avoid rather than
being solved automatically by the library.

---

## 15. Debugging

[Source: https://mui.com/material-ui/migration/troubleshooting/] The
troubleshooting guide's core debugging heuristic for "styles look broken" is
to check, in order: (1) is `StyledEngineProvider` correctly configured at
the app root, (2) are there lingering old-major-version dependencies still
resolving (`npm ls @material-ui/core` for v4 leftovers), (3) for SSR set-ups,
is the working example being diffed against a known-good SSR reference
implementation.

[Source: https://mui.com/material-ui/getting-started/faq/] Debugging class
name collisions: "the #1 reason for styling issues" in production bundles is
class-name-generator conflicts when more than one instance of the styling
library ends up bundled — resolved via dependency deduplication.

[Source: https://mui.com/material-ui/getting-started/faq/] For fixed-position
elements jumping/misaligning when a modal opens, the documented debugging
fix is to apply the `.mui-fixed` class to those elements so Material UI's
modal scroll-lock logic accounts for them.

[Source: https://mui.com/material-ui/migration/troubleshooting/] For
`Fade`/`Grow`/`Slide`/`Zoom` throwing "Cannot read property scrollTop of
null," the documented debug/fix path is checking for a `React.Fragment`
child (needs a real forwarded-ref DOM node instead) or a custom child
component missing `React.forwardRef`.

[Inference, not confirmed in docs] No dedicated official "MUI DevTools"
browser extension or standalone debugging tool (distinct from standard React
DevTools) was found in this research; Material UI's debugging guidance, as
documented, is primarily a curated FAQ/troubleshooting knowledge base rather
than a dedicated tool.

---

## 16. Integration

[Source: https://mui.com/material-ui/integrations/nextjs/] **Next.js App
Router**: install `@mui/material-nextjs` + `@emotion/cache`; wrap
`app/layout.tsx`'s body content in `AppRouterCacheProvider` (imported from a
version-pinned subpath such as `@mui/material-nextjs/v15-appRouter`
[version-sensitive: subpath names track supported Next.js major versions]),
which streams collected Emotion CSS into `<head>` to avoid FOUC. **Pages
Router** (legacy) needs `AppCacheProvider` instead, configured in both
`pages/_document.tsx` (via `DocumentHeadTags` +
`documentGetInitialProps`) and `pages/_app.tsx`, plus the `@emotion/server`
package.

[Source: https://mui.com/blog/mui-next-js-app-router/] App Router
compatibility (via `"use client"` on all components) shipped in **Material
UI v5.14.0** [version-sensitive].

[Source: https://mui.com/material-ui/integrations/interoperability/]
Documented interoperability targets: **plain/global CSS** (MUI's CSS-in-JS
injects at the bottom of `<head>`, giving it precedence over earlier
stylesheets by default — a documented ordering concern for teams mixing
approaches); **styled-components** (recommended as an alternative *default*
engine to cut bundle size and remove injection-order configuration need);
**CSS Modules** (via `:global` selectors or the `slotProps` API to target
MUI's internal class names); **Emotion** (native — both `css()` and
`styled()`, theme-shared); **Tailwind CSS v3** (documented setup: disable
Tailwind's preflight, configure `important`, adjust injection order via
`StyledEngineProvider`); **JSS successor** — `tss-react` is the recommended
hook-based replacement for the deprecated `@mui/styles` (JSS) package for
teams migrating from pre-v5 styling.

[Source: https://mui.com/material-ui/guides/server-rendering/] **Express
SSR**: documented via a from-scratch example (shared theme file, Express
middleware rendering to string, `createEmotionServer` critical-CSS
extraction, client hydration) — framework-agnostic pattern for non-Next.js
Node servers.

[Source: https://mui.com/material-ui/getting-started/faq/] **Routing
libraries** (React Router etc.): integration is documented via a dedicated
"integration with third-party routing libraries" guide (referenced from the
FAQ; not independently fetched in this pass) — [Unresolved: exact guide URL
and content not directly verified in this research].

[Source: https://mui.com/blog/mui-product-comparison/] **MUI X**: a
separate, independently versioned package family (Data Grid, Date/Time
Pickers, Charts, Tree View, Scheduler [alpha, v9], Chat [alpha, v9]) that
integrates with Material UI's theme but ships its own docs at `mui.com/x`
and, per v9, now shares major-version numbering with Material UI ("both
libraries will share major versioning, simplifying upgrades across the tech
stack" — [Source: https://mui.com/blog/introducing-mui-v9/]).

---

## 17. Production considerations

[Source: https://mui.com/material-ui/getting-started/installation/] Use the
default **Emotion** styling engine for any server-rendered production app;
styled-components is documented as SSR-incompatible with Material UI.

[Source: https://mui.com/material-ui/guides/content-security-policy/]
Production deployments under a strict CSP need per-request nonce plumbing
(Emotion `CacheProvider` + response header) and must accept
`style-src-attr 'unsafe-inline'` for certain dynamic inline styles — plan
CSP headers accordingly rather than assuming a nonce-only policy will work
unmodified (see §4, §7, §14).

[Source: https://mui.com/material-ui/getting-started/versions/,
https://github.com/mui/material-ui/blob/master/SECURITY.md] For long-lived
production apps that can't track every major release immediately, **v7.x is
the documented long-term-support line** receiving security/regression
patches alongside current v9.x — a relevant fact for planning upgrade
cadence versus staying on a security-patched older major.

[Source: https://mui.com/material-ui/getting-started/faq/] Material UI
itself is **MIT-licensed and free** with no runtime licensing/telemetry
requirement for the core `@mui/material` package. [Source:
https://mui.com/blog/introducing-material-ui-v9/] By contrast, MUI X's
**commercial** components (Pro/Premium tiers) introduced telemetry enabled
by default in development mode as of v9 [version-sensitive: MUI X commercial
tiers only, not Material UI core] — production teams using MUI X Pro/Premium
should review the licensing/telemetry docs at `mui.com/x/introduction/licensing/`
before deployment (not independently fetched in full in this research pass;
flagged as a scope boundary since this research targets Material UI, not
MUI X).

[Source: https://mui.com/material-ui/getting-started/support/] No official
paid support channel exists for Material UI core specifically; production
teams needing contracted support are pointed to third-party options (custom
contract engineering work, or a Tidelift subscription for OSS-dependency
coverage) rather than an MUI-run enterprise support product for Core (MUI X
has its own separate technical support for paying customers).

[Source: https://mui.com/material-ui/guides/minimizing-bundle-size/]
Production builds should still audit for accidentally-bundled duplicate
styling-engine instances (a documented cause of the "#1 styling issue" in
§15) even though tree-shaking handles most dead-code elimination
automatically in modern bundlers.

---

## Sources consulted (deduplicated)

- https://mui.com/material-ui/ — overview/positioning
- https://mui.com/material-ui/getting-started/installation/ — install, peer deps, styling engines, fonts/icons
- https://mui.com/material-ui/getting-started/versions/ — version history, semver policy, cadence
- https://mui.com/material-ui/getting-started/faq/ — gotchas, anti-patterns, legacy SSR issues
- https://mui.com/material-ui/getting-started/support/ — support channels, LTS framing
- https://mui.com/material-ui/customization/theming/ — theme structure, CSS variables, module augmentation
- https://mui.com/material-ui/customization/palette/ — palette tokens, contrastThreshold, tonalOffset, colorSchemes
- https://mui.com/material-ui/customization/how-to-customize/ — sx/styled()/theme-overrides/GlobalStyles
- https://mui.com/material-ui/guides/minimizing-bundle-size/ — import patterns, dev-perf, ESLint/VSCode config
- https://mui.com/material-ui/guides/testing/ — Testing Library guidance, snapshot-testing caveat
- https://mui.com/material-ui/guides/server-rendering/ — Express + Emotion SSR pattern
- https://mui.com/material-ui/guides/content-security-policy/ — CSP nonce/directive guidance
- https://mui.com/material-ui/migration/upgrade-to-v7/ — v6→v7 breaking changes/codemods
- https://mui.com/material-ui/migration/upgrade-to-v9/ — v7→v9 breaking changes/codemods
- https://mui.com/material-ui/migration/troubleshooting/ — v4→v5 troubleshooting guide
- https://mui.com/material-ui/integrations/nextjs/ — Next.js App/Pages Router integration
- https://mui.com/material-ui/integrations/interoperability/ — styling-library interop
- https://mui.com/material-ui/api/button/ — component API reference structure
- https://mui.com/system/screen-readers/ — visuallyHidden accessibility utility
- https://mui.com/material-ui/discover-more/changelog/ — changelog pointer (to GitHub CHANGELOG.md)
- https://mui.com/blog/introducing-material-ui-v9/ — v9.0 release details
- https://mui.com/blog/mui-next-js-app-router/ — v5.14.0 App Router support announcement
- https://mui.com/blog/mui-product-comparison/ — MUI ecosystem architecture (Base UI/Material UI/Joy UI/System/X)
- https://github.com/mui/material-ui/blob/master/SECURITY.md — vulnerability reporting, supported-version security policy
- https://registry.npmjs.org (npm registry API for `@mui/material`) — current published version confirmation
