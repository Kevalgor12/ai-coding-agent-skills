# SFC compiler macros, the Vue 2→3 breaking-change catalogue, and Vapor Mode's scope (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Grounded in
[research/technologies/vue.md](../../../research/technologies/vue.md) — every
claim below traces to an official source cited there. Citation convention
matches the source doc: `[Source: <url>]` for documented facts,
`[VERSION-SENSITIVE: <range>]` for claims that hold only for a version range.

## `<script setup>` compiler-macro version table

| Macro | Purpose | Introduced | Notes |
|---|---|---|---|
| `defineProps()` | Declare props with type inference | Baseline | Runtime-object form and (3.3+) type-only generic form; not both in the same block [Source: https://vuejs.org/api/sfc-script-setup.html] |
| `defineEmits()` | Declare emits with type inference | Baseline | Same runtime-object/type-only-generic split as `defineProps()` [Source: https://vuejs.org/api/sfc-script-setup.html] |
| `defineExpose({...})` | Explicitly expose bindings to parent `template ref` access | Baseline | `<script setup>` components are closed/private by default; nothing is exposed without this [Source: https://vuejs.org/api/sfc-script-setup.html] |
| `useSlots()` / `useAttrs()` | Programmatic slots/attrs access | Baseline | Equivalent to `this.$slots`/`this.$attrs` in Options API [Source: https://vuejs.org/api/sfc-script-setup.html] |
| `defineOptions({...})` | Declare non-prop/emit component options (e.g. `inheritAttrs`) inside `<script setup>` | **3.3** | [VERSION-SENSITIVE: >=3.3] [Source: https://vuejs.org/api/sfc-script-setup.html] |
| `defineSlots<{...}>()` | Type-hints for slots | **3.3** | [VERSION-SENSITIVE: >=3.3] [Source: https://vuejs.org/api/sfc-script-setup.html] |
| `defineModel()` | Declare a two-way-bindable prop for `v-model`, returning a ref whose writes auto-emit `update:<name>` | **3.4** | Supports a modifiers/transform form [VERSION-SENSITIVE: >=3.4] [Source: https://vuejs.org/api/sfc-script-setup.html] |
| Reactive Props Destructure | Destructuring `defineProps()`'s return value while retaining reactivity (Vue auto-transforms bare destructured bindings into `props.x` access) | **3.5** | [VERSION-SENSITIVE: >=3.5] [Source: https://vuejs.org/api/sfc-script-setup.html] |

Code using a macro from a later row than the project's pinned Vue 3 minor
will not compile/run. Always confirm the installed minor before assuming a
macro is available.

## Vue 2 → Vue 3 breaking-change catalogue (summary)

Full source: [Source: https://v3-migration.vuejs.org/breaking-changes/].
[VERSION-SENSITIVE: applies to upgrading a Vue-2-authored codebase only; does
not describe any breaking change within the Vue 3.x line, which is a
separate, much smaller category — see the `computed()` 3.4 note in
[SKILL.md](../SKILL.md#performance).]

- **Global API**: moved from a global `Vue` object to a per-`createApp()`
  application instance; global/internal APIs restructured to be tree-shakable.
- **Template directives**: `v-model` component usage reworked, replacing the
  old `.sync` modifier; `key` usage on `<template v-for>`/non-`v-for` nodes
  changed; `v-if`/`v-for` precedence on the same element changed (and is now
  a compile error, not just a precedence quirk — see
  [SKILL.md](../SKILL.md#anti-patterns)); `v-bind="object"` became
  order-sensitive; the `v-on:event.native` modifier was removed.
- **Components**: functional components must now be plain functions; async
  components require `defineAsyncComponent`; component custom events must be
  declared via the `emits` option.
- **Render function**: API updated; `$scopedSlots` removed (all slots now
  exposed as functions via `$slots`); `$listeners` removed/merged into
  `$attrs`; `$attrs` now includes `class`/`style`.
- **Custom elements**: custom-element resolution now happens at
  template-compile time; `<component>` reserved for `is`-attribute usage.
- **Lifecycle & other**: `destroyed` → `unmounted`, `beforeDestroy` →
  `beforeUnmount`; prop `default` factory functions lose access to `this`;
  custom directive hook API realigned to component lifecycle naming; `data`
  must be a function even on the root instance; transition class names
  changed; array watchers require an explicit `deep: true` to catch in-place
  mutation; a mounted app no longer replaces its target DOM element outright.
- **Removed APIs**: `keyCode` modifiers for `v-on`; the `$on`/`$off`/`$once`
  instance event-emitter methods; filters (the `{{ value | filter }}`
  template syntax); inline-template attributes; `$children`; the
  `propsData` app-creation option; `$destroy()`; the global/instance
  `Vue.set`/`Vue.delete`/`$set`/`$delete` reactivity-caveat-workaround APIs
  (superseded because Proxy-based reactivity no longer needs them).

A dedicated **Migration Build** exists to ease incremental upgrades of
existing Vue 2 codebases (and to give library authors a compatibility
bridge) rather than requiring an all-at-once rewrite [Source:
https://v3-migration.vuejs.org/]. No Vue 3→4 breaking-changes page exists,
since no Vue 4 has been announced as of the research date.

## Vapor Mode's documented incompatibility scope

[Source: https://github.com/vuejs/core/releases/tag/v3.6.0-rc.1]
[VERSION-SENSITIVE: Vue 3.6.0-rc line only, opt-in scope only, not yet
stable — see [SKILL.md](../SKILL.md#knowledge) for the stability caveat.]

Vapor Mode is an opt-in per-SFC compilation mode (`<script setup vapor>` /
`<script vapor>` / `<template vapor>`) that compiles directly to
fine-grained DOM update instructions instead of going through the Virtual
DOM, requires `<script setup>` syntax, and reuses the same underlying
reactivity primitives as standard Vue 3. Within that opt-in scope only,
Vapor components do **not** support:

- The Options API
- Global properties (`app.config.globalProperties`)
- `@vue:xxx` lifecycle DOM events
- `getCurrentInstance()`
- `v-memo`
- Template refs exposing `$el`/`$props`/etc.

Additional documented behavioral differences scoped to Vapor components:

- Event handling uses **document-level event delegation**, meaning
  `stopPropagation()` inside a Vapor handler can prevent *other* delegated
  handlers elsewhere in the document from firing — a documented behavioral
  difference from standard VDOM-mode event handling.
- Calling `slots.default()` in Vapor mode actually **executes** render
  logic rather than being inspectable as a dry run.
- Custom directives use a different interface (reactive getters) in Vapor
  mode.

Standard VDOM-mode Vue 3 components are explicitly stated to be unaffected
by any of the above — the incompatibilities apply only to components that
explicitly opt in via the `vapor` markers.

## Unresolved

- **Vue Router v5.x**: the Vue Router intro page references "v4.x and v5.x"
  as current, plus v3.x for older Vue versions, but the primary research
  pass for this skill only retrieved an AI-summarized extraction of that
  page, not the raw version-support table. **Unresolved: the
  existence/status of a Vue Router v5 should be re-verified directly
  against `router.vuejs.org` before being cited as fact** [Source:
  research/technologies/vue.md §3, Unresolved note].
- **`vue` CSP-build dist-tag** (`csp` → `1.0.28-csp` per npm metadata): what
  this build specifically changes (e.g. avoiding `new Function()` for CSP
  `unsafe-eval` compliance) was not documented on the vuejs.org guide pages
  fetched in the primary research pass — flagged for follow-up rather than
  guessed [Source: https://registry.npmjs.org/vue].
