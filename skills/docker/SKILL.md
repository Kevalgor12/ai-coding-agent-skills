---
name: Docker
description: >-
  Docker-specific Engine/CLI/BuildKit/Compose mechanics: Engine API version
  floor, the Go SDK module migration, Build Checks' Buildx/syntax gates,
  Compose V2 build-field gates (ssh, platforms), cgroup v1's deprecation
  timeline, Enhanced Container Isolation's WSL2/kernel floor, and
  isolation-runtime selection. Use for Docker Engine/API/Compose/Buildx
  version-compatibility questions. Not general image authoring/layering or
  the root-daemon security model, which containerization already covers.
spec_version: "1.0"
---

## Purpose & scope

Apply Docker's concrete Engine/CLI/API/BuildKit/Compose mechanics correctly
and version-appropriately. The engine-agnostic image-authoring method
(layer-caching order, multi-stage builds, the root-daemon-by-default
security model, rootless-vs-`userns-remap`, Docker Content Trust's removal)
is already owned by the parent skill,
[containerization](../containerization/SKILL.md) — this skill adds Docker's
implementation depth on top of it: Engine API versioning, the Go SDK
migration, Build Checks' version gates, Compose V2's build-field version
gates, cgroup v1's deprecation timeline, and Enhanced Container Isolation's
platform floor. Deep cross-cutting security threat modeling is owned by
security-engineering (`SK-QA-002`) — not restated here.

## When to use / When not to use

**Use** when a task turns on Docker Engine API or Go SDK version
compatibility, whether Build Checks is actually available, whether a
specific Compose V2 build field works at the project's Compose version,
selecting an isolation runtime for a stated threat model, or cgroup v1/v2
and Enhanced Container Isolation platform-floor questions. **Do not use**
for general Dockerfile/image authoring, layer-caching order, or non-root
defaults with no version-specific question — that's
[containerization](../containerization/SKILL.md). Not for a stack that
doesn't use Docker at all, or for deep cross-cutting threat modeling beyond
Docker-specific mechanics (route to security-engineering, `SK-QA-002`, not
yet authored).

## Knowledge

**Engine API versioning.** The current stable Docker Engine API version is
**v1.56**, paired with Engine 29.8. Engine 29.0.0 raised the *minimum*
supported API version to **v1.44** (compatible with Engine 25.0+ clients);
API versions before **v1.40** are documented as deprecated/unsupported
against current Engine releases [Source: https://docs.docker.com/engine/api/]
[Source: https://docs.docker.com/engine/release-notes/29/]. Concretely: a
client built against a pre-v1.40 API is unsupported against a current
daemon, even though the API itself is otherwise documented as
backward-compatible ("you don't need to update code that uses the API
unless you need to take advantage of new features")
[Source: https://docs.docker.com/engine/api/].

**Go SDK module migration.** As of Engine 29.0.0, the Go module
`github.com/docker/docker` is deprecated in favor of
`github.com/moby/moby/client` and `github.com/moby/moby/api` — a breaking
change specifically for Go SDK consumers importing the old module path
[Source: https://docs.docker.com/engine/release-notes/29/]. New Go tooling
against a current Engine should import the new module paths from the start,
not the deprecated one.

**Build Checks version gates.** `docker build --check` requires **Buildx
>= 0.15.0** and **Dockerfile syntax >= 1.8**, gated independently of the
Docker Engine version [Source: https://docs.docker.com/reference/build-checks/].
A project can be on a current Engine and still lack Build Checks if its
Buildx or `# syntax=` directive version is too old — the Engine version
alone does not guarantee availability.

**Compose V2 build-field version gates.** Compose V2 added several
build-related fields absent from V1: `cache_to`, `no-cache`, `pull`,
`secrets` (build-time secrets), and `tags`. Within V2 itself, two fields
have their own later gates: **`ssh` was added in V2.4.0+**, and
**`platforms` (multi-arch builds) was added in V2.11.0+**, and `platforms`
additionally requires a `docker-container` Buildx driver to be configured
[Source: https://www.docker.com/blog/new-docker-compose-v2-and-v1-deprecation/].
Relying on `platforms` or `ssh` without checking both the Compose version
and, for `platforms`, the active Buildx driver is a silent-failure risk.

**cgroup v1 deprecation timeline.** cgroup v1 support is deprecated as of
Engine 29.0.0, with support continuing only until **May 2029**
[Source: https://docs.docker.com/engine/release-notes/29/]. This is a real,
dated deprecation with a long tail — new deployments should target cgroup
v2 hosts, but existing cgroup v1 hosts are not facing an imminent break.

**Enhanced Container Isolation (ECI) platform floor.** On the WSL2 backend,
ECI hard-requires **WSL >= 2.6** and **Linux kernel >= 6.3.0**, because it
depends on kernel features unavailable below that version
[Source: https://docs.docker.com/security/for-admins/hardened-desktop/enhanced-container-isolation/limitations/].
Adopting ECI without confirming both floors first will fail on an
unsupported host rather than degrade gracefully.

## Decision framework

1. **Isolation runtime, given the actual threat model.** Docker's default
   runtime is `runc`, invoked under containerd; alternative runtimes
   (**Wasmtime** for WebAssembly, **gVisor** and **Kata Containers** for
   sandboxed/VM-level isolation) integrate natively at the containerd-shim
   layer and are selectable purely via `docker run --runtime`, with no
   further daemon reconfiguration
   [Source: https://docs.docker.com/engine/daemon/alternative-runtimes/].
   Default to `runc` for trusted, first-party workloads — switching runtime
   for everything is unjustified overhead. Reach for gVisor/Kata
   specifically when running genuinely untrusted code (multi-tenant
   execution, user-submitted workloads) where the stronger isolation is a
   real requirement, not a precaution applied by default.
2. **Docker Build Cloud vs. self-hosting multi-platform builders.**
   Self-hosted native builder nodes or QEMU emulation (see
   [containerization](../containerization/SKILL.md#performance)) work
   without an external dependency but require maintaining
   architecture-specific build infrastructure. **Docker Build Cloud**
   offers managed, Docker-hosted multi-node builders as an alternative
   [Source: https://docs.docker.com/build/building/multi-platform/]. Justify
   it against the actual build volume and compute cost of self-hosting:
   infrequent or low-compute multi-arch builds rarely justify the
   operational overhead of a self-hosted native-builder fleet; frequent,
   compute-heavy multi-arch builds are where a managed service's cost
   trades favorably against engineering time spent running that fleet.
   Don't default to either without weighing the actual build frequency.
3. **Whether to adopt Enhanced Container Isolation.** ECI is only reachable
   on a WSL2 backend meeting the WSL >= 2.6 / kernel >= 6.3.0 floor (see
   Knowledge). Confirm both before proposing it as a hardening step; a host
   below either floor cannot use it regardless of how well-justified the
   security case is, and the correct action is flagging the platform gap,
   not assuming the feature is available.

## Engineering rules

- Verify a Go SDK client's API version against the daemon's reported
  version before assuming compatibility; treat a pre-v1.40 client against a
  current daemon as unsupported, not merely deprecated
  [Source: https://docs.docker.com/engine/api/] [Source: https://docs.docker.com/engine/release-notes/29/].
- Import `github.com/moby/moby/client` and `github.com/moby/moby/api` for
  new Go tooling against Engine >= 29.0.0; don't start new code against the
  deprecated `github.com/docker/docker` module
  [Source: https://docs.docker.com/engine/release-notes/29/].
- Before relying on `docker build --check`, confirm Buildx >= 0.15.0 and
  Dockerfile syntax >= 1.8 are both actually in use — neither is implied by
  the Engine version alone
  [Source: https://docs.docker.com/reference/build-checks/].
- Before using a Compose build field, check its version gate: `ssh` needs
  Compose >= V2.4.0; `platforms` needs Compose >= V2.11.0 *and* a
  `docker-container` Buildx driver configured
  [Source: https://www.docker.com/blog/new-docker-compose-v2-and-v1-deprecation/].
- Treat cgroup v1 as a long-tail deprecation (supported through May 2029),
  not an immediate break — steer new deployments to cgroup v2 without
  presenting existing cgroup v1 hosts as broken today
  [Source: https://docs.docker.com/engine/release-notes/29/].
- Confirm WSL >= 2.6 and kernel >= 6.3.0 before proposing Enhanced
  Container Isolation on a WSL2 backend
  [Source: https://docs.docker.com/security/for-admins/hardened-desktop/enhanced-container-isolation/limitations/].

## Anti-patterns

- **Assuming a pre-v1.40 API client works against a current Engine
  daemon** — it's documented as unsupported, not just legacy
  [Source: https://docs.docker.com/engine/api/].
- **Using a Compose `platforms` or `ssh` build field without checking its
  version gate** (V2.11.0+ and a `docker-container` driver for `platforms`;
  V2.4.0+ for `ssh`) — the field silently isn't available below the gate
  [Source: https://www.docker.com/blog/new-docker-compose-v2-and-v1-deprecation/].
- **Writing new Go tooling against `github.com/docker/docker`** for a
  project targeting Engine >= 29.0.0 — the module is deprecated in favor of
  `github.com/moby/moby/client`/`github.com/moby/moby/api`
  [Source: https://docs.docker.com/engine/release-notes/29/].
- **Assuming `docker build --check` works because the Engine is current** —
  it's gated independently on Buildx >= 0.15.0 and Dockerfile syntax >= 1.8
  [Source: https://docs.docker.com/reference/build-checks/].
- **Switching every workload to gVisor/Kata "for security"** — the
  domain's over-engineering trap; the containerd-shim runtime swap is real
  and cheap to invoke, but unjustified for trusted first-party workloads
  where default `runc` is already documented as secure when combined with
  non-root, non-privileged processes.

## Security

**Build Checks' secrets-in-metadata rule.** Build Checks include a
documented rule preventing sensitive data from being placed in `ARG` or
`ENV` instructions, since both can leak into image history/metadata
[Source: https://docs.docker.com/reference/build-checks/]. This is a
concrete, checkable rule `docker build --check` enforces — not general
secrets-handling advice, but a specific Dockerfile-instruction-level check.

**Alternative-runtime extensibility at the containerd-shim layer.** Beyond
the default `runc`, Docker's namespace/cgroup/capability isolation can be
swapped for a stronger boundary via `docker run --runtime`: **Wasmtime**
(WebAssembly), **gVisor**, and **Kata Containers** (sandboxed/VM-level
isolation) implement the containerd shim API natively and require no daemon
reconfiguration beyond the `--runtime` flag; drop-in `runc`-compatible
replacements (e.g. **youki**) instead require explicit daemon
reconfiguration and are not selectable purely via the flag
[Source: https://docs.docker.com/engine/daemon/alternative-runtimes/]. This
is a real, documented extensibility point for workloads whose threat model
genuinely needs stronger isolation than the default runtime provides — see
Decision framework above for when it's actually justified.

**Docker Scout's SBOM/recalibration mechanism.** Docker Scout analyzes an
image's contents to produce a Software Bill of Materials (SBOM) and
evaluate it against vulnerability advisories. After analysis, Scout stores
a metadata snapshot and recalibrates against newly disclosed CVEs without
needing to re-scan the image — i.e. an image's vulnerability status can
update as new advisories are published, without re-running the scan itself
[Source: https://docs.docker.com/scout/]. Accessible via Docker Desktop or
`docker scout` CLI subcommands (e.g. `docker scout cves`).

Deep threat modeling beyond these Docker-specific mechanics is owned by
security-engineering (`SK-QA-002`) — not
restated here.

## Performance

Beyond QEMU-vs-native-builders-vs-cross-compilation (already covered by
[containerization](../containerization/SKILL.md#performance)), **Docker
Build Cloud** is documented as a managed, Docker-hosted alternative to
self-hosting native multi-node builder infrastructure for multi-platform
builds [Source: https://docs.docker.com/build/building/multi-platform/] —
see Decision framework above for when the managed option is actually
justified against self-hosting's operational cost.

## Testing

`docker build --check` doubles as a pre-flight validation pass over a
Dockerfile and build configuration without producing build output — useful
as a fast pre-build gate once its Buildx/syntax version gate is met (see
Knowledge) [Source: https://docs.docker.com/reference/build-checks/].
Docker's docs also cover **Testcontainers** (and **Testcontainers Cloud**)
as the official pattern for integration-testing against real containerized
dependencies rather than mocks [Source: https://docs.docker.com/testcontainers/];
deeper test-strategy method for that pattern belongs to the app's own
testing-strategy skill, not restated here.

## Failure handling

- If the Docker Engine/API/Buildx/Compose (or WSL2/kernel) version cannot
  be determined, ask for it or state the version the guidance assumes
  before making a version-gated claim; never assume "latest" silently.
- If shell is unavailable/denied, degrade to advisory version-compatibility
  analysis (state the gate, don't run `docker`/`docker compose`/`buildx`)
  and say so.
- If a claim would depend on a consolidated cross-major Engine
  breaking-changes page that the underlying research did not find (only
  inline per-release notes were located), say "verify against the current
  Engine release notes" rather than assert by analogy to Engine 29.0.0's
  documented changes.

## Escalation

- Switching a production workload's container runtime (e.g. to gVisor/Kata)
  or its cgroup-version targeting has real operational impact and requires
  explicit confirmation before applying, not unilateral action.

## Outputs & verification

- **Outputs:** version-compatibility analysis (API client, Go SDK import,
  Build Checks setup, or Compose build field against the project's actual
  versions), plus config/runtime changes (Compose fields, `--runtime`
  selection) reflecting the correct version gate.
- **Verify:** the API/client compatibility claim is checked against the
  daemon's actual reported API version; any recommended Compose build field
  is checked against the project's real Compose version (and, for
  `platforms`, an active `docker-container` Buildx driver); any Go SDK code
  for Engine >= 29.0.0 targets the current module path, not the deprecated
  one.

## References

- Source list: see `skill.yaml.source_references` — Docker's official docs
  (`docs.docker.com`), the Docker blog's Compose V2 migration post, and
  this library's version/security/performance knowledge maps, all
  retrieved 2026-09-10 via `research/technologies/docker.md` and
  `research/knowledge-maps/*.md`.
- Parent skill: [containerization](../containerization/SKILL.md) — general
  image-authoring, layering, multi-stage builds, and the root-daemon
  security model.
- Cross-cutting reference: security-engineering (`SK-QA-002`) — deep threat
  modeling beyond Docker-specific mechanics.
