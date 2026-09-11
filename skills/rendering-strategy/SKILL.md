---
name: Rendering strategy
description: >-
  Choose how a page or app renders — CSR, SSR, SSG, ISR, or streaming SSR
  with partial/selective hydration — weighing SEO need, time-to-interactive,
  personalization, and infrastructure complexity. Use when deciding or
  reviewing how a page/app should render in a framework capable of more than
  one mode, or when a rendering choice has SEO/TTI consequences. Not for
  component/state architecture (frontend-architecture) or a specific
  framework's rendering-mode API/config mechanics once the mode is already
  decided (its own technology skill).
spec_version: "1.0"
---

## Purpose & scope

Choose the rendering mode for a page or app — CSR, SSR, SSG, ISR, or
streaming SSR with partial/selective hydration — independent of which
framework implements it. Component/state architecture belongs to
[frontend-architecture](../frontend-architecture/SKILL.md); each framework's
concrete mechanics for implementing the chosen mode (React's RSC
Server/Client Component split, Next.js's Cache Components/ISR APIs, Nuxt's
`routeRules`, Angular's per-route `RenderMode`) belong to that framework's
own technology skill. SEO implementation depth beyond the rendering-mode
tie-in (structured data, canonicalization, sitemaps, Core Web Vitals) belongs
to [seo-optimization](../seo-optimization/SKILL.md).

## When to use / When not to use

**Use** when a page/app's rendering mode is an open decision in a framework
capable of more than one mode, when a rendering choice has real SEO/TTI/
personalization consequences, or when reviewing an existing app for a
rendering-mode mismatch against its actual needs. **Do not use** for a pure
client-only SPA with no SEO/SSR concern and nothing actually open to decide,
while the framework/meta-framework choice itself is still open (that's
frontend-architecture), for a specific framework's rendering-mode API/config
once the mode is already decided (route to react/nextjs/vue/nuxt/angular),
or for backend-only work with no rendered page.

## Knowledge

**Rendering mode is fundamentally a question of *when* HTML is produced and
*when* the page becomes interactive — every mode is a different answer to
that pair of questions.** [Source:
research/knowledge-maps/concept-knowledge-map.md §C]

- **CSR (Client-Side Rendering):** the server ships a near-empty HTML shell
  plus a JS bundle; the browser builds the DOM after the bundle downloads
  and executes. Simplest infrastructure (a static host is enough), worst
  time-to-first-content, and the weakest default SEO story.
- **SSR (Server-Side Rendering):** the server renders full HTML per request,
  the browser paints it immediately, then client JS **hydrates** it.
  Documented SSR-by-default benefits: faster initial page load, improved SEO
  indexing, reduced client-side processing for low-powered devices, and
  easier server-side caching [Source:
  https://nuxt.com/docs/4.x/getting-started/introduction]. Cost: a live
  Node.js (or equivalent) server process is required — SSR is explicitly
  **not** deployable as static files, unlike SSG [Source:
  https://vuejs.org/guide/scaling-up/ssr.html].
- **SSG (Static Site Generation):** pages are pre-rendered to static HTML at
  *build* time and served from a CDN with no per-request render cost or
  server process. Best performance and infrastructure simplicity, at the
  cost of staleness between builds — it fits content that doesn't change
  per-request.
- **ISR (Incremental Static Regeneration):** SSG's staleness problem solved
  by regenerating a static page on a revalidation interval or on-demand
  after deploy, without a full rebuild — Next.js's ISR and Nuxt's `routeRules`
  `swr`/`isr` keys are two named implementations of this same idea
  [Source: https://nuxt.com/docs/4.x/guide/concepts/rendering].
- **Streaming SSR with partial/selective hydration:** rather than
  render-then-hydrate-everything-at-once, a static/cacheable shell is served
  immediately and the remaining content streams in behind `<Suspense>`-style
  boundaries as it becomes ready, with hydration applied progressively
  rather than all at once. Next.js's Cache Components/Partial Prerendering
  (static shell + Suspense-streamed dynamic content) [Source:
  https://nextjs.org/docs/app/getting-started/caching] and React Server
  Components (server-executed components that never ship their own code to
  the client, composed with client components that do) [Source:
  https://react.dev/reference/rsc/server-components] are two concrete,
  differently-shaped implementations of this pattern.
- **Hydration**, the mechanism every SSR/SSG/ISR/streaming mode above
  depends on: "the process that restores the server-side rendered
  application on the client," reusing existing DOM rather than re-rendering
  from scratch [Source: https://angular.dev/guide/hydration]. Hydration has
  a real cost proportional to the amount of interactive JS shipped — this is
  *why* streaming/partial-hydration approaches exist: to avoid paying the
  full hydration cost before any of the page is interactive.

**Rendering-choice and indexability are two ends of one mechanism, not two
separate concerns.** Google's crawl pipeline is Crawling → **Rendering**
(a distinct, queued step where a headless Chromium browser executes JS) →
Indexing of the **rendered** DOM, not the initial server response [Source:
https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics].
Googlebot does execute client-side JS, so a CSR-only page is not
automatically unindexable — but the render step is queued and can lag well
behind crawling, so CSR-only content is real SEO risk that must be stated
explicitly, not assumed safe just because "Google runs JS now."

**Not every framework exposes the same set of modes, and the framework
choice constrains which modes are actually on the table.** Angular's
`RenderMode` is configured **per-route** (`Server`/`Client`/`Prerender`)
[Source: https://angular.dev/guide/ssr]; Nuxt's default is **Universal
Rendering** (SSR + hydration) with `Client-Side Rendering` and per-route
**Hybrid Rendering** (`routeRules`) as alternatives [Source:
https://nuxt.com/docs/4.x/guide/concepts/rendering]. Confirm which modes the
chosen framework actually supports before recommending one it doesn't.

Full mode-by-mode trade-off table (TTI, SEO, infra cost, personalization
fit, and which frameworks expose it) is in
[references/rendering-mode-comparison.md](references/rendering-mode-comparison.md).

## Decision framework

1. **Does this page need anything beyond default CSR at all?** An
   internal tool, an authenticated dashboard with no SEO need and no
   first-paint sensitivity, or a genuinely simple SPA doesn't need SSR/SSG/
   ISR machinery — CSR is the simplest-sufficient answer and the correct
   default absent a stated reason otherwise. Don't reach for a
   meta-framework's rendering machinery "just in case."
2. **Does the page need to be indexed by search engines?** If yes, CSR-only
   is real risk (rendering is a queued, lag-prone step, not a guarantee) —
   SSR, SSG, ISR, or streaming SSR are all viable answers; pure CSR needs an
   explicit, stated justification, not a default.
3. **How often does the content actually change?** Static/rarely-changing →
   SSG. Changes periodically but not per-request → ISR (revalidate on an
   interval or on-demand). Genuinely per-request/per-user dynamic → SSR.
   Mixed within one app → streaming SSR/hybrid per-route rendering (most
   frameworks now support mixing modes per route rather than one app-wide
   choice).
4. **Is content personalized per-user?** Heavy personalization pushes
   toward SSR or streaming (render the personalized parts server-side or
   stream them in) over SSG/ISR, which assume the same output serves every
   visitor.
5. **What does time-to-interactive actually need to be, and how much
   interactive JS does the page ship?** A content-heavy, light-interactivity
   page benefits most from SSG/ISR (cheap to serve, little to hydrate); a
   highly interactive page pays real hydration cost regardless of mode —
   streaming/partial hydration exists specifically to avoid blocking
   interactivity on hydrating the whole tree at once.
6. **What infrastructure is actually available?** SSG needs only a static
   host/CDN. SSR, ISR-with-on-demand-revalidation, and streaming all need a
   live server runtime (or a platform, e.g. Vercel/Netlify, that provides
   one) — don't recommend SSR/ISR against a static-hosting-only constraint
   without flagging the infrastructure change it requires.
7. **Confirm the chosen framework actually exposes the recommended mode**,
   then hand off implementation to that framework's technology skill.

## Workflow

1. Confirm the framework/meta-framework choice is settled (hand off to
   frontend-architecture if not — a rendering mode can't be chosen
   independent of what the framework supports).
2. Gather per-page requirements: SEO need, content-change frequency,
   personalization level, interactivity/TTI sensitivity, available infra.
3. Apply the decision framework above, starting from "does this page need
   anything beyond CSR."
4. Where an app has genuinely different needs per route (e.g. a static
   marketing shell plus a dynamic dashboard), recommend a per-route mix
   rather than forcing one app-wide mode.
5. State the SEO/TTI/infrastructure trade-off explicitly for the
   recommendation, not just the mode name.
6. Hand off to the framework's own technology skill for the concrete
   implementation (React/Next.js/Vue/Nuxt/Angular).

## Engineering rules

- Default to CSR when nothing stated actually requires more — don't reach
  for SSR/SSG/ISR/streaming without a concrete SEO, TTI, or personalization
  driver.
- Never recommend CSR-only for a page with a real, stated SEO requirement
  without flagging the indexability risk explicitly.
- Match content-change frequency to the mode: static content doesn't need
  per-request SSR; genuinely per-request/per-user content doesn't fit SSG.
- Prefer a per-route mix over forcing one rendering mode across an entire
  app when different routes have genuinely different needs.
- Confirm the target framework actually supports the recommended mode
  before recommending it.
- Recommending SSR/ISR against a static-hosting-only infrastructure
  constraint requires flagging the infra change it forces.

## Trade-offs

CSR trades the worst default SEO/first-paint story for the simplest
infrastructure (a static host, no server runtime). SSR trades a live server
process and per-request render cost for the best per-request freshness and
personalization fit. SSG trades staleness between builds for the best raw
performance and lowest infrastructure cost. ISR is a middle ground —
SSG-level serving performance with bounded staleness — at the cost of
revalidation-logic complexity SSG/SSR don't have. Streaming SSR with partial
hydration recovers a fast, indexable first paint on pages that also need
real interactivity, at the cost of the most complex mental model (Suspense
boundaries, static/dynamic shell separation) of any mode here.

## Anti-patterns

- **Reaching for SSR/ISR/streaming infrastructure for a page with no SEO,
  TTI, or personalization need that justifies it** — the domain's
  over-engineering trap; default build-time prerendering or plain CSR
  already covers that case for free.
- **Assuming Googlebot's ability to execute JS makes CSR-only "safe" for
  SEO** without weighing that rendering is a distinct, queued, lag-prone
  step, not an instant equivalent to server-rendered HTML.
- **Forcing one app-wide rendering mode** when different routes have
  genuinely different content-volatility/interactivity/SEO profiles instead
  of mixing modes per route.
- **Recommending a rendering mode the chosen framework doesn't actually
  expose**, or without checking which modes it supports.
- **Treating hydration cost as fixed regardless of mode** — shipping the
  full interactive bundle to hydrate at once on a page that could have used
  streaming/partial hydration to defer non-critical interactivity.
- **Recommending SSR/ISR without flagging that it requires a live server
  runtime**, against an infrastructure constraint that only supports static
  hosting.

## Security

Server-rendered pages commonly pass initial data into the client as
serialized props/state embedded in the HTML response — this is a real,
common vector for accidentally leaking server-only data (internal IDs,
unfiltered database fields, secrets) to the client if the rendering layer
doesn't explicitly filter what crosses the server→client boundary. Any
rendering-mode recommendation that involves passing server-fetched data into
client-rendered/hydrated output should flag this boundary explicitly. Deep
threat modeling and secret handling are owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Rendering mode is one of the largest levers on Core Web Vitals: SSG/ISR
serve pre-built HTML from a CDN with effectively no server-side render cost
per request; SSR pays a real per-request render cost server-side; CSR pays
the full render cost client-side after the JS bundle downloads and
executes, which is the worst starting point for both first paint and TTI.
Streaming SSR with partial hydration is the documented lever for decoupling
"first paint" from "fully hydrated and interactive" so a page doesn't have
to block one on the other [Source:
https://nextjs.org/docs/app/getting-started/caching]. Deep performance
measurement/optimization method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

Hydration mismatches (server-rendered markup that doesn't match what the
client would render) are the characteristic bug class of every SSR/SSG/ISR/
streaming mode — verify against the actual rendered/hydrated DOM, not just
that the server response looks correct, and check for the framework's
documented mismatch causes (non-deterministic values rendered server-side,
invalid HTML nesting the browser silently "fixes," timezone-dependent
formatting) before treating a rendering-mode implementation as done. Verify
the resulting Core Web Vitals (LCP/INP/CLS) rather than assuming the chosen
mode delivers the expected numbers. Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If per-page requirements (SEO need, content volatility, interactivity)
  aren't stated, ask rather than assuming a mode.
- If the framework/meta-framework choice is still open, hand off to
  frontend-architecture first.
- If the target framework's exact rendering-mode API isn't known, state the
  recommended mode and rationale, and hand off implementation specifics to
  that framework's technology skill rather than guessing its API.

## Escalation

- Changing an existing production app's rendering mode (e.g. CSR→SSR, or
  adding ISR) is an infrastructure change, not just a code change — present
  it with the infra/deployment trade-off for explicit confirmation before
  applying it.

## Outputs & verification

- **Outputs:** a rendering-mode recommendation (or a per-route mix) with
  SEO/TTI/infrastructure rationale, handed off to the relevant framework
  technology skill for implementation.
- **Verify:** the recommendation is justified against the page's actual
  requirements, not chosen by default; a CSR-only recommendation for an
  SEO-relevant page states the indexability risk explicitly; the
  simplest-sufficient mode is recommended before reaching for ISR/streaming
  machinery a page doesn't need.

## References

- [references/rendering-mode-comparison.md](references/rendering-mode-comparison.md) — Tier-2 full mode-by-mode comparison table.
- [research/knowledge-maps/concept-knowledge-map.md](../../research/knowledge-maps/concept-knowledge-map.md) §C — cross-framework rendering-concept sourcing.
- [research/technologies/google-seo.md](../../research/technologies/google-seo.md) — crawl/render/index pipeline.
- [research/technologies/nextjs.md](../../research/technologies/nextjs.md), [research/technologies/nuxt.md](../../research/technologies/nuxt.md), [research/technologies/vue.md](../../research/technologies/vue.md), [research/technologies/angular.md](../../research/technologies/angular.md), [research/technologies/react.md](../../research/technologies/react.md) — per-framework rendering-mode sourcing (mechanics owned by each framework's own technology skill).
- Source list: see `skill.yaml.source_references`.
