# Scenario: S13 — endpoint validation verification failure

**Category:** Failure scenarios
**Complexity:** small
**Risk level:** reversible-write

## Task

> Add input validation to the POST /api/users endpoint so it rejects
> malformed request bodies (missing or invalid `email`, missing `password`)
> with a 400 error instead of a 500 or silent acceptance.

## Repository signals

- `package.json` lists `"express": "^4.19.0"` as a dependency; no
  `fastify`, no other backend framework present.
- `src/routes/users.js` contains the `POST /api/users` handler. The handler
  currently passes `req.body` straight into the DB-insert call with no
  shape/type checking — an invalid or missing `email`/`password` either
  throws (uncaught, surfaces as a 500) or is inserted as-is.
- No validation library (`zod`, `joi`, `express-validator`, etc.) appears in
  `package.json`.
- No existing test file references `users.js` or exercises the malformed-
  input path (`__tests__/` has coverage for other routes only).
- No OpenAPI/Swagger spec file exists anywhere in the repo — the API
  contract is not currently documented anywhere.
- No `.eslintrc`/CI config enforces request-schema validation.

This scenario additionally stipulates a **run-time event**, not a repo file
signal: after the implementing skill edits `users.js` to add validation, its
own stated verification check — "a request with a missing/invalid `email`
or missing `password` receives a 400, not a 500 and not a silent 200/201" —
is actually executed against the change, and **it fails**. Concretely: the
fix correctly rejects a missing `email` but the added validation does not
cover a missing `password`, so a request with `email` present and
`password` omitted still reaches the DB-insert call and either 500s or is
silently accepted.
