---
name: UI/UX design
description: >-
  Apply interaction and visual-design judgment — information hierarchy,
  responsive layout, interaction states (hover/focus/loading/empty/
  error), and consistency — to UI work. Use when designing or improving a
  user-facing interface, or reviewing one for design quality. Not for
  styling implementation syntax (styling-systems) or component/state
  architecture (frontend-architecture).
spec_version: "1.0"
---

## Purpose & scope

Apply interaction and visual-design judgment — hierarchy, layout,
responsive behavior, interaction states, consistency — to UI work.
Implementation-specific styling syntax belongs to
[styling-systems](../styling-systems/SKILL.md); component/state
architecture belongs to
[frontend-architecture](../frontend-architecture/SKILL.md). **A real
grounding boundary, stated honestly**: this library's research is
technology-documentation-shaped (component libraries, markup specs,
CSS), not an independently deep UX-research corpus with usability-testing
methodology or quantitative design research. What's grounded here is what
that documentation actually covers — native-element affordances,
component-variant systems, responsive/dark-mode variant conventions — applied
alongside professional design judgment for the rest, not presented as more
independently researched than it is.

## When to use / When not to use

**Use** when designing or improving a user-facing interface, or when a UI's
hierarchy/layout/interaction states need review, including an explicit
frontend design review. **Do not use** for non-visual/backend tasks,
implementation-specific styling syntax with design decisions already made,
or component/state architecture with no visual/interaction-design
question.

## Knowledge

**Native HTML elements provide interaction affordances "for free," and
this is the highest-leverage, lowest-cost interaction-design decision
available.** Keyboard support, focus management, and the correct implicit
interaction states (hover/focus/active/disabled) come built in with the
right element — a `<button>` instead of a styled `<div>`, a `<label>`
properly associated with its `<input>`. Faking this with a generic
container requires manually reconstructing everything the native element
already gave you, characterized in this library's research as
"significantly more work" than using the right element from the start
[Source: developer.mozilla.org — HTML: A good basis for accessibility].
This isn't just an accessibility concern (covered in depth by
[web-accessibility](../web-accessibility/SKILL.md)) — it's also the
cheapest path to correct interaction-state behavior, full stop.

**Design-system/theming and responsive-design approaches differ
meaningfully across the component libraries and styling tools this
library researched, and the differences are structural, not cosmetic.**
MUI centralizes theming via `ThemeProvider` distributing a theme object at
runtime. Tailwind's design tokens are the literal basis of its utility
classes — the token system isn't a separate layer bolted onto CSS, it *is*
the styling system. shadcn/ui delivers its design system as copy-in
source rather than an installed package — a structurally different
distribution model from the other two (already covered in depth by
[shadcn-ui](../shadcn-ui/SKILL.md)'s supply-chain framing). Sass's
theming is compile-time (SassScript variables), not runtime. CSS itself
supports theming natively via custom properties
[Source: concept-knowledge-map.md — Design System/Theming]. **Which
approach fits depends on whether theming needs to change at runtime** (MUI's
`ThemeProvider`, CSS custom properties) **or is fixed at build time** (Sass
variables, Tailwind's generated utility classes) — a real, consequential
design decision, not an implementation detail to defer.

**Responsive-design and dark-mode conventions vary by tool, and knowing
each tool's own idiom matters for a design that actually gets implemented
well.** Tailwind stacks responsive breakpoint variants (`sm:`, `md:`,
`lg:`) directly on utility classes, and its `dark:` variant composes with
state/responsive variants on the same class — a single class can express
"on medium screens, in dark mode, when hovered." This composability is a
real design affordance, not just a syntax convenience — it means
responsive and dark-mode behavior can be specified together rather than
as separate concerns layered awkwardly on top of each other
[Source: concept-knowledge-map.md — Responsive Design, Dark Mode Theming].

## Decision framework

1. **Does a native HTML element already provide the interaction behavior
   needed?** If so, design around it rather than reconstructing its
   affordances from scratch — this is true even before accessibility
   considerations enter the picture.
2. **Are loading, empty, and error states designed explicitly**, or only
   the "happy path"? A UI task isn't complete until these are addressed —
   they're not edge cases to discover during implementation.
3. **Does theming/design-system needs happen at runtime or build time?**
   Runtime theming (a user-toggleable theme, white-labeling) needs a
   runtime mechanism (CSS custom properties, MUI's `ThemeProvider`-style
   approach); a fixed brand needs no such machinery — don't add runtime
   theming complexity a project doesn't need.
4. **Is responsive behavior designed as a first-class concern**, not an
   afterthought applied to a single-viewport design? Design across the
   viewport range the feature actually needs to support, not just desktop.
5. **Does this design favor a sensible, consistent default over novelty
   for its own sake?** Consistency with the existing product's patterns
   usually serves users better than a bespoke one-off treatment, absent a
   specific reason for the exception.
6. **Does this request need UX-research depth this library hasn't
   researched** (formal usability-testing methodology, quantitative
   research)? If so, say so rather than presenting design judgment as if
   it were research-backed.

## Workflow

1. Confirm feature intent and any existing brand/design-system
   constraints.
2. Check whether a native element already provides the needed
   interaction behavior before designing a custom one.
3. Design information hierarchy and layout for the actual content, not a
   placeholder.
4. Design interaction states explicitly: hover, focus, loading, empty,
   error — not just the happy path.
5. Design responsive behavior across the viewport range the feature needs.
6. Decide runtime vs. build-time theming based on actual need.
7. Favor consistency with existing patterns over novelty, absent a
   specific reason.
8. Hand off implementation syntax to styling-systems and component/state
   structure to frontend-architecture.

## Engineering rules

- Use native element affordances before reconstructing interaction
  behavior manually.
- Design loading/empty/error interaction states explicitly, not as an
  afterthought.
- Design responsive behavior across the actual viewport range needed, not
  just one size.
- Choose runtime vs. build-time theming based on actual need, not
  reflexively.
- Favor consistent, sensible defaults over novelty without a specific
  reason.

## Trade-offs

Native-element-based interaction design is the cheapest, most robust
default but constrains visual customization somewhat compared to a fully
custom component built from generic containers. Runtime theming (MUI-
style `ThemeProvider`, CSS custom properties) buys flexibility a
user-toggleable theme or white-labeling need requires, at the cost of
runtime overhead and complexity a fixed-brand project doesn't need.
Novel, bespoke interaction patterns can differentiate a product but cost
more design/implementation effort and risk inconsistency with the rest of
the product — worth it only when there's a specific reason.

## Anti-patterns

- **Reconstructing native-element interaction behavior from a generic
  container** ("div-itis") instead of using the element that already
  provides it.
- **Designing only the happy path**, discovering loading/empty/error
  states as afterthoughts during implementation.
- **Designing for a single viewport** and treating responsive behavior as
  an implementation detail to sort out later.
- **Adding runtime theming machinery a project doesn't actually need**
  (a fixed single brand with no theme-switching requirement).
- **Reaching for novelty over consistency** without a specific reason the
  existing pattern doesn't serve the need.

## Security

Not a primary concern for this skill's scope; where UI design intersects
security (e.g. a form collecting sensitive data), defer to
[security-engineering](../security-engineering/SKILL.md).

## Performance

Runtime theming/CSS-in-JS approaches carry real runtime cost that
build-time approaches (Tailwind's generated utilities, Sass's compiled
output) don't — a design decision with a genuine performance dimension,
not just an aesthetic one. Deep performance method is owned by
[performance-engineering](../performance-engineering/SKILL.md).

## Testing

Interaction-state coverage (does the loading/empty/error state actually
render, not just the happy path) is the design-specific testing concern —
verify explicitly rather than assuming implementation covers states that
were never designed. Deep test-strategy method is owned by
[testing-strategy](../testing-strategy/SKILL.md).

## Failure handling

- If feature intent or design constraints aren't clear, ask rather than
  assume a visual direction.
- If a request needs UX-research depth this library hasn't researched,
  state that boundary rather than fabricating research-backed claims.

## Escalation

- A significant visual-identity or design-system change affecting
  existing product consistency is presented with trade-offs for explicit
  confirmation, not applied unilaterally.

## Outputs & verification

- **Outputs:** information hierarchy, responsive layout, and interaction-
  state design, with rationale.
- **Verify:** interaction states are designed explicitly; responsive
  behavior is addressed across the actual viewport range; the design
  favors consistency over unjustified novelty.

## References

- [research/knowledge-maps/concept-knowledge-map.md](../../research/knowledge-maps/concept-knowledge-map.md)
- [research/technologies/html.md](../../research/technologies/html.md)
