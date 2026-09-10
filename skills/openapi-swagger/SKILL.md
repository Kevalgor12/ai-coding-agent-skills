---
name: OpenAPI & Swagger
description: >-
  Author OpenAPI documents (paths/components/securitySchemes) and configure
  Swagger's UI/Editor/Codegen tooling that consumes them — design-first vs.
  code-first authoring, mock-server/SDK/server-stub generation, and safe
  Swagger UI deployment (OAuth config, the documented CVE, EOL policy). Use
  when writing/reviewing an OpenAPI spec or setting up Swagger tooling. Not
  for the REST-vs-GraphQL decision, REST contract design itself, or GraphQL.
spec_version: "1.0"
---

## Purpose & scope

**OpenAPI is the specification; Swagger is SmartBear's tooling that consumes
and visualizes it.** OpenAPI (OAS) is a vendor-neutral, machine-readable
format for describing HTTP-based APIs, maintained by the OpenAPI Initiative
since it was donated by SmartBear as Swagger 2.0 in 2016 [Source:
https://learn.openapis.org/introduction.html]. Swagger UI/Editor/Codegen are
three distinct official tools that read an OpenAPI document and render docs,
provide a design/editing surface, or generate client/server code from it
[Source: https://github.com/swagger-api/swagger-ui;
https://github.com/swagger-api/swagger-codegen] — Swagger does not define
its own competing spec today; it implements OAS. This skill owns OpenAPI
document structure/authoring and Swagger tooling mechanics. It does **not**
own the REST-vs-GraphQL paradigm decision or REST contract design itself
(both belong to [api-design](../api-design/SKILL.md)), nor GraphQL schema
design ([graphql-api-design](../graphql-api-design/SKILL.md)).

## When to use / When not to use

**Use** when writing or reviewing an OpenAPI document, configuring Swagger
UI/Editor/Codegen, deciding design-first vs. code-first authoring, or
generating a mock server/SDK/server-stub from an existing spec. **Do not
use** for the REST-vs-GraphQL decision or REST resource/versioning/pagination
contract design with no spec-tooling question (api-design), GraphQL
schema/resolver work (graphql-api-design), or prose documentation unrelated
to an API spec (technical-documentation).

## Knowledge

**Document structure.** The root of an OpenAPI document is the OpenAPI
Object, which must contain `openapi` (version string), an `info` object
(minimum `title` + `version`), and at least one of `paths`, `components`, or
`webhooks` [Source: https://learn.openapis.org/specification/structure.html].
`paths` holds the endpoints/operations; `components` holds reusable
Schema/Response/Parameter/SecurityScheme objects referenced via `$ref`;
`webhooks` describes incoming callbacks the API may initiate; `servers`
lists target endpoint URLs [Source:
https://learn.openapis.org/specification/structure.html]. An OpenAPI
Description (OAD) can span multiple physical documents linked by reference,
with one designated entry document [Source:
https://learn.openapis.org/specification/structure.html] — resolved
references form a **graph, not necessarily a tree**, so a tool that resolves
`$ref` by removal/substitution rather than in-memory graph resolution cannot
correctly support every valid OAD [Source:
https://learn.openapis.org/referencing/resolve.html].

**Security schemes.** Security Scheme Objects support five types —
`apiKey`, `http` (Basic/Bearer/other RFC 7235 schemes), `mutualTLS`,
`oauth2`, and `openIdConnect` — defined once under
`components.securitySchemes` and referenced by name from Security
Requirement Objects, applicable globally (`security`) or per-operation (an
operation-level `security` overrides the global one); schemes cannot be
declared inline [Source:
https://learn.openapis.org/specification/security.html]. OAS 3.2.0 adds the
OAuth 2.0 Device Authorization Flow and an `oauth2MetadataUrl` field for
automatic OAuth 2.0 Authorization Server Metadata discovery, narrowing the
gap with OpenID Connect discovery [Version-sensitive: OpenAPI 3.2.0 —
Source: research/knowledge-maps/technology-decision-matrix.md §7]. (The full
REST-vs-GraphQL security-scheme comparison lives in
[api-design](../api-design/SKILL.md); this skill covers only the OAS-side
object model.)

**Swagger's three tools.** *Swagger UI* renders interactive, browsable
documentation from an OpenAPI-compliant document, without needing the API's
source code [Source: https://github.com/swagger-api/swagger-ui]. *Swagger
Editor* validates OAS syntax live as you type and renders a live preview
[Source: https://swagger.io/tools/swagger-editor/]. *Swagger Codegen* is a
template-driven engine generating client SDKs, server stubs, and docs from
an OpenAPI/Swagger definition via `java -jar swagger-codegen-cli.jar
generate -i <spec> -l <language> -o <output-dir>`, with two parallel major
lines (3.x for OpenAPI 3.0.x, 2.x for Swagger/OpenAPI 1.0–2.0) rather than a
linear upgrade path [Source:
https://github.com/swagger-api/swagger-codegen/blob/master/README.md]. Full
Swagger UI JS config table, `initOAuth()` options, Docker env vars, and the
Codegen CLI reference are in
[references/swagger-ui-configuration.md](references/swagger-ui-configuration.md).

**Design-first vs. code-first authoring.** The official best-practices guide
states "the number of APIs that can be created in code is far superior to
what can be described in OpenAPI," and that generating descriptions after
the fact from code tends to produce "unintuitive and incomplete
descriptions" that scale poorly — design-first is the recommended default
[Source: https://learn.openapis.org/best-practices.html]. If code and a
hand-written OAD must coexist, verify their consistency via CI rather than
trusting both stay in sync manually [Source:
https://learn.openapis.org/best-practices.html]. Note the exception:
[SK-TECH-fastify](../fastify/SKILL.md) (a sibling skill in this library)
generates OpenAPI documents directly from its route schemas — for that
stack, code-first is not the anti-pattern the general guidance warns
against, because the schema (not free-hand code) is the single source of
truth generating both validation and the spec.

## Decision framework

1. **Design-first or code-first?** Default to design-first: write/edit the
   OpenAPI document before or alongside implementation, treat it as a
   first-class, version-controlled source file, and wire it into CI to keep
   code and spec consistent [Source:
   https://learn.openapis.org/best-practices.html]. Code-first is acceptable
   when the framework generates the OAD from a schema that is *itself* the
   source of truth (e.g. Fastify route schemas — see
   [SK-TECH-fastify](../fastify/SKILL.md)) rather than from ad hoc
   annotations bolted onto existing handlers.
2. **Hand-author, or use an editor/generator?** For anything beyond a small
   API, prefer Swagger Editor, another domain-specific editor, or a
   code-annotation generator over hand-writing large YAML/JSON — the docs
   call hand-authoring at scale impractical [Source:
   https://learn.openapis.org/best-practices.html].
3. **Self-host Swagger UI, or use a hosted/alternative doc renderer?**
   Self-hosting means owning the patch cadence: only the 5.x line receives
   security patches, and there is a real, documented CVE
   (GHSA-qrmm-w75w-3wpx) in older versions (see Security below). The
   simplest, do-nothing-extra option — pin `swagger-ui`/`swagger-ui-dist` to
   a current 5.x release, keep it on that patch cadence, and never enable
   `?url` overrides — is sufficient for most teams; only reach for a managed
   alternative if there is no capacity to track SmartBear's advisories and
   apply upgrades on schedule. Do not self-host an old pinned version
   "because it works" — an EOL major version accumulates unpatched, publicly
   known vulnerabilities over time [Source:
   https://github.com/swagger-api/swagger-ui/security].
4. **Codegen: Swagger Codegen or the community fork?** Swagger Codegen has
   no official Swagger-side migration guidance toward OpenAPI Generator (a
   well-known community fork) [Source: research/knowledge-maps/technology-decision-matrix.md
   §7] — pick whichever the target language's templates better support and
   stay consistent; do not treat this as an in-place upgrade path.

## Workflow

1. Confirm a REST contract exists (domain model, resources, status/error
   semantics) — if not, hand off to api-design first.
2. Apply the decision framework: design-first vs. code-first.
3. Author/extend the OpenAPI document: `info`, `paths`, `components`
   (including `securitySchemes`), `servers`, and `tags`; factor any
   fragment repeated more than once into `components` and reference it via
   `$ref` [Source: https://learn.openapis.org/best-practices.html].
4. Wire the document into CI: validate it parses, and check
   implementation-matches-spec where feasible [Source:
   https://learn.openapis.org/best-practices.html].
5. Expose the OAD to consumers directly (e.g. served alongside the API) so
   they can self-serve client generation [Source:
   https://learn.openapis.org/best-practices.html].
6. If serving Swagger UI: configure it with `deepLinking`/`docExpansion`
   deliberately, never set `clientSecret` in `initOAuth()`, and leave `?url`
   overrides disabled unless a specific, controlled need exists (see
   Security).
7. If generating clients/servers/mocks: run Swagger Codegen (or a mock
   server) against the finished document rather than a half-written one.

## Engineering rules

- Declare security schemes under `components.securitySchemes` and reference
  them by name; never declare a security scheme inline [Source:
  https://learn.openapis.org/specification/security.html].
- Move any YAML/JSON fragment that appears more than once into `components`
  and reference it via `$ref` [Source:
  https://learn.openapis.org/best-practices.html].
- Treat the OpenAPI document as a first-class, version-controlled source
  file wired into CI — not a document maintained by hand, out-of-band from
  the code [Source: https://learn.openapis.org/best-practices.html].
- Prefer the `swagger-ui` npm module (bundler-friendly) over
  `swagger-ui-dist` (pre-bundled) whenever build tooling supports it, since
  `swagger-ui-dist` ships more code to the client [Source:
  https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/installation.md].
- Pin Swagger UI/Editor/Codegen to explicit versions (e.g. in a CDN URL or
  Docker tag) rather than `@latest`, and track that pin against the 5.x
  support line [Source:
  https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/installation.md;
  https://github.com/swagger-api/swagger-ui/security].

## Trade-offs

Design-first authoring costs upfront discipline (writing/maintaining the
OAD as a real artifact) in exchange for a spec that stays complete and
intuitive as the API grows [Source:
https://learn.openapis.org/best-practices.html]. Code-first/annotation-driven
generation is faster to start but risks incomplete or unintuitive
descriptions at scale — unless, as with Fastify, the generating schema is
itself authoritative rather than an afterthought annotation layer. Swagger
UI's Redux-based plugin architecture is flexible but has no built-in
dependency management for plugins — the integrator must sequence plugin
registration manually [Source:
https://swagger.io/docs/open-source-tools/swagger-ui/customization/plugin-api/].

## Anti-patterns

- **Duplicating API truth across code and a separately maintained OpenAPI
  document with no consistency check** — the docs explicitly call out
  divergence ("headaches") as the predictable outcome [Source:
  https://learn.openapis.org/best-practices.html].
- **Writing the OpenAPI description code-first/after implementation** for
  anything beyond a small API — produces incomplete, unintuitive
  descriptions that scale poorly [Source:
  https://learn.openapis.org/best-practices.html]. (This is the domain's
  over-engineering-adjacent trap in reverse: skipping the spec-as-source-of
  -truth investment early, then paying for it later in drift and rework.)
- **Setting `clientSecret` in `initOAuth()` in production** — see Security.
- **Leaving `useUnsafeMarkdown` enabled** — it is deprecated and removes
  markdown sanitization, reintroducing an XSS risk class [Source:
  https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/].
- **Self-hosting a pinned Swagger UI major version indefinitely without
  tracking the EOL line** — 4.x/3.x/2.x receive no further security patches
  (see Security); "it still renders fine" is not a patch-status check.

## Security

**GHSA-qrmm-w75w-3wpx** (no CVE assigned): a Moderate-severity SSRF-adjacent
vulnerability in Swagger UI. An attacker-crafted `?url` query-string value
(e.g. `https://example.com/api-docs?url=https://evildomain/fakeapi.yaml`)
could point a legitimately hosted Swagger UI at an attacker-controlled spec
— a phishing vector that can trick users into submitting credentials/data
through "Try it out" while trusting the legitimate domain [Source:
https://github.com/advisories/GHSA-qrmm-w75w-3wpx]. **Affected:**
`swagger-ui`, `swagger-ui-dist`, `swagger-ui-react` (npm) versions < 4.1.3.
**Fixed** in those packages at >= 4.1.3 by disabling query-string spec
overrides by default (re-enabling is opt-in) [Version-sensitive: applies to
Swagger UI < 4.1.3 — Source:
https://github.com/advisories/GHSA-qrmm-w75w-3wpx]. In production, keep
`?url` overrides disabled unless there is a specific, controlled need.

**EOL/patch policy:** only the **5.x line** currently receives security
patches. 4.x reached EOL August 2023; 3.x reached EOL November 2021; 2.x
reached EOL in 2017 [Source: https://github.com/swagger-api/swagger-ui/security].
There is no fixed-cadence LTS calendar commitment — EOL is tied to the next
major release. A production deployment pinned to an EOL major version
accumulates unpatched, publicly known vulnerabilities over time [Source:
https://github.com/swagger-api/swagger-ui/security]. Treat "which Swagger
UI major version is deployed" as a standing question to check, not a
one-time setup decision.

**Never set `clientSecret` in `initOAuth()` in production** — the official
docs flag this explicitly ("Never use this parameter in your production
environment. It exposes crucial security information.") because it embeds a
confidential OAuth client secret in a client-side, publicly servable
configuration [Source:
https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/]. Use
`usePkceWithAuthorizationCodeGrant: true` for the authorization-code grant
where a public client is involved instead [Source:
https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/].

Cross-cutting threat modeling and secret-handling practice are owned by
[security-engineering](../../core/taxonomy/skill-catalog.md); this section
covers only OpenAPI/Swagger-specific exposures. (The REST-vs-GraphQL
security-scheme comparison is owned by [api-design](../api-design/SKILL.md)
— not restated here.)

## Performance

OpenAPI itself is a static document format; the official docs do not
present a spec-level performance section — the one architectural point made
is that tools resolving `$ref` in-memory as a graph can handle any valid
OAD, while removal-based tools are limited to tree-shaped reference
structures [Source: https://learn.openapis.org/referencing/resolve.html].
For Swagger UI, v5.0.0 cited "performance optimizations for sub-tree
expansion in complex schemas" [Source:
https://github.com/swagger-api/swagger-ui/releases/tag/v5.0.0], and choosing
the bundler-friendly `swagger-ui` package over `swagger-ui-dist` is a
documented client-payload-size consideration (see Engineering rules). No
official guidance on document-size limits or rendering benchmarks for very
large specs was found in either source.

## Testing

Mock servers generated directly from an OpenAPI document are a primary
documented use case, enabling early integration testing before the real
implementation exists [Source:
https://learn.openapis.org/introduction.html]. Wiring the OAD into CI to
verify that implementation code matches the spec — and vice versa — is a
named best practice [Source: https://learn.openapis.org/best-practices.html].
Deep test-strategy method beyond these two spec-driven practices is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If no OpenAPI document exists and the underlying REST contract isn't
  designed yet, hand off to api-design first rather than authoring a spec
  against assumptions.
- If the deployed Swagger UI/Editor version is unknown, ask for it before
  asserting CVE/EOL exposure; never assume it is on the patched 5.x line.
- If shell/network access isn't available to run Codegen or fetch a live
  spec, degrade to advisory: propose the OpenAPI document and Swagger
  config as file edits/instructions instead of executing them.

## Escalation

A production Swagger UI deployment found on an EOL line (4.x/3.x/2.x) or
with `?url` overrides re-enabled is a security exposure — flag it and
require explicit confirmation before treating remediation as optional.

## Outputs & verification

- **Outputs:** an OpenAPI document (or diff), Swagger UI/Editor/Codegen
  configuration, and/or a design-first-vs-code-first or CVE/EOL exposure
  analysis.
- **Verify:** security schemes are declared under `components.securitySchemes`
  and referenced by name; any production Swagger UI config omits
  `clientSecret` from `initOAuth()` and leaves `?url` overrides disabled
  unless a stated need exists; the Swagger UI/Editor/Codegen version in use
  is on the 5.x line or the EOL risk is explicitly called out.

## References

- [references/swagger-ui-configuration.md](references/swagger-ui-configuration.md) — full Swagger UI JS config table, `initOAuth()` options, Docker env vars, Codegen CLI reference.
- [research/technologies/openapi.md](../../research/technologies/openapi.md)
- [research/technologies/swagger.md](../../research/technologies/swagger.md)
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md) — §7, OpenAPI vs. GraphQL (plus Swagger)
- [api-design](../api-design/SKILL.md) — REST-vs-GraphQL and OpenAPI-vs-GraphQL comparisons (not duplicated here)
