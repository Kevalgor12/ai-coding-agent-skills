# Scenario: S06 — user authentication with email verification

**Category:** Multi-skill tasks
**Complexity:** multi-step
**Risk level:** reversible-write

## Task

> Add user authentication with email verification: users sign up with an
> email and password, receive a verification email, and can't log in until
> they've clicked the link.

## Repository signals

- `package.json` lists `"express": "^4.19.0"` and `"pg": "^8.11.0"` as
  dependencies. No ORM (`prisma`, `drizzle`, `typeorm`, `sequelize`) appears
  anywhere in `package.json` or the lockfile — the codebase talks to
  Postgres through the raw `pg` driver.
- `src/` contains only `routes/products.js` and `routes/orders.js` — an
  existing, working Express API for an e-commerce backend. There is **no**
  `users` table, **no** session/auth middleware, and no existing login
  route anywhere in the repo.
- The repo is API-only: no `public/`, no template engine, no frontend
  framework in `package.json`, no `.html`/`.jsx`/`.vue` files. A separate
  frontend service (not in this repository) is the actual consumer of this
  API; the verification link the email contains hits a backend endpoint
  that returns a JSON result, not a server-rendered page.
- `src/lib/mailer.js` already exists and is already used elsewhere in the
  codebase (a password-reset flow was removed in a prior refactor, but the
  mailer wrapper around the transactional-email provider was left in place
  and is still tested by `__tests__/mailer.test.js`). Sending the
  verification email itself is therefore **reusing** existing
  infrastructure, not standing up a new email-provider integration.
- `package.json` lists `"jest": "^29.7.0"` as a dev dependency; `__tests__/`
  already covers `products.js` and `orders.js` with Jest. No `bcrypt`/
  `argon2`/`jsonwebtoken`/`express-session` appears in `package.json` yet —
  none of the password-hashing or session/token machinery exists.
- No `docs/` directory and no OpenAPI/Swagger spec exists for this API.
- No CI config, no Dockerfile — infra/delivery concerns are out of scope for
  this repository as it stands.
