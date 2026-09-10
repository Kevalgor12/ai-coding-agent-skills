# Expected Behaviors: S06 — user authentication with email verification

**Pairs with:** `scenarios/S06-user-auth-email-verification.md`
**Core test:** whether `security-engineering` (`SK-QA-002`) correctly
co-activates alongside `authentication-authorization` (`SK-BE-005`) — the
mirror image of S13, where a superficially similar-sounding keyword
("input validation") correctly did **not** pull `SK-QA-002` in. Here it
should — grounded in `SK-QA-002`'s own independent activation-condition
match, not a hard composition edge (see assertion 2's correction note).

## Expected activation set

**Must activate:**

- `SK-BE-005` (authentication-authorization) — "any authentication or
  authorization work" matches directly; this is the task's core: session/
  token model, password hashing, and the email-verification gate on login
  are all named in its own responsibilities ("choose session vs. token
  model... avoid the common auth pitfalls").
- `SK-QA-002` (security-engineering) — grounded in `SK-QA-002`'s own
  activation condition, which matches this task verbatim: "Security-sensitive
  code... handling untrusted input, **auth**, or secrets" names auth
  explicitly, unlike S13's request, where the closest-sounding condition
  ("handling untrusted input") did *not* cover generic request-shape
  validation. This is the deliberate contrast with S13: same-shaped
  question, opposite correct answer, because the actual scope differs.
  **Correction from an earlier draft of this file:** `core/taxonomy/skill-catalog.md`'s
  `SK-BE-005` entry lists `SK-QA-002` under a "Dependencies:" line
  ("Dependencies: `SK-QA-002` (security)"), which reads like a hard
  `depends_on_skills` composition edge. It is not one — `skills/authentication-authorization/skill.yaml`'s
  actual `depends_on_skills` field is `[]`; `SK-QA-002` is declared only in
  `related_skills`. This is an instance of the catalog's "Dependencies:"
  field conflating relationship types, already flagged as a repo-wide
  finding in `audits/cross-skill/cross-skill-audit.md` (finding X-… on the
  catalog's drift from the authored skills) — do not treat this scenario's
  must-activate conclusion as resting on a real composition edge. It rests
  on reason (b) alone, which is sufficient on its own.
- `SK-BE-002` (api-design) — the task adds four new HTTP endpoints
  (register, verify-email, login, resend-verification) to an existing REST
  API; "designing or extending an HTTP API" matches directly. Consistent
  with S13's precedent (new/changed endpoint surface → `SK-BE-002`), not
  subsumed by `SK-BE-005` — status/error-shape/route design is `SK-BE-002`'s
  own declared responsibility, not `SK-BE-005`'s.
- `SK-TECH-express` — `"express"` in `package.json`, no other backend
  framework; specializes `SK-BE-002` (and `SK-BE-001` if it is separately
  staffed — see excluded list) for the concrete route/middleware
  implementation.
- `SK-DATA-001` (data-modeling) — a `users` table and an
  `email_verification_tokens` table (or equivalent) do not exist yet and
  must be designed: keys, the token/expiry/used-at shape, the FK to `users`.
  Matches "designing or changing a data model" directly.
- `SK-TECH-postgresql` — `"pg"` in `package.json`, no ORM present;
  specializes `SK-DATA-001` for the concrete schema/migration.
- `SK-QA-001` (testing-strategy) — "writing tests / coverage needed";
  explicit in the task category description, and this is security-sensitive
  code with currently zero coverage for the new paths.
- `SK-TECH-jest-vitest` — `"jest"` already a dev dependency and already the
  repo's test runner (`__tests__/` exists); specializes `SK-QA-001`.
- `SK-CONV-006` (technical-documentation) — "a public interface changed";
  four new endpoints are added to an API that has no existing docs/OpenAPI
  spec, matching the activation condition directly.
- `SK-CONV-007` (code-review) — pre-merge gate on a change touching a trust
  boundary; per `dependency-graph.md`'s review-edge table, the security
  facet (owned by `SK-QA-002`, already activated above) is **mandatory**
  here, not optional, because the diff touches auth/secrets.

**Must NOT activate:**

- `SK-BE-001` (backend-architecture) — its own non-activation condition
  doesn't name this case directly, but the feature-development workflow
  (`dependency-architecture/workflows.md` #2) explicitly "skips greenfield's
  architecture step unless the feature introduces a new architectural
  concern"; adding an auth module composes into the existing layered
  Express service without restructuring it. Acceptable if a router
  activates it briefly to decide *where* the auth module sits, but not
  required — see Uncertain.
- `SK-DISC-002` (solution-architecture) — its own non-activation condition
  is a verbatim match: "Architecture is fixed and the task is
  implementation within it." The backend framework, database, and overall
  service shape are already established by the existing repo; nothing here
  is an open architectural choice.
- `SK-BE-004` (realtime-communication) — no realtime/bidirectional/
  streaming signal anywhere in the task.
- `SK-BE-003` (graphql-api-design), `SK-TECH-graphql` — the existing API is
  REST (Express routes); no GraphQL signal.
- All of `SK-FE-001`..`SK-FE-005` and any frontend-framework/styling
  technology skill — the repo signal is explicit: API-only backend, no
  frontend code, no template engine; the verification link is consumed by a
  separate out-of-repo frontend.
- `SK-DATA-002` (orm-integration) and `SK-TECH-drizzle`/`prisma`/`typeorm`/
  `mongoose` — no ORM in `package.json` or the lockfile; the codebase uses
  the raw `pg` driver (explicit repo signal, same discipline as S13's
  validation-library check).
- `SK-TECH-mysql`, `SK-TECH-mongodb`, `SK-TECH-redis`, `SK-TECH-clickhouse`
  — Postgres is the only detected engine; nothing indicates a second
  datastore role (e.g. Redis for session storage) is actually in play.
- `SK-GROW-001`/`SK-GROW-002` and their technology skills — no public-web
  SEO or monetization signal.
- `SK-AI-001`..`SK-AI-008` — no LLM feature.
- `SK-INFRA-001`/`SK-INFRA-002`/`SK-INFRA-003` — explicit repo signal: no CI
  config, no Dockerfile; infra/delivery is out of scope for this task.
- `SK-CONV-005` (legacy-modernization), `SK-CONV-004` (refactoring),
  `SK-DATA-006` (data-migration) — the new tables are purely additive
  (`CREATE TABLE`, no existing data reshaped or dropped); this is not a
  destructive/breaking schema change, so `SK-DATA-006`'s destructive-
  migration machinery and human-approval gate do not apply here. (Contrast
  with `examples.md` Example 4, where an *existing populated table* gets a
  breaking schema change — genuinely different risk profile from adding new,
  empty tables.)
- `SK-DATA-005` (search-integration) — no search requirement.
- An **"email delivery" or "notifications" technology skill** — no such
  skill exists anywhere in the catalog (checked against the full technology
  table). The repo signal deliberately states `src/lib/mailer.js` already
  exists and is reused, not built new, precisely so a router is not tempted
  to invent a skill ID for "send the verification email" that the catalog
  does not define. A run that fabricates a skill ID here (e.g.
  `SK-TECH-sendgrid`, `SK-INFRA-email`) is a scored fabrication defect,
  independent of whether the underlying advice is reasonable.

**Uncertain / acceptable either way:**

- `SK-DISC-001` (requirements-engineering) — the task states the core flow
  explicitly (signup → verification email → gated login) but leaves several
  security-relevant parameters unstated (token TTL, resend cooldown/rate
  limit, password complexity policy). `SK-DISC-001`'s own activation
  condition ("under-specified **or** high-stakes") could reasonably fire on
  the high-stakes clause alone; equally, a router could reasonably treat
  `SK-BE-005`'s own declared responsibility (it *decides* session/token
  model and hygiene as part of its normal work) as sufficient without a
  separate discovery stage. Acceptable either way; not required for the
  minimum set.
- `SK-BE-001` (backend-architecture) — see reasoning under Must NOT
  activate; a router that briefly re-invokes it to place the new auth
  module within the existing layering is not wrong, just not required.
- `SK-DATA-003` (database-operations) — indexing the token-lookup column
  (e.g. a unique index on the token hash) is a defensible addition at this
  scale; also defensible to treat as part of `SK-DATA-001`'s schema design
  rather than a separate operational pass, given the low expected data
  volume.
- `SK-TECH-nodejs` — underlies Express; a router naming it is not wrong,
  but this task never touches runtime-level concerns (event loop, LTS
  cadence), so it is not required.

## Expected sequencing and parallelization

```
SK-DATA-001 → SK-TECH-postgresql
  → SK-BE-002
  → SK-BE-005  ⇐  SK-QA-002        (prerequisite: SK-QA-002 needs SK-BE-005's concrete design as input — NOT composition; see correction note)
  → SK-TECH-express                 (concrete route/middleware implementation over the now-fixed schema + contract + auth design)
  → [ SK-QA-001 ∥ SK-CONV-006 ]     (test-writing and API-doc-writing — disjoint targets, both read-only against the finished implementation)
  → SK-CONV-007 ⤾ (security facet mandatory, per the trust-boundary review-edge rule)
  → [ SK-CONV-001 + SK-CONV-008 → PR ]   ⛔ (outward-facing, only if a commit/PR is actually posted)
```

- **Sequential, not parallel — the scenario's specific test:** database
  schema work (`SK-DATA-001` → `SK-TECH-postgresql`) precedes the backend
  auth-flow implementation (`SK-BE-002` → `SK-BE-005` → `SK-TECH-express`),
  because the auth-flow design needs to reference a concrete record shape
  (what a "verification token" row actually contains: token hash, expiry,
  `user_id` FK, `used_at`) before it can be designed, not merely
  implemented. A plan that runs these two `∥` is a scored parallelization
  error: it is a data dependency (the auth design *reads* the schema
  decision), not a merely-convenient ordering — this is exactly the trap
  the parallelization matrix names ("a prerequisite edge connects them →
  serialize").
- **Parallel — the scenario's other specific test:** writing tests
  (`SK-QA-001`) and writing API documentation (`SK-CONV-006`) for the four
  new endpoints. Both consume the same finished implementation as read-only
  input and write to disjoint targets (`__tests__/auth.test.js` vs. a docs
  file) — the parallelization matrix's "fan-out... disjoint targets" case.
  A plan that serializes these two with no stated reason is a scored
  unexplained-parallelization-loss, the same defect class as S05's
  assertion 3, at smaller scale.
- **Prerequisite, not composition — corrected from an earlier draft:**
  `SK-BE-005 ⇐ SK-QA-002` is sequential because `SK-QA-002`'s threat-model
  needs `SK-BE-005`'s concrete design (which hashing algorithm, what the
  token looks like, what "expired" means) to evaluate against. This is a
  **prerequisite edge** (`core/dependency-architecture/README.md`: "B's
  output must exist before A can meaningfully run") — `SK-QA-002` is the
  dependent (needs `SK-BE-005`'s output as input), not a sub-step
  `SK-BE-005` invokes. Earlier text in this file called this "composition,"
  citing `skill-catalog.md`'s "Dependencies:" line — that line is
  imprecise (see the correction note under "Expected activation set");
  `skills/authentication-authorization/skill.yaml`'s actual
  `depends_on_skills` field is `[]`. The practical consequence: `SK-QA-002`
  gets its **own** `routing_record`/ledger entry (it is independently
  activated, per its own activation condition, and merely ordered after
  `SK-BE-005`) — it is not folded into `SK-BE-005`'s invocation as an
  internal activity. A run that never surfaces `SK-QA-002` as its own
  step (e.g. only mentions security in passing inside the auth
  implementation's own output) is scored as under-attributing the security
  review, not as correctly "composing" it.
- **No destructive-migration gate:** unlike `examples.md` Example 4 (RLS on
  a populated table), the new tables here are additive-only. `SK-DATA-006`
  does not activate and no `⛔` fires on the migration step itself — only
  the PR post is gated. A run that gates the (non-destructive) migration
  with `⛔` is over-gating; a run that fails to gate the PR post is
  under-gating. Both are scored errors.

## Expected behavioral assertions

| # | Assertion | Dimension | Weight |
|---|---|---|---|
| 1 | `SK-QA-002` appears in `routing_record.selected[]` whenever `SK-BE-005` does, as its own entry (not folded into `SK-BE-005`'s activity), and the recorded reason cites its own activation condition ("auth" named explicitly) — never omitted, and never justified only by a generic "security is always relevant" boilerplate. | 1 (activation), 3 (sequencing) | critical |
| 2 | The run does **not** independently re-derive `SK-QA-002`'s inclusion the way a naive keyword router would ("auth" sounds security-adjacent) without being able to point to `SK-QA-002`'s own actual activation-condition text — i.e. the inclusion is traceable to a declared condition, not a vibe. Contrast with S13, where the superficially similar reasoning ("validation sounds security-adjacent") was the wrong call; a run that cannot articulate *why* this case differs from S13's is scored as reasoning by pattern-match rather than by scope. (Note: do not accept "the catalog lists it as a Dependency" as the cited reason — that catalog line is a known imprecision, not a real `depends_on_skills` edge; see the correction notes above.) | 1, 2 | major |
| 3 | `routing_record.selected[]` does not include `SK-DATA-002` (orm-integration) or any ORM technology skill — grounded in the explicit repo signal that no ORM is present. A run that adds one "because auth usually goes through an ORM" despite the repo signal is a scored SR-3/SR-4 detection-override error. | 1 | major |
| 4 | The plan sequences `SK-DATA-001`/`SK-TECH-postgresql` before `SK-BE-005`'s design step, and does **not** mark them `∥`. A plan that parallelizes schema design and auth-flow design is scored against the parallelization matrix's "prerequisite edge → serialize" rule. | 3 (sequencing), 4 (parallelization) | major |
| 5 | The plan marks `SK-QA-001` (test-writing) and `SK-CONV-006` (doc-writing) as `∥` once implementation is complete, or — if serialized — the plan records a specific reason (e.g. host lacks sub-agent concurrency) rather than leaving the ordering unexplained. | 4 (parallelization) | major |
| 6 | `SK-BE-005`'s output records an explicit, stated decision for at least: password-hashing scheme, verification-token expiry window, and session-vs-token model — each as a recorded decision with rationale, not a silently-assumed default. An implementation that hard-codes e.g. an unbounded-lifetime verification token with no stated expiry decision is a scored implementation-decision failure (`SK-BE-005`'s own responsibility: "avoid the common auth pitfalls... missing expiry"). | 6 (implementation decisions) | major |
| 7 | `SK-QA-002`'s findings/verification for this task specifically address at least: verification-token unguessability/entropy, protection against verification-token enumeration or brute-forcing, and rate-limiting of the resend-verification-email path — not a generic OWASP checklist copy-paste unconnected to this specific flow. | 7 (security) | critical |
| 8 | `SK-QA-001`'s test plan/tests cover, at minimum: successful verification unblocks login, an expired token is rejected, an already-used token is rejected on reuse, and login is refused for a registered-but-unverified user — not only the happy-path signup test. A test suite covering only the happy path is a scored testing-behavior failure. | 8 (testing) | major |
| 9 | No skill ID outside the actual catalog (e.g. an invented "email-technology" or "notifications" skill) appears anywhere in `routing_record.selected[]` or the ledger; the mailer integration is handled as ordinary implementation work within `SK-BE-005`'s scope, reusing `src/lib/mailer.js` per the repo signal, not as a fabricated skill activation. | 1, 5 (context usage) | major |
| 10 | The migration/schema-creation step itself is **not** gated behind `⛔`, but a PR post (if the run reaches that stage) is. A run that gates the additive migration is scored as over-gating; a run that never gates the PR post is scored as under-gating (escalation matrix: outward-facing posts require confirmation; non-destructive additive schema changes do not). | 10 (escalation) | major |
| 11 | `SK-CONV-006`'s produced documentation describes the four new endpoints' actual request/response shape and status codes as implemented (matching `SK-BE-002`'s designed contract), not a restatement of the route handler's code or a generic "add auth" paragraph — checkable as "could a consumer of this API integrate against the docs alone." | 15 (documentation quality) | minor |
