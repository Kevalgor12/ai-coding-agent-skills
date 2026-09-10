---
name: Security engineering
description: >-
  Threat-model a change and apply mitigations for injection, XSS, CORS/
  CSRF, SSRF, secrets hygiene, transport security, sandboxing/isolation,
  supply-chain/dependency risk, DoS, and information disclosure. Use for
  security-sensitive code, a security review, or when handling untrusted
  input or secrets. Treats CVE/version-specific claims as time-sensitive
  and re-verifiable rather than permanently settled. Auth/authz depth is
  owned by authentication-authorization.
spec_version: "1.0"
---

## Purpose & scope

The cross-cutting security skill for this library — technology skills
reference it rather than re-documenting security. Covers injection, XSS,
CORS/CSRF, SSRF, secrets/credential handling, transport security,
sandboxing/isolation, supply-chain/dependency risk, denial of service, and
error-handling/information disclosure. Authentication/authorization depth
(sessions, tokens, OAuth2/OIDC, RBAC/RLS, MFA) is owned by
[authentication-authorization](../authentication-authorization/SKILL.md);
this skill still applies its general risk categories to auth-adjacent code
but defers auth-specific design to that skill.

## When to use / When not to use

**Use** for security-sensitive code (untrusted input, secrets, a trust
boundary), an explicit security review, a dependency/supply-chain check,
or a change touching a documented CVE-affected version range. **Do not
use** when no trust boundary or sensitive data is involved; route
authentication/authorization *design* questions to
authentication-authorization for depth.

## Knowledge

**Secrets never belong in client bundles, plaintext CI config, or logs —
and "convenient" env-var naming can silently create a leak.** Vite exposes
only `VITE_`-prefixed vars to client code; a registry token or API key
named with that prefix ends up shipped to every visitor
[Source: vite.dev/guide/env-and-mode]. CI log redaction is documented as
**best-effort, not guaranteed** — structured secrets (JSON/XML blobs)
don't mask reliably since redaction does exact-string matching; each
derived sensitive value needs its own registered secret
[Source: docs.github.com — security-hardening-for-github-actions].

**Injection defenses converge on the same structural blind spot across
every mainstream ORM.** Parameterized queries/tagged templates (Prisma,
Drizzle, TypeORM as of v1.0, Go's `database/sql`) protect *values*
substituted into a query, but none of them protect an app that lets
untrusted input choose a table/column *name*, a `$nor`/`$where`-style
operator key (see Mongoose's CVE-2026-42334 in the watch list — a
protection gap specifically around `$nor`), or a raw SQL fragment
(`$queryRawUnsafe`, `sql.raw()`) [Synthesis, security-knowledge-map.md
§2.1]. An application-level allowlist for identifiers is required
regardless of which ORM is chosen — parameterization alone does not cover
this surface.

**XSS defense is layered by design, and every frontend framework in this
research pushes at least one layer of it back onto the server/HTTP-header
level.** React's `dangerouslySetInnerHTML`, Vue's `v-html`, and raw HTML
`innerHTML` are each documented as the primary bypass of otherwise-default
auto-escaping. The documented layered-defense order: output encoding via
templating → quote interpolated attributes → sanitize untrusted HTML
(DOMPurify) → enforce Trusted Types via CSP → deploy a strict CSP as
defense-in-depth [Source: developer.mozilla.org/.../Attacks/XSS]. Vue's
docs specifically require URL sanitization **server-side**, not just
client-side, before persistence — a client-only check is documented as
insufficient [Source: vuejs.org/guide/best-practices/security.html].
**No framework in this dataset treats client-side sanitization alone as
sufficient** — a security review of any frontend is incomplete if it only
inspects client bundle code.

**CORS/Origin checks are a browser-only, partial-transport control —
never a complete access-control mechanism on their own.** WebSocket's
`Origin`-header validation defends only browser-originated attacks (non-
browser clients can forge `Origin`); Socket.IO's CORS configuration only
covers its HTTP long-polling transport, not the WebSocket transport
itself — which is exactly why its own docs recommend `allowRequest` as a
required supplement [Synthesis, security-knowledge-map.md §4]. Any server
accepting non-browser clients gets **no** CORS/Origin protection at all
and needs its own connection-level authentication regardless of CORS
configuration.

**"TLS is on" is not one binary state — encryption guarantees differ
meaningfully by protocol.** WebRTC treats encryption as architecturally
non-optional (DTLS-SRTP mandatory, no plaintext mode exists). WebSocket
treats frame-masking as an *additional*, TLS-independent wire-level
control — RFC 6455 mandates client-to-server masking even over `wss`,
since masking guards against cache/proxy poisoning, not confidentiality.
ClickHouse's MySQL-compatibility layer shows wrapping a protocol in TLS
doesn't guarantee full interoperability (SNI routing can still break)
[Synthesis, security-knowledge-map.md §6]. A review that only checks
"is TLS enabled" misses meaningfully different residual risks per
protocol.

**Sandboxing/isolation stacks independently at multiple layers, and
missing one doesn't get compensated by another.** Docker's daemon runs
root by default; Chromium's sandbox is separately disabled specifically
when the *container's own process* runs as root — Docker rootless mode
and a non-root Chromium user address two different layers of the same
"don't run as root" principle, and neither substitutes for the other
[Synthesis, security-knowledge-map.md §7]. Vitest's API server defaults to
localhost-only and auto-disables `allowWrite`/`allowExec` if the host is
changed, since `allowWrite` "gives anyone who can connect to the API the
ability to run any arbitrary code on your machine."

**Supply-chain blast radius is determined by a technology's *distribution
model*, not just whether it has a security policy.** A normal versioned
npm dependency (Fastify, TypeORM, MUI) gets one upstream security policy
and one `npm update` fix. A copy-paste distribution model (shadcn/ui) gets
neither — each consuming project silently forks the code the moment it's
copied, so there's no single point to patch; a vulnerability in previously
copied component code must be manually re-pulled per project. A git-hook
tool (Husky) that dispatches to whatever is on `node_modules/.bin`
inherits the transitive trust of the entire devDependency tree, with no
surveyed technology's security policy claiming ownership of that risk
[Synthesis, security-knowledge-map.md §8].

**Error handling's "leak internal detail" failure mode compounds across
independently-configured layers of the same stack.** Express, Prisma, and
Fastify's default error handler each independently gate on
`NODE_ENV`/production status for how much detail leaks in an error
response. A single missing `NODE_ENV=production` therefore compounds
across all three simultaneously — Express dumps stack traces, Prisma dumps
schema/query internals, and (absent a custom Fastify handler) raw DB
driver errors reach the client [Synthesis, security-knowledge-map.md §11].

**A substantial set of CVE/version-bound findings exist in this
library's research and are explicitly time-sensitive** — see
[references/vulnerability-watch-list.md](references/vulnerability-watch-list.md)
for the full dated table (React RSC RCE/DoS, Next.js's May/August 2026
releases, Mongoose's `$nor` sanitization gap, Nuxt's four v4.5 advisories,
and more) plus vulnerability-disclosure policies by technology. **Never
present an entry from that table as permanently current** — it describes
the state as of early-mid September 2026 research, and patched versions
ship continuously.

## Decision framework

1. **What's actually untrusted here** — external user input, a
   third-party dependency, another service's response? Threat-model from
   that boundary, not from an assumed worst/best case.
2. **Is the mitigation layered, or a single control?** For XSS/injection-
   class risks, prefer encode → sanitize → CSP/allowlist over any single
   layer — every framework surveyed here relies on more than one.
3. **Does this touch a documented CVE-affected version range?** Check the
   watch list, but treat any match as needing live re-verification, not
   as settled by this library's research snapshot.
4. **Does the mitigation's distribution model matter?** A copied-code
   dependency (shadcn/ui-style) has no automatic patch path — flag that
   explicitly rather than assuming "update the package" applies.
5. **Is `NODE_ENV`/environment-gating actually set correctly in
   deployment?** A single missing production flag compounds leak risk
   across multiple stack layers simultaneously — verify it, don't assume.
6. **Is this actually an authentication/authorization design question?**
   If so, hand off the design depth to
   [authentication-authorization](../authentication-authorization/SKILL.md)
   while still applying this skill's general categories where relevant.

## Workflow

1. Identify the trust boundary and what's actually untrusted.
2. Check the relevant risk category/categories (injection, XSS, CORS/
   CSRF, SSRF, secrets, transport, sandboxing, supply-chain, DoS,
   disclosure) against this skill's Knowledge and the full knowledge map.
3. Check the vulnerability watch list for any version-range match; flag
   for live re-verification if found, don't assert it as settled.
4. Apply layered mitigations matched to the specific risk.
5. Verify `NODE_ENV`/environment-gating is correctly configured wherever
   error-detail leakage is a risk.
6. Hand off auth-specific design depth to authentication-authorization.

## Engineering rules

- Every mitigation is matched to a specifically identified risk — never
  applied generically "just in case" without a stated reason.
- Any CVE/version-specific claim is flagged as time-sensitive, never
  presented as permanently settled.
- Prefer layered defense over a single control, especially for XSS/
  injection-class risks.
- Verify environment-gating (`NODE_ENV=production` or equivalent) rather
  than assuming it's correctly set.
- Secrets are never logged, committed, or exposed to a client bundle.

## Trade-offs

Layered defense costs more implementation effort than a single control but
closes the gap left by any one layer failing — worth the cost for
injection/XSS-class risks given how consistently this research shows
single-layer defenses being documented as insufficient by the frameworks'
own docs. Disabling GraphQL introspection reduces attack surface but
breaks developer tooling that depends on it — the documented middle ground
is selective/allowlisted disabling, not blanket.

## Anti-patterns

- **Relying on a single defense layer** (client-side sanitization alone,
  CORS alone, parameterized queries alone) where the research shows every
  framework pushing at least one additional layer server-side.
- **Presenting a CVE watch-list entry as permanently fixed** without a
  re-verification caveat — patched versions ship continuously.
- **Assuming a copied-code dependency (shadcn/ui-style) has an automatic
  upgrade path** the way a normal npm dependency does.
- **Leaving `NODE_ENV` unset or misconfigured** in production, silently
  compounding error-detail leakage across multiple stack layers at once.
- **Naming a secret with a client-exposed env-var prefix** (e.g. `VITE_`)
  out of convenience.

## Security

This skill's entire content is Security. See Knowledge above for the
organized categories; see
[references/vulnerability-watch-list.md](references/vulnerability-watch-list.md)
for the dated CVE table and per-technology disclosure policies. Auth-
specific depth is owned by
[authentication-authorization](../authentication-authorization/SKILL.md).

## Performance

DoS/resource-exhaustion mitigation (rate limiting, query-complexity
analysis for GraphQL, message-size caps) sits at the intersection of
security and performance — covered here as a security concern; broader
performance method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).

## Testing

Security fixtures (seeded vulnerabilities: injection, XSS, exposed
secrets) are the standard verification pattern for this skill per its own
evaluation criteria. Deep test-strategy method is owned by
[testing-strategy](../testing-strategy/SKILL.md).

## Failure handling

- If the threat context isn't clear, ask rather than assume a posture.
- If a CVE/version-specific claim is being relied on for a live decision,
  state it must be re-verified against current advisories.
- If the request is specifically auth design, route that depth to
  authentication-authorization while still applying this skill's general
  categories.

## Escalation

- An actively-exploitable, currently-unpatched vulnerability in
  production is escalated immediately, not queued as a routine finding.
- A CVE-bound claim older than this skill's research snapshot (dated
  2026-09) is flagged for independent re-verification before being acted
  on for a live decision.

## Outputs & verification

- **Outputs:** security findings per risk category with severity/
  rationale, and concrete mitigations matched to each.
- **Verify:** mitigations are layered, not single-control; CVE claims
  carry a re-verification caveat; secrets never leak to logs/bundles/
  commits.

## References

- [references/vulnerability-watch-list.md](references/vulnerability-watch-list.md) — Tier-2 dated CVE table and disclosure policies.
- [research/knowledge-maps/security-knowledge-map.md](../../research/knowledge-maps/security-knowledge-map.md)
