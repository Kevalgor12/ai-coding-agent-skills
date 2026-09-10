---
name: Go
description: >-
  Go-specific concurrency (goroutines/channels), explicit multi-value error
  returns, the module system (go.mod/go.sum/go.work), generics (since Go
  1.18), GOMEMLIMIT/PGO performance tuning, and standard-library testing
  (go test, benchmarks, fuzzing). Use when the stack is Go (go.mod present,
  .go files, or the task names Go/goroutines/channels). Not for Node.js or
  Python backends (use those skills), or generic service structuring (use
  backend-architecture).
spec_version: "1.0"
---

## Purpose & scope

Apply Go correctly for the version in use — goroutine/channel concurrency,
explicit multi-value error handling, the module system, generics, and
version-gated toolchain/runtime behavior. The *method* for structuring the
service itself (layering, middleware, DI, graceful shutdown) comes from the
parent skill ([backend-architecture](../backend-architecture/SKILL.md));
this skill supplies Go's concrete facts on top of that method.

## When to use / When not to use

**Use** when a `go.mod` file or `.go` source files are present, or the task
names Go, goroutines, channels, or a Go-specific tool (`go test`, `go build`,
`go mod`, `govulncheck`). **Do not use** when the stack is Node.js or Python
(route to that runtime's skill), for generic backend layering/DI decisions
with no runtime chosen yet
([backend-architecture](../backend-architecture/SKILL.md)), or for
database-specific SQL/schema design unrelated to Go's `database/sql` usage.

## Knowledge

**Concurrency primitives.** Goroutines (`go` statement) and channels (typed
conduits via `make(chan T)`, optionally buffered, directional types
`chan<-`/`<-chan`, closed via `close`) are first-class language constructs,
not a library [Source: https://go.dev/ref/spec]. `select` multiplexes over
multiple channel send/receive operations [Source: https://go.dev/ref/spec].
The runtime scheduler multiplexes goroutines M:N onto OS threads, moving a
blocked coroutine's OS thread over to run others so they aren't blocked
alongside it; goroutines start with a small, resizable stack, making
hundreds of thousands of concurrent goroutines practical
[Source: https://go.dev/doc/faq]. `GOMAXPROCS` bounds how many goroutines
execute truly simultaneously, defaulting to the number of available CPU
cores [Source: https://go.dev/doc/faq]. The documented design philosophy:
"Do not communicate by sharing memory; instead, share memory by
communicating" [Source: https://go.dev/doc/effective_go].

**Explicit error handling.** Errors are a built-in `error` interface
(`Error() string`); functions conventionally return `(result, error)` pairs
instead of throwing exceptions, with the idiom of checking `err != nil`
immediately and returning early rather than deep-nesting the success path
[Source: https://go.dev/doc/faq; https://go.dev/doc/effective_go].
`assert`-style constructs are deliberately absent from the language — the
FAQ states programmers use them "as a crutch to avoid thinking about proper
error handling and reporting," so ordinary/recoverable failures must be
returned and handled as `error` values, not asserted or panicked on
[Source: https://go.dev/doc/faq]. Documented gotcha: a `nil` concrete-pointer
value returned through an `error`-typed (or any interface-typed) return
produces a *non-nil* interface value — return the literal `nil`, not a
typed nil pointer [Source: https://go.dev/doc/faq].

**Module system.** `go.mod` directives: `module`, `go` (minimum language
version), `toolchain`, `require`, `replace`, `exclude`, `retract`, `tool`,
`ignore`, `godebug` [Source: https://go.dev/doc/modules/gomod-ref].
Dependency resolution uses Minimal Version Selection (MVS) — for every
module in the build, the *minimum* version that still satisfies every
`require` constraint in the graph, not simply the latest available
[Source: https://go.dev/ref/mod]. `go.sum` records cryptographic hashes of
module content for reproducible, tamper-evident builds, generated/updated
automatically by module-aware commands [Source: https://go.dev/ref/mod].
Multi-module local development uses a `go.work` file (normally left
uncommitted) with `use`/`replace` entries [Source: https://go.dev/ref/mod].
**Version-sensitive:** module-aware mode has been the default since Go
1.16; explicit `require` directives for transitive dependencies (with
module-graph pruning for `go 1.17+` deps) since Go 1.17; the `go` directive
became mandatory and enforced as of Go 1.21+, meaning a toolchain refuses to
build a module declaring a newer Go version than it implements
[Source: https://go.dev/doc/modules/gomod-ref; research/knowledge-maps/version-matrix.md]
(applies_to: >=1.16 / >=1.17 / >=1.21).

**Generics.** Type parameters on types and functions, with general
interfaces usable as constraints, were introduced in Go 1.18
[Source: https://go.dev/ref/spec] (applies_to: >=1.18). Self-referential
generic type declarations — a generic type referring to itself in its own
type-parameter list, previously disallowed — became legal in Go 1.26
[Source: https://go.dev/doc/go1.26] (applies_to: >=1.26). Methods may
declare their own type parameters ("generic methods") as of Go 1.27, though
interface methods still cannot declare type parameters
[Source: https://go.dev/doc/go1.27] (applies_to: >=1.27). Note: this
directly reverses a set of implementation obstacles the FAQ documents as
reasons methods couldn't have type parameters; whether the FAQ page has
since been updated to reconcile this was not directly confirmed — Unresolved
[Source: https://go.dev/doc/faq; https://go.dev/doc/go1.27].

## Decision framework

1. **Simplest concurrency first (anti-overengineering):** a single async
   operation or a handful of independent calls needs nothing more than
   plain goroutines with a `sync.WaitGroup` — don't reach for channels or a
   worker pool for something that small.
2. **Goroutines + channels vs. a bounded worker pool:** unbounded fan-out
   (spawning one goroutine per incoming item with no cap) risks unbounded
   goroutine growth against a slow downstream dependency, or leaked
   goroutines blocked on a channel nobody drains — common enough that Go
   1.27 added a dedicated goroutine-leak pprof profile to detect goroutines
   blocked and unreachable from any runnable goroutine
   [Source: https://go.dev/doc/go1.27]. Reach for a bounded worker pool
   (a fixed number of goroutines reading from one input channel) when work
   arrives faster than it can be safely processed, each unit of work holds
   a scarce resource (DB connection, file handle), or backpressure needs to
   be explicit. Prefer raw per-request goroutines + channels when
   concurrency is naturally bounded by the request itself (e.g. fanning out
   N sub-queries per incoming request and waiting for all N).
3. **Channels vs. a mutex for shared state:** default to channels for
   handing off ownership of data or signaling completion, per the
   documented "share memory by communicating" philosophy
   [Source: https://go.dev/doc/effective_go]. Reach for `sync.Mutex`/
   `sync.RWMutex` (or `sync.Map` for concurrent map access — plain maps are
   unsafe for concurrent writes by design [Source: https://go.dev/doc/faq])
   when the shared state is a simple counter/cache and channel indirection
   would add ceremony without a real coordination benefit.
4. **Is FIPS 140-3 mode actually required, or just available?** Enable the
   Go Cryptographic Module's FIPS mode (`GOFIPS140` at build time,
   `GODEBUG=fips140=on` at runtime) [Source: https://go.dev/doc/security/fips140]
   only when a real regulatory/contractual requirement names FIPS 140-3. It
   restricts `crypto/tls` to an approved protocol/cipher subset and is
   unsupported on OpenBSD, Wasm, AIX, and 32-bit Windows
   [Source: https://go.dev/doc/security/fips140], so enabling it
   speculatively can silently break a TLS configuration or a target
   platform. For services with no such mandate, standard `crypto/tls`
   defaults are the right choice — FIPS mode is a compliance constraint,
   not a general hardening upgrade.
5. **Version gate:** confirm the Go version (`go.mod`'s `go` directive, or
   `go version`) before recommending a version-gated feature (generics
   detail, `GOMEMLIMIT`, PGO default-on behavior) — state the version the
   guidance targets.

## Workflow

1. Determine the Go version/toolchain in use before proposing a
   version-gated feature.
2. Design the concurrency shape from the actual need (decision framework
   above) — single goroutines+`WaitGroup`, channel-coordinated fan-out, or a
   bounded worker pool.
3. Handle every returned error at the call site — check `err != nil` and
   return early; don't defer or swallow it [Source: https://go.dev/doc/effective_go].
4. For module/dependency changes, edit `go.mod` and run `go mod tidy`; let
   `go.sum` regenerate automatically rather than hand-editing it
   [Source: https://go.dev/ref/mod].
5. Write or update `_test.go` files alongside the change (see Testing) and
   run `go test -race` for anything touching goroutines/shared state
   [Source: https://go.dev/doc/articles/race_detector.html].
6. For a production-performance task, follow the PGO loop: ship an initial
   binary, collect a CPU profile, commit `default.pgo`, redeploy, re-profile
   [Source: https://go.dev/doc/pgo].
7. Verify (below) before declaring done.

## Engineering rules

- Check every returned error; a deliberately-discarded error (`_`) should
  be rare and justified, not the default [Source: https://go.dev/doc/effective_go].
- Give every spawned goroutine an explicit termination path (channel close,
  `context` cancellation, or `WaitGroup`) — don't start one with no way to
  know it finished or to stop it.
- Don't mutate a shared map from multiple goroutines without
  synchronization (`sync.Mutex` or `sync.Map`) — plain maps are unsafe for
  concurrent writes by design [Source: https://go.dev/doc/faq].
- Run all code through `gofmt`; don't hand-format
  [Source: https://go.dev/doc/effective_go].
- Parameterize all `database/sql` queries; never build SQL via
  `fmt.Sprintf`/string concatenation
  [Source: https://go.dev/doc/database/sql-injection].
- Keep interfaces small and defined near their consumer, not bundled with
  the implementation [Source: https://go.dev/doc/effective_go].
- Never assume "latest" Go behavior implicitly — state the version the
  guidance targets, given the ~6-month release cadence and rolling
  two-major support window [Source: https://go.dev/doc/devel/release].

## Trade-offs

Channels buy safe hand-off of ownership and composable coordination
(`select`) at the cost of more ceremony than a mutex for simple shared
counters/caches — not every piece of shared state needs channel indirection.
A bounded worker pool buys predictable resource usage and backpressure at
the cost of tuning a pool size and added structure, versus unbounded
per-item goroutines, which are simpler but riskier under load. FIPS 140-3
mode buys regulatory compliance at the cost of a narrower approved
`crypto/tls` protocol/cipher set and loss of support on some platforms
(OpenBSD, Wasm, AIX, 32-bit Windows) [Source: https://go.dev/doc/security/fips140]
— a real cost when it isn't actually mandated.

## Anti-patterns

- **Goroutine leaks** — spawning a goroutine that blocks forever (e.g.
  writing to a channel nobody drains) with no cancellation path; common
  enough that Go 1.27 added a dedicated goroutine-leak pprof profile
  [Source: https://go.dev/doc/go1.27].
- **Ignoring returned errors** (assigning to `_` as a habit, or not
  checking `err != nil` at all) instead of handling them at the call site
  [Source: https://go.dev/doc/effective_go].
- **Using `panic`/`recover` or `assert`-style helpers for ordinary,
  recoverable failures** instead of returning `error` — the FAQ explicitly
  frames `assert`-style constructs as a way to avoid proper error handling
  [Source: https://go.dev/doc/faq].
- **Concurrent unsynchronized map writes** — maps have no built-in locking;
  this is a data race, not a supported pattern [Source: https://go.dev/doc/faq].
- **Building a worker-pool/abstraction framework "for future scale" before
  a single concurrency need actually demands bounded parallelism** — the
  domain's over-engineering trap; plain goroutines+`WaitGroup` or a channel
  fan-out is usually enough until a real backpressure/resource-limit
  problem appears.
- **Enabling FIPS 140-3 mode speculatively** without a stated regulatory
  requirement, then being surprised `crypto/tls` rejects a previously
  working cipher/protocol, or that it's unsupported on the deploy target
  [Source: https://go.dev/doc/security/fips140].
- **Building SQL via string concatenation/`fmt.Sprintf`** with untrusted
  input [Source: https://go.dev/doc/database/sql-injection].

## Security

Always pass `database/sql` query parameters as separate arguments
(placeholder syntax is driver-dependent — `?` for many drivers, `$1`/`$2`
for PostgreSQL drivers like `lib/pq`) rather than building queries via
`fmt.Sprintf`/concatenation — Go's official documented SQL-injection
defense [Source: https://go.dev/doc/database/sql-injection]. Run
`govulncheck` against the codebase's dependencies; it reports only
vulnerabilities in functions actually reachable from the analyzed code,
reducing noise versus flagging every vulnerable transitive dependency
[Source: https://go.dev/security/]. **FIPS 140-3 mode** (Go 1.24+, applies_to
>=1.24): the Go Cryptographic Module supports a FIPS 140-3-oriented mode —
build-time via `GOFIPS140=latest|certified|<version>`, runtime via
`GODEBUG=fips140=on` (`fips140=only` is explicitly documented as
testing-only, not for production); in this mode `crypto/tls` is restricted
to FIPS-approved protocols/ciphers and startup runs self-tests plus NIST SP
800-90A DRBG-based random generation. **Unsupported on OpenBSD, Wasm, AIX,
and 32-bit Windows** [Source: https://go.dev/doc/security/fips140]. Go 1.27
(applies_to >=1.27) removed several previously-deprecated unsafe TLS
`GODEBUG` opt-outs (`tlsunsafeekm`, `tlsrsakex`, `tls3des`, `tls10server`,
`x509keypairleaf`) entirely — those insecure fallbacks no longer exist as of
1.27 [Source: https://go.dev/doc/go1.27]. Deep cross-cutting threat modeling
(secrets, transport, authn/authz) is owned by `SK-QA-002`, not restated
here (QR-2).

## Performance

`GOGC` (default 100) trades memory for GC CPU cost; `GOMEMLIMIT`
(introduced Go 1.19, applies_to: >=1.19) sets a soft memory cap, settable
via `runtime/debug.SetMemoryLimit` — use it only when the Go process is the
sole memory tenant of its environment (e.g. a dedicated container) with
5–10% headroom, since misconfiguring it in a shared/uncontrolled
environment can cause GC thrashing worse than an OOM
[Source: https://go.dev/doc/gc-guide]. **PGO (Profile-Guided Optimization):**
capture a production CPU pprof profile, save it as `default.pgo` in the
main package directory — `go build` auto-detects it. Version-sensitive: PGO
required explicit opt-in before Go 1.21; from 1.21 onward it's
auto-detected/on by default whenever `default.pgo` is present (`-pgo=off`
disables it) [Source: https://go.dev/doc/pgo] (applies_to: <1.21 opt-in,
>=1.21 default), reported to yield roughly 2–14% improvement across
representative programs as of Go 1.22 [Source: https://go.dev/doc/pgo]. Go
1.26's default "Green Tea" garbage collector reduces GC overhead by 10–40%
[Source: https://go.dev/doc/go1.26] (applies_to: >=1.26). Escape-analysis
output (`go build -gcflags=-m=3`) finds values unexpectedly escaping to the
heap [Source: https://go.dev/doc/gc-guide]. Deep cross-cutting performance
method is owned by `SK-QA-003`.

## Testing

Go ships official first-party testing tooling in the standard library — a
real contrast to gaps found elsewhere in this project (e.g. Express has no
official app-testing guide, per
[backend-architecture](../backend-architecture/SKILL.md#testing)). Tests
live in `_test.go` files as `func TestXxx(t *testing.T)`; table-driven
tests with `t.Run` subtests (producing `/`-separated names, selectable via
`-run`) are the documented idiom
[Source: https://go.dev/doc/effective_go; https://pkg.go.dev/testing].
Useful `*testing.T` methods: `t.Helper()`, `t.Cleanup(f)`, `t.TempDir()`,
`t.Setenv`/`t.Chdir` (auto-restoring), `t.Context()`, `t.Parallel()`
[Source: https://pkg.go.dev/testing]. Benchmarks (`func BenchmarkXxx(b
*testing.B)`) use the modern `for b.Loop() {...}` style (auto-managed
timer) or the legacy `for i := 0; i < b.N; i++`; `-benchmem` reports
allocations [Source: https://pkg.go.dev/testing]. Native fuzz testing
(`func FuzzXxx(f *testing.F)`, seeded via `f.Add`, run via `go test
-fuzz=<Name>`) has been part of the standard toolchain since Go 1.18 and is
also exercised continuously via OSS-Fuzz [Source: https://go.dev/security/]
(applies_to: >=1.18). The data race detector (`-race` on `go test`/`go
run`/`go build`) catches concurrent unsynchronized access but only on
exercised code paths, at a documented ~5–10x memory / ~2–20x
execution-time cost — treat it as a CI/test-time tool, not something to
ship to production [Source: https://go.dev/doc/articles/race_detector.html].
Deep cross-cutting test-strategy method is owned by `SK-QA-001`.

## Failure handling

- If the Go version/toolchain in use cannot be determined, ask for it or
  state the version the guidance assumes — never assume "latest" silently,
  given the ~6-month release cadence and rolling two-major support window.
- If shell is unavailable/denied, degrade to advisory code/module-change
  output and state that `go build`/`go test`/`govulncheck` were not run.
- If a claim would require FIPS mode on a platform the research already
  documents as unsupported (OpenBSD, Wasm, AIX, 32-bit Windows), say so
  rather than assert it works there.

## Escalation

- Adopting FIPS 140-3 mode for a service is a compliance-scoped,
  hard-to-reverse decision (narrows `crypto/tls` protocol/cipher support
  and drops platform support) — present with trade-offs for explicit
  confirmation, never enabled unilaterally.
- Changing a module's major-version import path (e.g. appending `/v2`)
  breaks every consumer's import path; Go's module system does not
  auto-migrate v1 imports to v2 [Source: https://go.dev/doc/modules/major-version]
  — requires explicit confirmation and a stated support policy for the old
  major version.

## Outputs & verification

- **Outputs:** Go source or `go.mod`/`go.sum`/`go.work` changes, a
  concurrency/error-handling design, or analysis (concurrency approach,
  FIPS-mode applicability, performance tuning) with rationale and the
  version it applies to.
- **Verify:** every returned error is checked or deliberately/justifiably
  discarded; every spawned goroutine has a termination path; any
  version-specific claim is tagged with its range and confirmed against the
  repo's actual Go version.

## References

- Source list: see `skill.yaml.source_references` (Go official docs at
  go.dev / pkg.go.dev, retrieved 2026-09-10, via
  `research/technologies/go.md` and
  `research/knowledge-maps/version-matrix.md`).

**Unresolved (carried from research, do not paper over):**
- Whether the FAQ page's stated rationale against generic methods (four
  documented implementation obstacles) has been updated to reconcile with
  Go 1.27's introduction of generic methods was not directly confirmed
  [Source: https://go.dev/doc/faq; https://go.dev/doc/go1.27].
- The exact Go version `runtime/secret` first shipped in, and its
  stability roadmap, was not independently confirmed beyond its appearance
  as "experimental" in the Go 1.26 release notes
  [Source: https://go.dev/doc/security/fips140].
- Go 1.27.1's reported release date (2026-09-01) was only surfaced via a
  search-engine summary, not a direct fetch of the release page — lower
  confidence than the directly-fetched 1.25.0/1.26.0/1.27.0 dates
  [Source: https://go.dev/doc/devel/release].
- Whether go.dev hosts an updated, modules-era canonical Docker/container
  deployment guide (the official blog post found predates Go modules) was
  not confirmed [Source: https://go.dev/blog/docker].
