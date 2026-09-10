# Unresolved Items

This file collects every unresolved question, ambiguity, or unverified claim flagged during research across the 49 technologies in this Skill Library project. These are gaps the researching agent explicitly declined to guess at -- conflicting official sources, pages that 404'd, facts sourced only from search summaries rather than direct fetches, or genuinely undocumented behavior. Treat these as known open questions to re-verify before relying on the adjacent claims in each technology's `research/technologies/<slug>.md` doc. Items are grouped by technology; technologies with no unresolved items are omitted.

## Angular

- Exact default providedIn behavior of bare @Service() (v22) was not independently confirmed against raw page markup beyond a WebFetch summary.
- Whether the v22.0.0 TypeScript pin of '>=6.0.0 <6.1.0' has since loosened in later 22.x releases was not verified beyond the fetch-time snapshot.
- Exact version Vitest specifically became labeled 'stable' (vs. merely 'new default for new projects') was reported as v21 only via a WebSearch synthesis, not a direct raw angular.dev fetch.
- Full content/API list of the @angular/aria package (stabilized in v22 per third-party/WebSearch-derived summary of the official v22 blog) was not directly fetched from its own angular.dev guide page.
- Total count/full index of angular.dev/errors error codes was not enumerated; only NG0100 was directly verified.
- Router-specific testing guide content (guards/resolvers/navigation testing APIs) was not directly fetched, only noted as present in the router guide's navigation.
- Exact version the CLI's build pipeline defaulted to Vite/esbuild (over legacy Webpack-based @angular-devkit/build-angular) was not pinned to a specific version boundary in official docs fetched.
- Whether every 20.x/21.x/22.x minor release (not just the .0.0 majors) is free of breaking changes was not exhaustively verified against the full CHANGELOG.md, only assumed consistent with the documented semver policy.

## ClickHouse

- Exact LDAP/Kerberos external-authenticator support and NIST-800-63B password-policy/SSH-auth claims — only surfaced via WebSearch summaries, not a directly fetched full official page.
- Precise Stable/LTS support-duration SLA wording (three-prior-Stable/three-month, one-year LTS overlap) — from a WebSearch summary of the legal support-services-policy page, not independently fetched in full.
- Whether ClickHouse Keeper is a from-scratch Raft-based C++ ZooKeeper reimplementation — dedicated Keeper overview page 404'd on fetch; stated as inference only.
- Completeness of 2026 breaking changes — changelog fetch summary claimed only one 2026 release existed, conflicting with other evidence of 26.1-26.8; likely incomplete page capture, so only 26.8's changes are documented here.
- MySQL-to-ClickHouse migration guide specifics — inferred from site navigation only, not fetched directly.
- Existence/current URL of a stable 'network-security' guide page — a search-indexed URL 404'd on direct fetch.
- Query-execution engine internals (vectorized execution / processor pipeline) — no official architecture page describing this was successfully fetched.

## CSS (Cascading Style Sheets)

- Exact current browser-support percentages/version cutoffs for native CSS nesting were not pulled from MDN's browser-compat-data table -- only qualitative 'growing support, check tables' guidance was captured.
- Whether any specific CSS syntax was formally deprecated or removed from a Recommendation-track spec in 2024-2026 could not be confirmed against an official CSSWG changelog; no such changelog distinct from the annual Snapshot notes was located.
- Whether MDN's pre-2025 URL structure (e.g. /Web/CSS/@supports, /Web/CSS/box-sizing) fully 404s everywhere or partially redirects was not exhaustively checked; several old paths tested during this research returned direct 404s.
- Whether @import and @charset are covered in the MDN Getting Started guide was explicitly noted by that guide itself as out of scope, so this document does not claim official coverage of them beyond what was separately verified.

## Docker

- Whether Docker publishes a formal LTS/support-window table for Engine major versions anywhere on docs.docker.com beyond the general statement that patch releases are backward-compatible within a major.minor line and the stable/test release-channel distinction -- no such table was located in this research pass.
- Whether there is a single consolidated 'breaking changes across major versions' page for Docker Engine versus breaking changes being documented only inline per-version in engine/release-notes/<major>/ -- only the 29.x notes page was directly verified; older major-version transitions (e.g. 24->25, 25->26) were not independently checked.
- Whether docs.docker.com currently hosts an official 'migrating from Docker Toolbox' page -- not confirmed present or absent in pages fetched.
- Whether a dedicated storage-driver migration guide (e.g. aufs/devicemapper -> overlay2) exists beyond the daemon.json storage-driver configuration reference itself -- not located in this pass.
- The claim that Compose V1-launched containers get recreated under new names on first V2 'up' was sourced from blog/secondary summarization rather than independently re-verified against a primary docs.docker.com page in this pass, and is flagged as an inference in the document.
- No single consolidated architecture diagram/page showing the full dockerd -> containerd -> containerd-shim -> runc process tree (including shim persistence across daemon restarts) was located; component relationships were pieced together from multiple pages.

## Drizzle ORM

- Exact bundle-size claim for drizzle-orm is inconsistent across two fetches of the same overview page (7.4kb vs ~31KB gzipped) — likely context-dependent (core vs. with-adapters) but not disambiguated in this pass.
- Whether the v0-style global `drizzle({ casing: 'camelCase' })` init option is fully removed in v1 or retained as a deprecated fallback alongside the new table-level snakeCase/camelCase builders — the v0-v1-changes page says it was 'replaced' but no v1 API reference page was fetched to confirm total removal vs. deprecation.
- A `1.0.0-rc.5`-style build tag was referenced by a third-party scanner (Snyk) during research but could not be confirmed as an official tagged GitHub/npm release; not used as a cited fact, only flagged as a signal the rc line kept advancing past rc.4.
- Drizzle Studio's underlying architecture (local-only proxy vs. any hosted/remote component) could not be confirmed — the dedicated /docs/studio page returned HTTP 404 during this research pass; security-relevant claims about Studio should not be made without re-verifying this.
- Whether orm.drizzle.team/docs/latest-releases is simply stale/unmaintained relative to GitHub releases, or whether this pass's fetch just failed to load pagination/lazy-loaded newer entries — the page showed nothing past beta.2 (Feb 2025) despite GitHub showing releases through rc.4 (June 2026).

## ECMAScript

- Full itemized contents of the ECMA-262 section on 'Additions and Changes That Introduce Incompatibilities with Prior Editions' — its existence was confirmed via official-source search snippets but direct primary-source extraction of the full list was not achieved due to WebFetch truncating the large multipage spec document.
- Exact reconciliation between the process document's stated 'July' General Assembly approval timeline and the 'June 2026' release date given on ecma-international.org for the 17th edition — both are official-source claims not reconciled to an exact date.
- Whether the tc39/ecma262 GitHub README documents explicit edition versioning/branching strategy (main branch vs. tagged yearly releases) — the fetched README excerpt did not surface this detail despite being sought.
- Full introductory normative text of Annex B (rationale, complete list of legacy features it documents) — WebFetch repeatedly returned only table-of-contents-level content for this large page rather than body text.

## Express

- The exact wording and confirmed status of a CVE (referenced in third-party summaries as CVE-2024-51999) claimed to have been filed against Express 5.2.0 and then rejected in 5.2.1 -- could not confirm this against an expressjs.com-hosted security page in this research pass; the official security-updates.html page did not surface a 5.x-specific CVE entry.
- Whether Express 4.x has entered an informal 'maintenance' phase with a targeted EOL date (~October 2026) as claimed by third-party commercial vendor (HeroDevs) content -- the official expressjs.com/en/support/ page lists 4.x support simply as 'Ongoing' with no maintenance-phase distinction or EOL date, so the commercial claim is flagged but not asserted as fact.
- The official expressjs.com/en/changelog/ page (linked from the site's own Resources nav per search results) returned HTTP 404 at fetch time; could not directly verify its current content or confirm whether it has been removed/relocated post-redesign.

## Fastify

- Exact date fastify.dev became the canonical docs host replacing fastify.io was not confirmed — only that fastify.dev is canonical as of 2026-09-09 and that the domain was controlled by a maintainer since at least 2019.
- Whether /docs/latest/ is formally defined by the project as 'latest stable' vs 'most recently built docs' — inferred to mean v5.x throughout this document since no v6-only content was observed on any fetched /latest/ page.
- Whether the Prototype-Poisoning guide page has been updated since its original (2019-era, Eran Hammer-authored) content, or remains purely historical.
- Full list of FSTDEP0xx and FSTWRN0xx codes — only 4 FSTDEP codes (022-025) and 3 FSTWRN codes (001, 003, 004) were captured from the fetched Warnings page excerpt; FSTWRN002 and any FSTDEP001-021 were not observed and are presumed to exist but unverified.
- Exact new Node.js minimum version for the upcoming v6 major was not confirmed in fetched v6.0.0-alpha release notes excerpts.
- Whether fastify.dev hosts a dedicated 'Debugging' guide page — a targeted search did not locate one; only scattered debugging-relevant facts (warning-trace flags, frameworkErrors, onError hook, logger) were confirmed from other pages.
- Existence/mechanics of printRoutes() as a debugging aid was reported only via a WebSearch summary, not verified by directly reading a primary fastify.dev page.
- Whether useSemicolonDelimiter's pre-v5 default/behavior was independently verified against an older versioned Server reference page, versus being taken solely from the V5 migration guide's framing.
- Contents of the V3->V4 and V2->V3 migration guides were not reviewed in detail (only existence/URL confirmed).

## GitHub

- Exact standard support-window length in months from a GHES feature release GA date to its discontinuation date -- only individual dates and a 'four most recent releases' rule were found, no fixed N-month figure
- GHES production hardware-sizing table (vCPU/RAM/storage by user count) was only confirmed via WebSearch result snippets, not a successful direct page fetch -- the guessed canonical URL 404'd
- Whether GitHub.com/GHEC publishes a customer-facing SLA/uptime commitment within docs.github.com itself -- not located in pages fetched
- Whether GraphQL API breaking changes follow a formal deprecation-window policy analogous to REST's 24-month rule -- not found; GraphQL changelog appears continuous rather than discretely versioned

## GitHub Actions (CI/CD)

- Exact latest actions/runner patch version and release date as of September 2026 -- fetched releases page returned dates inconsistent with 2026 changelog context (likely a tool date-resolution artifact); only the enforced minimum (v2.329.0) is confidently confirmed.
- Whether the set-output/save-state workflow commands have now been hard-removed or still merely emit deprecation warnings -- last confirmed state (warning-only) was not re-verified against a live current page.
- Whether the Node.js 20 removal from GitHub-hosted runners (scheduled Sept 16, 2026, one week after this research's date) has actually completed on schedule or was extended, since no changelog page dated on/after that date was fetched.
- Precise GHES per-version end-of-support dates (3.14, 3.16, 3.17) -- sourced from a WebSearch summary rather than a directly fetched official release/support table.
- Specific documented concurrent-job ceiling numbers (e.g. 500 standard / 1,000 larger-runner jobs on GitHub Enterprise Cloud) -- sourced via WebSearch summary, not a directly quoted official page snippet.
- Exact current URL/content for the ACTIONS_RUNNER_DEBUG (runner-level debug) setting -- distinguished from the directly-fetched ACTIONS_STEP_DEBUG page, but not independently re-fetched itself.

## Go

- Whether go.dev hosts a current, modules-era canonical Docker/container deployment guide beyond the older (GOPATH-era) /blog/docker post -- not confirmed.
- The exact Go version runtime/secret first shipped in and its stability roadmap -- only seen labeled 'experimental' in Go 1.26 notes.
- The FAQ's stated rationale against generic methods (four implementation obstacles) appears superseded by Go 1.27 actually introducing generic methods; whether/when the FAQ page itself was updated to reconcile this was not confirmed.
- Go 1.27.1 / 2026-09-01 patch release was only seen via a search-engine summary, not confirmed by directly fetching the go.dev/doc/devel/release page's 1.27.x subsection.
- Content of /doc/jsonv2-migration, /blog/migrating-to-go-modules, /blog/c-go-cgo, /doc/build-cover, and most of /doc/database/* sub-pages beyond sql-injection were referenced only by title from the doc index, not independently fetched.
- Breaking-change specifics for Go 1.24 and 1.25 were not independently fetched (only referenced indirectly via later releases' deprecation timelines).

## Google AdSense

- Exact enforcement date (commonly reported as January 16, 2024) for the mandatory Google-certified CMP/TCF requirement in EEA/UK/Switzerland -- the requirement itself was directly confirmed via WebFetch of support.google.com/adsense/answer/16918505, but that specific date was not present in the fetched page text (only found via third-party coverage).
- Exact sunset dates for AdSense Management API v1.2/v1.3 (Aug 17, 2016) and v1.4 (Oct 12, 2021) -- sourced from WebSearch snippets referencing Google's own blog/Groups post titles, not independently re-confirmed via direct WebFetch of the original announcement text.
- The specific '70%+ viewability rate for top performing ad units' optimization figure attributed to support.google.com/adsense/answer/10760404 -- surfaced via a WebSearch summary of that page rather than confirmed in the direct WebFetch performed in this session.
- Whether AdSense offers file-upload or DNS-record site-verification methods in addition to the AdSense code and meta tag (only these two were found on the directly-fetched site-management page).
- Whether Google-provided client libraries for the AdSense Management API are still actively maintained for all languages as of 2026 -- the getting-started page references a separate 'Client Libraries and Samples' page that was not directly fetched in this pass.
- Whether there is any official AdSense-specific security/bug-bounty or account-security documentation beyond general Google Account security and Program Policy anti-fraud rules -- none was found in this research pass.

## Google SEO (Google Search Central / Google Search)

- Exact current numeric daily quota for the Indexing API (a secondary search suggested 200/day but this could not be confirmed in the primary fetched official page text, which only said a 'default quota' is granted for onboarding/testing).
- Whether a dedicated, currently-live official page on 'HTTPS as a ranking signal' still exists — the historical URL (developers.google.com/search/docs/crawling-indexing/https) returned HTTP 404 during this research pass; HTTPS's role was only confirmed indirectly as one of several canonicalization-selection signals.
- Whether a single dedicated official 'site move / domain migration' step-by-step guide page currently exists and what it says beyond the general canonicalization/redirect signals confirmed in the canonicalization doc.
- Whether Search Central docs still carry an explicit callout/migration notice about INP replacing FID, versus having simply dropped FID from current pages over time.

## Grafana

- Whether "dashboards as code" workflows are documented as primarily using the HTTP API's dashboard-update endpoints versus exclusively file-based provisioning or third-party as-code tools — the docs describe multiple coexisting paths without a stated preference.
- Exact HTTP API authentication mechanisms (API tokens vs. service accounts vs. basic auth) were not confirmed with quoted text from the `developers/http_api/` page itself.
- Whether `[auth.saml]` (or an Enterprise-specific SAML config) has its own documented `grafana.ini` section name — SAML's existence is implied by a security advisory but its exact configuration surface was not directly confirmed.
- Whether Grafana publishes an aggregate/historical CVE count or an explicit disclosure-process SLA (acknowledgment/embargo timelines).
- The precise set of tabs/data exposed by the Query Inspector tool — confirmed only at the level of "lets you view and optimize your query," not itemized tab-by-tab.
- **The literal term "LGTM stack" was not found verbatim in any official grafana.com/docs page fetched** — the four-component architecture (Loki, Grafana, Tempo, Mimir) is fully documented under OpenTelemetry/OTLP ingestion pages, just not under that acronym; skill content should describe the components explicitly rather than assuming "LGTM stack" resolves to a specific official docs anchor.
- Whether Tempo's trace data format is explicitly documented as OpenTelemetry-based on the Tempo data-source page itself — this fact was established via the separate OpenTelemetry/OTLP docs rather than the Tempo page directly.
- No dedicated "reference org/folder structure for a growing engineering team" governance playbook was located beyond the isolation-boundary and RBAC primitives.
- Dashboard/query sizing guidance (how many panels or concurrent queries is "too many" for a single Grafana instance) was not located.

## GraphQL

- Whether the ~6-month spec release cadence stated in the October 2016 release notes is still operative — the ~4-year gap between October 2021 and September 2025 editions suggests it wasn't maintained as planned, but no current-cadence statement was found in reachable docs.
- The www.graphql-js.org 'Migration from express-graphql' guide is referenced from getting-started page navigation but was not independently opened/content-verified in this pass.
- No official GraphQL/graphql-js testing methodology guide could be located — www.graphql-js.org/docs/testing/ returned HTTP 404.
- No official 'common errors' troubleshooting reference or graphql-js 'error-handling' guide could be located — both graphql.org/learn/common-errors/ and www.graphql-js.org/docs/error-handling/ returned HTTP 404.

## HTML

- Whether an official WHATWG changelog/release-notes page (distinct from the raw GitHub commit history of the whatwg/html repo) exists that summarizes recent breaking/notable changes over a time window — none was located during this research pass; tracking changes in practice would require diffing spec commits rather than reading a changelog page, which is an inference, not a confirmed documented workflow.
- Whether the WHATWG spec's parsing/error-recovery algorithm has had any recent (2025-2026) backward-incompatible change — no specific recent breaking change to parsing behavior was found documented, so Section 13 notes the general 'extreme care' policy without a concrete recent example.
- Whether a current, actively maintained official W3C or WHATWG page exists that explicitly walks through migrating an HTML4 document to current HTML (as opposed to the obsolete-features table, which functions as a de facto but not purpose-built migration guide) — not found in the sections fetched.
- Whether meta charset is required to appear within the first 1024 bytes as a hard normative rule versus a practical consequence of the encoding-sniffing prescan window — the meta-element page itself did not explicitly state the 1024-byte constraint (that number came from the parsing/encoding-sniffing page), so the two facts were combined via reasonable inference rather than found stated together on one page.

## Husky

- Whether Husky v10.0.0 is imminent — the docs/source reference it as the version removing deprecated shim lines, but no v10 tag, branch, or changelog entry exists as of 2026-09-09; repo has continued (docs/CI) commits into 2026 without a new npm publish since Nov 2024
- Whether the Node.js-18-removal / Node-24-addition CI change (commit 2025-10-10) will land in a future 9.1.x patch or is being held for an unreleased v10 — the published package.json engines field still reads >=18
- Whether the ~/.huskyrc startup-file deprecation has a committed removal version — unlike the shebang/sourcing-line deprecation, which is explicitly tied to v10.0.0, no removal version is stated for ~/.huskyrc

## Jest

- Exact date/announcement of the facebook/jest → jestjs/jest GitHub org transfer was not located in official docs; inferred only from current canonical URLs.
- waitForUnhandledRejections' actual default value: the v30 upgrade-guide prose implies it's enabled by default, but the fetched configuration reference table listed its default as false — needs direct re-check against the live configuration doc.
- Whether Jest has any v31 pre-release work in progress: npm's 'next' dist-tag pointed to a stale 30.0.0-rc.1, inconsistent with 'latest' being 30.5.1.
- Exact automatic-vs-explicit-jest.mock() semantics for manual mocks (__mocks__ directory) depending on node_modules vs. user-module location — described only in general terms in the fetched summary.
- bail being ignored inside individual `projects` sub-configs was sourced via a referenced GitHub PR discussion, not independently re-confirmed against the current live configuration doc text.

## MongoDB

- Whether MongoDB officially documents/endorses in-memory or in-process test servers (e.g., the pattern used by the community mongodb-memory-server package) — no official MongoDB-authored guidance was found; only the Docker-based mongodb-atlas-local image and a replica-set-for-testing tutorial are officially documented for local test deployments.
- Whether MongoDB 9.0 has reached General Availability, and if so its GA date and feature scope — a WebSearch reference to 9.0 PPA/packaging activity (Aug 2026) could not be corroborated with a fetched official 9.0 release-notes page.
- A curated, itemized list of MongoDB 7.0-vs-6.0 breaking/compatibility changes analogous to the official 8.0-compatibility page — no equivalent 7.0-compatibility page was located; the fetched 7.0 release-notes page is patch-changelog-oriented instead.
- The exact mechanics of the Rapid-Release-to-Minor-Release transition at 8.2 (Atlas-only to downloadable) were pieced together from WebSearch snippets referencing MongoDB's own release-cadence blog post plus the official versioning page, not verified against a single directly-fetched official page — flagged in the doc as an inference, not a verbatim citation.
- A fully exhaustive catalog of every officially maintained MongoDB connector/integration (Kafka, Spark, Power BI, and Tableau were confirmed; the full /docs/tools-and-connectors/ hub was not exhaustively walked).

## Mongoose (MongoDB Object Modeling for Node.js)

- Whether Mongoose 8.x's stated 'support through Feb 1, 2026' is still operative given continued 8.24.x patch releases observed through August 2026
- Full technical detail behind the 8.24.3 changelog line 'Applied sanitizeFilter to countDocuments and cursor operations' - no dedicated official advisory found for it
- Exact schema-level API syntax for MongoDB Client-Side Field Level Encryption integration
- Complete breaking-change lists for the 6->7 and 7->8 major migrations (only headlines captured, not full page fetch)
- Minimum Node.js version specifically required for Mongoose 8.x (only 9.x's 20.19.0 minimum was explicitly found)
- Whether mongoose.set('debug', true) exposing sensitive data in production logs is stated explicitly in official docs or is only general/inferred caution
- Whether a single consolidated official 'production checklist' or 'testing strategy' page exists beyond the distributed guidance found across multiple pages
- Whether additional entries exist on the deprecations page beyond the single validateSync() entry captured

## MUI (Material UI)

- Exact official rationale/announcement for why Material UI's major version skipped v8 entirely (jumping v7 -> v9) was not located in the docs pages fetched; only the general framing of 'ecosystem-wide version alignment with MUI X' was found.
- Whether an internal/unreleased v8 ever existed for Material UI specifically was not conclusively confirmed by the versions page.
- Exact URL/content of the official 'integration with third-party routing libraries' guide referenced from the FAQ was not independently fetched/verified.
- Full content of MUI X's v9 telemetry/licensing docs (mui.com/x/introduction/licensing/) was not fetched in depth -- flagged only via search-result summary, since it is technically out of scope for a Material-UI-only research pass but was surfaced during production-considerations research.
- Whether Cypress (vs. Testing Library) has any official Material UI-specific guidance was not found in the fetched testing guide.

## MySQL

- Whether MySQL 9.7 LTS will be renumbered under the new calendar-versioning scheme or remains permanently legacy-numbered.
- Exact official EOL dates for MySQL 8.4 LTS and 9.7 LTS — derived from a search summary, not a clean direct WebFetch of mysql.com/support/eol-notice.html.
- Breaking changes specific to the 8.4→9.7 LTS transition and to the new 26.7.0 calendar-versioned release were not enumerated (only 8.0→8.4 was fully researched).
- innodb-limits.html figures were sourced via a WebSearch summary after a direct WebFetch 404'd on one attempt; needs re-verification at the primary URL.
- Official Kubernetes / MySQL Operator integration documentation was not independently verified in this pass.
- No first-party 'testing your application against MySQL' guidance was found in official docs (only MySQL's internal dev test suite) — flagged as a genuine documentation gap.
- X DevAPI / C API compatibility and versioning guarantees were not fully verified against a dedicated compatibility-policy page.

## Next.js

- Exact CVE identifiers/advisory detail for the August 2026 Next.js security release (16.3.3 / 15.5.24, two critical vulnerabilities) — only found via WebSearch summary, not a direct page fetch
- The 'roughly once a month' security-release cadence claim traces to a WebSearch summary of nextjs.org/blog/next-security-release-program, not a direct fetch of that page
- Full content of the three dedicated framework-migration guides (App Router migration, Create React App, Vite) — only index titles/descriptions were confirmed, not full guide steps
- Full content of the Self-Hosting guide (/docs/app/guides/self-hosting) — only cross-references from other pages were captured
- Whether Next.js documents first-party mocking utilities for Server Actions/Route Handlers/App Router request context beyond the experimental config-testing helper — no direct evidence found
- Precise mechanics of the 'previous' (non-Cache-Components) caching model (caching-without-cache-components guide) were not independently fetched

## Node.js

- Exact release dates for the current patch versions (v26.8.2, v24.21.0) were not independently confirmed — nodejs.org/en/download gives version numbers only, and the separately-fetched previous-releases page's per-line 'Last Updated' dates (Sep 09, 2026 for v26; Sep 07, 2026 for v24) were not verified to correspond exactly to those specific patch releases rather than to some other status-change event.
- Whether nodejs.org or the nodejs/node GitHub org publishes a single consolidated 'breaking changes across all majors' index distinct from each release's own changelog — none was located in this research pass; each major version's changes must be read from its own CHANGELOG_V<N>.md or release blog post.
- Breaking-change specifics for Node.js v20 and earlier majors were not independently fetched in this pass (only v22.0.0, v24.0.0, and v26.0.0 changelogs/release notes were read in full); consult the corresponding CHANGELOG_V<N>.md files directly if that history is needed.
- Which npm version ships bundled with Node.js 26.0.0 was not confirmed — only that Node.js 24.0.0 bundled npm 11; the v26.0.0 release notes fetched did not mention an npm version bump.
- Whether the OpenJS Foundation or Node.js TSC publishes any formal, versioned deprecation-window policy (e.g., a minimum number of releases between runtime-deprecation and removal) was not found; the documented pattern (e.g., crypto.createCipher/createDecipher runtime-deprecated in v22.0.0, fully removed in v26.0.0) was observed but no policy document stating a guaranteed minimum window was located.
- Whether nodejs.org hosts any official, platform-specific (AWS/GCP/Azure/Vercel) deployment guide beyond the Docker working group's container-focused best practices — none was found in this research pass; absence is not confirmed as complete, only as not located.
- Corepack's longer-term roadmap (e.g., whether it will ever be re-bundled with Node.js core after its removal from bundling at v25.0.0, or remains permanently a separate install) was not addressed in the README fetched.
- The precise current status/detail of the OpenJS Foundation's referenced 'AI Coding Assistants Policy' (mentioned in passing on the governance page) was not independently fetched or summarized in this pass.

## Nuxt

- Whether nuxt.com's docs host has a distinct stable '5.x' URL path yet, since Nuxt 5 was not released as stable at research time.
- Exact current full content of the official Nuxt 2→3 migration guide was not re-fetched verbatim in this pass; only its existence and general description were confirmed.
- A discrepancy between two official-adjacent sources on Nuxt 3's EOL date: one summarized fetch of nuxt.com/blog/v4 stated Nuxt 3 support ran 'through January 2026,' while the Roadmap page and Nuxt-3-EOL GitHub discussion both state 2026-07-31. The more specific Roadmap date (2026-07-31) was treated as authoritative but the conflict itself is flagged in the document rather than silently resolved.
- Nuxt DevTools' specific feature-panel names (Timeline, Render Tree, Hooks tab, Assets panel) were sourced from a WebSearch summary of devtools.nuxt.com content rather than a direct full WebFetch read in this pass, so the exact panel names carry lower confidence.
- The characterization of Nuxt 4.5 as 'the biggest release in a while' was a WebSearch-summarized phrase, not independently confirmed as verbatim official wording.
- No single consolidated 'Security' best-practices guide page (as opposed to advisory/patch-note blog posts) was located on nuxt.com/docs during this research pass -- it's possible one exists under a URL not surfaced by search/fetch in this session.
- No official Nuxt docs page for migrating *from* a different framework (e.g., Next.js) to Nuxt was located -- only version-to-version (2->3, 3->4, 4->5-preview) upgrade guides exist in official docs as far as this research could confirm.

## OpenAPI

- Exact CHANGELOG.md contents for 3.1.1 and 3.0.4 patch releases — GitHub blob and raw.githubusercontent.com URLs both returned 404 during this session, so their 'editorial only' characterization rests on the upgrade guides' summary framing, not a direct changelog read.
- Step-by-step official migration guidance for Swagger 2.0 → OpenAPI 3.0 was not directly fetched; the Learn site's TOC references a '1.0 to 3.2' upgrading resource but its specific content wasn't retrieved in this pass.
- No formal LTS / end-of-life / support-window policy for older OAS lines (e.g. 3.0.x) was found in the primary sources checked — unclear if the OAI publishes one elsewhere.
- Whether the openapis.org FAQ page's stale '3.1.1 is latest' claim reflects infrequent page updates or some other cause is unconfirmed — noted only as an observed documentation-staleness discrepancy.

## OpenSearch

- Exact default values for network.host, path.data, path.logs in opensearch.yml — page structure confirmed but full body text not retrieved by fetch tooling
- Exact numeric bulk-indexing-size and refresh_interval tuning recommendations on tuning-your-cluster/performance/ — only navigation structure was retrievable
- Exact minimum RAM/CPU/disk sizing per node role (data/cluster-manager/coordinating) — not retrieved verbatim
- Full quoted breaking-changes catalogue across all 2.x minor versions on the consolidated docs.opensearch.org/latest/breaking-changes/ page — only the 3.0 GitHub-issue-tracked list was fully retrieved
- Whether the '50% RAM heap, ~32GB cap' JVM sizing guidance appears in those exact terms on a current docs.opensearch.org page vs. only in search-engine-indexed snippets of that domain — treated as inference pending direct-page confirmation

## OpenTelemetry

- Exact calendar release dates for the current Collector, JS, Python, and Go SDK releases — version numbers were captured with reasonable confidence, but this session's tooling returned apparently-inconsistent years across separate fetches of the same GitHub release pages, so specific dates were deliberately omitted rather than asserted.
- Whether a dedicated official "testing your OpenTelemetry instrumentation" guide exists anywhere on `opentelemetry.io` beyond the Node.js instrumentation page checked — the most likely single page was checked and found not to cover testing, but the full site was not exhaustively searched.
- The full pros/cons comparison table on `/docs/collector/deploy/` and the full contents of `/docs/collector/distributions/` — only the pages' framing/table-of-contents was retrieved, not their complete body content.
- Numeric SDK-instrumentation performance overhead (e.g. added per-request latency) from `/docs/collector/benchmarks/` — page exists in the docs but was not fetched in this pass.
- **Grafana- and Sentry-specific technical integration detail** — `opentelemetry.io`'s own vendor/ecosystem page confirms both are OTLP-compatible backends but does not itself document the integration mechanics; that material lives on each vendor's own documentation site, outside OpenTelemetry's own docs. This is why the Grafana and Sentry research docs, not this one, carry the integration-mechanics detail.
- A consolidated, cross-repository OpenTelemetry governance page (CNCF Governance Committee, Technical Committee, per-language SIGs) was not found; only the multi-repo *structure* was confirmed via `github.com/open-telemetry` directly, not the formal governance/decision-making process.

## Playwright

- Exact publish dates for recent releases (v1.60-v1.63): a GitHub releases fetch returned '2024' years which contradicts the current date context (2026) and a separate web search implying 2026 dates with matching month/day -- likely a tool/summarization artifact, but not independently confirmed via a verbatim page read.
- Whether Playwright/Microsoft has an explicit, stated policy of never bumping to a 2.0 / handling all breaking changes within the 1.x line -- inferred from observed release-notes content, not from a dedicated versioning-policy page (none was found).
- Full API-mapping detail of the official Protractor migration guide (playwright.dev/docs/protractor) -- confirmed the page exists and its headline claim (eliminates webdriver-manager/Selenium dependency) but did not deep-fetch its full content.
- Whether cross-origin iframe access restrictions are documented anywhere on playwright.dev/docs/frames -- the fetched excerpt did not address this topic at all (absence of coverage, not a confirmed non-limitation).
- Whether Playwright MCP has a dedicated, more extensive security-guidance page beyond the introduction page's implicit signal (the browser_run_code_unsafe tool name) -- playwright.dev/mcp/configuration/* subpages were not directly fetched.
- Precise official-doc wording confirming release cadence (~4-6 weeks) -- this figure is an inference from observed minor-version gaps, not from an explicit cadence statement on an official page.

## PostgreSQL

- Exact GA date for PostgreSQL 19 - only Beta 3 (2026-08-13) confirmed; Sept/Oct GA window is inferred from historical cadence, not confirmed.
- Whether PG18's documented breaking changes will change before PG19 GA - v19 release-notes pages not fetched since content is still in flux.
- Target removal version for md5 password authentication - PG18 notes only a deprecation-warning stage, no stated removal version.
- Whether postgresql.org has any official first-party container/Docker deployment documentation - none was found in pages fetched, but absence isn't fully confirmed (the widely-used Docker Hub postgres image appears to be Docker's Official Images program, not authored by postgresql.org itself).
- Full shared-memory/buffer-pool/lock-manager architecture detail - the tutorial-arch.html page explicitly stated this wasn't covered in the fetched section; likely documented elsewhere in the internals chapter but not individually fetched this pass.

## Prisma

- Whether Prisma 8.0.0 has reached (or will imminently reach) stable/GA status is contradictory across official sources: the docs site (prisma.io/docs/orm) presents v8 as the default/primary experience, but GitHub Releases shows only prerelease rc builds (latest rc.8, 2026-08-26) and the official announcement blog says v7 remains the production choice with a 12-month support commitment. Re-check github.com/prisma/orm/releases for a non-prerelease 8.x.x tag before treating v8 as production-ready.
- Prisma 8 pagination API naming conflicts between two official sources: the /docs/orm/reference/orm-client page's code example still uses take()/skip(), while the v8.0.0-rc.7 GitHub release notes state pagination was renamed to limit()/offset(). Not resolved which is current for the actual pinned version.
- The Prisma 8 claim of '~90% the speed of raw PostgreSQL' has no benchmark methodology, dataset, or reproduction steps surfaced in the fetched docs summary — treated as an unverified vendor claim.
- Exact scope of 'major API changes to aggregates and constraints' in v8.0.0-rc.2 was not detailed beyond the release-note title.
- Exact before/after type mapping for the v8.0.0-rc.6 change to PostgreSQL temporal columns (moved to explicit Temporal representations or text) was not confirmed beyond the release-note title.
- Current relationship between Prisma Pulse (real-time event streaming product) and the newer Prisma Compute/Postgres/Accelerate product lineup was not confirmed in this research pass.
- Exact release-candidate at which MongoDB support lands within the v8 line was not confirmed — only that it's targeted for the v8 cycle rather than v7.
- Whether prisma.io/docs/orm/reference/orm-client's example code (take()/skip(), db.orm.public.User accessor shape, etc.) reflects the final v8 GA API or an in-flux RC-era snapshot could not be independently verified against a stable release.

## Python

- Whether the 'Idioms and Anti-Idioms in Python' HOWTO (howto/doanddont.html) still exists in the current Python 3.14 documentation tree — a fetch returned only the generic docs landing page rather than anti-idiom content, consistent with removal but not conclusively confirmed vs. a fetch-tooling artifact.
- Exact current default value and introducing version of sys.set_int_max_str_digits() (the int<->str conversion length guard) — referenced by inference but not independently re-verified with a dedicated fetch of library/stdtypes.html#int-max-str-digits.
- Python 3.9's precise end-of-life date — its row was not present in the fetched devguide versions table excerpt; likely already past EOL as of the 2026-09-09 research date but not directly re-confirmed against the live table.
- The current, exact URL and disclosure-timeline process for the PSF/Python Security Response Team's official CVE handling — devguide.python.org/security-adjacent pages were not deep-fetched in this pass.
- Exact current content of extending/cporting.html (Porting Extension Modules to Python 3) for 3.x-to-3.(x+1) porting specifics — page was referenced but not deep-fetched.
- Whether alternative CPython implementations (PyPy, Jython, IronPython) are still discussed anywhere in current docs.python.org content — no current page comparing implementations was located in this pass.

## React

- Whether current react.dev docs use the term "Fiber" anywhere for React's internal reconciliation architecture — not found in pages fetched; react.dev's render/commit explanation stays conceptual.
- Full breaking-change content of the React 17->18 upgrade guide (react.dev/blog/2022/03/08/react-18-upgrade-guide) — only its existence/title was confirmed via search, not fetched in full.
- Exact release date and full changelog content for React 19.2.8 (and whether 19.2.5-19.2.7 carried further security-relevant fixes) — only npm dist-tags and GitHub release-title search snippets were obtained, not the full CHANGELOG.md or GitHub releases page.
- Whether React 18.x or earlier majors have any official, time-bounded security-backport support-window commitment now that 19.x is current -- no LTS/support-window policy page was found.
- Whether react.dev publishes a standalone security-policy or responsible-disclosure page beyond the two RSC CVE blog posts from Dec 2025.
- Detailed content of the React Compiler debugging/troubleshooting guide at react.dev/learn/react-compiler/debugging -- existence confirmed via search, not fetched in full.
- Whether the React Compiler has an official first-party SWC (non-Babel) integration, or is Babel-only with frameworks bridging into SWC pipelines.
- Full content of the library-compilation guide at react.dev/reference/react-compiler/compiling-libraries -- existence confirmed via search, not fetched in full.
- Whether react.dev currently hosts any first-party, end-to-end 'how to test a React component' tutorial beyond the act() reference page and the two testing-tool deprecation-warning pages -- testing documentation appears comparatively thin.

## Redis

- Exact quorum/failover mechanics of Redis Sentinel — page fetched but body exceeded capture size in this pass; only table of contents confirmed
- Precise scope of what Redis 8.0's new io-threads implementation parallelizes (network I/O only vs. more)
- Whether an official first-party app-testing guide (fake Redis, Testcontainers module, etc.) exists anywhere on redis.io/docs — none found in pages reached, but site was not exhaustively crawled
- Whether an official Kubernetes deployment path exists for plain Redis Open Source distinct from the commercial Redis Enterprise/Software operator (only the latter was documented and fetched)
- Release-cadence claim ('new major version yearly, minors ~6 months apart') was sourced via a WebSearch summary of a third-party tracker (endoflife.date), not independently confirmed by directly reading an official redis.io page
- Full changelog contents and exact release date for Redis 8.10.1 were not independently fetched from an official page
- The 'Other security topics' subsection linked at the bottom of the main security page was not individually followed to its subpages
- Dedicated official memory-optimization and CPU-optimization guidance pages (linked from the optimization/ index) were not fetched in this pass

## Sass

- Exact LibSass end-of-life date (~October 2025) was surfaced only via a search-engine summary of sass-lang.com content, not independently re-fetched and quoted from a primary page — treat as unconfirmed pending direct verification of the source page.
- Whether sass-lang.com documents any numeric limits (max recursion depth, max nesting depth) was not found in pages retrieved; could not confirm absence vs. simply not being surfaced by the fetches performed.
- Full list of older breaking-changes entries (versions 1.0.0-1.55.0) was not individually re-fetched; only summarized as 'also listed' per the breaking-changes index page summary.

## Sentry

- The precise, itemized list of field names/patterns redacted by Sentry's *default* server-side data scrubber (as opposed to the SDK-side `beforeSend` pattern and the opt-in Advanced Data Scrubbing rules, both documented in detail) was not extracted from the fetched page content — only that such a default exists, and that Advanced Data Scrubbing is a separate, configurable layer.
- A Python SDK (`sentry-sdk`) major-version migration guide, and a Python-specific breaking-changes history analogous to the detailed JS v7→v8/v8→v9/v9→v10 series, was not located/fetched.
- The exact SSL/TLS protocol versions, cipher suites, and plan-by-plan data-retention windows referenced from the `security-legal-pii` index page were not independently fetched.
- Whether docs.sentry.io publishes a single consolidated SDK-version × language-runtime × framework-version compatibility matrix; version floors here were assembled from multiple pages rather than one authoritative table.
- Numeric SDK performance-overhead benchmarks (CPU/memory/latency cost of stack-trace capture, breadcrumb recording, or tracing) — only qualitative guidance and one named trade-off (eager profiler mode's constant CPU overhead) were found.
- A dedicated official guide or first-party plugin for testing Sentry-instrumented application code (asserting on captured events in Jest/pytest/etc.) — the closest documented pattern is conditional `Sentry.init()` skipping plus `debug: true`.
- Exact authentication-token scopes required per Sentry Web API endpoint, beyond the one "Organization Token" reference found in the release-automation/GitHub Actions context.
- [Inference, not confirmed in docs] Sentry's positioning as "not a metrics/logging platform in the Prometheus/OpenTelemetry sense" is inferred from two separate documented facts — the SDK's Metrics API being removed entirely in v9, and Logs' plan-tier-gated 7/14/30-day retention — rather than from any single page that states this boundary explicitly by name-checking Prometheus or OpenTelemetry Metrics.

## shadcn/ui

- Whether shadcn/ui publishes a first-party, general component-testing guide (Vitest/Jest/Testing Library) beyond the AI-SDK-specific deterministic chat-streaming helper — a GitHub-registry starter template reference to vitest.config.ts/docs/testing.md surfaced in search but was not confirmed against a live official docs page.
- Whether the CLI v4 changelog entry omits breaking changes vs CLI v3 because there genuinely are none, or because the fetched page simply doesn't enumerate them — the page itself does not address migration/breaking-change details from v3.
- Whether older major CLI versions receive any backported security/bug fixes — no LTS or support-window policy was found in the fetched changelog or docs.
- The Base UI v1.6.0 / 6M-weekly-downloads figure is quoted from shadcn's own changelog about a third-party project (Base UI), not independently verified against Base UI's own official docs.

## Socket.IO

- Minor date discrepancy between an earlier web-search summary (npm showing 4.8.3 'last published 8 months ago' relative to research date) and the changelog page's explicit Dec 23, 2025 date for 4.8.3 -- flagged as Unresolved in the doc (Section 12) rather than guessed at, since neither raw timestamp was independently reconciled.
- No official 'migrating from a different real-time library' (e.g. raw ws, SockJS) guide was found -- official migration content is scoped only to major-version-to-major-version (2.x->3.0, 3.x->4.0).
- No formal LTS/support-window policy was found published anywhere in the official docs or changelog; only signal is that 3.x is called 'no longer actively maintained'.

## Swagger

- Whether 'Swagger Studio', 'Swagger Explore', and 'Swagger Portal' (seen on swagger.io/docs landing page) are a rename/successor of SwaggerHub, a parallel new product line, or an in-progress site migration — the swagger.io/tools/ page still lists the classic lineup with no mention of these names
- Exact opt-out configuration key/env var for Swagger Editor's Scarf analytics reporting — not visible in the fetched README excerpt
- Minor version discrepancy: Swagger UI README states current version 5.32.0 while the releases page's latest tag is 5.32.15 (likely README staleness, not a real conflict)
- Whether Swagger Editor security vulnerability reports route to the same security@swagger.io address used for Swagger UI — no SECURITY.md found in the swagger-editor repo
- Whether any JS-config-level breaking changes shipped in Swagger UI v5.0.0 — release notes list only additive features/fixes with no explicit breaking-changes section
- Specific unit-test/Cypress test-runner commands for Swagger UI's own test suite — CONTRIBUTING.md returned 404 and the fetched setup doc did not include test commands
- Direct URL of the referenced 'detailed blog post on the Swagger website' covering v3→v4 migration guidance
- Full per-major-version OpenAPI spec compatibility matrix for Swagger UI (only the current 5.32.0 line's supported spec versions were captured)

## Tailwind CSS

- Whether Tailwind Labs has a formally documented LTS policy (explicit end-of-support date, guaranteed backport scope) for the v3 line, versus this being informal best-effort maintenance — evidence supports ongoing v3 patching but no documented support-window commitment was found.
- Whether `@tailwindcss/postcss` still requires a separately configured `autoprefixer` PostCSS plugin in any edge cases; the Compatibility page implies Lightning CSS handles vendor prefixing internally, but this was not independently re-verified against a raw fetch of the PostCSS installation page.
- The exact official wording/section confirming `bg-gradient-*` was renamed to `bg-linear-*` as a breaking change — this was inferred from the v4 announcement's feature list by an AI-summarized fetch rather than read directly from an explicit 'breaking changes' bullet; worth re-verifying against the upgrade guide's literal text before downstream use.
- Whether an official v2-to-v3 (or earlier) migration guide still exists on any live/archived Tailwind Labs-maintained host; only the v3-to-v4 guide was directly confirmed in this research pass.
- No dedicated official Tailwind testing guide, CSP/security guide, or centralized debugging/troubleshooting page was found; absence was inferred from failed targeted searches rather than confirmed via an official 'no such page exists' statement, so a page could theoretically exist at an unindexed URL.

## Three.js

- Exact date three.js's canonical docs infrastructure switched to the current JSDoc-generated system / dropped i18n (only known to be 'r181->182' per migration guide, no calendar date found)
- Whether first-party TypeScript type definitions have since been folded into the core 'three' npm package (Installation manual page still says types are 'community-maintained' as of this fetch)
- Exact release that fully removed the CommonJS build (r186 changelog says 'Deprecate CommonJS build' but package.json on dev branch, fetched same day, still lists a require/./build/three.cjs export)
- No official docs page found covering cross-origin texture/asset loading security (crossOrigin attribute, canvas tainting, CSP guidance for WebGL/WebGPU contexts)
- No official first-party guide for how application developers (as opposed to three.js contributors) should test their own three.js apps
- Existence/usage of an official browser 'Inspector' devtool is only inferable from r186 changelog entry titles (e.g. 'Add split screen...CSP compliance' under an Inspector heading) — no dedicated docs page was found describing it
- Apparent tension between the general 'upgrade in increments of 10' migration policy and the WebGPURenderer-specific advice to 'upgrade to the latest version whenever possible' is left unresolved as stated by the docs themselves

## TypeORM

- Exact current minimum TypeScript version — docs say 4.5+ but this may be stale given the pace of 2026 changes around v1.0.
- Whether TypeORM publishes a formal internal driver-interface/plugin-authoring document — none found.
- Complete enumerated Repository/EntityManager method list — only a subset (findOneBy, save, findBy+In, exists, etc.) was directly verified from fetched pages; a 'Repository APIs' reference page is referenced but was not separately fetched.
- Which released version line(s) (0.3.x vs 1.x) currently receive official security backports — not stated on the security policy page.
- Any officially assigned CVE identifiers against TypeORM — none surfaced in official sources.
- Official 0.3.x end-of-support date or any formal LTS/support-window policy — no such page was found; TypeORM does not appear to document one.
- Full content of the 'Indexes' and 'Query Hints' performance sub-pages — referenced by the performance index page's navigation but not individually fetched in this pass.
- Whether an official TypeORM testing guide exists — extensive searching found none; all testing patterns discovered were third-party/community sources and were excluded from citation per project rules.

## TypeScript

- Whether the microsoft/TypeScript wiki 'Architectural Overview' page has been updated to describe the Go-native (7.0) compiler architecture, or still only documents the legacy JavaScript compiler internals -- could not confirm either way in this pass.
- The 'Migrating from JavaScript' official tutorial page's example tsconfig.json uses target: es5, which appears inconsistent with TypeScript 6.0's documented removal of es5 as a valid target value -- unclear whether the live page is simply stale/not yet updated post-6.0, or whether the fetched content was cached/stale at fetch time.
- The microsoft/TypeScript GitHub wiki 'Roadmap' page fetch returned content referencing TypeScript 5.0/4.x as the most recent releases (pre-2023 era), which is inconsistent with the confirmed 2026 version landscape (5.9/6.0/7.0) -- most likely a stale fetch/cache artifact rather than the page's true live content, but not independently re-verified. The 'quarterly release cadence' figure derived from it is only an inference, not a directly confirmed official claim.
- Whether Microsoft publishes a distinct security-disclosure/CVE policy page for the TypeScript compiler on GitHub (as it does for many Microsoft OSS projects) -- not confirmed from typescriptlang.org itself; would need direct verification against the microsoft/TypeScript repo's security policy, which was not checked in this pass.
- Exact documented semantics of the tsconfig mapRoot and sourceRoot options were listed by category but not individually re-verified beyond their presence in the Emit category of the tsconfig reference.

## Vite

- Exact date of the vitejs.dev → vite.dev canonical-domain migration was not directly confirmed in fetched pages, only inferred from coexisting version-pinned subdomains.
- Exact Vite 8.0 release date (March 12, 2026) came from a WebFetch tool summary of the announcement blog post, not independently cross-checked against raw HTML text.
- The claim that server.fs.strict has defaulted to enabled 'since Vite 2.7' came from a WebFetch summary and was not independently re-verified against primary doc text.
- Whether vite.dev's main guide has a dedicated standalone 'Testing' page (as opposed to only a passing mention on the /guide/why page) was not confirmed — testing coverage on the official vite.dev site itself appears thin, with the substantive testing docs living on the separate (same-org) vitest.dev site.
- Full content of pre-v7 major-version migration guides (e.g. v5→v6, v6→v7) was not independently fetched in this pass; only the current v7→v8 guide was retrieved in full.
- Real-world Rolldown speedup figures (Linear 46s→6s, Beehiiv 64% reduction) are relayed via the official blog post but are themselves third-party-reported anecdotes rather than Vite's own benchmark methodology, so their generalizability is uncertain.
- Exact Node.js version floor for pre-v8 majors (to contrast with v8's Node 20.19+/22.12+ requirement) was not independently re-verified in this pass.

## Vitest

- Exact list of 'several deprecated entry points removed entirely' in v5.0 -- the migration guide references this without enumerating the specific entry points.
- Precise scope of the documented 'limitation when using assertion functions such as assert' in in-source testing -- the fetched page pointed to the API docs for detail without giving it inline.
- Whether aroundEach/aroundAll hooks existed before v5.0 or were introduced in v5.0 -- could not pin down the introduction version from pages fetched.
- Full content of the Vitest 4.1 announcement blog post itself was not fetched, only its role as the current security-backport target.
- Whether vitest.dev's version-history claim ('specific historical release dates') fully matches github.com/vitest-dev/vitest/releases was not independently cross-verified line by line.

## Vue.js

- Exact bundle-size/footprint figures were not separately investigated for Vue core (unlike the Drizzle precedent file) - not flagged as a specific unresolved item since no conflicting figures were encountered, but not independently verified either.
- Whether Vue 3.6 / Vapor Mode has been promoted from release-candidate to the stable npm 'latest' tag between this research pass's npm snapshot (3.5.42 stable, 3.6.0-rc.7 as newest rc, captured 2026-09-09) and any later point of use - community sources describe Vapor as 'confirmed stable' by Evan You, but npm dist-tags and the official 3.6.0-rc.1 GitHub release notes at time of research did not corroborate general-availability/production-ready status. Must be re-verified against live npm and vuejs.org before citing as stable.
- Vue Router's exact current major-version support matrix (the intro-page AI-extracted summary mentioned both v4.x and v5.x as 'current' plus v3.x for older Vue - this reads as internally inconsistent and was not resolved against the raw page).
- Whether any official or endorsed extended-support/security-patch channel exists for Vue 2 post-EOL (Dec 31 2023) - no such endorsement was found on vuejs.org pages fetched in this pass, but absence of evidence is not proof of absence.
- What Vue's separate npm 'csp' dist-tag build (1.0.28-csp) specifically changes (e.g., CSP unsafe-eval avoidance) - noted in the Security section as unverified in this pass.
- Drizzle-style exact architecture of Vue Devtools' Vite-only features (asset inspection, transform-step inspection) beyond the feature list extracted - underlying mechanism not independently confirmed.

## WebRTC

- Whether webrtc.org (redesigned) or webrtc.github.io/webrtc-org/ (archived) is the forward-canonical doc host, or just an old/new snapshot pair of the same GitHub Pages project.
- Whether Chrome/Firefox/Safari's browser-embedded WebRTC implementations are built directly on the webrtc.googlesource.com/src native code library — not explicitly confirmed in the fetched native-code overview excerpt.
- The current canonical source repository for adapter.js/webrtc-adapter, given github.com/webrtc/adapter is now marked a read-only fork.
- RTCDataChannelInit fields beyond negotiated/id (ordered, maxRetransmits, maxPacketLifeTime, protocol) were not present in the specific MDN guide page fetched.
- TURN server credential-rotation mechanisms (e.g., time-limited/shared-secret schemes) — not found documented on an official WebRTC page in this pass.
- Mesh/SFU/MCU multi-party scaling guidance and any official participant-count limits — not found on an official page; treated as inference only from the one-peer-per-RTCPeerConnection API model.
- Whether there is a current official page equivalent to a 'test.webrtc.org' browser capability/connectivity test tool.

## WebSocket API

- Exact browser-implementation-specific boundary of what counts as 'same device/network' for the ws:// secure-context exception referenced by MDN's client guide — not pinned down in normative text
- Whether any WHATWG spec changes between the 2021 spec-split and the May 2023 http(s)-scheme change constitute additional undocumented breaking changes — only top commits were surfaced, not an exhaustive history
- Whether Chrome DevTools / Safari Web Inspector have official first-party WebSocket frame-inspection documentation equivalent to Firefox's (only Firefox's was directly fetched and cited)
- Formal LTS/support-window concept does not meaningfully apply to a Living Standard / Internet Standard — treated as evergreen by definition rather than left genuinely uncertain
