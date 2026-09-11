# Node.js — Deep Technology Reference

Research date: 2026-09-10. Primary source: official Node.js documentation hosted
at `nodejs.org` (API reference under `/api/`, guides under `/en/learn/`, release
and governance material under `/en/about/` and `/en/blog/`) — no host migration
observed. Supplemented by the official `nodejs` GitHub organization
(`github.com/nodejs/node`, `github.com/nodejs/Release`, `github.com/nodejs/corepack`,
`github.com/nodejs/docker-node`) for release policy, changelogs, and working-group
guidance, and by `docs.libuv.org` (the libuv project Node.js embeds for its event
loop) for thread-pool internals not documented on nodejs.org itself. Because the
task explicitly requires documenting Node.js's integration with npm, the official
npm documentation at `docs.npmjs.com` is also cited for the npm-specific claims in
Sections 4, 10, and 16 — npm is organizationally separate from the OpenJS
Foundation-governed Node.js project, but is the tool being integrated with, and its
own docs are the only authoritative source for its own behavior.

Citation format per project convention: `[Source: <url>] <claim>.` Claims not
found in official docs are marked "Not documented / could not verify."
Uncertain claims are marked "Unresolved: …". Inferences are labeled
"[Inference, not confirmed in docs]".

---

## 1. Core Concepts

[Source: https://nodejs.org/en/learn/getting-started/introduction-to-nodejs] Node.js is described as "an open-source and cross-platform JavaScript runtime environment" that runs the V8 JavaScript engine (the same engine that powers Google Chrome) and executes JavaScript outside a browser.

[Source: https://nodejs.org/en/learn/getting-started/introduction-to-nodejs] A Node.js application "runs in a single process without creating a new thread for every request"; Node.js provides asynchronous, non-blocking I/O primitives so that JavaScript code is not blocked waiting on network, filesystem, or database responses, allowing a single process to handle many concurrent connections without the overhead of thread-per-connection concurrency.

[Source: https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick] The event loop is "the mechanism that allows Node.js to perform non-blocking I/O operations ... despite the fact that JavaScript is single-threaded," by offloading operations to the OS kernel where possible and to libuv's worker thread pool otherwise, and re-invoking JavaScript callbacks once results are ready.

[Source: https://docs.libuv.org/en/v1.x/threadpool.html] libuv is the C library underlying Node.js's event loop and worker thread pool; its thread pool "is used to run user code and get notified in the loop thread" for operations the OS cannot itself perform asynchronously, and defaults to 4 threads, configurable via the `UV_THREADPOOL_SIZE` environment variable up to an absolute maximum of 1024 (raised from a prior 128-thread ceiling in libuv 1.30.0). [Source: https://docs.libuv.org/en/v1.x/threadpool.html] The thread pool is "internally used to run all file system operations, as well as `getaddrinfo` and `getnameinfo` requests"; it is a single global pool shared across all event loops in a process, and the functions using it are not thread-safe.

[Source: https://nodejs.org/api/packages.html] Node.js supports two module systems: CommonJS (the historical `require()`/`module.exports` system, and the default) and ECMAScript Modules (ESM, `import`/`export`). A package's `"type"` field in `package.json` controls how Node.js interprets `.js` files: `"commonjs"` (default) or `"module"`; `.mjs` files are always ESM and `.cjs` files are always CommonJS regardless of `"type"`.

[Source: https://nodejs.org/api/esm.html] When no explicit marker (extension, `"type"` field, or `--input-type`) is present, Node.js falls back to inspecting the source text for ES module syntax (`import`/`export`, `import.meta`, top-level `await`) to auto-detect the module format.

[Source: https://nodejs.org/api/esm.html] CommonJS↔ESM interop: ESM can `import` CommonJS modules, with `module.exports` exposed as the default export and named exports detected via static analysis (added v14.13.0/v12.20.0); CommonJS `require()` can synchronously load ESM (support for `require()`-ing synchronous ESM graphs landed as a Node.js 22 headline feature, per Section 13); dynamic `import()` works from both module systems. ESM lacks CommonJS globals (`require`, `__filename`, `__dirname`, `module.exports`) — equivalents are `import.meta.resolve()`, `import.meta.filename`/`import.meta.dirname` (stable since v24.0.0), and `module.createRequire()`.

[Source: https://nodejs.org/api/esm.html] Import Attributes (`import config from './package.json' with { type: 'json' }`, stable since v23.1.0) replaced the earlier, deprecated Import Assertions syntax (`assert { type: 'json' }`).

---

## 2. Architecture

[Source: https://nodejs.org/en/learn/getting-started/introduction-to-nodejs] Node.js's architecture layers embedded V8 (JavaScript parsing/execution/JIT compilation) beneath a C++ binding layer and libuv (event loop, async I/O, thread pool), with a JavaScript standard library (`node:fs`, `node:http`, etc.) built on top.

[Source: https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick] The event loop cycles through six phases each iteration, in order: **timers** (execute `setTimeout`/`setInterval` callbacks whose threshold has elapsed), **pending callbacks** (deferred I/O callbacks, e.g. certain TCP errors like `ECONNREFUSED`), **idle, prepare** (internal use only), **poll** (retrieve new I/O events and execute their callbacks; the loop blocks here when appropriate), **check** (execute `setImmediate()` callbacks), and **close callbacks** (e.g. `socket.on('close', ...)`).

[Source: https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick] Timer thresholds are not exact execution times — a callback fires only after at least the specified delay *and* only once the poll phase yields control back to the timers phase; a long-running poll-phase task (e.g. an I/O callback) can push a nominally-due timer past its threshold. Starting with libuv 1.45.0 (bundled from Node.js 20), timers run after the poll phase in each iteration.

[Source: https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick] `process.nextTick()` is explicitly **not** part of the event loop's phase cycle: its queue is drained after the current operation completes, before the loop proceeds to the next phase, regardless of which phase is current. Recursive `process.nextTick()` calls can therefore "starve" I/O by preventing the loop from ever reaching the poll phase. `setImmediate()` differs by scheduling a callback for the **check** phase of the *next* loop iteration; when both are scheduled inside an I/O callback, `setImmediate()` always executes before any pending `setTimeout(fn, 0)`, independent of how many timers are queued.

[Source: https://nodejs.org/en/about/governance] Node.js's core repository (`nodejs/node`) is maintained by Collaborators with commit access, nominated by existing Collaborators; a Technical Steering Committee (TSC), a subset of active Collaborators, provides high-level project governance under a published TSC Charter, using a consensus-seeking decision model. [Source: https://nodejs.org/en/about/governance] The project operates under the OpenJS Foundation, which holds the project's trademarks and maintains cross-project policies (Code of Conduct, Security Policy, Trademark Policy).

[Source: https://nodejs.org/api/typescript.html] Since v22.6.0, Node.js's module loader includes a native TypeScript **type-stripping** pipeline as part of its module-resolution architecture: type annotations are erased (replaced with whitespace) rather than transpiled, so no source maps are generated and no type checking is performed at load time — architecturally distinct from a full compile step.

---

## 3. APIs

[Source: https://nodejs.org/api/fs.html] The `node:fs` module offers three parallel API styles: callback-based (`require('node:fs')`, historically the primary style), promise-based (`require('node:fs/promises')`, built around the `FileHandle` class wrapping a file descriptor, recommended for new async/await code), and synchronous (blocking) functions intended for startup scripts, not request-handling code. Notable additions include `fs.glob()`/`fsPromises.glob()` for pattern-based file discovery.

[Source: https://nodejs.org/api/http.html] The `node:http` module implements HTTP/1.1 client and server functionality (`http.createServer()`, `http.request()`/`http.get()`); it never buffers an entire request or response, making it efficient for large or chunked payloads. Connection reuse and pooling for clients is managed via the `http.Agent` class (`keepAlive`, `maxSockets`, `maxTotalSockets`, `maxFreeSockets`, `keepAliveMsecs`); `keepAlive` defaults to `false`. HTTP/2 is implemented in the **separate** `node:http2` module, not `node:http`.

[Source: https://nodejs.org/api/path.html] The `node:path` module provides cross-platform path manipulation; its behavior adapts to the host OS by default (Windows vs. POSIX semantics), and it exposes explicit `path.win32` and `path.posix` namespaces so code can force one convention's behavior regardless of the host platform.

[Source: https://nodejs.org/api/stream.html] The `node:stream` module defines four fundamental stream types — Readable, Writable, Duplex (both readable and writable, e.g. `net.Socket`), and Transform (a Duplex that modifies data in transit, e.g. `zlib.createDeflate()`). Backpressure is signaled when `writable.write()` returns `false` once the internal buffer reaches `highWaterMark`; producers should wait for the `'drain'` event before continuing to write. `stream.Readable.fromWeb()`/`toWeb()` (and Writable/Duplex equivalents) interoperate with WHATWG web streams; `node:stream/promises` provides promise-based `pipeline()` and `finished()`, both supporting `AbortSignal`.

[Source: https://nodejs.org/api/worker_threads.html] The `node:worker_threads` module runs JavaScript on additional OS threads that can share memory (via `ArrayBuffer`/`SharedArrayBuffer`), unlike `child_process` or `cluster`. Documented guidance: "Workers (threads) are useful for performing CPU-intensive JavaScript operations. They do not help much with I/O-intensive work. The Node.js built-in asynchronous I/O operations are more efficient than Workers can be." Core API surface: `Worker`, `isMainThread`, `parentPort`, `workerData`, `MessageChannel`/`MessagePort`, `BroadcastChannel`, transfer lists (`postMessage(data, [transferable])`), `resourceLimits`, and `getEnvironmentData()`/`setEnvironmentData()`.

[Source: https://nodejs.org/api/cluster.html] The `node:cluster` module (Stability: 2 — Stable) forks multiple worker **processes** (via `child_process.fork()` under the hood) that share listening ports, coordinated by a primary process, to spread load across CPU cores. On all platforms except Windows the primary distributes accepted connections round-robin by default; the alternative (primary hands the listening socket directly to workers) is documented as having "unbalanced" real-world distribution "due to operating system scheduler vagaries," with an observed case of over 70% of connections landing on 2 of 8 worker processes. `node:cluster` provides no routing/session-affinity logic and no automatic worker-pool sizing — the application must manage both. For simpler in-process multithreading, Node.js's own docs point to `worker_threads` instead of `cluster` when process isolation is unnecessary.

[Source: https://nodejs.org/api/diagnostics_channel.html] The `node:diagnostics_channel` module (introduced v15.1.0/v14.17.0, Stable since v19.2.0/v18.13.0) lets modules publish named diagnostic events (`Channel`, `TracingChannel`, `BoundedChannel`) for consumption by monitoring/tracing tooling, with built-in instrumentation for HTTP, HTTP/2, module loading, networking, and SQLite.

[Source: https://nodejs.org/api/util.html] The `node:util` module provides `util.promisify()` (callback→Promise conversion), `util.inspect()` (debug string formatting), `util.debuglog()` (conditional logging gated by the `NODE_DEBUG` env var), `util.parseArgs()` (structured CLI argument parsing), `util.callbackify()`, `util.isDeepStrictEqual()`, `util.types.*` type predicates, and WHATWG `TextEncoder`/`TextDecoder`.

[Source: https://nodejs.org/api/process.html] The global `process` object exposes `process.env` (environment variables; case-insensitive access on Windows; in-process mutations do not propagate to the OS environment), `process.argv`, `process.exit([code])`, `process.on(signal, cb)` for OS signals (`SIGINT`, `SIGTERM`, `SIGHUP`, etc.), and `process.report` (a diagnostic-report API, `writeReport()`/`getReport()`, for capturing process/heap state for post-mortem debugging).

[Source: https://nodejs.org/api/test.html] The built-in `node:test` module (see Section 9) and `node:permissions` (see Sections 4/7) round out the built-ins most relevant to application development; the full standard-library index is published and auto-updated at `nodejs.org/api/`, which should be consulted per-module rather than exhaustively mirrored here. Not documented / could not verify: an exhaustive module-by-module API listing is out of scope for this reference.

---

## 4. Configuration

[Source: https://nodejs.org/api/packages.html] Node.js reads and interprets specific `package.json` fields: `"type"` (added v12.0.0 — module format, `"commonjs"`/`"module"`); `"main"` (added v0.4.0 — legacy entry point, superseded by `"exports"` when both are present); `"exports"` (added v12.7.0 — declares public entry points/subpaths and encapsulates everything else, throwing `ERR_PACKAGE_PATH_NOT_EXPORTED` for anything not listed); `"imports"` (added v14.6.0/v12.19.0 — private `#`-prefixed import-specifier remapping, supports conditional and external-package targets); and `"name"` (added v13.1.0/v12.16.0, enables self-referencing a package by its own name).

[Source: https://nodejs.org/api/packages.html] Conditional exports resolve in a documented priority order — `"node-addons"`, `"node"`, `"import"`/`"require"` (mutually exclusive), `"module-sync"`, then `"default"` as the catch-all — plus community-defined conditions (`"types"`, `"browser"`, `"development"`/`"production"`) and custom conditions enabled via `node --conditions=<name>`. Export target strings must start with `./`, may not contain `..`/`.` path-traversal segments, and cannot reference paths outside the package.

[Source: https://nodejs.org/api/cli.html] `NODE_OPTIONS` is an environment variable accepting most CLI flags that are also permitted inside a Node.js configuration file; command-line-supplied flags take precedence over `NODE_OPTIONS`, which in turn takes precedence over flags loaded from a `--env-file` or from `--experimental-config-file`.

[Source: https://nodejs.org/api/cli.html] `--env-file=<path>` (added v20.6.0, stable as of v24.10.0/v22.21.0) loads `KEY=VALUE` pairs from a dotenv-style file into `process.env`; multiple `--env-file` flags may be given, later files overriding earlier ones; `#`-prefixed lines are comments, quoted and multi-line values are supported, a leading `export` keyword is ignored, and existing environment variables take precedence over file contents. `--env-file-if-exists` (v22.9.0) is a non-erroring variant for an optional file.

[Source: https://nodejs.org/api/cli.html] Notable environment variables Node.js itself reads (non-exhaustive): `NODE_DEBUG`/`NODE_DEBUG_NATIVE` (module debug logging), `NODE_PATH` (colon-delimited module search path), `NODE_EXTRA_CA_CERTS`, `NODE_NO_WARNINGS`, `NODE_PENDING_DEPRECATION`, `NODE_PRESERVE_SYMLINKS`, `NODE_TLS_REJECT_UNAUTHORIZED`, `NODE_V8_COVERAGE`, `NODE_COMPILE_CACHE` (and `_PORTABLE`/`_READONLY` variants), `UV_THREADPOOL_SIZE` (libuv thread pool size — see Section 2), `FORCE_COLOR`/`NO_COLOR`, and `TZ`.

[Source: https://nodejs.org/api/cli.html] Native TypeScript type-stripping input handling: `--input-type` accepts `"module-typescript"`/`"commonjs-typescript"` values (updated v23.6.0/v22.18.0); `--no-strip-types` (added v26.0.0) disables type stripping outright and disallows those `-typescript` input-type values. When `--input-type` is not specified, Node.js attempts CommonJS, then ESM, then type-stripping, in that documented fallback order.

[Source: https://nodejs.org/api/cli.html] `--experimental-config-file` (v23.10.0, release-candidate as of v26.7.0) allows a JSON configuration file (`node.config.json` by default) with namespaced sections (`nodeOptions`, `test`, `watch`, `permission`); presence of a namespace in the file auto-enables the corresponding runtime flag.

[Source: https://docs.npmjs.com/cli/v11/configuring-npm/npmrc] npm (bundled with Node.js) reads configuration from `.npmrc` files at four precedence levels, highest first: per-project (`/path/to/project/.npmrc`, not read for global installs), per-user (`~/.npmrc`), global (`$PREFIX/etc/npmrc`, overridable via the `globalconfig` setting), and npm's own built-in defaults file. Files use `key = value` INI-style syntax with `;`/`#` comments and `key[]` array syntax.

[Source: https://github.com/nodejs/corepack#readme] Corepack — "a zero-runtime-dependency Node.js script that acts as a bridge between Node.js projects and the package managers they are intended to be used with" (Yarn, npm, and pnpm) — ships bundled with Node.js from v14.19.0 up to (but not including) v25.0.0; on Node.js 25.0.0+ it must be installed separately (`npm install -g corepack`). It is enabled per-machine via `corepack enable`.

---

## 5. Recommended Patterns

[Source: https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop] Node.js's own guidance frames the core performance/security discipline as: "Node.js is fast when the work associated with each client at any given time is 'small'" — keep event-loop callbacks and worker-pool tasks bounded, because Node.js serves many concurrent clients with a small, fixed number of threads (one event loop plus the libuv worker pool), so one blocked thread delays every pending client.

[Source: https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop] Recommended mitigation for unavoidable long-running work: **task partitioning** — break a long synchronous computation into smaller chunks yielded back to the event loop via `setImmediate()` between chunks — or **offload to the worker pool/worker threads/child processes/cluster**, accepting serialization overhead as the tradeoff. Bound and validate untrusted input sizes (JSON payload length, regex pattern length) before processing them synchronously. Prefer streaming JSON parsers for very large payloads over `JSON.parse()`/`JSON.stringify()`, and prefer `indexOf()`/well-audited regex over ad hoc patterns vulnerable to ReDoS (see Section 6).

[Source: https://nodejs.org/api/stream.html] Use `stream/promises`' `pipeline()` (rather than manually wiring `.pipe()` chains) to compose Readable/Transform/Writable streams with correct error propagation, backpressure handling, and `AbortSignal`-based cancellation.

[Source: https://docs.npmjs.com/cli/v11/commands/npm-ci] Use `npm ci` rather than `npm install` in CI/CD and deployment pipelines: it requires an existing, matching `package-lock.json`/`npm-shrinkwrap.json`, deletes `node_modules` before installing, never modifies `package.json` or the lockfile, and fails outright on a mismatch — producing a reproducible, "frozen" install rather than a potentially-drifting one.

[Source: https://nodejs.org/api/permissions.html] For adopting the Permission Model incrementally in an existing codebase, use `--permission-audit` first: it performs the same permission checks as `--permission` but does not block access, instead publishing violations to `node:diagnostics_channel` — letting an operator discover the exact allowlist a workload needs before switching to enforcing mode.

[Source: https://nodejs.org/en/learn/getting-started/security-best-practices] Recommended dependency-supply-chain hygiene: `npm install --ignore-scripts` (or `npm config set ignore-scripts true`) to prevent arbitrary install-time script execution from third-party packages; `npm audit` for known-vulnerability scanning; and, as of npm v11.10.0+, a "dependency cooldown" (`npm config set min-release-age=1`) that refuses to install packages published within the last N days, with an explicit per-install override (`--min-release-age=0`) for urgent security fixes.

[Source: https://nodejs.org/api/typescript.html] For TypeScript projects relying on native type stripping (TypeScript 5.8+), the documented required `tsconfig.json` shape sets `"noEmit": true`, `"module": "nodenext"`, `"rewriteRelativeImportExtensions": true`, `"erasableSyntaxOnly": true`, and `"verbatimModuleSyntax": true`, and source files must use explicit `.ts`/`.mts`/`.cts` extensions in import specifiers.

---

## 6. Anti-Patterns

[Source: https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop] Regular expressions with nested quantifiers (`(a+)*`), overlapping alternation (`(a|a)*`), or backreferences (`(a.*)\1`) risk catastrophic/exponential-time backtracking (ReDoS) when matched against adversarial input on the event loop — documented as both a performance and a denial-of-service anti-pattern; safer alternatives cited are `indexOf()`-based matching, the `safe-regex` linting tool, or the RE2-backed `node-re2` module.

[Source: https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop] Calling the *synchronous* forms of expensive built-in APIs on the main thread inside request-handling code is explicitly flagged as dangerous: `crypto.randomBytes()`'s sync form, `crypto.randomFillSync()`, `crypto.pbkdf2Sync()`, `zlib.*Sync()`, any synchronous `fs` call (especially against network filesystems like NFS), and `child_process.spawnSync()`/`execSync()`/`execFileSync()`.

[Source: https://nodejs.org/en/learn/getting-started/security-best-practices] Enabling `insecureHTTPParser` when constructing an HTTP server is called out as an anti-pattern that reopens HTTP request-smuggling risk (CWE-444) by tolerating ambiguous request framing that front-end/back-end servers may interpret differently.

[Source: https://nodejs.org/en/learn/getting-started/security-best-practices] Comparing secrets (tokens, password hashes) with ordinary `===`/string comparison is an anti-pattern enabling timing-attack information disclosure (CWE-208); use `crypto.timingSafeEqual()` (or `crypto.scrypt()` for password comparison) instead, and avoid branching control flow on secret values.

[Source: https://nodejs.org/en/learn/getting-started/security-best-practices] Merging untrusted, attacker-controlled objects into application state without guarding `__proto__`/`constructor`/`prototype` keys is flagged as the prototype-pollution anti-pattern (CWE-1321); documented mitigations include `Object.create(null)` for untrusted-data containers, `Object.freeze()` on prototypes, `Object.hasOwn()` checks, and the (Windows-unsupported) `--disable-proto` flag — not merely "validate with a schema" as a first line of defense.

[Source: https://nodejs.org/en/learn/getting-started/security-best-practices] Running production Node.js processes with the inspector left enabled, or exposing `--inspect`'s debug port beyond `127.0.0.1`, is an anti-pattern: any client that can reach the inspector port gets arbitrary code execution in the process, and — per the debugging guide below — even loopback-bound inspectors are fully open to any *local* process by design.

[Source: https://nodejs.org/api/cluster.html] Relying on `cluster`'s optional "hand the listening socket directly to workers" distribution mode for load balancing is discouraged by the module's own docs, which document observed real-world imbalance as severe as 70%+ of connections landing on 2 of 8 workers; the default round-robin primary-side distribution is the safer choice.

[Source: https://nodejs.org/api/worker_threads.html] Using `worker_threads` for I/O-bound work (as opposed to CPU-bound computation) is an anti-pattern per the module's own docs: "they do not help much with I/O-intensive work" and add per-worker overhead that Node's native async I/O already avoids.

---

## 7. Security

[Source: https://nodejs.org/en/about/security] Node.js's threat model, as codified in its Security Policy: reports of vulnerabilities in Node.js core (not third-party npm packages, which should be reported to their own maintainers) go through HackerOne (`hackerone.com/nodejs`), require a minimum HackerOne Signal score of 1.0 (contributors below that threshold are directed to the OpenJS Foundation Slack to reach security release stewards directly), and receive an initial acknowledgment within 5 days and a substantive response within 10 days (subject to slippage around year-end holidays).

[Source: https://nodejs.org/en/about/security] Disclosure process: a report is triaged and validated against all supported release lines; affected versions are confirmed and the codebase is audited for similar issues; fixes are prepared and held privately; a CVE is requested and an embargo date set (**default 72 hours** from CVE issuance, adjustable for severity/complexity); on the embargo date, the fix ships to the `nodejs-sec` Google Group and the Node.js blog (advisory published within 6 hours), and new builds are published to nodejs.org. Node.js also runs an official HackerOne-hosted bug bounty program and holds an OpenSSF Best Practices badge.

[Source: https://nodejs.org/en/blog/vulnerability/july-2026-security-releases] Concrete recent example (July 29, 2026 security release, patching v26.5.1/v24.18.1/v22.23.2): 11 CVEs were disclosed simultaneously across the 26.x/24.x/22.x lines, spanning HIGH (CVE-2026-56846 — HTTP/2 retained headers bypassing `maxSessionMemory`, remote memory exhaustion; CVE-2026-56848 — HTTP/2 re-entrant `nghttp2_session_mem_send()` causing heap-use-after-free), MEDIUM, and LOW severities. Notably, **CVE-2026-58043 (HIGH)** was a Permission Model bug: "path matching can over-grant filesystem access across radix-tree prefix boundaries under `--permission`" — i.e., a security feature meant to *restrict* filesystem access instead granted more access than intended, and CVE-2026-58040 was documented as "an incomplete fix for CVE-2026-48934," showing a prior HTTPS-Agent hostname-verification patch had not fully closed the issue.

[Source: https://nodejs.org/api/permissions.html] The Permission Model (`--permission` flag; introduced v20.0.0, Stable as of v23.5.0/v22.13.0) restricts, by default-deny, access to the filesystem (`--allow-fs-read`/`--allow-fs-write`), child processes (`--allow-child-process`), worker threads (`--allow-worker`), native addons (`--allow-addons`), WASI (`--allow-wasi`), FFI (`--allow-ffi`), network (`--allow-net`), and OpenSSL STORE loaders (`--allow-openssl-store`); violations throw `ERR_ACCESS_DENIED`. **Explicit, official caveat: "This does NOT provide security against malicious code. Per Node.js Security Policy, Node.js trusts any code it is asked to run"** — it is documented as a "seat belt" against *unintentional* resource access by trusted code, not a sandbox.

[Source: https://nodejs.org/api/permissions.html] Documented Permission Model limitations: permissions do not inherit into worker threads (each worker's permission state is independent); using an already-open file descriptor via `node:fs` bypasses the model entirely; pre-initialization flags (`--env-file`, `--openssl-config`, V8 flags) are processed before the model initializes and are unaffected by it; symbolic links are followed even outside granted paths, so a relative symlink inside an allowed directory can escape it; and `process._debugProcess(pid)` — used to force open another process's inspector — is *not* gated by the Permission Model at all, consistent with the "trusts the OS environment" threat model described above.

[Source: https://nodejs.org/en/learn/getting-started/security-best-practices] Documented mitigation for prototype-pollution, monkey-patching, and DNS-rebinding-against-the-inspector attack classes are covered in Section 6 (Anti-Patterns); additional documented hardening flags: `--frozen-intrinsics` (experimental, recursively freezes built-in globals/prototypes) and `--secure-heap=<n>` (secure heap allocation for sensitive data, unavailable on Windows).

---

## 8. Performance

[Source: https://docs.libuv.org/en/v1.x/threadpool.html] `UV_THREADPOOL_SIZE` (default 4, max 1024) is the primary lever for filesystem- and DNS-lookup-heavy workloads that saturate the libuv worker pool; as of libuv 1.45.0, pool threads use an 8 MB stack rather than the platform default (previously "sometimes too low").

[Source: https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop] For CPU-bound work, the documented options are offloading to `worker_threads`, a `child_process`/`cluster` pool, or a native addon via N-API — and, when offloading, still partitioning the work to minimize per-task time variance, since one long worker-pool task blocks that worker slot for its full duration.

[Source: https://nodejs.org/api/cluster.html] `cluster` scales a Node.js application across CPU cores by forking one worker process per core (commonly sized via `os.availableParallelism()`); see Section 6 for the documented caveat about uneven load distribution under the non-default direct-socket-handoff mode.

[Source: https://nodejs.org/en/learn/diagnostics/flame-graphs] Official CPU-profiling/flame-graph guidance centers on Linux `perf` plus V8-specific flags: `--perf-basic-prof` (or the lower-overhead, production-oriented `--perf-basic-prof-only-functions`) to expose JS function names to `perf`, and `--interpreted-frames-native-stack` (Node.js 10+) to fix function-name resolution across V8's Turbofan-optimized code paths. The community tool `0x` is documented as a pre-packaged wrapper that "has built-in mitigations for V8 Turbofan issues" and simplifies local flame-graph generation.

[Source: https://nodejs.org/en/learn/diagnostics/memory/using-heap-profiler] Two documented heap-profiling modes via `--inspect` + Chrome DevTools' Memory tab: the **allocation timeline** (traces every allocation, high overhead, development-only) and the **sampling heap profiler** (low overhead, "safe for production systems," reports allocations aggregated by stack trace).

[Source: https://nodejs.org/api/esm.html] Type-stripped TypeScript execution (Section 1/4) has no separate compile step and generates no source maps, since type annotations are erased in place rather than transformed — a documented architectural performance tradeoff versus a full `tsc`/`tsx` compile pipeline.

VERSION SENSITIVITY: [Source: https://nodejs.org/en/blog/release/v26.0.0] Node.js 26.0.0 (2026-05-05) updated V8 to 14.6.202.33 and Undici (the bundled `fetch`/HTTP client implementation) to 8.0.2; [Source: https://raw.githubusercontent.com/nodejs/node/main/doc/changelogs/CHANGELOG_V24.md] Node.js 24.0.0 (2025-05-06) updated V8 to 13.6 and bundled Undici 7 ("numerous improvements to the HTTP client capabilities, including better performance"), and switched `AsyncLocalStorage` to use `AsyncContextFrame` by default, described as "a more efficient implementation of asynchronous context tracking."

---

## 9. Testing

[Source: https://nodejs.org/api/test.html] The built-in `node:test` module has been available since v18.0.0 and became **Stable** in v20.0.0. It is run via `node --test` (default file-discovery globs include `**/*.test.{cjs,mjs,js}`, `**/test/**/*.{cjs,mjs,js}`, etc.) or programmatically via `run()`.

[Source: https://nodejs.org/api/test.html] Core API: `test()`/`describe()`/`it()` (with `.skip`, `.todo`, `.only` — the latter gated by `--test-only`), `.expectFailure()`, nested subtests (`t.test(...)`), lifecycle hooks (`before`/`after`/`beforeEach`/`afterEach`), and context-scoped mocking (`t.mock.fn()`, `t.mock.method()`, `t.mock.timers` for fake `setTimeout`/`Date`).

[Source: https://nodejs.org/api/test.html] Coverage is enabled via `--experimental-test-coverage` and reported through pluggable reporters (`--test-reporter=spec|tap|dot|junit|lcov`); coverage-exclusion pragmas (`/* node:coverage disable */`/`enable`/`ignore next`) are supported inline. Snapshot testing (`t.assert.snapshot()`, `t.assert.fileSnapshot()`, regenerated via `--test-update-snapshots`) and experimental tag-based filtering (`--experimental-test-tag-filter`) are also built in.

[Source: https://nodejs.org/api/test.html] Node.js's documentation does not explicitly recommend `node:test` over third-party frameworks such as Jest or Mocha; the module is presented as a viable, dependency-free, stable option with native ESM/CJS support, integrated mocking, and integrated coverage, while third-party frameworks may still suit more complex testing scenarios.

---

## 10. Deployment

[Source: https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md] The official Node.js Docker working group's best practices: use **multi-stage builds** — a build stage where the package manager installs dependencies and builds the app, and a slimmer runtime stage that copies only the built `app` and `node` directories, excluding the package manager itself; use `npm ci` (not `npm install`) for reproducible installs; the official `node` Docker images ship a pre-created unprivileged `node` user (uid 1000) for running the container as non-root.

[Source: https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md] Explicit documented gotcha: "Node.js was not designed to run as PID 1 which leads to unexpected behaviour when running inside of Docker" (signal handling for graceful shutdown breaks under PID 1 without special handling) — mitigated by Docker's `--init` flag (Docker 1.13+) or by including an init process such as Tini directly in the image. Additional documented recommendations: set `NODE_ENV=production`, apply container memory limits, and `CMD` the application directly (bypassing an `npm start` wrapper process) so it becomes PID 1's direct child rather than a grandchild of npm.

[Source: https://github.com/nodejs/corepack#readme] For deployments that pin a specific package manager version, Corepack (Section 4) is the documented mechanism — `corepack enable` plus a `"packageManager"` field convention — though on Node.js 25+ it must be installed as a separate dependency rather than relying on the Node.js-bundled copy.

[Source: https://docs.npmjs.com/cli/v11/commands/npm-ci] `npm ci`'s "frozen install" contract (exact lockfile match required, `node_modules` always rebuilt from scratch, no writes to `package.json`/lockfiles) is the documented basis for deterministic, repeatable deployment builds.

Not documented / could not verify: nodejs.org itself does not host a first-party, platform-specific (AWS/GCP/Vercel/etc.) deployment guide; official deployment guidance is scoped to the Docker working group's container-image practices cited above plus general process-management advice (signals, `NODE_ENV`) found across the security and diagnostics guides.

---

## 11. Migration

[Source: https://nodejs.org/en/about/previous-releases] Node.js does not publish a single official "vN-to-vN+1 migration guide" document analogous to some frameworks; the documented mechanism for discovering what changed between major versions is each release's own **changelog** (`doc/changelogs/CHANGELOG_V<N>.md` in `github.com/nodejs/node`) and its accompanying release-announcement blog post on `nodejs.org/en/blog/release/`, both of which itemize semver-major commits, deprecations, and removals per release (see Section 13 for worked examples from v22, v24, and v26).

[Source: https://nodejs.org/api/cli.html] `NODE_PENDING_DEPRECATION=1` surfaces "pending deprecation" warnings for APIs slated for future runtime-deprecation, giving codebases a way to proactively audit for upcoming breakage ahead of a major upgrade.

[Source: https://github.com/nodejs/corepack#readme] Corepack's removal from Node.js's own bundled distribution starting at v25.0.0 is itself a documented migration point: projects that assumed `corepack` ships with `node` must add it as an explicit dependency (`npm install -g corepack`) when upgrading past v24.x.

[Source: https://nodejs.org/api/typescript.html] Migrating a codebase onto Node's native TypeScript type-stripping (rather than a third-party transpiler such as `tsx`) requires adjusting `tsconfig.json` to the documented shape (Section 5) and rewriting code that uses unsupported constructs — enum declarations, namespaces containing runtime code, parameter properties, import aliases, and decorators all raise `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX` under type stripping and must be rewritten or run through a real transformer instead.

[Source: https://nodejs.org/en/blog/release/v26.0.0] Node.js 26.0.0's release notes double as example migration guidance: they explicitly instruct upgraders to replace `http.Server.prototype.writeHeader()` with `writeHead()` (the former was fully removed) and to stop depending on the legacy `_stream_*` internal modules (also fully removed), and they call out new build-toolchain minimums (GCC 13.2+, Python 3.10+) that affect anyone building Node.js itself or native addons against it.

Not documented / could not verify: whether the OpenJS Foundation or Node.js TSC publishes a consolidated, versioned "breaking changes across all majors" index page distinct from the per-release changelogs; none was located in this research pass.

---

## 12. Version Information

[Source: https://nodejs.org/en/download] As of this research, the current **Current** release is **v26.8.2** and the current **LTS** release is **v24.21.0**.

[Source: https://raw.githubusercontent.com/nodejs/Release/main/README.md] Full active-line schedule at time of research: **v22.x "Jod"** — initial release 2024-04-24, Active LTS started 2024-10-29, Maintenance started 2025-10-21, End-of-life 2027-04-30 (currently in Maintenance LTS); **v24.x "Krypton"** — initial release 2025-05-06, Active LTS started 2025-10-28, Maintenance starts 2026-10-20, EOL 2028-04-30 (currently Active LTS); **v26.x** — initial release 2026-05-05, Active LTS starts 2026-10-28, Maintenance starts 2027-10-20, EOL 2029-04-30 (currently Current, not yet LTS).

[Source: https://raw.githubusercontent.com/nodejs/Release/main/README.md] Release policy quoted, describing the model that produced v22/v24/v26 above: "New *semver-major* releases of Node.js are branched from `main` every six months. New even-numbered versions are released in April and odd-numbered versions in October." "In coordination with a new *odd-numbered* major release, the previous *even-numbered* major version will transition to Long Term Support." "Every even (LTS) major version will be actively maintained for 12 months from the date it enters LTS coverage. Following those 12 months of active support, the major version will transition into 'maintenance' mode for 18 months." Odd-numbered lines never receive LTS status and become unsupported roughly 6 months after release. Changes generally must live in a Current release for at least 2 weeks before being backported to an LTS line.

[Source: https://nodejs.org/en/about/previous-releases] Confirming the above: v25 (initial release 2025-10-15) is already EOL (its "unsupported after 6 months" status is consistent with the odd-line policy); v23 and v21 (both odd) are likewise EOL.

VERSION SENSITIVITY — upcoming cadence change: [Source: https://nodejs.org/en/blog/announcements/evolving-the-nodejs-release-schedule] Node.js announced (2026-03-10) that **starting with Node.js 27, the twice-yearly cadence and odd/even LTS distinction are being retired in favor of one major release per year, with every release becoming LTS.** Under the new model: a 6-month **Alpha** channel (semver-major changes permitted; explicitly "not for production use," aimed at library authors and CI) runs October–March; **Current** runs April–October of the release year; **LTS** then runs for 30 months, for **36 months of total support** from first Current release to EOL — the same total *support duration* as today's model, per the announcement, but delivered as one continuous line instead of split even/odd lines. Node.js 26 (released April 2026) is explicitly the **last** release under the old six-month/odd-even model; Node.js 27 enters Alpha in October 2026 and is expected to become Current in April 2027, entering LTS in October 2027 with an EOL around April 2030. Because this transition begins in the month immediately following this research date, treat any claim about the *v27+* process as provisional until confirmed against a live schedule after October 2026.

[Source: https://nodejs.org/en/about/security] Security-patch releases (see Section 7 for a worked example) are issued out-of-band across all currently-supported lines simultaneously when a qualifying vulnerability is fixed, independent of the feature-release cadence above.

Node.js does not use a Go-style "N and N-1 supported" window; instead, at any moment there are up to three active lines — one Current, one Active LTS, one Maintenance LTS — as shown in the schedule table above.

---

## 13. Breaking Changes

VERSION SENSITIVITY — Node.js 26.0.0 (2026-05-05), [Source: https://nodejs.org/en/blog/release/v26.0.0]:
- Fully removed (no longer just deprecated): `crypto.createCipher()`/`createDecipher()` (use `createCipheriv()`/`createDecipheriv()`); `http.Server.prototype.writeHeader()` (use `writeHead()`); the legacy `_stream_wrap`/`_stream_readable`/`_stream_writable`/`_stream_duplex`/`_stream_transform`/`_stream_passthrough` internal modules; the `--experimental-transform-types` flag.
- Promoted to *runtime* deprecation (from documentation-only): two `crypto` deprecations (DEP0203, DEP0204), one `stream` deprecation (DEP0201), and `module.register()`.
- Temporal API enabled by default (a new global, not merely an opt-in flag). V8 bumped to 14.6.202.33; Undici to 8.0.2; `NODE_MODULE_VERSION` bumped to 147 (native addons must be rebuilt).
- Build/toolchain minimums raised: GCC 13.2+, Python 3.10+ (3.9 dropped), Windows SDK 11; AIX/IBM i now targets Power 9 only (p8/z13 dropped).

VERSION SENSITIVITY — Node.js 24.0.0 (2025-05-06), [Source: https://raw.githubusercontent.com/nodejs/node/main/doc/changelogs/CHANGELOG_V24.md]:
- MSVC support removed for building Node.js on Windows; **ClangCL is now required**. Minimum macOS bumped to 13.5; minimum Xcode bumped to 16.1. `armv7` support downgraded to experimental; 32-bit `s390` support removed.
- `--experimental-permission` flag renamed to `--permission` (signaling increased stability of the Permission Model, per the release notes).
- `SlowBuffer` moved to end-of-life (fully removed); `dirent.path` removed from `fs.Dirent`; `fs.F_OK`/`R_OK`/`W_OK`/`X_OK` runtime-deprecated; `tls.createSecurePair` removed; `tls.Server.prototype.setOptions` moved to end-of-life; `net._setSimultaneousAccepts()` moved to end-of-life; the obsolete `Cipher` export removed from `lib`.
- `node:test`'s `test()`/`t.test()` no longer return the promises they used to (test runner now automatically awaits subtests — a breaking API-shape change for code that awaited those return values itself).
- Passing `args` to `child_process.spawn()`/`execFile()` deprecated. `fs.existsSync()` now deprecates invalid argument types instead of silently coercing them. `URLPattern` added as a new global (potential name collision for code defining its own `URLPattern`). `AsyncLocalStorage` switched its default internal implementation to `AsyncContextFrame`.
- npm bundled version bumped to npm 11.

VERSION SENSITIVITY — Node.js 22.0.0 (2024-04-24), [Source: https://raw.githubusercontent.com/nodejs/node/main/doc/changelogs/CHANGELOG_V22.md]:
- `require()`-ing synchronous ESM module graphs became supported (a `SEMVER-MINOR` capability addition, but one that changes CJS/ESM interop behavior broadly).
- WebSocket client enabled by default as a global. Default stream `highWaterMark` was increased (`SEMVER-MAJOR` — changes default buffering/backpressure timing for code relying on the old default). Import assertions (the `assert { type: 'json' }` syntax, as opposed to the newer Import Attributes `with` syntax) were dropped from ESM support.
- V8 bumped to 12.4.254.14, enabling the Maglev mid-tier JIT compiler on supported architectures. `--watch` mode marked Stable. `node --run <script>` added as a native `package.json`-script runner (`SEMVER-MINOR`). `crypto`'s `Hmac`/`Hash` constructors runtime-deprecated; `crypto.createCipher`/`createDecipher` moved to end-of-life in this release (fully removed later, in v26 per above — a multi-release deprecation-to-removal arc).

Not documented / could not verify: breaking-change specifics for Node.js v20 and earlier majors were not independently re-fetched in this research pass; consult `github.com/nodejs/node/blob/main/doc/changelogs/CHANGELOG_V20.md` and earlier directly if that history is needed.

---

## 14. Limitations

[Source: https://nodejs.org/api/permissions.html] The Permission Model's own documentation is explicit that Node.js's security threat model does not defend against malicious code the process is asked to run at all — "Node.js trusts any code it is asked to run" — a foundational, documented limitation that shapes how every other security feature (Permission Model, `--frozen-intrinsics`, `--secure-heap`) should be understood: they harden against *unintended* behavior of trusted code, not against a genuinely adversarial dependency.

[Source: https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop] Because Node.js multiplexes many clients onto a small, fixed set of threads (the single JS thread plus the libuv worker pool), any single blocking operation — a slow synchronous call, a pathological regex, an oversized synchronous JSON parse — degrades service for *every* concurrent client, not just the one that triggered it; this is a structural consequence of the single-threaded event-loop model, not a bug to be patched.

[Source: https://nodejs.org/api/cluster.html] `cluster` provides no built-in cross-worker state sharing or session affinity: "It is therefore important to design an application such that it does not rely too heavily on in-memory data objects for things like sessions and login" — shared state must live in an external store (Redis, a database, etc.). On Windows specifically, "it is not yet possible to set up a named pipe server in a worker" under `cluster`.

[Source: https://nodejs.org/api/worker_threads.html] `worker_threads` documents itself as poorly suited to I/O-bound work — the overhead of thread creation and message-passing serialization outweighs the benefit versus Node's native async I/O for that workload class (see Section 6).

[Source: https://nodejs.org/api/typescript.html] Native TypeScript type stripping cannot handle any TypeScript construct that requires actual code transformation rather than pure erasure: enum declarations, namespaces containing runtime (non-type-only) code, constructor parameter properties, import aliases, and decorators all raise `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`. It also does not read `tsconfig.json` at all (no path-alias resolution, no syntax downleveling), requires explicit file extensions in every import specifier, and is disabled for code inside `node_modules`.

[Source: https://docs.libuv.org/en/v1.x/threadpool.html] The libuv thread pool is a single pool shared globally across all event loops in a process, and — per its own docs — "the functions are not thread safe," constraining how it can be reused by embedders or addons beyond Node's own internal use.

[Source: https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md] Node.js "was not designed to run as PID 1," which breaks default OS-signal delivery/handling semantics for graceful shutdown when a Node.js process is the direct entrypoint of a container — a documented, structural gap requiring an external init wrapper (Docker's `--init` or an embedded Tini) rather than a Node.js-side fix.

---

## 15. Debugging

[Source: https://nodejs.org/learn/getting-started/debugging] `node --inspect` starts a debugging-client listener on `127.0.0.1:9229` by default (custom host/port via `--inspect=[host:port]`); `--inspect-brk` additionally breaks execution before any user code runs; `--inspect-wait` waits for a debugger client to attach before proceeding. Node.js also begins listening for the inspector protocol when it receives `SIGUSR1` (not available on Windows; `--disable-sigusr1` turns this off). Each inspected process exposes a unique UUID-scoped WebSocket debugging URL (`ws://127.0.0.1:9229/<uuid>`).

[Source: https://nodejs.org/learn/getting-started/debugging] Documented security caveats: binding the inspector to a public IP/`0.0.0.0` lets *any* network client execute arbitrary code in the process; even bound to loopback, "local applications have full access to the inspector" by design, so co-located untrusted local processes are not isolated from it; Node.js validates the `Host` header on the inspector's initial HTTP handshake (must be an IP literal or exactly `localhost`) specifically to block DNS-rebinding attacks from browser tabs. **Official recommendation: never bind the inspector to a public IP; use an SSH tunnel** (`ssh -L 9221:localhost:9229 user@remote`) for remote debugging instead.

[Source: https://nodejs.org/learn/getting-started/debugging] Documented first-party and IDE integrations: Chrome DevTools 55+/Edge (`chrome://inspect` / `edge://inspect`, or a manually-copied `devtoolsFrontendUrl` from `http://localhost:<port>/json/list`), Visual Studio Code 1.10+ (`.vscode/launch.json`, Node.js debug configuration), Visual Studio 2017+, JetBrains IDEs (WebStorm et al., `--inspect` used by default for Node.js 7+), and Eclipse (Wild Web Developer). The pre-Node-8 legacy debugger (`--debug`/`--debug-brk`, port 5858, the discontinued V8 Debugging Protocol) has been deprecated since Node.js 7.7.0 in favor of `--inspect`.

[Source: https://nodejs.org/api/diagnostics_channel.html] `node:diagnostics_channel` (Section 3) is the documented low-level hook for building custom tracing/APM instrumentation without patching Node's own source, with built-in channels already wired into HTTP, HTTP/2, module loading, DNS/networking, and SQLite.

[Source: https://nodejs.org/api/permissions.html] When the Permission Model is enabled, `--permission-audit` mode (Section 5) doubles as a debugging tool for discovering exactly which filesystem/network/child-process/worker/addon resources a piece of code touches, by subscribing to the `node:permission-model:*` diagnostics channels rather than blocking access outright.

[Source: https://nodejs.org/en/learn/diagnostics/memory/using-heap-profiler] Memory-leak/allocation debugging is done via the `--inspect` + Chrome DevTools Memory tab workflow (allocation timeline for development, sampling profiler safe for production; see Section 8), and [Source: https://nodejs.org/en/learn/diagnostics/flame-graphs] CPU-time debugging via `perf`-based flame graphs or the `0x` wrapper tool (Section 8).

[Source: https://nodejs.org/api/process.html] `process.report.writeReport()`/`getReport()` generate a point-in-time diagnostic report (process/heap/resource state) useful for post-mortem debugging of crashes or hangs without attaching a live debugger.

---

## 16. Integration

[Source: https://docs.npmjs.com/cli/v11/configuring-npm/npmrc] Node.js ships bundled with npm, whose behavior is configured through the four-level `.npmrc` hierarchy described in Section 4; [Source: https://docs.npmjs.com/cli/v11/commands/npm-ci] `npm ci` is npm's documented integration point for reproducible CI/deployment installs against a committed `package-lock.json`.

[Source: https://github.com/nodejs/corepack#readme] Corepack is Node.js's documented integration layer for **other** package managers — Yarn and pnpm, alongside npm — letting a project pin an exact package-manager version (conventionally via a `"packageManager"` field) without each contributor globally installing that manager themselves; distributed with Node.js core through v24.x, a separate install as of v25+.

[Source: https://nodejs.org/api/packages.html] Node.js's module-resolution "conditions" mechanism (`package.json` `"exports"`, Section 4) is itself an integration point that third-party build tooling (bundlers, TypeScript) has extended via community-defined conditions such as `"types"` and `"browser"`, layered on top of the Node.js-defined `"node"`/`"import"`/`"require"`/`"default"` conditions.

[Source: https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md] The official `nodejs/docker-node` working group repository is the documented integration surface between Node.js and Docker/container platforms, publishing the multi-stage-build, non-root-user, and PID-1/init-wrapper guidance summarized in Section 10.

[Source: https://nodejs.org/api/stream.html] `stream.Readable.fromWeb()`/`toWeb()` (and the Writable/Duplex equivalents) are the documented integration bridge between Node.js's native stream implementation and the WHATWG web-standard Streams API used by `fetch`, service workers, and browser-portable code.

[Source: https://nodejs.org/api/test.html] `node:test`'s pluggable reporter interface (`--test-reporter=junit|lcov|tap|...`, or a custom `Transform`-based reporter) is the documented integration point for feeding CI systems and coverage services (e.g., an LCOV-consuming coverage dashboard) without a third-party test framework in between.

[Source: https://nodejs.org/api/esm.html] `node:` protocol imports (`import fs from 'node:fs'`, mandatory-prefix support since v14.13.1 for builtins) are the documented, unambiguous way userland code and bundlers distinguish Node.js built-in modules from same-named npm packages during ESM/CJS interop and bundling.

---

## 17. Production Considerations

[Source: https://raw.githubusercontent.com/nodejs/Release/main/README.md] Production deployments should track one of the two currently-maintained even-numbered lines (Active LTS or Maintenance LTS) rather than a Current or (historically) odd-numbered release — Current/odd lines exist for early testing and library-author CI, not production, per the release policy's own framing, and lack the 30-month support runway LTS lines carry (see Section 12 for the incoming v27+ change to this model).

[Source: https://nodejs.org/en/about/security] Subscribe to the `nodejs-sec` Google Group and/or the Node.js blog's vulnerability feed for security-release notifications, since patches ship out-of-band across all supported lines simultaneously on an embargo date rather than on the normal feature-release cadence (Section 7).

[Source: https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md] For containerized production deployments: multi-stage builds to exclude build-time tooling from the runtime image; run as the bundled non-root `node` user; set `NODE_ENV=production`; use `--init` (or an embedded Tini) to correctly propagate shutdown signals given Node's documented PID-1 limitation; and `CMD` the app directly rather than through an `npm start` indirection layer.

[Source: https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop] Production capacity planning should account for the single-event-loop-thread model: use `cluster` or a process manager to run one Node.js process per CPU core for throughput, and route genuinely CPU-bound work to `worker_threads` (Sections 3, 8) rather than letting it run inline on the request-handling thread.

[Source: https://nodejs.org/api/permissions.html] For defense-in-depth against unintentional resource access from trusted-but-imperfect code (not against malicious dependencies — see Section 14's threat-model caveat), roll out the Permission Model progressively: `--permission-audit` in staging to derive the exact allowlist, then `--permission` with that allowlist enforced in production.

[Source: https://docs.npmjs.com/cli/v11/commands/npm-ci] Production build pipelines should use `npm ci` against a committed lockfile for deterministic, auditable dependency resolution, combined (per Section 5) with `--ignore-scripts` and `npm audit`/a minimum-release-age policy to reduce supply-chain exposure from the moment a dependency version is first pulled.

[Source: https://nodejs.org/api/process.html] `process.on('SIGTERM', ...)`/`process.on('SIGINT', ...)` handlers for graceful shutdown (draining in-flight requests, closing DB pools) are a production baseline, given both the PID-1 signal-delivery caveat in containers (Section 14) and `cluster`'s documented lack of automatic client-connection cleanup on worker disconnect (Section 3).

---

## Sources Consulted (full list)

- https://raw.githubusercontent.com/nodejs/Release/main/README.md — official release schedule and policy (LTS/Current/Maintenance definitions, cadence)
- https://nodejs.org/en/about/previous-releases — release schedule table (cross-check)
- https://nodejs.org/en/download — current Current/LTS version numbers
- https://nodejs.org/en/blog/announcements/evolving-the-nodejs-release-schedule — official announcement of the v27+ annual release-cadence change
- https://nodejs.org/en/about/security — security policy, vulnerability reporting/disclosure process
- https://nodejs.org/en/blog/vulnerability/july-2026-security-releases — worked example security release with CVE list
- https://nodejs.org/en/about/governance — project governance (Collaborators, TSC, OpenJS Foundation)
- https://nodejs.org/en/learn/getting-started/introduction-to-nodejs — core concepts/architecture overview
- https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick — event loop phases, process.nextTick, setImmediate
- https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop — blocking-the-event-loop anti-patterns and mitigations
- https://nodejs.org/en/learn/getting-started/security-best-practices — documented vulnerability classes and mitigations
- https://nodejs.org/learn/getting-started/debugging — --inspect/--inspect-brk, DevTools/IDE integration, security caveats
- https://nodejs.org/en/learn/diagnostics/flame-graphs — CPU profiling / flame graph guidance
- https://nodejs.org/en/learn/diagnostics/memory/using-heap-profiler — heap profiling guidance
- https://nodejs.org/api/esm.html — ECMAScript Modules implementation and CJS/ESM interop
- https://nodejs.org/api/packages.html — package.json fields, conditional exports
- https://nodejs.org/api/permissions.html — Permission Model reference
- https://nodejs.org/api/test.html — node:test built-in test runner
- https://nodejs.org/api/worker_threads.html — worker_threads module
- https://nodejs.org/api/cluster.html — cluster module
- https://nodejs.org/api/cli.html — CLI flags, NODE_OPTIONS, env vars, TypeScript flags
- https://nodejs.org/api/diagnostics_channel.html — diagnostics_channel module
- https://nodejs.org/api/util.html — util module
- https://nodejs.org/api/fs.html — fs module
- https://nodejs.org/api/stream.html — stream module
- https://nodejs.org/api/http.html — http module
- https://nodejs.org/api/path.html — path module
- https://nodejs.org/api/process.html — process global object
- https://nodejs.org/api/typescript.html — native TypeScript type-stripping support
- https://nodejs.org/en/blog/release/v26.0.0 — Node.js 26.0.0 release notes
- https://raw.githubusercontent.com/nodejs/node/main/doc/changelogs/CHANGELOG_V24.md — Node.js 24.0.0 changelog/breaking changes
- https://raw.githubusercontent.com/nodejs/node/main/doc/changelogs/CHANGELOG_V22.md — Node.js 22.0.0 changelog/breaking changes
- https://docs.libuv.org/en/v1.x/threadpool.html — libuv thread pool internals (UV_THREADPOOL_SIZE)
- https://github.com/nodejs/corepack#readme — Corepack (npm/Yarn/pnpm bridge) documentation
- https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md — official Docker working group best practices
- https://docs.npmjs.com/cli/v11/configuring-npm/npmrc — npm's .npmrc configuration hierarchy
- https://docs.npmjs.com/cli/v11/commands/npm-ci — npm ci documentation
