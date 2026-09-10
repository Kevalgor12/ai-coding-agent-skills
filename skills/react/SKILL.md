---
name: React
description: >-
  React-specific hooks API, component composition, reconciliation, and React
  Server Components mechanics (RSC, "use client"/"use server", Server
  Functions). Use when the stack is React (react/react-dom in package.json,
  JSX/TSX files, or a React-based meta-framework). Not for the React vs. Vue
  vs. Angular choice (frontend-architecture) or Next.js-specific
  routing/caching (SK-TECH-nextjs).
spec_version: "1.0"
---

## Purpose & scope

Apply React correctly and version-appropriately: the hooks API, component
composition, reconciliation, and React Server Components mechanics, for the
React version actually in use. The generic component/state-management
*method* comes from the parent skill,
[frontend-architecture](../frontend-architecture/SKILL.md) (`SK-FE-001`,
already authored) — this skill supplies React's concrete API and behavior.
The broader SSR/SSG/CSR rendering-mode decision is owned by `SK-FE-005`
(rendering-strategy, a forward reference — not yet authored in this library);
this skill covers the RSC Server/Client Component split once RSC is already
in scope, not the general rendering-mode choice. The React-vs-Vue-vs-Angular
framework comparison itself is owned by `SK-FE-001` and is not repeated here.

## When to use / When not to use

**Use** when `react`/`react-dom` are dependencies, JSX/TSX files are present,
or the task names a React-specific API or concept (hooks, Server Components,
`"use client"`/`"use server"`, the React Compiler, reconciliation). **Do not
use** when the framework choice is still open (route to `SK-FE-001`), when
the stack is Vue or Angular (route to `SK-TECH-vue`/`SK-TECH-angular`), for
Next.js-specific routing/caching/App Router mechanics with no underlying
React question (route to `SK-TECH-nextjs`), or for generic component/state
structure independent of React's own API (route to `SK-FE-001`).

## Knowledge

**Component model.** A component is a JavaScript function whose name must
start with a capital letter — the mechanism JSX uses to distinguish a custom
component from a built-in HTML tag — returning JSX, which is stricter than
HTML (all tags explicitly closed, one top-level parent per return)
[Source: react.dev/learn]. Props pass data down; **state** is local,
per-component memory created with `useState`. Critically, React associates
state with a component's **position in the render tree**, not the component
instance conceptually — the same component type re-rendered at the same tree
position keeps its state, and a different type/key at that position destroys
and recreates it. The `key` prop is the documented mechanism to override this:
give a component explicit identity independent of position (e.g.
`<Chat key={to.id} contact={to} />` to reset state per recipient), or force
distinct list items to keep independent state as a list reorders
[Source: react.dev/learn/preserving-and-resetting-state]. **"Thinking in
React"** is the documented five-step architectural methodology: decompose the
UI into components, build a static version from props only, find the
minimal-but-complete state (nothing that's derivable from props/other state
is state), lift each piece of state to the closest common parent (one-way
data flow), then add inverse data flow via callback props
[Source: react.dev/learn/thinking-in-react].

**Hooks model.** Hooks are functions whose names start with `use` that let
function components tap into state, lifecycle-like behavior, context, and
refs. The **Rules of React** (treated by the React team as mandatory, not
style guidelines — violations cause bugs, enforced via Strict Mode and
`eslint-plugin-react-hooks`) are three groups: (1) components and Hooks must
be **pure** — idempotent, side effects only in an Effect or event handler
(never during render), props/state/Hook return values treated as immutable
snapshots; (2) **React calls Components and Hooks** — never call a component
as a plain function (`MyComponent()`) or pass a Hook around as a value; (3)
**Rules of Hooks** — Hooks are called only at the **top level**, never inside
loops, conditionals, nested functions, or after an early return, and only
from function components or custom Hooks (name must start with `use`)
[Source: react.dev/reference/rules].

**Reconciliation and the update model.** React's documented update model has
three phases: **Trigger** (initial `createRoot().render()` or a state `set`
call), **Render** (React calls component functions, recursively, to
determine output — this must be pure, and Strict Mode double-invokes
component bodies/initializers in development specifically to surface
impurities), and **Commit** (React applies the minimal DOM diff — on
re-renders it only touches nodes whose render output actually changed, e.g.
leaving a live `<input>` value untouched)
[Source: react.dev/learn/render-and-commit]. Reconciliation itself is
position-in-tree-based: for each tree position, React compares the previous
and new element type (and `key`) — same type/key → the instance and its
state are reused; different type, different key, or removal → destroyed and
recreated [Source: react.dev/learn/preserving-and-resetting-state].
**Unresolved:** whether current react.dev docs use the term "Fiber" anywhere
for the internal reconciler architecture — not found in the research pass;
treat any "Fiber" claim as outside official-docs grounding.

**React Server Components (RSC).** Per the docs, RSC is "a fundamental shift
in React's rendering architecture, treating servers and clients as equal
partners in component rendering." Server Components execute ahead of time in
a separate server environment — at build time (producing static content, no
runtime server needed) or at request time (per-request dynamic rendering) —
and are distinct from traditional SSR because they never ship their own
component code to the client. They compose with **Client Components**
(marked `"use client"`) to add interactivity: the client receives only the
already-rendered output of Server Components as props passed into Client
Components, not the Server Components' source. `"use server"` marks **Server
Functions** (not Server Components) — callable async functions invoked from
Client Components [Source: react.dev/reference/rsc/server-components].
**Version-sensitive:** RSC as an application-facing feature is semver-stable
across React 19.x minors, but the underlying bundler/framework-integration
APIs (`react-server-dom-webpack`/`-parcel`/`-turbopack`) explicitly do
**not** follow semver and may break between minors — framework authors are
told to pin an exact React version for that integration layer
[Source: react.dev/reference/rsc/server-components] (applies_to: RSC
integration layer, all 19.x).

**React 19 additions** (applies_to: `>=19.0`): Actions/`useActionState`
(returns `[data, submitAction, isPending]`, replacing `useFormState`);
`useFormStatus` (reads the nearest parent `<form>`'s pending/data/method
without prop drilling); `useOptimistic` (optimistic value during an in-flight
async action, auto-reverting); `use()` (reads a Promise or Context during
render, callable conditionally/after early returns — only cached promises
may be passed, not ones created fresh during render); `ref` as a normal prop
on function components (removing most `forwardRef` need) plus cleanup
functions returned from ref callbacks; `<Context>` usable directly as a
provider; `react-dom/static`'s `prerender()`/`prerenderToNodeStream()`;
native `<title>`/`<link>`/`<meta>` rendering with auto-hoist to `<head>`;
native stylesheet/async-script support with ordering/de-duplication; full
custom-elements support; new root error options (`onCaughtError`,
`onUncaughtError`, `onRecoverableError`) [Source: react.dev/blog/2024/12/05/react-19].

**React 19.2 additions** (applies_to: `>=19.2`): `<Activity>` (wraps a
subtree in `mode="visible"`/`"hidden"` to deprioritize/preserve state for
off-screen UI); `useEffectEvent` (extracts "event-like" logic out of an
Effect so it always sees latest props/state — must **not** be added to the
Effect's dependency array, and requires an up-to-date
`eslint-plugin-react-hooks`); `cacheSignal` (RSC-only, signals when a
`cache()` call's lifetime ended); partial pre-rendering resume APIs
(`resume`, `resumeToPipeableStream`, `resumeAndPrerender`,
`resumeAndPrerenderToNodeStream`); Web Streams support added for Node
(docs still recommend the Node Streams variants for performance/compression);
`useId` prefix changed from `:r:`/`«r»` to `_r_`
[Source: react.dev/blog/2025/10/01/react-19-2].

Deeper API surface (Actions form details, custom-elements SSR/CSR property
handling, the full Legacy APIs list) is in the API reference itself
(`react.dev/reference/react`) — not restated here per context-efficiency.

## Decision framework

1. **Hooks composition — extract a custom Hook or keep logic inline?** Extract
   when logic is reused across components or when naming it clarifies intent;
   don't extract prematurely for one call site (over-abstraction trap).
2. **Effect vs. event handler vs. derived-during-render value** (the
   documented decision tree): "is this running *because the component was
   displayed*?" → Effect. "is this running because of a specific user
   interaction?" → event handler. "can this value be derived from existing
   props/state?" → compute it during render, optionally cached with
   `useMemo` [Source: react.dev/learn/you-might-not-need-an-effect]. Default
   to the last two; reach for an Effect only when nothing else fits.
3. **Is a Server Component or a Client Component warranted?** Default to a
   Server Component (no client bundle cost, direct server-side data access)
   and add `"use client"` only once a documented client-only capability is
   actually needed — local state, Effects, browser-only APIs, event
   listeners, or a client-only third-party library. This decision only
   applies once a meta-framework with RSC support is already chosen (that
   broader rendering-mode choice is `SK-FE-005`'s); within RSC, marking
   everything `"use client"` "to be safe" defeats the point of RSC and is the
   most common misapplication.
4. **Does React Compiler adoption change the manual-memoization answer?**
   With the Compiler adopted, `memo`/`useMemo`/`useCallback` become escape
   hatches for fine-grained manual control rather than the default pattern —
   docs describe the Compiler's automatic, potentially conditional
   memoization as more comprehensive than manual `memo`+`useMemo` combined,
   and state it is "safe to remove `memo` annotations" once the Compiler is
   in place [Source: react.dev/reference/react/memo]
   [Source: react.dev/reference/react/useMemo]. Without the Compiler, keep
   the documented `useMemo` bar: only for calculations empirically measured
   as slow (rule of thumb: roughly ≥1ms, on a representative/slower device,
   in production mode), values feeding a `memo`-wrapped child, or values used
   as another Hook's dependency — not speculatively.
5. **Simplest first (anti-overengineering):** don't add a Suspense boundary
   more granular than the actual loading sequence you want the user to
   experience [Source: react.dev/reference/react/Suspense]; don't add
   `useMemo`/`memo` without having measured a real cost; don't mark a
   component `"use client"` without a concrete client-only need.

## Workflow

1. Determine the installed React major/minor version (`package.json`) — it
   gates which APIs, the RSC CVE exposure check, and the migration path
   apply.
2. Confirm whether RSC is in scope (a meta-framework with RSC support
   configured); if so, apply the Server/Client boundary decision above before
   writing component code.
3. Apply the Rules of React and the Effect-vs-event-handler-vs-derived-value
   decision tree while implementing.
4. If touching memoization, check whether the React Compiler is adopted
   before adding/removing manual `memo`/`useMemo`/`useCallback`.
5. Verify (see Outputs & verification) before declaring done.

## Engineering rules

- Call Hooks only at the top level of a component or another Hook — never
  conditionally, in a loop, or after an early return.
- Never call a component as a plain function or pass a Hook around as a value.
- Keep render pure: no side effects, no mutation of props/state/Hook return
  values during render; side effects belong in an Effect or event handler.
- Don't define a component function inside another component's body — it
  gets a new identity every render, which destroys and recreates its state
  each time (looks like "state won't stick"; the real cause is the nested
  definition, not React's state model)
  [Source: react.dev/learn/preserving-and-resetting-state].
- Default new components in an RSC-enabled tree to Server Components; add
  `"use client"` only for a documented client-only need.
- Before removing existing manual memoization after adopting the Compiler,
  confirm test coverage exists — see Testing.

## Trade-offs

Error boundaries can only currently be written as class components (the docs
state there is "no way to write an Error Boundary as a function component"),
with the third-party `react-error-boundary` package as the documented
workaround for authors who want to avoid the class
[Source: react.dev/reference/react/Component] — a real, still-open API gap,
not an oversight to "fix" locally. The React Compiler trades a build-time
Babel dependency and initial adoption effort (incremental-adoption guide,
gating strategies for existing apps) for removing most hand-written
memoization; teams not ready to add a compiler step keep the manual
`memo`/`useMemo`/`useCallback` discipline instead. `useMemo`'s cache is
explicitly **not a correctness guarantee** — React may discard a memoized
value (dev-mode file edits, a component suspending before first mount) — so
it must never substitute for `useState`/`useRef` when a result must persist
[Source: react.dev/reference/react/useMemo].

## Anti-patterns

The official, extensive catalog is the "You Might Not Need an Effect" page
[Source: react.dev/learn/you-might-not-need-an-effect]:
- **Deriving state with an Effect** (an Effect that computes one value from
  another and calls `setState`) — causes an extra render with a stale
  intermediate value; compute the derived value directly during render.
- **Caching an expensive computation via Effect + state** — use `useMemo`.
- **Resetting a subtree's state via Effect on a prop change** — give the
  subtree an explicit `key` instead.
- **Sharing logic between event handlers via a shared Effect** — an Effect
  triggered by a state change fires on more occasions than the intended
  action (e.g. also on page reload) — extract a plain function called from
  each handler instead; this is a correctness bug, not a style issue.
- **Handling a user event's side effect by setting state and reacting in an
  Effect** — perform the action directly in the event handler.
- **Chaining multiple state-setting Effects to trigger the next Effect** —
  compute all next state inside a single event handler instead.
- **Fetching data in an Effect without a cleanup/ignore flag** — an explicit
  documented **race condition** (a slower, stale response can overwrite a
  newer one); track an `ignore` boolean set in the cleanup function.
- **"Run once" init logic guarded only by a module-level flag** — still runs
  twice under Strict Mode without the guard; move such logic to
  module-initialization time instead.

Also documented elsewhere: **calling a component as a plain function** or
**passing a Hook as an ordinary value** [Source: react.dev/reference/rules];
writing `dangerouslySetInnerHTML={{__html: ...}}` **inline** at the JSX call
site rather than in a clearly-named helper near where the HTML is produced,
which makes the trust boundary harder to audit
[Source: react.dev/reference/react-dom/components/common]; omitting a
`useMemo` dependency array (silently recomputes every render) or writing an
arrow function with implicit-object-return shorthand (`() => { key: value }`,
parsed as a function body, not an object literal) instead of an explicit
`return`
[Source: react.dev/reference/react/useMemo]. **Over-engineering trap for
this domain:** adding a Suspense boundary around every component, or adding
`useMemo`/`memo` speculatively without having measured a real cost — both add
complexity without the documented payoff.

## Security

**`dangerouslySetInnerHTML`** is the primary documented XSS vector — React's
equivalent of DOM `innerHTML`, deliberately verbosely named as friction. The
docs state plainly: "Unless the markup is coming from a completely trusted
source, it is trivial to introduce an XSS vulnerability this way," with a
worked `<img onerror=...>` injection example
[Source: react.dev/reference/react-dom/components/common]. It is genuinely
needed only for markup from a fully trusted or already-sanitized source (e.g.
the output of a trusted Markdown-to-HTML renderer) — never for raw user
input; when needed, construct the `{__html}` object as close as possible to
where the HTML is actually generated, not inline at the render call site, so
the trust boundary stays auditable. The broader React-vs-Vue-vs-Angular
default-escaping comparison is owned by `SK-FE-001` and not repeated here.

**CVE-2025-55182 (CVSS 10.0, Critical, unauthenticated RCE)** — disclosed
December 3, 2025: an RSC Server Function payload-deserialization
vulnerability in `react-server-dom-webpack`, `react-server-dom-parcel`, and
`react-server-dom-turbopack`. Apps can be vulnerable even without explicitly
implementing a Server Function endpoint, as long as RSC is supported at all.
**Vulnerable: 19.0, 19.1.0, 19.1.1, 19.2.0. Fixed: 19.0.1, 19.1.2, 19.2.1**
(plus framework-specific patches, e.g. multiple Next.js minors from 14.2.35
through 16.1.5). The same disclosure also covered CVE-2025-55184 /
CVE-2025-67779 (High, DoS) and CVE-2025-55183 (Medium, Server Function
source-code exposure — runtime secrets like `process.env.SECRET` are *not*
exposed by this one)
[Source: react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components].

**CVE-2026-23864 (High, CVSS 7.5, DoS)** — disclosed 8 days later, December
11, 2025: the initial patch was **incomplete**. **Vulnerable: 19.0.0–19.0.3,
19.1.0–19.1.3, 19.2.0–19.2.3, across the same three `react-server-dom-*`
packages. Actually fixed: 19.0.4, 19.1.5, 19.2.4.** Apps already updated to
the Dec-3 patch versions (19.0.3 / 19.1.4 / 19.2.3) were **still vulnerable**
and needed to update again; the original RCE fix (CVE-2025-55182) itself
remained effective — this follow-up is DoS/source-exposure only, not RCE
[Source: react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components].
**Any app using RSC must be checked against both ranges, not just the first
disclosure** — staying current on `react`, `react-dom`, and the specific
`react-server-dom-*` bundler package is a documented **hard production
requirement** for RSC apps, not an optional best practice; don't rely on a
hosting provider's mitigation as a substitute for actually upgrading.

Error boundaries do **not** catch errors in event handlers, async callbacks
(`setTimeout`, `requestAnimationFrame`), during SSR, or inside the boundary's
own `componentDidCatch`/render — a robustness limitation worth flagging
alongside the class-only gap noted in Trade-offs
[Source: react.dev/reference/react/Component]. Deep threat modeling beyond
React's own documented surface is owned by `security-engineering` (see the
[skill catalog](../../core/taxonomy/skill-catalog.md)) and not restated here.

## Performance

**React Compiler** (stable v1.0, October 7, 2025) is the current headline
performance recommendation: a build-time Babel plugin
(`babel-plugin-react-compiler`) that auto-memoizes components and values,
including conditional memoization manual `useMemo`/`useCallback` can't
express. Documented Meta-internal production numbers: "initial loads and
cross-page navigation improved by up to 12%," "certain interactions up to
2.5× faster," memory neutral
[Source: react.dev/blog/2025/10/07/react-compiler-1]. Pre-configured by
default in Expo SDK 54+; available via `create-vite` and `create-next-app`
scaffolds for new apps; existing apps use the documented incremental-adoption
guide with gating strategies (applies_to: works best on React 19; also
supports 17/18 via `react-compiler-runtime` + a minimum-target-version
config).

**Resource preloading APIs** (`prefetchDNS`, `preconnect`, `preload`,
`preinit`, all from `react-dom`, introduced in React 19) imperatively hint
the browser to fetch scripts/fonts/stylesheets/connections ahead of when
they're rendered [Source: react.dev/blog/2024/12/05/react-19].

**Suspense reveal batching**: React reveals suspended content at most once
every 300ms measured from the last reveal, so nearby-resolving boundaries
appear together; a documented heuristic stops batching as the page nears the
~2.5s LCP threshold, to avoid hurting Core Web Vitals — extended to SSR in
19.2 to align server/client reveal behavior
[Source: react.dev/reference/react/Suspense]
[Source: react.dev/blog/2025/10/01/react-19-2] (applies_to: SSR batching,
`>=19.2`). Deep cross-cutting performance method is owned by
`performance-engineering` (see the
[skill catalog](../../core/taxonomy/skill-catalog.md)).

## Testing

**Documented gap:** react.dev currently offers **no official recommendation
for a unit-test runner**. The closest first-party guidance is two
deprecation-warning pages: `react-test-renderer` is explicitly deprecated
("implements its own renderer environment that doesn't match the environment
users use, promotes testing implementation details, relies on introspection
of React's internals"), and `react-dom/test-utils` carries a similar
deprecation warning — both point to **`@testing-library/react`**
(`@testing-library/react-native` for React Native) as the recommended
replacement [Source: react.dev/warnings/react-test-renderer]. No standalone
"how to test a React component" tutorial was located on react.dev beyond the
`act` reference page and these two deprecation pages — **Unresolved:**
whether such a first-party guide exists elsewhere in the current
information architecture; treat react.dev's testing documentation as thin
relative to other dimensions and `@testing-library/react` as the de facto,
not officially-taught, standard.

**Version-sensitive:** `act`, used to ensure all updates from a test
interaction are applied before assertions run, moved from
`react-dom/test-utils` into the `react` package itself as of React 19
(`import {act} from 'react'`; codemod:
`npx codemod@latest react/19/replace-act-import`)
[Source: react.dev/reference/react/act] (applies_to: `>=19.0`).

When adopting the React Compiler, the docs recommend "following the Rules of
React and employing continuous end-to-end testing of your app so you can
upgrade the compiler with confidence" — a solid pre-existing test suite is a
documented prerequisite for safely enabling the Compiler and for safely
removing manual memoization afterward, not something the Compiler
substitutes for [Source: react.dev/blog/2025/10/07/react-compiler-1]. Deep
test-strategy method beyond React's own gap here is owned by
`testing-strategy` (see the
[skill catalog](../../core/taxonomy/skill-catalog.md)).

## Failure handling

- If the installed React version can't be determined, ask or explicitly state
  the version the guidance assumes — never assume "latest" silently,
  especially given the RSC CVE ranges above.
- If shell is unavailable or denied, degrade to advisory code/diff output and
  state that install/codemod/build/test commands were not actually run.
- If it's unclear whether a component needs interactivity, default to a
  Server Component and only add `"use client"` once a documented client-only
  capability is actually needed.

## Escalation

- An app found running `react-server-dom-*` versions inside the
  CVE-2025-55182 or CVE-2026-23864 vulnerable ranges is flagged immediately
  as a security issue requiring an upgrade, not treated as a routine
  version-bump suggestion.
- A React major-version migration (e.g. 18→19) affecting a production app is
  presented with the documented breaking-change list for explicit
  confirmation, not applied unilaterally.

## Outputs & verification

- **Outputs:** version-correct component/Hook code; a Server/Client Component
  boundary recommendation when RSC is in scope; analysis (memoization
  strategy, version-correct API usage, CVE-exposure check) with the React
  version it applies to.
- **Verify:** Hooks called only at the top level, never conditionally/in a
  loop/after an early return; any `dangerouslySetInnerHTML` traces to a
  trusted/sanitized source and is constructed near where the HTML is
  produced, not inline; any `react-server-dom-*` version referenced is
  checked against the fixed-version list above; every version-specific claim
  carries the range it holds for.

## References

- [frontend-architecture](../frontend-architecture/SKILL.md) (`SK-FE-001`) —
  parent skill; owns the React-vs-Vue-vs-Angular comparison and the generic
  component/state-management method.
- `SK-FE-005` (rendering-strategy) — forward reference, not yet authored;
  owns the general SSR/SSG/CSR rendering-mode decision.
- `SK-TECH-nextjs`, `SK-TECH-typescript` — related skills, forward
  references, authored by sibling agents in this batch.
- Source list: see `skill.yaml.source_references` (react.dev official docs
  and blog, plus `research/knowledge-maps/version-matrix.md`; retrieved
  2026-09-10, via `research/technologies/react.md`).
