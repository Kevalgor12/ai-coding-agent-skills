# Google AdSense

Deep reference research on **Google AdSense**, Google's ad-monetization
product for website publishers (plus the associated **AdSense Management
API** for programmatic reporting/management). AdSense is not a software
library/framework in the conventional sense — it is a hosted advertising
service consumed via (a) a JavaScript snippet embedded in a publisher's site
and (b) a REST management/reporting API for publishers and platform
partners. Primary sources: **support.google.com/adsense** (the canonical
publisher-facing help center) and **developers.google.com/adsense** (the
canonical developer/API documentation, including
`developers.google.com/adsense/management` for the AdSense Management API
and `developers.google.com/adsense/platforms` for the AdSense-for-Platforms
API used by hosting partners). Research date: **2026-09-09**.

[Source: https://support.google.com/adsense/?hl=en] and
[Source: https://developers.google.com/adsense/] Both hosts are current and
active as of the research date; no host migration was found. Note the
docs are split across two properties with different audiences:
support.google.com/adsense targets publishers configuring ads through the
AdSense UI (ad code, Auto ads, policies, payments), while
developers.google.com/adsense targets developers building against the
AdSense Management API or AdSense-for-Platforms API (report automation,
account management for hosting partners). This document draws from both
because "AdSense" as a technology spans both surfaces.

---

## 1. Core concepts

[Source: https://support.google.com/adsense/answer/9274634?hl=en] The
**AdSense code** is the HTML snippet (`<script>` tag) publishers place on
their site to enable Auto ads and other AdSense features; Google recommends
placing it on every page of the site.

[Source: https://support.google.com/adsense/answer/9261805?hl=en] **Auto
ads**: a single piece of ad code is placed once per site; Google's
technology then scans the page structure and existing ad placements and
automatically inserts ads where they are "likely to perform well," adapting
as the site's layout changes over time. Auto ads formats fall into three
categories: (1) **intent-driven** — in-article links, anchors, and chips
inserted into content; (2) **overlay** — anchor ads (sticky top/bottom),
vignette ads (full-screen interstitial-style), and side rail ads for
widescreen viewports; (3) **in-page** — banner and multiplex ad units placed
within content areas.

[Source: https://support.google.com/adsense/answer/32713?hl=en] (page title
"Ad code") In addition to Auto ads, publishers can generate and place manual
**ad units** (individually configured ad slots) via the same code-generation
flow in the AdSense UI (Ads → By ad unit).

[Source: https://support.google.com/adsense/answer/9724?hl=en] Core
eligibility concepts for becoming an AdSense publisher: the site must have
"high-quality, original" content, the publisher must have access to the
site's HTML source, content must comply with AdSense Program policies, and
the applicant must be at least 18 years old (a parent/guardian may sign up
on behalf of a minor and receive payments). Publishers can also monetize via
"host partners" like Blogger or YouTube using hosted AdSense accounts.

[Source: https://support.google.com/adsense/answer/48182?hl=en] AdSense
revenue is governed by **Program policies** covering invalid clicks/
impressions, prohibitions on encouraging ad clicks, restrictions on traffic
sources (no paid-to-click schemes, no unsolicited mass email traffic), ad
placement rules (no ads in pop-ups, software, or ad-only pages), and general
site-behavior requirements (no malware, deceptive navigation, or unwanted
redirects).

[Source: https://developers.google.com/adsense/management] The **AdSense
Management API** is a separate, distinct concept from the ad-serving code:
it is a REST API that lets publishers "get reports on AdSense earnings and
manage AdSense inventory" programmatically (as opposed to using the AdSense
web UI).

[Source: https://developers.google.com/adsense/platforms/api/getting-started]
There is also an **AdSense for Platforms** product/API, distinct again, for
"hosting partners" (platforms that host many sub-publisher sites, e.g.
website builders) to manage child publisher accounts, sites, and ad
placements at scale — this is a different API surface (`v1`/`v1alpha`) from
the standard AdSense Management API.

---

## 2. Architecture

[Inference, not confirmed in docs] AdSense's architecture, as documented
across the publisher-facing pages, is best described as three loosely
coupled layers rather than a single system with an official architecture
diagram (no official architecture-diagram page was found):

1. **Ad-serving layer (client-side)**: [Source:
   https://support.google.com/adsense/answer/9274634?hl=en] a JavaScript
   snippet (`adsbygoogle.js`, served from
   `pagead2.googlesyndication.com`) loaded into the publisher's page, which
   requests and renders ads either via Auto ads' automatic placement engine
   or via explicit `<ins class="adsbygoogle">` ad-unit tags.
2. **Publisher account/config layer**: [Source:
   https://support.google.com/adsense/answer/9485926?hl=en] the AdSense web
   UI/account (Ads settings, Policy center, Payments, Ad review center) where
   publishers configure ad formats, review policy compliance, and manage
   payments.
3. **Management/reporting API layer**: [Source:
   https://developers.google.com/adsense/management] the AdSense Management
   API (REST, OAuth2-authenticated) providing programmatic access to
   accounts, ad clients, ad units, custom/URL channels, alerts, payments,
   and generated reports — mirroring what's available in the UI.

[Source: https://support.google.com/adsense/answer/9261805?hl=en] Within the
ad-serving layer, Auto ads is described as adaptive: Google's system
"understand[s] your page structure, detect[s] any existing Google ads on
your page," and places additional ads accordingly, re-evaluating as the page
changes — i.e., ad placement decisions happen dynamically/client-side per
page load rather than being statically fixed by the publisher.

[Source: https://developers.google.com/adsense/management/getting_started]
The Management API architecture follows standard Google API Console
patterns: register a project in Google API Console, generate OAuth2
credentials (Client ID), and use one of Google's provided client libraries
(which handle auth, service discovery, and request/response
marshalling) or make raw REST calls.

---

## 3. APIs

[Source: https://developers.google.com/adsense/management] The **AdSense
Management API** (current major version: **v2**) exposes REST resources
including Accounts, Ad Clients, Ad Units, Custom Channels, URL Channels,
Alerts, Payments, Policy Issues, and Reports (`reports.generate`,
`reports.generateCsv`, `reports.saved.generate`).

[Source: https://developers.google.com/adsense/management/getting_started]
Typical API workflow: authenticate via OAuth2 (the developer's Google
Cloud/API-Console project does not need to be tied to the AdSense login
itself), call `accounts.adclients.list` to enumerate ad clients, then call
`accounts.reports.generate` to run reports, optionally filtered by ad unit
or channel.

[Source: https://developers.google.com/adsense/management/release_notes]
Version history/breaking changes (see §13 for detail): the API progressed
through v1 → v1.1 → v1.2 → v1.3 → v1.4, then a major-breaking-change jump to
**v2** (initial release **2021-04-19**), which is the current version as of
this research date, having received incremental additive updates through
**2026-02-05** (most recent release note found).

[Source: https://developers.google.com/adsense/platforms/reference/rest] A
separate **AdSense Platform API** (REST, versions **v1** and **v1alpha**)
exists specifically for **AdSense for Platforms** hosting-partner scenarios
— managing platform accounts, events, and sites for partners who host many
sub-publishers. This is a distinct product/API from the AdSense Management
API and is not a version relationship (v1 here is not "older" than
Management API v2 — they are parallel products).

[Source: https://developers.google.com/adsense/platforms/direct/ad-tags] The
AdSense for Platforms product also documents a specific ad-tag pattern for
platform-hosted sites: `<script async
src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXX&host=ca-host-pub-XXXX"
crossorigin="anonymous"></script>`, including a `host` parameter that
differentiates it from the standalone-publisher ad tag.

[Source: https://developers.google.com/adsense/management/appendix/limits]
The Management API documents explicit rate/size limits — see §14
(Limitations) for the numbers.

[Unresolved: whether the AdSense Management API has "client libraries"
still officially maintained for all major languages as of 2026-09; the
getting-started page references a "Client Libraries and Samples" page but
this run did not fetch that page's current content to confirm per-language
support status.]

---

## 4. Configuration

[Source: https://support.google.com/adsense/answer/9274019?hl=en] Primary
publisher-facing configuration happens through the AdSense account UI: sign
in → **Ads** → **Get code** (for Auto ads, "Copy code snippet") or **Ads →
By ad unit** (for a specific manual ad unit's code). The Auto ads code is
pasted between the page's `<head>` and `</head>` tags.

[Source: https://support.google.com/adsense/answer/9261805?hl=en] Auto ads
configuration options (set in the AdSense UI, not via code): overall ad
format toggles (which of the intent-driven/overlay/in-page formats are
allowed), page-level exclusions, in-page-area exclusions, and vignette-ad
frequency controls.

[Source: https://support.google.com/adsense/answer/16918505?hl=en] For
publishers serving ads to users in the **EEA, UK, and Switzerland**,
configuration must include selecting **Ad Technology Partners (ATPs)** —
Google provides a "commonly used" partner list and a "full eligible
partners" list, and publishers must configure which ATPs are permitted to
serve/measure ads, tied to EU User Consent Policy compliance.

[Source: https://support.google.com/adsense/answer/16918505?hl=en]
(directly confirmed via WebFetch) Publishers "must use a consent management
platform (CMP) that has been certified by Google and integrates with the
IAB's Transparency and Consent Framework (TCF) when serving personalized
ads to users in the EEA, UK, and Switzerland." The page directs publishers
to check Google's list of certified third-party CMPs "regularly," since
Google continues certifying additional platforms over time.
[Unresolved: the specific **January 16, 2024** enforcement date reported by
third-party coverage of this requirement was not present in the text
returned from a direct WebFetch of this page in this run — the page as
fetched states the requirement itself but not a specific effective date.
Treat the January 2024 date as third-party-reported, not confirmed against
official-doc text in this pass.]

[Source: https://support.google.com/adsense/answer/47333?hl=en] (page title
"Enter your payments information in AdSense") Payment configuration requires
entering payment method and payee details in Payments settings; regional tax
information may also be required (see §17).

[Source: https://developers.google.com/adsense/management/getting_started]
API-side configuration: register an application/project in Google API
Console, generate OAuth2 Client ID credentials, select or configure a client
library, and complete the one-time OAuth authorization flow where the
AdSense account owner authorizes the registered application.

[Source: https://support.google.com/adsense/answer/12171612?hl=en] **ads.txt
configuration**: publishers create a plaintext `ads.txt` file at their
site's root declaring authorized sellers, one line per authorized exchange/
SSP; for Google seller accounts the domain is always `google.com` and the
publisher ID is the `pub-0000000000000000` value from the AdSense account.

---

## 5. Recommended patterns

[Source: https://support.google.com/adsense/answer/9274634?hl=en] Place the
AdSense code on **every page** of the site (not just select pages) so Auto
ads and other features can operate consistently.

[Source: https://support.google.com/adsense/answer/10760404?hl=en] (page
title "Optimisation tips for your site and your ads") Recommended
optimization patterns: use **Auto ads** with tuned ad-load settings and
formats rather than fully manual placement; convert fixed-size manual ad
units to **responsive ad units**; avoid over-restrictive advertiser/category
blocking (excessive blocking reduces advertiser competition and can lower
revenue); balance ad density against user experience per AdSense policies;
measure and optimize page speed via **PageSpeed Insights** and **Web
Vitals**; follow Google's SEO Starter Guide to grow qualified traffic
(more/better traffic, not just more ads, is framed as the sustainable
revenue lever).

[Unresolved: the WebFetch summary of this page also referenced "reducing
page length, placing ads above the fold, using vertical ad sizes on
desktop, and targeting 70%+ viewability for top ad units" as best practices,
but this specific figure/guidance was surfaced via a WebSearch snippet
rather than a direct fetch of the primary source page — flagging for
confirmation rather than asserting as fully verified.]

[Source: https://support.google.com/adsense/answer/9724?hl=en] Recommended
pattern before applying for an account: ensure the site already has
high-quality original content and full policy compliance *before* signing
up, since this improves approval likelihood (implying AdSense reviews
existing site quality as part of onboarding, not just after code
installation).

[Source: https://support.google.com/adsense/answer/9485926?hl=en] Use the
**Policy center** proactively to monitor for detected policy issues and
request review once issues are fixed, rather than waiting for ad-serving to
be limited/disabled.

[Source: https://developers.google.com/adsense/management/getting_started]
For programmatic use, the recommended pattern is to use an official client
library (handles auth, discovery, request building, response parsing)
rather than hand-rolling raw REST calls, unless a supported library isn't
available for the target language.

---

## 6. Anti-patterns

[Source: https://support.google.com/adsense/answer/48182?hl=en] Explicitly
prohibited (documented anti-patterns, not just style preferences): clicking
your own ads or using any means (manual or automated/bot) to inflate
impressions/clicks; compensating users for viewing/clicking ads (outside
approved rewarded-inventory mechanisms); using phrases like "click the ads"
or "support us" to encourage clicks; placing misleading graphical elements
near ads to induce clicks; running paid-to-click traffic schemes or
unsolicited mass email traffic to inventory; displaying ads via pop-ups,
within software/toolbars, or on pages whose primary purpose is to show ads;
framing another site's content without permission alongside ads.

[Source: https://support.google.com/adsense/answer/9261805?hl=en] Using
Auto ads together with certain non-standard implementations is documented as
unreliable/unsupported: the docs note Auto ads "may not function correctly"
with dynamically-injected code, third-party ad-server implementations, or
on certain host-partner site types — implying manual verification is needed
in those setups rather than assuming Auto ads works everywhere.

[Source: https://support.google.com/adsense/answer/1348752?hl=en] (page
title "How Google prevents invalid traffic") Generating or tolerating
**invalid traffic** (bots/automated clicks, accidental clicks from poor ad
placement e.g. ads placed too close to navigation controls) is an
anti-pattern with account-level consequences, not merely a metrics-hygiene
issue — see §7/§14.

[Source: https://support.google.com/adsense/answer/9724019?hl=en /
9274019?hl=en region — general AdSense code guidance] Placing AdSense/Auto
ads code without following AMP-specific ad code on AMP pages is called out
as incorrect: [Source:
https://support.google.com/adsense/answer/9579782?hl=en region /
9261309?hl=en] AMP pages require a distinct AMP-specific Auto ads script
(the `amp-auto-ads` library) rather than the standard AdSense code snippet.

---

## 7. Security

[Source: https://support.google.com/adsense/answer/48182?hl=en] Program
policy explicitly prohibits sites from engaging in malware distribution,
deceptive practices, or unwanted redirects — framed as an eligibility/
compliance requirement rather than a separate "security" doc set, since
AdSense itself is a service, not code the publisher deploys and secures.

[Source: https://support.google.com/adsense/answer/16918505?hl=en] For
EEA/UK/Switzerland traffic, security/privacy compliance is enforced via
mandatory **Ad Technology Partner (ATP)** configuration and (per the CMP
requirement — see §4) a **Google-certified Consent Management Platform**
integrating with the IAB TCF, which governs what user data is shared with
which ad-tech vendors.

[Source: https://support.google.com/adsense/answer/12171612?hl=en] **ads.txt**
functions as a supply-chain-security control: it lets publishers declare
which sellers (e.g., `google.com` with a specific `pub-` ID) are authorized
to sell their inventory, which "helps prevent counterfeit inventory from
being presented to advertisers" and lets ad buyers avoid bidding on
spoofed/unauthorized inventory claiming to represent the publisher's site.

[Source: https://support.google.com/adsense/answer/7679060?hl=en] (page
title "Ensure your ads.txt files can be crawled") Google's crawler must be
able to access `ads.txt` at the site root (not blocked by robots.txt or
server config) for the authorized-sellers declaration to take effect —
i.e., ads.txt is a security/trust control that depends on correct
crawlability configuration, not just file presence.

[Source: https://support.google.com/adsense/answer/157667?hl=en] Payment
identity/address is protected via a **PIN verification** step: once
earnings cross a threshold, Google mails a physical 6-digit PIN to the
payee address; the account holder must enter it correctly (3 attempts
allowed) to verify the payments address before further payment can proceed
— an anti-fraud control on the payout side.

[Not documented / could not verify: a dedicated "AdSense security" page
covering topics like account-takeover protection, 2FA requirements
specific to AdSense, or a formal security disclosure/bug-bounty process for
the AdSense product itself was not surfaced in this research pass — general
Google Account security (2-Step Verification) likely applies but is
documented at the Google Account level, not an AdSense-specific doc.]

---

## 8. Performance

[Source: https://support.google.com/adsense/answer/10760404?hl=en] Google's
own guidance ties **ad performance** to **site performance**: publishers
are directed to use **PageSpeed Insights** to measure page speed and **Web
Vitals** to "quantify the experience of your site and identify
opportunities to improve," on the premise that a faster, higher-quality
site sustains higher ad revenue over time (not just an SEO concern).

[Source: https://support.google.com/adsense/answer/9261805?hl=en] Auto ads'
adaptive placement is itself framed as a performance mechanism — Google's
system aims to place ads "where they're likely to perform well," implying
placement optimization is handled by Google's algorithm rather than left
purely to manual publisher tuning.

[Source: https://developers.googleblog.com/2013/07/an-async-script-for-adsense-tagging/]
The AdSense ad-loading script is designed to be loaded **asynchronously**
(`<script async src=".../adsbygoogle.js">`) specifically so it does not
block rendering of the rest of the page — this is the documented
recommended loading pattern (contrasted with older synchronous
`document.write`-based tagging).
[Inference, not confirmed in the current support.google.com docs fetched in
this run] This async pattern is widely described elsewhere as the current
default for generated ad code, but this run did not directly re-confirm the
literal current code Google's UI generates in 2026 — flagged for
verification if exact current markup matters.

[Not documented / could not verify: a numeric SLA or benchmark for
acceptable ad-load latency, nor an official "performance budget" figure for
AdSense scripts, was not found in the pages fetched in this pass.]

---

## 9. Testing

[Source: https://support.google.com/adsense/answer/13547173?hl=en] The **Ad
review center** is the primary official tool for publishers to inspect
ads actually being served on their site after the fact: publishers can view
ad details (creative image/format, metadata, metrics, related ads), search/
filter by ad network or type, and block individual ads or "visually
similar" ads (including an image-upload-based "block similar" feature
integrated with Google Image Search).

[Source: https://support.google.com/adsense/troubleshooter/9556696?hl=en]
Google provides dedicated **troubleshooters** for specific problem classes,
e.g. the **ads.txt troubleshooter**, as guided diagnostic tools distinct
from general documentation pages.

[Source: https://support.google.com/adsense/troubleshooter/6082669?hl=en]
A **Policy troubleshooter** exists similarly for diagnosing policy-related
ad-serving issues.

[Source: https://support.google.com/adsense/answer/9485926?hl=en] The
**Policy center** functions as an ongoing "testing/validation" surface for
compliance: it surfaces sites/pages that automated review processes flagged
as violating one or more Program policies, with issue descriptions and
(where available) screenshots; publishers can trigger a re-review after
fixing an issue. The docs explicitly caveat that "review processes... can't
detect every issue" — i.e., Policy center is not a complete/exhaustive
compliance test.

[Source: https://support.google.com/adsense/answer/16906718?hl=en] (page
title "Troubleshoot ad coverage issues") A dedicated troubleshooting flow
exists for diagnosing why ad coverage/fill is lower than expected.

[Not documented / could not verify: no official "staging/sandbox mode" for
serving fake/test ads without affecting live metrics was found in the pages
reviewed — AdSense appears to only serve live ads against the real account;
publishers are cautioned in Program policy against clicking their own live
ads even for testing purposes (§6), which is a notable constraint on how
testing can be done at all.]

---

## 10. Deployment

[Inference, not confirmed in docs — "deployment" for AdSense means site
integration/go-live, not software deployment in the traditional sense,
since AdSense itself is a hosted service.] The closest documented
equivalent to "deployment" is the ad-code rollout and site-verification
process:

[Source: https://support.google.com/adsense/answer/9274019?hl=en] 1)
Generate the code in the AdSense UI (Ads → Get code, or Ads → By ad unit).
2) Paste it into the site's HTML (`<head>` section for the main Auto ads
code). 3) Publish/deploy the site change through the publisher's normal
site-deployment process (this step is the publisher's own infra, not
AdSense's).

[Source: https://support.google.com/adsense/answer/13996652?hl=en]
(directly confirmed via WebFetch, page titled "Improvements to site
management") As of **September 15, 2023**, "when you add a new site in
AdSense, we'll now verify your site ownership in real time" — a change from
the prior manual review process that could take over a day. Documented
verification methods on this page: the **AdSense code snippet** (default)
and a newer **meta tag** option, the latter positioned as an alternative for
publishers who don't want to show ads on their homepage. The same update
added an ads.txt "last crawled" timestamp and a "Check for updates" button
in the AdSense UI.
[Not documented / could not verify: whether file-upload or DNS-record
verification methods (common on other Google products like Search Console)
are also offered specifically within AdSense — this page names only the ad
code and meta tag methods.]

[Source: https://support.google.com/adsense/answer/9261307?hl=en] (page
title "Set up Auto ads on your site") It can take **up to an hour** for
Auto ads to begin appearing after code deployment.

[Source: https://support.google.com/adsense/answer/9261309?hl=en] For AMP
sites specifically, deployment requires a separate **Auto ads for AMP**
script (loading `amp-auto-ads` libraries) pasted in `<head>`, turned on from
the dedicated "Auto ads for AMP" page in the AdSense UI; the docs state ads
"usually" appear within minutes but "occasionally" up to an hour.

[Source: https://support.google.com/adsense/answer/9579782?hl=en] WordPress
sites (and their AMP variants) have dedicated, separate deployment
instructions distinct from generic HTML sites, referenced from the main ad
code page.

---

## 11. Migration

[Inference, not confirmed as a single docs page] AdSense's documented
"migration" content is fragmented across a few distinct scenarios rather
than one canonical "migration guide":

[Source: https://support.google.com/adsense/answer/10760404?hl=en]
**Manual ad units → responsive ad units**: explicitly recommended as an
optimization/migration step ("switch fixed-sized ad units to responsive
versions").

[Source: https://support.google.com/adsense/answer/9261805?hl=en]
**Legacy/manual placement → Auto ads**: the docs note "Auto ads now works
through any AdSense ad unit code," implying a migration path where existing
ad-unit code can continue to host Auto ads' automatic placements rather than
requiring a full code replacement.

[Source: https://developers.google.com/adsense/management/release_notes]
**API v1.x → v2**: the only well-documented *version-to-version* migration
in the official docs is the AdSense Management API's move from v1.4 to v2
(2021-04-19), which was an explicit breaking change requiring API consumers
to migrate (see §13 for the specific breaking changes; Google's release
notes explicitly recommend migrating off v1.4 given its sunset).

[Source: https://support.google.com/admob/answer/9234653?hl=en] AdSense vs.
**AdMob vs. Ad Manager** is documented as a product-selection/migration
consideration for publishers whose needs change: AdSense is described as
the default/simpler product for websites; **Ad Manager** is for publishers
needing multiple demand sources or more granular control; **AdMob** is for
mobile-app inventory specifically (AdSense does not serve mobile in-app
inventory). Google documents these as complementary products a publisher
might migrate between as their business scales, rather than direct
competitors of each other.
[Inference, not confirmed in docs] No official step-by-step "migrate your
account from AdSense to Ad Manager" walkthrough was located in this
research pass; the comparison page frames it as a product-choice guide, not
a migration runbook.

[Not documented / could not verify: migration guidance from third-party ad
networks (e.g., Media.net, Ezoic) *into* AdSense — this is a cross-vendor
migration scenario that Google's own docs, being AdSense/Google-product
centric, do not cover (and this project's sourcing rules exclude non-
official sources for such a claim anyway).]

---

## 12. Version information

[Source: https://developers.google.com/adsense/management/release_notes]
**AdSense Management API**: current major version is **v2**, first released
**2021-04-19**, receiving ongoing incremental (additive, non-breaking)
updates; most recent documented release-note entry found is **2026-02-05**
(addition of `OS_TYPE`, `BROWSER_TYPE`, `WEBVIEW_TYPE` report dimensions).
Prior versions in the lineage: v1 (initial), v1.1, v1.2, v1.3, v1.4 — all
now deprecated/sunset (see §13).

[Source: https://developers.google.com/adsense/platforms/reference/rest]
**AdSense Platform API** (for AdSense-for-Platforms hosting partners):
documented as available in **v1** and **v1alpha**. This is a parallel,
separate product/version line from the Management API's v2, not a
predecessor.

[Source: https://support.google.com/adsense/answer/9261805?hl=en /
9274634?hl=en] The consumer-facing **AdSense product itself** (the ad-
serving code, Auto ads, the account UI) is a continuously-updated hosted
service with **no publicly numbered "major version"** the way a software
library has — Google does not document AdSense-the-product with a version
number/changelog analogous to a software release; features roll out on
Google's own cadence via the account UI ("Auto ads now works through any
AdSense ad unit code" — an example of a behavior change communicated
in-place on a help page rather than as a versioned release).

[Not documented / could not verify: no official LTS or formal support-
window policy for AdSense (the product) or for the Management API beyond
the explicit deprecation notices per version — Google's practice, per the
release notes, appears to be "announce deprecation with a sunset date,"
not a published fixed-length support window (e.g., "N years of support")
applied uniformly.]

---

## 13. Breaking changes

[Source: https://developers.google.com/adsense/management/release_notes]
**v1.4 → v2 (2021-04-19), the major documented breaking change**:
- Removed all deprecated v1.4 methods.
- Restructured resource identification to use a `name` field (REST resource
  name pattern) instead of prior identifier conventions.
- Removed the `kind` field from resources.
- Renamed multiple fields across Account, AdClient, AdUnit, Alert,
  CustomChannel, Payment, Report, and Site resources.
- **Discontinued AdMob and YouTube support** within this API (i.e., v2
  narrowed scope relative to v1.4, which had broader cross-product
  coverage).
- **Limited report data to a 3-year history** (a functional regression/
  constraint relative to whatever v1.4 supported).

[Source: (search-derived from Google Ads Developer Blog posts, titles
confirmed via WebSearch)
https://ads-developers.googleblog.com/2016/03/adsense-management-api-v12-v13-are.html]
**v1.2 and v1.3 deprecation**: sunset **August 17, 2016**.
[Source: (search-derived, Google Groups adsense-api announcement, title
"Deprecation of AdSense Management API v1.4")] **v1.4 deprecation**: sunset
**October 12, 2021**, with Google recommending migration to v2.
[Unresolved: these two deprecation-date claims were sourced via WebSearch
snippets of Google's own blog/Groups announcements rather than a direct
WebFetch of the original post content in this run; treat the exact dates as
likely-correct-but-not-independently-reconfirmed against the primary page
text. (Note: the CMP-certification date and site-verification claims flagged
elsewhere in this document as unresolved have since been directly confirmed
— see updated §4 and §10.)]

[Source: https://developers.google.com/adsense/management/release_notes]
Post-v2, subsequent changes have been **additive rather than breaking**
(new dimensions/metrics, new fields, new methods) — e.g. 2025-02-24 added a
`policyTopics[].type` field while **deprecating** (not removing) the
`must_fix` field, and 2025-05-06 changed `must_fix` to always report
`false` rather than removing the field outright — indicating Google's v2
change-management approach favors soft-deprecation of fields over
hard-breaking removals within the v2 major version.

[Not documented / could not verify: a breaking-change changelog for the
consumer-facing AdSense product (Auto ads behavior changes, ad-format
retirements, etc.) analogous to the API release notes was not found —
publisher-facing changes appear to be communicated via individual help-page
updates and account notifications rather than a consolidated changelog.]

---

## 14. Limitations

[Source: https://developers.google.com/adsense/management/appendix/limits]
**AdSense Management API rate/size limits**:
- 100 queries/minute per single user+project.
- 500 queries/minute across all users of a single project.
- 10,000 queries/day (daily quota resets around midnight Pacific time).
- JSON reports capped at **100,000 rows** (truncated beyond this, with a
  `totalMatchedRows` field indicating true size).
- CSV reports capped at **1,000,000 rows** (also truncated beyond this).
- An additional "report row quota" limits total reporting data retrievable
  over daily/shorter windows to prevent abusive usage; exceeding it returns
  HTTP 429 "Report row quota exceeded."
- Exceeding general request-rate quotas returns HTTP 429 "Too Many
  Requests"; exceeding pagination-parameter maximums returns HTTP 400 "Bad
  Request."

[Source: https://developers.google.com/adsense/management/release_notes]
(2021-04-19, v2 launch note) Report data is limited to a **3-year history**
in the Management API v2 — a hard limitation relative to whatever range
v1.4 supported.

[Source: https://support.google.com/admob/answer/9234653?hl=en] AdSense is
limited to **website/web inventory**; it does not serve mobile in-app ad
inventory (that is AdMob's scope) and does not provide access to non-Google
demand sources (unlike Ad Manager, which can mediate multiple demand
sources).

[Source: https://support.google.com/adsense/answer/9261805?hl=en] Auto ads
is documented as **not reliable in all implementations** — specifically
called out as potentially not functioning correctly with dynamically
injected/used code, certain third-party ad-server setups, or certain
host-partner site configurations.

[Source: https://support.google.com/adsense/answer/9485926?hl=en] The
Policy center's automated detection is explicitly documented as
**incomplete** — "they can't detect every issue" — meaning passing Policy
center review is not a guarantee of full policy compliance.

[Source: https://support.google.com/adsense/answer/157667?hl=en] Address/
PIN verification has a hard failure limitation: **3 incorrect PIN entry
attempts** fail verification and stop ad serving; if the address remains
unverified after **4 months**, ad serving stops on the account's pages.

---

## 15. Debugging

[Source: https://support.google.com/adsense/answer/13547173?hl=en] **Ad
review center** — the primary debugging surface for "why is this specific
ad showing," letting publishers inspect creative details/metadata/metrics
for served ads and block problematic ones (including bulk "block similar"
via image upload).

[Source: https://support.google.com/adsense/troubleshooter/9556696?hl=en]
**ads.txt troubleshooter** — guided diagnostic for ads.txt-related issues
(e.g., file not found, not crawlable, misconfigured entries).

[Source: https://support.google.com/adsense/troubleshooter/6082669?hl=en]
**Policy troubleshooter** — guided diagnostic for policy-violation-related
ad-serving problems.

[Source: https://support.google.com/adsense/answer/16906718?hl=en] Dedicated
troubleshooting guidance for **ad coverage issues** (low fill rate/no ads
showing).

[Source: https://support.google.com/adsense/answer/9668823?hl=en] Dedicated
troubleshooting guidance for **address (PIN) verification problems**.

[Source: https://support.google.com/adsense/answer/1348752?hl=en] For
invalid-traffic concerns specifically, Google states its filtration is
designed so that the flagged party (browser/bot/etc.) receives no visible
indication of being filtered — implying there is **no self-service tool**
to directly query "was this specific click/impression flagged as invalid,"
which is itself a documented limitation on debuggability of this dimension.

[Source: https://support.google.com/adsense/answer/1208370?hl=en] A
dedicated page for **reporting policy violations** (i.e., reporting other
sites/ads) exists as a distinct debugging-adjacent workflow from
troubleshooting one's own account.

---

## 16. Integration

[Source: https://support.google.com/adsense/answer/6084409?hl=en /
14333766] **Google Analytics 4 (GA4) integration**: publishers can link a
GA4 property with AdSense; the integration is described as relying on
shared IDs, automatically collected events, and data joining between the
two products. Linking/unlinking requires Admin role in AdSense and Editor
role in GA4; once linked, the connection is visible under GA4 **Admin →
Product links → Google AdSense Links**.

[Source: https://support.google.com/analytics/answer/9691421?hl=en] A
parallel integration exists between **Google Ad Manager** and GA4 (revenue
data surfaced in GA4's Advertising → Publishing → Publisher ads report),
documented as a related but separate integration from the AdSense↔GA4 one.

[Source: https://support.google.com/adsense/answer/9261309?hl=en /
9579782?hl=en] **AMP integration**: dedicated Auto-ads-for-AMP script
(`amp-auto-ads` library) and a dedicated AMP-compatible manual ad-unit
creation flow; AMP requires different ad markup than standard HTML pages.

[Source: https://support.google.com/adsense/answer/9579782?hl=en]
**WordPress integration**: dedicated instructions for inserting AdSense/Auto
ads code into standard WordPress sites and their AMP variants, distinct
from generic HTML placement instructions (implying no single universal
snippet-placement instruction covers all platforms).

[Source: https://support.google.com/adsense/answer/16918505?hl=en]
**Consent Management Platform (CMP) integration**: for EEA/UK/Switzerland
traffic, AdSense integrates with third-party CMPs that are **Google-
certified** and support the **IAB Transparency and Consent Framework
(TCF)** — this is a required integration point for legal ad serving in
those regions, not optional tooling.

[Source: https://developers.google.com/adsense/management/getting_started]
**Programmatic/API integration**: via OAuth2 + the AdSense Management API
(or, for hosting platforms, the AdSense Platform API), using Google-provided
client libraries across supported languages for building custom reporting
dashboards or account-management tooling outside the AdSense web UI.

[Source: https://support.google.com/admob/answer/9234653?hl=en]
**Cross-product integration within Google's ads stack**: AdSense, Ad
Manager, and AdMob are documented as a complementary trio (web-simple,
web-advanced/multi-demand, and mobile-app respectively), with Ad Manager
explicitly positioned as able to combine both web and app inventory in ways
AdSense alone cannot.

---

## 17. Production considerations

[Source: https://support.google.com/adsense/answer/48182?hl=en] Ongoing
**Program policy compliance** is a continuous production concern, not a
one-time setup step: Google reserves the right to disable ad serving or
close accounts for non-compliance, "without prior authorization exceptions"
per the policy page's framing — i.e., there is no documented general
appeals-before-enforcement guarantee.

[Source: https://support.google.com/adsense/answer/1348752?hl=en /
16737?hl=en] **Invalid traffic** monitoring is an ongoing production
concern: Google runs continuous automated + human review of clicks/
impressions; accounts with persistently high invalid-traffic levels risk
suspension or closure, and Google may limit or disable ad serving if it
cannot verify traffic quality — publishers are directed to a "how you can
help prevent invalid traffic" page, implying some production responsibility
is on the publisher (e.g., ad placement away from accidental-click zones).

[Source: https://support.google.com/adsense/answer/1709871?hl=en /
1709858?hl=en] **Payments in production**: governed by a payment threshold
(minimum earnings balance before payout is issued) and a documented
"Steps to getting paid" sequence; production revenue realization depends on
completing address/PIN verification (§7/§14) and, where applicable, tax
information submission.

[Source: https://support.google.com/adsense/answer/2490070?hl=en /
10735961?hl=en] **US tax information** submission is required for
applicable publishers and is presented at first sign-in; incomplete tax
info is a documented blocker to normal payment processing (mirroring the
YouTube monetization requirement referenced on the FAQ page, though that is
a different product).

[Source: https://support.google.com/adsense/answer/16918505?hl=en /
CMP-certification requirement] For any production site serving EEA/UK/
Switzerland traffic, maintaining a **currently-certified** CMP integration
is an ongoing production requirement (Google can decertify/require
migration to different certified CMPs over time), not a set-once
configuration.

[Source: https://support.google.com/adsense/answer/7679060?hl=en] Production
`ads.txt` maintenance requires ensuring the file remains crawlable (not
blocked by robots.txt, WAF rules, or CDN configuration changes) on an
ongoing basis, since infra changes downstream of initial setup can silently
break this control.

[Source: https://support.google.com/adsense/answer/10760404?hl=en]
Production performance monitoring is explicitly tied to standard web
performance tooling (PageSpeed Insights, Web Vitals) rather than an
AdSense-specific performance dashboard, meaning AdSense production
health monitoring is documented as partially delegated to general
web-performance tooling outside the AdSense product itself.

---

## Summary of sourcing caveats

Several claims in this document are marked **[Unresolved]** or
**[Inference, not confirmed in docs]** because they came from WebSearch
result *snippets* of official support.google.com/developers.google.com
pages rather than a full WebFetch of the primary page text. Two such flags
(the CMP-certification requirement and the site-verification
methods/real-time behavior) were subsequently upgraded to directly-fetched
confirmations — see §4/§7 and §10, sourced respectively from
`support.google.com/adsense/answer/16918505` and
`support.google.com/adsense/answer/13996652`. Remaining unresolved items
still needing direct-fetch confirmation in a follow-up pass: the exact
January 16, 2024 CMP-enforcement date (third-party-reported, not found in
the official page's own text as fetched), the v1.2/v1.3/v1.4 API
deprecation dates (sourced from Google's own blog/Groups post titles via
WebSearch but not independently re-fetched), and the specific 70%+
viewability-rate figure attributed to
`support.google.com/adsense/answer/10760404`.
