# Docker — Technology Research

Research date: 2026-09-09. Primary source: `docs.docker.com/*` (canonical documentation host — confirmed reachable and current at time of research; source repo is the open `docker/docs` GitHub org repository). Secondary official sources used only to locate/confirm facts already anchored to `docs.docker.com` or to cite release-note content not mirrored there: `docker.com/blog/*` (official Docker Inc. blog) and `github.com/docker/compose` / `github.com/moby/moby` (official Docker/Moby GitHub org repos, used for release-note dates). All claims are tagged per this project's convention: `[Source: <url>]` for documented facts, `[Inference, not confirmed in docs]` for reasoning, "Not documented / could not verify" where docs did not cover something in the pages fetched, and "Unresolved: ..." where confidence is genuinely low.

**Doc host note**: No evidence of a canonical-doc-host migration was found — `docs.docker.com` remains the single documentation host for Docker Engine, Docker Desktop, Docker Compose, Docker Build/BuildKit, Docker Hub, and Docker Scout, all under one unified docs site (`docs.docker.com/engine/`, `/compose/`, `/build/`, `/desktop/`, `/reference/`, `/docker-hub/`, `/scout/`). This is itself worth noting: Docker consolidated what were historically more separated doc trees (Engine vs. Compose vs. Desktop) into one site.

**Scope note**: "Docker" is a family of related but distinct products — the open-source Docker Engine/Moby, the commercial Docker Desktop application, Docker Compose (the multi-container orchestration tool), Docker Build/BuildKit (the build subsystem), Docker Hub (the registry SaaS), and Docker Scout (vulnerability/SBOM analysis). This research treats "Docker" primarily as Docker Engine + the CLI + BuildKit + Compose, since that is the core surface a coding-agent skill would need to be grounded in, while noting product-specific facts (e.g. Desktop licensing) where they matter for production/deployment guidance.

---

## 1. Core concepts

[Source: https://docs.docker.com/get-started/docker-overview/] Docker is described as "an open platform for developing, shipping, and running applications," enabling developers to separate applications from infrastructure via containerization.

[Source: https://docs.docker.com/get-started/docker-overview/] An **image** is "a read-only template with instructions for creating a Docker container." Images are commonly layered on top of a base image (e.g. Ubuntu) with additional customization; a **Dockerfile** defines the steps to build an image, and each instruction in it creates a layer — only layers that change need to be rebuilt on update.

[Source: https://docs.docker.com/get-started/docker-overview/] A **container** is "a runnable instance of an image" — a loosely isolated environment in which an application runs with everything it needs bundled in. Containers are lightweight, portable across environments, and can be created, started, stopped, moved, or deleted via the Docker API or CLI.

[Source: https://docs.docker.com/get-started/docker-overview/] A **registry** stores Docker images; Docker Hub is the default public registry, though private registries are supported. `docker pull` retrieves images from a configured registry, `docker push` uploads them.

[Source: https://docs.docker.com/engine/] Docker Engine is "an open source containerization technology for building and containerizing your applications," composed of: the **server** (`dockerd`, a long-running daemon process), a set of **APIs** for programmatic interaction with the daemon, and a **CLI client** (`docker`) that talks to the daemon over those APIs.

[Source: https://docs.docker.com/engine/daemon/alternative-runtimes/] Under the daemon, Docker Engine uses **containerd** to manage the container lifecycle (create/start/stop), and containerd by default uses **runc** as the low-level OCI runtime that actually creates and runs containers.

[Source: https://docs.docker.com/reference/dockerfile/] The **Dockerfile syntax directive** (e.g. `# syntax=docker/dockerfile:1`) decouples the Dockerfile's own feature-version from the installed Docker Engine version, letting a Dockerfile opt into newer BuildKit frontend features without requiring an Engine upgrade.

---

## 2. Architecture

[Source: https://docs.docker.com/engine/] Docker follows a **client-server model**: the CLI ("the primary way that many Docker users interact with Docker") sends commands to the Docker daemon via the Docker API, either over UNIX sockets or a network interface; the daemon (`dockerd`) listens for API requests and manages Docker objects (images, containers, networks, volumes).

[Source: https://docs.docker.com/engine/daemon/alternative-runtimes/] Underneath `dockerd`, **containerd** manages the container lifecycle, and by default delegates the actual process-level container execution to **runc**, an OCI-runtime-spec implementation. containerd can also delegate to alternative runtimes via native containerd shims (documented examples: **Wasmtime** for WebAssembly workloads, **gVisor** and **Kata Containers** for sandboxed/VM-isolated execution) or via drop-in `runc`-compatible replacements requiring daemon reconfiguration (documented example: **youki**, a Rust reimplementation of runc). Runtime selection is exposed via `docker run --runtime`.

[Source: https://docs.docker.com/engine/security/] Isolation is built from Linux kernel primitives: **namespaces** (pid, net, ipc, mnt, uts — "the first and most straightforward form of isolation," present in the kernel since roughly 2.6.15–2.6.26) and **control groups / cgroups** (resource accounting and limiting — pid, memory, cpu, blkio, present since kernel 2.6.24).

[Source: https://docs.docker.com/engine/network/] By default, on Linux, Docker creates a **default bridge network** at daemon startup; containers on it can reach the outside world via NAT/masquerading if the host has connectivity, but cannot resolve each other by container name (only by IP) unless placed on a user-defined bridge network, which does provide DNS-based name resolution between containers.

[Source: https://docs.docker.com/engine/storage/] Two distinct storage concerns exist in the architecture: (1) how the **daemon itself stores image/container layers on disk** (storage drivers, e.g. `overlay2`), and (2) how **container data persists outside the writable container layer** (volumes, bind mounts, tmpfs, image mounts, named pipes).

Not documented / could not verify in the pages fetched: a single consolidated architecture diagram showing daemon ↔ containerd ↔ containerd-shim ↔ runc process relationships and how shim persistence allows containers to survive a `dockerd` restart — the fetched pages describe the components' roles individually but this research did not locate one canonical page presenting the full process tree.

---

## 3. APIs

[Source: https://docs.docker.com/engine/api/] The **Docker Engine API** is a RESTful, HTTP-based API. It is versioned, and "a given version of the Docker Engine SDK supports a specific version of the Docker Engine API, as well as all earlier versions." Requests can be made directly via `curl`/`wget` by including the version in the URL path (e.g. `/v1.56/containers/`), or via official client SDKs.

[Version-sensitive, Source: https://docs.docker.com/engine/api/] The current stable Engine API version at time of research is **v1.56**, corresponding to Docker Engine 29.8. [Source: https://docs.docker.com/engine/release-notes/29/] Docker Engine 29.0.0 raised the *minimum* supported API version to v1.44 (i.e. compatible with Docker Engine 25.0+ clients); versions of the API prior to v1.40 are documented as deprecated/unsupported by current Engine versions.

[Source: https://docs.docker.com/engine/api/] The API is documented as backward-compatible: "you don't need to update code that uses the API unless you need to take advantage of new features."

[Source: https://docs.docker.com/engine/api/] Official SDKs are documented for **Go** and **Python**; the Go SDK supports automatic API-version negotiation between client and daemon.

[Source: https://docs.docker.com/engine/release-notes/29/] As of Docker Engine 29.0.0, the Go module `github.com/docker/docker` is deprecated in favor of `github.com/moby/moby/client` and `github.com/moby/moby/api` — a breaking change for Go SDK consumers importing the old module path.

Not documented / could not verify in the pages fetched: specific authentication/authorization mechanisms for the Engine API beyond TLS client-certificate mutual auth (covered under Security/Configuration, not on the API reference page itself).

[Source: https://docs.docker.com/reference/] Docker also documents a **CLI reference** (all `docker` commands), a separate **Compose CLI reference** (`docker compose` subcommands), a **Dockerfile reference**, and a **BuildKit/Buildx reference** — these function as the primary "API" surface most users and tooling interact with day to day, distinct from the low-level HTTP Engine API.

---

## 4. Configuration

[Source: https://docs.docker.com/reference/cli/dockerd/] The Docker daemon is configured via a JSON file, `daemon.json` — default location `/etc/docker/daemon.json` on Linux, `%programdata%\docker\config\daemon.json` on Windows. The file must be created manually if absent, or an alternate path supplied via `dockerd --config-file`.

[Source: https://docs.docker.com/reference/cli/dockerd/] Configuration can be supplied three ways — config file, CLI flags to `dockerd`, or environment variables (e.g. `DOCKER_DRIVER`, `DOCKER_TMPDIR`) — with CLI-flag and file settings taking precedence over environment variables. Critically: **the daemon fails to start if the same option is set in both the config file and as a CLI flag**, regardless of whether the values agree.

[Source: https://docs.docker.com/reference/cli/dockerd/] Key `daemon.json` options documented include: `storage-driver` (image/container layer storage backend — `overlay2` is "the preferred storage driver for all currently supported Linux distributions, and is selected by default"), `log-driver`/`log-opts` (default logging driver and its options, default `json-file`), `log-format` (default `text`), `default-address-pools` (custom CIDR ranges for auto-created networks), and `tls`/`tlsverify`/`tlscacert`/`tlscert`/`tlskey` (daemon TLS).

[Source: https://docs.docker.com/reference/dockerfile/] Dockerfile-level configuration includes **parser directives** at the top of the file (`# syntax=`, `# escape=` for Windows path handling, `# check=` for build validation), and **build-scoped variables** via `ARG` (build-time only, not present in the final image) vs. `ENV` (persists into the built image and running container).

[Source: https://docs.docker.com/engine/network/] Networking is configured per-container at `docker run`/Compose time (`--network`, driver selection: bridge/host/none/overlay/macvlan/ipvlan) and daemon-wide for default network behavior via `daemon.json`.

[Source: https://docs.docker.com/engine/logging/configure/] Logging is configurable both daemon-wide (`daemon.json`'s `log-driver`/`log-opts`, applying only to newly created containers) and per-container (`docker run --log-driver ... --log-opt ...`), with the documented caveat that all `log-opts` values must be strings even for numeric-looking settings like `max-file`.

[Source: https://docs.docker.com/compose/] Docker Compose is configured via a YAML file (`compose.yaml`/`docker-compose.yaml`) defining services, networks, and volumes for a multi-container application as a single declarative unit, replacing the need to run multiple separate `docker` commands by hand.

---

## 5. Recommended patterns

[Source: https://docs.docker.com/build/building/best-practices/] **Multi-stage builds**: split a Dockerfile into distinct stages (e.g. build stage vs. runtime stage) so "the resulting output only contains the files that are needed to run the application," keeping build-time tooling and intermediate artifacts out of the final image.

[Source: https://docs.docker.com/build/building/best-practices/] **Minimize image size**: prefer slim/Alpine-style base images, avoid installing unnecessary packages, and clean up package-manager caches (e.g. remove `/var/lib/apt/lists` after `apt-get install`) within the same `RUN` layer that installed them.

[Source: https://docs.docker.com/build/building/best-practices/] **Pin and verify base images**: pin base image versions, and the docs recommend pinning by content digest for supply-chain integrity rather than by mutable tag alone.

[Source: https://docs.docker.com/build/building/best-practices/] **.dockerignore**: exclude irrelevant files/directories from the build context to speed up builds and avoid accidentally copying secrets or bloat into the image.

[Source: https://docs.docker.com/build/cache/] **Cache-aware instruction ordering**: because "whenever a layer changes, that layer will need to be re-built" along with every subsequent layer, the recommended pattern is to order Dockerfile instructions so frequently-changing content (e.g. `COPY . .` of application source) comes *after* rarely-changing content (e.g. dependency installation), maximizing cache reuse across rebuilds.

[Source: https://docs.docker.com/build/building/best-practices/] Build and test images automatically in CI/CD pipelines, and use `docker build --pull --no-cache` when a fully fresh, dependency-updated build is explicitly desired.

[Source: https://docs.docker.com/engine/containers/resource_constraints/] For resource-constrained production use, the documented pattern is to test an application's real memory requirements before deploying, set explicit `--memory`/`--memory-reservation` limits, and — at cluster scale — use Swarm service-level resource constraints so scheduling accounts for availability across nodes.

[Source: https://docs.docker.com/engine/storage/] For persistent application data, the documented recommendation is **volumes** ("ideal for performance-critical data processing and long-term storage needs," daemon-managed, retained after container removal); **bind mounts** are recommended specifically when a host process and a container both need direct access to the same files; **tmpfs** is recommended only for genuinely ephemeral, non-critical, or sensitive in-memory data.

[Source: https://docs.docker.com/engine/network/] For multi-container communication, the documented pattern is to place related containers on a **user-defined bridge network** so they get DNS-based name resolution, rather than relying on the default bridge network (which only supports IP-based reachability).

[Source: https://docs.docker.com/reference/build-checks/] **Build Checks** (`docker build --check`) let a Dockerfile and build configuration be validated against ~20 documented rule categories (formatting consistency, undeclared `ARG`s, secrets leaking via `ARG`/`ENV`, JSON-form `CMD`/`ENTRYPOINT`, deprecated `MAINTAINER`, relative `WORKDIR`, files excluded by `.dockerignore` being referenced, lowercase `EXPOSE` protocols, etc.) before running an actual build — described as a native, more accurate alternative to external Dockerfile linters. [Version-sensitive] Requires Buildx 0.15.0+ and Dockerfile syntax 1.8+.

---

## 6. Anti-patterns

[Inference, not confirmed in docs] Docker's official docs are written prescriptively (how to do it right) more often than as an explicitly labeled "anti-patterns" catalog; most items below are documented as things to avoid directly, but a few are the inverse of a stated recommendation rather than a page titled "anti-patterns."

[Source: https://docs.docker.com/build/building/best-practices/] Splitting `apt-get update` and `apt-get install` into **separate `RUN` instructions** is explicitly called out: doing so causes "caching issues and subsequent apt-get install instructions to fail," because Docker may reuse a stale cached `apt-get update` layer while the install layer changes, installing packages against outdated package lists.

[Source: https://docs.docker.com/build/building/best-practices/] Chaining commands through a pipe inside `RUN` **without `set -o pipefail`** is flagged: the build can "succeed and produce a new image" even if an intermediate command in the pipeline actually failed, silently masking build errors.

[Source: https://docs.docker.com/build/building/best-practices/] Frequent `USER` switching within a single Dockerfile is discouraged as it adds unnecessary layers.

[Source: https://docs.docker.com/engine/containers/resource_constraints/] Manually adjusting `--oom-score-adj` or enabling `--oom-kill-disable` **without** also setting a memory limit is explicitly warned against, as it "can destabilize the entire host" by removing Docker's normal OOM-priority safeguards.

[Source: https://docs.docker.com/engine/storage/] Bind-mounting `/var/lib/docker/` (the daemon's own data directory) into a container is documented as a pitfall — it can hold open filesystem handles that prevent container removal.

[Source: https://docs.docker.com/engine/release-notes/29/] Continued reliance on **cgroup v1** is now a documented deprecation-in-progress: as of Engine 29.0.0, cgroup v1 support is deprecated (support continues only until May 2029), signaling that new deployments should target cgroup v2 hosts.

[Source: https://docs.docker.com/docker-hub/usage/pulls/] Relying on high-frequency anonymous or free-tier authenticated pulls in automated/CI contexts is an implicit anti-pattern given documented Docker Hub pull rate limits (see Section 14) — the docs' remedy is authenticating with a paid plan or otherwise minimizing redundant pulls (e.g. image caching), not a behavior to just retry through.

---

## 7. Security

[Source: https://docs.docker.com/engine/security/] Core isolation rests on Linux **namespaces** (process/filesystem/network isolation between containers and host) and **control groups** (prevents a single container from exhausting host CPU/memory/disk-I/O and causing host-level denial of service).

[Source: https://docs.docker.com/engine/security/] The Docker **daemon runs with root privileges by default**, so daemon access must be restricted to trusted users; the docs recommend using Unix sockets over TCP where possible (TCP-socket-by-default behavior changed in Docker 0.5.2) and, when the API must be exposed over the network, securing it with HTTPS and certificates.

[Source: https://docs.docker.com/engine/security/] Docker uses a **capability allowlist** approach — unnecessary Linux capabilities are dropped by default rather than granting full root, and capabilities can be further restricted per-container (`--cap-drop`/`--cap-add`).

[Source: https://docs.docker.com/engine/security/] Additional documented hardening layers: **user namespaces** (`userns-remap`, mapping container root to an unprivileged host UID), **Docker Content Trust** (image signature verification before pull/run — but see version-sensitive note below), compatibility with kernel MAC systems (**AppArmor, SELinux, GRSEC, TOMOYO**), and **seccomp profiles** to restrict available syscalls.

[Version-sensitive, Source: https://docs.docker.com/engine/release-notes/29/] **Docker Content Trust was removed from the CLI** as of Docker Engine 29.0.0 — a breaking change for any workflow relying on `DOCKER_CONTENT_TRUST=1` / `docker trust` at the CLI level; this materially changes the security-guidance page's older content-trust recommendation for current Engine versions.

[Source: https://docs.docker.com/engine/security/rootless/] **Rootless mode** runs both the Docker daemon and containers inside a user namespace without root privileges at all (distinct from `userns-remap`, where the daemon itself still runs as root). It avoids setuid binaries except `newuidmap`/`newgidmap`, requires `/etc/subuid`/`/etc/subgid` to allocate at least 65,536 subordinate UIDs/GIDs per user, and is installed via `dockerd-rootless-setuptool.sh install` (package-based) or the `get.docker.com/rootless` script (not supported on s390x).

[Source: https://docs.docker.com/engine/security/] The overarching documented posture: "Docker containers are, by default, quite secure; especially if you run your processes as non-privileged users inside the container."

[Source: https://docs.docker.com/reference/build-checks/] Build Checks include a documented security-relevant rule preventing sensitive data from being placed in `ARG`/`ENV` instructions (since both can leak into image history/metadata).

[Source: https://docs.docker.com/scout/] **Docker Scout** analyzes an image's contents to produce a Software Bill of Materials (SBOM) and evaluate it against vulnerability advisories; per the docs, Scout stores a metadata snapshot after analysis and recalibrates against newly disclosed CVEs without needing to re-scan the image — real-time vulnerability status without repeated re-analysis. Accessible via Docker Desktop or the `docker scout` CLI subcommands (e.g. `docker scout cves`).

---

## 8. Performance

[Source: https://docs.docker.com/build/cache/] Build performance centers on **layer caching**: "each instruction in this Dockerfile translates to a layer," and rebuilding reuses unchanged layers; changing any layer invalidates it and every layer after it, regardless of whether the later layers' actual output would differ.

[Source: https://docs.docker.com/build/building/multi-platform/] **Multi-platform builds** (via Buildx/BuildKit) can be produced three documented ways: **QEMU emulation** (no Dockerfile changes needed, but "can be much slower than native builds, especially for compute-heavy tasks like compilation"), **multiple native builder nodes** (`docker buildx create --append` to combine native machines per architecture — better performance/reliability than emulation), and **cross-compilation** using the predefined `BUILDPLATFORM`/`TARGETPLATFORM` build args where the target toolchain supports it.

[Source: https://docs.docker.com/build/building/multi-platform/] Docker also documents **Docker Build Cloud** — managed, Docker-hosted multi-node builders — as an alternative to self-hosting native multi-arch builder infrastructure.

[Source: https://docs.docker.com/engine/containers/resource_constraints/] Runtime CPU performance is tunable via the CFS scheduler: `--cpus` (fractional CPU allocation), `--cpu-period`/`--cpu-quota` (lower-level equivalents), `--cpuset-cpus` (pin to specific cores), and `--cpu-shares` (soft-limit weight, default 1024, effective only under contention). By default a container has no CPU ceiling.

[Source: https://docs.docker.com/engine/containers/resource_constraints/] Memory performance/stability is tunable via `--memory` (hard cap, 6MB minimum), `--memory-reservation` (soft limit under contention), `--memory-swap` (total memory+swap; setting equal to `--memory` disables swap), and `--memory-swappiness` (0–100).

[Source: https://docs.docker.com/build/building/best-practices/] Using **bind mounts** for build-context files consumed only during a single `RUN` step (via `RUN --mount=type=bind`), rather than `COPY`, is documented as more efficient when the files don't need to persist into the final image — `COPY` remains required when the files must be present in the resulting image.

[Source: https://docs.docker.com/build/cache/] BuildKit supports **cache mounts** (`RUN --mount=type=cache`) for persisting package-manager/dependency caches across builds, and separate documentation pages cover "Optimize build cache" and "Cache storage backends" for CI-oriented remote cache export/import (`cache_to`/`cache_from` in Compose, per the Compose V2 migration content).

---

## 9. Testing

[Source: https://docs.docker.com/reference/build-checks/] **Docker Build Checks** (`docker build --check`) function as a validation/lint pass over a Dockerfile and build configuration without producing build output — described as "an advanced form of linting for your Dockerfile and build options, or a dry-run mode for builds." [Version-sensitive] Requires Buildx 0.15.0+ and Dockerfile syntax 1.8+.

[Source: https://docs.docker.com/reference/dockerfile/] The **`HEALTHCHECK`** Dockerfile instruction defines an in-container command Docker runs periodically to determine container health, surfaced via `docker ps`/`docker inspect` status and configurable via `docker run --health-cmd`/`--health-interval`/`--health-timeout`/`--health-retries`/`--health-start-period` or disabled with `--no-healthcheck`.

[Source: https://docs.docker.com/compose/] `docker compose` provides lifecycle commands (`up`, `down`, logs, exec into a running service) that support exercising a full multi-service application stack consistently "across development, staging, production, and CI" — the documented basis for using Compose as an integration-test harness for a full application.

[Source: https://docs.docker.com/testcontainers/] Docker's official docs cover **Testcontainers** — "a set of open source libraries that provides easy and lightweight APIs for bootstrapping local development and test dependencies with real services wrapped in Docker containers" — as the documented pattern for writing integration tests against real dependency containers (databases, message brokers, etc.) rather than mocks, with containers started before tests run and torn down afterward regardless of test outcome.

[Source: https://docs.docker.com/guides/testcontainers-cloud/] **Testcontainers Cloud** is documented as a companion product that runs the Testcontainers-managed containers remotely rather than on the local machine or CI runner, intended to reduce local/CI resource pressure and improve consistency of test environments.

[Source: https://docs.docker.com/build/ci/github-actions/] For build/test automation, Docker documents official **GitHub Actions**: `docker/build-push-action` (build and push via BuildKit), `docker/setup-buildx-action` (provision a BuildKit builder), `docker/login-action` (registry auth), `docker/metadata-action` (derive tags/labels from git/GitHub event metadata), and `docker/setup-qemu-action` (enable multi-platform emulated builds) — intended to be composed into a CI pipeline that builds and validates an image on every push/PR before merge.

---

## 10. Deployment

[Source: https://docs.docker.com/engine/swarm/] **Docker Swarm mode** is Docker's built-in orchestration system, letting a set of Docker Engines form a cluster ("swarm") onto which application **services** are deployed declaratively. Nodes are runtime-classified as **manager** or **worker**; a service's running containers are its **tasks**.

[Source: https://docs.docker.com/engine/swarm/] The docs explicitly distinguish current Swarm mode from **"Docker Classic Swarm, which is no longer actively developed"** — i.e., Swarm mode (built into Engine) is the maintained orchestrator; the older standalone Classic Swarm project is not.

[Source: https://docs.docker.com/engine/swarm/] For teams targeting Kubernetes specifically, Docker Desktop documents an **integrated Kubernetes** option as an alternative deployment target to Swarm; the docs frame the choice as Swarm for Swarm-native production deployments vs. Kubernetes for Kubernetes-targeted deployments, without asserting one universally supersedes the other.

[Source: https://docs.docker.com/build/ci/github-actions/] Image build-and-push as a deployment prerequisite is documented via the GitHub Actions listed in Section 9 (build-push-action, setup-buildx-action, login-action, metadata-action), forming the documented CI pipeline pattern that produces the image artifact a deployment step then pulls.

[Source: https://docs.docker.com/build/building/multi-platform/] Multi-platform image builds (Section 8) are a deployment consideration whenever target infrastructure spans architectures (e.g. amd64 servers + arm64 servers/Apple Silicon dev machines) — a single manifest-list image tag is documented as resolving to the correct architecture-specific variant automatically at pull time.

Not documented / could not verify in the pages fetched: a single canonical "how to deploy Docker Engine/containers to production" page independent of Swarm/Kubernetes-specific guidance — deployment content in the fetched docs is split across Swarm, Compose, and CI-integration pages rather than consolidated on one page.

---

## 11. Migration

[Source: https://docs.docker.com/compose/migrate/] **Docker Compose V1 → V2**: "Docker Compose v1 (`docker-compose`), a Python-based tool ... has been superseded by Compose v2 (`docker compose`), which is written in Go and integrates with the Docker CLI." Compose V1 "is no longer maintained, and users should migrate to Compose v2."

[Source: https://www.docker.com/blog/new-docker-compose-v2-and-v1-deprecation/] Per the official Docker blog: Compose V1 support ended June 2023 and V1 has since been removed from Docker Desktop; migration is primarily a matter of switching the invoked command from `docker-compose` (hyphenated, V1) to `docker compose` (space-separated subcommand, V2) — or enabling a Compose V2 compatibility symlink in Docker Desktop settings so the legacy `docker-compose` command continues to resolve to V2. The Compose *file format* is largely backward compatible (same services/volumes/networks/environment syntax); the top-level `version:` field is deprecated in V2 and should be removed. V2 added new build-related fields not present in V1: `cache_to`, `no-cache`, `pull`, `secrets` (build-time secrets), `tags`, `ssh` (V2.4.0+), and `platforms` (V2.11.0+, for multi-arch builds, requiring a `docker-container` Buildx driver).

[Inference, not confirmed in docs] Because Compose V1 and V2 generate different container/project naming, migrating a project with already-running V1-launched containers to V2 is likely to recreate those containers under new names on first `up` — this is stated as an inference since the specific claim was not independently re-verified against a primary `docs.docker.com` page in this research pass, only against blog/secondary summarization.

[Source: https://docs.docker.com/engine/security/] **Docker daemon `userns-remap` vs. Rootless mode** are documented as two distinct, non-identical migration paths toward reduced-privilege operation — they are not drop-in replacements for each other and the choice affects how the daemon itself is installed/run (see Section 7).

[Source: https://docs.docker.com/engine/daemon/alternative-runtimes/] Migrating a container's runtime away from the default `runc` is documented as either (a) a same-daemon-config runtime swap for native containerd-shim runtimes (Wasmtime, gVisor, Kata) via `docker run --runtime`, or (b) requiring explicit daemon reconfiguration for drop-in `runc`-compatible replacements (e.g. youki).

Not documented / could not verify in the pages fetched: an official "migrating from Docker Toolbox" page (Toolbox is old/pre-native-Docker-Desktop tooling for legacy Windows/macOS); this research did not confirm current-docs coverage of that specific historical migration path. Also not confirmed: a page dedicated to storage-driver migration (e.g. `aufs`/`devicemapper` → `overlay2`) beyond the `daemon.json` `storage-driver` configuration reference itself.

---

## 12. Version information

[Version-sensitive, Source: https://docs.docker.com/engine/release-notes/29/] The current Docker Engine major version series at time of research is **29.x**. The latest release found was **29.8.0, dated 2026-09-03**. Prior releases in the same series (with dates) include 29.7.2 (2026-08-05), 29.7.1 (2026-07-31), 29.7.0 (2026-07-30), 29.6.2 (2026-07-16), 29.6.1 (2026-06-26), 29.6.0 (2026-06-18), down through 29.0.0 (2025-11-10, the first 29.x release).

[Source: https://docs.docker.com/engine/release-notes/29/] The docs state: "Patch releases are always backward compatible with its major and minor version," indicating a semver-like patch/minor/major model for Engine releases, though the fetched install docs did not spell out a formal major-version support-window/EOL policy beyond that compatibility statement.

[Source: https://docs.docker.com/engine/release-notes/29/] Docker Engine ships via documented **release channels**: **stable** (general-availability releases, synced to major/minor Engine releases, "only features that are well-tested and ready for production are added") and **test** (feature-complete pre-release builds on the way to becoming the next stable release, more stable than a nightly channel but not GA).

[Version-sensitive, Source: https://github.com/docker/compose/releases (official Docker/Moby GitHub org repo)] Docker Compose's own version is independent of the Engine version number; the latest Compose release found was **v5.4.0** (dated 2026-08-03 per secondary aggregation of the official GitHub releases feed), with v5.3.0 (2026-07-02) and v5.2.0 (2026-06-23) as recent predecessors.

[Source: https://docs.docker.com/reference/build-checks/] Build Checks requires **Buildx ≥ 0.15.0** and **Dockerfile syntax ≥ 1.8** — an example of a feature whose availability is gated on the Buildx/BuildKit version and Dockerfile-syntax-directive version independently of the Docker Engine version.

[Source: https://docs.docker.com/engine/api/] The Engine **HTTP API** is versioned separately again: current is **v1.56** (paired with Engine 29.8); the minimum supported API version was raised to **v1.44** by Engine 29.0.0.

Unresolved: whether Docker publishes a formal "supported major versions" / LTS table anywhere on `docs.docker.com` analogous to, e.g., Node.js's LTS schedule — the pages fetched in this research did not surface one; only the general "patch releases are backward compatible with major.minor" statement and the release-channel (stable/test) distinction were found. If such a table exists it was not located in this pass.

---

## 13. Breaking changes

[Version-sensitive, Source: https://docs.docker.com/engine/release-notes/29/] **Docker Engine 29.0.0** (2025-11-10) is documented as introducing the following breaking/deprecating changes:
- Minimum supported Engine API version raised to **v1.44** (i.e., clients built against pre-25.0 Engine API versions are no longer supported).
- The Go module `github.com/docker/docker` is **deprecated**; consumers should migrate to `github.com/moby/moby/client` and `github.com/moby/moby/api`.
- Debian **armhf** packages now target ARMv7 specifically; **ARMv6 devices are no longer supported**.
- Official **Raspbian 32-bit packages discontinued**.
- **cgroup v1 is deprecated** (support continues until May 2029, per the release notes).
- **Docker Content Trust removed from the CLI.**
- Legacy container **`--link` environment-variable injection support deprecated**.
- `docker commit --pause` **deprecated** in favor of `--no-pause`.
- The **containerd image store became the default** for fresh installations (a behavioral default change, not just a deprecation).
- Experimental **nftables** firewall support introduced (opt-in, not default, but a notable new capability alongside the above breaking items).

[Version-sensitive, Source: https://docs.docker.com/engine/release-notes/29/] Later 29.x releases added further notable (non-breaking, additive) changes worth tracking for version-awareness: 29.2.0 added experimental **NRI** (Node Resource Interface) support; 29.5.0 added a rootless-mode **gvisor-tap-vsock** default network driver and enabled a private time namespace by default for rootless containers; 29.7.0 made the **`image` mount type** non-experimental and added an experimental embedded-containerd feature; 29.8.0 added a `HostConfig.Umask` container option and expanded CloudWatch logging-driver capabilities.

[Source: https://www.docker.com/blog/new-docker-compose-v2-and-v1-deprecation/] **Compose V1 → V2** (see Section 11) is itself the largest documented Compose-level breaking change: a full rewrite (Python → Go), CLI invocation change (`docker-compose` → `docker compose`), and file-format field changes (`version:` key deprecated).

Unresolved: whether there is a single consolidated "breaking changes across major versions" page for Docker Engine (analogous to a dedicated migration guide) versus breaking changes being documented only inline within each version's release notes — this research found breaking changes listed inline in `engine/release-notes/29/` rather than on a separate dedicated breaking-changes page, so older major-version transitions (e.g. 24→25, 25→26, etc.) were not independently verified in this pass.

---

## 14. Limitations

[Source: https://docs.docker.com/docker-hub/usage/pulls/] **Docker Hub pull rate limits** are explicitly documented: unauthenticated pulls are limited to **100 per 6-hour window per IPv4 address or IPv6 /64 subnet**; authenticated **Docker Personal (free)** accounts get **200 pulls per 6 hours**; **Docker Pro, Team, and Business** subscriptions have **no pull rate limit**. A pull against a multi-arch image manifest counts once per architecture pulled. Limit status is exposed via `ratelimit-limit`/`ratelimit-remaining`/`docker-ratelimit-source` response headers; exceeding the limit returns HTTP 429.

[Source: https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/known-issues/] **Apple Silicon emulation limitations**: images without native ARM64 support can be run under QEMU emulation via `--platform linux/amd64`, but this is documented as "best effort" only — QEMU can crash unexpectedly on certain containers, **inotify-based filesystem change notifications do not work under QEMU emulation**, and even successfully emulated containers run slower and use more memory than native equivalents.

[Source: https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/known-issues/] Docker Desktop's macOS **HyperKit** hypervisor conflicts with other hypervisor-dependent tools (e.g. Intel HAXM); running both concurrently is unsupported.

[Source: https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/known-issues/] On Intel Macs, macOS **Activity Monitor over-reports Docker's memory usage** by roughly double the actual consumption due to a documented macOS-level bug, not a Docker defect.

[Source: https://docs.docker.com/security/for-admins/hardened-desktop/enhanced-container-isolation/limitations/] **Enhanced Container Isolation (ECI)** on the WSL2 backend has a documented hard requirement: WSL **≥ 2.6** and a Linux kernel **≥ 6.3.0**, because ECI depends on kernel features at that minimum version.

[Source: https://docs.docker.com/engine/containers/resource_constraints/] The **minimum allowed `--memory` limit is 6MB**; attempting a lower hard memory cap is not supported.

[Source: https://docs.docker.com/subscription/desktop-license/] **Docker Desktop licensing is a documented product limitation, not a technical one**: free use of Docker Desktop is restricted to personal use, education, non-commercial open-source projects, and organizations under 250 employees **and** under $10M annual revenue; larger/commercial organizations require a paid Docker Pro/Team/Business subscription. This limitation applies to the **Docker Desktop application specifically** — the docs are explicit that "the licensing and distribution terms for Docker and Moby open-source projects, such as Docker Engine, aren't changing," i.e. Docker Engine itself (e.g. run directly on a Linux server) is not subject to this licensing restriction.

[Source: https://docs.docker.com/engine/daemon/alternative-runtimes/] Drop-in `runc`-alternative runtimes (e.g. youki) explicitly require manual daemon registration/configuration and are not selectable purely via `docker run --runtime` the way native containerd-shim runtimes (Wasmtime, gVisor, Kata) are — a documented capability gap between the two runtime-integration approaches.

---

## 15. Debugging

[Source: https://docs.docker.com/engine/daemon/logs/] Daemon debug logging is enabled via `daemon.json`'s `debug: true` key (the documented recommended approach, working across all Docker platforms) or via a `dockerd` CLI flag; the default log level is `info`, with possible values `debug`, `info`, `warn`, `error`, `fatal`.

[Source: https://docs.docker.com/engine/daemon/troubleshoot/] A **full stack trace of all daemon threads** can be forced into the daemon log by sending the daemon process a `SIGUSR` signal — documented specifically as a low-level daemon-hang debugging technique.

[Source: https://docs.docker.com/engine/daemon/troubleshoot/] Documented common troubleshooting scenarios include: "Cannot connect to the Docker daemon" errors (check the daemon is running via `docker info`, check the `DOCKER_HOST` environment variable, check network connectivity for remote hosts); conflicting `daemon.json` vs. systemd-unit startup flags (a documented pitfall specifically on Debian/Ubuntu when a custom daemon host address is set in both places); kernel-version requirements (**kernel ≥ 3.10** required, verifiable via the documented `check-config.sh` script); and networking conflicts with `systemd-networkd`/`NetworkManager`/`dnsmasq` DNS caching.

[Source: https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/] On macOS and Windows (WSL2), Docker Desktop writes daemon logs (`dockerd`, `containerd`, and other VM-internal services) into a **single multiplexed `init.log` file in JSON format**, with each line tagged with a `component` field identifying which service emitted it — a Desktop-specific debugging detail distinct from native-Linux daemon logging.

[Source: https://docs.docker.com/reference/cli/docker/container/run/] Container-level debugging flags documented on `docker run` include `--pid=host` (share the host PID namespace, enabling host tools like `strace`/`gdb` to see container processes), `--pid=container:<name>` (join another container's PID namespace to debug it from outside), `--cap-add SYS_PTRACE` (grant the ptrace capability needed by debuggers), and `--security-opt seccomp=unconfined` (remove seccomp syscall filtering, another common debugging-only relaxation).

[Source: https://docs.docker.com/reference/build-checks/] `docker build --check` doubles as a pre-flight debugging tool for Dockerfile/build-configuration problems, surfacing issues before a real build is attempted (see Sections 5 and 9).

[Source: https://docs.docker.com/reference/cli/docker/container/run/] `--health-cmd` and related `--health-*` flags (Section 9) provide a documented mechanism for surfacing in-container application-health problems through `docker ps`/`docker inspect` rather than requiring a separate external check.

---

## 16. Integration

[Source: https://docs.docker.com/build/ci/github-actions/] **GitHub Actions** integration is officially documented and maintained via first-party actions: `docker/build-push-action`, `docker/setup-buildx-action`, `docker/login-action`, `docker/metadata-action`, `docker/setup-qemu-action`, plus Buildx **Bake** support for complex multi-target build configurations.

[Source: https://docs.docker.com/compose/] **Docker Compose** integrates directly with the Docker CLI (`docker compose` is now a CLI subcommand, not a separate binary, as of V2) and is documented as usable consistently "across development, staging, production, and CI" environments.

[Source: https://docs.docker.com/engine/swarm/] **Kubernetes** integration is documented at the Docker Desktop level: an integrated single-node Kubernetes cluster is offered as an alternative orchestration target to Swarm, for teams building toward Kubernetes-based production deployments.

[Source: https://docs.docker.com/engine/daemon/alternative-runtimes/] **Alternative container runtimes** integrate at the containerd-shim layer: **Wasmtime** (WebAssembly workloads), **gVisor** (sandboxed isolation), and **Kata Containers** (VM-level isolation) are documented as usable via `docker run --runtime` without further daemon reconfiguration, since they implement the containerd shim API natively.

[Source: https://docs.docker.com/testcontainers/] **Testcontainers** (and **Testcontainers Cloud**) is documented as Docker's officially covered integration path for language-level integration testing against real containerized dependencies, spanning multiple language ecosystems (the docs reference per-language getting-started guides, e.g. .NET).

[Source: https://docs.docker.com/scout/] **Docker Scout** integrates with Docker Hub repositories (automatic image analysis once enabled) and with the `docker scout` CLI subcommands for local/CI-driven vulnerability and SBOM analysis, plus documented integration with Docker Hardened Images scanning.

[Source: https://docs.docker.com/engine/security/] Integration with host **Linux Security Modules** (AppArmor, SELinux) and mandatory access control frameworks (GRSEC, TOMOYO) is documented as compatible/supported alongside Docker's own namespace/cgroup/capability isolation, i.e. Docker layers on top of rather than replaces these host-level security systems.

[Source: https://docs.docker.com/engine/logging/configure/] **External log aggregation systems** integrate via documented logging drivers: `syslog`, `journald`, `gelf` (Graylog/Logstash), `fluentd`, `awslogs` (CloudWatch), `splunk`, `gcplogs`, and Windows `etwlogs`, configurable daemon-wide or per-container.

---

## 17. Production considerations

[Source: https://docs.docker.com/engine/logging/configure/] The documented default logging driver, `json-file`, is explicitly **not** the documentation's own production recommendation — Docker recommends the **`local`** driver for production because it "performs log-rotation by default, and uses a more efficient file format," explicitly framed as preventing **disk exhaustion**. For `json-file`, rotation must be configured manually via `max-size`/`max-file` log-opts; without that, log files can grow unbounded.

[Source: https://docs.docker.com/engine/containers/resource_constraints/] Production memory-safety guidance: set explicit `--memory` limits after testing real application memory needs, ensure hosts have adequate headroom, and understand that Docker deliberately lowers its own daemon's OOM-kill priority relative to containers so that, under host memory pressure, **containers are more likely to be OOM-killed than the Docker daemon itself** — manually disabling this behavior without limits is explicitly discouraged (Section 6).

[Source: https://docs.docker.com/engine/storage/] For production data persistence, **volumes** are the documented recommended mechanism (daemon-managed lifecycle, host-level file performance, survive container removal); the docs explicitly caution that **direct host-filesystem access to volume internals is unsupported** — volumes should be accessed through the Docker API/CLI or by mounting them into a container, not by reaching into the daemon's storage directory.

[Source: https://docs.docker.com/engine/swarm/] For multi-node production orchestration without adopting Kubernetes, **Swarm mode** is the documented built-in option — services, declarative desired state, and manager/worker node roles — while Kubernetes is documented as Docker Desktop's integrated alternative for teams already targeting Kubernetes in production.

[Source: https://docs.docker.com/docker-hub/usage/pulls/] Production CI/CD and fleet-scale pull volume should account for **Docker Hub's pull rate limits** (Section 14) — unlimited only for paid Pro/Team/Business accounts — since exceeding the limit returns HTTP 429 and can break automated deployment pipelines that pull frequently.

[Source: https://docs.docker.com/scout/] Docker's documented supply-chain-security production practice is continuous **Docker Scout** analysis of production images for newly disclosed CVEs, using its snapshot-based recalibration so images don't need re-scanning from scratch as new vulnerability data is published.

[Source: https://docs.docker.com/engine/security/rootless/] For hosts where daemon-level root privilege is a production security concern, **Rootless mode** is the documented mitigation, at the cost of the documented prerequisite/setup overhead (subordinate UID/GID ranges, `newuidmap`/`newgidmap`) and behavioral differences from standard root-daemon operation (e.g. the default rootless network driver changed to `gvisor-tap-vsock` as of Engine 29.5.0 — see Section 13).

[Source: https://docs.docker.com/subscription/desktop-license/] For organizations evaluating "production Docker," it's a documented and easily-conflated distinction that **Docker Desktop licensing terms do not apply to Docker Engine running on production servers** — only to the Desktop application typically used on developer workstations; production Engine deployments on Linux servers remain governed by the open-source Docker/Moby licensing, not the Desktop Subscription Service Agreement.

---
