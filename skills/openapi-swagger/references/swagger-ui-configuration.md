# Swagger UI configuration reference (Tier-2)

Loaded only when [SKILL.md](../SKILL.md) links here. Condensed from
[research/technologies/swagger.md](../../../research/technologies/swagger.md)
— consult that document for the full citation trail and package/architecture
detail (the `swagger-ui` vs. `swagger-ui-dist` vs. `swagger-ui-react`
distinction, Docker env vars, plugin system).

## JS initialization config object

Full documented table of `SwaggerUIBundle`/`SwaggerUI()` init options
[Source: https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/]:

| Option | Default | Notes |
|---|---|---|
| `configUrl` | — | URL to fetch an external config document from |
| `dom_id` | — | ID of the DOM element to render into (required unless `domNode` given) |
| `domNode` | — | DOM element to render into; overrides `dom_id` |
| `spec` | `{}` | Inline OpenAPI definition object; bypasses URL fetch |
| `url` | — | URL/path to the API definition; ignored if `urls` or `spec` set |
| `urls` | — | Array of `{url, name}` definitions for the Topbar plugin's spec switcher |
| `urls.primaryName` | — | Which spec in `urls` displays on load |
| `queryConfigEnabled` | `false` | Allow URL query-string params to override config |
| `layout` | `"BaseLayout"` | Root layout component name |
| `plugins` | `[]` | Array of plugin functions |
| `presets` | `[SwaggerUI.presets.ApisPreset]` | Preset bundles |
| `deepLinking` | `false` | Enable tag/operation deep linking |
| `displayOperationId` | `false` | Show `operationId` in the operations list |
| `defaultModelsExpandDepth` | `1` | Model section expansion depth (`-1` hides models entirely) |
| `defaultModelExpandDepth` | `1` | Expansion depth inside a model-example |
| `defaultModelRendering` | `"example"` | `"example"` or `"model"` |
| `displayRequestDuration` | `false` | Show request duration (ms) after Try-it-out |
| `docExpansion` | `"list"` | `"list"`, `"full"`, or `"none"` |
| `filter` | `false` | Boolean or search string to enable tag filtering |
| `maxDisplayedTags` | — | Limit number of tags shown |
| `operationsSorter` | — | `"alpha"`, `"method"`, or a custom comparator function |
| `showExtensions` | `false` | Show vendor `x-*` extension fields |
| `showCommonExtensions` | `false` | Show extension fields on parameters |
| `tagsSorter` | — | `"alpha"` or a custom comparator |
| `useUnsafeMarkdown` | `false` | **Deprecated** — disables markdown sanitization; do not use |
| `onComplete` | no-op | Callback fired once rendering completes |
| `syntaxHighlight.activated` | `true` | Toggle syntax highlighting |
| `syntaxHighlight.theme` | `"agate"` | highlight.js theme name |
| `tryItOutEnabled` | `false` | Whether "Try it out" starts enabled |
| `requestSnippetsEnabled` | `false` | Enable the request-snippets section |
| `oauth2RedirectUrl` | — | OAuth2 redirect target |
| `requestInterceptor` | identity fn | Mutates outgoing requests |
| `request.curlOptions` | — | Extra CLI flags shown in the generated curl snippet |
| `responseInterceptor` | identity fn | Mutates incoming responses |
| `showMutatedRequest` | `true` | Show the interceptor-mutated request in the curl display |
| `supportedSubmitMethods` | `["get","put","post","delete","options","head","patch","trace"]` | HTTP methods that get a "Try it out" button |
| `validatorUrl` | `"https://validator.swagger.io/validator"` | Spec-validator endpoint; set to `"none"`, `"127.0.0.1"`, or `"localhost"` to disable |
| `withCredentials` | `false` | Send credentials on CORS "Try it out" requests |
| `modelPropertyMacro` | — | Function setting default model-property values |
| `parameterMacro` | — | Function setting default parameter values |
| `persistAuthorization` | `false` | Persist entered auth data across page reloads |

[Source: https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/]
**Configuration precedence**, highest to lowest: URL query-string params (if
`queryConfigEnabled`) > `configUrl` document > the initialization object literal.

## `initOAuth()` options

[Source: https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/]
`clientId` (string, required for the default client), `clientSecret` (string
— **never use in production**, exposes a confidential OAuth secret to every
visitor), `appName` (shown in the authorization popup), `realm` (OAuth1-style
query param appended to authorize/token URLs), `scopeSeparator` (default:
space), `scopes` (initial scope array or delimited string),
`additionalQueryStringParams` (object merged into authorize/token URL query
strings), `useBasicAuthenticationWithAccessCodeGrant` (boolean, default
`false`), `usePkceWithAuthorizationCodeGrant` (boolean, default `false` —
enables PKCE for the authorization-code grant; recommended for public
clients).

## Docker deployment env vars

[Source: https://swagger.io/docs/open-source-tools/swagger-ui/usage/installation/,
https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/installation.md]
Image: `docker.swagger.io/swaggerapi/swagger-ui`. Env vars: `SWAGGER_JSON`
(local spec file path), `SWAGGER_JSON_URL` (external spec URL), `BASE_URL`
(base path), `PORT` (default `8080`), `EMBEDDING` (controls whether
`X-Frame-Options` is set — a clickjacking-relevant production setting).
[Version-sensitive: multi-platform images and `PORT_IPV6` added in v5.0.0,
June 2023 — source: https://github.com/swagger-api/swagger-ui/releases/tag/v5.0.0]

## Swagger Codegen CLI

[Source: https://github.com/swagger-api/swagger-codegen/blob/master/README.md]
`java -jar swagger-codegen-cli.jar generate -i <spec-file-or-url> -l <language> -o <output-dir>`.
Flags: `-a`/`--auth` (auth headers for a remote spec), `-c`/`--config`
(language-specific JSON config file), `-t`/`--template-dir` (custom template
directory), `-v`/`--verbose`, `-s`/`--skip-overwrite`.
`config-help -l <language>` lists that language's config options. Two
parallel major lines are maintained: 3.x (`io.swagger.codegen.v3`, targets
OpenAPI 3.0.x) and 2.x (`io.swagger`, targets Swagger/OpenAPI 1.0–2.0) — not
a sequential upgrade path, choose based on the spec version in hand.
