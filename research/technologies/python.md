# Python — Technology Research

Research date: 2026-09-09. Primary source: `docs.python.org/3/*` (canonical documentation host — confirmed reachable and current at time of research; the docs landing page for the stable branch showed "Python 3.14.7 ... Last updated September 8, 2026"). Supplementary official sources used where docs.python.org itself doesn't cover a topic: `peps.python.org` (the canonical host for Python Enhancement Proposals, an official python.org-family site), `devguide.python.org` (the official CPython developer/release-process guide), and `packaging.python.org` (maintained by the Python Packaging Authority, PyPA — a PSF-affiliated working group, but organizationally and editorially separate from the core `docs.python.org` documentation; treated here as official but noted explicitly wherever that distinction matters). All claims are tagged per this project's convention: `[Source: <url>]` for documented facts, `[Inference, not confirmed in docs]` for reasoning, "Not documented / could not verify" where docs did not cover something, and "Unresolved: ..." where confidence is genuinely low.

**Doc host note**: [Source: https://docs.python.org/3/] No canonical doc-host migration was found — `docs.python.org` remains the primary documentation host, versioned per release (`docs.python.org/3.14/...`, `docs.python.org/3.10/...`, etc., with `docs.python.org/3/` aliasing to the current stable branch). [Source: https://peps.python.org/pep-2026/] Notably, a 2025-era proposal (PEP 2026, "Calendar versioning for Python") to rename the numbering scheme itself — which would have changed the next release from "3.15" to "3.26" and, by extension, reshaped doc URL versioning — was **rejected** by the Python Steering Council, so the sequential `3.15`, `3.16`, ... scheme continues unchanged. This is called out because a technology researcher revisiting this file after October 2026 should not be surprised the numbering didn't jump.

---

## 1. Core concepts

[Source: https://docs.python.org/3/reference/datamodel.html] Python's data model defines every value in a running program as an **object**: "Every object has an identity, a type and a value. An object's *identity* never changes once it has been created; you may think of it as the object's address in memory." Identity is compared with `is` / `id()`; type is fixed and returned by `type()`; value may be mutable or immutable depending on the type. "Objects whose value can change are said to be *mutable*; objects whose value is unchangeable once they are created are called *immutable*."

[Source: https://docs.python.org/3/reference/datamodel.html] The standard type hierarchy documents: `None`, `NotImplemented`, `Ellipsis` as singletons; numeric types `int`/`bool`/`float`/`complex` (all immutable); sequences (`str`, `tuple`, `bytes` immutable; `list`, `bytearray` mutable); `set` (mutable) / `frozenset` (immutable); `dict` (mutable, documented as insertion-ordered since 3.7); callables (functions, methods, classes); and modules (namespaces backed by dictionaries).

[Source: https://docs.python.org/3/reference/datamodel.html] **Special methods** ("dunder" methods) are Python's mechanism for operator overloading and protocol implementation: attribute access (`__getattr__`/`__setattr__`), container emulation (`__getitem__`/`__len__`/`__iter__`/`__contains__`), descriptors (`__get__`/`__set__`/`__delete__` — data descriptors define `__get__` plus `__set__`/`__delete__`; non-data descriptors define only `__get__`), lifecycle (`__init__`/`__new__`/`__del__`), and callables (`__call__`). "Setting a special method to `None` indicates that the corresponding operation is not available." Class attribute lookup is dictionary-based: "Class attribute references are translated to lookups in this dictionary, e.g., `C.x` is translated to `C.__dict__["x"]`."

[Source: https://docs.python.org/3/glossary.html#term-EAFP] The glossary formally names Python's idiomatic error-handling style as **EAFP** ("Easier to Ask Forgiveness than Permission" — try the operation and catch the exception) and contrasts it with **LBYL** ("Look Before You Leap" — explicit pre-condition checks), noting EAFP is the more common Python style.

[Source: https://docs.python.org/3/glossary.html#term-global-interpreter-lock] The **Global Interpreter Lock (GIL)** is "the mechanism used by the CPython interpreter to assure that only one thread executes Python bytecode at a time," which "simplifies the CPython implementation by making the object model ... implicitly safe against concurrent access ... at the expense of much of the parallelism afforded by multi-processor machines." The GIL is released during I/O and by some standard/third-party extensions during heavy computation (e.g. compression, hashing). [Version-sensitive] As of Python 3.13, the GIL can be disabled at build time (`--disable-gil`) and toggled at runtime via `-X gil=0` or `PYTHON_GIL=0`, per PEP 703 — see Sections 2, 8, and 14.

[Source: https://docs.python.org/3/library/exceptions.html] All exceptions derive from `BaseException`; user code should subclass `Exception` (or its subclasses), not `BaseException` directly. Exception chaining is a documented, first-class concept: implicit chaining sets `__context__` automatically when an exception is raised inside an `except`/`finally`/`with` block; explicit chaining via `raise NewException(...) from original` sets `__cause__`; `raise ... from None` sets `__suppress_context__ = True` to hide the original. `__notes__` (a list, mutable via `BaseException.add_note()`) was [Version-sensitive] added in Python 3.11.

[Source: https://docs.python.org/3/reference/import.html] Python's **import system** is a core language concept, not an incidental feature: a module is "an object that serves as an organizational unit of Python code," and a package is specifically "any module that contains a `__path__` attribute" — "all packages are modules, but not all modules are packages." Namespace packages (no `__init__.py` required, spanning multiple directories) are a documented alternative to regular packages, per PEP 420.

---

## 2. Architecture

[Source: https://docs.python.org/3/glossary.html#term-CPython] **CPython** is documented as "the canonical implementation of the Python programming language" — the reference implementation this research targets. [Inference, not confirmed in docs] The glossary's phrasing implies other implementations exist (the docs elsewhere reference Jython/IronPython/PyPy in older FAQ material), but this research pass did not locate a current docs.python.org page comparing implementations, so alternative-implementation coverage should be treated as "Not documented / could not verify" within this pass.

[Source: https://docs.python.org/3/reference/import.html] The import pipeline is: check `sys.modules` (the import cache) first — "If the module name is in `sys.modules`, that cached module is used"; if absent, `sys.meta_path` finders are consulted (meta path hooks run first), then the path-based finder searches `sys.path` entries; a successful finder returns a **module spec**, which a **loader** executes via `exec_module()` to populate the module's namespace; the result is cached back into `sys.modules`. Compiled bytecode is cached in `__pycache__/*.pyc`, invalidated either by source timestamp+size or (since 3.7) by a hash of the source contents, in "checked" or "unchecked" hash-based variants.

[Source: https://docs.python.org/3/glossary.html#term-global-interpreter-lock] Threading architecture in standard CPython centers on the single GIL described in Section 1. [Version-sensitive, Source: https://docs.python.org/3/whatsnew/3.12.html] Python 3.12 (PEP 684) gave **sub-interpreters their own, independent GIL** ("per-interpreter GIL"), enabling true parallelism between interpreters within one process at the C-API level (`Py_NewInterpreterFromConfig` with `PyInterpreterConfig_OWN_GIL`). [Version-sensitive, Source: https://docs.python.org/3/whatsnew/3.14.html] Python 3.14 (PEP 734) exposed this at the **standard-library level** via the new `concurrent.interpreters` module, described as enabling "a new (to Python), human-friendly concurrency model" with "true multi-core parallelism," plus `concurrent.futures.InterpreterPoolExecutor`.

[Version-sensitive, Source: https://docs.python.org/3/howto/free-threading-python.html] **Free-threaded ("no-GIL") CPython**, per PEP 703, removes the single global lock in favor of biased/deferred reference counting, object immortalization, per-object locking, and the mimalloc allocator. [Source: https://peps.python.org/pep-0703/] PEP 703 was **accepted as Final by the Python Steering Council on 2023-10-24**, explicitly with a gradual, reversible rollout plan. [Version-sensitive] Introduced experimentally in Python 3.13 (build with `--disable-gil`, binary typically named `python3.13t`); [Source: https://docs.python.org/3/whatsnew/3.14.html] "officially supported" as of Python 3.14 (PEP 779), with the specializing adaptive interpreter now also enabled in free-threaded mode and single-threaded overhead reduced to roughly 5–10%.

[Source: https://docs.python.org/3/whatsnew/3.14.html] Python 3.14 also introduces an alternate **"tail-call" interpreter loop** — "a new type of interpreter ... uses tail calls between small C functions," opt-in via `--with-tail-call-interp` (requires Clang 19+ on x86-64/AArch64), with preliminary benchmarks showing "a geometric mean of 3-5% faster" on the pyperformance suite.

[Source: https://docs.python.org/3/whatsnew/3.14.html] An **experimental JIT compiler** exists in CPython (introduced experimentally in 3.13 per PEP 744, see Section 8); [Version-sensitive] as of 3.14, official macOS and Windows binary releases include the experimental JIT.

[Source: https://docs.python.org/3/extending/extending.html] At the extension boundary, CPython's C API centers on `Python.h`, `PyObject*` reference-counted objects (`Py_INCREF`/`Py_DECREF`), module-definition structs (`PyModuleDef`) with `PyModuleDef_Slot` multi-phase initialization, and a documented **Limited API / stable ABI** (`Py_LIMITED_API`) that lets an extension compiled against one Python version load on newer versions without recompilation.

---

## 3. APIs

[Source: https://docs.python.org/3/library/index.html] The **Python Standard Library** ("Library Reference") is Python's primary first-party API surface — hundreds of modules covering text processing, data types, numeric/math, file/directory access, persistence, compression, file formats, cryptographic services (`hashlib`, `hmac`, `secrets`), OS services, concurrency (`threading`, `multiprocessing`, `asyncio`, `concurrent.futures`, and — new in 3.14 — `concurrent.interpreters`), networking (`socket`, `ssl`, `http`, `urllib`), internet data handling, structured markup (`xml`, `html`), internationalization, program frameworks, GUI (`tkinter`), development tools (`unittest`, `pdb`, `typing`), debugging/profiling, and C-level interfaces (`ctypes`).

[Source: https://docs.python.org/3/library/typing.html] The **`typing` module** (PEP 484) is the standard-library API for static type hints: `TypeVar`, `Generic`, `ParamSpec`, `TypeVarTuple`, `Protocol` (structural/duck typing, PEP 544), `TypedDict`, `NamedTuple`, `Union`/`X | Y`, `Literal`, `Any`, `Self`, `Annotated`, `NewType`, `overload`, `TypeGuard`/`TypeIs`. Explicitly documented: type hints are **not enforced at runtime** by the interpreter — `x: int = "string"` raises no error; enforcement is left to third-party static checkers, IDEs, and linters. [Version-sensitive] PEP 695's compact generic syntax (`class C[T]:`, `def f[T](x: T) -> T:`, the `type` statement for aliases) was added in Python 3.12; `TypeIs` in 3.13; the older `TypeVar`-object-based generic syntax remains supported but PEP 695 syntax is the modern preferred form.

[Source: https://docs.python.org/3/library/asyncio.html] **`asyncio`** is the standard-library API for single-threaded, event-loop-based concurrent I/O using `async`/`await`: an event loop drives coroutines, `Task`s, and `Future`s cooperatively (tasks yield control at `await` points; this is concurrency, not OS-thread parallelism, so it does not contend with the GIL the way threading does). [Version-sensitive, Source: https://docs.python.org/3/whatsnew/3.14.html] Python 3.14 added an asyncio introspection CLI (`python -m asyncio ps PID` / `pstree PID`) and `capture_call_graph()`/`print_call_graph()`.

[Source: https://docs.python.org/3/extending/extending.html] The **C API** (`Python.h`, documented fully under `/3/c-api/`) is the API surface for writing extension modules and embedding the interpreter in a host C/C++ application; `PyArg_ParseTuple()`/`PyArg_ParseTupleAndKeywords()` convert Python call arguments to C values, `Py_BuildValue()` constructs return values, and Capsules (`PyCapsule_New`/`PyCapsule_Import`) expose a C-level API from one extension module to another.

[Source: https://docs.python.org/3/library/unittest.html] **`unittest`** (`TestCase`, assertion methods, fixtures, test discovery) is the standard-library testing API — see Section 9.

---

## 4. Configuration

[Source: https://docs.python.org/3/library/venv.html] The **`venv`** module (standard library since 3.3) creates isolated virtual environments, each with its own interpreter/`site-packages`; activation modifies `sys.prefix`/`sys.exec_prefix` relative to `sys.base_prefix`. Documented options include `--system-site-packages`, `--symlinks`/`--copies`, `--upgrade-deps`, `--without-pip`. The docs explicitly state environments are **not portable** (recreate rather than move them) and should not be committed to source control.

[Source: https://docs.python.org/3/using/cmdline.html] Runtime configuration is primarily via **command-line flags** and **`PYTHON*` environment variables**, with flags taking precedence on conflict. Documented flags include `-I` (isolated mode: ignores `PYTHON*` env vars, excludes script dir/user site-packages from `sys.path`), `-P` (safe-path: omits the implicit current/script directory from `sys.path`; `-I` implies `-E`, `-P`, `-s`), `-O`/`-OO` (drop asserts / drop asserts+docstrings, per PEP 488), `-X dev` (Development Mode — extra runtime checks), `-X importtime`, `-X tracemalloc=NFRAME`, `-X perf`/`-X perf_jit` (Linux `perf` integration), `-X gil=0/1` (free-threaded builds), `-B` (no `.pyc` writes), `-u` (unbuffered stdio), `-E` (ignore `PYTHON*` vars), `-W` (warning filters). Key environment variables: `PYTHONPATH`, `PYTHONHOME`, `PYTHONSAFEPATH` (`-P` equivalent), `PYTHONDONTWRITEBYTECODE`, `PYTHONPYCACHEPREFIX`, `PYTHONOPTIMIZE`, `PYTHONHASHSEED` (hash randomization control — `0` to disable, an integer for a fixed seed, default random-per-process), `PYTHONWARNINGS`, `PYTHONUNBUFFERED`, `PYTHONBREAKPOINT` (controls what `breakpoint()` invokes — `pdb.set_trace` by default, `0` disables it), `PYTHONPROFILEIMPORTTIME`, and `PYTHON_GIL`.

[Source: https://packaging.python.org/en/latest/tutorials/packaging-projects/] Project/build configuration is standardized around **`pyproject.toml`**: a `[build-system]` table (`requires`, `build-backend`) selects the build backend (Hatchling, Setuptools, Flit, PDM, uv-build all named as options), and a `[project]` table holds metadata (name, version, dependencies, Python-version constraints, classifiers). [Inference, not confirmed in docs] This guide is PyPA-maintained rather than authored by the core `docs.python.org` team — see the header note above on that distinction — but is the closest thing to an official packaging-configuration reference for the ecosystem.

[Source: https://docs.python.org/3/reference/datamodel.html] Not strictly "configuration" but adjacent: [Inference, not confirmed in docs] class-level configuration hooks like `__slots__`, metaclasses, and `__init_subclass__` exist in the data model but were not deep-dived in this research pass — flagged as an area for a future, more targeted pass if a skill needs it.

---

## 5. Recommended patterns

[Source: https://peps.python.org/pep-0008/] **PEP 8**, "Style Guide for Python Code," is the canonical style guide for the standard library and widely adopted for Python code generally: 4-space indentation, ~79-character line length guidance, naming conventions (`snake_case` functions/variables, `PascalCase` classes, `UPPER_CASE` constants), and general readability-over-cleverness guidance. [Inference, not confirmed in docs] PEP 8 predates and is separate from `docs.python.org`'s Library/Language Reference but is published on the official `peps.python.org` host maintained by the CPython project.

[Source: https://docs.python.org/3/glossary.html#term-EAFP] EAFP (try/except around the risky operation) is documented as the idiomatic Python error-handling style, contrasted with LBYL pre-checks — see Section 1.

[Source: https://docs.python.org/3/library/exceptions.html] Exception chaining (`raise ... from ...`, or letting implicit `__context__` chaining occur) is the documented pattern for converting/wrapping exceptions without losing the original cause; `raise ... from None` is the documented way to deliberately suppress an uninteresting original context.

[Source: https://docs.python.org/3/library/unittest.html] For tests: subclass `TestCase`, use the rich `assert*` family (`assertEqual`, `assertRaises` as a context manager, `assertLogs`, etc.), use `setUp`/`tearDown` or `addCleanup`/`enterContext` (3.11+) for fixtures, and use `subTest()` to report multiple failures within one test method instead of stopping at the first. See Section 9 for the full pattern set.

[Source: https://docs.python.org/3/howto/logging.html#logging-cookbook] and [https://docs.python.org/3/library/logging.html] The documented logging pattern is a **module-level logger named via `logging.getLogger(__name__)`**, with handlers attached at the **root logger** and messages reaching handlers via propagation up the logger hierarchy, rather than attaching handlers to every individual logger.

[Source: https://docs.python.org/3/library/venv.html] Isolate project dependencies per-project via `venv` rather than installing packages into a shared/system interpreter — the documented default workflow.

[Source: https://docs.python.org/3/library/doctest.html] Embedding runnable, verified examples directly in docstrings (`>>>` prompts, checked via `doctest.testmod()`) is a documented pattern for keeping usage documentation synchronized with actual behavior.

---

## 6. Anti-patterns

[Inference, not confirmed in docs] Similar to other reference-manual-style projects, `docs.python.org`'s core reference material is prescriptive rather than an explicit "anti-patterns" catalog. Python did historically ship a dedicated "Idioms and Anti-Idioms in Python" HOWTO (`howto/doanddont.html`, covering bare `except:`, wildcard `from module import *`, and similar) in older doc versions (confirmed present through the 3.1 docs series); [Unresolved: whether this page still exists in the current 3.14 documentation tree] — a direct fetch of `docs.python.org/3/howto/doanddont.html` during this research pass returned only the generic documentation landing page rather than the anti-idioms content, which is consistent with the page having been removed from the current HOWTO index, but this research pass could not conclusively confirm removal vs. a fetch-tooling artifact. Treat any specific "the anti-idioms HOWTO says X" claim about the *current* docs as unverified; the anti-patterns below are instead drawn from other, currently-live official pages.

[Source: https://docs.python.org/3/library/exceptions.html] Bare `except:` (or `except BaseException:`) that swallows everything including `SystemExit`/`KeyboardInterrupt`/`GeneratorExit` is discouraged by the documented exception hierarchy design — those three are intentionally direct `BaseException` subclasses (not `Exception` subclasses) specifically so that ordinary `except Exception:` handlers do *not* accidentally catch them.

[Source: https://docs.python.org/3/library/security_warnings.html] Using `random` for anything security-sensitive (tokens, passwords, keys) is explicitly discouraged in favor of the `secrets` module. Using `pickle`/`shelve` to deserialize data from untrusted sources is explicitly flagged as dangerous. Using `tempfile.mktemp()` is documented as vulnerable to a race condition (superseded by `NamedTemporaryFile`/`mkstemp`).

[Source: https://docs.python.org/3/whatsnew/3.12.html] Depending on `distutils` is now an anti-pattern by removal: `distutils` was deleted from the standard library in Python 3.12 (PEP 632); the documented migration path is `setuptools`. [Version-sensitive: 3.12+]

[Source: https://docs.python.org/3/library/security_warnings.html] `logging`'s configuration-via-dictionary/`fileConfig` path uses `eval()` internally for some values, which the docs flag as a security consideration if configuration is loaded from an untrusted source.

[Source: https://docs.python.org/3/library/2to3.html and https://docs.python.org/3/whatsnew/3.13.html] Relying on the `2to3`/`lib2to3` tool for Python-2-to-3 porting is now moot: [Version-sensitive] both were **removed** in Python 3.13, and the dedicated `pyporting.html` HOWTO guide was itself discontinued as of Python 3.11 (an archived copy remains only in the 3.10 docs branch) — see Section 11.

---

## 7. Security

[Source: https://docs.python.org/3/library/security_warnings.html] Official security guidance is centralized on a dedicated "Security Considerations" reference page, cross-linking module-level warnings: `pickle`/`shelve` (arbitrary code execution risk on untrusted input — "restrict globals" if processing untrusted pickles), `xml`/`xml.etree.ElementTree` (XML entity-expansion/XXE-class vulnerabilities), `subprocess` (shell-injection risk, esp. `shell=True`), `ssl` (TLS/certificate-verification considerations), `hashlib` (constructors take a `usedforsecurity` keyword-only flag to gate known-insecure/blocked algorithms), `random` (not cryptographically secure — use `secrets`), `tempfile` (`mktemp()` race condition, deprecated), `http.server` (explicitly "not suitable for production use; only implements basic security checks"), `zipfile` (maliciously crafted archives can cause disk-exhaustion "zip bomb" conditions), `multiprocessing` (`Connection.recv()` uses pickle internally, inheriting pickle's deserialization risk).

[Source: https://docs.python.org/3/using/cmdline.html] Hardening flags for running untrusted or security-sensitive code: `-I` (isolated mode — ignores `PYTHON*` env vars and excludes script-directory/user site-packages from `sys.path`), `-P` / `PYTHONSAFEPATH` (omit the implicit current-working/script directory from `sys.path`, closing a common local-file-injection vector), `-E` (ignore `PYTHON*` environment variables).

[Source: https://docs.python.org/3/glossary.html#term-global-interpreter-lock and https://docs.python.org/3/using/cmdline.html] `PYTHONHASHSEED` controls hash randomization (a security mitigation against hash-collision denial-of-service attacks on `dict`/`set`); the documented default is a random seed per process, with `PYTHONHASHSEED=0` disabling randomization (documented as intended for debugging/reproducibility, not production).

Not documented / could not verify in this pass: a single consolidated "how CPython/PSF handles and discloses CVEs" page under `docs.python.org` itself — the Python Security Response Team's process lives on `python.org`/`devguide.python.org` security pages, which were not deep-fetched in this research pass. [Unresolved: exact current URL and disclosure-timeline process for the PSF/PSRT vulnerability-reporting workflow.]

---

## 8. Performance

[Source: https://docs.python.org/3/library/profile.html] **`cProfile`** (C-extension, low overhead, recommended) and **`profile`** (pure Python, higher overhead, easier to extend) are the standard-library deterministic profilers; output columns are `ncalls`/`tottime`/`percall`/`cumtime`/`percall`, post-processed via `pstats.Stats` (`sort_stats`, `print_stats`, `print_callers`/`print_callees`). The docs explicitly distinguish profiling (execution analysis) from benchmarking, pointing to `timeit` for the latter. [Version-sensitive, Source: https://docs.python.org/3/library/profile.html] `cProfile.Profile` gained context-manager support (`with cProfile.Profile(): ...`) in 3.8; `pstats.Stats.get_stats_profile()` was added in 3.9.

[Source: https://docs.python.org/3/howto/perf_profiling.html] [Version-sensitive: Python 3.12+] CPython can interoperate with the Linux **`perf`** profiler so Python-level function names (not just native C symbols) appear in `perf` output, enabled via `sys.activate_stack_trampoline("perf")`, the `-X perf` / `-X perf_jit` flags, or `PYTHONPERFSUPPORT=1`; frame-pointer-preserving builds (`-fno-omit-frame-pointer`) are recommended for best results, and non-frame-pointer builds require `perf` ≥ 6.8 plus a `perf inject --jit` post-processing step.

[Source: https://docs.python.org/3/whatsnew/3.12.html] Python 3.12 introduced **`sys.monitoring`** (PEP 669), a documented low-overhead event-monitoring API purpose-built so debuggers/profilers/coverage tools no longer need `sys.settrace()`'s much higher overhead.

[Source: https://docs.python.org/3/whatsnew/3.12.html] Documented 3.12 performance changes: comprehensions (list/dict/set) are now inlined rather than compiled as separate function objects (PEP 709) — "roughly 2x faster," with the side effect that comprehension scopes are no longer isolated from `locals()`/tracebacks the way they were; `isinstance()` checks against `typing.Protocol` classes are "2-20x faster"; `asyncio` gained up to a documented "75%" speedup in some operations; `super()` calls compile to a dedicated `LOAD_SUPER_ATTR` bytecode instruction.

[Source: https://docs.python.org/3/whatsnew/3.13.html] Python 3.13 added an **experimental JIT compiler** (PEP 744; build with `--enable-experimental-jit`; tiered — specialized bytecode → "uops" IR → machine code via copy-and-patch) described as giving "modest" gains expected to grow in later releases, off by default, and free-threaded builds (PEP 703, experimental in 3.13) with a documented single-threaded performance penalty.

[Source: https://docs.python.org/3/howto/free-threading-python.html and https://docs.python.org/3/whatsnew/3.14.html] [Version-sensitive] Free-threaded-build single-thread overhead: documented as roughly **1–8%** depending on platform/workload in the free-threading HOWTO (as low as ~1% on macOS aarch64, up to ~8% on x86-64 Linux) as of 3.13; the 3.14 What's New narrows this to "roughly 5-10%" after the specializing adaptive interpreter was enabled in free-threaded mode. Free-threaded builds also use **more memory** (larger non-GC object headers, immortal interned strings, mimalloc overhead, deferred/QSBR-based reclamation) — `gc.collect()` is documented as a way to force cross-thread refcount merging and QSBR-deferred frees.

[Source: https://docs.python.org/3/whatsnew/3.14.html] Python 3.14's opt-in **tail-call interpreter** is documented at "a geometric mean of 3-5% faster" on the pyperformance suite (build flag `--with-tail-call-interp`).

---

## 9. Testing

[Source: https://docs.python.org/3/library/unittest.html] **`unittest`** (xUnit-style) is the standard-library testing framework: `TestCase` subclasses with `test*`-prefixed methods, a rich `assert*` family (`assertEqual`, `assertTrue`/`assertFalse`, `assertIs`/`assertIsNot`, `assertIn`, `assertRaises`/`assertRaisesRegex` (usable as context managers), `assertWarns`, `assertLogs`/`assertNoLogs` (3.10+), `assertAlmostEqual`), fixtures at the method (`setUp`/`tearDown`), class (`setUpClass`/`tearDownClass`, 3.2+), and module (`setUpModule`/`tearDownModule`) levels, plus `addCleanup()` (LIFO cleanup queue, 3.1+) and `enterContext()`/`enterAsyncContext()` (3.11+) for context-manager-based fixtures. `subTest()` (3.4+) reports every failing iteration of a loop instead of stopping at the first. Test discovery: `python -m unittest discover [-s dir] [-p pattern]`. [Version-sensitive] `--durations N` (slowest-N report) added 3.12; `assertIsSubclass`/`assertStartsWith`/`assertEndsWith`/`assertHasAttr` and colorized output by default added 3.14.

[Source: https://docs.python.org/3/library/unittest.html] `IsolatedAsyncioTestCase` (3.8+) is the documented path for testing `async def` test methods under `unittest`.

[Source: https://docs.python.org/3/library/doctest.html] **`doctest`** extracts and executes `>>>`-prompted interactive examples embedded in docstrings/text files and checks actual output against the expected output shown, serving simultaneously as regression tests and living documentation; run via `doctest.testmod()`/`testfile()` or `python -m doctest`.

Not documented / could not verify: `docs.python.org` does not document third-party test runners/frameworks (pytest, nose2, hypothesis) — those are outside official-docs scope per this project's sourcing rules, so any skill built on this research should treat pytest-specific guidance as needing separate, pytest-official-doc-grounded research, not this file.

---

## 10. Deployment

[Source: https://docs.python.org/3/using/unix.html] On Unix, Python is documented as typically pre-installed or available via the system package manager; distribution-specific pointers are given for Debian/Fedora/OpenSUSE/Slackware/FreeBSD/OpenBSD. Building from source uses the conventional `./configure && make`, but the docs give an explicit, load-bearing deployment warning: use **`make altinstall`**, not `make install`, when building an additional/custom Python from source — plain `make install` can overwrite the system's default `python3` binary, while `altinstall` only installs the version-suffixed binary (e.g. `python3.14`).

[Source: https://packaging.python.org/en/latest/tutorials/packaging-projects/] For distributing Python *code* (as opposed to the interpreter itself), the documented PyPA workflow is: declare metadata and a build backend in `pyproject.toml`; run the `build` tool to produce a source distribution (`.tar.gz`) and a wheel (`.whl`) into `dist/`; upload with `twine`, recommended first against TestPyPI before the production Python Package Index, using API-token authentication.

[Source: https://docs.python.org/3/library/venv.html] For application-level environment reproducibility, the documented mechanism is `venv` plus a `pip`-installable requirements/dependency list; environments themselves are explicitly non-portable and meant to be recreated, not copied between machines.

[Source: https://docs.python.org/3/whatsnew/3.14.html and https://docs.python.org/3/whatsnew/3.13.html] [Version-sensitive] Mobile/alternative-platform deployment gained official tiers recently: iOS support (Tier 3, PEP 730) and Android support (Tier 3, PEP 738) landed in Python 3.13; Python 3.14 added official Android *binary releases* and Emscripten Tier 3 support (PEP 776), while `wasm32-emscripten` lost its earlier tier-2-ish standing per the 3.13 notes (no longer "officially supported" as of 3.13, per that release's notes) before Emscripten was re-elevated to Tier 3 in 3.14.

Not documented / could not verify: `docs.python.org` does not document how to produce a single-file standalone executable (the PyInstaller/cx_Freeze/Nuitka/shiv space) — this is left entirely to third-party tooling and is out of scope for official-docs-only citation here. Similarly, official first-party Docker-image guidance for Python deployment was not located under `docs.python.org` in this pass (the widely used `python` image on Docker Hub is a Docker Official Image, not `docs.python.org`-authored content) — [Inference, not confirmed in docs] structurally analogous to the PostgreSQL container-deployment gap noted in this project's PostgreSQL research file.

---

## 11. Migration

[Source: https://docs.python.org/3/whatsnew/index.html] Each major/minor release ships a dedicated **"What's New"** document (e.g. `whatsnew/3.14.html`) that is the documented, official mechanism for tracking behavior changes, new features, deprecations, and removals between versions — this is the primary "migration guide" artifact `docs.python.org` provides for upgrading between Python versions, rather than a single generic "how to migrate" page.

[Source: https://docs.python.org/3/deprecations/index.html] A dedicated, forward-looking **Deprecations** index tracks pending removals *by future version number* (e.g., what's slated for removal in 3.15, 3.16, 3.17, 3.18, 3.19, and an "unscheduled" bucket), separately for pure-Python-visible deprecations and C-API deprecations — see Section 13 for specifics.

[Source: https://docs.python.org/3/howto/pyporting.html] The Python-2-to-3 porting HOWTO is explicitly **discontinued**: "[Version-sensitive] The original comprehensive porting guide was discontinued as of Python 3.11," with only an archived copy remaining under the Python 3.10 docs branch (`docs.python.org/3.10/howto/pyporting.html`); the current page instead points to third-party resources (a Fedora porting guide, a PyCon talk, community blog posts) and to the still-live `cporting.html` guide specifically for **porting C extension modules** to Python 3.

[Source: https://docs.python.org/3/whatsnew/3.13.html] [Version-sensitive] The `2to3` tool and `lib2to3` module (the primary automated Python-2→3 source-rewriting tool) were themselves **removed in Python 3.13**, after being deprecated since 3.11 — meaning current-generation Python no longer ships first-party automated 2-to-3 porting tooling at all.

[Source: https://docs.python.org/3/extending/cporting.html] For C-extension authors, `cporting.html` ("Porting Extension Modules to Python 3") remains the documented reference for adapting extension-module C code across the Python 2/3 boundary and, by extension, across API-level changes between 3.x releases. [Inference, not confirmed in docs] This page was referenced but not deep-fetched in this pass; its exact current content for 3.x→3.(x+1) porting (as opposed to 2→3) was not verified.

[Source: https://docs.python.org/3/whatsnew/3.12.html] For major-version migrations with concrete removed dependencies: the `distutils` removal (3.12, PEP 632) is documented with an explicit migration target (`setuptools`).

---

## 12. Version information

[Source: https://docs.python.org/3/] Current stable release as of this research (2026-09-09): **Python 3.14.7** (per the docs landing page's "Last updated September 8, 2026" stamp under the `/3/` current-stable alias).

[Source: https://devguide.python.org/versions/] Supported-branch status table (fetched during this research pass):

| Branch | Status (at fetch time) | First release | End-of-life |
|---|---|---|---|
| main (3.16) | feature | 2027-10-06 (planned) | 2032-10 (planned) |
| 3.15 | prerelease | 2026-10-01 (planned) | 2031-10 (planned) |
| 3.14 | bugfix | 2025-10-07 | 2030-10 |
| 3.13 | bugfix | 2024-10-07 | 2029-10 |
| 3.12 | security | 2023-10-02 | 2028-10 |
| 3.11 | security | 2022-10-24 | 2027-10 |
| 3.10 | security | 2021-10-04 | 2026-10 |

[Unresolved: Python 3.9's row was not present in the fetched table excerpt — it is likely already past its documented end-of-life (its 5-year window from an October 2021... actually October 2020 release would place EOL around October 2025), i.e. already end-of-life as of this research date, but this was not directly re-confirmed against the live devguide table in this pass.]

[Source: https://docs.python.org/3/whatsnew/index.html and web search corroboration against `python.org/downloads`] **Python 3.15** was in **release-candidate stage** at research time (search results indicated an "rc1" then "rc2" cut around 2026-09-01), with **general availability expected around October 2026** — consistent with the annual-October cadence below.

[Source: https://devguide.python.org/versions/ and https://peps.python.org/pep-0602/] Release cadence is governed by **PEP 602** ("Annual Release Cycle for Python"), in effect since Python 3.9: a new feature (`X.Y.0`) release ships **every 12 months, in October**. Each branch's lifecycle (per the devguide's phase key): **feature** phase (pre-first-beta, new features land) → **prerelease** phase (beta/RC, no new features) → **bugfix** phase (binary bugfix releases "roughly every two months") → **security** phase (security-only fixes, source-only releases) → **end-of-life**, "five years after a release." [Version-sensitive] The bugfix→security transition point is documented as **2 years** post-release for 3.13 and later, versus **18 months** for releases before 3.13 — i.e., 3.10–3.12 got a shorter bugfix window than 3.13+ will, even though total support (5 years) is unchanged.

[Source: https://peps.python.org/pep-2026/] A 2025 proposal, **PEP 2026** ("Calendar versioning for Python"), would have replaced sequential minor-version numbers with a `3.YY` calendar-year scheme starting at what would have been 3.15 (i.e. "Python 3.26" shipping in 2026) specifically to make each version's 5-year EOL self-evident from its number. [Source: https://peps.python.org/pep-2026/] This PEP was **rejected** by the Steering Council, reportedly over ecosystem-compatibility concerns (wheel filenames and version-parsing code that assumes the existing scheme) — so the sequential numbering in the table above is confirmed to continue.

---

## 13. Breaking changes

[Version-sensitive: Python 3.12, Source: https://docs.python.org/3/whatsnew/3.12.html] `distutils` **removed** from the standard library (PEP 632; migrate to `setuptools`). Several "dead battery" modules deprecated in 3.11 remain scheduled/removed per PEP 594 (`aifc`, `audioop`, `cgi`, `cgitb`, `chunk`, `crypt`, `imghdr`, `mailcap`, `msilib`, `nis`, `nntplib`, `ossaudiodev`, `pipes`, `sndhdr`, `spwd`, `sunau`, `telnetlib`, `uu`, `xdrlib`). `asynchat`/`asyncore` and `imp` removed (use `asyncio` / `importlib`). C API: `wstr` removed from Unicode objects (PEP 623), shrinking `str` objects by 8+ bytes on 64-bit platforms — a C-extension-visible ABI change. `venv`-created environments no longer pre-install `setuptools`/`pip`'s legacy `easy_install`/`pkg_resources` by default.

[Version-sensitive: Python 3.13, Source: https://docs.python.org/3/whatsnew/3.13.html] **`2to3` and `lib2to3` removed** entirely. `tkinter.tix`, `locale.resetlocale()`, `typing.io`/`typing.re` namespaces removed. `wasm32-emscripten` dropped from officially-supported platform status (per that release's notes) even as `wasm32-wasi` was promoted to Tier 2. `locals()` mutation semantics were formally defined (PEP 667): in optimized scopes, `locals()` now returns an independent snapshot rather than a sometimes-live view, which is a documented, potentially code-breaking semantic tightening for code that relied on the old, under-specified behavior.

[Version-sensitive: Python 3.14, Source: https://docs.python.org/3/whatsnew/3.14.html] `int()` **no longer delegates to `__trunc__()`** — classes wanting to support `int()` conversion must implement `__int__()` or `__index__()` instead; code relying on `__trunc__`-only classes being `int()`-convertible breaks. Using `NotImplemented` in a boolean context now **raises `TypeError`** (previously only a `DeprecationWarning`, since 3.9). On Unix platforms other than macOS, **`ProcessPoolExecutor`'s default start method changed from `fork` to `forkserver`** — a behavior-affecting default for any code relying on fork semantics (e.g. implicit inheritance of open resources/global state) without having pinned a start method explicitly. `except`/`except*` syntax now permits omitting the parenthesized-tuple brackets when there's no `as` clause (additive, non-breaking). PGP signatures were **discontinued** for official release artifacts (PEP 761) — a supply-chain-verification workflow change for anyone who was validating releases via PGP.

[Source: https://docs.python.org/3/whatsnew/3.14.html] **Notable mid-cycle behavioral reversal, not tied to a clean version boundary**: "Python 3.14.0-3.14.4 shipped with a new incremental GC. However, due to a number of reports of significant memory pressure in production environments, it has been reverted back to the generational GC from 3.13" — i.e. this reversion happened within the 3.14 bugfix series itself (3.14.5+), not at a 3.x→3.(x+1) boundary. This is called out explicitly because it means "Python 3.14" alone is not a sufficiently precise version tag for GC-behavior-sensitive claims — the *patch* version matters here, an unusual level of version-sensitivity for this project's tagging convention to capture accurately.

[Source: https://docs.python.org/3/deprecations/index.html] Scheduled **future** breaking changes (pending-removal list, by target version): **3.15** — import-system `__cached__`/`__package__` attribute removal, `ctypes.SetPointerType()`, `http.server.CGIHTTPRequestHandler`/`--cgi`, `importlib`/`zipimport` `load_module()`, `pathlib.PurePath.is_reserved()`, `platform.java_ver()`, `threading.RLock()` losing its argument, `types.CodeType.co_lnotab`, `typing.NamedTuple` keyword syntax, `typing.TypedDict` functional syntax without fields, `wave.getmark()`/`setmark()`/`getmarkers()`. **3.16** — import-system `__loader__`, `array`'s `'u'` format code, `asyncio.iscoroutinefunction()` and the *entire* `asyncio` event-loop-policy system (`AbstractEventLoopPolicy`, `DefaultEventLoopPolicy`, `get_event_loop_policy()`, etc. — a substantial `asyncio` API-surface removal), `functools.reduce()` keyword arguments, `~True`/`~False` bitwise inversion on `bool`. **3.17+** — `collections.abc.ByteString`, `typing.ByteString`. C-API-side deprecations scheduled for **3.15** include `PyImport_ImportModuleNoBlock()`, `PyWeakref_GetObject()`/`PyWeakref_GET_OBJECT()`, `Py_UNICODE`/`Py_UNICODE_WIDE`, and several process-initialization/config functions (`Py_GetPath()`, `Py_SetProgramName()`, etc.).

---

## 14. Limitations

[Source: https://docs.python.org/3/library/sys.html#sys.setrecursionlimit] CPython enforces a **recursion depth limit** (`sys.getrecursionlimit()`/`setrecursionlimit()`) specifically "to prevent infinite recursion from causing an overflow of the C stack and crashing Python"; exceeding it raises `RecursionError`. The maximum settable value is documented as platform-dependent, and the docs warn that setting it "too high can lead to a crash" — i.e. the limit is a genuine, load-bearing safety constraint, not an arbitrary default to casually override.

[Source: https://docs.python.org/3/glossary.html#term-global-interpreter-lock] The GIL is a documented, longstanding limitation on true multi-core parallelism for standard (non-free-threaded) CPython threads — see Sections 1–2, 8 for the free-threading (PEP 703) mitigation path and its own new limitations (below).

[Source: https://docs.python.org/3/howto/free-threading-python.html] Free-threaded builds carry their own documented limitations: many third-party C extensions are **not yet compatible** and will cause the GIL to be silently (with a warning) re-enabled on import; accessing a frame's `f_locals` from a different thread is documented as **unsafe and can crash the interpreter**; built-in container iterators are **not thread-safe** for concurrent access (may yield duplicate or missing elements without an error); and immortalized objects (interned strings, certain code constants) **never get deallocated**, an intentional but memory-relevant limitation.

[Source: https://docs.python.org/3/using/cmdline.html and general C-API cross-reference] [Inference, not confirmed in docs] The `sys.set_int_max_str_digits()` limit (a documented guard against a specific quadratic-time int-to-string/string-to-int conversion denial-of-service class) exists in current Python but was not independently re-verified with a dedicated fetch in this research pass; flagged as **Unresolved: exact introducing version and current default digit limit** — should be re-confirmed against `docs.python.org/3/library/stdtypes.html#int-max-str-digits` before being cited as a hard fact in a downstream skill.

Not documented / could not verify: `docs.python.org` does not appear (in the pages fetched this pass) to publish a single consolidated "known limitations of CPython" page; limitations are instead scattered across `sys`, glossary, and HOWTO pages as documented above, requiring this kind of cross-referenced assembly rather than one canonical citation.

---

## 15. Debugging

[Source: https://docs.python.org/3/library/pdb.html] **`pdb`** is the standard-library interactive source debugger: invoked via the `breakpoint()` builtin (documented as the modern, preferred entry point, configurable via `PYTHONBREAKPOINT`), `import pdb; pdb.set_trace()`, `python -m pdb script.py`, or programmatically (`pdb.run()`, `pdb.runcall()`, `pdb.post_mortem()`, `pdb.pm()` for post-mortem debugging of the last exception). Core commands: `step`/`next`/`continue`/`return`/`break`/`tbreak`/`list`/`where`/`up`/`down`/`print`/`pp`/`quit`; conditional breakpoints (`break 10, x > 5`) and per-breakpoint command lists (`commands` ... `end`) are documented. A `.pdbrc` file provides persistent aliases. [Version-sensitive] `python -m pdb -p PID` **remote-attach to an already-running process** and convenience variables like `$_asynctask` were **added in Python 3.14**, implemented via the new `sys.remote_exec()` zero-overhead-attach mechanism (PEP 768) described in Section 2/16.

[Source: https://docs.python.org/3/library/pdb.html] The `Pdb` class supports a `backend` option (`'settrace'` vs `'monitoring'`), letting the debugger use the newer, lower-overhead `sys.monitoring` (PEP 669, 3.12+) event source instead of the classic `sys.settrace()` hook.

[Source: https://docs.python.org/3/whatsnew/3.14.html] **PEP 768**, "Safe External Debugger Interface for CPython," is documented as "a zero-overhead debugging interface that allows debuggers and profilers to safely attach to running Python processes without stopping or restarting them," exposed via `sys.remote_exec(pid, script_path)`. [Version-sensitive: 3.14]

[Source: https://docs.python.org/3/using/cmdline.html] `-X dev` (Development Mode) enables extra runtime checks (e.g. surfacing otherwise-silent `ResourceWarning`s and other debug-oriented behavior); `-X tracemalloc=NFRAME` and the `tracemalloc` module trace memory-allocation call stacks; `-X importtime`/`PYTHONPROFILEIMPORTTIME` profile per-module import cost; `faulthandler` dumps Python tracebacks on fatal crashes/timeouts/signals — referenced from the pdb docs as a related debugging tool.

---

## 16. Integration

[Source: https://docs.python.org/3/extending/extending.html] **C/C++ integration**: extension modules are written against `Python.h`, exposing functions via a `PyMethodDef` table and a `PyModuleDef`/`PyModuleDef_Slot` multi-phase-init struct, with `PyInit_<name>()` as the required module entry point; the same "Extending and Embedding" manual documents the reverse direction — **embedding** the CPython interpreter inside a larger C/C++ application. A documented **Limited API / stable ABI** (`Py_LIMITED_API`) lets a compiled extension target a minimum Python version (3.13+ in current guidance) and remain binary-compatible with newer Python releases without recompilation, easing integration for binary-distributed extensions.

[Source: https://docs.python.org/3/library/ctypes.html — referenced, not independently deep-fetched this pass] [Inference, not confirmed in docs] `ctypes` is the standard-library mechanism for calling into C shared libraries **without** writing a compiled C extension module — this is the documented lighter-weight alternative integration path to the full `Python.h` extension-module approach, but this specific page was not independently re-fetched in this research pass to pull exact quotes; flagged for a follow-up pass if a skill needs `ctypes`-specific detail.

[Source: https://docs.python.org/3/library/asyncio.html] `asyncio` documents integration points with OS-level asynchronous I/O (event loop policies historically abstracted platform selectors; see Section 13 for the policy system's scheduled 3.16 removal), subprocess management (`asyncio.subprocess`), and streams (`asyncio.streams`) for network-protocol integration.

[Source: https://docs.python.org/3/reference/import.html] The import system's **finder/loader hook architecture** (`sys.meta_path`, `importlib.abc.MetaPathFinder`/`Loader`) is the documented, official extension point for integrating custom module sources (e.g. loading modules from non-filesystem locations, zip archives, or network sources) into the standard `import` statement.

[Source: https://docs.python.org/3/library/logging.html] `logging` integrates with process-level shutdown via an auto-registered `atexit` handler (`logging.shutdown()`, flushing/closing all handlers) and is documented as thread-safe by default (a module-level lock plus a per-handler lock serialize concurrent access) — with the explicit caveat that logging is **not** safe to call from asynchronous signal handlers, since the underlying locks are not re-entrant/signal-safe.

---

## 17. Production considerations

[Source: https://docs.python.org/3/library/security_warnings.html] `http.server` is explicitly documented as **not suitable for production use** ("only implements basic security checks") — production HTTP serving is left to third-party WSGI/ASGI servers, which `docs.python.org` does not itself document (out of scope for this official-docs-only file).

[Source: https://docs.python.org/3/library/logging.html] Production logging guidance (drawn from the Logging HOWTO/Cookbook cross-references within the library docs): configure explicitly (`basicConfig()` is a no-op if handlers already exist unless `force=True`) and do so **from the main thread before spawning other threads**, to avoid a documented race-condition class in earlier-generation code; call `logging.shutdown()` (or rely on its auto-registered `atexit` hook) so buffered log handlers flush on exit; set `logging.raiseExceptions = False` in production so a logging-subsystem failure doesn't mask/crash the application it's instrumenting (errors instead surface via the `lastResort` stderr handler).

[Source: https://docs.python.org/3/using/cmdline.html] Documented environment/flag hardening and container-friendly defaults: `PYTHONDONTWRITEBYTECODE=1` (skip `.pyc` writes — commonly used in ephemeral container images), `PYTHONUNBUFFERED=1` (unbuffered stdout/stderr — important so container log collectors see output promptly rather than buffered), `PYTHONHASHSEED` left at its random default in production (fixing it removes a DoS mitigation), and `-I`/`PYTHONSAFEPATH`/`-E` for isolating a production process from ambient environment/path influence.

[Source: https://docs.python.org/3/whatsnew/3.14.html] The 3.14 default-start-method change for `ProcessPoolExecutor` (`fork` → `forkserver` on non-macOS Unix, see Section 13) is directly production-relevant for any multiprocessing-based service that depended on fork's implicit-inheritance semantics (open file descriptors, already-initialized global state) — worth an explicit compatibility check when upgrading a production multiprocessing workload to 3.14.

[Source: https://docs.python.org/3/howto/free-threading-python.html] For production services considering free-threaded Python (3.13 experimental / 3.14 officially supported): the documented guidance frames it as a good fit for **multi-threaded I/O-bound** workloads (web scrapers, API clients, concurrent server workloads) and a **poor fit** for CPU-bound work (where `multiprocessing` remains the documented recommendation) or single-threaded scripts, given the documented single-thread overhead and higher memory footprint discussed in Sections 8/14 — and it requires auditing C-extension dependencies for free-threading compatibility (an incompatible extension silently re-enables the GIL with a warning at import time, which is a production-monitoring-worthy event, not just a dev-time curiosity).

---

## Summary of sources consulted

Primary: `docs.python.org/3/` (landing page, `reference/datamodel.html`, `reference/import.html`, `library/index.html`, `library/exceptions.html`, `library/unittest.html`, `library/doctest.html`, `library/pdb.html`, `library/profile.html`, `library/typing.html`, `library/asyncio.html`, `library/venv.html`, `library/2to3.html`, `library/security_warnings.html`, `library/sys.html`, `library/logging.html`, `using/cmdline.html`, `using/unix.html`, `extending/extending.html`, `howto/free-threading-python.html`, `howto/perf_profiling.html`, `howto/pyporting.html`, `howto/doanddont.html` [inconclusive fetch], `glossary.html`, `deprecations/index.html`, `whatsnew/3.12.html`, `whatsnew/3.13.html`, `whatsnew/3.14.html`, `faq/design.html`). Supplementary official: `devguide.python.org/versions/`, `peps.python.org/pep-0703/`, `peps.python.org/pep-0602/`, `peps.python.org/pep-2026/`, `peps.python.org/pep-0008/`, `packaging.python.org/en/latest/tutorials/packaging-projects/`.
