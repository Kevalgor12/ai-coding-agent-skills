---
name: Styling systems
description: >-
  Architect styling — design-token/theme structure, responsive strategy,
  style scoping/encapsulation, and dark-mode strategy, and choose a
  styling tool when that choice is open. Use when setting up or
  restructuring how an app is styled. Not for visual/interaction-design
  judgment (ui-ux-design) or a one-off style tweak with an established
  system already in place.
spec_version: "1.0"
---

## Purpose & scope

Architect design-token/theme structure, responsive strategy, style
scoping, and dark-mode strategy — independent of tool, though specialized
by [tailwindcss](../tailwindcss/SKILL.md), [sass](../sass/SKILL.md),
[web-standards](../web-standards/SKILL.md), [shadcn-ui](../shadcn-ui/SKILL.md),
and [mui](../mui/SKILL.md) for implementation depth. Visual/interaction-
design judgment belongs to [ui-ux-design](../ui-ux-design/SKILL.md);
accessibility depth belongs to
[web-accessibility](../web-accessibility/SKILL.md).

## When to use / When not to use

**Use** when setting up or restructuring how an app is styled, designing a
design-token/theme architecture, or when a styling-tool choice is open.
**Do not use** for a one-off style tweak with an established system
already in place, or for visual/interaction-design judgment once the
styling architecture is settled.

## Knowledge

**Design-system/theming implementation differs structurally, not just
syntactically, across every styling technology this library researched —
and the difference maps directly onto runtime-vs-build-time theming.**
MUI centralizes theming via `ThemeProvider` distributing a theme object at
runtime. Tailwind's design tokens are the literal basis of its utility
classes, generated at build time. shadcn/ui delivers its design system as
copy-in source, not an installed package. Sass's theming (SassScript
variables) is compile-time. CSS supports theming natively via custom
properties, which — unlike Sass variables — persist into runtime and can
be read/written by JavaScript
[Source: concept-knowledge-map.md — Design System/Theming]. **This is the
single most consequential architectural choice this skill makes**: a
project needing genuine runtime theme-switching (user-toggleable
light/dark, white-labeling) needs CSS custom properties or MUI's
`ThemeProvider` model; a project with a fixed brand needs neither and can
use compile-time tokens (Sass variables, Tailwind's generated utilities)
with no runtime cost.

**MUI and shadcn/ui represent genuinely different distribution models with
different supply-chain and patch-propagation consequences — not just
different APIs.** MUI is an installed npm package (`@mui/material`) with a
standard upgrade path; only v9.x (current) and v7.x (LTS) receive security
patches. shadcn/ui is explicitly **not a component library — a code
distribution platform**: components are copied as readable, modifiable
source into the consuming project via a CLI, with no CSS-in-JS runtime
since Tailwind v4 adoption. **The code-ownership trade-off shadcn/ui
advertises as a benefit has a documented-but-unstated cost**: a security
fix upstream in shadcn/ui's registry does not propagate to a project
automatically the way an `npm update` on MUI would — a vulnerability in
previously-copied component code must be manually re-pulled per project
[Synthesis, technology-decision-matrix.md §8]. This is a structural
architecture decision, not a preference — see
[mui](../mui/SKILL.md) and [shadcn-ui](../shadcn-ui/SKILL.md) for full
depth.

**Sass, Tailwind, and native CSS occupy genuinely different points on the
build-time-processing spectrum, and Tailwind v4 specifically declines to
support using Sass alongside it.** Tailwind v4 explicitly names Sass
(along with Less/Stylus) as "not supported" for use alongside it, since
its native-CSS-feature architecture (CSS Nesting, `@property`, custom
properties) replaces what preprocessors used to provide. Native CSS
Nesting is itself documented by MDN as a **migration target away from**
Sass-style preprocessor nesting. **None of the three sources states a
direct "X is faster than Y" claim across tools** — Tailwind's v4 benchmark
is against its own v3, and Sass's benchmark is against its own prior
implementations (Ruby Sass, LibSass), not against each other
[Source: technology-decision-matrix.md §9]. Treat any cross-tool
performance comparison as unresearched unless it's this same-tool,
same-vendor kind of claim.

**Style scoping/encapsulation has no single dominant approach across this
research — the right choice depends on the styling tool already in
place.** Tailwind's utility-class model sidesteps traditional CSS
specificity conflicts by generating single-purpose classes rather than
cascading rules. CSS Modules and Sass's own scoping conventions (BEM-style
naming, `@use`'s module namespacing) solve the same specificity-war
problem differently. shadcn/ui's copied-source components use `data-slot`
attributes rather than wrapper-component overhead for styling hooks. Match
the scoping approach to the tool already chosen rather than importing a
convention from a different ecosystem.

## Decision framework

1. **Does theming need to change at runtime, or is the brand fixed at
   build time?** Runtime need → CSS custom properties or MUI's
   `ThemeProvider` model. Fixed brand → compile-time tokens (Sass
   variables, Tailwind's generated utilities), avoiding unnecessary
   runtime cost.
2. **Is a component library needed, and if so, which distribution model
   fits?** An installed-dependency model (MUI) gets automatic
   `npm update` patch propagation at the cost of CSP/nonce configuration
   for its CSS-in-JS runtime. A copy-in-source model (shadcn/ui) gets full
   code ownership and no CSS-in-JS runtime, at the cost of manual
   re-patching per project when a vulnerability is found upstream.
3. **Is a preprocessor actually needed**, given Tailwind v4's native-CSS
   feature set (nesting, custom properties, `@property`) covers much of
   what preprocessors used to provide, and Tailwind v4 doesn't support
   using Sass alongside it? Don't default to a preprocessor out of habit.
4. **What scoping/encapsulation convention fits the tool already in
   place?** Don't import a convention (BEM naming, CSS Modules) from a
   different ecosystem than the one already chosen without a specific
   reason.
5. **Is dark mode designed as a first-class variant**, composable with
   responsive breakpoints (as Tailwind's `dark:` variant demonstrates), or
   bolted on separately? Design it as a first-class concern from the
   start.

## Workflow

1. Confirm design-system/brand constraints and whether a styling tool is
   already chosen.
2. Decide runtime vs. build-time theming based on actual need.
3. If a component library is in scope, choose distribution model
   (installed dependency vs. copy-in-source) based on the patch-
   propagation and ownership trade-offs.
4. Design token/theme structure avoiding duplicated magic values.
5. Design responsive strategy and dark-mode variant composition together,
   not as separate afterthoughts.
6. Choose scoping/encapsulation convention matching the tool in use.
7. Hand off implementation syntax to the relevant technology skill.

## Engineering rules

- Choose runtime vs. build-time theming based on actual need, not by
  default.
- Treat component-library distribution model (installed dependency vs.
  copy-in-source) as an architecture decision with real patch-propagation
  consequences, not a style preference.
- Don't default to a preprocessor without checking whether native CSS
  features already cover the need.
- Match scoping convention to the tool already in use.
- Design dark mode as a first-class, composable variant from the start.

## Trade-offs

Runtime theming buys flexibility (user-toggleable themes, white-labeling)
at a real runtime cost a fixed-brand project doesn't need to pay.
Installed-dependency component libraries buy automatic patch propagation
at the cost of CSS-in-JS runtime/CSP configuration; copy-in-source
libraries buy full code ownership and zero runtime cost at the cost of
manual re-patching when a vulnerability is found. Preprocessors buy
authoring conveniences (nesting, mixins) that native CSS increasingly
provides natively — worth checking whether the convenience still
justifies the added build step.

## Anti-patterns

- **Adding runtime theming machinery for a fixed single brand** with no
  actual theme-switching requirement.
- **Choosing a component library's distribution model without
  considering patch-propagation consequences** — shadcn/ui's copy-in-
  source model has no automatic upgrade path the way an installed
  dependency does.
- **Reaching for Sass by default** without checking whether native CSS
  (nesting, custom properties, `@property`) already covers the need —
  especially relevant given Tailwind v4's explicit non-support for using
  Sass alongside it.
- **Importing a scoping convention from a different ecosystem** than the
  styling tool already in use.
- **Bolting dark mode on as a separate, later concern** instead of
  designing it as a first-class composable variant from the start.

## Security

MUI's Emotion-injected `<style>` tags require a CSP `style-src-elem
'nonce-<base64>'` directive matched per-request; shadcn/ui's copy-in-
source model has no automatic vulnerability-patch propagation, requiring
manual re-pulls per project — both real, structural security-relevant
architecture decisions covered in depth by
[mui](../mui/SKILL.md) and [shadcn-ui](../shadcn-ui/SKILL.md). Deep
threat modeling is owned by
[security-engineering](../security-engineering/SKILL.md).

## Performance

Runtime theming/CSS-in-JS costs real runtime overhead that build-time
tokens (Tailwind's generated utilities, Sass's compiled output) don't
pay — a genuine performance dimension of the theming decision, not just
an architectural preference. Deep performance method is owned by
[performance-engineering](../performance-engineering/SKILL.md).

## Testing

No styling technology this library researched (Sass, Tailwind, plain CSS)
publishes a dedicated official testing framework — each is a build-time
CSS-generation concern with no component behavior of its own to unit-test;
component-library testing (MUI, shadcn/ui) is owned by those skills.
Conformance testing (web-platform-tests) is browser-conformance testing,
not application testing. Deep test-strategy method is owned by
[testing-strategy](../testing-strategy/SKILL.md).

## Failure handling

- If design-system/brand constraints aren't stated, ask rather than
  assume a token structure.
- If a styling tool is already in place, work within it unless a switch
  is explicitly requested.

## Escalation

- A styling-tool or component-library switch for an established codebase
  is a significant, hard-to-reverse decision — presented with trade-offs
  for explicit confirmation, never applied unilaterally.

## Outputs & verification

- **Outputs:** token/theme structure, responsive strategy, scoping
  approach, and dark-mode strategy, with rationale.
- **Verify:** theming/dark-mode/responsive behavior works without
  duplicated magic values; a tool recommendation cites documented
  structural differentiators, not unresearched preference.

## References

- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
- [research/knowledge-maps/concept-knowledge-map.md](../../research/knowledge-maps/concept-knowledge-map.md)
