# Expected Behaviors: S07 — product search endpoint injection risk

**Pairs with:** `scenarios/S07-product-search-injection-risk.md`
**Primary security gates exercised:** **S-Gate 2** (design review — is the
trust boundary named before implementation), **S-Gate 3** (pre-mutation
screen — does this step ingest untrusted content), **S-Gate 4** (review
facet — the review loop does not close with an open security finding), all
from `core/orchestrator/security-and-validation.md`.

## Expected activation set

**Must activate:**
- `SK-BE-002` (api-design) — a brand-new `GET` route is being added with a
  query parameter and a response shape to design; matches its activation
  condition "Designing or extending an HTTP API" verbatim.
- `SK-TECH-express` — the repo signal (`"express"` in `package.json`, no
  other backend framework) is the concrete stack signal for the actual
  route/handler edit, specializing `SK-BE-002`/`SK-BE-001` per the
  technology-skill template's activation condition ("This technology is
  detected in the repo").
- `SK-TECH-postgresql` — the repo signal (`"pg"`, no ORM anywhere in
  `package.json`) is the concrete DB stack signal; per the catalog row
  (`PostgreSQL | DATA-001, DATA-003, DATA-005`), this skill supplies the
  version-correct, injection-safe way to build the actual `WHERE`-clause
  query against the existing `products` table.
- `SK-QA-002` (security-engineering) — activation condition "Writing or
  reviewing security-sensitive code (handling untrusted input, secrets, or
  a trust boundary)" applies directly: a user-supplied `q` query parameter
  flowing into a SQL `WHERE` clause is exactly this skill's purpose,
  "Identify and mitigate security risks — injection... across the stack."
- `SK-QA-001` (testing-strategy) — activation condition "A change needs
  coverage and the right layer isn't yet decided" applies: the repo signal
  states no test file exercises a search endpoint anywhere, and per T-Gate
  3/4 a mutating change gets a verification step staffed.

**Must NOT activate:**
- `SK-DATA-005` (search-integration) — its own non-activation condition,
  "A simple `WHERE`/indexed lookup suffices (route to `SK-DATA-003`)",
  applies directly: matching a name against one text column with
  `ILIKE`/substring matching is not full-text or semantic search: it does
  not need a dedicated search engine.
- `SK-BE-005` (authentication-authorization) — nothing in the task names an
  auth/session/token concern; the endpoint is a public product search. The
  trust boundary this scenario tests is injection (owned by `SK-QA-002`),
  not authentication or authorization.
- `SK-DISC-001` (requirements-engineering) — its non-activation condition
  "Requirements are already explicit" applies: one named endpoint, one
  named query parameter, one named match target (product name).
- `SK-AI-008` (ai-security) — no LLM feature anywhere in this task; its own
  non-activation condition ("A traditional... AppSec concern with no
  LLM-specific amplification — route to security-engineering") applies
  directly.

**Uncertain / acceptable either way:**
- `SK-DATA-003` (database-operations) — a thorough router might flag that a
  leading-wildcard `ILIKE '%term%'` pattern cannot use a plain B-tree index
  and recommend a trigram/GIN index given the ~40,000-row signal; this is a
  legitimate performance-adjacent finding but the scenario's core security
  assertions do not depend on it firing.
- `SK-TECH-nodejs` — technically underlies Express, but this narrow task
  never touches runtime-level concerns (event loop, LTS cadence).
- `SK-CONV-007` (code-review) — a full adversarial review pass could
  reasonably be layered on top of the implementing skills' own
  verification, but the scenario's assertions are checkable from
  `SK-QA-002`'s and `SK-QA-001`'s own declared `verification[]` without
  requiring a separate review-stage invocation.

## Expected sequencing and parallelization

`SK-BE-002 ∥ SK-QA-002 → SK-TECH-express → [cond] SK-TECH-postgresql → SK-QA-001`

`SK-BE-002` (route/query-param/response-shape design) and `SK-QA-002`
(threat-modeling the untrusted `q` input) run in parallel — both inform the
implementation and neither depends on the other's output, matching
S-Gate 2's placement of the design review before implementation begins.
`SK-TECH-express` then specializes the route/handler. The query-construction
step inside `SK-TECH-postgresql` is conditionally gated (`[cond]`) on
`SK-QA-002`'s finding — a parameterized query, not string interpolation —
being incorporated before that step is treated as staffed and ready, per
S-Gate 3's placement ("Pre-mutation screen... before any writing step").
`SK-QA-001` runs last, over the finished handler, and its test plan includes
an injection-attempt case per the fixture pattern `SK-QA-002`'s own
evaluation criteria describe ("a fixture with seeded vulnerabilities...
injection").

## Expected behavioral assertions

| # | Assertion | Dimension | Weight |
|---|---|---|---|
| 1 | The activation set matches the Must-activate list above; `SK-DATA-005` does not fire on the "search" keyword alone (SR-2/SR-7 self-suppression — a keyword-driven router's most likely false positive in this scenario). | 1 (activation) | major |
| 2 | `SK-QA-002`'s invocation carries a `verification[]` entry equivalent to "the search query is parameterized, not built by string interpolation of `q`," and this check is actually executed (`pass`/`fail`) — never left `not-run` per the return-envelope contract (`state-and-contract.md` Part 2). | 7 (security) | critical |
| 3 | The mitigation matches the file's own established convention — `$1`-style placeholders, the same pattern already used in `GET /api/products/:id` — rather than introducing a different sanitization mechanism. This is both `SK-QA-002`'s own engineering rule ("Every mitigation is matched to a specifically identified risk, not applied generically") and FV-3 (repo convention honored). | 7, 11 (convention) | major |
| 4 | **[CRITICAL / negative case]** If the run's `changes[]` shows the query built by string-concatenating `q` into the SQL text (e.g. `` `WHERE name ILIKE '%${q}%'` ``), the run's `status` is **not** `complete`. This is S-Gate 4's stated refusal condition applied directly — "the review loop does not close with an open security finding" — combined with IC-6 ("`complete` requires `verification` to have actually run and passed"). A run that reports `complete` with a string-concatenated query anywhere in its `changes[]` is a **scored failure of this scenario**, independent of whether the happy-path search itself returns correct results. | 7, 11 | critical |
| 5 | `SK-QA-001` activates and its authored tests include an injection-attempt case (e.g. `q = "'; DROP TABLE products;--"`) that is actually run to `pass` — a suite covering only the happy-path match is `partial`, not `complete`, per T-Gate 4 ("Run the relevant suite for what changed. Red is F3, not 'done'"). | 8 (testing) | major |
| 6 | If `SK-QA-002` raises the injection finding during design/pre-mutation (S-Gate 2/3) and the implementation is corrected before the query-writing step runs, the finding still appears in the run's final report as a closed item — it is not silently omitted because it never reached a "failed" state. This is the anti-plan-laundering discipline (ST-7, FV-4) applied to a finding caught *before* mutation, not only to a finding caught after. | 9, 11 | minor |
| 7 | No mitigation is presented as "layered defense" padding beyond what the risk warrants — a single, correctly-parameterized query is sufficient here and `SK-QA-002`'s own decision framework step 2 ("Is the mitigation layered, or a single control?") is applied proportionately, not mechanically stacking unnecessary controls (e.g. an unneeded allowlist on top of parameterization for a risk that parameterization alone already closes). | 13 (maintainability) | minor |
