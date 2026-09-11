# GitHub — Technology Research

Research date: 2026-09-09. Primary source: `docs.github.com/*` (canonical documentation host — confirmed reachable and current at time of research). Secondary official sources used only to confirm changelog/release facts not fully mirrored in the docs tree: `github.blog/changelog/*` and `github.blog/developer-skills/*` (official GitHub blog). All claims are tagged per this project's convention: `[Source: <url>]` for documented facts, `[Inference, not confirmed in docs]` for reasoning, "Not documented / could not verify" where docs did not cover something in the pages fetched, and "Unresolved: ..." where confidence is genuinely low.

**Doc host note**: No evidence of a canonical-doc-host migration was found — `docs.github.com` remains the single documentation host for GitHub.com, GitHub Enterprise Cloud (GHEC), and GitHub Enterprise Server (GHES), with per-product/per-version URL segments (e.g. `/en/enterprise-server@<version>/...`, `/en/enterprise-cloud@latest/...`). The legacy `developer.github.com` and `help.github.com` hosts redirect into `docs.github.com`.

**Scope note**: Per the task instructions, this research covers **core GitHub product** — repositories, pull requests, issues, the REST/GraphQL APIs, webhooks, security features, GitHub Pages/Packages, and Enterprise deployment/administration. It explicitly excludes **GitHub Actions / CI-CD**, which is covered as a separate technology. Where a page's content leaned entirely on Actions (e.g. some Packages authentication flows), only the non-Actions-specific facts are included here.

---

## 1. Core concepts

[Source: https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories] A **repository** is GitHub's fundamental storage unit, holding a project's files and each file's revision history; it can be shared with collaborators and set to public or private visibility.

[Source: https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories] Core repository terminology as documented: a **branch** is "a parallel version of your code that is contained within the repository, but does not affect the primary or main branch"; a **fork** is a derivative repository sharing code/history with the original; a **clone** downloads a full local copy; **merge** applies changes from one branch to another; a **pull request** is a proposal to integrate changes between branches; **remote** refers to a repository hosted on GitHub (vs. local); **upstream** is the original repository in a fork/clone relationship.

[Source: https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories] Repositories support collaboration tooling beyond raw code storage: **Issues** (feedback/bug tracking), **Discussions** (community conversation), **pull requests** (proposing changes), and **Projects** (organizing tasks/priorities).

[Source: https://docs.github.com/en/get-started/using-github/github-flow] **GitHub Flow** is documented as "a lightweight, branch-based workflow" applicable to developers and non-developers alike, built around isolated branches and peer review. Its steps: create a branch → make changes and commit (with isolated, complete commits — e.g. "put the variable rename in one commit and the tests in another commit") → open a pull request → address review comments via additional commits → merge → delete the branch.

[Source: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-merge-methods-on-github] Three pull-request **merge methods** are documented: **merge commit** (default — all source-branch commits plus a new merge commit are added to the base branch), **squash and merge** (all PR commits are squashed into one commit on the base branch, producing a more linear/simplified history), and **rebase and merge** (all PR commits are individually replayed onto the base branch without a merge commit, resembling a fast-forward merge but rewriting commit metadata).

[Source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets] A **ruleset** is "a named list of rules that applies to a repository or to multiple repositories in an organization," governing push access, force-pushes, deletions, signed-commit requirements, and (for push rulesets) file-extension/path/size restrictions.

---

## 2. Architecture

GitHub.com and GitHub Enterprise Cloud are continuously-deployed SaaS products; GitHub does not publish a public internal-architecture reference for GitHub.com's own infrastructure comparable to, e.g., a self-hosted server's architecture diagram. [Inference, not confirmed in docs] This research therefore documents the architecture facts GitHub *does* publish: the product-deployment topology (Cloud vs. Server) and the client/API surface, rather than GitHub.com's internal infra.

[Source: https://docs.github.com/en/enterprise-cloud@latest/admin/overview/about-github-enterprise-cloud] **GitHub Enterprise Cloud (GHEC)** is a GitHub-hosted deployment option adding enterprise features (SAML authentication, additional Actions minutes, restriction of email notifications to verified domains, etc.) on top of GitHub.com, organized under an **enterprise account** that centrally manages multiple organizations.

[Source: https://docs.github.com/en/enterprise-cloud@latest/admin/overview/about-github-enterprise-cloud] For **GHEC with data residency**, the enterprise is hosted on a dedicated subdomain of `GHE.com`, and customers can choose a data-residency region — documented regions include the EU (including EFTA countries), Australia, the US, and Japan; data resides in the US by default otherwise.

[Source: https://docs.github.com/en/enterprise-cloud@latest/admin/overview/about-github-enterprise-cloud] **GitHub Enterprise Server (GHES)** is the alternative deployment: a self-hosted instance run on the customer's own infrastructure, as opposed to GHEC's GitHub-hosted model. Purchasing "GitHub Enterprise" grants access to both Cloud and Server deployment options.

[Source: https://docs.github.com/en/migrations/using-github-enterprise-importer/understanding-github-enterprise-importer/about-github-enterprise-importer] GHES instance version compatibility for migration tooling is pinned to specific minimums (e.g. GHES 3.4.1+ as a supported Enterprise Importer source), which [Inference, not confirmed in docs] implies GHES runs as versioned, installable server software distinct from the continuously-deployed GitHub.com/GHEC codebase.

[Source: https://docs.github.com/en/webhooks/about-webhooks] At the integration-architecture level, GitHub exposes an **event-driven webhook model**: a registered target URL receives an HTTP POST with event data whenever a subscribed event occurs, as an alternative to polling the REST/GraphQL APIs.

Not documented / could not verify: a canonical page diagramming GitHub.com's own internal service architecture (e.g. Git storage backend, MySQI/Spokes/DGit-style replication) — GitHub does not appear to publish this as end-user documentation.

---

## 3. APIs

[Source: https://docs.github.com/en/rest/about-the-rest-api/about-the-rest-api] The **REST API** is described as "GitHub's API to build scripts and applications that automate processes, integrate with GitHub, and extend GitHub" — e.g. triaging issues, building analytics dashboards, managing releases.

[Source: https://docs.github.com/en/rest/about-the-rest-api/api-versions] The REST API is **date-versioned**: each version is named after its release date (e.g. version `2026-03-10` was released Tue, 10 Mar 2026). The version is specified per-request via the `X-GitHub-Api-Version` header.

[Version-sensitive, Source: https://docs.github.com/en/rest/about-the-rest-api/breaking-changes?apiVersion=2026-03-10] Requests that omit the `X-GitHub-Api-Version` header default to version **`2022-11-28`** — documented as "the first version of the GitHub Free, Pro & Team REST API after date-based versioning was introduced," with no breaking changes of its own.

[Source: https://docs.github.com/en/rest/about-the-rest-api/api-versions] **Breaking changes** are only introduced in a new dated API version, with advance notice given beforehand; **additive (non-breaking)** changes roll out to all supported versions simultaneously. When a new version ships, the prior version remains supported for **at least 24 more months**.

[Source: https://docs.github.com/en/graphql] The **GraphQL API** offers "more precise and flexible queries than the GitHub REST API," letting callers define exactly the data shape they want in a single request; GitHub publishes a dedicated REST→GraphQL migration guide and a GraphQL changelog spanning 2017 onward.

[Source: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps] Two distinct app/integration models exist: **GitHub Apps** (short-lived ~1-hour tokens minted via a private key; fine-grained, per-resource permissions; installed per-repository/organization with admin approval; acts as its own bot identity `@appname[bot]`; rate limits scale with installed repositories/org users) and **OAuth Apps** (long-lived tokens obtained via user authorization; coarser scopes like `repo`/`public_repo`; acts as the authorizing user; fixed rate limit of 5,000 requests/hour/user).

[Source: https://docs.github.com/en/webhooks/about-webhooks] **Webhooks** let integrations "subscribe to events happening in a software system and automatically receive a delivery of data" via HTTP POST, avoiding the need to poll the REST/GraphQL APIs — documented as scaling better and avoiding rate-limit consumption versus polling.

[Source: https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries] Webhook payload authenticity is verified via an **HMAC-SHA256 signature**: GitHub signs the payload with a shared secret and sends it as the `X-Hub-Signature-256` header (`"sha256=" + hexdigest`); recipients must recompute the hash and compare it using a constant-time comparison function to avoid timing attacks, and must treat the payload as UTF-8.

[Source: https://docs.github.com/en/rest/deployments/deployments] The **Deployments API** lets tooling create a `deployment` (targeting a named environment such as production/staging/qa) without granting GitHub direct server access; GitHub fires a `deployment` event that external systems consume, then those systems report back deployment status (`success`/`failure`/`error`/`pending`, optionally with `description`/`log_url`). By default, a successful deployment marks prior non-transient, non-production deployments to the same environment `inactive`.

Not documented / could not verify: a single canonical page enumerating every REST media type (`Accept` header variants) in one place — media types are documented per-endpoint rather than centrally, based on the pages fetched.

---

## 4. Configuration

[Source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets] Repository governance is configured via **rulesets**: up to 75 per repository, targetable to branches/tags via `fnmatch`-style patterns (e.g. `releases/**/*`), with an **Active** or **Disabled** enforcement status. Multiple rulesets can target the same branch simultaneously (unlike the older single-branch-protection-rule model), and when several rulesets overlap on a target, "the most restrictive version of the rule applies." Bypass permissions can be scoped to specific roles, teams, or GitHub Apps.

[Source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets] Rulesets are visible to anyone with read access to the repository (improved transparency versus legacy branch protection rules), and support commit-metadata rules such as commit-message pattern validation, in addition to push-access, force-push, deletion, and signed-commit controls.

[Source: https://docs.github.com/en/webhooks/about-webhooks] **Webhook** configuration is per-repository/organization/app: a target URL, an optional shared secret (for HMAC signature validation), a content type, and a selected set of subscribed event types.

[Source: https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-two-factor-authentication] **Two-factor authentication (2FA)** configuration supports multiple methods: TOTP authenticator apps, SMS text codes, FIDO2 security keys (including platform authenticators like Apple Touch ID / Windows Hello), passkeys, and GitHub Mobile (public-key based). Recovery codes and fallback methods are configurable to prevent lockout.

[Source: https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages] **GitHub Packages** supports configuring per-registry publishing across npm (`package.json`), RubyGems (`Gemfile`), Maven (`pom.xml`) / Gradle (`build.gradle`), NuGet (`.nupkg`), and Docker/OCI container images, with permissions inherited from the hosting repository or, for some registries, set granularly per user/organization.

[Source: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages] **GitHub Pages** is configured per-repository as either a user/organization site (`<owner>.github.io` repository) or a project site (served from a project repository's configured branch/folder), with an optional custom-domain configuration in place of the default `github.io` domain.

[Source: https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization] Organization-level **audit log** access/configuration is restricted to organization owners, found under Organization Settings → Archive → Logs → Audit log; the log supports filter/search by operation type, repository, actor, action, timestamp, and location, and can be exported as JSON or CSV (export capped at 100 MB compressed or 10 minutes processing time, whichever comes first).

---

## 5. Recommended patterns

[Source: https://docs.github.com/en/get-started/using-github/github-flow] **GitHub Flow** (branch → commit → PR → review → merge → delete branch) is the documented lightweight recommended workflow, with an explicit recommendation to keep each branch scoped to "a set of unrelated changes" and each commit isolated/complete (e.g. separate a variable rename from its accompanying tests) so reviews stay focused and reverts stay clean.

[Source: https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories] Recommended repository practices: include a README, LICENSE, CITATION file (where applicable), contribution guidelines, and code of conduct; enable free security tooling — Dependabot alerts, secret scanning, push protection, and code scanning — on public repositories; add a `SECURITY.md` with vulnerability-reporting instructions and enable private vulnerability reporting; use protected branches (required status checks, required PR reviews) for important branches like `main`.

[Source: https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories] For internal team collaboration, GitHub's documented recommendation is to **"favor branching over forking"** — forking is reserved for external, unaffiliated contributors, while regular team members work from a single shared repository.

[Source: https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories] Large binary files should be tracked via **Git LFS** rather than committed directly, to avoid repository performance degradation.

[Source: https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api] Recommended REST API integration patterns: **prefer webhooks over polling**; if polling is unavoidable, do so on a fixed schedule using **conditional requests** (store `etag`/`last-modified` response headers, resend as `if-none-match`/`if-modified-since` — successful `304` responses don't consume the primary rate limit); use `Link` header pagination rather than hand-constructed pagination URLs and keep a stable sort order to raise the chance of `304`s; issue mutating (`POST`/`PATCH`/`PUT`/`DELETE`) requests **serially rather than concurrently**, spaced at least one second apart, to avoid secondary rate limits; on `429`/rate-limit errors, honor the `retry-after` header if present, otherwise back off exponentially with a retry cap; investigate rather than blindly retry recurring `4xx`/`5xx` errors.

[Source: https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/testing-webhooks] Recommended local webhook development pattern: use **smee.io** as a public proxy URL, run the `smee-client` locally to forward deliveries to a local server/port, and verify at three checkpoints — GitHub's delivery confirmation, smee.io receipt, and local-server processing — with the ability to **redeliver** a past webhook delivery from GitHub's UI for repeat testing without generating new events.

---

## 6. Anti-patterns

[Source: https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories] Explicitly documented anti-patterns: relying on **forking for internal team collaboration** (reserve forking for external/unaffiliated contributors — branching is recommended instead); **committing large files without Git LFS**, which degrades repository performance; and **skipping security features and documentation** (no Dependabot/secret scanning/code scanning, no README/SECURITY.md).

[Source: https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api] Explicitly documented API anti-patterns: **polling the REST API instead of using webhooks** for data that changes on an unpredictable schedule; issuing **concurrent mutating requests** instead of a serial queue (triggers secondary rate limits); **ignoring repeated 4xx/5xx errors** instead of investigating them; and continuing to hammer the API while already rate-limited, which risks integration suspension.

[Source: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github] Pushing files over the documented size thresholds without LFS is an anti-pattern GitHub actively warns against: files over 50 MiB trigger a warning (push still succeeds but harms performance), the web-upload UI caps at 25 MiB, and files over 100 MiB are **hard-blocked** by Git pushes.

Not documented / could not verify: a single consolidated "anti-patterns" reference page comparable to a style guide — the anti-patterns above are each drawn from best-practice pages that state the *recommended* pattern and its documented failure mode, not from a dedicated anti-pattern catalog.

---

## 7. Security

[Source: https://docs.github.com/en/code-security] GitHub's documented security-feature set spans: **Dependabot** (dependency vulnerability alerts, automated security-update PRs, version-update PRs, malware detection, customizable auto-triage rules), **code scanning** (default or advanced setup, CodeQL analysis, third-party SARIF upload support, AI-powered detections for languages beyond CodeQL coverage, merge protection, and autofix), **secret scanning** (pattern matching plus validity checks; **push protection** blocks contributors from pushing detected secrets; public-repository monitoring extends detection beyond the enterprise boundary; supports custom patterns and delegated bypass), **security advisories** (private coordinated disclosure workspace per repository, plus a public Advisory Database aggregating CVEs and GitHub-originated advisories), and **supply-chain security** (dependency graph, license/provenance visibility, immutable releases).

[Source: https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-two-factor-authentication] [Version/date-sensitive] Since **March 2023**, GitHub has required 2FA for users who contribute code on GitHub.com, rolled out group-by-group with a **45-day enrollment window** per notified group — not a blanket requirement for every account, but mandatory for the notified cohorts; other users are "strongly encouraged" but not required.

[Source: https://docs.github.com/en/authentication] Documented authentication mechanisms: **personal access tokens** (used in place of a password for CLI/API auth, with expiration and revocation management), **SSH keys** ("a secure channel over an unsecured network"), **passkeys** (passwordless sign-in that also satisfies 2FA), and **commit signature verification** (GPG, SSH, or S/MIME signatures so "other people will know that your commits come from a trusted source").

[Source: https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries] Webhook security requires a random, high-entropy shared **secret** (never hardcoded/committed), HMAC-SHA256 payload signing via the `X-Hub-Signature-256` header, constant-time comparison on verification to prevent timing attacks, and awareness that intermediary proxies/load balancers must not mutate the payload before verification.

[Source: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps] From a least-privilege standpoint, **GitHub Apps** are the documented preference over OAuth Apps for integrations: fine-grained, resource-scoped permissions and short-lived (~1 hour) tokens versus OAuth Apps' broader `repo`/`public_repo`-style scopes and long-lived user tokens.

[Source: https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization] The **organization audit log** (owner-only access, 180-day retention, JSON/CSV export) is the documented mechanism for security monitoring/accountability of member actions.

---

## 8. Performance

[Source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api] REST API **primary rate limits**: unauthenticated requests are capped at **60 requests/hour**; authenticated requests (personal access token) get **5,000 requests/hour**; GitHub Enterprise Cloud raises this to **15,000 requests/hour**; Git LFS has its own limits — 300 requests/minute unauthenticated, 3,000/minute authenticated. GitHub Apps' limits instead **scale with the number of installed repositories and organization users** rather than being a flat number.

[Source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api] REST API **secondary rate limits** additionally cap concurrent requests (max 100), enforce a per-endpoint minimum (900 points/minute), and a CPU-time budget of "90 seconds of CPU time per 60 seconds [of wall time]." Status is exposed via `x-ratelimit-limit` / `x-ratelimit-remaining` / `x-ratelimit-reset` response headers, or via `GET /rate_limit` (documented as itself capable of triggering secondary limits if polled too often).

[Source: https://docs.github.com/en/graphql/overview/resource-limitations] GraphQL API is **point-based**: standard users get **5,000 points/hour**; GHEC organizations and certain app contexts get higher allocations; a **secondary limit of 2,000 points/minute** also applies, with mutation-bearing queries costing 5 points versus 1 point for pure queries. Individual queries cannot exceed **500,000 total nodes**, connection arguments (`first`/`last`) must be in the 1–100 range, and node counts multiply across nested connections (e.g. 50 repositories × 10 issues each = 550 nodes). Query execution is capped at **10 seconds**, after which GitHub returns a 502/504 and additionally deducts points from the next hourly window as a penalty.

[Source: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github] Documented repository-size performance guidance: keep repositories "ideally less than 1 GB, and less than 5 GB is strongly recommended" — larger repositories can degrade GitHub's own infrastructure performance and may prompt GitHub Support intervention; the `github/git-sizer` tool is the documented way to audit repository size/health, and package managers (rather than committing dependencies) are recommended for dependency management.

[Source: https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api] Conditional requests (ETag/`If-None-Match`, `Last-Modified`/`If-Modified-Since`) are the documented mechanism to avoid consuming primary rate limit on unchanged resources, and serial (not concurrent) mutating requests are recommended to avoid secondary limits.

---

## 9. Testing

GitHub does not document a general-purpose "testing framework" for the platform itself (that is Actions/CI territory, out of scope here); its testing-related official guidance is specifically about **testing integrations** (webhooks, apps) against the platform.

[Source: https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/testing-webhooks] Documented webhook testing workflow: (1) confirm GitHub shows a successful delivery for the triggering event, (2) use **smee.io** as a public proxy endpoint plus the `smee-client` npm package to forward deliveries to a local dev server/port during development, (3) verify processing at each of the three hops (GitHub → smee.io → local server), and (4) use GitHub's **redeliver** feature to resend a past webhook delivery for repeat/regression testing without needing to re-trigger the underlying event.

[Source: https://docs.github.com/en/migrations/using-github-enterprise-importer/understanding-github-enterprise-importer/about-github-enterprise-importer] GitHub Enterprise Importer documents support for **trial migrations** — a way to test/validate an org or repo migration path before committing to the real cutover — plus detailed error logging that lets a migration continue past non-critical failures for inspection afterward.

Not documented / could not verify: an official GitHub-hosted API "sandbox"/staging environment for testing REST/GraphQL API integrations against non-production data — the fetched pages describe production rate-limit-aware best practices but no separate sandbox tier.

---

## 10. Deployment

[Source: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages] **GitHub Pages** is documented as "a static site hosting service that takes HTML, CSS, and JavaScript files straight from a repository on GitHub, optionally runs the files through a build process, and publishes a website" — either a user/organization site (`<owner>.github.io` repo, one per account) or a project site (`https://<owner>.github.io/<repositoryname>`, one per repository), with custom-domain support as an alternative to the default `github.io` domain. Visitor IP addresses are logged on every Pages request, authenticated or not, for security purposes.

[Source: https://docs.github.com/en/rest/deployments/deployments] The **Deployments API** is GitHub's documented mechanism for third-party/self-hosted deployment tooling to integrate loosely with GitHub: create a deployment request targeting a named environment, GitHub emits a `deployment` webhook event, external tooling performs the actual deploy and reports status (`pending`/`success`/`failure`/`error`) back via the deployment-status endpoints.

[Source: https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages] **GitHub Packages** functions as a deployment/distribution target for built artifacts across npm, RubyGems, Maven/Gradle, NuGet, and Docker/OCI registries, with public packages free and private packages billed against account-tier storage/transfer allotments.

[Source: https://docs.github.com/en/enterprise-server@latest/admin/overview/about-upgrades-to-new-releases] **GitHub Enterprise Server** is deployed as a self-hosted instance with its own **quarterly feature-release** cadence (each beginning with at least one release-candidate phase) and more frequent **patch releases** ("typically less than five minutes of downtime"). Release candidates are explicitly documented as install-fresh-only — GitHub instructs against upgrading a production instance to a release candidate, and RC test environments must be destroyed rather than upgraded further.

---

## 11. Migration

[Source: https://docs.github.com/en/migrations/using-github-enterprise-importer/understanding-github-enterprise-importer/about-github-enterprise-importer] **GitHub Enterprise Importer (GEI)** is "a highly customizable migration tool designed to help you move your enterprise to GitHub Enterprise Cloud," operable at the repository or organization level. Documented supported sources: **Azure DevOps Cloud**, **Bitbucket Server and Data Center (5.14+)**, **GitHub.com**, **GitHub Enterprise Server (3.4.1+)**, and **GitLab** (cloud and certain maintained self-hosted versions). GEI preserves Git history/metadata and user ownership, supports trial migrations, and logs errors in enough detail to let a migration continue past non-critical failures.

[Source: https://docs.github.com/en/migrations/using-github-enterprise-importer/understanding-github-enterprise-importer/about-github-enterprise-importer] Migrations are run via the **GitHub CLI** (documented as recommended for most users) or the **API** (for advanced customization). Migrations from GHE.com to GHE.com are explicitly **not supported** by GEI; GHES-to-GHE.com transfers instead route through a separate offering, **Enterprise Live Migrations**.

[Source: https://docs.github.com/en/rest/about-the-rest-api/api-versions] **REST API version migration**: moving to a newer dated API version is opt-in per request (`X-GitHub-Api-Version` header); the prior version stays supported for at least 24 months after a new version ships, giving integrators a defined migration window.

[Source: https://docs.github.com/en/graphql] A dedicated **REST-to-GraphQL migration guide** is published for teams moving integrations from the REST API to GraphQL.

---

## 12. Version information

[Source: https://docs.github.com/en/rest/about-the-rest-api/api-versions] [Version-sensitive] The REST API's current dated version at time of research is **`2026-03-10`**; requests without an explicit `X-GitHub-Api-Version` header default to **`2022-11-28`**. [Source: https://github.blog/changelog/2026-03-12-rest-api-version-2026-03-10-is-now-available/] This changelog post confirms `2026-03-10` as newly available (dated March 12, 2026 changelog entry for the March 10, 2026 version).

[Source: https://docs.github.com/en/rest/about-the-rest-api/api-versions] REST API versions are supported for **at least 24 months** after superseded by a newer version.

GitHub.com / GitHub Enterprise Cloud are **continuously deployed SaaS** and are not versioned with a traditional release number in end-user docs. [Inference, not confirmed in docs — no single dated "GitHub.com version" is documented anywhere in the pages fetched; only the REST/GraphQL API surface and GHES carry explicit version numbers.]

[Source: https://docs.github.com/en/enterprise-server@latest/admin/overview/about-upgrades-to-new-releases] **GitHub Enterprise Server** ships **quarterly feature releases** (each starting with ≥1 release-candidate build) plus interim **patch releases**. [Source, from search of docs.github.com] GitHub's documented support model for GHES is to support **at least the four most recent feature releases**; specific versions carry individually announced discontinuation dates (e.g. GHES 3.9 was discontinued 2024-07-09; GHES 3.17 is scheduled for discontinuation 2026-09-22) — Unresolved: the exact standard number of months from a GHES release's GA date to its discontinuation date is not stated as a single fixed figure in the pages retrieved; it appears to follow the "four most recent feature releases" rolling window rather than a fixed N-month clock. Discontinued GHES versions receive **no further patches, including for critical security issues**, per docs.github.com (URL not independently re-verified beyond search-snippet confirmation — see Unresolved list).

[Source: https://docs.github.com/en/graphql] The GraphQL API's schema/changelog spans **2017 through 2026**, evolving continuously rather than through discrete major versions; GitHub does not document GraphQL with the same date-versioning scheme used for REST.

[Version-sensitive, Inference from search results, not independently fetched in full: GHES sizing] GHES sizing guidance scales with user count — approximately 4 vCPU/16 GB RAM for up to 500 users, 8 vCPU/32 GB RAM for up to 2,000 users, 16 vCPU/64 GB RAM for up to 5,000 users, x86-64 architecture required, with a documented +25% CPU/memory uplift recommended when enabling Actions or GitHub Advanced Security on the instance. This is drawn from WebSearch result snippets of `docs.github.com/en/enterprise-server@.../admin/installation/...` sizing pages rather than a full page fetch (the direct fetch attempt 404'd on the URL guessed), so treat the exact numbers as **Unresolved: not independently confirmed by direct page fetch**, only by search-snippet excerpt.

---

## 13. Breaking changes

[Source: https://docs.github.com/en/rest/about-the-rest-api/breaking-changes?apiVersion=2026-03-10] [Version-sensitive — applies specifically to REST API version **2026-03-10**, released March 10, 2026] This is documented as the **first calendar-dated API version to ship breaking changes** since date-based versioning began with `2022-11-28`. Documented breaking changes in `2026-03-10` include (non-exhaustive, as captured):
- Removal of the deprecated `rate` property from the rate-limit endpoint (use `resources.core`).
- Removal of the deprecated `permission` property from team-creation requests.
- Repository Contents API: submodules now report `type: "submodule"` instead of `type: "file"`.
- SARIF response `Content-Type` corrected from `application/json+sarif` to `application/sarif+json`.
- Removal of `use_squash_pr_title_as_default` from repository settings (replaced by `squash_merge_commit_title`).
- Removal of `authorizations_url` and `hub_url` from the API root, reflecting the (long-deprecated, since 2020) OAuth Authorization API's removal.
- Removal of several under-specified beta-media-type fields (`emails` as a flat array, `pull_request` defaults, `user` property, `master_branch`).
- Removal of `history`/`forks` fields from base gist objects.
- Installation-deletion success status changed from `204` to `202` (background processing).
- Removal of `secret_scanning_push_protection_custom_link_enabled` from organization settings.
- Code-scanning language values `javascript` and `typescript` consolidated into `javascript-typescript`.
- Removal of the long-deprecated `has_downloads` repository property (unused for 10+ years).
- Several endpoints now return **`451 Unavailable For Legal Reasons`** instead of `403`/`422` when blocked by trade controls.
- Advisory `cvss` property deprecated in favor of `cvss_severities` (`cvss_v3`/`cvss_v4`).
- Removal of certain repository-detail fields from migration-resource responses.
- Removal of the deprecated `/hub` endpoint entirely.
- Removal of `merge_commit_sha` from all pull-request responses.
- Workflow-dispatch endpoint response changed from `204` to `200` with run details; `return_run_details` parameter removed.
- Removal of the singular `assignee` field from issues (use the `assignees` array).
- Dependabot secrets' `selected_repository_ids` parameter now integers-only.
- Removal of the `bundle` property from attestation-list responses (use `bundle_url`).

[Source: https://docs.github.com/en/rest/about-the-rest-api/breaking-changes?apiVersion=2026-03-10] Version `2022-11-28` is documented as carrying **no breaking changes** — it was the initial baseline of date-based versioning.

Not documented / could not verify: a consolidated breaking-changes changelog for the **GraphQL** API comparable to the REST one — GraphQL is documented as evolving via an ongoing changelog rather than discrete breaking-change-tagged versions in the pages fetched.

---

## 14. Limitations

[Source: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github] File-size limitations: files over **50 MiB** trigger a warning (push still succeeds); web-UI uploads are capped at **25 MiB**; files over **100 MiB** are **hard-blocked** from being pushed via Git (Git LFS required beyond this).

[Source: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github] Repository-size limitation (soft/recommended, not hard-enforced): "ideally less than 1 GB, and less than 5 GB is strongly recommended," with GitHub Support potentially intervening on oversized repositories.

[Source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api] REST API rate-limit ceilings, as detailed under Performance above (60/hr unauthenticated, 5,000/hr authenticated, 15,000/hr GHEC, plus secondary limits on concurrency/CPU-time/per-endpoint minimums), constitute a hard operational ceiling on integration throughput.

[Source: https://docs.github.com/en/graphql/overview/resource-limitations] GraphQL API limitations: 500,000-node cap per query, 1–100 range on `first`/`last` pagination arguments, 10-second execution timeout (502/504 beyond that plus a rate-limit penalty), 5,000 points/hour standard allocation, 2,000 points/minute secondary cap.

[Source: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages] GitHub Pages limitation: **one Pages site per user/organization account** and **one Pages site per repository**.

[Source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets] Ruleset limitation: **up to 75 rulesets per repository**.

[Source: https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization] Audit-log limitations: **180-day retention window**, and CSV/JSON exports capped at **100 MB compressed or 10 minutes of processing**, whichever comes first; no full-text search (filter-based search only).

---

## 15. Debugging

[Source: https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/testing-webhooks] Webhook debugging is documented around GitHub's **delivery log UI** (per-webhook history of each delivery attempt, with the ability to **redeliver** any past delivery for repeat/regression testing) and the **smee.io** proxy workflow for surfacing deliveries to a local dev server during development, checked in three stages: GitHub's own delivery confirmation, the smee.io relay, and local-server processing.

[Source: https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api] REST API debugging guidance: inspect `x-ratelimit-*` response headers to diagnose rate-limit exhaustion; honor `retry-after` on `429`s; investigate rather than blind-retry persistent `4xx`/`5xx` responses; for `404`s specifically, first verify authentication/authorization before assuming the resource doesn't exist (GitHub returns `404` rather than `403` for private resources the caller can't see, as an intentional information-disclosure guard — [Inference, not confirmed in docs] this rationale wasn't stated explicitly on the fetched page, but the recommended debugging step implies it).

[Source: https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization] The **organization audit log** is the documented tool for debugging/investigating "who did what, when" at the organization-administration level, filterable by operation type, repository, actor, action, timestamp, and location.

[Source: https://docs.github.com/en/graphql/overview/resource-limitations] For GraphQL, a `502`/`504` response is the documented signal of a query exceeding the 10-second execution budget, with GitHub explicitly warning that repeated timeouts also cost extra rate-limit points as a deterrent — a debugging signal to reduce query complexity/nesting rather than just retry.

Not documented / could not verify: a dedicated GitHub-hosted request-tracing or correlation-ID debugging tool for REST/GraphQL API calls beyond response headers and status codes — no such tool was surfaced in the pages fetched.

---

## 16. Integration

[Source: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps] GitHub's primary documented **integration/extensibility surfaces** are: **GitHub Apps** (installable, fine-grained-permission integrations acting as their own bot identity), **OAuth Apps** (user-authorization-based integrations), the **REST API**, the **GraphQL API**, and **webhooks** (event push model).

[Source: https://docs.github.com/en/webhooks/about-webhooks] Webhooks are the documented mechanism for near-real-time integration with external systems (CI/CD tools, chat notifications, deployment tooling, etc.) reacting to GitHub events (pushes, pull requests, issues, team membership changes, and more) without polling.

[Source: https://docs.github.com/en/rest/deployments/deployments] The **Deployments API** is the documented integration point for external/self-hosted deployment and release-management tooling to coordinate with GitHub's environment/deployment-status tracking.

[Source: https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages] **GitHub Packages** integrates with standard package-manager tooling (npm, RubyGems, Maven/Gradle, NuGet) and container tooling (Docker/OCI) as a drop-in registry, and documents authentication via `GITHUB_TOKEN` (within Actions workflows — out of scope here) or personal access tokens with `read:packages` scope (for external/local tooling).

[Source: https://docs.github.com/en/migrations/using-github-enterprise-importer/understanding-github-enterprise-importer/about-github-enterprise-importer] GitHub Enterprise Importer documents integration/migration paths from **Azure DevOps**, **Bitbucket Server/Data Center**, **GitHub.com**, **GitHub Enterprise Server**, and **GitLab** into GitHub Enterprise Cloud, executable via GitHub CLI or API.

[Source: https://docs.github.com/en/graphql] The published **REST-to-GraphQL migration guide** and the GraphQL global node ID / pagination guides are the documented path for integrations moving between GitHub's two first-party API surfaces.

Not documented in scope: GitHub Actions-based CI/CD integration (excluded per task scope — covered as its own technology).

---

## 17. Production considerations

[Source: https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api] For production API integrations: prefer webhooks over polling, respect both primary and secondary rate limits (serial mutating requests, ≥1 second apart), implement conditional requests to conserve rate-limit budget, and implement exponential backoff with a retry ceiling on `429`s — GitHub explicitly warns that continuing to call the API while rate-limited "risks integration suspension."

[Source: https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization] For production organization administration: the audit log (180-day retention, owner-only, JSON/CSV export with size/time export caps) is the documented tool for ongoing security monitoring and compliance evidence-gathering.

[Source: https://docs.github.com/en/enterprise-server@latest/admin/overview/about-upgrades-to-new-releases] For production **self-hosted GHES** operation: patch releases are documented to typically cause "less than five minutes of downtime," while feature-release upgrades should be planned around the quarterly release cadence; release candidates must never be installed by upgrading a production instance and RC test environments must be destroyed rather than carried forward.

[Version-sensitive, Unresolved — see Version information section] GHES production sizing (vCPU/RAM/storage scaling with user count, +25% headroom for Actions/Advanced Security) was found via search-result snippets of official docs pages but not confirmed by a successful direct page fetch in this research pass (the guessed canonical URL 404'd); flagged as **Unresolved: exact current sizing table not independently re-verified by direct fetch**, though the search snippets did cite `docs.github.com/en/enterprise-server@.../admin/installation/...` as their source.

[Source: https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories] For production repository hygiene: enabling Dependabot alerts, secret scanning + push protection, and code scanning is the documented baseline security posture; branch protection (required status checks, required reviews) on `main`/release branches is the documented control for production-code-path safety.

[Source: https://docs.github.com/en/rest/about-the-rest-api/api-versions] For production API-consuming systems: pin to an explicit `X-GitHub-Api-Version` rather than relying on the implicit default, since the implicit default (`2022-11-28`) will eventually itself be retired once its 24-month support window from the newest version's release lapses — an unpinned integration risks a future breaking change landing silently once support for the default version ends. [Inference, not confirmed in docs — the docs state the 24-month support policy and the version-pinning mechanism; the "silent breakage risk of not pinning" is this research's inference from those two facts, not a direct docs quote.]

---

## Unresolved items (summary)

- Exact standard support-window length (in months) from a GHES feature release's GA date to its documented discontinuation date — search snippets show individual discontinuation dates (e.g. 3.9 discontinued 2024-07-09; 3.17 discontinued 2026-09-22) and a "four most recent feature releases" support-window rule, but no single fixed N-month figure was found in the pages fetched.
- GHES production hardware-sizing table (vCPU/RAM/storage by user count) — sourced from WebSearch snippets of `docs.github.com/en/enterprise-server@.../admin/installation/...`-family pages; a direct fetch attempt against a guessed canonical URL 404'd, so the exact current numbers are not independently re-verified against a live page in this pass.
- Whether GitHub.com/GHEC publishes any customer-facing SLA/uptime commitment in `docs.github.com` itself (as opposed to a separate legal/Trust Center site) — not located in the pages fetched; **Not documented / could not verify** within the scope of this pass.
- A canonical single-page architecture diagram of GitHub.com's own internal infrastructure (storage/replication layer, etc.) — not found; GitHub does not appear to publish this as end-user documentation.
- Whether GraphQL API breaking changes follow any formal deprecation-window policy analogous to REST's 24-month rule — not found in the pages fetched; GraphQL's changelog appears continuous/additive rather than versioned in the same way.

---

## Sources consulted (deduplicated)

- https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories
- https://docs.github.com/en/get-started/using-github/github-flow
- https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-merge-methods-on-github
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- https://docs.github.com/en/enterprise-cloud@latest/admin/overview/about-github-enterprise-cloud
- https://docs.github.com/en/migrations/using-github-enterprise-importer/understanding-github-enterprise-importer/about-github-enterprise-importer
- https://docs.github.com/en/webhooks/about-webhooks
- https://docs.github.com/en/rest/about-the-rest-api/about-the-rest-api
- https://docs.github.com/en/rest/about-the-rest-api/api-versions
- https://docs.github.com/en/rest/about-the-rest-api/breaking-changes?apiVersion=2026-03-10
- https://docs.github.com/en/graphql
- https://docs.github.com/en/graphql/overview/resource-limitations
- https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
- https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
- https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/testing-webhooks
- https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
- https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api
- https://docs.github.com/en/authentication
- https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-two-factor-authentication
- https://docs.github.com/en/code-security
- https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization
- https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories
- https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages
- https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages
- https://docs.github.com/en/rest/deployments/deployments
- https://docs.github.com/en/enterprise-server@latest/admin/overview/about-upgrades-to-new-releases
- https://github.blog/changelog/2026-03-12-rest-api-version-2026-03-10-is-now-available/
