---
name: Authentication & authorization
description: >-
  Design authentication and authorization — session vs. token model,
  OAuth2/OIDC flows, safe JWT handling, RBAC and database row-level
  security, and MFA. Use for any authentication or authorization work.
  Avoids the common pitfalls (secrets in tokens, missing expiry, broken
  flows). Not for the general injection/XSS/CSRF/secrets-hygiene risk
  categories, which are owned by security-engineering.
spec_version: "1.0"
---

## Purpose & scope

Design auth as one coherent capability — session vs. token model,
OAuth2/OIDC flows, safe JWT handling, RBAC/row-level security, MFA. This
skill exists to fill a documented gap: this library's concept map found
auth fragmented across separate JWT/OAuth2/MFA/session/RBAC research with
no unifying skill pulling it together. General injection/XSS/CSRF/secrets-
hygiene risk is owned by
[security-engineering](../security-engineering/SKILL.md) — referenced
here, not repeated.

## When to use / When not to use

**Use** for any authentication work (login, session, token issuance/
validation), any authorization work (RBAC, row-level security, permission
checks), designing/integrating an OAuth2/OIDC flow, or reviewing an
existing auth/authz design. **Do not use** when no trust boundary is
involved, or for the general security risk categories with no auth-
specific angle (route to security-engineering).

## Knowledge

**Auth mechanisms vary substantially by layer, and no single technology in
this research documents the end-to-end contract across them.** At the
database/connection layer: PostgreSQL supports `trust`/password/
`scram-sha-256`/GSSAPI/LDAP/RADIUS/cert/PAM, plus (new in v18) **OAuth 2.0
via SASL OAUTHBEARER**; MongoDB supports SCRAM (default)/X.509/LDAP/
Kerberos/OIDC, with RBAC as the authorization model that **must be
explicitly enabled** on self-managed deployments — not on by default
[Source: mongodb.com/docs/manual/security/]. At the application/API layer,
Next.js explicitly recommends external auth providers (Auth0, Clerk,
NextAuth.js/Auth.js, WorkOS, and others) for "increased security and
simplicity" over a hand-rolled scheme [Source: nextjs.org/docs/app/
guides/authentication]. **A synthesis worth internalizing**: a modern
Postgres-backed app's auth story spans at least three loosely-coordinated
layers — the database connection itself (PG18's OAuth), row-level policies
keyed off an ORM-wired claim (see below), and the actual user session
issued by a third-party provider — and no surveyed technology documents
the claim-propagation contract between them. That seam is squarely this
skill's responsibility to design correctly, not something to assume is
handled elsewhere.

**Row-level security (RLS) support differs meaningfully across the ORMs
this library researched.** Drizzle ORM has first-class, schema-level RLS
on PostgreSQL (`pgTable.withRLS()` + `pgPolicy()`, with provider-specific
integrations for Neon and Supabase). Prisma implements RLS via a Client
Extension pattern layered on native Postgres RLS (custom migration,
non-superuser DB role) rather than a first-class schema attribute in
v6/v7 — Prisma 8 is documented as introducing native RLS policies.
TypeORM has **no RLS mention at all** in this library's research
[Source: security-knowledge-map.md §5.2]. For a multi-tenant app relying
on database-enforced row isolation, this is a real, material choice
between ORMs, not an implementation detail to defer.

**Application-level auth has concrete, documented pitfalls worth checking
for by name.** Express: prefer `express-session` (server-side storage)
over `cookie-session` (client-stored — "use only for small data") for
production; change the default `connect.sid` cookie name; set `secure`/
`httpOnly` flags; use `rate-limiter-flexible` to block brute-force login
attempts on consecutive same-username-and-IP failures
[Source: expressjs.com/en/advanced/best-practice-security.html]. Socket.IO
expects auth as connection middleware (`io.use()`) validating
`socket.handshake.auth`/headers/cookies **at connect time and on every
reconnect attempt**, rejecting via `next(new Error(...))`
[Source: socket.io/docs/v4/middlewares/] — a common miss is validating
only the initial connection, not reconnects. GitHub Apps are the
documented least-privilege preference over OAuth Apps: fine-grained,
resource-scoped permissions and short-lived (~1 hour) tokens versus OAuth
Apps' broader `repo`/`public_repo`-style scopes and long-lived user tokens
[Source: docs.github.com — differences-between-github-apps-and-oauth-apps].

**Webhook/API authentication has its own, distinct verification pattern
from session auth.** GitHub's webhook payload authenticity is verified via
HMAC-SHA256 signature in `X-Hub-Signature-256`, recomputed with a
**constant-time comparison** to avoid timing attacks
[Source: docs.github.com/.../validating-webhook-deliveries]. OpenAPI's
Security Scheme Objects support five types (`apiKey`, `http`,
`mutualTLS`, `oauth2`, `openIdConnect`), defined under
`components.securitySchemes` and referenced by name — OpenAPI explicitly
scopes itself to *describing* security requirements, not enforcing them;
deployment-level mechanics (key exchange, certificate management) are
out of spec scope, left to the implementation or a gateway.

## Decision framework

1. **Session or token model?** Server-side sessions are simpler to
   invalidate immediately (log out actually logs out); tokens (JWT) scale
   better statelessly but need an explicit expiry/refresh strategy since
   they can't be revoked the same way — choose based on whether immediate
   revocation matters more than statelessness for this system.
2. **Does the identity need to span a third-party provider (OAuth2/OIDC)?**
   If so, prefer an established provider/library over hand-rolling the
   flow — this library's research shows major frameworks (Next.js)
   explicitly recommending this over a custom implementation.
3. **What RLS/RBAC capability does the chosen ORM actually have?** Drizzle
   (first-class), Prisma (Client-Extension workaround pre-v8), and
   TypeORM (no RLS support documented) are materially different starting
   points — check before designing a row-isolation scheme around an
   assumption the ORM doesn't support.
4. **Is the claim-propagation contract across layers stated explicitly?**
   Connection-layer auth, RLS-layer role claims, and session-layer
   identity can all diverge if the mapping between them isn't designed
   deliberately — no technology in this research documents this
   end-to-end, so it's this skill's job to make explicit.
5. **Does auth validation happen on every reconnect/every request, not
   just the initial handshake?** A common miss (see Socket.IO) is
   validating only the first connection.

## Workflow

1. Determine session vs. token model based on revocation vs. statelessness
   needs.
2. If OAuth2/OIDC is in scope, prefer an established provider/library over
   a hand-rolled flow.
3. Design RBAC/RLS at the layer(s) that actually need it, checking the
   chosen ORM's real RLS capability first.
4. Design token expiry/refresh explicitly; never issue a token that lives
   indefinitely by default.
5. State the claim-propagation contract across connection/RLS/session
   layers explicitly when more than one is in play.
6. Verify auth checks run on every request/reconnect, not just initial
   connection.
7. Hand off general injection/XSS/CSRF/secrets-hygiene concerns to
   security-engineering rather than re-deriving them here.

## Engineering rules

- Tokens have a stated expiry and refresh strategy; never issued to live
  indefinitely.
- No secrets or sensitive data embedded inside a JWT payload.
- Authorization is least-privilege by default, not broad-then-restricted.
- Check the ORM's actual RLS capability (Drizzle/Prisma/TypeORM differ
  materially) before designing a row-isolation scheme.
- Auth/authz checks run on every request or reconnect, not just an initial
  handshake.

## Trade-offs

Server-side sessions are simpler to revoke immediately but require shared
session storage across instances at scale. Tokens (JWT) scale statelessly
but trade away immediate revocation — a compromised token stays valid
until it expires unless a revocation-list mechanism is added on top,
which reintroduces some of the statefulness tokens were meant to avoid.
Hand-rolled OAuth2/OIDC flows offer full control at real implementation-
risk cost; established providers trade some control for correctness the
research shows major frameworks explicitly recommending.

## Anti-patterns

- **Secrets or sensitive data embedded in a JWT payload** — tokens are
  typically only signed, not encrypted; anything sensitive in the payload
  is readable by anyone who intercepts it.
- **Tokens with no expiry, or an unbounded refresh chain** — a real,
  common auth-design mistake this skill explicitly guards against.
- **Validating Socket.IO/realtime auth only at initial connection**, not
  on reconnect — a documented, specific miss.
- **Designing an RLS scheme against an ORM that doesn't support it**
  (TypeORM, per this library's research) without checking first.
- **Broad-then-restricted authorization** instead of least-privilege by
  default.

## Security

Auth-specific security concerns are this skill's own content (see
Knowledge above). General injection/XSS/CSRF/secrets-hygiene risk
categories are owned by
[security-engineering](../security-engineering/SKILL.md) — this skill
defers to it rather than re-deriving those categories.

## Performance

Session-store lookups (for server-side sessions at scale) and token-
validation cost (for high-throughput token verification) are the two
auth-specific performance concerns; deep performance method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

Auth-flow correctness (token expiry actually enforced, RLS actually
restricts cross-tenant access, reconnect auth actually re-validates) is
the auth-specific testing concern; deep test-strategy method is owned by
[testing-strategy](../testing-strategy/SKILL.md).

## Failure handling

- If the auth requirement's threat context isn't clear, ask rather than
  assume a default model.
- If the request is really about general security hygiene with no
  auth-specific angle, route to security-engineering.

## Escalation

- A production auth-flow change (login, session invalidation, token-
  issuance logic) is presented with trade-offs for explicit confirmation,
  given the blast radius of getting it wrong.

## Outputs & verification

- **Outputs:** an auth/authz design (session/token model, flow, RBAC/RLS
  structure) with trade-offs, and implementation guidance.
- **Verify:** tokens have explicit expiry/refresh; no secrets in JWTs;
  authorization is least-privilege; claim-propagation across layers is
  stated explicitly.

## References

- [research/knowledge-maps/security-knowledge-map.md](../../research/knowledge-maps/security-knowledge-map.md)
