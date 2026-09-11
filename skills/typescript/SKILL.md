---
name: TypeScript
description: >-
  TypeScript's type system, tsconfig configuration, declaration files, and the
  TypeScript 6.0/7.0 breaking-defaults and Go-native-compiler transition. Use
  when the codebase has a tsconfig.json, .ts/.tsx files, or the task is about
  TypeScript types, compiler options, or migration/upgrade between TypeScript
  versions. Not for general code-quality conventions independent of language
  (use code-quality), or a specific framework's own TypeScript integration
  patterns (use that framework's skill).
spec_version: "1.0"
---

## Purpose & scope

Apply TypeScript correctly and version-appropriately: its structural,
gradually-strict type system, `tsconfig.json` configuration, declaration
files, and — critically for anything authored in 2026 — the TypeScript
5.9 -> 6.0 -> 7.0 breaking-defaults transition. The *general* code-quality
method (naming, structure, avoiding over-engineering) comes from the parent
skill, `SK-CONV-003`; this skill supplies TypeScript's own specifics.
ECMAScript language-spec behavior is folded into this skill per the taxonomy
rather than authored as a separate skill.

## When to use / When not to use

**Use** when a `tsconfig.json`, `.ts`/`.tsx`/`.mts`/`.cts` file is present, or
the task is about TypeScript's type system, compiler options, declaration
files, or a version upgrade/migration (including a JS-to-TS migration).
**Do not use** for generic naming/structure/readability conventions
independent of language (route to `SK-CONV-003`), or a specific framework's
own TypeScript integration mechanics when the type system itself isn't in
question (route to that framework's skill — `SK-TECH-react`, `SK-TECH-vue`,
`SK-TECH-nodejs`, etc.).

## Knowledge

**Type system fundamentals.** TypeScript is a static type-checker built as a
superset of JavaScript, adding compile-time-only type annotations; types are
fully erased at emit, so the emitted JavaScript has no runtime trace of them
[Source: https://www.typescriptlang.org/docs/handbook/2/basic-types.html].
It uses **structural typing** — `x` is compatible with `y` if `x` has at
least the members `y` requires, regardless of declared type names — chosen
because it models JavaScript's anonymous-object idioms better than nominal
typing [Source: https://www.typescriptlang.org/docs/handbook/type-compatibility.html].
The type system is explicitly **not fully sound by design**: documented
unsound-but-intentional behaviors include method-parameter bivariance,
optional/rest-parameter interchangeability, and permissive excess-property
checks on non-literal assignments — deliberate trade-offs against being
"unnecessarily restrictive" on common JS patterns, not oversights
[Source: https://www.typescriptlang.org/docs/handbook/type-compatibility.html].
Strictness is gradual/opt-in via individual flags (`noImplicitAny`,
`strictNullChecks`, ...) or the umbrella `strict` flag, supporting
incremental adoption from plain JavaScript
[Source: https://www.typescriptlang.org/docs/handbook/2/basic-types.html].

**TypeScript 6.0 changed long-standing defaults (2026-03-23).** `strict` now
defaults to `true` (was `false`); `module` now defaults to `esnext` (was
`commonjs`); `target` now defaults to a floating current-year `es2025`;
`types` now defaults to `[]` instead of auto-including all visible
`@types/*` packages, so **most Node.js projects now need an explicit
`"types": ["node"]`**; `noUncheckedSideEffectImports` and `libReplacement`
also flipped (`true`/`false` respectively). Removed/deprecated in the same
release: `target: es5`, `--downlevelIteration`, `--moduleResolution classic`,
`--outFile`, `--module amd/umd/systemjs`; `baseUrl` and
`--moduleResolution node` (node10) deprecated in favor of `paths` and
`nodenext`/`bundler`. A temporary escape hatch, `"ignoreDeprecations": "6.0"`,
suppresses the new warnings during migration
[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/].
*Applies to: TypeScript >=6.0.*

**TypeScript 7.0 is a Go-native compiler rewrite — with no Compiler API.**
Released 2026-07-08, TypeScript 7.0 ("tsgo") reimplements the compiler
natively in Go (replacing the JS implementation used through 6.x) while
preserving 6.0's behavior, adding multithreaded compilation
(`--checkers`/`--builders`) and a rebuilt `--watch` mode. **Most
significantly: TypeScript 7.0 ships with no programmatic Compiler API at
all** — the official announcement states this explicitly delays support for
tools that embed the compiler programmatically, naming Vue, Angular, and
Svelte tooling as examples, until a planned **TypeScript 7.1**
[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/].
*Applies to: TypeScript >=7.0 <7.1.* The pre-7.0 Compiler API itself
(`ts.createProgram()`, `ts.createSourceFile()`, `ts.transpileModule()`, the
`TypeChecker`, the `LanguageService`) is documented via the compiler wiki,
which states its own content "currently describe[s] TypeScript 6.0 and
earlier. TypeScript 7.1 will have a completely different API"
[Source: https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API].
*Applies to: that documented API surface is valid for TypeScript <=6.0 only.*

**Other version-tagged facts worth knowing:**
- `noUncheckedSideEffectImports` added in 5.6; `rewriteRelativeImportExtensions`
  added in 5.7 *(applies to: >=5.6 / >=5.7 respectively)*
  [Source: https://www.typescriptlang.org/tsconfig/].
- `ArrayBuffer` is no longer a supertype of typed-array types in `lib.d.ts`,
  which can surface new errors around `Buffer`/`Uint8Array` interop
  *(applies to: >=5.9)*
  [Source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html].
- `--module node20` (added in 5.9) models Node 20 behavior and implies
  `target: es2023`; unlike `nodenext`, it is not expected to keep evolving
  *(applies to: >=5.9)*
  [Source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html].
- Stage-3 ECMAScript decorators (without `experimentalDecorators`) are
  available alongside the older flag-gated legacy decorator implementation
  *(applies to: >=5.0)*
  [Source: https://www.typescriptlang.org/docs/handbook/decorators.html].

**Migration sequencing (engineering guidance, not just trivia): upgrade to
6.0 first, then 7.0.** TypeScript 7.0 deliberately adopts 6.0's new defaults
and behavior for compatibility rather than introducing another wave of
default changes — the intended path is to absorb 6.0's default/deprecation
changes first, then take 7.0's native-compiler swap with minimal further
config churn
[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/].
Jumping straight from a pre-6.0 project to 7.0 means absorbing both waves of
breaking change at once with no intermediate checkpoint.

> Full 6.0-defaults table and the 5.9/6.0/7.0 breaking-change list live in
> [`references/version-transition.md`](references/version-transition.md) —
> loaded only when needed (context-efficiency rule CE-3).

## Decision framework

1. **Simplest first (anti-overengineering):** for a new project, just take
   the current stable release's defaults (`strict: true`, `esnext`/`nodenext`
   modules) rather than hand-rolling a permissive config "to be safe" — the
   6.0 defaults exist precisely to make the safe path the default path.
2. **Adopting 6.0's new defaults on an *existing* codebase vs. opting back to
   old behavior:**
   - If the codebase is small/actively maintained: let the new defaults land
     (`strict: true`, `esnext` module, empty `types`), fix the resulting
     errors, and add explicit `"types": ["node"]` (or whatever ambient types
     are actually needed) rather than reaching for `ignoreDeprecations`.
   - If the codebase is large/low-investment and a full strict-mode pass
     isn't justified right now: use `"ignoreDeprecations": "6.0"` and pin the
     pre-6.0-equivalent flags explicitly (rather than relying on silently
     -carried-forward implicit defaults) as a deliberate, temporary bridge —
     not a permanent stance, since those options are fully removed in 7.0
     [Source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html].
   - Don't silently keep old defaults by *not* upgrading — that just delays
     the same migration to a later, larger jump.
3. **Whether to adopt 7.0 now:**
   - Adopt it if the project only ever shells out to `tsc` (CI type-checking,
     build step) and does not embed the compiler programmatically — 7.0's
     ~8-12x build speedup is real value with no API-surface cost.
   - Hold off if the project (or a load-bearing dependency's tooling — Vue,
     Angular, or Svelte language tooling are the documented examples) embeds
     the Compiler API, since 7.0 ships with none at all; wait for 7.1, or
     stay on 6.0 in the meantime
     [Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/].
   - Either way, do the 6.0 migration first (see rule above) — 7.0 assumes
     6.0's defaults are already in place.

## Workflow

1. Determine the current TypeScript major/minor version (`package.json` /
   `tsc --version`) before making any version-sensitive recommendation.
2. If migrating JS -> TS: start with a permissive `tsconfig.json`
   (`allowJs: true`, explicit `outDir`), rename files incrementally, convert
   `require`/`module.exports` to `import`/`export`, install missing
   `@types/*`, then progressively enable stricter checks rather than
   `strict` all at once
   [Source: https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html].
3. If upgrading TypeScript versions: apply the 6.0 default/deprecation
   changes first, run the full test/build suite, then consider 7.0 (see
   Decision framework).
4. For any type-system or config change, run (or propose) `tsc --noEmit` to
   confirm it actually type-checks — don't rely on the change merely looking
   plausible.
5. Verify (below) before declaring done.

## Engineering rules

- Use lowercase primitive types (`number`, `string`, `boolean`) — never the
  boxed wrapper types (`Number`, `String`, `Boolean`)
  [Source: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html].
- Prefer `unknown` over `any` for values you accept but don't directly
  interact with; reserve `any` for genuine JS-to-TS migration scenarios
  [Source: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html].
- Every declared generic type parameter must actually appear in the
  resulting type signature, or it provides false type safety
  [Source: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html].
- Prefer an `as const` object plus a derived union type over `enum` in new
  code; where enums are unavoidable, never publish an ambient `const enum` in
  a `.d.ts` for other packages to consume — it's incompatible with
  `isolatedModules`, and a build/runtime version mismatch can silently inline
  wrong values in a way tests running against matched dependency versions
  won't catch
  [Source: https://www.typescriptlang.org/docs/handbook/enums.html].
- Always tag a version-specific claim with the range it applies to before
  asserting it — see the Knowledge section for why this matters this much
  right now (5.9/6.0/7.0 changed a lot at once).
- When publishing a typed package, point `package.json`'s `"types"` at your
  bundled `.d.ts`, and list required `@types/*` under `dependencies` (not
  `devDependencies`) so consumers receive them automatically
  [Source: https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html].

## Trade-offs

- Structural typing plus intentional unsoundness (bivariance, excess-property
  laxity on non-literals) trades some compile-time guarantee for modeling
  JavaScript's actual idioms naturally — don't treat TypeScript's type system
  as a complete correctness guarantee
  [Source: https://www.typescriptlang.org/docs/handbook/type-compatibility.html].
- Adopting TypeScript 6.0's stricter defaults immediately surfaces real
  latent bugs but costs migration time on an existing codebase; the
  `ignoreDeprecations` bridge buys time at the cost of carrying legacy
  behavior that will be fully removed in 7.0.
- TypeScript 7.0's build-speed win is large, but for any project embedding
  the Compiler API, upgrading now means losing that integration entirely
  until 7.1 ships — there is no partial/compatibility mode documented.

## Anti-patterns

- **Upgrading straight to TypeScript 7.0 while depending on tooling that
  needs the Compiler API** (e.g. Vue/Angular/Svelte language tooling that
  embeds it) — 7.0 ships with zero programmatic API, so this silently breaks
  that tooling with no documented workaround short of staying on 6.x or
  waiting for 7.1
  [Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/].
- **Skipping the 6.0 migration and jumping a pre-6.0 project straight to
  7.0** — 7.0 assumes 6.0's defaults are already the baseline, so this stacks
  both breaking-change waves into one migration instead of two manageable
  ones (the domain's over-engineering-adjacent trap: trying to do the whole
  jump in one step because it's "just a version bump").
- Writing multiple function overloads that differ only in callback arity
  instead of one overload using the callback's maximum arity
  [Source: https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html].
- Letting `include`/`exclude` fall back to defaults instead of explicitly
  scoping `include` (e.g. `["src"]`) and excluding `**/node_modules` — a
  documented frequent, avoidable cause of slow compiles and editor slowness
  [Source: https://github.com/microsoft/TypeScript/wiki/Performance].
- Assuming "current TypeScript defaults" from pre-2026 knowledge (e.g.
  `strict: false`, `module: commonjs` by default) — those defaults flipped in
  6.0; state the version any config guidance targets rather than assuming
  latest behavior implicitly.

## Security

TypeScript's own official documentation has no dedicated security-guidance
page; the closest documented adjacent point is the design non-goal that the
type system is not fully sound by design, so its static checks should not be
relied on as a complete guarantee against type-confusion-adjacent runtime
bugs
[Source: https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals].
Unresolved: whether Microsoft publishes a separate TypeScript-compiler
security-disclosure/CVE process was not confirmed in the source research. For
general secure-coding practice (injection, secrets, trust boundaries), defer
to the cross-cutting security skill — not restated here (no-duplication rule
QR-2).

## Performance

TypeScript 7.0's Go-native compiler reports **8x-12x faster full builds**
versus 6.x on real-world projects (a cited example: VS Code's own codebase,
125.7s on TypeScript 6 vs. 10.6s on 7.0), with memory usage down 6-26%
depending on project — vendor-reported figures from the TypeScript team's own
announcement, not independently corroborated
[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/].
*Applies to: TypeScript >=7.0, measured against 6.x.* For any TypeScript
version, the documented compiler-side levers are: explicit `include`/exclude
scoping, `skipLibCheck: true`, `--incremental`, project references for large
codebases, and preferring `interface` extension over intersection types
(cached by the checker, unlike intersections)
[Source: https://github.com/microsoft/TypeScript/wiki/Performance]. Cross-cutting
performance method beyond compiler-specific tuning is owned by the
performance skill, not restated here.

## Testing

TypeScript's official docs contain no dedicated testing-framework guidance —
TypeScript does not ship or endorse a test runner
[Source: https://www.typescriptlang.org/docs/handbook/]. The one documented
testing-adjacent mechanism is `isolatedModules`, needed because some
transpiler-based tools (Babel, esbuild-based runners) compile files
independently of the full TypeScript program and can't support
whole-program-dependent constructs like ambient `const enum`
[Source: https://www.typescriptlang.org/tsconfig/#isolatedModules]. Test
strategy itself is owned by the testing skill, not restated here.

## Failure handling

- If the TypeScript major/minor version can't be determined, ask for it or
  explicitly state the version the guidance assumes — never assume "latest"
  silently, given how much changed across 5.9/6.0/7.0.
- If shell is unavailable/denied, output advisory tsconfig/type changes and
  state that `tsc` was not actually run to confirm they compile.
- If evaluating a 7.0 upgrade and Compiler API embedding status is unknown,
  ask rather than assuming it's safe to upgrade.

## Escalation

- A tsconfig change that would newly fail the build across a large existing
  codebase (enabling `strict`, or absorbing the 6.0 default flip) requires
  the user's explicit go-ahead before applying, given how disruptive it can
  be.

## Outputs & verification

- **Outputs:** a tsconfig/type/declaration-file change, a version-upgrade
  migration plan, or analysis of type-system/config choices.
- **Verify:** every version-specific claim is tagged with its applicable
  range; `tsc --noEmit` (or equivalent) confirms the change type-checks; a
  7.0-upgrade recommendation explicitly checked Compiler API dependence.

## References

- [`references/version-transition.md`](references/version-transition.md) —
  Tier-2 deep dive: the full 5.9/6.0/7.0 breaking-change and default-change
  detail.
- Source list: see `skill.yaml.source_references` (TypeScript official docs
  and devblogs, retrieved 2026-09-10, via `research/technologies/typescript.md`).
