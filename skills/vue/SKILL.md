---
name: Vue
description: >-
  Vue-specific implementation: Composition API vs. Options API, SFC mechanics
  (`<script setup>` compiler macros), Proxy-based reactivity (v3) vs.
  Object.defineProperty (v2, EOL 2023-12-31), Pinia, Vue Router, and the
  pre-stable Vapor Mode (3.6 line). Use when vue/@vue, a .vue SFC,
  @vitejs/plugin-vue, Vue Router, or Pinia is present, or the task names Vue.
  Not for React/Angular, generic framework selection, or the SSR/SSG
  rendering-mode decision (frontend-architecture/rendering-strategy).
spec_version: "1.0"
---

## Purpose & scope

Apply Vue correctly and version-appropriately: the Composition API, SFC
mechanics, Proxy-based reactivity, and the Vue 2 (EOL) → Vue 3 split. The
generic framework-selection method and the React/Vue/Angular comparison
(reactivity model, XSS auto-escaping, compiler story, test runner) belong to
[frontend-architecture](../frontend-architecture/SKILL.md) (`SK-FE-001`) and
are not repeated here. The SSR/SSG rendering-mode decision belongs to
rendering-strategy (`SK-FE-005`, not yet authored). Nuxt-specific
meta-framework concerns belong to the Nuxt technology skill (`SK-TECH-nuxt`).

## When to use / When not to use

**Use** when `vue`/`@vue/*`, a `.vue` SFC, `@vitejs/plugin-vue`, Vue Router,
or Pinia is present, or the task names Vue, the Composition API, `<script
setup>`, Pinia, Vue Router, or Vapor Mode specifically. **Do not use** for
React or Angular (route to that technology skill), for a still-open framework
choice (`frontend-architecture`), for the SSR/SSG rendering-mode decision on
its own (`rendering-strategy`), or for Nuxt-specific concerns with no Vue-core
question (`SK-TECH-nuxt`).

## Knowledge

**Two API styles, one recommendation for real applications.** The Options
API organizes a component as an object (`data`, `methods`, `mounted`); the
Composition API uses imported functions (`ref()`, `onMounted()`) inside
`setup()` or `<script setup>` [Source:
https://vuejs.org/guide/introduction.html]. The docs do not deprecate the
Options API — it remains valid for low-to-medium complexity components — but
recommend Composition API + SFCs "for building full applications" [Source:
https://vuejs.org/guide/introduction.html]. The Composition API exists for
four stated reasons: logic reuse via composables (replacing mixins), more
flexible code organization by concern, better TypeScript inference, and
smaller/more minification-friendly bundles [Source:
https://vuejs.org/guide/extras/composition-api-faq.html].

**Composables are the reusable-stateful-logic unit.** A composable is a
function that "leverages Vue's Composition API to encapsulate and reuse
stateful logic," conventionally `use`-prefixed. It must be called
synchronously inside `<script setup>`, `setup()`, or another
composable/lifecycle hook (the one exception being after a top-level `await`
in `<script setup>`) so Vue can associate its lifecycle hooks and injections
with the right component instance; each calling component instance gets an
isolated copy of the composable's state [Source:
https://vuejs.org/guide/reusability/composables.html]. `toValue()` normalizes
a `ref`, getter function, or plain value into a plain value, so composables
can accept flexible input types [Source:
https://vuejs.org/guide/reusability/composables.html].

**SFC mechanics.** The recommended production authoring format is the
Single-File Component (a `*.vue` file bundling `<template>`, `<script>`, and
`<style>`), compiled by Vite [Source:
https://vuejs.org/guide/scaling-up/tooling.html]. `<script setup>` is closed/
private by default — nothing is exposed to a parent `template ref` unless
explicitly passed to `defineExpose({...})` — and has structural limits: no
`src` attribute referencing an external script file, unusable with an in-DOM
root template, and props/emits declared via compiler macros are hoisted to
module scope so they cannot reference other local `<script setup>` variables
[Source: https://vuejs.org/api/sfc-script-setup.html]. The compiler-macro
surface is version-gated: `defineProps()`/`defineEmits()` and
`defineExpose({...})` are baseline; `defineOptions({...})` and
`defineSlots<{...}>()` shipped at **3.3**; `defineModel()` (two-way-bindable
prop returning a ref whose writes auto-emit `update:<name>`) at **3.4**;
Reactive Props Destructure (destructuring `defineProps()`'s return while
retaining reactivity) at **3.5** [Source:
https://vuejs.org/api/sfc-script-setup.html]. Full macro/version table and
the Vue 2→3 breaking-change catalogue are in
[references/sfc-macros-and-version-split.md](references/sfc-macros-and-version-split.md).

**The v2/v3 reactivity split is architectural, not cosmetic.** Vue 2's
reactivity used `Object.defineProperty()` getter/setters exclusively, "due to
browser support limitations" on `Proxy`; Vue 3's `reactive()` uses a native ES
`Proxy` [Source: https://vuejs.org/guide/extras/reactivity-in-depth.html].
This is a core architectural difference between the majors, per the docs' own
comparison — not merely a renamed API. In v3, `track()`/`trigger()` intercept
property access via the Proxy to record and re-run reactive effects, stored in
a `WeakMap<target, Map<key, Set<effect>>>` [Source:
https://vuejs.org/guide/extras/reactivity-in-depth.html]. Destructuring a
`reactive()` object breaks reactivity for the destructured binding, and
`reactive(obj) !== obj` (different object identity) — both are documented
ergonomic limitations of the Proxy-based model, not bugs [Source:
https://vuejs.org/guide/extras/reactivity-in-depth.html]. **Vue 2 reached end
of support on 2023-12-31**: no new features, fixes, or security patches from
the core team; `2.7.16` is the final published Vue 2 line [Source:
https://vuejs.org/guide/introduction.html; VERSION-SENSITIVE: Vue 2.x, all].
Vue does not document any official extended-support channel for Vue 2 past
that date. Treat any Vue 2 codebase as unsupported and steer toward migration
rather than new Vue-2-specific work.

**Compiler-Informed Virtual DOM.** The template compiler and runtime are
tightly coupled, so the compiler embeds optimization hints into generated
render code: static subtrees are hoisted (Cache Static); dynamic vnodes carry
bitwise Patch Flags so the patcher skips full prop diffing; dynamic
descendants are flattened into per-block arrays (Tree Flattening) so static
subtrees are skipped entirely [Source:
https://vuejs.org/guide/extras/rendering-mechanism.html]. These same
optimizations accelerate SSR hydration — described as "partial hydration at
the template level" [Source:
https://vuejs.org/guide/extras/rendering-mechanism.html].

**Vapor Mode exists but is not yet stable.** As of the research date, npm's
`latest` dist-tag for `vue` resolves to **3.5.42**; **3.6.0 is at
release-candidate stage** (`3.6.0-rc.7`) [Source:
https://registry.npmjs.org/vue]. Vapor Mode — an opt-in per-SFC compilation
mode (`<script setup vapor>`) that compiles directly to fine-grained DOM
update instructions, bypassing the Virtual DOM entirely — ships in the 3.6
line. The official 3.6.0-rc.1 release notes describe it as "feature-complete"
but still recommend it only for partial adoption or small new apps, not
full-scale production use [Source:
https://github.com/vuejs/core/releases/tag/v3.6.0-rc.1]. Some secondary
sources (not vuejs.org) describe it as "confirmed stable" by Evan You — that
claim is **not corroborated** by the official npm channel or release notes as
of this research date [Source: research/technologies/vue.md §12,
VERSION-SENSITIVE: 3.6.0-rc line only]. Do not treat Vapor Mode as
production-ready without re-checking the live `latest`/`rc` npm dist-tags at
time of use.

## Decision framework

This extends `frontend-architecture`'s framework-selection framework
(`SK-FE-001`) with Vue-specific calls once Vue is the chosen framework; it
does not re-litigate the React/Vue/Angular comparison itself.

1. **Options API vs. Composition API for this codebase?** Default to
   Composition API + `<script setup>` for a new, non-trivial application —
   it's the officially recommended production pattern [Source:
   https://vuejs.org/guide/introduction.html]. Options API remains a
   defensible choice for a low-complexity component or an existing
   Options-API codebase; don't force a rewrite without a concrete reuse or
   TypeScript-inference need driving it. The two can be mixed via `setup()`
   inside an Options API component when adopting a Composition-API-based
   library feature incrementally [Source:
   https://vuejs.org/guide/extras/composition-api-faq.html].
2. **Pinia vs. Vuex/other state management?** For anything beyond a small
   `reactive()` module export, Pinia is the official recommendation for Vue
   3 — stronger TypeScript inference, Composition-API-style API, Devtools
   time-travel/timeline, HMR, and SSR support [Source:
   https://vuejs.org/guide/scaling-up/state-management.html]. Vuex is
   maintenance-mode; keep an existing Vuex store rather than forcing a
   rewrite, but don't start a new store on it. Pinia dropped Vue 2 support in
   2025 [Source: https://pinia.vuejs.org/introduction.html,
   VERSION-SENSITIVE], so a Vue 2 project needing a new store has no current
   first-party Pinia path — evaluate Vuex or the migration path instead.
3. **Adopt Vapor Mode now?** Not for an existing production app or anything
   beyond a small greenfield project, given its RC status and the explicit
   "not for full-scale production use" guidance in the 3.6.0-rc.1 release
   notes [Source: https://github.com/vuejs/core/releases/tag/v3.6.0-rc.1].
   Reasonable to trial in an isolated, non-critical SFC once a project is
   already on the 3.6 pre-release channel and the team accepts RC risk;
   unreasonable as a default for anything shipping to users now.
4. **Simplest first (anti-overengineering):** most component-scope reactivity
   needs are met by `ref()`/`reactive()`/`computed()` directly — reach for a
   composable only when logic is genuinely reused across components, and for
   Pinia only when state genuinely needs to be shared beyond a
   parent/child prop-and-emit chain.

## Workflow

1. Determine the installed Vue major/minor (`package.json`/lockfile) —
   Vue 2 (EOL), a specific Vue 3.x minor, or a 3.6 pre-release line. Never
   assume "latest" silently.
2. If Vue 2, flag its EOL status explicitly before doing new feature work;
   default to scoping a migration rather than extending Vue-2-only patterns.
3. Choose Options vs. Composition API per the decision framework above,
   consistent with the existing codebase unless a rewrite was requested.
4. Author the SFC/composable, using only compiler macros valid at the
   confirmed minor (see the version-gate table above and in
   [references/sfc-macros-and-version-split.md](references/sfc-macros-and-version-split.md)).
5. Wire state (Pinia) and routing (Vue Router) per the decision framework.
6. Verify per the checks below before declaring done.

## Engineering rules

- Confirm the installed Vue major before writing or trusting any
  version-sensitive API (Proxy-based reactivity assumptions, `<script
  setup>` macros, Lazy Hydration, `computed()`'s 3.4+ change-detection
  behavior).
- Never bind `v-html` to user-provided content — see Security.
- Prefer local component registration over global; it's tree-shakeable and
  keeps dependencies traceable, reserving global registration for pervasive
  base primitives [Source: https://vuejs.org/guide/components/registration.html].
- Use `provide`/`inject` over `app.config.globalProperties` for cross-cutting
  app-wide state — the docs warn global properties "can quickly become
  confusing if too many ... injected by different plugins" [Source:
  https://vuejs.org/guide/reusability/plugins.html].
- Don't destructure a `reactive()` object and expect the destructured
  bindings to stay reactive; use `toRefs()`/`ref()` or keep the object intact
  [Source: https://vuejs.org/guide/extras/reactivity-in-depth.html].
- Don't combine `v-if` and `v-for` on the same element — it's a Vue 3
  compile error, not merely discouraged; pre-filter with a `computed()` or
  split across a wrapping `<template>` [Source:
  https://vuejs.org/guide/essentials/list.html].

## Trade-offs

Composition API buys logic reuse, TS inference, and smaller bundles at the
cost of more indirection for simple components — Options API stays more
approachable for those. Pinia's stronger DX/TS story over Vuex costs nothing
for new Vue 3 code, but it isn't a drop-in for an existing Vue 2 app since
Vue 2 support was dropped in 2025. Vapor Mode's bypass-the-VDOM performance
story is real per the release notes, but adopting it pre-GA trades stability
and Options-API/`getCurrentInstance()`/`v-memo` compatibility for that
upside — a cost most production codebases shouldn't pay yet.

## Anti-patterns

- **Treating Vapor Mode as production-ready** because a secondary source
  called it "confirmed stable" — the official npm `latest` tag and the
  3.6.0-rc.1 release notes themselves say otherwise as of the research date
  [Source: https://registry.npmjs.org/vue;
  https://github.com/vuejs/core/releases/tag/v3.6.0-rc.1]. Re-verify the live
  dist-tags before trusting either claim.
- **Copying `<script setup>` macro examples (`defineModel()`,
  `defineSlots()`, Reactive Props Destructure) into a codebase pinned to an
  earlier 3.x minor** than the macro's introduction version — code will not
  run [Source: https://vuejs.org/api/sfc-script-setup.html].
- **Assuming Vue 2 reactivity/API behavior applies to Vue 3 code, or vice
  versa** — the Proxy-vs-`defineProperty` split and the full breaking-change
  catalogue (removed `filters`, `$children`, `$set`/`$delete`, reworked
  `v-model`, etc.) mean copy-pasted snippets across the major-version
  boundary are a common, avoidable source of bugs [Source:
  https://v3-migration.vuejs.org/breaking-changes/].
- **Directly mutating an array by index or via non-mutating methods
  (`filter()`, `slice()`) in place** and expecting the view to update — only
  `push`/`pop`/`shift`/`unshift`/`splice`/`sort`/`reverse` are tracked as
  in-place mutations [Source: https://vuejs.org/guide/essentials/list.html].
- **Global state for everything via `app.config.globalProperties` or a
  Pinia store "just in case"** — the domain's overengineering trap; most
  state should stay local or lifted only as far as actual sharing requires
  (this mirrors `frontend-architecture`'s general anti-pattern, applied to
  Vue's specific mechanisms).

## Security

Vue **automatically HTML-escapes** text interpolations (`{{ }}`) and dynamic
attribute bindings — the framework's default XSS mitigation, requiring no
developer action [Source: https://vuejs.org/guide/best-practices/security.html].
`v-html` (and raw `innerHTML`) is the **explicit, documented bypass**: "only
use `v-html` on trusted content and never on user-provided content," with the
caveat that even "trusted" user content is never fully safe unless sandboxed
in an iframe or shown only to its author [Source:
https://vuejs.org/guide/best-practices/security.html]. User-provided URLs
bound via `:href` must be sanitized **on the backend before persistence**,
not only client-side — the docs' stated reason is protecting every client
(web, mobile, etc.), with `@braintree/sanitize-url` named as a client-side
supplement, not a substitute [Source:
https://vuejs.org/guide/best-practices/security.html]. Vue explicitly
prevents rendering literal `<style>` tags from interpolated user content
(clickjacking-via-CSS mitigation); the safe pattern for user-influenced
styling is the object syntax for `:style` with an explicit property
whitelist, never a raw user-controlled CSS string [Source:
https://vuejs.org/guide/best-practices/security.html]. Never bind
user-provided strings to event-handler attributes (`:onclick="userCode"`) —
called out as equally unsafe as unsanitized `v-html` [Source:
https://vuejs.org/guide/best-practices/security.html]. Compiling untrusted
strings as a component's `template` is equated directly with arbitrary code
execution: "no practical way for Vue to completely shield against malicious
code execution" in that scenario [Source:
https://vuejs.org/guide/best-practices/security.html]. CSRF/XSSI is framed as
a backend responsibility, not something Vue itself addresses [Source:
https://vuejs.org/guide/best-practices/security.html]. Full cross-cutting
threat modeling is owned by `SK-QA-002`, not restated here.

## Performance

Compiler-informed VDOM optimizations (Cache Static, Patch Flags, Tree
Flattening) apply automatically — no developer action needed [Source:
https://vuejs.org/guide/extras/rendering-mechanism.html]. Manual update-perf
levers: keep child `props` stable by computing derived booleans in the
parent rather than passing a whole object plus a comparison key; `v-once`
for permanently-static content; `v-memo="[deps]"` to skip re-render of large
`v-for` subtrees when a dependency array is unchanged; as of **Vue 3.4**,
`computed()` only re-triggers dependents when its return value actually
changed, not on every re-evaluation — a within-major behavioral shift not
cataloged on the formal breaking-changes page, worth flagging since code
relying on unconditional re-triggering can observe different behavior after
upgrading past 3.4 [Source:
https://vuejs.org/guide/best-practices/performance.html;
VERSION-SENSITIVE: >=3.4]. **Lazy Hydration** (3.5+) —
`hydrateOnIdle()`/`hydrateOnVisible()`/`hydrateOnMediaQuery()`/
`hydrateOnInteraction()`/a custom `HydrationStrategy` passed to
`defineAsyncComponent`'s `hydrate` option — defers making an SSR-rendered
async component interactive until the chosen trigger fires [Source:
https://vuejs.org/guide/components/async.html; VERSION-SENSITIVE: >=3.5].
Use `shallowRef()`/`shallowReactive()` for large, effectively-immutable data
to avoid deep-reactivity overhead, with the caveat that in-place nested
mutation then stops being reactive [Source:
https://vuejs.org/guide/best-practices/performance.html]. Vue ships no
first-party list virtualization; community libraries (`vue-virtual-scroller`
etc.) are the documented path for 1000+-item lists [Source:
https://vuejs.org/guide/best-practices/performance.html]. Deeper cross-cutting
performance method is owned by `SK-QA-003`.

## Testing

Vue **recommends Vitest**, "created and maintained by members of the Vue /
Vite team," for unit testing [Source:
https://vuejs.org/guide/scaling-up/testing.html]. Concrete setup: `npm
install -D vitest happy-dom @testing-library/vue`, with `test: { globals:
true, environment: 'happy-dom' }` added to `vite.config.js` and a `"test":
"vitest"` script — reusing the app's own Vite config rather than a separate
test-runner config file [Source:
https://vuejs.org/guide/scaling-up/testing.html]. Component testing adds
`@vue/test-utils` (official, low-level mounting) for a fast Node-based
approach, or Cypress Component Testing for a real-browser approach that also
catches style/layout issues; `@testing-library/vue` is the alternative,
user-centric mounting library [Source:
https://vuejs.org/guide/scaling-up/testing.html]. E2E: Playwright or
Cypress, not prescribed as a single default [Source:
https://vuejs.org/guide/scaling-up/testing.html]. Composables using
lifecycle hooks or `provide`/`inject` need a `withSetup()` test helper that
invokes the composable inside a throwaway `createApp({ setup() {...}
}).mount(...)`, then explicitly `app.unmount()`s afterward — a
composable-specific pattern beyond generic component testing [Source:
https://vuejs.org/guide/scaling-up/testing.html]. Assert on a component's
public interface (rendered output, reaction to props/slots/interaction), not
private state; mock as little as possible; don't rely solely on snapshots
[Source: https://vuejs.org/guide/scaling-up/testing.html]. Deep test-strategy
method is owned by `SK-QA-001`.

## Failure handling

- If the installed Vue major (2.x vs. 3.x) cannot be determined, ask rather
  than assume Vue 3/"latest" — applying Vue 3-only reactivity or `<script
  setup>` macros to a Vue 2 project produces code that won't run.
- If a Vue 2 codebase is detected, state its EOL status explicitly rather
  than silently proceeding as if it received ongoing support.
- If shell is unavailable, produce advisory component/composable/store code
  and state plainly that it was not run, built, or type-checked (`vue-tsc`).

## Escalation

- Adopting Vapor Mode, or any other 3.6 pre-release feature, for a
  production codebase is a stability trade-off that requires explicit user
  confirmation before proceeding — it is not applied as a silent default.
- A Vue-2-to-Vue-3 migration for an existing production app is a
  significant, hard-to-reverse effort; scope and confirm with the user
  rather than starting it unprompted (defers to `frontend-architecture`'s
  framework-switch escalation discipline where relevant).

## Outputs & verification

- **Outputs:** version-line-correct SFC/component or composable code, a
  Pinia store or Vue Router config, or an analysis of which v2-vs-v3/Vapor
  Mode caveats apply.
- **Verify:** every version-gated compiler macro matches the confirmed Vue 3
  minor; any Vapor Mode usage is flagged as pre-stable; reactivity claims
  correctly attribute Proxy (v3) vs. `Object.defineProperty` (v2); any
  `v-html` usage is checked against the never-on-user-content rule.

## References

- [references/sfc-macros-and-version-split.md](references/sfc-macros-and-version-split.md) — Tier-2: full `<script setup>` compiler-macro version table, the Vue 2→3 breaking-change catalogue, and Vapor Mode's documented incompatibility scope.
- Source list: see `skill.yaml.source_references` (vuejs.org, v3-migration.vuejs.org, router.vuejs.org, pinia.vuejs.org, npm registry, and GitHub releases, retrieved 2026-09-10, via `research/technologies/vue.md`).
- [frontend-architecture/references/framework-comparison.md](../frontend-architecture/references/framework-comparison.md) — owns the React-vs-Vue-vs-Angular comparison; not restated here.
