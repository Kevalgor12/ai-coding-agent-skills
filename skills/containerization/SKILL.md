---
name: Containerization
description: >-
  Containerize an application or service — write efficient, secure images
  (small base, non-root, layer caching, multi-stage builds), compose local
  dependency stacks, and address image vulnerability scanning. Use when
  containerizing an app or standing up local dependencies in containers.
  Not for CI/CD pipeline design or deployment/release strategy, which are
  separate skills.
spec_version: "1.0"
---

## Purpose & scope

Design container images and local compose stacks — independent of which
container engine is used, though in this library's research Docker is the
only profiled implementation, so the paired
[docker](../docker/SKILL.md) technology skill adds implementation depth
rather than covering a meaningfully different engine. CI/CD pipeline design
is a separate concern (ci-cd-pipeline, not yet authored in this library);
deployment/release strategy once an image exists belongs to
[deployment-release](../deployment-release/SKILL.md).

## When to use / When not to use

**Use** when containerizing an application or service, standing up local
dependencies (databases, caches, search engines) in containers for
development, or reviewing an existing image's size/cache-efficiency/
security posture. **Do not use** for CI/CD pipeline design once
containerization is settled, or for deployment/release strategy once an
image already exists.

## Knowledge

**Build performance is dominated by layer-caching order, and this is the
single highest-leverage decision in image authoring.** Any changed
instruction invalidates that layer and every subsequent one — the
documented pattern is ordering rarely-changing instructions (dependency
installation) before frequently-changing ones (`COPY . .`), so a source-code
change doesn't force a full dependency reinstall on every build
[Source: docs.docker.com/build/cache/]. BuildKit cache mounts
(`RUN --mount=type=cache`) persist package-manager/dependency caches across
builds independent of layer caching; bind mounts are more efficient than
`COPY` for build-context-only files [Source: docs.docker.com/build/building/
best-practices/].

**Multi-stage builds separate the build toolchain from the runtime image**,
avoiding shipping compilers/dev-dependencies in the final artifact — this is
the mechanism behind "small base image" advice, not a separate practice
from it.

**The container daemon runs with root privileges by default, and this
shapes every other security decision** [Source: docs.docker.com/engine/
security/]. Access to the daemon must be restricted to trusted users; Unix
sockets are recommended over TCP, and when the API must be network-exposed,
HTTPS with certificates is required. Layered hardening options beyond the
default: a capability allowlist (unnecessary Linux capabilities dropped by
default, further restrictable via `--cap-drop`/`--cap-add`), user
namespaces (`userns-remap`), and seccomp profiles. **Rootless mode is
architecturally distinct from `userns-remap`**: rootless mode runs both the
daemon and containers inside a user namespace with no root privileges at
all, while `userns-remap` still runs the daemon itself as root — don't
conflate the two when advising on a hardening posture.

**A real, dated breaking change removed image-signature verification from
the CLI**: Docker Content Trust (`DOCKER_CONTENT_TRUST=1`/`docker trust`)
was removed from the CLI as of Docker Engine 29.0.0
[Source: docs.docker.com/engine/release-notes/29/]. Any guidance or
existing workflow relying on Content Trust needs to be flagged and
re-evaluated against this removal, not carried forward as if it still
works.

**Multi-platform builds have real, non-obvious performance costs.** QEMU
emulation requires no Dockerfile changes but is much slower for
compute-heavy tasks; native builder nodes or `BUILDPLATFORM`/`TARGETPLATFORM`
cross-compilation avoid the emulation penalty [Source: docs.docker.com/
build/building/multi-platform/]. On Apple Silicon specifically, images
without native ARM64 support run under QEMU as "best effort" only —
emulated containers run slower, use more memory, and `inotify`-based
filesystem change notifications do not work under emulation
[Source: docs.docker.com — known issues].

## Decision framework

1. **Order Dockerfile instructions by change frequency, not by logical
   grouping** — dependency installation before source copy, always, unless
   a specific reason overrides it.
2. **Default to a non-root user** unless there's a stated, justified reason
   the process needs root (rare, and should be explicitly called out when
   it happens).
3. **Use a multi-stage build whenever a build toolchain (compilers,
   dev-dependencies) would otherwise ship in the runtime image** — this is
   the default, not an optimization to consider later.
4. **Choose rootless mode vs. `userns-remap` vs. default-root-daemon
   deliberately** based on the actual threat model — rootless is the
   strongest posture (no root privileges at all) but has real operational
   trade-offs (subordinate UID/GID allocation requirements); don't default
   to the weakest option out of inertia.
5. **If multi-platform builds are needed, choose the build strategy
   (QEMU vs. native builders vs. cross-compilation) based on how
   compute-heavy the build actually is** — QEMU's simplicity trades against
   real slowdown for non-trivial builds.

## Workflow

1. Confirm the app's runtime, dependencies, and any local-dev stack it
   needs (databases, caches).
2. Choose a base image and design the instruction order for cache
   efficiency (dependency install before source copy).
3. Use a multi-stage build if a build toolchain is involved.
4. Default to a non-root user; choose a hardening posture (rootless mode,
   `userns-remap`, capability drops, seccomp) deliberately based on the
   threat model.
5. If local dependencies are needed, design a compose stack standing up
   the app plus those dependencies.
6. If image scanning is available, run it and address findings before
   treating the image as production-ready.
7. Hand off to deployment-release for how the resulting image actually
   gets deployed, and to ci-cd-pipeline (not yet authored) for how it gets
   built/tested/pushed automatically.

## Engineering rules

- Order instructions by change frequency (dependency install before source
  copy) — this is the default, not a case-by-case judgment call.
- Default to non-root; state the reason explicitly on the rare occasion
  root is genuinely needed.
- Use multi-stage builds whenever a build toolchain would otherwise ship in
  the runtime image.
- Don't recommend Docker Content Trust (`DOCKER_CONTENT_TRUST`/`docker
  trust`) for Engine 29.0.0+ — it was removed from the CLI; flag the break
  if existing workflows depend on it.
- Choose a multi-platform build strategy based on actual compute cost, not
  by defaulting to QEMU emulation for everything.

## Trade-offs

Rootless mode buys the strongest privilege posture at the cost of real
operational complexity (subordinate UID/GID allocation, some feature
limitations vs. the default daemon). `userns-remap` is a lighter-weight
middle ground that still leaves the daemon itself running as root.
Multi-stage builds buy a smaller, more secure runtime image at the cost of
a longer/more complex Dockerfile. QEMU-based multi-platform builds buy
simplicity (no Dockerfile changes) at the cost of real slowdown for
compute-heavy builds, where native builders or cross-compilation trade
setup complexity for speed.

## Anti-patterns

- **Copying source before installing dependencies** — invalidates the
  dependency-install cache layer on every source change, the single most
  common build-cache mistake.
- **Running as root without a stated reason** — the default posture should
  be non-root; root should be a deliberate, justified exception.
- **Relying on Docker Content Trust workflows on Engine 29.0.0+** — it was
  removed from the CLI; a workflow still referencing `DOCKER_CONTENT_TRUST`
  will silently stop providing the verification it once did.
- **Conflating rootless mode with `userns-remap`** — they address
  different layers of "don't run as root"; treating them as
  interchangeable misrepresents the actual security posture.
- **Defaulting to QEMU emulation for compute-heavy multi-platform builds**
  without considering native builders — an avoidable, real performance cost.

## Security

The daemon runs root by default; access must be restricted to trusted
users, with Unix sockets preferred over a network-exposed API (HTTPS +
certificates when exposure is unavoidable). Hardening layers: capability
allowlisting (`--cap-drop`/`--cap-add`), user namespaces (`userns-remap`),
rootless mode (no root privileges at all, distinct from `userns-remap`),
and seccomp profiles — layered on top of and compatible with host Linux
Security Modules (AppArmor/SELinux). Docker Content Trust was removed from
the CLI as of Engine 29.0.0 — a real, dated breaking change for any
workflow still relying on `DOCKER_CONTENT_TRUST`/`docker trust`. Image
scanning (e.g. Docker Scout, which produces an SBOM and evaluates it
against vulnerability advisories, recalibrating against newly disclosed
CVEs without re-scanning) should run before an image is treated as
production-ready. Deep threat modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

Layer-caching order and BuildKit cache mounts are the two highest-leverage
build-performance levers — see Knowledge above. Multi-platform build
strategy (QEMU vs. native builders vs. cross-compilation) should match the
build's actual compute cost; Apple Silicon's QEMU-based emulation for
non-native-ARM64 images carries documented slowdowns and a broken
`inotify` behavior worth knowing about before debugging a mysterious
file-watch failure. Deep performance method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

Image-level testing (does the image build correctly, run as expected, pass
a vulnerability scan) is this skill's concern; application-level testing
inside a container is owned by the app's own technology/testing skills.
Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If the app's runtime/dependencies are too thin to design an image
  (unclear entrypoint, missing dependency list), request them rather than
  guessing a base image.
- If an image already exists, work within its structure unless a rework
  is explicitly requested.

## Escalation

- A hardening-posture change for an existing production image (e.g.
  switching to rootless mode) can have real operational impact — presented
  with trade-offs for explicit confirmation, not applied unilaterally.

## Outputs & verification

- **Outputs:** Dockerfile/image authoring guidance (base image, layering,
  multi-stage structure, non-root user), and a compose configuration when
  local dependencies are needed.
- **Verify:** the image runs non-root by default; layer order minimizes
  cache invalidation; a multi-stage build is used wherever a toolchain
  would otherwise bloat the runtime image.

## References

- [research/knowledge-maps/performance-knowledge-map.md](../../research/knowledge-maps/performance-knowledge-map.md)
- [research/knowledge-maps/security-knowledge-map.md](../../research/knowledge-maps/security-knowledge-map.md)
