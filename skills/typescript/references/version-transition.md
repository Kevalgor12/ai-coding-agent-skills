# TypeScript 5.9 -> 6.0 -> 7.0 version transition (Tier-2 deep dive)

Loaded on demand from `SKILL.md` — do not auto-load. All claims sourced from
`research/technologies/typescript.md`; primary citations are the TypeScript
team's own devblogs announcements and official release notes / tsconfig
reference / compiler wiki. Retrieved 2026-09-10.

## TypeScript 5.9 (last release before 6.0)

[Source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html]

- `tsc --init` now generates a leaner template with prescriptive defaults:
  `"module": "nodenext"`, `"target": "esnext"`, `"strict": true`,
  `"jsx": "react-jsx"`.
- New `--module node20` option: models Node 20 behavior, implies
  `target: es2023`; unlike `nodenext`, it is not expected to gain new
  behavior in future releases (a fixed snapshot rather than an evolving
  target).
- Support for ECMAScript `import defer` syntax (namespace-only), requiring
  `--module preserve` or `--module esnext`.
- **Breaking change:** `ArrayBuffer` is no longer a supertype of typed-array
  types (e.g. `Uint8Array`) in `lib.d.ts` — can surface new type errors
  around `Buffer`/typed-array interop. Documented fixes: update
  `@types/node`, use precise buffer types, or access `.buffer` explicitly.
- Also documented: generic type-argument inference "leak" fixes that may
  surface new errors requiring explicit type arguments at some call sites.

## TypeScript 6.0 (2026-03-23) — the "bridge" release

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/]
[Source: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html]

**Default changes:**

| Option | Old default | New default (6.0) |
|---|---|---|
| `strict` | `false` | `true` |
| `module` | `commonjs` | `esnext` |
| `target` | fixed per-release | floating current-year (`es2025`) |
| `types` | all visible `@types/*` | `[]` (empty — nothing auto-included) |
| `noUncheckedSideEffectImports` | `false` | `true` |
| `libReplacement` | `true` | `false` |

The `types: []` change is the one most likely to silently break a build:
most Node.js projects now need an explicit `"types": ["node"]`, since
`@types/node` is no longer picked up automatically.

**Removed:** `target: es5`, `--downlevelIteration`, `--moduleResolution
classic`, `--outFile` (use an external bundler instead), `--module
amd`/`umd`/`systemjs`, `--alwaysStrict false`.

**Deprecated (still functions, with a warning):** `--moduleResolution node`
(aka `node10`, in favor of `nodenext`/`bundler`), `baseUrl` (in favor of
explicit `paths`). `esModuleInterop: false` and
`allowSyntheticDefaultImports: false` no longer take effect (always-on
behavior now assumed).

**Other breaking changes:** legacy `module Foo { }` namespace syntax is now
an error (must use the `namespace` keyword); running bare `tsc foo.ts` in a
directory that also has a `tsconfig.json` now errors (requires
`--ignoreConfig` to get the old implicit behavior).

**Migration aids documented by the 6.0 announcement:**
- `"ignoreDeprecations": "6.0"` — temporarily suppresses the new deprecation
  warnings while migrating.
- `--stableTypeOrdering` — aligns type-ordering behavior with 7.0's
  deterministic ordering ahead of time; documented as potentially causing
  "~25% type-checking slowdown" when enabled, so treat it as a transitional
  tool, not a permanent setting.
- `ts5to6` — a tool for automated config migration.
- The announcement recommends settling on either `--module preserve` with
  `--moduleResolution bundler`, or `--module nodenext`, as the durable
  long-term module configuration going forward.

Deprecated options in 6.0 are **fully removed in TypeScript 7.0** — the
`ignoreDeprecations` escape hatch is a bridge, not a permanent stance.

## TypeScript 7.0 (2026-07-08) — the Go-native compiler rewrite

[Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/]

- The compiler implementation itself was rewritten natively in Go (replacing
  the JS implementation used through 6.x), codenamed `tsgo` /
  `@typescript/native-preview`, while preserving 6.0's behavior for
  compatibility.
- Adds multithreaded/parallel compilation (`--checkers`, `--builders` flags)
  and a rebuilt `--watch` mode using a ported Parcel file watcher; continues
  to expose Language Server Protocol-based editor integration.
- **`target: es5` remains unsupported** (carried over from 6.0's removal).
- **`baseUrl` removed** entirely (use `paths` relative to the project root).
- **`rootDir` now defaults to `./`** (the tsconfig directory) rather than
  being inferred — the announcement notes this requires explicit
  configuration in some existing projects.
- **`types` continues to default to `[]`.**
- **No programmatic Compiler API at all.** This is the single most
  consequential fact for tooling authors: 7.0 does not ship
  `ts.createProgram()`, `ts.createSourceFile()`, `ts.transpileModule()`, the
  `TypeChecker`, or the `LanguageService` API surface documented for 6.x and
  earlier. The announcement explicitly names Vue, Angular, and Svelte
  tooling as examples of projects delayed by this gap. A full, different API
  is planned for **TypeScript 7.1**, not 7.0 itself.
  [Source: https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API]
  confirms from the wiki side: its documented API surface "currently
  describe[s] TypeScript 6.0 and earlier. TypeScript 7.1 will have a
  completely different API."

**Migration sequencing guidance (stated directly by the TypeScript team):**
7.0 deliberately adopts 6.0's new defaults/behavior for compatibility rather
than introducing another wave of default changes. The intended upgrade path
is 6.0 first (absorb the default/deprecation changes), then 7.0 (absorb the
native-compiler swap with minimal further config churn). Do not treat 7.0 as
a drop-in replacement for a pre-6.0 project.

## Practical adoption checklist

1. Confirm current TypeScript version before recommending anything
   version-specific.
2. If pre-6.0: plan the 6.0 default migration as its own step — expect
   `strict` violations, missing `"types": ["node"]`, and removed/deprecated
   module-resolution options to surface.
3. Use `"ignoreDeprecations": "6.0"` only as a deliberate, temporary bridge
   on a large codebase — not a permanent config.
4. Before recommending 7.0, explicitly check whether the project or any
   load-bearing dependency's tooling embeds the Compiler API. If yes, hold
   off until 7.1 or confirm the dependency has already adapted.
5. After adopting 7.0, expect the ~8-12x build speedup reported by the
   TypeScript team (vendor-reported, not independently corroborated here)
   [Source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/].
