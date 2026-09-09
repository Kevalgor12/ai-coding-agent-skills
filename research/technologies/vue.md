# Vue.js — Technology Research

Research date: 2026-09-09. Primary source: `vuejs.org` (the canonical, current Vue 3 docs host — confirmed live and actively maintained; no evidence of a host migration was found). Supplementary authoritative sources: `v3-migration.vuejs.org` (official Vue 2→3 migration guide, a separate subdomain maintained by the Vue team), `github.com/vuejs/core` (official monorepo, releases, changelog), `registry.npmjs.org/vue` (official npm registry metadata, used only to confirm version/dist-tag facts, not as a documentation citation), `devtools.vuejs.org` (official Vue Devtools docs), `router.vuejs.org` and `pinia.vuejs.org` (official companion-library docs maintained by the Vue core team, linked directly from vuejs.org). Citation convention: `[Source: <url>] <claim>.` for documented facts, `[Inference, not confirmed in docs]` for reasoning not explicitly stated, `Not documented / could not verify` where no authoritative answer was found, `Unresolved: ...` where confidence is genuinely low.

**Doc host note:** No migration away from `vuejs.org` was found. Vue 2's docs live separately at `v2.vuejs.org` (archived/legacy), and the Vue 2→3 migration guide lives on its own subdomain, `v3-migration.vuejs.org`. All three were treated as official for this research.

**Framing note on version state at research time:** [Source: https://registry.npmjs.org/vue] As of 2026-09-09, npm's `latest` dist-tag for the `vue` package resolves to **3.5.42** (the current stable line), while **3.6.0 is in release-candidate stage** (`rc` dist-tag → `3.6.0-rc.7`, dated Sep 4 2026 per GitHub releases), with `alpha`/`beta` dist-tags further ahead (`3.6.0-alpha.7`, `3.6.0-beta.17`). This means the *headline new feature of the 3.6 line, Vapor Mode,* is not yet in the stable release channel as of this research date, despite some secondary/community coverage describing it as "confirmed stable" — see the Version Information and Breaking Changes sections for the flagged discrepancy.

---

## 1. Core Concepts

[Source: https://vuejs.org/guide/introduction.html] Vue is described as "The Progressive JavaScript Framework" — it is designed to be incrementally adoptable, usable for anything from enhancing static HTML with no build step, to embedding as Web Components, to full Single-Page Applications (SPA), Server-Side Rendering (SSR), and Static Site Generation (SSG).

[Source: https://vuejs.org/guide/introduction.html] Two foundational pillars are named explicitly: **Declarative Rendering** (extending HTML template syntax to declaratively describe UI based on JS state) and **Reactivity** (Vue automatically tracks JavaScript state changes and efficiently updates the DOM).

[Source: https://vuejs.org/guide/introduction.html] Vue offers two API styles: the **Options API** (organizes component logic using an object of options such as `data`, `methods`, `mounted`) and the **Composition API** (uses imported functions such as `ref()`, `onMounted()` inside a `setup()` function or `<script setup>`). [Source: https://vuejs.org/guide/introduction.html] Official recommendation: for learning, "choose whichever style makes it easier for you to understand"; for production, Options API is suggested for low-complexity scenarios, Composition API + Single-File Components for building full applications.

[Source: https://vuejs.org/guide/introduction.html] Vue's minimal example instantiates an app via `createApp({...}).mount('#app')`, binding reactive `data()` state to a template.

[Source: https://vuejs.org/guide/scaling-up/tooling.html] Vue's recommended production authoring format is the **Single-File Component (SFC)**, a `*.vue` file that encapsulates a component's logic (`<script>`), template (`<template>`), and styles (`<style>`) together, compiled by a build tool (Vite).

[Source: https://vuejs.org/guide/extras/reactivity-in-depth.html] Vue's reactivity works by intercepting property access to `track()` dependencies and `trigger()` updates when values change; `reactive()` uses a JavaScript `Proxy`, and `ref()` uses a getter/setter object with a `.value` accessor, because JavaScript's language semantics offer no way to intercept access to a plain local variable without a container object.

[Source: https://vuejs.org/guide/extras/reactivity-in-depth.html] Destructuring a `reactive()` object breaks reactivity for the destructured binding (the local variable disconnects from the underlying Proxy traps), and a `reactive()` proxy has a different object identity than its source object (`reactive(obj) !== obj`). [VERSION-SENSITIVE, applies to Vue 3's Proxy-based model.]

[Source: https://vuejs.org/guide/extras/composition-api-faq.html] The Composition API exists for four stated reasons: better logic reuse (via composables, replacing mixins), more flexible code organization (co-locating logic by concern instead of by option type), better TypeScript inference, and smaller/more minification-friendly production bundles. [Source: https://vuejs.org/guide/extras/composition-api-faq.html] The docs explicitly state the Options API "is not being deprecated" and remains valid for low-to-medium complexity components; the two APIs can be mixed via `setup()` inside an Options API component, mainly recommended when integrating Composition-API-based library features into an existing Options API codebase.

[Source: https://vuejs.org/guide/reusability/composables.html] A **composable** is a function that "leverages Vue's Composition API to encapsulate and reuse stateful logic," conventionally named with a `use` prefix (e.g. `useMouse()`). Composables must be called synchronously inside `<script setup>`, `setup()`, or another composable/lifecycle hook — not called asynchronously outside `<script setup>`'s top-level `await` exception. Each component instance calling a composable gets an isolated copy of its state.

[Source: https://vuejs.org/guide/introduction.html] Vue supports non-SPA/non-web targets too: desktop and mobile apps (via Electron/Tauri-style integrations), and WebGL/terminal targets are mentioned as reachable via Vue's flexible rendering system, though the introduction page does not enumerate official first-party tooling for each.

---

## 2. Architecture

[Source: https://vuejs.org/guide/extras/rendering-mechanism.html] Vue's rendering pipeline has three stages: **Compile** (templates are compiled to render functions, ahead-of-time via build tools or at runtime), **Mount** (render functions are invoked, walking the resulting Virtual DOM tree to construct real DOM nodes, executed as a reactive effect), and **Patch** (when reactive dependencies used during the mount effect change, the effect re-runs, producing a new VDOM tree that is diffed against the old one, applying only the necessary DOM mutations).

[Source: https://vuejs.org/guide/extras/rendering-mechanism.html] Vue's approach is described as "Compiler-Informed Virtual DOM": because the template compiler and runtime are tightly coupled (unlike, e.g., JSX-based VDOM libraries with a generic runtime), the compiler embeds optimization hints directly into generated render code. Three named optimizations: (1) **Cache Static** — static (non-dynamic) template subtrees are hoisted and rendered once via `innerHTML` rather than re-created on every re-render; (2) **Patch Flags** — each dynamic vnode is annotated with a bitwise integer flag (e.g. `2` for `CLASS`) so the patch algorithm can skip full prop diffing and jump straight to the relevant update path; (3) **Tree Flattening** — dynamic (patch-flagged) descendant nodes are collected into a flat array per "block," so the patch algorithm skips over static subtrees entirely rather than recursively walking the full tree; `v-if`/`v-for` create new nested blocks.

[Source: https://vuejs.org/guide/extras/rendering-mechanism.html] These compiler optimizations also accelerate SSR hydration: patch-flag fast paths apply per element, and only block nodes plus their dynamic descendants are traversed during hydration — described as achieving "partial hydration at the template level."

[Source: https://vuejs.org/guide/extras/reactivity-in-depth.html] Reactivity architecture: dependency subscriptions are stored in a `WeakMap<target, Map<key, Set<effect>>>` structure; `track()` records the currently-running reactive effect against the property being read, and `trigger()` re-runs all subscribed effects when that property is written. [Source: https://vuejs.org/guide/extras/reactivity-in-depth.html] Vue's reactivity is explicitly **runtime-based** (dependency tracking happens during code execution), contrasted with compile-time reactivity approaches (cited example: Svelte) that inject tracking logic at build time; Vue states it "explored [a compile-time] idea" via a "Reactivity Transform" proposal but "decided against it" (no reasoning beyond that decision was extracted from the fetched page).

[Source: https://vuejs.org/guide/extras/reactivity-in-depth.html] Vue 2's reactivity used `Object.defineProperty()` getter/setters exclusively, "due to browser support limitations" on `Proxy`; Vue 3 uses native ES `Proxy` objects for `reactive()`. [VERSION-SENSITIVE: this is a core architectural difference between Vue 2 and Vue 3 reactivity, per the doc's own comparison.]

[Source: https://vuejs.org/guide/extras/rendering-mechanism.html, https://vuejs.org/guide/scaling-up/ssr.html] Vue's core (`vue` package) separates a **compiler** (template → render function) from a **runtime** (VDOM creation/patching, reactivity, component instance management); the runtime itself is split into `runtime-core` (platform-agnostic) and `runtime-dom` (browser DOM operations), enabling custom renderers via `createRenderer` (mentioned in the migration overview) for non-DOM targets.

[Source: https://vuejs.org/guide/scaling-up/tooling.html] Separately, the **project tooling architecture** treats `vue` (the framework runtime/compiler) as distinct from `create-vue`/Vite (scaffolding and dev server/bundler), `vue-tsc`/Vue Language Tools (TypeScript type-checking and IDE language server, replacing the older Vetur), and companion libraries (`vue-router`, `pinia`) that are officially maintained but published/versioned independently of `vue` core.

[Source: https://github.com/vuejs/core/releases/tag/v3.6.0-rc.1] As of the 3.6 line (release-candidate as of this research date, not yet promoted to the stable npm `latest` tag), an alternate architecture called **Vapor Mode** exists as an opt-in compilation mode for SFCs that "reduc[es] baseline bundle size and improv[es] performance" by compiling directly to fine-grained DOM update instructions instead of going through the Virtual DOM at all; it requires `<script setup>` syntax (Options API is unsupported in Vapor components) and reuses the same underlying reactivity primitives. [VERSION-SENSITIVE — 3.6.x only, and still pre-stable at research time; see Version Information / Breaking Changes.]

---

## 3. APIs

### Reactivity API
[Source: https://vuejs.org/guide/extras/reactivity-in-depth.html, https://vuejs.org/guide/reusability/composables.html] Core primitives: `ref()` (reactive container for any value, `.value` access, auto-unwrapped in templates), `reactive()` (deep-reactive Proxy of an object), `computed()` (derived reactive value, cached), `watch()`/`watchEffect()` (reactive side-effect subscriptions), `toValue()` (normalizes a ref, getter function, or plain value into a plain value — used in composables to accept flexible input types), `shallowRef()`/`shallowReactive()` (root-level-only reactivity, for performance with large data — see Performance section).

### Application API
[Source: https://vuejs.org/api/application.html] `createApp(rootComponent, rootProps?)` creates an app instance. `app.mount(rootContainer)` mounts to a DOM element/selector (callable once per app). `app.unmount()` tears down the app and fires unmount lifecycle hooks. `app.use(plugin, ...options)` installs a plugin. `app.component(name, def?)` registers/retrieves a global component. `app.directive(name, def?)` registers/retrieves a global custom directive. `app.provide(key, value)` provides an app-level injectable value.

[Source: https://vuejs.org/api/application.html] `app.config` surface: `errorHandler(err, instance, info)` (global uncaught-error handler), `warnHandler(msg, instance, trace)` (custom handler for Vue's dev-time runtime warnings), `globalProperties` (object of properties/methods exposed on every component instance — documented as something to "use scarcely," see Anti-Patterns), `performance` (boolean; enables component performance markers in the browser Performance panel, dev-only), `compilerOptions` (runtime template compiler config: `isCustomElement(tag)`, `whitespace: 'condense'|'preserve'`, `delimiters: [string,string]` — default `['{{','}}']` — and `comments: boolean`).

### Component/SFC compiler-macro API (`<script setup>`)
[Source: https://vuejs.org/api/sfc-script-setup.html] `defineProps()` / `defineEmits()` — declare props/emits with type inference; both support a runtime-object form and (3.3+) a type-only generic form, but not both simultaneously in the same block. `defineExpose({...})` — explicitly exposes bindings to parent `template ref` access (components using `<script setup>` are closed/private by default). `defineOptions({...})` **(3.3+)** — declare non-prop/emit component options (e.g. `inheritAttrs`) directly inside `<script setup>`. `defineSlots<{...}>()` **(3.3+)** — type-hints for slots. `defineModel()` **(3.4+)** — declares a two-way-bindable prop for `v-model`, returning a ref whose writes auto-emit `update:<name>`; supports a modifiers/transform form. `useSlots()` / `useAttrs()` — programmatic access to slots/attrs equivalent to `this.$slots`/`this.$attrs` in Options API.

[Source: https://vuejs.org/api/sfc-script-setup.html] **Reactive Props Destructure**, i.e. destructuring `defineProps()`'s return value while retaining reactivity (Vue auto-transforms bare destructured bindings into `props.x` access), is available **3.5+**. [VERSION-SENSITIVE]

### Async / Suspense API
[Source: https://vuejs.org/guide/components/async.html] `defineAsyncComponent(loader | { loader, loadingComponent, errorComponent, delay, timeout, suspensible })` — lazy-loads a component on demand; `delay` defaults to 200ms before showing `loadingComponent` (to avoid flicker), `timeout` defaults to `Infinity`.

[Source: https://vuejs.org/guide/components/async.html] **Lazy Hydration strategies (3.5+)**: `hydrateOnIdle()`, `hydrateOnVisible()`, `hydrateOnMediaQuery(query)`, `hydrateOnInteraction(event | event[])`, plus a custom `HydrationStrategy` function type — passed as the `hydrate` option of `defineAsyncComponent` to control when an SSR-rendered async component becomes interactive on the client. [VERSION-SENSITIVE: 3.5+]

[Source: https://vuejs.org/guide/built-ins/suspense.html] `<Suspense>` — built-in component with a default slot (rendered once nested async dependencies resolve) and a `#fallback` slot (shown while pending); emits `pending`, `resolve`, `fallback` events; accepts a `timeout` prop. **Explicitly and currently marked experimental**: "`<Suspense>` is an experimental feature. It is not guaranteed to reach stable status and the API may change before it does." Nested `<Suspense>` requires the `suspensible` prop (3.3+) to avoid empty intermediate nodes. Vue Router's own lazy-loaded route components do **not** trigger Suspense — only true async components do.

### Web Components API
[Source: https://vuejs.org/guide/extras/web-components.html] `defineCustomElement(componentOptions)` compiles a Vue component into a native Custom Element class, registered via `customElements.define(tag, ElementClass)`; props/emits map to element properties/attributes (with automatic type casting for `Boolean`/`Number`) and native `CustomEvent`s respectively. `.ce.vue` SFC extension injects the component's `<style>` into the custom element's shadow root instead of extracting to a page-level stylesheet.

### Companion library APIs (officially maintained, not in `vue` core)
[Source: https://router.vuejs.org/introduction.html] **Vue Router** — "the official router for Vue.js," deeply integrated with core; docs describe current major lines as v4.x (for Vue 3) and v3.x (for Vue 2), with v5.x also referenced on the intro page (treated with caution — see Unresolved below since only summarized text was retrieved, not the full versioned matrix).

[Source: https://pinia.vuejs.org/introduction.html] **Pinia** — the official state-management library; does not require the Composition API (map-helper APIs exist for Options API use too); Vue 2 support was discontinued in 2025 per the fetched summary (documentation now focuses on Vue 3). [VERSION-SENSITIVE]

Unresolved: the Vue Router intro-page summary mentions "v4.x and v5.x" as current plus "v3.x... for users on older Vue versions," but this research pass only retrieved an AI-summarized extraction of the page, not the raw version-support table. The existence/status of a Vue Router v5 as of 2026-09-09 should be re-verified directly against `router.vuejs.org` before being cited as fact in any downstream skill.

---

## 4. Configuration

[Source: https://vuejs.org/guide/scaling-up/tooling.html] Recommended project bootstrap is `npm create vue@latest` (or the pnpm/yarn/bun equivalents), which runs the official `create-vue` scaffolding tool and produces a Vite-based project pre-configured for production builds, TypeScript (optional), routing, state management, testing, and linting, selected via interactive prompts.

[Source: https://vuejs.org/guide/scaling-up/tooling.html] **Vue CLI is in maintenance mode**; the docs recommend Vite for new projects "unless you rely on specific webpack-only features," and link a community migration guide plus `awesome-vite`'s auto-migration tooling for existing Vue-CLI projects. [VERSION-SENSITIVE / ecosystem-status note, not major-version-specific.]

[Source: https://vuejs.org/guide/typescript/overview.html] TypeScript project config: `isolatedModules` or `verbatimModuleSyntax` is required in `tsconfig.json` for Vite/esbuild-based transpilation; `strict: true` (or at minimum `noImplicitThis`) is recommended so `this` is correctly typed under the Options API; `jsx: "preserve"` + `jsxImportSource: "vue"` for TSX support; `paths` for resolver aliases (e.g. `@/*`). Vite performs transpilation only (no type-checking) during dev for speed — type-checking is a separate step via `vue-tsc` (wraps `tsc`) or the IDE extension.

[Source: https://vuejs.org/guide/extras/web-components.html] Runtime template-compiler configuration for recognizing non-Vue custom elements is set via `compilerOptions.isCustomElement` — configured through the Vite plugin (`@vitejs/plugin-vue`'s `template.compilerOptions.isCustomElement`) or, for Vue CLI, via `vue-loader`'s `compilerOptions` in a `chainWebpack` config block. The same option is also settable at runtime via `app.config.compilerOptions.isCustomElement` for non-build-tool (in-browser template compilation) setups.

[Source: https://vuejs.org/api/application.html] App-instance-level configuration lives on `app.config` (see APIs section): `errorHandler`, `warnHandler`, `globalProperties`, `performance`, `compilerOptions.{isCustomElement, whitespace, delimiters, comments}`.

[Source: https://vuejs.org/guide/scaling-up/testing.html] Test-runner configuration example given for Vitest is set inside `vite.config.js`'s `test` field (e.g. `{ globals: true, environment: 'happy-dom' }`), reusing the same config file as the app build rather than a separate test-runner config file — reflecting Vitest's Vite-native design.

[Source: https://vuejs.org/guide/scaling-up/tooling.html] Official linting is via `eslint-plugin-vue` (Vue-SFC-aware ESLint plugin); formatting via the "Vue - Official" (Volar/Vue Language Tools) extension's built-in SFC formatter, or Prettier (which has Vue SFC support).

---

## 5. Recommended Patterns

[Source: https://vuejs.org/guide/reusability/composables.html] Composables are the recommended unit of reusable **stateful** logic, replacing the Options-API-era mixin pattern; return a plain (non-reactive-wrapped) object of refs so destructuring at the call site preserves reactivity and lets consumers rename bindings to avoid collisions; side effects (event listeners, subscriptions) should be set up in `onMounted()`/created inline and always torn down in `onUnmounted()`; composables should accept `ref`s, getter functions, or plain values interchangeably by normalizing input through `toValue()`.

[Source: https://vuejs.org/guide/reusability/composables.html] Composables should only be invoked synchronously in `<script setup>`, `setup()`, or another composable/lifecycle-hook context (with the sanctioned exception of after a top-level `await` inside `<script setup>`) — this is what lets Vue correctly associate the composable's lifecycle hooks and injections with the right component instance.

[Source: https://vuejs.org/guide/reusability/plugins.html] For cross-cutting app-wide state or utilities exposed to many components, the documentation recommends **provide/inject** (`app.provide()` + `inject()`) over `app.config.globalProperties`, explicitly to avoid namespace pollution/confusion from many plugins each injecting global properties.

[Source: https://vuejs.org/guide/scaling-up/state-management.html] For small/simple shared state, a plain `reactive()` object exported from a module is an officially documented pattern; for anything beyond that, **Pinia is the official recommended state management library** for Vue 3, chosen over the (now maintenance-mode) Vuex for its stronger TypeScript inference, Composition-API-style API, Devtools integration (timeline, time-travel), HMR support, and SSR support.

[Source: https://vuejs.org/guide/components/registration.html] **Local component registration is preferred over global registration** for most cases: it is tree-shakeable (unused globally-registered components are not eliminated from the bundle), keeps dependency relationships explicit/traceable, and avoids global-scope pollution; global registration is reserved for components used pervasively across the app (e.g. base UI primitives). PascalCase is the recommended naming convention for component tags in SFCs/string templates (valid JS identifier, clear visual distinction from native HTML elements and Web Components).

[Source: https://vuejs.org/guide/best-practices/performance.html] Recommended update-performance patterns: keep child-component `props` stable by computing derived/boolean values in the parent rather than passing a whole shared object plus a comparison key down to every list child; use `v-once` for content that never changes after first render; use `v-memo` to skip re-render of large sub-trees/`v-for` blocks when a dependency array is unchanged; as of **Vue 3.4+**, `computed()` only triggers downstream effects if its return value actually changed, and the docs show a pattern of manually returning the previous object reference from inside a `computed(oldValue => ...)` getter when the derived value is unchanged, to avoid needless downstream re-triggers.

[Source: https://vuejs.org/guide/best-practices/testing.html — cited via https://vuejs.org/guide/scaling-up/testing.html] Recommended testing pattern: assert a component's rendered output and behavior in response to props/user interaction (its public interface), not internal state/method calls; mock as little as possible in component tests; avoid relying solely on snapshot tests.

---

## 6. Anti-Patterns

[Source: https://vuejs.org/style-guide/] The official **Style Guide** organizes rules into four priority tiers: **A — Essential** (error prevention, near-zero exceptions), **B — Strongly Recommended**, **C — Recommended** (arbitrary-but-consistent conventions), and **D — Use with Caution**, which the guide itself frames as documenting patterns that "can become anti-patterns" when overused.

[Source: https://vuejs.org/style-guide/rules-use-with-caution] Priority-D ("use with caution") rules found: (1) **element selectors with `scoped` styles** are discouraged — Vue's scoped-CSS mechanism adds an attribute selector to every rule, and bare element selectors (e.g. `button { ... }`) are "significantly slower" than class selectors at that same specificity, because the browser must match every element of that tag rather than a scoped class; (2) **implicit parent-child communication** — reaching up via `this.$parent` to read/mutate ancestor state, or mutating a prop object directly from a child (e.g. binding `v-model` straight onto a prop) — is discouraged in favor of the explicit "props down, events up" model (`emits`/`defineEmits`, `@input`-style custom events).

[Source: https://vuejs.org/guide/reusability/plugins.html] Explicit anti-pattern warning: "Use global properties scarcely, since it can quickly become confusing if too many global properties injected by different plugins are used throughout an app" — `app.config.globalProperties` is the named mechanism to avoid overusing; provide/inject is the recommended alternative (see Recommended Patterns).

[Source: https://vuejs.org/guide/essentials/list.html] Anti-pattern: using `v-if` and `v-for` on the *same* element — the docs describe this as producing an error in Vue 3 because `v-if` is evaluated with higher precedence and cannot see the `v-for` scope variable; the recommended fix is either a computed property that pre-filters the list, or moving `v-for` to a wrapping `<template>` and `v-if` to the inner element.

[Source: https://vuejs.org/guide/essentials/list.html] Anti-pattern: directly mutating an array by index (`items.value[0] = x`) or via non-reactive-triggering methods (`filter()`, `concat()`, `slice()` used in place without reassignment) and expecting the view to update; and calling mutating array methods (`reverse()`, `sort()`) directly inside a `computed()` getter, which silently mutates the source array as a side effect of what should be a pure derivation — the docs recommend cloning (`[...array]`) before calling these.

[Source: https://vuejs.org/guide/best-practices/security.html] Explicit anti-pattern / severe warning: **never** compile untrusted/user-provided strings as a Vue template (`template: userProvidedString`) — the docs equate this directly with arbitrary JavaScript execution, stating there is "no practical way for Vue to completely shield against malicious code execution" in that scenario short of unrealistic performance overhead.

[Source: https://vuejs.org/guide/best-practices/performance.html] Anti-pattern: introducing unnecessary component-instance abstractions (e.g. wrapper/renderless components) inside large `v-for` lists — the docs state component instances are "much more expensive than plain DOM nodes," so removing one superfluous wrapper component from a 100-item list removes "hundreds" of component instances.

---

## 7. Security

[Source: https://vuejs.org/guide/best-practices/security.html] **Rule No. 1, stated verbatim in spirit:** never use non-trusted content as a component's `template` — equivalent to arbitrary code execution.

[Source: https://vuejs.org/guide/best-practices/security.html] Vue **automatically HTML-escapes** text interpolations (`{{ }}`) and dynamic attribute bindings (`:attr="..."`, applied via native browser APIs like `setAttribute`) — this is the framework's default XSS mitigation and requires no developer action.

[Source: https://vuejs.org/guide/best-practices/security.html] **`v-html` (and raw `innerHTML`)** bypass escaping entirely and are explicitly flagged as an HTML-injection vector: "only use `v-html` on trusted content and never on user-provided content," with the caveat that even "trusted" user content is never 100% safe unless sandboxed in an iframe or shown only to the user who authored it.

[Source: https://vuejs.org/guide/best-practices/security.html] **URL injection**: user-provided URLs bound via `:href` should be sanitized **on the backend before persistence**, not only client-side — the docs give this as the primary reason (protecting every client: web, mobile, etc.), and mention `@braintree/sanitize-url` as an example client-side library while stressing it is not a substitute for backend sanitization.

[Source: https://vuejs.org/guide/best-practices/security.html] **Style injection**: Vue explicitly prevents rendering literal `<style>` tags bound to interpolated user content (a documented framework-level mitigation), because malicious CSS can enable clickjacking; the recommended safe pattern for user-influenced styling is the object syntax for `:style` with an explicit whitelist of style properties, never a raw user-controlled CSS string.

[Source: https://vuejs.org/guide/best-practices/security.html] **JavaScript/event injection**: never bind user-provided strings to event-handler attributes (e.g. `:onclick="userProvidedCode"`); this is called out as equally unsafe as unsanitized `v-html`, with the same "safe only in a sandboxed iframe" caveat.

[Source: https://vuejs.org/guide/best-practices/security.html] The docs explicitly state Vue does **not** treat certain scenarios as framework vulnerabilities, because the developer opted into the unsafe behavior: rendering unsanitized user content directly as a Vue template, and mounting a Vue app onto a DOM node that mixes server-rendered markup with user-provided content — the latter is called out specifically as unsafe and to be avoided.

[Source: https://vuejs.org/guide/best-practices/security.html] CSRF/XSSI-class HTTP vulnerabilities are explicitly framed as a **backend** responsibility, not something Vue itself addresses; the docs direct developers to coordinate with backend teams and reference the OWASP XSS Prevention Cheat Sheet and the HTML5 Security Cheat Sheet as external resources.

[Source: https://vuejs.org/guide/best-practices/security.html] Vulnerability reporting: **security@vuejs.org**, described as prioritized for immediate response.

[Source: https://vuejs.org/guide/best-practices/security.html] Additional SSR-specific security concerns are called out as applicable, with a pointer to the SSR guide, but the security page itself does not enumerate them in the fetched content — see the SSR cross-request-state-pollution note under Architecture/Production Considerations, which is the one SSR-adjacent hardening concern this research pass found documented ([Source: https://vuejs.org/guide/scaling-up/ssr.html]).

[Source: https://registry.npmjs.org/vue] A separate **`vue` CSP-build dist-tag** exists (`csp` → `1.0.28-csp` per npm metadata retrieved in this pass) — Not documented / could not verify what this build specifically changes (e.g. avoiding `new Function()` for CSP `unsafe-eval` compliance) from the vuejs.org guide pages fetched in this research pass; flagged for follow-up rather than guessed.

---

## 8. Performance

[Source: https://vuejs.org/guide/best-practices/performance.html] Recommended profiling tools: **PageSpeed Insights** / **WebPageTest** for production/field profiling; **Chrome DevTools' Performance panel** (combined with `app.config.performance = true` to emit Vue-specific component render/patch markers) and the **Vue Devtools extension**'s built-in profiling feature for local/dev profiling.

[Source: https://vuejs.org/guide/best-practices/performance.html] **Load-performance guidance**: avoid pure client-rendered SPAs for load-sensitive pages — use SSR or SSG instead for faster time-to-content; separate static marketing pages from the main SPA bundle. Enable tree-shaking via a build step (cited savings: roughly 14kb min+gzip from tree-shaking unused Vue APIs, another roughly 14kb from precompiling templates so the runtime template compiler isn't shipped). Prefer ESM-friendly dependency builds (e.g. `lodash-es` over `lodash`) for tree-shaking; the no-build-step **petite-vue** (~6kb) is mentioned as an option for progressive-enhancement scenarios. Use `bundlejs.com`-style tools to verify dependency footprint. Use code splitting via dynamic `import()`, `defineAsyncComponent()`, and Vue Router's lazy route-component loading (`() => import('./Home.vue')`).

[Source: https://vuejs.org/guide/best-practices/performance.html] **Update-performance guidance**: keep child props "stable" (compute derived booleans in the parent instead of passing a whole object + separate comparison key so every list child re-renders on any change); `v-once` for permanently-static subtrees; `v-memo="[deps]"` to skip re-render of large subtrees/`v-for` blocks when the given dependency array hasn't changed; **as of Vue 3.4**, `computed()` only re-triggers dependents if the computed value actually changed (not merely re-evaluated) — with a documented pattern for object-returning computeds to manually diff and return the previous reference when unchanged, since object equality otherwise always differs.

[Source: https://vuejs.org/guide/best-practices/performance.html] **General/list-heavy guidance**: virtualize lists of "1000+ items" (or generally very large lists) so only visible rows are rendered — community libraries named: `vue-virtual-scroller`, `vue-virtual-scroll-grid`, `vueuc/VVirtualList` (Vue does not ship a first-party virtualization primitive per this page). For very large, effectively-immutable datasets, use `shallowRef()`/`shallowReactive()` to avoid deep-reactivity overhead — with the explicit caveat that in-place nested mutation then stops being reactive and callers must replace the relevant reference (root value for `shallowRef`, or the specific nested object) to trigger updates.

[Source: https://vuejs.org/guide/best-practices/performance.html] Named metrics to track: **Largest Contentful Paint (LCP)** for load performance, **Interaction to Next Paint (INP)** for update responsiveness, plus bundle size and component-instance count (via Devtools).

---

## 9. Testing

[Source: https://vuejs.org/guide/scaling-up/testing.html] Three testing tiers are named with official tool recommendations: **Unit testing** (isolated functions/composables/modules) → **Vitest**, described as "created and maintained by members of the Vue / Vite team" and integrating tightly with Vite-based projects. **Component testing** (props, events, slots, styles, lifecycle, user interaction, at the public-interface level) → **Vitest + `@vue/test-utils`** (the official low-level component-mounting library) for a fast Node-based approach, or **Cypress Component Testing** for a real-browser approach that also catches style/layout issues; `@testing-library/vue` is named as an alternative, user-centric mounting library. **End-to-end (E2E) testing** (multi-page flows against a production build, real network/backend) → **Playwright** (cross-browser: Chromium, WebKit, Firefox; praised for debugging) or **Cypress** (graphical UI, component-testing crossover).

[Source: https://vuejs.org/guide/scaling-up/testing.html] Composable testing pattern: simple reactivity-only composables can be called directly in a test and asserted on their returned refs; composables using lifecycle hooks or `provide`/`inject` need a `withSetup()` test helper that invokes the composable inside a throwaway `createApp({ setup() {...} }).mount(...)` so lifecycle/injection context exists, then explicitly `app.unmount()`s afterward.

[Source: https://vuejs.org/guide/scaling-up/testing.html] Recommended testing principles: assert on a component's public interface (rendered output, reaction to props/slots/user input) rather than private state or internal method calls; mock as little as possible; do not rely exclusively on snapshot testing.

[Source: https://vuejs.org/guide/scaling-up/testing.html] Minimal Vitest setup shown: `npm install -D vitest happy-dom @testing-library/vue`, with `test: { globals: true, environment: 'happy-dom' }` added to `vite.config.js` and a `"test": "vitest"` script in `package.json`.

[Source: https://vuejs.org/guide/scaling-up/tooling.html] Jest is mentioned only as an alternative unit-test runner via a community `vite-jest` adapter, not as a first-line recommendation.

---

## 10. Deployment

[Source: https://vuejs.org/guide/best-practices/production-deployment.html] Vue ships development-only behavior (error/pitfall warnings, props/events runtime validation, reactivity debugging hooks, Devtools integration hooks) that adds overhead and dead code, and must be stripped for production via a production build.

[Source: https://vuejs.org/guide/best-practices/production-deployment.html] **No-build-tool / CDN usage**: load the `.prod.js`-suffixed builds (e.g. `vue.global.prod.js`, `vue.esm-browser.prod.js`) — these are pre-minified with development-only code branches removed.

[Source: https://vuejs.org/guide/best-practices/production-deployment.html] **Build-tool usage**: projects scaffolded via `create-vue` (Vite) or Vue CLI (webpack) are pre-configured correctly; for custom setups, the docs specify three requirements: `vue` must resolve to the `vue.runtime.esm-bundler.js` build, [compile-time feature flags](https://vuejs.org/api/compile-time-flags) must be configured correctly, and `process.env.NODE_ENV` must be replaced with the literal string `"production"` at build time. Links out to Vite's own build/deploy guides (`vite.dev/guide/build.html`, `vite.dev/guide/static-deploy.html`) and Vue CLI's deployment guide for the actual bundler-level steps.

[Source: https://vuejs.org/guide/best-practices/production-deployment.html] **Error tracking**: set `app.config.errorHandler = (err, instance, info) => {...}` to route uncaught errors to a tracking service; the docs name **Sentry** and **Bugsnag** as having official Vue-specific integration guides.

[Source: https://vuejs.org/guide/scaling-up/ssr.html] For SSR/SSG deployment specifically, the docs steer production users toward a higher-level meta-framework — **Nuxt** is named as "the recommended" one — rather than hand-rolling SSR build/deploy coordination, because Nuxt handles the dual client/server build, routing, state management, and hydration complexity; **VitePress** is named as the SSG option for docs/content sites. SSR deployment requires a Node.js server process (rendering is CPU-intensive and needs caching strategy); it is explicitly not compatible with pure static-file hosting, unlike SSG output.

---

## 11. Migration

[Source: https://v3-migration.vuejs.org/] The Vue team maintains a dedicated, separately-hosted **Vue 2 → Vue 3 migration guide** at `v3-migration.vuejs.org`, aimed at developers with prior Vue 2 experience; framed against the fact that "Vue 2 support ended on December 31, 2023" [also stated at https://vuejs.org/guide/introduction.html]. The guide's own recommendation is to learn Vue 3 primarily through the main `vuejs.org` docs and consult the migration guide only for specific "how did X change" questions, rather than reading it front-to-back.

[Source: https://v3-migration.vuejs.org/] A dedicated **Migration Build** is documented as available, providing a Vue-2-compatible runtime configuration to ease incremental upgrades of existing Vue 2 codebases (and to give library authors a compatibility bridge) rather than requiring an all-at-once rewrite.

[Source: https://v3-migration.vuejs.org/breaking-changes/] Breaking changes are catalogued by category: **Global API** (moved from a global `Vue` object to a per-`createApp()` application instance; global/internal APIs restructured to be tree-shakable), **Template Directives** (`v-model` component usage reworked, replacing the old `.sync` modifier; `key` usage on `<template v-for>`/non-`v-for` nodes changed; `v-if`/`v-for` precedence on the same element changed; `v-bind="object"` became order-sensitive; the `v-on:event.native` modifier was removed), **Components** (functional components must now be plain functions; async components require `defineAsyncComponent`; component custom events must be declared via the `emits` option), **Render Function** (API updated; `$scopedSlots` removed — all slots now exposed as functions via `$slots`; `$listeners` removed/merged into `$attrs`; `$attrs` now includes `class`/`style`), **Custom Elements** (custom-element resolution now happens at template-compile time; `<component>` reserved for `is`-attribute usage), and a broad **Lifecycle & Other** bucket (`destroyed` → `unmounted`, `beforeDestroy` → `beforeUnmount`; prop `default` factory functions lose access to `this`; custom directive hook API realigned to component lifecycle naming; `data` must be a function even on the root instance; transition class names changed; array watchers require an explicit `deep: true` to catch in-place mutation; a mounted app no longer replaces its target DOM element outright).

[Source: https://v3-migration.vuejs.org/breaking-changes/] **Removed APIs**: `keyCode` modifiers for `v-on`, the `$on`/`$off`/`$once` instance event-emitter methods, filters (the `{{ value | filter }}` template syntax), inline-template attributes, `$children`, the `propsData` app-creation option, `$destroy()`, and the global/instance `Vue.set`/`Vue.delete`/`$set`/`$delete` reactivity-caveat-workaround APIs (superseded by Proxy-based reactivity no longer needing them).

[Source: https://github.com/vuejs/core/releases/tag/v3.6.0-rc.1] Within the still-in-progress **Vue 3.6** line (not yet stable as of this research date — see Version Info), the release notes describe Vapor Mode as introducing its own compatibility boundary rather than a breaking change to existing Options/Composition-API code: Vapor components are opt-in per-SFC (`<script setup vapor>` / `<script vapor>` / `<template vapor>`) and, within that opt-in scope only, do **not** support the Options API, global properties, `@vue:xxx` lifecycle DOM events, `getCurrentInstance()`, `v-memo`, or template refs exposing `$el`/`$props`/etc.; event handling for Vapor components uses document-level event delegation, meaning `stopPropagation()` inside a Vapor handler can prevent *other* delegated handlers elsewhere in the document from firing (a documented behavioral difference from standard VDOM-mode event handling); calling `slots.default()` in Vapor mode actually executes render logic rather than being inspectable as a dry run; custom directives use a different interface (reactive getters) in Vapor mode.

[Source: https://vuejs.org/guide/typescript/overview.html] Separately from major-version migration, the docs explicitly recommend **migrating off Vue CLI to Vite**, citing `ts-loader`-related type-checking misalignment with source, slow builds, and redundant double type-checking (IDE + build) as the reasons, with a pointer to a community Vue-CLI-to-Vite migration article and `awesome-vite`'s automated tooling.

Not documented / could not verify: an official "migrating from React/Angular/Svelte to Vue" guide was not found in this research pass; the official migration content is scoped specifically to Vue-2-to-Vue-3 and Vue-CLI-to-Vite, not cross-framework migration.

---

## 12. Version Information

[Source: https://registry.npmjs.org/vue] npm dist-tags for the `vue` package, captured 2026-09-09: `latest` → **3.5.42**, `rc` → **3.6.0-rc.7**, `beta` → **3.6.0-beta.17**, `alpha` → **3.6.0-alpha.7**, `v2-latest`/`legacy` → **2.7.16**, `csp` → **1.0.28-csp**.

[Source: https://github.com/vuejs/core/releases] Recent stable patch history on the 3.5.x line as of this pass: 3.5.40 (Jul 16 2026), 3.5.41 (Aug 5 2026), 3.5.42 (Aug 27 2026); the 3.6.0 pre-release train ran in parallel: rc.1 (Jul 18), rc.2 (Jul 22), rc.3 (Aug 11), rc.4 (Aug 14), rc.5 (Aug 21), rc.6 (Aug 28), rc.7 (Sep 4 2026).

[Source: https://vuejs.org/about/releases] Documented release-cadence policy: **no fixed release cycle**; patch releases ship as needed; minor releases ship roughly every 3–6 months, always contain new features, and go through a beta pre-release phase; major releases are announced ahead of time and progress through early-discussion → alpha → beta → RC phases before stabilizing. Pre-release channels are installable via `npx install-vue@alpha|beta|rc|edge` (`edge` tracks the latest commit on main); the docs warn pre-releases are unstable and production usage should pin exact versions.

[Source: https://vuejs.org/about/releases] Semver policy with two documented carve-outs: (1) bundled **TypeScript type definitions** may ship incompatible changes in a **minor** release, because TS itself introduces breaking changes between its own minor versions and Vue sometimes needs newer TS features — the docs recommend pinning to the current Vue minor and upgrading TS types deliberately; (2) **compiled-template output** from a newer minor version's compiler is not guaranteed compatible with an older minor version's runtime — a concern specifically for library authors shipping precompiled `.vue` output, not for applications (whose compiler and runtime versions always match at build time).

[Source: https://vuejs.org/guide/introduction.html] **Vue 2 reached end of support on December 31, 2023** and receives no new features, fixes, or security patches from the core team as of that date; `2.7.16` (per npm `legacy`/`v2-latest` dist-tags above) is the final published Vue 2 line version found in this pass. Not documented / could not verify: whether any paid/third-party extended-support program for Vue 2 (e.g. via a vendor such as HeroDevs) is officially endorsed or linked from vuejs.org — this research pass did not find such an endorsement on the fetched pages, so no claim is made either way.

[Source: https://registry.npmjs.org/vue, https://github.com/vuejs/core/releases/tag/v3.6.0-rc.1] **Vapor Mode / Vue 3.6 status conflict, explicitly flagged**: secondary/community sources found during this research pass (Vue School, Medium, and other blogs — not cited as authorities here per this project's sourcing rules) describe Vapor Mode as "confirmed stable" by Evan You. The *official* signal available in this pass — npm's `latest` tag still pointing at 3.5.42 and the newest 3.6 build still carrying an `-rc.N` pre-release identifier as of Sep 4 2026 — does not corroborate general availability as of the 2026-09-09 research date; and the official 3.6.0-rc.1 GitHub release notes themselves describe Vapor as "feature-complete" but still recommend it only for partial adoption or small new apps, not full-scale production use. Unresolved: whether Vue 3.6 (and Vapor Mode's promoted status) has shipped to the stable npm channel between the community coverage's publication and this research pass's npm snapshot should be re-checked at time of use — do not assume Vapor Mode is production-stable without re-verifying the live npm `latest` tag and official release notes.

---

## 13. Breaking Changes

[Source: https://v3-migration.vuejs.org/breaking-changes/] The full Vue 2 → Vue 3 breaking-changes catalogue is summarized in the Migration section above (Global API restructuring, template-directive precedence/behavior changes, component/render-function API changes, custom-element resolution timing, lifecycle hook renames, and a list of outright-removed APIs including filters, `$children`, `propsData`, `$set`/`$delete`, and the `keyCode` event modifiers). This is the only major-version breaking-change set the official docs currently catalogue in a dedicated reference page (Vue 3 is the only major version with a published, comprehensive from-guide; no Vue 3 → Vue 4 breaking-changes page exists, since no Vue 4 exists as of this research date). [VERSION-SENSITIVE: applies specifically to upgrading a Vue-2-authored codebase; does not describe any breaking change between Vue 3 minor versions, which is a distinct, much smaller category — see below.]

[Source: https://vuejs.org/api/sfc-script-setup.html] Within the Vue 3 line, several `<script setup>` capabilities were introduced (additively, not as breaking changes) at specific minors: `defineOptions()` and `defineSlots()` at **3.3**, `defineModel()` at **3.4**, and Reactive Props Destructure at **3.5**. These are feature additions, not breaking removals, but are flagged here because code relying on them will not run on an earlier Vue 3 minor.

[Source: https://vuejs.org/guide/best-practices/performance.html] The `computed()` change-detection behavior shift (only re-triggering dependents when the computed's return value actually differs, rather than on every re-evaluation) is dated to **Vue 3.4** and is a documented behavioral change within the 3.x line — not cataloged on the dedicated breaking-changes page in this research pass, but worth flagging as a within-major-version behavioral change since code relying on unconditional re-triggering (e.g. an object-returning computed used purely for its side effect of re-running on every dependency touch) could observe different behavior after upgrading past 3.4. [Inference, not confirmed in docs: whether the Vue team formally classifies this as a "breaking change" anywhere outside the performance guide's framing was not verified in this pass.]

[Source: https://github.com/vuejs/core/releases/tag/v3.6.0-rc.1] Within the pre-stable 3.6 line, Vapor Mode's documented incompatibilities (Options API unsupported in Vapor-opted components, no `getCurrentInstance()`/`v-memo`/certain template-ref properties, document-level event delegation altering `stopPropagation()` semantics) are scoped **only** to components that explicitly opt in via the `vapor` markers — standard VDOM-mode Vue 3 components are stated to be unaffected. [VERSION-SENSITIVE, 3.6.x opt-in only, and not yet stable — see Version Information.]

Not documented / could not verify: an official "Vue 1 → Vue 2" breaking-changes page was not searched for in this pass (Vue 1 is long past end-of-life and out of scope for a project targeting current, version-aware guidance); not pursued further.

---

## 14. Limitations

[Source: https://vuejs.org/guide/extras/reactivity-in-depth.html] Reactivity has documented ergonomic limitations rooted in JavaScript language semantics: destructuring a `reactive()` object's properties into local variables loses reactivity for those bindings; a `reactive()` proxy is not referentially equal to its source object; and primitive values require the `ref()` wrapper (with explicit `.value` access outside templates) because JS offers no way to intercept access to a bare local variable.

[Source: https://vuejs.org/guide/essentials/list.html] Array reactivity has method-specific limitations: only `push`, `pop`, `shift`, `unshift`, `splice`, `sort`, `reverse` are detected as in-place mutations; non-mutating methods (`filter`, `concat`, `slice`) require reassigning the result back to the reactive reference to trigger a view update; direct index assignment (`arr[i] = x`) is likewise not tracked and must go through `splice()` or reassignment instead.

[Source: https://vuejs.org/guide/essentials/list.html] `v-if` and `v-for` cannot be combined on the same template element — this is enforced (produces a compile error in Vue 3) rather than merely discouraged, due to `v-if`'s higher compilation precedence not having access to the `v-for` scope.

[Source: https://vuejs.org/guide/built-ins/suspense.html] `<Suspense>` is explicitly and currently an experimental API ("not guaranteed to reach stable status and the API may change before it does"), with no built-in error-handling path (must be paired with `onErrorCaptured()`/`errorCaptured` on a parent), and does not react to Vue Router's own lazy-loaded route chunks (only genuine async components trigger it).

[Source: https://vuejs.org/guide/scaling-up/ssr.html] SSR has multiple documented hard constraints: only `beforeCreate`/`created` lifecycle hooks run during server rendering (`mounted`/`updated`/`unmounted` do not fire server-side, so DOM-touching side effects must live in `mounted()` only); browser-only globals (`window`, `document`) are unavailable and will error if referenced outside client-only lifecycle hooks; a fresh app (and any associated store) instance must be created per incoming request to avoid cross-request state leakage in a long-lived Node process; `<Teleport>` requires special handling (either client-only conditional rendering, or passing an SSR context object to `renderToString` and manually injecting the teleported markup); SSR requires a Node.js server process and is explicitly not deployable as static files (unlike SSG).

[Source: https://vuejs.org/guide/extras/web-components.html] Vue-authored Web Components (via `defineCustomElement`) cannot support Vue's scoped-slot composition pattern once consumed as opaque custom elements with eager (non-scoped) native slots — named as a fundamental capability gap of the Custom Elements spec itself, not something Vue can work around; a baseline "~16kb" runtime-size cost is cited for shipping a component this way.

[Source: https://vuejs.org/guide/components/registration.html] A locally-registered component is only available inside the component that registers it — it is **not** automatically available to that component's descendants/children (each must import/register it independently, or it must be registered globally).

[Source: https://vuejs.org/api/sfc-script-setup.html] `<script setup>` has structural limitations: it cannot use a `src` attribute to reference an external script file (module-execution semantics conflict); it cannot be used with an in-DOM root component template; and props/emits declared via the compiler macros are hoisted to module scope, so they cannot reference other local variables declared inside `<script setup>`.

[Inference, not confirmed in docs] Vue core itself does not ship first-party list virtualization, and (per the Performance section) the docs point to third-party community libraries for this — meaning very-large-list rendering performance is not something the framework solves out of the box without additional dependencies. This is inferred from the absence of a first-party API in the performance guide's virtualization recommendation, not from an explicit "Vue does not provide X" statement.

---

## 15. Debugging

[Source: https://devtools.vuejs.org/getting-started/features] Official **Vue Devtools** (browser extension + standalone Electron app + Vite plugin, per the Tooling guide) ships: a **Components** tab (interactive component tree with live state inspection/editing, "scroll to component" DOM linking), a **Timeline** tab (records rendering/update performance history over time), a **Router** tab (integrated with vue-router: route list and per-route details) and a related **Pages** tab (current route display/navigation), a **Pinia** tab (store list, per-store state inspection and live editing), an inspector for DOM-tree-to-component-source mapping, a module-relationship graph view, a command palette, and support for switching between/split-viewing multiple app instances on one page. Some features (asset inspection, transform-step inspection, the DOM inspector integration) are explicitly noted as requiring **Vite** specifically.

[Source: https://vuejs.org/guide/scaling-up/tooling.html] Devtools documentation is hosted at its own domain, `devtools.vuejs.org`; distribution channels are the Chrome Web Store extension, a Vite plugin, and a standalone Electron app for non-Chromium/non-browser debugging contexts.

[Source: https://vuejs.org/guide/best-practices/performance.html] For performance-specific debugging, the docs direct developers to Chrome DevTools' native Performance panel (with `app.config.performance = true` enabling Vue-emitted component mount/patch/update markers visible in that panel — development-only) in addition to Vue Devtools' own profiling view.

[Source: https://vuejs.org/api/application.html] Programmatic error/warning interception for debugging or centralized logging is available via `app.config.errorHandler` (uncaught component-lifecycle/render/watcher errors) and `app.config.warnHandler` (intercepts Vue's own development-mode runtime warnings, e.g. missing required props) — both receive the originating `ComponentPublicInstance` and either an `info` string or `trace` string identifying where in the component tree the issue occurred.

[Source: https://vuejs.org/guide/scaling-up/ssr.html] SSR-specific debugging guidance: hydration mismatches are attributed to three documented causes — invalid HTML nesting in the template (browsers silently "fix" malformed nesting during parsing, producing a DOM structure that differs from what Vue expects to hydrate), use of non-deterministic values (e.g. `Math.random()`/timestamps) during server render without special handling (recommended fix: gate the random/non-deterministic part behind `v-if` + `onMounted()` so it only renders client-side, or use a seeded RNG), and timezone-dependent date formatting differing between server and client locale (recommended fix: perform such conversions client-only).

---

## 16. Integration

[Source: https://router.vuejs.org/introduction.html] **Vue Router** is documented as the official, core-team-maintained router, deeply integrated with Vue's own reactivity/component model (nested routes, dynamic route matching, navigation guards, transition-effect integration, HTML5 history or hash-based routing modes); installed into an app via the standard plugin mechanism (`app.use(router)`, per the general plugin API — the fetched intro-page summary did not show the exact snippet, but this follows directly from the documented `app.use()` plugin API in section 3).

[Source: https://pinia.vuejs.org/introduction.html] **Pinia** integrates as a standard Vue plugin as well and is the official state-management recommendation (see Recommended Patterns); works with both Composition API stores and Options-API-style map helpers, and is Devtools-integrated (timeline/time-travel, per the Devtools features list).

[Source: https://vuejs.org/guide/scaling-up/ssr.html] **Nuxt** is named as the recommended higher-level meta-framework for SSR/SSG use cases, handling client/server build coordination, routing, state, and hydration on top of Vue core rather than requiring hand-rolled SSR setup for production apps. **VitePress** is named specifically for SSG/documentation-site use cases.

[Source: https://vuejs.org/guide/typescript/overview.html] **TypeScript** integration is first-class: bundled type declarations, `defineComponent()` for Options API type inference, generic `<script setup lang="ts">` for Composition API, `vue-tsc` for CLI/CI type-checking, and the "Vue - Official" (Volar) VS Code extension (which supersedes the older Vetur extension) providing the language server for template-expression intellisense and prop validation in the editor.

[Source: https://vuejs.org/guide/extras/web-components.html] **Web Components / Custom Elements** integration is bidirectional and officially documented: Vue can consume arbitrary native custom elements (via `compilerOptions.isCustomElement` plus `.prop` binding modifier for forced property-vs-attribute binding) and can author custom elements from Vue components via `defineCustomElement()`; the docs cite a **100% score on the community "Custom Elements Everywhere" compatibility test suite** for Vue's consumption-side interop.

[Source: https://vuejs.org/guide/scaling-up/tooling.html] **Build-tool integration**: Vite is the first-class/recommended build tool (`@vitejs/plugin-vue` for SFC compilation), with Vue CLI (webpack-based) kept only in maintenance mode. **Backend framework integration**: Laravel is named as shipping an official Vite plugin; a generic pointer to Vite's own backend-integration guide is given for other server frameworks (e.g. for classic server-rendered-page + Vite-asset-pipeline setups).

[Source: https://vuejs.org/guide/best-practices/production-deployment.html] **Error-tracking service integration**: Sentry and Bugsnag are named as having official Vue-specific SDK integration guides, wired through `app.config.errorHandler`.

[Source: https://vuejs.org/guide/scaling-up/testing.html] **Testing ecosystem integration**: Vitest (Vite-native), `@vue/test-utils` (official low-level mounting library) and `@testing-library/vue` (community, user-centric mounting library) for unit/component tests; Cypress and Playwright for E2E and (Cypress only, among these two) component testing.

---

## 17. Production Considerations

[Source: https://vuejs.org/guide/best-practices/production-deployment.html] Ship the production build (`.prod.js` CDN builds, or `vue.runtime.esm-bundler.js` + `NODE_ENV=production` + correct compile-time flags under a bundler) to strip dev-only warnings, prop/event runtime validation, and Devtools hooks — all of which add both bundle weight and runtime overhead if left in.

[Source: https://vuejs.org/guide/best-practices/production-deployment.html] Wire `app.config.errorHandler` to a real error-tracking service (Sentry/Bugsnag officially integrated) before going to production, rather than relying on default unhandled-error console output.

[Source: https://vuejs.org/guide/best-practices/performance.html] For load-sensitive production apps, choose SSR/SSG over a pure client-rendered SPA specifically for time-to-content, and isolate static/marketing pages from the main app bundle rather than shipping the whole SPA runtime for content that doesn't need it.

[Source: https://vuejs.org/guide/scaling-up/ssr.html] Production SSR requires planning for **server CPU load** (rendering to string is CPU-intensive at scale) and a **caching strategy**, plus **cross-request state isolation** (fresh app/store instances created per incoming request — a shared/module-level singleton store in a long-lived Node process would leak state between concurrent users' requests) — this is called out as a "critical" consideration, not an edge case.

[Source: https://vuejs.org/guide/best-practices/security.html] Production security posture per the docs: keep Vue and official companion libraries up to date, sanitize all user-provided URLs server-side before persistence (not merely client-side at render time), never mount a Vue app on a DOM node containing a mix of server-rendered and user-supplied markup, and review any third-party component's source before adopting it in a production app (since `v-html`/dangerous patterns inside a dependency are just as exploitable as first-party code).

[Source: https://vuejs.org/guide/best-practices/performance.html] Production monitoring guidance names Core Web Vitals-family metrics specifically: **LCP** (load) and **INP** (interaction responsiveness) as the metrics to track post-deployment, alongside bundle-size and component-instance-count budgets trackable via Devtools during development.

[Source: https://v3-migration.vuejs.org/] For teams maintaining a production Vue 2 app: since Vue 2 reached end of support Dec 31 2023, the only officially documented forward path is migrating to Vue 3 (optionally staged via the Migration Build) — the docs do not describe any ongoing official security-patch channel for Vue 2 in production past that date, and this research pass did not find one referenced from vuejs.org itself (see the Unresolved note on third-party extended support in Version Information).

---

## Summary of Citation Sources

| URL | Covers |
|---|---|
| https://vuejs.org/guide/introduction.html | Core concepts, API styles, framework philosophy |
| https://vuejs.org/guide/reusability/composables.html | Composables pattern, reactivity best practices |
| https://vuejs.org/guide/extras/composition-api-faq.html | Composition vs Options API rationale/tradeoffs |
| https://vuejs.org/guide/extras/rendering-mechanism.html | VDOM/compiler architecture, patch flags, blocks |
| https://vuejs.org/guide/extras/reactivity-in-depth.html | Reactivity architecture, Proxy vs defineProperty, limitations |
| https://vuejs.org/guide/best-practices/security.html | Security guidance (XSS, v-html, URL/style/JS injection, CSRF) |
| https://vuejs.org/guide/best-practices/performance.html | Performance guidance, profiling, computed 3.4+ behavior |
| https://vuejs.org/guide/scaling-up/testing.html | Testing tools and patterns |
| https://vuejs.org/guide/best-practices/production-deployment.html | Deployment/production build guidance |
| https://vuejs.org/guide/scaling-up/ssr.html | SSR architecture, limitations, production considerations |
| https://vuejs.org/guide/typescript/overview.html | TypeScript integration/configuration |
| https://vuejs.org/api/sfc-script-setup.html | `<script setup>` compiler macros, version-gated features |
| https://vuejs.org/api/application.html | Application API (`createApp`, `app.config`, etc.) |
| https://vuejs.org/guide/components/async.html | Async components, lazy hydration (3.5+) |
| https://vuejs.org/guide/built-ins/suspense.html | Suspense (experimental status, API, limitations) |
| https://vuejs.org/guide/essentials/list.html | List rendering caveats/anti-patterns |
| https://vuejs.org/guide/components/registration.html | Component registration patterns |
| https://vuejs.org/guide/reusability/plugins.html | Plugin architecture, globalProperties anti-pattern |
| https://vuejs.org/style-guide/ | Style guide priority tiers |
| https://vuejs.org/style-guide/rules-use-with-caution | Documented anti-patterns (Priority D) |
| https://vuejs.org/guide/scaling-up/state-management.html | State management guidance, Pinia recommendation |
| https://vuejs.org/guide/scaling-up/tooling.html | Tooling: scaffolding, IDE, devtools, linting, testing |
| https://vuejs.org/guide/extras/web-components.html | Web Components integration, defineCustomElement |
| https://vuejs.org/about/releases | Release cadence, semver policy, pre-release channels |
| https://v3-migration.vuejs.org/ | Vue 2→3 migration guide overview, Migration Build |
| https://v3-migration.vuejs.org/breaking-changes/ | Full Vue 2→3 breaking-changes catalogue |
| https://github.com/vuejs/core/releases | Recent release history/dates |
| https://github.com/vuejs/core/releases/tag/v3.6.0-rc.1 | Vapor Mode details, 3.6 status |
| https://registry.npmjs.org/vue | npm dist-tags (latest/rc/beta/alpha/legacy/csp versions) |
| https://devtools.vuejs.org/getting-started/features | Vue Devtools feature set |
| https://router.vuejs.org/introduction.html | Vue Router official status |
| https://pinia.vuejs.org/introduction.html | Pinia official status |

**Total distinct official source URLs cited: 32.**
