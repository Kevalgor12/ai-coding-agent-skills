---
name: Angular
description: >-
  Angular-specific implementation: dependency injection (inject(),
  @Service()/@Injectable()), standalone-vs-NgModule architecture, the
  Signals API (signal/computed/effect/resource/httpResource), zoneless
  change detection, and per-major TypeScript/Node.js version floors. Use
  when the stack is Angular (angular.json, @angular/core, ng CLI) or the
  task names Angular. Not for an open framework choice or React/Vue
  specifics (route to frontend-architecture or their skills).
spec_version: "1.0"
---

## Purpose & scope

Apply Angular correctly and version-appropriately: dependency injection,
standalone-vs-NgModule component architecture, the Signals API, and zoneless
change detection, tracked against Angular's unusually strict per-major
TypeScript/Node.js coupling. The generic frontend-structure method and the
React-vs-Vue-vs-Angular framework-selection decision belong to the parent,
[frontend-architecture](../frontend-architecture/SKILL.md) (`SK-FE-001`) —
this skill does not repeat that comparison, only adds Angular-specific
implementation depth. The SSR/SSG rendering-mode decision belongs to
rendering-strategy (`SK-FE-005`, not yet authored).

## When to use / When not to use

**Use** when the stack is Angular (`angular.json`, `@angular/core`, `ng`
CLI usage) and the task is Angular-specific: DI/service design, standalone
vs NgModule structure, signals/change-detection work, template/forms work,
or a version-upgrade question. **Do not use** when the framework choice is
still open (route to `SK-FE-001`), when the stack uses React or Vue instead
(route to their technology skills), or for generic component/state
structure with no Angular-specific mechanism involved (route to
`SK-FE-001`).

## Knowledge

**Dependency injection.** DI is Angular's mechanism for supplying
dependencies to a class instead of creating them inside it
[Source: https://angular.dev/guide/di]. Services are TypeScript classes made
injectable; `inject()` is the documented idiomatic way to request a
dependency, usable in class-field initializers or constructor bodies of
components, directives, services, and route guards — shown in the docs as a
field initializer (`dataStore = inject(BasicDataStore);`), positioned ahead
of constructor-parameter injection in the style guide
[Source: https://angular.dev/guide/di/creating-and-using-services]. Angular
supports hierarchical injectors, scoping providers at different levels of
the app. **[Version-sensitive, v22]** v22 introduced a second, more
ergonomic decorator for injectable classes, `@Service()`, positioned
alongside the traditional `@Injectable({ providedIn: 'root' })`; the docs
note it's particularly suited to services using `inject()` rather than
constructor injection, and both decorators support `providedIn: 'root'`
(singleton, tree-shakable, auto-registered)
[Source: https://angular.dev/guide/di/creating-and-using-services]. Unresolved:
the exact default `providedIn` behavior of bare `@Service()` was not
independently confirmed against raw page markup in the source research.

**Standalone components vs NgModules.** A component requires a TypeScript
class, an HTML template, and a CSS selector, attached via `@Component`
[Source: https://angular.dev/guide/components]. **[Version-sensitive]**
Before Angular 19.0.0, `standalone` defaulted to `false`, requiring
`NgModule` registration; as of 19+, components are standalone by default and
can be added directly to another component's `imports` array
[Source: https://angular.dev/guide/components]. An `NgModule` is a class
decorated `@NgModule` that declares components/directives/pipes and
configures DI providers, historically via `forRoot()`/`forChild()` for
root-level provider registration; NgModules are **not deprecated** and
remain fully supported, but "the Angular team recommends using standalone
components instead of NgModule for all new code"
[Source: https://angular.dev/guide/ngmodules/overview]. Only standalone
components/directives/pipes are eligible for `@defer` — NgModule-declared
dependencies inside a `@defer` block still load eagerly
[Source: https://angular.dev/guide/templates/defer].

**Signals API.** A signal is "a wrapper around a value that notifies
interested consumers when that value changes," letting Angular granularly
track state usage to optimize rendering [Source: https://angular.dev/guide/signals].
`signal()` creates a writable signal (read by calling it, written via
`.set()`/`.update()`); `computed()` creates a read-only, lazily-evaluated,
memoized derived signal; `effect()` runs side effects when read signals
change. `resource()` incorporates async data into signal-based code
(`resource({ params: () => (...), loader: ({params}) => fetchData(params) })`),
returning `isLoading`/`error`/`status`/`value` signals; `httpResource()`
wraps `HttpClient`, exposing request status and the resolved response as
signals, still flowing through Angular's interceptor chain
[Source: https://angular.dev/guide/signals/resource]. **[Version-sensitive,
v22]** `resource()`/`httpResource()` were promoted to developer-stable as
part of v22's signal-first push [Source: https://angular.dev/guide/signals/resource].
`@angular/core/rxjs-interop` bridges signals and RxJS: `toSignal()`
subscribes immediately and exposes the latest value as a signal
(`initialValue`, `requireSync`, `equal` options); `toObservable()` does the
inverse; `rxResource()` is a `resource()` variant backed by an Observable;
`takeUntilDestroyed()` auto-unsubscribes tied to a `DestroyRef`
[Source: https://angular.dev/ecosystem/rxjs-interop].

**Zoneless change detection.** Angular historically relied on Zone.js, which
monkey-patches browser APIs (timers, listeners, promises) to detect
state changes and trigger a change-detection pass
[Source: https://angular.dev/guide/zoneless]. **[Version-sensitive]**
Zoneless is stable and the default from **v21+**; in **v20** it required
opt-in via `provideZonelessChangeDetection()`, which was itself a rename
from the Experimental-tier `provideExperimentalZonelessChangeDetection()`
(status became "Developer Preview" as part of the v20.0.0 breaking changes)
[Source: https://angular.dev/guide/zoneless; https://raw.githubusercontent.com/angular/angular/main/CHANGELOG.md
(v20.0.0 entry)]. Under zoneless, Angular relies on explicit notifications
(signal writes, `markForCheck`, async pipe) rather than patched global APIs.
Migrating off Zone.js means removing `zone.js` from `angular.json`
polyfills and `npm uninstall zone.js`
[Source: https://angular.dev/guide/zoneless]. **[Version-sensitive, v22]**
Components with an undefined `changeDetection` property now default to
`OnPush` (previously the Zone-checked "Default" strategy); the old default
is retained via `changeDetection: ChangeDetectionStrategy.Eager`
[Source: https://raw.githubusercontent.com/angular/angular/main/CHANGELOG.md
(v22.0.0 entry)]. Recommended pairing: **OnPush + Signals** — OnPush is
"recommended but not required," with signals as the notification mechanism
that keeps OnPush components correctly updated without Zone.js
[Source: https://angular.dev/guide/zoneless].

**Angular's version coupling is unusually strict — each major raises the
TypeScript/Node.js floor as a breaking change**, not a soft recommendation
[Source: https://angular.dev/reference/versions]:

| Angular | Node.js | TypeScript | RxJS |
|---|---|---|---|
| 22.0.x | `^22.22.3 \|\| ^24.15.0 \|\| ^26.0.0` | `>=6.0.0 <6.1.0` | `^6.5.3 \|\| ^7.4.0` |
| 21.0.x-21.2.x | `^20.19.0 \|\| ^22.12.0 \|\| ^24.0.0` | `>=5.9.0 <6.0.0` | `^6.5.3 \|\| ^7.4.0` |
| 20.0.x-20.3.x | `^20.19.0 \|\| ^22.12.0 \|\| ^24.0.0` | `>=5.8.0 <6.0.0` | `^6.5.3 \|\| ^7.4.0` |

Confirm the installed Angular major before stating a TypeScript/Node.js
requirement — a CI pipeline or local toolchain pinned below the floor for
the installed major will fail to build, not just warn
[Source: https://angular.dev/reference/versions]. Unresolved: whether the
narrow `TypeScript >=6.0.0 <6.1.0` window for 22.0.x widens in later 22.x
minors was not confirmed in the source research; verify against
`angular.dev/reference/versions` directly before relying on it for a
specific patch/minor.

## Decision framework

This does not repeat `frontend-architecture`'s React-vs-Vue-vs-Angular
comparison — see [`SK-FE-001`](../frontend-architecture/SKILL.md) for that.
Within an already-chosen Angular codebase:

1. **Zoneless or Zone.js-based change detection — driven by migration
   timeline, not a blanket default.** For a new project, zoneless is stable
   and the default from v21+ and is documented as a genuine performance win
   (fewer change-detection cycles, no Zone.js monkey-patch overhead) — take
   the default. For an **existing** Zone.js-reliant codebase: weigh the
   removal cost (some third-party libraries may implicitly assume Zone.js
   patching for their own async notifications) against staying on a
   supported LTS with Zone.js still active via
   `provideZoneChangeDetection(...)`. Migrating is not required to stay
   supported — Zone.js-based apps remain valid on v21+, they just don't get
   zoneless by default. Don't remove Zone.js from a codebase with unaudited
   third-party dependencies without first confirming none of them rely on
   it.
2. **Standalone or NgModule for new code — the official guidance is
   standalone, but existing NgModule code is not a migration mandate.** For
   new components/features, use standalone — this is the framework's own
   documented recommendation, not house preference
   [Source: https://angular.dev/guide/ngmodules/overview]. For an
   **existing** NgModule-based app, the real decision is incremental
   migration (via the `ng generate` standalone-components schematic, one
   module at a time) vs. leaving stable, low-churn modules as-is — NgModules
   are fully supported, not deprecated, so migrating purely for its own sake
   without a concrete need (a `@defer`-eligibility requirement, tree-shaking
   goals, team standardization) is not automatically justified.
3. **`@Service()` or `@Injectable()` for a new service (v22+)?** Both
   support `providedIn: 'root'` singleton/tree-shakable semantics; `@Service()`
   is documented as suited to services built around `inject()`. For a
   codebase not yet on v22, `@Injectable()` is the only option — don't
   introduce a v22-only decorator into code that must also run on v20/v21.
4. **Reactive Forms, Template-Driven Forms, or Signal Forms?** Reactive
   Forms offer explicit object-model access and synchronous, more testable
   data flow; Template-Driven Forms are simpler for basic cases but
   asynchronous via `NgModel`; Signal Forms are the newer signal-integrated
   option [Source: https://angular.dev/guide/forms]. Pick based on
   testability/complexity needs, not by default to whichever is already
   used elsewhere in the org without checking fit.

## Workflow

Adding a new feature/component to an already-Angular codebase:

1. Confirm the installed Angular major (`package.json`/`angular.json`) —
   this gates which TS/Node floor, zoneless default, and `@Service()`
   availability apply (see Knowledge table).
2. Scaffold as a standalone component unless the surrounding code is
   NgModule-based and a mixed pattern would be inconsistent with the
   immediate area of the codebase.
3. Use `inject()` for DI in new code; prefer `@Service()` over `@Injectable()`
   only when the confirmed major is v22+ and the service is `inject()`-based.
4. Model state with `signal()`/`computed()`; use `resource()`/`httpResource()`
   for async data fetching tied to the component's lifecycle; bridge only to
   RxJS where an existing Observable-based API requires it, via
   `toSignal()`/`toObservable()`.
5. Apply `OnPush` (or rely on the v22+ default) and confirm the codebase's
   change-detection provider (`provideZonelessChangeDetection` vs
   `provideZoneChangeDetection`) matches what the new code assumes.
6. Use `@defer` for non-critical, standalone-only template content to keep
   the initial bundle small.
7. Write tests against the codebase's actual configured runner (see
   Testing) — don't assume Vitest for a pre-v21 project still on Karma.

## Engineering rules

- Confirm the Angular major before stating any TypeScript/Node.js/RxJS
  requirement or zoneless/OnPush-default claim — these are breaking changes
  gated per major, not universal facts (see the version table above).
- Prefer `inject()` over constructor-parameter injection for new code — the
  documented style-guide preference [Source: https://angular.dev/style-guide].
- Prefer standalone components for new code; don't force-migrate stable
  NgModule code without a concrete driver.
- Prefer `[class.x]`/`[style.x]` bindings over `[ngClass]`/`[ngStyle]` for
  new templates [Source: https://angular.dev/style-guide].
- Name event handlers after what they do (`(click)="saveUserData()"`), not
  after the triggering DOM event (`(click)="handleClick()"`)
  [Source: https://angular.dev/style-guide].
- Organize by feature area, not by code type — avoid `components/`,
  `directives/`-style top-level folders
  [Source: https://angular.dev/style-guide].
- Implement the corresponding TypeScript lifecycle interface (e.g.
  `OnInit`) whenever a lifecycle hook method is defined
  [Source: https://angular.dev/style-guide].
- Before removing Zone.js from a codebase, audit third-party dependencies
  for implicit reliance on Zone.js-patched async APIs — zoneless assumes
  explicit notification, and an unaudited dependency can silently miss
  updates.

## Trade-offs

Zoneless buys removal of Zone.js's global monkey-patch overhead and fewer
unnecessary change-detection cycles, at the cost of requiring every state
change to flow through an explicit notification path (signals,
`markForCheck`, async pipe) — a library that mutates state outside that path
silently stops updating the view. Standalone components simplify the mental
model and unlock `@defer` eligibility, at the cost of a mechanical migration
effort for existing NgModule-heavy codebases that gains little for modules
that are already stable and low-churn. `@Service()` is more ergonomic for
`inject()`-based services but is v22-only, so adopting it in a library
meant to support v20/v21 consumers isn't viable.

## Anti-patterns

- **Using `[ngClass]`/`[ngStyle]` instead of native class/style bindings**
  in new code — the style guide's explicit AVOID pattern
  [Source: https://angular.dev/style-guide].
- **Constructor-parameter DI instead of `inject()`** for new code
  [Source: https://angular.dev/style-guide].
- **Organizing a project by code type** (`components/`, `services/`,
  `directives/` folders) instead of by feature area — the guide explicitly
  calls this out to avoid [Source: https://angular.dev/style-guide].
- **Using `DomSanitizer.bypassSecurityTrust*` methods without justification
  or review** — the docs explicitly warn these "introduce security
  vulnerabilities if the trusted value is malicious"
  [Source: https://angular.dev/best-practices/security].
- **Assuming a pre-v19 codebase is standalone-by-default** — before
  19.0.0, `standalone` defaults to `false`, so template guidance written
  against the current default silently doesn't apply
  [Source: https://angular.dev/guide/components].
- **Over-engineering trap: force-migrating a stable, low-churn NgModule
  area to standalone (or removing Zone.js) purely to "modernize," with no
  concrete driver** — NgModules remain fully supported and Zone.js-based
  apps remain valid on v21+; a migration effort should be justified by an
  actual need (a `@defer` requirement, a measured change-detection
  bottleneck, a dependency conflict), not novelty.
- **Reassigning a property Angular itself sets** (e.g. an `@Input`-bound or
  Angular-initialized field) — mark such properties `readonly` instead
  [Source: https://angular.dev/style-guide].

## Security

Angular auto-sanitizes template bindings/interpolation by **security
context** (HTML, Style, URL, Resource URL) by default, treating all values
as untrusted; it **cannot sanitize Resource URLs containing arbitrary
code** — that gap requires manual `bypassSecurityTrustResourceUrl` review
[Source: https://angular.dev/best-practices/security]. When bypass is
genuinely needed, `DomSanitizer` exposes `bypassSecurityTrustHtml`,
`bypassSecurityTrustScript`, `bypassSecurityTrustStyle`,
`bypassSecurityTrustUrl`, `bypassSecurityTrustResourceUrl` — using them
introduces vulnerabilities if the trusted value is attacker-controlled, and
the method chosen must match the actual usage context
[Source: https://angular.dev/best-practices/security].

**CSRF/XSRF** (concrete detail beyond `frontend-architecture`'s high-level
note): `HttpClient`'s built-in interceptor reads a token from the
`XSRF-TOKEN` cookie and sets it as the `X-XSRF-TOKEN` header on mutating
(POST/PUT/DELETE) same-origin requests; GET requests are excluded because
same-origin policy already prevents cross-domain retrieval of authenticated
responses. Customize via `withXsrfConfiguration({...})` (custom
cookie/header names) or disable entirely via `withNoXsrfProtection()`,
composed into `provideHttpClient(...)`
[Source: https://angular.dev/best-practices/security]. `HttpClient` also
automatically strips the `")]}',\n"` XSSI security prefix from JSON
responses [Source: https://angular.dev/best-practices/security].

**CSP/Trusted Types**: documented minimal CSP header is
`default-src 'self'; style-src 'self' 'nonce-randomNonceGoesHere'; script-src 'self' 'nonce-randomNonceGoesHere';`,
with the server generating a unique per-request nonce, suppliable via
workspace config (`autoCsp`), the `ngCspNonce` template attribute, or the
`CSP_NONCE` injection token. Trusted Types policies: `angular` (internal,
reviewed code), `angular#bundler` (CLI lazy chunks), `angular#unsafe-bypass`
(apps using sanitizer bypass), `angular#unsafe-jit` (JIT compiler),
`angular#unsafe-upgrade` (AngularJS hybrid apps)
[Source: https://angular.dev/best-practices/security]. **AOT compilation**
(the CLI production default) is documented as a security measure — it
prevents template-injection vulnerabilities and "should always be used in
production" [Source: https://angular.dev/best-practices/security]. Deep
threat-modeling method beyond Angular specifics is owned by
`security-engineering`, not restated here.

## Performance

Zoneless (stable/default v21+) removes Zone.js's global monkey-patch
overhead entirely and reduces change-detection passes to explicit
notifications, documented as improving both raw performance and Core Web
Vitals [Source: https://angular.dev/guide/zoneless]. **[Version-sensitive,
v22]** New components defaulting to `ChangeDetectionStrategy.OnPush` limits
re-render checks to input/signal changes/events rather than every
Zone-detected tick [Source: https://raw.githubusercontent.com/angular/angular/main/CHANGELOG.md
(v22.0.0 entry)]. `@defer` (idle/viewport/interaction/hover/timer/immediate
triggers, plus prefetching) is the primary template-level lazy-loading
primitive for shrinking initial bundle size
[Source: https://angular.dev/guide/templates/defer]. `NgOptimizedImage`
(`ngSrc` in place of `src`, explicit `width`/`height`, `priority` on the LCP
image) auto-generates responsive `srcset`, defaults non-priority images to
`loading=lazy`, and targets Largest Contentful Paint specifically
[Source: https://angular.dev/best-practices/images]. Deep cross-cutting
performance method is owned by `performance-engineering`.

## Testing

**[Version-sensitive, v21+]** Vitest is now the default test runner for new
Angular CLI projects, replacing Karma: "This guide covers the default
testing setup for new Angular CLI projects, which uses Vitest," running in
Node.js with jsdom or happy-dom for DOM emulation
[Source: https://angular.dev/guide/testing]. Real-browser testing remains
available via providers like Playwright or WebdriverIO for browser-specific
coverage. **Karma/Jasmine remain fully supported for existing projects —
there is no forced migration**, and Angular publishes a dedicated official
**"Migrating from Karma to Vitest"** guide
(`angular.dev/guide/testing/migrating-to-vitest`)
[Source: https://angular.dev/guide/testing]: don't assume a pre-v21 project
is on Vitest, and don't force a migration without a concrete driver — check
the actual configured runner before writing new tests. Component **test
harnesses** are a first-class, documented testing utility (harness
overview, using harnesses, creating custom harnesses, adding harness
support for additional environments) [Source: https://angular.dev/guide/testing].
`TestBed` **rethrows errors by default** so framework-caught mistakes
surface during tests, configurable via `rethrowApplicationErrors: false` in
`configureTestingModule` only "as a last resort"
[Source: https://angular.dev/best-practices/error-handling]. Reactive Forms
are directly/synchronously testable without rendering the UI;
Template-Driven Forms require more familiarity with change-detection
cycles because of their async `NgModel`-driven data flow
[Source: https://angular.dev/guide/forms]. Deep test-strategy method beyond
Angular specifics is owned by `SK-QA-001`.

## Failure handling

- If the Angular major version cannot be determined, ask for it or state
  explicitly which major the guidance assumes — never assume "latest"
  silently, since the TS/Node floor, zoneless default, and OnPush default
  are all breaking changes gated per major.
- If shell is unavailable/denied, produce advisory component/service/config
  code and state explicitly that `ng generate`/`ng update`/tests were not
  run.

## Escalation

- Removing Zone.js from `angular.json` polyfills, or running `ng update`
  across a major version, is a breaking-change-bearing operation — confirm
  explicitly before applying, since each major has removed or renamed APIs
  (see the per-major breaking-change entries cited in Knowledge/Performance).

## Outputs & verification

- **Outputs:** Angular component/service/DI code using version-correct
  APIs, a change-detection or standalone/NgModule structural change, and
  version-gated analysis tagged with the applicable major.
- **Verify:** every TypeScript/Node.js/RxJS version claim matches the
  confirmed Angular major's floor; zoneless-vs-Zone.js guidance matches the
  codebase's actual provider configuration; standalone-vs-NgModule guidance
  matches the codebase's actual structure rather than an assumed default.

## References

- Primary source: [`research/technologies/angular.md`](../../research/technologies/angular.md)
  (angular.dev, `blog.angular.dev`, and the `angular/angular` GitHub
  CHANGELOG.md; retrieved 2026-09-09).
- Version-floor table cross-checked against
  [`research/knowledge-maps/version-matrix.md`](../../research/knowledge-maps/version-matrix.md)
  (Angular row).
- Parent skills: [`SK-FE-001` frontend-architecture](../frontend-architecture/SKILL.md)
  — owns the generic frontend-structure method and the
  React-vs-Vue-vs-Angular comparison
  ([references/framework-comparison.md](../frontend-architecture/references/framework-comparison.md));
  `SK-FE-005` rendering-strategy (not yet authored) — will own the SSR/SSG
  rendering-mode decision.
- Related (forthcoming, being authored alongside this skill): `SK-TECH-typescript`
  — Angular is TypeScript-first; the version-floor table above is the
  concrete coupling point between the two skills.
- Angular itself publishes official "Agent Skills" for AI coding agents
  (`angular-developer`, `angular-new-app`) as of v22
  [Source: https://angular.dev/ai/agent-skills] — worth being aware of as a
  point of comparison/divergence, not duplicated here.
- Full source list: see `skill.yaml.source_references`.
