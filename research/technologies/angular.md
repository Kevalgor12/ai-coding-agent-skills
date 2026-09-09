# Angular

Deep reference research on **Angular**, Google's TypeScript-based web
application framework. Primary source is the official documentation site
**angular.dev**, supplemented by the official `angular.dev` blog
(`blog.angular.dev`) and the official `angular/angular` GitHub repository
(source of truth for the CHANGELOG). Research date: **2026-09-09**.

## 0. Canonical docs host and how to read this document

[Source: https://angular.dev/overview] The canonical, current documentation
host is **https://angular.dev**. This is a change worth flagging explicitly
per the task's instructions: historically Angular's docs lived at
`angular.io`; **angular.dev** is now the site the framework's own pages,
blog, and update tooling (`update.angular.io` redirects into
`angular.dev/update-guide`) all point to. [Inference, not confirmed in docs]
Legacy version-pinned docs subdomains such as `v17.angular.io` still appear
in search results and presumably still resolve, but they were not used as
citations in this document except where explicitly noted as a legacy/search
artifact.

[Source: https://angular.dev/reference/releases] This document is based on
docs current as of **Angular v22** (specifically build "v22.1.5" per the
angular.dev site footer at fetch time), the latest major version as of the
research date. Angular has an unusually fast-moving current release
(v22.1.x and v22.2.0-next prereleases were shipping weekly as of this
research), so **version-sensitive claims are tagged throughout** — this
framework changed its major-release cadence, its default change-detection
strategy, its default test runner, and stabilized several previously
experimental APIs all within the v20-v22 window (roughly May 2025-June
2026), so version tagging matters more than usual here.

A general framing note: [Source: https://blog.angular.dev/announcing-angular-v22-c52bb83a4664]
Angular's own v22 announcement describes v22 as the release where the
framework's "signal-first" direction — begun with Signals in v16/v17 —
"stops being 'the future' and becomes the default," with several
experimental/developer-preview APIs (Signal Forms, Angular ARIA) graduating
to stable and OnPush becoming the default change-detection strategy for new
components. Readers should treat idioms from pre-v20 Angular material
(NgModules-first, decorator-based `@Input`/`@Output`, Zone.js-based change
detection) as legacy-but-supported rather than current best practice.

---

## 1. Core concepts

[Source: https://angular.dev/overview] Angular is described as providing "a
broad suite of tools, APIs, and libraries to simplify and streamline your
development workflow," maintained by "a dedicated team at Google," intended
to build apps that "scale with both the size of your team and the size of
your codebase."

[Source: https://angular.dev/guide/components] **Components** are the basic
building block: every component requires (1) a TypeScript class with
behavior, (2) an HTML template controlling what renders, and (3) a CSS
selector defining how it's used in other templates. The `@Component`
decorator attaches this metadata to the class.

[Source: https://angular.dev/guide/components] **Standalone by default**:
[Version-sensitive] "In Angular versions before 19.0.0, the `standalone`
option defaults to `false`" — meaning components required registration in an
`NgModule`. As of Angular 19+, components are standalone by default and can
be added directly to another component's `imports` array without an
`NgModule`. Older components may still explicitly set `standalone: false`.

[Source: https://angular.dev/guide/components] Components compose into a
**tree structure**: parent components import and reference child components
in their templates, and this hierarchy matters for dependency injection and
queries.

[Source: https://angular.dev/guide/signals] **Signals**: "a wrapper around a
value that notifies interested consumers when that value changes." Signals
let Angular "granularly track how and where your state is used throughout an
application, allowing the framework to optimize rendering updates." Core
APIs: `signal()` creates a writable signal (read by calling it as a
function, written via `.set()`/`.update()`); `computed()` creates a
read-only, **lazily evaluated and memoized** derived signal; `effect()` runs
side effects when read signals change (there is also `afterRenderEffect()`
for post-render timing). Reading a signal inside a template, a `computed()`,
an `effect()`, or a `linkedSignal`/`resource()` establishes a live
dependency ("reactive context").

[Source: https://angular.dev/guide/di] **Dependency Injection (DI)**: "a
design pattern you use to organize and share code across your application by
supplying dependencies to a class instead of creating them inside it."
Services are TypeScript classes made injectable; the `inject()` function is
the primary mechanism for requesting a dependency and can be used in class
field initializers or constructor bodies of components, directives,
services, and route guards. Angular supports hierarchical injectors (scoping
providers at different levels of the app).

[Version-sensitive, Angular v22] [Source: https://angular.dev/guide/di/creating-and-using-services]
Angular v22 introduces a second, more ergonomic decorator for injectable
classes: **`@Service()`**, positioned as "a modern, ergonomic decorator"
alongside the traditional `@Injectable()`. Example from the docs:
```ts
@Service()
export class BasicDataStore {
  private data: string[] = [];
  addData(item: string): void { this.data.push(item); }
}
```
versus the traditional `@Injectable({ providedIn: 'root' })`. The docs note
`@Service()` is particularly suited to services that use the `inject()`
function rather than constructor-based injection; both decorators support
`providedIn: 'root'` semantics (singleton, tree-shakable, auto-registered).
Unresolved: the exact default `providedIn` behavior of bare `@Service()`
(the WebFetch summary implied it defaults to root-provided, but this was not
independently confirmed against the raw page markup).

[Source: https://angular.dev/guide/templates] **Templates**: "a chunk of
HTML" enhanced with Angular-specific syntax. Angular compiles templates into
JavaScript to build an internal understanding of the application, enabling
automatic rendering optimizations. Attributes with special characters
(`[]`, `()`) have special meaning: property binding and event binding.
Templates also support two-way binding, pipes, content projection
(`ng-content`), template fragments (`ng-template`), and grouping
(`ng-container`).

[Source: https://angular.dev/guide/templates] `@`-prefixed **control flow**
syntax (`@if`, `@for`, `@switch`) is the current template control-flow
mechanism (see §5/§6 for how this relates to the older `*ngIf`/`*ngFor`
structural directives).

[Source: https://angular.dev/guide/routing] **Angular Router**
(`@angular/router`) is "the official library for managing navigation," built
around three concepts: Routes (URL → component mapping), Outlets
(placeholders where routed components render), and Links (navigation without
full page reloads). Supports nested routes, programmatic navigation, route
parameters/queries/wildcards, view-transition effects, guards, resolvers,
and `ActivatedRoute` for reading route info.

[Source: https://angular.dev/guide/forms] **Forms**: three systems now
coexist — Reactive Forms (`FormControl`/`FormGroup`/`FormArray`, explicit
object-model access, synchronous data flow, more testable/scalable),
Template-Driven Forms (directive-driven via `NgModel`, asynchronous data
flow, simpler for basic cases), and the newer Signal Forms (see §11/§13).
`ControlValueAccessor` bridges `FormControl` instances to DOM elements in
both reactive and template-driven forms.

[Source: https://angular.dev/guide/hydration] **Hydration**: "the process
that restores the server-side rendered application on the client," reusing
existing DOM rather than re-rendering from scratch. **Event Replay** (stable
since [Version-sensitive] v18 per search-corroborated docs reference — see
§9) captures user interactions that occur before hydration completes and
replays them afterward; it is automatically enabled when incremental
hydration is active.

## 2. Architecture

[Source: https://angular.dev/overview] Angular ships an integrated set of
architectural layers: a component/template rendering layer with the Signals
reactivity model and "compile-time optimizations," a DI system, a
feature-rich router, SSR/SSG with hydration, a CLI (project setup "in under
a minute"), and DevTools (component tree inspector, DI tree view, custom
performance profiler).

[Source: https://angular.dev/overview] The modern build pipeline uses
**Vite and esbuild** "for fast compilation of large codebases" — this is a
shift from the older Webpack-based `@angular-devkit/build-angular` toolchain
of earlier major versions. [Inference, not confirmed in docs] The exact
version this became the CLI default was not directly confirmed on the
overview page; it is widely reported elsewhere (non-official sources) as
having landed progressively across v17-v20, so treat the specific version
boundary as unresolved.

[Source: https://angular.dev/guide/ngmodules/overview] **NgModules vs.
standalone architecture**: An `NgModule` is a class decorated with
`@NgModule` that (a) declares components/directives/pipes and (b) configures
DI providers, historically via `forRoot()`/`forChild()` patterns for
root-level provider registration. "The Angular team recommends using
standalone components instead of NgModule for all new code." NgModules are
**not deprecated** and remain fully supported — the framework's documented
position is that they matter mainly for understanding/maintaining existing
(pre-standalone) codebases, not for new architecture decisions.

[Source: https://angular.dev/guide/zoneless] **Change detection
architecture**: Angular historically relied on **Zone.js**, a library that
monkey-patches browser APIs (timers, event listeners, promises) to detect
when app state might have changed and trigger a change-detection pass.
[Version-sensitive] **Zoneless change detection is stable and the default in
Angular v21+**; in v20 it required opting in via
`provideZonelessChangeDetection()` (renamed from the "Experimental"-tier
`provideExperimentalZonelessChangeDetection()`, which became "Developer
Preview"-tier `provideZonelessChangeDetection` as of the v20.0.0 breaking
changes — see §13). Under zoneless, Angular relies on explicit
notifications from core APIs (signal writes, `markForCheck`, async pipe,
etc.) rather than patched global APIs to know when to re-render. Migrating
off Zone.js means removing `zone.js` from `angular.json` polyfills and
`npm uninstall zone.js`.

[Version-sensitive, Angular v22] [Source: https://raw.githubusercontent.com/angular/angular/main/CHANGELOG.md
(v22.0.0 entry)] As of v22, components with an **undefined `changeDetection`
property now default to `OnPush`** (previously "Default"/Zone-checked
strategy); the old default can be retained by explicitly specifying
`changeDetection: ChangeDetectionStrategy.Eager`. This is a formal breaking
change in the v22.0.0 changelog, not just a soft recommendation.

[Source: https://angular.dev/guide/ssr] **Rendering architecture** offers
three modes configured per-route via `ServerRoute`/`RenderMode` objects in
`app.routes.server.ts`: **Server** (SSR — render per request), **Client**
(CSR — the historical Angular default), and **Prerender** (SSG — static HTML
generated at build time). `outputMode: 'static'` in `angular.json` produces
a fully static build (no Node.js server needed) for static hosting.

[Source: https://angular.dev/reference/configs/workspace-config]
**Workspace architecture**: an `angular.json` file at the workspace root
configures the CLI/build tooling. Top-level keys: `version`,
`newProjectRoot` (default `projects`), `cli`, `schematics` (defaults for
`ng generate`), and `projects` (per-app/library config). Each project
defines "architect" targets (`build`, `serve`, `test`, `e2e`, `lint`,
`extract-i18n`), each with a `builder` package reference, default `options`,
and named `configurations` (e.g. `production`). Default builders live in
`@angular-devkit/build-angular`; default schematics in
`@schematics/angular`.

## 3. APIs

[Source: https://angular.dev/api] The official API reference is organized
by package: core packages `@angular/core`, `@angular/common`,
`@angular/forms`, `@angular/router`; platform packages
`@angular/platform-browser`, `@angular/platform-server`,
`@angular/platform-browser-dynamic`; specialized packages
`@angular/animations`, `@angular/elements`, `@angular/service-worker`,
`@angular/localize`, `@angular/ssr`, `@angular/cdk`; plus per-package testing
utility modules.

[Source: https://angular.dev/api] Every API entry is labeled with a
**stability badge** — Stable (default/unmarked), **Developer Preview**,
**Experimental** ("EXP"), or **Deprecated** — and a type marker (Block,
Class, Const, Directive, Element, Enum, Function, Interface, Pipe, Module,
Type Alias, Initializer API). [Inference, not confirmed in docs] This
badge system is the documented mechanism for signaling API stability
per-symbol, which is the correct place to check before depending on any
specific Angular API in a skill or generated code — more reliable than
inferring stability from a guide page's prose alone.

[Source: https://angular.dev/guide/signals/resource] **`resource()`**:
incorporates async data into signal-based code while keeping synchronous
read access; typical shape: `resource({ params: () => (...), loader:
({params}) => fetchData(params) })`. Returns status signals
(`isLoading`, `error`, `status`, `value`). [Source: https://blog.angular.dev/announcing-angular-v22-c52bb83a4664]
Per the WebSearch-derived summary of Angular's own v22 announcement,
`resource()`/`httpResource()` were "promoted to developer stable" as part
of v22's signal-first push — cross-checked against the API reference
fetch, which showed both APIs presented without an experimental/preview
badge in the v22 docs.

[Source: https://angular.dev/guide/signals/resource] **`httpResource()`**: a
wrapper around `HttpClient` exposing request status and the resolved
response as signals; e.g. `httpResource(() => \`/endpoint/${id()}\`)`.
Requests still flow through Angular's HTTP interceptor chain. Supports
reactive params, status signals, and abort-signal-based cancellation.

[Source: https://angular.dev/ecosystem/rxjs-interop] **`@angular/core/rxjs-interop`**
bridges signals and RxJS: `toSignal()` subscribes to an Observable
immediately (side effects included) and exposes its latest value as a
signal, with options `initialValue`, `requireSync` (for sources that emit
synchronously, e.g. `BehaviorSubject`), and `equal` (custom equality);
errors from the source Observable are thrown when the signal is read, and
completion freezes the signal at its last value. `toObservable()` does the
inverse via an internal `effect()`. `rxResource()` is a `resource()`
variant whose `stream` function returns an Observable. `takeUntilDestroyed()`
auto-unsubscribes tied to a component/service's `DestroyRef`.

[Source: https://angular.dev/guide/http] **`HttpClient`**
(`@angular/common/http`): typed response values, streamlined error
handling, request/response interceptors, and dedicated testing utilities.
Provisioned via `provideHttpClient(...)` with feature functions such as
`withXhr`, `withFetch` (see §13 for its v22 deprecation), and XSRF
configuration functions (see §7).

[Source: https://angular.dev/guide/templates/defer] **`@defer`** blocks (a
template-level API, not a TS API) reduce initial bundle size by deferring
loading of non-critical template content. Trigger types via `on`: `idle`
(default), `viewport`, `interaction` (click/keydown), `hover`
(mouseover/focusin), `immediate`, `timer`. A `when` trigger accepts an
arbitrary expression and fires once when it becomes truthy. Optional
prefetch triggers preload JS ahead of display. Supporting blocks:
`@placeholder` (shown before trigger; its own dependencies load eagerly),
`@loading` (with `after`/`minimum` timing params to avoid flicker), and
`@error`. **Only standalone** components/directives/pipes are eligible to
be deferred — NgModule-declared dependencies inside a `@defer` block still
load eagerly.

[Source: https://angular.dev/guide/di/creating-and-using-services]
`inject(SomeService)` is the documented idiomatic way to obtain a
dependency, shown in the docs as a class-field initializer:
`dataStore = inject(BasicDataStore);` — positioned ahead of constructor
parameter injection in the style guide (see §5).

## 4. Configuration

[Source: https://angular.dev/reference/configs/workspace-config] The
primary configuration surface is **`angular.json`** at the workspace root
(schema keys detailed in §2 above: `projects`, per-project `architect`
targets `build`/`serve`/`test`/`e2e`/`lint`/`extract-i18n`, each with
`builder`, `options`, `configurations`). Common `build` options include
`assets`, `styles`, `scripts` (global CSS/JS), `optimization`, `sourceMap`,
and `outputPath`.

[Source: https://angular.dev/guide/ssr] SSR/static-site configuration is
expressed via **`app.routes.server.ts`**, using `ServerRoute` objects with a
`renderMode` of `Server`, `Client`, or `Prerender` per route, and via the
`outputMode: 'static'` `angular.json` build option for fully static output.

[Source: https://angular.dev/guide/http] HTTP client configuration is
provider-based: `provideHttpClient()` composed with feature functions
(`withXhr`, `withFetch`, `withXsrfConfiguration({...})`,
`withNoXsrfProtection()` — see §7).

[Source: https://angular.dev/guide/zoneless] Change-detection configuration:
`provideZonelessChangeDetection()` (opt-in prior to v21; default from v21
onward) vs. Zone.js-based `provideZoneChangeDetection(...)`, plus removal of
`zone.js` from the `polyfills` array in `angular.json` to fully drop Zone.js.

[Source: https://angular.dev/best-practices/security] Trusted Types /
CSP-related configuration: nonces can be supplied via workspace config
(`autoCsp`), the `ngCspNonce` template attribute, or the `CSP_NONCE`
injection token (see §7).

[Source: https://angular.dev/reference/versions] Engine/tooling
configuration constraints (peer-dependency style, not a config file per se)
— see the version compatibility table in §12.

## 5. Recommended patterns

[Source: https://angular.dev/style-guide] Angular publishes an official
style guide. Key documented **DO** patterns, contrasted with documented
**AVOID** patterns:

| Concern | DO | AVOID |
|---|---|---|
| Class/style bindings | `[class.admin]="isAdmin"` | `[ngClass]`, `[ngStyle]` directives |
| Event handler naming | `(click)="saveUserData()"` (name after what it does) | `(click)="handleClick()"` (name after the trigger) |
| Dependency injection | `inject()` function | Constructor-parameter injection |
| Angular-initialized properties | Mark `readonly` | Reassigning Angular-set properties |
| Template-only class members | `protected` | Public members not needed outside the template |
| Lifecycle hooks | Implement the corresponding TS interface (e.g. `OnInit`) | Omitting the interface |

[Source: https://angular.dev/style-guide] **File naming**: hyphen-separate
words in filenames (e.g. `user-profile.ts`); test files end in `.spec.ts`;
filenames should match the TS identifiers they contain; a component's
TS/template/style files should share a base name.

[Source: https://angular.dev/style-guide] **Directive selectors**: use
camelCase attribute selectors (e.g. `[mrTooltip]`).

[Source: https://angular.dev/style-guide] **Project structure**: all UI code
under `src`; bootstrap in `main.ts`; group closely related files in the
same directory; organize by **feature area, not by code type** (the guide
explicitly says to avoid `components/`, `directives/`-style folders), aiming
for "one concept per file."

[Source: https://angular.dev/style-guide] **Single responsibility**: keep
components/directives focused on presentation; move validation/data
transforms into separate functions; avoid complex logic inline in templates
(prefer computed/derived properties); keep lifecycle-hook bodies simple by
delegating to named helper methods.

[Source: https://angular.dev/guide/zoneless] Recommended pairing:
**OnPush + Signals** — OnPush is "recommended but not required," and
signals are the key notification mechanism that keeps OnPush components
correctly updated without Zone.js.

[Source: https://angular.dev/best-practices/images] Use the
**`NgOptimizedImage`** directive (`ngSrc` in place of `src`, explicit
`width`/`height`, and a `priority` attribute on the LCP image) rather than
plain `<img>` tags for image-heavy pages — it auto-generates responsive
`srcset`, defaults non-priority images to `loading=lazy`, and integrates
with major CDN loaders (Cloudinary, Imgix, ImageKit, Netlify, Cloudflare) or
custom loaders.

[Source: https://angular.dev/guide/templates/defer] Use `@defer` (with
appropriate triggers/placeholders) to keep initial bundles small for
non-critical, standalone-only UI.

[Source: https://angular.dev/reference/migrations] Angular ships **13
documented automated migration schematics** (run via `ng generate`) for
incrementally adopting recommended modern patterns on existing code:
standalone components, `@if`/`@for`/`@switch` control flow, `inject()`,
lazy-loaded routes, signal inputs, the `output()` function, signal queries,
unused-import cleanup, self-closing tags, `NgClass`→class bindings,
`NgStyle`→style bindings, `RouterTestingModule` modernization, and
`CommonModule`→standalone-directive imports. [Inference, not confirmed in
docs] The presence of dedicated migrations for each of these is itself
strong evidence of what the Angular team currently considers "recommended
pattern" vs. legacy — a migration schematic effectively encodes an official
before/after pattern pair.

## 6. Anti-patterns

[Source: https://angular.dev/style-guide] The style guide's DO/AVOID table
(reproduced in §5) is the primary documented source of explicit
anti-patterns: using `[ngClass]`/`[ngStyle]` instead of native class/style
bindings; naming event handlers after the DOM event rather than the
resulting action; constructor-parameter DI instead of `inject()`;
reassigning properties Angular itself sets; leaving template-only class
members `public`; implementing lifecycle-hook methods without declaring the
corresponding interface.

[Source: https://angular.dev/style-guide] Anti-pattern by omission: putting
non-trivial logic (validation, data transformation) directly in templates
rather than factoring it into named methods/computed values — the guide
frames "avoid overly complex logic in templates" as a corollary of the
single-responsibility principle.

[Source: https://angular.dev/style-guide] Anti-pattern by omission:
organizing a project by code type (`components/`, `directives/`,
`services/` folders) instead of by feature — the guide explicitly says to
avoid this.

[Source: https://angular.dev/best-practices/security] Security-flavored
anti-pattern: using `DomSanitizer.bypassSecurityTrust*` methods without
justification/review — the docs explicitly warn these "introduce security
vulnerabilities if the trusted value is malicious" and call for auditing any
code path that uses them (see §7 for full detail).

[Inference, not confirmed in docs] The framework's continued investment in
one-click migration schematics away from NgModules, decorator-based
`@Input`/`@Output`, `*ngIf`/`*ngFor`, `NgClass`/`NgStyle`, and constructor
injection (§5) implies the Angular team now treats each of these *patterns
themselves* as soft anti-patterns for new code, even though none of them are
formally deprecated/removed — this inference is drawn from the existence and
framing of the migration tooling, not from an explicit "anti-patterns" page,
since angular.dev does not appear to publish a page titled that way.

## 7. Security

[Source: https://angular.dev/best-practices/security] Angular treats all
values as **untrusted by default**. Template bindings/interpolation are
automatically sanitized/escaped based on **security context** (HTML, Style,
URL, Resource URL). "Sanitization is the inspection of an untrusted value,
turning it into a value that's safe to insert into the DOM." Angular can
sanitize HTML and URLs, but **cannot sanitize resource URLs containing
arbitrary code**. In dev mode, sanitization-caused alterations are logged
to the console.

[Source: https://angular.dev/best-practices/security] When an app
genuinely needs to bypass sanitization, `DomSanitizer` exposes
`bypassSecurityTrustHtml`, `bypassSecurityTrustScript`,
`bypassSecurityTrustStyle`, `bypassSecurityTrustUrl`,
`bypassSecurityTrustResourceUrl`. Explicit warning: using these introduces
vulnerabilities if the trusted value is attacker-controlled, and the method
chosen must match the actual usage context.

[Source: https://angular.dev/best-practices/security] **XSRF/CSRF**:
`HttpClient` includes XSRF protection by default — an interceptor reads a
token from the `XSRF-TOKEN` cookie and sets it as the `X-XSRF-TOKEN` header
on mutating (POST/PUT/DELETE) same-origin requests; GET requests are
excluded because same-origin policy already prevents cross-domain retrieval
of authenticated responses. Customize via `withXsrfConfiguration(...)`
(custom cookie/header names) or disable entirely via
`withNoXsrfProtection()`.

[Source: https://angular.dev/best-practices/security] **Content Security
Policy**: documented minimal recommended header:
`default-src 'self'; style-src 'self' 'nonce-randomNonceGoesHere'; script-src 'self' 'nonce-randomNonceGoesHere';`
— the server must generate a unique, unpredictable nonce per request.
Angular supports supplying that nonce via workspace configuration
(`autoCsp`), the `ngCspNonce` template attribute, or the `CSP_NONCE`
injection token.

[Source: https://angular.dev/best-practices/security] **Trusted Types**
support: Angular documents specific policies —`angular` (internal,
security-reviewed Angular code), `angular#bundler` (Angular CLI lazy chunk
files), `angular#unsafe-bypass` (apps using `DomSanitizer` bypass methods),
`angular#unsafe-jit` (apps using the JIT compiler), `angular#unsafe-upgrade`
(AngularJS hybrid `ngUpgrade` apps).

[Source: https://angular.dev/best-practices/security] **AOT compilation**
(the Angular CLI default) is called out as a security measure: it prevents
template-injection vulnerabilities and "should always be used in
production."

[Source: https://angular.dev/best-practices/security] **XSSI protection**:
`HttpClient` automatically strips the `")]}',\n"` security prefix from JSON
responses to prevent cross-site script inclusion.

[Source: https://angular.dev/best-practices/security] Documented best
practices summary: keep Angular updated, don't modify vendored Angular
code, always use the AOT compiler, avoid APIs explicitly flagged as
security-sensitive, and audit any code using `bypassSecurityTrust*`.

## 8. Performance

[Source: https://angular.dev/best-practices/runtime-performance] "Change
detection is highly optimized and performant, but it can still cause
slowdowns if the application runs it too frequently." Angular's change
detection walks the component tree top-to-bottom looking for state changes
to reflect into the DOM. The runtime-performance guide's documented topic
set: the zoneless approach, slow computations, component-subtree skipping,
"zone pollution," and using Chrome DevTools for profiling.

[Source: https://angular.dev/guide/zoneless] **Zoneless** (stable/default
v21+, see §2) is explicitly framed as a performance feature: documented
benefits are "improved performance" via fewer unnecessary change-detection
cycles and "improved Core Web Vitals" from removing Zone.js's monkey-patch
overhead.

[Version-sensitive, v22] [Source: https://raw.githubusercontent.com/angular/angular/main/CHANGELOG.md
(v22.0.0 entry)] New components defaulting to `ChangeDetectionStrategy.OnPush`
as of v22 (see §2/§13) is itself a performance-relevant default change —
OnPush limits re-render checks to inputs/signal changes/events rather than
every zone-detected tick.

[Source: https://angular.dev/guide/templates/defer] `@defer` (see §3) is
Angular's primary documented lazy-loading/code-splitting performance
primitive at the template level, reducing initial bundle size for
non-critical UI with configurable idle/viewport/interaction/hover/
timer/immediate triggers plus prefetching.

[Source: https://angular.dev/best-practices/images] `NgOptimizedImage`
(see §5) is the documented performance tool for image-heavy pages,
specifically targeting Largest Contentful Paint (LCP) via `priority`
loading, `fetchpriority=high`, preload link generation under SSR, and
automatic responsive `srcset` generation.

[Source: https://angular.dev/guide/ssr] SSR/SSG rendering-mode selection
(`Server`/`Client`/`Prerender` per route) is documented as a
performance/architecture lever, alongside automatic transfer of cached
HTTP GET/HEAD responses from server to browser during hydration to avoid
redundant initial-load requests.

[Source: https://angular.dev/tools/devtools] **Angular DevTools'
Profiler tab** is the documented tool for diagnosing change-detection
performance bottlenecks specifically (see §15 for full DevTools detail).

## 9. Testing

[Source: https://angular.dev/guide/testing] [Version-sensitive, Angular
v21+] **Vitest is now the default test runner for new Angular CLI
projects**, replacing Karma: "This guide covers the default testing setup
for new Angular CLI projects, which uses Vitest." Vitest runs in Node.js
using **jsdom** (or **happy-dom**) for DOM emulation — the docs state
"jsdom and happy-dom are the supported DOM emulation libraries" — which
speeds up execution by avoiding real-browser overhead. Real-browser testing
remains available via providers like Playwright or WebdriverIO for
browser-specific API coverage/debugging.

[Version-sensitive] [Source: WebSearch summary of Angular v21-related
official/community sources] Karma was deprecated by the Angular team in
2023; **Karma and Jasmine remain fully supported** for existing projects
(no forced migration), and a dedicated official **"Migrating from Karma to
Vitest"** guide exists at `angular.dev/guide/testing/migrating-to-vitest`.
Unresolved: the precise version in which Vitest specifically became
"stable" (as opposed to merely "new default for new projects") was reported
by a WebSearch summary as v21, but this specific stability-label claim was
not independently re-verified against a raw angular.dev page fetch, so
treat the exact wording/version boundary as not fully confirmed.

[Source: https://angular.dev/guide/testing] Angular provides **component
test harnesses** as a first-class testing utility, with documented guides
for: harness overview, using harnesses in tests, creating custom harnesses,
and adding harness support for additional test environments.

[Source: https://angular.dev/guide/forms] Testing implications of the two
classic forms systems: reactive forms are directly/synchronously testable
without rendering the UI; template-driven forms require more familiarity
with change-detection cycles because of their async data flow via `NgModel`.

[Source: https://angular.dev/best-practices/error-handling] `TestBed`
**rethrows errors by default** so framework-caught mistakes surface during
tests, configurable via `rethrowApplicationErrors: false` in
`configureTestingModule` as "a last resort."

[Source: https://angular.dev/guide/routing] The router guide's documented
topic list explicitly includes a dedicated **testing** section for routed
applications (guards, resolvers, navigation), though its specific content
was not independently fetched in this research pass — see Unresolved
below.

Unresolved: this research did not directly fetch the router-testing guide
page's content, only its existence in the router guide's navigation; do not
assume specific router-testing API names beyond what's stated here.

## 10. Deployment

[Source: https://angular.dev/tools/cli/deployment] Build with `ng build`
(uses the production configuration by default), output to `dist/my-app/`
(configurable via `outputPath`). Angular CLI documents **CLI-builder-driven
"automatic" deploys** via `ng add` + `ng deploy` for: Firebase Hosting
(`ng add @angular/fire`), Netlify (`ng add @netlify-builder/deploy`),
GitHub Pages (`ng add angular-cli-ghpages`), Amazon S3
(`ng add @jefiozie/ngx-aws-deploy`), and a documented Vercel path
(`vercel init angular`).

[Source: https://angular.dev/tools/cli/deployment] For **manual/custom
server** deployment: copy `dist/` to the web server or CDN. Server-side,
**deep-link fallback to `index.html` is required** for SPA routing — without
it, direct navigation to a routed URL (e.g. `/users/42`) 404s, since
Angular's client-side router only takes over after `index.html` loads.

[Source: https://angular.dev/tools/cli/deployment] **Base href**: prefer
runtime `<base href>` configuration over the build-time `--deploy-url` CLI
flag for asset path resolution where possible. **CORS** must be configured
server-side; the client cannot override browser cross-origin restrictions.

[Source: https://angular.dev/tools/cli/deployment] Production builds
include AOT compilation, minification, bundling, dead-code elimination,
and stripping of development-only code paths.

[Source: https://angular.dev/guide/ssr] SSR deployment requires a Node.js
server runtime (unless `outputMode: 'static'` is used for a fully static
SSG build — see §2/§4) — the deployment guide's own text notes it covers
"server-side & hybrid-rendering" as a distinct, more involved deployment
mode versus the static-file CSR path.

[Source: https://angular.dev/ecosystem/service-workers] The **Angular
service worker** is a documented, CLI-installable PWA/offline-caching layer
that runs as a network proxy in the browser, generating an `ngsw.json`
manifest tracking cached resources and content hashes. Requires HTTPS
(except `localhost`). Caching principles: the app caches "as unified
units" with synchronized file updates so a running instance never mixes
cached versions; refreshing always loads the latest cached version;
background updates don't interrupt the current session; only changed
resources are re-downloaded.

## 11. Migration

[Source: https://angular.dev/update-guide] Angular publishes an
**interactive Update Guide** (angular.dev/update-guide) that generates
tailored upgrade instructions from a chosen from-version/to-version pair,
app complexity level (Basic/Medium/Advanced), and special dependencies
(ngUpgrade, Angular Material, Windows). At fetch time it supported
generating a path from v21.0 to v22.0 (and, per the CLI reference within
it, links out to version-compatibility and Extended Diagnostics pages).

[Source: https://angular.dev/reference/releases] The primary migration
mechanism between majors is `ng update`, described as providing "code
transformations tested across hundreds of thousands of projects."

[Source: https://angular.dev/reference/migrations] Beyond major-version
`ng update` upgrades, Angular ships **13 standalone, opt-in `ng generate`
migration schematics** for incrementally adopting individual modern
patterns on an existing codebase without a full major-version bump — see
the full list in §5 (standalone components, control-flow syntax, `inject()`,
lazy routes, signal inputs, `output()`, signal queries, unused-import
cleanup, self-closing tags, `NgClass`/`NgStyle` → native bindings,
`RouterTestingModule` modernization, `CommonModule` → standalone
directives).

[Source: https://angular.dev/guide/testing] A dedicated official
**"Migrating from Karma to Vitest"** guide exists for the test-runner
transition described in §9.

[Source: https://angular.dev/reference/releases] **Deprecation-to-removal
policy** (relevant to migration planning): a deprecated API stays available
for "at least the next major release (period of at least 12 months)";
removal happens only in a major release; deprecations are announced via the
changelog, documentation, and `@deprecated` JSDoc annotations.

[Inference, not confirmed in docs] Angular does not document an official
migration path *from a different framework* (e.g. React, Vue) into
Angular — its "migration" documentation is exclusively about upgrading
between Angular's own major versions (and the legacy `ngUpgrade` path for
mixing AngularJS 1.x and modern Angular in one app, referenced in the
Update Guide's "special dependencies" option and the v21 changelog's
`upgrade` package entries). Framework-to-framework migration is out of
scope for angular.dev.

## 12. Version information

[Source: https://angular.dev/reference/releases] **Versioning scheme**:
strict semver, `major.minor.patch` (e.g. 7.2.11). Major = significant new
features, may require developer action/scripts/refactoring/testing. Minor =
smaller, fully backward-compatible features, update optional. Patch =
low-risk bug fixes, no developer action needed. Preview channels: "Next"
builds (`-next` tag, active development) and Release Candidates (`-rc` tag,
feature-complete).

[Version-sensitive] [Source: https://angular.dev/reference/releases]
**Release cadence changed at v22**: prior to v22, Angular followed a
**6-month major release cycle** with 1-3 minor releases per major. As of
v22, the target is **a major release every 12 months**, with **4-6 minor
releases per major**, plus weekly patch/prerelease builds.

[Source: https://angular.dev/reference/releases] **Current version**: the
latest stable is **v22** (released 2026-06-03). At research time, the
angular.dev site itself was on build "v22.1.5." Forward schedule referenced
on the releases page: v22.1 (week of 2026-07-27), v22.2-v22.5 through
2026-2027, v23.0 approximately June 2027.

[Source: https://angular.dev/reference/releases] **Support window**: each
major release gets **24 months total** support — a **12-month Active phase**
(regular feature/bug-fix updates) followed by a **12-month LTS phase**
(critical/security fixes only). This is itself a change from the pre-v22
model implied by the 6-month cadence figures the same page cites.

[Source: https://angular.dev/reference/releases] **Supported-versions
table** (as fetched):

| Version | Status | Released | Active ends | LTS ends |
|---|---|---|---|---|
| v22.0.0+ | Active | 2026-06-03 | 2027-06 | 2028-06 |
| v21.0.0 | LTS | 2025-11-19 | 2026-06-03 | 2027-06 |
| v20.0.0 | LTS | 2025-05-28 | 2025-11-19 | 2026-11-28 |

Versions v2-v19 are documented as no longer supported.

[Source: https://angular.dev/reference/releases] **LTS fix policy**:
critical LTS-phase fixes are limited to newly identified security
vulnerabilities or regressions caused by third-party changes (e.g. a new
browser release).

[Source: https://angular.dev/reference/versions] **Engine compatibility**
(current majors):

| Angular | Node.js | TypeScript | RxJS |
|---|---|---|---|
| 22.0.x | ^22.22.3 \|\| ^24.15.0 \|\| ^26.0.0 | >=6.0.0 <6.1.0 | ^6.5.3 \|\| ^7.4.0 |
| 21.0.x-21.2.x | ^20.19.0 \|\| ^22.12.0 \|\| ^24.0.0 | >=5.9.0 <6.0.0 | ^6.5.3 \|\| ^7.4.0 |
| 20.0.x-20.3.x | ^20.19.0 \|\| ^22.12.0 \|\| ^24.0.0 | >=5.8.0 <6.0.0 | ^6.5.3 \|\| ^7.4.0 |

Unresolved: whether "TypeScript >=6.0.0 <6.1.0" for Angular 22.0.x is a
narrow initial-release pin that later 22.x patch/minor releases loosened —
this table reflects the state at fetch time only; check
`angular.dev/reference/versions` directly for the current window before
relying on it.

[Source: https://angular.dev/reference/versions] **Browser support policy
changed at v20**: v20+ uses the ["widely available" Baseline](https://web.dev/baseline)
standard, targeting browsers released within **30 months** of a baseline
date set near each major's release (v22: 2026-05-07; v21: 2025-10-20; v20:
2025-04-30), aiming to cover roughly 95% of web users. Pre-v20 releases
instead targeted a fixed "2 most recent versions" of Chrome/Firefox/
Edge/Safari and "2 most recent major versions" of iOS/Android.

## 13. Breaking changes

[Source: https://raw.githubusercontent.com/angular/angular/main/CHANGELOG.md]
The canonical breaking-changes record is the `angular/angular` GitHub
CHANGELOG.md, which lists changes per version under an explicit
`## Breaking Changes` heading, organized by affected package. Selected
major-version highlights (not exhaustive — consult the changelog directly
for the full per-package list):

**v22.0.0 (2026-06-03)**, blog: "Announcing Angular v22"
(`https://goo.gle/angular-v22-blog`):
- `core`: TypeScript versions older than **6.0** no longer supported.
- `core`: Components with an **undefined `changeDetection`** now default to
  **`OnPush`** (was Zone-checked "Default"); use
  `changeDetection: ChangeDetectionStrategy.Eager` to opt back into the old
  default.
- `core`: `ChangeDetectorRef.checkNoChanges` **removed** — use
  `fixture.detectChanges()` in tests.
- `core`: `createNgModuleRef` **removed** — use `createNgModule`.
- `core`: `ComponentFactoryResolver`/`ComponentFactory` **removed** — pass
  the component class directly to APIs like `ViewContainerRef.createComponent`.
- `compiler`: `data-`-prefixed attributes **no longer bind** inputs/outputs;
  the compiler now **throws** if an input/output/model binds to the same
  property twice, and `in` used as a template expression variable now
  throws.
- `compiler-cli`: elements matching **multiple selectors** now throw a
  compile-time error.
- `forms`: `min`/`max` validators **no longer accept string values** — must
  be a number or `null`.
- `http`: upload-progress reporting requires explicitly opting into
  `HttpXhrBackend` via `provideHttpClient(withXhr)`; `withFetch` and the
  `reportProgress` option are **deprecated** (see below).
- `platform-browser`: **Hammer.js integration removed**; unused component
  styles are now pruned when their associated host is dropped.
- `router`: `paramsInheritanceStrategy` **default changed** from
  `'emptyOnly'` to **`'always'`**; `provideRoutes()` **removed** (use
  `provideRouter()`/`ROUTES`); `CanMatchFn`/`CanMatch.canMatch` now
  **require** a `currentSnapshot` third argument.
- `upgrade`: deprecated `getAngularLib`/`setAngularLib` **removed** — use
  `getAngularJSGlobal`/`setAngularJSGlobal`.
- **Deprecations introduced in 22.0.0**: `http`'s `withFetch` (safely
  removable) and `reportProgress` (use `reportUploadProgress`/
  `reportDownloadProgress`).

**v21.0.0 (2025-11-19)**, blog: "Announcing Angular v21"
(`http://goo.gle/angular-v21-blog`):
- `core`: TypeScript versions **less than 5.9** no longer supported.
- `core`: server-side bootstrapping changed to **remove reliance on a
  global platform injector** — `bootstrapApplication` on the server now
  takes a `BootstrapContext` second argument (a schematic auto-updates
  `main.server.ts`); `getPlatform()`/`destroyPlatform()` now return
  `null`/no-op server-side.
- `core`: `ignoreChangesOutsideZone` option **removed**; Angular **no
  longer provides a default change-detection scheduler for Zone.js-based**
  apps — `provideZoneChangeDetection` must be added explicitly if still
  using Zone.js (covered by an automated migration).
- `core`: `moduleId` **removed** from `@Component` metadata; the
  `interpolation` custom-delimiter option **removed** (only default
  `{{ }}` supported).
- `common`: `NgModuleFactory` **removed** — use `NgModule` directly.
- `platform-browser`: deprecated `ApplicationConfig` export **removed** —
  import from `@angular/core` instead.
- `router`: `lastSuccessfulNavigation` **is now a signal** (must be
  invoked as a function); router navigations may take additional
  microtasks to complete, which can affect test timing assumptions.
- `upgrade`: `UpgradeAdapter` **removed** — use `upgrade/static`.
- `zone.js`: **IE / non-Chromium Edge no longer supported**.

**v20.0.0 (2025-05-28)**, blog: `https://blog.angular.dev/announcing-angular-v20-b5c9c06cf301`:
- `core`: TypeScript versions **less than 5.8** no longer supported; Node.js
  **v18 and Node 22.0-22.10 no longer supported** (minimum 20.11.1).
- `core`: `TestBed.flushEffects()` **removed** — use `TestBed.tick()`.
- `core`: `provideExperimentalZonelessChangeDetection` **renamed** to
  `provideZonelessChangeDetection` (status changed from "Experimental" to
  "Developer Preview"). `provideExperimentalCheckNoChangesForDebug`
  renamed to `provideCheckNoChangesConfig` with behavior changes (applies
  to *all* `checkNoChanges` runs; `useNgZoneOnStable` option removed).
- `core`: `InjectFlags` **removed** entirely (no longer accepted by
  `inject`, `Injector.get`, `EnvironmentInjector.get`, `TestBed.get`,
  `TestBed.inject`); `TestBed.get` **removed** — use `TestBed.inject`.
- `core`: `afterRender` **renamed to `afterEveryRender`**.
- `common`: `AsyncPipe` now directly catches and reports unhandled
  subscription/promise errors to `ErrorHandler` (previously Zone.js-mediated
  in Zone apps) — can shift error timing in test environments.
- `compiler`: `in` and `void` in template expressions **now refer to their
  JS operators**, not a same-named component property (use `this.void` to
  disambiguate); **parentheses are now always respected** in expressions,
  which can surface new runtime errors for patterns like
  `{{ (foo?.bar).baz }}` when `foo` is nullish (matches native JS
  semantics).

Unresolved: the full CHANGELOG.md file is very long (multiple megabytes of
history); this research fetched and reviewed the v20.0.0, v21.0.0, and
v22.0.0 sections directly but did not exhaustively review every intervening
minor release's own breaking-change notes (there generally shouldn't be
any, per the semver policy in §12, but this was not independently verified
for every 20.x/21.x/22.x minor).

## 14. Limitations

[Source: https://angular.dev/best-practices/security] Angular's sanitizer
**cannot sanitize Resource URLs containing arbitrary code** — this is an
explicitly documented gap requiring manual `bypassSecurityTrustResourceUrl`
review rather than automatic protection.

[Source: https://angular.dev/ecosystem/service-workers] The Angular service
worker is explicitly described as "a basic caching utility for simple
offline support with a **limited featureset**" — the docs recommend using
native browser Service Worker APIs directly for advanced caching needs
beyond what the Angular abstraction covers.

[Source: https://angular.dev/guide/ssr] SSR/server execution environments
**do not have `window`/`document`** and other browser globals available;
code needing browser APIs must be gated behind `afterNextRender()` or use
the platform-agnostic `DOCUMENT` injection token instead of the global.

[Source: https://angular.dev/tools/devtools] **Angular DevTools only
supports development builds** — pointing it at a production build produces
an explicit in-extension warning ("We detected an application built with
production configuration. Angular DevTools only supports development
builds"), requiring optimization to be disabled to inspect a compiled app.

[Source: https://angular.dev/reference/versions] Browser support is
explicitly bounded by the documented Baseline/30-month policy (§12) —
Angular does not claim indefinite backward browser compatibility.

[Source: https://angular.dev/best-practices/error-handling] Angular's
`ErrorHandler` **does not catch errors from APIs called directly by
application code** (only errors inside framework-managed code paths —
component lifecycle, explicit async contracts like `AsyncPipe`/
`PendingTasks.run`) — developers must use `try...catch`/`catchError`
themselves for arbitrary async work, and errors thrown during initial app
bootstrap may bypass `ErrorHandler` entirely because the root component
(and thus the DI tree that would locate a custom handler) doesn't exist yet.

## 15. Debugging

[Source: https://angular.dev/tools/devtools] **Angular DevTools** is an
official browser extension (Chrome Web Store, Firefox Add-ons) providing:
a **Components tab** (inspect/edit component and directive state live), a
**Profiler tab** (identify change-detection performance bottlenecks), an
**Injector Tree tab** (visualize environment/element injector hierarchy),
and a **Router Tree tab** (inspect routing structure/navigation). Accessed
via the browser's own DevTools (F12 / Ctrl+Shift+I / Cmd+Option+I) under an
"Angular" panel. **Requires a development build**; production builds show
an explicit unsupported-configuration warning (see §14).

[Version-sensitive, mentioned for 2026] [Source: WebSearch summary,
"Angular angular.dev documentation overview 2026"] Per a WebSearch summary
of angular.dev's own 2026 feature messaging, "better tooling for debugging
Signals has been added, including a new UI for inspecting and debugging
signals" in Angular DevTools. Unresolved: this specific Signals-debugging
UI claim was surfaced only via a WebSearch synthesis of angular.dev
content, not confirmed against a direct raw fetch of a DevTools changelog
page, so treat the exact feature scope/version as unresolved pending direct
verification.

[Source: https://angular.dev/best-practices/error-handling] Documented
error-surfacing mechanisms usable for debugging: the root `ErrorHandler`
(overridable via a provider in `ApplicationConfig`),
`provideBrowserGlobalErrorListeners()` (adds `window` `'error'` and
`'unhandledrejection'` listeners forwarding to `ErrorHandler`; included by
default in Angular CLI apps), and, server-side, automatic
`'unhandledRejection'`/`'uncaughtException'` process listeners to prevent
SSR process crashes while still logging.

[Source: WebSearch result "NG0100: Expression Changed After Checked •
Angular" (https://angular.dev/errors/NG0100)] Angular publishes an
**Error Encyclopedia** at `angular.dev/errors`, with individual pages per
numbered runtime error code (e.g. **NG0100**,
`ExpressionChangedAfterItHasBeenCheckedError`). NG0100 specifically: thrown
**only in development mode**, when Angular's additional post-change-detection
consistency check finds a binding changed after it was already checked —
commonly from a method/getter returning a different value on each call, or
a child component mutating a value used by its parent; documented fix is to
set values in the correct lifecycle hook (constructor/`ngOnInit`, or
`ngAfterContentInit` rather than `ngAfterViewInit`) rather than mutating
post-check.

Unresolved: this research directly located and summarized only the NG0100
error page (via WebSearch, not a direct raw-content WebFetch); the full
`angular.dev/errors` index and its complete catalog of error codes was not
enumerated, so no claim is made here about the total number of documented
error codes or their full list.

## 16. Integration

[Source: https://angular.dev/ecosystem/rxjs-interop] **RxJS**: first-class,
official interop package `@angular/core/rxjs-interop` (`toSignal`,
`toObservable`, `rxResource`, `takeUntilDestroyed`) — see §3 for API detail.

[Source: https://angular.dev/guide/http] **HTTP backends**: `HttpClient`
integrates with either the XHR-based `HttpXhrBackend` (needed specifically
for upload-progress support, per the v22 breaking change in §13) or a
Fetch-based backend via `withFetch` (deprecated as of v22, see §13).

[Source: https://angular.dev/best-practices/security] **AngularJS
interop**: the `upgrade` package (`ngUpgrade`) supports hybrid apps mixing
legacy AngularJS 1.x and modern Angular; `upgrade/static` is the current
documented entry point (the older `UpgradeAdapter` was removed in v21, see
§13).

[Source: https://angular.dev/ecosystem/service-workers] **PWA/offline**:
official `@angular/service-worker` package, CLI-installable, for basic
caching/offline scenarios (see §10/§14 for scope and limitations).

[Source: https://angular.dev/guide/testing] **Testing framework
integration**: Vitest (new default, v21+), Karma/Jasmine (still supported
legacy default), and real-browser test providers (Playwright,
WebdriverIO) — see §9.

[Version-sensitive, Angular v22] [Source: https://angular.dev/ai/agent-skills]
Angular officially publishes **"Agent Skills"** — "specialized,
domain-specific instructions and capabilities designed for AI agents like
Gemini CLI" — as of the v22 era. Documented supported tools: **Gemini
CLI**, **Antigravity**, and community tools such as `skills.sh`
(installable via `npx skills add https://github.com/angular/skills`).
Two official skills are named: **`angular-developer`** (architectural
guidance and idiomatic code generation across reactivity — signals,
`linkedSignal`, `resource` — forms, DI, routing, SSR, accessibility,
animations, styling, testing, CLI tooling) and **`angular-new-app`**
(project scaffolding via the Angular CLI). The docs describe these skills
as regularly maintained to "stay in sync with the latest framework
improvements." [Inference, not confirmed in docs] This is directly germane
to the meta-purpose of the Skill Library project this research feeds: it
means Angular itself, as of v22, ships an *official* competing/complementary
skill definition for AI coding agents, which a library-authored Angular
skill should be aware of (and possibly reference or diverge from
deliberately) rather than duplicate blindly.

[Source: https://angular.dev/guide/ngmodules/overview] **Angular
Material / CDK**: referenced throughout the docs (e.g. as a documented
"special dependency" option in the Update Guide, §11) as the
officially-maintained companion component/UI-primitives library, published
under the `@angular/cdk` and Material packages tracked in the API
reference package list (§3).

[Version-sensitive, Angular v22] [Source: WebSearch summary of Angular v22
sources] **`@angular/aria`** — a package of headless, fully-accessible
directive patterns (accordions, tabs, menus, listboxes, trees, etc.)
handling keyboard navigation/ARIA semantics while leaving styling to the
consumer — reportedly went from developer preview (v21) to **stable** in
v22, with roughly twelve documented UI patterns and accompanying test
harnesses per third-party summaries of the official v22 announcement.
Unresolved: this specific package's own dedicated angular.dev guide page
was not directly fetched in this research pass (only referenced via
WebSearch synthesis of the v22 blog announcement), so exact API names and
the precise "stable" wording should be re-verified directly against
`angular.dev` before being treated as load-bearing for a skill.

## 17. Production considerations

[Source: https://angular.dev/best-practices/security] Production
checklist items explicit in the security docs: keep Angular updated,
never modify vendored Angular source, always build with the **AOT
compiler** (CLI default) rather than JIT, avoid explicitly
security-flagged APIs, and audit all `bypassSecurityTrust*` usage.

[Source: https://angular.dev/tools/cli/deployment] Production builds
(`ng build`, production config by default) apply AOT compilation,
minification, bundling, dead-code elimination, and removal of
development-only code. Server-side deployment must implement SPA-fallback
routing to `index.html` for deep links, and CORS must be handled
server-side.

[Source: https://angular.dev/guide/ssr] For SSR/hybrid apps in production,
per-route rendering-mode choice (`Server`/`Client`/`Prerender`) is a
deliberate production architecture decision, and `outputMode: 'static'`
is documented specifically as a way to avoid needing a Node.js server
process in production for content that can be fully prerendered.

[Source: https://angular.dev/tools/devtools] Angular DevTools is
explicitly **not usable against production builds** (§14) — production
debugging requires either a parallel dev build or the documented
`ErrorHandler`/global-error-listener mechanisms (§15) rather than the
DevTools extension.

[Source: https://angular.dev/reference/releases] Production support
planning should account for the documented **24-month total support
window** (12 Active + 12 LTS) per major version and the **critical-only**
nature of LTS-phase fixes (security + third-party-caused regressions only,
see §12) — i.e., an app pinned to an LTS major will not receive new
features or general bug fixes, only security/compat patches, for up to a
year before that version drops out of support entirely.

[Source: https://angular.dev/ecosystem/service-workers] For PWA/offline
production deployments, HTTPS is a hard requirement (except `localhost`
during development) for the Angular service worker to function at all.

[Inference, not confirmed in docs] Given the v20-v22 changes documented in
§13 (Node.js minimums moving from "no v18/no 22.0-22.10" at v20 to a
`^22.22.3 || ^24.15.0 || ^26.0.0` range at v22, and TypeScript minimums
moving from 5.8 → 5.9 → 6.0 across the same three majors), production CI/CD
pipelines pinned to older Node/TypeScript toolchains are likely to need
active maintenance to track each Angular major upgrade — this pattern is
inferred from the version-compatibility table (§12) and changelog entries
(§13) rather than from an explicit angular.dev statement urging this.

---

## Notes on research process

This document was compiled primarily via `WebFetch` against angular.dev
guide/reference pages and via direct `curl` retrieval of the raw
`angular/angular` GitHub CHANGELOG.md (fetching the raw file directly, then
searching it locally, proved much more reliable than WebFetch's
AI-summarized rendering of the GitHub UI, which repeatedly failed to
surface changelog content through the repo's web viewer). Several
WebFetch-summarized claims were caught as likely wrong or under-specified
on inspection and re-verified against a second, more targeted fetch before
being included (for example, an initial WebFetch summary claimed Angular
services use a decorator called `@Service()` as if it were the *only*
current decorator, which on the surface reads like a hallucinated rename of
`@Injectable()`; a follow-up fetch of the specific creating-services page
confirmed `@Service()` is a genuine new, additional v22 decorator existing
alongside `@Injectable()`, not a replacement or a fabrication — but this
kind of cross-check was not exhaustively repeated for every claim in this
document, so treat any single-sourced WebFetch summary claim with
appropriate caution, especially ones without direct quoted text).
