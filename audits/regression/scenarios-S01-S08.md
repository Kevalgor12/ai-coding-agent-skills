# Regression check — S01–S08

**Checked against:** Step 34 changes (rendered 2026-09-11)
**Checked by:** Step 35 regression pass

## Step 34 changes screened in this check

1. **New skill `rendering-strategy` (SK-FE-005)** — activates when CSR/SSR/SSG/ISR/streaming rendering-mode choice is open; does NOT activate for pure client-only SPAs with no SEO/SSR concern, or when mode is already decided.
2. **New skill `graphql` (SK-TECH-graphql)** — activates when `.graphql`/`.gql` files, `graphql` npm package, or Apollo Server present, or when writing/modifying resolvers/schema/subscriptions; does NOT activate when REST-vs-GraphQL paradigm choice is still open.
3. **`code-review` depends_on_skills change** — SK-QA-002 (security-engineering) and SK-QA-003 (performance-engineering) moved from `depends_on_skills` to `related_skills`; they are now conditional delegations, not unconditional hard sub-steps of every review.
4. **`refactoring` depends_on_skills change** — SK-QA-001 (testing-strategy) moved from `depends_on_skills` to `related_skills`.
5. **`legacy-modernization` depends_on_skills change** — SK-QA-001 (testing-strategy) moved from `depends_on_skills` to `related_skills`.
6. **C-2 gate fix** — policy-authorizing requests classify at the gate class they bypass.
7. **mysql trigger change** — non_activation_conditions scoped to "relational" engine; functional meaning unchanged.
8. **VR-3/VR-8 text fixes** — stale "not yet authored" prose removed from ~25 skill files; activation conditions themselves unchanged.

---

## Summary

8/8 pass, 0 regressions found.

---

## S01 — PostgreSQL duplicate-rows query bug

**Relevant Step 34 changes:** None — no rendering-mode decision, no GraphQL signals, no code-review/refactoring/legacy-modernization in scope.

**rendering-strategy false-positive check:** The repo is backend-only (Node.js + Express + `pg`, no SSR/SSG framework). rendering-strategy's non_activation_condition "Backend-only work with no rendered page involved" applies outright. React is detected in `frontend/package.json` but the task is a SQL query fix; even the React SPA is CRA-style with no rendering-mode choice open. No false positive.

**graphql false-positive check:** No `.graphql`/`.gql` files, no `graphql` npm package, no Apollo Server anywhere in the repo. graphql's detection-based activation conditions are not met. No false positive.

**depends_on_skills changes:** code-review (SK-CONV-007) is in Must NOT activate for S01; refactoring (SK-CONV-004) is also in Must NOT activate. Neither change is reachable in this scenario.

**Verdict:** PASS

---

## S02 — Commit message for a staged change

**Relevant Step 34 changes:** None — the request is to write commit text; no rendering-mode decision, no GraphQL signals, no code-review/refactoring in the activation set.

**rendering-strategy false-positive check:** No framework is being scaffolded or configured. The staged change is a one-line bug fix in `src/utils/formatCurrency.js`. No rendering-mode choice is open at any point in this request. No false positive.

**graphql false-positive check:** No GraphQL signals in the repo. No false positive.

**depends_on_skills changes:** None of the affected skills (code-review, refactoring, legacy-modernization) appear in S02's activation set or sequencing.

**Verdict:** PASS

---

## S03 — App feels slow

**Relevant Step 34 changes:** rendering-strategy (SK-FE-005) newly authored; code-review depends_on_skills change (SK-QA-002, SK-QA-003 → related_skills).

**rendering-strategy false-positive check:** The expected behavior (S03) already explicitly lists `rendering-strategy (SK-FE-005)` in Must NOT activate with the reason: "Non-activation condition covers 'pure SPA with no SEO/SSR concern'; this is a Vite/CRA SPA, and no rendering-mode decision is implicated by a slowness complaint in isolation." The current rendering-strategy skill.yaml contains exactly the matching non_activation_condition: "A pure client-only SPA with no SEO/SSR concern and no rendering-mode choice actually open (nothing to decide)." The expected behavior and the authored skill are consistent. No false positive.

**graphql false-positive check:** The repo manifest (`package.json`) lists `react`, `express`, `pg` — no graphql package, no `.graphql` files. No false positive.

**code-review depends_on_skills change:** code-review appears in the expected sequencing as `→ code-review ⤾ (performance facet)`. SK-QA-003 (performance-engineering) is the PRIMARY skill for S03, activated before code-review in the sequence. The change makes SK-QA-003 a conditional delegation from code-review rather than an unconditional sub-step. Since performance-engineering already activates independently as the lead skill, code-review's conditional delegation to it is still expected to fire (a performance concern is explicitly present). The assertion that code-review comes after implementation and delegates performance findings is unchanged.

**Verdict:** PASS

---

## S04 — "Can you clean this up?"

**Relevant Step 34 changes:** legacy-modernization depends_on_skills change (SK-QA-001 → related_skills) is the only possibly-relevant change; legacy-modernization may activate after scope is established, though this is outside the scenario's tested scope.

**rendering-strategy false-positive check:** The request is entirely ambiguous about object and action; no rendering-mode decision is anywhere on the table. rendering-strategy's activation conditions ("Deciding how a page or app should render… in a framework capable of more than one mode") are not met by "Can you clean this up?" No false positive.

**graphql false-positive check:** No GraphQL signals in the described repo (`src/legacy/callbacks.js`, `src/utils/helpers.js`, `scripts/build.sh`). No false positive.

**depends_on_skills changes:** The scenario's core assertion is that requirements-engineering fires first (status: blocked) before any build skill. The legacy-modernization depends_on_skills change affects what happens AFTER scope is established — outside this scenario's graded assertions. The initial routing expectation (requirements-engineering only, no refactoring/code-quality/legacy-modernization in initial plan) is unchanged.

**Verdict:** PASS

---

## S05 — Realtime multiplayer browser game

**Relevant Step 34 changes:** rendering-strategy (SK-FE-005) newly authored; graphql (SK-TECH-graphql) newly authored; code-review depends_on_skills change (SK-QA-002, SK-QA-003 → related_skills).

**rendering-strategy false-positive check:** The expected behavior (S05) places SK-FE-005 in "Conditional / deferred-but-expected once architecture resolves the open choice" — the weakest of the three categories (neither Must activate nor Must NOT activate). The skill notes "SSR/CSR is largely moot for a WebGL canvas, but hydration-adjacent concerns may still surface it." rendering-strategy's non_activation_condition "A pure client-only SPA with no SEO/SSR concern and no rendering-mode choice actually open" maps cleanly to a Three.js game canvas. A router that excludes it is following the non_activation_condition; one that defers it is also acceptable. The new skill does not create a false-positive activation risk that the expected behavior scores as an error.

**graphql false-positive check:** The expected behavior explicitly lists `SK-BE-003 (graphql-api-design), SK-TECH-graphql` in Must NOT activate with reason "no GraphQL signal." The repository is empty/near-empty (no `package.json`, no `.graphql` files). graphql's detection-based activation conditions are unmet. No false positive.

**code-review depends_on_skills change:** The expected sequencing shows `→ SK-CONV-007 ⤾ (delegates SK-QA-002 ∥ SK-QA-003 ∥ SK-CONV-003 ∥ SK-CONV-002 facets, parallel — same diff, no shared state)`. Before Step 34, SK-QA-002 and SK-QA-003 were unconditional hard sub-steps; after, they are conditional delegations. In S05 both skills appear earlier in the sequence as independent primary activations (Must-activate items in their own right). When code-review runs the review loop, both security and performance concerns are clearly present (multiplayer untrusted-client threat model; realtime latency budget), so the conditional delegation fires in both cases. The Must-activate status of SK-QA-002 and SK-QA-003 is grounded in their own activation conditions, not in code-review's depends_on_skills — the change does not remove them from the required activation set.

**Verdict:** PASS

---

## S06 — User authentication with email verification

**Relevant Step 34 changes:** rendering-strategy (SK-FE-005) newly authored; graphql (SK-TECH-graphql) newly authored; code-review depends_on_skills change (SK-QA-002 → related_skills).

**rendering-strategy false-positive check:** The repository is API-only: no `public/`, no template engine, no frontend framework, no `.html`/`.jsx`/`.vue` files. rendering-strategy's non_activation_condition "Backend-only work with no rendered page involved" applies directly. The expected behavior also lists `SK-FE-001..SK-FE-005` in Must NOT activate. No false positive.

**graphql false-positive check:** The expected behavior lists `SK-BE-003 (graphql-api-design), SK-TECH-graphql` in Must NOT activate ("the existing API is REST (Express routes); no GraphQL signal."). `package.json` contains only `express` and `pg` — no graphql package. No false positive.

**code-review depends_on_skills change:** S06 requires code-review (SK-CONV-007) as a Must-activate skill with the reason that the security facet is "mandatory per the trust-boundary review-edge rule." Under the new related_skills model, code-review conditionally delegates to SK-QA-002 when a security concern is present. In S06, auth code with secrets handling is the entire task — the security concern is unambiguous — so the conditional delegation fires. Critically, S06's expected behavior already notes that SK-QA-002 activates independently ("grounded in SK-QA-002's own independent activation-condition match… It is not a hard depends_on_skills composition edge"). Assertion 1 explicitly states the inclusion is "traceable to a declared condition" of SK-QA-002 itself, not to code-review's depends_on_skills. The change is consistent with how S06's expected behavior already frames the relationship. The mandatory security facet of code-review still fires because the security condition is present.

**Verdict:** PASS

---

## S07 — Product search endpoint injection risk

**Relevant Step 34 changes:** None that materially affect this scenario. rendering-strategy and graphql are new, but neither has signals in this repo.

**rendering-strategy false-positive check:** The repository is an Express + PostgreSQL backend API with no frontend framework and no rendering-mode decision. rendering-strategy's non_activation_condition "Backend-only work with no rendered page involved" applies. No false positive.

**graphql false-positive check:** `package.json` lists only `express` and `pg`; no `graphql` package, no `.graphql` files. No false positive.

**depends_on_skills changes:** code-review is "Uncertain / acceptable either way" for S07 — not a required activation. The depends_on_skills change to code-review doesn't affect any scored assertion for this scenario. refactoring and legacy-modernization are not in scope.

**Verdict:** PASS

---

## S08 — Support-triage agent with refund tool access

**Relevant Step 34 changes:** None that materially affect this scenario. rendering-strategy and graphql are new, but neither has signals in this repo.

**rendering-strategy false-positive check:** The repository is a Node.js/Express backend with an AI agent feature. No frontend framework, no rendering-mode decision. rendering-strategy would not activate. No false positive.

**graphql false-positive check:** `package.json` lists `@anthropic-ai/sdk` and `express` — no graphql package, no `.graphql` files, no Apollo Server. No false positive.

**depends_on_skills changes:** code-review, refactoring, and legacy-modernization are not in the Must-activate set for S08. The depends_on_skills changes to these skills do not affect S08's activation or sequencing expectations. C-2 gate fix: no policy-authorization request in scope here. No impact.

**Verdict:** PASS
