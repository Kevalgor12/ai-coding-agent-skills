# Model Context Protocol (MCP)

Research pass on the **Model Context Protocol** itself — the open, cross-vendor
protocol, not any single vendor's coding agent. Primary sources are the official
spec site (modelcontextprotocol.io), the `modelcontextprotocol` GitHub org, and
the official MCP blog. Research date: 2026-09-09.

## 0. Which spec version this document is based on, and why that matters

This is the single most important caveat for everything below.

[Source: https://blog.modelcontextprotocol.io/posts/2026-07-28/] On **2026-07-28**
the MCP steering group shipped **the largest revision of the protocol since
launch**: "Today, we're officially pushing the release button on the next
version of the MCP specification, `2026-07-28`." This is not a draft or RC —
it is the current, finalized `latest` specification as of this research date
(2026-09-09), i.e. it has been final for about six weeks.

[Source: https://modelcontextprotocol.io/specification/2026-07-28/changelog] This
revision is a near-total rewrite of the base protocol: it **removes the
`initialize`/`notifications/initialized` handshake and protocol-level sessions**,
makes MCP **stateless** (every request self-describes its protocol version and
capabilities), replaces server-initiated requests (`roots/list`,
`sampling/createMessage`, `elicitation/create`) with a new **Multi Round-Trip
Requests (MRTR)** pattern, adds a `server/discover` RPC, and **deprecates
Roots, Sampling, and Logging** as named features (still functional, but frozen
and scheduled for eventual removal no sooner than 12 months out).

[Inference, not confirmed in docs] Given the finality is only ~6 weeks old,
it is highly likely that **most currently-deployed MCP clients and servers in
the wild** (the ones a reader of this document has actually used — Claude
Desktop, Cursor, Windsurf, VS Code extensions, etc., as of mid-2026) were built
against one of the earlier, `initialize`-handshake-based revisions
(`2025-03-26`, `2025-06-18`, `2025-11-25`), not `2026-07-28`. The spec's own
[versioning page](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)
calls these earlier revisions **"Legacy"** and the new one **"Modern,"**
and defines an explicit compatibility matrix between them (reproduced in
§10 below) — strong evidence the maintainers themselves expect a long mixed
transition period. **This document describes both**: the current Modern
(2026-07-28) design as the source of truth for "what MCP is," and the
preceding Legacy model wherever it materially changes what a cross-vendor
skill spec can assume about "how MCP actually works today in practice."

---

## 1. Skills

[Source: https://modelcontextprotocol.io/specification/2026-07-28] The core
specification overview explicitly lists **"Skills over MCP"** as one of three
named example *extensions* (alongside Tasks and MCP Apps): *"Rich, structured
instructions for agent workflows, discovered and consumed through MCP."* This
means: **as of today, "skill" is not a core MCP primitive** (it is not listed
under Server Features — Resources/Prompts/Tools — or Client Features —
Elicitation/Sampling/Roots). It exists only as an **optional, separately
negotiated extension**, still in progress.

[Source: https://modelcontextprotocol.io/community/working-groups/skills-over-mcp]
There is a dedicated **Skills Over MCP Working Group** (co-led by Nordstrom and
Anthropic representatives, with Google, Databricks, GitHub, AWS, and other
maintainers participating). Its charter states the mission is to define *"how
'agent skills' — rich, structured instructions for agent workflows — are
discovered, distributed, and consumed through MCP,"* and that it grew out of
**SEP-2076 — "Agent Skills as a First-Class MCP Primitive"** — i.e. there was
an explicit proposal to make skills a first-class primitive, and the working
group's existence signals that proposal did not (yet) succeed outright; instead
the WG's current direction (as of the charter's last update) is captured in
**SEP-2640 — "Skills Extension"**, explicitly scoped as an **Extensions Track**
SEP built on the existing **Resources** primitive, not a new core primitive.

[Source: https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2640
(SEP-2640, fetched via WebFetch)] As of the fetch date, SEP-2640 has been
**Accepted by Core Maintainers** (dated 2026-09-03 — six days before this
research), moving toward reference implementations and conformance tests. Key
design points reported from the PR:
- The extension identifier is `io.modelcontextprotocol/skills` — negotiated like
  any other MCP extension, via the `extensions` field of capabilities (see §12).
- Skills are represented as **resources** addressable by a `skill://` URI
  scheme, with a primary definition file conventionally at
  `skill://<skill-path>/SKILL.md`, sibling files addressable alongside it, and
  a discovery resource at `skill://index.json` listing available skills.
- Reported metadata fields include **name, description, and instructions**
  (consistent with reusing `Resource`'s `name`/`title`/`description` fields
  plus a text body).
- Discovery/consumption methods described in secondary sources include a
  `skills/list` / `skills/get` pairing and a `read_skill` tool, layered on top
  of (not replacing) the standard `resources/list` / `resources/read` methods.
- The WG's scope explicitly **excludes** "Plugin/bundle packaging (installable
  bundles — skills + servers + subagents + configuration as a single
  artifact)," calling that "a broader packaging effort" outside this WG.
- The WG explicitly coordinates with the external
  **[Agent Skills](https://agentskills.io/) spec** (a separate,
  vendor-originated content format and discovery convention — i.e. the thing
  Anthropic/Claude calls "Agent Skills" / `SKILL.md`) on "content format and
  well-known URI discovery." This is a strong signal that MCP's Skills
  Extension is explicitly being designed to interoperate with, not replace,
  that already-existing `SKILL.md`-style convention.

**Bottom line for Skills**: [Inference, not confirmed in docs — synthesizing the
above] MCP does not yet have a finished, ratified "skill" primitive. What it
has is (a) core primitives — Resources, Prompts, Tools — any of which today can
informally carry "skill-like" content, and (b) an in-flight, resource-based
extension (SEP-2640, Accepted but not yet fully specified/implemented as of
2026-09-09) that is converging toward representing skills as a directory of
resources under a `skill://` URI convention, coordinating with the external
Agent Skills / `SKILL.md` format for the actual content shape.

---

## 2. Rules / project instructions / user instructions

[Source: https://modelcontextprotocol.io/specification/2026-07-28/server/prompts]
MCP has no primitive literally named "rule." The closest fit is the **Prompts**
primitive: *"Prompts allow servers to provide structured messages and
instructions for interacting with language models."* Critically, the spec
frames Prompts as **user-controlled**, not automatically injected: *"Prompts
are designed to be user-controlled, meaning they are exposed from servers to
clients with the intention of the user being able to explicitly select them for
use... Typically, prompts would be triggered through user-initiated commands in
the user interface"* (the docs' own example is a slash command). This is
different from what most coding-agent ecosystems mean by "rules" or "project
instructions" — i.e. standing context automatically applied to every
turn/session without explicit per-use invocation.

Not part of the MCP spec / not documented: there is no MCP primitive for
"always-on project instructions" analogous to a `CLAUDE.md`, `.cursorrules`, or
system-prompt-injection file. A server *could* expose such content as a Prompt
(user must invoke it) or a Resource (client decides whether/when to include it
in context — see §3), but the spec does not define a "standing instructions"
concept distinct from those two primitives, and does not mandate that any
client auto-load any given resource or prompt at session start.

[Inference, not confirmed in docs] In practice, several coding-agent clients
that speak MCP layer their own separate "rules"/"instructions" conventions
(CLAUDE.md, `.cursor/rules`, etc.) entirely outside MCP — this is host/client
behavior, not something the MCP spec defines or requires.

---

## 3. Context and context loading — the Resources primitive

[Source: https://modelcontextprotocol.io/specification/2026-07-28/server/resources]
Resources are MCP's primitive for exposing data/context: *"Resources allow
servers to share data that provides context to language models, such as files,
database schemas, or application-specific information. Each resource is
uniquely identified by a URI."*

Key protocol facts:
- Capability declaration: servers supporting resources **MUST** declare
  `capabilities.resources`, with optional sub-flags `listChanged` and
  `subscribe`.
- Methods: `resources/list` (paginated, cacheable), `resources/read` (given a
  URI, returns one or more `contents` blocks — text or base64 `blob`),
  `resources/templates/list` (RFC 6570 URI templates for parameterized
  resources, e.g. `file:///{path}`).
- Standard URI schemes documented: `https://` (client fetches directly off the
  web, bypassing the server, when possible), `file://` (filesystem-like,
  not necessarily backed by a real filesystem), `git://`. Custom schemes are
  explicitly permitted and common.
- Content carries optional **annotations**: `audience` (`"user"` and/or
  `"assistant"`), `priority` (0.0–1.0 importance hint), `lastModified`
  (ISO 8601). These are advisory hints for the client, not protocol-enforced.
- User interaction model is explicitly **application-driven**: *"host
  applications determin[e] how to incorporate context based on their
  needs... the protocol itself does not mandate any specific user interaction
  model"* — i.e. MCP does not say whether/when a resource is auto-loaded into
  the model's context; that is entirely a client/host decision.
- In the 2026-07-28 revision, `resources/list` and `resources/read` results
  carry `ttlMs` (freshness hint, ms) and `cacheScope` (`"public"`/`"private"`)
  fields to guide client-side caching — this is new caching machinery, not
  present in earlier revisions.
- Change notifications moved from the old `resources/subscribe` /
  `resources/unsubscribe` methods to a unified long-lived
  `subscriptions/listen` stream (see §9 for detail on this pattern).

Tools and Prompts can also carry **resource links** (a URI reference the
client may separately fetch) or **embedded resources** (inlined resource
content) — so Resources interoperate with, rather than compete against, the
Tools and Prompts primitives.

---

## 4. Tools and tool calling

[Source: https://modelcontextprotocol.io/specification/2026-07-28/server/tools]
Tools are MCP's primitive for model-invokable functions: *"servers to expose
tools that can be invoked by language models... Each tool is uniquely
identified by a name and includes metadata describing its schema."* This
primitive is explicitly **model-controlled**: *"the language model can
discover and invoke tools automatically based on its contextual understanding
and the user's prompts,"* while the spec strongly recommends (SHOULD-level)
a human-in-the-loop confirmation step — it does not mandate one at the
protocol level.

Schema/shape:
- Capability: servers declare `capabilities.tools`, with optional
  `listChanged`.
- Discovery: `tools/list` (paginated, cacheable — servers **SHOULD** return a
  deterministic order to help client-side/LLM prompt caching).
- A `Tool` object has: `name` (required; guidance: 1–128 chars, case-sensitive,
  restricted charset, unique per-server), `title` (optional display name),
  `description`, `icons`, `inputSchema` (JSON Schema, defaults to 2020-12
  dialect), `outputSchema` (optional JSON Schema for `structuredContent`),
  `annotations` (behavior hints — explicitly flagged: *"clients MUST consider
  tool annotations to be untrusted unless they come from trusted servers"*).
- Invocation: `tools/call` with `name` + `arguments`; results carry `content`
  (an array of `text` / `image` / `audio` / `resource_link` / `resource`
  blocks) and/or `structuredContent` (any JSON value, validated against
  `outputSchema` if declared), plus `isError`.
- Two distinct error channels: **protocol errors** (malformed
  request/unknown tool — standard JSON-RPC `error`, code `-32602` etc.) vs.
  **tool execution errors** (`isError: true` in a normal result) — the spec is
  explicit that execution errors, not protocol errors, are what should be fed
  back to the model so it can self-correct: *"Clients SHOULD provide tool
  execution errors to language models to enable self-correction."*
- New in 2026-07-28: `tools/call` may return an `InputRequiredResult`
  (`resultType: "input_required"`) mid-call to request more information via
  the MRTR pattern (see §9) — e.g. triggering an elicitation before completing.
- Also new: `x-mcp-header`, a JSON-Schema-level annotation letting a tool
  parameter be mirrored into an HTTP header (`Mcp-Param-{name}`) on Streamable
  HTTP, for proxy/intermediary routing without body-parsing. Explicitly *not*
  for sensitive parameters (credentials, PII) since headers are visible to
  intermediaries.
- Non-normative "Stateful Tools" guidance: MCP has **no protocol-level session
  concept for tools** (consistent with the whole protocol going stateless).
  Servers that need cross-call state (a shopping cart, a DB transaction) are
  told to mint an explicit opaque handle string, return it in one tool's
  result, and have the model pass it as a plain argument to later calls — "the
  protocol has no concept of a state handle; from the wire's perspective a
  handle is an ordinary string."

This is the most stable, mature, and universally-implemented primitive in MCP
— essentially unchanged in its user-facing shape (name/description/inputSchema
+ call/result) across all spec revisions; the 2026-07-28 changes here are
additive (caching hints, `x-mcp-header`, MRTR-based mid-call input requests),
not a redesign of the primitive itself.

---

## 5. File access and repository understanding — the Roots primitive

[Source: https://modelcontextprotocol.io/specification/2026-07-28/client/roots]
**Roots is deprecated as of protocol version 2026-07-28** (SEP-2577). The page
carries an explicit warning: *"Deprecated: The Roots feature is deprecated...
Under the feature lifecycle policy, it remains in the specification for at
least twelve months after this revision's release before it becomes eligible
for removal. New implementations SHOULD NOT adopt it; existing implementations
SHOULD migrate to passing directories or files via tool parameters, resource
URIs, or server configuration."*

What Roots was/is (still functional during the deprecation window): *"a
standardized way for clients to expose filesystem 'roots' to servers. Roots
inform servers about the directories and files the client considers relevant,
so that servers can focus their operations accordingly."* Explicitly stated:
*"They are informational guidance rather than an access-control mechanism. The
protocol does not enforce that servers stay within roots."* A `Root` is just
`{ uri: file://..., name?: string }`; under the new stateless design, a server
requests the root list via an `InputRequiredResult` containing a
`roots/list` request (MRTR pattern), rather than the old server-initiated
JSON-RPC request over an open session.

**Implication for "file access / repository understanding" generally**: MCP
never defined more than this coarse, advisory, non-enforced directory hint —
and even that is now on a deprecation track. There is no MCP primitive for
"repository understanding" (indexing, symbol search, project structure) beyond
whatever a server chooses to expose as ordinary Tools (e.g. a `grep`/`read_file`
tool) or Resources (`file://` URIs). [Inference, not confirmed in docs] The
suggested migration path — "pass directories or files via tool parameters,
resource URIs, or server configuration" — effectively means MCP is
consolidating "how a server learns what part of the filesystem to touch" onto
the Tools and Resources primitives rather than a dedicated concept, which
matches how most real coding-agent MCP servers (filesystem servers, etc.)
already behave in practice.

---

## 6. Memory

Not part of the MCP spec / not documented. There is no "memory" primitive
anywhere in the Server Features (Resources, Prompts, Tools) or Client Features
(Elicitation, Sampling, Roots) taxonomy, in the 2026-07-28 spec or any earlier
revision found. [Source:
https://modelcontextprotocol.io/specification/2026-07-28] confirms the full
list of first-class features and memory is absent from it. Persistent memory
in the MCP ecosystem today is implemented entirely at the server-application
level (e.g. a community "memory server" that stores facts and exposes them
back as Tools/Resources) — this is a convention built on top of existing
primitives, not something MCP itself defines or standardizes.

---

## 7. Sub-agents and delegation

Not part of the MCP spec / not documented as a core primitive. Searching the
spec's feature list (server features, client features, extensions) turns up
no agent-to-agent delegation primitive. Two adjacent, but distinct, findings:

- [Source: https://modelcontextprotocol.io/community/working-groups/skills-over-mcp]
  There is an **"Agents WG"** referenced as a related/coordinating group in the
  Skills-over-MCP charter, with scope described (from the charter's "Related
  Groups" table) as covering *"How agents consume server metadata, skill
  activation"* — i.e. its concern is a client/agent's *consumption* of
  server-exposed metadata and skills, not agent-to-agent task delegation or
  orchestration.
- [Inference, not confirmed in docs] Web search surfaced Google's separate
  **Agent2Agent (A2A) protocol** and academic work on agent delegation/identity
  (e.g. arXiv papers on "verifiable delegation across MCP and A2A") as related
  but **explicitly distinct** efforts — A2A is a different, non-MCP protocol
  aimed at agent-to-agent communication; it is not part of MCP and MCP's own
  docs do not claim to subsume it. Sub-agent delegation, if a coding agent
  supports it (e.g. a "spawn a sub-agent to do X" capability), is a
  host/client-side orchestration feature layered on top of MCP, not something
  MCP's wire protocol expresses.

The closest MCP has to "delegation" is **Sampling** (§ below is folded into
"reusable instructions" section per the task's own note that Sampling maps
more naturally there) — where a *server* asks the *client* to run an LLM
completion on its behalf — but that is model-access delegation, not
agent-task delegation, and it too is now deprecated (see §11).

---

## 8. Hooks

Not part of the MCP spec / not documented. There is no lifecycle-hook concept
(pre-tool-call, post-tool-call, session-start, etc.) exposed by the protocol
itself. [Source: https://modelcontextprotocol.io/specification/2026-07-28]
— the "Additional Utilities" list is Configuration, Progress tracking,
Cancellation, and Error reporting; hooks are not among them, in this or any
earlier revision surveyed. [Inference, not confirmed in docs] Individual
coding-agent hosts (e.g. Claude Code) implement their own hook systems
(pre/post-tool hooks, etc.) entirely client-side; these hooks may fire around
an MCP tool call from the host's perspective, but MCP itself carries no
concept of, or wire representation for, a hook.

---

## 9. Commands — the Prompts primitive (reusable prompt templates)

[Source: https://modelcontextprotocol.io/specification/2026-07-28/server/prompts]
Covered in detail in §2 above; summarizing the "commands" angle specifically:
Prompts are explicitly designed to surface as user-invoked commands — the
spec's own illustrative screenshot is captioned as a **slash-command** UI, and
the prose says *"Typically, prompts would be triggered through user-initiated
commands in the user interface... For example, as slash commands."* So: MCP's
answer to "reusable command templates a user can invoke by name" is Prompts,
with:
- `prompts/list` → `Prompt { name, title?, description?, icons?, arguments?
  }` (arguments are named, with `description` and `required` flags; argument
  values can be auto-completed via the separate Completion utility).
- `prompts/get` → resolves a named prompt + arguments into a
  `messages: PromptMessage[]` array (role `user`/`assistant`, content blocks:
  text/image/audio/resource_link/embedded resource) ready to hand to a model.
- Same MRTR-based `InputRequiredResult` escape hatch as Tools/Resources, for
  prompts that need extra input before they can resolve.

---

## 10. MCP itself — transports, handshake, capability negotiation

### 10.1 Transports

[Source: https://modelcontextprotocol.io/specification/2026-07-28/basic/transports]
Two standard transports are currently specified, plus explicit allowance for
custom ones:
1. **stdio** — newline-delimited JSON-RPC messages over the standard streams
   of a client-launched subprocess.
2. **Streamable HTTP** — each message is an HTTP POST to a single MCP
   endpoint; replies arrive either as a single JSON object or as a
   request-scoped SSE stream (i.e. SSE is now scoped to one request/response,
   not a long-lived side-channel).

[Source: https://modelcontextprotocol.io/specification/2026-07-28/changelog]
The older **HTTP+SSE** transport (deprecated since protocol version
`2025-03-26`) has now been formally **reclassified as Deprecated** under the
new feature-lifecycle policy in this revision. Also removed in this revision:
SSE stream resumability and message redelivery (the `Last-Event-ID` header and
SSE event IDs) — *"A broken response stream loses the in-flight request;
clients MUST re-issue it as a new request with a new request ID."*

A transport is explicitly defined as **only a binding** — "It defines how
messages are framed and delivered... It does not define what the messages
mean" — protocol semantics (the message patterns) are identical across every
transport.

### 10.2 The old handshake vs. the new "no handshake" model

[Source: https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning]
This is the single biggest structural change in MCP's history. Quoting
directly: *"There is no negotiation handshake. Every request carries its
protocol version, and the server accepts or rejects each request
independently."*

- **Legacy model** (2025-11-25 and earlier — what most deployed
  implementations as of this writing still speak, per the reasoning in §0):
  client and server perform an `initialize` request/response (exchanging
  `protocolVersion` and `capabilities` once), then a `notifications/initialized`
  notification, establishing a connection-scoped session. Servers could
  thereafter send *server-initiated* JSON-RPC requests to the client
  (`roots/list`, `sampling/createMessage`, etc.) at any point in that session.
- **Modern model** (2026-07-28): no handshake at all. Every single request
  carries required `_meta` fields: `io.modelcontextprotocol/protocolVersion`
  (required) and `io.modelcontextprotocol/clientCapabilities` (required),
  plus optional `clientInfo`. Every response should carry
  `io.modelcontextprotocol/serverInfo`. There is a new
  **`server/discover`** RPC that servers **MUST** implement, which clients
  *may* (not must) call up front to learn a server's supported versions,
  capabilities, and identity — but a client is equally free to just fire an
  ordinary request and handle an `UnsupportedProtocolVersionError`
  (code `-32022`) if the version guess was wrong. Servers no longer initiate
  requests at all — anything that used to be server-initiated (roots,
  sampling, elicitation) is now expressed as an `InputRequiredResult`
  (`resultType: "input_required"`) returned *in reply to* a client request,
  which the client resolves and then **retries the original request** with
  `inputResponses` attached (a pattern the spec names **Multi Round-Trip
  Requests / MRTR**).

### 10.3 Capability negotiation, precisely

- Legacy: capabilities exchanged once, at `initialize`, and assumed valid for
  the life of the connection.
- Modern: capabilities are supplied **on every single request** (not cached
  connection state), because the protocol is stateless — *"Servers MUST NOT
  rely on prior requests over the same connection to establish context (e.g.,
  capabilities, protocol version, client identity)."* If a server needs a
  capability the client didn't declare on that request, it returns
  `MissingRequiredClientCapabilityError` (`-32021`) listing
  `data.requiredCapabilities`.
- Both eras use the same conceptual shape for capabilities: a server
  advertises which primitives it supports (`{"tools": {...}, "resources":
  {...}, "prompts": {...}}`, each optionally with sub-flags like
  `listChanged`/`subscribe`); a client advertises which client-side features
  it supports (`roots`, `sampling`, `elicitation`).
- New in Modern: an `extensions` map on both `ClientCapabilities` and
  `ServerCapabilities`, keyed by reverse-DNS-style extension identifiers
  (e.g. `io.modelcontextprotocol/ui`), each with its own settings object —
  this is how optional Extensions (Tasks, MCP Apps, Skills-over-MCP, auth
  extensions) opt in on top of the core protocol (see §12 below).

### 10.4 Backward-compatibility mechanics (Legacy ↔ Modern interop)

[Source: https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning]
The spec ships an explicit **compatibility matrix** for every combination of
client/server era:

| Client | Server | Outcome |
|---|---|---|
| Modern | Modern | Works — `server/discover` optional; version mismatch retried via `UnsupportedProtocolVersionError`. |
| Modern | Legacy | Fails, unless the client probes with `server/discover` first (stdio) to fail deterministically and surface an actionable error. |
| Dual-era | Modern | Works — client stays modern. |
| Dual-era | Legacy | Works — client falls back to `initialize` after detecting a non-modern response. |
| Legacy | Modern | Fails — legacy clients have no fall-forward mechanism. |
| Legacy | Dual-era | Works — server answers `initialize` and serves legacy semantics. |
| Legacy | Legacy | Works per the legacy revision (out of scope for the modern spec doc). |

A server built to support both eras ("dual-era") picks its behavior per
request: modern `_meta` present → served statelessly under 2026-07-28 rules;
an `initialize` request → legacy session semantics for that stdio process or
HTTP session. [Inference, not confirmed in docs] This matrix, published by the
maintainers themselves, is effectively an admission that the ecosystem will
run mixed-era for a long transition window — directly relevant to a
vendor-neutral skill spec, since "does this client speak MCP" is no longer a
single yes/no question but "which era, and does it probe or assume."

---

## 11. Client (formerly server-initiated) features: Sampling, and its deprecation

[Source: https://modelcontextprotocol.io/specification/2026-07-28/client/sampling]
**Sampling is deprecated as of 2026-07-28** (same SEP-2577 as Roots and
Logging), with the same 12-month minimum deprecation window. What it does
(still functional): lets a *server* ask the *client* to run an LLM completion
("sampling") using the client's own model access, so servers can implement
agentic sub-behavior without needing their own API keys — *"This flow allows
clients to maintain control over model access, selection, and permissions
while enabling servers to leverage AI capabilities—with no server API keys
necessary."* It supports model-selection abstraction via `modelPreferences`
(`costPriority`/`speedPriority`/`intelligencePriority`, plus advisory `hints`),
and — notably added machinery — a full tool-use sub-loop inside a single
sampling flow (`tools`, `toolChoice`, multi-turn tool-result exchange, with
explicit content-shape rules requiring tool_use/tool_result messages to pair
up and not mix with other content types, mirroring how mainstream provider
APIs — Claude/OpenAI/Gemini — represent tool turns). The spec's own suggested
replacement: *"integrate directly with LLM provider APIs instead of
Sampling."* Under the Modern MRTR model, a sampling request is delivered as an
`InputRequiredResult` containing a `sampling/createMessage` request, resolved
by the client retrying the original request with the result.

**Elicitation** (client feature, *not* deprecated) is the other client-side
feature: a server-initiated (now MRTR-mediated) request for structured user
input (`mode: "form"`, JSON-Schema-constrained, deliberately restricted to
flat primitive-only schemas) or an out-of-band URL redirect (`mode: "url"`,
for anything sensitive like credentials/OAuth/payment, explicitly barred from
form mode: *"Servers MUST NOT use form mode elicitation to request sensitive
information such as passwords, API keys, access tokens, or payment
credentials"*). Elicitation responses use a 3-way `accept`/`decline`/`cancel`
action model. This is the primitive a coding-agent-adjacent MCP server would
use to, e.g., ask the user to fill in a missing parameter or complete an OAuth
flow in a browser, without ever routing secrets through the model or the MCP
client.

---

## 12. Extensions framework and capability discovery mechanics (deep dive)

[Source: https://modelcontextprotocol.io/extensions/overview] MCP extensions
are optional, opt-in additions "beyond the core protocol," identified by a
mandatory vendor-prefixed identifier (official ones use
`io.modelcontextprotocol/...`; third parties are told to use a reverse-DNS
prefix they own, "similar to Java package naming"). Documented official
extension families: **MCP Authorization Extensions** (`ext-auth` — OAuth
client-credentials flow, enterprise-managed authorization), **MCP Apps**
(interactive inline UI — charts/forms/video players), **MCP Tasks**
(async long-running operations with polling/durable handles). Skills-over-MCP
is tracked as a fourth, still-in-review, extension (§1). Extensions:
- Go through a formal SEP process (**Extensions Track**), requiring at least
  one reference implementation in an official SDK before review, with final
  authority resting with Core Maintainers.
- Are **"always disabled by default and require explicit opt-in from the
  developer"** — even at the SDK level, let alone the client/server level.
- Are negotiated exactly like core capabilities: via the `extensions` map
  inside `ClientCapabilities`/`ServerCapabilities`. Client side, this appears
  inside `_meta.io.modelcontextprotocol/clientCapabilities.extensions` on
  *every request* (consistent with the stateless model); server side, inside
  the `capabilities.extensions` field of the `server/discover` response.
- Fall back gracefully by design contract: *"If one side supports an
  extension but the other doesn't, the supporting side needs to either fall
  back to core protocol behavior or reject the request... It's a good
  practice to document expected fallback behavior."*

This extensions framework is itself new in 2026-07-28 (formalized via
SEP-2133) — in earlier spec revisions there was no equivalent sanctioned
mechanism for "optional, independently-versioned add-ons to the core wire
protocol"; experimental/vendor-specific features simply existed outside the
spec.

---

## 13. Configuration: what the spec mandates vs. what is pure convention

Not part of the MCP spec / not documented: **file names and formats for
declaring/registering MCP servers to a client are not specified by MCP at
all.** The protocol defines what a client and server say to each other once
connected (JSON-RPC over a transport) — it does not define how a human or a
host application decides *which* servers to launch, with what command/args/env,
or what such a config file should be named.

[Inference, not confirmed in docs, corroborated by general web search rather
than the official spec — the spec itself is silent here] `claude_desktop_config.json`
(Claude Desktop, macOS/Windows-specific paths under Application
Support/AppData), `.mcp.json`/`~/.claude.json` (Claude Code), and the informal,
now fairly widely-copied `mcp.json` shape (`{"mcpServers": {"<name>": {"command":
..., "args": [...], "env": {...}}}}`) are all **client/vendor conventions**,
not protocol requirements. Different clients use different file names, paths,
and (for HTTP transports) slightly different fields for URL/headers/auth.
Because the wire-level JSON-RPC schema is shared, the *content* clients need
to configure (a command to launch, or a URL to connect to) is similar across
clients, which is presumably why an `mcp.json`-shaped convention has become a
de facto common denominator among several tools — but this convergence is
social/ecosystem convention, not spec-mandated. Nothing in the specification
pages (basic protocol, transports, versioning, authorization) prescribes a
config file schema.

---

## 14. Agent-specific limitations / explicitly out-of-scope areas / version deltas

Since MCP is a protocol rather than a product, "agent limitations" translates
to: what does the spec explicitly decline to define, and how has scope shifted
across versions.

Explicitly out of scope, per the spec's own words:
- **User interaction model** for every primitive (Tools, Resources, Prompts,
  Elicitation, Sampling) is explicitly left to implementations: each primitive
  page repeats some form of *"the protocol itself does not mandate any
  specific user interaction model."*
- **Security/consent enforcement mechanics**: [Source:
  https://modelcontextprotocol.io/specification/2026-07-28] *"While MCP itself
  cannot enforce these security principles at the protocol level,
  implementors SHOULD..."* — user consent, tool-safety review UI, data-privacy
  controls are all delegated to host/client implementations; MCP defines the
  *principles* (explicit consent, no silent data transmission, treat tool
  annotations as untrusted unless from a trusted server) but not the
  enforcement.
- **The authorization server's implementation**: *"The implementation details
  of the authorization server are beyond the scope of this specification."*
  (MCP defines the OAuth 2.1-based *client↔resource-server* flow, not how an
  auth server itself works.)
- **Non-HTTP auth**: STDIO transport is explicitly told **not** to use the
  HTTP-oriented OAuth authorization framework — *"implementations using an
  STDIO transport SHOULD NOT follow this specification, and instead retrieve
  credentials from the environment."*
- **Plugin/bundle packaging** (skills + servers + subagents + config as one
  installable artifact) is explicitly named as out of scope for the Skills WG,
  "belongs to a broader packaging effort" (§1).
- **Registry schema ownership** is explicitly assigned elsewhere (a separate
  Registry WG), even though Skills-over-MCP depends on it.

Version deltas that matter most for a cross-vendor skill spec (chronological,
oldest-referenced → newest):
- `2025-03-26`: (referenced only as the point at which HTTP+SSE was first
  superseded/deprecated in favor of Streamable HTTP; not deep-dived in this
  pass).
- `2025-06-18` / `2025-11-25`: "Legacy" `initialize`-handshake era; URL-mode
  elicitation was introduced in `2025-11-25` per the elicitation page's own
  note ("New feature: URL mode elicitation is introduced in the 2025-11-25
  version... may change in future protocol revisions").
- `2026-07-28` ("Modern"): stateless core, no handshake, `server/discover`,
  MRTR pattern replacing all server-initiated requests, Roots/Sampling/Logging
  deprecated, HTTP+SSE formally reclassified Deprecated, Extensions framework
  formalized, resource-not-found error code changed `-32002` → `-32602`,
  formal error-code allocation policy and 12-month deprecation policy adopted.

[Source: https://blog.modelcontextprotocol.io/posts/2026-07-28/] Per the
official announcement, SDK adoption at launch: all four **Tier 1 SDKs**
(TypeScript, Python, Go, C#) updated for `2026-07-28` at release, Rust SDK in
beta; the post explicitly flags migration cost, "especially for developers
that did depend on session identifiers" — i.e. the maintainers themselves
acknowledge this was not a drop-in-compatible change for existing server
implementations.

---

## Preliminary cross-ecosystem notes (to be reconciled in the comparison doc)

*(All of the following are explicitly preliminary and my own synthesis, not
direct spec quotes — flagged per the research instructions.)*

**1. Which parts of MCP are the universal/common substrate other ecosystems build on?**
[Inference] Overwhelmingly the **Tools** primitive: name + description +
JSON-Schema `inputSchema` + `tools/list`/`tools/call` is essentially unchanged
across every spec revision surveyed and is what nearly every MCP-integrating
coding agent actually exercises day to day. **Resources** (URI-addressed
context blobs) is the second most universal piece — most "give the model
files/data" integrations map onto it even when the client doesn't expose a
resource picker UI. JSON-RPC 2.0 framing and the notion of a
capability-declaring handshake (in whichever era) are also universal. Roots,
Sampling, and Prompts are used far less consistently in practice, and Roots/
Sampling are now formally sunset — a vendor-neutral "core" skill schema should
probably not lean on them.

**2. Anything vendor-specific despite being "the standard"?**
[Inference] Config declaration (mcp.json/claude_desktop_config.json/.mcp.json
— see §13) is the clearest case: identical underlying JSON-RPC servers, but
each client wants its own file name/location/shape to register them. Also:
the **user-interaction model** for every primitive is deliberately left open
by the spec, so in practice each client's UX for tool-confirmation, resource
picking, and prompt/slash-command surfacing diverges significantly even
though the wire protocol is shared. And the **era split** itself (§0, §10.4)
means "speaks MCP" today spans two materially different wire behaviors
(handshake-based vs. stateless/per-request), which is itself a form of
non-uniformity baked into the standard's own transition design.

**3. What from MCP's design should directly inform a vendor-neutral core skill schema?**
[Inference] Several transferable ideas: (a) explicit **capability
declaration with graceful degradation** — declare what you support, get a
typed error (`MissingRequiredClientCapabilityError`) rather than silent
failure, when you don't; (b) the **Extensions** pattern — a small, versioned,
independently-evolving add-on mechanism keyed by a namespaced identifier, with
mandatory opt-in and documented fallback — is a strong template for how a
skill spec could let vendors add proprietary fields without breaking the
common core; (c) JSON-Schema-typed inputs/outputs (`inputSchema`/
`outputSchema`) as the lingua franca for describing a capability's shape; (d)
the tool-execution-error vs. protocol-error split, which cleanly separates
"the model can fix this by retrying differently" from "something is broken" —
directly relevant to designing how a skill reports failure back to an agent;
(e) MRTR's approach of surfacing "I need more input" as a typed, resumable
result rather than an out-of-band side-channel, which is a clean pattern for
skills that need human/user input mid-execution.

**4. What would still require an adapter even when both sides speak MCP?**
[Inference] (a) **Era mismatch** (Legacy handshake-based vs. Modern
stateless) — a client and server that both "speak MCP" may still fail to
interoperate without explicit dual-era support or probing logic (§10.4); (b)
**tool permission/consent models** — MCP mandates none, so "does this call
need user approval, and how is that surfaced" differs per client, meaning a
skill that assumes a particular consent UX (e.g. auto-approve vs.
always-confirm) needs an adapter layer regardless of shared MCP compliance;
(c) **extension support** — a skill relying on MCP Apps or Tasks or
Skills-over-MCP will silently degrade (per the mandated fallback contract) on
a client that doesn't implement that extension, so functional parity is not
guaranteed just because both sides are MCP-compliant; (d) **config
registration format** (§13) — getting a given MCP server actually loaded into
a given client is not standardized at all.

**5. What about MCP should NOT be assumed to be uniformly implemented across every client?**
[Inference] (a) Any of the three now-deprecated features — **Roots,
Sampling, Logging** — since they were always optional client capabilities and
are now explicitly discouraged for new adoption; a vendor-neutral spec should
not assume a client can supply filesystem roots or serve sampling requests.
(b) **Elicitation's URL mode** — flagged in the spec itself as introduced only
in `2025-11-25` and explicitly "may change in future protocol revisions." (c)
**Any Extension** (MCP Apps, Tasks, Skills-over-MCP, auth extensions) — all
extensions are opt-in by design and, per the framework's own rules, "always
disabled by default," so none can be assumed present. (d) **`server/discover`
and the whole Modern/stateless request model** — given the ~6-week-old
finalization and the explicit Legacy/Modern compatibility matrix the
maintainers themselves published, a large fraction of currently-deployed
servers/clients should be assumed to still be Legacy (handshake-based) unless
proven otherwise. (e) **Caching hints (`ttlMs`/`cacheScope`)** and
**deterministic tool ordering** — both introduced in 2026-07-28 as SHOULD-level
guidance, not guaranteed by older or non-compliant implementations.
