---
name: Web accessibility
description: >-
  Ensure UI markup and components are accessible — semantic HTML as the
  foundation, component-library accessibility primitives, and
  accessibility-aware testing via Playwright's role-based locators. Use when
  building user-facing UI or auditing for accessibility. Honest about scope:
  does not provide WCAG-success-criterion-level conformance depth, which is
  a documented research gap, not covered here.
spec_version: "1.0"
---

## Purpose & scope

Make user interfaces accessible, grounded in what this library has actually
researched: semantic HTML as the accessibility foundation, how component
libraries (MUI, shadcn/ui) build accessibility in, and accessibility-aware
testing via Playwright's role-based locators. **This skill is explicit about
a real boundary**: it does not provide WCAG-success-criterion-level
conformance auditing — that would require a dedicated research pass this
library hasn't done, and inventing conformance-level detail from general
knowledge would violate this project's source-grounding discipline. Where a
request needs that depth, this skill says so rather than fabricating it.

## When to use / When not to use

**Use** when building user-facing UI markup/components, or when an
accessibility review is requested. **Do not use** for backend/non-UI work,
or — without an explicit caveat — for formal WCAG conformance certification,
which exceeds this skill's grounded scope.

## Knowledge

**Semantic HTML is the accessibility foundation, and it's free.** The
WHATWG HTML Living Standard itself describes HTML as "a semantic-level
markup language... for authoring accessible pages" [Source:
html.spec.whatwg.org/multipage/introduction.html]. The central, well-grounded
principle: **use the right element for the right job.** Native elements
provide keyboard support, focus management, and screen-reader semantics "for
free," which must otherwise be manually reconstructed with ARIA and
JavaScript [Source: developer.mozilla.org — HTML: A good basis for
accessibility]. Concretely: `<button>` instead of a clickable `<div>`;
`<a href="...">` for navigation instead of `<div onclick>`; `<label>`
explicitly associated via `for`/`id` instead of bare text near an `<input>`;
`<header>`/`<nav>`/`<main>`/`<article>`/`<aside>`/`<footer>` instead of
undifferentiated `<div>`s.

**"Div-itis" is the named, documented anti-pattern**: using generic
`<div>`/`<span>` plus styling/JS to fake semantic elements' behavior and
appearance. This discards free keyboard/focus/screen-reader behavior and
requires manually re-adding `tabindex`, `role`, and key-event handling to
reach parity — explicitly characterized as "significantly more work" than
using the right element from the start [Source: developer.mozilla.org — HTML:
A good basis for accessibility].

**ARIA is a supplement, not a first choice.** Prefer native HTML
semantics/attributes over ARIA whenever a native equivalent exists; ARIA
(`role`, `aria-labelledby`, etc.) covers gaps native HTML cannot, it does not
replace semantic markup as the default [Source: developer.mozilla.org — HTML:
A good basis for accessibility]. Other concrete, grounded practices: a single
`<h1>` per page with logically nested subsequent headings (so screen-reader
users can navigate by heading and build an implicit table of contents);
meaningful `alt` text describing only what's visually conveyed and
contextually relevant (empty `alt=""` for purely decorative images — an
omitted `alt` makes a screen reader read the filename, "often useless");
`<th scope="col"|"row">` + `<caption>` on data tables so header/data
relationships reach assistive technology; descriptive link text ("Find out
more about whales") rather than context-free text ("click here"), since
screen readers frequently list links out of surrounding context [Source:
developer.mozilla.org — HTML: A good basis for accessibility].

**Component libraries build accessibility in differently.** MUI's contrast
ratios target WCAG-AA-ish defaults (raisable to 4.5:1 for stricter AA text
contrast), and its component architecture is layered on **Base UI** for
headless behavior/accessibility. shadcn/ui's accessibility comes from
whichever underlying primitive (Base UI or Radix) a component wraps, plus
shadcn's own variant props — its own docs don't have a dedicated
"Accessibility" section, but point to the underlying primitive [Source:
research/technologies/mui.md; research/technologies/shadcn-ui.md]. Neither
library's own docs make a comparative accessibility claim against the
other — treat both as "accessible via their underlying primitive," verify
specifics per component, don't assume parity.

**Testing can be accessibility-aware by construction.** Playwright's
Locators API surface prioritizes user-facing, accessibility-oriented queries
— `getByRole()`, `getByText()`, `getByLabel()`, `getByPlaceholder()`,
`getByAltText()`, `getByTitle()` — meaning a test suite written against these
locators is implicitly testing that the UI exposes correct accessible names
and roles, not just that pixels render [Source: playwright.dev/docs/locators].
Playwright's MCP integration goes further, operating on accessibility-tree
snapshots rather than screenshots/DOM dumps specifically because that
structured output is cheaper for an LLM agent to parse [Source:
playwright.dev/mcp/introduction] — a genuinely useful signal: if a UI's
elements don't have clear accessible roles/names, both screen-reader users
and AI-agent tooling struggle with it for the same underlying reason.

**Validation tooling exists for markup-level checks.** The W3C's Nu Html
Checker validates markup for "accessibility, usability, interoperability,
and security concerns" via web UI, bookmarklet (checks the live serialized
DOM), CLI, or Grunt/Gulp integration [Source: validator.w3.org/nu/about.html].

**What this skill does not cover**: a WCAG success-criteria-level
conformance matrix (e.g. per-criterion AA/AAA pass/fail auditing), a
comprehensive ARIA authoring-patterns catalog, or framework-specific (React/
Vue/Angular) accessibility API depth — none of these were part of this
library's completed research. Say so explicitly if asked for this depth
rather than inventing it.

## Decision framework

1. **Does a native HTML element already do this?** If yes, use it — that's
   the highest-leverage, lowest-cost accessibility decision available, and
   it's free.
2. **Only reach for ARIA when there's a genuine gap** — a custom widget with
   no native equivalent. Adding ARIA roles to elements that already have
   correct native semantics is redundant at best, contradictory at worst.
3. **When using a component library, trust but verify its underlying
   primitive** — MUI/shadcn build on Base UI or Radix for behavior/
   accessibility; check the specific component's documented behavior rather
   than assuming every component in the library is equally accessible.
4. **When a request exceeds this skill's grounded scope** (formal WCAG
   conformance, deep ARIA patterns, framework-specific a11y APIs), say so
   explicitly and recommend a dedicated research/audit pass rather than
   fabricating confidence.

## Workflow

1. Check whether native semantic elements already solve the need; use them.
2. Add ARIA only for genuine gaps with no native equivalent.
3. Verify alt text, heading hierarchy, table markup, and link text follow
   the grounded practices above.
4. If using a component library, confirm the underlying primitive's
   documented accessibility behavior for the specific component in use.
5. Where automated testing exists, prefer role/label-based locators
   (Playwright's `getByRole()` etc.) so tests double as an accessibility signal.
6. State explicitly if the request needs conformance-level depth this skill doesn't have.

## Engineering rules

- Use the right native element for the job before reaching for ARIA.
- Never leave an `<img>` without either meaningful `alt` text or an explicit empty `alt=""` for decorative images.
- Keep heading hierarchy logical (one `<h1>`, nested subsequent headings).
- Use `<th scope>` + `<caption>` on data tables, not plain `<td>`-only tables.
- Write descriptive link text, not "click here."
- State the boundary of this skill's grounded scope rather than fabricating WCAG-conformance-level claims.

## Trade-offs

Semantic HTML costs nothing extra and buys accessibility "for free" —
there's no real trade-off here, which is why it's the first-line
recommendation. ARIA buys accessibility for genuinely custom widgets at the
cost of manual maintenance (ARIA attributes don't self-verify the way native
element behavior does) — use it only where a native element truly can't do
the job.

## Anti-patterns

- **Div-itis** — the named, documented anti-pattern: generic containers
  styled/scripted to fake semantic elements, discarding free keyboard/focus/
  screen-reader behavior for "significantly more work" reconstructing it.
- **Faking document structure** with inline styles and `<br>` line breaks
  instead of real headings/paragraphs/lists — removes all semantic hooks
  assistive technology relies on.
- **Reaching for ARIA before checking for a native equivalent** — adds
  maintenance burden the native element would have avoided entirely.
- **Omitted or filename-derived alt text** — "often useless" per the
  research; either write meaningful alt text or explicitly mark decorative
  images empty.
- **Claiming WCAG conformance this skill hasn't actually verified** — the
  domain's specific "overengineering-in-reverse" trap: asserting confidence
  beyond the grounded scope.

## Security

Not a primary concern for this skill's scope; where accessibility markup
intersects security (e.g. ARIA live regions and content injection), defer to
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Not a primary concern for this skill's scope; semantic HTML has no
meaningful performance cost relative to div-based markup.

## Testing

Playwright's role-based locators (`getByRole()`, `getByLabel()`, etc.) make
accessibility testing a natural extension of functional testing rather than
a separate discipline — a test suite written this way fails when an
accessible name/role is missing, catching real regressions [Source:
playwright.dev/docs/locators]. Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md); Playwright-specific
depth is owned by the [playwright](../../core/taxonomy/skill-catalog.md)
technology skill.

## Failure handling

- If asked for WCAG-conformance-level auditing beyond this skill's grounded
  scope, state the gap explicitly rather than fabricating an assessment.
- If no target standard is stated, default to semantic-HTML-first practice
  rather than assuming a specific WCAG level.

## Escalation

- A legal/compliance accessibility requirement (ADA, AODA, EN 301 549, etc.)
  is flagged to the user directly — this skill's grounded scope does not
  constitute legal compliance verification.

## Outputs & verification

- **Outputs:** accessible markup/components using semantic elements and
  ARIA-as-supplement, and accessibility findings that state clearly what's
  in vs. out of this skill's grounded scope.
- **Verify:** native semantics used before ARIA; meaningful alt text present;
  interactive elements keyboard-operable via native behavior, not
  reconstructed div+JS.

## References

- [research/technologies/html.md](../../research/technologies/html.md) — the primary source for semantic-HTML accessibility guidance.
- [research/technologies/mui.md](../../research/technologies/mui.md), [research/technologies/shadcn-ui.md](../../research/technologies/shadcn-ui.md) — component-library accessibility framing.
- [research/technologies/playwright.md](../../research/technologies/playwright.md) — accessibility-aware testing locators.
