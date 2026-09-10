# Scenario: S11 — jQuery module modernized to Vue

**Category:** Legacy-code tasks
**Complexity:** multi-step (assessment, target-structure decision, and staged
implementation each precede the next; spans the modernization, frontend-
architecture, and Vue-technology domains)
**Risk level:** reversible-write (code edits only, fully revertible via VCS;
no destructive, outward-facing, or production-deploy action is inherent to
the task itself — though legacy-modernization's own `escalation` field still
gates *execution* of the plan behind explicit confirmation, see below)

## Task

"We have an old jQuery-based module, modernize it to Vue."

This is the complete, verbatim request. No target Vue version is named, no
file path is given beyond "the module," and no clarifying detail follows.

## Repository signals

- `package.json` lists `jquery` (`^3.6.0`) as a direct dependency. No `vue`,
  `@vue/*`, `vue-router`, or `pinia` entries exist yet — the target framework
  is not yet installed anywhere in the repo.
- `src/widgets/order-panel.js` (~400 lines): direct DOM manipulation via
  `$(...)` selectors, manual event binding (`$('#submit').on('click', ...)`),
  and ad hoc shared state stored on `window.OrderPanelState`. This is "the
  module" the request refers to.
- No `.vue` Single-File Component files exist anywhere in the repo.
- No `vite.config.*` and no `@vitejs/plugin-vue` — Vue tooling isn't wired
  up yet either.
- `tests/order-panel.spec.js` exists: a DOM-fixture-based spec file, last
  touched (per `git blame`) three years ago, covering roughly half of the
  module's exported functions. It currently passes in CI.
- `.github/workflows/ci.yml` runs this spec file plus lint on every PR; no
  performance budget, no security-scanning step specific to this module.
- `CHANGELOG.md` shows no dependency bump touching this module since before
  jQuery 3's own release line matured — the module has sat untouched across
  at least one library-wide deprecation boundary.
- Nothing elsewhere in the repo names React or Angular; no other frontend
  framework is in use anywhere in the codebase.

## Expected activation set

**Must activate:**
- `SK-CONV-005` (legacy-modernization) — the task is "modernize [a module]
  to Vue," matching the activation condition "Migrating off a deprecated
  approach" (jQuery's direct-DOM/manual-binding paradigm) and "Modernizing
  outdated patterns"; this is not a routine minor bump, so the
  non-activation condition doesn't apply.
- `SK-TECH-vue` — the named, and only, target framework; owns SFC/
  reactivity specifics and the XSS-in-template-escaping concern for the
  actual rewrite.
- `SK-FE-001` (frontend-architecture) — `order-panel.js`'s ad hoc
  `window.OrderPanelState` global is exactly the kind of state-management/
  component-decomposition decision FE-001 owns, and it must be resolved
  *before* there is a target shape for `SK-TECH-vue` to specialize into.
- `SK-CONV-004` (refactoring) and `SK-QA-001` (testing-strategy) —
  activate, but via composition, not independent top-level matching. See
  "Composition-edge reasoning" below.

**Composition-edge reasoning.** `SK-CONV-005` declares
`depends_on_skills: [SK-CONV-004, SK-QA-001]`, and `SK-CONV-004` itself
declares `depends_on_skills: [SK-QA-001]`. Per
`core/dependency-architecture/README.md`'s edge vocabulary, `depends_on_skills`
*is* the "parent — composition" edge, defined as "A invokes B as a sub-step
during its own work" — not "commonly co-activated" (that's `related_skills`,
a different field). `SK-CONV-005`'s own `verification` list makes this
concrete rather than abstract: "Behavior-preservation for each incremental
step is verified via refactoring's method, not assumed." So yes —
a `depends_on_skills` hard edge means the dependency's *method actually
runs* as part of the depending skill's own execution, even though
`SK-CONV-004`/`SK-QA-001` never independently matched an activation
condition against this task's own text. The distinction that matters for
scoring: these two should appear in the run's routing record with an
activation *reason* of "composed by `SK-CONV-005` per `depends_on_skills`,"
not "matched own activation_conditions" — and their absence from a
top-level, keyword-driven activation list is not itself a defect. Their
absence from the run's *evidence* (no behavior-preservation check ever
executed against any staged increment) is a defect: see the assertions
below.

**Must NOT activate:**
- `SK-TECH-react`, `SK-TECH-angular` — no signal for either framework
  anywhere in the repo; explicitly ruled out by the repository signals.
- `SK-FE-005` (rendering-strategy) — its own non-activation condition
  ("Pure SPA with no SEO/SSR concern") applies directly; `order-panel.js`
  is a widget, not a page, and nothing in the task or signals raises SSR/
  SEO/indexability.
- `SK-QA-002` (security-engineering) — no trust boundary, injection, auth,
  or secrets concern is named; the one security-adjacent detail in play
  (template-escaping) is `SK-TECH-vue`'s own declared note, not a reason to
  pull in the cross-cutting security skill.
- `SK-DISC-002` (solution-architecture) — related to `SK-CONV-005` via
  `related_skills` (complementary, no hard ordering), not a dependency; the
  scope here is one ~400-line module, not a system-level architecture
  decision, so the full solution-architecture skill isn't warranted.
- `SK-DATA-006` (data-migration) — also only `related_skills` on
  `SK-CONV-005`; nothing in the task touches a data store or schema.

**Uncertain / acceptable either way:**
- `SK-DISC-001` (requirements-engineering) — the task names no target Vue
  version, and `SK-CONV-005`'s own `target-versions` input is `required:
  true`. A router could reasonably invoke requirements-engineering to pin
  this down, or could treat it as a single narrow open question that
  `SK-CONV-005`'s own assessment step surfaces directly (`open_questions[]`)
  without a separate activation. Either is acceptable; what is not
  acceptable is silently assuming a version.
- `SK-CONV-007` (code-review) / `SK-CONV-001` (git-conventions) — a
  thorough router might attach a pre-merge review pass or note the staged-
  commit convention for the rollback points; neither is required for this
  scenario's core assertions.

## Expected sequencing and parallelization

```
SK-CONV-005                                   # frames assessment + staged plan
  → SK-FE-001                                 # target component/state-management decision
  → SK-TECH-vue                               # specializes FE-001's decision into the SFC/reactivity edit
⛔ SK-CONV-005                                 # staged plan + rollback points presented for confirmation
                                               #   before execution begins (escalation field)
⟳ ( SK-TECH-vue → SK-CONV-004 → SK-QA-001 )   # per staged increment: apply the Vue-specific edit,
                                               #   then refactoring's behavior-preservation method,
                                               #   then testing-strategy's verification — repeat per
                                               #   increment until the staged plan is exhausted
```

`SK-FE-001 → SK-TECH-vue` is sequential, not parallel, for the same reason
as S13's `SK-BE-002 → SK-TECH-express`: the generic skill makes the
structural decision the technology skill specializes into a concrete edit,
so the second cannot start until the first's decision exists. The
`⟳` loop is scoped to each individually-verifiable staged step, per
`SK-CONV-004`'s own verification bullet ("changes are applied in small,
independently-verifiable steps"); there is no cross-increment parallelism
because every increment writes to the same target file
(`order-panel.js` → its `.vue` replacement), which fails the parallel-safe
"disjoint targets" test (IC-5).
