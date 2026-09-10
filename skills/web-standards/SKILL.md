---
name: Web Standards (HTML & CSS)
description: >-
  HTML document structure, the DOM data model, and Custom Elements/DOM
  APIs, plus CSS cascade, specificity, box model, layout, custom
  properties, and modern at-rules (@container, @property, @layer, native
  nesting) with Baseline-availability awareness. Use for raw HTML/CSS
  platform mechanics. Not for accessibility semantics (use
  web-accessibility), styling-architecture decisions like design tokens or
  utility-first vs. component CSS (use styling-systems), or Sass/Tailwind
  syntax (use those skills).
spec_version: "1.0"
---

## Purpose & scope

Apply HTML document structure/DOM APIs and CSS cascade/layout/theming
mechanics correctly and version-appropriately. This is **HTML+CSS
technology knowledge** — the foundational, almost-always-co-present
web-platform primitives underneath any frontend framework, component
library, or CSS methodology (hence the merge into one skill; see
`core/taxonomy/taxonomy-analysis.md`). Two boundaries matter: **accessibility-
specific** guidance (semantic-HTML-for-a11y, alt text, heading hierarchy,
table markup) is owned by `web-accessibility` (`SK-FE-004`) and only
referenced here, not repeated; **styling-architecture** decisions (design
tokens, utility-first vs. component CSS, CSS-in-JS) belong to
`styling-systems` (`SK-FE-003`), which is not yet authored in this library
— forward-referenced, not fabricated.

## When to use / When not to use

**Use** when authoring or reviewing raw HTML document structure/DOM usage,
or CSS selectors/cascade/box-model/layout/custom-properties/modern
at-rules, independent of a specific framework or preprocessor — including
deciding whether a modern CSS feature's Baseline status is safe to ship.
**Do not use** for: accessibility semantics (alt text, ARIA, heading
hierarchy — use `web-accessibility`); styling-architecture/design-system
decisions (tokens, utility-first vs. component CSS, choosing among
Sass/Tailwind/CSS-in-JS — use `styling-systems`); Sass-specific
(`@use`/`@forward`, mixins) or Tailwind-specific (utility classes, config)
syntax (use those tech skills); or backend/non-UI work.

## Knowledge

**HTML is a Living Standard, not a versioned release.** The 2019
WHATWG/W3C agreement established the WHATWG HTML Living Standard as the
single authoritative spec, replacing the earlier versioned "HTML5/5.1/5.2"
W3C Recommendations; there is no discrete "HTML6" to target [Source:
whatwg.org/faq]. HTML is described in the spec itself as "a semantic-level
markup language and associated semantic-level scripting APIs for authoring
accessible pages... from static documents to dynamic applications" [Source:
html.spec.whatwg.org/multipage/introduction.html].

**Document data model: the DOM.** Every HTML document is represented as a
`Document` object — a tree of nodes/elements, with `document.head` /
`document.body` as structural access points and per-element interfaces
(`HTMLElement`, and subtypes like `HTMLInputElement`, `HTMLAnchorElement`)
exposed to script [Source: html.spec.whatwg.org/multipage/dom.html]. The
parser is **error-tolerant by specification**, not by accident: malformed
markup (misnested tags, missing attributes) has precisely defined recovery
behavior (e.g. the "adoption agency algorithm" for `<b><i></b></i>`), so
all conforming browsers produce the same DOM from the same invalid markup
[Source: html.spec.whatwg.org/multipage/parsing.html].

**Custom Elements extend the DOM.** `customElements.define(name,
constructor)` registers either standalone "autonomous" custom elements
(hyphenated tag names, e.g. `<flag-icon>`) or, via `extends`, "customized
built-in elements" that inherit a native element's semantics. Lifecycle
callbacks (`connectedCallback`, `disconnectedCallback`,
`attributeChangedCallback`, `adoptedCallback`, `formAssociatedCallback`)
are deliberately delayed until "just before returning to user script" for
safe DOM-operation ordering [Source:
html.spec.whatwg.org/multipage/custom-elements.html]. This is the
documented extension point most JS frameworks/design systems use to add
first-class custom tags.

**Obsolete HTML has documented replacements** — don't author these even
where browsers still render them for legacy compatibility: `applet` →
`embed`/`object`; `frame`/`frameset` → `iframe` + CSS; `center`/`font`/
`big`/`tt`/`marquee`/`blink` → CSS; `acronym` → `abbr`; `keygen` → the Web
Cryptography API [Source: html.spec.whatwg.org/multipage/obsolete.html].

**CSS is module-based, not versioned as a whole.** Since CSS3, CSS is
developed as independently-versioned modules (Selectors, Cascade, Flexbox,
Grid, Color, Nesting, Containment, ...) rather than one "CSS Level 4." The
CSSWG's annual **CSS Snapshot** Group Note (2018/2023/2024/2025/2026
editions identified) is the closest thing to an official "current CSS"
reference, aimed at implementers, not authors [Source: w3.org/TR/css-2026/].
Practical "is this safe to use" versioning instead comes from MDN's
**Baseline** system: *widely available* (consistent support ≥2.5 years),
*newly available* (works in the latest stable Baseline browsers, may break
on older ones), *limited availability* (not yet supported everywhere)
[Source: developer.mozilla.org/en-US/docs/Glossary/Baseline/Compatibility].

**The cascade resolves conflicts in five ordered steps**: (1) relevance —
does the selector match and does the `@media`/conditional context apply;
(2) origin and importance — author beats user beats user-agent for
non-`!important`, reversed for `!important`, with CSS transitions ranked
above even `!important` and animations just below `!important` author
rules; (3) specificity; (4) scoping proximity (`@scope`, fewer DOM hops
wins on a specificity tie); (5) source order, last declaration wins
[Source: developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Cascade].
**Specificity** is a three-column (ID, CLASS, TYPE) weight compared
left-to-right — IDs are 1-0-0, classes/attributes/pseudo-classes are
0-1-0, types/pseudo-elements are 0-0-1, `*` and combinators contribute
nothing, inline `style=""` outranks all three columns. `:where()` always
contributes 0-0-0; `:is()`/`:not()`/`:has()` take the specificity of their
highest-specificity argument [Source:
developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity].

**The box model**: `box-sizing: content-box` (default) sizes only the
content box, so padding/border add to the declared width/height;
`box-sizing: border-box` makes the declared width/height include
padding+border [Source:
developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/box-sizing].

**Custom properties** (`--name: value`) participate in the cascade and
inherit like normal properties; read via `var(--name, fallback)`. `var()`
is valid only in property *values* — not in selectors, property names, or
media-/container-query conditions [Source:
developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascading_variables/Using_custom_properties].

**Modern CSS features and their Baseline status** (verify against current
MDN compat tables before relying on this table — Baseline status changes
over time):

| Feature | Baseline status | Since | Notes |
|---|---|---|---|
| `box-sizing: border-box` | Widely available | July 2015 [Source: css.md/box-sizing] | Safe as a universal reset. |
| `will-change` | Widely available | January 2020 [Source: css.md/will-change] | Safe, but use sparingly (see Anti-patterns). |
| `@container` (container queries) | Widely available | February 2023 [Source: css.md/@container] | Requires `container-type` on the queried ancestor first. |
| `@property` | **Newly available** | July 2024 [Source: css.md/@property] | Recent — expect gaps on older browsers; not yet safe for broad production use without a fallback. |
| CSS Nesting Module Level 1 | Comparatively new | MDN page flagged "last update November 2025" [Source: css.md/CSS_nesting] | Check current compat tables before production use. |

## Decision framework

1. **Native CSS Nesting vs. a preprocessor (Sass):** now that nesting has
   browser support, native nesting removes a build step for projects that
   used Sass/Less *only* for nesting. But: (a) nesting changes how
   specificity is calculated relative to flattened rules — a real porting
   gotcha, not just syntax [Source: developer.mozilla.org/en-US/docs/Web/CSS/CSS_nesting];
   (b) if the project already needs Sass for other features (mixins,
   `@use`/`@forward` modules — see `SK-TECH-sass`), dropping the
   preprocessor just for nesting is not worth the churn. Simplest-first: if
   nesting is the *only* reason for the preprocessor and the target
   browsers support it, go native; otherwise keep the preprocessor.
2. **Is a "newly available" Baseline feature safe to ship?** `@property`
   (newly available since July 2024) is not yet safe for broad production
   use without an `@supports`-gated fallback or acceptance that older
   browsers silently lose the enhancement — check the project's actual
   browser-support requirements before using it unconditionally [Source:
   developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@property].
   Widely-available features (`box-sizing`, `will-change`, `@container`)
   need no such gate.
3. **`!important` vs. cascade layers (`@layer`) for precedence fights:**
   MDN's own guidance frames heavy `!important` use as a workaround and
   recommends `@layer` for maintainable precedence control, with
   `:where()` to give reset/third-party CSS zero added specificity
   [Source: developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity].
   Reach for `@layer` before reaching for `!important` chains.
4. **Do nothing / simplest option:** for a single specificity conflict, the
   simplest fix is usually reordering source rules or lowering one
   selector's specificity — not `!important`, not a new cascade layer,
   not a rewrite.

## Engineering rules

- Emit a correct `<!DOCTYPE html>` and `<meta charset="utf-8">` early in
  `<head>` (within the parser's ~1024-byte prescan window) to avoid
  quirks-mode rendering and encoding-detection failures [Source:
  html.spec.whatwg.org/multipage/syntax.html#the-doctype; html.spec.whatwg.org/multipage/parsing.html].
- Serve HTML with an explicit `Content-Type: text/html; charset=utf-8`
  header — content sniffing cannot substitute for it ("no sequence of
  bytes can uniquely identify an HTML document") [Source:
  html.spec.whatwg.org/multipage/iana.html].
- Don't author obsolete elements/attributes even where browsers still
  render them for legacy pages; use the documented replacement (see
  Knowledge).
- Read the actual cascade order before reaching for `!important`; prefer
  `@layer` for precedence control [Source:
  developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity].
- Tag any "newly available" or "limited availability" Baseline feature
  with its status and a fallback plan; never assert unconditional browser
  support.
- Use `content-visibility: auto` for long, chunked off-screen content
  instead of `display: none` when the content should remain in the
  accessibility tree and searchable (see Performance).

## Trade-offs

- Native CSS Nesting removes a build step but is newer than the preprocessor
  ecosystem it's replacing and changes specificity math relative to
  flattened rules — a real migration cost for existing Sass/Less codebases,
  not a free swap.
- `@layer` centralizes precedence control but adds a layer-ordering concept
  every contributor must understand; for a small stylesheet with few
  precedence conflicts, plain source-order + specificity may be simpler
  and not worth introducing layers for.
- `content-visibility: auto` buys large rendering-cost savings on long
  pages but requires the content to genuinely be off-screen/chunkable;
  applying it to already-short pages adds complexity for no measurable
  gain.

## Anti-patterns

- **Relying on a Baseline-"newly available" feature (e.g. `@property`)
  without a fallback or an explicit "may not work on older browsers"
  caveat** — the domain's central version-awareness trap [Source:
  developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@property].
- **Overusing `will-change`** — applying it broadly (e.g. to `<body>`) or
  leaving it applied indefinitely "results in excessive memory consumption
  and makes rendering more complex than necessary," the opposite of its
  intent; also don't set it inside `@keyframes` (animated properties are
  already implicitly treated as changing) — the domain's over-engineering
  trap: applying a targeted last-resort fix proactively [Source:
  developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/will-change].
- **`!important` chains / specificity wars** as a substitute for `@layer`
  or simpler selectors — inverts and complicates the cascade [Source:
  developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity].
- **Inline `style=""` as the default styling mechanism** — MDN
  "strongly discourages" it outside narrow cases (restrictive CMS,
  HTML-email compatibility, JS-driven dynamic styling); it mixes
  presentation into markup and can't be reused [Source:
  developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Getting_started].
- **Presentational HTML markup** (`<center>`, `<font>`, `align`,
  `bgcolor`, etc.) instead of CSS — explicitly discouraged by the spec
  itself, not just a style preference [Source:
  html.spec.whatwg.org/multipage/introduction.html].
- **Porting nested Sass/Less rules to native CSS Nesting without checking
  specificity** — nesting changes specificity calculation relative to the
  flattened output a preprocessor would have produced [Source:
  developer.mozilla.org/en-US/docs/Web/CSS/CSS_nesting].

## Security

**HTML's primary documented risk is XSS** via sinks that interpret a
string as markup: `Element.innerHTML`/`outerHTML`,
`insertAdjacentHTML()`, `Document.write()`. Unquoted/unescaped attribute
interpolation is a distinct vector (event-handler attributes like
`onblur` are especially unsafe) [Source:
developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS]. Documented
layered defenses, in order: output-encode via a templating engine; always
quote interpolated attribute values; sanitize any HTML that must be
inserted (MDN names **DOMPurify**, or the browser's **HTML Sanitizer
API**); enforce **Trusted Types** (CSP `require-trusted-types-for`) so
unsafe sinks only accept sanitizer output; layer a strict **CSP** to
disallow inline handlers/`javascript:` URLs as defense-in-depth [Source:
developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS;
developer.mozilla.org/en-US/docs/Web/API/HTML_Sanitizer_API]. The `nonce`
content attribute is specified so the cryptographic nonce is exposed only
to script, "not to side-channels like CSS attribute selectors" — a
documented CSS-side-channel mitigation [Source:
html.spec.whatwg.org/multipage/urls-and-fetching.html].

**CSS's own documented privacy issue is `:visited` history sniffing**: a
page could once probe computed styles or layout to detect visited links.
Browsers mitigate this by making `getComputedStyle()` report as if the
link were unvisited, and by restricting which properties `:visited` rules
may affect (broadly `color`, `background-color`, `border-color`,
`outline-color`) — production stylesheets styling `:visited` links are
confined to that limited set; layout-affecting properties on `:visited`
simply won't take effect, by design [Source:
developer.mozilla.org/en-US/docs/Web/CSS/Guides/Selectors/Privacy_and_:visited].
Deeper application-security threat modeling (injection, secrets,
transport) is cross-cutting and owned elsewhere in this library, not
restated here.

## Performance

`content-visibility: auto` builds on CSS **containment** to let the
browser skip layout/paint for off-screen content while keeping it in the
DOM and accessibility tree (unlike `display: none`/`visibility: hidden`),
so it stays searchable/navigable; web.dev's own demos report **up to a 7x
rendering-performance improvement on initial load** for long, chunked
pages [Source: web.dev/articles/content-visibility;
developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Using].
`@container` queries require `container-type` on the queried ancestor
first — itself a containment-driven performance mechanism, not just a
layout convenience [Source:
developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@container].
On the HTML side, `loading="lazy"` (default `eager`) defers below-the-fold
`img`/`iframe` fetches, and `fetchpriority="high"|"low"|"auto"` signals
relative resource priority to the browser's scheduler — both are formally
specified, individually controllable attributes rather than implicit
behavior [Source: html.spec.whatwg.org/multipage/urls-and-fetching.html].

## Testing

**HTML markup**: the W3C **Nu Html Checker** validates syntax, parsing/
error-recovery problems, and content-model violations via web UI,
bookmarklet, CLI, or Grunt/Gulp — but its own docs are explicit it "should
not be used as a means to attempt to unilaterally enforce pass/fail
conformance," and a zero-error result today is not a durable guarantee as
its rule set expands over time [Source:
validator.w3.org/nu/about.html]. (`web-accessibility` already covers this
tool for accessibility-flagged errors specifically; here it's cited for
general markup conformance, to avoid pure duplication.)

**CSS**: the CSS Working Group's own conformance suite lives in
**web-platform-tests (WPT)**, primarily under `css/` — short, self-contained
HTML pages that verify *browser implementations* match the spec. This is
**browser-conformance testing, not application testing**: it tells you
whether a browser correctly implements a CSS feature, not whether your
stylesheet is correct [Source: web-platform-tests.org/test-suite-design.html].
For authored CSS, MDN's own guidance points to the **W3C CSS Validator**
to catch syntax errors, since invalid CSS is otherwise silently discarded
rather than raising a visible error [Source:
developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Debugging_CSS].
No official unit/visual-regression-testing methodology for authored CSS
is documented by MDN/CSSWG — that space is filled by third-party tooling,
out of scope for this skill's official-sources grounding.

## Failure handling

- If a feature's current Baseline/browser-support status cannot be
  confirmed as current, state "verify against current Baseline/MDN compat
  tables" rather than asserting support — applies especially to
  `@property` and CSS Nesting, both flagged as recent in this skill's
  research pass.
- If the task is actually an accessibility concern, defer to
  `web-accessibility` (`SK-FE-004`) rather than restating its content.
- If the task is a styling-architecture decision beyond raw CSS mechanics,
  state that `styling-systems` (`SK-FE-003`) — not yet authored in this
  library — owns that decision.

## Escalation

None specific to this skill beyond the failure-handling routing above;
legal/compliance accessibility requirements are escalated by
`web-accessibility`, not duplicated here.

## Outputs & verification

- **Outputs:** HTML structure or CSS rules reflecting correct document/
  DOM/cascade/layout usage and Baseline-aware feature choices; analysis of
  document-structure, DOM-API, or CSS-mechanics decisions with version/
  Baseline caveats stated.
- **Verify:** every Baseline-availability claim is tagged with its
  applicable date/range; HTML uses a correct DOCTYPE/charset/Content-Type
  and avoids obsolete elements; CSS cascade/specificity reasoning is
  correct and doesn't reach for `!important` where `@layer` or a simpler
  selector would do; no accessibility-specific or styling-architecture
  content is restated rather than referenced.

## References

- Source list: see `skill.yaml.source_references` (WHATWG HTML Living
  Standard and MDN/W3C CSS docs, retrieved 2026-09-10, via
  `research/technologies/html.md` and `research/technologies/css.md`).
- [`skills/web-accessibility/SKILL.md`](../web-accessibility/SKILL.md) —
  owns semantic-HTML-for-accessibility, alt text, heading hierarchy, table
  markup; referenced, not repeated, here.
- `core/taxonomy/taxonomy-analysis.md` — the HTML+CSS merge rationale for
  this skill.
