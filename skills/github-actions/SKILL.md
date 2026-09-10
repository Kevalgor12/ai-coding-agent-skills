---
name: GitHub Actions
description: >-
  GitHub-Actions-specific workflow YAML syntax, reusable workflows,
  actions/cache and artifact-storage mechanics, self-hosted-runner risk,
  cache-poisoning on pull_request_target, and the set-output/save-state
  security fix. Use when the CI platform is (or is being set up as) GitHub
  Actions. Not for platform-agnostic pipeline design (use ci-cd-pipeline) or
  other CI platforms, which have no researched grounding in this library.
spec_version: "1.0"
---

## Purpose & scope

Apply GitHub Actions correctly and version-appropriately: workflow YAML
mechanics, reusable-workflow/composite-action composition, artifact-storage
internals, self-hosted-runner risk, cache-poisoning boundaries, and the
`set-output`/`save-state` security fix. This skill specializes
[ci-cd-pipeline](../ci-cd-pipeline/SKILL.md), which already owns the
platform-agnostic method (stage sequencing, OIDC-over-static-keys posture,
least-privilege tokens, caching's general limits, matrix/fail-fast/
concurrency behavior) — this skill adds GitHub-Actions-specific
implementation depth on top of that, not a restatement of it.

## When to use / When not to use

**Use** when a `.github/workflows/*.yml` file exists or is being authored,
the task names GitHub Actions/a workflow file/a custom action/a self-hosted
runner, or the task configures `GITHUB_TOKEN` permissions, `actions/cache`,
`actions/*-artifact`, or GitHub's OIDC-to-cloud federation. **Do not use**
for platform-agnostic pipeline design with no CI platform chosen yet (route
to [ci-cd-pipeline](../ci-cd-pipeline/SKILL.md)), for a different CI
platform (Jenkins, CircleCI, GitLab CI — none of which have researched
grounding in this library), or for local git hooks (route to
[husky](../husky/SKILL.md), which runs on the developer's machine, not a
runner — Husky documents a `HUSKY: 0` env var specifically to skip its own
install step on CI runners, making the two skills complementary rather than
overlapping).

## Knowledge

**Workflow structure.** A workflow is YAML under `.github/workflows/`,
triggered by an `on` event (`push`, `pull_request`, `schedule` with POSIX
cron — minimum 5-minute interval, UTC, best-effort timing — `workflow_dispatch`
for typed manual/API-triggered runs, or `repository_dispatch` for an
arbitrary external JSON payload). Top-level keys: `name`, `run-name`, `on`,
`permissions`, `env`, `defaults`, `concurrency`, `jobs`. A job's `runs-on`
selects a runner label; jobs run in parallel unless linked by `needs`; a
`strategy.matrix` fans a job out across variable combinations. A step is
`run` (shell) or `uses` (an action, referenced by tag/branch/SHA or a Docker
image), with `with` for inputs and step-scoped `env` as the most specific
override. Eleven expression contexts (`github`, `env`, `vars`, `job`,
`steps`, `runner`, `secrets`, `strategy`, `matrix`, `needs`, `inputs`) back
`${{ }}` expressions, but availability varies by location — e.g. `secrets`
is unavailable inside composite actions [Source: docs.github.com/en/actions/
reference/workflow-syntax-for-github-actions, docs.github.com/en/actions/
learn-github-actions/contexts].

**Reusable-workflow and composite-action composition.** Reusable workflows
(`on: workflow_call`) are invoked from a caller as a job via
`uses: ./.github/workflows/<file>` (same repo) or
`owner/repo/.github/workflows/<file>@ref` (cross-repo), passing typed
`inputs`/`secrets` and consuming results via
`needs.<job_id>.outputs.<name>`; `secrets: inherit` forwards all caller
secrets within the same organization. Composite actions (`action.yml` with
`runs.using: composite`) wrap multiple `run`/`uses` steps behind one step
call. Custom actions have three types: JavaScript (`runs.using: node20` or
`node24`, a `main` entry, optional `pre`/`post` lifecycle scripts), Docker
container, and composite — declared in `action.yml`'s `runs` key, with
`inputs`/`outputs` blocks defining the contract (`INPUT_<NAME>` env vars for
JS/Docker actions) [Source: docs.github.com/en/actions/sharing-automations/
reusing-workflows, docs.github.com/en/actions/creating-actions/
metadata-syntax-for-github-actions].

**Masking beyond registered secrets.** Where a runtime value needs masking
that isn't already a registered secret, use the `::add-mask::VALUE` workflow
command in a step's output [Source: docs.github.com/en/actions/security-for-
github-actions/security-guides/security-hardening-for-github-actions].

**Least-privilege permissions block.** Concretely, this is a `permissions:`
map (workflow-wide or per-job) from `none` up to `read-all`/`write-all`, or
scoped per-resource, e.g.:

```yaml
permissions:
  contents: read
jobs:
  deploy:
    permissions:
      contents: read
      id-token: write   # only the job that needs OIDC gets it
```

[Source: docs.github.com/en/actions/reference/workflow-syntax-for-github-actions]

**OIDC step mechanics.** A job requests a short-lived JWT by declaring
`permissions: id-token: write`; a step (e.g.
`aws-actions/configure-aws-credentials`) exchanges that JWT with the cloud
provider for temporary credentials — no long-lived cloud secret is stored in
GitHub. Trust is configured cloud-side, on the target role/identity's OIDC
trust policy, which validates claims in the presented token (repo, ref,
environment, etc.) before issuing credentials [Source: docs.github.com/en/
actions/security-for-github-actions/security-hardening-your-deployments/
about-security-hardening-with-openid-connect].

**Artifact storage: v3 to v4.** `actions/upload-artifact`/`download-artifact`
v3 was fully blocked on GitHub.com as of **2025-01-30**; v4 is required
there. v4 changed artifacts from mutable to immutable (no appending;
duplicate names within one run fail by default), changed download behavior
(a per-artifact subdirectory when no `name` filter is given; new `pattern`
and `merge-multiple` inputs replace old wildcard `name` matching), and moved
to a new content-addressable storage backend — "10x faster on average" for
downloads than v3 [Version-sensitive, Source: github.blog/changelog/
2024-04-16-deprecation-notice-v3-of-the-artifact-actions]. `download-
artifact@v4+` remains unsupported on GitHub Enterprise Server; GHES users
stay on v3 there [Source: github.com/actions/download-artifact].

**Node runtime migration.** `runs.using` on JavaScript actions currently
accepts `node20` or `node24`; GitHub forces JS actions to `node24` by
default starting **2026-06-02** (opt-out via
`ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true` during the transition), with
`node20` scheduled for complete removal from GitHub-hosted runners on
**2026-09-16** [Version-sensitive, Source: github.blog/changelog/
2025-09-19-deprecation-of-node-20-on-github-actions-runners]. This date is
imminent as of this skill's `last_verified` date — treat any custom action
still targeting `node20` as urgent.

## Decision framework

1. **GitHub-hosted vs. self-hosted runners.** Default to GitHub-hosted:
   fully managed, automatically patched, clean per-job. Self-hosted buys
   custom hardware/OS/tooling control, but you own patching, and — per the
   Security section below — self-hosted runners carry real operational risk
   that GitHub-hosted runners don't. Choose self-hosted only when a specific
   need (private network access, GPU/hardware not available hosted, cost at
   sustained scale) outweighs that risk, and never for public repositories
   [Source: docs.github.com/en/actions/hosting-your-own-runners/
   managing-self-hosted-runners/about-self-hosted-runners].
2. **OIDC vs. static secrets for a given deploy target.** If the target
   (AWS, Azure, GCP, HashiCorp Vault, or another documented OIDC-compatible
   provider) supports federation, use `permissions: id-token: write` plus
   the provider's official configure-credentials action — this is the
   default, not a judgment call (the parent skill already establishes
   OIDC-over-static-keys as the posture; this is its concrete mechanism).
   Fall back to a registered static secret only when the target genuinely
   has no OIDC support.
3. **Reusable workflow vs. duplicating steps.** Extract a reusable workflow
   (`workflow_call`) or composite action when the same job/step sequence is
   about to be copy-pasted across two or more workflow files, or when a
   caller needs to pass different inputs/secrets to otherwise-identical
   logic. For a single workflow file with no duplication pressure, inline
   steps are simpler and should not be prematurely factored out — an
   over-engineering trap in the other direction is building a reusable
   workflow "for future reuse" that has no second caller yet.
4. **Larger runners vs. standard hosted runners vs. a matrix.** If a single
   job is CPU/memory/disk-bound, a larger runner adds resources per-minute
   with no idle cost. If the workload is actually independent permutations
   (OS × version, sharded test suites), a matrix strategy parallelizes
   across standard runners instead — cheaper per-minute, and often more
   effective than one bigger machine for embarrassingly parallel work
   [Source: docs.github.com/en/actions/using-github-hosted-runners/
   using-larger-runners/about-larger-runners].

## Workflow

1. Confirm GitHub Actions is the target platform (else route to the
   parent).
2. Author `on`, `permissions` (least-privilege default), and `jobs` per the
   YAML structure above.
3. For shared logic across two or more workflows, factor into a reusable
   workflow or composite action rather than duplicating steps.
4. Configure `actions/cache` keyed on a lockfile hash with `restore-keys`
   fallbacks; use `actions/upload-artifact`/`download-artifact` v4 syntax
   for build outputs.
5. Wire OIDC (`id-token: write` + the target's configure-credentials
   action) for any cloud deploy step, or a registered secret if the target
   lacks OIDC support.
6. Pin every third-party `uses:` to a full-length commit SHA.
7. Verify no step uses `::set-output::`/`::save-state::`, and that no
   `pull_request_target` job both handles privileged secrets and checks
   out/executes PR head code.
8. State that this skill authors and reviews workflow YAML but does not
   itself run the workflow (Tier A, same posture as the parent).

## Engineering rules

- Reference reusable workflows/composite actions by pinned commit SHA (or,
  for same-repo reusable workflows, by path) — not a mutable tag.
- Use `$GITHUB_OUTPUT`/`$GITHUB_STATE` environment files for step
  outputs/state; never `::set-output::`/`::save-state::`.
- Grant `id-token: write` only to the job that performs the OIDC exchange,
  not workflow-wide.
- Keep `pull_request_target` jobs read-only on cache and free of any PR
  head-code checkout; use `pull_request` or `workflow_run` instead when the
  workflow needs to build/test untrusted PR code.
- Track the `actions/*-artifact` v4 requirement and the Node 20 removal
  timeline as live migration risks in any repo still on older pins.

## Trade-offs

Self-hosted runners buy hardware/network control at the cost of owning
patching and the operational risks in Security below — GitHub-hosted is the
simpler default. Reusable workflows buy DRY composition at the cost of an
extra layer of indirection (a failure now requires checking the caller
*and* the called workflow) — worth it only once duplication is real, not
speculative. Larger runners buy more resources at a materially higher
per-minute rate than standard runners with no idle-cost offset, so they pay
off only for jobs that are actually resource-bound, not merely slow for
other reasons (e.g. an uncached dependency install).

## Anti-patterns

- **Still emitting `::set-output::`/`::save-state::`** instead of writing to
  `$GITHUB_OUTPUT`/`$GITHUB_STATE` — beyond being deprecated, the old
  commands are a documented log-injection vector (see Security).
- **Granting cache write access to a `pull_request_target`-triggered
  workflow** — enables an untrusted PR to poison a cache entry a later
  privileged run will trust (see Security).
- **Running untrusted public-repo workloads on self-hosted runners** —
  GitHub's own guidance says self-hosted runners should "almost never" be
  used for public repositories, since any fork can submit a PR/workflow
  that executes arbitrary code on that runner.
- **Building a reusable workflow before there's a second caller** — an
  over-engineering trap: the indirection cost is paid immediately, the DRY
  benefit only arrives with actual duplication.
- **Pinning third-party actions to a mutable tag** (e.g. `@v1`) instead of a
  commit SHA — a maintainer's account compromise can repoint the tag to
  malicious code without changing the visible version string.

## Security

This section is the deepest in this skill because these three risks are
GitHub-Actions-specific and not covered by the parent
([ci-cd-pipeline](../ci-cd-pipeline/SKILL.md) owns the general
secrets/token/OIDC posture; see it for that layer).

**Self-hosted-runner risk.** Self-hosted runners are not automatically
patched by GitHub — the operator is responsible for OS and software updates
— and, unlike GitHub-hosted runners, do not necessarily start from a clean
instance per job unless built that way (ephemeral/just-in-time runners).
GitHub's own hardening guidance says self-hosted runners should "almost
never be used for public repositories," because any fork can submit a
workflow/PR that executes arbitrary code on the runner, and an unmanaged
runner "can be persistently compromised by untrusted code" if it isn't made
ephemeral between jobs. Mitigation: run self-hosted runners as
ephemeral/JIT instances with a clean environment per job, and do not attach
them to public repositories at all [Source: docs.github.com/en/actions/
hosting-your-own-runners/managing-self-hosted-runners/
about-self-hosted-runners, docs.github.com/en/actions/security-for-
github-actions/security-guides/security-hardening-for-github-actions].

**Cache poisoning on low-trust triggers.** `actions/cache` restricts
low-trust event triggers — specifically `pull_request_target` — to
**read-only** cache access. This exists to prevent an untrusted PR from
writing a poisoned cache entry that a later, privileged run (one that does
carry the base repo's secrets/token) would then restore and trust. This is
a separate, narrower issue from the caching *limits* the parent skill
covers (7-day eviction, 10GB cap, LRU) — it's about trust boundary, not
capacity [Source: docs.github.com/en/actions/using-workflows/
caching-dependencies-to-speed-up-workflows].

**`pull_request_target` + PR-head-checkout combination.**
`pull_request_target` runs with the base repository's privileged
token/secrets (unlike `pull_request`, which runs with a read-only token and
no secrets for forked PRs). Checking out and executing the PR's *head* code
under that trigger hands an attacker-controlled PR both write access and
secrets. GitHub recommends avoiding this combination — use `workflow_run`
instead, or never check out untrusted PR code under a privileged-context
trigger [Source: docs.github.com/en/actions/security-for-github-actions/
security-guides/security-hardening-for-github-actions].

**The `set-output`/`save-state` deprecation was a security fix, not just an
API cleanup.** The old `::set-output::`/`::save-state::` workflow commands
could be triggered by untrusted content appearing in step logs (log
injection), letting an attacker influence workflow outputs/state the author
never intended. The replacement — writing to the `$GITHUB_OUTPUT`/
`$GITHUB_STATE` environment files instead of emitting a magic log string —
is not subject to the same log-parsing injection vector [Version-sensitive,
Source: github.blog/changelog/2022-10-11-github-actions-deprecating-
save-state-and-set-output-commands]. Deprecation was announced 2022-10-11;
per the research, the commands still ran with a deprecation warning rather
than a hard failure as of the last confirmed check — **Unresolved: whether
GitHub has since hard-removed them was not re-confirmed against a live page
in the underlying research; verify current status before assuming either
way.**

## Performance

(Deep general method — the caching-limits/matrix/concurrency *principles*
— is owned by [ci-cd-pipeline](../ci-cd-pipeline/SKILL.md); this is the
concrete GitHub-Actions mechanism for each.)

**`actions/cache` usage.** Key the cache on a hash of the dependency
lockfile, with sequential fallback prefixes:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ hashFiles('package-lock.json') }}
    restore-keys: |
      npm-
```

Built-in caching flags on setup actions (e.g. `actions/setup-node`'s
`cache:` input) wrap this same mechanism [Source: docs.github.com/en/
actions/using-workflows/caching-dependencies-to-speed-up-workflows].

**Artifact storage v3→v4: ~10x faster downloads.** As covered in Knowledge/
Security above, `actions/upload-artifact`/`download-artifact` v4's new
content-addressable storage backend is documented as making artifact
downloads "10x faster on average" than v3 — a concrete, dated improvement
tied to the mandatory v3→v4 migration (v3 blocked on GitHub.com since
2025-01-30) [Version-sensitive, Source: github.blog/changelog/
2024-04-16-deprecation-notice-v3-of-the-artifact-actions].

**Larger runners.** GitHub-managed larger runners provide more RAM, CPU,
disk, and (for some configurations) GPU acceleration than standard hosted
runners, with optional static IPs/private networking and runner-group
access control; billed strictly per execution minute with no idle cost
[Source: docs.github.com/en/actions/using-github-hosted-runners/
using-larger-runners/about-larger-runners].

## Testing

GitHub does not document a dedicated test framework for whole workflows
themselves; the documented mechanism for iterating after a failure is
re-running failed or all jobs (optionally with debug logging) from the
Actions UI or REST API [Source: docs.github.com/en/actions/
managing-workflow-runs-and-deployments/managing-workflow-runs/
re-running-workflows-and-jobs]. For **authoring custom JavaScript actions**
specifically, GitHub's own `actions/toolkit` repo unit-tests action logic
with standard JS test frameworks against `@actions/core`/`@actions/github`,
decoupled from an actual workflow run, and GitHub publishes `github/
local-action` for running/debugging a JS action's entrypoint locally (e.g.
in VS Code) against emulated Toolkit inputs/outputs [Source: github.com/
actions/toolkit, github.com/github/local-action]. **Unresolved:** the
widely-used community tool for running full workflows locally
(`nektos/act`) is not GitHub-maintained and is out of scope for this
official-docs-grounded skill — do not present it as an official GitHub
tool.

## Failure handling

- If it's unclear whether the platform is GitHub Actions vs. still
  undecided, ask or route to [ci-cd-pipeline](../ci-cd-pipeline/SKILL.md)
  rather than assuming.
- If shell/execution isn't available, produce workflow YAML advisory-only
  and state plainly that the workflow was not run.
- If a version-sensitive fact (e.g. whether `set-output` has been hard-
  removed) can't be confirmed against current docs, say "verify against
  current docs" rather than assert a resolved date.

## Escalation

- A proposal to run self-hosted runners on a public repository is flagged
  and requires explicit confirmation, given the "almost never" guidance.
- Any `pull_request_target` change that adds cache write access or PR
  head-code checkout is flagged as security-sensitive and requires
  confirmation before proceeding.
- A production-deployment-affecting workflow change defers to the parent's
  escalation rule (present trade-offs, require confirmation).

## Outputs & verification

- **Outputs:** workflow/reusable-workflow/composite-action YAML; analysis
  of runner choice, cache/artifact configuration, or a security-hardening
  gap.
- **Verify:** third-party `uses:` references are SHA-pinned; no
  `::set-output::`/`::save-state::` remains; no `pull_request_target` job
  combines privileged secrets, PR-head checkout, and cache write access;
  every version-specific claim carries the date/range it holds for.

## References

- [ci-cd-pipeline](../ci-cd-pipeline/SKILL.md) — the parent skill; general
  pipeline design, OIDC-over-static-keys posture, least-privilege tokens,
  caching's general limits, matrix/fail-fast/concurrency behavior.
- [husky](../husky/SKILL.md) — local git hooks; complementary via the
  `HUSKY: 0` CI-skip pattern.
- [research/technologies/github-actions.md](../../research/technologies/github-actions.md) — primary research source for every claim above.
- Full source list: `skill.yaml.source_references`.
