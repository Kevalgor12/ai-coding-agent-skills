---
name: Python
description: >-
  Python-specific engineering: the GIL and its free-threading evolution (PEP
  703/779), sub-interpreters (PEP 684/734), concurrency-model choice
  (asyncio/multiprocessing vs. free-threaded builds), venv/pyproject.toml
  packaging, and exception chaining (raise...from). Use when the stack is
  Python (pyproject.toml/requirements.txt/setup.py, a .py entrypoint, or the
  task names Python). Not for the generic backend-structure decision
  (backend-architecture) or LLM/agent-application-specific design.
spec_version: "1.0"
---

## Purpose & scope

Apply Python correctly and version-appropriately: the GIL and its
free-threading evolution, sub-interpreters, concurrency-model selection,
virtual environments/packaging, and exception chaining. The generic
backend-structure method (layering, DI, error handling, shutdown) comes from
the parent skill ([backend-architecture](../backend-architecture/SKILL.md),
`SK-BE-001`). Python's role specifically in LLM/agent application engineering
belongs to `SK-AI-001` — a forward reference to a skill not yet authored in
this library (a documented research gap, not an oversight); no LLM-specific
content is assumed here.

## When to use / When not to use

**Use** when the stack is Python (`pyproject.toml`/`requirements.txt`/
`setup.py`, a Python interpreter/venv as the runtime target, or the task
names a Python-specific concern: GIL, free-threaded/no-GIL builds,
sub-interpreters, venv, pip, asyncio, multiprocessing, unittest, exception
chaining). **Do not use** for another language/runtime with no Python
component (route to that technology skill), for the generic backend-structure
decision with no language chosen yet (route to `SK-BE-001`), or for
LLM/agent-application design itself (prompt engineering, RAG, agent
orchestration — route to `SK-AI-001` once authored).

## Knowledge

**The GIL and its free-threading evolution.** The Global Interpreter Lock is
"the mechanism used by the CPython interpreter to assure that only one thread
executes Python bytecode at a time," trading multi-processor parallelism for
a simpler, implicitly-thread-safe object model; it is released during I/O and
by some extensions during heavy computation [Source:
https://docs.python.org/3/glossary.html#term-global-interpreter-lock].
**[Version: 3.13 experimental → 3.14 officially supported]** Free-threaded
("no-GIL") CPython, per PEP 703, removes the single lock via biased/deferred
reference counting, object immortalization, per-object locking, and mimalloc.
It is disable-at-build (`--disable-gil`, binary typically `python3.13t`) plus
a runtime toggle (`-X gil=0` / `PYTHON_GIL=0`), introduced experimentally in
3.13; as of 3.14 (PEP 779) it is "officially supported," with the
specializing adaptive interpreter now also enabled in free-threaded mode and
single-thread overhead narrowed to roughly 5–10% (down from a documented
1–8%, platform-dependent, at 3.13) [Source:
https://docs.python.org/3/howto/free-threading-python.html; Source:
https://peps.python.org/pep-0703/; Source:
https://docs.python.org/3/whatsnew/3.14.html]. Free-threaded builds also use
more memory (larger non-GC object headers, immortalized interned strings,
mimalloc overhead) and carry real limitations: many third-party C extensions
are not yet compatible and silently (with a warning) re-enable the GIL on
import; accessing another thread's `f_locals` is unsafe and can crash the
interpreter; built-in container iterators are not thread-safe for concurrent
access [Source: https://docs.python.org/3/howto/free-threading-python.html].

**Sub-interpreters.** **[Version: >=3.12 C-API, >=3.14 stdlib]**
Sub-interpreters gained their own, independent per-interpreter GIL at the
C-API level in 3.12 (PEP 684, `Py_NewInterpreterFromConfig` with
`PyInterpreterConfig_OWN_GIL`), enabling true parallelism between
interpreters in one process. Python 3.14 (PEP 734) exposed this at the
standard-library level via `concurrent.interpreters` and
`concurrent.futures.InterpreterPoolExecutor` [Source:
https://docs.python.org/3/whatsnew/3.14.html]. This is a third concurrency
axis distinct from both classic GIL-bound threading and free-threaded builds.

**Virtual environments and packaging.** `venv` (standard library since 3.3)
creates isolated virtual environments, each with its own interpreter/
`site-packages`; environments are explicitly documented as **not portable**
(recreate rather than move or commit them) [Source:
https://docs.python.org/3/library/venv.html]. Project/build configuration is
standardized around `pyproject.toml`: a `[build-system]` table selects the
build backend (Hatchling, Setuptools, Flit, PDM, uv-build) and a `[project]`
table holds metadata and dependencies [Source:
https://packaging.python.org/en/latest/tutorials/packaging-projects/].
**[Version: >=3.12]** `distutils` was removed from the standard library (PEP
632); the documented migration target is `setuptools` [Source:
https://docs.python.org/3/whatsnew/3.12.html].

**Exception chaining.** All exceptions derive from `BaseException`; user code
should subclass `Exception`, not `BaseException` directly. Implicit chaining
sets `__context__` automatically when an exception is raised inside an
`except`/`finally`/`with` block; explicit chaining via `raise NewException(
...) from original` sets `__cause__`; `raise ... from None` sets
`__suppress_context__ = True` to deliberately hide the original [Source:
https://docs.python.org/3/library/exceptions.html]. This is the documented
pattern for wrapping/translating exceptions across a layer boundary (e.g. a
data-access exception becoming a domain exception) without losing the
original cause.

> Deep version-by-version detail (the 3.14 GC revert's patch-level nuance,
> platform-tier history, the tail-call interpreter build) is inline below and
> in `skill.yaml.version_sensitive_claims` rather than a separate reference
> file — the material is claims, not a large table, so it stays Tier 1
> (context-efficiency rule CE-3).

## Decision framework

1. **Simplest first (anti-overengineering):** does `asyncio` already solve
   an I/O-bound concurrency need? Don't reach for free-threaded builds or
   sub-interpreters when cooperative concurrency already fits — free-threaded
   builds carry real single-thread overhead and memory cost, and
   sub-interpreters have process-like isolation semantics that add real
   complexity.
2. **CPU-bound work:** `multiprocessing` remains the traditional, documented
   answer under the standard GIL-bound interpreter [Source:
   https://docs.python.org/3/howto/free-threading-python.html]. A
   free-threaded build is worth evaluating only when (a) the workload is
   genuinely multi-threaded and CPU-bound, (b) the C-extension dependency
   surface has been audited for free-threading compatibility (an
   incompatible extension silently re-enables the GIL at import — a
   production-monitoring-worthy event, not a dev-time curiosity), and (c) the
   team can tolerate 3.13's "experimental" status or has moved to 3.14's
   "officially supported" one. Otherwise, `multiprocessing` or accepting the
   GIL's threading ceiling is the safer default.
3. **Sub-interpreters vs. multiprocessing vs. free-threading:** sub-
   interpreters (3.14+ via `concurrent.interpreters`) sit between the two —
   per-interpreter isolation without a full OS-process's overhead — but are
   the newest and least-battle-tested of the three stdlib-level options;
   don't adopt them as a default over the more mature `multiprocessing`/
   `asyncio` without a concrete reason.
4. **Can this project safely target 3.14 today?** Check the exact patch
   version, not just "3.14," before making a GC-behavior-sensitive claim or
   commitment: 3.14.0–3.14.4 shipped an incremental GC that caused reported
   production memory pressure, reverted to 3.13's generational GC in
   3.14.5+ [Source: https://docs.python.org/3/whatsnew/3.14.html]. A project
   pinning an early 3.14.x patch should be flagged for that specific risk,
   independent of whether "3.14" in general is otherwise safe to adopt. Also
   check for reliance on `ProcessPoolExecutor`'s old `fork` default (now
   `forkserver` on non-macOS Unix as of 3.14) and any dependency on
   `distutils` (removed 3.12) or `2to3`/`lib2to3` (removed 3.13).
5. **Version gate generally:** state the exact Python version (and, for
   GC/concurrency claims, patch) the guidance targets — never assume
   "latest" implicitly (rule VA-3).

## Engineering rules

- State the Python version (and patch, for GC/free-threading claims) any
  recommendation targets; don't give version-generic advice for
  version-gated behavior.
- Default to `multiprocessing`/`asyncio` for concurrency; only recommend a
  free-threaded build after workload shape and C-extension compatibility are
  both confirmed.
- Use `venv` + `pyproject.toml` for dependency isolation and packaging;
  don't install into a shared/system interpreter.
- Use explicit exception chaining (`raise ... from`) when translating an
  exception across a layer boundary; use `raise ... from None` only to
  deliberately suppress an uninteresting original context, not to hide bugs.
- Don't depend on `distutils` (removed 3.12) or `2to3`/`lib2to3` (removed
  3.13); migrate to `setuptools` and drop 2-to-3 tooling entirely.

## Trade-offs

Free-threaded builds buy real multi-core threading parallelism at the cost of
single-thread overhead (~5–10% as of 3.14, down from ~1–8%, platform-
dependent, at 3.13), higher memory use, and a C-extension compatibility tax
[Source: https://docs.python.org/3/howto/free-threading-python.html; Source:
https://docs.python.org/3/whatsnew/3.14.html]. `multiprocessing` avoids that
compatibility tax entirely but pays IPC/serialization overhead and higher
per-worker memory (separate processes, no shared memory by default).
Sub-interpreters (3.14+) trade some of `multiprocessing`'s isolation
guarantees for lower overhead than a full OS process, at the cost of being
the newest, least field-proven option of the three.

## Anti-patterns

- **Assuming free-threading is available or default** without checking the
  actual interpreter build/version — it is opt-in through 3.14, not the
  default CPython build [Source:
  https://docs.python.org/3/howto/free-threading-python.html].
- **Adopting free-threaded builds or sub-interpreters as a default over
  `asyncio`/`multiprocessing`** without a concrete workload reason — the
  domain's over-engineering trap; both existing models remain the documented,
  battle-tested answers for their respective workload shapes.
- **Bare `except:` (or `except BaseException:`)** — swallows
  `SystemExit`/`KeyboardInterrupt`/`GeneratorExit`, which are deliberately
  direct `BaseException` subclasses so ordinary `except Exception:` handlers
  don't catch them by accident [Source:
  https://docs.python.org/3/library/exceptions.html].
- **Depending on `distutils`** (removed in 3.12) or **`2to3`/`lib2to3`**
  (removed in 3.13) [Source: https://docs.python.org/3/whatsnew/3.12.html;
  Source: https://docs.python.org/3/library/2to3.html].
- **Citing "Python 3.14" as sufficient version detail for a GC-behavior
  claim** — the incremental-GC-then-revert happened within the 3.14 bugfix
  series itself (3.14.0–3.14.4 vs. 3.14.5+); the patch version is
  load-bearing here [Source: https://docs.python.org/3/whatsnew/3.14.html].
- **Assuming a PEP 2026-style calendar-versioning jump** for future Python
  releases — that proposal was rejected; sequential 3.15, 3.16, ... numbering
  continues [Source: https://peps.python.org/pep-2026/].

## Security

Use the `secrets` module, not `random`, for anything security-sensitive
(tokens, passwords, keys); deserializing `pickle`/`shelve` data from
untrusted sources is explicitly flagged as dangerous (arbitrary code
execution risk); `subprocess` with `shell=True` carries shell-injection risk
[Source: https://docs.python.org/3/library/security_warnings.html].
Hardening flags for untrusted/security-sensitive execution: `-I` (isolated
mode — ignores `PYTHON*` env vars, excludes script-dir/user site-packages
from `sys.path`), `-P`/`PYTHONSAFEPATH` (omit the implicit current/script
directory from `sys.path`), `-E` (ignore `PYTHON*` env vars) [Source:
https://docs.python.org/3/using/cmdline.html]. `PYTHONHASHSEED` randomizes
hashing by default as a DoS mitigation against hash-collision attacks on
`dict`/`set`; fixing it (`PYTHONHASHSEED=0` or a constant) removes that
mitigation and is documented for debugging/reproducibility, not production
[Source: https://docs.python.org/3/using/cmdline.html]. Deep threat modeling
is owned by `security-engineering` (`SK-QA-002`), not restated here.

## Performance

`cProfile` (C-extension, low overhead, recommended) and `profile` (pure
Python, higher overhead) are the standard-library deterministic profilers,
post-processed via `pstats.Stats`; `timeit` is the documented tool for
benchmarking rather than profiling [Source:
https://docs.python.org/3/library/profile.html]. Free-threaded builds:
single-thread overhead is documented as roughly 1–8% (platform-dependent) at
3.13, narrowing to roughly 5–10% at 3.14 after the specializing adaptive
interpreter was enabled in free-threaded mode; they also use more memory
[Source: https://docs.python.org/3/howto/free-threading-python.html; Source:
https://docs.python.org/3/whatsnew/3.14.html]. Sub-interpreters via
`concurrent.interpreters`/`InterpreterPoolExecutor` (3.14+) are the
documented path to standard-library-level multi-core parallelism without a
free-threaded build [Source: https://docs.python.org/3/whatsnew/3.14.html].
An opt-in tail-call interpreter build (`--with-tail-call-interp`, 3.14,
requires Clang 19+ on x86-64/AArch64) measures "a geometric mean of 3-5%
faster" on the pyperformance suite [Source:
https://docs.python.org/3/whatsnew/3.14.html]. Deep performance method is
owned by `performance-engineering` (`SK-QA-003`).

## Testing

`unittest` (xUnit-style `TestCase` subclasses, a rich `assert*` family,
`setUp`/`tearDown`/`setUpClass`/`setUpModule` fixtures, `addCleanup()`,
`enterContext()`/`enterAsyncContext()` for context-manager fixtures,
`subTest()` for reporting every failing loop iteration) is Python's own
first-party, standard-library testing framework — the equivalent of
Express's gap being that Fastify has an official in-process test primitive
and Express doesn't: here Python *does* ship an official framework, but it is
`unittest`, not the third-party `pytest` that most of the ecosystem actually
uses day to day. `docs.python.org` does not document `pytest` (or
`nose2`/`hypothesis`) at all — that is explicitly out of this project's
official-docs sourcing scope, so `pytest`-specific guidance needs separate,
pytest-official-doc-grounded research, not this skill [Source:
https://docs.python.org/3/library/unittest.html]. `IsolatedAsyncioTestCase`
is the documented path for testing `async def` test methods under
`unittest`. Deep test-strategy method is owned by `testing-strategy`
(`SK-QA-001`).

## Failure handling

- If the Python version (and, for GC-behavior questions, the patch version)
  cannot be determined, ask for it or explicitly state the version the
  guidance assumes — never assume "latest" silently (rule VA-3).
- If shell is unavailable or denied, degrade to advisory code/config output
  and state that python/pip/venv/profiler commands were not actually run.
- If it is unknown whether third-party C-extension dependencies are
  free-threading-compatible, do not recommend a free-threaded build without
  flagging that audit as a prerequisite.

## Escalation

- Adopting a free-threaded build in an existing production service is a
  significant, hard-to-reverse-cheaply decision (requires a C-extension
  compatibility audit) — present the trade-offs and require explicit
  confirmation before applying it.
- Pinning `PYTHONHASHSEED` or disabling isolation flags (`-I`/`-P`/`-E`) in
  production removes a documented security mitigation — confirm explicitly
  before recommending.

## Outputs & verification

- **Outputs:** version-correct Python code or packaging config
  (`pyproject.toml`), a concurrency-model or version-upgrade analysis with
  the version/patch range it applies to, and any diagnostic commands run.
- **Verify:** GIL/free-threading claims are tagged with the exact version
  (and patch, where GC is involved); the concurrency-model choice matches the
  workload shape (I/O-bound vs. CPU-bound) rather than a default; exception
  handling uses explicit or documented-implicit chaining rather than
  swallowing the original error; packaging changes produce a valid
  `pyproject.toml` or document why an existing `setup.py`/`requirements.txt`
  approach is intentionally retained.

## References

- Source list: see `skill.yaml.source_references` (Python official docs,
  `peps.python.org`, and `packaging.python.org`, retrieved 2026-09-10, via
  `research/technologies/python.md`).
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md) — the Python version-gate table this skill's `version_sensitive_claims` mirror.
- [backend-architecture](../backend-architecture/SKILL.md) (`SK-BE-001`) — the generic backend-structure parent skill.
