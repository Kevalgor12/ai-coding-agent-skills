# Frontend framework & meta-framework comparison (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Condensed from
[technology-decision-matrix.md §4 and §5](../../../research/knowledge-maps/technology-decision-matrix.md)
— consult that document for the full citation trail.

## React vs. Vue vs. Angular

| | React | Vue | Angular |
|---|---|---|---|
| Reactivity model | Hooks (`useState`, position-in-render-tree) | Proxy-based automatic dependency tracking | Signals (`signal()`/`computed()`/`effect()`) |
| Default XSS mitigation | None named beyond standard JSX escaping; `dangerouslySetInnerHTML` is the documented primary vector | Automatic HTML-escaping of interpolations/bindings; `v-html` is the explicit bypass | Auto-sanitizes all template bindings by security context by default |
| Built-in CSRF/XSRF handling | Not addressed (no HTTP client) | Framed as a backend responsibility | `HttpClient` includes CSRF protection by default via an interceptor |
| Critical recent CVE | CVE-2025-55182 (CVSS 10.0, RSC RCE, React 19.0–19.2.0) + follow-up CVE-2026-23864 | None reported in the source data | None reported in the source data |
| Compiler/optimization | React Compiler (stable v1.0, Oct 2025): auto-memoization | Compiler-informed VDOM: static hoisting, Patch Flags, Tree Flattening; accelerates SSR hydration | Zoneless change detection (stable/default v21+); v22+ defaults undecorated components to `OnPush` |
| Default/recommended unit-test runner | No official recommendation; `react-test-renderer` deprecated | Vitest (Vue/Vite team-maintained) | Vitest is now the default for new CLI projects (v21+), replacing Karma |
| Recommended E2E tool | Not prescribed | Playwright or Cypress | Playwright or WebdriverIO |

**Unresolved (per source research):** no direct official statement from any
of the three compares its own performance/bundle size numerically against
either of the others — every performance claim is self-referential.

## Next.js vs. Nuxt

| | Next.js (React) | Nuxt (Vue) |
|---|---|---|
| Framework relationship claim | Documents an official Vite→Next.js migration guide | No official comparison to Next.js exists; the entry is an inference from feature-set similarity |
| Default rendering | App Router (RSC) + Pages Router coexist | "Universal Rendering" (SSR + hydration) default, plus Client-Side/Hybrid modes |
| Per-route caching | Cache Components model (`"use cache"` + Suspense) → Partial Prerendering | `routeRules` (`swr`/`isr`/`prerender`/`ssr:false`); unavailable when output is via static `nuxt generate` |
| Major coordinated security release | May 2026: 13 advisories, affects all Next.js 13–14 with no direct patch, forces upgrade to 15.5.18+/16.2.6+ | v4.5 security post: 4 named advisories incl. a dev-only Critical RCE over the Vite HMR socket |
| Officially documented unit-test tools | Jest and Vitest both first-party-documented, plus Cypress and Playwright | Vitest-only for the Nuxt runtime environment; E2E supports Vitest/Jest/Cucumber/Playwright |
| Documented testing constraint | Async Server Components: docs recommend E2E over unit testing as a workaround | Nuxt-runtime tests and E2E-style tests cannot coexist in the same file |

**Unresolved (per source research):** because the Next.js↔Nuxt pairing
itself is an inference rather than a documented alternative, there is no
head-to-head statement on which is "better" for a given use case.
