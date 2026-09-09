# TypeScript — Deep Reference Research

Research date: 2026-09-09. Primary source: official TypeScript documentation at `https://www.typescriptlang.org/docs/`, supplemented by the official `microsoft/TypeScript` GitHub org (repo, wiki, release-note pages hosted on typescriptlang.org) and the official TypeScript team blog at `https://devblogs.microsoft.com/typescript/`. Node.js's own official docs (`nodejs.org`) are cited only for the one integration claim about Node's native TypeScript support, since that is Node's documented behavior, not TypeScript's.

**Canonical docs host note:** [Source: https://www.typescriptlang.org/docs/] As of this research date, `typescriptlang.org` is still the canonical documentation host (Handbook, Reference, tsconfig reference, release notes). It has not moved. However, [Source: https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API] the compiler-internals wiki explicitly warns its own content is being superseded: "The contents of this page currently describe TypeScript 6.0 and earlier. TypeScript 7.1 will have a completely different API," and [Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] deep architectural/API documentation is actively being migrated as the compiler moves to a Go-native implementation. Treat wiki-hosted API pages as time-sensitive.

**Major version-landscape note (important for grounding any skill built on this research):** [Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] TypeScript underwent a complete compiler rewrite from JavaScript to Go, shipped as **TypeScript 7.0 on July 8, 2026** (a "native port," project codename `tsgo`/`@typescript/native-preview`). [Source: https://www.npmjs.com/package/typescript] The current published npm version at research time is **7.0.2**. TypeScript 6.0 (released March 23, 2026, per the devblogs announcement) was a deliberate "bridge" release that changed long-standing defaults to prepare for 7.0. This means any pre-2026 training knowledge of TypeScript defaults (e.g., `strict: false` by default, `module: commonjs` by default) is now version-stale — see Section 12–13 for specifics.

---

## 1. Core Concepts

[Source: https://www.typescriptlang.org/docs/handbook/2/basic-types.html] TypeScript is a static type-checker built as a superset of JavaScript: it adds type annotations and compile-time analysis on top of standard JavaScript syntax and semantics.

[Source: https://www.typescriptlang.org/docs/handbook/2/basic-types.html] TypeScript catches errors at compile time by statically analyzing what values and operations a program's code can legally use — including "non-exception failures" such as accessing a property that doesn't exist on an object, which plain JavaScript would only surface as `undefined` at runtime.

[Source: https://www.typescriptlang.org/docs/handbook/2/basic-types.html] Types are fully erased at compile time: the emitted JavaScript contains no type annotations, interfaces, or type-only constructs. Type annotations are a compile-time-only feature with no effect on runtime behavior.

[Source: https://www.typescriptlang.org/docs/handbook/type-compatibility.html] TypeScript uses a **structural type system**: a type `x` is compatible with type `y` if `x` has at least the members `y` requires, regardless of explicit inheritance or declared type names (in contrast to nominal typing in languages like Java or C#). The docs state this was chosen because JavaScript idiomatically uses anonymous objects (object literals, function expressions), which structural typing models more naturally than nominal typing.

[Source: https://www.typescriptlang.org/docs/handbook/type-compatibility.html] The docs explicitly state the type system is **not fully sound** by design, and enumerate specific unsound-but-intentional behaviors: function parameter bivariance, optional/rest parameter interchangeability, and permitting extra properties on objects assigned (as opposed to literal) to a typed variable. The docs frame these as deliberate trade-offs to avoid being "unnecessarily restrictive" against common JavaScript patterns.

[Source: https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals] The official Design Goals page lists TypeScript's stated goals, including (paraphrased/quoted): "Statically identify constructs that are likely to be errors," "Provide a structuring mechanism for larger pieces of code," "Impose no runtime overhead on emitted programs," "Emit clean, idiomatic, recognizable JavaScript code," "Align with current and future ECMAScript proposals," "Preserve runtime behavior of all JavaScript code," "Use a consistent, fully erasable, structural type system," and "Do not cause substantial breaking changes from TypeScript 1.0."

[Source: https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals] The same page lists explicit **non-goals**, including: not implementing a fully sound type system (balancing correctness against productivity), not providing an end-to-end build pipeline, not providing runtime type information/metadata by default, and not providing additional runtime functionality or libraries beyond describing existing ones.

[Source: https://www.typescriptlang.org/docs/handbook/2/basic-types.html] TypeScript ships gradual/opt-in strictness: individual flags like `noImplicitAny` and `strictNullChecks`, or the umbrella `strict` flag, control how aggressively the checker flags loosely-typed code, supporting incremental adoption from plain JavaScript.

---

## 2. Architecture

[Source: https://github.com/microsoft/TypeScript/wiki/Architectural-Overview] The (pre-7.0, JS-implemented) compiler pipeline is described as layered stages: a **Scanner** tokenizes source text (also handling "trivia" — whitespace/comments); a **Parser** builds an Abstract Syntax Tree (AST) from tokens; a **Binder** creates symbol tables and establishes semantic links between declarations and their references; a **Checker** performs type analysis/validation against the bound AST; an **Emitter** produces output JavaScript and/or `.d.ts` declaration files from the checked AST; and a **Language Service** layer sits on top of these to power IDE features (completions, diagnostics, refactors). The wiki notes deeper structural documentation was moved to the community-maintained `microsoft/TypeScript-Compiler-Notes` repo and its glossary — [Inference, not confirmed in docs] that repo appears to not be an official Microsoft-maintained doc source, so it is not cited further here.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] **Version-sensitive:** As of TypeScript 7.0 (July 2026), the compiler's implementation itself was rewritten natively in Go (replacing the JavaScript implementation used through 6.x), while preserving behavioral compatibility with 6.0. This native port ("tsgo") adds multithreaded/parallel compilation via new `--checkers` and `--builders` flags, a rebuilt `--watch` mode using a ported Parcel file watcher, and continues to expose Language Server Protocol-based editor integration. [Inference, not confirmed in docs] The Scanner→Parser→Binder→Checker→Emitter conceptual pipeline from the Architectural Overview wiki page likely still describes the high-level stages in the Go implementation, but the wiki page itself has not been confirmed updated for 7.0's Go architecture — flagged as **Unresolved: whether the Architectural Overview wiki page has been updated to describe the Go-native (7.0) implementation, or still only documents the legacy JS compiler internals.**

[Source: https://www.typescriptlang.org/docs/handbook/modules/theory.html] TypeScript's module architecture centers on modeling "the host" — the external runtime, bundler, or transpiler that will actually load the compiled output. The compiler's job is described as three-fold: (1) compile files into a valid output module format, (2) ensure imports in that output resolve correctly under the target host's rules, and (3) assign correct types to imported names. The `module` compiler option controls emitted syntax/semantics (e.g. `commonjs`, `es2022`, `node18`, `nodenext`, `preserve`), while the separate `moduleResolution` option controls how import specifiers are mapped to files.

[Source: https://www.typescriptlang.org/docs/handbook/modules/theory.html] A documented architectural subtlety: TypeScript resolves import specifiers by modeling runtime resolution of the **output** files, not the input `.ts` files — which is why relative imports of TypeScript sources are conventionally written with a `.js` extension (e.g. `import { add } from "./math.js"` even though the source file is `math.ts`), since that is what the compiled output's runtime host will actually resolve.

---

## 3. APIs

[Source: https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API] The (pre-7.1) public Compiler API, exposed via the `typescript` npm package, documents: `ts.createProgram()` as the primary full-compilation entry point (creates a default `CompilerHost` that reads from the file system given filenames + compiler options); `ts.createSourceFile()` to parse a single source string into an AST `SourceFile` node without a full `Program`; `ts.transpileModule()` as a simplified string-to-string transform for lightweight transpilation without full type-checking; a `TypeChecker` (via `program.getTypeChecker()`) exposing methods such as `getSymbolAtLocation()` and `getTypeAtLocation()`; and a `LanguageService` API supporting incremental compilation via file versioning/snapshots, used to power IDE tooling.

[Source: https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API] **Critical version-sensitive caveat, quoted directly from the official wiki:** "The contents of this page currently describe TypeScript 6.0 and earlier. TypeScript 7.1 will have a completely different API." Combined with the next point, this means the entire documented Compiler API surface above should be treated as **only valid for TypeScript ≤ 6.x**, not 7.x.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] **Version-sensitive / significant limitation:** TypeScript 7.0 itself "does not ship with an API" at all — the official announcement states this explicitly delays support for tools embedding the compiler programmatically (cited examples: Vue, Angular, Svelte tooling) until a planned TypeScript 7.1. This is a major discontinuity for any skill/tool that programmatically drives `tsc` internals rather than shelling out to the `tsc` CLI.

[Source: https://www.typescriptlang.org/docs/handbook/compiler-options.html] (referenced via the docs navigation) The `tsc` CLI itself is documented as the primary command-line API surface — `tsc`, `tsc --init`, `tsc -b`/`--build`, `tsc --watch`, plus diagnostic flags. See Sections 4 and 8 for option details actually verified.

[Source: https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html] A separate, stable "API surface" is TypeScript's JSDoc type-annotation support for plain `.js` files: documented tags include `@type`, `@import`, `@param`/`@returns`, `@typedef`/`@callback`, `@template` (generics), `@satisfies`, class-modifier tags (`@public`/`@private`/`@protected`/`@readonly`/`@override`), `@extends`/`@augments`, `@implements`, `@constructor`/`@class`, `@this`, and doc-only tags `@deprecated`/`@see`/`@link`. The docs note unsupported tags (`@memberof`, `@yields`, `@member`, and any undocumented tag) and that type-bearing tags only take effect in `.js` files (or JSDoc comments in `.ts` files for the doc-only tags).

---

## 4. Configuration

[Source: https://www.typescriptlang.org/tsconfig/] Configuration is centered on `tsconfig.json`, whose `compilerOptions` are organized by the official reference into named categories: Type Checking (~20 options, e.g. `strict`, `noImplicitAny`, `strictNullChecks`, `noImplicitReturns`), Modules (~19 options, e.g. `module`, `moduleResolution`, `paths`, `resolveJsonModule`), Emit (~21 options, e.g. `declaration`, `outDir`, `sourceMap`, `noEmit`), JavaScript Support (`allowJs`, `checkJs`, `maxNodeModuleJsDepth`), Editor Support (`plugins`, `disableSizeLimit`), Interop Constraints (`esModuleInterop`, `allowSyntheticDefaultImports`, `isolatedModules`), Backwards Compatibility (legacy/deprecated options), Language and Environment (`target`, `lib`, `jsx`, `experimentalDecorators`), Compiler Diagnostics (`diagnostics`, `listFiles`, `traceResolution`, `explainFiles`), Projects (`composite`, `incremental`, `references`, `tsBuildInfoFile`), Output Formatting, Completeness (`skipLibCheck`, `skipDefaultLibCheck`), and Watch Options.

[Source: https://www.typescriptlang.org/tsconfig/] The reference marks a specific set of options as "Recommended" for stricter type safety: `strict` (umbrella), `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `noImplicitThis`, `exactOptionalPropertyTypes`, `noImplicitOverride`.

[Source: https://www.typescriptlang.org/tsconfig/] Version-sensitive additions noted directly on the reference: `noUncheckedSideEffectImports` was added in TypeScript 5.6; `rewriteRelativeImportExtensions` was added in TypeScript 5.7.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/] **Version-sensitive — TypeScript 6.0 (March 2026) changed several long-standing defaults:** `strict` now defaults to `true` (was `false`); `module` now defaults to `esnext` (was `commonjs`); `target` now defaults to a "floating current-year" `es2025`; `types` now defaults to `[]` — an empty array — rather than automatically including all visible `@types/*` packages, meaning most Node.js projects now need to explicitly add `"types": ["node"]`. `noUncheckedSideEffectImports` and became `true` by default; `libReplacement` became `false` by default.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/] **Version-sensitive — options removed/deprecated in TypeScript 6.0:** `target: es5` removed (ES2015 is now the effective minimum); `--downlevelIteration` removed; `--moduleResolution classic` removed; `--outFile` removed (external bundlers recommended instead); `--module amd`/`umd`/`systemjs` removed; `--moduleResolution node` (aka `node10`) deprecated in favor of `nodenext`/`bundler`; `baseUrl` deprecated in favor of explicit `paths`; `esModuleInterop: false` and `allowSyntheticDefaultImports: false` no longer effective (always-on behavior now assumed); `--alwaysStrict false` removed. A migration escape hatch, `"ignoreDeprecations": "6.0"`, suppresses these warnings temporarily.

[Source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html] **Version-sensitive — TypeScript 5.9** (the release immediately preceding 6.0) shipped a leaner `tsc --init` template with prescriptive defaults (`"module": "nodenext"`, `"target": "esnext"`, `"strict": true`, `"jsx": "react-jsx"`), the new `--module node20` option (models Node 20 behavior, implies `target: es2023`, and — unlike `nodenext` — is not expected to gain new behavior in future releases), and support for the ECMAScript `import defer` syntax (namespace-only, requires `--module preserve` or `--module esnext`).

[Source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html] **Version-sensitive breaking change in 5.9:** `lib.d.ts` changed so `ArrayBuffer` is no longer a supertype of typed-array types (e.g. `Uint8Array`), which can surface new type errors around `Buffer`/typed-array interop; the docs suggest updating `@types/node`, using precise buffer types, or accessing `.buffer` explicitly as fixes.

[Source: https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html] A minimal starter `tsconfig.json` for adopting TypeScript in an existing JS project is documented with `outDir`, `allowJs`, and (in the example shown) `target: "es5"`. **Unresolved:** this example's use of `target: "es5"` in the fetched migration-guide content appears inconsistent with TypeScript 6.0's documented removal of `es5` as a valid `target` value (see above) — it is unclear whether the live migration-guide page has simply not been updated post-6.0, or whether the page content returned to this research was stale/cached at fetch time. Treat the `es5` example on that specific page as unverified for TypeScript ≥ 6.0 until directly re-confirmed.

---

## 5. Recommended Patterns

[Source: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html] Use lowercase primitive types (`number`, `string`, `boolean`, `symbol`, `object`) rather than the boxed/capitalized wrapper types (`Number`, `String`, `Boolean`, `Symbol`, `Object`), since the boxed types describe rarely-used runtime wrapper objects.

[Source: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html] For callback types, use `void` as the return type when a callback's return value is intentionally ignored (this prevents callers from accidentally relying on a return value that isn't meaningfully used), and write callback parameters as non-optional (callers may always supply a callback that accepts fewer parameters than declared, so making parameters optional adds no safety and can hide bugs).

[Source: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html] For function overloads: order overload signatures from most specific to least specific — TypeScript resolves to the first matching overload, so a general signature listed first will shadow more specific ones; prefer optional parameters over near-duplicate overloads that only differ by trailing arguments; prefer a union type parameter over overloads that differ only in one parameter's type.

[Source: https://www.typescriptlang.org/docs/handbook/enums.html] For modern TypeScript, the docs explicitly suggest an `as const` object plus a derived union type as a preferred alternative to `enum` in many cases: `const ODirection = { Up: 0, ... } as const; type Direction = typeof ODirection[keyof typeof ODirection];` — stated as keeping "your codebase aligned with the state of JavaScript."

[Source: https://github.com/microsoft/TypeScript/wiki/Performance] Recommended performance-oriented patterns: prefer `interface` extension over intersection types where possible (interface relationships are cached by the checker, whereas intersections are not cached as a whole); add explicit return-type annotations on exported functions (produces more compact, named types instead of large inferred anonymous ones, especially relevant for `.d.ts` emission); prefer base-type/inheritance hierarchies over large union types (union comparison is pairwise/quadratic); extract complex conditional/mapped types into named type aliases so the checker can cache them instead of re-evaluating structurally-identical expressions repeatedly.

[Source: https://www.typescriptlang.org/docs/handbook/project-references.html] For multi-package/large codebases, use **project references** (`composite: true` + `references` in `tsconfig.json`) to split a program into independently buildable units, enabling `tsc -b`/`--build` to build only out-of-date dependency projects in correct order — documented as improving both build time and editor memory usage.

[Source: https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html] When publishing a typed npm package, bundle your own `.d.ts` and point `package.json`'s `"types"` (a.k.a. `"typings"`, documented as a synonym) field at it; list any `@types/*` packages your public API depends on under `"dependencies"` (not `devDependencies`) so consumers automatically receive required type packages; avoid `/// <reference path="...">` in favor of `/// <reference types="...">`; avoid copying another package's type declarations rather than depending on its published `@types` package.

---

## 6. Anti-Patterns

[Source: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html] Avoid unused generic type parameters — every declared generic parameter should actually appear in the resulting type signature, or it provides false type safety.

[Source: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html] Avoid `any`, including as an implicit callback return type; the docs recommend `unknown` when you need to accept a value you won't directly interact with, reserving `any` largely for JS-to-TS migration scenarios.

[Source: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html] Avoid writing multiple overloads that differ only in callback arity (e.g. separate overloads for zero-arg vs. one-arg callback) — the docs recommend a single overload using the callback's maximum arity, since callers can supply a callback with fewer parameters.

[Source: https://www.typescriptlang.org/docs/handbook/enums.html] Avoid **ambient `const enum`** declarations published in `.d.ts` files for consumption by other packages. Documented pitfalls: they are incompatible with consumers using `isolatedModules`; because `const enum` values are inlined at the call site at compile time, a mismatch between the const-enum-declaring package's build-time version and its published runtime version can silently produce wrong inlined values — and the docs specifically warn this bug class is easy to miss because "it is common to run automated tests at roughly the same time as projects are built, with the same dependency versions, which misses these bugs completely." Recommended mitigations: ban const enums via lint rule, or use `preserveConstEnums` to allow local inlining while not publishing ambient const enums.

[Source: https://github.com/microsoft/TypeScript/wiki/Performance] Misconfigured/missing `include`/`exclude` glob patterns are called out as a frequent, avoidable cause of slow compiles and editor slowness — the docs recommend always excluding `node_modules` and hidden directories with globs like `**/node_modules` (not a bare `node_modules`, which misses nested occurrences), and explicitly scoping `include` (e.g. `["src"]`) rather than letting the compiler discover the whole workspace.

---

## 7. Security

[Source: https://www.typescriptlang.org/docs/handbook/] Not documented / could not verify: a search of `typescriptlang.org` and the official Handbook/Reference navigation turned up no dedicated security-guidance page (no CVE/security-advisory process page, no "secure coding in TypeScript" guide). TypeScript's own documentation does not appear to treat security as a distinct documented topic separate from general type-safety.

[Source: https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals] The closest documented adjacent claim is the design non-goal that TypeScript does not aim to implement a fully sound type system, and correspondingly (Section 1/2) that certain unsound behaviors (bivariant method parameters, permissive excess-property checks on non-literal assignments) are intentional trade-offs — meaning TypeScript's static checks should not be relied upon as a complete guarantee against type-confusion-adjacent runtime bugs. [Inference, not confirmed in docs] This is a design-philosophy statement, not security guidance, and should not be extrapolated into specific security claims.

Unresolved: whether Microsoft publishes a separate TypeScript-compiler security-disclosure/CVE process (as it does for many other Microsoft OSS projects) was not confirmed from typescriptlang.org itself in this pass — it would live on the `microsoft/TypeScript` GitHub repo's security policy if it exists, which was not directly checked as a distinct citation here.

---

## 8. Performance

[Source: https://github.com/microsoft/TypeScript/wiki/Performance] The official performance guidance (compiler team's wiki page) covers: writing performant type-level code (interfaces over intersections for caching, explicit return types, named types over large unions, avoiding deeply nested/recomputed conditional types); `tsconfig.json` tuning (explicit `include`, exclude `node_modules`/hidden dirs, `"types": []` to avoid loading unnecessary ambient `@types` packages, `skipLibCheck: true` to skip re-checking `.d.ts` files, `--incremental` to persist compile state across runs); project structuring via project references (suggested guidance: 5–20 interdependent projects, kept evenly sized, grouping files that are typically edited together); and build-tool separation of concerns (e.g. `fork-ts-checker-webpack-plugin` to run type-checking asynchronously off the main emit path, `isolatedModules` to let per-file transpilers like Babel/`ts-loader`-alternatives skip full program semantic analysis).

[Source: https://github.com/microsoft/TypeScript/wiki/Performance] Documented diagnostic tooling: `tsc --extendedDiagnostics` (phase-by-phase timing breakdown), `tsc --listFilesOnly` (lists included files), `tsc --explainFiles` (explains why each file was included), `tsc --traceResolution` (module-resolution debugging), and `tsc --generateTrace <folder>` (produces a trace analyzable with the official `@typescript/analyze-trace` tool or Chrome DevTools' trace viewer). For editor slowness specifically, VS Code's `"typescript.tsserver.log": "verbose"` setting is documented for diagnosing `tsserver` performance issues.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] **Version-sensitive, major performance claim:** TypeScript 7.0's Go-native compiler reports "speedups between 8x and 12x on full builds" versus TypeScript 6.x on real-world projects, with a specific cited example of VS Code's own codebase compiling in "10.6 seconds versus 125.7 seconds with TypeScript 6" (≈11.9x), and memory usage reported as decreasing 6–26% depending on project. [Inference, not confirmed in docs] These are the TypeScript team's own reported benchmark figures from the announcement post; no independent third-party benchmark was checked, and these numbers should be treated as vendor-reported until corroborated.

---

## 9. Testing

Not documented / could not verify: `typescriptlang.org`'s official Handbook and Reference sections contain no dedicated page on unit testing, test runners, or testing patterns — TypeScript does not ship or officially endorse a testing framework, and a targeted search of the official site returned no dedicated testing guidance.

[Source: https://www.typescriptlang.org/tsconfig/#isolatedModules] The only testing-adjacent officially documented mechanism found is the `isolatedModules` compiler option (Interop Constraints category), which exists because some transpiler-based tools (including per-file transpiling test runners/bundler-integrated test tooling) compile files independently of the full TypeScript program and therefore cannot support certain whole-program-dependent constructs (e.g. ambient `const enum`, as noted in Section 6). [Inference, not confirmed in docs] This is inferred to be relevant to testing setups that use non-`tsc` transpilation (e.g. via Babel or esbuild-based test runners), but the docs frame it generically around transpilers, not testing specifically.

[Source: https://www.typescriptlang.org/docs/handbook/integrating-with-build-tools.html] Testing tools themselves are absent from this page's coverage of build-tool integrations (it covers Babel, Browserify, Gulp, Webpack, Rollup, Vite, Grunt, Svelte, Jspm, MSBuild, NuGet — see Section 16) — no Jest/Mocha/Vitest/Playwright integration guidance is present on official TypeScript docs.

---

## 10. Deployment

[Source: https://www.typescriptlang.org/download/] The official install/download page documents three install routes: npm (`npm install typescript --save-dev`, run via `npx tsc`; also documented as supporting yarn and pnpm with lockfiles), a NuGet package (`Microsoft.TypeScript.MSBuild`) for MSBuild/.NET projects, and a Visual Studio extension. The page recommends per-project installation over global installation for reproducible builds across a team.

[Source: https://www.typescriptlang.org/docs/handbook/project-references.html] For deploying/building multi-package TypeScript codebases, `tsc -b`/`--build` (project-references build mode) is documented as the mechanism: it locates all referenced projects, detects out-of-date dependency projects, and builds them in dependency order. `tsc -b` is documented to behave "as if `noEmitOnError` is enabled" — i.e., a build-mode invocation will not emit output for a project that has type errors. Documented CLI forms: `tsc -b`, `tsc -b src`, `tsc -b src test` (multiple configs), `tsc -b --watch`, `tsc -b --force`, `tsc -b --clean`.

[Source: https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html] For deploying TypeScript as a published library (npm package), the documented pattern is emitting `.d.ts` declaration files alongside compiled JS and pointing `package.json`'s `"types"` field at the entry declaration file (see Section 5).

TypeScript itself compiles to plain JavaScript for execution — [Source: https://www.typescriptlang.org/docs/handbook/2/basic-types.html] type erasure means the deployed artifact is ordinary JS with no TypeScript-specific runtime dependency, so "deployment" of a TypeScript project is, per the docs' own framing, deployment of its compiled JavaScript output plus (for libraries) accompanying `.d.ts` files.

---

## 11. Migration

[Source: https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html] The official JS→TS migration guide recommends: separate source (`.js`) from build output directory; start with a permissive `tsconfig.json` (`allowJs: true`, an explicit `outDir`) so the project still compiles while files are gradually converted; rename files from `.js`/`.jsx` to `.ts`/`.tsx` incrementally rather than all at once, tolerating compile errors during the transition; convert CommonJS/AMD-style `require`/`module.exports` to `import`/`export` syntax (or `import foo = require("foo")` / `export = foo` for CJS interop); install `@types/*` packages for untyped dependencies; then progressively enable stricter checks (`noImplicitAny`, `strictNullChecks`, `noImplicitThis`, `noImplicitReturns`, `noFallthroughCasesInSwitch`) rather than turning on full `strict` immediately.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/] **Version migration (6.0→7.0 and pre-6.0→6.0):** the TypeScript 6.0 announcement documents `"ignoreDeprecations": "6.0"` as a temporary suppression flag for newly-deprecated options, a `--stableTypeOrdering` flag to align type-ordering behavior with 7.0's deterministic ordering ahead of time (documented as potentially causing "~25% type-checking slowdown" when enabled), and mentions a `ts5to6` tool for automated config migration. The announcement recommends projects plan to move toward either `--module preserve` with `--moduleResolution bundler`, or `--module nodenext`, as the durable long-term module configuration.

[Source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html] TypeScript 6.0 is explicitly framed in its own release notes as a transitional/bridge release: deprecated options continue to function (with `ignoreDeprecations` opt-out of warnings) but are documented as being **fully removed in TypeScript 7.0**.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] TypeScript 7.0 is documented as deliberately adopting 6.0's new defaults and behavior for compatibility, rather than introducing another wave of default changes — i.e., the intended migration path is 6.0 first (absorb default/deprecation changes), then 7.0 (absorb the native-compiler swap with minimal further config churn).

TypeScript does not document migration guidance to/from a comparable alternative language (e.g. Flow) as part of its official docs; [Inference, not confirmed in docs] the "Migrating from JavaScript" tutorial is the closest analog and is the only migration narrative TypeScript's own docs provide, since JavaScript is the substrate TypeScript compiles to/from rather than a competing static-typing tool.

---

## 12. Version Information

[Source: https://www.npmjs.com/package/typescript] Current published stable version at research time (2026-09-09): **TypeScript 7.0.2** (per npm search results, published roughly 2 months prior to this research date).

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] TypeScript 7.0 (the Go-native compiler rewrite) was released **July 8, 2026**.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/] TypeScript 6.0 (the JS-implemented "bridge" release preceding 7.0) was released **March 23, 2026**.

[Source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html] TypeScript 5.9 preceded 6.0 in the same numbering line (the last release before the 5.x→6.0→7.0 progression documented above).

Release cadence: [Inference, not confirmed in docs] based on the observed spacing between the confirmed dated releases above (5.9 → 6.0 → 7.0 within roughly a 4–5 month window in early-to-mid 2026) this is consistent with TypeScript's historically reported quarterly-ish minor-release cadence, but this research could not obtain a live, current official cadence statement to cite directly — a fetch of the `microsoft/TypeScript` GitHub wiki Roadmap page returned only pre-2023 release history and did not reflect current (2026) content, which is flagged below as unresolved rather than cited as fact.

Unresolved: the `microsoft/TypeScript` wiki "Roadmap" page fetch returned content that appears stale (referencing TypeScript 5.0/4.x as the most recent releases, with no information past March 2023), inconsistent with the confirmed 2026 versions above. This is most likely a stale cache/fallback in the fetch pipeline rather than the wiki page's actual live content, but it could not be independently re-verified in this pass — do not treat the specific "~3 months" cadence figure surfaced by that fetch as a confirmed official claim; it is included above only as a directionally-consistent inference from independently-dated releases, not as a direct citation.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/] TypeScript 6.0's own announcement states the team considered TypeScript 7.0 "extremely close to completion" at 6.0's release time and pointed early adopters to the `@typescript/native-preview` npm package to try the Go compiler ahead of its stable release — corroborating the short 6.0→7.0 gap.

LTS/support-window status: [Inference, not confirmed in docs] TypeScript's official docs do not describe an LTS or extended-support-window model comparable to, e.g., Node.js LTS — each minor/major version supersedes the prior one with no separately maintained long-term branch documented on typescriptlang.org. This is an inference from absence of any LTS-policy page found, not a positive confirmed claim; flagged accordingly as **Not documented / could not verify** rather than asserted as fact.

---

## 13. Breaking Changes

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/] **TypeScript 6.0 breaking changes** (see Section 4 for full option-level detail): default changes to `strict` (→ `true`), `module` (→ `esnext`), `target` (→ floating `es2025`), `types` (→ `[]`), `noUncheckedSideEffectImports` (→ `true`), `libReplacement` (→ `false`); removed options `target: es5`, `--downlevelIteration`, `--moduleResolution classic`, `--outFile`, `--module amd/umd/systemjs`; deprecated `baseUrl`, `--moduleResolution node` (node10); `esModuleInterop`/`allowSyntheticDefaultImports` no longer accept `false`; legacy `module Foo { }` namespace syntax becomes an error (must use `namespace` keyword); running bare `tsc foo.ts` in a directory that also has a `tsconfig.json` now errors (requires `--ignoreConfig` to override the previous implicit behavior).

[Source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html] **TypeScript 5.9 breaking change:** `ArrayBuffer` is no longer a supertype of typed-array types in `lib.d.ts`, which can surface new errors involving `Buffer`/`Uint8Array` interop (see Section 4 for the documented fix pattern). Also documented: generic type-argument inference "leak" fixes that may surface new errors requiring explicit type arguments in some call sites.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] **TypeScript 7.0 breaking changes:** `target: es5` remains unsupported (carried over from 6.0's removal); `baseUrl` removed (use `paths` relative to the project root instead); `rootDir` now defaults to `./` (the tsconfig directory) rather than being inferred, which the announcement notes requires explicit configuration in some existing projects; `types` continues to default to an empty array; and — most significantly for tooling authors — **TypeScript 7.0 ships with no programmatic Compiler API at all**, deferring API support (needed by embedders like Vue/Angular/Svelte language tooling) to a planned TypeScript 7.1.

[Source: https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API] Reiterating from Section 3 because it is itself a breaking-change fact: the entire pre-7.0 Compiler API (`createProgram`, `createSourceFile`, `transpileModule`, `LanguageService`, etc.) is explicitly flagged by the official wiki as describing "TypeScript 6.0 and earlier" only, with "a completely different API" promised for 7.1 — i.e., any tool built against the documented 6.x API surface should expect it to not carry forward unchanged.

---

## 14. Limitations

[Source: https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals] Explicitly documented non-goals / limitations by design: TypeScript does not implement a fully sound type system (explicit trade-off for productivity); does not aggressively optimize runtime performance of emitted code (prioritizes idiomatic/recognizable JS output over maximal runtime speed); does not provide an end-to-end build pipeline (defers to external tools); does not provide runtime type information/reflection by default; does not provide additional runtime functionality or libraries beyond describing what already exists in the target environment.

[Source: https://www.typescriptlang.org/docs/handbook/type-compatibility.html] Documented specific unsoundness: method parameters are bivariant (narrower argument types are unsoundly permitted in method-syntax subtypes, though not in property-typed function subtypes); optional and rest parameters are treated as interchangeable, and rest parameters are effectively treated as an infinite sequence of optional parameters; object literals get excess-property checking, but values assigned indirectly through a variable do not, so "extra" properties can silently pass through in the latter case. The docs describe these as deliberate, "carefully considered" trade-offs necessary to model common JavaScript idioms rather than oversights.

[Source: https://www.typescriptlang.org/docs/handbook/2/basic-types.html] Type erasure is itself a hard limitation: because all type information disappears at compile time, TypeScript provides no runtime type-checking, no `instanceof`-style checks against structural/interface types, and no reflection over interfaces or type aliases at runtime.

[Source: https://github.com/microsoft/typescript/wiki/faq] The compiler team's own FAQ acknowledges some structural-typing outcomes as looking wrong even though intentional — e.g., empty interfaces (`{}`) accept nearly any value, and objects are not "sealed," so structurally-compatible-but-excess-property objects pass type checks in many contexts. The FAQ states some of these behaviors are treated as non-negotiable because "fixing" them would break widely-relied-upon patterns (the docs cite array/method-related patterns specifically).

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] **Version-sensitive limitation:** as of TypeScript 7.0 specifically, there is no supported programmatic Compiler API (see Sections 3 and 13) — this is a temporary but currently-real limitation for any tool that needs to embed TypeScript's checker/compiler rather than shell out to `tsc`.

---

## 15. Debugging

[Source: https://code.visualstudio.com/docs/typescript/typescript-debugging] Official VS Code guidance (Microsoft-maintained docs for the editor most closely associated with TypeScript) documents: enabling `sourceMap: true` in `tsconfig.json` (or the `--sourcemap` CLI flag) to generate source maps that let the debugger map compiled JS back to original `.ts` source; both separate `.map` files and inlined (data-URL) source maps are supported, though inlined *source content* has more limited support; a `launch.json` debug configuration is generated via VS Code's Run-and-Debug view, typically including a `preLaunchTask` pointing at the TypeScript build task and an `outFiles` glob telling the debugger where compiled JS output lives; breakpoints can be set directly in `.ts` files and are mapped to the corresponding emitted JS via source maps at debug time. The documented most-common failure mode is a missing `sourceMap: true` in `tsconfig.json` or a missing/incorrect `outFiles` in `launch.json`, which prevents the debugger from locating the compiled output relative to the TypeScript source.

[Source: https://www.typescriptlang.org/tsconfig/] Related source-map compiler options documented in the official tsconfig reference (Emit category): `sourceMap`, `inlineSourceMap`, `inlineSources`, `mapRoot`, `sourceRoot` — [Inference, not confirmed in docs] exact per-option semantics for `mapRoot`/`sourceRoot` were not independently re-verified beyond the category listing in this pass.

[Source: https://github.com/microsoft/TypeScript/wiki/Performance] For diagnosing compiler/type-checker behavior (as distinct from runtime debugging of compiled code), the official performance wiki documents `tsc --extendedDiagnostics`, `--listFilesOnly`, `--explainFiles`, `--traceResolution`, and `--generateTrace <folder>` (analyzable via the official `@typescript/analyze-trace` package or Chrome DevTools), plus VS Code's `"typescript.tsserver.log": "verbose"` setting for diagnosing editor/language-service slowness or incorrect behavior.

---

## 16. Integration

[Source: https://www.typescriptlang.org/docs/handbook/integrating-with-build-tools.html] The official build-tools integration page documents setup for: **Babel** (`@babel/preset-typescript` — transpile-only, no type-checking), **Browserify** (via the `tsify` plugin), **Gulp** (via `gulp-typescript`), **Webpack** (via `ts-loader`, or the alternative `awesome-typescript-loader`), **Rollup** (via `@rollup/plugin-typescript`, requiring `typescript` and `tslib` as peer dependencies), **Vite** (native `.ts` support, explicitly documented as transpile-only/no type-checking — type errors must be caught by a separate `tsc` invocation), **Grunt** (`grunt-ts` noted as no longer maintained; `grunt-browserify` + `tsify` recommended instead), **Svelte** (via `svelte-preprocess`, requiring `typescript` as a separate dependency, `<script lang="ts">`), **Jspm** (documented as beta support via `jspm@beta`), and **MSBuild/NuGet** for .NET/Visual Studio projects (`Microsoft.TypeScript.Default.props`/`.targets` imports, `Microsoft.TypeScript.MSBuild` NuGet package).

[Source: https://www.typescriptlang.org/docs/handbook/integrating-with-build-tools.html] A documented recurring pattern across bundler integrations: several tools (Vite, Babel's TS preset) perform **transpilation only** and do not perform TypeScript's semantic type-checking — the docs note type-checking must be run separately (e.g. via `tsc --noEmit`, or a plugin like `fork-ts-checker-webpack-plugin` referenced in the performance docs) when using these transpile-only pipelines.

[Source: https://www.typescriptlang.org/docs/handbook/modules/theory.html] Editor/tooling integration is documented as built on the Language Service layer (Section 2), which provides the incremental, file-versioned API that VS Code and other LSP-based editors use for live diagnostics, completions, and refactors — [Inference, not confirmed in docs] this Language-Service-based integration model is described at the architecture level; this pass did not independently re-fetch a dedicated official "Using the Language Service API" page for further detail.

[Source: https://www.typescriptlang.org/docs/handbook/babel-with-typescript.html] (page present in official docs navigation, referenced from Section 16's Babel integration content) TypeScript is documented as interoperating with Babel-based toolchains specifically through `isolatedModules`-safe code (per-file transpilation constraints) since Babel transpiles each file independently without TypeScript's whole-program type information.

[Source: https://nodejs.org/api/typescript.html] **Not a TypeScript-official source; cited here only for Node's own documented behavior, since it materially affects how TypeScript integrates with the Node runtime.** [Source: https://nodejs.org/api/typescript.html] Node.js documents native, buit-in "type stripping" support for running `.ts` files directly: introduced experimentally in Node v22.6.0, enabled by default from v23.6.0/v22.18.0, and marked stable as of v25.2.0/v24.12.0, with the `--experimental-transform-types` flag removed (behavior now standard) in v26.0.0. Node's type stripping explicitly performs **no type-checking** (types are erased as whitespace only) and **ignores `tsconfig.json` entirely** — meaning path-alias resolution (`paths`), syntax downleveling, and source-map generation configured via `tsconfig.json` are not honored by Node's native runner. Node's docs list unsupported constructs for type-stripping: `enum` declarations, `namespace` blocks containing runtime code, parameter properties, import aliases requiring transformation, and (at time of that page's writing) TC39 Stage-3 decorators; `.tsx` is documented as unsupported by Node's stripper. For full-featured TypeScript execution without a separate build step, Node's own docs point to third-party tools such as `tsx`.

[Source: https://www.typescriptlang.org/docs/handbook/decorators.html] TypeScript's decorator support is documented in two generations: the original `experimentalDecorators` compiler-flag-gated implementation (based on a since-superseded, older TC39 decorators proposal), and — per the docs' own cross-reference — stage-3 ECMAScript decorator support (without the `experimentalDecorators` flag) available since TypeScript 5.0. `emitDecoratorMetadata` (combined with `experimentalDecorators`) is documented as enabling `reflect-metadata`-based runtime metadata emission for the legacy decorator model specifically.

---

## 17. Production Considerations

[Source: https://www.typescriptlang.org/docs/handbook/project-references.html] For production builds of multi-package codebases, the docs recommend a "solution" `tsconfig.json` containing only `references` (and an empty `files` array), separating leaf-node projects (source, tests, libraries) with their own configs, using `declaration: true` + `composite: true` on referenced projects, and optionally `declarationMap: true` to enable cross-project "Go to Definition"/refactoring. `tsc -b` behaves as if `noEmitOnError` is always on, so a project with type errors will not produce build output — a relevant CI/production-build gating behavior. The docs also flag that generated `.d.ts` outputs and their timestamps matter for incremental-build correctness in version-controlled/CI workflows (stale or missing `.d.ts` outputs after a fresh clone can block downstream project builds until rebuilt).

[Source: https://github.com/microsoft/TypeScript/wiki/Performance] For production-scale codebases, `skipLibCheck: true` is documented as a common trade-off (faster builds by not re-type-checking third-party `.d.ts` files, at the cost of not catching certain library-declaration inconsistencies), and `--incremental` build-state caching plus project references are the documented scaling mechanisms for keeping both `tsc` and editor (`tsserver`) performance acceptable as a codebase grows.

[Source: https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html] For production library publishing, the documented practice of listing `@types/*` dependencies under `dependencies` (not `devDependencies`) ensures downstream consumers automatically receive necessary type packages at install time in production dependency graphs, rather than requiring manual `@types` installation.

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] Version-sensitive production consideration: teams currently relying on programmatic access to the TypeScript compiler in production build/tooling pipelines (rather than invoking the `tsc` CLI as a subprocess) cannot yet upgrade to TypeScript 7.0 without a compatibility gap, since 7.0 ships no Compiler API — this is a concrete adoption blocker documented by the TypeScript team itself, not an inferred risk.

---

## Summary of Sources Consulted

- `https://www.typescriptlang.org/docs/` — documentation homepage/navigation
- `https://www.typescriptlang.org/docs/handbook/2/basic-types.html` — core concepts, type erasure, strictness
- `https://www.typescriptlang.org/docs/handbook/type-compatibility.html` — structural typing, documented unsoundness
- `https://www.typescriptlang.org/docs/handbook/enums.html` — enum caveats, `as const` alternative
- `https://www.typescriptlang.org/docs/handbook/decorators.html` — decorators, experimentalDecorators, stage-3 decorators
- `https://www.typescriptlang.org/docs/handbook/modules/theory.html` — module architecture, host modeling, resolution
- `https://www.typescriptlang.org/docs/handbook/project-references.html` — project references, `tsc -b`
- `https://www.typescriptlang.org/docs/handbook/integrating-with-build-tools.html` — build-tool integrations
- `https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html` — JS→TS migration guide
- `https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html` — JSDoc type-annotation API surface
- `https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html` — declaration-file patterns/anti-patterns
- `https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html` — publishing typed packages
- `https://www.typescriptlang.org/docs/handbook/babel-with-typescript.html` — Babel interop reference
- `https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html` — TS 5.9 release notes
- `https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html` — TS 6.0 release notes
- `https://www.typescriptlang.org/tsconfig/` — tsconfig / compiler options reference
- `https://www.typescriptlang.org/download/` — installation instructions
- `https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/` — official TS 6.0 announcement
- `https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/` — official TS 7.0 (native/Go) announcement
- `https://github.com/microsoft/TypeScript/wiki/Architectural-Overview` — compiler architecture (pre-7.0)
- `https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API` — Compiler API reference (≤6.0, flagged 7.1 rewrite)
- `https://github.com/microsoft/TypeScript/wiki/Performance` — official performance tuning/diagnostics guidance
- `https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals` — official goals/non-goals
- `https://github.com/microsoft/typescript/wiki/faq` — official FAQ (soundness, structural typing caveats)
- `https://github.com/microsoft/TypeScript/wiki/Roadmap` — fetch returned stale/unreliable content; not used as a direct citation, flagged Unresolved
- `https://code.visualstudio.com/docs/typescript/typescript-debugging` — VS Code (Microsoft) official TypeScript debugging guidance
- `https://nodejs.org/api/typescript.html` — Node.js official docs, cited only for Node's native TS type-stripping behavior (integration section)
- `https://www.npmjs.com/package/typescript` — current published version confirmation
