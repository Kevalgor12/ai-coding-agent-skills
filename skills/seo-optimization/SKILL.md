---
name: SEO optimization
description: >-
  Improve search visibility — ensure crawlability/indexability, implement
  structured data, set canonical URLs, meet Core Web Vitals thresholds,
  build sitemaps, and use hreflang for i18n. Use when search visibility
  matters for the work. Covers Next.js-specific SEO mechanics (Metadata
  API, sitemap/robots generation) where researched. Not for internal
  tools or non-public apps.
spec_version: "1.0"
---

## Purpose & scope

Improve search visibility across crawlability, structured data,
canonicalization, Core Web Vitals, sitemaps, and hreflang. Google is the
dominant search engine in this library's research, so this generic skill
and Google-SEO technical content are one skill rather than a split
generic-plus-technology pair. Framework-specific mechanics (Next.js's
Metadata API, sitemap/robots generation) are covered here where the
research supports them — **honestly thin on that specific angle**: Next.js's
own production checklist names "use the Metadata API, generate Open Graph
images, and generate sitemaps/robots files" in one line, plus the
`generateMetadata()`/`generateSitemaps()` function names — not a deep,
independently-researched Next.js-SEO methodology. Core Web Vitals
implementation depth itself is owned by
[performance-engineering](../performance-engineering/SKILL.md); the
rendering-mode decision is owned by rendering-strategy (not yet
authored).

## When to use / When not to use

**Use** when search visibility matters for the work — a public-facing
page or site, structured data/canonicalization/sitemap/hreflang work, a
JS-rendered page's crawlability is in question, or Core Web Vitals
thresholds are relevant. **Do not use** for internal tools or non-public
apps with no search-visibility need.

## Knowledge

**Google Search is a three-stage, sequential pipeline, and understanding
the sequencing explains most JS-SEO bugs.** Crawling (Googlebot fetches
the URL and checks robots.txt) → Rendering (a headless Chromium browser
executes JavaScript, on a separate, queued step) → Indexing (Google
indexes the **rendered** HTML — the post-JS DOM — not the initial server
response) [Source: developers.google.com/search/docs/crawling-indexing/
javascript/javascript-seo-basics]. Rendering being a distinct, queued step
means there can be a real delay between a page being crawled and its
JS-rendered content being indexed — "fetched" and "rendered" HTML can
differ, which is the underlying cause of most JS-SEO bugs. **Indexing is
never guaranteed** — Google explicitly disclaims that meeting all
technical requirements guarantees crawling, indexing, or ranking
[Source: developers.google.com/search/docs/essentials].

**robots.txt and `noindex` solve different problems, and conflating them
is a real, common mistake.** robots.txt blocking prevents *crawling*
outright — so Google can't even see a `noindex` directive on a blocked
page. `noindex` (meta tag or `X-Robots-Tag` header) prevents *indexing*
while still allowing crawling. Critically: **"a page that's disallowed in
robots.txt can still be indexed if linked to from other sites"** — robots.txt
is not a reliable content-hiding mechanism, its own docs state this
plainly [Source: developers.google.com/search/docs/crawling-indexing/
robots/intro].

**Canonical signals are a hint Google weighs, not an enforced rule — a
site owner's stated preference can be overridden.** When Google finds
duplicate/similar pages, it clusters them and algorithmically selects one
canonical version using signals including HTTPS-vs-HTTP, redirects,
sitemap inclusion, and `rel="canonical"` — described explicitly as "a
hint, not a rule" [Source: developers.google.com/search/docs/crawling-
indexing/canonicalization]. The canonical page is crawled more frequently;
duplicates are crawled less, reducing server load — a real server-side
performance benefit of getting canonicalization right, beyond the ranking
consideration.

**Structured data has three implementation formats, with a clear
recommended default and hard eligibility rules.** JSON-LD (Google's
recommended format, decoupled from visible markup, in a
`<script type="application/ld+json">` tag), Microdata (HTML tag
attributes), or RDFa. **All required properties for a given rich-result
type must be present for eligibility** — a partial implementation doesn't
get partial credit. Validate with the Rich Results Test before and after
deployment, and monitor ongoing via the Rich Result Status report in
Search Console, since templating/serving bugs can surface post-deployment
even after a clean one-off test
[Source: developers.google.com/search/docs/appearance/structured-data/
intro-structured-data].

**Sitemaps have hard, documented size limits — plan for sharding on
larger sites.** Max **50MB uncompressed** per file, max **50,000 URLs**
per file; larger sites need multiple sitemaps referenced by a sitemap
index file. `<priority>` and `<changefreq>` are explicitly ignored by
Google; `<lastmod>` is used "when consistently accurate"
[Source: developers.google.com/search/docs/crawling-indexing/sitemaps/
build-sitemap].

**hreflang tells Google which URLs are locale variants of the same
content — cookie/browser-based switching is explicitly discouraged.**
Google recommends distinct URLs per language rather than content-
switching based on cookies or browser settings, specifically so each
variant stays independently crawlable and indexable. `x-default`
designates a fallback (e.g. a language/country selector) that doesn't
target a specific locale
[Source: developers.google.com/search/docs/specialty/international/
localized-versions].

**Core Web Vitals has three current metrics with documented "good"
thresholds, and one of them recently replaced an older metric industry-
wide.** LCP ≤ 2.5s, INP < 200ms, CLS < 0.1
[Source: developers.google.com/search/docs/appearance/core-web-vitals].
**INP (Interaction to Next Paint) replaced First Input Delay (FID)** as
the responsiveness metric industry-wide in March 2024 — any guidance still
referencing FID as a live ranking metric is out of date. Google states
these thresholds "align with what Google's core ranking systems reward."

**A specific, named class of practice is explicitly prohibited and worth
checking against directly, not just avoiding vaguely.** Google's spam
policies name, among others: cloaking (different content to crawlers vs.
users), scaled content abuse (explicitly including "using generative AI
tools... to generate many pages without adding value" — a real, dated
policy expansion directly relevant to AI-assisted content work), hidden
text/links, keyword stuffing, link spam, and sneaky redirects
[Source: developers.google.com/search/docs/essentials/spam-policies].
**Never propose any of these even if they'd plausibly help a metric
short-term** — they risk demotion or removal, and the "scaled content
abuse" policy specifically targets low-value AI-generated content at
scale.

**Mobile-first indexing means mobile parity is the baseline, not an
afterthought.** Mobile content, headings, meta tags, and structured data
must be equivalent to desktop; a more-restrictive robots meta tag on
mobile than desktop is a real, documented mistake. Lazy-loading primary
content behind a simulated user interaction (click/swipe/type) that
Googlebot won't perform is explicitly flagged as a mistake
[Source: developers.google.com/search/docs/crawling-indexing/mobile/
mobile-sites-mobile-first-indexing].

**Next.js's own SEO-specific guidance is thin, and this skill states that
honestly rather than inflating it.** The production checklist's one line
on SEO/metadata: "use the Metadata API, generate Open Graph images, and
generate sitemaps/robots files"
[Source: nextjs.org/docs/app/guides/production-checklist]. The framework
exposes `generateMetadata()` and `generateSitemaps()` as documented
functions, consistent with that guidance. This is real but shallow —
treat it as confirming Next.js has first-party mechanisms for the
concerns this skill already covers generically (metadata, sitemaps), not
as an independently-researched Next.js-specific SEO methodology beyond
that.

## Decision framework

1. **Is the page/site actually meant to be publicly indexed?** If not
   (internal tool, non-public app), this skill doesn't apply.
2. **Is content JS-rendered?** If so, verify what Googlebot actually
   indexes is the *rendered* DOM, not just the initial server response —
   test against rendered output, not raw HTML.
3. **Does the request risk conflating robots.txt and `noindex`?** Check
   which is actually needed — hide from crawling entirely (robots.txt) vs.
   allow crawling but prevent indexing (`noindex`) are different tools for
   different goals.
4. **Would a proposed canonical/redirect choice actually be honored, or
   is it just a hint Google might override?** Design for the documented
   signal set (HTTPS, redirects, sitemap inclusion, `rel="canonical"`)
   working together, not `rel="canonical"` alone as an enforced rule.
5. **Does the proposed content strategy risk a spam-policy violation**
   (especially scaled/AI-generated low-value content, a real, named,
   dated policy)? If so, decline or flag rather than implementing it.
6. **Are Core Web Vitals thresholds actually being measured**, or assumed
   met? Hand off measurement/optimization depth to
   [performance-engineering](../performance-engineering/SKILL.md) while
   this skill tracks the thresholds as ranking-relevant targets.

## Workflow

1. Confirm the page/site is meant to be publicly indexed.
2. Check crawlability: robots.txt permits crawling, and (for JS-rendered
   content) the rendered DOM contains the intended content/links/
   structured data.
3. Implement/verify structured data (JSON-LD preferred), validating with
   the Rich Results Test.
4. Set canonical URLs and verify the full signal set (HTTPS, redirects,
   sitemap inclusion) is consistent with the stated preference.
5. Build/verify sitemaps within the 50MB/50,000-URL limits, sharding with
   a sitemap index if needed.
6. Add hreflang for locale variants, using distinct URLs, not cookie/
   browser-based switching.
7. Verify Core Web Vitals thresholds (LCP/INP/CLS), handing off deep
   measurement/optimization to performance-engineering.
8. Check the proposed approach against spam policies before implementing.

## Engineering rules

- Verify JS-rendered content against the rendered DOM, not just the raw
  server response.
- Distinguish robots.txt (prevents crawling) from `noindex` (allows
  crawling, prevents indexing) — never conflate them.
- Treat `rel="canonical"` as one signal among several, not a guaranteed
  enforced rule.
- Never propose a spam-policy-violating tactic, even if it might help a
  metric short-term — especially scaled/AI-generated low-value content.
- State plainly when indexing/ranking isn't guaranteed, rather than
  implying a change will definitely improve visibility.

## Trade-offs

Server-side/hybrid rendering benefits all crawlers (not just Googlebot,
which does execute JS) and real users' perceived performance, at the cost
of more rendering infrastructure than a pure client-rendered SPA. Splitting
a large sitemap into a sitemap index adds file-management overhead but is
required once the 50MB/50,000-URL limits are hit. Distinct per-locale URLs
(vs. cookie-based switching) cost more routing/content-management
complexity but keep each locale independently crawlable and indexable —
the trade the research shows Google explicitly recommending.

## Anti-patterns

- **Assuming raw server-response HTML is what gets indexed** for a
  JS-rendered page — Google indexes the rendered DOM.
- **Using robots.txt to try to hide a page from search results** — it
  only prevents crawling, and a linked-to page can still surface in
  results without robots.txt-blocked crawling.
- **Treating `rel="canonical"` as an enforced rule** rather than one
  signal Google can and does override.
- **Fragment-based (`#/route`) routing** for JS-rendered pages — Googlebot
  cannot reliably discover fragment-based URLs; use the History API
  instead.
- **Scaled or AI-generated low-value content** — explicitly named as a
  spam-policy violation, a real and dated policy addition directly
  relevant to AI-assisted content work.
- **Lazy-loading primary content behind a simulated interaction**
  Googlebot won't perform (click/swipe/type).

## Security

Hacked content (unauthorized third-party content injected via a security
vulnerability) is treated as a distinct spam-policy category that can
flag an entire site even though the owner didn't create the offending
content [Source: developers.google.com/search/docs/essentials/spam-
policies]. Deep threat modeling is owned by
[security-engineering](../security-engineering/SKILL.md).

## Performance

Core Web Vitals thresholds (LCP ≤2.5s, INP <200ms, CLS <0.1) are the
ranking-relevant targets this skill tracks; deep measurement/optimization
method is owned by
[performance-engineering](../performance-engineering/SKILL.md). Server-side
rendering is recommended as a performance best practice benefiting real
users and all crawlers, not just Googlebot.

## Testing

The Rich Results Test (structured data) and the URL Inspection tool
(live indexing status, rendered content, HTTP status) are the documented
official verification tools — use them rather than assuming a change
works. **Testing/measuring SEO changes needs real patience**: Google's own
guidance is to wait weeks (sometimes months) to assess impact, comparing
Search Console Performance-report data before/after over a period of
months rather than expecting an immediate signal — set that expectation
explicitly when proposing SEO changes.

## Failure handling

- If SEO goals aren't stated, ask what matters most rather than
  optimizing everything reflexively.
- If a ranking-weight claim isn't directly documented (e.g. HTTPS's exact
  ranking weight — this library's research could not verify current
  official wording on this beyond its role as one canonicalization
  signal), state that as unresolved rather than asserting a number.
- If asked about a search engine other than Google, state that this
  library's research covers Google specifically.

## Escalation

- A canonical/redirect/domain-migration change carries real
  ranking-continuity risk — presented with trade-offs for explicit
  confirmation, not applied unilaterally.
- A request that would violate a documented spam policy, however
  incidentally, is flagged and declined.

## Outputs & verification

- **Outputs:** SEO findings (defects with severity) and concrete fixes
  (structured data, canonical tags, sitemap/robots config, hreflang).
- **Verify:** rendered-DOM content matches intent for JS-rendered pages;
  structured data validates via Rich Results Test; no spam-policy-
  violating tactic is proposed.

## References

- [research/technologies/google-seo.md](../../research/technologies/google-seo.md)
- [research/technologies/nextjs.md](../../research/technologies/nextjs.md) — production checklist's SEO/metadata guidance.
