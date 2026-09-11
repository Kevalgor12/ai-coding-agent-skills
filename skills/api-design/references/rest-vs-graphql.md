# REST (OpenAPI) vs. GraphQL comparison (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Condensed from
[technology-decision-matrix.md §7](../../../research/knowledge-maps/technology-decision-matrix.md)
— consult that document for the full citation trail.

| | OpenAPI (REST) | GraphQL |
|---|---|---|
| Model | Discrete REST-style operations per resource/URL | Single-endpoint graph-query model |
| Versioning | Implicit via URL/path convention (`/v1`, `/v2`) | Schema evolution (add fields/types without breaking clients) as REST-versioning's documented alternative |
| Security scheme model | Formal: `apiKey`/`http`/`mutualTLS`/`oauth2`/`openIdConnect`, declarable globally or per-operation | No formal equivalent; relies on transport (TLS) + app-layer authorization |
| DoS exposure | Not an inherent spec-level risk (static documentation) | **Explicitly documented**: one endpoint can express wildly varying query cost (nesting, aliasing, batching) |
| Recommended DoS mitigation | N/A | Max query depth, nested-list limits, alias/top-level-field caps, batch-op caps; fixed-window rate limiting explicitly called insufficient |
| Introspection | N/A | Disabling in production is common; trusted-document allowlisting recommended over blanket disabling |
| N+1-class issue | N/A | The most common documented GraphQL performance issue, from per-field resolver execution; DataLoader-style batching is the standard fix |
| Caching | Standard HTTP caching (GET + headers) applies naturally | Persisted queries (hash instead of full text) enable HTTP/CDN caching of otherwise-uncacheable POST requests; multi-layer caching recommended |
| Testing/contract verification | Mock-server generation from the spec is a primary documented use case; CI verification against the spec is a named best practice | **No official testing methodology guide located** — `graphql-js.org/docs/testing/` 404'd during research |
| Recent spec evolution | OAS 3.2.0 adds OAuth2 Device Authorization Flow + `oauth2MetadataUrl` for discovery | Not comparably covered in the source data |

**Swagger** (tooling, not a spec alternative): consumes/visualizes an
OpenAPI document via three official tools (UI/Editor/Codegen); had a real
CVE (GHSA-qrmm-w75w-3wpx, SSRF-adjacent via a crafted `?url` parameter,
fixed in `swagger-ui`/`swagger-ui-dist`/`swagger-ui-react` ≥ 4.1.3); only the
5.x line receives security patches. Full detail in the
[openapi-swagger](../../openapi-swagger/SKILL.md) skill.

**Unresolved (per the source research):** "which is more secure, OpenAPI or
GraphQL" is not a question the underlying research can answer — OpenAPI's
own security-scope statement puts deployment-level mechanics out of spec
scope, and the two operate at different layers (static contract vs. runtime
query language). GraphQL's larger attack surface is a function of its
dynamic query model, not a documented security ranking against REST.
