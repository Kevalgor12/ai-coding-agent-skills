---
name: Node.js
description: >-
  Node.js runtime specifics: CommonJS vs ESM, the event loop and libuv thread
  pool, worker_threads/child_process/cluster, the Permission Model, node:test,
  and release-line/version policy (including the v27 annual-release change).
  Use when the stack runs on Node.js and the question is runtime-level (module
  system, concurrency primitive, sandboxing, version support). Not for
  Express/Fastify framework specifics, generic backend structure (use
  backend-architecture), or other runtimes (Go, Python).
spec_version: "1.0"
---

## Purpose & scope

Apply Node.js correctly for the release line in use — its module system,
event-loop/concurrency model, Permission Model, and version/release policy.
The generic backend-structure method (layering, middleware, DI, centralized
error handling, graceful shutdown, and the Node-vs-Go-vs-Python choice) comes
from the parent skill, [backend-architecture](../backend-architecture/SKILL.md)
(`SK-BE-001`); this skill supplies the Node.js runtime specifics underneath
it. Framework-level behavior belongs to the forthcoming `SK-TECH-express` and
`SK-TECH-fastify` skills, not here.

## When to use / When not to use

**Use** when the project targets Node.js and the question is runtime-level:
CommonJS vs ESM, `worker_threads` vs `child_process` vs `cluster`, adopting
the Permission Model, a version/upgrade/EOL/security-release question, or a
suspected event-loop-blocking/CPU/memory issue in a Node.js process. **Do
not use** for Go/Python runtimes (route to that skill), Express/Fastify
routing and middleware specifics with the runtime itself not in question
(route to `SK-TECH-express`/`SK-TECH-fastify`), or generic backend layering/
error-handling/shutdown design with no Node-specific mechanism involved
(route to `SK-BE-001`).

## Knowledge

**Event loop.** Node.js runs JavaScript single-threaded but performs
non-blocking I/O by offloading to the OS kernel or to libuv's worker thread
pool [Source: https://nodejs.org/en/learn/getting-started/introduction-to-nodejs].
Each iteration cycles six phases in order: **timers** → **pending callbacks**
→ **idle/prepare** (internal) → **poll** (I/O events; the loop blocks here
when appropriate) → **check** (`setImmediate()`) → **close callbacks**
[Source: https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick].
Timer thresholds are minimums, not guarantees — a long poll-phase callback can
push a due timer later. `process.nextTick()` is *not* part of the phase
cycle: its queue drains after the current operation, before the loop
advances, regardless of phase, and unbounded recursive use can starve I/O by
never letting the loop reach poll. `setImmediate()` scheduled inside an I/O
callback always runs before a `setTimeout(fn, 0)` scheduled in the same
callback [Source: https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick].

**libuv thread pool.** File-system ops, DNS `getaddrinfo`/`getnameinfo`, and
worker-pool-offloaded crypto/zlib calls run on libuv's thread pool, default
size 4, tunable via `UV_THREADPOOL_SIZE` up to 1024 (raised from a prior
128-thread ceiling in libuv 1.30.0); it is one pool shared globally across a
process and its functions are not thread-safe [Source:
https://docs.libuv.org/en/v1.x/threadpool.html].

**CommonJS vs ESM.** `package.json`'s `"type"` field selects `"commonjs"`
(default) or `"module"`; `.mjs` is always ESM, `.cjs` always CommonJS
regardless of `"type"` [Source: https://nodejs.org/api/packages.html]. With no
explicit marker, Node.js falls back to inspecting source text for ESM syntax
[Source: https://nodejs.org/api/esm.html]. Interop: ESM can `import`
CommonJS (default export = `module.exports`, named exports via static
analysis, added v14.13.0/v12.20.0); CommonJS `require()` can synchronously
load an ESM graph (a Node.js 22 headline addition); dynamic `import()` works
from both. ESM lacks CommonJS globals (`require`, `__dirname`) — use
`import.meta.filename`/`import.meta.dirname` (stable since v24.0.0) or
`module.createRequire()` [Source: https://nodejs.org/api/esm.html].

**Concurrency primitives are not interchangeable.** `worker_threads` runs JS
on additional OS threads that can share memory via `SharedArrayBuffer`;
Node's own docs are explicit that they help CPU-intensive work and "do not
help much with I/O-intensive work," since native async I/O is already more
efficient [Source: https://nodejs.org/api/worker_threads.html].
`child_process`/`cluster` fork separate OS *processes*; `cluster` (Stability
2, Stable) shares listening ports across forked workers coordinated by a
primary, and on non-Windows platforms defaults to round-robin distribution —
the alternative direct-socket-handoff mode is documented as producing
"unbalanced" real-world distribution (observed: >70% of connections on 2 of 8
workers) [Source: https://nodejs.org/api/cluster.html]. `cluster` provides no
routing/session-affinity or automatic pool sizing; that's the application's
job.

**Release-line policy is changing.** At any moment there are up to three
supported lines — Current, Active LTS, Maintenance LTS — never a Go-style
"N and N-1" window [Source: https://raw.githubusercontent.com/nodejs/Release/main/README.md].
As of this research (2026-09-10): **Current is v26.8.2**; **Active LTS is
v24.21.0 "Krypton"**; **Maintenance LTS is v22.x "Jod"** [Source:
https://nodejs.org/en/download, https://raw.githubusercontent.com/nodejs/Release/main/README.md].
**Version-sensitive (applies to v27+):** Node.js announced 2026-03-10 that
starting with **v27** it is retiring the twice-yearly odd/even cadence for
one annual release where **every** line becomes LTS: 6 months Alpha
(Oct–Mar, explicitly not for production) → 6 months Current (Apr–Oct) → 30
months LTS, 36 months total support — the same total duration as today,
delivered as one continuous line instead of split odd/even lines. **v26 is
explicitly the last release under the old model**; v27 enters Alpha October
2026 [Source: https://nodejs.org/en/blog/announcements/evolving-the-nodejs-release-schedule].
Unresolved: the source material itself flags that any claim about the
v27+ process specifics is provisional until confirmed against a live
schedule after October 2026 — re-verify before relying on it.

**v26.0.0 breaking changes (applies to >=26.0.0):** the Temporal API is
enabled by default as a new global (not opt-in); `crypto.createCipher()`/
`createDecipher()`, `http.Server.prototype.writeHeader()`, and the legacy
`_stream_wrap`/`_stream_readable`/`_stream_writable`/`_stream_duplex`/
`_stream_transform`/`_stream_passthrough` internal modules are **fully
removed**, not merely deprecated [Source: https://nodejs.org/en/blog/release/v26.0.0].

> Deep module-by-module API detail, the full v22/v24/v26 breaking-change
> lists, and the debugging/profiling tool inventory live in
> [`research/technologies/nodejs.md`](../../research/technologies/nodejs.md)
> — consult it directly for anything beyond this summary (context-efficiency;
> no separate references/ file duplicates it here).

## Decision framework

This does not repeat backend-architecture's Node-vs-Go-vs-Python framework —
see [`SK-BE-001`](../backend-architecture/SKILL.md) for that. Within an
already-chosen Node.js service:

1. **CommonJS or ESM for a new project?** Prefer ESM by default for new code
   (the direction Node's own tooling — `import.meta.dirname`, Import
   Attributes, native TypeScript support — is moving) *unless* a dependency
   or deployment target hard-requires CommonJS interop that ESM's `import()`-
   based interop can't cleanly cover, or the team's existing codebase and
   tooling are CommonJS and a migration isn't justified by the task at hand.
   Don't force a mid-project rewrite to "modernize" without a concrete reason.
2. **worker_threads vs child_process vs cluster — what's actually the
   bottleneck?**
   - I/O-bound (network, disk, DB) → neither; Node's native async I/O and the
     libuv pool already handle this. Tune `UV_THREADPOOL_SIZE` before adding
     concurrency machinery.
   - CPU-bound work that must not block the event loop → `worker_threads`
     (shared-memory option available via `SharedArrayBuffer`); reach for
     `child_process` only if isolation (crash containment, a different
     language/runtime) matters more than shared-memory convenience.
   - Scaling a whole service across CPU cores for throughput → `cluster` (or
     an external process manager), keeping session/shared state in an
     external store since `cluster` shares nothing in-process.
   - **Simplest-first:** if the workload is small or infrequent, don't stand
     up a worker pool at all — measure before adding concurrency machinery.
3. **Adopt the Permission Model?** Its own docs are explicit it is not a
   sandbox against malicious code, only a guard against *unintentional*
   resource access by trusted code (see Security). Worth adopting as
   defense-in-depth for a service with well-understood, narrow resource
   needs; not a substitute for dependency vetting or process-level isolation
   (containers, VMs) when the threat model includes malicious dependencies.
   Roll out via `--permission-audit` first to derive the real allowlist,
   then switch to enforcing `--permission`.
4. **Which release line to target?** Track Active LTS or Maintenance LTS in
   production, not Current — Current exists for early testing and
   library-author CI, not production use, per the release policy itself.
   Confirm the current line assignments before committing to one (see
   Knowledge; they shift as of this writing and again materially at v27).

## Workflow

Diagnosing a suspected event-loop-blocking or capacity issue:

1. Confirm the symptom is event-loop blocking and not a memory leak or GC
   pause — check whether *all* concurrent requests stall together (blocking
   signature) vs. gradual latency growth (leak/GC signature).
2. Profile: CPU — `perf` with `--perf-basic-prof`/`--perf-basic-prof-only-functions`
   and `--interpreted-frames-native-stack`, or the `0x` wrapper tool, for
   flame graphs [Source: https://nodejs.org/en/learn/diagnostics/flame-graphs].
   Memory — `--inspect` + Chrome DevTools' Memory tab, using the sampling
   heap profiler (low overhead, documented "safe for production") rather than
   the allocation timeline (development-only) [Source:
   https://nodejs.org/en/learn/diagnostics/memory/using-heap-profiler].
3. Locate the offending synchronous call or hot computation (see
   Anti-patterns for the common offenders).
4. Apply the smallest fix: task-partition the computation with `setImmediate()`
   yields, or offload to `worker_threads`/a `child_process` pool/`cluster`,
   accepting serialization overhead as the cost [Source:
   https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop].
5. Re-profile to confirm the fix actually removed the blocking signature
   before declaring done.

## Engineering rules

- State which Node.js release line (Current/Active LTS/Maintenance LTS) your
  guidance targets; never assume "latest" silently.
- Match the concurrency primitive to the bottleneck (I/O vs CPU vs
  process-isolation vs core-scaling) — don't default to `cluster` or
  `worker_threads` out of habit.
- Use `stream/promises`' `pipeline()` over manual `.pipe()` chains for
  correct backpressure, error propagation, and `AbortSignal` cancellation
  [Source: https://nodejs.org/api/stream.html].
- Use `npm ci` (not `npm install`) in CI/deployment: it requires a matching
  lockfile, always rebuilds `node_modules`, and never mutates
  `package.json`/the lockfile [Source: https://docs.npmjs.com/cli/v11/commands/npm-ci].
- If adopting native TypeScript type stripping, remember it does not read
  `tsconfig.json`, requires explicit file extensions in import specifiers,
  and rejects enums/namespaces-with-runtime-code/parameter
  properties/decorators (`ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`) — these need a
  real transformer instead [Source: https://nodejs.org/api/typescript.html].

## Trade-offs

CommonJS's synchronous, ubiquitous `require()` remains simpler for scripts
and legacy interop; ESM's static structure enables tooling (tree-shaking,
`import.meta`) and is where Node's own newer features (Import Attributes,
`import.meta.dirname`) land first, at the cost of CommonJS interop rules
that are easy to get wrong on first exposure. `worker_threads` buys
shared-memory speed for CPU-bound work at the cost of message-passing/
serialization overhead that is pure loss for I/O-bound work (per the
module's own docs); `child_process`/`cluster` buy crash isolation and
core-scaling at the cost of no shared memory and — for `cluster` — no
built-in session affinity, pushing state into an external store.

## Anti-patterns

- **Blocking the event loop with synchronous CPU-heavy work** — the
  domain's central anti-pattern: Node.js serves many clients on one thread
  plus a small worker pool, so one blocked call degrades *every* concurrent
  client, not just its own caller [Source:
  https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop].
- **Calling the synchronous form of an expensive built-in in request-handling
  code**: `crypto.randomBytes()`'s sync form, `randomFillSync()`,
  `pbkdf2Sync()`, `zlib.*Sync()`, synchronous `fs` calls (especially over
  NFS), `child_process.spawnSync()`/`execSync()`/`execFileSync()` [Source:
  https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop].
- **Pathological regexes** (nested quantifiers, overlapping alternation,
  backreferences) matched against untrusted input on the event loop — ReDoS;
  use `indexOf()`-based matching, `safe-regex` linting, or `node-re2` instead
  [Source: https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop].
- **Using `worker_threads` for I/O-bound work** — the module's own docs call
  this out; native async I/O already beats it [Source:
  https://nodejs.org/api/worker_threads.html].
- **Relying on `cluster`'s optional direct-socket-handoff mode** for load
  balancing — documented real-world imbalance as severe as 70%+ on 2 of 8
  workers; the default round-robin mode is safer [Source:
  https://nodejs.org/api/cluster.html].
- **Standing up a worker pool "for performance" before measuring** — the
  domain's over-engineering trap; profile first (Workflow), since most
  slowness is I/O-bound and unaffected by `worker_threads`/`cluster`.
- **Running Node.js as container PID 1 without an init wrapper** — signal
  delivery for graceful shutdown breaks; Node's own Docker working group
  documents this as a structural gap requiring `--init` or an embedded Tini
  [Source: https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md].

## Security

- **Permission Model (`--permission`, Stable since v23.5.0/v22.13.0;
  `--permission` name since v24.0.0, was `--experimental-permission`)**
  restricts filesystem, child-process, worker, native-addon, WASI, FFI,
  network, and OpenSSL-store access by default-deny [Source:
  https://nodejs.org/api/permissions.html]. **Explicit official caveat: "This
  does NOT provide security against malicious code. Per Node.js Security
  Policy, Node.js trusts any code it is asked to run"** — it is a guard
  against *unintentional* access by trusted code, not a sandbox. Documented
  gaps: permissions don't inherit into worker threads; an already-open file
  descriptor bypasses the model entirely; symlinks are followed even outside
  granted paths; `process._debugProcess(pid)` is not gated at all [Source:
  https://nodejs.org/api/permissions.html].
- **CVE-2026-58043 (HIGH, applies to lines before v26.5.1/v24.18.1/v22.23.2,
  patched 2026-07-29):** the Permission Model's own path-matching logic could
  **over-grant** filesystem access across radix-tree prefix boundaries under
  `--permission` — a sandboxing feature had a sandbox-escape bug. It shipped
  in a coordinated release alongside 10 other CVEs across the 26.x/24.x/22.x
  lines, including two HIGH HTTP/2 issues (retained-header memory exhaustion,
  and a re-entrant-callback use-after-free) [Source:
  https://nodejs.org/en/blog/vulnerability/july-2026-security-releases]. Treat
  any Permission Model deployment predating that release as unpatched;
  confirm the running patch level rather than assuming an old pin is safe.
- Other documented anti-patterns worth enforcing: never enable
  `insecureHTTPParser` (reopens HTTP request smuggling, CWE-444); compare
  secrets with `crypto.timingSafeEqual()`, never `===` (timing attacks,
  CWE-208); guard `__proto__`/`constructor`/`prototype` keys on
  untrusted-object merges (prototype pollution, CWE-1321) via
  `Object.create(null)`/`Object.freeze()`/`Object.hasOwn()`, not schema
  validation alone; never expose `--inspect` beyond `127.0.0.1` — even
  loopback-bound inspectors are open to any local process by design [Source:
  https://nodejs.org/en/learn/getting-started/security-best-practices].
- Node.js core vulnerabilities (not npm-package vulnerabilities) are reported
  via HackerOne with a default 72-hour embargo before coordinated disclosure
  [Source: https://nodejs.org/en/about/security]. Deep threat-modeling method
  beyond Node-specifics is owned by `security-engineering`, not restated here.

## Performance

- `UV_THREADPOOL_SIZE` (default 4, max 1024) is the primary lever for
  filesystem-/DNS-heavy workloads saturating the libuv pool [Source:
  https://docs.libuv.org/en/v1.x/threadpool.html].
- For CPU-bound work: offload to `worker_threads`, a `child_process`/
  `cluster` pool, or an N-API native addon — and still partition the work,
  since one long worker-pool task blocks that worker slot for its full
  duration [Source: https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop].
- `cluster` scales across CPU cores by forking one worker process per core
  (commonly sized via `os.availableParallelism()`) [Source:
  https://nodejs.org/api/cluster.html].
- Profiling tools: `perf` + V8 flags or the `0x` wrapper for CPU flame
  graphs; `--inspect` + DevTools Memory tab (sampling profiler for
  production-safe use, allocation timeline for development) for heap issues
  [Source: https://nodejs.org/en/learn/diagnostics/flame-graphs,
  https://nodejs.org/en/learn/diagnostics/memory/using-heap-profiler].
  Deep cross-cutting performance method is owned by `performance-engineering`.

## Testing

The built-in **`node:test`** module has been available since v18.0.0 and
Stable since v20.0.0, run via `node --test` or programmatically via `run()`
[Source: https://nodejs.org/api/test.html]. It supports `test()`/
`describe()`/`it()` with `.skip`/`.todo`/`.only`, nested subtests, lifecycle
hooks, context-scoped mocking (`t.mock.fn()`, `t.mock.timers`), coverage via
`--experimental-test-coverage` with pluggable reporters
(`spec`/`tap`/`dot`/`junit`/`lcov`), and snapshot testing. **Node.js's own
documentation does not recommend `node:test` over third-party frameworks**
like Jest or Vitest — it presents `node:test` as a viable, dependency-free,
stable option, while noting third-party frameworks may still suit more
complex scenarios [Source: https://nodejs.org/api/test.html]. Deep
test-strategy method is owned by `SK-QA-001` / the Jest-Vitest technology
skill; this skill only states what `node:test` itself supports.

## Failure handling

- If the Node.js release line cannot be determined, ask for it or state
  explicitly which line (Current/Active LTS/Maintenance LTS) the guidance
  assumes — never assume "latest" silently.
- If shell is unavailable/denied, output advisory config/flag/code changes
  (package.json, tsconfig, CLI flags) and state that nothing was executed or
  profiled.

## Escalation

- A production Permission Model allowlist change, or an upgrade across a
  Node.js major line, should be confirmed explicitly before applying — both
  are documented to change runtime behavior (removed APIs, a bumped
  `NODE_MODULE_VERSION` ABI requiring native-addon rebuilds).

## Outputs & verification

- **Outputs:** Node.js-runtime guidance (module system, concurrency
  primitive, Permission Model adoption, or a diagnosed performance issue),
  and config/flag/code changes reflecting it.
- **Verify:** every version claim is tagged with the release line/range it
  applies to; Permission Model guidance repeats its "not a sandbox against
  malicious code" caveat; the chosen concurrency primitive matches the
  actual bottleneck (I/O vs CPU vs isolation vs core-scaling).

## References

- Primary source: [`research/technologies/nodejs.md`](../../research/technologies/nodejs.md)
  (37 official sources: nodejs.org, the `nodejs` GitHub organization, and
  `docs.libuv.org`; retrieved 2026-09-10).
- Parent skill: [`SK-BE-001` backend-architecture](../backend-architecture/SKILL.md)
  — owns generic layering/middleware/DI/error-handling/shutdown and the
  Node-vs-Go-vs-Python runtime-selection framework.
- Related (forthcoming, not yet authored): `SK-TECH-express`,
  `SK-TECH-fastify` — framework-level specifics that run on this runtime.
- Full source list: see `skill.yaml.source_references`.
