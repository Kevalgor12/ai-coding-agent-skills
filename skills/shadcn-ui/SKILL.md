---
name: shadcn/ui
description: >-
  shadcn/ui-specific CLI usage (init/add/build/migrate), the copy-in-source
  component distribution model (not an installed npm package), Base UI vs.
  Radix UI primitive selection, components.json configuration, registry
  protocol, and theming. Use when components.json is present, the shadcn CLI
  is invoked, or @/components/ui imports appear. Not for MUI (SK-TECH-mui),
  the general styling-system choice (SK-FE-003), or UI/UX design method
  (SK-FE-002).
spec_version: "1.0"
---

## Purpose & scope

shadcn/ui describes itself as **"not a component library. It is how you
build your component library."** [Source: https://ui.shadcn.com/docs] It is
a **code distribution platform**: running its CLI copies component *source
code* — readable, modifiable `.tsx` files — directly into the consuming
project (typically under `components/ui/`), rather than installing a
compiled, opaque package from npm. There is no runtime `shadcn` package the
app imports as a UI library in the traditional sense. This skill covers
shadcn/ui-specific CLI, registry, configuration, and theming mechanics. The
general styling-system choice (Tailwind vs. Sass vs. plain CSS) and UI/UX
design method come from the parent Layer-3 skills `SK-FE-003`
(styling-systems) and `SK-FE-002` (ui-ux-design) — neither is yet authored in
this library.

## When to use / When not to use

**Use** when `components.json` is present, the `shadcn` (or legacy
`shadcn-ui`) CLI is invoked, `@/components/ui` imports appear, or the task
names shadcn/ui, a specific component, registry, or theme token. **Do not
use** when the stack uses MUI or another installed component-library package
(`SK-TECH-mui`), when the general styling-system choice hasn't been made yet
(`SK-FE-003`), for pure UI/UX design method with no technology chosen
(`SK-FE-002`), or when the project has no Tailwind CSS + React (or another
shadcn-supported framework) foundation at all.

## Knowledge

- **Copy-in-source model:** `add`/`init` copy component source into the
  project; the developer owns and can freely edit it. Five stated
  principles: Open Code, Composition, Distribution (registry + CLI), Beautiful
  Defaults, AI-Ready. [Source: https://ui.shadcn.com/docs]
- **Architecture:** a CLI tool (`shadcn`), a registry protocol
  (`registry.json` — framework-agnostic, not React-only), and Tailwind CSS as
  the styling engine with CSS variables for theming. Each project keeps a
  `components.json` describing style, RSC support, TS/JS, Tailwind paths, and
  import aliases — a map for the CLI, not a runtime config the components
  read. [Source: https://ui.shadcn.com/docs/registry] [Source:
  https://ui.shadcn.com/docs/components-json]
- **CLI (v4 line, current 4.21.0):** `init` (`--template`, `--base radix|<Base UI>`,
  `--preset`, `--css-variables`, `--monorepo`), `add` (`--all`, `--overwrite`,
  `--dry-run`, `--diff`), `build`, `view`, `search`, `docs`, `info`,
  `preset {decode,resolve,url,open}`, `migrate {cn,icons,base-color,rtl,radix}`,
  `eject` (irreversible), `mcp`/`mcp init`. Invoked as `pnpm dlx shadcn@latest
  <command>` (or `npx shadcn@latest <command>`). [Source:
  https://ui.shadcn.com/docs/cli] The legacy `shadcn-ui` npm package name is
  deprecated/unmaintained — use `shadcn`. [Source:
  https://www.npmjs.com/package/shadcn]
- **Base UI is the new default primitive (>= July 2026):** newly scaffolded
  projects default to **Base UI** (v1.6.0, 6M+ weekly downloads) instead of
  **Radix UI**, the prior default through early 2026. Radix remains fully
  supported, not deprecated — opt back in with `shadcn init -b radix`.
  [VERSION-SENSITIVE: applies to the default as of 2026-07; Radix is
  available at any time via the flag.] [Source:
  https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default]
- **`"new-york"` style is current; `"default"` is deprecated.** `style`,
  `tailwind.baseColor`, and `tailwind.cssVariables` in `components.json` are
  **immutable after `init`** without reinstalling components — an
  easy-to-miss, one-way decision made at project init. [Source:
  https://ui.shadcn.com/docs/components-json]
- **`data-slot` attributes replace `forwardRef`:** since the Tailwind v4
  adoption (dated Feb 2025), components use plain function components with
  `data-slot` attributes on primitive elements instead of
  `React.forwardRef`-wrapped components, letting Tailwind/CSS target internal
  parts without ref-forwarding boilerplate. [Source:
  https://ui.shadcn.com/docs/tailwind-v4]
- **Theming:** semantic CSS-variable tokens (`background`/`foreground`,
  `primary`/`primary-foreground`, `destructive`, `border`, `ring`,
  `chart-1`…`chart-5`) defined in global CSS, overridden under `.dark`; a
  single `--radius` token derives the full corner-radius scale. [Source:
  https://ui.shadcn.com/docs/theming]
- **`cn` utility (Sept 2026):** a first-party package released with **no
  breaking changes** — existing hand-rolled `lib/utils.ts` (clsx +
  tailwind-merge) keeps working; `migrate cn` is opt-in. [Source:
  https://ui.shadcn.com/docs/changelog/2026-09-cn]
- **React 19 peer-dependency friction:** npm may surface peer-dependency
  errors for packages not yet declaring React 19 support; Recharts
  specifically needs a `package.json` `overrides` entry pinning `react-is` to
  a `19.0.0-rc` build, then `npm install --legacy-peer-deps`. Tailwind v3 +
  React 18 projects keep working unchanged — only new projects default to
  Tailwind v4 + React 19. [Source: https://ui.shadcn.com/docs/react-19]

## Decision framework

**1. shadcn/ui vs. MUI (component-library layer)** — this is a structural
choice, not a quality ranking; neither official source states a direct
security/performance ranking between them. [Source:
research/knowledge-maps/technology-decision-matrix.md §8]

| | MUI | shadcn/ui |
|---|---|---|
| Distribution | Installed npm package (`@mui/material`), versioned dependency | **Not a component library — a code distribution platform**: source is copied into the project via a CLI |
| Styling engine | Emotion CSS-in-JS (`sx` prop) | No CSS-in-JS runtime (Tailwind, build-time utility classes) |
| CSP | Needs `style-src-elem 'nonce-<base64>'` for Emotion-injected `<style>` tags | Not applicable in the same way — no CSS-in-JS runtime to nonce |
| Patch policy | Only current-major + one LTS line receive security patches | No published SLA / patchable-version list |
| Vuln-patch mechanism | Standard `npm update` | **No automatic upgrade path** — a vulnerability in already-copied component code must be manually re-pulled/patched per project |
| Testing guidance | Test the app, not MUI internals; snapshot testing discouraged | No dedicated general testing guide; AI-SDK-specific deterministic chat-UI testing only |

Choose MUI when you want a versioned dependency with a normal `npm audit` /
upgrade signal and are fine with an Emotion CSP nonce. Choose shadcn/ui when
you want full control over component source (no wrapper/override layer) and
accept that upstream patches don't propagate automatically. **Simplest
option:** if the project doesn't need per-component customization beyond
theming, a smaller, purpose-built widget set (or no component library at all
for a handful of primitives) can be less overhead than either.

**2. Base UI vs. Radix UI (headless-primitive choice, new projects)** — Base
UI is the default for projects initialized `>= July 2026`; Radix remains
fully supported via `shadcn init -b radix` and is the correct choice for
projects that must match an existing Radix-based codebase, or where a
specific Radix-only behavior/plugin is required. Don't switch an existing
production project's primitive without going through the documented
AI-driven, component-by-component migration tool (see Workflow) — a blind
codemod risks silently changing prop names/behavior. [Source:
https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default]

## Workflow

1. Determine whether `components.json` already exists; if so, read its
   `style`, `tailwind.baseColor`/`cssVariables`, and primitive choice before
   proposing any `add` — these fields are immutable post-init.
2. For a new project: `shadcn init` (choose `--base radix` explicitly if
   matching an existing Radix codebase or org convention; otherwise Base UI
   applies by default on `>=July 2026` CLI versions).
3. For adding a component: `shadcn add <component>`, previewing with
   `--dry-run`/`--diff` first when the component may already be customized.
4. For theming: edit CSS-variable tokens in global CSS rather than
   hand-editing component class names.
5. For a primitive migration (Radix → Base UI) on an existing app: use the
   documented AI-driven migration tool (component-by-component, preserves
   custom variants, one commit per component) rather than a blanket
   `add --overwrite`. [Source: https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default]

## Engineering rules

- Install the `shadcn` npm package, never `shadcn-ui` (deprecated/unmaintained).
- Treat `style`, `tailwind.baseColor`, and `tailwind.cssVariables` as
  one-way, init-time decisions — confirm them deliberately, don't let a
  default slip through unnoticed.
- Re-skin via CSS-variable tokens; don't hunt through component source for
  hardcoded colors when a token override would do.
- Use `buttonVariants` + a real `<a>` for link semantics rather than
  rendering `<Button>` "as" a link. [Source:
  https://ui.shadcn.com/docs/components/button]
- When declaring registry dependencies, use bare names only for
  already-configured shadcn components; use a full registry-item address for
  any third-party dependency, to avoid ambiguous resolution. [Source:
  https://ui.shadcn.com/docs/registry/faq]

## Trade-offs

The central trade-off is **code ownership vs. automatic upgrades**: shadcn/ui
gives full control over component source with no wrapper/override layer to
maintain, but there is no `npm update`-style path — every previously copied
component is frozen at the state it was copied in, and staying current
requires deliberately re-running `add --diff`/`--overwrite` or a `migrate`
command per component. [Source: https://ui.shadcn.com/docs/registry/faq;
research/knowledge-maps/technology-decision-matrix.md §8]

## Anti-patterns

- Running `npm install shadcn-ui` instead of `npm install shadcn` — the old
  package name is a deprecated, unmaintained shell. [Source:
  https://www.npmjs.com/package/shadcn]
- Assuming components "auto-update" the way an npm dependency would; the CLI
  never modifies already-installed component files without an explicit
  `add --overwrite` or `migrate` run. **(Over-engineering trap for this
  domain, inverted):** conversely, don't build a custom auto-sync/patch
  pipeline to simulate npm-style updates before confirming the project
  actually needs frequent upstream syncs — most projects are fine
  re-pulling components manually and rarely.
- Referencing a third-party registry dependency by a bare name instead of
  its full address — risks the CLI resolving it to the wrong (e.g. built-in)
  component of the same name. [Source: https://ui.shadcn.com/docs/registry/faq]
- Pinning a third-party registry item's `#ref` to a mutable branch instead of
  a tag or full commit SHA. [Source: https://ui.shadcn.com/docs/registry/faq]
- Re-running `add --overwrite` over a hand-edited component without checking
  first — silently discards local customizations.

## Security

The single most important security fact for this skill: **because component
code is copied into the project rather than installed as a versioned
dependency, there is no automatic upgrade path for a vulnerability in
already-copied component code** — it must be manually re-pulled/patched per
project, unlike a normal npm dependency's `npm audit`/update signal.
[Inference from shadcn-ui.md, not an explicit doc statement; corroborated by
research/knowledge-maps/technology-decision-matrix.md §8]

- **Private/internal registries:** documented auth options are Bearer-token,
  custom-header/API-key, or query-parameter, with secrets stored in
  environment variables (e.g. `REGISTRY_TOKEN`), HTTPS enforced, and rate
  limiting/token rotation/access logging as production considerations.
  [Source: https://ui.shadcn.com/docs/registry/authentication]
- **Supply-chain pinning:** pin third-party registry items via `#ref` to a
  **tag or full commit SHA**, not a mutable branch, since `add`/`init`
  execute code — including arbitrary declared npm `dependencies` — that gets
  copied directly into the project. [Source:
  https://ui.shadcn.com/docs/registry/faq]
- **Vulnerability reporting:** the `shadcn-ui/ui` GitHub repo directs reports
  to GitHub's private vulnerability reporting feature; no published SLA or
  list of currently-patched versions. [Source: https://github.com/shadcn-ui/ui
  (SECURITY.md)]
- For the general injection/secrets/transport threat model, defer to
  `SK-QA-002` — not restated here (no-duplication rule QR-2).

## Performance

The "no library-wide runtime or unused-component bundle cost" framing is
shadcn/ui's own architectural/philosophy claim (only installed components
exist in the project's source tree), **not an independently benchmarked
figure** — the official docs do not publish comparative bundle-size or
runtime benchmarks against other libraries. [Source: https://ui.shadcn.com/docs]
Since the Tailwind v4 adoption there is no CSS-in-JS runtime; styling is
build-time Tailwind utility classes, and `data-slot` attributes replace
`React.forwardRef` wrapper overhead. [Source:
https://ui.shadcn.com/docs/tailwind-v4] Cross-cutting performance method is
owned by `SK-QA-003`.

## Testing

There is **no dedicated general "Testing" guide** published for shadcn/ui
components (no official unit-testing or visual-regression guidance). The one
documented testing-relevant feature is AI-SDK-specific: `@shadcn/helpers`'s
`ai-sdk` integration lets a scripted conversation stream through `useChat`
with no model, API route, or network calls — useful for deterministic
chat-UI testing in CI, not general component testing. [Source:
https://ui.shadcn.com/docs/helpers/ai-sdk] Unresolved: whether shadcn/ui
publishes a first-party, general component-testing guide beyond this
AI-SDK-specific helper could not be confirmed. General test strategy is
owned by `SK-QA-001`.

## Failure handling

- If it's unknown whether the project already has `components.json` (and
  what style/primitive it declares), inspect the repo or ask before running
  `init` — re-initializing can silently target the wrong primitive/style,
  and both are immutable post-init.
- If shell is unavailable or denied, degrade to advisory output (which CLI
  commands would run, what files would change) and state that the CLI was
  not actually invoked.
- If asked to install a package literally named `shadcn-ui`, stop and flag
  it as the deprecated/unmaintained legacy package name; use `shadcn`
  instead.

## Escalation

- Re-running `add --overwrite` over hand-edited components requires explicit
  user confirmation — it can silently discard local customizations.
- A Radix-to-Base-UI primitive migration on an existing production project
  is presented for confirmation before running the documented AI-driven,
  component-by-component migration tool, since it changes imports/behavior
  per component.

## Outputs & verification

- **Outputs:** component source files under `components/ui/` (or a
  workspace-aliased path) plus `components.json`; the CLI commands actually
  run; an analysis of primitive/style/theme choices and upgrade strategy.
- **Verify:** confirm which style and primitive the project's
  `components.json` already declares before adding components (both are
  init-immutable); check any proposed CLI command against the documented v4
  command surface rather than an invented flag; confirm every
  version-specific claim carries the range it holds for.

## References

- Source list: see `skill.yaml.source_references` (shadcn/ui official docs
  and changelog, npm, GitHub SECURITY.md — retrieved 2026-09-10, via
  `research/technologies/shadcn-ui.md`; MUI-comparison claims via
  `research/knowledge-maps/technology-decision-matrix.md` §8; version facts
  via `research/knowledge-maps/version-matrix.md`).
