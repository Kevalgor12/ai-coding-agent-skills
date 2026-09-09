# React

Deep reference research on **React**, the JavaScript library for building user
interfaces. Primary source is the official documentation site **react.dev**,
supplemented by the official `react.dev` blog, the official `reactjs/react.dev`
and `react/react` (formerly `facebook/react`) GitHub repositories, and the npm
registry (the official distribution channel for the `react` package). Research
date: **2026-09-09**.

## 0. Canonical docs host and how to read this document

[Source: https://react.dev/versions] The canonical, current documentation
host is **https://react.dev** (launched March 16, 2023, replacing the old
`reactjs.org` docs). [Source: https://react.dev/versions] React's docs policy
is to document **only the latest major version** at the root domain; when a
new major version ships, the previous major's docs are frozen and archived at
a version-prefixed subdomain (`18.react.dev`, `17.react.dev`, `16.react.dev`,
`15.react.dev`), and versions older than 15 are on `legacy.reactjs.org`. This
document is based on the **react.dev docs for React 19** (the current major
version as of the research date — see §12).

[Source: https://registry.npmjs.org (npm dist-tags for the `react` package,
queried 2026-09-09)] The npm registry — the official package distribution
channel — reports `latest: 19.2.8`, `next: 19.3.0-canary-...`, `canary:
19.3.0-canary-...`, `experimental: 0.0.0-experimental-...`, and a
`backport: 19.0.8` tag. This corroborates the version claims sourced from
react.dev/blog below.

[Source: https://react.dev/blog/2026/02/24/the-react-foundation] As of
**February 24, 2026**, React's project ownership (React, React Native, and
supporting projects like JSX) transitioned from sole Meta ownership to an
independent **React Foundation** hosted by the **Linux Foundation**, with
eight "Platinum Founding Members" (Amazon, Callstack, Expo, Huawei, Meta,
Microsoft, Software Mansion, Vercel) and Executive Director Seth Webster.
[Source: https://react.dev/blog/2026/02/24/the-react-foundation] The blog
post states technical governance remains independent of the foundation board:
"React's technical direction continues to be set by contributors and
maintainers," with a provisional leadership council formed to define the
long-term technical governance structure ("updates expected in coming
months" as of that post). [Inference, not confirmed in docs] This is a
recent enough change (about 6 months before this research date) that release
process/governance documentation on react.dev may not yet fully reflect it;
readers should treat any statement about "who maintains React" as
time-sensitive.

---

## 1. Core concepts

[Source: https://react.dev/learn] React's "Learn React" section is the
canonical description of core concepts, organized as a progressive course:
Components & Nesting → JSX Markup → Styling → Displaying Data → Conditional
Rendering → Rendering Lists → Event Handling → State (`useState`) → Hooks →
Sharing data between components (props, lifting state up) → tutorial app.

[Source: https://react.dev/learn] **Components**: React apps are built from
*components* — independent, reusable pieces of UI. A component is a
JavaScript function whose name **must start with a capital letter** (this is
how React/JSX distinguishes a custom component from a built-in HTML tag), and
which returns markup (JSX).

[Source: https://react.dev/learn] **JSX**: a markup syntax that mixes
HTML-like markup with JavaScript in the same file. JSX is **stricter than
HTML** — for example, all tags must be explicitly closed, and multiple JSX
elements at the top level must be wrapped in a single parent (e.g. a
Fragment). Curly braces `{}` embed JavaScript expressions inside JSX.

[Source: https://react.dev/learn] **Props**: the mechanism by which a parent
component passes data down to a child component; props are read like
function parameters by the receiving component.

[Source: https://react.dev/learn] **State**: local, per-component-instance
memory that a component can use to "remember" information across renders,
created with the `useState` Hook. [Source:
https://react.dev/learn/preserving-and-resetting-state] Critically, React
associates state not with the component *instance* per se but with the
component's **position in the render tree** — the same component type
re-rendered at the same tree position keeps its state; the `key` prop is the
documented mechanism to override this and give a component an explicit
identity independent of position (see §5 and §8).

[Source: https://react.dev/learn] **Hooks**: functions whose names start
with `use` (e.g. `useState`) that let function components tap into React
features (state, lifecycle-like behavior, context, refs, etc.). Hooks must be
called only at the top level of a component or another Hook — see the Rules
of React in §5.

[Source: https://react.dev/learn/thinking-in-react] **"Thinking in React"**
is documented as a five-step official methodology for building a UI in
React: (1) break the UI into a component hierarchy, (2) build a static
(non-interactive) version from the data model using only props, (3) find the
minimal-but-complete representation of UI state (applying a DRY principle:
if a value can be computed from props/other state, it is not state), (4)
identify where each piece of state should live (in the closest common
parent of the components that need it — "one-way data flow"), and (5) add
inverse data flow (pass setter functions down as callbacks). [Source:
https://react.dev/learn/thinking-in-react] This is presented as the
canonical mental model for React application architecture, built around a
**single source of truth** for each piece of state and unidirectional data
flow.

---

## 2. Architecture

[Source: https://react.dev/learn/render-and-commit] React's documented
update model has three phases: **(1) Trigger** — a render is triggered
either by the initial `createRoot().render()` call or by a state update via
a `set` function; **(2) Render** — React calls component functions
(recursively, for nested components) to determine what should be displayed.
[Source: https://react.dev/learn/render-and-commit] Rendering must be
**pure**: the same inputs (props, state, context) must produce the same JSX
output, and components must not mutate external state during render; React's
Strict Mode (see §5, §8) calls component functions twice in development
specifically to surface impurities. [Source:
https://react.dev/learn/render-and-commit] **(3) Commit** — React applies the
minimal set of DOM operations needed to reconcile the previous commit with
the new render output (on initial render, it uses `appendChild()` to build
the whole tree; on re-renders, it only touches what actually changed, e.g.
leaving an `<input>`'s live value untouched if the render output for that
node didn't change). Note: [Inference, not confirmed in docs] the fetched
page explicitly states it does **not** go into "virtual DOM," "Fiber," or a
low-level reconciliation algorithm — react.dev's official Learn docs
describe the render/commit model at a conceptual level, not an implementation
level; no page found during this research names "Fiber" as the internal
architecture, though this is widely known from other (non-canonical) sources
and should be treated as **Unresolved: whether current official react.dev
docs use the term "Fiber" anywhere** — not found in the pages fetched.

[Source: https://react.dev/learn/preserving-and-resetting-state] React's
reconciliation is documented as position-in-tree-based: for each position in
the render tree, React compares the previous and new element type (and `key`
if present) — same type/key at the same position → the existing component
instance and its state are reused; different type, different key, or removal
from the tree → the old instance and its state are destroyed and a new
instance is created.

[Source: https://react.dev/reference/rsc/server-components] **React Server
Components (RSC)** represent, per the docs, "a fundamental shift in React's
rendering architecture, treating servers and clients as equal partners in
component rendering." Server Components execute ahead of time in a separate
server environment — either at build time (e.g. on CI, to produce static
content with no runtime server needed) or at request time (on a web server,
for per-request dynamic rendering) — and are documented as distinct from
traditional SSR because they never need to ship their own component code to
the client. [Source: https://react.dev/reference/rsc/server-components]
Server Components compose with **Client Components** (marked with the
`"use client"` directive) to add interactivity; the client receives only the
already-rendered output of Server Components as props passed into Client
Components, not the Server Components' own source. [Source:
https://react.dev/reference/rsc/server-components] The `"use server"`
directive marks **Server Functions** (not Server Components) — callable async
functions invoked from Client Components. [Source:
https://react.dev/reference/rsc/server-components] **Version-sensitive**:
"While React Server Components in React 19 are stable and will not break
between minor versions, the underlying APIs used to implement a React Server
Components bundler or framework do not follow semver and may break between
minors in React 19.x" — i.e. RSC as an *application-facing* feature is
semver-stable in 19.x, but the low-level bundler/framework integration APIs
are explicitly **not** semver-stable and framework authors are told to pin
exact React versions.

[Inference, not confirmed in docs] React itself, as distributed via the
`react` package, is architecturally a rendering-target-agnostic core (the
reconciler) paired with separate renderer packages (`react-dom` for the web,
and implicitly `react-native` for native, not covered by react.dev) — this is
consistent with the package structure observed (`react`, `react-dom`,
`react-dom/client`, `react-dom/server`, `react-dom/static`) but no single
react.dev page was found in this research that states this "core +
renderers" architecture explicitly as an architectural principle; treat as
inference from package layout, not a documented architectural claim.

---

## 3. APIs

[Source: https://react.dev/reference/react] The API reference is organized
into: **React core** — Hooks (`/reference/react/hooks`), Components
(`/reference/react/components`, including `Fragment`, `Profiler`,
`StrictMode`, `Suspense`, and `Activity`), top-level APIs
(`/reference/react/apis`, e.g. `createContext`, `lazy`, `memo`,
`forwardRef`), and RSC Directives (`/reference/rsc/directives`); **React
DOM** — DOM-specific Hooks (`/reference/react-dom/hooks`), built-in HTML/SVG
components (`/reference/react-dom/components`), and APIs split into general
(`/reference/react-dom`), client (`/reference/react-dom/client`), server
(`/reference/react-dom/server`), and static (`/reference/react-dom/static`);
plus a separate **Legacy APIs** section (`/reference/react/legacy`) for
deprecated APIs "not recommended for new code," and dedicated pages for the
**React Compiler**, the **ESLint plugin for React Hooks**, and the **Rules of
React**.

[Source: https://react.dev/blog/2024/12/05/react-19] **New in React 19**
(version-sensitive — introduced in the v19.0.0 major release, Dec 5, 2024):
- **Actions / `useActionState`**: wraps an action function, returns
  `[data, submitAction, isPending]`; replaces the earlier `useFormState` API.
- **`useFormStatus`**: reads the pending/data/method status of the nearest
  parent `<form>` without prop drilling (imported from `react-dom`).
- **`useOptimistic`**: shows an optimistic UI value while an async action is
  in flight, auto-reverting on completion/error.
- **`use()`**: reads the value of a Promise or Context during render (not a
  traditional Hook — it can be called conditionally/after early returns);
  used with Suspense for promises. Only promises that are cached across
  renders may be passed — passing a promise created fresh during render is
  documented as unsupported.
- **`ref` as a normal prop** on function components (removing the need for
  `forwardRef` in most cases), plus **cleanup functions returned from ref
  callbacks** (analogous to Effect cleanup).
- **`<Context>` used directly as a provider** instead of
  `<Context.Provider>`.
- **`react-dom/static`**: `prerender()` and `prerenderToNodeStream()` for
  static HTML generation that waits for data to load (successor pattern to
  `renderToString` for this use case).
- **Resource preloading APIs** in `react-dom`: `prefetchDNS`, `preconnect`,
  `preload`, `preinit`.
- **Native document metadata**: rendering `<title>`, `<link>`, `<meta>`
  directly inside components, auto-hoisted to `<head>`.
- **Native stylesheet support** via `<link rel="stylesheet" precedence="...">`
  with automatic insertion-order management, and native async `<script>`
  support with automatic de-duplication.
- **Full custom-elements (Web Components) support**, including correct
  property vs. attribute handling for SSR and CSR.
- **New root error-handling options**: `onCaughtError`, `onUncaughtError`,
  `onRecoverableError` on `createRoot`/`hydrateRoot`.

[Source: https://react.dev/blog/2025/10/01/react-19-2] **New in React 19.2**
(version-sensitive — minor release, Oct 1, 2025):
- **`<Activity>`** component: wraps a subtree in `mode="visible"` or
  `mode="hidden"` to let React deprioritize/hide-and-preserve state for
  off-screen UI (e.g. pre-rendering a likely-next screen, or keeping a
  navigated-away screen's state alive).
- **`useEffectEvent`**: extracts "event-like" logic out of an Effect so it
  always sees latest props/state without being an Effect dependency; the
  docs state it **must not** be added to the Effect's dependency array, and
  using it requires an up-to-date `eslint-plugin-react-hooks`.
- **`cacheSignal`** (React Server Components only): signals when a `cache()`
  call's lifetime has ended, to support cleanup/abort of in-flight work tied
  to a render that completed, aborted, or errored.
- **Partial pre-rendering** for `react-dom/static`/`react-dom/server`:
  `prerender()` (with `AbortController`), `resume()`,
  `resumeToPipeableStream()`, `resumeAndPrerender()`,
  `resumeAndPrerenderToNodeStream()`.
- **Web Streams support added for Node.js**: `renderToReadableStream()`,
  `prerender()`, `resume()`, `resumeAndPrerender()` now work under Node, but
  the docs still recommend the Node Streams variants
  (`renderToPipeableStream`, etc.) for better performance/compression
  support under Node.
- **`useId` prefix changed** from `:r:`/`«r»` to `_r_` (so generated IDs are
  valid for CSS `view-transition-name` and XML 1.0 names) — a
  version-sensitive, technically-breaking-for-snapshot-tests change, though
  the blog post frames it as a bug fix rather than a documented breaking
  change.

[Source: https://react.dev/reference/react/Component] **Legacy/class-only
API surface still in the reference**: class components remain supported
("Class components are still supported by React, but we don't recommend
using them in new code"), and the **error-boundary pattern** — implementing
`static getDerivedStateFromError(error)` and optionally
`componentDidCatch(error, info)` — is documented as requiring a class
component; the docs explicitly state "there is currently no way to write an
Error Boundary as a function component" and point to the third-party
`react-error-boundary` package as the documented alternative for authors who
want to avoid writing the class themselves.

---

## 4. Configuration

[Inference, not confirmed in docs] React itself (the `react` / `react-dom`
packages) is a library, not a framework, and has **no first-party
configuration file format of its own** (no `react.config.js` equivalent is
documented) — "configuration" in the official docs is almost entirely about
(a) which framework/build tool you use to consume React, and (b)
compiler/lint configuration for the React Compiler.

[Source: https://react.dev/learn/installation] Official docs describe three
setup paths: **(1)** start a new app with a **recommended framework**
(Next.js, React Router v7, Expo — see §16), **(2)** [Source:
https://react.dev/learn/build-a-react-app-from-scratch] build from scratch
using a build tool (**Vite**, **Parcel**, or **RSbuild** are the tools named)
when a framework isn't a good fit, or **(3)** add React to an existing
non-React page/app incrementally.

[Source: https://react.dev/learn/installation] [Source:
https://react.dev/blog/2025/02/14/sunsetting-create-react-app]
**Version-sensitive**: **Create React App (CRA) is deprecated** — the
official sunsetting announcement is dated **February 14, 2025** — and is no
longer an officially endorsed way to start a new React app; existing CRA
apps are pointed toward migrating to a framework or a build tool (Vite,
Parcel, RSbuild).

[Source: https://react.dev/learn/typescript] **TypeScript configuration**:
adding TypeScript to an existing React project requires `npm install
--save-dev @types/react @types/react-dom`, a `tsconfig.json` with `"dom"`
included in `lib` (default if `lib` is unset) and a valid `jsx` compiler
option (`preserve` is the option named for most app setups), and `.tsx` file
extensions for any file containing JSX. [Source:
https://react.dev/learn/typescript] The docs explicitly note the react.dev
sandboxes support TypeScript syntax but **do not type-check** — the
TypeScript Playground is recommended for actual type validation.

[Source: https://react.dev/reference/react-compiler] [Source:
https://react.dev/blog/2025/10/07/react-compiler-1] **React Compiler
configuration**: installed as `babel-plugin-react-compiler` (npm/pnpm/yarn,
pinned with `--save-exact`); documented to **work with no configuration by
default**. [Source: https://react.dev/blog/2025/10/07/react-compiler-1]
**Version-sensitive**: the Compiler is designed to work best with **React
19**, but also **supports React 17 and 18** — for those older majors, the
docs say to add the `react-compiler-runtime` package as a dependency and
specify a minimum target React version in the compiler config. [Source:
https://react.dev/blog/2025/10/07/react-compiler-1] For **new** apps, the
Compiler is pre-configured by default in **Expo SDK 54+**, and available via
`create-vite` and `create-next-app` scaffolds; for **existing** apps, the
docs point to a documented incremental-adoption guide
(`/learn/react-compiler/incremental-adoption`) with gating strategies.
[Source: https://react.dev/blog/2025/10/07/react-compiler-1] Compiler-powered
ESLint rules ship inside `eslint-plugin-react-hooks` (e.g.
`set-state-in-render`, `set-state-in-effect`, `refs`), configured via the
flat ESLint config as `reactHooks.configs.flat.recommended`.

---

## 5. Recommended patterns

[Source: https://react.dev/reference/rules] The **Rules of React** page
states these are treated by the React team as **mandatory rules, not style
guidelines** — violating them causes bugs, and the recommended enforcement
tools are **Strict Mode** and **`eslint-plugin-react-hooks`**. The three
top-level rule groups:
1. **Components and Hooks must be pure**: components must be idempotent
   (same props/state/context → same output, since React may call them
   multiple times); side effects must run outside render (in an Effect or
   an event handler, not during the render call itself); props and state
   must be treated as immutable snapshots; Hook arguments/return values, and
   any value already passed into JSX, must not be mutated afterward.
2. **React calls Components and Hooks** — you never call a component as a
   plain function (`MyComponent()`) or pass a Hook around as a value; Hooks
   are only ever called from inside components or other Hooks.
3. **Rules of Hooks**: Hooks may only be called at the **top level** — never
   inside loops, conditionals, or nested functions, and never after an early
   return — and only from React function components or custom Hooks (whose
   names must start with `use`).

[Source: https://react.dev/learn/thinking-in-react] The **Thinking in React**
five-step methodology (see §1) is the documented top-level architectural
pattern: minimal state, single source of truth, state lifted to the closest
common parent, one-way (top-down) data flow with inverse data flow via
callback props.

[Source: https://react.dev/learn/preserving-and-resetting-state] **Using
`key` to control identity**: the docs recommend explicit `key` props to (a)
force distinct list items to keep independent state as the list is
reordered/filtered, and (b) intentionally reset a subtree's state when
switching between logically distinct instances of the same component (e.g.
`<Chat key={to.id} contact={to} />` to fully reset chat state per
recipient).

[Source: https://react.dev/learn/you-might-not-need-an-effect] A whole
dedicated page frames the **default-to-render-or-event-handler, not Effect**
pattern as the core recommendation for state/data-flow logic (also see §6,
since this page is simultaneously the canonical anti-pattern catalog): the
documented decision framework is "is this code running *because* the
component was displayed?" → use an Effect; "is this running because of a
specific user interaction?" → use an event handler; "can this value be
derived from existing props/state?" → compute it during render (optionally
cached with `useMemo`).

[Source: https://react.dev/learn/typescript] For TypeScript users: prefer
`interface`/`type` definitions for props (documented as more idiomatic than
inline object-literal prop types for anything beyond the simplest case), and
prefer setting the type on `initialState` for `useReducer` rather than
supplying it as an explicit generic argument.

[Source: https://react.dev/reference/react/memo]
[Source: https://react.dev/reference/react/useMemo] With the React Compiler
adopted, official guidance shifts: `memo`/`useMemo`/`useCallback` are
described as usable **escape hatches for fine-grained manual control**
rather than the default pattern; the compiler's automatic, potentially
conditional memoization is described as "more comprehensive" than manual
`memo` (comparable to `memo` + `useMemo` combined), and docs state it is
"safe to remove `memo` annotations" once the compiler is in place — but see
§6 for the caveat about *testing* before removing existing manual
memoization.

---

## 6. Anti-patterns

[Source: https://react.dev/learn/you-might-not-need-an-effect] This page is
the official, extensive anti-pattern catalog for `useEffect` misuse. Documented
anti-patterns and their prescribed fixes:
- **Deriving state with an Effect** (`useEffect` that calls `setFullName` from
  `firstName`/`lastName`) — causes an extra render pass with a stale
  intermediate value; fix: compute the derived value directly during render.
- **Caching an expensive computation via Effect + state** — fix: `useMemo`.
- **Resetting a whole subtree's state on a prop change via Effect** — fix:
  give the subtree an explicit `key` derived from the identity that changed.
- **Adjusting some state in response to a prop change via Effect** — fix:
  either compute the adjusted value during render, or (documented as a
  fallback, not preferred) adjust state directly during render guarded by a
  "previous value" comparison, rather than in an Effect.
- **Sharing logic between multiple event handlers via a shared Effect** —
  fix: extract a plain function called from each handler; an Effect
  triggered by a state change fires on more occasions than the intended user
  action (e.g. also on page reload), which is called out as a correctness
  bug, not just a style issue.
- **Handling a user event's side effect (e.g. a POST request) by setting
  state and reacting to it in an Effect** — fix: perform the action directly
  in the event handler.
- **Chaining multiple Effects that each set state to trigger the next
  Effect** — documented as inefficient (multiple extra render passes) and
  fragile; fix: compute all next state inside a single event handler.
- **"Run once" initialization logic in an Effect with a module-level guard
  flag** — documented as still running twice under Strict Mode without the
  guard, and the doc's own top recommendation is to move such logic to
  module-initialization time (guarded by an `if (typeof window !==
  'undefined')` check) rather than inside a component Effect at all.
- **Notifying a parent of a state change via an Effect calling a prop
  callback** (`onChange`) — documented as causing a cascade of extra
  renders because the parent update happens "too late"; fix: call both the
  local setter and the parent callback together, in the same event handler,
  or lift the state fully to the parent (controlled component).
- **Passing fetched data to a parent via an Effect calling a prop
  callback** — fix: fetch in the parent and pass data down as props instead.
- **Fetching data in an Effect without a cleanup/ignore flag** — documented
  explicitly as a **race-condition bug** (a slower, stale response can
  overwrite a newer one); fix: track an `ignore` boolean set `true` in the
  Effect's cleanup function and check it before calling `setState`.

[Source: https://react.dev/learn/preserving-and-resetting-state] **Defining
a component function inside another component's body** is called out
explicitly as an anti-pattern: because the inner function is a *new*
function identity on every render, React treats it as a different component
type at that tree position on every render, destroying and recreating its
state every time — visually this looks like "state won't stick," but the
root cause is the nested definition, not React's state model.

[Source: https://react.dev/reference/rules] Calling a component as a plain
function (`MyComponent()` instead of `<MyComponent />`) and passing Hooks
around as ordinary values (as function arguments, stored in
data structures, etc.) are both explicitly named anti-patterns under "React
calls Components and Hooks."

[Source: https://react.dev/reference/react-dom/components/common]
`dangerouslySetInnerHTML={{__html: ...}}` written **inline** (constructing
the `{__html}` object literal directly at the JSX call site rather than in a
clearly-named helper close to where the HTML string is produced) is called
out as a pattern to avoid, separate from the underlying XSS risk (see §7),
because it makes it harder to audit where raw/untrusted HTML enters the
render tree.

[Source: https://react.dev/reference/react/useMemo] Two useMemo-specific
footguns are explicitly named: (1) omitting the dependency array entirely
(silently recomputes on every render, defeating the purpose), and (2) using
an arrow function with an implicit-object-return shorthand
(`() => { key: value }`), which JS parses as a function *body* rather than
an object literal — the docs prescribe an explicit `return` statement inside
braces as the fix.

---

## 7. Security

[Source: https://react.dev/reference/react-dom/components/common]
**`dangerouslySetInnerHTML`** is the primary documented XSS vector: it is
React's equivalent of the DOM `innerHTML` property, deliberately named
verbosely as a friction/warning mechanism. The docs give a worked example of
injecting `<img src="" onerror='alert("you were hacked")'>` via unsanitized
`post.content`, and state plainly: "Unless the markup is coming from a
completely trusted source, it is trivial to introduce an XSS vulnerability
this way." Official mitigations documented: only use it with markup from a
fully trusted or already-sanitized source (e.g. output of a trusted
Markdown-to-HTML renderer); construct the `{__html}` object as close as
possible to where the HTML is actually generated (not inline at the render
call site) so the trust boundary is auditable; never pass raw user input
directly.

[Source: https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components]
**Version-sensitive, critical**: On **December 3, 2025**, the React team
disclosed **CVE-2025-55182** (CVSS 10.0, Critical) — an **unauthenticated
remote code execution** vulnerability in how React Server Components
deserialize payloads sent to Server Function HTTP endpoints. Affected
packages: `react-server-dom-webpack`, `react-server-dom-parcel`,
`react-server-dom-turbopack` at versions **19.0, 19.1.0, 19.1.1, 19.2.0**.
The docs note apps can be vulnerable **even without explicitly implementing
a Server Function endpoint**, as long as they support RSC at all. Affected
downstream frameworks/bundlers named: Next.js, React Router, Waku,
`@parcel/rsc`, `@vitejs/plugin-rsc`, `rwsdk`. Fixed in **react 19.0.1,
19.1.2, 19.2.1**, plus framework-specific patched releases (e.g. multiple
patched Next.js minor lines from 14.2.35 through 16.1.5). The same
disclosure also covered **CVE-2025-55184** and **CVE-2025-67779** (High,
CVSS 7.5, Denial of Service) and **CVE-2025-55183** (Medium, CVSS 5.3,
Server Function source-code exposure, including any hardcoded secrets
embedded in that source — the docs explicitly note runtime secrets like
`process.env.SECRET` are *not* exposed by this one).

[Source: https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components]
**Version-sensitive**: Eight days later, on **December 11, 2025**, the team
disclosed that the **initial round of patches was incomplete**: a further
DoS issue, **CVE-2026-23864** (High, CVSS 7.5), remained, and the previously
issued Dec-3 patches for CVE-2025-55184/CVE-2025-67779/CVE-2025-55183 did
not fully close the gap. Newly vulnerable-until-patched versions listed:
**19.0.0–19.0.3, 19.1.0–19.1.3, 19.2.0–19.2.3**, across the same three
`react-server-dom-*` packages. **Actually-fixed versions: 19.0.4, 19.1.5,
19.2.4.** The post explicitly warns that apps already updated to the
Dec-3 patch versions (19.0.3 / 19.1.4 / 19.2.3) were **still vulnerable to
the newly disclosed issues** and needed to update again. It also clarifies
the RCE fix (CVE-2025-55182) from the first disclosure remained effective —
these follow-up CVEs are DoS/source-exposure only, not RCE. [Inference, not
confirmed in docs] Given this two-part, same-month disclosure pattern (an
incomplete first patch followed by a second, broader one), any app pinning a
specific React 19.x / `react-server-dom-*` version from before **December
11, 2025** should be treated as a likely-still-vulnerable target for a skill
that scaffolds RSC-based projects — this is a reasonable inference from the
two posts' content but is stated here as guidance synthesis, not a verbatim
docs claim.

[Source: https://react.dev/reference/react/Component] Error boundaries are
documented as **not** catching errors thrown inside event handlers,
asynchronous callbacks (`setTimeout`, `requestAnimationFrame`), during SSR,
or inside the error boundary's own `componentDidCatch`/render — a
security-adjacent robustness limitation (an uncaught error path in one of
these categories can crash the whole app rather than being contained) rather
than a strict "security" finding, but documented as a caveat under the same
reference page.

[Inference, not confirmed in docs] No dedicated, general-purpose "React
Security" guide (of the kind some frameworks publish, e.g. covering CSRF,
CSP, or dependency-supply-chain guidance) was located on react.dev during
this research; official security content found is limited to (a) the
`dangerouslySetInnerHTML` warning embedded in the API reference and (b) the
two RSC CVE disclosure blog posts above. **Unresolved: whether react.dev
publishes a standalone security-policy or responsible-disclosure page** (a
`SECURITY.md`-style page) — not found via the searches/fetches performed in
this research pass.

---

## 8. Performance

[Source: https://react.dev/blog/2025/10/07/react-compiler-1] **The React
Compiler** (stable/v1.0 as of **October 7, 2025**) is the current official
headline performance recommendation: a build-time Babel plugin
(`babel-plugin-react-compiler`) that automatically memoizes components and
values, including **conditional** memoization that manual `useMemo`/
`useCallback` cannot express. Documented, Meta-internal, production-measured
results cited in the release post: "initial loads and cross-page navigation
improved by up to 12%," "certain interactions up to 2.5× faster," with
memory usage reported neutral.

[Source: https://react.dev/reference/react/memo] **`memo`**: skips
re-rendering a component when its props are shallowly equal (`Object.is`
per-prop) to the previous render. Documented caveats: shallow comparison
means new object/array/function literals created fresh each parent render
defeat `memo` even when their contents are unchanged (fix: `useMemo` the
object, or pass primitive props instead); `memo` does **not** prevent
re-renders caused by the memoized component's *own* state changes or by
context values it consumes changing; it is explicitly documented as "never a
guarantee," only an optimization; a custom comparator function can be
supplied but the docs warn deep-equality comparators can become slower than
just re-rendering.

[Source: https://react.dev/reference/react/useMemo] **`useMemo`**:
recommended only for (a) calculations empirically shown to be slow via
`console.time` (rule-of-thumb threshold given: roughly ≥1ms measured, on a
representative/slower device, in production mode) with dependencies that
change rarely, (b) values passed into a `memo`-wrapped child, or (c) values
used as another Hook's dependency. Documented as **not a semantic
guarantee** — React may discard a memoized value (e.g. on file edit in dev,
or when a component suspends before its first successful mount) — so it must
never be relied on for correctness, only performance; `useState`/`useRef`
are the documented tools when a value must be guaranteed to persist.

[Source: https://react.dev/reference/react/Suspense] **Suspense boundary
reveal batching**: "React reveals suspended content at most once every
300ms, measured from the last reveal" so multiple boundaries resolving close
together appear together rather than popping in one at a time. [Source:
https://react.dev/blog/2025/10/01/react-19-2] **Version-sensitive (19.2)**:
this batching was extended to **SSR** specifically to align server/client
reveal behavior and prepare for `<ViewTransition>` support during SSR; React
uses a documented heuristic that **stops batching as the page nears the
~2.5s LCP threshold**, to avoid batching hurting Core Web Vitals.

[Source: https://react.dev/reference/react/Suspense] Documented granularity
guidance: "Don't put a Suspense boundary around every component. Suspense
boundaries should not be more granular than the loading sequence that you
want the user to experience" — over-splitting boundaries is called out as a
performance/UX anti-pattern, not just a code-organization concern.

[Source: https://react.dev/blog/2025/10/01/react-19-2] **New Chrome DevTools
Performance tracks (19.2)**: a "Scheduler Track" (shows React work by
priority — blocking vs. transition — plus event types and timing) and a
"Components Track" (shows component-tree render/effect timing) were added
specifically to help profile React apps in Chrome DevTools — see also §15
(Debugging).

[Source: https://react.dev/blog/2024/12/05/react-19] Resource preloading
APIs (`prefetchDNS`, `preconnect`, `preload`, `preinit`, all from
`react-dom`) are documented performance primitives introduced in React 19
for imperatively hinting the browser to fetch scripts/fonts/stylesheets/
connections ahead of when they're rendered.

---

## 9. Testing

[Source: https://react.dev/reference/react/act] React ships a helper,
**`act`**, whose documented purpose is to ensure all updates related to a
"unit" of test interaction have been processed and applied to the DOM before
assertions run, making test behavior closer to real browser behavior;
`act` usage is normally wrapped for you by testing libraries rather than
called directly. [Source: https://react.dev/blog/2024/04/25/react-19-upgrade-guide]
**Version-sensitive**: as of React 19, `act` moved from `react-dom/test-utils`
into the `react` package itself (`import {act} from 'react'`); a codemod
(`npx codemod@latest react/19/replace-act-import`) is provided for this
move.

[Source: https://react.dev/warnings/react-dom-test-utils] [Source:
https://react.dev/warnings/react-test-renderer] **Version-sensitive
deprecations**: React is deprecating **`react-test-renderer`**. The
documented rationale is that it "implements its own renderer environment
that doesn't match the environment users use, promotes testing
implementation details, and relies on introspection of React's internals."
The official recommended replacement is **`@testing-library/react`** (or
`@testing-library/react-native` for React Native). `react-dom/test-utils`
carries similar deprecation warnings pointing at the same replacement, apart
from `act` itself which was relocated rather than deprecated (previous
paragraph).

[Source: https://react.dev/blog/2025/10/07/react-compiler-1] In the context
of adopting the React Compiler, the docs recommend "following the Rules of
React and employing continuous end-to-end testing of your app so you can
upgrade the compiler with confidence" — i.e. official Compiler-adoption
guidance treats a solid pre-existing test suite as a prerequisite for safely
turning the Compiler on, rather than the Compiler substituting for tests.

[Inference, not confirmed in docs] No standalone, current "How to test React
components" tutorial/guide page was located on react.dev during this
research (the pre-2023 reactjs.org docs had a dedicated Testing Recipes /
Testing Environments guide; this research did not find an equivalent page
under the current react.dev information architecture). **Unresolved:
whether react.dev has a current first-party testing how-to guide beyond the
`act` reference page and the two deprecation-warning pages** — not
conclusively located; treat react.dev's testing documentation as thin
relative to other dimensions, with `@testing-library/react` presented as the
de facto recommended external tool rather than something react.dev teaches
end-to-end itself.

---

## 10. Deployment

[Source: https://react.dev/learn/start-a-new-react-project] Official
guidance funnels new projects toward a **framework**, each of which is
documented as supporting client-side rendering (CSR), single-page-app (SPA)
mode, and static-site generation (SSG), with **optional per-route SSR** and
**deployability to a plain static CDN with no server required** as a common
baseline capability across the recommended frameworks:
- **Next.js (App Router)** — `npx create-next-app@latest`; described as
  taking "full advantage of React's architecture" for full-stack apps, and
  as having the most complete implementation of Server Components +
  Suspense among the options; maintained by Vercel; deployable to
  Node.js/Docker hosting or as a static export.
- **React Router (v7)** — `npx create-react-router@latest`; paired with Vite
  to form a full-stack framework; maintained by Shopify; emphasizes standard
  Web APIs; ships ready-to-deploy templates for multiple runtimes/platforms.
- **Expo** — `npx create-expo-app@latest`; for universal Android/iOS/web
  apps sharing one native-capable codebase; free to build and submit to app
  stores, with optional paid Expo cloud services.
- Also named as emerging options: **TanStack Start** (beta; SSR, streaming,
  server functions, built on TanStack Router) and **RedwoodSDK**
  (pre-configured full-stack React framework).

[Source: https://react.dev/learn/build-a-react-app-from-scratch] For
projects that don't fit a framework, the docs describe building from
scratch with **Vite**, **Parcel**, or **RSbuild**, explicitly trading
flexibility for having to make your own decisions about routing, data
fetching, and other concerns a framework would otherwise standardize.

[Source: https://react.dev/blog/2024/12/05/react-19]
[Source: https://react.dev/blog/2025/10/01/react-19-2] Deployment-relevant
server APIs: `react-dom/server`'s streaming renderers
(`renderToPipeableStream` for Node, `renderToReadableStream` for Web
Streams/edge runtimes), and `react-dom/static`'s `prerender`/
`prerenderToNodeStream` (React 19) plus the 19.2 partial-prerendering
resume APIs (`resume`, `resumeToPipeableStream`, `resumeAndPrerender`,
`resumeAndPrerenderToNodeStream`) for splitting a page into a
pre-generated-at-build-time static shell and a request-time-resumed dynamic
portion.

[Inference, not confirmed in docs] React itself has no first-party CLI
deploy command or hosting product; "deployment" in the official docs is
entirely mediated through whichever framework/build tool a project uses —
consistent with React's position as a UI library rather than a full
application framework.

---

## 11. Migration

[Source: https://react.dev/blog/2024/04/25/react-19-upgrade-guide]
**Version-sensitive — React 18 → 19.** Documented step-by-step process:
(1) first upgrade to the final React **18.3** release specifically to
surface React-19-relevant deprecation warnings while still on 18's runtime
semantics; (2) run the provided codemods, individually or via the bundled
recipe `npx codemod@latest react/19/migration-recipe`
(`react/prop-types-typescript`, `react/19/replace-reactdom-render`,
`react/19/replace-string-ref`, `react/19/replace-act-import`, and others);
(3) for TypeScript projects, run `npx types-react-codemod@latest preset-19
./path-to-app` and the `react-element-default-any-props` codemod; (4)
manually update remaining string refs, `PropTypes`/`defaultProps` usage on
function components, legacy context, and test utilities; (5) install
`react@^19.0.0 react-dom@^19.0.0` (and matching `@types/*` packages) with
`--save-exact`.

Removed in React 19 (from the same upgrade guide): function-component
`propTypes`/`defaultProps` (→ TypeScript or ES6 default params); legacy
context (`contextTypes`/`getChildContext`) (→ `createContext`); string refs
on class components (→ callback refs); module-pattern factory components;
`React.createFactory`; `react-test-renderer/shallow` as a bundled export (→
install `react-shallow-renderer` directly, or migrate to Testing Library);
`ReactDOM.render`, `ReactDOM.hydrate`, `ReactDOM.unmountComponentAtNode`,
`ReactDOM.findDOMNode` (→ `createRoot`/`root.render`, `hydrateRoot`,
`root.unmount()`, and DOM refs, respectively); UMD builds (→ ESM CDN such as
`esm.sh`); several `unstable_*` APIs
(`unstable_flushControlled`, `unstable_createEventHandle`,
`unstable_renderSubtreeIntoContainer`, `unstable_runWithPriority`).

Breaking **behavior** changes documented for React 19 (not simply removed
APIs): uncaught render errors are no longer duplicated to the console and
instead routed to `window.reportError` (uncaught) or `console.error`
(caught by an error boundary), configurable via the new `onUncaughtError`/
`onCaughtError`/`onRecoverableError` root options; Suspense fallbacks commit
immediately rather than waiting on sibling subtrees; Strict Mode's second
pass now also re-invokes ref callbacks, and reuses `useMemo`/`useCallback`
results across the extra Strict Mode render.

Breaking **TypeScript** changes (React 19, from the same guide): `useRef()`
now requires an explicit argument (`useRef(undefined)` at minimum);
`ReactElement["props"]` changed from typed `any` to `unknown`; the global
`JSX` namespace was removed in favor of the scoped `React.JSX` namespace;
returning a value from a ref callback is now a type error (only `void` or a
cleanup function are allowed); `useReducer`'s recommended typing pattern
changed (best practice: no explicit generic type argument, letting it infer
from the reducer, or explicit `useReducer<State, [Action]>(reducer)` rather
than the old `useReducer<React.Reducer<State, Action>>(reducer)` form).

[Source: https://react.dev/blog/2022/03/08/react-18-upgrade-guide] React
also documents an equivalent upgrade guide for the **React 17 → 18**
transition (title confirmed via search: "How to Upgrade to React 18"); this
document was not fetched in full during this research pass. **Unresolved:
full content of the React 18 upgrade guide** — only the existence and title
were confirmed, not the detailed breaking-change list; if a future skill
needs React 17→18 migration specifics, that page should be fetched directly
rather than relying on this document.

[Source: https://react.dev/community/versioning-policy] As a general
migration/stability policy (not specific to any one version transition):
React's stable ("Latest") channel commits to standard semver, deprecated
APIs are generally kept working via companion packages (e.g. mixins support
was preserved via a separate `create-react-class` package rather than a hard
break) rather than deleted outright, development builds are used to surface
console warnings ahead of the next major release specifically so apps can
upgrade component-by-component, and `react-codemod` is the documented
general-purpose automated migration tool across versions, not just for the
19 transition.

[Inference, not confirmed in docs] No official "migrating from Vue/Angular/
[other framework] to React" guide was found in this research pass — React's
migration documentation is scoped to *upgrading within React* (major-version
transitions), not to migrating an app from a different UI library. This
absence is treated as expected/non-notable given the dimension's own
framing ("whichever the official docs actually cover").

---

## 12. Version information

[Source: https://react.dev/blog/2024/12/05/react-19] **Current major
version: React 19**, initially released **December 5, 2024** (preceded by an
RC shared April 2024).

[Source: https://react.dev/blog/2025/10/01/react-19-2] **Current minor:
19.2**, released **October 1, 2025**.

[Source: https://registry.npmjs.org (npm dist-tags, queried 2026-09-09)]
**Current patch, per npm's `latest` dist-tag: 19.2.8.** Other observed
dist-tags at query time: `next: 19.3.0-canary-...` (Canary channel tracking
an unreleased 19.3 line), `canary: 19.3.0-canary-...`, `experimental:
0.0.0-experimental-...`, `backport: 19.0.8` (a maintained backport line off
the 19.0.x branch, consistent with the security backports described in
§7 continuing past the original 19.0.4 fix).
[Source: https://github.com/react/react/releases (confirmed via search
result titles, not a full fetch)] GitHub release tags corroborate patch
activity into mid-2026: "Release 19.2.8 (July 21st, 2026)" and "Release
19.1.9 (July 21st, 2026)" were both returned as literal release titles in
search results.
[Inference, not confirmed in docs] **Unresolved: exact release date of
19.2.8 and whether any 19.2.5–19.2.7 patches shipped additional security
fixes** — this research did not fetch the full GitHub releases changelog or
CHANGELOG.md; the npm dist-tag and the two GitHub release-title search hits
are the only corroboration obtained for the precise current patch number.

[Source: https://react.dev/community/versioning-policy] React's stable
releases follow **semantic versioning** (`major.minor.patch`): patch
releases are reserved for critical bug/security fixes; minor releases carry
new features and non-critical fixes (documented as the most common release
type); major releases carry breaking changes. Historical major-release
cadence cited on that page: React 15→16 took about 1.5 years, 16→17 took
about 3 years — i.e. **major versions are explicitly infrequent by
design**, not on a fixed calendar cadence.

[Source: https://react.dev/community/versioning-policy] **Release channels**:
**Latest** (stable, semver, recommended for all user-facing apps); **Canary**
(tracks the `main` branch, roughly minor-release-equivalent stability,
hash-versioned e.g. `18.3.0-canary-388686f29-20230503`, intended for
frameworks/libraries to integrate not-yet-`Latest` features, must be pinned
in production, not intended for direct use in user-facing apps); and
**Experimental** (feature-flagged unreleased APIs, no stability guarantees
between releases, undocumented until near shipping, may never ship at all).
[Source: https://react.dev/blog/2023/05/03/react-canaries] (title confirmed
via search; not fetched in full) A dedicated blog post,
"React Canaries: Enabling Incremental Feature Rollout Outside Meta"
(2023-05-03), formalized this Canary-channel policy as a way for
non-Meta frameworks to adopt in-progress React features ahead of a
numbered stable release.

[Inference, not confirmed in docs] **No LTS (Long-Term-Support) concept** is
documented for React — the versioning policy page describes only the three
channels above and a general commitment to gradual, warning-preceded
breaking changes, with **no** stated support window (e.g. "React 18 will
receive security patches until X date") for any past major version.
**Unresolved: whether React 18.x or earlier majors still receive security
backports** as a matter of official policy — the observed `backport:
19.0.8` npm dist-tag shows an active backport line *within* 19.x, but no
docs page found states whether/how long 18.x itself continues to receive
fixes now that 19 is current.

[Source: https://react.dev/blog/2026/02/24/the-react-foundation] Governance
context relevant to future versioning: as of Feb 24, 2026 React's technical
governance is in a stated **transitional/provisional** state (a "provisional
leadership council" was still determining the long-term technical-decision
structure as of that post) — [Inference, not confirmed in docs] this makes
it plausible, though not documented, that release cadence or versioning
policy specifics could be revisited in the near term as governance
stabilizes; treat this document's §12 content as accurate to the research
date but watch for updates to `/community/versioning-policy` specifically.

---

## 13. Breaking changes

[Source: https://react.dev/blog/2024/04/25/react-19-upgrade-guide] The
authoritative breaking-changes list for the current major version is the
**React 19 Upgrade Guide**, fully detailed in §11 above (Migration) — removed
APIs (`ReactDOM.render`/`hydrate`/`unmountComponentAtNode`/`findDOMNode`,
string refs, legacy context, function-component `propTypes`/`defaultProps`,
module-pattern factories, `createFactory`, UMD builds, several
`unstable_*` internals), breaking behavior changes (error reporting via
`window.reportError`/`console.error` instead of duplicated dev-mode
re-throws, Suspense fallback commit timing, Strict Mode's extra ref-callback
invocation and `useMemo`/`useCallback` reuse), and breaking TypeScript
changes (`useRef()` argument now required, `ReactElement["props"]` typed as
`unknown` not `any`, global `JSX` namespace removed in favor of
`React.JSX`, ref-callback return-value type tightened, `useReducer` generic
usage changed). Section §11 above should be treated as the canonical
detail for this dimension; it is not repeated verbatim here to avoid
duplication.

[Source: https://react.dev/blog/2025/10/01/react-19-2] React **19.2**
(a *minor* release, per semver expected to be non-breaking for application
code) is explicitly documented as having made **no breaking changes**; the
`useId` prefix format change (`:r:`/`«r»` → `_r_`) is the one change in that
release with a realistic chance of breaking something (e.g. snapshot tests
asserting on generated IDs, or code relying on the old prefix format), but
the release notes frame it as a bug fix rather than list it under a
"Breaking Changes" heading.

[Source: https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components]
[Source: https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components]
The December 2025 security patches (19.0.1→19.0.4, 19.1.2→19.1.5,
19.2.1→19.2.4 for the `react-server-dom-*` packages specifically) are **not
described as breaking API changes** — they are security fixes distributed
as patch releases — but are included here because they are the most
consequential recent forced-upgrade events for any app using React Server
Components, and a skill scaffolding RSC projects should treat "pin an
unpatched pre-Dec-2025 React 19.x + `react-server-dom-*` combination" as
something to actively avoid.

---

## 14. Limitations

[Source: https://react.dev/reference/react/Suspense] Suspense has several
explicitly documented limitations: it does **not** detect data fetching
performed inside `useEffect` or an event handler — only `lazy()`, `use()`
on a promise, RSC-streamed data, certain resource loads (stylesheets with
`precedence`, fonts/images specifically during `<ViewTransition>` updates),
and CPU-bound work under the experimental `<Suspense defer>` prop activate a
boundary; React does **not preserve local state for a subtree that suspends
before its first successful mount** — on eventual success it retries
rendering that subtree "from scratch," discarding any state initialization
that happened before the suspend; a boundary that was showing content and
then **suspends again** re-shows its fallback unless the triggering update
was wrapped in `startTransition` (or came from `useDeferredValue`); and
layout Effects in a suspended-again subtree are torn down and re-fired when
content reappears, which any DOM-measuring layout Effect must account for.

[Source: https://react.dev/reference/rsc/server-components] React Server
Components' underlying bundler/framework-integration APIs are explicitly
**not** semver-stable within the React 19.x line (only the
application-facing RSC feature surface is), meaning framework authors, not
application authors, bear an ongoing compatibility burden — documented as a
structural limitation of RSC's current maturity level, not a bug.

[Source: https://react.dev/reference/react/Component] Class-component-only
capability: **error boundaries cannot currently be written as function
components** — this is an explicit, named gap in the function-component
API surface, with a third-party package (`react-error-boundary`) as the
documented workaround rather than a first-party function-component
equivalent.

[Source: https://react.dev/reference/react/memo] `memo`'s shallow-equality
comparison is a documented, inherent limitation (not a bug) — it cannot see
through object/array/function prop identity changes without extra
memoization on the caller's side, and even a correctly memoized component
still re-renders on its own state or consumed-context changes.

[Source: https://react.dev/reference/react/useMemo] `useMemo`'s cache is
explicitly documented as **not a correctness guarantee**: React may discard
a memoized value (component file edited in dev; component suspends before
first mount; the docs note React "may add more" cache-invalidation triggers
in the future, e.g. for virtualized-list items scrolled out of view) —
so it must never be used as a substitute for `useState`/`useRef` when a
computation's result must be guaranteed to persist.

[Inference, not confirmed in docs] As a UI-rendering library rather than an
application framework, React has no first-party router, no first-party data
layer/cache, and no first-party global state-management primitive beyond
`useState`/`useReducer`/Context — this is evident throughout the docs
(routing and full-stack data-fetching guidance is delegated entirely to
third-party frameworks per §10/§16) but no single page states "React does
not include X" as an enumerated limitations list; it is inferred from the
consistent framing across the Learn and framework-recommendation pages.

---

## 15. Debugging

[Source: https://react.dev/learn/react-developer-tools] **React Developer
Tools** is the official primary debugging tool: a browser extension
(Chrome, Firefox, Edge official store links given) with a **Components**
panel (inspect the component tree, view/edit props and state live) and a
**Profiler** panel (identify performance problems). For browsers without
extension support (e.g. Safari) or non-browser environments, the docs
describe installing the standalone `react-devtools` npm package globally and
connecting via a `<script src="http://localhost:8097"></script>` tag. For
React Native, **React Native DevTools** (built into React Native 0.76+) is
documented as including all React DevTools functionality plus native
element highlighting/selection; earlier React Native versions use the same
standalone `react-devtools` package method.

[Source: https://react.dev/reference/react/StrictMode] **`<StrictMode>`**
is a development-only, no-production-impact debugging aid that: double-
invokes pure functions (component bodies, `useState`/`useReducer`
initializers, `useMemo` calculators) to surface impurity bugs immediately
rather than after they've caused a real issue; runs an extra
setup→cleanup→setup cycle for both Effects and ref callbacks to surface
missing-cleanup bugs (memory leaks, duplicate subscriptions) immediately;
and warns on deprecated APIs (e.g. legacy `UNSAFE_` class lifecycle
methods). The docs state there is **no way to selectively opt a subtree out**
of StrictMode's checks once wrapped in `<StrictMode>`, and recommend
wrapping the whole app, especially for new projects.

[Source: https://react.dev/errors] Production builds strip full error text
to reduce bundle size, surfacing only a numeric "Minified React error #N"
with a link to react.dev's own **Minified Error Decoder**
(`react.dev/errors`, with per-code pages like `react.dev/errors/130`) which
reconstructs the full development-mode error message and any interpolated
arguments from the code + URL query args.

[Source: https://react.dev/blog/2025/10/01/react-19-2] **Version-sensitive
(19.2)**: two new custom Chrome DevTools Performance-panel tracks were
added specifically for React debugging/profiling — a **Scheduler Track**
(shows React's internal work broken out by priority — blocking vs.
transition — plus event types and per-render timing) and a **Components
Track** (shows per-component render/effect timing across the tree) — aimed
at identifying performance bottlenecks directly inside the standard browser
profiler rather than only in the separate React DevTools Profiler panel.

[Source: https://react.dev/blog/2024/12/05/react-19] React 19 is documented
as improving **hydration-mismatch error reporting**: a single, clearer error
with an explicit diff of what didn't match between server and client
render output, replacing noisier/duplicated prior messaging; and
consolidating duplicate error logging generally via the new
`onCaughtError`/`onUncaughtError`/`onRecoverableError` root callbacks (see
§3).

[Source: https://react.dev/learn/react-compiler/debugging] A dedicated
**React Compiler debugging/troubleshooting guide** exists (page located via
search; title and existence confirmed, full content not fetched in this
research pass) covering distinguishing compiler-time errors from
runtime issues and common breaking patterns. **Unresolved: detailed content
of the React Compiler debugging guide** — flagged for direct fetch if a
future skill needs Compiler-specific debugging steps beyond what's captured
in §4/§8 above.

---

## 16. Integration

[Source: https://react.dev/learn/typescript] **TypeScript** is documented as
a first-class, officially supported integration (see §4 for setup detail);
the docs link out to TypeScript's own Handbook and release notes as the
authoritative TS reference, and to the community "React TypeScript
Cheatsheet" as a supplementary (non-official) resource, explicitly
distinguishing "official" from "community" sources on that page itself.

[Source: https://react.dev/learn/start-a-new-react-project] **Framework
integration** is the dominant officially-recommended integration path:
**Next.js**, **React Router v7**, and **Expo** are the three primary named
frameworks (see §10 for detail on each), with **TanStack Start** and
**RedwoodSDK** named as emerging/beta options. [Source:
https://react.dev/learn/typescript] The TypeScript page separately links to
each major framework's own TypeScript docs (Next.js, Remix, Gatsby, Expo),
implying Remix and Gatsby are also treated as within the recognized
framework ecosystem even though they weren't listed among the primary three
"start a new project" recommendations at the fetch date — [Inference, not
confirmed in docs] this likely reflects Remix's functionality having
migrated into React Router v7 and Gatsby's reduced prominence, but the docs
do not state this transition explicitly on the pages fetched.

[Source: https://react.dev/reference/rsc/server-components] **Bundler/RSC
integration**: Server Components require a compatible bundler integration
(`react-server-dom-webpack`, `react-server-dom-parcel`,
`react-server-dom-turbopack` are the three named packages, corroborated
independently by the security-advisory posts in §7); these are the
lower-level, non-semver-stable integration points frameworks build on.

[Source: https://react.dev/blog/2025/10/07/react-compiler-1] **Build-tool
integration for the React Compiler**: ships as a **Babel plugin**
(`babel-plugin-react-compiler`); pre-wired into `create-vite`,
`create-next-app`, and Expo SDK 54+ scaffolds for new projects; a **SWC**
integration is implied by Next.js's usual reliance on SWC but not
independently confirmed on the pages fetched in this research —
**Unresolved: whether the React Compiler has an official first-party SWC
(non-Babel) integration**, versus relying on frameworks to bridge Babel-only
tooling into SWC-based pipelines.

[Source: https://react.dev/reference/react-compiler/compiling-libraries]
A dedicated guide exists for **library authors** shipping pre-compiled
library code with the Compiler (page located via search; not fetched in
full in this pass) — **Unresolved: full content of the library-compilation
guide.**

[Source: https://react.dev/reference/react/act]
[Source: https://react.dev/warnings/react-dom-test-utils] **Testing-library
integration**: `@testing-library/react` (and `@testing-library/react-native`)
are the officially recommended external testing integrations, referenced
directly from React's own deprecation-warning pages for `react-test-renderer`
and `react-dom/test-utils` (see §9).

[Source: https://react.dev/learn/react-developer-tools] **Browser
integration**: React Developer Tools ships as an extension for Chrome,
Firefox, and Edge specifically (official store links given for those three);
other browsers (e.g. Safari) require the standalone npm-distributed
`react-devtools` app connected via a manually-inserted script tag, which is
a materially different (and more manual) integration path than the
extension-based one.

---

## 17. Production considerations

[Source: https://react.dev/reference/react/StrictMode] Development-only
behaviors (double-render, double-Effect, double-ref-callback invocation)
are explicitly documented as **stripped in production builds** — StrictMode
has zero production runtime cost, so it is safe (and recommended) to leave
wrapping the whole app permanently rather than conditionally applying it.

[Source: https://react.dev/errors] Production builds ship **minified error
messages** (numeric codes only) specifically to reduce bytes over the wire;
`react.dev/errors` is the documented, official channel for decoding a
production error code back into its full development-mode message — this
is presented as an intentional production/development tradeoff, not a bug.

[Source: https://react.dev/reference/react/Component] **Error boundaries**
are the documented production resilience mechanism for render-time errors —
catching a subtree crash and rendering a fallback instead of unmounting the
whole app — but with explicitly limited coverage (does not catch event
handler errors, async callback errors, SSR errors, or errors inside the
boundary's own catch logic; see §7/§14). [Inference, not confirmed in docs]
Because error boundaries can't be written as function components and don't
cover event-handler/async errors, a production-grade app is implied to need
**both** an error boundary (for render-time crashes) **and** manual
try/catch or a global error handler (for event handlers and async code) —
this composite recommendation is a synthesis across documented facts, not a
single docs statement.

[Source: https://react.dev/blog/2024/12/05/react-19] The new
`onCaughtError`/`onUncaughtError`/`onRecoverableError` root options
(`createRoot`/`hydrateRoot`) are the documented React-19-era mechanism for
routing all render errors, caught or not, to a production error-reporting
service (e.g. Sentry-style tooling) with a single, non-duplicated log path,
replacing the previous behavior of errors being both re-thrown and
separately dev-console-logged.

[Source: https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components]
[Source: https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components]
For any production app that uses **React Server Components**, staying
current on `react`, `react-dom`, and the specific `react-server-dom-*`
bundler package is documented as a **hard production requirement**, not an
optional best practice, given the December 2025 critical-RCE and follow-up
DoS/source-exposure disclosures; the docs explicitly warn against relying on
a hosting provider's mitigation as a substitute for actually upgrading (see
§7 for exact affected/fixed version ranges).

[Source: https://react.dev/reference/rsc/server-components] For RSC-based
production deployments specifically, the docs' explicit non-semver-stability
warning for the underlying bundler APIs (§3/§14) is itself a production
consideration: teams are told to **pin an exact React version** for RSC
bundler/framework integration code rather than using a caret/tilde range, to
avoid unannounced breakage between React 19 minor releases at that layer.

[Source: https://react.dev/blog/2025/10/01/react-19-2] The documented
Core-Web-Vitals-aware Suspense-batching heuristic (batching boundary reveals
up to 300ms, but backing off as the page approaches the ~2.5s LCP threshold)
is presented as a production performance/UX tuning consideration built into
React itself, requiring no application-level configuration.

[Source: https://react.dev/blog/2025/02/14/sunsetting-create-react-app] Any
production app still on **Create React App** is implicitly flagged as being
on an unsupported, no-longer-recommended toolchain as of Feb 14, 2025 —
the sunsetting post directs such apps toward migrating to a framework or to
Vite/Parcel/RSbuild, which is a relevant production-hygiene item for a
skill assessing an existing codebase's setup.

[Source: https://react.dev/blog/2026/02/24/the-react-foundation] At an
organizational level, React's move to Linux-Foundation-hosted, multi-vendor
governance (Feb 2026, see §0/§12) is a production-relevant supply-chain/
governance fact for risk-averse organizations evaluating long-term
dependency risk on React, though it does not change any technical API or
runtime behavior documented elsewhere in this file.

---

## Summary of Unresolved items

- Whether current react.dev docs use the term "Fiber" anywhere for React's
  internal architecture (§2).
- Full content of the React 17→18 upgrade guide
  (`react.dev/blog/2022/03/08/react-18-upgrade-guide`) — only title/existence
  confirmed (§11).
- Exact release date and any additional patch-level fix content for React
  19.2.8 beyond what npm dist-tags and GitHub release-title search snippets
  show (§12).
- Whether React 18.x (or earlier majors) receives an official, time-bounded
  security-backport commitment now that 19.x is current — no LTS/support-
  window policy was found (§12).
- Whether react.dev publishes a standalone security-policy/responsible-
  disclosure page beyond the two RSC CVE blog posts (§7).
- Detailed content of the React Compiler debugging/troubleshooting guide at
  `/learn/react-compiler/debugging` (§15).
- Whether the React Compiler has an official first-party SWC integration,
  versus Babel-only with framework-level bridging (§16).
- Full content of the library-compilation guide at
  `/reference/react-compiler/compiling-libraries` (§16).
- Whether react.dev currently hosts any first-party, end-to-end "how to test
  a React component" tutorial beyond the `act` reference page and the two
  testing-tool deprecation-warning pages (§9).

## Sources consulted (official only)

All citations above are to `react.dev` pages (react.dev/learn/*,
react.dev/reference/*, react.dev/blog/*, react.dev/community/*,
react.dev/warnings/*, react.dev/errors, react.dev/versions), plus the npm
registry's dist-tags for the `react` package as a corroborating, official
distribution-channel source for current version numbers, and GitHub
release-title search snippets from `github.com/react/react/releases` used
only to corroborate a patch-version date already implied by npm, not as a
standalone citation for any claim.
