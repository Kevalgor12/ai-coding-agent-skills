# OpenAPI Specification (OAS)

Research scope note: OpenAPI is a **specification/standard**, not a runnable piece of software. Several of the 17 dimensions below (Architecture as "system design," Performance, Deployment, Testing, Debugging as tool behavior) do not map onto a specification the way they would onto a library or framework. Where that is the case, this document says so explicitly and reports what the official docs *do* say about the adjacent, applicable concept, rather than inventing framework-style content.

Primary official sources used:
- [Source: https://www.openapis.org/] — OpenAPI Initiative homepage
- [Source: https://spec.openapis.org/] — Specification hub (OpenAPI, Arazzo, Overlay specs + registries)
- [Source: https://spec.openapis.org/oas/v3.2.0.html] — OpenAPI Specification v3.2.0 (current)
- [Source: https://spec.openapis.org/oas/v3.1.0.html] — OpenAPI Specification v3.1.0
- [Source: https://learn.openapis.org/] — "Learn OpenAPI" companion documentation site (OAI-maintained)
- [Source: https://learn.openapis.org/introduction.html] — Introduction / core concepts
- [Source: https://learn.openapis.org/specification/structure.html] — Document structure
- [Source: https://learn.openapis.org/specification/security.html] — Describing API Security
- [Source: https://learn.openapis.org/best-practices.html] — Best Practices
- [Source: https://learn.openapis.org/upgrading/v3.0-to-v3.1.html] — Upgrading 3.0 → 3.1
- [Source: https://learn.openapis.org/upgrading/v3.1-to-v3.2.html] — Upgrading 3.1 → 3.2
- [Source: https://learn.openapis.org/referencing/overview.html] and https://learn.openapis.org/referencing/resolve.html — Referencing ($ref) mechanics
- [Source: https://github.com/OAI/OpenAPI-Specification/releases] — Official release history (GitHub Releases, OAI org repo)
- [Source: https://api.github.com/repos/OAI/OpenAPI-Specification/releases] — Machine-readable release/publish dates (GitHub API, OAI org repo)
- [Source: https://www.openapis.org/blog/2025/09/23/announcing-openapi-v3-2] — Official 3.2.0 announcement blog post
- [Source: https://www.openapis.org/faq] — Official FAQ
- [Source: https://spec.openapis.org/overlay/v1.0.0.html] — Overlay Specification v1.0.0
- [Source: https://spec.openapis.org/arazzo/v1.0.1.html] — Arazzo Specification v1.0.1
- [Source: https://spec.openapis.org/registry/] — OAI registries (extensions, formats, media types, tag kinds)
- [Source: https://github.com/OAI/sig-moonwalk] — Moonwalk SIG (future OAS 4.0 effort, OAI org repo)

---

## 1. Core Concepts

[Source: https://learn.openapis.org/introduction.html] The OpenAPI Specification (OAS) is a vendor-neutral, machine-readable format for describing HTTP-based (and HTTP-like, e.g. WebSocket, CoAP) remote APIs. It was originally derived from the Swagger 2.0 specification, donated by SmartBear Software, and has been maintained separately since 2016 by the OpenAPI Initiative (OAI).

[Source: https://learn.openapis.org/introduction.html] An **OpenAPI Description (OAD)** is the umbrella term for "one or more documents (such as local files or HTTP-accessible network resources)" that together, via references, describe an API using the OAS format. A single OAD can span multiple physical documents.

[Source: https://learn.openapis.org/introduction.html] Key terminology: **API Provider** (the entity offering the API), **API Consumer** (the entity calling it), and **API Contract** (the provider's commitment to keep the described behavior consistent over time). The docs draw an explicit analogy: machine-readable remote-API descriptions serve the same role that local method/function signatures serve for compiled code — enabling earlier error detection and reducing runtime failures.

[Source: https://learn.openapis.org/introduction.html] OAS deliberately does not attempt to describe every conceivable API; it "tries to describe efficiently the most common use cases," focused on HTTP and HTTP-like protocols.

[Source: https://learn.openapis.org/introduction.html] Stated benefits of having a machine-readable API description: automatic generation of human-readable documentation that stays in sync with the description, generation of server/client boilerplate code in arbitrary languages (removing the need to hand-write data validation or SDK glue code), GUI-based description editors, and mock servers that return example responses for early integration testing.

[Source: https://spec.openapis.org/oas/v3.2.0.html] The root of an OpenAPI document is the **OpenAPI Object**, which — per the structure page below — must contain `openapi` (version string), an `info` object, and at least one of `paths`, `components`, or `webhooks`.

## 2. Architecture

[Inference, not confirmed in docs] "Architecture" in the software-system sense (processes, data flow, deployment topology) does not apply to a specification. What the official docs do describe is the **document architecture** of an OpenAPI Description:

[Source: https://learn.openapis.org/specification/structure.html] Required root fields: `openapi` (the OAS version this document conforms to, e.g. `3.1.0`), `info` (metadata Object requiring at minimum `title` and `version`), and at least one of `paths`, `components`, or `webhooks`.

[Source: https://learn.openapis.org/specification/structure.html] Other top-level sections: `servers` (target endpoint URLs), `paths` (endpoints/operations), `webhooks` (incoming callbacks the API may initiate), `components` (reusable Schema/Response/Parameter/SecurityScheme objects, etc., referenced via `$ref`), and `security`/`tags`/`externalDocs`.

[Source: https://spec.openapis.org/oas/v3.2.0.html] Version 3.2.0 adds an optional `$self` field at the document root that gives the document a canonical URI, used to identify "the document containing the OpenAPI Object where parsing begins" — termed the OAD's **entry document** — in a multi-document OAD.

[Source: https://learn.openapis.org/referencing/resolve.html] An OpenAPI Description with all `$ref` references resolved is **not necessarily a tree — it is a graph**. This is an explicit architectural point in the docs: "Tools that resolve references in-memory and work with the graph structure can process all OADs. Tools that rely on reference removal … can only support OADs that form trees." This distinguishes reference *resolution* (target identified, references preserved for tooling/debuggability) from reference *removal* (target value substituted in place, discarding the reference itself).

[Source: https://learn.openapis.org/specification/structure.html] Documents can be split across multiple files/network resources and linked via references, with one designated entry document.

## 3. APIs

[Inference, not confirmed in docs] OpenAPI is a document format/data model, not a programmatic API with function calls, so there is no "API" in the SDK sense to document. What the specification *is*, functionally, is the object model that any conforming tool's API must expose/consume. Key object types documented across the spec and Learn site:

[Source: https://learn.openapis.org/specification/structure.html] Info Object, Server Object, Paths Object, Path Item Object, Operation Object, Parameter Object, Request Body Object, Response Object, Components Object, Security Scheme Object, Tag Object, External Documentation Object.

[Source: https://learn.openapis.org/specification/security.html] Security Scheme Object supports five types: `apiKey` (credential in header/query/cookie), `http` (RFC 7235 schemes such as Basic and Bearer, with an optional `bearerFormat` hint like `JWT`), `mutualTLS` (client-cert transport-layer auth), `oauth2` (with configurable flows/grant types and scopes), and `openIdConnect` (OAuth2 profile using a discovery document). Security Scheme Objects must be defined under `components.securitySchemes` and referenced by name from Security Requirement Objects — they cannot be declared inline.

[Source: https://www.openapis.org/blog/2025/09/23/announcing-openapi-v3-2] New in 3.2.0: the `query` HTTP method as a native Operation location (safe/idempotent queries with a request payload), the `additionalOperations` field for defining arbitrary/non-standard HTTP methods as full Operation Objects, and a `querystring` keyword letting all query parameters be described as one unified Schema Object.

[Source: https://www.openapis.org/blog/2025/09/23/announcing-openapi-v3-2] New Tag Object fields in 3.2.0: `summary`, `parent` (for hierarchical/nested tags), and `kind` (machine-readable classification, backed by the OAI Tag Kind Registry).

[Source: https://www.openapis.org/blog/2025/09/23/announcing-openapi-v3-2] New streaming/sequential media type support in 3.2.0: recognizes Server-Sent Events (`text/event-stream`), JSON Lines (`application/jsonl`), JSON Text Sequences (`application/json-seq`), and `multipart/mixed`, with a new `itemSchema` keyword describing the schema of each individual streamed item/event.

[Source: https://www.openapis.org/blog/2025/09/23/announcing-openapi-v3-2] Security-related additions in 3.2.0: OAuth2 Device Authorization Flow support (for limited-input devices), and an `oauth2MetadataUrl` property enabling automatic discovery of OAuth 2.0 Authorization Server Metadata.

[Source: https://spec.openapis.org/registry/] The OAI also maintains companion **registries** (not part of the core spec document but referenced by it): Extension Field Registry, Extension Field Namespace Registry, Format Registry, Media Type Registry, Tag Kind Registry, Draft Features Registry, and Alternative Schema Type Registry — community-contributed catalogs of values usable in OAS documents (e.g., `x-` extension fields, `format` strings).

## 4. Configuration

[Inference, not confirmed in docs] There is no runtime "configuration" for a specification. The closest analog documented is how an OpenAPI *document itself* is configured/declared:

[Source: https://learn.openapis.org/specification/structure.html] The `openapi` field declares which specification version the document conforms to (e.g. `3.1.0`, `3.2.0`) and must be a valid version string; tooling uses this to select parsing/validation rules.

[Source: https://learn.openapis.org/upgrading/v3.0-to-v3.1.html] The `jsonSchemaDialect` root field (introduced in 3.1) lets a document declare the default JSON Schema `$schema` dialect used by Schema Objects in that document, avoiding ambiguity when tools process documents that mix schema dialects.

[Source: https://spec.openapis.org/overlay/v1.0.0.html] The separate **Overlay Specification** (currently v1.0.0, released 2024-10-17) provides a declarative, out-of-band "configuration" mechanism for OpenAPI documents: an Overlay is its own JSON/YAML document containing an ordered list of actions that use JSONPath expressions to target elements of an existing OpenAPI Description and update or remove them — used to enrich, redact, or otherwise transform a description without editing it directly, and repeatably (e.g. in CI) or across multiple target documents.

## 5. Recommended Patterns

[Source: https://learn.openapis.org/best-practices.html] **Design-first approach**: the docs state "the number of APIs that can be created in code is far superior to what can be described in OpenAPI," and that generating descriptions after the fact from code tends to produce "unintuitive and incomplete descriptions" that scale poorly — designing the OAD first is the recommended approach.

[Source: https://learn.openapis.org/best-practices.html] **Single source of truth**: avoid maintaining API details in two places (e.g. code annotations and a hand-written OpenAPI file) because "one of the places will be updated while the other won't, leading to headaches"; if two sources must coexist, verify their consistency via CI.

[Source: https://learn.openapis.org/best-practices.html] **Treat the OAD as a first-class source file**: commit it to source control early, and wire it into automated processes such as codegen and testing.

[Source: https://learn.openapis.org/best-practices.html] **Expose the OAD to consumers directly** so they can generate client code or automated bindings themselves.

[Source: https://learn.openapis.org/best-practices.html] **For large APIs**: move any YAML/JSON fragment that appears more than once into `components` and reference it via `$ref` rather than duplicating it; split files along natural URL/resource hierarchies; apply `tags` to operations for organization and discoverability.

[Source: https://learn.openapis.org/best-practices.html] Prefer editors, domain-specific tooling, or code-annotation generators over hand-writing large OpenAPI documents by hand, since hand-authoring becomes impractical at scale.

[Source: https://learn.openapis.org/referencing/overview.html] Use referencing (`$ref`) deliberately to manage document size/complexity and to avoid copy-paste/change-management errors from duplicated fragments — this is presented as a core recommended pattern, not just an optional feature.

## 6. Anti-Patterns

[Source: https://learn.openapis.org/best-practices.html] Duplicating API truth across code and a separately maintained OpenAPI document without a consistency check — the docs explicitly call out that divergence ("headaches") is the predictable outcome.

[Source: https://learn.openapis.org/best-practices.html] Writing the OpenAPI description code-first / after implementation for anything beyond a small API — flagged as producing incomplete, unintuitive descriptions.

[Source: https://learn.openapis.org/best-practices.html] Hand-authoring large documents without tooling (editors/generators) — described as impractical for larger projects, implying it as something to avoid.

[Source: https://learn.openapis.org/best-practices.html] Repeating the same YAML/JSON fragment across a document instead of factoring it into `components` — explicitly called out as the trigger to refactor into reusable components.

[Inference, not confirmed in docs] Relying on reference-*removal* tooling for documents that contain non-tree (graph/cyclic) reference structures would be an anti-pattern given the docs' explicit statement that removal-based tools "can only support OADs that form trees" [Source: https://learn.openapis.org/referencing/resolve.html] — but the docs describe this as a tooling capability limitation rather than using the word "anti-pattern" themselves.

## 7. Security

[Source: https://learn.openapis.org/specification/security.html] OAS models API security via **Security Scheme Objects**, defined once under `components.securitySchemes` and referenced (never declared inline) by name from **Security Requirement Objects**, which can be applied globally (root-level `security`) or per-operation; an operation-level `security` declaration overrides the global one.

[Source: https://learn.openapis.org/specification/security.html] Five scheme types are supported: `apiKey`, `http` (Basic/Bearer/other RFC 7235 schemes), `mutualTLS`, `oauth2` (multiple flows: e.g. Authorization Code, Client Credentials), and `openIdConnect`.

[Source: https://learn.openapis.org/specification/security.html] For OAuth2, the docs recommend creating **separate Security Scheme Objects** to segregate different grant types or to differentiate available scopes, rather than overloading one scheme object.

[Source: https://learn.openapis.org/specification/security.html] For OpenID Connect, scopes can be omitted from the OpenAPI description itself since they can be resolved via the identity provider's discovery endpoint.

[Source: https://learn.openapis.org/specification/security.html] Explicit scope statement: OAS aims to give "humans and tooling the means to understand the basic security requirements" of an API, but deployment-level security concerns — such as key exchange mechanics and certificate management — are explicitly **out of scope** for the specification itself.

[Source: https://www.openapis.org/blog/2025/09/23/announcing-openapi-v3-2] OAS 3.2.0 adds OAuth 2.0 **Device Authorization Flow** (for limited-input devices such as smart TVs) and an `oauth2MetadataUrl` property enabling automatic discovery of OAuth 2.0 Authorization Server Metadata (RFC 8414-style), narrowing the gap with OpenID Connect discovery. It also adds URI-based security-scheme references and a way to mark security schemes deprecated. [Version-sensitive: 3.2.0 only]

[Inference, not confirmed in docs] Because OAS only *describes* security requirements and does not itself perform authentication/authorization, actual runtime enforcement (validating tokens, checking scopes) is the responsibility of the API implementation or gateway — this is a natural consequence of the documented "out of scope" statement above rather than a separately stated claim.

## 8. Performance

Not documented / could not verify as a distinct topic. [Inference, not confirmed in docs] OpenAPI is a static document format; the official docs do not present a "performance" section for the specification itself. The one performance-adjacent point made is architectural, not a benchmark or tuning guide: [Source: https://learn.openapis.org/referencing/resolve.html] tools that resolve `$ref` in-memory as a graph can handle any valid OAD, while tools that resolve by physically substituting ("removing") references can only handle documents whose reference graph forms a tree — a scalability/capability constraint on tooling, not on the spec itself. No guidance on document size limits, parse-time benchmarks, or runtime performance of generated code was found in the primary sources consulted.

## 9. Testing

[Source: https://learn.openapis.org/introduction.html] The docs describe **mock servers** as one of the primary use cases enabled by a machine-readable OpenAPI Description: tooling can "create fake servers providing example responses," which supports early integration testing against an API description before the real implementation exists.

[Source: https://learn.openapis.org/best-practices.html] The best-practices guidance recommends wiring the OAD into automated CI processes, including using it to keep code and description in sync ("processes that verify... code matches the OpenAPI descriptions, and vice versa") — i.e., using the spec as a contract-testing source of truth.

[Inference, not confirmed in docs] Beyond mock-server generation and CI consistency checks, the official docs consulted do not describe a dedicated OpenAPI testing framework or methodology of their own — testing tooling (contract testing, fuzzing against a schema, etc.) is left to the third-party tooling ecosystem, which the docs note is tracked on a separate community "OpenAPI Tooling" site rather than in the core/Learn docs. [Source: https://www.openapis.org/]

## 10. Deployment

[Inference, not confirmed in docs] "Deployment" in the runtime-service sense does not apply to a specification. What the docs describe instead is **publishing/distributing the description document**:

[Source: https://learn.openapis.org/best-practices.html] Recommendation to make the OpenAPI Description directly available to API consumers (e.g., published alongside or from the API itself) so they can generate clients/bindings.

[Source: https://learn.openapis.org/specification/structure.html] An OAD can be a single local file or one or more HTTP-accessible network resources, with one entry document; multi-document OADs are explicitly supported via references, implying documents can be distributed/hosted separately and resolved at consumption time.

[Source: https://spec.openapis.org/oas/v3.2.0.html] The 3.2.0 `$self` field lets a document assert its own canonical URI, which is relevant when a description is deployed/served from multiple locations or bundled differently by different tools.

## 11. Migration

[Source: https://learn.openapis.org/upgrading/v3.0-to-v3.1.html] **Upgrading 3.0 → 3.1** [Version-sensitive: 3.0.x → 3.1.x], documented required changes:
- Update the `openapi` field (e.g. `3.0.3` → `3.1.1`).
- `nullable: true` is removed; use JSON Schema type arrays instead, e.g. `type: string` + `nullable: true` becomes `type: ["string", "null"]`.
- `exclusiveMinimum`/`exclusiveMaximum` change from booleans modifying `minimum`/`maximum` to standalone numeric values directly, e.g. `minimum: 7` + `exclusiveMinimum: true` becomes `exclusiveMinimum: 7`.
- Singular `example` on Schema Objects should move to the plural `examples` array form.
- File upload descriptions change: binary files drop `format` in favor of an empty/unconstrained schema; base64 uploads use `contentEncoding: base64` instead of `format: base64`; multipart uploads use `contentMediaType` (e.g. `application/octet-stream`) instead of a `format` keyword.
- Optional: declare `$schema` / `jsonSchemaDialect` explicitly to avoid ambiguity across mixed-dialect tooling.
- Recommendation: validate the upgraded document against 3.1-compatible tooling afterward.

[Source: https://learn.openapis.org/upgrading/v3.1-to-v3.2.html] **Upgrading 3.1 → 3.2** [Version-sensitive: 3.1.x → 3.2.0]: explicitly stated as **non-breaking** — "OpenAPI 3.2 does not introduce breaking changes. All existing 3.1 documents will work without modification" after updating the `openapi` version field. New optional capabilities available after upgrading include the enhanced Tag Object (`parent`/`kind`/`summary`), the `query` HTTP method and `additionalOperations`, sequential/streaming media type support (`itemSchema`), OAuth2 Device Flow / `oauth2MetadataUrl`, Discriminator `defaultMapping`, and example `dataValue`/`serializedValue` fields.

[Source: https://www.openapis.org/faq] The OAS lineage: originally the Swagger Specification (donated by SmartBear), became the independent, OAI-governed "OpenAPI Specification" starting with 3.0 in 2016/2017 — i.e., **Swagger 2.0 → OpenAPI 3.0** is itself a major, non-trivial migration (schema/structure changes), though the FAQ page consulted did not enumerate the 2.0→3.0 field-by-field differences; the Learn site's "Upgrading Between Versions" section (per its table of contents) also includes a "1.0 to 3.2" migration path in its index, but individual step-by-step content for that specific path was not directly retrieved in this research pass. Unresolved: exact documented steps for Swagger 2.0 → OAS 3.0 migration were not fetched/verified in this pass; only the 3.0→3.1 and 3.1→3.2 guides were confirmed in detail.

[Source: https://spec.openapis.org/overlay/v1.0.0.html] Overlays are also positioned as a **migration/transformation tool**: repeatable, declarative, JSONPath-driven edits that can be used to adapt or update descriptions (e.g., across versions or for different audiences) without hand-editing the source OAD.

[Source: https://github.com/OAI/sig-moonwalk] A future **OAS 4.0 ("Moonwalk")** is in early design (Architectural Design Records, not yet a formal spec as of the sources checked); the SIG's own repo states it will pursue "an automated upgrade process from 3.x to 4.0," but this does not exist yet and the SIG explicitly recommends continuing to use 3.x today.

## 12. Version Information

[Source: https://api.github.com/repos/OAI/OpenAPI-Specification/releases] Confirmed release history (dates from the official GitHub Releases API, OAI/OpenAPI-Specification repo):

| Version | Published (UTC) |
|---|---|
| 3.2.0 (current stable) | 2025-09-19 |
| 3.1.2 | 2025-09-19 |
| 3.1.1 | 2024-10-24 |
| 3.0.4 | 2024-10-24 |
| 3.1.0 | 2021-02-16 |
| 3.1.0-rc1 | 2020-10-09 |
| 3.1.0-rc0 | 2020-06-18 |
| 3.0.3 | 2020-02-21 |
| 3.0.2 | 2018-10-08 |
| 3.0.1 | 2017-12-07 |
| 3.0.0 | 2017-07-26 |

[Source: https://spec.openapis.org/oas/v3.2.0.html] The **current stable version is 3.2.0**, published 2025-09-19.

[Source: https://www.openapis.org/blog/2025/09/23/announcing-openapi-v3-2] Official announcement of 3.2.0 was published 2025-09-23 (four days after the spec's own publish date) at openapis.org/blog.

[Source: https://www.openapis.org/faq] The FAQ page as fetched in this research pass still states "the latest version is 3.1.1" — this appears to be **stale content on that specific page** relative to the confirmed 3.2.0 release; treat the GitHub release data and the spec.openapis.org v3.2.0 page as authoritative over the FAQ page for "current version." Flagging explicitly per the task's version-sensitivity instruction.

[Source: https://www.openapis.org/faq] There are currently two actively-documented major/minor lines: **3.0.x** (latest patch 3.0.4) and **3.1.x/3.2.x** (3.1 introduced full JSON Schema 2020-12 alignment; 3.2 is additive on top of 3.1 with no breaking changes per the upgrade guide above).

Not documented / could not verify: an explicit LTS/support-window policy (e.g., "3.0.x supported until X date") was not found in the primary sources consulted; the OAI does not appear to publish a formal support-window/EOL schedule the way some software projects do — versions instead remain permanently valid specifications that tools may or may not continue to support.

[Source: https://github.com/OAI/sig-moonwalk] A next major version, OAS 4.0 ("Moonwalk"), is in active design discussion (ADR-based, weekly open meetings per the repo) but has "no planned end date" and is not yet a published specification. [Version-sensitive: forward-looking, not yet released]

## 13. Breaking Changes

[Source: https://learn.openapis.org/upgrading/v3.0-to-v3.1.html] **3.0 → 3.1** is the most recent breaking major/minor transition, requiring document changes (see Migration section above for the full list): removal of `nullable` in favor of JSON Schema type arrays, `exclusiveMinimum`/`exclusiveMaximum` changing from boolean modifiers to direct numeric values, `example` → `examples`, and revised file-upload description patterns (`contentEncoding`/`contentMediaType` replacing certain `format` usages). [Version-sensitive: applies specifically to upgrading pre-3.1 documents to 3.1+]

[Source: https://learn.openapis.org/upgrading/v3.1-to-v3.2.html] **3.1 → 3.2** introduced **no breaking changes** — explicitly stated by the official upgrade guide. All new 3.2 features (structured tags, `query` method, `additionalOperations`, streaming media types, OAuth2 device flow, `$self`, discriminator `defaultMapping`) are additive/optional. [Version-sensitive: 3.2.0]

[Source: https://api.github.com/repos/OAI/OpenAPI-Specification/releases] 3.1.1 (2024-10-24) and 3.0.4 (2024-10-24) were released together as documentation/editorial patch releases; per general OAS patch-release convention (SemVer-style, though not separately confirmed via a dedicated versioning-policy doc in this pass) patch releases are not expected to carry breaking or even normative-requirement changes — they are clarifications only. [Inference, not confirmed in docs: the "no normative changes" characterization for these specific two releases was reported by a web-search summary of the GitHub changelog, not independently re-verified line-by-line against the CHANGELOG.md in this pass, since the raw CHANGELOG.md fetch attempts returned 404s during this research session — flagged as Unresolved below.]

Unresolved: the exact CHANGELOG.md entries for 3.1.1 and 3.0.4 (whether they contain any normative, non-editorial changes) could not be directly fetched in this session — both `github.com/.../blob/main/CHANGELOG.md` and the raw.githubusercontent.com equivalent returned HTTP 404 during this research pass. The release dates and version numbers themselves are confirmed via the GitHub Releases API, but the fine-grained per-release changelog text is not independently re-verified beyond what the v3.1-to-v3.2 and v3.0-to-v3.1 upgrade guides state.

## 14. Limitations

[Source: https://learn.openapis.org/introduction.html] OAS explicitly does **not** aim to describe every possible API; it targets "the most common use cases" for HTTP and HTTP-like (WebSocket, CoAP) protocols specifically — non-HTTP-like RPC/binary protocols are out of its stated scope.

[Source: https://learn.openapis.org/specification/security.html] OAS explicitly limits its security modeling to describing *requirements* (which scheme, where credentials go); it does **not** cover deployment-level security mechanics such as key-exchange procedures or certificate management.

[Source: https://www.openapis.org/faq] Per the official FAQ, OpenAPI and GraphQL "solve similar problems in slightly different ways" — OAS is oriented around discrete REST-style operations rather than the graph-query model GraphQL uses, implying OAS is not positioned as a general graph-query description format.

[Source: https://github.com/OAI/sig-moonwalk] The existence and stated motivation of the Moonwalk (4.0) effort implies the OAI itself considers current 3.x semantics insufficient for some emerging needs (e.g., better machine/AI-semantic support, RPC-style APIs, more flexible URI templating) — these are documented as *drivers for future work*, i.e., implicit current limitations, though phrased prospectively rather than as a formal "Limitations" list in the 3.x spec itself.

[Source: https://learn.openapis.org/referencing/resolve.html] Tooling-level limitation (not a spec limitation per se): tools that resolve `$ref` by removal/substitution rather than in-memory graph resolution cannot correctly support OpenAPI Descriptions whose reference structure is not a tree (e.g., contains shared/cyclic references) — this is a constraint consumers should be aware of when choosing tooling, even though the *specification* itself permits graph-shaped reference structures.

## 15. Debugging

[Inference, not confirmed in docs] There is no runtime process to "debug" in a specification; the closest official concept is **validating/resolving a description correctly**.

[Source: https://learn.openapis.org/referencing/resolve.html] The docs distinguish reference *resolution* from reference *removal* partly on debuggability grounds: resolution ("Its target has been identified" while keeping the reference information) is noted as useful for debugging, since the origin of a resolved value remains traceable, whereas removal (replacing the reference with the target value in place) discards that traceability.

[Inference, not confirmed in docs] Beyond this resolution/removal distinction, the primary Learn/spec sources consulted in this pass did not present a dedicated "debugging your OpenAPI document" guide (e.g., linter usage, common validation-error walkthroughs); such tooling-specific debugging guidance is likely covered by third-party/community tools referenced from the OAI's separate "OpenAPI Tooling" listing site rather than in spec.openapis.org or learn.openapis.org themselves. [Source: https://www.openapis.org/]

## 16. Integration

[Source: https://spec.openapis.org/overlay/v1.0.0.html] **Overlay Specification** (current: v1.0.0, 2024-10-17) is the OAI's own companion spec for non-invasively layering changes onto an OpenAPI Description — e.g., enriching a description with tooling-specific metadata, or redacting fields before sharing externally — via JSONPath-targeted actions in a separate document.

[Source: https://spec.openapis.org/arazzo/v1.0.1.html] **Arazzo Specification** (current: v1.0.1, released 2025-01-16, following 1.0.0 on 2024-05-29) is the OAI's own companion spec for describing **multi-step API workflows** — sequences of calls and their dependencies — built on top of one or more OpenAPI (or other API) descriptions, used to express an end-to-end outcome across several operations rather than a single call.

[Source: https://learn.openapis.org/introduction.html] Generic integration points documented at the concept level: documentation generators, client/server code generators, GUI description editors, and mock servers are all named as first-class consumers of an OpenAPI Description — but the Learn/spec sites intentionally keep the list of specific third-party tools out of the core docs, instead pointing to a community-run "OpenAPI Tooling" site. [Source: https://www.openapis.org/]

[Source: https://spec.openapis.org/registry/] The OAI registries (Extension Field Registry, Format Registry, Media Type Registry, Tag Kind Registry, Alternative Schema Type Registry, Draft Features Registry) function as the sanctioned integration surface for extending OAS documents in tool-interoperable ways — e.g., registering a custom `x-` extension field or a `format` string so multiple independent tools interpret it consistently.

[Source: https://spec.openapis.org/oas/v3.1.0.html] Since 3.1.0, Schema Objects use full **JSON Schema draft 2020-12** semantics (via `jsonSchemaDialect`), which is the primary documented mechanism by which OAS integrates with the broader JSON Schema ecosystem/tooling rather than a bespoke OAS-only schema dialect. [Version-sensitive: 3.1.0+ only — 3.0.x used a JSON-Schema-like but not fully compliant subset, per the nullable/exclusiveMinimum differences documented in the 3.0→3.1 migration guide]

## 17. Production Considerations

[Source: https://learn.openapis.org/best-practices.html] Treat the OpenAPI Description as a first-class, version-controlled source artifact integrated into CI — including automated checks that implementation code and the OAD remain consistent, and automated generation of docs/clients/mocks from it — rather than a document maintained manually and out-of-band from the codebase.

[Source: https://learn.openapis.org/best-practices.html] Publish/expose the OAD to API consumers directly so they can self-serve client generation, rather than only using it internally for documentation generation.

[Source: https://learn.openapis.org/specification/security.html] For production APIs, define distinct Security Scheme Objects per OAuth2 grant type/scope set rather than a single overloaded scheme, and remember that the OAD only *describes* the security requirement — actual enforcement (token validation, cert management, key exchange) must be handled by the running service/gateway, which is explicitly outside the specification's scope.

[Source: https://spec.openapis.org/overlay/v1.0.0.html] For production description management (e.g., redacting internal-only fields before publishing a partner-facing OAD, or injecting environment-specific `servers` values), the officially recommended non-invasive mechanism is an Overlay applied at publish/build time, rather than maintaining hand-forked copies of the source OAD.

[Inference, not confirmed in docs] Given the explicit statement that OAS does not cover deployment-level security mechanics [Source: https://learn.openapis.org/specification/security.html], production deployments should treat the OpenAPI document as a **description of intended behavior**, not a substitute for a gateway/runtime that actually enforces authentication, rate limiting, or other operational controls — this is a direct implication of the documented scope boundary rather than a separately stated "production considerations" claim.

---

## Summary of Version-Sensitive Facts Worth Tracking

1. Current stable OAS version: **3.2.0**, published 2025-09-19. [Source: GitHub Releases API]
2. 3.1 → 3.2 is a **non-breaking** minor upgrade (docs' own wording). [Source: learn.openapis.org/upgrading/v3.1-to-v3.2.html]
3. 3.0 → 3.1 **is breaking** for documents using `nullable`, boolean `exclusiveMinimum`/`exclusiveMaximum`, singular `example`, or certain file-upload `format` patterns. [Source: learn.openapis.org/upgrading/v3.0-to-v3.1.html]
4. Full JSON Schema 2020-12 alignment (`jsonSchemaDialect`) only applies from **3.1.0 onward**; 3.0.x schemas are JSON-Schema-*like* but diverge (e.g., `nullable`, boolean exclusive bounds). [Source: spec.openapis.org/oas/v3.1.0.html + upgrade guide]
5. Two parallel maintained lines exist: 3.0.x (latest patch 3.0.4, 2024-10-24) and 3.1.x/3.2.x (3.1.2 and 3.2.0 both released 2025-09-19; 3.1.1 released 2024-10-24).
6. A future major version, OAS 4.0 ("Moonwalk"), is in early ADR-stage design with no release date; the OAI itself recommends using 3.x today. [Source: github.com/OAI/sig-moonwalk]
7. The official FAQ page (openapis.org/faq), as fetched during this research pass, still reports 3.1.1 as "the latest version" — stale relative to the confirmed 3.2.0 release. Treat spec.openapis.org and the GitHub Releases API as authoritative over that FAQ page.

## Unresolved Items

- Exact CHANGELOG.md line items for the 3.1.1 and 3.0.4 patch releases could not be directly fetched (404s from both the GitHub blob URL and raw.githubusercontent.com during this session); their "editorial only, no normative changes" characterization is not independently re-verified beyond the two upgrade guides' framing.
- Step-by-step official guidance for migrating from Swagger 2.0 to OpenAPI 3.0 was not directly retrieved in this pass (the Learn site's table of contents indicates an "Upgrading ... from 1.0 to 3.2" resource exists, but its specific content was not fetched/confirmed).
- No formal LTS/support-window or end-of-life policy for older OAS minor/patch lines (e.g. 3.0.x) was found in the primary sources checked; it is unclear whether the OAI publishes one anywhere else.
- Whether the openapis.org FAQ page is simply infrequently updated (vs. some other explanation for the version discrepancy) is not confirmed — noted as a documentation staleness observation rather than a spec fact.
