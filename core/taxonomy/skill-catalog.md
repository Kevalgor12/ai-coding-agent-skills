# Skill Catalog

Full specification for every proposed skill, per the 13-field schema defined in
[README.md](README.md#per-skill-specification-schema). Organized by layer/domain.

- **Layers 0–3 (generic skills)** get individual full specs below.
- **Layer 4 (technology skills)** are defined once by a shared template, then
  enumerated in a parameter table — because they are structurally identical
  (same activation shape, same "specializes a Layer-3 skill" relationship) and
  writing 30+ near-duplicate specs would violate the very minimal-duplication
  and maintainability principles the taxonomy is built on. Each row maps 1:1 to
  a researched technology doc.

Execution tier (A/B/C) is per [README.md](README.md#vendor-neutrality-model-how-a-skill-stays-portable).

---

# Layer 0 — Orchestration & Meta

## SK-ORCH-001 · skill-router

- **Purpose:** Read an incoming task and determine which skills/domains apply, in what order.
- **Scope:** Intent classification and skill selection; does not do the domain work itself.
- **Responsibilities:** Parse task intent; detect the stack in play (languages, frameworks, DBs) from files/config; select the minimal sufficient skill set; sequence them; hand off.
- **Inputs:** User task, repository signals (package manifests, config files, file extensions).
- **Outputs:** An ordered, de-duplicated list of skills to activate, with rationale.
- **Activation conditions:** A task spans more than one domain, or the correct skill set is non-obvious.
- **Non-activation conditions:** A single, unambiguous skill clearly owns the task (let it trigger directly — routing overhead is waste).
- **Dependencies:** None (Layer 0 root). Agent capability: file read.
- **Conflicts:** None; it precedes other skills rather than competing.
- **Related:** `SK-ORCH-002`, `SK-ORCH-003`, `SK-DISC-003`.
- **Evaluation requirements:** Given seeded multi-domain tasks, selects the expected skill set with no missing essential skill and no more than N spurious selections; correctly detects stack from manifests.
- **Tier:** A.

## SK-ORCH-002 · capability-adapter

- **Purpose:** Reconcile a skill's required agent capabilities against what the *host* agent can actually do, and choose execute-vs-advise-vs-fallback.
- **Scope:** The vendor-neutrality enforcement point. Owns the mapping from abstract capability → host reality.
- **Responsibilities:** Detect host execution capabilities (shell, browser, container, MCP servers present); for each activated skill's declared requirements, decide Tier A/B/C viability; select documented fallbacks (e.g. Playwright-via-MCP on Claude Code); surface when a task simply cannot execute in the current ecosystem.
- **Inputs:** Activated skills' capability declarations; host-agent capability signals.
- **Outputs:** Per-skill execution decision (execute / degrade-to-advisory / fallback route / not-possible-here) with reason.
- **Activation conditions:** Any Tier B or Tier C skill is about to act.
- **Non-activation conditions:** All active skills are Tier A (pure advisory) — nothing to adapt.
- **Dependencies:** None. Reference: [agent-capability map](../../research/knowledge-maps/agent-capability-map.md).
- **Conflicts:** None; it gates rather than competes.
- **Related:** Every Tier B/C skill; `SK-ORCH-001`.
- **Evaluation requirements:** Given simulated host profiles (e.g. "no browser automation", "no shell", "MCP Postgres present"), routes each capability to the correct execute/fallback/refuse decision; never claims execution succeeded when the capability was absent.
- **Tier:** A.

## SK-ORCH-003 · workflow-composer

- **Purpose:** Sequence a multi-skill effort into an ordered workflow (e.g. plan → implement → test → review) and carry state between stages.
- **Scope:** Cross-skill orchestration of larger tasks; not the work of any one stage.
- **Responsibilities:** Establish stage order; define hand-off artifacts between skills; enforce that review/test stages run before "done"; prevent skipping conventions (git, comments) at the end.
- **Inputs:** Router output; task goal.
- **Outputs:** A staged plan with explicit gates and the artifact each stage passes on.
- **Activation conditions:** A task requires several skills across build + verify phases.
- **Non-activation conditions:** Single-stage tasks; pure Q&A.
- **Dependencies:** `SK-ORCH-001`. Agent capability: sub-agent delegation *optional* (declared, not required — history-inheritance varies per the capability map, so composer must not assume it).
- **Conflicts:** None.
- **Related:** `SK-DISC-003`, `SK-CONV-007`, `SK-QA-001`.
- **Evaluation requirements:** For a seeded feature task, produces a stage order that places verification and conventions after implementation and never marks completion with an unrun required gate.
- **Tier:** A (B if it delegates via sub-agents).

---

# Layer 1 — Discovery, Requirements & Architecture

## SK-DISC-001 · requirements-engineering

- **Purpose:** Turn a vague request into explicit, testable requirements and surface hidden constraints before code is written.
- **Scope:** Functional/non-functional requirements, acceptance criteria, constraint elicitation. Not solution design.
- **Responsibilities:** Extract goals; identify implicit constraints; write acceptance criteria; flag ambiguities as questions rather than guessing.
- **Inputs:** User request, existing docs/tickets.
- **Outputs:** Structured requirements + acceptance criteria + open questions.
- **Activation conditions:** Task is under-specified or high-stakes; a feature is being scoped.
- **Non-activation conditions:** Requirements are already explicit; trivial/mechanical change.
- **Dependencies:** None.
- **Conflicts:** None.
- **Related:** `SK-DISC-002`, `SK-DISC-003`, `SK-DISC-004`.
- **Evaluation requirements:** Given an ambiguous request, produces acceptance criteria covering the stated goal and raises the material ambiguities a human reviewer would flag; does not invent unrequested scope.
- **Tier:** A.

## SK-DISC-002 · solution-architecture

- **Purpose:** Choose an architecture and technology approach that fits the requirements and constraints.
- **Scope:** System decomposition, component boundaries, technology selection *rationale*. Consumes the decision matrix; does not re-derive per-tech facts.
- **Responsibilities:** Propose component/service structure; select patterns; make and record technology choices with tradeoffs; identify cross-cutting concerns (auth, observability, caching) early.
- **Inputs:** Requirements; constraints; [technology-decision-matrix](../../research/knowledge-maps/technology-decision-matrix.md).
- **Outputs:** An architecture description + chosen stack + recorded tradeoffs/risks.
- **Activation conditions:** New system/feature of non-trivial size; a significant tech choice is open.
- **Non-activation conditions:** Architecture is fixed and the task is implementation within it.
- **Dependencies:** `SK-DISC-001` (ideally). References Layer-3 domain skills for feasibility.
- **Conflicts:** None.
- **Related:** All Layer-3 skills; `SK-CONV-005`.
- **Evaluation requirements:** For a seeded requirement set, proposes an architecture whose components cover all requirements, records at least the tradeoffs the decision matrix documents, and does not select a combination the research flags as inappropriate.
- **Tier:** A.

## SK-DISC-003 · technical-planning

- **Purpose:** Decompose an agreed approach into an ordered, dependency-aware task plan.
- **Scope:** Task breakdown, sequencing, effort/risk flags. Not project tracking (that is `SK-DISC-004`).
- **Responsibilities:** Break work into steps; order by dependency; flag risky/uncertain steps; identify what to verify at each step.
- **Inputs:** Architecture/requirements; repository state.
- **Outputs:** An ordered task plan with dependencies and verification points.
- **Activation conditions:** Multi-step implementation; user asks for a plan.
- **Non-activation conditions:** Single-step change.
- **Dependencies:** None hard.
- **Conflicts:** Overlaps the host agent's own native planning; defer to native plan tooling when present (declared, not assumed).
- **Related:** `SK-ORCH-003`, `SK-DISC-002`.
- **Evaluation requirements:** Produces a plan whose step order respects real dependencies (no step depends on a later one) and attaches a verification step to each build step.
- **Tier:** A.

## SK-DISC-004 · project-management

- **Purpose:** Track work as issues/milestones and keep status legible across a longer effort.
- **Scope:** Issue/milestone framing, status tracking, changelog/release-notes framing. **Thin** — see [analysis](taxonomy-analysis.md#missing-capabilities); the only researched touchpoint is GitHub issues.
- **Responsibilities:** Frame tasks as trackable items; maintain status; draft release notes/changelogs.
- **Inputs:** Task plan; repo issue/PR state.
- **Outputs:** Issue/milestone drafts; status summaries; changelog entries.
- **Activation conditions:** Long-running effort; user asks for tracking/release notes.
- **Non-activation conditions:** One-off change; no tracking system in use.
- **Dependencies:** Agent capability: Git/GitHub integration (Tier B/C — the capability map shows PR/issue automation is *not* uniform).
- **Conflicts:** None.
- **Related:** `SK-CONV-001`, `SK-CONV-008`, `SK-INFRA-002`.
- **Evaluation requirements:** Given a completed change, drafts a changelog entry that matches the change and a well-formed issue; degrades to advisory text when no tracker/GitHub access exists.
- **Tier:** A (advisory) / C (if it writes to a tracker).

---

# Layer 2 — Engineering Conventions (universal practice)

> The two skills the brief singled out (`SK-CONV-001`, `SK-CONV-002`) are
> specified in extra depth. Both are ruled **first-class** — see
> [taxonomy-analysis.md](taxonomy-analysis.md#mandated-skill-rulings).

## SK-CONV-001 · git-conventions  *(mandated · first-class)*

- **Purpose:** Produce professional, convention-compliant Git branch names and commit messages, conforming to an existing repository convention when one exists and applying a sane professional default when none does.
- **Scope:** The *text and structure* of branch names and commit messages. **Not** branching strategy, rebasing, or PR mechanics (that is `SK-CONV-008`).
- **Responsibilities:**
  - **Detect existing convention first.** Inspect recent `git log`, any `commitlint`/`.commitlintrc`/Conventional-Commits config, `CONTRIBUTING`/`CLAUDE.md` guidance, and existing branch-name patterns. If a convention is detected, conform to it and do not impose the default.
  - **Default prefix set (only when no convention exists):** `feat`, `feature`, `fix`, `bugfix`, `hotfix`, `refactor`, `chore`, `docs`, `test`, `perf`, `ci`, `build`, `release`. Choose the prefix that matches the actual change.
  - **Commit messages:** concise, imperative subject; body only when it adds real context; never a decorative or auto-generated body by default. (Honors the project's own stated preference for one-line messages.)
  - **Branch names:** lowercase, hyphenated, prefixed to match the change type, short and descriptive.
  - **Never** invent scope, fabricate a ticket ID, or add a signature/attribution line the repo convention does not already use.
- **Inputs:** The staged/described change; repository git history and any commit-lint/contribution config.
- **Outputs:** A proposed branch name and/or commit message string (advisory), or the actual commit/branch when the host permits and the user authorized it.
- **Activation conditions:** A commit or branch is about to be created; the user asks for a commit message or branch name.
- **Non-activation conditions:** No version control in the workspace; the user explicitly dictates an exact message/branch (use theirs verbatim); pushing/PR concerns (route to `SK-CONV-008`).
- **Dependencies:** Agent capability: git access (Tier B to commit; Tier A to propose text). No skill dependencies.
- **Conflicts:** Must yield to a detected repository convention over its own defaults — the convention always wins. Defers to explicit user instruction.
- **Related:** `SK-CONV-008` (git-workflow), `SK-DISC-004`, `SK-CONV-007`.
- **Evaluation requirements:**
  - Repo *with* Conventional Commits config → output conforms to that config, not the default set.
  - Repo *with* a different existing style (e.g. Jira-key prefixes, sentence-case subjects) → output matches the observed style.
  - Repo *with no* convention → uses the default prefix set, correct prefix for the change type, concise imperative subject, one line unless a body is warranted.
  - Rejects/repairs a non-professional message (vague "update stuff", wrong type, decorative noise, spurious signature).
  - Never fabricates a ticket reference or attribution not already in use.
- **Tier:** A (propose) / B (commit).

## SK-CONV-002 · code-commenting  *(mandated · first-class)*

- **Purpose:** Write useful, natural code comments that explain what code cannot say for itself, and actively prevent comment noise.
- **Scope:** Comment content and placement in source the agent writes or edits. Not prose documentation (that is `SK-CONV-006`).
- **Responsibilities:**
  - **Require comments that carry real information:** the *why*, non-obvious constraints, invariants, workarounds for specific bugs, and behavior that would surprise a reader.
  - **Prevent noise, specifically:**
    - phase/step narration comments (`// Step 1:`, `// Now we loop over…`),
    - AI/tool signatures or attribution in code comments (`// Generated by…`, co-author lines inside code),
    - decorative comments (banner bars, `////////`, ASCII separators),
    - comments that merely restate what the code already says plainly.
  - Match the surrounding file's existing comment style and density.
  - Prefer deleting a stale/redundant comment over "fixing" it.
- **Inputs:** The code being written/edited; the file's existing comment conventions.
- **Outputs:** Comments inserted/edited in source (or review findings flagging comment noise).
- **Activation conditions:** Writing or substantially editing source code; reviewing code for comment quality.
- **Non-activation conditions:** Documentation prose / READMEs / markdown (route to `SK-CONV-006`); a file whose established style legitimately uses banner conventions (respect the local norm).
- **Dependencies:** Agent capability: file write. No skill dependencies.
- **Conflicts:** None; composes with every code-producing skill.
- **Related:** `SK-CONV-003`, `SK-CONV-006`, `SK-CONV-007`.
- **Evaluation requirements:**
  - Given code with a genuinely non-obvious constraint, produces a *why* comment.
  - Given obvious code, produces *no* restating comment.
  - Flags/removes step-narration, AI signatures, decorative bars, and obvious-restatement comments in a review fixture.
  - Preserves and matches a file's legitimate existing comment style.
- **Tier:** A.

## SK-CONV-003 · code-quality

- **Purpose:** Enforce clean, readable, idiomatic code — naming, structure, size, cohesion — independent of language.
- **Scope:** Structural/readability quality of code the agent writes or reviews. Not correctness bugs (review), not performance (perf skill).
- **Responsibilities:** Meaningful naming; appropriate function/module size; avoid premature abstraction and dead code; language-idiomatic structure; no over-engineering.
- **Inputs:** Code being written/edited; language context.
- **Outputs:** Cleaner code, or quality findings.
- **Activation conditions:** Writing non-trivial code; a quality pass is requested.
- **Non-activation conditions:** Throwaway snippet; user wants a quick spike explicitly.
- **Dependencies:** None hard; specialized by Layer-4 language skills for idiom.
- **Conflicts:** None.
- **Related:** `SK-CONV-002`, `SK-CONV-004`, `SK-CONV-007`.
- **Evaluation requirements:** On a fixture with poor naming/over-abstraction/dead code, produces improvements a reviewer agrees with and introduces no premature abstraction of its own.
- **Tier:** A.

## SK-CONV-004 · refactoring

- **Purpose:** Improve the structure of existing code without changing its behavior.
- **Scope:** Behavior-preserving transformation. Requires a safety net (tests) or explicit acknowledgement of its absence.
- **Responsibilities:** Identify a refactoring target; apply behavior-preserving changes in small steps; verify behavior is unchanged (tests / equivalence reasoning); avoid scope creep into feature changes.
- **Inputs:** Target code; available tests.
- **Outputs:** Refactored code + statement of how behavior-preservation was checked.
- **Activation conditions:** User asks to refactor; a change is blocked by structural debt.
- **Non-activation conditions:** New feature work (that is not refactoring); no way to verify behavior and user hasn't accepted the risk.
- **Dependencies:** `SK-QA-001` (verification). Agent capability: shell (to run tests, Tier B) — degrades to reasoning-only with a stated caveat.
- **Conflicts:** Must not bundle behavior changes; if it finds a bug, hands off rather than silently fixing.
- **Related:** `SK-CONV-003`, `SK-CONV-005`, `SK-QA-001`.
- **Evaluation requirements:** On a fixture with tests, refactors and keeps tests green; when no tests exist, explicitly flags the unverifiable risk instead of proceeding silently.
- **Tier:** B.

## SK-CONV-005 · legacy-modernization

- **Purpose:** Safely evolve legacy/outdated code toward current practice and supported versions.
- **Scope:** Incremental modernization, dependency/version upgrades, strangler-style migration. Consumes the version matrix and per-tech breaking-change data.
- **Responsibilities:** Assess current vs. target state; plan incremental steps with rollback points; apply breaking-change migrations using the researched breaking-change notes; avoid big-bang rewrites unless justified.
- **Inputs:** Legacy code; target versions; [version-matrix](../../research/knowledge-maps/version-matrix.md) and per-tech breaking-changes sections.
- **Outputs:** A staged modernization plan and/or applied incremental changes.
- **Activation conditions:** Upgrading a major version; modernizing outdated patterns; migrating off a deprecated approach.
- **Non-activation conditions:** Greenfield code; a routine minor-version bump with no breaking changes.
- **Dependencies:** `SK-CONV-004`, `SK-QA-001`; relevant Layer-4 tech skills for version specifics.
- **Conflicts:** None.
- **Related:** `SK-DISC-002`, `SK-DATA-006`.
- **Evaluation requirements:** For a seeded major-version upgrade, produces a plan that addresses the documented breaking changes for that version and sequences steps with verification/rollback points.
- **Tier:** B.

## SK-CONV-006 · technical-documentation

- **Purpose:** Produce and maintain accurate prose documentation — READMEs, API docs, ADRs, inline module docs.
- **Scope:** Human-readable documentation artifacts. Not in-code comments (that is `SK-CONV-002`).
- **Responsibilities:** Write docs that match current behavior; keep them concise and non-duplicative; record architectural decisions (ADRs); avoid docs that will rot (prefer generating from source where possible, e.g. OpenAPI).
- **Inputs:** Code/architecture; existing docs.
- **Outputs:** Documentation files/sections.
- **Activation conditions:** User asks for docs; a public interface changed; an architectural decision needs recording.
- **Non-activation conditions:** In-code commenting (route to `SK-CONV-002`); the user explicitly wants code only.
- **Dependencies:** None hard.
- **Conflicts:** None.
- **Related:** `SK-CONV-002`, `SK-BE-002` (API docs), `SK-TECH-openapi-swagger`.
- **Evaluation requirements:** Produced docs match the actual current interface (no drift) and do not merely restate code; ADRs capture decision + rationale + alternatives.
- **Tier:** A.

## SK-CONV-007 · code-review

- **Purpose:** Review a change for correctness, quality, security, and convention adherence, and report actionable findings.
- **Scope:** Adversarial review of a diff/PR. The general **review** skill; specialized reviews (security, performance) delegate to their domain skills.
- **Responsibilities:** Find correctness bugs; check convention adherence (git, comments, quality); flag security/perf concerns by delegating to the relevant skill; rank findings by severity; distinguish confirmed from speculative.
- **Inputs:** A diff, PR, or changeset; repo conventions.
- **Outputs:** Ranked, actionable findings (optionally posted as PR comments where the host allows).
- **Activation conditions:** A change is up for review; user asks for a review; pre-merge gate.
- **Non-activation conditions:** Authoring net-new code (that is the build skills, though they may self-check); no change to review.
- **Dependencies:** `SK-QA-002`, `SK-QA-003`, `SK-CONV-002`, `SK-CONV-003` (delegated facets). Agent capability: PR posting is Tier C (not uniform per capability map).
- **Conflicts:** None.
- **Related:** All Layer-2 and Layer-4 skills.
- **Evaluation requirements:** On a fixture diff with seeded defects, surfaces the real defects, ranks by severity, avoids a high false-positive rate, and delegates security/perf findings rather than duplicating them.
- **Tier:** A (review) / C (post to PR).

## SK-CONV-008 · git-workflow

- **Purpose:** Manage branching strategy, history hygiene, merges/rebases, worktrees, and PR mechanics — the *operations* of version control.
- **Scope:** Git operations and workflow. **Not** commit/branch *text* (that is `SK-CONV-001`).
- **Responsibilities:** Choose/apply a branching model; keep history clean (safe rebase/squash); manage worktrees; open/update PRs; **guard risky operations** (force-push, reset --hard) behind confirmation per the safety rules.
- **Inputs:** Repo state; branching conventions; task.
- **Outputs:** Branch/merge/PR operations, or advisory guidance.
- **Activation conditions:** Branch creation, merge/rebase, PR management, worktree isolation.
- **Non-activation conditions:** Composing commit/branch *text* only (route to `SK-CONV-001`); no VCS present.
- **Dependencies:** `SK-CONV-001`. Agent capability: git access (Tier B), PR automation (Tier C — varies per capability map).
- **Conflicts:** None.
- **Related:** `SK-CONV-001`, `SK-CONV-007`, `SK-INFRA-002`, `SK-DISC-004`.
- **Evaluation requirements:** Applies the repo's branching model correctly; never performs a history-destroying operation without explicit confirmation; opens a well-formed PR when the host allows.
- **Tier:** B/C.

---

# Layer 3 — Domain Capability Skills (generic, tech-neutral)

## Frontend & UI/UX

### SK-FE-001 · frontend-architecture
- **Purpose:** Structure a frontend application — component architecture, state management, data flow, routing — independent of framework.
- **Scope:** Tech-neutral frontend structure. Specialized by React/Vue/Angular/Next/Nuxt tech skills.
- **Responsibilities:** Component decomposition; state-management strategy; data-fetching patterns; routing structure; separation of concerns.
- **Inputs:** UI requirements; chosen framework.
- **Outputs:** Frontend structure/decisions; scaffolding guidance.
- **Activation conditions:** Building/structuring a frontend app or feature.
- **Non-activation conditions:** Pure styling (route to `SK-FE-003`); backend work.
- **Dependencies:** Specialized by `SK-TECH-react|vue|angular|nextjs|nuxt`.
- **Conflicts:** None.
- **Related:** `SK-FE-002`, `SK-FE-003`, `SK-FE-005`.
- **Evaluation requirements:** Proposes a component/state structure that satisfies seeded UI requirements without prop-drilling anti-patterns or an unjustified global store.
- **Tier:** A.

### SK-FE-002 · ui-ux-design
- **Purpose:** Apply interaction and visual-design judgment — layout, hierarchy, responsive behavior, usability — to UI work.
- **Scope:** UX/visual-design decisions. Not implementation-specific styling syntax.
- **Responsibilities:** Information hierarchy; responsive layout; interaction states; consistency; sensible defaults over novelty.
- **Inputs:** Feature intent; brand/design constraints.
- **Outputs:** UX/layout decisions and rationale.
- **Activation conditions:** Designing or improving a user-facing interface.
- **Non-activation conditions:** Non-visual/backend tasks.
- **Dependencies:** None hard.
- **Conflicts:** None.
- **Related:** `SK-FE-003`, `SK-FE-004`, component-library tech skills.
- **Evaluation requirements:** For a seeded UI task, produces a layout/hierarchy a designer would accept and handles at least the responsive and empty/loading/error states.
- **Tier:** A.

### SK-FE-003 · styling-systems
- **Purpose:** Architect styling — design tokens, theming, responsive strategy, scoping — independent of the styling tool.
- **Scope:** Tech-neutral styling architecture. Specialized by Tailwind/Sass/CSS/shadcn/MUI tech skills.
- **Responsibilities:** Token/theme structure; responsive strategy; style scoping/encapsulation; dark-mode strategy; avoiding specificity wars.
- **Inputs:** Design system/brand; chosen styling tool.
- **Outputs:** Styling architecture and conventions.
- **Activation conditions:** Setting up or restructuring how an app is styled.
- **Non-activation conditions:** One-off style tweak with an established system already in place.
- **Dependencies:** Specialized by `SK-TECH-tailwindcss|sass|web-standards|shadcn-ui|mui`.
- **Conflicts:** None.
- **Related:** `SK-FE-002`, `SK-FE-004`.
- **Evaluation requirements:** Produces a token/theme architecture supporting theming + dark mode + responsive without duplicated magic values.
- **Tier:** A.

### SK-FE-004 · web-accessibility
- **Purpose:** Ensure UIs meet accessibility standards (semantic markup, ARIA, keyboard, contrast).
- **Scope:** Cross-cutting a11y — spans HTML, components, and testing (the concept map shows a11y touching HTML/MUI/shadcn/Playwright).
- **Responsibilities:** Semantic markup; ARIA where needed; keyboard operability; contrast; a11y regression checks.
- **Inputs:** UI/markup; a11y target (e.g. WCAG level).
- **Outputs:** Accessible markup/components; a11y findings.
- **Activation conditions:** Building user-facing UI; an a11y audit is requested.
- **Non-activation conditions:** Backend/non-UI work.
- **Dependencies:** Related to `SK-TECH-playwright` (a11y-tree automation) for verification.
- **Conflicts:** None.
- **Related:** `SK-FE-002`, `SK-TECH-web-standards`, `SK-TECH-shadcn-ui`, `SK-TECH-mui`.
- **Evaluation requirements:** On a fixture with a11y defects (missing labels, non-semantic elements, low contrast), identifies and fixes them; produced markup passes an automated a11y check.
- **Tier:** A (author) / C (browser-based verification).

### SK-FE-005 · rendering-strategy
- **Purpose:** Choose the right rendering mode — SSR/SSG/ISR/CSR/streaming/hydration — for a given page/app, including SEO implications.
- **Scope:** Rendering-mode selection and its tradeoffs. Ties frontend to SEO (the map shows rendering-choice and indexability are two sides of one mechanism).
- **Responsibilities:** Match rendering mode to content/interactivity/SEO needs; reason about hydration cost; flag SEO/perf consequences.
- **Inputs:** Page requirements (dynamism, SEO need, interactivity); chosen framework.
- **Outputs:** Rendering-mode decision + rationale.
- **Activation conditions:** Deciding how pages render in an SSR-capable framework; SEO+rendering tradeoffs arise.
- **Non-activation conditions:** Pure SPA with no SEO/SSR concern; backend work.
- **Dependencies:** Specialized by `SK-TECH-nextjs|nuxt|react|vue|angular`; related to `SK-GROW-001`.
- **Conflicts:** None.
- **Related:** `SK-FE-001`, `SK-GROW-001`, `SK-QA-003`.
- **Evaluation requirements:** For seeded page types (marketing page, dashboard, blog), recommends a defensible rendering mode and correctly flags the SEO consequence of a CSR-only choice.
- **Tier:** A.

## Backend, API & Realtime

### SK-BE-001 · backend-architecture
- **Purpose:** Structure a backend service — layering, middleware, dependency injection, error handling, graceful shutdown — independent of framework/language.
- **Scope:** Tech-neutral backend structure. Specialized by Express/Fastify/Go/Python tech skills.
- **Responsibilities:** Layering/module boundaries; middleware/interceptor design; DI; consistent error handling; graceful shutdown; config management.
- **Inputs:** Service requirements; chosen framework/language.
- **Outputs:** Backend structure/decisions.
- **Activation conditions:** Building/structuring a backend service.
- **Non-activation conditions:** Frontend-only work; pure DB modeling (route to `SK-DATA-001`).
- **Dependencies:** Specialized by `SK-TECH-express|fastify|go|python`.
- **Conflicts:** None.
- **Related:** `SK-BE-002`, `SK-BE-005`, `SK-DATA-*`.
- **Evaluation requirements:** Proposes a layered structure with consistent error handling and graceful shutdown for a seeded service spec; no business logic in the transport layer.
- **Tier:** A.

### SK-BE-002 · api-design
- **Purpose:** Design HTTP/REST APIs — resource modeling, versioning, pagination, status/error semantics, idempotency.
- **Scope:** REST/HTTP API contract design. GraphQL is `SK-BE-003`; spec tooling is `SK-TECH-openapi-swagger`.
- **Responsibilities:** Resource/route modeling; consistent status codes and error shape; pagination (incl. cursor-based); versioning strategy; idempotency; contract-first via OpenAPI where useful.
- **Inputs:** Domain model; consumer needs.
- **Outputs:** API contract/design; route definitions.
- **Activation conditions:** Designing or extending an HTTP API.
- **Non-activation conditions:** GraphQL schema design (route to `SK-BE-003`); realtime transport (route to `SK-BE-004`).
- **Dependencies:** Related `SK-TECH-openapi-swagger`; specialized by `SK-TECH-express|fastify`.
- **Conflicts:** None.
- **Related:** `SK-BE-005`, `SK-CONV-006`, `SK-DATA-001`.
- **Evaluation requirements:** Produces a contract with consistent error/status semantics and correct pagination for a seeded resource; versioning strategy stated.
- **Tier:** A.

### SK-BE-003 · graphql-api-design
- **Purpose:** Design GraphQL schemas and resolvers — type modeling, N+1 avoidance, pagination, field-level authorization, schema evolution.
- **Scope:** GraphQL-specific API design. Distinct from REST because the failure modes (N+1, over-fetching-by-resolver, versionless evolution) differ.
- **Responsibilities:** Schema/type design; resolver structure with batching to avoid N+1; connection-style cursor pagination; field-level authz; evolve-without-versioning discipline.
- **Inputs:** Domain model; consumer query needs.
- **Outputs:** GraphQL schema + resolver design.
- **Activation conditions:** Building/extending a GraphQL API.
- **Non-activation conditions:** REST/HTTP design (route to `SK-BE-002`).
- **Dependencies:** Specialized by `SK-TECH-graphql`; related `SK-DATA-002` (N+1).
- **Conflicts:** None.
- **Related:** `SK-BE-005`, `SK-DATA-002`.
- **Evaluation requirements:** Produces a schema whose resolvers batch to avoid N+1 on a seeded nested query and applies field-level authorization where required.
- **Tier:** A.

### SK-BE-004 · realtime-communication
- **Purpose:** Choose and design a realtime transport — WebSocket, Socket.IO, WebRTC, SSE — and its connection lifecycle, scaling, and auth.
- **Scope:** Realtime transport selection and design. Absorbs the raw WebSocket-API concern (see [analysis merge note](taxonomy-analysis.md#skills-to-merge)).
- **Responsibilities:** Transport selection (P2P media → WebRTC; server-push events → WS/Socket.IO/SSE); connection lifecycle/reconnection; horizontal scaling with sticky sessions/pub-sub; handshake auth.
- **Inputs:** Realtime requirement (latency, media vs. events, scale).
- **Outputs:** Transport choice + connection/scaling/auth design.
- **Activation conditions:** A feature needs realtime/bidirectional/streaming communication.
- **Non-activation conditions:** Request/response APIs suffice (route to `SK-BE-002`/`003`).
- **Dependencies:** Specialized by `SK-TECH-socketio|webrtc|websocket-api`; related `SK-TECH-redis` (pub/sub scaling).
- **Conflicts:** None.
- **Related:** `SK-BE-005`, `SK-DATA-004`.
- **Evaluation requirements:** For seeded realtime scenarios (video call vs. live dashboard vs. notifications), selects a defensible transport and addresses reconnection + multi-instance scaling.
- **Tier:** A.

### SK-BE-005 · authentication-authorization
- **Purpose:** Design authentication and authorization — sessions vs. tokens, OAuth2/OIDC flows, JWT handling, RBAC/RLS, MFA — as one coherent capability.
- **Scope:** Auth/authz across the stack. **Created to fill a gap:** the concept map shows auth fragmented across JWT/OAuth2/MFA/session/RBAC with no unifying skill.
- **Responsibilities:** Choose session vs. token model; design OAuth2/OIDC flows correctly; safe JWT handling; RBAC and DB row-level security; MFA; avoid the common auth pitfalls (secrets in tokens, missing expiry, broken flows).
- **Inputs:** Auth requirements; threat context; stack.
- **Outputs:** Auth/authz design and implementation guidance.
- **Activation conditions:** Any authentication or authorization work.
- **Non-activation conditions:** No trust boundary involved.
- **Dependencies:** `SK-QA-002` (security); related `SK-DATA-003` (RLS), tech skills for framework auth middleware.
- **Conflicts:** None.
- **Related:** `SK-BE-002`, `SK-BE-003`, `SK-QA-002`.
- **Evaluation requirements:** For a seeded auth requirement, produces a design with correct token expiry/refresh, no secrets in JWTs, and least-privilege authorization; flags the OWASP-relevant risks.
- **Tier:** A.

## Data — Databases, ORM, Caching, Search

### SK-DATA-001 · data-modeling
- **Purpose:** Design data models — relational schemas and document schemas — fitting access patterns and integrity needs.
- **Scope:** Schema/data-model design, relational and document. Not query tuning (that is `SK-DATA-003`).
- **Responsibilities:** Normalize/denormalize per access pattern; keys/relationships; constraints/integrity; document-vs-relational choice; schema validation.
- **Inputs:** Domain; access patterns; chosen DB family.
- **Outputs:** Schema design.
- **Activation conditions:** Designing or changing a data model.
- **Non-activation conditions:** Query optimization only (route to `SK-DATA-003`).
- **Dependencies:** Specialized by DB and ORM tech skills.
- **Conflicts:** None.
- **Related:** `SK-DATA-002`, `SK-DATA-003`, `SK-DATA-006`.
- **Evaluation requirements:** For seeded access patterns, produces a schema with appropriate normalization and integrity constraints; justifies relational-vs-document choice.
- **Tier:** A.

### SK-DATA-002 · orm-integration
- **Purpose:** Use an ORM/ODM correctly — schema/migration workflow, relations, and avoiding N+1 and other ORM pitfalls — independent of which ORM.
- **Scope:** Tech-neutral ORM usage patterns. Specialized by Drizzle/Prisma/TypeORM/Mongoose.
- **Responsibilities:** Model relations; eager/lazy loading to avoid N+1; migration workflow; transaction handling through the ORM; know when to drop to raw SQL.
- **Inputs:** Data model; chosen ORM.
- **Outputs:** ORM models/queries/migration setup.
- **Activation conditions:** Working through an ORM/ODM.
- **Non-activation conditions:** Raw SQL/direct-driver work with no ORM.
- **Dependencies:** Specialized by `SK-TECH-drizzle|prisma|typeorm|mongoose`; related `SK-DATA-006`.
- **Conflicts:** None.
- **Related:** `SK-DATA-001`, `SK-DATA-003`.
- **Evaluation requirements:** On a seeded nested-relation query, produces an N+1-free access pattern and a correct migration; drops to raw SQL only when justified.
- **Tier:** B.

### SK-DATA-003 · database-operations
- **Purpose:** Operate a database well — indexing, query optimization, transactions/isolation, connection pooling, replication/HA awareness.
- **Scope:** DB operational concerns beyond schema. Specialized by each DB tech skill.
- **Responsibilities:** Index strategy; read/analyze query plans; transaction/isolation choices; pool sizing; awareness of replication/backup/PITR.
- **Inputs:** Schema; workload; chosen DB.
- **Outputs:** Index/query/transaction/pooling recommendations or changes.
- **Activation conditions:** Query performance, transactions, indexing, or pooling are in play.
- **Non-activation conditions:** Pure schema design (route to `SK-DATA-001`).
- **Dependencies:** Specialized by DB tech skills; related `SK-QA-003`.
- **Conflicts:** None.
- **Related:** `SK-DATA-001`, `SK-DATA-004`.
- **Evaluation requirements:** For a seeded slow query, proposes an index/rewrite that addresses the plan; chooses a defensible isolation level for a seeded transaction scenario.
- **Tier:** B.

### SK-DATA-004 · caching-strategy
- **Purpose:** Design caching — what to cache, where (client/CDN/app/DB), invalidation, and TTLs — across the stack.
- **Scope:** Cross-cutting caching (the map shows caching spanning Redis, ORMs, Next/Nuxt rendering, Docker/CI layers).
- **Responsibilities:** Choose cache layer(s); invalidation strategy (the hard part); TTL/eviction; avoid stale-data and thundering-herd pitfalls.
- **Inputs:** Access/latency requirements; data volatility.
- **Outputs:** Caching design.
- **Activation conditions:** Performance/scale needs caching; a cache layer is being added.
- **Non-activation conditions:** No caching need.
- **Dependencies:** Related `SK-TECH-redis`, `SK-FE-005`, `SK-QA-003`.
- **Conflicts:** None.
- **Related:** `SK-DATA-003`, `SK-QA-003`.
- **Evaluation requirements:** For a seeded read-heavy workload, proposes a cache layer + invalidation that avoids serving stale data past its tolerance.
- **Tier:** A.

### SK-DATA-005 · search-integration
- **Purpose:** Add full-text and/or vector/semantic search — indexing, mapping, relevance, and the engine choice.
- **Scope:** Search capability design. Specialized by OpenSearch/Postgres-FTS/Redis.
- **Responsibilities:** Choose search approach (DB-native FTS vs. dedicated engine vs. vector); index/analyzer/mapping design; relevance tuning; keep search index in sync with source of truth.
- **Inputs:** Search requirements (full-text, semantic, scale).
- **Outputs:** Search design + indexing/sync strategy.
- **Activation conditions:** A feature needs search beyond simple queries.
- **Non-activation conditions:** A simple `WHERE`/indexed lookup suffices (route to `SK-DATA-003`).
- **Dependencies:** Specialized by `SK-TECH-opensearch|postgresql|redis`.
- **Conflicts:** None.
- **Related:** `SK-DATA-001`, `SK-AI-001` (vector/RAG).
- **Evaluation requirements:** For a seeded search need, chooses a defensible engine and designs index sync that won't silently drift from source data.
- **Tier:** B.

### SK-DATA-006 · data-migration
- **Purpose:** Evolve schemas and migrate data safely, including zero-downtime and rollback.
- **Scope:** Migration mechanics and safety. Distinct from `SK-DATA-001` (design) and `SK-CONV-005` (whole-codebase modernization).
- **Responsibilities:** Author reversible migrations; expand/contract for zero-downtime; backfill strategy; guard destructive operations behind confirmation.
- **Inputs:** Current + target schema; data volume; downtime tolerance.
- **Outputs:** Migration scripts + rollout/rollback plan.
- **Activation conditions:** Schema change on a populated/production DB.
- **Non-activation conditions:** Greenfield schema with no data.
- **Dependencies:** `SK-DATA-002`; specialized by ORM/DB tech skills.
- **Conflicts:** Must not run a destructive migration without confirmation.
- **Related:** `SK-CONV-005`, `SK-DATA-001`.
- **Evaluation requirements:** For a seeded breaking schema change, produces an expand/contract sequence that is reversible and never drops data without explicit confirmation.
- **Tier:** B.

## Infrastructure & Delivery

### SK-INFRA-001 · containerization
- **Purpose:** Containerize applications and services — image authoring, layering/caching, multi-stage builds, compose for local dev.
- **Scope:** Container concerns. In this technology set, **Docker is the dominant implementation**, so this generic skill and `SK-TECH-docker` are effectively unified (see [merge note](taxonomy-analysis.md#skills-to-merge)).
- **Responsibilities:** Write efficient, secure images (small base, non-root, layer caching, multi-stage); compose local dependency stacks; scan for vulnerabilities.
- **Inputs:** App/runtime; dependencies.
- **Outputs:** Dockerfile/compose config; image guidance.
- **Activation conditions:** Containerizing an app or standing up local dependencies in containers.
- **Non-activation conditions:** No containerization involved.
- **Dependencies:** Agent capability: shell to build/run (Tier B — the capability map shows no first-class container primitive anywhere; it's shell-wrapped everywhere).
- **Conflicts:** None.
- **Related:** `SK-INFRA-002`, `SK-QA-002`, DB tech skills (containerized local DBs).
- **Evaluation requirements:** Produces a multi-stage, non-root image with sensible layer caching for a seeded app; compose file stands up the app + a DB dependency.
- **Tier:** B.

### SK-INFRA-002 · ci-cd-pipeline
- **Purpose:** Design CI/CD pipelines — build/test/lint/deploy stages, caching, secrets/OIDC, least privilege.
- **Scope:** Pipeline design. In this set, **GitHub Actions is the dominant implementation**, so this generic skill and `SK-TECH-github-actions` are effectively unified (see [merge note](taxonomy-analysis.md#skills-to-merge)).
- **Responsibilities:** Stage design; dependency caching; run tests/lint/build as gates; secrets via OIDC not static keys; least-privilege tokens; reusable workflows.
- **Inputs:** Repo; build/test commands; deploy target.
- **Outputs:** Pipeline config.
- **Activation conditions:** Setting up or changing CI/CD.
- **Non-activation conditions:** Local-only workflow; no CI.
- **Dependencies:** Related `SK-QA-001`, `SK-INFRA-001`, `SK-CONV-008`.
- **Conflicts:** None.
- **Related:** `SK-TECH-husky` (local hooks complement CI), `SK-DISC-004`.
- **Evaluation requirements:** Produces a pipeline that gates merge on tests/lint, caches dependencies, and uses OIDC/secrets correctly (no static long-lived keys in config).
- **Tier:** A (author config) — note the capability map found **no** ecosystem drives GitHub Actions natively; treat execution as external.

### SK-INFRA-003 · deployment-release
- **Purpose:** Plan and execute deployments and releases — strategy (rolling/blue-green/canary), environment config, rollback, release tagging.
- **Scope:** Deployment/release mechanics beyond the pipeline definition. **Thin** on researched grounding beyond framework/edge deployment notes.
- **Responsibilities:** Choose a deployment strategy; manage env/config per environment; ensure rollback; coordinate release tagging/versioning.
- **Inputs:** Artifact; target environment(s); risk tolerance.
- **Outputs:** Deployment/release plan or config.
- **Activation conditions:** Deploying or cutting a release.
- **Non-activation conditions:** Local dev only.
- **Dependencies:** `SK-INFRA-002`; related `SK-CONV-001` (release commits), `SK-QA-004`.
- **Conflicts:** Must guard production-affecting actions behind confirmation.
- **Related:** `SK-INFRA-001`, `SK-CONV-005`.
- **Evaluation requirements:** For a seeded service, proposes a deployment strategy with a working rollback path and correct per-environment config separation.
- **Tier:** A (plan/config) / C (execute — host- and infra-specific).

## Quality — Testing, Security, Performance, Observability

### SK-QA-001 · testing-strategy
- **Purpose:** Decide what to test at which layer (unit/integration/e2e/component/visual/contract/load) and structure a test suite accordingly.
- **Scope:** Test strategy and structure, tech-neutral. Tool specifics come from `SK-TECH-jest-vitest|playwright`.
- **Responsibilities:** Apply the test pyramid; pick the right layer per risk; design for isolation/determinism; coverage that means something; contract tests for APIs.
- **Inputs:** Code/feature under test; risk profile.
- **Outputs:** Test plan and/or tests.
- **Activation conditions:** Writing tests; deciding test strategy; a change needs coverage.
- **Non-activation conditions:** Explicitly throwaway code.
- **Dependencies:** Specialized by `SK-TECH-jest-vitest|playwright`. Agent capability: shell to run tests (Tier B).
- **Conflicts:** None.
- **Related:** `SK-CONV-004`, `SK-CONV-007`, `SK-QA-003`.
- **Evaluation requirements:** For a seeded feature, assigns the right test layer to each risk (no e2e-for-everything, no unit-testing-a-getter) and produces deterministic tests.
- **Tier:** B.

### SK-QA-002 · security-engineering
- **Purpose:** Identify and mitigate security risks — injection, XSS, CSRF, SSRF, secrets, transport, supply-chain — across the stack.
- **Scope:** The cross-cutting security skill. Consumes the [security knowledge map](../../research/knowledge-maps/security-knowledge-map.md); tech skills reference it rather than re-documenting security.
- **Responsibilities:** Threat-model a change; apply OWASP-aligned mitigations; secrets hygiene; injection/XSS/CSRF/SSRF prevention; dependency/supply-chain checks; flag time-sensitive CVEs from the research (with re-verification caveat).
- **Inputs:** Code/architecture/change; threat context.
- **Outputs:** Security findings + mitigations.
- **Activation conditions:** Security-sensitive code; a security review; handling untrusted input, auth, or secrets.
- **Non-activation conditions:** No trust boundary or sensitive data involved.
- **Dependencies:** Related to nearly all Layer-4 skills; `SK-BE-005`.
- **Conflicts:** None.
- **Related:** `SK-CONV-007`, `SK-BE-005`, `SK-QA-003`.
- **Evaluation requirements:** On a fixture with seeded vulnerabilities (injection, XSS, exposed secret), identifies each and proposes a correct mitigation; treats CVE claims as time-sensitive and re-verifiable.
- **Tier:** A.

### SK-QA-003 · performance-engineering
- **Purpose:** Diagnose and improve performance — profiling, caching, query tuning, bundle size, connection pooling, scaling.
- **Scope:** Cross-cutting performance. Consumes the [performance knowledge map](../../research/knowledge-maps/performance-knowledge-map.md).
- **Responsibilities:** Measure before optimizing; address the dominant cost (N+1, bundle bloat, missing index, pool exhaustion); avoid premature/micro-optimization; know when caching vs. tuning is the right lever.
- **Inputs:** Perf symptom/target; profiling data if available.
- **Outputs:** Performance findings + prioritized changes.
- **Activation conditions:** A performance problem or budget is in play.
- **Non-activation conditions:** No performance concern; premature optimization the user didn't ask for.
- **Dependencies:** Related `SK-DATA-003`, `SK-DATA-004`, `SK-FE-005`.
- **Conflicts:** None.
- **Related:** `SK-QA-001`, `SK-CONV-004`.
- **Evaluation requirements:** For a seeded perf issue, identifies the dominant cost from evidence (not a guess) and proposes a change targeting it; refuses to micro-optimize a non-bottleneck.
- **Tier:** A/B.

### SK-QA-004 · observability
- **Purpose:** Instrument systems for logging, metrics, and tracing so production behavior is diagnosable.
- **Scope:** Observability design — structured logging, metrics, distributed tracing, error monitoring, alerting. Specialized by the OpenTelemetry, Prometheus, Grafana, and Sentry technology skills. **Resolved gap** (2026-09-10): a dedicated research pass on these four technologies closed the near-zero-grounding gap flagged at original taxonomy design. **Not resolved**: application-level reliability/resilience *patterns* (retries, circuit breakers, timeouts, bulkheads, graceful degradation) remain a distinct, still-open research gap — see [taxonomy-analysis.md](taxonomy-analysis.md#missing-capabilities). Observability (visibility into system behavior) and resilience (behavior under failure) are related but genuinely different disciplines; this skill does not fabricate resilience-pattern guidance to fill that separate gap.
- **Responsibilities:** Structured logging; meaningful metrics; distributed tracing; error monitoring; actionable alerting; avoid log noise / PII leakage in logs.
- **Inputs:** System; SLOs/failure modes of concern.
- **Outputs:** Instrumentation plan/changes.
- **Activation conditions:** Making a system diagnosable in production; debugging a production issue.
- **Non-activation conditions:** Local/throwaway code; a request for resilience/fault-tolerance *patterns* rather than observability instrumentation (a separate, still-open research gap).
- **Dependencies:** Specialized by `SK-TECH-opentelemetry|prometheus|grafana|sentry`; related `SK-TECH-opensearch`, `SK-TECH-docker`.
- **Conflicts:** None.
- **Related:** `SK-QA-003`, `SK-INFRA-003`.
- **Evaluation requirements:** Produces structured logs with correlation IDs and metrics tied to stated SLOs, without logging secrets/PII; correctly declines to answer a resilience-pattern request as if it were covered by this skill's grounded scope.
- **Tier:** B.

## Growth

### SK-GROW-001 · seo-optimization
- **Purpose:** Improve search visibility — indexability, structured data, canonicalization, Core Web Vitals, sitemaps, i18n hreflang.
- **Scope:** Technical SEO. **Google is the dominant search engine in scope**, so this and `SK-TECH-google-seo` are effectively unified (see [merge note](taxonomy-analysis.md#skills-to-merge)).
- **Responsibilities:** Ensure crawlability/indexability; structured data; canonical URLs; Core Web Vitals; sitemaps; hreflang; reconcile rendering strategy with indexing.
- **Inputs:** Site/pages; SEO goals.
- **Outputs:** SEO findings + changes.
- **Activation conditions:** Search visibility matters for the work.
- **Non-activation conditions:** Internal tools / non-public apps.
- **Dependencies:** Related `SK-FE-005`, `SK-QA-003`.
- **Conflicts:** None.
- **Related:** `SK-GROW-002`, `SK-FE-005`.
- **Evaluation requirements:** On a fixture page with SEO defects (missing meta/structured-data, CSR-only content, no canonical), identifies and fixes them.
- **Tier:** A / C (browser verification).

### SK-GROW-002 · web-monetization  *(thin)*
- **Purpose:** Integrate ad monetization (AdSense) — script loading, ad placement, consent management, policy compliance.
- **Scope:** Ad integration. **Thin/niche**; unified with `SK-TECH-google-adsense`.
- **Responsibilities:** Async script loading; responsive/auto ad placement; consent management (privacy); avoid policy violations that risk account suspension.
- **Inputs:** Site; monetization goals; consent/privacy requirements.
- **Outputs:** Ad-integration changes + consent handling.
- **Activation conditions:** Adding/adjusting ad monetization.
- **Non-activation conditions:** No monetization; internal apps.
- **Dependencies:** Related `SK-GROW-001`, `SK-QA-002` (consent/privacy).
- **Conflicts:** None.
- **Related:** `SK-GROW-001`.
- **Evaluation requirements:** Integrates ads with async loading and consent handling; flags placements/patterns that violate documented policy.
- **Tier:** A / C.

## AI / LLM

*Resolved 2026-09-10.* Originally one thin, research-gap-flagged placeholder
(`SK-AI-001`). A dedicated research pass (Anthropic Claude API, OpenAI API,
OWASP Top 10 for LLM Applications 2026) and a principal-architect taxonomy
pass decomposed it into 8 skills against the master plan's 14 named
candidates — merging tightly-coupled pairs (prompt+context,
structured-output+tool-calling, RAG+embeddings, evaluation+hallucination-mitigation),
declining a 9th "AI Observability" skill (folded into the root skill as a
lightweight extension of `SK-QA-004`), and declining a new "Vector Search"
skill (already covered by `SK-DATA-005`). See
[taxonomy-analysis.md](taxonomy-analysis.md#missing-capabilities).

### SK-AI-001 · llm-application-engineering
- **Purpose:** Decide the architecture of an LLM-powered feature — which AI/LLM disciplines apply and how they compose — and own lightweight LLM-specific observability.
- **Scope:** The AI/LLM domain's root skill. Composes `SK-AI-002`–`SK-AI-008` selectively rather than reimplementing them; no dominant single LLM-provider technology to specialize into (model selection, `SK-AI-006`, is itself the vendor-neutral decision layer, grounded in both Anthropic's and OpenAI's documented guidance). Also owns LLM-call observability (prompt/completion logging, token/cost tracking, per-call latency) as a lightweight extension of the already-authored `SK-QA-004`, not as a separate skill — research found no LLM-specific observability concern deep enough to warrant one.
- **Responsibilities:** Decide which of `SK-AI-002`–`SK-AI-008` a feature needs and sequence them; own the LLM-call observability plan (structured request/response logging with secret/PII scrubbing, token/cost tracking, latency); flag over-engineering (e.g. reaching for agent-architecture or RAG when a single structured-output call suffices).
- **Inputs:** LLM feature requirement.
- **Outputs:** LLM feature architecture (applicable sub-disciplines + composition) + LLM-call observability plan.
- **Activation conditions:** Starting a new LLM-powered feature; deciding its overall shape before implementation.
- **Non-activation conditions:** No LLM in the feature; the request is already scoped to one specific sub-discipline (route directly to `SK-AI-002`–`SK-AI-008`).
- **Dependencies:** Related `SK-AI-002`–`SK-AI-008` (composes selectively, not unconditionally); related `SK-QA-004` (general observability, specialized here).
- **Conflicts:** None.
- **Related:** `SK-AI-002`–`SK-AI-008`, `SK-QA-004`.
- **Evaluation requirements:** Given a feature requirement, correctly identifies which sub-disciplines apply and declines the ones that don't; LLM-call observability plan never logs unscrubbed secrets/PII in prompts or completions.
- **Tier:** A/B.

### SK-AI-002 · prompt-context-engineering
- **Purpose:** Design system prompts, message structure, and context-window composition for reliable LLM behavior.
- **Scope:** Prompt architecture (system prompts, structural delimiters, few-shot examples, role framing) and context engineering (context-window composition/ordering, long-context placement, budget/rot management, cache-friendly structuring). Grounded in Anthropic's and OpenAI's own prompting guidance, which converge on largely the same structural recommendations despite differing vendor terminology.
- **Responsibilities:** Structure system prompts (role, instructions, examples, context ordering); place long-context content before the query, not after; manage context budget as a conversation grows; structure cache-friendly prefixes (stable content first) where the target provider supports prompt caching; avoid documented anti-patterns (over-aggressive imperative tool-triggering language, deprecated prefill-based patterns).
- **Inputs:** Feature/task the prompt needs to accomplish; target model(s); any existing prompt.
- **Outputs:** System prompt + message-structure design; context-management approach.
- **Activation conditions:** Designing or debugging a prompt; output quality depends on prompt/context structure; long-running conversations need budget/compaction design.
- **Non-activation conditions:** The request is about the output's *shape* (structured output/tool calling — route to `SK-AI-003`) rather than its content/quality.
- **Dependencies:** Related `SK-AI-003` (structured output/tool calling), `SK-AI-005` (RAG's retrieved content is a context-engineering input), `SK-AI-001`.
- **Conflicts:** None.
- **Related:** `SK-AI-001`, `SK-AI-003`, `SK-AI-005`.
- **Evaluation requirements:** On a fixture prompt-quality task, produces a prompt following documented structural best practices and a context-budget/caching plan proportionate to the task's context-window needs.
- **Tier:** A/B.

### SK-AI-003 · structured-output-tool-calling
- **Purpose:** Get reliable, schema-conformant structured output and tool/function calls from an LLM.
- **Scope:** Structured output and tool/function calling, treated as one skill because both researched vendors implement them via the same underlying enforcement mechanism (Anthropic's strict tool use/`output_config.format`; OpenAI's Structured Outputs and strict-mode function tools share "one underlying enforcement engine"). Covers tool-schema design, forcing semantics, parallel tool calls, the tool-call round trip, and each platform's documented JSON Schema support ceiling.
- **Responsibilities:** Design tool/function schemas (clear names, descriptions, parameter docs); choose forcing semantics appropriate to the task; design the tool-call round trip; design JSON-schema-constrained output for non-tool structured responses; work within the target provider's JSON Schema support ceiling; keep the tool count small (~20 is the documented soft ceiling on both platforms) and use dynamic tool loading for larger tool ecosystems.
- **Inputs:** Task requiring structured/schema-conformant output or external tool invocation; target model/provider.
- **Outputs:** Tool/schema definitions + round-trip handling design.
- **Activation conditions:** A feature needs schema-conformant output; a feature needs the LLM to call external tools/functions.
- **Non-activation conditions:** The output is unconstrained free text; the request is about the multi-step orchestration loop around tool calls (route to `SK-AI-004`).
- **Dependencies:** Related `SK-AI-004` (agent architecture builds on tool calling), `SK-AI-002` (context for tool definitions).
- **Conflicts:** None.
- **Related:** `SK-AI-001`, `SK-AI-002`, `SK-AI-004`.
- **Evaluation requirements:** On a fixture task, produces schema-conformant output or a correct tool-call round trip within the target provider's documented JSON Schema ceiling; doesn't over-provision unnecessary tools into a single turn.
- **Tier:** A/B.

### SK-AI-004 · agent-architecture
- **Purpose:** Architect multi-step, tool-using LLM agent loops — the orchestration layer above a single tool call.
- **Scope:** Agent loop design (the while-loop-on-stop-reason pattern both researched vendors document), state-management strategy across turns, multi-agent patterns (handoffs, subagents) where supported, and hand-rolled-loop vs. managed-framework choice per each vendor's own documented criteria. Distinct from `SK-AI-003` (a single tool call's mechanics) and from excessive-agency risk management (owned by `SK-AI-008`).
- **Responsibilities:** Design the agent's tool-execution loop and termination conditions; choose a state-management/conversation-persistence strategy; decide hand-rolled loop vs. managed framework per the task's control-vs-convenience trade-off; design multi-agent composition only where genuinely needed; bound agent autonomy (step/recursion/cost limits), coordinating with `SK-AI-008` on the security implications.
- **Inputs:** Multi-step or tool-using task requiring an LLM agent; target platform.
- **Outputs:** Agent loop/orchestration design + state-management strategy.
- **Activation conditions:** A feature requires an LLM to autonomously sequence multiple tool calls or sub-tasks.
- **Non-activation conditions:** A single tool call or single structured-output response suffices (route to `SK-AI-003`); the concern is really about bounding what the agent is authorized to do (route to `SK-AI-008`).
- **Dependencies:** Related `SK-AI-003` (tool calling), `SK-AI-008` (excessive-agency/blast-radius limits).
- **Conflicts:** None.
- **Related:** `SK-AI-001`, `SK-AI-003`, `SK-AI-008`.
- **Evaluation requirements:** On a fixture multi-step task, designs a bounded agent loop (explicit termination/step limits); correctly declines to add agent orchestration when a single call would do.
- **Tier:** A/B.

### SK-AI-005 · rag-engineering
- **Purpose:** Design retrieval-augmented generation — grounding LLM output in retrieved content via embeddings and vector/semantic search.
- **Scope:** The RAG pattern (retrieval → context injection → generation) and the embedding layer feeding it (model/dimensionality choice, chunking strategy). The vector/semantic *search infrastructure* itself is owned by the already-authored `SK-DATA-005` (search-integration), which already scopes "vector/semantic search"; this skill owns the RAG pattern and two risks the OWASP research documents directly (LLM09, LLM02): retrieval-authorization ordering and embedding-store sensitivity.
- **Responsibilities:** Design the retrieve-then-generate pipeline; choose chunking/embedding strategy; design context injection (per `SK-AI-002`'s placement guidance); enforce authorization *inside* the retrieval query rather than filtering results after retrieval; treat embedding stores/backups as source-document-sensitive, not lower-sensitivity, per documented embedding-inversion risk.
- **Inputs:** Task requiring grounding in a retrievable corpus.
- **Outputs:** RAG pipeline design (retrieval, chunking/embedding choice, context injection) + authorization/sensitivity notes for the retrieval layer.
- **Activation conditions:** A feature needs LLM output grounded in a specific document/data corpus rather than the model's own knowledge.
- **Non-activation conditions:** No retrieval corpus involved; the request is about the search infrastructure itself (route to `SK-DATA-005`).
- **Dependencies:** Related `SK-DATA-005` (vector/semantic search infrastructure), `SK-AI-002` (context injection), `SK-AI-008` (retrieval-authorization/embedding-sensitivity risk).
- **Conflicts:** None.
- **Related:** `SK-AI-001`, `SK-DATA-005`, `SK-AI-002`, `SK-AI-008`.
- **Evaluation requirements:** On a fixture RAG task, designs authorization-at-query-time (not post-filter) retrieval and treats embedding backups as sensitive; correctly delegates pure search-infrastructure concerns to `SK-DATA-005`.
- **Tier:** A/B.

### SK-AI-006 · model-selection
- **Purpose:** Choose the right LLM/provider/model tier for a task's capability, cost, and latency requirements.
- **Scope:** Model/provider/tier selection as a vendor-neutral decision framework, explicitly grounded in more than one vendor's own documented guidance rather than a single-vendor recommendation — per the master plan's "do not assume one model/provider is always best."
- **Responsibilities:** Weigh capability tier vs. cost vs. latency against the task's actual requirements (not reflexively defaulting to the most capable/expensive tier); apply each vendor's own "start with the default tier, escalate for harder cases" guidance as a pattern, not a specific product endorsement; account for context-window and per-request-cost differences across tiers; account for model-snapshot pinning and deprecation-notice practices when choosing a model for production use.
- **Inputs:** Task requirements (capability need, cost/latency budget, context-window need); candidate providers/models.
- **Outputs:** Model/provider/tier selection + rationale.
- **Activation conditions:** Choosing which model/provider/tier a feature should call; evaluating whether a currently-used model is appropriately sized for its task.
- **Non-activation conditions:** The model is already fixed by an external constraint with no real choice to make.
- **Dependencies:** Related `SK-AI-001`.
- **Conflicts:** None.
- **Related:** `SK-AI-001`, `SK-AI-007`.
- **Evaluation requirements:** Given a task's stated capability/cost/latency requirements, selects a tier proportionate to the requirement and states the trade-off explicitly rather than defaulting silently.
- **Tier:** A.

### SK-AI-007 · llm-evaluation
- **Purpose:** Build evaluation harnesses for LLM-powered features and detect/mitigate hallucination.
- **Scope:** LLM-specific evaluation (success-criteria design, grading-method selection, golden datasets, eval-before-ship discipline) and hallucination mitigation (grounding requirements, claim verification). Distinct from `SK-QA-001` (general testing-strategy): LLM output is *graded*, not merely asserted true/false, so this skill owns grading-method selection and hallucination-specific verification; ties back to `SK-QA-001` for surrounding test-suite discipline (fixtures, CI gating).
- **Responsibilities:** Design measurable, specific, achievable success criteria; choose a grading method matched to the task (exact-match for categorical tasks, semantic-similarity/ROUGE for semantic tasks, LLM-as-judge for subjective ones — using a different model to grade than to generate); build/maintain a golden test-case set; design hallucination-mitigation checks (require grounding, verify claims before an agent acts on them); gate prompt/model changes behind eval regression checks before shipping.
- **Inputs:** LLM feature and its stated behavioral requirements.
- **Outputs:** Eval harness design (success criteria, grading method, test cases) + hallucination-mitigation checks.
- **Activation conditions:** Building or reviewing an LLM feature that needs quality verification before shipping; a feature is exhibiting suspected hallucination.
- **Non-activation conditions:** General (non-LLM-output) test authoring — route to `SK-QA-001`.
- **Dependencies:** Related `SK-QA-001` (general testing-strategy/CI discipline).
- **Conflicts:** None.
- **Related:** `SK-AI-001`, `SK-QA-001`.
- **Evaluation requirements:** Given an LLM feature, produces success criteria and a grading method matched to the task type; hallucination-mitigation checks require grounding rather than trusting fluent-but-unverified output.
- **Tier:** A/B.

### SK-AI-008 · ai-security
- **Purpose:** Defend LLM-powered applications against threat classes specific to or meaningfully amplified by LLM use — prompt injection, excessive agency, sensitive-information disclosure via model/embedding channels, and LLM-specific supply-chain risk.
- **Scope:** LLM-specific security, grounded directly in the OWASP GenAI LLM Top 10 (2026). Genuinely distinct from `SK-QA-002` (general security-engineering, which owns traditional AppSec). Prompt injection has no architectural equivalent to a parameterized-query code/data boundary, and the standard itself states "no reliable prevention mechanism exists today" — so this skill frames defense as *bounding blast radius* rather than promising prevention.
- **Responsibilities:** Apply least-privilege architecture (credentials held in application code, not the model; deterministic policy re-validation at execution time); treat untrusted external content (web pages, tool results, RAG passages, emails) as belonging only in clearly-delineated, skepticism-flagged channels, never blended into system-level instructions; require human approval for high-impact/irreversible agent actions; validate/encode LLM output contextually before it reaches a downstream system, per the same parameterized-query discipline OWASP reasserts for LLM-generated queries; treat hidden context (system prompts, tool schemas) as discoverable by default; recommend adaptive (not merely static) red-teaming; flag LLM-specific supply-chain risk (model/adapter provenance, quantization-introduced behavior changes).
- **Inputs:** LLM feature/system and its tool/data access surface.
- **Outputs:** Threat assessment + mitigations mapped to the applicable OWASP LLM Top 10 categories.
- **Activation conditions:** Reviewing or designing an LLM feature with tool access, untrusted-content ingestion, or user-facing exposure; a security review of an LLM-powered system.
- **Non-activation conditions:** A traditional (non-LLM-specific) AppSec concern with no LLM-specific amplification — route to `SK-QA-002`.
- **Dependencies:** Related `SK-QA-002` (general security-engineering), `SK-AI-004` (excessive-agency limits on agent design), `SK-AI-005` (retrieval-authorization/embedding-sensitivity risk).
- **Conflicts:** None.
- **Related:** `SK-AI-001`, `SK-QA-002`, `SK-AI-004`, `SK-AI-005`.
- **Evaluation requirements:** On a fixture LLM feature with a seeded prompt-injection or excessive-agency vector, identifies the risk and proposes blast-radius-bounding mitigation rather than a false claim of complete prevention; correctly declines to answer a traditional non-LLM-specific AppSec question as if it were in scope.
- **Tier:** A/B.

---

# Layer 4 — Technology Specializations

## Shared template

Every technology skill instantiates this template. Fields not in the table below
take these defaults, so they are not repeated per row:

- **ID:** `SK-TECH-<slug>`.
- **Purpose:** Apply *this technology* correctly and version-appropriately, specializing its parent Layer-3 skill(s) with concrete, cited, version-aware detail.
- **Scope:** This technology only. It supplies specifics; the parent generic skill supplies the method.
- **Responsibilities:** Version-correct APIs/config/patterns; the technology's documented anti-patterns, security notes, performance notes, and breaking changes (all traceable to its `research/technologies/<slug>.md` doc and the [version registry](../../research/technologies/VERSION_REGISTRY.md)).
- **Inputs:** The parent skill's output + task context indicating this technology is in play.
- **Outputs:** Concrete, version-correct implementation/config/guidance for this technology.
- **Activation conditions:** This technology is detected in the repo (manifest/config/imports/file types) **or** named in the task.
- **Non-activation conditions:** The technology is absent from the stack and not requested; a sibling alternative is the one actually in use (e.g. don't load `prisma` when the repo uses `drizzle`).
- **Conflicts:** Sibling alternatives should not co-activate for the same decision (pick one ORM, one test runner, one frontend framework) unless the task is explicitly comparative.
- **Related:** Its parent generic skill(s) + siblings + commonly-combined technologies (from the [integration map](../../research/knowledge-maps/integration-map.md)).
- **Evaluation requirements (common):** Output uses the **current** stable version's APIs (per the version registry), avoids that technology's documented anti-patterns, and any version-sensitive claim is correct for the version in the repo. Per-technology evals add specifics (e.g. Postgres: correct index type for a seeded query; Playwright: stable auto-waiting locators, no arbitrary sleeps).
- **Execution tier:** inherited from the parent generic skill (mostly B; frontend/UI verification may be C).
- **Dependencies (common):** its parent Layer-3 skill; abstract agent capabilities per its work (shell for DB/build/test skills; browser for UI-verification skills — resolved by `SK-ORCH-002`).

## Technology skill table

Parent = the Layer-3 skill(s) each specializes. "Notes" flags the most
important per-tech specialization or a merge/version caveat. Every row = one
researched technology doc.

| ID | Technology | Parent skill(s) | Notes |
|---|---|---|---|
| `SK-TECH-react` | React | FE-001, FE-005 | Hooks, RSC/streaming; version-sensitive (RSC, recent CVEs) |
| `SK-TECH-vue` | Vue | FE-001, FE-005 | SFCs, reactivity, XSS-in-template escaping |
| `SK-TECH-angular` | Angular | FE-001, FE-005 | Signals, DI, built-in CSRF; version-sensitive |
| `SK-TECH-nextjs` | Next.js | FE-001, FE-005, GROW-001 | App Router, caching model, SSR/ISR; recent SSRF CVEs |
| `SK-TECH-nuxt` | Nuxt | FE-001, FE-005, GROW-001 | Nitro/edge, universal rendering; GHSAs |
| `SK-TECH-threejs` | Three.js | FE-001 | WebGL/WebGPU, scene graph, GPU resource mgmt; **r-number versioning, no semver** |
| `SK-TECH-tailwindcss` | Tailwind CSS | FE-003 | Utility-first, content-detection tree-shaking; v4 engine changes |
| `SK-TECH-sass` | Sass | FE-003 | `@use`/`@forward` module system; deprecation management |
| `SK-TECH-shadcn-ui` | shadcn/ui | FE-003, FE-002 | Copy-in source model (not a dep); supply-chain pinning; needs Tailwind |
| `SK-TECH-mui` | MUI | FE-003, FE-002 | CSS-in-JS, theming, CSP nonce handling |
| `SK-TECH-web-standards` | Web Standards (HTML & CSS) | FE-003, FE-004 | **Merge of HTML + CSS** (see analysis) — semantic markup, DOM, cascade/specificity, custom properties, Baseline-tracked modern CSS (`@container`, `@property`, native nesting), CSP-relevant sinks |
| `SK-TECH-nodejs` | Node.js | BE-001 | **Added post-hoc (2026-09-10)** — missed from the original 44; researched separately in `research/technologies/nodejs.md`. Event loop/libuv runtime underneath Express/Fastify; annual-LTS cadence change starting v27 |
| `SK-TECH-express` | Express | BE-001, BE-002 | Middleware pipeline; **no official app-testing guidance** (research gap); runs on Node.js (`SK-TECH-nodejs`) |
| `SK-TECH-fastify` | Fastify | BE-001, BE-002 | Schema-driven validation/serialization, plugins, DI; runs on Node.js (`SK-TECH-nodejs`) |
| `SK-TECH-go` | Go | BE-001 | Goroutines, explicit errors, parameterized SQL; std-lib testing |
| `SK-TECH-python` | Python | BE-001, AI-001 | GIL, venvs, exception chaining; broad backend + scripting + AI use |
| `SK-TECH-typescript` | TypeScript | CONV-003 (+ all TS-based) | Type system; **ECMAScript folded in here** (see analysis) |
| `SK-TECH-postgresql` | PostgreSQL | DATA-001, DATA-003, DATA-005 | MVCC/WAL, RLS, FTS; auth deprecations version-sensitive |
| `SK-TECH-mysql` | MySQL | DATA-001, DATA-003 | Pluggable engines; **mid-switch to calendar versioning (26.x)** |
| `SK-TECH-mongodb` | MongoDB | DATA-001, DATA-005 | Document model, aggregation, sharding, field-level encryption |
| `SK-TECH-redis` | Redis | DATA-004, BE-004, DATA-005 | Cache/pub-sub/vector; the multi-role data-layer tech |
| `SK-TECH-clickhouse` | ClickHouse | DATA-003 | Columnar OLAP, sparse indexing, materialized views |
| `SK-TECH-opensearch` | OpenSearch | DATA-005, QA-004 | Full-text + vector search; log analytics (observability tie-in) |
| `SK-TECH-opentelemetry` | OpenTelemetry | QA-004 | **Added post-hoc (2026-09-10)** — closes the observability research gap; researched in `research/technologies/opentelemetry.md`. Vendor-neutral traces/metrics/logs instrumentation standard; multi-repo, per-signal stability, explicitly not a backend/storage/visualization system itself |
| `SK-TECH-prometheus` | Prometheus | QA-004 | **Added post-hoc (2026-09-10)** — pull-based metrics, PromQL, not natively clustered/HA; `promtool test rules` unit testing |
| `SK-TECH-grafana` | Grafana | QA-004 | **Added post-hoc (2026-09-10)** — visualization/dashboarding layer over Prometheus/OpenSearch/other data sources; unified alerting extends Prometheus Alertmanager |
| `SK-TECH-sentry` | Sentry | QA-004 | **Added post-hoc (2026-09-10)** — error monitoring/tracing/session replay; JS SDK runs on OpenTelemetry internally since v8; not a Prometheus-style metrics platform |
| `SK-TECH-drizzle` | Drizzle ORM | DATA-002, DATA-006 | SQL-first TS ORM, edge-ready; **v1 RC vs v0.x stable version caveat** |
| `SK-TECH-prisma` | Prisma | DATA-002, DATA-006 | Schema-driven client, migrations; **v8 docs contradict on a rename** |
| `SK-TECH-typeorm` | TypeORM | DATA-002, DATA-006 | Active-Record + Data-Mapper; N+1 pitfalls |
| `SK-TECH-mongoose` | Mongoose | DATA-002, DATA-006 | Mongo ODM, middleware hooks; NoSQL-injection CVE (time-sensitive) |
| `SK-TECH-openapi-swagger` | OpenAPI + Swagger | BE-002, CONV-006 | **Merged** (spec + its tooling); design-first, codegen, docs |
| `SK-TECH-graphql` | GraphQL | BE-003 | Schema/resolvers, N+1 batching, subscriptions |
| `SK-TECH-socketio` | Socket.IO | BE-004 | Bidirectional events, reconnection, Redis-adapter scaling |
| `SK-TECH-webrtc` | WebRTC | BE-004 | P2P media, NAT traversal, mandatory encryption |
| `SK-TECH-websocket-api` | WebSocket API | BE-004 | Raw browser primitive; **thin — mostly absorbed by BE-004** (see analysis) |
| `SK-TECH-docker` | Docker | INFRA-001, QA-002 | **Unified with containerization**; multi-stage, non-root, scanning |
| `SK-TECH-github-actions` | GitHub Actions | INFRA-002 | **Unified with ci-cd-pipeline**; OIDC, caching, reusable workflows |
| `SK-TECH-husky` | Husky | INFRA-002, CONV-001 | Git hooks: pre-commit lint/test, commit-msg linting |
| `SK-TECH-vite` | Vite | INFRA-001, FE-001 | ESM dev server, HMR, build (Rolldown/Oxc); the build-tool hub |
| `SK-TECH-jest-vitest` | Jest + Vitest | QA-001 | **Merged** (near-identical API, choose-one); unit/mocking/coverage/snapshot |
| `SK-TECH-playwright` | Playwright | QA-001, FE-004 | E2E/browser/visual; **Tier C — browser automation not universal across agents** |
| `SK-TECH-google-seo` | Google SEO | GROW-001 | **Unified with seo-optimization**; crawl/index/serve, Core Web Vitals |
| `SK-TECH-google-adsense` | Google AdSense | GROW-002 | **Unified with web-monetization**; consent, policy compliance |

**Not promoted to standalone technology skills** (see [analysis](taxonomy-analysis.md#unnecessary-or-non-promoted-skills)):
`ECMAScript` (folded into `SK-TECH-typescript` / language practice) and `GitHub`
(the platform — its concerns are covered by `git-workflow`, `ci-cd-pipeline`,
`code-review`, and `project-management`; a standalone skill would mis-trigger and
duplicate).
