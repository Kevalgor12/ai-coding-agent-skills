# shadcn/ui

Deep reference research on **shadcn/ui**, a code-distribution platform for UI
components used with React and Tailwind CSS. Primary source is the official
documentation site **ui.shadcn.com/docs**, supplemented by the official
`shadcn-ui/ui` GitHub repository/security policy and the npm registry (the
official distribution channel for the `shadcn` CLI package). Research date:
**2026-09-09**.

## 0. Canonical docs host and a note on pace of change

[Source: https://ui.shadcn.com/docs] The canonical, current documentation
host is **https://ui.shadcn.com/docs**. [Source: https://ui.shadcn.com/docs/changelog]
The project ships an unusually fast, continuous stream of dated changelog
entries (roughly monthly, sometimes multiple entries per month) rather than
discrete numbered doc "editions." Between June 2023 and September 2026 the
official changelog lists 55 entries spanning CLI rewrites, a primitive-library
default switch (Radix → Base UI), a new preset/design-system-sharing system,
and a new `cn` utility package. [Inference, not confirmed in docs] Given this
pace, any third-party tutorial, blog post, or AI training data older than a
few months should be treated as likely stale for this technology specifically
— this document relies on the dated official changelog rather than general
prose descriptions wherever precision mattered.

[Source: https://www.npmjs.com/package/shadcn (queried via `npm view shadcn
version`, 2026-09-09)] The current published version of the `shadcn` CLI
package on npm is **4.21.0**, last modified 2026-09-04. [Source:
https://www.npmjs.com/package/shadcn] The legacy package name `shadcn-ui` is
deprecated/unmaintained (last published roughly two years prior per npm); the
current, actively maintained package is named **`shadcn`** (no `-ui` suffix).
Anyone following older instructions that reference `shadcn-ui` as the install
package is following stale guidance — this is a version-sensitive naming
change worth flagging explicitly.

---

## 1. Core concepts

[Source: https://ui.shadcn.com/docs] shadcn/ui describes itself as **"not a
component library. It is how you build your component library."** — i.e. a
**code distribution platform**, not an installable npm package of pre-built,
opaque components. Running the CLI copies component *source code* directly
into the consuming project, where the developer owns and can freely modify it.

[Source: https://ui.shadcn.com/docs] The docs frame the problem this solves:
teams otherwise "end up wrapping library components, writing workarounds to
override styles, or mixing components from different libraries with
incompatible APIs" when using traditional installed-as-a-dependency component
libraries.

[Source: https://ui.shadcn.com/docs] Five stated foundational principles:
1. **Open Code** — components ship as readable, modifiable source, not a
   black-box package.
2. **Composition** — every component shares a common, predictable interface.
3. **Distribution** — a flat-file schema plus a CLI make components
   installable/sharable across projects (the "registry" system).
4. **Beautiful Defaults** — components come polished/pre-styled out of the box.
5. **AI-Ready** — because the code is open and follows consistent patterns,
   AI models/agents can read, understand, and extend it directly.

[Source: https://ui.shadcn.com/docs/components] shadcn/ui ships roughly 75
base components (buttons, dialogs, tables, forms, etc.) as of the research
date, plus form-library integrations (React Hook Form, TanStack Form,
Formisch), utility components (scroll-fade, shimmer), and separate helper
packages (`@shadcn/react`, `@shadcn/helpers`).

[Source: https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default] As of
**July 2026**, newly scaffolded projects default to **Base UI** as the
underlying headless-primitive library instead of **Radix UI**, which was the
long-standing default from the project's earlier history through early 2026.
Radix remains fully supported and is not deprecated; developers can opt back
into it with `shadcn init -b radix`. [VERSION-SENSITIVE: any doc, code sample,
or component source referencing Radix primitives (`@radix-ui/react-*`
imports, `asChild`/Radix-specific props) reflects the pre-July-2026 default,
or a project explicitly initialized with `-b radix`; new default installs
after July 2026 use Base UI primitives instead, which have different prop
names/behavior in places.]

---

## 2. Architecture

[Source: https://ui.shadcn.com/docs] Architecturally, shadcn/ui is a
combination of (a) a **CLI tool** (`shadcn`), (b) a **registry protocol**
(JSON schema describing installable "items" — components, blocks, hooks,
libs, themes, fonts), and (c) **Tailwind CSS** as the styling engine,
with **CSS variables** as the theming layer. There is no runtime shadcn
package that your app imports as a UI library in the traditional sense (aside
from small first-party helper packages like `cn`, `@shadcn/react`, and
`@shadcn/helpers`, discussed below) — the actual `Button`, `Dialog`, etc.
components live as plain `.tsx` files inside the consumer's own repository
under something like `components/ui/`.

[Source: https://ui.shadcn.com/docs/components-json] Each project that uses
the CLI keeps a `components.json` file describing style choice, whether
React Server Components (RSC) support is enabled, TypeScript vs JavaScript,
Tailwind config paths, and import-alias mappings — this file is the CLI's
map of the local project architecture, not a runtime config consumed by the
components themselves.

[Source: https://ui.shadcn.com/docs/registry] A **registry** is described as
"a distribution system for code" — a `registry.json` manifest (see §3) that
can describe components, hooks, pages, config, or arbitrary files, and which
is explicitly **framework-agnostic** ("any project type and any framework"),
not limited to React. The public shadcn registry at ui.shadcn.com is one
instance of this protocol; anyone can host a private or public registry that
the CLI can pull from.

[Source: https://ui.shadcn.com/docs/monorepo] In monorepo setups (Turborepo
is the officially documented/scaffolded build tool), the architecture splits
into a shared `packages/ui` workspace holding base components (imported via
e.g. `@workspace/ui/components/button`) and app-level workspaces (`apps/web`)
that pull block-level, app-specific compositions locally. Both workspaces
need their own `components.json`.

[Source: https://ui.shadcn.com/docs/registry/registry-json] Registry items
are typed: `registry:component`, `registry:ui`, `registry:hook`,
`registry:lib`, `registry:block`, and (per the CLI v4 changelog) a newer
`registry:base` type for distributing an entire design-system payload
(colors, fonts, radius) as one unit. [Source:
https://ui.shadcn.com/docs/changelog/2026-03-cli-v4] `registry:base` and
first-class font registry items were introduced in the March 2026 "CLI v4"
release.

[Source: https://ui.shadcn.com/docs/tailwind-v4] Since the Tailwind v4
migration (dated February 2025 in the changelog, described further in the
`tailwind-v4` guide), components rely on `data-slot` attributes on every
primitive element (replacing `React.forwardRef`-wrapped components) so that
Tailwind/CSS can target internal parts for styling without ref-forwarding
boilerplate. [VERSION-SENSITIVE: `forwardRef`-based component source is the
pre-Tailwind-v4 (pre-2025) shape; current components use plain function
components with `data-slot` attributes.]

---

## 3. APIs

shadcn/ui exposes two distinct "API" surfaces: the **CLI command API** and
the **per-component prop API** (which is just the props of whatever
underlying primitive — Base UI or Radix — plus shadcn's own variant props).

### 3.1 CLI commands
[Source: https://ui.shadcn.com/docs/cli] Documented commands as of the
research date:
- `init` — initialize/configure a project; flags include `--template`,
  `--base` (choose `radix` or Base UI primitives), `--preset`,
  `--css-variables`, `--rtl`, `--monorepo`, `--name`.
- `add [component]` — install a component and its dependencies; flags
  `--all`, `--overwrite`, `--path`, `--dry-run`, `--diff`.
- `apply [preset-code]` — apply a shareable design-system preset code
  (optionally scoped with `--only theme` or `--only font`).
- `view [item]` — preview a registry item before installing, including from
  namespaced/third-party registries.
- `search [registry]` — query available items in a registry (`--query`,
  `--limit`, `--offset`).
- `docs [component]` — fetch component documentation from the CLI
  (`--base`, `--json`).
- `info` — print project/framework info, installed components, doc links.
- `build` — generate `registry.json`-conformant output files for hosting
  your own registry (`--output`).
- `preset` (subcommands `decode`, `resolve`, `url`, `open`) — manage/inspect
  design-system preset codes.
- `migrate cn` — rewrite local `clsx`/`tailwind-merge` usage to the new `cn`
  package (see §13).
- `migrate icons` — swap icon library across the codebase (supports lucide,
  tabler, hugeicons, phosphor, remixicon, radix; e.g.
  `--from lucide --to phosphor --yes`).
- `migrate base-color` — change the base color token set (`--to <color>`,
  options include neutral, zinc, stone, mauve, olive, mist, taupe).
- `migrate rtl` — convert physical CSS properties to logical (RTL) ones and
  update `components.json`.
- `migrate radix` — consolidate individual `@radix-ui/react-*` imports into
  the single `radix-ui` package (see §13).
- `eject` — inline shadcn's own utility packages permanently into the
  project, removing the external dependency; documented as irreversible.
- `mcp` / `mcp init --client <claude|cursor|...>` — run/configure the MCP
  server (see §16).

[Source: https://ui.shadcn.com/docs/cli] Package-manager invocation pattern
shown throughout the docs: `pnpm dlx shadcn@latest <command>` (equivalently
`npx shadcn@latest <command>` for npm users).

### 3.2 Component prop API
[Source: https://ui.shadcn.com/docs/components/button] Example (Button):
installed via `pnpm dlx shadcn@latest add button`; imported as
`import { Button } from "@/components/ui/button"`; exposes `variant`
(`"default" | "outline" | "ghost" | "destructive" | "secondary" | "link"`)
and `size` (`"default" | "xs" | "sm" | "lg" | "icon" | "icon-xs" | "icon-sm"
| "icon-lg"`) props, both defaulting to `"default"`. A `buttonVariants` helper
is exported for applying the same classes to non-`<Button>` elements (e.g.
plain `<a>` tags for semantically correct links) rather than rendering the
button "as" a link.

[Source: https://ui.shadcn.com/docs/components/button] The Button doc notes
Base UI's Button component applies `role="button"`, and explicitly
recommends using `buttonVariants` + a plain `<a>` for link semantics instead
of trying to make `<Button>` itself act as a link — a documented
accessibility/semantics guidance point, though there is no dedicated
"Accessibility" section on the page itself.

Not documented / could not verify: shadcn/ui does not publish one unified,
versioned API reference across all ~75 components (unlike, say, a single
TypeScript `.d.ts` reference) — each component's prop surface must be read
from its individual docs page, and (per §2) is really the prop surface of
the underlying Base UI or Radix primitive plus shadcn's variant additions.

---

## 4. Configuration

[Source: https://ui.shadcn.com/docs/components-json] The `components.json`
file (optional, but required for CLI usage) is the primary configuration
surface:
- `$schema`: `https://ui.shadcn.com/schema.json`.
- `style`: component visual style; currently `"new-york"` is current, and
  `"default"` is **deprecated** [VERSION-SENSITIVE]. Cannot be changed after
  init without reinstalling components.
- `rsc`: boolean — enables React Server Components support; when true the CLI
  auto-adds `"use client"` directives where needed.
- `tsx`: boolean — TypeScript (`true`) vs JavaScript (`false`) output.
- `tailwind.config`: path to `tailwind.config.js/.ts` — left blank for
  Tailwind v4 projects (which use CSS-based `@theme` config instead).
- `tailwind.css`: path to the CSS file that imports Tailwind.
- `tailwind.baseColor`: one of `neutral | stone | zinc | mauve | olive |
  mist | taupe`; generates the default token palette; immutable after init.
- `tailwind.cssVariables`: boolean — `true` generates semantic CSS-variable
  tokens (`background`, `foreground`, `primary`, etc.); `false` uses raw
  Tailwind utility classes directly in component markup instead. Immutable
  after init.
- `tailwind.prefix`: optional custom Tailwind utility-class prefix.
- `aliases`: import-path mapping (`utils`, `components`, `ui`, `lib`,
  `hooks`) backed by `tsconfig.json#paths` or `package.json#imports`.
- `registries`: configuration for additional (public/private/namespaced)
  component registries beyond the default shadcn registry, supporting
  URL templates with a `{name}` placeholder, custom auth headers, and
  `${ENV_VAR}` expansion for secrets.

[Source: https://ui.shadcn.com/docs/theming] Theming configuration is
CSS-variable-based: tokens like `background`/`foreground`,
`primary`/`primary-foreground`, `secondary`/`secondary-foreground`,
`muted`/`muted-foreground`, `destructive`, `border`, `input`, `ring`, and
`chart-1` through `chart-5` are defined in the project's global CSS, with a
`.dark` selector overriding the same token set for dark mode. A single
`--radius` base token derives a full corner-radius scale
(`radius-sm`…`radius-4xl`) via calculated multipliers.

[Source: https://ui.shadcn.com/docs/registry/registry-json] For anyone
hosting their own registry, `registry.json` is the configuration schema:
requires `$schema`, `name`, `homepage`, and at least one of `items` or
`include`; each item declares `name`, `type`, `title`, `description`,
`registryDependencies`, `dependencies` (npm packages), and `files` (with
per-file `path`/`type`).

---

## 5. Recommended patterns

[Source: https://ui.shadcn.com/docs] Because components are copied into the
project rather than imported from a package, the docs' implicit recommended
pattern is: **install only what you use, then edit directly** — there is no
wrapper/override layer to maintain, so customization means editing the
component file itself.

[Source: https://ui.shadcn.com/docs/theming] Recommended theming pattern:
"override tokens in your CSS to change the look of your app without
rewriting component classes" — i.e. re-skin via the semantic CSS-variable
tokens rather than hunting through component source for hardcoded colors.

[Source: https://ui.shadcn.com/docs/forms/react-hook-form] For forms, the
officially documented pattern combines **React Hook Form** (`useForm`,
`<Controller>`) with **Zod** schema validation via `zodResolver`, composed
with shadcn's own `<Field>` component system (label/description/error
sub-components) for markup and accessibility structure — errors are surfaced
by adding `aria-invalid` to the input and `data-invalid` to the `<Field>`
wrapper. Documented field patterns include text/textarea, select, checkbox
arrays, radio groups, toggle switches, and dynamic arrays via
`useFieldArray`.

[Source: https://ui.shadcn.com/docs/monorepo] Recommended monorepo pattern:
base/shared components live in a shared `packages/ui` workspace and are
imported by app workspaces via a workspace alias (`@workspace/ui/...`);
app-specific block compositions (e.g. `login-01`) install directly into the
consuming app workspace rather than the shared package.

[Source: https://ui.shadcn.com/docs/registry/authentication] For anyone
building a private/internal registry, documented recommended practices
include: storing tokens in environment variables (not committed to version
control), enforcing HTTPS, rate limiting, token rotation, and access
logging; supporting Bearer-token, custom-header (e.g. `X-API-Key`), or
query-parameter auth depending on the registry's needs.

[Source: https://ui.shadcn.com/docs/registry/faq] For registry dependency
declarations, the documented convention is: bare names (e.g. `"button"`)
resolve to the project's already-configured shadcn components, while
external/third-party dependencies must use a full registry item address, to
avoid ambiguous or incorrect resolution.

---

## 6. Anti-patterns

[Source: https://ui.shadcn.com/docs/components/button] Documented anti-pattern:
rendering `<Button>` "as" a link/anchor for semantic link behavior; the docs
instead recommend using the exported `buttonVariants` helper applied to a
real `<a>` element.

[Source: https://ui.shadcn.com/docs/registry/faq] Implicit anti-pattern
(stated as a recommendation, framed negatively here for clarity): referencing
a third-party registry dependency by a bare name instead of its full address
risks the CLI resolving it to the wrong (e.g. built-in) component of the same
name.

[Source: https://ui.shadcn.com/docs/registry/faq] For registry publishers,
pinning to a mutable branch ref instead of a tag or full commit SHA is
discouraged for published/production registries — the docs state a
preference for "tags or full commit SHAs" over branches for stability when
consumers pin dependencies via `#ref`.

Not documented / could not verify: shadcn/ui's official docs do not publish
a dedicated "Anti-patterns" or "Common mistakes" page comparable to what
some other frameworks maintain; the above are inferred from scattered
recommendation language across component and registry docs, not from one
canonical anti-patterns section. [Inference, not confirmed in docs] Broader
community-known anti-patterns (e.g. "don't blindly re-run `add` with
`--overwrite` over hand-edited components," "don't treat the copied code as
if it will receive upstream patches automatically") are consistent with the
CLI's `--overwrite`/`--diff` flag design but are not explicitly called out
as anti-patterns in the fetched docs pages.

---

## 7. Security

[Source: https://ui.shadcn.com/docs/registry/authentication] The most
substantial officially documented security surface is **registry
authentication**: private registries are documented as needing Bearer-token,
API-key/custom-header, or query-parameter based auth, with server-side
validation examples given for Next.js and Express; environment variables
(e.g. `REGISTRY_TOKEN` in `.env.local`) are the documented way to avoid
committing secrets; the CLI is described as handling 401/403 responses and
surfacing registry-specific error messages (e.g. expired token, subscription
required).

[Source: https://ui.shadcn.com/docs/registry/faq] Because `add`/`init`
execute code that gets copied directly into a consuming project (and can
declare arbitrary npm `dependencies`), the docs' guidance to pin third-party
registry items via `#ref` (branch/tag/commit SHA) and to prefer tags/commit
SHAs for published registries functions as supply-chain-risk mitigation,
though it is not framed in the docs using "supply chain" terminology.

[Source: https://github.com/shadcn-ui/ui (SECURITY.md via GitHub)] The
`shadcn-ui/ui` GitHub repository has a security policy directing
vulnerability reports to GitHub's private vulnerability reporting feature
("Report a vulnerability" under the repo's Security tab) rather than public
issues; the policy states legitimate reports will be investigated and fixed
promptly, but does not publish a specific SLA or a list of currently
"supported" versions eligible for security patches.

[Inference, not confirmed in docs] Because shadcn/ui components are copied
into a consumer's own repo rather than installed as a versioned dependency,
there is no automatic "upgrade to patch a vulnerability" path the way there
is for a normal npm dependency — a vulnerability discovered in a previously
copied component's code would need to be manually re-pulled/patched per
project. This structural implication is not explicitly discussed as a
security tradeoff in the fetched official docs.

Not documented / could not verify: shadcn/ui does not appear to publish a
dedicated general "Security" guide (e.g. XSS/CSP guidance for using the
components) distinct from the registry-authentication material above.

---

## 8. Performance

[Source: https://ui.shadcn.com/docs] The "Beautiful Defaults" / open-code
philosophy implies (but the fetched official pages do not explicitly
benchmark) that because only the components a project actually installs
exist in that project's source tree, there is no library-wide runtime or
unused-component bundle cost to opt out of — this is architectural, not a
documented performance claim per se.

[Source: https://ui.shadcn.com/docs/tailwind-v4] The Tailwind v4 migration
notes state there is no CSS-in-JS runtime: styling is Tailwind utility
classes processed at build time, and components use `data-slot` attributes
rather than `React.forwardRef` wrapper overhead.

Unresolved: multiple third-party (non-official) sources make specific
bundle-size comparisons against other component libraries (e.g. Material UI,
Chakra UI) and quote figures like "50-100KB tree-shaken" — per this
research's sourcing rules, these are **not official sources** and are
excluded as citations here. The official docs do not themselves publish
comparative bundle-size or runtime-performance benchmarks in the pages
fetched for this research, so no verified performance-benchmark claim can be
made. Not documented / could not verify.

---

## 9. Testing

[Source: https://ui.shadcn.com/docs/helpers/ai-sdk] The clearest officially
documented testing-relevant tooling found is `@shadcn/helpers`'s AI SDK
integration, which lets developers "write an AI conversation in code and
stream it through `useChat`" with **no model, API route, or network calls**
— explicitly framed as enabling deterministic chat-UI testing in CI "with no
network calls, token spend, or flaky model output."

Not documented / could not verify: the general shadcn/ui documentation set
fetched for this research does not include a dedicated "Testing" guide for
UI components generally (e.g. no official guidance on unit-testing installed
components with Vitest/Jest/Testing Library, no official visual-regression
tooling). A GitHub-registry starter template referenced in search results
appears to include `vitest.config.ts` / `docs/testing.md` scaffolding, but
this was not independently confirmed against an official, currently-live
docs page during this research pass, so it is flagged rather than cited.
Unresolved: whether shadcn/ui publishes a first-party, general
component-testing guide beyond the AI-SDK-specific deterministic-streaming
helper above could not be confirmed from the pages retrieved.

---

## 10. Deployment

Not applicable in the traditional sense: shadcn/ui is not a hosted service
or runtime you deploy — it is source code copied into a consumer
application, so "deployment" is really the deployment of the *host*
framework (Next.js, Vite, Astro, Laravel, React Router, TanStack Start,
etc.), which is out of scope for shadcn/ui's own docs.

[Source: https://ui.shadcn.com/docs/registry] What *is* documented under a
deployment-adjacent heading is **hosting your own component registry**: a
registry is built via `shadcn build` (generating static `registry.json`-
conformant JSON) and can be served from any static host or web
server/framework (the docs give Next.js and Express server examples for
registries that need authentication).

[Source: https://ui.shadcn.com/docs/registry/github] Registries can also be
hosted directly from a GitHub repository ("GitHub Registries," introduced
per the changelog in June 2026) — public `github.com` repos can be
referenced directly as a registry address; private repos require a
namespace with an authenticated URL. [Source:
https://ui.shadcn.com/docs] Per the changelog, "Private GitHub Registries"
support was added in August 2026, extending this to authenticated private
repo hosting.

---

## 11. Migration

[Source: https://ui.shadcn.com/docs/tailwind-v4] **Tailwind v3 → v4
migration** is officially documented: existing Tailwind v3 + React 18
projects continue to work unchanged (non-breaking for existing projects);
only *new* projects default to Tailwind v4 + React 19. Documented steps:
run Tailwind's own `@tailwindcss/upgrade@next` codemod; move `:root`/`.dark`
variable declarations out of `@layer base`; wrap color values in `hsl()` and
expose them via `@theme inline`; drop `hsl()` wrappers specifically for
chart-color config; adopt the combined `size-*` utility in place of paired
`w-*`/`h-*` classes; upgrade Radix UI, `cmdk`, `lucide-react`, `recharts`,
and related deps; remove `React.forwardRef` usage in favor of `data-slot`-
attributed function components. The Toast component was deprecated in favor
of **Sonner** as part of this same wave, and the `"default"` style was
deprecated in favor of `"new-york"` for new projects. `tailwindcss-animate`
was deprecated in favor of `tw-animate-css` (dated March 2025 within that
guide).

[Source: https://ui.shadcn.com/docs/react-19] **React 18 → React 19
migration**: Next.js 15 supports React 19; using React 19 with npm may
surface peer-dependency resolution errors for packages that haven't yet
declared React 19 compatibility, remedied with `--force` or
`--legacy-peer-deps` (the `shadcn` CLI itself prompts to pick a flag during
`init`), or by temporarily pinning back to React 18
(`npm i react@18 react-dom@18`). pnpm/bun/yarn are documented as generally
not needing these flags. Recharts specifically needs a `package.json`
`overrides` entry pinning `react-is` to a `19.0.0-rc` build, then
`npm install --legacy-peer-deps`.

[Source: https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default]
**Radix → Base UI migration** (the largest recent architectural shift,
dated July 2026): not forced — Radix continues to be fully supported and is
not being deprecated; existing production apps need not change anything.
For teams that do want to move, the docs describe a dedicated **AI-driven
"skill"-based migration tool** (compatible with Claude Code, Cursor, and
similar AI coding agents) that migrates component-by-component rather than
via a blind automated codemod: it preserves custom variants/modified
classes, flags behavior changes instead of silently patching them, produces
a per-component migration report, and aims for one clean git commit per
migrated component.

[Source: https://ui.shadcn.com/docs/cli] **Radix package consolidation**:
the `migrate radix` CLI command consolidates many individual
`@radix-ui/react-*` package imports into the single unified `radix-ui`
package import.

[Source: https://ui.shadcn.com/docs/changelog/2026-09-cn] **`cn` utility
migration**: existing projects with a hand-rolled `lib/utils.ts`
(`clsx`+`tailwind-merge`) are not broken by the September 2026 `cn` package
release; running `migrate cn` rewrites imports, consolidates
`twMerge(clsx(...))` call sites, removes now-unused `clsx`/`tailwind-merge`
packages, and turns `lib/utils.ts` into a thin re-export
(`export { cn } from "cn"`) for backward compatibility.

[Source: https://ui.shadcn.com/docs/cli] Other documented one-off migration
commands: `migrate icons` (swap icon set across the whole codebase, e.g.
lucide → phosphor) and `migrate base-color` / `migrate rtl` (swap the base
color token set, or convert physical CSS to logical/RTL-safe properties).

Not documented / could not verify: shadcn/ui does not document migration
*from* other component libraries (e.g. Material UI, Chakra UI, Ant Design)
as an official guide — all documented migration paths are internal
(Tailwind version, React version, primitive-library choice, utility-package
choice), not library-to-library.

---

## 12. Version information

[Source: https://www.npmjs.com/package/shadcn] Current stable CLI package
version: **4.21.0** (npm, last published 2026-09-04, at time of research
2026-09-09).

[Source: https://ui.shadcn.com/docs/changelog/2026-03-cli-v4] The CLI's
major-version-4 line ("shadcn/cli v4") was introduced in **March 2026**,
adding `shadcn/skills` (AI-agent design-system context), the Presets system,
enhanced inspection flags (`--dry-run`, `--diff`, `--view`), full-project
`init --template` scaffolding, the `--base` primitive-choice flag, `shadcn
info`/`shadcn docs`, `registry:base` items, first-class font registry items,
and `--monorepo` support.

[Source: https://ui.shadcn.com/docs/changelog] shadcn/ui does not publish a
formal LTS/support-window policy in the fetched changelog or docs pages —
Not documented / could not verify whether older major CLI versions receive
any backported fixes. Release cadence is empirically frequent/rolling
(changelog shows near-monthly dated entries, several months in 2026 with
multiple entries), rather than a fixed release-train schedule.

[Source: https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default] Cited
within that changelog entry: **Base UI reached v1.6.0** with over 6 million
weekly downloads at the time shadcn/ui adopted it as the new default
primitive library (July 2026) — this is a fact about the Base UI project
quoted from shadcn's own changelog, not independently verified against
Base UI's own docs in this research pass.

Selected version-sensitive milestones from the official changelog
[Source: https://ui.shadcn.com/docs/changelog]:
- June 2023 — original CLI, styles.
- August 2024 — `npx shadcn init` (rename away from the old `shadcn-ui`
  package naming).
- October 2024 — React 19 support added; Sidebar component.
- February 2025 — Tailwind v4 compatibility; updated registry schema.
- April 2025 — `shadcn` 2.5.0 release.
- June 2025 — Radix UI import-consolidation migration ("radix-ui" package).
- August 2025 — shadcn CLI 3.0 and MCP Server introduced.
- January 2026 — Base UI documentation added (alongside existing Radix docs).
- February 2026 — Unified Radix UI package finalized as the consolidated
  import pattern.
- March 2026 — shadcn/cli v4 (see above); "Luma" style/preset introduced.
- July 2026 — **Base UI becomes the default** primitive library for new
  projects; `shadcn/typeset` and `@shadcn/helpers` introduced; React Aria
  support added; Toast component updated.
- September 2026 — dedicated `cn` utility package released, replacing local
  `clsx`+`tailwind-merge` boilerplate.

---

## 13. Breaking changes

[Source: https://ui.shadcn.com/docs/tailwind-v4] Tailwind v4 adoption
(dated from February 2025) is framed as **non-breaking for existing
projects** (v3 projects keep working) but changes the *default* for new
projects and requires manual migration steps to move an existing project
forward (see §11) — including removal of `React.forwardRef` component
patterns in favor of `data-slot` attributes, and deprecation of the Toast
component (→ Sonner) and the `"default"` style (→ `"new-york"`).

[Source: https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default] The
Radix → Base UI default switch (July 2026) is explicitly **not** a forced
breaking change for existing apps ("Existing production applications can
continue unchanged"); it only changes behavior for newly-initialized
projects (or `add`/`init` runs without `-b radix` after the switch date).

[Source: https://ui.shadcn.com/docs/changelog/2026-09-cn] The `cn` package
release (September 2026) is explicitly documented as **no breaking
changes** for existing projects — old `lib/utils.ts` files keep working
unmodified; migration via `migrate cn` is opt-in.

[Source: https://ui.shadcn.com/docs/changelog/2026-03-cli-v4] The CLI v4
changelog entry, per the fetched page, does **not** enumerate specific
breaking changes versus CLI v3, nor explicit migration steps — Not
documented / could not verify what (if anything) breaks for scripts/tooling
built against the v3 CLI's exact flag surface.

[Inference, not confirmed in docs] Given the project's stated design
philosophy (copied-in source code, not a versioned dependency), the
practical "breaking change" surface for most users is narrower than for a
typical npm UI library: most changes affect *newly generated* code or
*opt-in* migration commands rather than silently altering already-installed
component files in a consumer's repo, since the CLI does not auto-update
previously-installed components without an explicit `add --overwrite` or
`migrate` run.

---

## 14. Limitations

[Source: https://ui.shadcn.com/docs/react-19] React 19 + npm peer-dependency
resolution is a documented friction point: some ecosystem packages may not
yet declare React 19 compatibility, requiring `--force`/`--legacy-peer-deps`
or a temporary React 18 pin; Recharts specifically needs a manual
`react-is` override.

[Source: https://ui.shadcn.com/docs/components-json] Several `components.json`
fields are explicitly documented as **immutable after initialization**:
`style`, `tailwind.baseColor`, and `tailwind.cssVariables` cannot be changed
post-init without effectively reinstalling/reconfiguring the project.

[Source: https://ui.shadcn.com/docs/components] The components overview page
frames the component set as a work in progress ("We are working on adding
more components") and points users to the community registry directory for
components not yet in the core set — implying the first-party component
catalog, while broad (~75 components), is not exhaustive by design, with
gaps expected to be filled by third-party/community registries rather than
the core team.

[Source: https://ui.shadcn.com/docs/registry] The registry protocol's
framework-agnostic design is a documented feature, but also implies a
limitation: an individual registry item's actual portability across
frameworks depends entirely on how that specific item's author wrote it —
Not documented / could not verify what validation, if any, prevents a
registry item from silently declaring itself framework-agnostic while
actually containing framework-specific code.

[Inference, not confirmed in docs] Because components are copied rather
than versioned as a dependency, there is no built-in mechanism to know
whether an already-installed component in a given project is "out of date"
relative to the upstream registry, beyond manually re-running
`add --diff`/`--overwrite` per component — this is a structural
consequence of the "open code" philosophy rather than an explicitly stated
limitation in the docs.

---

## 15. Debugging

[Source: https://ui.shadcn.com/docs/cli] The CLI's `--dry-run` and `--diff`
flags on `add` (and `init`'s inspection flags per the v4 changelog) are the
primary officially documented debugging/inspection tooling — they let a
developer preview exactly what files/dependencies a command would
add/change before committing to it.

[Source: https://ui.shadcn.com/docs/cli] `shadcn info` is documented as
printing framework details, currently-installed components, and
documentation links for the current project — useful for diagnosing
environment/config mismatches.

[Source: https://ui.shadcn.com/docs/helpers/ai-sdk] For chat-interface
components specifically, `@shadcn/helpers`'s AI SDK integration is
documented as enabling deterministic, network-free reproduction of a given
conversation/streaming sequence — explicitly useful for debugging chat UI
behavior without depending on a live, non-deterministic model backend.

Not documented / could not verify: there is no dedicated official "Debugging"
or "Troubleshooting" guide covering runtime component bugs, hydration
mismatches, or styling conflicts distinct from the CLI inspection flags and
the React-19 peer-dependency troubleshooting notes covered in §11/§14.

---

## 16. Integration

[Source: https://ui.shadcn.com/docs/installation] Officially documented
framework integrations (each with a dedicated install guide): **Next.js**,
**Vite**, **TanStack Start**, **Laravel**, **React Router**, **Astro**, and
manual/plain **React**. Each framework guide includes both a scaffold-new-
project path (`shadcn init -t <framework>`) and an "Existing Project"
section for adding shadcn/ui to an app that already exists.

[Source: https://ui.shadcn.com/docs/dark-mode] Dark mode integration guides
are published per framework: Next.js, Vite, Astro, Remix, and TanStack
Start each have a dedicated `/docs/dark-mode/<framework>` page (specific
library choices such as `next-themes` are referenced by the site's
navigation/framework-specific pages rather than in a single unified guide).

[Source: https://ui.shadcn.com/docs/forms/react-hook-form] Form-library
integration is officially documented for **React Hook Form** (with Zod
validation), and the components overview page also lists **TanStack Form**
and **Formisch** as documented form-integration targets.

[Source: https://ui.shadcn.com/docs/mcp] **MCP (Model Context Protocol)
server** integration lets AI coding agents browse, search, and install
components via natural language. Documented client integrations: **Claude
Code** (via `.mcp.json`, initialized with
`shadcn mcp init --client claude`), **Cursor** (`.cursor/mcp.json`),
**VS Code with GitHub Copilot** (`.vscode/mcp.json`), and **Codex**
(`~/.codex/config.toml`). Example config:
```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

[Source: https://ui.shadcn.com/docs/helpers/ai-sdk] **Vercel AI SDK**
integration via `@shadcn/helpers/ai-sdk`: enables scripted, deterministic
chat conversations through `useChat` (no live model/API route needed), plus
"human in the loop" support for client-executed and approval-gated tool
calls within chat UIs — used for building/testing/documenting chat
components and AI SDK–based tool-approval workflows.

[Source: https://ui.shadcn.com/docs/registry/github] **GitHub-as-registry**
integration: a public GitHub repository can be referenced directly as a
registry source address; private repositories require namespace +
authenticated URL configuration (private GitHub registry support added per
the changelog in August 2026).

[Source: https://ui.shadcn.com/docs/monorepo] **Turborepo** is the
officially documented/scaffolded monorepo build-tool integration.

[Inference, not confirmed in docs] The Base-UI-vs-Radix default switch
(§1, §11, §13) is itself effectively an "integration" decision about which
headless-primitive ecosystem a project is wired into, since it changes which
upstream library (`@base-ui-components/react` vs `radix-ui`) the generated
component source imports from.

---

## 17. Production considerations

[Source: https://ui.shadcn.com/docs/registry/authentication] For teams
running their own internal/private registry in production, documented
considerations include token-based auth, HTTPS enforcement, rate limiting,
token rotation, access logging, and returning registry-specific error
context (subscription/expiry/team-restriction messaging) rather than bare
401s.

[Source: https://ui.shadcn.com/docs/react-19] Teams on npm (rather than
pnpm/bun/yarn) adopting React 19 should expect to explicitly choose between
`--force`/`--legacy-peer-deps` installs or a temporary React 18 pin as a
production-readiness decision, and to audit third-party dependencies (e.g.
Recharts) for React 19 peer-dependency overrides before shipping.

[Source: https://ui.shadcn.com/docs/tailwind-v4] Production Tailwind v4
migration requires coordinated updates across CSS variable structure
(`@theme inline`), chart color config, icon/animation packages
(`tailwindcss-animate` → `tw-animate-css`), and the Radix/Base UI primitive
versions the installed components depend on — the docs frame this as a
project-wide, coordinated upgrade rather than a piecemeal one.

[Inference, not confirmed in docs] Because installed components are
project-owned source rather than a pinned dependency version, production
teams bear direct responsibility for tracking upstream shadcn/ui changes
relevant to already-installed components (accessibility fixes, primitive
library security patches, etc.) themselves — there is no `npm audit`/
version-bump signal for component code that has already been copied in,
only for the primitive libraries (Base UI/Radix) and other real npm
dependencies those components still import.

Not documented / could not verify: shadcn/ui's official docs do not publish
dedicated production guidance on topics like SSR streaming edge cases,
CSP/nonce configuration for injected styles, or monitoring/observability —
these appear out of scope for what is fundamentally a component-source
distribution tool rather than a runtime framework.

---

## Sources consulted (official only)

- https://ui.shadcn.com/docs (Introduction)
- https://ui.shadcn.com/docs/changelog (full changelog index)
- https://ui.shadcn.com/docs/installation
- https://ui.shadcn.com/docs/installation/next
- https://ui.shadcn.com/docs/cli
- https://ui.shadcn.com/docs/components-json
- https://ui.shadcn.com/docs/theming
- https://ui.shadcn.com/docs/dark-mode
- https://ui.shadcn.com/docs/registry
- https://ui.shadcn.com/docs/registry/registry-json
- https://ui.shadcn.com/docs/registry/authentication
- https://ui.shadcn.com/docs/registry/github
- https://ui.shadcn.com/docs/registry/faq
- https://ui.shadcn.com/docs/monorepo
- https://ui.shadcn.com/docs/mcp
- https://ui.shadcn.com/docs/components
- https://ui.shadcn.com/docs/components/button
- https://ui.shadcn.com/docs/forms/react-hook-form
- https://ui.shadcn.com/docs/helpers/ai-sdk
- https://ui.shadcn.com/docs/tailwind-v4
- https://ui.shadcn.com/docs/react-19
- https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default
- https://ui.shadcn.com/docs/changelog/2026-03-cli-v4
- https://ui.shadcn.com/docs/changelog/2026-09-cn
- https://ui.shadcn.com/docs/changelog/2026-03-luma
- https://ui.shadcn.com/docs/changelog/2026-07-typeset
- https://www.npmjs.com/package/shadcn (official npm distribution channel)
- https://github.com/shadcn-ui/ui (official GitHub org repo; SECURITY.md)
