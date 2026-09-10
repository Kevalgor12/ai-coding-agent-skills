# MUI migration: v6→v7 and v7→v9 breaking changes

Tier-2 deep reference for `skills/mui`. Loaded only when a migration task
needs the full breaking-change list; the Knowledge section of `SKILL.md`
covers only what's needed for everyday component/theme authoring.

All claims sourced from `research/technologies/mui.md` §11/§13, itself
sourced from the official migration guides. Retrieved 2026-09-10.

## v6 → v7

[Source: https://mui.com/material-ui/migration/upgrade-to-v7/]

- **Import restructuring:** deep imports beyond one path segment are no
  longer supported — e.g. `createTheme` must be imported from
  `@mui/material/styles`, not a deeper subpath.
- **Grid rename:** the legacy `Grid` was renamed to `GridLegacy`, and the
  new `Grid2` became the primary `Grid`. Codemod:
  `npx @mui/codemod@latest v7.0.0/grid-props <path>`.
- **InputLabel size:** `size="normal"` became `size="medium"`. Codemod:
  `npx @mui/codemod@latest v7.0.0/input-label-size-normal-medium <path>`.
- **Removed deprecated APIs:** `createMuiTheme` → `createTheme`, `Hidden` →
  `sx`/`useMediaQuery`, `experimentalStyled` → `styled`, Dialog/Modal
  `onBackdropClick` → `onClose` reason check, `StepButtonIcon` type →
  `StepButtonProps['icon']`.
- **`@mui/lab` consolidation:** several `@mui/lab` components (Alert,
  Autocomplete, Rating, Skeleton, etc.) moved into `@mui/material` proper.
  Codemod: `npx @mui/codemod@latest v7.0.0/lab-removed-components <path>`.
- **TypeScript minimum raised to 4.9** (from 4.7).
- **`react-is` peer gotcha:** React <=18 apps must pin `react-is` to their
  installed React major via package-manager `overrides`, because Material
  UI itself depends on `react-is@19`.
- **CSS variables behavior:** with CSS variables enabled, "the theme no
  longer changes between modes" — components read `theme.vars.*` instead,
  for performance.

## v7 → v9

Material UI's major version jumped from v7 directly to v9, **skipping v8**,
to align numbering with the rest of the MUI product suite (MUI X now shares
major-version numbers with Material UI as of v9) [Source:
https://mui.com/blog/introducing-material-ui-v9/,
https://mui.com/material-ui/migration/upgrade-to-v9/]. [Unresolved: the
exact rationale/announcement for why v8 specifically was skipped, beyond the
blog's general "coordinated effort across the entire product suite" framing,
was not located in the official docs pages retrieved during research.]

[Source: https://mui.com/material-ui/migration/upgrade-to-v9/]

- **`GridLegacy` fully removed** — must migrate to the `size` prop on
  `Grid`, dropping the `item` prop and the `xs`/`sm`/`md`/`lg`/`xl`
  boolean-breakpoint props.
- **`Grid` direction props removed:** no longer accepts
  `direction="column"`/`"column-reverse"` — use `Stack` for vertical
  layouts instead.
- **`disableEscapeKeyDown` removed:** on `Dialog`/`Modal`, use the `reason`
  argument in `onClose` instead.
- **`ButtonBase` event-bubbling change:** Enter/Space-triggered clicks now
  bubble properly; keyboard handlers no longer fire on disabled
  non-native buttons.
- **`components`/`componentsProps` → `slots`/`slotProps`** across most
  components (e.g. `PaperProps` → `slotProps.paper`). Codemod:
  `npx @mui/codemod@latest deprecations/[component-name]-props <path>`.
- **Minimum supported browsers raised** to Chrome 117+, Firefox 121+,
  Safari 17.0+.
- **System props removed from layout components:** `Box`, `Typography`,
  `Stack`, etc. no longer accept direct system props (`mt`, `mr`, etc. as
  top-level props) — use the `sx` prop instead.

[Source: https://mui.com/blog/introducing-material-ui-v9/] Non-breaking but
notable v9 changes: CSS variables now generate `color-mix()`-based derived
colors (more precise palette derivation); `Backdrop` no longer applies
`aria-hidden` by default; `Autocomplete` no longer opens its menu on
right-click; roving-tabindex keyboard navigation improved for Stepper, Tabs,
MenuList.

## Historical: v4 → v5 (still documented, long troubleshooting tail)

[Source: https://mui.com/material-ui/migration/troubleshooting/] Package
rename `@material-ui/core` → `@mui/material`; styling engine default
changed from JSS to Emotion; `makeStyles`/`withStyles` deprecated in favor
of `styled`/`sx`. Common residual issues: missing `StyledEngineProvider`,
lingering `@material-ui/core` (v4 package name) dependencies breaking
styles (check via `npm ls @material-ui/core`), Storybook 6.x needing an
Emotion webpack alias fix (`@emotion/core` → `@emotion/react`), and color
imports needing named imports (`import { red } from '@mui/material/colors'`,
not a deep default import) — codemod:
`npx @mui/codemod@latest v5.0.0/optimal-imports <path>`.

[Source: https://mui.com/material-ui/getting-started/faq/] Legacy
(pre-v5, JSS-era) SSR issues, explicitly marked "[Legacy]" and not
applicable to current Emotion-based v5+ setups: multiple styling-library
instances in one bundle, missing `StylesProvider`, reusing one JSS `sheets`
instance across multiple SSR requests (a fresh one is needed per request),
and hydration mismatches from mismatched MUI versions/`NODE_ENV` between
server and client.
