# ECMAScript — Deep Reference Research

Research date: 2026-09-09. Primary sources: the official ECMAScript Language Specification hosted by TC39 at `https://tc39.es/ecma262/` (living "next edition" draft) and its yearly-snapshot editions (e.g. `https://tc39.es/ecma262/2026/`), the official TC39 process document at `https://tc39.es/process-document/`, the official TC39 proposals tracking repository at `https://github.com/tc39/proposals`, the official `tc39/ecma262` and `tc39/test262` GitHub repositories, and the standards-body publication pages at `https://ecma-international.org/publications-and-standards/standards/ecma-262/` and `https://ecma-international.org/publications-and-standards/standards/ecma-402/`. MDN, W3Schools, and other third-party JavaScript reference sites were deliberately **not** used as citations per this project's official-sources-only rule, even though they are commonly used JS references — they are not TC39/Ecma-published.

**Canonical docs host note:** [Source: https://tc39.es/ecma262/] `tc39.es` is the current canonical host for the ECMAScript specification's human-readable HTML rendering; it has not moved. [Source: https://ecma-international.org/publications-and-standards/standards/ecma-262/] `ecma-international.org` remains the canonical host for the formally ratified/ISO-adjacent PDF+HTML publication record and edition history. [Source: https://github.com/tc39/ecma262] The specification's source of truth for day-to-day editorial development is the `tc39/ecma262` GitHub repository, built with a markup toolchain into the tc39.es HTML rendering.

**Naming note:** [Source: https://tc39.es/ecma262/2026/] The formal standard is named "ECMAScript"; [Source: https://tc39.es/ecma262/] "JavaScript" is the specification's most widely known implementation/embodiment, not a separate technology — this document researches the language-specification layer (distinct from the separately-tracked TypeScript superset).

**Version-landscape note (important for grounding any skill built on this research):** [Source: https://ecma-international.org/publications-and-standards/standards/ecma-262/] As of this research date, the most recently **ratified/published** edition is the **17th edition, ECMAScript 2026**, released **June 2026**. [Source: https://tc39.es/ecma262/] The **living draft** at the canonical `tc39.es/ecma262/` URL (no year in the path) has already moved on to represent the **ECMAScript 2027** in-progress edition, since TC39 continuously edits the "next" draft as proposals reach Stage 4 year-round. Any skill content should distinguish "the current published/ratified standard" (2026, 17th edition) from "the current tc39.es/ecma262/ page" (2027 draft, not yet ratified).

---

## 1. Core Concepts

[Source: https://tc39.es/ecma262/2026/] ECMAScript is defined by the specification's own overview material as "a general purpose, lightweight, interpreted programming language" intended for scripting/general computation, most widely known through its JavaScript implementation used in web browsers and server-side runtimes.

[Source: https://tc39.es/ecma262/multipage/overview.html] The specification's Overview (clause 4) is organized into: 4.1 Web Scripting, 4.2 Hosts and Implementations, 4.3 ECMAScript Overview (with subsections 4.3.1 Objects and 4.3.2 The Strict Variant of ECMAScript), 4.4 Terms and Definitions, and 4.5 Organization of This Specification.

[Source: https://ecma-international.org/publications-and-standards/standards/ecma-262/] ECMA-262 is developed and maintained by Ecma International's Technical Committee 39 (TC39), and defines the ECMAScript general-purpose programming language as a formal, ratified standard (with an equivalent ISO/IEC 16262 relationship historically maintained, per Ecma's standard-suite process — see Section 16).

[Source: https://tc39.es/ecma262/multipage/overview.html] The specification distinguishes strict-mode ECMAScript from the non-strict ("sloppy") default variant in 4.3.2 "The Strict Variant of ECMAScript," and provides normative static semantics (`IsStrict`) to determine strictness of a given piece of code, per 11.2.2 "Strict Mode Code."

[Source: https://tc39.es/ecma262/multipage/overview.html] Objects are foundational to the language's overview description (4.3.1 Objects) — ECMAScript is described in terms of objects, properties, and prototype-based behavior rather than class-based inheritance as the language's original model (classes were added later as sugar over this model — see Section 2).

[Source: https://github.com/tc39/proposals] TC39's own framing of the language's evolution model is that ECMAScript is not a fixed, monolithic artifact but a **yearly composite** of the prior edition plus every proposal that independently reached Stage 4 (Finished) in that year's cycle — each feature is designed, vetted, and tested largely independently before being folded into the next edition.

[Source: https://tc39.es/process-document/] Core to the language's evolution philosophy: proposals for new syntax or semantics go through a five-stage (0–4) maturity process (see Section 2/11) requiring, by Stage 4, two independent, Test262-passing implementations and significant in-the-field experience before becoming part of the standard — the spec is deliberately implementation-experience-driven rather than committee-designed-in-a-vacuum.

---

## 2. Architecture

[Source: https://tc39.es/ecma262/multipage/overview.html] Clause 4.2 "Hosts and Implementations" establishes the core architectural split between the **language specification** (ECMA-262 itself) and the **host environment** (e.g., a web browser or other embedding runtime) that supplies additional objects, behavior, and integration points not defined by the language spec proper — ECMAScript as a spec deliberately does not define I/O, a full standard library, or a runtime environment on its own.

[Source: https://tc39.es/ecma262/multipage/additional-ecmascript-features-for-web-browsers.html] Annex B, "Additional ECMAScript Features for Web Browsers," is normative for web browser hosts but explicitly **normative-optional** for non-browser ECMAScript hosts — it documents legacy syntax/behaviors (compatibility corner cases) that browsers must implement for web compatibility but that other hosts (e.g., some embedded or server runtimes) are not required to support.

[Source: https://tc39.es/ecma262/multipage/overview.html] The execution-model architecture is defined in clause 9 of the spec: 9.3 Realms (an isolated global environment with its own global object and intrinsics), 9.4 Execution Contexts (the stack-based activation-record model tracking currently-running code), 9.5 Jobs and Job Queues (the abstract model underlying microtask-style deferred execution, e.g. for Promises), and 9.6 Agents (the spec's abstraction for a unit of concurrent execution, relevant to shared-memory/Atomics semantics).

[Source: https://github.com/tc39/proposal-shadowrealm] Multiple/isolated Realms as a first-class *scripting* primitive (beyond the spec's internal Realm abstraction used for `<iframe>`-style isolation) is proposed via **ShadowRealm**, which as of this research date is a separate, not-yet-Stage-4 proposal (Stage 2.7) — i.e., **not part of ECMA-262 itself**; it is tracked independently at `tc39/proposal-shadowrealm` and would add a `ShadowRealm` constructor exposing `evaluate()` and `importValue()` for isolated same-thread code execution if it advances to Stage 4.

[Source: https://tc39.es/ecma262/multipage/host-layering-points.html] The spec defines explicit **"host hooks"** — abstract operations partially or wholly defined by an external source (the host environment) rather than fully by ECMA-262 — including `HostEnsureCanCompileStrings`, `HostFinalizeImportMeta`, `HostGetImportMetaProperties`, `HostHasSourceTextAvailable`, `HostLoadImportedModule`, `HostMakeJobCallback`, and `HostPromiseRejectionTracker`. This "host layering" is the formal architectural seam through which browsers and non-browser runtimes (e.g., server-side JS engines) plug module resolution, dynamic `import()`, CSP string-compilation checks, and unhandled-rejection tracking into the pure language spec.

[Source: https://github.com/tc39/ecma262] The specification's own build architecture: source is authored/edited on GitHub (`tc39/ecma262`, main branch), built locally via `npm install` then `npm run build` (or `npm run watch` for continuous rebuilds), and the processed output is what's published as the human-readable HTML at tc39.es. Yearly-edition snapshots are produced from this same repository (see Section 12).

[Source: https://tc39.es/ecma262/2026/] The document's top-level clause organization (confirmed from the 2026 edition's table of contents) proceeds: Scope/Conformance/Normative References (1–3), Overview (4), Notational Conventions (5), through ECMAScript Data Types and Values, Abstract Operations, Syntax-Directed Operations, Executable Code and Execution Contexts, Ordinary and Exotic Objects Behaviours, and the full ECMAScript language grammar chapters (lexical grammar, expressions, statements, functions, classes, scripts/modules), followed by the standard built-in object library chapters and normative/informative annexes.

---

## 3. APIs

[Source: https://tc39.es/ecma262/multipage/overview.html] The spec's overview text (4.3.1 Objects) frames ECMAScript's built-in surface primarily around **objects** — the "API" of the language is the set of standard built-in objects/intrinsics the spec mandates every conforming implementation provide.

[Source: https://tc39.es/ecma262/2026/] Confirmed (from the 2026 edition's built-in-object chapters) standard built-in globals include, among others: fundamental/value types `Array`, `Object`, `String`, `Number`, `Boolean`, `Symbol`, `BigInt`; control-flow/async primitives `Promise`, generator/iterator protocol objects, and `Iterator` helpers (a Stage-4-landed helper-method surface on the Iterator prototype); meta-level reflection objects `Proxy` and `Reflect`; typed-array/binary-data types (the `TypedArray` family, `DataView`, `ArrayBuffer`); and memory/concurrency primitives `WeakRef` and `FinalizationRegistry`.

[Source: https://github.com/tc39/proposals/blob/main/finished-proposals.md] Per the official finished-proposals ledger, notable **API additions landing in recent editions** (each independently reaching Stage 4) include: **ES2024** — `Promise.withResolvers`, `Object.groupBy`/`Map.groupBy` ("Array Grouping"), resizable/growable `ArrayBuffer`, the RegExp `v` flag with set notation, `Atomics.waitAsync`, well-formed-Unicode-string methods, and "change array by copy" methods (`toSorted`/`toReversed`/`toSpliced`/`with`); **ES2025** — redeclarable global `eval`-introduced vars, Float16 support on typed arrays/DataView plus `Math.f16round`, synchronous `Iterator` helper methods, JSON module imports, import attributes, RegExp named-group modifiers, new `Set` methods (e.g. union/intersection-style operations), duplicate named capture groups, and `ArrayBuffer.prototype.transfer`; **ES2026** — `Map`/`WeakMap` "Upsert" (`getOrInsert`), `JSON.parse` source-text access (`context.source`), Iterator Sequencing, `Uint8Array.fromBase64`/`toBase64` and hex equivalents, `Math.sumPrecise`, `Error.isError`, `Array.fromAsync`, and `RegExp.escape`.

[Source: https://github.com/tc39/proposals/blob/main/finished-proposals.md] **Version-sensitive:** proposals reported as Stage 4 and slated for the still-in-progress **ES2027** draft (i.e., not yet in the ratified ES2026 standard as of this research date) include Explicit Resource Management (`using`/`await using` declarations), `Atomics.pause`, Joint Iteration, and **Temporal** (the long-in-development date/time API replacing many `Date` pain points).

[Source: https://ecma-international.org/publications-and-standards/standards/ecma-402/] Internationalization-related APIs (the `Intl` namespace — `Intl.DateTimeFormat`, `Intl.NumberFormat`, `Intl.Collator`, etc.) are **not** defined in ECMA-262 itself; they are defined in the companion standard **ECMA-402** ("ECMAScript Internationalization API Specification"), maintained by the same TC39 committee as a complement to ECMA-262, with its functionality drawn from established i18n libraries (ICU, .NET, Java).

[Source: https://tc39.es/ecma262/multipage/host-layering-points.html] Beyond in-language built-ins, the spec exposes an API surface to **host environments** in the form of host hooks (`HostLoadImportedModule`, `HostEnsureCanCompileStrings`, etc. — see Section 2) — these are the contract points a runtime (browser, server engine) must implement to support modules, dynamic import, and related host-integrated behavior; they are not callable JS APIs but are architecturally the spec's "API to the host."

---

## 4. Configuration

Not documented / does not apply in the conventional sense. [Source: https://tc39.es/ecma262/multipage/overview.html] ECMA-262 is a language specification, not a distributed software artifact — it defines no config file, CLI flags, or environment variables of its own. The closest in-language "configuration" surface is **strict mode**, which the spec (4.3.2, 11.2.2) treats as a per-script/per-module/per-function opt-in that changes semantics (e.g., disallowing certain silent errors, `this` binding differences, restricted syntax) — enabled via the `"use strict"` directive prologue or implicitly for the entire body of ECMAScript **modules** and **classes**, which the spec defines as always-strict without needing the directive. [Inference, not confirmed in docs] Practical "configuration" of which ECMAScript edition/feature set a project targets (e.g., via a bundler's `target` option or a `.browserslistrc`) is a toolchain-level concern outside ECMA-262's scope, governed instead by the consuming tool's own documentation.

---

## 5. Recommended Patterns

[Source: https://tc39.es/ecma262/multipage/overview.html] The specification itself is normative/descriptive, not prescriptive about application-level coding style — it does not publish a style guide or "recommended patterns" document for application authors the way a framework or library would. Not documented / could not verify: TC39/ECMA-262 does not maintain an official "how to write idiomatic ECMAScript" guide.

[Source: https://tc39.es/process-document/] Where TC39 does publish prescriptive guidance is for **proposal authors**, not application developers: the process document specifies that proposals should identify "cross-cutting concerns" early (Stage 1), provide complete spec text and usage examples before Stage 2/3, and secure two independent, Test262-conformant implementations plus real-world usage signal before Stage 4 — this is process guidance for evolving the language, not a coding-pattern guide for using it.

[Inference, not confirmed in docs] Given the spec's own strict-mode framing (Section 4) and its statement that classes/modules are implicitly strict, a defensible pattern grounded directly in spec text is: prefer ECMAScript modules and/or explicit `"use strict"` for script code, since strict mode's spec-defined restrictions (no implicit global creation via undeclared assignment, no silent failure on invalid assignments, restricted `with`, etc.) eliminate several categories of the language's own documented legacy/error-prone behavior (see Annex B, Section 6). This is a reasonable inference from spec structure, not a directly stated TC39 "recommendation."

---

## 6. Anti-Patterns

[Source: https://tc39.es/ecma262/multipage/additional-ecmascript-features-for-web-browsers.html] Annex B, "Additional ECMAScript Features for Web Browsers," is the specification's own closest analogue to a documented anti-pattern list: it exists specifically to preserve legacy, non-strict-mode behaviors that browsers must still support for web compatibility but which the spec segregates as normative-*optional* outside the browser context — i.e., the spec architecturally signals these are compatibility carve-outs, not the language's forward-looking design center.

[Source: https://tc39.es/ecma262/multipage/overview.html] Strict mode's existence and its specific list of prohibited constructs (per 4.3.2/11.2.2) function as the spec's implicit anti-pattern catalogue: constructs strict mode disallows or changes the semantics of (e.g., assignment to undeclared identifiers silently creating globals, use of `with`, certain forms of `eval`/`arguments` aliasing) are, by the spec's own design, behaviors the language evolved away from.

Not documented / could not verify beyond the above: ECMA-262 does not publish a standalone "anti-patterns" or "common mistakes" section comparable to what an application framework's docs would include; it is a semantics specification, not a style/practice guide.

---

## 7. Security

Not documented / could not verify as a dedicated section: ECMA-262 does not publish a security-advisories page, threat model, or "security considerations" clause comparable to a networked-software spec (e.g., an RFC's Security Considerations section). [Inference, not confirmed in docs] This is architecturally consistent with the spec's own scope: because ECMAScript defines a hosted, sandboxed-by-hosting-environment language with no built-in file/network/OS access, most security properties (sandboxing strength, same-origin enforcement, CSP interaction) are host-environment responsibilities layered on top via host hooks, not something ECMA-262 itself specifies.

[Source: https://tc39.es/ecma262/multipage/host-layering-points.html] One directly spec-relevant host hook, `HostEnsureCanCompileStrings`, is explicitly the seam through which a host can restrict/observe string-to-code compilation (e.g., `eval`, the `Function` constructor) — this is the specification's formal integration point for host-level code-execution security policies (such as a browser's Content-Security-Policy), though the security *policy* itself is host-defined, not specified by ECMA-262.

[Source: https://github.com/tc39/proposal-shadowrealm] The **ShadowRealm** proposal (Stage 2.7, not yet in the ratified standard as of this research date) is TC39's in-progress answer to same-thread code isolation/sandboxing (e.g., running third-party code without letting it pollute or read the host realm's globals) — its existence as a still-advancing proposal signals that same-thread sandboxing is explicitly **not yet** a finished, standardized ECMAScript capability.

[Inference, not confirmed in docs] Strict mode's restrictions on `eval`/`arguments` scope leakage and disallowing accidental implicit globals are the spec's closest built-in mitigations against a class of injection/scope-pollution bugs, though the spec frames these as language-semantics changes, not explicitly as "security" features.

---

## 8. Performance

Not documented / could not verify as a dedicated section: [Inference, not confirmed in docs] ECMA-262 specifies observable language *semantics* (what a conforming program must produce), not performance characteristics — the spec is written so that algorithm steps describe required observable behavior while leaving actual execution strategy (JIT compilation, inline caching, garbage-collection strategy, etc.) fully implementation-defined; no official ECMA-262 material was found during this research making performance claims or recommendations, since that is intentionally left to individual engine implementations (V8, SpiderMonkey, JavaScriptCore, and others), which are outside ECMA-262's own documentation scope.

[Source: https://tc39.es/ecma262/multipage/overview.html] The only spec-adjacent performance-relevant material found is architectural: the Agent/Realm/Job-queue model (Section 2) formally defines *ordering and concurrency* guarantees (e.g., job-queue-based microtask ordering for Promises, Atomics-based shared-memory operations across Agents) that implementations must respect — these are correctness/ordering guarantees, not performance guidance per se.

---

## 9. Testing

[Source: https://github.com/tc39/test262] **Test262** is the official ECMAScript conformance test suite, described as "the implementation conformance test suite for the latest drafts (or most recent published edition)" of the Ecma specifications, and is itself formally referenced by ECMA TR/104 and included in the ECMA-414 standards suite.

[Source: https://github.com/tc39/test262] Test262's stated goal is to cover "every observable behavior specified in the ECMA-414 Standards Suite"; as of a May 2025 count cited in the repository, it comprised over 50,000 individual test files covering the majority of the pseudo-code algorithms and grammar productions in the spec.

[Source: https://github.com/tc39/test262/blob/main/INTERPRETING.md] Guidance on how a test-runner must interpret a Test262 test file (metadata format, expected-outcome frontmatter, harness includes) is documented in the repository's `INTERPRETING.md`.

[Source: https://github.com/tc39/test262/blob/main/CONTRIBUTING.md] Guidance for contributing new tests is documented in `CONTRIBUTING.md`; the repository README notes that volunteer-maintained harness projects exist to execute Test262 against various ECMAScript hosts (e.g. Node.js, Python, browser, C++, .NET-based runners), though these harnesses themselves are described as community/volunteer-maintained rather than official TC39 deliverables.

[Source: https://tc39.es/process-document/] Test262 conformance is load-bearing in the standardization process itself, not just a QA afterthought: **Stage 4 entrance criteria explicitly require** the proposal to have Test262 acceptance tests and two independent implementations that pass them, before a feature can be folded into a yearly edition (see Section 11/12) — i.e., official ECMAScript testing infrastructure is a formal gate on the language's own evolution, not merely a downstream conformance checker.

---

## 10. Deployment

Not documented / does not apply in the conventional software-deployment sense. [Inference, not confirmed in docs] ECMA-262 specifies a language, not a distributable runtime or package — there is nothing to "deploy" from the specification itself. Deployment of *ECMAScript-conformant code* is entirely a function of the choice of host runtime (a specific browser version, a specific Node.js/Deno/Bun version, etc.), each of which has its own official docs (outside ECMA-262's scope) describing which spec editions/features it implements and how to ship code that targets it.

[Source: https://tc39.es/ecma262/multipage/host-layering-points.html] The spec's host-hooks architecture (Section 2/3) is the formal mechanism by which any given deployment target integrates module loading and execution — but the spec deliberately leaves the concrete hook implementations (how a browser fetches a module over the network, how a server runtime resolves a bare specifier from `node_modules`, etc.) fully to the host's own documentation.

---

## 11. Migration

[Source: https://tc39.es/process-document/] Because each yearly ECMAScript edition is a strict superset assembled from independently-vetted Stage 4 proposals layered on the prior edition, TC39's own process is architected to make "migration" between editions low-friction by design — there is no dedicated "migrating from ES20XX to ES20YY" guide because editions are not intended to require one for existing conformant code.

[Source: https://github.com/tc39/proposals] The mechanism for tracking *what changed* between editions is the finished-proposals ledger itself (`finished-proposals.md`), organized by target edition year, which functions as the closest official analogue to a changelog for anyone migrating code/tooling forward across editions (see Section 3/13 for the itemized recent-edition contents pulled from this ledger).

[Source: https://tc39.es/process-document/] For contributors/tooling authors rather than application code, the official migration-relevant document is "Contributing to ECMAScript" (linked from the `tc39/ecma262` README) — it governs how a proposal or spec-text change gets incorporated, not how application code migrates between language versions.

Not documented / could not verify: a dedicated, TC39-published "breaking changes and how to fix them" migration guide per edition (analogous to what a framework like Angular or a compiler like TypeScript publishes) was not found; per the backward-compatibility framing in Section 13, this appears to be because breaking changes across ECMAScript editions are rare and individually called out rather than requiring an edition-wide migration guide.

---

## 12. Version Information

[Source: https://ecma-international.org/publications-and-standards/standards/ecma-262/] Confirmed publication history: 1st edition — June 1997; edition 4 was reserved but never published; editions 5 through 16 were released annually from 2009 through 2025; editions 13–16 correspond to June 2022 through June 2025.

[Source: https://ecma-international.org/publications-and-standards/standards/ecma-262/] **Current ratified/published edition:** the **17th edition**, defining **ECMAScript 2026**, released **June 2026**. [Source: https://tc39.es/ecma262/2026/] This edition is also directly accessible as a permanent yearly snapshot at `https://tc39.es/ecma262/2026/`.

[Source: https://tc39.es/ecma262/] **Living/in-progress draft:** the canonical no-year URL `https://tc39.es/ecma262/` currently renders as the **"ECMAScript 2027 Language Specification"** — i.e., TC39's continuous-editing draft has already moved past the 2026 ratified edition and is accumulating Stage-4 proposals toward the next (18th) yearly edition. This draft is **not yet ratified** as of this research date (2026-09-09).

[Source: https://tc39.es/process-document/] **Release cadence:** ECMAScript follows a fixed **yearly release cadence**, with a documented annual production timeline: a Candidate Draft is produced **February 1**; a **60-day royalty-free opt-out period** runs February–March; the **March TC39 meeting** is where that cycle's Stage 4 proposals are incorporated and the next edition's working branch is created; **April–June** covers Ecma Executive Committee and General Assembly review; and **July** is when the Ecma General Assembly formally approves the new standard. [Inference, not confirmed in docs] Note this described "July approval" timeline is in modest tension with the "June 2026" release date given for the 17th edition on the ecma-international.org publications page — both are official-source claims but were not reconciled to the day; treat "June/July" as the annual ratification window rather than a single fixed date.

[Source: https://tc39.es/] TC39, the committee that produces the standard, meets **every two months** to discuss and advance proposals — this is the underlying proposal-review cadence feeding the yearly edition cycle, not the edition-release cadence itself.

**LTS / support-window status:** Not documented / does not apply. [Inference, not confirmed in docs] ECMA-262 is a specification, not a maintained software product, so it has no "supported versions" or end-of-life policy in the way a runtime or library does; each yearly edition simply supersedes the prior one as the current standard, and prior editions remain historically published/archived (per the ecma-international.org edition list) rather than "deprecated." Runtime-specific support windows (e.g., which edition a given browser or Node.js version implements) are outside ECMA-262's own scope.

---

## 13. Breaking Changes

[Source: https://tc39.es/process-document/] TC39's process is explicitly designed around backward compatibility as a governing constraint on proposal advancement — proposals that would break existing conforming programs face a substantially higher bar, and "web compatibility" issues are one of the things Stage 3 implementation experience is specifically meant to surface before a feature can reach Stage 4.

[Source: https://tc39.es/ecma262/multipage/additional-ecmascript-features-for-web-browsers.html] Per official-source search results, ECMA-262 maintains a section documenting "Additions and Changes That Introduce Incompatibilities with Prior Editions" — its existence signals that TC39 treats backward-incompatible changes as rare, enumerable exceptions rather than routine occurrences; direct extraction of the full itemized contents of this section was not achieved during this research pass due to tool/page-size limitations. **Unresolved:** could not directly confirm the exact anchor/URL and full itemized list of this incompatibilities section for the current (2026/2027) edition text; only its existence and general framing were confirmed via search-result snippets of official spec pages, not a direct primary-source read of its contents.

[Source: https://github.com/tc39/proposals/blob/main/finished-proposals.md] Because each edition is additive-by-design (new APIs and syntax layered on the prior edition rather than removing existing behavior), the finished-proposals ledger itself does not surface any edition-over-edition **removals** among ES2024–ES2027; every entry examined (Array grouping, Promise.withResolvers, Set methods, Float16 typed arrays, Upsert, Iterator Sequencing, Temporal, Explicit Resource Management, etc.) is an addition, consistent with the backward-compatibility framing above.

[Inference, not confirmed in docs] Given the strict-mode/non-strict-mode split (Section 1/6) and Annex B's browser-legacy carve-out (Section 2/6), the spec's actual mechanism for "breaking changes" appears to be: new restrictions are introduced only inside strict-mode/module/class contexts (which did not exist or were opt-in at the time the restricted behavior was legal), rather than retroactively breaking pre-existing non-strict scripts — this is a structural inference from how the spec is organized, not a directly quoted TC39 statement enumerating this as policy.

---

## 14. Limitations

[Source: https://tc39.es/ecma262/multipage/overview.html] By explicit design (clause 4.2, Hosts and Implementations), ECMA-262 does not define a general-purpose standard library, I/O, networking, file-system access, or a runtime/execution environment — all such capabilities are host-environment-supplied, not part of the language specification itself. This is a documented scope limitation, not an oversight.

[Source: https://tc39.es/ecma262/multipage/host-layering-points.html] Several core behaviors that application developers experience as "part of JavaScript" — module fetching/resolution, dynamic `import()` semantics beyond the abstract algorithm, unhandled-promise-rejection reporting, and code-compilation security gating — are only **partially** specified by ECMA-262 via host hooks; the concrete behavior is host-defined and therefore intentionally out of ECMA-262's own documentation scope (see Sections 2, 3, 7, 10).

[Source: https://ecma-international.org/publications-and-standards/standards/ecma-402/] Internationalization functionality (locale-aware formatting, collation, etc.) is explicitly out of scope for ECMA-262 and is delegated entirely to the separate ECMA-402 standard.

[Source: https://tc39.es/ecma262/multipage/additional-ecmascript-features-for-web-browsers.html] Certain legacy behaviors documented in Annex B are explicitly **not required** outside web browser hosts — meaning "the ECMAScript language" as experienced in a non-browser host (e.g., certain embedded engines) can legitimately omit Annex B behaviors while still being fully conformant, a documented source of cross-host behavioral variance.

[Source: https://tc39.es/process-document/] The proposal process itself is a documented constraint on the language's evolution speed: a feature cannot enter the standard without passing through five maturity stages, requiring (by Stage 4) two independent conformant implementations and Test262 coverage — meaning even a committee-approved design can be blocked indefinitely on implementation availability, which the process document treats as a deliberate quality gate rather than a defect.

---

## 15. Debugging

Not documented / could not verify as a dedicated section. [Inference, not confirmed in docs] Debugging tooling (breakpoints, stack inspection, source maps, devtools protocols) is implementation/host territory (browser DevTools, Node.js Inspector, etc.), not something ECMA-262 itself specifies or documents — consistent with the same host/language split noted in Sections 2 and 14, no official TC39/ECMA-262 material describing debugging workflows or tooling was found.

[Source: https://tc39.es/ecma262/multipage/overview.html] The specification does define the `Error` object family (and subtypes) as part of the standard built-in object library, which is the language-level primitive that host debugging tools build upon (e.g., surfacing `Error.prototype.message`/`stack`-style diagnostic info) — but the spec itself does not mandate a `stack` property or any particular diagnostic-string format; such details are host-defined, outside ECMA-262's normative requirements. [Inference, not confirmed in docs] This is why stack-trace formatting famously differs across JS engines — it is not specified by ECMA-262.

---

## 16. Integration

[Source: https://tc39.es/] TC39 (the committee) operates under Ecma International, alongside related technical committees; the specification suite it maintains includes ECMA-262 (the language), and — per the tc39.es site's own referenced standards — **ECMA-402** (Internationalization API), **ECMA-404** (JSON Data Interchange Syntax), and **ECMA-414** (the ECMAScript Specification Suite, which formally bundles the others together, and which Test262 is scoped against per Section 9).

[Source: https://ecma-international.org/publications-and-standards/standards/ecma-402/] ECMA-402 is explicitly documented as "a complement to" ECMA-262, versioned in step with it (e.g., the "ECMAScript 2022 Internationalization API Specification, 9th edition" complements "ECMA-262, 13th edition or successor") — this is the specification suite's own documented integration model between the core language and the i18n layer.

[Source: https://tc39.es/ecma262/multipage/host-layering-points.html] The formal integration surface between ECMA-262 and any embedding host (browsers, Node.js-class server runtimes, embedded engines) is the **host hooks** mechanism (Section 2/3): `HostLoadImportedModule` for module resolution/fetching, `HostGetImportMetaProperties`/`HostFinalizeImportMeta` for `import.meta`, `HostEnsureCanCompileStrings` for string-to-code compilation gating, `HostMakeJobCallback` and `HostPromiseRejectionTracker` for job/microtask and rejection-tracking integration. A cited concrete example: HTML (the browser host spec, maintained by WHATWG, outside TC39) uses the `hostDefined` parameter of `HostLoadImportedModule` to set correct fetch destinations for constructs like `<link rel="preload" as="...">`.

[Source: https://github.com/tc39/ecma262] The specification's own tooling integration is documented at the repository level: it is authored and versioned on GitHub, built via `npm install && npm run build`, with contribution guidance pointing to a separate "Contributing to ECMAScript" resource and to the `tc39/proposals` repository for anything that isn't an already-Stage-4, purely-editorial change.

---

## 17. Production Considerations

Not documented / could not verify as a dedicated "production considerations" section — ECMA-262 does not publish operational/production guidance, since it specifies a language, not a deployed service or runtime with production concerns of its own (see Sections 8, 10).

[Source: https://tc39.es/process-document/] The most production-relevant official guidance is indirect, via the process document's Stage 3 criteria: Stage 3 exists specifically to gather **real-world implementation and usage experience** before a feature is finalized, and the process explicitly treats web-compatibility breakage discovered at this stage as grounds to revisit or block a proposal — i.e., TC39's own process functions as the pre-production risk gate for new language features, rather than there being separate "how to run this in production" documentation.

[Inference, not confirmed in docs] Because ECMA-262 does not mandate any particular Error/stack format, i18n behavior (delegated to ECMA-402), or performance characteristics, and because Annex B legacy behavior varies by host type (Section 14), a production consideration inferable directly from the spec's own structure — but not stated by TC39 as production advice per se — is that spec conformance alone does not guarantee observably identical behavior across hosts/engines in these specific areas; teams shipping to multiple runtimes should expect host-defined variance precisely where the spec itself defers to host hooks or annexes.

---

## Summary of Citation Sources Used

- https://tc39.es/ecma262/ — living/next-edition specification (currently rendering as ECMAScript 2027 draft)
- https://tc39.es/ecma262/2026/ — ECMAScript 2026, 17th edition, ratified snapshot
- https://tc39.es/ecma262/multipage/overview.html — Overview clause (4), execution-model clauses (9.x)
- https://tc39.es/ecma262/multipage/additional-ecmascript-features-for-web-browsers.html — Annex B
- https://tc39.es/ecma262/multipage/host-layering-points.html — Host hooks / host layering points
- https://tc39.es/ — TC39 committee overview page
- https://tc39.es/process-document/ — The TC39 Process (stage 0–4 definitions, yearly release timeline)
- https://ecma-international.org/publications-and-standards/standards/ecma-262/ — ECMA-262 publication/edition history
- https://ecma-international.org/publications-and-standards/standards/ecma-402/ — ECMA-402 (Internationalization API) publication page
- https://github.com/tc39/ecma262 — spec source repository (build process, contribution pointers)
- https://github.com/tc39/proposals — proposals tracking repository (stage listing, process linkage)
- https://github.com/tc39/proposals/blob/main/finished-proposals.md — Stage 4 finished proposals ledger by edition year
- https://github.com/tc39/proposal-shadowrealm — ShadowRealm proposal (Stage 2.7, sandboxing/isolation)
- https://github.com/tc39/test262 — Test262 official conformance test suite (README)
- https://github.com/tc39/test262/blob/main/INTERPRETING.md — Test262 test-file interpretation guidance
- https://github.com/tc39/test262/blob/main/CONTRIBUTING.md — Test262 contribution guidance
