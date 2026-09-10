---
name: Frontend architecture
description: >-
  Structure a frontend application — components, state management, data
  flow, routing — and choose a framework (React/Vue/Angular, and a
  meta-framework on top) when that choice is open. Use when building or
  structuring a frontend app or feature. Not for styling specifics,
  accessibility depth, or the SSR/SSG rendering-mode decision.
spec_version: "1.0"
---

## Purpose & scope

Structure how a frontend application is put together — components, state
management, data flow, routing — and choose a framework when that's still
open. Styling specifics belong to styling-systems (not yet authored),
accessibility depth to [web-accessibility](../web-accessibility/SKILL.md),
and the SSR/SSG rendering-mode decision to rendering-strategy (not yet
authored).

## When to use / When not to use

**Use** when building or structuring a frontend application or non-trivial
feature, or when a framework/meta-framework choice is genuinely open. **Do
not use** for pure styling with structure already settled, backend-only
work, or a purely technology-specific question once the framework is fixed.

## Knowledge

**React, Vue, and Angular make different default security trade-offs, not
just different syntax** [Source: technology-decision-matrix.md §4]. Vue
auto-escapes `{{ }}` interpolations and dynamic attribute bindings with no
developer action needed (`v-html` is the explicit, documented bypass, "never
on user-provided content"). Angular auto-sanitizes all template bindings by
security context (HTML/Style/URL/Resource URL) by default, and its
`HttpClient` includes CSRF protection out of the box via an interceptor
reading the `XSRF-TOKEN` cookie. React has **no built-in auto-escaping
mechanism called out as a named security feature** — `dangerouslySetInnerHTML`
is the documented primary XSS vector, and mitigating it is framed entirely as
the developer's responsibility. This is a genuine, documented
security-posture difference worth weighing, not incidental.

**A critical, real CVE affects React specifically.** CVE-2025-55182 (CVSS
10.0, unauthenticated RCE) hit RSC Server Function payload deserialization in
React 19.0–19.2.0, affecting downstream frameworks including Next.js — and a
follow-up patch was itself incomplete, requiring a second CVE
(CVE-2026-23864) [Source: technology-decision-matrix.md §4;
version-matrix.md React]. If a codebase uses React Server Components, verify
the patched version is actually in use (fixed in 19.0.1/19.1.2/19.2.1 for the
first CVE, 19.0.4/19.1.5/19.2.4 for the follow-up) rather than assuming any
React 19.x is safe.

**Next.js and Nuxt's relationship to each other is inferred, not
documented** [Source: technology-decision-matrix.md §5] — Nuxt's own docs
make no official comparison to Next.js; the pairing exists because Nuxt's
feature set mirrors what Next.js does for React (SSR-by-default, file-based
routing, hybrid rendering, built-in API routes), not because either
vendor states it. Both had major coordinated security releases in this
project's research window — Next.js's May 2026 release patched 13 advisories
across all of Next.js 13–14 with **no direct patch**, forcing upgrade to
15.5.18+/16.2.6+; Nuxt's v4.5 security post named four advisories including a
dev-only Critical RCE over the Vite HMR socket.

**Compiler/optimization stories now genuinely differ in kind, not just
degree.** React Compiler (stable v1.0, Oct 2025) auto-memoizes; Vue's
compiler does static hoisting/Patch Flags/Tree Flattening and accelerates
SSR hydration; Angular's zoneless change detection (stable/default v21+, with
v22+ defaulting undecorated components to `OnPush`) removes Zone.js
monkey-patch overhead entirely [Source: technology-decision-matrix.md §4].
None of these have a documented head-to-head number against each other —
each framework only benchmarks against its own prior version.

Full React/Vue/Angular and Next.js/Nuxt comparison tables are in
[references/framework-comparison.md](references/framework-comparison.md).

## Decision framework

1. **Is a framework already in place?** Work within it unless the user
   explicitly asks to evaluate a switch.
2. **What does the security-posture default need to be?** A team that can't
   guarantee XSS discipline benefits more from Vue/Angular's auto-sanitizing
   defaults than from React's developer-responsibility model — this is a
   real, documented differentiator, not a style preference.
3. **Does the app need SSR/SSG/hybrid rendering, and for what reason
   (SEO, initial-load performance)?** If yes, a meta-framework
   (Next.js on React, Nuxt on Vue) is likely warranted — the base framework
   choice should usually come first, since the meta-framework follows from it.
4. **What does the team already know, and is there an existing
   organizational stack to stay consistent with?** Switching costs are real;
   weigh them against the security/tooling differentiators above rather than
   defaulting to whichever is most familiar without checking.
5. **Component boundaries should track real reuse/ownership seams** — a
   different data source, a different update frequency, a genuinely reusable
   unit — not arbitrary size limits.
6. **State scope should match actual sharing need**: local state for
   component-only concerns, lifted/shared state only where multiple
   components genuinely need it, global state only for truly
   cross-cutting concerns (auth, theme) — not by default.

## Workflow

1. Confirm whether a framework choice is open; if not, work within the existing one.
2. If open, apply the decision framework and record the trade-off, citing the React/Vue/Angular comparison where relevant.
3. Decide whether a meta-framework is warranted (SSR/SSG/SEO need).
4. Decompose components around real reuse/ownership boundaries.
5. Choose state-management scope per actual sharing need.
6. Design data-fetching and routing structure.
7. Hand off styling to styling-systems, accessibility depth to web-accessibility, and rendering-mode specifics to rendering-strategy.

## Engineering rules

- Don't default to a framework without checking its documented security posture against the app's actual risk profile.
- Verify a patched version is in use before assuming a framework/library version is safe, especially for named CVEs.
- Match state scope to actual sharing need; don't default to a global store.
- Component boundaries reflect real seams, not arbitrary splitting.
- Don't propose a framework switch unasked.

## Trade-offs

React's flexibility and ecosystem size trade against having to build XSS
discipline into process rather than getting it from the framework. Vue's and
Angular's stronger security/structure defaults trade against more opinionated
patterns that can feel restrictive for highly custom UIs. Meta-frameworks
(Next.js/Nuxt) trade added build/deployment complexity for SEO and
initial-load wins that a pure SPA doesn't get for free.

## Anti-patterns

- **Assuming React's JSX escaping is equivalent to Vue's/Angular's named
  auto-sanitization features** — it isn't documented as an equivalent
  framework-level security control.
- **Running an old React 19.x pinned before the RSC CVE fixes** without checking the patched version.
- **Global state for everything** — the domain's most common structural drift, adding unnecessary coupling and re-render surface.
- **Over-decomposing components** below any real reuse/ownership seam — the domain's overengineering trap.
- **Adding a meta-framework "for SEO" without an actual SEO requirement** — the added complexity should be justified by a real need.

## Security

React has no built-in auto-escaping mechanism named as a security feature;
`dangerouslySetInnerHTML` is the documented primary XSS vector, mitigated
only by developer discipline. Vue and Angular both auto-sanitize by default.
Verify patched versions for named CVEs (React's RSC deserialization CVEs;
Next.js's May 2026 and Nuxt's v4.5 coordinated security releases) [Source:
technology-decision-matrix.md §4, §5]. Deep threat modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Compiler-driven auto-optimization now exists in some form across all three
frameworks (React Compiler, Vue's Patch Flags/Tree Flattening, Angular's
zoneless change detection) — each framework's own vendor-reported numbers are
directional, not comparative. Deep performance method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

No official recommendation exists from React itself for a unit-test runner —
the closest is a deprecation-warning page pointing to
`@testing-library/react`, with `react-test-renderer` explicitly deprecated.
Vue recommends Vitest ("created and maintained by members of the Vue/Vite
team"). Angular defaults new CLI projects to Vitest as of v21+, replacing
Karma [Source: technology-decision-matrix.md §4]. Deep test-strategy method
is owned by [testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If requirements are too thin for a framework decision, request them or hand off to requirements-engineering.
- If a framework is already in place, work within it unless a switch is explicitly requested.

## Escalation

- A framework/meta-framework switch for an existing production app is a
  significant, hard-to-reverse decision — presented with trade-offs for
  explicit confirmation, never applied unilaterally.

## Outputs & verification

- **Outputs:** a framework/meta-framework recommendation with trade-offs
  (when open), and a component/state/data-flow/routing structure.
- **Verify:** component boundaries reflect real seams; state scope matches
  actual sharing need; any framework recommendation cites real,
  research-backed differentiators.

## References

- [references/framework-comparison.md](references/framework-comparison.md) — Tier-2 full comparison tables.
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
