# GitHub Actions (CI/CD) — Technology Research

Research date: 2026-09-09. Primary source: `docs.github.com/en/actions/*` (canonical documentation host — confirmed reachable and current at time of research). Secondary official sources used to confirm release/changelog facts not fully covered on the docs site: `github.blog/changelog/*` (official GitHub Changelog blog) and `github.com/actions/*` (official GitHub Actions org repos — `actions/runner`, `actions/upload-artifact`, `actions/toolkit`, etc.). All claims are tagged per this project's convention: `[Source: <url>]` for documented facts, `[Inference, not confirmed in docs]` for reasoning, "Not documented / could not verify" where docs did not cover something in the pages fetched, and "Unresolved: ..." where confidence is genuinely low.

**Doc host note**: No evidence of a canonical-doc-host migration was found — `docs.github.com/en/actions` remains GitHub Actions' single documentation home. Note that GitHub has recently reorganized the docs' internal URL structure (e.g. a new `concepts/`, `how-tos/`, `tutorials/`, `reference/` taxonomy layered over the older `learn-github-actions/`, `deployment/`, `monitoring-and-troubleshooting-workflows/` paths); many older paths now 404 or redirect, so URLs cited below are the ones confirmed live at research time — some may move again as GitHub continues this restructuring. Enterprise Server (GHES) and Enterprise Cloud have their own versioned doc trees (e.g. `docs.github.com/en/enterprise-server@3.17/actions`) that track the same product with version-specific caveats noted inline.

**Scope note**: "GitHub Actions" is both (1) the hosted CI/CD orchestration product (workflows, runners, the Actions REST/GraphQL APIs, billing) and (2) an ecosystem of reusable "actions" (packaged units of automation distributed via GitHub repos / the Marketplace). This research covers both, plus the `actions/runner` open-source runner agent and the metadata format for authoring custom actions, since a coding-agent skill would need grounding in all of these.

---

## 1. Core concepts

[Source: https://docs.github.com/en/actions/get-started/understand-github-actions] GitHub Actions is a CI/CD platform that lets you automate build, test, and deployment pipelines, and more broadly automate any workflow triggered by activity on GitHub or on a schedule/external event.

[Source: https://docs.github.com/en/actions/get-started/understand-github-actions] A **workflow** is "a configurable automated process that will run one or more jobs." Workflows are defined as YAML files checked into a repository's `.github/workflows` directory and are triggered by an **event** (repository activity such as `push` or `pull_request`, a scheduled time, `workflow_dispatch` for manual triggering, or an external REST API call via `repository_dispatch`).

[Source: https://docs.github.com/en/actions/get-started/understand-github-actions] A **job** is a set of **steps** that execute on the same runner. Jobs can run in parallel or be made to depend on each other sequentially via `needs`. A **matrix strategy** lets a single job definition fan out into multiple runs across variable combinations (e.g. OS × language version).

[Source: https://docs.github.com/en/actions/get-started/understand-github-actions] A **step** is either a shell command (`run`) or a reusable **action** (`uses`); steps within the same job execute in order on the same runner and can share data (files on disk, or outputs passed between steps).

[Source: https://docs.github.com/en/actions/get-started/understand-github-actions] An **action** is a reusable, packaged unit of code that performs a specific task, reducing repetitive workflow code. Actions can be authored by GitHub, the community (shared publicly, discoverable via GitHub Marketplace), or written privately for internal use.

[Source: https://docs.github.com/en/actions/get-started/understand-github-actions] A **runner** is the server that executes a job. GitHub provides hosted Linux, Windows, and macOS virtual-machine runners; you can alternatively host your own runners, or use GitHub-managed "larger runners" with more resources.

[Source: https://docs.github.com/en/actions/get-started/understand-github-actions] Flow summary: an **event** triggers a **workflow** → the workflow contains one or more **jobs** → each job contains one or more **steps**, executed in order on the same **runner** → steps invoke shell commands or **actions**.

---

## 2. Architecture

[Source: https://docs.github.com/en/actions/get-started/understand-github-actions] Workflows live as YAML files in `.github/workflows/` and are picked up by GitHub's Actions service when a matching event occurs; the service schedules the workflow's jobs onto available runners (GitHub-hosted or self-hosted, per each job's `runs-on`).

[Source: https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners] Self-hosted runners can be "physical, virtual, in a container, on-premises, or in a cloud," and can be registered at three scopes: repository-level (dedicated to one repository), organization-level (shared across an org's repositories), and enterprise-level (assigned across multiple organizations in an enterprise).

[Source: https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners] GitHub-hosted runners are fully managed by GitHub (OS/software updates are automatic); self-hosted runners give more control over hardware, OS, and installed tooling, but "you are responsible for updating the operating system and all other software," and — unlike GitHub-hosted runners — do not necessarily start from a clean instance for every job unless you build that yourself (e.g. via ephemeral/JIT runners).

[Source: https://github.com/actions/runner] The runner itself (`actions/runner`) is an open-source agent (the "Actions Runner") that GitHub also publishes as the software running inside GitHub-hosted VMs; self-hosted runners install and run this same agent, configured with `config.sh`/`config.cmd` to register against a repo, org, or enterprise.

[Source: https://docs.github.com/en/actions/using-github-hosted-runners/using-larger-runners/about-larger-runners] "Larger runners" are GitHub-hosted VMs with more RAM/CPU/disk, optional static IP addresses, private networking, and (for some configurations) GPU support; they support runner groups for access control and autoscaling, and — unlike standard GitHub-hosted runners — are billed strictly per-minute of execution with no idle charges and do not draw from a plan's included free minutes.

[Source: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions] Reusable workflows and composite actions let workflow logic be composed hierarchically: a top-level ("caller") workflow can invoke reusable workflows (`workflow_call`) as jobs, and individual steps can invoke composite actions that themselves wrap multiple steps.

Not documented / could not verify in the pages fetched: an official single architecture diagram tracing the full request path from a GitHub.com event, through the Actions scheduling/queueing service, to runner pickup and container/VM provisioning — the docs describe each component's role but this research did not locate one canonical end-to-end systems diagram.

---

## 3. APIs

[Source: https://docs.github.com/en/rest/actions] The **GitHub REST API for Actions** covers: Workflows, Workflow Runs, Workflow Jobs, Artifacts, Cache, Secrets, Variables, Self-hosted Runners, Runner Groups, GitHub-hosted Runners, Concurrency Groups, Permissions, and OIDC — i.e. essentially every management surface of the product is API-accessible (list/trigger/cancel/re-run workflow runs, download artifacts, manage secrets/variables, manage runner registration tokens, etc.).

[Source: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions] `workflow_dispatch` and `repository_dispatch` events allow workflows to be triggered externally: `workflow_dispatch` supports manual/API-triggered runs with typed input parameters defined in the workflow file; `repository_dispatch` allows a custom external event (with an arbitrary JSON payload) to trigger a workflow via the REST API.

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect] GitHub also exposes an **OIDC provider**: each workflow job can request a short-lived, auto-generated JWT from GitHub's OIDC token endpoint, which is then exchanged with a cloud provider (AWS, Azure, GCP, HashiCorp Vault, and others) for temporary cloud credentials, without any long-lived cloud secret stored in GitHub.

[Source: https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions] For custom-action authors, GitHub provides the **Actions Toolkit** (`@actions/core`, `@actions/github`, etc., published as npm packages under `actions/toolkit`) as the supported way for JavaScript actions to read inputs, set outputs, write to logs, and call the GitHub API from within a workflow run.

[Source: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions] Within workflow YAML, an **expression syntax** (`${{ }}`) backed by named **contexts** (see Configuration, below) functions as the declarative "API" for reading run-time state (commit SHA, event payload, secrets, matrix values, previous step/job outputs) and computing conditional (`if`) values.

Not documented / could not verify in the pages fetched: a GraphQL-specific API surface dedicated to Actions comparable in breadth to the REST API — the REST API is the documented primary programmatic interface for Actions management.

---

## 4. Configuration

[Source: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions] Workflow YAML top-level keys include: `name` (display name), `run-name` (per-run custom name, supports expressions), `on` (trigger events — a string, list, or a map with per-event filters such as branches/tags/paths), `permissions` (controls the auto-generated `GITHUB_TOKEN`'s scopes, settable workflow-wide or per-job, from `none` up to `read-all`/`write-all`), `env` (workflow-wide environment variables — variables here cannot reference each other), `defaults` (e.g. `defaults.run.shell`, `defaults.run.working-directory`), `concurrency` (a `group` key plus `cancel-in-progress` or queueing behavior to limit simultaneous runs), and `jobs` (the required map of job definitions).

[Source: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions] Job-level keys include `runs-on` (target runner label(s), e.g. `ubuntu-latest`, `windows-latest`, `macos-latest`, `self-hosted`, or larger-runner group names), `steps` (ordered list of `run`/`uses` steps), `needs` (job dependency declaration), `strategy.matrix` (fan-out across variable combinations, with optional `include`/`exclude` and `fail-fast`/`max-parallel`), `permissions` and `environment` (job-scoped overrides), `if` (conditional job execution), and `outputs` (job-level outputs, typically mapped from step outputs).

[Source: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions] Step-level keys include `uses` (reference an action, by tag/branch/SHA, or by Docker image), `run` (shell command, with configurable `shell:`), `with` (input parameters to an action), `env` (step-scoped environment variables, highest specificity), and `if` (conditional step execution).

[Source: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions] Scheduled workflows use POSIX cron syntax under `on.schedule`; the shortest supported interval is every 5 minutes, and cron schedules run in UTC (per broader GitHub Actions documentation on scheduled events; scheduling reliability during high-load periods is documented as best-effort, i.e. the exact minute is not guaranteed).

[Source: https://docs.github.com/en/actions/learn-github-actions/contexts] Eleven named **contexts** are available in expressions: `github`, `env`, `vars` (org/repo/environment-level configuration variables, distinct from `env`), `job`, `steps`, `runner`, `secrets`, `strategy`, `matrix`, `needs`, and `inputs`. Availability differs by workflow location — for example, the `secrets` context is unavailable inside composite actions, and the `jobs` context is only usable in reusable workflows for propagating job outputs; `hashFiles()` and some other functions are restricted to specific keys (e.g. step-level `if`).

[Source: https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions] Custom actions are configured via an `action.yml`/`action.yaml` metadata file with a `runs` key selecting one of three action types: **JavaScript actions** (`using: node20` or `node24`, a `main` entry file, optional `pre`/`post` lifecycle scripts with `pre-if`/`post-if` conditions), **Docker container actions** (`using: docker`, an `image` — local Dockerfile or registry reference — plus optional `entrypoint`, `args`, `env`, `pre-entrypoint`/`post-entrypoint`), and **composite actions** (`using: composite`, a required `steps` array that can itself mix `run` and `uses` steps). `inputs` and `outputs` blocks declare the action's parameter contract (inputs become `INPUT_<NAME>` env vars inside JS/Docker actions); an optional `branding` block (icon + color) styles the action's Marketplace listing.

[Version-sensitive, Source: https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions] JavaScript action runtimes are versioned (`node20`/`node24`); see Breaking changes, below, for the Node 20 → Node 24 migration timeline.

---

## 5. Recommended patterns

[Source: https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows] Use the `actions/cache` action (or built-in caching in setup actions like `actions/setup-node`) keyed on a hash of the dependency lockfile (e.g. `"npm-${{ hashFiles('package-lock.json') }}"`), with `restore-keys` providing sequential fallback prefixes, so dependency installs are skipped or accelerated on cache hit.

[Source: https://docs.github.com/en/actions/sharing-automations/reusing-workflows] Factor shared CI/CD logic into **reusable workflows** (`on: workflow_call`) invoked from caller workflows via `uses: ./.github/workflows/<file>` (same repo) or `owner/repo/.github/workflows/<file>@ref` (cross-repo), passing typed `inputs`/`secrets` and consuming `outputs` via `needs.<job_id>.outputs.<name>`; `secrets: inherit` implicitly forwards all caller secrets to the called workflow within the same organization.

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions] Set the default `GITHUB_TOKEN` permission to read-only (least privilege) at the workflow or organization level, and grant elevated (e.g. `contents: write`) permissions only on the specific jobs that need them.

[Source: https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments] Use **environments** (e.g. `staging`, `production`) referenced from a job's `environment:` key to gate deployments with required reviewers, wait timers, branch restrictions, or custom deployment protection rules, and to scope environment-specific secrets/variables.

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect] Prefer OIDC-based short-lived cloud credentials over long-lived cloud secrets stored as repository/organization secrets when deploying to AWS/Azure/GCP.

[Source: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions] Use `concurrency.group` (optionally with `cancel-in-progress: true`) to avoid redundant/overlapping runs of the same workflow on the same ref (e.g. superseding stale PR builds when new commits are pushed).

---

## 6. Anti-patterns

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions] Using `pull_request_target` (which runs with the base repo's privileged token/secrets) while also checking out and executing the pull request's *head* code is explicitly called out as dangerous — it can hand write access and secrets to an attacker-controlled PR; GitHub recommends avoiding this trigger where possible, or using `workflow_run` instead, and never checking out untrusted PR code under a privileged-context trigger.

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions] Referencing third-party actions by a mutable tag (e.g. `@v1`) or branch name is discouraged versus pinning to a full-length immutable commit SHA, since tags can be repointed by the action's maintainer (or an attacker who compromises the maintainer's account) to inject malicious code without changing the visible version string in your workflow.

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions] Treating structured data (JSON/XML/YAML blobs) as a single GitHub secret is discouraged, since GitHub's log redaction does exact-string matching and structured/encoded transformations of a secret value will not be reliably masked; each derived/transformed value should itself be registered as a secret.

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions] Using self-hosted runners for public repositories is discouraged ("almost never be used for public repositories") because any fork can submit a workflow/PR that executes arbitrary code on that runner; the runner "can be persistently compromised by untrusted code" if not made ephemeral between jobs.

[Source: https://github.blog/changelog/2022-10-11-github-actions-deprecating-save-state-and-set-output-commands/] The older `::set-output::` and `::save-state::` workflow commands are deprecated in favor of writing to the `$GITHUB_OUTPUT`/`$GITHUB_STATE` environment files, because the old commands allowed untrusted step-log content to be interpreted as commands — see Breaking changes, below.

---

## 7. Security

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions] Store all sensitive values as GitHub **secrets** (never plaintext in workflow YAML); automatic log redaction of secret values is documented as best-effort ("automatic redaction is not guaranteed"), so use `::add-mask::VALUE` to mask additional sensitive runtime values, and register every derived/transformed form of a secret as its own secret.

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions] Set `GITHUB_TOKEN` default permissions to read-only content access at minimum, elevate only per-job as needed, and pin third-party actions to full-length commit SHAs — "currently the only way to use an action as an immutable release" — or, failing that, to tags from creators explicitly marked as verified.

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect] OIDC lets workflows authenticate to cloud providers using per-job, automatically expiring JWTs exchanged for short-lived cloud credentials, eliminating the need to store long-lived cloud secrets in GitHub; trust between GitHub and the cloud provider is configured by the cloud-side role/identity's OIDC trust policy, which validates claims in the presented token (repo, ref, environment, etc.) before issuing credentials.

[Source: https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners] Self-hosted runners carry real operational security risk: they are not automatically kept patched by GitHub, and (per the security-hardening guidance above) should be run as ephemeral/JIT instances with a clean environment per job, and generally not used for public repositories at all.

[Source: https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows] Cache poisoning is a documented risk: low-trust event triggers such as `pull_request_target` are restricted to **read-only** cache access to prevent an untrusted PR from writing a poisoned cache entry that a later privileged run would then restore and trust.

[Source: https://github.blog/changelog/2022-10-11-github-actions-deprecating-save-state-and-set-output-commands/] The `set-output`/`save-state` deprecation was itself a security fix: these workflow commands could be triggered by untrusted content appearing in step logs (log injection), letting an attacker influence workflow state/outputs the author never intended; the replacement (`$GITHUB_OUTPUT`/`$GITHUB_STATE` environment files) is not subject to the same log-parsing injection vector.

---

## 8. Performance

[Source: https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows] Dependency caching (via `actions/cache` or built-in caching flags on setup actions) is the primary documented lever to reduce workflow run time; GitHub automatically evicts caches unused for 7 days and enforces a default 10 GB per-repository cache size cap, with least-recently-used eviction once the cap is exceeded.

[Source: https://docs.github.com/en/actions/using-github-hosted-runners/using-larger-runners/about-larger-runners] For CPU/memory/disk-bound jobs, GitHub-managed **larger runners** provide more RAM, CPU, disk, and (for some configurations) GPU acceleration versus standard GitHub-hosted runners, billed only for actual execution minutes with no idle cost.

[Source: https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/] `actions/upload-artifact`/`download-artifact` v4 introduced a new content-addressable storage backend, making artifact downloads "10x faster on average" versus v3 — a concrete, documented performance improvement tied to the v3→v4 migration (see Migration/Breaking changes).

[Source: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions] Matrix strategies (`strategy.matrix`) parallelize independent test/build permutations across multiple runners simultaneously rather than serially within one job; `strategy.max-parallel` can throttle concurrency, and `fail-fast` (default `true`) cancels remaining matrix jobs once one fails.

[Source: https://docs.github.com/en/actions/concepts/overview/usage-limits-billing-and-administration] Concurrency and queueing limits (see Limitations) act as an upper bound on achievable parallelism per account/plan; hitting these limits manifests as queued rather than immediately-running jobs.

---

## 9. Testing

[Source: https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/re-running-workflows-and-jobs] GitHub documents re-running failed or all jobs in a workflow run (optionally with debug logging enabled) directly from the Actions UI or the REST API as the primary supported mechanism for iterating on a workflow after a failure, rather than a dedicated "test framework" for workflows themselves.

[Source: https://github.com/actions/toolkit] For **authoring** custom JavaScript actions, GitHub's own `actions/toolkit` repository documents unit-testing action logic (string/data manipulation, business logic) with standard JS test frameworks (the toolkit's own CI uses tools such as Jest) against the `@actions/core`/`@actions/github` packages, decoupled from actually running inside a GitHub Actions job.

[Source: https://github.com/github/local-action] GitHub publishes `github/local-action`, a utility (documented as usable in VS Code) for running and debugging a custom JavaScript action locally by emulating core Actions Toolkit functionality (reading `INPUT_*` env vars, `core.setOutput`, etc.) without needing an actual workflow run.

Not documented / could not verify in the pages fetched: an official, GitHub-maintained tool for running full *workflows* (as opposed to individual custom actions) locally end-to-end — the widely used community tool for that purpose (`nektos/act`) is not a GitHub-maintained project and is out of scope for this official-docs-only research.

---

## 10. Deployment

[Source: https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments] **Environments** describe deployment targets (e.g. `staging`, `production`); a job references at most one environment via `environment:`, and the environment is then surfaced on the repository's main page. Configurable **protection rules** include required reviewers, a wait timer, branch/tag restrictions on which refs may deploy, and custom deployment protection rules (third-party gating integrations) — all such rules must pass before the job referencing the environment is dispatched to a runner.

[Source: https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments] Environment-scoped **secrets** and **variables** can be defined per environment, restricting their availability to jobs that reference that specific environment.

[Source: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments] When a job referencing an environment runs, GitHub Actions creates a **deployment** object (`environment` property set) and, as the job progresses, **deployment status** objects (with `environment_url` and `state`), integrating with GitHub's native Deployments feature/API (visible in the repo's "Environments"/"Deployments" UI).

[Source: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments] Common trigger events for deployment workflows documented by GitHub include `push`, `pull_request`, and `workflow_dispatch` (for manual/controlled deploys).

---

## 11. Migration

[Source: https://docs.github.com/en/actions/tutorials/migrate-to-github-actions/automated-migrations] GitHub publishes **GitHub Actions Importer**, an official CLI (`gh actions-importer`, a `gh` extension) that audits, forecasts, and automates migration of pipelines from Azure DevOps, Bamboo, CircleCI, GitLab CI, Jenkins, and Travis CI into GitHub Actions workflows, via `audit`, `dry-run`, and `migrate` commands.

[Source: https://docs.github.com/en/actions/migrating-to-github-actions/manually-migrating-to-github-actions] GitHub also documents manual migration guidance describing configuration-concept mappings between GitHub Actions and each of Azure Pipelines, CircleCI, GitLab CI/CD, Jenkins, and Travis CI (e.g. equivalent concepts for stages/jobs/steps, environment variables, and caching) for teams migrating without the automated importer.

[Version-sensitive, Source: https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/] Migrating from `actions/upload-artifact`/`download-artifact` **v3 to v4** is a required, breaking migration (v3 usage blocked as of January 30, 2025, per the changelog) — see Breaking changes for specifics.

[Source: https://github.com/actions/download-artifact] `download-artifact@v4+` is documented (via the action's own repo) as not currently supported on GitHub Enterprise Server (GHES); GHES users must remain on v3 for that action until GHES support ships.

Not documented / could not verify in the pages fetched: an official guide for migrating *between* major GitHub Actions runner versions (e.g. self-hosted runner upgrade procedure beyond "update to the minimum required version") — runner version enforcement is covered under Breaking changes/Version information instead, since the runner is treated as a continuously-updated agent rather than a versioned product with a formal migration guide.

---

## 12. Version information

[Source: https://docs.github.com/en/actions] GitHub Actions on GitHub.com/GitHub Enterprise Cloud is a continuously-deployed SaaS product with no discrete "release version" for the product itself; version-sensitive facts instead attach to specific sub-components (the runner agent, GHES releases, JS action Node runtimes, artifact-action major versions).

[Version-sensitive, Source: https://github.blog/changelog/2026-02-05-github-actions-early-february-2026-updates/] Self-hosted **runner** minimum-version enforcement: as of the February 2026 changelog, self-hosted runners were required to be on **v2.329.0 or later** by March 16, 2026 to continue calling `./config.sh`, with a brownout period (Feb 23–Mar 16, 2026) of scheduled configuration blocks used to surface runners needing upgrades.

[Version-sensitive, Source: https://github.blog/changelog/2026-09-03-github-actions-early-september-2026-updates/] A September 2026 changelog entry documents a new REST endpoint, `GET /actions/runners/deprecations/{version}` (at repo/org/enterprise scope), returning `runner_version`, `runtime_deprecates_at`, and `registration_deprecates_at` — i.e. GitHub now formally publishes forward-looking runner-version deprecation dates via the API.

[Unresolved: the exact latest `actions/runner` release number and its release date as of September 2026 could not be pinned down with confidence — one search result cited v2.337.0 as "the latest runner version mentioned" in September 2026 context, but a direct fetch of the `actions/runner` GitHub releases page returned dates (e.g. "August 26, 2024") that are inconsistent with that same version number appearing in 2026-dated changelog search results, suggesting the fetch tool resolved relative/cached date text incorrectly. Treat v2.329.0 as the confirmed-current *minimum required* version (per the Feb 2026 changelog) and do not rely on this document for the precise latest patch version — check https://github.com/actions/runner/releases directly.]

[Version-sensitive, Source: https://github.blog/changelog/2026-02-05-github-actions-self-hosted-runner-minimum-version-enforcement-extended/] GitHub has previously extended self-hosted-runner minimum-version enforcement deadlines at least once, indicating these are not always hard-enforced on the first announced date.

[Source: https://docs.github.com/en/enterprise-server@3.17/admin/all-releases] GitHub Enterprise Server (GHES) follows a distinct versioned-release model, independent from GitHub.com's continuous deployment; [Source: https://github.blog/changelog/2026-06-11-github-enterprise-server-3-21-is-now-generally-available/] GHES 3.21 was GA as of June 11, 2026.

[Version-sensitive, per GHES support-lifecycle search findings — Unresolved: precise end-of-support dates for each GHES minor version were found via search snippets (e.g. "3.14 discontinued 2026-03-17," "3.16 discontinued 2026-06-02," "3.17 discontinued 2026-09-22") but were not independently verified against a directly fetched official page in this research pass; treat these dates as indicative, not confirmed, and check https://docs.github.com/en/enterprise-server/admin/all-releases for the authoritative current table.] GitHub's documented general policy (per search result) is to support "at least the four most recent feature releases" of GHES at any time.

[Version-sensitive, Source: https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions] JavaScript action `runs.using` currently accepts `node20` or `node24`; see Breaking changes for the Node 20 deprecation timeline.

---

## 13. Breaking changes

[Version-sensitive, Source: https://github.blog/changelog/2022-10-11-github-actions-deprecating-save-state-and-set-output-commands/] The `::set-output::` and `::save-state::` workflow commands were deprecated (announced October 11, 2022) in favor of the `$GITHUB_OUTPUT`/`$GITHUB_STATE` environment-file mechanism, for the log-injection security reason described above; per widely corroborated secondary reporting the original hard-removal date was postponed from its initial May 31, 2023 target given usage volume — workflows using the old commands continue to run with deprecation warnings rather than hard failures as of the last confirmed removal-status check. [Unresolved: whether/when GitHub ultimately hard-removed these commands entirely was not re-confirmed against a live official page in this research pass; treat "still works with a warning" as the last officially-confirmed state and verify current status before relying on it.]

[Version-sensitive, Source: https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/] `actions/upload-artifact` and `actions/download-artifact` **v3 were fully blocked/deprecated on GitHub.com as of January 30, 2025**; users had to migrate to **v4**, which changed artifacts from mutable to **immutable** (no appending to an existing artifact; duplicate artifact names within one run fail by default unless configured otherwise), changed download behavior (creates a per-artifact subdirectory when no `name` filter is given; new `pattern` and `merge-multiple` inputs replace old wildcard `name` matching), and switched to a new, ~10x-faster content-addressable storage backend. [Source: https://github.com/actions/download-artifact] `download-artifact@v4+` remains unsupported on GHES, so GHES users must stay on v3 there.

[Version-sensitive, Source: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/] **Node.js 20 is being deprecated on GitHub-hosted runners.** Per the changelog and corroborating search findings: Node.js 20 reaches upstream end-of-life in April 2026; GitHub began forcing JavaScript actions to run on **Node.js 24 by default starting June 2, 2026** (opt-out via `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true` during the transition window; opt-in early testing via `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`); Node.js 20 is scheduled for **complete removal from GitHub-hosted runners on September 16, 2026** — i.e. as of this research's date (2026-09-09), this removal is imminent (about one week away) and actions still targeting `node20` should treat this as urgent. [Inference, not confirmed in docs: whether the September 16, 2026 removal date has definitively passed or been extended was not re-verified against a live changelog page dated on/after that date in this research pass.]

[Version-sensitive, Source: https://github.blog/changelog/2026-02-05-github-actions-self-hosted-runner-minimum-version-enforcement-extended/, https://github.blog/changelog/2026-02-05-github-actions-early-february-2026-updates/] Self-hosted runners below **v2.329.0** lost the ability to run `./config.sh` starting March 16, 2026 (with a Feb 23–Mar 16, 2026 brownout period beforehand) — a breaking change for any unmaintained self-hosted runner fleet.

---

## 14. Limitations

[Source: https://docs.github.com/en/actions/concepts/overview/usage-limits-billing-and-administration] **Workflow run duration**: a workflow run is cancelled after **35 days**. **Job duration**: GitHub-hosted-runner jobs may run up to **6 hours**; self-hosted-runner jobs up to **5 days**. **Environment gate approval wait**: capped at **30 days**. **Matrix size**: up to **256 jobs per workflow run**. **Re-runs**: a maximum of **50 re-runs per workflow run**. **Self-hosted queue time**: a queued self-hosted job is auto-cancelled after **24 hours**.

[Source: https://docs.github.com/en/actions/concepts/overview/usage-limits-billing-and-administration] **Workflow file size**: max **500 KB** per workflow file. **Check runs**: up to **50,000 check runs per check suite**.

[Source: https://docs.github.com/en/actions/concepts/overview/usage-limits-billing-and-administration] **API/event rate limits**: workflow-triggering events capped at **1,500 events per 10 seconds per repository**; queued workflow runs capped at **500 per 10 seconds**; concurrency-group queueing capped at **100 workflow runs per concurrency group**; `GITHUB_TOKEN` API calls capped at **1,000 requests/hour/repository** (raised to **15,000/hour** on GitHub Enterprise Cloud).

[Source: https://docs.github.com/en/actions/concepts/overview/usage-limits-billing-and-administration] **Cache API rate limits**: **200 uploads/minute**, **1,500 downloads/minute**, **400 deletes/minute**, per repository; default **10 GB** cache storage per repository with LRU eviction beyond that, and unused caches auto-evicted after **7 days**. **Artifact/Packages storage**: billed per plan allotment beyond included free storage (see Performance/Deployment sections).

[Source: https://docs.github.com/en/actions/concepts/overview/usage-limits-billing-and-administration] **Self-hosted runner registration**: capped at **1,500 runner registrations per 5 minutes** per scope; up to **10,000 runners per runner group**. **Concurrent jobs**: plan- and runner-type-dependent; GitHub Enterprise Cloud is documented (per search-derived figures) as supporting up to 500 concurrent standard jobs and 1,000 concurrent larger-runner jobs — [Unresolved: these specific concurrency ceiling numbers were sourced via a WebSearch summary rather than a directly fetched official page snippet in this pass; verify against the live limits page for current figures.]

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions] Secret log redaction is explicitly documented as not fully guaranteed — a documented limitation of the security model rather than a bug, requiring manual masking/hygiene practices from workflow authors.

---

## 15. Debugging

[Source: https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/enabling-debug-logging] Set the `ACTIONS_STEP_DEBUG` secret or repository/organization variable to `true` to enable additional step-debug logging when standard workflow logs are insufficient to diagnose a failure; if both a secret and a variable of that name are set, the secret's value takes precedence.

[Source: https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/re-running-workflows-and-jobs] Failed workflow runs can be re-run (all jobs, or only failed jobs) directly from the Actions UI or via the REST API, and re-runs can optionally be triggered with debug logging enabled for that specific re-run without needing to permanently set the debug secret/variable.

[Source: https://docs.github.com/en/actions] GitHub documents `ACTIONS_RUNNER_DEBUG` (an analogous secret/variable) for enabling additional **runner-level** diagnostic logging, distinct from `ACTIONS_STEP_DEBUG`'s step-level logging. [Inference, not confirmed in docs: the exact current canonical URL for this specific setting was not independently re-fetched in this pass beyond the general debug-logging page above, which covers step-debug logging; treat the runner-debug variable's existence as corroborated by strong secondary/community evidence rather than a directly quoted official docs snippet in this research pass.]

[Source: https://github.com/github/local-action] For debugging custom JavaScript actions specifically (as opposed to whole workflows), GitHub publishes `github/local-action`, letting an action's `main` entrypoint be run and debugged locally (e.g. in VS Code) against emulated Toolkit inputs/outputs.

---

## 16. Integration

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect] GitHub documents OIDC-based integration patterns for **AWS**, **Azure**, **GCP**, and **HashiCorp Vault**, among others, for credential-free cloud deployment from workflows.

[Source: https://docs.github.com/en/actions/tutorials/migrate-to-github-actions/automated-migrations] GitHub Actions Importer documents integration/migration paths from **Azure DevOps**, **Bamboo**, **CircleCI**, **GitLab CI**, **Jenkins**, and **Travis CI**.

[Source: https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments] Deployment integrations use GitHub's native **Deployments API/objects** (`environment`, `environment_url`, deployment `state`), which third-party deployment/observability tools can consume via the REST API to reflect Actions-driven deployments in external dashboards.

[Source: https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions] Custom and third-party actions integrate with the broader ecosystem via **GitHub Marketplace** listings (discoverability, branding) and via the Docker/container-action model, which lets any container-packaged tool be wrapped as an action.

[Source: https://docs.github.com/en/actions] Actions integrates natively with other GitHub features referenced throughout this document — **repository secrets/variables**, **branch protection/rulesets** (as a required-check gate), **Environments**, **Packages** (artifact/cache storage billing is shared with Packages storage), and **security features** (e.g. code scanning workflows, Dependabot-triggered workflows) — though a single consolidated "integration matrix" page was not located in this research pass.

---

## 17. Production considerations

[Source: https://docs.github.com/en/actions/concepts/overview/usage-limits-billing-and-administration] Organization owners (or users with the "View organization Actions metrics" permission) can view Actions usage metrics to understand minute/storage consumption across an organization — relevant for capacity planning and cost control in production use.

[Source: https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions] Billing is per-minute and OS-dependent on GitHub-hosted runners (documented example rates: Linux 1-core ≈ $0.002/min, Windows 2-core ≈ $0.010/min, macOS 3–4 core ≈ $0.062/min — macOS and Windows runners consume included-minutes quota at a documented multiplier versus Linux); included free minutes vary by plan (e.g. Free: 2,000 min/month, Pro/Team: 3,000 min/month, Enterprise Cloud: 50,000 min/month), and usage beyond the included quota is billed to the account's payment method (blocked without one, or capped by configured budgets). Public-repository workflows on standard GitHub-hosted runners, and all self-hosted-runner usage, remain free regardless of plan.

[Source: https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions] Storage beyond included quota is billed by GB-hour: artifact storage (shared with Packages) at documented rates around $0.25/GB-month, cache storage around $0.07/GB-month, and custom runner image storage at the same cache rate; deleting artifacts stops further accrual but does not refund already-accrued charges.

[Source: https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments] For production deployment pipelines specifically, GitHub recommends configuring environment protection rules (required reviewers, branch restrictions, wait timers, custom deployment protection rules) as the primary control point for gating who/what can deploy to a production environment.

[Source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions] For production-grade security posture, GitHub's hardening guidance (least-privilege `GITHUB_TOKEN`, SHA-pinned actions, OIDC over static cloud secrets, avoiding `pull_request_target` misuse, ephemeral self-hosted runners) is presented as the consolidated official checklist, rather than being spread as isolated tips — worth treating as a single canonical reference for production readiness review.

Not documented / could not verify in the pages fetched: a dedicated official "production readiness checklist" or SRE-style runbook page distinct from the security-hardening and usage-limits pages already cited above — GitHub's production guidance is distributed across the Security, Deployment, and Limits/Billing docs rather than consolidated into one dedicated "production considerations" page.
